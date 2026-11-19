from __future__ import annotations

import numpy as np
import pandas as pd

from drift_algorithm.methods.batchdistributioncomparison import detect_energy_distance


def _frame(reference: np.ndarray, current: np.ndarray) -> pd.DataFrame:
    ref_time = pd.date_range("2026-01-01 00:00", periods=len(reference), freq="min")
    cur_time = pd.date_range("2026-01-02 00:00", periods=len(current), freq="min")
    return pd.DataFrame({"time": list(ref_time) + list(cur_time), "value": list(reference) + list(current)})


def test_energy_distance_default_distance_only_watch() -> None:
    rng = np.random.default_rng(500)
    data = _frame(rng.normal(0, 1, 100), rng.normal(0, 1, 100))
    result = detect_energy_distance(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 01:39"),
        current_window=("2026-01-02 00:00", "2026-01-02 01:39"),
    )
    assert result.variant_id == "UNIVARIATE_ENERGY_DISTANCE"
    assert result.drift_detected is None
    assert result.severity == "watch"
    assert result.p_value is None
    assert result.measurements["DRIFT_ALARM_STATE"] == "undetermined"
    assert result.measurements["TEST_STATISTIC"] == result.measurements["ENERGY_DISTANCE"]
    assert any("no distance threshold" in warning for warning in result.warnings)


def test_energy_distance_threshold_normal_and_drift() -> None:
    rng = np.random.default_rng(501)
    normal_data = _frame(rng.normal(0, 1, 100), rng.normal(0, 1, 100))
    normal = detect_energy_distance(
        normal_data,
        reference_window=("2026-01-01 00:00", "2026-01-01 01:39"),
        current_window=("2026-01-02 00:00", "2026-01-02 01:39"),
        params={"threshold": 10.0},
    )
    assert normal.drift_detected is False
    assert normal.severity == "normal"
    assert normal.threshold == 10.0
    assert normal.p_value is None

    shifted_data = _frame(rng.normal(0, 1, 100), rng.normal(2.0, 1, 100))
    drift = detect_energy_distance(
        shifted_data,
        reference_window=("2026-01-01 00:00", "2026-01-01 01:39"),
        current_window=("2026-01-02 00:00", "2026-01-02 01:39"),
        params={"threshold": 0.2},
    )
    assert drift.measurements["ENERGY_DISTANCE"] > 0.2
    assert drift.drift_detected is True
    assert drift.severity == "drift_detected"


def test_energy_distance_permutation_no_drift_and_drift() -> None:
    rng = np.random.default_rng(500)
    no_drift_data = _frame(rng.normal(0, 1, 100), rng.normal(0, 1, 100))
    no_drift = detect_energy_distance(
        no_drift_data,
        reference_window=("2026-01-01 00:00", "2026-01-01 01:39"),
        current_window=("2026-01-02 00:00", "2026-01-02 01:39"),
        params={"variant_id": "ENERGY_DISTANCE_PERMUTATION_TEST", "permutation_count": 199, "random_seed": 20},
    )
    assert no_drift.p_value is not None
    assert no_drift.p_value >= 0.05
    assert no_drift.drift_detected is False
    assert no_drift.measurements["PERMUTATION_COUNT"] == 199

    rng = np.random.default_rng(530)
    drift_data = _frame(rng.normal(0, 1, 100), rng.normal(1.2, 1, 100))
    drift = detect_energy_distance(
        drift_data,
        reference_window=("2026-01-01 00:00", "2026-01-01 01:39"),
        current_window=("2026-01-02 00:00", "2026-01-02 01:39"),
        params={"variant_id": "ENERGY_DISTANCE_PERMUTATION_TEST", "permutation_count": 199, "random_seed": 21},
    )
    assert drift.p_value is not None
    assert drift.p_value < 0.05
    assert drift.drift_detected is True
    assert drift.severity == "drift_detected"


def test_energy_distance_threshold_or_alpha_policy() -> None:
    rng = np.random.default_rng(502)
    data = _frame(rng.normal(0, 1, 40), rng.normal(0, 1, 40))
    threshold_alias = detect_energy_distance(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:39"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:39"),
        params={"threshold_or_alpha": 10.0},
    )
    assert threshold_alias.threshold == 10.0
    assert any("threshold_or_alpha" in warning for warning in threshold_alias.warnings)

    alpha_alias = detect_energy_distance(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:39"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:39"),
        params={
            "variant_id": "ENERGY_DISTANCE_PERMUTATION_TEST",
            "threshold_or_alpha": 0.1,
            "permutation_count": 49,
            "random_seed": 22,
        },
    )
    assert alpha_alias.threshold == 0.1
    assert alpha_alias.metadata["alpha"] == 0.1

    conflict = detect_energy_distance(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:39"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:39"),
        params={"variant_id": "ENERGY_DISTANCE_PERMUTATION_TEST", "alpha": 0.03, "significance_level": 0.05},
    )
    assert conflict.severity == "not_applicable"


def test_energy_distance_not_applicable_cases() -> None:
    data = _frame(np.arange(3, dtype=float), np.arange(3, dtype=float))
    missing_windows = detect_energy_distance(data)
    assert missing_windows.severity == "not_applicable"

    too_small = detect_energy_distance(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:02"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:02"),
    )
    assert too_small.severity == "not_applicable"

    multivariate = detect_energy_distance(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:02"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:02"),
        params={"variant_id": "MULTIVARIATE_ENERGY_DISTANCE", "feature_cols": ["a", "b"]},
    )
    assert multivariate.severity == "not_applicable"

    bool_data = data.copy()
    bool_data["value"] = True
    bool_result = detect_energy_distance(
        bool_data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:02"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:02"),
    )
    assert bool_result.severity == "not_applicable"

    bad_metric = detect_energy_distance(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:02"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:02"),
        params={"distance_metric": "wasserstein"},
    )
    assert bad_metric.severity == "not_applicable"


def test_energy_distance_warning_behavior() -> None:
    reference = np.repeat(np.arange(40, dtype=float), 2)
    current = np.arange(24, dtype=float) + 0.25
    data = _frame(reference, current)
    data["time"] = data["time"].astype(object)
    data.loc[0, "value"] = np.nan
    data.loc[1, "time"] = "not-a-time"
    result = detect_energy_distance(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 01:19"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:23"),
        params={
            "variant_id": "ENERGY_DISTANCE_PERMUTATION_TEST",
            "multiple_testing_correction": "bonferroni",
            "sample_imbalance_warning_ratio": 2.0,
            "permutation_count": 49,
            "random_seed": 23,
            "min_reference_size": 20,
            "min_current_size": 20,
        },
    )
    assert result.severity in {"normal", "drift_detected"}


def test_multivariate_energy_distance_uses_projected_stream() -> None:
    data = _frame(np.arange(40, dtype=float), np.arange(40, dtype=float) + 4.0)
    result = detect_energy_distance(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:39"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:39"),
        params={
            "variant_id": "MULTIVARIATE_ENERGY_DISTANCE",
            "value_col": "value",
            "threshold": 0.2,
            "min_reference_size": 20,
            "min_current_size": 20,
        },
    )

    assert result.severity == "drift_detected"
    assert result.metadata["projection_policy"] == "single_projected_numeric_stream"
    assert result.metadata["projection_count"] == 1
