from __future__ import annotations

import numpy as np
import pandas as pd

from drift_algorithm.methods.streamingchangedetector import detect_bocd


def _frame(reference: np.ndarray, current: np.ndarray) -> pd.DataFrame:
    ref_time = pd.date_range("2026-01-01 00:00", periods=len(reference), freq="min")
    cur_time = pd.date_range("2026-01-02 00:00", periods=len(current), freq="min")
    return pd.DataFrame({"time": list(ref_time) + list(cur_time), "value": list(reference) + list(current)})


def test_bocd_default_no_alarm_finite_replay() -> None:
    rng = np.random.default_rng(970)
    data = _frame(rng.normal(0.0, 0.15, 80), rng.normal(0.02, 0.15, 80))
    result = detect_bocd(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 01:19"),
        current_window=("2026-01-02 00:00", "2026-01-02 01:19"),
        params={
            "change_probability_threshold": 0.9,
            "hazard_rate": 0.02,
            "warmup_size": 30,
            "run_length_truncation": 120,
        },
    )
    assert result.variant_id == "BAYESIAN_ONLINE_CHANGE_POINT_GAUSSIAN"
    assert result.p_value is None
    assert result.measurements["P_VALUE"] is None
    assert result.drift_detected is False
    assert result.severity == "normal"
    assert result.measurements["DRIFT_ALARM_STATE"] == "normal"
    assert result.measurements["TEST_STATISTIC"] == result.test_statistic
    assert result.measurements["MAX_CHANGE_POINT_PROBABILITY"] == result.test_statistic
    assert result.measurements["PROCESSED_COUNT"] == 160


def test_bocd_gaussian_mean_shift_alarm() -> None:
    rng = np.random.default_rng(971)
    data = _frame(rng.normal(0.0, 0.08, 80), rng.normal(1.2, 0.08, 80))
    result = detect_bocd(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 01:19"),
        current_window=("2026-01-02 00:00", "2026-01-02 01:19"),
        params={
            "change_probability_threshold": 0.25,
            "hazard_rate": 0.05,
            "warmup_size": 30,
            "run_length_truncation": 120,
        },
    )
    assert result.drift_detected is True
    assert result.severity == "drift_detected"
    assert result.threshold == 0.25
    assert result.measurements["ALARM_COUNT"] > 0
    assert result.measurements["FIRST_ALARM_TIME"] is not None
    assert result.measurements["FIRST_ALARM_TYPE"] == "change_probability"
    assert len(result.measurements["ALARM_EVENTS"]) <= 50


def test_bocd_hazard_and_predictive_probability_variants() -> None:
    rng = np.random.default_rng(972)
    data = _frame(rng.normal(0.0, 0.1, 70), rng.normal(0.9, 0.1, 70))
    hazard = detect_bocd(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 01:09"),
        current_window=("2026-01-02 00:00", "2026-01-02 01:09"),
        params={
            "variant_id": "BOCD_HAZARD_RATE_VARIANT",
            "expected_run_length": 20,
            "threshold_or_alpha": 0.2,
            "warmup_size": 25,
        },
    )
    assert hazard.variant_id == "BOCD_HAZARD_RATE_VARIANT"
    assert np.isclose(hazard.measurements["HAZARD_RATE"], 0.05)
    assert hazard.threshold == 0.2
    assert any("threshold_or_alpha" in warning for warning in hazard.warnings)

    predictive = detect_bocd(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 01:09"),
        current_window=("2026-01-02 00:00", "2026-01-02 01:09"),
        params={
            "variant_id": "BOCD_PREDICTIVE_PROBABILITY",
            "change_probability_threshold": 0.95,
            "predictive_probability_threshold": 0.01,
            "hazard_rate": 0.02,
            "warmup_size": 25,
        },
    )
    assert predictive.variant_id == "BOCD_PREDICTIVE_PROBABILITY"
    assert predictive.measurements["PREDICTIVE_PROBABILITY_THRESHOLD"] == 0.01
    assert predictive.measurements["MIN_PREDICTIVE_PROBABILITY"] is not None
    assert predictive.measurements["LAST_PREDICTIVE_PROBABILITY"] is not None


def test_bocd_schema_window_warning_and_validation() -> None:
    bool_data = _frame(np.ones(30), np.ones(30))
    bool_data["value"] = True
    bool_result = detect_bocd(
        bool_data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:29"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:29"),
    )
    assert bool_result.severity == "not_applicable"

    small = detect_bocd(
        _frame(np.arange(10, dtype=float), np.arange(10, dtype=float)),
        reference_window=("2026-01-01 00:00", "2026-01-01 00:09"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:09"),
    )
    assert small.severity == "not_applicable"

    invalid = detect_bocd(
        _frame(np.zeros(30), np.ones(30)),
        reference_window=("2026-01-01 00:00", "2026-01-01 00:29"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:29"),
        params={"hazard_rate": 1.5},
    )
    assert invalid.severity == "not_applicable"

    warning_data = _frame(np.arange(40, dtype=float), np.arange(20, dtype=float) + 2)
    warning_data["time"] = warning_data["time"].astype(object)
    warning_data.loc[0, "value"] = np.nan
    warning_data.loc[1, "time"] = "not-a-time"
    result = detect_bocd(
        warning_data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:39"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:19"),
        params={
            "min_reference_size": 20,
            "min_current_size": 20,
            "sample_imbalance_warning_ratio": 1.5,
            "change_probability_threshold": 0.99,
        },
    )
    assert result.severity in {"normal", "drift_detected"}
    assert any("dropped" in warning for warning in result.warnings)
    assert any("imbalanced" in warning for warning in result.warnings)


def test_bocd_non_scalar_requests() -> None:
    data = _frame(np.zeros(30), np.ones(30))
    feature_request = detect_bocd(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:29"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:29"),
        params={"feature_cols": ["a", "b"]},
    )
    assert feature_request.severity == "not_applicable"
