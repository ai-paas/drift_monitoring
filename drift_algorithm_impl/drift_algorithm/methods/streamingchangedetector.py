from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
from scipy.special import gammaln
from scipy.stats import ks_2samp

from drift_algorithm.core.result import DriftResult, not_applicable_result


ADWIN_METHOD_ID = "DM-026"
ADWIN_METHOD_NAME = "ADWIN"
ADWIN_METHOD_CATEGORY = "StreamingChangeDetector"
KSWIN_METHOD_ID = "DM-027"
KSWIN_METHOD_NAME = "KSWIN"
KSWIN_METHOD_CATEGORY = "StreamingChangeDetector"
PAGE_HINKLEY_METHOD_ID = "DM-028"
PAGE_HINKLEY_METHOD_NAME = "Page-Hinkley Test"
PAGE_HINKLEY_METHOD_CATEGORY = "StreamingChangeDetector"
CUSUM_METHOD_ID = "DM-029"
CUSUM_METHOD_NAME = "CUSUM"
CUSUM_METHOD_CATEGORY = "StreamingChangeDetector"
EWMA_METHOD_ID = "DM-030"
EWMA_METHOD_NAME = "EWMA"
EWMA_METHOD_CATEGORY = "StreamingChangeDetector"
GMA_METHOD_ID = "DM-031"
GMA_METHOD_NAME = "Geometric Moving Average"
GMA_METHOD_CATEGORY = "StreamingChangeDetector"
BOCD_METHOD_ID = "DM-032"
BOCD_METHOD_NAME = "BOCD"
BOCD_METHOD_CATEGORY = "StreamingChangeDetector"
SEQDRIFT_METHOD_ID = "DM-033"
SEQDRIFT_METHOD_NAME = "SeqDrift"
SEQDRIFT_METHOD_CATEGORY = "StreamingChangeDetector"
SPRT_METHOD_ID = "DM-034"
SPRT_METHOD_NAME = "SPRT"
SPRT_METHOD_CATEGORY = "StreamingChangeDetector"

SUPPORTED_ADWIN_VARIANTS = {"ADWIN_MEAN_STREAM", "ADWIN_ERROR_RATE", "ADWIN_DISTANCE_STREAM"}
DEFERRED_ADWIN_VARIANTS: set[str] = set()
SUPPORTED_KSWIN_VARIANTS = {"KSWIN_STANDARD", "KSWIN_NUMERIC_STREAM", "KSWIN_WITH_SUBSAMPLING"}
DEFERRED_KSWIN_VARIANTS: set[str] = set()
SUPPORTED_PAGE_HINKLEY_VARIANTS = {"PAGE_HINKLEY_INCREASE", "PAGE_HINKLEY_DECREASE"}
DEFERRED_PAGE_HINKLEY_VARIANTS = {"DRIFT_RETRAINING_WITH_PAGE_HINKLEY"}
SUPPORTED_CUSUM_VARIANTS = {
    "ONE_SIDED_UPPER_CUSUM",
    "ONE_SIDED_LOWER_CUSUM",
    "TWO_SIDED_CUSUM",
    "CUSUM_ON_DISTANCE_STREAM",
}
DEFERRED_CUSUM_VARIANTS: set[str] = set()
SUPPORTED_EWMA_VARIANTS = {"EWMA_UNIVARIATE_CONTROL_CHART", "EWMA_ONE_SIDED", "EWMA_BASELINE_REPLAY_THRESHOLD"}
DEFERRED_EWMA_VARIANTS: set[str] = set()
SUPPORTED_GMA_VARIANTS = {"GMA_CONTROL_CHART", "GMA_ONE_SIDED", "GMA_WITH_EMPIRICAL_LIMIT"}
DEFERRED_GMA_VARIANTS: set[str] = set()
SUPPORTED_BOCD_VARIANTS = {
    "BAYESIAN_ONLINE_CHANGE_POINT_GAUSSIAN",
    "BOCD_HAZARD_RATE_VARIANT",
    "BOCD_PREDICTIVE_PROBABILITY",
}
SUPPORTED_SEQDRIFT_VARIANTS = {"SEQDRIFT1", "SEQDRIFT2"}
SUPPORTED_SPRT_VARIANTS = {"SPRT_BERNOULLI_ERROR_RATE", "SPRT_GAUSSIAN_MEAN_SHIFT"}


# @managed-contract contract_id=drift_algorithm.streaming.detect_adwin level=P0
def detect_adwin(
    data: pd.DataFrame,
    *,
    time_col: str = "time",
    value_col: str | None = "value",
    reference_window: tuple[str, str] | None = None,
    current_window: tuple[str, str] | None = None,
    params: dict[str, Any] | None = None,
) -> DriftResult:
    params = dict(params or {})
    variant_id = str(params.get("variant_id", "ADWIN_MEAN_STREAM")).upper()
    metadata: dict[str, Any] = {
        "params": params,
        "finite_replay_policy": "reference_window_for_validation_or_calibration_then_current_window_sprt",
    }

    if variant_id in DEFERRED_ADWIN_VARIANTS:
        return _adwin_not_applicable(
            variant_id,
            f"ADWIN variant requires a separate input contract and is not implemented yet: {variant_id}",
            metadata,
        )
    if variant_id not in SUPPORTED_ADWIN_VARIANTS:
        return _adwin_not_applicable(variant_id, f"unsupported ADWIN variant: {variant_id}", metadata)
    if any(params.get(key) is not None for key in ("feature_cols", "embedding_cols", "category_col", "count_col")):
        return _adwin_not_applicable(
            variant_id,
            "categorical, count, multivariate, and embedding ADWIN inputs are not implemented yet",
            metadata,
        )
    if variant_id != "ADWIN_ERROR_RATE" and any(params.get(key) is not None for key in ("y_true", "y_pred", "label_col", "error_col")):
        return _adwin_not_applicable(
            variant_id,
            "raw label or prediction columns require the deferred ADWIN_ERROR_RATE contract",
            metadata,
        )
    if variant_id != "ADWIN_DISTANCE_STREAM" and any(params.get(key) is not None for key in ("base_distance_method", "distance_window_size")):
        return _adwin_not_applicable(
            variant_id,
            "distance stream settings require the deferred ADWIN_DISTANCE_STREAM contract",
            metadata,
        )

    try:
        resolved = _resolve_adwin_params(params)
        prepared = _prepare_adwin_stream(
            data,
            time_col=time_col,
            value_col=value_col,
            reference_window=reference_window,
            current_window=current_window,
            params=params,
            min_reference_size=resolved["min_reference_size"],
            min_current_size=resolved["min_current_size"],
        )
    except (KeyError, TypeError, ValueError) as exc:
        return _adwin_not_applicable(variant_id, str(exc), metadata)

    metadata.update(prepared["metadata"])
    metadata.update(
        {
            "backend": "numpy_exact_window_adwin",
            "compression_policy": "not_compressed_exact_finite_replay",
            "value_col": prepared["value_col"],
            "delta": resolved["delta"],
            "clock": resolved["clock"],
            "max_buckets": resolved["max_buckets"],
            "min_window_length": resolved["min_window_length"],
            "grace_period": resolved["grace_period"],
        }
    )
    if variant_id == "ADWIN_ERROR_RATE":
        metadata["stream_semantics"] = "projected_error_rate_stream"
        metadata["projection_policy"] = "bucket_mean_as_error_rate"
    elif variant_id == "ADWIN_DISTANCE_STREAM":
        metadata["stream_semantics"] = "projected_distance_stream"
        metadata["projection_policy"] = "bucket_mean_as_distance"
    warnings = list(prepared["warnings"])
    if params.get("threshold_or_alpha") is not None:
        warnings.append("threshold_or_alpha was interpreted as ADWIN delta")
    if resolved["clock"] > 1:
        warnings.append("clock > 1 checks ADWIN alarms periodically and may delay detection")
    if params.get("multiple_testing_correction", "none") not in (None, "none"):
        warnings.append("multiple_testing_correction is recorded but not applied by detect_adwin")

    ref_n = len(prepared["reference_values"])
    cur_n = len(prepared["current_values"])
    if ref_n and cur_n:
        imbalance_ratio = max(ref_n, cur_n) / min(ref_n, cur_n)
        if imbalance_ratio > resolved["sample_imbalance_warning_ratio"]:
            warnings.append(
                f"reference/current sample sizes are imbalanced (ratio={imbalance_ratio:.3g})"
            )
    if len(prepared["stream_values"]) <= resolved["grace_period"] * 2:
        warnings.append("finite replay length is close to the ADWIN grace_period")

    try:
        run = _run_adwin_mean_stream(
            prepared["stream_values"],
            prepared["stream_times"],
            delta=resolved["delta"],
            clock=resolved["clock"],
            max_buckets=resolved["max_buckets"],
            min_window_length=resolved["min_window_length"],
            grace_period=resolved["grace_period"],
            record_events=resolved["record_events"],
            max_event_records=resolved["max_event_records"],
        )
    except (FloatingPointError, ValueError) as exc:
        return DriftResult(
            method_id=ADWIN_METHOD_ID,
            method_name=ADWIN_METHOD_NAME,
            method_category=ADWIN_METHOD_CATEGORY,
            variant_id=variant_id,
            drift_detected=None,
            severity="error",
            threshold=resolved["delta"],
            warnings=warnings + [str(exc)],
            metadata=metadata,
            interpretation=f"ADWIN calculation failed: {exc}",
        )

    if run["event_history_truncated"]:
        warnings.append("ADWIN alarm event history was truncated by max_event_records")

    alarm_count = int(run["alarm_count"])
    drift_detected = alarm_count > 0
    severity = "drift_detected" if drift_detected else "normal"
    alarm_state = "drift_detected" if drift_detected else "normal"
    summary = _numeric_summary(prepared["reference_values"], prepared["current_values"])

    measurements: dict[str, Any] = {
        "DRIFT_ALARM_STATE": alarm_state,
        "WINDOW_SIZE": run["window_size"],
        "ADAPTIVE_WINDOW_WIDTH": run["window_size"],
        "ALARM_COUNT": alarm_count,
        "FIRST_ALARM_TIME": run["first_alarm_time"],
        "LAST_ALARM_TIME": run["last_alarm_time"],
        "FIRST_ALARM_INDEX": run["first_alarm_index"],
        "LAST_ALARM_INDEX": run["last_alarm_index"],
        "FINAL_WINDOW_MEAN": run["final_window_mean"],
        "FINAL_WINDOW_VARIANCE": run["final_window_variance"],
        "FINAL_WINDOW_MIN": run["final_window_min"],
        "FINAL_WINDOW_MAX": run["final_window_max"],
        "PROCESSED_COUNT": len(prepared["stream_values"]),
        "SAMPLE_SIZE": {
            "reference": ref_n,
            "current": cur_n,
            "stream": len(prepared["stream_values"]),
            "dropped_reference": prepared["metadata"]["reference_original_count"] - ref_n,
            "dropped_current": prepared["metadata"]["current_original_count"] - cur_n,
        },
        "SAMPLE_SIZE_REFERENCE": ref_n,
        "SAMPLE_SIZE_CURRENT": cur_n,
        "DELTA": resolved["delta"],
        "CLOCK": resolved["clock"],
        "MAX_BUCKETS": resolved["max_buckets"],
        "MIN_WINDOW_LENGTH": resolved["min_window_length"],
        "GRACE_PERIOD": resolved["grace_period"],
        **summary,
    }
    if resolved["record_events"]:
        measurements["ALARM_EVENTS"] = run["events"]

    metadata.update(
        {
            "record_events": resolved["record_events"],
            "max_event_records": resolved["max_event_records"],
            "event_history_truncated": run["event_history_truncated"],
        }
    )

    return DriftResult(
        method_id=ADWIN_METHOD_ID,
        method_name=ADWIN_METHOD_NAME,
        method_category=ADWIN_METHOD_CATEGORY,
        variant_id=variant_id,
        drift_detected=drift_detected,
        severity=severity,
        threshold=resolved["delta"],
        measurements=measurements,
        interpretation=_adwin_interpretation(
            variant_id,
            ref_n,
            cur_n,
            len(prepared["stream_values"]),
            resolved,
            run,
            alarm_state,
        ),
        warnings=warnings,
        metadata=metadata,
    )


def detect_kswin(
    data: pd.DataFrame,
    *,
    time_col: str = "time",
    value_col: str | None = "value",
    reference_window: tuple[str, str] | None = None,
    current_window: tuple[str, str] | None = None,
    params: dict[str, Any] | None = None,
) -> DriftResult:
    params = dict(params or {})
    variant_id = str(params.get("variant_id", "KSWIN_STANDARD")).upper()
    metadata: dict[str, Any] = {
        "params": params,
        "finite_replay_policy": "reference_and_current_windows_sorted_by_time",
    }

    if variant_id in DEFERRED_KSWIN_VARIANTS:
        return _kswin_not_applicable(
            variant_id,
            "KSWIN_WITH_SUBSAMPLING requires an approved sampling and reproducibility contract",
            metadata,
        )
    if variant_id not in SUPPORTED_KSWIN_VARIANTS:
        return _kswin_not_applicable(variant_id, f"unsupported KSWIN variant: {variant_id}", metadata)
    if any(params.get(key) is not None for key in ("feature_cols", "embedding_cols", "category_col", "count_col")):
        return _kswin_not_applicable(
            variant_id,
            "categorical, count, multivariate, and embedding KSWIN inputs are not implemented yet",
            metadata,
        )
    if any(params.get(key) is not None for key in ("y_true", "y_pred", "label_col", "error_col")):
        return _kswin_not_applicable(
            variant_id,
            "raw label or prediction columns are not valid KSWIN numeric-stream input",
            metadata,
        )

    try:
        resolved = _resolve_kswin_params(params)
        prepared = _prepare_adwin_stream(
            data,
            time_col=time_col,
            value_col=value_col,
            reference_window=reference_window,
            current_window=current_window,
            params=params,
            min_reference_size=resolved["min_reference_size"],
            min_current_size=resolved["min_current_size"],
        )
        if variant_id == "KSWIN_WITH_SUBSAMPLING":
            prepared = _apply_kswin_subsampling(prepared, resolved, params)
        if len(prepared["stream_values"]) < resolved["window_size"]:
            raise ValueError(
                f"effective stream length {len(prepared['stream_values'])} is below window_size {resolved['window_size']}"
            )
    except (KeyError, TypeError, ValueError) as exc:
        return _kswin_not_applicable(variant_id, str(exc), metadata)

    metadata.update(prepared["metadata"])
    metadata.update(
        {
            "backend": "scipy.stats.ks_2samp",
            "value_col": prepared["value_col"],
            "alpha": resolved["alpha"],
            "window_size": resolved["window_size"],
            "stat_size": resolved["stat_size"],
            "check_every": resolved["check_every"],
            "tie_policy": resolved["tie_policy"],
            "sampling_policy": prepared["metadata"].get("sampling_policy"),
        }
    )
    warnings = list(prepared["warnings"])
    if params.get("threshold_or_alpha") is not None:
        warnings.append("threshold_or_alpha was interpreted as KSWIN alpha")
    if resolved["check_every"] > 1:
        warnings.append("check_every > 1 checks KSWIN alarms periodically and may delay detection")
    if params.get("multiple_testing_correction", "none") not in (None, "none"):
        warnings.append("multiple_testing_correction is recorded but not applied by detect_kswin")
    warnings.extend(prepared.get("sampling_warnings", []))

    ref_n = len(prepared["reference_values"])
    cur_n = len(prepared["current_values"])
    imbalance_ratio = max(ref_n, cur_n) / min(ref_n, cur_n)
    if imbalance_ratio > resolved["sample_imbalance_warning_ratio"]:
        warnings.append(f"reference/current sample sizes are imbalanced (ratio={imbalance_ratio:.3g})")
    if len(prepared["stream_values"]) <= resolved["window_size"] * 2:
        warnings.append("finite replay length is close to the KSWIN window_size")

    try:
        run = _run_kswin_stream(
            prepared["stream_values"],
            prepared["stream_times"],
            alpha=resolved["alpha"],
            window_size=resolved["window_size"],
            stat_size=resolved["stat_size"],
            check_every=resolved["check_every"],
            record_events=resolved["record_events"],
            max_event_records=resolved["max_event_records"],
        )
    except (FloatingPointError, ValueError) as exc:
        return DriftResult(
            method_id=KSWIN_METHOD_ID,
            method_name=KSWIN_METHOD_NAME,
            method_category=KSWIN_METHOD_CATEGORY,
            variant_id=variant_id,
            drift_detected=None,
            severity="error",
            threshold=resolved["alpha"],
            warnings=warnings + [str(exc)],
            metadata=metadata,
            interpretation=f"KSWIN calculation failed: {exc}",
        )

    if run["event_history_truncated"]:
        warnings.append("KSWIN alarm event history was truncated by max_event_records")

    alarm_count = int(run["alarm_count"])
    drift_detected = alarm_count > 0
    severity = "drift_detected" if drift_detected else "normal"
    alarm_state = "drift_detected" if drift_detected else "normal"
    top_p = run["min_alarm_p_value"] if drift_detected else run["last_p_value"]
    top_stat = run["max_alarm_statistic"] if drift_detected else run["last_statistic"]
    summary = _numeric_summary(prepared["reference_values"], prepared["current_values"])

    measurements: dict[str, Any] = {
        "TEST_STATISTIC": top_stat,
        "P_VALUE": top_p,
        "DRIFT_ALARM_STATE": alarm_state,
        "KS_STATISTIC": top_stat,
        "LAST_KS_STATISTIC": run["last_statistic"],
        "LAST_P_VALUE": run["last_p_value"],
        "WINDOW_SIZE": resolved["window_size"],
        "STAT_SIZE": resolved["stat_size"],
        "REFERENCE_SUBWINDOW_SIZE": resolved["window_size"] - resolved["stat_size"],
        "ALPHA": resolved["alpha"],
        "CHECK_EVERY": resolved["check_every"],
        "SAMPLING_POLICY": prepared["metadata"].get("sampling_policy", "none"),
        "SUBSAMPLE_SIZE": prepared["metadata"].get("subsample_size"),
        "ALARM_COUNT": alarm_count,
        "FIRST_ALARM_TIME": run["first_alarm_time"],
        "LAST_ALARM_TIME": run["last_alarm_time"],
        "FIRST_ALARM_INDEX": run["first_alarm_index"],
        "LAST_ALARM_INDEX": run["last_alarm_index"],
        "PROCESSED_COUNT": len(prepared["stream_values"]),
        "CHECK_COUNT": run["check_count"],
        "LAST_CHECK_TIME": run["last_check_time"],
        "SAMPLE_SIZE": {
            "reference": ref_n,
            "current": cur_n,
            "stream": len(prepared["stream_values"]),
            "dropped_reference": prepared["metadata"]["reference_original_count"] - ref_n,
            "dropped_current": prepared["metadata"]["current_original_count"] - cur_n,
        },
        "SAMPLE_SIZE_REFERENCE": ref_n,
        "SAMPLE_SIZE_CURRENT": cur_n,
        **summary,
    }
    if resolved["record_events"]:
        measurements["ALARM_EVENTS"] = run["events"]

    return DriftResult(
        method_id=KSWIN_METHOD_ID,
        method_name=KSWIN_METHOD_NAME,
        method_category=KSWIN_METHOD_CATEGORY,
        variant_id=variant_id,
        drift_detected=drift_detected,
        severity=severity,
        drift_score=top_stat,
        p_value=top_p,
        test_statistic=top_stat,
        threshold=resolved["alpha"],
        measurements=measurements,
        interpretation=_kswin_interpretation(
            variant_id,
            ref_n,
            cur_n,
            len(prepared["stream_values"]),
            resolved,
            run,
            alarm_state,
        ),
        warnings=warnings,
        metadata=metadata,
    )


