# DM-030 EWMA Design

## 1. Method Identity

- Method ID: `DM-030`
- Method name: `EWMA`
- Category: `StreamingChangeDetector`
- Method kind: `detector`
- Status: `확정`
- Source catalog: `drift_methods_catalog.md`
- Source variant document: `algorithm_variants/ewma_algorithm_variants.md`
- Source parameter tables:
  - `drift_method_variant_links.csv`
  - `drift_method_variant_measurement_summary.csv`
  - `drift_method_variant_parameters.csv`
  - `drift_method_parameter_guide.md`

The first implementation is a univariate numeric exponentially weighted
moving average control chart executed over a finite DataFrame slice. It
accepts the common `(time, value)` pandas DataFrame contract, sorts rows by
time, slices the supplied reference/current timestamp windows, calibrates the
center line and control limits from the reference window unless explicit
parameters are supplied, concatenates the two slices in time order, and
replays the values through an EWMA state machine.

## 2. Purpose

`EWMA` monitors whether an exponentially weighted moving average of a scalar
numeric metric moves outside a control limit. It is a sequential control-chart
detector for gradual mean movement, not a two-sample distribution test and not
a p-value test.

The catalog input is `numeric metric stream`; the catalog output is `EWMA
value, control limit, alarm`. The first implementation narrows that catalog
scope to scalar numeric `(time, value)` rows because the public API receives
finite DataFrame windows, not an unbounded online iterator. It should be read
as:

```text
Replay the selected reference/current rows as a time-ordered numeric stream and
report whether the EWMA statistic crossed its configured control limit during
that replay.
```

Use the first implementation when:

- the monitored signal is one scalar numeric metric
- the caller can provide timestamp ranges for `reference_window` and
  `current_window`
- the operational question is whether a sequential EWMA control chart would
  alarm while processing those rows in chronological order
- small sustained shifts matter more than one-off spikes
- direction matters: upward for loss, error rate, latency, reject rate, or
  other "larger is worse" metrics; downward for confidence, throughput, recall,
  acceptance rate, or other "smaller is worse" metrics
- EWMA value, center line, upper/lower control limits, smoothing factor, and
  alarm history are useful monitoring outputs

Do not use the first implementation for categorical labels, count tables,
probability vectors, raw embeddings, multivariate feature matrices, text, SHAP
matrices, raw supervised prediction pairs, or retraining policy decisions.
Those require another method family or a future contract.

## 3. Supported Variants

Supported for the first implementation:

- `EWMA_UNIVARIATE_CONTROL_CHART`
  - Default variant.
  - Detects sustained movement in either direction from the center line.
  - Uses chronological replay of the selected reference/current rows.
  - Raises an alarm when EWMA exceeds `ucl` or falls below `lcl`.
- `EWMA_ONE_SIDED`
  - Detects sustained movement only in the configured risk direction.
  - Uses `direction="increase"` for upper-limit monitoring or
    `direction="decrease"` for lower-limit monitoring.
  - Raises an alarm only when the monitored one-sided limit is crossed.

Deferred until separate calibration policy is approved:

- `EWMA_BASELINE_REPLAY_THRESHOLD`
  - Requires a documented baseline replay/calibration period, empirical
    quantile policy, target false alarm rate, and separation between threshold
    calibration data and evaluated current data.
  - Must not silently approximate empirical thresholds from the same current
    rows being evaluated.
  - In the first implementation, return `severity="not_applicable"` unless
    this empirical threshold contract is explicitly implemented.
- Multivariate EWMA:
  - Belongs to DM-043 MEWMA or another multivariate method, not DM-030.
  - Must not average feature columns or build a vector statistic inside
    `detect_ewma`.
- Supervised error-rate EWMA:
  - Requires an explicit label/error schema, `error_col` or `y_true`/`y_pred`
    handling, label-delay policy, and error definition.
  - Must not infer performance drift from arbitrary numeric `value` rows.

Default variant selection:

```text
if params["variant_id"] is omitted:
    variant_id = "EWMA_UNIVARIATE_CONTROL_CHART"
```

## 4. Input Schema

Use the common `pandas.DataFrame` input boundary from
`../input_output_contracts.md`.

Public function shape:

```python
def detect_ewma(
    data: pd.DataFrame,
    *,
    time_col: str = "time",
    value_col: str | None = "value",
    reference_window: tuple[str, str] | None = None,
    current_window: tuple[str, str] | None = None,
    params: dict | None = None,
) -> DriftResult:
    ...
```

