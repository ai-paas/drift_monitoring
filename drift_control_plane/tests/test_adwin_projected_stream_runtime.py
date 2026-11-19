from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone

from drift_server.app.drift.runtime_registry import get_runtime_method
from drift_server.app.runtime_methods.adwin_mean_stream import run_adwin_mean_stream


def _assignment(runtime_key: str, variant_id: str) -> dict:
    return {
        "assignment_id": f"assign-{runtime_key}",
        "runtime_method_key": runtime_key,
        "params_json": json.dumps(
            {
                "variant_id": variant_id,
                "delta": 0.2,
                "min_window_length": 1,
                "grace_period": 1,
                "min_reference_size": 1,
                "min_current_size": 1,
                "maxStatePoints": 20,
            }
        ),
    }


def _bucket(index: int, value: float) -> dict:
    start = datetime(2027, 12, 1, tzinfo=timezone.utc) + timedelta(minutes=10 * index)
    end = start + timedelta(minutes=10)
    return {
        "bucket_id": f"bucket-adwin-{index}",
        "source_id": "source-adwin-projected",
        "adapter_id": "adapter-adwin-projected",
        "feature_id": "metric",
        "window_start": start.isoformat().replace("+00:00", "Z"),
        "window_end": end.isoformat().replace("+00:00", "Z"),
        "mean_value": value,
        "row_count": 10,
    }


def _run_sequence(runtime_key: str, variant_id: str) -> dict:
    assignment = _assignment(runtime_key, variant_id)
    state: dict = {}
    output = {}
    for index, value in enumerate(([0.0] * 10) + ([10.0] * 10)):
        output = run_adwin_mean_stream(assignment, _bucket(index, value), state)
        state = output["nextState"]
    return output


def test_registry_resolves_projected_adwin_aliases() -> None:
    assert get_runtime_method("adwin_error_rate") is run_adwin_mean_stream
    assert get_runtime_method("adwin_distance_stream") is run_adwin_mean_stream


def test_adwin_error_rate_runtime_detects_projected_shift() -> None:
    output = _run_sequence("adwin_error_rate", "ADWIN_ERROR_RATE")

    assert output["runStatus"] == "success"
    assert output["level"] == "drift"
    assert output["event"] is not None
    assert output["diagnostics"]["algorithmImplSucceeded"] is True
    assert output["diagnostics"]["algorithmMetadata"]["stream_semantics"] == "projected_error_rate_stream"


def test_adwin_distance_stream_runtime_detects_projected_shift() -> None:
    output = _run_sequence("adwin_distance_stream", "ADWIN_DISTANCE_STREAM")

    assert output["runStatus"] == "success"
    assert output["level"] == "drift"
    assert output["event"] is not None
    assert output["diagnostics"]["algorithmImplSucceeded"] is True
    assert output["diagnostics"]["algorithmMetadata"]["stream_semantics"] == "projected_distance_stream"
