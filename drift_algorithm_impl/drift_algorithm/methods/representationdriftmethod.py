from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
from scipy.stats import ks_2samp

from drift_algorithm.core.result import DriftResult, not_applicable_result


OCDD_METHOD_ID = "DM-045"
OCDD_METHOD_NAME = "OCDD"
OCDD_METHOD_CATEGORY = "RepresentationDriftMethod"
FEATURE_MAP_DRIFT_METHOD_ID = "DM-046"
FEATURE_MAP_DRIFT_METHOD_NAME = "Feature Map Drift"
FEATURE_MAP_DRIFT_METHOD_CATEGORY = "RepresentationDriftMethod"
AUTOENCODER_REPRESENTATION_METHOD_ID = "DM-047"
AUTOENCODER_REPRESENTATION_METHOD_NAME = "Autoencoder Representation Drift"
AUTOENCODER_REPRESENTATION_METHOD_CATEGORY = "RepresentationDriftMethod"
GRAPH_EMBEDDING_METHOD_ID = "DM-048"
GRAPH_EMBEDDING_METHOD_NAME = "Graph Embedding Drift"
GRAPH_EMBEDDING_METHOD_CATEGORY = "RepresentationDriftMethod"
LLM_QUERY_SEMANTIC_METHOD_ID = "DM-049"
LLM_QUERY_SEMANTIC_METHOD_NAME = "LLM Query / Semantic Distance 기반 감지"
LLM_QUERY_SEMANTIC_METHOD_CATEGORY = "RepresentationDriftMethod"
MODEL_UNCERTAINTY_METHOD_ID = "DM-050"
MODEL_UNCERTAINTY_METHOD_NAME = "Model Uncertainty Drift"
MODEL_UNCERTAINTY_METHOD_CATEGORY = "RepresentationDriftMethod"

SUPPORTED_OCDD_VARIANTS = {
    "ONE_CLASS_SVM_DRIFT",
    "ISOLATION_FOREST_DRIFT_SCORE",
    "AUTOENCODER_RECONSTRUCTION_DRIFT",
}
SUPPORTED_FEATURE_MAP_DRIFT_VARIANTS = {
    "MODEL_FEATURE_MAP_KS",
    "MODEL_FEATURE_MAP_MMD",
    "LAYERWISE_FEATURE_MAP_DRIFT",
}
SUPPORTED_AUTOENCODER_REPRESENTATION_VARIANTS = {
    "LATENT_SPACE_DRIFT",
    "RECONSTRUCTION_ERROR_DRIFT",
    "AUTOENCODER_DOMAIN_CLASSIFIER",
}
SUPPORTED_GRAPH_EMBEDDING_VARIANTS = {
    "GRAPH_EMBEDDING_MMD",
    "GRAPH_EMBEDDING_CENTROID_SHIFT",
    "NODE_REPRESENTATION_DRIFT",
}
SUPPORTED_LLM_QUERY_SEMANTIC_VARIANTS = {
    "QUERY_CENTROID_COSINE_SHIFT",
    "TEXT_DOMAIN_CLASSIFIER_DRIFT",
    "TOPIC_DISTRIBUTION_SHIFT",
}
SUPPORTED_MODEL_UNCERTAINTY_VARIANTS = {
    "SOFTMAX_CONFIDENCE_DRIFT",
    "ENTROPY_DRIFT",
    "PREDICTIVE_VARIANCE_DRIFT",
}


def detect_ocdd(
    data: pd.DataFrame,
    *,
    time_col: str = "time",
    value_col: str | None = None,
    reference_window: tuple[str, str] | None = None,
    current_window: tuple[str, str] | None = None,
    params: dict[str, Any] | None = None,
) -> DriftResult:
    params = dict(params or {})
    variant_id = str(params.get("variant_id", "ONE_CLASS_SVM_DRIFT")).upper()
    metadata: dict[str, Any] = {"params": params}

    if variant_id not in SUPPORTED_OCDD_VARIANTS:
        return _ocdd_not_applicable(variant_id, f"unsupported OCDD variant: {variant_id}", metadata)

    try:
        resolved = _resolve_ocdd_params(params, value_col, variant_id)
        prepared = _prepare_representation_windows(
            data,
            time_col=time_col,
            feature_cols=resolved["feature_cols"],
            reference_window=reference_window,
            current_window=current_window,
            min_reference_size=resolved["min_reference_size"],
            min_current_size=resolved["min_current_size"],
        )
    except (KeyError, TypeError, ValueError) as exc:
        return _ocdd_not_applicable(variant_id, str(exc), metadata)

    reference = prepared["reference_values"]
    current = prepared["current_values"]
    n_ref, p = reference.shape
    n_cur = current.shape[0]
    warnings = list(prepared["warnings"])
    metadata.update(prepared["metadata"])
    metadata.update(
        {
            "backend": "numpy_ocdd_surrogate",
            "feature_cols": resolved["feature_cols"],
            "alpha": resolved["alpha"],
            "threshold_policy": resolved["threshold_policy"],
        }
    )

    if params.get("threshold_or_alpha") is not None:
        warnings.append("threshold_or_alpha was interpreted as OCDD alpha")
    if variant_id in {"ONE_CLASS_SVM_DRIFT", "ISOLATION_FOREST_DRIFT_SCORE"}:
        warnings.append(f"{variant_id} uses a deterministic NumPy surrogate because scikit-learn is not required")
    if variant_id == "AUTOENCODER_RECONSTRUCTION_DRIFT":
        warnings.append("AUTOENCODER_RECONSTRUCTION_DRIFT uses a linear PCA reconstruction surrogate")

    try:
        run = _run_ocdd(reference, current, variant_id, resolved)
    except ValueError as exc:
        return _ocdd_not_applicable(variant_id, str(exc), metadata, warnings)

    drift_detected = bool(run["anomaly_rate"] > resolved["anomaly_rate_threshold"])
    severity = "drift_detected" if drift_detected else "normal"
    measurements = {
        "ANOMALY_SCORE": run["mean_anomaly_score"],
        "MAX_ANOMALY_SCORE": run["max_anomaly_score"],
        "OUTLIER_OR_ANOMALY_RATE": run["anomaly_rate"],
        "BOUNDARY_VIOLATION_RATE": run["anomaly_rate"],
        "RECONSTRUCTION_ERROR": run["mean_reconstruction_error"],
        "THRESHOLD": run["threshold"],
        "ANOMALY_RATE_THRESHOLD": resolved["anomaly_rate_threshold"],
        "THRESHOLD_EXCEEDANCE": drift_detected,
        "DRIFT_ALARM_STATE": "drift_detected" if drift_detected else "normal",
        "METHOD_POLICY": run["method_policy"],
        "SAMPLE_SIZE": {"reference": int(n_ref), "current": int(n_cur)},
        "SAMPLE_SIZE_REFERENCE": int(n_ref),
        "SAMPLE_SIZE_CURRENT": int(n_cur),
        "FEATURE_DIMENSION": int(p),
        "FEATURE_COLUMNS": resolved["feature_cols"],
        "ANOMALY_COUNT": run["anomaly_count"],
    }

    return DriftResult(
        method_id=OCDD_METHOD_ID,
        method_name=OCDD_METHOD_NAME,
        method_category=OCDD_METHOD_CATEGORY,
        variant_id=variant_id,
        drift_detected=drift_detected,
        severity=severity,
        drift_score=run["anomaly_rate"],
        p_value=None,
        test_statistic=run["mean_anomaly_score"],
        threshold=resolved["anomaly_rate_threshold"],
        measurements=measurements,
        interpretation=_ocdd_interpretation(
            variant_id=variant_id,
            n_ref=n_ref,
            n_cur=n_cur,
            dimension=p,
            mean_score=run["mean_anomaly_score"],
            score_threshold=run["threshold"],
            anomaly_rate=run["anomaly_rate"],
            rate_threshold=resolved["anomaly_rate_threshold"],
            alarm_state=measurements["DRIFT_ALARM_STATE"],
            policy=run["method_policy"],
        ),
        warnings=warnings,
        metadata=metadata,
    )


def detect_feature_map_drift(
    data: pd.DataFrame,
    *,
    time_col: str = "time",
    value_col: str | None = None,
    reference_window: tuple[str, str] | None = None,
    current_window: tuple[str, str] | None = None,
    params: dict[str, Any] | None = None,
) -> DriftResult:
    params = dict(params or {})
    variant_id = str(params.get("variant_id", "MODEL_FEATURE_MAP_KS")).upper()
    metadata: dict[str, Any] = {"params": params}

    if variant_id not in SUPPORTED_FEATURE_MAP_DRIFT_VARIANTS:
        return _feature_map_not_applicable(
            variant_id,
            f"unsupported Feature Map Drift variant: {variant_id}",
            metadata,
        )

    try:
        resolved = _resolve_feature_map_params(params, value_col, variant_id)
        prepared = _prepare_representation_windows(
            data,
            time_col=time_col,
            feature_cols=resolved["feature_cols"],
            reference_window=reference_window,
            current_window=current_window,
            min_reference_size=resolved["min_reference_size"],
            min_current_size=resolved["min_current_size"],
        )
    except (KeyError, TypeError, ValueError) as exc:
        return _feature_map_not_applicable(variant_id, str(exc), metadata)

    reference = prepared["reference_values"]
    current = prepared["current_values"]
    n_ref, p = reference.shape
    n_cur = current.shape[0]
    warnings = list(prepared["warnings"])
    metadata.update(prepared["metadata"])
    metadata.update(
        {
            "backend": "numpy_scipy_feature_map_drift",
            "feature_cols": resolved["feature_cols"],
            "alpha": resolved["alpha"],
            "threshold_policy": resolved["threshold_policy"],
            "model_layer": resolved["model_layer"],
            "feature_extractor_version": resolved["feature_extractor_version"],
        }
    )

    if params.get("threshold_or_alpha") is not None:
        warnings.append("threshold_or_alpha was interpreted as Feature Map Drift alpha")
    if variant_id == "MODEL_FEATURE_MAP_MMD" and resolved["permutation_count"] == 0:
        warnings.append("MMD p-value is not computed when permutation_count is 0")
    if variant_id == "LAYERWISE_FEATURE_MAP_DRIFT" and len(resolved["layer_feature_cols"]) <= 1:
        warnings.append("LAYERWISE_FEATURE_MAP_DRIFT received one layer; layerwise result is equivalent to a single layer score")

    try:
        run = _run_feature_map_drift(reference, current, variant_id, resolved)
    except ValueError as exc:
        return _feature_map_not_applicable(variant_id, str(exc), metadata, warnings)

    p_value = run["p_value"]
    if p_value is not None:
        drift_detected = bool(p_value < resolved["alpha"])
    else:
        drift_detected = bool(run["test_statistic"] > run["threshold"])
    severity = "drift_detected" if drift_detected else "normal"
    measurements = {
        "TEST_STATISTIC": run["test_statistic"],
        "P_VALUE": p_value,
        "DRIFT_ALARM_STATE": "drift_detected" if drift_detected else "normal",
        "THRESHOLD": run["threshold"],
        "METHOD_POLICY": run["method_policy"],
        "FEATURE_MAP_DRIFT_SCORE": run["test_statistic"],
        "MAX_FEATURE_STATISTIC": run["max_feature_statistic"],
        "SIGNIFICANT_FEATURE_COUNT": run["significant_feature_count"],
        "SIGNIFICANT_FEATURE_FRACTION": run["significant_feature_fraction"],
        "LAYERWISE_SCORES": run["layerwise_scores"],
        "SAMPLE_SIZE": {"reference": int(n_ref), "current": int(n_cur)},
        "SAMPLE_SIZE_REFERENCE": int(n_ref),
        "SAMPLE_SIZE_CURRENT": int(n_cur),
        "FEATURE_DIMENSION": int(p),
        "FEATURE_COLUMNS": resolved["feature_cols"],
    }

    return DriftResult(
        method_id=FEATURE_MAP_DRIFT_METHOD_ID,
        method_name=FEATURE_MAP_DRIFT_METHOD_NAME,
        method_category=FEATURE_MAP_DRIFT_METHOD_CATEGORY,
        variant_id=variant_id,
        drift_detected=drift_detected,
        severity=severity,
        drift_score=run["test_statistic"],
        p_value=p_value,
        test_statistic=run["test_statistic"],
        threshold=run["threshold"] if p_value is None else resolved["alpha"],
        measurements=measurements,
        interpretation=_feature_map_interpretation(
            variant_id=variant_id,
            n_ref=n_ref,
            n_cur=n_cur,
            dimension=p,
            statistic=run["test_statistic"],
            p_value=p_value,
            threshold=measurements["THRESHOLD"],
            alpha=resolved["alpha"],
            alarm_state=measurements["DRIFT_ALARM_STATE"],
            policy=run["method_policy"],
        ),
        warnings=warnings,
        metadata=metadata,
    )