Required DataFrame schema for supported first-scope variants:

```text
time: datetime64[ns] or parseable timestamp
value: numeric integer or floating scalar dtype
```

The caller may override column names with `time_col` and `value_col`. If
`value_col is None`, resolve the numeric value column from
`params["input_signal"]`. The resolved value column must contain scalar numeric
values, not arrays, objects, strings, categories, booleans, labels,
probability vectors, or embeddings.

Window contract:

```text
reference_window: inclusive (start_timestamp, end_timestamp)
current_window: inclusive (start_timestamp, end_timestamp)
```

Although EWMA is a streaming control chart, the first public API still
requires both windows. They define the finite replay scope and, when control
parameters are omitted, the reference window supplies the baseline center and
standard deviation:

1. Convert `time_col` with `pd.to_datetime(..., errors="coerce")`.
2. Convert the value column with `pd.to_numeric(..., errors="coerce")`.
3. Sort by `time_col`.
4. Slice inclusive reference/current windows.
5. Reject overlapping windows unless an explicit overlap policy is added
   later.
6. Drop rows with invalid timestamps or non-finite values.
7. Resolve `center_line` and `sigma` from the effective reference slice when
   omitted.
8. Resolve theoretical or explicit control limits.
9. Concatenate the effective reference/current rows and sort by `time_col`.
10. Iterate the effective rows in time order.

Minimum effective sample sizes:

```text
EWMA_UNIVARIATE_CONTROL_CHART and EWMA_ONE_SIDED:
  min_reference_size: default 20
  min_current_size: default 20
  warmup_size: default 20
```

If either effective DataFrame window is below its minimum, or if the combined
finite replay stream is below `warmup_size`, return
`severity="not_applicable"` and do not run the detector.

## 5. Parameters

Accepted `params` keys and defaults for the first implementation:

| Param | Type | Default | Applies to | Meaning |
|---|---:|---:|---|---|
| `variant_id` | string | `EWMA_UNIVARIATE_CONTROL_CHART` | all | Variant selector. |
| `lambda` | float | `0.2` | supported variants | EWMA smoothing factor. Must be `0 < lambda <= 1`. Larger values react faster to recent values. |
| `center_line` | float | reference mean | supported variants | Baseline center used by the EWMA recurrence and control limits. |
| `sigma` | float | reference sample std | supported variants | Baseline standard deviation used for theoretical control limits. Must be non-negative. |
| `control_width` | float | `3.0` | supported variants | Width multiplier for theoretical control limits. Must be positive. |
| `ucl` | float | computed | supported variants | Explicit upper control limit. |
| `lcl` | float | computed | supported variants | Explicit lower control limit. |
| `threshold` | float | optional | `EWMA_ONE_SIDED` | Compatibility alias for the monitored one-sided control limit. |
| `threshold_or_alpha` | float | optional | supported variants | Compatibility alias for `control_width` only when no explicit limit is supplied; must not be treated as a p-value alpha. |
| `direction` | string | `both` or inferred | supported variants | `both`, `increase`, or `decrease`; must match the selected variant. |
| `direction_or_alternative` | string | optional | `EWMA_ONE_SIDED` | Compatibility alias for `direction`. |
| `warmup_size` | int | `20` | supported variants | Minimum replay length before alarms are evaluated. |
| `check_every` | int | `1` | supported variants | Check interval in processed observations after `warmup_size`. |
| `reset_policy` | string | `none` | supported variants | State handling after alarm. First implementation supports `none`; `after_alarm` is deferred unless explicitly implemented. |
| `input_signal` | string | optional | supported variants | Value column name only when `value_col is None`; otherwise metadata label such as `loss`, `latency`, `confidence`, or `score`. |
| `min_reference_size` | int | `20` | supported variants | Minimum effective reference rows after invalid rows are dropped. |
| `min_current_size` | int | `20` | supported variants | Minimum effective current rows after invalid rows are dropped. |
| `nan_policy` | string | `drop` | supported variants | First implementation supports `drop`/`omit` only. |
| `record_events` | bool | `True` | supported variants | Include compact alarm event history in measurements. |
| `max_event_records` | int | `50` | supported variants | Maximum number of alarm events retained in measurements. |
| `sample_imbalance_warning_ratio` | float | `10.0` | supported variants | Warn when larger input window size divided by smaller size exceeds this ratio. |
| `baseline_replay_period` | any | none | deferred empirical variant | Not supported in first implementation except for explicit not-applicable reporting. |
| `empirical_quantile` | float | none | deferred empirical variant | Not supported in first implementation except for explicit not-applicable reporting. |
| `target_false_alarm_rate` | float | none | deferred empirical variant | Not supported in first implementation except for explicit not-applicable reporting. |

