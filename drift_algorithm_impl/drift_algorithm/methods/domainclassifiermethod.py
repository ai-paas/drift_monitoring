from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
from scipy.stats import ks_2samp

from drift_algorithm.core.result import DriftResult, not_applicable_result


CLASSIFIER_EMBEDDING_METHOD_ID = "DM-053"
CLASSIFIER_EMBEDDING_METHOD_NAME = "Classifier 기반 embedding drift detection"
CLASSIFIER_EMBEDDING_METHOD_CATEGORY = "DomainClassifierMethod"
TEXT_DOMAIN_CLASSIFIER_METHOD_ID = "DM-054"
TEXT_DOMAIN_CLASSIFIER_METHOD_NAME = "Text Domain Classifier Drift"
TEXT_DOMAIN_CLASSIFIER_METHOD_CATEGORY = "DomainClassifierMethod"

SUPPORTED_CLASSIFIER_EMBEDDING_VARIANTS = {
    "DOMAIN_CLASSIFIER_ROC_AUC",
    "DOMAIN_CLASSIFIER_PROBABILITY_DRIFT",
    "CROSS_VALIDATED_DOMAIN_CLASSIFIER",
}
SUPPORTED_TEXT_DOMAIN_CLASSIFIER_VARIANTS = {
    "TEXT_DOMAIN_CLASSIFIER_ROC_AUC",
    "TEXT_DOMAIN_CLASSIFIER_STAT_TEST",
    "TEXT_DESCRIPTOR_DRIFT",
}


def detect_classifier_embedding_drift_detection(
    data: pd.DataFrame,
    *,
    time_col: str = "time",
    value_col: str | None = None,
    reference_window: tuple[str, str] | None = None,
    current_window: tuple[str, str] | None = None,
    params: dict[str, Any] | None = None,
) -> DriftResult:
    params = dict(params or {})
    variant_id = str(params.get("variant_id", "DOMAIN_CLASSIFIER_ROC_AUC")).upper()
    metadata: dict[str, Any] = {"params": params}

    if variant_id not in SUPPORTED_CLASSIFIER_EMBEDDING_VARIANTS:
        return _classifier_embedding_not_applicable(
            variant_id,
            f"unsupported Classifier Embedding Drift variant: {variant_id}",
            metadata,
        )

    try:
        resolved = _resolve_classifier_embedding_params(params, value_col, variant_id)
        prepared = _prepare_embedding_windows(
            data,
            time_col=time_col,
            embedding_cols=resolved["embedding_cols"],
            reference_window=reference_window,
            current_window=current_window,
            min_reference_size=resolved["min_reference_size"],
            min_current_size=resolved["min_current_size"],
        )
    except (KeyError, TypeError, ValueError) as exc:
        return _classifier_embedding_not_applicable(variant_id, str(exc), metadata)

    reference = prepared["reference_values"]
    current = prepared["current_values"]
    n_ref, p = reference.shape
    n_cur = current.shape[0]
    warnings = list(prepared["warnings"])
    metadata.update(prepared["metadata"])
    metadata.update(
        {
            "backend": "numpy_centroid_domain_classifier",
            "embedding_cols": resolved["embedding_cols"],
            "threshold_policy": resolved["threshold_policy"],
        }
    )
    warnings.append("Domain classifier uses a deterministic centroid-score surrogate, not a trained classifier")

    try:
        if variant_id == "DOMAIN_CLASSIFIER_ROC_AUC":
            run = _run_domain_classifier_auc(reference, current, resolved)
        elif variant_id == "DOMAIN_CLASSIFIER_PROBABILITY_DRIFT":
            run = _run_domain_classifier_probability_drift(reference, current, resolved)
        else:
            run = _run_cross_validated_domain_classifier(reference, current, resolved)
    except ValueError as exc:
        return _classifier_embedding_not_applicable(variant_id, str(exc), metadata, warnings)

    drift_detected = bool(run["drift_detected"])
    severity = "drift_detected" if drift_detected else "normal"
    measurements = {
        "ROC_AUC": run["roc_auc"],
        "DOMAIN_CLASSIFIER_SCORE": run["domain_classifier_score"],
        "TEST_STATISTIC": run["test_statistic"],
        "P_VALUE": run["p_value"],
        "DRIFT_ALARM_STATE": severity,
        "THRESHOLD": run["threshold"],
        "METHOD_POLICY": run["method_policy"],
        "REFERENCE_SAMPLE_SIZE": int(n_ref),
        "CURRENT_SAMPLE_SIZE": int(n_cur),
        "SAMPLE_SIZE": {"reference": int(n_ref), "current": int(n_cur)},
        "EMBEDDING_DIMENSION": int(p),
        "EMBEDDING_COLUMNS": resolved["embedding_cols"],
        "PROBABILITY_MEAN_REFERENCE": run["probability_mean_reference"],
        "PROBABILITY_MEAN_CURRENT": run["probability_mean_current"],
        "PROBABILITY_MEAN_DELTA": run["probability_mean_delta"],
        "HIGH_CURRENT_PROBABILITY_RATE": run["high_current_probability_rate"],
    }
    if run.get("fold_scores") is not None:
        measurements["CROSS_VALIDATION_FOLD_SCORES"] = run["fold_scores"]
        measurements["ROC_AUC_STD"] = run["roc_auc_std"]

    return DriftResult(
        method_id=CLASSIFIER_EMBEDDING_METHOD_ID,
        method_name=CLASSIFIER_EMBEDDING_METHOD_NAME,
        method_category=CLASSIFIER_EMBEDDING_METHOD_CATEGORY,
        variant_id=variant_id,
        drift_detected=drift_detected,
        severity=severity,
        drift_score=run["domain_classifier_score"],
        p_value=run["p_value"],
        test_statistic=run["test_statistic"],
        threshold=run["threshold"],
        measurements=measurements,
        interpretation=_classifier_embedding_interpretation(
            variant_id=variant_id,
            n_ref=n_ref,
            n_cur=n_cur,
            dimension=p,
            score=run["domain_classifier_score"],
            roc_auc=run["roc_auc"],
            p_value=run["p_value"],
            threshold=run["threshold"],
            alarm_state=severity,
            policy=run["method_policy"],
        ),
        warnings=warnings,
        metadata=metadata,
    )


