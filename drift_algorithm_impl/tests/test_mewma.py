from __future__ import annotations

import numpy as np
import pandas as pd

from drift_algorithm.methods.multivariateprocesscontrol import detect_mewma


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


def test_mewma_standard_no_alarm() -> None:
    base = np.column_stack(
        [
            np.linspace(-1.0, 1.0, 80),
            np.sin(np.linspace(0.0, 4.0, 80)),
            np.cos(np.linspace(0.0, 4.0, 80)),
        ]
    )
    data = _multivariate_frame(base, base + 0.01)
    result = detect_mewma(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 01:19"),
        current_window=("2026-01-02 00:00", "2026-01-02 01:19"),
        params={"feature_cols": ["x1", "x2", "x3"], "lambda": 0.2, "control_limit": 100.0},
    )
    assert result.variant_id == "MEWMA_STANDARD"
    assert result.p_value is None
    assert result.drift_detected is False
    assert result.measurements["DRIFT_ALARM_STATE"] == "normal"
    assert result.measurements["MEWMA_STATISTIC"] < result.measurements["CONTROL_LIMIT"]


def test_mewma_standard_drift_alarm() -> None:
    base = np.column_stack(
        [
            np.linspace(-1.0, 1.0, 80),
            np.sin(np.linspace(0.0, 4.0, 80)),
            np.cos(np.linspace(0.0, 4.0, 80)),
        ]
    )
    data = _multivariate_frame(base, base + np.array([1.2, 1.0, -0.9]))
    result = detect_mewma(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 01:19"),
        current_window=("2026-01-02 00:00", "2026-01-02 01:19"),
        params={"feature_cols": ["x1", "x2", "x3"], "lambda": 0.3, "control_limit": 5.0},
    )
    assert result.drift_detected is True
    assert result.severity == "drift_detected"
    assert result.measurements["MEWMA_STATISTIC"] > result.measurements["CONTROL_LIMIT"]
    assert result.measurements["ALARM_INDEX"] is not None


def test_mewma_with_mahalanobis_d2_regularized() -> None:
    ref_time = pd.date_range("2026-01-01 00:00", periods=10, freq="min")
    cur_time = pd.date_range("2026-01-02 00:00", periods=10, freq="min")
    cols = [f"f{i}" for i in range(5)]
    reference = np.arange(50, dtype=float).reshape(10, 5) / 10.0
    current = reference + 0.5
    data = pd.DataFrame(np.vstack([reference, current]), columns=cols)
    data.insert(0, "time", list(ref_time) + list(cur_time))
    result = detect_mewma(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:09"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:09"),
        params={
            "variant_id": "MEWMA_WITH_MAHALANOBIS_D2",
            "feature_cols": cols,
            "covariance_estimator": "regularized",
            "regularization_strength": 0.1,
            "control_limit": 0.1,
            "min_reference_size": 7,
            "min_current_size": 7,
        },
    )
    assert result.variant_id == "MEWMA_WITH_MAHALANOBIS_D2"
    assert result.drift_detected is True
    assert result.measurements["MAHALANOBIS_DISTANCE"] >= 0
    assert any("regularized covariance" in warning for warning in result.warnings)


def test_mewma_validation_and_warnings() -> None:
    data = _multivariate_frame(np.zeros((5, 3)), np.ones((5, 3)))
    invalid = detect_mewma(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:04"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:04"),
        params={"feature_cols": ["x1"], "lambda": 0.2},
    )
    assert invalid.severity == "not_applicable"

    dirty = data.copy()
    dirty.loc[0, "x1"] = np.nan
    dirty["time"] = dirty["time"].astype(object)
    dirty.loc[1, "time"] = "not-a-time"
    result = detect_mewma(
        dirty,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:04"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:04"),
        params={
            "feature_cols": ["x1", "x2", "x3"],
            "min_reference_size": 3,
            "min_current_size": 3,
            "control_limit": 1.0,
        },
    )
    assert result.severity in {"normal", "drift_detected"}
    assert any("dropped" in warning for warning in result.warnings)