Parameter rules:

- `lambda` is the smoothing factor. It is not a reserved word in `params`, but
  implementation helpers should avoid using `lambda` as a Python variable name.
- `center_line`, when omitted, is computed from the effective reference window
  after invalid rows are dropped. Current rows must not be used to set it.
- `sigma`, when omitted, is computed from the effective reference sample
  standard deviation. If it is zero, theoretical limits collapse to the center
  line unless explicit `ucl`/`lcl` are supplied; return not applicable or warn
  according to the implemented zero-variance policy.
- The default two-sided theoretical limits are:

```text
steady_state_sigma_ewma = sigma * sqrt(lambda / (2 - lambda))
ucl = center_line + control_width * steady_state_sigma_ewma
lcl = center_line - control_width * steady_state_sigma_ewma
```

- Time-varying startup limits may be added later, but the first implementation
  should use the steady-state limit above for deterministic finite replay.
- `threshold_or_alpha` is accepted only as a compatibility alias for
  `control_width` when `control_width`, `ucl`, `lcl`, and `threshold` are not
  supplied. It must not be interpreted as a p-value alpha.
- For `EWMA_ONE_SIDED`, `threshold` maps to the monitored limit: upper limit
  for `direction="increase"` and lower limit for `direction="decrease"`.
- `direction` must be `both` for `EWMA_UNIVARIATE_CONTROL_CHART`,
  `increase` or `decrease` for `EWMA_ONE_SIDED`.
- `direction_or_alternative` accepts `up`/`greater` as `increase`,
  `down`/`less` as `decrease`, and `two-sided`/`both` as `both`.
- `warmup_size`, `check_every`, `min_reference_size`, `min_current_size`, and
  `max_event_records` must be positive integers.
- `reset_policy="none"` leaves the EWMA recurrence unchanged after an alarm.
  Other reset policies are deferred because resetting a smoothed average
  changes the control-chart interpretation.
- `nan_policy` supports `drop` and `omit` as aliases for dropping invalid rows.
  Other values return `not_applicable`.
- Reject or warn on unrelated params such as `feature_cols`, `embedding_cols`,
  `category_col`, `count_col`, raw label columns, classifier settings,
  distance-stream settings, or preprocessing functions.

## 6. EWMA Statistic and State Policy

Normalize the selected finite stream to one-dimensional arrays:

```python
stream_values = np.asarray(..., dtype=float)
stream_times = np.asarray(..., dtype="datetime64[ns]")
```

For observation `x_t`, center line `mu0`, smoothing factor `lambda`, and prior
EWMA value `z_{t-1}`, maintain:

```text
z_0 = center_line
z_t = lambda * x_t + (1 - lambda) * z_{t-1}
```

Control limit behavior:

```text
EWMA_UNIVARIATE_CONTROL_CHART:
  upper alarm if z_t > ucl
  lower alarm if z_t < lcl

EWMA_ONE_SIDED with direction="increase":
  upper alarm if z_t > ucl

EWMA_ONE_SIDED with direction="decrease":
  lower alarm if z_t < lcl
```

Implementation-level pseudocode:

```text
events = []
ewma = center_line
max_ewma = center_line
min_ewma = center_line
max_upper_excess = 0
max_lower_excess = 0

for index, (time, value) in chronological stream:
    ewma = lambda * value + (1 - lambda) * ewma
    max_ewma = max(max_ewma, ewma)
    min_ewma = min(min_ewma, ewma)
    upper_excess = ewma - ucl
    lower_excess = lcl - ewma
    max_upper_excess = max(max_upper_excess, upper_excess)
    max_lower_excess = max(max_lower_excess, lower_excess)

    if index + 1 < warmup_size:
        continue
    if (index + 1 - warmup_size) % check_every != 0:
        continue

    if variant monitors upper and ewma > ucl:
        record upper alarm event

    if variant monitors lower and ewma < lcl:
        record lower alarm event
```

