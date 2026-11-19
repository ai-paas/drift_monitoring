from __future__ import annotations

import warnings as py_warnings
from typing import Any

import numpy as np
import pandas as pd
from scipy.stats import (
    anderson_ksamp,
    chi2_contingency,
    chisquare,
    cramervonmises_2samp,
    energy_distance,
    epps_singleton_2samp,
    f,
    f_oneway,
    fisher_exact,
    ks_2samp,
    levene,
    mannwhitneyu,
    power_divergence,
    ttest_1samp,
    ttest_ind,
    ttest_rel,
    wasserstein_distance,
)

from drift_algorithm.core.result import DriftResult, not_applicable_result
from drift_algorithm.core.windows import WindowedNumericData, prepare_numeric_windows


METHOD_ID = "DM-001"
METHOD_NAME = "KS Test"
METHOD_CATEGORY = "BatchDistributionComparison"
WASSERSTEIN_METHOD_ID = "DM-002"
WASSERSTEIN_METHOD_NAME = "Wasserstein Distance"
CHI_SQUARE_METHOD_ID = "DM-003"
CHI_SQUARE_METHOD_NAME = "Chi-square Test"
FISHER_METHOD_ID = "DM-004"
FISHER_METHOD_NAME = "Fisher's Exact Test"
G_TEST_METHOD_ID = "DM-005"
G_TEST_METHOD_NAME = "G-test"
PSI_METHOD_ID = "DM-006"
PSI_METHOD_NAME = "PSI"
KL_METHOD_ID = "DM-007"
KL_METHOD_NAME = "KL Divergence"
JS_METHOD_ID = "DM-008"
JS_METHOD_NAME = "Jensen-Shannon Distance"
HELLINGER_METHOD_ID = "DM-009"
HELLINGER_METHOD_NAME = "Hellinger Distance"
TOTAL_VARIATION_METHOD_ID = "DM-010"
TOTAL_VARIATION_METHOD_NAME = "Total Variation Distance"
L_INFINITY_METHOD_ID = "DM-011"
L_INFINITY_METHOD_NAME = "L-Infinity Distance"
BHATTACHARYYA_METHOD_ID = "DM-012"
BHATTACHARYYA_METHOD_NAME = "Bhattacharyya Distance"
HINC_METHOD_ID = "DM-013"
HINC_METHOD_NAME = "Histogram Intersection Normalized Complement"
MANN_WHITNEY_METHOD_ID = "DM-018"
MANN_WHITNEY_METHOD_NAME = "Mann-Whitney U / Wilcoxon Rank Sum Test"
T_TEST_METHOD_ID = "DM-019"
T_TEST_METHOD_NAME = "t-test 계열"
LEVENE_METHOD_ID = "DM-021"
LEVENE_METHOD_NAME = "Levene's Test"
ANDERSON_DARLING_METHOD_ID = "DM-014"
ANDERSON_DARLING_METHOD_NAME = "Anderson-Darling Test"
CRAMER_VON_MISES_METHOD_ID = "DM-015"
CRAMER_VON_MISES_METHOD_NAME = "Cramer-von Mises Test"
KUIPER_METHOD_ID = "DM-016"
KUIPER_METHOD_NAME = "Kuiper's Test"
BAUMGARTNER_WEISS_SCHINDLER_METHOD_ID = "DM-017"
BAUMGARTNER_WEISS_SCHINDLER_METHOD_NAME = "Baumgartner-Weiss-Schindler Test"
F_TEST_METHOD_ID = "DM-020"
F_TEST_METHOD_NAME = "F-test / Variance Test 계열"
ENERGY_DISTANCE_METHOD_ID = "DM-022"
ENERGY_DISTANCE_METHOD_NAME = "Energy Distance"
EPPS_SINGLETON_METHOD_ID = "DM-023"
EPPS_SINGLETON_METHOD_NAME = "Epps-Singleton Test"
MMD_METHOD_ID = "DM-024"
MMD_METHOD_NAME = "MMD"
LSDD_METHOD_ID = "DM-025"
LSDD_METHOD_NAME = "LSDD"

SUPPORTED_KS_VARIANTS = {
    "ONE_SAMPLE_KS_KNOWN_CDF",
    "TWO_SAMPLE_KS_TWO_SIDED",
    "TWO_SAMPLE_KS_ONE_SIDED_GREATER",
    "TWO_SAMPLE_KS_ONE_SIDED_LESS",
    "TWO_SAMPLE_KS_EXACT_PVALUE",
    "TWO_SAMPLE_KS_ASYMPTOTIC_PVALUE",
    "KS_WITH_TIES_OR_DISCRETE_CAUTION",
    "LILLIEFORS_RELATED_ONE_SAMPLE",
    "HIGHER_ORDER_KS",
    "TWO_SAMPLE_KS_APPROX_QUANTILE",
}

DEFERRED_KS_VARIANTS: set[str] = set()

SUPPORTED_WASSERSTEIN_VARIANTS = {
    "WASSERSTEIN_1D_EXACT",
    "WASSERSTEIN_APPROX_HISTOGRAM",
    "WASSERSTEIN_WINDOW_TREND",
    "SLICED_WASSERSTEIN_EMBEDDING",
}

SUPPORTED_CHI_SQUARE_VARIANTS = {
    "CHI_SQUARE_GOODNESS_OF_FIT",
    "CHI_SQUARE_HOMOGENEITY",
    "CHI_SQUARE_WITH_LOW_EXPECTED_COUNT_CAUTION",
}

SUPPORTED_FISHER_VARIANTS = {
    "TWO_BY_TWO_FISHER_EXACT",
    "ONE_SIDED_FISHER_EXACT",
    "EXTENDED_CONTINGENCY_EXACT_TEST",
}

SUPPORTED_G_TEST_VARIANTS = {
    "LIKELIHOOD_RATIO_G_TEST_GOF",
    "LIKELIHOOD_RATIO_G_TEST_INDEPENDENCE",
    "G_TEST_WITH_SMALL_COUNT_CAUTION",
}

SUPPORTED_PSI_VARIANTS = {
    "NUMERIC_BINNED_PSI",
    "CATEGORICAL_PSI",
    "SCORE_BAND_PSI",
    "POPULATION_WEIGHTED_PSI",
}

SUPPORTED_KL_VARIANTS = {
    "DISCRETE_KL_DIVERGENCE",
    "HISTOGRAM_KL_DIVERGENCE",
    "SMOOTHED_KL_DIVERGENCE",
    "SYMMETRIZED_KL",
}

SUPPORTED_JS_VARIANTS = {
    "JENSEN_SHANNON_DIVERGENCE",
    "JENSEN_SHANNON_DISTANCE",
    "MULTICLASS_PROBABILITY_JS",
    "TEXT_TOPIC_JS",
}

SUPPORTED_HELLINGER_VARIANTS = {
    "DISCRETE_HELLINGER_DISTANCE",
    "HISTOGRAM_HELLINGER_DISTANCE",
    "CATEGORICAL_HELLINGER_DISTANCE",
}

SUPPORTED_TOTAL_VARIATION_VARIANTS = {
    "CATEGORICAL_TOTAL_VARIATION",
    "HISTOGRAM_TOTAL_VARIATION",
    "PROBABILITY_VECTOR_TOTAL_VARIATION",
}

SUPPORTED_L_INFINITY_VARIANTS = {
    "CATEGORICAL_L_INFINITY",
    "PROBABILITY_VECTOR_L_INFINITY",
    "BINNED_NUMERIC_L_INFINITY",
}

SUPPORTED_BHATTACHARYYA_VARIANTS = {
    "DISCRETE_BHATTACHARYYA_DISTANCE",
    "GAUSSIAN_BHATTACHARYYA_DISTANCE",
    "HISTOGRAM_BHATTACHARYYA_DISTANCE",
}

SUPPORTED_HINC_VARIANTS = {
    "HINC_CATEGORICAL",
    "HINC_HISTOGRAM_NUMERIC",
    "HINC_IMAGE_FEATURE",
}

DEFERRED_WASSERSTEIN_VARIANTS: set[str] = set()

SUPPORTED_MANN_WHITNEY_VARIANTS = {
    "MANN_WHITNEY_TWO_SIDED",
    "MANN_WHITNEY_ONE_SIDED",
    "MANN_WHITNEY_EXACT",
}

SUPPORTED_T_TEST_VARIANTS = {
    "ONE_SAMPLE_T_TEST",
    "TWO_SAMPLE_STUDENT_T_TEST",
    "WELCH_T_TEST",
    "PAIRED_T_TEST",
}

SUPPORTED_LEVENE_VARIANTS = {
    "LEVENE_MEAN_CENTER",
    "BROWN_FORSYTHE_MEDIAN_CENTER",
    "TRIMMED_MEAN_LEVENE",
}

SUPPORTED_ANDERSON_DARLING_VARIANTS = {
    "ONE_SAMPLE_ANDERSON_DARLING",
    "TWO_SAMPLE_ANDERSON_DARLING",
    "K_SAMPLE_ANDERSON_DARLING",
    "TAIL_SENSITIVE_AD",
}

DEFERRED_ANDERSON_DARLING_VARIANTS: set[str] = set()

SUPPORTED_CRAMER_VON_MISES_VARIANTS = {
    "ONE_SAMPLE_CVM",
    "TWO_SAMPLE_CVM",
    "K_SAMPLE_CVM",
}

DEFERRED_CRAMER_VON_MISES_VARIANTS: set[str] = set()

SUPPORTED_KUIPER_VARIANTS = {
    "KUIPER_TWO_SAMPLE",
    "KUIPER_CIRCULAR_DATA",
    "KUIPER_ONE_SAMPLE",
}

DEFERRED_KUIPER_VARIANTS: set[str] = set()

SUPPORTED_BWS_VARIANTS = {
    "BWS_TWO_SAMPLE",
    "BWS_EXACT_OR_ASYMPTOTIC",
    "BWS_RANK_BASED",
}

DEFERRED_BWS_VARIANTS: set[str] = set()

SUPPORTED_F_TEST_VARIANTS = {
    "F_TEST_EQUAL_VARIANCE",
    "ANOVA_F_TEST_GROUP_MEAN",
    "MODEL_COMPARISON_F_TEST",
}

DEFERRED_F_TEST_VARIANTS: set[str] = set()

SUPPORTED_ENERGY_DISTANCE_VARIANTS = {
    "UNIVARIATE_ENERGY_DISTANCE",
    "ENERGY_DISTANCE_PERMUTATION_TEST",
    "MULTIVARIATE_ENERGY_DISTANCE",
}

DEFERRED_ENERGY_DISTANCE_VARIANTS: set[str] = set()

SUPPORTED_EPPS_SINGLETON_VARIANTS = {
    "TWO_SAMPLE_EPPS_SINGLETON",
    "DISCRETE_EPPS_SINGLETON",
    "ASYMPTOTIC_EPPS_SINGLETON",
}

DEFERRED_EPPS_SINGLETON_VARIANTS: set[str] = set()

SUPPORTED_MMD_VARIANTS = {
    "KERNEL_MMD_BIASED",
    "KERNEL_MMD_UNBIASED",
    "LINEAR_TIME_MMD",
    "STREAMING_MMD",
}

DEFERRED_MMD_VARIANTS: set[str] = set()

SUPPORTED_LSDD_VARIANTS = {
    "LEAST_SQUARES_DENSITY_DIFFERENCE",
    "PERMUTATION_LSDD",
    "LSDD_WITH_PREPROCESSING",
}

DEFERRED_LSDD_VARIANTS: set[str] = set()


def detect_ks_test(
    data: pd.DataFrame,
    *,
    time_col: str = "time",
    value_col: str | None = "value",
    reference_window: tuple[str, str] | None = None,
    current_window: tuple[str, str] | None = None,
    params: dict[str, Any] | None = None,
) -> DriftResult:
    params = dict(params or {})
    variant_id = params.get("variant_id", "TWO_SAMPLE_KS_TWO_SIDED")
    metadata: dict[str, Any] = {"params": dict(params)}

    if variant_id in DEFERRED_KS_VARIANTS:
        return _not_applicable(variant_id, f"KS variant is not implemented yet: {variant_id}", metadata)
    if variant_id not in SUPPORTED_KS_VARIANTS:
        return _not_applicable(variant_id, f"unsupported KS variant: {variant_id}", metadata)

    try:
        alpha = _resolve_alpha(params)
        alternative = _resolve_alternative(variant_id, params)
        p_value_method = _resolve_p_value_method(variant_id, params)
        min_reference_size = _positive_int(params.get("min_reference_size", 20), "min_reference_size")
        min_current_size = _positive_int(params.get("min_current_size", 20), "min_current_size")
        tie_policy = params.get("tie_policy", "warn_only")
        if tie_policy != "warn_only":
            return _not_applicable(variant_id, f"unsupported tie_policy: {tie_policy}", metadata)
        tie_unique_ratio_threshold = float(params.get("tie_unique_ratio_threshold", 0.95))
        if not 0 < tie_unique_ratio_threshold <= 1:
            return _not_applicable(variant_id, "tie_unique_ratio_threshold must be in (0, 1]", metadata)
        if params.get("multiple_testing_correction", "none") is None:
            params["multiple_testing_correction"] = "none"
        value_col = _resolve_value_col(value_col, params)
    except (TypeError, ValueError) as exc:
        return _not_applicable(variant_id, str(exc), metadata)

    try:
        prepared = prepare_numeric_windows(
            data,
            time_col=time_col,
            value_col=value_col,
            reference_window=reference_window,
            current_window=current_window,
        )
    except (KeyError, ValueError) as exc:
        return _not_applicable(variant_id, str(exc), metadata)

    metadata.update(prepared.metadata)
    metadata.update(
        {
            "value_col": value_col,
            "alternative": alternative,
            "p_value_method": p_value_method,
            "alpha": alpha,
            "tie_policy": tie_policy,
            "multiple_testing_correction": params.get("multiple_testing_correction", "none"),
        }
    )
    warnings = list(prepared.warnings)
    if variant_id in {
        "ONE_SAMPLE_KS_KNOWN_CDF",
        "LILLIEFORS_RELATED_ONE_SAMPLE",
        "HIGHER_ORDER_KS",
        "TWO_SAMPLE_KS_APPROX_QUANTILE",
    }:
        metadata["execution_policy"] = "two_sample_ks_reference_current"
        warnings.append(f"{variant_id} is executed with the two-sample KS engine over reference/current windows")

    if len(prepared.reference_values) < min_reference_size:
        return _not_applicable(
            variant_id,
            f"effective reference sample size {len(prepared.reference_values)} is below min_reference_size {min_reference_size}",
            metadata,
            warnings,
        )
    if len(prepared.current_values) < min_current_size:
        return _not_applicable(
            variant_id,
            f"effective current sample size {len(prepared.current_values)} is below min_current_size {min_current_size}",
            metadata,
            warnings,
        )

    tie_metadata = _tie_metadata(prepared.reference_values, prepared.current_values)
    metadata.update(tie_metadata)
    if tie_metadata["reference_has_ties"] or tie_metadata["current_has_ties"]:
        warnings.append("ties detected; continuous KS p-value interpretation may be weak")
    if tie_metadata["combined_unique_ratio"] < tie_unique_ratio_threshold:
        warnings.append("low unique-value ratio suggests discrete or rounded data; interpret KS p-value with caution")
    if params.get("multiple_testing_correction", "none") != "none":
        warnings.append("multiple_testing_correction is recorded but not applied by detect_ks_test")

    try:
        result = ks_2samp(
            prepared.reference_values,
            prepared.current_values,
            alternative=alternative,
            method=p_value_method,
        )
        ks_statistic = float(result.statistic)
        p_value = float(result.pvalue)
    except Exception as exc:  # scipy raises different errors across versions.
        return DriftResult(
            method_id=METHOD_ID,
            method_name=METHOD_NAME,
            method_category=METHOD_CATEGORY,
            variant_id=variant_id,
            drift_detected=None,
            severity="watch",
            drift_score=None,
            p_value=None,
            test_statistic=None,
            threshold=alpha,
            measurements=_base_measurements(prepared.reference_values, prepared.current_values, None, None),
            interpretation=f"KS statistic could not be computed: {exc}",
            warnings=warnings + [f"ks_2samp failed: {exc}"],
            metadata=metadata,
        )

    if not np.isfinite(ks_statistic) or not np.isfinite(p_value):
        return _not_applicable(variant_id, "KS statistic or p-value is not finite", metadata, warnings)

    drift_detected = bool(p_value < alpha)
    if drift_detected and _has_tie_caution(warnings):
        severity = "drift_candidate"
    else:
        severity = "drift_detected" if drift_detected else "normal"
    alarm_state = "drift_detected" if drift_detected else "normal"
    measurements = _base_measurements(prepared.reference_values, prepared.current_values, ks_statistic, p_value)
    measurements["DRIFT_ALARM_STATE"] = alarm_state

    return DriftResult(
        method_id=METHOD_ID,
        method_name=METHOD_NAME,
        method_category=METHOD_CATEGORY,
        variant_id=variant_id,
        drift_detected=drift_detected,
        severity=severity,
        drift_score=ks_statistic,
        p_value=p_value,
        test_statistic=ks_statistic,
        threshold=alpha,
        measurements=measurements,
        interpretation=_interpretation(
            variant_id=variant_id,
            reference_count=len(prepared.reference_values),
            current_count=len(prepared.current_values),
            ks_statistic=ks_statistic,
            p_value=p_value,
            alpha=alpha,
            drift_detected=drift_detected,
            warnings=warnings,
        ),
        warnings=warnings,
        metadata=metadata,
    )


def detect_wasserstein_distance(
    data: pd.DataFrame,
    *,
    time_col: str = "time",
    value_col: str | None = "value",
    reference_window: tuple[str, str] | None = None,
    current_window: tuple[str, str] | None = None,
    params: dict[str, Any] | None = None,
) -> DriftResult:
    params = dict(params or {})
    variant_id = params.get("variant_id", "WASSERSTEIN_1D_EXACT")
    metadata: dict[str, Any] = {"params": dict(params)}

    if variant_id in DEFERRED_WASSERSTEIN_VARIANTS:
        return _wasserstein_not_applicable(
            variant_id,
            f"Wasserstein variant is not implemented yet: {variant_id}",
            metadata,
        )
    if variant_id not in SUPPORTED_WASSERSTEIN_VARIANTS:
        return _wasserstein_not_applicable(variant_id, f"unsupported Wasserstein variant: {variant_id}", metadata)

    try:
        threshold, threshold_warning = _resolve_wasserstein_threshold(params)
        min_reference_size = _positive_int(params.get("min_reference_size", 20), "min_reference_size")
        min_current_size = _positive_int(params.get("min_current_size", 20), "min_current_size")
        value_col = _resolve_value_col(value_col, params)
        _validate_wasserstein_policy_params(params, variant_id)
        reference_weight_col = params.get("sample_weights_reference")
        current_weight_col = params.get("sample_weights_current")
    except (TypeError, ValueError) as exc:
        return _wasserstein_not_applicable(variant_id, str(exc), metadata)

    try:
        prepared = _prepare_wasserstein_windows(
            data,
            time_col=time_col,
            value_col=value_col,
            reference_window=reference_window,
            current_window=current_window,
            reference_weight_col=reference_weight_col,
            current_weight_col=current_weight_col,
        )
    except (KeyError, ValueError) as exc:
        return _wasserstein_not_applicable(variant_id, str(exc), metadata)

    reference_values = prepared["reference_values"]
    current_values = prepared["current_values"]
    reference_weights = prepared["reference_weights"]
    current_weights = prepared["current_weights"]
    warnings = list(prepared["warnings"])
    if threshold_warning:
        warnings.append(threshold_warning)
    if threshold is None:
        warnings.append("no distance threshold supplied; returning Wasserstein distance without binary alarm")
    if reference_weights is not None or current_weights is not None:
        warnings.append("sample weights are used; weighted and unweighted Wasserstein distances are not directly comparable")
    if params.get("trend_threshold") is not None and variant_id != "WASSERSTEIN_WINDOW_TREND":
        warnings.append(f"trend_threshold is recorded but not used by {variant_id}")

    metadata.update(prepared["metadata"])
    metadata.update(
        {
            "value_col": value_col,
            "threshold": threshold,
            "distance_order": 1,
            "normalization_policy": params.get("normalization_policy", "none"),
            "outlier_policy": params.get("outlier_policy", "keep"),
            "nan_policy": params.get("nan_policy", "drop"),
            "exact_method": params.get("exact_method", "scipy"),
            "binning_policy": _wasserstein_binning_policy(params, variant_id),
            "sample_weights_reference": reference_weight_col,
            "sample_weights_current": current_weight_col,
        }
    )

    if len(reference_values) < min_reference_size:
        return _wasserstein_not_applicable(
            variant_id,
            f"effective reference sample size {len(reference_values)} is below min_reference_size {min_reference_size}",
            metadata,
            warnings,
        )
    if len(current_values) < min_current_size:
        return _wasserstein_not_applicable(
            variant_id,
            f"effective current sample size {len(current_values)} is below min_current_size {min_current_size}",
            metadata,
            warnings,
        )

    distance_result = _wasserstein_distance_by_variant(
        variant_id=variant_id,
        params=params,
        reference_values=reference_values,
        current_values=current_values,
        reference_weights=reference_weights,
        current_weights=current_weights,
    )
    if distance_result["status"] != "success":
        return _wasserstein_not_applicable(variant_id, distance_result["reason"], metadata, warnings)
    distance = float(distance_result["distance"])
    warnings.extend(distance_result.get("warnings", []))
    metadata.update(distance_result.get("metadata", {}))

    if not np.isfinite(distance):
        return _wasserstein_not_applicable(variant_id, "Wasserstein distance is not finite", metadata, warnings)

    if threshold is None:
        drift_detected = None
        severity = "watch"
        alarm_state = "undetermined"
    elif distance > threshold:
        drift_detected = True
        severity = "drift_detected"
        alarm_state = "drift_detected"
    else:
        drift_detected = False
        severity = "normal"
        alarm_state = "normal"

    measurements = {
        "WASSERSTEIN_DISTANCE": distance,
        "SAMPLE_SIZE": {"reference": int(len(reference_values)), "current": int(len(current_values))},
        "SAMPLE_SIZE_REFERENCE": int(len(reference_values)),
        "SAMPLE_SIZE_CURRENT": int(len(current_values)),
        "WINDOW_SIZE": {"reference": int(len(reference_values)), "current": int(len(current_values))},
        "DRIFT_ALARM_STATE": alarm_state,
        "FEATURE_IMPORTANCE_OR_RANK": {"value_column": value_col, "rank": 1, "score": distance},
    }
    if variant_id == "WASSERSTEIN_APPROX_HISTOGRAM":
        measurements["METHOD_POLICY"] = {
            "distance": "wasserstein_distance",
            "approximation": "histogram_bin_centers",
            "binning_policy": metadata.get("binning_policy"),
            "bin_count": metadata.get("histogram_bin_count"),
        }
    if variant_id == "WASSERSTEIN_WINDOW_TREND":
        trend_threshold = params.get("trend_threshold", threshold)
        measurements["METHOD_POLICY"] = {
            "distance": "wasserstein_distance",
            "trend_policy": "single_reference_current_window_delta",
            "trend_threshold": trend_threshold,
        }
        measurements["WINDOW_TREND_DISTANCE"] = distance
        metadata["trend_policy"] = "single_reference_current_window_delta"
        metadata["trend_threshold"] = trend_threshold
    if variant_id == "SLICED_WASSERSTEIN_EMBEDDING":
        measurements["METHOD_POLICY"] = {
            "distance": "wasserstein_distance",
            "projection_policy": metadata.get("projection_policy", "single_projected_numeric_stream"),
            "projection_count": metadata.get("projection_count", 1),
        }

    return DriftResult(
        method_id=WASSERSTEIN_METHOD_ID,
        method_name=WASSERSTEIN_METHOD_NAME,
        method_category=METHOD_CATEGORY,
        variant_id=variant_id,
        drift_detected=drift_detected,
        severity=severity,
        drift_score=distance,
        p_value=None,
        test_statistic=distance,
        threshold=threshold,
        measurements=measurements,
        interpretation=_wasserstein_interpretation(
            variant_id=variant_id,
            reference_count=len(reference_values),
            current_count=len(current_values),
            distance=distance,
            threshold=threshold,
            alarm_state=alarm_state,
            warnings=warnings,
        ),
        warnings=warnings,
        metadata=metadata,
    )


def detect_chi_square_test(
    data: pd.DataFrame,
    *,
    time_col: str = "time",
    value_col: str | None = None,
    reference_window: tuple[str, str] | None = None,
    current_window: tuple[str, str] | None = None,
    params: dict[str, Any] | None = None,
) -> DriftResult:
    params = dict(params or {})
    variant_id = str(params.get("variant_id", "CHI_SQUARE_HOMOGENEITY")).upper()
    metadata: dict[str, Any] = {"params": dict(params)}

    if variant_id not in SUPPORTED_CHI_SQUARE_VARIANTS:
        return _chi_square_not_applicable(variant_id, f"unsupported Chi-square variant: {variant_id}", metadata)

    try:
        alpha = _resolve_alpha(params)
        min_reference_size = _positive_int(params.get("min_reference_size", 1), "min_reference_size")
        min_current_size = _positive_int(params.get("min_current_size", 1), "min_current_size")
        low_expected_threshold = float(params.get("low_expected_threshold", 5.0))
        if low_expected_threshold < 0:
            raise ValueError("low_expected_threshold must be non-negative")
        prepared = _prepare_categorical_counts(
            data,
            time_col=time_col,
            category_col=str(params.get("category_col", value_col or "category")),
            count_col=params.get("count_col"),
            reference_window=reference_window,
            current_window=current_window,
            min_reference_size=min_reference_size,
            min_current_size=min_current_size,
        )
    except (KeyError, TypeError, ValueError) as exc:
        return _chi_square_not_applicable(variant_id, str(exc), metadata)

    ref_counts = prepared["reference_counts"]
    cur_counts = prepared["current_counts"]
    categories = prepared["categories"]
    metadata.update(prepared["metadata"])
    metadata.update({"alpha": alpha, "low_expected_threshold": low_expected_threshold})
    warnings = list(prepared["warnings"])

    try:
        if variant_id == "CHI_SQUARE_GOODNESS_OF_FIT":
            expected = _expected_counts_from_reference(ref_counts, float(np.sum(cur_counts)))
            result = chisquare(f_obs=cur_counts, f_exp=expected)
            statistic = float(result.statistic)
            p_value = float(result.pvalue)
            expected_counts = expected
            dof = int(len(categories) - 1)
            method_policy = "current_counts_vs_reference_expected_proportions"
        else:
            table = np.vstack([ref_counts, cur_counts])
            statistic, p_value, dof, expected = chi2_contingency(table, correction=False)
            statistic = float(statistic)
            p_value = float(p_value)
            expected_counts = np.asarray(expected, dtype=float)
            method_policy = "reference_current_chi_square_homogeneity"
    except ValueError as exc:
        return _chi_square_not_applicable(variant_id, str(exc), metadata, warnings)

    low_expected_count = int(np.sum(expected_counts < low_expected_threshold))
    if low_expected_count:
        warnings.append(f"{low_expected_count} expected cells are below {low_expected_threshold:g}; chi-square approximation may be weak")
    if variant_id == "CHI_SQUARE_WITH_LOW_EXPECTED_COUNT_CAUTION":
        warnings.append("low expected count caution variant reports assumption diagnostics with the chi-square result")

    drift_detected = p_value < alpha
    severity = "drift_detected" if drift_detected else "normal"
    residuals = _chi_square_residuals(ref_counts, cur_counts, expected_counts, variant_id)
    measurements = {
        "TEST_STATISTIC": statistic,
        "P_VALUE": p_value,
        "DRIFT_ALARM_STATE": severity,
        "THRESHOLD": alpha,
        "METHOD_POLICY": method_policy,
        "DEGREES_OF_FREEDOM": dof,
        "CATEGORY_COUNTS_REFERENCE": dict(zip(categories, ref_counts.astype(float).tolist())),
        "CATEGORY_COUNTS_CURRENT": dict(zip(categories, cur_counts.astype(float).tolist())),
        "CATEGORY_PROPORTION_DELTA": _category_proportion_delta(categories, ref_counts, cur_counts),
        "STANDARDIZED_RESIDUALS": residuals,
        "LOW_EXPECTED_COUNT": low_expected_count,
        "REFERENCE_SAMPLE_SIZE": float(np.sum(ref_counts)),
        "CURRENT_SAMPLE_SIZE": float(np.sum(cur_counts)),
        "SAMPLE_SIZE": {"reference": float(np.sum(ref_counts)), "current": float(np.sum(cur_counts))},
        "CATEGORY_COUNT": len(categories),
    }

    return DriftResult(
        method_id=CHI_SQUARE_METHOD_ID,
        method_name=CHI_SQUARE_METHOD_NAME,
        method_category=METHOD_CATEGORY,
        variant_id=variant_id,
        drift_detected=drift_detected,
        severity=severity,
        drift_score=statistic,
        p_value=p_value,
        test_statistic=statistic,
        threshold=alpha,
        measurements=measurements,
        interpretation=_chi_square_interpretation(
            variant_id=variant_id,
            statistic=statistic,
            p_value=p_value,
            alpha=alpha,
            category_count=len(categories),
            alarm_state=severity,
            low_expected_count=low_expected_count,
        ),
        warnings=warnings,
        metadata=metadata,
    )


def detect_fisher_s_exact_test(
    data: pd.DataFrame,
    *,
    time_col: str = "time",
    value_col: str | None = None,
    reference_window: tuple[str, str] | None = None,
    current_window: tuple[str, str] | None = None,
    params: dict[str, Any] | None = None,
) -> DriftResult:
    params = dict(params or {})
    variant_id = str(params.get("variant_id", "TWO_BY_TWO_FISHER_EXACT")).upper()
    metadata: dict[str, Any] = {"params": dict(params)}

    if variant_id not in SUPPORTED_FISHER_VARIANTS:
        return _fisher_not_applicable(variant_id, f"unsupported Fisher exact variant: {variant_id}", metadata)

    try:
        alpha = _resolve_alpha(params)
        prepared = _prepare_categorical_counts(
            data,
            time_col=time_col,
            category_col=str(params.get("category_col", value_col or "category")),
            count_col=params.get("count_col"),
            reference_window=reference_window,
            current_window=current_window,
            min_reference_size=_positive_int(params.get("min_reference_size", 1), "min_reference_size"),
            min_current_size=_positive_int(params.get("min_current_size", 1), "min_current_size"),
        )
        alternative = str(params.get("alternative", "two-sided")).replace("_", "-")
        if alternative not in {"two-sided", "less", "greater"}:
            raise ValueError("alternative must be two-sided, less, or greater")
    except (KeyError, TypeError, ValueError) as exc:
        return _fisher_not_applicable(variant_id, str(exc), metadata)

    ref_counts = prepared["reference_counts"]
    cur_counts = prepared["current_counts"]
    categories = prepared["categories"]
    warnings = list(prepared["warnings"])
    metadata.update(prepared["metadata"])
    metadata.update({"alpha": alpha, "alternative": alternative})

    table = np.vstack([ref_counts, cur_counts])
    try:
        if variant_id in {"TWO_BY_TWO_FISHER_EXACT", "ONE_SIDED_FISHER_EXACT"}:
            if table.shape != (2, 2):
                raise ValueError(f"{variant_id} requires exactly two categories")
            fisher_alternative = alternative
            if variant_id == "TWO_BY_TWO_FISHER_EXACT":
                fisher_alternative = "two-sided"
            elif alternative == "two-sided":
                fisher_alternative = "greater"
                warnings.append("ONE_SIDED_FISHER_EXACT defaulted alternative to greater")
            odds_ratio, p_value = fisher_exact(table, alternative=fisher_alternative)
            statistic = float(odds_ratio)
            method_policy = f"scipy_fisher_exact_{fisher_alternative}"
        else:
            permutations = _positive_int(params.get("permutations", 2000), "permutations")
            seed = int(params.get("random_state", 0))
            statistic, p_value = _fisher_extended_permutation_pvalue(table, permutations=permutations, seed=seed)
            method_policy = "permutation_chi_square_statistic_fixed_group_sizes"
            metadata.update({"permutations": permutations, "random_state": seed})
            warnings.append("EXTENDED_CONTINGENCY_EXACT_TEST uses a deterministic permutation exact-test surrogate")
    except ValueError as exc:
        return _fisher_not_applicable(variant_id, str(exc), metadata, warnings)

    drift_detected = bool(p_value < alpha)
    severity = "drift_detected" if drift_detected else "normal"
    measurements = {
        "TEST_STATISTIC": statistic,
        "P_VALUE": float(p_value),
        "DRIFT_ALARM_STATE": severity,
        "THRESHOLD": alpha,
        "METHOD_POLICY": method_policy,
        "CATEGORY_COUNTS_REFERENCE": dict(zip(categories, ref_counts.astype(float).tolist())),
        "CATEGORY_COUNTS_CURRENT": dict(zip(categories, cur_counts.astype(float).tolist())),
        "CATEGORY_PROPORTION_DELTA": _category_proportion_delta(categories, ref_counts, cur_counts),
        "ODDS_RATIO": statistic if table.shape == (2, 2) else None,
        "REFERENCE_SAMPLE_SIZE": float(np.sum(ref_counts)),
        "CURRENT_SAMPLE_SIZE": float(np.sum(cur_counts)),
        "SAMPLE_SIZE": {"reference": float(np.sum(ref_counts)), "current": float(np.sum(cur_counts))},
        "CATEGORY_COUNT": len(categories),
    }

    return DriftResult(
        method_id=FISHER_METHOD_ID,
        method_name=FISHER_METHOD_NAME,
        method_category=METHOD_CATEGORY,
        variant_id=variant_id,
        drift_detected=drift_detected,
        severity=severity,
        drift_score=statistic,
        p_value=float(p_value),
        test_statistic=statistic,
        threshold=alpha,
        measurements=measurements,
        interpretation=_fisher_interpretation(
            variant_id=variant_id,
            statistic=statistic,
            p_value=float(p_value),
            alpha=alpha,
            category_count=len(categories),
            alarm_state=severity,
            method_policy=method_policy,
        ),
        warnings=warnings,
        metadata=metadata,
    )


