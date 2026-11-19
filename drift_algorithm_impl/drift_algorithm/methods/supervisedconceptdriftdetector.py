from __future__ import annotations

import math
from typing import Any

import numpy as np
import pandas as pd

from drift_algorithm.core.result import DriftResult, not_applicable_result


DDM_METHOD_ID = "DM-035"
DDM_METHOD_NAME = "DDM"
DDM_METHOD_CATEGORY = "SupervisedConceptDriftDetector"
RDDM_METHOD_ID = "DM-036"
RDDM_METHOD_NAME = "RDDM"
RDDM_METHOD_CATEGORY = "SupervisedConceptDriftDetector"
EDDM_METHOD_ID = "DM-037"
EDDM_METHOD_NAME = "EDDM"
EDDM_METHOD_CATEGORY = "SupervisedConceptDriftDetector"
ECDD_WT_METHOD_ID = "DM-038"
ECDD_WT_METHOD_NAME = "ECDD-WT"
ECDD_WT_METHOD_CATEGORY = "SupervisedConceptDriftDetector"
HDDM_A_METHOD_ID = "DM-039"
HDDM_A_METHOD_NAME = "HDDM-A"
HDDM_A_METHOD_CATEGORY = "SupervisedConceptDriftDetector"
HDDM_W_METHOD_ID = "DM-040"
HDDM_W_METHOD_NAME = "HDDM-W"
HDDM_W_METHOD_CATEGORY = "SupervisedConceptDriftDetector"
STEPD_METHOD_ID = "DM-041"
STEPD_METHOD_NAME = "STEPD"
STEPD_METHOD_CATEGORY = "SupervisedConceptDriftDetector"

SUPPORTED_DDM_VARIANTS = {"DDM_STANDARD", "DDM_WARNING_BUFFER", "DDM_CLASS_SPECIFIC"}
SUPPORTED_RDDM_VARIANTS = {"RDDM_STANDARD", "RDDM_REACTIVE_RESET"}
SUPPORTED_EDDM_VARIANTS = {"EDDM_DISTANCE_BETWEEN_ERRORS", "EDDM_WARNING_DRIFT", "EDDM_GRADUAL_DRIFT"}
SUPPORTED_ECDD_WT_VARIANTS = {"ECDD_WT_STANDARD", "ECDD_WT_WARNING_DRIFT", "ECDD_WT_ERROR_STREAM"}
SUPPORTED_HDDM_A_VARIANTS = {"HDDM_A_HOEFFDING_BOUND", "HDDM_A_WARNING_DRIFT", "HDDM_A_TWO_SIDED"}
SUPPORTED_HDDM_W_VARIANTS = {"HDDM_W_WEIGHTED_AVERAGE", "HDDM_W_WARNING_DRIFT", "HDDM_W_RECENT_ERROR_WEIGHTING"}
SUPPORTED_STEPD_VARIANTS = {"STEPD_ACCURACY_WINDOW", "STEPD_WARNING_DRIFT", "STEPD_SUPERVISED_STREAM"}


def detect_ddm(
    data: pd.DataFrame,
    *,
    time_col: str = "time",
    value_col: str | None = None,
    reference_window: tuple[str, str] | None = None,
    current_window: tuple[str, str] | None = None,
    params: dict[str, Any] | None = None,
) -> DriftResult:
    params = dict(params or {})
    variant_id = str(params.get("variant_id", "DDM_STANDARD")).upper()
    metadata: dict[str, Any] = {
        "params": params,
        "finite_replay_policy": "reference_and_current_error_stream_sorted_by_time",
    }

    if variant_id not in SUPPORTED_DDM_VARIANTS:
        return _ddm_not_applicable(variant_id, f"unsupported DDM variant: {variant_id}", metadata)
    if any(params.get(key) is not None for key in ("feature_cols", "embedding_cols", "category_col", "count_col")):
        return _ddm_not_applicable(
            variant_id,
            "categorical, count, multivariate, and embedding DDM inputs are not implemented",
            metadata,
        )

    try:
        resolved = _resolve_ddm_params(params, variant_id)
        prepared = _prepare_ddm_error_stream(
            data,
            time_col=time_col,
            value_col=value_col,
            reference_window=reference_window,
            current_window=current_window,
            params=params,
            variant_id=variant_id,
            class_label=resolved["class_label"],
            min_reference_size=resolved["min_reference_size"],
            min_current_size=resolved["min_current_size"],
        )
    except (KeyError, TypeError, ValueError) as exc:
        return _ddm_not_applicable(variant_id, str(exc), metadata)

    metadata.update(prepared["metadata"])
    metadata.update(
        {
            "backend": "numpy_ddm",
            "error_source": prepared["error_source"],
            "warning_level": resolved["warning_level"],
            "drift_level": resolved["drift_level"],
            "min_num_instances": resolved["min_num_instances"],
            "buffer_policy": resolved["buffer_policy"],
            "max_buffer_size": resolved["max_buffer_size"],
            "class_label": resolved["class_label"],
        }
    )
    warnings = list(prepared["warnings"])
    if params.get("threshold_or_alpha") is not None:
        warnings.append("threshold_or_alpha was interpreted as DDM drift_level")
    if resolved["warning_level"] >= resolved["drift_level"]:
        warnings.append("warning_level is not smaller than drift_level; warning state may be skipped")
    if variant_id == "DDM_CLASS_SPECIFIC":
        warnings.append("DDM_CLASS_SPECIFIC monitors only rows whose true label matches class_label")
    if params.get("multiple_testing_correction", "none") not in (None, "none"):
        warnings.append("multiple_testing_correction is recorded but not applied by detect_ddm")

    ref_n = len(prepared["reference_errors"])
    cur_n = len(prepared["current_errors"])
    imbalance_ratio = max(ref_n, cur_n) / min(ref_n, cur_n)
    if imbalance_ratio > resolved["sample_imbalance_warning_ratio"]:
        warnings.append(f"reference/current sample sizes are imbalanced (ratio={imbalance_ratio:.3g})")

    try:
        run = _run_ddm(
            prepared["stream_errors"],
            prepared["stream_times"],
            current_start_index=ref_n,
            warning_level=resolved["warning_level"],
            drift_level=resolved["drift_level"],
            min_num_instances=resolved["min_num_instances"],
            buffer_policy=resolved["buffer_policy"],
            max_buffer_size=resolved["max_buffer_size"],
            record_events=resolved["record_events"],
            max_event_records=resolved["max_event_records"],
        )
    except ValueError as exc:
        return DriftResult(
            method_id=DDM_METHOD_ID,
            method_name=DDM_METHOD_NAME,
            method_category=DDM_METHOD_CATEGORY,
            variant_id=variant_id,
            drift_detected=None,
            severity="error",
            warnings=warnings + [str(exc)],
            metadata=metadata,
            interpretation=f"DDM calculation failed: {exc}",
        )

    if run["event_history_truncated"]:
        warnings.append("DDM event history was truncated by max_event_records")

    drift_detected = run["drift_alarm_state"] == "drift_detected"
    severity = "drift_detected" if drift_detected else ("warning" if run["warning_state"] else "normal")
    measurements: dict[str, Any] = {
        "ERROR_RATE": run["error_rate"],
        "STANDARD_DEVIATION": run["standard_deviation"],
        "WARNING_STATE": run["warning_state"],
        "DRIFT_ALARM_STATE": run["drift_alarm_state"],
        "BUFFERED_INSTANCE_COUNT": run["buffered_instance_count"],
        "WARNING_START_TIME": run["warning_start_time"],
        "WARNING_START_INDEX": run["warning_start_index"],
        "DRIFT_TIME": run["drift_time"],
        "DRIFT_INDEX": run["drift_index"],
        "ERROR_RATE_MIN": run["error_rate_min"],
        "STANDARD_DEVIATION_MIN": run["standard_deviation_min"],
        "DDM_STATISTIC": run["ddm_statistic"],
        "WARNING_THRESHOLD": run["warning_threshold"],
        "DRIFT_THRESHOLD": run["drift_threshold"],
        "PROCESSED_COUNT": len(prepared["stream_errors"]),
        "SAMPLE_SIZE": {
            "reference": ref_n,
            "current": cur_n,
            "stream": len(prepared["stream_errors"]),
            "dropped_reference": prepared["metadata"]["reference_original_count"] - ref_n,
            "dropped_current": prepared["metadata"]["current_original_count"] - cur_n,
        },
        "SAMPLE_SIZE_REFERENCE": ref_n,
        "SAMPLE_SIZE_CURRENT": cur_n,
        "REFERENCE_ERROR_RATE": float(np.mean(prepared["reference_errors"])),
        "CURRENT_ERROR_RATE": float(np.mean(prepared["current_errors"])),
        "ERROR_RATE_DELTA": float(np.mean(prepared["current_errors"]) - np.mean(prepared["reference_errors"])),
    }
    if variant_id == "DDM_CLASS_SPECIFIC":
        measurements["CLASS_LABEL"] = resolved["class_label"]
        measurements["CLASS_ERROR_RATE"] = run["error_rate"]
        measurements["CLASS_DRIFT_STATE"] = run["drift_alarm_state"]
    if resolved["record_events"]:
        measurements["DDM_EVENTS"] = run["events"]
    if variant_id == "DDM_WARNING_BUFFER":
        measurements["WARNING_BUFFER"] = run["warning_buffer"]

    return DriftResult(
        method_id=DDM_METHOD_ID,
        method_name=DDM_METHOD_NAME,
        method_category=DDM_METHOD_CATEGORY,
        variant_id=variant_id,
        drift_detected=drift_detected,
        severity=severity,
        drift_score=run["ddm_statistic"],
        p_value=None,
        test_statistic=run["ddm_statistic"],
        threshold=run["drift_threshold"],
        measurements=measurements,
        interpretation=_ddm_interpretation(variant_id, ref_n, cur_n, resolved, run),
        warnings=warnings,
        metadata=metadata,
    )


def detect_rddm(
    data: pd.DataFrame,
    *,
    time_col: str = "time",
    value_col: str | None = None,
    reference_window: tuple[str, str] | None = None,
    current_window: tuple[str, str] | None = None,
    params: dict[str, Any] | None = None,
) -> DriftResult:
    params = dict(params or {})
    variant_id = str(params.get("variant_id", "RDDM_STANDARD")).upper()
    metadata: dict[str, Any] = {
        "params": params,
        "finite_replay_policy": "reference_and_current_error_stream_sorted_by_time",
    }

    if variant_id not in SUPPORTED_RDDM_VARIANTS:
        return _rddm_not_applicable(variant_id, f"unsupported RDDM variant: {variant_id}", metadata)
    if any(params.get(key) is not None for key in ("feature_cols", "embedding_cols", "category_col", "count_col")):
        return _rddm_not_applicable(
            variant_id,
            "categorical, count, multivariate, and embedding RDDM inputs are not implemented",
            metadata,
        )

    try:
        resolved = _resolve_rddm_params(params, variant_id)
        prepared = _prepare_ddm_error_stream(
            data,
            time_col=time_col,
            value_col=value_col,
            reference_window=reference_window,
            current_window=current_window,
            params=params,
            variant_id=variant_id,
            class_label=None,
            min_reference_size=resolved["min_reference_size"],
            min_current_size=resolved["min_current_size"],
        )
    except (KeyError, TypeError, ValueError) as exc:
        return _rddm_not_applicable(variant_id, str(exc), metadata)

    metadata.update(prepared["metadata"])
    metadata.update(
        {
            "backend": "numpy_rddm",
            "error_source": prepared["error_source"],
            "warning_level": resolved["warning_level"],
            "drift_level": resolved["drift_level"],
            "min_num_instances": resolved["min_num_instances"],
            "max_concept_size": resolved["max_concept_size"],
            "min_concept_size": resolved["min_concept_size"],
            "retention_policy": resolved["retention_policy"],
            "reset_policy": resolved["reset_policy"],
        }
    )
    warnings = list(prepared["warnings"])
    if params.get("threshold_or_alpha") is not None:
        warnings.append("threshold_or_alpha was interpreted as RDDM drift_level")
    if resolved["warning_level"] >= resolved["drift_level"]:
        warnings.append("warning_level is not smaller than drift_level; warning state may be skipped")
    if resolved["max_concept_size"] < len(prepared["stream_errors"]):
        warnings.append("max_concept_size may truncate retained long-running concept history")

    ref_n = len(prepared["reference_errors"])
    cur_n = len(prepared["current_errors"])
    imbalance_ratio = max(ref_n, cur_n) / min(ref_n, cur_n)
    if imbalance_ratio > resolved["sample_imbalance_warning_ratio"]:
        warnings.append(f"reference/current sample sizes are imbalanced (ratio={imbalance_ratio:.3g})")

    try:
        run = _run_rddm(
            prepared["stream_errors"],
            prepared["stream_times"],
            current_start_index=ref_n,
            warning_level=resolved["warning_level"],
            drift_level=resolved["drift_level"],
            min_num_instances=resolved["min_num_instances"],
            max_concept_size=resolved["max_concept_size"],
            min_concept_size=resolved["min_concept_size"],
            retention_policy=resolved["retention_policy"],
            reset_policy=resolved["reset_policy"],
            record_events=resolved["record_events"],
            max_event_records=resolved["max_event_records"],
        )
    except ValueError as exc:
        return DriftResult(
            method_id=RDDM_METHOD_ID,
            method_name=RDDM_METHOD_NAME,
            method_category=RDDM_METHOD_CATEGORY,
            variant_id=variant_id,
            drift_detected=None,
            severity="error",
            warnings=warnings + [str(exc)],
            metadata=metadata,
            interpretation=f"RDDM calculation failed: {exc}",
        )

    if run["event_history_truncated"]:
        warnings.append("RDDM event history was truncated by max_event_records")

    drift_detected = run["drift_alarm_state"] == "drift_detected"
    severity = "drift_detected" if drift_detected else ("warning" if run["warning_state"] else "normal")
    measurements: dict[str, Any] = {
        "WARNING_STATE": run["warning_state"],
        "DRIFT_ALARM_STATE": run["drift_alarm_state"],
        "WINDOW_SIZE": run["retained_window_size"],
        "RETAINED_WINDOW_SIZE": run["retained_window_size"],
        "ERROR_RATE": run["error_rate"],
        "STANDARD_DEVIATION": run["standard_deviation"],
        "RDDM_STATISTIC": run["rddm_statistic"],
        "WARNING_THRESHOLD": run["warning_threshold"],
        "DRIFT_THRESHOLD": run["drift_threshold"],
        "WARNING_START_TIME": run["warning_start_time"],
        "WARNING_START_INDEX": run["warning_start_index"],
        "DRIFT_TIME": run["drift_time"],
        "DRIFT_INDEX": run["drift_index"],
        "ADAPTATION_EVENT": run["adaptation_event"],
        "RESET_EVENT": run["reset_event"],
        "POST_RESET_ERROR_RATE": run["post_reset_error_rate"],
        "PROCESSED_COUNT": len(prepared["stream_errors"]),
        "SAMPLE_SIZE": {
            "reference": ref_n,
            "current": cur_n,
            "stream": len(prepared["stream_errors"]),
            "dropped_reference": prepared["metadata"]["reference_original_count"] - ref_n,
            "dropped_current": prepared["metadata"]["current_original_count"] - cur_n,
        },
        "SAMPLE_SIZE_REFERENCE": ref_n,
        "SAMPLE_SIZE_CURRENT": cur_n,
        "REFERENCE_ERROR_RATE": float(np.mean(prepared["reference_errors"])),
        "CURRENT_ERROR_RATE": float(np.mean(prepared["current_errors"])),
        "ERROR_RATE_DELTA": float(np.mean(prepared["current_errors"]) - np.mean(prepared["reference_errors"])),
    }
    if resolved["record_events"]:
        measurements["RDDM_EVENTS"] = run["events"]

    return DriftResult(
        method_id=RDDM_METHOD_ID,
        method_name=RDDM_METHOD_NAME,
        method_category=RDDM_METHOD_CATEGORY,
        variant_id=variant_id,
        drift_detected=drift_detected,
        severity=severity,
        drift_score=run["rddm_statistic"],
        p_value=None,
        test_statistic=run["rddm_statistic"],
        threshold=run["drift_threshold"],
        measurements=measurements,
        interpretation=_rddm_interpretation(variant_id, ref_n, cur_n, resolved, run),
        warnings=warnings,
        metadata=metadata,
    )


