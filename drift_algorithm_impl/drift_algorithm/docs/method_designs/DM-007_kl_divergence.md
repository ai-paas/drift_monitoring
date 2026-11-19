# DM-007 KL Divergence Design

## 1. Method Identity

- Method ID: `DM-007`
- Method name: `KL Divergence`
- Category: `BatchDistributionComparison`
- Method kind: `detector`
- Status: `확정`
- Source catalog: `drift_methods_catalog.md`
- Source variant document: `algorithm_variants/kl_divergence_algorithm_variants.md`

## 2. Purpose

This method answers the drift question represented by `KL Divergence` in the
catalog. Primary input from the catalog: 확률분포, histogram, category distribution.
Primary output from the catalog: KL divergence.

## 3. Supported Variants

- `DISCRETE_KL_DIVERGENCE`
- `HISTOGRAM_KL_DIVERGENCE`
- `SMOOTHED_KL_DIVERGENCE`
- `SYMMETRIZED_KL`

## 4. Input Schema

Use the common `pandas.DataFrame` input boundary from
`../input_output_contracts.md`.

Required schema:

```text
categorical_schema.md or probability schema. Required: `time` plus category/count or probability columns.
```

The implementation must validate the concrete columns through `params` and
return `severity="not_applicable"` if the supplied schema cannot represent this
method's required input.

## 5. Parameters

Method-specific parameters come from `drift_method_parameter_guide.md` and the
variant source document. The implementation should at minimum support:

- `variant_id`: one of the supported variants above. Default:
  `DISCRETE_KL_DIVERGENCE`.
- `threshold`: non-negative KL alarm threshold. Default: `0.1`.
- `epsilon`: positive smoothing floor applied before probability normalization.
  Default: `1e-12`.
- `category_col`: categorical distribution column for discrete, smoothed, and
  symmetrized variants. Default: `value_col` or `category`.
- `count_col`: optional non-negative count/weight column. If omitted, row counts
  are used.
- `value_col`: numeric value column for `HISTOGRAM_KL_DIVERGENCE`.
- `bin_count`: reference quantile bin count for histogram KL. Default: `10`.
- `min_reference_size` and `min_current_size`.

## 6. Output Measurements

Return canonical measurements where applicable:

- `DRIFT_ALARM_STATE`
- `P_VALUE`
- `TEST_STATISTIC`
- `KL_DIVERGENCE`
- `KL_CURRENT_REFERENCE`
- `KL_REFERENCE_CURRENT`
- `KL_CONTRIBUTION`
- `CATEGORY_COUNTS_REFERENCE`
- `CATEGORY_COUNTS_CURRENT`

Always include `SAMPLE_SIZE` or relevant effective count metadata when the
method compares reference/current windows.

## 7. Algorithm Steps

1. Validate required DataFrame columns and parameter names.
2. Convert `time` to datetime and sort by time.
3. Split reference/current windows or iterate the stream according to the method
   category.
4. Convert validated values to `numpy.ndarray` when numeric calculation starts.
5. Build reference and current probability vectors from category counts or
   histogram bins.
6. Apply epsilon smoothing and re-normalize both probability vectors.
7. Compute `KL_CURRENT_REFERENCE = sum(current * log(current / reference))`.
8. Also compute `KL_REFERENCE_CURRENT`; for `SYMMETRIZED_KL`, use the average
   of the two directional KL values as `KL_DIVERGENCE`.
9. Apply the threshold rule.
10. Return `DriftResult` with canonical measurement keys and interpretation text.

## 8. Drift Decision Rule

This implementation does not produce a p-value. It reports drift when:

```text
KL_DIVERGENCE > threshold
```

The default threshold is `0.1`.

## 9. Warnings and Not-Applicable Conditions

Return warnings for:

- missing required columns
- empty reference/current windows
- sample size below method minimum
- unsupported variant id
- numerical instability such as singular covariance or zero-probability bins
- label-dependent methods called without labels or error stream

## 10. Implementation Target

```text
module: drift_algorithm.methods.batchdistributioncomparison
function: detect_kl_divergence
```

## 11. Verification Plan

Implemented tests:

1. no-drift categorical data with similar reference/current distributions
2. drift-candidate categorical data with large distribution change
3. histogram KL over shifted numeric windows
4. smoothed and symmetrized KL variants
5. validation and dropped-row warning behavior

The test must assert canonical measurement keys, warning behavior, and the
documented `drift_detected` rule.