def detect_g_test(
    data: pd.DataFrame,
    *,
    time_col: str = "time",
    value_col: str | None = None,
    reference_window: tuple[str, str] | None = None,
    current_window: tuple[str, str] | None = None,
    params: dict[str, Any] | None = None,
) -> DriftResult:
    params = dict(params or {})
    variant_id = str(params.get("variant_id", "LIKELIHOOD_RATIO_G_TEST_INDEPENDENCE")).upper()
    metadata: dict[str, Any] = {"params": dict(params)}

    if variant_id not in SUPPORTED_G_TEST_VARIANTS:
        return _g_test_not_applicable(variant_id, f"unsupported G-test variant: {variant_id}", metadata)

    try:
        alpha = _resolve_alpha(params)
        small_count_threshold = float(params.get("small_count_threshold", 5.0))
        if small_count_threshold < 0:
            raise ValueError("small_count_threshold must be non-negative")
        prepared = _prepare_categorical_counts(
            data,
            time_col=time_col,
            category_col=str(params.get("category_col", value_col or "category")),
            count_col=params.get("count_col"),
            reference_window=reference_window,
            current_window=current_window,
            min_reference_size=_positive_int(params.get("min_reference_size", 1), "min_reference_size"),
            min_current_size=_positive_int(params.get("min_current_size", 1), "min_current_size"),
        )
    except (KeyError, TypeError, ValueError) as exc:
        return _g_test_not_applicable(variant_id, str(exc), metadata)

    ref_counts = prepared["reference_counts"]
    cur_counts = prepared["current_counts"]
    categories = prepared["categories"]
    warnings = list(prepared["warnings"])
    metadata.update(prepared["metadata"])
    metadata.update({"alpha": alpha, "small_count_threshold": small_count_threshold})

    try:
        if variant_id == "LIKELIHOOD_RATIO_G_TEST_GOF":
            expected = _expected_counts_from_reference(ref_counts, float(np.sum(cur_counts)))
            result = power_divergence(f_obs=cur_counts, f_exp=expected, lambda_="log-likelihood")
            statistic = float(result.statistic)
            p_value = float(result.pvalue)
            dof = int(len(categories) - 1)
            expected_counts = expected
            method_policy = "current_counts_vs_reference_expected_likelihood_ratio"
        else:
            table = np.vstack([ref_counts, cur_counts])
            statistic, p_value, dof, expected = chi2_contingency(table, correction=False, lambda_="log-likelihood")
            statistic = float(statistic)
            p_value = float(p_value)
            expected_counts = np.asarray(expected, dtype=float)
            method_policy = "reference_current_g_test_independence"
    except ValueError as exc:
        return _g_test_not_applicable(variant_id, str(exc), metadata, warnings)

    small_expected_count = int(np.sum(expected_counts < small_count_threshold))
    if small_expected_count:
        warnings.append(f"{small_expected_count} expected cells are below {small_count_threshold:g}; G-test approximation may be weak")
    if variant_id == "G_TEST_WITH_SMALL_COUNT_CAUTION":
        warnings.append("small count caution variant reports likelihood-ratio assumption diagnostics")

    drift_detected = bool(p_value < alpha)
    severity = "drift_detected" if drift_detected else "normal"
    measurements = {
        "TEST_STATISTIC": statistic,
        "G_STATISTIC": statistic,
        "P_VALUE": p_value,
        "DRIFT_ALARM_STATE": severity,
        "THRESHOLD": alpha,
        "METHOD_POLICY": method_policy,
        "DEGREES_OF_FREEDOM": dof,
        "CATEGORY_COUNTS_REFERENCE": dict(zip(categories, ref_counts.astype(float).tolist())),
        "CATEGORY_COUNTS_CURRENT": dict(zip(categories, cur_counts.astype(float).tolist())),
        "CATEGORY_PROPORTION_DELTA": _category_proportion_delta(categories, ref_counts, cur_counts),
        "SMALL_EXPECTED_COUNT": small_expected_count,
        "REFERENCE_SAMPLE_SIZE": float(np.sum(ref_counts)),
        "CURRENT_SAMPLE_SIZE": float(np.sum(cur_counts)),
        "SAMPLE_SIZE": {"reference": float(np.sum(ref_counts)), "current": float(np.sum(cur_counts))},
        "CATEGORY_COUNT": len(categories),
    }

    return DriftResult(
        method_id=G_TEST_METHOD_ID,
        method_name=G_TEST_METHOD_NAME,
        method_category=METHOD_CATEGORY,
        variant_id=variant_id,
        drift_detected=drift_detected,
        severity=severity,
        drift_score=statistic,
        p_value=p_value,
        test_statistic=statistic,
        threshold=alpha,
        measurements=measurements,
        interpretation=_g_test_interpretation(
            variant_id=variant_id,
            statistic=statistic,
            p_value=p_value,
            alpha=alpha,
            category_count=len(categories),
            alarm_state=severity,
            small_expected_count=small_expected_count,
        ),
        warnings=warnings,
        metadata=metadata,
    )


def detect_psi(
    data: pd.DataFrame,
    *,
    time_col: str = "time",
    value_col: str | None = "value",
    reference_window: tuple[str, str] | None = None,
    current_window: tuple[str, str] | None = None,
    params: dict[str, Any] | None = None,
) -> DriftResult:
    params = dict(params or {})
    variant_id = str(params.get("variant_id", "NUMERIC_BINNED_PSI")).upper()
    metadata: dict[str, Any] = {"params": dict(params)}

    if variant_id not in SUPPORTED_PSI_VARIANTS:
        return _psi_not_applicable(variant_id, f"unsupported PSI variant: {variant_id}", metadata)

    try:
        threshold = float(params.get("threshold", params.get("threshold_or_alpha", 0.25)))
        if threshold < 0:
            raise ValueError("threshold must be non-negative")
        epsilon = float(params.get("epsilon", 1e-6))
        if epsilon <= 0:
            raise ValueError("epsilon must be positive")
        if variant_id == "NUMERIC_BINNED_PSI":
            prepared = prepare_numeric_windows(
                data,
                time_col=time_col,
                value_col=_resolve_value_col(value_col, params),
                reference_window=reference_window,
                current_window=current_window,
            )
            min_reference_size = _positive_int(params.get("min_reference_size", 20), "min_reference_size")
            min_current_size = _positive_int(params.get("min_current_size", 20), "min_current_size")
            if len(prepared.reference_values) < min_reference_size:
                raise ValueError(f"effective reference sample size {len(prepared.reference_values)} is below min_reference_size {min_reference_size}")
            if len(prepared.current_values) < min_current_size:
                raise ValueError(f"effective current sample size {len(prepared.current_values)} is below min_current_size {min_current_size}")
            bin_count = _positive_int(params.get("bin_count", 10), "bin_count")
            categories, ref_counts, cur_counts = _numeric_psi_bins(prepared.reference_values, prepared.current_values, bin_count)
            warnings = list(prepared.warnings)
            metadata.update(prepared.metadata)
            metadata.update({"value_col": _resolve_value_col(value_col, params), "bin_count": bin_count})
        else:
            category_param = "score_band_col" if variant_id == "SCORE_BAND_PSI" else "category_col"
            category_col = str(params.get(category_param, params.get("category_col", value_col or "category")))
            prepared_counts = _prepare_categorical_counts(
                data,
                time_col=time_col,
                category_col=category_col,
                count_col=params.get("count_col"),
                reference_window=reference_window,
                current_window=current_window,
                min_reference_size=_positive_int(params.get("min_reference_size", 1), "min_reference_size"),
                min_current_size=_positive_int(params.get("min_current_size", 1), "min_current_size"),
            )
            categories = prepared_counts["categories"]
            ref_counts = prepared_counts["reference_counts"]
            cur_counts = prepared_counts["current_counts"]
            warnings = list(prepared_counts["warnings"])
            metadata.update(prepared_counts["metadata"])
            if variant_id == "POPULATION_WEIGHTED_PSI" and params.get("count_col") is None:
                warnings.append("POPULATION_WEIGHTED_PSI used row counts because count_col was not supplied")
    except (KeyError, TypeError, ValueError) as exc:
        return _psi_not_applicable(variant_id, str(exc), metadata)

    psi_score, contributions = _psi_from_counts(categories, ref_counts, cur_counts, epsilon)
    drift_detected = bool(psi_score > threshold)
    severity = "drift_detected" if drift_detected else "normal"
    measurements = {
        "PSI_SCORE": psi_score,
        "TEST_STATISTIC": psi_score,
        "P_VALUE": None,
        "DRIFT_ALARM_STATE": severity,
        "THRESHOLD": threshold,
        "METHOD_POLICY": "psi_threshold",
        "PSI_CONTRIBUTION": contributions,
        "CATEGORY_COUNTS_REFERENCE": dict(zip(categories, ref_counts.astype(float).tolist())),
        "CATEGORY_COUNTS_CURRENT": dict(zip(categories, cur_counts.astype(float).tolist())),
        "REFERENCE_SAMPLE_SIZE": float(np.sum(ref_counts)),
        "CURRENT_SAMPLE_SIZE": float(np.sum(cur_counts)),
        "SAMPLE_SIZE": {"reference": float(np.sum(ref_counts)), "current": float(np.sum(cur_counts))},
        "CATEGORY_COUNT": len(categories),
    }

    return DriftResult(
        method_id=PSI_METHOD_ID,
        method_name=PSI_METHOD_NAME,
        method_category=METHOD_CATEGORY,
        variant_id=variant_id,
        drift_detected=drift_detected,
        severity=severity,
        drift_score=psi_score,
        p_value=None,
        test_statistic=psi_score,
        threshold=threshold,
        measurements=measurements,
        interpretation=_psi_interpretation(
            variant_id=variant_id,
            psi_score=psi_score,
            threshold=threshold,
            category_count=len(categories),
            alarm_state=severity,
        ),
        warnings=warnings,
        metadata=metadata,
    )


def detect_kl_divergence(
    data: pd.DataFrame,
    *,
    time_col: str = "time",
    value_col: str | None = "value",
    reference_window: tuple[str, str] | None = None,
    current_window: tuple[str, str] | None = None,
    params: dict[str, Any] | None = None,
) -> DriftResult:
    params = dict(params or {})
    variant_id = str(params.get("variant_id", "DISCRETE_KL_DIVERGENCE")).upper()
    metadata: dict[str, Any] = {"params": dict(params)}

    if variant_id not in SUPPORTED_KL_VARIANTS:
        return _kl_not_applicable(variant_id, f"unsupported KL Divergence variant: {variant_id}", metadata)

    try:
        threshold = float(params.get("threshold", params.get("threshold_or_alpha", 0.1)))
        if threshold < 0:
            raise ValueError("threshold must be non-negative")
        epsilon = float(params.get("epsilon", 1e-12))
        if epsilon <= 0:
            raise ValueError("epsilon must be positive")

        if variant_id == "HISTOGRAM_KL_DIVERGENCE":
            resolved_value_col = _resolve_value_col(value_col, params)
            prepared = prepare_numeric_windows(
                data,
                time_col=time_col,
                value_col=resolved_value_col,
                reference_window=reference_window,
                current_window=current_window,
            )
            min_reference_size = _positive_int(params.get("min_reference_size", 20), "min_reference_size")
            min_current_size = _positive_int(params.get("min_current_size", 20), "min_current_size")
            if len(prepared.reference_values) < min_reference_size:
                raise ValueError(f"effective reference sample size {len(prepared.reference_values)} is below min_reference_size {min_reference_size}")
            if len(prepared.current_values) < min_current_size:
                raise ValueError(f"effective current sample size {len(prepared.current_values)} is below min_current_size {min_current_size}")
            bin_count = _positive_int(params.get("bin_count", 10), "bin_count")
            categories, ref_counts, cur_counts = _numeric_psi_bins(prepared.reference_values, prepared.current_values, bin_count)
            warnings = list(prepared.warnings)
            metadata.update(prepared.metadata)
            metadata.update({"value_col": resolved_value_col, "bin_count": bin_count})
        else:
            category_col = str(params.get("category_col", value_col or "category"))
            prepared_counts = _prepare_categorical_counts(
                data,
                time_col=time_col,
                category_col=category_col,
                count_col=params.get("count_col"),
                reference_window=reference_window,
                current_window=current_window,
                min_reference_size=_positive_int(params.get("min_reference_size", 1), "min_reference_size"),
                min_current_size=_positive_int(params.get("min_current_size", 1), "min_current_size"),
            )
            categories = prepared_counts["categories"]
            ref_counts = prepared_counts["reference_counts"]
            cur_counts = prepared_counts["current_counts"]
            warnings = list(prepared_counts["warnings"])
            metadata.update(prepared_counts["metadata"])
            metadata.update({"category_col": category_col})
            if variant_id == "SMOOTHED_KL_DIVERGENCE":
                warnings.append(f"SMOOTHED_KL_DIVERGENCE applied epsilon={epsilon:g} smoothing before normalization")
    except (KeyError, TypeError, ValueError) as exc:
        return _kl_not_applicable(variant_id, str(exc), metadata)

    kl_result = _kl_from_counts(categories, ref_counts, cur_counts, epsilon, symmetrized=variant_id == "SYMMETRIZED_KL")
    kl_score = kl_result["score"]
    drift_detected = bool(kl_score > threshold)
    severity = "drift_detected" if drift_detected else "normal"
    measurements = {
        "KL_DIVERGENCE": kl_score,
        "KL_CURRENT_REFERENCE": kl_result["current_reference"],
        "KL_REFERENCE_CURRENT": kl_result["reference_current"],
        "TEST_STATISTIC": kl_score,
        "P_VALUE": None,
        "DRIFT_ALARM_STATE": severity,
        "THRESHOLD": threshold,
        "METHOD_POLICY": "kl_divergence_threshold",
        "KL_CONTRIBUTION": kl_result["contributions"],
        "CATEGORY_COUNTS_REFERENCE": dict(zip(categories, ref_counts.astype(float).tolist())),
        "CATEGORY_COUNTS_CURRENT": dict(zip(categories, cur_counts.astype(float).tolist())),
        "REFERENCE_SAMPLE_SIZE": float(np.sum(ref_counts)),
        "CURRENT_SAMPLE_SIZE": float(np.sum(cur_counts)),
        "SAMPLE_SIZE": {"reference": float(np.sum(ref_counts)), "current": float(np.sum(cur_counts))},
        "CATEGORY_COUNT": len(categories),
        "EPSILON": epsilon,
    }

    return DriftResult(
        method_id=KL_METHOD_ID,
        method_name=KL_METHOD_NAME,
        method_category=METHOD_CATEGORY,
        variant_id=variant_id,
        drift_detected=drift_detected,
        severity=severity,
        drift_score=kl_score,
        p_value=None,
        test_statistic=kl_score,
        threshold=threshold,
        measurements=measurements,
        interpretation=_kl_interpretation(
            variant_id=variant_id,
            kl_score=kl_score,
            threshold=threshold,
            category_count=len(categories),
            alarm_state=severity,
        ),
        warnings=warnings,
        metadata=metadata,
    )


def detect_jensen_shannon_distance(
    data: pd.DataFrame,
    *,
    time_col: str = "time",
    value_col: str | None = "value",
    reference_window: tuple[str, str] | None = None,
    current_window: tuple[str, str] | None = None,
    params: dict[str, Any] | None = None,
) -> DriftResult:
    params = dict(params or {})
    variant_id = str(params.get("variant_id", "JENSEN_SHANNON_DIVERGENCE")).upper()
    metadata: dict[str, Any] = {"params": dict(params)}

    if variant_id not in SUPPORTED_JS_VARIANTS:
        return _js_not_applicable(variant_id, f"unsupported Jensen-Shannon Distance variant: {variant_id}", metadata)

    try:
        threshold = float(params.get("threshold", params.get("threshold_or_alpha", 0.1)))
        if threshold < 0:
            raise ValueError("threshold must be non-negative")
        epsilon = float(params.get("epsilon", 1e-12))
        if epsilon <= 0:
            raise ValueError("epsilon must be positive")

        input_mode = params.get("input_mode")
        if input_mode == "numeric_histogram":
            if variant_id not in {"JENSEN_SHANNON_DIVERGENCE", "JENSEN_SHANNON_DISTANCE"}:
                raise ValueError(f"{variant_id} does not support input_mode='numeric_histogram'")
            resolved_value_col = _resolve_value_col(value_col, params)
            prepared = prepare_numeric_windows(
                data,
                time_col=time_col,
                value_col=resolved_value_col,
                reference_window=reference_window,
                current_window=current_window,
            )
            min_reference_size = _positive_int(params.get("min_reference_size", 20), "min_reference_size")
            min_current_size = _positive_int(params.get("min_current_size", 20), "min_current_size")
            if len(prepared.reference_values) < min_reference_size:
                raise ValueError(f"effective reference sample size {len(prepared.reference_values)} is below min_reference_size {min_reference_size}")
            if len(prepared.current_values) < min_current_size:
                raise ValueError(f"effective current sample size {len(prepared.current_values)} is below min_current_size {min_current_size}")
            bin_count = _positive_int(params.get("bin_count", 10), "bin_count")
            categories, ref_counts, cur_counts = _numeric_psi_bins(prepared.reference_values, prepared.current_values, bin_count)
            warnings = list(prepared.warnings)
            metadata.update(prepared.metadata)
            metadata.update({"value_col": resolved_value_col, "bin_count": bin_count, "input_mode": "numeric_histogram"})
        else:
            category_col = str(params.get("category_col", value_col or "category"))
            prepared_counts = _prepare_categorical_counts(
                data,
                time_col=time_col,
                category_col=category_col,
                count_col=params.get("count_col"),
                reference_window=reference_window,
                current_window=current_window,
                min_reference_size=_positive_int(params.get("min_reference_size", 1), "min_reference_size"),
                min_current_size=_positive_int(params.get("min_current_size", 1), "min_current_size"),
            )
            categories = prepared_counts["categories"]
            ref_counts = prepared_counts["reference_counts"]
            cur_counts = prepared_counts["current_counts"]
            warnings = list(prepared_counts["warnings"])
            metadata.update(prepared_counts["metadata"])
            metadata.update({"category_col": category_col, "input_mode": "categorical_counts"})
            if variant_id in {"MULTICLASS_PROBABILITY_JS", "TEXT_TOPIC_JS"}:
                warnings.append(f"{variant_id} uses category/count proportions as the probability distribution contract")
    except (KeyError, TypeError, ValueError) as exc:
        return _js_not_applicable(variant_id, str(exc), metadata)

    js_result = _js_from_counts(categories, ref_counts, cur_counts, epsilon)
    score = js_result["distance"] if variant_id == "JENSEN_SHANNON_DISTANCE" else js_result["divergence"]
    drift_detected = bool(score > threshold)
    severity = "drift_detected" if drift_detected else "normal"
    measurements = {
        "JENSEN_SHANNON_DIVERGENCE": js_result["divergence"],
        "JENSEN_SHANNON_DISTANCE": js_result["distance"],
        "TEST_STATISTIC": score,
        "P_VALUE": None,
        "DRIFT_ALARM_STATE": severity,
        "THRESHOLD": threshold,
        "METHOD_POLICY": "jensen_shannon_threshold",
        "JENSEN_SHANNON_CONTRIBUTION": js_result["contributions"],
        "CATEGORY_PROPORTION_DELTA": _category_proportion_delta(categories, ref_counts, cur_counts),
        "CATEGORY_COUNTS_REFERENCE": dict(zip(categories, ref_counts.astype(float).tolist())),
        "CATEGORY_COUNTS_CURRENT": dict(zip(categories, cur_counts.astype(float).tolist())),
        "REFERENCE_SAMPLE_SIZE": float(np.sum(ref_counts)),
        "CURRENT_SAMPLE_SIZE": float(np.sum(cur_counts)),
        "SAMPLE_SIZE": {"reference": float(np.sum(ref_counts)), "current": float(np.sum(cur_counts))},
        "CATEGORY_COUNT": len(categories),
        "EPSILON": epsilon,
    }

    return DriftResult(
        method_id=JS_METHOD_ID,
        method_name=JS_METHOD_NAME,
        method_category=METHOD_CATEGORY,
        variant_id=variant_id,
        drift_detected=drift_detected,
        severity=severity,
        drift_score=score,
        p_value=None,
        test_statistic=score,
        threshold=threshold,
        measurements=measurements,
        interpretation=_js_interpretation(
            variant_id=variant_id,
            js_score=score,
            threshold=threshold,
            category_count=len(categories),
            alarm_state=severity,
            score_name="distance" if variant_id == "JENSEN_SHANNON_DISTANCE" else "divergence",
        ),
        warnings=warnings,
        metadata=metadata,
    )


def detect_hellinger_distance(
    data: pd.DataFrame,
    *,
    time_col: str = "time",
    value_col: str | None = "value",
    reference_window: tuple[str, str] | None = None,
    current_window: tuple[str, str] | None = None,
    params: dict[str, Any] | None = None,
) -> DriftResult:
    params = dict(params or {})
    variant_id = str(params.get("variant_id", "DISCRETE_HELLINGER_DISTANCE")).upper()
    metadata: dict[str, Any] = {"params": dict(params)}

    if variant_id not in SUPPORTED_HELLINGER_VARIANTS:
        return _hellinger_not_applicable(variant_id, f"unsupported Hellinger Distance variant: {variant_id}", metadata)

    try:
        threshold = float(params.get("threshold", params.get("threshold_or_alpha", 0.1)))
        if threshold < 0:
            raise ValueError("threshold must be non-negative")

        if variant_id == "HISTOGRAM_HELLINGER_DISTANCE":
            resolved_value_col = _resolve_value_col(value_col, params)
            prepared = prepare_numeric_windows(
                data,
                time_col=time_col,
                value_col=resolved_value_col,
                reference_window=reference_window,
                current_window=current_window,
            )
            min_reference_size = _positive_int(params.get("min_reference_size", 20), "min_reference_size")
            min_current_size = _positive_int(params.get("min_current_size", 20), "min_current_size")
            if len(prepared.reference_values) < min_reference_size:
                raise ValueError(f"effective reference sample size {len(prepared.reference_values)} is below min_reference_size {min_reference_size}")
            if len(prepared.current_values) < min_current_size:
                raise ValueError(f"effective current sample size {len(prepared.current_values)} is below min_current_size {min_current_size}")
            bin_count = _positive_int(params.get("bin_count", 10), "bin_count")
            categories, ref_counts, cur_counts = _numeric_psi_bins(prepared.reference_values, prepared.current_values, bin_count)
            warnings = list(prepared.warnings)
            metadata.update(prepared.metadata)
            metadata.update({"value_col": resolved_value_col, "bin_count": bin_count, "input_mode": "numeric_histogram"})
        else:
            category_col = str(params.get("category_col", value_col or "category"))
            prepared_counts = _prepare_categorical_counts(
                data,
                time_col=time_col,
                category_col=category_col,
                count_col=params.get("count_col"),
                reference_window=reference_window,
                current_window=current_window,
                min_reference_size=_positive_int(params.get("min_reference_size", 1), "min_reference_size"),
                min_current_size=_positive_int(params.get("min_current_size", 1), "min_current_size"),
            )
            categories = prepared_counts["categories"]
            ref_counts = prepared_counts["reference_counts"]
            cur_counts = prepared_counts["current_counts"]
            warnings = list(prepared_counts["warnings"])
            metadata.update(prepared_counts["metadata"])
            metadata.update({"category_col": category_col, "input_mode": "categorical_counts"})
    except (KeyError, TypeError, ValueError) as exc:
        return _hellinger_not_applicable(variant_id, str(exc), metadata)

    hellinger_result = _hellinger_from_counts(categories, ref_counts, cur_counts)
    distance = hellinger_result["distance"]
    drift_detected = bool(distance > threshold)
    severity = "drift_detected" if drift_detected else "normal"
    measurements = {
        "HELLINGER_DISTANCE": distance,
        "TEST_STATISTIC": distance,
        "P_VALUE": None,
        "DRIFT_ALARM_STATE": severity,
        "THRESHOLD": threshold,
        "METHOD_POLICY": "hellinger_distance_threshold",
        "HELLINGER_CONTRIBUTION": hellinger_result["contributions"],
        "CATEGORY_PROPORTION_DELTA": _category_proportion_delta(categories, ref_counts, cur_counts),
        "CATEGORY_COUNTS_REFERENCE": dict(zip(categories, ref_counts.astype(float).tolist())),
        "CATEGORY_COUNTS_CURRENT": dict(zip(categories, cur_counts.astype(float).tolist())),
        "REFERENCE_SAMPLE_SIZE": float(np.sum(ref_counts)),
        "CURRENT_SAMPLE_SIZE": float(np.sum(cur_counts)),
        "SAMPLE_SIZE": {"reference": float(np.sum(ref_counts)), "current": float(np.sum(cur_counts))},
        "CATEGORY_COUNT": len(categories),
    }

    return DriftResult(
        method_id=HELLINGER_METHOD_ID,
        method_name=HELLINGER_METHOD_NAME,
        method_category=METHOD_CATEGORY,
        variant_id=variant_id,
        drift_detected=drift_detected,
        severity=severity,
        drift_score=distance,
        p_value=None,
        test_statistic=distance,
        threshold=threshold,
        measurements=measurements,
        interpretation=_hellinger_interpretation(
            variant_id=variant_id,
            distance=distance,
            threshold=threshold,
            category_count=len(categories),
            alarm_state=severity,
        ),
        warnings=warnings,
        metadata=metadata,
    )


def detect_total_variation_distance(
    data: pd.DataFrame,
    *,
    time_col: str = "time",
    value_col: str | None = "value",
    reference_window: tuple[str, str] | None = None,
    current_window: tuple[str, str] | None = None,
    params: dict[str, Any] | None = None,
) -> DriftResult:
    params = dict(params or {})
    variant_id = str(params.get("variant_id", "CATEGORICAL_TOTAL_VARIATION")).upper()
    metadata: dict[str, Any] = {"params": dict(params)}

    if variant_id not in SUPPORTED_TOTAL_VARIATION_VARIANTS:
        return _total_variation_not_applicable(variant_id, f"unsupported Total Variation Distance variant: {variant_id}", metadata)

    try:
        threshold = float(params.get("threshold", params.get("threshold_or_alpha", 0.1)))
        if threshold < 0:
            raise ValueError("threshold must be non-negative")

        if variant_id == "HISTOGRAM_TOTAL_VARIATION":
            resolved_value_col = _resolve_value_col(value_col, params)
            prepared = prepare_numeric_windows(
                data,
                time_col=time_col,
                value_col=resolved_value_col,
                reference_window=reference_window,
                current_window=current_window,
            )
            min_reference_size = _positive_int(params.get("min_reference_size", 20), "min_reference_size")
            min_current_size = _positive_int(params.get("min_current_size", 20), "min_current_size")
            if len(prepared.reference_values) < min_reference_size:
                raise ValueError(f"effective reference sample size {len(prepared.reference_values)} is below min_reference_size {min_reference_size}")
            if len(prepared.current_values) < min_current_size:
                raise ValueError(f"effective current sample size {len(prepared.current_values)} is below min_current_size {min_current_size}")
            bin_count = _positive_int(params.get("bin_count", 10), "bin_count")
            categories, ref_counts, cur_counts = _numeric_psi_bins(prepared.reference_values, prepared.current_values, bin_count)
            warnings = list(prepared.warnings)
            metadata.update(prepared.metadata)
            metadata.update({"value_col": resolved_value_col, "bin_count": bin_count, "input_mode": "numeric_histogram"})
        else:
            category_col = str(params.get("category_col", value_col or "category"))
            prepared_counts = _prepare_categorical_counts(
                data,
                time_col=time_col,
                category_col=category_col,
                count_col=params.get("count_col"),
                reference_window=reference_window,
                current_window=current_window,
                min_reference_size=_positive_int(params.get("min_reference_size", 1), "min_reference_size"),
                min_current_size=_positive_int(params.get("min_current_size", 1), "min_current_size"),
            )
            categories = prepared_counts["categories"]
            ref_counts = prepared_counts["reference_counts"]
            cur_counts = prepared_counts["current_counts"]
            warnings = list(prepared_counts["warnings"])
            metadata.update(prepared_counts["metadata"])
            metadata.update({"category_col": category_col, "input_mode": "categorical_counts"})
            if variant_id == "PROBABILITY_VECTOR_TOTAL_VARIATION":
                warnings.append("PROBABILITY_VECTOR_TOTAL_VARIATION uses category/count proportions as the probability vector contract")
    except (KeyError, TypeError, ValueError) as exc:
        return _total_variation_not_applicable(variant_id, str(exc), metadata)

    tv_result = _total_variation_from_counts(categories, ref_counts, cur_counts)
    distance = tv_result["distance"]
    drift_detected = bool(distance > threshold)
    severity = "drift_detected" if drift_detected else "normal"
    measurements = {
        "TOTAL_VARIATION_DISTANCE": distance,
        "TEST_STATISTIC": distance,
        "P_VALUE": None,
        "DRIFT_ALARM_STATE": severity,
        "THRESHOLD": threshold,
        "METHOD_POLICY": "total_variation_distance_threshold",
        "TOTAL_VARIATION_CONTRIBUTION": tv_result["contributions"],
        "CATEGORY_PROPORTION_DELTA": _category_proportion_delta(categories, ref_counts, cur_counts),
        "CATEGORY_COUNTS_REFERENCE": dict(zip(categories, ref_counts.astype(float).tolist())),
        "CATEGORY_COUNTS_CURRENT": dict(zip(categories, cur_counts.astype(float).tolist())),
        "REFERENCE_SAMPLE_SIZE": float(np.sum(ref_counts)),
        "CURRENT_SAMPLE_SIZE": float(np.sum(cur_counts)),
        "SAMPLE_SIZE": {"reference": float(np.sum(ref_counts)), "current": float(np.sum(cur_counts))},
        "CATEGORY_COUNT": len(categories),
    }

    return DriftResult(
        method_id=TOTAL_VARIATION_METHOD_ID,
        method_name=TOTAL_VARIATION_METHOD_NAME,
        method_category=METHOD_CATEGORY,
        variant_id=variant_id,
        drift_detected=drift_detected,
        severity=severity,
        drift_score=distance,
        p_value=None,
        test_statistic=distance,
        threshold=threshold,
        measurements=measurements,
        interpretation=_total_variation_interpretation(
            variant_id=variant_id,
            distance=distance,
            threshold=threshold,
            category_count=len(categories),
            alarm_state=severity,
        ),
        warnings=warnings,
        metadata=metadata,
    )


def detect_l_infinity_distance(
    data: pd.DataFrame,
    *,
    time_col: str = "time",
    value_col: str | None = "value",
    reference_window: tuple[str, str] | None = None,
    current_window: tuple[str, str] | None = None,
    params: dict[str, Any] | None = None,
) -> DriftResult:
    params = dict(params or {})
    variant_id = str(params.get("variant_id", "CATEGORICAL_L_INFINITY")).upper()
    metadata: dict[str, Any] = {"params": dict(params)}

    if variant_id not in SUPPORTED_L_INFINITY_VARIANTS:
        return _l_infinity_not_applicable(variant_id, f"unsupported L-Infinity Distance variant: {variant_id}", metadata)

    try:
        threshold = float(params.get("threshold", params.get("threshold_or_alpha", 0.1)))
        if threshold < 0:
            raise ValueError("threshold must be non-negative")

        if variant_id == "BINNED_NUMERIC_L_INFINITY":
            resolved_value_col = _resolve_value_col(value_col, params)
            prepared = prepare_numeric_windows(
                data,
                time_col=time_col,
                value_col=resolved_value_col,
                reference_window=reference_window,
                current_window=current_window,
            )
            min_reference_size = _positive_int(params.get("min_reference_size", 20), "min_reference_size")
            min_current_size = _positive_int(params.get("min_current_size", 20), "min_current_size")
            if len(prepared.reference_values) < min_reference_size:
                raise ValueError(f"effective reference sample size {len(prepared.reference_values)} is below min_reference_size {min_reference_size}")
            if len(prepared.current_values) < min_current_size:
                raise ValueError(f"effective current sample size {len(prepared.current_values)} is below min_current_size {min_current_size}")
            bin_count = _positive_int(params.get("bin_count", 10), "bin_count")
            categories, ref_counts, cur_counts = _numeric_psi_bins(prepared.reference_values, prepared.current_values, bin_count)
            warnings = list(prepared.warnings)
            metadata.update(prepared.metadata)
            metadata.update({"value_col": resolved_value_col, "bin_count": bin_count, "input_mode": "numeric_histogram"})
        else:
            category_col = str(params.get("category_col", value_col or "category"))
            prepared_counts = _prepare_categorical_counts(
                data,
                time_col=time_col,
                category_col=category_col,
                count_col=params.get("count_col"),
                reference_window=reference_window,
                current_window=current_window,
                min_reference_size=_positive_int(params.get("min_reference_size", 1), "min_reference_size"),
                min_current_size=_positive_int(params.get("min_current_size", 1), "min_current_size"),
            )
            categories = prepared_counts["categories"]
            ref_counts = prepared_counts["reference_counts"]
            cur_counts = prepared_counts["current_counts"]
            warnings = list(prepared_counts["warnings"])
            metadata.update(prepared_counts["metadata"])
            metadata.update({"category_col": category_col, "input_mode": "categorical_counts"})
            if variant_id == "PROBABILITY_VECTOR_L_INFINITY":
                warnings.append("PROBABILITY_VECTOR_L_INFINITY uses category/count proportions as the probability vector contract")
    except (KeyError, TypeError, ValueError) as exc:
        return _l_infinity_not_applicable(variant_id, str(exc), metadata)

    l_inf_result = _l_infinity_from_counts(categories, ref_counts, cur_counts)
    distance = l_inf_result["distance"]
    drift_detected = bool(distance > threshold)
    severity = "drift_detected" if drift_detected else "normal"
    measurements = {
        "L_INFINITY_DISTANCE": distance,
        "MAX_ABSOLUTE_PROPORTION_DELTA": distance,
        "MAX_COMPONENT": l_inf_result["max_component"],
        "TEST_STATISTIC": distance,
        "P_VALUE": None,
        "DRIFT_ALARM_STATE": severity,
        "THRESHOLD": threshold,
        "METHOD_POLICY": "l_infinity_distance_threshold",
        "L_INFINITY_CONTRIBUTION": l_inf_result["contributions"],
        "CATEGORY_PROPORTION_DELTA": _category_proportion_delta(categories, ref_counts, cur_counts),
        "CATEGORY_COUNTS_REFERENCE": dict(zip(categories, ref_counts.astype(float).tolist())),
        "CATEGORY_COUNTS_CURRENT": dict(zip(categories, cur_counts.astype(float).tolist())),
        "REFERENCE_SAMPLE_SIZE": float(np.sum(ref_counts)),
        "CURRENT_SAMPLE_SIZE": float(np.sum(cur_counts)),
        "SAMPLE_SIZE": {"reference": float(np.sum(ref_counts)), "current": float(np.sum(cur_counts))},
        "CATEGORY_COUNT": len(categories),
    }

    return DriftResult(
        method_id=L_INFINITY_METHOD_ID,
        method_name=L_INFINITY_METHOD_NAME,
        method_category=METHOD_CATEGORY,
        variant_id=variant_id,
        drift_detected=drift_detected,
        severity=severity,
        drift_score=distance,
        p_value=None,
        test_statistic=distance,
        threshold=threshold,
        measurements=measurements,
        interpretation=_l_infinity_interpretation(
            variant_id=variant_id,
            distance=distance,
            max_component=l_inf_result["max_component"],
            threshold=threshold,
            category_count=len(categories),
            alarm_state=severity,
        ),
        warnings=warnings,
        metadata=metadata,
    )


