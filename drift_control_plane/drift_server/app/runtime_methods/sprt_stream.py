from __future__ import annotations

import json
from typing import Any

from drift_server.app.runtime_methods.adwin_mean_stream import (
    _append_bucket_point,
    _drift_result_to_dict,
    _next_state,
    _normal_output,
    _split_windows,
)
from drift_server.app.runtime_methods.error_rate_stream_common import (
    append_error_points,
    bucket_error_points,
    bucket_error_rate,
    ensure_algorithm_impl_path,
    next_error_state,
)


# @managed-contract contract_id=runtime_methods.sprt_stream.run_sprt_stream level=P0
def run_sprt_stream(assignment: Any, bucket: dict[str, Any], previous_state: dict[str, Any]) -> dict[str, Any]:
    params = json.loads(assignment["params_json"])
    variant_id = str(params.get("variant_id", "SPRT_BERNOULLI_ERROR_RATE")).upper()
    if variant_id == "SPRT_BERNOULLI_ERROR_RATE":
        return _run_bernoulli_error_rate_stream(assignment, bucket, previous_state, params)
    return _run_gaussian_mean_stream(assignment, bucket, previous_state, params)


def _run_bernoulli_error_rate_stream(
    assignment: Any, bucket: dict[str, Any], previous_state: dict[str, Any], params: dict[str, Any]
) -> dict[str, Any]:
    bucket_errors = bucket_error_points(bucket)
    points = append_error_points(previous_state, bucket_errors, params)
    error_rate = bucket_error_rate(bucket, bucket_errors)
    next_state = next_error_state(previous_state, bucket, points, error_rate)

    if len(points) < 2:
        return _normal_output(
            assignment,
            bucket,
            next_state,
            error_rate,
            previous_state.get("lastErrorRate"),
            "state initialized",
            {
                "implementation": "drift_algorithm_impl_sprt",
                "algorithmImplAttempted": False,
                "fallbackReason": "insufficient_points",
            },
        )

    algorithm_result = _run_algorithm_impl(params, [{"time": point["time"], "value": point["error"]} for point in points])
    if algorithm_result["status"] == "success":
        converted = _convert_drift_result(assignment, bucket, next_state, error_rate, previous_state, algorithm_result)
        if converted is not None:
            converted["metrics"]["errorRate"] = error_rate
            converted["metrics"]["previousErrorRate"] = previous_state.get("lastErrorRate")
            return converted

    return _fallback_output(
        assignment,
        bucket,
        next_state,
        error_rate,
        previous_state.get("lastErrorRate"),
        params,
        algorithm_result,
        "SPRT error-rate drift detected",
    )


def _run_gaussian_mean_stream(
    assignment: Any, bucket: dict[str, Any], previous_state: dict[str, Any], params: dict[str, Any]
) -> dict[str, Any]:
    current_mean = float(bucket["mean_value"])
    points = _append_bucket_point(previous_state, bucket, current_mean, params)
    next_state = _next_state(previous_state, bucket, current_mean, points)

    if len(points) < 2:
        return _normal_output(
            assignment,
            bucket,
            next_state,
            current_mean,
            previous_state.get("lastMean"),
            "state initialized",
            {
                "implementation": "drift_algorithm_impl_sprt",
                "algorithmImplAttempted": False,
                "fallbackReason": "insufficient_points",
            },
        )

    algorithm_result = _run_algorithm_impl(params, points)
    if algorithm_result["status"] == "success":
        converted = _convert_drift_result(assignment, bucket, next_state, current_mean, previous_state, algorithm_result)
        if converted is not None:
            converted["metrics"]["mean"] = current_mean
            converted["metrics"]["previousMean"] = previous_state.get("lastMean")
            return converted

    return _fallback_output(
        assignment,
        bucket,
        next_state,
        current_mean,
        previous_state.get("lastMean"),
        params,
        algorithm_result,
        "SPRT Gaussian mean drift detected",
    )


def _run_algorithm_impl(params: dict[str, Any], points: list[dict[str, Any]]) -> dict[str, Any]:
    if params.get("useAlgorithmImpl", True) is False:
        return {
            "status": "disabled",
            "attempted": False,
            "algorithmImpl": "drift_algorithm_impl_sprt",
            "fallbackReason": "useAlgorithmImpl=false",
        }
    ensure_algorithm_impl_path()
    try:
        from drift_algorithm.methods.streamingchangedetector import detect_sprt
    except Exception as exc:  # noqa: BLE001
        return {
            "status": "import_error",
            "attempted": True,
            "algorithmImpl": "drift_algorithm_impl_sprt",
            "fallbackReason": f"detect_sprt import failed: {exc}",
        }
    try:
        import pandas as pd
    except Exception as exc:  # noqa: BLE001
        return {
            "status": "import_error",
            "attempted": True,
            "algorithmImpl": "drift_algorithm_impl_sprt",
            "fallbackReason": f"pandas import failed: {exc}",
        }

    data = pd.DataFrame([{"time": point["time"], "value": point["value"]} for point in points])
    reference_window, current_window = _split_windows(points)
    algorithm_params = _algorithm_params(params)
    try:
        result = detect_sprt(
            data,
            time_col="time",
            value_col="value",
            reference_window=reference_window,
            current_window=current_window,
            params=algorithm_params,
        )
    except Exception as exc:  # noqa: BLE001
        return {
            "status": "exception",
            "attempted": True,
            "algorithmImpl": "drift_algorithm_impl_sprt",
            "fallbackReason": f"{exc.__class__.__name__}: {exc}",
        }

    result_dict = _drift_result_to_dict(result)
    if result_dict.get("severity") == "not_applicable":
        return {
            "status": "not_applicable",
            "attempted": True,
            "algorithmImpl": "drift_algorithm_impl_sprt",
            "fallbackReason": result_dict.get("interpretation") or "not_applicable",
            **result_dict,
        }
    if result_dict.get("severity") == "error":
        return {
            "status": "error",
            "attempted": True,
            "algorithmImpl": "drift_algorithm_impl_sprt",
            "fallbackReason": result_dict.get("interpretation") or "algorithm_error",
            **result_dict,
        }
    return {
        "status": "success",
        "attempted": True,
        "algorithmImpl": "drift_algorithm_impl_sprt",
        "referenceWindow": reference_window,
        "currentWindow": current_window,
        **result_dict,
    }


