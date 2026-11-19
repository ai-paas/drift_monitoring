from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone

from drift_server.app.drift.runtime_registry import get_runtime_method
from drift_server.app.runtime_methods.autoencoder_representation_window import run_autoencoder_representation_window


def _assignment(runtime_key: str, variant_id: str, **params: object) -> dict:
    payload = {
        "variant_id": variant_id,
        "latent_cols": ["x1", "x2", "x3"],
        "alpha": 0.1,
        "permutation_count": 19,
        "random_state": 7,
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
    start = datetime(2027, 5, 1, tzinfo=timezone.utc)
    values = []
    for index in range(25):
        x = -1.0 + (index / 10.0)
        values.append(
            {
                "time": (start + timedelta(minutes=index)).isoformat().replace("+00:00", "Z"),
                "period": "reference",
                "features": {"x1": x, "x2": x * 0.5, "x3": (index % 7) / 7.0},
                "metric": x,
            }
        )
    current_start = start + timedelta(days=1)
    for index in range(25):
        x = -1.0 + (index / 10.0)
        values.append(
            {
                "time": (current_start + timedelta(minutes=index)).isoformat().replace("+00:00", "Z"),
                "period": "current",
                "features": {"x1": x + 2.0, "x2": x * 0.5 - 1.5, "x3": (index % 7) / 7.0 + 1.0},
                "metric": x + 2.0,
            }
        )
    return {
        "bucket_id": "bucket-autoencoder-rep-001",
        "source_id": "source-autoencoder-rep-001",
        "adapter_id": "adapter-autoencoder-rep-001",
        "feature_id": "multivariate",
        "window_start": "2027-05-01T00:00:00Z",
        "window_end": "2027-05-02T00:24:00Z",
        "row_count": len(values),
        "payload": json.dumps({"values": values, "featureColumns": ["x1", "x2", "x3"]}),
    }


def test_registry_resolves_autoencoder_representation_aliases() -> None:
    assert get_runtime_method("autoencoder_representation_window") is run_autoencoder_representation_window
    assert get_runtime_method("latent_space_drift") is run_autoencoder_representation_window
    assert get_runtime_method("reconstruction_error_drift") is run_autoencoder_representation_window
    assert get_runtime_method("autoencoder_domain_classifier") is run_autoencoder_representation_window


def test_autoencoder_representation_runtime_detects_all_supported_variants() -> None:
    cases = [
        ("latent_space_drift", "LATENT_SPACE_DRIFT", {}),
        ("reconstruction_error_drift", "RECONSTRUCTION_ERROR_DRIFT", {"alpha": 0.2}),
        ("autoencoder_domain_classifier", "AUTOENCODER_DOMAIN_CLASSIFIER", {"threshold": 0.6}),
    ]
    for runtime_key, variant_id, params in cases:
        output = run_autoencoder_representation_window(_assignment(runtime_key, variant_id, **params), _bucket(), {})

        assert output["runStatus"] == "success"
        assert output["level"] == "drift"
        assert output["event"] is not None
        assert output["diagnostics"]["algorithmImplSucceeded"] is True
        assert output["metrics"]["measurements"]["PROCESSED_COUNT"] == 50
