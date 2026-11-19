from __future__ import annotations

import json
from typing import Any

from drift_server.app.runtime_methods.adwin_mean_stream import _drift_result_to_dict
from drift_server.app.runtime_methods.error_rate_stream_common import ensure_algorithm_impl_path


DETECTOR_BY_VARIANT: dict[str, str] = {
    "MANN_WHITNEY_TWO_SIDED": "detect_mann_whitney_u_wilcoxon_rank_sum_test",
    "MANN_WHITNEY_ONE_SIDED": "detect_mann_whitney_u_wilcoxon_rank_sum_test",
    "MANN_WHITNEY_EXACT": "detect_mann_whitney_u_wilcoxon_rank_sum_test",
    "ONE_SAMPLE_T_TEST": "detect_t_test",
    "TWO_SAMPLE_STUDENT_T_TEST": "detect_t_test",
    "WELCH_T_TEST": "detect_t_test",
    "PAIRED_T_TEST": "detect_t_test",
    "BWS_TWO_SAMPLE": "detect_baumgartner_weiss_schindler_test",
    "BWS_EXACT_OR_ASYMPTOTIC": "detect_baumgartner_weiss_schindler_test",
    "BWS_RANK_BASED": "detect_baumgartner_weiss_schindler_test",
    "F_TEST_EQUAL_VARIANCE": "detect_f_test_variance_test",
    "ANOVA_F_TEST_GROUP_MEAN": "detect_f_test_variance_test",
    "MODEL_COMPARISON_F_TEST": "detect_f_test_variance_test",
    "LEVENE_MEAN_CENTER": "detect_levene_s_test",
    "BROWN_FORSYTHE_MEDIAN_CENTER": "detect_levene_s_test",
    "TRIMMED_MEAN_LEVENE": "detect_levene_s_test",
}


# @managed-contract contract_id=runtime_methods.generic_statistical_test_window.run_generic_statistical_test_window level=P0
def run_generic_statistical_test_window(
    assignment: Any, bucket: dict[str, Any], previous_state: dict[str, Any]
) -> dict[str, Any]:
    params = json.loads(assignment["params_json"])
    values = _bucket_values(bucket)
    next_state = {
        "lastBucketEnd": bucket["window_end"],
        "seenBuckets": int(previous_state.get("seenBuckets", 0)) + 1,
        "lastRowCount": len(values),
    }
    if len(values) < 2:
        return _normal_output(assignment, bucket, next_state, "insufficient_values", False, {})

    algorithm_result = _run_algorithm_impl(params, values)
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
            "pair_id": row.get("pair_id"),
        }
        for row in payload.get("values", [])
    ]


