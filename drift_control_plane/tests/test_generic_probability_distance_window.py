from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone

from drift_server.app.drift.runtime_registry import get_runtime_method
from drift_server.app.runtime_methods.generic_probability_distance_window import (
    run_generic_probability_distance_window,
)


def _assignment(variant_id: str, extra_params: dict | None = None) -> dict:
    params = {
        "variant_id": variant_id,
        "threshold": 0.05,
        "min_reference_size": 1,
        "min_current_size": 1,
    }
    if extra_params:
        params.update(extra_params)
    return {
        "assignment_id": f"assign-{variant_id.lower()}",
        "runtime_method_key": "generic_probability_distance_window",
        "params_json": json.dumps(params),
    }


def _categorical_bucket() -> dict:
    start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    values = [
        {"time": start.isoformat().replace("+00:00", "Z"), "category": "approved", "count": 50, "period": "reference"},
        {
            "time": (start + timedelta(minutes=1)).isoformat().replace("+00:00", "Z"),
            "category": "review",
            "count": 30,
            "period": "reference",
        },
        {
            "time": (start + timedelta(minutes=2)).isoformat().replace("+00:00", "Z"),
            "category": "declined",
            "count": 20,
            "period": "reference",
        },
        {
            "time": (start + timedelta(days=1)).isoformat().replace("+00:00", "Z"),
            "category": "approved",
            "count": 20,
            "period": "current",
        },
        {
            "time": (start + timedelta(days=1, minutes=1)).isoformat().replace("+00:00", "Z"),
            "category": "review",
            "count": 30,
            "period": "current",
        },
        {
            "time": (start + timedelta(days=1, minutes=2)).isoformat().replace("+00:00", "Z"),
            "category": "declined",
            "count": 50,
            "period": "current",
        },
    ]
    return {
        "bucket_id": "bucket-prob-001",
        "source_id": "source-001",
        "adapter_id": "adapter-001",
        "feature_id": "category",
        "window_start": "2026-01-01T00:00:00Z",
        "window_end": "2026-01-02T00:02:00Z",
        "row_count": len(values),
        "payload": json.dumps({"values": values}),
    }


def _numeric_bucket() -> dict:
    start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    values = []
    for index in range(40):
        values.append(
            {
                "time": (start + timedelta(minutes=index)).isoformat().replace("+00:00", "Z"),
                "value": float(index % 10),
                "period": "reference",
            }
        )
    for index in range(40):
        values.append(
            {
                "time": (start + timedelta(days=1, minutes=index)).isoformat().replace("+00:00", "Z"),
                "value": float(20 + (index % 10)),
                "period": "current",
            }
        )
    return {
        "bucket_id": "bucket-prob-002",
        "source_id": "source-001",
        "adapter_id": "adapter-001",
        "feature_id": "score",
        "window_start": "2026-01-01T00:00:00Z",
        "window_end": "2026-01-02T00:39:00Z",
        "row_count": len(values),
        "payload": json.dumps({"values": values}),
    }


def test_registry_resolves_probability_distance_aliases() -> None:
    assert get_runtime_method("generic_probability_distance_window") is run_generic_probability_distance_window
    assert get_runtime_method("kl_divergence_window") is run_generic_probability_distance_window
    assert get_runtime_method("jensen_shannon_window") is run_generic_probability_distance_window
    assert get_runtime_method("hinc_window") is run_generic_probability_distance_window


def test_generic_probability_distance_runtime_detects_categorical_kl_shift() -> None:
    output = run_generic_probability_distance_window(_assignment("DISCRETE_KL_DIVERGENCE"), _categorical_bucket(), {})

    assert output["runStatus"] == "success"
    assert output["level"] == "drift"
    assert output["event"] is not None
    assert output["diagnostics"]["algorithmImplSucceeded"] is True
    assert output["metrics"]["measurements"]["PROCESSED_COUNT"] == 200


def test_generic_probability_distance_runtime_detects_numeric_histogram_hinc_shift() -> None:
    output = run_generic_probability_distance_window(
        _assignment("HINC_HISTOGRAM_NUMERIC", {"bin_count": 5, "threshold": 0.01}),
        _numeric_bucket(),
        {},
    )

    assert output["runStatus"] == "success"
    assert output["level"] == "drift"
    assert output["diagnostics"]["algorithmImplSucceeded"] is True
    assert output["metrics"]["measurements"]["PROCESSED_COUNT"] == 80
