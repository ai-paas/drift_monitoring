from __future__ import annotations

import numpy as np
import pandas as pd

from drift_algorithm.methods.batchdistributioncomparison import detect_wasserstein_distance


def _frame(reference: np.ndarray, current: np.ndarray) -> pd.DataFrame:
    ref_time = pd.date_range("2026-01-01 00:00", periods=len(reference), freq="min")
    cur_time = pd.date_range("2026-01-02 00:00", periods=len(current), freq="min")
    return pd.DataFrame(
        {
            "time": list(ref_time) + list(cur_time),
            "value": list(reference) + list(current),
        }
    )


def test_wasserstein_no_threshold_returns_watch_score_only() -> None:
    rng = np.random.default_rng(10)
    reference = rng.normal(0, 1, 200)
    current = rng.normal(0, 1, 200)
    result = detect_wasserstein_distance(
        _frame(reference, current),
        reference_window=("2026-01-01 00:00", "2026-01-01 03:19"),
        current_window=("2026-01-02 00:00", "2026-01-02 03:19"),
    )

    assert result.method_id == "DM-002"
    assert result.variant_id == "WASSERSTEIN_1D_EXACT"
    assert result.drift_detected is None
    assert result.severity == "watch"
    assert result.p_value is None
    assert result.drift_score == result.test_statistic
    assert "WASSERSTEIN_DISTANCE" in result.measurements
    assert result.measurements["DRIFT_ALARM_STATE"] == "undetermined"


def test_wasserstein_threshold_detects_shift() -> None:
    rng = np.random.default_rng(12)
    reference = rng.normal(0, 1, 200)
    current = rng.normal(2.0, 1, 200)
    result = detect_wasserstein_distance(
        _frame(reference, current),
        reference_window=("2026-01-01 00:00", "2026-01-01 03:19"),
        current_window=("2026-01-02 00:00", "2026-01-02 03:19"),
        params={"threshold": 0.5},
    )

    assert result.drift_detected is True
    assert result.severity == "drift_detected"
    assert result.threshold == 0.5
    assert result.measurements["DRIFT_ALARM_STATE"] == "drift_detected"


def test_wasserstein_approx_histogram_detects_shift() -> None:
    rng = np.random.default_rng(121)
    reference = rng.normal(0, 1, 200)
    current = rng.normal(2.0, 1, 200)
    result = detect_wasserstein_distance(
        _frame(reference, current),
        reference_window=("2026-01-01 00:00", "2026-01-01 03:19"),
        current_window=("2026-01-02 00:00", "2026-01-02 03:19"),
        params={
            "variant_id": "WASSERSTEIN_APPROX_HISTOGRAM",
            "threshold": 0.5,
            "bin_count": 24,
        },
    )

    assert result.variant_id == "WASSERSTEIN_APPROX_HISTOGRAM"
    assert result.drift_detected is True
    assert result.severity == "drift_detected"
    assert result.measurements["WASSERSTEIN_DISTANCE"] > 0.5
    assert result.measurements["METHOD_POLICY"]["approximation"] == "histogram_bin_centers"
    assert result.metadata["histogram_bin_count"] == 24


def test_wasserstein_window_trend_detects_shift() -> None:
    rng = np.random.default_rng(122)
    reference = rng.normal(0, 1, 200)
    current = rng.normal(2.0, 1, 200)
    result = detect_wasserstein_distance(
        _frame(reference, current),
        reference_window=("2026-01-01 00:00", "2026-01-01 03:19"),
        current_window=("2026-01-02 00:00", "2026-01-02 03:19"),
        params={
            "variant_id": "WASSERSTEIN_WINDOW_TREND",
            "threshold": 0.5,
            "trend_threshold": 0.5,
        },
    )

    assert result.variant_id == "WASSERSTEIN_WINDOW_TREND"
    assert result.drift_detected is True
    assert result.severity == "drift_detected"
    assert result.measurements["WINDOW_TREND_DISTANCE"] > 0.5
    assert result.measurements["METHOD_POLICY"]["trend_policy"] == "single_reference_current_window_delta"
    assert result.metadata["trend_policy"] == "single_reference_current_window_delta"


def test_wasserstein_threshold_normal_when_below_limit() -> None:
    rng = np.random.default_rng(13)
    reference = rng.normal(0, 1, 200)
    current = rng.normal(0, 1, 200)
    result = detect_wasserstein_distance(
        _frame(reference, current),
        reference_window=("2026-01-01 00:00", "2026-01-01 03:19"),
        current_window=("2026-01-02 00:00", "2026-01-02 03:19"),
        params={"threshold": 10.0},
    )

    assert result.drift_detected is False
    assert result.severity == "normal"
    assert result.measurements["DRIFT_ALARM_STATE"] == "normal"


def test_wasserstein_threshold_or_alpha_alias_warns() -> None:
    data = _frame(np.linspace(0, 1, 50), np.linspace(0.2, 1.2, 50))
    result = detect_wasserstein_distance(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:49"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:49"),
        params={"threshold_or_alpha": 0.1},
    )

    assert result.threshold == 0.1
    assert any("not a p-value alpha" in warning for warning in result.warnings)


def test_wasserstein_weights_and_invalid_weights() -> None:
    data = _frame(np.array([0.0, 1.0, 2.0] * 20), np.array([1.0, 2.0, 3.0] * 20))
    data["ref_weight"] = 1.0
    data["cur_weight"] = 1.0
    result = detect_wasserstein_distance(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:59"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:59"),
        params={"sample_weights_reference": "ref_weight", "sample_weights_current": "cur_weight"},
    )

    assert result.severity == "watch"
    assert result.measurements["WASSERSTEIN_DISTANCE"] > 0
    assert result.metadata["sample_weights_reference"] == "ref_weight"

    bad = data.copy()
    bad.loc[bad["time"] < pd.Timestamp("2026-01-02"), "ref_weight"] = -1.0
    invalid = detect_wasserstein_distance(
        bad,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:59"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:59"),
        params={"sample_weights_reference": "ref_weight"},
    )
    assert invalid.severity == "not_applicable"


def test_wasserstein_not_applicable_cases() -> None:
    data = _frame(np.arange(10, dtype=float), np.arange(10, dtype=float))

    missing_windows = detect_wasserstein_distance(data)
    assert missing_windows.severity == "not_applicable"

    too_small = detect_wasserstein_distance(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:09"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:09"),
    )
    assert too_small.severity == "not_applicable"

    invalid_policy = detect_wasserstein_distance(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:09"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:09"),
        params={"normalization_policy": "standard"},
    )
    assert invalid_policy.severity == "not_applicable"


def test_sliced_wasserstein_embedding_uses_projected_stream() -> None:
    rng = np.random.default_rng(123)
    reference = rng.normal(0, 1, 100)
    current = rng.normal(2.0, 1, 100)
    result = detect_wasserstein_distance(
        _frame(reference, current),
        reference_window=("2026-01-01 00:00", "2026-01-01 01:39"),
        current_window=("2026-01-02 00:00", "2026-01-02 01:39"),
        params={
            "variant_id": "SLICED_WASSERSTEIN_EMBEDDING",
            "threshold": 0.5,
            "projection_count": 1,
        },
    )

    assert result.variant_id == "SLICED_WASSERSTEIN_EMBEDDING"
    assert result.drift_detected is True
    assert result.measurements["METHOD_POLICY"]["projection_policy"] == "single_projected_numeric_stream"
    assert result.metadata["projection_count"] == 1
