# DM-008 Jensen-Shannon Distance Design

## 1. Method Identity

- Method ID: `DM-008`
- Method name: `Jensen-Shannon Distance`
- Category: `BatchDistributionComparison`
- Method kind: `detector`
- Status: `확정`
- Source catalog: `drift_methods_catalog.md`
- Source variant document: `algorithm_variants/js_distance_algorithm_variants.md`

## 2. Purpose

This method answers the drift question represented by `Jensen-Shannon Distance` in the
catalog. Primary input from the catalog: 확률분포, histogram, topic distribution.
Primary output from the catalog: JS divergence/distance.

## 3. Supported Variants

- `JENSEN_SHANNON_DIVERGENCE`
- `JENSEN_SHANNON_DISTANCE`
- `MULTICLASS_PROBABILITY_JS`
- `TEXT_TOPIC_JS`

## 4. Input Schema

Use the common `pandas.DataFrame` input boundary from
`../input_output_contracts.md`.

Implemented schemas:

```text
1. Categorical/probability-count schema
   Required: `time`, `category_col`
   Optional: `count_col`
   Used by:
   - JENSEN_SHANNON_DIVERGENCE
   - JENSEN_SHANNON_DISTANCE
   - MULTICLASS_PROBABILITY_JS
   - TEXT_TOPIC_JS

2. Numeric histogram schema
   Required: `time`, `value_col`
   Enable with: params["input_mode"] == "numeric_histogram"
   Used by:
   - JENSEN_SHANNON_DIVERGENCE
   - JENSEN_SHANNON_DISTANCE
```

The implementation must validate the concrete columns through `params` and
return `severity="not_applicable"` if the supplied schema cannot represent this
method's required input.

## 5. Parameters

Implemented parameters:

- `variant_id`: defaults to `JENSEN_SHANNON_DIVERGENCE`
- `threshold` or `threshold_or_alpha`: threshold for the selected JS score,
  default `0.1`
- `epsilon`: positive smoothing floor before probability normalization, default
  `1e-12`
- `category_col`: category/class/topic column for count-based inputs
- `count_col`: optional count/weight column; omitted means each row counts as 1
- `value_col`: numeric value column for `input_mode="numeric_histogram"`
- `input_mode`: set to `numeric_histogram` for numeric histogram distance
- `bin_count`: reference-quantile histogram bin count for numeric mode, default
  `10`
- `min_reference_size`, `min_current_size`: effective sample-size guards

## 6. Output Measurements

Return canonical measurements where applicable:

- `DRIFT_ALARM_STATE`
- `P_VALUE`
- `TEST_STATISTIC`
- `JENSEN_SHANNON_DIVERGENCE`
- `JENSEN_SHANNON_DISTANCE`
- `JENSEN_SHANNON_CONTRIBUTION`
- `CATEGORY_PROPORTION_DELTA`
- `CATEGORY_COUNTS_REFERENCE`
- `CATEGORY_COUNTS_CURRENT`

Always include `SAMPLE_SIZE` or relevant effective count metadata when the
method compares reference/current windows.

## 7. Algorithm Steps

1. Validate the variant, threshold, epsilon, and selected input schema.
2. Split reference/current windows.
3. Build aligned category/bin counts.
4. Convert counts to proportions.
5. Apply epsilon smoothing and renormalize both distributions.
6. Compute midpoint distribution `m = 0.5 * (p + q)`.
7. Compute base-2 JS divergence:
   `0.5 * KL2(p || m) + 0.5 * KL2(q || m)`.
8. Compute JS distance as `sqrt(JS divergence)`.
9. Use divergence as the alarm score except for
   `JENSEN_SHANNON_DISTANCE`, which uses distance.
10. Return `DriftResult` with both divergence and distance measurements.

## 8. Drift Decision Rule

This implementation does not produce a p-value.

- `JENSEN_SHANNON_DISTANCE`: `drift_detected = distance > threshold`
- Other supported variants: `drift_detected = divergence > threshold`
- `severity = "drift_detected"` when the threshold is exceeded, otherwise
  `"normal"`

## 9. Warnings and Not-Applicable Conditions

Return warnings for:

- missing required columns
- empty reference/current windows
- sample size below method minimum
- unsupported variant id
- invalid threshold or epsilon
- invalid count values
- constant numeric reference values in histogram mode
- label-dependent or topic-specific variants are interpreted through the
  category/count probability contract unless a richer probability-vector schema
  is added later

## 10. Implementation Target

```text
module: drift_algorithm.methods.batchdistributioncomparison
function: detect_jensen_shannon_distance
```

## 11. Verification Plan

Implemented tests:

```text
tests/test_jensen_shannon_distance.py
```

Coverage:

1. no-drift categorical counts
2. categorical drift candidate
3. distance-scale alarm rule
4. numeric histogram distance mode
5. multiclass probability and text topic variants through category/count
   probability contract
6. validation and cleaning warnings