def detect_eddm(
    data: pd.DataFrame,
    *,
    time_col: str = "time",
    value_col: str | None = None,
    reference_window: tuple[str, str] | None = None,
    current_window: tuple[str, str] | None = None,
    params: dict[str, Any] | None = None,
) -> DriftResult:
    params = dict(params or {})
    variant_id = str(params.get("variant_id", "EDDM_DISTANCE_BETWEEN_ERRORS")).upper()
    metadata: dict[str, Any] = {
        "params": params,
        "finite_replay_policy": "reference_and_current_error_stream_sorted_by_time",
    }

    if variant_id not in SUPPORTED_EDDM_VARIANTS:
        return _eddm_not_applicable(variant_id, f"unsupported EDDM variant: {variant_id}", metadata)
    if any(params.get(key) is not None for key in ("feature_cols", "embedding_cols", "category_col", "count_col")):
        return _eddm_not_applicable(
            variant_id,
            "categorical, count, multivariate, and embedding EDDM inputs are not implemented",
            metadata,
        )

    try:
        resolved = _resolve_eddm_params(params, variant_id)
        prepared = _prepare_ddm_error_stream(
            data,
            time_col=time_col,
            value_col=value_col,
            reference_window=reference_window,
            current_window=current_window,
            params=params,
            variant_id=variant_id,
            class_label=None,
            min_reference_size=resolved["min_reference_size"],
            min_current_size=resolved["min_current_size"],
        )
    except (KeyError, TypeError, ValueError) as exc:
        return _eddm_not_applicable(variant_id, str(exc), metadata)

    metadata.update(prepared["metadata"])
    metadata.update(
        {
            "backend": "numpy_eddm",
            "error_source": prepared["error_source"],
            "warning_level": resolved["warning_level"],
            "drift_level": resolved["drift_level"],
            "min_num_errors": resolved["min_num_errors"],
            "error_distance_metric": resolved["error_distance_metric"],
        }
    )
    warnings = list(prepared["warnings"])
    if params.get("threshold_or_alpha") is not None:
        warnings.append("threshold_or_alpha was interpreted as EDDM drift_level ratio")
    if resolved["warning_level"] <= resolved["drift_level"]:
        warnings.append("warning_level is not greater than drift_level; warning state may be skipped")
    if variant_id == "EDDM_GRADUAL_DRIFT":
        warnings.append("EDDM_GRADUAL_DRIFT uses the same error-distance score with gradual-state metadata")

    ref_n = len(prepared["reference_errors"])
    cur_n = len(prepared["current_errors"])
    imbalance_ratio = max(ref_n, cur_n) / min(ref_n, cur_n)
    if imbalance_ratio > resolved["sample_imbalance_warning_ratio"]:
        warnings.append(f"reference/current sample sizes are imbalanced (ratio={imbalance_ratio:.3g})")

    try:
        run = _run_eddm(
            prepared["stream_errors"],
            prepared["stream_times"],
            current_start_index=ref_n,
            warning_level=resolved["warning_level"],
            drift_level=resolved["drift_level"],
            min_num_errors=resolved["min_num_errors"],
            record_events=resolved["record_events"],
            max_event_records=resolved["max_event_records"],
        )
    except ValueError as exc:
        return DriftResult(
            method_id=EDDM_METHOD_ID,
            method_name=EDDM_METHOD_NAME,
            method_category=EDDM_METHOD_CATEGORY,
            variant_id=variant_id,
            drift_detected=None,
            severity="error",
            warnings=warnings + [str(exc)],
            metadata=metadata,
            interpretation=f"EDDM calculation failed: {exc}",
        )

    if run["event_history_truncated"]:
        warnings.append("EDDM event history was truncated by max_event_records")

    drift_detected = run["drift_alarm_state"] == "drift_detected"
    severity = "drift_detected" if drift_detected else ("warning" if run["warning_state"] else "normal")
    measurements: dict[str, Any] = {
        "TEST_STATISTIC": run["eddm_statistic"],
        "EDDM_SCORE": run["eddm_score"],
        "EDDM_SCORE_RATIO": run["score_ratio"],
        "ERROR_DISTANCE_MEAN": run["distance_mean"],
        "ERROR_DISTANCE_STD": run["distance_std"],
        "ERROR_DISTANCE_MAX_SCORE": run["max_score"],
        "ERROR_COUNT": run["error_count"],
        "WARNING_STATE": run["warning_state"],
        "DRIFT_ALARM_STATE": run["drift_alarm_state"],
        "WARNING_THRESHOLD": run["warning_level"],
        "DRIFT_THRESHOLD": run["drift_level"],
        "WARNING_START_TIME": run["warning_start_time"],
        "WARNING_START_INDEX": run["warning_start_index"],
        "DRIFT_TIME": run["drift_time"],
        "DRIFT_INDEX": run["drift_index"],
        "GRADUAL_DRIFT_STATE": run["gradual_drift_state"] if variant_id == "EDDM_GRADUAL_DRIFT" else None,
        "P_VALUE": None,
        "PROCESSED_COUNT": len(prepared["stream_errors"]),
        "SAMPLE_SIZE": {
            "reference": ref_n,
            "current": cur_n,
            "stream": len(prepared["stream_errors"]),
            "dropped_reference": prepared["metadata"]["reference_original_count"] - ref_n,
            "dropped_current": prepared["metadata"]["current_original_count"] - cur_n,
        },
        "SAMPLE_SIZE_REFERENCE": ref_n,
        "SAMPLE_SIZE_CURRENT": cur_n,
        "REFERENCE_ERROR_RATE": float(np.mean(prepared["reference_errors"])),
        "CURRENT_ERROR_RATE": float(np.mean(prepared["current_errors"])),
        "ERROR_RATE_DELTA": float(np.mean(prepared["current_errors"]) - np.mean(prepared["reference_errors"])),
    }
    if resolved["record_events"]:
        measurements["EDDM_EVENTS"] = run["events"]

    return DriftResult(
        method_id=EDDM_METHOD_ID,
        method_name=EDDM_METHOD_NAME,
        method_category=EDDM_METHOD_CATEGORY,
        variant_id=variant_id,
        drift_detected=drift_detected,
        severity=severity,
        drift_score=run["score_ratio"],
        p_value=None,
        test_statistic=run["eddm_statistic"],
        threshold=run["drift_level"],
        measurements=measurements,
        interpretation=_eddm_interpretation(variant_id, ref_n, cur_n, resolved, run),
        warnings=warnings,
        metadata=metadata,
    )


def detect_ecdd_wt(
    data: pd.DataFrame,
    *,
    time_col: str = "time",
    value_col: str | None = None,
    reference_window: tuple[str, str] | None = None,
    current_window: tuple[str, str] | None = None,
    params: dict[str, Any] | None = None,
) -> DriftResult:
    params = dict(params or {})
    variant_id = str(params.get("variant_id", "ECDD_WT_STANDARD")).upper()
    metadata: dict[str, Any] = {
        "params": params,
        "finite_replay_policy": "reference_and_current_error_stream_sorted_by_time",
    }

    if variant_id not in SUPPORTED_ECDD_WT_VARIANTS:
        return _ecdd_wt_not_applicable(variant_id, f"unsupported ECDD-WT variant: {variant_id}", metadata)
    if any(params.get(key) is not None for key in ("feature_cols", "embedding_cols", "category_col", "count_col")):
        return _ecdd_wt_not_applicable(
            variant_id,
            "categorical, count, multivariate, and embedding ECDD-WT inputs are not implemented",
            metadata,
        )

    try:
        resolved = _resolve_ecdd_wt_params(params, variant_id)
        prepared = _prepare_ddm_error_stream(
            data,
            time_col=time_col,
            value_col=value_col,
            reference_window=reference_window,
            current_window=current_window,
            params=params,
            variant_id=variant_id,
            class_label=None,
            min_reference_size=resolved["min_reference_size"],
            min_current_size=resolved["min_current_size"],
        )
    except (KeyError, TypeError, ValueError) as exc:
        return _ecdd_wt_not_applicable(variant_id, str(exc), metadata)

    ref_n = len(prepared["reference_errors"])
    cur_n = len(prepared["current_errors"])
    baseline_error_rate = float(np.mean(prepared["reference_errors"]))
    metadata.update(prepared["metadata"])
    metadata.update(
        {
            "backend": "numpy_ecdd_wt",
            "error_source": prepared["error_source"],
            "lambda": resolved["lambda_value"],
            "warning_threshold": resolved["warning_threshold"],
            "drift_threshold": resolved["drift_threshold"],
            "min_instances": resolved["min_instances"],
            "error_definition": resolved["error_definition"],
            "baseline_error_rate": baseline_error_rate,
        }
    )
    warnings = list(prepared["warnings"])
    if params.get("threshold_or_alpha") is not None:
        warnings.append("threshold_or_alpha was interpreted as ECDD-WT drift_threshold")
    if resolved["warning_threshold"] >= resolved["drift_threshold"]:
        warnings.append("warning_threshold is not smaller than drift_threshold; warning state may be skipped")
    if baseline_error_rate <= 0.0 or baseline_error_rate >= 1.0:
        warnings.append("reference error rate was clipped for EWMA variance calculation")
    if variant_id == "ECDD_WT_ERROR_STREAM":
        warnings.append("ECDD_WT_ERROR_STREAM assumes the supplied error stream definition is operationally valid")

    imbalance_ratio = max(ref_n, cur_n) / min(ref_n, cur_n)
    if imbalance_ratio > resolved["sample_imbalance_warning_ratio"]:
        warnings.append(f"reference/current sample sizes are imbalanced (ratio={imbalance_ratio:.3g})")

    try:
        run = _run_ecdd_wt(
            prepared["stream_errors"],
            prepared["stream_times"],
            current_start_index=ref_n,
            lambda_value=resolved["lambda_value"],
            warning_threshold=resolved["warning_threshold"],
            drift_threshold=resolved["drift_threshold"],
            min_instances=resolved["min_instances"],
            baseline_error_rate=baseline_error_rate,
            variance_epsilon=resolved["variance_epsilon"],
            record_events=resolved["record_events"],
            max_event_records=resolved["max_event_records"],
        )
    except ValueError as exc:
        return DriftResult(
            method_id=ECDD_WT_METHOD_ID,
            method_name=ECDD_WT_METHOD_NAME,
            method_category=ECDD_WT_METHOD_CATEGORY,
            variant_id=variant_id,
            drift_detected=None,
            severity="error",
            warnings=warnings + [str(exc)],
            metadata=metadata,
            interpretation=f"ECDD-WT calculation failed: {exc}",
        )

    if run["event_history_truncated"]:
        warnings.append("ECDD-WT event history was truncated by max_event_records")

    drift_detected = run["drift_alarm_state"] == "drift_detected"
    severity = "drift_detected" if drift_detected else ("warning" if run["warning_state"] else "normal")
    measurements: dict[str, Any] = {
        "TEST_STATISTIC": run["ecdd_statistic"],
        "P_VALUE": None,
        "DRIFT_ALARM_STATE": run["drift_alarm_state"],
        "WARNING_STATE": run["warning_state"],
        "EWMA_ERROR_STATISTIC": run["ewma_error_statistic"],
        "ECDD_WT_STATISTIC": run["ecdd_statistic"],
        "BASELINE_ERROR_RATE": baseline_error_rate,
        "ERROR_RATE": run["final_error_rate"],
        "WARNING_THRESHOLD": run["warning_threshold"],
        "DRIFT_THRESHOLD": run["drift_threshold"],
        "LAMBDA": resolved["lambda_value"],
        "WARNING_START_TIME": run["warning_start_time"],
        "WARNING_START_INDEX": run["warning_start_index"],
        "DRIFT_TIME": run["drift_time"],
        "DRIFT_INDEX": run["drift_index"],
        "PROCESSED_COUNT": len(prepared["stream_errors"]),
        "SAMPLE_SIZE": {
            "reference": ref_n,
            "current": cur_n,
            "stream": len(prepared["stream_errors"]),
            "dropped_reference": prepared["metadata"]["reference_original_count"] - ref_n,
            "dropped_current": prepared["metadata"]["current_original_count"] - cur_n,
        },
        "SAMPLE_SIZE_REFERENCE": ref_n,
        "SAMPLE_SIZE_CURRENT": cur_n,
        "REFERENCE_ERROR_RATE": baseline_error_rate,
        "CURRENT_ERROR_RATE": float(np.mean(prepared["current_errors"])),
        "ERROR_RATE_DELTA": float(np.mean(prepared["current_errors"]) - baseline_error_rate),
    }
    if resolved["record_events"]:
        measurements["ECDD_WT_EVENTS"] = run["events"]

    return DriftResult(
        method_id=ECDD_WT_METHOD_ID,
        method_name=ECDD_WT_METHOD_NAME,
        method_category=ECDD_WT_METHOD_CATEGORY,
        variant_id=variant_id,
        drift_detected=drift_detected,
        severity=severity,
        drift_score=run["ecdd_statistic"],
        p_value=None,
        test_statistic=run["ecdd_statistic"],
        threshold=run["drift_threshold"],
        measurements=measurements,
        interpretation=_ecdd_wt_interpretation(variant_id, ref_n, cur_n, resolved, run, baseline_error_rate),
        warnings=warnings,
        metadata=metadata,
    )