def detect_text_domain_classifier_drift(
    data: pd.DataFrame,
    *,
    time_col: str = "time",
    value_col: str | None = None,
    reference_window: tuple[str, str] | None = None,
    current_window: tuple[str, str] | None = None,
    params: dict[str, Any] | None = None,
) -> DriftResult:
    params = dict(params or {})
    variant_id = str(params.get("variant_id", "TEXT_DOMAIN_CLASSIFIER_ROC_AUC")).upper()
    metadata: dict[str, Any] = {"params": params}

    if variant_id not in SUPPORTED_TEXT_DOMAIN_CLASSIFIER_VARIANTS:
        return _text_domain_not_applicable(
            variant_id,
            f"unsupported Text Domain Classifier Drift variant: {variant_id}",
            metadata,
        )

    try:
        resolved = _resolve_text_domain_params(params, value_col, variant_id)
        prepared = _prepare_text_domain_windows(
            data,
            time_col=time_col,
            resolved=resolved,
            reference_window=reference_window,
            current_window=current_window,
        )
    except (KeyError, TypeError, ValueError) as exc:
        return _text_domain_not_applicable(variant_id, str(exc), metadata)

    reference = prepared["reference_values"]
    current = prepared["current_values"]
    n_ref, p = reference.shape
    n_cur = current.shape[0]
    warnings = list(prepared["warnings"])
    metadata.update(prepared["metadata"])
    metadata.update(
        {
            "backend": "numpy_text_domain_classifier",
            "feature_source": prepared["feature_source"],
            "feature_columns": prepared["feature_columns"],
            "threshold_policy": resolved["threshold_policy"],
        }
    )
    if prepared["feature_source"] == "bag_of_words":
        warnings.append("Text domain classifier uses a deterministic bag-of-words centroid surrogate")

    try:
        if variant_id == "TEXT_DOMAIN_CLASSIFIER_ROC_AUC":
            run = _run_domain_classifier_auc(reference, current, resolved)
        elif variant_id == "TEXT_DOMAIN_CLASSIFIER_STAT_TEST":
            run = _run_domain_classifier_probability_drift(reference, current, resolved)
        else:
            run = _run_text_descriptor_drift(reference, current, resolved, prepared["feature_columns"])
    except ValueError as exc:
        return _text_domain_not_applicable(variant_id, str(exc), metadata, warnings)

    drift_detected = bool(run["drift_detected"])
    severity = "drift_detected" if drift_detected else "normal"
    measurements = {
        "ROC_AUC": run["roc_auc"],
        "DOMAIN_CLASSIFIER_SCORE": run["domain_classifier_score"],
        "TEXT_DOMAIN_CLASSIFIER_STATISTIC": run["test_statistic"],
        "TEST_STATISTIC": run["test_statistic"],
        "P_VALUE": run["p_value"],
        "DRIFT_ALARM_STATE": severity,
        "THRESHOLD": run["threshold"],
        "METHOD_POLICY": run["method_policy"],
        "REFERENCE_SAMPLE_SIZE": int(n_ref),
        "CURRENT_SAMPLE_SIZE": int(n_cur),
        "SAMPLE_SIZE": {"reference": int(n_ref), "current": int(n_cur)},
        "TEXT_FEATURE_DIMENSION": int(p),
        "TEXT_FEATURE_COLUMNS": prepared["feature_columns"],
        "PROBABILITY_MEAN_REFERENCE": run["probability_mean_reference"],
        "PROBABILITY_MEAN_CURRENT": run["probability_mean_current"],
        "PROBABILITY_MEAN_DELTA": run["probability_mean_delta"],
        "HIGH_CURRENT_PROBABILITY_RATE": run["high_current_probability_rate"],
    }
    if run.get("descriptor_drift") is not None:
        measurements["TEXT_DESCRIPTOR_DRIFT"] = run["descriptor_drift"]
        measurements["SIGNIFICANT_DESCRIPTORS"] = run["significant_descriptors"]

    return DriftResult(
        method_id=TEXT_DOMAIN_CLASSIFIER_METHOD_ID,
        method_name=TEXT_DOMAIN_CLASSIFIER_METHOD_NAME,
        method_category=TEXT_DOMAIN_CLASSIFIER_METHOD_CATEGORY,
        variant_id=variant_id,
        drift_detected=drift_detected,
        severity=severity,
        drift_score=run["domain_classifier_score"],
        p_value=run["p_value"],
        test_statistic=run["test_statistic"],
        threshold=run["threshold"],
        measurements=measurements,
        interpretation=_text_domain_interpretation(
            variant_id=variant_id,
            n_ref=n_ref,
            n_cur=n_cur,
            dimension=p,
            score=run["domain_classifier_score"],
            roc_auc=run["roc_auc"],
            p_value=run["p_value"],
            threshold=run["threshold"],
            alarm_state=severity,
            policy=run["method_policy"],
        ),
        warnings=warnings,
        metadata=metadata,
    )


