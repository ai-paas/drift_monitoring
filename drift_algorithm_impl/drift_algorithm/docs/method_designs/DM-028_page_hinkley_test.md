# DM-028 Page-Hinkley Test Design

## 1. Method Identity

- Method ID: `DM-028`
- Method name: `Page-Hinkley Test`
- Category: `StreamingChangeDetector`
- Method kind: `detector`
- Status: `확정`
- Source catalog: `drift_methods_catalog.md`
- Source variant document: `algorithm_variants/page_hinkley_test_algorithm_variants.md`
- Source parameter tables:
  - `drift_method_variant_links.csv`
  - `drift_method_variant_measurement_summary.csv`
  - `drift_method_variant_parameters.csv`
  - `drift_method_parameter_guide.md`

The first implementation is a univariate numeric streaming mean-change
detector executed over a finite DataFrame slice. It accepts the common
`(time, value)` pandas DataFrame contract, sorts rows by time, slices the
supplied reference/current timestamp windows, concatenates the two slices in
time order, and replays the values through a Page-Hinkley cumulative-deviation
state machine.

## 2. Purpose

`Page-Hinkley Test` detects persistent mean-level movement in a numeric stream
by accumulating deviations from an online mean and raising an alarm when the
cumulative deviation exceeds a threshold. It is a sequential mean-change
detector, not a two-sample distribution test.

The catalog input is `numeric stream`; the catalog output is `PH statistic,
alarm`. The first implementation narrows that catalog scope to scalar numeric
`(time, value)` rows because the public API receives finite DataFrame windows,
not an unbounded online iterator. It should be read as:

```text
Replay the selected reference/current rows as a time-ordered numeric stream and
report whether Page-Hinkley raised a cumulative mean-change alarm during that
replay.
```

Use the first implementation when:

- the monitored signal is one scalar numeric column
- the caller can provide timestamp ranges for `reference_window` and
  `current_window`
- the operational question is whether a sequential mean-change detector would
  alarm while processing those rows in chronological order
- direction matters: increase for loss, error, latency, anomaly rate, or other
  "larger is worse" metrics; decrease for confidence, recall, throughput,
  conversion, or other "smaller is worse" metrics
- PH statistic, running mean, threshold, and alarm history are useful monitoring
  outputs

Do not use the first implementation for categorical labels, count tables,
probability vectors, raw embeddings, multivariate feature matrices, text, SHAP
matrices, raw supervised prediction pairs, or retraining policy decisions.
Those require another method family or a future contract.

## 3. Supported Variants

Supported for the first implementation:

- `PAGE_HINKLEY_INCREASE`
  - Default variant.
  - Detects an upward mean shift in a scalar numeric stream.
  - Uses chronological replay of the selected reference/current rows.
  - Raises an alarm when the increase-direction PH statistic exceeds the
    resolved threshold.
- `PAGE_HINKLEY_DECREASE`
  - Detects a downward mean shift in a scalar numeric stream.
  - Uses the same state machine after applying direction normalization
    equivalent to `x_directional = -x`.
  - Raises an alarm when the decrease-direction PH statistic exceeds the
    resolved threshold.

Deferred until separate contracts are approved:

- Supervised error-rate Page-Hinkley:
  - Requires an explicit label/error schema, `error_col` or `y_true`/`y_pred`
    handling, label-delay policy, and error definition.
  - Must not infer performance drift from arbitrary numeric `value` rows.
- `DRIFT_RETRAINING_WITH_PAGE_HINKLEY`:
  - Belongs to DM-056, not DM-028.
  - Requires classifier, retraining-window, and champion/challenger policies.
  - Must not be implemented inside `detect_page_hinkley_test`.
- Multivariate or score-stream aggregation:
  - Requires documented feature selection, aggregation, scaling, or upstream
    score generation policy.
  - Must not silently average feature columns or compute a distance stream
    inside this method.

Default variant selection:

```text
if params["variant_id"] is omitted:
    variant_id = "PAGE_HINKLEY_INCREASE"
```

## 4. Input Schema

