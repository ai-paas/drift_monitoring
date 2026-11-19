from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
from scipy.stats import ks_2samp

from drift_algorithm.core.result import DriftResult, not_applicable_result


SHAP_DRIFT_METHOD_ID = "DM-051"
SHAP_DRIFT_METHOD_NAME = "SHAP Drift"
SHAP_DRIFT_METHOD_CATEGORY = "ExplanationDriftMethod"
TREE_FEATURE_METHOD_ID = "DM-052"
TREE_FEATURE_METHOD_NAME = "Tree Feature 기반 감지"
TREE_FEATURE_METHOD_CATEGORY = "ExplanationDriftMethod"

SUPPORTED_SHAP_DRIFT_VARIANTS = {
    "SHAP_VALUE_DISTRIBUTION_TEST",
    "GLOBAL_IMPORTANCE_RANK_SHIFT",
    "CLASS_CONDITIONAL_SHAP_DRIFT",
}
SUPPORTED_TREE_FEATURE_VARIANTS = {
    "TIME_FEATURE_SPLIT_DETECTOR",
    "DOMAIN_CLASSIFIER_TREE",
}


def detect_shap_drift(
    data: pd.DataFrame,
    *,
    time_col: str = "time",
    value_col: str | None = None,
    reference_window: tuple[str, str] | None = None,
    current_window: tuple[str, str] | None = None,
    params: dict[str, Any] | None = None,
) -> DriftResult:
    params = dict(params or {})
    variant_id = str(params.get("variant_id", "SHAP_VALUE_DISTRIBUTION_TEST")).upper()
    metadata: dict[str, Any] = {"params": params}

    if variant_id not in SUPPORTED_SHAP_DRIFT_VARIANTS:
        return _shap_not_applicable(variant_id, f"unsupported SHAP Drift variant: {variant_id}", metadata)

    try:
        resolved = _resolve_shap_params(params, value_col, variant_id)
        prepared = _prepare_shap_windows(
            data,
            time_col=time_col,
            shap_cols=resolved["shap_cols"],
            reference_window=reference_window,
            current_window=current_window,
            min_reference_size=resolved["min_reference_size"],
            min_current_size=resolved["min_current_size"],
            class_col=resolved["class_col"] if variant_id == "CLASS_CONDITIONAL_SHAP_DRIFT" else None,
        )
    except (KeyError, TypeError, ValueError) as exc:
        return _shap_not_applicable(variant_id, str(exc), metadata)

    reference = prepared["reference_values"]
    current = prepared["current_values"]
    n_ref, p = reference.shape
    n_cur = current.shape[0]
    warnings = list(prepared["warnings"])
    metadata.update(prepared["metadata"])
    metadata.update(
        {
            "backend": "numpy_scipy_shap_drift",
            "shap_cols": resolved["shap_cols"],
            "alpha": resolved["alpha"],
            "threshold_policy": resolved["threshold_policy"],
        }
    )

    try:
        if variant_id == "SHAP_VALUE_DISTRIBUTION_TEST":
            run = _run_shap_distribution_test(reference, current, resolved)
        elif variant_id == "GLOBAL_IMPORTANCE_RANK_SHIFT":
            run = _run_global_importance_rank_shift(reference, current, resolved)
        else:
            run = _run_class_conditional_shap_drift(prepared["reference_frame"], prepared["current_frame"], resolved)
    except ValueError as exc:
        return _shap_not_applicable(variant_id, str(exc), metadata, warnings)

    drift_detected = bool(run["drift_detected"])
    severity = "drift_detected" if drift_detected else "normal"
    measurements = {
        "SHAP_DRIFT_DISTANCE": run["distance"],
        "TEST_STATISTIC": run["test_statistic"],
        "P_VALUE": run["p_value"],
        "DRIFT_ALARM_STATE": severity,
        "THRESHOLD": run["threshold"],
        "METHOD_POLICY": run["method_policy"],
        "FEATURE_IMPORTANCE_OR_RANK": run["feature_importance_or_rank"],
        "REFERENCE_SAMPLE_SIZE": int(n_ref),
        "CURRENT_SAMPLE_SIZE": int(n_cur),
        "SAMPLE_SIZE": {"reference": int(n_ref), "current": int(n_cur)},
        "FEATURE_DIMENSION": int(p),
        "FEATURE_COLUMNS": resolved["shap_cols"],
    }
    if run.get("class_distances") is not None:
        measurements["CLASS_SHAP_DRIFT_DISTANCE"] = run["class_distances"]
    if run.get("significant_features") is not None:
        measurements["SIGNIFICANT_FEATURES"] = run["significant_features"]

    return DriftResult(
        method_id=SHAP_DRIFT_METHOD_ID,
        method_name=SHAP_DRIFT_METHOD_NAME,
        method_category=SHAP_DRIFT_METHOD_CATEGORY,
        variant_id=variant_id,
        drift_detected=drift_detected,
        severity=severity,
        drift_score=run["distance"],
        p_value=run["p_value"],
        test_statistic=run["test_statistic"],
        threshold=run["threshold"],
        measurements=measurements,
        interpretation=_shap_interpretation(
            variant_id=variant_id,
            n_ref=n_ref,
            n_cur=n_cur,
            dimension=p,
            distance=run["distance"],
            p_value=run["p_value"],
            threshold=run["threshold"],
            alarm_state=severity,
            top_feature=run["top_feature"],
            policy=run["method_policy"],
        ),
        warnings=warnings,
        metadata=metadata,
    )


