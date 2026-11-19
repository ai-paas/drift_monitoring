from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone

from drift_server.app.drift.runtime_registry import get_runtime_method
from drift_server.app.runtime_methods.shap_window import run_shap_window


def _assignment(runtime_key: str, variant_id: str, **params: object) -> dict:
    payload = {
        "variant_id": variant_id,
        "shap_cols": ["shap_a", "shap_b", "shap_c"],
        "alpha": 0.05,
        "rank_shift_threshold": 0.4,
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
        cls = "A" if index < 10 else "B"
        values.append(
            {
                "time": (start + timedelta(minutes=index)).isoformat().replace("+00:00", "Z"),
                "period": "reference",
                "features": {"shap_a": 3.0, "shap_b": 1.0, "shap_c": 0.2},
                "attributes": {"class": cls},
                "metric": 3.0,
            }
        )
    current_start = start + timedelta(hours=1)
    for index in range(20):
        cls = "A" if index < 10 else "B"
        shap_b = 1.0 if cls == "A" else 3.0
        values.append(
            {
                "time": (current_start + timedelta(minutes=index)).isoformat().replace("+00:00", "Z"),
                "period": "current",
                "features": {"shap_a": 0.2, "shap_b": shap_b, "shap_c": 3.0},
                "attributes": {"class": cls},
                "metric": 3.0,
            }
        )
    return {
        "bucket_id": "bucket-shap-001",
        "source_id": "source-shap-001",
        "adapter_id": "adapter-shap-001",
        "feature_id": "multivariate",
        "window_start": "2027-04-01T00:00:00Z",
        "window_end": "2027-04-01T02:00:00Z",
        "row_count": len(values),
        "payload": json.dumps(
            {"values": values, "featureColumns": ["shap_a", "shap_b", "shap_c"], "attributeColumns": ["class"]}
        ),
    }


def test_registry_resolves_shap_aliases() -> None:
    assert get_runtime_method("shap_window") is run_shap_window
    assert get_runtime_method("shap_value_distribution_test") is run_shap_window
    assert get_runtime_method("global_importance_rank_shift") is run_shap_window
    assert get_runtime_method("class_conditional_shap_drift") is run_shap_window


def test_shap_runtime_detects_all_supported_variants() -> None:
    cases = [
        ("shap_value_distribution_test", "SHAP_VALUE_DISTRIBUTION_TEST", {}),
        ("global_importance_rank_shift", "GLOBAL_IMPORTANCE_RANK_SHIFT", {"rank_shift_threshold": 0.4}),
        ("class_conditional_shap_drift", "CLASS_CONDITIONAL_SHAP_DRIFT", {"class_col": "class", "min_class_size": 5}),
    ]
    for runtime_key, variant_id, params in cases:
        output = run_shap_window(_assignment(runtime_key, variant_id, **params), _bucket(), {})

        assert output["runStatus"] == "success"
        assert output["level"] == "drift"
        assert output["event"] is not None
        assert output["diagnostics"]["algorithmImplSucceeded"] is True
        assert output["metrics"]["measurements"]["PROCESSED_COUNT"] == 40
