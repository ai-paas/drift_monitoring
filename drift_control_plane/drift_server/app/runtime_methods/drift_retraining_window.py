from __future__ import annotations

import json
from typing import Any

from drift_server.app.runtime_methods.adwin_mean_stream import _drift_result_to_dict
from drift_server.app.runtime_methods.error_rate_stream_common import ensure_algorithm_impl_path
from drift_server.app.runtime_methods.multivariate_process_window import _bucket_values


# @managed-contract contract_id=runtime_methods.drift_retraining_window.run_drift_retraining_window level=P0
def run_drift_retraining_window(
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


def _run_algorithm_impl(
    params: dict[str, Any],
    values: list[dict[str, Any]],
    feature_columns: list[str],
) -> dict[str, Any]:
    if params.get("useAlgorithmImpl", True) is False:
        return {
            "status": "disabled",
            "attempted": False,
            "algorithmImpl": "drift_algorithm_impl_drift_retraining_classifier",
            "fallbackReason": "useAlgorithmImpl=false",
        }
    ensure_algorithm_impl_path()
    try:
        from drift_algorithm.methods.operationaladaptationmethod import detect_driftretrainingclassifier
    except Exception as exc:  # noqa: BLE001
        return {
            "status": "import_error",
            "attempted": True,
            "algorithmImpl": "drift_algorithm_impl_drift_retraining_classifier",
            "fallbackReason": f"detect_driftretrainingclassifier import failed: {exc}",
        }
    try:
        import pandas as pd
    except Exception as exc:  # noqa: BLE001
        return {
            "status": "import_error",
            "attempted": True,
            "algorithmImpl": "drift_algorithm_impl_drift_retraining_classifier",
            "fallbackReason": f"pandas import failed: {exc}",
        }

    reference_times = [row["time"] for row in values if row.get("period") == "reference"]
    current_times = [row["time"] for row in values if row.get("period") == "current"]
    if not reference_times or not current_times:
        return {
            "status": "not_applicable",
            "attempted": True,
            "algorithmImpl": "drift_algorithm_impl_drift_retraining_classifier",
            "fallbackReason": "reference/current periods are required",
        }

    data = pd.DataFrame(values)
    algorithm_params = _algorithm_params(params, feature_columns)
    try:
        result = detect_driftretrainingclassifier(
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
            "algorithmImpl": "drift_algorithm_impl_drift_retraining_classifier",
            "fallbackReason": f"{exc.__class__.__name__}: {exc}",
        }

    result_dict = _drift_result_to_dict(result)
    if result_dict.get("severity") == "not_applicable":
        return {
            "status": "not_applicable",
            "attempted": True,
            "algorithmImpl": "drift_algorithm_impl_drift_retraining_classifier",
            "fallbackReason": result_dict.get("interpretation") or "not_applicable",
            **result_dict,
        }
    if result_dict.get("severity") == "error":
        return {
            "status": "error",
            "attempted": True,
            "algorithmImpl": "drift_algorithm_impl_drift_retraining_classifier",
            "fallbackReason": result_dict.get("interpretation") or "algorithm_error",
            **result_dict,
        }
    return {
        "status": "success",
        "attempted": True,
        "algorithmImpl": "drift_algorithm_impl_drift_retraining_classifier",
        "referenceWindow": (min(reference_times), max(reference_times)),
        "currentWindow": (min(current_times), max(current_times)),
        **result_dict,
    }


def _algorithm_params(params: dict[str, Any], feature_columns: list[str]) -> dict[str, Any]:
    excluded = {"useAlgorithmImpl", "fallbackOnNotApplicable"}
    algorithm_params = {key: value for key, value in params.items() if key not in excluded}
    algorithm_params.setdefault("variant_id", "DRIFT_RETRAINING_WITH_ADWIN")
    algorithm_params["variant_id"] = str(algorithm_params["variant_id"]).upper()
    algorithm_params.setdefault("metric_col", "metric" if "metric" in feature_columns else feature_columns[0])
    algorithm_params.setdefault("champion_metric_col", "champion_metric")
    algorithm_params.setdefault("challenger_metric_col", "challenger_metric")
    return algorithm_params


# @managed-contract contract_id=runtime_methods.drift_retraining_window._convert_drift_result level=P0
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
        reference_count = measurements.get("REFERENCE_SAMPLE_SIZE", 0)
        current_count = measurements.get("CURRENT_SAMPLE_SIZE", 0)
        measurements["PROCESSED_COUNT"] = int(float(reference_count or 0) + float(current_count or 0))
    statistic = float(
        algorithm_result.get("drift_score")
        or algorithm_result.get("test_statistic")
        or measurements.get("TEST_STATISTIC")
        or measurements.get("METRIC_MEAN_DELTA")
        or measurements.get("CHAMPION_CHALLENGER_UPLIFT")
        or 0.0
    )
    level = "drift" if drift_detected is True else "normal"
    event = None
    if level == "drift":
        event = {
            "eventStart": bucket["window_start"],
            "eventEnd": bucket["window_end"],
            "eventLevel": "drift",
            "eventTitle": "Drift retraining workflow drift detected",
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
            "implementation": "drift_algorithm_impl_drift_retraining_classifier",
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
            "implementation": "drift_algorithm_impl_drift_retraining_classifier",
            "algorithmImplAttempted": attempted,
            "reason": reason,
            **diagnostics,
        },
        "payloadHints": {"highlightBucketEnd": bucket["window_end"]},
    }
