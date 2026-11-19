from __future__ import annotations

import numpy as np
import pandas as pd

from drift_algorithm.methods.representationdriftmethod import detect_autoencoder_representation_drift


def _autoencoder_frame(reference: np.ndarray, current: np.ndarray) -> pd.DataFrame:
    ref_time = pd.date_range("2026-01-01 00:00", periods=len(reference), freq="min")
    cur_time = pd.date_range("2026-01-02 00:00", periods=len(current), freq="min")
    values = np.vstack([reference, current])
    return pd.DataFrame(
        {
            "time": list(ref_time) + list(cur_time),
            "z1": values[:, 0],
            "z2": values[:, 1],
            "z3": values[:, 2],
            "z4": values[:, 3],
        }
    )


def _latent_reference(n: int = 80) -> np.ndarray:
    x = np.linspace(-2.0, 2.0, n)
    return np.column_stack([x, np.sin(x), np.cos(x), x**2 / 4.0])


def test_latent_space_drift_no_drift() -> None:
    reference = _latent_reference()
    current = reference + 0.001
    data = _autoencoder_frame(reference, current)
    result = detect_autoencoder_representation_drift(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 01:19"),
        current_window=("2026-01-02 00:00", "2026-01-02 01:19"),
        params={
            "latent_cols": ["z1", "z2", "z3", "z4"],
            "alpha": 0.05,
            "permutation_count": 19,
            "random_state": 11,
        },
    )
    assert result.variant_id == "LATENT_SPACE_DRIFT"
    assert result.drift_detected is False
    assert result.measurements["LATENT_DRIFT_SCORE"] >= 0
    assert result.p_value is not None and result.p_value > 0.05


def test_latent_space_drift_detects_shift() -> None:
    reference = _latent_reference(60)
    current = reference + np.array([1.3, -0.9, 0.8, 0.7])
    data = _autoencoder_frame(reference, current)
    result = detect_autoencoder_representation_drift(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:59"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:59"),
        params={
            "variant_id": "LATENT_SPACE_DRIFT",
            "latent_cols": ["z1", "z2", "z3", "z4"],
            "alpha": 0.1,
            "permutation_count": 19,
            "random_state": 13,
        },
    )
    assert result.drift_detected is True
    assert result.severity == "drift_detected"
    assert result.p_value is not None and result.p_value < 0.1


def test_reconstruction_error_drift_with_error_column() -> None:
    ref_time = pd.date_range("2026-01-01 00:00", periods=50, freq="min")
    cur_time = pd.date_range("2026-01-02 00:00", periods=50, freq="min")
    data = pd.DataFrame(
        {
            "time": list(ref_time) + list(cur_time),
            "reconstruction_error": list(np.linspace(0.05, 0.15, 50)) + list(np.linspace(0.8, 1.2, 50)),
        }
    )
    result = detect_autoencoder_representation_drift(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:49"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:49"),
        params={
            "variant_id": "RECONSTRUCTION_ERROR_DRIFT",
            "reconstruction_error_col": "reconstruction_error",
            "alpha": 0.05,
        },
    )
    assert result.variant_id == "RECONSTRUCTION_ERROR_DRIFT"
    assert result.drift_detected is True
    assert result.measurements["RECONSTRUCTION_ERROR"] > result.measurements["RECONSTRUCTION_ERROR_REFERENCE"]
    assert result.p_value is not None and result.p_value < 0.05


def test_autoencoder_domain_classifier_surrogate() -> None:
    reference = _latent_reference(70)
    current = reference + np.array([1.5, 1.0, -0.8, 0.5])
    data = _autoencoder_frame(reference, current)
    result = detect_autoencoder_representation_drift(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 01:09"),
        current_window=("2026-01-02 00:00", "2026-01-02 01:09"),
        params={
            "variant_id": "AUTOENCODER_DOMAIN_CLASSIFIER",
            "latent_cols": ["z1", "z2", "z3", "z4"],
            "threshold": 0.6,
        },
    )
    assert result.variant_id == "AUTOENCODER_DOMAIN_CLASSIFIER"
    assert result.drift_detected is True
    assert result.p_value is None
    assert result.measurements["DOMAIN_CLASSIFIER_AUC"] > 0.6
    assert any("nearest-centroid" in warning for warning in result.warnings)


def test_autoencoder_representation_validation_and_warnings() -> None:
    data = _autoencoder_frame(np.zeros((5, 4)), np.ones((5, 4)))
    invalid = detect_autoencoder_representation_drift(
        data,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:04"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:04"),
        params={"latent_cols": ["z1"]},
    )
    assert invalid.severity == "not_applicable"

    dirty = _autoencoder_frame(_latent_reference(25), _latent_reference(10) + 0.5)
    dirty.loc[0, "z1"] = np.nan
    dirty["time"] = dirty["time"].astype(object)
    dirty.loc[1, "time"] = "not-a-time"
    result = detect_autoencoder_representation_drift(
        dirty,
        reference_window=("2026-01-01 00:00", "2026-01-01 00:24"),
        current_window=("2026-01-02 00:00", "2026-01-02 00:09"),
        params={
            "latent_cols": ["z1", "z2", "z3", "z4"],
            "min_reference_size": 20,
            "min_current_size": 5,
            "threshold": 0.0,
        },
    )
    assert result.severity in {"normal", "drift_detected"}
    assert any("dropped" in warning for warning in result.warnings)
