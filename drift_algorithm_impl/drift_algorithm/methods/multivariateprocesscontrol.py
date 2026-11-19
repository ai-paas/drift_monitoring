from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
from scipy.stats import chi2, f

from drift_algorithm.core.result import DriftResult, not_applicable_result


HOTELLING_T2_METHOD_ID = "DM-042"
HOTELLING_T2_METHOD_NAME = "Hotelling T2"
HOTELLING_T2_METHOD_CATEGORY = "MultivariateProcessControl"
MEWMA_METHOD_ID = "DM-043"
MEWMA_METHOD_NAME = "MEWMA"
MEWMA_METHOD_CATEGORY = "MultivariateProcessControl"
MAHALANOBIS_METHOD_ID = "DM-044"
MAHALANOBIS_METHOD_NAME = "Mahalanobis Distance"
MAHALANOBIS_METHOD_CATEGORY = "MultivariateProcessControl"

SUPPORTED_HOTELLING_T2_VARIANTS = {
    "HOTELLING_T2_ONE_SAMPLE_PHASE_II",
    "HOTELLING_T2_TWO_SAMPLE",
    "REGULARIZED_HOTELLING_T2",
}
SUPPORTED_MEWMA_VARIANTS = {"MEWMA_STANDARD", "MEWMA_WITH_MAHALANOBIS_D2"}
SUPPORTED_MAHALANOBIS_VARIANTS = {
    "SAMPLE_MAHALANOBIS_OUTLIER",
    "WINDOW_MEAN_MAHALANOBIS",
    "ROBUST_MAHALANOBIS",
}


def detect_hotelling_t2(
    data: pd.DataFrame,
    *,
    time_col: str = "time",
    value_col: str | None = None,
    reference_window: tuple[str, str] | None = None,
    current_window: tuple[str, str] | None = None,
    params: dict[str, Any] | None = None,
) -> DriftResult:
    params = dict(params or {})
    variant_id = str(params.get("variant_id", "HOTELLING_T2_TWO_SAMPLE")).upper()
    metadata: dict[str, Any] = {"params": params}

    if variant_id not in SUPPORTED_HOTELLING_T2_VARIANTS:
        return _hotelling_not_applicable(variant_id, f"unsupported Hotelling T2 variant: {variant_id}", metadata)

    try:
        resolved = _resolve_hotelling_params(params, value_col, variant_id)
        prepared = _prepare_multivariate_windows(
            data,
            time_col=time_col,
            feature_cols=resolved["feature_cols"],
            reference_window=reference_window,
            current_window=current_window,
            min_reference_size=resolved["min_reference_size"],
            min_current_size=resolved["min_current_size"],
        )
    except (KeyError, TypeError, ValueError) as exc:
        return _hotelling_not_applicable(variant_id, str(exc), metadata)

    reference = prepared["reference_values"]
    current = prepared["current_values"]
    feature_cols = resolved["feature_cols"]
    n_ref, p = reference.shape
    n_cur = current.shape[0]
    warnings = list(prepared["warnings"])
    metadata.update(prepared["metadata"])
    metadata.update(
        {
            "backend": "numpy_hotelling_t2",
            "feature_cols": feature_cols,
            "alpha": resolved["alpha"],
            "covariance_estimator": resolved["covariance_estimator"],
            "regularization_strength": resolved["regularization_strength"],
            "regularization_method": resolved["regularization_method"],
        }
    )

    if params.get("threshold_or_alpha") is not None:
        warnings.append("threshold_or_alpha was interpreted as Hotelling T2 alpha")
    if min(n_ref, n_cur) <= p:
        warnings.append("sample size is not much larger than feature dimension; covariance estimates may be unstable")
    if resolved["sample_imbalance_warning_ratio"] < max(n_ref, n_cur) / min(n_ref, n_cur):
        warnings.append("reference/current sample sizes are imbalanced")

    try:
        run = _run_hotelling_t2(reference, current, variant_id, resolved)
    except ValueError as exc:
        return _hotelling_not_applicable(variant_id, str(exc), metadata, warnings)

    if run["condition_number"] is not None and run["condition_number"] > resolved["condition_number_warning"]:
        warnings.append("covariance matrix is ill-conditioned; interpret Hotelling T2 with caution")
    if run["regularized"]:
        warnings.append("regularized covariance was used; statistic scale depends on regularization policy")

    p_value = run["p_value"]
    control_limit = run["control_limit"]
    drift_detected = bool(run["t2_statistic"] > control_limit) if control_limit is not None else bool(
        p_value is not None and p_value < resolved["alpha"]
    )
    severity = "drift_detected" if drift_detected else "normal"
    alarm_state = "drift_detected" if drift_detected else "normal"
    measurements = {
        "HOTELLING_T2_STATISTIC": run["t2_statistic"],
        "TEST_STATISTIC": run["t2_statistic"],
        "P_VALUE": p_value,
        "CONTROL_LIMIT": control_limit,
        "DRIFT_ALARM_STATE": alarm_state,
        "METHOD_POLICY": run["method_policy"],
        "SAMPLE_SIZE": {"reference": int(n_ref), "current": int(n_cur)},
        "SAMPLE_SIZE_REFERENCE": int(n_ref),
        "SAMPLE_SIZE_CURRENT": int(n_cur),
        "FEATURE_DIMENSION": int(p),
        "MEAN_DIFFERENCE_VECTOR": run["mean_difference"].tolist(),
        "FEATURE_COLUMNS": feature_cols,
    }

    return DriftResult(
        method_id=HOTELLING_T2_METHOD_ID,
        method_name=HOTELLING_T2_METHOD_NAME,
        method_category=HOTELLING_T2_METHOD_CATEGORY,
        variant_id=variant_id,
        drift_detected=drift_detected,
        severity=severity,
        drift_score=run["t2_statistic"],
        p_value=p_value,
        test_statistic=run["t2_statistic"],
        threshold=control_limit if control_limit is not None else resolved["alpha"],
        measurements=measurements,
        interpretation=_hotelling_interpretation(
            variant_id=variant_id,
            n_ref=n_ref,
            n_cur=n_cur,
            dimension=p,
            t2_statistic=run["t2_statistic"],
            p_value=p_value,
            control_limit=control_limit,
            alpha=resolved["alpha"],
            alarm_state=alarm_state,
            regularized=run["regularized"],
        ),
        warnings=warnings,
        metadata=metadata,
    )


