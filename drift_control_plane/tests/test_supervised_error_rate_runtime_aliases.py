from __future__ import annotations

import json
from datetime import datetime, timedelta

from drift_server.app.drift.runtime_registry import get_runtime_method
from drift_server.app.runtime_methods.ddm_error_rate_stream import run_ddm_error_rate_stream
from drift_server.app.runtime_methods.eddm_error_rate_stream import run_eddm_error_rate_stream
from drift_server.app.runtime_methods.rddm_error_rate_stream import run_rddm_error_rate_stream


def test_supervised_error_rate_variant_aliases_resolve() -> None:
    assert get_runtime_method("ddm_warning_buffer") is run_ddm_error_rate_stream
    assert get_runtime_method("ddm_class_specific") is run_ddm_error_rate_stream
    assert get_runtime_method("rddm_reactive_reset") is run_rddm_error_rate_stream
    assert get_runtime_method("eddm_warning_drift") is run_eddm_error_rate_stream
    assert get_runtime_method("eddm_gradual_drift") is run_eddm_error_rate_stream


def test_ddm_class_specific_runtime_preserves_label_columns() -> None:
    start = datetime(2026, 1, 1)
    errors = []
    for index in range(240):
        y_true = "B" if index % 2 else "A"
        if index < 120:
            y_pred = y_true
        elif y_true == "B":
            y_pred = "A"
        else:
            y_pred = y_true
        errors.append(
            {
                "time": (start + timedelta(minutes=index)).isoformat(),
                "error": 0 if y_true == y_pred else 1,
                "y_true": y_true,
                "y_pred": y_pred,
                "confidence": 0.92 if y_true == y_pred else 0.41,
            }
        )

    assignment = {
        "runtime_method_key": "ddm_class_specific",
        "params_json": json.dumps(
            {
                "variant_id": "DDM_CLASS_SPECIFIC",
                "error_col": "error",
                "y_true": "y_true",
                "y_pred": "y_pred",
                "class_label": "B",
                "min_num_instances": 30,
                "min_reference_size": 30,
                "min_current_size": 30,
                "record_events": True,
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

    result = run_ddm_error_rate_stream(assignment, bucket, {})

    assert result["runStatus"] == "success"
    assert result["diagnostics"]["implementation"] == "drift_algorithm_impl_ddm"
    assert result["diagnostics"]["algorithmImplSucceeded"] is True
    measurements = result["metrics"]["measurements"]
    assert measurements["CLASS_LABEL"] == "B"
    assert measurements["PROCESSED_COUNT"] >= 60
