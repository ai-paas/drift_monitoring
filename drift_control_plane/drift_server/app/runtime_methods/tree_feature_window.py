from __future__ import annotations

import json
from typing import Any

from drift_server.app.runtime_methods.adwin_mean_stream import _drift_result_to_dict
from drift_server.app.runtime_methods.error_rate_stream_common import ensure_algorithm_impl_path


# @managed-contract contract_id=runtime_methods.tree_feature_window.run_tree_feature_window level=P0
def run_tree_feature_window(assignment: Any, bucket: dict[str, Any], previous_state: dict[str, Any]) -> dict[str, Any]:
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


def _bucket_values(bucket: dict[str, Any], params: dict[str, Any]) -> tuple[list[dict[str, Any]], list[str]]:
    payload = bucket.get("payload") or {}
    if isinstance(payload, str):
        payload = json.loads(payload)
    feature_columns = list(params.get("feature_cols") or payload.get("featureColumns") or [])
    time_feature_col = str(params.get("time_feature_col", "period_indicator"))
    values: list[dict[str, Any]] = []
    for row in payload.get("values", []):
        features = row.get("features", {})
        item = {
            "time": row.get("time"),
            "period": row.get("period"),
            **{column: float(features.get(column, 0.0)) for column in feature_columns if column in features},
        }
        if time_feature_col in feature_columns and time_feature_col not in item:
            item[time_feature_col] = _period_indicator(row.get("period"))
        values.append(item)
    return values, feature_columns


def _period_indicator(period: Any) -> float:
    return 0.0 if str(period).lower() == "reference" else 1.0


def _run_algorithm_impl(
    params: dict[str, Any],
    values: list[dict[str, Any]],
    feature_columns: list[str],
) -> dict[str, Any]:
    if params.get("useAlgorithmImpl", True) is False:
        return {
            "status": "disabled",
            "attempted": False,
            "algorithmImpl": "drift_algorithm_impl_tree_feature",
            "fallbackReason": "useAlgorithmImpl=false",
        }
    ensure_algorithm_impl_path()
    try:
        from drift_algorithm.methods.explanationdriftmethod import detect_tree_feature
    except Exception as exc:  # noqa: BLE001
        return {
            "status": "import_error",
            "attempted": True,
            "algorithmImpl": "drift_algorithm_impl_tree_feature",
            "fallbackReason": f"detect_tree_feature import failed: {exc}",
        }
    try:
        import pandas as pd
    except Exception as exc:  # noqa: BLE001
        return {
            "status": "import_error",
            "attempted": True,
            "algorithmImpl": "drift_algorithm_impl_tree_feature",
            "fallbackReason": f"pandas import failed: {exc}",
        }

    reference_times = [row["time"] for row in values if row.get("period") == "reference"]
    current_times = [row["time"] for row in values if row.get("period") == "current"]
    if not reference_times or not current_times:
        return {
            "status": "not_applicable",
            "attempted": True,
            "algorithmImpl": "drift_algorithm_impl_tree_feature",
            "fallbackReason": "reference/current periods are required",
        }

    data = pd.DataFrame(values)
    algorithm_params = _algorithm_params(params, feature_columns)
    try:
        result = detect_tree_feature(
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
            "algorithmImpl": "drift_algorithm_impl_tree_feature",
            "fallbackReason": f"{exc.__class__.__name__}: {exc}",
        }

    result_dict = _drift_result_to_dict(result)
    if result_dict.get("severity") == "not_applicable":
        return {
            "status": "not_applicable",
            "attempted": True,
            "algorithmImpl": "drift_algorithm_impl_tree_feature",
            "fallbackReason": result_dict.get("interpretation") or "not_applicable",
            **result_dict,
        }
    if result_dict.get("severity") == "error":
        return {
            "status": "error",
            "attempted": True,
            "algorithmImpl": "drift_algorithm_impl_tree_feature",
            "fallbackReason": result_dict.get("interpretation") or "algorithm_error",
            **result_dict,
        }
    return {
        "status": "success",
        "attempted": True,
        "algorithmImpl": "drift_algorithm_impl_tree_feature",
        "referenceWindow": (min(reference_times), max(reference_times)),
        "currentWindow": (min(current_times), max(current_times)),
        **result_dict,
    }


def _algorithm_params(params: dict[str, Any], feature_columns: list[str]) -> dict[str, Any]:
    excluded = {"useAlgorithmImpl", "fallbackOnNotApplicable"}
    algorithm_params = {key: value for key, value in params.items() if key not in excluded}
    algorithm_params.setdefault("variant_id", "TIME_FEATURE_SPLIT_DETECTOR")
    algorithm_params.setdefault("feature_cols", list(feature_columns))
    return algorithm_params


# @managed-contract contract_id=runtime_methods.tree_feature_window._convert_drift_result level=P0
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
    if "PROCESSED_COUNT" not in measurements or int(float(measurements.get("PROCESSED_COUNT") or 0)) <= 0:
        reference_count = measurements.get("REFERENCE_SAMPLE_SIZE", 0)
        current_count = measurements.get("CURRENT_SAMPLE_SIZE", 0)
        measurements["PROCESSED_COUNT"] = int(float(reference_count or 0) + float(current_count or 0))
    statistic = float(algorithm_result.get("drift_score") or measurements.get("TEST_STATISTIC") or 0.0)
    level = "drift" if drift_detected is True else "normal"
    event = None
    if level == "drift":
        event = {
            "eventStart": bucket["window_start"],
            "eventEnd": bucket["window_end"],
            "eventLevel": "drift",
            "eventTitle": "Tree feature drift detected",
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
            "implementation": "drift_algorithm_impl_tree_feature",
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
            "implementation": "drift_algorithm_impl_tree_feature",
            "algorithmImplAttempted": attempted,
            "reason": reason,
            **diagnostics,
        },
        "payloadHints": {"highlightBucketEnd": bucket["window_end"]},
    }
