from __future__ import annotations

import numpy as np
import pandas as pd

from drift_algorithm.methods.representationdriftmethod import detect_model_uncertainty_drift


def _uncertainty_frame(reference: np.ndarray, current: np.ndarray, columns: list[str]) -> pd.DataFrame:
    ref_time = pd.date_range("2026-01-01 00:00", periods=len(reference), freq="min")
    cur_time = pd.date_range("2026-01-02 00:00", periods=len(current), freq="min")
    data = pd.DataFrame(np.vstack([reference, current]), columns=columns)
    data.insert(0, "time", list(ref_time) + list(cur_time))
    return data


def test_softmax_confidence_drift_no_drift() -> None:
    reference = np.linspace(0.75, 0.95, 80).reshape(-1, 1)
    current = reference + 0.001
    data = _uncertainty_frame(reference, current, ["confidence"])
    result = detect_model_uncertainty_drift(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 01:19"),
        current_window=("2026-01-02 00:00", "2026-01-02 01:19"),
        params={"confidence_col": "confidence", "alpha": 0.01},
    )
    assert result.variant_id == "SOFTMAX_CONFIDENCE_DRIFT"
    assert result.drift_detected is False
    assert result.measurements["UNCERTAINTY_MEAN_CURRENT"] > 0
    assert result.p_value is not None and result.p_value > 0.01


def test_softmax_confidence_drift_detects_drop() -> None:
    reference = np.linspace(0.75, 0.95, 80).reshape(-1, 1)
    current = np.linspace(0.25, 0.45, 80).reshape(-1, 1)
    data = _uncertainty_frame(reference, current, ["confidence"])
    result = detect_model_uncertainty_drift(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 01:19"),
        current_window=("2026-01-02 00:00", "2026-01-02 01:19"),
        params={"confidence_col": "confidence", "alpha": 0.05, "confidence_threshold": 0.5},
    )
    assert result.drift_detected is True
    assert result.measurements["LOW_CONFIDENCE_RATE_CURRENT"] > result.measurements["LOW_CONFIDENCE_RATE_REFERENCE"]
    assert result.p_value is not None and result.p_value < 0.05


def test_entropy_drift_from_probability_columns() -> None:
    reference = np.tile(np.array([[0.9, 0.08, 0.02]]), (60, 1))
    current = np.tile(np.array([[0.34, 0.33, 0.33]]), (60, 1))
    data = _uncertainty_frame(reference, current, ["p1", "p2", "p3"])
    result = detect_model_uncertainty_drift(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:59"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:59"),
        params={"variant_id": "ENTROPY_DRIFT", "probability_cols": ["p1", "p2", "p3"], "alpha": 0.05},
    )
    assert result.variant_id == "ENTROPY_DRIFT"
    assert result.drift_detected is True
    assert result.measurements["UNCERTAINTY_MEAN_CURRENT"] > result.measurements["UNCERTAINTY_MEAN_REFERENCE"]


def test_predictive_variance_drift_from_prediction_columns() -> None:
    x = np.linspace(-1.0, 1.0, 70)
    reference = np.column_stack([x, x + 0.01, x - 0.01])
    current = np.column_stack([x - 1.0, x, x + 1.0])
    data = _uncertainty_frame(reference, current, ["m1", "m2", "m3"])
    result = detect_model_uncertainty_drift(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 01:09"),
        current_window=("2026-01-02 00:00", "2026-01-02 01:09"),
        params={"variant_id": "PREDICTIVE_VARIANCE_DRIFT", "prediction_cols": ["m1", "m2", "m3"], "alpha": 0.05},
    )
    assert result.variant_id == "PREDICTIVE_VARIANCE_DRIFT"
    assert result.drift_detected is True
    assert result.measurements["UNCERTAINTY_MEAN_CURRENT"] > result.measurements["UNCERTAINTY_MEAN_REFERENCE"]


def test_model_uncertainty_validation_and_warnings() -> None:
    data = _uncertainty_frame(np.zeros((5, 1)), np.ones((5, 1)), ["confidence"])
    invalid = detect_model_uncertainty_drift(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:04"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:04"),
        params={"variant_id": "ENTROPY_DRIFT"},
    )
    assert invalid.severity == "not_applicable"

    dirty = _uncertainty_frame(np.linspace(0.7, 0.9, 25).reshape(-1, 1), np.linspace(0.4, 0.6, 10).reshape(-1, 1), ["confidence"])
    dirty.loc[0, "confidence"] = np.nan
    dirty["time"] = dirty["time"].astype(object)
    dirty.loc[1, "time"] = "not-a-time"
    result = detect_model_uncertainty_drift(
        dirty,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:24"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:09"),
        params={"confidence_col": "confidence", "min_reference_size": 20, "min_current_size": 5},
    )
    assert result.severity in {"normal", "drift_detected"}
    assert any("dropped" in warning for warning in result.warnings)