The first implementation should use a deterministic NumPy/Pandas
implementation. It does not require SciPy or network-installed streaming
libraries. The design does not require a top-level p-value. Do not label the
EWMA statistic as `P_VALUE`.

## 7. Output Measurements

`drift_method_variant_measurement_summary.csv` maps DM-030 variants to:

```text
EWMA_UNIVARIATE_CONTROL_CHART: EWMA_VALUE, CONTROL_LIMIT, DRIFT_ALARM_STATE
EWMA_ONE_SIDED: EWMA_VALUE, CONTROL_LIMIT
EWMA_BASELINE_REPLAY_THRESHOLD: CONTROL_LIMIT, FALSE_ALARM_TARGET
```

Return these canonical measurements for every successful supported run:

```python
{
    "EWMA_VALUE": <final EWMA value>,
    "CONTROL_LIMIT": {
        "ucl": <resolved ucl or None>,
        "lcl": <resolved lcl or None>,
        "mode": <"two_sided" | "upper" | "lower">,
    },
    "DRIFT_ALARM_STATE": <"drift_detected" | "normal">,
    "UCL": <resolved upper control limit or None>,
    "LCL": <resolved lower control limit or None>,
    "CENTER_LINE": <resolved center_line>,
    "SIGMA": <resolved sigma>,
    "LAMBDA": <resolved smoothing factor>,
    "CONTROL_WIDTH": <resolved control_width or None>,
    "DIRECTION": <"both" | "increase" | "decrease">,
    "RESET_POLICY": <resolved reset_policy>,
    "WARMUP_SIZE": <resolved warmup_size>,
    "CHECK_EVERY": <resolved check_every>,
    "ALARM_COUNT": <int>,
    "FIRST_ALARM_TIME": <ISO timestamp or None>,
    "LAST_ALARM_TIME": <ISO timestamp or None>,
    "FIRST_ALARM_INDEX": <int or None>,
    "LAST_ALARM_INDEX": <int or None>,
    "FIRST_ALARM_DIRECTION": <"upper" | "lower" | None>,
    "LAST_ALARM_DIRECTION": <"upper" | "lower" | None>,
    "PROCESSED_COUNT": <effective stream row count>,
    "SAMPLE_SIZE": {
        "reference": <effective_reference_n>,
        "current": <effective_current_n>,
        "stream": <effective_stream_n>,
        "dropped_reference": <dropped_reference_n>,
        "dropped_current": <dropped_current_n>,
    },
    "SAMPLE_SIZE_REFERENCE": <effective_reference_n>,
    "SAMPLE_SIZE_CURRENT": <effective_current_n>,
    "REFERENCE_MEAN": <float>,
    "CURRENT_MEAN": <float>,
    "REFERENCE_STD": <float>,
    "CURRENT_STD": <float>,
    "REFERENCE_MEDIAN": <float>,
    "CURRENT_MEDIAN": <float>,
    "MEAN_DELTA": <current mean - reference mean>,
    "MAX_EWMA_VALUE": <max EWMA value seen during replay>,
    "MIN_EWMA_VALUE": <min EWMA value seen during replay>,
    "MAX_UPPER_EXCESS": <max(ewma - ucl) seen, or None>,
    "MAX_LOWER_EXCESS": <max(lcl - ewma) seen, or None>,
}
```

When `record_events=True`, include a compact event list:

```python
{
    "ALARM_EVENTS": [
        {
            "time": <ISO timestamp>,
            "index": <zero-based stream index>,
            "direction": <"upper" | "lower">,
            "ewma_value": <float>,
            "control_limit": <float>,
            "center_line": <float>,
            "lambda": <float>,
            "raw_value": <float>,
        },
        ...
    ]
}
```

For `EWMA_UNIVARIATE_CONTROL_CHART`, top-level `drift_score` should be the
larger of `MAX_UPPER_EXCESS` and `MAX_LOWER_EXCESS`, clipped or represented so
that non-crossing values do not imply a positive breach unless the project
convention prefers signed margin. For `EWMA_ONE_SIDED`, `drift_score` should
be the maximum monitored-limit excess in the configured direction.

Top-level `DriftResult` field mapping:

```text
method_id = "DM-030"
method_name = "EWMA"
method_category = "StreamingChangeDetector"
variant_id = resolved variant id
drift_score = max monitored control-limit excess during replay
p_value = None
test_statistic = final EWMA_VALUE
threshold = monitored control limit for one-sided variants, otherwise None
```

