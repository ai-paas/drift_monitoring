# DM-013 Histogram Intersection Normalized Complement Design

## 1. Method Identity

- Method ID: `DM-013`
- Method name: `Histogram Intersection Normalized Complement`
- Category: `BatchDistributionComparison`
- Method kind: `detector`
- Status: `확정`
- Source catalog: `drift_methods_catalog.md`
- Source variant document: `algorithm_variants/histogram_intersection_normalized_complement_algorithm_variants.md`

## 2. Purpose

This method answers the drift question represented by `Histogram Intersection Normalized Complement` in the
catalog. Primary input from the catalog: histogram, image feature histogram.
Primary output from the catalog: normalized complement score.

## 3. Supported Variants

- `HINC_CATEGORICAL`
- `HINC_HISTOGRAM_NUMERIC`
- `HINC_IMAGE_FEATURE`

## 4. Input Schema

Use the common `pandas.DataFrame` input boundary from
`../input_output_contracts.md`.

Implemented schemas:

```text
1. Categorical/feature-bin count schema
   Required: `time`, `category_col`
   Optional: `count_col`
   Used by:
   - HINC_CATEGORICAL
   - HINC_IMAGE_FEATURE

2. Numeric histogram schema
   Required: `time`, `value_col`
   Used by:
   - HINC_HISTOGRAM_NUMERIC
```

The implementation must validate the concrete columns through `params` and
return `severity="not_applicable"` if the supplied schema cannot represent this
method's required input.

## 5. Parameters

Implemented parameters:

- `variant_id`: defaults to `HINC_CATEGORICAL`
- `threshold` or `threshold_or_alpha`: complement-score alarm threshold,
  default `0.1`
- `category_col`: category or feature-bin column for count-based inputs
- `count_col`: optional count/weight column; omitted means each row counts as 1
- `value_col`: numeric value column for `HINC_HISTOGRAM_NUMERIC`
- `bin_count`: reference-quantile histogram bin count for numeric mode, default
  `10`
- `min_reference_size`, `min_current_size`: effective sample-size guards

## 6. Output Measurements

Return canonical measurements where applicable:

- `DRIFT_ALARM_STATE`
- `P_VALUE`
- `TEST_STATISTIC`
- `HISTOGRAM_INTERSECTION_NORMALIZED_COMPLEMENT`
- `HISTOGRAM_INTERSECTION`
- `HINC_CONTRIBUTION`
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
5. Compute histogram intersection `sum(min(p_i, q_i))`.
6. Compute normalized complement score as `1 - intersection`.
7. Use the complement score as the drift score and compare it with `threshold`.

## 8. Drift Decision Rule

This implementation does not produce a p-value.

- `drift_detected = HISTOGRAM_INTERSECTION_NORMALIZED_COMPLEMENT > threshold`
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
- `HINC_IMAGE_FEATURE` is interpreted through the category/count feature-bin
  histogram contract unless an image extractor schema is added later

## 10. Implementation Target

```text
module: drift_algorithm.methods.batchdistributioncomparison
function: detect_histogram_intersection_normalized_complement
```

## 11. Verification Plan

Implemented tests:

```text
tests/test_histogram_intersection_normalized_complement.py
```

Coverage:

1. no-drift categorical counts
2. categorical overlap-loss drift candidate
3. numeric histogram HINC
4. image-feature variant through feature-bin histogram contract
5. validation and cleaning warnings
