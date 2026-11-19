from __future__ import annotations

import numpy as np
import pandas as pd

from drift_algorithm.methods.streamingchangedetector import detect_cusum


def _frame(reference: np.ndarray, current: np.ndarray) -> pd.DataFrame:
    ref_time = pd.date_range("2026-01-01 00:00", periods=len(reference), freq="min")
    cur_time = pd.date_range("2026-01-02 00:00", periods=len(current), freq="min")
    return pd.DataFrame({"time": list(ref_time) + list(cur_time), "value": list(reference) + list(current)})


def test_cusum_default_no_alarm_finite_replay() -> None:
    rng = np.random.default_rng(930)
    data = _frame(rng.normal(0.0, 0.02, 60), rng.normal(0.0, 0.02, 60))
    result = detect_cusum(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:59"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:59"),
        params={"target_mean": 0.0, "allowance_k": 0.05, "decision_threshold_h": 3.0, "warmup_size": 30},
    )
    assert result.variant_id == "ONE_SIDED_UPPER_CUSUM"
    assert result.p_value is None
    assert result.drift_detected is False
    assert result.severity == "normal"
    assert result.threshold == 3.0
    assert result.measurements["DRIFT_ALARM_STATE"] == "normal"
    assert result.measurements["CUSUM_STATISTIC"] == result.test_statistic
    assert result.measurements["DIRECTION"] == "increase"
    assert result.measurements["PROCESSED_COUNT"] == 120


def test_cusum_upper_alarm() -> None:
    rng = np.random.default_rng(931)
    data = _frame(rng.normal(0.0, 0.02, 60), rng.normal(0.5, 0.02, 60))
    result = detect_cusum(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:59"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:59"),
        params={"target_mean": 0.0, "allowance_k": 0.01, "decision_threshold_h": 2.0, "warmup_size": 30},
    )
    assert result.drift_detected is True
    assert result.severity == "drift_detected"
    assert result.drift_score is not None and result.drift_score > 2.0
    assert result.measurements["ALARM_COUNT"] > 0
    assert result.measurements["FIRST_ALARM_DIRECTION"] == "upper"
    assert len(result.measurements["ALARM_EVENTS"]) <= 50


def test_cusum_lower_and_two_sided_alarm() -> None:
    rng = np.random.default_rng(932)
    data = _frame(rng.normal(1.0, 0.02, 60), rng.normal(0.2, 0.02, 60))
    lower = detect_cusum(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:59"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:59"),
        params={
            "variant_id": "ONE_SIDED_LOWER_CUSUM",
            "target_mean": 1.0,
            "allowance_k": 0.01,
            "decision_threshold_h": 2.0,
            "warmup_size": 30,
        },
    )
    assert lower.measurements["DIRECTION"] == "decrease"
    assert lower.drift_detected is True
    assert lower.measurements["FIRST_ALARM_DIRECTION"] == "lower"

    two_sided = detect_cusum(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:59"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:59"),
        params={
            "variant_id": "TWO_SIDED_CUSUM",
            "target_mean": 1.0,
            "allowance_k": 0.01,
            "decision_threshold_h": 2.0,
            "warmup_size": 30,
        },
    )
    assert two_sided.measurements["DIRECTION"] == "both"
    assert two_sided.drift_detected is True
    assert two_sided.measurements["FIRST_ALARM_DIRECTION"] == "lower"


def test_cusum_alias_inferred_calibration_and_validation() -> None:
    data = _frame(np.zeros(40), np.ones(40))
    inferred = detect_cusum(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:39"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:39"),
        params={"threshold_or_alpha": 1.0, "allowance_k": 0.0, "record_events": False},
    )
    assert inferred.threshold == 1.0
    assert "ALARM_EVENTS" not in inferred.measurements
    assert inferred.measurements["TARGET_MEAN"] == 0.0
    assert any("target_mean was inferred" in warning for warning in inferred.warnings)
    assert any("threshold alias" in warning for warning in inferred.warnings)

    conflict = detect_cusum(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:39"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:39"),
        params={"decision_threshold_h": 1.0, "threshold_or_alpha": 2.0},
    )
    assert conflict.severity == "not_applicable"

    wrong_direction = detect_cusum(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:39"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:39"),
        params={"variant_id": "ONE_SIDED_LOWER_CUSUM", "direction": "increase"},
    )
    assert wrong_direction.severity == "not_applicable"


def test_cusum_schema_window_warning_and_deferred_requests() -> None:
    bool_data = _frame(np.ones(30), np.ones(30))
    bool_data["value"] = True
    bool_result = detect_cusum(
        bool_data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:29"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:29"),
    )
    assert bool_result.severity == "not_applicable"

    small = detect_cusum(
        _frame(np.arange(10, dtype=float), np.arange(10, dtype=float)),
        reference_window=("2026-01-01 00:00", "2026-01-01 00:09"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:09"),
        params={"warmup_size": 30},
    )
    assert small.severity == "not_applicable"

    distance_stream = detect_cusum(
        _frame(np.zeros(30), np.ones(30)),
        reference_window=("2026-01-01 00:00", "2026-01-01 00:29"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:29"),
        params={
            "variant_id": "CUSUM_ON_DISTANCE_STREAM",
            "target_mean": 0.0,
            "allowance_k": 0.0,
            "decision_threshold_h": 1.0,
            "warmup_size": 1,
        },
    )
    assert distance_stream.drift_detected is True
    assert distance_stream.measurements["DIRECTION"] == "increase"

    warning_data = _frame(np.arange(40, dtype=float), np.arange(20, dtype=float) + 2)
    warning_data["time"] = warning_data["time"].astype(object)
    warning_data.loc[0, "value"] = np.nan
    warning_data.loc[1, "time"] = "not-a-time"
    result = detect_cusum(
        warning_data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:39"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:19"),
        params={
            "decision_threshold_h": 100.0,
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


def test_cusum_non_scalar_requests() -> None:
    data = _frame(np.zeros(30), np.ones(30))
    feature_request = detect_cusum(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:29"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:29"),
        params={"feature_cols": ["a", "b"]},
    )
    assert feature_request.severity == "not_applicable"
