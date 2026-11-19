# DM-003 Chi-square Test Design

## 1. Method Identity

- Method ID: `DM-003`
- Method name: `Chi-square Test`
- Category: `BatchDistributionComparison`
- Method kind: `detector`
- Status: `구현 완료`
- Source catalog: `drift_methods_catalog.md`
- Source variant document: `algorithm_variants/chi_square_test_algorithm_variants.md`

## 2. Purpose

This method answers the drift question represented by `Chi-square Test` in the
catalog. Primary input from the catalog: 범주형 빈도, class distribution.
Primary output from the catalog: chi-square statistic, p-value.

## 3. Supported Variants

- `CHI_SQUARE_GOODNESS_OF_FIT`
- `CHI_SQUARE_HOMOGENEITY`
- `CHI_SQUARE_WITH_LOW_EXPECTED_COUNT_CAUTION`

## 4. Input Schema

Use the common `pandas.DataFrame` input boundary from
`../input_output_contracts.md`.

Supported schema:

```text
Common: `time`
Long categorical count format: `category_col` and optional `count_col`
If `count_col` is absent, each row counts as one observation.
```

The implementation must validate the concrete columns through `params` and
return `severity="not_applicable"` if the supplied schema cannot represent this
method's required input.

## 5. Parameters

Method-specific parameters come from `drift_method_parameter_guide.md` and the
variant source document. The implementation should at minimum support:

- `variant_id`: one of the supported variant IDs.
- `category_col`: category column, default `category`.
- `count_col`: optional non-negative count column.
- `alpha`: p-value threshold, default `0.05`.
- `low_expected_threshold`: expected-count caution threshold, default `5`.
- `min_reference_size` and `min_current_size`.

## 6. Output Measurements

Return canonical measurements where applicable:

- `DRIFT_ALARM_STATE`
- `P_VALUE`
- `TEST_STATISTIC`
- `DEGREES_OF_FREEDOM`
- `CATEGORY_COUNTS_REFERENCE`
- `CATEGORY_COUNTS_CURRENT`
- `CATEGORY_PROPORTION_DELTA`
- `STANDARDIZED_RESIDUALS`
- `LOW_EXPECTED_COUNT`

Always include `SAMPLE_SIZE` or relevant effective count metadata when the
method compares reference/current windows.

## 7. Algorithm Steps

1. Validate required DataFrame columns and parameter names.
2. Convert `time` to datetime and sort by time.
3. Split reference/current windows.
4. Aggregate category counts per window.
5. Compute Chi-square goodness-of-fit or homogeneity statistic.
6. Apply `p_value < alpha`.
7. Return `DriftResult` with canonical measurement keys and interpretation text.

## 8. Drift Decision Rule

Implemented rule:

```text
drift_detected = p_value < alpha
```

## 9. Warnings and Not-Applicable Conditions

Return warnings for:

- missing required columns
- empty reference/current windows
- sample size below method minimum
- unsupported variant id
- invalid negative or nonnumeric counts
- fewer than two categories
- zero expected counts
- low expected count approximation warnings

## 10. Implementation Target

```text
module: drift_algorithm.methods.batchdistributioncomparison
function: detect_chi_square_test
```

## 11. Verification Plan

Create at least two tests when implementation starts:

1. no-drift synthetic data with similar reference/current windows
2. drift-candidate synthetic data that changes the statistic or alarm in the
   expected direction

The test must assert canonical measurement keys, warning behavior, and the
documented `drift_detected` rule.

## 12. Implementation Notes

Implemented in `drift_algorithm.methods.batchdistributioncomparison` as
`detect_chi_square_test`.

Implemented behavior:

- `CHI_SQUARE_GOODNESS_OF_FIT` compares current counts with reference-derived
  expected proportions.
- `CHI_SQUARE_HOMOGENEITY` compares reference/current contingency tables.
- `CHI_SQUARE_WITH_LOW_EXPECTED_COUNT_CAUTION` runs the homogeneity test and
  surfaces expected-count diagnostics.
- unsupported variants, missing columns, invalid windows, invalid counts, too
  few categories, and insufficient samples return `not_applicable`.

Verification:

```text
py_compile: passed
DM-003 pytest: 5 passed
DM-001/002/003 batch regression pytest: 17 passed
```