def _run_algorithm_impl(params: dict[str, Any], values: list[dict[str, Any]]) -> dict[str, Any]:
    if params.get("useAlgorithmImpl", True) is False:
        return {
            "status": "disabled",
            "attempted": False,
            "algorithmImpl": "drift_algorithm_impl_statistical_test",
            "fallbackReason": "useAlgorithmImpl=false",
        }
    variant_id = str(params.get("variant_id") or "").upper()
    if not variant_id:
        return {
            "status": "not_applicable",
            "attempted": False,
            "algorithmImpl": "drift_algorithm_impl_statistical_test",
            "fallbackReason": "variant_id is required",
        }
    detector_name = DETECTOR_BY_VARIANT.get(variant_id)
    if not detector_name:
        return {
            "status": "not_applicable",
            "attempted": False,
            "algorithmImpl": "drift_algorithm_impl_statistical_test",
            "fallbackReason": f"unsupported statistical test variant: {variant_id}",
        }

    import_result = _import_detector(detector_name)
    if import_result["status"] != "success":
        return import_result
    detector = import_result["detector"]
    try:
        import pandas as pd
    except Exception as exc:  # noqa: BLE001
        return {
            "status": "import_error",
            "attempted": True,
            "algorithmImpl": "drift_algorithm_impl_statistical_test",
            "fallbackReason": f"pandas import failed: {exc}",
        }

    reference_times = [row["time"] for row in values if row.get("period") == "reference"]
    current_times = [row["time"] for row in values if row.get("period") == "current"]
    if not reference_times or not current_times:
        return {
            "status": "not_applicable",
            "attempted": True,
            "algorithmImpl": "drift_algorithm_impl_statistical_test",
            "fallbackReason": "reference/current periods are required",
        }

    algorithm_params = _algorithm_params(params, variant_id)
    pair_col = algorithm_params.get("pair_col")
    records = [{"time": row["time"], "value": row["value"]} for row in values]
    if pair_col:
        for record, row in zip(records, values, strict=False):
            record[str(pair_col)] = row.get("pair_id")
    data = pd.DataFrame(records)
    try:
        result = detector(
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
            "algorithmImpl": "drift_algorithm_impl_statistical_test",
            "fallbackReason": f"{exc.__class__.__name__}: {exc}",
        }

    result_dict = _drift_result_to_dict(result)
    if result_dict.get("severity") == "not_applicable":
        return {
            "status": "not_applicable",
            "attempted": True,
            "algorithmImpl": "drift_algorithm_impl_statistical_test",
            "fallbackReason": result_dict.get("interpretation") or "not_applicable",
            **result_dict,
        }
    if result_dict.get("severity") == "error":
        return {
            "status": "error",
            "attempted": True,
            "algorithmImpl": "drift_algorithm_impl_statistical_test",
            "fallbackReason": result_dict.get("interpretation") or "algorithm_error",
            **result_dict,
        }
    return {
        "status": "success",
        "attempted": True,
        "algorithmImpl": "drift_algorithm_impl_statistical_test",
        "referenceWindow": (min(reference_times), max(reference_times)),
        "currentWindow": (min(current_times), max(current_times)),
        **result_dict,
    }


def _import_detector(detector_name: str) -> dict[str, Any]:
    ensure_algorithm_impl_path()
    try:
        from drift_algorithm.methods import batchdistributioncomparison as methods
    except Exception as exc:  # noqa: BLE001
        return {
            "status": "import_error",
            "attempted": True,
            "algorithmImpl": "drift_algorithm_impl_statistical_test",
            "fallbackReason": f"batchdistributioncomparison import failed: {exc}",
        }
    detector = getattr(methods, detector_name, None)
    if not callable(detector):
        return {
            "status": "import_error",
            "attempted": True,
            "algorithmImpl": "drift_algorithm_impl_statistical_test",
            "fallbackReason": f"{detector_name} not found",
        }
    return {"status": "success", "detector": detector}


def _algorithm_params(params: dict[str, Any], variant_id: str) -> dict[str, Any]:
    excluded = {"useAlgorithmImpl", "fallbackOnNotApplicable"}
    algorithm_params = {key: value for key, value in params.items() if key not in excluded}
    algorithm_params["variant_id"] = variant_id
    algorithm_params.setdefault("value_col", "value")
    if variant_id == "MANN_WHITNEY_ONE_SIDED":
        algorithm_params.setdefault("alternative", "greater")
    return algorithm_params


# @managed-contract contract_id=runtime_methods.generic_statistical_test_window._convert_drift_result level=P0
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
    statistic = float(
        algorithm_result.get("drift_score")
        or algorithm_result.get("test_statistic")
        or measurements.get("TEST_STATISTIC")
        or measurements.get("STATISTIC")
        or measurements.get("U_STATISTIC")
        or measurements.get("T_STATISTIC")
        or measurements.get("F_STATISTIC")
        or measurements.get("LEVENE_STATISTIC")
        or measurements.get("BWS_STATISTIC")
        or 0.0
    )
    level = "drift" if drift_detected is True else "normal"
    event = None
    if level == "drift":
        event = {
            "eventStart": bucket["window_start"],
            "eventEnd": bucket["window_end"],
            "eventLevel": "drift",
            "eventTitle": "Statistical test drift detected",
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
            "implementation": "drift_algorithm_impl_statistical_test",
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
        "metrics": {"statistic": 0.0, "threshold": None, "measurements": {}},
        "diagnostics": {
            "runtime": assignment["runtime_method_key"],
            "implementation": "deterministic_fallback",
            "algorithmImplAttempted": attempted,
            "reason": reason,
            **diagnostics,
        },
        "payloadHints": {"highlightBucketEnd": bucket["window_end"]},
    }
