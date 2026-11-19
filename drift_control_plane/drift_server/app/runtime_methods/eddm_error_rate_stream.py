from __future__ import annotations

import json
from typing import Any

from drift_server.app.runtime_methods.adwin_mean_stream import _drift_result_to_dict, _split_windows
from drift_server.app.runtime_methods.error_rate_stream_common import (
    append_error_points,
    bucket_error_points,
    bucket_error_rate,
    ensure_algorithm_impl_path,
    fallback_output,
    next_error_state,
    normal_output,
)


# @managed-contract contract_id=runtime_methods.eddm_error_rate_stream.run_eddm_error_rate_stream level=P0
def run_eddm_error_rate_stream(
    assignment: Any, bucket: dict[str, Any], previous_state: dict[str, Any]
) -> dict[str, Any]:
    params = json.loads(assignment["params_json"])
    bucket_errors = bucket_error_points(bucket)
    points = append_error_points(previous_state, bucket_errors, params)
    error_rate = bucket_error_rate(bucket, bucket_errors)
    next_state = next_error_state(previous_state, bucket, points, error_rate)

    if len(points) < 2:
        return normal_output(
            assignment,
            bucket,
            next_state,
            error_rate,
            previous_state.get("lastErrorRate"),
            "state initialized",
            {
                "implementation": "deterministic_fallback",
                "algorithmImplAttempted": False,
                "fallbackReason": "insufficient_points",
            },
        )

    algorithm_result = _run_algorithm_impl(params, points)
    if algorithm_result["status"] == "success":
        converted = _convert_drift_result(assignment, bucket, next_state, error_rate, previous_state, algorithm_result)
        if converted is not None:
            return converted

    return fallback_output(
        assignment,
        bucket,
        next_state,
        error_rate,
        previous_state.get("lastErrorRate"),
        params,
        {
            "algorithmImplAttempted": algorithm_result.get("attempted", True),
            "algorithmImplSucceeded": False,
            "algorithmImpl": algorithm_result.get("algorithmImpl"),
            "algorithmSeverity": algorithm_result.get("severity"),
            "algorithmWarnings": algorithm_result.get("warnings", []),
            "algorithmInterpretation": algorithm_result.get("interpretation"),
            "algorithmMetadata": algorithm_result.get("metadata", {}),
            "fallbackReason": algorithm_result.get("fallbackReason") or "algorithm_result_not_usable",
        },
        "EDDM",
    )


def _run_algorithm_impl(params: dict[str, Any], points: list[dict[str, Any]]) -> dict[str, Any]:
    if params.get("useAlgorithmImpl", True) is False:
        return {
            "status": "disabled",
            "attempted": False,
            "algorithmImpl": "drift_algorithm_impl_eddm",
            "fallbackReason": "useAlgorithmImpl=false",
        }
    import_result = _import_detect_eddm()
    if import_result["status"] != "success":
        return import_result
    detect_eddm = import_result["detect_eddm"]
    try:
        import pandas as pd
    except Exception as exc:  # noqa: BLE001
        return {
            "status": "import_error",
            "attempted": True,
            "algorithmImpl": "drift_algorithm_impl_eddm",
            "fallbackReason": f"pandas import failed: {exc}",
        }

    data = pd.DataFrame([{"time": point["time"], "error": point["error"]} for point in points])
    reference_window, current_window = _split_windows([{"time": point["time"], "value": point["error"]} for point in points])
    algorithm_params = _algorithm_params(params)
    try:
        result = detect_eddm(
            data,
            time_col="time",
            value_col="error",
            reference_window=reference_window,
            current_window=current_window,
            params=algorithm_params,
        )
    except Exception as exc:  # noqa: BLE001
        return {
            "status": "exception",
            "attempted": True,
            "algorithmImpl": "drift_algorithm_impl_eddm",
            "fallbackReason": f"{exc.__class__.__name__}: {exc}",
        }

    result_dict = _drift_result_to_dict(result)
    if result_dict.get("severity") == "not_applicable":
        return {
            "status": "not_applicable",
            "attempted": True,
            "algorithmImpl": "drift_algorithm_impl_eddm",
            "fallbackReason": result_dict.get("interpretation") or "not_applicable",
            **result_dict,
        }
    if result_dict.get("severity") == "error":
        return {
            "status": "error",
            "attempted": True,
            "algorithmImpl": "drift_algorithm_impl_eddm",
            "fallbackReason": result_dict.get("interpretation") or "algorithm_error",
            **result_dict,
        }
    return {
        "status": "success",
        "attempted": True,
        "algorithmImpl": "drift_algorithm_impl_eddm",
        "referenceWindow": reference_window,
        "currentWindow": current_window,
        **result_dict,
    }


