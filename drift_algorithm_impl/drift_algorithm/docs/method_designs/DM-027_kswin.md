# DM-027 KSWIN Design

## 1. Method Identity

- Method ID: `DM-027`
- Method name: `KSWIN`
- Category: `StreamingChangeDetector`
- Method kind: `detector`
- Status: `확정`
- Source catalog: `drift_methods_catalog.md`
- Source variant document: `algorithm_variants/kswin_algorithm_variants.md`
- Source parameter tables:
  - `drift_method_variant_links.csv`
  - `drift_method_variant_measurement_summary.csv`
  - `drift_method_variant_parameters.csv`
  - `drift_method_parameter_guide.md`

The first implementation is a univariate numeric streaming/windowed KS
detector executed over a finite DataFrame slice. It accepts the common
`(time, value)` pandas DataFrame contract, sorts rows by time, slices the
supplied reference/current timestamp windows, concatenates the two slices in
time order, and replays the values through a KSWIN-style sliding window. At
each eligible step, the detector compares an older reference sample from the
sliding window with the most recent statistic window by a two-sample KS test.

## 2. Purpose

`KSWIN` detects distribution changes in a numeric stream by maintaining a fixed
sliding window and comparing the recent part of that window against an earlier
part using a Kolmogorov-Smirnov statistic. Unlike ADWIN, which is primarily a
mean-change adaptive-window detector, KSWIN is a fixed-window distribution
screening detector. It can react to location, scale, tail, or shape changes
when those changes appear in the sliding-window empirical CDF comparison.

The catalog input is `numeric stream`; the catalog output is `KS-window alarm`.
The first implementation narrows that catalog scope to scalar numeric
`(time, value)` rows because the public API receives finite DataFrame windows,
not an unbounded online iterator. It should be read as:

```text
Replay the selected reference/current rows as a time-ordered numeric stream and
report whether KSWIN raised a KS-window alarm during that replay.
```

Use the first implementation when:

- the monitored signal is one scalar numeric column
- the caller can provide timestamp ranges for `reference_window` and
  `current_window`
- the question is whether a sliding-window KS detector would alarm while
  processing those rows in chronological order
- KS statistic, p-value, window size, statistic-window size, and alarm history
  are useful monitoring outputs

Do not use the first implementation for categorical labels, count tables,
probability vectors, raw embeddings, multivariate feature matrices, text, SHAP
matrices, raw supervised prediction pairs, or model-performance drift claims
without a defined label/error stream.

## 3. Supported Variants

Supported for the first implementation:

- `KSWIN_STANDARD`
  - Default variant.
  - Uses scalar numeric reference/current windows as a finite stream replay.
  - Maintains a fixed-size sliding window of length `window_size`.
  - Compares the latest `stat_size` observations with an older reference sample
    from the same sliding window.
  - Uses a two-sample KS statistic and p-value at each eligible check.
  - Returns a streaming alarm when any checked window has `p_value < alpha`.
- `KSWIN_NUMERIC_STREAM`
  - Alias-style supported variant for the same first-scope numeric stream
    behavior.
  - Use when the caller wants the variant id to emphasize feature, score,
    latency, loss-proxy, or other numeric signal monitoring.
  - The calculation, output fields, and decision rule are the same as
    `KSWIN_STANDARD` unless a later contract differentiates the two.
- `KSWIN_WITH_SUBSAMPLING`
  - Supported with deterministic even-index subsampling over the finite replay
    stream before sliding-window checks.
  - `subsample_size` or `sample_size` may be supplied; when omitted, the target
    is `min(stream_length, max(window_size, 100))`.
  - `subsample_size` must be at least `window_size`.
  - No random replacement is used. `sampling_seed` is recorded in metadata when
    supplied but does not affect deterministic even-index sampling.
  - Output shape is the same as `KSWIN_STANDARD`, with additional measurement
    fields `SAMPLING_POLICY` and `SUBSAMPLE_SIZE`.

Default variant selection:

```text
if params["variant_id"] is omitted:
    variant_id = "KSWIN_STANDARD"
```

## 4. Input Schema

Use the common `pandas.DataFrame` input boundary from
`../input_output_contracts.md`.

Public function shape:

```python
def detect_kswin(
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

Although KSWIN is a streaming/windowed detector, the first public API still
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
KSWIN_STANDARD and KSWIN_NUMERIC_STREAM:
  min_reference_size: default 20
  min_current_size: default 20
  window_size: default 100
  stat_size: default 30
KSWIN_WITH_SUBSAMPLING:
  same minimums, plus optional subsample_size/sample_size
```

