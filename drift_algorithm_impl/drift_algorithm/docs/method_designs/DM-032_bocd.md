# DM-032 BOCD Design

## 1. Method Identity

- Method ID: `DM-032`
- Method name: `BOCD`
- Category: `StreamingChangeDetector`
- Method kind: `detector`
- Status: `확정`
- Source catalog: `drift_methods_catalog.md`
- Source variant document: `algorithm_variants/bocd_algorithm_variants.md`

## 2. Purpose

This method answers the drift question represented by `BOCD` in the
catalog. Primary input from the catalog: numeric stream, probabilistic time series.
Primary output from the catalog: change point probability.

## 3. Supported Variants

- `BAYESIAN_ONLINE_CHANGE_POINT_GAUSSIAN`
- `BOCD_HAZARD_RATE_VARIANT`
- `BOCD_PREDICTIVE_PROBABILITY`

First implementation status:

- supported for scalar numeric finite replay over `(time, value)`
- `BAYESIAN_ONLINE_CHANGE_POINT_GAUSSIAN` is the default variant
- `BOCD_HAZARD_RATE_VARIANT` uses the same Gaussian BOCD engine with explicit
  `hazard_rate` or `expected_run_length`
- `BOCD_PREDICTIVE_PROBABILITY` uses the same posterior engine and can add a
  low predictive probability alarm through `predictive_probability_threshold`
- multivariate, embedding, categorical, count, and supervised label/error
  contracts are not supported in the first implementation

## 4. Input Schema

Use the common `pandas.DataFrame` input boundary from
`../input_output_contracts.md`.

Required first implementation schema:

```text
numeric_schema.md. Required: `time` plus numeric `value` unless `value_col` or
params["input_signal"] supplies another scalar numeric column.
```

The implementation must validate the concrete columns through `params` and
return `severity="not_applicable"` if the supplied schema cannot represent this
method's required input.

## 5. Parameters

Method-specific parameters come from `drift_method_parameter_guide.md` and the
variant source document. The implementation should at minimum support:

- `change_probability_threshold`, `threshold`, or `threshold_or_alpha`
- `hazard_rate` or `expected_run_length`
- `predictive_probability_threshold`
- `run_length_truncation`
- `short_run_length`
- `prior_mean`, `prior_kappa`, `prior_alpha`, `prior_beta`
- `warmup_size`, `check_every`
- `min_reference_size`, `min_current_size`, `min_stream_size`
- `record_events`, `max_event_records`
- `sample_imbalance_warning_ratio`

Default prior policy:

- if `prior_mean` or `prior_beta` is omitted, calibrate the Gaussian
  Normal-Inverse-Gamma prior from the effective reference window
- `prior_kappa=1.0`
- `prior_alpha=2.0`
- `prior_beta=reference_variance * (prior_alpha - 1)` when omitted

## 6. Output Measurements

Return canonical measurements where applicable:

- `DRIFT_ALARM_STATE`
- `P_VALUE`
- `TEST_STATISTIC`

First implementation canonical mapping:

- `TEST_STATISTIC`: maximum short-run posterior mass
- `P_VALUE`: `None`; BOCD does not return a frequentist p-value
- `DRIFT_ALARM_STATE`: `normal` or `drift_detected`

Additional measurements:

- `CHANGE_POINT_PROBABILITY`
- `MAX_CHANGE_POINT_PROBABILITY`
- `FINAL_RUN_LENGTH_MAP`
- `FINAL_RUN_LENGTH_EXPECTED`
- `LAST_PREDICTIVE_PROBABILITY`
- `MIN_PREDICTIVE_PROBABILITY`
- `ALARM_COUNT`, alarm timing fields, and optional `ALARM_EVENTS`
- `SAMPLE_SIZE`, `SAMPLE_SIZE_REFERENCE`, `SAMPLE_SIZE_CURRENT`

## 7. Algorithm Steps

1. Validate the scalar numeric input request.
2. Convert `time` to datetime, split reference/current windows, drop invalid
   timestamps or non-finite values, and sort by time.
3. Concatenate reference/current rows as a finite chronological replay stream.
4. Calibrate a Gaussian Normal-Inverse-Gamma prior from the reference window
   unless explicit prior parameters are supplied.
5. Run a log-space Bayesian online change point update with Student-t
   predictive likelihood.
6. Use posterior mass for run lengths `0..short_run_length` as the operational
   change probability score.
7. Raise an alarm when the score is greater than
   `change_probability_threshold`.
8. For `BOCD_PREDICTIVE_PROBABILITY`, also raise a warning-style alarm when
   predictive probability is below `predictive_probability_threshold`.
9. Return `DriftResult` with canonical measurement keys and interpretation
   text.

## 8. Drift Decision Rule

The first implementation uses:

```text
MAX_CHANGE_POINT_PROBABILITY > change_probability_threshold
```

where `MAX_CHANGE_POINT_PROBABILITY` is the maximum posterior mass assigned to
short run lengths `0..short_run_length` after warmup. This avoids treating the
constant-hazard `run_length=0` posterior alone as the alarm score.

For `BOCD_PREDICTIVE_PROBABILITY`, an additional alarm condition is:

```text
predictive_probability < predictive_probability_threshold
```

when `predictive_probability_threshold` is supplied.

## 9. Warnings and Not-Applicable Conditions

Return warnings for:

- missing required columns
- empty reference/current windows
- sample size below method minimum
- unsupported variant id
- numerical instability such as singular covariance or zero-probability bins
- label-dependent methods called without labels or error stream
- high or low hazard settings that may increase false alarms or delay detection
- reference-window prior calibration

## 10. Implementation Target

```text
module: drift_algorithm.methods.streamingchangedetector
function: detect_bocd
```

## 11. Verification Plan

Implemented tests:

- no-drift synthetic data with similar reference/current windows
- Gaussian mean-shift synthetic data that triggers a posterior alarm
- hazard-rate and predictive-probability variant behavior
- schema, window, warning, and validation behavior
- non-scalar request rejection

Current test file:

```text
tests/test_bocd.py
```