Use the common `pandas.DataFrame` input boundary from
`../input_output_contracts.md`.

Public function shape:

```python
def detect_page_hinkley_test(
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

Although Page-Hinkley is a streaming detector, the first public API still
requires both windows. They define the finite replay scope:

1. Convert `time_col` with `pd.to_datetime(..., errors="coerce")`.
2. Convert the value column with `pd.to_numeric(..., errors="coerce")`.
3. Sort by `time_col`.
4. Slice inclusive reference/current windows.
5. Reject overlapping windows unless an explicit overlap policy is added later.
6. Concatenate the two slices and sort by `time_col`.
7. Drop rows with invalid timestamps or non-finite values.
8. Iterate the effective rows in time order.

Minimum effective sample sizes:

```text
PAGE_HINKLEY_INCREASE and PAGE_HINKLEY_DECREASE:
  min_reference_size: default 20
  min_current_size: default 20
  min_instances: default 30
```

If either effective DataFrame window is below its minimum, or if the combined
finite replay stream is below `min_instances`, return
`severity="not_applicable"` and do not run the detector.

## 5. Parameters

Accepted `params` keys and defaults for the first implementation:

| Param | Type | Default | Applies to | Meaning |
|---|---:|---:|---|---|
| `variant_id` | string | `PAGE_HINKLEY_INCREASE` | all | Variant selector. |
| `threshold` | float | `50.0` | supported variants | PH statistic alarm limit in the scale of the input signal. Must be positive. |
| `threshold_or_alpha` | float | optional | supported variants | Compatibility alias for `threshold`; must not conflict with explicit `threshold`. |
| `delta` | float | `0.005` | supported variants | Tolerance subtracted from directional deviations. Larger values ignore smaller mean movements. Must be non-negative. |
| `alpha` | float | optional | supported variants | Forgetting/smoothing compatibility parameter. First implementation records it only unless a backend explicitly supports it. |
| `min_instances` | int | `30` | supported variants | Minimum replay length before alarms are evaluated. |
| `direction` | string | inferred from variant | supported variants | `increase` or `decrease`; may not conflict with `variant_id`. |
| `reset_policy` | string | `after_alarm` | supported variants | State handling after an alarm: `after_alarm` or `none` in the first implementation. |
| `input_signal` | string | optional | supported variants | Value column name only when `value_col is None`; otherwise metadata label such as `loss`, `latency`, `confidence`, or `score`. |
| `min_reference_size` | int | `20` | supported variants | Minimum effective reference rows after invalid rows are dropped. |
| `min_current_size` | int | `20` | supported variants | Minimum effective current rows after invalid rows are dropped. |
| `nan_policy` | string | `drop` | supported variants | First implementation supports `drop`/`omit` only. |
| `check_every` | int | `1` | supported variants | Check interval in processed observations after `min_instances`. |
| `record_events` | bool | `True` | supported variants | Include compact alarm event history in measurements. |
| `max_event_records` | int | `50` | supported variants | Maximum number of alarm events retained in measurements. |
| `sample_imbalance_warning_ratio` | float | `10.0` | supported variants | Warn when larger input window size divided by smaller size exceeds this ratio. |

Parameter rules:

- `threshold` is an alarm limit on `PAGE_HINKLEY_STATISTIC`; it is not a
  p-value threshold.
- `threshold_or_alpha` is accepted only as a compatibility alias for
  `threshold`. If both are supplied and differ, return
  `severity="not_applicable"`.
- `delta` is the Page-Hinkley tolerance for small directional deviations. It
  must be `>= 0`.
- `alpha`, if supplied, is recorded in metadata with a warning unless the
  implementation uses a backend whose Page-Hinkley definition includes an
  `alpha` forgetting factor. It must not be interpreted as a p-value alpha.
- `min_instances`, `check_every`, `min_reference_size`, `min_current_size`, and
  `max_event_records` must be positive integers.
- `direction` must be `increase` for `PAGE_HINKLEY_INCREASE` and `decrease` for
  `PAGE_HINKLEY_DECREASE`.
- `reset_policy="after_alarm"` resets cumulative state after each alarm so that
  multiple events in one finite replay are auditable. `reset_policy="none"`
  leaves state unchanged after an alarm. Other policies are deferred.
- `nan_policy` supports `drop` and `omit` as aliases for dropping invalid rows.
  Other values return `not_applicable`.
- Reject or warn on unrelated params such as `feature_cols`, `embedding_cols`,
  `category_col`, `count_col`, raw label columns, classifier settings,
  distance-stream settings, or preprocessing functions.

## 6. Page-Hinkley Statistic and State Policy

Normalize the selected finite stream to one-dimensional arrays:

```python
stream_values = np.asarray(..., dtype=float)
stream_times = np.asarray(..., dtype="datetime64[ns]")
```

For both supported variants, transform values into the monitored direction:

```text
PAGE_HINKLEY_INCREASE: directional_value = value
PAGE_HINKLEY_DECREASE: directional_value = -value
```

Then run one cumulative-deviation detector:

```text
running_mean_t = mean(directional_value_1 ... directional_value_t)
cumulative_t = cumulative_{t-1} + directional_value_t - running_mean_t - delta
min_cumulative_t = min(min_cumulative_{t-1}, cumulative_t)
ph_statistic_t = cumulative_t - min_cumulative_t
alarm if ph_statistic_t > threshold after min_instances and check_every policy
```

Implementation-level pseudocode:

```text
events = []
running_mean = 0
cumulative = 0
min_cumulative = 0
max_statistic = 0

