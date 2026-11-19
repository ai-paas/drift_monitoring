# DM-026 ADWIN Design

## 1. Method Identity

- Method ID: `DM-026`
- Method name: `ADWIN`
- Category: `StreamingChangeDetector`
- Method kind: `detector`
- Status: `확정`
- Source catalog: `drift_methods_catalog.md`
- Source variant document: `algorithm_variants/adwin_algorithm_variants.md`
- Source parameter tables:
  - `drift_method_variant_links.csv`
  - `drift_method_variant_measurement_summary.csv`
  - `drift_method_variant_parameters.csv`
  - `drift_method_parameter_guide.md`

The first implementation is a univariate numeric streaming detector executed
over a finite DataFrame slice. It accepts the common `(time, value)` pandas
DataFrame contract, sorts rows by time, slices the supplied reference/current
timestamp windows, concatenates the two slices in time order, and feeds the
values to an ADWIN mean-change detector. The result reports the final adaptive
window state and whether any alarm occurred while replaying the requested
stream.

## 2. Purpose

`ADWIN` detects changes in the mean level of a numeric stream by maintaining an
adaptive window and dropping older observations when a statistically meaningful
difference is found between older and newer subwindows. In the catalog it can
represent numeric metric streams, error streams, or distance-score streams.

The first implementation intentionally narrows that catalog scope to scalar
numeric `(time, value)` rows because the public function receives finite
DataFrame windows, not an open-ended online iterator. It should be read as:

```text
Replay the selected reference/current rows as a time-ordered stream and report
whether ADWIN raised a mean-level alarm during that replay.
```

Use the first implementation when:

- the monitored signal is one scalar numeric column
- the caller can provide timestamp ranges for `reference_window` and
  `current_window`
- the question is whether a streaming mean-change detector would alarm while
  processing those rows in chronological order
- final adaptive window width, last-window mean, and alarm history are useful
  monitoring outputs

Do not use the first implementation for categorical labels, probability
vectors, raw embeddings, multivariate feature matrices, text, SHAP matrices, or
raw supervised prediction pairs. Those require another method family or a
future ADWIN variant contract.

## 3. Supported Variants

Supported for the first implementation:

- `ADWIN_MEAN_STREAM`
  - Default variant.
  - Uses scalar numeric reference/current windows as a finite stream replay.
  - Detects changes in the mean of the input signal.
  - Returns a binary streaming alarm based on ADWIN's internal cut rule.
  - Records final adaptive window width, final window mean, alarm count, and
    optional event history.

Deferred until separate contracts are approved:

- `ADWIN_ERROR_RATE`
  - Requires a label/error schema, `error_col` or `y_true`/`y_pred` handling,
    label-delay policy, and error definition.
  - Must return `severity="not_applicable"` in the first implementation unless
    manager explicitly approves mapping a precomputed numeric `value` error
    stream to `ADWIN_MEAN_STREAM`.
  - Must not infer supervised performance drift from unlabeled numeric values.
- `ADWIN_DISTANCE_STREAM`
  - Requires a documented upstream distance series contract, including
    `base_distance_method`, `distance_window_size`, whether each row already is
    a distance, and how the original detector threshold differs from ADWIN's
    `delta`.
  - Must return `severity="not_applicable"` in the first implementation.
  - Must not compute Wasserstein, MMD, PSI, or other distance values inside
    `detect_adwin`.

Default variant selection:

```text
if params["variant_id"] is omitted:
    variant_id = "ADWIN_MEAN_STREAM"
```

## 4. Input Schema

Use the common `pandas.DataFrame` input boundary from
`../input_output_contracts.md`.

Public function shape:

```python
def detect_adwin(
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

Required DataFrame schema for `ADWIN_MEAN_STREAM`:

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

Even though ADWIN is a streaming detector, the first public API still requires
both windows. They define the finite stream replay scope:

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
ADWIN_MEAN_STREAM:
  min_reference_size: default 20
  min_current_size: default 20
  grace_period: default max(20, min_window_length * 2)
```

The implementation default keeps very short finite replays from producing
unstable alarms. If either effective window is below its minimum, return
`severity="not_applicable"` and do not run the detector.

## 5. Parameters

