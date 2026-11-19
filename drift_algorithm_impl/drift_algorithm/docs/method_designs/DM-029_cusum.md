# DM-029 CUSUM Design

## 1. Method Identity

- Method ID: `DM-029`
- Method name: `CUSUM`
- Category: `StreamingChangeDetector`
- Method kind: `detector`
- Status: `확정`
- Source catalog: `drift_methods_catalog.md`
- Source variant document: `algorithm_variants/cusum_algorithm_variants.md`
- Source parameter tables:
  - `drift_method_variant_links.csv`
  - `drift_method_variant_measurement_summary.csv`
  - `drift_method_variant_parameters.csv`
  - `drift_method_parameter_guide.md`

The first implementation is a univariate numeric sequential cumulative-sum
detector executed over a finite DataFrame slice. It accepts the common
`(time, value)` pandas DataFrame contract, sorts rows by time, slices the
supplied reference/current timestamp windows, concatenates the two slices in
time order, and replays the values through a CUSUM state machine.

## 2. Purpose

`CUSUM` detects persistent movement away from a baseline mean by accumulating
small signed deviations over time. It is a sequential control-chart detector,
not a p-value test and not a batch reference-vs-current distance calculation.

The catalog input is `numeric metric stream`; the catalog output is
`cumulative sum, alarm`. The first implementation narrows that catalog scope to
scalar numeric `(time, value)` rows because the public API receives finite
DataFrame windows, not an unbounded online iterator. It should be read as:

```text
Replay the selected reference/current rows as a time-ordered numeric stream and
report whether CUSUM raised a cumulative-deviation alarm during that replay.
```

Use the first implementation when:

- the monitored signal is one scalar numeric metric
- the caller can provide timestamp ranges for `reference_window` and
  `current_window`
- the operational question is whether a sequential cumulative-sum detector
  would alarm while processing those rows in chronological order
- direction matters: upward for loss, error rate, latency, reject rate, or
  other "larger is worse" metrics; downward for confidence, throughput, recall,
  acceptance rate, or other "smaller is worse" metrics
- positive CUSUM, negative CUSUM, threshold, target mean, allowance, and alarm
  history are useful monitoring outputs

Do not use the first implementation for categorical labels, count tables,
probability vectors, raw embeddings, multivariate feature matrices, text, SHAP
matrices, raw supervised prediction pairs, or retraining policy decisions.
Those require another method family or a future contract.

## 3. Supported Variants

Supported for the first implementation:

- `ONE_SIDED_UPPER_CUSUM`
  - Default variant.
  - Detects a sustained upward movement from the target mean.
  - Uses chronological replay of the selected reference/current rows.
  - Raises an alarm when positive CUSUM exceeds `decision_threshold_h`.
- `ONE_SIDED_LOWER_CUSUM`
  - Detects a sustained downward movement from the target mean.
  - Uses chronological replay of the selected reference/current rows.
  - Raises an alarm when negative CUSUM exceeds `decision_threshold_h`.
- `TWO_SIDED_CUSUM`
  - Detects sustained movement in either direction.
  - Maintains positive and negative CUSUM states in the same replay.
  - Raises an alarm when either direction exceeds `decision_threshold_h` and
    records which direction triggered the alarm.

Deferred until separate contracts are approved:

- `CUSUM_ON_DISTANCE_STREAM`
  - Requires a documented upstream distance stream, `base_distance_method`,
    distance-window construction, distance baseline, and replay cadence.
  - Must not compute Wasserstein, PSI, MMD, embedding distance, or other
    distance values inside `detect_cusum` in the first implementation.
  - Must return `severity="not_applicable"` in the first implementation unless
    a manager explicitly approves the distance-stream contract.
- Supervised error-rate CUSUM:
  - Requires an explicit label/error schema, `error_col` or `y_true`/`y_pred`
    handling, label-delay policy, and error definition.
  - Must not infer performance drift from arbitrary numeric `value` rows.
- Multivariate or score aggregation:
  - Requires documented feature selection, aggregation, scaling, or upstream
    score generation policy.
  - Must not silently average feature columns or compute a distance stream
    inside this method.

Default variant selection:

```text
if params["variant_id"] is omitted:
    variant_id = "ONE_SIDED_UPPER_CUSUM"
```

## 4. Input Schema

