from __future__ import annotations

import numpy as np
import pandas as pd

from drift_algorithm.methods.batchdistributioncomparison import detect_mmd


def _frame(reference: np.ndarray, current: np.ndarray) -> pd.DataFrame:
    ref_time = pd.date_range("2026-01-01 00:00", periods=len(reference), freq="min")
    cur_time = pd.date_range("2026-01-02 00:00", periods=len(current), freq="min")
    return pd.DataFrame({"time": list(ref_time) + list(cur_time), "value": list(reference) + list(current)})


def test_mmd_default_score_only_watch() -> None:
    rng = np.random.default_rng(700)
    data = _frame(rng.normal(0, 1, 80), rng.normal(0, 1, 80))
    result = detect_mmd(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 01:19"),
        current_window=("2026-01-02 00:00", "2026-01-02 01:19"),
    )
    assert result.variant_id == "KERNEL_MMD_BIASED"
    assert result.drift_detected is None
    assert result.severity == "watch"
    assert result.p_value is None
    assert result.measurements["DRIFT_ALARM_STATE"] == "undetermined"
    assert result.measurements["TEST_STATISTIC"] == result.measurements["MMD_STATISTIC"]
    assert result.measurements["KERNEL"] == "rbf"
    assert result.measurements["KERNEL_BANDWIDTH"] > 0


def test_mmd_threshold_normal_and_drift() -> None:
    rng = np.random.default_rng(701)
    normal_data = _frame(rng.normal(0, 1, 80), rng.normal(0, 1, 80))
    normal = detect_mmd(
        normal_data,
        reference_window=("2026-01-01 00:00", "2026-01-01 01:19"),
        current_window=("2026-01-02 00:00", "2026-01-02 01:19"),
        params={"threshold": 10.0},
    )
    assert normal.drift_detected is False
    assert normal.severity == "normal"
    assert normal.p_value is None

    drift_data = _frame(rng.normal(0, 1, 80), rng.normal(2.0, 1, 80))
    drift = detect_mmd(
        drift_data,
        reference_window=("2026-01-01 00:00", "2026-01-01 01:19"),
        current_window=("2026-01-02 00:00", "2026-01-02 01:19"),
        params={"threshold": 0.01},
    )
    assert drift.measurements["MMD_STATISTIC"] > 0.01
    assert drift.drift_detected is True
    assert drift.severity == "drift_detected"


def test_mmd_permutation_no_drift_and_drift() -> None:
    rng = np.random.default_rng(700)
    no_drift_data = _frame(rng.normal(0, 1, 80), rng.normal(0, 1, 80))
    no_drift = detect_mmd(
        no_drift_data,
        reference_window=("2026-01-01 00:00", "2026-01-01 01:19"),
        current_window=("2026-01-02 00:00", "2026-01-02 01:19"),
        params={"p_value_method": "permutation", "permutation_count": 199, "random_seed": 30},
    )
    assert no_drift.p_value is not None
    assert no_drift.p_value >= 0.05
    assert no_drift.drift_detected is False
    assert no_drift.measurements["PERMUTATION_COUNT"] == 199

    rng = np.random.default_rng(730)
    drift_data = _frame(rng.normal(0, 1, 80), rng.normal(1.2, 1, 80))
    drift = detect_mmd(
        drift_data,
        reference_window=("2026-01-01 00:00", "2026-01-01 01:19"),
        current_window=("2026-01-02 00:00", "2026-01-02 01:19"),
        params={"p_value_method": "permutation", "permutation_count": 199, "random_seed": 31},
    )
    assert drift.p_value is not None
    assert drift.p_value < 0.05
    assert drift.drift_detected is True
    assert drift.severity == "drift_detected"