def detect_autoencoder_representation_drift(
    data: pd.DataFrame,
    *,
    time_col: str = "time",
    value_col: str | None = None,
    reference_window: tuple[str, str] | None = None,
    current_window: tuple[str, str] | None = None,
    params: dict[str, Any] | None = None,
) -> DriftResult:
    params = dict(params or {})
    variant_id = str(params.get("variant_id", "LATENT_SPACE_DRIFT")).upper()
    metadata: dict[str, Any] = {"params": params}

    if variant_id not in SUPPORTED_AUTOENCODER_REPRESENTATION_VARIANTS:
        return _autoencoder_not_applicable(
            variant_id,
            f"unsupported Autoencoder Representation Drift variant: {variant_id}",
            metadata,
        )

    try:
        resolved = _resolve_autoencoder_params(params, value_col, variant_id)
        prepared = _prepare_representation_windows(
            data,
            time_col=time_col,
            feature_cols=resolved["feature_cols"],
            reference_window=reference_window,
            current_window=current_window,
            min_reference_size=resolved["min_reference_size"],
            min_current_size=resolved["min_current_size"],
        )
    except (KeyError, TypeError, ValueError) as exc:
        return _autoencoder_not_applicable(variant_id, str(exc), metadata)

    reference = prepared["reference_values"]
    current = prepared["current_values"]
    n_ref, p = reference.shape
    n_cur = current.shape[0]
    warnings = list(prepared["warnings"])
    metadata.update(prepared["metadata"])
    metadata.update(
        {
            "backend": "numpy_autoencoder_representation_drift",
            "feature_cols": resolved["feature_cols"],
            "alpha": resolved["alpha"],
            "threshold_policy": resolved["threshold_policy"],
            "encoder_version": resolved["encoder_version"],
            "scaling_policy": resolved["scaling_policy"],
        }
    )

    if params.get("threshold_or_alpha") is not None:
        warnings.append("threshold_or_alpha was interpreted as Autoencoder Representation Drift alpha")
    if variant_id == "RECONSTRUCTION_ERROR_DRIFT" and resolved["error_col"] is None:
        warnings.append("RECONSTRUCTION_ERROR_DRIFT uses a linear PCA reconstruction-error surrogate")
    if variant_id == "AUTOENCODER_DOMAIN_CLASSIFIER":
        warnings.append("AUTOENCODER_DOMAIN_CLASSIFIER uses a nearest-centroid domain separability surrogate")

    try:
        run = _run_autoencoder_representation_drift(reference, current, variant_id, resolved)
    except ValueError as exc:
        return _autoencoder_not_applicable(variant_id, str(exc), metadata, warnings)

    p_value = run["p_value"]
    if p_value is not None:
        drift_detected = bool(p_value < resolved["alpha"])
    else:
        drift_detected = bool(run["test_statistic"] > run["threshold"])
    severity = "drift_detected" if drift_detected else "normal"
    measurements = {
        "TEST_STATISTIC": run["test_statistic"],
        "P_VALUE": p_value,
        "DRIFT_ALARM_STATE": "drift_detected" if drift_detected else "normal",
        "THRESHOLD": run["threshold"],
        "METHOD_POLICY": run["method_policy"],
        "LATENT_DRIFT_SCORE": run["latent_drift_score"],
        "RECONSTRUCTION_ERROR": run["reconstruction_error"],
        "RECONSTRUCTION_ERROR_REFERENCE": run["reference_reconstruction_error"],
        "DOMAIN_CLASSIFIER_AUC": run["domain_classifier_auc"],
        "DOMAIN_CLASSIFIER_ACCURACY": run["domain_classifier_accuracy"],
        "DOMAIN_PROBABILITY_MEAN": run["domain_probability_mean"],
        "SAMPLE_SIZE": {"reference": int(n_ref), "current": int(n_cur)},
        "SAMPLE_SIZE_REFERENCE": int(n_ref),
        "SAMPLE_SIZE_CURRENT": int(n_cur),
        "FEATURE_DIMENSION": int(p),
        "FEATURE_COLUMNS": resolved["feature_cols"],
    }

    return DriftResult(
        method_id=AUTOENCODER_REPRESENTATION_METHOD_ID,
        method_name=AUTOENCODER_REPRESENTATION_METHOD_NAME,
        method_category=AUTOENCODER_REPRESENTATION_METHOD_CATEGORY,
        variant_id=variant_id,
        drift_detected=drift_detected,
        severity=severity,
        drift_score=run["test_statistic"],
        p_value=p_value,
        test_statistic=run["test_statistic"],
        threshold=run["threshold"] if p_value is None else resolved["alpha"],
        measurements=measurements,
        interpretation=_autoencoder_interpretation(
            variant_id=variant_id,
            n_ref=n_ref,
            n_cur=n_cur,
            dimension=p,
            statistic=run["test_statistic"],
            p_value=p_value,
            threshold=measurements["THRESHOLD"],
            alpha=resolved["alpha"],
            alarm_state=measurements["DRIFT_ALARM_STATE"],
            policy=run["method_policy"],
        ),
        warnings=warnings,
        metadata=metadata,
    )


def detect_graph_embedding_drift(
    data: pd.DataFrame,
    *,
    time_col: str = "time",
    value_col: str | None = None,
    reference_window: tuple[str, str] | None = None,
    current_window: tuple[str, str] | None = None,
    params: dict[str, Any] | None = None,
) -> DriftResult:
    params = dict(params or {})
    variant_id = str(params.get("variant_id", "GRAPH_EMBEDDING_MMD")).upper()
    metadata: dict[str, Any] = {"params": params}

    if variant_id not in SUPPORTED_GRAPH_EMBEDDING_VARIANTS:
        return _graph_embedding_not_applicable(
            variant_id,
            f"unsupported Graph Embedding Drift variant: {variant_id}",
            metadata,
        )

    try:
        resolved = _resolve_graph_embedding_params(params, value_col, variant_id)
        prepared = _prepare_representation_windows(
            data,
            time_col=time_col,
            feature_cols=resolved["feature_cols"],
            group_col=resolved["node_group_col"],
            reference_window=reference_window,
            current_window=current_window,
            min_reference_size=resolved["min_reference_size"],
            min_current_size=resolved["min_current_size"],
        )
    except (KeyError, TypeError, ValueError) as exc:
        return _graph_embedding_not_applicable(variant_id, str(exc), metadata)

    reference = prepared["reference_values"]
    current = prepared["current_values"]
    n_ref, p = reference.shape
    n_cur = current.shape[0]
    warnings = list(prepared["warnings"])
    metadata.update(prepared["metadata"])
    metadata.update(
        {
            "backend": "numpy_graph_embedding_drift",
            "feature_cols": resolved["feature_cols"],
            "alpha": resolved["alpha"],
            "threshold_policy": resolved["threshold_policy"],
            "graph_embedding_model": resolved["graph_embedding_model"],
            "node_or_graph_level": resolved["node_or_graph_level"],
            "sampling_policy": resolved["sampling_policy"],
        }
    )

    if params.get("threshold_or_alpha") is not None:
        warnings.append("threshold_or_alpha was interpreted as Graph Embedding Drift alpha")
    if variant_id == "GRAPH_EMBEDDING_MMD" and resolved["permutation_count"] == 0:
        warnings.append("MMD p-value is not computed when permutation_count is 0")
    if variant_id == "NODE_REPRESENTATION_DRIFT" and resolved["node_group_col"] is None:
        warnings.append("NODE_REPRESENTATION_DRIFT used row-level distance because node_group_col was not supplied")

    try:
        run = _run_graph_embedding_drift(
            reference,
            current,
            prepared.get("reference_groups"),
            prepared.get("current_groups"),
            variant_id,
            resolved,
        )
    except ValueError as exc:
        return _graph_embedding_not_applicable(variant_id, str(exc), metadata, warnings)

    p_value = run["p_value"]
    if p_value is not None:
        drift_detected = bool(p_value < resolved["alpha"])
    else:
        drift_detected = bool(run["test_statistic"] > run["threshold"])
    severity = "drift_detected" if drift_detected else "normal"
    measurements = {
        "TEST_STATISTIC": run["test_statistic"],
        "P_VALUE": p_value,
        "DRIFT_ALARM_STATE": "drift_detected" if drift_detected else "normal",
        "THRESHOLD": run["threshold"],
        "METHOD_POLICY": run["method_policy"],
        "GRAPH_EMBEDDING_DRIFT_SCORE": run["test_statistic"],
        "CENTROID_SHIFT": run["centroid_shift"],
        "COSINE_DISTANCE": run["cosine_distance"],
        "NODE_GROUP_SCORES": run["node_group_scores"],
        "TOP_NODE_GROUP": run["top_node_group"],
        "SAMPLE_SIZE": {"reference": int(n_ref), "current": int(n_cur)},
        "SAMPLE_SIZE_REFERENCE": int(n_ref),
        "SAMPLE_SIZE_CURRENT": int(n_cur),
        "FEATURE_DIMENSION": int(p),
        "FEATURE_COLUMNS": resolved["feature_cols"],
    }

    return DriftResult(
        method_id=GRAPH_EMBEDDING_METHOD_ID,
        method_name=GRAPH_EMBEDDING_METHOD_NAME,
        method_category=GRAPH_EMBEDDING_METHOD_CATEGORY,
        variant_id=variant_id,
        drift_detected=drift_detected,
        severity=severity,
        drift_score=run["test_statistic"],
        p_value=p_value,
        test_statistic=run["test_statistic"],
        threshold=run["threshold"] if p_value is None else resolved["alpha"],
        measurements=measurements,
        interpretation=_graph_embedding_interpretation(
            variant_id=variant_id,
            n_ref=n_ref,
            n_cur=n_cur,
            dimension=p,
            statistic=run["test_statistic"],
            p_value=p_value,
            threshold=measurements["THRESHOLD"],
            alpha=resolved["alpha"],
            alarm_state=measurements["DRIFT_ALARM_STATE"],
            policy=run["method_policy"],
        ),
        warnings=warnings,
        metadata=metadata,
    )