def detect_page_hinkley_test(
    data: pd.DataFrame,
    *,
    time_col: str = "time",
    value_col: str | None = "value",
    reference_window: tuple[str, str] | None = None,
    current_window: tuple[str, str] | None = None,
    params: dict[str, Any] | None = None,
) -> DriftResult:
    params = dict(params or {})
    variant_id = str(params.get("variant_id", "PAGE_HINKLEY_INCREASE")).upper()
    metadata: dict[str, Any] = {
        "params": params,
        "finite_replay_policy": "reference_and_current_windows_sorted_by_time",
    }

    if variant_id in DEFERRED_PAGE_HINKLEY_VARIANTS:
        return _page_hinkley_not_applicable(
            variant_id,
            "DRIFT_RETRAINING_WITH_PAGE_HINKLEY belongs to DM-056 and requires retraining policy inputs",
            metadata,
        )
    if variant_id not in SUPPORTED_PAGE_HINKLEY_VARIANTS:
        return _page_hinkley_not_applicable(variant_id, f"unsupported Page-Hinkley variant: {variant_id}", metadata)
    if any(params.get(key) is not None for key in ("feature_cols", "embedding_cols", "category_col", "count_col")):
        return _page_hinkley_not_applicable(
            variant_id,
            "categorical, count, multivariate, and embedding Page-Hinkley inputs are not implemented yet",
            metadata,
        )
    if any(params.get(key) is not None for key in ("y_true", "y_pred", "label_col", "error_col")):
        return _page_hinkley_not_applicable(
            variant_id,
            "supervised Page-Hinkley requires an explicit error stream contract",
            metadata,
        )

    try:
        resolved = _resolve_page_hinkley_params(params, variant_id)
        prepared = _prepare_adwin_stream(
            data,
            time_col=time_col,
            value_col=value_col,
            reference_window=reference_window,
            current_window=current_window,
            params=params,
            min_reference_size=resolved["min_reference_size"],
            min_current_size=resolved["min_current_size"],
        )
        if len(prepared["stream_values"]) < resolved["min_instances"]:
            raise ValueError(
                f"effective stream length {len(prepared['stream_values'])} is below min_instances {resolved['min_instances']}"
            )
    except (KeyError, TypeError, ValueError) as exc:
        return _page_hinkley_not_applicable(variant_id, str(exc), metadata)

    metadata.update(prepared["metadata"])
    metadata.update(
        {
            "backend": "numpy_page_hinkley",
            "value_col": prepared["value_col"],
            "threshold": resolved["threshold"],
            "delta": resolved["delta"],
            "direction": resolved["direction"],
            "min_instances": resolved["min_instances"],
            "check_every": resolved["check_every"],
            "reset_policy": resolved["reset_policy"],
            "alpha": resolved["alpha"],
            "alpha_policy": "metadata_only",
        }
    )
    warnings = list(prepared["warnings"])
    if params.get("threshold_or_alpha") is not None:
        warnings.append("threshold_or_alpha was interpreted as Page-Hinkley threshold")
    if resolved["alpha"] is not None:
        warnings.append("alpha is recorded but not used by the NumPy Page-Hinkley implementation")
    if resolved["check_every"] > 1:
        warnings.append("check_every > 1 checks Page-Hinkley alarms periodically and may delay detection")

    ref_n = len(prepared["reference_values"])
    cur_n = len(prepared["current_values"])
    imbalance_ratio = max(ref_n, cur_n) / min(ref_n, cur_n)
    if imbalance_ratio > resolved["sample_imbalance_warning_ratio"]:
        warnings.append(f"reference/current sample sizes are imbalanced (ratio={imbalance_ratio:.3g})")
    if len(prepared["stream_values"]) <= resolved["min_instances"] * 2:
        warnings.append("finite replay length is close to Page-Hinkley min_instances")

    try:
        run = _run_page_hinkley_stream(
            prepared["stream_values"],
            prepared["stream_times"],
            direction=resolved["direction"],
            threshold=resolved["threshold"],
            delta=resolved["delta"],
            min_instances=resolved["min_instances"],
            check_every=resolved["check_every"],
            reset_policy=resolved["reset_policy"],
            record_events=resolved["record_events"],
            max_event_records=resolved["max_event_records"],
        )
    except (FloatingPointError, ValueError) as exc:
        return DriftResult(
            method_id=PAGE_HINKLEY_METHOD_ID,
            method_name=PAGE_HINKLEY_METHOD_NAME,
            method_category=PAGE_HINKLEY_METHOD_CATEGORY,
            variant_id=variant_id,
            drift_detected=None,
            severity="error",
            threshold=resolved["threshold"],
            warnings=warnings + [str(exc)],
            metadata=metadata,
            interpretation=f"Page-Hinkley calculation failed: {exc}",
        )

    if run["event_history_truncated"]:
        warnings.append("Page-Hinkley alarm event history was truncated by max_event_records")

    alarm_count = int(run["alarm_count"])
    drift_detected = alarm_count > 0
    severity = "drift_detected" if drift_detected else "normal"
    alarm_state = "drift_detected" if drift_detected else "normal"
    summary = _numeric_summary(prepared["reference_values"], prepared["current_values"])

    measurements: dict[str, Any] = {
        "PAGE_HINKLEY_STATISTIC": run["final_statistic"],
        "DRIFT_ALARM_STATE": alarm_state,
        "PH_STATISTIC": run["final_statistic"],
        "MAX_PAGE_HINKLEY_STATISTIC": run["max_statistic"],
        "THRESHOLD": resolved["threshold"],
        "DELTA": resolved["delta"],
        "DIRECTION": resolved["direction"],
        "RESET_POLICY": resolved["reset_policy"],
        "MIN_INSTANCES": resolved["min_instances"],
        "CHECK_EVERY": resolved["check_every"],
        "ALARM_COUNT": alarm_count,
        "FIRST_ALARM_TIME": run["first_alarm_time"],
        "LAST_ALARM_TIME": run["last_alarm_time"],
        "FIRST_ALARM_INDEX": run["first_alarm_index"],
        "LAST_ALARM_INDEX": run["last_alarm_index"],
        "PROCESSED_COUNT": len(prepared["stream_values"]),
        "SAMPLE_SIZE": {
            "reference": ref_n,
            "current": cur_n,
            "stream": len(prepared["stream_values"]),
            "dropped_reference": prepared["metadata"]["reference_original_count"] - ref_n,
            "dropped_current": prepared["metadata"]["current_original_count"] - cur_n,
        },
        "SAMPLE_SIZE_REFERENCE": ref_n,
        "SAMPLE_SIZE_CURRENT": cur_n,
        "FINAL_RUNNING_MEAN": run["final_running_mean"],
        "FINAL_CUMULATIVE_DEVIATION": run["final_cumulative"],
        "FINAL_MIN_CUMULATIVE_DEVIATION": run["final_min_cumulative"],
        **summary,
    }
    if resolved["record_events"]:
        measurements["ALARM_EVENTS"] = run["events"]

    return DriftResult(
        method_id=PAGE_HINKLEY_METHOD_ID,
        method_name=PAGE_HINKLEY_METHOD_NAME,
        method_category=PAGE_HINKLEY_METHOD_CATEGORY,
        variant_id=variant_id,
        drift_detected=drift_detected,
        severity=severity,
        drift_score=run["max_statistic"],
        p_value=None,
        test_statistic=run["final_statistic"],
        threshold=resolved["threshold"],
        measurements=measurements,
        interpretation=_page_hinkley_interpretation(
            variant_id,
            ref_n,
            cur_n,
            len(prepared["stream_values"]),
            resolved,
            run,
            alarm_state,
        ),
        warnings=warnings,
        metadata=metadata,
    )


def detect_cusum(
    data: pd.DataFrame,
    *,
    time_col: str = "time",
    value_col: str | None = "value",
    reference_window: tuple[str, str] | None = None,
    current_window: tuple[str, str] | None = None,
    params: dict[str, Any] | None = None,
) -> DriftResult:
    params = dict(params or {})
    variant_id = str(params.get("variant_id", "ONE_SIDED_UPPER_CUSUM")).upper()
    metadata: dict[str, Any] = {
        "params": params,
        "finite_replay_policy": "reference_and_current_windows_sorted_by_time",
    }

    if variant_id in DEFERRED_CUSUM_VARIANTS:
        return _cusum_not_applicable(
            variant_id,
            "CUSUM_ON_DISTANCE_STREAM requires an approved upstream distance-stream contract",
            metadata,
        )
    if variant_id not in SUPPORTED_CUSUM_VARIANTS:
        return _cusum_not_applicable(variant_id, f"unsupported CUSUM variant: {variant_id}", metadata)
    if any(params.get(key) is not None for key in ("feature_cols", "embedding_cols", "category_col", "count_col")):
        return _cusum_not_applicable(
            variant_id,
            "categorical, count, multivariate, and embedding CUSUM inputs are not implemented yet",
            metadata,
        )
    if any(params.get(key) is not None for key in ("y_true", "y_pred", "label_col", "error_col")):
        return _cusum_not_applicable(
            variant_id,
            "supervised CUSUM requires an explicit error stream contract",
            metadata,
        )
    try:
        resolved_pre = _resolve_cusum_params(params, variant_id)
        prepared = _prepare_adwin_stream(
            data,
            time_col=time_col,
            value_col=value_col,
            reference_window=reference_window,
            current_window=current_window,
            params=params,
            min_reference_size=resolved_pre["min_reference_size"],
            min_current_size=resolved_pre["min_current_size"],
        )
        resolved = _finalize_cusum_calibration(resolved_pre, params, prepared["reference_values"])
        if len(prepared["stream_values"]) < resolved["warmup_size"]:
            raise ValueError(
                f"effective stream length {len(prepared['stream_values'])} is below warmup_size {resolved['warmup_size']}"
            )
    except (KeyError, TypeError, ValueError) as exc:
        return _cusum_not_applicable(variant_id, str(exc), metadata)

    metadata.update(prepared["metadata"])
    metadata.update(
        {
            "backend": "numpy_cusum",
            "value_col": prepared["value_col"],
            "target_mean": resolved["target_mean"],
            "target_mean_policy": resolved["target_mean_policy"],
            "allowance_k": resolved["allowance_k"],
            "allowance_k_policy": resolved["allowance_k_policy"],
            "decision_threshold_h": resolved["decision_threshold_h"],
            "decision_threshold_h_policy": resolved["decision_threshold_h_policy"],
            "direction": resolved["direction"],
            "warmup_size": resolved["warmup_size"],
            "check_every": resolved["check_every"],
            "reset_policy": resolved["reset_policy"],
        }
    )
    warnings = list(prepared["warnings"])
    if resolved["target_mean_policy"] == "reference_mean":
        warnings.append("target_mean was inferred from the effective reference window")
    if resolved["allowance_k_policy"] == "reference_std":
        warnings.append("allowance_k was inferred from the effective reference standard deviation")
    if resolved["decision_threshold_h_policy"] == "reference_std":
        warnings.append("decision_threshold_h was inferred from the effective reference standard deviation")
    if resolved["reference_std"] == 0.0:
        warnings.append("reference standard deviation is zero; default CUSUM calibration used fallback scale")
    if params.get("threshold") is not None or params.get("threshold_or_alpha") is not None:
        warnings.append("threshold alias was interpreted as CUSUM decision_threshold_h")
    if resolved["check_every"] > 1:
        warnings.append("check_every > 1 checks CUSUM alarms periodically and may delay detection")

    ref_n = len(prepared["reference_values"])
    cur_n = len(prepared["current_values"])
    imbalance_ratio = max(ref_n, cur_n) / min(ref_n, cur_n)
    if imbalance_ratio > resolved["sample_imbalance_warning_ratio"]:
        warnings.append(f"reference/current sample sizes are imbalanced (ratio={imbalance_ratio:.3g})")
    if len(prepared["stream_values"]) <= resolved["warmup_size"] * 2:
        warnings.append("finite replay length is close to CUSUM warmup_size")

    try:
        run = _run_cusum_stream(
            prepared["stream_values"],
            prepared["stream_times"],
            variant_id=variant_id,
            direction=resolved["direction"],
            target_mean=resolved["target_mean"],
            allowance_k=resolved["allowance_k"],
            decision_threshold_h=resolved["decision_threshold_h"],
            warmup_size=resolved["warmup_size"],
            check_every=resolved["check_every"],
            reset_policy=resolved["reset_policy"],
            record_events=resolved["record_events"],
            max_event_records=resolved["max_event_records"],
        )
    except (FloatingPointError, ValueError) as exc:
        return DriftResult(
            method_id=CUSUM_METHOD_ID,
            method_name=CUSUM_METHOD_NAME,
            method_category=CUSUM_METHOD_CATEGORY,
            variant_id=variant_id,
            drift_detected=None,
            severity="error",
            threshold=resolved["decision_threshold_h"],
            warnings=warnings + [str(exc)],
            metadata=metadata,
            interpretation=f"CUSUM calculation failed: {exc}",
        )

    if run["event_history_truncated"]:
        warnings.append("CUSUM alarm event history was truncated by max_event_records")

    alarm_count = int(run["alarm_count"])
    drift_detected = alarm_count > 0
    severity = "drift_detected" if drift_detected else "normal"
    alarm_state = "drift_detected" if drift_detected else "normal"
    summary = _numeric_summary_with_std(prepared["reference_values"], prepared["current_values"])
    monitored_final = _cusum_monitored_final(variant_id, run)
    monitored_max = _cusum_monitored_max(variant_id, run)

    measurements: dict[str, Any] = {
        "CUSUM_STATISTIC": monitored_final,
        "DRIFT_ALARM_STATE": alarm_state,
        "CUSUM_POSITIVE": run["final_positive"],
        "CUSUM_NEGATIVE": run["final_negative"],
        "MAX_CUSUM_POSITIVE": run["max_positive"],
        "MAX_CUSUM_NEGATIVE": run["max_negative"],
        "TARGET_MEAN": resolved["target_mean"],
        "ALLOWANCE_K": resolved["allowance_k"],
        "DECISION_THRESHOLD_H": resolved["decision_threshold_h"],
        "DIRECTION": resolved["direction"],
        "RESET_POLICY": resolved["reset_policy"],
        "WARMUP_SIZE": resolved["warmup_size"],
        "CHECK_EVERY": resolved["check_every"],
        "ALARM_COUNT": alarm_count,
        "FIRST_ALARM_TIME": run["first_alarm_time"],
        "LAST_ALARM_TIME": run["last_alarm_time"],
        "FIRST_ALARM_INDEX": run["first_alarm_index"],
        "LAST_ALARM_INDEX": run["last_alarm_index"],
        "FIRST_ALARM_DIRECTION": run["first_alarm_direction"],
        "LAST_ALARM_DIRECTION": run["last_alarm_direction"],
        "PROCESSED_COUNT": len(prepared["stream_values"]),
        "SAMPLE_SIZE": {
            "reference": ref_n,
            "current": cur_n,
            "stream": len(prepared["stream_values"]),
            "dropped_reference": prepared["metadata"]["reference_original_count"] - ref_n,
            "dropped_current": prepared["metadata"]["current_original_count"] - cur_n,
        },
        "SAMPLE_SIZE_REFERENCE": ref_n,
        "SAMPLE_SIZE_CURRENT": cur_n,
        **summary,
    }
    if resolved["record_events"]:
        measurements["ALARM_EVENTS"] = run["events"]

    return DriftResult(
        method_id=CUSUM_METHOD_ID,
        method_name=CUSUM_METHOD_NAME,
        method_category=CUSUM_METHOD_CATEGORY,
        variant_id=variant_id,
        drift_detected=drift_detected,
        severity=severity,
        drift_score=monitored_max,
        p_value=None,
        test_statistic=monitored_final,
        threshold=resolved["decision_threshold_h"],
        measurements=measurements,
        interpretation=_cusum_interpretation(
            variant_id,
            ref_n,
            cur_n,
            len(prepared["stream_values"]),
            resolved,
            run,
            alarm_state,
        ),
        warnings=warnings,
        metadata=metadata,
    )


def detect_ewma(
    data: pd.DataFrame,
    *,
    time_col: str = "time",
    value_col: str | None = "value",
    reference_window: tuple[str, str] | None = None,
    current_window: tuple[str, str] | None = None,
    params: dict[str, Any] | None = None,
) -> DriftResult:
    params = dict(params or {})
    variant_id = str(params.get("variant_id", "EWMA_UNIVARIATE_CONTROL_CHART")).upper()
    metadata: dict[str, Any] = {
        "params": params,
        "finite_replay_policy": "reference_and_current_windows_sorted_by_time",
    }

    if variant_id in DEFERRED_EWMA_VARIANTS:
        return _ewma_not_applicable(
            variant_id,
            "EWMA_BASELINE_REPLAY_THRESHOLD requires an approved empirical baseline replay calibration contract",
            metadata,
        )
    if variant_id not in SUPPORTED_EWMA_VARIANTS:
        return _ewma_not_applicable(variant_id, f"unsupported EWMA variant: {variant_id}", metadata)
    if any(params.get(key) is not None for key in ("feature_cols", "embedding_cols", "category_col", "count_col")):
        return _ewma_not_applicable(
            variant_id,
            "categorical, count, multivariate, and embedding EWMA inputs are not implemented yet",
            metadata,
        )
    if any(params.get(key) is not None for key in ("y_true", "y_pred", "label_col", "error_col")):
        return _ewma_not_applicable(
            variant_id,
            "supervised EWMA requires an explicit error stream contract",
            metadata,
        )
    try:
        resolved_pre = _resolve_ewma_params(params, variant_id)
        prepared = _prepare_adwin_stream(
            data,
            time_col=time_col,
            value_col=value_col,
            reference_window=reference_window,
            current_window=current_window,
            params=params,
            min_reference_size=resolved_pre["min_reference_size"],
            min_current_size=resolved_pre["min_current_size"],
        )
        resolved = _finalize_ewma_calibration(resolved_pre, params, prepared["reference_values"])
        if len(prepared["stream_values"]) < resolved["warmup_size"]:
            raise ValueError(
                f"effective stream length {len(prepared['stream_values'])} is below warmup_size {resolved['warmup_size']}"
            )
    except (KeyError, TypeError, ValueError) as exc:
        return _ewma_not_applicable(variant_id, str(exc), metadata)

    metadata.update(prepared["metadata"])
    metadata.update(
        {
            "backend": "numpy_ewma",
            "value_col": prepared["value_col"],
            "center_line": resolved["center_line"],
            "center_line_policy": resolved["center_line_policy"],
            "sigma": resolved["sigma"],
            "sigma_policy": resolved["sigma_policy"],
            "lambda": resolved["lambda_"],
            "control_width": resolved["control_width"],
            "control_width_policy": resolved["control_width_policy"],
            "ucl": resolved["ucl"],
            "lcl": resolved["lcl"],
            "direction": resolved["direction"],
            "warmup_size": resolved["warmup_size"],
            "check_every": resolved["check_every"],
            "reset_policy": resolved["reset_policy"],
        }
    )
    warnings = list(prepared["warnings"])
    if resolved["center_line_policy"] == "reference_mean":
        warnings.append("center_line was inferred from the effective reference window")
    if resolved["sigma_policy"] == "reference_std":
        warnings.append("sigma was inferred from the effective reference standard deviation")
    if resolved["reference_std"] == 0.0:
        warnings.append("reference standard deviation is zero; EWMA control limits may be narrow")
    if params.get("threshold_or_alpha") is not None:
        warnings.append("threshold_or_alpha was interpreted as EWMA control_width")
    if params.get("threshold") is not None:
        warnings.append("threshold was interpreted as the monitored EWMA one-sided control limit")
    if resolved["lambda_"] >= 0.8:
        warnings.append("EWMA lambda is high and may react to short-lived noise")
    if resolved["lambda_"] <= 0.05:
        warnings.append("EWMA lambda is low and may delay alarms")
    if resolved["check_every"] > 1:
        warnings.append("check_every > 1 checks EWMA alarms periodically and may delay detection")

    ref_n = len(prepared["reference_values"])
    cur_n = len(prepared["current_values"])
    imbalance_ratio = max(ref_n, cur_n) / min(ref_n, cur_n)
    if imbalance_ratio > resolved["sample_imbalance_warning_ratio"]:
        warnings.append(f"reference/current sample sizes are imbalanced (ratio={imbalance_ratio:.3g})")

    try:
        run = _run_ewma_stream(
            prepared["stream_values"],
            prepared["stream_times"],
            direction=resolved["direction"],
            center_line=resolved["center_line"],
            lambda_=resolved["lambda_"],
            ucl=resolved["ucl"],
            lcl=resolved["lcl"],
            warmup_size=resolved["warmup_size"],
            check_every=resolved["check_every"],
            record_events=resolved["record_events"],
            max_event_records=resolved["max_event_records"],
        )
    except (FloatingPointError, ValueError) as exc:
        return DriftResult(
            method_id=EWMA_METHOD_ID,
            method_name=EWMA_METHOD_NAME,
            method_category=EWMA_METHOD_CATEGORY,
            variant_id=variant_id,
            drift_detected=None,
            severity="error",
            warnings=warnings + [str(exc)],
            metadata=metadata,
            interpretation=f"EWMA calculation failed: {exc}",
        )

    if run["event_history_truncated"]:
        warnings.append("EWMA alarm event history was truncated by max_event_records")

    alarm_count = int(run["alarm_count"])
    drift_detected = alarm_count > 0
    severity = "drift_detected" if drift_detected else "normal"
    alarm_state = "drift_detected" if drift_detected else "normal"
    drift_score = _ewma_monitored_excess(resolved["direction"], run)
    summary = _numeric_summary_with_std(prepared["reference_values"], prepared["current_values"])
    threshold = _ewma_top_level_threshold(resolved)

    measurements: dict[str, Any] = {
        "EWMA_VALUE": run["final_ewma"],
        "CONTROL_LIMIT": {
            "ucl": resolved["ucl"],
            "lcl": resolved["lcl"],
            "mode": _ewma_limit_mode(resolved["direction"]),
        },
        "DRIFT_ALARM_STATE": alarm_state,
        "UCL": resolved["ucl"],
        "LCL": resolved["lcl"],
        "CENTER_LINE": resolved["center_line"],
        "SIGMA": resolved["sigma"],
        "LAMBDA": resolved["lambda_"],
        "CONTROL_WIDTH": resolved["control_width"],
        "DIRECTION": resolved["direction"],
        "RESET_POLICY": resolved["reset_policy"],
        "WARMUP_SIZE": resolved["warmup_size"],
        "CHECK_EVERY": resolved["check_every"],
        "ALARM_COUNT": alarm_count,
        "FIRST_ALARM_TIME": run["first_alarm_time"],
        "LAST_ALARM_TIME": run["last_alarm_time"],
        "FIRST_ALARM_INDEX": run["first_alarm_index"],
        "LAST_ALARM_INDEX": run["last_alarm_index"],
        "FIRST_ALARM_DIRECTION": run["first_alarm_direction"],
        "LAST_ALARM_DIRECTION": run["last_alarm_direction"],
        "PROCESSED_COUNT": len(prepared["stream_values"]),
        "SAMPLE_SIZE": {
            "reference": ref_n,
            "current": cur_n,
            "stream": len(prepared["stream_values"]),
            "dropped_reference": prepared["metadata"]["reference_original_count"] - ref_n,
            "dropped_current": prepared["metadata"]["current_original_count"] - cur_n,
        },
        "SAMPLE_SIZE_REFERENCE": ref_n,
        "SAMPLE_SIZE_CURRENT": cur_n,
        "MAX_EWMA_VALUE": run["max_ewma"],
        "MIN_EWMA_VALUE": run["min_ewma"],
        "MAX_UPPER_EXCESS": run["max_upper_excess"],
        "MAX_LOWER_EXCESS": run["max_lower_excess"],
        **summary,
    }
    if resolved["record_events"]:
        measurements["ALARM_EVENTS"] = run["events"]

    return DriftResult(
        method_id=EWMA_METHOD_ID,
        method_name=EWMA_METHOD_NAME,
        method_category=EWMA_METHOD_CATEGORY,
        variant_id=variant_id,
        drift_detected=drift_detected,
        severity=severity,
        drift_score=drift_score,
        p_value=None,
        test_statistic=run["final_ewma"],
        threshold=threshold,
        measurements=measurements,
        interpretation=_ewma_interpretation(
            variant_id,
            ref_n,
            cur_n,
            len(prepared["stream_values"]),
            resolved,
            run,
            alarm_state,
        ),
        warnings=warnings,
        metadata=metadata,
    )