for index, (time, value) in chronological stream:
    directional = value if direction == "increase" else -value
    update running_mean with directional
    cumulative += directional - running_mean - delta
    min_cumulative = min(min_cumulative, cumulative)
    statistic = cumulative - min_cumulative
    max_statistic = max(max_statistic, statistic)

    if index + 1 < min_instances:
        continue
    if (index + 1 - min_instances) % check_every != 0:
        continue
    if statistic > threshold:
        record alarm event with time, index, statistic, running_mean
        if reset_policy == "after_alarm":
            cumulative = 0
            min_cumulative = 0
            restart or continue running_mean according to implementation policy
```

The first implementation should use one deterministic NumPy/Pandas
implementation rather than requiring network-installed streaming libraries. If
an optional backend is already available, it may be used only when its statistic
definition, `delta`, `threshold`, `alpha`, and reset behavior are recorded in
metadata.

The design does not require a top-level p-value. Page-Hinkley raises alarms via
its sequential statistic crossing a threshold. Do not label the PH statistic as
`P_VALUE`.

## 7. Output Measurements

`drift_method_variant_measurement_summary.csv` maps both DM-028 variants to:

```text
PAGE_HINKLEY_STATISTIC
DRIFT_ALARM_STATE
```

Return these canonical measurements for every successful supported run:

```python
{
    "PAGE_HINKLEY_STATISTIC": <final PH statistic>,
    "DRIFT_ALARM_STATE": <"drift_detected" | "normal">,
    "PH_STATISTIC": <same float as PAGE_HINKLEY_STATISTIC>,
    "MAX_PAGE_HINKLEY_STATISTIC": <max statistic seen during replay>,
    "THRESHOLD": <resolved threshold>,
    "DELTA": <resolved delta>,
    "DIRECTION": <"increase" | "decrease">,
    "RESET_POLICY": <resolved reset_policy>,
    "MIN_INSTANCES": <resolved min_instances>,
    "CHECK_EVERY": <resolved check_every>,
    "ALARM_COUNT": <int>,
    "FIRST_ALARM_TIME": <ISO timestamp or None>,
    "LAST_ALARM_TIME": <ISO timestamp or None>,
    "FIRST_ALARM_INDEX": <int or None>,
    "LAST_ALARM_INDEX": <int or None>,
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
    "REFERENCE_MEDIAN": <float>,
    "CURRENT_MEDIAN": <float>,
    "MEAN_DELTA": <current mean - reference mean>,
    "FINAL_RUNNING_MEAN": <float>,
    "FINAL_CUMULATIVE_DEVIATION": <float>,
    "FINAL_MIN_CUMULATIVE_DEVIATION": <float>,
}
```

When `record_events=True`, include a compact event list:

```python
{
    "ALARM_EVENTS": [
        {
            "time": <ISO timestamp>,
            "index": <zero-based stream index>,
            "page_hinkley_statistic": <float>,
            "threshold": <float>,
            "running_mean": <float>,
            "cumulative_deviation": <float>,
            "direction": <"increase" | "decrease">,
        },
        ...
    ]
}
```

Top-level `DriftResult` field mapping:

```text
method_id = "DM-028"
method_name = "Page-Hinkley Test"
method_category = "StreamingChangeDetector"
variant_id = resolved variant id
drift_score = max PAGE_HINKLEY_STATISTIC seen during replay
p_value = None
test_statistic = final PAGE_HINKLEY_STATISTIC
threshold = resolved threshold
```

Interpretation text should state:

- which variant and direction ran
- that reference/current windows were replayed as one finite chronological
  numeric stream
- effective reference/current/stream row counts
- resolved `threshold`, `delta`, `min_instances`, `check_every`, and
  `reset_policy`
- final and maximum PH statistic
- whether an alarm occurred, and first/last alarm time if applicable
- that Page-Hinkley on a numeric value stream is a sequential mean-change
  signal, not proof of root cause, model performance degradation, supervised
  concept drift, or retraining necessity

## 8. Algorithm Steps

1. Normalize `params` to an empty dict when omitted.
2. Resolve `variant_id`; default to `PAGE_HINKLEY_INCREASE`.
3. Reject unknown variants with `severity="not_applicable"` and a warning.
4. Reject DM-056 retraining variants or supervised detector requests inside
   this method.
5. Resolve direction from variant and validate any explicit `direction`.
6. Reject multivariate, embedding, categorical, count-table, raw label, and raw
   prediction requests in the first implementation.
7. Resolve `threshold`, `delta`, `min_instances`, `reset_policy`,
   `check_every`, `nan_policy`, event-recording settings, sample-size minima,
   and the value column.
8. Validate that both reference and current windows are supplied and parseable.
9. Validate required columns and scalar numeric value data. Boolean data is not
   valid Page-Hinkley numeric-stream input.
10. Convert and sort the DataFrame according to the common window handling
    contract.
11. Slice inclusive reference/current windows.
12. Reject overlapping windows unless an explicit overlap policy is added.
13. Drop rows with invalid timestamps or non-finite values; record original and
    effective counts.
14. If either effective sample is empty or below minimum, return not
    applicable.
15. Concatenate effective reference/current rows and sort by timestamp to form
    the finite replay stream.
16. If the effective stream length is below `min_instances`, return not
    applicable.
17. Add warnings for invalid rows, highly imbalanced sample sizes, small
    samples that pass the hard minimum, autocorrelation risk, seasonality, and
    any metadata-only `alpha`.
18. Direction-normalize values for increase or decrease monitoring.
19. Iterate each stream row in chronological order, updating running mean,
    cumulative deviation, minimum cumulative deviation, current PH statistic,
    and maximum PH statistic.
20. After `min_instances` and according to `check_every`, compare
    `PAGE_HINKLEY_STATISTIC > threshold`.
21. Record alarm events and apply `reset_policy`.
22. Compute final sample summaries, final state, alarm summary, and maximum
    statistic.
23. Apply the drift decision rule from section 9.
24. Build `DriftResult` with method identity, variant, canonical measurements,
    helper summaries, counts, windows, parameters, warnings, metadata, and
    concise interpretation text.

## 9. Drift Decision Rule

Streaming alarm rule for both supported variants:

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

Use strict `PAGE_HINKLEY_STATISTIC > threshold`, not `>= threshold`, for each
eligible check. Equality is not drift. `threshold` in the top-level result is
the resolved PH threshold. `p_value` remains `None`.

For report wording:

- increase alarm: "Page-Hinkley raised an increase-direction mean-stream alarm
  while replaying the selected reference/current rows"
- decrease alarm: "Page-Hinkley raised a decrease-direction mean-stream alarm
  while replaying the selected reference/current rows"
- no alarm: "no Page-Hinkley alarm was raised under this finite replay,
  threshold, delta, and reset policy"
- unsupported supervised request: "supervised Page-Hinkley requires an explicit
  error stream contract"
- retraining request: "DRIFT_RETRAINING_WITH_PAGE_HINKLEY belongs to DM-056 and
  requires retraining policy inputs"

The Page-Hinkley result depends on stream order, direction, `threshold`,
`delta`, `min_instances`, reset policy, sample count, and finite replay scope.
It must not be compared directly with ADWIN, KSWIN, CUSUM, EWMA, GMA, BOCD, or
batch two-sample tests without method and variant context.

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
- effective stream length below `min_instances`
- unsupported or unknown `variant_id`
- `DRIFT_RETRAINING_WITH_PAGE_HINKLEY` or other DM-056 retraining requests
- supervised error-rate Page-Hinkley requests until label/error-stream handling
  is approved
- `feature_cols`, `embedding_cols`, object embeddings, list-valued rows,
  category/count columns, raw `y_true`/`y_pred` requests, or other non-scalar
  inputs in the first implementation
- invalid `threshold`, conflicting `threshold` and `threshold_or_alpha`,
  invalid `delta`, conflicting variant and `direction`, invalid
  `min_instances`, `reset_policy`, `check_every`, event-record settings,
  `nan_policy`, sample-size parameter, or warning-ratio parameter
- current/reference window overlap when overlap policy is not explicitly
  defined by the implementation
- backend missing when a non-NumPy optional backend was explicitly requested
- non-finite PH statistic or non-finite running state

Return `severity="normal"` or `"drift_detected"` with warnings when the method
can still run but interpretation needs caution:

- timestamps or values were dropped because they were invalid or non-finite
- `threshold_or_alpha` was interpreted as PH `threshold`
- `alpha` was supplied but recorded only because the first implementation does
  not use a forgetting factor
- reference/current sample sizes are highly imbalanced
- effective stream length is only slightly above `min_instances`
- observations are autocorrelated time-series rows rather than independent
  draws
- strong seasonality, batch collection cycles, or traffic mix changes may
  trigger mean alarms that are operational-pattern changes rather than drift
- `threshold` is unusually low or high relative to the value scale
- `delta` is unusually high and may suppress small sustained shifts
- `check_every > 1` may delay or miss alarms between check points
- event history was truncated by `max_event_records`

Unexpected backend or numeric exceptions should return `severity="error"` or
`"watch"` according to project convention, with `drift_detected=None` and a
clear warning, without raising through the public detector boundary.

Do not silently coerce categorical values, boolean flags, labels, embeddings,
lists, object arrays, count tables, or multivariate matrices into the
univariate Page-Hinkley detector.

## 11. Implementation Target

```text
module: drift_algorithm.methods.streamingchangedetector
function: detect_page_hinkley_test
```

Expected dependencies:

```text
pandas
numpy
```

Optional backend:

```text
river.drift.PageHinkley, only if already available in the project environment
```

The first implementation must be able to run without adding a new network
dependency. If an optional backend is used, its threshold, delta, alpha, warmup,
and reset semantics must be checked against this design and recorded in
metadata.

Expected result object:

```text
DriftResult from drift_algorithm/docs/input_output_contracts.md equivalent code
contract
```

Helper functions should follow existing project patterns:

- add `PAGE_HINKLEY_METHOD_ID = "DM-028"` and
  `PAGE_HINKLEY_METHOD_NAME = "Page-Hinkley Test"`
- define `SUPPORTED_PAGE_HINKLEY_VARIANTS` for `PAGE_HINKLEY_INCREASE` and
  `PAGE_HINKLEY_DECREASE`
- use the common `DriftResult` dataclass
- use `not_applicable_result` or a method-specific not-applicable helper for
  validation failures
- reuse common numeric-window preparation where it matches the finite replay
  contract, but ensure the final stream is sorted chronologically
- keep Page-Hinkley helpers private to the module unless another streaming
  detector already exposes a shared helper
- record backend name, finite-replay policy, direction, value column, effective
  windows, resolved parameters, sample-size metadata, and unsupported/deferred
  variant decisions so the result is auditable

Suggested private helper shape:

```python
def _page_hinkley_not_applicable(
    variant_id: str | None,
    warning: str,
    metadata: dict[str, Any] | None = None,
    prior_warnings: list[str] | None = None,
) -> DriftResult:
    ...

