from __future__ import annotations

import numpy as np
import pandas as pd

from drift_algorithm.methods.batchdistributioncomparison import detect_cramer_von_mises_test


def _frame(reference: np.ndarray, current: np.ndarray) -> pd.DataFrame:
    ref_time = pd.date_range("2026-01-01 00:00", periods=len(reference), freq="min")
    cur_time = pd.date_range("2026-01-02 00:00", periods=len(current), freq="min")
    return pd.DataFrame({"time": list(ref_time) + list(cur_time), "value": list(reference) + list(current)})


def test_cramer_von_mises_default_no_drift() -> None:
    rng = np.random.default_rng(90)
    data = _frame(rng.normal(0, 1, 120), rng.normal(0, 1, 120))
    result = detect_cramer_von_mises_test(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 01:59"),
        current_window=("2026-01-02 00:00", "2026-01-02 01:59"),
    )
    assert result.variant_id == "TWO_SAMPLE_CVM"
    assert result.drift_detected is False
    assert result.severity == "normal"
    assert result.p_value is not None
    assert result.p_value >= 0.05
    assert {"TEST_STATISTIC", "P_VALUE", "DRIFT_ALARM_STATE", "SAMPLE_SIZE"}.issubset(result.measurements)
    assert result.measurements["SAMPLE_SIZE_REFERENCE"] == 120
    assert result.measurements["SAMPLE_SIZE_CURRENT"] == 120


def test_cramer_von_mises_detects_distribution_shift() -> None:
    rng = np.random.default_rng(130)
    data = _frame(rng.normal(0, 1, 160), rng.normal(1.1, 1, 160))
    result = detect_cramer_von_mises_test(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 02:39"),
        current_window=("2026-01-02 00:00", "2026-01-02 02:39"),
    )
    assert result.p_value is not None
    assert result.p_value < 0.05
    assert result.drift_detected is True
    assert result.severity == "drift_detected"
    assert result.measurements["MEDIAN_DELTA"] > 0


def test_cramer_von_mises_alpha_aliases_and_p_value_method() -> None:
    rng = np.random.default_rng(91)
    data = _frame(rng.normal(0, 1, 30), rng.normal(0, 1, 30))
    exact = detect_cramer_von_mises_test(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:29"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:29"),
        params={"threshold_or_alpha": 0.1, "p_value_method": "exact"},
    )
    assert exact.threshold == 0.1
    assert exact.metadata["p_value_method"] == "exact"

    significance_alias = detect_cramer_von_mises_test(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:29"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:29"),
        params={"alpha": 0.03, "significance_level": 0.03},
    )
    assert significance_alias.threshold == 0.03

    conflict = detect_cramer_von_mises_test(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:29"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:29"),
        params={"alpha": 0.03, "threshold_or_alpha": 0.05},
    )
    assert conflict.severity == "not_applicable"


def test_cramer_von_mises_parameter_validation() -> None:
    data = _frame(np.arange(30, dtype=float), np.arange(30, dtype=float))
    one_sided = detect_cramer_von_mises_test(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:29"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:29"),
        params={"alternative": "greater"},
    )
    assert one_sided.severity == "not_applicable"

    bad_method = detect_cramer_von_mises_test(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:29"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:29"),
        params={"p_value_method": "permutation"},
    )
    assert bad_method.severity == "not_applicable"

    bad_nan_policy = detect_cramer_von_mises_test(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:29"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:29"),
        params={"nan_policy": "raise"},
    )
    assert bad_nan_policy.severity == "not_applicable"


def test_cramer_von_mises_not_applicable_cases() -> None:
    data = _frame(np.arange(3, dtype=float), np.arange(3, dtype=float))
    missing_windows = detect_cramer_von_mises_test(data)
    assert missing_windows.severity == "not_applicable"

    too_small = detect_cramer_von_mises_test(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:02"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:02"),
    )
    assert too_small.severity == "not_applicable"

    one_sample = detect_cramer_von_mises_test(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:02"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:02"),
        params={"variant_id": "ONE_SAMPLE_CVM"},
    )
    assert one_sample.severity == "not_applicable"

    k_sample = detect_cramer_von_mises_test(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:02"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:02"),
        params={"variant_id": "K_SAMPLE_CVM"},
    )
    assert k_sample.severity == "not_applicable"

    bool_data = data.copy()
    bool_data["value"] = True
    bool_result = detect_cramer_von_mises_test(
        bool_data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:02"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:02"),
    )
    assert bool_result.severity == "not_applicable"


def test_cramer_von_mises_warning_behavior() -> None:
    reference = np.repeat(np.arange(40, dtype=float), 2)
    current = np.arange(24, dtype=float) + 0.25
    data = _frame(reference, current)
    data["time"] = data["time"].astype(object)
    data.loc[0, "value"] = np.nan
    data.loc[1, "time"] = "not-a-time"
    result = detect_cramer_von_mises_test(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 01:19"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:23"),
        params={
            "multiple_testing_correction": "bonferroni",
            "sample_imbalance_warning_ratio": 2.0,
            "min_reference_size": 20,
            "min_current_size": 20,
        },
    )
    assert result.severity in {"normal", "drift_detected"}
    assert any("dropped" in warning for warning in result.warnings)
    assert any("ties" in warning for warning in result.warnings)
    assert any("imbalanced" in warning for warning in result.warnings)
    assert any("multiple_testing_correction" in warning for warning in result.warnings)
