# DM-039 HDDM-A Design

## 1. Method Identity

- Method ID: `DM-039`
- Method name: `HDDM-A`
- Category: `SupervisedConceptDriftDetector`
- Method kind: `detector`
- Status: `확정`
- Source catalog: `drift_methods_catalog.md`
- Source variant document: `algorithm_variants/hddm_a_algorithm_variants.md`

## 2. Purpose

This method answers the drift question represented by `HDDM-A` in the
catalog. Primary input from the catalog: classification error stream.
Primary output from the catalog: Hoeffding-bound alarm.

## 3. Supported Variants

- `HDDM_A_HOEFFDING_BOUND`
- `HDDM_A_WARNING_DRIFT`
- `HDDM_A_TWO_SIDED`

First implementation status:

- all three variants support a precomputed binary error stream or derive errors
  from `y_true`/`y_pred`
- `HDDM_A_HOEFFDING_BOUND` and `HDDM_A_WARNING_DRIFT` monitor increasing error
  mean shifts
- `HDDM_A_TWO_SIDED` monitors both increasing and decreasing binary mean shifts
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
- `drift_confidence` or `threshold_or_alpha`
- `warning_confidence`
- `two_sided`
- `min_instances`
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

- `TEST_STATISTIC`: absolute mean difference for two-sided mode, otherwise
  positive current-minus-reference mean difference
- `P_VALUE`: `None`, because HDDM-A uses Hoeffding confidence bounds rather
  than returning a frequentist p-value
- `DRIFT_ALARM_STATE`: `normal` or `drift_detected`

Additional measurements:

- `MEAN_DIFFERENCE`
- `REFERENCE_MEAN`, `CURRENT_PREFIX_MEAN`
- `HOEFFDING_WARNING_BOUND`, `HOEFFDING_DRIFT_BOUND`
- `CHANGE_DIRECTION`
- `WARNING_STATE`
- `WARNING_START_TIME`, `DRIFT_TIME`
- optional `HDDM_A_EVENTS`
- sample sizes and reference/current error-rate summaries

## 7. Algorithm Steps

1. Validate error-stream or label/prediction input.
2. Convert `time` to datetime, split reference/current windows, drop invalid
   timestamps or non-finite errors, and sort by time.
3. Derive a binary error stream from `error_col` or `y_true != y_pred`.
4. Estimate the reference mean from the reference window.
5. Replay the current window as chronological prefixes.
6. Compare each current prefix mean with the reference mean.
7. Compute Hoeffding warning and drift bounds from the reference and current
   prefix sample sizes.
8. Mark warning/drift when the effective mean difference exceeds the
   corresponding bound.
9. Return `DriftResult` with canonical measurement keys and interpretation
   text.

## 8. Drift Decision Rule

The first implementation uses a reference-vs-current-prefix Hoeffding rule:

```text
diff_i = mean(current_prefix_i) - mean(reference)
effective_diff_i = abs(diff_i) for two-sided mode, otherwise diff_i
bound(delta) = sqrt(log(1 / delta) / (2 * n_reference))
             + sqrt(log(1 / delta) / (2 * n_current_prefix))
warning if effective_diff_i >= bound(warning_confidence / sides)
drift   if effective_diff_i >= bound(drift_confidence / sides)
```

Defaults:

```text
drift_confidence = 0.001
warning_confidence = 0.005
two_sided = False except for HDDM_A_TWO_SIDED
min_instances = 30
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
- invalid confidence or two-sided parameter values
- current sample size below `min_instances`

## 10. Implementation Target

```text
module: drift_algorithm.methods.supervisedconceptdriftdetector
function: detect_hddm_a
```

## 11. Verification Plan

Implemented tests:

- no-drift binary error stream
- one-sided warning/drift alarm from increased current error stream
- two-sided decrease alarm from `y_true`/`y_pred`
- validation and warning behavior
- non-scalar request rejection

Current test file:

```text
tests/test_hddm_a.py
```
