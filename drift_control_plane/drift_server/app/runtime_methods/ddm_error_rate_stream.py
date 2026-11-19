from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any

from drift_server.app.runtime_methods.adwin_mean_stream import _drift_result_to_dict, _json_safe, _split_windows


# @managed-contract contract_id=runtime_methods.ddm_error_rate_stream.run_ddm_error_rate_stream level=P0
def run_ddm_error_rate_stream(
    assignment: Any, bucket: dict[str, Any], previous_state: dict[str, Any]
) -> dict[str, Any]:
    params = json.loads(assignment["params_json"])
    bucket_errors = _bucket_error_points(bucket)
    points = _append_error_points(previous_state, bucket_errors, params)
    error_rate = _bucket_error_rate(bucket, bucket_errors)
    next_state = _next_state(previous_state, bucket, points, error_rate)

    if len(points) < 2:
        return _normal_output(
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

    return _fallback_output(
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
    )


def _bucket_error_points(bucket: dict[str, Any]) -> list[dict[str, Any]]:
    payload = bucket.get("payload") or {}
    if isinstance(payload, str):
        payload = json.loads(payload)
    rows = payload.get("errors") or []
    points = []
    for row in rows:
        point = {
            "time": row.get("time") or bucket["window_end"],
            "error": int(float(row.get("error", 0))),
            "bucketId": bucket["bucket_id"],
        }
        for optional_key in ("y_true", "y_pred", "confidence"):
            if optional_key in row:
                point[optional_key] = row.get(optional_key)
        points.append(point)
    return points


def _append_error_points(
    previous_state: dict[str, Any], bucket_errors: list[dict[str, Any]], params: dict[str, Any]
) -> list[dict[str, Any]]:
    points = list(previous_state.get("points", []))
    existing = {(point.get("bucketId"), point.get("time")) for point in points}
    for point in bucket_errors:
        key = (point.get("bucketId"), point.get("time"))
        if key not in existing:
            points.append(point)
            existing.add(key)
    max_state_points = int(params.get("maxStatePoints", 2000))
    return points[-max_state_points:]


def _next_state(
    previous_state: dict[str, Any], bucket: dict[str, Any], points: list[dict[str, Any]], error_rate: float
) -> dict[str, Any]:
    return {
        "lastErrorRate": error_rate,
        "previousErrorRate": previous_state.get("lastErrorRate"),
        "seenBuckets": int(previous_state.get("seenBuckets", 0)) + 1,
        "lastBucketEnd": bucket["window_end"],
        "points": points,
    }


def _bucket_error_rate(bucket: dict[str, Any], bucket_errors: list[dict[str, Any]]) -> float:
    if bucket.get("error_rate") is not None:
        return float(bucket["error_rate"])
    if bucket_errors:
        return sum(point["error"] for point in bucket_errors) / len(bucket_errors)
    return 0.0


def _run_algorithm_impl(params: dict[str, Any], points: list[dict[str, Any]]) -> dict[str, Any]:
    if params.get("useAlgorithmImpl", True) is False:
        return {
            "status": "disabled",
            "attempted": False,
            "algorithmImpl": "drift_algorithm_impl_ddm",
            "fallbackReason": "useAlgorithmImpl=false",
        }
    import_result = _import_detect_ddm()
    if import_result["status"] != "success":
        return import_result
    detect_ddm = import_result["detect_ddm"]
    try:
        import pandas as pd
    except Exception as exc:  # noqa: BLE001
        return {
            "status": "import_error",
            "attempted": True,
            "algorithmImpl": "drift_algorithm_impl_ddm",
            "fallbackReason": f"pandas import failed: {exc}",
        }

    data = pd.DataFrame(
        [
            {
                key: point.get(key)
                for key in ("time", "error", "y_true", "y_pred", "confidence")
                if key in point
            }
            for point in points
        ]
    )
    reference_window, current_window = _split_windows([{"time": point["time"], "value": point["error"]} for point in points])
    algorithm_params = _algorithm_params(params)
    try:
        result = detect_ddm(
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
            "algorithmImpl": "drift_algorithm_impl_ddm",
            "fallbackReason": f"{exc.__class__.__name__}: {exc}",
        }

    result_dict = _drift_result_to_dict(result)
    if result_dict.get("severity") == "not_applicable":
        return {
            "status": "not_applicable",
            "attempted": True,
            "algorithmImpl": "drift_algorithm_impl_ddm",
            "fallbackReason": result_dict.get("interpretation") or "not_applicable",
            **result_dict,
        }
    if result_dict.get("severity") == "error":
        return {
            "status": "error",
            "attempted": True,
            "algorithmImpl": "drift_algorithm_impl_ddm",
            "fallbackReason": result_dict.get("interpretation") or "algorithm_error",
            **result_dict,
        }
    return {
        "status": "success",
        "attempted": True,
        "algorithmImpl": "drift_algorithm_impl_ddm",
        "referenceWindow": reference_window,
        "currentWindow": current_window,
        **result_dict,
    }


def _import_detect_ddm() -> dict[str, Any]:
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
        from drift_algorithm.methods.supervisedconceptdriftdetector import detect_ddm
    except Exception as exc:  # noqa: BLE001
        return {
            "status": "import_error",
            "attempted": True,
            "algorithmImpl": "drift_algorithm_impl_ddm",
            "fallbackReason": f"detect_ddm import failed: {exc}",
        }
    return {"status": "success", "detect_ddm": detect_ddm}


def _algorithm_params(params: dict[str, Any]) -> dict[str, Any]:
    excluded = {"errorRateShiftThreshold", "maxStatePoints", "useAlgorithmImpl", "fallbackOnNotApplicable"}
    algorithm_params = {key: value for key, value in params.items() if key not in excluded}
    algorithm_params.setdefault("variant_id", "DDM_STANDARD")
    algorithm_params.setdefault("error_col", "error")
    if algorithm_params.get("variant_id") == "DDM_CLASS_SPECIFIC":
        algorithm_params.setdefault("y_true", "y_true")
        algorithm_params.setdefault("y_pred", "y_pred")
    return algorithm_params


# @managed-contract contract_id=runtime_methods.ddm_error_rate_stream._convert_drift_result level=P0
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
    score = float(algorithm_result.get("drift_score") or measurements.get("DDM_STATISTIC") or 0.0)
    event = None
    if level in {"warning", "drift"}:
        event = {
            "eventStart": bucket["window_start"],
            "eventEnd": bucket["window_end"],
            "eventLevel": level,
            "eventTitle": "DDM error-rate drift detected" if level == "drift" else "DDM error-rate warning",
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
            "implementation": "drift_algorithm_impl_ddm",
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
    error_rate: float,
    previous_error_rate: Any,
    params: dict[str, Any],
    diagnostics: dict[str, Any],
) -> dict[str, Any]:
    if previous_error_rate is None:
        return _normal_output(
            assignment,
            bucket,
            next_state,
            error_rate,
            previous_error_rate,
            "state initialized",
            {"implementation": "deterministic_fallback", **diagnostics},
        )
    threshold = float(params.get("errorRateShiftThreshold", 0.15))
    score = max(0.0, error_rate - float(previous_error_rate))
    level = "drift" if score >= threshold else "normal"
    event = None
    if level == "drift":
        event = {
            "eventStart": bucket["window_start"],
            "eventEnd": bucket["window_end"],
            "eventLevel": "drift",
            "eventTitle": "DDM error-rate drift detected",
        }
    return {
        "runStatus": "success",
        "level": level,
        "score": score,
        "event": event,
        "nextState": next_state,
        "metrics": {
            "errorRate": error_rate,
            "previousErrorRate": previous_error_rate,
            "threshold": threshold,
            "measurements": {},
        },
        "diagnostics": {
            "runtime": assignment["runtime_method_key"],
            "implementation": "deterministic_fallback",
            "reason": "error-rate shift detected" if level == "drift" else "error-rate shift below threshold",
            **diagnostics,
        },
        "payloadHints": {"highlightBucketEnd": bucket["window_end"]},
    }


def _normal_output(
    assignment: Any,
    bucket: dict[str, Any],
    next_state: dict[str, Any],
    error_rate: float,
    previous_error_rate: Any,
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
            "errorRate": error_rate,
            "previousErrorRate": previous_error_rate,
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