def detect_hddm_a(
    data: pd.DataFrame,
    *,
    time_col: str = "time",
    value_col: str | None = None,
    reference_window: tuple[str, str] | None = None,
    current_window: tuple[str, str] | None = None,
    params: dict[str, Any] | None = None,
) -> DriftResult:
    params = dict(params or {})
    variant_id = str(params.get("variant_id", "HDDM_A_HOEFFDING_BOUND")).upper()
    metadata: dict[str, Any] = {
        "params": params,
        "finite_replay_policy": "reference_error_rate_vs_current_prefix_error_rate",
    }

    if variant_id not in SUPPORTED_HDDM_A_VARIANTS:
        return _hddm_a_not_applicable(variant_id, f"unsupported HDDM-A variant: {variant_id}", metadata)
    if any(params.get(key) is not None for key in ("feature_cols", "embedding_cols", "category_col", "count_col")):
        return _hddm_a_not_applicable(
            variant_id,
            "categorical, count, multivariate, and embedding HDDM-A inputs are not implemented",
            metadata,
        )

    try:
        resolved = _resolve_hddm_a_params(params, variant_id)
        prepared = _prepare_ddm_error_stream(
            data,
            time_col=time_col,
            value_col=value_col,
            reference_window=reference_window,
            current_window=current_window,
            params=params,
            variant_id=variant_id,
            class_label=None,
            min_reference_size=resolved["min_reference_size"],
            min_current_size=resolved["min_current_size"],
        )
    except (KeyError, TypeError, ValueError) as exc:
        return _hddm_a_not_applicable(variant_id, str(exc), metadata)

    ref_n = len(prepared["reference_errors"])
    cur_n = len(prepared["current_errors"])
    reference_mean = float(np.mean(prepared["reference_errors"]))
    metadata.update(prepared["metadata"])
    metadata.update(
        {
            "backend": "numpy_hddm_a",
            "error_source": prepared["error_source"],
            "drift_confidence": resolved["drift_confidence"],
            "warning_confidence": resolved["warning_confidence"],
            "two_sided": resolved["two_sided"],
            "min_instances": resolved["min_instances"],
            "reference_mean": reference_mean,
        }
    )
    warnings = list(prepared["warnings"])
    if params.get("threshold_or_alpha") is not None:
        warnings.append("threshold_or_alpha was interpreted as HDDM-A drift_confidence")
    if resolved["warning_confidence"] <= resolved["drift_confidence"]:
        warnings.append("warning_confidence is not greater than drift_confidence; warning state may be skipped")
    if variant_id == "HDDM_A_TWO_SIDED":
        warnings.append("HDDM_A_TWO_SIDED monitors both increasing and decreasing mean shifts")

    imbalance_ratio = max(ref_n, cur_n) / min(ref_n, cur_n)
    if imbalance_ratio > resolved["sample_imbalance_warning_ratio"]:
        warnings.append(f"reference/current sample sizes are imbalanced (ratio={imbalance_ratio:.3g})")

    try:
        run = _run_hddm_a(
            prepared["current_errors"],
            prepared["stream_times"][ref_n:],
            reference_mean=reference_mean,
            reference_n=ref_n,
            drift_confidence=resolved["drift_confidence"],
            warning_confidence=resolved["warning_confidence"],
            two_sided=resolved["two_sided"],
            min_instances=resolved["min_instances"],
            record_events=resolved["record_events"],
            max_event_records=resolved["max_event_records"],
        )
    except ValueError as exc:
        return DriftResult(
            method_id=HDDM_A_METHOD_ID,
            method_name=HDDM_A_METHOD_NAME,
            method_category=HDDM_A_METHOD_CATEGORY,
            variant_id=variant_id,
            drift_detected=None,
            severity="error",
            warnings=warnings + [str(exc)],
            metadata=metadata,
            interpretation=f"HDDM-A calculation failed: {exc}",
        )

    if run["event_history_truncated"]:
        warnings.append("HDDM-A event history was truncated by max_event_records")

    drift_detected = run["drift_alarm_state"] == "drift_detected"
    severity = "drift_detected" if drift_detected else ("warning" if run["warning_state"] else "normal")
    measurements: dict[str, Any] = {
        "TEST_STATISTIC": run["test_statistic"],
        "P_VALUE": None,
        "DRIFT_ALARM_STATE": run["drift_alarm_state"],
        "WARNING_STATE": run["warning_state"],
        "MEAN_DIFFERENCE": run["mean_difference"],
        "REFERENCE_MEAN": reference_mean,
        "CURRENT_PREFIX_MEAN": run["current_prefix_mean"],
        "HOEFFDING_WARNING_BOUND": run["warning_bound"],
        "HOEFFDING_DRIFT_BOUND": run["drift_bound"],
        "CHANGE_DIRECTION": run["change_direction"],
        "WARNING_START_TIME": run["warning_start_time"],
        "WARNING_START_INDEX": run["warning_start_index"],
        "DRIFT_TIME": run["drift_time"],
        "DRIFT_INDEX": run["drift_index"],
        "PROCESSED_COUNT": len(prepared["stream_errors"]),
        "SAMPLE_SIZE": {
            "reference": ref_n,
            "current": cur_n,
            "stream": len(prepared["stream_errors"]),
            "dropped_reference": prepared["metadata"]["reference_original_count"] - ref_n,
            "dropped_current": prepared["metadata"]["current_original_count"] - cur_n,
        },
        "SAMPLE_SIZE_REFERENCE": ref_n,
        "SAMPLE_SIZE_CURRENT": cur_n,
        "REFERENCE_ERROR_RATE": reference_mean,
        "CURRENT_ERROR_RATE": float(np.mean(prepared["current_errors"])),
        "ERROR_RATE_DELTA": float(np.mean(prepared["current_errors"]) - reference_mean),
    }
    if resolved["record_events"]:
        measurements["HDDM_A_EVENTS"] = run["events"]

    return DriftResult(
        method_id=HDDM_A_METHOD_ID,
        method_name=HDDM_A_METHOD_NAME,
        method_category=HDDM_A_METHOD_CATEGORY,
        variant_id=variant_id,
        drift_detected=drift_detected,
        severity=severity,
        drift_score=run["test_statistic"],
        p_value=None,
        test_statistic=run["test_statistic"],
        threshold=run["drift_bound"],
        measurements=measurements,
        interpretation=_hddm_a_interpretation(variant_id, ref_n, cur_n, resolved, run, reference_mean),
        warnings=warnings,
        metadata=metadata,
    )


def detect_hddm_w(
    data: pd.DataFrame,
    *,
    time_col: str = "time",
    value_col: str | None = None,
    reference_window: tuple[str, str] | None = None,
    current_window: tuple[str, str] | None = None,
    params: dict[str, Any] | None = None,
) -> DriftResult:
    params = dict(params or {})
    variant_id = str(params.get("variant_id", "HDDM_W_WEIGHTED_AVERAGE")).upper()
    metadata: dict[str, Any] = {
        "params": params,
        "finite_replay_policy": "reference_error_rate_vs_current_weighted_error_rate",
    }

    if variant_id not in SUPPORTED_HDDM_W_VARIANTS:
        return _hddm_w_not_applicable(variant_id, f"unsupported HDDM-W variant: {variant_id}", metadata)
    if any(params.get(key) is not None for key in ("feature_cols", "embedding_cols", "category_col", "count_col")):
        return _hddm_w_not_applicable(
            variant_id,
            "categorical, count, multivariate, and embedding HDDM-W inputs are not implemented",
            metadata,
        )

    try:
        resolved = _resolve_hddm_w_params(params, variant_id)
        prepared = _prepare_ddm_error_stream(
            data,
            time_col=time_col,
            value_col=value_col,
            reference_window=reference_window,
            current_window=current_window,
            params=params,
            variant_id=variant_id,
            class_label=None,
            min_reference_size=resolved["min_reference_size"],
            min_current_size=resolved["min_current_size"],
        )
    except (KeyError, TypeError, ValueError) as exc:
        return _hddm_w_not_applicable(variant_id, str(exc), metadata)

    ref_n = len(prepared["reference_errors"])
    cur_n = len(prepared["current_errors"])
    reference_mean = float(np.mean(prepared["reference_errors"]))
    metadata.update(prepared["metadata"])
    metadata.update(
        {
            "backend": "numpy_hddm_w",
            "error_source": prepared["error_source"],
            "drift_confidence": resolved["drift_confidence"],
            "warning_confidence": resolved["warning_confidence"],
            "lambda": resolved["lambda_value"],
            "two_sided": resolved["two_sided"],
            "min_instances": resolved["min_instances"],
            "reference_mean": reference_mean,
        }
    )
    warnings = list(prepared["warnings"])
    if params.get("threshold_or_alpha") is not None:
        warnings.append("threshold_or_alpha was interpreted as HDDM-W drift_confidence")
    if resolved["warning_confidence"] <= resolved["drift_confidence"]:
        warnings.append("warning_confidence is not greater than drift_confidence; warning state may be skipped")
    if resolved["two_sided"]:
        warnings.append("HDDM-W two_sided mode monitors both increasing and decreasing weighted mean shifts")
    if variant_id == "HDDM_W_RECENT_ERROR_WEIGHTING":
        warnings.append("HDDM_W_RECENT_ERROR_WEIGHTING emphasizes the most recent labeled errors")

    imbalance_ratio = max(ref_n, cur_n) / min(ref_n, cur_n)
    if imbalance_ratio > resolved["sample_imbalance_warning_ratio"]:
        warnings.append(f"reference/current sample sizes are imbalanced (ratio={imbalance_ratio:.3g})")

    try:
        run = _run_hddm_w(
            prepared["current_errors"],
            prepared["stream_times"][ref_n:],
            reference_mean=reference_mean,
            reference_n=ref_n,
            drift_confidence=resolved["drift_confidence"],
            warning_confidence=resolved["warning_confidence"],
            lambda_value=resolved["lambda_value"],
            two_sided=resolved["two_sided"],
            min_instances=resolved["min_instances"],
            record_events=resolved["record_events"],
            max_event_records=resolved["max_event_records"],
        )
    except ValueError as exc:
        return DriftResult(
            method_id=HDDM_W_METHOD_ID,
            method_name=HDDM_W_METHOD_NAME,
            method_category=HDDM_W_METHOD_CATEGORY,
            variant_id=variant_id,
            drift_detected=None,
            severity="error",
            warnings=warnings + [str(exc)],
            metadata=metadata,
            interpretation=f"HDDM-W calculation failed: {exc}",
        )

    if run["event_history_truncated"]:
        warnings.append("HDDM-W event history was truncated by max_event_records")

    drift_detected = run["drift_alarm_state"] == "drift_detected"
    severity = "drift_detected" if drift_detected else ("warning" if run["warning_state"] else "normal")
    measurements: dict[str, Any] = {
        "TEST_STATISTIC": run["test_statistic"],
        "P_VALUE": None,
        "DRIFT_ALARM_STATE": run["drift_alarm_state"],
        "WARNING_STATE": run["warning_state"],
        "WEIGHTED_MEAN_DIFFERENCE": run["weighted_mean_difference"],
        "REFERENCE_MEAN": reference_mean,
        "WEIGHTED_CURRENT_MEAN": run["weighted_current_mean"],
        "EFFECTIVE_CURRENT_SAMPLE_SIZE": run["effective_current_sample_size"],
        "HOEFFDING_WARNING_BOUND": run["warning_bound"],
        "HOEFFDING_DRIFT_BOUND": run["drift_bound"],
        "CHANGE_DIRECTION": run["change_direction"],
        "LAMBDA": resolved["lambda_value"],
        "WARNING_START_TIME": run["warning_start_time"],
        "WARNING_START_INDEX": run["warning_start_index"],
        "DRIFT_TIME": run["drift_time"],
        "DRIFT_INDEX": run["drift_index"],
        "PROCESSED_COUNT": len(prepared["stream_errors"]),
        "SAMPLE_SIZE": {
            "reference": ref_n,
            "current": cur_n,
            "stream": len(prepared["stream_errors"]),
            "dropped_reference": prepared["metadata"]["reference_original_count"] - ref_n,
            "dropped_current": prepared["metadata"]["current_original_count"] - cur_n,
        },
        "SAMPLE_SIZE_REFERENCE": ref_n,
        "SAMPLE_SIZE_CURRENT": cur_n,
        "REFERENCE_ERROR_RATE": reference_mean,
        "CURRENT_ERROR_RATE": float(np.mean(prepared["current_errors"])),
        "ERROR_RATE_DELTA": float(np.mean(prepared["current_errors"]) - reference_mean),
    }
    if resolved["record_events"]:
        measurements["HDDM_W_EVENTS"] = run["events"]

    return DriftResult(
        method_id=HDDM_W_METHOD_ID,
        method_name=HDDM_W_METHOD_NAME,
        method_category=HDDM_W_METHOD_CATEGORY,
        variant_id=variant_id,
        drift_detected=drift_detected,
        severity=severity,
        drift_score=run["test_statistic"],
        p_value=None,
        test_statistic=run["test_statistic"],
        threshold=run["drift_bound"],
        measurements=measurements,
        interpretation=_hddm_w_interpretation(variant_id, ref_n, cur_n, resolved, run, reference_mean),
        warnings=warnings,
        metadata=metadata,
    )