The effective finite stream length must be at least `window_size`, and
`stat_size` must be smaller than `window_size`. If either DataFrame window is
below its minimum, or if the combined replay stream is too short to fill the
KSWIN sliding window, return `severity="not_applicable"` and do not run the
detector.

## 5. Parameters

Accepted `params` keys and defaults for the first implementation:

| Param | Type | Default | Applies to | Meaning |
|---|---:|---:|---|---|
| `variant_id` | string | `KSWIN_STANDARD` | all | Variant selector. |
| `alpha` | float | `0.005` | supported variants | KS p-value alarm threshold. Must satisfy `0 < alpha < 1`. |
| `threshold_or_alpha` | float | optional | supported variants | Alias for `alpha`; must not conflict with explicit `alpha`. |
| `window_size` | int | `100` | supported variants | Fixed KSWIN sliding-window length. |
| `stat_size` | int | `30` | supported variants | Number of most recent rows used as the current/statistic sample. |
| `data_points` | int | optional | supported variants | Compatibility alias for `window_size`; must not conflict if both are supplied. |
| `input_signal` | string | optional | supported variants | Value column name only when `value_col is None`; otherwise metadata label such as `feature`, `score`, `loss`, or `latency`. |
| `min_reference_size` | int | `20` | supported variants | Minimum effective reference rows after invalid rows are dropped. |
| `min_current_size` | int | `20` | supported variants | Minimum effective current rows after invalid rows are dropped. |
| `nan_policy` | string | `drop` | supported variants | First implementation supports `drop`/`omit` only. |
| `check_every` | int | `1` | supported variants | Check interval in processed observations after the sliding window is full. |
| `record_events` | bool | `True` | supported variants | Include compact alarm event history in measurements. |
| `max_event_records` | int | `50` | supported variants | Maximum number of alarm events retained in measurements. |
| `sample_imbalance_warning_ratio` | float | `10.0` | supported variants | Warn when larger input window size divided by smaller size exceeds this ratio. |
| `tie_policy` | string | `warn_only` | supported variants | Add warnings for ties/discrete values; do not alter the KS statistic in the first implementation. |
| `multiple_testing_correction` | string | `none` | supported variants | Recorded as metadata only. Correction is not applied inside KSWIN. |
| `seed` | int or None | `None` | deferred subsampling | Recorded only unless `KSWIN_WITH_SUBSAMPLING` is later implemented. |

Parameter rules:

- `alpha` is the per-check KS p-value alarm threshold. It is not a global
  family-wise threshold across all replay checks.
- `threshold_or_alpha` is accepted only as a compatibility alias for `alpha`.
  If both are supplied and differ, return `severity="not_applicable"`.
- `window_size`, `stat_size`, `data_points`, `check_every`,
  `min_reference_size`, `min_current_size`, and `max_event_records` must be
  positive integers.
- `stat_size < window_size` is required.
- The older reference sample length is `window_size - stat_size`; it should be
  at least 2. The recent statistic sample length `stat_size` should also be at
  least 2.
- `data_points`, when supplied, means `window_size` for catalog compatibility.
  It does not replace the actual DataFrame rows.
- `nan_policy` supports `drop` and `omit` as aliases for dropping invalid rows.
  Other values return `not_applicable`.
- `tie_policy` supports `warn_only` only in the first implementation.
- `record_events=False` may omit detailed event rows but must still return
  `ALARM_COUNT`, `FIRST_ALARM_TIME`, and `LAST_ALARM_TIME`.
- `multiple_testing_correction != "none"` adds a warning and is recorded in
  metadata; this detector does not apply correction internally.
- Reject or warn on unrelated params such as `feature_cols`, `embedding_cols`,
  `category_col`, `count_col`, raw label columns, classifier settings,
  distance-stream settings, or preprocessing functions.

## 6. KSWIN Statistic and Window Policy

Normalize the selected finite stream to one-dimensional arrays:

```python
stream_values = np.asarray(..., dtype=float)
stream_times = np.asarray(..., dtype="datetime64[ns]")
```

For each eligible stream index after the fixed window is full:

```text
sliding_window = last window_size values ending at current index
reference_sample = sliding_window[: window_size - stat_size]
current_sample = sliding_window[window_size - stat_size :]
ks_statistic, p_value = two_sample_ks(reference_sample, current_sample)
```