def _algorithm_params(params: dict[str, Any]) -> dict[str, Any]:
    excluded = {"meanShiftThreshold", "errorRateShiftThreshold", "maxStatePoints", "useAlgorithmImpl"}
    algorithm_params = {key: value for key, value in params.items() if key not in excluded}
    variant_id = str(algorithm_params.get("variant_id", "SPRT_BERNOULLI_ERROR_RATE")).upper()
    algorithm_params["variant_id"] = variant_id
    if variant_id == "SPRT_BERNOULLI_ERROR_RATE":
        algorithm_params.setdefault("error_col", "value")
    return algorithm_params


# @managed-contract contract_id=runtime_methods.sprt_stream._convert_drift_result level=P0
def _convert_drift_result(
    assignment: Any,
    bucket: dict[str, Any],
    next_state: dict[str, Any],
    current_value: float,
    previous_state: dict[str, Any],
    algorithm_result: dict[str, Any],
) -> dict[str, Any] | None:
    drift_detected = algorithm_result.get("drift_detected")
    if drift_detected is None:
        return None

    severity = algorithm_result.get("severity")
    level = "drift" if drift_detected is True else ("warning" if severity == "watch" else "normal")
    measurements = algorithm_result.get("measurements", {})
    score = float(
        algorithm_result.get("drift_score")
        or measurements.get("LOG_LIKELIHOOD_RATIO")
        or measurements.get("ALARM_COUNT")
        or 0.0
    )
    event = None
    if level in {"warning", "drift"}:
        event = {
            "eventStart": bucket["window_start"],
            "eventEnd": bucket["window_end"],
            "eventLevel": level,
            "eventTitle": "SPRT drift detected" if level == "drift" else "SPRT watch state",
        }

    return {
        "runStatus": "success",
        "level": level,
        "score": score,
        "event": event,
        "nextState": next_state,
        "metrics": {
            "value": current_value,
            "previousValue": previous_state.get("lastMean") or previous_state.get("lastErrorRate"),
            "threshold": algorithm_result.get("threshold"),
            "measurements": measurements,
            "pValue": algorithm_result.get("p_value"),
            "testStatistic": algorithm_result.get("test_statistic"),
        },
        "diagnostics": {
            "runtime": assignment["runtime_method_key"],
            "implementation": algorithm_result.get("algorithmImpl"),
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


def _fallback_output(
    assignment: Any,
    bucket: dict[str, Any],
    next_state: dict[str, Any],
    current_value: float,
    previous_value: Any,
    params: dict[str, Any],
    algorithm_result: dict[str, Any],
    event_title: str,
) -> dict[str, Any]:
    if previous_value is None:
        return _normal_output(
            assignment,
            bucket,
            next_state,
            current_value,
            previous_value,
            "state initialized",
            {"implementation": "deterministic_fallback", **_diagnostics(algorithm_result)},
        )
    threshold = float(params.get("meanShiftThreshold", params.get("errorRateShiftThreshold", 0.15)))
    score = abs(float(current_value) - float(previous_value))
    level = "drift" if score >= threshold else "normal"
    event = None
    if level == "drift":
        event = {
            "eventStart": bucket["window_start"],
            "eventEnd": bucket["window_end"],
            "eventLevel": "drift",
            "eventTitle": event_title,
        }
    return {
        "runStatus": "success",
        "level": level,
        "score": score,
        "event": event,
        "nextState": next_state,
        "metrics": {
            "value": current_value,
            "previousValue": previous_value,
            "threshold": threshold,
            "measurements": {},
        },
        "diagnostics": {
            "runtime": assignment["runtime_method_key"],
            "implementation": "deterministic_fallback",
            "reason": "value shift detected" if level == "drift" else "value shift below threshold",
            **_diagnostics(algorithm_result),
        },
        "payloadHints": {"highlightBucketEnd": bucket["window_end"]},
    }


def _diagnostics(algorithm_result: dict[str, Any]) -> dict[str, Any]:
    return {
        "algorithmImplAttempted": algorithm_result.get("attempted", True),
        "algorithmImplSucceeded": False,
        "algorithmImpl": algorithm_result.get("algorithmImpl"),
        "algorithmSeverity": algorithm_result.get("severity"),
        "algorithmWarnings": algorithm_result.get("warnings", []),
        "algorithmInterpretation": algorithm_result.get("interpretation"),
        "algorithmMetadata": algorithm_result.get("metadata", {}),
        "fallbackReason": algorithm_result.get("fallbackReason") or "algorithm_result_not_usable",
    }