def detect_mewma(
    data: pd.DataFrame,
    *,
    time_col: str = "time",
    value_col: str | None = None,
    reference_window: tuple[str, str] | None = None,
    current_window: tuple[str, str] | None = None,
    params: dict[str, Any] | None = None,
) -> DriftResult:
    params = dict(params or {})
    variant_id = str(params.get("variant_id", "MEWMA_STANDARD")).upper()
    metadata: dict[str, Any] = {"params": params}

    if variant_id not in SUPPORTED_MEWMA_VARIANTS:
        return _mewma_not_applicable(variant_id, f"unsupported MEWMA variant: {variant_id}", metadata)

    try:
        resolved = _resolve_mewma_params(params, value_col)
        prepared = _prepare_multivariate_windows(
            data,
            time_col=time_col,
            feature_cols=resolved["feature_cols"],
            reference_window=reference_window,
            current_window=current_window,
            min_reference_size=resolved["min_reference_size"],
            min_current_size=resolved["min_current_size"],
        )
    except (KeyError, TypeError, ValueError) as exc:
        return _mewma_not_applicable(variant_id, str(exc), metadata)

    reference = prepared["reference_values"]
    current = prepared["current_values"]
    feature_cols = resolved["feature_cols"]
    n_ref, p = reference.shape
    n_cur = current.shape[0]
    warnings = list(prepared["warnings"])
    metadata.update(prepared["metadata"])
    metadata.update(
        {
            "backend": "numpy_mewma",
            "feature_cols": feature_cols,
            "lambda": resolved["lambda_value"],
            "alpha": resolved["alpha"],
            "covariance_estimator": resolved["covariance_estimator"],
            "regularization_strength": resolved["regularization_strength"],
            "metric_scaling_policy": resolved["metric_scaling_policy"],
        }
    )
    if params.get("threshold_or_alpha") is not None:
        warnings.append("threshold_or_alpha was interpreted as MEWMA alpha")
    if min(n_ref, n_cur) <= p:
        warnings.append("sample size is not much larger than feature dimension; covariance estimates may be unstable")

    try:
        run = _run_mewma(reference, current, resolved)
    except ValueError as exc:
        return _mewma_not_applicable(variant_id, str(exc), metadata, warnings)

    if run["condition_number"] is not None and run["condition_number"] > resolved["condition_number_warning"]:
        warnings.append("covariance matrix is ill-conditioned; interpret MEWMA with caution")
    if run["regularized"]:
        warnings.append("regularized covariance was used for MEWMA")

    drift_detected = run["alarm_state"] == "drift_detected"
    severity = "drift_detected" if drift_detected else "normal"
    measurements = {
        "MEWMA_STATISTIC": run["mewma_statistic"],
        "TEST_STATISTIC": run["mewma_statistic"],
        "MAHALANOBIS_DISTANCE": run["mahalanobis_d2"],
        "CONTROL_LIMIT": run["control_limit"],
        "DRIFT_ALARM_STATE": run["alarm_state"],
        "SAMPLE_SIZE": {"reference": int(n_ref), "current": int(n_cur)},
        "SAMPLE_SIZE_REFERENCE": int(n_ref),
        "SAMPLE_SIZE_CURRENT": int(n_cur),
        "FEATURE_DIMENSION": int(p),
        "FEATURE_COLUMNS": feature_cols,
        "LAMBDA": resolved["lambda_value"],
        "ALARM_TIME": run["alarm_time"],
        "ALARM_INDEX": run["alarm_index"],
        "FINAL_EWMA_VECTOR": run["final_ewma_vector"].tolist(),
        "REFERENCE_MEAN_VECTOR": run["reference_mean"].tolist(),
    }

    return DriftResult(
        method_id=MEWMA_METHOD_ID,
        method_name=MEWMA_METHOD_NAME,
        method_category=MEWMA_METHOD_CATEGORY,
        variant_id=variant_id,
        drift_detected=drift_detected,
        severity=severity,
        drift_score=run["mewma_statistic"],
        p_value=None,
        test_statistic=run["mewma_statistic"],
        threshold=run["control_limit"],
        measurements=measurements,
        interpretation=_mewma_interpretation(
            variant_id=variant_id,
            n_ref=n_ref,
            n_cur=n_cur,
            dimension=p,
            statistic=run["mewma_statistic"],
            control_limit=run["control_limit"],
            alarm_state=run["alarm_state"],
            lambda_value=resolved["lambda_value"],
            regularized=run["regularized"],
        ),
        warnings=warnings,
        metadata=metadata,
    )