Interpretation text should state:

- which variant and direction ran
- that reference/current windows were replayed as one finite chronological
  numeric stream
- effective reference/current/stream row counts
- resolved `center_line`, `sigma`, `lambda`, `control_width`, `ucl`, `lcl`,
  `warmup_size`, and `check_every`
- final, maximum, and minimum EWMA values
- whether an alarm occurred, and first/last alarm time and direction if
  applicable
- that EWMA on a numeric metric stream is a sequential control-chart signal,
  not proof of root cause, model performance degradation, supervised concept
  drift, or retraining necessity

## 8. Algorithm Steps

1. Normalize `params` to an empty dict when omitted.
2. Resolve `variant_id`; default to `EWMA_UNIVARIATE_CONTROL_CHART`.
3. Reject unknown variants with `severity="not_applicable"` and a warning.
4. Reject `EWMA_BASELINE_REPLAY_THRESHOLD` until empirical replay threshold
   calibration is implemented.
5. Resolve direction from variant and validate any explicit `direction` or
   `direction_or_alternative`.
6. Reject multivariate, embedding, categorical, count-table, raw label, raw
   prediction, and distance-stream requests in the first implementation.
7. Resolve value column, `nan_policy`, event-recording settings, sample-size
   minima, `warmup_size`, `check_every`, `reset_policy`, `lambda`,
   `center_line`, `sigma`, limit parameters, and threshold aliases.
8. Validate that both reference and current windows are supplied and parseable.
9. Validate required columns and scalar numeric value data. Boolean data is not
   valid EWMA numeric-stream input.
10. Convert and sort the DataFrame according to the common window handling
    contract.
11. Slice inclusive reference/current windows.
12. Reject overlapping windows unless an explicit overlap policy is added.
13. Drop rows with invalid timestamps or non-finite values; record original and
    effective counts.
14. If either effective sample is empty or below minimum, return not
    applicable.
15. Resolve omitted `center_line` and `sigma` from effective reference summary
    statistics.
16. Resolve explicit or theoretical `ucl` and `lcl` according to variant and
    direction.
17. Concatenate effective reference/current rows and sort by timestamp to form
    the finite replay stream.
18. If the effective stream length is below `warmup_size`, return not
    applicable.
19. Add warnings for invalid rows, highly imbalanced sample sizes, small
    samples that pass the hard minimum, autocorrelation risk, seasonality, zero
    reference variance, and threshold aliases.
20. Iterate each stream row in chronological order, updating EWMA value,
    maximum/minimum EWMA, monitored margin, and event summaries.
21. After `warmup_size` and according to `check_every`, compare the monitored
    EWMA value to the configured control limit.
22. Record alarm events. Do not reset EWMA state unless a later design approves
    a reset policy.
23. Compute final sample summaries, final state, alarm summary, and maximum
    monitored margin.
24. Apply the drift decision rule from section 9.
25. Build `DriftResult` with method identity, variant, canonical measurements,
    helper summaries, counts, windows, parameters, warnings, metadata, and
    concise interpretation text.

## 9. Drift Decision Rule

Streaming alarm rule for supported first-scope variants:

```text
if alarm_count > 0:
    drift_detected = True
    severity = "drift_detected"
    DRIFT_ALARM_STATE = "drift_detected"
else:
    drift_detected = False
    severity = "normal"
    DRIFT_ALARM_STATE = "normal"
```

Use strict control-limit crossing:

```text
upper alarm: EWMA_VALUE > ucl
lower alarm: EWMA_VALUE < lcl
```

Equality is not drift. `p_value` remains `None`.

For report wording:

- two-sided alarm: "EWMA raised a control-chart alarm in the recorded direction
  while replaying the selected reference/current rows"
- upper alarm: "EWMA raised an upper control-limit alarm while replaying the
  selected reference/current rows"
- lower alarm: "EWMA raised a lower control-limit alarm while replaying the
  selected reference/current rows"
- no alarm: "no EWMA alarm was raised under this finite replay, smoothing
  factor, center line, and control-limit policy"
- deferred empirical threshold request: "`EWMA_BASELINE_REPLAY_THRESHOLD`
  requires an explicit baseline replay threshold calibration contract"
- unsupported supervised request: "supervised EWMA requires an explicit error
  stream contract"

