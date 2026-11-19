from __future__ import annotations

import json
from typing import Any

from drift_server.app.runtime_methods.adwin_mean_stream import _drift_result_to_dict
from drift_server.app.runtime_methods.error_rate_stream_common import ensure_algorithm_impl_path
from drift_server.app.runtime_methods.multivariate_process_window import _bucket_values


# @managed-contract contract_id=runtime_methods.model_uncertainty_window.run_model_uncertainty_window level=P0
def run_model_uncertainty_window(
    assignment: Any, bucket: dict[str, Any], previous_state: dict[str, Any]
) -> dict[str, Any]:
    params = json.loads(assignment["params_json"])
    values, feature_columns = _bucket_values(bucket, params)
    next_state = {
        "lastBucketEnd": bucket["window_end"],
        "seenBuckets": int(previous_state.get("seenBuckets", 0)) + 1,
        "lastRowCount": len(values),
    }
    if len(values) < 2:
        return _normal_output(assignment, bucket, next_state, "insufficient_values", False, {})

    algorithm_result = _run_algorithm_impl(params, values, feature_columns)
    if algorithm_result["status"] == "success":
        converted = _convert_drift_result(assignment, bucket, next_state, algorithm_result)
        if converted is not None:
            return converted

    return _fallback_output(assignment, bucket, next_state, algorithm_result)


# @managed-contract contract_id=runtime_methods.model_uncertainty_window.run_softmax_confidence_drift level=P0
def run_softmax_confidence_drift(
    assignment: Any, bucket: dict[str, Any], previous_state: dict[str, Any]
) -> dict[str, Any]:
    params = json.loads(assignment["params_json"])
    values, feature_columns = _bucket_values(bucket, params)
    reference_limit = max(int(params.get("referenceSampleLimit", 5000)), 1)
    current_limit = max(int(params.get("currentSampleLimit", 1000)), 1)
    reference_values = _state_values(previous_state.get("referenceValues"), "reference")
    current_values = _state_values(previous_state.get("currentValues"), "current")
    reference_values.extend(row for row in values if row.get("period") == "reference")
    current_values.extend(row for row in values if row.get("period") == "current")
    reference_values = reference_values[-reference_limit:]
    current_values = current_values[-current_limit:]
    next_state = {
        "lastBucketEnd": bucket["window_end"],
        "seenBuckets": int(previous_state.get("seenBuckets", 0)) + 1,
        "lastRowCount": len(values),
        "referenceValues": reference_values,
        "currentValues": current_values,
    }

    min_reference_size = max(int(params.get("min_reference_size", 20)), 1)
    min_current_size = max(int(params.get("min_current_size", 20)), 1)
    if len(reference_values) < min_reference_size:
        return _normal_output(assignment, bucket, next_state, "building_reference_baseline", False, {})
    if len(current_values) < min_current_size:
        return _normal_output(assignment, bucket, next_state, "building_current_window", False, {})

    algorithm_result = _run_algorithm_impl(params, [*reference_values, *current_values], feature_columns)
    if algorithm_result["status"] == "success":
        converted = _convert_drift_result(assignment, bucket, next_state, algorithm_result)
        if converted is not None:
            return converted
    return _fallback_output(assignment, bucket, next_state, algorithm_result)


def _state_values(value: Any, period: str) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    return [dict(row, period=period) for row in value if isinstance(row, dict)]