def detect_stepd(
    data: pd.DataFrame,
    *,
    time_col: str = "time",
    value_col: str | None = None,
    reference_window: tuple[str, str] | None = None,
    current_window: tuple[str, str] | None = None,
    params: dict[str, Any] | None = None,
) -> DriftResult:
    params = dict(params or {})
    variant_id = str(params.get("variant_id", "STEPD_ACCURACY_WINDOW")).upper()
    metadata: dict[str, Any] = {
        "params": params,
        "finite_replay_policy": "reference_accuracy_vs_current_rolling_accuracy",
    }

    if variant_id not in SUPPORTED_STEPD_VARIANTS:
        return _stepd_not_applicable(variant_id, f"unsupported STEPD variant: {variant_id}", metadata)
    if any(params.get(key) is not None for key in ("feature_cols", "embedding_cols", "category_col", "count_col")):
        return _stepd_not_applicable(
            variant_id,
            "categorical, count, multivariate, and embedding STEPD inputs are not implemented",
            metadata,
        )

    try:
        resolved = _resolve_stepd_params(params, variant_id)
        prepared = _prepare_ddm_error_stream(
            data,
            time_col=time_col,
            value_col=value_col,
            reference_window=reference_window,
            current_window=current_window,
            params=params,
            variant_id=variant_id,
            class_label=None,
            min_reference_size=resolved["min_reference_size"],
            min_current_size=resolved["min_current_size"],
        )
    except (KeyError, TypeError, ValueError) as exc:
        return _stepd_not_applicable(variant_id, str(exc), metadata)

    ref_n = len(prepared["reference_errors"])
    cur_n = len(prepared["current_errors"])
    reference_accuracy = float(1.0 - np.mean(prepared["reference_errors"]))
    metadata.update(prepared["metadata"])
    metadata.update(
        {
            "backend": "numpy_stepd",
            "error_source": prepared["error_source"],
            "alpha_drift": resolved["alpha_drift"],
            "alpha_warning": resolved["alpha_warning"],
            "window_size": resolved["window_size"],
            "min_instances": resolved["min_instances"],
            "accuracy_definition": resolved["accuracy_definition"],
            "step_size": resolved["step_size"],
            "reference_accuracy": reference_accuracy,
        }
    )
    warnings = list(prepared["warnings"])
    if params.get("threshold_or_alpha") is not None:
        warnings.append("threshold_or_alpha was interpreted as STEPD alpha_drift")
    if resolved["alpha_warning"] <= resolved["alpha_drift"]:
        warnings.append("alpha_warning is not greater than alpha_drift; warning state may be skipped")
    if variant_id == "STEPD_SUPERVISED_STREAM":
        warnings.append("STEPD_SUPERVISED_STREAM assumes label arrival order is represented by time_col")

    imbalance_ratio = max(ref_n, cur_n) / min(ref_n, cur_n)
    if imbalance_ratio > resolved["sample_imbalance_warning_ratio"]:
        warnings.append(f"reference/current sample sizes are imbalanced (ratio={imbalance_ratio:.3g})")

    try:
        run = _run_stepd(
            prepared["current_errors"],
            prepared["stream_times"][ref_n:],
            reference_accuracy=reference_accuracy,
            reference_n=ref_n,
            alpha_drift=resolved["alpha_drift"],
            alpha_warning=resolved["alpha_warning"],
            window_size=resolved["window_size"],
            min_instances=resolved["min_instances"],
            step_size=resolved["step_size"],
            record_events=resolved["record_events"],
            max_event_records=resolved["max_event_records"],
        )
    except ValueError as exc:
        return DriftResult(
            method_id=STEPD_METHOD_ID,
            method_name=STEPD_METHOD_NAME,
            method_category=STEPD_METHOD_CATEGORY,
            variant_id=variant_id,
            drift_detected=None,
            severity="error",
            warnings=warnings + [str(exc)],
            metadata=metadata,
            interpretation=f"STEPD calculation failed: {exc}",
        )

    if run["event_history_truncated"]:
        warnings.append("STEPD event history was truncated by max_event_records")

    drift_detected = run["drift_alarm_state"] == "drift_detected"
    severity = "drift_detected" if drift_detected else ("warning" if run["warning_state"] else "normal")
    measurements: dict[str, Any] = {
        "TEST_STATISTIC": run["test_statistic"],
        "P_VALUE": run["p_value"],
        "DRIFT_ALARM_STATE": run["drift_alarm_state"],
        "WARNING_STATE": run["warning_state"],
        "REFERENCE_ACCURACY": reference_accuracy,
        "CURRENT_WINDOW_ACCURACY": run["current_window_accuracy"],
        "ACCURACY_DELTA": run["accuracy_delta"],
        "WINDOW_SIZE": run["window_size"],
        "ALPHA_WARNING": resolved["alpha_warning"],
        "ALPHA_DRIFT": resolved["alpha_drift"],
        "WARNING_START_TIME": run["warning_start_time"],
        "WARNING_START_INDEX": run["warning_start_index"],
        "DRIFT_TIME": run["drift_time"],
        "DRIFT_INDEX": run["drift_index"],
        "PROCESSED_COUNT": len(prepared["stream_errors"]),
        "SAMPLE_SIZE": {
            "reference": ref_n,
            "current": cur_n,
            "stream": len(prepared["stream_errors"]),
            "dropped_reference": prepared["metadata"]["reference_original_count"] - ref_n,
            "dropped_current": prepared["metadata"]["current_original_count"] - cur_n,
        },
        "SAMPLE_SIZE_REFERENCE": ref_n,
        "SAMPLE_SIZE_CURRENT": cur_n,
        "REFERENCE_ERROR_RATE": float(np.mean(prepared["reference_errors"])),
        "CURRENT_ERROR_RATE": float(np.mean(prepared["current_errors"])),
        "ERROR_RATE_DELTA": float(np.mean(prepared["current_errors"]) - np.mean(prepared["reference_errors"])),
    }
    if resolved["record_events"]:
        measurements["STEPD_EVENTS"] = run["events"]

    return DriftResult(
        method_id=STEPD_METHOD_ID,
        method_name=STEPD_METHOD_NAME,
        method_category=STEPD_METHOD_CATEGORY,
        variant_id=variant_id,
        drift_detected=drift_detected,
        severity=severity,
        drift_score=run["test_statistic"],
        p_value=run["p_value"],
        test_statistic=run["test_statistic"],
        threshold=resolved["alpha_drift"],
        measurements=measurements,
        interpretation=_stepd_interpretation(variant_id, ref_n, cur_n, resolved, run, reference_accuracy),
        warnings=warnings,
        metadata=metadata,
    )


def _resolve_ddm_params(params: dict[str, Any], variant_id: str) -> dict[str, Any]:
    warning_level = _as_float(params.get("warning_level", 2.0), "warning_level")
    drift_level_source = params.get("drift_level", params.get("threshold_or_alpha", 3.0))
    drift_level = _as_float(drift_level_source, "drift_level")
    if warning_level <= 0.0 or drift_level <= 0.0:
        raise ValueError("warning_level and drift_level must be positive")
    buffer_policy = str(params.get("buffer_policy", "warning_period")).lower()
    if buffer_policy not in {"warning_period", "none"}:
        raise ValueError("buffer_policy must be 'warning_period' or 'none'")
    class_label = params.get("class_label")
    if variant_id == "DDM_CLASS_SPECIFIC" and class_label is None:
        raise ValueError("DDM_CLASS_SPECIFIC requires params['class_label']")
    resolved = {
        "warning_level": warning_level,
        "drift_level": drift_level,
        "min_num_instances": _as_positive_int(params.get("min_num_instances", 30), "min_num_instances"),
        "min_reference_size": _as_positive_int(params.get("min_reference_size", 20), "min_reference_size"),
        "min_current_size": _as_positive_int(params.get("min_current_size", 20), "min_current_size"),
        "buffer_policy": buffer_policy,
        "max_buffer_size": _as_positive_int(params.get("max_buffer_size", 1000), "max_buffer_size"),
        "record_events": _as_bool(params.get("record_events", True), "record_events"),
        "max_event_records": _as_positive_int(params.get("max_event_records", 50), "max_event_records"),
        "class_label": class_label,
        "sample_imbalance_warning_ratio": _as_float(
            params.get("sample_imbalance_warning_ratio", 10.0),
            "sample_imbalance_warning_ratio",
        ),
    }
    if resolved["sample_imbalance_warning_ratio"] < 1.0:
        raise ValueError("sample_imbalance_warning_ratio must be >= 1")
    return resolved


def _resolve_rddm_params(params: dict[str, Any], variant_id: str) -> dict[str, Any]:
    warning_level = _as_float(params.get("warning_level", 2.0), "warning_level")
    drift_level_source = params.get("drift_level", params.get("threshold_or_alpha", 3.0))
    drift_level = _as_float(drift_level_source, "drift_level")
    if warning_level <= 0.0 or drift_level <= 0.0:
        raise ValueError("warning_level and drift_level must be positive")
    retention_policy = str(params.get("retention_policy", "warning_period")).lower()
    if retention_policy not in {"warning_period", "recent_window"}:
        raise ValueError("retention_policy must be 'warning_period' or 'recent_window'")
    reset_policy = str(
        params.get("reset_policy", "reactive" if variant_id == "RDDM_REACTIVE_RESET" else "none")
    ).lower()
    if reset_policy not in {"none", "reactive"}:
        raise ValueError("reset_policy must be 'none' or 'reactive'")
    if variant_id == "RDDM_STANDARD" and reset_policy != "none":
        raise ValueError("RDDM_STANDARD first implementation requires reset_policy='none'")
    if variant_id == "RDDM_REACTIVE_RESET" and reset_policy != "reactive":
        raise ValueError("RDDM_REACTIVE_RESET requires reset_policy='reactive'")

    min_concept_size = _as_positive_int(params.get("min_concept_size", 30), "min_concept_size")
    max_concept_size = _as_positive_int(params.get("max_concept_size", 1000), "max_concept_size")
    if min_concept_size > max_concept_size:
        raise ValueError("min_concept_size must be <= max_concept_size")
    resolved = {
        "warning_level": warning_level,
        "drift_level": drift_level,
        "min_num_instances": _as_positive_int(params.get("min_num_instances", 30), "min_num_instances"),
        "min_reference_size": _as_positive_int(params.get("min_reference_size", 20), "min_reference_size"),
        "min_current_size": _as_positive_int(params.get("min_current_size", 20), "min_current_size"),
        "max_concept_size": max_concept_size,
        "min_concept_size": min_concept_size,
        "retention_policy": retention_policy,
        "reset_policy": reset_policy,
        "record_events": _as_bool(params.get("record_events", True), "record_events"),
        "max_event_records": _as_positive_int(params.get("max_event_records", 50), "max_event_records"),
        "sample_imbalance_warning_ratio": _as_float(
            params.get("sample_imbalance_warning_ratio", 10.0),
            "sample_imbalance_warning_ratio",
        ),
    }
    if resolved["sample_imbalance_warning_ratio"] < 1.0:
        raise ValueError("sample_imbalance_warning_ratio must be >= 1")
    return resolved