Use the common `pandas.DataFrame` input boundary from
`../input_output_contracts.md`.

Public function shape:

```python
def detect_cusum(
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

Although CUSUM is a streaming detector, the first public API still requires
both windows. They define the finite replay scope and, when `target_mean` is
omitted, the baseline mean:

1. Convert `time_col` with `pd.to_datetime(..., errors="coerce")`.
2. Convert the value column with `pd.to_numeric(..., errors="coerce")`.
3. Sort by `time_col`.
4. Slice inclusive reference/current windows.
5. Reject overlapping windows unless an explicit overlap policy is added
   later.
6. Drop rows with invalid timestamps or non-finite values.
7. Resolve `target_mean` from the effective reference slice when omitted.
8. Concatenate the effective reference/current rows and sort by `time_col`.
9. Iterate the effective rows in time order.

Minimum effective sample sizes:

```text
ONE_SIDED_UPPER_CUSUM, ONE_SIDED_LOWER_CUSUM, TWO_SIDED_CUSUM:
  min_reference_size: default 20
  min_current_size: default 20
  warmup_size: default 30
```

If either effective DataFrame window is below its minimum, or if the combined
finite replay stream is below `warmup_size`, return
`severity="not_applicable"` and do not run the detector.

## 5. Parameters

Accepted `params` keys and defaults for the first implementation:

| Param | Type | Default | Applies to | Meaning |
|---|---:|---:|---|---|
| `variant_id` | string | `ONE_SIDED_UPPER_CUSUM` | all | Variant selector. |
| `target_mean` | float | reference mean | supported variants | Baseline center used by the CUSUM recurrence. |
| `allowance_k` | float | `0.5 * reference_std` or `0.0` if reference std is zero | supported variants | Slack/allowance subtracted from deviations before accumulation. Must be non-negative. |
| `decision_threshold_h` | float | `5.0 * reference_std` or `5.0` if reference std is zero | supported variants | CUSUM alarm limit in the scale of the input signal. Must be positive. |
| `threshold` | float | optional | supported variants | Compatibility alias for `decision_threshold_h`; must not conflict if both are supplied. |
| `threshold_or_alpha` | float | optional | supported variants | Compatibility alias for `decision_threshold_h`; must not conflict with explicit threshold params. |
| `direction` | string | inferred from variant | supported variants | `increase`, `decrease`, or `both`; may not conflict with `variant_id`. |
| `direction_or_alternative` | string | optional | one-sided variants | Compatibility alias for `direction`; may not conflict with variant direction. |
| `reset_policy` | string | `after_alarm` | supported variants | State handling after an alarm: `after_alarm` or `none` in the first implementation. |
| `warmup_size` | int | `30` | supported variants | Minimum replay length before alarms are evaluated. |
| `input_signal` | string | optional | supported variants | Value column name only when `value_col is None`; otherwise metadata label such as `loss`, `latency`, `confidence`, or `score`. |
| `min_reference_size` | int | `20` | supported variants | Minimum effective reference rows after invalid rows are dropped. |
| `min_current_size` | int | `20` | supported variants | Minimum effective current rows after invalid rows are dropped. |
| `nan_policy` | string | `drop` | supported variants | First implementation supports `drop`/`omit` only. |
| `check_every` | int | `1` | supported variants | Check interval in processed observations after `warmup_size`. |
| `record_events` | bool | `True` | supported variants | Include compact alarm event history in measurements. |
| `max_event_records` | int | `50` | supported variants | Maximum number of alarm events retained in measurements. |
| `sample_imbalance_warning_ratio` | float | `10.0` | supported variants | Warn when larger input window size divided by smaller size exceeds this ratio. |
| `base_distance_method` | string | none | deferred distance stream | Not supported in first implementation except for explicit not-applicable reporting. |
| `distance_window_size` | int | none | deferred distance stream | Not supported in first implementation except for explicit not-applicable reporting. |

Parameter rules:

- `decision_threshold_h` is an alarm limit on `CUSUM_STATISTIC`. It is not a
  p-value threshold.
- `threshold` and `threshold_or_alpha` are accepted only as compatibility
  aliases for `decision_threshold_h`. If multiple threshold params are supplied
  and differ, return `severity="not_applicable"`.
- `target_mean`, when omitted, is computed from the effective reference window
  after invalid rows are dropped. This makes the finite replay auditable and
  avoids using current data to set the center line.
- `allowance_k` must be `>= 0`. Larger values ignore smaller sustained shifts;
  very large values can suppress alarms.
- `decision_threshold_h` must be `> 0`.
- `warmup_size`, `check_every`, `min_reference_size`, `min_current_size`, and
  `max_event_records` must be positive integers.
- `direction` must be `increase` for `ONE_SIDED_UPPER_CUSUM`, `decrease` for
  `ONE_SIDED_LOWER_CUSUM`, and `both` for `TWO_SIDED_CUSUM`.
- `direction_or_alternative` accepts `up`/`greater` as `increase`,
  `down`/`less` as `decrease`, and `two-sided`/`both` as `both`.
- `reset_policy="after_alarm"` resets the alarmed CUSUM state after each alarm
  so that multiple events in one finite replay are auditable.
  `reset_policy="none"` leaves state unchanged after an alarm. Other policies
  are deferred.
- `nan_policy` supports `drop` and `omit` as aliases for dropping invalid rows.
  Other values return `not_applicable`.
- Reject or warn on unrelated params such as `feature_cols`, `embedding_cols`,
  `category_col`, `count_col`, raw label columns, classifier settings,
  distance-stream settings, or preprocessing functions.

## 6. CUSUM Statistic and State Policy

Normalize the selected finite stream to one-dimensional arrays:

```python
stream_values = np.asarray(..., dtype=float)
stream_times = np.asarray(..., dtype="datetime64[ns]")
```

For an observation `x_t`, target mean `mu0`, allowance `k`, and decision
threshold `h`, maintain positive and/or negative CUSUM states:

```text
positive_t = max(0, positive_{t-1} + x_t - mu0 - k)
negative_t = max(0, negative_{t-1} + mu0 - x_t - k)
upper alarm if positive_t > h
lower alarm if negative_t > h
```

Variant behavior:

```text
ONE_SIDED_UPPER_CUSUM: evaluate only positive_t
ONE_SIDED_LOWER_CUSUM: evaluate only negative_t
TWO_SIDED_CUSUM: evaluate both positive_t and negative_t
```

Implementation-level pseudocode:

```text
events = []
positive = 0
negative = 0
max_positive = 0
max_negative = 0

