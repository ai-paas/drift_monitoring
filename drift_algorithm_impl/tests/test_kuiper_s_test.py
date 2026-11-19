from __future__ import annotations

import numpy as np
import pandas as pd

from drift_algorithm.methods.batchdistributioncomparison import detect_kuiper_s_test


def _frame(reference: np.ndarray, current: np.ndarray) -> pd.DataFrame:
    ref_time = pd.date_range("2026-01-01 00:00", periods=len(reference), freq="min")
    cur_time = pd.date_range("2026-01-02 00:00", periods=len(current), freq="min")
    return pd.DataFrame({"time": list(ref_time) + list(cur_time), "value": list(reference) + list(current)})


def test_kuiper_default_no_drift() -> None:
    rng = np.random.default_rng(200)
    data = _frame(rng.normal(0, 1, 120), rng.normal(0, 1, 120))
    result = detect_kuiper_s_test(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 01:59"),
        current_window=("2026-01-02 00:00", "2026-01-02 01:59"),
        params={"permutation_count": 199, "random_seed": 1},
    )
    assert result.variant_id == "KUIPER_TWO_SAMPLE"
    assert result.drift_detected is False
    assert result.severity == "normal"
    assert result.p_value is not None
    assert result.p_value >= 0.05
    assert {"TEST_STATISTIC", "P_VALUE", "DRIFT_ALARM_STATE", "SAMPLE_SIZE"}.issubset(result.measurements)
    assert "KUIPER_D_PLUS" in result.measurements
    assert "KUIPER_D_MINUS" in result.measurements


def test_kuiper_detects_distribution_shift() -> None:
    rng = np.random.default_rng(240)
    data = _frame(rng.normal(0, 1, 160), rng.normal(1.0, 1, 160))
    result = detect_kuiper_s_test(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 02:39"),
        current_window=("2026-01-02 00:00", "2026-01-02 02:39"),
        params={"permutation_count": 199, "random_seed": 2},
    )
    assert result.p_value is not None
    assert result.p_value < 0.05
    assert result.drift_detected is True
    assert result.severity == "drift_detected"
    assert result.measurements["TEST_STATISTIC"] == result.measurements["KUIPER_D_PLUS"] + result.measurements["KUIPER_D_MINUS"]


def test_kuiper_threshold_mode_and_tiny_statistic() -> None:
    data = _frame(np.array([0.0, 1.0, 2.0, 3.0]), np.array([0.0, 1.0, 2.0, 4.0]))
    result = detect_kuiper_s_test(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:03"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:03"),
        params={
            "decision_policy": "threshold",
            "p_value_method": "none",
            "threshold": 0.4,
            "min_reference_size": 4,
            "min_current_size": 4,
        },
    )
    assert result.p_value is None
    assert result.threshold == 0.4
    assert result.measurements["KUIPER_D_PLUS"] == 0.25
    assert result.measurements["KUIPER_D_MINUS"] == 0.0
    assert result.measurements["TEST_STATISTIC"] == 0.25
    assert result.drift_detected is False
    assert any("threshold mode" in warning for warning in result.warnings)

    identical = detect_kuiper_s_test(
        _frame(np.array([0.0, 1.0, 2.0, 3.0]), np.array([0.0, 1.0, 2.0, 3.0])),
        reference_window=("2026-01-01 00:00", "2026-01-01 00:03"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:03"),
        params={
            "decision_policy": "threshold",
            "p_value_method": "none",
            "threshold_or_alpha": 0.0,
            "min_reference_size": 4,
            "min_current_size": 4,
        },
    )
    assert identical.measurements["TEST_STATISTIC"] == 0.0
    assert identical.drift_detected is False


def test_kuiper_alpha_aliases_and_validation() -> None:
    rng = np.random.default_rng(201)
    data = _frame(rng.normal(0, 1, 30), rng.normal(0, 1, 30))
    alpha_alias = detect_kuiper_s_test(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:29"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:29"),
        params={"threshold_or_alpha": 0.1, "permutation_count": 49, "random_seed": 3},
    )
    assert alpha_alias.threshold == 0.1
    assert any("low permutation_count" in warning for warning in alpha_alias.warnings)

    conflict = detect_kuiper_s_test(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:29"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:29"),
        params={"alpha": 0.03, "significance_level": 0.05},
    )
    assert conflict.severity == "not_applicable"

    bad_method = detect_kuiper_s_test(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:29"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:29"),
        params={"p_value_method": "asymptotic"},
    )
    assert bad_method.severity == "not_applicable"

    one_sided = detect_kuiper_s_test(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:29"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:29"),
        params={"alternative": "greater"},
    )
    assert one_sided.severity == "not_applicable"


def test_kuiper_not_applicable_cases() -> None:
    data = _frame(np.arange(3, dtype=float), np.arange(3, dtype=float))
    missing_windows = detect_kuiper_s_test(data)
    assert missing_windows.severity == "not_applicable"

    too_small = detect_kuiper_s_test(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:02"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:02"),
    )
    assert too_small.severity == "not_applicable"

    circular = detect_kuiper_s_test(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:02"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:02"),
        params={"variant_id": "KUIPER_CIRCULAR_DATA"},
    )
    assert circular.severity == "not_applicable"

    one_sample = detect_kuiper_s_test(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:02"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:02"),
        params={"variant_id": "KUIPER_ONE_SAMPLE"},
    )
    assert one_sample.severity == "not_applicable"

    bool_data = data.copy()
    bool_data["value"] = True
    bool_result = detect_kuiper_s_test(
        bool_data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:02"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:02"),
    )
    assert bool_result.severity == "not_applicable"


def test_kuiper_warning_behavior_and_permutation_guardrail() -> None:
    reference = np.repeat(np.arange(40, dtype=float), 2)
    current = np.arange(24, dtype=float) + 0.25
    data = _frame(reference, current)
    data["time"] = data["time"].astype(object)
    data.loc[0, "value"] = np.nan
    data.loc[1, "time"] = "not-a-time"
    result = detect_kuiper_s_test(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 01:19"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:23"),
        params={
            "multiple_testing_correction": "bonferroni",
            "sample_imbalance_warning_ratio": 2.0,
            "permutation_count": 49,
            "random_seed": 4,
            "min_reference_size": 20,
            "min_current_size": 20,
        },
    )
    assert result.severity in {"normal", "drift_detected"}
    assert any("dropped" in warning for warning in result.warnings)
    assert any("ties" in warning for warning in result.warnings)
    assert any("imbalanced" in warning for warning in result.warnings)
    assert any("low permutation_count" in warning for warning in result.warnings)
    assert any("multiple_testing_correction" in warning for warning in result.warnings)

    guardrail = detect_kuiper_s_test(
        _frame(np.arange(30, dtype=float), np.arange(30, dtype=float)),
        reference_window=("2026-01-01 00:00", "2026-01-01 00:29"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:29"),
        params={"permutation_max_total_size": 10},
    )
    assert guardrail.severity == "not_applicable"
