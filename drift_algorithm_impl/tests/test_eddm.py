from __future__ import annotations

import numpy as np
import pandas as pd

from drift_algorithm.methods.supervisedconceptdriftdetector import detect_eddm


def _error_frame(reference: np.ndarray, current: np.ndarray) -> pd.DataFrame:
    ref_time = pd.date_range("2026-01-01 00:00", periods=len(reference), freq="min")
    cur_time = pd.date_range("2026-01-02 00:00", periods=len(current), freq="min")
    return pd.DataFrame({"time": list(ref_time) + list(cur_time), "error": list(reference) + list(current)})


def test_eddm_distance_between_errors_no_alarm() -> None:
    reference = np.zeros(300)
    current = np.zeros(300)
    reference[::10] = 1
    current[::10] = 1
    data = _error_frame(reference, current)
    result = detect_eddm(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 04:59"),
        current_window=("2026-01-02 00:00", "2026-01-02 04:59"),
        params={"error_col": "error", "min_num_errors": 30},
    )
    assert result.variant_id == "EDDM_DISTANCE_BETWEEN_ERRORS"
    assert result.p_value is None
    assert result.drift_detected is False
    assert result.severity == "normal"
    assert result.measurements["DRIFT_ALARM_STATE"] == "normal"
    assert result.measurements["WARNING_STATE"] is False
    assert result.measurements["ERROR_COUNT"] == 60
    assert result.measurements["EDDM_SCORE_RATIO"] == 1.0


def test_eddm_warning_drift_alarm_from_error_stream() -> None:
    reference = np.zeros(300)
    reference[::20] = 1
    current = np.zeros(300)
    current[::4] = 1
    data = _error_frame(reference, current)
    result = detect_eddm(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 04:59"),
        current_window=("2026-01-02 00:00", "2026-01-02 04:59"),
        params={"variant_id": "EDDM_WARNING_DRIFT", "error_col": "error", "min_num_errors": 20},
    )
    assert result.variant_id == "EDDM_WARNING_DRIFT"
    assert result.drift_detected is True
    assert result.severity == "drift_detected"
    assert result.measurements["DRIFT_ALARM_STATE"] == "drift_detected"
    assert result.measurements["EDDM_SCORE_RATIO"] < result.measurements["DRIFT_THRESHOLD"]
    assert result.measurements["EDDM_EVENTS"]


def test_eddm_gradual_drift_from_labels() -> None:
    reference_true = np.ones(300, dtype=int)
    reference_pred = reference_true.copy()
    reference_pred[::20] = 0
    current_true = np.ones(300, dtype=int)
    current_pred = current_true.copy()
    current_pred[::5] = 0
    ref_time = pd.date_range("2026-01-01 00:00", periods=300, freq="min")
    cur_time = pd.date_range("2026-01-02 00:00", periods=300, freq="min")
    data = pd.DataFrame(
        {
            "time": list(ref_time) + list(cur_time),
            "y_true": list(reference_true) + list(current_true),
            "y_pred": list(reference_pred) + list(current_pred),
        }
    )
    result = detect_eddm(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 04:59"),
        current_window=("2026-01-02 00:00", "2026-01-02 04:59"),
        params={
            "variant_id": "EDDM_GRADUAL_DRIFT",
            "y_true": "y_true",
            "y_pred": "y_pred",
            "min_num_errors": 20,
        },
    )
    assert result.variant_id == "EDDM_GRADUAL_DRIFT"
    assert result.drift_detected is True
    assert result.measurements["GRADUAL_DRIFT_STATE"] == "gradual_drift_candidate"
    assert result.measurements["P_VALUE"] is None


def test_eddm_validation_and_warnings() -> None:
    data = _error_frame(np.zeros(40), np.ones(40))
    invalid_metric = detect_eddm(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:39"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:39"),
        params={"error_col": "error", "error_distance_metric": "time_gap"},
    )
    assert invalid_metric.severity == "not_applicable"

    invalid_error = data.copy()
    invalid_error.loc[0, "error"] = 2
    invalid_result = detect_eddm(
        invalid_error,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:39"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:39"),
        params={"error_col": "error"},
    )
    assert invalid_result.severity == "not_applicable"

    warning_data = _error_frame(np.r_[np.ones(30), np.zeros(20)], np.r_[np.ones(30), np.zeros(20)])
    warning_data["time"] = warning_data["time"].astype(object)
    warning_data.loc[0, "error"] = np.nan
    warning_data.loc[1, "time"] = "not-a-time"
    result = detect_eddm(
        warning_data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:49"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:49"),
        params={
            "error_col": "error",
            "min_reference_size": 20,
            "min_current_size": 20,
            "min_num_errors": 30,
            "sample_imbalance_warning_ratio": 1.5,
        },
    )
    assert result.severity in {"normal", "warning", "drift_detected"}
    assert any("dropped" in warning for warning in result.warnings)


def test_eddm_non_scalar_requests() -> None:
    data = _error_frame(np.ones(30), np.ones(30))
    feature_request = detect_eddm(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:29"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:29"),
        params={"feature_cols": ["a", "b"]},
    )
    assert feature_request.severity == "not_applicable"
