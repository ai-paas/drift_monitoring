from __future__ import annotations

import ast
import csv
import json
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .config import CONTROL_PLANE_ROOT, PROJECT_ROOT
from .matrix_runner import DEFAULT_MATRIX_PATH, load_matrix_seed


METHOD_DATA_PATH = PROJECT_ROOT / "drift 보고서" / "charts" / "method_data.js"
RUNTIME_REGISTRY_PATH = CONTROL_PLANE_ROOT / "drift_server" / "app" / "drift" / "runtime_registry.py"
BINDING_DIR = CONTROL_PLANE_ROOT / "drift_server" / "app" / "payload_adapter" / "bindings"
COVERAGE_REPORT_PATH = CONTROL_PLANE_ROOT / "testing" / "payload_adapter_coverage_report.json"
DEFAULT_OUTPUT_DIR = CONTROL_PLANE_ROOT / "testing" / "harness" / "matrix" / "generated" / "sprint36"


RUNTIME_ALIAS_BY_VARIANT = {
    "ADWIN_MEAN_STREAM": "adwin_mean_stream",
    "ADWIN_ERROR_RATE": "adwin_error_rate",
    "ADWIN_DISTANCE_STREAM": "adwin_distance_stream",
    "GENERIC_METRIC_THRESHOLD_DRIFT": "generic_metric_threshold_drift",
    "TIME_FEATURE_SPLIT_DETECTOR": "time_feature_split_detector",
    "DOMAIN_CLASSIFIER_TREE": "domain_classifier_tree",
    "BAYESIAN_ONLINE_CHANGE_POINT_GAUSSIAN": "bocd_stream",
    "BOCD_HAZARD_RATE_VARIANT": "bocd_stream",
    "BOCD_PREDICTIVE_PROBABILITY": "bocd_stream",
    "ONE_SAMPLE_KS_KNOWN_CDF": "generic_distribution_ecdf_window",
    "TWO_SAMPLE_KS_TWO_SIDED": "generic_distribution_ecdf_window",
    "TWO_SAMPLE_KS_ONE_SIDED_GREATER": "generic_distribution_ecdf_window",
    "TWO_SAMPLE_KS_ONE_SIDED_LESS": "generic_distribution_ecdf_window",
    "TWO_SAMPLE_KS_EXACT_PVALUE": "generic_distribution_ecdf_window",
    "TWO_SAMPLE_KS_ASYMPTOTIC_PVALUE": "generic_distribution_ecdf_window",
    "KS_WITH_TIES_OR_DISCRETE_CAUTION": "generic_distribution_ecdf_window",
    "LILLIEFORS_RELATED_ONE_SAMPLE": "generic_distribution_ecdf_window",
    "HIGHER_ORDER_KS": "generic_distribution_ecdf_window",
    "TWO_SAMPLE_KS_APPROX_QUANTILE": "generic_distribution_ecdf_window",
    "ONE_SAMPLE_ANDERSON_DARLING": "generic_distribution_ecdf_window",
    "TWO_SAMPLE_ANDERSON_DARLING": "generic_distribution_ecdf_window",
    "K_SAMPLE_ANDERSON_DARLING": "generic_distribution_ecdf_window",
    "TAIL_SENSITIVE_AD": "generic_distribution_ecdf_window",
    "ONE_SAMPLE_CVM": "generic_distribution_ecdf_window",
    "TWO_SAMPLE_CVM": "generic_distribution_ecdf_window",
    "K_SAMPLE_CVM": "generic_distribution_ecdf_window",
    "KUIPER_TWO_SAMPLE": "generic_distribution_ecdf_window",
    "KUIPER_CIRCULAR_DATA": "generic_distribution_ecdf_window",
    "KUIPER_ONE_SAMPLE": "generic_distribution_ecdf_window",
    "TWO_SAMPLE_EPPS_SINGLETON": "generic_distribution_ecdf_window",
    "DISCRETE_EPPS_SINGLETON": "generic_distribution_ecdf_window",
    "ASYMPTOTIC_EPPS_SINGLETON": "generic_distribution_ecdf_window",
    "UNIVARIATE_ENERGY_DISTANCE": "energy_distance_window",
    "ENERGY_DISTANCE_PERMUTATION_TEST": "energy_distance_window",
    "MULTIVARIATE_ENERGY_DISTANCE": "multivariate_energy_distance",
    "LEAST_SQUARES_DENSITY_DIFFERENCE": "lsdd_window",
    "PERMUTATION_LSDD": "lsdd_window",
    "LSDD_WITH_PREPROCESSING": "lsdd_with_preprocessing",
    "KERNEL_MMD_BIASED": "mmd_window",
    "KERNEL_MMD_UNBIASED": "mmd_window",
    "LINEAR_TIME_MMD": "linear_time_mmd",
    "STREAMING_MMD": "streaming_mmd",
    "MEWMA_STANDARD": "mewma_window",
    "MEWMA_WITH_MAHALANOBIS_D2": "mewma_window",
    "HOTELLING_T2_ONE_SAMPLE_PHASE_II": "hotelling_t2_window",
    "HOTELLING_T2_TWO_SAMPLE": "hotelling_t2_window",
    "REGULARIZED_HOTELLING_T2": "hotelling_t2_window",
    "SAMPLE_MAHALANOBIS_OUTLIER": "mahalanobis_window",
    "WINDOW_MEAN_MAHALANOBIS": "mahalanobis_window",
    "ROBUST_MAHALANOBIS": "mahalanobis_window",
    "SOFTMAX_CONFIDENCE_DRIFT": "softmax_confidence_drift",
    "ENTROPY_DRIFT": "entropy_drift",
    "PREDICTIVE_VARIANCE_DRIFT": "predictive_variance_drift",
    "ONE_CLASS_SVM_DRIFT": "one_class_svm_drift",
    "ISOLATION_FOREST_DRIFT_SCORE": "isolation_forest_drift_score",
    "AUTOENCODER_RECONSTRUCTION_DRIFT": "autoencoder_reconstruction_drift",
    "DOMAIN_CLASSIFIER_ROC_AUC": "domain_classifier_roc_auc",
    "DOMAIN_CLASSIFIER_PROBABILITY_DRIFT": "domain_classifier_probability_drift",
    "CROSS_VALIDATED_DOMAIN_CLASSIFIER": "cross_validated_domain_classifier",
    "SHAP_VALUE_DISTRIBUTION_TEST": "shap_value_distribution_test",
    "GLOBAL_IMPORTANCE_RANK_SHIFT": "global_importance_rank_shift",
    "CLASS_CONDITIONAL_SHAP_DRIFT": "class_conditional_shap_drift",
    "MODEL_FEATURE_MAP_KS": "model_feature_map_ks",
    "MODEL_FEATURE_MAP_MMD": "model_feature_map_mmd",
    "LAYERWISE_FEATURE_MAP_DRIFT": "layerwise_feature_map_drift",
    "LATENT_SPACE_DRIFT": "latent_space_drift",
    "RECONSTRUCTION_ERROR_DRIFT": "reconstruction_error_drift",
    "AUTOENCODER_DOMAIN_CLASSIFIER": "autoencoder_domain_classifier",
    "GRAPH_EMBEDDING_MMD": "graph_embedding_mmd",
    "GRAPH_EMBEDDING_CENTROID_SHIFT": "graph_embedding_centroid_shift",
    "NODE_REPRESENTATION_DRIFT": "node_representation_drift",
    "QUERY_CENTROID_COSINE_SHIFT": "query_centroid_cosine_shift",
    "TEXT_DOMAIN_CLASSIFIER_DRIFT": "text_domain_classifier_drift",
    "TOPIC_DISTRIBUTION_SHIFT": "topic_distribution_shift",
    "TEXT_DOMAIN_CLASSIFIER_ROC_AUC": "text_domain_classifier_roc_auc",
    "TEXT_DOMAIN_CLASSIFIER_STAT_TEST": "text_domain_classifier_stat_test",
    "TEXT_DESCRIPTOR_DRIFT": "text_descriptor_drift",
    "DRIFT_RETRAINING_WITH_ADWIN": "drift_retraining_with_adwin",
    "DRIFT_RETRAINING_WITH_PAGE_HINKLEY": "drift_retraining_with_page_hinkley",
    "DRIFT_RETRAINING_CHAMPION_CHALLENGER": "drift_retraining_champion_challenger",
    "HAT_ADWIN_NODE_MONITORING": "hat_adwin_node_monitoring",
    "HAT_ALTERNATE_TREE_REPLACEMENT": "hat_alternate_tree_replacement",
    "MANN_WHITNEY_TWO_SIDED": "generic_statistical_test_window",
    "MANN_WHITNEY_ONE_SIDED": "generic_statistical_test_window",
    "MANN_WHITNEY_EXACT": "generic_statistical_test_window",
    "ONE_SAMPLE_T_TEST": "generic_statistical_test_window",
    "TWO_SAMPLE_STUDENT_T_TEST": "generic_statistical_test_window",
    "WELCH_T_TEST": "generic_statistical_test_window",
    "PAIRED_T_TEST": "generic_statistical_test_window",
    "BWS_TWO_SAMPLE": "generic_statistical_test_window",
    "BWS_EXACT_OR_ASYMPTOTIC": "generic_statistical_test_window",
    "BWS_RANK_BASED": "generic_statistical_test_window",
    "ONE_SIDED_UPPER_CUSUM": "cusum_stream",
    "ONE_SIDED_LOWER_CUSUM": "cusum_stream",
    "TWO_SIDED_CUSUM": "cusum_stream",
    "CUSUM_ON_DISTANCE_STREAM": "cusum_on_distance_stream",
    "F_TEST_EQUAL_VARIANCE": "generic_statistical_test_window",
    "ANOVA_F_TEST_GROUP_MEAN": "generic_statistical_test_window",
    "MODEL_COMPARISON_F_TEST": "generic_statistical_test_window",
    "LEVENE_MEAN_CENTER": "generic_statistical_test_window",
    "BROWN_FORSYTHE_MEDIAN_CENTER": "generic_statistical_test_window",
    "TRIMMED_MEAN_LEVENE": "generic_statistical_test_window",
    "CHI_SQUARE_GOODNESS_OF_FIT": "generic_categorical_contingency_window",
    "CHI_SQUARE_HOMOGENEITY": "generic_categorical_contingency_window",
    "CHI_SQUARE_WITH_LOW_EXPECTED_COUNT_CAUTION": "generic_categorical_contingency_window",
    "TWO_BY_TWO_FISHER_EXACT": "generic_categorical_contingency_window",
    "ONE_SIDED_FISHER_EXACT": "generic_categorical_contingency_window",
    "EXTENDED_CONTINGENCY_EXACT_TEST": "generic_categorical_contingency_window",
    "LIKELIHOOD_RATIO_G_TEST_GOF": "generic_categorical_contingency_window",
    "LIKELIHOOD_RATIO_G_TEST_INDEPENDENCE": "generic_categorical_contingency_window",
    "G_TEST_WITH_SMALL_COUNT_CAUTION": "generic_categorical_contingency_window",
    "CATEGORICAL_PSI": "generic_probability_distance_window",
    "POPULATION_WEIGHTED_PSI": "generic_probability_distance_window",
    "DISCRETE_KL_DIVERGENCE": "generic_probability_distance_window",
    "HISTOGRAM_KL_DIVERGENCE": "generic_probability_distance_window",
    "SMOOTHED_KL_DIVERGENCE": "generic_probability_distance_window",
    "SYMMETRIZED_KL": "generic_probability_distance_window",
    "JENSEN_SHANNON_DIVERGENCE": "generic_probability_distance_window",
    "JENSEN_SHANNON_DISTANCE": "generic_probability_distance_window",
    "MULTICLASS_PROBABILITY_JS": "generic_probability_distance_window",
    "TEXT_TOPIC_JS": "generic_probability_distance_window",
    "DISCRETE_HELLINGER_DISTANCE": "generic_probability_distance_window",
    "HISTOGRAM_HELLINGER_DISTANCE": "generic_probability_distance_window",
    "CATEGORICAL_HELLINGER_DISTANCE": "generic_probability_distance_window",
    "CATEGORICAL_TOTAL_VARIATION": "generic_probability_distance_window",
    "HISTOGRAM_TOTAL_VARIATION": "generic_probability_distance_window",
    "PROBABILITY_VECTOR_TOTAL_VARIATION": "generic_probability_distance_window",
    "CATEGORICAL_L_INFINITY": "generic_probability_distance_window",
    "PROBABILITY_VECTOR_L_INFINITY": "generic_probability_distance_window",
    "BINNED_NUMERIC_L_INFINITY": "generic_probability_distance_window",
    "DISCRETE_BHATTACHARYYA_DISTANCE": "generic_probability_distance_window",
    "GAUSSIAN_BHATTACHARYYA_DISTANCE": "generic_probability_distance_window",
    "HISTOGRAM_BHATTACHARYYA_DISTANCE": "generic_probability_distance_window",
    "HINC_CATEGORICAL": "generic_probability_distance_window",
    "HINC_HISTOGRAM_NUMERIC": "generic_probability_distance_window",
    "HINC_IMAGE_FEATURE": "generic_probability_distance_window",
    "DDM_STANDARD": "ddm_error_rate_stream",
    "DDM_WARNING_BUFFER": "ddm_warning_buffer",
    "DDM_CLASS_SPECIFIC": "ddm_class_specific",
    "ECDD_WT_STANDARD": "ecdd_wt_error_rate_stream",
    "ECDD_WT_WARNING_DRIFT": "ecdd_wt_error_rate_stream",
    "ECDD_WT_ERROR_STREAM": "ecdd_wt_error_rate_stream",
    "EWMA_UNIVARIATE_CONTROL_CHART": "ewma_stream",
    "EWMA_ONE_SIDED": "ewma_stream",
    "EWMA_BASELINE_REPLAY_THRESHOLD": "ewma_baseline_replay_threshold",
    "GMA_CONTROL_CHART": "gma_stream",
    "GMA_ONE_SIDED": "gma_stream",
    "GMA_WITH_EMPIRICAL_LIMIT": "gma_with_empirical_limit",
    "HDDM_A_HOEFFDING_BOUND": "hddm_a_error_rate_stream",
    "HDDM_A_WARNING_DRIFT": "hddm_a_error_rate_stream",
    "HDDM_A_TWO_SIDED": "hddm_a_error_rate_stream",
    "HDDM_W_WEIGHTED_AVERAGE": "hddm_w_error_rate_stream",
    "HDDM_W_WARNING_DRIFT": "hddm_w_error_rate_stream",
    "HDDM_W_RECENT_ERROR_WEIGHTING": "hddm_w_error_rate_stream",
    "RDDM_STANDARD": "rddm_error_rate_stream",
    "RDDM_REACTIVE_RESET": "rddm_reactive_reset",
    "STEPD_ACCURACY_WINDOW": "stepd_error_rate_stream",
    "STEPD_WARNING_DRIFT": "stepd_error_rate_stream",
    "STEPD_SUPERVISED_STREAM": "stepd_error_rate_stream",
    "EDDM_DISTANCE_BETWEEN_ERRORS": "eddm_error_rate_stream",
    "EDDM_WARNING_DRIFT": "eddm_warning_drift",
    "EDDM_GRADUAL_DRIFT": "eddm_gradual_drift",
    "NUMERIC_BINNED_PSI": "psi_numeric_binned",
    "SCORE_BAND_PSI": "psi_numeric_binned",
    "KSWIN_STANDARD": "kswin_numeric_window",
    "KSWIN_WITH_SUBSAMPLING": "kswin_numeric_window",
    "KSWIN_NUMERIC_STREAM": "kswin_numeric_window",
    "PAGE_HINKLEY_INCREASE": "page_hinkley_stream",
    "PAGE_HINKLEY_DECREASE": "page_hinkley_stream",
    "SEQDRIFT1": "seqdrift_numeric_window",
    "SEQDRIFT2": "seqdrift_numeric_window",
    "SPRT_BERNOULLI_ERROR_RATE": "sprt_bernoulli_error_rate",
    "SPRT_GAUSSIAN_MEAN_SHIFT": "sprt_gaussian_mean_shift",
    "WASSERSTEIN_1D_EXACT": "wasserstein_numeric_window",
    "WASSERSTEIN_WINDOW_TREND": "wasserstein_numeric_window",
    "WASSERSTEIN_APPROX_HISTOGRAM": "wasserstein_numeric_window",
    "SLICED_WASSERSTEIN_EMBEDDING": "sliced_wasserstein_embedding",
}