def _resolve_eddm_params(params: dict[str, Any], variant_id: str) -> dict[str, Any]:
    warning_level = _as_float(params.get("warning_level", 0.95), "warning_level")
    drift_level_source = params.get("drift_level", params.get("threshold_or_alpha", 0.90))
    drift_level = _as_float(drift_level_source, "drift_level")
    if warning_level <= 0.0 or drift_level <= 0.0:
        raise ValueError("warning_level and drift_level must be positive")
    if warning_level > 1.0 or drift_level > 1.0:
        raise ValueError("EDDM warning_level and drift_level are score ratios and must be <= 1")
    error_distance_metric = str(params.get("error_distance_metric", "index_gap")).lower()
    if error_distance_metric not in {"index_gap"}:
        raise ValueError("error_distance_metric must be 'index_gap'")
    resolved = {
        "warning_level": warning_level,
        "drift_level": drift_level,
        "min_num_errors": _as_positive_int(params.get("min_num_errors", 30), "min_num_errors"),
        "min_reference_size": _as_positive_int(params.get("min_reference_size", 20), "min_reference_size"),
        "min_current_size": _as_positive_int(params.get("min_current_size", 20), "min_current_size"),
        "error_distance_metric": error_distance_metric,
        "record_events": _as_bool(params.get("record_events", True), "record_events"),
        "max_event_records": _as_positive_int(params.get("max_event_records", 50), "max_event_records"),
        "sample_imbalance_warning_ratio": _as_float(
            params.get("sample_imbalance_warning_ratio", 10.0),
            "sample_imbalance_warning_ratio",
        ),
    }
    if resolved["sample_imbalance_warning_ratio"] < 1.0:
        raise ValueError("sample_imbalance_warning_ratio must be >= 1")
    return resolved


def _resolve_ecdd_wt_params(params: dict[str, Any], variant_id: str) -> dict[str, Any]:
    lambda_value = _as_float(params.get("lambda", params.get("lambda_value", 0.2)), "lambda")
    if lambda_value <= 0.0 or lambda_value > 1.0:
        raise ValueError("lambda must be in (0, 1]")
    warning_threshold = _as_float(params.get("warning_threshold", 2.0), "warning_threshold")
    drift_threshold_source = params.get("drift_threshold", params.get("threshold_or_alpha", 3.0))
    drift_threshold = _as_float(drift_threshold_source, "drift_threshold")
    if warning_threshold <= 0.0 or drift_threshold <= 0.0:
        raise ValueError("warning_threshold and drift_threshold must be positive")
    error_definition = str(params.get("error_definition", "binary_misclassification")).lower()
    if error_definition not in {"binary_misclassification", "precomputed_binary_error"}:
        raise ValueError("error_definition must be 'binary_misclassification' or 'precomputed_binary_error'")
    resolved = {
        "lambda_value": lambda_value,
        "warning_threshold": warning_threshold,
        "drift_threshold": drift_threshold,
        "min_instances": _as_positive_int(params.get("min_instances", 30), "min_instances"),
        "min_reference_size": _as_positive_int(params.get("min_reference_size", 20), "min_reference_size"),
        "min_current_size": _as_positive_int(params.get("min_current_size", 20), "min_current_size"),
        "error_definition": error_definition,
        "variance_epsilon": _as_float(params.get("variance_epsilon", 1e-6), "variance_epsilon"),
        "record_events": _as_bool(params.get("record_events", True), "record_events"),
        "max_event_records": _as_positive_int(params.get("max_event_records", 50), "max_event_records"),
        "sample_imbalance_warning_ratio": _as_float(
            params.get("sample_imbalance_warning_ratio", 10.0),
            "sample_imbalance_warning_ratio",
        ),
    }
    if resolved["variance_epsilon"] <= 0.0:
        raise ValueError("variance_epsilon must be positive")
    if resolved["sample_imbalance_warning_ratio"] < 1.0:
        raise ValueError("sample_imbalance_warning_ratio must be >= 1")
    return resolved


def _resolve_hddm_a_params(params: dict[str, Any], variant_id: str) -> dict[str, Any]:
    drift_confidence_source = params.get("drift_confidence", params.get("threshold_or_alpha", 0.001))
    drift_confidence = _as_float(drift_confidence_source, "drift_confidence")
    warning_confidence = _as_float(params.get("warning_confidence", 0.005), "warning_confidence")
    if not 0.0 < drift_confidence < 1.0:
        raise ValueError("drift_confidence must be in (0, 1)")
    if not 0.0 < warning_confidence < 1.0:
        raise ValueError("warning_confidence must be in (0, 1)")
    two_sided = _as_bool(params.get("two_sided", variant_id == "HDDM_A_TWO_SIDED"), "two_sided")
    if variant_id == "HDDM_A_TWO_SIDED" and not two_sided:
        raise ValueError("HDDM_A_TWO_SIDED requires two_sided=True")
    if variant_id != "HDDM_A_TWO_SIDED" and two_sided:
        raise ValueError("two_sided=True is only supported by HDDM_A_TWO_SIDED")
    resolved = {
        "drift_confidence": drift_confidence,
        "warning_confidence": warning_confidence,
        "two_sided": two_sided,
        "min_instances": _as_positive_int(params.get("min_instances", 30), "min_instances"),
        "min_reference_size": _as_positive_int(params.get("min_reference_size", 20), "min_reference_size"),
        "min_current_size": _as_positive_int(params.get("min_current_size", 20), "min_current_size"),
        "record_events": _as_bool(params.get("record_events", True), "record_events"),
        "max_event_records": _as_positive_int(params.get("max_event_records", 50), "max_event_records"),
        "sample_imbalance_warning_ratio": _as_float(
            params.get("sample_imbalance_warning_ratio", 10.0),
            "sample_imbalance_warning_ratio",
        ),
    }
    if resolved["sample_imbalance_warning_ratio"] < 1.0:
        raise ValueError("sample_imbalance_warning_ratio must be >= 1")
    return resolved


def _resolve_hddm_w_params(params: dict[str, Any], variant_id: str) -> dict[str, Any]:
    drift_confidence_source = params.get("drift_confidence", params.get("threshold_or_alpha", 0.001))
    drift_confidence = _as_float(drift_confidence_source, "drift_confidence")
    warning_confidence = _as_float(params.get("warning_confidence", 0.005), "warning_confidence")
    if not 0.0 < drift_confidence < 1.0:
        raise ValueError("drift_confidence must be in (0, 1)")
    if not 0.0 < warning_confidence < 1.0:
        raise ValueError("warning_confidence must be in (0, 1)")
    lambda_default = 0.3 if variant_id == "HDDM_W_RECENT_ERROR_WEIGHTING" else 0.2
    lambda_value = _as_float(params.get("lambda", params.get("lambda_value", lambda_default)), "lambda")
    if lambda_value <= 0.0 or lambda_value > 1.0:
        raise ValueError("lambda must be in (0, 1]")
    resolved = {
        "drift_confidence": drift_confidence,
        "warning_confidence": warning_confidence,
        "lambda_value": lambda_value,
        "two_sided": _as_bool(params.get("two_sided", False), "two_sided"),
        "min_instances": _as_positive_int(params.get("min_instances", 30), "min_instances"),
        "min_reference_size": _as_positive_int(params.get("min_reference_size", 20), "min_reference_size"),
        "min_current_size": _as_positive_int(params.get("min_current_size", 20), "min_current_size"),
        "record_events": _as_bool(params.get("record_events", True), "record_events"),
        "max_event_records": _as_positive_int(params.get("max_event_records", 50), "max_event_records"),
        "sample_imbalance_warning_ratio": _as_float(
            params.get("sample_imbalance_warning_ratio", 10.0),
            "sample_imbalance_warning_ratio",
        ),
    }
    if resolved["sample_imbalance_warning_ratio"] < 1.0:
        raise ValueError("sample_imbalance_warning_ratio must be >= 1")
    return resolved


def _resolve_stepd_params(params: dict[str, Any], variant_id: str) -> dict[str, Any]:
    alpha_drift_source = params.get("alpha_drift", params.get("threshold_or_alpha", 0.01))
    alpha_drift = _as_float(alpha_drift_source, "alpha_drift")
    alpha_warning = _as_float(params.get("alpha_warning", 0.05), "alpha_warning")
    if not 0.0 < alpha_drift < 1.0:
        raise ValueError("alpha_drift must be in (0, 1)")
    if not 0.0 < alpha_warning < 1.0:
        raise ValueError("alpha_warning must be in (0, 1)")
    accuracy_definition = str(params.get("accuracy_definition", "1_minus_binary_error")).lower()
    if accuracy_definition not in {"1_minus_binary_error", "y_true_equals_y_pred"}:
        raise ValueError("accuracy_definition must be '1_minus_binary_error' or 'y_true_equals_y_pred'")
    window_size = _as_positive_int(params.get("window_size", 30), "window_size")
    min_instances = _as_positive_int(params.get("min_instances", window_size), "min_instances")
    step_size = _as_positive_int(params.get("step_size", 1), "step_size")
    resolved = {
        "alpha_drift": alpha_drift,
        "alpha_warning": alpha_warning,
        "window_size": window_size,
        "min_instances": min_instances,
        "step_size": step_size,
        "accuracy_definition": accuracy_definition,
        "min_reference_size": _as_positive_int(params.get("min_reference_size", 20), "min_reference_size"),
        "min_current_size": _as_positive_int(params.get("min_current_size", 20), "min_current_size"),
        "record_events": _as_bool(params.get("record_events", True), "record_events"),
        "max_event_records": _as_positive_int(params.get("max_event_records", 50), "max_event_records"),
        "sample_imbalance_warning_ratio": _as_float(
            params.get("sample_imbalance_warning_ratio", 10.0),
            "sample_imbalance_warning_ratio",
        ),
    }
    if resolved["min_instances"] < resolved["window_size"]:
        raise ValueError("min_instances must be >= window_size")
    if resolved["sample_imbalance_warning_ratio"] < 1.0:
        raise ValueError("sample_imbalance_warning_ratio must be >= 1")
    return resolved


def _prepare_ddm_error_stream(
    data: pd.DataFrame,
    *,
    time_col: str,
    value_col: str | None,
    reference_window: tuple[str, str] | None,
    current_window: tuple[str, str] | None,
    params: dict[str, Any],
    variant_id: str,
    class_label: Any,
    min_reference_size: int,
    min_current_size: int,
) -> dict[str, Any]:
    if reference_window is None or current_window is None:
        raise ValueError("reference_window and current_window are required")
    if time_col not in data.columns:
        raise KeyError(f"missing time column: {time_col}")
    ref_start, ref_end = _parse_window(reference_window, "reference_window")
    cur_start, cur_end = _parse_window(current_window, "current_window")
    if max(ref_start, cur_start) <= min(ref_end, cur_end):
        raise ValueError("reference_window and current_window must not overlap")

    frame = data.copy()
    original_rows = len(frame)
    frame[time_col] = pd.to_datetime(frame[time_col], errors="coerce")
    invalid_time_rows = int(frame[time_col].isna().sum())

    error_col = params.get("error_col", value_col or params.get("input_signal"))
    y_true_col = params.get("y_true", params.get("y_true_col"))
    y_pred_col = params.get("y_pred", params.get("y_pred_col"))
    if error_col and error_col in frame.columns:
        errors = pd.to_numeric(frame[error_col], errors="coerce")
        error_source = str(error_col)
    elif y_true_col and y_pred_col:
        if y_true_col not in frame.columns:
            raise KeyError(f"missing y_true column: {y_true_col}")
        if y_pred_col not in frame.columns:
            raise KeyError(f"missing y_pred column: {y_pred_col}")
        errors = (frame[y_true_col] != frame[y_pred_col]).astype(float)
        error_source = f"{y_true_col}!={y_pred_col}"
    else:
        raise ValueError("DDM requires error_col/input_signal or y_true/y_pred columns")

    frame["_ddm_error"] = errors
    if variant_id == "DDM_CLASS_SPECIFIC":
        y_true_for_class = y_true_col or params.get("class_col")
        if y_true_for_class is None or y_true_for_class not in frame.columns:
            raise ValueError("DDM_CLASS_SPECIFIC requires y_true/y_true_col or class_col")
        frame = frame[frame[y_true_for_class] == class_label]
        if frame.empty:
            raise ValueError(f"DDM_CLASS_SPECIFIC has no rows for class_label={class_label!r}")

    raw_reference_mask = (frame[time_col] >= ref_start) & (frame[time_col] <= ref_end)
    raw_current_mask = (frame[time_col] >= cur_start) & (frame[time_col] <= cur_end)
    reference_original_count = int(raw_reference_mask.sum())
    current_original_count = int(raw_current_mask.sum())
    invalid_error_rows = int(frame["_ddm_error"].isna().sum())
    frame = frame.dropna(subset=[time_col, "_ddm_error"])
    frame = frame[np.isfinite(frame["_ddm_error"].to_numpy(dtype=float))]
    if not frame["_ddm_error"].isin([0, 1, 0.0, 1.0, False, True]).all():
        raise ValueError("DDM error stream must contain binary 0/1 values")
    frame = frame.sort_values(time_col)

    reference_frame = frame[(frame[time_col] >= ref_start) & (frame[time_col] <= ref_end)]
    current_frame = frame[(frame[time_col] >= cur_start) & (frame[time_col] <= cur_end)]
    if len(reference_frame) < min_reference_size:
        raise ValueError(
            f"reference sample size {len(reference_frame)} is below min_reference_size {min_reference_size}"
        )
    if len(current_frame) < min_current_size:
        raise ValueError(f"current sample size {len(current_frame)} is below min_current_size {min_current_size}")

    stream_frame = pd.concat([reference_frame, current_frame], axis=0).sort_values(time_col)
    warnings: list[str] = []
    if invalid_time_rows:
        warnings.append(f"dropped {invalid_time_rows} rows with invalid timestamps")
    if invalid_error_rows:
        warnings.append(f"dropped {invalid_error_rows} rows with non-finite error values")
    return {
        "reference_errors": reference_frame["_ddm_error"].to_numpy(dtype=float),
        "current_errors": current_frame["_ddm_error"].to_numpy(dtype=float),
        "stream_errors": stream_frame["_ddm_error"].to_numpy(dtype=float),
        "stream_times": stream_frame[time_col].to_numpy(dtype="datetime64[ns]"),
        "error_source": error_source,
        "warnings": warnings,
        "metadata": {
            "original_rows": original_rows,
            "valid_rows": int(len(frame)),
            "invalid_time_rows": invalid_time_rows,
            "invalid_error_rows": invalid_error_rows,
            "reference_original_count": reference_original_count,
            "current_original_count": current_original_count,
        },
    }


