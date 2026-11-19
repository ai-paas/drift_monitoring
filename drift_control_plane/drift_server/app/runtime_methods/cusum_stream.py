from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any

from drift_server.app.runtime_methods.adwin_mean_stream import (
    _append_bucket_point,
    _drift_result_to_dict,
    _next_state,
    _split_windows,
)


# @managed-contract contract_id=runtime_methods.cusum_stream.run_cusum_stream level=P0
def run_cusum_stream(assignment: Any, bucket: dict[str, Any], previous_state: dict[str, Any]) -> dict[str, Any]:
    params = json.loads(assignment["params_json"])
    current_mean = float(bucket["mean_value"])
    points = _append_bucket_point(previous_state, bucket, current_mean, params)
    base_state = _next_state(previous_state, bucket, current_mean, points)

    if len(points) < 2:
        return _normal_output(
            assignment,
            bucket,
            base_state,
            current_mean,
            previous_state.get("lastMean"),
            "state initialized",
            {
                "implementation": "drift_algorithm_impl_cusum",
                "algorithmImplAttempted": False,
                "fallbackReason": "insufficient_points",
            },
        )

    algorithm_result = _run_algorithm_impl(params, points)
    if algorithm_result["status"] == "success":
        converted = _convert_drift_result(assignment, bucket, base_state, current_mean, previous_state, algorithm_result)
        if converted is not None:
            return converted

    fallback_reason = algorithm_result.get("fallbackReason") or "algorithm_result_not_usable"
    return _fallback_output(
        assignment,
        bucket,
        base_state,
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
            "fallbackReason": fallback_reason,
        },
    )


def _run_algorithm_impl(params: dict[str, Any], points: list[dict[str, Any]]) -> dict[str, Any]:
    if params.get("useAlgorithmImpl", True) is False:
        return {
            "status": "disabled",
            "attempted": False,
            "algorithmImpl": "drift_algorithm_impl_cusum",
            "fallbackReason": "useAlgorithmImpl=false",
        }

    import_result = _import_detect_cusum()
    if import_result["status"] != "success":
        return import_result

    detect_cusum = import_result["detect_cusum"]
    try:
        import pandas as pd
    except Exception as exc:  # noqa: BLE001
        return {
            "status": "import_error",
            "attempted": True,
            "algorithmImpl": "drift_algorithm_impl_cusum",
            "fallbackReason": f"pandas import failed: {exc}",
        }

    data = pd.DataFrame([{"time": point["time"], "value": point["value"]} for point in points])
    reference_window, current_window = _split_windows(points)
    algorithm_params = _algorithm_params(params)
    try:
        result = detect_cusum(
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
            "algorithmImpl": "drift_algorithm_impl_cusum",
            "fallbackReason": f"{exc.__class__.__name__}: {exc}",
        }

    result_dict = _drift_result_to_dict(result)
    if result_dict.get("severity") == "not_applicable":
        return {
            "status": "not_applicable",
            "attempted": True,
            "algorithmImpl": "drift_algorithm_impl_cusum",
            "fallbackReason": result_dict.get("interpretation") or "not_applicable",
            **result_dict,
        }
    if result_dict.get("severity") == "error":
        return {
            "status": "error",
            "attempted": True,
            "algorithmImpl": "drift_algorithm_impl_cusum",
            "fallbackReason": result_dict.get("interpretation") or "algorithm_error",
            **result_dict,
        }
    return {
        "status": "success",
        "attempted": True,
        "algorithmImpl": "drift_algorithm_impl_cusum",
        "referenceWindow": reference_window,
        "currentWindow": current_window,
        **result_dict,
    }


