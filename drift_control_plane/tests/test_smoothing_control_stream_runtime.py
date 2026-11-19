from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone

from drift_server.app.drift.runtime_registry import get_runtime_method
from drift_server.app.runtime_methods.smoothing_control_stream import run_ewma_stream, run_gma_stream


def _assignment(runtime_key: str, variant_id: str) -> dict:
    params = {
        "variant_id": variant_id,
        "center_line": 0.0,
        "sigma": 0.1,
        "lambda": 0.3,
        "control_width": 3.0,
        "warmup_size": 1,
        "min_reference_size": 1,
        "min_current_size": 1,
        "maxStatePoints": 40,
    }
    if variant_id.endswith("ONE_SIDED"):
        params.update({"threshold": 0.2, "direction": "increase"})
    return {
        "assignment_id": f"assign-{variant_id.lower()}",
        "runtime_method_key": runtime_key,
        "params_json": json.dumps(params),
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


def _run_values(runtime_key: str, variant_id: str, values: list[float]) -> dict:
    state = {}
    output = {}
    runner = run_ewma_stream if runtime_key == "ewma_stream" else run_gma_stream
    assignment = _assignment(runtime_key, variant_id)
    for index, value in enumerate(values):
        output = runner(assignment, _bucket(index, value), state)
        state = output["nextState"]
    return output


def test_registry_resolves_smoothing_control_aliases() -> None:
    assert get_runtime_method("ewma_stream") is run_ewma_stream
    assert get_runtime_method("ewma_univariate_control_chart") is run_ewma_stream
    assert get_runtime_method("ewma_one_sided") is run_ewma_stream
    assert get_runtime_method("ewma_baseline_replay_threshold") is run_ewma_stream
    assert get_runtime_method("gma_stream") is run_gma_stream
    assert get_runtime_method("gma_control_chart") is run_gma_stream
    assert get_runtime_method("gma_one_sided") is run_gma_stream
    assert get_runtime_method("gma_with_empirical_limit") is run_gma_stream


def test_ewma_runtime_detects_stream_shift() -> None:
    output = _run_values("ewma_stream", "EWMA_UNIVARIATE_CONTROL_CHART", [0.0, 0.0, 0.0, 1.0, 1.0, 1.0])

    assert output["runStatus"] == "success"
    assert output["level"] == "drift"
    assert output["event"] is not None
    assert output["diagnostics"]["algorithmImplSucceeded"] is True
    assert output["metrics"]["measurements"]["FIRST_ALARM_DIRECTION"] == "upper"


def test_gma_runtime_detects_stream_shift() -> None:
    output = _run_values("gma_stream", "GMA_CONTROL_CHART", [0.0, 0.0, 0.0, 1.0, 1.0, 1.0])

    assert output["runStatus"] == "success"
    assert output["level"] == "drift"
    assert output["event"] is not None
    assert output["diagnostics"]["algorithmImplSucceeded"] is True
    assert output["metrics"]["measurements"]["FIRST_ALARM_DIRECTION"] == "upper"


def test_deferred_smoothing_variants_are_executable() -> None:
    ewma = _run_values("ewma_stream", "EWMA_BASELINE_REPLAY_THRESHOLD", [0.0, 0.0, 0.0, 1.0, 1.0, 1.0])
    gma = _run_values("gma_stream", "GMA_WITH_EMPIRICAL_LIMIT", [0.0, 0.0, 0.0, 1.0, 1.0, 1.0])

    assert ewma["runStatus"] == "success"
    assert ewma["level"] == "drift"
    assert ewma["diagnostics"]["algorithmImplSucceeded"] is True
    assert gma["runStatus"] == "success"
    assert gma["level"] == "drift"
    assert gma["diagnostics"]["algorithmImplSucceeded"] is True