def detect_llm_query_semantic_distance(
    data: pd.DataFrame,
    *,
    time_col: str = "time",
    value_col: str | None = None,
    reference_window: tuple[str, str] | None = None,
    current_window: tuple[str, str] | None = None,
    params: dict[str, Any] | None = None,
) -> DriftResult:
    params = dict(params or {})
    variant_id = str(params.get("variant_id", "QUERY_CENTROID_COSINE_SHIFT")).upper()
    metadata: dict[str, Any] = {"params": params}

    if variant_id not in SUPPORTED_LLM_QUERY_SEMANTIC_VARIANTS:
        return _llm_query_not_applicable(
            variant_id,
            f"unsupported LLM Query / Semantic Distance variant: {variant_id}",
            metadata,
        )

    try:
        resolved = _resolve_llm_query_params(params, value_col, variant_id)
        if variant_id == "TOPIC_DISTRIBUTION_SHIFT":
            prepared = _prepare_topic_distribution_windows(
                data,
                time_col=time_col,
                topic_col=resolved["topic_col"],
                count_col=resolved["count_col"],
                reference_window=reference_window,
                current_window=current_window,
                min_reference_size=resolved["min_reference_size"],
                min_current_size=resolved["min_current_size"],
            )
        else:
            prepared = _prepare_representation_windows(
                data,
                time_col=time_col,
                feature_cols=resolved["feature_cols"],
                reference_window=reference_window,
                current_window=current_window,
                min_reference_size=resolved["min_reference_size"],
                min_current_size=resolved["min_current_size"],
            )
    except (KeyError, TypeError, ValueError) as exc:
        return _llm_query_not_applicable(variant_id, str(exc), metadata)

    warnings = list(prepared["warnings"])
    metadata.update(prepared["metadata"])
    metadata.update(
        {
            "backend": "numpy_llm_query_semantic_distance",
            "alpha": resolved["alpha"],
            "threshold_policy": resolved["threshold_policy"],
            "embedding_model": resolved["embedding_model"],
            "embedding_version": resolved["embedding_version"],
            "topic_model": resolved["topic_model"],
        }
    )
    if params.get("threshold_or_alpha") is not None:
        warnings.append("threshold_or_alpha was interpreted as LLM semantic distance alpha")
    if variant_id == "TEXT_DOMAIN_CLASSIFIER_DRIFT":
        warnings.append("TEXT_DOMAIN_CLASSIFIER_DRIFT uses a nearest-centroid domain separability surrogate")

    try:
        if variant_id == "TOPIC_DISTRIBUTION_SHIFT":
            run = _run_topic_distribution_shift(prepared, resolved)
            n_ref = prepared["sample_size_reference"]
            n_cur = prepared["sample_size_current"]
            dimension = len(prepared["topics"])
        else:
            reference = prepared["reference_values"]
            current = prepared["current_values"]
            n_ref, dimension = reference.shape
            n_cur = current.shape[0]
            run = _run_llm_query_semantic_distance(reference, current, variant_id, resolved)
    except ValueError as exc:
        return _llm_query_not_applicable(variant_id, str(exc), metadata, warnings)

    p_value = run["p_value"]
    drift_detected = bool(run["test_statistic"] > run["threshold"]) if p_value is None else bool(p_value < resolved["alpha"])
    severity = "drift_detected" if drift_detected else "normal"
    measurements = {
        "TEST_STATISTIC": run["test_statistic"],
        "P_VALUE": p_value,
        "DRIFT_ALARM_STATE": "drift_detected" if drift_detected else "normal",
        "THRESHOLD": run["threshold"],
        "METHOD_POLICY": run["method_policy"],
        "COSINE_DISTANCE": run["cosine_distance"],
        "CENTROID_SHIFT": run["centroid_shift"],
        "ROC_AUC": run["roc_auc"],
        "CLASSIFIER_CONFIDENCE": run["classifier_confidence"],
        "JENSEN_SHANNON_DISTANCE": run["jensen_shannon_distance"],
        "TOPIC_PROPORTION_DELTA": run["topic_proportion_delta"],
        "TOPIC_PROPORTIONS_REFERENCE": run["topic_proportions_reference"],
        "TOPIC_PROPORTIONS_CURRENT": run["topic_proportions_current"],
        "SAMPLE_SIZE": {"reference": int(n_ref), "current": int(n_cur)},
        "SAMPLE_SIZE_REFERENCE": int(n_ref),
        "SAMPLE_SIZE_CURRENT": int(n_cur),
        "FEATURE_DIMENSION": int(dimension),
        "FEATURE_COLUMNS": resolved["feature_cols"],
    }

    return DriftResult(
        method_id=LLM_QUERY_SEMANTIC_METHOD_ID,
        method_name=LLM_QUERY_SEMANTIC_METHOD_NAME,
        method_category=LLM_QUERY_SEMANTIC_METHOD_CATEGORY,
        variant_id=variant_id,
        drift_detected=drift_detected,
        severity=severity,
        drift_score=run["test_statistic"],
        p_value=p_value,
        test_statistic=run["test_statistic"],
        threshold=run["threshold"] if p_value is None else resolved["alpha"],
        measurements=measurements,
        interpretation=_llm_query_interpretation(
            variant_id=variant_id,
            n_ref=n_ref,
            n_cur=n_cur,
            dimension=dimension,
            statistic=run["test_statistic"],
            threshold=run["threshold"],
            alarm_state=measurements["DRIFT_ALARM_STATE"],
            policy=run["method_policy"],
        ),
        warnings=warnings,
        metadata=metadata,
    )


def detect_model_uncertainty_drift(
    data: pd.DataFrame,
    *,
    time_col: str = "time",
    value_col: str | None = None,
    reference_window: tuple[str, str] | None = None,
    current_window: tuple[str, str] | None = None,
    params: dict[str, Any] | None = None,
) -> DriftResult:
    params = dict(params or {})
    variant_id = str(params.get("variant_id", "SOFTMAX_CONFIDENCE_DRIFT")).upper()
    metadata: dict[str, Any] = {"params": params}

    if variant_id not in SUPPORTED_MODEL_UNCERTAINTY_VARIANTS:
        return _model_uncertainty_not_applicable(
            variant_id,
            f"unsupported Model Uncertainty Drift variant: {variant_id}",
            metadata,
        )

    try:
        resolved = _resolve_model_uncertainty_params(params, value_col, variant_id)
        prepared = _prepare_representation_windows(
            data,
            time_col=time_col,
            feature_cols=resolved["feature_cols"],
            reference_window=reference_window,
            current_window=current_window,
            min_reference_size=resolved["min_reference_size"],
            min_current_size=resolved["min_current_size"],
        )
    except (KeyError, TypeError, ValueError) as exc:
        return _model_uncertainty_not_applicable(variant_id, str(exc), metadata)

    warnings = list(prepared["warnings"])
    metadata.update(prepared["metadata"])
    metadata.update(
        {
            "backend": "numpy_scipy_model_uncertainty_drift",
            "feature_cols": resolved["feature_cols"],
            "alpha": resolved["alpha"],
            "threshold_policy": resolved["threshold_policy"],
            "uncertainty_metric": resolved["uncertainty_metric"],
            "calibration_policy": resolved["calibration_policy"],
        }
    )
    if params.get("threshold_or_alpha") is not None:
        warnings.append("threshold_or_alpha was interpreted as Model Uncertainty Drift alpha")
    if variant_id == "SOFTMAX_CONFIDENCE_DRIFT" and resolved["confidence_col"] is None:
        warnings.append("SOFTMAX_CONFIDENCE_DRIFT derived confidence as max probability across probability_cols")
    if variant_id == "PREDICTIVE_VARIANCE_DRIFT" and resolved["variance_col"] is None:
        warnings.append("PREDICTIVE_VARIANCE_DRIFT derived variance across prediction_cols")

    try:
        run = _run_model_uncertainty_drift(
            prepared["reference_values"],
            prepared["current_values"],
            variant_id,
            resolved,
        )
    except ValueError as exc:
        return _model_uncertainty_not_applicable(variant_id, str(exc), metadata, warnings)

    drift_detected = bool(run["p_value"] < resolved["alpha"])
    severity = "drift_detected" if drift_detected else "normal"
    n_ref = prepared["reference_values"].shape[0]
    n_cur = prepared["current_values"].shape[0]
    measurements = {
        "TEST_STATISTIC": run["test_statistic"],
        "P_VALUE": run["p_value"],
        "DRIFT_ALARM_STATE": "drift_detected" if drift_detected else "normal",
        "THRESHOLD": resolved["alpha"],
        "METHOD_POLICY": run["method_policy"],
        "UNCERTAINTY_MEAN_REFERENCE": run["mean_reference"],
        "UNCERTAINTY_MEAN_CURRENT": run["mean_current"],
        "UNCERTAINTY_MEAN_DELTA": run["mean_delta"],
        "LOW_CONFIDENCE_RATE_REFERENCE": run["low_confidence_rate_reference"],
        "LOW_CONFIDENCE_RATE_CURRENT": run["low_confidence_rate_current"],
        "SAMPLE_SIZE": {"reference": int(n_ref), "current": int(n_cur)},
        "SAMPLE_SIZE_REFERENCE": int(n_ref),
        "SAMPLE_SIZE_CURRENT": int(n_cur),
        "FEATURE_COLUMNS": resolved["feature_cols"],
    }

    return DriftResult(
        method_id=MODEL_UNCERTAINTY_METHOD_ID,
        method_name=MODEL_UNCERTAINTY_METHOD_NAME,
        method_category=MODEL_UNCERTAINTY_METHOD_CATEGORY,
        variant_id=variant_id,
        drift_detected=drift_detected,
        severity=severity,
        drift_score=run["test_statistic"],
        p_value=run["p_value"],
        test_statistic=run["test_statistic"],
        threshold=resolved["alpha"],
        measurements=measurements,
        interpretation=_model_uncertainty_interpretation(
            variant_id=variant_id,
            n_ref=n_ref,
            n_cur=n_cur,
            statistic=run["test_statistic"],
            p_value=run["p_value"],
            alpha=resolved["alpha"],
            mean_reference=run["mean_reference"],
            mean_current=run["mean_current"],
            alarm_state=measurements["DRIFT_ALARM_STATE"],
            policy=run["method_policy"],
        ),
        warnings=warnings,
        metadata=metadata,
    )


