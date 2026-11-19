from __future__ import annotations

import json
from typing import Any

from drift_server.app.runtime_methods.adwin_mean_stream import _drift_result_to_dict
from drift_server.app.runtime_methods.error_rate_stream_common import ensure_algorithm_impl_path


DETECTOR_BY_VARIANT: dict[str, str] = {
    "CATEGORICAL_PSI": "detect_psi",
    "POPULATION_WEIGHTED_PSI": "detect_psi",
    "DISCRETE_KL_DIVERGENCE": "detect_kl_divergence",
    "HISTOGRAM_KL_DIVERGENCE": "detect_kl_divergence",
    "SMOOTHED_KL_DIVERGENCE": "detect_kl_divergence",
    "SYMMETRIZED_KL": "detect_kl_divergence",
    "JENSEN_SHANNON_DIVERGENCE": "detect_jensen_shannon_distance",
    "JENSEN_SHANNON_DISTANCE": "detect_jensen_shannon_distance",
    "MULTICLASS_PROBABILITY_JS": "detect_jensen_shannon_distance",
    "TEXT_TOPIC_JS": "detect_jensen_shannon_distance",
    "DISCRETE_HELLINGER_DISTANCE": "detect_hellinger_distance",
    "HISTOGRAM_HELLINGER_DISTANCE": "detect_hellinger_distance",
    "CATEGORICAL_HELLINGER_DISTANCE": "detect_hellinger_distance",
    "CATEGORICAL_TOTAL_VARIATION": "detect_total_variation_distance",
    "HISTOGRAM_TOTAL_VARIATION": "detect_total_variation_distance",
    "PROBABILITY_VECTOR_TOTAL_VARIATION": "detect_total_variation_distance",
    "CATEGORICAL_L_INFINITY": "detect_l_infinity_distance",
    "PROBABILITY_VECTOR_L_INFINITY": "detect_l_infinity_distance",
    "BINNED_NUMERIC_L_INFINITY": "detect_l_infinity_distance",
    "DISCRETE_BHATTACHARYYA_DISTANCE": "detect_bhattacharyya_distance",
    "GAUSSIAN_BHATTACHARYYA_DISTANCE": "detect_bhattacharyya_distance",
    "HISTOGRAM_BHATTACHARYYA_DISTANCE": "detect_bhattacharyya_distance",
    "HINC_CATEGORICAL": "detect_histogram_intersection_normalized_complement",
    "HINC_HISTOGRAM_NUMERIC": "detect_histogram_intersection_normalized_complement",
    "HINC_IMAGE_FEATURE": "detect_histogram_intersection_normalized_complement",
}

NUMERIC_VARIANTS = {
    "HISTOGRAM_KL_DIVERGENCE",
    "HISTOGRAM_HELLINGER_DISTANCE",
    "HISTOGRAM_TOTAL_VARIATION",
    "BINNED_NUMERIC_L_INFINITY",
    "GAUSSIAN_BHATTACHARYYA_DISTANCE",
    "HISTOGRAM_BHATTACHARYYA_DISTANCE",
    "HINC_HISTOGRAM_NUMERIC",
}