def detect_mahalanobis_distance(
    data: pd.DataFrame,
    *,
    time_col: str = "time",
    value_col: str | None = None,
    reference_window: tuple[str, str] | None = None,
    current_window: tuple[str, str] | None = None,
    params: dict[str, Any] | None = None,
) -> DriftResult:
    params = dict(params or {})
    variant_id = str(params.get("variant_id", "WINDOW_MEAN_MAHALANOBIS")).upper()
    metadata: dict[str, Any] = {"params": params}

    if variant_id not in SUPPORTED_MAHALANOBIS_VARIANTS:
        return _mahalanobis_not_applicable(
            variant_id,
            f"unsupported Mahalanobis Distance variant: {variant_id}",
            metadata,
        )

    try:
        resolved = _resolve_mahalanobis_params(params, value_col, variant_id)
        prepared = _prepare_multivariate_windows(
            data,
            time_col=time_col,
            feature_cols=resolved["feature_cols"],
            reference_window=reference_window,
            current_window=current_window,
            min_reference_size=resolved["min_reference_size"],
            min_current_size=resolved["min_current_size"],
        )
    except (KeyError, TypeError, ValueError) as exc:
        return _mahalanobis_not_applicable(variant_id, str(exc), metadata)

    reference = prepared["reference_values"]
    current = prepared["current_values"]
    feature_cols = resolved["feature_cols"]
    n_ref, p = reference.shape
    n_cur = current.shape[0]
    warnings = list(prepared["warnings"])
    metadata.update(prepared["metadata"])
    metadata.update(
        {
            "backend": "numpy_mahalanobis_distance",
            "feature_cols": feature_cols,
            "alpha": resolved["alpha"],
            "threshold_policy": resolved["threshold_policy"],
            "regularization_strength": resolved["regularization_strength"],
        }
    )

    if params.get("threshold_or_alpha") is not None:
        warnings.append("threshold_or_alpha was interpreted as Mahalanobis alpha")
    if min(n_ref, n_cur) <= p:
        warnings.append("sample size is not much larger than feature dimension; covariance estimates may be unstable")

    try:
        run = _run_mahalanobis_distance(reference, current, variant_id, resolved)
    except ValueError as exc:
        return _mahalanobis_not_applicable(variant_id, str(exc), metadata, warnings)

    if run["condition_number"] is not None and run["condition_number"] > resolved["condition_number_warning"]:
        warnings.append("covariance matrix is ill-conditioned; interpret Mahalanobis distance with caution")
    if run["regularized"]:
        warnings.append("regularized covariance was used for Mahalanobis distance")
    if run["robust"]:
        warnings.append("robust diagonal covariance was used; distance scale differs from classical covariance")

    drift_detected = bool(run["threshold_exceedance"])
    severity = "drift_detected" if drift_detected else "normal"
    measurements = {
        "MAHALANOBIS_DISTANCE": run["mahalanobis_distance"],
        "MAHALANOBIS_D2": run["mahalanobis_d2"],
        "TEST_STATISTIC": run["mahalanobis_d2"],
        "P_VALUE": run["p_value"],
        "CONTROL_LIMIT": run["control_limit"],
        "THRESHOLD": run["control_limit"],
        "DRIFT_ALARM_STATE": "drift_detected" if drift_detected else "normal",
        "METHOD_POLICY": run["method_policy"],
        "OUTLIER_FLAG": drift_detected,
        "THRESHOLD_EXCEEDANCE": drift_detected,
        "OUTLIER_COUNT": run["outlier_count"],
        "OUTLIER_FRACTION": run["outlier_fraction"],
        "SAMPLE_SIZE": {"reference": int(n_ref), "current": int(n_cur)},
        "SAMPLE_SIZE_REFERENCE": int(n_ref),
        "SAMPLE_SIZE_CURRENT": int(n_cur),
        "FEATURE_DIMENSION": int(p),
        "FEATURE_COLUMNS": feature_cols,
        "REFERENCE_CENTER_VECTOR": run["reference_center"].tolist(),
        "CURRENT_CENTER_VECTOR": run["current_center"].tolist(),
    }

    return DriftResult(
        method_id=MAHALANOBIS_METHOD_ID,
        method_name=MAHALANOBIS_METHOD_NAME,
        method_category=MAHALANOBIS_METHOD_CATEGORY,
        variant_id=variant_id,
        drift_detected=drift_detected,
        severity=severity,
        drift_score=run["mahalanobis_distance"],
        p_value=run["p_value"],
        test_statistic=run["mahalanobis_d2"],
        threshold=run["control_limit"],
        measurements=measurements,
        interpretation=_mahalanobis_interpretation(
            variant_id=variant_id,
            n_ref=n_ref,
            n_cur=n_cur,
            dimension=p,
            distance=run["mahalanobis_distance"],
            d2=run["mahalanobis_d2"],
            control_limit=run["control_limit"],
            p_value=run["p_value"],
            outlier_fraction=run["outlier_fraction"],
            alarm_state=measurements["DRIFT_ALARM_STATE"],
            robust=run["robust"],
        ),
        warnings=warnings,
        metadata=metadata,
    )


