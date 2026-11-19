# DM-038 ECDD-WT Design

## 1. Method Identity

- Method ID: `DM-038`
- Method name: `ECDD-WT`
- Category: `SupervisedConceptDriftDetector`
- Method kind: `detector`
- Status: `확정`
- Source catalog: `drift_methods_catalog.md`
- Source variant document: `algorithm_variants/ecdd_wt_algorithm_variants.md`

## 2. Purpose

This method answers the drift question represented by `ECDD-WT` in the
catalog. Primary input from the catalog: classification error stream.
Primary output from the catalog: control statistic, warning/drift.

## 3. Supported Variants

- `ECDD_WT_STANDARD`
- `ECDD_WT_WARNING_DRIFT`
- `ECDD_WT_ERROR_STREAM`

First implementation status:

- all three variants support a precomputed binary error stream or derive errors
  from `y_true`/`y_pred`
- the first implementation estimates the baseline error rate from the reference
  window
- the ECDD-WT statistic is an EWMA error statistic standardized against the
  reference baseline
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
- `lambda` or `lambda_value`
- `warning_threshold`
- `drift_threshold` or `threshold_or_alpha`
- `min_instances`
- `error_definition`
- `min_reference_size`, `min_current_size`
- `variance_epsilon`
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

- `TEST_STATISTIC`: standardized ECDD-WT EWMA statistic
- `P_VALUE`: `None`, because ECDD-WT returns a detector score rather than a
  frequentist p-value
- `DRIFT_ALARM_STATE`: `normal` or `drift_detected`

Additional measurements:

- `EWMA_ERROR_STATISTIC`, `ECDD_WT_STATISTIC`
- `BASELINE_ERROR_RATE`, `ERROR_RATE`
- `WARNING_STATE`
- `WARNING_THRESHOLD`, `DRIFT_THRESHOLD`, `LAMBDA`
- `WARNING_START_TIME`, `DRIFT_TIME`
- optional `ECDD_WT_EVENTS`
- sample sizes and reference/current error-rate summaries

## 7. Algorithm Steps

1. Validate error-stream or label/prediction input.
2. Convert `time` to datetime, split reference/current windows, drop invalid
   timestamps or non-finite errors, and sort by time.
3. Derive a binary error stream from `error_col` or `y_true != y_pred`.
4. Estimate the baseline error rate from the reference window.
5. Replay reference and current rows chronologically.
6. Update the EWMA error statistic:
   `z_i = lambda * error_i + (1 - lambda) * z_(i-1)`.
7. Standardize the statistic against the reference baseline EWMA variance.
8. Compare the standardized statistic with warning/drift thresholds.
9. Return `DriftResult` with canonical measurement keys and interpretation
   text.

## 8. Drift Decision Rule

The first implementation uses a one-sided ECDD-WT rule for increased error:

```text
p0 = mean(reference_error)
z_i = lambda * error_i + (1 - lambda) * z_(i-1)
sigma_i = sqrt(p0 * (1 - p0) * lambda * (1 - (1 - lambda)^(2i)) / (2 - lambda))
statistic_i = (z_i - p0) / sigma_i
warning if statistic_i >= warning_threshold
drift   if statistic_i >= drift_threshold
```

Defaults:

```text
lambda = 0.2
warning_threshold = 2.0
drift_threshold = 3.0
min_instances = 30
error_definition = binary_misclassification
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
- invalid lambda or threshold values
- baseline error rate at 0 or 1, which requires variance clipping

## 10. Implementation Target

```text
module: drift_algorithm.methods.supervisedconceptdriftdetector
function: detect_ecdd_wt
```

## 11. Verification Plan

Implemented tests:

- no-drift binary error stream
- warning/drift alarm from an increased current error stream
- error stream derived from `y_true`/`y_pred`
- validation and warning behavior
- non-scalar request rejection

Current test file:

```text
tests/test_ecdd_wt.py
```
