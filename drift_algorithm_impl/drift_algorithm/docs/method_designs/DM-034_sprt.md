# DM-034 SPRT Design

## 1. Method Identity

- Method ID: `DM-034`
- Method name: `SPRT`
- Category: `StreamingChangeDetector`
- Method kind: `detector`
- Status: `확정`
- Source catalog: `drift_methods_catalog.md`
- Source variant document: `algorithm_variants/sprt_algorithm_variants.md`

## 2. Purpose

This method answers the drift question represented by `SPRT` in the
catalog. Primary input from the catalog: Bernoulli 또는 numeric stream.
Primary output from the catalog: likelihood ratio decision.

## 3. Supported Variants

- `SPRT_BERNOULLI_ERROR_RATE`
- `SPRT_GAUSSIAN_MEAN_SHIFT`

## 4. Input Schema

Use the common `pandas.DataFrame` input boundary from
`../input_output_contracts.md`.

Implemented schemas:

```text
1. Bernoulli error stream schema
   Required: `time`, `error_col` or numeric `value_col`
   Values must be 0/1.
   Used by:
   - SPRT_BERNOULLI_ERROR_RATE

2. Gaussian numeric stream schema
   Required: `time`, numeric `value_col`
   Used by:
   - SPRT_GAUSSIAN_MEAN_SHIFT
```

The implementation must validate the concrete columns through `params` and
return `severity="not_applicable"` if the supplied schema cannot represent this
method's required input.

## 5. Parameters

Implemented parameters:

- `variant_id`: defaults to `SPRT_BERNOULLI_ERROR_RATE`
- `alpha` or `threshold_or_alpha`: type-I error setting, default `0.05`
- `beta`: type-II error setting, default `0.1`
- `upper_boundary`: optional H1 log-likelihood boundary, default
  `log((1 - beta) / alpha)`
- `lower_boundary`: optional H0 log-likelihood boundary, default
  `log(beta / (1 - alpha))`
- `check_every`: boundary check interval, default `1`
- `reset_policy`: `stop_after_decision` or `continue`, default
  `stop_after_decision`
- `error_col`: Bernoulli 0/1 stream column for `SPRT_BERNOULLI_ERROR_RATE`
- `p0`, `p1`: null and alternative Bernoulli error rates, with `p1 > p0`
- `mu0`, `mu1` or `mean_shift`: null and alternative Gaussian means
- `sigma` or `std`: Gaussian standard deviation; if omitted, reference-window
  standard deviation is used
- `min_reference_size`, `min_current_size`: effective sample-size guards
- `record_events`, `max_event_records`: decision event recording controls

## 6. Output Measurements

Return canonical measurements where applicable:

- `CONTROL_LIMIT`
- `HYPOTHESIS_DECISION_STATE`
- `LOG_LIKELIHOOD_RATIO`
- `SEQUENTIAL_BOUND`
- `DRIFT_ALARM_STATE`
- `ALARM_COUNT`
- `DECISION_COUNT`
- `FIRST_ALARM_TIME`
- `LAST_ALARM_TIME`

Always include `SAMPLE_SIZE` or relevant effective count metadata when the
method compares reference/current windows.

## 7. Algorithm Steps

1. Validate the variant, alpha/beta, boundaries, and selected stream schema.
2. Split reference/current windows and clean numeric rows.
3. Use the reference window for validation and optional Gaussian sigma
   calibration.
4. Replay only the current window as the sequential SPRT stream.
5. Accumulate log-likelihood ratio under H1 versus H0.
6. At `check_every` intervals, compare the LLR with the lower/upper boundary.
7. Return H0/H1/continue decision state, LLR, boundaries, alarm events, and
   sample-size metadata.

## 8. Drift Decision Rule

This implementation does not produce a p-value.

- `LLR >= upper_boundary`: accept H1 and set `drift_detected=True`
- `LLR <= lower_boundary`: accept H0 and set `drift_detected=False`
- neither boundary reached: `drift_detected=False`, severity `watch`, alarm
  state `undetermined`
- with `reset_policy="continue"`, any H1 decision in the current stream sets
  `drift_detected=True`

## 9. Warnings and Not-Applicable Conditions

Return warnings for:

- missing required columns
- empty reference/current windows
- sample size below method minimum
- unsupported variant id
- invalid alpha/beta or boundary order
- Bernoulli stream values outside 0/1
- `p1 <= p0` for Bernoulli error-rate SPRT
- missing Gaussian `sigma` when reference standard deviation is not positive
- raw labels/predictions without a precomputed Bernoulli error stream

## 10. Implementation Target

```text
module: drift_algorithm.methods.streamingchangedetector
function: detect_sprt
```

## 11. Verification Plan

Implemented tests:

```text
tests/test_sprt.py
```

Coverage:

1. Bernoulli SPRT accepts H0 under stable error rate
2. Bernoulli SPRT accepts H1 under error-rate increase
3. Gaussian SPRT accepts H1 under mean shift
4. continue reset policy records H1 decision events
5. validation and cleaning warnings