for index, (time, value) in chronological stream:
    positive = max(0, positive + value - target_mean - allowance_k)
    negative = max(0, negative + target_mean - value - allowance_k)
    max_positive = max(max_positive, positive)
    max_negative = max(max_negative, negative)

    if index + 1 < warmup_size:
        continue
    if (index + 1 - warmup_size) % check_every != 0:
        continue

    if variant monitors upper and positive > decision_threshold_h:
        record upper alarm event
        if reset_policy == "after_alarm":
            positive = 0

    if variant monitors lower and negative > decision_threshold_h:
        record lower alarm event
        if reset_policy == "after_alarm":
            negative = 0
```

The first implementation should use a deterministic NumPy/Pandas
implementation. It does not require SciPy or network-installed streaming
libraries. The design does not require a top-level p-value. Do not label the
CUSUM statistic as `P_VALUE`.

## 7. Output Measurements

`drift_method_variant_measurement_summary.csv` maps all DM-029 variants to:

```text
CUSUM_STATISTIC
DRIFT_ALARM_STATE
```

Return these canonical measurements for every successful supported run:

```python
{
    "CUSUM_STATISTIC": <final monitored statistic>,
    "DRIFT_ALARM_STATE": <"drift_detected" | "normal">,
    "CUSUM_POSITIVE": <final positive CUSUM>,
    "CUSUM_NEGATIVE": <final negative CUSUM>,
    "MAX_CUSUM_POSITIVE": <max positive CUSUM seen during replay>,
    "MAX_CUSUM_NEGATIVE": <max negative CUSUM seen during replay>,
    "TARGET_MEAN": <resolved target_mean>,
    "ALLOWANCE_K": <resolved allowance_k>,
    "DECISION_THRESHOLD_H": <resolved decision_threshold_h>,
    "DIRECTION": <"increase" | "decrease" | "both">,
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
}
```

For `ONE_SIDED_UPPER_CUSUM`, `CUSUM_STATISTIC` is the final positive CUSUM and
the top-level `drift_score` should be `MAX_CUSUM_POSITIVE`. For
`ONE_SIDED_LOWER_CUSUM`, `CUSUM_STATISTIC` is the final negative CUSUM and
`drift_score` should be `MAX_CUSUM_NEGATIVE`. For `TWO_SIDED_CUSUM`,
`CUSUM_STATISTIC` is the larger of final positive and final negative CUSUM, and
`drift_score` should be the larger of the two maximum CUSUM states.

When `record_events=True`, include a compact event list:

```python
{
    "ALARM_EVENTS": [
        {
            "time": <ISO timestamp>,
            "index": <zero-based stream index>,
            "direction": <"upper" | "lower">,
            "cusum_statistic": <float>,
            "positive_cusum": <float>,
            "negative_cusum": <float>,
            "target_mean": <float>,
            "allowance_k": <float>,
            "decision_threshold_h": <float>,
        },
        ...
    ]
}
```

Top-level `DriftResult` field mapping:

```text
method_id = "DM-029"
method_name = "CUSUM"
method_category = "StreamingChangeDetector"
variant_id = resolved variant id
drift_score = max monitored CUSUM statistic seen during replay
p_value = None
test_statistic = final monitored CUSUM statistic
threshold = resolved decision_threshold_h
```

Interpretation text should state:

- which variant and direction ran
- that reference/current windows were replayed as one finite chronological
  numeric stream
- effective reference/current/stream row counts
- resolved `target_mean`, `allowance_k`, `decision_threshold_h`,
  `warmup_size`, `check_every`, and `reset_policy`
- final and maximum monitored CUSUM statistic
- whether an alarm occurred, and first/last alarm time and direction if
  applicable
- that CUSUM on a numeric metric stream is a sequential cumulative-deviation
  signal, not proof of root cause, model performance degradation, supervised
  concept drift, or retraining necessity

## 8. Algorithm Steps

1. Normalize `params` to an empty dict when omitted.
2. Resolve `variant_id`; default to `ONE_SIDED_UPPER_CUSUM`.
3. Reject unknown variants with `severity="not_applicable"` and a warning.
4. Reject `CUSUM_ON_DISTANCE_STREAM` until the distance-stream contract is
   approved.
5. Resolve direction from variant and validate any explicit `direction` or
   `direction_or_alternative`.
6. Reject multivariate, embedding, categorical, count-table, raw label, raw
   prediction, and distance-stream requests in the first implementation.
7. Resolve value column, `nan_policy`, event-recording settings, sample-size
   minima, `warmup_size`, `check_every`, `reset_policy`, threshold aliases,
   and any explicit `target_mean`/`allowance_k`.
8. Validate that both reference and current windows are supplied and parseable.
9. Validate required columns and scalar numeric value data. Boolean data is not
   valid CUSUM numeric-stream input.
10. Convert and sort the DataFrame according to the common window handling
    contract.
11. Slice inclusive reference/current windows.
12. Reject overlapping windows unless an explicit overlap policy is added.
13. Drop rows with invalid timestamps or non-finite values; record original and
    effective counts.
14. If either effective sample is empty or below minimum, return not
    applicable.
15. Resolve omitted `target_mean`, `allowance_k`, and `decision_threshold_h`
    from effective reference summary statistics.
16. Concatenate effective reference/current rows and sort by timestamp to form
    the finite replay stream.
17. If the effective stream length is below `warmup_size`, return not
    applicable.
18. Add warnings for invalid rows, highly imbalanced sample sizes, small
    samples that pass the hard minimum, autocorrelation risk, seasonality,
    zero reference variance, and threshold aliases.
19. Iterate each stream row in chronological order, updating positive and/or
    negative CUSUM states and maximum states.
20. After `warmup_size` and according to `check_every`, compare monitored
    CUSUM state to `decision_threshold_h`.
21. Record alarm events and apply `reset_policy`.
22. Compute final sample summaries, final state, alarm summary, and maximum
    monitored statistic.
23. Apply the drift decision rule from section 9.
24. Build `DriftResult` with method identity, variant, canonical measurements,
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

Use strict `CUSUM_STATISTIC > decision_threshold_h`, not `>=`, for each
eligible check. Equality is not drift. `threshold` in the top-level result is
the resolved `decision_threshold_h`. `p_value` remains `None`.

For report wording:

- upper alarm: "CUSUM raised an upper-direction cumulative-deviation alarm
  while replaying the selected reference/current rows"
- lower alarm: "CUSUM raised a lower-direction cumulative-deviation alarm
  while replaying the selected reference/current rows"
- two-sided alarm: "CUSUM raised a cumulative-deviation alarm in the recorded
  direction while replaying the selected reference/current rows"
- no alarm: "no CUSUM alarm was raised under this finite replay, target mean,
  allowance, threshold, and reset policy"
- deferred distance-stream request: "`CUSUM_ON_DISTANCE_STREAM` requires an
  explicit distance-stream construction contract"
- unsupported supervised request: "supervised CUSUM requires an explicit error
  stream contract"

The CUSUM result depends on stream order, direction, `target_mean`,
`allowance_k`, `decision_threshold_h`, `warmup_size`, reset policy, sample
count, and finite replay scope. It must not be compared directly with ADWIN,
KSWIN, Page-Hinkley, EWMA, GMA, BOCD, or batch two-sample tests without method
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
- `CUSUM_ON_DISTANCE_STREAM` until the distance-stream policy is approved
- supervised error-rate CUSUM requests until label/error-stream handling is
  approved
- `feature_cols`, `embedding_cols`, object embeddings, list-valued rows,
  category/count columns, raw `y_true`/`y_pred` requests, `base_distance_method`,
  `distance_window_size`, or other non-scalar inputs in the first
  implementation
- invalid `target_mean`, invalid `allowance_k`, invalid or conflicting
  `decision_threshold_h`/`threshold`/`threshold_or_alpha`, conflicting variant
  and direction, invalid `warmup_size`, `reset_policy`, `check_every`,
  event-record settings, `nan_policy`, sample-size parameter, or warning-ratio
  parameter
- current/reference window overlap when overlap policy is not explicitly
  defined by the implementation
- non-finite CUSUM statistic or non-finite running state

Return `severity="normal"` or `"drift_detected"` with warnings when the method
can still run but interpretation needs caution:

- timestamps or values were dropped because they were invalid or non-finite
- `threshold` or `threshold_or_alpha` was interpreted as
  `decision_threshold_h`
- `target_mean` was inferred from the effective reference window rather than
  supplied by a calibration process
- `allowance_k` or `decision_threshold_h` was inferred from a low or zero
  reference standard deviation
- reference/current sample sizes are highly imbalanced
- effective stream length is only slightly above `warmup_size`
- observations are autocorrelated time-series rows rather than independent
  draws
- strong seasonality, batch collection cycles, or traffic mix changes may
  trigger cumulative-deviation alarms that are operational-pattern changes
  rather than drift
- `decision_threshold_h` is unusually low or high relative to the value scale
- `allowance_k` is unusually high and may suppress small sustained shifts
- `check_every > 1` may delay or miss alarms between check points
- event history was truncated by `max_event_records`

Unexpected backend or numeric exceptions should return `severity="error"` or
`"watch"` according to project convention, with `drift_detected=None` and a
clear warning, without raising through the public detector boundary.

Do not silently coerce categorical values, boolean flags, labels, embeddings,
lists, object arrays, count tables, distance inputs, or multivariate matrices
into the univariate CUSUM detector.

## 11. Implementation Target

```text
module: drift_algorithm.methods.streamingchangedetector
function: detect_cusum
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