def test_mmd_unbiased_and_bandwidth_policy() -> None:
    rng = np.random.default_rng(702)
    data = _frame(rng.normal(0, 1, 40), rng.normal(0, 1, 40))
    unbiased = detect_mmd(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:39"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:39"),
        params={"variant_id": "KERNEL_MMD_UNBIASED", "kernel_bandwidth": 1.5},
    )
    assert np.isfinite(unbiased.measurements["MMD_STATISTIC"])
    assert unbiased.measurements["BANDWIDTH_POLICY"] == "fixed"
    assert unbiased.measurements["KERNEL_BANDWIDTH"] == 1.5

    gamma = detect_mmd(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:39"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:39"),
        params={"gamma": 0.5},
    )
    assert gamma.measurements["KERNEL_GAMMA"] == 0.5

    conflict = detect_mmd(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:39"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:39"),
        params={"gamma": 0.5, "kernel_bandwidth": 1.0},
    )
    assert conflict.severity == "not_applicable"


def test_mmd_parameter_aliases_and_deferred_variants() -> None:
    rng = np.random.default_rng(703)
    data = _frame(rng.normal(0, 1, 40), rng.normal(0, 1, 40))
    threshold_alias = detect_mmd(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:39"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:39"),
        params={"threshold_or_alpha": 10.0},
    )
    assert threshold_alias.threshold == 10.0
    assert any("threshold_or_alpha" in warning for warning in threshold_alias.warnings)

    alpha_alias = detect_mmd(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:39"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:39"),
        params={"p_value_method": "permutation", "threshold_or_alpha": 0.1, "permutation_count": 49, "random_seed": 32},
    )
    assert alpha_alias.threshold == 0.1
    assert alpha_alias.metadata["alpha"] == 0.1

    multivariate_data = data.copy()
    multivariate_data["a"] = np.r_[rng.normal(0, 1, 40), rng.normal(2, 1, 40)]
    multivariate_data["b"] = np.r_[rng.normal(0, 1, 40), rng.normal(2, 1, 40)]
    multivariate = detect_mmd(
        multivariate_data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:39"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:39"),
        params={"variant_id": "LINEAR_TIME_MMD", "feature_cols": ["a", "b"], "threshold": 0.01},
    )
    assert multivariate.severity == "drift_detected"
    assert multivariate.metadata["projection_policy"] == "feature_matrix_rbf_mmd"
    assert multivariate.metadata["projection_count"] == 2


def test_mmd_not_applicable_and_warning_behavior() -> None:
    data = _frame(np.ones(20), np.ones(20))
    identical = detect_mmd(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:19"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:19"),
    )
    assert identical.severity == "not_applicable"

    small = detect_mmd(
        _frame(np.arange(3, dtype=float), np.arange(3, dtype=float)),
        reference_window=("2026-01-01 00:00", "2026-01-01 00:02"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:02"),
    )
    assert small.severity == "not_applicable"

    bool_data = _frame(np.arange(3, dtype=float), np.arange(3, dtype=float))
    bool_data["value"] = True
    bool_result = detect_mmd(
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
    result = detect_mmd(
        warn_data,
        reference_window=("2026-01-01 00:00", "2026-01-01 01:19"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:23"),
        params={
            "p_value_method": "permutation",
            "multiple_testing_correction": "bonferroni",
            "sample_imbalance_warning_ratio": 2.0,
            "permutation_count": 49,
            "random_seed": 33,
            "min_reference_size": 20,
            "min_current_size": 20,
        },
    )
    assert result.severity in {"normal", "drift_detected"}


def test_mmd_projected_stream_variants() -> None:
    data = _frame(np.arange(40, dtype=float), np.arange(40, dtype=float) + 4.0)

    for variant_id in ("LINEAR_TIME_MMD", "STREAMING_MMD"):
        result = detect_mmd(
            data,
            reference_window=("2026-01-01 00:00", "2026-01-01 00:39"),
            current_window=("2026-01-02 00:00", "2026-01-02 00:39"),
            params={
                "variant_id": variant_id,
                "value_col": "value",
                "threshold": 0.01,
                "min_reference_size": 20,
                "min_current_size": 20,
            },
        )

        assert result.severity == "drift_detected"
        assert result.metadata["projection_policy"] == "single_projected_numeric_stream"
        assert result.metadata["projection_count"] == 1
        assert result.metadata["runtime_policy"] == "finite_replay_rbf_mmd"
