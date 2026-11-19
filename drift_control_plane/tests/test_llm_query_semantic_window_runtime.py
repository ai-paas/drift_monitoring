from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone

from drift_server.app.drift.runtime_registry import get_runtime_method
from drift_server.app.runtime_methods.llm_query_semantic_window import run_llm_query_semantic_window


def _assignment(runtime_key: str, variant_id: str, **params: object) -> dict:
    payload = {
        "variant_id": variant_id,
        "embedding_cols": ["emb1", "emb2", "emb3"],
        "alpha": 0.1,
        "threshold": 0.1,
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
    start = datetime(2027, 7, 1, tzinfo=timezone.utc)
    ref_topics = ["billing"] * 12 + ["claims"] * 6 + ["fraud"] * 2
    cur_topics = ["billing"] * 2 + ["claims"] * 6 + ["fraud"] * 12
    values = []
    for index, topic in enumerate(ref_topics):
        values.append(
            {
                "time": (start + timedelta(minutes=index)).isoformat().replace("+00:00", "Z"),
                "period": "reference",
                "features": {"emb1": 0.1 + index * 0.01, "emb2": 0.2, "emb3": 0.1},
                "attributes": {"topic": topic},
                "metric": 0.1,
            }
        )
    current_start = start + timedelta(hours=1)
    for index, topic in enumerate(cur_topics):
        values.append(
            {
                "time": (current_start + timedelta(minutes=index)).isoformat().replace("+00:00", "Z"),
                "period": "current",
                "features": {"emb1": 2.2 + index * 0.01, "emb2": -1.1, "emb3": 1.4},
                "attributes": {"topic": topic},
                "metric": 2.2,
            }
        )
    return {
        "bucket_id": "bucket-llm-query-001",
        "source_id": "source-llm-query-001",
        "adapter_id": "adapter-llm-query-001",
        "feature_id": "multivariate",
        "window_start": "2027-07-01T00:00:00Z",
        "window_end": "2027-07-01T01:19:00Z",
        "row_count": len(values),
        "payload": json.dumps({"values": values, "featureColumns": ["emb1", "emb2", "emb3"], "attributeColumns": ["topic"]}),
    }


def test_registry_resolves_llm_query_semantic_aliases() -> None:
    assert get_runtime_method("llm_query_semantic_window") is run_llm_query_semantic_window
    assert get_runtime_method("query_centroid_cosine_shift") is run_llm_query_semantic_window
    assert get_runtime_method("text_domain_classifier_drift") is run_llm_query_semantic_window
    assert get_runtime_method("topic_distribution_shift") is run_llm_query_semantic_window


def test_llm_query_semantic_runtime_detects_all_supported_variants() -> None:
    cases = [
        ("query_centroid_cosine_shift", "QUERY_CENTROID_COSINE_SHIFT", {"threshold": 0.1}),
        ("text_domain_classifier_drift", "TEXT_DOMAIN_CLASSIFIER_DRIFT", {"threshold": 0.6}),
        ("topic_distribution_shift", "TOPIC_DISTRIBUTION_SHIFT", {"topic_col": "topic", "threshold": 0.1}),
    ]
    for runtime_key, variant_id, params in cases:
        output = run_llm_query_semantic_window(_assignment(runtime_key, variant_id, **params), _bucket(), {})

        assert output["runStatus"] == "success"
        assert output["level"] == "drift"
        assert output["event"] is not None
        assert output["diagnostics"]["algorithmImplSucceeded"] is True
        assert output["metrics"]["measurements"]["PROCESSED_COUNT"] == 40
