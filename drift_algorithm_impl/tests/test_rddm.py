from __future__ import annotations

import numpy as np
import pandas as pd

from drift_algorithm.methods.supervisedconceptdriftdetector import detect_rddm


def _error_frame(reference: np.ndarray, current: np.ndarray) -> pd.DataFrame:
    ref_time = pd.date_range("2026-01-01 00:00", periods=len(reference), freq="min")
    cur_time = pd.date_range("2026-01-02 00:00", periods=len(current), freq="min")
    return pd.DataFrame({"time": list(ref_time) + list(cur_time), "error": list(reference) + list(current)})


def test_rddm_standard_no_alarm_error_stream() -> None:
    reference = np.zeros(100)
    current = np.zeros(100)
    reference[::10] = 1
    current[::10] = 1
    data = _error_frame(reference, current)
    result = detect_rddm(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 01:39"),
        current_window=("2026-01-02 00:00", "2026-01-02 01:39"),
        params={"error_col": "error", "min_num_instances": 30, "min_concept_size": 30},
    )
    assert result.variant_id == "RDDM_STANDARD"
    assert result.p_value is None
    assert result.drift_detected is False
    assert result.severity == "normal"
    assert result.measurements["DRIFT_ALARM_STATE"] == "normal"
    assert result.measurements["WARNING_STATE"] is False
    assert result.measurements["WINDOW_SIZE"] > 0
    assert result.measurements["REFERENCE_ERROR_RATE"] == 0.1
    assert result.measurements["CURRENT_ERROR_RATE"] == 0.1


def test_rddm_standard_drift_and_retained_window() -> None:
    reference = np.zeros(100)
    reference[::20] = 1
    current = np.r_[np.zeros(60), np.ones(40)]
    data = _error_frame(reference, current)
    result = detect_rddm(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 01:39"),
        current_window=("2026-01-02 00:00", "2026-01-02 01:39"),
        params={"error_col": "error", "min_num_instances": 30, "min_concept_size": 30},
    )
    assert result.drift_detected is True
    assert result.severity == "drift_detected"
    assert result.measurements["DRIFT_ALARM_STATE"] == "drift_detected"
    assert result.measurements["RETAINED_WINDOW_SIZE"] > 0
    assert result.measurements["ADAPTATION_EVENT"] == "drift_alarm_no_reset"
    assert result.measurements["RDDM_EVENTS"]


def test_rddm_reactive_reset_from_labels() -> None:
    reference_true = np.ones(100, dtype=int)
    reference_pred = reference_true.copy()
    reference_pred[::20] = 0
    current_true = np.ones(110, dtype=int)
    current_pred = current_true.copy()
    current_pred[60:95] = 0
    ref_time = pd.date_range("2026-01-01 00:00", periods=100, freq="min")
    cur_time = pd.date_range("2026-01-02 00:00", periods=110, freq="min")
    data = pd.DataFrame(
        {
            "time": list(ref_time) + list(cur_time),
            "y_true": list(reference_true) + list(current_true),
            "y_pred": list(reference_pred) + list(current_pred),
        }
    )
    result = detect_rddm(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 01:39"),
        current_window=("2026-01-02 00:00", "2026-01-02 01:49"),
        params={
            "variant_id": "RDDM_REACTIVE_RESET",
            "y_true": "y_true",
            "y_pred": "y_pred",
            "min_num_instances": 30,
            "min_concept_size": 30,
            "max_concept_size": 120,
        },
    )
    assert result.variant_id == "RDDM_REACTIVE_RESET"
    assert result.drift_detected is True
    assert result.measurements["ADAPTATION_EVENT"] == "reactive_reset"
    assert result.measurements["RESET_EVENT"] is not None
    assert result.measurements["POST_RESET_ERROR_RATE"] is not None


def test_rddm_validation_and_warnings() -> None:
    data = _error_frame(np.zeros(40), np.ones(40))
    invalid_policy = detect_rddm(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:39"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:39"),
        params={"error_col": "error", "reset_policy": "reactive"},
    )
    assert invalid_policy.severity == "not_applicable"

    invalid_error = data.copy()
    invalid_error.loc[0, "error"] = 2
    invalid_result = detect_rddm(
        invalid_error,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:39"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:39"),
        params={"error_col": "error"},
    )
    assert invalid_result.severity == "not_applicable"

    warning_data = _error_frame(np.zeros(40), np.r_[np.zeros(20), np.ones(20)])
    warning_data["time"] = warning_data["time"].astype(object)
    warning_data.loc[0, "error"] = np.nan
    warning_data.loc[1, "time"] = "not-a-time"
    result = detect_rddm(
        warning_data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:39"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:39"),
        params={
            "error_col": "error",
            "min_reference_size": 20,
            "min_current_size": 20,
            "sample_imbalance_warning_ratio": 1.5,
        },
    )
    assert result.severity in {"normal", "warning", "drift_detected"}
    assert any("dropped" in warning for warning in result.warnings)


def test_rddm_non_scalar_requests() -> None:
    data = _error_frame(np.zeros(30), np.ones(30))
    feature_request = detect_rddm(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:29"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:29"),
        params={"feature_cols": ["a", "b"]},
    )
    assert feature_request.severity == "not_applicable"
