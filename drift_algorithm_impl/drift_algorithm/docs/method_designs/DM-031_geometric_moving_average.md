# DM-031 Geometric Moving Average Design

## 1. Method Identity

- Method ID: `DM-031`
- Method name: `Geometric Moving Average`
- Category: `StreamingChangeDetector`
- Method kind: `detector`
- Status: `확정`
- Source catalog: `drift_methods_catalog.md`
- Source variant document: `algorithm_variants/geometric_moving_average_algorithm_variants.md`
- Source parameter tables:
  - `drift_method_variant_links.csv`
  - `drift_method_variant_measurement_summary.csv`
  - `drift_method_variant_parameters.csv`
  - `drift_method_parameter_guide.md`

The first implementation is a univariate numeric geometric moving average
control chart executed over a finite DataFrame slice. In this catalog,
Geometric Moving Average is treated as the exponentially weighted moving
average style control-chart family: recent observations receive geometric
weights while older observations remain in the statistic through the recursive
state.

It accepts the common `(time, value)` pandas DataFrame contract, sorts rows by
time, slices the supplied reference/current timestamp windows, calibrates the
center line and control limits from the reference window unless explicit
parameters are supplied, concatenates the two slices in time order, and replays
the values through a GMA state machine.

## 2. Purpose

`Geometric Moving Average` monitors whether a geometrically weighted moving
average of a scalar numeric metric moves outside a control limit. It is a
sequential control-chart detector for gradual or sustained mean movement, not a
two-sample distribution test and not a p-value test.

The catalog input is `numeric metric stream`; the catalog output is `GMA
statistic, control limit`. The first implementation narrows that catalog scope
to scalar numeric `(time, value)` rows because the public API receives finite
DataFrame windows, not an unbounded online iterator. It should be read as:

```text
Replay the selected reference/current rows as a time-ordered numeric stream and
report whether the GMA statistic crossed its configured control limit during
that replay.
```

Use the first implementation when:

- the monitored signal is one scalar numeric metric
- the caller can provide timestamp ranges for `reference_window` and
  `current_window`
- the operational question is whether a sequential GMA control chart would
  alarm while processing those rows in chronological order
- small sustained shifts matter more than one-off spikes
- direction matters: upward for loss, error rate, latency, reject rate, or
  other "larger is worse" metrics; downward for confidence, throughput, recall,
  acceptance rate, or other "smaller is worse" metrics
- GMA statistic, center line, upper/lower control limits, smoothing factor, and
  alarm history are useful monitoring outputs

Do not use the first implementation for categorical labels, count tables,
probability vectors, raw embeddings, multivariate feature matrices, text, SHAP
matrices, raw supervised prediction pairs, or retraining policy decisions.
Those require another method family or a future contract.

## 3. Supported Variants

Supported for the first implementation:

- `GMA_CONTROL_CHART`
  - Default variant.
  - Detects sustained movement in either direction from the center line.
  - Uses chronological replay of the selected reference/current rows.
  - Raises an alarm when the GMA statistic exceeds `ucl` or falls below `lcl`.
- `GMA_ONE_SIDED`
  - Detects sustained movement only in the configured risk direction.
  - Uses `direction="increase"` for upper-limit monitoring or
    `direction="decrease"` for lower-limit monitoring.
  - Raises an alarm only when the monitored one-sided limit is crossed.

Deferred until separate calibration policy is approved:

- `GMA_WITH_EMPIRICAL_LIMIT`
  - Requires a documented baseline replay/calibration period, empirical
    quantile policy, target false alarm rate, and separation between threshold
    calibration data and evaluated current data.
  - Must not silently approximate empirical thresholds from the same current
    rows being evaluated.
  - In the first implementation, return `severity="not_applicable"` unless
    this empirical limit contract is explicitly implemented.
- Multivariate GMA:
  - Belongs to a multivariate control-chart contract, not the first DM-031
    implementation.
  - Must not average feature columns or build a vector statistic inside
    `detect_geometric_moving_average`.
- Supervised error-rate GMA:
  - Requires an explicit label/error schema, `error_col` or `y_true`/`y_pred`
    handling, label-delay policy, and error definition.
  - Must not infer performance drift from arbitrary numeric `value` rows.

Default variant selection:

```text
if params["variant_id"] is omitted:
    variant_id = "GMA_CONTROL_CHART"
```

## 4. Input Schema

