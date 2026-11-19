# DM-041 STEPD Design

## 1. Method Identity

- Method ID: `DM-041`
- Method name: `STEPD`
- Category: `SupervisedConceptDriftDetector`
- Method kind: `detector`
- Status: `확정`
- Source catalog: `drift_methods_catalog.md`
- Source variant document: `algorithm_variants/stepd_algorithm_variants.md`

## 2. Purpose

This method answers the drift question represented by `STEPD` in the
catalog. Primary input from the catalog: recent/overall accuracy window.
Primary output from the catalog: warning state, drift state.

## 3. Supported Variants

- `STEPD_ACCURACY_WINDOW`
- `STEPD_WARNING_DRIFT`
- `STEPD_SUPERVISED_STREAM`

First implementation status:

- all three variants support a precomputed binary error stream or derive errors
  from `y_true`/`y_pred`
- the implementation compares reference-window accuracy against rolling
  current-window accuracy
- warning and drift states are separated by `alpha_warning` and `alpha_drift`
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
- `alpha_drift` or `threshold_or_alpha`
- `alpha_warning`
- `window_size`
- `min_instances`
- `accuracy_definition`
- `step_size`
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

- `TEST_STATISTIC`: one-sided z statistic for reference accuracy being higher
  than current rolling-window accuracy
- `P_VALUE`: one-sided normal-approximation p-value
- `DRIFT_ALARM_STATE`: `normal` or `drift_detected`

Additional measurements:

- `REFERENCE_ACCURACY`, `CURRENT_WINDOW_ACCURACY`
- `ACCURACY_DELTA`
- `WINDOW_SIZE`
- `ALPHA_WARNING`, `ALPHA_DRIFT`
- `WARNING_STATE`
- `WARNING_START_TIME`, `DRIFT_TIME`
- optional `STEPD_EVENTS`
- sample sizes and reference/current error-rate summaries

## 7. Algorithm Steps

1. Validate error-stream or label/prediction input.
2. Convert `time` to datetime, split reference/current windows, drop invalid
   timestamps or non-finite errors, and sort by time.
3. Derive a binary error stream from `error_col` or `y_true != y_pred`.
4. Convert error to accuracy as `1 - error`.
5. Estimate reference accuracy from the reference window.
6. Replay the current window as rolling accuracy windows.
7. Run a one-sided two-proportion z test for current accuracy degradation.
8. Mark warning/drift by comparing the p-value with `alpha_warning` and
   `alpha_drift`.
9. Return `DriftResult` with canonical measurement keys and interpretation
   text.

## 8. Drift Decision Rule

The first implementation uses a one-sided rolling-window accuracy test:

```text
ref_acc = mean(1 - reference_error)
cur_acc_i = mean(1 - current_error_window_i)
z_i = (ref_acc - cur_acc_i) / pooled_standard_error
p_i = P(Z >= z_i)
warning if p_i <= alpha_warning and cur_acc_i < ref_acc
drift   if p_i <= alpha_drift and cur_acc_i < ref_acc
```

Defaults:

```text
alpha_drift = 0.01
alpha_warning = 0.05
window_size = 30
min_instances = window_size
accuracy_definition = 1_minus_binary_error
step_size = 1
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
- invalid alpha or window parameter values
- current sample size below `min_instances`

## 10. Implementation Target

```text
module: drift_algorithm.methods.supervisedconceptdriftdetector
function: detect_stepd
```

## 11. Verification Plan

Implemented tests:

- no-drift binary error stream
- warning/drift alarm from recent accuracy degradation
- supervised stream from `y_true`/`y_pred`
- validation and warning behavior
- non-scalar request rejection

Current test file:

```text
tests/test_stepd.py
```
