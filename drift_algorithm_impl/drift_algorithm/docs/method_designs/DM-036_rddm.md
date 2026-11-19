# DM-036 RDDM Design

## 1. Method Identity

- Method ID: `DM-036`
- Method name: `RDDM`
- Category: `SupervisedConceptDriftDetector`
- Method kind: `detector`
- Status: `확정`
- Source catalog: `drift_methods_catalog.md`
- Source variant document: `algorithm_variants/rddm_algorithm_variants.md`

## 2. Purpose

This method answers the drift question represented by `RDDM` in the
catalog. Primary input from the catalog: classification error stream.
Primary output from the catalog: warning state, drift state.

## 3. Supported Variants

- `RDDM_STANDARD`
- `RDDM_REACTIVE_RESET`

First implementation status:

- `RDDM_STANDARD` supports a precomputed binary error stream or derives errors
  from `y_true`/`y_pred`
- `RDDM_REACTIVE_RESET` uses the same RDDM state machine and records a reactive
  reset summary at the first drift alarm
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
- `max_concept_size`, `min_concept_size`
- `retention_policy`
- `reset_policy`
- `min_reference_size`, `min_current_size`
- `record_events`, `max_event_records`
- `sample_imbalance_warning_ratio`

## 6. Output Measurements

Return canonical measurements where applicable:

- `ADAPTATION_EVENT`
- `DRIFT_ALARM_STATE`
- `ERROR_RATE`
- `WARNING_STATE`
- `WINDOW_SIZE`

Always include `SAMPLE_SIZE` or relevant effective count metadata when the
method compares reference/current windows.

First implementation canonical mapping:

- `WARNING_STATE`: active warning state when no drift alarm has occurred
- `DRIFT_ALARM_STATE`: `normal` or `drift_detected`
- `WINDOW_SIZE`: retained window size
- `ADAPTATION_EVENT`: `drift_alarm_no_reset`, `reactive_reset`, or `None`
- `ERROR_RATE`: final RDDM error rate at the terminal state or first drift alarm

Additional measurements:

- `RETAINED_WINDOW_SIZE`
- `RDDM_STATISTIC`
- `STANDARD_DEVIATION`
- `WARNING_THRESHOLD`, `DRIFT_THRESHOLD`
- `RESET_EVENT`, `POST_RESET_ERROR_RATE`
- optional `RDDM_EVENTS`
- sample sizes and reference/current error-rate summaries

## 7. Algorithm Steps

1. Validate error-stream or label/prediction input.
2. Convert `time` to datetime, split reference/current windows, drop invalid
   timestamps or non-finite errors, and sort by time.
3. Derive a binary error stream from `error_col` or `y_true != y_pred`.
4. Replay reference and current rows chronologically.
5. Maintain an RDDM error-rate statistic with bounded concept history using
   `max_concept_size` and `min_concept_size`.
6. Mark warning/drift using DDM-style thresholds.
7. Retain the warning/recent window according to `retention_policy`.
8. For `RDDM_REACTIVE_RESET`, emit a reset event and post-reset error summary
   when drift is detected.
9. Return `DriftResult` with canonical measurement keys and interpretation
   text.

## 8. Drift Decision Rule

The first implementation uses the DDM-style RDDM rule:

```text
warning if p_i + s_i >= p_min + warning_level * s_min
drift   if p_i + s_i >= p_min + drift_level * s_min
```

The effective concept history is bounded by `max_concept_size`.

Defaults:

```text
warning_level = 2.0
drift_level = 3.0
min_num_instances = 30
min_concept_size = 30
max_concept_size = 1000
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
- invalid reset policy for the selected variant
- concept size settings where `min_concept_size > max_concept_size`

## 10. Implementation Target

```text
module: drift_algorithm.methods.supervisedconceptdriftdetector
function: detect_rddm
```

## 11. Verification Plan

Implemented tests:

- no-drift binary error stream
- drift-candidate binary error stream with retained window
- reactive reset behavior from `y_true`/`y_pred`
- validation and warning behavior
- non-scalar request rejection

Current test file:

```text
tests/test_rddm.py
```