def detect_bhattacharyya_distance(
    data: pd.DataFrame,
    *,
    time_col: str = "time",
    value_col: str | None = "value",
    reference_window: tuple[str, str] | None = None,
    current_window: tuple[str, str] | None = None,
    params: dict[str, Any] | None = None,
) -> DriftResult:
    params = dict(params or {})
    variant_id = str(params.get("variant_id", "DISCRETE_BHATTACHARYYA_DISTANCE")).upper()
    metadata: dict[str, Any] = {"params": dict(params)}

    if variant_id not in SUPPORTED_BHATTACHARYYA_VARIANTS:
        return _bhattacharyya_not_applicable(variant_id, f"unsupported Bhattacharyya Distance variant: {variant_id}", metadata)

    try:
        threshold = float(params.get("threshold", params.get("threshold_or_alpha", 0.1)))
        if threshold < 0:
            raise ValueError("threshold must be non-negative")

        if variant_id == "GAUSSIAN_BHATTACHARYYA_DISTANCE":
            resolved_value_col = _resolve_value_col(value_col, params)
            prepared = prepare_numeric_windows(
                data,
                time_col=time_col,
                value_col=resolved_value_col,
                reference_window=reference_window,
                current_window=current_window,
            )
            min_reference_size = _positive_int(params.get("min_reference_size", 20), "min_reference_size")
            min_current_size = _positive_int(params.get("min_current_size", 20), "min_current_size")
            if len(prepared.reference_values) < min_reference_size:
                raise ValueError(f"effective reference sample size {len(prepared.reference_values)} is below min_reference_size {min_reference_size}")
            if len(prepared.current_values) < min_current_size:
                raise ValueError(f"effective current sample size {len(prepared.current_values)} is below min_current_size {min_current_size}")
            bh_result = _gaussian_bhattacharyya_from_values(prepared.reference_values, prepared.current_values)
            warnings = list(prepared.warnings)
            metadata.update(prepared.metadata)
            metadata.update({"value_col": resolved_value_col, "input_mode": "gaussian_numeric"})
            categories: list[str] = []
            ref_counts = np.array([], dtype=float)
            cur_counts = np.array([], dtype=float)
        elif variant_id == "HISTOGRAM_BHATTACHARYYA_DISTANCE":
            resolved_value_col = _resolve_value_col(value_col, params)
            prepared = prepare_numeric_windows(
                data,
                time_col=time_col,
                value_col=resolved_value_col,
                reference_window=reference_window,
                current_window=current_window,
            )
            min_reference_size = _positive_int(params.get("min_reference_size", 20), "min_reference_size")
            min_current_size = _positive_int(params.get("min_current_size", 20), "min_current_size")
            if len(prepared.reference_values) < min_reference_size:
                raise ValueError(f"effective reference sample size {len(prepared.reference_values)} is below min_reference_size {min_reference_size}")
            if len(prepared.current_values) < min_current_size:
                raise ValueError(f"effective current sample size {len(prepared.current_values)} is below min_current_size {min_current_size}")
            bin_count = _positive_int(params.get("bin_count", 10), "bin_count")
            categories, ref_counts, cur_counts = _numeric_psi_bins(prepared.reference_values, prepared.current_values, bin_count)
            bh_result = _bhattacharyya_from_counts(categories, ref_counts, cur_counts)
            warnings = list(prepared.warnings)
            metadata.update(prepared.metadata)
            metadata.update({"value_col": resolved_value_col, "bin_count": bin_count, "input_mode": "numeric_histogram"})
        else:
            category_col = str(params.get("category_col", value_col or "category"))
            prepared_counts = _prepare_categorical_counts(
                data,
                time_col=time_col,
                category_col=category_col,
                count_col=params.get("count_col"),
                reference_window=reference_window,
                current_window=current_window,
                min_reference_size=_positive_int(params.get("min_reference_size", 1), "min_reference_size"),
                min_current_size=_positive_int(params.get("min_current_size", 1), "min_current_size"),
            )
            categories = prepared_counts["categories"]
            ref_counts = prepared_counts["reference_counts"]
            cur_counts = prepared_counts["current_counts"]
            bh_result = _bhattacharyya_from_counts(categories, ref_counts, cur_counts)
            warnings = list(prepared_counts["warnings"])
            metadata.update(prepared_counts["metadata"])
            metadata.update({"category_col": category_col, "input_mode": "categorical_counts"})
    except (KeyError, TypeError, ValueError) as exc:
        return _bhattacharyya_not_applicable(variant_id, str(exc), metadata)

    distance = bh_result["distance"]
    drift_detected = bool(distance > threshold)
    severity = "drift_detected" if drift_detected else "normal"
    measurements = {
        "BHATTACHARYYA_DISTANCE": distance,
        "BHATTACHARYYA_COEFFICIENT": bh_result.get("coefficient"),
        "TEST_STATISTIC": distance,
        "P_VALUE": None,
        "DRIFT_ALARM_STATE": severity,
        "THRESHOLD": threshold,
        "METHOD_POLICY": "bhattacharyya_distance_threshold",
    }
    if variant_id == "GAUSSIAN_BHATTACHARYYA_DISTANCE":
        measurements.update(
            {
                "GAUSSIAN_SUMMARY": bh_result["gaussian_summary"],
                "REFERENCE_SAMPLE_SIZE": int(bh_result["reference_sample_size"]),
                "CURRENT_SAMPLE_SIZE": int(bh_result["current_sample_size"]),
                "SAMPLE_SIZE": {
                    "reference": int(bh_result["reference_sample_size"]),
                    "current": int(bh_result["current_sample_size"]),
                },
            }
        )
    else:
        measurements.update(
            {
                "BHATTACHARYYA_CONTRIBUTION": bh_result["contributions"],
                "CATEGORY_PROPORTION_DELTA": _category_proportion_delta(categories, ref_counts, cur_counts),
                "CATEGORY_COUNTS_REFERENCE": dict(zip(categories, ref_counts.astype(float).tolist())),
                "CATEGORY_COUNTS_CURRENT": dict(zip(categories, cur_counts.astype(float).tolist())),
                "REFERENCE_SAMPLE_SIZE": float(np.sum(ref_counts)),
                "CURRENT_SAMPLE_SIZE": float(np.sum(cur_counts)),
                "SAMPLE_SIZE": {"reference": float(np.sum(ref_counts)), "current": float(np.sum(cur_counts))},
                "CATEGORY_COUNT": len(categories),
            }
        )

    return DriftResult(
        method_id=BHATTACHARYYA_METHOD_ID,
        method_name=BHATTACHARYYA_METHOD_NAME,
        method_category=METHOD_CATEGORY,
        variant_id=variant_id,
        drift_detected=drift_detected,
        severity=severity,
        drift_score=distance,
        p_value=None,
        test_statistic=distance,
        threshold=threshold,
        measurements=measurements,
        interpretation=_bhattacharyya_interpretation(
            variant_id=variant_id,
            distance=distance,
            coefficient=bh_result.get("coefficient"),
            threshold=threshold,
            alarm_state=severity,
        ),
        warnings=warnings,
        metadata=metadata,
    )


def detect_histogram_intersection_normalized_complement(
    data: pd.DataFrame,
    *,
    time_col: str = "time",
    value_col: str | None = "value",
    reference_window: tuple[str, str] | None = None,
    current_window: tuple[str, str] | None = None,
    params: dict[str, Any] | None = None,
) -> DriftResult:
    params = dict(params or {})
    variant_id = str(params.get("variant_id", "HINC_CATEGORICAL")).upper()
    metadata: dict[str, Any] = {"params": dict(params)}

    if variant_id not in SUPPORTED_HINC_VARIANTS:
        return _hinc_not_applicable(variant_id, f"unsupported Histogram Intersection Normalized Complement variant: {variant_id}", metadata)

    try:
        threshold = float(params.get("threshold", params.get("threshold_or_alpha", 0.1)))
        if threshold < 0:
            raise ValueError("threshold must be non-negative")

        if variant_id == "HINC_HISTOGRAM_NUMERIC":
            resolved_value_col = _resolve_value_col(value_col, params)
            prepared = prepare_numeric_windows(
                data,
                time_col=time_col,
                value_col=resolved_value_col,
                reference_window=reference_window,
                current_window=current_window,
            )
            min_reference_size = _positive_int(params.get("min_reference_size", 20), "min_reference_size")
            min_current_size = _positive_int(params.get("min_current_size", 20), "min_current_size")
            if len(prepared.reference_values) < min_reference_size:
                raise ValueError(f"effective reference sample size {len(prepared.reference_values)} is below min_reference_size {min_reference_size}")
            if len(prepared.current_values) < min_current_size:
                raise ValueError(f"effective current sample size {len(prepared.current_values)} is below min_current_size {min_current_size}")
            bin_count = _positive_int(params.get("bin_count", 10), "bin_count")
            categories, ref_counts, cur_counts = _numeric_psi_bins(prepared.reference_values, prepared.current_values, bin_count)
            warnings = list(prepared.warnings)
            metadata.update(prepared.metadata)
            metadata.update({"value_col": resolved_value_col, "bin_count": bin_count, "input_mode": "numeric_histogram"})
        else:
            category_col = str(params.get("category_col", value_col or "category"))
            prepared_counts = _prepare_categorical_counts(
                data,
                time_col=time_col,
                category_col=category_col,
                count_col=params.get("count_col"),
                reference_window=reference_window,
                current_window=current_window,
                min_reference_size=_positive_int(params.get("min_reference_size", 1), "min_reference_size"),
                min_current_size=_positive_int(params.get("min_current_size", 1), "min_current_size"),
            )
            categories = prepared_counts["categories"]
            ref_counts = prepared_counts["reference_counts"]
            cur_counts = prepared_counts["current_counts"]
            warnings = list(prepared_counts["warnings"])
            metadata.update(prepared_counts["metadata"])
            metadata.update({"category_col": category_col, "input_mode": "categorical_counts"})
            if variant_id == "HINC_IMAGE_FEATURE":
                warnings.append("HINC_IMAGE_FEATURE uses category/count feature-bin proportions as the image feature histogram contract")
    except (KeyError, TypeError, ValueError) as exc:
        return _hinc_not_applicable(variant_id, str(exc), metadata)

    hinc_result = _hinc_from_counts(categories, ref_counts, cur_counts)
    score = hinc_result["score"]
    drift_detected = bool(score > threshold)
    severity = "drift_detected" if drift_detected else "normal"
    measurements = {
        "HISTOGRAM_INTERSECTION_NORMALIZED_COMPLEMENT": score,
        "HISTOGRAM_INTERSECTION": hinc_result["intersection"],
        "TEST_STATISTIC": score,
        "P_VALUE": None,
        "DRIFT_ALARM_STATE": severity,
        "THRESHOLD": threshold,
        "METHOD_POLICY": "histogram_intersection_normalized_complement_threshold",
        "HINC_CONTRIBUTION": hinc_result["contributions"],
        "CATEGORY_PROPORTION_DELTA": _category_proportion_delta(categories, ref_counts, cur_counts),
        "CATEGORY_COUNTS_REFERENCE": dict(zip(categories, ref_counts.astype(float).tolist())),
        "CATEGORY_COUNTS_CURRENT": dict(zip(categories, cur_counts.astype(float).tolist())),
        "REFERENCE_SAMPLE_SIZE": float(np.sum(ref_counts)),
        "CURRENT_SAMPLE_SIZE": float(np.sum(cur_counts)),
        "SAMPLE_SIZE": {"reference": float(np.sum(ref_counts)), "current": float(np.sum(cur_counts))},
        "CATEGORY_COUNT": len(categories),
    }

    return DriftResult(
        method_id=HINC_METHOD_ID,
        method_name=HINC_METHOD_NAME,
        method_category=METHOD_CATEGORY,
        variant_id=variant_id,
        drift_detected=drift_detected,
        severity=severity,
        drift_score=score,
        p_value=None,
        test_statistic=score,
        threshold=threshold,
        measurements=measurements,
        interpretation=_hinc_interpretation(
            variant_id=variant_id,
            score=score,
            intersection=hinc_result["intersection"],
            threshold=threshold,
            category_count=len(categories),
            alarm_state=severity,
        ),
        warnings=warnings,
        metadata=metadata,
    )


def detect_mann_whitney_u_wilcoxon_rank_sum_test(
    data: pd.DataFrame,
    *,
    time_col: str = "time",
    value_col: str | None = "value",
    reference_window: tuple[str, str] | None = None,
    current_window: tuple[str, str] | None = None,
    params: dict[str, Any] | None = None,
) -> DriftResult:
    params = dict(params or {})
    variant_id = params.get("variant_id", "MANN_WHITNEY_TWO_SIDED")
    metadata: dict[str, Any] = {"params": dict(params)}

    if variant_id not in SUPPORTED_MANN_WHITNEY_VARIANTS:
        return _mann_whitney_not_applicable(variant_id, f"unsupported Mann-Whitney variant: {variant_id}", metadata)

    try:
        alpha = _resolve_alpha(params)
        alternative = _resolve_mann_whitney_alternative(variant_id, params)
        min_reference_size = _positive_int(params.get("min_reference_size", 5), "min_reference_size")
        min_current_size = _positive_int(params.get("min_current_size", 5), "min_current_size")
        p_value_method = _resolve_mann_whitney_method(variant_id, params)
        continuity_correction = _bool_param(params.get("continuity_correction", True), "continuity_correction")
        tie_correction = _bool_param(params.get("tie_correction", True), "tie_correction")
        exact_max_sample_size = _positive_int(params.get("exact_max_sample_size", 8), "exact_max_sample_size")
        exact_fallback = str(params.get("exact_fallback", "not_applicable"))
        if exact_fallback not in {"not_applicable", "asymptotic"}:
            raise ValueError("exact_fallback must be one of not_applicable, asymptotic")
        value_col = _resolve_value_col(value_col, params)
    except (TypeError, ValueError) as exc:
        return _mann_whitney_not_applicable(variant_id, str(exc), metadata)

    if value_col in data.columns and pd.api.types.is_bool_dtype(data[value_col]):
        return _mann_whitney_not_applicable(variant_id, "boolean value column is not valid numeric rank input", metadata)

    try:
        prepared = prepare_numeric_windows(
            data,
            time_col=time_col,
            value_col=value_col,
            reference_window=reference_window,
            current_window=current_window,
        )
    except (KeyError, ValueError) as exc:
        return _mann_whitney_not_applicable(variant_id, str(exc), metadata)

    warnings = list(prepared.warnings)
    reference_values = prepared.reference_values
    current_values = prepared.current_values
    metadata.update(prepared.metadata)
    metadata.update(
        {
            "value_col": value_col,
            "alpha": alpha,
            "alternative": alternative,
            "continuity_correction": continuity_correction,
            "tie_correction": tie_correction,
            "exact_max_sample_size": exact_max_sample_size,
            "exact_fallback": exact_fallback,
        }
    )

    if len(reference_values) < min_reference_size:
        return _mann_whitney_not_applicable(
            variant_id,
            f"effective reference sample size {len(reference_values)} is below min_reference_size {min_reference_size}",
            metadata,
            warnings,
        )
    if len(current_values) < min_current_size:
        return _mann_whitney_not_applicable(
            variant_id,
            f"effective current sample size {len(current_values)} is below min_current_size {min_current_size}",
            metadata,
            warnings,
        )

    has_ties = _has_ties(reference_values, current_values)
    if has_ties:
        warnings.append("ties detected; asymptotic tie correction is required for reliable p-value interpretation")
    if max(len(reference_values), len(current_values)) / min(len(reference_values), len(current_values)) > 10:
        warnings.append("reference/current sample sizes are highly imbalanced")

    resolved_method = p_value_method
    exact_preconditions = (
        len(reference_values) <= exact_max_sample_size
        and len(current_values) <= exact_max_sample_size
        and not has_ties
    )
    if p_value_method == "auto":
        resolved_method = "exact" if exact_preconditions else "asymptotic"
    if variant_id == "MANN_WHITNEY_EXACT" and not exact_preconditions:
        if exact_fallback == "asymptotic":
            resolved_method = "asymptotic"
            warnings.append("exact preconditions failed; falling back to asymptotic Mann-Whitney calculation")
        else:
            return _mann_whitney_not_applicable(
                variant_id,
                "exact Mann-Whitney requires both sample sizes <= exact_max_sample_size and no ties",
                metadata,
                warnings,
            )
    if resolved_method == "exact" and has_ties:
        return _mann_whitney_not_applicable(variant_id, "exact Mann-Whitney does not support ties", metadata, warnings)
    if resolved_method == "asymptotic" and not tie_correction and has_ties:
        return _mann_whitney_not_applicable(variant_id, "tie_correction must be true when ties are present", metadata, warnings)
    metadata["p_value_method"] = resolved_method

    try:
        stat = mannwhitneyu(
            reference_values,
            current_values,
            use_continuity=continuity_correction,
            alternative=alternative,
            method=resolved_method,
        )
        u_statistic = float(stat.statistic)
        p_value = float(stat.pvalue)
    except ValueError as exc:
        return _mmd_not_applicable(variant_id, str(exc), metadata, warnings)
    except ValueError as exc:
        return _mmd_not_applicable(variant_id, str(exc), metadata, warnings)
    except Exception as exc:
        return DriftResult(
            method_id=MANN_WHITNEY_METHOD_ID,
            method_name=MANN_WHITNEY_METHOD_NAME,
            method_category=METHOD_CATEGORY,
            variant_id=variant_id,
            drift_detected=None,
            severity="error",
            threshold=alpha,
            interpretation=f"Mann-Whitney calculation failed: {exc}",
            warnings=warnings + [f"mannwhitneyu failed: {exc}"],
            metadata=metadata,
        )

    if not np.isfinite(u_statistic) or not np.isfinite(p_value):
        return _mann_whitney_not_applicable(variant_id, "Mann-Whitney statistic or p-value is not finite", metadata, warnings)

    drift_detected = bool(p_value < alpha)
    severity = "drift_detected" if drift_detected else "normal"
    alarm_state = "drift_detected" if drift_detected else "normal"
    rank_biserial = 1.0 - (2.0 * u_statistic) / (len(reference_values) * len(current_values))
    metadata["rank_biserial_orientation"] = "1 - 2 * U_reference / (n_reference * n_current)"

    measurements = {
        "TEST_STATISTIC": u_statistic,
        "MANN_WHITNEY_U_STATISTIC": u_statistic,
        "P_VALUE": p_value,
        "DRIFT_ALARM_STATE": alarm_state,
        "SAMPLE_SIZE": {
            "reference": int(len(reference_values)),
            "current": int(len(current_values)),
            "dropped_reference": int(metadata.get("reference_original_count", len(reference_values)) - len(reference_values)),
            "dropped_current": int(metadata.get("current_original_count", len(current_values)) - len(current_values)),
        },
        "SAMPLE_SIZE_REFERENCE": int(len(reference_values)),
        "SAMPLE_SIZE_CURRENT": int(len(current_values)),
        "RANK_BISERIAL_CORRELATION": float(rank_biserial),
    }

    return DriftResult(
        method_id=MANN_WHITNEY_METHOD_ID,
        method_name=MANN_WHITNEY_METHOD_NAME,
        method_category=METHOD_CATEGORY,
        variant_id=variant_id,
        drift_detected=drift_detected,
        severity=severity,
        drift_score=abs(float(rank_biserial)),
        p_value=p_value,
        test_statistic=u_statistic,
        threshold=alpha,
        measurements=measurements,
        interpretation=_mann_whitney_interpretation(
            variant_id=variant_id,
            alternative=alternative,
            reference_count=len(reference_values),
            current_count=len(current_values),
            u_statistic=u_statistic,
            p_value=p_value,
            alpha=alpha,
            drift_detected=drift_detected,
            warnings=warnings,
        ),
        warnings=warnings,
        metadata=metadata,
    )


def detect_t_test(
    data: pd.DataFrame,
    *,
    time_col: str = "time",
    value_col: str | None = "value",
    reference_window: tuple[str, str] | None = None,
    current_window: tuple[str, str] | None = None,
    params: dict[str, Any] | None = None,
) -> DriftResult:
    params = dict(params or {})
    variant_id = params.get("variant_id", "WELCH_T_TEST")
    metadata: dict[str, Any] = {"params": dict(params)}
    if variant_id not in SUPPORTED_T_TEST_VARIANTS:
        return _t_test_not_applicable(variant_id, f"unsupported t-test variant: {variant_id}", metadata)

    try:
        alpha = _resolve_alpha(params)
        confidence_level = float(params.get("confidence_level", 0.95))
        if not 0 < confidence_level < 1:
            raise ValueError("confidence_level must be in (0, 1)")
        min_reference_size = _positive_int(params.get("min_reference_size", 2), "min_reference_size")
        min_current_size = _positive_int(params.get("min_current_size", 2), "min_current_size")
        variance_ratio_warning_threshold = float(params.get("variance_ratio_warning_threshold", 4.0))
        sample_imbalance_warning_ratio = float(params.get("sample_imbalance_warning_ratio", 10.0))
        if variance_ratio_warning_threshold <= 0 or sample_imbalance_warning_ratio < 1:
            raise ValueError("warning ratio parameters must be positive")
        value_col = _resolve_value_col(value_col, params)
        _validate_t_test_policy_params(variant_id, params)
        alternative = _resolve_t_test_alternative(variant_id, params)
    except (TypeError, ValueError) as exc:
        return _t_test_not_applicable(variant_id, str(exc), metadata)

    if value_col in data.columns and pd.api.types.is_bool_dtype(data[value_col]):
        return _t_test_not_applicable(variant_id, "boolean value column is not valid numeric t-test input", metadata)

    try:
        if variant_id == "PAIRED_T_TEST":
            prepared = _prepare_paired_t_test_data(
                data,
                time_col=time_col,
                value_col=value_col,
                reference_window=reference_window,
                current_window=current_window,
                pair_col=params.get("pair_col"),
            )
        elif variant_id == "ONE_SAMPLE_T_TEST" and reference_window is None and params.get("baseline_mean") is not None:
            prepared = _prepare_current_only_t_test_data(
                data,
                time_col=time_col,
                value_col=value_col,
                current_window=current_window,
            )
        else:
            windowed = prepare_numeric_windows(
                data,
                time_col=time_col,
                value_col=value_col,
                reference_window=reference_window,
                current_window=current_window,
            )
            prepared = {
                "reference_values": windowed.reference_values,
                "current_values": windowed.current_values,
                "metadata": windowed.metadata,
                "warnings": windowed.warnings,
                "paired": False,
            }
    except (KeyError, ValueError) as exc:
        return _t_test_not_applicable(variant_id, str(exc), metadata)

    reference_values = prepared.get("reference_values")
    current_values = prepared["current_values"]
    warnings = list(prepared["warnings"])
    metadata.update(prepared["metadata"])
    metadata.update(
        {
            "value_col": value_col,
            "alpha": alpha,
            "alternative": alternative,
            "confidence_level": confidence_level,
            "variant_equal_var": variant_id == "TWO_SAMPLE_STUDENT_T_TEST",
            "variant_paired": variant_id == "PAIRED_T_TEST",
        }
    )

    if len(current_values) < min_current_size:
        return _t_test_not_applicable(
            variant_id,
            f"effective current sample size {len(current_values)} is below min_current_size {min_current_size}",
            metadata,
            warnings,
        )
    if variant_id != "ONE_SAMPLE_T_TEST" or reference_values is not None:
        if reference_values is None or len(reference_values) < min_reference_size:
            n_ref = 0 if reference_values is None else len(reference_values)
            return _t_test_not_applicable(
                variant_id,
                f"effective reference sample size {n_ref} is below min_reference_size {min_reference_size}",
                metadata,
                warnings,
            )

    try:
        t_statistic, p_value, baseline_mean = _run_t_test_variant(
            variant_id=variant_id,
            reference_values=reference_values,
            current_values=current_values,
            params=params,
            alternative=alternative,
            metadata=metadata,
            warnings=warnings,
            min_reference_size=min_reference_size,
        )
    except ValueError as exc:
        return _t_test_not_applicable(variant_id, str(exc), metadata, warnings)
    except Exception as exc:
        return DriftResult(
            method_id=T_TEST_METHOD_ID,
            method_name=T_TEST_METHOD_NAME,
            method_category=METHOD_CATEGORY,
            variant_id=variant_id,
            drift_detected=None,
            severity="error",
            threshold=alpha,
            interpretation=f"t-test calculation failed: {exc}",
            warnings=warnings + [f"t-test backend failed: {exc}"],
            metadata=metadata,
        )

    if not np.isfinite(t_statistic) or not np.isfinite(p_value):
        return _t_test_not_applicable(variant_id, "t statistic or p-value is not finite", metadata, warnings)

    if reference_values is not None and len(reference_values) >= 2 and len(current_values) >= 2:
        _add_t_test_warnings(reference_values, current_values, variant_id, variance_ratio_warning_threshold, sample_imbalance_warning_ratio, warnings)

    drift_detected = bool(p_value < alpha)
    severity = "drift_detected" if drift_detected else "normal"
    alarm_state = "drift_detected" if drift_detected else "normal"
    reference_mean = None if reference_values is None else float(np.mean(reference_values))
    current_mean = float(np.mean(current_values))
    baseline_for_diff = baseline_mean if baseline_mean is not None else reference_mean
    mean_difference = None if baseline_for_diff is None else float(current_mean - baseline_for_diff)
    reference_variance = None if reference_values is None or len(reference_values) < 2 else float(np.var(reference_values, ddof=1))
    current_variance = None if len(current_values) < 2 else float(np.var(current_values, ddof=1))

    measurements = {
        "TEST_STATISTIC": float(t_statistic),
        "P_VALUE": float(p_value),
        "DRIFT_ALARM_STATE": alarm_state,
        "SAMPLE_SIZE": {
            "reference": None if reference_values is None else int(len(reference_values)),
            "current": int(len(current_values)),
            "paired": metadata.get("paired_count"),
            "dropped_reference": metadata.get("dropped_reference"),
            "dropped_current": metadata.get("dropped_current"),
            "dropped_unpaired": metadata.get("dropped_unpaired"),
        },
        "SAMPLE_SIZE_REFERENCE": None if reference_values is None else int(len(reference_values)),
        "SAMPLE_SIZE_CURRENT": int(len(current_values)),
        "REFERENCE_MEAN": reference_mean,
        "CURRENT_MEAN": current_mean,
        "MEAN_DIFFERENCE": mean_difference,
        "REFERENCE_VARIANCE": reference_variance,
        "CURRENT_VARIANCE": current_variance,
        "BASELINE_MEAN": baseline_mean,
        "CONFIDENCE_INTERVAL": None,
    }

    return DriftResult(
        method_id=T_TEST_METHOD_ID,
        method_name=T_TEST_METHOD_NAME,
        method_category=METHOD_CATEGORY,
        variant_id=variant_id,
        drift_detected=drift_detected,
        severity=severity,
        drift_score=None if mean_difference is None else abs(mean_difference),
        p_value=float(p_value),
        test_statistic=float(t_statistic),
        threshold=alpha,
        measurements=measurements,
        interpretation=_t_test_interpretation(
            variant_id=variant_id,
            alternative=alternative,
            t_statistic=float(t_statistic),
            p_value=float(p_value),
            alpha=alpha,
            current_mean=current_mean,
            reference_or_baseline_mean=baseline_for_diff,
            drift_detected=drift_detected,
            warnings=warnings,
        ),
        warnings=warnings,
        metadata=metadata,
    )


def detect_levene_s_test(
    data: pd.DataFrame,
    *,
    time_col: str = "time",
    value_col: str | None = "value",
    reference_window: tuple[str, str] | None = None,
    current_window: tuple[str, str] | None = None,
    params: dict[str, Any] | None = None,
) -> DriftResult:
    params = dict(params or {})
    variant_id = params.get("variant_id", "BROWN_FORSYTHE_MEDIAN_CENTER")
    metadata: dict[str, Any] = {"params": dict(params)}
    if variant_id not in SUPPORTED_LEVENE_VARIANTS:
        return _levene_not_applicable(variant_id, f"unsupported Levene variant: {variant_id}", metadata)

    try:
        alpha = _resolve_alpha(params)
        center = _resolve_levene_center(variant_id, params)
        proportiontocut = float(params.get("proportiontocut", 0.05))
        if not 0 <= proportiontocut < 0.5:
            raise ValueError("proportiontocut must satisfy 0 <= proportiontocut < 0.5")
        alternative = str(params.get("alternative", "two-sided"))
        if alternative not in {"two-sided", "both"}:
            raise ValueError("Levene's Test first implementation supports only two-sided alternative")
        if params.get("nan_policy", "omit") != "omit":
            raise ValueError("nan_policy must be 'omit' in the first Levene implementation")
        min_reference_size = _positive_int(params.get("min_reference_size", 3), "min_reference_size")
        min_current_size = _positive_int(params.get("min_current_size", 3), "min_current_size")
        variance_ratio_warning_threshold = float(params.get("variance_ratio_warning_threshold", 4.0))
        small_sample_warning_threshold = _positive_int(params.get("small_sample_warning_threshold", 10), "small_sample_warning_threshold")
        if variance_ratio_warning_threshold <= 0:
            raise ValueError("variance_ratio_warning_threshold must be positive")
        value_col = _resolve_value_col(value_col, params)
    except (TypeError, ValueError) as exc:
        return _levene_not_applicable(variant_id, str(exc), metadata)

    if value_col in data.columns and pd.api.types.is_bool_dtype(data[value_col]):
        return _levene_not_applicable(variant_id, "boolean value column is not valid numeric variance input", metadata)

    try:
        prepared = prepare_numeric_windows(
            data,
            time_col=time_col,
            value_col=value_col,
            reference_window=reference_window,
            current_window=current_window,
        )
    except (KeyError, ValueError) as exc:
        return _levene_not_applicable(variant_id, str(exc), metadata)

    reference_values = prepared.reference_values
    current_values = prepared.current_values
    warnings = list(prepared.warnings)
    metadata.update(prepared.metadata)
    metadata.update(
        {
            "value_col": value_col,
            "alpha": alpha,
            "center": center,
            "proportiontocut": proportiontocut if center == "trimmed" else None,
            "alternative": "two-sided",
            "backend": "scipy.stats.levene",
        }
    )

    if len(reference_values) < min_reference_size:
        return _levene_not_applicable(
            variant_id,
            f"effective reference sample size {len(reference_values)} is below min_reference_size {min_reference_size}",
            metadata,
            warnings,
        )
    if len(current_values) < min_current_size:
        return _levene_not_applicable(
            variant_id,
            f"effective current sample size {len(current_values)} is below min_current_size {min_current_size}",
            metadata,
            warnings,
        )
    ref_var = float(np.var(reference_values, ddof=1))
    cur_var = float(np.var(current_values, ddof=1))
    if ref_var == 0 and cur_var == 0:
        return _levene_not_applicable(variant_id, "both windows are constant; variance comparison is not informative", metadata, warnings)

    if min(len(reference_values), len(current_values)) < small_sample_warning_threshold:
        warnings.append("small effective sample size may weaken Levene p-value stability")
    variance_ratio = _variance_ratio(ref_var, cur_var)
    if variance_ratio is not None and variance_ratio > variance_ratio_warning_threshold:
        warnings.append("reference/current variance ratio is large; report as scale-drift effect context")
    if variant_id == "LEVENE_MEAN_CENTER":
        warnings.append("mean-centered Levene can be sensitive to outliers; compare Brown-Forsythe for robust interpretation")
    if variant_id == "TRIMMED_MEAN_LEVENE" and proportiontocut != 0.05:
        warnings.append("non-default trimmed proportion was used")

    try:
        stat = levene(
            reference_values,
            current_values,
            center=center,
            proportiontocut=proportiontocut,
        )
        test_statistic = float(stat.statistic)
        p_value = float(stat.pvalue)
    except Exception as exc:
        return DriftResult(
            method_id=LEVENE_METHOD_ID,
            method_name=LEVENE_METHOD_NAME,
            method_category=METHOD_CATEGORY,
            variant_id=variant_id,
            drift_detected=None,
            severity="error",
            threshold=alpha,
            interpretation=f"Levene calculation failed: {exc}",
            warnings=warnings + [f"levene failed: {exc}"],
            metadata=metadata,
        )
    if not np.isfinite(test_statistic) or not np.isfinite(p_value):
        return _levene_not_applicable(variant_id, "Levene statistic or p-value is not finite", metadata, warnings)

    drift_detected = bool(p_value < alpha)
    severity = "drift_detected" if drift_detected else "normal"
    alarm_state = "drift_detected" if drift_detected else "normal"
    ref_center = _center_value(reference_values, center, proportiontocut)
    cur_center = _center_value(current_values, center, proportiontocut)

    measurements = {
        "TEST_STATISTIC": test_statistic,
        "P_VALUE": p_value,
        "DRIFT_ALARM_STATE": alarm_state,
        "SAMPLE_SIZE": {
            "reference": int(len(reference_values)),
            "current": int(len(current_values)),
            "dropped_reference": int(metadata.get("reference_original_count", len(reference_values)) - len(reference_values)),
            "dropped_current": int(metadata.get("current_original_count", len(current_values)) - len(current_values)),
        },
        "SAMPLE_SIZE_REFERENCE": int(len(reference_values)),
        "SAMPLE_SIZE_CURRENT": int(len(current_values)),
        "REFERENCE_VARIANCE": ref_var,
        "CURRENT_VARIANCE": cur_var,
        "VARIANCE_RATIO": variance_ratio,
        "REFERENCE_CENTER": ref_center,
        "CURRENT_CENTER": cur_center,
        "CENTER_POLICY": center,
        "PROPORTION_TO_CUT": proportiontocut if center == "trimmed" else None,
    }

    return DriftResult(
        method_id=LEVENE_METHOD_ID,
        method_name=LEVENE_METHOD_NAME,
        method_category=METHOD_CATEGORY,
        variant_id=variant_id,
        drift_detected=drift_detected,
        severity=severity,
        drift_score=test_statistic,
        p_value=p_value,
        test_statistic=test_statistic,
        threshold=alpha,
        measurements=measurements,
        interpretation=_levene_interpretation(
            variant_id=variant_id,
            center=center,
            test_statistic=test_statistic,
            p_value=p_value,
            alpha=alpha,
            ref_var=ref_var,
            cur_var=cur_var,
            drift_detected=drift_detected,
            warnings=warnings,
        ),
        warnings=warnings,
        metadata=metadata,
    )


def detect_anderson_darling_test(
    data: pd.DataFrame,
    *,
    time_col: str = "time",
    value_col: str | None = "value",
    reference_window: tuple[str, str] | None = None,
    current_window: tuple[str, str] | None = None,
    params: dict[str, Any] | None = None,
) -> DriftResult:
    params = dict(params or {})
    variant_id = params.get("variant_id", "TWO_SAMPLE_ANDERSON_DARLING")
    metadata: dict[str, Any] = {"params": dict(params)}

    if variant_id in DEFERRED_ANDERSON_DARLING_VARIANTS:
        return _anderson_darling_not_applicable(
            variant_id,
            f"Anderson-Darling variant is not implemented yet: {variant_id}",
            metadata,
        )
    if variant_id not in SUPPORTED_ANDERSON_DARLING_VARIANTS:
        return _anderson_darling_not_applicable(variant_id, f"unsupported Anderson-Darling variant: {variant_id}", metadata)

    try:
        alpha = _resolve_anderson_alpha(params)
        if params.get("p_value_method", "asymptotic") != "asymptotic":
            raise ValueError("p_value_method must be 'asymptotic' in the first Anderson-Darling implementation")
        if params.get("distribution_family", "empirical") != "empirical":
            raise ValueError("distribution_family must be 'empirical' for supported Anderson-Darling variants")
        if params.get("nan_policy", "drop") != "drop":
            raise ValueError("nan_policy must be 'drop'")
        min_reference_size = _positive_int(params.get("min_reference_size", 20), "min_reference_size")
        min_current_size = _positive_int(params.get("min_current_size", 20), "min_current_size")
        value_col = _resolve_value_col(value_col, params)
        tail_quantiles = _resolve_tail_quantiles(params)
        tail_direction = params.get("tail_direction", "both")
        if tail_direction not in {"lower", "upper", "both"}:
            raise ValueError("tail_direction must be one of lower, upper, both")
    except (TypeError, ValueError) as exc:
        return _anderson_darling_not_applicable(variant_id, str(exc), metadata)

    if value_col in data.columns and pd.api.types.is_bool_dtype(data[value_col]):
        return _anderson_darling_not_applicable(variant_id, "boolean value column is not valid numeric AD input", metadata)

    try:
        prepared = prepare_numeric_windows(
            data,
            time_col=time_col,
            value_col=value_col,
            reference_window=reference_window,
            current_window=current_window,
        )
    except (KeyError, ValueError) as exc:
        return _anderson_darling_not_applicable(variant_id, str(exc), metadata)

    reference_values = prepared.reference_values
    current_values = prepared.current_values
    warnings = list(prepared.warnings)
    metadata.update(prepared.metadata)
    metadata.update(
        {
            "value_col": value_col,
            "alpha": alpha,
            "p_value_method": "asymptotic",
            "distribution_family": "empirical",
            "tail_quantiles": {"lower": tail_quantiles[0], "upper": tail_quantiles[1]},
            "tail_direction": tail_direction,
            "multiple_testing_correction": params.get("multiple_testing_correction", "none"),
        }
    )
    if variant_id in {"ONE_SAMPLE_ANDERSON_DARLING", "K_SAMPLE_ANDERSON_DARLING"}:
        metadata["execution_policy"] = "anderson_ksamp_reference_current"
        warnings.append(f"{variant_id} is executed with scipy.stats.anderson_ksamp over reference/current windows")

    if len(reference_values) < min_reference_size:
        return _anderson_darling_not_applicable(
            variant_id,
            f"effective reference sample size {len(reference_values)} is below min_reference_size {min_reference_size}",
            metadata,
            warnings,
        )
    if len(current_values) < min_current_size:
        return _anderson_darling_not_applicable(
            variant_id,
            f"effective current sample size {len(current_values)} is below min_current_size {min_current_size}",
            metadata,
            warnings,
        )
    if _has_ties(reference_values, current_values):
        warnings.append("ties detected; continuous Anderson-Darling interpretation may be weaker")
    if params.get("multiple_testing_correction", "none") != "none":
        warnings.append("multiple_testing_correction is recorded but not applied by detect_anderson_darling_test")

    try:
        with py_warnings.catch_warnings(record=True) as caught_warnings:
            py_warnings.simplefilter("always")
            ad_result = anderson_ksamp([reference_values, current_values], midrank=True)
        statistic = float(ad_result.statistic)
        p_value = float(ad_result.pvalue)
        warnings.extend(str(item.message) for item in caught_warnings)
    except Exception as exc:
        return DriftResult(
            method_id=ANDERSON_DARLING_METHOD_ID,
            method_name=ANDERSON_DARLING_METHOD_NAME,
            method_category=METHOD_CATEGORY,
            variant_id=variant_id,
            drift_detected=None,
            severity="error",
            threshold=alpha,
            interpretation=f"Anderson-Darling calculation failed: {exc}",
            warnings=warnings + [f"anderson_ksamp failed: {exc}"],
            metadata=metadata,
        )
    if not np.isfinite(statistic) or not np.isfinite(p_value):
        return _anderson_darling_not_applicable(variant_id, "AD statistic or p-value is not finite", metadata, warnings)
    if p_value in {0.001, 0.25}:
        warnings.append("scipy anderson_ksamp p-value may be capped or floored")

    drift_detected = bool(p_value < alpha)
    severity = "drift_detected" if drift_detected else "normal"
    alarm_state = "drift_detected" if drift_detected else "normal"
    measurements: dict[str, Any] = {
        "TEST_STATISTIC": statistic,
        "P_VALUE": p_value,
        "DRIFT_ALARM_STATE": alarm_state,
        "SAMPLE_SIZE": {"reference": int(len(reference_values)), "current": int(len(current_values))},
        "SAMPLE_SIZE_REFERENCE": int(len(reference_values)),
        "SAMPLE_SIZE_CURRENT": int(len(current_values)),
        "WINDOW_SIZE": {"reference": int(len(reference_values)), "current": int(len(current_values))},
    }
    if variant_id == "TAIL_SENSITIVE_AD":
        tail_measurements, tail_warnings = _tail_sensitive_measurements(reference_values, current_values, tail_quantiles)
        measurements.update(tail_measurements)
        warnings.extend(tail_warnings)

    return DriftResult(
        method_id=ANDERSON_DARLING_METHOD_ID,
        method_name=ANDERSON_DARLING_METHOD_NAME,
        method_category=METHOD_CATEGORY,
        variant_id=variant_id,
        drift_detected=drift_detected,
        severity=severity,
        drift_score=statistic,
        p_value=p_value,
        test_statistic=statistic,
        threshold=alpha,
        measurements=measurements,
        interpretation=_anderson_darling_interpretation(
            variant_id=variant_id,
            statistic=statistic,
            p_value=p_value,
            alpha=alpha,
            reference_count=len(reference_values),
            current_count=len(current_values),
            drift_detected=drift_detected,
            warnings=warnings,
        ),
        warnings=warnings,
        metadata=metadata,
    )