The EWMA result depends on stream order, smoothing factor, center line,
baseline variance, control-limit policy, direction, warmup size, sample count,
and finite replay scope. It must not be compared directly with ADWIN, KSWIN,
Page-Hinkley, CUSUM, GMA, BOCD, MEWMA, or batch two-sample tests without method
and variant context.

## 10. Warnings and Not-Applicable Conditions

Return `severity="not_applicable"` and `drift_detected=None` for:

- missing `time_col`
- missing resolved value column
- non-datetime-coercible `time_col`
- nonnumeric, boolean, object, array, category, label, embedding, or text value
  data
- omitted or unparseable `reference_window` or `current_window`
- empty reference or current window after slicing
- no finite numeric values after invalid rows are handled
- effective reference or current sample size below minimum
- effective stream length below `warmup_size`
- unsupported or unknown `variant_id`
- `EWMA_BASELINE_REPLAY_THRESHOLD` until empirical threshold policy is approved
- supervised error-rate EWMA requests until label/error-stream handling is
  approved
- `feature_cols`, `embedding_cols`, object embeddings, list-valued rows,
  category/count columns, raw `y_true`/`y_pred` requests, or other non-scalar
  inputs in the first implementation
- invalid `lambda`, invalid `center_line`, invalid `sigma`, invalid
  `control_width`, invalid or conflicting `ucl`/`lcl`/`threshold`/
  `threshold_or_alpha`, conflicting variant and direction, invalid
  `warmup_size`, `reset_policy`, `check_every`, event-record settings,
  `nan_policy`, sample-size parameter, or warning-ratio parameter
- current/reference window overlap when overlap policy is not explicitly
  defined by the implementation
- theoretical limit computation cannot produce finite control limits
- non-finite EWMA statistic or non-finite running state

Return `severity="normal"` or `"drift_detected"` with warnings when the method
can still run but interpretation needs caution:

- timestamps or values were dropped because they were invalid or non-finite
- `threshold`, `threshold_or_alpha`, `ucl`, or `lcl` was interpreted through a
  compatibility path
- `center_line` or `sigma` was inferred from the effective reference window
  rather than supplied by a calibration process
- reference standard deviation is very small, making theoretical limits narrow
- reference/current sample sizes are highly imbalanced
- effective stream length is only slightly above `warmup_size`
- observations are autocorrelated time-series rows rather than independent
  draws
- strong seasonality, batch collection cycles, or traffic mix changes may
  trigger EWMA alarms that are operational-pattern changes rather than drift
- `lambda` is unusually high and may react to short-lived noise
- `lambda` is unusually low and may delay alarms
- `control_width` or explicit limits are unusually narrow or wide relative to
  the value scale
- `check_every > 1` may delay or miss alarms between check points
- event history was truncated by `max_event_records`

Unexpected numeric exceptions should return `severity="error"` or `"watch"`
according to project convention, with `drift_detected=None` and a clear
warning, without raising through the public detector boundary.

Do not silently coerce categorical values, boolean flags, labels, embeddings,
lists, object arrays, count tables, distance inputs, or multivariate matrices
into the univariate EWMA detector.

## 11. Implementation Target

```text
module: drift_algorithm.methods.streamingchangedetector
function: detect_ewma
```

Expected dependencies:

```text
pandas
numpy
```

The first implementation must be able to run without adding a new network
dependency.

Expected result object:

```text
DriftResult from drift_algorithm/docs/input_output_contracts.md equivalent code
contract
```

Helper functions should follow existing project patterns:

- add `EWMA_METHOD_ID = "DM-030"` and `EWMA_METHOD_NAME = "EWMA"`
- define `SUPPORTED_EWMA_VARIANTS` for `EWMA_UNIVARIATE_CONTROL_CHART` and
  `EWMA_ONE_SIDED`
- define `DEFERRED_EWMA_VARIANTS` for `EWMA_BASELINE_REPLAY_THRESHOLD`
- use the common `DriftResult` dataclass
- use `not_applicable_result` or a method-specific not-applicable helper for
  validation failures
- reuse common numeric-window preparation where it matches the finite replay
  contract, but ensure the final stream is sorted chronologically
- keep EWMA helpers private to the module unless another streaming detector
  already exposes a shared helper
- record backend name, finite-replay policy, direction, value column, effective
  windows, resolved parameters, sample-size metadata, and unsupported/deferred
  variant decisions so the result is auditable

