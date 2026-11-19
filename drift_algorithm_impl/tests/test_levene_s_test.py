from __future__ import annotations

import numpy as np
import pandas as pd

from drift_algorithm.methods.batchdistributioncomparison import detect_levene_s_test


def _frame(reference: np.ndarray, current: np.ndarray) -> pd.DataFrame:
    ref_time = pd.date_range("2026-01-01 00:00", periods=len(reference), freq="min")
    cur_time = pd.date_range("2026-01-02 00:00", periods=len(current), freq="min")
    return pd.DataFrame({"time": list(ref_time) + list(cur_time), "value": list(reference) + list(current)})


def test_levene_default_brown_forsythe_no_drift() -> None:
    rng = np.random.default_rng(41)
    data = _frame(rng.normal(0, 1, 120), rng.normal(0, 1, 120))
    result = detect_levene_s_test(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 01:59"),
        current_window=("2026-01-02 00:00", "2026-01-02 01:59"),
    )
    assert result.variant_id == "BROWN_FORSYTHE_MEDIAN_CENTER"
    assert result.metadata["center"] == "median"
    assert result.drift_detected is False
    assert result.severity == "normal"
    assert {"TEST_STATISTIC", "P_VALUE", "DRIFT_ALARM_STATE", "SAMPLE_SIZE"}.issubset(result.measurements)


def test_levene_detects_variance_shift() -> None:
    rng = np.random.default_rng(42)
    data = _frame(rng.normal(0, 1, 200), rng.normal(0, 5, 200))
    result = detect_levene_s_test(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 03:19"),
        current_window=("2026-01-02 00:00", "2026-01-02 03:19"),
    )
    assert result.p_value is not None
    assert result.p_value < 0.05
    assert result.drift_detected is True
    assert result.measurements["CURRENT_VARIANCE"] > result.measurements["REFERENCE_VARIANCE"]
    assert result.measurements["VARIANCE_RATIO"] > 1


def test_levene_mean_center_warns_about_outliers() -> None:
    rng = np.random.default_rng(43)
    data = _frame(rng.normal(0, 1, 80), rng.normal(0, 1, 80))
    result = detect_levene_s_test(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 01:19"),
        current_window=("2026-01-02 00:00", "2026-01-02 01:19"),
        params={"variant_id": "LEVENE_MEAN_CENTER"},
    )
    assert result.metadata["center"] == "mean"
    assert any("outliers" in warning for warning in result.warnings)


def test_levene_trimmed_variant_records_proportion() -> None:
    rng = np.random.default_rng(44)
    data = _frame(rng.normal(0, 1, 80), rng.normal(0, 2, 80))
    result = detect_levene_s_test(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 01:19"),
        current_window=("2026-01-02 00:00", "2026-01-02 01:19"),
        params={"variant_id": "TRIMMED_MEAN_LEVENE", "proportiontocut": 0.1},
    )
    assert result.metadata["center"] == "trimmed"
    assert result.metadata["proportiontocut"] == 0.1
    assert result.measurements["CENTER_POLICY"] == "trimmed"

    invalid = detect_levene_s_test(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 01:19"),
        current_window=("2026-01-02 00:00", "2026-01-02 01:19"),
        params={"variant_id": "TRIMMED_MEAN_LEVENE", "proportiontocut": 0.5},
    )
    assert invalid.severity == "not_applicable"


def test_levene_parameter_validation() -> None:
    data = _frame(np.arange(10, dtype=float), np.arange(10, dtype=float) + 1)
    bad_alpha = detect_levene_s_test(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:09"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:09"),
        params={"alpha": 2},
    )
    assert bad_alpha.severity == "not_applicable"

    one_sided = detect_levene_s_test(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:09"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:09"),
        params={"alternative": "greater"},
    )
    assert one_sided.severity == "not_applicable"

    contradictory = detect_levene_s_test(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:09"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:09"),
        params={"variant_id": "LEVENE_MEAN_CENTER", "center": "median"},
    )
    assert contradictory.severity == "not_applicable"


def test_levene_schema_and_window_validation() -> None:
    data = _frame(np.arange(3, dtype=float), np.arange(3, dtype=float))
    missing_windows = detect_levene_s_test(data)
    assert missing_windows.severity == "not_applicable"

    too_small = detect_levene_s_test(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:01"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:01"),
    )
    assert too_small.severity == "not_applicable"

    constant = detect_levene_s_test(
        _frame(np.ones(20), np.ones(20)),
        reference_window=("2026-01-01 00:00", "2026-01-01 00:19"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:19"),
    )
    assert constant.severity == "not_applicable"

    bool_data = data.copy()
    bool_data["value"] = True
    bool_result = detect_levene_s_test(
        bool_data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:02"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:02"),
    )
    assert bool_result.severity == "not_applicable"


def test_levene_warning_behavior_for_invalid_rows_and_small_samples() -> None:
    data = _frame(np.arange(10, dtype=float), np.arange(10, dtype=float) * 2)
    data.loc[0, "value"] = np.nan
    result = detect_levene_s_test(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:09"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:09"),
        params={"small_sample_warning_threshold": 20},
    )
    assert any("dropped" in warning for warning in result.warnings)
    assert any("small effective sample" in warning for warning in result.warnings)
