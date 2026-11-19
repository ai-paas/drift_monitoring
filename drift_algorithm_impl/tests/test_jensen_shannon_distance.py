from __future__ import annotations

import numpy as np
import pandas as pd

from drift_algorithm.methods.batchdistributioncomparison import detect_jensen_shannon_distance


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


def test_js_divergence_no_drift() -> None:
    data = _count_frame({"A": 45, "B": 35, "C": 20}, {"A": 44, "B": 36, "C": 20})
    result = detect_jensen_shannon_distance(
        data,
        reference_window=("2026-01-01", "2026-01-01 23:59"),
        current_window=("2026-01-02", "2026-01-02 23:59"),
        params={"category_col": "category", "count_col": "count", "threshold": 0.1},
    )
    assert result.method_id == "DM-008"
    assert result.variant_id == "JENSEN_SHANNON_DIVERGENCE"
    assert result.drift_detected is False
    assert result.p_value is None
    assert result.measurements["JENSEN_SHANNON_DIVERGENCE"] <= 0.1


def test_js_divergence_detects_shift() -> None:
    data = _count_frame({"A": 80, "B": 15, "C": 5}, {"A": 20, "B": 30, "C": 50})
    result = detect_jensen_shannon_distance(
        data,
        reference_window=("2026-01-01", "2026-01-01 23:59"),
        current_window=("2026-01-02", "2026-01-02 23:59"),
        params={"category_col": "category", "count_col": "count", "threshold": 0.1},
    )
    assert result.drift_detected is True
    assert result.measurements["DRIFT_ALARM_STATE"] == "drift_detected"
    assert result.measurements["JENSEN_SHANNON_DIVERGENCE"] > 0.1
    assert result.measurements["JENSEN_SHANNON_CONTRIBUTION"][0]["category"] in {"A", "C"}


def test_js_distance_uses_distance_scale_for_alarm() -> None:
    data = _count_frame({"A": 90, "B": 10}, {"A": 55, "B": 45})
    result = detect_jensen_shannon_distance(
        data,
        reference_window=("2026-01-01", "2026-01-01 23:59"),
        current_window=("2026-01-02", "2026-01-02 23:59"),
        params={"variant_id": "JENSEN_SHANNON_DISTANCE", "category_col": "category", "count_col": "count", "threshold": 0.25},
    )
    assert result.drift_score == result.measurements["JENSEN_SHANNON_DISTANCE"]
    assert result.measurements["JENSEN_SHANNON_DISTANCE"] == np.sqrt(result.measurements["JENSEN_SHANNON_DIVERGENCE"])
    assert result.drift_detected is True


def test_numeric_histogram_js_distance_detects_shift() -> None:
    reference = np.linspace(0, 1, 100)
    current = np.linspace(1, 2, 100)
    divergence = detect_jensen_shannon_distance(
        _numeric_frame(reference, current),
        reference_window=("2026-01-01 00:00", "2026-01-01 01:39"),
        current_window=("2026-01-02 00:00", "2026-01-02 01:39"),
        params={
            "variant_id": "JENSEN_SHANNON_DIVERGENCE",
            "input_mode": "numeric_histogram",
            "bin_count": 5,
            "threshold": 0.1,
        },
    )
    distance = detect_jensen_shannon_distance(
        _numeric_frame(reference, current),
        reference_window=("2026-01-01 00:00", "2026-01-01 01:39"),
        current_window=("2026-01-02 00:00", "2026-01-02 01:39"),
        params={
            "variant_id": "JENSEN_SHANNON_DISTANCE",
            "input_mode": "numeric_histogram",
            "bin_count": 5,
            "threshold": 0.1,
        },
    )
    assert divergence.variant_id == "JENSEN_SHANNON_DIVERGENCE"
    assert divergence.drift_detected is True
    assert divergence.measurements["CATEGORY_COUNT"] == 5
    assert distance.variant_id == "JENSEN_SHANNON_DISTANCE"
    assert distance.drift_detected is True
    assert distance.measurements["CATEGORY_COUNT"] == 5


def test_multiclass_and_text_topic_variants_use_probability_contract() -> None:
    data = _count_frame({"class_a": 70, "class_b": 30}, {"class_a": 40, "class_b": 60})
    multiclass = detect_jensen_shannon_distance(
        data,
        reference_window=("2026-01-01", "2026-01-01 23:59"),
        current_window=("2026-01-02", "2026-01-02 23:59"),
        params={"variant_id": "MULTICLASS_PROBABILITY_JS", "category_col": "category", "count_col": "count", "threshold": 0.02},
    )
    text_topic = detect_jensen_shannon_distance(
        data,
        reference_window=("2026-01-01", "2026-01-01 23:59"),
        current_window=("2026-01-02", "2026-01-02 23:59"),
        params={"variant_id": "TEXT_TOPIC_JS", "category_col": "category", "count_col": "count", "threshold": 0.02},
    )
    assert multiclass.drift_detected is True
    assert text_topic.drift_detected is True
    assert any("probability distribution contract" in warning for warning in multiclass.warnings)
    assert any("probability distribution contract" in warning for warning in text_topic.warnings)


def test_js_validation_and_warnings() -> None:
    invalid = detect_jensen_shannon_distance(
        pd.DataFrame({"time": ["2026-01-01"], "other": ["A"]}),
        reference_window=("2026-01-01", "2026-01-01 23:59"),
        current_window=("2026-01-02", "2026-01-02 23:59"),
        params={"category_col": "category"},
    )
    assert invalid.severity == "not_applicable"

    dirty = _count_frame({"A": 10, "B": 10, "C": 10}, {"A": 10, "B": 10, "C": 10})
    dirty.loc[0, "count"] = None
    dirty.loc[1, "time"] = "not-a-time"
    result = detect_jensen_shannon_distance(
        dirty,
        reference_window=("2026-01-01", "2026-01-01 23:59"),
        current_window=("2026-01-02", "2026-01-02 23:59"),
        params={"category_col": "category", "count_col": "count"},
    )
    assert result.severity in {"normal", "drift_detected"}
    assert any("dropped" in warning for warning in result.warnings)
