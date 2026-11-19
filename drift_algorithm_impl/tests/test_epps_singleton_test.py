from __future__ import annotations

import numpy as np
import pandas as pd

from drift_algorithm.methods.batchdistributioncomparison import detect_epps_singleton_test


def _frame(reference: np.ndarray, current: np.ndarray) -> pd.DataFrame:
    ref_time = pd.date_range("2026-01-01 00:00", periods=len(reference), freq="min")
    cur_time = pd.date_range("2026-01-02 00:00", periods=len(current), freq="min")
    return pd.DataFrame({"time": list(ref_time) + list(cur_time), "value": list(reference) + list(current)})


def test_epps_singleton_default_no_drift() -> None:
    rng = np.random.default_rng(600)
    data = _frame(rng.normal(0, 1, 100), rng.normal(0, 1, 100))
    result = detect_epps_singleton_test(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 01:39"),
        current_window=("2026-01-02 00:00", "2026-01-02 01:39"),
    )
    assert result.variant_id == "TWO_SAMPLE_EPPS_SINGLETON"
    assert result.drift_detected is False
    assert result.severity == "normal"
    assert result.p_value is not None
    assert result.p_value >= 0.05
    assert {"TEST_STATISTIC", "EPPS_SINGLETON_STATISTIC", "P_VALUE", "DRIFT_ALARM_STATE"}.issubset(result.measurements)
    assert result.measurements["T_POINTS"] == [0.4, 0.8]


def test_epps_singleton_detects_distribution_shift() -> None:
    rng = np.random.default_rng(630)
    data = _frame(rng.normal(0, 1, 100), rng.normal(1.0, 1, 100))
    result = detect_epps_singleton_test(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 01:39"),
        current_window=("2026-01-02 00:00", "2026-01-02 01:39"),
    )
    assert result.p_value is not None
    assert result.p_value < 0.05
    assert result.drift_detected is True
    assert result.severity == "drift_detected"
    assert result.measurements["DRIFT_ALARM_STATE"] == "drift_detected"


def test_epps_singleton_custom_t_points_and_aliases() -> None:
    rng = np.random.default_rng(601)
    data = _frame(rng.normal(0, 1, 80), rng.normal(0, 1, 80))
    result = detect_epps_singleton_test(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 01:19"),
        current_window=("2026-01-02 00:00", "2026-01-02 01:19"),
        params={"t_points": [0.4, 0.8, 1.2], "threshold_or_alpha": 0.1, "p_value_method": "scipy_asymptotic"},
    )
    assert result.threshold == 0.1
    assert result.metadata["t_points"] == [0.4, 0.8, 1.2]
    assert result.measurements["T_POINTS"] == [0.4, 0.8, 1.2]

    bad_t = detect_epps_singleton_test(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 01:19"),
        current_window=("2026-01-02 00:00", "2026-01-02 01:19"),
        params={"t_points": [0.4, 0.4]},
    )
    assert bad_t.severity == "not_applicable"

    conflict = detect_epps_singleton_test(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 01:19"),
        current_window=("2026-01-02 00:00", "2026-01-02 01:19"),
        params={"alpha": 0.03, "significance_level": 0.05},
    )
    assert conflict.severity == "not_applicable"


def test_discrete_epps_singleton_numeric_variant() -> None:
    rng = np.random.default_rng(602)
    reference = rng.poisson(3, 120)
    current = rng.poisson(4, 120)
    data = _frame(reference.astype(float), current.astype(float))
    result = detect_epps_singleton_test(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 01:59"),
        current_window=("2026-01-02 00:00", "2026-01-02 01:59"),
        params={"variant_id": "DISCRETE_EPPS_SINGLETON"},
    )
    assert result.variant_id == "DISCRETE_EPPS_SINGLETON"
    assert "DISCRETE_VALUE_COUNT_REFERENCE" in result.measurements
    assert "DISCRETE_TOP_VALUE_FREQUENCIES" in result.measurements
    assert any("DISCRETE_EPPS_SINGLETON" in warning for warning in result.warnings)


def test_epps_singleton_not_applicable_cases() -> None:
    data = _frame(np.arange(3, dtype=float), np.arange(3, dtype=float))
    missing_windows = detect_epps_singleton_test(data)
    assert missing_windows.severity == "not_applicable"

    too_small = detect_epps_singleton_test(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:02"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:02"),
    )
    assert too_small.severity == "not_applicable"

    asymptotic = detect_epps_singleton_test(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:02"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:02"),
        params={"variant_id": "ASYMPTOTIC_EPPS_SINGLETON"},
    )
    assert asymptotic.severity == "not_applicable"

    bool_data = data.copy()
    bool_data["value"] = True
    bool_result = detect_epps_singleton_test(
        bool_data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:02"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:02"),
    )
    assert bool_result.severity == "not_applicable"

    bad_method = detect_epps_singleton_test(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:02"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:02"),
        params={"p_value_method": "permutation"},
    )
    assert bad_method.severity == "not_applicable"


def test_epps_singleton_warning_behavior() -> None:
    reference = np.repeat(np.arange(40, dtype=float), 2)
    current = np.arange(24, dtype=float) + 0.25
    data = _frame(reference, current)
    data["time"] = data["time"].astype(object)
    data.loc[0, "value"] = np.nan
    data.loc[1, "time"] = "not-a-time"
    result = detect_epps_singleton_test(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 01:19"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:23"),
        params={
            "multiple_testing_correction": "bonferroni",
            "sample_imbalance_warning_ratio": 2.0,
            "min_reference_size": 20,
            "min_current_size": 20,
            "t_points": [0.4, 0.8, 1.2, 1.6, 2.0],
        },
    )
    assert result.severity in {"normal", "drift_detected"}
    assert any("dropped" in warning for warning in result.warnings)
    assert any("ties" in warning or "unique-value" in warning for warning in result.warnings)
    assert any("imbalanced" in warning for warning in result.warnings)
    assert any("t_points" in warning for warning in result.warnings)
    assert any("multiple_testing_correction" in warning for warning in result.warnings)
