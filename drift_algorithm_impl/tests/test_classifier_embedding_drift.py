from __future__ import annotations

import numpy as np
import pandas as pd

from drift_algorithm.methods.domainclassifiermethod import detect_classifier_embedding_drift_detection


def _embedding_frame(reference: np.ndarray, current: np.ndarray, columns: list[str]) -> pd.DataFrame:
    ref_time = pd.date_range("2026-01-01 00:00", periods=len(reference), freq="min")
    cur_time = pd.date_range("2026-01-02 00:00", periods=len(current), freq="min")
    data = pd.DataFrame(np.vstack([reference, current]), columns=columns)
    data.insert(0, "time", list(ref_time) + list(cur_time))
    return data


def test_domain_classifier_roc_auc_no_drift() -> None:
    x = np.linspace(-1.0, 1.0, 80)
    reference = np.column_stack([x, np.sin(x), np.cos(x)])
    current = reference + 0.0001
    data = _embedding_frame(reference, current, ["e1", "e2", "e3"])

    result = detect_classifier_embedding_drift_detection(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 01:19"),
        current_window=("2026-01-02 00:00", "2026-01-02 01:19"),
        params={"embedding_cols": ["e1", "e2", "e3"], "auc_threshold": 0.8},
    )

    assert result.variant_id == "DOMAIN_CLASSIFIER_ROC_AUC"
    assert result.drift_detected is False
    assert result.measurements["ROC_AUC"] < 0.8
    assert result.measurements["EMBEDDING_DIMENSION"] == 3


def test_domain_classifier_roc_auc_detects_embedding_shift() -> None:
    x = np.linspace(-1.0, 1.0, 90)
    reference = np.column_stack([x, np.sin(x), np.cos(x)])
    current = reference + np.array([3.0, 0.0, 0.0])
    data = _embedding_frame(reference, current, ["e1", "e2", "e3"])

    result = detect_classifier_embedding_drift_detection(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 01:29"),
        current_window=("2026-01-02 00:00", "2026-01-02 01:29"),
        params={"embedding_cols": ["e1", "e2", "e3"], "auc_threshold": 0.8},
    )

    assert result.drift_detected is True
    assert result.measurements["ROC_AUC"] >= 0.8
    assert result.measurements["PROBABILITY_MEAN_CURRENT"] > result.measurements["PROBABILITY_MEAN_REFERENCE"]


def test_domain_classifier_probability_drift() -> None:
    x = np.linspace(-1.0, 1.0, 80)
    reference = np.column_stack([x, np.sin(x)])
    current = reference + np.array([2.5, 0.0])
    data = _embedding_frame(reference, current, ["e1", "e2"])

    result = detect_classifier_embedding_drift_detection(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 01:19"),
        current_window=("2026-01-02 00:00", "2026-01-02 01:19"),
        params={
            "variant_id": "DOMAIN_CLASSIFIER_PROBABILITY_DRIFT",
            "embedding_cols": ["e1", "e2"],
            "alpha": 0.05,
            "probability_threshold": 0.7,
        },
    )

    assert result.variant_id == "DOMAIN_CLASSIFIER_PROBABILITY_DRIFT"
    assert result.drift_detected is True
    assert result.p_value is not None and result.p_value < 0.05
    assert result.measurements["HIGH_CURRENT_PROBABILITY_RATE"] > 0.0


def test_cross_validated_domain_classifier() -> None:
    x = np.linspace(-1.0, 1.0, 90)
    reference = np.column_stack([x, np.sin(x), np.cos(x)])
    current = reference + np.array([2.0, 0.0, 0.0])
    data = _embedding_frame(reference, current, ["e1", "e2", "e3"])

    result = detect_classifier_embedding_drift_detection(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 01:29"),
        current_window=("2026-01-02 00:00", "2026-01-02 01:29"),
        params={
            "variant_id": "CROSS_VALIDATED_DOMAIN_CLASSIFIER",
            "embedding_cols": ["e1", "e2", "e3"],
            "auc_threshold": 0.75,
            "cv_folds": 3,
            "min_fold_size": 10,
        },
    )

    assert result.variant_id == "CROSS_VALIDATED_DOMAIN_CLASSIFIER"
    assert result.drift_detected is True
    assert result.measurements["ROC_AUC"] >= 0.75
    assert len(result.measurements["CROSS_VALIDATION_FOLD_SCORES"]) == 3


def test_classifier_embedding_validation_and_warnings() -> None:
    data = _embedding_frame(np.zeros((5, 1)), np.ones((5, 1)), ["e1"])
    invalid = detect_classifier_embedding_drift_detection(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:04"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:04"),
        params={"embedding_cols": ["missing"]},
    )
    assert invalid.severity == "not_applicable"

    dirty = _embedding_frame(np.linspace(0.0, 1.0, 25).reshape(-1, 1), np.linspace(0.0, 1.0, 10).reshape(-1, 1), ["e1"])
    dirty.loc[0, "e1"] = np.nan
    dirty["time"] = dirty["time"].astype(object)
    dirty.loc[1, "time"] = "not-a-time"

    result = detect_classifier_embedding_drift_detection(
        dirty,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:24"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:09"),
        params={"embedding_cols": ["e1"], "min_reference_size": 20, "min_current_size": 5},
    )

    assert result.severity in {"normal", "drift_detected"}
    assert any("dropped" in warning for warning in result.warnings)
