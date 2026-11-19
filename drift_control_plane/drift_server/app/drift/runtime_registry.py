from __future__ import annotations

from typing import Any, Callable

from drift_server.app.runtime_methods.adwin_mean_stream import run_adwin_mean_stream
from drift_server.app.runtime_methods.autoencoder_representation_window import run_autoencoder_representation_window
from drift_server.app.runtime_methods.bocd_stream import run_bocd_stream
from drift_server.app.runtime_methods.classifier_embedding_window import run_classifier_embedding_window
from drift_server.app.runtime_methods.cusum_stream import run_cusum_stream
from drift_server.app.runtime_methods.ddm_error_rate_stream import run_ddm_error_rate_stream
from drift_server.app.runtime_methods.drift_retraining_window import run_drift_retraining_window
from drift_server.app.runtime_methods.ecdd_wt_error_rate_stream import run_ecdd_wt_error_rate_stream
from drift_server.app.runtime_methods.eddm_error_rate_stream import run_eddm_error_rate_stream
from drift_server.app.runtime_methods.feature_map_window import run_feature_map_window
from drift_server.app.runtime_methods.generic_categorical_contingency_window import (
    run_generic_categorical_contingency_window,
)
from drift_server.app.runtime_methods.generic_distribution_ecdf_window import run_generic_distribution_ecdf_window
from drift_server.app.runtime_methods.generic_metric_threshold import run_generic_metric_threshold
from drift_server.app.runtime_methods.generic_probability_distance_window import run_generic_probability_distance_window
from drift_server.app.runtime_methods.generic_statistical_test_window import run_generic_statistical_test_window
from drift_server.app.runtime_methods.graph_embedding_window import run_graph_embedding_window
from drift_server.app.runtime_methods.hat_window import run_hat_window
from drift_server.app.runtime_methods.hddm_error_rate_stream import (
    run_hddm_a_error_rate_stream,
    run_hddm_w_error_rate_stream,
)
from drift_server.app.runtime_methods.kswin_numeric_window import run_kswin_numeric_window
from drift_server.app.runtime_methods.llm_query_semantic_window import run_llm_query_semantic_window
from drift_server.app.runtime_methods.model_uncertainty_window import (
    run_model_uncertainty_window,
    run_softmax_confidence_drift,
)
from drift_server.app.runtime_methods.multivariate_process_window import run_multivariate_process_window
from drift_server.app.runtime_methods.ocdd_window import run_ocdd_window
from drift_server.app.runtime_methods.page_hinkley_stream import run_page_hinkley_stream
from drift_server.app.runtime_methods.psi_numeric_binned import run_psi_numeric_binned
from drift_server.app.runtime_methods.rddm_error_rate_stream import run_rddm_error_rate_stream
from drift_server.app.runtime_methods.seqdrift_numeric_window import run_seqdrift_numeric_window
from drift_server.app.runtime_methods.shap_window import run_shap_window
from drift_server.app.runtime_methods.smoothing_control_stream import run_ewma_stream, run_gma_stream
from drift_server.app.runtime_methods.sprt_stream import run_sprt_stream
from drift_server.app.runtime_methods.stepd_error_rate_stream import run_stepd_error_rate_stream
from drift_server.app.runtime_methods.text_domain_classifier_window import run_text_domain_classifier_window
from drift_server.app.runtime_methods.tree_feature_window import run_tree_feature_window
from drift_server.app.runtime_methods.wasserstein_numeric_window import run_wasserstein_numeric_window


class RuntimeMethodNotFound(KeyError):
    pass


RuntimeMethod = Callable[[Any, dict[str, Any], dict[str, Any]], dict[str, Any]]

