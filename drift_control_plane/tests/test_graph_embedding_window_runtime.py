from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone

from drift_server.app.drift.runtime_registry import get_runtime_method
from drift_server.app.runtime_methods.graph_embedding_window import run_graph_embedding_window


def _assignment(runtime_key: str, variant_id: str, **params: object) -> dict:
    payload = {
        "variant_id": variant_id,
        "embedding_cols": ["x1", "x2", "x3"],
        "alpha": 0.1,
        "permutation_count": 19,
        "random_state": 11,
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
    start = datetime(2027, 6, 1, tzinfo=timezone.utc)
    values = []
    for index in range(20):
        group = "A" if index < 10 else "B"
        x = -1.0 + (index / 10.0)
        values.append(
            {
                "time": (start + timedelta(minutes=index)).isoformat().replace("+00:00", "Z"),
                "period": "reference",
                "features": {"x1": x, "x2": x * 0.5, "x3": (index % 7) / 7.0},
                "attributes": {"class": group},
                "metric": x,
            }
        )
    current_start = start + timedelta(hours=1)
    for index in range(20):
        group = "A" if index < 10 else "B"
        x = -1.0 + (index / 10.0)
        shift = 2.0 if group == "A" else 3.0
        values.append(
            {
                "time": (current_start + timedelta(minutes=index)).isoformat().replace("+00:00", "Z"),
                "period": "current",
                "features": {"x1": x + shift, "x2": x * 0.5 - shift, "x3": (index % 7) / 7.0 + shift},
                "attributes": {"class": group},
                "metric": x + shift,
            }
        )
    return {
        "bucket_id": "bucket-graph-embedding-001",
        "source_id": "source-graph-embedding-001",
        "adapter_id": "adapter-graph-embedding-001",
        "feature_id": "multivariate",
        "window_start": "2027-06-01T00:00:00Z",
        "window_end": "2027-06-01T01:19:00Z",
        "row_count": len(values),
        "payload": json.dumps({"values": values, "featureColumns": ["x1", "x2", "x3"], "attributeColumns": ["class"]}),
    }


def test_registry_resolves_graph_embedding_aliases() -> None:
    assert get_runtime_method("graph_embedding_window") is run_graph_embedding_window
    assert get_runtime_method("graph_embedding_mmd") is run_graph_embedding_window
    assert get_runtime_method("graph_embedding_centroid_shift") is run_graph_embedding_window
    assert get_runtime_method("node_representation_drift") is run_graph_embedding_window


def test_graph_embedding_runtime_detects_all_supported_variants() -> None:
    cases = [
        ("graph_embedding_mmd", "GRAPH_EMBEDDING_MMD", {}),
        ("graph_embedding_centroid_shift", "GRAPH_EMBEDDING_CENTROID_SHIFT", {"threshold": 0.5}),
        ("node_representation_drift", "NODE_REPRESENTATION_DRIFT", {"node_group_col": "class", "threshold": 0.5, "min_group_size": 5}),
    ]
    for runtime_key, variant_id, params in cases:
        output = run_graph_embedding_window(_assignment(runtime_key, variant_id, **params), _bucket(), {})

        assert output["runStatus"] == "success"
        assert output["level"] == "drift"
        assert output["event"] is not None
        assert output["diagnostics"]["algorithmImplSucceeded"] is True
        assert output["metrics"]["measurements"]["PROCESSED_COUNT"] == 40
