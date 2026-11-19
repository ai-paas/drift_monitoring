from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from drift_algorithm.core.result import DriftResult, not_applicable_result


HAT_METHOD_ID = "DM-055"
HAT_METHOD_NAME = "HAT"
HAT_METHOD_CATEGORY = "OperationalAdaptationMethod"
DRIFT_RETRAINING_METHOD_ID = "DM-056"
DRIFT_RETRAINING_METHOD_NAME = "DriftRetrainingClassifier"
DRIFT_RETRAINING_METHOD_CATEGORY = "OperationalAdaptationMethod"

SUPPORTED_HAT_VARIANTS = {
    "HAT_ADWIN_NODE_MONITORING",
    "HAT_ALTERNATE_TREE_REPLACEMENT",
}
SUPPORTED_DRIFT_RETRAINING_VARIANTS = {
    "DRIFT_RETRAINING_WITH_ADWIN",
    "DRIFT_RETRAINING_WITH_PAGE_HINKLEY",
    "DRIFT_RETRAINING_CHAMPION_CHALLENGER",
}


def detect_hat(
    data: pd.DataFrame,
    *,
    time_col: str = "time",
    value_col: str | None = None,
    reference_window: tuple[str, str] | None = None,
    current_window: tuple[str, str] | None = None,
    params: dict[str, Any] | None = None,
) -> DriftResult:
    params = dict(params or {})
    variant_id = str(params.get("variant_id", "HAT_ADWIN_NODE_MONITORING")).upper()
    metadata: dict[str, Any] = {"params": params, "finite_replay_policy": "reference_current_hat_log_replay"}

    if variant_id not in SUPPORTED_HAT_VARIANTS:
        return _hat_not_applicable(variant_id, f"unsupported HAT variant: {variant_id}", metadata)

    try:
        resolved = _resolve_hat_params(params, value_col)
        prepared = _prepare_hat_windows(
            data,
            time_col=time_col,
            reference_window=reference_window,
            current_window=current_window,
            resolved=resolved,
        )
    except (KeyError, TypeError, ValueError) as exc:
        return _hat_not_applicable(variant_id, str(exc), metadata)

    warnings = list(prepared["warnings"])
    metadata.update(prepared["metadata"])
    metadata.update({"backend": "numpy_hat_log_replay", "threshold_policy": resolved["threshold_policy"]})
    warnings.append("HAT uses finite log replay and does not train a Hoeffding Adaptive Tree")

    reference_errors = prepared["reference_errors"]
    current_errors = prepared["current_errors"]
    current_frame = prepared["current_frame"]
    n_ref = len(reference_errors)
    n_cur = len(current_errors)

    try:
        if variant_id == "HAT_ADWIN_NODE_MONITORING":
            run = _run_hat_node_monitoring(reference_errors, current_errors, current_frame, resolved)
        else:
            run = _run_hat_alternate_replacement(reference_errors, current_errors, current_frame, resolved)
    except ValueError as exc:
        return _hat_not_applicable(variant_id, str(exc), metadata, warnings)

    drift_detected = run["drift_alarm_state"] == "drift_detected"
    severity = "drift_detected" if drift_detected else ("warning" if run["warning_state"] else "normal")
    measurements = {
        "ADAPTATION_EVENT": run["adaptation_event"],
        "DRIFT_ALARM_STATE": run["drift_alarm_state"],
        "WARNING_STATE": run["warning_state"],
        "ONLINE_OR_PRE_POST_PERFORMANCE": run["performance"],
        "HAT_STATISTIC": run["hat_statistic"],
        "TEST_STATISTIC": run["hat_statistic"],
        "THRESHOLD": run["threshold"],
        "METHOD_POLICY": run["method_policy"],
        "NODE_DRIFT_STATE": run["node_drift_state"],
        "NODE_ALARM_COUNT": run["node_alarm_count"],
        "REFERENCE_ERROR_RATE": float(np.mean(reference_errors)),
        "CURRENT_ERROR_RATE": float(np.mean(current_errors)),
        "ERROR_RATE_DELTA": float(np.mean(current_errors) - np.mean(reference_errors)),
        "REFERENCE_SAMPLE_SIZE": int(n_ref),
        "CURRENT_SAMPLE_SIZE": int(n_cur),
        "SAMPLE_SIZE": {"reference": int(n_ref), "current": int(n_cur)},
    }

    return DriftResult(
        method_id=HAT_METHOD_ID,
        method_name=HAT_METHOD_NAME,
        method_category=HAT_METHOD_CATEGORY,
        variant_id=variant_id,
        drift_detected=drift_detected,
        severity=severity,
        drift_score=run["hat_statistic"],
        p_value=None,
        test_statistic=run["hat_statistic"],
        threshold=run["threshold"],
        measurements=measurements,
        interpretation=_hat_interpretation(
            variant_id=variant_id,
            n_ref=n_ref,
            n_cur=n_cur,
            statistic=run["hat_statistic"],
            threshold=run["threshold"],
            alarm_state=run["drift_alarm_state"],
            policy=run["method_policy"],
            adaptation_event=run["adaptation_event"],
        ),
        warnings=warnings,
        metadata=metadata,
    )


