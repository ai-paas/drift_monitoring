from __future__ import annotations

import numpy as np
import pandas as pd

from drift_algorithm.methods.streamingchangedetector import detect_seqdrift


def _frame(reference: np.ndarray, current: np.ndarray) -> pd.DataFrame:
    ref_time = pd.date_range("2026-01-01 00:00", periods=len(reference), freq="min")
    cur_time = pd.date_range("2026-01-02 00:00", periods=len(current), freq="min")
    return pd.DataFrame({"time": list(ref_time) + list(cur_time), "value": list(reference) + list(current)})


def test_seqdrift1_default_no_alarm_finite_replay() -> None:
    rng = np.random.default_rng(980)
    data = _frame(rng.normal(0.0, 0.04, 100), rng.normal(0.01, 0.04, 100))
    result = detect_seqdrift(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 01:39"),
        current_window=("2026-01-02 00:00", "2026-01-02 01:39"),
        params={"delta": 0.001, "block_size": 20, "value_min": -1.0, "value_max": 1.0},
    )
    assert result.variant_id == "SEQDRIFT1"
    assert result.p_value is None
    assert result.drift_detected is False
    assert result.severity == "normal"
    assert result.measurements["DRIFT_ALARM_STATE"] == "normal"
    assert result.measurements["SEQUENTIAL_BOUND"] == result.measurements["LAST_BOUND"]
    assert result.measurements["METHOD_POLICY"]["sampling_policy"] == "exact"
    assert result.measurements["CHECK_COUNT"] == 5


def test_seqdrift1_mean_shift_alarm() -> None:
    rng = np.random.default_rng(981)
    data = _frame(rng.normal(0.0, 0.03, 100), rng.normal(0.8, 0.03, 100))
    result = detect_seqdrift(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 01:39"),
        current_window=("2026-01-02 00:00", "2026-01-02 01:39"),
        params={"delta": 0.01, "block_size": 20, "value_min": -1.0, "value_max": 1.0},
    )
    assert result.drift_detected is True
    assert result.severity == "drift_detected"
    assert result.measurements["ALARM_COUNT"] > 0
    assert result.measurements["FIRST_ALARM_TIME"] is not None
    assert result.measurements["MAX_MARGIN"] > 0.0
    assert len(result.measurements["ALARM_EVENTS"]) <= 50


def test_seqdrift2_reservoir_policy_and_alias() -> None:
    rng = np.random.default_rng(982)
    data = _frame(rng.normal(0.0, 0.05, 160), rng.normal(0.5, 0.05, 80))
    result = detect_seqdrift(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 02:39"),
        current_window=("2026-01-02 00:00", "2026-01-02 01:19"),
        params={
            "variant_id": "SEQDRIFT2",
            "threshold_or_alpha": 0.02,
            "block_size": 20,
            "reservoir_size": 50,
            "random_seed": 123,
            "value_min": -1.0,
            "value_max": 1.0,
        },
    )
    assert result.variant_id == "SEQDRIFT2"
    assert result.threshold is not None
    assert result.measurements["METHOD_POLICY"]["sampling_policy"] == "reservoir"
    assert result.measurements["REFERENCE_SIZE_EFFECTIVE"] == 50
    assert result.measurements["DELTA"] == 0.02
    assert any("threshold_or_alpha" in warning for warning in result.warnings)
    assert any("reservoir" in warning for warning in result.warnings)


def test_seqdrift_validation_and_warnings() -> None:
    data = _frame(np.zeros(40), np.ones(40))
    conflict = detect_seqdrift(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:39"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:39"),
        params={"delta": 0.01, "threshold_or_alpha": 0.02},
    )
    assert conflict.severity == "not_applicable"

    labels = data.copy()
    labels["y_true"] = 1
    labels["y_pred"] = 1
    supervised = detect_seqdrift(
        labels,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:39"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:39"),
        params={"y_true": "y_true", "y_pred": "y_pred"},
    )
    assert supervised.severity == "not_applicable"

    warning_data = _frame(np.arange(40, dtype=float), np.arange(20, dtype=float) + 2)
    warning_data["time"] = warning_data["time"].astype(object)
    warning_data.loc[0, "value"] = np.nan
    warning_data.loc[1, "time"] = "not-a-time"
    result = detect_seqdrift(
        warning_data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:39"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:19"),
        params={
            "block_size": 20,
            "min_reference_size": 20,
            "min_current_size": 20,
            "sample_imbalance_warning_ratio": 1.5,
            "value_min": 0.0,
            "value_max": 50.0,
        },
    )
    assert result.severity in {"normal", "drift_detected"}
    assert any("dropped" in warning for warning in result.warnings)
    assert any("imbalanced" in warning for warning in result.warnings)


def test_seqdrift_non_scalar_requests() -> None:
    data = _frame(np.zeros(30), np.ones(30))
    feature_request = detect_seqdrift(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:29"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:29"),
        params={"feature_cols": ["a", "b"]},
    )
    assert feature_request.severity == "not_applicable"
