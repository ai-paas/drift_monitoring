from __future__ import annotations

import numpy as np
import pandas as pd

from drift_algorithm.methods.representationdriftmethod import detect_llm_query_semantic_distance


def _embedding_frame(reference: np.ndarray, current: np.ndarray) -> pd.DataFrame:
    ref_time = pd.date_range("2026-01-01 00:00", periods=len(reference), freq="min")
    cur_time = pd.date_range("2026-01-02 00:00", periods=len(current), freq="min")
    values = np.vstack([reference, current])
    return pd.DataFrame(
        {
            "time": list(ref_time) + list(cur_time),
            "q1": values[:, 0],
            "q2": values[:, 1],
            "q3": values[:, 2],
            "q4": values[:, 3],
        }
    )


def _query_embeddings(n: int = 60) -> np.ndarray:
    x = np.linspace(-2.0, 2.0, n)
    return np.column_stack([x, np.sin(x), np.cos(x), x**2 / 4.0])


def test_query_centroid_cosine_shift_no_drift() -> None:
    reference = _query_embeddings()
    current = reference + 0.001
    data = _embedding_frame(reference, current)
    result = detect_llm_query_semantic_distance(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:59"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:59"),
        params={"embedding_cols": ["q1", "q2", "q3", "q4"], "threshold": 0.2},
    )
    assert result.variant_id == "QUERY_CENTROID_COSINE_SHIFT"
    assert result.drift_detected is False
    assert result.measurements["COSINE_DISTANCE"] <= result.measurements["THRESHOLD"]
    assert result.measurements["CENTROID_SHIFT"] >= 0


def test_query_centroid_cosine_shift_detects_direction_change() -> None:
    reference = _query_embeddings()
    current = -reference + np.array([0.3, 0.0, 0.0, 0.0])
    data = _embedding_frame(reference, current)
    result = detect_llm_query_semantic_distance(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:59"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:59"),
        params={"embedding_cols": ["q1", "q2", "q3", "q4"], "threshold": 0.2},
    )
    assert result.drift_detected is True
    assert result.measurements["COSINE_DISTANCE"] > 0.2


def test_text_domain_classifier_drift_surrogate() -> None:
    reference = _query_embeddings(70)
    current = reference + np.array([1.5, -1.0, 0.9, 0.4])
    data = _embedding_frame(reference, current)
    result = detect_llm_query_semantic_distance(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 01:09"),
        current_window=("2026-01-02 00:00", "2026-01-02 01:09"),
        params={
            "variant_id": "TEXT_DOMAIN_CLASSIFIER_DRIFT",
            "embedding_cols": ["q1", "q2", "q3", "q4"],
            "roc_auc_threshold": 0.6,
        },
    )
    assert result.variant_id == "TEXT_DOMAIN_CLASSIFIER_DRIFT"
    assert result.drift_detected is True
    assert result.measurements["ROC_AUC"] > 0.6
    assert result.measurements["CLASSIFIER_CONFIDENCE"] is not None


def test_topic_distribution_shift() -> None:
    ref_time = pd.date_range("2026-01-01 00:00", periods=60, freq="min")
    cur_time = pd.date_range("2026-01-02 00:00", periods=60, freq="min")
    data = pd.DataFrame(
        {
            "time": list(ref_time) + list(cur_time),
            "topic": ["billing"] * 40 + ["support"] * 20 + ["billing"] * 10 + ["support"] * 10 + ["technical"] * 40,
        }
    )
    result = detect_llm_query_semantic_distance(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:59"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:59"),
        params={"variant_id": "TOPIC_DISTRIBUTION_SHIFT", "topic_col": "topic", "threshold": 0.2},
    )
    assert result.variant_id == "TOPIC_DISTRIBUTION_SHIFT"
    assert result.drift_detected is True
    assert result.measurements["JENSEN_SHANNON_DISTANCE"] > 0.2
    assert result.measurements["TOPIC_PROPORTION_DELTA"] > 0


def test_llm_query_semantic_validation_and_warnings() -> None:
    data = _embedding_frame(np.zeros((5, 4)), np.ones((5, 4)))
    invalid = detect_llm_query_semantic_distance(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:04"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:04"),
        params={"embedding_cols": ["q1"]},
    )
    assert invalid.severity == "not_applicable"

    dirty = _embedding_frame(_query_embeddings(25), _query_embeddings(10) + 0.5)
    dirty.loc[0, "q1"] = np.nan
    dirty["time"] = dirty["time"].astype(object)
    dirty.loc[1, "time"] = "not-a-time"
    result = detect_llm_query_semantic_distance(
        dirty,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:24"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:09"),
        params={
            "embedding_cols": ["q1", "q2", "q3", "q4"],
            "min_reference_size": 20,
            "min_current_size": 5,
            "threshold": 0.0,
        },
    )
    assert result.severity in {"normal", "drift_detected"}
    assert any("dropped" in warning for warning in result.warnings)