def detect_driftretrainingclassifier(
    data: pd.DataFrame,
    *,
    time_col: str = "time",
    value_col: str | None = None,
    reference_window: tuple[str, str] | None = None,
    current_window: tuple[str, str] | None = None,
    params: dict[str, Any] | None = None,
) -> DriftResult:
    params = dict(params or {})
    variant_id = str(params.get("variant_id", "DRIFT_RETRAINING_WITH_ADWIN")).upper()
    metadata: dict[str, Any] = {"params": params, "finite_replay_policy": "reference_current_retraining_log_replay"}

    if variant_id not in SUPPORTED_DRIFT_RETRAINING_VARIANTS:
        return _drift_retraining_not_applicable(
            variant_id,
            f"unsupported DriftRetrainingClassifier variant: {variant_id}",
            metadata,
        )

    try:
        resolved = _resolve_drift_retraining_params(params, value_col, variant_id)
        prepared = _prepare_retraining_windows(
            data,
            time_col=time_col,
            reference_window=reference_window,
            current_window=current_window,
            resolved=resolved,
        )
    except (KeyError, TypeError, ValueError) as exc:
        return _drift_retraining_not_applicable(variant_id, str(exc), metadata)

    warnings = list(prepared["warnings"])
    metadata.update(prepared["metadata"])
    metadata.update({"backend": "numpy_retraining_log_replay", "threshold_policy": resolved["threshold_policy"]})
    warnings.append("DriftRetrainingClassifier consumes operational logs and does not train or deploy a model")

    reference_metric = prepared["reference_metric"]
    current_metric = prepared["current_metric"]
    current_frame = prepared["current_frame"]
    n_ref = len(reference_metric)
    n_cur = len(current_metric)

    try:
        if variant_id == "DRIFT_RETRAINING_WITH_ADWIN":
            run = _run_retraining_adwin(reference_metric, current_metric, current_frame, resolved)
        elif variant_id == "DRIFT_RETRAINING_WITH_PAGE_HINKLEY":
            run = _run_retraining_page_hinkley(reference_metric, current_metric, current_frame, resolved)
        else:
            run = _run_retraining_champion_challenger(reference_metric, current_metric, current_frame, resolved)
    except ValueError as exc:
        return _drift_retraining_not_applicable(variant_id, str(exc), metadata, warnings)

    drift_detected = run["drift_alarm_state"] == "drift_detected"
    severity = "drift_detected" if drift_detected else ("warning" if run["warning_state"] else "normal")
    measurements = {
        "DRIFT_ALARM_STATE": run["drift_alarm_state"],
        "WARNING_STATE": run["warning_state"],
        "TEST_STATISTIC": run["test_statistic"],
        "THRESHOLD": run["threshold"],
        "METHOD_POLICY": run["method_policy"],
        "RETRAINING_EVENT": run["retraining_event"],
        "ADAPTATION_EVENT": run["retraining_event"],
        "ONLINE_OR_PRE_POST_PERFORMANCE": run["performance"],
        "RETRAINING_CANDIDATE_WINDOW": run["candidate_window"],
        "REFERENCE_METRIC_MEAN": float(np.mean(reference_metric)),
        "CURRENT_METRIC_MEAN": float(np.mean(current_metric)),
        "METRIC_MEAN_DELTA": float(np.mean(current_metric) - np.mean(reference_metric)),
        "REFERENCE_SAMPLE_SIZE": int(n_ref),
        "CURRENT_SAMPLE_SIZE": int(n_cur),
        "SAMPLE_SIZE": {"reference": int(n_ref), "current": int(n_cur)},
    }
    if run.get("promotion_decision") is not None:
        measurements["PROMOTION_DECISION"] = run["promotion_decision"]
        measurements["CHAMPION_CHALLENGER_UPLIFT"] = run["champion_challenger_uplift"]

    return DriftResult(
        method_id=DRIFT_RETRAINING_METHOD_ID,
        method_name=DRIFT_RETRAINING_METHOD_NAME,
        method_category=DRIFT_RETRAINING_METHOD_CATEGORY,
        variant_id=variant_id,
        drift_detected=drift_detected,
        severity=severity,
        drift_score=run["test_statistic"],
        p_value=None,
        test_statistic=run["test_statistic"],
        threshold=run["threshold"],
        measurements=measurements,
        interpretation=_drift_retraining_interpretation(
            variant_id=variant_id,
            n_ref=n_ref,
            n_cur=n_cur,
            statistic=run["test_statistic"],
            threshold=run["threshold"],
            alarm_state=run["drift_alarm_state"],
            policy=run["method_policy"],
            retraining_event=run["retraining_event"],
        ),
        warnings=warnings,
        metadata=metadata,
    )


