from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone

from drift_server.app.drift.runtime_registry import get_runtime_method
from drift_server.app.runtime_methods.drift_retraining_window import run_drift_retraining_window


def _assignment(runtime_key: str, variant_id: str, **params: object) -> dict:
    payload = {
        "variant_id": variant_id,
        "metric_col": "metric",
        "champion_metric_col": "champion_metric",
        "challenger_metric_col": "challenger_metric",
        "threshold": 0.2,
        "warning_threshold": 0.1,
        "uplift_threshold": 0.05,
        "metric_direction": "higher_is_worse",
        "min_reference_size": 30,
        "min_current_size": 30,
        **params,
    }
    return {
        "assignment_id": f"assign-{runtime_key}",
        "runtime_method_key": runtime_key,
        "params_json": json.dumps(payload),
    }


def _bucket() -> dict:
    start = datetime(2027, 9, 1, tzinfo=timezone.utc)
    values = []
    for index in range(30):
        values.append(
            {
                "time": (start + timedelta(minutes=index * 2)).isoformat().replace("+00:00", "Z"),
                "period": "reference",
                "features": {
                    "metric": 0.10 + (index % 3) * 0.01,
                    "champion_metric": 0.20,
                    "challenger_metric": 0.19,
                    "retraining_triggered": 0.0,
                    "model_promoted": 0.0,
                },
            }
        )
    current_start = start + timedelta(hours=1)
    for index in range(30):
        values.append(
            {
                "time": (current_start + timedelta(minutes=index * 2)).isoformat().replace("+00:00", "Z"),
                "period": "current",
                "features": {
                    "metric": 0.44 + (index % 4) * 0.01,
                    "champion_metric": 0.45,
                    "challenger_metric": 0.30,
                    "retraining_triggered": 1.0 if index >= 15 else 0.0,
                    "model_promoted": 1.0 if index >= 20 else 0.0,
                },
            }
        )
    return {
        "bucket_id": "bucket-retraining-001",
        "source_id": "source-retraining-001",
        "adapter_id": "adapter-retraining-001",
        "feature_id": "multivariate",
        "window_start": "2027-09-01T00:00:00Z",
        "window_end": "2027-09-01T02:00:00Z",
        "row_count": len(values),
        "payload": json.dumps(
            {
                "values": values,
                "featureColumns": [
                    "metric",
                    "champion_metric",
                    "challenger_metric",
                    "retraining_triggered",
                    "model_promoted",
                ],
            }
        ),
    }


def test_registry_resolves_drift_retraining_aliases() -> None:
    assert get_runtime_method("drift_retraining_window") is run_drift_retraining_window
    assert get_runtime_method("drift_retraining_with_adwin") is run_drift_retraining_window
    assert get_runtime_method("drift_retraining_with_page_hinkley") is run_drift_retraining_window
    assert get_runtime_method("drift_retraining_champion_challenger") is run_drift_retraining_window


def test_drift_retraining_runtime_detects_all_supported_variants() -> None:
    cases = [
        ("drift_retraining_with_adwin", "DRIFT_RETRAINING_WITH_ADWIN", {}),
        ("drift_retraining_with_page_hinkley", "DRIFT_RETRAINING_WITH_PAGE_HINKLEY", {"threshold": 1.0}),
        ("drift_retraining_champion_challenger", "DRIFT_RETRAINING_CHAMPION_CHALLENGER", {}),
    ]
    for runtime_key, variant_id, params in cases:
        output = run_drift_retraining_window(_assignment(runtime_key, variant_id, **params), _bucket(), {})

        assert output["runStatus"] == "success"
        assert output["level"] == "drift"
        assert output["event"] is not None
        assert output["diagnostics"]["algorithmImplSucceeded"] is True
        assert output["metrics"]["measurements"]["PROCESSED_COUNT"] == 60
