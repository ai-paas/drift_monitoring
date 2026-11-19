# DM-035 DDM Design

## 1. Method Identity

- Method ID: `DM-035`
- Method name: `DDM`
- Category: `SupervisedConceptDriftDetector`
- Method kind: `detector`
- Status: `확정`
- Source catalog: `drift_methods_catalog.md`
- Source variant document: `algorithm_variants/ddm_algorithm_variants.md`

## 2. Purpose

This method answers the drift question represented by `DDM` in the
catalog. Primary input from the catalog: classification error stream.
Primary output from the catalog: warning state, drift state.

## 3. Supported Variants

- `DDM_STANDARD`
- `DDM_WARNING_BUFFER`
- `DDM_CLASS_SPECIFIC`

First implementation status:

- `DDM_STANDARD` supports a precomputed binary error stream or derives errors
  from `y_true`/`y_pred`
- `DDM_WARNING_BUFFER` uses the same DDM state machine and records warning
  period instances up to `max_buffer_size`
- `DDM_CLASS_SPECIFIC` filters rows by `class_label` using the true label and
  then runs the same DDM state machine
- feature, embedding, categorical-count, and unsupervised input contracts are
  not supported

## 4. Input Schema

Use the common `pandas.DataFrame` input boundary from
`../input_output_contracts.md`.

Required schema:

```text
label_schema.md. Required: `time` plus either a binary `error_col` /
`input_signal`, or `y_true`/`y_pred` columns.
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
- `min_num_instances`
- `buffer_policy`, `max_buffer_size`
- `class_label`
- `min_reference_size`, `min_current_size`
- `record_events`, `max_event_records`
- `sample_imbalance_warning_ratio`

## 6. Output Measurements

Return canonical measurements where applicable:

- `BUFFERED_INSTANCE_COUNT`
- `DRIFT_ALARM_STATE`
- `ERROR_RATE`
- `STANDARD_DEVIATION`
- `WARNING_STATE`

Always include `SAMPLE_SIZE` or relevant effective count metadata when the
method compares reference/current windows.

First implementation canonical mapping:

- `ERROR_RATE`: final DDM error rate at the terminal state or first drift alarm
- `STANDARD_DEVIATION`: final binomial standard deviation
- `WARNING_STATE`: active warning state when no drift alarm has occurred
- `DRIFT_ALARM_STATE`: `normal` or `drift_detected`
- `BUFFERED_INSTANCE_COUNT`: number of retained warning-period instances

Additional measurements:

- `DDM_STATISTIC`
- `WARNING_THRESHOLD`, `DRIFT_THRESHOLD`
- `ERROR_RATE_MIN`, `STANDARD_DEVIATION_MIN`
- warning/drift timing fields
- optional `DDM_EVENTS`
- optional `WARNING_BUFFER`
- class-specific fields for `DDM_CLASS_SPECIFIC`

## 7. Algorithm Steps

1. Validate error-stream or label/prediction input.
2. Convert `time` to datetime, split reference/current windows, drop invalid
   timestamps or non-finite errors, and sort by time.
3. Derive a binary error stream from `error_col` or `y_true != y_pred`.
4. For `DDM_CLASS_SPECIFIC`, filter rows to `class_label` before window checks.
5. Replay reference and current rows chronologically.
6. Maintain DDM error rate `p_i`, standard deviation `s_i`, and the historical
   minimum of `p_i + s_i` after `min_num_instances`.
7. Mark warning when `p_i + s_i >= p_min + warning_level * s_min`.
8. Mark drift when `p_i + s_i >= p_min + drift_level * s_min`.
9. Return `DriftResult` with canonical measurement keys and interpretation
   text.

## 8. Drift Decision Rule

The first implementation uses the standard DDM rule:

```text
warning if p_i + s_i >= p_min + warning_level * s_min
drift   if p_i + s_i >= p_min + drift_level * s_min
```

Defaults:

```text
warning_level = 2.0
drift_level = 3.0
min_num_instances = 30
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
- missing `class_label` for `DDM_CLASS_SPECIFIC`
- class-specific sample size below minimum support

## 10. Implementation Target

```text
module: drift_algorithm.methods.supervisedconceptdriftdetector
function: detect_ddm
```

## 11. Verification Plan

Implemented tests:

- no-drift binary error stream
- drift-candidate binary error stream
- warning-buffer behavior from `y_true`/`y_pred`
- class-specific DDM behavior
- validation and warning behavior

Current test file:

```text
tests/test_ddm.py
```