def detect_tree_feature(
    data: pd.DataFrame,
    *,
    time_col: str = "time",
    value_col: str | None = None,
    reference_window: tuple[str, str] | None = None,
    current_window: tuple[str, str] | None = None,
    params: dict[str, Any] | None = None,
) -> DriftResult:
    params = dict(params or {})
    variant_id = str(params.get("variant_id", "TIME_FEATURE_SPLIT_DETECTOR")).upper()
    metadata: dict[str, Any] = {"params": params}

    if variant_id not in SUPPORTED_TREE_FEATURE_VARIANTS:
        return _tree_feature_not_applicable(variant_id, f"unsupported Tree Feature variant: {variant_id}", metadata)

    try:
        resolved = _resolve_tree_feature_params(params, value_col, variant_id, time_col)
        prepared = _prepare_tree_feature_windows(
            data,
            time_col=time_col,
            feature_cols=resolved["feature_cols"],
            reference_window=reference_window,
            current_window=current_window,
            min_reference_size=resolved["min_reference_size"],
            min_current_size=resolved["min_current_size"],
        )
    except (KeyError, TypeError, ValueError) as exc:
        return _tree_feature_not_applicable(variant_id, str(exc), metadata)

    reference = prepared["reference_values"]
    current = prepared["current_values"]
    n_ref, p = reference.shape
    n_cur = current.shape[0]
    warnings = list(prepared["warnings"])
    metadata.update(prepared["metadata"])
    metadata.update(
        {
            "backend": "numpy_decision_stump_surrogate",
            "feature_cols": resolved["feature_cols"],
            "threshold_policy": resolved["threshold_policy"],
        }
    )
    warnings.append("Tree Feature uses a deterministic decision-stump surrogate, not a full tree learner")

    try:
        if variant_id == "TIME_FEATURE_SPLIT_DETECTOR":
            run = _run_time_feature_split_detector(reference, current, resolved)
        else:
            run = _run_domain_classifier_tree(reference, current, resolved)
    except ValueError as exc:
        return _tree_feature_not_applicable(variant_id, str(exc), metadata, warnings)

    drift_detected = bool(run["drift_detected"])
    severity = "drift_detected" if drift_detected else "normal"
    measurements = {
        "TREE_SPLIT_SIGNAL": run["tree_split_signal"],
        "ROC_AUC": run["roc_auc"],
        "FEATURE_IMPORTANCE_OR_RANK": run["feature_importance_or_rank"],
        "DRIFT_ALARM_STATE": severity,
        "THRESHOLD": run["threshold"],
        "METHOD_POLICY": run["method_policy"],
        "TEST_STATISTIC": run["test_statistic"],
        "REFERENCE_SAMPLE_SIZE": int(n_ref),
        "CURRENT_SAMPLE_SIZE": int(n_cur),
        "SAMPLE_SIZE": {"reference": int(n_ref), "current": int(n_cur)},
        "FEATURE_DIMENSION": int(p),
        "FEATURE_COLUMNS": resolved["feature_cols"],
    }

    return DriftResult(
        method_id=TREE_FEATURE_METHOD_ID,
        method_name=TREE_FEATURE_METHOD_NAME,
        method_category=TREE_FEATURE_METHOD_CATEGORY,
        variant_id=variant_id,
        drift_detected=drift_detected,
        severity=severity,
        drift_score=run["test_statistic"],
        p_value=None,
        test_statistic=run["test_statistic"],
        threshold=run["threshold"],
        measurements=measurements,
        interpretation=_tree_feature_interpretation(
            variant_id=variant_id,
            n_ref=n_ref,
            n_cur=n_cur,
            dimension=p,
            score=run["test_statistic"],
            threshold=run["threshold"],
            best_feature=run["tree_split_signal"]["best_split_feature"],
            alarm_state=severity,
            policy=run["method_policy"],
        ),
        warnings=warnings,
        metadata=metadata,
    )