def _resolve_hotelling_params(params: dict[str, Any], value_col: str | None, variant_id: str) -> dict[str, Any]:
    feature_cols = params.get("feature_cols", params.get("embedding_cols"))
    if feature_cols is None and value_col is not None:
        feature_cols = [value_col]
    if feature_cols is None:
        feature_cols = params.get("input_signal")
    if isinstance(feature_cols, str):
        feature_cols = [feature_cols]
    if not feature_cols:
        raise ValueError("Hotelling T2 requires params['feature_cols'] or params['embedding_cols']")
    feature_cols = [str(col) for col in feature_cols]
    if len(feature_cols) < 2:
        raise ValueError("Hotelling T2 requires at least two numeric feature columns")
    if params.get("pca_components") is not None:
        raise ValueError("pca_components is not implemented in the first Hotelling T2 implementation")

    alpha = float(params.get("alpha", params.get("threshold_or_alpha", 0.05)))
    if not 0.0 < alpha < 1.0:
        raise ValueError("alpha must be in (0, 1)")
    covariance_estimator = str(params.get("covariance_estimator", "pooled")).lower()
    if covariance_estimator not in {"pooled", "reference", "regularized"}:
        raise ValueError("covariance_estimator must be pooled, reference, or regularized")
    regularization_method = str(params.get("regularization_method", "diagonal_loading")).lower()
    if regularization_method not in {"diagonal_loading", "shrinkage"}:
        raise ValueError("regularization_method must be diagonal_loading or shrinkage")
    regularization_strength = float(
        params.get("regularization_strength", params.get("shrinkage_alpha", 1e-6))
    )
    if not np.isfinite(regularization_strength) or regularization_strength < 0.0:
        raise ValueError("regularization_strength must be a finite number >= 0")
    if variant_id == "REGULARIZED_HOTELLING_T2" and regularization_strength == 0.0:
        regularization_strength = 1e-3

    return {
        "feature_cols": feature_cols,
        "alpha": alpha,
        "control_limit": None if params.get("control_limit") is None else float(params["control_limit"]),
        "min_reference_size": _positive_int(params.get("min_reference_size", len(feature_cols) + 2), "min_reference_size"),
        "min_current_size": _positive_int(params.get("min_current_size", len(feature_cols) + 2), "min_current_size"),
        "covariance_estimator": covariance_estimator,
        "regularization_strength": regularization_strength,
        "regularization_method": regularization_method,
        "sample_imbalance_warning_ratio": float(params.get("sample_imbalance_warning_ratio", 10.0)),
        "condition_number_warning": float(params.get("condition_number_warning", 1e8)),
    }