def detect_geometric_moving_average(
    data: pd.DataFrame,
    *,
    time_col: str = "time",
    value_col: str | None = "value",
    reference_window: tuple[str, str] | None = None,
    current_window: tuple[str, str] | None = None,
    params: dict[str, Any] | None = None,
) -> DriftResult:
    params = dict(params or {})
    variant_id = str(params.get("variant_id", "GMA_CONTROL_CHART")).upper()
    metadata: dict[str, Any] = {
        "params": params,
        "finite_replay_policy": "reference_and_current_windows_sorted_by_time",
    }

    if variant_id in DEFERRED_GMA_VARIANTS:
        return _gma_not_applicable(
            variant_id,
            "GMA_WITH_EMPIRICAL_LIMIT requires an approved empirical baseline replay calibration contract",
            metadata,
        )
    if variant_id not in SUPPORTED_GMA_VARIANTS:
        return _gma_not_applicable(variant_id, f"unsupported GMA variant: {variant_id}", metadata)
    if any(params.get(key) is not None for key in ("feature_cols", "embedding_cols", "category_col", "count_col")):
        return _gma_not_applicable(
            variant_id,
            "categorical, count, multivariate, and embedding GMA inputs are not implemented yet",
            metadata,
        )
    if any(params.get(key) is not None for key in ("y_true", "y_pred", "label_col", "error_col")):
        return _gma_not_applicable(
            variant_id,
            "supervised GMA requires an explicit error stream contract",
            metadata,
        )
    try:
        resolved_pre = _resolve_gma_params(params, variant_id)
        prepared = _prepare_adwin_stream(
            data,
            time_col=time_col,
            value_col=value_col,
            reference_window=reference_window,
            current_window=current_window,
            params=params,
            min_reference_size=resolved_pre["min_reference_size"],
            min_current_size=resolved_pre["min_current_size"],
        )
        resolved = _finalize_ewma_calibration(resolved_pre, params, prepared["reference_values"])
        if len(prepared["stream_values"]) < resolved["warmup_size"]:
            raise ValueError(
                f"effective stream length {len(prepared['stream_values'])} is below warmup_size {resolved['warmup_size']}"
            )
    except (KeyError, TypeError, ValueError) as exc:
        return _gma_not_applicable(variant_id, str(exc), metadata)

    metadata.update(prepared["metadata"])
    metadata.update(
        {
            "backend": "numpy_gma",
            "value_col": prepared["value_col"],
            "center_line": resolved["center_line"],
            "center_line_policy": resolved["center_line_policy"],
            "sigma": resolved["sigma"],
            "sigma_policy": resolved["sigma_policy"],
            "lambda": resolved["lambda_"],
            "control_width": resolved["control_width"],
            "control_width_policy": resolved["control_width_policy"],
            "ucl": resolved["ucl"],
            "lcl": resolved["lcl"],
            "direction": resolved["direction"],
            "warmup_size": resolved["warmup_size"],
            "check_every": resolved["check_every"],
            "reset_policy": resolved["reset_policy"],
        }
    )
    warnings = list(prepared["warnings"])
    if resolved["center_line_policy"] == "reference_mean":
        warnings.append("center_line was inferred from the effective reference window")
    if resolved["sigma_policy"] == "reference_std":
        warnings.append("sigma was inferred from the effective reference standard deviation")
    if resolved["reference_std"] == 0.0:
        warnings.append("reference standard deviation is zero; GMA control limits may be narrow")
    if params.get("threshold_or_alpha") is not None:
        warnings.append("threshold_or_alpha was interpreted as GMA control_width")
    if params.get("threshold") is not None or params.get("control_limit") is not None:
        warnings.append("control limit alias was interpreted through GMA compatibility parameters")
    if resolved["lambda_"] >= 0.8:
        warnings.append("GMA lambda is high and may react to short-lived noise")
    if resolved["lambda_"] <= 0.05:
        warnings.append("GMA lambda is low and may delay alarms")
    if resolved["check_every"] > 1:
        warnings.append("check_every > 1 checks GMA alarms periodically and may delay detection")

    ref_n = len(prepared["reference_values"])
    cur_n = len(prepared["current_values"])
    imbalance_ratio = max(ref_n, cur_n) / min(ref_n, cur_n)
    if imbalance_ratio > resolved["sample_imbalance_warning_ratio"]:
        warnings.append(f"reference/current sample sizes are imbalanced (ratio={imbalance_ratio:.3g})")

    try:
        run = _run_ewma_stream(
            prepared["stream_values"],
            prepared["stream_times"],
            direction=resolved["direction"],
            center_line=resolved["center_line"],
            lambda_=resolved["lambda_"],
            ucl=resolved["ucl"],
            lcl=resolved["lcl"],
            warmup_size=resolved["warmup_size"],
            check_every=resolved["check_every"],
            record_events=resolved["record_events"],
            max_event_records=resolved["max_event_records"],
        )
    except (FloatingPointError, ValueError) as exc:
        return DriftResult(
            method_id=GMA_METHOD_ID,
            method_name=GMA_METHOD_NAME,
            method_category=GMA_METHOD_CATEGORY,
            variant_id=variant_id,
            drift_detected=None,
            severity="error",
            warnings=warnings + [str(exc)],
            metadata=metadata,
            interpretation=f"GMA calculation failed: {exc}",
        )

    if run["event_history_truncated"]:
        warnings.append("GMA alarm event history was truncated by max_event_records")

    alarm_count = int(run["alarm_count"])
    drift_detected = alarm_count > 0
    severity = "drift_detected" if drift_detected else "normal"
    alarm_state = "drift_detected" if drift_detected else "normal"
    drift_score = _ewma_monitored_excess(resolved["direction"], run)
    threshold = _ewma_top_level_threshold(resolved)
    summary = _numeric_summary_with_std(prepared["reference_values"], prepared["current_values"])

    measurements: dict[str, Any] = {
        "TEST_STATISTIC": run["final_ewma"],
        "P_VALUE": None,
        "DRIFT_ALARM_STATE": alarm_state,
        "GMA_STATISTIC": run["final_ewma"],
        "CONTROL_LIMIT": {
            "ucl": resolved["ucl"],
            "lcl": resolved["lcl"],
            "mode": _ewma_limit_mode(resolved["direction"]),
        },
        "UCL": resolved["ucl"],
        "LCL": resolved["lcl"],
        "CENTER_LINE": resolved["center_line"],
        "SIGMA": resolved["sigma"],
        "LAMBDA": resolved["lambda_"],
        "CONTROL_WIDTH": resolved["control_width"],
        "DIRECTION": resolved["direction"],
        "RESET_POLICY": resolved["reset_policy"],
        "WARMUP_SIZE": resolved["warmup_size"],
        "CHECK_EVERY": resolved["check_every"],
        "ALARM_COUNT": alarm_count,
        "FIRST_ALARM_TIME": run["first_alarm_time"],
        "LAST_ALARM_TIME": run["last_alarm_time"],
        "FIRST_ALARM_INDEX": run["first_alarm_index"],
        "LAST_ALARM_INDEX": run["last_alarm_index"],
        "FIRST_ALARM_DIRECTION": run["first_alarm_direction"],
        "LAST_ALARM_DIRECTION": run["last_alarm_direction"],
        "PROCESSED_COUNT": len(prepared["stream_values"]),
        "SAMPLE_SIZE": {
            "reference": ref_n,
            "current": cur_n,
            "stream": len(prepared["stream_values"]),
            "dropped_reference": prepared["metadata"]["reference_original_count"] - ref_n,
            "dropped_current": prepared["metadata"]["current_original_count"] - cur_n,
        },
        "SAMPLE_SIZE_REFERENCE": ref_n,
        "SAMPLE_SIZE_CURRENT": cur_n,
        "MAX_GMA_STATISTIC": run["max_ewma"],
        "MIN_GMA_STATISTIC": run["min_ewma"],
        "MAX_UPPER_EXCESS": run["max_upper_excess"],
        "MAX_LOWER_EXCESS": run["max_lower_excess"],
        **summary,
    }
    if resolved["record_events"]:
        measurements["ALARM_EVENTS"] = _gma_event_names(run["events"])

    return DriftResult(
        method_id=GMA_METHOD_ID,
        method_name=GMA_METHOD_NAME,
        method_category=GMA_METHOD_CATEGORY,
        variant_id=variant_id,
        drift_detected=drift_detected,
        severity=severity,
        drift_score=drift_score,
        p_value=None,
        test_statistic=run["final_ewma"],
        threshold=threshold,
        measurements=measurements,
        interpretation=_gma_interpretation(
            variant_id,
            ref_n,
            cur_n,
            len(prepared["stream_values"]),
            resolved,
            run,
            alarm_state,
        ),
        warnings=warnings,
        metadata=metadata,
    )


def detect_bocd(
    data: pd.DataFrame,
    *,
    time_col: str = "time",
    value_col: str | None = "value",
    reference_window: tuple[str, str] | None = None,
    current_window: tuple[str, str] | None = None,
    params: dict[str, Any] | None = None,
) -> DriftResult:
    params = dict(params or {})
    variant_id = str(params.get("variant_id", "BAYESIAN_ONLINE_CHANGE_POINT_GAUSSIAN")).upper()
    metadata: dict[str, Any] = {
        "params": params,
        "finite_replay_policy": "reference_and_current_windows_sorted_by_time",
    }

    if variant_id not in SUPPORTED_BOCD_VARIANTS:
        return _bocd_not_applicable(variant_id, f"unsupported BOCD variant: {variant_id}", metadata)
    if any(params.get(key) is not None for key in ("feature_cols", "embedding_cols", "category_col", "count_col")):
        return _bocd_not_applicable(
            variant_id,
            "categorical, count, multivariate, and embedding BOCD inputs are not implemented yet",
            metadata,
        )
    if any(params.get(key) is not None for key in ("y_true", "y_pred", "label_col", "error_col")):
        return _bocd_not_applicable(
            variant_id,
            "supervised BOCD requires an explicit error stream contract",
            metadata,
        )
    if params.get("likelihood_model") is not None and str(params["likelihood_model"]).lower() not in {
        "gaussian",
        "student_t_predictive",
    }:
        return _bocd_not_applicable(
            variant_id,
            "only gaussian/student_t_predictive likelihood_model is implemented for BOCD",
            metadata,
        )

    try:
        resolved = _resolve_bocd_params(params)
        prepared = _prepare_adwin_stream(
            data,
            time_col=time_col,
            value_col=value_col,
            reference_window=reference_window,
            current_window=current_window,
            params=params,
            min_reference_size=resolved["min_reference_size"],
            min_current_size=resolved["min_current_size"],
        )
        if len(prepared["stream_values"]) < resolved["min_stream_size"]:
            raise ValueError(
                f"effective stream length {len(prepared['stream_values'])} is below min_stream_size "
                f"{resolved['min_stream_size']}"
            )
        resolved = _finalize_bocd_prior(resolved, prepared["reference_values"])
    except (KeyError, TypeError, ValueError) as exc:
        return _bocd_not_applicable(variant_id, str(exc), metadata)

    metadata.update(prepared["metadata"])
    metadata.update(
        {
            "backend": "numpy_gaussian_conjugate_bocd",
            "value_col": prepared["value_col"],
            "likelihood_model": "student_t_predictive",
            "hazard_rate": resolved["hazard_rate"],
            "run_length_truncation": resolved["run_length_truncation"],
            "short_run_length": resolved["short_run_length"],
            "prior_mean": resolved["prior_mean"],
            "prior_kappa": resolved["prior_kappa"],
            "prior_alpha": resolved["prior_alpha"],
            "prior_beta": resolved["prior_beta"],
        }
    )
    warnings = list(prepared["warnings"])
    if resolved["hazard_rate_policy"] != "provided":
        warnings.append("hazard_rate was inferred from expected_run_length")
    if resolved["prior_policy"] == "reference_window":
        warnings.append("Gaussian BOCD prior was calibrated from the effective reference window")
    if params.get("threshold_or_alpha") is not None:
        warnings.append("threshold_or_alpha was interpreted as change_probability_threshold")
    if resolved["hazard_rate"] >= 0.2:
        warnings.append("high BOCD hazard_rate may increase false alarms")
    if resolved["hazard_rate"] <= 0.005:
        warnings.append("low BOCD hazard_rate may delay change point detection")

    ref_n = len(prepared["reference_values"])
    cur_n = len(prepared["current_values"])
    imbalance_ratio = max(ref_n, cur_n) / min(ref_n, cur_n)
    if imbalance_ratio > resolved["sample_imbalance_warning_ratio"]:
        warnings.append(f"reference/current sample sizes are imbalanced (ratio={imbalance_ratio:.3g})")

    try:
        run = _run_bocd_gaussian(
            prepared["stream_values"],
            prepared["stream_times"],
            hazard_rate=resolved["hazard_rate"],
            change_probability_threshold=resolved["change_probability_threshold"],
            predictive_probability_threshold=resolved["predictive_probability_threshold"],
            run_length_truncation=resolved["run_length_truncation"],
            short_run_length=resolved["short_run_length"],
            prior_mean=resolved["prior_mean"],
            prior_kappa=resolved["prior_kappa"],
            prior_alpha=resolved["prior_alpha"],
            prior_beta=resolved["prior_beta"],
            warmup_size=resolved["warmup_size"],
            check_every=resolved["check_every"],
            record_events=resolved["record_events"],
            max_event_records=resolved["max_event_records"],
        )
    except (FloatingPointError, ValueError) as exc:
        return DriftResult(
            method_id=BOCD_METHOD_ID,
            method_name=BOCD_METHOD_NAME,
            method_category=BOCD_METHOD_CATEGORY,
            variant_id=variant_id,
            drift_detected=None,
            severity="error",
            warnings=warnings + [str(exc)],
            metadata=metadata,
            interpretation=f"BOCD calculation failed: {exc}",
        )

    if run["event_history_truncated"]:
        warnings.append("BOCD alarm event history was truncated by max_event_records")

    alarm_count = int(run["alarm_count"])
    drift_detected = alarm_count > 0
    severity = "drift_detected" if drift_detected else "normal"
    alarm_state = "drift_detected" if drift_detected else "normal"
    summary = _numeric_summary_with_std(prepared["reference_values"], prepared["current_values"])

    test_statistic = float(run["max_change_probability"])
    p_value = None
    measurements: dict[str, Any] = {
        "TEST_STATISTIC": test_statistic,
        "P_VALUE": p_value,
        "DRIFT_ALARM_STATE": alarm_state,
        "CHANGE_POINT_PROBABILITY": run["last_change_probability"],
        "MAX_CHANGE_POINT_PROBABILITY": run["max_change_probability"],
        "MAX_CHANGE_POINT_TIME": run["max_change_probability_time"],
        "MAX_CHANGE_POINT_INDEX": run["max_change_probability_index"],
        "FINAL_RUN_LENGTH_MAP": run["final_run_length_map"],
        "FINAL_RUN_LENGTH_EXPECTED": run["final_run_length_expected"],
        "LAST_PREDICTIVE_PROBABILITY": run["last_predictive_probability"],
        "MIN_PREDICTIVE_PROBABILITY": run["min_predictive_probability"],
        "MIN_PREDICTIVE_PROBABILITY_TIME": run["min_predictive_probability_time"],
        "ALARM_COUNT": alarm_count,
        "FIRST_ALARM_TIME": run["first_alarm_time"],
        "LAST_ALARM_TIME": run["last_alarm_time"],
        "FIRST_ALARM_INDEX": run["first_alarm_index"],
        "LAST_ALARM_INDEX": run["last_alarm_index"],
        "FIRST_ALARM_TYPE": run["first_alarm_type"],
        "LAST_ALARM_TYPE": run["last_alarm_type"],
        "CHANGE_PROBABILITY_THRESHOLD": resolved["change_probability_threshold"],
        "PREDICTIVE_PROBABILITY_THRESHOLD": resolved["predictive_probability_threshold"],
        "HAZARD_RATE": resolved["hazard_rate"],
        "EXPECTED_RUN_LENGTH": resolved["expected_run_length"],
        "RUN_LENGTH_TRUNCATION": resolved["run_length_truncation"],
        "SHORT_RUN_LENGTH": resolved["short_run_length"],
        "PROCESSED_COUNT": len(prepared["stream_values"]),
        "SAMPLE_SIZE": {
            "reference": ref_n,
            "current": cur_n,
            "stream": len(prepared["stream_values"]),
            "dropped_reference": prepared["metadata"]["reference_original_count"] - ref_n,
            "dropped_current": prepared["metadata"]["current_original_count"] - cur_n,
        },
        "SAMPLE_SIZE_REFERENCE": ref_n,
        "SAMPLE_SIZE_CURRENT": cur_n,
        **summary,
    }
    if resolved["record_events"]:
        measurements["ALARM_EVENTS"] = run["events"]

    metadata.update(
        {
            "record_events": resolved["record_events"],
            "max_event_records": resolved["max_event_records"],
            "event_history_truncated": run["event_history_truncated"],
            "prior_policy": resolved["prior_policy"],
        }
    )

    return DriftResult(
        method_id=BOCD_METHOD_ID,
        method_name=BOCD_METHOD_NAME,
        method_category=BOCD_METHOD_CATEGORY,
        variant_id=variant_id,
        drift_detected=drift_detected,
        severity=severity,
        drift_score=test_statistic,
        p_value=p_value,
        test_statistic=test_statistic,
        threshold=resolved["change_probability_threshold"],
        measurements=measurements,
        interpretation=_bocd_interpretation(
            variant_id,
            ref_n,
            cur_n,
            len(prepared["stream_values"]),
            resolved,
            run,
            alarm_state,
        ),
        warnings=warnings,
        metadata=metadata,
    )


