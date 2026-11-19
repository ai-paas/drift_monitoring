from __future__ import annotations

import json
from typing import Any

from drift_server.app.runtime_methods.adwin_mean_stream import _drift_result_to_dict
from drift_server.app.runtime_methods.error_rate_stream_common import ensure_algorithm_impl_path


# @managed-contract contract_id=runtime_methods.wasserstein_numeric_window.run_wasserstein_numeric_window level=P0
def run_wasserstein_numeric_window(
    assignment: Any, bucket: dict[str, Any], previous_state: dict[str, Any]
) -> dict[str, Any]:
    params = json.loads(assignment["params_json"])
    values = _bucket_values(bucket)
    window_values = _window_values(previous_state, values, params)
    next_state = {
        "lastBucketEnd": bucket["window_end"],
        "seenBuckets": int(previous_state.get("seenBuckets", 0)) + 1,
        "lastRowCount": len(values),
        "values": window_values,
    }
    if len(window_values) < 2:
        return _normal_output(assignment, bucket, next_state, "insufficient_values", False, {})

    algorithm_result = _run_algorithm_impl(params, window_values)
    if algorithm_result["status"] == "success":
        converted = _convert_drift_result(assignment, bucket, next_state, algorithm_result)
        if converted is not None:
            return converted

    return _fallback_output(assignment, bucket, next_state, params, algorithm_result)


def _bucket_values(bucket: dict[str, Any]) -> list[dict[str, Any]]:
    payload = bucket.get("payload") or {}
    if isinstance(payload, str):
        payload = json.loads(payload)
    return [
        {
            "time": row.get("time"),
            "value": float(row.get("value", 0.0)),
            "period": row.get("period"),
        }
        for row in payload.get("values", [])
    ]


def _window_values(previous_state: dict[str, Any], values: list[dict[str, Any]], params: dict[str, Any]) -> list[dict[str, Any]]:
    previous_values = previous_state.get("values") if isinstance(previous_state, dict) else []
    if not isinstance(previous_values, list):
        previous_values = []
    max_state_points = int(params.get("maxStatePoints") or params.get("max_state_points") or 5000)
    combined = [
        item
        for item in [*previous_values, *values]
        if isinstance(item, dict) and item.get("time") and item.get("period") in {"reference", "current"}
    ]
    if max_state_points > 0 and len(combined) > max_state_points:
        combined = combined[-max_state_points:]
    return combined


def _run_algorithm_impl(params: dict[str, Any], values: list[dict[str, Any]]) -> dict[str, Any]:
    if params.get("useAlgorithmImpl", True) is False:
        return {
            "status": "disabled",
            "attempted": False,
            "algorithmImpl": "drift_algorithm_impl_wasserstein",
            "fallbackReason": "useAlgorithmImpl=false",
        }
    import_result = _import_detect_wasserstein()
    if import_result["status"] != "success":
        return import_result
    detect_wasserstein_distance = import_result["detect_wasserstein_distance"]
    try:
        import pandas as pd
    except Exception as exc:  # noqa: BLE001
        return {
            "status": "import_error",
            "attempted": True,
            "algorithmImpl": "drift_algorithm_impl_wasserstein",
            "fallbackReason": f"pandas import failed: {exc}",
        }

    reference_times = [row["time"] for row in values if row.get("period") == "reference"]
    current_times = [row["time"] for row in values if row.get("period") == "current"]
    if not reference_times or not current_times:
        return {
            "status": "not_applicable",
            "attempted": True,
            "algorithmImpl": "drift_algorithm_impl_wasserstein",
            "fallbackReason": "reference/current periods are required",
        }

    data = pd.DataFrame([{"time": row["time"], "value": row["value"]} for row in values])
    algorithm_params = _algorithm_params(params)
    try:
        result = detect_wasserstein_distance(
            data,
            time_col="time",
            value_col="value",
            reference_window=(min(reference_times), max(reference_times)),
            current_window=(min(current_times), max(current_times)),
            params=algorithm_params,
        )
    except Exception as exc:  # noqa: BLE001
        return {
            "status": "exception",
            "attempted": True,
            "algorithmImpl": "drift_algorithm_impl_wasserstein",
            "fallbackReason": f"{exc.__class__.__name__}: {exc}",
        }

    result_dict = _drift_result_to_dict(result)
    if result_dict.get("severity") == "not_applicable":
        return {
            "status": "not_applicable",
            "attempted": True,
            "algorithmImpl": "drift_algorithm_impl_wasserstein",
            "fallbackReason": result_dict.get("interpretation") or "not_applicable",
            **result_dict,
        }
    if result_dict.get("severity") == "error":
        return {
            "status": "error",
            "attempted": True,
            "algorithmImpl": "drift_algorithm_impl_wasserstein",
            "fallbackReason": result_dict.get("interpretation") or "algorithm_error",
            **result_dict,
        }
    return {
        "status": "success",
        "attempted": True,
        "algorithmImpl": "drift_algorithm_impl_wasserstein",
        "referenceWindow": (min(reference_times), max(reference_times)),
        "currentWindow": (min(current_times), max(current_times)),
        **result_dict,
    }