The reference sample is the older part of the current sliding window, not the
full `reference_window` DataFrame slice. The supplied `reference_window` still
matters because it seeds the finite replay stream and affects the earliest
sliding windows checked by KSWIN.

Implementation-level pseudocode:

```text
events = []
last_statistic = None
last_p_value = None
for index, (time, value) in chronological stream:
    append value to fixed sliding window
    if sliding window has fewer than window_size rows:
        continue
    if (index + 1 - window_size) % check_every != 0:
        continue
    old = first window_size - stat_size rows of sliding window
    recent = last stat_size rows of sliding window
    statistic, p_value = ks_2samp(old, recent, alternative="two-sided")
    update last_statistic and last_p_value
    if p_value < alpha:
        record alarm event with time, index, statistic, p_value
```

Recommended backend:

```python
scipy.stats.ks_2samp(old, recent, alternative="two-sided", method="auto")
```

If SciPy is unavailable, the implementation may compute the two-sample KS
statistic from sorted ECDFs directly. In that fallback, return
`P_VALUE=None`, set `drift_detected=None` and `severity="watch"` unless a
manager-approved approximate p-value is implemented. Do not fabricate a
p-value from the statistic.

## 7. Output Measurements

`drift_method_variant_measurement_summary.csv` maps all DM-027 variants to:

```text
TEST_STATISTIC
P_VALUE
DRIFT_ALARM_STATE
```

Return these canonical measurements for every successful supported run:

```python
{
    "TEST_STATISTIC": <last checked KS statistic or None>,
    "P_VALUE": <last checked KS p-value or None>,
    "DRIFT_ALARM_STATE": <"drift_detected" | "normal" | "undetermined">,
    "KS_STATISTIC": <same float as TEST_STATISTIC or None>,
    "WINDOW_SIZE": <resolved window_size>,
    "STAT_SIZE": <resolved stat_size>,
    "REFERENCE_SUBWINDOW_SIZE": <window_size - stat_size>,
    "ALPHA": <resolved alpha>,
    "CHECK_EVERY": <resolved check_every>,
    "ALARM_COUNT": <int>,
    "FIRST_ALARM_TIME": <ISO timestamp or None>,
    "LAST_ALARM_TIME": <ISO timestamp or None>,
    "FIRST_ALARM_INDEX": <int or None>,
    "LAST_ALARM_INDEX": <int or None>,
    "PROCESSED_COUNT": <effective stream row count>,
    "CHECK_COUNT": <number of KS checks performed>,
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
    "LAST_CHECK_TIME": <ISO timestamp or None>,
}
```

When `record_events=True`, include a compact event list:

```python
{
    "ALARM_EVENTS": [
        {
            "time": <ISO timestamp>,
            "index": <zero-based stream index>,
            "ks_statistic": <float>,
            "p_value": <float>,
            "window_start_time": <ISO timestamp>,
            "reference_subwindow_size": <int>,
            "stat_size": <int>,
        },
        ...
    ]
}
```

Top-level `DriftResult` field mapping:

```text
method_id = "DM-027"
method_name = "KSWIN"
method_category = "StreamingChangeDetector"
variant_id = resolved variant id
drift_score = last checked KS statistic, or max alarm KS statistic if an alarm occurred
p_value = last checked KS p-value, or min alarm p-value if an alarm occurred
test_statistic = same value as drift_score
threshold = resolved alpha
```

Interpretation text should state:

- which variant ran
- that reference/current windows were replayed as one finite chronological
  numeric stream
- effective reference/current/stream row counts
- resolved `alpha`, `window_size`, `stat_size`, and `check_every`
- number of KS checks and alarm count
- last checked KS statistic and p-value when available
- first/last alarm time if applicable
- that KSWIN on a numeric value stream is a windowed distribution-change signal,
  not proof of root cause, model performance degradation, or supervised concept
  drift

## 8. Algorithm Steps

1. Normalize `params` to an empty dict when omitted.
2. Resolve `variant_id`; default to `KSWIN_STANDARD`.
3. Reject unknown variants with `severity="not_applicable"` and a warning.
4. Reject `KSWIN_WITH_SUBSAMPLING` with `severity="not_applicable"` until the
   sampling policy is approved.
5. Treat `KSWIN_NUMERIC_STREAM` as the same first-scope numeric replay detector
   as `KSWIN_STANDARD`.
6. Reject multivariate, embedding, categorical, count-table, raw label, and raw
   prediction requests in the first implementation.