# @managed-contract contract_id=runtime_methods.generic_probability_distance_window.run_generic_probability_distance_window level=P0
def run_generic_probability_distance_window(
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
    values = []
    for index, row in enumerate(payload.get("values", [])):
        item = {
            "time": row.get("time"),
            "period": row.get("period"),
        }
        if row.get("value") is not None:
            item["value"] = float(row.get("value") or 0.0)
        category = row.get("category", row.get("label", row.get("bin")))
        if category is not None:
            item["category"] = str(category)
        elif row.get("value") is not None:
            item["category"] = str(row.get("value"))
        else:
            item["category"] = f"row_{index}"
        item["count"] = float(row.get("count", 1.0) or 0.0)
        values.append(item)
    return values


def _run_algorithm_impl(params: dict[str, Any], values: list[dict[str, Any]]) -> dict[str, Any]:
    if params.get("useAlgorithmImpl", True) is False:
        return {
            "status": "disabled",
            "attempted": False,
            "algorithmImpl": "drift_algorithm_impl_probability_distance",
            "fallbackReason": "useAlgorithmImpl=false",
        }
    variant_id = str(params.get("variant_id") or "").upper()
    if not variant_id:
        return {
            "status": "not_applicable",
            "attempted": False,
            "algorithmImpl": "drift_algorithm_impl_probability_distance",
            "fallbackReason": "variant_id is required",
        }
    detector_name = DETECTOR_BY_VARIANT.get(variant_id)
    if not detector_name:
        return {
            "status": "not_applicable",
            "attempted": False,
            "algorithmImpl": "drift_algorithm_impl_probability_distance",
            "fallbackReason": f"unsupported probability distance variant: {variant_id}",
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
            "algorithmImpl": "drift_algorithm_impl_probability_distance",
            "fallbackReason": f"pandas import failed: {exc}",
        }

    reference_times = [row["time"] for row in values if row.get("period") == "reference"]
    current_times = [row["time"] for row in values if row.get("period") == "current"]
    if not reference_times or not current_times:
        return {
            "status": "not_applicable",
            "attempted": True,
            "algorithmImpl": "drift_algorithm_impl_probability_distance",
            "fallbackReason": "reference/current periods are required",
        }

    records = []
    for row in values:
        record = {
            "time": row["time"],
            "category": row["category"],
            "count": row["count"],
        }
        if "value" in row:
            record["value"] = row["value"]
        records.append(record)
    data = pd.DataFrame(records)
    algorithm_params = _algorithm_params(params, variant_id)
    try:
        result = detector(
            data,
            time_col="time",
            value_col="value" if variant_id in NUMERIC_VARIANTS else "category",
            reference_window=(min(reference_times), max(reference_times)),
            current_window=(min(current_times), max(current_times)),
            params=algorithm_params,
        )
    except Exception as exc:  # noqa: BLE001
        return {
            "status": "exception",
            "attempted": True,
            "algorithmImpl": "drift_algorithm_impl_probability_distance",
            "fallbackReason": f"{exc.__class__.__name__}: {exc}",
        }

    result_dict = _drift_result_to_dict(result)
    if result_dict.get("severity") == "not_applicable":
        return {
            "status": "not_applicable",
            "attempted": True,
            "algorithmImpl": "drift_algorithm_impl_probability_distance",
            "fallbackReason": result_dict.get("interpretation") or "not_applicable",
            **result_dict,
        }
    if result_dict.get("severity") == "error":
        return {
            "status": "error",
            "attempted": True,
            "algorithmImpl": "drift_algorithm_impl_probability_distance",
            "fallbackReason": result_dict.get("interpretation") or "algorithm_error",
            **result_dict,
        }
    return {
        "status": "success",
        "attempted": True,
        "algorithmImpl": "drift_algorithm_impl_probability_distance",
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
            "algorithmImpl": "drift_algorithm_impl_probability_distance",
            "fallbackReason": f"batchdistributioncomparison import failed: {exc}",
        }
    detector = getattr(methods, detector_name, None)
    if not callable(detector):
        return {
            "status": "import_error",
            "attempted": True,
            "algorithmImpl": "drift_algorithm_impl_probability_distance",
            "fallbackReason": f"{detector_name} not found",
        }
    return {"status": "success", "detector": detector}


def _algorithm_params(params: dict[str, Any], variant_id: str) -> dict[str, Any]:
    excluded = {"useAlgorithmImpl", "fallbackOnNotApplicable"}
    algorithm_params = {key: value for key, value in params.items() if key not in excluded}
    algorithm_params["variant_id"] = variant_id
    if variant_id in NUMERIC_VARIANTS:
        algorithm_params.setdefault("value_col", "value")
    else:
        algorithm_params.setdefault("category_col", "category")
        algorithm_params.setdefault("count_col", "count")
    return algorithm_params


# @managed-contract contract_id=runtime_methods.generic_probability_distance_window._convert_drift_result level=P0
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
        reference_count = measurements.get("REFERENCE_SAMPLE_SIZE", measurements.get("SAMPLE_SIZE_REFERENCE", 0))
        current_count = measurements.get("CURRENT_SAMPLE_SIZE", measurements.get("SAMPLE_SIZE_CURRENT", 0))
        measurements["PROCESSED_COUNT"] = int(float(reference_count or 0) + float(current_count or 0))
    statistic = float(
        algorithm_result.get("drift_score")
        or algorithm_result.get("test_statistic")
        or measurements.get("TEST_STATISTIC")
        or measurements.get("PSI_SCORE")
        or measurements.get("KL_DIVERGENCE")
        or measurements.get("JENSEN_SHANNON_DISTANCE")
        or measurements.get("JENSEN_SHANNON_DIVERGENCE")
        or measurements.get("HELLINGER_DISTANCE")
        or measurements.get("TOTAL_VARIATION_DISTANCE")
        or measurements.get("L_INFINITY_DISTANCE")
        or measurements.get("BHATTACHARYYA_DISTANCE")
        or measurements.get("HISTOGRAM_INTERSECTION_NORMALIZED_COMPLEMENT")
        or 0.0
    )
    level = "drift" if drift_detected is True else "normal"
    event = None
    if level == "drift":
        event = {
            "eventStart": bucket["window_start"],
            "eventEnd": bucket["window_end"],
            "eventLevel": "drift",
            "eventTitle": "Probability distance drift detected",
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
            "implementation": "drift_algorithm_impl_probability_distance",
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