def _resolve_shap_params(params: dict[str, Any], value_col: str | None, variant_id: str) -> dict[str, Any]:
    shap_cols = params.get("shap_cols", params.get("feature_cols"))
    if shap_cols is None and value_col is not None:
        shap_cols = [value_col]
    if isinstance(shap_cols, str):
        shap_cols = [shap_cols]
    if not shap_cols:
        raise ValueError("SHAP Drift requires shap_cols, feature_cols, or value_col")
    shap_cols = [str(col) for col in shap_cols]

    alpha = float(params.get("alpha", params.get("threshold_or_alpha", 0.05)))
    if not 0.0 < alpha < 1.0:
        raise ValueError("alpha must be between 0 and 1")
    rank_shift_threshold = float(params.get("rank_shift_threshold", params.get("threshold", 0.25)))
    if rank_shift_threshold < 0:
        raise ValueError("rank_shift_threshold must be non-negative")
    min_reference_size = int(params.get("min_reference_size", 20))
    min_current_size = int(params.get("min_current_size", 20))
    if min_reference_size < 1 or min_current_size < 1:
        raise ValueError("minimum sample sizes must be positive")

    class_col = params.get("class_col", params.get("label_col"))
    if variant_id == "CLASS_CONDITIONAL_SHAP_DRIFT" and not class_col:
        raise ValueError("CLASS_CONDITIONAL_SHAP_DRIFT requires class_col or label_col")

    return {
        "shap_cols": shap_cols,
        "alpha": alpha,
        "rank_shift_threshold": rank_shift_threshold,
        "min_reference_size": min_reference_size,
        "min_current_size": min_current_size,
        "min_class_size": int(params.get("min_class_size", 5)),
        "class_col": str(class_col) if class_col else None,
        "threshold_policy": "ks_pvalue" if variant_id != "GLOBAL_IMPORTANCE_RANK_SHIFT" else "normalized_mean_rank_shift",
    }