def _resolve_hat_params(params: dict[str, Any], value_col: str | None) -> dict[str, Any]:
    error_col = params.get("error_col", value_col)
    y_true = params.get("y_true", params.get("label_col"))
    y_pred = params.get("y_pred", params.get("prediction_col"))
    if not error_col and not (y_true and y_pred):
        raise ValueError("HAT requires error_col/value_col or y_true and y_pred")

    warning_delta = float(params.get("warning_delta", 0.1))
    drift_delta = float(params.get("drift_delta", params.get("threshold", 0.2)))
    if warning_delta < 0 or drift_delta < 0:
        raise ValueError("warning_delta and drift_delta must be non-negative")
    if warning_delta > drift_delta:
        raise ValueError("warning_delta must be less than or equal to drift_delta")

    min_reference_size = int(params.get("min_reference_size", 30))
    min_current_size = int(params.get("min_current_size", 30))
    if min_reference_size < 1 or min_current_size < 1:
        raise ValueError("minimum sample sizes must be positive")

    return {
        "error_col": str(error_col) if error_col else None,
        "y_true": str(y_true) if y_true else None,
        "y_pred": str(y_pred) if y_pred else None,
        "node_col": str(params.get("node_col", "node_id")) if params.get("node_col", "node_id") else None,
        "online_accuracy_col": str(params.get("online_accuracy_col", "online_accuracy")),
        "alternate_created_col": str(params.get("alternate_created_col", "alternate_created")),
        "replacement_col": str(params.get("replacement_col", "tree_replaced")),
        "warning_delta": warning_delta,
        "drift_delta": drift_delta,
        "min_reference_size": min_reference_size,
        "min_current_size": min_current_size,
        "min_node_size": int(params.get("min_node_size", 10)),
        "threshold_policy": "current_error_rate_delta",
    }


def _resolve_drift_retraining_params(params: dict[str, Any], value_col: str | None, variant_id: str) -> dict[str, Any]:
    metric_col = params.get("metric_col", params.get("error_col", value_col))
    y_true = params.get("y_true", params.get("label_col"))
    y_pred = params.get("y_pred", params.get("prediction_col"))
    if variant_id != "DRIFT_RETRAINING_CHAMPION_CHALLENGER" and not metric_col and not (y_true and y_pred):
        raise ValueError("DriftRetrainingClassifier requires metric_col/error_col/value_col or y_true and y_pred")

    champion_metric_col = params.get("champion_metric_col", "champion_metric")
    challenger_metric_col = params.get("challenger_metric_col", "challenger_metric")
    if variant_id == "DRIFT_RETRAINING_CHAMPION_CHALLENGER" and not (champion_metric_col and challenger_metric_col):
        raise ValueError("champion/challenger variant requires champion_metric_col and challenger_metric_col")

    threshold = float(params.get("threshold", params.get("drift_threshold", 0.2)))
    warning_threshold = float(params.get("warning_threshold", threshold / 2.0))
    if threshold < 0 or warning_threshold < 0:
        raise ValueError("threshold and warning_threshold must be non-negative")
    if warning_threshold > threshold:
        raise ValueError("warning_threshold must be less than or equal to threshold")
    delta = float(params.get("delta", 0.0))
    uplift_threshold = float(params.get("uplift_threshold", params.get("promotion_threshold", 0.02)))
    min_reference_size = int(params.get("min_reference_size", 30))
    min_current_size = int(params.get("min_current_size", 30))
    if min_reference_size < 1 or min_current_size < 1:
        raise ValueError("minimum sample sizes must be positive")

    return {
        "metric_col": str(metric_col) if metric_col else None,
        "y_true": str(y_true) if y_true else None,
        "y_pred": str(y_pred) if y_pred else None,
        "metric_direction": str(params.get("metric_direction", "higher_is_worse")),
        "threshold": threshold,
        "warning_threshold": warning_threshold,
        "delta": delta,
        "uplift_threshold": uplift_threshold,
        "min_reference_size": min_reference_size,
        "min_current_size": min_current_size,
        "retraining_event_col": str(params.get("retraining_event_col", "retraining_triggered")),
        "model_promoted_col": str(params.get("model_promoted_col", "model_promoted")),
        "champion_metric_col": str(champion_metric_col),
        "challenger_metric_col": str(challenger_metric_col),
        "threshold_policy": "metric_mean_delta"
        if variant_id != "DRIFT_RETRAINING_CHAMPION_CHALLENGER"
        else "champion_challenger_uplift",
    }