Accepted `params` keys and defaults for the first implementation:

| Param | Type | Default | Applies to | Meaning |
|---|---:|---:|---|---|
| `variant_id` | string | `ADWIN_MEAN_STREAM` | all | Variant selector. |
| `delta` | float | `0.002` | supported variant | ADWIN false-alarm sensitivity. Must satisfy `0 < delta < 1`. |
| `threshold_or_alpha` | float | optional | supported variant | Alias for `delta`; must not conflict with explicit `delta`. |
| `clock` | int | `1` | supported variant | Check interval in processed observations. `1` checks after every row. |
| `max_buckets` | int | `5` | supported variant | Maximum bucket count per bucket row for ADWIN's compressed window. |
| `min_window_length` | int | `5` | supported variant | Minimum older/newer subwindow length considered for a cut. |
| `grace_period` | int | `20` | supported variant | Minimum processed observations before alarms are evaluated. |
| `input_signal` | string | optional | supported variant | Value column name only when `value_col is None`; otherwise metadata label such as `feature`, `score`, `loss`, or `latency`. |
| `min_reference_size` | int | `20` | supported variant | Minimum effective reference rows after invalid rows are dropped. |
| `min_current_size` | int | `20` | supported variant | Minimum effective current rows after invalid rows are dropped. |
| `nan_policy` | string | `drop` | supported variant | First implementation supports `drop`/`omit` only. |
| `record_events` | bool | `True` | supported variant | Include compact alarm event history in measurements. |
| `max_event_records` | int | `50` | supported variant | Maximum number of alarm events retained in measurements. |
| `sample_imbalance_warning_ratio` | float | `10.0` | supported variant | Warn when larger window size divided by smaller size exceeds this ratio. |
| `multiple_testing_correction` | string | `none` | supported variant | Recorded as metadata only. Correction is not applied inside ADWIN. |

Parameter rules:

- `delta` is ADWIN's detector sensitivity, not a p-value returned by this
  method. Lower values are more conservative and may delay detection.
- `threshold_or_alpha` is accepted only as a compatibility alias for `delta`.
  If both are supplied and differ, return `severity="not_applicable"`.
- `clock`, `max_buckets`, `min_window_length`, `grace_period`,
  `min_reference_size`, `min_current_size`, and `max_event_records` must be
  positive integers.
- `nan_policy` supports `drop` and `omit` as aliases for dropping invalid rows.
  Other values return `not_applicable`.
- `record_events=False` may omit detailed event rows but must still return
  `ALARM_COUNT`, `FIRST_ALARM_TIME`, and `LAST_ALARM_TIME` when applicable.
- `multiple_testing_correction != "none"` adds a warning and is recorded in
  metadata; this detector does not apply correction internally.
- Reject or warn on unrelated params such as `feature_cols`, `embedding_cols`,
  `category_col`, `count_col`, raw label columns, classifier settings,
  `base_distance_method`, or `distance_window_size` unless the matching
  deferred variant is implemented.

## 6. ADWIN Statistic and State Policy

Normalize the selected finite stream to a one-dimensional array:

```python
stream_values = np.asarray(..., dtype=float)
stream_times = np.asarray(..., dtype="datetime64[ns]")
```

The implementation should use a deterministic ADWIN mean-change algorithm. A
River-compatible backend may be used if already available, but the public
contract must not require network downloads. If implemented directly, the
detector should maintain a compressed adaptive window with bucket rows and
evaluate candidate cuts using ADWIN's mean-difference bound.

Implementation-level pseudocode:

```text
state = empty_adwin_state(delta, max_buckets)
for index, (time, value) in chronological stream:
    state.add(value)
    if index + 1 < grace_period:
        continue
    if (index + 1) % clock != 0:
        continue
    while state has a valid cut with both sides >= min_window_length:
        if abs(mean_recent - mean_old) > adwin_bound(delta, n_old, n_recent):
            drop the older side from the adaptive window
            record alarm event with time, index, width before/after, means
        else:
            break
```

The design does not require a top-level p-value because ADWIN raises alarms via
its internal confidence bound. If a backend exposes an internal epsilon or
cut statistic, record it as helper measurements or metadata, but do not label
it as `P_VALUE`.

