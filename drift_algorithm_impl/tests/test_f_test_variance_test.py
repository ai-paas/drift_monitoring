from __future__ import annotations

import numpy as np
import pandas as pd

from drift_algorithm.methods.batchdistributioncomparison import detect_f_test_variance_test


def _frame(reference: np.ndarray, current: np.ndarray) -> pd.DataFrame:
    ref_time = pd.date_range("2026-01-01 00:00", periods=len(reference), freq="min")
    cur_time = pd.date_range("2026-01-02 00:00", periods=len(current), freq="min")
    return pd.DataFrame({"time": list(ref_time) + list(cur_time), "value": list(reference) + list(current)})


def test_f_test_default_no_drift() -> None:
    rng = np.random.default_rng(400)
    data = _frame(rng.normal(0, 1, 120), rng.normal(0, 1, 120))
    result = detect_f_test_variance_test(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 01:59"),
        current_window=("2026-01-02 00:00", "2026-01-02 01:59"),
    )
    assert result.variant_id == "F_TEST_EQUAL_VARIANCE"
    assert result.drift_detected is False
    assert result.severity == "normal"
    assert result.p_value is not None
    assert result.p_value >= 0.05
    assert {"TEST_STATISTIC", "P_VALUE", "DRIFT_ALARM_STATE", "SAMPLE_SIZE"}.issubset(result.measurements)
    assert "VARIANCE_RATIO" in result.measurements
    assert "DEGREES_OF_FREEDOM" in result.measurements


def test_f_test_detects_variance_increase() -> None:
    rng = np.random.default_rng(430)
    data = _frame(rng.normal(0, 1, 120), rng.normal(0, 2.5, 120))
    result = detect_f_test_variance_test(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 01:59"),
        current_window=("2026-01-02 00:00", "2026-01-02 01:59"),
        params={"alternative": "current_greater"},
    )
    assert result.p_value is not None
    assert result.p_value < 0.05
    assert result.drift_detected is True
    assert result.severity == "drift_detected"
    assert result.measurements["VARIANCE_RATIO"] > 1


def test_f_test_detects_variance_decrease() -> None:
    rng = np.random.default_rng(460)
    data = _frame(rng.normal(0, 2.5, 120), rng.normal(0, 1, 120))
    result = detect_f_test_variance_test(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 01:59"),
        current_window=("2026-01-02 00:00", "2026-01-02 01:59"),
        params={"alternative": "current_less"},
    )
    assert result.p_value is not None
    assert result.p_value < 0.05
    assert result.drift_detected is True
    assert result.measurements["VARIANCE_RATIO"] < 1


def test_f_test_two_sided_symmetry() -> None:
    rng = np.random.default_rng(431)
    reference = rng.normal(0, 1, 80)
    current = rng.normal(0, 2, 80)
    forward = detect_f_test_variance_test(
        _frame(reference, current),
        reference_window=("2026-01-01 00:00", "2026-01-01 01:19"),
        current_window=("2026-01-02 00:00", "2026-01-02 01:19"),
    )
    swapped = detect_f_test_variance_test(
        _frame(current, reference),
        reference_window=("2026-01-01 00:00", "2026-01-01 01:19"),
        current_window=("2026-01-02 00:00", "2026-01-02 01:19"),
    )
    assert forward.p_value is not None
    assert swapped.p_value is not None
    assert np.isclose(forward.p_value, swapped.p_value)
    assert np.isclose(forward.measurements["VARIANCE_RATIO"], 1 / swapped.measurements["VARIANCE_RATIO"])
    assert np.isclose(forward.measurements["TEST_STATISTIC"], swapped.measurements["TEST_STATISTIC"])


def test_f_test_parameter_aliases_and_validation() -> None:
    rng = np.random.default_rng(401)
    data = _frame(rng.normal(0, 1, 30), rng.normal(0, 1, 30))
    alias = detect_f_test_variance_test(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:29"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:29"),
        params={"threshold_or_alpha": 0.1},
    )
    assert alias.threshold == 0.1

    conflict = detect_f_test_variance_test(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:29"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:29"),
        params={"alpha": 0.03, "significance_level": 0.05},
    )
    assert conflict.severity == "not_applicable"

    bad_alt = detect_f_test_variance_test(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:29"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:29"),
        params={"alternative": "left"},
    )
    assert bad_alt.severity == "not_applicable"

    bad_method = detect_f_test_variance_test(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:29"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:29"),
        params={"p_value_method": "permutation"},
    )
    assert bad_method.severity == "not_applicable"


def test_f_test_not_applicable_cases() -> None:
    data = _frame(np.arange(2, dtype=float), np.arange(2, dtype=float))
    missing_windows = detect_f_test_variance_test(data)
    assert missing_windows.severity == "not_applicable"

    too_small = detect_f_test_variance_test(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:01"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:01"),
    )
    assert too_small.severity == "not_applicable"

    zero_variance = detect_f_test_variance_test(
        _frame(np.ones(5), np.arange(5, dtype=float)),
        reference_window=("2026-01-01 00:00", "2026-01-01 00:04"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:04"),
    )
    assert zero_variance.severity == "error"
    assert zero_variance.drift_detected is None

    anova = detect_f_test_variance_test(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:01"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:01"),
        params={"variant_id": "ANOVA_F_TEST_GROUP_MEAN"},
    )
    assert anova.severity == "not_applicable"

    bool_data = data.copy()
    bool_data["value"] = True
    bool_result = detect_f_test_variance_test(
        bool_data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:01"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:01"),
    )
    assert bool_result.severity == "not_applicable"


def test_f_test_warning_behavior() -> None:
    reference = np.repeat(np.arange(20, dtype=float), 2)
    current = np.arange(8, dtype=float) + 0.25
    data = _frame(reference, current)
    data["time"] = data["time"].astype(object)
    data.loc[0, "value"] = np.nan
    data.loc[1, "time"] = "not-a-time"
    result = detect_f_test_variance_test(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:39"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:07"),
        params={
            "multiple_testing_correction": "bonferroni",
            "sample_imbalance_warning_ratio": 2.0,
            "low_power_sample_size": 20,
        },
    )
    assert result.severity in {"normal", "drift_detected"}
    assert any("dropped" in warning for warning in result.warnings)
    assert any("tied" in warning or "repeated" in warning for warning in result.warnings)
    assert any("imbalanced" in warning for warning in result.warnings)
    assert any("small effective sample" in warning for warning in result.warnings)
    assert any("non-normality" in warning for warning in result.warnings)
    assert any("multiple_testing_correction" in warning for warning in result.warnings)
