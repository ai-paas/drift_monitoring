from __future__ import annotations

import numpy as np
import pandas as pd

from drift_algorithm.methods.batchdistributioncomparison import detect_lsdd


def _frame(reference: np.ndarray, current: np.ndarray) -> pd.DataFrame:
    ref_time = pd.date_range("2026-01-01 00:00", periods=len(reference), freq="min")
    cur_time = pd.date_range("2026-01-02 00:00", periods=len(current), freq="min")
    return pd.DataFrame({"time": list(ref_time) + list(cur_time), "value": list(reference) + list(current)})


def test_lsdd_default_score_only_watch() -> None:
    rng = np.random.default_rng(800)
    data = _frame(rng.normal(0, 1, 60), rng.normal(0, 1, 60))
    result = detect_lsdd(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:59"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:59"),
    )
    assert result.variant_id == "LEAST_SQUARES_DENSITY_DIFFERENCE"
    assert result.drift_detected is None
    assert result.severity == "watch"
    assert result.p_value is None
    assert result.measurements["DRIFT_ALARM_STATE"] == "undetermined"
    assert result.measurements["TEST_STATISTIC"] == result.measurements["LSDD_SCORE"]
    assert result.measurements["N_CENTERS"] == 100
    assert result.measurements["REGULARIZATION_LAMBDA"] == 0.001


def test_lsdd_threshold_normal_and_drift() -> None:
    rng = np.random.default_rng(801)
    normal_data = _frame(rng.normal(0, 1, 60), rng.normal(0, 1, 60))
    normal = detect_lsdd(
        normal_data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:59"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:59"),
        params={"threshold": 10.0},
    )
    assert normal.drift_detected is False
    assert normal.severity == "normal"

    drift_data = _frame(rng.normal(0, 1, 60), rng.normal(2.0, 1, 60))
    drift = detect_lsdd(
        drift_data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:59"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:59"),
        params={"threshold": 0.01},
    )
    assert drift.measurements["LSDD_SCORE"] > 0.01
    assert drift.drift_detected is True
    assert drift.severity == "drift_detected"


def test_lsdd_permutation_no_drift_and_drift() -> None:
    rng = np.random.default_rng(800)
    no_drift_data = _frame(rng.normal(0, 1, 60), rng.normal(0, 1, 60))
    no_drift = detect_lsdd(
        no_drift_data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:59"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:59"),
        params={"variant_id": "PERMUTATION_LSDD", "permutation_count": 99, "random_seed": 40},
    )
    assert no_drift.p_value is not None
    assert no_drift.p_value >= 0.05
    assert no_drift.drift_detected is False
    assert no_drift.measurements["PERMUTATION_COUNT"] == 99

    rng = np.random.default_rng(830)
    drift_data = _frame(rng.normal(0, 1, 60), rng.normal(1.5, 1, 60))
    drift = detect_lsdd(
        drift_data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:59"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:59"),
        params={"variant_id": "PERMUTATION_LSDD", "permutation_count": 99, "random_seed": 41},
    )
    assert drift.p_value is not None
    assert drift.p_value < 0.05
    assert drift.drift_detected is True
    assert drift.severity == "drift_detected"


def test_lsdd_bandwidth_center_and_regularization_policy() -> None:
    rng = np.random.default_rng(802)
    data = _frame(rng.normal(0, 1, 40), rng.normal(0, 1, 40))
    fixed = detect_lsdd(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:39"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:39"),
        params={"kernel_bandwidth": 1.5, "n_centers": 20, "regularization_lambda": 0.01},
    )
    assert fixed.measurements["BANDWIDTH_POLICY"] == "fixed"
    assert fixed.measurements["KERNEL_BANDWIDTH"] == 1.5
    assert fixed.measurements["N_CENTERS"] == 20
    assert fixed.measurements["REGULARIZATION_LAMBDA"] == 0.01

    random_centers = detect_lsdd(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:39"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:39"),
        params={"center_selection": "random", "n_centers": 10, "random_seed": 42},
    )
    assert random_centers.measurements["CENTER_SELECTION"] == "random"
    assert random_centers.measurements["N_CENTERS"] == 10

    bad_lambda = detect_lsdd(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:39"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:39"),
        params={"regularization_lambda": -1},
    )
    assert bad_lambda.severity == "not_applicable"


def test_lsdd_aliases_deferred_and_not_applicable() -> None:
    rng = np.random.default_rng(803)
    data = _frame(rng.normal(0, 1, 40), rng.normal(0, 1, 40))
    threshold_alias = detect_lsdd(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:39"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:39"),
        params={"threshold_or_alpha": 10.0},
    )
    assert threshold_alias.threshold == 10.0
    assert any("threshold_or_alpha" in warning for warning in threshold_alias.warnings)

    alpha_alias = detect_lsdd(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:39"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:39"),
        params={"p_value_method": "permutation", "threshold_or_alpha": 0.1, "permutation_count": 49, "random_seed": 43},
    )
    assert alpha_alias.threshold == 0.1
    assert alpha_alias.metadata["alpha"] == 0.1

    multivariate = detect_lsdd(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:39"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:39"),
        params={"feature_cols": ["a", "b"]},
    )
    assert multivariate.severity == "not_applicable"


def test_lsdd_not_applicable_and_warning_behavior() -> None:
    identical = detect_lsdd(
        _frame(np.ones(20), np.ones(20)),
        reference_window=("2026-01-01 00:00", "2026-01-01 00:19"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:19"),
    )
    assert identical.severity == "not_applicable"

    small = detect_lsdd(
        _frame(np.arange(3, dtype=float), np.arange(3, dtype=float)),
        reference_window=("2026-01-01 00:00", "2026-01-01 00:02"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:02"),
    )
    assert small.severity == "not_applicable"

    bool_data = _frame(np.arange(3, dtype=float), np.arange(3, dtype=float))
    bool_data["value"] = True
    bool_result = detect_lsdd(
        bool_data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:02"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:02"),
    )
    assert bool_result.severity == "not_applicable"

    reference = np.repeat(np.arange(40, dtype=float), 2)
    current = np.arange(24, dtype=float) + 0.25
    warn_data = _frame(reference, current)
    warn_data["time"] = warn_data["time"].astype(object)
    warn_data.loc[0, "value"] = np.nan
    warn_data.loc[1, "time"] = "not-a-time"
    result = detect_lsdd(
        warn_data,
        reference_window=("2026-01-01 00:00", "2026-01-01 01:19"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:23"),
        params={
            "p_value_method": "permutation",
            "multiple_testing_correction": "bonferroni",
            "sample_imbalance_warning_ratio": 2.0,
            "permutation_count": 49,
            "random_seed": 44,
            "min_reference_size": 20,
            "min_current_size": 20,
        },
    )
    assert result.severity in {"normal", "drift_detected"}


def test_lsdd_with_preprocessing_uses_identity_projection() -> None:
    data = _frame(np.arange(40, dtype=float), np.arange(40, dtype=float) + 4.0)
    result = detect_lsdd(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:39"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:39"),
        params={
            "variant_id": "LSDD_WITH_PREPROCESSING",
            "value_col": "value",
            "threshold": 0.01,
            "min_reference_size": 20,
            "min_current_size": 20,
        },
    )

    assert result.severity == "drift_detected"
    assert result.metadata["preprocessing_policy"] == "identity_numeric_projection"
    assert result.metadata["projection_policy"] == "single_projected_numeric_stream"
    assert result.metadata["projection_count"] == 1
