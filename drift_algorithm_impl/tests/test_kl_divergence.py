from __future__ import annotations

import numpy as np
import pandas as pd

from drift_algorithm.methods.batchdistributioncomparison import detect_kl_divergence


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


def test_discrete_kl_no_drift() -> None:
    data = _count_frame({"A": 45, "B": 35, "C": 20}, {"A": 44, "B": 36, "C": 20})
    result = detect_kl_divergence(
        data,
        reference_window=("2026-01-01", "2026-01-01 23:59"),
        current_window=("2026-01-02", "2026-01-02 23:59"),
        params={"category_col": "category", "count_col": "count", "threshold": 0.1},
    )
    assert result.method_id == "DM-007"
    assert result.variant_id == "DISCRETE_KL_DIVERGENCE"
    assert result.drift_detected is False
    assert result.p_value is None
    assert result.measurements["KL_DIVERGENCE"] <= 0.1


def test_discrete_kl_detects_shift() -> None:
    data = _count_frame({"A": 80, "B": 15, "C": 5}, {"A": 20, "B": 30, "C": 50})
    result = detect_kl_divergence(
        data,
        reference_window=("2026-01-01", "2026-01-01 23:59"),
        current_window=("2026-01-02", "2026-01-02 23:59"),
        params={"category_col": "category", "count_col": "count", "threshold": 0.1},
    )
    assert result.drift_detected is True
    assert result.measurements["DRIFT_ALARM_STATE"] == "drift_detected"
    assert result.measurements["KL_CURRENT_REFERENCE"] > 0.1
    assert result.measurements["KL_CONTRIBUTION"][0]["category"] in {"A", "C"}


def test_histogram_kl_detects_numeric_shift() -> None:
    reference = np.linspace(0, 1, 100)
    current = np.linspace(1, 2, 100)
    result = detect_kl_divergence(
        _numeric_frame(reference, current),
        reference_window=("2026-01-01 00:00", "2026-01-01 01:39"),
        current_window=("2026-01-02 00:00", "2026-01-02 01:39"),
        params={"variant_id": "HISTOGRAM_KL_DIVERGENCE", "bin_count": 5, "threshold": 0.1},
    )
    assert result.variant_id == "HISTOGRAM_KL_DIVERGENCE"
    assert result.drift_detected is True
    assert result.measurements["CATEGORY_COUNT"] == 5


def test_smoothed_and_symmetrized_kl_variants() -> None:
    data = _count_frame({"A": 50, "B": 50}, {"A": 99, "B": 1})
    smoothed = detect_kl_divergence(
        data,
        reference_window=("2026-01-01", "2026-01-01 23:59"),
        current_window=("2026-01-02", "2026-01-02 23:59"),
        params={"variant_id": "SMOOTHED_KL_DIVERGENCE", "category_col": "category", "count_col": "count", "threshold": 0.1},
    )
    symmetrized = detect_kl_divergence(
        data,
        reference_window=("2026-01-01", "2026-01-01 23:59"),
        current_window=("2026-01-02", "2026-01-02 23:59"),
        params={"variant_id": "SYMMETRIZED_KL", "category_col": "category", "count_col": "count", "threshold": 0.1},
    )
    assert smoothed.drift_detected is True
    assert any("epsilon" in warning for warning in smoothed.warnings)
    assert symmetrized.measurements["KL_DIVERGENCE"] == 0.5 * (
        symmetrized.measurements["KL_CURRENT_REFERENCE"] + symmetrized.measurements["KL_REFERENCE_CURRENT"]
    )


def test_kl_validation_and_warnings() -> None:
    invalid = detect_kl_divergence(
        pd.DataFrame({"time": ["2026-01-01"], "other": ["A"]}),
        reference_window=("2026-01-01", "2026-01-01 23:59"),
        current_window=("2026-01-02", "2026-01-02 23:59"),
        params={"category_col": "category"},
    )
    assert invalid.severity == "not_applicable"

    dirty = _count_frame({"A": 10, "B": 10, "C": 10}, {"A": 10, "B": 10, "C": 10})
    dirty.loc[0, "count"] = None
    dirty.loc[1, "time"] = "not-a-time"
    result = detect_kl_divergence(
        dirty,
        reference_window=("2026-01-01", "2026-01-01 23:59"),
        current_window=("2026-01-02", "2026-01-02 23:59"),
        params={"category_col": "category", "count_col": "count"},
    )
    assert result.severity in {"normal", "drift_detected"}
    assert any("dropped" in warning for warning in result.warnings)
