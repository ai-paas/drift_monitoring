from __future__ import annotations

import numpy as np
import pandas as pd

from drift_algorithm.methods.batchdistributioncomparison import detect_baumgartner_weiss_schindler_test


def _frame(reference: np.ndarray, current: np.ndarray) -> pd.DataFrame:
    ref_time = pd.date_range("2026-01-01 00:00", periods=len(reference), freq="min")
    cur_time = pd.date_range("2026-01-02 00:00", periods=len(current), freq="min")
    return pd.DataFrame({"time": list(ref_time) + list(cur_time), "value": list(reference) + list(current)})


def test_bws_default_no_drift() -> None:
    rng = np.random.default_rng(300)
    data = _frame(rng.normal(0, 1, 120), rng.normal(0, 1, 120))
    result = detect_baumgartner_weiss_schindler_test(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 01:59"),
        current_window=("2026-01-02 00:00", "2026-01-02 01:59"),
        params={"permutation_count": 199, "random_seed": 10},
    )
    assert result.variant_id == "BWS_TWO_SAMPLE"
    assert result.drift_detected is False
    assert result.severity == "normal"
    assert result.p_value is not None
    assert result.p_value >= 0.05
    assert {"TEST_STATISTIC", "P_VALUE", "DRIFT_ALARM_STATE", "SAMPLE_SIZE"}.issubset(result.measurements)
    assert "BWS_REFERENCE_COMPONENT" in result.measurements
    assert "BWS_CURRENT_COMPONENT" in result.measurements


def test_bws_rank_based_variant_uses_same_policy() -> None:
    rng = np.random.default_rng(301)
    data = _frame(rng.normal(0, 1, 80), rng.normal(0.2, 1, 80))
    result = detect_baumgartner_weiss_schindler_test(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 01:19"),
        current_window=("2026-01-02 00:00", "2026-01-02 01:19"),
        params={"variant_id": "BWS_RANK_BASED", "permutation_count": 99, "random_seed": 11},
    )
    assert result.variant_id == "BWS_RANK_BASED"
    assert result.metadata["backend"] == "local_bws_two_sample"
    assert result.measurements["PERMUTATION_COUNT"] == 99


def test_bws_detects_distribution_shift() -> None:
    rng = np.random.default_rng(340)
    data = _frame(rng.normal(0, 1, 120), rng.normal(1.1, 1, 120))
    result = detect_baumgartner_weiss_schindler_test(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 01:59"),
        current_window=("2026-01-02 00:00", "2026-01-02 01:59"),
        params={"permutation_count": 199, "random_seed": 11},
    )
    assert result.p_value is not None
    assert result.p_value < 0.05
    assert result.drift_detected is True
    assert result.severity == "drift_detected"
    assert result.measurements["MEDIAN_DELTA"] > 0


def test_bws_threshold_mode_and_tiny_statistic() -> None:
    data = _frame(np.array([0.0, 1.0, 2.0, 3.0]), np.array([0.0, 1.0, 2.0, 4.0]))
    result = detect_baumgartner_weiss_schindler_test(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:03"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:03"),
        params={
            "decision_policy": "threshold",
            "p_value_method": "none",
            "threshold": 1.0,
            "min_reference_size": 4,
            "min_current_size": 4,
        },
    )
    assert result.p_value is None
    assert result.threshold == 1.0
    assert np.isclose(result.measurements["BWS_REFERENCE_COMPONENT"], 1.0886863425925926)
    assert np.isclose(result.measurements["BWS_CURRENT_COMPONENT"], 0.5678530092592592)
    assert np.isclose(result.measurements["TEST_STATISTIC"], 0.8282696759259258)
    assert result.drift_detected is False
    assert any("threshold mode" in warning for warning in result.warnings)


def test_bws_alpha_aliases_and_validation() -> None:
    rng = np.random.default_rng(302)
    data = _frame(rng.normal(0, 1, 30), rng.normal(0, 1, 30))
    alpha_alias = detect_baumgartner_weiss_schindler_test(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:29"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:29"),
        params={"threshold_or_alpha": 0.1, "permutation_count": 49, "random_seed": 12},
    )
    assert alpha_alias.threshold == 0.1
    assert any("low permutation_count" in warning for warning in alpha_alias.warnings)

    conflict = detect_baumgartner_weiss_schindler_test(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:29"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:29"),
        params={"alpha": 0.03, "significance_level": 0.05},
    )
    assert conflict.severity == "not_applicable"

    exact = detect_baumgartner_weiss_schindler_test(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:29"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:29"),
        params={"p_value_method": "exact"},
    )
    assert exact.severity == "not_applicable"

    one_sided = detect_baumgartner_weiss_schindler_test(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:29"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:29"),
        params={"alternative": "greater"},
    )
    assert one_sided.severity == "not_applicable"


def test_bws_not_applicable_cases() -> None:
    data = _frame(np.arange(3, dtype=float), np.arange(3, dtype=float))
    missing_windows = detect_baumgartner_weiss_schindler_test(data)
    assert missing_windows.severity == "not_applicable"

    too_small = detect_baumgartner_weiss_schindler_test(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:02"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:02"),
    )
    assert too_small.severity == "not_applicable"

    deferred = detect_baumgartner_weiss_schindler_test(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:02"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:02"),
        params={"variant_id": "BWS_EXACT_OR_ASYMPTOTIC"},
    )
    assert deferred.severity == "not_applicable"

    bool_data = data.copy()
    bool_data["value"] = True
    bool_result = detect_baumgartner_weiss_schindler_test(
        bool_data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:02"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:02"),
    )
    assert bool_result.severity == "not_applicable"


def test_bws_warning_behavior_and_permutation_guardrail() -> None:
    reference = np.repeat(np.arange(40, dtype=float), 2)
    current = np.arange(24, dtype=float) + 0.25
    data = _frame(reference, current)
    data["time"] = data["time"].astype(object)
    data.loc[0, "value"] = np.nan
    data.loc[1, "time"] = "not-a-time"
    result = detect_baumgartner_weiss_schindler_test(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 01:19"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:23"),
        params={
            "multiple_testing_correction": "bonferroni",
            "sample_imbalance_warning_ratio": 2.0,
            "permutation_count": 49,
            "random_seed": 13,
            "min_reference_size": 20,
            "min_current_size": 20,
            "exact_method": "requested",
        },
    )
    assert result.severity in {"normal", "drift_detected"}
    assert any("dropped" in warning for warning in result.warnings)
    assert any("ties" in warning for warning in result.warnings)
    assert any("imbalanced" in warning for warning in result.warnings)
    assert any("low permutation_count" in warning for warning in result.warnings)
    assert any("multiple_testing_correction" in warning for warning in result.warnings)
    assert any("exact_method" in warning for warning in result.warnings)

    guardrail = detect_baumgartner_weiss_schindler_test(
        _frame(np.arange(30, dtype=float), np.arange(30, dtype=float)),
        reference_window=("2026-01-01 00:00", "2026-01-01 00:29"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:29"),
        params={"permutation_max_total_size": 10},
    )
    assert guardrail.severity == "not_applicable"