def detect_cramer_von_mises_test(
    data: pd.DataFrame,
    *,
    time_col: str = "time",
    value_col: str | None = "value",
    reference_window: tuple[str, str] | None = None,
    current_window: tuple[str, str] | None = None,
    params: dict[str, Any] | None = None,
) -> DriftResult:
    params = dict(params or {})
    variant_id = params.get("variant_id", "TWO_SAMPLE_CVM")
    metadata: dict[str, Any] = {"params": dict(params)}

    if variant_id in DEFERRED_CRAMER_VON_MISES_VARIANTS:
        return _cramer_von_mises_not_applicable(
            variant_id,
            f"Cramer-von Mises variant is not implemented yet: {variant_id}",
            metadata,
        )
    if variant_id not in SUPPORTED_CRAMER_VON_MISES_VARIANTS:
        return _cramer_von_mises_not_applicable(variant_id, f"unsupported Cramer-von Mises variant: {variant_id}", metadata)

    try:
        alpha = _resolve_cvm_alpha(params)
        alternative = str(params.get("alternative", "two-sided"))
        if alternative not in {"two-sided", "both"}:
            raise ValueError("alternative must be 'two-sided' or 'both' in the first Cramer-von Mises implementation")
        p_value_method = _resolve_cvm_p_value_method(params)
        nan_policy = str(params.get("nan_policy", "drop"))
        if nan_policy not in {"drop", "omit"}:
            raise ValueError("nan_policy must be 'drop' or 'omit'")
        tie_policy = str(params.get("tie_policy", "warn_only"))
        if tie_policy != "warn_only":
            raise ValueError("tie_policy must be 'warn_only'")
        min_reference_size = _positive_int(params.get("min_reference_size", 20), "min_reference_size")
        min_current_size = _positive_int(params.get("min_current_size", 20), "min_current_size")
        imbalance_warning_ratio = float(params.get("sample_imbalance_warning_ratio", 10.0))
        if imbalance_warning_ratio < 1:
            raise ValueError("sample_imbalance_warning_ratio must be >= 1")
        value_col = _resolve_value_col(value_col, params)
    except (TypeError, ValueError) as exc:
        return _cramer_von_mises_not_applicable(variant_id, str(exc), metadata)

    if value_col in data.columns and pd.api.types.is_bool_dtype(data[value_col]):
        return _cramer_von_mises_not_applicable(variant_id, "boolean value column is not valid numeric CvM input", metadata)

    try:
        prepared = prepare_numeric_windows(
            data,
            time_col=time_col,
            value_col=value_col,
            reference_window=reference_window,
            current_window=current_window,
        )
    except (KeyError, ValueError, TypeError) as exc:
        return _cramer_von_mises_not_applicable(variant_id, str(exc), metadata)

    reference_values = prepared.reference_values
    current_values = prepared.current_values
    warnings = list(prepared.warnings)
    metadata.update(prepared.metadata)
    metadata.update(
        {
            "value_col": value_col,
            "alpha": alpha,
            "alternative": alternative,
            "p_value_method": p_value_method,
            "nan_policy": nan_policy,
            "tie_policy": tie_policy,
            "multiple_testing_correction": params.get("multiple_testing_correction", "none"),
            "backend": "scipy.stats.cramervonmises_2samp",
        }
    )
    if variant_id in {"ONE_SAMPLE_CVM", "K_SAMPLE_CVM"}:
        metadata["execution_policy"] = "two_sample_cvm_reference_current"
        warnings.append(f"{variant_id} is executed with scipy.stats.cramervonmises_2samp over reference/current windows")

    if len(reference_values) < min_reference_size:
        return _cramer_von_mises_not_applicable(
            variant_id,
            f"effective reference sample size {len(reference_values)} is below min_reference_size {min_reference_size}",
            metadata,
            warnings,
        )
    if len(current_values) < min_current_size:
        return _cramer_von_mises_not_applicable(
            variant_id,
            f"effective current sample size {len(current_values)} is below min_current_size {min_current_size}",
            metadata,
            warnings,
        )
    if _has_ties(reference_values, current_values):
        warnings.append("ties detected; continuous Cramer-von Mises interpretation may be weaker")
    if min(len(reference_values), len(current_values)) > 0:
        sample_ratio = max(len(reference_values), len(current_values)) / min(len(reference_values), len(current_values))
        metadata["sample_size_ratio"] = float(sample_ratio)
        if sample_ratio > imbalance_warning_ratio:
            warnings.append("reference/current sample sizes are highly imbalanced")
    if params.get("multiple_testing_correction", "none") != "none":
        warnings.append("multiple_testing_correction is recorded but not applied by detect_cramer_von_mises_test")

    try:
        with py_warnings.catch_warnings(record=True) as caught_warnings:
            py_warnings.simplefilter("always")
            cvm_result = cramervonmises_2samp(reference_values, current_values, method=p_value_method)
        statistic = float(cvm_result.statistic)
        p_value = float(cvm_result.pvalue)
        warnings.extend(str(item.message) for item in caught_warnings)
    except Exception as exc:
        return DriftResult(
            method_id=CRAMER_VON_MISES_METHOD_ID,
            method_name=CRAMER_VON_MISES_METHOD_NAME,
            method_category=METHOD_CATEGORY,
            variant_id=variant_id,
            drift_detected=None,
            severity="error",
            threshold=alpha,
            interpretation=f"Cramer-von Mises calculation failed: {exc}",
            warnings=warnings + [f"cramervonmises_2samp failed: {exc}"],
            metadata=metadata,
        )

    if not np.isfinite(statistic) or not np.isfinite(p_value) or not 0 <= p_value <= 1:
        return _cramer_von_mises_not_applicable(variant_id, "CvM statistic or p-value is invalid", metadata, warnings)

    drift_detected = bool(p_value < alpha)
    severity = "drift_detected" if drift_detected else "normal"
    alarm_state = "drift_detected" if drift_detected else "normal"
    summary_measurements = _cvm_summary_measurements(reference_values, current_values)
    measurements: dict[str, Any] = {
        "TEST_STATISTIC": statistic,
        "P_VALUE": p_value,
        "DRIFT_ALARM_STATE": alarm_state,
        "SAMPLE_SIZE": {
            "reference": int(len(reference_values)),
            "current": int(len(current_values)),
            "dropped_reference": int(metadata.get("reference_original_count", len(reference_values)) - len(reference_values)),
            "dropped_current": int(metadata.get("current_original_count", len(current_values)) - len(current_values)),
        },
        "SAMPLE_SIZE_REFERENCE": int(len(reference_values)),
        "SAMPLE_SIZE_CURRENT": int(len(current_values)),
        "WINDOW_SIZE": {"reference": int(len(reference_values)), "current": int(len(current_values))},
        **summary_measurements,
    }

    return DriftResult(
        method_id=CRAMER_VON_MISES_METHOD_ID,
        method_name=CRAMER_VON_MISES_METHOD_NAME,
        method_category=METHOD_CATEGORY,
        variant_id=variant_id,
        drift_detected=drift_detected,
        severity=severity,
        drift_score=statistic,
        p_value=p_value,
        test_statistic=statistic,
        threshold=alpha,
        measurements=measurements,
        interpretation=_cramer_von_mises_interpretation(
            statistic=statistic,
            p_value=p_value,
            alpha=alpha,
            reference_count=len(reference_values),
            current_count=len(current_values),
            median_delta=summary_measurements["MEDIAN_DELTA"],
            drift_detected=drift_detected,
            warnings=warnings,
        ),
        warnings=warnings,
        metadata=metadata,
    )


def detect_kuiper_s_test(
    data: pd.DataFrame,
    *,
    time_col: str = "time",
    value_col: str | None = "value",
    reference_window: tuple[str, str] | None = None,
    current_window: tuple[str, str] | None = None,
    params: dict[str, Any] | None = None,
) -> DriftResult:
    params = dict(params or {})
    variant_id = params.get("variant_id", "KUIPER_TWO_SAMPLE")
    metadata: dict[str, Any] = {"params": dict(params)}

    if variant_id in DEFERRED_KUIPER_VARIANTS:
        return _kuiper_not_applicable(variant_id, f"Kuiper variant is not implemented yet: {variant_id}", metadata)
    if variant_id not in SUPPORTED_KUIPER_VARIANTS:
        return _kuiper_not_applicable(variant_id, f"unsupported Kuiper variant: {variant_id}", metadata)

    try:
        decision_policy = str(params.get("decision_policy", "p_value"))
        if decision_policy not in {"p_value", "threshold"}:
            raise ValueError("decision_policy must be 'p_value' or 'threshold'")
        alpha = _resolve_kuiper_alpha(params, decision_policy)
        threshold = _resolve_kuiper_threshold(params, decision_policy)
        alternative = str(params.get("alternative", "two-sided"))
        if alternative not in {"two-sided", "both"}:
            raise ValueError("alternative must be 'two-sided' or 'both' in the first Kuiper implementation")
        p_value_method = str(params.get("p_value_method", "permutation"))
        if decision_policy == "p_value" and p_value_method != "permutation":
            raise ValueError("decision_policy='p_value' requires p_value_method='permutation'")
        if decision_policy == "threshold" and p_value_method not in {"none", "permutation"}:
            raise ValueError("threshold mode p_value_method must be 'none' or 'permutation'")
        nan_policy = str(params.get("nan_policy", "drop"))
        if nan_policy not in {"drop", "omit"}:
            raise ValueError("nan_policy must be 'drop' or 'omit'")
        tie_policy = str(params.get("tie_policy", "warn_only"))
        if tie_policy != "warn_only":
            raise ValueError("tie_policy must be 'warn_only'")
        if params.get("circular_data_policy", "not_supported") != "not_supported":
            raise ValueError("circular_data_policy must be 'not_supported' in the first Kuiper implementation")
        permutation_count = _positive_int(params.get("permutation_count", 999), "permutation_count")
        permutation_max_total_size = _positive_int(
            params.get("permutation_max_total_size", 5000),
            "permutation_max_total_size",
        )
        random_seed = _optional_int(params.get("random_seed"), "random_seed")
        min_reference_size = _positive_int(params.get("min_reference_size", 20), "min_reference_size")
        min_current_size = _positive_int(params.get("min_current_size", 20), "min_current_size")
        imbalance_warning_ratio = float(params.get("sample_imbalance_warning_ratio", 10.0))
        if imbalance_warning_ratio < 1:
            raise ValueError("sample_imbalance_warning_ratio must be >= 1")
        value_col = _resolve_value_col(value_col, params)
    except (TypeError, ValueError) as exc:
        return _kuiper_not_applicable(variant_id, str(exc), metadata)

    if value_col in data.columns and pd.api.types.is_bool_dtype(data[value_col]):
        return _kuiper_not_applicable(variant_id, "boolean value column is not valid numeric Kuiper input", metadata)

    try:
        prepared = prepare_numeric_windows(
            data,
            time_col=time_col,
            value_col=value_col,
            reference_window=reference_window,
            current_window=current_window,
        )
    except (KeyError, ValueError, TypeError) as exc:
        return _kuiper_not_applicable(variant_id, str(exc), metadata)

    reference_values = prepared.reference_values
    current_values = prepared.current_values
    warnings = list(prepared.warnings)
    metadata.update(prepared.metadata)
    metadata.update(
        {
            "value_col": value_col,
            "alpha": alpha,
            "threshold": threshold,
            "alternative": alternative,
            "decision_policy": decision_policy,
            "p_value_method": p_value_method,
            "nan_policy": nan_policy,
            "tie_policy": tie_policy,
            "permutation_count": permutation_count if p_value_method == "permutation" else None,
            "random_seed": random_seed,
            "permutation_max_total_size": permutation_max_total_size,
            "multiple_testing_correction": params.get("multiple_testing_correction", "none"),
            "backend": "local_kuiper_two_sample",
        }
    )
    if variant_id in {"KUIPER_CIRCULAR_DATA", "KUIPER_ONE_SAMPLE"}:
        metadata["execution_policy"] = "two_sample_kuiper_reference_current"
        warnings.append(f"{variant_id} is executed with the two-sample Kuiper engine over reference/current windows")

    if len(reference_values) < min_reference_size:
        return _kuiper_not_applicable(
            variant_id,
            f"effective reference sample size {len(reference_values)} is below min_reference_size {min_reference_size}",
            metadata,
            warnings,
        )
    if len(current_values) < min_current_size:
        return _kuiper_not_applicable(
            variant_id,
            f"effective current sample size {len(current_values)} is below min_current_size {min_current_size}",
            metadata,
            warnings,
        )
    if _has_ties(reference_values, current_values):
        warnings.append("ties detected; continuous Kuiper interpretation may be weaker")
    sample_ratio = max(len(reference_values), len(current_values)) / min(len(reference_values), len(current_values))
    metadata["sample_size_ratio"] = float(sample_ratio)
    if sample_ratio > imbalance_warning_ratio:
        warnings.append("reference/current sample sizes are highly imbalanced")
    if permutation_count < 199 and p_value_method == "permutation":
        warnings.append("low permutation_count gives coarse Monte Carlo p-value resolution")
    if params.get("multiple_testing_correction", "none") != "none":
        warnings.append("multiple_testing_correction is recorded but not applied by detect_kuiper_s_test")
    if decision_policy == "threshold":
        warnings.append("threshold mode uses an externally calibrated Kuiper statistic threshold")

    try:
        statistic, d_plus, d_minus = _kuiper_two_sample_statistic(reference_values, current_values)
        p_value = None
        if p_value_method == "permutation":
            total_size = len(reference_values) + len(current_values)
            if total_size > permutation_max_total_size:
                return _kuiper_not_applicable(
                    variant_id,
                    f"total effective sample size {total_size} exceeds permutation_max_total_size {permutation_max_total_size}",
                    metadata,
                    warnings,
                )
            p_value = _kuiper_permutation_p_value(
                reference_values,
                current_values,
                observed_statistic=statistic,
                permutation_count=permutation_count,
                random_seed=random_seed,
            )
    except Exception as exc:
        return DriftResult(
            method_id=KUIPER_METHOD_ID,
            method_name=KUIPER_METHOD_NAME,
            method_category=METHOD_CATEGORY,
            variant_id=variant_id,
            drift_detected=None,
            severity="error",
            threshold=alpha if decision_policy == "p_value" else threshold,
            interpretation=f"Kuiper calculation failed: {exc}",
            warnings=warnings + [f"local Kuiper calculation failed: {exc}"],
            metadata=metadata,
        )

    if not np.isfinite(statistic) or not np.isfinite(d_plus) or not np.isfinite(d_minus):
        return _kuiper_not_applicable(variant_id, "Kuiper statistic is not finite", metadata, warnings)
    if p_value is not None and (not np.isfinite(p_value) or not 0 <= p_value <= 1):
        return _kuiper_not_applicable(variant_id, "Kuiper p-value is invalid", metadata, warnings)

    if decision_policy == "p_value":
        drift_detected = bool(p_value is not None and p_value < alpha)
        threshold_out = alpha
    else:
        drift_detected = bool(statistic > threshold)
        threshold_out = threshold
    severity = "drift_detected" if drift_detected else "normal"
    alarm_state = "drift_detected" if drift_detected else "normal"
    summary_measurements = _cvm_summary_measurements(reference_values, current_values)
    measurements: dict[str, Any] = {
        "TEST_STATISTIC": statistic,
        "P_VALUE": p_value,
        "DRIFT_ALARM_STATE": alarm_state,
        "SAMPLE_SIZE": {
            "reference": int(len(reference_values)),
            "current": int(len(current_values)),
            "dropped_reference": int(metadata.get("reference_original_count", len(reference_values)) - len(reference_values)),
            "dropped_current": int(metadata.get("current_original_count", len(current_values)) - len(current_values)),
        },
        "SAMPLE_SIZE_REFERENCE": int(len(reference_values)),
        "SAMPLE_SIZE_CURRENT": int(len(current_values)),
        "WINDOW_SIZE": {"reference": int(len(reference_values)), "current": int(len(current_values))},
        "KUIPER_D_PLUS": d_plus,
        "KUIPER_D_MINUS": d_minus,
        "PERMUTATION_COUNT": permutation_count if p_value_method == "permutation" else None,
        **summary_measurements,
    }

    return DriftResult(
        method_id=KUIPER_METHOD_ID,
        method_name=KUIPER_METHOD_NAME,
        method_category=METHOD_CATEGORY,
        variant_id=variant_id,
        drift_detected=drift_detected,
        severity=severity,
        drift_score=statistic,
        p_value=p_value,
        test_statistic=statistic,
        threshold=threshold_out,
        measurements=measurements,
        interpretation=_kuiper_interpretation(
            statistic=statistic,
            d_plus=d_plus,
            d_minus=d_minus,
            p_value=p_value,
            alpha=alpha,
            threshold=threshold,
            decision_policy=decision_policy,
            reference_count=len(reference_values),
            current_count=len(current_values),
            median_delta=summary_measurements["MEDIAN_DELTA"],
            drift_detected=drift_detected,
            warnings=warnings,
        ),
        warnings=warnings,
        metadata=metadata,
    )


def detect_baumgartner_weiss_schindler_test(
    data: pd.DataFrame,
    *,
    time_col: str = "time",
    value_col: str | None = "value",
    reference_window: tuple[str, str] | None = None,
    current_window: tuple[str, str] | None = None,
    params: dict[str, Any] | None = None,
) -> DriftResult:
    params = dict(params or {})
    variant_id = params.get("variant_id", "BWS_TWO_SAMPLE")
    metadata: dict[str, Any] = {"params": dict(params)}

    if variant_id in DEFERRED_BWS_VARIANTS:
        return _bws_not_applicable(variant_id, f"BWS variant is not implemented yet: {variant_id}", metadata)
    if variant_id not in SUPPORTED_BWS_VARIANTS:
        return _bws_not_applicable(variant_id, f"unsupported BWS variant: {variant_id}", metadata)

    try:
        decision_policy = str(params.get("decision_policy", "p_value"))
        if decision_policy not in {"p_value", "threshold"}:
            raise ValueError("decision_policy must be 'p_value' or 'threshold'")
        alpha = _resolve_kuiper_alpha(params, decision_policy)
        threshold = _resolve_kuiper_threshold(params, decision_policy)
        alternative = str(params.get("alternative", "two-sided"))
        if alternative not in {"two-sided", "both"}:
            raise ValueError("alternative must be 'two-sided' or 'both' in the first BWS implementation")
        p_value_method = str(params.get("p_value_method", "permutation"))
        if p_value_method in {"exact", "asymptotic"}:
            raise ValueError(f"p_value_method={p_value_method!r} is deferred for BWS")
        if decision_policy == "p_value" and p_value_method != "permutation":
            raise ValueError("decision_policy='p_value' requires p_value_method='permutation'")
        if decision_policy == "threshold" and p_value_method not in {"none", "permutation"}:
            raise ValueError("threshold mode p_value_method must be 'none' or 'permutation'")
        nan_policy = str(params.get("nan_policy", "drop"))
        if nan_policy not in {"drop", "omit"}:
            raise ValueError("nan_policy must be 'drop' or 'omit'")
        rank_tie_policy = str(params.get("rank_tie_policy", params.get("tie_policy", "average_rank_warn")))
        if rank_tie_policy == "warn_only":
            rank_tie_policy = "average_rank_warn"
        if rank_tie_policy != "average_rank_warn":
            raise ValueError("rank_tie_policy must be 'average_rank_warn'")
        permutation_count = _positive_int(params.get("permutation_count", 999), "permutation_count")
        permutation_max_total_size = _positive_int(
            params.get("permutation_max_total_size", 5000),
            "permutation_max_total_size",
        )
        random_seed = _optional_int(params.get("random_seed"), "random_seed")
        min_reference_size = _positive_int(params.get("min_reference_size", 20), "min_reference_size")
        min_current_size = _positive_int(params.get("min_current_size", 20), "min_current_size")
        low_power_sample_size = _positive_int(params.get("low_power_sample_size", 50), "low_power_sample_size")
        imbalance_warning_ratio = float(params.get("sample_imbalance_warning_ratio", 10.0))
        if imbalance_warning_ratio < 1:
            raise ValueError("sample_imbalance_warning_ratio must be >= 1")
        value_col = _resolve_value_col(value_col, params)
    except (TypeError, ValueError) as exc:
        return _bws_not_applicable(variant_id, str(exc), metadata)

    if value_col in data.columns and pd.api.types.is_bool_dtype(data[value_col]):
        return _bws_not_applicable(variant_id, "boolean value column is not valid numeric BWS input", metadata)

    try:
        prepared = prepare_numeric_windows(
            data,
            time_col=time_col,
            value_col=value_col,
            reference_window=reference_window,
            current_window=current_window,
        )
    except (KeyError, ValueError, TypeError) as exc:
        return _bws_not_applicable(variant_id, str(exc), metadata)

    reference_values = prepared.reference_values
    current_values = prepared.current_values
    warnings = list(prepared.warnings)
    metadata.update(prepared.metadata)
    metadata.update(
        {
            "value_col": value_col,
            "alpha": alpha,
            "threshold": threshold,
            "alternative": alternative,
            "decision_policy": decision_policy,
            "p_value_method": p_value_method,
            "nan_policy": nan_policy,
            "rank_tie_policy": rank_tie_policy,
            "permutation_count": permutation_count if p_value_method == "permutation" else None,
            "random_seed": random_seed,
            "permutation_max_total_size": permutation_max_total_size,
            "multiple_testing_correction": params.get("multiple_testing_correction", "none"),
            "backend": "local_bws_two_sample",
        }
    )
    if variant_id == "BWS_EXACT_OR_ASYMPTOTIC":
        metadata["execution_policy"] = "permutation_bws_reference_current"
        warnings.append("BWS_EXACT_OR_ASYMPTOTIC is executed with the local permutation BWS engine")

    if len(reference_values) < min_reference_size:
        return _bws_not_applicable(
            variant_id,
            f"effective reference sample size {len(reference_values)} is below min_reference_size {min_reference_size}",
            metadata,
            warnings,
        )
    if len(current_values) < min_current_size:
        return _bws_not_applicable(
            variant_id,
            f"effective current sample size {len(current_values)} is below min_current_size {min_current_size}",
            metadata,
            warnings,
        )
    if _has_ties(reference_values, current_values):
        warnings.append("ties detected; average ranks are used and continuous BWS interpretation may be weaker")
    sample_ratio = max(len(reference_values), len(current_values)) / min(len(reference_values), len(current_values))
    metadata["sample_size_ratio"] = float(sample_ratio)
    if sample_ratio > imbalance_warning_ratio:
        warnings.append("reference/current sample sizes are highly imbalanced")
    if min(len(reference_values), len(current_values)) < low_power_sample_size:
        warnings.append("small effective sample size may weaken BWS permutation-test power")
    if permutation_count < 199 and p_value_method == "permutation":
        warnings.append("low permutation_count gives coarse Monte Carlo p-value resolution")
    if params.get("multiple_testing_correction", "none") != "none":
        warnings.append("multiple_testing_correction is recorded but not applied by detect_baumgartner_weiss_schindler_test")
    if params.get("exact_method") is not None or params.get("asymptotic_method") is not None:
        warnings.append("exact_method/asymptotic_method are recorded but ignored by the local permutation BWS backend")
    if decision_policy == "threshold":
        warnings.append("threshold mode uses an externally calibrated BWS statistic threshold")

    try:
        statistic, reference_component, current_component = _bws_two_sample_statistic(reference_values, current_values)
        p_value = None
        if p_value_method == "permutation":
            total_size = len(reference_values) + len(current_values)
            if total_size > permutation_max_total_size:
                return _bws_not_applicable(
                    variant_id,
                    f"total effective sample size {total_size} exceeds permutation_max_total_size {permutation_max_total_size}",
                    metadata,
                    warnings,
                )
            p_value = _bws_permutation_p_value(
                reference_values,
                current_values,
                observed_statistic=statistic,
                permutation_count=permutation_count,
                random_seed=random_seed,
            )
    except Exception as exc:
        return DriftResult(
            method_id=BAUMGARTNER_WEISS_SCHINDLER_METHOD_ID,
            method_name=BAUMGARTNER_WEISS_SCHINDLER_METHOD_NAME,
            method_category=METHOD_CATEGORY,
            variant_id=variant_id,
            drift_detected=None,
            severity="error",
            threshold=alpha if decision_policy == "p_value" else threshold,
            interpretation=f"BWS calculation failed: {exc}",
            warnings=warnings + [f"local BWS calculation failed: {exc}"],
            metadata=metadata,
        )

    if not np.isfinite(statistic) or not np.isfinite(reference_component) or not np.isfinite(current_component):
        return _bws_not_applicable(variant_id, "BWS statistic is not finite", metadata, warnings)
    if p_value is not None and (not np.isfinite(p_value) or not 0 <= p_value <= 1):
        return _bws_not_applicable(variant_id, "BWS p-value is invalid", metadata, warnings)

    if decision_policy == "p_value":
        drift_detected = bool(p_value is not None and p_value < alpha)
        threshold_out = alpha
    else:
        drift_detected = bool(statistic > threshold)
        threshold_out = threshold
    severity = "drift_detected" if drift_detected else "normal"
    alarm_state = "drift_detected" if drift_detected else "normal"
    summary_measurements = _cvm_summary_measurements(reference_values, current_values)
    measurements: dict[str, Any] = {
        "TEST_STATISTIC": statistic,
        "P_VALUE": p_value,
        "DRIFT_ALARM_STATE": alarm_state,
        "SAMPLE_SIZE": {
            "reference": int(len(reference_values)),
            "current": int(len(current_values)),
            "dropped_reference": int(metadata.get("reference_original_count", len(reference_values)) - len(reference_values)),
            "dropped_current": int(metadata.get("current_original_count", len(current_values)) - len(current_values)),
        },
        "SAMPLE_SIZE_REFERENCE": int(len(reference_values)),
        "SAMPLE_SIZE_CURRENT": int(len(current_values)),
        "WINDOW_SIZE": {"reference": int(len(reference_values)), "current": int(len(current_values))},
        "BWS_REFERENCE_COMPONENT": reference_component,
        "BWS_CURRENT_COMPONENT": current_component,
        "PERMUTATION_COUNT": permutation_count if p_value_method == "permutation" else None,
        **summary_measurements,
    }

    return DriftResult(
        method_id=BAUMGARTNER_WEISS_SCHINDLER_METHOD_ID,
        method_name=BAUMGARTNER_WEISS_SCHINDLER_METHOD_NAME,
        method_category=METHOD_CATEGORY,
        variant_id=variant_id,
        drift_detected=drift_detected,
        severity=severity,
        drift_score=statistic,
        p_value=p_value,
        test_statistic=statistic,
        threshold=threshold_out,
        measurements=measurements,
        interpretation=_bws_interpretation(
            variant_id=variant_id,
            statistic=statistic,
            p_value=p_value,
            alpha=alpha,
            threshold=threshold,
            decision_policy=decision_policy,
            reference_count=len(reference_values),
            current_count=len(current_values),
            median_delta=summary_measurements["MEDIAN_DELTA"],
            drift_detected=drift_detected,
            warnings=warnings,
        ),
        warnings=warnings,
        metadata=metadata,
    )


def detect_f_test_variance_test(
    data: pd.DataFrame,
    *,
    time_col: str = "time",
    value_col: str | None = "value",
    reference_window: tuple[str, str] | None = None,
    current_window: tuple[str, str] | None = None,
    params: dict[str, Any] | None = None,
) -> DriftResult:
    params = dict(params or {})
    variant_id = params.get("variant_id", "F_TEST_EQUAL_VARIANCE")
    metadata: dict[str, Any] = {"params": dict(params)}

    if variant_id in DEFERRED_F_TEST_VARIANTS:
        return _f_test_not_applicable(variant_id, f"F-test variant is not implemented yet: {variant_id}", metadata)
    if variant_id not in SUPPORTED_F_TEST_VARIANTS:
        return _f_test_not_applicable(variant_id, f"unsupported F-test variant: {variant_id}", metadata)

    try:
        alpha = _resolve_anderson_alpha(params)
        alternative = _resolve_f_test_alternative(params)
        variance_ratio_definition = str(params.get("variance_ratio_definition", "current_over_reference"))
        if variance_ratio_definition != "current_over_reference":
            raise ValueError("variance_ratio_definition must be 'current_over_reference'")
        p_value_method = str(params.get("p_value_method", "scipy"))
        if p_value_method not in {"scipy", "f_distribution"}:
            raise ValueError("p_value_method must be 'scipy' or 'f_distribution'")
        nan_policy = str(params.get("nan_policy", "drop"))
        if nan_policy not in {"drop", "omit"}:
            raise ValueError("nan_policy must be 'drop' or 'omit'")
        if params.get("normality_warning_policy", "warn_only") != "warn_only":
            raise ValueError("normality_warning_policy must be 'warn_only'")
        if params.get("zero_variance_policy", "not_applicable") != "not_applicable":
            raise ValueError("zero_variance_policy must be 'not_applicable'")
        min_reference_size = _positive_int(params.get("min_reference_size", 3), "min_reference_size")
        min_current_size = _positive_int(params.get("min_current_size", 3), "min_current_size")
        if min_reference_size < 3 or min_current_size < 3:
            raise ValueError("min_reference_size and min_current_size must be at least 3")
        low_power_sample_size = _positive_int(params.get("low_power_sample_size", 20), "low_power_sample_size")
        imbalance_warning_ratio = float(params.get("sample_imbalance_warning_ratio", 10.0))
        if imbalance_warning_ratio < 1:
            raise ValueError("sample_imbalance_warning_ratio must be >= 1")
        value_col = _resolve_value_col(value_col, params)
    except (TypeError, ValueError) as exc:
        return _f_test_not_applicable(variant_id, str(exc), metadata)

    if value_col in data.columns and pd.api.types.is_bool_dtype(data[value_col]):
        return _f_test_not_applicable(variant_id, "boolean value column is not valid numeric F-test input", metadata)

    try:
        prepared = prepare_numeric_windows(
            data,
            time_col=time_col,
            value_col=value_col,
            reference_window=reference_window,
            current_window=current_window,
        )
    except (KeyError, ValueError, TypeError) as exc:
        return _f_test_not_applicable(variant_id, str(exc), metadata)

    reference_values = prepared.reference_values
    current_values = prepared.current_values
    warnings = list(prepared.warnings)
    metadata.update(prepared.metadata)
    metadata.update(
        {
            "value_col": value_col,
            "alpha": alpha,
            "alternative": alternative,
            "variance_ratio_definition": variance_ratio_definition,
            "p_value_method": p_value_method,
            "nan_policy": nan_policy,
            "multiple_testing_correction": params.get("multiple_testing_correction", "none"),
            "backend": "scipy.stats.f",
        }
    )
    if variant_id == "MODEL_COMPARISON_F_TEST":
        metadata["execution_policy"] = "variance_ratio_reference_current"
        warnings.append("MODEL_COMPARISON_F_TEST is executed with the two-sample variance-ratio F engine")

    if len(reference_values) < min_reference_size:
        return _f_test_not_applicable(
            variant_id,
            f"effective reference sample size {len(reference_values)} is below min_reference_size {min_reference_size}",
            metadata,
            warnings,
        )
    if len(current_values) < min_current_size:
        return _f_test_not_applicable(
            variant_id,
            f"effective current sample size {len(current_values)} is below min_current_size {min_current_size}",
            metadata,
            warnings,
        )
    if min(len(reference_values), len(current_values)) < low_power_sample_size:
        warnings.append("small effective sample size may weaken F-test variance power")
    sample_ratio = max(len(reference_values), len(current_values)) / min(len(reference_values), len(current_values))
    metadata["sample_size_ratio"] = float(sample_ratio)
    if sample_ratio > imbalance_warning_ratio:
        warnings.append("reference/current sample sizes are highly imbalanced")
    if _has_ties(reference_values, current_values):
        warnings.append("repeated or tied values detected; variance-ratio interpretation may reflect discrete or rounded data")
    warnings.append("F-test variance p-value is sensitive to non-normality and outliers")
    if params.get("multiple_testing_correction", "none") != "none":
        warnings.append("multiple_testing_correction is recorded but not applied by detect_f_test_variance_test")

    try:
        stat = _f_test_equal_variance_statistic(reference_values, current_values, alternative=alternative)
        if variant_id == "ANOVA_F_TEST_GROUP_MEAN":
            anova_result = f_oneway(reference_values, current_values)
            test_statistic = float(anova_result.statistic)
            p_value = float(anova_result.pvalue)
            metadata["backend"] = "scipy.stats.f_oneway"
            metadata["execution_policy"] = "one_way_anova_reference_current"
            warnings.append("ANOVA_F_TEST_GROUP_MEAN is executed as one-way ANOVA over reference/current groups")
        else:
            p_value = _f_distribution_p_value(
                stat["directional_ratio"],
                df_current=int(stat["df_current"]),
                df_reference=int(stat["df_reference"]),
                alternative=alternative,
            )
            test_statistic = float(stat["test_statistic"])
    except Exception as exc:
        return DriftResult(
            method_id=F_TEST_METHOD_ID,
            method_name=F_TEST_METHOD_NAME,
            method_category=METHOD_CATEGORY,
            variant_id=variant_id,
            drift_detected=None,
            severity="error",
            threshold=alpha,
            interpretation=f"F-test calculation failed: {exc}",
            warnings=warnings + [f"F-test calculation failed: {exc}"],
            metadata=metadata,
        )

    if not np.isfinite(test_statistic) or not np.isfinite(p_value) or not 0 <= p_value <= 1:
        return _f_test_not_applicable(variant_id, "F statistic or p-value is invalid", metadata, warnings)

    drift_detected = bool(p_value < alpha)
    severity = "drift_detected" if drift_detected else "normal"
    alarm_state = "drift_detected" if drift_detected else "normal"
    measurements: dict[str, Any] = {
        "TEST_STATISTIC": test_statistic,
        "P_VALUE": p_value,
        "DRIFT_ALARM_STATE": alarm_state,
        "SAMPLE_SIZE": {
            "reference": int(len(reference_values)),
            "current": int(len(current_values)),
            "dropped_reference": int(metadata.get("reference_original_count", len(reference_values)) - len(reference_values)),
            "dropped_current": int(metadata.get("current_original_count", len(current_values)) - len(current_values)),
        },
        "SAMPLE_SIZE_REFERENCE": int(len(reference_values)),
        "SAMPLE_SIZE_CURRENT": int(len(current_values)),
        "WINDOW_SIZE": {"reference": int(len(reference_values)), "current": int(len(current_values))},
        "VARIANCE_REFERENCE": float(stat["variance_reference"]),
        "VARIANCE_CURRENT": float(stat["variance_current"]),
        "VARIANCE_RATIO": float(stat["variance_ratio"]),
        "VARIANCE_RATIO_ABS": float(stat["variance_ratio_abs"]),
        "DEGREES_OF_FREEDOM": {
            "reference": int(stat["df_reference"]),
            "current": int(stat["df_current"]),
            "numerator": int(stat["df_numerator"]),
            "denominator": int(stat["df_denominator"]),
        },
        "REFERENCE_MEAN": float(np.mean(reference_values)),
        "CURRENT_MEAN": float(np.mean(current_values)),
        "REFERENCE_STD": float(np.std(reference_values, ddof=1)),
        "CURRENT_STD": float(np.std(current_values, ddof=1)),
    }

    return DriftResult(
        method_id=F_TEST_METHOD_ID,
        method_name=F_TEST_METHOD_NAME,
        method_category=METHOD_CATEGORY,
        variant_id=variant_id,
        drift_detected=drift_detected,
        severity=severity,
        drift_score=test_statistic,
        p_value=p_value,
        test_statistic=test_statistic,
        threshold=alpha,
        measurements=measurements,
        interpretation=_f_test_interpretation(
            alternative=alternative,
            test_statistic=test_statistic,
            p_value=p_value,
            alpha=alpha,
            variance_reference=float(stat["variance_reference"]),
            variance_current=float(stat["variance_current"]),
            variance_ratio=float(stat["variance_ratio"]),
            drift_detected=drift_detected,
            warnings=warnings,
        ),
        warnings=warnings,
        metadata=metadata,
    )