def _resolve_classifier_embedding_params(
    params: dict[str, Any],
    value_col: str | None,
    variant_id: str,
) -> dict[str, Any]:
    embedding_cols = params.get("embedding_cols", params.get("feature_cols"))
    if embedding_cols is None and value_col is not None:
        embedding_cols = [value_col]
    if isinstance(embedding_cols, str):
        embedding_cols = [embedding_cols]
    if not embedding_cols:
        raise ValueError("Classifier Embedding Drift requires embedding_cols, feature_cols, or value_col")
    embedding_cols = [str(col) for col in embedding_cols]

    auc_threshold = float(params.get("auc_threshold", params.get("threshold", 0.75)))
    if not 0.5 <= auc_threshold <= 1.0:
        raise ValueError("auc_threshold must be between 0.5 and 1.0")
    alpha = float(params.get("alpha", params.get("threshold_or_alpha", 0.05)))
    if not 0.0 < alpha < 1.0:
        raise ValueError("alpha must be between 0 and 1")
    probability_threshold = float(params.get("probability_threshold", 0.7))
    if not 0.0 <= probability_threshold <= 1.0:
        raise ValueError("probability_threshold must be between 0 and 1")
    min_reference_size = int(params.get("min_reference_size", 20))
    min_current_size = int(params.get("min_current_size", 20))
    cv_folds = int(params.get("cv_folds", 3))
    min_fold_size = int(params.get("min_fold_size", 8))
    if min_reference_size < 1 or min_current_size < 1 or cv_folds < 2 or min_fold_size < 1:
        raise ValueError("minimum sample sizes and cv_folds must be positive")

    return {
        "embedding_cols": embedding_cols,
        "auc_threshold": auc_threshold,
        "alpha": alpha,
        "probability_threshold": probability_threshold,
        "min_reference_size": min_reference_size,
        "min_current_size": min_current_size,
        "cv_folds": cv_folds,
        "min_fold_size": min_fold_size,
        "threshold_policy": "ks_pvalue"
        if variant_id == "DOMAIN_CLASSIFIER_PROBABILITY_DRIFT"
        else "domain_classifier_auc",
    }


