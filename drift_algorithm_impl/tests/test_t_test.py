from __future__ import annotations

import numpy as np
import pandas as pd

from drift_algorithm.methods.batchdistributioncomparison import detect_t_test


def _frame(reference: np.ndarray, current: np.ndarray) -> pd.DataFrame:
    ref_time = pd.date_range("2026-01-01 00:00", periods=len(reference), freq="min")
    cur_time = pd.date_range("2026-01-02 00:00", periods=len(current), freq="min")
    return pd.DataFrame({"time": list(ref_time) + list(cur_time), "value": list(reference) + list(current)})


def test_t_test_welch_default_no_drift() -> None:
    rng = np.random.default_rng(31)
    data = _frame(rng.normal(0, 1, 120), rng.normal(0, 1, 120))
    result = detect_t_test(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 01:59"),
        current_window=("2026-01-02 00:00", "2026-01-02 01:59"),
    )
    assert result.variant_id == "WELCH_T_TEST"
    assert result.drift_detected is False
    assert result.severity == "normal"
    assert result.metadata["equal_var"] is False
    assert {"TEST_STATISTIC", "P_VALUE", "DRIFT_ALARM_STATE", "SAMPLE_SIZE"}.issubset(result.measurements)


def test_t_test_welch_detects_mean_shift() -> None:
    rng = np.random.default_rng(32)
    data = _frame(rng.normal(0, 1, 120), rng.normal(1.5, 1, 120))
    result = detect_t_test(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 01:59"),
        current_window=("2026-01-02 00:00", "2026-01-02 01:59"),
    )
    assert result.p_value is not None
    assert result.p_value < 0.05
    assert result.drift_detected is True
    assert result.measurements["MEAN_DIFFERENCE"] > 0


def test_t_test_student_records_equal_var_and_warns_on_variance_ratio() -> None:
    rng = np.random.default_rng(33)
    data = _frame(rng.normal(0, 1, 100), rng.normal(0, 8, 100))
    result = detect_t_test(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 01:39"),
        current_window=("2026-01-02 00:00", "2026-01-02 01:39"),
        params={"variant_id": "TWO_SAMPLE_STUDENT_T_TEST"},
    )
    assert result.metadata["equal_var"] is True
    assert any("variance ratio" in warning for warning in result.warnings)


def test_t_test_one_sample_baseline_and_reference_fallback() -> None:
    rng = np.random.default_rng(34)
    data = _frame(rng.normal(0, 1, 80), rng.normal(1.0, 1, 80))
    fixed = detect_t_test(
        data,
        current_window=("2026-01-02 00:00", "2026-01-02 01:19"),
        params={"variant_id": "ONE_SAMPLE_T_TEST", "baseline_mean": 0.0},
    )
    assert fixed.drift_detected is True
    assert fixed.measurements["BASELINE_MEAN"] == 0.0

    fallback = detect_t_test(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 01:19"),
        current_window=("2026-01-02 00:00", "2026-01-02 01:19"),
        params={"variant_id": "ONE_SAMPLE_T_TEST"},
    )
    assert fallback.metadata["baseline_source"] == "reference_window_mean"
    assert any("reference window mean" in warning for warning in fallback.warnings)


def test_t_test_paired_variant_and_duplicate_rejection() -> None:
    pairs = np.arange(30)
    ref_time = pd.date_range("2026-01-01 00:00", periods=30, freq="min")
    cur_time = pd.date_range("2026-01-02 00:00", periods=30, freq="min")
    data = pd.DataFrame(
        {
            "time": list(ref_time) + list(cur_time),
            "value": list(np.linspace(0, 1, 30)) + list(np.linspace(0.5, 1.5, 30) + np.linspace(0, 0.1, 30)),
            "pair_id": list(pairs) + list(pairs),
        }
    )
    result = detect_t_test(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:29"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:29"),
        params={"variant_id": "PAIRED_T_TEST", "pair_col": "pair_id", "direction_or_alternative": "increase"},
    )
    assert result.metadata["paired"] is True
    assert result.metadata["alternative"] == "less"
    assert result.measurements["SAMPLE_SIZE"]["paired"] == 30

    duplicate = pd.concat([data, data.iloc[[0]]], ignore_index=True)
    rejected = detect_t_test(
        duplicate,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:29"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:29"),
        params={"variant_id": "PAIRED_T_TEST", "pair_col": "pair_id"},
    )
    assert rejected.severity == "not_applicable"


def test_t_test_direction_aliases() -> None:
    rng = np.random.default_rng(35)
    data = _frame(rng.normal(0, 1, 100), rng.normal(1.3, 1, 100))
    increase = detect_t_test(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 01:39"),
        current_window=("2026-01-02 00:00", "2026-01-02 01:39"),
        params={"variant_id": "WELCH_T_TEST", "direction_or_alternative": "increase"},
    )
    decrease = detect_t_test(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 01:39"),
        current_window=("2026-01-02 00:00", "2026-01-02 01:39"),
        params={"variant_id": "WELCH_T_TEST", "direction_or_alternative": "decrease"},
    )
    assert increase.metadata["alternative"] == "less"
    assert increase.drift_detected is True
    assert decrease.metadata["alternative"] == "greater"
    assert decrease.drift_detected is False


def test_t_test_not_applicable_cases() -> None:
    data = _frame(np.arange(1, dtype=float), np.arange(1, dtype=float))
    missing_windows = detect_t_test(data)
    assert missing_windows.severity == "not_applicable"

    too_small = detect_t_test(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:00"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:00"),
    )
    assert too_small.severity == "not_applicable"

    bad_alpha = detect_t_test(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:00"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:00"),
        params={"alpha": 2},
    )
    assert bad_alpha.severity == "not_applicable"

    bool_data = data.copy()
    bool_data["value"] = True
    bool_result = detect_t_test(
        bool_data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:00"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:00"),
    )
    assert bool_result.severity == "not_applicable"
