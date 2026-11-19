# DM-006 PSI Design

## 1. Method Identity

- Method ID: `DM-006`
- Method name: `PSI`
- Category: `BatchDistributionComparison`
- Method kind: `detector`
- Status: `구현 완료`
- Source catalog: `drift_methods_catalog.md`
- Source variant document: `algorithm_variants/psi_algorithm_variants.md`

## 2. Purpose

This method answers the drift question represented by `PSI` in the
catalog. Primary input from the catalog: score band, numeric bin, category proportion.
Primary output from the catalog: PSI score.

## 3. Supported Variants

- `NUMERIC_BINNED_PSI`
- `CATEGORICAL_PSI`
- `SCORE_BAND_PSI`
- `POPULATION_WEIGHTED_PSI`

## 4. Input Schema

Use the common `pandas.DataFrame` input boundary from
`../input_output_contracts.md`.

Supported schema:

```text
Common: `time`
Numeric PSI: `value_col`
Categorical/score-band/weighted PSI: `category_col`, `score_band_col`, and optional `count_col`
```

The implementation must validate the concrete columns through `params` and
return `severity="not_applicable"` if the supplied schema cannot represent this
method's required input.

## 5. Parameters

Method-specific parameters come from `drift_method_parameter_guide.md` and the
variant source document. The implementation should at minimum support:

- `variant_id`: one of the supported variant IDs.
- `value_col`: numeric score/value column for binned PSI.
- `bin_count`: reference quantile bin count, default `10`.
- `category_col` or `score_band_col`: categorical PSI key.
- `count_col`: optional population weight/count column.
- `threshold`: PSI alarm threshold, default `0.25`.
- `epsilon`: smoothing floor for proportions, default `1e-6`.
- `min_reference_size` and `min_current_size`.

## 6. Output Measurements

Return canonical measurements where applicable:

- `DRIFT_ALARM_STATE`
- `P_VALUE`
- `TEST_STATISTIC`
- `PSI_SCORE`
- `PSI_CONTRIBUTION`
- `CATEGORY_COUNTS_REFERENCE`
- `CATEGORY_COUNTS_CURRENT`

Always include `SAMPLE_SIZE` or relevant effective count metadata when the
method compares reference/current windows.

## 7. Algorithm Steps

1. Validate required DataFrame columns and parameter names.
2. Convert `time` to datetime and sort by time.
3. Split reference/current windows.
4. Build reference/current bins or category counts.
5. Compute PSI contribution per bin/category.
6. Apply `PSI_SCORE > threshold`.
7. Return `DriftResult` with canonical measurement keys and interpretation text.

## 8. Drift Decision Rule

Implemented rule:

```text
drift_detected = PSI_SCORE > threshold
```

## 9. Warnings and Not-Applicable Conditions

Return warnings for:

- missing required columns
- empty reference/current windows
- sample size below method minimum
- unsupported variant id
- constant numeric reference values that cannot form bins
- invalid negative or nonnumeric counts
- missing category or score-band columns
- invalid threshold or smoothing parameters

## 10. Implementation Target

```text
module: drift_algorithm.methods.batchdistributioncomparison
function: detect_psi
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
`detect_psi`.

Implemented behavior:

- `NUMERIC_BINNED_PSI` bins values using reference quantile edges.
- `CATEGORICAL_PSI` compares category proportions.
- `SCORE_BAND_PSI` compares configured score bands.
- `POPULATION_WEIGHTED_PSI` uses supplied counts/weights or row counts.
- PSI does not produce a p-value; decision is threshold-based.
- unsupported variants, missing columns, invalid windows, invalid counts,
  invalid thresholds, and insufficient samples return `not_applicable`.

Verification:

```text
py_compile: passed
DM-006 pytest: 5 passed
DM-001 through DM-006 batch regression pytest: 32 passed
```
