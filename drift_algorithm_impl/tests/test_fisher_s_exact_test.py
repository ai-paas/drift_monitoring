from __future__ import annotations

import pandas as pd

from drift_algorithm.methods.batchdistributioncomparison import detect_fisher_s_exact_test


def _count_frame(reference: dict[str, int], current: dict[str, int]) -> pd.DataFrame:
    rows = []
    for category, count in reference.items():
        rows.append({"time": "2026-01-01 00:00", "category": category, "count": count})
    for category, count in current.items():
        rows.append({"time": "2026-01-02 00:00", "category": category, "count": count})
    return pd.DataFrame(rows)


def test_two_by_two_fisher_exact_no_drift() -> None:
    data = _count_frame({"A": 10, "B": 10}, {"A": 11, "B": 9})
    result = detect_fisher_s_exact_test(
        data,
        reference_window=("2026-01-01", "2026-01-01 23:59"),
        current_window=("2026-01-02", "2026-01-02 23:59"),
        params={"category_col": "category", "count_col": "count", "alpha": 0.05},
    )
    assert result.variant_id == "TWO_BY_TWO_FISHER_EXACT"
    assert result.drift_detected is False
    assert result.p_value is not None and result.p_value > 0.05
    assert result.measurements["ODDS_RATIO"] is not None


def test_two_by_two_fisher_exact_detects_shift() -> None:
    data = _count_frame({"A": 18, "B": 2}, {"A": 2, "B": 18})
    result = detect_fisher_s_exact_test(
        data,
        reference_window=("2026-01-01", "2026-01-01 23:59"),
        current_window=("2026-01-02", "2026-01-02 23:59"),
        params={"category_col": "category", "count_col": "count", "alpha": 0.05},
    )
    assert result.drift_detected is True
    assert result.p_value is not None and result.p_value < 0.05


def test_one_sided_fisher_exact() -> None:
    data = _count_frame({"A": 18, "B": 2}, {"A": 2, "B": 18})
    result = detect_fisher_s_exact_test(
        data,
        reference_window=("2026-01-01", "2026-01-01 23:59"),
        current_window=("2026-01-02", "2026-01-02 23:59"),
        params={
            "variant_id": "ONE_SIDED_FISHER_EXACT",
            "category_col": "category",
            "count_col": "count",
            "alternative": "greater",
            "alpha": 0.05,
        },
    )
    assert result.variant_id == "ONE_SIDED_FISHER_EXACT"
    assert result.drift_detected is True
    assert result.metadata["alternative"] == "greater"


def test_extended_contingency_exact_surrogate() -> None:
    data = _count_frame({"A": 40, "B": 5, "C": 5}, {"A": 5, "B": 20, "C": 25})
    result = detect_fisher_s_exact_test(
        data,
        reference_window=("2026-01-01", "2026-01-01 23:59"),
        current_window=("2026-01-02", "2026-01-02 23:59"),
        params={
            "variant_id": "EXTENDED_CONTINGENCY_EXACT_TEST",
            "category_col": "category",
            "count_col": "count",
            "permutations": 500,
            "random_state": 7,
            "alpha": 0.05,
        },
    )
    assert result.variant_id == "EXTENDED_CONTINGENCY_EXACT_TEST"
    assert result.drift_detected is True
    assert result.measurements["ODDS_RATIO"] is None
    assert any("permutation" in warning for warning in result.warnings)


def test_fisher_validation_and_warnings() -> None:
    data = _count_frame({"A": 10, "B": 10, "C": 1}, {"A": 10, "B": 10, "C": 1})
    invalid = detect_fisher_s_exact_test(
        data,
        reference_window=("2026-01-01", "2026-01-01 23:59"),
        current_window=("2026-01-02", "2026-01-02 23:59"),
        params={"category_col": "category", "count_col": "count"},
    )
    assert invalid.severity == "not_applicable"

    dirty = _count_frame({"A": 10, "B": 10, "C": 10}, {"A": 10, "B": 10, "C": 10})
    dirty.loc[0, "count"] = None
    dirty.loc[1, "time"] = "not-a-time"
    result = detect_fisher_s_exact_test(
        dirty,
        reference_window=("2026-01-01", "2026-01-01 23:59"),
        current_window=("2026-01-02", "2026-01-02 23:59"),
        params={
            "variant_id": "EXTENDED_CONTINGENCY_EXACT_TEST",
            "category_col": "category",
            "count_col": "count",
            "permutations": 100,
        },
    )
    assert result.severity in {"normal", "drift_detected"}
    assert any("dropped" in warning for warning in result.warnings)