def detect_seqdrift(
    data: pd.DataFrame,
    *,
    time_col: str = "time",
    value_col: str | None = "value",
    reference_window: tuple[str, str] | None = None,
    current_window: tuple[str, str] | None = None,
    params: dict[str, Any] | None = None,
) -> DriftResult:
    params = dict(params or {})
    variant_id = str(params.get("variant_id", "SEQDRIFT1")).upper()
    metadata: dict[str, Any] = {
        "params": params,
        "finite_replay_policy": "reference_window_baseline_then_current_window_prefix_checks",
    }

    if variant_id not in SUPPORTED_SEQDRIFT_VARIANTS:
        return _seqdrift_not_applicable(variant_id, f"unsupported SeqDrift variant: {variant_id}", metadata)
    if any(params.get(key) is not None for key in ("feature_cols", "embedding_cols", "category_col", "count_col")):
        return _seqdrift_not_applicable(
            variant_id,
            "categorical, count, multivariate, and embedding SeqDrift inputs are not implemented yet",
            metadata,
        )
    if any(params.get(key) is not None for key in ("y_true", "y_pred", "label_col")):
        return _seqdrift_not_applicable(
            variant_id,
            "raw label/prediction SeqDrift requires an explicit error-stream contract",
            metadata,
        )

    try:
        resolved = _resolve_seqdrift_params(params, variant_id)
        prepared = _prepare_adwin_stream(
            data,
            time_col=time_col,
            value_col=value_col,
            reference_window=reference_window,
            current_window=current_window,
            params=params,
            min_reference_size=resolved["min_reference_size"],
            min_current_size=resolved["min_current_size"],
        )
        reference_values = _seqdrift_reference_values(
            prepared["reference_values"],
            variant_id=variant_id,
            reservoir_size=resolved["reservoir_size"],
            random_seed=resolved["random_seed"],
        )
    except (KeyError, TypeError, ValueError) as exc:
        return _seqdrift_not_applicable(variant_id, str(exc), metadata)

    metadata.update(prepared["metadata"])
    metadata.update(
        {
            "backend": "numpy_seqdrift_hoeffding_prefix_bound",
            "value_col": prepared["value_col"],
            "delta": resolved["delta"],
            "block_size": resolved["block_size"],
            "bound_type": resolved["bound_type"],
            "sampling_policy": resolved["sampling_policy"],
            "reservoir_size": resolved["reservoir_size"],
            "random_seed": resolved["random_seed"],
        }
    )
    warnings = list(prepared["warnings"])
    if params.get("threshold_or_alpha") is not None:
        warnings.append("threshold_or_alpha was interpreted as SeqDrift delta")
    if variant_id == "SEQDRIFT2":
        warnings.append("SEQDRIFT2 used deterministic reservoir sampling for the first implementation")
    if resolved["sampling_policy"] == "exact" and variant_id == "SEQDRIFT2":
        warnings.append("SEQDRIFT2 sampling_policy=exact disables reservoir downsampling")

    ref_n = len(prepared["reference_values"])
    cur_n = len(prepared["current_values"])
    imbalance_ratio = max(ref_n, cur_n) / min(ref_n, cur_n)
    if imbalance_ratio > resolved["sample_imbalance_warning_ratio"]:
        warnings.append(f"reference/current sample sizes are imbalanced (ratio={imbalance_ratio:.3g})")

    try:
        run = _run_seqdrift_stream(
            reference_values,
            prepared["current_values"],
            prepared["stream_times"][-cur_n:],
            delta=resolved["delta"],
            block_size=resolved["block_size"],
            value_min=resolved["value_min"],
            value_max=resolved["value_max"],
            record_events=resolved["record_events"],
            max_event_records=resolved["max_event_records"],
        )
    except (FloatingPointError, ValueError) as exc:
        return DriftResult(
            method_id=SEQDRIFT_METHOD_ID,
            method_name=SEQDRIFT_METHOD_NAME,
            method_category=SEQDRIFT_METHOD_CATEGORY,
            variant_id=variant_id,
            drift_detected=None,
            severity="error",
            warnings=warnings + [str(exc)],
            metadata=metadata,
            interpretation=f"SeqDrift calculation failed: {exc}",
        )

    if run["event_history_truncated"]:
        warnings.append("SeqDrift alarm event history was truncated by max_event_records")

    alarm_count = int(run["alarm_count"])
    drift_detected = alarm_count > 0
    severity = "drift_detected" if drift_detected else "normal"
    alarm_state = "drift_detected" if drift_detected else "normal"
    summary = _numeric_summary_with_std(prepared["reference_values"], prepared["current_values"])

    measurements: dict[str, Any] = {
        "DRIFT_ALARM_STATE": alarm_state,
        "SEQUENTIAL_BOUND": run["min_exceeded_bound"] if drift_detected else run["last_bound"],
        "METHOD_POLICY": {
            "variant": variant_id,
            "bound_type": resolved["bound_type"],
            "sampling_policy": resolved["sampling_policy"],
            "block_size": resolved["block_size"],
            "reservoir_size": resolved["reservoir_size"],
            "random_seed": resolved["random_seed"],
        },
        "TEST_STATISTIC": run["max_evidence"],
        "P_VALUE": None,
        "DRIFT_SCORE": run["max_margin"],
        "MAX_EVIDENCE": run["max_evidence"],
        "MAX_MARGIN": run["max_margin"],
        "LAST_EVIDENCE": run["last_evidence"],
        "LAST_BOUND": run["last_bound"],
        "REFERENCE_MEAN_EFFECTIVE": run["reference_mean"],
        "REFERENCE_SIZE_EFFECTIVE": len(reference_values),
        "VALUE_RANGE": run["value_range"],
        "DELTA": resolved["delta"],
        "ALARM_COUNT": alarm_count,
        "FIRST_ALARM_TIME": run["first_alarm_time"],
        "LAST_ALARM_TIME": run["last_alarm_time"],
        "FIRST_ALARM_INDEX": run["first_alarm_index"],
        "LAST_ALARM_INDEX": run["last_alarm_index"],
        "CHECK_COUNT": run["check_count"],
        "PROCESSED_COUNT": len(prepared["stream_values"]),
        "SAMPLE_SIZE": {
            "reference": ref_n,
            "current": cur_n,
            "effective_reference": len(reference_values),
            "stream": len(prepared["stream_values"]),
            "dropped_reference": prepared["metadata"]["reference_original_count"] - ref_n,
            "dropped_current": prepared["metadata"]["current_original_count"] - cur_n,
        },
        "SAMPLE_SIZE_REFERENCE": ref_n,
        "SAMPLE_SIZE_CURRENT": cur_n,
        **summary,
    }
    if resolved["record_events"]:
        measurements["ALARM_EVENTS"] = run["events"]

    return DriftResult(
        method_id=SEQDRIFT_METHOD_ID,
        method_name=SEQDRIFT_METHOD_NAME,
        method_category=SEQDRIFT_METHOD_CATEGORY,
        variant_id=variant_id,
        drift_detected=drift_detected,
        severity=severity,
        drift_score=run["max_margin"],
        p_value=None,
        test_statistic=run["max_evidence"],
        threshold=run["min_exceeded_bound"] if drift_detected else run["last_bound"],
        measurements=measurements,
        interpretation=_seqdrift_interpretation(
            variant_id,
            ref_n,
            cur_n,
            len(reference_values),
            resolved,
            run,
            alarm_state,
        ),
        warnings=warnings,
        metadata=metadata,
    )


def detect_sprt(
    data: pd.DataFrame,
    *,
    time_col: str = "time",
    value_col: str | None = "value",
    reference_window: tuple[str, str] | None = None,
    current_window: tuple[str, str] | None = None,
    params: dict[str, Any] | None = None,
) -> DriftResult:
    params = dict(params or {})
    variant_id = str(params.get("variant_id", "SPRT_BERNOULLI_ERROR_RATE")).upper()
    metadata: dict[str, Any] = {
        "params": params,
        "finite_replay_policy": "reference_and_current_windows_sorted_by_time",
    }

    if variant_id not in SUPPORTED_SPRT_VARIANTS:
        return _sprt_not_applicable(variant_id, f"unsupported SPRT variant: {variant_id}", metadata)
    if any(params.get(key) is not None for key in ("feature_cols", "embedding_cols", "category_col", "count_col")):
        return _sprt_not_applicable(
            variant_id,
            "categorical, count, multivariate, and embedding SPRT inputs are not implemented yet",
            metadata,
        )
    if any(params.get(key) is not None for key in ("y_true", "y_pred", "label_col")):
        return _sprt_not_applicable(
            variant_id,
            "raw labels/predictions require a precomputed Bernoulli error stream for SPRT",
            metadata,
        )

    try:
        resolved = _resolve_sprt_params(params, variant_id)
        sprt_value_col = params.get("error_col") if variant_id == "SPRT_BERNOULLI_ERROR_RATE" else value_col
        prepared = _prepare_adwin_stream(
            data,
            time_col=time_col,
            value_col=sprt_value_col,
            reference_window=reference_window,
            current_window=current_window,
            params=params,
            min_reference_size=resolved["min_reference_size"],
            min_current_size=resolved["min_current_size"],
        )
        if variant_id == "SPRT_BERNOULLI_ERROR_RATE":
            run = _run_sprt_bernoulli(
                prepared["current_values"],
                prepared["stream_times"][-len(prepared["current_values"]):],
                p0=resolved["p0"],
                p1=resolved["p1"],
                lower_boundary=resolved["lower_boundary"],
                upper_boundary=resolved["upper_boundary"],
                check_every=resolved["check_every"],
                reset_policy=resolved["reset_policy"],
                record_events=resolved["record_events"],
                max_event_records=resolved["max_event_records"],
            )
        else:
            if resolved["sigma"] is None:
                reference_std = float(np.std(prepared["reference_values"], ddof=1))
                if reference_std <= 0 or not np.isfinite(reference_std):
                    raise ValueError("reference standard deviation must be positive for Gaussian SPRT")
                resolved["sigma"] = reference_std
            run = _run_sprt_gaussian(
                prepared["current_values"],
                prepared["stream_times"][-len(prepared["current_values"]):],
                mu0=resolved["mu0"],
                mu1=resolved["mu1"],
                sigma=resolved["sigma"],
                lower_boundary=resolved["lower_boundary"],
                upper_boundary=resolved["upper_boundary"],
                check_every=resolved["check_every"],
                reset_policy=resolved["reset_policy"],
                record_events=resolved["record_events"],
                max_event_records=resolved["max_event_records"],
            )
    except (KeyError, TypeError, ValueError) as exc:
        return _sprt_not_applicable(variant_id, str(exc), metadata)

    metadata.update(prepared["metadata"])
    metadata.update(
        {
            "backend": "numpy_finite_replay_sprt",
            "value_col": prepared["value_col"],
            "alpha": resolved["alpha"],
            "beta": resolved["beta"],
            "lower_boundary": resolved["lower_boundary"],
            "upper_boundary": resolved["upper_boundary"],
            "check_every": resolved["check_every"],
            "reset_policy": resolved["reset_policy"],
        }
    )
    warnings = list(prepared["warnings"])
    if params.get("threshold_or_alpha") is not None:
        warnings.append("threshold_or_alpha was interpreted as SPRT alpha")
    if params.get("error_col") is not None and variant_id == "SPRT_BERNOULLI_ERROR_RATE":
        warnings.append("error_col was used as the Bernoulli SPRT input stream")
    if resolved["check_every"] > 1:
        warnings.append("check_every > 1 checks SPRT boundaries periodically and may delay decisions")
    if run["event_history_truncated"]:
        warnings.append("SPRT decision event history was truncated by max_event_records")

    ref_n = len(prepared["reference_values"])
    cur_n = len(prepared["current_values"])
    decision_state = run["decision_state"]
    drift_detected = int(run["h1_decision_count"]) > 0
    severity = "drift_detected" if drift_detected else "normal"
    if decision_state == "continue":
        severity = "watch"
    alarm_state = "drift_detected" if drift_detected else ("normal" if decision_state == "accept_h0" else "undetermined")
    summary = _numeric_summary_with_std(prepared["reference_values"], prepared["current_values"])

    measurements: dict[str, Any] = {
        "DRIFT_ALARM_STATE": alarm_state,
        "HYPOTHESIS_DECISION_STATE": decision_state,
        "LOG_LIKELIHOOD_RATIO": run["final_log_likelihood_ratio"],
        "TEST_STATISTIC": run["final_log_likelihood_ratio"],
        "P_VALUE": None,
        "CONTROL_LIMIT": {"lower": resolved["lower_boundary"], "upper": resolved["upper_boundary"]},
        "SEQUENTIAL_BOUND": {"lower": resolved["lower_boundary"], "upper": resolved["upper_boundary"]},
        "ALPHA": resolved["alpha"],
        "BETA": resolved["beta"],
        "LOWER_BOUNDARY": resolved["lower_boundary"],
        "UPPER_BOUNDARY": resolved["upper_boundary"],
        "DECISION_COUNT": run["decision_count"],
        "ALARM_COUNT": run["h1_decision_count"],
        "FIRST_DECISION_TIME": run["first_decision_time"],
        "LAST_DECISION_TIME": run["last_decision_time"],
        "FIRST_ALARM_TIME": run["first_h1_time"],
        "LAST_ALARM_TIME": run["last_h1_time"],
        "FIRST_ALARM_INDEX": run["first_h1_index"],
        "LAST_ALARM_INDEX": run["last_h1_index"],
        "CHECK_COUNT": run["check_count"],
        "PROCESSED_COUNT": len(prepared["stream_values"]),
        "CURRENT_PROCESSED_COUNT": cur_n,
        "SAMPLE_SIZE": {
            "reference": ref_n,
            "current": cur_n,
            "stream": len(prepared["stream_values"]),
            "dropped_reference": prepared["metadata"]["reference_original_count"] - ref_n,
            "dropped_current": prepared["metadata"]["current_original_count"] - cur_n,
        },
        "SAMPLE_SIZE_REFERENCE": ref_n,
        "SAMPLE_SIZE_CURRENT": cur_n,
        **summary,
    }
    if variant_id == "SPRT_BERNOULLI_ERROR_RATE":
        measurements.update({"P0": resolved["p0"], "P1": resolved["p1"]})
    else:
        measurements.update({"MU0": resolved["mu0"], "MU1": resolved["mu1"], "SIGMA": resolved["sigma"]})
    if resolved["record_events"]:
        measurements["DECISION_EVENTS"] = run["events"]

    return DriftResult(
        method_id=SPRT_METHOD_ID,
        method_name=SPRT_METHOD_NAME,
        method_category=SPRT_METHOD_CATEGORY,
        variant_id=variant_id,
        drift_detected=drift_detected,
        severity=severity,
        drift_score=run["final_log_likelihood_ratio"],
        p_value=None,
        test_statistic=run["final_log_likelihood_ratio"],
        threshold=resolved["upper_boundary"],
        measurements=measurements,
        interpretation=_sprt_interpretation(variant_id, ref_n, cur_n, resolved, run, alarm_state),
        warnings=warnings,
        metadata=metadata,
    )