When multiple alarms occur during one finite replay:

- top-level `drift_detected=True` if at least one alarm occurred
- `severity="drift_detected"` if at least one alarm occurred
- `DRIFT_ALARM_STATE="drift_detected"` if at least one alarm occurred
- `FIRST_ALARM_*` and `LAST_ALARM_*` identify the first and last alarms
- final adaptive window measurements describe the state after all rows are
  processed

If no alarm occurs:

- `drift_detected=False`
- `severity="normal"`
- `DRIFT_ALARM_STATE="normal"`

## 7. Output Measurements

`drift_method_variant_measurement_summary.csv` maps `ADWIN_MEAN_STREAM` to:

```text
WINDOW_SIZE
DRIFT_ALARM_STATE
```

Return these canonical measurements for every successful supported run:

```python
{
    "DRIFT_ALARM_STATE": <"drift_detected" | "normal">,
    "WINDOW_SIZE": <final adaptive window width>,
    "ADAPTIVE_WINDOW_WIDTH": <same int as WINDOW_SIZE>,
    "ALARM_COUNT": <int>,
    "FIRST_ALARM_TIME": <ISO timestamp or None>,
    "LAST_ALARM_TIME": <ISO timestamp or None>,
    "FIRST_ALARM_INDEX": <int or None>,
    "LAST_ALARM_INDEX": <int or None>,
    "FINAL_WINDOW_MEAN": <float>,
    "FINAL_WINDOW_VARIANCE": <float or None>,
    "FINAL_WINDOW_MIN": <float>,
    "FINAL_WINDOW_MAX": <float>,
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
    "DELTA": <resolved ADWIN delta>,
    "CLOCK": <resolved clock>,
    "MAX_BUCKETS": <resolved max_buckets>,
    "MIN_WINDOW_LENGTH": <resolved min_window_length>,
    "GRACE_PERIOD": <resolved grace_period>,
}
```

When `record_events=True`, include a compact event list:

```python
{
    "ALARM_EVENTS": [
        {
            "time": <ISO timestamp>,
            "index": <zero-based stream index>,
            "width_before": <int>,
            "width_after": <int>,
            "mean_before_cut": <float>,
            "mean_after_cut": <float>,
            "cut_epsilon": <float if available>,
        },
        ...
    ]
}
```

For `ADWIN_ERROR_RATE`, once implemented later, also return canonical
`ERROR_RATE`. In the first implementation this variant is deferred and should
not fabricate `ERROR_RATE` from an arbitrary numeric value stream.

Top-level `DriftResult` field mapping:

```text
method_id = "DM-026"
method_name = "ADWIN"
method_category = "StreamingChangeDetector"
variant_id = resolved variant id
drift_score = None, or final absolute cut statistic if a backend exposes one
p_value = None
test_statistic = None, or final cut statistic if a backend exposes one
threshold = resolved delta
```

Interpretation text should state:

- which variant ran
- that reference/current windows were replayed as one finite chronological
  stream
- effective reference/current/stream row counts
- resolved `delta`, `clock`, `max_buckets`, `min_window_length`, and
  `grace_period`
- final adaptive window width and final window mean
- whether an alarm occurred, and first/last alarm time if applicable
- that ADWIN on a numeric value stream is a mean-level change signal, not proof
  of root cause, model performance degradation, or supervised concept drift

## 8. Algorithm Steps

1. Normalize `params` to an empty dict when omitted.
2. Resolve `variant_id`; default to `ADWIN_MEAN_STREAM`.
3. Reject unknown variants with `severity="not_applicable"` and a warning.
4. Reject `ADWIN_ERROR_RATE` and `ADWIN_DISTANCE_STREAM` with
   `severity="not_applicable"` until their separate input contracts are
   approved.
5. Reject multivariate, embedding, categorical, count-table, raw label, and raw
   prediction requests in the first implementation.
6. Resolve `delta`, `clock`, `max_buckets`, `min_window_length`,
   `grace_period`, `nan_policy`, event-recording settings, sample-size minima,
   and the value column.
7. Validate that both reference and current windows are supplied and parseable.
8. Validate required columns and scalar numeric value data. Boolean data is not
   valid ADWIN numeric-stream input.