def _resolve_mewma_params(params: dict[str, Any], value_col: str | None) -> dict[str, Any]:
    feature_cols = params.get("feature_cols", params.get("embedding_cols"))
    if feature_cols is None and value_col is not None:
        feature_cols = [value_col]
    if feature_cols is None:
        feature_cols = params.get("input_signal")
    if isinstance(feature_cols, str):
        feature_cols = [feature_cols]
    if not feature_cols:
        raise ValueError("MEWMA requires params['feature_cols'] or params['embedding_cols']")
    feature_cols = [str(col) for col in feature_cols]
    if len(feature_cols) < 2:
        raise ValueError("MEWMA requires at least two numeric feature columns")

    lambda_value = float(params.get("lambda", params.get("lambda_value", 0.2)))
    if not 0.0 < lambda_value <= 1.0:
        raise ValueError("lambda must be in (0, 1]")
    alpha = float(params.get("alpha", params.get("threshold_or_alpha", 0.01)))
    if not 0.0 < alpha < 1.0:
        raise ValueError("alpha must be in (0, 1)")
    covariance_estimator = str(params.get("covariance_estimator", "reference")).lower()
    if covariance_estimator not in {"reference", "regularized"}:
        raise ValueError("covariance_estimator must be reference or regularized")
    metric_scaling_policy = str(params.get("metric_scaling_policy", "covariance")).lower()
    if metric_scaling_policy != "covariance":
        raise ValueError("metric_scaling_policy must be 'covariance'")
    regularization_strength = float(params.get("regularization_strength", 1e-6))
    if not np.isfinite(regularization_strength) or regularization_strength < 0.0:
        raise ValueError("regularization_strength must be a finite number >= 0")
    return {
        "feature_cols": feature_cols,
        "lambda_value": lambda_value,
        "alpha": alpha,
        "control_limit": None if params.get("control_limit") is None else float(params["control_limit"]),
        "min_reference_size": _positive_int(params.get("min_reference_size", len(feature_cols) + 2), "min_reference_size"),
        "min_current_size": _positive_int(params.get("min_current_size", 20), "min_current_size"),
        "covariance_estimator": covariance_estimator,
        "regularization_strength": regularization_strength,
        "metric_scaling_policy": metric_scaling_policy,
        "condition_number_warning": float(params.get("condition_number_warning", 1e8)),
    }


def _resolve_mahalanobis_params(params: dict[str, Any], value_col: str | None, variant_id: str) -> dict[str, Any]:
    feature_cols = params.get("feature_cols", params.get("embedding_cols"))
    if feature_cols is None and value_col is not None:
        feature_cols = [value_col]
    if feature_cols is None:
        feature_cols = params.get("input_signal")
    if isinstance(feature_cols, str):
        feature_cols = [feature_cols]
    if not feature_cols:
        raise ValueError("Mahalanobis Distance requires params['feature_cols'] or params['embedding_cols']")
    feature_cols = [str(col) for col in feature_cols]
    if len(feature_cols) < 2:
        raise ValueError("Mahalanobis Distance requires at least two numeric feature columns")

    alpha = float(params.get("alpha", params.get("threshold_or_alpha", 0.01)))
    if not 0.0 < alpha < 1.0:
        raise ValueError("alpha must be in (0, 1)")
    threshold = params.get("threshold", params.get("control_limit"))
    threshold_policy = str(params.get("threshold_policy", "chi_square")).lower()
    if threshold_policy not in {"chi_square", "explicit"}:
        raise ValueError("threshold_policy must be chi_square or explicit")
    if threshold is not None:
        threshold = float(threshold)
        if threshold <= 0.0:
            raise ValueError("threshold/control_limit must be positive")
        threshold_policy = "explicit"
    elif threshold_policy == "explicit":
        raise ValueError("explicit threshold_policy requires threshold or control_limit")

    regularization_strength = float(params.get("regularization_strength", 1e-6))
    if not np.isfinite(regularization_strength) or regularization_strength < 0.0:
        raise ValueError("regularization_strength must be a finite number >= 0")
    outlier_fraction_threshold = float(params.get("outlier_fraction_threshold", 0.0))
    if not 0.0 <= outlier_fraction_threshold <= 1.0:
        raise ValueError("outlier_fraction_threshold must be in [0, 1]")

    min_current_default = 1 if variant_id == "SAMPLE_MAHALANOBIS_OUTLIER" else len(feature_cols) + 2
    return {
        "feature_cols": feature_cols,
        "alpha": alpha,
        "threshold": threshold,
        "threshold_policy": threshold_policy,
        "regularization_strength": regularization_strength,
        "outlier_fraction_threshold": outlier_fraction_threshold,
        "min_reference_size": _positive_int(params.get("min_reference_size", len(feature_cols) + 2), "min_reference_size"),
        "min_current_size": _positive_int(params.get("min_current_size", min_current_default), "min_current_size"),
        "condition_number_warning": float(params.get("condition_number_warning", 1e8)),
    }


