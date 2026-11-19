from __future__ import annotations

import json
from typing import Any

from drift_server.app.runtime_methods.adwin_mean_stream import _drift_result_to_dict
from drift_server.app.runtime_methods.error_rate_stream_common import ensure_algorithm_impl_path


DETECTOR_BY_VARIANT: dict[str, str] = {
    "ONE_SAMPLE_KS_KNOWN_CDF": "detect_ks_test",
    "TWO_SAMPLE_KS_TWO_SIDED": "detect_ks_test",
    "TWO_SAMPLE_KS_ONE_SIDED_GREATER": "detect_ks_test",
    "TWO_SAMPLE_KS_ONE_SIDED_LESS": "detect_ks_test",
    "TWO_SAMPLE_KS_EXACT_PVALUE": "detect_ks_test",
    "TWO_SAMPLE_KS_ASYMPTOTIC_PVALUE": "detect_ks_test",
    "KS_WITH_TIES_OR_DISCRETE_CAUTION": "detect_ks_test",
    "LILLIEFORS_RELATED_ONE_SAMPLE": "detect_ks_test",
    "HIGHER_ORDER_KS": "detect_ks_test",
    "TWO_SAMPLE_KS_APPROX_QUANTILE": "detect_ks_test",
    "ONE_SAMPLE_ANDERSON_DARLING": "detect_anderson_darling_test",
    "TWO_SAMPLE_ANDERSON_DARLING": "detect_anderson_darling_test",
    "K_SAMPLE_ANDERSON_DARLING": "detect_anderson_darling_test",
    "TAIL_SENSITIVE_AD": "detect_anderson_darling_test",
    "ONE_SAMPLE_CVM": "detect_cramer_von_mises_test",
    "TWO_SAMPLE_CVM": "detect_cramer_von_mises_test",
    "K_SAMPLE_CVM": "detect_cramer_von_mises_test",
    "KUIPER_TWO_SAMPLE": "detect_kuiper_s_test",
    "KUIPER_CIRCULAR_DATA": "detect_kuiper_s_test",
    "KUIPER_ONE_SAMPLE": "detect_kuiper_s_test",
    "TWO_SAMPLE_EPPS_SINGLETON": "detect_epps_singleton_test",
    "DISCRETE_EPPS_SINGLETON": "detect_epps_singleton_test",
    "ASYMPTOTIC_EPPS_SINGLETON": "detect_epps_singleton_test",
    "UNIVARIATE_ENERGY_DISTANCE": "detect_energy_distance",
    "ENERGY_DISTANCE_PERMUTATION_TEST": "detect_energy_distance",
    "MULTIVARIATE_ENERGY_DISTANCE": "detect_energy_distance",
    "LEAST_SQUARES_DENSITY_DIFFERENCE": "detect_lsdd",
    "PERMUTATION_LSDD": "detect_lsdd",
    "LSDD_WITH_PREPROCESSING": "detect_lsdd",
    "KERNEL_MMD_BIASED": "detect_mmd",
    "KERNEL_MMD_UNBIASED": "detect_mmd",
    "LINEAR_TIME_MMD": "detect_mmd",
    "STREAMING_MMD": "detect_mmd",
}


