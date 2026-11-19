from __future__ import annotations

import numpy as np
import pandas as pd

from drift_algorithm.methods.batchdistributioncomparison import detect_ks_test


def _frame(reference: np.ndarray, current: np.ndarray) -> pd.DataFrame:
    ref_time = pd.date_range("2026-01-01 00:00", periods=len(reference), freq="min")
    cur_time = pd.date_range("2026-01-02 00:00", periods=len(current), freq="min")
    return pd.DataFrame(
        {
            "time": list(ref_time) + list(cur_time),
            "value": list(reference) + list(current),
        }
    )


def test_ks_no_drift_default_two_sided() -> None:
    rng = np.random.default_rng(11)
    reference = rng.normal(0, 1, 240)
    current = rng.normal(0, 1, 240)
    result = detect_ks_test(
        _frame(reference, current),
        reference_window=("2026-01-01 00:00", "2026-01-01 03:59"),
        current_window=("2026-01-02 00:00", "2026-01-02 03:59"),
    )

    assert result.variant_id == "TWO_SAMPLE_KS_TWO_SIDED"
    assert result.drift_detected is False
    assert result.severity == "normal"
    assert {"KS_STATISTIC", "TEST_STATISTIC", "P_VALUE", "SAMPLE_SIZE"}.issubset(result.measurements)
    assert result.measurements["SAMPLE_SIZE_REFERENCE"] == 240
    assert result.measurements["SAMPLE_SIZE_CURRENT"] == 240


def test_ks_detects_shifted_distribution() -> None:
    rng = np.random.default_rng(3)
    reference = rng.normal(0, 1, 240)
    current = rng.normal(1.5, 1, 240)
    result = detect_ks_test(
        _frame(reference, current),
        reference_window=("2026-01-01 00:00", "2026-01-01 03:59"),
        current_window=("2026-01-02 00:00", "2026-01-02 03:59"),
    )

    assert result.p_value is not None
    assert result.p_value < 0.05
    assert result.drift_detected is True
    assert result.severity == "drift_detected"


def test_ks_one_sided_records_alternative_and_rejects_conflict() -> None:
    data = _frame(np.arange(100, dtype=float), np.arange(100, dtype=float) + 10)
    result = detect_ks_test(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 01:39"),
        current_window=("2026-01-02 00:00", "2026-01-02 01:39"),
        params={"variant_id": "TWO_SAMPLE_KS_ONE_SIDED_GREATER"},
    )
    assert result.metadata["alternative"] == "greater"

    conflict = detect_ks_test(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 01:39"),
        current_window=("2026-01-02 00:00", "2026-01-02 01:39"),
        params={"variant_id": "TWO_SAMPLE_KS_ONE_SIDED_GREATER", "alternative": "less"},
    )
    assert conflict.severity == "not_applicable"
    assert conflict.drift_detected is None


def test_ks_p_value_method_variants() -> None:
    data = _frame(np.linspace(0, 1, 40), np.linspace(0.2, 1.2, 40))
    exact = detect_ks_test(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:39"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:39"),
        params={"variant_id": "TWO_SAMPLE_KS_EXACT_PVALUE"},
    )
    asymp = detect_ks_test(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:39"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:39"),
        params={"variant_id": "TWO_SAMPLE_KS_ASYMPTOTIC_PVALUE"},
    )

    assert exact.metadata["p_value_method"] == "exact"
    assert asymp.metadata["p_value_method"] == "asymp"


def test_ks_ties_discrete_caution_uses_candidate_severity_when_significant() -> None:
    reference = np.repeat([0.0, 1.0], 60)
    current = np.repeat([2.0, 3.0], 60)
    result = detect_ks_test(
        _frame(reference, current),
        reference_window=("2026-01-01 00:00", "2026-01-01 01:59"),
        current_window=("2026-01-02 00:00", "2026-01-02 01:59"),
        params={"variant_id": "KS_WITH_TIES_OR_DISCRETE_CAUTION"},
    )

    assert result.drift_detected is True
    assert result.severity == "drift_candidate"
    assert any("ties" in warning or "unique-value" in warning for warning in result.warnings)


def test_ks_not_applicable_cases() -> None:
    data = _frame(np.arange(10, dtype=float), np.arange(10, dtype=float))

    missing_windows = detect_ks_test(data)
    assert missing_windows.severity == "not_applicable"

    too_small = detect_ks_test(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:09"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:09"),
    )
    assert too_small.severity == "not_applicable"

    deferred = detect_ks_test(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:09"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:09"),
        params={"variant_id": "ONE_SAMPLE_KS_KNOWN_CDF"},
    )
    assert deferred.severity == "not_applicable"
