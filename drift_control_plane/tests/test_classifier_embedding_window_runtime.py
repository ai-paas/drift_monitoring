from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone

from drift_server.app.drift.runtime_registry import get_runtime_method
from drift_server.app.runtime_methods.classifier_embedding_window import run_classifier_embedding_window


def _assignment(runtime_key: str, variant_id: str, **params: object) -> dict:
    payload = {
        "variant_id": variant_id,
        "embedding_cols": ["e1", "e2", "e3"],
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
    start = datetime(2027, 3, 1, tzinfo=timezone.utc)
    values = []
    for index in range(60):
        x = -1.0 + (index / 30.0)
        values.append(
            {
                "time": (start + timedelta(minutes=index)).isoformat().replace("+00:00", "Z"),
                "period": "reference",
                "features": {"e1": x, "e2": x * x, "e3": (index % 9) / 9.0},
                "metric": x,
            }
        )
    current_start = start + timedelta(days=1)
    for index in range(60):
        x = -1.0 + (index / 30.0)
        values.append(
            {
                "time": (current_start + timedelta(minutes=index)).isoformat().replace("+00:00", "Z"),
                "period": "current",
                "features": {"e1": x + 3.0, "e2": x * x, "e3": (index % 9) / 9.0},
                "metric": x + 3.0,
            }
        )
    return {
        "bucket_id": "bucket-cls-001",
        "source_id": "source-cls-001",
        "adapter_id": "adapter-cls-001",
        "feature_id": "multivariate",
        "window_start": "2027-03-01T00:00:00Z",
        "window_end": "2027-03-02T00:59:00Z",
        "row_count": len(values),
        "payload": json.dumps({"values": values, "featureColumns": ["e1", "e2", "e3"]}),
    }


def test_registry_resolves_classifier_embedding_aliases() -> None:
    assert get_runtime_method("classifier_embedding_window") is run_classifier_embedding_window
    assert get_runtime_method("domain_classifier_roc_auc") is run_classifier_embedding_window
    assert get_runtime_method("domain_classifier_probability_drift") is run_classifier_embedding_window
    assert get_runtime_method("cross_validated_domain_classifier") is run_classifier_embedding_window


def test_classifier_embedding_runtime_detects_all_supported_variants() -> None:
    cases = [
        ("domain_classifier_roc_auc", "DOMAIN_CLASSIFIER_ROC_AUC", {"auc_threshold": 0.8}),
        (
            "domain_classifier_probability_drift",
            "DOMAIN_CLASSIFIER_PROBABILITY_DRIFT",
            {"alpha": 0.05, "probability_threshold": 0.7},
        ),
        (
            "cross_validated_domain_classifier",
            "CROSS_VALIDATED_DOMAIN_CLASSIFIER",
            {"auc_threshold": 0.75, "cv_folds": 3, "min_fold_size": 10},
        ),
    ]
    for runtime_key, variant_id, params in cases:
        output = run_classifier_embedding_window(_assignment(runtime_key, variant_id, **params), _bucket(), {})

        assert output["runStatus"] == "success"
        assert output["level"] == "drift"
        assert output["event"] is not None
        assert output["diagnostics"]["algorithmImplSucceeded"] is True
        assert output["metrics"]["measurements"]["PROCESSED_COUNT"] == 120
