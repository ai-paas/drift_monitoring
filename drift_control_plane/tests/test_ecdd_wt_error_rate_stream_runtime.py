from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone

from drift_server.app.drift.runtime_registry import get_runtime_method
from drift_server.app.runtime_methods.ecdd_wt_error_rate_stream import run_ecdd_wt_error_rate_stream


def _assignment(variant_id: str) -> dict:
    return {
        "assignment_id": f"assign-{variant_id.lower()}",
        "runtime_method_key": "ecdd_wt_error_rate_stream",
        "params_json": json.dumps(
            {
                "variant_id": variant_id,
                "error_col": "error",
                "lambda": 0.2,
                "min_instances": 30,
                "min_reference_size": 30,
                "min_current_size": 30,
                "maxStatePoints": 500,
                "errorRateShiftThreshold": 0.12,
            }
        ),
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


def _run_values(variant_id: str) -> dict:
    state = {}
    output = {}
    low_error = [1 if index % 20 == 0 else 0 for index in range(50)]
    high_error = [0] * 10 + [1] * 40
    for index, errors in enumerate([low_error, low_error, low_error, low_error, high_error, high_error, high_error]):
        output = run_ecdd_wt_error_rate_stream(_assignment(variant_id), _bucket(index, errors), state)
        state = output["nextState"]
    return output


def test_registry_resolves_ecdd_wt_aliases() -> None:
    assert get_runtime_method("ecdd_wt_error_rate_stream") is run_ecdd_wt_error_rate_stream
    assert get_runtime_method("ecdd_wt_standard") is run_ecdd_wt_error_rate_stream
    assert get_runtime_method("ecdd_wt_warning_drift") is run_ecdd_wt_error_rate_stream
    assert get_runtime_method("ecdd_wt_error_stream") is run_ecdd_wt_error_rate_stream


def test_ecdd_wt_runtime_detects_error_rate_shift() -> None:
    output = _run_values("ECDD_WT_WARNING_DRIFT")

    assert output["runStatus"] == "success"
    assert output["level"] == "drift"
    assert output["event"] is not None
    assert output["diagnostics"]["algorithmImplSucceeded"] is True
    assert output["metrics"]["measurements"]["DRIFT_ALARM_STATE"] == "drift_detected"
