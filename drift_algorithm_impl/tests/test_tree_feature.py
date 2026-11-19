from __future__ import annotations

import numpy as np
import pandas as pd

from drift_algorithm.methods.explanationdriftmethod import detect_tree_feature


def _tree_frame(reference: np.ndarray, current: np.ndarray, columns: list[str]) -> pd.DataFrame:
    ref_time = pd.date_range("2026-01-01 00:00", periods=len(reference), freq="min")
    cur_time = pd.date_range("2026-01-02 00:00", periods=len(current), freq="min")
    data = pd.DataFrame(np.vstack([reference, current]), columns=columns)
    data.insert(0, "time", list(ref_time) + list(cur_time))
    return data


def test_time_feature_split_no_drift() -> None:
    x = np.linspace(-1.0, 1.0, 80)
    reference = np.column_stack([x, np.sin(x)])
    current = reference + 0.001
    data = _tree_frame(reference, current, ["period_indicator", "feature_b"])

    result = detect_tree_feature(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 01:19"),
        current_window=("2026-01-02 00:00", "2026-01-02 01:19"),
        params={
            "feature_cols": ["period_indicator", "feature_b"],
            "time_feature_col": "period_indicator",
            "split_accuracy_threshold": 0.75,
        },
    )

    assert result.variant_id == "TIME_FEATURE_SPLIT_DETECTOR"
    assert result.drift_detected is False
    assert result.measurements["TREE_SPLIT_SIGNAL"]["time_split_count"] == 0
    assert result.measurements["FEATURE_IMPORTANCE_OR_RANK"][0]["feature"] in {"period_indicator", "feature_b"}


def test_time_feature_split_detects_period_indicator() -> None:
    reference = np.column_stack([np.zeros(70), np.linspace(-1.0, 1.0, 70)])
    current = np.column_stack([np.ones(70), np.linspace(-1.0, 1.0, 70)])
    data = _tree_frame(reference, current, ["period_indicator", "feature_b"])

    result = detect_tree_feature(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 01:09"),
        current_window=("2026-01-02 00:00", "2026-01-02 01:09"),
        params={
            "feature_cols": ["period_indicator", "feature_b"],
            "time_feature_col": "period_indicator",
            "split_accuracy_threshold": 0.9,
        },
    )

    assert result.drift_detected is True
    assert result.measurements["TREE_SPLIT_SIGNAL"]["best_split_feature"] == "period_indicator"
    assert result.measurements["TREE_SPLIT_SIGNAL"]["time_split_count"] == 1
    assert result.test_statistic is not None and result.test_statistic >= 0.9


def test_domain_classifier_tree_detects_feature_shift() -> None:
    x = np.linspace(-1.0, 1.0, 90)
    reference = np.column_stack([x, np.sin(x), np.cos(x)])
    current = np.column_stack([x, np.sin(x) + 3.0, np.cos(x)])
    data = _tree_frame(reference, current, ["feature_a", "feature_b", "feature_c"])

    result = detect_tree_feature(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 01:29"),
        current_window=("2026-01-02 00:00", "2026-01-02 01:29"),
        params={
            "variant_id": "DOMAIN_CLASSIFIER_TREE",
            "feature_cols": ["feature_a", "feature_b", "feature_c"],
            "auc_threshold": 0.8,
        },
    )

    assert result.variant_id == "DOMAIN_CLASSIFIER_TREE"
    assert result.drift_detected is True
    assert result.measurements["ROC_AUC"] >= 0.8
    assert result.measurements["FEATURE_IMPORTANCE_OR_RANK"][0]["feature"] == "feature_b"


def test_domain_classifier_tree_no_drift() -> None:
    x = np.linspace(-1.0, 1.0, 80)
    reference = np.column_stack([x, np.sin(x)])
    current = reference + 0.0001
    data = _tree_frame(reference, current, ["feature_a", "feature_b"])

    result = detect_tree_feature(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 01:19"),
        current_window=("2026-01-02 00:00", "2026-01-02 01:19"),
        params={
            "variant_id": "DOMAIN_CLASSIFIER_TREE",
            "feature_cols": ["feature_a", "feature_b"],
            "auc_threshold": 0.8,
        },
    )

    assert result.drift_detected is False
    assert result.measurements["ROC_AUC"] < 0.8


def test_tree_feature_validation_and_warnings() -> None:
    data = _tree_frame(np.zeros((5, 1)), np.ones((5, 1)), ["feature_a"])
    invalid = detect_tree_feature(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:04"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:04"),
        params={"feature_cols": ["feature_a"], "time_feature_col": "missing_time_feature"},
    )
    assert invalid.severity == "not_applicable"

    dirty = _tree_frame(np.linspace(0.0, 1.0, 25).reshape(-1, 1), np.linspace(0.0, 1.0, 10).reshape(-1, 1), ["feature_a"])
    dirty.loc[0, "feature_a"] = np.nan
    dirty["time"] = dirty["time"].astype(object)
    dirty.loc[1, "time"] = "not-a-time"

    result = detect_tree_feature(
        dirty,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:24"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:09"),
        params={
            "variant_id": "DOMAIN_CLASSIFIER_TREE",
            "feature_cols": ["feature_a"],
            "min_reference_size": 20,
            "min_current_size": 5,
        },
    )

    assert result.severity in {"normal", "drift_detected"}
    assert any("dropped" in warning for warning in result.warnings)