def detect_energy_distance(
    data: pd.DataFrame,
    *,
    time_col: str = "time",
    value_col: str | None = "value",
    reference_window: tuple[str, str] | None = None,
    current_window: tuple[str, str] | None = None,
    params: dict[str, Any] | None = None,
) -> DriftResult:
    params = dict(params or {})
    variant_id = params.get("variant_id", "UNIVARIATE_ENERGY_DISTANCE")
    metadata: dict[str, Any] = {"params": dict(params)}

    if variant_id in DEFERRED_ENERGY_DISTANCE_VARIANTS:
        return _energy_distance_not_applicable(
            variant_id,
            f"Energy Distance variant is not implemented yet: {variant_id}",
            metadata,
        )
    if variant_id not in SUPPORTED_ENERGY_DISTANCE_VARIANTS:
        return _energy_distance_not_applicable(variant_id, f"unsupported Energy Distance variant: {variant_id}", metadata)
    if variant_id == "MULTIVARIATE_ENERGY_DISTANCE" and any(params.get(key) is not None for key in ("feature_cols", "embedding_cols")):
        return _energy_distance_not_applicable(
            variant_id,
            "explicit multivariate Energy Distance columns are not implemented yet",
            metadata,
        )

    try:
        if params.get("distance_metric", "energy") not in {"energy", "energy_distance"}:
            raise ValueError("distance_metric must be 'energy' or 'energy_distance'")
        p_value_method = str(params.get("p_value_method", "permutation" if variant_id == "ENERGY_DISTANCE_PERMUTATION_TEST" else "none"))
        if variant_id == "UNIVARIATE_ENERGY_DISTANCE" and p_value_method not in {"none"}:
            raise ValueError("UNIVARIATE_ENERGY_DISTANCE supports p_value_method='none' only")
        if variant_id == "ENERGY_DISTANCE_PERMUTATION_TEST" and p_value_method != "permutation":
            raise ValueError("ENERGY_DISTANCE_PERMUTATION_TEST requires p_value_method='permutation'")
        threshold, threshold_warning = _resolve_energy_distance_threshold(params, variant_id)
        alpha = _resolve_anderson_alpha(params) if variant_id == "ENERGY_DISTANCE_PERMUTATION_TEST" else None
        permutation_count = _positive_int(params.get("permutation_count", 999), "permutation_count")
        random_seed = _optional_int(params.get("random_seed"), "random_seed")
        nan_policy = str(params.get("nan_policy", "drop"))
        if nan_policy not in {"drop", "omit"}:
            raise ValueError("nan_policy must be 'drop' or 'omit'")
        min_reference_size = _positive_int(params.get("min_reference_size", 20), "min_reference_size")
        min_current_size = _positive_int(params.get("min_current_size", 20), "min_current_size")
        imbalance_warning_ratio = float(params.get("sample_imbalance_warning_ratio", 10.0))
        if imbalance_warning_ratio < 1:
            raise ValueError("sample_imbalance_warning_ratio must be >= 1")
        if params.get("permutation_alternative", "greater") != "greater":
            raise ValueError("permutation_alternative must be 'greater'")
        value_col = _resolve_value_col(value_col, params)
    except (TypeError, ValueError) as exc:
        return _energy_distance_not_applicable(variant_id, str(exc), metadata)

    if value_col in data.columns and pd.api.types.is_bool_dtype(data[value_col]):
        return _energy_distance_not_applicable(variant_id, "boolean value column is not valid Energy Distance input", metadata)

    try:
        prepared = prepare_numeric_windows(
            data,
            time_col=time_col,
            value_col=value_col,
            reference_window=reference_window,
            current_window=current_window,
        )
    except (KeyError, ValueError, TypeError) as exc:
        return _energy_distance_not_applicable(variant_id, str(exc), metadata)

    reference_values = prepared.reference_values
    current_values = prepared.current_values
    warnings = list(prepared.warnings)
    if threshold_warning:
        warnings.append(threshold_warning)
    metadata.update(prepared.metadata)
    metadata.update(
        {
            "value_col": value_col,
            "threshold": threshold,
            "alpha": alpha,
            "distance_metric": "energy_distance",
            "p_value_method": p_value_method,
            "nan_policy": nan_policy,
            "permutation_count": permutation_count if p_value_method == "permutation" else None,
            "random_seed": random_seed,
            "multiple_testing_correction": params.get("multiple_testing_correction", "none"),
            "backend": "scipy.stats.energy_distance",
        }
    )
    if variant_id == "MULTIVARIATE_ENERGY_DISTANCE":
        metadata["projection_policy"] = "single_projected_numeric_stream"
        metadata["projection_count"] = 1

    if len(reference_values) < min_reference_size:
        return _energy_distance_not_applicable(
            variant_id,
            f"effective reference sample size {len(reference_values)} is below min_reference_size {min_reference_size}",
            metadata,
            warnings,
        )
    if len(current_values) < min_current_size:
        return _energy_distance_not_applicable(
            variant_id,
            f"effective current sample size {len(current_values)} is below min_current_size {min_current_size}",
            metadata,
            warnings,
        )
    sample_ratio = max(len(reference_values), len(current_values)) / min(len(reference_values), len(current_values))
    metadata["sample_size_ratio"] = float(sample_ratio)
    if sample_ratio > imbalance_warning_ratio:
        warnings.append("reference/current sample sizes are highly imbalanced")
    if _has_ties(reference_values, current_values):
        warnings.append("repeated or tied values detected; Energy Distance may reflect discrete or rounded data")
    if variant_id == "UNIVARIATE_ENERGY_DISTANCE" and threshold is None:
        warnings.append("no distance threshold supplied; returning Energy distance without binary alarm")
    if p_value_method == "permutation" and permutation_count < 199:
        warnings.append("low permutation_count gives coarse Monte Carlo p-value resolution")
    if params.get("multiple_testing_correction", "none") != "none":
        warnings.append("multiple_testing_correction is recorded but not applied by detect_energy_distance")

    try:
        distance = float(energy_distance(reference_values, current_values))
        permutation_extreme_count = None
        p_value = None
        if p_value_method == "permutation":
            p_value, permutation_extreme_count = _energy_distance_permutation_p_value(
                reference_values,
                current_values,
                observed_distance=distance,
                permutation_count=permutation_count,
                random_seed=random_seed,
            )
    except Exception as exc:
        return DriftResult(
            method_id=ENERGY_DISTANCE_METHOD_ID,
            method_name=ENERGY_DISTANCE_METHOD_NAME,
            method_category=METHOD_CATEGORY,
            variant_id=variant_id,
            drift_detected=None,
            severity="error",
            threshold=alpha if variant_id == "ENERGY_DISTANCE_PERMUTATION_TEST" else threshold,
            interpretation=f"Energy Distance calculation failed: {exc}",
            warnings=warnings + [f"energy_distance failed: {exc}"],
            metadata=metadata,
        )

    if not np.isfinite(distance) or distance < 0:
        return _energy_distance_not_applicable(variant_id, "Energy distance is invalid", metadata, warnings)
    if p_value is not None and (not np.isfinite(p_value) or not 0 <= p_value <= 1):
        return _energy_distance_not_applicable(variant_id, "Energy Distance permutation p-value is invalid", metadata, warnings)

    if variant_id == "ENERGY_DISTANCE_PERMUTATION_TEST":
        drift_detected = bool(p_value is not None and p_value < alpha)
        severity = "drift_detected" if drift_detected else "normal"
        alarm_state = "drift_detected" if drift_detected else "normal"
        threshold_out = alpha
    elif threshold is None:
        drift_detected = None
        severity = "watch"
        alarm_state = "undetermined"
        threshold_out = None
    elif distance > threshold:
        drift_detected = True
        severity = "drift_detected"
        alarm_state = "drift_detected"
        threshold_out = threshold
    else:
        drift_detected = False
        severity = "normal"
        alarm_state = "normal"
        threshold_out = threshold

    summary_measurements = _cvm_summary_measurements(reference_values, current_values)
    measurements: dict[str, Any] = {
        "TEST_STATISTIC": distance,
        "P_VALUE": p_value,
        "DRIFT_ALARM_STATE": alarm_state,
        "SAMPLE_SIZE": {
            "reference": int(len(reference_values)),
            "current": int(len(current_values)),
            "dropped_reference": int(metadata.get("reference_original_count", len(reference_values)) - len(reference_values)),
            "dropped_current": int(metadata.get("current_original_count", len(current_values)) - len(current_values)),
        },
        "SAMPLE_SIZE_REFERENCE": int(len(reference_values)),
        "SAMPLE_SIZE_CURRENT": int(len(current_values)),
        "WINDOW_SIZE": {"reference": int(len(reference_values)), "current": int(len(current_values))},
        "ENERGY_DISTANCE": distance,
        **summary_measurements,
    }
    if p_value_method == "permutation":
        measurements.update(
            {
                "PERMUTATION_COUNT": permutation_count,
                "PERMUTATION_EXTREME_COUNT": int(permutation_extreme_count),
                "PERMUTATION_ALTERNATIVE": "greater",
            }
        )

    return DriftResult(
        method_id=ENERGY_DISTANCE_METHOD_ID,
        method_name=ENERGY_DISTANCE_METHOD_NAME,
        method_category=METHOD_CATEGORY,
        variant_id=variant_id,
        drift_detected=drift_detected,
        severity=severity,
        drift_score=distance,
        p_value=p_value,
        test_statistic=distance,
        threshold=threshold_out,
        measurements=measurements,
        interpretation=_energy_distance_interpretation(
            variant_id=variant_id,
            distance=distance,
            p_value=p_value,
            alpha=alpha,
            threshold=threshold,
            reference_count=len(reference_values),
            current_count=len(current_values),
            alarm_state=alarm_state,
            warnings=warnings,
        ),
        warnings=warnings,
        metadata=metadata,
    )


def detect_epps_singleton_test(
    data: pd.DataFrame,
    *,
    time_col: str = "time",
    value_col: str | None = "value",
    reference_window: tuple[str, str] | None = None,
    current_window: tuple[str, str] | None = None,
    params: dict[str, Any] | None = None,
) -> DriftResult:
    params = dict(params or {})
    variant_id = params.get("variant_id", "TWO_SAMPLE_EPPS_SINGLETON")
    metadata: dict[str, Any] = {"params": dict(params)}

    if variant_id in DEFERRED_EPPS_SINGLETON_VARIANTS:
        return _epps_singleton_not_applicable(
            variant_id,
            f"Epps-Singleton variant is not implemented yet: {variant_id}",
            metadata,
        )
    if variant_id not in SUPPORTED_EPPS_SINGLETON_VARIANTS:
        return _epps_singleton_not_applicable(variant_id, f"unsupported Epps-Singleton variant: {variant_id}", metadata)

    try:
        alpha = _resolve_anderson_alpha(params)
        t_points = _resolve_epps_singleton_t_points(params)
        p_value_method = str(params.get("p_value_method", "asymptotic"))
        if p_value_method not in {"asymptotic", "scipy", "scipy_asymptotic"}:
            raise ValueError("p_value_method must be asymptotic, scipy, or scipy_asymptotic")
        correction_policy = str(params.get("correction_policy", "scipy_default"))
        if correction_policy not in {"scipy_default", "auto"}:
            raise ValueError("correction_policy must be 'scipy_default' or 'auto'")
        nan_policy = str(params.get("nan_policy", "drop"))
        if nan_policy not in {"drop", "omit"}:
            raise ValueError("nan_policy must be 'drop' or 'omit'")
        tie_unique_ratio_threshold = float(params.get("tie_unique_ratio_threshold", 0.95))
        if not 0 < tie_unique_ratio_threshold <= 1:
            raise ValueError("tie_unique_ratio_threshold must be in (0, 1]")
        min_reference_size = _positive_int(params.get("min_reference_size", 20), "min_reference_size")
        min_current_size = _positive_int(params.get("min_current_size", 20), "min_current_size")
        imbalance_warning_ratio = float(params.get("sample_imbalance_warning_ratio", 10.0))
        if imbalance_warning_ratio < 1:
            raise ValueError("sample_imbalance_warning_ratio must be >= 1")
        value_col = _resolve_value_col(value_col, params)
    except (TypeError, ValueError) as exc:
        return _epps_singleton_not_applicable(variant_id, str(exc), metadata)

    if value_col in data.columns and pd.api.types.is_bool_dtype(data[value_col]):
        return _epps_singleton_not_applicable(variant_id, "boolean value column is not valid Epps-Singleton input", metadata)

    try:
        prepared = prepare_numeric_windows(
            data,
            time_col=time_col,
            value_col=value_col,
            reference_window=reference_window,
            current_window=current_window,
        )
    except (KeyError, ValueError, TypeError) as exc:
        return _epps_singleton_not_applicable(variant_id, str(exc), metadata)

    reference_values = prepared.reference_values
    current_values = prepared.current_values
    warnings = list(prepared.warnings)
    metadata.update(prepared.metadata)
    metadata.update(
        {
            "value_col": value_col,
            "alpha": alpha,
            "t_points": list(t_points),
            "p_value_method": p_value_method,
            "correction_policy": correction_policy,
            "nan_policy": nan_policy,
            "multiple_testing_correction": params.get("multiple_testing_correction", "none"),
            "backend": "scipy.stats.epps_singleton_2samp",
        }
    )
    if variant_id == "ASYMPTOTIC_EPPS_SINGLETON":
        metadata["execution_policy"] = "asymptotic_epps_singleton_reference_current"
        warnings.append("ASYMPTOTIC_EPPS_SINGLETON is executed with scipy.stats.epps_singleton_2samp")

    if len(reference_values) < min_reference_size:
        return _epps_singleton_not_applicable(
            variant_id,
            f"effective reference sample size {len(reference_values)} is below min_reference_size {min_reference_size}",
            metadata,
            warnings,
        )
    if len(current_values) < min_current_size:
        return _epps_singleton_not_applicable(
            variant_id,
            f"effective current sample size {len(current_values)} is below min_current_size {min_current_size}",
            metadata,
            warnings,
        )

    tie_metadata = _tie_metadata(reference_values, current_values)
    metadata.update(tie_metadata)
    if tie_metadata["reference_has_ties"] or tie_metadata["current_has_ties"]:
        warnings.append("ties detected; Epps-Singleton interpretation should consider discrete or rounded values")
    if tie_metadata["combined_unique_ratio"] < tie_unique_ratio_threshold:
        warnings.append("low unique-value ratio suggests discrete-like input")
    sample_ratio = max(len(reference_values), len(current_values)) / min(len(reference_values), len(current_values))
    metadata["sample_size_ratio"] = float(sample_ratio)
    if sample_ratio > imbalance_warning_ratio:
        warnings.append("reference/current sample sizes are highly imbalanced")
    if len(t_points) > 4:
        warnings.append("more than four t_points may increase singular-covariance risk")
    if params.get("multiple_testing_correction", "none") != "none":
        warnings.append("multiple_testing_correction is recorded but not applied by detect_epps_singleton_test")
    discrete_measurements: dict[str, Any] = {}
    if variant_id == "DISCRETE_EPPS_SINGLETON":
        discrete_measurements = _epps_singleton_discrete_metadata(reference_values, current_values)
        warnings.append("DISCRETE_EPPS_SINGLETON uses numeric discrete-like values, not categories or count tables")

    try:
        with py_warnings.catch_warnings(record=True) as caught_warnings:
            py_warnings.simplefilter("always")
            result = epps_singleton_2samp(reference_values, current_values, t=t_points)
        statistic = float(result.statistic)
        p_value = float(result.pvalue)
        warnings.extend(str(item.message) for item in caught_warnings)
    except Exception as exc:
        return DriftResult(
            method_id=EPPS_SINGLETON_METHOD_ID,
            method_name=EPPS_SINGLETON_METHOD_NAME,
            method_category=METHOD_CATEGORY,
            variant_id=variant_id,
            drift_detected=None,
            severity="error",
            threshold=alpha,
            interpretation=f"Epps-Singleton calculation failed: {exc}",
            warnings=warnings + [f"epps_singleton_2samp failed: {exc}"],
            metadata=metadata,
        )

    if not np.isfinite(statistic) or not np.isfinite(p_value) or not 0 <= p_value <= 1:
        return _epps_singleton_not_applicable(variant_id, "Epps-Singleton statistic or p-value is invalid", metadata, warnings)

    drift_detected = bool(p_value < alpha)
    severity = "drift_detected" if drift_detected else "normal"
    alarm_state = "drift_detected" if drift_detected else "normal"
    summary_measurements = _cvm_summary_measurements(reference_values, current_values)
    measurements: dict[str, Any] = {
        "TEST_STATISTIC": statistic,
        "EPPS_SINGLETON_STATISTIC": statistic,
        "P_VALUE": p_value,
        "DRIFT_ALARM_STATE": alarm_state,
        "SAMPLE_SIZE": {
            "reference": int(len(reference_values)),
            "current": int(len(current_values)),
            "dropped_reference": int(metadata.get("reference_original_count", len(reference_values)) - len(reference_values)),
            "dropped_current": int(metadata.get("current_original_count", len(current_values)) - len(current_values)),
        },
        "SAMPLE_SIZE_REFERENCE": int(len(reference_values)),
        "SAMPLE_SIZE_CURRENT": int(len(current_values)),
        "WINDOW_SIZE": {"reference": int(len(reference_values)), "current": int(len(current_values))},
        "T_POINTS": list(t_points),
        "REFERENCE_UNIQUE_RATIO": tie_metadata["reference_unique_ratio"],
        "CURRENT_UNIQUE_RATIO": tie_metadata["current_unique_ratio"],
        "COMBINED_UNIQUE_RATIO": tie_metadata["combined_unique_ratio"],
        "MEAN_DELTA": float(np.mean(current_values) - np.mean(reference_values)),
        **summary_measurements,
        **discrete_measurements,
    }

    return DriftResult(
        method_id=EPPS_SINGLETON_METHOD_ID,
        method_name=EPPS_SINGLETON_METHOD_NAME,
        method_category=METHOD_CATEGORY,
        variant_id=variant_id,
        drift_detected=drift_detected,
        severity=severity,
        drift_score=statistic,
        p_value=p_value,
        test_statistic=statistic,
        threshold=alpha,
        measurements=measurements,
        interpretation=_epps_singleton_interpretation(
            variant_id=variant_id,
            statistic=statistic,
            p_value=p_value,
            alpha=alpha,
            t_points=t_points,
            reference_count=len(reference_values),
            current_count=len(current_values),
            drift_detected=drift_detected,
            warnings=warnings,
        ),
        warnings=warnings,
        metadata=metadata,
    )


def detect_mmd(
    data: pd.DataFrame,
    *,
    time_col: str = "time",
    value_col: str | None = "value",
    reference_window: tuple[str, str] | None = None,
    current_window: tuple[str, str] | None = None,
    params: dict[str, Any] | None = None,
) -> DriftResult:
    params = dict(params or {})
    variant_id = params.get("variant_id", "KERNEL_MMD_BIASED")
    metadata: dict[str, Any] = {"params": dict(params)}

    if variant_id in DEFERRED_MMD_VARIANTS:
        return _mmd_not_applicable(variant_id, f"MMD variant is not implemented yet: {variant_id}", metadata)
    if variant_id not in SUPPORTED_MMD_VARIANTS:
        return _mmd_not_applicable(variant_id, f"unsupported MMD variant: {variant_id}", metadata)
    feature_cols = [str(item) for item in params.get("feature_cols", params.get("embedding_cols", [])) or []]

    try:
        if params.get("kernel", "rbf") not in {"rbf", "gaussian"}:
            raise ValueError("kernel must be 'rbf' or 'gaussian'")
        p_value_method = str(params.get("p_value_method", "none"))
        if p_value_method not in {"none", "permutation"}:
            raise ValueError("p_value_method must be 'none' or 'permutation'")
        threshold, threshold_warning = _resolve_mmd_threshold(params, p_value_method)
        alpha = _resolve_anderson_alpha(params) if p_value_method == "permutation" else None
        permutation_count = _positive_int(params.get("permutation_count", 999), "permutation_count")
        random_seed = _optional_int(params.get("random_seed"), "random_seed")
        if params.get("permutation_alternative", "greater") != "greater":
            raise ValueError("permutation_alternative must be 'greater'")
        nan_policy = str(params.get("nan_policy", "drop"))
        if nan_policy not in {"drop", "omit"}:
            raise ValueError("nan_policy must be 'drop' or 'omit'")
        min_reference_size = _positive_int(params.get("min_reference_size", 20), "min_reference_size")
        min_current_size = _positive_int(params.get("min_current_size", 20), "min_current_size")
        if variant_id == "KERNEL_MMD_UNBIASED" and (min_reference_size < 2 or min_current_size < 2):
            raise ValueError("unbiased MMD requires min_reference_size and min_current_size >= 2")
        imbalance_warning_ratio = float(params.get("sample_imbalance_warning_ratio", 10.0))
        if imbalance_warning_ratio < 1:
            raise ValueError("sample_imbalance_warning_ratio must be >= 1")
        value_col = _resolve_value_col(value_col, params) if not feature_cols else str(feature_cols[0])
    except (TypeError, ValueError) as exc:
        return _mmd_not_applicable(variant_id, str(exc), metadata)

    if not feature_cols and value_col in data.columns and pd.api.types.is_bool_dtype(data[value_col]):
        return _mmd_not_applicable(variant_id, "boolean value column is not valid MMD input", metadata)

    try:
        if feature_cols:
            prepared = _prepare_mmd_feature_windows(
                data,
                time_col=time_col,
                feature_cols=feature_cols,
                reference_window=reference_window,
                current_window=current_window,
            )
        else:
            prepared = prepare_numeric_windows(
                data,
                time_col=time_col,
                value_col=value_col,
                reference_window=reference_window,
                current_window=current_window,
            )
    except (KeyError, ValueError, TypeError) as exc:
        return _mmd_not_applicable(variant_id, str(exc), metadata)

    reference_values = prepared.reference_values
    current_values = prepared.current_values
    warnings = list(prepared.warnings)
    if threshold_warning:
        warnings.append(threshold_warning)
    metadata.update(prepared.metadata)

    if len(reference_values) < min_reference_size:
        return _mmd_not_applicable(
            variant_id,
            f"effective reference sample size {len(reference_values)} is below min_reference_size {min_reference_size}",
            metadata,
            warnings,
        )
    if len(current_values) < min_current_size:
        return _mmd_not_applicable(
            variant_id,
            f"effective current sample size {len(current_values)} is below min_current_size {min_current_size}",
            metadata,
            warnings,
        )

    try:
        bandwidth = _resolve_mmd_bandwidth(reference_values, current_values, params)
        mmd_score = _mmd_rbf_statistic(reference_values, current_values, gamma=bandwidth["gamma"], variant_id=variant_id)
        p_value = None
        permutation_extreme_count = None
        if p_value_method == "permutation":
            p_value, permutation_extreme_count = _mmd_permutation_p_value(
                reference_values,
                current_values,
                gamma=bandwidth["gamma"],
                variant_id=variant_id,
                observed_mmd=mmd_score,
                permutation_count=permutation_count,
                random_seed=random_seed,
            )
    except ValueError as exc:
        return _mmd_not_applicable(variant_id, str(exc), metadata, warnings)
    except Exception as exc:
        return DriftResult(
            method_id=MMD_METHOD_ID,
            method_name=MMD_METHOD_NAME,
            method_category=METHOD_CATEGORY,
            variant_id=variant_id,
            drift_detected=None,
            severity="error",
            threshold=alpha if p_value_method == "permutation" else threshold,
            interpretation=f"MMD calculation failed: {exc}",
            warnings=warnings + [f"MMD calculation failed: {exc}"],
            metadata=metadata,
        )

    if not np.isfinite(mmd_score):
        return _mmd_not_applicable(variant_id, "MMD statistic is not finite", metadata, warnings)
    if p_value is not None and (not np.isfinite(p_value) or not 0 <= p_value <= 1):
        return _mmd_not_applicable(variant_id, "MMD permutation p-value is invalid", metadata, warnings)

    sample_ratio = max(len(reference_values), len(current_values)) / min(len(reference_values), len(current_values))
    metadata.update(
        {
            "value_col": value_col,
            "feature_cols": feature_cols or None,
            "threshold": threshold,
            "alpha": alpha,
            "kernel": "rbf",
            "kernel_bandwidth": bandwidth["sigma"],
            "kernel_gamma": bandwidth["gamma"],
            "bandwidth_policy": bandwidth["policy"],
            "p_value_method": p_value_method,
            "nan_policy": nan_policy,
            "permutation_count": permutation_count if p_value_method == "permutation" else None,
            "random_seed": random_seed,
            "sample_size_ratio": float(sample_ratio),
            "multiple_testing_correction": params.get("multiple_testing_correction", "none"),
            "backend": "numpy_rbf_mmd",
        }
    )
    if variant_id in {"LINEAR_TIME_MMD", "STREAMING_MMD"}:
        metadata["projection_policy"] = "feature_matrix_rbf_mmd" if feature_cols else "single_projected_numeric_stream"
        metadata["projection_count"] = len(feature_cols) if feature_cols else 1
        metadata["runtime_policy"] = "finite_replay_rbf_mmd"
    if sample_ratio > imbalance_warning_ratio:
        warnings.append("reference/current sample sizes are highly imbalanced")
    if _has_ties(reference_values, current_values):
        warnings.append("repeated or tied values detected; MMD may reflect discrete or rounded data")
    if p_value_method == "none" and threshold is None:
        warnings.append("no MMD score threshold supplied; returning MMD score without binary alarm")
    if p_value_method == "permutation" and permutation_count < 199:
        warnings.append("low permutation_count gives coarse Monte Carlo p-value resolution")
    if params.get("multiple_testing_correction", "none") != "none":
        warnings.append("multiple_testing_correction is recorded but not applied by detect_mmd")

    if p_value_method == "permutation":
        drift_detected = bool(p_value is not None and p_value < alpha)
        severity = "drift_detected" if drift_detected else "normal"
        alarm_state = "drift_detected" if drift_detected else "normal"
        threshold_out = alpha
    elif threshold is None:
        drift_detected = None
        severity = "watch"
        alarm_state = "undetermined"
        threshold_out = None
    elif mmd_score > threshold:
        drift_detected = True
        severity = "drift_detected"
        alarm_state = "drift_detected"
        threshold_out = threshold
    else:
        drift_detected = False
        severity = "normal"
        alarm_state = "normal"
        threshold_out = threshold

    summary_measurements = _cvm_summary_measurements(reference_values, current_values)
    measurements: dict[str, Any] = {
        "TEST_STATISTIC": mmd_score,
        "P_VALUE": p_value,
        "DRIFT_ALARM_STATE": alarm_state,
        "SAMPLE_SIZE": {
            "reference": int(len(reference_values)),
            "current": int(len(current_values)),
            "dropped_reference": int(metadata.get("reference_original_count", len(reference_values)) - len(reference_values)),
            "dropped_current": int(metadata.get("current_original_count", len(current_values)) - len(current_values)),
        },
        "SAMPLE_SIZE_REFERENCE": int(len(reference_values)),
        "SAMPLE_SIZE_CURRENT": int(len(current_values)),
        "WINDOW_SIZE": {"reference": int(len(reference_values)), "current": int(len(current_values))},
        "MMD_STATISTIC": mmd_score,
        "MMD_SQUARED": mmd_score,
        "KERNEL": "rbf",
        "KERNEL_BANDWIDTH": bandwidth["sigma"],
        "KERNEL_GAMMA": bandwidth["gamma"],
        "BANDWIDTH_POLICY": bandwidth["policy"],
        "MEAN_DELTA": float(np.mean(current_values) - np.mean(reference_values)),
        **summary_measurements,
    }
    if p_value_method == "permutation":
        measurements.update(
            {
                "PERMUTATION_COUNT": permutation_count,
                "PERMUTATION_EXTREME_COUNT": int(permutation_extreme_count),
                "PERMUTATION_ALTERNATIVE": "greater",
            }
        )

    return DriftResult(
        method_id=MMD_METHOD_ID,
        method_name=MMD_METHOD_NAME,
        method_category=METHOD_CATEGORY,
        variant_id=variant_id,
        drift_detected=drift_detected,
        severity=severity,
        drift_score=mmd_score,
        p_value=p_value,
        test_statistic=mmd_score,
        threshold=threshold_out,
        measurements=measurements,
        interpretation=_mmd_interpretation(
            variant_id=variant_id,
            mmd_score=mmd_score,
            p_value=p_value,
            alpha=alpha,
            threshold=threshold,
            bandwidth=bandwidth,
            reference_count=len(reference_values),
            current_count=len(current_values),
            alarm_state=alarm_state,
            warnings=warnings,
        ),
        warnings=warnings,
        metadata=metadata,
    )