def _resolve_text_domain_params(params: dict[str, Any], value_col: str | None, variant_id: str) -> dict[str, Any]:
    text_col = params.get("text_col", value_col)
    embedding_cols = params.get("embedding_cols", params.get("feature_cols"))
    descriptor_cols = params.get("descriptor_cols")
    if isinstance(embedding_cols, str):
        embedding_cols = [embedding_cols]
    if isinstance(descriptor_cols, str):
        descriptor_cols = [descriptor_cols]
    if embedding_cols is not None:
        embedding_cols = [str(col) for col in embedding_cols]
    if descriptor_cols is not None:
        descriptor_cols = [str(col) for col in descriptor_cols]
    if text_col is not None:
        text_col = str(text_col)

    if variant_id in {"TEXT_DOMAIN_CLASSIFIER_ROC_AUC", "TEXT_DOMAIN_CLASSIFIER_STAT_TEST"}:
        if not text_col and not embedding_cols:
            raise ValueError(f"{variant_id} requires text_col, embedding_cols, feature_cols, or value_col")
    elif not descriptor_cols and not text_col:
        raise ValueError("TEXT_DESCRIPTOR_DRIFT requires descriptor_cols or text_col")

    auc_threshold = float(params.get("auc_threshold", params.get("threshold", 0.75)))
    if not 0.5 <= auc_threshold <= 1.0:
        raise ValueError("auc_threshold must be between 0.5 and 1.0")
    alpha = float(params.get("alpha", params.get("threshold_or_alpha", 0.05)))
    if not 0.0 < alpha < 1.0:
        raise ValueError("alpha must be between 0 and 1")
    probability_threshold = float(params.get("probability_threshold", 0.7))
    if not 0.0 <= probability_threshold <= 1.0:
        raise ValueError("probability_threshold must be between 0 and 1")
    min_reference_size = int(params.get("min_reference_size", 20))
    min_current_size = int(params.get("min_current_size", 20))
    max_features = int(params.get("max_features", 100))
    if min_reference_size < 1 or min_current_size < 1 or max_features < 1:
        raise ValueError("minimum sample sizes and max_features must be positive")

    return {
        "text_col": text_col,
        "embedding_cols": embedding_cols,
        "descriptor_cols": descriptor_cols,
        "auc_threshold": auc_threshold,
        "alpha": alpha,
        "probability_threshold": probability_threshold,
        "min_reference_size": min_reference_size,
        "min_current_size": min_current_size,
        "max_features": max_features,
        "threshold_policy": "ks_pvalue" if variant_id != "TEXT_DOMAIN_CLASSIFIER_ROC_AUC" else "domain_classifier_auc",
    }


def _prepare_embedding_windows(
    data: pd.DataFrame,
    *,
    time_col: str,
    embedding_cols: list[str],
    reference_window: tuple[str, str] | None,
    current_window: tuple[str, str] | None,
    min_reference_size: int,
    min_current_size: int,
) -> dict[str, Any]:
    if not isinstance(data, pd.DataFrame):
        raise TypeError("data must be a pandas DataFrame")
    required_cols = [time_col, *embedding_cols]
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

    for col in embedding_cols:
        frame[col] = pd.to_numeric(frame[col], errors="coerce")
    before_value_drop = len(frame)
    frame = frame.dropna(subset=embedding_cols)
    if len(frame) < before_value_drop:
        warnings.append(f"dropped {before_value_drop - len(frame)} rows with invalid embedding values")
    if frame.empty:
        raise ValueError("no valid embedding rows after cleaning")
    frame = frame.sort_values(time_col).reset_index(drop=True)

    reference, current = _split_embedding_windows(frame, time_col, reference_window, current_window)
    if len(reference) < min_reference_size:
        raise ValueError(f"reference sample size {len(reference)} is below min_reference_size {min_reference_size}")
    if len(current) < min_current_size:
        raise ValueError(f"current sample size {len(current)} is below min_current_size {min_current_size}")

    return {
        "reference_values": reference[embedding_cols].to_numpy(dtype=float),
        "current_values": current[embedding_cols].to_numpy(dtype=float),
        "warnings": warnings,
        "metadata": {
            "time_col": time_col,
            "reference_window": reference_window,
            "current_window": current_window,
        },
    }


