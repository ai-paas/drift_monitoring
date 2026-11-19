# DM-011 L-Infinity Distance Design

## 1. Method Identity

- Method ID: `DM-011`
- Method name: `L-Infinity Distance`
- Category: `BatchDistributionComparison`
- Method kind: `detector`
- Status: `확정`
- Source catalog: `drift_methods_catalog.md`
- Source variant document: `algorithm_variants/l_infinity_distance_algorithm_variants.md`

## 2. Purpose

This method answers the drift question represented by `L-Infinity Distance` in the
catalog. Primary input from the catalog: category distribution, probability vector.
Primary output from the catalog: max absolute proportion delta.

## 3. Supported Variants

- `CATEGORICAL_L_INFINITY`
- `PROBABILITY_VECTOR_L_INFINITY`
- `BINNED_NUMERIC_L_INFINITY`

## 4. Input Schema

Use the common `pandas.DataFrame` input boundary from
`../input_output_contracts.md`.

Implemented schemas:

```text
1. Categorical/probability-count schema
   Required: `time`, `category_col`
   Optional: `count_col`
   Used by:
   - CATEGORICAL_L_INFINITY
   - PROBABILITY_VECTOR_L_INFINITY

2. Numeric histogram schema
   Required: `time`, `value_col`
   Used by:
   - BINNED_NUMERIC_L_INFINITY
```

The implementation must validate the concrete columns through `params` and
return `severity="not_applicable"` if the supplied schema cannot represent this
method's required input.

## 5. Parameters

Implemented parameters:

- `variant_id`: defaults to `CATEGORICAL_L_INFINITY`
- `threshold` or `threshold_or_alpha`: max-delta alarm threshold, default `0.1`
- `category_col`: category/probability-vector component column for count-based
  inputs
- `count_col`: optional count/weight column; omitted means each row counts as 1
- `value_col`: numeric value column for `BINNED_NUMERIC_L_INFINITY`
- `bin_count`: reference-quantile histogram bin count for numeric mode, default
  `10`
- `min_reference_size`, `min_current_size`: effective sample-size guards

## 6. Output Measurements

Return canonical measurements where applicable:

- `DRIFT_ALARM_STATE`
- `P_VALUE`
- `TEST_STATISTIC`
- `L_INFINITY_DISTANCE`
- `MAX_ABSOLUTE_PROPORTION_DELTA`
- `MAX_COMPONENT`
- `L_INFINITY_CONTRIBUTION`
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
5. Compute per-component proportion deltas.
6. Compute L-infinity distance as `max(abs(p_i - q_i))`.
7. Return the max component and sorted contribution rows with the score.

## 8. Drift Decision Rule

This implementation does not produce a p-value.

- `drift_detected = L_INFINITY_DISTANCE > threshold`
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
function: detect_l_infinity_distance
```

## 11. Verification Plan

Implemented tests:

```text
tests/test_l_infinity_distance.py
```

Coverage:

1. no-drift categorical counts
2. categorical max-component drift candidate
3. probability-vector variant through category/count probability contract
4. binned numeric L-infinity distance
5. validation and cleaning warnings