def _resolve_ocdd_params(params: dict[str, Any], value_col: str | None, variant_id: str) -> dict[str, Any]:
    feature_cols = params.get("feature_cols", params.get("embedding_cols"))
    if feature_cols is None and value_col is not None:
        feature_cols = [value_col]
    if feature_cols is None:
        feature_cols = params.get("input_signal")
    if isinstance(feature_cols, str):
        feature_cols = [feature_cols]
    if not feature_cols:
        raise ValueError("OCDD requires params['feature_cols'] or params['embedding_cols']")
    feature_cols = [str(col) for col in feature_cols]
    if len(feature_cols) < 2:
        raise ValueError("OCDD requires at least two numeric feature columns")

    alpha = float(params.get("alpha", params.get("threshold_or_alpha", 0.05)))
    if not 0.0 < alpha < 1.0:
        raise ValueError("alpha must be in (0, 1)")
    threshold = params.get("threshold", params.get("score_threshold"))
    threshold_policy = "explicit" if threshold is not None else "reference_quantile"
    threshold = None if threshold is None else float(threshold)
    if threshold is not None and threshold < 0.0:
        raise ValueError("threshold/score_threshold must be >= 0")

    anomaly_rate_threshold = float(params.get("anomaly_rate_threshold", max(alpha * 2.0, 0.05)))
    if not 0.0 <= anomaly_rate_threshold <= 1.0:
        raise ValueError("anomaly_rate_threshold must be in [0, 1]")
    n_estimators = int(params.get("n_estimators", 64))
    if n_estimators <= 0:
        raise ValueError("n_estimators must be a positive integer")
    latent_dim = int(params.get("latent_dim", params.get("n_components", max(1, min(len(feature_cols) - 1, 2)))))
    if not 1 <= latent_dim < len(feature_cols):
        raise ValueError("latent_dim/n_components must be in [1, feature_dimension)")

    return {
        "feature_cols": feature_cols,
        "alpha": alpha,
        "threshold": threshold,
        "threshold_policy": threshold_policy,
        "anomaly_rate_threshold": anomaly_rate_threshold,
        "n_estimators": n_estimators,
        "random_state": int(params.get("random_state", 13)),
        "latent_dim": latent_dim,
        "min_reference_size": _positive_int(params.get("min_reference_size", max(len(feature_cols) + 2, 20)), "min_reference_size"),
        "min_current_size": _positive_int(params.get("min_current_size", 5), "min_current_size"),
    }


def _resolve_autoencoder_params(params: dict[str, Any], value_col: str | None, variant_id: str) -> dict[str, Any]:
    feature_cols = params.get("feature_cols", params.get("embedding_cols", params.get("latent_cols")))
    error_col = params.get("reconstruction_error_col", params.get("error_col"))
    if variant_id == "RECONSTRUCTION_ERROR_DRIFT" and error_col is not None:
        feature_cols = [str(error_col)]
    elif feature_cols is None and value_col is not None:
        feature_cols = [value_col]
    if feature_cols is None:
        feature_cols = params.get("input_signal")
    if isinstance(feature_cols, str):
        feature_cols = [feature_cols]
    if not feature_cols:
        raise ValueError(
            "Autoencoder Representation Drift requires feature_cols, embedding_cols, latent_cols, or reconstruction_error_col"
        )
    feature_cols = [str(col) for col in feature_cols]
    if variant_id != "RECONSTRUCTION_ERROR_DRIFT" and len(feature_cols) < 2:
        raise ValueError(f"{variant_id} requires at least two numeric representation columns")

    alpha = float(params.get("alpha", params.get("threshold_or_alpha", 0.05)))
    if not 0.0 < alpha < 1.0:
        raise ValueError("alpha must be in (0, 1)")
    threshold = params.get("threshold")
    threshold_policy = "explicit" if threshold is not None else "alpha_or_permutation"
    threshold = None if threshold is None else float(threshold)
    if threshold is not None and threshold < 0.0:
        raise ValueError("threshold must be >= 0")
    bandwidth = params.get("bandwidth", params.get("kernel_bandwidth"))
    bandwidth = None if bandwidth is None else float(bandwidth)
    if bandwidth is not None and bandwidth <= 0.0:
        raise ValueError("bandwidth/kernel_bandwidth must be > 0")
    permutation_count = int(params.get("permutation_count", 0))
    if permutation_count < 0:
        raise ValueError("permutation_count must be >= 0")
    latent_dim = int(params.get("latent_dim", params.get("n_components", max(1, min(len(feature_cols) - 1, 2)))))
    if variant_id == "RECONSTRUCTION_ERROR_DRIFT" and error_col is None:
        if not 1 <= latent_dim < len(feature_cols):
            raise ValueError("latent_dim/n_components must be in [1, feature_dimension)")

    return {
        "feature_cols": feature_cols,
        "error_col": None if error_col is None else str(error_col),
        "alpha": alpha,
        "threshold": threshold,
        "threshold_policy": threshold_policy,
        "bandwidth": bandwidth,
        "permutation_count": permutation_count,
        "random_state": int(params.get("random_state", 19)),
        "latent_dim": latent_dim,
        "encoder_version": params.get("encoder_version"),
        "scaling_policy": str(params.get("scaling_policy", "reference_standardize")).lower(),
        "min_reference_size": _positive_int(params.get("min_reference_size", max(len(feature_cols) + 2, 20)), "min_reference_size"),
        "min_current_size": _positive_int(params.get("min_current_size", 5), "min_current_size"),
    }


def _resolve_graph_embedding_params(params: dict[str, Any], value_col: str | None, variant_id: str) -> dict[str, Any]:
    feature_cols = params.get("feature_cols", params.get("embedding_cols"))
    if feature_cols is None and value_col is not None:
        feature_cols = [value_col]
    if feature_cols is None:
        feature_cols = params.get("input_signal")
    if isinstance(feature_cols, str):
        feature_cols = [feature_cols]
    if not feature_cols:
        raise ValueError("Graph Embedding Drift requires params['feature_cols'] or params['embedding_cols']")
    feature_cols = [str(col) for col in feature_cols]
    if len(feature_cols) < 2:
        raise ValueError("Graph Embedding Drift requires at least two numeric embedding columns")

    alpha = float(params.get("alpha", params.get("threshold_or_alpha", 0.05)))
    if not 0.0 < alpha < 1.0:
        raise ValueError("alpha must be in (0, 1)")
    threshold = params.get("threshold")
    threshold_policy = "explicit" if threshold is not None else "alpha_or_reference_quantile"
    threshold = None if threshold is None else float(threshold)
    if threshold is not None and threshold < 0.0:
        raise ValueError("threshold must be >= 0")
    bandwidth = params.get("bandwidth", params.get("kernel_bandwidth"))
    bandwidth = None if bandwidth is None else float(bandwidth)
    if bandwidth is not None and bandwidth <= 0.0:
        raise ValueError("bandwidth/kernel_bandwidth must be > 0")
    permutation_count = int(params.get("permutation_count", 0))
    if permutation_count < 0:
        raise ValueError("permutation_count must be >= 0")
    node_group_col = params.get("node_group_col", params.get("group_col"))

    return {
        "feature_cols": feature_cols,
        "alpha": alpha,
        "threshold": threshold,
        "threshold_policy": threshold_policy,
        "bandwidth": bandwidth,
        "permutation_count": permutation_count,
        "random_state": int(params.get("random_state", 23)),
        "node_group_col": None if node_group_col is None else str(node_group_col),
        "graph_embedding_model": params.get("graph_embedding_model"),
        "node_or_graph_level": params.get("node_or_graph_level", "graph"),
        "sampling_policy": params.get("sampling_policy"),
        "min_group_size": _positive_int(params.get("min_group_size", 2), "min_group_size"),
        "min_reference_size": _positive_int(params.get("min_reference_size", max(len(feature_cols) + 2, 20)), "min_reference_size"),
        "min_current_size": _positive_int(params.get("min_current_size", 5), "min_current_size"),
    }


def _resolve_llm_query_params(params: dict[str, Any], value_col: str | None, variant_id: str) -> dict[str, Any]:
    feature_cols = params.get("feature_cols", params.get("embedding_cols"))
    if feature_cols is None and value_col is not None:
        feature_cols = [value_col]
    if feature_cols is None:
        feature_cols = params.get("input_signal")
    if isinstance(feature_cols, str):
        feature_cols = [feature_cols]

    topic_col = params.get("topic_col", params.get("category_col"))
    count_col = params.get("count_col")
    if variant_id == "TOPIC_DISTRIBUTION_SHIFT":
        if topic_col is None:
            raise ValueError("TOPIC_DISTRIBUTION_SHIFT requires params['topic_col'] or params['category_col']")
        feature_cols = []
    else:
        if not feature_cols:
            raise ValueError(f"{variant_id} requires params['feature_cols'] or params['embedding_cols']")
        feature_cols = [str(col) for col in feature_cols]
        if len(feature_cols) < 2:
            raise ValueError(f"{variant_id} requires at least two embedding columns")

    alpha = float(params.get("alpha", params.get("threshold_or_alpha", 0.05)))
    if not 0.0 < alpha < 1.0:
        raise ValueError("alpha must be in (0, 1)")
    default_threshold = 0.6 if variant_id == "TEXT_DOMAIN_CLASSIFIER_DRIFT" else 0.1
    threshold = params.get("threshold", params.get("roc_auc_threshold", default_threshold))
    threshold_policy = "explicit" if threshold is not None else "default"
    threshold = float(threshold)
    if threshold < 0.0:
        raise ValueError("threshold/roc_auc_threshold must be >= 0")

    return {
        "feature_cols": feature_cols,
        "topic_col": None if topic_col is None else str(topic_col),
        "count_col": None if count_col is None else str(count_col),
        "alpha": alpha,
        "threshold": threshold,
        "threshold_policy": threshold_policy,
        "embedding_model": params.get("embedding_model"),
        "embedding_version": params.get("embedding_version"),
        "topic_model": params.get("topic_model"),
        "normalization_policy": params.get("normalization_policy", "reference_standardize"),
        "min_reference_size": _positive_int(params.get("min_reference_size", 20), "min_reference_size"),
        "min_current_size": _positive_int(params.get("min_current_size", 5), "min_current_size"),
    }


