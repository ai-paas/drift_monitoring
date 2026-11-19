from __future__ import annotations

import numpy as np
import pandas as pd

from drift_algorithm.methods.batchdistributioncomparison import detect_mann_whitney_u_wilcoxon_rank_sum_test


def _frame(reference: np.ndarray, current: np.ndarray) -> pd.DataFrame:
    ref_time = pd.date_range("2026-01-01 00:00", periods=len(reference), freq="min")
    cur_time = pd.date_range("2026-01-02 00:00", periods=len(current), freq="min")
    return pd.DataFrame(
        {
            "time": list(ref_time) + list(cur_time),
            "value": list(reference) + list(current),
        }
    )


def test_mann_whitney_two_sided_no_drift() -> None:
    rng = np.random.default_rng(21)
    reference = rng.normal(0, 1, 120)
    current = rng.normal(0, 1, 120)
    result = detect_mann_whitney_u_wilcoxon_rank_sum_test(
        _frame(reference, current),
        reference_window=("2026-01-01 00:00", "2026-01-01 01:59"),
        current_window=("2026-01-02 00:00", "2026-01-02 01:59"),
    )

    assert result.method_id == "DM-018"
    assert result.variant_id == "MANN_WHITNEY_TWO_SIDED"
    assert result.drift_detected is False
    assert result.severity == "normal"
    assert result.measurements["DRIFT_ALARM_STATE"] == "normal"
    assert {"TEST_STATISTIC", "P_VALUE", "SAMPLE_SIZE"}.issubset(result.measurements)


def test_mann_whitney_two_sided_detects_shift() -> None:
    rng = np.random.default_rng(22)
    reference = rng.normal(0, 1, 120)
    current = rng.normal(1.5, 1, 120)
    result = detect_mann_whitney_u_wilcoxon_rank_sum_test(
        _frame(reference, current),
        reference_window=("2026-01-01 00:00", "2026-01-01 01:59"),
        current_window=("2026-01-02 00:00", "2026-01-02 01:59"),
    )

    assert result.p_value is not None
    assert result.p_value < 0.05
    assert result.drift_detected is True
    assert result.severity == "drift_detected"


def test_mann_whitney_one_sided_direction_orientation() -> None:
    rng = np.random.default_rng(23)
    reference = rng.normal(0, 1, 120)
    current = rng.normal(1.5, 1, 120)
    increase = detect_mann_whitney_u_wilcoxon_rank_sum_test(
        _frame(reference, current),
        reference_window=("2026-01-01 00:00", "2026-01-01 01:59"),
        current_window=("2026-01-02 00:00", "2026-01-02 01:59"),
        params={"variant_id": "MANN_WHITNEY_ONE_SIDED", "direction_or_alternative": "increase"},
    )
    opposite = detect_mann_whitney_u_wilcoxon_rank_sum_test(
        _frame(reference, current),
        reference_window=("2026-01-01 00:00", "2026-01-01 01:59"),
        current_window=("2026-01-02 00:00", "2026-01-02 01:59"),
        params={"variant_id": "MANN_WHITNEY_ONE_SIDED", "direction_or_alternative": "decrease"},
    )

    assert increase.metadata["alternative"] == "less"
    assert increase.drift_detected is True
    assert opposite.metadata["alternative"] == "greater"
    assert opposite.drift_detected is False


def test_mann_whitney_exact_variant_and_tie_rejection() -> None:
    data = _frame(np.array([1.0, 2.0, 3.0, 4.0, 5.0]), np.array([6.0, 7.0, 8.0, 9.0, 10.0]))
    exact = detect_mann_whitney_u_wilcoxon_rank_sum_test(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:04"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:04"),
        params={"variant_id": "MANN_WHITNEY_EXACT"},
    )
    assert exact.metadata["p_value_method"] == "exact"
    assert exact.severity == "drift_detected"

    tied = _frame(np.array([1.0, 1.0, 2.0, 3.0, 4.0]), np.array([4.0, 5.0, 6.0, 7.0, 8.0]))
    rejected = detect_mann_whitney_u_wilcoxon_rank_sum_test(
        tied,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:04"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:04"),
        params={"variant_id": "MANN_WHITNEY_EXACT"},
    )
    assert rejected.severity == "not_applicable"


def test_mann_whitney_invalid_rows_warn_and_effective_counts() -> None:
    data = _frame(np.arange(10, dtype=float), np.arange(10, dtype=float) + 1)
    data.loc[0, "value"] = np.nan
    result = detect_mann_whitney_u_wilcoxon_rank_sum_test(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:09"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:09"),
        params={"min_reference_size": 5, "min_current_size": 5},
    )
    assert result.measurements["SAMPLE_SIZE"]["reference"] == 9
    assert any("dropped" in warning for warning in result.warnings)


def test_mann_whitney_not_applicable_cases() -> None:
    data = _frame(np.arange(4, dtype=float), np.arange(4, dtype=float))

    missing_windows = detect_mann_whitney_u_wilcoxon_rank_sum_test(data)
    assert missing_windows.severity == "not_applicable"

    too_small = detect_mann_whitney_u_wilcoxon_rank_sum_test(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:03"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:03"),
    )
    assert too_small.severity == "not_applicable"

    no_direction = detect_mann_whitney_u_wilcoxon_rank_sum_test(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:03"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:03"),
        params={"variant_id": "MANN_WHITNEY_ONE_SIDED"},
    )
    assert no_direction.severity == "not_applicable"

    bool_data = data.copy()
    bool_data["value"] = True
    bool_result = detect_mann_whitney_u_wilcoxon_rank_sum_test(
        bool_data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:03"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:03"),
    )
    assert bool_result.severity == "not_applicable"
