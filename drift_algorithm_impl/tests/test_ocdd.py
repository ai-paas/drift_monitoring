from __future__ import annotations

import numpy as np
import pandas as pd

from drift_algorithm.methods.representationdriftmethod import detect_ocdd


def _representation_frame(reference: np.ndarray, current: np.ndarray) -> pd.DataFrame:
    ref_time = pd.date_range("2026-01-01 00:00", periods=len(reference), freq="min")
    cur_time = pd.date_range("2026-01-02 00:00", periods=len(current), freq="min")
    values = np.vstack([reference, current])
    return pd.DataFrame(
        {
            "time": list(ref_time) + list(cur_time),
            "f1": values[:, 0],
            "f2": values[:, 1],
            "f3": values[:, 2],
            "f4": values[:, 3],
        }
    )


def _base_reference(n: int = 100) -> np.ndarray:
    x = np.linspace(-2.0, 2.0, n)
    return np.column_stack([x, np.sin(x), np.cos(x), x**2 / 4.0])


def test_one_class_svm_drift_surrogate_no_drift() -> None:
    reference = _base_reference()
    current = reference[:40] + 0.01
    data = _representation_frame(reference, current)
    result = detect_ocdd(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 01:39"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:39"),
        params={"feature_cols": ["f1", "f2", "f3", "f4"], "alpha": 0.05, "anomaly_rate_threshold": 0.5},
    )
    assert result.variant_id == "ONE_CLASS_SVM_DRIFT"
    assert result.drift_detected is False
    assert result.measurements["ANOMALY_SCORE"] >= 0
    assert result.measurements["OUTLIER_OR_ANOMALY_RATE"] <= result.measurements["ANOMALY_RATE_THRESHOLD"]
    assert "radial" in result.measurements["METHOD_POLICY"]


def test_one_class_svm_drift_surrogate_detects_boundary_violations() -> None:
    reference = _base_reference()
    current = reference[:40] + np.array([4.0, 3.0, -3.0, 2.0])
    data = _representation_frame(reference, current)
    result = detect_ocdd(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 01:39"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:39"),
        params={"feature_cols": ["f1", "f2", "f3", "f4"], "alpha": 0.05, "anomaly_rate_threshold": 0.2},
    )
    assert result.drift_detected is True
    assert result.severity == "drift_detected"
    assert result.measurements["BOUNDARY_VIOLATION_RATE"] > result.measurements["ANOMALY_RATE_THRESHOLD"]
    assert result.measurements["ANOMALY_COUNT"] > 0


def test_isolation_forest_drift_score_surrogate() -> None:
    reference = _base_reference()
    current = reference[:35] + np.array([2.5, -2.0, 2.0, 1.5])
    data = _representation_frame(reference, current)
    result = detect_ocdd(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 01:39"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:34"),
        params={
            "variant_id": "ISOLATION_FOREST_DRIFT_SCORE",
            "feature_cols": ["f1", "f2", "f3", "f4"],
            "alpha": 0.05,
            "anomaly_rate_threshold": 0.2,
            "n_estimators": 32,
            "random_state": 7,
        },
    )
    assert result.variant_id == "ISOLATION_FOREST_DRIFT_SCORE"
    assert result.drift_detected is True
    assert "random_projection" in result.measurements["METHOD_POLICY"]
    assert any("deterministic NumPy surrogate" in warning for warning in result.warnings)


def test_autoencoder_reconstruction_drift_surrogate() -> None:
    reference = _base_reference(120)
    current = reference[:45].copy()
    current[:, 3] += 3.0
    data = _representation_frame(reference, current)
    result = detect_ocdd(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 01:59"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:44"),
        params={
            "variant_id": "AUTOENCODER_RECONSTRUCTION_DRIFT",
            "feature_cols": ["f1", "f2", "f3", "f4"],
            "latent_dim": 2,
            "alpha": 0.05,
            "anomaly_rate_threshold": 0.2,
        },
    )
    assert result.variant_id == "AUTOENCODER_RECONSTRUCTION_DRIFT"
    assert result.drift_detected is True
    assert result.measurements["RECONSTRUCTION_ERROR"] is not None
    assert "pca_reconstruction" in result.measurements["METHOD_POLICY"]
    assert any("linear PCA reconstruction" in warning for warning in result.warnings)


def test_ocdd_validation_and_warnings() -> None:
    data = _representation_frame(np.zeros((5, 4)), np.ones((5, 4)))
    invalid = detect_ocdd(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:04"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:04"),
        params={"feature_cols": ["f1"]},
    )
    assert invalid.severity == "not_applicable"

    dirty = _representation_frame(_base_reference(25), _base_reference(10) + 1.0)
    dirty.loc[0, "f1"] = np.nan
    dirty["time"] = dirty["time"].astype(object)
    dirty.loc[1, "time"] = "not-a-time"
    result = detect_ocdd(
        dirty,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:24"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:09"),
        params={
            "feature_cols": ["f1", "f2", "f3", "f4"],
            "min_reference_size": 20,
            "min_current_size": 5,
            "anomaly_rate_threshold": 0.2,
        },
    )
    assert result.severity in {"normal", "drift_detected"}
    assert any("dropped" in warning for warning in result.warnings)