def _resolve_model_uncertainty_params(params: dict[str, Any], value_col: str | None, variant_id: str) -> dict[str, Any]:
    confidence_col = params.get("confidence_col")
    variance_col = params.get("variance_col")
    probability_cols = params.get("probability_cols")
    prediction_cols = params.get("prediction_cols")
    value = params.get("value_col", value_col)

    if isinstance(probability_cols, str):
        probability_cols = [probability_cols]
    if isinstance(prediction_cols, str):
        prediction_cols = [prediction_cols]

    if variant_id == "SOFTMAX_CONFIDENCE_DRIFT":
        if confidence_col is not None:
            feature_cols = [str(confidence_col)]
        elif probability_cols:
            feature_cols = [str(col) for col in probability_cols]
        elif value is not None:
            feature_cols = [str(value)]
            confidence_col = str(value)
        else:
            raise ValueError("SOFTMAX_CONFIDENCE_DRIFT requires confidence_col or probability_cols")
    elif variant_id == "ENTROPY_DRIFT":
        if not probability_cols:
            raise ValueError("ENTROPY_DRIFT requires probability_cols")
        feature_cols = [str(col) for col in probability_cols]
    else:
        if variance_col is not None:
            feature_cols = [str(variance_col)]
        elif prediction_cols:
            feature_cols = [str(col) for col in prediction_cols]
        elif value is not None:
            feature_cols = [str(value)]
            variance_col = str(value)
        else:
            raise ValueError("PREDICTIVE_VARIANCE_DRIFT requires variance_col or prediction_cols")

    alpha = float(params.get("alpha", params.get("threshold_or_alpha", 0.05)))
    if not 0.0 < alpha < 1.0:
        raise ValueError("alpha must be in (0, 1)")
    confidence_threshold = float(params.get("confidence_threshold", 0.5))
    if not 0.0 <= confidence_threshold <= 1.0:
        raise ValueError("confidence_threshold must be in [0, 1]")
    entropy_base = float(params.get("entropy_base", np.e))
    if entropy_base <= 0.0 or np.isclose(entropy_base, 1.0):
        raise ValueError("entropy_base must be positive and not 1")

    return {
        "feature_cols": feature_cols,
        "confidence_col": None if confidence_col is None else str(confidence_col),
        "variance_col": None if variance_col is None else str(variance_col),
        "probability_cols": None if probability_cols is None else [str(col) for col in probability_cols],
        "prediction_cols": None if prediction_cols is None else [str(col) for col in prediction_cols],
        "alpha": alpha,
        "threshold_policy": "ks_pvalue",
        "confidence_threshold": confidence_threshold,
        "entropy_base": entropy_base,
        "uncertainty_metric": params.get("uncertainty_metric", variant_id.lower()),
        "calibration_policy": params.get("calibration_policy"),
        "min_reference_size": _positive_int(params.get("min_reference_size", 20), "min_reference_size"),
        "min_current_size": _positive_int(params.get("min_current_size", 5), "min_current_size"),
    }


def _resolve_feature_map_params(params: dict[str, Any], value_col: str | None, variant_id: str) -> dict[str, Any]:
    raw_layer_cols = params.get("layer_feature_cols")
    layer_feature_cols: dict[str, list[str]] = {}
    if raw_layer_cols is not None:
        if not isinstance(raw_layer_cols, dict):
            raise ValueError("layer_feature_cols must be a mapping of layer name to feature columns")
        for layer, cols in raw_layer_cols.items():
            if isinstance(cols, str):
                cols = [cols]
            if not cols:
                raise ValueError("layer_feature_cols entries must not be empty")
            layer_feature_cols[str(layer)] = [str(col) for col in cols]
        feature_cols = [col for cols in layer_feature_cols.values() for col in cols]
    else:
        feature_cols = params.get("feature_cols", params.get("embedding_cols"))
        if feature_cols is None and value_col is not None:
            feature_cols = [value_col]
        if feature_cols is None:
            feature_cols = params.get("input_signal")
        if isinstance(feature_cols, str):
            feature_cols = [feature_cols]
        if not feature_cols:
            raise ValueError("Feature Map Drift requires params['feature_cols'], params['embedding_cols'], or params['layer_feature_cols']")
        feature_cols = [str(col) for col in feature_cols]
        layer_feature_cols = {str(params.get("model_layer", "feature_map")): feature_cols}
    if len(feature_cols) < 2:
        raise ValueError("Feature Map Drift requires at least two numeric feature columns")
    if len(set(feature_cols)) != len(feature_cols):
        raise ValueError("feature columns must be unique across layer_feature_cols")

    alpha = float(params.get("alpha", params.get("threshold_or_alpha", 0.05)))
    if not 0.0 < alpha < 1.0:
        raise ValueError("alpha must be in (0, 1)")
    threshold = params.get("threshold")
    threshold_policy = "explicit" if threshold is not None else "alpha_or_permutation"
    threshold = None if threshold is None else float(threshold)
    if threshold is not None and threshold < 0.0:
        raise ValueError("threshold must be >= 0")
    bandwidth = params.get("bandwidth", params.get("kernel_bandwidth"))
    bandwidth = None if bandwidth is None else float(bandwidth)
    if bandwidth is not None and bandwidth <= 0.0:
        raise ValueError("bandwidth/kernel_bandwidth must be > 0")
    permutation_count = int(params.get("permutation_count", 0))
    if permutation_count < 0:
        raise ValueError("permutation_count must be >= 0")

    return {
        "feature_cols": feature_cols,
        "layer_feature_cols": layer_feature_cols,
        "alpha": alpha,
        "threshold": threshold,
        "threshold_policy": threshold_policy,
        "bandwidth": bandwidth,
        "permutation_count": permutation_count,
        "random_state": int(params.get("random_state", 17)),
        "model_layer": params.get("model_layer"),
        "feature_extractor_version": params.get("feature_extractor_version"),
        "min_reference_size": _positive_int(params.get("min_reference_size", max(len(feature_cols) + 2, 20)), "min_reference_size"),
        "min_current_size": _positive_int(params.get("min_current_size", 5), "min_current_size"),
    }


def _prepare_representation_windows(
    data: pd.DataFrame,
    *,
    time_col: str,
    feature_cols: list[str],
    reference_window: tuple[str, str] | None,
    current_window: tuple[str, str] | None,
    min_reference_size: int,
    min_current_size: int,
    group_col: str | None = None,
) -> dict[str, Any]:
    if reference_window is None or current_window is None:
        raise ValueError("reference_window and current_window are required")
    if time_col not in data.columns:
        raise KeyError(f"missing time column: {time_col}")
    missing = [col for col in feature_cols if col not in data.columns]
    if missing:
        raise KeyError(f"missing feature columns: {missing}")
    if group_col is not None and group_col not in data.columns:
        raise KeyError(f"missing group column: {group_col}")
    ref_start, ref_end = _parse_window(reference_window, "reference_window")
    cur_start, cur_end = _parse_window(current_window, "current_window")
    if max(ref_start, cur_start) <= min(ref_end, cur_end):
        raise ValueError("reference_window and current_window must not overlap")

    selected_cols = [time_col, *feature_cols] if group_col is None else [time_col, group_col, *feature_cols]
    frame = data[selected_cols].copy()
    original_rows = len(frame)
    frame[time_col] = pd.to_datetime(frame[time_col], errors="coerce")
    invalid_time_rows = int(frame[time_col].isna().sum())
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
        "reference_groups": None if group_col is None else reference_frame[group_col].astype(str).to_numpy(),
        "current_groups": None if group_col is None else current_frame[group_col].astype(str).to_numpy(),
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


def _prepare_topic_distribution_windows(
    data: pd.DataFrame,
    *,
    time_col: str,
    topic_col: str,
    count_col: str | None,
    reference_window: tuple[str, str] | None,
    current_window: tuple[str, str] | None,
    min_reference_size: int,
    min_current_size: int,
) -> dict[str, Any]:
    if reference_window is None or current_window is None:
        raise ValueError("reference_window and current_window are required")
    if time_col not in data.columns:
        raise KeyError(f"missing time column: {time_col}")
    if topic_col not in data.columns:
        raise KeyError(f"missing topic column: {topic_col}")
    if count_col is not None and count_col not in data.columns:
        raise KeyError(f"missing count column: {count_col}")
    ref_start, ref_end = _parse_window(reference_window, "reference_window")
    cur_start, cur_end = _parse_window(current_window, "current_window")
    if max(ref_start, cur_start) <= min(ref_end, cur_end):
        raise ValueError("reference_window and current_window must not overlap")

    selected_cols = [time_col, topic_col] if count_col is None else [time_col, topic_col, count_col]
    frame = data[selected_cols].copy()
    original_rows = len(frame)
    frame[time_col] = pd.to_datetime(frame[time_col], errors="coerce")
    invalid_time_rows = int(frame[time_col].isna().sum())
    invalid_count_rows = 0
    if count_col is not None:
        frame[count_col] = pd.to_numeric(frame[count_col], errors="coerce")
        invalid_count_rows = int((~np.isfinite(frame[count_col].to_numpy(dtype=float))).sum())
        frame = frame.dropna(subset=[time_col, topic_col, count_col])
        frame = frame[frame[count_col] >= 0.0]
    else:
        frame = frame.dropna(subset=[time_col, topic_col])
        frame["_count"] = 1.0
        count_col = "_count"
    frame = frame.sort_values(time_col)

    reference_frame = frame[(frame[time_col] >= ref_start) & (frame[time_col] <= ref_end)]
    current_frame = frame[(frame[time_col] >= cur_start) & (frame[time_col] <= cur_end)]
    if len(reference_frame) < min_reference_size:
        raise ValueError(
            f"reference sample size {len(reference_frame)} is below min_reference_size {min_reference_size}"
        )
    if len(current_frame) < min_current_size:
        raise ValueError(f"current sample size {len(current_frame)} is below min_current_size {min_current_size}")
    ref_counts = reference_frame.groupby(topic_col)[count_col].sum()
    cur_counts = current_frame.groupby(topic_col)[count_col].sum()
    topics = sorted(set(ref_counts.index.astype(str)).union(set(cur_counts.index.astype(str))))
    ref_counts = ref_counts.rename(index=str).reindex(topics, fill_value=0.0).to_numpy(dtype=float)
    cur_counts = cur_counts.rename(index=str).reindex(topics, fill_value=0.0).to_numpy(dtype=float)
    if ref_counts.sum() <= 0.0 or cur_counts.sum() <= 0.0:
        raise ValueError("topic counts must be positive in both reference and current windows")
    warnings: list[str] = []
    if invalid_time_rows:
        warnings.append(f"dropped {invalid_time_rows} rows with invalid timestamps")
    if invalid_count_rows:
        warnings.append(f"dropped {invalid_count_rows} rows with invalid topic counts")
    return {
        "topics": topics,
        "reference_probabilities": ref_counts / ref_counts.sum(),
        "current_probabilities": cur_counts / cur_counts.sum(),
        "sample_size_reference": int(len(reference_frame)),
        "sample_size_current": int(len(current_frame)),
        "warnings": warnings,
        "metadata": {
            "original_rows": original_rows,
            "valid_rows": int(len(frame)),
            "invalid_time_rows": invalid_time_rows,
            "invalid_count_rows": invalid_count_rows,
            "reference_window": [ref_start.isoformat(), ref_end.isoformat()],
            "current_window": [cur_start.isoformat(), cur_end.isoformat()],
        },
    }