def _resolve_page_hinkley_params(params: dict[str, Any]) -> dict[str, Any]:
    ...

def _prepare_page_hinkley_stream(
    data: pd.DataFrame,
    *,
    time_col: str,
    value_col: str,
    reference_window: tuple[str, str],
    current_window: tuple[str, str],
    params: dict[str, Any],
) -> dict[str, Any]:
    ...

def _run_page_hinkley_stream(
    values: np.ndarray,
    times: np.ndarray,
    *,
    direction: str,
    threshold: float,
    delta: float,
    min_instances: int,
    check_every: int,
    reset_policy: str,
    record_events: bool,
    max_event_records: int,
) -> dict[str, Any]:
    ...
```

Public contract:

- `detect_page_hinkley_test` must be importable from
  `drift_algorithm.methods.streamingchangedetector`.
- The function must accept the common arguments exactly as shown in section 4.
- It must return `DriftResult`, never raw tuples or dictionaries.
- Validation failures must return `severity="not_applicable"` unless they are
  unexpected numeric/runtime errors.
- The first implementation must not fabricate a p-value.
- `threshold` in the result must contain the resolved PH statistic threshold.
- `PAGE_HINKLEY_DECREASE` must be a real decrease-direction detector, not an
  increase detector reported under a different variant id.
- Retraining and supervised error-rate variants must be explicit
  `not_applicable` results until their separate contracts are approved.

## 12. Verification Plan

Unit tests for the first implementation:

1. Default no-alarm finite replay:
   - Generate stable numeric reference/current rows from the same distribution
     with deterministic timestamps.
   - Omit `variant_id` and Page-Hinkley settings.
   - Assert `variant_id == "PAGE_HINKLEY_INCREASE"`.
   - Assert `PAGE_HINKLEY_STATISTIC`, `DRIFT_ALARM_STATE`, `THRESHOLD`,
     `DELTA`, `DIRECTION`, `ALARM_COUNT`, `PROCESSED_COUNT`, `SAMPLE_SIZE`,
     `SAMPLE_SIZE_REFERENCE`, and `SAMPLE_SIZE_CURRENT` exist.
   - Assert `p_value is None`, `drift_detected is False`,
     `severity == "normal"`, and `DRIFT_ALARM_STATE == "normal"` for a stable
     deterministic stream.
2. Increase-direction alarm:
   - Generate reference values around one mean and current values with a clear
     upward shift.
   - Use deterministic `threshold`, `delta`, and `min_instances` chosen to
     produce an alarm.
   - Assert `ALARM_COUNT > 0`, `drift_detected is True`,
     `severity == "drift_detected"`, and first/last alarm metadata is present.
3. Decrease-direction alarm:
   - Generate reference values around one mean and current values with a clear
     downward shift.
   - Use `variant_id="PAGE_HINKLEY_DECREASE"`.
   - Assert the decrease variant alarms and records `DIRECTION == "decrease"`.
   - Assert the same data does not rely on reporting the increase variant id.
4. Parameter alias and validation:
   - Assert `threshold_or_alpha` is treated as `threshold`.
   - Assert conflicting `threshold` and `threshold_or_alpha` return
     `severity="not_applicable"`.
   - Assert invalid `threshold`, `delta`, `alpha`, `min_instances`,
     `direction`, `reset_policy`, `check_every`, `record_events`,
     `max_event_records`, `nan_policy`, and sample-size settings return not
     applicable.
5. Window and stream ordering:
   - Provide unsorted input rows and assert processed counts and alarm event
     indices follow chronological order.
   - Assert missing windows, unparseable windows, empty slices, insufficient
     sample sizes, stream shorter than `min_instances`, and overlapping windows
     return `not_applicable`.
6. Schema validation:
   - Missing value column.
   - Non-numeric, boolean, object/list, embedding-like, categorical, or text
     value column.
   - Invalid timestamps and non-finite values are dropped with warnings and
     effective counts.
7. Event recording and reset:
   - With `record_events=True`, assert `ALARM_EVENTS` is present and bounded by
     `max_event_records`.
   - With `record_events=False`, assert detailed events can be omitted while
     alarm count and first/last alarm summaries remain available.
   - Compare `reset_policy="after_alarm"` and `reset_policy="none"` on a stream
     with sustained shift and assert alarm count/state behavior is auditable.
8. Warning behavior:
   - Imbalanced sample sizes produce a caution warning.
   - `alpha` supplied without a supported forgetting-factor backend produces a
     metadata-only warning.
   - `check_every > 1` records that alarm checks are periodic.
   - Event truncation is recorded as a warning.
9. Deferred and unrelated requests:
   - Supplying DM-056 `DRIFT_RETRAINING_WITH_PAGE_HINKLEY` returns
     `severity="not_applicable"` with a retraining-policy warning.
   - Supplying raw `y_true`/`y_pred`, `feature_cols`, `embedding_cols`, or
     distance-stream settings does not trigger silent coercion.
10. Backend/numeric failure:
   - Simulate non-finite PH state or optional backend failure.
   - Assert the public detector returns `severity="error"`, `"watch"`, or
     `not_applicable` according to project convention with
     `drift_detected=None` and a clear warning.

Recommended commands after implementation:

```text
python -m py_compile drift_algorithm\methods\streamingchangedetector.py
python -m pytest tests\test_page_hinkley_test.py
python -m pytest tests\test_adwin.py tests\test_kswin.py
```

Manual review before marking implementation complete:

- Confirm public function signature matches the common contract.
- Confirm canonical measurement names match
  `drift_method_variant_measurement_summary.csv`.
- Confirm default variant is `PAGE_HINKLEY_INCREASE`.
- Confirm `reference_window` and `current_window` define a finite replay stream
  rather than a batch two-sample statistic.
- Confirm `PAGE_HINKLEY_DECREASE` uses direction normalization or an equivalent
  decrease-specific formula.
- Confirm strict `PAGE_HINKLEY_STATISTIC > threshold` is used.
- Confirm top-level `threshold` stores resolved PH threshold.
- Confirm top-level `p_value` remains `None`.
- Confirm event history and final PH state are auditable.
- Confirm supervised error-rate and retraining requests fail explicitly instead
  of being silently interpreted as generic numeric streams.
- Confirm interpretation text avoids root-cause, performance-degradation,
  supervised concept-drift, and retraining claims without labeled evidence and
  policy inputs.

## 13. Manager Review Points

- First implementation scope is `PAGE_HINKLEY_INCREASE` and
  `PAGE_HINKLEY_DECREASE` over scalar numeric `(time, value)` rows only.
- Although Page-Hinkley is streaming, the current public API supplies finite
  timestamp windows; this design replays reference/current rows in
  chronological order and reports the resulting sequential alarm state.
- `reference_window` and `current_window` are required for API consistency and
  for defining replay scope, but the algorithm is not a batch
  reference-vs-current test.
- Proposed defaults are `threshold=50.0`, `delta=0.005`,
  `min_instances=30`, `check_every=1`, and `reset_policy="after_alarm"`;
  these should be reviewed against any chosen backend and value scale.
- `threshold_or_alpha` is only a compatibility alias for `threshold`; Page-
  Hinkley does not return a p-value and `alpha` is metadata-only unless an
  approved backend uses it.
- `PAGE_HINKLEY_DECREASE` is supported by direction normalization, not deferred.
- Supervised error-rate Page-Hinkley and
  `DRIFT_RETRAINING_WITH_PAGE_HINKLEY` remain deferred to avoid conflating
  generic numeric streams with model performance or retraining policy.
- The public target is `detect_page_hinkley_test` in
  `drift_algorithm.methods.streamingchangedetector`.