Suggested private helper shape:

```python
def _ewma_not_applicable(
    variant_id: str | None,
    warning: str,
    metadata: dict[str, Any] | None = None,
    prior_warnings: list[str] | None = None,
) -> DriftResult:
    ...

def _resolve_ewma_params(params: dict[str, Any]) -> dict[str, Any]:
    ...

def _prepare_ewma_stream(
    data: pd.DataFrame,
    *,
    time_col: str,
    value_col: str,
    reference_window: tuple[str, str],
    current_window: tuple[str, str],
    params: dict[str, Any],
) -> dict[str, Any]:
    ...

def _run_ewma_stream(
    values: np.ndarray,
    times: np.ndarray,
    *,
    variant_id: str,
    direction: str,
    center_line: float,
    sigma: float,
    lambda_: float,
    ucl: float | None,
    lcl: float | None,
    warmup_size: int,
    check_every: int,
    record_events: bool,
    max_event_records: int,
) -> dict[str, Any]:
    ...
```

Public contract:

- `detect_ewma` must be importable from
  `drift_algorithm.methods.streamingchangedetector`.
- The function must accept the common arguments exactly as shown in section 4.
- It must return `DriftResult`, never raw tuples or dictionaries.
- Validation failures must return `severity="not_applicable"` unless they are
  unexpected numeric/runtime errors.
- The first implementation must not fabricate a p-value.
- `EWMA_UNIVARIATE_CONTROL_CHART` must evaluate both upper and lower limits.
- `EWMA_ONE_SIDED` must record the monitored direction and must not report the
  opposite direction as drift.
- `EWMA_BASELINE_REPLAY_THRESHOLD`, supervised error-rate EWMA, and
  multivariate aggregation requests must be explicit `not_applicable` results
  until their separate contracts are approved.

## 12. Verification Plan

Unit tests for the first implementation:

1. Default no-alarm finite replay:
   - Generate stable numeric reference/current rows from the same distribution
     with deterministic timestamps.
   - Omit `variant_id` and EWMA settings.
   - Assert `variant_id == "EWMA_UNIVARIATE_CONTROL_CHART"`.
   - Assert `EWMA_VALUE`, `CONTROL_LIMIT`, `DRIFT_ALARM_STATE`, `CENTER_LINE`,
     `SIGMA`, `LAMBDA`, `UCL`, `LCL`, `ALARM_COUNT`, `PROCESSED_COUNT`,
     `SAMPLE_SIZE`, `SAMPLE_SIZE_REFERENCE`, and `SAMPLE_SIZE_CURRENT` exist.
   - Assert `p_value is None`, `drift_detected is False`,
     `severity == "normal"`, and `DRIFT_ALARM_STATE == "normal"` for a stable
     deterministic stream.
2. Two-sided upper alarm:
   - Generate reference values around one mean and current values with a clear
     upward shift.
   - Use deterministic `center_line`, `sigma`, `lambda`, `control_width`, and
     `warmup_size` chosen to produce an upper alarm.
   - Assert `ALARM_COUNT > 0`, `drift_detected is True`,
     `severity == "drift_detected"`, and first/last alarm direction is
     `upper`.
3. Two-sided lower alarm:
   - Generate reference values around one mean and current values with a clear
     downward shift.
   - Assert the default two-sided variant can raise a lower alarm and records
     the alarm direction.
4. One-sided routing:
   - Use `variant_id="EWMA_ONE_SIDED"` with `direction="increase"` and assert
     only upper-limit alarms are monitored.
   - Use `direction="decrease"` and assert only lower-limit alarms are
     monitored.
   - Assert a direction conflicting with the selected variant returns
     `not_applicable`.
5. Parameter alias and validation:
   - Assert `threshold_or_alpha` is treated as `control_width` only in the
     documented compatibility case.
   - Assert `threshold` maps to the monitored one-sided limit.
   - Assert invalid `lambda`, `center_line`, `sigma`, `control_width`, `ucl`,
     `lcl`, `threshold`, `threshold_or_alpha`, `warmup_size`, `direction`,
     `direction_or_alternative`, `reset_policy`, `check_every`,
     `record_events`, `max_event_records`, `nan_policy`, and sample-size
     settings return not applicable.