def _run_autoencoder_representation_drift(
    reference: np.ndarray,
    current: np.ndarray,
    variant_id: str,
    resolved: dict[str, Any],
) -> dict[str, Any]:
    if variant_id == "LATENT_SPACE_DRIFT":
        ref_z, cur_z = _standardize(reference, current)
        score, p_value, threshold = _mmd_score_with_optional_permutation(ref_z, cur_z, resolved)
        return {
            "test_statistic": score,
            "p_value": p_value,
            "threshold": threshold,
            "method_policy": "rbf_mmd_latent_space",
            "latent_drift_score": score,
            "reconstruction_error": None,
            "reference_reconstruction_error": None,
            "domain_classifier_auc": None,
            "domain_classifier_accuracy": None,
            "domain_probability_mean": None,
        }
    if variant_id == "RECONSTRUCTION_ERROR_DRIFT":
        return _autoencoder_reconstruction_error_drift(reference, current, resolved)
    return _autoencoder_domain_classifier(reference, current, resolved)


def _run_graph_embedding_drift(
    reference: np.ndarray,
    current: np.ndarray,
    reference_groups: np.ndarray | None,
    current_groups: np.ndarray | None,
    variant_id: str,
    resolved: dict[str, Any],
) -> dict[str, Any]:
    ref_z, cur_z = _standardize(reference, current)
    if variant_id == "GRAPH_EMBEDDING_MMD":
        score, p_value, threshold = _mmd_score_with_optional_permutation(ref_z, cur_z, resolved)
        centroid_shift, cosine_distance = _centroid_distances(ref_z, cur_z)
        return {
            "test_statistic": score,
            "p_value": p_value,
            "threshold": threshold,
            "method_policy": "rbf_mmd_graph_embedding",
            "centroid_shift": centroid_shift,
            "cosine_distance": cosine_distance,
            "node_group_scores": None,
            "top_node_group": None,
        }
    if variant_id == "GRAPH_EMBEDDING_CENTROID_SHIFT":
        centroid_shift, cosine_distance = _centroid_distances(ref_z, cur_z)
        threshold = resolved["threshold"]
        if threshold is None:
            threshold = float(np.quantile(np.linalg.norm(ref_z - np.mean(ref_z, axis=0), axis=1), 1.0 - resolved["alpha"]))
        return {
            "test_statistic": centroid_shift,
            "p_value": None,
            "threshold": float(threshold),
            "method_policy": "standardized_embedding_centroid_shift",
            "centroid_shift": centroid_shift,
            "cosine_distance": cosine_distance,
            "node_group_scores": None,
            "top_node_group": None,
        }
    return _node_representation_drift(ref_z, cur_z, reference_groups, current_groups, resolved)


def _run_llm_query_semantic_distance(
    reference: np.ndarray,
    current: np.ndarray,
    variant_id: str,
    resolved: dict[str, Any],
) -> dict[str, Any]:
    if variant_id == "QUERY_CENTROID_COSINE_SHIFT":
        centroid_shift, cosine_distance = _centroid_distances(reference, current)
        return {
            "test_statistic": cosine_distance,
            "p_value": None,
            "threshold": resolved["threshold"],
            "method_policy": "query_centroid_cosine_shift",
            "cosine_distance": cosine_distance,
            "centroid_shift": centroid_shift,
            "roc_auc": None,
            "classifier_confidence": None,
            "jensen_shannon_distance": None,
            "topic_proportion_delta": None,
            "topic_proportions_reference": None,
            "topic_proportions_current": None,
        }
    run = _autoencoder_domain_classifier(reference, current, {"threshold": resolved["threshold"]})
    return {
        "test_statistic": run["test_statistic"],
        "p_value": None,
        "threshold": resolved["threshold"],
        "method_policy": "nearest_centroid_text_domain_classifier_surrogate",
        "cosine_distance": None,
        "centroid_shift": None,
        "roc_auc": run["domain_classifier_auc"],
        "classifier_confidence": run["domain_probability_mean"],
        "jensen_shannon_distance": None,
        "topic_proportion_delta": None,
        "topic_proportions_reference": None,
        "topic_proportions_current": None,
    }


def _run_model_uncertainty_drift(
    reference: np.ndarray,
    current: np.ndarray,
    variant_id: str,
    resolved: dict[str, Any],
) -> dict[str, Any]:
    if variant_id == "SOFTMAX_CONFIDENCE_DRIFT":
        reference_scores = reference[:, 0] if resolved["confidence_col"] is not None else np.max(reference, axis=1)
        current_scores = current[:, 0] if resolved["confidence_col"] is not None else np.max(current, axis=1)
        low_ref = float(np.mean(reference_scores < resolved["confidence_threshold"]))
        low_cur = float(np.mean(current_scores < resolved["confidence_threshold"]))
        policy = "softmax_confidence_ks"
    elif variant_id == "ENTROPY_DRIFT":
        reference_scores = _row_entropy(reference, resolved["entropy_base"])
        current_scores = _row_entropy(current, resolved["entropy_base"])
        low_ref = None
        low_cur = None
        policy = "predictive_entropy_ks"
    else:
        reference_scores = reference[:, 0] if resolved["variance_col"] is not None else np.var(reference, axis=1, ddof=0)
        current_scores = current[:, 0] if resolved["variance_col"] is not None else np.var(current, axis=1, ddof=0)
        low_ref = None
        low_cur = None
        policy = "predictive_variance_ks"

    if not np.all(np.isfinite(reference_scores)) or not np.all(np.isfinite(current_scores)):
        raise ValueError("uncertainty scores must be finite")
    result = ks_2samp(reference_scores, current_scores, alternative="two-sided", method="asymp")
    mean_ref = float(np.mean(reference_scores))
    mean_cur = float(np.mean(current_scores))
    return {
        "test_statistic": float(result.statistic),
        "p_value": float(result.pvalue),
        "mean_reference": mean_ref,
        "mean_current": mean_cur,
        "mean_delta": float(mean_cur - mean_ref),
        "low_confidence_rate_reference": low_ref,
        "low_confidence_rate_current": low_cur,
        "method_policy": policy,
    }


def _row_entropy(probabilities: np.ndarray, base: float) -> np.ndarray:
    clipped = np.clip(probabilities.astype(float), 1e-12, None)
    row_sums = clipped.sum(axis=1, keepdims=True)
    if np.any(row_sums <= 0.0):
        raise ValueError("probability rows must have positive sums")
    normalized = clipped / row_sums
    return -np.sum(normalized * np.log(normalized), axis=1) / np.log(base)


def _run_topic_distribution_shift(prepared: dict[str, Any], resolved: dict[str, Any]) -> dict[str, Any]:
    reference = prepared["reference_probabilities"]
    current = prepared["current_probabilities"]
    delta = np.abs(current - reference)
    js_distance = _jensen_shannon_distance(reference, current)
    return {
        "test_statistic": js_distance,
        "p_value": None,
        "threshold": resolved["threshold"],
        "method_policy": "topic_distribution_jensen_shannon_distance",
        "cosine_distance": None,
        "centroid_shift": None,
        "roc_auc": None,
        "classifier_confidence": None,
        "jensen_shannon_distance": js_distance,
        "topic_proportion_delta": float(np.max(delta)),
        "topic_proportions_reference": dict(zip(prepared["topics"], reference.tolist())),
        "topic_proportions_current": dict(zip(prepared["topics"], current.tolist())),
    }


def _jensen_shannon_distance(reference: np.ndarray, current: np.ndarray) -> float:
    eps = 1e-12
    p = np.clip(reference.astype(float), eps, None)
    q = np.clip(current.astype(float), eps, None)
    p = p / p.sum()
    q = q / q.sum()
    midpoint = 0.5 * (p + q)
    kl_pm = np.sum(p * np.log(p / midpoint))
    kl_qm = np.sum(q * np.log(q / midpoint))
    return float(np.sqrt(0.5 * (kl_pm + kl_qm)))


def _node_representation_drift(
    reference: np.ndarray,
    current: np.ndarray,
    reference_groups: np.ndarray | None,
    current_groups: np.ndarray | None,
    resolved: dict[str, Any],
) -> dict[str, Any]:
    if reference_groups is None or current_groups is None:
        centroid = np.mean(reference, axis=0)
        current_distances = np.linalg.norm(current - centroid, axis=1)
        reference_distances = np.linalg.norm(reference - centroid, axis=1)
        score = float(np.max(current_distances))
        threshold = resolved["threshold"]
        if threshold is None:
            threshold = float(np.quantile(reference_distances, 1.0 - resolved["alpha"]))
        return {
            "test_statistic": score,
            "p_value": None,
            "threshold": float(threshold),
            "method_policy": "row_level_node_embedding_distance",
            "centroid_shift": score,
            "cosine_distance": None,
            "node_group_scores": None,
            "top_node_group": None,
        }

    group_scores: dict[str, dict[str, Any]] = {}
    common_groups = sorted(set(reference_groups).intersection(set(current_groups)))
    if not common_groups:
        raise ValueError("node_group_col has no overlapping groups between reference and current windows")
    for group in common_groups:
        ref_mask = reference_groups == group
        cur_mask = current_groups == group
        n_ref = int(np.sum(ref_mask))
        n_cur = int(np.sum(cur_mask))
        if n_ref < resolved["min_group_size"] or n_cur < resolved["min_group_size"]:
            continue
        group_ref = reference[ref_mask]
        group_cur = current[cur_mask]
        centroid_shift, cosine_distance = _centroid_distances(group_ref, group_cur)
        group_scores[group] = {
            "sample_size_reference": n_ref,
            "sample_size_current": n_cur,
            "centroid_shift": centroid_shift,
            "cosine_distance": cosine_distance,
            "alarm_state": "unknown",
        }
    if not group_scores:
        raise ValueError("no node groups met min_group_size in both reference and current windows")
    score = float(max(item["centroid_shift"] for item in group_scores.values()))
    threshold = resolved["threshold"]
    if threshold is None:
        threshold = float(np.quantile(np.linalg.norm(reference - np.mean(reference, axis=0), axis=1), 1.0 - resolved["alpha"]))
    top_group = max(group_scores, key=lambda group: group_scores[group]["centroid_shift"])
    for item in group_scores.values():
        item["alarm_state"] = "drift_detected" if item["centroid_shift"] > threshold else "normal"
    return {
        "test_statistic": score,
        "p_value": None,
        "threshold": float(threshold),
        "method_policy": "groupwise_node_embedding_centroid_shift",
        "centroid_shift": score,
        "cosine_distance": group_scores[top_group]["cosine_distance"],
        "node_group_scores": group_scores,
        "top_node_group": top_group,
    }


