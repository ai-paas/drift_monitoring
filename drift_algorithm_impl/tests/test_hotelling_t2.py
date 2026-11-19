from __future__ import annotations

import numpy as np
import pandas as pd

from drift_algorithm.methods.multivariateprocesscontrol import detect_hotelling_t2


def _multivariate_frame(reference: np.ndarray, current: np.ndarray) -> pd.DataFrame:
    ref_time = pd.date_range("2026-01-01 00:00", periods=len(reference), freq="min")
    cur_time = pd.date_range("2026-01-02 00:00", periods=len(current), freq="min")
    values = np.vstack([reference, current])
    return pd.DataFrame(
        {
            "time": list(ref_time) + list(cur_time),
            "x1": values[:, 0],
            "x2": values[:, 1],
            "x3": values[:, 2] if values.shape[1] > 2 else values[:, 0] + values[:, 1],
        }
    )


def test_hotelling_t2_two_sample_no_drift() -> None:
    base = np.column_stack(
        [
            np.linspace(-1.0, 1.0, 80),
            np.sin(np.linspace(0.0, 4.0, 80)),
            np.cos(np.linspace(0.0, 4.0, 80)),
        ]
    )
    data = _multivariate_frame(base, base + 0.01)
    result = detect_hotelling_t2(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 01:19"),
        current_window=("2026-01-02 00:00", "2026-01-02 01:19"),
        params={"variant_id": "HOTELLING_T2_TWO_SAMPLE", "feature_cols": ["x1", "x2", "x3"], "alpha": 0.01},
    )
    assert result.variant_id == "HOTELLING_T2_TWO_SAMPLE"
    assert result.p_value is not None
    assert result.drift_detected is False
    assert result.severity == "normal"
    assert result.measurements["DRIFT_ALARM_STATE"] == "normal"
    assert result.measurements["FEATURE_DIMENSION"] == 3


def test_hotelling_t2_two_sample_drift() -> None:
    base = np.column_stack(
        [
            np.linspace(-1.0, 1.0, 80),
            np.sin(np.linspace(0.0, 4.0, 80)),
            np.cos(np.linspace(0.0, 4.0, 80)),
        ]
    )
    data = _multivariate_frame(base, base + np.array([1.5, 1.0, -1.2]))
    result = detect_hotelling_t2(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 01:19"),
        current_window=("2026-01-02 00:00", "2026-01-02 01:19"),
        params={"variant_id": "HOTELLING_T2_TWO_SAMPLE", "feature_cols": ["x1", "x2", "x3"], "alpha": 0.05},
    )
    assert result.drift_detected is True
    assert result.severity == "drift_detected"
    assert result.measurements["HOTELLING_T2_STATISTIC"] > result.measurements["CONTROL_LIMIT"]
    assert result.measurements["P_VALUE"] < 0.05


def test_hotelling_t2_one_sample_phase_ii_control_limit() -> None:
    base = np.column_stack(
        [
            np.linspace(-1.0, 1.0, 60),
            np.sin(np.linspace(0.0, 3.0, 60)),
            np.cos(np.linspace(0.0, 3.0, 60)),
        ]
    )
    data = _multivariate_frame(base, base + np.array([0.8, 0.6, 0.5]))
    result = detect_hotelling_t2(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:59"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:59"),
        params={
            "variant_id": "HOTELLING_T2_ONE_SAMPLE_PHASE_II",
            "feature_cols": ["x1", "x2", "x3"],
            "control_limit": 1.0,
        },
    )
    assert result.variant_id == "HOTELLING_T2_ONE_SAMPLE_PHASE_II"
    assert result.drift_detected is True
    assert result.measurements["CONTROL_LIMIT"] == 1.0
    assert result.measurements["DRIFT_ALARM_STATE"] == "drift_detected"


def test_regularized_hotelling_t2_high_dimension() -> None:
    ref_time = pd.date_range("2026-01-01 00:00", periods=8, freq="min")
    cur_time = pd.date_range("2026-01-02 00:00", periods=8, freq="min")
    cols = [f"f{i}" for i in range(6)]
    reference = np.arange(48, dtype=float).reshape(8, 6) / 10.0
    current = reference + 0.8
    data = pd.DataFrame(np.vstack([reference, current]), columns=cols)
    data.insert(0, "time", list(ref_time) + list(cur_time))
    result = detect_hotelling_t2(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:07"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:07"),
        params={
            "variant_id": "REGULARIZED_HOTELLING_T2",
            "feature_cols": cols,
            "regularization_strength": 0.1,
            "control_limit": 0.1,
            "min_reference_size": 7,
            "min_current_size": 7,
        },
    )
    assert result.variant_id == "REGULARIZED_HOTELLING_T2"
    assert result.drift_detected is True
    assert result.measurements["METHOD_POLICY"].startswith("regularized")
    assert any("regularized covariance" in warning for warning in result.warnings)


def test_hotelling_t2_validation_and_warnings() -> None:
    data = _multivariate_frame(np.zeros((5, 3)), np.ones((5, 3)))
    missing_features = detect_hotelling_t2(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:04"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:04"),
        params={"feature_cols": ["x1"]},
    )
    assert missing_features.severity == "not_applicable"

    dirty = data.copy()
    dirty.loc[0, "x1"] = np.nan
    dirty["time"] = dirty["time"].astype(object)
    dirty.loc[1, "time"] = "not-a-time"
    result = detect_hotelling_t2(
        dirty,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:04"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:04"),
        params={
            "variant_id": "REGULARIZED_HOTELLING_T2",
            "feature_cols": ["x1", "x2", "x3"],
            "min_reference_size": 3,
            "min_current_size": 3,
        },
    )
    assert result.severity in {"normal", "drift_detected"}
    assert any("dropped" in warning for warning in result.warnings)