def _prepare_text_domain_windows(
    data: pd.DataFrame,
    *,
    time_col: str,
    resolved: dict[str, Any],
    reference_window: tuple[str, str] | None,
    current_window: tuple[str, str] | None,
) -> dict[str, Any]:
    if not isinstance(data, pd.DataFrame):
        raise TypeError("data must be a pandas DataFrame")
    candidate_cols = [time_col]
    if resolved["text_col"] is not None:
        candidate_cols.append(resolved["text_col"])
    if resolved["embedding_cols"]:
        candidate_cols.extend(resolved["embedding_cols"])
    if resolved["descriptor_cols"]:
        candidate_cols.extend(resolved["descriptor_cols"])
    required_cols = list(dict.fromkeys(candidate_cols))
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
    if frame.empty:
        raise ValueError("no valid text-domain rows after cleaning")
    frame = frame.sort_values(time_col).reset_index(drop=True)
    reference, current = _split_embedding_windows(frame, time_col, reference_window, current_window)

    if len(reference) < resolved["min_reference_size"]:
        raise ValueError(f"reference sample size {len(reference)} is below min_reference_size {resolved['min_reference_size']}")
    if len(current) < resolved["min_current_size"]:
        raise ValueError(f"current sample size {len(current)} is below min_current_size {resolved['min_current_size']}")

    if resolved["descriptor_cols"]:
        feature_cols = resolved["descriptor_cols"]
        reference_values, current_values, value_warnings = _numeric_text_features(reference, current, feature_cols)
        feature_source = "descriptor_cols"
    elif resolved["embedding_cols"]:
        feature_cols = resolved["embedding_cols"]
        reference_values, current_values, value_warnings = _numeric_text_features(reference, current, feature_cols)
        feature_source = "embedding_cols"
    else:
        feature_cols, reference_values, current_values, value_warnings = _bag_of_words_features(
            reference[resolved["text_col"]],
            current[resolved["text_col"]],
            resolved["max_features"],
        )
        feature_source = "bag_of_words"
    warnings.extend(value_warnings)

    if reference_values.shape[0] < resolved["min_reference_size"]:
        raise ValueError(f"reference sample size {reference_values.shape[0]} is below min_reference_size {resolved['min_reference_size']}")
    if current_values.shape[0] < resolved["min_current_size"]:
        raise ValueError(f"current sample size {current_values.shape[0]} is below min_current_size {resolved['min_current_size']}")

    return {
        "reference_values": reference_values,
        "current_values": current_values,
        "warnings": warnings,
        "feature_source": feature_source,
        "feature_columns": feature_cols,
        "metadata": {
            "time_col": time_col,
            "reference_window": reference_window,
            "current_window": current_window,
        },
    }


def _numeric_text_features(
    reference: pd.DataFrame,
    current: pd.DataFrame,
    feature_cols: list[str],
) -> tuple[np.ndarray, np.ndarray, list[str]]:
    ref = reference[feature_cols].copy()
    cur = current[feature_cols].copy()
    for col in feature_cols:
        ref[col] = pd.to_numeric(ref[col], errors="coerce")
        cur[col] = pd.to_numeric(cur[col], errors="coerce")
    before_drop = len(ref) + len(cur)
    ref = ref.dropna(subset=feature_cols)
    cur = cur.dropna(subset=feature_cols)
    warnings: list[str] = []
    after_drop = len(ref) + len(cur)
    if after_drop < before_drop:
        warnings.append(f"dropped {before_drop - after_drop} rows with invalid text-domain numeric values")
    return ref.to_numpy(dtype=float), cur.to_numpy(dtype=float), warnings


def _bag_of_words_features(
    reference_text: pd.Series,
    current_text: pd.Series,
    max_features: int,
) -> tuple[list[str], np.ndarray, np.ndarray, list[str]]:
    ref_tokens = [_tokenize_text(value) for value in reference_text]
    cur_tokens = [_tokenize_text(value) for value in current_text]
    all_tokens: dict[str, int] = {}
    for tokens in [*ref_tokens, *cur_tokens]:
        for token in set(tokens):
            all_tokens[token] = all_tokens.get(token, 0) + 1
    vocab = [token for token, _ in sorted(all_tokens.items(), key=lambda item: (-item[1], item[0]))[:max_features]]
    if not vocab:
        raise ValueError("text_col contains no usable tokens")
    feature_cols = [f"token:{token}" for token in vocab]
    token_to_idx = {token: idx for idx, token in enumerate(vocab)}
    return feature_cols, _tokens_to_matrix(ref_tokens, token_to_idx), _tokens_to_matrix(cur_tokens, token_to_idx), []


def _tokenize_text(value: Any) -> list[str]:
    text = "" if pd.isna(value) else str(value).lower()
    tokens: list[str] = []
    current = []
    for char in text:
        if char.isalnum():
            current.append(char)
        elif current:
            token = "".join(current)
            if len(token) > 1:
                tokens.append(token)
            current = []
    if current:
        token = "".join(current)
        if len(token) > 1:
            tokens.append(token)
    return tokens