# @managed-contract contract_id=runtime_registry.RUNTIME_METHODS level=P0
RUNTIME_METHODS: dict[str, RuntimeMethod] = {
    "adwin_mean_stream": run_adwin_mean_stream,
    "adwin_error_rate": run_adwin_mean_stream,
    "adwin_distance_stream": run_adwin_mean_stream,
    "bocd_stream": run_bocd_stream,
    "bayesian_online_change_point_gaussian": run_bocd_stream,
    "bocd_hazard_rate_variant": run_bocd_stream,
    "bocd_predictive_probability": run_bocd_stream,
    "ddm_error_rate_stream": run_ddm_error_rate_stream,
    "ddm_warning_buffer": run_ddm_error_rate_stream,
    "ddm_class_specific": run_ddm_error_rate_stream,
    "ecdd_wt_error_rate_stream": run_ecdd_wt_error_rate_stream,
    "ecdd_wt_standard": run_ecdd_wt_error_rate_stream,
    "ecdd_wt_warning_drift": run_ecdd_wt_error_rate_stream,
    "ecdd_wt_error_stream": run_ecdd_wt_error_rate_stream,
    "eddm_error_rate_stream": run_eddm_error_rate_stream,
    "eddm_warning_drift": run_eddm_error_rate_stream,
    "eddm_gradual_drift": run_eddm_error_rate_stream,
    "ewma_stream": run_ewma_stream,
    "ewma_univariate_control_chart": run_ewma_stream,
    "ewma_one_sided": run_ewma_stream,
    "ewma_baseline_replay_threshold": run_ewma_stream,
    "gma_stream": run_gma_stream,
    "gma_control_chart": run_gma_stream,
    "gma_one_sided": run_gma_stream,
    "gma_with_empirical_limit": run_gma_stream,
    "hddm_a_error_rate_stream": run_hddm_a_error_rate_stream,
    "hddm_a_hoeffding_bound": run_hddm_a_error_rate_stream,
    "hddm_a_warning_drift": run_hddm_a_error_rate_stream,
    "hddm_a_two_sided": run_hddm_a_error_rate_stream,
    "hddm_w_error_rate_stream": run_hddm_w_error_rate_stream,
    "hddm_w_weighted_average": run_hddm_w_error_rate_stream,
    "hddm_w_warning_drift": run_hddm_w_error_rate_stream,
    "hddm_w_recent_error_weighting": run_hddm_w_error_rate_stream,
    "generic_distribution_ecdf_window": run_generic_distribution_ecdf_window,
    "generic_metric_threshold_drift": run_generic_metric_threshold,
    "generic_probability_distance_window": run_generic_probability_distance_window,
    "anderson_darling_window": run_generic_distribution_ecdf_window,
    "cramer_von_mises_window": run_generic_distribution_ecdf_window,
    "epps_singleton_window": run_generic_distribution_ecdf_window,
    "energy_distance_window": run_generic_distribution_ecdf_window,
    "univariate_energy_distance": run_generic_distribution_ecdf_window,
    "energy_distance_permutation_test": run_generic_distribution_ecdf_window,
    "multivariate_energy_distance": run_generic_distribution_ecdf_window,
    "lsdd_window": run_generic_distribution_ecdf_window,
    "least_squares_density_difference": run_generic_distribution_ecdf_window,
    "permutation_lsdd": run_generic_distribution_ecdf_window,
    "lsdd_with_preprocessing": run_generic_distribution_ecdf_window,
    "mmd_window": run_generic_distribution_ecdf_window,
    "kernel_mmd_biased": run_generic_distribution_ecdf_window,
    "kernel_mmd_unbiased": run_generic_distribution_ecdf_window,
    "linear_time_mmd": run_generic_distribution_ecdf_window,
    "streaming_mmd": run_generic_distribution_ecdf_window,
    "multivariate_process_window": run_multivariate_process_window,
    "mewma_window": run_multivariate_process_window,
    "mewma_standard": run_multivariate_process_window,
    "mewma_with_mahalanobis_d2": run_multivariate_process_window,
    "hotelling_t2_window": run_multivariate_process_window,
    "hotelling_t2_one_sample_phase_ii": run_multivariate_process_window,
    "hotelling_t2_two_sample": run_multivariate_process_window,
    "regularized_hotelling_t2": run_multivariate_process_window,
    "mahalanobis_window": run_multivariate_process_window,
    "sample_mahalanobis_outlier": run_multivariate_process_window,
    "window_mean_mahalanobis": run_multivariate_process_window,
    "robust_mahalanobis": run_multivariate_process_window,
    "model_uncertainty_window": run_model_uncertainty_window,
    "softmax_confidence_drift": run_softmax_confidence_drift,
    "entropy_drift": run_model_uncertainty_window,
    "predictive_variance_drift": run_model_uncertainty_window,
    "ocdd_window": run_ocdd_window,
    "one_class_svm_drift": run_ocdd_window,
    "isolation_forest_drift_score": run_ocdd_window,
    "autoencoder_reconstruction_drift": run_ocdd_window,
    "classifier_embedding_window": run_classifier_embedding_window,
    "domain_classifier_roc_auc": run_classifier_embedding_window,
    "domain_classifier_probability_drift": run_classifier_embedding_window,
    "cross_validated_domain_classifier": run_classifier_embedding_window,
    "shap_window": run_shap_window,
    "shap_value_distribution_test": run_shap_window,
    "global_importance_rank_shift": run_shap_window,
    "class_conditional_shap_drift": run_shap_window,
    "tree_feature_window": run_tree_feature_window,
    "time_feature_split_detector": run_tree_feature_window,
    "domain_classifier_tree": run_tree_feature_window,
    "feature_map_window": run_feature_map_window,
    "model_feature_map_ks": run_feature_map_window,
    "model_feature_map_mmd": run_feature_map_window,
    "layerwise_feature_map_drift": run_feature_map_window,
    "autoencoder_representation_window": run_autoencoder_representation_window,
    "latent_space_drift": run_autoencoder_representation_window,
    "reconstruction_error_drift": run_autoencoder_representation_window,
    "autoencoder_domain_classifier": run_autoencoder_representation_window,
    "graph_embedding_window": run_graph_embedding_window,
    "graph_embedding_mmd": run_graph_embedding_window,
    "graph_embedding_centroid_shift": run_graph_embedding_window,
    "node_representation_drift": run_graph_embedding_window,
    "llm_query_semantic_window": run_llm_query_semantic_window,
    "query_centroid_cosine_shift": run_llm_query_semantic_window,
    "text_domain_classifier_drift": run_llm_query_semantic_window,
    "topic_distribution_shift": run_llm_query_semantic_window,
    "text_domain_classifier_window": run_text_domain_classifier_window,
    "text_domain_classifier_roc_auc": run_text_domain_classifier_window,
    "text_domain_classifier_stat_test": run_text_domain_classifier_window,
    "text_descriptor_drift": run_text_domain_classifier_window,
    "drift_retraining_window": run_drift_retraining_window,
    "drift_retraining_with_adwin": run_drift_retraining_window,
    "drift_retraining_with_page_hinkley": run_drift_retraining_window,
    "drift_retraining_champion_challenger": run_drift_retraining_window,
    "hat_window": run_hat_window,
    "hat_adwin_node_monitoring": run_hat_window,
    "hat_alternate_tree_replacement": run_hat_window,
    "generic_statistical_test_window": run_generic_statistical_test_window,
    "baumgartner_weiss_schindler_window": run_generic_statistical_test_window,
    "cusum_stream": run_cusum_stream,
    "one_sided_upper_cusum": run_cusum_stream,
    "one_sided_lower_cusum": run_cusum_stream,
    "two_sided_cusum": run_cusum_stream,
    "cusum_on_distance_stream": run_cusum_stream,
    "f_test_variance_window": run_generic_statistical_test_window,
    "generic_categorical_contingency_window": run_generic_categorical_contingency_window,
    "kswin_numeric_window": run_kswin_numeric_window,
    "kswin_numeric_stream": run_kswin_numeric_window,
    "kswin_standard": run_kswin_numeric_window,
    "kswin_with_subsampling": run_kswin_numeric_window,
    "page_hinkley_stream": run_page_hinkley_stream,
    "page_hinkley_decrease": run_page_hinkley_stream,
    "page_hinkley_increase": run_page_hinkley_stream,
    "ks_test_window": run_generic_distribution_ecdf_window,
    "kuiper_window": run_generic_distribution_ecdf_window,
    "levene_window": run_generic_statistical_test_window,
    "chi_square_window": run_generic_categorical_contingency_window,
    "fisher_exact_window": run_generic_categorical_contingency_window,
    "g_test_window": run_generic_categorical_contingency_window,
    "probability_distance_window": run_generic_probability_distance_window,
    "kl_divergence_window": run_generic_probability_distance_window,
    "jensen_shannon_window": run_generic_probability_distance_window,
    "hellinger_window": run_generic_probability_distance_window,
    "total_variation_window": run_generic_probability_distance_window,
    "l_infinity_window": run_generic_probability_distance_window,
    "bhattacharyya_window": run_generic_probability_distance_window,
    "hinc_window": run_generic_probability_distance_window,
    "mann_whitney_window": run_generic_statistical_test_window,
    "psi_numeric_binned": run_psi_numeric_binned,
    "rddm_error_rate_stream": run_rddm_error_rate_stream,
    "rddm_reactive_reset": run_rddm_error_rate_stream,
    "seqdrift_numeric_window": run_seqdrift_numeric_window,
    "seqdrift1": run_seqdrift_numeric_window,
    "seqdrift2": run_seqdrift_numeric_window,
    "sprt_stream": run_sprt_stream,
    "sprt_bernoulli_error_rate": run_sprt_stream,
    "sprt_gaussian_mean_shift": run_sprt_stream,
    "stepd_error_rate_stream": run_stepd_error_rate_stream,
    "stepd_accuracy_window": run_stepd_error_rate_stream,
    "stepd_warning_drift": run_stepd_error_rate_stream,
    "stepd_supervised_stream": run_stepd_error_rate_stream,
    "t_test_window": run_generic_statistical_test_window,
    "wasserstein_1d_exact": run_wasserstein_numeric_window,
    "wasserstein_approx_histogram": run_wasserstein_numeric_window,
    "wasserstein_numeric_window": run_wasserstein_numeric_window,
    "wasserstein_window_trend": run_wasserstein_numeric_window,
    "sliced_wasserstein_embedding": run_wasserstein_numeric_window,
}


# @managed-contract contract_id=runtime_registry.get_runtime_method level=P0
def get_runtime_method(key: str) -> RuntimeMethod:
    try:
        return RUNTIME_METHODS[key]
    except KeyError as exc:
        raise RuntimeMethodNotFound(key) from exc
