from __future__ import annotations

import json
from typing import Any

from drift_server.app.runtime_methods.adwin_mean_stream import (
    _append_bucket_point,
    _drift_result_to_dict,
    _fallback_output,
    _next_state,
    _normal_output,
    _split_windows,
)
from drift_server.app.runtime_methods.error_rate_stream_common import ensure_algorithm_impl_path


# @managed-contract contract_id=runtime_methods.bocd_stream.run_bocd_stream level=P0
def run_bocd_stream(assignment: Any, bucket: dict[str, Any], previous_state: dict[str, Any]) -> dict[str, Any]:
    params = json.loads(assignment["params_json"])
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
                "implementation": "drift_algorithm_impl_bocd",
                "algorithmImplAttempted": False,
                "fallbackReason": "insufficient_points",
            },
        )

    algorithm_result = _run_algorithm_impl(params, points)
    if algorithm_result["status"] == "success":
        converted = _convert_drift_result(assignment, bucket, next_state, current_mean, previous_state, algorithm_result)
        if converted is not None:
            return converted
    if algorithm_result["status"] == "not_applicable":
        return _normal_output(
            assignment,
            bucket,
            next_state,
            current_mean,
            previous_state.get("lastMean"),
            algorithm_result.get("fallbackReason") or "algorithm_not_applicable",
            {
                "implementation": "drift_algorithm_impl_bocd",
                "algorithmImplAttempted": algorithm_result.get("attempted", True),
                "algorithmImplSucceeded": False,
                "algorithmImpl": algorithm_result.get("algorithmImpl"),
                "algorithmSeverity": algorithm_result.get("severity"),
                "algorithmWarnings": algorithm_result.get("warnings", []),
                "algorithmInterpretation": algorithm_result.get("interpretation"),
                "algorithmMetadata": algorithm_result.get("metadata", {}),
                "fallbackReason": algorithm_result.get("fallbackReason") or "algorithm_not_applicable",
            },
        )

    return _fallback_output(
        assignment,
        bucket,
        next_state,
        current_mean,
        previous_state.get("lastMean"),
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
    )


def _run_algorithm_impl(params: dict[str, Any], points: list[dict[str, Any]]) -> dict[str, Any]:
    if params.get("useAlgorithmImpl", True) is False:
        return {
            "status": "disabled",
            "attempted": False,
            "algorithmImpl": "drift_algorithm_impl_bocd",
            "fallbackReason": "useAlgorithmImpl=false",
        }
    ensure_algorithm_impl_path()
    try:
        from drift_algorithm.methods.streamingchangedetector import detect_bocd
    except Exception as exc:  # noqa: BLE001
        return {
            "status": "import_error",
            "attempted": True,
            "algorithmImpl": "drift_algorithm_impl_bocd",
            "fallbackReason": f"detect_bocd import failed: {exc}",
        }
    try:
        import pandas as pd
    except Exception as exc:  # noqa: BLE001
        return {
            "status": "import_error",
            "attempted": True,
            "algorithmImpl": "drift_algorithm_impl_bocd",
            "fallbackReason": f"pandas import failed: {exc}",
        }

    data = pd.DataFrame([{"time": point["time"], "value": point["value"]} for point in points])
    reference_window, current_window = _split_windows(points)
    algorithm_params = _algorithm_params(params)
    try:
        result = detect_bocd(
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
            "algorithmImpl": "drift_algorithm_impl_bocd",
            "fallbackReason": f"{exc.__class__.__name__}: {exc}",
        }

    result_dict = _drift_result_to_dict(result)
    if result_dict.get("severity") == "not_applicable":
        return {
            "status": "not_applicable",
            "attempted": True,
            "algorithmImpl": "drift_algorithm_impl_bocd",
            "fallbackReason": result_dict.get("interpretation") or "not_applicable",
            **result_dict,
        }
    if result_dict.get("severity") == "error":
        return {
            "status": "error",
            "attempted": True,
            "algorithmImpl": "drift_algorithm_impl_bocd",
            "fallbackReason": result_dict.get("interpretation") or "algorithm_error",
            **result_dict,
        }
    return {
        "status": "success",
        "attempted": True,
        "algorithmImpl": "drift_algorithm_impl_bocd",
        "referenceWindow": reference_window,
        "currentWindow": current_window,
        **result_dict,
    }


def _algorithm_params(params: dict[str, Any]) -> dict[str, Any]:
    excluded = {"meanShiftThreshold", "maxStatePoints", "useAlgorithmImpl", "fallbackOnNotApplicable"}
    algorithm_params = {key: value for key, value in params.items() if key not in excluded}
    algorithm_params.setdefault("variant_id", "BAYESIAN_ONLINE_CHANGE_POINT_GAUSSIAN")
    return algorithm_params


# @managed-contract contract_id=runtime_methods.bocd_stream._convert_drift_result level=P0
def _convert_drift_result(
    assignment: Any,
    bucket: dict[str, Any],
    next_state: dict[str, Any],
    current_mean: float,
    previous_state: dict[str, Any],
    algorithm_result: dict[str, Any],
) -> dict[str, Any] | None:
    drift_detected = algorithm_result.get("drift_detected")
    if drift_detected is None:
        return None

    level = "drift" if drift_detected is True else "normal"
    measurements = algorithm_result.get("measurements", {})
    score = float(
        algorithm_result.get("drift_score")
        or measurements.get("MAX_CHANGE_POINT_PROBABILITY")
        or measurements.get("TEST_STATISTIC")
        or 0.0
    )
    event = None
    if level == "drift":
        event = {
            "eventStart": bucket["window_start"],
            "eventEnd": bucket["window_end"],
            "eventLevel": "drift",
            "eventTitle": "BOCD change-point drift detected",
        }

    return {
        "runStatus": "success",
        "level": level,
        "score": score,
        "event": event,
        "nextState": next_state,
        "metrics": {
            "mean": current_mean,
            "previousMean": previous_state.get("lastMean"),
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