def _import_detect_wasserstein() -> dict[str, Any]:
    ensure_algorithm_impl_path()
    try:
        from drift_algorithm.methods.batchdistributioncomparison import detect_wasserstein_distance
    except Exception as exc:  # noqa: BLE001
        return {
            "status": "import_error",
            "attempted": True,
            "algorithmImpl": "drift_algorithm_impl_wasserstein",
            "fallbackReason": f"detect_wasserstein_distance import failed: {exc}",
        }
    return {"status": "success", "detect_wasserstein_distance": detect_wasserstein_distance}


def _algorithm_params(params: dict[str, Any]) -> dict[str, Any]:
    excluded = {"useAlgorithmImpl", "fallbackOnNotApplicable"}
    algorithm_params = {key: value for key, value in params.items() if key not in excluded}
    algorithm_params.setdefault("variant_id", "WASSERSTEIN_1D_EXACT")
    algorithm_params.setdefault("value_col", "value")
    return algorithm_params


# @managed-contract contract_id=runtime_methods.wasserstein_numeric_window._convert_drift_result level=P0
def _convert_drift_result(
    assignment: Any,
    bucket: dict[str, Any],
    next_state: dict[str, Any],
    algorithm_result: dict[str, Any],
) -> dict[str, Any] | None:
    drift_detected = algorithm_result.get("drift_detected")
    if drift_detected is None:
        return None

    measurements = dict(algorithm_result.get("measurements", {}))
    if "PROCESSED_COUNT" not in measurements:
        reference_count = measurements.get("SAMPLE_SIZE_REFERENCE", measurements.get("REFERENCE_SAMPLE_SIZE", 0))
        current_count = measurements.get("SAMPLE_SIZE_CURRENT", measurements.get("CURRENT_SAMPLE_SIZE", 0))
        measurements["PROCESSED_COUNT"] = int(float(reference_count or 0) + float(current_count or 0))
    distance = float(
        algorithm_result.get("drift_score")
        or measurements.get("WASSERSTEIN_DISTANCE")
        or measurements.get("TEST_STATISTIC")
        or 0.0
    )
    level = "drift" if drift_detected is True else "normal"
    event = None
    if level == "drift":
        event = {
            "eventStart": bucket["window_start"],
            "eventEnd": bucket["window_end"],
            "eventLevel": "drift",
            "eventTitle": "Wasserstein distance drift detected",
        }

    return {
        "runStatus": "success",
        "level": level,
        "score": distance,
        "event": event,
        "nextState": next_state,
        "metrics": {
            "distance": distance,
            "threshold": algorithm_result.get("threshold"),
            "measurements": measurements,
            "pValue": algorithm_result.get("p_value"),
            "testStatistic": algorithm_result.get("test_statistic"),
        },
        "diagnostics": {
            "runtime": assignment["runtime_method_key"],
            "implementation": "drift_algorithm_impl_wasserstein",
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
    params: dict[str, Any],
    algorithm_result: dict[str, Any],
) -> dict[str, Any]:
    return _normal_output(
        assignment,
        bucket,
        next_state,
        algorithm_result.get("fallbackReason") or "algorithm_result_not_usable",
        algorithm_result.get("attempted", True),
        {
            "algorithmImplSucceeded": False,
            "algorithmImpl": algorithm_result.get("algorithmImpl"),
            "algorithmSeverity": algorithm_result.get("severity"),
            "algorithmWarnings": algorithm_result.get("warnings", []),
            "algorithmInterpretation": algorithm_result.get("interpretation"),
            "algorithmMetadata": algorithm_result.get("metadata", {}),
            "fallbackReason": algorithm_result.get("fallbackReason") or "algorithm_result_not_usable",
            "threshold": params.get("threshold"),
        },
    )


def _normal_output(
    assignment: Any,
    bucket: dict[str, Any],
    next_state: dict[str, Any],
    reason: str,
    attempted: bool,
    diagnostics: dict[str, Any],
) -> dict[str, Any]:
    return {
        "runStatus": "success",
        "level": "normal",
        "score": 0.0,
        "event": None,
        "nextState": next_state,
        "metrics": {"distance": 0.0, "threshold": None, "measurements": {}},
        "diagnostics": {
            "runtime": assignment["runtime_method_key"],
            "implementation": "deterministic_fallback",
            "algorithmImplAttempted": attempted,
            "reason": reason,
            **diagnostics,
        },
        "payloadHints": {"highlightBucketEnd": bucket["window_end"]},
    }
