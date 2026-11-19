from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone

from drift_server.app.drift.runtime_registry import get_runtime_method
from drift_server.app.runtime_methods.seqdrift_numeric_window import run_seqdrift_numeric_window


def _assignment(variant_id: str) -> dict:
    return {
        "assignment_id": f"assign-{variant_id.lower()}",
        "runtime_method_key": "seqdrift_numeric_window",
        "params_json": json.dumps(
            {
                "variant_id": variant_id,
                "delta": 0.01,
                "block_size": 20,
                "value_min": -1.0,
                "value_max": 2.0,
                "min_reference_size": 20,
                "min_current_size": 20,
            }
        ),
    }


def _bucket(reference_shift: float = 0.0, current_shift: float = 0.8, reference_count: int = 80, current_count: int = 80) -> dict:
    start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    values = []
    for index in range(reference_count):
        values.append(
            {
                "time": (start + timedelta(minutes=index)).isoformat().replace("+00:00", "Z"),
                "value": float(index % 5) * 0.01 + reference_shift,
                "period": "reference",
            }
        )
    current_start = start + timedelta(days=1)
    for index in range(current_count):
        values.append(
            {
                "time": (current_start + timedelta(minutes=index)).isoformat().replace("+00:00", "Z"),
                "value": float(index % 5) * 0.01 + current_shift,
                "period": "current",
            }
        )
    return {
        "bucket_id": "bucket-001",
        "source_id": "source-001",
        "adapter_id": "adapter-001",
        "feature_id": "score",
        "window_start": "2026-01-01T00:00:00Z",
        "window_end": "2026-01-02T01:19:00Z",
        "row_count": len(values),
        "payload": json.dumps({"values": values}),
    }


def test_registry_resolves_seqdrift_aliases() -> None:
    assert get_runtime_method("seqdrift_numeric_window") is run_seqdrift_numeric_window
    assert get_runtime_method("seqdrift1") is run_seqdrift_numeric_window
    assert get_runtime_method("seqdrift2") is run_seqdrift_numeric_window


def test_seqdrift_numeric_window_detects_seqdrift1_shift() -> None:
    output = run_seqdrift_numeric_window(_assignment("SEQDRIFT1"), _bucket(), {})

    assert output["runStatus"] == "success"
    assert output["level"] == "drift"
    assert output["event"] is not None
    assert output["diagnostics"]["algorithmImplSucceeded"] is True
    assert output["metrics"]["measurements"]["ALARM_COUNT"] > 0


def test_seqdrift_numeric_window_detects_seqdrift2_shift() -> None:
    assignment = _assignment("SEQDRIFT2")
    params = json.loads(assignment["params_json"])
    params.update({"reservoir_size": 50, "random_seed": 58})
    assignment["params_json"] = json.dumps(params)

    output = run_seqdrift_numeric_window(assignment, _bucket(current_shift=1.0, reference_count=160, current_count=80), {})

    assert output["runStatus"] == "success"
    assert output["level"] == "drift"
    assert output["diagnostics"]["algorithmImplSucceeded"] is True