def _resolve_tree_feature_params(
    params: dict[str, Any],
    value_col: str | None,
    variant_id: str,
    time_col: str,
) -> dict[str, Any]:
    feature_cols = params.get("feature_cols")
    if feature_cols is None and value_col is not None:
        feature_cols = [value_col]
    if isinstance(feature_cols, str):
        feature_cols = [feature_cols]
    if not feature_cols:
        raise ValueError("Tree Feature requires feature_cols or value_col")
    feature_cols = [str(col) for col in feature_cols]

    auc_threshold = float(params.get("auc_threshold", params.get("threshold", 0.75)))
    split_accuracy_threshold = float(params.get("split_accuracy_threshold", params.get("threshold", 0.75)))
    if not 0.5 <= auc_threshold <= 1.0:
        raise ValueError("auc_threshold must be between 0.5 and 1.0")
    if not 0.5 <= split_accuracy_threshold <= 1.0:
        raise ValueError("split_accuracy_threshold must be between 0.5 and 1.0")
    min_reference_size = int(params.get("min_reference_size", 20))
    min_current_size = int(params.get("min_current_size", 20))
    if min_reference_size < 1 or min_current_size < 1:
        raise ValueError("minimum sample sizes must be positive")

    time_feature_col = str(params.get("time_feature_col", time_col))
    if variant_id == "TIME_FEATURE_SPLIT_DETECTOR" and time_feature_col not in feature_cols:
        raise ValueError("TIME_FEATURE_SPLIT_DETECTOR requires time_feature_col to be included in feature_cols")

    return {
        "feature_cols": feature_cols,
        "time_feature_col": time_feature_col,
        "auc_threshold": auc_threshold,
        "split_accuracy_threshold": split_accuracy_threshold,
        "min_reference_size": min_reference_size,
        "min_current_size": min_current_size,
        "threshold_policy": "time_feature_best_split_accuracy"
        if variant_id == "TIME_FEATURE_SPLIT_DETECTOR"
        else "domain_classifier_univariate_auc",
    }


def _prepare_shap_windows(
    data: pd.DataFrame,
    *,
    time_col: str,
    shap_cols: list[str],
    reference_window: tuple[str, str] | None,
    current_window: tuple[str, str] | None,
    min_reference_size: int,
    min_current_size: int,
    class_col: str | None,
) -> dict[str, Any]:
    if not isinstance(data, pd.DataFrame):
        raise TypeError("data must be a pandas DataFrame")
    required_cols = [time_col, *shap_cols]
    if class_col is not None:
        required_cols.append(class_col)
    missing = [col for col in required_cols if col not in data.columns]
    if missing:
        raise KeyError(f"missing required columns: {missing}")

    frame = data[required_cols].copy()
    frame[time_col] = pd.to_datetime(frame[time_col], errors="coerce")
    before_time_drop = len(frame)
    frame = frame.dropna(subset=[time_col])
    warnings: list[str] = []
    if len(frame) < before_time_drop:
        warnings.append(f"dropped {before_time_drop - len(frame)} rows with invalid time values")

    for col in shap_cols:
        frame[col] = pd.to_numeric(frame[col], errors="coerce")
    before_value_drop = len(frame)
    frame = frame.dropna(subset=shap_cols)
    if len(frame) < before_value_drop:
        warnings.append(f"dropped {before_value_drop - len(frame)} rows with invalid SHAP values")
    if frame.empty:
        raise ValueError("no valid SHAP rows after cleaning")
    frame = frame.sort_values(time_col).reset_index(drop=True)

    reference, current = _split_shap_windows(frame, time_col, reference_window, current_window)
    if len(reference) < min_reference_size:
        raise ValueError(f"reference sample size {len(reference)} is below min_reference_size {min_reference_size}")
    if len(current) < min_current_size:
        raise ValueError(f"current sample size {len(current)} is below min_current_size {min_current_size}")

    return {
        "reference_frame": reference,
        "current_frame": current,
        "reference_values": reference[shap_cols].to_numpy(dtype=float),
        "current_values": current[shap_cols].to_numpy(dtype=float),
        "warnings": warnings,
        "metadata": {
            "time_col": time_col,
            "reference_window": reference_window,
            "current_window": current_window,
        },
    }


