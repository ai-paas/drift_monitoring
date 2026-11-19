from __future__ import annotations

import numpy as np
import pandas as pd

from drift_algorithm.methods.operationaladaptationmethod import detect_driftretrainingclassifier


def _metric_frame(reference: np.ndarray, current: np.ndarray) -> pd.DataFrame:
    ref_time = pd.date_range("2026-01-01 00:00", periods=len(reference), freq="min")
    cur_time = pd.date_range("2026-01-02 00:00", periods=len(current), freq="min")
    return pd.DataFrame({"time": list(ref_time) + list(cur_time), "error": list(reference) + list(current)})


def test_drift_retraining_adwin_no_retraining() -> None:
    reference = np.zeros(100)
    current = np.zeros(100)
    reference[::10] = 1
    current[::10] = 1
    data = _metric_frame(reference, current)

    result = detect_driftretrainingclassifier(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 01:39"),
        current_window=("2026-01-02 00:00", "2026-01-02 01:39"),
        params={"metric_col": "error", "threshold": 0.2, "warning_threshold": 0.1},
    )

    assert result.variant_id == "DRIFT_RETRAINING_WITH_ADWIN"
    assert result.drift_detected is False
    assert result.measurements["DRIFT_ALARM_STATE"] == "normal"
    assert result.measurements["RETRAINING_EVENT"]["retraining_recommended"] is False


def test_drift_retraining_adwin_recommends_retraining() -> None:
    reference = np.zeros(100)
    reference[::20] = 1
    current = np.r_[np.zeros(40), np.ones(60)]
    data = _metric_frame(reference, current)
    data["retraining_triggered"] = 0
    data.loc[130, "retraining_triggered"] = 1

    result = detect_driftretrainingclassifier(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 01:39"),
        current_window=("2026-01-02 00:00", "2026-01-02 01:39"),
        params={"metric_col": "error", "threshold": 0.2, "warning_threshold": 0.1},
    )

    assert result.drift_detected is True
    assert result.measurements["RETRAINING_EVENT"]["retraining_triggered_count"] == 1
    assert result.measurements["METRIC_MEAN_DELTA"] > 0


def test_drift_retraining_page_hinkley() -> None:
    reference = np.full(100, 0.05)
    current = np.linspace(0.08, 0.35, 100)
    data = _metric_frame(reference, current)

    result = detect_driftretrainingclassifier(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 01:39"),
        current_window=("2026-01-02 00:00", "2026-01-02 01:39"),
        params={
            "variant_id": "DRIFT_RETRAINING_WITH_PAGE_HINKLEY",
            "metric_col": "error",
            "threshold": 2.0,
            "warning_threshold": 1.0,
            "delta": 0.0,
        },
    )

    assert result.variant_id == "DRIFT_RETRAINING_WITH_PAGE_HINKLEY"
    assert result.drift_detected is True
    assert result.measurements["TEST_STATISTIC"] >= 2.0
    assert result.measurements["RETRAINING_CANDIDATE_WINDOW"]["sample_size"] == 100


def test_drift_retraining_champion_challenger() -> None:
    reference = np.full(90, 0.2)
    current = np.full(90, 0.25)
    data = _metric_frame(reference, current)
    data["champion_metric"] = list(np.repeat(0.2, 90)) + list(np.repeat(0.30, 90))
    data["challenger_metric"] = list(np.repeat(0.2, 90)) + list(np.repeat(0.20, 90))
    data["model_promoted"] = 0
    data.loc[150, "model_promoted"] = 1

    result = detect_driftretrainingclassifier(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 01:29"),
        current_window=("2026-01-02 00:00", "2026-01-02 01:29"),
        params={
            "variant_id": "DRIFT_RETRAINING_CHAMPION_CHALLENGER",
            "metric_col": "error",
            "metric_direction": "higher_is_worse",
            "uplift_threshold": 0.05,
            "warning_threshold": 0.02,
        },
    )

    assert result.variant_id == "DRIFT_RETRAINING_CHAMPION_CHALLENGER"
    assert result.drift_detected is True
    assert result.measurements["PROMOTION_DECISION"]["promotion_recommended"] is True
    assert result.measurements["PROMOTION_DECISION"]["promoted"] is True
    assert result.measurements["CHAMPION_CHALLENGER_UPLIFT"] >= 0.05


def test_drift_retraining_validation_and_warnings() -> None:
    data = _metric_frame(np.zeros(30), np.ones(30))
    invalid = detect_driftretrainingclassifier(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:29"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:29"),
        params={"metric_col": "missing"},
    )
    assert invalid.severity == "not_applicable"

    dirty = _metric_frame(np.zeros(40), np.r_[np.zeros(20), np.ones(20)])
    dirty["time"] = dirty["time"].astype(object)
    dirty.loc[0, "error"] = np.nan
    dirty.loc[1, "time"] = "not-a-time"
    result = detect_driftretrainingclassifier(
        dirty,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:39"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:39"),
        params={"metric_col": "error", "min_reference_size": 20, "min_current_size": 20},
    )

    assert result.severity in {"normal", "warning", "drift_detected"}
    assert any("dropped" in warning for warning in result.warnings)
