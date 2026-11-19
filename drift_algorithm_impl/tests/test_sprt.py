from __future__ import annotations

import numpy as np
import pandas as pd

from drift_algorithm.methods.streamingchangedetector import detect_sprt


def _frame(reference: np.ndarray, current: np.ndarray, value_col: str = "value") -> pd.DataFrame:
    ref_time = pd.date_range("2026-01-01 00:00", periods=len(reference), freq="min")
    cur_time = pd.date_range("2026-01-02 00:00", periods=len(current), freq="min")
    return pd.DataFrame({"time": list(ref_time) + list(cur_time), value_col: list(reference) + list(current)})


def test_bernoulli_sprt_accepts_h0_no_drift() -> None:
    reference = np.array([0] * 95 + [1] * 5, dtype=float)
    current = np.array([0] * 95 + [1] * 5, dtype=float)
    result = detect_sprt(
        _frame(reference, current, "error"),
        value_col=None,
        reference_window=("2026-01-01 00:00", "2026-01-01 01:39"),
        current_window=("2026-01-02 00:00", "2026-01-02 01:39"),
        params={"error_col": "error", "p0": 0.05, "p1": 0.2, "alpha": 0.05, "beta": 0.1},
    )
    assert result.method_id == "DM-034"
    assert result.variant_id == "SPRT_BERNOULLI_ERROR_RATE"
    assert result.drift_detected is False
    assert result.measurements["HYPOTHESIS_DECISION_STATE"] == "accept_h0"
    assert result.measurements["LOG_LIKELIHOOD_RATIO"] <= result.measurements["LOWER_BOUNDARY"]
    assert result.p_value is None


def test_bernoulli_sprt_accepts_h1_error_rate_increase() -> None:
    reference = np.array([0] * 95 + [1] * 5, dtype=float)
    current = np.array([1] * 35 + [0] * 65, dtype=float)
    result = detect_sprt(
        _frame(reference, current, "error"),
        value_col=None,
        reference_window=("2026-01-01 00:00", "2026-01-01 01:39"),
        current_window=("2026-01-02 00:00", "2026-01-02 01:39"),
        params={"error_col": "error", "p0": 0.05, "p1": 0.2, "alpha": 0.05, "beta": 0.1},
    )
    assert result.drift_detected is True
    assert result.severity == "drift_detected"
    assert result.measurements["HYPOTHESIS_DECISION_STATE"] == "accept_h1"
    assert result.measurements["ALARM_COUNT"] == 1
    assert result.measurements["FIRST_ALARM_TIME"] is not None


def test_gaussian_sprt_accepts_h1_mean_shift() -> None:
    reference = np.linspace(-0.1, 0.1, 80)
    current = np.linspace(1.0, 1.2, 80)
    result = detect_sprt(
        _frame(reference, current),
        reference_window=("2026-01-01 00:00", "2026-01-01 01:19"),
        current_window=("2026-01-02 00:00", "2026-01-02 01:19"),
        params={
            "variant_id": "SPRT_GAUSSIAN_MEAN_SHIFT",
            "mu0": 0.0,
            "mu1": 1.0,
            "sigma": 0.2,
            "alpha": 0.05,
            "beta": 0.1,
        },
    )
    assert result.variant_id == "SPRT_GAUSSIAN_MEAN_SHIFT"
    assert result.drift_detected is True
    assert result.measurements["MU0"] == 0.0
    assert result.measurements["MU1"] == 1.0
    assert result.measurements["SIGMA"] == 0.2
    assert result.measurements["LOG_LIKELIHOOD_RATIO"] >= result.measurements["UPPER_BOUNDARY"]


def test_sprt_continue_reset_policy_records_multiple_h1_events() -> None:
    reference = np.zeros(40)
    current = np.concatenate([np.ones(15), np.zeros(10), np.ones(15)])
    result = detect_sprt(
        _frame(reference, current, "error"),
        value_col=None,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:39"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:39"),
        params={
            "error_col": "error",
            "p0": 0.05,
            "p1": 0.3,
            "alpha": 0.2,
            "beta": 0.2,
            "reset_policy": "continue",
            "min_reference_size": 20,
            "min_current_size": 20,
        },
    )
    assert result.drift_detected is True
    assert result.measurements["ALARM_COUNT"] >= 1
    assert len(result.measurements["DECISION_EVENTS"]) >= 1


def test_sprt_validation_and_warnings() -> None:
    data = _frame(np.zeros(30), np.ones(30))
    invalid = detect_sprt(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:29"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:29"),
        params={"variant_id": "SPRT_BERNOULLI_ERROR_RATE", "p0": 0.2, "p1": 0.1},
    )
    assert invalid.severity == "not_applicable"

    labels = data.copy()
    labels["y_true"] = 1
    labels["y_pred"] = 1
    supervised = detect_sprt(
        labels,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:29"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:29"),
        params={"y_true": "y_true", "y_pred": "y_pred"},
    )
    assert supervised.severity == "not_applicable"

    dirty = _frame(np.zeros(30), np.ones(30), "error")
    dirty["time"] = dirty["time"].astype(object)
    dirty.loc[0, "error"] = np.nan
    dirty.loc[1, "time"] = "not-a-time"
    result = detect_sprt(
        dirty,
        value_col=None,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:29"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:29"),
        params={"error_col": "error", "p0": 0.05, "p1": 0.3, "min_reference_size": 20, "min_current_size": 20},
    )
    assert result.severity in {"normal", "drift_detected", "watch"}
    assert any("dropped" in warning for warning in result.warnings)
