from __future__ import annotations

from typing import Any

from drift_server.app.db import get_connection
from drift_server.app.drift.payload_registry import PayloadAdapterNotFound, get_payload_adapter
from drift_server.app.repositories.adapter_state_repository import AdapterStateRepository
from drift_server.app.repositories.analysis_chart_repository import AnalysisChartRepository
from drift_server.app.repositories.bucket_repository import BucketRepository
from drift_server.app.repositories.event_repository import EventRepository
from drift_server.app.repositories.method_repository import MethodRepository


class PayloadContextInvalid(RuntimeError):
    def __init__(self, details: dict[str, Any]) -> None:
        self.details = details
        super().__init__("event analysis context is incomplete")


class PayloadAdapterError(RuntimeError):
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


class DriftService:
    def __init__(self, runtime_state: Any) -> None:
        self.runtime_state = runtime_state

    def get_timeseries_data(self, source_id: str, resolution: str) -> dict[str, Any]:
        with get_connection() as conn:
            bucket_repo = BucketRepository(conn)
            feature_id = bucket_repo.first_feature_id(source_id) or "metric"
            bucket_rows = bucket_repo.list_metric_buckets(source_id, feature_id)
            event_rows = EventRepository(conn).list_timeseries_events(source_id)
            method_rows = MethodRepository(conn).list_runs(source_id)
            assignments = _assignments_for_source(conn, source_id)
        points = [
            {
                "time": row["window_end"],
                "windowStart": row["window_start"],
                "windowEnd": row["window_end"],
                "value": row["error_rate"] if row["feature_id"] == "error_rate" else row["mean_value"],
                "rowCount": row["row_count"],
                "errorCount": row["error_count"],
                "errorRate": row["error_rate"],
                "meanConfidence": row["mean_confidence"],
            }
            for row in bucket_rows
        ]
        score_points = _method_score_points_for_timeseries(method_rows, assignments, feature_id)
        if score_points:
            points = score_points
        full_domain = [points[0]["windowStart"], points[-1]["windowEnd"]] if points else [
            "2026-01-01T00:00:00Z",
            "2026-01-01T00:20:00Z",
        ]
        return {
            "sourceId": source_id,
            "modelId": source_id,
            "fullDomain": full_domain,
            "features": [{"featureId": feature_id, "label": _feature_label(feature_id), "valueType": "numeric", "unit": None}],
            "series": {feature_id: points},
            "events": {feature_id: [_format_event(row) for row in event_rows]},
            "resolution": resolution,
            "pollIntervalMs": 600000,
        }

    # @managed-contract contract_id=drift_service.DriftService.build_event_analysis level=P0
    def build_event_analysis(self, source_id: str, event_id: str) -> dict[str, Any]:
        with get_connection() as conn:
            events = EventRepository(conn)
            methods = MethodRepository(conn)
            charts = AnalysisChartRepository(conn)
            buckets = BucketRepository(conn)
            event = events.get_event(source_id, event_id)
            if event is None:
                raise KeyError("DRIFT_EVENT_NOT_FOUND")
            method_run = methods.get_run(event["method_run_id"])
            assignment = _assignment_by_id(conn, event["assignment_id"])
            method_state = methods.get_state(event["assignment_id"]) or {}
            chart = charts.get_for_assignment(source_id, event["assignment_id"])
            bucket_rows = buckets.list_metric_buckets(source_id, event["feature_id"])

        if method_run is None or assignment is None or chart is None:
            raise PayloadContextInvalid(
                {
                    "eventId": event_id,
                    "hasMethodRun": method_run is not None,
                    "hasAssignment": assignment is not None,
                    "hasAnalysisChart": chart is not None,
                }
            )

        context = self._build_analysis_context(source_id, event, method_run, assignment, method_state, chart, bucket_rows)
        key = context["analysisChart"]["payloadAdapterKey"]
        try:
            payload_adapter = get_payload_adapter(key)
        except PayloadAdapterNotFound:
            raise
        try:
            chart_payload = payload_adapter(context)
        except Exception as exc:  # noqa: BLE001
            raise PayloadAdapterError(str(exc)) from exc

        return {
            "sourceId": source_id,
            "eventId": event_id,
            "analysisChartId": context["analysisChart"]["analysisChartId"],
            "chartId": context["analysisChart"]["chartId"],
            "chartDefinitionId": context["analysisChart"]["chartDefinitionId"],
            "chartDefinition": context["chartDefinition"],
            "chartPayload": chart_payload,
        }

    def get_counts(self, source_id: str, adapter_id: str | None, assignment_id: str | None) -> dict[str, Any]:
        with get_connection() as conn:
            adapter_cursor_time = None
            if adapter_id:
                row = AdapterStateRepository(conn).get(adapter_id)
                adapter_cursor_time = row["cursor_time"] if row else None
            return {
                "sourceId": source_id,
                "adapterId": adapter_id,
                "assignmentId": assignment_id,
                "bucketCount": BucketRepository(conn).count(source_id),
                "methodRunCount": MethodRepository(conn).count_runs(source_id, assignment_id),
                "driftEventCount": EventRepository(conn).count_events(source_id, assignment_id),
                "analysisChartRegistrationCount": AnalysisChartRepository(conn).count(source_id),
                "adapterCursorTime": adapter_cursor_time,
            }

    # @managed-contract contract_id=drift_service.DriftService._build_analysis_context level=P0
    def _build_analysis_context(
        self,
        source_id: str,
        event: dict[str, Any],
        method_run: dict[str, Any],
        assignment: dict[str, Any],
        method_state: dict[str, Any],
        chart: dict[str, Any],
        bucket_rows: list[Any],
    ) -> dict[str, Any]:
        source = self.runtime_state.sources.get(source_id, {"sourceId": source_id, "sourceType": "unknown", "title": source_id})
        adapter = self.runtime_state.adapters.get(event["adapter_id"], {"adapterId": event["adapter_id"], "sourceId": source_id})
        return {
            "source": {
                "sourceId": source_id,
                "sourceTitle": source.get("title") or source.get("sourceTitle") or source_id,
                "sourceType": source.get("sourceType"),
                "sourceUrl": source.get("sourceUrl"),
            },
            "adapter": adapter,
            "feature": {
                "featureId": event["feature_id"],
                "featureLabel": _feature_label(event["feature_id"]),
                "valueType": "numeric",
                "unit": None,
            },
            "assignment": {
                "assignmentId": assignment["assignment_id"],
                "sourceId": assignment["source_id"],
                "adapterId": assignment["adapter_id"],
                "featureId": assignment["feature_id"],
                "runtimeMethodKey": assignment["runtime_method_key"],
                "params": assignment["params_json"],
                "threshold": assignment["threshold_json"],
                "windowConfig": assignment["window_config_json"],
            },
            "methodRun": {
                "methodRunId": method_run["method_run_id"],
                "windowStart": method_run["window_start"],
                "windowEnd": method_run["window_end"],
                "runStatus": method_run["run_status"],
                "level": method_run["level"],
                "score": method_run["score"],
                "result": method_run["result_json"],
            },
            "methodState": method_state,
            "driftEvent": {
                "eventId": event["event_id"],
                "eventStart": event["event_start"],
                "eventEnd": event["event_end"],
                "level": event["event_level"],
                "score": event["score"],
                "payload": event["payload_json"],
            },
            "analysisChart": {
                "analysisChartId": chart["analysis_chart_id"],
                "chartId": chart["chart_id"],
                "chartDefinitionId": chart["chart_definition_id"],
                "payloadAdapterKey": chart["payload_adapter_key"],
            },
            "chartDefinition": chart["chart_definition_json"],
            "buckets": [_format_bucket_for_payload(row) for row in bucket_rows],
            "runtimeResult": method_run["result_json"],
            "payloadAdapterConfig": chart["payload_adapter_config_json"],
        }