def _prepare_multivariate_windows(
    data: pd.DataFrame,
    *,
    time_col: str,
    feature_cols: list[str],
    reference_window: tuple[str, str] | None,
    current_window: tuple[str, str] | None,
    min_reference_size: int,
    min_current_size: int,
) -> dict[str, Any]:
    if reference_window is None or current_window is None:
        raise ValueError("reference_window and current_window are required")
    if time_col not in data.columns:
        raise KeyError(f"missing time column: {time_col}")
    missing = [col for col in feature_cols if col not in data.columns]
    if missing:
        raise KeyError(f"missing feature columns: {missing}")
    ref_start, ref_end = _parse_window(reference_window, "reference_window")
    cur_start, cur_end = _parse_window(current_window, "current_window")
    if max(ref_start, cur_start) <= min(ref_end, cur_end):
        raise ValueError("reference_window and current_window must not overlap")

    frame = data[[time_col, *feature_cols]].copy()
    original_rows = len(frame)
    frame[time_col] = pd.to_datetime(frame[time_col], errors="coerce")
    invalid_time_rows = int(frame[time_col].isna().sum())
    invalid_numeric_rows = 0
    for col in feature_cols:
        frame[col] = pd.to_numeric(frame[col], errors="coerce")
    values = frame[feature_cols].to_numpy(dtype=float)
    invalid_numeric_rows = int((~np.isfinite(values)).any(axis=1).sum())
    frame = frame.dropna(subset=[time_col, *feature_cols])
    values = frame[feature_cols].to_numpy(dtype=float)
    frame = frame[np.isfinite(values).all(axis=1)].sort_values(time_col)

    reference_frame = frame[(frame[time_col] >= ref_start) & (frame[time_col] <= ref_end)]
    current_frame = frame[(frame[time_col] >= cur_start) & (frame[time_col] <= cur_end)]
    if len(reference_frame) < min_reference_size:
        raise ValueError(
            f"reference sample size {len(reference_frame)} is below min_reference_size {min_reference_size}"
        )
    if len(current_frame) < min_current_size:
        raise ValueError(f"current sample size {len(current_frame)} is below min_current_size {min_current_size}")
    warnings: list[str] = []
    if invalid_time_rows:
        warnings.append(f"dropped {invalid_time_rows} rows with invalid timestamps")
    if invalid_numeric_rows:
        warnings.append(f"dropped {invalid_numeric_rows} rows with non-finite feature values")
    return {
        "reference_values": reference_frame[feature_cols].to_numpy(dtype=float),
        "current_values": current_frame[feature_cols].to_numpy(dtype=float),
        "warnings": warnings,
        "metadata": {
            "original_rows": original_rows,
            "valid_rows": int(len(frame)),
            "invalid_time_rows": invalid_time_rows,
            "invalid_numeric_rows": invalid_numeric_rows,
            "reference_window": [ref_start.isoformat(), ref_end.isoformat()],
            "current_window": [cur_start.isoformat(), cur_end.isoformat()],
        },
    }


def _run_mahalanobis_distance(
    reference: np.ndarray,
    current: np.ndarray,
    variant_id: str,
    resolved: dict[str, Any],
) -> dict[str, Any]:
    _, p = reference.shape
    robust = variant_id == "ROBUST_MAHALANOBIS"
    if robust:
        center = np.median(reference, axis=0)
        mad = np.median(np.abs(reference - center), axis=0) / 0.6744897501960817
        variance = np.square(np.maximum(mad, 1e-12))
        cov = np.diag(variance)
        method_policy = "robust_median_mad_diagonal_covariance"
        regularized = False
    else:
        center = np.mean(reference, axis=0)
        cov = np.cov(reference, rowvar=False, ddof=1)
        method_policy = "reference_covariance_sample_distance"
        regularized = resolved["regularization_strength"] > 0.0
        if regularized:
            cov = _regularize_covariance(cov, resolved["regularization_strength"], "diagonal_loading")
            method_policy = "regularized_reference_covariance"

    condition_number = _condition_number(cov)
    inv_cov = np.linalg.pinv(cov)
    control_limit = resolved["threshold"]
    if control_limit is None:
        control_limit = float(chi2.ppf(1.0 - resolved["alpha"], p))

    sample_d2 = np.array([float((row - center).T @ inv_cov @ (row - center)) for row in current])
    if not np.all(np.isfinite(sample_d2)):
        raise ValueError("Mahalanobis distance produced non-finite values")
    sample_distances = np.sqrt(np.maximum(sample_d2, 0.0))
    sample_outliers = sample_d2 > control_limit
    outlier_count = int(np.sum(sample_outliers))
    outlier_fraction = float(outlier_count / len(current))

    if variant_id == "WINDOW_MEAN_MAHALANOBIS":
        current_center = np.mean(current, axis=0)
        diff = current_center - center
        d2 = float(diff.T @ inv_cov @ diff)
        method_policy = "reference_covariance_window_mean_distance" if not regularized else method_policy
        threshold_exceedance = d2 > control_limit
    else:
        current_center = np.mean(current, axis=0)
        d2 = float(np.max(sample_d2))
        if resolved["outlier_fraction_threshold"] > 0.0:
            threshold_exceedance = outlier_fraction >= resolved["outlier_fraction_threshold"]
        else:
            threshold_exceedance = bool(sample_outliers.any())

    distance = float(np.sqrt(max(d2, 0.0)))
    p_value = float(chi2.sf(d2, p))
    return {
        "mahalanobis_distance": distance,
        "mahalanobis_d2": d2,
        "sample_distances": sample_distances,
        "p_value": p_value,
        "control_limit": float(control_limit),
        "threshold_exceedance": threshold_exceedance,
        "outlier_count": outlier_count,
        "outlier_fraction": outlier_fraction,
        "method_policy": method_policy,
        "reference_center": center,
        "current_center": current_center,
        "regularized": regularized,
        "robust": robust,
        "condition_number": condition_number,
    }


