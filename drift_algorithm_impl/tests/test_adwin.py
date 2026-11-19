from __future__ import annotations

import numpy as np
import pandas as pd

from drift_algorithm.methods.streamingchangedetector import detect_adwin


def _frame(reference: np.ndarray, current: np.ndarray) -> pd.DataFrame:
    ref_time = pd.date_range("2026-01-01 00:00", periods=len(reference), freq="min")
    cur_time = pd.date_range("2026-01-02 00:00", periods=len(current), freq="min")
    return pd.DataFrame({"time": list(ref_time) + list(cur_time), "value": list(reference) + list(current)})


def test_adwin_default_no_alarm_finite_replay() -> None:
    rng = np.random.default_rng(900)
    data = _frame(rng.normal(0.0, 0.05, 80), rng.normal(0.0, 0.05, 80))
    result = detect_adwin(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 01:19"),
        current_window=("2026-01-02 00:00", "2026-01-02 01:19"),
        params={"delta": 0.001, "min_window_length": 10, "grace_period": 40},
    )
    assert result.variant_id == "ADWIN_MEAN_STREAM"
    assert result.p_value is None
    assert result.threshold == 0.001
    assert result.drift_detected is False
    assert result.severity == "normal"
    assert result.measurements["DRIFT_ALARM_STATE"] == "normal"
    assert result.measurements["WINDOW_SIZE"] == result.measurements["ADAPTIVE_WINDOW_WIDTH"]
    assert result.measurements["ALARM_COUNT"] == 0
    assert result.measurements["PROCESSED_COUNT"] == 160
    assert result.measurements["SAMPLE_SIZE_REFERENCE"] == 80
    assert result.measurements["SAMPLE_SIZE_CURRENT"] == 80


def test_adwin_mean_shift_alarm() -> None:
    rng = np.random.default_rng(901)
    data = _frame(rng.normal(0.0, 0.02, 80), rng.normal(1.2, 0.02, 80))
    result = detect_adwin(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 01:19"),
        current_window=("2026-01-02 00:00", "2026-01-02 01:19"),
        params={"delta": 0.05, "min_window_length": 10, "grace_period": 40},
    )
    assert result.drift_detected is True
    assert result.severity == "drift_detected"
    assert result.measurements["DRIFT_ALARM_STATE"] == "drift_detected"
    assert result.measurements["ALARM_COUNT"] > 0
    assert result.measurements["FIRST_ALARM_TIME"] is not None
    assert result.measurements["LAST_ALARM_INDEX"] is not None
    assert len(result.measurements["ALARM_EVENTS"]) <= 50


def test_adwin_parameter_alias_validation_and_event_policy() -> None:
    data = _frame(np.zeros(30), np.zeros(30))
    alias = detect_adwin(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:29"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:29"),
        params={"threshold_or_alpha": 0.01, "record_events": False},
    )
    assert alias.threshold == 0.01
    assert "ALARM_EVENTS" not in alias.measurements
    assert any("threshold_or_alpha" in warning for warning in alias.warnings)

    conflict = detect_adwin(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:29"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:29"),
        params={"delta": 0.01, "threshold_or_alpha": 0.02},
    )
    assert conflict.severity == "not_applicable"

    invalid = detect_adwin(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:29"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:29"),
        params={"clock": 0},
    )
    assert invalid.severity == "not_applicable"


def test_adwin_schema_window_and_warning_behavior() -> None:
    bool_data = _frame(np.ones(25), np.ones(25))
    bool_data["value"] = True
    bool_result = detect_adwin(
        bool_data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:24"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:24"),
    )
    assert bool_result.severity == "not_applicable"

    small = detect_adwin(
        _frame(np.arange(3, dtype=float), np.arange(3, dtype=float)),
        reference_window=("2026-01-01 00:00", "2026-01-01 00:02"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:02"),
    )
    assert small.severity == "not_applicable"

    warning_data = _frame(np.arange(40, dtype=float), np.arange(20, dtype=float) + 2.0)
    warning_data["time"] = warning_data["time"].astype(object)
    warning_data.loc[0, "value"] = np.nan
    warning_data.loc[1, "time"] = "not-a-time"
    result = detect_adwin(
        warning_data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:39"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:19"),
        params={
            "clock": 2,
            "min_reference_size": 20,
            "min_current_size": 20,
            "sample_imbalance_warning_ratio": 1.5,
            "multiple_testing_correction": "bonferroni",
        },
    )
    assert result.severity in {"normal", "drift_detected"}
    assert any("dropped" in warning for warning in result.warnings)
    assert any("imbalanced" in warning for warning in result.warnings)
    assert any("clock > 1" in warning for warning in result.warnings)
    assert any("multiple_testing_correction" in warning for warning in result.warnings)


def test_adwin_projected_stream_variants() -> None:
    data = _frame(np.zeros(30), np.ones(30))

    for variant_id, stream_semantics in (
        ("ADWIN_ERROR_RATE", "projected_error_rate_stream"),
        ("ADWIN_DISTANCE_STREAM", "projected_distance_stream"),
    ):
        result = detect_adwin(
            data,
            reference_window=("2026-01-01 00:00", "2026-01-01 00:29"),
            current_window=("2026-01-02 00:00", "2026-01-02 00:29"),
            params={
                "variant_id": variant_id,
                "delta": 0.2,
                "min_window_length": 2,
                "grace_period": 5,
                "min_reference_size": 20,
                "min_current_size": 20,
            },
        )
        assert result.severity == "drift_detected"
        assert result.metadata["stream_semantics"] == stream_semantics


def test_adwin_non_scalar_requests() -> None:
    data = _frame(np.zeros(30), np.ones(30))

    feature_request = detect_adwin(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:29"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:29"),
        params={"feature_cols": ["a", "b"]},
    )
    assert feature_request.severity == "not_applicable"