def _run_algorithm_impl(
    params: dict[str, Any],
    values: list[dict[str, Any]],
    feature_columns: list[str],
) -> dict[str, Any]:
    if params.get("useAlgorithmImpl", True) is False:
        return {
            "status": "disabled",
            "attempted": False,
            "algorithmImpl": "drift_algorithm_impl_model_uncertainty_drift",
            "fallbackReason": "useAlgorithmImpl=false",
        }
    ensure_algorithm_impl_path()
    try:
        from drift_algorithm.methods.representationdriftmethod import detect_model_uncertainty_drift
    except Exception as exc:  # noqa: BLE001
        return {
            "status": "import_error",
            "attempted": True,
            "algorithmImpl": "drift_algorithm_impl_model_uncertainty_drift",
            "fallbackReason": f"detect_model_uncertainty_drift import failed: {exc}",
        }
    try:
        import pandas as pd
    except Exception as exc:  # noqa: BLE001
        return {
            "status": "import_error",
            "attempted": True,
            "algorithmImpl": "drift_algorithm_impl_model_uncertainty_drift",
            "fallbackReason": f"pandas import failed: {exc}",
        }

    reference_times = [row["time"] for row in values if row.get("period") == "reference"]
    current_times = [row["time"] for row in values if row.get("period") == "current"]
    if not reference_times or not current_times:
        return {
            "status": "not_applicable",
            "attempted": True,
            "algorithmImpl": "drift_algorithm_impl_model_uncertainty_drift",
            "fallbackReason": "reference/current periods are required",
        }

    data = pd.DataFrame(values)
    algorithm_params = _algorithm_params(params, feature_columns)
    try:
        result = detect_model_uncertainty_drift(
            data,
            time_col="time",
            reference_window=(min(reference_times), max(reference_times)),
            current_window=(min(current_times), max(current_times)),
            params=algorithm_params,
        )
    except Exception as exc:  # noqa: BLE001
        return {
            "status": "exception",
            "attempted": True,
            "algorithmImpl": "drift_algorithm_impl_model_uncertainty_drift",
            "fallbackReason": f"{exc.__class__.__name__}: {exc}",
        }

    result_dict = _drift_result_to_dict(result)
    if result_dict.get("severity") == "not_applicable":
        return {
            "status": "not_applicable",
            "attempted": True,
            "algorithmImpl": "drift_algorithm_impl_model_uncertainty_drift",
            "fallbackReason": result_dict.get("interpretation") or "not_applicable",
            **result_dict,
        }
    if result_dict.get("severity") == "error":
        return {
            "status": "error",
            "attempted": True,
            "algorithmImpl": "drift_algorithm_impl_model_uncertainty_drift",
            "fallbackReason": result_dict.get("interpretation") or "algorithm_error",
            **result_dict,
        }
    return {
        "status": "success",
        "attempted": True,
        "algorithmImpl": "drift_algorithm_impl_model_uncertainty_drift",
        "referenceWindow": (min(reference_times), max(reference_times)),
        "currentWindow": (min(current_times), max(current_times)),
        **result_dict,
    }


def _algorithm_params(params: dict[str, Any], feature_columns: list[str]) -> dict[str, Any]:
    excluded = {"useAlgorithmImpl", "fallbackOnNotApplicable"}
    algorithm_params = {key: value for key, value in params.items() if key not in excluded}
    algorithm_params.setdefault("variant_id", "SOFTMAX_CONFIDENCE_DRIFT")
    if not any(key in algorithm_params for key in ("probability_cols", "confidence_col", "prediction_cols", "variance_col")):
        algorithm_params["probability_cols"] = list(feature_columns)
    return algorithm_params


# @managed-contract contract_id=runtime_methods.model_uncertainty_window._convert_drift_result level=P0
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
        reference_count = measurements.get("SAMPLE_SIZE_REFERENCE", 0)
        current_count = measurements.get("SAMPLE_SIZE_CURRENT", 0)
        measurements["PROCESSED_COUNT"] = int(float(reference_count or 0) + float(current_count or 0))
    statistic = float(algorithm_result.get("drift_score") or measurements.get("TEST_STATISTIC") or 0.0)
    level = "drift" if drift_detected is True else "normal"
    event = None
    if level == "drift":
        event = {
            "eventStart": bucket["window_start"],
            "eventEnd": bucket["window_end"],
            "eventLevel": "drift",
            "eventTitle": "Model uncertainty drift detected",
        }

    return {
        "runStatus": "success",
        "level": level,
        "score": statistic,
        "event": event,
        "nextState": next_state,
        "metrics": {
            "statistic": statistic,
            "threshold": algorithm_result.get("threshold"),
            "measurements": measurements,
            "pValue": algorithm_result.get("p_value"),
            "testStatistic": algorithm_result.get("test_statistic"),
        },
        "diagnostics": {
            "runtime": assignment["runtime_method_key"],
            "implementation": "drift_algorithm_impl_model_uncertainty_drift",
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
        "metrics": {
            "statistic": 0.0,
            "threshold": None,
            "measurements": {},
        },
        "diagnostics": {
            "runtime": assignment["runtime_method_key"],
            "implementation": "drift_algorithm_impl_model_uncertainty_drift",
            "algorithmImplAttempted": attempted,
            "reason": reason,
            **diagnostics,
        },
        "payloadHints": {"highlightBucketEnd": bucket["window_end"]},
    }
