from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone

from drift_server.app.drift.runtime_registry import get_runtime_method
from drift_server.app.runtime_methods.tree_feature_window import run_tree_feature_window


def _assignment(runtime_key: str, variant_id: str, **params: object) -> dict:
    payload = {
        "variant_id": variant_id,
        "feature_cols": ["period_indicator", "shap_a", "shap_b", "shap_c"],
        "time_feature_col": "period_indicator",
        "split_accuracy_threshold": 0.9,
        "auc_threshold": 0.8,
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
    for index in range(20):
        values.append(
            {
                "time": (start + timedelta(minutes=index)).isoformat().replace("+00:00", "Z"),
                "period": "reference",
                "features": {"shap_a": 3.0, "shap_b": 1.0, "shap_c": 0.2},
                "metric": 3.0,
            }
        )
    current_start = start + timedelta(hours=1)
    for index in range(20):
        values.append(
            {
                "time": (current_start + timedelta(minutes=index)).isoformat().replace("+00:00", "Z"),
                "period": "current",
                "features": {"shap_a": 0.2, "shap_b": 3.0, "shap_c": 3.0},
                "metric": 3.0,
            }
        )
    return {
        "bucket_id": "bucket-tree-feature-001",
        "source_id": "source-tree-feature-001",
        "adapter_id": "adapter-tree-feature-001",
        "feature_id": "multivariate",
        "window_start": "2027-04-01T00:00:00Z",
        "window_end": "2027-04-01T02:00:00Z",
        "row_count": len(values),
        "payload": json.dumps(
            {"values": values, "featureColumns": ["shap_a", "shap_b", "shap_c"], "attributeColumns": []}
        ),
    }


def test_registry_resolves_tree_feature_aliases() -> None:
    assert get_runtime_method("tree_feature_window") is run_tree_feature_window
    assert get_runtime_method("time_feature_split_detector") is run_tree_feature_window
    assert get_runtime_method("domain_classifier_tree") is run_tree_feature_window


def test_tree_feature_runtime_detects_all_supported_variants() -> None:
    cases = [
        ("time_feature_split_detector", "TIME_FEATURE_SPLIT_DETECTOR", {}),
        (
            "domain_classifier_tree",
            "DOMAIN_CLASSIFIER_TREE",
            {"feature_cols": ["shap_a", "shap_b", "shap_c"]},
        ),
    ]
    for runtime_key, variant_id, params in cases:
        output = run_tree_feature_window(_assignment(runtime_key, variant_id, **params), _bucket(), {})

        assert output["runStatus"] == "success"
        assert output["level"] == "drift"
        assert output["event"] is not None
        assert output["diagnostics"]["algorithmImplSucceeded"] is True
        assert output["metrics"]["measurements"]["PROCESSED_COUNT"] == 40
