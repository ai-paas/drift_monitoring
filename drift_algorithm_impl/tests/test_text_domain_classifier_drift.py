from __future__ import annotations

import numpy as np
import pandas as pd

from drift_algorithm.methods.domainclassifiermethod import detect_text_domain_classifier_drift


def _text_frame(reference: list[str], current: list[str]) -> pd.DataFrame:
    ref_time = pd.date_range("2026-01-01 00:00", periods=len(reference), freq="min")
    cur_time = pd.date_range("2026-01-02 00:00", periods=len(current), freq="min")
    return pd.DataFrame({"time": list(ref_time) + list(cur_time), "text": reference + current})


def test_text_domain_classifier_roc_auc_no_drift() -> None:
    reference = [f"claim payment status stable account {idx % 5}" for idx in range(80)]
    current = [f"claim payment status stable account {idx % 5}" for idx in range(80)]
    data = _text_frame(reference, current)

    result = detect_text_domain_classifier_drift(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 01:19"),
        current_window=("2026-01-02 00:00", "2026-01-02 01:19"),
        params={"text_col": "text", "auc_threshold": 0.8},
    )

    assert result.variant_id == "TEXT_DOMAIN_CLASSIFIER_ROC_AUC"
    assert result.drift_detected is False
    assert result.measurements["ROC_AUC"] < 0.8
    assert result.measurements["TEXT_FEATURE_DIMENSION"] > 0


def test_text_domain_classifier_roc_auc_detects_vocabulary_shift() -> None:
    reference = [f"claim payment status stable account {idx % 5}" for idx in range(90)]
    current = [f"fraud dispute urgent chargeback investigation {idx % 5}" for idx in range(90)]
    data = _text_frame(reference, current)

    result = detect_text_domain_classifier_drift(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 01:29"),
        current_window=("2026-01-02 00:00", "2026-01-02 01:29"),
        params={"text_col": "text", "auc_threshold": 0.8},
    )

    assert result.drift_detected is True
    assert result.measurements["ROC_AUC"] >= 0.8
    assert result.measurements["PROBABILITY_MEAN_CURRENT"] > result.measurements["PROBABILITY_MEAN_REFERENCE"]


def test_text_domain_classifier_stat_test() -> None:
    reference = [f"short inquiry payment status {idx % 4}" for idx in range(80)]
    current = [f"urgent fraud escalation chargeback review {idx % 4}" for idx in range(80)]
    data = _text_frame(reference, current)

    result = detect_text_domain_classifier_drift(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 01:19"),
        current_window=("2026-01-02 00:00", "2026-01-02 01:19"),
        params={"variant_id": "TEXT_DOMAIN_CLASSIFIER_STAT_TEST", "text_col": "text", "alpha": 0.05},
    )

    assert result.variant_id == "TEXT_DOMAIN_CLASSIFIER_STAT_TEST"
    assert result.drift_detected is True
    assert result.p_value is not None and result.p_value < 0.05
    assert result.measurements["TEXT_DOMAIN_CLASSIFIER_STATISTIC"] > 0


def test_text_descriptor_drift_numeric_columns() -> None:
    ref_time = pd.date_range("2026-01-01 00:00", periods=70, freq="min")
    cur_time = pd.date_range("2026-01-02 00:00", periods=70, freq="min")
    data = pd.DataFrame(
        {
            "time": list(ref_time) + list(cur_time),
            "token_count": list(np.linspace(8, 12, 70)) + list(np.linspace(30, 40, 70)),
            "uppercase_rate": list(np.linspace(0.01, 0.02, 70)) + list(np.linspace(0.01, 0.02, 70)),
        }
    )

    result = detect_text_domain_classifier_drift(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 01:09"),
        current_window=("2026-01-02 00:00", "2026-01-02 01:09"),
        params={
            "variant_id": "TEXT_DESCRIPTOR_DRIFT",
            "descriptor_cols": ["token_count", "uppercase_rate"],
            "alpha": 0.05,
        },
    )

    assert result.variant_id == "TEXT_DESCRIPTOR_DRIFT"
    assert result.drift_detected is True
    assert result.measurements["TEXT_DESCRIPTOR_DRIFT"][0]["descriptor"] == "token_count"
    assert "token_count" in result.measurements["SIGNIFICANT_DESCRIPTORS"]


def test_text_domain_validation_and_warnings() -> None:
    data = _text_frame(["same text"] * 5, ["other text"] * 5)
    invalid = detect_text_domain_classifier_drift(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:04"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:04"),
        params={"text_col": "missing"},
    )
    assert invalid.severity == "not_applicable"

    ref_time = pd.date_range("2026-01-01 00:00", periods=25, freq="min")
    cur_time = pd.date_range("2026-01-02 00:00", periods=10, freq="min")
    dirty = pd.DataFrame(
        {
            "time": list(ref_time) + list(cur_time),
            "length": list(np.linspace(1, 2, 25)) + list(np.linspace(2, 3, 10)),
        }
    )
    dirty.loc[0, "length"] = np.nan
    dirty["time"] = dirty["time"].astype(object)
    dirty.loc[1, "time"] = "not-a-time"

    result = detect_text_domain_classifier_drift(
        dirty,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:24"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:09"),
        params={
            "variant_id": "TEXT_DESCRIPTOR_DRIFT",
            "descriptor_cols": ["length"],
            "min_reference_size": 20,
            "min_current_size": 5,
        },
    )

    assert result.severity in {"normal", "drift_detected"}
    assert any("dropped" in warning for warning in result.warnings)