7. Resolve `alpha`, `window_size`, `stat_size`, `check_every`, `nan_policy`,
   event-recording settings, sample-size minima, tie policy, and value column.
8. Validate that both reference and current windows are supplied and parseable.
9. Validate required columns and scalar numeric value data. Boolean data is not
   valid KSWIN numeric-stream input.
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
16. If the effective stream length is below `window_size`, return not
    applicable.
17. Add warnings for invalid rows, highly imbalanced sample sizes, repeated or
    tied values, small samples that pass the hard minimum, autocorrelation risk,
    and multiple-testing metadata when applicable.
18. Iterate the replay stream in chronological order with a fixed-length
    sliding window.
19. On each eligible check point, split the sliding window into older reference
    and recent statistic samples.
20. Compute the two-sided KS statistic and p-value.
21. Record alarm events for checks with `p_value < alpha`.
22. Compute final sample summaries, check count, last statistic, last p-value,
    and alarm summary.
23. Apply the drift decision rule from section 9.
24. Build `DriftResult` with method identity, variant, canonical measurements,
    helper summaries, counts, windows, parameters, warnings, metadata, and
    concise interpretation text.

## 9. Drift Decision Rule

Streaming alarm rule for `KSWIN_STANDARD` and `KSWIN_NUMERIC_STREAM`:

```text
if no p_value can be computed:
    drift_detected = None
    severity = "watch"
    DRIFT_ALARM_STATE = "undetermined"
elif alarm_count > 0:
    drift_detected = True
    severity = "drift_detected"
    DRIFT_ALARM_STATE = "drift_detected"
else:
    drift_detected = False
    severity = "normal"
    DRIFT_ALARM_STATE = "normal"
```

Use strict `p_value < alpha`, not `<= alpha`, for each checked sliding window.
Equality is not drift. `threshold` in the top-level result is the resolved
`alpha`. The p-value reported at the top level should be the minimum alarm
p-value when alarms occurred; otherwise it should be the last checked p-value.
Record the last checked p-value separately in measurements for auditability if
the top-level field uses the minimum alarm p-value.

For report wording:

- alarm: "KSWIN raised a KS-window alarm while replaying the selected
  reference/current rows"
- no alarm: "no KSWIN alarm was raised under this finite replay, alpha, and
  sliding-window policy"
- no p-value fallback: "KS-window statistic was computed, but p-value-based
  alarm is undetermined because p-value calculation was unavailable"
- deferred subsampling request: "KSWIN_WITH_SUBSAMPLING requires an explicit
  sampling and reproducibility contract"

The KSWIN result depends on stream order, `alpha`, `window_size`, `stat_size`,
check interval, sample count, and finite replay scope. It must not be compared
directly with batch KS, Wasserstein, MMD, LSDD, ADWIN, Page-Hinkley, CUSUM, or
EWMA without method and variant context.

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
- effective stream length below `window_size`
- unsupported or unknown `variant_id`
- `KSWIN_WITH_SUBSAMPLING` until the sampling policy is approved
- `feature_cols`, `embedding_cols`, object embeddings, list-valued rows,
  category/count columns, raw `y_true`/`y_pred` requests, or other non-scalar
  inputs in the first implementation
- invalid `alpha`, conflicting `alpha` and `threshold_or_alpha`, `window_size`,
  `stat_size`, `data_points`, `check_every`, event-record settings,
  `nan_policy`, `tie_policy`, sample-size parameter, or warning-ratio parameter
- `stat_size >= window_size`
- reference subwindow size or statistic subwindow size below 2
- current/reference window overlap when overlap policy is not explicitly
  defined by the implementation
- backend missing when p-value computation is required and no approved fallback
  exists
- non-finite KS statistic or p-value outside `[0, 1]`

Return `severity="normal"`, `"watch"`, or `"drift_detected"` with warnings when
the method can still run but interpretation needs caution:

- timestamps or values were dropped because they were invalid or non-finite
- `threshold_or_alpha` was interpreted as KSWIN `alpha`
- reference/current sample sizes are highly imbalanced
- effective stream length is only slightly above `window_size`
- values are repeated, rounded, tied, or discrete, weakening classical KS
  p-value interpretation
- observations are autocorrelated time-series rows rather than independent
  draws
- strong seasonality, batch collection cycles, or traffic mix changes may
  trigger distribution alarms that are operational-pattern changes rather than
  drift
