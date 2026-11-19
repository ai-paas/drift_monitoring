# DM-009 Hellinger Distance Design

## 1. Method Identity

- Method ID: `DM-009`
- Method name: `Hellinger Distance`
- Category: `BatchDistributionComparison`
- Method kind: `detector`
- Status: `확정`
- Source catalog: `drift_methods_catalog.md`
- Source variant document: `algorithm_variants/hellinger_distance_algorithm_variants.md`

## 2. Purpose

This method answers the drift question represented by `Hellinger Distance` in the
catalog. Primary input from the catalog: 확률분포, category distribution, histogram.
Primary output from the catalog: Hellinger distance.

## 3. Supported Variants

- `DISCRETE_HELLINGER_DISTANCE`
- `HISTOGRAM_HELLINGER_DISTANCE`
- `CATEGORICAL_HELLINGER_DISTANCE`

## 4. Input Schema

Use the common `pandas.DataFrame` input boundary from
`../input_output_contracts.md`.

Implemented schemas:

```text
1. Categorical/probability-count schema
   Required: `time`, `category_col`
   Optional: `count_col`
   Used by:
   - DISCRETE_HELLINGER_DISTANCE
   - CATEGORICAL_HELLINGER_DISTANCE

2. Numeric histogram schema
   Required: `time`, `value_col`
   Used by:
   - HISTOGRAM_HELLINGER_DISTANCE
```

The implementation must validate the concrete columns through `params` and
return `severity="not_applicable"` if the supplied schema cannot represent this
method's required input.

## 5. Parameters

Implemented parameters:

- `variant_id`: defaults to `DISCRETE_HELLINGER_DISTANCE`
- `threshold` or `threshold_or_alpha`: distance alarm threshold, default `0.1`
- `category_col`: category column for count-based inputs
- `count_col`: optional count/weight column; omitted means each row counts as 1
- `value_col`: numeric value column for `HISTOGRAM_HELLINGER_DISTANCE`
- `bin_count`: reference-quantile histogram bin count for histogram mode,
  default `10`
- `min_reference_size`, `min_current_size`: effective sample-size guards

## 6. Output Measurements

Return canonical measurements where applicable:

- `DRIFT_ALARM_STATE`
- `P_VALUE`
- `TEST_STATISTIC`
- `HELLINGER_DISTANCE`
- `HELLINGER_CONTRIBUTION`
- `CATEGORY_PROPORTION_DELTA`
- `CATEGORY_COUNTS_REFERENCE`
- `CATEGORY_COUNTS_CURRENT`

Always include `SAMPLE_SIZE` or relevant effective count metadata when the
method compares reference/current windows.

## 7. Algorithm Steps

1. Validate the variant, threshold, and selected input schema.
2. Split reference/current windows.
3. Build aligned category/bin counts.
4. Convert counts to proportions.
5. Compute Hellinger distance:
   `sqrt(0.5 * sum((sqrt(p_i) - sqrt(q_i))^2))`.
6. Use the distance as the score and compare it with `threshold`.
7. Return `DriftResult` with distance, contribution, proportion delta, count,
   and sample-size measurements.

## 8. Drift Decision Rule

This implementation does not produce a p-value.

- `drift_detected = HELLINGER_DISTANCE > threshold`
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
- constant numeric reference values in histogram mode

## 10. Implementation Target

```text
module: drift_algorithm.methods.batchdistributioncomparison
function: detect_hellinger_distance
```

## 11. Verification Plan

Implemented tests:

```text
tests/test_hellinger_distance.py
```

Coverage:

1. no-drift categorical counts
2. categorical drift candidate
3. new category handling
4. numeric histogram Hellinger distance
5. validation and cleaning warnings
