from __future__ import annotations

import numpy as np
import pandas as pd

from drift_algorithm.methods.supervisedconceptdriftdetector import detect_ddm


def _error_frame(reference: np.ndarray, current: np.ndarray) -> pd.DataFrame:
    ref_time = pd.date_range("2026-01-01 00:00", periods=len(reference), freq="min")
    cur_time = pd.date_range("2026-01-02 00:00", periods=len(current), freq="min")
    return pd.DataFrame({"time": list(ref_time) + list(cur_time), "error": list(reference) + list(current)})


def test_ddm_standard_no_alarm_error_stream() -> None:
    reference = np.zeros(100)
    current = np.zeros(100)
    reference[::10] = 1
    current[::10] = 1
    data = _error_frame(reference, current)
    result = detect_ddm(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 01:39"),
        current_window=("2026-01-02 00:00", "2026-01-02 01:39"),
        params={"error_col": "error", "min_num_instances": 30},
    )
    assert result.variant_id == "DDM_STANDARD"
    assert result.p_value is None
    assert result.drift_detected is False
    assert result.severity == "normal"
    assert result.measurements["DRIFT_ALARM_STATE"] == "normal"
    assert result.measurements["WARNING_STATE"] is False
    assert result.measurements["DDM_STATISTIC"] == result.test_statistic
    assert result.measurements["REFERENCE_ERROR_RATE"] == 0.1
    assert result.measurements["CURRENT_ERROR_RATE"] == 0.1


def test_ddm_standard_drift_from_error_stream() -> None:
    reference = np.r_[np.zeros(95), np.ones(5)]
    current = np.r_[np.zeros(60), np.ones(40)]
    data = _error_frame(reference, current)
    result = detect_ddm(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 01:39"),
        current_window=("2026-01-02 00:00", "2026-01-02 01:39"),
        params={"error_col": "error", "min_num_instances": 30},
    )
    assert result.drift_detected is True
    assert result.severity == "drift_detected"
    assert result.measurements["DRIFT_ALARM_STATE"] == "drift_detected"
    assert result.measurements["DRIFT_TIME"] is not None
    assert result.measurements["DDM_EVENTS"]


def test_ddm_warning_buffer_from_labels() -> None:
    reference_true = np.ones(100, dtype=int)
    reference_pred = reference_true.copy()
    reference_pred[-5:] = 0
    current_true = np.ones(100, dtype=int)
    current_pred = current_true.copy()
    current_pred[65:] = 0
    ref_time = pd.date_range("2026-01-01 00:00", periods=100, freq="min")
    cur_time = pd.date_range("2026-01-02 00:00", periods=100, freq="min")
    data = pd.DataFrame(
        {
            "time": list(ref_time) + list(cur_time),
            "y_true": list(reference_true) + list(current_true),
            "y_pred": list(reference_pred) + list(current_pred),
        }
    )
    result = detect_ddm(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 01:39"),
        current_window=("2026-01-02 00:00", "2026-01-02 01:39"),
        params={
            "variant_id": "DDM_WARNING_BUFFER",
            "y_true": "y_true",
            "y_pred": "y_pred",
            "min_num_instances": 30,
            "max_buffer_size": 20,
        },
    )
    assert result.variant_id == "DDM_WARNING_BUFFER"
    assert result.drift_detected is True
    assert result.measurements["BUFFERED_INSTANCE_COUNT"] <= 20
    assert "WARNING_BUFFER" in result.measurements


def test_ddm_class_specific() -> None:
    ref_time = pd.date_range("2026-01-01 00:00", periods=120, freq="min")
    cur_time = pd.date_range("2026-01-02 00:00", periods=120, freq="min")
    y_true_ref = np.array(["A"] * 60 + ["B"] * 60)
    y_pred_ref = y_true_ref.copy()
    y_pred_ref[55:60] = "A"
    y_true_cur = np.array(["A"] * 60 + ["B"] * 60)
    y_pred_cur = y_true_cur.copy()
    y_pred_cur[80:120] = "A"
    data = pd.DataFrame(
        {
            "time": list(ref_time) + list(cur_time),
            "y_true": list(y_true_ref) + list(y_true_cur),
            "y_pred": list(y_pred_ref) + list(y_pred_cur),
        }
    )
    result = detect_ddm(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 01:59"),
        current_window=("2026-01-02 00:00", "2026-01-02 01:59"),
        params={
            "variant_id": "DDM_CLASS_SPECIFIC",
            "y_true": "y_true",
            "y_pred": "y_pred",
            "class_label": "B",
            "min_reference_size": 50,
            "min_current_size": 50,
            "min_num_instances": 30,
        },
    )
    assert result.variant_id == "DDM_CLASS_SPECIFIC"
    assert result.measurements["CLASS_LABEL"] == "B"
    assert result.measurements["CLASS_ERROR_RATE"] == result.measurements["ERROR_RATE"]
    assert result.drift_detected is True
    assert any("CLASS_SPECIFIC" in warning for warning in result.warnings)


def test_ddm_validation_and_warnings() -> None:
    data = _error_frame(np.zeros(30), np.ones(30))
    missing = detect_ddm(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:29"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:29"),
    )
    assert missing.severity == "not_applicable"

    invalid = data.copy()
    invalid.loc[0, "error"] = 2
    invalid_result = detect_ddm(
        invalid,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:29"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:29"),
        params={"error_col": "error"},
    )
    assert invalid_result.severity == "not_applicable"

    warning_data = _error_frame(np.zeros(40), np.r_[np.zeros(20), np.ones(20)])
    warning_data["time"] = warning_data["time"].astype(object)
    warning_data.loc[0, "error"] = np.nan
    warning_data.loc[1, "time"] = "not-a-time"
    result = detect_ddm(
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