- `alpha` is unusually high or low for the project defaults
- `check_every > 1` may delay or miss alarms between check points
- event history was truncated by `max_event_records`
- `multiple_testing_correction` is not `"none"`; record that this detector does
  not apply correction internally across repeated sliding-window checks

Unexpected backend or numeric exceptions should return `severity="error"` or
`"watch"` according to project convention, with `drift_detected=None` and a
clear warning, without raising through the public detector boundary.

Do not silently coerce categorical values, boolean flags, labels, embeddings,
lists, object arrays, count tables, or multivariate matrices into the
univariate KSWIN detector.

## 11. Implementation Target

```text
module: drift_algorithm.methods.streamingchangedetector
function: detect_kswin
```

Expected dependencies:

```text
pandas
numpy
scipy.stats.ks_2samp
```

Expected result object:

```text
DriftResult from drift_algorithm/docs/input_output_contracts.md equivalent code
contract
```

Helper functions should follow existing project patterns:

- add `KSWIN_METHOD_ID = "DM-027"` and `KSWIN_METHOD_NAME = "KSWIN"`
- define `SUPPORTED_KSWIN_VARIANTS` for `KSWIN_STANDARD` and
  `KSWIN_NUMERIC_STREAM`
- define `DEFERRED_KSWIN_VARIANTS` for `KSWIN_WITH_SUBSAMPLING`
- use the common `DriftResult` dataclass
- use `not_applicable_result` or a method-specific not-applicable helper for
  validation failures
- reuse common numeric-window preparation where it matches the finite replay
  contract, but ensure the final stream is sorted chronologically
- keep KSWIN helpers private to the module unless another streaming detector
  already exposes a shared helper
- record backend name, finite-replay policy, value column, effective windows,
  resolved parameters, sample-size metadata, tie policy, and
  unsupported/deferred variant decisions so the result is auditable

Suggested private helper shape:

```python
def _kswin_not_applicable(
    variant_id: str | None,
    warning: str,
    metadata: dict[str, Any] | None = None,
    prior_warnings: list[str] | None = None,
) -> DriftResult:
    ...

def _resolve_kswin_params(params: dict[str, Any]) -> dict[str, Any]:
    ...

def _prepare_kswin_stream(
    data: pd.DataFrame,
    *,
    time_col: str,
    value_col: str,
    reference_window: tuple[str, str],
    current_window: tuple[str, str],
    params: dict[str, Any],
) -> dict[str, Any]:
    ...

def _run_kswin_stream(
    values: np.ndarray,
    times: np.ndarray,
    *,
    alpha: float,
    window_size: int,
    stat_size: int,
    check_every: int,
    record_events: bool,
    max_event_records: int,
) -> dict[str, Any]:
    ...
```

Public contract:

- `detect_kswin` must be importable from
  `drift_algorithm.methods.streamingchangedetector`.
- The function must accept the common arguments exactly as shown in section 4.
- It must return `DriftResult`, never raw tuples or dictionaries.
- Validation failures must return `severity="not_applicable"` unless they are
  unexpected numeric/runtime errors.
- The first implementation must not fabricate a p-value if the KS backend only
  provides a statistic.
- `threshold` in the result must contain the resolved `alpha`.
- `KSWIN_WITH_SUBSAMPLING` must be an explicit `not_applicable` result until
  its sampling policy is approved.

## 12. Verification Plan

Unit tests for the first implementation:

1. Default no-alarm finite replay:
   - Generate stable numeric reference/current rows from the same distribution
     with deterministic timestamps.
   - Omit `variant_id` and KSWIN settings.
   - Assert `variant_id == "KSWIN_STANDARD"`.
   - Assert `TEST_STATISTIC`, `P_VALUE`, `DRIFT_ALARM_STATE`, `WINDOW_SIZE`,
     `STAT_SIZE`, `ALARM_COUNT`, `PROCESSED_COUNT`, `CHECK_COUNT`,
     `SAMPLE_SIZE`, `SAMPLE_SIZE_REFERENCE`, and `SAMPLE_SIZE_CURRENT` exist.
   - Assert `drift_detected is False`, `severity == "normal"`, and
     `DRIFT_ALARM_STATE == "normal"` for a deterministic seed chosen to keep
     every checked p-value at or above `alpha`.
2. Distribution-shift alarm:
   - Generate reference values from one distribution and current values with a
     clear location, scale, or shape shift.
   - Use deterministic `alpha`, `window_size`, and `stat_size` chosen to
     produce an alarm.
   - Assert `ALARM_COUNT > 0`, `drift_detected is True`,
     `severity == "drift_detected"`, and first/last alarm metadata is present.