def _run_ddm(
    errors: np.ndarray,
    times: np.ndarray,
    *,
    current_start_index: int,
    warning_level: float,
    drift_level: float,
    min_num_instances: int,
    buffer_policy: str,
    max_buffer_size: int,
    record_events: bool,
    max_event_records: int,
) -> dict[str, Any]:
    error_count = 0.0
    p_min = np.inf
    s_min = np.inf
    warning_state = False
    warning_start_time = None
    warning_start_index = None
    drift_time = None
    drift_index = None
    drift_alarm_state = "normal"
    events: list[dict[str, Any]] = []
    warning_buffer: list[dict[str, Any]] = []
    event_history_truncated = False
    final_p = 0.0
    final_s = 0.0
    final_statistic = 0.0
    warning_threshold = None
    drift_threshold = None

    for index, error in enumerate(errors):
        error_count += float(error)
        n = index + 1
        final_p = error_count / n
        final_s = float(np.sqrt(final_p * (1.0 - final_p) / n))
        final_statistic = final_p + final_s
        if n < min_num_instances:
            continue
        if final_statistic < p_min + s_min:
            p_min = final_p
            s_min = final_s
        warning_threshold = p_min + warning_level * s_min
        drift_threshold = p_min + drift_level * s_min
        state = "normal"
        if final_statistic >= drift_threshold:
            state = "drift_detected"
        elif final_statistic >= warning_threshold:
            state = "warning"

        if index >= current_start_index and state in {"warning", "drift_detected"} and not warning_state:
            warning_state = True
            warning_start_time = _iso_time(times[index])
            warning_start_index = index
        if warning_state and buffer_policy == "warning_period" and index >= current_start_index:
            if len(warning_buffer) < max_buffer_size:
                warning_buffer.append({"time": _iso_time(times[index]), "index": int(index), "error": float(error)})

        if index >= current_start_index and state == "drift_detected":
            drift_alarm_state = "drift_detected"
            drift_time = _iso_time(times[index])
            drift_index = index
            if record_events:
                if len(events) < max_event_records:
                    events.append(
                        {
                            "time": drift_time,
                            "index": int(index),
                            "error_rate": final_p,
                            "standard_deviation": final_s,
                            "ddm_statistic": final_statistic,
                            "drift_threshold": drift_threshold,
                        }
                    )
                else:
                    event_history_truncated = True
            break
        if state == "normal" and index >= current_start_index:
            warning_state = False
            warning_buffer = []

    if not np.isfinite(p_min) or not np.isfinite(s_min):
        raise ValueError("DDM did not reach min_num_instances")
    return {
        "error_rate": float(final_p),
        "standard_deviation": float(final_s),
        "warning_state": bool(warning_state and drift_alarm_state != "drift_detected"),
        "drift_alarm_state": drift_alarm_state,
        "buffered_instance_count": len(warning_buffer),
        "warning_buffer": warning_buffer,
        "warning_start_time": warning_start_time,
        "warning_start_index": warning_start_index,
        "drift_time": drift_time,
        "drift_index": drift_index,
        "error_rate_min": float(p_min),
        "standard_deviation_min": float(s_min),
        "ddm_statistic": float(final_statistic),
        "warning_threshold": None if warning_threshold is None else float(warning_threshold),
        "drift_threshold": None if drift_threshold is None else float(drift_threshold),
        "events": events,
        "event_history_truncated": event_history_truncated,
    }


def _run_rddm(
    errors: np.ndarray,
    times: np.ndarray,
    *,
    current_start_index: int,
    warning_level: float,
    drift_level: float,
    min_num_instances: int,
    max_concept_size: int,
    min_concept_size: int,
    retention_policy: str,
    reset_policy: str,
    record_events: bool,
    max_event_records: int,
) -> dict[str, Any]:
    error_count = 0.0
    p_min = np.inf
    s_min = np.inf
    warning_state = False
    warning_start_time = None
    warning_start_index = None
    drift_time = None
    drift_index = None
    drift_alarm_state = "normal"
    events: list[dict[str, Any]] = []
    event_history_truncated = False
    retained_start_index = 0
    final_p = 0.0
    final_s = 0.0
    final_statistic = 0.0
    warning_threshold = None
    drift_threshold = None

    for index, error in enumerate(errors):
        error_count += float(error)
        n = index + 1
        if n > max_concept_size:
            window_start = n - max_concept_size
            concept_errors = errors[window_start : index + 1]
            effective_n = len(concept_errors)
            effective_error_count = float(np.sum(concept_errors))
        else:
            window_start = 0
            effective_n = n
            effective_error_count = error_count
        final_p = effective_error_count / effective_n
        final_s = float(np.sqrt(final_p * (1.0 - final_p) / effective_n))
        final_statistic = final_p + final_s
        if n < min_num_instances or effective_n < min_concept_size:
            continue
        if final_statistic < p_min + s_min:
            p_min = final_p
            s_min = final_s
        warning_threshold = p_min + warning_level * s_min
        drift_threshold = p_min + drift_level * s_min
        state = "normal"
        if final_statistic >= drift_threshold:
            state = "drift_detected"
        elif final_statistic >= warning_threshold:
            state = "warning"

        if index >= current_start_index and state in {"warning", "drift_detected"} and not warning_state:
            warning_state = True
            warning_start_time = _iso_time(times[index])
            warning_start_index = index
            retained_start_index = index if retention_policy == "warning_period" else max(window_start, index + 1 - max_concept_size)

        if index >= current_start_index and state == "drift_detected":
            drift_alarm_state = "drift_detected"
            drift_time = _iso_time(times[index])
            drift_index = index
            if record_events:
                if len(events) < max_event_records:
                    events.append(
                        {
                            "time": drift_time,
                            "index": int(index),
                            "error_rate": final_p,
                            "standard_deviation": final_s,
                            "rddm_statistic": final_statistic,
                            "drift_threshold": drift_threshold,
                            "retained_window_size": int(index - retained_start_index + 1),
                        }
                    )
                else:
                    event_history_truncated = True
            break
        if state == "normal" and index >= current_start_index:
            warning_state = False
            warning_start_time = None
            warning_start_index = None
            retained_start_index = max(window_start, index + 1 - min_concept_size)

    if not np.isfinite(p_min) or not np.isfinite(s_min):
        raise ValueError("RDDM did not reach min_num_instances/min_concept_size")

    retained_window_size = max(0, (drift_index if drift_index is not None else len(errors) - 1) - retained_start_index + 1)
    reset_event = None
    post_reset_error_rate = None
    adaptation_event = None
    if drift_alarm_state == "drift_detected" and reset_policy == "reactive":
        reset_event = {
            "time": drift_time,
            "index": int(drift_index),
            "policy": "reactive",
            "retained_window_size_before_reset": int(retained_window_size),
        }
        adaptation_event = "reactive_reset"
        post_reset_values = errors[drift_index + 1 :]
        if len(post_reset_values):
            post_reset_error_rate = float(np.mean(post_reset_values))
        else:
            post_reset_error_rate = float(final_p)
    elif drift_alarm_state == "drift_detected":
        adaptation_event = "drift_alarm_no_reset"

    return {
        "error_rate": float(final_p),
        "standard_deviation": float(final_s),
        "warning_state": bool(warning_state and drift_alarm_state != "drift_detected"),
        "drift_alarm_state": drift_alarm_state,
        "retained_window_size": int(retained_window_size),
        "warning_start_time": warning_start_time,
        "warning_start_index": warning_start_index,
        "drift_time": drift_time,
        "drift_index": drift_index,
        "rddm_statistic": float(final_statistic),
        "warning_threshold": None if warning_threshold is None else float(warning_threshold),
        "drift_threshold": None if drift_threshold is None else float(drift_threshold),
        "adaptation_event": adaptation_event,
        "reset_event": reset_event,
        "post_reset_error_rate": post_reset_error_rate,
        "events": events,
        "event_history_truncated": event_history_truncated,
    }


def _run_eddm(
    errors: np.ndarray,
    times: np.ndarray,
    *,
    current_start_index: int,
    warning_level: float,
    drift_level: float,
    min_num_errors: int,
    record_events: bool,
    max_event_records: int,
) -> dict[str, Any]:
    error_positions: list[int] = []
    distances: list[int] = []
    max_score = 0.0
    warning_state = False
    warning_start_time = None
    warning_start_index = None
    drift_time = None
    drift_index = None
    drift_alarm_state = "normal"
    events: list[dict[str, Any]] = []
    event_history_truncated = False
    final_score = 0.0
    final_ratio = 1.0
    final_mean = 0.0
    final_std = 0.0

    for index, error in enumerate(errors):
        if float(error) != 1.0:
            continue
        if error_positions:
            distances.append(index - error_positions[-1])
        error_positions.append(index)
        error_count = len(error_positions)
        if error_count < min_num_errors or not distances:
            continue

        distance_array = np.asarray(distances, dtype=float)
        final_mean = float(np.mean(distance_array))
        final_std = float(np.std(distance_array, ddof=0))
        final_score = final_mean + 2.0 * final_std
        if final_score > max_score:
            max_score = final_score
        if max_score <= 0.0:
            continue
        final_ratio = final_score / max_score

        state = "normal"
        if final_ratio < drift_level:
            state = "drift_detected"
        elif final_ratio < warning_level:
            state = "warning"

        if index >= current_start_index and state in {"warning", "drift_detected"} and not warning_state:
            warning_state = True
            warning_start_time = _iso_time(times[index])
            warning_start_index = index

        if index >= current_start_index and state == "drift_detected":
            drift_alarm_state = "drift_detected"
            drift_time = _iso_time(times[index])
            drift_index = index
            if record_events:
                if len(events) < max_event_records:
                    events.append(
                        {
                            "time": drift_time,
                            "index": int(index),
                            "error_count": int(error_count),
                            "distance_mean": final_mean,
                            "distance_std": final_std,
                            "eddm_score": final_score,
                            "score_ratio": final_ratio,
                            "drift_level": drift_level,
                        }
                    )
                else:
                    event_history_truncated = True
            break
        if state == "normal" and index >= current_start_index:
            warning_state = False
            warning_start_time = None
            warning_start_index = None

    if len(error_positions) < min_num_errors:
        raise ValueError(f"EDDM requires at least min_num_errors={min_num_errors} observed errors")
    eddm_statistic = 1.0 - final_ratio
    gradual_drift_state = "gradual_drift_candidate" if warning_state or drift_alarm_state == "drift_detected" else "normal"
    return {
        "distance_mean": float(final_mean),
        "distance_std": float(final_std),
        "eddm_score": float(final_score),
        "max_score": float(max_score),
        "score_ratio": float(final_ratio),
        "eddm_statistic": float(eddm_statistic),
        "error_count": int(len(error_positions)),
        "warning_state": bool(warning_state and drift_alarm_state != "drift_detected"),
        "drift_alarm_state": drift_alarm_state,
        "warning_level": float(warning_level),
        "drift_level": float(drift_level),
        "warning_start_time": warning_start_time,
        "warning_start_index": warning_start_index,
        "drift_time": drift_time,
        "drift_index": drift_index,
        "gradual_drift_state": gradual_drift_state,
        "events": events,
        "event_history_truncated": event_history_truncated,
    }


