# DM-005 G-test Design

## 1. Method Identity

- Method ID: `DM-005`
- Method name: `G-test`
- Category: `BatchDistributionComparison`
- Method kind: `detector`
- Status: `구현 완료`
- Source catalog: `drift_methods_catalog.md`
- Source variant document: `algorithm_variants/g_test_algorithm_variants.md`

## 2. Purpose

This method answers the drift question represented by `G-test` in the
catalog. Primary input from the catalog: 범주형 빈도, likelihood ratio.
Primary output from the catalog: G statistic, p-value.

## 3. Supported Variants

- `LIKELIHOOD_RATIO_G_TEST_GOF`
- `LIKELIHOOD_RATIO_G_TEST_INDEPENDENCE`
- `G_TEST_WITH_SMALL_COUNT_CAUTION`

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
- `small_count_threshold`: expected-count caution threshold, default `5`.
- `min_reference_size` and `min_current_size`.

## 6. Output Measurements

Return canonical measurements where applicable:

- `DRIFT_ALARM_STATE`
- `P_VALUE`
- `TEST_STATISTIC`
- `G_STATISTIC`
- `DEGREES_OF_FREEDOM`
- `CATEGORY_COUNTS_REFERENCE`
- `CATEGORY_COUNTS_CURRENT`
- `CATEGORY_PROPORTION_DELTA`
- `SMALL_EXPECTED_COUNT`

Always include `SAMPLE_SIZE` or relevant effective count metadata when the
method compares reference/current windows.

## 7. Algorithm Steps

1. Validate required DataFrame columns and parameter names.
2. Convert `time` to datetime and sort by time.
3. Split reference/current windows.
4. Aggregate category counts per window.
5. Compute likelihood-ratio G statistic for goodness-of-fit or independence.
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
- small expected-count approximation warnings

## 10. Implementation Target

```text
module: drift_algorithm.methods.batchdistributioncomparison
function: detect_g_test
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
`detect_g_test`.

Implemented behavior:

- `LIKELIHOOD_RATIO_G_TEST_GOF` compares current counts with reference-derived
  expected proportions using log-likelihood power divergence.
- `LIKELIHOOD_RATIO_G_TEST_INDEPENDENCE` compares reference/current contingency
  tables using log-likelihood chi-square contingency.
- `G_TEST_WITH_SMALL_COUNT_CAUTION` reports small expected-count diagnostics.
- unsupported variants, missing columns, invalid windows, invalid counts, too
  few categories, and insufficient samples return `not_applicable`.

Verification:

```text
py_compile: passed
DM-005 pytest: 5 passed
DM-001 through DM-005 batch regression pytest: 27 passed
```