- add `CUSUM_METHOD_ID = "DM-029"` and `CUSUM_METHOD_NAME = "CUSUM"`
- define `SUPPORTED_CUSUM_VARIANTS` for `ONE_SIDED_UPPER_CUSUM`,
  `ONE_SIDED_LOWER_CUSUM`, and `TWO_SIDED_CUSUM`
- define `DEFERRED_CUSUM_VARIANTS` for `CUSUM_ON_DISTANCE_STREAM`
- use the common `DriftResult` dataclass
- use `not_applicable_result` or a method-specific not-applicable helper for
  validation failures
- reuse common numeric-window preparation where it matches the finite replay
  contract, but ensure the final stream is sorted chronologically
- keep CUSUM helpers private to the module unless another streaming detector
  already exposes a shared helper
- record backend name, finite-replay policy, direction, value column, effective
  windows, resolved parameters, sample-size metadata, and unsupported/deferred
  variant decisions so the result is auditable

Suggested private helper shape:

```python
def _cusum_not_applicable(
    variant_id: str | None,
    warning: str,
    metadata: dict[str, Any] | None = None,
    prior_warnings: list[str] | None = None,
) -> DriftResult:
    ...

def _resolve_cusum_params(params: dict[str, Any]) -> dict[str, Any]:
    ...

def _prepare_cusum_stream(
    data: pd.DataFrame,
    *,
    time_col: str,
    value_col: str,
    reference_window: tuple[str, str],
    current_window: tuple[str, str],
    params: dict[str, Any],
) -> dict[str, Any]:
    ...

def _run_cusum_stream(
    values: np.ndarray,
    times: np.ndarray,
    *,
    variant_id: str,
    direction: str,
    target_mean: float,
    allowance_k: float,
    decision_threshold_h: float,
    warmup_size: int,
    check_every: int,
    reset_policy: str,
    record_events: bool,
    max_event_records: int,
) -> dict[str, Any]:
    ...
```