def _tokens_to_matrix(token_rows: list[list[str]], token_to_idx: dict[str, int]) -> np.ndarray:
    matrix = np.zeros((len(token_rows), len(token_to_idx)), dtype=float)
    for row_idx, tokens in enumerate(token_rows):
        for token in tokens:
            idx = token_to_idx.get(token)
            if idx is not None:
                matrix[row_idx, idx] += 1.0
        total = float(np.sum(matrix[row_idx]))
        if total > 0.0:
            matrix[row_idx] /= total
    return matrix


def _split_embedding_windows(
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


def _run_domain_classifier_auc(reference: np.ndarray, current: np.ndarray, resolved: dict[str, Any]) -> dict[str, Any]:
    scores = _centroid_domain_scores(reference, current)
    labels = _domain_labels(reference, current)
    roc_auc = _binary_auc(labels, scores)
    probs = _scores_to_probabilities(scores)
    mean_ref, mean_cur = _probability_means(probs, reference.shape[0])
    return _classifier_embedding_run(
        roc_auc=roc_auc,
        p_value=None,
        test_statistic=roc_auc,
        threshold=resolved["auc_threshold"],
        method_policy="centroid_domain_classifier_auc",
        drift_detected=roc_auc >= resolved["auc_threshold"],
        probability_mean_reference=mean_ref,
        probability_mean_current=mean_cur,
        high_rate=float(np.mean(probs[reference.shape[0] :] >= resolved["probability_threshold"])),
    )


def _run_domain_classifier_probability_drift(
    reference: np.ndarray,
    current: np.ndarray,
    resolved: dict[str, Any],
) -> dict[str, Any]:
    scores = _centroid_domain_scores(reference, current)
    labels = _domain_labels(reference, current)
    probs = _scores_to_probabilities(scores)
    ref_probs = probs[: reference.shape[0]]
    cur_probs = probs[reference.shape[0] :]
    result = ks_2samp(ref_probs, cur_probs, alternative="two-sided", method="asymp")
    roc_auc = _binary_auc(labels, scores)
    mean_ref, mean_cur = _probability_means(probs, reference.shape[0])
    return _classifier_embedding_run(
        roc_auc=roc_auc,
        p_value=float(result.pvalue),
        test_statistic=float(result.statistic),
        threshold=resolved["alpha"],
        method_policy="centroid_probability_ks_min_pvalue",
        drift_detected=float(result.pvalue) < resolved["alpha"],
        probability_mean_reference=mean_ref,
        probability_mean_current=mean_cur,
        high_rate=float(np.mean(cur_probs >= resolved["probability_threshold"])),
    )


def _run_text_descriptor_drift(
    reference: np.ndarray,
    current: np.ndarray,
    resolved: dict[str, Any],
    feature_cols: list[str],
) -> dict[str, Any]:
    stats: list[float] = []
    p_values: list[float] = []
    descriptor_drift: list[dict[str, Any]] = []
    for idx, feature in enumerate(feature_cols):
        result = ks_2samp(reference[:, idx], current[:, idx], alternative="two-sided", method="asymp")
        statistic = float(result.statistic)
        p_value = float(result.pvalue)
        stats.append(statistic)
        p_values.append(p_value)
        descriptor_drift.append(
            {
                "descriptor": feature,
                "rank": 0,
                "score": statistic,
                "p_value": p_value,
                "reference_mean": float(np.mean(reference[:, idx])),
                "current_mean": float(np.mean(current[:, idx])),
                "mean_delta": float(np.mean(current[:, idx]) - np.mean(reference[:, idx])),
            }
        )
    ranked = sorted(descriptor_drift, key=lambda item: (-item["score"], item["descriptor"]))
    for rank, item in enumerate(ranked, start=1):
        item["rank"] = rank
    min_p_value = float(np.min(p_values))
    max_statistic = float(np.max(stats))
    return {
        "roc_auc": float("nan"),
        "domain_classifier_score": max_statistic,
        "test_statistic": max_statistic,
        "p_value": min_p_value,
        "threshold": resolved["alpha"],
        "method_policy": "descriptor_feature_ks_min_pvalue",
        "drift_detected": min_p_value < resolved["alpha"],
        "probability_mean_reference": float("nan"),
        "probability_mean_current": float("nan"),
        "probability_mean_delta": float("nan"),
        "high_current_probability_rate": float("nan"),
        "descriptor_drift": ranked,
        "significant_descriptors": [item["descriptor"] for item in ranked if item["p_value"] < resolved["alpha"]],
    }


def _run_cross_validated_domain_classifier(
    reference: np.ndarray,
    current: np.ndarray,
    resolved: dict[str, Any],
) -> dict[str, Any]:
    folds = _blocked_fold_indices(reference.shape[0], current.shape[0], resolved["cv_folds"], resolved["min_fold_size"])
    fold_scores: list[dict[str, Any]] = []
    probs_full = np.empty(reference.shape[0] + current.shape[0], dtype=float)
    for fold_index, (ref_test, cur_test) in enumerate(folds, start=1):
        ref_train = np.setdiff1d(np.arange(reference.shape[0]), ref_test)
        cur_train = np.setdiff1d(np.arange(current.shape[0]), cur_test)
        if len(ref_train) < resolved["min_fold_size"] or len(cur_train) < resolved["min_fold_size"]:
            raise ValueError("not enough train rows for cross-validated domain classifier")
        test = np.vstack([reference[ref_test], current[cur_test]])
        labels = np.concatenate([np.zeros(len(ref_test), dtype=int), np.ones(len(cur_test), dtype=int)])
        scores = _centroid_domain_scores(reference[ref_train], current[cur_train], test_values=test)
        probs = _scores_to_probabilities(scores)
        probs_full[np.concatenate([ref_test, reference.shape[0] + cur_test])] = probs
        fold_auc = _binary_auc(labels, scores)
        fold_scores.append(
            {
                "fold": fold_index,
                "roc_auc": fold_auc,
                "test_sample_size": {"reference": int(len(ref_test)), "current": int(len(cur_test))},
            }
        )
    roc_values = np.array([item["roc_auc"] for item in fold_scores], dtype=float)
    roc_auc = float(np.mean(roc_values))
    mean_ref, mean_cur = _probability_means(probs_full, reference.shape[0])
    run = _classifier_embedding_run(
        roc_auc=roc_auc,
        p_value=None,
        test_statistic=roc_auc,
        threshold=resolved["auc_threshold"],
        method_policy="blocked_cross_validated_centroid_auc",
        drift_detected=roc_auc >= resolved["auc_threshold"],
        probability_mean_reference=mean_ref,
        probability_mean_current=mean_cur,
        high_rate=float(np.mean(probs_full[reference.shape[0] :] >= resolved["probability_threshold"])),
    )
    run["fold_scores"] = fold_scores
    run["roc_auc_std"] = float(np.std(roc_values, ddof=0))
    return run


def _classifier_embedding_run(
    *,
    roc_auc: float,
    p_value: float | None,
    test_statistic: float,
    threshold: float,
    method_policy: str,
    drift_detected: bool,
    probability_mean_reference: float,
    probability_mean_current: float,
    high_rate: float,
) -> dict[str, Any]:
    return {
        "roc_auc": float(roc_auc),
        "domain_classifier_score": float(test_statistic),
        "test_statistic": float(test_statistic),
        "p_value": p_value,
        "threshold": float(threshold),
        "method_policy": method_policy,
        "drift_detected": bool(drift_detected),
        "probability_mean_reference": float(probability_mean_reference),
        "probability_mean_current": float(probability_mean_current),
        "probability_mean_delta": float(probability_mean_current - probability_mean_reference),
        "high_current_probability_rate": float(high_rate),
    }


def _centroid_domain_scores(reference: np.ndarray, current: np.ndarray, test_values: np.ndarray | None = None) -> np.ndarray:
    ref_center = np.mean(reference, axis=0)
    cur_center = np.mean(current, axis=0)
    direction = cur_center - ref_center
    norm = float(np.linalg.norm(direction))
    if not np.isfinite(norm) or norm <= 0.0:
        if test_values is None:
            return np.zeros(reference.shape[0] + current.shape[0], dtype=float)
        return np.zeros(test_values.shape[0], dtype=float)
    matrix = np.vstack([reference, current]) if test_values is None else test_values
    midpoint = (ref_center + cur_center) / 2.0
    return ((matrix - midpoint) @ direction) / norm


def _scores_to_probabilities(scores: np.ndarray) -> np.ndarray:
    scale = float(np.std(scores))
    if not np.isfinite(scale) or scale <= 0.0:
        return np.full(scores.shape[0], 0.5, dtype=float)
    z = np.clip((scores - float(np.mean(scores))) / scale, -40.0, 40.0)
    return 1.0 / (1.0 + np.exp(-z))


def _domain_labels(reference: np.ndarray, current: np.ndarray) -> np.ndarray:
    return np.concatenate([np.zeros(reference.shape[0], dtype=int), np.ones(current.shape[0], dtype=int)])


def _probability_means(probs: np.ndarray, reference_size: int) -> tuple[float, float]:
    return float(np.mean(probs[:reference_size])), float(np.mean(probs[reference_size:]))


def _binary_auc(labels: np.ndarray, scores: np.ndarray) -> float:
    pos = scores[labels == 1]
    neg = scores[labels == 0]
    if len(pos) == 0 or len(neg) == 0:
        raise ValueError("AUC requires both reference and current rows")
    comparisons = (pos[:, None] > neg[None, :]).mean()
    ties = (pos[:, None] == neg[None, :]).mean()
    return float(comparisons + 0.5 * ties)


def _blocked_fold_indices(
    reference_size: int,
    current_size: int,
    cv_folds: int,
    min_fold_size: int,
) -> list[tuple[np.ndarray, np.ndarray]]:
    if reference_size < cv_folds * min_fold_size or current_size < cv_folds * min_fold_size:
        raise ValueError("not enough rows for requested cv_folds and min_fold_size")
    ref_indices = np.array_split(np.arange(reference_size), cv_folds)
    cur_indices = np.array_split(np.arange(current_size), cv_folds)
    folds = []
    for ref_fold, cur_fold in zip(ref_indices, cur_indices):
        if len(ref_fold) < min_fold_size or len(cur_fold) < min_fold_size:
            raise ValueError("fold sample size is below min_fold_size")
        folds.append((ref_fold, cur_fold))
    return folds


def _classifier_embedding_interpretation(
    *,
    variant_id: str,
    n_ref: int,
    n_cur: int,
    dimension: int,
    score: float,
    roc_auc: float,
    p_value: float | None,
    threshold: float,
    alarm_state: str,
    policy: str,
) -> str:
    p_value_text = "n/a" if p_value is None else f"{p_value:.6g}"
    return (
        f"{variant_id} compared {n_ref} reference and {n_cur} current embedding rows across {dimension} dimensions. "
        f"Domain classifier score={score:.6g}, ROC-AUC={roc_auc:.6g}, p_value={p_value_text}, "
        f"threshold={threshold:.6g}, policy={policy}. Alarm state is {alarm_state}."
    )


def _text_domain_interpretation(
    *,
    variant_id: str,
    n_ref: int,
    n_cur: int,
    dimension: int,
    score: float,
    roc_auc: float,
    p_value: float | None,
    threshold: float,
    alarm_state: str,
    policy: str,
) -> str:
    p_value_text = "n/a" if p_value is None else f"{p_value:.6g}"
    roc_text = "n/a" if np.isnan(roc_auc) else f"{roc_auc:.6g}"
    return (
        f"{variant_id} compared {n_ref} reference and {n_cur} current text rows across {dimension} text features. "
        f"Score={score:.6g}, ROC-AUC={roc_text}, p_value={p_value_text}, "
        f"threshold={threshold:.6g}, policy={policy}. Alarm state is {alarm_state}."
    )


def _classifier_embedding_not_applicable(
    variant_id: str | None,
    warning: str,
    metadata: dict[str, Any] | None = None,
    prior_warnings: list[str] | None = None,
) -> DriftResult:
    result = not_applicable_result(
        method_id=CLASSIFIER_EMBEDDING_METHOD_ID,
        method_name=CLASSIFIER_EMBEDDING_METHOD_NAME,
        method_category=CLASSIFIER_EMBEDDING_METHOD_CATEGORY,
        variant_id=variant_id,
        warning=warning,
        metadata=metadata,
    )
    if prior_warnings:
        result.warnings = [*prior_warnings, warning]
    return result


def _text_domain_not_applicable(
    variant_id: str | None,
    warning: str,
    metadata: dict[str, Any] | None = None,
    prior_warnings: list[str] | None = None,
) -> DriftResult:
    result = not_applicable_result(
        method_id=TEXT_DOMAIN_CLASSIFIER_METHOD_ID,
        method_name=TEXT_DOMAIN_CLASSIFIER_METHOD_NAME,
        method_category=TEXT_DOMAIN_CLASSIFIER_METHOD_CATEGORY,
        variant_id=variant_id,
        warning=warning,
        metadata=metadata,
    )
    if prior_warnings:
        result.warnings = [*prior_warnings, warning]
    return result


__all__ = ["detect_classifier_embedding_drift_detection", "detect_text_domain_classifier_drift"]
