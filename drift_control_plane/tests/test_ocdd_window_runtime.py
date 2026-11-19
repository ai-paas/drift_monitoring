from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone

from drift_server.app.drift.runtime_registry import get_runtime_method
from drift_server.app.runtime_methods.ocdd_window import run_ocdd_window


def _assignment(runtime_key: str, variant_id: str, **params: object) -> dict:
    payload = {
        "variant_id": variant_id,
        "feature_cols": ["x1", "x2", "x3", "x4"],
        "alpha": 0.05,
        "anomaly_rate_threshold": 0.2,
        "min_reference_size": 20,
        "min_current_size": 20,
        **params,
    }
    return {
        "assignment_id": f"assign-{runtime_key}",
        "runtime_method_key": runtime_key,
        "params_json": json.dumps(payload),
    }


def _bucket() -> dict:
    start = datetime(2027, 2, 1, tzinfo=timezone.utc)
    values = []
    for index in range(60):
        x = -2.0 + (index / 15.0)
        values.append(
            {
                "time": (start + timedelta(minutes=index)).isoformat().replace("+00:00", "Z"),
                "period": "reference",
                "features": {"x1": x, "x2": x * x / 4.0, "x3": (index % 7) / 7.0, "x4": (index % 5) / 5.0},
                "metric": x,
            }
        )
    current_start = start + timedelta(days=1)
    for index in range(40):
        x = -2.0 + (index / 15.0)
        values.append(
            {
                "time": (current_start + timedelta(minutes=index)).isoformat().replace("+00:00", "Z"),
                "period": "current",
                "features": {
                    "x1": x + 4.0,
                    "x2": x * x / 4.0 + 3.0,
                    "x3": (index % 7) / 7.0 - 2.0,
                    "x4": (index % 5) / 5.0 + 1.5,
                },
                "metric": x + 4.0,
            }
        )
    return {
        "bucket_id": "bucket-ocdd-001",
        "source_id": "source-ocdd-001",
        "adapter_id": "adapter-ocdd-001",
        "feature_id": "multivariate",
        "window_start": "2027-02-01T00:00:00Z",
        "window_end": "2027-02-02T00:39:00Z",
        "row_count": len(values),
        "payload": json.dumps({"values": values, "featureColumns": ["x1", "x2", "x3", "x4"]}),
    }


def test_registry_resolves_ocdd_aliases() -> None:
    assert get_runtime_method("ocdd_window") is run_ocdd_window
    assert get_runtime_method("one_class_svm_drift") is run_ocdd_window
    assert get_runtime_method("isolation_forest_drift_score") is run_ocdd_window
    assert get_runtime_method("autoencoder_reconstruction_drift") is run_ocdd_window


def test_ocdd_runtime_detects_all_supported_variants() -> None:
    cases = [
        ("one_class_svm_drift", "ONE_CLASS_SVM_DRIFT", {}),
        ("isolation_forest_drift_score", "ISOLATION_FOREST_DRIFT_SCORE", {"random_state": 7}),
        ("autoencoder_reconstruction_drift", "AUTOENCODER_RECONSTRUCTION_DRIFT", {"latent_dim": 2}),
    ]
    for runtime_key, variant_id, params in cases:
        output = run_ocdd_window(_assignment(runtime_key, variant_id, **params), _bucket(), {})

        assert output["runStatus"] == "success"
        assert output["level"] == "drift"
        assert output["event"] is not None
        assert output["diagnostics"]["algorithmImplSucceeded"] is True
        assert output["metrics"]["measurements"]["PROCESSED_COUNT"] == 100
