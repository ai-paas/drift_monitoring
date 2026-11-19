# DM-051 SHAP Drift Design

## 1. Method Identity

- Method ID: `DM-051`
- Method name: `SHAP Drift`
- Category: `ExplanationDriftMethod`
- Method kind: `detector`
- Status: `구현 완료`
- Source catalog: `drift_methods_catalog.md`
- Source variant document: `algorithm_variants/shap_drift_algorithm_variants.md`

## 2. Purpose

This method answers the drift question represented by `SHAP Drift` in the
catalog. Primary input from the catalog: SHAP value matrix.
Primary output from the catalog: SHAP distribution shift, importance shift.

## 3. Supported Variants

- `SHAP_VALUE_DISTRIBUTION_TEST`
- `GLOBAL_IMPORTANCE_RANK_SHIFT`
- `CLASS_CONDITIONAL_SHAP_DRIFT`

## 4. Input Schema

Use the common `pandas.DataFrame` input boundary from
`../input_output_contracts.md`.

Supported schema:

```text
Common: `time`
Wide SHAP matrix: `shap_cols` or `feature_cols`
CLASS_CONDITIONAL_SHAP_DRIFT: wide SHAP matrix plus `class_col` or `label_col`
```

The implementation must validate the concrete columns through `params` and
return `severity="not_applicable"` if the supplied schema cannot represent this
method's required input.

## 5. Parameters

Method-specific parameters come from `drift_method_parameter_guide.md` and the
variant source document. The implementation should at minimum support:

- `variant_id`: one of the supported variant IDs.
- `shap_cols` or `feature_cols`: wide SHAP value columns.
- `alpha`: p-value decision threshold for KS-based variants, default `0.05`.
- `rank_shift_threshold`: normalized mean absolute rank-shift threshold for
  `GLOBAL_IMPORTANCE_RANK_SHIFT`, default `0.25`.
- `class_col` or `label_col`: required for `CLASS_CONDITIONAL_SHAP_DRIFT`.
- `min_reference_size` and `min_current_size`: default `20`.
- `min_class_size`: class-conditional minimum rows per class/window, default `5`.

## 6. Output Measurements

Return canonical measurements where applicable:

- `FEATURE_IMPORTANCE_OR_RANK`
- `SHAP_DRIFT_DISTANCE`
- `TEST_STATISTIC`
- `P_VALUE`
- `DRIFT_ALARM_STATE`
- `THRESHOLD`
- `METHOD_POLICY`
- `CLASS_SHAP_DRIFT_DISTANCE`
- `SIGNIFICANT_FEATURES`
- `REFERENCE_SAMPLE_SIZE`
- `CURRENT_SAMPLE_SIZE`
- `FEATURE_COLUMNS`

Always include `SAMPLE_SIZE` or relevant effective count metadata when the
method compares reference/current windows.

## 7. Algorithm Steps

1. Validate required DataFrame columns and parameter names.
2. Convert `time` to datetime and sort by time.
3. Split reference/current windows.
4. Convert SHAP columns to numeric arrays and drop invalid rows with warnings.
5. Compute the variant-specific score:
   - feature-wise SHAP KS distribution test
   - normalized global importance rank shift
   - class-conditional feature-wise SHAP KS distribution test
6. Apply the documented p-value or rank-shift threshold rule.
7. Return `DriftResult` with canonical measurement keys and interpretation text.

## 8. Drift Decision Rule

Implemented rules:

- `SHAP_VALUE_DISTRIBUTION_TEST`: drift when the minimum feature-wise KS p-value
  is below `alpha`.
- `GLOBAL_IMPORTANCE_RANK_SHIFT`: drift when mean normalized absolute rank delta
  is greater than `rank_shift_threshold`.
- `CLASS_CONDITIONAL_SHAP_DRIFT`: drift when the minimum class/feature KS
  p-value is below `alpha`.

## 9. Warnings and Not-Applicable Conditions

Return warnings for:

- missing required columns
- empty reference/current windows
- sample size below method minimum
- unsupported variant id
- non-numeric SHAP values after cleaning
- class-conditional variant called without class or label column
- class-conditional variant without common classes or with too-small class
  windows

## 10. Implementation Target

```text
module: drift_algorithm.methods.explanationdriftmethod
function: detect_shap_drift
```

## 11. Verification Plan

Create at least two tests when implementation starts:

1. no-drift synthetic data with similar reference/current windows
2. drift-candidate synthetic data that changes the statistic or alarm in the
   expected direction

The test must assert canonical measurement keys, warning behavior, and the
documented `drift_detected` rule.

## 12. Implementation Notes

Implemented in `drift_algorithm.methods.explanationdriftmethod` as
`detect_shap_drift`.

Implemented behavior:

- `SHAP_VALUE_DISTRIBUTION_TEST` compares each SHAP column with a two-sample KS
  test and reports the largest feature distance and minimum p-value.
- `GLOBAL_IMPORTANCE_RANK_SHIFT` compares mean absolute SHAP importance ranks and
  reports normalized rank movement.
- `CLASS_CONDITIONAL_SHAP_DRIFT` repeats feature-wise KS tests within common
  reference/current classes and reports class-specific distances.
- unsupported variants, missing columns, invalid windows, invalid numeric input,
  insufficient samples, and invalid class partitions return `not_applicable`.

Verification:

```text
py_compile: passed
DM-051 pytest: 5 passed
implemented numeric, streaming, supervised, multivariate, representation, and explanation pytest: 216 passed
```