def _run_ecdd_wt(
    errors: np.ndarray,
    times: np.ndarray,
    *,
    current_start_index: int,
    lambda_value: float,
    warning_threshold: float,
    drift_threshold: float,
    min_instances: int,
    baseline_error_rate: float,
    variance_epsilon: float,
    record_events: bool,
    max_event_records: int,
) -> dict[str, Any]:
    if len(errors) < min_instances:
        raise ValueError("ECDD-WT did not reach min_instances")
    p0 = float(np.clip(baseline_error_rate, variance_epsilon, 1.0 - variance_epsilon))
    ewma = p0
    error_count = 0.0
    warning_state = False
    warning_start_time = None
    warning_start_index = None
    drift_time = None
    drift_index = None
    drift_alarm_state = "normal"
    events: list[dict[str, Any]] = []
    event_history_truncated = False
    final_statistic = 0.0

    for index, error in enumerate(errors):
        error_value = float(error)
        error_count += error_value
        ewma = lambda_value * error_value + (1.0 - lambda_value) * ewma
        n = index + 1
        variance_multiplier = lambda_value * (1.0 - (1.0 - lambda_value) ** (2 * n)) / (2.0 - lambda_value)
        sigma = float(np.sqrt(max(p0 * (1.0 - p0) * variance_multiplier, variance_epsilon)))
        final_statistic = (ewma - p0) / sigma
        if n < min_instances:
            continue

        state = "normal"
        if final_statistic >= drift_threshold:
            state = "drift_detected"
        elif final_statistic >= warning_threshold:
            state = "warning"

        if index >= current_start_index and state in {"warning", "drift_detected"} and not warning_state:
            warning_state = True
            warning_start_time = _iso_time(times[index])
            warning_start_index = index

        if index >= current_start_index and state == "drift_detected":
            drift_alarm_state = "drift_detected"
            drift_time = _iso_time(times[index])
            drift_index = index
            if record_events:
                if len(events) < max_event_records:
                    events.append(
                        {
                            "time": drift_time,
                            "index": int(index),
                            "ewma_error_statistic": float(ewma),
                            "ecdd_statistic": float(final_statistic),
                            "baseline_error_rate": p0,
                            "drift_threshold": drift_threshold,
                        }
                    )
                else:
                    event_history_truncated = True
            break
        if state == "normal" and index >= current_start_index:
            warning_state = False
            warning_start_time = None
            warning_start_index = None

    return {
        "ewma_error_statistic": float(ewma),
        "ecdd_statistic": float(final_statistic),
        "final_error_rate": float(error_count / len(errors)),
        "warning_state": bool(warning_state and drift_alarm_state != "drift_detected"),
        "drift_alarm_state": drift_alarm_state,
        "warning_threshold": float(warning_threshold),
        "drift_threshold": float(drift_threshold),
        "warning_start_time": warning_start_time,
        "warning_start_index": warning_start_index,
        "drift_time": drift_time,
        "drift_index": drift_index,
        "events": events,
        "event_history_truncated": event_history_truncated,
    }


def _run_hddm_a(
    current_errors: np.ndarray,
    current_times: np.ndarray,
    *,
    reference_mean: float,
    reference_n: int,
    drift_confidence: float,
    warning_confidence: float,
    two_sided: bool,
    min_instances: int,
    record_events: bool,
    max_event_records: int,
) -> dict[str, Any]:
    if len(current_errors) < min_instances:
        raise ValueError("HDDM-A did not reach min_instances")
    warning_state = False
    warning_start_time = None
    warning_start_index = None
    drift_time = None
    drift_index = None
    drift_alarm_state = "normal"
    events: list[dict[str, Any]] = []
    event_history_truncated = False
    final_difference = 0.0
    final_test_statistic = 0.0
    final_prefix_mean = 0.0
    final_warning_bound = None
    final_drift_bound = None
    final_direction = "none"
    current_sum = 0.0

    for index, error in enumerate(current_errors):
        current_sum += float(error)
        current_n = index + 1
        final_prefix_mean = current_sum / current_n
        final_difference = final_prefix_mean - reference_mean
        effective_difference = abs(final_difference) if two_sided else final_difference
        final_test_statistic = effective_difference
        final_direction = "increase" if final_difference > 0 else ("decrease" if final_difference < 0 else "none")
        if current_n < min_instances:
            continue

        sides = 2.0 if two_sided else 1.0
        warning_delta = warning_confidence / sides
        drift_delta = drift_confidence / sides
        final_warning_bound = _hddm_a_bound(reference_n, current_n, warning_delta)
        final_drift_bound = _hddm_a_bound(reference_n, current_n, drift_delta)
        state = "normal"
        if effective_difference >= final_drift_bound:
            state = "drift_detected"
        elif effective_difference >= final_warning_bound:
            state = "warning"

        if state in {"warning", "drift_detected"} and not warning_state:
            warning_state = True
            warning_start_time = _iso_time(current_times[index])
            warning_start_index = index
        if state == "drift_detected":
            drift_alarm_state = "drift_detected"
            drift_time = _iso_time(current_times[index])
            drift_index = index
            if record_events:
                if len(events) < max_event_records:
                    events.append(
                        {
                            "time": drift_time,
                            "index": int(index),
                            "mean_difference": final_difference,
                            "test_statistic": final_test_statistic,
                            "drift_bound": final_drift_bound,
                            "change_direction": final_direction,
                        }
                    )
                else:
                    event_history_truncated = True
            break
        if state == "normal":
            warning_state = False
            warning_start_time = None
            warning_start_index = None

    if final_warning_bound is None or final_drift_bound is None:
        raise ValueError("HDDM-A did not compute Hoeffding bounds")
    return {
        "current_prefix_mean": float(final_prefix_mean),
        "mean_difference": float(final_difference),
        "test_statistic": float(final_test_statistic),
        "warning_bound": float(final_warning_bound),
        "drift_bound": float(final_drift_bound),
        "change_direction": final_direction,
        "warning_state": bool(warning_state and drift_alarm_state != "drift_detected"),
        "drift_alarm_state": drift_alarm_state,
        "warning_start_time": warning_start_time,
        "warning_start_index": warning_start_index,
        "drift_time": drift_time,
        "drift_index": drift_index,
        "events": events,
        "event_history_truncated": event_history_truncated,
    }


def _run_hddm_w(
    current_errors: np.ndarray,
    current_times: np.ndarray,
    *,
    reference_mean: float,
    reference_n: int,
    drift_confidence: float,
    warning_confidence: float,
    lambda_value: float,
    two_sided: bool,
    min_instances: int,
    record_events: bool,
    max_event_records: int,
) -> dict[str, Any]:
    if len(current_errors) < min_instances:
        raise ValueError("HDDM-W did not reach min_instances")
    weighted_mean = reference_mean
    warning_state = False
    warning_start_time = None
    warning_start_index = None
    drift_time = None
    drift_index = None
    drift_alarm_state = "normal"
    events: list[dict[str, Any]] = []
    event_history_truncated = False
    final_difference = 0.0
    final_test_statistic = 0.0
    final_warning_bound = None
    final_drift_bound = None
    final_direction = "none"
    final_effective_n = 0.0

    for index, error in enumerate(current_errors):
        weighted_mean = lambda_value * float(error) + (1.0 - lambda_value) * weighted_mean
        current_n = index + 1
        final_difference = weighted_mean - reference_mean
        effective_difference = abs(final_difference) if two_sided else final_difference
        final_test_statistic = effective_difference
        final_direction = "increase" if final_difference > 0 else ("decrease" if final_difference < 0 else "none")
        if current_n < min_instances:
            continue

        weight_sum = 1.0 - (1.0 - lambda_value) ** current_n
        weight_sq_sum = lambda_value * (1.0 - (1.0 - lambda_value) ** (2 * current_n)) / (2.0 - lambda_value)
        final_effective_n = max((weight_sum * weight_sum) / weight_sq_sum, 1.0)
        sides = 2.0 if two_sided else 1.0
        warning_delta = warning_confidence / sides
        drift_delta = drift_confidence / sides
        final_warning_bound = _hddm_a_bound(reference_n, final_effective_n, warning_delta)
        final_drift_bound = _hddm_a_bound(reference_n, final_effective_n, drift_delta)
        state = "normal"
        if effective_difference >= final_drift_bound:
            state = "drift_detected"
        elif effective_difference >= final_warning_bound:
            state = "warning"

        if state in {"warning", "drift_detected"} and not warning_state:
            warning_state = True
            warning_start_time = _iso_time(current_times[index])
            warning_start_index = index
        if state == "drift_detected":
            drift_alarm_state = "drift_detected"
            drift_time = _iso_time(current_times[index])
            drift_index = index
            if record_events:
                if len(events) < max_event_records:
                    events.append(
                        {
                            "time": drift_time,
                            "index": int(index),
                            "weighted_mean_difference": final_difference,
                            "test_statistic": final_test_statistic,
                            "drift_bound": final_drift_bound,
                            "effective_current_sample_size": final_effective_n,
                            "change_direction": final_direction,
                        }
                    )
                else:
                    event_history_truncated = True
            break
        if state == "normal":
            warning_state = False
            warning_start_time = None
            warning_start_index = None

    if final_warning_bound is None or final_drift_bound is None:
        raise ValueError("HDDM-W did not compute weighted Hoeffding bounds")
    return {
        "weighted_current_mean": float(weighted_mean),
        "weighted_mean_difference": float(final_difference),
        "test_statistic": float(final_test_statistic),
        "effective_current_sample_size": float(final_effective_n),
        "warning_bound": float(final_warning_bound),
        "drift_bound": float(final_drift_bound),
        "change_direction": final_direction,
        "warning_state": bool(warning_state and drift_alarm_state != "drift_detected"),
        "drift_alarm_state": drift_alarm_state,
        "warning_start_time": warning_start_time,
        "warning_start_index": warning_start_index,
        "drift_time": drift_time,
        "drift_index": drift_index,
        "events": events,
        "event_history_truncated": event_history_truncated,
    }


def _run_stepd(
    current_errors: np.ndarray,
    current_times: np.ndarray,
    *,
    reference_accuracy: float,
    reference_n: int,
    alpha_drift: float,
    alpha_warning: float,
    window_size: int,
    min_instances: int,
    step_size: int,
    record_events: bool,
    max_event_records: int,
) -> dict[str, Any]:
    if len(current_errors) < min_instances:
        raise ValueError("STEPD did not reach min_instances")
    accuracies = 1.0 - current_errors.astype(float)
    warning_state = False
    warning_start_time = None
    warning_start_index = None
    drift_time = None
    drift_index = None
    drift_alarm_state = "normal"
    events: list[dict[str, Any]] = []
    event_history_truncated = False
    final_z = 0.0
    final_p_value = 1.0
    final_window_accuracy = 0.0
    final_delta = 0.0

    for end_index in range(window_size - 1, len(accuracies), step_size):
        processed = end_index + 1
        if processed < min_instances:
            continue
        window = accuracies[end_index - window_size + 1 : end_index + 1]
        final_window_accuracy = float(np.mean(window))
        final_delta = final_window_accuracy - reference_accuracy
        pooled_accuracy = (
            reference_accuracy * reference_n + final_window_accuracy * window_size
        ) / (reference_n + window_size)
        se = math.sqrt(max(pooled_accuracy * (1.0 - pooled_accuracy) * (1.0 / reference_n + 1.0 / window_size), 1e-12))
        final_z = (reference_accuracy - final_window_accuracy) / se
        final_p_value = _normal_upper_tail(final_z)

        state = "normal"
        if final_p_value <= alpha_drift and final_delta < 0.0:
            state = "drift_detected"
        elif final_p_value <= alpha_warning and final_delta < 0.0:
            state = "warning"

        if state in {"warning", "drift_detected"} and not warning_state:
            warning_state = True
            warning_start_time = _iso_time(current_times[end_index])
            warning_start_index = end_index
        if state == "drift_detected":
            drift_alarm_state = "drift_detected"
            drift_time = _iso_time(current_times[end_index])
            drift_index = end_index
            if record_events:
                if len(events) < max_event_records:
                    events.append(
                        {
                            "time": drift_time,
                            "index": int(end_index),
                            "reference_accuracy": reference_accuracy,
                            "current_window_accuracy": final_window_accuracy,
                            "accuracy_delta": final_delta,
                            "z_statistic": final_z,
                            "p_value": final_p_value,
                        }
                    )
                else:
                    event_history_truncated = True
            break
        if state == "normal":
            warning_state = False
            warning_start_time = None
            warning_start_index = None

    return {
        "current_window_accuracy": float(final_window_accuracy),
        "accuracy_delta": float(final_delta),
        "test_statistic": float(final_z),
        "p_value": float(final_p_value),
        "window_size": int(window_size),
        "warning_state": bool(warning_state and drift_alarm_state != "drift_detected"),
        "drift_alarm_state": drift_alarm_state,
        "warning_start_time": warning_start_time,
        "warning_start_index": warning_start_index,
        "drift_time": drift_time,
        "drift_index": drift_index,
        "events": events,
        "event_history_truncated": event_history_truncated,
    }


def _normal_upper_tail(z_value: float) -> float:
    return float(0.5 * math.erfc(z_value / math.sqrt(2.0)))


def _hddm_a_bound(reference_n: int, current_n: int, confidence: float) -> float:
    return float(
        np.sqrt(np.log(1.0 / confidence) / (2.0 * reference_n))
        + np.sqrt(np.log(1.0 / confidence) / (2.0 * current_n))
    )


