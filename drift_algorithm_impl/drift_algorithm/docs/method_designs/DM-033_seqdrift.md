# DM-033 SeqDrift Design

## 1. Method Identity

- Method ID: `DM-033`
- Method name: `SeqDrift`
- Category: `StreamingChangeDetector`
- Method kind: `detector`
- Status: `확정`
- Source catalog: `drift_methods_catalog.md`
- Source variant document: `algorithm_variants/seqdrift_algorithm_variants.md`

## 2. Purpose

This method answers the drift question represented by `SeqDrift` in the
catalog. Primary input from the catalog: numeric stream, error stream.
Primary output from the catalog: sequential bound, alarm.

## 3. Supported Variants

- `SEQDRIFT1`
- `SEQDRIFT2`

First implementation status:

- supported for scalar numeric finite replay over `(time, value)`
- `SEQDRIFT1` uses the full effective reference window as the baseline
- `SEQDRIFT2` uses deterministic reservoir sampling for the reference baseline
  when `reservoir_size` is smaller than the reference window
- raw `y_true`/`y_pred` error-stream construction is deferred until an explicit
  label/error stream contract is approved
- multivariate, embedding, categorical, and count contracts are not supported
  in the first implementation

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

- `delta` or `threshold_or_alpha`
- `block_size`
- `reservoir_size`
- `sampling_policy`
- `bound_type`
- `random_seed`
- `value_min`, `value_max`
- `min_reference_size`, `min_current_size`
- `record_events`, `max_event_records`
- `sample_imbalance_warning_ratio`

## 6. Output Measurements

Return canonical measurements where applicable:

- `DRIFT_ALARM_STATE`
- `METHOD_POLICY`
- `SEQUENTIAL_BOUND`

First implementation canonical mapping:

- `SEQUENTIAL_BOUND`: the bound that was crossed, or the last checked bound
  when no alarm is raised
- `DRIFT_ALARM_STATE`: `normal` or `drift_detected`
- `METHOD_POLICY`: variant, bound type, sampling policy, block size, reservoir
  size, and random seed

Additional measurements:

- `TEST_STATISTIC`: maximum observed mean-difference evidence
- `P_VALUE`: `None`; SeqDrift is implemented as a sequential-bound detector
- `DRIFT_SCORE`: maximum evidence-minus-bound margin
- `MAX_EVIDENCE`, `MAX_MARGIN`, `LAST_EVIDENCE`, `LAST_BOUND`
- `ALARM_COUNT`, alarm timing fields, and optional `ALARM_EVENTS`
- `SAMPLE_SIZE`, `SAMPLE_SIZE_REFERENCE`, `SAMPLE_SIZE_CURRENT`

## 7. Algorithm Steps

1. Validate the scalar numeric input request.
2. Convert `time` to datetime, split reference/current windows, drop invalid
   timestamps or non-finite values, and sort by time.
3. Use the effective reference window as the baseline for `SEQDRIFT1`.
4. Use deterministic reservoir sampling for the reference baseline for
   `SEQDRIFT2` unless `sampling_policy="exact"` is explicitly supplied.
5. Iterate current-window prefixes at `block_size` intervals.
6. Compare the absolute mean difference between the reference baseline and each
   current prefix with a Hoeffding-style sequential bound.
7. Raise an alarm when evidence is greater than the bound.
8. Return `DriftResult` with canonical measurement keys and interpretation
   text.

## 8. Drift Decision Rule

The first implementation uses:

```text
abs(current_prefix_mean - reference_mean) > sequential_bound
```

where:

```text
sequential_bound =
  value_range * sqrt(0.5 * log(2 / delta) * (1 / reference_n + 1 / current_prefix_n))
```

`value_range` is supplied by `value_min`/`value_max` when available, otherwise
it is inferred from the effective reference/current values.

## 9. Warnings and Not-Applicable Conditions

Return warnings for:

- missing required columns
- empty reference/current windows
- sample size below method minimum
- unsupported variant id
- numerical instability such as singular covariance or zero-probability bins
- label-dependent methods called without labels or error stream
- `SEQDRIFT1` requested with reservoir sampling
- raw labels/predictions supplied before the error-stream contract is approved
- non-positive value range

## 10. Implementation Target

```text
module: drift_algorithm.methods.streamingchangedetector
function: detect_seqdrift
```

## 11. Verification Plan

Implemented tests:

- no-drift synthetic data with similar reference/current windows
- mean-shift synthetic data that triggers a sequential-bound alarm
- `SEQDRIFT2` reservoir policy and threshold alias behavior
- validation and warning behavior
- non-scalar request rejection

Current test file:

```text
tests/test_seqdrift.py
```