Use the common `pandas.DataFrame` input boundary from
`../input_output_contracts.md`.

Public function shape:

```python
def detect_geometric_moving_average(
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

Although GMA is a streaming control chart, the first public API still requires
both windows. They define the finite replay scope and, when control parameters
are omitted, the reference window supplies the baseline center and standard
deviation:

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
GMA_CONTROL_CHART and GMA_ONE_SIDED:
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
| `variant_id` | string | `GMA_CONTROL_CHART` | all | Variant selector. |
| `lambda` | float | `0.2` | supported variants | Geometric smoothing factor. Must be `0 < lambda <= 1`. Larger values react faster to recent values. |
| `center_line` | float | reference mean | supported variants | Baseline center used by the GMA recurrence and control limits. |
| `sigma` | float | reference sample std | supported variants | Baseline standard deviation used for theoretical control limits. Must be non-negative. |
| `control_width` | float | `3.0` | supported variants | Width multiplier for theoretical control limits. Must be positive. |
| `ucl` | float | computed | supported variants | Explicit upper control limit. |
| `lcl` | float | computed | supported variants | Explicit lower control limit. |
| `control_limit` | float or dict | optional | supported variants | Compatibility alias for one-sided limit, or `{ "ucl": ..., "lcl": ... }` for two-sided limits. |
| `threshold` | float | optional | `GMA_ONE_SIDED` | Compatibility alias for the monitored one-sided control limit. |
| `threshold_or_alpha` | float | optional | supported variants | Compatibility alias for `control_width` only when no explicit limit is supplied; must not be treated as a p-value alpha. |
| `direction` | string | `both` or inferred | supported variants | `both`, `increase`, or `decrease`; must match the selected variant. |
| `direction_or_alternative` | string | optional | `GMA_ONE_SIDED` | Compatibility alias for `direction`. |
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

- `lambda` is the geometric smoothing factor. It is not a reserved word in
  `params`, but implementation helpers should avoid using `lambda` as a Python
  variable name.
- `center_line`, when omitted, is computed from the effective reference window
  after invalid rows are dropped. Current rows must not be used to set it.
- `sigma`, when omitted, is computed from the effective reference sample
  standard deviation. If it is zero, theoretical limits collapse to the center
  line unless explicit `ucl`/`lcl` or `control_limit` values are supplied;
  return not applicable or warn according to the implemented zero-variance
  policy.
- The default two-sided theoretical limits are the same steady-state
  exponentially weighted control-chart limits used for a geometric moving
  average:

```text
steady_state_sigma_gma = sigma * sqrt(lambda / (2 - lambda))
ucl = center_line + control_width * steady_state_sigma_gma
lcl = center_line - control_width * steady_state_sigma_gma
```

- Time-varying startup limits may be added later, but the first implementation
  should use the steady-state limit above for deterministic finite replay.
- `control_limit` may be a scalar only for `GMA_ONE_SIDED`; it maps to the
  monitored upper or lower limit according to `direction`. For
  `GMA_CONTROL_CHART`, scalar `control_limit` is ambiguous and must return
  `not_applicable`; a dict with compatible `ucl` and `lcl` keys is allowed.
- `threshold_or_alpha` is accepted only as a compatibility alias for
  `control_width` when `control_width`, `ucl`, `lcl`, `control_limit`, and
  `threshold` are not supplied. It must not be interpreted as a p-value alpha.
- For `GMA_ONE_SIDED`, `threshold` maps to the monitored limit: upper limit for
  `direction="increase"` and lower limit for `direction="decrease"`.
- `direction` must be `both` for `GMA_CONTROL_CHART`, `increase` or
  `decrease` for `GMA_ONE_SIDED`.
- `direction_or_alternative` accepts `up`/`greater` as `increase`,
  `down`/`less` as `decrease`, and `two-sided`/`both` as `both`.
- `warmup_size`, `check_every`, `min_reference_size`, `min_current_size`, and
  `max_event_records` must be positive integers.
- `reset_policy="none"` leaves the GMA recurrence unchanged after an alarm.
  Other reset policies are deferred because resetting a smoothed average
  changes the control-chart interpretation.
- `nan_policy` supports `drop` and `omit` as aliases for dropping invalid rows.
  Other values return `not_applicable`.
- Reject or warn on unrelated params such as `feature_cols`, `embedding_cols`,
  `category_col`, `count_col`, raw label columns, classifier settings,
  distance-stream settings, or preprocessing functions.

## 6. GMA Statistic and State Policy

Normalize the selected finite stream to one-dimensional arrays:

```python
stream_values = np.asarray(..., dtype=float)
stream_times = np.asarray(..., dtype="datetime64[ns]")
```

For observation `x_t`, center line `mu0`, smoothing factor `lambda`, and prior
GMA statistic `g_{t-1}`, maintain:

```text
g_0 = center_line
g_t = lambda * x_t + (1 - lambda) * g_{t-1}
```

This recurrence gives the newest observation weight `lambda`, the prior
observation weight `lambda * (1 - lambda)`, and older observations
geometrically decreasing weights. It is therefore equivalent to the
exponentially weighted moving-average style control chart, but the result
fields should use GMA naming for DM-031.

Control limit behavior:

```text
GMA_CONTROL_CHART:
  upper alarm if g_t > ucl
  lower alarm if g_t < lcl

