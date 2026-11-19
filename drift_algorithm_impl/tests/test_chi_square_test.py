from __future__ import annotations

import pandas as pd

from drift_algorithm.methods.batchdistributioncomparison import detect_chi_square_test


def _count_frame(reference: dict[str, int], current: dict[str, int]) -> pd.DataFrame:
    rows = []
    for category, count in reference.items():
        rows.append({"time": "2026-01-01 00:00", "category": category, "count": count})
    for category, count in current.items():
        rows.append({"time": "2026-01-02 00:00", "category": category, "count": count})
    return pd.DataFrame(rows)


def test_chi_square_homogeneity_no_drift() -> None:
    data = _count_frame({"A": 50, "B": 30, "C": 20}, {"A": 51, "B": 29, "C": 20})
    result = detect_chi_square_test(
        data,
        reference_window=("2026-01-01", "2026-01-01 23:59"),
        current_window=("2026-01-02", "2026-01-02 23:59"),
        params={"category_col": "category", "count_col": "count", "alpha": 0.01},
    )
    assert result.variant_id == "CHI_SQUARE_HOMOGENEITY"
    assert result.drift_detected is False
    assert result.measurements["P_VALUE"] > 0.01
    assert result.measurements["CATEGORY_COUNT"] == 3


def test_chi_square_homogeneity_detects_distribution_shift() -> None:
    data = _count_frame({"A": 80, "B": 15, "C": 5}, {"A": 20, "B": 30, "C": 50})
    result = detect_chi_square_test(
        data,
        reference_window=("2026-01-01", "2026-01-01 23:59"),
        current_window=("2026-01-02", "2026-01-02 23:59"),
        params={"category_col": "category", "count_col": "count", "alpha": 0.05},
    )
    assert result.drift_detected is True
    assert result.p_value is not None and result.p_value < 0.05
    assert result.measurements["CATEGORY_PROPORTION_DELTA"]["C"] > 0


def test_chi_square_goodness_of_fit_uses_reference_expected_counts() -> None:
    data = _count_frame({"A": 70, "B": 20, "C": 10}, {"A": 30, "B": 30, "C": 40})
    result = detect_chi_square_test(
        data,
        reference_window=("2026-01-01", "2026-01-01 23:59"),
        current_window=("2026-01-02", "2026-01-02 23:59"),
        params={
            "variant_id": "CHI_SQUARE_GOODNESS_OF_FIT",
            "category_col": "category",
            "count_col": "count",
            "alpha": 0.05,
        },
    )
    assert result.variant_id == "CHI_SQUARE_GOODNESS_OF_FIT"
    assert result.drift_detected is True
    assert "current_vs_expected" in result.measurements["STANDARDIZED_RESIDUALS"]


def test_chi_square_row_per_observation_and_low_expected_warning() -> None:
    rows = []
    rows.extend({"time": "2026-01-01", "category": category} for category in ["A"] * 25 + ["B"] * 1)
    rows.extend({"time": "2026-01-02", "category": category} for category in ["A"] * 20 + ["B"] * 6)
    data = pd.DataFrame(rows)
    result = detect_chi_square_test(
        data,
        reference_window=("2026-01-01", "2026-01-01 23:59"),
        current_window=("2026-01-02", "2026-01-02 23:59"),
        params={
            "variant_id": "CHI_SQUARE_WITH_LOW_EXPECTED_COUNT_CAUTION",
            "category_col": "category",
            "low_expected_threshold": 5,
        },
    )
    assert result.measurements["LOW_EXPECTED_COUNT"] > 0
    assert any("expected cells" in warning for warning in result.warnings)


def test_chi_square_validation_and_warnings() -> None:
    data = _count_frame({"A": 10, "B": 10}, {"A": 10, "B": 10})
    missing = detect_chi_square_test(
        data,
        reference_window=("2026-01-01", "2026-01-01 23:59"),
        current_window=("2026-01-02", "2026-01-02 23:59"),
        params={"category_col": "missing"},
    )
    assert missing.severity == "not_applicable"

    dirty = _count_frame({"A": 10, "B": 10, "C": 10}, {"A": 10, "B": 10, "C": 10})
    dirty.loc[0, "count"] = None
    dirty.loc[1, "time"] = "not-a-time"
    result = detect_chi_square_test(
        dirty,
        reference_window=("2026-01-01", "2026-01-01 23:59"),
        current_window=("2026-01-02", "2026-01-02 23:59"),
        params={"category_col": "category", "count_col": "count", "min_reference_size": 1, "min_current_size": 1},
    )
    assert result.severity in {"normal", "drift_detected"}
    assert any("dropped" in warning for warning in result.warnings)
