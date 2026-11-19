from __future__ import annotations

import numpy as np
import pandas as pd

from drift_algorithm.methods.supervisedconceptdriftdetector import detect_ecdd_wt


def _error_frame(reference: np.ndarray, current: np.ndarray) -> pd.DataFrame:
    ref_time = pd.date_range("2026-01-01 00:00", periods=len(reference), freq="min")
    cur_time = pd.date_range("2026-01-02 00:00", periods=len(current), freq="min")
    return pd.DataFrame({"time": list(ref_time) + list(cur_time), "error": list(reference) + list(current)})


def test_ecdd_wt_standard_no_alarm_error_stream() -> None:
    reference = np.zeros(120)
    current = np.zeros(120)
    reference[::10] = 1
    current[::10] = 1
    data = _error_frame(reference, current)
    result = detect_ecdd_wt(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 01:59"),
        current_window=("2026-01-02 00:00", "2026-01-02 01:59"),
        params={"error_col": "error", "lambda": 0.2, "min_instances": 30},
    )
    assert result.variant_id == "ECDD_WT_STANDARD"
    assert result.p_value is None
    assert result.drift_detected is False
    assert result.severity == "normal"
    assert result.measurements["DRIFT_ALARM_STATE"] == "normal"
    assert result.measurements["WARNING_STATE"] is False
    assert result.measurements["BASELINE_ERROR_RATE"] == 0.1
    assert result.measurements["CURRENT_ERROR_RATE"] == 0.1


def test_ecdd_wt_warning_drift_alarm() -> None:
    reference = np.zeros(120)
    reference[::20] = 1
    current = np.r_[np.zeros(40), np.ones(80)]
    data = _error_frame(reference, current)
    result = detect_ecdd_wt(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 01:59"),
        current_window=("2026-01-02 00:00", "2026-01-02 01:59"),
        params={"variant_id": "ECDD_WT_WARNING_DRIFT", "error_col": "error", "lambda": 0.2, "min_instances": 30},
    )
    assert result.variant_id == "ECDD_WT_WARNING_DRIFT"
    assert result.drift_detected is True
    assert result.severity == "drift_detected"
    assert result.measurements["DRIFT_ALARM_STATE"] == "drift_detected"
    assert result.measurements["TEST_STATISTIC"] >= result.measurements["DRIFT_THRESHOLD"]
    assert result.measurements["ECDD_WT_EVENTS"]


def test_ecdd_wt_error_stream_from_labels() -> None:
    reference_true = np.ones(120, dtype=int)
    reference_pred = reference_true.copy()
    reference_pred[::20] = 0
    current_true = np.ones(120, dtype=int)
    current_pred = current_true.copy()
    current_pred[50:] = 0
    ref_time = pd.date_range("2026-01-01 00:00", periods=120, freq="min")
    cur_time = pd.date_range("2026-01-02 00:00", periods=120, freq="min")
    data = pd.DataFrame(
        {
            "time": list(ref_time) + list(cur_time),
            "y_true": list(reference_true) + list(current_true),
            "y_pred": list(reference_pred) + list(current_pred),
        }
    )
    result = detect_ecdd_wt(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 01:59"),
        current_window=("2026-01-02 00:00", "2026-01-02 01:59"),
        params={
            "variant_id": "ECDD_WT_ERROR_STREAM",
            "y_true": "y_true",
            "y_pred": "y_pred",
            "lambda": 0.2,
            "min_instances": 30,
        },
    )
    assert result.variant_id == "ECDD_WT_ERROR_STREAM"
    assert result.drift_detected is True
    assert result.measurements["P_VALUE"] is None
    assert result.measurements["EWMA_ERROR_STATISTIC"] > result.measurements["BASELINE_ERROR_RATE"]


def test_ecdd_wt_validation_and_warnings() -> None:
    data = _error_frame(np.zeros(40), np.ones(40))
    invalid_lambda = detect_ecdd_wt(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:39"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:39"),
        params={"error_col": "error", "lambda": 0.0},
    )
    assert invalid_lambda.severity == "not_applicable"

    invalid_error = data.copy()
    invalid_error.loc[0, "error"] = 2
    invalid_result = detect_ecdd_wt(
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
    result = detect_ecdd_wt(
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


def test_ecdd_wt_non_scalar_requests() -> None:
    data = _error_frame(np.zeros(30), np.ones(30))
    feature_request = detect_ecdd_wt(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:29"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:29"),
        params={"feature_cols": ["a", "b"]},
    )
    assert feature_request.severity == "not_applicable"
