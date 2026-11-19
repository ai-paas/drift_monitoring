from __future__ import annotations

import numpy as np
import pandas as pd

from drift_algorithm.methods.supervisedconceptdriftdetector import detect_hddm_a


def _error_frame(reference: np.ndarray, current: np.ndarray) -> pd.DataFrame:
    ref_time = pd.date_range("2026-01-01 00:00", periods=len(reference), freq="min")
    cur_time = pd.date_range("2026-01-02 00:00", periods=len(current), freq="min")
    return pd.DataFrame({"time": list(ref_time) + list(cur_time), "error": list(reference) + list(current)})


def test_hddm_a_hoeffding_bound_no_alarm() -> None:
    reference = np.zeros(200)
    current = np.zeros(200)
    reference[::10] = 1
    current[::10] = 1
    data = _error_frame(reference, current)
    result = detect_hddm_a(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 03:19"),
        current_window=("2026-01-02 00:00", "2026-01-02 03:19"),
        params={"error_col": "error", "min_instances": 30},
    )
    assert result.variant_id == "HDDM_A_HOEFFDING_BOUND"
    assert result.p_value is None
    assert result.drift_detected is False
    assert result.severity == "normal"
    assert result.measurements["DRIFT_ALARM_STATE"] == "normal"
    assert result.measurements["WARNING_STATE"] is False
    assert result.measurements["REFERENCE_ERROR_RATE"] == 0.1
    assert result.measurements["CURRENT_ERROR_RATE"] == 0.1


def test_hddm_a_warning_drift_alarm() -> None:
    reference = np.zeros(200)
    reference[::20] = 1
    current = np.r_[np.zeros(50), np.ones(150)]
    data = _error_frame(reference, current)
    result = detect_hddm_a(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 03:19"),
        current_window=("2026-01-02 00:00", "2026-01-02 03:19"),
        params={"variant_id": "HDDM_A_WARNING_DRIFT", "error_col": "error", "min_instances": 30},
    )
    assert result.variant_id == "HDDM_A_WARNING_DRIFT"
    assert result.drift_detected is True
    assert result.severity == "drift_detected"
    assert result.measurements["DRIFT_ALARM_STATE"] == "drift_detected"
    assert result.measurements["TEST_STATISTIC"] >= result.measurements["HOEFFDING_DRIFT_BOUND"]
    assert result.measurements["CHANGE_DIRECTION"] == "increase"
    assert result.measurements["HDDM_A_EVENTS"]


def test_hddm_a_two_sided_decrease_from_labels() -> None:
    reference_true = np.ones(200, dtype=int)
    reference_pred = np.zeros(200, dtype=int)
    reference_pred[::5] = 1
    current_true = np.ones(200, dtype=int)
    current_pred = current_true.copy()
    current_pred[::20] = 0
    ref_time = pd.date_range("2026-01-01 00:00", periods=200, freq="min")
    cur_time = pd.date_range("2026-01-02 00:00", periods=200, freq="min")
    data = pd.DataFrame(
        {
            "time": list(ref_time) + list(cur_time),
            "y_true": list(reference_true) + list(current_true),
            "y_pred": list(reference_pred) + list(current_pred),
        }
    )
    result = detect_hddm_a(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 03:19"),
        current_window=("2026-01-02 00:00", "2026-01-02 03:19"),
        params={
            "variant_id": "HDDM_A_TWO_SIDED",
            "y_true": "y_true",
            "y_pred": "y_pred",
            "min_instances": 30,
        },
    )
    assert result.variant_id == "HDDM_A_TWO_SIDED"
    assert result.drift_detected is True
    assert result.measurements["CHANGE_DIRECTION"] == "decrease"
    assert result.measurements["P_VALUE"] is None


def test_hddm_a_validation_and_warnings() -> None:
    data = _error_frame(np.zeros(40), np.ones(40))
    invalid_confidence = detect_hddm_a(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:39"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:39"),
        params={"error_col": "error", "drift_confidence": 1.0},
    )
    assert invalid_confidence.severity == "not_applicable"

    invalid_error = data.copy()
    invalid_error.loc[0, "error"] = 2
    invalid_result = detect_hddm_a(
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
    result = detect_hddm_a(
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


def test_hddm_a_non_scalar_requests() -> None:
    data = _error_frame(np.zeros(30), np.ones(30))
    feature_request = detect_hddm_a(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:29"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:29"),
        params={"feature_cols": ["a", "b"]},
    )
    assert feature_request.severity == "not_applicable"
