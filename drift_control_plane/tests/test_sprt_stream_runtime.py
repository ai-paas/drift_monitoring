from __future__ import annotations

import json
from datetime import datetime, timedelta

from drift_server.app.drift.runtime_registry import get_runtime_method
from drift_server.app.runtime_methods.sprt_stream import run_sprt_stream


def test_sprt_variant_aliases_resolve() -> None:
    assert get_runtime_method("sprt_stream") is run_sprt_stream
    assert get_runtime_method("sprt_bernoulli_error_rate") is run_sprt_stream
    assert get_runtime_method("sprt_gaussian_mean_shift") is run_sprt_stream


def test_sprt_bernoulli_error_rate_runtime_calls_algorithm_impl() -> None:
    start = datetime(2026, 1, 1)
    errors = []
    for index in range(200):
        error = 0 if index < 100 else (1 if index < 140 else 0)
        errors.append({"time": (start + timedelta(minutes=index)).isoformat(), "error": error})
    assignment = {
        "runtime_method_key": "sprt_bernoulli_error_rate",
        "params_json": json.dumps(
            {
                "variant_id": "SPRT_BERNOULLI_ERROR_RATE",
                "error_col": "value",
                "p0": 0.05,
                "p1": 0.25,
                "alpha": 0.1,
                "beta": 0.1,
                "min_reference_size": 40,
                "min_current_size": 40,
            }
        ),
    }
    bucket = {
        "bucket_id": "bucket-001",
        "window_start": errors[0]["time"],
        "window_end": errors[-1]["time"],
        "payload": {"errors": errors},
        "error_rate": None,
    }

    result = run_sprt_stream(assignment, bucket, {})

    assert result["runStatus"] == "success"
    assert result["diagnostics"]["implementation"] == "drift_algorithm_impl_sprt"
    assert result["diagnostics"]["algorithmImplSucceeded"] is True
    assert result["metrics"]["measurements"]["HYPOTHESIS_DECISION_STATE"] == "accept_h1"
    assert result["level"] == "drift"


def test_sprt_gaussian_mean_runtime_calls_algorithm_impl() -> None:
    start = datetime(2026, 1, 1)
    assignment = {
        "runtime_method_key": "sprt_gaussian_mean_shift",
        "params_json": json.dumps(
            {
                "variant_id": "SPRT_GAUSSIAN_MEAN_SHIFT",
                "mu0": 0.0,
                "mu1": 1.0,
                "sigma": 0.2,
                "alpha": 0.05,
                "beta": 0.1,
                "maxStatePoints": 200,
            }
        ),
    }
    previous_state = {"points": []}
    result = None
    for index in range(160):
        value = 0.0 if index < 80 else 1.1
        bucket = {
            "bucket_id": f"bucket-{index:03d}",
            "window_start": (start + timedelta(minutes=index)).isoformat(),
            "window_end": (start + timedelta(minutes=index + 1)).isoformat(),
            "mean_value": value,
        }
        result = run_sprt_stream(assignment, bucket, previous_state)
        previous_state = result["nextState"]

    assert result is not None
    assert result["runStatus"] == "success"
    assert result["diagnostics"]["implementation"] == "drift_algorithm_impl_sprt"
    assert result["diagnostics"]["algorithmImplSucceeded"] is True
    assert result["metrics"]["measurements"]["HYPOTHESIS_DECISION_STATE"] == "accept_h1"
    assert result["level"] == "drift"
