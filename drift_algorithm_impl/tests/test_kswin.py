from __future__ import annotations

import numpy as np
import pandas as pd

from drift_algorithm.methods.streamingchangedetector import detect_kswin


def _frame(reference: np.ndarray, current: np.ndarray) -> pd.DataFrame:
    ref_time = pd.date_range("2026-01-01 00:00", periods=len(reference), freq="min")
    cur_time = pd.date_range("2026-01-02 00:00", periods=len(current), freq="min")
    return pd.DataFrame({"time": list(ref_time) + list(cur_time), "value": list(reference) + list(current)})


def test_kswin_default_no_alarm_finite_replay() -> None:
    rng = np.random.default_rng(910)
    data = _frame(rng.normal(0, 1, 80), rng.normal(0, 1, 80))
    result = detect_kswin(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 01:19"),
        current_window=("2026-01-02 00:00", "2026-01-02 01:19"),
        params={"alpha": 0.0001, "window_size": 60, "stat_size": 20},
    )
    assert result.variant_id == "KSWIN_STANDARD"
    assert result.drift_detected is False
    assert result.severity == "normal"
    assert result.p_value is not None
    assert result.threshold == 0.0001
    assert result.measurements["DRIFT_ALARM_STATE"] == "normal"
    assert result.measurements["TEST_STATISTIC"] == result.test_statistic
    assert result.measurements["P_VALUE"] == result.p_value
    assert result.measurements["WINDOW_SIZE"] == 60
    assert result.measurements["STAT_SIZE"] == 20
    assert result.measurements["CHECK_COUNT"] > 0
    assert result.measurements["PROCESSED_COUNT"] == 160


def test_kswin_distribution_shift_alarm() -> None:
    rng = np.random.default_rng(911)
    data = _frame(rng.normal(0, 0.2, 80), rng.normal(2.0, 0.2, 80))
    result = detect_kswin(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 01:19"),
        current_window=("2026-01-02 00:00", "2026-01-02 01:19"),
        params={"alpha": 0.01, "window_size": 60, "stat_size": 20},
    )
    assert result.drift_detected is True
    assert result.severity == "drift_detected"
    assert result.p_value is not None and result.p_value < 0.01
    assert result.measurements["ALARM_COUNT"] > 0
    assert result.measurements["FIRST_ALARM_TIME"] is not None
    assert result.measurements["LAST_ALARM_INDEX"] is not None
    assert len(result.measurements["ALARM_EVENTS"]) <= 50


def test_kswin_variant_alias_subsampling_and_parameter_validation() -> None:
    data = _frame(np.zeros(60), np.ones(60))
    alias = detect_kswin(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:59"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:59"),
        params={"variant_id": "KSWIN_NUMERIC_STREAM", "threshold_or_alpha": 0.01, "window_size": 50, "stat_size": 15},
    )
    assert alias.variant_id == "KSWIN_NUMERIC_STREAM"
    assert alias.threshold == 0.01
    assert any("threshold_or_alpha" in warning for warning in alias.warnings)

    subsampled = detect_kswin(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:59"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:59"),
        params={
            "variant_id": "KSWIN_WITH_SUBSAMPLING",
            "alpha": 0.01,
            "window_size": 50,
            "stat_size": 15,
            "subsample_size": 80,
        },
    )
    assert subsampled.variant_id == "KSWIN_WITH_SUBSAMPLING"
    assert subsampled.severity in {"normal", "drift_detected"}
    assert subsampled.measurements["SAMPLING_POLICY"] == "deterministic_even_index"
    assert subsampled.measurements["SUBSAMPLE_SIZE"] == 80

    conflict = detect_kswin(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:59"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:59"),
        params={"alpha": 0.01, "threshold_or_alpha": 0.02},
    )
    assert conflict.severity == "not_applicable"

    invalid = detect_kswin(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:59"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:59"),
        params={"window_size": 10, "stat_size": 10},
    )
    assert invalid.severity == "not_applicable"


def test_kswin_schema_window_warning_and_event_policy() -> None:
    bool_data = _frame(np.ones(30), np.ones(30))
    bool_data["value"] = True
    bool_result = detect_kswin(
        bool_data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:29"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:29"),
    )
    assert bool_result.severity == "not_applicable"

    small = detect_kswin(
        _frame(np.arange(10, dtype=float), np.arange(10, dtype=float)),
        reference_window=("2026-01-01 00:00", "2026-01-01 00:09"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:09"),
        params={"window_size": 30},
    )
    assert small.severity == "not_applicable"

    warning_data = _frame(np.repeat(np.arange(40, dtype=float), 2), np.arange(20, dtype=float) + 2)
    warning_data["time"] = warning_data["time"].astype(object)
    warning_data.loc[0, "value"] = np.nan
    warning_data.loc[1, "time"] = "not-a-time"
    result = detect_kswin(
        warning_data,
        reference_window=("2026-01-01 00:00", "2026-01-01 01:19"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:19"),
        params={
            "window_size": 50,
            "stat_size": 15,
            "check_every": 2,
            "record_events": False,
            "min_reference_size": 20,
            "min_current_size": 20,
            "sample_imbalance_warning_ratio": 2.0,
            "multiple_testing_correction": "bonferroni",
        },
    )
    assert result.severity in {"normal", "drift_detected"}
    assert "ALARM_EVENTS" not in result.measurements
    assert any("dropped" in warning for warning in result.warnings)
    assert any("repeated" in warning or "tied" in warning for warning in result.warnings)
    assert any("imbalanced" in warning for warning in result.warnings)
    assert any("check_every > 1" in warning for warning in result.warnings)
    assert any("multiple_testing_correction" in warning for warning in result.warnings)


def test_kswin_non_scalar_requests() -> None:
    data = _frame(np.zeros(60), np.ones(60))
    feature_request = detect_kswin(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:59"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:59"),
        params={"feature_cols": ["a", "b"]},
    )
    assert feature_request.severity == "not_applicable"
