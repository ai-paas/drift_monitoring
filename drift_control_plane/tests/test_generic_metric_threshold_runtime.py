from __future__ import annotations

import json

from drift_server.app.drift.runtime_registry import get_runtime_method
from drift_server.app.runtime_methods.generic_metric_threshold import run_generic_metric_threshold


def _assignment(direction: str = "greater_equal") -> dict:
    return {
        "assignment_id": "assign-generic-threshold",
        "runtime_method_key": "generic_metric_threshold_drift",
        "params_json": json.dumps(
            {
                "variant_id": "GENERIC_METRIC_THRESHOLD_DRIFT",
                "threshold": 0.7,
                "direction": direction,
            }
        ),
    }


def _bucket(value: float) -> dict:
    return {
        "bucket_id": "bucket-generic-threshold",
        "window_start": "2026-01-01T00:00:00Z",
        "window_end": "2026-01-01T00:10:00Z",
        "mean_value": value,
        "row_count": 10,
    }


def test_registry_resolves_generic_metric_threshold() -> None:
    assert get_runtime_method("generic_metric_threshold_drift") is run_generic_metric_threshold


def test_generic_metric_threshold_detects_upper_crossing() -> None:
    output = run_generic_metric_threshold(_assignment(), _bucket(0.9), {})

    assert output["runStatus"] == "success"
    assert output["level"] == "drift"
    assert output["event"] is not None
    assert output["metrics"]["measurements"]["DRIFT_ALARM_STATE"] == "drift_detected"
    assert output["diagnostics"]["implementation"] == "deterministic_threshold"
    assert output["diagnostics"]["algorithmImplAttempted"] is True
    assert output["diagnostics"]["algorithmImplSucceeded"] is True


def test_generic_metric_threshold_keeps_normal_below_upper_threshold() -> None:
    output = run_generic_metric_threshold(_assignment(), _bucket(0.2), {})

    assert output["runStatus"] == "success"
    assert output["level"] == "normal"
    assert output["event"] is None
