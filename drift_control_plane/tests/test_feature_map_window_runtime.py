from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone

from drift_server.app.drift.runtime_registry import get_runtime_method
from drift_server.app.runtime_methods.feature_map_window import run_feature_map_window


def _assignment(runtime_key: str, variant_id: str, **params: object) -> dict:
    payload = {
        "variant_id": variant_id,
        "feature_cols": ["x1", "x2", "x3"],
        "alpha": 0.1,
        "permutation_count": 19,
        "random_state": 5,
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
    start = datetime(2027, 4, 1, tzinfo=timezone.utc)
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
        "bucket_id": "bucket-feature-map-001",
        "source_id": "source-feature-map-001",
        "adapter_id": "adapter-feature-map-001",
        "feature_id": "multivariate",
        "window_start": "2027-04-01T00:00:00Z",
        "window_end": "2027-04-02T00:24:00Z",
        "row_count": len(values),
        "payload": json.dumps({"values": values, "featureColumns": ["x1", "x2", "x3"]}),
    }


def test_registry_resolves_feature_map_aliases() -> None:
    assert get_runtime_method("feature_map_window") is run_feature_map_window
    assert get_runtime_method("model_feature_map_ks") is run_feature_map_window
    assert get_runtime_method("model_feature_map_mmd") is run_feature_map_window
    assert get_runtime_method("layerwise_feature_map_drift") is run_feature_map_window


def test_feature_map_runtime_detects_all_supported_variants() -> None:
    cases = [
        ("model_feature_map_ks", "MODEL_FEATURE_MAP_KS", {}),
        ("model_feature_map_mmd", "MODEL_FEATURE_MAP_MMD", {}),
        (
            "layerwise_feature_map_drift",
            "LAYERWISE_FEATURE_MAP_DRIFT",
            {"layer_feature_cols": {"layer1": ["x1"], "layer2": ["x2", "x3"]}},
        ),
    ]
    for runtime_key, variant_id, params in cases:
        output = run_feature_map_window(_assignment(runtime_key, variant_id, **params), _bucket(), {})

        assert output["runStatus"] == "success"
        assert output["level"] == "drift"
        assert output["event"] is not None
        assert output["diagnostics"]["algorithmImplSucceeded"] is True
        assert output["metrics"]["measurements"]["PROCESSED_COUNT"] == 50
