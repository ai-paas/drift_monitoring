from __future__ import annotations

import pandas as pd

from drift_algorithm.methods.batchdistributioncomparison import detect_g_test


def _count_frame(reference: dict[str, int], current: dict[str, int]) -> pd.DataFrame:
    rows = []
    for category, count in reference.items():
        rows.append({"time": "2026-01-01 00:00", "category": category, "count": count})
    for category, count in current.items():
        rows.append({"time": "2026-01-02 00:00", "category": category, "count": count})
    return pd.DataFrame(rows)


def test_g_test_independence_no_drift() -> None:
    data = _count_frame({"A": 50, "B": 30, "C": 20}, {"A": 49, "B": 31, "C": 20})
    result = detect_g_test(
        data,
        reference_window=("2026-01-01", "2026-01-01 23:59"),
        current_window=("2026-01-02", "2026-01-02 23:59"),
        params={"category_col": "category", "count_col": "count", "alpha": 0.01},
    )
    assert result.variant_id == "LIKELIHOOD_RATIO_G_TEST_INDEPENDENCE"
    assert result.drift_detected is False
    assert result.measurements["P_VALUE"] > 0.01


def test_g_test_independence_detects_shift() -> None:
    data = _count_frame({"A": 80, "B": 15, "C": 5}, {"A": 20, "B": 30, "C": 50})
    result = detect_g_test(
        data,
        reference_window=("2026-01-01", "2026-01-01 23:59"),
        current_window=("2026-01-02", "2026-01-02 23:59"),
        params={"category_col": "category", "count_col": "count", "alpha": 0.05},
    )
    assert result.drift_detected is True
    assert result.p_value is not None and result.p_value < 0.05
    assert result.measurements["G_STATISTIC"] == result.measurements["TEST_STATISTIC"]


def test_g_test_goodness_of_fit() -> None:
    data = _count_frame({"A": 70, "B": 20, "C": 10}, {"A": 30, "B": 30, "C": 40})
    result = detect_g_test(
        data,
        reference_window=("2026-01-01", "2026-01-01 23:59"),
        current_window=("2026-01-02", "2026-01-02 23:59"),
        params={
            "variant_id": "LIKELIHOOD_RATIO_G_TEST_GOF",
            "category_col": "category",
            "count_col": "count",
            "alpha": 0.05,
        },
    )
    assert result.variant_id == "LIKELIHOOD_RATIO_G_TEST_GOF"
    assert result.drift_detected is True
    assert result.measurements["DEGREES_OF_FREEDOM"] == 2


def test_g_test_small_count_caution_row_counts() -> None:
    rows = []
    rows.extend({"time": "2026-01-01", "category": category} for category in ["A"] * 25 + ["B"] * 1)
    rows.extend({"time": "2026-01-02", "category": category} for category in ["A"] * 20 + ["B"] * 6)
    data = pd.DataFrame(rows)
    result = detect_g_test(
        data,
        reference_window=("2026-01-01", "2026-01-01 23:59"),
        current_window=("2026-01-02", "2026-01-02 23:59"),
        params={
            "variant_id": "G_TEST_WITH_SMALL_COUNT_CAUTION",
            "category_col": "category",
            "small_count_threshold": 5,
        },
    )
    assert result.measurements["SMALL_EXPECTED_COUNT"] > 0
    assert any("expected cells" in warning for warning in result.warnings)


def test_g_test_validation_and_warnings() -> None:
    data = _count_frame({"A": 10, "B": 10}, {"A": 10, "B": 10})
    missing = detect_g_test(
        data,
        reference_window=("2026-01-01", "2026-01-01 23:59"),
        current_window=("2026-01-02", "2026-01-02 23:59"),
        params={"category_col": "missing"},
    )
    assert missing.severity == "not_applicable"

    dirty = _count_frame({"A": 10, "B": 10, "C": 10}, {"A": 10, "B": 10, "C": 10})
    dirty.loc[0, "count"] = None
    dirty.loc[1, "time"] = "not-a-time"
    result = detect_g_test(
        dirty,
        reference_window=("2026-01-01", "2026-01-01 23:59"),
        current_window=("2026-01-02", "2026-01-02 23:59"),
        params={"category_col": "category", "count_col": "count", "min_reference_size": 1, "min_current_size": 1},
    )
    assert result.severity in {"normal", "drift_detected"}
    assert any("dropped" in warning for warning in result.warnings)
