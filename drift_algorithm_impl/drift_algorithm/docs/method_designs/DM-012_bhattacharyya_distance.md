# DM-012 Bhattacharyya Distance Design

## 1. Method Identity

- Method ID: `DM-012`
- Method name: `Bhattacharyya Distance`
- Category: `BatchDistributionComparison`
- Method kind: `detector`
- Status: `확정`
- Source catalog: `drift_methods_catalog.md`
- Source variant document: `algorithm_variants/bhattacharyya_distance_algorithm_variants.md`

## 2. Purpose

This method answers the drift question represented by `Bhattacharyya Distance` in the
catalog. Primary input from the catalog: histogram, Gaussian summary, category distribution.
Primary output from the catalog: Bhattacharyya distance.

## 3. Supported Variants

- `DISCRETE_BHATTACHARYYA_DISTANCE`
- `GAUSSIAN_BHATTACHARYYA_DISTANCE`
- `HISTOGRAM_BHATTACHARYYA_DISTANCE`

## 4. Input Schema

Use the common `pandas.DataFrame` input boundary from
`../input_output_contracts.md`.

Implemented schemas:

```text
1. Categorical/probability-count schema
   Required: `time`, `category_col`
   Optional: `count_col`
   Used by:
   - DISCRETE_BHATTACHARYYA_DISTANCE

2. Numeric histogram schema
   Required: `time`, `value_col`
   Used by:
   - HISTOGRAM_BHATTACHARYYA_DISTANCE

3. Univariate Gaussian numeric schema
   Required: `time`, `value_col`
   Used by:
   - GAUSSIAN_BHATTACHARYYA_DISTANCE
```

The implementation must validate the concrete columns through `params` and
return `severity="not_applicable"` if the supplied schema cannot represent this
method's required input.

## 5. Parameters

Implemented parameters:

- `variant_id`: defaults to `DISCRETE_BHATTACHARYYA_DISTANCE`
- `threshold` or `threshold_or_alpha`: distance alarm threshold, default `0.1`
- `category_col`: category column for count-based inputs
- `count_col`: optional count/weight column; omitted means each row counts as 1
- `value_col`: numeric value column for histogram/Gaussian variants
- `bin_count`: reference-quantile histogram bin count for histogram mode,
  default `10`
- `min_reference_size`, `min_current_size`: effective sample-size guards

## 6. Output Measurements

Return canonical measurements where applicable:

- `DRIFT_ALARM_STATE`
- `P_VALUE`
- `TEST_STATISTIC`
- `BHATTACHARYYA_DISTANCE`
- `BHATTACHARYYA_COEFFICIENT`
- `BHATTACHARYYA_CONTRIBUTION`
- `GAUSSIAN_SUMMARY`
- `CATEGORY_PROPORTION_DELTA`
- `CATEGORY_COUNTS_REFERENCE`
- `CATEGORY_COUNTS_CURRENT`

Always include `SAMPLE_SIZE` or relevant effective count metadata when the
method compares reference/current windows.

## 7. Algorithm Steps

1. Validate the variant, threshold, and selected input schema.
2. Split reference/current windows.
3. For discrete/histogram variants, build aligned category/bin counts and
   convert counts to proportions.
4. Compute Bhattacharyya coefficient `sum(sqrt(p_i * q_i))`.
5. Compute distance as `-log(coefficient)`.
6. For Gaussian variant, estimate univariate mean and variance for each window
   and compute the closed-form Gaussian Bhattacharyya distance.
7. Use the distance as the score and compare it with `threshold`.

## 8. Drift Decision Rule

This implementation does not produce a p-value.

- `drift_detected = BHATTACHARYYA_DISTANCE > threshold`
- `severity = "drift_detected"` when the threshold is exceeded, otherwise
  `"normal"`

## 9. Warnings and Not-Applicable Conditions

Return warnings for:

- missing required columns
- empty reference/current windows
- sample size below method minimum
- unsupported variant id
- invalid threshold
- invalid count values
- constant numeric reference/current values for Gaussian mode
- constant numeric reference values in histogram mode

## 10. Implementation Target

```text
module: drift_algorithm.methods.batchdistributioncomparison
function: detect_bhattacharyya_distance
```

## 11. Verification Plan

Implemented tests:

```text
tests/test_bhattacharyya_distance.py
```

Coverage:

1. no-drift discrete counts
2. discrete drift candidate
3. numeric histogram Bhattacharyya distance
4. Gaussian mean-shift candidate
5. validation, constant-variance, and cleaning warnings