def _prepare_hat_windows(
    data: pd.DataFrame,
    *,
    time_col: str,
    reference_window: tuple[str, str] | None,
    current_window: tuple[str, str] | None,
    resolved: dict[str, Any],
) -> dict[str, Any]:
    if not isinstance(data, pd.DataFrame):
        raise TypeError("data must be a pandas DataFrame")

    required_cols = [time_col]
    if resolved["error_col"]:
        required_cols.append(resolved["error_col"])
    else:
        required_cols.extend([resolved["y_true"], resolved["y_pred"]])
    optional_cols = [
        resolved["node_col"],
        resolved["online_accuracy_col"],
        resolved["alternate_created_col"],
        resolved["replacement_col"],
    ]
    required_present = [col for col in dict.fromkeys(required_cols) if col is not None]
    missing = [col for col in required_present if col not in data.columns]
    if missing:
        raise KeyError(f"missing required columns: {missing}")
    use_cols = list(dict.fromkeys([*required_present, *[col for col in optional_cols if col in data.columns]]))

    frame = data[use_cols].copy()
    frame[time_col] = pd.to_datetime(frame[time_col], errors="coerce")
    before_time_drop = len(frame)
    frame = frame.dropna(subset=[time_col])
    warnings: list[str] = []
    if len(frame) < before_time_drop:
        warnings.append(f"dropped {before_time_drop - len(frame)} rows with invalid time values")

    if resolved["error_col"]:
        frame["_hat_error"] = pd.to_numeric(frame[resolved["error_col"]], errors="coerce")
    else:
        frame["_hat_error"] = (frame[resolved["y_true"]] != frame[resolved["y_pred"]]).astype(float)
    before_error_drop = len(frame)
    frame = frame.dropna(subset=["_hat_error"])
    if len(frame) < before_error_drop:
        warnings.append(f"dropped {before_error_drop - len(frame)} rows with invalid HAT error values")
    if not frame["_hat_error"].isin([0, 1, 0.0, 1.0]).all():
        raise ValueError("HAT error stream must contain only 0/1 values")
    frame["_hat_error"] = frame["_hat_error"].astype(float)

    frame = frame.sort_values(time_col).reset_index(drop=True)
    reference, current = _split_hat_windows(frame, time_col, reference_window, current_window)
    if len(reference) < resolved["min_reference_size"]:
        raise ValueError(f"reference sample size {len(reference)} is below min_reference_size {resolved['min_reference_size']}")
    if len(current) < resolved["min_current_size"]:
        raise ValueError(f"current sample size {len(current)} is below min_current_size {resolved['min_current_size']}")

    return {
        "reference_errors": reference["_hat_error"].to_numpy(dtype=float),
        "current_errors": current["_hat_error"].to_numpy(dtype=float),
        "current_frame": current,
        "warnings": warnings,
        "metadata": {
            "time_col": time_col,
            "reference_window": reference_window,
            "current_window": current_window,
            "available_optional_columns": [col for col in optional_cols if col in data.columns],
        },
    }