def _import_detect_cusum() -> dict[str, Any]:
    configured = os.environ.get("DRIFT_ALGORITHM_IMPL_PATH")
    candidates = []
    if configured:
        candidates.append(Path(configured))
    candidates.append(Path(__file__).resolve().parents[4] / "drift_algorithm_impl")

    for candidate in candidates:
        if candidate.exists():
            candidate_text = str(candidate)
            if candidate_text not in sys.path:
                sys.path.insert(0, candidate_text)
            break

    try:
        from drift_algorithm.methods.streamingchangedetector import detect_cusum
    except Exception as exc:  # noqa: BLE001
        return {
            "status": "import_error",
            "attempted": True,
            "algorithmImpl": "drift_algorithm_impl_cusum",
            "fallbackReason": f"detect_cusum import failed: {exc}",
        }
    return {"status": "success", "detect_cusum": detect_cusum}


def _algorithm_params(params: dict[str, Any]) -> dict[str, Any]:
    excluded = {"meanShiftThreshold", "maxStatePoints", "useAlgorithmImpl", "fallbackOnNotApplicable"}
    algorithm_params = {key: value for key, value in params.items() if key not in excluded}
    algorithm_params.setdefault("variant_id", "ONE_SIDED_UPPER_CUSUM")
    return algorithm_params


# @managed-contract contract_id=runtime_methods.cusum_stream._convert_drift_result level=P0
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
    score = algorithm_result.get("drift_score")
    if score is None:
        score = measurements.get("MAX_CUSUM_STATISTIC", measurements.get("CUSUM_STATISTIC", 0.0))
    score = float(score or 0.0)
    event = None
    if level == "drift":
        event = {
            "eventStart": bucket["window_start"],
            "eventEnd": bucket["window_end"],
            "eventLevel": "drift",
            "eventTitle": "CUSUM cumulative deviation drift detected",
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
            "implementation": "drift_algorithm_impl_cusum",
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
    current_mean: float,
    previous_mean: Any,
    params: dict[str, Any],
    diagnostics: dict[str, Any],
) -> dict[str, Any]:
    threshold = float(params.get("meanShiftThreshold", params.get("decision_threshold_h", 2.0)))
    if previous_mean is None:
        return _normal_output(
            assignment,
            bucket,
            next_state,
            current_mean,
            previous_mean,
            "state initialized",
            {"implementation": "deterministic_fallback", **diagnostics},
        )

    score = abs(current_mean - float(previous_mean))
    level = "drift" if score >= threshold else "normal"
    event = None
    if level == "drift":
        event = {
            "eventStart": bucket["window_start"],
            "eventEnd": bucket["window_end"],
            "eventLevel": "drift",
            "eventTitle": "CUSUM cumulative deviation drift detected",
        }

    return {
        "runStatus": "success",
        "level": level,
        "score": score,
        "event": event,
        "nextState": next_state,
        "metrics": {
            "mean": current_mean,
            "previousMean": previous_mean,
            "meanDifference": score,
            "threshold": threshold,
            "measurements": {},
        },
        "diagnostics": {
            "runtime": assignment["runtime_method_key"],
            "implementation": "deterministic_fallback",
            "reason": "mean shift detected" if level == "drift" else "mean shift below threshold",
            **diagnostics,
        },
        "payloadHints": {"highlightBucketEnd": bucket["window_end"]},
    }


def _normal_output(
    assignment: Any,
    bucket: dict[str, Any],
    next_state: dict[str, Any],
    current_mean: float,
    previous_mean: Any,
    reason: str,
    diagnostics: dict[str, Any],
) -> dict[str, Any]:
    return {
        "runStatus": "success",
        "level": "normal",
        "score": 0.0,
        "event": None,
        "nextState": next_state,
        "metrics": {
            "mean": current_mean,
            "previousMean": previous_mean,
            "meanDifference": 0.0,
            "threshold": None,
            "measurements": {},
        },
        "diagnostics": {
            "runtime": assignment["runtime_method_key"],
            "reason": reason,
            **diagnostics,
        },
        "payloadHints": {"highlightBucketEnd": bucket["window_end"]},
    }
