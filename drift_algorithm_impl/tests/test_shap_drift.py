from __future__ import annotations

import numpy as np
import pandas as pd

from drift_algorithm.methods.explanationdriftmethod import detect_shap_drift


def _shap_frame(reference: np.ndarray, current: np.ndarray, columns: list[str]) -> pd.DataFrame:
    ref_time = pd.date_range("2026-01-01 00:00", periods=len(reference), freq="min")
    cur_time = pd.date_range("2026-01-02 00:00", periods=len(current), freq="min")
    data = pd.DataFrame(np.vstack([reference, current]), columns=columns)
    data.insert(0, "time", list(ref_time) + list(cur_time))
    return data


def test_shap_distribution_no_drift() -> None:
    x = np.linspace(-0.5, 0.5, 80)
    reference = np.column_stack([x, x * 0.5, np.sin(x)])
    current = reference + 0.0001
    data = _shap_frame(reference, current, ["shap_a", "shap_b", "shap_c"])

    result = detect_shap_drift(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 01:19"),
        current_window=("2026-01-02 00:00", "2026-01-02 01:19"),
        params={"shap_cols": ["shap_a", "shap_b", "shap_c"], "alpha": 0.01},
    )

    assert result.variant_id == "SHAP_VALUE_DISTRIBUTION_TEST"
    assert result.drift_detected is False
    assert result.measurements["SHAP_DRIFT_DISTANCE"] >= 0.0
    assert result.p_value is not None and result.p_value > 0.01
    assert result.measurements["FEATURE_IMPORTANCE_OR_RANK"][0]["feature"] in {"shap_a", "shap_b", "shap_c"}


def test_shap_distribution_detects_feature_shift() -> None:
    x = np.linspace(-0.5, 0.5, 90)
    reference = np.column_stack([x, x * 0.5, np.sin(x)])
    current = np.column_stack([x + 2.0, x * 0.5, np.sin(x)])
    data = _shap_frame(reference, current, ["shap_a", "shap_b", "shap_c"])

    result = detect_shap_drift(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 01:29"),
        current_window=("2026-01-02 00:00", "2026-01-02 01:29"),
        params={"shap_cols": ["shap_a", "shap_b", "shap_c"], "alpha": 0.05},
    )

    assert result.drift_detected is True
    assert result.p_value is not None and result.p_value < 0.05
    assert result.measurements["FEATURE_IMPORTANCE_OR_RANK"][0]["feature"] == "shap_a"
    assert "shap_a" in result.measurements["SIGNIFICANT_FEATURES"]


def test_global_importance_rank_shift() -> None:
    reference = np.tile(np.array([[3.0, 1.0, 0.2]]), (60, 1))
    current = np.tile(np.array([[0.2, 1.0, 3.0]]), (60, 1))
    data = _shap_frame(reference, current, ["shap_a", "shap_b", "shap_c"])

    result = detect_shap_drift(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:59"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:59"),
        params={
            "variant_id": "GLOBAL_IMPORTANCE_RANK_SHIFT",
            "shap_cols": ["shap_a", "shap_b", "shap_c"],
            "rank_shift_threshold": 0.4,
        },
    )

    assert result.variant_id == "GLOBAL_IMPORTANCE_RANK_SHIFT"
    assert result.drift_detected is True
    assert result.p_value is None
    assert result.measurements["METHOD_POLICY"] == "mean_normalized_absolute_rank_delta"
    assert result.measurements["FEATURE_IMPORTANCE_OR_RANK"][0]["score"] >= 1.0


def test_class_conditional_shap_drift() -> None:
    x = np.linspace(-0.5, 0.5, 80)
    reference = np.column_stack([x, x * 0.25])
    current = np.column_stack([x, x * 0.25])
    current[40:, 1] += 2.0
    data = _shap_frame(reference, current, ["shap_a", "shap_b"])
    data["class"] = ["A"] * 40 + ["B"] * 40 + ["A"] * 40 + ["B"] * 40

    result = detect_shap_drift(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 01:19"),
        current_window=("2026-01-02 00:00", "2026-01-02 01:19"),
        params={
            "variant_id": "CLASS_CONDITIONAL_SHAP_DRIFT",
            "shap_cols": ["shap_a", "shap_b"],
            "class_col": "class",
            "alpha": 0.05,
            "min_class_size": 10,
        },
    )

    assert result.drift_detected is True
    assert result.measurements["CLASS_SHAP_DRIFT_DISTANCE"]["B"]["min_p_value"] < 0.05
    assert "B:shap_b" in result.measurements["SIGNIFICANT_FEATURES"]


def test_shap_validation_and_warnings() -> None:
    data = _shap_frame(np.zeros((5, 1)), np.ones((5, 1)), ["shap_a"])
    invalid = detect_shap_drift(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:04"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:04"),
        params={"variant_id": "CLASS_CONDITIONAL_SHAP_DRIFT", "shap_cols": ["shap_a"]},
    )
    assert invalid.severity == "not_applicable"

    dirty = _shap_frame(np.linspace(0.0, 1.0, 25).reshape(-1, 1), np.linspace(0.0, 1.0, 10).reshape(-1, 1), ["shap_a"])
    dirty.loc[0, "shap_a"] = np.nan
    dirty["time"] = dirty["time"].astype(object)
    dirty.loc[1, "time"] = "not-a-time"

    result = detect_shap_drift(
        dirty,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:24"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:09"),
        params={"shap_cols": ["shap_a"], "min_reference_size": 20, "min_current_size": 5},
    )

    assert result.severity in {"normal", "drift_detected"}
    assert any("dropped" in warning for warning in result.warnings)
