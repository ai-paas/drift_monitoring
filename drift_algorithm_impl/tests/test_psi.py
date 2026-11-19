from __future__ import annotations

import numpy as np
import pandas as pd

from drift_algorithm.methods.batchdistributioncomparison import detect_psi


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


def test_numeric_binned_psi_no_drift() -> None:
    reference = np.linspace(0, 1, 100)
    current = reference + 0.001
    result = detect_psi(
        _numeric_frame(reference, current),
        reference_window=("2026-01-01 00:00", "2026-01-01 01:39"),
        current_window=("2026-01-02 00:00", "2026-01-02 01:39"),
        params={"bin_count": 5, "threshold": 0.2},
    )
    assert result.variant_id == "NUMERIC_BINNED_PSI"
    assert result.drift_detected is False
    assert result.p_value is None
    assert result.measurements["PSI_SCORE"] <= 0.2


def test_numeric_binned_psi_detects_shift() -> None:
    reference = np.linspace(0, 1, 100)
    current = np.linspace(1, 2, 100)
    result = detect_psi(
        _numeric_frame(reference, current),
        reference_window=("2026-01-01 00:00", "2026-01-01 01:39"),
        current_window=("2026-01-02 00:00", "2026-01-02 01:39"),
        params={"bin_count": 5, "threshold": 0.2},
    )
    assert result.drift_detected is True
    assert result.measurements["DRIFT_ALARM_STATE"] == "drift_detected"
    assert result.measurements["PSI_CONTRIBUTION"][0]["psi_contribution"] > 0


def test_categorical_psi() -> None:
    data = _count_frame({"A": 80, "B": 15, "C": 5}, {"A": 20, "B": 30, "C": 50})
    result = detect_psi(
        data,
        reference_window=("2026-01-01", "2026-01-01 23:59"),
        current_window=("2026-01-02", "2026-01-02 23:59"),
        params={"variant_id": "CATEGORICAL_PSI", "category_col": "category", "count_col": "count", "threshold": 0.2},
    )
    assert result.variant_id == "CATEGORICAL_PSI"
    assert result.drift_detected is True
    assert result.measurements["CATEGORY_COUNT"] == 3


def test_score_band_and_population_weighted_psi() -> None:
    data = _count_frame({"low": 10, "mid": 80, "high": 10}, {"low": 40, "mid": 30, "high": 30})
    data = data.rename(columns={"category": "score_band"})
    score = detect_psi(
        data,
        reference_window=("2026-01-01", "2026-01-01 23:59"),
        current_window=("2026-01-02", "2026-01-02 23:59"),
        params={"variant_id": "SCORE_BAND_PSI", "score_band_col": "score_band", "count_col": "count", "threshold": 0.1},
    )
    weighted = detect_psi(
        data.rename(columns={"score_band": "segment"}),
        reference_window=("2026-01-01", "2026-01-01 23:59"),
        current_window=("2026-01-02", "2026-01-02 23:59"),
        params={"variant_id": "POPULATION_WEIGHTED_PSI", "category_col": "segment", "count_col": "count", "threshold": 0.1},
    )
    assert score.drift_detected is True
    assert weighted.drift_detected is True
    assert weighted.measurements["PSI_SCORE"] == score.measurements["PSI_SCORE"]


def test_psi_validation_and_warnings() -> None:
    constant = _numeric_frame(np.ones(30), np.ones(30))
    invalid = detect_psi(
        constant,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:29"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:29"),
        params={"bin_count": 5},
    )
    assert invalid.severity == "not_applicable"

    dirty = _count_frame({"A": 10, "B": 10, "C": 10}, {"A": 10, "B": 10, "C": 10})
    dirty.loc[0, "count"] = None
    dirty.loc[1, "time"] = "not-a-time"
    result = detect_psi(
        dirty,
        reference_window=("2026-01-01", "2026-01-01 23:59"),
        current_window=("2026-01-02", "2026-01-02 23:59"),
        params={"variant_id": "CATEGORICAL_PSI", "category_col": "category", "count_col": "count"},
    )
    assert result.severity in {"normal", "drift_detected"}
    assert any("dropped" in warning for warning in result.warnings)
