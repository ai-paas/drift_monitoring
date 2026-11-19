from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone

from drift_server.app.drift.runtime_registry import get_runtime_method
from drift_server.app.runtime_methods.generic_categorical_contingency_window import (
    run_generic_categorical_contingency_window,
)


def _assignment(variant_id: str) -> dict:
    return {
        "assignment_id": f"assign-{variant_id.lower()}",
        "runtime_method_key": "generic_categorical_contingency_window",
        "params_json": json.dumps(
            {
                "variant_id": variant_id,
                "alpha": 0.05,
                "category_col": "category",
                "count_col": "count",
                "min_reference_size": 1,
                "min_current_size": 1,
            }
        ),
    }


def _bucket(reference: dict[str, int] | None = None, current: dict[str, int] | None = None) -> dict:
    reference = reference or {"A": 80, "B": 15, "C": 5}
    current = current or {"A": 20, "B": 30, "C": 50}
    start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    values = []
    for index, (category, count) in enumerate(reference.items()):
        values.append(
            {
                "time": (start + timedelta(minutes=index)).isoformat().replace("+00:00", "Z"),
                "category": category,
                "count": count,
                "period": "reference",
            }
        )
    current_start = start + timedelta(days=1)
    for index, (category, count) in enumerate(current.items()):
        values.append(
            {
                "time": (current_start + timedelta(minutes=index)).isoformat().replace("+00:00", "Z"),
                "category": category,
                "count": count,
                "period": "current",
            }
        )
    return {
        "bucket_id": "bucket-001",
        "source_id": "source-001",
        "adapter_id": "adapter-001",
        "feature_id": "category",
        "window_start": "2026-01-01T00:00:00Z",
        "window_end": "2026-01-02T00:02:00Z",
        "row_count": len(values),
        "payload": json.dumps({"values": values}),
    }


def test_registry_resolves_categorical_contingency_aliases() -> None:
    assert get_runtime_method("generic_categorical_contingency_window") is run_generic_categorical_contingency_window
    assert get_runtime_method("chi_square_window") is run_generic_categorical_contingency_window
    assert get_runtime_method("fisher_exact_window") is run_generic_categorical_contingency_window
    assert get_runtime_method("g_test_window") is run_generic_categorical_contingency_window


def test_generic_categorical_contingency_runtime_detects_chi_square_shift() -> None:
    output = run_generic_categorical_contingency_window(_assignment("CHI_SQUARE_HOMOGENEITY"), _bucket(), {})

    assert output["runStatus"] == "success"
    assert output["level"] == "drift"
    assert output["event"] is not None
    assert output["diagnostics"]["algorithmImplSucceeded"] is True
    assert output["metrics"]["measurements"]["PROCESSED_COUNT"] == 200


def test_generic_categorical_contingency_runtime_detects_fisher_shift() -> None:
    output = run_generic_categorical_contingency_window(
        _assignment("TWO_BY_TWO_FISHER_EXACT"),
        _bucket(reference={"A": 30, "B": 2}, current={"A": 10, "B": 20}),
        {},
    )

    assert output["runStatus"] == "success"
    assert output["level"] == "drift"
    assert output["diagnostics"]["algorithmImplSucceeded"] is True