GMA_ONE_SIDED with direction="increase":
  upper alarm if g_t > ucl

GMA_ONE_SIDED with direction="decrease":
  lower alarm if g_t < lcl
```

Implementation-level pseudocode:

```text
events = []
gma = center_line
max_gma = center_line
min_gma = center_line
max_upper_excess = 0
max_lower_excess = 0

for index, (time, value) in chronological stream:
    gma = lambda * value + (1 - lambda) * gma
    max_gma = max(max_gma, gma)
    min_gma = min(min_gma, gma)
    upper_excess = gma - ucl
    lower_excess = lcl - gma
    max_upper_excess = max(max_upper_excess, upper_excess)
    max_lower_excess = max(max_lower_excess, lower_excess)

    if index + 1 < warmup_size:
        continue
    if (index + 1 - warmup_size) % check_every != 0:
        continue

    if variant monitors upper and gma > ucl:
        record upper alarm event

    if variant monitors lower and gma < lcl:
        record lower alarm event
```

The first implementation should use a deterministic NumPy/Pandas
implementation. It does not require SciPy or network-installed streaming
libraries. The design does not require a top-level p-value. Do not label the
GMA statistic as `P_VALUE`.

## 7. Output Measurements

`drift_method_variant_measurement_summary.csv` maps DM-031 variants to:

```text
GMA_CONTROL_CHART: TEST_STATISTIC, P_VALUE, DRIFT_ALARM_STATE
GMA_ONE_SIDED: TEST_STATISTIC, P_VALUE, DRIFT_ALARM_STATE
GMA_WITH_EMPIRICAL_LIMIT: TEST_STATISTIC, P_VALUE, DRIFT_ALARM_STATE
```

For supported first-scope control-chart runs, return `P_VALUE` as `None`
because GMA is not a p-value test. Also include explicit GMA/control-limit
helper measurements so the catalog's `GMA statistic, control limit` output is
auditable:

```python
{
    "TEST_STATISTIC": <final GMA statistic>,
    "P_VALUE": None,
    "DRIFT_ALARM_STATE": <"drift_detected" | "normal">,
    "GMA_STATISTIC": <final GMA statistic>,
    "CONTROL_LIMIT": {
        "ucl": <resolved ucl or None>,
        "lcl": <resolved lcl or None>,
        "mode": <"two_sided" | "upper" | "lower">,
    },
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
    "MAX_GMA_STATISTIC": <max GMA statistic seen during replay>,
    "MIN_GMA_STATISTIC": <min GMA statistic seen during replay>,
    "MAX_UPPER_EXCESS": <max(gma - ucl) seen, or None>,
    "MAX_LOWER_EXCESS": <max(lcl - gma) seen, or None>,
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
            "gma_statistic": <float>,
            "control_limit": <float>,
            "center_line": <float>,
            "lambda": <float>,
            "raw_value": <float>,
        },
        ...
    ]
}
```

For `GMA_CONTROL_CHART`, top-level `drift_score` should be the larger of
`MAX_UPPER_EXCESS` and `MAX_LOWER_EXCESS`, clipped or represented so that
non-crossing values do not imply a positive breach unless the project
convention prefers signed margin. For `GMA_ONE_SIDED`, `drift_score` should be
the maximum monitored-limit excess in the configured direction.

Top-level `DriftResult` field mapping:

```text
method_id = "DM-031"
method_name = "Geometric Moving Average"
method_category = "StreamingChangeDetector"
variant_id = resolved variant id
drift_score = max monitored control-limit excess during replay
p_value = None
test_statistic = final GMA_STATISTIC
threshold = monitored control limit for one-sided variants, otherwise None
```

Interpretation text should state:

- which variant and direction ran
- that reference/current windows were replayed as one finite chronological
  numeric stream
- effective reference/current/stream row counts
- resolved `center_line`, `sigma`, `lambda`, `control_width`, `ucl`, `lcl`,
  `warmup_size`, and `check_every`
- final, maximum, and minimum GMA statistics
- whether an alarm occurred, and first/last alarm time and direction if
  applicable
- that GMA on a numeric metric stream is a sequential control-chart signal,
  not proof of root cause, model performance degradation, supervised concept
  drift, or retraining necessity

## 8. Algorithm Steps

1. Normalize `params` to an empty dict when omitted.
2. Resolve `variant_id`; default to `GMA_CONTROL_CHART`.
3. Reject unknown variants with `severity="not_applicable"` and a warning.
4. Reject `GMA_WITH_EMPIRICAL_LIMIT` until empirical limit calibration is
   implemented.
5. Resolve direction from variant and validate any explicit `direction` or
   `direction_or_alternative`.
6. Reject multivariate, embedding, categorical, count-table, raw label, raw
   prediction, and distance-stream requests in the first implementation.
7. Resolve value column, `nan_policy`, event-recording settings, sample-size
   minima, `warmup_size`, `check_every`, `reset_policy`, `lambda`,
   `center_line`, `sigma`, limit parameters, and threshold aliases.
8. Validate that both reference and current windows are supplied and parseable.
9. Validate required columns and scalar numeric value data. Boolean data is not
   valid GMA numeric-stream input.
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
20. Iterate each stream row in chronological order, updating GMA statistic,
    maximum/minimum GMA statistic, monitored margin, and event summaries.
21. After `warmup_size` and according to `check_every`, compare the monitored
    GMA statistic to the configured control limit.
22. Record alarm events. Do not reset GMA state unless a later design approves
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
upper alarm: GMA_STATISTIC > ucl
lower alarm: GMA_STATISTIC < lcl
```