9. Convert and sort the DataFrame according to the common window handling
   contract.
10. Slice inclusive reference/current windows.
11. Reject overlapping windows unless an explicit overlap policy is added.
12. Drop rows with invalid timestamps or non-finite values; record original and
    effective counts.
13. If either effective sample is empty or below minimum, return not
    applicable.
14. Concatenate effective reference/current rows and sort by timestamp to form
    the finite replay stream.
15. Add warnings for invalid rows, highly imbalanced sample sizes, repeated or
    degenerate values, small samples that pass the hard minimum, autocorrelation
    risk, and multiple-testing metadata when applicable.
16. Initialize ADWIN state with the resolved `delta` and `max_buckets`.
17. Iterate each stream row in chronological order, updating adaptive-window
    state.
18. After `grace_period` and according to `clock`, evaluate candidate cuts with
    both sides at least `min_window_length`.
19. Record each alarm event and drop old observations according to ADWIN's
    adaptive-window rule.
20. Compute final adaptive-window width, final mean, final variance, sample
    summaries, and alarm summary.
21. Apply the drift decision rule from section 9.
22. Build `DriftResult` with method identity, variant, canonical measurements,
    helper summaries, counts, windows, parameters, warnings, metadata, and
    concise interpretation text.

## 9. Drift Decision Rule

Streaming alarm rule for `ADWIN_MEAN_STREAM`:

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

No separate score threshold is used in the first implementation. `threshold`
in the top-level result is the resolved ADWIN `delta` for auditability, not a
distance-score threshold. `p_value` remains `None`.

For report wording:

- alarm: "ADWIN raised a numeric mean-stream alarm while replaying the selected
  reference/current rows"
- no alarm: "no ADWIN alarm was raised under this finite replay, delta, and
  window policy"
- deferred error-rate request: "ADWIN_ERROR_RATE requires an explicit
  supervised error stream contract"
- deferred distance-stream request: "ADWIN_DISTANCE_STREAM requires a
  precomputed distance stream contract"

The ADWIN result depends on stream order, `delta`, compression settings,
minimum cut length, sample count, and the finite replay scope. It must not be
compared directly with KS, Wasserstein, MMD, LSDD, Page-Hinkley, CUSUM, or EWMA
without method and variant context.

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
- unsupported or unknown `variant_id`
- `ADWIN_ERROR_RATE` until label/error-stream handling is approved
- `ADWIN_DISTANCE_STREAM` until precomputed distance-stream handling is
  approved
- `feature_cols`, `embedding_cols`, object embeddings, list-valued rows,
  category/count columns, raw `y_true`/`y_pred` requests, or other non-scalar
  inputs in the first implementation
- invalid `delta`, conflicting `delta` and `threshold_or_alpha`, `clock`,
  `max_buckets`, `min_window_length`, `grace_period`, event-record settings,
  `nan_policy`, sample-size parameter, or warning-ratio parameter
- current/reference window overlap when overlap policy is not explicitly
  defined by the implementation
- backend missing when a non-NumPy optional backend was explicitly requested
- non-finite adaptive-window statistics

Return `severity="normal"` or `"drift_detected"` with warnings when the method
can still run but interpretation needs caution:

- timestamps or values were dropped because they were invalid or non-finite
- `threshold_or_alpha` was interpreted as ADWIN `delta`
- reference/current sample sizes are highly imbalanced
- effective stream length is only slightly above `grace_period`
- values are repeated, rounded, or tied, making the signal effectively
  discrete
- observations are autocorrelated time-series rows rather than independent
  draws
- strong seasonality, batch collection cycles, or traffic mix changes may
  trigger mean alarms that are operational-pattern changes rather than drift
- `delta` is unusually high or low for the project defaults
- `clock > 1` may delay or miss alarms between check points
- event history was truncated by `max_event_records`
- `multiple_testing_correction` is not `"none"`; record that this detector does
  not apply correction internally

Unexpected backend or numeric exceptions should return `severity="error"` or
`"watch"` according to project convention, with `drift_detected=None` and a
clear warning, without raising through the public detector boundary.

