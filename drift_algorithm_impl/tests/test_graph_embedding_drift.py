from __future__ import annotations

import numpy as np
import pandas as pd

from drift_algorithm.methods.representationdriftmethod import detect_graph_embedding_drift


def _graph_embedding_frame(reference: np.ndarray, current: np.ndarray, groups: list[str] | None = None) -> pd.DataFrame:
    ref_time = pd.date_range("2026-01-01 00:00", periods=len(reference), freq="min")
    cur_time = pd.date_range("2026-01-02 00:00", periods=len(current), freq="min")
    values = np.vstack([reference, current])
    data = pd.DataFrame(
        {
            "time": list(ref_time) + list(cur_time),
            "e1": values[:, 0],
            "e2": values[:, 1],
            "e3": values[:, 2],
            "e4": values[:, 3],
        }
    )
    if groups is not None:
        data["node_group"] = groups
    return data


def _embedding_reference(n: int = 70) -> np.ndarray:
    x = np.linspace(-2.0, 2.0, n)
    return np.column_stack([x, np.sin(x), np.cos(x), x**2 / 4.0])


def test_graph_embedding_mmd_no_drift() -> None:
    reference = _embedding_reference(60)
    current = reference + 0.001
    data = _graph_embedding_frame(reference, current)
    result = detect_graph_embedding_drift(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:59"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:59"),
        params={
            "embedding_cols": ["e1", "e2", "e3", "e4"],
            "alpha": 0.05,
            "permutation_count": 19,
            "random_state": 17,
        },
    )
    assert result.variant_id == "GRAPH_EMBEDDING_MMD"
    assert result.drift_detected is False
    assert result.measurements["GRAPH_EMBEDDING_DRIFT_SCORE"] >= 0
    assert result.p_value is not None and result.p_value > 0.05


def test_graph_embedding_mmd_detects_shift() -> None:
    reference = _embedding_reference(60)
    current = reference + np.array([1.4, -0.9, 0.8, 0.5])
    data = _graph_embedding_frame(reference, current)
    result = detect_graph_embedding_drift(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:59"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:59"),
        params={
            "variant_id": "GRAPH_EMBEDDING_MMD",
            "embedding_cols": ["e1", "e2", "e3", "e4"],
            "alpha": 0.1,
            "permutation_count": 19,
            "random_state": 19,
        },
    )
    assert result.drift_detected is True
    assert result.p_value is not None and result.p_value < 0.1


def test_graph_embedding_centroid_shift() -> None:
    reference = _embedding_reference(50)
    current = reference + np.array([0.8, 0.7, -0.6, 0.4])
    data = _graph_embedding_frame(reference, current)
    result = detect_graph_embedding_drift(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:49"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:49"),
        params={
            "variant_id": "GRAPH_EMBEDDING_CENTROID_SHIFT",
            "embedding_cols": ["e1", "e2", "e3", "e4"],
            "threshold": 0.5,
        },
    )
    assert result.variant_id == "GRAPH_EMBEDDING_CENTROID_SHIFT"
    assert result.drift_detected is True
    assert result.p_value is None
    assert result.measurements["CENTROID_SHIFT"] > 0.5
    assert result.measurements["COSINE_DISTANCE"] >= 0


def test_node_representation_drift_group_scores() -> None:
    reference = _embedding_reference(80)
    current = reference.copy()
    current[40:] += np.array([1.2, -0.8, 0.6, 0.5])
    groups = ["stable"] * 40 + ["shifted"] * 40 + ["stable"] * 40 + ["shifted"] * 40
    data = _graph_embedding_frame(reference, current, groups)
    result = detect_graph_embedding_drift(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 01:19"),
        current_window=("2026-01-02 00:00", "2026-01-02 01:19"),
        params={
            "variant_id": "NODE_REPRESENTATION_DRIFT",
            "embedding_cols": ["e1", "e2", "e3", "e4"],
            "node_group_col": "node_group",
            "threshold": 0.7,
        },
    )
    assert result.variant_id == "NODE_REPRESENTATION_DRIFT"
    assert result.drift_detected is True
    assert result.measurements["TOP_NODE_GROUP"] == "shifted"
    assert result.measurements["NODE_GROUP_SCORES"]["shifted"]["alarm_state"] == "drift_detected"


def test_graph_embedding_validation_and_warnings() -> None:
    data = _graph_embedding_frame(np.zeros((5, 4)), np.ones((5, 4)))
    invalid = detect_graph_embedding_drift(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:04"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:04"),
        params={"embedding_cols": ["e1"]},
    )
    assert invalid.severity == "not_applicable"

    dirty = _graph_embedding_frame(_embedding_reference(25), _embedding_reference(10) + 0.5)
    dirty.loc[0, "e1"] = np.nan
    dirty["time"] = dirty["time"].astype(object)
    dirty.loc[1, "time"] = "not-a-time"
    result = detect_graph_embedding_drift(
        dirty,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:24"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:09"),
        params={
            "embedding_cols": ["e1", "e2", "e3", "e4"],
            "min_reference_size": 20,
            "min_current_size": 5,
            "threshold": 0.0,
        },
    )
    assert result.severity in {"normal", "drift_detected"}
    assert any("dropped" in warning for warning in result.warnings)
