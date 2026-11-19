from __future__ import annotations

import numpy as np
import pandas as pd

from drift_algorithm.methods.representationdriftmethod import detect_feature_map_drift


def _feature_map_frame(reference: np.ndarray, current: np.ndarray) -> pd.DataFrame:
    ref_time = pd.date_range("2026-01-01 00:00", periods=len(reference), freq="min")
    cur_time = pd.date_range("2026-01-02 00:00", periods=len(current), freq="min")
    values = np.vstack([reference, current])
    return pd.DataFrame(
        {
            "time": list(ref_time) + list(cur_time),
            "l1_f1": values[:, 0],
            "l1_f2": values[:, 1],
            "l2_f1": values[:, 2],
            "l2_f2": values[:, 3],
        }
    )


def _base_feature_map(n: int = 80) -> np.ndarray:
    x = np.linspace(-2.0, 2.0, n)
    return np.column_stack([x, np.sin(x), np.cos(x), x**2 / 4.0])


def test_model_feature_map_ks_no_drift() -> None:
    reference = _base_feature_map()
    current = reference + 0.001
    data = _feature_map_frame(reference, current)
    result = detect_feature_map_drift(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 01:19"),
        current_window=("2026-01-02 00:00", "2026-01-02 01:19"),
        params={"feature_cols": ["l1_f1", "l1_f2", "l2_f1", "l2_f2"], "alpha": 0.01},
    )
    assert result.variant_id == "MODEL_FEATURE_MAP_KS"
    assert result.drift_detected is False
    assert result.measurements["DRIFT_ALARM_STATE"] == "normal"
    assert result.measurements["P_VALUE"] > 0.01
    assert result.measurements["MAX_FEATURE_STATISTIC"] >= 0


def test_model_feature_map_ks_detects_axis_shift() -> None:
    reference = _base_feature_map()
    current = reference + np.array([1.5, 0.0, -1.2, 0.8])
    data = _feature_map_frame(reference, current)
    result = detect_feature_map_drift(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 01:19"),
        current_window=("2026-01-02 00:00", "2026-01-02 01:19"),
        params={"variant_id": "MODEL_FEATURE_MAP_KS", "feature_cols": ["l1_f1", "l1_f2", "l2_f1", "l2_f2"], "alpha": 0.05},
    )
    assert result.drift_detected is True
    assert result.severity == "drift_detected"
    assert result.measurements["SIGNIFICANT_FEATURE_COUNT"] >= 1
    assert result.p_value is not None and result.p_value < 0.05


def test_model_feature_map_mmd_with_permutation() -> None:
    reference = _base_feature_map(50)
    current = reference + np.array([1.0, -0.8, 0.7, 0.5])
    data = _feature_map_frame(reference, current)
    result = detect_feature_map_drift(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:49"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:49"),
        params={
            "variant_id": "MODEL_FEATURE_MAP_MMD",
            "feature_cols": ["l1_f1", "l1_f2", "l2_f1", "l2_f2"],
            "alpha": 0.1,
            "permutation_count": 19,
            "random_state": 3,
        },
    )
    assert result.variant_id == "MODEL_FEATURE_MAP_MMD"
    assert result.measurements["TEST_STATISTIC"] > 0
    assert result.p_value is not None
    assert result.drift_detected is True


def test_layerwise_feature_map_drift_reports_layers() -> None:
    reference = _base_feature_map(60)
    current = reference.copy()
    current[:, 2:] += np.array([1.2, -0.9])
    data = _feature_map_frame(reference, current)
    result = detect_feature_map_drift(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:59"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:59"),
        params={
            "variant_id": "LAYERWISE_FEATURE_MAP_DRIFT",
            "layer_feature_cols": {"layer1": ["l1_f1", "l1_f2"], "layer2": ["l2_f1", "l2_f2"]},
            "alpha": 0.1,
            "permutation_count": 19,
            "random_state": 5,
        },
    )
    assert result.variant_id == "LAYERWISE_FEATURE_MAP_DRIFT"
    assert result.drift_detected is True
    assert set(result.measurements["LAYERWISE_SCORES"]) == {"layer1", "layer2"}
    assert result.measurements["SIGNIFICANT_FEATURE_COUNT"] >= 1


def test_feature_map_drift_validation_and_warnings() -> None:
    data = _feature_map_frame(np.zeros((5, 4)), np.ones((5, 4)))
    invalid = detect_feature_map_drift(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:04"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:04"),
        params={"feature_cols": ["l1_f1"]},
    )
    assert invalid.severity == "not_applicable"

    dirty = _feature_map_frame(_base_feature_map(25), _base_feature_map(10) + 0.5)
    dirty.loc[0, "l1_f1"] = np.nan
    dirty["time"] = dirty["time"].astype(object)
    dirty.loc[1, "time"] = "not-a-time"
    result = detect_feature_map_drift(
        dirty,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:24"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:09"),
        params={
            "feature_cols": ["l1_f1", "l1_f2", "l2_f1", "l2_f2"],
            "min_reference_size": 20,
            "min_current_size": 5,
            "alpha": 0.2,
        },
    )
    assert result.severity in {"normal", "drift_detected"}
    assert any("dropped" in warning for warning in result.warnings)
