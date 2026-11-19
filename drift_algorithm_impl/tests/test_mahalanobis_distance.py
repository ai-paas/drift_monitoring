from __future__ import annotations

import numpy as np
import pandas as pd

from drift_algorithm.methods.multivariateprocesscontrol import detect_mahalanobis_distance


def _multivariate_frame(reference: np.ndarray, current: np.ndarray) -> pd.DataFrame:
    ref_time = pd.date_range("2026-01-01 00:00", periods=len(reference), freq="min")
    cur_time = pd.date_range("2026-01-02 00:00", periods=len(current), freq="min")
    values = np.vstack([reference, current])
    return pd.DataFrame(
        {
            "time": list(ref_time) + list(cur_time),
            "x1": values[:, 0],
            "x2": values[:, 1],
            "x3": values[:, 2],
        }
    )


def test_window_mean_mahalanobis_no_drift() -> None:
    base = np.column_stack(
        [
            np.linspace(-1.0, 1.0, 80),
            np.sin(np.linspace(0.0, 4.0, 80)),
            np.cos(np.linspace(0.0, 4.0, 80)),
        ]
    )
    data = _multivariate_frame(base, base + 0.01)
    result = detect_mahalanobis_distance(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 01:19"),
        current_window=("2026-01-02 00:00", "2026-01-02 01:19"),
        params={"feature_cols": ["x1", "x2", "x3"], "alpha": 0.01},
    )
    assert result.variant_id == "WINDOW_MEAN_MAHALANOBIS"
    assert result.drift_detected is False
    assert result.severity == "normal"
    assert result.measurements["MAHALANOBIS_DISTANCE"] >= 0
    assert result.measurements["MAHALANOBIS_D2"] < result.measurements["CONTROL_LIMIT"]
    assert result.measurements["THRESHOLD_EXCEEDANCE"] is False


def test_window_mean_mahalanobis_drift() -> None:
    base = np.column_stack(
        [
            np.linspace(-1.0, 1.0, 80),
            np.sin(np.linspace(0.0, 4.0, 80)),
            np.cos(np.linspace(0.0, 4.0, 80)),
        ]
    )
    data = _multivariate_frame(base, base + np.array([1.2, 1.0, -0.8]))
    result = detect_mahalanobis_distance(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 01:19"),
        current_window=("2026-01-02 00:00", "2026-01-02 01:19"),
        params={"feature_cols": ["x1", "x2", "x3"], "threshold": 2.0},
    )
    assert result.drift_detected is True
    assert result.severity == "drift_detected"
    assert result.measurements["MAHALANOBIS_D2"] > result.measurements["CONTROL_LIMIT"]
    assert result.measurements["OUTLIER_FLAG"] is True


def test_sample_mahalanobis_outlier_counts_current_samples() -> None:
    reference = np.column_stack(
        [
            np.linspace(-1.0, 1.0, 60),
            np.sin(np.linspace(0.0, 3.0, 60)),
            np.cos(np.linspace(0.0, 3.0, 60)),
        ]
    )
    current = reference[:10].copy()
    current[-1] = np.array([4.0, 4.0, -4.0])
    data = _multivariate_frame(reference, current)
    result = detect_mahalanobis_distance(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:59"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:09"),
        params={
            "variant_id": "SAMPLE_MAHALANOBIS_OUTLIER",
            "feature_cols": ["x1", "x2", "x3"],
            "threshold": 10.0,
            "min_current_size": 1,
        },
    )
    assert result.variant_id == "SAMPLE_MAHALANOBIS_OUTLIER"
    assert result.drift_detected is True
    assert result.measurements["OUTLIER_COUNT"] >= 1
    assert result.measurements["OUTLIER_FRACTION"] > 0


def test_robust_mahalanobis_uses_robust_policy() -> None:
    reference = np.column_stack(
        [
            np.linspace(-1.0, 1.0, 70),
            np.sin(np.linspace(0.0, 4.0, 70)),
            np.cos(np.linspace(0.0, 4.0, 70)),
        ]
    )
    reference[0] = np.array([10.0, -10.0, 10.0])
    current = reference[:20] + np.array([1.0, 0.8, -0.9])
    data = _multivariate_frame(reference, current)
    result = detect_mahalanobis_distance(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 01:09"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:19"),
        params={
            "variant_id": "ROBUST_MAHALANOBIS",
            "feature_cols": ["x1", "x2", "x3"],
            "threshold": 2.0,
            "min_current_size": 10,
        },
    )
    assert result.variant_id == "ROBUST_MAHALANOBIS"
    assert result.measurements["METHOD_POLICY"] == "robust_median_mad_diagonal_covariance"
    assert any("robust diagonal covariance" in warning for warning in result.warnings)


def test_mahalanobis_validation_and_warnings() -> None:
    data = _multivariate_frame(np.zeros((5, 3)), np.ones((5, 3)))
    invalid = detect_mahalanobis_distance(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:04"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:04"),
        params={"feature_cols": ["x1"]},
    )
    assert invalid.severity == "not_applicable"

    dirty = data.copy()
    dirty.loc[0, "x1"] = np.nan
    dirty["time"] = dirty["time"].astype(object)
    dirty.loc[1, "time"] = "not-a-time"
    result = detect_mahalanobis_distance(
        dirty,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:04"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:04"),
        params={
            "feature_cols": ["x1", "x2", "x3"],
            "min_reference_size": 3,
            "min_current_size": 3,
            "threshold": 1.0,
        },
    )
    assert result.severity in {"normal", "drift_detected"}
    assert any("dropped" in warning for warning in result.warnings)