Equality is not drift. `p_value` remains `None` even though the measurement
summary includes `P_VALUE` through the generic optional score mapping.

For report wording:

- two-sided alarm: "GMA raised a control-chart alarm in the recorded direction
  while replaying the selected reference/current rows"
- upper alarm: "GMA raised an upper control-limit alarm while replaying the
  selected reference/current rows"
- lower alarm: "GMA raised a lower control-limit alarm while replaying the
  selected reference/current rows"
- no alarm: "no GMA alarm was raised under this finite replay, smoothing
  factor, center line, and control-limit policy"
- deferred empirical limit request: "`GMA_WITH_EMPIRICAL_LIMIT` requires an
  explicit baseline replay empirical-limit calibration contract"
- unsupported supervised request: "supervised GMA requires an explicit error
  stream contract"

The GMA result depends on stream order, smoothing factor, center line,
baseline variance, control-limit policy, direction, warmup size, sample count,
and finite replay scope. It must not be compared directly with ADWIN, KSWIN,
Page-Hinkley, CUSUM, EWMA, BOCD, MEWMA, or batch two-sample tests without
method and variant context.

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
- `GMA_WITH_EMPIRICAL_LIMIT` until empirical limit policy is approved
- supervised error-rate GMA requests until label/error-stream handling is
  approved
- `feature_cols`, `embedding_cols`, object embeddings, list-valued rows,
  category/count columns, raw `y_true`/`y_pred` requests, or other non-scalar
  inputs in the first implementation
- invalid `lambda`, invalid `center_line`, invalid `sigma`, invalid
  `control_width`, invalid or conflicting `ucl`/`lcl`/`control_limit`/
  `threshold`/`threshold_or_alpha`, conflicting variant and direction, invalid
  `warmup_size`, `reset_policy`, `check_every`, event-record settings,
  `nan_policy`, sample-size parameter, or warning-ratio parameter
- current/reference window overlap when overlap policy is not explicitly
  defined by the implementation
- theoretical limit computation cannot produce finite control limits
- non-finite GMA statistic or non-finite running state

Return `severity="normal"` or `"drift_detected"` with warnings when the method
can still run but interpretation needs caution:

- timestamps or values were dropped because they were invalid or non-finite
- `threshold`, `threshold_or_alpha`, `control_limit`, `ucl`, or `lcl` was
  interpreted through a compatibility path
- `center_line` or `sigma` was inferred from the effective reference window
  rather than supplied by a calibration process
- reference standard deviation is very small, making theoretical limits narrow
- reference/current sample sizes are highly imbalanced
- effective stream length is only slightly above `warmup_size`
- observations are autocorrelated time-series rows rather than independent
  draws
- strong seasonality, batch collection cycles, or traffic mix changes may
  trigger GMA alarms that are operational-pattern changes rather than drift
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
into the univariate GMA detector.

## 11. Implementation Target

```text
module: drift_algorithm.methods.streamingchangedetector
function: detect_geometric_moving_average
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

- add `GMA_METHOD_ID = "DM-031"` and
  `GMA_METHOD_NAME = "Geometric Moving Average"`
- define `SUPPORTED_GMA_VARIANTS` for `GMA_CONTROL_CHART` and `GMA_ONE_SIDED`
- define `DEFERRED_GMA_VARIANTS` for `GMA_WITH_EMPIRICAL_LIMIT`
- use the common `DriftResult` dataclass
- use `not_applicable_result` or a method-specific not-applicable helper for
  validation failures
- reuse common numeric-window preparation where it matches the finite replay
  contract, but ensure the final stream is sorted chronologically
- keep GMA helpers private to the module unless another streaming detector
  already exposes a shared helper
- record backend name, finite-replay policy, direction, value column, effective
  windows, resolved parameters, sample-size metadata, and
  unsupported/deferred variant decisions so the result is auditable

Suggested private helper shape:

```python
def _gma_not_applicable(
    variant_id: str | None,
    warning: str,
    metadata: dict[str, Any] | None = None,
    prior_warnings: list[str] | None = None,
) -> DriftResult:
    ...

def _resolve_gma_params(params: dict[str, Any]) -> dict[str, Any]:
    ...

def _prepare_gma_stream(
    data: pd.DataFrame,
    *,
    time_col: str,
    value_col: str,
    reference_window: tuple[str, str],
    current_window: tuple[str, str],
    params: dict[str, Any],
) -> dict[str, Any]:
    ...

