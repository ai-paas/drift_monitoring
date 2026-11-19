from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone

from drift_server.app.drift.runtime_registry import get_runtime_method
from drift_server.app.runtime_methods.text_domain_classifier_window import run_text_domain_classifier_window


def _assignment(runtime_key: str, variant_id: str, **params: object) -> dict:
    payload = {
        "variant_id": variant_id,
        "embedding_cols": ["emb1", "emb2", "emb3"],
        "descriptor_cols": ["emb1", "emb2", "emb3"],
        "auc_threshold": 0.75,
        "alpha": 0.05,
        "min_reference_size": 15,
        "min_current_size": 15,
        **params,
    }
    return {
        "assignment_id": f"assign-{runtime_key}",
        "runtime_method_key": runtime_key,
        "params_json": json.dumps(payload),
    }


def _bucket() -> dict:
    start = datetime(2027, 8, 1, tzinfo=timezone.utc)
    values = []
    for index in range(20):
        values.append(
            {
                "time": (start + timedelta(minutes=index)).isoformat().replace("+00:00", "Z"),
                "period": "reference",
                "features": {"emb1": 0.1 + index * 0.01, "emb2": 0.2, "emb3": 0.1},
                "metric": 0.1,
            }
        )
    current_start = start + timedelta(hours=1)
    for index in range(20):
        values.append(
            {
                "time": (current_start + timedelta(minutes=index)).isoformat().replace("+00:00", "Z"),
                "period": "current",
                "features": {"emb1": 2.2 + index * 0.02, "emb2": -1.1, "emb3": 1.4},
                "metric": 2.2,
            }
        )
    return {
        "bucket_id": "bucket-text-domain-001",
        "source_id": "source-text-domain-001",
        "adapter_id": "adapter-text-domain-001",
        "feature_id": "multivariate",
        "window_start": "2027-08-01T00:00:00Z",
        "window_end": "2027-08-01T01:19:00Z",
        "row_count": len(values),
        "payload": json.dumps({"values": values, "featureColumns": ["emb1", "emb2", "emb3"]}),
    }


def test_registry_resolves_text_domain_aliases() -> None:
    assert get_runtime_method("text_domain_classifier_window") is run_text_domain_classifier_window
    assert get_runtime_method("text_domain_classifier_roc_auc") is run_text_domain_classifier_window
    assert get_runtime_method("text_domain_classifier_stat_test") is run_text_domain_classifier_window
    assert get_runtime_method("text_descriptor_drift") is run_text_domain_classifier_window


def test_text_domain_runtime_detects_all_supported_variants() -> None:
    cases = [
        ("text_domain_classifier_roc_auc", "TEXT_DOMAIN_CLASSIFIER_ROC_AUC", {}),
        ("text_domain_classifier_stat_test", "TEXT_DOMAIN_CLASSIFIER_STAT_TEST", {}),
        ("text_descriptor_drift", "TEXT_DESCRIPTOR_DRIFT", {}),
    ]
    for runtime_key, variant_id, params in cases:
        output = run_text_domain_classifier_window(_assignment(runtime_key, variant_id, **params), _bucket(), {})

        assert output["runStatus"] == "success"
        assert output["level"] == "drift"
        assert output["event"] is not None
        assert output["diagnostics"]["algorithmImplSucceeded"] is True
        assert output["metrics"]["measurements"]["PROCESSED_COUNT"] == 40