def _prepare_retraining_windows(
    data: pd.DataFrame,
    *,
    time_col: str,
    reference_window: tuple[str, str] | None,
    current_window: tuple[str, str] | None,
    resolved: dict[str, Any],
) -> dict[str, Any]:
    if not isinstance(data, pd.DataFrame):
        raise TypeError("data must be a pandas DataFrame")

    required_cols = [time_col]
    if resolved["metric_col"]:
        required_cols.append(resolved["metric_col"])
    elif resolved["y_true"] and resolved["y_pred"]:
        required_cols.extend([resolved["y_true"], resolved["y_pred"]])
    if resolved["champion_metric_col"] in data.columns or resolved["challenger_metric_col"] in data.columns:
        required_cols.extend([resolved["champion_metric_col"], resolved["challenger_metric_col"]])
    optional_cols = [resolved["retraining_event_col"], resolved["model_promoted_col"]]
    use_cols = [col for col in dict.fromkeys(required_cols + optional_cols) if col in data.columns]
    missing = [col for col in dict.fromkeys(required_cols) if col not in data.columns]
    if missing:
        raise KeyError(f"missing required columns: {missing}")

    frame = data[use_cols].copy()
    frame[time_col] = pd.to_datetime(frame[time_col], errors="coerce")
    before_time_drop = len(frame)
    frame = frame.dropna(subset=[time_col])
    warnings: list[str] = []
    if len(frame) < before_time_drop:
        warnings.append(f"dropped {before_time_drop - len(frame)} rows with invalid time values")

    if resolved["metric_col"]:
        frame["_retraining_metric"] = pd.to_numeric(frame[resolved["metric_col"]], errors="coerce")
    elif resolved["y_true"] and resolved["y_pred"]:
        frame["_retraining_metric"] = (frame[resolved["y_true"]] != frame[resolved["y_pred"]]).astype(float)
    else:
        frame["_retraining_metric"] = 0.0

    before_metric_drop = len(frame)
    frame = frame.dropna(subset=["_retraining_metric"])
    if len(frame) < before_metric_drop:
        warnings.append(f"dropped {before_metric_drop - len(frame)} rows with invalid retraining metric values")
    frame = frame.sort_values(time_col).reset_index(drop=True)

    reference, current = _split_hat_windows(frame, time_col, reference_window, current_window)
    if len(reference) < resolved["min_reference_size"]:
        raise ValueError(f"reference sample size {len(reference)} is below min_reference_size {resolved['min_reference_size']}")
    if len(current) < resolved["min_current_size"]:
        raise ValueError(f"current sample size {len(current)} is below min_current_size {resolved['min_current_size']}")

    return {
        "reference_metric": reference["_retraining_metric"].to_numpy(dtype=float),
        "current_metric": current["_retraining_metric"].to_numpy(dtype=float),
        "current_frame": current,
        "warnings": warnings,
        "metadata": {
            "time_col": time_col,
            "reference_window": reference_window,
            "current_window": current_window,
            "available_optional_columns": [col for col in optional_cols if col in data.columns],
        },
    }


