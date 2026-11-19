from __future__ import annotations

import numpy as np
import pandas as pd

from drift_algorithm.methods.batchdistributioncomparison import detect_anderson_darling_test


def _frame(reference: np.ndarray, current: np.ndarray) -> pd.DataFrame:
    ref_time = pd.date_range("2026-01-01 00:00", periods=len(reference), freq="min")
    cur_time = pd.date_range("2026-01-02 00:00", periods=len(current), freq="min")
    return pd.DataFrame({"time": list(ref_time) + list(cur_time), "value": list(reference) + list(current)})


def test_anderson_darling_default_no_drift() -> None:
    rng = np.random.default_rng(50)
    data = _frame(rng.normal(0, 1, 120), rng.normal(0, 1, 120))
    result = detect_anderson_darling_test(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 01:59"),
        current_window=("2026-01-02 00:00", "2026-01-02 01:59"),
    )
    assert result.variant_id == "TWO_SAMPLE_ANDERSON_DARLING"
    assert result.drift_detected is False
    assert result.severity == "normal"
    assert result.p_value is not None
    assert result.p_value >= 0.05
    assert {"TEST_STATISTIC", "P_VALUE", "DRIFT_ALARM_STATE", "SAMPLE_SIZE"}.issubset(result.measurements)


def test_anderson_darling_detects_distribution_shift() -> None:
    rng = np.random.default_rng(80)
    data = _frame(rng.normal(0, 1, 160), rng.normal(1.2, 1, 160))
    result = detect_anderson_darling_test(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 02:39"),
        current_window=("2026-01-02 00:00", "2026-01-02 02:39"),
    )
    assert result.p_value is not None
    assert result.p_value < 0.05
    assert result.drift_detected is True
    assert result.severity == "drift_detected"
    assert result.measurements["DRIFT_ALARM_STATE"] == "drift_detected"


def test_tail_sensitive_ad_adds_tail_metadata() -> None:
    rng = np.random.default_rng(81)
    reference = rng.normal(0, 1, 180)
    current = np.concatenate([rng.normal(0, 1, 150), rng.normal(3.0, 0.25, 30)])
    data = _frame(reference, current)
    result = detect_anderson_darling_test(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 02:59"),
        current_window=("2026-01-02 00:00", "2026-01-02 02:59"),
        params={"variant_id": "TAIL_SENSITIVE_AD"},
    )
    assert result.variant_id == "TAIL_SENSITIVE_AD"
    assert result.measurements["TAIL_RATE_DELTA"]["upper"] > 0
    assert "TAIL_COUNTS_REFERENCE" in result.measurements
    assert "TAIL_RATES_CURRENT" in result.measurements


def test_anderson_darling_alpha_aliases_and_conflicts() -> None:
    rng = np.random.default_rng(82)
    data = _frame(rng.normal(0, 1, 80), rng.normal(0, 1, 80))
    threshold_alias = detect_anderson_darling_test(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 01:19"),
        current_window=("2026-01-02 00:00", "2026-01-02 01:19"),
        params={"threshold_or_alpha": 0.1},
    )
    assert threshold_alias.threshold == 0.1

    significance_alias = detect_anderson_darling_test(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 01:19"),
        current_window=("2026-01-02 00:00", "2026-01-02 01:19"),
        params={"alpha": 0.03, "significance_level": 0.03},
    )
    assert significance_alias.threshold == 0.03

    conflict = detect_anderson_darling_test(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 01:19"),
        current_window=("2026-01-02 00:00", "2026-01-02 01:19"),
        params={"alpha": 0.03, "significance_level": 0.05},
    )
    assert conflict.severity == "not_applicable"


def test_anderson_darling_not_applicable_cases() -> None:
    data = _frame(np.arange(3, dtype=float), np.arange(3, dtype=float))
    missing_windows = detect_anderson_darling_test(data)
    assert missing_windows.severity == "not_applicable"

    too_small = detect_anderson_darling_test(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:02"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:02"),
    )
    assert too_small.severity == "not_applicable"

    one_sample = detect_anderson_darling_test(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:02"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:02"),
        params={"variant_id": "ONE_SAMPLE_ANDERSON_DARLING"},
    )
    assert one_sample.severity == "not_applicable"

    k_sample = detect_anderson_darling_test(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:02"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:02"),
        params={"variant_id": "K_SAMPLE_ANDERSON_DARLING"},
    )
    assert k_sample.severity == "not_applicable"

    bool_data = data.copy()
    bool_data["value"] = True
    bool_result = detect_anderson_darling_test(
        bool_data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:02"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:02"),
    )
    assert bool_result.severity == "not_applicable"


def test_anderson_darling_warning_behavior() -> None:
    reference = np.repeat(np.arange(30, dtype=float), 2)
    current = np.repeat(np.arange(30, dtype=float) + 0.5, 2)
    data = _frame(reference, current)
    data["time"] = data["time"].astype(object)
    data.loc[0, "value"] = np.nan
    data.loc[1, "time"] = "not-a-time"
    result = detect_anderson_darling_test(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:59"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:59"),
        params={"multiple_testing_correction": "bonferroni", "min_reference_size": 20, "min_current_size": 20},
    )
    assert result.severity in {"normal", "drift_detected"}
    assert any("dropped" in warning for warning in result.warnings)
    assert any("ties" in warning for warning in result.warnings)
    assert any("multiple_testing_correction" in warning for warning in result.warnings)