def detect_lsdd(
    data: pd.DataFrame,
    *,
    time_col: str = "time",
    value_col: str | None = "value",
    reference_window: tuple[str, str] | None = None,
    current_window: tuple[str, str] | None = None,
    params: dict[str, Any] | None = None,
) -> DriftResult:
    params = dict(params or {})
    variant_id = params.get("variant_id", "LEAST_SQUARES_DENSITY_DIFFERENCE")
    metadata: dict[str, Any] = {"params": dict(params)}

    if variant_id in DEFERRED_LSDD_VARIANTS:
        return _lsdd_not_applicable(variant_id, f"LSDD variant is not implemented yet: {variant_id}", metadata)
    if variant_id not in SUPPORTED_LSDD_VARIANTS:
        return _lsdd_not_applicable(variant_id, f"unsupported LSDD variant: {variant_id}", metadata)
    if any(params.get(key) is not None for key in ("feature_cols", "embedding_cols", "preprocessing_fn")):
        return _lsdd_not_applicable(variant_id, "preprocessing, multivariate, or embedding LSDD inputs are not implemented yet", metadata)

    try:
        if params.get("kernel", "rbf") not in {"rbf", "gaussian"}:
            raise ValueError("kernel must be 'rbf' or 'gaussian'")
        p_value_method = str(params.get("p_value_method", "permutation" if variant_id == "PERMUTATION_LSDD" else "none"))
        if variant_id == "PERMUTATION_LSDD" and p_value_method != "permutation":
            raise ValueError("PERMUTATION_LSDD requires p_value_method='permutation'")
        if p_value_method not in {"none", "permutation"}:
            raise ValueError("p_value_method must be 'none' or 'permutation'")
        threshold, threshold_warning = _resolve_mmd_threshold(params, p_value_method)
        alpha = _resolve_anderson_alpha(params) if p_value_method == "permutation" else None
        regularization_lambda = float(params.get("regularization_lambda", 0.001))
        if not np.isfinite(regularization_lambda) or regularization_lambda < 0:
            raise ValueError("regularization_lambda must be a finite number >= 0")
        center_selection = str(params.get("center_selection", "quantile"))
        if center_selection not in {"quantile", "random"}:
            raise ValueError("center_selection must be 'quantile' or 'random'")
        permutation_count = _positive_int(params.get("permutation_count", 999), "permutation_count")
        random_seed = _optional_int(params.get("random_seed"), "random_seed")
        if params.get("permutation_alternative", "greater") != "greater":
            raise ValueError("permutation_alternative must be 'greater'")
        nan_policy = str(params.get("nan_policy", "drop"))
        if nan_policy not in {"drop", "omit"}:
            raise ValueError("nan_policy must be 'drop' or 'omit'")
        min_reference_size = _positive_int(params.get("min_reference_size", 20), "min_reference_size")
        min_current_size = _positive_int(params.get("min_current_size", 20), "min_current_size")
        imbalance_warning_ratio = float(params.get("sample_imbalance_warning_ratio", 10.0))
        if imbalance_warning_ratio < 1:
            raise ValueError("sample_imbalance_warning_ratio must be >= 1")
        value_col = _resolve_value_col(value_col, params)
    except (TypeError, ValueError) as exc:
        return _lsdd_not_applicable(variant_id, str(exc), metadata)

    if value_col in data.columns and pd.api.types.is_bool_dtype(data[value_col]):
        return _lsdd_not_applicable(variant_id, "boolean value column is not valid LSDD input", metadata)

    try:
        prepared = prepare_numeric_windows(
            data,
            time_col=time_col,
            value_col=value_col,
            reference_window=reference_window,
            current_window=current_window,
        )
    except (KeyError, ValueError, TypeError) as exc:
        return _lsdd_not_applicable(variant_id, str(exc), metadata)

    reference_values = prepared.reference_values
    current_values = prepared.current_values
    warnings = list(prepared.warnings)
    if threshold_warning:
        warnings.append(threshold_warning)
    metadata.update(prepared.metadata)

    if len(reference_values) < min_reference_size:
        return _lsdd_not_applicable(
            variant_id,
            f"effective reference sample size {len(reference_values)} is below min_reference_size {min_reference_size}",
            metadata,
            warnings,
        )
    if len(current_values) < min_current_size:
        return _lsdd_not_applicable(
            variant_id,
            f"effective current sample size {len(current_values)} is below min_current_size {min_current_size}",
            metadata,
            warnings,
        )

    try:
        bandwidth = _resolve_mmd_bandwidth(reference_values, current_values, params)
        pooled = np.concatenate([reference_values, current_values])
        centers, center_warnings = _select_lsdd_centers(
            pooled,
            n_centers=params.get("n_centers", "auto"),
            center_selection=center_selection,
            random_seed=random_seed,
        )
        warnings.extend(center_warnings)
        score_result = _lsdd_rbf_score(
            reference_values,
            current_values,
            centers=centers,
            gamma=bandwidth["gamma"],
            regularization_lambda=regularization_lambda,
        )
        lsdd_score = score_result["score"]
        p_value = None
        permutation_extreme_count = None
        if p_value_method == "permutation":
            p_value, permutation_extreme_count = _lsdd_permutation_p_value(
                reference_values,
                current_values,
                centers=centers,
                gamma=bandwidth["gamma"],
                regularization_lambda=regularization_lambda,
                observed_lsdd=lsdd_score,
                permutation_count=permutation_count,
                random_seed=random_seed,
            )
    except ValueError as exc:
        return _lsdd_not_applicable(variant_id, str(exc), metadata, warnings)
    except Exception as exc:
        return DriftResult(
            method_id=LSDD_METHOD_ID,
            method_name=LSDD_METHOD_NAME,
            method_category=METHOD_CATEGORY,
            variant_id=variant_id,
            drift_detected=None,
            severity="error",
            threshold=alpha if p_value_method == "permutation" else threshold,
            interpretation=f"LSDD calculation failed: {exc}",
            warnings=warnings + [f"LSDD calculation failed: {exc}"],
            metadata=metadata,
        )

    if not np.isfinite(lsdd_score):
        return _lsdd_not_applicable(variant_id, "LSDD score is not finite", metadata, warnings)
    if p_value is not None and (not np.isfinite(p_value) or not 0 <= p_value <= 1):
        return _lsdd_not_applicable(variant_id, "LSDD permutation p-value is invalid", metadata, warnings)

    sample_ratio = max(len(reference_values), len(current_values)) / min(len(reference_values), len(current_values))
    metadata.update(
        {
            "value_col": value_col,
            "threshold": threshold,
            "alpha": alpha,
            "kernel": "rbf",
            "kernel_bandwidth": bandwidth["sigma"],
            "kernel_gamma": bandwidth["gamma"],
            "bandwidth_policy": bandwidth["policy"],
            "regularization_lambda": regularization_lambda,
            "n_centers": int(len(centers)),
            "center_selection": center_selection,
            "raw_lsdd_objective": score_result["raw_objective"],
            "p_value_method": p_value_method,
            "nan_policy": nan_policy,
            "permutation_count": permutation_count if p_value_method == "permutation" else None,
            "random_seed": random_seed,
            "sample_size_ratio": float(sample_ratio),
            "multiple_testing_correction": params.get("multiple_testing_correction", "none"),
            "backend": "numpy_rbf_lsdd",
        }
    )
    if variant_id == "LSDD_WITH_PREPROCESSING":
        metadata["preprocessing_policy"] = "identity_numeric_projection"
        metadata["projection_policy"] = "single_projected_numeric_stream"
        metadata["projection_count"] = 1
    if sample_ratio > imbalance_warning_ratio:
        warnings.append("reference/current sample sizes are highly imbalanced")
    if _has_ties(reference_values, current_values):
        warnings.append("repeated or tied values detected; LSDD may reflect discrete or rounded data")
    if p_value_method == "none" and threshold is None:
        warnings.append("no LSDD score threshold supplied; returning LSDD score without binary alarm")
    if p_value_method == "permutation" and permutation_count < 199:
        warnings.append("low permutation_count gives coarse Monte Carlo p-value resolution")
    if params.get("multiple_testing_correction", "none") != "none":
        warnings.append("multiple_testing_correction is recorded but not applied by detect_lsdd")

    if p_value_method == "permutation":
        drift_detected = bool(p_value is not None and p_value < alpha)
        severity = "drift_detected" if drift_detected else "normal"
        alarm_state = "drift_detected" if drift_detected else "normal"
        threshold_out = alpha
    elif threshold is None:
        drift_detected = None
        severity = "watch"
        alarm_state = "undetermined"
        threshold_out = None
    elif lsdd_score > threshold:
        drift_detected = True
        severity = "drift_detected"
        alarm_state = "drift_detected"
        threshold_out = threshold
    else:
        drift_detected = False
        severity = "normal"
        alarm_state = "normal"
        threshold_out = threshold

    summary_measurements = _cvm_summary_measurements(reference_values, current_values)
    measurements: dict[str, Any] = {
        "TEST_STATISTIC": lsdd_score,
        "P_VALUE": p_value,
        "DRIFT_ALARM_STATE": alarm_state,
        "SAMPLE_SIZE": {
            "reference": int(len(reference_values)),
            "current": int(len(current_values)),
            "dropped_reference": int(metadata.get("reference_original_count", len(reference_values)) - len(reference_values)),
            "dropped_current": int(metadata.get("current_original_count", len(current_values)) - len(current_values)),
        },
        "SAMPLE_SIZE_REFERENCE": int(len(reference_values)),
        "SAMPLE_SIZE_CURRENT": int(len(current_values)),
        "WINDOW_SIZE": {"reference": int(len(reference_values)), "current": int(len(current_values))},
        "LSDD_SCORE": lsdd_score,
        "LSDD_RAW_OBJECTIVE": score_result["raw_objective"],
        "KERNEL": "rbf",
        "KERNEL_BANDWIDTH": bandwidth["sigma"],
        "KERNEL_GAMMA": bandwidth["gamma"],
        "BANDWIDTH_POLICY": bandwidth["policy"],
        "REGULARIZATION_LAMBDA": regularization_lambda,
        "N_CENTERS": int(len(centers)),
        "CENTER_SELECTION": center_selection,
        "MEAN_DELTA": float(np.mean(current_values) - np.mean(reference_values)),
        **summary_measurements,
    }
    if p_value_method == "permutation":
        measurements.update(
            {
                "PERMUTATION_COUNT": permutation_count,
                "PERMUTATION_EXTREME_COUNT": int(permutation_extreme_count),
                "PERMUTATION_ALTERNATIVE": "greater",
            }
        )

    return DriftResult(
        method_id=LSDD_METHOD_ID,
        method_name=LSDD_METHOD_NAME,
        method_category=METHOD_CATEGORY,
        variant_id=variant_id,
        drift_detected=drift_detected,
        severity=severity,
        drift_score=lsdd_score,
        p_value=p_value,
        test_statistic=lsdd_score,
        threshold=threshold_out,
        measurements=measurements,
        interpretation=_lsdd_interpretation(
            variant_id=variant_id,
            lsdd_score=lsdd_score,
            p_value=p_value,
            alpha=alpha,
            threshold=threshold,
            bandwidth=bandwidth,
            n_centers=len(centers),
            regularization_lambda=regularization_lambda,
            reference_count=len(reference_values),
            current_count=len(current_values),
            alarm_state=alarm_state,
            warnings=warnings,
        ),
        warnings=warnings,
        metadata=metadata,
    )


def _select_lsdd_centers(
    pooled_values: np.ndarray,
    *,
    n_centers: Any,
    center_selection: str,
    random_seed: int | None,
) -> tuple[np.ndarray, list[str]]:
    pooled_values = np.asarray(pooled_values, dtype=float)
    pooled_count = len(pooled_values)
    warnings: list[str] = []
    if isinstance(n_centers, str):
        if n_centers == "auto":
            count = min(100, pooled_count)
        elif n_centers == "all":
            count = pooled_count
        else:
            raise ValueError("n_centers must be a positive integer, 'auto', or 'all'")
    else:
        count = _positive_int(n_centers, "n_centers")
    if count > pooled_count:
        warnings.append("n_centers was capped by pooled sample size")
        count = pooled_count
    if center_selection == "quantile":
        centers = np.quantile(pooled_values, np.linspace(0.0, 1.0, count))
    else:
        rng = np.random.default_rng(random_seed)
        indices = rng.choice(pooled_count, size=count, replace=False)
        centers = np.sort(pooled_values[indices])
    if len(centers) == 0 or not np.isfinite(centers).all():
        raise ValueError("LSDD centers are invalid")
    return np.asarray(centers, dtype=float), warnings


def _lsdd_rbf_score(
    reference_values: np.ndarray,
    current_values: np.ndarray,
    *,
    centers: np.ndarray,
    gamma: float,
    regularization_lambda: float,
) -> dict[str, float]:
    phi_ref = np.exp(-gamma * (reference_values[:, None] - centers[None, :]) ** 2)
    phi_cur = np.exp(-gamma * (current_values[:, None] - centers[None, :]) ** 2)
    if not np.isfinite(phi_ref).all() or not np.isfinite(phi_cur).all():
        raise ValueError("non-finite LSDD basis matrix value")
    h = np.mean(phi_cur, axis=0) - np.mean(phi_ref, axis=0)
    h_mat = (phi_ref.T @ phi_ref / len(reference_values) + phi_cur.T @ phi_cur / len(current_values)) / 2.0
    system = h_mat + regularization_lambda * np.eye(len(centers))
    try:
        theta = np.linalg.solve(system, h)
    except np.linalg.LinAlgError:
        theta = np.linalg.lstsq(system, h, rcond=None)[0]
    if not np.isfinite(theta).all():
        raise ValueError("non-finite LSDD theta vector")
    raw_objective = float(h @ theta - 0.5 * theta @ h_mat @ theta)
    if not np.isfinite(raw_objective):
        raise ValueError("non-finite LSDD objective")
    return {"score": float(max(0.0, raw_objective)), "raw_objective": raw_objective}


def _lsdd_permutation_p_value(
    reference_values: np.ndarray,
    current_values: np.ndarray,
    *,
    centers: np.ndarray,
    gamma: float,
    regularization_lambda: float,
    observed_lsdd: float,
    permutation_count: int,
    random_seed: int | None,
) -> tuple[float, int]:
    rng = np.random.default_rng(random_seed)
    reference_count = len(reference_values)
    pooled = np.concatenate([reference_values, current_values]).astype(float, copy=True)
    extreme_count = 0
    for _ in range(permutation_count):
        permuted = rng.permutation(pooled)
        perm_reference = permuted[:reference_count]
        perm_current = permuted[reference_count:]
        perm_score = _lsdd_rbf_score(
            perm_reference,
            perm_current,
            centers=centers,
            gamma=gamma,
            regularization_lambda=regularization_lambda,
        )["score"]
        if perm_score >= observed_lsdd:
            extreme_count += 1
    return float((extreme_count + 1) / (permutation_count + 1)), extreme_count


def _lsdd_interpretation(
    *,
    variant_id: str,
    lsdd_score: float,
    p_value: float | None,
    alpha: float | None,
    threshold: float | None,
    bandwidth: dict[str, float | str],
    n_centers: int,
    regularization_lambda: float,
    reference_count: int,
    current_count: int,
    alarm_state: str,
    warnings: list[str],
) -> str:
    suffix = " Warnings are present." if warnings else ""
    if p_value is not None:
        rule = f"p-value={p_value:.6g}, alpha={alpha:.6g}"
    elif threshold is not None:
        rule = f"threshold={threshold:.6g}"
    else:
        rule = "no threshold or p-value; alarm is undetermined"
    return (
        f"{variant_id} compared {reference_count} reference rows and {current_count} current rows. "
        f"LSDD score={lsdd_score:.6g}, kernel=rbf, sigma={bandwidth['sigma']:.6g}, "
        f"gamma={bandwidth['gamma']:.6g}, n_centers={n_centers}, lambda={regularization_lambda:.6g}; "
        f"{rule}; alarm_state={alarm_state}.{suffix}"
    )


def _lsdd_not_applicable(
    variant_id: str | None,
    warning: str,
    metadata: dict[str, Any] | None = None,
    prior_warnings: list[str] | None = None,
) -> DriftResult:
    result = not_applicable_result(
        method_id=LSDD_METHOD_ID,
        method_name=LSDD_METHOD_NAME,
        method_category=METHOD_CATEGORY,
        variant_id=variant_id,
        warning=warning,
        metadata=metadata,
    )
    if prior_warnings:
        result.warnings = prior_warnings + result.warnings
    return result


def _prepare_mmd_feature_windows(
    data: pd.DataFrame,
    *,
    time_col: str,
    feature_cols: list[str],
    reference_window: tuple[str, str] | None,
    current_window: tuple[str, str] | None,
) -> WindowedNumericData:
    if reference_window is None or current_window is None:
        raise ValueError("reference_window and current_window are required")
    if time_col not in data.columns:
        raise KeyError(f"missing time column: {time_col}")
    missing = [column for column in feature_cols if column not in data.columns]
    if missing:
        raise KeyError(f"missing feature columns: {', '.join(missing)}")

    ref_start, ref_end = _parse_mmd_window(reference_window, "reference_window")
    cur_start, cur_end = _parse_mmd_window(current_window, "current_window")
    if max(ref_start, cur_start) <= min(ref_end, cur_end):
        raise ValueError("reference_window and current_window must not overlap")

    frame = data[[time_col, *feature_cols]].copy()
    original_rows = len(frame)
    frame[time_col] = pd.to_datetime(frame[time_col], errors="coerce")
    invalid_time_rows = int(frame[time_col].isna().sum())
    invalid_value_rows = 0
    for column in feature_cols:
        frame[column] = pd.to_numeric(frame[column], errors="coerce")
        invalid_value_rows += int((~np.isfinite(frame[column].to_numpy(dtype=float, na_value=np.nan))).sum())
    frame = frame.dropna(subset=[time_col, *feature_cols])
    finite_mask = np.isfinite(frame[feature_cols].to_numpy(dtype=float)).all(axis=1)
    frame = frame[finite_mask].sort_values(time_col)

    reference_frame = frame[(frame[time_col] >= ref_start) & (frame[time_col] <= ref_end)]
    current_frame = frame[(frame[time_col] >= cur_start) & (frame[time_col] <= cur_end)]
    parsed_times = pd.to_datetime(data[time_col], errors="coerce")
    metadata = {
        "original_rows": original_rows,
        "valid_rows": int(len(frame)),
        "invalid_time_rows": invalid_time_rows,
        "invalid_value_rows": invalid_value_rows,
        "reference_window": [ref_start.isoformat(), ref_end.isoformat()],
        "current_window": [cur_start.isoformat(), cur_end.isoformat()],
        "reference_original_count": int(((parsed_times >= ref_start) & (parsed_times <= ref_end)).sum()),
        "current_original_count": int(((parsed_times >= cur_start) & (parsed_times <= cur_end)).sum()),
        "reference_effective_count": int(len(reference_frame)),
        "current_effective_count": int(len(current_frame)),
        "feature_cols": list(feature_cols),
    }
    warnings: list[str] = []
    if invalid_time_rows:
        warnings.append(f"dropped {invalid_time_rows} rows with invalid timestamps")
    if invalid_value_rows:
        warnings.append(f"dropped {invalid_value_rows} feature values with non-finite numeric values")

    return WindowedNumericData(
        reference_values=reference_frame[feature_cols].to_numpy(dtype=float),
        current_values=current_frame[feature_cols].to_numpy(dtype=float),
        metadata=metadata,
        warnings=warnings,
    )


def _parse_mmd_window(window: tuple[str, str], name: str) -> tuple[pd.Timestamp, pd.Timestamp]:
    if len(window) != 2:
        raise ValueError(f"{name} must be a (start, end) pair")
    start = pd.to_datetime(window[0], errors="coerce")
    end = pd.to_datetime(window[1], errors="coerce")
    if pd.isna(start) or pd.isna(end):
        raise ValueError(f"{name} contains an unparseable timestamp")
    if start > end:
        raise ValueError(f"{name} start must be <= end")
    return start, end


def _resolve_mmd_threshold(params: dict[str, Any], p_value_method: str) -> tuple[float | None, str | None]:
    if p_value_method == "permutation":
        return params.get("threshold"), None
    value = params.get("threshold")
    warning = None
    if "threshold_or_alpha" in params:
        value = params["threshold_or_alpha"]
        warning = "threshold_or_alpha was interpreted as an MMD score threshold, not a p-value alpha"
    if value is None:
        return None, warning
    threshold = float(value)
    if not np.isfinite(threshold) or threshold < 0:
        raise ValueError("threshold must be a finite number >= 0")
    return threshold, warning


def _resolve_mmd_bandwidth(
    reference_values: np.ndarray,
    current_values: np.ndarray,
    params: dict[str, Any],
) -> dict[str, float | str]:
    gamma_value = params.get("gamma")
    bandwidth_value = params.get("kernel_bandwidth", "median")
    bandwidth_policy = str(params.get("bandwidth_policy", "median"))
    if bandwidth_policy not in {"median", "fixed"}:
        raise ValueError("bandwidth_policy must be 'median' or 'fixed'")
    if gamma_value is not None:
        if bandwidth_value not in {"median", "median_heuristic"}:
            raise ValueError("gamma and numeric kernel_bandwidth must not both be supplied")
        gamma = float(gamma_value)
        if not np.isfinite(gamma) or gamma <= 0:
            raise ValueError("gamma must be a finite positive number")
        sigma = float(np.sqrt(1.0 / (2.0 * gamma)))
        return {"sigma": sigma, "gamma": gamma, "policy": "fixed"}
    if isinstance(bandwidth_value, str):
        if bandwidth_value not in {"median", "median_heuristic"}:
            raise ValueError("kernel_bandwidth string must be 'median' or 'median_heuristic'")
        pooled = _mmd_as_2d(np.concatenate([reference_values, current_values], axis=0))
        distances = np.sqrt(_pairwise_squared_distances(pooled, pooled))
        positive_distances = distances[distances > 0]
        if len(positive_distances) == 0:
            raise ValueError("median bandwidth cannot be resolved when all pooled values are identical")
        sigma = float(np.median(positive_distances))
        policy = "median"
    else:
        sigma = float(bandwidth_value)
        policy = "fixed"
    if bandwidth_policy == "fixed" and policy != "fixed":
        raise ValueError("bandwidth_policy='fixed' requires numeric kernel_bandwidth or gamma")
    if not np.isfinite(sigma) or sigma <= 0:
        raise ValueError("kernel_bandwidth must be a finite positive number")
    gamma = float(1.0 / (2.0 * sigma * sigma))
    return {"sigma": sigma, "gamma": gamma, "policy": policy}


def _mmd_rbf_statistic(
    reference_values: np.ndarray,
    current_values: np.ndarray,
    *,
    gamma: float,
    variant_id: str,
) -> float:
    reference_values = _mmd_as_2d(reference_values)
    current_values = _mmd_as_2d(current_values)
    kxx = np.exp(-gamma * _pairwise_squared_distances(reference_values, reference_values))
    kyy = np.exp(-gamma * _pairwise_squared_distances(current_values, current_values))
    kxy = np.exp(-gamma * _pairwise_squared_distances(reference_values, current_values))
    if not np.isfinite(kxx).all() or not np.isfinite(kyy).all() or not np.isfinite(kxy).all():
        raise ValueError("non-finite kernel matrix value")
    if variant_id == "KERNEL_MMD_UNBIASED":
        n = len(reference_values)
        m = len(current_values)
        if n < 2 or m < 2:
            raise ValueError("unbiased MMD requires at least two values per sample")
        return float(
            (np.sum(kxx) - np.trace(kxx)) / (n * (n - 1))
            + (np.sum(kyy) - np.trace(kyy)) / (m * (m - 1))
            - 2.0 * np.mean(kxy)
        )
    return float(np.mean(kxx) + np.mean(kyy) - 2.0 * np.mean(kxy))


def _mmd_as_2d(values: np.ndarray) -> np.ndarray:
    array = np.asarray(values, dtype=float)
    if array.ndim == 1:
        return array.reshape(-1, 1)
    if array.ndim == 2:
        return array
    raise ValueError("MMD input must be a 1D numeric vector or 2D feature matrix")


def _pairwise_squared_distances(left: np.ndarray, right: np.ndarray) -> np.ndarray:
    if left.shape[1] != right.shape[1]:
        raise ValueError("MMD feature dimensions must match")
    diff = left[:, None, :] - right[None, :, :]
    return np.sum(diff * diff, axis=2)


def _mmd_permutation_p_value(
    reference_values: np.ndarray,
    current_values: np.ndarray,
    *,
    gamma: float,
    variant_id: str,
    observed_mmd: float,
    permutation_count: int,
    random_seed: int | None,
) -> tuple[float, int]:
    rng = np.random.default_rng(random_seed)
    reference_count = len(reference_values)
    pooled = np.concatenate([_mmd_as_2d(reference_values), _mmd_as_2d(current_values)], axis=0).astype(float, copy=True)
    extreme_count = 0
    for _ in range(permutation_count):
        permuted = rng.permutation(pooled)
        perm_reference = permuted[:reference_count]
        perm_current = permuted[reference_count:]
        perm_mmd = _mmd_rbf_statistic(perm_reference, perm_current, gamma=gamma, variant_id=variant_id)
        if perm_mmd >= observed_mmd:
            extreme_count += 1
    return float((extreme_count + 1) / (permutation_count + 1)), extreme_count


def _mmd_interpretation(
    *,
    variant_id: str,
    mmd_score: float,
    p_value: float | None,
    alpha: float | None,
    threshold: float | None,
    bandwidth: dict[str, float | str],
    reference_count: int,
    current_count: int,
    alarm_state: str,
    warnings: list[str],
) -> str:
    suffix = " Warnings are present." if warnings else ""
    if p_value is not None:
        rule = f"p-value={p_value:.6g}, alpha={alpha:.6g}"
    elif threshold is not None:
        rule = f"threshold={threshold:.6g}"
    else:
        rule = "no threshold or p-value; alarm is undetermined"
    return (
        f"{variant_id} compared {reference_count} reference rows and {current_count} current rows. "
        f"MMD^2={mmd_score:.6g}, kernel=rbf, sigma={bandwidth['sigma']:.6g}, "
        f"gamma={bandwidth['gamma']:.6g}; {rule}; alarm_state={alarm_state}.{suffix}"
    )


def _mmd_not_applicable(
    variant_id: str | None,
    warning: str,
    metadata: dict[str, Any] | None = None,
    prior_warnings: list[str] | None = None,
) -> DriftResult:
    result = not_applicable_result(
        method_id=MMD_METHOD_ID,
        method_name=MMD_METHOD_NAME,
        method_category=METHOD_CATEGORY,
        variant_id=variant_id,
        warning=warning,
        metadata=metadata,
    )
    if prior_warnings:
        result.warnings = prior_warnings + result.warnings
    return result


def _resolve_epps_singleton_t_points(params: dict[str, Any]) -> tuple[float, ...]:
    raw = params.get("t_points", (0.4, 0.8))
    if isinstance(raw, (str, bytes)):
        raise ValueError("t_points must be a numeric sequence, not a string")
    values = tuple(float(value) for value in raw)
    if not values:
        raise ValueError("t_points must not be empty")
    if any((not np.isfinite(value)) or value <= 0 for value in values):
        raise ValueError("t_points must contain finite positive values")
    if len(set(values)) != len(values):
        raise ValueError("t_points must not contain duplicates")
    return values


def _epps_singleton_discrete_metadata(reference_values: np.ndarray, current_values: np.ndarray) -> dict[str, Any]:
    def top_counts(values: np.ndarray) -> list[dict[str, int | float]]:
        unique, counts = np.unique(values, return_counts=True)
        order = np.argsort(counts)[::-1][:5]
        return [{"value": float(unique[index]), "count": int(counts[index])} for index in order]

    return {
        "DISCRETE_VALUE_COUNT_REFERENCE": int(len(np.unique(reference_values))),
        "DISCRETE_VALUE_COUNT_CURRENT": int(len(np.unique(current_values))),
        "DISCRETE_TOP_VALUE_FREQUENCIES": {
            "reference": top_counts(reference_values),
            "current": top_counts(current_values),
        },
    }


def _epps_singleton_interpretation(
    *,
    variant_id: str,
    statistic: float,
    p_value: float,
    alpha: float,
    t_points: tuple[float, ...],
    reference_count: int,
    current_count: int,
    drift_detected: bool,
    warnings: list[str],
) -> str:
    decision = "numeric distribution drift candidate" if drift_detected else "normal"
    suffix = " Warnings are present." if warnings else ""
    return (
        f"{variant_id} compared {reference_count} reference rows and {current_count} current rows. "
        f"Epps-Singleton statistic={statistic:.6g}, p-value={p_value:.6g}, alpha={alpha:.6g}, "
        f"t_points={list(t_points)}; decision={decision}.{suffix}"
    )


def _epps_singleton_not_applicable(
    variant_id: str | None,
    warning: str,
    metadata: dict[str, Any] | None = None,
    prior_warnings: list[str] | None = None,
) -> DriftResult:
    result = not_applicable_result(
        method_id=EPPS_SINGLETON_METHOD_ID,
        method_name=EPPS_SINGLETON_METHOD_NAME,
        method_category=METHOD_CATEGORY,
        variant_id=variant_id,
        warning=warning,
        metadata=metadata,
    )
    if prior_warnings:
        result.warnings = prior_warnings + result.warnings
    return result


def _resolve_energy_distance_threshold(params: dict[str, Any], variant_id: str) -> tuple[float | None, str | None]:
    if variant_id == "ENERGY_DISTANCE_PERMUTATION_TEST":
        return params.get("threshold"), None
    value = params.get("threshold")
    warning = None
    if "threshold_or_alpha" in params:
        value = params["threshold_or_alpha"]
        warning = "threshold_or_alpha was interpreted as an Energy distance threshold, not a p-value alpha"
    if value is None:
        return None, warning
    threshold = float(value)
    if not np.isfinite(threshold) or threshold < 0:
        raise ValueError("threshold must be a finite number >= 0")
    return threshold, warning


def _energy_distance_permutation_p_value(
    reference_values: np.ndarray,
    current_values: np.ndarray,
    *,
    observed_distance: float,
    permutation_count: int,
    random_seed: int | None,
) -> tuple[float, int]:
    rng = np.random.default_rng(random_seed)
    reference_count = len(reference_values)
    pooled = np.concatenate([reference_values, current_values]).astype(float, copy=True)
    extreme_count = 0
    for _ in range(permutation_count):
        permuted = rng.permutation(pooled)
        perm_reference = permuted[:reference_count]
        perm_current = permuted[reference_count:]
        perm_distance = float(energy_distance(perm_reference, perm_current))
        if perm_distance >= observed_distance:
            extreme_count += 1
    return float((extreme_count + 1) / (permutation_count + 1)), extreme_count


def _energy_distance_interpretation(
    *,
    variant_id: str,
    distance: float,
    p_value: float | None,
    alpha: float | None,
    threshold: float | None,
    reference_count: int,
    current_count: int,
    alarm_state: str,
    warnings: list[str],
) -> str:
    suffix = " Warnings are present." if warnings else ""
    if p_value is not None:
        rule = f"p-value={p_value:.6g}, alpha={alpha:.6g}"
    elif threshold is not None:
        rule = f"threshold={threshold:.6g}"
    else:
        rule = "no threshold or p-value; alarm is undetermined"
    return (
        f"{variant_id} compared {reference_count} reference rows and {current_count} current rows. "
        f"Energy distance={distance:.6g}; {rule}; alarm_state={alarm_state}.{suffix}"
    )


def _energy_distance_not_applicable(
    variant_id: str | None,
    warning: str,
    metadata: dict[str, Any] | None = None,
    prior_warnings: list[str] | None = None,
) -> DriftResult:
    result = not_applicable_result(
        method_id=ENERGY_DISTANCE_METHOD_ID,
        method_name=ENERGY_DISTANCE_METHOD_NAME,
        method_category=METHOD_CATEGORY,
        variant_id=variant_id,
        warning=warning,
        metadata=metadata,
    )
    if prior_warnings:
        result.warnings = prior_warnings + result.warnings
    return result


def _resolve_f_test_alternative(params: dict[str, Any]) -> str:
    alternative = str(params.get("alternative", params.get("direction_or_alternative", "two-sided")))
    aliases = {
        "both": "two-sided",
        "two_sided": "two-sided",
        "greater": "current_greater",
        "current_greater": "current_greater",
        "increase": "current_greater",
        "reference_less": "current_greater",
        "less": "current_less",
        "current_less": "current_less",
        "decrease": "current_less",
        "reference_greater": "current_less",
    }
    resolved = aliases.get(alternative, alternative)
    if resolved not in {"two-sided", "current_greater", "current_less"}:
        raise ValueError("alternative must be two-sided, current_greater, current_less, or a documented alias")
    return resolved


def _f_test_equal_variance_statistic(
    reference_values: np.ndarray,
    current_values: np.ndarray,
    *,
    alternative: str,
) -> dict[str, float | int | str]:
    variance_reference = float(np.var(reference_values, ddof=1))
    variance_current = float(np.var(current_values, ddof=1))
    if (
        not np.isfinite(variance_reference)
        or not np.isfinite(variance_current)
        or variance_reference <= 0
        or variance_current <= 0
    ):
        raise ValueError("reference and current sample variances must be finite and positive")
    df_reference = len(reference_values) - 1
    df_current = len(current_values) - 1
    variance_ratio = float(variance_current / variance_reference)
    variance_ratio_abs = float(max(variance_current, variance_reference) / min(variance_current, variance_reference))
    if alternative == "two-sided":
        return {
            "variance_reference": variance_reference,
            "variance_current": variance_current,
            "variance_ratio": variance_ratio,
            "variance_ratio_abs": variance_ratio_abs,
            "directional_ratio": variance_ratio,
            "test_statistic": variance_ratio_abs,
            "df_reference": df_reference,
            "df_current": df_current,
            "df_numerator": df_current if variance_ratio >= 1 else df_reference,
            "df_denominator": df_reference if variance_ratio >= 1 else df_current,
            "statistic_definition": "larger_variance_over_smaller_variance",
        }
    return {
        "variance_reference": variance_reference,
        "variance_current": variance_current,
        "variance_ratio": variance_ratio,
        "variance_ratio_abs": variance_ratio_abs,
        "directional_ratio": variance_ratio,
        "test_statistic": variance_ratio,
        "df_reference": df_reference,
        "df_current": df_current,
        "df_numerator": df_current,
        "df_denominator": df_reference,
        "statistic_definition": "current_variance_over_reference_variance",
    }


def _f_distribution_p_value(
    directional_ratio: float,
    *,
    df_current: int,
    df_reference: int,
    alternative: str,
) -> float:
    if alternative == "current_greater":
        return float(f.sf(directional_ratio, df_current, df_reference))
    if alternative == "current_less":
        return float(f.cdf(directional_ratio, df_current, df_reference))
    lower = float(f.cdf(directional_ratio, df_current, df_reference))
    upper = float(f.sf(directional_ratio, df_current, df_reference))
    return float(min(1.0, 2.0 * min(lower, upper)))


def _f_test_interpretation(
    *,
    alternative: str,
    test_statistic: float,
    p_value: float,
    alpha: float,
    variance_reference: float,
    variance_current: float,
    variance_ratio: float,
    drift_detected: bool,
    warnings: list[str],
) -> str:
    decision = "numeric variance/scale drift candidate" if drift_detected else "normal"
    suffix = " Warnings are present." if warnings else ""
    return (
        f"F_TEST_EQUAL_VARIANCE ran with alternative={alternative}. F statistic={test_statistic:.6g}, "
        f"p-value={p_value:.6g}, alpha={alpha:.6g}; reference_variance={variance_reference:.6g}, "
        f"current_variance={variance_current:.6g}, variance_ratio={variance_ratio:.6g}; "
        f"decision={decision}.{suffix}"
    )


def _f_test_not_applicable(
    variant_id: str | None,
    warning: str,
    metadata: dict[str, Any] | None = None,
    prior_warnings: list[str] | None = None,
) -> DriftResult:
    result = not_applicable_result(
        method_id=F_TEST_METHOD_ID,
        method_name=F_TEST_METHOD_NAME,
        method_category=METHOD_CATEGORY,
        variant_id=variant_id,
        warning=warning,
        metadata=metadata,
    )
    if prior_warnings:
        result.warnings = prior_warnings + result.warnings
    return result


def _bws_two_sample_statistic(reference_values: np.ndarray, current_values: np.ndarray) -> tuple[float, float, float]:
    reference_values = np.asarray(reference_values, dtype=float)
    current_values = np.asarray(current_values, dtype=float)
    n = len(reference_values)
    m = len(current_values)
    if n == 0 or m == 0:
        raise ValueError("reference and current samples must be non-empty")
    total = n + m
    pooled = np.concatenate([reference_values, current_values])
    pooled_ranks = pd.Series(pooled).rank(method="average").to_numpy(dtype=float)
    reference_ranks = pooled_ranks[:n][np.argsort(reference_values, kind="mergesort")]
    current_ranks = pooled_ranks[n:][np.argsort(current_values, kind="mergesort")]

    i = np.arange(1, n + 1, dtype=float)
    j = np.arange(1, m + 1, dtype=float)
    reference_expected = (total + 1) * i / n
    current_expected = (total + 1) * j / m
    reference_weight = (i / (n + 1)) * (1 - i / (n + 1)) * (m * (total + 1) / n)
    current_weight = (j / (m + 1)) * (1 - j / (m + 1)) * (n * (total + 1) / m)
    reference_component = float(np.mean(((reference_ranks - reference_expected) ** 2) / reference_weight))
    current_component = float(np.mean(((current_ranks - current_expected) ** 2) / current_weight))
    statistic = float(0.5 * (reference_component + current_component))
    return statistic, reference_component, current_component


def _bws_permutation_p_value(
    reference_values: np.ndarray,
    current_values: np.ndarray,
    *,
    observed_statistic: float,
    permutation_count: int,
    random_seed: int | None,
) -> float:
    rng = np.random.default_rng(random_seed)
    reference_count = len(reference_values)
    pooled = np.concatenate([reference_values, current_values]).astype(float, copy=True)
    exceed_count = 0
    for _ in range(permutation_count):
        permuted = rng.permutation(pooled)
        perm_reference = permuted[:reference_count]
        perm_current = permuted[reference_count:]
        perm_statistic, _, _ = _bws_two_sample_statistic(perm_reference, perm_current)
        if perm_statistic >= observed_statistic:
            exceed_count += 1
    return float((exceed_count + 1) / (permutation_count + 1))


def _bws_interpretation(
    *,
    variant_id: str,
    statistic: float,
    p_value: float | None,
    alpha: float,
    threshold: float | None,
    decision_policy: str,
    reference_count: int,
    current_count: int,
    median_delta: float,
    drift_detected: bool,
    warnings: list[str],
) -> str:
    decision = "numeric distribution drift candidate" if drift_detected else "normal"
    suffix = " Warnings are present." if warnings else ""
    if decision_policy == "p_value":
        rule = f"p-value={p_value:.6g}, alpha={alpha:.6g}"
    else:
        rule = f"threshold={threshold:.6g}"
    return (
        f"{variant_id} compared {reference_count} reference rows and {current_count} current rows. "
        f"BWS statistic={statistic:.6g}, {rule}; median_delta={median_delta:.6g}; "
        f"decision={decision}.{suffix}"
    )


def _bws_not_applicable(
    variant_id: str | None,
    warning: str,
    metadata: dict[str, Any] | None = None,
    prior_warnings: list[str] | None = None,
) -> DriftResult:
    result = not_applicable_result(
        method_id=BAUMGARTNER_WEISS_SCHINDLER_METHOD_ID,
        method_name=BAUMGARTNER_WEISS_SCHINDLER_METHOD_NAME,
        method_category=METHOD_CATEGORY,
        variant_id=variant_id,
        warning=warning,
        metadata=metadata,
    )
    if prior_warnings:
        result.warnings = prior_warnings + result.warnings
    return result