Public contract:

- `detect_cusum` must be importable from
  `drift_algorithm.methods.streamingchangedetector`.
- The function must accept the common arguments exactly as shown in section 4.
- It must return `DriftResult`, never raw tuples or dictionaries.
- Validation failures must return `severity="not_applicable"` unless they are
  unexpected numeric/runtime errors.
- The first implementation must not fabricate a p-value.
- `threshold` in the result must contain the resolved
  `decision_threshold_h`.
- `ONE_SIDED_LOWER_CUSUM` must be a real lower-direction detector, not an upper
  detector reported under a different variant id.
- `TWO_SIDED_CUSUM` must record the alarm direction for every event.
- `CUSUM_ON_DISTANCE_STREAM`, supervised error-rate CUSUM, and multivariate
  aggregation requests must be explicit `not_applicable` results until their
  separate contracts are approved.

## 12. Verification Plan

Unit tests for the first implementation:

1. Default no-alarm finite replay:
   - Generate stable numeric reference/current rows from the same distribution
     with deterministic timestamps.
   - Omit `variant_id` and CUSUM settings.
   - Assert `variant_id == "ONE_SIDED_UPPER_CUSUM"`.
   - Assert `CUSUM_STATISTIC`, `DRIFT_ALARM_STATE`, `CUSUM_POSITIVE`,
     `CUSUM_NEGATIVE`, `TARGET_MEAN`, `ALLOWANCE_K`,
     `DECISION_THRESHOLD_H`, `ALARM_COUNT`, `PROCESSED_COUNT`,
     `SAMPLE_SIZE`, `SAMPLE_SIZE_REFERENCE`, and `SAMPLE_SIZE_CURRENT` exist.
   - Assert `p_value is None`, `drift_detected is False`,
     `severity == "normal"`, and `DRIFT_ALARM_STATE == "normal"` for a stable
     deterministic stream.
