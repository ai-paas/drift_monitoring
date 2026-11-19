# DM-040 HDDM-W Design

## 1. Method Identity

- Method ID: `DM-040`
- Method name: `HDDM-W`
- Category: `SupervisedConceptDriftDetector`
- Method kind: `detector`
- Status: `확정`
- Source catalog: `drift_methods_catalog.md`
- Source variant document: `algorithm_variants/hddm_w_algorithm_variants.md`

## 2. Purpose

This method answers the drift question represented by `HDDM-W` in the
catalog. Primary input from the catalog: weighted error stream.
Primary output from the catalog: weighted Hoeffding alarm.

## 3. Supported Variants

- `HDDM_W_WEIGHTED_AVERAGE`
- `HDDM_W_WARNING_DRIFT`
- `HDDM_W_RECENT_ERROR_WEIGHTING`

First implementation status:

- all three variants support a precomputed binary error stream or derive errors
  from `y_true`/`y_pred`
- the implementation compares reference-window mean against a current
  recent-weighted mean
- weighted Hoeffding bounds use the effective sample size induced by `lambda`
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
- `lambda` or `lambda_value`
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

- `TEST_STATISTIC`: absolute weighted mean difference for two-sided mode,
  otherwise positive current-minus-reference weighted mean difference
- `P_VALUE`: `None`, because HDDM-W uses weighted Hoeffding confidence bounds
  rather than returning a frequentist p-value
- `DRIFT_ALARM_STATE`: `normal` or `drift_detected`

Additional measurements:

- `WEIGHTED_MEAN_DIFFERENCE`
- `REFERENCE_MEAN`, `WEIGHTED_CURRENT_MEAN`
- `EFFECTIVE_CURRENT_SAMPLE_SIZE`
- `HOEFFDING_WARNING_BOUND`, `HOEFFDING_DRIFT_BOUND`
- `CHANGE_DIRECTION`, `LAMBDA`
- `WARNING_STATE`
- `WARNING_START_TIME`, `DRIFT_TIME`
- optional `HDDM_W_EVENTS`
- sample sizes and reference/current error-rate summaries

## 7. Algorithm Steps

1. Validate error-stream or label/prediction input.
2. Convert `time` to datetime, split reference/current windows, drop invalid
   timestamps or non-finite errors, and sort by time.
3. Derive a binary error stream from `error_col` or `y_true != y_pred`.
4. Estimate the reference mean from the reference window.
5. Replay the current window chronologically.
6. Update the current recent-weighted mean with `lambda`.
7. Compute the effective sample size from the current weights.
8. Compute weighted Hoeffding warning and drift bounds.
9. Mark warning/drift when the effective weighted mean difference exceeds the
   corresponding bound.
10. Return `DriftResult` with canonical measurement keys and interpretation
    text.

## 8. Drift Decision Rule

The first implementation uses a recent-weighted Hoeffding rule:

```text
weighted_mean_i = lambda * error_i + (1 - lambda) * weighted_mean_(i-1)
diff_i = weighted_mean_i - mean(reference)
effective_diff_i = abs(diff_i) for two-sided mode, otherwise diff_i
n_eff_i = sum(weights)^2 / sum(weights^2)
bound(delta) = sqrt(log(1 / delta) / (2 * n_reference))
             + sqrt(log(1 / delta) / (2 * n_eff_i))
warning if effective_diff_i >= bound(warning_confidence / sides)
drift   if effective_diff_i >= bound(drift_confidence / sides)
```

Defaults:

```text
drift_confidence = 0.001
warning_confidence = 0.005
lambda = 0.2, or 0.3 for HDDM_W_RECENT_ERROR_WEIGHTING
two_sided = False
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
- invalid confidence, lambda, or two-sided parameter values
- current sample size below `min_instances`

## 10. Implementation Target

```text
module: drift_algorithm.methods.supervisedconceptdriftdetector
function: detect_hddm_w
```

## 11. Verification Plan

Implemented tests:

- no-drift binary error stream
- weighted warning/drift alarm from recent error increase
- recent-error weighting with two-sided decrease from `y_true`/`y_pred`
- validation and warning behavior
- non-scalar request rejection

Current test file:

```text
tests/test_hddm_w.py
```