Do not silently coerce categorical values, boolean flags, labels, embeddings,
lists, object arrays, count tables, or multivariate matrices into the
univariate ADWIN mean-stream detector.

## 11. Implementation Target

```text
module: drift_algorithm.methods.streamingchangedetector
function: detect_adwin
```

Expected dependencies:

```text
pandas
numpy
```

Optional backend:

```text
river.drift.ADWIN, only if already available in the project environment
```

The first implementation must be able to run without adding a new network
dependency. If `river` is not already present, implement the required ADWIN
state directly or return a clear manager-reviewed implementation decision
before coding.

Expected result object:

```text
DriftResult from drift_algorithm/docs/input_output_contracts.md equivalent code
contract
```

Helper functions should follow existing project patterns:

- add `ADWIN_METHOD_ID = "DM-026"` and `ADWIN_METHOD_NAME = "ADWIN"`
- define `SUPPORTED_ADWIN_VARIANTS` for `ADWIN_MEAN_STREAM`
- define `DEFERRED_ADWIN_VARIANTS` for `ADWIN_ERROR_RATE` and
  `ADWIN_DISTANCE_STREAM`
- use the common `DriftResult` dataclass
- use `not_applicable_result` or a method-specific not-applicable helper for
  validation failures
- reuse common numeric-window preparation where it matches the finite replay
  contract, but ensure the final stream is sorted chronologically
- keep ADWIN state helpers private to the module unless another streaming
  detector already exposes a shared helper
- record backend name, finite-replay policy, value column, effective windows,
  resolved parameters, sample-size metadata, and unsupported/deferred variant
  decisions so the result is auditable

Suggested private helper shape:

```python
def _adwin_not_applicable(
    variant_id: str | None,
    warning: str,
    metadata: dict[str, Any] | None = None,
    prior_warnings: list[str] | None = None,
) -> DriftResult:
    ...

def _resolve_adwin_params(params: dict[str, Any]) -> dict[str, Any]:
    ...

def _prepare_adwin_stream(
    data: pd.DataFrame,
    *,
    time_col: str,
    value_col: str,
    reference_window: tuple[str, str],
    current_window: tuple[str, str],
    params: dict[str, Any],
) -> dict[str, Any]:
    ...

def _run_adwin_mean_stream(
    values: np.ndarray,
    times: np.ndarray,
    *,
    delta: float,
    clock: int,
    max_buckets: int,
    min_window_length: int,
    grace_period: int,
    record_events: bool,
    max_event_records: int,
) -> dict[str, Any]:
    ...
```

Public contract:

- `detect_adwin` must be importable from
  `drift_algorithm.methods.streamingchangedetector`.
- The function must accept the common arguments exactly as shown in section 4.
- It must return `DriftResult`, never raw tuples or dictionaries.
- Validation failures must return `severity="not_applicable"` unless they are
  unexpected numeric/runtime errors.
- The first implementation must not fabricate a p-value.
- `threshold` in the result must contain the resolved `delta`, not a separate
  score threshold.
- Error-rate and distance-stream variants must be explicit `not_applicable`
  results until their separate contracts are approved.

## 12. Verification Plan

Unit tests for the first implementation:

1. Default no-alarm finite replay:
   - Generate stable numeric reference/current rows from the same distribution
     with deterministic timestamps.
   - Omit `variant_id` and ADWIN settings.
   - Assert `variant_id == "ADWIN_MEAN_STREAM"`.
   - Assert `DRIFT_ALARM_STATE`, `WINDOW_SIZE`, `ADAPTIVE_WINDOW_WIDTH`,
     `ALARM_COUNT`, `PROCESSED_COUNT`, `SAMPLE_SIZE`,
     `SAMPLE_SIZE_REFERENCE`, and `SAMPLE_SIZE_CURRENT` exist.
   - Assert `p_value is None`, `drift_detected is False`,
     `severity == "normal"`, and `DRIFT_ALARM_STATE == "normal"`.
2. Mean-shift alarm:
   - Generate reference values around one mean and current values with a clear
     level shift.
   - Use deterministic `delta`, `grace_period`, and `min_window_length` chosen
     to produce an alarm.
   - Assert `ALARM_COUNT > 0`, `drift_detected is True`,
     `severity == "drift_detected"`, and first/last alarm metadata is present.