def _run_hotelling_t2(reference: np.ndarray, current: np.ndarray, variant_id: str, resolved: dict[str, Any]) -> dict[str, Any]:
    n_ref, p = reference.shape
    n_cur = current.shape[0]
    mean_ref = np.mean(reference, axis=0)
    mean_cur = np.mean(current, axis=0)
    diff = mean_cur - mean_ref
    regularized = variant_id == "REGULARIZED_HOTELLING_T2"

    if variant_id == "HOTELLING_T2_TWO_SAMPLE":
        cov = _pooled_covariance(reference, current)
        scale = n_ref * n_cur / (n_ref + n_cur)
        df2 = n_ref + n_cur - p - 1
        if df2 <= 0:
            raise ValueError("sample sizes are too small for Hotelling T2 two-sample F approximation")
        policy = "pooled_covariance_two_sample"
    else:
        cov = np.cov(reference, rowvar=False, ddof=1)
        scale = n_cur
        df2 = n_ref - p
        if df2 <= 0 and not regularized:
            raise ValueError("reference sample size must be greater than feature dimension")
        policy = "reference_covariance_phase_ii"

    if regularized:
        cov = _regularize_covariance(cov, resolved["regularization_strength"], resolved["regularization_method"])
        policy = f"regularized_{resolved['regularization_method']}"
    condition_number = _condition_number(cov)
    inv_cov = np.linalg.pinv(cov)
    t2 = float(scale * diff.T @ inv_cov @ diff)

    control_limit = resolved["control_limit"]
    p_value = None
    if variant_id == "HOTELLING_T2_TWO_SAMPLE":
        f_stat = (df2 / ((n_ref + n_cur - 2) * p)) * t2
        p_value = float(f.sf(f_stat, p, df2))
        if control_limit is None:
            control_limit = float(((n_ref + n_cur - 2) * p / df2) * f.ppf(1.0 - resolved["alpha"], p, df2))
    elif not regularized or n_ref > p:
        df2_eff = max(n_ref - p, 1)
        f_stat = (df2_eff / (p * (n_ref - 1))) * t2
        p_value = float(f.sf(f_stat, p, df2_eff))
        if control_limit is None:
            control_limit = float((p * (n_ref - 1) / df2_eff) * f.ppf(1.0 - resolved["alpha"], p, df2_eff))
    elif control_limit is None:
        control_limit = float(f.ppf(1.0 - resolved["alpha"], p, max(n_ref - 1, 1)) * p)

    return {
        "t2_statistic": t2,
        "p_value": p_value,
        "control_limit": control_limit,
        "mean_difference": diff,
        "method_policy": policy,
        "regularized": regularized,
        "condition_number": condition_number,
    }


def _run_mewma(reference: np.ndarray, current: np.ndarray, resolved: dict[str, Any]) -> dict[str, Any]:
    n_ref, p = reference.shape
    mean_ref = np.mean(reference, axis=0)
    cov = np.cov(reference, rowvar=False, ddof=1)
    regularized = resolved["covariance_estimator"] == "regularized" or resolved["regularization_strength"] > 0.0
    if regularized:
        cov = _regularize_covariance(cov, resolved["regularization_strength"], "diagonal_loading")
    condition_number = _condition_number(cov)
    inv_cov = np.linalg.pinv(cov)
    lambda_value = resolved["lambda_value"]
    z = mean_ref.copy()
    control_limit = resolved["control_limit"]
    if control_limit is None:
        control_limit = float(chi2.ppf(1.0 - resolved["alpha"], p))
    max_statistic = 0.0
    max_d2 = 0.0
    alarm_state = "normal"
    alarm_time = None
    alarm_index = None

    for index, row in enumerate(current):
        z = lambda_value * row + (1.0 - lambda_value) * z
        scale = lambda_value * (1.0 - (1.0 - lambda_value) ** (2 * (index + 1))) / (2.0 - lambda_value)
        diff = z - mean_ref
        mahalanobis_d2 = float(diff.T @ inv_cov @ diff)
        statistic = float(mahalanobis_d2 / max(scale, 1e-12))
        if statistic > max_statistic:
            max_statistic = statistic
            max_d2 = mahalanobis_d2
        if statistic > control_limit:
            alarm_state = "drift_detected"
            alarm_index = index
            break

    return {
        "mewma_statistic": float(max_statistic),
        "mahalanobis_d2": float(max_d2),
        "control_limit": float(control_limit),
        "alarm_state": alarm_state,
        "alarm_time": alarm_time,
        "alarm_index": alarm_index,
        "final_ewma_vector": z,
        "reference_mean": mean_ref,
        "regularized": regularized,
        "condition_number": condition_number,
    }


def _pooled_covariance(reference: np.ndarray, current: np.ndarray) -> np.ndarray:
    n_ref = reference.shape[0]
    n_cur = current.shape[0]
    cov_ref = np.cov(reference, rowvar=False, ddof=1)
    cov_cur = np.cov(current, rowvar=False, ddof=1)
    return ((n_ref - 1) * cov_ref + (n_cur - 1) * cov_cur) / (n_ref + n_cur - 2)


