from __future__ import annotations

import numpy as np
import pandas as pd

from drift_algorithm.methods.streamingchangedetector import detect_page_hinkley_test


def _frame(reference: np.ndarray, current: np.ndarray) -> pd.DataFrame:
    ref_time = pd.date_range("2026-01-01 00:00", periods=len(reference), freq="min")
    cur_time = pd.date_range("2026-01-02 00:00", periods=len(current), freq="min")
    return pd.DataFrame({"time": list(ref_time) + list(cur_time), "value": list(reference) + list(current)})


def test_page_hinkley_default_no_alarm_finite_replay() -> None:
    rng = np.random.default_rng(920)
    data = _frame(rng.normal(0.0, 0.02, 60), rng.normal(0.0, 0.02, 60))
    result = detect_page_hinkley_test(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:59"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:59"),
        params={"threshold": 5.0, "delta": 0.001, "min_instances": 30},
    )
    assert result.variant_id == "PAGE_HINKLEY_INCREASE"
    assert result.p_value is None
    assert result.drift_detected is False
    assert result.severity == "normal"
    assert result.threshold == 5.0
    assert result.measurements["DRIFT_ALARM_STATE"] == "normal"
    assert result.measurements["PAGE_HINKLEY_STATISTIC"] == result.test_statistic
    assert result.measurements["PH_STATISTIC"] == result.measurements["PAGE_HINKLEY_STATISTIC"]
    assert result.measurements["DIRECTION"] == "increase"
    assert result.measurements["PROCESSED_COUNT"] == 120


def test_page_hinkley_increase_alarm() -> None:
    rng = np.random.default_rng(921)
    data = _frame(rng.normal(0.0, 0.02, 60), rng.normal(0.8, 0.02, 60))
    result = detect_page_hinkley_test(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:59"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:59"),
        params={"threshold": 2.0, "delta": 0.001, "min_instances": 30},
    )
    assert result.drift_detected is True
    assert result.severity == "drift_detected"
    assert result.drift_score is not None and result.drift_score > 2.0
    assert result.measurements["ALARM_COUNT"] > 0
    assert result.measurements["FIRST_ALARM_TIME"] is not None
    assert len(result.measurements["ALARM_EVENTS"]) <= 50


def test_page_hinkley_decrease_alarm() -> None:
    rng = np.random.default_rng(922)
    data = _frame(rng.normal(1.0, 0.02, 60), rng.normal(0.0, 0.02, 60))
    result = detect_page_hinkley_test(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:59"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:59"),
        params={"variant_id": "PAGE_HINKLEY_DECREASE", "threshold": 2.0, "delta": 0.001, "min_instances": 30},
    )
    assert result.variant_id == "PAGE_HINKLEY_DECREASE"
    assert result.measurements["DIRECTION"] == "decrease"
    assert result.drift_detected is True
    assert result.severity == "drift_detected"


def test_page_hinkley_alias_validation_alpha_and_reset_policy() -> None:
    data = _frame(np.zeros(40), np.ones(40))
    alias = detect_page_hinkley_test(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:39"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:39"),
        params={"threshold_or_alpha": 1.0, "alpha": 0.2, "record_events": False, "reset_policy": "none"},
    )
    assert alias.threshold == 1.0
    assert "ALARM_EVENTS" not in alias.measurements
    assert any("threshold_or_alpha" in warning for warning in alias.warnings)
    assert any("alpha is recorded" in warning for warning in alias.warnings)

    conflict = detect_page_hinkley_test(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:39"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:39"),
        params={"threshold": 1.0, "threshold_or_alpha": 2.0},
    )
    assert conflict.severity == "not_applicable"

    wrong_direction = detect_page_hinkley_test(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:39"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:39"),
        params={"variant_id": "PAGE_HINKLEY_DECREASE", "direction": "increase"},
    )
    assert wrong_direction.severity == "not_applicable"


def test_page_hinkley_schema_window_warning_and_deferred_requests() -> None:
    bool_data = _frame(np.ones(30), np.ones(30))
    bool_data["value"] = True
    bool_result = detect_page_hinkley_test(
        bool_data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:29"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:29"),
    )
    assert bool_result.severity == "not_applicable"

    small = detect_page_hinkley_test(
        _frame(np.arange(10, dtype=float), np.arange(10, dtype=float)),
        reference_window=("2026-01-01 00:00", "2026-01-01 00:09"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:09"),
        params={"min_instances": 30},
    )
    assert small.severity == "not_applicable"

    deferred = detect_page_hinkley_test(
        _frame(np.zeros(30), np.ones(30)),
        reference_window=("2026-01-01 00:00", "2026-01-01 00:29"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:29"),
        params={"variant_id": "DRIFT_RETRAINING_WITH_PAGE_HINKLEY"},
    )
    assert deferred.severity == "not_applicable"

    warning_data = _frame(np.arange(40, dtype=float), np.arange(20, dtype=float) + 2)
    warning_data["time"] = warning_data["time"].astype(object)
    warning_data.loc[0, "value"] = np.nan
    warning_data.loc[1, "time"] = "not-a-time"
    result = detect_page_hinkley_test(
        warning_data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:39"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:19"),
        params={
            "threshold": 10.0,
            "min_reference_size": 20,
            "min_current_size": 20,
            "sample_imbalance_warning_ratio": 1.5,
            "check_every": 2,
        },
    )
    assert result.severity in {"normal", "drift_detected"}
    assert any("dropped" in warning for warning in result.warnings)
    assert any("imbalanced" in warning for warning in result.warnings)
    assert any("check_every > 1" in warning for warning in result.warnings)


def test_page_hinkley_non_scalar_requests() -> None:
    data = _frame(np.zeros(30), np.ones(30))
    feature_request = detect_page_hinkley_test(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:29"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:29"),
        params={"feature_cols": ["a", "b"]},
    )
    assert feature_request.severity == "not_applicable"