def _resolve_kuiper_alpha(params: dict[str, Any], decision_policy: str) -> float:
    if decision_policy == "threshold" and "threshold_or_alpha" in params and "alpha" not in params:
        params = dict(params)
        params.pop("threshold_or_alpha")
    return _resolve_anderson_alpha(params)


def _resolve_kuiper_threshold(params: dict[str, Any], decision_policy: str) -> float | None:
    if decision_policy != "threshold":
        return None
    value = params.get("threshold", params.get("threshold_or_alpha"))
    if value is None:
        raise ValueError("threshold mode requires threshold or threshold_or_alpha")
    threshold = float(value)
    if not np.isfinite(threshold) or threshold < 0:
        raise ValueError("threshold must be a finite number >= 0")
    return threshold


def _optional_int(value: Any, name: str) -> int | None:
    if value is None:
        return None
    parsed = int(value)
    if parsed != value and not (isinstance(value, str) and str(parsed) == value):
        raise ValueError(f"{name} must be an integer")
    return parsed


def _kuiper_two_sample_statistic(reference_values: np.ndarray, current_values: np.ndarray) -> tuple[float, float, float]:
    reference_sorted = np.sort(np.asarray(reference_values, dtype=float))
    current_sorted = np.sort(np.asarray(current_values, dtype=float))
    if len(reference_sorted) == 0 or len(current_sorted) == 0:
        raise ValueError("reference and current samples must be non-empty")
    grid = np.sort(np.unique(np.concatenate([reference_sorted, current_sorted])))
    reference_cdf = np.searchsorted(reference_sorted, grid, side="right") / len(reference_sorted)
    current_cdf = np.searchsorted(current_sorted, grid, side="right") / len(current_sorted)
    d_plus = float(np.max(reference_cdf - current_cdf))
    d_minus = float(np.max(current_cdf - reference_cdf))
    statistic = float(d_plus + d_minus)
    return statistic, d_plus, d_minus


def _kuiper_permutation_p_value(
    reference_values: np.ndarray,
    current_values: np.ndarray,
    *,
    observed_statistic: float,
    permutation_count: int,
    random_seed: int | None,
) -> float:
    rng = np.random.default_rng(random_seed)
    reference_count = len(reference_values)
    pooled = np.concatenate([reference_values, current_values]).astype(float, copy=True)
    exceed_count = 0
    for _ in range(permutation_count):
        permuted = rng.permutation(pooled)
        perm_reference = permuted[:reference_count]
        perm_current = permuted[reference_count:]
        perm_statistic, _, _ = _kuiper_two_sample_statistic(perm_reference, perm_current)
        if perm_statistic >= observed_statistic:
            exceed_count += 1
    return float((exceed_count + 1) / (permutation_count + 1))


def _kuiper_interpretation(
    *,
    statistic: float,
    d_plus: float,
    d_minus: float,
    p_value: float | None,
    alpha: float,
    threshold: float | None,
    decision_policy: str,
    reference_count: int,
    current_count: int,
    median_delta: float,
    drift_detected: bool,
    warnings: list[str],
) -> str:
    decision = "numeric distribution drift candidate" if drift_detected else "normal"
    suffix = " Warnings are present." if warnings else ""
    if decision_policy == "p_value":
        rule = f"p-value={p_value:.6g}, alpha={alpha:.6g}"
    else:
        rule = f"threshold={threshold:.6g}"
    return (
        f"KUIPER_TWO_SAMPLE compared {reference_count} reference rows and {current_count} current rows. "
        f"Kuiper statistic={statistic:.6g}, D_plus={d_plus:.6g}, D_minus={d_minus:.6g}, "
        f"{rule}; median_delta={median_delta:.6g}; decision={decision}.{suffix}"
    )


def _kuiper_not_applicable(
    variant_id: str | None,
    warning: str,
    metadata: dict[str, Any] | None = None,
    prior_warnings: list[str] | None = None,
) -> DriftResult:
    result = not_applicable_result(
        method_id=KUIPER_METHOD_ID,
        method_name=KUIPER_METHOD_NAME,
        method_category=METHOD_CATEGORY,
        variant_id=variant_id,
        warning=warning,
        metadata=metadata,
    )
    if prior_warnings:
        result.warnings = prior_warnings + result.warnings
    return result


def _resolve_cvm_alpha(params: dict[str, Any]) -> float:
    return _resolve_anderson_alpha(params)


def _resolve_cvm_p_value_method(params: dict[str, Any]) -> str:
    method = str(params.get("p_value_method", "auto"))
    if method not in {"auto", "asymptotic", "exact"}:
        raise ValueError("p_value_method must be one of auto, asymptotic, exact")
    return method


def _cvm_summary_measurements(reference_values: np.ndarray, current_values: np.ndarray) -> dict[str, float]:
    ref_q25, ref_q75 = np.quantile(reference_values, [0.25, 0.75])
    cur_q25, cur_q75 = np.quantile(current_values, [0.25, 0.75])
    ref_median = float(np.median(reference_values))
    cur_median = float(np.median(current_values))
    return {
        "REFERENCE_MEAN": float(np.mean(reference_values)),
        "CURRENT_MEAN": float(np.mean(current_values)),
        "REFERENCE_MEDIAN": ref_median,
        "CURRENT_MEDIAN": cur_median,
        "REFERENCE_Q25": float(ref_q25),
        "CURRENT_Q25": float(cur_q25),
        "REFERENCE_Q75": float(ref_q75),
        "CURRENT_Q75": float(cur_q75),
        "MEDIAN_DELTA": float(cur_median - ref_median),
    }


def _cramer_von_mises_interpretation(
    *,
    statistic: float,
    p_value: float,
    alpha: float,
    reference_count: int,
    current_count: int,
    median_delta: float,
    drift_detected: bool,
    warnings: list[str],
) -> str:
    decision = "numeric distribution drift candidate" if drift_detected else "normal"
    suffix = " Warnings are present." if warnings else ""
    return (
        f"TWO_SAMPLE_CVM compared {reference_count} reference rows and {current_count} current rows. "
        f"Cramer-von Mises statistic={statistic:.6g}, p-value={p_value:.6g}, alpha={alpha:.6g}; "
        f"median_delta={median_delta:.6g}; decision={decision}.{suffix}"
    )


def _cramer_von_mises_not_applicable(
    variant_id: str | None,
    warning: str,
    metadata: dict[str, Any] | None = None,
    prior_warnings: list[str] | None = None,
) -> DriftResult:
    result = not_applicable_result(
        method_id=CRAMER_VON_MISES_METHOD_ID,
        method_name=CRAMER_VON_MISES_METHOD_NAME,
        method_category=METHOD_CATEGORY,
        variant_id=variant_id,
        warning=warning,
        metadata=metadata,
    )
    if prior_warnings:
        result.warnings = prior_warnings + result.warnings
    return result


def _resolve_anderson_alpha(params: dict[str, Any]) -> float:
    alpha_values = []
    for key in ("alpha", "threshold_or_alpha", "significance_level"):
        if key in params and params[key] is not None:
            alpha_values.append((key, float(params[key])))
    if not alpha_values:
        return 0.05
    first_key, first_value = alpha_values[0]
    for key, value in alpha_values[1:]:
        if not np.isclose(first_value, value):
            raise ValueError(f"conflicting alpha aliases: {first_key}={first_value} and {key}={value}")
    if not 0 < first_value < 1:
        raise ValueError("alpha must be in (0, 1)")
    return float(first_value)


def _resolve_tail_quantiles(params: dict[str, Any]) -> tuple[float, float]:
    raw = params.get("tail_quantiles", (0.05, 0.95))
    if isinstance(raw, dict):
        lower = float(raw["lower"])
        upper = float(raw["upper"])
    else:
        if len(raw) != 2:
            raise ValueError("tail_quantiles must contain exactly two values")
        lower = float(raw[0])
        upper = float(raw[1])
    if not 0 < lower < upper < 1:
        raise ValueError("tail_quantiles must satisfy 0 < lower < upper < 1")
    return lower, upper


def _tail_sensitive_measurements(
    reference_values: np.ndarray,
    current_values: np.ndarray,
    tail_quantiles: tuple[float, float],
) -> tuple[dict[str, Any], list[str]]:
    lower_q, upper_q = tail_quantiles
    lower_threshold = float(np.quantile(reference_values, lower_q))
    upper_threshold = float(np.quantile(reference_values, upper_q))

    ref_lower_count = int(np.sum(reference_values <= lower_threshold))
    ref_upper_count = int(np.sum(reference_values >= upper_threshold))
    cur_lower_count = int(np.sum(current_values <= lower_threshold))
    cur_upper_count = int(np.sum(current_values >= upper_threshold))

    ref_n = len(reference_values)
    cur_n = len(current_values)
    ref_lower_rate = float(ref_lower_count / ref_n)
    ref_upper_rate = float(ref_upper_count / ref_n)
    cur_lower_rate = float(cur_lower_count / cur_n)
    cur_upper_rate = float(cur_upper_count / cur_n)

    warnings = []
    if min(ref_lower_count, ref_upper_count, cur_lower_count, cur_upper_count) < 5:
        warnings.append("one or more Anderson-Darling tail buckets have fewer than 5 observations")

    measurements = {
        "TAIL_QUANTILES": {"lower": lower_q, "upper": upper_q},
        "TAIL_THRESHOLDS": {"lower": lower_threshold, "upper": upper_threshold},
        "TAIL_COUNTS_REFERENCE": {"lower": ref_lower_count, "upper": ref_upper_count},
        "TAIL_COUNTS_CURRENT": {"lower": cur_lower_count, "upper": cur_upper_count},
        "TAIL_RATES_REFERENCE": {"lower": ref_lower_rate, "upper": ref_upper_rate},
        "TAIL_RATES_CURRENT": {"lower": cur_lower_rate, "upper": cur_upper_rate},
        "TAIL_RATE_DELTA": {
            "lower": float(cur_lower_rate - ref_lower_rate),
            "upper": float(cur_upper_rate - ref_upper_rate),
        },
    }
    return measurements, warnings


def _anderson_darling_interpretation(
    *,
    variant_id: str,
    statistic: float,
    p_value: float,
    alpha: float,
    reference_count: int,
    current_count: int,
    drift_detected: bool,
    warnings: list[str],
) -> str:
    decision = "distribution drift candidate" if drift_detected else "normal"
    suffix = " Warnings are present." if warnings else ""
    return (
        f"{variant_id} compared {reference_count} reference rows and {current_count} current rows. "
        f"Anderson-Darling statistic={statistic:.6g}, p-value={p_value:.6g}, alpha={alpha:.6g}; "
        f"decision={decision}.{suffix}"
    )


def _anderson_darling_not_applicable(
    variant_id: str | None,
    warning: str,
    metadata: dict[str, Any] | None = None,
    prior_warnings: list[str] | None = None,
) -> DriftResult:
    result = not_applicable_result(
        method_id=ANDERSON_DARLING_METHOD_ID,
        method_name=ANDERSON_DARLING_METHOD_NAME,
        method_category=METHOD_CATEGORY,
        variant_id=variant_id,
        warning=warning,
        metadata=metadata,
    )
    if prior_warnings:
        result.warnings = prior_warnings + result.warnings
    return result


def _resolve_alpha(params: dict[str, Any]) -> float:
    value = params.get("threshold_or_alpha", params.get("alpha", 0.05))
    alpha = float(value)
    if not 0 < alpha < 1:
        raise ValueError("alpha must be in (0, 1)")
    return alpha


def _resolve_alternative(variant_id: str, params: dict[str, Any]) -> str:
    forced = {
        "ONE_SAMPLE_KS_KNOWN_CDF": "two-sided",
        "TWO_SAMPLE_KS_TWO_SIDED": "two-sided",
        "TWO_SAMPLE_KS_ONE_SIDED_GREATER": "greater",
        "TWO_SAMPLE_KS_ONE_SIDED_LESS": "less",
        "TWO_SAMPLE_KS_EXACT_PVALUE": "two-sided",
        "TWO_SAMPLE_KS_ASYMPTOTIC_PVALUE": "two-sided",
        "KS_WITH_TIES_OR_DISCRETE_CAUTION": "two-sided",
        "LILLIEFORS_RELATED_ONE_SAMPLE": "two-sided",
        "HIGHER_ORDER_KS": "two-sided",
        "TWO_SAMPLE_KS_APPROX_QUANTILE": "two-sided",
    }[variant_id]
    requested = params.get("direction_or_alternative", params.get("alternative", forced))
    requested = _normalize_alternative(str(requested))
    if requested != forced:
        raise ValueError(f"conflicting alternative for {variant_id}: expected {forced}, got {requested}")
    return forced


def _normalize_alternative(value: str) -> str:
    aliases = {"both": "two-sided", "two_sided": "two-sided"}
    normalized = aliases.get(value, value)
    if normalized not in {"two-sided", "greater", "less"}:
        raise ValueError("alternative must be one of two-sided, greater, less")
    return normalized


def _resolve_mann_whitney_alternative(variant_id: str, params: dict[str, Any]) -> str:
    if variant_id == "MANN_WHITNEY_TWO_SIDED":
        requested = str(params.get("alternative", "two-sided"))
        normalized = _normalize_mann_whitney_direction(requested)
        if normalized != "two-sided":
            raise ValueError("MANN_WHITNEY_TWO_SIDED requires alternative='two-sided'")
        return normalized
    if variant_id == "MANN_WHITNEY_EXACT":
        return _normalize_mann_whitney_direction(str(params.get("alternative", "two-sided")))
    requested = params.get("direction_or_alternative", params.get("alternative"))
    if requested is None:
        raise ValueError("MANN_WHITNEY_ONE_SIDED requires alternative or direction_or_alternative")
    normalized = _normalize_mann_whitney_direction(str(requested))
    if normalized == "two-sided":
        raise ValueError("MANN_WHITNEY_ONE_SIDED requires greater/less direction")
    return normalized


def _normalize_mann_whitney_direction(value: str) -> str:
    aliases = {
        "both": "two-sided",
        "two_sided": "two-sided",
        "up": "less",
        "increase": "less",
        "current_increase": "less",
        "down": "greater",
        "decrease": "greater",
        "current_decrease": "greater",
    }
    normalized = aliases.get(value, value)
    if normalized not in {"two-sided", "greater", "less"}:
        raise ValueError("alternative must be one of two-sided, greater, less, increase, decrease")
    return normalized


def _resolve_p_value_method(variant_id: str, params: dict[str, Any]) -> str:
    if variant_id == "TWO_SAMPLE_KS_EXACT_PVALUE":
        return "exact"
    if variant_id == "TWO_SAMPLE_KS_ASYMPTOTIC_PVALUE":
        return "asymp"
    value = str(params.get("p_value_method", "auto"))
    aliases = {"asymptotic": "asymp"}
    value = aliases.get(value, value)
    if value not in {"auto", "exact", "asymp"}:
        raise ValueError("p_value_method must be one of auto, exact, asymp")
    return value


def _resolve_mann_whitney_method(variant_id: str, params: dict[str, Any]) -> str:
    if variant_id == "MANN_WHITNEY_EXACT":
        return "exact"
    value = str(params.get("p_value_method", "auto"))
    aliases = {"asymptotic": "asymptotic", "asymp": "asymptotic"}
    value = aliases.get(value, value)
    if value not in {"auto", "exact", "asymptotic"}:
        raise ValueError("p_value_method must be one of auto, exact, asymptotic")
    return value


def _validate_t_test_policy_params(variant_id: str, params: dict[str, Any]) -> None:
    if params.get("nan_policy", "omit") != "omit":
        raise ValueError("nan_policy must be 'omit' in the first t-test implementation")
    if params.get("multiple_testing_correction", "none") != "none":
        raise ValueError("multiple_testing_correction must be 'none' for single-call t-test")
    if "paired" in params and bool(params["paired"]) != (variant_id == "PAIRED_T_TEST"):
        raise ValueError("paired parameter conflicts with selected t-test variant")
    if "equal_var" in params:
        if variant_id == "TWO_SAMPLE_STUDENT_T_TEST" and bool(params["equal_var"]) is not True:
            raise ValueError("TWO_SAMPLE_STUDENT_T_TEST requires equal_var=True")
        if variant_id == "WELCH_T_TEST" and bool(params["equal_var"]) is not False:
            raise ValueError("WELCH_T_TEST requires equal_var=False")


def _resolve_levene_center(variant_id: str, params: dict[str, Any]) -> str:
    forced = {
        "LEVENE_MEAN_CENTER": "mean",
        "BROWN_FORSYTHE_MEDIAN_CENTER": "median",
        "TRIMMED_MEAN_LEVENE": "trimmed",
    }[variant_id]
    requested = params.get("center", forced)
    if requested != forced:
        raise ValueError(f"{variant_id} requires center={forced!r}")
    return forced


def _resolve_t_test_alternative(variant_id: str, params: dict[str, Any]) -> str:
    requested = params.get("direction_or_alternative", params.get("alternative", "two-sided"))
    value = str(requested)
    if value in {"both", "two_sided"}:
        return "two-sided"
    if value in {"greater", "less", "two-sided"}:
        return value
    if value in {"current_increase", "increase", "up"}:
        return "greater" if variant_id == "ONE_SAMPLE_T_TEST" else "less"
    if value in {"current_decrease", "decrease", "down"}:
        return "less" if variant_id == "ONE_SAMPLE_T_TEST" else "greater"
    raise ValueError("alternative must be two-sided, greater, less, increase, or decrease")


def _bool_param(value: Any, name: str) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str) and value.lower() in {"true", "false"}:
        return value.lower() == "true"
    raise ValueError(f"{name} must be boolean")


def _prepare_current_only_t_test_data(
    data: pd.DataFrame,
    *,
    time_col: str,
    value_col: str,
    current_window: tuple[str, str] | None,
) -> dict[str, Any]:
    if current_window is None:
        raise ValueError("current_window is required")
    if time_col not in data.columns:
        raise KeyError(f"missing time column: {time_col}")
    if value_col not in data.columns:
        raise KeyError(f"missing value column: {value_col}")
    from drift_algorithm.core.windows import _parse_window

    cur_start, cur_end = _parse_window(current_window, "current_window")
    frame = data[[time_col, value_col]].copy()
    frame[time_col] = pd.to_datetime(frame[time_col], errors="coerce")
    frame[value_col] = pd.to_numeric(frame[value_col], errors="coerce")
    invalid_time_rows = int(frame[time_col].isna().sum())
    invalid_value_rows = int((~np.isfinite(frame[value_col].to_numpy(dtype=float, na_value=np.nan))).sum())
    frame = frame.dropna(subset=[time_col, value_col])
    frame = frame[np.isfinite(frame[value_col].to_numpy(dtype=float))]
    current_frame = frame[(frame[time_col] >= cur_start) & (frame[time_col] <= cur_end)]
    warnings: list[str] = []
    if invalid_time_rows:
        warnings.append(f"dropped {invalid_time_rows} rows with invalid timestamps")
    if invalid_value_rows:
        warnings.append(f"dropped {invalid_value_rows} rows with non-finite numeric values")
    return {
        "reference_values": None,
        "current_values": current_frame[value_col].to_numpy(dtype=float),
        "metadata": {
            "current_window": [cur_start.isoformat(), cur_end.isoformat()],
            "current_effective_count": int(len(current_frame)),
            "dropped_current": invalid_value_rows,
        },
        "warnings": warnings,
        "paired": False,
    }


def _prepare_paired_t_test_data(
    data: pd.DataFrame,
    *,
    time_col: str,
    value_col: str,
    reference_window: tuple[str, str] | None,
    current_window: tuple[str, str] | None,
    pair_col: str | None,
) -> dict[str, Any]:
    if not pair_col:
        raise ValueError("PAIRED_T_TEST requires params['pair_col']")
    for column in (time_col, value_col, pair_col):
        if column not in data.columns:
            raise KeyError(f"missing column: {column}")
    from drift_algorithm.core.windows import _parse_window

    ref_start, ref_end = _parse_window(reference_window, "reference_window") if reference_window else (_raise_missing_window("reference_window"))
    cur_start, cur_end = _parse_window(current_window, "current_window") if current_window else (_raise_missing_window("current_window"))
    frame = data[[time_col, value_col, pair_col]].copy()
    frame[time_col] = pd.to_datetime(frame[time_col], errors="coerce")
    frame[value_col] = pd.to_numeric(frame[value_col], errors="coerce")
    frame = frame.dropna(subset=[time_col, value_col, pair_col])
    frame = frame[np.isfinite(frame[value_col].to_numpy(dtype=float))]
    ref = frame[(frame[time_col] >= ref_start) & (frame[time_col] <= ref_end)].copy()
    cur = frame[(frame[time_col] >= cur_start) & (frame[time_col] <= cur_end)].copy()
    if ref[pair_col].duplicated().any() or cur[pair_col].duplicated().any():
        raise ValueError("duplicate pair keys are not supported")
    merged = ref[[pair_col, value_col]].merge(
        cur[[pair_col, value_col]],
        on=pair_col,
        how="inner",
        suffixes=("_reference", "_current"),
    ).sort_values(pair_col)
    if merged.empty:
        raise ValueError("no overlapping pair keys between reference and current windows")
    return {
        "reference_values": merged[f"{value_col}_reference"].to_numpy(dtype=float),
        "current_values": merged[f"{value_col}_current"].to_numpy(dtype=float),
        "metadata": {
            "reference_window": [ref_start.isoformat(), ref_end.isoformat()],
            "current_window": [cur_start.isoformat(), cur_end.isoformat()],
            "pair_col": pair_col,
            "paired_count": int(len(merged)),
            "dropped_unpaired": int((len(ref) + len(cur)) - 2 * len(merged)),
            "dropped_reference": int(len(ref) - len(merged)),
            "dropped_current": int(len(cur) - len(merged)),
        },
        "warnings": [],
        "paired": True,
    }


def _raise_missing_window(name: str) -> None:
    raise ValueError(f"{name} is required")


def _positive_int(value: Any, name: str) -> int:
    parsed = int(value)
    if parsed <= 0:
        raise ValueError(f"{name} must be a positive integer")
    return parsed


def _resolve_value_col(value_col: str | None, params: dict[str, Any]) -> str:
    if value_col is not None:
        return value_col
    input_signal = params.get("input_signal")
    if not input_signal:
        raise ValueError("value_col is None and params['input_signal'] is not supplied")
    return str(input_signal)


def _tie_metadata(reference_values: np.ndarray, current_values: np.ndarray) -> dict[str, Any]:
    combined = np.concatenate([reference_values, current_values])
    reference_unique_ratio = float(len(np.unique(reference_values)) / len(reference_values))
    current_unique_ratio = float(len(np.unique(current_values)) / len(current_values))
    combined_unique_ratio = float(len(np.unique(combined)) / len(combined))
    return {
        "reference_unique_ratio": reference_unique_ratio,
        "current_unique_ratio": current_unique_ratio,
        "combined_unique_ratio": combined_unique_ratio,
        "reference_has_ties": reference_unique_ratio < 1.0,
        "current_has_ties": current_unique_ratio < 1.0,
    }


def _base_measurements(
    reference_values: np.ndarray,
    current_values: np.ndarray,
    ks_statistic: float | None,
    p_value: float | None,
) -> dict[str, Any]:
    measurements: dict[str, Any] = {
        "SAMPLE_SIZE": {"reference": int(len(reference_values)), "current": int(len(current_values))},
        "SAMPLE_SIZE_REFERENCE": int(len(reference_values)),
        "SAMPLE_SIZE_CURRENT": int(len(current_values)),
        "WINDOW_SIZE": {"reference": int(len(reference_values)), "current": int(len(current_values))},
    }
    if ks_statistic is not None:
        measurements["KS_STATISTIC"] = ks_statistic
        measurements["TEST_STATISTIC"] = ks_statistic
    if p_value is not None:
        measurements["P_VALUE"] = p_value
    return measurements


def _interpretation(
    *,
    variant_id: str,
    reference_count: int,
    current_count: int,
    ks_statistic: float,
    p_value: float,
    alpha: float,
    drift_detected: bool,
    warnings: list[str],
) -> str:
    decision = "drift candidate" if drift_detected else "normal"
    caution = " Tie/discrete-data caution is present." if _has_tie_caution(warnings) else ""
    return (
        f"{variant_id} compared {reference_count} reference rows and {current_count} current rows. "
        f"KS statistic={ks_statistic:.6g}, p-value={p_value:.6g}, alpha={alpha:.6g}; "
        f"decision={decision}.{caution}"
    )


def _has_tie_caution(warnings: list[str]) -> bool:
    return any("ties" in warning or "unique-value" in warning or "discrete" in warning for warning in warnings)


def _has_ties(reference_values: np.ndarray, current_values: np.ndarray) -> bool:
    pooled = np.concatenate([reference_values, current_values])
    return len(np.unique(pooled)) < len(pooled)


def _variance_ratio(ref_var: float, cur_var: float) -> float | None:
    smaller = min(ref_var, cur_var)
    larger = max(ref_var, cur_var)
    if smaller <= 0:
        return None
    return float(larger / smaller)


def _center_value(values: np.ndarray, center: str, proportiontocut: float) -> float:
    if center == "mean":
        return float(np.mean(values))
    if center == "median":
        return float(np.median(values))
    sorted_values = np.sort(values)
    cut = int(len(sorted_values) * proportiontocut)
    if cut:
        sorted_values = sorted_values[cut:-cut]
    return float(np.mean(sorted_values))


def _levene_interpretation(
    *,
    variant_id: str,
    center: str,
    test_statistic: float,
    p_value: float,
    alpha: float,
    ref_var: float,
    cur_var: float,
    drift_detected: bool,
    warnings: list[str],
) -> str:
    decision = "numeric variance/scale drift candidate" if drift_detected else "normal"
    suffix = " Warnings are present." if warnings else ""
    return (
        f"{variant_id} ran with center={center}. Levene statistic={test_statistic:.6g}, "
        f"p-value={p_value:.6g}, alpha={alpha:.6g}; reference_variance={ref_var:.6g}, "
        f"current_variance={cur_var:.6g}; decision={decision}.{suffix}"
    )


def _run_t_test_variant(
    *,
    variant_id: str,
    reference_values: np.ndarray | None,
    current_values: np.ndarray,
    params: dict[str, Any],
    alternative: str,
    metadata: dict[str, Any],
    warnings: list[str],
    min_reference_size: int,
) -> tuple[float, float, float | None]:
    if variant_id == "ONE_SAMPLE_T_TEST":
        if params.get("baseline_mean") is not None:
            baseline_mean = float(params["baseline_mean"])
        elif params.get("allow_reference_mean_as_baseline", True) and reference_values is not None:
            if len(reference_values) < min_reference_size:
                raise ValueError("reference sample is too small to use as one-sample baseline")
            baseline_mean = float(np.mean(reference_values))
            warnings.append("reference window mean used as fixed one-sample baseline; reference uncertainty is not modeled")
        else:
            raise ValueError("ONE_SAMPLE_T_TEST requires baseline_mean or reference mean fallback")
        stat = ttest_1samp(current_values, popmean=baseline_mean, alternative=alternative)
        metadata["baseline_source"] = "param" if params.get("baseline_mean") is not None else "reference_window_mean"
        return float(stat.statistic), float(stat.pvalue), baseline_mean
    if variant_id == "TWO_SAMPLE_STUDENT_T_TEST":
        if reference_values is None:
            raise ValueError("reference_window is required")
        stat = ttest_ind(reference_values, current_values, equal_var=True, alternative=alternative)
        metadata["equal_var"] = True
        return float(stat.statistic), float(stat.pvalue), None
    if variant_id == "WELCH_T_TEST":
        if reference_values is None:
            raise ValueError("reference_window is required")
        stat = ttest_ind(reference_values, current_values, equal_var=False, alternative=alternative)
        metadata["equal_var"] = False
        return float(stat.statistic), float(stat.pvalue), None
    if reference_values is None:
        raise ValueError("paired reference/current arrays are required")
    stat = ttest_rel(reference_values, current_values, alternative=alternative)
    metadata["paired"] = True
    return float(stat.statistic), float(stat.pvalue), None


def _add_t_test_warnings(
    reference_values: np.ndarray,
    current_values: np.ndarray,
    variant_id: str,
    variance_ratio_warning_threshold: float,
    sample_imbalance_warning_ratio: float,
    warnings: list[str],
) -> None:
    if len(reference_values) >= 2 and len(current_values) >= 2:
        ref_var = float(np.var(reference_values, ddof=1))
        cur_var = float(np.var(current_values, ddof=1))
        smaller = min(ref_var, cur_var)
        larger = max(ref_var, cur_var)
        if smaller > 0 and larger / smaller > variance_ratio_warning_threshold:
            warnings.append("reference/current variance ratio is high; Student t-test equal-variance assumption may be weak")
        if min(len(reference_values), len(current_values)) > 0:
            ratio = max(len(reference_values), len(current_values)) / min(len(reference_values), len(current_values))
            if ratio > sample_imbalance_warning_ratio:
                warnings.append("reference/current sample sizes are highly imbalanced")
    if min(len(reference_values), len(current_values)) < 10:
        warnings.append("small sample size may weaken t-test power and normality approximation")
    if variant_id == "PAIRED_T_TEST" and np.nanstd(reference_values - current_values) == 0:
        warnings.append("paired differences have zero variance; t-test result may be degenerate")


def _t_test_interpretation(
    *,
    variant_id: str,
    alternative: str,
    t_statistic: float,
    p_value: float,
    alpha: float,
    current_mean: float,
    reference_or_baseline_mean: float | None,
    drift_detected: bool,
    warnings: list[str],
) -> str:
    decision = "numeric mean drift candidate" if drift_detected else "normal"
    baseline = "not available" if reference_or_baseline_mean is None else f"{reference_or_baseline_mean:.6g}"
    suffix = " Warnings are present." if warnings else ""
    return (
        f"{variant_id} ran with alternative={alternative}. t statistic={t_statistic:.6g}, "
        f"p-value={p_value:.6g}, alpha={alpha:.6g}; current_mean={current_mean:.6g}, "
        f"reference_or_baseline_mean={baseline}; decision={decision}.{suffix}"
    )


def _mann_whitney_interpretation(
    *,
    variant_id: str,
    alternative: str,
    reference_count: int,
    current_count: int,
    u_statistic: float,
    p_value: float,
    alpha: float,
    drift_detected: bool,
    warnings: list[str],
) -> str:
    decision = "rank/location drift candidate" if drift_detected else "normal"
    suffix = " Warnings are present." if warnings else ""
    return (
        f"{variant_id} compared {reference_count} reference rows and {current_count} current rows "
        f"with alternative={alternative}. U statistic={u_statistic:.6g}, "
        f"p-value={p_value:.6g}, alpha={alpha:.6g}; decision={decision}.{suffix}"
    )


def _not_applicable(
    variant_id: str | None,
    warning: str,
    metadata: dict[str, Any] | None = None,
    prior_warnings: list[str] | None = None,
) -> DriftResult:
    result = not_applicable_result(
        method_id=METHOD_ID,
        method_name=METHOD_NAME,
        method_category=METHOD_CATEGORY,
        variant_id=variant_id,
        warning=warning,
        metadata=metadata,
    )
    if prior_warnings:
        result.warnings = prior_warnings + result.warnings
    return result


def _resolve_wasserstein_threshold(params: dict[str, Any]) -> tuple[float | None, str | None]:
    warning = None
    value = params.get("threshold")
    if "threshold_or_alpha" in params:
        value = params["threshold_or_alpha"]
        warning = "threshold_or_alpha was interpreted as a distance threshold, not a p-value alpha"
    if value is None:
        return None, warning
    threshold = float(value)
    if not np.isfinite(threshold) or threshold < 0:
        raise ValueError("threshold must be a finite number >= 0")
    return threshold, warning


def _validate_wasserstein_policy_params(params: dict[str, Any], variant_id: str) -> None:
    if params.get("distance_order", 1) != 1:
        raise ValueError(f"distance_order must be 1 for {variant_id}")
    binning_policy = _wasserstein_binning_policy(params, variant_id)
    expected = {
        "normalization_policy": "none",
        "outlier_policy": "keep",
        "nan_policy": "drop",
    }
    for key, allowed in expected.items():
        if params.get(key, allowed) != allowed:
            raise ValueError(f"{key} must be {allowed!r} for {variant_id}")
    if params.get("exact_method", "scipy") != "scipy":
        raise ValueError(f"exact_method must be 'scipy' for {variant_id}")
    if variant_id in {"WASSERSTEIN_1D_EXACT", "WASSERSTEIN_WINDOW_TREND", "SLICED_WASSERSTEIN_EMBEDDING"} and binning_policy != "none":
        raise ValueError(f"binning_policy must be 'none' for {variant_id}")
    if variant_id == "WASSERSTEIN_APPROX_HISTOGRAM" and binning_policy != "equal_width":
        raise ValueError("binning_policy must be 'equal_width' for WASSERSTEIN_APPROX_HISTOGRAM")


def _wasserstein_binning_policy(params: dict[str, Any], variant_id: str) -> str:
    if "binning_policy" in params:
        return str(params["binning_policy"])
    if variant_id == "WASSERSTEIN_APPROX_HISTOGRAM":
        return "equal_width"
    return "none"


def _wasserstein_distance_by_variant(
    *,
    variant_id: str,
    params: dict[str, Any],
    reference_values: np.ndarray,
    current_values: np.ndarray,
    reference_weights: np.ndarray | None,
    current_weights: np.ndarray | None,
) -> dict[str, Any]:
    try:
        if variant_id == "WASSERSTEIN_APPROX_HISTOGRAM":
            return _wasserstein_approx_histogram_distance(params, reference_values, current_values)
        distance = float(
            wasserstein_distance(
                reference_values,
                current_values,
                u_weights=reference_weights,
                v_weights=current_weights,
            )
        )
    except Exception as exc:
        return {"status": "failed", "reason": f"wasserstein_distance failed: {exc}"}
    metadata: dict[str, Any] = {}
    warnings: list[str] = []
    if variant_id == "SLICED_WASSERSTEIN_EMBEDDING":
        metadata = {
            "projection_policy": str(params.get("projection_policy", "single_projected_numeric_stream")),
            "projection_count": int(params.get("projection_count", 1)),
        }
        warnings.append("SLICED_WASSERSTEIN_EMBEDDING used a single projected numeric stream in this finite replay")
    return {"status": "success", "distance": distance, "warnings": warnings, "metadata": metadata}


def _wasserstein_approx_histogram_distance(
    params: dict[str, Any],
    reference_values: np.ndarray,
    current_values: np.ndarray,
) -> dict[str, Any]:
    try:
        bin_count = _positive_int(params.get("bin_count", 20), "bin_count")
    except (TypeError, ValueError) as exc:
        return {"status": "failed", "reason": str(exc)}
    if bin_count < 2:
        return {"status": "failed", "reason": "bin_count must be at least 2"}
    combined = np.concatenate([reference_values, current_values])
    minimum = float(np.min(combined))
    maximum = float(np.max(combined))
    if not np.isfinite(minimum) or not np.isfinite(maximum):
        return {"status": "failed", "reason": "histogram range is not finite"}
    if minimum == maximum:
        return {
            "status": "success",
            "distance": 0.0,
            "warnings": ["all values share one histogram location; approximate Wasserstein distance is zero"],
            "metadata": {
                "binning_policy": "equal_width",
                "histogram_bin_count": bin_count,
                "histogram_range": [minimum, maximum],
            },
        }
    edges = np.linspace(minimum, maximum, bin_count + 1)
    centers = (edges[:-1] + edges[1:]) / 2.0
    reference_counts, _ = np.histogram(reference_values, bins=edges)
    current_counts, _ = np.histogram(current_values, bins=edges)
    if reference_counts.sum() <= 0 or current_counts.sum() <= 0:
        return {"status": "failed", "reason": "histogram counts are empty"}
    try:
        distance = float(
            wasserstein_distance(
                centers,
                centers,
                u_weights=reference_counts.astype(float),
                v_weights=current_counts.astype(float),
            )
        )
    except Exception as exc:
        return {"status": "failed", "reason": f"histogram wasserstein_distance failed: {exc}"}
    return {
        "status": "success",
        "distance": distance,
        "warnings": ["WASSERSTEIN_APPROX_HISTOGRAM uses equal-width histogram bin centers, not sample-level exact distance"],
        "metadata": {
            "binning_policy": "equal_width",
            "histogram_bin_count": bin_count,
            "histogram_range": [minimum, maximum],
        },
    }


