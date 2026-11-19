from __future__ import annotations

import numpy as np
import pandas as pd

from drift_algorithm.methods.batchdistributioncomparison import detect_l_infinity_distance


def _numeric_frame(reference: np.ndarray, current: np.ndarray) -> pd.DataFrame:
    ref_time = pd.date_range("2026-01-01 00:00", periods=len(reference), freq="min")
    cur_time = pd.date_range("2026-01-02 00:00", periods=len(current), freq="min")
    return pd.DataFrame({"time": list(ref_time) + list(cur_time), "value": list(reference) + list(current)})


def _count_frame(reference: dict[str, int], current: dict[str, int]) -> pd.DataFrame:
    rows = []
    for category, count in reference.items():
        rows.append({"time": "2026-01-01 00:00", "category": category, "count": count})
    for category, count in current.items():
        rows.append({"time": "2026-01-02 00:00", "category": category, "count": count})
    return pd.DataFrame(rows)


def test_categorical_l_infinity_no_drift() -> None:
    data = _count_frame({"A": 45, "B": 35, "C": 20}, {"A": 44, "B": 36, "C": 20})
    result = detect_l_infinity_distance(
        data,
        reference_window=("2026-01-01", "2026-01-01 23:59"),
        current_window=("2026-01-02", "2026-01-02 23:59"),
        params={"category_col": "category", "count_col": "count", "threshold": 0.1},
    )
    assert result.method_id == "DM-011"
    assert result.variant_id == "CATEGORICAL_L_INFINITY"
    assert result.drift_detected is False
    assert result.p_value is None
    assert result.measurements["L_INFINITY_DISTANCE"] <= 0.1


def test_categorical_l_infinity_detects_max_component_shift() -> None:
    data = _count_frame({"A": 80, "B": 15, "C": 5}, {"A": 20, "B": 30, "C": 50})
    result = detect_l_infinity_distance(
        data,
        reference_window=("2026-01-01", "2026-01-01 23:59"),
        current_window=("2026-01-02", "2026-01-02 23:59"),
        params={"category_col": "category", "count_col": "count", "threshold": 0.2},
    )
    assert result.drift_detected is True
    assert result.measurements["DRIFT_ALARM_STATE"] == "drift_detected"
    assert np.isclose(result.measurements["L_INFINITY_DISTANCE"], 0.6)
    assert result.measurements["MAX_COMPONENT"]["category"] == "A"
    assert result.measurements["L_INFINITY_CONTRIBUTION"][0]["is_max_component"] is True


def test_probability_vector_l_infinity_uses_probability_contract() -> None:
    data = _count_frame({"class_a": 70, "class_b": 30}, {"class_a": 40, "class_b": 60})
    result = detect_l_infinity_distance(
        data,
        reference_window=("2026-01-01", "2026-01-01 23:59"),
        current_window=("2026-01-02", "2026-01-02 23:59"),
        params={
            "variant_id": "PROBABILITY_VECTOR_L_INFINITY",
            "category_col": "category",
            "count_col": "count",
            "threshold": 0.2,
        },
    )
    assert result.drift_detected is True
    assert np.isclose(result.measurements["MAX_ABSOLUTE_PROPORTION_DELTA"], 0.3)
    assert any("probability vector contract" in warning for warning in result.warnings)


def test_binned_numeric_l_infinity_detects_shift() -> None:
    reference = np.linspace(0, 1, 100)
    current = np.linspace(1, 2, 100)
    result = detect_l_infinity_distance(
        _numeric_frame(reference, current),
        reference_window=("2026-01-01 00:00", "2026-01-01 01:39"),
        current_window=("2026-01-02 00:00", "2026-01-02 01:39"),
        params={"variant_id": "BINNED_NUMERIC_L_INFINITY", "bin_count": 5, "threshold": 0.1},
    )
    assert result.variant_id == "BINNED_NUMERIC_L_INFINITY"
    assert result.drift_detected is True
    assert result.measurements["CATEGORY_COUNT"] == 5
    assert result.measurements["MAX_COMPONENT"]["category"].startswith("bin_")


def test_l_infinity_validation_and_warnings() -> None:
    invalid = detect_l_infinity_distance(
        pd.DataFrame({"time": ["2026-01-01"], "other": ["A"]}),
        reference_window=("2026-01-01", "2026-01-01 23:59"),
        current_window=("2026-01-02", "2026-01-02 23:59"),
        params={"category_col": "category"},
    )
    assert invalid.severity == "not_applicable"

    dirty = _count_frame({"A": 10, "B": 10, "C": 10}, {"A": 10, "B": 10, "C": 10})
    dirty.loc[0, "count"] = None
    dirty.loc[1, "time"] = "not-a-time"
    result = detect_l_infinity_distance(
        dirty,
        reference_window=("2026-01-01", "2026-01-01 23:59"),
        current_window=("2026-01-02", "2026-01-02 23:59"),
        params={"category_col": "category", "count_col": "count"},
    )
    assert result.severity in {"normal", "drift_detected"}
    assert any("dropped" in warning for warning in result.warnings)