3. Parameter alias and validation:
   - Assert `threshold_or_alpha` is treated as `delta`.
   - Assert conflicting `delta` and `threshold_or_alpha` return
     `severity="not_applicable"`.
   - Assert invalid `delta`, `clock`, `max_buckets`, `min_window_length`,
     `grace_period`, `record_events`, `max_event_records`, `nan_policy`, and
     sample-size settings return not applicable.
4. Window and stream ordering:
   - Provide unsorted input rows and assert processed counts and alarm event
     indices follow chronological order.
   - Assert missing windows, unparseable windows, empty slices, insufficient
     sample sizes, and overlapping windows return `not_applicable`.
5. Schema validation:
   - Missing value column.
   - Non-numeric, boolean, object/list, embedding-like, categorical, or text
     value column.
   - Invalid timestamps and non-finite values are dropped with warnings and
     effective counts.
6. Deferred variants:
   - `ADWIN_ERROR_RATE` returns `severity="not_applicable"` with a warning
     about the supervised error-stream contract.
   - `ADWIN_DISTANCE_STREAM` returns `severity="not_applicable"` with a warning
     about the precomputed distance-stream contract.
   - Supplying `base_distance_method`, `distance_window_size`, raw
     `y_true`/`y_pred`, `feature_cols`, or `embedding_cols` does not trigger
     silent coercion.
7. Event recording:
   - With `record_events=True`, assert `ALARM_EVENTS` is present and bounded by
     `max_event_records`.
   - With `record_events=False`, assert detailed events can be omitted while
     alarm count and first/last alarm summaries remain available.
8. Warning behavior:
   - Imbalanced sample sizes produce a caution warning.
   - `clock > 1` records that alarm checks are periodic.
   - Event truncation and `multiple_testing_correction != "none"` are recorded
     as warnings.
9. Backend/numeric failure:
   - Simulate non-finite adaptive-window statistics or optional backend
     failure.
   - Assert the public detector returns `severity="error"`, `"watch"`, or
     `not_applicable` according to project convention with
     `drift_detected=None` and a clear warning.

Recommended commands after implementation:

```text
python -m py_compile drift_algorithm\methods\streamingchangedetector.py
python -m pytest tests\test_adwin.py
python -m pytest tests\test_kswin.py tests\test_page_hinkley_test.py
```

Manual review before marking implementation complete:

- Confirm public function signature matches the common contract.
- Confirm canonical measurement names match
  `drift_method_variant_measurement_summary.csv`.
- Confirm default variant is `ADWIN_MEAN_STREAM`.
- Confirm `reference_window` and `current_window` define a finite replay stream
  rather than a batch two-sample statistic.
- Confirm `delta` is the ADWIN confidence/sensitivity parameter and no p-value
  is fabricated.
- Confirm top-level `threshold` stores resolved `delta`.
- Confirm event history and final adaptive window state are auditable.
- Confirm error-rate and distance-stream requests fail explicitly instead of
  being silently interpreted as generic numeric streams.
- Confirm interpretation text avoids root-cause, performance-degradation, and
  supervised concept-drift claims without labeled evidence.

## 13. Manager Review Points

- First implementation scope is `ADWIN_MEAN_STREAM` over scalar numeric
  `(time, value)` rows only.
- Although ADWIN is streaming, the current public API supplies finite
  timestamp windows; this design replays reference/current rows in chronological
  order and reports the resulting streaming state.
- `reference_window` and `current_window` are required for API consistency and
  for defining replay scope, but the algorithm is not a batch reference-vs-
  current test.
- Default `delta=0.002`, `clock=1`, `max_buckets=5`,
  `min_window_length=5`, and `grace_period=20` are proposed implementation
  defaults and should be reviewed against any chosen backend.
- Top-level `p_value` remains `None`; top-level `threshold` records resolved
  ADWIN `delta`.
- `ADWIN_ERROR_RATE` and `ADWIN_DISTANCE_STREAM` remain deferred to avoid
  silently conflating supervised error streams or upstream distance streams
  with generic numeric values.
- The public target is `detect_adwin` in
  `drift_algorithm.methods.streamingchangedetector`.