def _assignment_by_id(conn: Any, assignment_id: str) -> dict[str, Any] | None:
    from drift_server.app.repositories.util import row_to_dict

    row = conn.execute("SELECT * FROM source_method_assignment WHERE assignment_id = ?", (assignment_id,)).fetchone()
    return row_to_dict(row)


def _assignments_for_source(conn: Any, source_id: str) -> dict[str, dict[str, Any]]:
    from drift_server.app.repositories.util import rows_to_dicts

    rows = conn.execute(
        """
        SELECT assignment_id, feature_id, runtime_method_key
        FROM source_method_assignment
        WHERE source_id = ? AND enabled = 1
        """,
        (source_id,),
    ).fetchall()
    return {str(row["assignment_id"]): row for row in rows_to_dicts(rows)}


def _method_score_points_for_timeseries(
    method_rows: list[dict[str, Any]],
    assignments: dict[str, dict[str, Any]],
    feature_id: str,
) -> list[dict[str, Any]]:
    eligible = {
        assignment_id
        for assignment_id, assignment in assignments.items()
        if assignment.get("feature_id") == feature_id
        and assignment.get("runtime_method_key") == "generic_probability_distance_window"
    }
    if not eligible:
        return []
    rows = [
        row
        for row in method_rows
        if row.get("assignment_id") in eligible
        and row.get("feature_id") == feature_id
        and row.get("score") is not None
        and row.get("run_status") == "success"
    ]
    return [
        {
            "time": row["window_end"],
            "windowStart": row["window_start"],
            "windowEnd": row["window_end"],
            "value": row["score"],
            "rowCount": None,
            "errorCount": None,
            "errorRate": None,
            "meanConfidence": None,
        }
        for row in sorted(rows, key=lambda item: (item["window_start"], item["method_run_id"]))
    ]


# @managed-contract contract_id=drift_service._format_event level=P0
def _format_event(row: Any) -> dict[str, Any]:
    return {
        "eventId": row["event_id"],
        "methodRunId": row["method_run_id"],
        "assignmentId": row["assignment_id"],
        "featureId": row["feature_id"],
        "eventStart": row["event_start"],
        "eventEnd": row["event_end"],
        "eventLevel": row["event_level"],
        "title": row["event_title"],
        "score": row["score"],
    }


# @managed-contract contract_id=drift_service._format_bucket_for_payload level=P0
def _format_bucket_for_payload(row: Any) -> dict[str, Any]:
    payload = row["payload_json"]
    if isinstance(payload, str):
        import json

        payload = json.loads(payload)
    value = row["error_rate"] if row["feature_id"] == "error_rate" else row["mean_value"]
    return {
        "bucketId": row["bucket_id"],
        "bucketStart": row["window_start"],
        "bucketEnd": row["window_end"],
        "v": value,
        "count": row["row_count"],
        "min": row["min_value"],
        "max": row["max_value"],
        "errorCount": row["error_count"],
        "errorRate": row["error_rate"],
        "meanConfidence": row["mean_confidence"],
        "status": "empty" if int(row["row_count"]) == 0 else "ok",
        "payload": payload,
    }


def _feature_label(feature_id: str) -> str:
    if feature_id == "error_rate":
        return "Error rate"
    return feature_id or "metric"