def _centroid_distances(reference: np.ndarray, current: np.ndarray) -> tuple[float, float]:
    ref_centroid = np.mean(reference, axis=0)
    cur_centroid = np.mean(current, axis=0)
    diff = cur_centroid - ref_centroid
    centroid_shift = float(np.linalg.norm(diff))
    denominator = float(np.linalg.norm(ref_centroid) * np.linalg.norm(cur_centroid))
    if denominator <= 1e-12:
        cosine_distance = 0.0 if np.linalg.norm(diff) <= 1e-12 else 1.0
    else:
        cosine_distance = float(1.0 - np.clip(ref_centroid @ cur_centroid / denominator, -1.0, 1.0))
    return centroid_shift, cosine_distance


def _autoencoder_reconstruction_error_drift(
    reference: np.ndarray,
    current: np.ndarray,
    resolved: dict[str, Any],
) -> dict[str, Any]:
    if resolved["error_col"] is not None:
        reference_errors = reference[:, 0]
        current_errors = current[:, 0]
        policy = "provided_reconstruction_error_ks"
    else:
        ref_z, cur_z = _standardize(reference, current)
        reference_errors, current_errors = _pca_reconstruction_errors(ref_z, cur_z, resolved["latent_dim"])
        policy = "linear_pca_reconstruction_error_surrogate"
    result = ks_2samp(reference_errors, current_errors, alternative="two-sided", method="asymp")
    mean_current = float(np.mean(current_errors))
    mean_reference = float(np.mean(reference_errors))
    threshold = resolved["threshold"] if resolved["threshold"] is not None else resolved["alpha"]
    return {
        "test_statistic": float(result.statistic),
        "p_value": float(result.pvalue),
        "threshold": float(threshold),
        "method_policy": policy,
        "latent_drift_score": None,
        "reconstruction_error": mean_current,
        "reference_reconstruction_error": mean_reference,
        "domain_classifier_auc": None,
        "domain_classifier_accuracy": None,
        "domain_probability_mean": None,
    }


def _autoencoder_domain_classifier(reference: np.ndarray, current: np.ndarray, resolved: dict[str, Any]) -> dict[str, Any]:
    ref_z, cur_z = _standardize(reference, current)
    mean_ref = np.mean(ref_z, axis=0)
    mean_cur = np.mean(cur_z, axis=0)
    direction = mean_cur - mean_ref
    norm = float(np.linalg.norm(direction))
    if norm <= 1e-12:
        scores_ref = np.zeros(len(ref_z), dtype=float)
        scores_cur = np.zeros(len(cur_z), dtype=float)
    else:
        direction = direction / norm
        midpoint = (mean_ref + mean_cur) / 2.0
        scores_ref = (ref_z - midpoint) @ direction
        scores_cur = (cur_z - midpoint) @ direction
    labels = np.concatenate([np.zeros(len(scores_ref), dtype=int), np.ones(len(scores_cur), dtype=int)])
    scores = np.concatenate([scores_ref, scores_cur])
    auc = _binary_auc(labels, scores)
    predictions = (scores >= 0.0).astype(int)
    accuracy = float(np.mean(predictions == labels))
    probability_mean = float(np.mean(1.0 / (1.0 + np.exp(-scores_cur))))
    statistic = float(max(auc, 1.0 - auc))
    threshold = resolved["threshold"] if resolved["threshold"] is not None else 0.6
    return {
        "test_statistic": statistic,
        "p_value": None,
        "threshold": float(threshold),
        "method_policy": "nearest_centroid_domain_separability_auc",
        "latent_drift_score": statistic,
        "reconstruction_error": None,
        "reference_reconstruction_error": None,
        "domain_classifier_auc": float(auc),
        "domain_classifier_accuracy": accuracy,
        "domain_probability_mean": probability_mean,
    }


def _binary_auc(labels: np.ndarray, scores: np.ndarray) -> float:
    positive_scores = scores[labels == 1]
    negative_scores = scores[labels == 0]
    if len(positive_scores) == 0 or len(negative_scores) == 0:
        return 0.5
    comparisons = positive_scores[:, None] - negative_scores[None, :]
    wins = np.sum(comparisons > 0)
    ties = np.sum(comparisons == 0)
    return float((wins + 0.5 * ties) / comparisons.size)


def _run_feature_map_drift(
    reference: np.ndarray,
    current: np.ndarray,
    variant_id: str,
    resolved: dict[str, Any],
) -> dict[str, Any]:
    if variant_id == "MODEL_FEATURE_MAP_KS":
        return _feature_map_ks(reference, current, resolved)
    if variant_id == "MODEL_FEATURE_MAP_MMD":
        score, p_value, threshold = _mmd_score_with_optional_permutation(reference, current, resolved)
        return {
            "test_statistic": score,
            "p_value": p_value,
            "threshold": threshold,
            "method_policy": "rbf_kernel_mmd_feature_map",
            "max_feature_statistic": None,
            "significant_feature_count": None,
            "significant_feature_fraction": None,
            "layerwise_scores": None,
        }
    return _layerwise_feature_map_drift(reference, current, resolved)


def _feature_map_ks(reference: np.ndarray, current: np.ndarray, resolved: dict[str, Any]) -> dict[str, Any]:
    stats: list[float] = []
    p_values: list[float] = []
    for index in range(reference.shape[1]):
        result = ks_2samp(reference[:, index], current[:, index], alternative="two-sided", method="asymp")
        stats.append(float(result.statistic))
        p_values.append(float(result.pvalue))
    min_p_value = float(np.min(p_values))
    max_statistic = float(np.max(stats))
    significant = [p_value < resolved["alpha"] for p_value in p_values]
    threshold = resolved["threshold"] if resolved["threshold"] is not None else resolved["alpha"]
    return {
        "test_statistic": max_statistic,
        "p_value": min_p_value,
        "threshold": float(threshold),
        "method_policy": "axiswise_ks_min_pvalue",
        "max_feature_statistic": max_statistic,
        "significant_feature_count": int(np.sum(significant)),
        "significant_feature_fraction": float(np.mean(significant)),
        "layerwise_scores": None,
    }


def _layerwise_feature_map_drift(reference: np.ndarray, current: np.ndarray, resolved: dict[str, Any]) -> dict[str, Any]:
    col_to_index = {col: index for index, col in enumerate(resolved["feature_cols"])}
    layer_scores: dict[str, dict[str, Any]] = {}
    min_p_value = 1.0
    max_statistic = 0.0
    significant_count = 0
    for layer, cols in resolved["layer_feature_cols"].items():
        indexes = [col_to_index[col] for col in cols]
        layer_reference = reference[:, indexes]
        layer_current = current[:, indexes]
        if len(indexes) == 1:
            result = ks_2samp(layer_reference[:, 0], layer_current[:, 0], alternative="two-sided", method="asymp")
            statistic = float(result.statistic)
            p_value = float(result.pvalue)
            policy = "layerwise_ks_single_feature"
        else:
            statistic, p_value, _ = _mmd_score_with_optional_permutation(layer_reference, layer_current, resolved)
            policy = "layerwise_rbf_mmd"
        alarm = bool(p_value is not None and p_value < resolved["alpha"])
        layer_scores[layer] = {
            "feature_count": len(indexes),
            "test_statistic": statistic,
            "p_value": p_value,
            "alarm_state": "drift_detected" if alarm else "normal",
            "method_policy": policy,
        }
        min_p_value = min(min_p_value, p_value if p_value is not None else 1.0)
        max_statistic = max(max_statistic, statistic)
        significant_count += int(alarm)
    threshold = resolved["threshold"] if resolved["threshold"] is not None else resolved["alpha"]
    return {
        "test_statistic": max_statistic,
        "p_value": min_p_value,
        "threshold": float(threshold),
        "method_policy": "layerwise_feature_map_min_pvalue",
        "max_feature_statistic": max_statistic,
        "significant_feature_count": significant_count,
        "significant_feature_fraction": float(significant_count / len(layer_scores)),
        "layerwise_scores": layer_scores,
    }


def _mmd_score_with_optional_permutation(
    reference: np.ndarray,
    current: np.ndarray,
    resolved: dict[str, Any],
) -> tuple[float, float | None, float]:
    bandwidth = resolved["bandwidth"]
    if bandwidth is None:
        bandwidth = _median_pairwise_distance(np.vstack([reference, current]))
    score = _rbf_mmd2(reference, current, bandwidth)
    threshold = resolved["threshold"] if resolved["threshold"] is not None else 0.0
    if resolved["permutation_count"] == 0:
        return score, None, float(threshold)

    rng = np.random.default_rng(resolved["random_state"])
    combined = np.vstack([reference, current])
    n_ref = reference.shape[0]
    permutation_scores = []
    for _ in range(resolved["permutation_count"]):
        order = rng.permutation(len(combined))
        perm_ref = combined[order[:n_ref]]
        perm_cur = combined[order[n_ref:]]
        permutation_scores.append(_rbf_mmd2(perm_ref, perm_cur, bandwidth))
    permutation_scores_array = np.asarray(permutation_scores, dtype=float)
    p_value = float((np.sum(permutation_scores_array >= score) + 1.0) / (len(permutation_scores_array) + 1.0))
    if resolved["threshold"] is None:
        threshold = float(np.quantile(permutation_scores_array, 1.0 - resolved["alpha"]))
    return score, p_value, float(threshold)


def _rbf_mmd2(reference: np.ndarray, current: np.ndarray, bandwidth: float) -> float:
    gamma = 1.0 / (2.0 * bandwidth * bandwidth)
    k_xx = _rbf_kernel(reference, reference, gamma)
    k_yy = _rbf_kernel(current, current, gamma)
    k_xy = _rbf_kernel(reference, current, gamma)
    return float(np.mean(k_xx) + np.mean(k_yy) - 2.0 * np.mean(k_xy))


def _rbf_kernel(left: np.ndarray, right: np.ndarray, gamma: float) -> np.ndarray:
    left_norm = np.sum(np.square(left), axis=1)[:, None]
    right_norm = np.sum(np.square(right), axis=1)[None, :]
    distances = np.maximum(left_norm + right_norm - 2.0 * left @ right.T, 0.0)
    return np.exp(-gamma * distances)


def _median_pairwise_distance(values: np.ndarray) -> float:
    if len(values) < 2:
        return 1.0
    diffs = values[:, None, :] - values[None, :, :]
    distances = np.sqrt(np.sum(np.square(diffs), axis=2))
    upper = distances[np.triu_indices(len(values), k=1)]
    positive = upper[upper > 1e-12]
    if len(positive) == 0:
        return 1.0
    return float(np.median(positive))