def _prepare_tree_feature_windows(
    data: pd.DataFrame,
    *,
    time_col: str,
    feature_cols: list[str],
    reference_window: tuple[str, str] | None,
    current_window: tuple[str, str] | None,
    min_reference_size: int,
    min_current_size: int,
) -> dict[str, Any]:
    if not isinstance(data, pd.DataFrame):
        raise TypeError("data must be a pandas DataFrame")
    required_cols = [time_col, *[col for col in feature_cols if col != time_col]]
    missing = [col for col in required_cols if col not in data.columns]
    if missing:
        raise KeyError(f"missing required columns: {missing}")

    frame = data[[col for col in dict.fromkeys(required_cols)]].copy()
    frame[time_col] = pd.to_datetime(frame[time_col], errors="coerce")
    before_time_drop = len(frame)
    frame = frame.dropna(subset=[time_col])
    warnings: list[str] = []
    if len(frame) < before_time_drop:
        warnings.append(f"dropped {before_time_drop - len(frame)} rows with invalid time values")

    for col in feature_cols:
        if col == time_col:
            frame[col] = frame[time_col].astype("int64") / 1_000_000_000
        else:
            frame[col] = pd.to_numeric(frame[col], errors="coerce")
    before_value_drop = len(frame)
    frame = frame.dropna(subset=feature_cols)
    if len(frame) < before_value_drop:
        warnings.append(f"dropped {before_value_drop - len(frame)} rows with invalid feature values")
    if frame.empty:
        raise ValueError("no valid feature rows after cleaning")
    frame = frame.sort_values(time_col).reset_index(drop=True)

    reference, current = _split_shap_windows(frame, time_col, reference_window, current_window)
    if len(reference) < min_reference_size:
        raise ValueError(f"reference sample size {len(reference)} is below min_reference_size {min_reference_size}")
    if len(current) < min_current_size:
        raise ValueError(f"current sample size {len(current)} is below min_current_size {min_current_size}")

    return {
        "reference_values": reference[feature_cols].to_numpy(dtype=float),
        "current_values": current[feature_cols].to_numpy(dtype=float),
        "warnings": warnings,
        "metadata": {
            "time_col": time_col,
            "reference_window": reference_window,
            "current_window": current_window,
        },
    }