def _import_detect_eddm() -> dict[str, Any]:
    ensure_algorithm_impl_path()
    try:
        from drift_algorithm.methods.supervisedconceptdriftdetector import detect_eddm
    except Exception as exc:  # noqa: BLE001
        return {
            "status": "import_error",
            "attempted": True,
            "algorithmImpl": "drift_algorithm_impl_eddm",
            "fallbackReason": f"detect_eddm import failed: {exc}",
        }
    return {"status": "success", "detect_eddm": detect_eddm}


def _algorithm_params(params: dict[str, Any]) -> dict[str, Any]:
    excluded = {"errorRateShiftThreshold", "maxStatePoints", "useAlgorithmImpl", "fallbackOnNotApplicable"}
    algorithm_params = {key: value for key, value in params.items() if key not in excluded}
    algorithm_params.setdefault("variant_id", "EDDM_DISTANCE_BETWEEN_ERRORS")
    algorithm_params.setdefault("error_col", "error")
    return algorithm_params


# @managed-contract contract_id=runtime_methods.eddm_error_rate_stream._convert_drift_result level=P0
def _convert_drift_result(
    assignment: Any,
    bucket: dict[str, Any],
    next_state: dict[str, Any],
    error_rate: float,
    previous_state: dict[str, Any],
    algorithm_result: dict[str, Any],
) -> dict[str, Any] | None:
    drift_detected = algorithm_result.get("drift_detected")
    if drift_detected is None:
        return None

    severity = algorithm_result.get("severity")
    level = "drift" if drift_detected is True else ("warning" if severity == "warning" else "normal")
    measurements = algorithm_result.get("measurements", {})
    score = float(algorithm_result.get("drift_score") or measurements.get("EDDM_SCORE_RATIO") or 0.0)
    event = None
    if level in {"warning", "drift"}:
        event = {
            "eventStart": bucket["window_start"],
            "eventEnd": bucket["window_end"],
            "eventLevel": level,
            "eventTitle": "EDDM error-distance drift detected" if level == "drift" else "EDDM error-distance warning",
        }

    return {
        "runStatus": "success",
        "level": level,
        "score": score,
        "event": event,
        "nextState": next_state,
        "metrics": {
            "errorRate": error_rate,
            "previousErrorRate": previous_state.get("lastErrorRate"),
            "threshold": algorithm_result.get("threshold"),
            "measurements": measurements,
            "pValue": algorithm_result.get("p_value"),
            "testStatistic": algorithm_result.get("test_statistic"),
        },
        "diagnostics": {
            "runtime": assignment["runtime_method_key"],
            "implementation": "drift_algorithm_impl_eddm",
            "algorithmImplAttempted": True,
            "algorithmImplSucceeded": True,
            "algorithmSeverity": algorithm_result.get("severity"),
            "algorithmWarnings": algorithm_result.get("warnings", []),
            "algorithmInterpretation": algorithm_result.get("interpretation"),
            "algorithmMetadata": algorithm_result.get("metadata", {}),
            "referenceWindow": algorithm_result.get("referenceWindow"),
            "currentWindow": algorithm_result.get("currentWindow"),
        },
        "payloadHints": {"highlightBucketEnd": bucket["window_end"]},
    }
