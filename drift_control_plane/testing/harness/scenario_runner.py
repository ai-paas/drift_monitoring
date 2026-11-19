from __future__ import annotations

import json
import hashlib
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Callable

from .artifact_store import ArtifactStore, safe_name, utc_now_iso
from .clients.admin_client import AdminClient
from .clients.drift_client import DriftClient
from .clients.http_client import HarnessHttpClient
from .clients.llm_client import LlmClient
from .clients.test_feeder_client import TestFeederClient
from .clock import HarnessClock
from .config import HarnessConfig
from .contract_validator import ContractValidator
from .chart_smoke import merge_interpretation_into_chart_payload, run_chart_runtime_smoke
from .models import StepResult, ValidationResult
from .proxy_runtime import set_active_proxy_run
from .ui_smoke import run_timeseries_ui_smoke


class ScenarioRunner:
    def __init__(self, config: HarnessConfig) -> None:
        self.config = config
        self.validator = ContractValidator()
        self.last_run_id: str | None = None
        self.last_run_dir: Path | None = None
        self.last_status: str | None = None

    def run(self, scenario_path: Path) -> int:
        scenario = json.loads(scenario_path.read_text(encoding="utf-8"))
        scenario_id = scenario["scenarioId"]
        mode = scenario.get("mode", "A")
        run_id = self._make_run_id(scenario_id, mode)
        store = ArtifactStore(run_id, self.config.runs_root)
        set_active_proxy_run(run_id, self.config.runs_root)
        self.last_run_id = run_id
        self.last_run_dir = store.run_dir

        admin = AdminClient(
            HarnessHttpClient("admin", self.config.admin_base_url, store, self.config.request_timeout_seconds)
        )
        drift = DriftClient(
            HarnessHttpClient("drift", self.config.drift_base_url, store, self.config.request_timeout_seconds)
        )
        feeder = TestFeederClient(
            HarnessHttpClient(
                "test_feeder", self.config.test_feeder_base_url, store, self.config.request_timeout_seconds
            )
        )
        llm = LlmClient(HarnessHttpClient("llm", self.config.llm_base_url, store, self.config.request_timeout_seconds))

        started_at = utc_now_iso()
        store.write_manifest(
            {
                "runId": run_id,
                "scenarioId": scenario_id,
                "mode": mode,
                "startedAt": started_at,
                "scenarioPath": str(scenario_path),
                "baseUrls": {
                    "admin": self.config.admin_base_url,
                    "drift": self.config.drift_base_url,
                    "testFeeder": self.config.test_feeder_base_url,
                    "llm": self.config.llm_base_url,
                },
            }
        )

        steps: list[StepResult] = []
        validations: list[ValidationResult] = []
        status = "passed"
        error: str | None = None

        try:
            self._run_steps(scenario, admin, drift, feeder, llm, store, steps, validations)
            if any(result.status == "failed" for result in validations):
                status = "failed"
                error = "contract validation failed"
        except Exception as exc:  # noqa: BLE001 - failures must be summarized as run artifacts.
            status = "failed"
            error = f"{exc.__class__.__name__}: {exc}"
        finally:
            self.last_status = status
            finished_at = utc_now_iso()
            store.write_json(
                "failure_artifacts/failure_summary.json",
                self._build_failure_summary(status, error, steps, validations),
            )
            store.write_steps(steps)
            store.write_validation_report(validations)
            store.write_summary(status, scenario_id, started_at, finished_at, error)
            store.append_index(
                {
                    "runId": run_id,
                    "scenarioId": scenario_id,
                    "mode": mode,
                    "status": status,
                    "startedAt": started_at,
                    "finishedAt": finished_at,
                    "summaryPath": f"{run_id}/summary.md",
                }
            )

        return 0 if status == "passed" else 1

    def _build_failure_summary(
        self,
        status: str,
        error: str | None,
        steps: list[StepResult],
        validations: list[ValidationResult],
    ) -> dict[str, Any]:
        failed_steps = [step.__dict__ for step in steps if step.status == "failed"]
        failed_validations = [result.__dict__ for result in validations if result.status == "failed"]
        first_failure = failed_steps[0] if failed_steps else (failed_validations[0] if failed_validations else None)
        return {
            "status": status,
            "error": error,
            "firstFailure": first_failure,
            "failedStepCount": len(failed_steps),
            "failedValidationCount": len(failed_validations),
            "failedSteps": failed_steps,
            "failedValidations": failed_validations,
        }

    def _run_steps(
        self,
        scenario: dict[str, Any],
        admin: AdminClient,
        drift: DriftClient,
        feeder: TestFeederClient,
        llm: LlmClient,
        store: ArtifactStore,
        steps: list[StepResult],
        validations: list[ValidationResult],
    ) -> None:
        context = {
            "sourceId": scenario["source"]["sourceId"],
            "adapterId": scenario["adapter"]["adapterId"],
            "assignmentId": scenario["methodAssignment"]["assignmentId"],
            "finalLogicalNow": scenario["feeder"]["startTime"],
        }
        poll_responses: list[dict[str, Any]] = []

        actions: list[tuple[str, Callable[[], Any], list[str]]] = [
            ("health.admin", admin.health, ["ok", "data"]),
            ("health.drift", drift.health, ["ok", "data"]),
            ("health.test_feeder", feeder.health, ["ok", "data"]),
            ("admin.test_reset", lambda: admin.test_reset(context["sourceId"]), ["ok", "data"]),
            ("test_feeder.register_feeder", lambda: feeder.register_feeder(scenario["feeder"]), ["ok", "data"]),
            ("admin.register_source", lambda: admin.register_source(scenario["source"]), ["ok", "data"]),
            ("admin.register_adapter", lambda: admin.register_adapter(scenario["adapter"]), ["ok", "data"]),
            (
                "admin.register_method_assignment",
                lambda: admin.register_method_assignment(context["sourceId"], scenario["methodAssignment"]),
                ["ok", "data"],
            ),
            (
                "admin.register_analysis_chart",
                lambda: admin.register_analysis_chart(
                    context["sourceId"], context["assignmentId"], scenario["analysisChart"]
                ),
                ["ok", "data"],
            ),
        ]

        for action, fn, required_paths in actions:
            response = self._execute_step(len(steps) + 1, action, fn, steps)
            validations.append(self.validator.validate_envelope(action, response))
            validations.extend(self.validator.validate_required_paths(action, response, required_paths))

        clock = HarnessClock.from_scenario(scenario)
        store.write_json("clock/clock_sequence.json", clock.to_artifact())
        validations.extend(self._validate_clock_sequence(clock))
        tick = scenario["tick"]
        poll_every_ticks = int(tick["pollEveryTicks"])

        for clock_tick in clock.ticks():
            index = clock_tick.tick_index
            logical_now = clock_tick.logical_now
            context["finalLogicalNow"] = logical_now

            feeder_action = f"test_feeder.tick.logicalNow.{logical_now[11:16]}"
            feeder_response = self._execute_step(
                len(steps) + 1,
                feeder_action,
                lambda logical_now=logical_now, index=index: feeder.tick(context["sourceId"], logical_now, index),
                steps,
            )
            validations.append(self.validator.validate_envelope(feeder_action, feeder_response))
            validations.append(
                self._expect_equal(
                    f"sprint11.clock.feeder.logical_now.{index}",
                    feeder_response.get("data", {}).get("logicalCursorTime"),
                    logical_now,
                )
            )

            action = f"admin.test_tick.logicalNow.{logical_now[11:16]}"
            response = self._execute_step(
                len(steps) + 1,
                action,
                lambda logical_now=logical_now, index=index: admin.tick(logical_now, index),
                steps,
            )
            validations.append(self.validator.validate_envelope(action, response))
            validations.append(
                self._expect_equal(
                    f"sprint11.clock.admin.logical_now.{index}",
                    response.get("data", {}).get("logicalNow"),
                    logical_now,
                )
            )

            if index % poll_every_ticks == 0:
                poll_action = f"drift.poll_once.logicalNow.{logical_now[11:16]}"
                poll_response = self._execute_step(
                    len(steps) + 1,
                    poll_action,
                    lambda adapter_id=context["adapterId"], logical_now=logical_now: drift.poll_once(
                        adapter_id, logical_now
                    ),
                    steps,
                )
                validations.append(self.validator.validate_envelope(poll_action, poll_response))
                if isinstance(poll_response, dict):
                    poll_responses.append(poll_response)
                validations.append(
                    self._expect_equal(
                        f"sprint11.clock.drift_poll.logical_now.{index}",
                        poll_response.get("data", {}).get("logicalNow"),
                        logical_now,
                    )
                )

        timeseries = self._execute_step(
            len(steps) + 1,
            "drift.timeseries_data",
            lambda: drift.timeseries_data(context["sourceId"]),
            steps,
        )
        validations.append(self.validator.validate_envelope("drift.timeseries_data", timeseries))
        validations.extend(
            self.validator.validate_required_paths(
                "drift.timeseries_data",
                timeseries,
                ["data.sourceId", "data.series", "data.events"],
            )
        )
        store.write_json("timeseries/timeseries_data.json", timeseries)
        store.write_json("debug/poll_responses.json", poll_responses)
        self._run_sprint2_validations(
            context, scenario, admin, drift, feeder, store, steps, validations, timeseries, poll_responses
        )

        event_id = self._first_event_id(timeseries)
        if event_id:
            analysis = self._execute_step(
                len(steps) + 1,
                "drift.event_analysis",
                lambda: drift.analysis(context["sourceId"], event_id),
                steps,
            )
            validations.append(self.validator.validate_envelope("drift.event_analysis", analysis))
            validations.extend(
                self.validator.validate_required_paths(
                    "drift.event_analysis",
                    analysis,
                    [
                        "data.sourceId",
                        "data.eventId",
                        "data.analysisChartId",
                        "data.chartId",
                        "data.chartDefinition",
                        "data.chartPayload",
                    ],
                )
            )
            validations.extend(self._validate_sprint4_analysis(event_id, analysis, scenario))
            store.write_json(f"analysis_payloads/{_short_artifact_name(event_id)}.json", analysis)
            interpretation: dict[str, Any] | None = None
            if scenario.get("expectations", {}).get("llmInterpretationRequired") is True:
                interpretation = self._run_sprint9_llm_interpretation(
                    event_id, analysis, scenario, llm, store, steps, validations
                )
            if scenario.get("expectations", {}).get("chartRuntimeSmokeRequired") is True:
                self._run_sprint14_chart_runtime_smoke(analysis, interpretation, scenario, store, steps, validations)
            self._run_sprint5_idempotency(
                context,
                event_id,
                drift,
                store,
                steps,
                validations,
            )
        if scenario.get("expectations", {}).get("uiSmokeRequired") is True:
            self._run_sprint13_ui_smoke(context, store, steps, validations)
        if scenario.get("expectations", {}).get("proxyRecordRequired") is True:
            self._run_sprint15_proxy_record_validation(store, validations)

    def _run_sprint2_validations(
        self,
        context: dict[str, str],
        scenario: dict[str, Any],
        admin: AdminClient,
        drift: DriftClient,
        feeder: TestFeederClient,
        store: ArtifactStore,
        steps: list[StepResult],
        validations: list[ValidationResult],
        timeseries: Any,
        poll_responses: list[dict[str, Any]],
    ) -> None:
        expectations = scenario.get("expectations", {})
        expected_raw_events = int(expectations.get("rawEventCount", 20))
        expected_bucket_count = int(expectations.get("bucketCount", 2))
        expected_method_run_count = int(expectations.get("methodRunCount", expected_bucket_count))
        expected_cursor_time = expectations.get("adapterCursorTime", "2026-01-01T00:20:00Z")
        expected_state_bucket_end = expectations.get("methodStateLastBucketEnd", expected_cursor_time)
        expected_bucket_row_count = int(expectations.get("bucketRowCount", 10))
        expected_drift_event_minimum = int(expectations.get("driftEventMinimum", 1))
        feature_id = scenario.get("methodAssignment", {}).get("featureId", "metric")

        raw_events = self._execute_step(
            len(steps) + 1,
            "test_feeder.debug.raw_events",
            lambda: feeder.raw_events(context["sourceId"]),
            steps,
        )
        buckets = self._execute_step(
            len(steps) + 1,
            "drift.debug.buckets",
            lambda: drift.buckets(context["sourceId"], context["adapterId"]),
            steps,
        )
        adapter_status = self._execute_step(
            len(steps) + 1,
            "drift.adapter_status",
            lambda: drift.adapter_status(context["adapterId"]),
            steps,
        )
        admin_adapter_status = self._execute_step(
            len(steps) + 1,
            "admin.adapter_status",
            lambda: admin.adapter_status(context["adapterId"]),
            steps,
        )
        store.write_json("debug/raw_events.json", raw_events)
        store.write_json("debug/buckets.json", buckets)
        store.write_json("debug/adapter_status.json", adapter_status)
        store.write_json("debug/admin_adapter_status.json", admin_adapter_status)
        method_runs = self._execute_step(
            len(steps) + 1,
            "drift.debug.method_runs",
            lambda: drift.method_runs(context["sourceId"], context["assignmentId"]),
            steps,
        )
        drift_events = self._execute_step(
            len(steps) + 1,
            "drift.debug.drift_events",
            lambda: drift.drift_events(context["sourceId"], context["assignmentId"]),
            steps,
        )
        method_state = self._execute_step(
            len(steps) + 1,
            "drift.debug.method_state",
            lambda: drift.method_state(context["assignmentId"]),
            steps,
        )
        store.write_json("debug/method_runs.json", method_runs)
        store.write_json("debug/drift_events.json", drift_events)
        store.write_json("debug/method_state.json", method_state)
        method_state_data = method_state.get("data", {}) if isinstance(method_state.get("data"), dict) else {}

        validations.extend(
            [
                self._expect_equal("sprint2.raw_event.count", raw_events.get("data", {}).get("count"), expected_raw_events),
                self._expect_equal("sprint2.bucket.count", buckets.get("data", {}).get("count"), expected_bucket_count),
                self._expect_equal(
                    f"sprint2.series.{feature_id}.count",
                    len(timeseries.get("data", {}).get("series", {}).get(feature_id, [])),
                    expected_bucket_count,
                ),
                self._expect_equal(
                    "sprint2.adapter.cursor_time",
                    adapter_status.get("data", {}).get("cursor_time"),
                    expected_cursor_time,
                ),
                self._expect_equal(
                    "sprint3.method_run.count",
                    method_runs.get("data", {}).get("count"),
                    expected_method_run_count,
                ),
                self._expect_equal(
                    "sprint3.method_state.last_bucket_end",
                    method_state_data.get("last_bucket_end"),
                    expected_state_bucket_end,
                ),
                self._expect_at_least(
                    "sprint3.drift_event.count",
                    drift_events.get("data", {}).get("count"),
                    expected_drift_event_minimum,
                ),
                self._expect_at_least(
                    f"sprint3.events.{feature_id}.count",
                    len(timeseries.get("data", {}).get("events", {}).get(feature_id, [])),
                    expected_drift_event_minimum,
                ),
            ]
        )
        bucket_rows = buckets.get("data", {}).get("rows", [])
        for index, row in enumerate(bucket_rows, start=1):
            validations.append(
                self._expect_equal(f"sprint2.bucket.{index}.row_count", row.get("row_count"), expected_bucket_row_count)
            )
        if expectations.get("bucketErrorRateMinimum") is not None:
            error_rates = [
                float(row.get("error_rate"))
                for row in bucket_rows
                if row.get("error_rate") is not None
            ]
            validations.append(
                self._expect_at_least_float(
                    "sprint20.bucket.error_rate.max",
                    max(error_rates) if error_rates else 0.0,
                    float(expectations["bucketErrorRateMinimum"]),
                )
            )
        validations.extend(self._validate_sprint7_runtime(method_runs, expectations))
        validations.extend(self._validate_sprint8_runtime(method_runs, expectations))
        validations.extend(self._validate_sprint11_time_policy(raw_events, buckets, adapter_status, method_runs, expectations))
        validations.extend(
            self._validate_sprint12_adapter_diagnostics(
                adapter_status,
                admin_adapter_status,
                poll_responses,
                expectations,
            )
        )
        if expectations.get("resetRecoveryRequired") is True:
            self._run_sprint12_reset_recovery(context, scenario, admin, store, steps, validations)

    def _expect_equal(self, name: str, actual: Any, expected: Any) -> ValidationResult:
        if actual == expected:
            return ValidationResult(name, "passed", "value matches", {"actual": actual, "expected": expected})
        return ValidationResult(name, "failed", "value does not match", {"actual": actual, "expected": expected})

    def _expect_at_least(self, name: str, actual: Any, minimum: int) -> ValidationResult:
        if isinstance(actual, int) and actual >= minimum:
            return ValidationResult(name, "passed", "value is at least minimum", {"actual": actual, "minimum": minimum})
        return ValidationResult(name, "failed", "value is below minimum", {"actual": actual, "minimum": minimum})

    def _expect_at_least_float(self, name: str, actual: Any, minimum: float) -> ValidationResult:
        try:
            value = float(actual)
        except (TypeError, ValueError):
            return ValidationResult(name, "failed", "value is not numeric", {"actual": actual, "minimum": minimum})
        if value >= minimum:
            return ValidationResult(name, "passed", "value is at least minimum", {"actual": value, "minimum": minimum})
        return ValidationResult(name, "failed", "value is below minimum", {"actual": value, "minimum": minimum})

    def _run_sprint13_ui_smoke(
        self,
        context: dict[str, str],
        store: ArtifactStore,
        steps: list[StepResult],
        validations: list[ValidationResult],
    ) -> None:
        state = self._execute_step(
            len(steps) + 1,
            "sprint13.ui_smoke.timeseries",
            lambda: run_timeseries_ui_smoke(context["sourceId"], self.config.drift_base_url, store),
            steps,
        )
        validations.extend(
            [
                self._expect_equal("sprint13.ui.source_id", state.get("sourceId"), context["sourceId"]),
                self._expect_at_least(
                    "sprint13.ui.series.metric.count",
                    len(state.get("series", {}).get("metric", [])),
                    1,
                ),
                self._expect_at_least(
                    "sprint13.ui.events.metric.count",
                    len(state.get("events", {}).get("metric", [])),
                    1,
                ),
                self._expect_at_least(
                    "sprint13.ui.event_markers.count",
                    len(state.get("eventMarkers", [])),
                    1,
                ),
                self._expect_at_least(
                    "sprint13.ui.analysis_links.count",
                    len(state.get("chartLinks", [])),
                    1,
                ),
                self._expect_equal(
                    "sprint13.ui.artifact.state_json",
                    (store.run_dir / "ui_state" / "state.json").exists(),
                    True,
                ),
            ]
        )

    def _validate_clock_sequence(self, clock: HarnessClock) -> list[ValidationResult]:
        ticks = clock.ticks()
        results = [
            self._expect_equal("sprint11.clock.sequence.count", len(ticks), clock.tick_count),
        ]
        previous = clock.start_time
        interval_seconds = clock.interval_minutes * 60
        for tick in ticks:
            current = self._parse_iso(tick.logical_now)
            results.append(
                self._expect_equal(
                    f"sprint11.clock.sequence.interval.{tick.tick_index}",
                    int((current - previous).total_seconds()),
                    interval_seconds,
                )
            )
            previous = current
        return results

    def _validate_sprint11_time_policy(
        self,
        raw_events: Any,
        buckets: Any,
        adapter_status: Any,
        method_runs: Any,
        expectations: dict[str, Any],
    ) -> list[ValidationResult]:
        if expectations.get("timePolicyValidationRequired") is not True:
            return []
        rows = raw_events.get("data", {}).get("rows", []) if isinstance(raw_events, dict) else []
        adapter_data = adapter_status.get("data", {}) if isinstance(adapter_status, dict) else {}
        results: list[ValidationResult] = []
        if expectations.get("sourceEventTimeRequired") is True:
            results.append(
                self._expect_equal(
                    "sprint11.time.raw_event.source_event_time_present",
                    all(bool(row.get("source_event_time")) for row in rows),
                    True,
                )
            )
        if expectations.get("eventTimeNormalizedRequired") is True:
            results.append(
                self._expect_equal(
                    "sprint11.time.raw_event.event_time_normalized",
                    all(row.get("event_time") != row.get("source_event_time") for row in rows),
                    True,
                )
            )
        expected_offset = expectations.get("sourceClockOffsetMs")
        if expected_offset is not None:
            results.append(
                self._expect_equal(
                    "sprint11.time.raw_event.source_clock_offset_ms_recorded",
                    sorted({row.get("source_clock_offset_ms") for row in rows}),
                    [int(expected_offset)],
                )
            )
        expected_collected_at = expectations.get("collectedAtMinimum")
        if expected_collected_at is not None:
            collected_values = [row.get("collected_at") for row in rows if row.get("collected_at")]
            results.append(
                self._expect_at_least(
                    "sprint11.time.raw_event.collected_at_present",
                    len(collected_values),
                    int(expected_collected_at),
                )
            )
        expected_status = expectations.get("adapterStatus")
        if expected_status is not None:
            results.append(
                self._expect_equal("sprint11.time.adapter.status", adapter_data.get("status"), expected_status)
            )
        if expectations.get("adapterUnusableRequired") is True:
            results.append(
                self._expect_equal(
                    "sprint11.time.adapter.unusable_on_large_offset",
                    adapter_data.get("status"),
                    "unusable",
                )
            )
        expected_rejected = expectations.get("futureRejectedRowsMinimum")
        if expected_rejected is not None:
            results.append(
                self._expect_at_least(
                    "sprint11.time.future_row.rejected",
                    raw_events.get("data", {}).get("futureRejectedRows", 0),
                    int(expected_rejected),
                )
            )
        if expectations.get("noBucketsExpected") is True:
            results.append(self._expect_equal("sprint11.time.bucket.count", buckets.get("data", {}).get("count"), 0))
        if expectations.get("noMethodRunsExpected") is True:
            results.append(
                self._expect_equal("sprint11.time.method_run.count", method_runs.get("data", {}).get("count"), 0)
            )
        return results

    def _validate_sprint12_adapter_diagnostics(
        self,
        adapter_status: Any,
        admin_adapter_status: Any,
        poll_responses: list[dict[str, Any]],
        expectations: dict[str, Any],
    ) -> list[ValidationResult]:
        if expectations.get("adapterDiagnosticsValidationRequired") is not True:
            return []
        adapter_data = adapter_status.get("data", {}) if isinstance(adapter_status, dict) else {}
        admin_data = admin_adapter_status.get("data", {}) if isinstance(admin_adapter_status, dict) else {}
        last_poll = poll_responses[-1].get("data", {}) if poll_responses else {}
        diagnostics = adapter_data.get("diagnostics", []) if isinstance(adapter_data.get("diagnostics"), list) else []
        poll_diagnostics = last_poll.get("diagnostics", []) if isinstance(last_poll.get("diagnostics"), list) else []
        diagnostic_codes = {item.get("code") for item in diagnostics if isinstance(item, dict)}
        poll_diagnostic_codes = {item.get("code") for item in poll_diagnostics if isinstance(item, dict)}
        diagnostic_severities = {item.get("severity") for item in diagnostics if isinstance(item, dict)}
        results = [
            self._expect_equal("sprint12.admin.adapter_status.ok", admin_adapter_status.get("ok"), True),
            self._expect_equal(
                "sprint12.admin.adapter_status.adapter_id",
                admin_data.get("adapterId"),
                adapter_data.get("adapterId"),
            ),
        ]
        expected_outcome = expectations.get("pollOutcome")
        if expected_outcome is not None:
            results.append(self._expect_equal("sprint12.poll.outcome", last_poll.get("outcome"), expected_outcome))
        expected_poll_status = expectations.get("pollStatus")
        if expected_poll_status is not None:
            results.append(self._expect_equal("sprint12.poll.status", last_poll.get("status"), expected_poll_status))
        expected_code = expectations.get("diagnosticsCode")
        if expected_code is not None:
            results.append(
                self._expect_equal(
                    "sprint12.adapter.diagnostics.code",
                    expected_code in diagnostic_codes or expected_code in poll_diagnostic_codes,
                    True,
                )
            )
        expected_severity = expectations.get("diagnosticsSeverity")
        if expected_severity is not None:
            results.append(
                self._expect_equal(
                    "sprint12.adapter.diagnostics.severity",
                    expected_severity in diagnostic_severities,
                    True,
                )
            )
        expected_rejected = expectations.get("pollRejectedRowsMinimum")
        if expected_rejected is not None:
            results.append(
                self._expect_at_least(
                    "sprint12.poll.rejected_rows",
                    int(last_poll.get("rejectedRows") or 0),
                    int(expected_rejected),
                )
            )
        return results

    def _run_sprint12_reset_recovery(
        self,
        context: dict[str, str],
        scenario: dict[str, Any],
        admin: AdminClient,
        store: ArtifactStore,
        steps: list[StepResult],
        validations: list[ValidationResult],
    ) -> None:
        reset_response = self._execute_step(
            len(steps) + 1,
            "sprint12.reset_recovery.admin_test_reset",
            lambda: admin.test_reset(context["sourceId"]),
            steps,
        )
        register_response = self._execute_step(
            len(steps) + 1,
            "sprint12.reset_recovery.register_adapter",
            lambda: admin.register_adapter(scenario["adapter"]),
            steps,
        )
        status_response = self._execute_step(
            len(steps) + 1,
            "sprint12.reset_recovery.adapter_status",
            lambda: admin.adapter_status(context["adapterId"]),
            steps,
        )
        store.write_json("debug/reset_recovery_reset.json", reset_response)
        store.write_json("debug/reset_recovery_register_adapter.json", register_response)
        store.write_json("debug/reset_recovery_adapter_status.json", status_response)
        diagnostics = status_response.get("data", {}).get("diagnostics", [])
        validations.extend(
            [
                self.validator.validate_envelope("sprint12.reset_recovery.reset", reset_response),
                self.validator.validate_envelope("sprint12.reset_recovery.register_adapter", register_response),
                self.validator.validate_envelope("sprint12.reset_recovery.adapter_status", status_response),
                self._expect_equal(
                    "sprint12.reset_recovery.status",
                    status_response.get("data", {}).get("status"),
                    "ready",
                ),
                self._expect_equal(
                    "sprint12.reset_recovery.diagnostics_empty",
                    diagnostics,
                    [],
                ),
            ]
        )

    def _validate_sprint4_analysis(self, event_id: str, analysis: Any, scenario: dict[str, Any]) -> list[ValidationResult]:
        expectations = scenario.get("expectations", {})
        expected_point_count = int(expectations.get("analysisPointCount", expectations.get("bucketCount", 2)))
        mean_difference_minimum = expectations.get("analysisMeanDifferenceMinimum", 2)
        expected_chart_id = scenario.get("analysisChart", {}).get("chartId", "CHART-STREAM-001")
        expected_runtime_method_key = scenario.get("methodAssignment", {}).get("runtimeMethodKey", "adwin_mean_stream")
        data = analysis.get("data", {}) if isinstance(analysis, dict) else {}
        payload = data.get("chartPayload", {}) if isinstance(data, dict) else {}
        series = payload.get("series", []) if isinstance(payload, dict) else []
        first_series = series[0] if series else {}
        points = first_series.get("points", []) if isinstance(first_series, dict) else []
        markers = payload.get("eventMarkers", []) if isinstance(payload, dict) else []
        metadata = payload.get("metadata", {}) if isinstance(payload, dict) else {}
        metrics = metadata.get("metrics", {}) if isinstance(metadata, dict) else {}
        layout = payload.get("layout", {}) if isinstance(payload, dict) else {}
        layout_areas = layout.get("areas", []) if isinstance(layout, dict) else []
        components = payload.get("components", []) if isinstance(payload, dict) else []
        payload_data = payload.get("data", {}) if isinstance(payload, dict) else {}
        metric_series = payload_data.get("metric_series", []) if isinstance(payload_data, dict) else []
        analysis_note = payload_data.get("analysis_note", []) if isinstance(payload_data, dict) else []
        notes_legend_components = [
            component
            for component in components
            if isinstance(component, dict)
            and (component.get("config") or {}).get("card_style") == "notes_legend"
        ]
        graph_components = [
            component
            for component in components
            if isinstance(component, dict)
            and component.get("componentType")
            in {"trend_line", "raw_signal_trend", "detector_statistic_view", "control_chart", "distance_metric_view"}
        ]
        data_source_row_counts = [
            len(rows)
            for rows in payload_data.values()
            if isinstance(rows, list)
        ]
        note_rows = [
            row
            for source, rows in payload_data.items()
            if isinstance(source, str)
            and (source.endswith(".notes") or source == "analysis_note" or "note" in source.lower())
            and isinstance(rows, list)
            for row in rows
            if isinstance(row, dict)
        ]
        results = [
            self._expect_equal("sprint4.analysis.chart_id", data.get("chartId"), expected_chart_id),
            self._expect_equal("sprint4.payload.chart_id", payload.get("chartId"), expected_chart_id),
            self._expect_equal("sprint4.payload.source_id", payload.get("sourceId"), data.get("sourceId")),
            self._expect_equal("sprint4.payload.event_id", payload.get("eventId"), event_id),
            self._expect_equal(
                "sprint4.payload.metadata.runtime_method_key",
                metadata.get("runtimeMethodKey"),
                expected_runtime_method_key,
            ),
        ]
        if expectations.get("legacySeriesPayloadRequired", True) is True:
            results.extend(
                [
                    self._expect_at_least("sprint4.payload.series.count", len(series), 1),
                    self._expect_equal("sprint4.payload.series.0.points.count", len(points), expected_point_count),
                    self._expect_at_least("sprint4.payload.event_markers.count", len(markers), 1),
                ]
            )
        if expectations.get("chartRuntimePayloadRequired") is True:
            graph_required = expectations.get("chartRuntimeGraphRequired", True) is True
            results.extend(
                [
                    self._expect_at_least("sprint10.payload.layout.areas.count", len(layout_areas), 3),
                    self._expect_at_least("sprint10.payload.components.count", len(components), 3),
                    self._expect_at_least(
                        "sprint10.payload.data.graph_source.max_count",
                        max(data_source_row_counts) if data_source_row_counts else len(metric_series),
                        expected_point_count,
                    ),
                    self._expect_at_least(
                        "sprint10.payload.data.analysis_note.count",
                        len(note_rows) if note_rows else len(analysis_note),
                        1,
                    ),
                    self._expect_at_least(
                        "sprint10.payload.components.notes_legend.count",
                        len(notes_legend_components),
                        1,
                    ),
                ]
            )
            if graph_required:
                results.append(self._expect_at_least("sprint10.payload.components.graph.count", len(graph_components), 1))
        if mean_difference_minimum is not None:
            results.append(
                self._expect_at_least(
                    "sprint4.payload.metadata.metrics.mean_difference",
                    int(metrics.get("meanDifference", 0)),
                    int(mean_difference_minimum),
                )
            )
        return results

    def _validate_sprint7_runtime(self, method_runs: Any, expectations: dict[str, Any]) -> list[ValidationResult]:
        if expectations.get("noMethodRunsExpected") is True or int(expectations.get("methodRunCount", 1)) == 0:
            return []
        rows = method_runs.get("data", {}).get("rows", []) if isinstance(method_runs, dict) else []
        diagnostics_rows = [
            row.get("result_json", {}).get("diagnostics", {})
            for row in rows
            if isinstance(row.get("result_json"), dict)
        ]
        metrics_rows = [
            row.get("result_json", {}).get("metrics", {})
            for row in rows
            if isinstance(row.get("result_json"), dict)
        ]
        implementations = [
            diagnostics.get("implementation")
            for diagnostics in diagnostics_rows
            if diagnostics.get("implementation")
        ]
        attempted = any(diagnostics.get("algorithmImplAttempted") is True for diagnostics in diagnostics_rows)
        fallback_rows = [
            diagnostics
            for diagnostics in diagnostics_rows
            if diagnostics.get("implementation") == "deterministic_fallback"
            and diagnostics.get("algorithmImplAttempted") is True
        ]
        has_fallback_reason = all(bool(diagnostics.get("fallbackReason")) for diagnostics in fallback_rows)
        has_measurements_key = any("measurements" in metrics for metrics in metrics_rows)
        return [
            self._expect_at_least("sprint7.runtime.implementation_present", len(implementations), 1),
            self._expect_equal("sprint7.runtime.algorithm_attempted", attempted, True),
            self._expect_equal("sprint7.runtime.fallback_reason_recorded_if_used", has_fallback_reason, True),
            self._expect_equal("sprint7.runtime.measurements_key_present", has_measurements_key, True),
        ]

    def _validate_sprint8_runtime(self, method_runs: Any, expectations: dict[str, Any]) -> list[ValidationResult]:
        if expectations.get("algorithmImplSuccessRequired") is not True:
            return []
        rows = method_runs.get("data", {}).get("rows", []) if isinstance(method_runs, dict) else []
        successful_algorithm_runs = []
        processed_counts = []
        fallback_on_success = False
        for row in rows:
            result = row.get("result_json", {})
            if not isinstance(result, dict):
                continue
            diagnostics = result.get("diagnostics", {})
            metrics = result.get("metrics", {})
            measurements = metrics.get("measurements", {}) if isinstance(metrics, dict) else {}
            if diagnostics.get("algorithmImplSucceeded") is True:
                successful_algorithm_runs.append(row)
                if diagnostics.get("fallbackReason"):
                    fallback_on_success = True
                processed_count = measurements.get("PROCESSED_COUNT")
                if isinstance(processed_count, int):
                    processed_counts.append(processed_count)
        minimum_processed = int(expectations.get("algorithmProcessedCountMinimum", 1))
        return [
            self._expect_at_least("sprint8.case011.algorithm_impl_success", len(successful_algorithm_runs), 1),
            self._expect_equal("sprint8.case011.no_fallback_on_success", fallback_on_success, False),
            self._expect_at_least(
                "sprint8.case011.measurements.processed_count",
                max(processed_counts) if processed_counts else 0,
                minimum_processed,
            ),
        ]

    def _run_sprint9_llm_interpretation(
        self,
        event_id: str,
        analysis: Any,
        scenario: dict[str, Any],
        llm: LlmClient,
        store: ArtifactStore,
        steps: list[StepResult],
        validations: list[ValidationResult],
    ) -> dict[str, Any] | None:
        health = self._execute_step(len(steps) + 1, "llm.health", llm.health, steps)
        validations.append(self._expect_equal("sprint9.llm.health.ok", health.get("ok"), True))

        request = self._build_llm_request(analysis)
        safe_event_id = _short_artifact_name(event_id)
        request_path = store.write_json(f"llm_requests/{safe_event_id}.json", request)

        create_response = self._execute_step(
            len(steps) + 1,
            "llm.interpret_chart.create_job",
            lambda: llm.create_chart_job(request),
            steps,
        )
        store.write_json(f"llm_responses/{safe_event_id}.create.json", create_response)
        job_id = create_response.get("jobId")
        validations.extend(
            [
                self._expect_equal("sprint9.llm.request.event_id", request.get("eventId"), event_id),
                self._expect_equal(
                    "sprint9.llm.request.chart_payload",
                    request.get("payload", {}).get("eventId"),
                    event_id,
                ),
                self._expect_equal("sprint9.llm.job_create.ok", create_response.get("ok"), True),
                self._expect_equal("sprint9.llm.job_create.job_id", bool(job_id), True),
            ]
        )
        if not job_id:
            return None

        get_response = self._poll_llm_job(job_id, llm, steps)
        store.write_json(f"llm_responses/{safe_event_id}.get.json", get_response)
        result = get_response.get("result", {}) if isinstance(get_response, dict) else {}
        validations.extend(
            [
                self._expect_equal("sprint9.llm.job_get.ok", get_response.get("ok"), True),
                self._expect_equal("sprint9.llm.job_get.status", get_response.get("status"), "succeeded"),
                self._expect_equal("sprint9.llm.job_get.result_present", isinstance(result, dict), True),
                self._expect_equal("sprint9.llm.job_get.chart_note", bool(result.get("chartNote")), True),
                self._expect_equal("sprint9.llm.artifact.request", request_path.exists(), True),
            ]
        )
        if scenario.get("expectations", {}).get("llmComponentNotesRequired") is True:
            component_notes = result.get("componentNotes", []) if isinstance(result, dict) else []
            validations.append(
                self._expect_at_least(
                    "sprint10.llm.component_notes.count",
                    len(component_notes) if isinstance(component_notes, list) else 0,
                    1,
                )
            )
        return result if isinstance(result, dict) else None

    def _run_sprint14_chart_runtime_smoke(
        self,
        analysis: Any,
        interpretation: dict[str, Any] | None,
        scenario: dict[str, Any],
        store: ArtifactStore,
        steps: list[StepResult],
        validations: list[ValidationResult],
    ) -> None:
        payload = merge_interpretation_into_chart_payload(analysis, interpretation)
        store.write_json("chart_test_state/input_payload.json", payload)
        state = self._execute_step(
            len(steps) + 1,
            "chart_runtime.smoke",
            lambda: run_chart_runtime_smoke(payload, store),
            steps,
        )
        checks = state.get("checks", {}) if isinstance(state, dict) else {}
        dom = state.get("dom", {}) if isinstance(state, dict) else {}
        expected_chart_id = analysis.get("data", {}).get("chartId", "CHART-STREAM-001") if isinstance(analysis, dict) else "CHART-STREAM-001"
        state_components = state.get("components", []) if isinstance(state, dict) else []
        state_bindings = state.get("dataBindings", []) if isinstance(state, dict) else []
        has_graph_rows = any(
            isinstance(binding, dict)
            and binding.get("componentType")
            in {"trend_line", "raw_signal_trend", "detector_statistic_view", "control_chart", "distance_metric_view"}
            and int(binding.get("rowCount") or 0) > 0
            for binding in state_bindings
        )
        has_summary_context = any(
            isinstance(binding, dict)
            and binding.get("componentType") == "decision_card"
            and int(binding.get("rowCount") or 0) > 0
            for binding in state_bindings
        )
        has_event_context = checks.get("hasEventMarker") is True or has_summary_context or any(
            isinstance(binding, dict)
            and binding.get("componentType") == "state_timeline"
            and int(binding.get("rowCount") or 0) > 0
            for binding in state_bindings
        )
        has_notes_legend = checks.get("hasNotesLegend") is True or any(
            isinstance(component, dict) and component.get("cardStyle") == "notes_legend"
            for component in state_components
        )
        graph_required = scenario.get("expectations", {}).get("chartRuntimeGraphRequired", True) is True
        validations.extend(
            [
                self._expect_equal("sprint14.chart_state.chart_id", state.get("chartId"), expected_chart_id),
                self._expect_at_least("sprint14.chart_state.components.count", state.get("componentCount", 0), 3),
                self._expect_equal("sprint14.chart_state.event_context", has_event_context, True),
                self._expect_equal("sprint14.chart_state.notes_legend", has_notes_legend, True),
                self._expect_equal(
                    "sprint14.chart_state.llm_component_notes",
                    checks.get("hasLlmComponentNotes"),
                    True,
                ),
                self._expect_at_least(
                    "sprint14.chart_state.dom.rendered_components",
                    dom.get("renderedComponentCount", 0),
                    3,
                ),
                self._expect_equal(
                    "sprint14.chart_state.artifact.state",
                    (store.run_dir / "chart_test_state" / "state.json").exists(),
                    True,
                ),
                self._expect_equal(
                    "sprint14.chart_state.artifact.screenshot",
                    (store.run_dir / "chart_test_state" / "chart_runtime.png").exists(),
                    True,
                ),
            ]
        )
        if graph_required:
            validations.append(
                self._expect_equal(
                    "sprint14.chart_state.trend_line.data_rows",
                    has_graph_rows,
                    True,
                )
            )

    def _run_sprint15_proxy_record_validation(
        self,
        store: ArtifactStore,
        validations: list[ValidationResult],
    ) -> None:
        proxy_calls_dir = store.run_dir / "proxy_calls"
        proxy_call_files = sorted(proxy_calls_dir.glob("*.json")) if proxy_calls_dir.exists() else []
        first_record = json.loads(proxy_call_files[0].read_text(encoding="utf-8")) if proxy_call_files else {}
        validations.extend(
            [
                self._expect_equal("sprint15.proxy_calls.dir_exists", proxy_calls_dir.exists(), True),
                self._expect_at_least("sprint15.proxy_calls.count", len(proxy_call_files), 1),
                self._expect_equal("sprint15.proxy_calls.first.method_present", bool(first_record.get("method")), True),
                self._expect_equal(
                    "sprint15.proxy_calls.first.target_url_present",
                    bool(first_record.get("targetUrl")),
                    True,
                ),
                self._expect_equal(
                    "sprint15.proxy_calls.first.status_code_present",
                    first_record.get("statusCode") is not None,
                    True,
                ),
                self._expect_equal(
                    "sprint15.proxy_calls.first.duration_present",
                    first_record.get("durationMs") is not None,
                    True,
                ),
            ]
        )

    def _build_llm_request(self, analysis: Any) -> dict[str, Any]:
        data = analysis.get("data", {}) if isinstance(analysis, dict) else {}
        chart_payload = dict(data.get("chartPayload", {}) if isinstance(data, dict) else {})
        metadata = chart_payload.get("metadata", {}) if isinstance(chart_payload.get("metadata"), dict) else {}
        return {
            "eventId": data.get("eventId"),
            "sourceId": data.get("sourceId"),
            "analysisChartId": data.get("analysisChartId"),
            "chartId": data.get("chartId"),
            "payload": chart_payload,
            "question": "이 drift event analysis chart를 한국어로 요약하고 해석상 주의점을 설명해 주세요.",
            "runtimeDiagnostics": metadata.get("diagnostics", {}),
            "runtimeMetrics": metadata.get("metrics", {}),
        }

    def _poll_llm_job(self, job_id: str, llm: LlmClient, steps: list[StepResult]) -> Any:
        last_response: Any = None
        for _ in range(50):
            last_response = self._execute_step(
                len(steps) + 1,
                "llm.interpret_chart.get_job",
                lambda job_id=job_id: llm.get_chart_job(job_id),
                steps,
            )
            if isinstance(last_response, dict) and last_response.get("status") in {"succeeded", "failed"}:
                return last_response
            time.sleep(0.2)
        return last_response

    def _run_sprint5_idempotency(
        self,
        context: dict[str, str],
        event_id: str,
        drift: DriftClient,
        store: ArtifactStore,
        steps: list[StepResult],
        validations: list[ValidationResult],
    ) -> None:
        before = self._execute_step(
            len(steps) + 1,
            "drift.debug.counts.before_idempotency",
            lambda: drift.counts(context["sourceId"], context["adapterId"], context["assignmentId"]),
            steps,
        )
        duplicate_poll = self._execute_step(
            len(steps) + 1,
            "drift.poll_once.duplicate_final_logicalNow",
            lambda: drift.poll_once(context["adapterId"], context["finalLogicalNow"]),
            steps,
        )
        after_poll = self._execute_step(
            len(steps) + 1,
            "drift.debug.counts.after_duplicate_poll",
            lambda: drift.counts(context["sourceId"], context["adapterId"], context["assignmentId"]),
            steps,
        )
        duplicate_analysis = self._execute_step(
            len(steps) + 1,
            "drift.event_analysis.duplicate_read_only",
            lambda: drift.analysis(context["sourceId"], event_id),
            steps,
        )
        after_analysis = self._execute_step(
            len(steps) + 1,
            "drift.debug.counts.after_duplicate_analysis",
            lambda: drift.counts(context["sourceId"], context["adapterId"], context["assignmentId"]),
            steps,
        )
        store.write_json("debug/idempotency_before.json", before)
        store.write_json("debug/idempotency_duplicate_poll.json", duplicate_poll)
        store.write_json("debug/idempotency_after_poll.json", after_poll)
        store.write_json("debug/idempotency_duplicate_analysis.json", duplicate_analysis)
        store.write_json("debug/idempotency_after_analysis.json", after_analysis)

        validations.append(self.validator.validate_envelope("sprint5.duplicate_poll", duplicate_poll))
        validations.append(self.validator.validate_envelope("sprint5.duplicate_analysis", duplicate_analysis))
        before_data = before.get("data", {})
        after_poll_data = after_poll.get("data", {})
        after_analysis_data = after_analysis.get("data", {})
        for key in ["bucketCount", "methodRunCount", "driftEventCount", "adapterCursorTime"]:
            validations.append(
                self._expect_equal(
                    f"sprint5.idempotency.poll.{key}",
                    after_poll_data.get(key),
                    before_data.get(key),
                )
            )
        for key in [
            "bucketCount",
            "methodRunCount",
            "driftEventCount",
            "analysisChartRegistrationCount",
            "adapterCursorTime",
        ]:
            validations.append(
                self._expect_equal(
                    f"sprint5.idempotency.analysis.{key}",
                    after_analysis_data.get(key),
                    after_poll_data.get(key),
                )
            )

    def _execute_step(
        self,
        index: int,
        action: str,
        fn: Callable[[], Any],
        steps: list[StepResult],
    ) -> Any:
        started_at = utc_now_iso()
        try:
            response = fn()
            steps.append(
                StepResult(index=index, action=action, status="passed", started_at=started_at, finished_at=utc_now_iso())
            )
            return response
        except Exception as exc:
            steps.append(
                StepResult(
                    index=index,
                    action=action,
                    status="failed",
                    started_at=started_at,
                    finished_at=utc_now_iso(),
                    error=f"{exc.__class__.__name__}: {exc}",
                )
            )
            raise

    def _first_event_id(self, timeseries: Any) -> str | None:
        if not isinstance(timeseries, dict):
            return None
        events = timeseries.get("data", {}).get("events", {})
        if not isinstance(events, dict):
            return None
        for event_list in events.values():
            if isinstance(event_list, list) and event_list:
                event = event_list[0]
                if isinstance(event, dict):
                    return event.get("eventId")
        return None

    def _make_run_id(self, scenario_id: str, mode: str) -> str:
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{stamp}_{scenario_id.lower()}_mode{mode.lower()}"

    def _parse_iso(self, value: str) -> datetime:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))

    def _format_iso(self, value: datetime) -> str:
        return value.replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _short_artifact_name(value: str, limit: int = 80) -> str:
    safe_value = safe_name(value)
    if len(safe_value) <= limit:
        return safe_value
    digest = hashlib.sha1(value.encode("utf-8")).hexdigest()[:10]
    return f"{safe_value[: limit - 11]}_{digest}"
