# DM-004 Fisher's Exact Test Design

## 1. Method Identity

- Method ID: `DM-004`
- Method name: `Fisher's Exact Test`
- Category: `BatchDistributionComparison`
- Method kind: `detector`
- Status: `구현 완료`
- Source catalog: `drift_methods_catalog.md`
- Source variant document: `algorithm_variants/fisher_s_exact_test_algorithm_variants.md`

## 2. Purpose

This method answers the drift question represented by `Fisher's Exact Test` in the
catalog. Primary input from the catalog: 작은 표본의 범주형 contingency table.
Primary output from the catalog: exact p-value.

## 3. Supported Variants

- `TWO_BY_TWO_FISHER_EXACT`
- `ONE_SIDED_FISHER_EXACT`
- `EXTENDED_CONTINGENCY_EXACT_TEST`

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
- `count_col`: optional non-negative integer count column.
- `alpha`: p-value threshold, default `0.05`.
- `alternative`: `two-sided`, `less`, or `greater` for 2x2 variants.
- `permutations` and `random_state`: deterministic extended-table surrogate
  settings.
- `min_reference_size` and `min_current_size`.

## 6. Output Measurements

Return canonical measurements where applicable:

- `DRIFT_ALARM_STATE`
- `P_VALUE`
- `TEST_STATISTIC`
- `ODDS_RATIO`
- `CATEGORY_COUNTS_REFERENCE`
- `CATEGORY_COUNTS_CURRENT`
- `CATEGORY_PROPORTION_DELTA`

Always include `SAMPLE_SIZE` or relevant effective count metadata when the
method compares reference/current windows.

## 7. Algorithm Steps

1. Validate required DataFrame columns and parameter names.
2. Convert `time` to datetime and sort by time.
3. Split reference/current windows.
4. Aggregate category counts per window.
5. Run 2x2 Fisher exact test or deterministic extended-table permutation
   surrogate.
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
- non-integer, negative, or nonnumeric counts
- 2x2 variants called with more than two categories
- invalid `alternative`
- insufficient rows or count totals

## 10. Implementation Target

```text
module: drift_algorithm.methods.batchdistributioncomparison
function: detect_fisher_s_exact_test
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
`detect_fisher_s_exact_test`.

Implemented behavior:

- `TWO_BY_TWO_FISHER_EXACT` uses SciPy Fisher exact test with two-sided
  alternative.
- `ONE_SIDED_FISHER_EXACT` uses SciPy Fisher exact test with one-sided
  alternative.
- `EXTENDED_CONTINGENCY_EXACT_TEST` uses a deterministic permutation exact-test
  surrogate for 2xK count tables.
- unsupported variants, missing columns, invalid windows, invalid counts,
  invalid alternatives, and insufficient samples return `not_applicable`.

Verification:

```text
py_compile: passed
DM-004 pytest: 5 passed
DM-001/002/003/004 batch regression pytest: 22 passed
```
