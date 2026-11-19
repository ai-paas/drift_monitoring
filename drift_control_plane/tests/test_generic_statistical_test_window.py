from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone

from drift_server.app.drift.runtime_registry import get_runtime_method
from drift_server.app.runtime_methods.generic_statistical_test_window import run_generic_statistical_test_window


def _assignment(variant_id: str, extra_params: dict | None = None) -> dict:
    params = {
        "variant_id": variant_id,
        "alpha": 0.05,
        "min_reference_size": 20,
        "min_current_size": 20,
    }
    if extra_params:
        params.update(extra_params)
    return {
        "assignment_id": f"assign-{variant_id.lower()}",
        "runtime_method_key": "generic_statistical_test_window",
        "params_json": json.dumps(params),
    }


def _bucket(reference_shift: float = 0.0, current_shift: float = 20.0) -> dict:
    start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    values = []
    for index in range(80):
        values.append(
            {
                "time": (start + timedelta(minutes=index)).isoformat().replace("+00:00", "Z"),
                "value": float(index % 10) + reference_shift,
                "period": "reference",
            }
        )
    current_start = start + timedelta(days=1)
    for index in range(80):
        values.append(
            {
                "time": (current_start + timedelta(minutes=index)).isoformat().replace("+00:00", "Z"),
                "value": float(index % 10) + current_shift,
                "period": "current",
            }
        )
    return {
        "bucket_id": "bucket-001",
        "source_id": "source-001",
        "adapter_id": "adapter-001",
        "feature_id": "score",
        "window_start": "2026-01-01T00:00:00Z",
        "window_end": "2026-01-02T01:19:00Z",
        "row_count": len(values),
        "payload": json.dumps({"values": values}),
    }


def _paired_bucket() -> dict:
    start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    values = []
    for index in range(30):
        values.append(
            {
                "time": (start + timedelta(minutes=index)).isoformat().replace("+00:00", "Z"),
                "value": float(index),
                "period": "reference",
                "pair_id": f"pair-{index:03d}",
            }
        )
    current_start = start + timedelta(days=1)
    for index in range(30):
        values.append(
            {
                "time": (current_start + timedelta(minutes=index)).isoformat().replace("+00:00", "Z"),
                "value": float(index) + 5.0 + (index % 3) * 0.1,
                "period": "current",
                "pair_id": f"pair-{index:03d}",
            }
        )
    return {
        "bucket_id": "bucket-paired-001",
        "source_id": "source-001",
        "adapter_id": "adapter-001",
        "feature_id": "score",
        "window_start": "2026-01-01T00:00:00Z",
        "window_end": "2026-01-02T00:29:00Z",
        "row_count": len(values),
        "payload": json.dumps({"values": values}),
    }


def test_registry_resolves_statistical_test_aliases() -> None:
    assert get_runtime_method("generic_statistical_test_window") is run_generic_statistical_test_window
    assert get_runtime_method("mann_whitney_window") is run_generic_statistical_test_window
    assert get_runtime_method("t_test_window") is run_generic_statistical_test_window
    assert get_runtime_method("levene_window") is run_generic_statistical_test_window


def test_generic_statistical_test_runtime_detects_mann_whitney_shift() -> None:
    output = run_generic_statistical_test_window(_assignment("MANN_WHITNEY_TWO_SIDED"), _bucket(), {})

    assert output["runStatus"] == "success"
    assert output["level"] == "drift"
    assert output["event"] is not None
    assert output["diagnostics"]["algorithmImplSucceeded"] is True
    assert output["metrics"]["measurements"]["PROCESSED_COUNT"] == 160


def test_generic_statistical_test_runtime_executes_promoted_variant() -> None:
    output = run_generic_statistical_test_window(_assignment("BWS_EXACT_OR_ASYMPTOTIC"), _bucket(), {})

    assert output["runStatus"] == "success"
    assert output["level"] == "drift"
    assert output["event"] is not None
    assert output["diagnostics"]["algorithmImplSucceeded"] is True
    assert output["diagnostics"]["algorithmMetadata"]["execution_policy"] == "permutation_bws_reference_current"
    assert output["metrics"]["measurements"]["PROCESSED_COUNT"] == 160


def test_generic_statistical_test_runtime_preserves_pair_id_for_paired_t_test() -> None:
    output = run_generic_statistical_test_window(
        _assignment(
            "PAIRED_T_TEST",
            {
                "pair_col": "pair_id",
                "direction_or_alternative": "increase",
                "min_reference_size": 20,
                "min_current_size": 20,
            },
        ),
        _paired_bucket(),
        {},
    )

    assert output["runStatus"] == "success"
    assert output["level"] == "drift"
    assert output["diagnostics"]["algorithmImplSucceeded"] is True
    assert output["diagnostics"]["algorithmMetadata"]["paired"] is True
    assert output["metrics"]["measurements"]["SAMPLE_SIZE"]["paired"] == 30