2. Upper-direction alarm:
   - Generate reference values around one mean and current values with a clear
     upward shift.
   - Use deterministic `target_mean`, `allowance_k`, `decision_threshold_h`,
     and `warmup_size` chosen to produce an alarm.
   - Assert `ALARM_COUNT > 0`, `drift_detected is True`,
     `severity == "drift_detected"`, and first/last alarm metadata is present.
3. Lower-direction alarm:
   - Generate reference values around one mean and current values with a clear
     downward shift.
   - Use `variant_id="ONE_SIDED_LOWER_CUSUM"`.
   - Assert the lower variant alarms and records `DIRECTION == "decrease"` and
     alarm event direction `lower`.
4. Two-sided routing:
   - Assert `TWO_SIDED_CUSUM` detects either an upward or downward sustained
     shift and records the alarm direction.
   - Assert a direction parameter conflicting with the two-sided variant
     returns `not_applicable`.
5. Parameter alias and validation:
   - Assert `threshold` and `threshold_or_alpha` are treated as
     `decision_threshold_h`.
   - Assert conflicting threshold aliases return `severity="not_applicable"`.
   - Assert invalid `target_mean`, `allowance_k`, `decision_threshold_h`,
     `warmup_size`, `direction`, `direction_or_alternative`, `reset_policy`,
     `check_every`, `record_events`, `max_event_records`, `nan_policy`, and
     sample-size settings return not applicable.
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
8. Event recording and reset:
   - With `record_events=True`, assert `ALARM_EVENTS` is present and bounded by
     `max_event_records`.
   - With `record_events=False`, assert detailed events can be omitted while
     alarm count and first/last alarm summaries remain available.
   - Compare `reset_policy="after_alarm"` and `reset_policy="none"` on a stream
     with sustained shift and assert alarm count/state behavior is auditable.