def _split_shap_windows(
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


def _run_shap_distribution_test(reference: np.ndarray, current: np.ndarray, resolved: dict[str, Any]) -> dict[str, Any]:
    stats: list[float] = []
    p_values: list[float] = []
    details: list[dict[str, Any]] = []
    for idx, feature in enumerate(resolved["shap_cols"]):
        result = ks_2samp(reference[:, idx], current[:, idx], alternative="two-sided", method="asymp")
        statistic = float(result.statistic)
        p_value = float(result.pvalue)
        stats.append(statistic)
        p_values.append(p_value)
        details.append(
            {
                "feature": feature,
                "rank": 0,
                "score": statistic,
                "p_value": p_value,
                "reference_importance": float(np.mean(np.abs(reference[:, idx]))),
                "current_importance": float(np.mean(np.abs(current[:, idx]))),
            }
        )
    ranked = _rank_feature_details(details, key="score")
    min_p_value = float(np.min(p_values))
    max_statistic = float(np.max(stats))
    significant = [item["feature"] for item in ranked if item["p_value"] < resolved["alpha"]]
    return {
        "distance": max_statistic,
        "test_statistic": max_statistic,
        "p_value": min_p_value,
        "threshold": resolved["alpha"],
        "method_policy": "per_feature_ks_min_pvalue",
        "drift_detected": min_p_value < resolved["alpha"],
        "feature_importance_or_rank": ranked,
        "significant_features": significant,
        "top_feature": ranked[0]["feature"],
    }


def _run_global_importance_rank_shift(reference: np.ndarray, current: np.ndarray, resolved: dict[str, Any]) -> dict[str, Any]:
    ref_importance = np.mean(np.abs(reference), axis=0)
    cur_importance = np.mean(np.abs(current), axis=0)
    ref_ranks = _descending_ranks(ref_importance)
    cur_ranks = _descending_ranks(cur_importance)
    rank_delta = cur_ranks - ref_ranks
    denominator = max(1, len(resolved["shap_cols"]) - 1)
    normalized_delta = np.abs(rank_delta) / denominator
    distance = float(np.mean(normalized_delta))
    details = []
    for idx, feature in enumerate(resolved["shap_cols"]):
        details.append(
            {
                "feature": feature,
                "rank": int(cur_ranks[idx]),
                "reference_rank": int(ref_ranks[idx]),
                "current_rank": int(cur_ranks[idx]),
                "rank_delta": int(rank_delta[idx]),
                "score": float(normalized_delta[idx]),
                "reference_importance": float(ref_importance[idx]),
                "current_importance": float(cur_importance[idx]),
                "importance_delta": float(cur_importance[idx] - ref_importance[idx]),
            }
        )
    ranked = _rank_feature_details(details, key="score")
    return {
        "distance": distance,
        "test_statistic": distance,
        "p_value": None,
        "threshold": resolved["rank_shift_threshold"],
        "method_policy": "mean_normalized_absolute_rank_delta",
        "drift_detected": distance > resolved["rank_shift_threshold"],
        "feature_importance_or_rank": ranked,
        "significant_features": None,
        "top_feature": ranked[0]["feature"],
    }


def _run_class_conditional_shap_drift(
    reference: pd.DataFrame,
    current: pd.DataFrame,
    resolved: dict[str, Any],
) -> dict[str, Any]:
    class_col = resolved["class_col"]
    shap_cols = resolved["shap_cols"]
    common_classes = sorted(set(reference[class_col].dropna()) & set(current[class_col].dropna()))
    if not common_classes:
        raise ValueError("no common classes in reference/current windows")

    class_distances: dict[str, Any] = {}
    details: list[dict[str, Any]] = []
    min_p_value = 1.0
    max_statistic = 0.0
    skipped: list[str] = []
    for class_value in common_classes:
        ref_class = reference[reference[class_col] == class_value]
        cur_class = current[current[class_col] == class_value]
        if len(ref_class) < resolved["min_class_size"] or len(cur_class) < resolved["min_class_size"]:
            skipped.append(str(class_value))
            continue
        class_key = str(class_value)
        feature_results = []
        for idx, feature in enumerate(shap_cols):
            result = ks_2samp(ref_class[feature].to_numpy(dtype=float), cur_class[feature].to_numpy(dtype=float), alternative="two-sided", method="asymp")
            statistic = float(result.statistic)
            p_value = float(result.pvalue)
            min_p_value = min(min_p_value, p_value)
            max_statistic = max(max_statistic, statistic)
            feature_results.append({"feature": feature, "score": statistic, "p_value": p_value})
            details.append(
                {
                    "feature": feature,
                    "class": class_key,
                    "rank": 0,
                    "score": statistic,
                    "p_value": p_value,
                    "reference_importance": float(np.mean(np.abs(ref_class[feature]))),
                    "current_importance": float(np.mean(np.abs(cur_class[feature]))),
                }
            )
        class_distances[class_key] = {
            "sample_size": {"reference": int(len(ref_class)), "current": int(len(cur_class))},
            "max_statistic": float(max(item["score"] for item in feature_results)),
            "min_p_value": float(min(item["p_value"] for item in feature_results)),
            "features": _rank_feature_details(feature_results, key="score"),
        }
    if not class_distances:
        raise ValueError("no class has enough rows for CLASS_CONDITIONAL_SHAP_DRIFT")

    ranked = _rank_feature_details(details, key="score")
    significant = [f"{item['class']}:{item['feature']}" for item in ranked if item["p_value"] < resolved["alpha"]]
    return {
        "distance": max_statistic,
        "test_statistic": max_statistic,
        "p_value": min_p_value,
        "threshold": resolved["alpha"],
        "method_policy": "class_conditional_per_feature_ks_min_pvalue",
        "drift_detected": min_p_value < resolved["alpha"],
        "feature_importance_or_rank": ranked,
        "class_distances": class_distances,
        "significant_features": significant,
        "top_feature": ranked[0]["feature"],
        "skipped_classes": skipped,
    }


def _descending_ranks(values: np.ndarray) -> np.ndarray:
    order = np.argsort(-values, kind="mergesort")
    ranks = np.empty(len(values), dtype=int)
    ranks[order] = np.arange(1, len(values) + 1)
    return ranks


def _run_time_feature_split_detector(reference: np.ndarray, current: np.ndarray, resolved: dict[str, Any]) -> dict[str, Any]:
    stumps = _feature_stump_scores(reference, current, resolved["feature_cols"])
    best = stumps[0]
    time_stump = next(item for item in stumps if item["feature"] == resolved["time_feature_col"])
    time_split_count = int(
        best["feature"] == resolved["time_feature_col"]
        and time_stump["split_accuracy"] >= resolved["split_accuracy_threshold"]
    )
    drift_detected = bool(time_split_count > 0)
    signal = {
        "best_split_feature": best["feature"],
        "best_split_threshold": best["threshold"],
        "best_split_accuracy": best["split_accuracy"],
        "best_split_direction": best["direction"],
        "time_feature": resolved["time_feature_col"],
        "time_feature_split_accuracy": time_stump["split_accuracy"],
        "time_split_count": time_split_count,
        "shallow_time_split": drift_detected,
    }
    return {
        "tree_split_signal": signal,
        "roc_auc": time_stump["roc_auc"],
        "feature_importance_or_rank": _tree_feature_rank(stumps),
        "threshold": resolved["split_accuracy_threshold"],
        "method_policy": "time_feature_best_stump_split",
        "test_statistic": time_stump["split_accuracy"],
        "drift_detected": drift_detected,
    }


def _run_domain_classifier_tree(reference: np.ndarray, current: np.ndarray, resolved: dict[str, Any]) -> dict[str, Any]:
    stumps = _feature_stump_scores(reference, current, resolved["feature_cols"])
    best = stumps[0]
    drift_detected = bool(best["roc_auc"] >= resolved["auc_threshold"])
    signal = {
        "best_split_feature": best["feature"],
        "best_split_threshold": best["threshold"],
        "best_split_accuracy": best["split_accuracy"],
        "best_split_direction": best["direction"],
        "time_split_count": int(best["feature"] == resolved.get("time_feature_col")),
        "shallow_time_split": best["feature"] == resolved.get("time_feature_col"),
    }
    return {
        "tree_split_signal": signal,
        "roc_auc": best["roc_auc"],
        "feature_importance_or_rank": _tree_feature_rank(stumps),
        "threshold": resolved["auc_threshold"],
        "method_policy": "best_univariate_domain_classifier_auc",
        "test_statistic": best["roc_auc"],
        "drift_detected": drift_detected,
    }


def _feature_stump_scores(reference: np.ndarray, current: np.ndarray, feature_cols: list[str]) -> list[dict[str, Any]]:
    labels = np.concatenate([np.zeros(reference.shape[0], dtype=int), np.ones(current.shape[0], dtype=int)])
    matrix = np.vstack([reference, current])
    scores: list[dict[str, Any]] = []
    for idx, feature in enumerate(feature_cols):
        values = matrix[:, idx]
        auc = _binary_auc(labels, values)
        threshold, accuracy, direction = _best_stump(values, labels)
        importance = abs(auc - 0.5) * 2.0
        scores.append(
            {
                "feature": feature,
                "roc_auc": auc,
                "split_accuracy": accuracy,
                "threshold": threshold,
                "direction": direction,
                "score": importance,
            }
        )
    return sorted(scores, key=lambda item: (-float(item["score"]), -float(item["split_accuracy"]), str(item["feature"])))


def _binary_auc(labels: np.ndarray, scores: np.ndarray) -> float:
    pos = scores[labels == 1]
    neg = scores[labels == 0]
    if len(pos) == 0 or len(neg) == 0:
        raise ValueError("AUC requires both reference and current rows")
    comparisons = (pos[:, None] > neg[None, :]).mean()
    ties = (pos[:, None] == neg[None, :]).mean()
    auc = float(comparisons + 0.5 * ties)
    return max(auc, 1.0 - auc)


def _best_stump(values: np.ndarray, labels: np.ndarray) -> tuple[float, float, str]:
    order = np.argsort(values, kind="mergesort")
    sorted_values = values[order]
    candidates = np.unique(sorted_values)
    if len(candidates) == 1:
        return float(candidates[0]), float(max(np.mean(labels == 0), np.mean(labels == 1))), "constant"
    thresholds = (candidates[:-1] + candidates[1:]) / 2.0
    best_threshold = float(thresholds[0])
    best_accuracy = 0.0
    best_direction = "current_above"
    for threshold in thresholds:
        pred_above = (values > threshold).astype(int)
        accuracy_above = float(np.mean(pred_above == labels))
        accuracy_below = float(np.mean((1 - pred_above) == labels))
        if accuracy_above >= best_accuracy:
            best_accuracy = accuracy_above
            best_threshold = float(threshold)
            best_direction = "current_above"
        if accuracy_below >= best_accuracy:
            best_accuracy = accuracy_below
            best_threshold = float(threshold)
            best_direction = "current_below"
    return best_threshold, best_accuracy, best_direction


def _tree_feature_rank(stumps: list[dict[str, Any]]) -> list[dict[str, Any]]:
    ranked = []
    for rank, item in enumerate(stumps, start=1):
        ranked.append(
            {
                "feature": item["feature"],
                "rank": rank,
                "score": item["score"],
                "roc_auc": item["roc_auc"],
                "split_accuracy": item["split_accuracy"],
                "split_threshold": item["threshold"],
                "split_direction": item["direction"],
            }
        )
    return ranked


def _rank_feature_details(details: list[dict[str, Any]], *, key: str) -> list[dict[str, Any]]:
    ranked = sorted(details, key=lambda item: (-float(item[key]), str(item["feature"])))
    output = []
    for rank, item in enumerate(ranked, start=1):
        copied = dict(item)
        copied["rank"] = rank
        output.append(copied)
    return output


def _shap_interpretation(
    *,
    variant_id: str,
    n_ref: int,
    n_cur: int,
    dimension: int,
    distance: float,
    p_value: float | None,
    threshold: float,
    alarm_state: str,
    top_feature: str,
    policy: str,
) -> str:
    p_value_text = "n/a" if p_value is None else f"{p_value:.6g}"
    return (
        f"{variant_id} compared SHAP explanations across {n_ref} reference and {n_cur} current rows "
        f"for {dimension} features. The largest/aggregate SHAP drift distance is {distance:.6g}; "
        f"p_value={p_value_text}, threshold={threshold:.6g}, policy={policy}, top shifted feature={top_feature}. "
        f"Alarm state is {alarm_state}."
    )


def _tree_feature_interpretation(
    *,
    variant_id: str,
    n_ref: int,
    n_cur: int,
    dimension: int,
    score: float,
    threshold: float,
    best_feature: str,
    alarm_state: str,
    policy: str,
) -> str:
    return (
        f"{variant_id} compared {n_ref} reference and {n_cur} current rows across {dimension} features. "
        f"The best tree-style split feature is {best_feature}; score={score:.6g}, threshold={threshold:.6g}, "
        f"policy={policy}. Alarm state is {alarm_state}."
    )


def _shap_not_applicable(
    variant_id: str | None,
    warning: str,
    metadata: dict[str, Any] | None = None,
    prior_warnings: list[str] | None = None,
) -> DriftResult:
    result = not_applicable_result(
        method_id=SHAP_DRIFT_METHOD_ID,
        method_name=SHAP_DRIFT_METHOD_NAME,
        method_category=SHAP_DRIFT_METHOD_CATEGORY,
        variant_id=variant_id,
        warning=warning,
        metadata=metadata,
    )
    if prior_warnings:
        result.warnings = [*prior_warnings, warning]
    return result


def _tree_feature_not_applicable(
    variant_id: str | None,
    warning: str,
    metadata: dict[str, Any] | None = None,
    prior_warnings: list[str] | None = None,
) -> DriftResult:
    result = not_applicable_result(
        method_id=TREE_FEATURE_METHOD_ID,
        method_name=TREE_FEATURE_METHOD_NAME,
        method_category=TREE_FEATURE_METHOD_CATEGORY,
        variant_id=variant_id,
        warning=warning,
        metadata=metadata,
    )
    if prior_warnings:
        result.warnings = [*prior_warnings, warning]
    return result


__all__ = ["detect_shap_drift", "detect_tree_feature"]