3. Variant routing:
   - Assert `KSWIN_NUMERIC_STREAM` runs the same numeric replay detector and
     records the selected variant id.
   - Assert `KSWIN_WITH_SUBSAMPLING` returns `severity="not_applicable"` with a
     warning about the deferred sampling policy.
   - Assert unknown variants return `not_applicable`.
4. Parameter alias and validation:
   - Assert `threshold_or_alpha` is treated as `alpha`.
   - Assert conflicting `alpha` and `threshold_or_alpha` return
     `severity="not_applicable"`.
   - Assert invalid `alpha`, `window_size`, `stat_size`, `data_points`,
     `check_every`, `record_events`, `max_event_records`, `nan_policy`,
     `tie_policy`, and sample-size settings return not applicable.
   - Assert `stat_size >= window_size` returns not applicable.
5. Window and stream ordering:
   - Provide unsorted input rows and assert processed counts and alarm event
     indices follow chronological order.
   - Assert missing windows, unparseable windows, empty slices, insufficient
     sample sizes, stream shorter than `window_size`, and overlapping windows
     return `not_applicable`.
6. Schema validation:
   - Missing value column.
   - Non-numeric, boolean, object/list, embedding-like, categorical, or text
     value column.
   - Invalid timestamps and non-finite values are dropped with warnings and
     effective counts.
7. Event recording:
   - With `record_events=True`, assert `ALARM_EVENTS` is present and bounded by
     `max_event_records`.
   - With `record_events=False`, assert detailed events can be omitted while
     alarm count and first/last alarm summaries remain available.
8. Warning behavior:
   - Imbalanced sample sizes produce a caution warning.
   - Tied/discrete values produce a KS p-value caution under `tie_policy`.
   - `check_every > 1` records that alarm checks are periodic.
   - Event truncation and `multiple_testing_correction != "none"` are recorded
     as warnings.
9. Backend/numeric failure:
   - Simulate SciPy unavailability or non-finite KS output.
   - Assert the public detector returns `severity="watch"`, `"error"`, or
     `not_applicable` according to project convention with
     `drift_detected=None` and a clear warning.

Recommended commands after implementation:

```text
python -m py_compile drift_algorithm\methods\streamingchangedetector.py
python -m pytest tests\test_kswin.py
python -m pytest tests\test_adwin.py tests\test_page_hinkley_test.py
```

Manual review before marking implementation complete:

- Confirm public function signature matches the common contract.
- Confirm canonical measurement names match
  `drift_method_variant_measurement_summary.csv`.
- Confirm default variant is `KSWIN_STANDARD`.
- Confirm `reference_window` and `current_window` define a finite replay stream
  rather than a batch two-sample KS test.
- Confirm the KSWIN comparison uses the older and latest parts of the sliding
  window, not the full DataFrame reference/current slices at every check.
- Confirm strict `p_value < alpha` is used.
- Confirm top-level `threshold` stores resolved `alpha`.
- Confirm event history and final checked KS state are auditable.
- Confirm `KSWIN_WITH_SUBSAMPLING` fails explicitly until sampling policy is
  approved.
- Confirm interpretation text avoids root-cause, performance-degradation, and
  supervised concept-drift claims without labeled evidence.

## 13. Manager Review Points

- First implementation scope is `KSWIN_STANDARD` and `KSWIN_NUMERIC_STREAM` over
  scalar numeric `(time, value)` rows only.
- Although KSWIN is streaming/windowed, the current public API supplies finite
  timestamp windows; this design replays reference/current rows in
  chronological order and reports the resulting streaming alarm state.
- `reference_window` and `current_window` are required for API consistency and
  for defining replay scope, but the algorithm is not the same as DM-001 batch
  KS over the two full windows.
- Inside KSWIN, each check compares the older part of the fixed sliding window
  with the latest `stat_size` rows.
- Proposed defaults are `alpha=0.005`, `window_size=100`, `stat_size=30`, and
  `check_every=1`; these should be reviewed against any chosen backend or
  existing project convention.
- Top-level `p_value` is p-value based when SciPy or an approved equivalent is
  available; no p-value should be fabricated in a statistic-only fallback.
- `KSWIN_WITH_SUBSAMPLING` remains deferred to avoid silently changing
  reproducibility, rare-event sensitivity, and alarm comparability.
- The public target is `detect_kswin` in
  `drift_algorithm.methods.streamingchangedetector`.
