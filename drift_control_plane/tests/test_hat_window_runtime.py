from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone

from drift_server.app.drift.runtime_registry import get_runtime_method
from drift_server.app.runtime_methods.hat_window import run_hat_window


def _assignment(runtime_key: str, variant_id: str) -> dict:
    return {
        "assignment_id": f"assign-{runtime_key}",
        "runtime_method_key": runtime_key,
        "params_json": json.dumps(
            {
                "variant_id": variant_id,
                "error_col": "error",
                "node_col": "node_id",
                "online_accuracy_col": "online_accuracy",
                "alternate_created_col": "alternate_created",
                "replacement_col": "tree_replaced",
                "warning_delta": 0.1,
                "drift_delta": 0.2,
                "min_reference_size": 30,
                "min_current_size": 30,
                "min_node_size": 8,
            }
        ),
    }


def _bucket() -> dict:
    start = datetime(2027, 10, 1, tzinfo=timezone.utc)
    values = []
    for index in range(30):
        values.append(
            {
                "time": (start + timedelta(minutes=index * 2)).isoformat().replace("+00:00", "Z"),
                "period": "reference",
                "features": {
                    "error": 1.0 if index in {4, 14, 24} else 0.0,
                    "online_accuracy": 0.95,
                    "alternate_created": 0.0,
                    "tree_replaced": 0.0,
                },
                "attributes": {"node_id": "stable"},
            }
        )
    current_start = start + timedelta(hours=1)
    for index in range(30):
        values.append(
            {
                "time": (current_start + timedelta(minutes=index * 2)).isoformat().replace("+00:00", "Z"),
                "period": "current",
                "features": {
                    "error": 1.0 if index >= 8 else 0.0,
                    "online_accuracy": 0.4 if 10 <= index <= 14 else 0.9,
                    "alternate_created": 1.0 if 10 <= index <= 14 else 0.0,
                    "tree_replaced": 1.0 if 13 <= index <= 14 else 0.0,
                },
                "attributes": {"node_id": "leaf-7" if index >= 8 else "stable"},
            }
        )
    return {
        "bucket_id": "bucket-hat-001",
        "source_id": "source-hat-001",
        "adapter_id": "adapter-hat-001",
        "feature_id": "multivariate",
        "window_start": "2027-10-01T00:00:00Z",
        "window_end": "2027-10-01T02:00:00Z",
        "row_count": len(values),
        "payload": json.dumps(
            {
                "values": values,
                "featureColumns": ["error", "online_accuracy", "alternate_created", "tree_replaced"],
                "attributeColumns": ["node_id"],
            }
        ),
    }


def test_registry_resolves_hat_aliases() -> None:
    assert get_runtime_method("hat_window") is run_hat_window
    assert get_runtime_method("hat_adwin_node_monitoring") is run_hat_window
    assert get_runtime_method("hat_alternate_tree_replacement") is run_hat_window


def test_hat_runtime_detects_all_supported_variants() -> None:
    cases = [
        ("hat_adwin_node_monitoring", "HAT_ADWIN_NODE_MONITORING"),
        ("hat_alternate_tree_replacement", "HAT_ALTERNATE_TREE_REPLACEMENT"),
    ]
    for runtime_key, variant_id in cases:
        output = run_hat_window(_assignment(runtime_key, variant_id), _bucket(), {})

        assert output["runStatus"] == "success"
        assert output["level"] == "drift"
        assert output["event"] is not None
        assert output["diagnostics"]["algorithmImplSucceeded"] is True
        assert output["metrics"]["measurements"]["PROCESSED_COUNT"] == 60