9. Deferred and unrelated requests:
   - Supplying `CUSUM_ON_DISTANCE_STREAM`, `base_distance_method`, or
     `distance_window_size` returns `severity="not_applicable"` with a
     distance-stream warning.
   - Supplying raw `y_true`/`y_pred`, `feature_cols`, `embedding_cols`, or
     distance-stream settings does not trigger silent coercion.
10. Warning behavior:
    - Imbalanced sample sizes produce a caution warning.
    - Omitted `target_mean`, `allowance_k`, or `decision_threshold_h` records
      how the value was inferred from the reference window.
    - `check_every > 1` records that alarm checks are periodic.
    - Event truncation is recorded as a warning.
11. Numeric failure:
    - Simulate non-finite CUSUM state or invalid computed defaults.
    - Assert the public detector returns `severity="error"`, `"watch"`, or
      `not_applicable` according to project convention with
      `drift_detected=None` and a clear warning.

Recommended commands after implementation:

```text
python -m py_compile drift_algorithm\methods\streamingchangedetector.py
python -m pytest tests\test_cusum.py
python -m pytest tests\test_adwin.py tests\test_kswin.py tests\test_page_hinkley_test.py
```

Manual review before marking implementation complete:

- Confirm public function signature matches the common contract.
- Confirm canonical measurement names match
  `drift_method_variant_measurement_summary.csv`.
- Confirm default variant is `ONE_SIDED_UPPER_CUSUM`.
- Confirm `reference_window` and `current_window` define a finite replay stream
  rather than a batch reference-vs-current statistic.
- Confirm omitted `target_mean` is inferred only from the effective reference
  window, not current data.
- Confirm upper, lower, and two-sided variants use the correct CUSUM states.
- Confirm strict `CUSUM_STATISTIC > decision_threshold_h` is used.
- Confirm top-level `threshold` stores resolved `decision_threshold_h`.
- Confirm top-level `p_value` remains `None`.
- Confirm event history, alarm direction, and final CUSUM state are auditable.
- Confirm `CUSUM_ON_DISTANCE_STREAM` fails explicitly until distance-stream
  policy is approved.
- Confirm interpretation text avoids root-cause, performance-degradation,
  supervised concept-drift, and retraining claims without labeled evidence and
  policy inputs.

## 13. Manager Review Points

- First implementation scope is `ONE_SIDED_UPPER_CUSUM`,
  `ONE_SIDED_LOWER_CUSUM`, and `TWO_SIDED_CUSUM` over scalar numeric
  `(time, value)` rows only.
- Although CUSUM is sequential/streaming, the current public API supplies
  finite timestamp windows; this design replays reference/current rows in
  chronological order and reports the resulting sequential alarm state.
- `reference_window` and `current_window` are required for API consistency and
  for defining replay scope. The reference window also supplies default
  calibration values when `target_mean`, `allowance_k`, or
  `decision_threshold_h` are omitted.
- Proposed defaults infer `target_mean` from the effective reference mean,
  `allowance_k` from `0.5 * reference_std`, `decision_threshold_h` from
  `5.0 * reference_std`, `warmup_size=30`, `check_every=1`, and
  `reset_policy="after_alarm"`. These should be reviewed against the target
  metric scale and any operational calibration practice.
- `threshold` and `threshold_or_alpha` are only compatibility aliases for
  `decision_threshold_h`; CUSUM does not return a p-value.
- `ONE_SIDED_LOWER_CUSUM` is supported by a separate negative CUSUM recurrence,
  not deferred.
- `CUSUM_ON_DISTANCE_STREAM` remains deferred to avoid mixing upstream distance
  construction with this scalar numeric metric-stream detector.
- Supervised error-rate CUSUM remains deferred to avoid conflating generic
  numeric streams with model performance or concept-drift claims.
- The public target is `detect_cusum` in
  `drift_algorithm.methods.streamingchangedetector`.
