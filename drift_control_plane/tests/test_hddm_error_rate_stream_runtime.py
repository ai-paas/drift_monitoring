from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone

from drift_server.app.drift.runtime_registry import get_runtime_method
from drift_server.app.runtime_methods.hddm_error_rate_stream import (
    run_hddm_a_error_rate_stream,
    run_hddm_w_error_rate_stream,
)


def _assignment(runtime_key: str, variant_id: str) -> dict:
    params = {
        "variant_id": variant_id,
        "error_col": "error",
        "min_instances": 30,
        "min_reference_size": 30,
        "min_current_size": 30,
        "errorRateShiftThreshold": 0.12,
        "maxStatePoints": 500,
    }
    if variant_id.startswith("HDDM_W"):
        params["lambda"] = 0.3
    if variant_id.endswith("TWO_SIDED") or variant_id.endswith("RECENT_ERROR_WEIGHTING"):
        params["two_sided"] = True
    return {
        "assignment_id": f"assign-{variant_id.lower()}",
        "runtime_method_key": runtime_key,
        "params_json": json.dumps(params),
    }


def _bucket(index: int, errors: list[int]) -> dict:
    start = datetime(2026, 1, 1, tzinfo=timezone.utc) + timedelta(minutes=10 * index)
    end = start + timedelta(minutes=10)
    rows = [
        {
            "time": (start + timedelta(seconds=offset)).isoformat().replace("+00:00", "Z"),
            "error": error,
        }
        for offset, error in enumerate(errors)
    ]
    return {
        "bucket_id": f"bucket-{index:03d}",
        "window_start": start.isoformat().replace("+00:00", "Z"),
        "window_end": end.isoformat().replace("+00:00", "Z"),
        "error_rate": sum(errors) / len(errors),
        "payload": json.dumps({"errors": rows}),
    }


def _run_values(runtime_key: str, variant_id: str) -> dict:
    state = {}
    output = {}
    runner = run_hddm_a_error_rate_stream if runtime_key == "hddm_a_error_rate_stream" else run_hddm_w_error_rate_stream
    assignment = _assignment(runtime_key, variant_id)
    low_error = [1 if index % 20 == 0 else 0 for index in range(50)]
    high_error = [0] * 10 + [1] * 40
    for index, errors in enumerate([low_error, low_error, low_error, low_error, high_error, high_error, high_error, high_error]):
        output = runner(assignment, _bucket(index, errors), state)
        state = output["nextState"]
    return output


def test_registry_resolves_hddm_aliases() -> None:
    assert get_runtime_method("hddm_a_error_rate_stream") is run_hddm_a_error_rate_stream
    assert get_runtime_method("hddm_a_hoeffding_bound") is run_hddm_a_error_rate_stream
    assert get_runtime_method("hddm_a_warning_drift") is run_hddm_a_error_rate_stream
    assert get_runtime_method("hddm_a_two_sided") is run_hddm_a_error_rate_stream
    assert get_runtime_method("hddm_w_error_rate_stream") is run_hddm_w_error_rate_stream
    assert get_runtime_method("hddm_w_weighted_average") is run_hddm_w_error_rate_stream
    assert get_runtime_method("hddm_w_warning_drift") is run_hddm_w_error_rate_stream
    assert get_runtime_method("hddm_w_recent_error_weighting") is run_hddm_w_error_rate_stream


def test_hddm_a_runtime_detects_error_rate_shift() -> None:
    output = _run_values("hddm_a_error_rate_stream", "HDDM_A_WARNING_DRIFT")

    assert output["runStatus"] == "success"
    assert output["level"] == "drift"
    assert output["event"] is not None
    assert output["diagnostics"]["algorithmImplSucceeded"] is True
    assert output["metrics"]["measurements"]["DRIFT_ALARM_STATE"] == "drift_detected"


def test_hddm_w_runtime_detects_error_rate_shift() -> None:
    output = _run_values("hddm_w_error_rate_stream", "HDDM_W_WARNING_DRIFT")

    assert output["runStatus"] == "success"
    assert output["level"] == "drift"
    assert output["event"] is not None
    assert output["diagnostics"]["algorithmImplSucceeded"] is True
    assert output["metrics"]["measurements"]["DRIFT_ALARM_STATE"] == "drift_detected"