def _prepare_wasserstein_windows(
    data: pd.DataFrame,
    *,
    time_col: str,
    value_col: str,
    reference_window: tuple[str, str] | None,
    current_window: tuple[str, str] | None,
    reference_weight_col: str | None,
    current_weight_col: str | None,
) -> dict[str, Any]:
    if reference_window is None or current_window is None:
        raise ValueError("reference_window and current_window are required")
    if time_col not in data.columns:
        raise KeyError(f"missing time column: {time_col}")
    if value_col not in data.columns:
        raise KeyError(f"missing value column: {value_col}")

    required_columns = [time_col, value_col]
    for column in (reference_weight_col, current_weight_col):
        if column:
            if column not in data.columns:
                raise KeyError(f"missing weight column: {column}")
            required_columns.append(column)

    from drift_algorithm.core.windows import _parse_window

    ref_start, ref_end = _parse_window(reference_window, "reference_window")
    cur_start, cur_end = _parse_window(current_window, "current_window")
    if max(ref_start, cur_start) <= min(ref_end, cur_end):
        raise ValueError("reference_window and current_window must not overlap")

    frame = data[list(dict.fromkeys(required_columns))].copy()
    original_rows = len(frame)
    frame[time_col] = pd.to_datetime(frame[time_col], errors="coerce")
    frame[value_col] = pd.to_numeric(frame[value_col], errors="coerce")
    for column in (reference_weight_col, current_weight_col):
        if column:
            frame[column] = pd.to_numeric(frame[column], errors="coerce")

    invalid_time_rows = int(frame[time_col].isna().sum())
    invalid_value_rows = int((~np.isfinite(frame[value_col].to_numpy(dtype=float, na_value=np.nan))).sum())
    frame = frame.dropna(subset=[time_col, value_col])
    frame = frame[np.isfinite(frame[value_col].to_numpy(dtype=float))]
    frame = frame.sort_values(time_col)

    reference_frame = frame[(frame[time_col] >= ref_start) & (frame[time_col] <= ref_end)].copy()
    current_frame = frame[(frame[time_col] >= cur_start) & (frame[time_col] <= cur_end)].copy()
    reference_values, reference_weights, reference_dropped_weights = _values_and_weights(
        reference_frame,
        value_col=value_col,
        weight_col=reference_weight_col,
        label="reference",
    )
    current_values, current_weights, current_dropped_weights = _values_and_weights(
        current_frame,
        value_col=value_col,
        weight_col=current_weight_col,
        label="current",
    )

    warnings: list[str] = []
    if invalid_time_rows:
        warnings.append(f"dropped {invalid_time_rows} rows with invalid timestamps")
    if invalid_value_rows:
        warnings.append(f"dropped {invalid_value_rows} rows with non-finite numeric values")
    if reference_dropped_weights:
        warnings.append(f"dropped {reference_dropped_weights} reference rows with invalid weights")
    if current_dropped_weights:
        warnings.append(f"dropped {current_dropped_weights} current rows with invalid weights")

    return {
        "reference_values": reference_values,
        "current_values": current_values,
        "reference_weights": reference_weights,
        "current_weights": current_weights,
        "metadata": {
            "original_rows": original_rows,
            "valid_rows": int(len(frame)),
            "invalid_time_rows": invalid_time_rows,
            "invalid_value_rows": invalid_value_rows,
            "reference_window": [ref_start.isoformat(), ref_end.isoformat()],
            "current_window": [cur_start.isoformat(), cur_end.isoformat()],
            "reference_effective_count": int(len(reference_values)),
            "current_effective_count": int(len(current_values)),
        },
        "warnings": warnings,
    }


def _values_and_weights(
    frame: pd.DataFrame,
    *,
    value_col: str,
    weight_col: str | None,
    label: str,
) -> tuple[np.ndarray, np.ndarray | None, int]:
    if weight_col is None:
        return frame[value_col].to_numpy(dtype=float), None, 0
    before = len(frame)
    weights = pd.to_numeric(frame[weight_col], errors="coerce")
    weight_values = weights.to_numpy(dtype=float, na_value=np.nan)
    valid = weights.notna() & np.isfinite(weight_values) & (weights >= 0)
    filtered = frame[valid].copy()
    filtered_weights = weights[valid].to_numpy(dtype=float)
    if len(filtered) and float(filtered_weights.sum()) <= 0:
        raise ValueError(f"{label} weights must have positive sum")
    return filtered[value_col].to_numpy(dtype=float), filtered_weights, before - len(filtered)


def _prepare_categorical_counts(
    data: pd.DataFrame,
    *,
    time_col: str,
    category_col: str,
    count_col: str | None,
    reference_window: tuple[str, str] | None,
    current_window: tuple[str, str] | None,
    min_reference_size: int,
    min_current_size: int,
) -> dict[str, Any]:
    if not isinstance(data, pd.DataFrame):
        raise TypeError("data must be a pandas DataFrame")
    required_cols = [time_col, category_col]
    if count_col is not None:
        count_col = str(count_col)
        required_cols.append(count_col)
    missing = [col for col in required_cols if col not in data.columns]
    if missing:
        raise KeyError(f"missing required columns: {missing}")
    if reference_window is None or current_window is None:
        raise ValueError("reference_window and current_window are required for categorical count comparisons")

    frame = data[required_cols].copy()
    frame[time_col] = pd.to_datetime(frame[time_col], errors="coerce")
    before_time_drop = len(frame)
    frame = frame.dropna(subset=[time_col, category_col])
    warnings: list[str] = []
    if len(frame) < before_time_drop:
        warnings.append(f"dropped {before_time_drop - len(frame)} rows with invalid time/category values")
    if count_col is None:
        frame["_count"] = 1.0
    else:
        frame["_count"] = pd.to_numeric(frame[count_col], errors="coerce")
        before_count_drop = len(frame)
        frame = frame.dropna(subset=["_count"])
        frame = frame[np.isfinite(frame["_count"]) & (frame["_count"] >= 0)]
        if len(frame) < before_count_drop:
            warnings.append(f"dropped {before_count_drop - len(frame)} rows with invalid count values")
    if frame.empty:
        raise ValueError("no valid categorical rows after cleaning")

    ref_start, ref_end = pd.to_datetime(reference_window[0]), pd.to_datetime(reference_window[1])
    cur_start, cur_end = pd.to_datetime(current_window[0]), pd.to_datetime(current_window[1])
    reference = frame[(frame[time_col] >= ref_start) & (frame[time_col] <= ref_end)]
    current = frame[(frame[time_col] >= cur_start) & (frame[time_col] <= cur_end)]
    if reference.empty or current.empty:
        raise ValueError("reference/current windows must contain categorical rows")

    ref_counts_series = reference.groupby(category_col)["_count"].sum()
    cur_counts_series = current.groupby(category_col)["_count"].sum()
    categories = sorted(set(ref_counts_series.index.astype(str)) | set(cur_counts_series.index.astype(str)))
    ref_counts = np.array([float(ref_counts_series.get(category, 0.0)) for category in categories], dtype=float)
    cur_counts = np.array([float(cur_counts_series.get(category, 0.0)) for category in categories], dtype=float)
    if float(np.sum(ref_counts)) < min_reference_size:
        raise ValueError(f"reference sample size {float(np.sum(ref_counts))} is below min_reference_size {min_reference_size}")
    if float(np.sum(cur_counts)) < min_current_size:
        raise ValueError(f"current sample size {float(np.sum(cur_counts))} is below min_current_size {min_current_size}")
    if np.sum(ref_counts) <= 0 or np.sum(cur_counts) <= 0:
        raise ValueError("reference and current count totals must be positive")
    if len(categories) < 2:
        raise ValueError("at least two categories are required")

    return {
        "reference_counts": ref_counts,
        "current_counts": cur_counts,
        "categories": categories,
        "warnings": warnings,
        "metadata": {
            "time_col": time_col,
            "category_col": category_col,
            "count_col": count_col,
            "reference_window": reference_window,
            "current_window": current_window,
        },
    }


def _expected_counts_from_reference(reference_counts: np.ndarray, current_total: float) -> np.ndarray:
    proportions = reference_counts / float(np.sum(reference_counts))
    expected = proportions * current_total
    if np.any(expected <= 0):
        raise ValueError("expected counts must be positive for Chi-square goodness-of-fit")
    scale = current_total / float(np.sum(expected))
    return expected * scale


def _chi_square_residuals(
    reference_counts: np.ndarray,
    current_counts: np.ndarray,
    expected_counts: np.ndarray,
    variant_id: str,
) -> dict[str, Any]:
    if variant_id == "CHI_SQUARE_GOODNESS_OF_FIT":
        expected = np.asarray(expected_counts, dtype=float)
        residuals = (current_counts - expected) / np.sqrt(np.maximum(expected, 1e-12))
        return {"current_vs_expected": residuals.astype(float).tolist()}
    expected = np.asarray(expected_counts, dtype=float)
    residuals = (np.vstack([reference_counts, current_counts]) - expected) / np.sqrt(np.maximum(expected, 1e-12))
    return {"reference": residuals[0].astype(float).tolist(), "current": residuals[1].astype(float).tolist()}


def _category_proportion_delta(categories: list[str], reference_counts: np.ndarray, current_counts: np.ndarray) -> dict[str, float]:
    ref_prop = reference_counts / float(np.sum(reference_counts))
    cur_prop = current_counts / float(np.sum(current_counts))
    return {category: float(cur_prop[idx] - ref_prop[idx]) for idx, category in enumerate(categories)}


def _fisher_extended_permutation_pvalue(table: np.ndarray, *, permutations: int, seed: int) -> tuple[float, float]:
    if table.ndim != 2 or table.shape[0] != 2 or table.shape[1] < 2:
        raise ValueError("extended Fisher surrogate requires a 2 x K contingency table")
    if np.any(table < 0) or not np.allclose(table, np.round(table)):
        raise ValueError("Fisher exact counts must be non-negative integers")
    ref_counts = table[0].astype(int)
    cur_counts = table[1].astype(int)
    labels = np.concatenate([np.zeros(int(np.sum(ref_counts)), dtype=int), np.ones(int(np.sum(cur_counts)), dtype=int)])
    categories = np.concatenate([np.repeat(idx, int(ref_counts[idx] + cur_counts[idx])) for idx in range(table.shape[1])])
    observed = _contingency_chi_square_statistic(table.astype(float))
    rng = np.random.default_rng(seed)
    exceed = 0
    for _ in range(permutations):
        shuffled = rng.permutation(labels)
        perm_table = np.zeros_like(table, dtype=float)
        for group in (0, 1):
            group_categories = categories[shuffled == group]
            if len(group_categories):
                perm_table[group] = np.bincount(group_categories, minlength=table.shape[1])
        if _contingency_chi_square_statistic(perm_table) >= observed - 1e-12:
            exceed += 1
    return observed, float((exceed + 1.0) / (permutations + 1.0))


def _contingency_chi_square_statistic(table: np.ndarray) -> float:
    row_sum = table.sum(axis=1, keepdims=True)
    col_sum = table.sum(axis=0, keepdims=True)
    total = float(table.sum())
    if total <= 0:
        raise ValueError("contingency table total must be positive")
    expected = row_sum @ col_sum / total
    valid = expected > 0
    return float(np.sum(((table[valid] - expected[valid]) ** 2) / expected[valid]))


def _numeric_psi_bins(reference_values: np.ndarray, current_values: np.ndarray, bin_count: int) -> tuple[list[str], np.ndarray, np.ndarray]:
    quantiles = np.linspace(0.0, 1.0, bin_count + 1)
    edges = np.quantile(reference_values, quantiles)
    edges = np.unique(edges)
    if len(edges) < 2:
        raise ValueError("numeric PSI requires at least two distinct reference values")
    edges[0] = -np.inf
    edges[-1] = np.inf
    ref_counts, _ = np.histogram(reference_values, bins=edges)
    cur_counts, _ = np.histogram(current_values, bins=edges)
    labels = [f"bin_{idx}" for idx in range(len(edges) - 1)]
    return labels, ref_counts.astype(float), cur_counts.astype(float)


def _psi_from_counts(
    categories: list[str],
    reference_counts: np.ndarray,
    current_counts: np.ndarray,
    epsilon: float,
) -> tuple[float, list[dict[str, float | str]]]:
    ref_prop = reference_counts / float(np.sum(reference_counts))
    cur_prop = current_counts / float(np.sum(current_counts))
    ref_adj = np.maximum(ref_prop, epsilon)
    cur_adj = np.maximum(cur_prop, epsilon)
    ref_adj = ref_adj / np.sum(ref_adj)
    cur_adj = cur_adj / np.sum(cur_adj)
    terms = (cur_adj - ref_adj) * np.log(cur_adj / ref_adj)
    contributions = [
        {
            "category": category,
            "reference_proportion": float(ref_prop[idx]),
            "current_proportion": float(cur_prop[idx]),
            "psi_contribution": float(terms[idx]),
        }
        for idx, category in enumerate(categories)
    ]
    return float(np.sum(terms)), sorted(contributions, key=lambda item: -float(item["psi_contribution"]))


def _kl_from_counts(
    categories: list[str],
    reference_counts: np.ndarray,
    current_counts: np.ndarray,
    epsilon: float,
    *,
    symmetrized: bool,
) -> dict[str, Any]:
    ref_prop = reference_counts / float(np.sum(reference_counts))
    cur_prop = current_counts / float(np.sum(current_counts))
    ref_adj = np.maximum(ref_prop, epsilon)
    cur_adj = np.maximum(cur_prop, epsilon)
    ref_adj = ref_adj / np.sum(ref_adj)
    cur_adj = cur_adj / np.sum(cur_adj)
    current_reference_terms = cur_adj * np.log(cur_adj / ref_adj)
    reference_current_terms = ref_adj * np.log(ref_adj / cur_adj)
    current_reference = float(np.sum(current_reference_terms))
    reference_current = float(np.sum(reference_current_terms))
    score = 0.5 * (current_reference + reference_current) if symmetrized else current_reference
    contributions = [
        {
            "category": category,
            "reference_proportion": float(ref_prop[idx]),
            "current_proportion": float(cur_prop[idx]),
            "kl_current_reference_contribution": float(current_reference_terms[idx]),
            "kl_reference_current_contribution": float(reference_current_terms[idx]),
        }
        for idx, category in enumerate(categories)
    ]
    return {
        "score": float(score),
        "current_reference": current_reference,
        "reference_current": reference_current,
        "contributions": sorted(contributions, key=lambda item: -abs(float(item["kl_current_reference_contribution"]))),
    }


def _js_from_counts(
    categories: list[str],
    reference_counts: np.ndarray,
    current_counts: np.ndarray,
    epsilon: float,
) -> dict[str, Any]:
    ref_prop = reference_counts / float(np.sum(reference_counts))
    cur_prop = current_counts / float(np.sum(current_counts))
    ref_adj = np.maximum(ref_prop, epsilon)
    cur_adj = np.maximum(cur_prop, epsilon)
    ref_adj = ref_adj / np.sum(ref_adj)
    cur_adj = cur_adj / np.sum(cur_adj)
    midpoint = 0.5 * (ref_adj + cur_adj)
    ref_terms = ref_adj * np.log2(ref_adj / midpoint)
    cur_terms = cur_adj * np.log2(cur_adj / midpoint)
    contribution_terms = 0.5 * (ref_terms + cur_terms)
    divergence = float(np.sum(contribution_terms))
    distance = float(np.sqrt(max(divergence, 0.0)))
    contributions = [
        {
            "category": category,
            "reference_proportion": float(ref_prop[idx]),
            "current_proportion": float(cur_prop[idx]),
            "proportion_delta": float(cur_prop[idx] - ref_prop[idx]),
            "js_contribution": float(contribution_terms[idx]),
        }
        for idx, category in enumerate(categories)
    ]
    return {
        "divergence": divergence,
        "distance": distance,
        "contributions": sorted(contributions, key=lambda item: -abs(float(item["proportion_delta"]))),
    }


def _hellinger_from_counts(
    categories: list[str],
    reference_counts: np.ndarray,
    current_counts: np.ndarray,
) -> dict[str, Any]:
    ref_prop = reference_counts / float(np.sum(reference_counts))
    cur_prop = current_counts / float(np.sum(current_counts))
    terms = 0.5 * (np.sqrt(ref_prop) - np.sqrt(cur_prop)) ** 2
    distance = float(np.sqrt(np.sum(terms)))
    contributions = [
        {
            "category": category,
            "reference_proportion": float(ref_prop[idx]),
            "current_proportion": float(cur_prop[idx]),
            "proportion_delta": float(cur_prop[idx] - ref_prop[idx]),
            "hellinger_contribution": float(terms[idx]),
        }
        for idx, category in enumerate(categories)
    ]
    return {
        "distance": distance,
        "contributions": sorted(contributions, key=lambda item: -float(item["hellinger_contribution"])),
    }


def _total_variation_from_counts(
    categories: list[str],
    reference_counts: np.ndarray,
    current_counts: np.ndarray,
) -> dict[str, Any]:
    ref_prop = reference_counts / float(np.sum(reference_counts))
    cur_prop = current_counts / float(np.sum(current_counts))
    abs_delta = np.abs(cur_prop - ref_prop)
    contribution_terms = 0.5 * abs_delta
    distance = float(np.sum(contribution_terms))
    contributions = [
        {
            "category": category,
            "reference_proportion": float(ref_prop[idx]),
            "current_proportion": float(cur_prop[idx]),
            "proportion_delta": float(cur_prop[idx] - ref_prop[idx]),
            "total_variation_contribution": float(contribution_terms[idx]),
        }
        for idx, category in enumerate(categories)
    ]
    return {
        "distance": distance,
        "contributions": sorted(contributions, key=lambda item: -float(item["total_variation_contribution"])),
    }


def _l_infinity_from_counts(
    categories: list[str],
    reference_counts: np.ndarray,
    current_counts: np.ndarray,
) -> dict[str, Any]:
    ref_prop = reference_counts / float(np.sum(reference_counts))
    cur_prop = current_counts / float(np.sum(current_counts))
    delta = cur_prop - ref_prop
    abs_delta = np.abs(delta)
    max_idx = int(np.argmax(abs_delta))
    distance = float(abs_delta[max_idx])
    contributions = [
        {
            "category": category,
            "reference_proportion": float(ref_prop[idx]),
            "current_proportion": float(cur_prop[idx]),
            "proportion_delta": float(delta[idx]),
            "absolute_proportion_delta": float(abs_delta[idx]),
            "is_max_component": bool(idx == max_idx),
        }
        for idx, category in enumerate(categories)
    ]
    return {
        "distance": distance,
        "max_component": {
            "category": categories[max_idx],
            "reference_proportion": float(ref_prop[max_idx]),
            "current_proportion": float(cur_prop[max_idx]),
            "proportion_delta": float(delta[max_idx]),
            "absolute_proportion_delta": distance,
        },
        "contributions": sorted(contributions, key=lambda item: -float(item["absolute_proportion_delta"])),
    }


def _bhattacharyya_from_counts(
    categories: list[str],
    reference_counts: np.ndarray,
    current_counts: np.ndarray,
) -> dict[str, Any]:
    ref_prop = reference_counts / float(np.sum(reference_counts))
    cur_prop = current_counts / float(np.sum(current_counts))
    coefficient_terms = np.sqrt(ref_prop * cur_prop)
    coefficient = float(np.sum(coefficient_terms))
    coefficient = min(max(coefficient, 0.0), 1.0)
    distance = float(-np.log(max(coefficient, 1e-300)))
    contributions = [
        {
            "category": category,
            "reference_proportion": float(ref_prop[idx]),
            "current_proportion": float(cur_prop[idx]),
            "proportion_delta": float(cur_prop[idx] - ref_prop[idx]),
            "bhattacharyya_coefficient_component": float(coefficient_terms[idx]),
        }
        for idx, category in enumerate(categories)
    ]
    return {
        "distance": distance,
        "coefficient": coefficient,
        "contributions": sorted(contributions, key=lambda item: -abs(float(item["proportion_delta"]))),
    }


def _gaussian_bhattacharyya_from_values(reference_values: np.ndarray, current_values: np.ndarray) -> dict[str, Any]:
    ref_mean = float(np.mean(reference_values))
    cur_mean = float(np.mean(current_values))
    ref_variance = float(np.var(reference_values, ddof=1))
    cur_variance = float(np.var(current_values, ddof=1))
    if ref_variance <= 0 or cur_variance <= 0:
        raise ValueError("Gaussian Bhattacharyya distance requires positive reference and current variance")
    variance_sum = ref_variance + cur_variance
    mean_term = 0.25 * ((ref_mean - cur_mean) ** 2 / variance_sum)
    variance_term = 0.25 * np.log(0.25 * (ref_variance / cur_variance + cur_variance / ref_variance + 2.0))
    distance = float(mean_term + variance_term)
    coefficient = float(np.exp(-distance))
    return {
        "distance": distance,
        "coefficient": coefficient,
        "reference_sample_size": int(len(reference_values)),
        "current_sample_size": int(len(current_values)),
        "gaussian_summary": {
            "reference_mean": ref_mean,
            "current_mean": cur_mean,
            "reference_variance": ref_variance,
            "current_variance": cur_variance,
            "mean_term": float(mean_term),
            "variance_term": float(variance_term),
        },
    }


def _hinc_from_counts(
    categories: list[str],
    reference_counts: np.ndarray,
    current_counts: np.ndarray,
) -> dict[str, Any]:
    ref_prop = reference_counts / float(np.sum(reference_counts))
    cur_prop = current_counts / float(np.sum(current_counts))
    overlap_terms = np.minimum(ref_prop, cur_prop)
    intersection = float(np.sum(overlap_terms))
    score = float(1.0 - intersection)
    complement_terms = 1.0 - overlap_terms
    contributions = [
        {
            "category": category,
            "reference_proportion": float(ref_prop[idx]),
            "current_proportion": float(cur_prop[idx]),
            "proportion_delta": float(cur_prop[idx] - ref_prop[idx]),
            "intersection_component": float(overlap_terms[idx]),
            "complement_component": float(complement_terms[idx]),
        }
        for idx, category in enumerate(categories)
    ]
    return {
        "score": score,
        "intersection": intersection,
        "contributions": sorted(contributions, key=lambda item: -abs(float(item["proportion_delta"]))),
    }


def _chi_square_interpretation(
    *,
    variant_id: str,
    statistic: float,
    p_value: float,
    alpha: float,
    category_count: int,
    alarm_state: str,
    low_expected_count: int,
) -> str:
    return (
        f"{variant_id} compared categorical count distributions across {category_count} categories. "
        f"Chi-square statistic={statistic:.6g}, p_value={p_value:.6g}, alpha={alpha:.6g}, "
        f"low_expected_count={low_expected_count}. Alarm state is {alarm_state}."
    )


def _psi_interpretation(
    *,
    variant_id: str,
    psi_score: float,
    threshold: float,
    category_count: int,
    alarm_state: str,
) -> str:
    return (
        f"{variant_id} computed PSI across {category_count} bins/categories. "
        f"PSI={psi_score:.6g}, threshold={threshold:.6g}. Alarm state is {alarm_state}. "
        "No p-value is produced by this implementation."
    )


def _kl_interpretation(
    *,
    variant_id: str,
    kl_score: float,
    threshold: float,
    category_count: int,
    alarm_state: str,
) -> str:
    return (
        f"{variant_id} computed KL divergence across {category_count} bins/categories. "
        f"KL={kl_score:.6g}, threshold={threshold:.6g}. Alarm state is {alarm_state}. "
        "No p-value is produced by this implementation."
    )


def _js_interpretation(
    *,
    variant_id: str,
    js_score: float,
    threshold: float,
    category_count: int,
    alarm_state: str,
    score_name: str,
) -> str:
    return (
        f"{variant_id} computed Jensen-Shannon {score_name} across {category_count} bins/categories. "
        f"JS {score_name}={js_score:.6g}, threshold={threshold:.6g}. Alarm state is {alarm_state}. "
        "No p-value is produced by this implementation."
    )


def _hellinger_interpretation(
    *,
    variant_id: str,
    distance: float,
    threshold: float,
    category_count: int,
    alarm_state: str,
) -> str:
    return (
        f"{variant_id} computed Hellinger distance across {category_count} bins/categories. "
        f"Hellinger distance={distance:.6g}, threshold={threshold:.6g}. Alarm state is {alarm_state}. "
        "No p-value is produced by this implementation."
    )


def _total_variation_interpretation(
    *,
    variant_id: str,
    distance: float,
    threshold: float,
    category_count: int,
    alarm_state: str,
) -> str:
    return (
        f"{variant_id} computed total variation distance across {category_count} bins/categories. "
        f"Total variation distance={distance:.6g}, threshold={threshold:.6g}. Alarm state is {alarm_state}. "
        "No p-value is produced by this implementation."
    )


def _l_infinity_interpretation(
    *,
    variant_id: str,
    distance: float,
    max_component: dict[str, Any],
    threshold: float,
    category_count: int,
    alarm_state: str,
) -> str:
    return (
        f"{variant_id} computed L-infinity distance across {category_count} bins/categories. "
        f"L-infinity distance={distance:.6g}, max_component={max_component['category']}, "
        f"threshold={threshold:.6g}. Alarm state is {alarm_state}. "
        "No p-value is produced by this implementation."
    )


def _bhattacharyya_interpretation(
    *,
    variant_id: str,
    distance: float,
    coefficient: float | None,
    threshold: float,
    alarm_state: str,
) -> str:
    coefficient_text = "not_applicable" if coefficient is None else f"{coefficient:.6g}"
    return (
        f"{variant_id} computed Bhattacharyya distance. "
        f"Distance={distance:.6g}, coefficient={coefficient_text}, threshold={threshold:.6g}. "
        f"Alarm state is {alarm_state}. No p-value is produced by this implementation."
    )


def _hinc_interpretation(
    *,
    variant_id: str,
    score: float,
    intersection: float,
    threshold: float,
    category_count: int,
    alarm_state: str,
) -> str:
    return (
        f"{variant_id} computed histogram intersection normalized complement across {category_count} bins/categories. "
        f"HINC score={score:.6g}, intersection={intersection:.6g}, threshold={threshold:.6g}. "
        f"Alarm state is {alarm_state}. No p-value is produced by this implementation."
    )


def _fisher_interpretation(
    *,
    variant_id: str,
    statistic: float,
    p_value: float,
    alpha: float,
    category_count: int,
    alarm_state: str,
    method_policy: str,
) -> str:
    return (
        f"{variant_id} compared categorical contingency counts across {category_count} categories. "
        f"Statistic={statistic:.6g}, p_value={p_value:.6g}, alpha={alpha:.6g}, "
        f"policy={method_policy}. Alarm state is {alarm_state}."
    )


def _g_test_interpretation(
    *,
    variant_id: str,
    statistic: float,
    p_value: float,
    alpha: float,
    category_count: int,
    alarm_state: str,
    small_expected_count: int,
) -> str:
    return (
        f"{variant_id} compared categorical count distributions across {category_count} categories. "
        f"G statistic={statistic:.6g}, p_value={p_value:.6g}, alpha={alpha:.6g}, "
        f"small_expected_count={small_expected_count}. Alarm state is {alarm_state}."
    )


def _wasserstein_interpretation(
    *,
    variant_id: str,
    reference_count: int,
    current_count: int,
    distance: float,
    threshold: float | None,
    alarm_state: str,
    warnings: list[str],
) -> str:
    threshold_text = "no threshold supplied" if threshold is None else f"threshold={threshold:.6g}"
    suffix = " Warnings are present." if warnings else ""
    return (
        f"{variant_id} compared {reference_count} reference rows and {current_count} current rows. "
        f"Wasserstein distance={distance:.6g}; {threshold_text}; alarm_state={alarm_state}. "
        f"No p-value is produced by this implementation.{suffix}"
    )


def _chi_square_not_applicable(
    variant_id: str | None,
    warning: str,
    metadata: dict[str, Any] | None = None,
    prior_warnings: list[str] | None = None,
) -> DriftResult:
    result = not_applicable_result(
        method_id=CHI_SQUARE_METHOD_ID,
        method_name=CHI_SQUARE_METHOD_NAME,
        method_category=METHOD_CATEGORY,
        variant_id=variant_id,
        warning=warning,
        metadata=metadata,
    )
    if prior_warnings:
        result.warnings = prior_warnings + result.warnings
    return result


def _fisher_not_applicable(
    variant_id: str | None,
    warning: str,
    metadata: dict[str, Any] | None = None,
    prior_warnings: list[str] | None = None,
) -> DriftResult:
    result = not_applicable_result(
        method_id=FISHER_METHOD_ID,
        method_name=FISHER_METHOD_NAME,
        method_category=METHOD_CATEGORY,
        variant_id=variant_id,
        warning=warning,
        metadata=metadata,
    )
    if prior_warnings:
        result.warnings = prior_warnings + result.warnings
    return result


def _g_test_not_applicable(
    variant_id: str | None,
    warning: str,
    metadata: dict[str, Any] | None = None,
    prior_warnings: list[str] | None = None,
) -> DriftResult:
    result = not_applicable_result(
        method_id=G_TEST_METHOD_ID,
        method_name=G_TEST_METHOD_NAME,
        method_category=METHOD_CATEGORY,
        variant_id=variant_id,
        warning=warning,
        metadata=metadata,
    )
    if prior_warnings:
        result.warnings = prior_warnings + result.warnings
    return result


def _psi_not_applicable(
    variant_id: str | None,
    warning: str,
    metadata: dict[str, Any] | None = None,
    prior_warnings: list[str] | None = None,
) -> DriftResult:
    result = not_applicable_result(
        method_id=PSI_METHOD_ID,
        method_name=PSI_METHOD_NAME,
        method_category=METHOD_CATEGORY,
        variant_id=variant_id,
        warning=warning,
        metadata=metadata,
    )
    if prior_warnings:
        result.warnings = prior_warnings + result.warnings
    return result


def _kl_not_applicable(
    variant_id: str | None,
    warning: str,
    metadata: dict[str, Any] | None = None,
    prior_warnings: list[str] | None = None,
) -> DriftResult:
    result = not_applicable_result(
        method_id=KL_METHOD_ID,
        method_name=KL_METHOD_NAME,
        method_category=METHOD_CATEGORY,
        variant_id=variant_id,
        warning=warning,
        metadata=metadata,
    )
    if prior_warnings:
        result.warnings = prior_warnings + result.warnings
    return result


def _js_not_applicable(
    variant_id: str | None,
    warning: str,
    metadata: dict[str, Any] | None = None,
    prior_warnings: list[str] | None = None,
) -> DriftResult:
    result = not_applicable_result(
        method_id=JS_METHOD_ID,
        method_name=JS_METHOD_NAME,
        method_category=METHOD_CATEGORY,
        variant_id=variant_id,
        warning=warning,
        metadata=metadata,
    )
    if prior_warnings:
        result.warnings = prior_warnings + result.warnings
    return result


def _hellinger_not_applicable(
    variant_id: str | None,
    warning: str,
    metadata: dict[str, Any] | None = None,
    prior_warnings: list[str] | None = None,
) -> DriftResult:
    result = not_applicable_result(
        method_id=HELLINGER_METHOD_ID,
        method_name=HELLINGER_METHOD_NAME,
        method_category=METHOD_CATEGORY,
        variant_id=variant_id,
        warning=warning,
        metadata=metadata,
    )
    if prior_warnings:
        result.warnings = prior_warnings + result.warnings
    return result


def _total_variation_not_applicable(
    variant_id: str | None,
    warning: str,
    metadata: dict[str, Any] | None = None,
    prior_warnings: list[str] | None = None,
) -> DriftResult:
    result = not_applicable_result(
        method_id=TOTAL_VARIATION_METHOD_ID,
        method_name=TOTAL_VARIATION_METHOD_NAME,
        method_category=METHOD_CATEGORY,
        variant_id=variant_id,
        warning=warning,
        metadata=metadata,
    )
    if prior_warnings:
        result.warnings = prior_warnings + result.warnings
    return result


def _l_infinity_not_applicable(
    variant_id: str | None,
    warning: str,
    metadata: dict[str, Any] | None = None,
    prior_warnings: list[str] | None = None,
) -> DriftResult:
    result = not_applicable_result(
        method_id=L_INFINITY_METHOD_ID,
        method_name=L_INFINITY_METHOD_NAME,
        method_category=METHOD_CATEGORY,
        variant_id=variant_id,
        warning=warning,
        metadata=metadata,
    )
    if prior_warnings:
        result.warnings = prior_warnings + result.warnings
    return result


def _bhattacharyya_not_applicable(
    variant_id: str | None,
    warning: str,
    metadata: dict[str, Any] | None = None,
    prior_warnings: list[str] | None = None,
) -> DriftResult:
    result = not_applicable_result(
        method_id=BHATTACHARYYA_METHOD_ID,
        method_name=BHATTACHARYYA_METHOD_NAME,
        method_category=METHOD_CATEGORY,
        variant_id=variant_id,
        warning=warning,
        metadata=metadata,
    )
    if prior_warnings:
        result.warnings = prior_warnings + result.warnings
    return result


def _hinc_not_applicable(
    variant_id: str | None,
    warning: str,
    metadata: dict[str, Any] | None = None,
    prior_warnings: list[str] | None = None,
) -> DriftResult:
    result = not_applicable_result(
        method_id=HINC_METHOD_ID,
        method_name=HINC_METHOD_NAME,
        method_category=METHOD_CATEGORY,
        variant_id=variant_id,
        warning=warning,
        metadata=metadata,
    )
    if prior_warnings:
        result.warnings = prior_warnings + result.warnings
    return result


def _wasserstein_not_applicable(
    variant_id: str | None,
    warning: str,
    metadata: dict[str, Any] | None = None,
    prior_warnings: list[str] | None = None,
) -> DriftResult:
    result = not_applicable_result(
        method_id=WASSERSTEIN_METHOD_ID,
        method_name=WASSERSTEIN_METHOD_NAME,
        method_category=METHOD_CATEGORY,
        variant_id=variant_id,
        warning=warning,
        metadata=metadata,
    )
    if prior_warnings:
        result.warnings = prior_warnings + result.warnings
    return result


def _mann_whitney_not_applicable(
    variant_id: str | None,
    warning: str,
    metadata: dict[str, Any] | None = None,
    prior_warnings: list[str] | None = None,
) -> DriftResult:
    result = not_applicable_result(
        method_id=MANN_WHITNEY_METHOD_ID,
        method_name=MANN_WHITNEY_METHOD_NAME,
        method_category=METHOD_CATEGORY,
        variant_id=variant_id,
        warning=warning,
        metadata=metadata,
    )
    if prior_warnings:
        result.warnings = prior_warnings + result.warnings
    return result


def _t_test_not_applicable(
    variant_id: str | None,
    warning: str,
    metadata: dict[str, Any] | None = None,
    prior_warnings: list[str] | None = None,
) -> DriftResult:
    result = not_applicable_result(
        method_id=T_TEST_METHOD_ID,
        method_name=T_TEST_METHOD_NAME,
        method_category=METHOD_CATEGORY,
        variant_id=variant_id,
        warning=warning,
        metadata=metadata,
    )
    if prior_warnings:
        result.warnings = prior_warnings + result.warnings
    return result


def _levene_not_applicable(
    variant_id: str | None,
    warning: str,
    metadata: dict[str, Any] | None = None,
    prior_warnings: list[str] | None = None,
) -> DriftResult:
    result = not_applicable_result(
        method_id=LEVENE_METHOD_ID,
        method_name=LEVENE_METHOD_NAME,
        method_category=METHOD_CATEGORY,
        variant_id=variant_id,
        warning=warning,
        metadata=metadata,
    )
    if prior_warnings:
        result.warnings = prior_warnings + result.warnings
    return result
