from __future__ import annotations

import json
from datetime import datetime, timedelta

from drift_server.app.drift.runtime_registry import get_runtime_method
from drift_server.app.runtime_methods.model_uncertainty_window import (
    run_model_uncertainty_window,
    run_softmax_confidence_drift,
)


def test_model_uncertainty_variant_aliases_resolve() -> None:
    assert get_runtime_method("model_uncertainty_window") is run_model_uncertainty_window
    assert get_runtime_method("softmax_confidence_drift") is run_softmax_confidence_drift
    assert get_runtime_method("entropy_drift") is run_model_uncertainty_window
    assert get_runtime_method("predictive_variance_drift") is run_model_uncertainty_window


def test_model_uncertainty_runtime_calls_algorithm_impl_for_all_variants() -> None:
    for runtime_key, params in [
        (
            "softmax_confidence_drift",
            {
                "variant_id": "SOFTMAX_CONFIDENCE_DRIFT",
                "probability_cols": ["p1", "p2", "p3"],
                "alpha": 0.05,
                "min_reference_size": 20,
                "min_current_size": 20,
            },
        ),
        (
            "entropy_drift",
            {
                "variant_id": "ENTROPY_DRIFT",
                "probability_cols": ["p1", "p2", "p3"],
                "alpha": 0.05,
                "min_reference_size": 20,
                "min_current_size": 20,
            },
        ),
        (
            "predictive_variance_drift",
            {
                "variant_id": "PREDICTIVE_VARIANCE_DRIFT",
                "prediction_cols": ["m1", "m2", "m3"],
                "alpha": 0.05,
                "min_reference_size": 20,
                "min_current_size": 20,
            },
        ),
    ]:
        result = run_model_uncertainty_window(
            {"runtime_method_key": runtime_key, "params_json": json.dumps(params)},
            _bucket(),
            {},
        )
        assert result["runStatus"] == "success"
        assert result["level"] == "drift"
        assert result["diagnostics"]["implementation"] == "drift_algorithm_impl_model_uncertainty_drift"
        assert result["diagnostics"]["algorithmImplSucceeded"] is True
        assert result["metrics"]["measurements"]["PROCESSED_COUNT"] == 60


def test_softmax_confidence_runtime_accumulates_reference_and_current_buckets() -> None:
    assignment = {
        "runtime_method_key": "softmax_confidence_drift",
        "params_json": json.dumps(
            {
                "variant_id": "SOFTMAX_CONFIDENCE_DRIFT",
                "confidence_col": "confidence",
                "alpha": 0.05,
                "min_reference_size": 5,
                "min_current_size": 5,
            }
        ),
    }
    reference = _period_bucket("reference-bucket", "reference", 0.95)
    first = run_softmax_confidence_drift(assignment, reference, {})

    assert first["runStatus"] == "success"
    assert first["level"] == "normal"
    assert first["diagnostics"]["reason"] == "building_current_window"
    assert len(first["nextState"]["referenceValues"]) == 10
    assert first["nextState"]["currentValues"] == []

    current = _period_bucket("current-bucket", "current", 0.35, hour=1)
    second = run_softmax_confidence_drift(assignment, current, first["nextState"])

    assert second["runStatus"] == "success"
    assert second["level"] == "drift"
    assert second["diagnostics"]["algorithmImplSucceeded"] is True
    assert second["metrics"]["measurements"]["PROCESSED_COUNT"] == 20
    assert len(second["nextState"]["referenceValues"]) == 10
    assert len(second["nextState"]["currentValues"]) == 10


def _period_bucket(bucket_id: str, period: str, confidence: float, hour: int = 0) -> dict[str, object]:
    start = datetime(2027, 1, 1) + timedelta(hours=hour)
    values = [
        {
            "time": (start + timedelta(seconds=index)).isoformat(),
            "period": period,
            "features": {"confidence": confidence},
            "metric": confidence,
        }
        for index in range(10)
    ]
    return {
        "bucket_id": bucket_id,
        "window_start": start.isoformat(),
        "window_end": (start + timedelta(minutes=10)).isoformat(),
        "payload": {"featureColumns": ["confidence"], "values": values},
    }


def _bucket() -> dict[str, object]:
    start = datetime(2027, 1, 1)
    values = []
    for index in range(30):
        values.append(
            {
                "time": (start + timedelta(minutes=index)).isoformat(),
                "period": "reference",
                "features": {"p1": 0.9, "p2": 0.08, "p3": 0.02, "variance": 0.01, "m1": -0.1, "m2": 0.0, "m3": 0.1},
                "metric": 0.9,
            }
        )
    for index in range(30):
        values.append(
            {
                "time": (start + timedelta(hours=1, minutes=index)).isoformat(),
                "period": "current",
                "features": {"p1": 0.34, "p2": 0.33, "p3": 0.33, "variance": 0.45, "m1": -1.0, "m2": 0.0, "m3": 1.0},
                "metric": 0.34,
            }
        )
    return {
        "bucket_id": "bucket-001",
        "window_start": start.isoformat(),
        "window_end": (start + timedelta(hours=2)).isoformat(),
        "payload": {"featureColumns": ["p1", "p2", "p3", "variance", "m1", "m2", "m3"], "values": values},
    }
