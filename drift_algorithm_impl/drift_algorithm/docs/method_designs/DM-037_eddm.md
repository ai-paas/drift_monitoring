# DM-037 EDDM Design

## 1. Method Identity

- Method ID: `DM-037`
- Method name: `EDDM`
- Category: `SupervisedConceptDriftDetector`
- Method kind: `detector`
- Status: `확정`
- Source catalog: `drift_methods_catalog.md`
- Source variant document: `algorithm_variants/eddm_algorithm_variants.md`

## 2. Purpose

This method answers the drift question represented by `EDDM` in the
catalog. Primary input from the catalog: distance between errors.
Primary output from the catalog: warning state, drift state.

## 3. Supported Variants

- `EDDM_DISTANCE_BETWEEN_ERRORS`
- `EDDM_WARNING_DRIFT`
- `EDDM_GRADUAL_DRIFT`

First implementation status:

- all three variants support a precomputed binary error stream or derive errors
  from `y_true`/`y_pred`
- the first implementation uses index-gap distance between consecutive errors
- feature, embedding, categorical-count, and unsupervised input contracts are
  not supported

## 4. Input Schema

Use the common `pandas.DataFrame` input boundary from
`../input_output_contracts.md`.

Required schema:

```text
label_schema.md. Required: `time` plus `y_true`/`y_pred` or precomputed `error`.
```

The implementation must validate the concrete columns through `params` and
return `severity="not_applicable"` if the supplied schema cannot represent this
method's required input.

## 5. Parameters

Method-specific parameters come from `drift_method_parameter_guide.md` and the
variant source document. The implementation should at minimum support:

- `error_col` or `input_signal`
- `y_true` / `y_true_col`
- `y_pred` / `y_pred_col`
- `warning_level`
- `drift_level` or `threshold_or_alpha`
- `min_num_errors`
- `error_distance_metric`
- `min_reference_size`, `min_current_size`
- `record_events`, `max_event_records`
- `sample_imbalance_warning_ratio`

## 6. Output Measurements

Return canonical measurements where applicable:

- `DRIFT_ALARM_STATE`
- `P_VALUE`
- `TEST_STATISTIC`

Always include `SAMPLE_SIZE` or relevant effective count metadata when the
method compares reference/current windows.

First implementation canonical mapping:

- `TEST_STATISTIC`: `1 - EDDM_SCORE_RATIO`, so larger values mean stronger
  shortening of error distances
- `P_VALUE`: `None`, because EDDM returns a detector score rather than a
  frequentist p-value
- `DRIFT_ALARM_STATE`: `normal` or `drift_detected`

Additional measurements:

- `EDDM_SCORE`, `EDDM_SCORE_RATIO`
- `ERROR_DISTANCE_MEAN`, `ERROR_DISTANCE_STD`, `ERROR_DISTANCE_MAX_SCORE`
- `ERROR_COUNT`
- `WARNING_STATE`
- `WARNING_START_TIME`, `DRIFT_TIME`
- optional `EDDM_EVENTS`
- `GRADUAL_DRIFT_STATE` for `EDDM_GRADUAL_DRIFT`
- sample sizes and reference/current error-rate summaries

## 7. Algorithm Steps

1. Validate error-stream or label/prediction input.
2. Convert `time` to datetime, split reference/current windows, drop invalid
   timestamps or non-finite errors, and sort by time.
3. Derive a binary error stream from `error_col` or `y_true != y_pred`.
4. Replay reference and current rows chronologically.
5. Track the positions where error equals `1`.
6. Compute index gaps between consecutive errors.
7. Maintain the EDDM score `mean(distance) + 2 * std(distance)`.
8. Compare the current score to the historical maximum score.
9. Return `DriftResult` with canonical measurement keys and interpretation
   text.

## 8. Drift Decision Rule

The first implementation uses the standard EDDM score ratio rule:

```text
score_i = mean(error_distance) + 2 * std(error_distance)
ratio_i = score_i / max(score_1 ... score_i)
warning if ratio_i < warning_level
drift   if ratio_i < drift_level
```

Defaults:

```text
warning_level = 0.95
drift_level = 0.90
min_num_errors = 30
error_distance_metric = index_gap
```

## 9. Warnings and Not-Applicable Conditions

Return warnings for:

- missing required columns
- empty reference/current windows
- sample size below method minimum
- unsupported variant id
- numerical instability such as singular covariance or zero-probability bins
- label-dependent methods called without labels or error stream
- non-binary error stream values
- unsupported error distance metric
- too few observed errors to reach `min_num_errors`

## 10. Implementation Target

```text
module: drift_algorithm.methods.supervisedconceptdriftdetector
function: detect_eddm
```

## 11. Verification Plan

Implemented tests:

- no-drift error stream with stable error spacing
- warning/drift alarm from shortened error spacing
- gradual drift variant from `y_true`/`y_pred`
- validation and warning behavior
- non-scalar request rejection

Current test file:

```text
tests/test_eddm.py
```