def _ddm_interpretation(
    variant_id: str,
    reference_n: int,
    current_n: int,
    resolved: dict[str, Any],
    run: dict[str, Any],
) -> str:
    base = (
        f"{variant_id} replayed labeled/error rows as a finite chronological stream "
        f"(reference_n={reference_n}, current_n={current_n}). "
        f"warning_level={resolved['warning_level']}, drift_level={resolved['drift_level']}, "
        f"min_num_instances={resolved['min_num_instances']}. "
        f"Final error_rate={run['error_rate']:.6g}, std={run['standard_deviation']:.6g}, "
        f"DDM statistic={run['ddm_statistic']:.6g}."
    )
    if run["drift_alarm_state"] == "drift_detected":
        return (
            f"{base} DDM reached drift state at {run['drift_time']}. "
            "This is a supervised error-rate drift candidate, not proof of root cause."
        )
    if run["warning_state"]:
        return (
            f"{base} DDM is in warning state from {run['warning_start_time']}. "
            "This is an investigation signal, not a drift alarm."
        )
    return f"{base} No DDM warning or drift state remained active under this finite replay policy."


def _rddm_interpretation(
    variant_id: str,
    reference_n: int,
    current_n: int,
    resolved: dict[str, Any],
    run: dict[str, Any],
) -> str:
    base = (
        f"{variant_id} replayed labeled/error rows as a finite chronological stream "
        f"(reference_n={reference_n}, current_n={current_n}). "
        f"warning_level={resolved['warning_level']}, drift_level={resolved['drift_level']}, "
        f"min_num_instances={resolved['min_num_instances']}, max_concept_size={resolved['max_concept_size']}. "
        f"Final error_rate={run['error_rate']:.6g}, std={run['standard_deviation']:.6g}, "
        f"RDDM statistic={run['rddm_statistic']:.6g}, retained_window_size={run['retained_window_size']}."
    )
    if run["drift_alarm_state"] == "drift_detected":
        reset_text = " Reactive reset was recorded." if run["reset_event"] is not None else ""
        return (
            f"{base} RDDM reached drift state at {run['drift_time']}.{reset_text} "
            "This is a supervised error-rate drift candidate, not proof of root cause."
        )
    if run["warning_state"]:
        return (
            f"{base} RDDM is in warning state from {run['warning_start_time']}. "
            "This is an investigation signal, not a drift alarm."
        )
    return f"{base} No RDDM warning or drift state remained active under this finite replay policy."


def _eddm_interpretation(
    variant_id: str,
    reference_n: int,
    current_n: int,
    resolved: dict[str, Any],
    run: dict[str, Any],
) -> str:
    base = (
        f"{variant_id} replayed labeled/error rows as a finite chronological stream "
        f"(reference_n={reference_n}, current_n={current_n}). "
        f"warning_ratio={resolved['warning_level']}, drift_ratio={resolved['drift_level']}, "
        f"min_num_errors={resolved['min_num_errors']}. "
        f"Final error-distance mean={run['distance_mean']:.6g}, std={run['distance_std']:.6g}, "
        f"score_ratio={run['score_ratio']:.6g}, EDDM statistic={run['eddm_statistic']:.6g}."
    )
    if run["drift_alarm_state"] == "drift_detected":
        return (
            f"{base} EDDM reached drift state at {run['drift_time']} because error distances shortened "
            "relative to the historical maximum score. This is a supervised performance-drift candidate, "
            "not proof of root cause."
        )
    if run["warning_state"]:
        return (
            f"{base} EDDM is in warning state from {run['warning_start_time']}. "
            "The result suggests more frequent prediction errors, but it is not a drift alarm."
        )
    return f"{base} No EDDM warning or drift state remained active under this finite replay policy."


def _ecdd_wt_interpretation(
    variant_id: str,
    reference_n: int,
    current_n: int,
    resolved: dict[str, Any],
    run: dict[str, Any],
    baseline_error_rate: float,
) -> str:
    base = (
        f"{variant_id} replayed labeled/error rows as a finite chronological stream "
        f"(reference_n={reference_n}, current_n={current_n}). "
        f"lambda={resolved['lambda_value']}, warning_threshold={resolved['warning_threshold']}, "
        f"drift_threshold={resolved['drift_threshold']}, min_instances={resolved['min_instances']}. "
        f"Reference baseline error_rate={baseline_error_rate:.6g}, "
        f"final EWMA error statistic={run['ewma_error_statistic']:.6g}, "
        f"ECDD-WT statistic={run['ecdd_statistic']:.6g}."
    )
    if run["drift_alarm_state"] == "drift_detected":
        return (
            f"{base} ECDD-WT reached drift state at {run['drift_time']} because the EWMA error statistic "
            "exceeded the drift threshold. This is a supervised error-rate drift candidate, not proof of root cause."
        )
    if run["warning_state"]:
        return (
            f"{base} ECDD-WT is in warning state from {run['warning_start_time']}. "
            "This is an investigation signal for recent error increase, not a drift alarm."
        )
    return f"{base} No ECDD-WT warning or drift state remained active under this finite replay policy."


def _hddm_a_interpretation(
    variant_id: str,
    reference_n: int,
    current_n: int,
    resolved: dict[str, Any],
    run: dict[str, Any],
    reference_mean: float,
) -> str:
    base = (
        f"{variant_id} compared reference error mean to current prefix means "
        f"(reference_n={reference_n}, current_n={current_n}). "
        f"drift_confidence={resolved['drift_confidence']}, warning_confidence={resolved['warning_confidence']}, "
        f"two_sided={resolved['two_sided']}, min_instances={resolved['min_instances']}. "
        f"Reference mean={reference_mean:.6g}, current_prefix_mean={run['current_prefix_mean']:.6g}, "
        f"mean_difference={run['mean_difference']:.6g}, drift_bound={run['drift_bound']:.6g}."
    )
    if run["drift_alarm_state"] == "drift_detected":
        return (
            f"{base} HDDM-A reached drift state at {run['drift_time']} in the "
            f"{run['change_direction']} direction. This is a supervised mean-shift candidate, not proof of root cause."
        )
    if run["warning_state"]:
        return (
            f"{base} HDDM-A is in warning state from {run['warning_start_time']}. "
            "This is an investigation signal, not a drift alarm."
        )
    return f"{base} No HDDM-A warning or drift state remained active under this finite replay policy."


def _hddm_w_interpretation(
    variant_id: str,
    reference_n: int,
    current_n: int,
    resolved: dict[str, Any],
    run: dict[str, Any],
    reference_mean: float,
) -> str:
    base = (
        f"{variant_id} compared reference error mean to current weighted error mean "
        f"(reference_n={reference_n}, current_n={current_n}). "
        f"lambda={resolved['lambda_value']}, drift_confidence={resolved['drift_confidence']}, "
        f"warning_confidence={resolved['warning_confidence']}, two_sided={resolved['two_sided']}, "
        f"min_instances={resolved['min_instances']}. Reference mean={reference_mean:.6g}, "
        f"weighted_current_mean={run['weighted_current_mean']:.6g}, "
        f"weighted_mean_difference={run['weighted_mean_difference']:.6g}, "
        f"drift_bound={run['drift_bound']:.6g}."
    )
    if run["drift_alarm_state"] == "drift_detected":
        return (
            f"{base} HDDM-W reached drift state at {run['drift_time']} in the "
            f"{run['change_direction']} direction. This is a recent-weighted supervised drift candidate, "
            "not proof of root cause."
        )
    if run["warning_state"]:
        return (
            f"{base} HDDM-W is in warning state from {run['warning_start_time']}. "
            "This is an investigation signal for recent weighted error shift, not a drift alarm."
        )
    return f"{base} No HDDM-W warning or drift state remained active under this finite replay policy."


def _stepd_interpretation(
    variant_id: str,
    reference_n: int,
    current_n: int,
    resolved: dict[str, Any],
    run: dict[str, Any],
    reference_accuracy: float,
) -> str:
    base = (
        f"{variant_id} compared reference accuracy to rolling current-window accuracy "
        f"(reference_n={reference_n}, current_n={current_n}). "
        f"window_size={resolved['window_size']}, alpha_warning={resolved['alpha_warning']}, "
        f"alpha_drift={resolved['alpha_drift']}, min_instances={resolved['min_instances']}. "
        f"Reference accuracy={reference_accuracy:.6g}, current_window_accuracy={run['current_window_accuracy']:.6g}, "
        f"accuracy_delta={run['accuracy_delta']:.6g}, z={run['test_statistic']:.6g}, "
        f"p_value={run['p_value']:.6g}."
    )
    if run["drift_alarm_state"] == "drift_detected":
        return (
            f"{base} STEPD reached drift state at {run['drift_time']} because recent accuracy was significantly lower. "
            "This is a supervised performance-drift candidate, not proof of root cause."
        )
    if run["warning_state"]:
        return (
            f"{base} STEPD is in warning state from {run['warning_start_time']}. "
            "This is an investigation signal for recent accuracy degradation, not a drift alarm."
        )
    return f"{base} No STEPD warning or drift state remained active under this finite replay policy."


def _ddm_not_applicable(
    variant_id: str | None,
    warning: str,
    metadata: dict[str, Any] | None = None,
) -> DriftResult:
    return not_applicable_result(
        method_id=DDM_METHOD_ID,
        method_name=DDM_METHOD_NAME,
        method_category=DDM_METHOD_CATEGORY,
        variant_id=variant_id,
        warning=warning,
        metadata=metadata,
    )


def _rddm_not_applicable(
    variant_id: str | None,
    warning: str,
    metadata: dict[str, Any] | None = None,
) -> DriftResult:
    return not_applicable_result(
        method_id=RDDM_METHOD_ID,
        method_name=RDDM_METHOD_NAME,
        method_category=RDDM_METHOD_CATEGORY,
        variant_id=variant_id,
        warning=warning,
        metadata=metadata,
    )


def _eddm_not_applicable(
    variant_id: str | None,
    warning: str,
    metadata: dict[str, Any] | None = None,
) -> DriftResult:
    return not_applicable_result(
        method_id=EDDM_METHOD_ID,
        method_name=EDDM_METHOD_NAME,
        method_category=EDDM_METHOD_CATEGORY,
        variant_id=variant_id,
        warning=warning,
        metadata=metadata,
    )


def _ecdd_wt_not_applicable(
    variant_id: str | None,
    warning: str,
    metadata: dict[str, Any] | None = None,
) -> DriftResult:
    return not_applicable_result(
        method_id=ECDD_WT_METHOD_ID,
        method_name=ECDD_WT_METHOD_NAME,
        method_category=ECDD_WT_METHOD_CATEGORY,
        variant_id=variant_id,
        warning=warning,
        metadata=metadata,
    )


def _hddm_a_not_applicable(
    variant_id: str | None,
    warning: str,
    metadata: dict[str, Any] | None = None,
) -> DriftResult:
    return not_applicable_result(
        method_id=HDDM_A_METHOD_ID,
        method_name=HDDM_A_METHOD_NAME,
        method_category=HDDM_A_METHOD_CATEGORY,
        variant_id=variant_id,
        warning=warning,
        metadata=metadata,
    )


def _hddm_w_not_applicable(
    variant_id: str | None,
    warning: str,
    metadata: dict[str, Any] | None = None,
) -> DriftResult:
    return not_applicable_result(
        method_id=HDDM_W_METHOD_ID,
        method_name=HDDM_W_METHOD_NAME,
        method_category=HDDM_W_METHOD_CATEGORY,
        variant_id=variant_id,
        warning=warning,
        metadata=metadata,
    )


def _stepd_not_applicable(
    variant_id: str | None,
    warning: str,
    metadata: dict[str, Any] | None = None,
) -> DriftResult:
    return not_applicable_result(
        method_id=STEPD_METHOD_ID,
        method_name=STEPD_METHOD_NAME,
        method_category=STEPD_METHOD_CATEGORY,
        variant_id=variant_id,
        warning=warning,
        metadata=metadata,
    )


def _parse_window(window: tuple[str, str], name: str) -> tuple[pd.Timestamp, pd.Timestamp]:
    if len(window) != 2:
        raise ValueError(f"{name} must be a (start, end) pair")
    start = pd.to_datetime(window[0], errors="coerce")
    end = pd.to_datetime(window[1], errors="coerce")
    if pd.isna(start) or pd.isna(end):
        raise ValueError(f"{name} contains an unparseable timestamp")
    if start > end:
        raise ValueError(f"{name} start must be <= end")
    return start, end


def _as_positive_int(value: Any, name: str) -> int:
    if isinstance(value, bool):
        raise ValueError(f"{name} must be a positive integer")
    try:
        int_value = int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must be a positive integer") from exc
    if int_value <= 0 or float(value) != float(int_value):
        raise ValueError(f"{name} must be a positive integer")
    return int_value


def _as_float(value: Any, name: str) -> float:
    if isinstance(value, bool):
        raise ValueError(f"{name} must be a finite number")
    try:
        float_value = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must be a finite number") from exc
    if not np.isfinite(float_value):
        raise ValueError(f"{name} must be finite")
    return float_value


def _as_bool(value: Any, name: str) -> bool:
    if isinstance(value, bool):
        return value
    raise ValueError(f"{name} must be boolean")


def _iso_time(value: np.datetime64) -> str:
    return pd.Timestamp(value).isoformat()
