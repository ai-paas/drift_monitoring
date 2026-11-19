from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone

from drift_server.app.drift.runtime_registry import get_runtime_method
from drift_server.app.runtime_methods.bocd_stream import run_bocd_stream


def _assignment(variant_id: str) -> dict:
    return {
        "assignment_id": f"assign-{variant_id.lower()}",
        "runtime_method_key": "bocd_stream",
        "params_json": json.dumps(
            {
                "variant_id": variant_id,
                "change_probability_threshold": 0.25,
                "predictive_probability_threshold": 0.01,
                "hazard_rate": 0.05,
                "warmup_size": 20,
                "run_length_truncation": 120,
                "min_reference_size": 20,
                "min_current_size": 20,
                "maxStatePoints": 200,
            }
        ),
    }


def _bucket(index: int, value: float) -> dict:
    start = datetime(2026, 1, 1, tzinfo=timezone.utc) + timedelta(minutes=index)
    end = start + timedelta(minutes=1)
    return {
        "bucket_id": f"bucket-{index:03d}",
        "window_start": start.isoformat().replace("+00:00", "Z"),
        "window_end": end.isoformat().replace("+00:00", "Z"),
        "mean_value": value,
    }


def _run_values(variant_id: str) -> dict:
    state = {}
    output = {}
    values = [0.0 for _ in range(80)] + [1.2 for _ in range(80)]
    for index, value in enumerate(values):
        output = run_bocd_stream(_assignment(variant_id), _bucket(index, value), state)
        state = output["nextState"]
    return output


def test_registry_resolves_bocd_aliases() -> None:
    assert get_runtime_method("bocd_stream") is run_bocd_stream
    assert get_runtime_method("bayesian_online_change_point_gaussian") is run_bocd_stream
    assert get_runtime_method("bocd_hazard_rate_variant") is run_bocd_stream
    assert get_runtime_method("bocd_predictive_probability") is run_bocd_stream


def test_bocd_runtime_detects_mean_shift() -> None:
    output = _run_values("BAYESIAN_ONLINE_CHANGE_POINT_GAUSSIAN")

    assert output["runStatus"] == "success"
    assert output["level"] == "drift"
    assert output["event"] is not None
    assert output["diagnostics"]["algorithmImplSucceeded"] is True
    assert output["metrics"]["measurements"]["DRIFT_ALARM_STATE"] == "drift_detected"


def test_bocd_runtime_keeps_not_applicable_warmup_normal() -> None:
    state = {}
    output = {}
    values = [0.0, 2.0, -2.0, 2.5]
    for index, value in enumerate(values):
        output = run_bocd_stream(_assignment("BOCD_PREDICTIVE_PROBABILITY"), _bucket(index, value), state)
        state = output["nextState"]

    assert output["runStatus"] == "success"
    assert output["level"] == "normal"
    assert output["event"] is None
    assert output["diagnostics"]["algorithmImplSucceeded"] is False
    assert output["diagnostics"]["algorithmSeverity"] == "not_applicable"
    assert output["diagnostics"]["implementation"] == "drift_algorithm_impl_bocd"
