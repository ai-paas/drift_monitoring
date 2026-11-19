# DM-010 Total Variation Distance Design

## 1. Method Identity

- Method ID: `DM-010`
- Method name: `Total Variation Distance`
- Category: `BatchDistributionComparison`
- Method kind: `detector`
- Status: `확정`
- Source catalog: `drift_methods_catalog.md`
- Source variant document: `algorithm_variants/total_variation_distance_algorithm_variants.md`

## 2. Purpose

This method answers the drift question represented by `Total Variation Distance` in the
catalog. Primary input from the catalog: category distribution, probability vector.
Primary output from the catalog: total variation distance.

## 3. Supported Variants

- `CATEGORICAL_TOTAL_VARIATION`
- `HISTOGRAM_TOTAL_VARIATION`
- `PROBABILITY_VECTOR_TOTAL_VARIATION`

## 4. Input Schema

Use the common `pandas.DataFrame` input boundary from
`../input_output_contracts.md`.

Implemented schemas:

```text
1. Categorical/probability-count schema
   Required: `time`, `category_col`
   Optional: `count_col`
   Used by:
   - CATEGORICAL_TOTAL_VARIATION
   - PROBABILITY_VECTOR_TOTAL_VARIATION

2. Numeric histogram schema
   Required: `time`, `value_col`
   Used by:
   - HISTOGRAM_TOTAL_VARIATION
```

The implementation must validate the concrete columns through `params` and
return `severity="not_applicable"` if the supplied schema cannot represent this
method's required input.

## 5. Parameters

Implemented parameters:

- `variant_id`: defaults to `CATEGORICAL_TOTAL_VARIATION`
- `threshold` or `threshold_or_alpha`: distance alarm threshold, default `0.1`
- `category_col`: category/probability-vector dimension column for count-based
  inputs
- `count_col`: optional count/weight column; omitted means each row counts as 1
- `value_col`: numeric value column for `HISTOGRAM_TOTAL_VARIATION`
- `bin_count`: reference-quantile histogram bin count for histogram mode,
  default `10`
- `min_reference_size`, `min_current_size`: effective sample-size guards

## 6. Output Measurements

Return canonical measurements where applicable:

- `DRIFT_ALARM_STATE`
- `P_VALUE`
- `TEST_STATISTIC`
- `TOTAL_VARIATION_DISTANCE`
- `TOTAL_VARIATION_CONTRIBUTION`
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
5. Compute total variation distance:
   `0.5 * sum(abs(p_i - q_i))`.
6. Use the distance as the score and compare it with `threshold`.
7. Return `DriftResult` with distance, contribution, proportion delta, count,
   and sample-size measurements.

## 8. Drift Decision Rule

This implementation does not produce a p-value.

- `drift_detected = TOTAL_VARIATION_DISTANCE > threshold`
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
- probability-vector variants are interpreted through the category/count
  probability-vector contract unless a richer vector schema is added later

## 10. Implementation Target

```text
module: drift_algorithm.methods.batchdistributioncomparison
function: detect_total_variation_distance
```

## 11. Verification Plan

Implemented tests:

```text
tests/test_total_variation_distance.py
```

Coverage:

1. no-drift categorical counts
2. categorical drift candidate
3. probability-vector variant through category/count probability contract
4. numeric histogram total variation
5. validation and cleaning warnings