def _run_gma_stream(
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

- `detect_geometric_moving_average` must be importable from
  `drift_algorithm.methods.streamingchangedetector`.
- The function must accept the common arguments exactly as shown in section 4.
- It must return `DriftResult`, never raw tuples or dictionaries.
- Validation failures must return `severity="not_applicable"` unless they are
  unexpected numeric/runtime errors.
- The first implementation must not fabricate a p-value.
- `GMA_CONTROL_CHART` must evaluate both upper and lower limits.
- `GMA_ONE_SIDED` must record the monitored direction and must not report the
  opposite direction as drift.
- `GMA_WITH_EMPIRICAL_LIMIT`, supervised error-rate GMA, and multivariate
  aggregation requests must be explicit `not_applicable` results until their
  separate contracts are approved.

## 12. Verification Plan

Unit tests for the first implementation:

1. Default no-alarm finite replay:
   - Generate stable numeric reference/current rows from the same distribution
     with deterministic timestamps.
   - Omit `variant_id` and GMA settings.
   - Assert `variant_id == "GMA_CONTROL_CHART"`.
   - Assert `TEST_STATISTIC`, `P_VALUE`, `DRIFT_ALARM_STATE`,
     `GMA_STATISTIC`, `CONTROL_LIMIT`, `CENTER_LINE`, `SIGMA`, `LAMBDA`,
     `UCL`, `LCL`, `ALARM_COUNT`, `PROCESSED_COUNT`, `SAMPLE_SIZE`,
     `SAMPLE_SIZE_REFERENCE`, and `SAMPLE_SIZE_CURRENT` exist.
   - Assert `p_value is None`, measurement `P_VALUE is None`,
     `drift_detected is False`, `severity == "normal"`, and
     `DRIFT_ALARM_STATE == "normal"` for a stable deterministic stream.
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
   - Use `variant_id="GMA_ONE_SIDED"` with `direction="increase"` and assert
     only upper-limit alarms are monitored.
   - Use `direction="decrease"` and assert only lower-limit alarms are
     monitored.
   - Assert a direction conflicting with the selected variant returns
     `not_applicable`.
5. Parameter alias and validation:
   - Assert `threshold_or_alpha` is treated as `control_width` only in the
     documented compatibility case.
   - Assert `threshold` and scalar `control_limit` map to the monitored
     one-sided limit.
   - Assert dict `control_limit` can supply two-sided `ucl`/`lcl`.
   - Assert invalid `lambda`, `center_line`, `sigma`, `control_width`, `ucl`,
     `lcl`, `control_limit`, `threshold`, `threshold_or_alpha`,
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
8. Event recording:
   - With `record_events=True`, assert `ALARM_EVENTS` is present and bounded by
     `max_event_records`.
   - With `record_events=False`, assert detailed events can be omitted while
     alarm count and first/last alarm summaries remain available.
9. Deferred and unrelated requests:
   - Supplying `GMA_WITH_EMPIRICAL_LIMIT`, `baseline_replay_period`,
     `empirical_quantile`, or `target_false_alarm_rate` returns
     `severity="not_applicable"` with an empirical-limit warning.
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
    - Simulate non-finite GMA state or invalid computed limits.
    - Assert the public detector returns `severity="error"`, `"watch"`, or
      `not_applicable` according to project convention with
      `drift_detected=None` and a clear warning.

Recommended commands after implementation:

```text
python -m py_compile drift_algorithm\methods\streamingchangedetector.py
python -m pytest tests\test_geometric_moving_average.py
python -m pytest tests\test_adwin.py tests\test_kswin.py tests\test_page_hinkley_test.py tests\test_cusum.py tests\test_ewma.py
```

Manual review before marking implementation complete:

- Confirm public function signature matches the common contract.
- Confirm canonical measurement names match
  `drift_method_variant_measurement_summary.csv`.
- Confirm default variant is `GMA_CONTROL_CHART`.
- Confirm `reference_window` and `current_window` define a finite replay stream
  rather than a batch reference-vs-current statistic.
- Confirm omitted `center_line` and `sigma` are inferred only from the
  effective reference window, not current data.
- Confirm `lambda` is validated as `0 < lambda <= 1`.
- Confirm strict `GMA_STATISTIC > ucl` and `GMA_STATISTIC < lcl` crossing is
  used.
- Confirm top-level `p_value` remains `None`, and measurement `P_VALUE` is
  either `None` or omitted only if the project later decides not to emit
  optional p-value placeholders.
- Confirm event history, alarm direction, and final GMA state are auditable.
- Confirm `GMA_WITH_EMPIRICAL_LIMIT` fails explicitly until empirical limit
  policy is approved.
- Confirm interpretation text avoids root-cause, performance-degradation,
  supervised concept-drift, and retraining claims without labeled evidence and
  policy inputs.

## 13. Manager Review Points

- First implementation scope is `GMA_CONTROL_CHART` and `GMA_ONE_SIDED` over
  scalar numeric `(time, value)` rows only.
- DM-031 GMA is intentionally aligned with the exponentially weighted moving
  average style control-chart recurrence, but result fields and interpretation
  should use GMA naming.
- Although GMA is a sequential control chart, the current public API supplies
  finite timestamp windows; this design replays reference/current rows in
  chronological order and reports the resulting alarm state.
- `reference_window` and `current_window` are required for API consistency and
  for defining replay scope. The reference window also supplies default
  calibration values when `center_line` or `sigma` are omitted.
- Proposed defaults are `lambda=0.2`, `control_width=3.0`,
  `warmup_size=20`, `check_every=1`, and `reset_policy="none"`. These should
  be reviewed against target metric scale and operational alert policy.
- The first theoretical limit uses the steady-state GMA standard deviation
  `sigma * sqrt(lambda / (2 - lambda))`; startup-varying limits are deferred.
- `threshold_or_alpha` is only a compatibility alias for `control_width` in a
  narrow case; GMA does not return a p-value.
- `control_limit` is allowed as a compatibility input, but scalar
  `control_limit` is valid only for one-sided GMA because it is ambiguous for a
  two-sided control chart.
- `GMA_ONE_SIDED` is supported for upper or lower risk direction, but the
  direction must be declared before evaluation.
- `GMA_WITH_EMPIRICAL_LIMIT` remains deferred because empirical false alarm
  calibration needs a separate baseline replay contract.
- The public target is `detect_geometric_moving_average` in
  `drift_algorithm.methods.streamingchangedetector`.