# @managed-contract contract_id=drift_algorithm.streaming._resolve_adwin_params level=P1
def _resolve_adwin_params(params: dict[str, Any]) -> dict[str, Any]:
    delta = params.get("delta", None)
    alias_delta = params.get("threshold_or_alpha", None)
    if delta is None and alias_delta is None:
        delta_value = 0.002
    elif delta is None:
        delta_value = _as_float(alias_delta, "threshold_or_alpha")
    elif alias_delta is None:
        delta_value = _as_float(delta, "delta")
    else:
        delta_value = _as_float(delta, "delta")
        alias_value = _as_float(alias_delta, "threshold_or_alpha")
        if not np.isclose(delta_value, alias_value):
            raise ValueError("delta and threshold_or_alpha must not conflict")
    if not 0.0 < delta_value < 1.0:
        raise ValueError("delta must satisfy 0 < delta < 1")

    resolved = {
        "delta": delta_value,
        "clock": _as_positive_int(params.get("clock", 1), "clock"),
        "max_buckets": _as_positive_int(params.get("max_buckets", 5), "max_buckets"),
        "min_window_length": _as_positive_int(params.get("min_window_length", 5), "min_window_length"),
        "grace_period": _as_positive_int(params.get("grace_period", 20), "grace_period"),
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
    nan_policy = str(params.get("nan_policy", "drop")).lower()
    if nan_policy not in {"drop", "omit"}:
        raise ValueError("nan_policy must be 'drop' or 'omit'")
    return resolved


def _resolve_kswin_params(params: dict[str, Any]) -> dict[str, Any]:
    alpha = params.get("alpha", None)
    alias_alpha = params.get("threshold_or_alpha", None)
    if alpha is None and alias_alpha is None:
        alpha_value = 0.005
    elif alpha is None:
        alpha_value = _as_float(alias_alpha, "threshold_or_alpha")
    elif alias_alpha is None:
        alpha_value = _as_float(alpha, "alpha")
    else:
        alpha_value = _as_float(alpha, "alpha")
        alias_value = _as_float(alias_alpha, "threshold_or_alpha")
        if not np.isclose(alpha_value, alias_value):
            raise ValueError("alpha and threshold_or_alpha must not conflict")
    if not 0.0 < alpha_value < 1.0:
        raise ValueError("alpha must satisfy 0 < alpha < 1")

    window_value = params.get("window_size", None)
    data_points = params.get("data_points", None)
    if window_value is None and data_points is None:
        window_size = 100
    elif window_value is None:
        window_size = _as_positive_int(data_points, "data_points")
    elif data_points is None:
        window_size = _as_positive_int(window_value, "window_size")
    else:
        window_size = _as_positive_int(window_value, "window_size")
        data_points_value = _as_positive_int(data_points, "data_points")
        if window_size != data_points_value:
            raise ValueError("window_size and data_points must not conflict")

    resolved = {
        "alpha": alpha_value,
        "window_size": window_size,
        "stat_size": _as_positive_int(params.get("stat_size", 30), "stat_size"),
        "check_every": _as_positive_int(params.get("check_every", 1), "check_every"),
        "min_reference_size": _as_positive_int(params.get("min_reference_size", 20), "min_reference_size"),
        "min_current_size": _as_positive_int(params.get("min_current_size", 20), "min_current_size"),
        "record_events": _as_bool(params.get("record_events", True), "record_events"),
        "max_event_records": _as_positive_int(params.get("max_event_records", 50), "max_event_records"),
        "sample_imbalance_warning_ratio": _as_float(
            params.get("sample_imbalance_warning_ratio", 10.0),
            "sample_imbalance_warning_ratio",
        ),
        "tie_policy": str(params.get("tie_policy", "warn_only")).lower(),
    }
    subsample_size = params.get("subsample_size", params.get("sample_size"))
    resolved["subsample_size"] = None if subsample_size is None else _as_positive_int(subsample_size, "subsample_size")
    if resolved["sample_imbalance_warning_ratio"] < 1.0:
        raise ValueError("sample_imbalance_warning_ratio must be >= 1")
    if resolved["stat_size"] >= resolved["window_size"]:
        raise ValueError("stat_size must be smaller than window_size")
    if resolved["stat_size"] < 2 or resolved["window_size"] - resolved["stat_size"] < 2:
        raise ValueError("reference and statistic subwindows must both contain at least 2 rows")
    if resolved["tie_policy"] != "warn_only":
        raise ValueError("tie_policy must be 'warn_only'")
    nan_policy = str(params.get("nan_policy", "drop")).lower()
    if nan_policy not in {"drop", "omit"}:
        raise ValueError("nan_policy must be 'drop' or 'omit'")
    return resolved


def _resolve_page_hinkley_params(params: dict[str, Any], variant_id: str) -> dict[str, Any]:
    threshold = params.get("threshold", None)
    alias_threshold = params.get("threshold_or_alpha", None)
    if threshold is None and alias_threshold is None:
        threshold_value = 50.0
    elif threshold is None:
        threshold_value = _as_float(alias_threshold, "threshold_or_alpha")
    elif alias_threshold is None:
        threshold_value = _as_float(threshold, "threshold")
    else:
        threshold_value = _as_float(threshold, "threshold")
        alias_value = _as_float(alias_threshold, "threshold_or_alpha")
        if not np.isclose(threshold_value, alias_value):
            raise ValueError("threshold and threshold_or_alpha must not conflict")
    if threshold_value <= 0.0:
        raise ValueError("threshold must be positive")

    direction = "increase" if variant_id == "PAGE_HINKLEY_INCREASE" else "decrease"
    explicit_direction = params.get("direction")
    if explicit_direction is not None:
        explicit_direction = str(explicit_direction).lower()
        if explicit_direction not in {"increase", "decrease"}:
            raise ValueError("direction must be 'increase' or 'decrease'")
        if explicit_direction != direction:
            raise ValueError("direction must not conflict with variant_id")

    delta = _as_float(params.get("delta", 0.005), "delta")
    if delta < 0.0:
        raise ValueError("delta must be >= 0")
    alpha = params.get("alpha", None)
    alpha_value = None if alpha is None else _as_float(alpha, "alpha")
    if alpha_value is not None and not 0.0 < alpha_value < 1.0:
        raise ValueError("alpha must satisfy 0 < alpha < 1 when supplied")

    reset_policy = str(params.get("reset_policy", "after_alarm")).lower()
    if reset_policy not in {"after_alarm", "none"}:
        raise ValueError("reset_policy must be 'after_alarm' or 'none'")
    nan_policy = str(params.get("nan_policy", "drop")).lower()
    if nan_policy not in {"drop", "omit"}:
        raise ValueError("nan_policy must be 'drop' or 'omit'")

    resolved = {
        "threshold": threshold_value,
        "delta": delta,
        "alpha": alpha_value,
        "direction": direction,
        "reset_policy": reset_policy,
        "min_instances": _as_positive_int(params.get("min_instances", 30), "min_instances"),
        "check_every": _as_positive_int(params.get("check_every", 1), "check_every"),
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


def _resolve_cusum_params(params: dict[str, Any], variant_id: str) -> dict[str, Any]:
    direction = {
        "ONE_SIDED_UPPER_CUSUM": "increase",
        "ONE_SIDED_LOWER_CUSUM": "decrease",
        "TWO_SIDED_CUSUM": "both",
        "CUSUM_ON_DISTANCE_STREAM": "increase",
    }[variant_id]
    for key in ("direction", "direction_or_alternative"):
        if params.get(key) is not None:
            explicit = _normalize_cusum_direction(params[key])
            if explicit != direction:
                raise ValueError(f"{key} must not conflict with variant_id")

    threshold_values = [
        params.get("decision_threshold_h"),
        params.get("threshold"),
        params.get("threshold_or_alpha"),
    ]
    supplied_thresholds = [_as_float(value, "decision_threshold_h") for value in threshold_values if value is not None]
    decision_threshold_h = None
    if supplied_thresholds:
        first = supplied_thresholds[0]
        if any(not np.isclose(first, value) for value in supplied_thresholds[1:]):
            raise ValueError("decision_threshold_h, threshold, and threshold_or_alpha must not conflict")
        if first <= 0.0:
            raise ValueError("decision_threshold_h must be positive")
        decision_threshold_h = first

    target_mean = None if params.get("target_mean") is None else _as_float(params["target_mean"], "target_mean")
    allowance_k = None if params.get("allowance_k") is None else _as_float(params["allowance_k"], "allowance_k")
    if allowance_k is not None and allowance_k < 0.0:
        raise ValueError("allowance_k must be >= 0")
    reset_policy = str(params.get("reset_policy", "after_alarm")).lower()
    if reset_policy not in {"after_alarm", "none"}:
        raise ValueError("reset_policy must be 'after_alarm' or 'none'")
    nan_policy = str(params.get("nan_policy", "drop")).lower()
    if nan_policy not in {"drop", "omit"}:
        raise ValueError("nan_policy must be 'drop' or 'omit'")

    resolved = {
        "direction": direction,
        "target_mean": target_mean,
        "target_mean_policy": "provided" if target_mean is not None else "reference_mean",
        "allowance_k": allowance_k,
        "allowance_k_policy": "provided" if allowance_k is not None else "reference_std",
        "decision_threshold_h": decision_threshold_h,
        "decision_threshold_h_policy": "provided" if decision_threshold_h is not None else "reference_std",
        "reset_policy": reset_policy,
        "warmup_size": _as_positive_int(params.get("warmup_size", 30), "warmup_size"),
        "check_every": _as_positive_int(params.get("check_every", 1), "check_every"),
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


def _resolve_ewma_params(params: dict[str, Any], variant_id: str) -> dict[str, Any]:
    direction = "both" if variant_id == "EWMA_UNIVARIATE_CONTROL_CHART" else "increase"
    explicit_direction = params.get("direction", params.get("direction_or_alternative"))
    if explicit_direction is not None:
        direction = _normalize_cusum_direction(explicit_direction)
    if variant_id == "EWMA_UNIVARIATE_CONTROL_CHART" and direction != "both":
        raise ValueError("direction must be both for EWMA_UNIVARIATE_CONTROL_CHART")
    if variant_id == "EWMA_ONE_SIDED" and direction not in {"increase", "decrease"}:
        raise ValueError("direction must be increase or decrease for EWMA_ONE_SIDED")

    lambda_value = _as_float(params.get("lambda", params.get("lambda_", 0.2)), "lambda")
    if not 0.0 < lambda_value <= 1.0:
        raise ValueError("lambda must satisfy 0 < lambda <= 1")
    center_line = None if params.get("center_line") is None else _as_float(params["center_line"], "center_line")
    sigma = None if params.get("sigma") is None else _as_float(params["sigma"], "sigma")
    if sigma is not None and sigma < 0.0:
        raise ValueError("sigma must be >= 0")
    control_width = params.get("control_width")
    if control_width is None and params.get("threshold_or_alpha") is not None and all(
        params.get(key) is None for key in ("ucl", "lcl", "threshold")
    ):
        control_width = params["threshold_or_alpha"]
    control_width_value = _as_float(3.0 if control_width is None else control_width, "control_width")
    if control_width_value <= 0.0:
        raise ValueError("control_width must be positive")
    ucl = None if params.get("ucl") is None else _as_float(params["ucl"], "ucl")
    lcl = None if params.get("lcl") is None else _as_float(params["lcl"], "lcl")
    threshold = None if params.get("threshold") is None else _as_float(params["threshold"], "threshold")
    if threshold is not None:
        if variant_id not in {"EWMA_ONE_SIDED", "EWMA_BASELINE_REPLAY_THRESHOLD"}:
            raise ValueError("threshold is only valid for one-sided EWMA variants")
        if direction == "increase":
            if ucl is not None and not np.isclose(ucl, threshold):
                raise ValueError("threshold and ucl must not conflict")
            ucl = threshold
        else:
            if lcl is not None and not np.isclose(lcl, threshold):
                raise ValueError("threshold and lcl must not conflict")
            lcl = threshold
    if ucl is not None and lcl is not None and lcl >= ucl:
        raise ValueError("lcl must be smaller than ucl")
    reset_policy = str(params.get("reset_policy", "none")).lower()
    if reset_policy != "none":
        raise ValueError("reset_policy must be 'none' for the first EWMA implementation")
    nan_policy = str(params.get("nan_policy", "drop")).lower()
    if nan_policy not in {"drop", "omit"}:
        raise ValueError("nan_policy must be 'drop' or 'omit'")

    resolved = {
        "lambda_": lambda_value,
        "center_line": center_line,
        "center_line_policy": "provided" if center_line is not None else "reference_mean",
        "sigma": sigma,
        "sigma_policy": "provided" if sigma is not None else "reference_std",
        "control_width": control_width_value,
        "control_width_policy": "provided" if control_width is not None else "default",
        "ucl": ucl,
        "lcl": lcl,
        "direction": direction,
        "reset_policy": reset_policy,
        "warmup_size": _as_positive_int(params.get("warmup_size", 20), "warmup_size"),
        "check_every": _as_positive_int(params.get("check_every", 1), "check_every"),
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


def _resolve_gma_params(params: dict[str, Any], variant_id: str) -> dict[str, Any]:
    gma_params = dict(params)
    gma_params["variant_id"] = (
        "EWMA_UNIVARIATE_CONTROL_CHART" if variant_id == "GMA_CONTROL_CHART" else "EWMA_ONE_SIDED"
    )
    control_limit = gma_params.get("control_limit")
    if control_limit is not None:
        if isinstance(control_limit, dict):
            if variant_id != "GMA_CONTROL_CHART":
                raise ValueError("dict control_limit is only valid for GMA_CONTROL_CHART")
            if "ucl" in control_limit:
                if gma_params.get("ucl") is not None and not np.isclose(
                    _as_float(gma_params["ucl"], "ucl"),
                    _as_float(control_limit["ucl"], "control_limit['ucl']"),
                ):
                    raise ValueError("control_limit['ucl'] and ucl must not conflict")
                gma_params["ucl"] = control_limit["ucl"]
            if "lcl" in control_limit:
                if gma_params.get("lcl") is not None and not np.isclose(
                    _as_float(gma_params["lcl"], "lcl"),
                    _as_float(control_limit["lcl"], "control_limit['lcl']"),
                ):
                    raise ValueError("control_limit['lcl'] and lcl must not conflict")
                gma_params["lcl"] = control_limit["lcl"]
        else:
            if variant_id not in {"GMA_ONE_SIDED", "GMA_WITH_EMPIRICAL_LIMIT"}:
                raise ValueError("scalar control_limit is ambiguous for two-sided GMA variants")
            if gma_params.get("threshold") is not None and not np.isclose(
                _as_float(gma_params["threshold"], "threshold"),
                _as_float(control_limit, "control_limit"),
            ):
                raise ValueError("control_limit and threshold must not conflict")
            gma_params["threshold"] = control_limit
    return _resolve_ewma_params(gma_params, gma_params["variant_id"])


def _resolve_bocd_params(params: dict[str, Any]) -> dict[str, Any]:
    threshold = params.get("change_probability_threshold", params.get("threshold"))
    alias_threshold = params.get("threshold_or_alpha")
    if threshold is None and alias_threshold is None:
        threshold_value = 0.5
    elif threshold is None:
        threshold_value = _as_float(alias_threshold, "threshold_or_alpha")
    elif alias_threshold is None:
        threshold_value = _as_float(threshold, "change_probability_threshold")
    else:
        threshold_value = _as_float(threshold, "change_probability_threshold")
        alias_value = _as_float(alias_threshold, "threshold_or_alpha")
        if not np.isclose(threshold_value, alias_value):
            raise ValueError("change_probability_threshold and threshold_or_alpha must not conflict")
    if not 0.0 < threshold_value < 1.0:
        raise ValueError("change_probability_threshold must satisfy 0 < threshold < 1")

    hazard_rate = params.get("hazard_rate", None)
    expected_run_length = params.get("expected_run_length", params.get("hazard_function", 100))
    if hazard_rate is None:
        expected_value = _as_float(expected_run_length, "expected_run_length")
        if expected_value <= 1.0:
            raise ValueError("expected_run_length must be > 1")
        hazard_value = 1.0 / expected_value
        hazard_policy = "expected_run_length"
    else:
        hazard_value = _as_float(hazard_rate, "hazard_rate")
        hazard_policy = "provided"
        if params.get("expected_run_length") is not None and not np.isclose(
            hazard_value, 1.0 / _as_float(params["expected_run_length"], "expected_run_length")
        ):
            raise ValueError("hazard_rate and expected_run_length must not conflict")
    if not 0.0 < hazard_value < 1.0:
        raise ValueError("hazard_rate must satisfy 0 < hazard_rate < 1")

    predictive_threshold = params.get("predictive_probability_threshold", None)
    predictive_threshold_value = None
    if predictive_threshold is not None:
        predictive_threshold_value = _as_float(predictive_threshold, "predictive_probability_threshold")
        if predictive_threshold_value <= 0.0:
            raise ValueError("predictive_probability_threshold must be positive")

    prior_mean = None if params.get("prior_mean") is None else _as_float(params["prior_mean"], "prior_mean")
    prior_kappa = _as_float(params.get("prior_kappa", 1.0), "prior_kappa")
    prior_alpha = _as_float(params.get("prior_alpha", 2.0), "prior_alpha")
    prior_beta = None if params.get("prior_beta") is None else _as_float(params["prior_beta"], "prior_beta")
    if prior_kappa <= 0.0:
        raise ValueError("prior_kappa must be positive")
    if prior_alpha <= 1.0:
        raise ValueError("prior_alpha must be > 1")
    if prior_beta is not None and prior_beta <= 0.0:
        raise ValueError("prior_beta must be positive")

    resolved = {
        "change_probability_threshold": threshold_value,
        "hazard_rate": hazard_value,
        "hazard_rate_policy": hazard_policy,
        "expected_run_length": 1.0 / hazard_value,
        "predictive_probability_threshold": predictive_threshold_value,
        "prior_mean": prior_mean,
        "prior_kappa": prior_kappa,
        "prior_alpha": prior_alpha,
        "prior_beta": prior_beta,
        "prior_policy": "provided" if prior_mean is not None and prior_beta is not None else "reference_window",
        "run_length_truncation": _as_positive_int(
            params.get("run_length_truncation", 200),
            "run_length_truncation",
        ),
        "short_run_length": _as_positive_int(params.get("short_run_length", 5), "short_run_length"),
        "warmup_size": _as_positive_int(params.get("warmup_size", 20), "warmup_size"),
        "check_every": _as_positive_int(params.get("check_every", 1), "check_every"),
        "min_reference_size": _as_positive_int(params.get("min_reference_size", 20), "min_reference_size"),
        "min_current_size": _as_positive_int(params.get("min_current_size", 20), "min_current_size"),
        "min_stream_size": _as_positive_int(params.get("min_stream_size", 40), "min_stream_size"),
        "record_events": _as_bool(params.get("record_events", True), "record_events"),
        "max_event_records": _as_positive_int(params.get("max_event_records", 50), "max_event_records"),
        "sample_imbalance_warning_ratio": _as_float(
            params.get("sample_imbalance_warning_ratio", 10.0),
            "sample_imbalance_warning_ratio",
        ),
    }
    if resolved["sample_imbalance_warning_ratio"] < 1.0:
        raise ValueError("sample_imbalance_warning_ratio must be >= 1")
    if resolved["run_length_truncation"] < 2:
        raise ValueError("run_length_truncation must be >= 2")
    if resolved["short_run_length"] >= resolved["run_length_truncation"]:
        raise ValueError("short_run_length must be smaller than run_length_truncation")
    nan_policy = str(params.get("nan_policy", "drop")).lower()
    if nan_policy not in {"drop", "omit"}:
        raise ValueError("nan_policy must be 'drop' or 'omit'")
    return resolved


def _resolve_seqdrift_params(params: dict[str, Any], variant_id: str) -> dict[str, Any]:
    delta = params.get("delta", None)
    alias_delta = params.get("threshold_or_alpha", None)
    if delta is None and alias_delta is None:
        delta_value = 0.01
    elif delta is None:
        delta_value = _as_float(alias_delta, "threshold_or_alpha")
    elif alias_delta is None:
        delta_value = _as_float(delta, "delta")
    else:
        delta_value = _as_float(delta, "delta")
        alias_value = _as_float(alias_delta, "threshold_or_alpha")
        if not np.isclose(delta_value, alias_value):
            raise ValueError("delta and threshold_or_alpha must not conflict")
    if not 0.0 < delta_value < 1.0:
        raise ValueError("delta must satisfy 0 < delta < 1")

    bound_type = str(params.get("bound_type", "hoeffding")).lower()
    if bound_type not in {"hoeffding", "sequential_hoeffding"}:
        raise ValueError("bound_type must be 'hoeffding' or 'sequential_hoeffding'")
    default_sampling_policy = "exact" if variant_id == "SEQDRIFT1" else "reservoir"
    sampling_policy = str(params.get("sampling_policy", default_sampling_policy)).lower()
    if sampling_policy not in {"exact", "reservoir"}:
        raise ValueError("sampling_policy must be 'exact' or 'reservoir'")
    if variant_id == "SEQDRIFT1" and sampling_policy != "exact":
        raise ValueError("SEQDRIFT1 first implementation requires sampling_policy='exact'")

    value_min = None if params.get("value_min") is None else _as_float(params["value_min"], "value_min")
    value_max = None if params.get("value_max") is None else _as_float(params["value_max"], "value_max")
    if value_min is not None and value_max is not None and value_min >= value_max:
        raise ValueError("value_min must be smaller than value_max")

    random_seed = params.get("random_seed", 0)
    if random_seed is not None:
        random_seed = _as_nonnegative_int(random_seed, "random_seed")

    resolved = {
        "delta": delta_value,
        "block_size": _as_positive_int(params.get("block_size", 20), "block_size"),
        "reservoir_size": _as_positive_int(params.get("reservoir_size", 100), "reservoir_size"),
        "sampling_policy": sampling_policy,
        "bound_type": bound_type,
        "random_seed": random_seed,
        "value_min": value_min,
        "value_max": value_max,
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
    if resolved["block_size"] > resolved["min_current_size"]:
        raise ValueError("block_size must be <= min_current_size")
    nan_policy = str(params.get("nan_policy", "drop")).lower()
    if nan_policy not in {"drop", "omit"}:
        raise ValueError("nan_policy must be 'drop' or 'omit'")
    return resolved


def _resolve_sprt_params(params: dict[str, Any], variant_id: str) -> dict[str, Any]:
    alpha = _as_float(params.get("alpha", params.get("threshold_or_alpha", 0.05)), "alpha")
    beta = _as_float(params.get("beta", 0.1), "beta")
    if not 0.0 < alpha < 1.0:
        raise ValueError("alpha must satisfy 0 < alpha < 1")
    if not 0.0 < beta < 1.0:
        raise ValueError("beta must satisfy 0 < beta < 1")
    if params.get("alpha") is not None and params.get("threshold_or_alpha") is not None:
        alias_alpha = _as_float(params["threshold_or_alpha"], "threshold_or_alpha")
        if not np.isclose(alpha, alias_alpha):
            raise ValueError("alpha and threshold_or_alpha must not conflict")

    upper_boundary = _as_float(params.get("upper_boundary", np.log((1.0 - beta) / alpha)), "upper_boundary")
    lower_boundary = _as_float(params.get("lower_boundary", np.log(beta / (1.0 - alpha))), "lower_boundary")
    if lower_boundary >= upper_boundary:
        raise ValueError("lower_boundary must be less than upper_boundary")
    reset_policy = str(params.get("reset_policy", "stop_after_decision"))
    if reset_policy not in {"stop_after_decision", "continue"}:
        raise ValueError("reset_policy must be 'stop_after_decision' or 'continue'")
    resolved: dict[str, Any] = {
        "alpha": alpha,
        "beta": beta,
        "upper_boundary": upper_boundary,
        "lower_boundary": lower_boundary,
        "check_every": _as_positive_int(params.get("check_every", 1), "check_every"),
        "reset_policy": reset_policy,
        "min_reference_size": _as_positive_int(params.get("min_reference_size", 20), "min_reference_size"),
        "min_current_size": _as_positive_int(params.get("min_current_size", 20), "min_current_size"),
        "record_events": _as_bool(params.get("record_events", True), "record_events"),
        "max_event_records": _as_positive_int(params.get("max_event_records", 50), "max_event_records"),
    }
    if variant_id == "SPRT_BERNOULLI_ERROR_RATE":
        p0 = _as_float(params.get("p0", params.get("null_error_rate", 0.1)), "p0")
        p1 = _as_float(params.get("p1", params.get("alternative_error_rate", 0.2)), "p1")
        if not 0.0 < p0 < 1.0 or not 0.0 < p1 < 1.0:
            raise ValueError("p0 and p1 must satisfy 0 < p < 1")
        if p1 <= p0:
            raise ValueError("SPRT_BERNOULLI_ERROR_RATE requires p1 > p0")
        resolved.update({"p0": p0, "p1": p1})
    else:
        mu0 = _as_float(params.get("mu0", params.get("null_mean", 0.0)), "mu0")
        if params.get("mu1") is not None or params.get("alternative_mean") is not None:
            mu1 = _as_float(params.get("mu1", params.get("alternative_mean")), "mu1")
        else:
            shift = _as_float(params.get("mean_shift", 1.0), "mean_shift")
            if np.isclose(shift, 0.0):
                raise ValueError("mean_shift must be nonzero")
            mu1 = mu0 + shift
        sigma = None if params.get("sigma", params.get("std")) is None else _as_float(params.get("sigma", params.get("std")), "sigma")
        if sigma is not None and sigma <= 0.0:
            raise ValueError("sigma must be positive")
        if np.isclose(mu0, mu1):
            raise ValueError("mu0 and mu1 must differ")
        resolved.update({"mu0": mu0, "mu1": mu1, "sigma": sigma})
    return resolved


def _finalize_cusum_calibration(
    resolved: dict[str, Any],
    params: dict[str, Any],
    reference_values: np.ndarray,
) -> dict[str, Any]:
    del params
    reference_std = float(np.std(reference_values, ddof=1)) if len(reference_values) > 1 else 0.0
    scale = reference_std if reference_std > 0.0 else 1.0
    finalized = dict(resolved)
    finalized["reference_std"] = reference_std
    if finalized["target_mean"] is None:
        finalized["target_mean"] = float(np.mean(reference_values))
    if finalized["allowance_k"] is None:
        finalized["allowance_k"] = 0.5 * scale
    if finalized["decision_threshold_h"] is None:
        finalized["decision_threshold_h"] = 5.0 * scale
    if not np.isfinite(finalized["target_mean"]):
        raise ValueError("target_mean must be finite")
    if not np.isfinite(finalized["allowance_k"]) or finalized["allowance_k"] < 0.0:
        raise ValueError("allowance_k must be finite and >= 0")
    if not np.isfinite(finalized["decision_threshold_h"]) or finalized["decision_threshold_h"] <= 0.0:
        raise ValueError("decision_threshold_h must be finite and > 0")
    return finalized


def _finalize_ewma_calibration(
    resolved: dict[str, Any],
    params: dict[str, Any],
    reference_values: np.ndarray,
) -> dict[str, Any]:
    del params
    reference_std = float(np.std(reference_values, ddof=1)) if len(reference_values) > 1 else 0.0
    finalized = dict(resolved)
    finalized["reference_std"] = reference_std
    if finalized["center_line"] is None:
        finalized["center_line"] = float(np.mean(reference_values))
    if finalized["sigma"] is None:
        finalized["sigma"] = reference_std
    if not np.isfinite(finalized["center_line"]):
        raise ValueError("center_line must be finite")
    if not np.isfinite(finalized["sigma"]) or finalized["sigma"] < 0.0:
        raise ValueError("sigma must be finite and >= 0")
    steady_sigma = finalized["sigma"] * float(np.sqrt(finalized["lambda_"] / (2.0 - finalized["lambda_"])))
    if finalized["ucl"] is None:
        finalized["ucl"] = finalized["center_line"] + finalized["control_width"] * steady_sigma
    if finalized["lcl"] is None:
        finalized["lcl"] = finalized["center_line"] - finalized["control_width"] * steady_sigma
    if finalized["direction"] == "increase":
        finalized["lcl"] = None
    elif finalized["direction"] == "decrease":
        finalized["ucl"] = None
    if finalized["direction"] == "both" and finalized["lcl"] >= finalized["ucl"]:
        raise ValueError("resolved lcl must be smaller than resolved ucl")
    for key in ("ucl", "lcl"):
        if finalized[key] is not None and not np.isfinite(finalized[key]):
            raise ValueError(f"{key} must be finite")
    return finalized


def _finalize_bocd_prior(resolved: dict[str, Any], reference_values: np.ndarray) -> dict[str, Any]:
    finalized = dict(resolved)
    reference_mean = float(np.mean(reference_values))
    reference_std = float(np.std(reference_values, ddof=1)) if len(reference_values) > 1 else 0.0
    reference_var = reference_std**2 if reference_std > 0.0 else 1.0
    if finalized["prior_mean"] is None:
        finalized["prior_mean"] = reference_mean
    if finalized["prior_beta"] is None:
        finalized["prior_beta"] = reference_var * (finalized["prior_alpha"] - 1.0)
    if not np.isfinite(finalized["prior_mean"]):
        raise ValueError("prior_mean must be finite")
    if not np.isfinite(finalized["prior_beta"]) or finalized["prior_beta"] <= 0.0:
        raise ValueError("prior_beta must be positive and finite")
    finalized["reference_std"] = reference_std
    return finalized


def _prepare_adwin_stream(
    data: pd.DataFrame,
    *,
    time_col: str,
    value_col: str | None,
    reference_window: tuple[str, str] | None,
    current_window: tuple[str, str] | None,
    params: dict[str, Any],
    min_reference_size: int,
    min_current_size: int,
) -> dict[str, Any]:
    if reference_window is None or current_window is None:
        raise ValueError("reference_window and current_window are required")
    if time_col not in data.columns:
        raise KeyError(f"missing time column: {time_col}")
    resolved_value_col = value_col
    if resolved_value_col is None:
        resolved_value_col = params.get("input_signal")
    if not resolved_value_col:
        raise ValueError("value_col or params['input_signal'] is required")
    if resolved_value_col not in data.columns:
        raise KeyError(f"missing value column: {resolved_value_col}")
    if pd.api.types.is_bool_dtype(data[resolved_value_col]):
        raise TypeError("boolean value column is not valid ADWIN numeric-stream input")
    if data[resolved_value_col].map(lambda value: isinstance(value, (list, tuple, dict, np.ndarray))).any():
        raise TypeError("array-like, object, or embedding values are not valid ADWIN numeric-stream input")

    ref_start, ref_end = _parse_window(reference_window, "reference_window")
    cur_start, cur_end = _parse_window(current_window, "current_window")
    if max(ref_start, cur_start) <= min(ref_end, cur_end):
        raise ValueError("reference_window and current_window must not overlap")

    frame = data[[time_col, resolved_value_col]].copy()
    original_rows = len(frame)
    frame[time_col] = pd.to_datetime(frame[time_col], errors="coerce")
    raw_reference_mask = (frame[time_col] >= ref_start) & (frame[time_col] <= ref_end)
    raw_current_mask = (frame[time_col] >= cur_start) & (frame[time_col] <= cur_end)
    reference_original_count = int(raw_reference_mask.sum())
    current_original_count = int(raw_current_mask.sum())
    invalid_time_rows = int(frame[time_col].isna().sum())
    frame[resolved_value_col] = pd.to_numeric(frame[resolved_value_col], errors="coerce")
    values = frame[resolved_value_col].to_numpy(dtype=float, na_value=np.nan)
    invalid_value_rows = int((~np.isfinite(values)).sum())
    frame = frame.dropna(subset=[time_col, resolved_value_col])
    frame = frame[np.isfinite(frame[resolved_value_col].to_numpy(dtype=float))]
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
    stream_values = stream_frame[resolved_value_col].to_numpy(dtype=float)
    stream_times = stream_frame[time_col].to_numpy(dtype="datetime64[ns]")
    if stream_values.size == 0 or not np.all(np.isfinite(stream_values)):
        raise ValueError("ADWIN stream has no finite numeric values")

    warnings: list[str] = []
    if invalid_time_rows:
        warnings.append(f"dropped {invalid_time_rows} rows with invalid timestamps")
    if invalid_value_rows:
        warnings.append(f"dropped {invalid_value_rows} rows with non-finite numeric values")
    if np.unique(stream_values).size < stream_values.size:
        warnings.append("stream contains many repeated or tied values")

    return {
        "reference_values": reference_frame[resolved_value_col].to_numpy(dtype=float),
        "current_values": current_frame[resolved_value_col].to_numpy(dtype=float),
        "stream_values": stream_values,
        "stream_times": stream_times,
        "value_col": resolved_value_col,
        "warnings": warnings,
        "metadata": {
            "original_rows": original_rows,
            "valid_rows": int(len(frame)),
            "invalid_time_rows": invalid_time_rows,
            "invalid_value_rows": invalid_value_rows,
            "reference_window": [ref_start.isoformat(), ref_end.isoformat()],
            "current_window": [cur_start.isoformat(), cur_end.isoformat()],
            "reference_original_count": reference_original_count,
            "current_original_count": current_original_count,
            "reference_effective_count": int(len(reference_frame)),
            "current_effective_count": int(len(current_frame)),
        },
    }


# @managed-contract contract_id=drift_algorithm.streaming._apply_kswin_subsampling level=P1
def _apply_kswin_subsampling(
    prepared: dict[str, Any],
    resolved: dict[str, Any],
    params: dict[str, Any],
) -> dict[str, Any]:
    stream_values = prepared["stream_values"]
    stream_times = prepared["stream_times"]
    target = resolved.get("subsample_size")
    if target is None:
        target = min(len(stream_values), max(resolved["window_size"], 100))
    target = int(target)
    if target < resolved["window_size"]:
        raise ValueError("subsample_size must be >= window_size for KSWIN_WITH_SUBSAMPLING")
    if target >= len(stream_values):
        prepared["metadata"].update(
            {
                "sampling_policy": "deterministic_even_index_noop",
                "subsample_size": int(len(stream_values)),
                "subsample_original_size": int(len(stream_values)),
                "sampling_seed": params.get("sampling_seed"),
            }
        )
        prepared["sampling_warnings"] = []
        return prepared

    indices = np.linspace(0, len(stream_values) - 1, target, dtype=int)
    unique_indices = np.unique(indices)
    if len(unique_indices) < target:
        missing = target - len(unique_indices)
        available = np.setdiff1d(np.arange(len(stream_values)), unique_indices, assume_unique=False)
        unique_indices = np.sort(np.concatenate([unique_indices, available[:missing]]))
    sampled = dict(prepared)
    sampled["stream_values"] = stream_values[unique_indices]
    sampled["stream_times"] = stream_times[unique_indices]
    sampled["metadata"] = dict(prepared["metadata"])
    sampled["metadata"].update(
        {
            "sampling_policy": "deterministic_even_index",
            "subsample_size": int(len(unique_indices)),
            "subsample_original_size": int(len(stream_values)),
            "sampling_seed": params.get("sampling_seed"),
        }
    )
    sampled["sampling_warnings"] = [
        f"KSWIN_WITH_SUBSAMPLING used deterministic even-index sampling: {len(stream_values)} -> {len(unique_indices)}"
    ]
    return sampled


# @managed-contract contract_id=drift_algorithm.streaming._run_adwin_mean_stream level=P1
def _run_adwin_mean_stream(
    values: np.ndarray,
    times: np.ndarray,
    *,
    delta: float,
    clock: int,
    max_buckets: int,
    min_window_length: int,
    grace_period: int,
    record_events: bool,
    max_event_records: int,
) -> dict[str, Any]:
    del max_buckets
    window: list[float] = []
    events: list[dict[str, Any]] = []
    event_history_truncated = False
    alarm_count = 0
    first_alarm_time = None
    last_alarm_time = None
    first_alarm_index = None
    last_alarm_index = None

    for index, value in enumerate(values):
        window.append(float(value))
        if len(window) < max(grace_period, min_window_length * 2):
            continue
        if (index + 1) % clock != 0:
            continue

        while len(window) >= min_window_length * 2:
            cut = _find_adwin_cut(window, delta=delta, min_window_length=min_window_length)
            if cut is None:
                break
            cut_index, epsilon, mean_old, mean_recent = cut
            width_before = len(window)
            window = window[cut_index:]
            width_after = len(window)
            alarm_count += 1
            alarm_time = _iso_time(times[index])
            if first_alarm_time is None:
                first_alarm_time = alarm_time
                first_alarm_index = index
            last_alarm_time = alarm_time
            last_alarm_index = index
            if record_events:
                if len(events) < max_event_records:
                    events.append(
                        {
                            "time": alarm_time,
                            "index": int(index),
                            "width_before": int(width_before),
                            "width_after": int(width_after),
                            "mean_before_cut": float(mean_old),
                            "mean_after_cut": float(mean_recent),
                            "cut_epsilon": float(epsilon),
                        }
                    )
                else:
                    event_history_truncated = True

    final = np.asarray(window, dtype=float)
    if final.size == 0 or not np.all(np.isfinite(final)):
        raise ValueError("ADWIN final window statistics are not finite")
    return {
        "alarm_count": alarm_count,
        "events": events,
        "event_history_truncated": event_history_truncated,
        "first_alarm_time": first_alarm_time,
        "last_alarm_time": last_alarm_time,
        "first_alarm_index": first_alarm_index,
        "last_alarm_index": last_alarm_index,
        "window_size": int(final.size),
        "final_window_mean": float(np.mean(final)),
        "final_window_variance": float(np.var(final, ddof=1)) if final.size > 1 else None,
        "final_window_min": float(np.min(final)),
        "final_window_max": float(np.max(final)),
    }


def _run_kswin_stream(
    values: np.ndarray,
    times: np.ndarray,
    *,
    alpha: float,
    window_size: int,
    stat_size: int,
    check_every: int,
    record_events: bool,
    max_event_records: int,
) -> dict[str, Any]:
    events: list[dict[str, Any]] = []
    event_history_truncated = False
    alarm_count = 0
    check_count = 0
    first_alarm_time = None
    last_alarm_time = None
    first_alarm_index = None
    last_alarm_index = None
    last_statistic = None
    last_p_value = None
    last_check_time = None
    min_alarm_p_value = None
    max_alarm_statistic = None
    reference_size = window_size - stat_size

    for index in range(window_size - 1, len(values)):
        if (index + 1 - window_size) % check_every != 0:
            continue
        window = values[index + 1 - window_size : index + 1]
        reference = window[:reference_size]
        recent = window[reference_size:]
        result = ks_2samp(reference, recent, alternative="two-sided", method="auto")
        statistic = float(result.statistic)
        p_value = float(result.pvalue)
        if not np.isfinite(statistic) or not np.isfinite(p_value) or not 0.0 <= p_value <= 1.0:
            raise ValueError("KSWIN produced a non-finite KS statistic or invalid p-value")
        check_count += 1
        last_statistic = statistic
        last_p_value = p_value
        last_check_time = _iso_time(times[index])
        if p_value < alpha:
            alarm_count += 1
            alarm_time = _iso_time(times[index])
            if first_alarm_time is None:
                first_alarm_time = alarm_time
                first_alarm_index = index
            last_alarm_time = alarm_time
            last_alarm_index = index
            min_alarm_p_value = p_value if min_alarm_p_value is None else min(min_alarm_p_value, p_value)
            max_alarm_statistic = statistic if max_alarm_statistic is None else max(max_alarm_statistic, statistic)
            if record_events:
                if len(events) < max_event_records:
                    events.append(
                        {
                            "time": alarm_time,
                            "index": int(index),
                            "ks_statistic": statistic,
                            "p_value": p_value,
                            "window_start_time": _iso_time(times[index + 1 - window_size]),
                            "reference_subwindow_size": int(reference_size),
                            "stat_size": int(stat_size),
                        }
                    )
                else:
                    event_history_truncated = True

    if check_count == 0:
        raise ValueError("KSWIN did not perform any KS checks")
    return {
        "alarm_count": alarm_count,
        "events": events,
        "event_history_truncated": event_history_truncated,
        "first_alarm_time": first_alarm_time,
        "last_alarm_time": last_alarm_time,
        "first_alarm_index": first_alarm_index,
        "last_alarm_index": last_alarm_index,
        "check_count": check_count,
        "last_statistic": last_statistic,
        "last_p_value": last_p_value,
        "last_check_time": last_check_time,
        "min_alarm_p_value": min_alarm_p_value,
        "max_alarm_statistic": max_alarm_statistic,
    }


def _run_page_hinkley_stream(
    values: np.ndarray,
    times: np.ndarray,
    *,
    direction: str,
    threshold: float,
    delta: float,
    min_instances: int,
    check_every: int,
    reset_policy: str,
    record_events: bool,
    max_event_records: int,
) -> dict[str, Any]:
    sign = 1.0 if direction == "increase" else -1.0
    count = 0
    running_mean = 0.0
    cumulative = 0.0
    min_cumulative = 0.0
    statistic = 0.0
    max_statistic = 0.0
    alarm_count = 0
    first_alarm_time = None
    last_alarm_time = None
    first_alarm_index = None
    last_alarm_index = None
    events: list[dict[str, Any]] = []
    event_history_truncated = False

    for index, raw_value in enumerate(values):
        directional_value = float(raw_value) * sign
        count += 1
        running_mean += (directional_value - running_mean) / count
        cumulative += directional_value - running_mean - delta
        min_cumulative = min(min_cumulative, cumulative)
        statistic = cumulative - min_cumulative
        max_statistic = max(max_statistic, statistic)
        if not np.all(np.isfinite([running_mean, cumulative, min_cumulative, statistic])):
            raise ValueError("Page-Hinkley produced a non-finite running state")

        if count < min_instances:
            continue
        if (count - min_instances) % check_every != 0:
            continue
        if statistic > threshold:
            alarm_count += 1
            alarm_time = _iso_time(times[index])
            if first_alarm_time is None:
                first_alarm_time = alarm_time
                first_alarm_index = index
            last_alarm_time = alarm_time
            last_alarm_index = index
            if record_events:
                if len(events) < max_event_records:
                    events.append(
                        {
                            "time": alarm_time,
                            "index": int(index),
                            "page_hinkley_statistic": float(statistic),
                            "threshold": float(threshold),
                            "running_mean": float(running_mean),
                            "cumulative_deviation": float(cumulative),
                            "direction": direction,
                        }
                    )
                else:
                    event_history_truncated = True
            if reset_policy == "after_alarm":
                cumulative = 0.0
                min_cumulative = 0.0
                statistic = 0.0

    return {
        "alarm_count": alarm_count,
        "events": events,
        "event_history_truncated": event_history_truncated,
        "first_alarm_time": first_alarm_time,
        "last_alarm_time": last_alarm_time,
        "first_alarm_index": first_alarm_index,
        "last_alarm_index": last_alarm_index,
        "final_statistic": float(statistic),
        "max_statistic": float(max_statistic),
        "final_running_mean": float(running_mean),
        "final_cumulative": float(cumulative),
        "final_min_cumulative": float(min_cumulative),
    }


def _run_cusum_stream(
    values: np.ndarray,
    times: np.ndarray,
    *,
    variant_id: str,
    direction: str,
    target_mean: float,
    allowance_k: float,
    decision_threshold_h: float,
    warmup_size: int,
    check_every: int,
    reset_policy: str,
    record_events: bool,
    max_event_records: int,
) -> dict[str, Any]:
    del variant_id
    monitor_upper = direction in {"increase", "both"}
    monitor_lower = direction in {"decrease", "both"}
    positive = 0.0
    negative = 0.0
    max_positive = 0.0
    max_negative = 0.0
    alarm_count = 0
    first_alarm_time = None
    last_alarm_time = None
    first_alarm_index = None
    last_alarm_index = None
    first_alarm_direction = None
    last_alarm_direction = None
    events: list[dict[str, Any]] = []
    event_history_truncated = False

    for index, value in enumerate(values):
        value = float(value)
        positive = max(0.0, positive + value - target_mean - allowance_k)
        negative = max(0.0, negative + target_mean - value - allowance_k)
        max_positive = max(max_positive, positive)
        max_negative = max(max_negative, negative)
        if not np.all(np.isfinite([positive, negative, max_positive, max_negative])):
            raise ValueError("CUSUM produced a non-finite running state")

        count = index + 1
        if count < warmup_size:
            continue
        if (count - warmup_size) % check_every != 0:
            continue

        alarm_directions: list[str] = []
        if monitor_upper and positive > decision_threshold_h:
            alarm_directions.append("upper")
        if monitor_lower and negative > decision_threshold_h:
            alarm_directions.append("lower")
        for alarm_direction in alarm_directions:
            alarm_count += 1
            alarm_time = _iso_time(times[index])
            if first_alarm_time is None:
                first_alarm_time = alarm_time
                first_alarm_index = index
                first_alarm_direction = alarm_direction
            last_alarm_time = alarm_time
            last_alarm_index = index
            last_alarm_direction = alarm_direction
            if record_events:
                if len(events) < max_event_records:
                    events.append(
                        {
                            "time": alarm_time,
                            "index": int(index),
                            "direction": alarm_direction,
                            "cusum_statistic": float(positive if alarm_direction == "upper" else negative),
                            "positive_cusum": float(positive),
                            "negative_cusum": float(negative),
                            "target_mean": float(target_mean),
                            "allowance_k": float(allowance_k),
                            "decision_threshold_h": float(decision_threshold_h),
                        }
                    )
                else:
                    event_history_truncated = True
            if reset_policy == "after_alarm":
                if alarm_direction == "upper":
                    positive = 0.0
                else:
                    negative = 0.0

    return {
        "alarm_count": alarm_count,
        "events": events,
        "event_history_truncated": event_history_truncated,
        "first_alarm_time": first_alarm_time,
        "last_alarm_time": last_alarm_time,
        "first_alarm_index": first_alarm_index,
        "last_alarm_index": last_alarm_index,
        "first_alarm_direction": first_alarm_direction,
        "last_alarm_direction": last_alarm_direction,
        "final_positive": float(positive),
        "final_negative": float(negative),
        "max_positive": float(max_positive),
        "max_negative": float(max_negative),
    }


def _run_ewma_stream(
    values: np.ndarray,
    times: np.ndarray,
    *,
    direction: str,
    center_line: float,
    lambda_: float,
    ucl: float | None,
    lcl: float | None,
    warmup_size: int,
    check_every: int,
    record_events: bool,
    max_event_records: int,
) -> dict[str, Any]:
    ewma = float(center_line)
    max_ewma = ewma
    min_ewma = ewma
    max_upper_excess = None if ucl is None else 0.0
    max_lower_excess = None if lcl is None else 0.0
    alarm_count = 0
    first_alarm_time = None
    last_alarm_time = None
    first_alarm_index = None
    last_alarm_index = None
    first_alarm_direction = None
    last_alarm_direction = None
    events: list[dict[str, Any]] = []
    event_history_truncated = False

    for index, value in enumerate(values):
        value = float(value)
        ewma = lambda_ * value + (1.0 - lambda_) * ewma
        max_ewma = max(max_ewma, ewma)
        min_ewma = min(min_ewma, ewma)
        if ucl is not None:
            max_upper_excess = max(float(max_upper_excess), ewma - ucl)
        if lcl is not None:
            max_lower_excess = max(float(max_lower_excess), lcl - ewma)
        if not np.isfinite(ewma):
            raise ValueError("EWMA produced a non-finite running state")

        count = index + 1
        if count < warmup_size:
            continue
        if (count - warmup_size) % check_every != 0:
            continue
        alarm_directions: list[str] = []
        if direction in {"increase", "both"} and ucl is not None and ewma > ucl:
            alarm_directions.append("upper")
        if direction in {"decrease", "both"} and lcl is not None and ewma < lcl:
            alarm_directions.append("lower")
        for alarm_direction in alarm_directions:
            alarm_count += 1
            alarm_time = _iso_time(times[index])
            if first_alarm_time is None:
                first_alarm_time = alarm_time
                first_alarm_index = index
                first_alarm_direction = alarm_direction
            last_alarm_time = alarm_time
            last_alarm_index = index
            last_alarm_direction = alarm_direction
            limit = ucl if alarm_direction == "upper" else lcl
            if record_events:
                if len(events) < max_event_records:
                    events.append(
                        {
                            "time": alarm_time,
                            "index": int(index),
                            "direction": alarm_direction,
                            "ewma_value": float(ewma),
                            "control_limit": float(limit),
                            "center_line": float(center_line),
                            "lambda": float(lambda_),
                            "raw_value": value,
                        }
                    )
                else:
                    event_history_truncated = True

    return {
        "alarm_count": alarm_count,
        "events": events,
        "event_history_truncated": event_history_truncated,
        "first_alarm_time": first_alarm_time,
        "last_alarm_time": last_alarm_time,
        "first_alarm_index": first_alarm_index,
        "last_alarm_index": last_alarm_index,
        "first_alarm_direction": first_alarm_direction,
        "last_alarm_direction": last_alarm_direction,
        "final_ewma": float(ewma),
        "max_ewma": float(max_ewma),
        "min_ewma": float(min_ewma),
        "max_upper_excess": None if max_upper_excess is None else float(max_upper_excess),
        "max_lower_excess": None if max_lower_excess is None else float(max_lower_excess),
    }


def _run_bocd_gaussian(
    values: np.ndarray,
    times: np.ndarray,
    *,
    hazard_rate: float,
    change_probability_threshold: float,
    predictive_probability_threshold: float | None,
    run_length_truncation: int,
    short_run_length: int,
    prior_mean: float,
    prior_kappa: float,
    prior_alpha: float,
    prior_beta: float,
    warmup_size: int,
    check_every: int,
    record_events: bool,
    max_event_records: int,
) -> dict[str, Any]:
    log_run_probs = np.array([0.0], dtype=float)
    mus = np.array([prior_mean], dtype=float)
    kappas = np.array([prior_kappa], dtype=float)
    alphas = np.array([prior_alpha], dtype=float)
    betas = np.array([prior_beta], dtype=float)

    alarm_count = 0
    first_alarm_time = None
    last_alarm_time = None
    first_alarm_index = None
    last_alarm_index = None
    first_alarm_type = None
    last_alarm_type = None
    events: list[dict[str, Any]] = []
    event_history_truncated = False

    last_change_probability = 0.0
    max_change_probability = 0.0
    max_change_probability_index = None
    max_change_probability_time = None
    last_predictive_probability = None
    min_predictive_probability = None
    min_predictive_probability_index = None
    min_predictive_probability_time = None

    for index, raw_value in enumerate(values):
        value = float(raw_value)
        if not np.isfinite(value):
            raise ValueError("BOCD received a non-finite value")

        log_predictive = _student_t_logpdf(value, mus, kappas, alphas, betas)
        log_growth = log_run_probs + log_predictive + np.log1p(-hazard_rate)
        log_cp = _logsumexp(log_run_probs + log_predictive + np.log(hazard_rate))
        next_log_probs = np.concatenate(([log_cp], log_growth))
        next_log_probs -= _logsumexp(next_log_probs)
        run_probs = np.exp(next_log_probs)

        predictive_probability = float(np.exp(_logsumexp(log_run_probs + log_predictive)))
        short_run_end = min(short_run_length + 1, len(run_probs))
        change_probability = float(np.sum(run_probs[:short_run_end]))
        last_change_probability = change_probability
        last_predictive_probability = predictive_probability
        if change_probability > max_change_probability:
            max_change_probability = change_probability
            max_change_probability_index = index
            max_change_probability_time = _iso_time(times[index])
        if min_predictive_probability is None or predictive_probability < min_predictive_probability:
            min_predictive_probability = predictive_probability
            min_predictive_probability_index = index
            min_predictive_probability_time = _iso_time(times[index])

        count = index + 1
        alarm_types: list[str] = []
        if count >= warmup_size and (count - warmup_size) % check_every == 0:
            if change_probability > change_probability_threshold:
                alarm_types.append("change_probability")
            if (
                predictive_probability_threshold is not None
                and predictive_probability < predictive_probability_threshold
            ):
                alarm_types.append("low_predictive_probability")
        for alarm_type in alarm_types:
            alarm_count += 1
            alarm_time = _iso_time(times[index])
            if first_alarm_time is None:
                first_alarm_time = alarm_time
                first_alarm_index = index
                first_alarm_type = alarm_type
            last_alarm_time = alarm_time
            last_alarm_index = index
            last_alarm_type = alarm_type
            if record_events:
                if len(events) < max_event_records:
                    events.append(
                        {
                            "time": alarm_time,
                            "index": int(index),
                            "alarm_type": alarm_type,
                            "change_probability": change_probability,
                            "predictive_probability": predictive_probability,
                            "run_length_map": int(np.argmax(run_probs)),
                        }
                    )
                else:
                    event_history_truncated = True

        growth_mus, growth_kappas, growth_alphas, growth_betas = _update_normal_inverse_gamma(
            value,
            mus,
            kappas,
            alphas,
            betas,
        )
        mus = np.concatenate(([prior_mean], growth_mus))
        kappas = np.concatenate(([prior_kappa], growth_kappas))
        alphas = np.concatenate(([prior_alpha], growth_alphas))
        betas = np.concatenate(([prior_beta], growth_betas))
        log_run_probs = next_log_probs

        if len(log_run_probs) > run_length_truncation:
            keep = np.r_[0, np.arange(len(log_run_probs) - (run_length_truncation - 1), len(log_run_probs))]
            log_run_probs = log_run_probs[keep]
            mus = mus[keep]
            kappas = kappas[keep]
            alphas = alphas[keep]
            betas = betas[keep]
            log_run_probs -= _logsumexp(log_run_probs)

        if not np.all(np.isfinite(log_run_probs)):
            raise ValueError("BOCD posterior produced non-finite probabilities")

    final_probs = np.exp(log_run_probs)
    run_lengths = np.arange(len(final_probs), dtype=float)
    return {
        "alarm_count": alarm_count,
        "events": events,
        "event_history_truncated": event_history_truncated,
        "first_alarm_time": first_alarm_time,
        "last_alarm_time": last_alarm_time,
        "first_alarm_index": first_alarm_index,
        "last_alarm_index": last_alarm_index,
        "first_alarm_type": first_alarm_type,
        "last_alarm_type": last_alarm_type,
        "last_change_probability": last_change_probability,
        "max_change_probability": max_change_probability,
        "max_change_probability_index": max_change_probability_index,
        "max_change_probability_time": max_change_probability_time,
        "final_run_length_map": int(np.argmax(final_probs)),
        "final_run_length_expected": float(np.sum(run_lengths * final_probs)),
        "last_predictive_probability": last_predictive_probability,
        "min_predictive_probability": min_predictive_probability,
        "min_predictive_probability_index": min_predictive_probability_index,
        "min_predictive_probability_time": min_predictive_probability_time,
    }


def _seqdrift_reference_values(
    reference_values: np.ndarray,
    *,
    variant_id: str,
    reservoir_size: int,
    random_seed: int | None,
) -> np.ndarray:
    if variant_id == "SEQDRIFT1" or len(reference_values) <= reservoir_size:
        return np.asarray(reference_values, dtype=float)
    rng = np.random.default_rng(random_seed)
    indices = rng.choice(len(reference_values), size=reservoir_size, replace=False)
    indices.sort()
    return np.asarray(reference_values[indices], dtype=float)


def _run_seqdrift_stream(
    reference_values: np.ndarray,
    current_values: np.ndarray,
    current_times: np.ndarray,
    *,
    delta: float,
    block_size: int,
    value_min: float | None,
    value_max: float | None,
    record_events: bool,
    max_event_records: int,
) -> dict[str, Any]:
    if len(reference_values) == 0 or len(current_values) == 0:
        raise ValueError("SeqDrift requires non-empty reference and current values")
    data_min = float(np.min(np.concatenate([reference_values, current_values]))) if value_min is None else value_min
    data_max = float(np.max(np.concatenate([reference_values, current_values]))) if value_max is None else value_max
    if data_min >= data_max:
        raise ValueError("SeqDrift value range must be positive")
    value_range = data_max - data_min
    reference_mean = float(np.mean(reference_values))
    reference_size = len(reference_values)
    log_term = float(np.log(2.0 / delta))

    alarm_count = 0
    first_alarm_time = None
    last_alarm_time = None
    first_alarm_index = None
    last_alarm_index = None
    events: list[dict[str, Any]] = []
    event_history_truncated = False
    check_count = 0
    max_evidence = 0.0
    max_margin = -np.inf
    last_evidence = 0.0
    last_bound = 0.0
    min_exceeded_bound = None

    cumsum = np.cumsum(current_values.astype(float))
    for end in range(block_size, len(current_values) + 1, block_size):
        current_mean = float(cumsum[end - 1] / end)
        evidence = abs(current_mean - reference_mean)
        bound = float(value_range * np.sqrt(0.5 * log_term * ((1.0 / reference_size) + (1.0 / end))))
        margin = evidence - bound
        check_count += 1
        last_evidence = evidence
        last_bound = bound
        max_evidence = max(max_evidence, evidence)
        max_margin = max(max_margin, margin)
        if evidence > bound:
            alarm_count += 1
            alarm_time = _iso_time(current_times[end - 1])
            if first_alarm_time is None:
                first_alarm_time = alarm_time
                first_alarm_index = end - 1
            last_alarm_time = alarm_time
            last_alarm_index = end - 1
            min_exceeded_bound = bound if min_exceeded_bound is None else min(min_exceeded_bound, bound)
            if record_events:
                if len(events) < max_event_records:
                    events.append(
                        {
                            "time": alarm_time,
                            "index": int(end - 1),
                            "current_prefix_size": int(end),
                            "reference_size": int(reference_size),
                            "reference_mean": reference_mean,
                            "current_mean": current_mean,
                            "evidence": evidence,
                            "sequential_bound": bound,
                            "margin": margin,
                        }
                    )
                else:
                    event_history_truncated = True
    if check_count == 0:
        raise ValueError("SeqDrift did not perform any sequential checks")
    return {
        "alarm_count": alarm_count,
        "events": events,
        "event_history_truncated": event_history_truncated,
        "first_alarm_time": first_alarm_time,
        "last_alarm_time": last_alarm_time,
        "first_alarm_index": first_alarm_index,
        "last_alarm_index": last_alarm_index,
        "check_count": check_count,
        "reference_mean": reference_mean,
        "value_range": value_range,
        "last_evidence": last_evidence,
        "last_bound": last_bound,
        "max_evidence": max_evidence,
        "max_margin": max_margin,
        "min_exceeded_bound": min_exceeded_bound,
    }


def _run_sprt_bernoulli(
    values: np.ndarray,
    times: np.ndarray,
    *,
    p0: float,
    p1: float,
    lower_boundary: float,
    upper_boundary: float,
    check_every: int,
    reset_policy: str,
    record_events: bool,
    max_event_records: int,
) -> dict[str, Any]:
    if not np.all((values == 0.0) | (values == 1.0)):
        raise ValueError("SPRT_BERNOULLI_ERROR_RATE requires a 0/1 Bernoulli stream")
    log_error = float(np.log(p1 / p0))
    log_ok = float(np.log((1.0 - p1) / (1.0 - p0)))
    return _run_sprt_llr_stream(
        values,
        times,
        log_increment=lambda value: log_error if value == 1.0 else log_ok,
        lower_boundary=lower_boundary,
        upper_boundary=upper_boundary,
        check_every=check_every,
        reset_policy=reset_policy,
        record_events=record_events,
        max_event_records=max_event_records,
    )


def _run_sprt_gaussian(
    values: np.ndarray,
    times: np.ndarray,
    *,
    mu0: float,
    mu1: float,
    sigma: float,
    lower_boundary: float,
    upper_boundary: float,
    check_every: int,
    reset_policy: str,
    record_events: bool,
    max_event_records: int,
) -> dict[str, Any]:
    variance = sigma * sigma
    if variance <= 0 or not np.isfinite(variance):
        raise ValueError("Gaussian SPRT sigma must be positive")

    def increment(value: float) -> float:
        return float(((value - mu0) ** 2 - (value - mu1) ** 2) / (2.0 * variance))

    return _run_sprt_llr_stream(
        values,
        times,
        log_increment=increment,
        lower_boundary=lower_boundary,
        upper_boundary=upper_boundary,
        check_every=check_every,
        reset_policy=reset_policy,
        record_events=record_events,
        max_event_records=max_event_records,
    )


def _run_sprt_llr_stream(
    values: np.ndarray,
    times: np.ndarray,
    *,
    log_increment: Any,
    lower_boundary: float,
    upper_boundary: float,
    check_every: int,
    reset_policy: str,
    record_events: bool,
    max_event_records: int,
) -> dict[str, Any]:
    llr = 0.0
    check_count = 0
    decision_count = 0
    h1_decision_count = 0
    decision_state = "continue"
    first_decision_time = None
    last_decision_time = None
    first_h1_time = None
    last_h1_time = None
    first_h1_index = None
    last_h1_index = None
    events: list[dict[str, Any]] = []
    event_history_truncated = False

    for index, value in enumerate(values):
        llr += float(log_increment(float(value)))
        if (index + 1) % check_every != 0:
            continue
        check_count += 1
        next_state = "continue"
        if llr >= upper_boundary:
            next_state = "accept_h1"
        elif llr <= lower_boundary:
            next_state = "accept_h0"
        if next_state == "continue":
            continue

        decision_count += 1
        decision_state = next_state
        decision_time = _iso_time(times[index])
        if first_decision_time is None:
            first_decision_time = decision_time
        last_decision_time = decision_time
        if next_state == "accept_h1":
            h1_decision_count += 1
            if first_h1_time is None:
                first_h1_time = decision_time
                first_h1_index = index
            last_h1_time = decision_time
            last_h1_index = index
        if record_events:
            if len(events) < max_event_records:
                events.append(
                    {
                        "time": decision_time,
                        "index": int(index),
                        "decision_state": next_state,
                        "log_likelihood_ratio": float(llr),
                        "lower_boundary": lower_boundary,
                        "upper_boundary": upper_boundary,
                    }
                )
            else:
                event_history_truncated = True
        if reset_policy == "stop_after_decision":
            break
        llr = 0.0
        decision_state = "continue"

    if check_count == 0:
        raise ValueError("SPRT did not perform any boundary checks")
    return {
        "decision_state": decision_state,
        "final_log_likelihood_ratio": float(llr),
        "decision_count": decision_count,
        "h1_decision_count": h1_decision_count,
        "check_count": check_count,
        "events": events,
        "event_history_truncated": event_history_truncated,
        "first_decision_time": first_decision_time,
        "last_decision_time": last_decision_time,
        "first_h1_time": first_h1_time,
        "last_h1_time": last_h1_time,
        "first_h1_index": first_h1_index,
        "last_h1_index": last_h1_index,
    }


def _student_t_logpdf(
    value: float,
    mus: np.ndarray,
    kappas: np.ndarray,
    alphas: np.ndarray,
    betas: np.ndarray,
) -> np.ndarray:
    df = 2.0 * alphas
    scale = np.sqrt(betas * (kappas + 1.0) / (alphas * kappas))
    z = (value - mus) / scale
    return (
        gammaln((df + 1.0) / 2.0)
        - gammaln(df / 2.0)
        - 0.5 * np.log(df * np.pi)
        - np.log(scale)
        - ((df + 1.0) / 2.0) * np.log1p((z * z) / df)
    )


def _update_normal_inverse_gamma(
    value: float,
    mus: np.ndarray,
    kappas: np.ndarray,
    alphas: np.ndarray,
    betas: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    next_kappas = kappas + 1.0
    next_mus = (kappas * mus + value) / next_kappas
    next_alphas = alphas + 0.5
    next_betas = betas + (kappas * (value - mus) ** 2) / (2.0 * next_kappas)
    return next_mus, next_kappas, next_alphas, next_betas


def _logsumexp(values: np.ndarray) -> float:
    max_value = float(np.max(values))
    return max_value + float(np.log(np.sum(np.exp(values - max_value))))


def _find_adwin_cut(
    window: list[float],
    *,
    delta: float,
    min_window_length: int,
) -> tuple[int, float, float, float] | None:
    array = np.asarray(window, dtype=float)
    n = array.size
    variance = float(np.var(array))
    log_term = np.log(2.0 / delta)
    best: tuple[int, float, float, float, float] | None = None
    cumsum = np.cumsum(array)
    total = float(cumsum[-1])
    for cut in range(min_window_length, n - min_window_length + 1):
        n_old = cut
        n_recent = n - cut
        mean_old = float(cumsum[cut - 1] / n_old)
        mean_recent = float((total - cumsum[cut - 1]) / n_recent)
        inv_n = (1.0 / n_old) + (1.0 / n_recent)
        epsilon = float(np.sqrt(2.0 * variance * inv_n * log_term) + (2.0 / 3.0) * log_term * inv_n)
        diff = abs(mean_recent - mean_old)
        if diff > epsilon and (best is None or diff - epsilon > best[0]):
            best = (diff - epsilon, cut, epsilon, mean_old, mean_recent)
    if best is None:
        return None
    _, cut, epsilon, mean_old, mean_recent = best
    return cut, epsilon, mean_old, mean_recent


def _numeric_summary(reference: np.ndarray, current: np.ndarray) -> dict[str, float]:
    return {
        "REFERENCE_MEAN": float(np.mean(reference)),
        "CURRENT_MEAN": float(np.mean(current)),
        "REFERENCE_MEDIAN": float(np.median(reference)),
        "CURRENT_MEDIAN": float(np.median(current)),
        "MEAN_DELTA": float(np.mean(current) - np.mean(reference)),
    }


def _numeric_summary_with_std(reference: np.ndarray, current: np.ndarray) -> dict[str, float]:
    summary = _numeric_summary(reference, current)
    summary["REFERENCE_STD"] = float(np.std(reference, ddof=1)) if len(reference) > 1 else 0.0
    summary["CURRENT_STD"] = float(np.std(current, ddof=1)) if len(current) > 1 else 0.0
    return summary


def _cusum_monitored_final(variant_id: str, run: dict[str, Any]) -> float:
    if variant_id == "ONE_SIDED_UPPER_CUSUM":
        return float(run["final_positive"])
    if variant_id == "ONE_SIDED_LOWER_CUSUM":
        return float(run["final_negative"])
    return float(max(run["final_positive"], run["final_negative"]))


def _cusum_monitored_max(variant_id: str, run: dict[str, Any]) -> float:
    if variant_id == "ONE_SIDED_UPPER_CUSUM":
        return float(run["max_positive"])
    if variant_id == "ONE_SIDED_LOWER_CUSUM":
        return float(run["max_negative"])
    return float(max(run["max_positive"], run["max_negative"]))


def _ewma_monitored_excess(direction: str, run: dict[str, Any]) -> float:
    candidates: list[float] = []
    if direction in {"increase", "both"} and run["max_upper_excess"] is not None:
        candidates.append(float(run["max_upper_excess"]))
    if direction in {"decrease", "both"} and run["max_lower_excess"] is not None:
        candidates.append(float(run["max_lower_excess"]))
    return max(candidates) if candidates else 0.0


def _ewma_top_level_threshold(resolved: dict[str, Any]) -> float | None:
    if resolved["direction"] == "increase":
        return resolved["ucl"]
    if resolved["direction"] == "decrease":
        return resolved["lcl"]
    return None


def _ewma_limit_mode(direction: str) -> str:
    if direction == "increase":
        return "upper"
    if direction == "decrease":
        return "lower"
    return "two_sided"


def _gma_event_names(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    renamed: list[dict[str, Any]] = []
    for event in events:
        converted = dict(event)
        converted["gma_statistic"] = converted.pop("ewma_value")
        renamed.append(converted)
    return renamed


def _adwin_interpretation(
    variant_id: str,
    reference_n: int,
    current_n: int,
    stream_n: int,
    resolved: dict[str, Any],
    run: dict[str, Any],
    alarm_state: str,
) -> str:
    base = (
        f"{variant_id} replayed reference/current rows as a finite chronological stream "
        f"(reference_n={reference_n}, current_n={current_n}, stream_n={stream_n}). "
        f"delta={resolved['delta']}, clock={resolved['clock']}, "
        f"min_window_length={resolved['min_window_length']}, grace_period={resolved['grace_period']}. "
        f"Final adaptive window width={run['window_size']} and mean={run['final_window_mean']:.6g}."
    )
    if alarm_state == "drift_detected":
        return (
            f"{base} ADWIN raised {run['alarm_count']} numeric mean-stream alarm(s); "
            f"first_alarm_time={run['first_alarm_time']}, last_alarm_time={run['last_alarm_time']}. "
            "This is a mean-level change signal, not proof of root cause or supervised concept drift."
        )
    return (
        f"{base} No ADWIN alarm was raised under this finite replay policy. "
        "This is a numeric mean-stream result, not proof that all forms of drift are absent."
    )


def _kswin_interpretation(
    variant_id: str,
    reference_n: int,
    current_n: int,
    stream_n: int,
    resolved: dict[str, Any],
    run: dict[str, Any],
    alarm_state: str,
) -> str:
    base = (
        f"{variant_id} replayed reference/current rows as a finite chronological stream "
        f"(reference_n={reference_n}, current_n={current_n}, stream_n={stream_n}). "
        f"alpha={resolved['alpha']}, window_size={resolved['window_size']}, "
        f"stat_size={resolved['stat_size']}, check_every={resolved['check_every']}. "
        f"KSWIN performed {run['check_count']} KS checks; last_statistic={run['last_statistic']:.6g}, "
        f"last_p_value={run['last_p_value']:.6g}."
    )
    if alarm_state == "drift_detected":
        return (
            f"{base} KSWIN raised {run['alarm_count']} KS-window alarm(s); "
            f"first_alarm_time={run['first_alarm_time']}, last_alarm_time={run['last_alarm_time']}. "
            "This is a windowed numeric distribution-change signal, not proof of root cause or supervised concept drift."
        )
    return (
        f"{base} No KSWIN alarm was raised under this finite replay and sliding-window policy. "
        "This is a numeric distribution-window result, not proof that all forms of drift are absent."
    )


def _page_hinkley_interpretation(
    variant_id: str,
    reference_n: int,
    current_n: int,
    stream_n: int,
    resolved: dict[str, Any],
    run: dict[str, Any],
    alarm_state: str,
) -> str:
    base = (
        f"{variant_id} replayed reference/current rows as a finite chronological stream "
        f"(reference_n={reference_n}, current_n={current_n}, stream_n={stream_n}). "
        f"direction={resolved['direction']}, threshold={resolved['threshold']}, delta={resolved['delta']}, "
        f"min_instances={resolved['min_instances']}, check_every={resolved['check_every']}, "
        f"reset_policy={resolved['reset_policy']}. "
        f"Final PH statistic={run['final_statistic']:.6g}; max statistic={run['max_statistic']:.6g}."
    )
    if alarm_state == "drift_detected":
        return (
            f"{base} Page-Hinkley raised {run['alarm_count']} {resolved['direction']}-direction mean-stream alarm(s); "
            f"first_alarm_time={run['first_alarm_time']}, last_alarm_time={run['last_alarm_time']}. "
            "This is a sequential numeric mean-change signal, not proof of root cause or retraining need."
        )
    return (
        f"{base} No Page-Hinkley alarm was raised under this finite replay policy. "
        "This is a numeric mean-stream result, not proof that all forms of drift are absent."
    )


def _cusum_interpretation(
    variant_id: str,
    reference_n: int,
    current_n: int,
    stream_n: int,
    resolved: dict[str, Any],
    run: dict[str, Any],
    alarm_state: str,
) -> str:
    monitored_final = _cusum_monitored_final(variant_id, run)
    monitored_max = _cusum_monitored_max(variant_id, run)
    base = (
        f"{variant_id} replayed reference/current rows as a finite chronological stream "
        f"(reference_n={reference_n}, current_n={current_n}, stream_n={stream_n}). "
        f"direction={resolved['direction']}, target_mean={resolved['target_mean']:.6g}, "
        f"allowance_k={resolved['allowance_k']:.6g}, decision_threshold_h={resolved['decision_threshold_h']:.6g}, "
        f"warmup_size={resolved['warmup_size']}, check_every={resolved['check_every']}, "
        f"reset_policy={resolved['reset_policy']}. "
        f"Final monitored CUSUM={monitored_final:.6g}; max monitored CUSUM={monitored_max:.6g}."
    )
    if alarm_state == "drift_detected":
        return (
            f"{base} CUSUM raised {run['alarm_count']} cumulative-deviation alarm(s); "
            f"first_alarm_time={run['first_alarm_time']}, last_alarm_time={run['last_alarm_time']}, "
            f"last_alarm_direction={run['last_alarm_direction']}. "
            "This is a sequential numeric cumulative-deviation signal, not proof of root cause or retraining need."
        )
    return (
        f"{base} No CUSUM alarm was raised under this finite replay policy. "
        "This is a numeric metric-stream result, not proof that all forms of drift are absent."
    )


def _ewma_interpretation(
    variant_id: str,
    reference_n: int,
    current_n: int,
    stream_n: int,
    resolved: dict[str, Any],
    run: dict[str, Any],
    alarm_state: str,
) -> str:
    base = (
        f"{variant_id} replayed reference/current rows as a finite chronological stream "
        f"(reference_n={reference_n}, current_n={current_n}, stream_n={stream_n}). "
        f"direction={resolved['direction']}, center_line={resolved['center_line']:.6g}, "
        f"sigma={resolved['sigma']:.6g}, lambda={resolved['lambda_']:.6g}, "
        f"ucl={resolved['ucl']}, lcl={resolved['lcl']}, warmup_size={resolved['warmup_size']}, "
        f"check_every={resolved['check_every']}. "
        f"Final EWMA={run['final_ewma']:.6g}; max={run['max_ewma']:.6g}; min={run['min_ewma']:.6g}."
    )
    if alarm_state == "drift_detected":
        return (
            f"{base} EWMA raised {run['alarm_count']} control-limit alarm(s); "
            f"first_alarm_time={run['first_alarm_time']}, last_alarm_time={run['last_alarm_time']}, "
            f"last_alarm_direction={run['last_alarm_direction']}. "
            "This is a sequential numeric control-chart signal, not proof of root cause or retraining need."
        )
    return (
        f"{base} No EWMA alarm was raised under this finite replay policy. "
        "This is a numeric metric-stream result, not proof that all forms of drift are absent."
    )


def _gma_interpretation(
    variant_id: str,
    reference_n: int,
    current_n: int,
    stream_n: int,
    resolved: dict[str, Any],
    run: dict[str, Any],
    alarm_state: str,
) -> str:
    base = (
        f"{variant_id} replayed reference/current rows as a finite chronological stream "
        f"(reference_n={reference_n}, current_n={current_n}, stream_n={stream_n}). "
        f"direction={resolved['direction']}, center_line={resolved['center_line']:.6g}, "
        f"sigma={resolved['sigma']:.6g}, lambda={resolved['lambda_']:.6g}, "
        f"ucl={resolved['ucl']}, lcl={resolved['lcl']}, warmup_size={resolved['warmup_size']}, "
        f"check_every={resolved['check_every']}. "
        f"Final GMA={run['final_ewma']:.6g}; max={run['max_ewma']:.6g}; min={run['min_ewma']:.6g}."
    )
    if alarm_state == "drift_detected":
        return (
            f"{base} GMA raised {run['alarm_count']} control-limit alarm(s); "
            f"first_alarm_time={run['first_alarm_time']}, last_alarm_time={run['last_alarm_time']}, "
            f"last_alarm_direction={run['last_alarm_direction']}. "
            "This is a sequential numeric control-chart signal, not proof of root cause or retraining need."
        )
    return (
        f"{base} No GMA alarm was raised under this finite replay policy. "
        "This is a numeric metric-stream result, not proof that all forms of drift are absent."
    )


def _bocd_interpretation(
    variant_id: str,
    reference_n: int,
    current_n: int,
    stream_n: int,
    resolved: dict[str, Any],
    run: dict[str, Any],
    alarm_state: str,
) -> str:
    base = (
        f"{variant_id} replayed reference/current rows as a finite chronological stream "
        f"(reference_n={reference_n}, current_n={current_n}, stream_n={stream_n}). "
        f"hazard_rate={resolved['hazard_rate']:.6g}, "
        f"change_probability_threshold={resolved['change_probability_threshold']:.6g}, "
        f"run_length_truncation={resolved['run_length_truncation']}, "
        f"short_run_length={resolved['short_run_length']}. "
        f"Max change point probability={run['max_change_probability']:.6g} "
        f"at index={run['max_change_probability_index']}; "
        f"final run length MAP={run['final_run_length_map']}."
    )
    if alarm_state == "drift_detected":
        return (
            f"{base} BOCD raised {run['alarm_count']} posterior/predictive alarm(s); "
            f"first_alarm_time={run['first_alarm_time']}, last_alarm_time={run['last_alarm_time']}, "
            f"last_alarm_type={run['last_alarm_type']}. "
            "This is a Gaussian online change point candidate, not proof of root cause or supervised concept drift."
        )
    return (
        f"{base} No BOCD alarm was raised under this finite replay policy. "
        "This is a Gaussian online change point result, not proof that all forms of drift are absent."
    )


def _seqdrift_interpretation(
    variant_id: str,
    reference_n: int,
    current_n: int,
    effective_reference_n: int,
    resolved: dict[str, Any],
    run: dict[str, Any],
    alarm_state: str,
) -> str:
    base = (
        f"{variant_id} compared the effective reference baseline against current-window prefixes "
        f"(reference_n={reference_n}, effective_reference_n={effective_reference_n}, current_n={current_n}). "
        f"delta={resolved['delta']}, block_size={resolved['block_size']}, "
        f"bound_type={resolved['bound_type']}, sampling_policy={resolved['sampling_policy']}. "
        f"Max evidence={run['max_evidence']:.6g}, last_bound={run['last_bound']:.6g}, "
        f"max_margin={run['max_margin']:.6g}."
    )
    if alarm_state == "drift_detected":
        return (
            f"{base} SeqDrift raised {run['alarm_count']} sequential-bound alarm(s); "
            f"first_alarm_time={run['first_alarm_time']}, last_alarm_time={run['last_alarm_time']}. "
            "This is a sequential numeric-stream change signal, not proof of root cause or supervised concept drift."
        )
    return (
        f"{base} No SeqDrift alarm was raised under this finite replay policy. "
        "This is a numeric sequential-bound result, not proof that all forms of drift are absent."
    )


def _sprt_interpretation(
    variant_id: str,
    reference_n: int,
    current_n: int,
    resolved: dict[str, Any],
    run: dict[str, Any],
    alarm_state: str,
) -> str:
    base = (
        f"{variant_id} replayed reference/current rows as a finite chronological stream "
        f"(reference_n={reference_n}, current_n={current_n}). "
        f"alpha={resolved['alpha']}, beta={resolved['beta']}, "
        f"lower_boundary={resolved['lower_boundary']:.6g}, upper_boundary={resolved['upper_boundary']:.6g}, "
        f"check_every={resolved['check_every']}, reset_policy={resolved['reset_policy']}. "
        f"Final LLR={run['final_log_likelihood_ratio']:.6g}, "
        f"decision_state={run['decision_state']}, decision_count={run['decision_count']}."
    )
    if alarm_state == "drift_detected":
        return (
            f"{base} SPRT accepted H1 {run['h1_decision_count']} time(s); "
            f"first_h1_time={run['first_h1_time']}, last_h1_time={run['last_h1_time']}. "
            "This is a pre-specified sequential likelihood-ratio signal, not proof of root cause."
        )
    if alarm_state == "normal":
        return (
            f"{base} SPRT accepted H0 under the configured hypotheses. "
            "This result depends on the pre-specified H0/H1 parameters."
        )
    return (
        f"{base} SPRT did not reach either decision boundary under this finite replay policy. "
        "This is an inconclusive sequential likelihood-ratio state."
    )


def _adwin_not_applicable(
    variant_id: str | None,
    warning: str,
    metadata: dict[str, Any] | None = None,
    prior_warnings: list[str] | None = None,
) -> DriftResult:
    result = not_applicable_result(
        method_id=ADWIN_METHOD_ID,
        method_name=ADWIN_METHOD_NAME,
        method_category=ADWIN_METHOD_CATEGORY,
        variant_id=variant_id,
        warning=warning,
        metadata=metadata,
    )
    if prior_warnings:
        result.warnings = prior_warnings + result.warnings
    return result


def _kswin_not_applicable(
    variant_id: str | None,
    warning: str,
    metadata: dict[str, Any] | None = None,
    prior_warnings: list[str] | None = None,
) -> DriftResult:
    result = not_applicable_result(
        method_id=KSWIN_METHOD_ID,
        method_name=KSWIN_METHOD_NAME,
        method_category=KSWIN_METHOD_CATEGORY,
        variant_id=variant_id,
        warning=warning,
        metadata=metadata,
    )
    if prior_warnings:
        result.warnings = prior_warnings + result.warnings
    return result


def _page_hinkley_not_applicable(
    variant_id: str | None,
    warning: str,
    metadata: dict[str, Any] | None = None,
    prior_warnings: list[str] | None = None,
) -> DriftResult:
    result = not_applicable_result(
        method_id=PAGE_HINKLEY_METHOD_ID,
        method_name=PAGE_HINKLEY_METHOD_NAME,
        method_category=PAGE_HINKLEY_METHOD_CATEGORY,
        variant_id=variant_id,
        warning=warning,
        metadata=metadata,
    )
    if prior_warnings:
        result.warnings = prior_warnings + result.warnings
    return result


def _cusum_not_applicable(
    variant_id: str | None,
    warning: str,
    metadata: dict[str, Any] | None = None,
    prior_warnings: list[str] | None = None,
) -> DriftResult:
    result = not_applicable_result(
        method_id=CUSUM_METHOD_ID,
        method_name=CUSUM_METHOD_NAME,
        method_category=CUSUM_METHOD_CATEGORY,
        variant_id=variant_id,
        warning=warning,
        metadata=metadata,
    )
    if prior_warnings:
        result.warnings = prior_warnings + result.warnings
    return result


def _ewma_not_applicable(
    variant_id: str | None,
    warning: str,
    metadata: dict[str, Any] | None = None,
    prior_warnings: list[str] | None = None,
) -> DriftResult:
    result = not_applicable_result(
        method_id=EWMA_METHOD_ID,
        method_name=EWMA_METHOD_NAME,
        method_category=EWMA_METHOD_CATEGORY,
        variant_id=variant_id,
        warning=warning,
        metadata=metadata,
    )
    if prior_warnings:
        result.warnings = prior_warnings + result.warnings
    return result


def _gma_not_applicable(
    variant_id: str | None,
    warning: str,
    metadata: dict[str, Any] | None = None,
    prior_warnings: list[str] | None = None,
) -> DriftResult:
    result = not_applicable_result(
        method_id=GMA_METHOD_ID,
        method_name=GMA_METHOD_NAME,
        method_category=GMA_METHOD_CATEGORY,
        variant_id=variant_id,
        warning=warning,
        metadata=metadata,
    )
    if prior_warnings:
        result.warnings = prior_warnings + result.warnings
    return result


def _bocd_not_applicable(
    variant_id: str | None,
    warning: str,
    metadata: dict[str, Any] | None = None,
    prior_warnings: list[str] | None = None,
) -> DriftResult:
    result = not_applicable_result(
        method_id=BOCD_METHOD_ID,
        method_name=BOCD_METHOD_NAME,
        method_category=BOCD_METHOD_CATEGORY,
        variant_id=variant_id,
        warning=warning,
        metadata=metadata,
    )
    if prior_warnings:
        result.warnings = prior_warnings + result.warnings
    return result


def _seqdrift_not_applicable(
    variant_id: str | None,
    warning: str,
    metadata: dict[str, Any] | None = None,
    prior_warnings: list[str] | None = None,
) -> DriftResult:
    result = not_applicable_result(
        method_id=SEQDRIFT_METHOD_ID,
        method_name=SEQDRIFT_METHOD_NAME,
        method_category=SEQDRIFT_METHOD_CATEGORY,
        variant_id=variant_id,
        warning=warning,
        metadata=metadata,
    )
    if prior_warnings:
        result.warnings = prior_warnings + result.warnings
    return result


def _sprt_not_applicable(
    variant_id: str | None,
    warning: str,
    metadata: dict[str, Any] | None = None,
    prior_warnings: list[str] | None = None,
) -> DriftResult:
    result = not_applicable_result(
        method_id=SPRT_METHOD_ID,
        method_name=SPRT_METHOD_NAME,
        method_category=SPRT_METHOD_CATEGORY,
        variant_id=variant_id,
        warning=warning,
        metadata=metadata,
    )
    if prior_warnings:
        result.warnings = prior_warnings + result.warnings
    return result


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


def _as_nonnegative_int(value: Any, name: str) -> int:
    if isinstance(value, bool):
        raise ValueError(f"{name} must be a nonnegative integer")
    try:
        int_value = int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must be a nonnegative integer") from exc
    if int_value < 0 or float(value) != float(int_value):
        raise ValueError(f"{name} must be a nonnegative integer")
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


def _normalize_cusum_direction(value: Any) -> str:
    normalized = str(value).lower().replace("_", "-")
    if normalized in {"increase", "upper", "up", "greater", "positive"}:
        return "increase"
    if normalized in {"decrease", "lower", "down", "less", "negative"}:
        return "decrease"
    if normalized in {"both", "two-sided", "two_sided", "two sided"}:
        return "both"
    raise ValueError("direction must be increase, decrease, or both")


def _iso_time(value: np.datetime64) -> str:
    return pd.Timestamp(value).isoformat()
