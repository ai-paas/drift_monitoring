from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone

from drift_server.app.drift.runtime_registry import get_runtime_method
from drift_server.app.runtime_methods.cusum_stream import run_cusum_stream


def _assignment(variant_id: str) -> dict:
    return {
        "assignment_id": f"assign-{variant_id.lower()}",
        "runtime_method_key": "cusum_stream",
        "params_json": json.dumps(
            {
                "variant_id": variant_id,
                "target_mean": 0.0 if variant_id != "ONE_SIDED_LOWER_CUSUM" else 5.0,
                "allowance_k": 0.0,
                "decision_threshold_h": 1.0,
                "warmup_size": 1,
                "min_reference_size": 1,
                "min_current_size": 1,
                "maxStatePoints": 40,
            }
        ),
    }


def _bucket(index: int, value: float) -> dict:
    start = datetime(2026, 1, 1, tzinfo=timezone.utc) + timedelta(minutes=10 * index)
    end = start + timedelta(minutes=10)
    return {
        "bucket_id": f"bucket-{index:03d}",
        "window_start": start.isoformat().replace("+00:00", "Z"),
        "window_end": end.isoformat().replace("+00:00", "Z"),
        "mean_value": value,
    }


def _run_values(variant_id: str, values: list[float]) -> dict:
    state = {}
    output = {}
    assignment = _assignment(variant_id)
    for index, value in enumerate(values):
        output = run_cusum_stream(assignment, _bucket(index, value), state)
        state = output["nextState"]
    return output


def test_registry_resolves_cusum_aliases() -> None:
    assert get_runtime_method("cusum_stream") is run_cusum_stream
    assert get_runtime_method("one_sided_upper_cusum") is run_cusum_stream
    assert get_runtime_method("one_sided_lower_cusum") is run_cusum_stream
    assert get_runtime_method("two_sided_cusum") is run_cusum_stream
    assert get_runtime_method("cusum_on_distance_stream") is run_cusum_stream


def test_cusum_runtime_detects_upper_stream_shift() -> None:
    output = _run_values("ONE_SIDED_UPPER_CUSUM", [0.0, 0.0, 5.0, 5.0])

    assert output["runStatus"] == "success"
    assert output["level"] == "drift"
    assert output["event"] is not None
    assert output["diagnostics"]["algorithmImplSucceeded"] is True
    assert output["metrics"]["measurements"]["FIRST_ALARM_DIRECTION"] == "upper"


def test_cusum_runtime_detects_lower_stream_shift() -> None:
    output = _run_values("ONE_SIDED_LOWER_CUSUM", [5.0, 5.0, 0.0, 0.0])

    assert output["runStatus"] == "success"
    assert output["level"] == "drift"
    assert output["event"] is not None
    assert output["diagnostics"]["algorithmImplSucceeded"] is True
    assert output["metrics"]["measurements"]["FIRST_ALARM_DIRECTION"] == "lower"


def test_cusum_runtime_detects_distance_stream_shift() -> None:
    output = _run_values("CUSUM_ON_DISTANCE_STREAM", [0.0, 0.0, 5.0, 5.0])

    assert output["runStatus"] == "success"
    assert output["level"] == "drift"
    assert output["event"] is not None
    assert output["diagnostics"]["algorithmImplSucceeded"] is True
    assert output["metrics"]["measurements"]["FIRST_ALARM_DIRECTION"] == "upper"