@dataclass(frozen=True)
class CatalogPair:
    chart_id: str
    method: str
    method_name: str
    method_variant_key: str
    description: str


def build_compatibility_matrix() -> dict[str, Any]:
    catalog_pairs = load_method_catalog_pairs(METHOD_DATA_PATH)
    runtime_keys = load_runtime_keys(RUNTIME_REGISTRY_PATH)
    explicit_binding_keys = load_explicit_binding_keys(BINDING_DIR)
    coverage_by_pair = load_payload_coverage(COVERAGE_REPORT_PATH)
    seed_by_pair = load_seed_evidence(DEFAULT_MATRIX_PATH)

    rows = []
    for pair in catalog_pairs:
        runtime_method_key = RUNTIME_ALIAS_BY_VARIANT.get(pair.method_variant_key)
        runtime_available = bool(runtime_method_key and runtime_method_key in runtime_keys)
        coverage = coverage_by_pair.get((pair.method_variant_key, pair.chart_id), {})
        binding_key = str(coverage.get("bindingKey") or "")
        binding_type = str(coverage.get("bindingType") or "")
        payload_coverage_available = bool(coverage)
        explicit_binding_available = binding_key in explicit_binding_keys
        scenario = seed_by_pair.get((pair.method_variant_key, pair.chart_id))
        scenario_available = bool(scenario and scenario.get("status") == "executable")
        scenario_blocked = bool(scenario and scenario.get("status") == "blocked")

        status, reasons = classify_status(
            runtime_available=runtime_available,
            payload_coverage_available=payload_coverage_available,
            scenario_available=scenario_available,
            scenario_blocked=scenario_blocked,
        )
        rows.append(
            {
                "chartId": pair.chart_id,
                "method": pair.method,
                "methodName": pair.method_name,
                "methodVariantKey": pair.method_variant_key,
                "runtimeMethodKey": runtime_method_key,
                "runtimeStatus": "runtime_available" if runtime_available else "runtime_wrapper_missing",
                "payloadBindingKey": binding_key or None,
                "payloadBindingType": binding_type or None,
                "payloadBindingStatus": "payload_coverage_available"
                if payload_coverage_available
                else "payload_binding_missing",
                "explicitBindingFile": explicit_binding_available,
                "scenarioStatus": "scenario_available"
                if scenario_available
                else ("scenario_blocked" if scenario_blocked else "scenario_missing"),
                "scenarioPath": scenario.get("scenarioPath") if scenario else None,
                "matrixRowId": scenario.get("matrixRowId") if scenario else None,
                "status": status,
                "blockingReasons": reasons,
                "description": pair.description,
            }
        )

    return {
        "matrixId": "sprint36-chart-method-compatibility-001",
        "version": 1,
        "sourceDocuments": [
            str(METHOD_DATA_PATH.relative_to(PROJECT_ROOT)),
            str(RUNTIME_REGISTRY_PATH.relative_to(CONTROL_PLANE_ROOT)),
            str(COVERAGE_REPORT_PATH.relative_to(CONTROL_PLANE_ROOT)),
            str(DEFAULT_MATRIX_PATH.relative_to(CONTROL_PLANE_ROOT)),
        ],
        "statusPolicy": {
            "tested_passed": "runtime, payload coverage, and seed scenario are present.",
            "scenario_blocked": "runtime and payload coverage are present, but the mapped seed row is blocked by a known data or algorithm constraint.",
            "scenario_missing": "runtime and payload coverage are present, but no harness scenario is mapped.",
            "binding_missing": "runtime is present, but payload coverage is absent.",
            "runtime_wrapper_missing": "no Drift Server runtime method key is mapped to the catalog variant.",
        },
        "summary": summarize_rows(rows, runtime_keys=runtime_keys, explicit_binding_keys=explicit_binding_keys),
        "rows": rows,
    }


