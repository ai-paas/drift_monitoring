from __future__ import annotations

import numpy as np
import pandas as pd

from drift_algorithm.methods.streamingchangedetector import detect_ewma, detect_geometric_moving_average


def _frame(reference: np.ndarray, current: np.ndarray) -> pd.DataFrame:
    ref_time = pd.date_range("2026-01-01 00:00", periods=len(reference), freq="min")
    cur_time = pd.date_range("2026-01-02 00:00", periods=len(current), freq="min")
    return pd.DataFrame({"time": list(ref_time) + list(cur_time), "value": list(reference) + list(current)})


def test_ewma_default_no_alarm_finite_replay() -> None:
    rng = np.random.default_rng(940)
    data = _frame(rng.normal(0.0, 0.02, 60), rng.normal(0.0, 0.02, 60))
    result = detect_ewma(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:59"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:59"),
        params={"center_line": 0.0, "sigma": 1.0, "control_width": 5.0, "warmup_size": 20},
    )
    assert result.variant_id == "EWMA_UNIVARIATE_CONTROL_CHART"
    assert result.p_value is None
    assert result.drift_detected is False
    assert result.severity == "normal"
    assert result.threshold is None
    assert result.measurements["DRIFT_ALARM_STATE"] == "normal"
    assert result.measurements["EWMA_VALUE"] == result.test_statistic
    assert result.measurements["CONTROL_LIMIT"]["mode"] == "two_sided"
    assert result.measurements["PROCESSED_COUNT"] == 120


def test_ewma_two_sided_upper_and_lower_alarm() -> None:
    rng = np.random.default_rng(941)
    upper_data = _frame(rng.normal(0.0, 0.02, 60), rng.normal(1.0, 0.02, 60))
    upper = detect_ewma(
        upper_data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:59"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:59"),
        params={"center_line": 0.0, "sigma": 0.1, "lambda": 0.3, "control_width": 3.0, "warmup_size": 20},
    )
    assert upper.drift_detected is True
    assert upper.severity == "drift_detected"
    assert upper.measurements["FIRST_ALARM_DIRECTION"] == "upper"
    assert len(upper.measurements["ALARM_EVENTS"]) <= 50

    lower_data = _frame(rng.normal(0.0, 0.02, 60), rng.normal(-1.0, 0.02, 60))
    lower = detect_ewma(
        lower_data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:59"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:59"),
        params={"center_line": 0.0, "sigma": 0.1, "lambda": 0.3, "control_width": 3.0, "warmup_size": 20},
    )
    assert lower.drift_detected is True
    assert lower.measurements["FIRST_ALARM_DIRECTION"] == "lower"


def test_ewma_one_sided_routing_and_threshold() -> None:
    rng = np.random.default_rng(942)
    data = _frame(rng.normal(0.0, 0.02, 60), rng.normal(0.8, 0.02, 60))
    result = detect_ewma(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:59"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:59"),
        params={"variant_id": "EWMA_ONE_SIDED", "direction": "increase", "lambda": 0.3, "threshold": 0.2},
    )
    assert result.threshold == 0.2
    assert result.measurements["DIRECTION"] == "increase"
    assert result.measurements["CONTROL_LIMIT"]["mode"] == "upper"
    assert result.measurements["LCL"] is None
    assert result.drift_detected is True
    assert result.measurements["FIRST_ALARM_DIRECTION"] == "upper"

    wrong_direction = detect_ewma(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:59"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:59"),
        params={"variant_id": "EWMA_UNIVARIATE_CONTROL_CHART", "direction": "increase"},
    )
    assert wrong_direction.severity == "not_applicable"


def test_ewma_alias_inferred_calibration_and_validation() -> None:
    data = _frame(np.zeros(40), np.ones(40))
    inferred = detect_ewma(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:39"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:39"),
        params={"threshold_or_alpha": 2.0, "sigma": 1.0, "record_events": False},
    )
    assert inferred.measurements["CONTROL_WIDTH"] == 2.0
    assert "ALARM_EVENTS" not in inferred.measurements
    assert any("center_line was inferred" in warning for warning in inferred.warnings)
    assert any("threshold_or_alpha" in warning for warning in inferred.warnings)

    invalid_lambda = detect_ewma(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:39"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:39"),
        params={"lambda": 0},
    )
    assert invalid_lambda.severity == "not_applicable"

    invalid_limit = detect_ewma(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:39"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:39"),
        params={"ucl": 0.0, "lcl": 1.0},
    )
    assert invalid_limit.severity == "not_applicable"


def test_ewma_schema_window_warning_and_deferred_requests() -> None:
    bool_data = _frame(np.ones(30), np.ones(30))
    bool_data["value"] = True
    bool_result = detect_ewma(
        bool_data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:29"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:29"),
    )
    assert bool_result.severity == "not_applicable"

    small = detect_ewma(
        _frame(np.arange(10, dtype=float), np.arange(10, dtype=float)),
        reference_window=("2026-01-01 00:00", "2026-01-01 00:09"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:09"),
        params={"warmup_size": 30},
    )
    assert small.severity == "not_applicable"

    baseline_replay = detect_ewma(
        _frame(np.zeros(30), np.ones(30)),
        reference_window=("2026-01-01 00:00", "2026-01-01 00:29"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:29"),
        params={
            "variant_id": "EWMA_BASELINE_REPLAY_THRESHOLD",
            "center_line": 0.0,
            "sigma": 0.1,
            "threshold": 0.2,
            "warmup_size": 1,
        },
    )
    assert baseline_replay.drift_detected is True
    assert baseline_replay.measurements["DIRECTION"] == "increase"

    gma_empirical = detect_geometric_moving_average(
        _frame(np.zeros(30), np.ones(30)),
        reference_window=("2026-01-01 00:00", "2026-01-01 00:29"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:29"),
        params={
            "variant_id": "GMA_WITH_EMPIRICAL_LIMIT",
            "center_line": 0.0,
            "sigma": 0.1,
            "control_limit": 0.2,
            "warmup_size": 1,
        },
    )
    assert gma_empirical.drift_detected is True
    assert gma_empirical.measurements["DIRECTION"] == "increase"

    warning_data = _frame(np.arange(40, dtype=float), np.arange(20, dtype=float) + 2)
    warning_data["time"] = warning_data["time"].astype(object)
    warning_data.loc[0, "value"] = np.nan
    warning_data.loc[1, "time"] = "not-a-time"
    result = detect_ewma(
        warning_data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:39"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:19"),
        params={
            "sigma": 10.0,
            "min_reference_size": 20,
            "min_current_size": 20,
            "sample_imbalance_warning_ratio": 1.5,
            "check_every": 2,
        },
    )
    assert result.severity in {"normal", "drift_detected"}
    assert any("dropped" in warning for warning in result.warnings)
    assert any("imbalanced" in warning for warning in result.warnings)
    assert any("check_every > 1" in warning for warning in result.warnings)


def test_ewma_non_scalar_requests() -> None:
    data = _frame(np.zeros(30), np.ones(30))
    feature_request = detect_ewma(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:29"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:29"),
        params={"feature_cols": ["a", "b"]},
    )
    assert feature_request.severity == "not_applicable"