def _regularize_covariance(cov: np.ndarray, strength: float, method: str) -> np.ndarray:
    if method == "shrinkage":
        diag = np.diag(np.diag(cov))
        return (1.0 - strength) * cov + strength * diag
    scale = float(np.trace(cov) / cov.shape[0]) if cov.shape[0] else 1.0
    return cov + strength * max(scale, 1e-12) * np.eye(cov.shape[0])


def _condition_number(cov: np.ndarray) -> float | None:
    try:
        return float(np.linalg.cond(cov))
    except np.linalg.LinAlgError:
        return None


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


def _positive_int(value: Any, name: str) -> int:
    parsed = int(value)
    if parsed <= 0:
        raise ValueError(f"{name} must be a positive integer")
    return parsed


def _hotelling_interpretation(
    *,
    variant_id: str,
    n_ref: int,
    n_cur: int,
    dimension: int,
    t2_statistic: float,
    p_value: float | None,
    control_limit: float | None,
    alpha: float,
    alarm_state: str,
    regularized: bool,
) -> str:
    p_text = "not computed" if p_value is None else f"{p_value:.6g}"
    limit_text = "not supplied" if control_limit is None else f"{control_limit:.6g}"
    regularized_text = " Regularized covariance was used." if regularized else ""
    return (
        f"{variant_id} compared {n_ref} reference rows and {n_cur} current rows across {dimension} features. "
        f"Hotelling T2={t2_statistic:.6g}, p-value={p_text}, control_limit={limit_text}, "
        f"alpha={alpha:.6g}; alarm_state={alarm_state}.{regularized_text}"
    )


def _mewma_interpretation(
    *,
    variant_id: str,
    n_ref: int,
    n_cur: int,
    dimension: int,
    statistic: float,
    control_limit: float,
    alarm_state: str,
    lambda_value: float,
    regularized: bool,
) -> str:
    regularized_text = " Regularized covariance was used." if regularized else ""
    return (
        f"{variant_id} monitored {n_cur} current rows against {n_ref} reference rows across {dimension} features. "
        f"lambda={lambda_value:.6g}, MEWMA statistic={statistic:.6g}, "
        f"control_limit={control_limit:.6g}; alarm_state={alarm_state}.{regularized_text}"
    )


def _mahalanobis_interpretation(
    *,
    variant_id: str,
    n_ref: int,
    n_cur: int,
    dimension: int,
    distance: float,
    d2: float,
    control_limit: float,
    p_value: float,
    outlier_fraction: float,
    alarm_state: str,
    robust: bool,
) -> str:
    robust_text = " Robust median/MAD covariance was used." if robust else ""
    return (
        f"{variant_id} compared {n_cur} current rows against {n_ref} reference rows across {dimension} features. "
        f"Mahalanobis distance={distance:.6g}, D2={d2:.6g}, p-value={p_value:.6g}, "
        f"control_limit(D2)={control_limit:.6g}, outlier_fraction={outlier_fraction:.6g}; "
        f"alarm_state={alarm_state}.{robust_text}"
    )


def _hotelling_not_applicable(
    variant_id: str | None,
    warning: str,
    metadata: dict[str, Any] | None = None,
    prior_warnings: list[str] | None = None,
) -> DriftResult:
    result = not_applicable_result(
        method_id=HOTELLING_T2_METHOD_ID,
        method_name=HOTELLING_T2_METHOD_NAME,
        method_category=HOTELLING_T2_METHOD_CATEGORY,
        variant_id=variant_id,
        warning=warning,
        metadata=metadata,
    )
    if prior_warnings:
        result.warnings = prior_warnings + result.warnings
    return result


def _mahalanobis_not_applicable(
    variant_id: str | None,
    warning: str,
    metadata: dict[str, Any] | None = None,
    prior_warnings: list[str] | None = None,
) -> DriftResult:
    result = not_applicable_result(
        method_id=MAHALANOBIS_METHOD_ID,
        method_name=MAHALANOBIS_METHOD_NAME,
        method_category=MAHALANOBIS_METHOD_CATEGORY,
        variant_id=variant_id,
        warning=warning,
        metadata=metadata,
    )
    if prior_warnings:
        result.warnings = prior_warnings + result.warnings
    return result


def _mewma_not_applicable(
    variant_id: str | None,
    warning: str,
    metadata: dict[str, Any] | None = None,
    prior_warnings: list[str] | None = None,
) -> DriftResult:
    result = not_applicable_result(
        method_id=MEWMA_METHOD_ID,
        method_name=MEWMA_METHOD_NAME,
        method_category=MEWMA_METHOD_CATEGORY,
        variant_id=variant_id,
        warning=warning,
        metadata=metadata,
    )
    if prior_warnings:
        result.warnings = prior_warnings + result.warnings
    return result