6. Window and stream ordering:
   - Provide unsorted input rows and assert processed counts and alarm event
     indices follow chronological order.
   - Assert missing windows, unparseable windows, empty slices, insufficient
     sample sizes, stream shorter than `warmup_size`, and overlapping windows
     return `not_applicable`.
7. Schema validation:
   - Missing value column.
   - Non-numeric, boolean, object/list, embedding-like, categorical, or text
     value column.
   - Invalid timestamps and non-finite values are dropped with warnings and
     effective counts.
8. Event recording:
   - With `record_events=True`, assert `ALARM_EVENTS` is present and bounded by
     `max_event_records`.
   - With `record_events=False`, assert detailed events can be omitted while
     alarm count and first/last alarm summaries remain available.
9. Deferred and unrelated requests:
   - Supplying `EWMA_BASELINE_REPLAY_THRESHOLD`, `baseline_replay_period`,
     `empirical_quantile`, or `target_false_alarm_rate` returns
     `severity="not_applicable"` with an empirical-threshold warning.
   - Supplying raw `y_true`/`y_pred`, `feature_cols`, `embedding_cols`, or
     distance-stream settings does not trigger silent coercion.
10. Warning behavior:
    - Imbalanced sample sizes produce a caution warning.
    - Omitted `center_line` or `sigma` records how the value was inferred from
      the reference window.
    - Very low/high `lambda`, zero or near-zero reference standard deviation,
      and `check_every > 1` produce interpretation warnings.
    - Event truncation is recorded as a warning.
11. Numeric failure:
    - Simulate non-finite EWMA state or invalid computed limits.
    - Assert the public detector returns `severity="error"`, `"watch"`, or
      `not_applicable` according to project convention with
      `drift_detected=None` and a clear warning.

Recommended commands after implementation:

```text
python -m py_compile drift_algorithm\methods\streamingchangedetector.py
python -m pytest tests\test_ewma.py
python -m pytest tests\test_adwin.py tests\test_kswin.py tests\test_page_hinkley_test.py tests\test_cusum.py
```

Manual review before marking implementation complete:

- Confirm public function signature matches the common contract.
- Confirm canonical measurement names match
  `drift_method_variant_measurement_summary.csv`.
- Confirm default variant is `EWMA_UNIVARIATE_CONTROL_CHART`.
- Confirm `reference_window` and `current_window` define a finite replay stream
  rather than a batch reference-vs-current statistic.
- Confirm omitted `center_line` and `sigma` are inferred only from the
  effective reference window, not current data.
- Confirm `lambda` is validated as `0 < lambda <= 1`.
- Confirm strict `EWMA_VALUE > ucl` and `EWMA_VALUE < lcl` crossing is used.
- Confirm top-level `p_value` remains `None`.
- Confirm event history, alarm direction, and final EWMA state are auditable.
- Confirm `EWMA_BASELINE_REPLAY_THRESHOLD` fails explicitly until empirical
  threshold policy is approved.
- Confirm interpretation text avoids root-cause, performance-degradation,
  supervised concept-drift, and retraining claims without labeled evidence and
  policy inputs.

## 13. Manager Review Points

- First implementation scope is `EWMA_UNIVARIATE_CONTROL_CHART` and
  `EWMA_ONE_SIDED` over scalar numeric `(time, value)` rows only.
- Although EWMA is a sequential control chart, the current public API supplies
  finite timestamp windows; this design replays reference/current rows in
  chronological order and reports the resulting alarm state.
- `reference_window` and `current_window` are required for API consistency and
  for defining replay scope. The reference window also supplies default
  calibration values when `center_line` or `sigma` are omitted.
- Proposed defaults are `lambda=0.2`, `control_width=3.0`,
  `warmup_size=20`, `check_every=1`, and `reset_policy="none"`. These should
  be reviewed against target metric scale and operational alert policy.
- The first theoretical limit uses the steady-state EWMA standard deviation
  `sigma * sqrt(lambda / (2 - lambda))`; startup-varying limits are deferred.
- `threshold_or_alpha` is only a compatibility alias for `control_width` in a
  narrow case; EWMA does not return a p-value.
- `EWMA_ONE_SIDED` is supported for upper or lower risk direction, but the
  direction must be declared before evaluation.
- `EWMA_BASELINE_REPLAY_THRESHOLD` remains deferred because empirical false
  alarm calibration needs a separate baseline replay contract.
- The public target is `detect_ewma` in
  `drift_algorithm.methods.streamingchangedetector`.
