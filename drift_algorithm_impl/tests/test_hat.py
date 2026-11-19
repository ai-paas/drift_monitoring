from __future__ import annotations

import numpy as np
import pandas as pd

from drift_algorithm.methods.operationaladaptationmethod import detect_hat


def _hat_frame(reference: np.ndarray, current: np.ndarray) -> pd.DataFrame:
    ref_time = pd.date_range("2026-01-01 00:00", periods=len(reference), freq="min")
    cur_time = pd.date_range("2026-01-02 00:00", periods=len(current), freq="min")
    return pd.DataFrame({"time": list(ref_time) + list(cur_time), "error": list(reference) + list(current)})


def test_hat_node_monitoring_no_drift() -> None:
    reference = np.zeros(120)
    current = np.zeros(120)
    reference[::10] = 1
    current[::10] = 1
    data = _hat_frame(reference, current)
    data["node_id"] = ["root"] * len(data)

    result = detect_hat(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 01:59"),
        current_window=("2026-01-02 00:00", "2026-01-02 01:59"),
        params={"error_col": "error", "warning_delta": 0.1, "drift_delta": 0.2, "min_node_size": 20},
    )

    assert result.variant_id == "HAT_ADWIN_NODE_MONITORING"
    assert result.drift_detected is False
    assert result.measurements["DRIFT_ALARM_STATE"] == "normal"
    assert result.measurements["ONLINE_OR_PRE_POST_PERFORMANCE"]["reference_accuracy"] == 0.9


def test_hat_node_monitoring_detects_node_drift() -> None:
    reference = np.zeros(120)
    reference[::20] = 1
    current = np.r_[np.zeros(60), np.ones(60)]
    data = _hat_frame(reference, current)
    data["node_id"] = ["stable"] * 120 + ["stable"] * 60 + ["leaf-7"] * 60

    result = detect_hat(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 01:59"),
        current_window=("2026-01-02 00:00", "2026-01-02 01:59"),
        params={"error_col": "error", "warning_delta": 0.1, "drift_delta": 0.2, "min_node_size": 20},
    )

    assert result.drift_detected is True
    assert result.measurements["DRIFT_ALARM_STATE"] == "drift_detected"
    assert result.measurements["NODE_ALARM_COUNT"] >= 1
    assert result.measurements["NODE_DRIFT_STATE"][0]["node_id"] == "leaf-7"


def test_hat_alternate_tree_replacement_event() -> None:
    reference = np.zeros(100)
    reference[::20] = 1
    current = np.r_[np.ones(40), np.zeros(60)]
    data = _hat_frame(reference, current)
    data["alternate_created"] = 0
    data["tree_replaced"] = 0
    data.loc[120, "alternate_created"] = 1
    data.loc[145, "tree_replaced"] = 1
    data["online_accuracy"] = list(np.repeat(0.95, 100)) + list(np.r_[np.repeat(0.4, 40), np.repeat(0.9, 60)])

    result = detect_hat(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 01:39"),
        current_window=("2026-01-02 00:00", "2026-01-02 01:39"),
        params={
            "variant_id": "HAT_ALTERNATE_TREE_REPLACEMENT",
            "error_col": "error",
            "warning_delta": 0.1,
            "drift_delta": 0.2,
        },
    )

    assert result.variant_id == "HAT_ALTERNATE_TREE_REPLACEMENT"
    assert result.drift_detected is True
    assert result.measurements["ADAPTATION_EVENT"]["alternate_tree_created_count"] == 1
    assert result.measurements["ADAPTATION_EVENT"]["tree_replacement_count"] == 1
    assert result.measurements["ONLINE_OR_PRE_POST_PERFORMANCE"]["online_accuracy_last"] == 0.9


def test_hat_from_labels() -> None:
    reference_true = np.ones(100, dtype=int)
    reference_pred = reference_true.copy()
    reference_pred[::20] = 0
    current_true = np.ones(100, dtype=int)
    current_pred = current_true.copy()
    current_pred[50:] = 0
    ref_time = pd.date_range("2026-01-01 00:00", periods=100, freq="min")
    cur_time = pd.date_range("2026-01-02 00:00", periods=100, freq="min")
    data = pd.DataFrame(
        {
            "time": list(ref_time) + list(cur_time),
            "y_true": list(reference_true) + list(current_true),
            "y_pred": list(reference_pred) + list(current_pred),
        }
    )

    result = detect_hat(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 01:39"),
        current_window=("2026-01-02 00:00", "2026-01-02 01:39"),
        params={"y_true": "y_true", "y_pred": "y_pred", "warning_delta": 0.1, "drift_delta": 0.2},
    )

    assert result.drift_detected is True
    assert result.measurements["CURRENT_ERROR_RATE"] > result.measurements["REFERENCE_ERROR_RATE"]


def test_hat_validation_and_warnings() -> None:
    data = _hat_frame(np.zeros(30), np.ones(30))
    invalid = detect_hat(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:29"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:29"),
        params={"error_col": "missing"},
    )
    assert invalid.severity == "not_applicable"

    dirty = _hat_frame(np.zeros(40), np.r_[np.zeros(20), np.ones(20)])
    dirty["time"] = dirty["time"].astype(object)
    dirty.loc[0, "error"] = np.nan
    dirty.loc[1, "time"] = "not-a-time"
    result = detect_hat(
        dirty,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:39"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:39"),
        params={"error_col": "error", "min_reference_size": 20, "min_current_size": 20},
    )

    assert result.severity in {"normal", "warning", "drift_detected"}
    assert any("dropped" in warning for warning in result.warnings)