def load_method_catalog_pairs(path: Path) -> list[CatalogPair]:
    raw = path.read_text(encoding="utf-8").strip()
    match = re.match(r"window\.CHART_METHODS\s*=\s*(.*);\s*$", raw, flags=re.DOTALL)
    if not match:
        raise ValueError(f"Unsupported method_data.js shape: {path}")
    catalog = json.loads(match.group(1))
    pairs = []
    for chart_id in sorted(catalog):
        for item in catalog[chart_id]:
            method = str(item.get("method") or "")
            method_name, method_variant_key = split_method(method)
            pairs.append(
                CatalogPair(
                    chart_id=str(chart_id),
                    method=method,
                    method_name=method_name,
                    method_variant_key=method_variant_key,
                    description=str(item.get("description") or ""),
                )
            )
    return pairs


def load_runtime_keys(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            if any(isinstance(target, ast.Name) and target.id == "RUNTIME_METHODS" for target in node.targets):
                if isinstance(node.value, ast.Dict):
                    return dict_string_keys(node.value)
        if isinstance(node, ast.AnnAssign):
            if isinstance(node.target, ast.Name) and node.target.id == "RUNTIME_METHODS":
                if isinstance(node.value, ast.Dict):
                    return dict_string_keys(node.value)
    raise ValueError(f"RUNTIME_METHODS not found: {path}")


def dict_string_keys(node: ast.Dict) -> set[str]:
    return {
        key.value
        for key in node.keys
        if isinstance(key, ast.Constant) and isinstance(key.value, str)
    }


def load_explicit_binding_keys(path: Path) -> set[str]:
    keys = set()
    if not path.exists():
        return keys
    for binding_path in path.glob("*.json"):
        try:
            spec = json.loads(binding_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        binding_key = spec.get("bindingKey")
        keys.add(str(binding_key or binding_path.stem))
    return keys


def load_payload_coverage(path: Path) -> dict[tuple[str, str], dict[str, Any]]:
    report = json.loads(path.read_text(encoding="utf-8"))
    coverage = {}
    for item in report.get("passedBindings", []):
        chart_id = str(item.get("chartId") or "")
        method_variant_key = str(item.get("methodVariantKey") or "")
        if chart_id and method_variant_key:
            coverage[(method_variant_key, chart_id)] = item
    return coverage


def load_seed_evidence(path: Path) -> dict[tuple[str, str], dict[str, Any]]:
    seed = load_matrix_seed(path)
    evidence = {}
    for row in seed.get("rows", []):
        method = row.get("method") if isinstance(row.get("method"), dict) else {}
        chart = row.get("chart") if isinstance(row.get("chart"), dict) else {}
        harness = row.get("harness") if isinstance(row.get("harness"), dict) else {}
        key = (str(method.get("methodVariantKey") or ""), str(chart.get("chartId") or ""))
        if key[0] and key[1]:
            compatibility = row.get("compatibility") if isinstance(row.get("compatibility"), dict) else {}
            evidence[key] = {
                "matrixRowId": row.get("matrixRowId"),
                "scenarioPath": harness.get("scenarioPath"),
                "status": row.get("status"),
                "blockedReasons": compatibility.get("blockedReasons", []),
            }
    return evidence


def classify_status(
    *,
    runtime_available: bool,
    payload_coverage_available: bool,
    scenario_available: bool,
    scenario_blocked: bool,
) -> tuple[str, list[str]]:
    reasons = []
    if not runtime_available:
        reasons.append("runtime_wrapper_missing")
    if not payload_coverage_available:
        reasons.append("payload_binding_missing")
    if scenario_blocked:
        reasons.append("scenario_blocked")
    elif not scenario_available:
        reasons.append("scenario_missing")
    if not reasons:
        return "tested_passed", []
    if "runtime_wrapper_missing" in reasons:
        return "runtime_wrapper_missing", reasons
    if "payload_binding_missing" in reasons:
        return "binding_missing", reasons
    if "scenario_blocked" in reasons:
        return "scenario_blocked", reasons
    return "scenario_missing", reasons


def summarize_rows(rows: list[dict[str, Any]], *, runtime_keys: set[str], explicit_binding_keys: set[str]) -> dict[str, Any]:
    status_counts = Counter(str(row["status"]) for row in rows)
    runtime_counts = Counter(str(row["runtimeStatus"]) for row in rows)
    binding_counts = Counter(str(row["payloadBindingStatus"]) for row in rows)
    scenario_counts = Counter(str(row["scenarioStatus"]) for row in rows)
    by_chart = defaultdict(Counter)
    by_method_name = defaultdict(Counter)
    for row in rows:
        by_chart[str(row["chartId"])][str(row["status"])] += 1
        by_method_name[str(row["methodName"])][str(row["status"])] += 1
    return {
        "chartCount": len({row["chartId"] for row in rows}),
        "chartMethodPairCount": len(rows),
        "uniqueMethodVariantCount": len({row["methodVariantKey"] for row in rows}),
        "runtimeRegistryKeys": sorted(runtime_keys),
        "explicitBindingFileCount": len(explicit_binding_keys),
        "statusCounts": dict(sorted(status_counts.items())),
        "runtimeStatusCounts": dict(sorted(runtime_counts.items())),
        "payloadBindingStatusCounts": dict(sorted(binding_counts.items())),
        "scenarioStatusCounts": dict(sorted(scenario_counts.items())),
        "topChartsByMissingRuntime": top_missing(by_chart, "runtime_wrapper_missing"),
        "topMethodNamesByMissingRuntime": top_missing(by_method_name, "runtime_wrapper_missing"),
    }


def write_compatibility_artifacts(matrix: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "chart_method_compatibility_matrix.json"
    csv_path = output_dir / "chart_method_compatibility_matrix.csv"
    summary_path = output_dir / "chart_method_gap_summary.json"
    report_path = output_dir / "chart_method_gap_report.md"

    json_path.write_text(json.dumps(matrix, ensure_ascii=False, indent=2), encoding="utf-8")
    summary_path.write_text(json.dumps(matrix["summary"], ensure_ascii=False, indent=2), encoding="utf-8")
    write_csv(matrix["rows"], csv_path)
    report_path.write_text(render_gap_report(matrix), encoding="utf-8")
    return {
        "matrixJson": str(json_path),
        "matrixCsv": str(csv_path),
        "summaryJson": str(summary_path),
        "gapReport": str(report_path),
    }


def write_csv(rows: list[dict[str, Any]], path: Path) -> None:
    fieldnames = [
        "chartId",
        "methodName",
        "methodVariantKey",
        "runtimeMethodKey",
        "runtimeStatus",
        "payloadBindingKey",
        "payloadBindingType",
        "payloadBindingStatus",
        "explicitBindingFile",
        "scenarioStatus",
        "scenarioPath",
        "matrixRowId",
        "status",
        "blockingReasons",
    ]
    with path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: csv_value(row.get(field)) for field in fieldnames})


def render_gap_report(matrix: dict[str, Any]) -> str:
    summary = matrix["summary"]
    rows = matrix["rows"]
    lines = [
        "# Sprint36 Chart-Method Gap Report",
        "",
        "## Summary",
        "",
        f"- chartCount: {summary['chartCount']}",
        f"- chartMethodPairCount: {summary['chartMethodPairCount']}",
        f"- uniqueMethodVariantCount: {summary['uniqueMethodVariantCount']}",
        f"- explicitBindingFileCount: {summary['explicitBindingFileCount']}",
        f"- runtimeRegistryKeys: {', '.join(summary['runtimeRegistryKeys'])}",
        "",
        "## Status Counts",
        "",
    ]
    for status, count in summary["statusCounts"].items():
        lines.append(f"- {status}: {count}")
    lines.extend(["", "## Interpretation", ""])
    lines.append("- `tested_passed` means the catalog pair has runtime mapping, payload coverage, and a seed scenario.")
    lines.append("- `scenario_blocked` means a seed scenario exists but is blocked by a known data or algorithm constraint.")
    lines.append("- `scenario_missing` means Drift Server can likely execute it, but a harness scenario is not mapped yet.")
    lines.append("- `runtime_wrapper_missing` means the algorithm may exist elsewhere, but Drift Server has no mapped runtime key for this variant.")
    lines.append("- Payload coverage is based on `testing/payload_adapter_coverage_report.json`; most bindings are auto bindings, not explicit JSON files.")
    lines.extend(["", "## Tested/Executable Pairs", ""])
    for row in rows:
        if row["status"] == "tested_passed":
            lines.append(
                f"- {row['chartId']} + {row['methodVariantKey']} -> {row['runtimeMethodKey']} ({row['scenarioPath']})"
            )
    lines.extend(["", "## Scenario Missing Pairs", ""])
    for row in rows:
        if row["status"] == "scenario_missing":
            lines.append(f"- {row['chartId']} + {row['methodVariantKey']} -> {row['runtimeMethodKey']}")
    lines.extend(["", "## Scenario Blocked Pairs", ""])
    for row in rows:
        if row["status"] == "scenario_blocked":
            lines.append(f"- {row['chartId']} + {row['methodVariantKey']} -> {row['runtimeMethodKey']}")
    lines.extend(["", "## Runtime Wrapper Missing Pairs", ""])
    for row in rows:
        if row["status"] == "runtime_wrapper_missing":
            lines.append(f"- {row['chartId']} + {row['methodVariantKey']} ({row['methodName']})")
    lines.append("")
    return "\n".join(lines)


def split_method(method: str) -> tuple[str, str]:
    if "/" not in method:
        return method.strip(), method.strip()
    parts = [part.strip() for part in method.split("/") if part.strip()]
    return " / ".join(parts[:-1]), parts[-1]


def top_missing(counters: dict[str, Counter], status: str, limit: int = 10) -> list[dict[str, Any]]:
    items = [
        {"key": key, "missingCount": counter[status], "totalCount": sum(counter.values())}
        for key, counter in counters.items()
        if counter[status]
    ]
    return sorted(items, key=lambda item: (-item["missingCount"], item["key"]))[:limit]


def csv_value(value: Any) -> str:
    if isinstance(value, list):
        return ";".join(str(item) for item in value)
    if value is None:
        return ""
    return str(value)