def _run_ocdd(reference: np.ndarray, current: np.ndarray, variant_id: str, resolved: dict[str, Any]) -> dict[str, Any]:
    ref_z, cur_z = _standardize(reference, current)
    if variant_id == "ONE_CLASS_SVM_DRIFT":
        reference_scores = np.linalg.norm(ref_z, axis=1)
        current_scores = np.linalg.norm(cur_z, axis=1)
        reconstruction_error = None
        method_policy = "numpy_radial_one_class_boundary"
    elif variant_id == "ISOLATION_FOREST_DRIFT_SCORE":
        reference_scores, current_scores = _random_projection_scores(ref_z, cur_z, resolved)
        reconstruction_error = None
        method_policy = "numpy_random_projection_anomaly_score"
    else:
        reference_scores, current_scores = _pca_reconstruction_errors(ref_z, cur_z, resolved["latent_dim"])
        reconstruction_error = float(np.mean(current_scores))
        method_policy = "numpy_linear_pca_reconstruction_surrogate"

    if not np.all(np.isfinite(reference_scores)) or not np.all(np.isfinite(current_scores)):
        raise ValueError("OCDD produced non-finite anomaly scores")
    threshold = resolved["threshold"]
    if threshold is None:
        threshold = float(np.quantile(reference_scores, 1.0 - resolved["alpha"]))
    anomaly_flags = current_scores > threshold
    anomaly_count = int(np.sum(anomaly_flags))
    anomaly_rate = float(anomaly_count / len(current_scores))
    return {
        "mean_anomaly_score": float(np.mean(current_scores)),
        "max_anomaly_score": float(np.max(current_scores)),
        "mean_reconstruction_error": reconstruction_error,
        "threshold": float(threshold),
        "anomaly_count": anomaly_count,
        "anomaly_rate": anomaly_rate,
        "method_policy": method_policy,
    }


def _standardize(reference: np.ndarray, current: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    center = np.mean(reference, axis=0)
    scale = np.std(reference, axis=0, ddof=1)
    scale = np.where(scale <= 1e-12, 1.0, scale)
    return (reference - center) / scale, (current - center) / scale


def _random_projection_scores(
    reference: np.ndarray,
    current: np.ndarray,
    resolved: dict[str, Any],
) -> tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(resolved["random_state"])
    directions = rng.normal(size=(resolved["n_estimators"], reference.shape[1]))
    directions /= np.maximum(np.linalg.norm(directions, axis=1, keepdims=True), 1e-12)
    ref_proj = reference @ directions.T
    cur_proj = current @ directions.T
    centers = np.median(ref_proj, axis=0)
    scales = np.median(np.abs(ref_proj - centers), axis=0) / 0.6744897501960817
    scales = np.where(scales <= 1e-12, 1.0, scales)
    return (
        np.mean(np.abs((ref_proj - centers) / scales), axis=1),
        np.mean(np.abs((cur_proj - centers) / scales), axis=1),
    )


def _pca_reconstruction_errors(
    reference: np.ndarray,
    current: np.ndarray,
    latent_dim: int,
) -> tuple[np.ndarray, np.ndarray]:
    _, _, vt = np.linalg.svd(reference, full_matrices=False)
    components = vt[:latent_dim].T
    ref_rec = reference @ components @ components.T
    cur_rec = current @ components @ components.T
    return (
        np.mean(np.square(reference - ref_rec), axis=1),
        np.mean(np.square(current - cur_rec), axis=1),
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


def _positive_int(value: Any, name: str) -> int:
    parsed = int(value)
    if parsed <= 0:
        raise ValueError(f"{name} must be a positive integer")
    return parsed


def _ocdd_interpretation(
    *,
    variant_id: str,
    n_ref: int,
    n_cur: int,
    dimension: int,
    mean_score: float,
    score_threshold: float,
    anomaly_rate: float,
    rate_threshold: float,
    alarm_state: str,
    policy: str,
) -> str:
    return (
        f"{variant_id} scored {n_cur} current rows against {n_ref} reference rows across {dimension} features. "
        f"mean anomaly score={mean_score:.6g}, score_threshold={score_threshold:.6g}, "
        f"anomaly_rate={anomaly_rate:.6g}, anomaly_rate_threshold={rate_threshold:.6g}; "
        f"alarm_state={alarm_state}, policy={policy}."
    )


def _feature_map_interpretation(
    *,
    variant_id: str,
    n_ref: int,
    n_cur: int,
    dimension: int,
    statistic: float,
    p_value: float | None,
    threshold: float,
    alpha: float,
    alarm_state: str,
    policy: str,
) -> str:
    p_text = "not computed" if p_value is None else f"{p_value:.6g}"
    return (
        f"{variant_id} compared {n_ref} reference rows and {n_cur} current rows across {dimension} feature-map columns. "
        f"statistic={statistic:.6g}, p-value={p_text}, threshold={threshold:.6g}, alpha={alpha:.6g}; "
        f"alarm_state={alarm_state}, policy={policy}."
    )


def _autoencoder_interpretation(
    *,
    variant_id: str,
    n_ref: int,
    n_cur: int,
    dimension: int,
    statistic: float,
    p_value: float | None,
    threshold: float,
    alpha: float,
    alarm_state: str,
    policy: str,
) -> str:
    p_text = "not computed" if p_value is None else f"{p_value:.6g}"
    return (
        f"{variant_id} compared {n_ref} reference rows and {n_cur} current rows across {dimension} autoencoder columns. "
        f"statistic={statistic:.6g}, p-value={p_text}, threshold={threshold:.6g}, alpha={alpha:.6g}; "
        f"alarm_state={alarm_state}, policy={policy}."
    )


def _graph_embedding_interpretation(
    *,
    variant_id: str,
    n_ref: int,
    n_cur: int,
    dimension: int,
    statistic: float,
    p_value: float | None,
    threshold: float,
    alpha: float,
    alarm_state: str,
    policy: str,
) -> str:
    p_text = "not computed" if p_value is None else f"{p_value:.6g}"
    return (
        f"{variant_id} compared {n_ref} reference rows and {n_cur} current rows across {dimension} graph embedding columns. "
        f"statistic={statistic:.6g}, p-value={p_text}, threshold={threshold:.6g}, alpha={alpha:.6g}; "
        f"alarm_state={alarm_state}, policy={policy}."
    )


def _llm_query_interpretation(
    *,
    variant_id: str,
    n_ref: int,
    n_cur: int,
    dimension: int,
    statistic: float,
    threshold: float,
    alarm_state: str,
    policy: str,
) -> str:
    return (
        f"{variant_id} compared {n_ref} reference rows and {n_cur} current rows across {dimension} semantic dimensions. "
        f"statistic={statistic:.6g}, threshold={threshold:.6g}; alarm_state={alarm_state}, policy={policy}."
    )


def _model_uncertainty_interpretation(
    *,
    variant_id: str,
    n_ref: int,
    n_cur: int,
    statistic: float,
    p_value: float,
    alpha: float,
    mean_reference: float,
    mean_current: float,
    alarm_state: str,
    policy: str,
) -> str:
    return (
        f"{variant_id} compared {n_ref} reference uncertainty rows and {n_cur} current rows. "
        f"KS statistic={statistic:.6g}, p-value={p_value:.6g}, alpha={alpha:.6g}, "
        f"mean_reference={mean_reference:.6g}, mean_current={mean_current:.6g}; "
        f"alarm_state={alarm_state}, policy={policy}."
    )


def _ocdd_not_applicable(
    variant_id: str | None,
    warning: str,
    metadata: dict[str, Any] | None = None,
    prior_warnings: list[str] | None = None,
) -> DriftResult:
    result = not_applicable_result(
        method_id=OCDD_METHOD_ID,
        method_name=OCDD_METHOD_NAME,
        method_category=OCDD_METHOD_CATEGORY,
        variant_id=variant_id,
        warning=warning,
        metadata=metadata,
    )
    if prior_warnings:
        result.warnings = prior_warnings + result.warnings
    return result


def _model_uncertainty_not_applicable(
    variant_id: str | None,
    warning: str,
    metadata: dict[str, Any] | None = None,
    prior_warnings: list[str] | None = None,
) -> DriftResult:
    result = not_applicable_result(
        method_id=MODEL_UNCERTAINTY_METHOD_ID,
        method_name=MODEL_UNCERTAINTY_METHOD_NAME,
        method_category=MODEL_UNCERTAINTY_METHOD_CATEGORY,
        variant_id=variant_id,
        warning=warning,
        metadata=metadata,
    )
    if prior_warnings:
        result.warnings = prior_warnings + result.warnings
    return result


def _llm_query_not_applicable(
    variant_id: str | None,
    warning: str,
    metadata: dict[str, Any] | None = None,
    prior_warnings: list[str] | None = None,
) -> DriftResult:
    result = not_applicable_result(
        method_id=LLM_QUERY_SEMANTIC_METHOD_ID,
        method_name=LLM_QUERY_SEMANTIC_METHOD_NAME,
        method_category=LLM_QUERY_SEMANTIC_METHOD_CATEGORY,
        variant_id=variant_id,
        warning=warning,
        metadata=metadata,
    )
    if prior_warnings:
        result.warnings = prior_warnings + result.warnings
    return result


def _graph_embedding_not_applicable(
    variant_id: str | None,
    warning: str,
    metadata: dict[str, Any] | None = None,
    prior_warnings: list[str] | None = None,
) -> DriftResult:
    result = not_applicable_result(
        method_id=GRAPH_EMBEDDING_METHOD_ID,
        method_name=GRAPH_EMBEDDING_METHOD_NAME,
        method_category=GRAPH_EMBEDDING_METHOD_CATEGORY,
        variant_id=variant_id,
        warning=warning,
        metadata=metadata,
    )
    if prior_warnings:
        result.warnings = prior_warnings + result.warnings
    return result


def _autoencoder_not_applicable(
    variant_id: str | None,
    warning: str,
    metadata: dict[str, Any] | None = None,
    prior_warnings: list[str] | None = None,
) -> DriftResult:
    result = not_applicable_result(
        method_id=AUTOENCODER_REPRESENTATION_METHOD_ID,
        method_name=AUTOENCODER_REPRESENTATION_METHOD_NAME,
        method_category=AUTOENCODER_REPRESENTATION_METHOD_CATEGORY,
        variant_id=variant_id,
        warning=warning,
        metadata=metadata,
    )
    if prior_warnings:
        result.warnings = prior_warnings + result.warnings
    return result


def _feature_map_not_applicable(
    variant_id: str | None,
    warning: str,
    metadata: dict[str, Any] | None = None,
    prior_warnings: list[str] | None = None,
) -> DriftResult:
    result = not_applicable_result(
        method_id=FEATURE_MAP_DRIFT_METHOD_ID,
        method_name=FEATURE_MAP_DRIFT_METHOD_NAME,
        method_category=FEATURE_MAP_DRIFT_METHOD_CATEGORY,
        variant_id=variant_id,
        warning=warning,
        metadata=metadata,
    )
    if prior_warnings:
        result.warnings = prior_warnings + result.warnings
    return result