def _split_hat_windows(
    frame: pd.DataFrame,
    time_col: str,
    reference_window: tuple[str, str] | None,
    current_window: tuple[str, str] | None,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    if reference_window is not None and current_window is not None:
        ref_start, ref_end = pd.to_datetime(reference_window[0]), pd.to_datetime(reference_window[1])
        cur_start, cur_end = pd.to_datetime(current_window[0]), pd.to_datetime(current_window[1])
        reference = frame[(frame[time_col] >= ref_start) & (frame[time_col] <= ref_end)]
        current = frame[(frame[time_col] >= cur_start) & (frame[time_col] <= cur_end)]
        if reference.empty or current.empty:
            raise ValueError("reference/current windows must contain rows")
        return reference.copy(), current.copy()
    midpoint = len(frame) // 2
    if midpoint == 0 or midpoint == len(frame):
        raise ValueError("data must contain enough rows to split reference/current windows")
    return frame.iloc[:midpoint].copy(), frame.iloc[midpoint:].copy()


def _run_retraining_adwin(
    reference_metric: np.ndarray,
    current_metric: np.ndarray,
    current_frame: pd.DataFrame,
    resolved: dict[str, Any],
) -> dict[str, Any]:
    delta = _directional_metric_delta(reference_metric, current_metric, resolved)
    warning_state = delta >= resolved["warning_threshold"]
    drift_state = delta >= resolved["threshold"] or _sum_optional_bool(current_frame, resolved["retraining_event_col"]) > 0
    return _retraining_run(
        statistic=delta,
        threshold=resolved["threshold"],
        warning_state=warning_state,
        drift_state=drift_state,
        method_policy="adwin_style_metric_mean_delta_retraining_trigger",
        reference_metric=reference_metric,
        current_metric=current_metric,
        current_frame=current_frame,
        resolved=resolved,
    )


def _run_retraining_page_hinkley(
    reference_metric: np.ndarray,
    current_metric: np.ndarray,
    current_frame: pd.DataFrame,
    resolved: dict[str, Any],
) -> dict[str, Any]:
    baseline = float(np.mean(reference_metric))
    direction = 1.0 if resolved["metric_direction"] == "higher_is_worse" else -1.0
    cumulative = 0.0
    min_cumulative = 0.0
    max_statistic = 0.0
    for value in current_metric:
        cumulative += direction * (float(value) - baseline - resolved["delta"])
        min_cumulative = min(min_cumulative, cumulative)
        max_statistic = max(max_statistic, cumulative - min_cumulative)
    warning_state = max_statistic >= resolved["warning_threshold"]
    drift_state = max_statistic >= resolved["threshold"] or _sum_optional_bool(current_frame, resolved["retraining_event_col"]) > 0
    return _retraining_run(
        statistic=max_statistic,
        threshold=resolved["threshold"],
        warning_state=warning_state,
        drift_state=drift_state,
        method_policy="page_hinkley_style_cumulative_metric_deviation",
        reference_metric=reference_metric,
        current_metric=current_metric,
        current_frame=current_frame,
        resolved=resolved,
    )


def _run_retraining_champion_challenger(
    reference_metric: np.ndarray,
    current_metric: np.ndarray,
    current_frame: pd.DataFrame,
    resolved: dict[str, Any],
) -> dict[str, Any]:
    champion_col = resolved["champion_metric_col"]
    challenger_col = resolved["challenger_metric_col"]
    if champion_col not in current_frame.columns or challenger_col not in current_frame.columns:
        raise ValueError("champion/challenger metric columns are required for DRIFT_RETRAINING_CHAMPION_CHALLENGER")
    champion = pd.to_numeric(current_frame[champion_col], errors="coerce").dropna().to_numpy(dtype=float)
    challenger = pd.to_numeric(current_frame[challenger_col], errors="coerce").dropna().to_numpy(dtype=float)
    if len(champion) == 0 or len(challenger) == 0:
        raise ValueError("champion/challenger metrics must contain numeric values")
    uplift = _metric_uplift(champion, challenger, resolved)
    promoted = _sum_optional_bool(current_frame, resolved["model_promoted_col"]) > 0
    drift_state = uplift >= resolved["uplift_threshold"] or promoted
    warning_state = uplift >= resolved["warning_threshold"]
    run = _retraining_run(
        statistic=uplift,
        threshold=resolved["uplift_threshold"],
        warning_state=warning_state,
        drift_state=drift_state,
        method_policy="champion_challenger_metric_uplift",
        reference_metric=reference_metric,
        current_metric=current_metric,
        current_frame=current_frame,
        resolved=resolved,
    )
    run["promotion_decision"] = {
        "promoted": bool(promoted),
        "promotion_recommended": bool(uplift >= resolved["uplift_threshold"]),
        "champion_metric_mean": float(np.mean(champion)),
        "challenger_metric_mean": float(np.mean(challenger)),
    }
    run["champion_challenger_uplift"] = uplift
    return run


def _retraining_run(
    *,
    statistic: float,
    threshold: float,
    warning_state: bool,
    drift_state: bool,
    method_policy: str,
    reference_metric: np.ndarray,
    current_metric: np.ndarray,
    current_frame: pd.DataFrame,
    resolved: dict[str, Any],
) -> dict[str, Any]:
    retraining_count = _sum_optional_bool(current_frame, resolved["retraining_event_col"])
    promoted_count = _sum_optional_bool(current_frame, resolved["model_promoted_col"])
    return {
        "test_statistic": float(statistic),
        "threshold": float(threshold),
        "warning_state": bool(warning_state),
        "drift_alarm_state": "drift_detected" if drift_state else ("warning" if warning_state else "normal"),
        "method_policy": method_policy,
        "retraining_event": {
            "retraining_triggered_count": retraining_count,
            "model_promoted_count": promoted_count,
            "retraining_recommended": bool(drift_state),
        },
        "performance": {
            "reference_metric_mean": float(np.mean(reference_metric)),
            "current_metric_mean": float(np.mean(current_metric)),
            "metric_mean_delta": float(np.mean(current_metric) - np.mean(reference_metric)),
        },
        "candidate_window": {
            "current_start_index": 0,
            "current_end_index": int(len(current_metric) - 1),
            "sample_size": int(len(current_metric)),
        },
    }


def _directional_metric_delta(reference_metric: np.ndarray, current_metric: np.ndarray, resolved: dict[str, Any]) -> float:
    delta = float(np.mean(current_metric) - np.mean(reference_metric))
    return delta if resolved["metric_direction"] == "higher_is_worse" else -delta


def _metric_uplift(champion: np.ndarray, challenger: np.ndarray, resolved: dict[str, Any]) -> float:
    delta = float(np.mean(challenger) - np.mean(champion))
    return -delta if resolved["metric_direction"] == "higher_is_worse" else delta


def _run_hat_node_monitoring(
    reference_errors: np.ndarray,
    current_errors: np.ndarray,
    current_frame: pd.DataFrame,
    resolved: dict[str, Any],
) -> dict[str, Any]:
    ref_rate = float(np.mean(reference_errors))
    cur_rate = float(np.mean(current_errors))
    delta = cur_rate - ref_rate
    warning_state = delta >= resolved["warning_delta"]
    drift_state = delta >= resolved["drift_delta"]
    node_states = _hat_node_states(reference_rate=ref_rate, current_frame=current_frame, resolved=resolved)
    node_alarm_count = sum(1 for item in node_states if item["state"] == "drift_detected")
    if node_alarm_count > 0:
        drift_state = True
    performance = _hat_performance(reference_errors, current_errors, current_frame, resolved)
    return {
        "hat_statistic": delta,
        "threshold": resolved["drift_delta"],
        "warning_state": bool(warning_state),
        "drift_alarm_state": "drift_detected" if drift_state else ("warning" if warning_state else "normal"),
        "adaptation_event": {
            "alternate_tree_created_count": _sum_optional_bool(current_frame, resolved["alternate_created_col"]),
            "tree_replacement_count": _sum_optional_bool(current_frame, resolved["replacement_col"]),
        },
        "performance": performance,
        "node_drift_state": node_states,
        "node_alarm_count": node_alarm_count,
        "method_policy": "hat_adwin_node_error_delta_surrogate",
    }


def _run_hat_alternate_replacement(
    reference_errors: np.ndarray,
    current_errors: np.ndarray,
    current_frame: pd.DataFrame,
    resolved: dict[str, Any],
) -> dict[str, Any]:
    ref_rate = float(np.mean(reference_errors))
    cur_rate = float(np.mean(current_errors))
    delta = cur_rate - ref_rate
    created_count = _sum_optional_bool(current_frame, resolved["alternate_created_col"])
    replacement_count = _sum_optional_bool(current_frame, resolved["replacement_col"])
    drift_state = replacement_count > 0 or created_count > 0 or delta >= resolved["drift_delta"]
    warning_state = delta >= resolved["warning_delta"] or created_count > 0
    performance = _hat_performance(reference_errors, current_errors, current_frame, resolved)
    return {
        "hat_statistic": float(max(delta, replacement_count)),
        "threshold": resolved["drift_delta"],
        "warning_state": bool(warning_state),
        "drift_alarm_state": "drift_detected" if drift_state else ("warning" if warning_state else "normal"),
        "adaptation_event": {
            "alternate_tree_created_count": created_count,
            "tree_replacement_count": replacement_count,
            "replacement_observed": replacement_count > 0,
        },
        "performance": performance,
        "node_drift_state": _hat_node_states(reference_rate=ref_rate, current_frame=current_frame, resolved=resolved),
        "node_alarm_count": 0,
        "method_policy": "hat_alternate_replacement_event_replay",
    }


def _hat_node_states(reference_rate: float, current_frame: pd.DataFrame, resolved: dict[str, Any]) -> list[dict[str, Any]]:
    node_col = resolved["node_col"]
    if node_col not in current_frame.columns:
        return []
    states: list[dict[str, Any]] = []
    for node_id, group in current_frame.groupby(node_col, sort=True):
        if len(group) < resolved["min_node_size"]:
            continue
        error_rate = float(np.mean(group["_hat_error"]))
        delta = error_rate - reference_rate
        state = "drift_detected" if delta >= resolved["drift_delta"] else ("warning" if delta >= resolved["warning_delta"] else "normal")
        states.append(
            {
                "node_id": str(node_id),
                "sample_size": int(len(group)),
                "error_rate": error_rate,
                "error_rate_delta": delta,
                "state": state,
            }
        )
    return sorted(states, key=lambda item: (-item["error_rate_delta"], item["node_id"]))


def _hat_performance(
    reference_errors: np.ndarray,
    current_errors: np.ndarray,
    current_frame: pd.DataFrame,
    resolved: dict[str, Any],
) -> dict[str, Any]:
    performance = {
        "reference_accuracy": float(1.0 - np.mean(reference_errors)),
        "current_accuracy": float(1.0 - np.mean(current_errors)),
        "accuracy_delta": float((1.0 - np.mean(current_errors)) - (1.0 - np.mean(reference_errors))),
    }
    col = resolved["online_accuracy_col"]
    if col in current_frame.columns:
        values = pd.to_numeric(current_frame[col], errors="coerce").dropna().to_numpy(dtype=float)
        if len(values):
            performance["online_accuracy_mean"] = float(np.mean(values))
            performance["online_accuracy_last"] = float(values[-1])
    return performance


def _sum_optional_bool(frame: pd.DataFrame, col: str) -> int:
    if col not in frame.columns:
        return 0
    values = frame[col]
    if values.dtype == bool:
        return int(values.sum())
    numeric = pd.to_numeric(values, errors="coerce").fillna(0)
    return int((numeric != 0).sum())


def _hat_interpretation(
    *,
    variant_id: str,
    n_ref: int,
    n_cur: int,
    statistic: float,
    threshold: float,
    alarm_state: str,
    policy: str,
    adaptation_event: dict[str, Any],
) -> str:
    return (
        f"{variant_id} replayed {n_ref} reference and {n_cur} current labeled stream rows. "
        f"HAT statistic={statistic:.6g}, threshold={threshold:.6g}, policy={policy}, "
        f"alternate_created={adaptation_event.get('alternate_tree_created_count', 0)}, "
        f"tree_replaced={adaptation_event.get('tree_replacement_count', 0)}. Alarm state is {alarm_state}."
    )


def _drift_retraining_interpretation(
    *,
    variant_id: str,
    n_ref: int,
    n_cur: int,
    statistic: float,
    threshold: float,
    alarm_state: str,
    policy: str,
    retraining_event: dict[str, Any],
) -> str:
    return (
        f"{variant_id} replayed {n_ref} reference and {n_cur} current operational rows. "
        f"Retraining statistic={statistic:.6g}, threshold={threshold:.6g}, policy={policy}, "
        f"retraining_triggers={retraining_event.get('retraining_triggered_count', 0)}, "
        f"model_promotions={retraining_event.get('model_promoted_count', 0)}. Alarm state is {alarm_state}."
    )


def _hat_not_applicable(
    variant_id: str | None,
    warning: str,
    metadata: dict[str, Any] | None = None,
    prior_warnings: list[str] | None = None,
) -> DriftResult:
    result = not_applicable_result(
        method_id=HAT_METHOD_ID,
        method_name=HAT_METHOD_NAME,
        method_category=HAT_METHOD_CATEGORY,
        variant_id=variant_id,
        warning=warning,
        metadata=metadata,
    )
    if prior_warnings:
        result.warnings = [*prior_warnings, warning]
    return result


def _drift_retraining_not_applicable(
    variant_id: str | None,
    warning: str,
    metadata: dict[str, Any] | None = None,
    prior_warnings: list[str] | None = None,
) -> DriftResult:
    result = not_applicable_result(
        method_id=DRIFT_RETRAINING_METHOD_ID,
        method_name=DRIFT_RETRAINING_METHOD_NAME,
        method_category=DRIFT_RETRAINING_METHOD_CATEGORY,
        variant_id=variant_id,
        warning=warning,
        metadata=metadata,
    )
    if prior_warnings:
        result.warnings = [*prior_warnings, warning]
    return result


__all__ = ["detect_hat", "detect_driftretrainingclassifier"]
