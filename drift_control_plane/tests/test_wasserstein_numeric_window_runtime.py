from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone

from drift_server.app.drift.runtime_registry import get_runtime_method
from drift_server.app.runtime_methods.wasserstein_numeric_window import run_wasserstein_numeric_window


def _assignment(runtime_key: str, variant_id: str) -> dict:
    return {
        "assignment_id": f"assign-{runtime_key}",
        "runtime_method_key": runtime_key,
        "params_json": json.dumps(
            {
                "variant_id": variant_id,
                "threshold": 0.25,
                "min_reference_size": 20,
                "min_current_size": 20,
                "projection_count": 1,
            }
        ),
    }


def _bucket() -> dict:
    start = datetime(2027, 11, 1, tzinfo=timezone.utc)
    values = []
    for index in range(30):
        values.append(
            {
                "time": (start + timedelta(minutes=index)).isoformat().replace("+00:00", "Z"),
                "period": "reference",
                "value": float(index % 5),
            }
        )
    current_start = start + timedelta(hours=1)
    for index in range(30):
        values.append(
            {
                "time": (current_start + timedelta(minutes=index)).isoformat().replace("+00:00", "Z"),
                "period": "current",
                "value": float(index % 5) + 3.0,
            }
        )
    return {
        "bucket_id": "bucket-wasserstein-001",
        "source_id": "source-wasserstein-001",
        "adapter_id": "adapter-wasserstein-001",
        "feature_id": "score",
        "window_start": "2027-11-01T00:00:00Z",
        "window_end": "2027-11-01T02:00:00Z",
        "row_count": len(values),
        "payload": json.dumps({"values": values}),
    }


def _single_period_bucket(period: str, shift: float, bucket_id: str, start: datetime) -> dict:
    values = [
        {
            "time": (start + timedelta(minutes=index)).isoformat().replace("+00:00", "Z"),
            "period": period,
            "value": float(index % 5) + shift,
        }
        for index in range(30)
    ]
    return {
        "bucket_id": bucket_id,
        "source_id": "source-wasserstein-001",
        "adapter_id": "adapter-wasserstein-001",
        "feature_id": "score",
        "window_start": start.isoformat().replace("+00:00", "Z"),
        "window_end": (start + timedelta(minutes=10)).isoformat().replace("+00:00", "Z"),
        "row_count": len(values),
        "payload": json.dumps({"values": values}),
    }


def test_registry_resolves_sliced_wasserstein_alias() -> None:
    assert get_runtime_method("sliced_wasserstein_embedding") is run_wasserstein_numeric_window


def test_sliced_wasserstein_runtime_detects_projected_shift() -> None:
    output = run_wasserstein_numeric_window(
        _assignment("sliced_wasserstein_embedding", "SLICED_WASSERSTEIN_EMBEDDING"),
        _bucket(),
        {},
    )

    assert output["runStatus"] == "success"
    assert output["level"] == "drift"
    assert output["event"] is not None
    assert output["diagnostics"]["algorithmImplSucceeded"] is True
    assert output["metrics"]["measurements"]["PROCESSED_COUNT"] == 60


def test_wasserstein_runtime_accumulates_reference_current_buckets() -> None:
    assignment = _assignment("wasserstein_numeric_window", "WASSERSTEIN_1D_EXACT")
    start = datetime(2027, 11, 1, tzinfo=timezone.utc)
    reference_output = run_wasserstein_numeric_window(
        assignment,
        _single_period_bucket("reference", 0.0, "bucket-wasserstein-reference", start),
        {},
    )
    current_output = run_wasserstein_numeric_window(
        assignment,
        _single_period_bucket("current", 3.0, "bucket-wasserstein-current", start + timedelta(hours=1)),
        reference_output["nextState"],
    )

    assert reference_output["level"] == "normal"
    assert current_output["runStatus"] == "success"
    assert current_output["level"] == "drift"
    assert current_output["event"] is not None
    assert current_output["metrics"]["measurements"]["PROCESSED_COUNT"] == 60