# @managed-contract contract_id=runtime_methods.generic_distribution_ecdf_window.run_generic_distribution_ecdf_window level=P0
def run_generic_distribution_ecdf_window(
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
    for row in payload.get("values", []):
        item = {
            "time": row.get("time"),
            "value": float(row.get("value", 0.0)),
            "period": row.get("period"),
        }
        features = row.get("features")
        if isinstance(features, dict):
            for key, value in features.items():
                if value not in {None, ""}:
                    item[str(key)] = float(value)
        values.append(item)
    return values


def _run_algorithm_impl(params: dict[str, Any], values: list[dict[str, Any]]) -> dict[str, Any]:
    if params.get("useAlgorithmImpl", True) is False:
        return {
            "status": "disabled",
            "attempted": False,
            "algorithmImpl": "drift_algorithm_impl_distribution_ecdf",
            "fallbackReason": "useAlgorithmImpl=false",
        }
    variant_id = str(params.get("variant_id") or "").upper()
    if not variant_id:
        return {
            "status": "not_applicable",
            "attempted": False,
            "algorithmImpl": "drift_algorithm_impl_distribution_ecdf",
            "fallbackReason": "variant_id is required",
        }
    detector_name = DETECTOR_BY_VARIANT.get(variant_id)
    if not detector_name:
        return {
            "status": "not_applicable",
            "attempted": False,
            "algorithmImpl": "drift_algorithm_impl_distribution_ecdf",
            "fallbackReason": f"unsupported distribution ECDF variant: {variant_id}",
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
            "algorithmImpl": "drift_algorithm_impl_distribution_ecdf",
            "fallbackReason": f"pandas import failed: {exc}",
        }

    reference_times = [row["time"] for row in values if row.get("period") == "reference"]
    current_times = [row["time"] for row in values if row.get("period") == "current"]
    if not reference_times or not current_times:
        return {
            "status": "not_applicable",
            "attempted": True,
            "algorithmImpl": "drift_algorithm_impl_distribution_ecdf",
            "fallbackReason": "reference/current periods are required",
        }

    feature_cols = [str(item) for item in params.get("feature_cols", params.get("embedding_cols", [])) or []]
    data_rows = []
    for row in values:
        data_row = {"time": row["time"], "value": row["value"]}
        for column in feature_cols:
            if column in row:
                data_row[column] = row[column]
        data_rows.append(data_row)
    data = pd.DataFrame(data_rows)
    algorithm_params = _algorithm_params(params, variant_id)
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
            "algorithmImpl": "drift_algorithm_impl_distribution_ecdf",
            "fallbackReason": f"{exc.__class__.__name__}: {exc}",
        }

    result_dict = _drift_result_to_dict(result)
    if result_dict.get("severity") == "not_applicable":
        return {
            "status": "not_applicable",
            "attempted": True,
            "algorithmImpl": "drift_algorithm_impl_distribution_ecdf",
            "fallbackReason": result_dict.get("interpretation") or "not_applicable",
            **result_dict,
        }
    if result_dict.get("severity") == "error":
        return {
            "status": "error",
            "attempted": True,
            "algorithmImpl": "drift_algorithm_impl_distribution_ecdf",
            "fallbackReason": result_dict.get("interpretation") or "algorithm_error",
            **result_dict,
        }
    return {
        "status": "success",
        "attempted": True,
        "algorithmImpl": "drift_algorithm_impl_distribution_ecdf",
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
            "algorithmImpl": "drift_algorithm_impl_distribution_ecdf",
            "fallbackReason": f"batchdistributioncomparison import failed: {exc}",
        }
    detector = getattr(methods, detector_name, None)
    if not callable(detector):
        return {
            "status": "import_error",
            "attempted": True,
            "algorithmImpl": "drift_algorithm_impl_distribution_ecdf",
            "fallbackReason": f"{detector_name} not found",
        }
    return {"status": "success", "detector": detector}


def _algorithm_params(params: dict[str, Any], variant_id: str) -> dict[str, Any]:
    excluded = {"useAlgorithmImpl", "fallbackOnNotApplicable"}
    algorithm_params = {key: value for key, value in params.items() if key not in excluded}
    algorithm_params["variant_id"] = variant_id
    algorithm_params.setdefault("value_col", "value")
    return algorithm_params


# @managed-contract contract_id=runtime_methods.generic_distribution_ecdf_window._convert_drift_result level=P0
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
        or measurements.get("KS_STATISTIC")
        or 0.0
    )
    level = "drift" if drift_detected is True else "normal"
    event = None
    if level == "drift":
        event = {
            "eventStart": bucket["window_start"],
            "eventEnd": bucket["window_end"],
            "eventLevel": "drift",
            "eventTitle": "Distribution ECDF drift detected",
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
            "implementation": "drift_algorithm_impl_distribution_ecdf",
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
