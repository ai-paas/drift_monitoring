# DM-002 Wasserstein Distance Design

## 1. Method Identity

- Method ID: `DM-002`
- Method name: `Wasserstein Distance`
- Category: `BatchDistributionComparison`
- Method kind: `detector`
- Status: `확정`
- Source catalog: `drift_methods_catalog.md`
- Source variant document: `algorithm_variants/wasserstein_distance_algorithm_variants.md`
- Source parameter tables:
  - `drift_method_variant_links.csv`
  - `drift_method_variant_measurement_summary.csv`
  - `drift_method_variant_parameters.csv`
  - `drift_method_parameter_guide.md`

The first implementation is a univariate numeric batch detector. It compares a
reference window and a current window by the 1-Wasserstein distance, also known
in this catalog as the Earth Mover's Distance family.

## 2. Purpose

`Wasserstein Distance` measures how much numeric distribution mass must move to
make the current sample match the reference sample. It is most useful when the
report needs a drift magnitude in the original value unit rather than only a
p-value.

Use this method when:

- the input signal is a scalar numeric feature, score, confidence, loss, or one
  numeric embedding summary
- both reference and current windows are available
- distance magnitude, feature ranking, or distance trend is the target output
- the operating team can provide or calibrate a distance threshold when an alarm
  is required

Do not use the first implementation for categorical labels, count tables,
probability vectors, text, multivariate vectors, raw embeddings, label/error
streams, or supervised concept-drift claims. Those require other schemas or
deferred variants.

## 3. Supported Variants

Supported for the first implementation:

- `WASSERSTEIN_1D_EXACT`
  - Default variant.
  - Uses the exact sample-level one-dimensional Wasserstein distance for one
    scalar numeric signal.
  - Emits `WASSERSTEIN_DISTANCE` and optional alarm state when a threshold is
    supplied.
  - Supports optional sample weights when they are supplied as DataFrame columns
    and pass validation.
- `WASSERSTEIN_APPROX_HISTOGRAM`
  - Uses equal-width histogram bins over the combined reference/current range.
  - Computes Wasserstein distance between bin centers with histogram counts as
    weights.
  - Emits `METHOD_POLICY` metadata so consumers can distinguish histogram
    approximation from exact sample-level distance.
- `WASSERSTEIN_WINDOW_TREND`
  - Uses the same one-dimensional reference/current distance as
    `WASSERSTEIN_1D_EXACT`.
  - Treats the single current window as the current trend point and emits
    `WINDOW_TREND_DISTANCE` plus `METHOD_POLICY.trend_policy`.
  - Uses `threshold` for the binary alarm. `trend_threshold`, when supplied, is
    recorded in `METHOD_POLICY` and metadata for downstream trend calibration.

Deferred variants that must return `severity="not_applicable"` until explicitly
implemented:

- `SLICED_WASSERSTEIN_EMBEDDING`
  - Needs embedding or multivariate schema, random projections, projection
    count, and seed handling.

Default variant selection:

```text
if params["variant_id"] is omitted:
    variant_id = "WASSERSTEIN_1D_EXACT"
```

## 4. Input Schema

Use the common `pandas.DataFrame` boundary from
`../input_output_contracts.md`.

Public function shape:

```python
def detect_wasserstein_distance(
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

Required DataFrame schema for the first implementation:

```text
time: datetime64[ns] or parseable timestamp
value: numeric integer or floating dtype
```

The caller may override column names with `time_col` and `value_col`. If
`value_col is None`, use `params["input_signal"]` as the numeric value column.
The resolved value column must contain scalar numeric values, not arrays,
objects, strings, categories, booleans, labels, or probability vectors.

Optional weight columns for `WASSERSTEIN_1D_EXACT`:

```text
sample_weights_reference: column name containing nonnegative numeric weights
sample_weights_current: column name containing nonnegative numeric weights
```

Weight columns are sliced with the same windows as the value column. If one
weight column is supplied, the matching window uses weights and the other window
uses unweighted samples unless its own weight column is supplied. Weights must
be finite, nonnegative, and have positive sum after invalid-row filtering.

Window contract:

```text
reference_window: inclusive (start_timestamp, end_timestamp)
current_window: inclusive (start_timestamp, end_timestamp)
```

Rows are processed as follows:

1. Validate that `time_col` and the resolved value column exist.
2. Convert `time_col` with `pd.to_datetime(..., errors="coerce")`.
3. Convert the value and optional weight columns with
   `pd.to_numeric(..., errors="coerce")`.
4. Sort by `time_col`.
5. Slice inclusive reference/current windows.
6. Drop rows with invalid timestamps, non-finite values, or invalid weights for
   calculation.
7. Record original and effective row counts in `metadata` and `measurements`.

Minimum effective sample sizes:

```text
min_reference_size: default 20
min_current_size: default 20
```

These defaults are implementation guards. If either effective sample size is
below its minimum, return `severity="not_applicable"` and do not compute a drift
decision.

## 5. Parameters

Accepted `params` keys and defaults:

```text
variant_id: "WASSERSTEIN_1D_EXACT"
threshold: None
threshold_or_alpha: optional alias for threshold
trend_threshold: optional reported policy value for WASSERSTEIN_WINDOW_TREND
min_reference_size: 20
min_current_size: 20
input_signal: optional value column name when value_col is None
distance_order: 1
normalization_policy: "none"
outlier_policy: "keep"
sample_weights_reference: optional reference weight column name
sample_weights_current: optional current weight column name
nan_policy: "drop"
exact_method: "scipy"
binning_policy: "none" for WASSERSTEIN_1D_EXACT and WASSERSTEIN_WINDOW_TREND, "equal_width" for WASSERSTEIN_APPROX_HISTOGRAM
bin_count: 20 for WASSERSTEIN_APPROX_HISTOGRAM
```

Parameter rules:

- `threshold`, when supplied, must be a finite numeric value and `threshold >= 0`.
- `threshold_or_alpha`, when supplied, overrides `threshold` as the distance
  alarm threshold. It is named generically in the catalog but is not a p-value
  alpha for this method.
- `distance_order` must be `1` in the first implementation.
- `normalization_policy` supports `none` only in the first implementation.
  Scaling changes the unit meaning of Wasserstein distance and should be owned
  by a later preprocessing layer or explicit variant.
- `outlier_policy` supports `keep` only in the first implementation.
- `nan_policy` supports `drop` only in the first implementation.
- `exact_method` supports `scipy` only in the first implementation.
- `binning_policy` must be `none` for exact 1D and window-trend calculation.
- `binning_policy` must be `equal_width` for `WASSERSTEIN_APPROX_HISTOGRAM`.
- `bin_count` must be an integer greater than or equal to 2 for
  `WASSERSTEIN_APPROX_HISTOGRAM`.
- `sample_weights_reference` and `sample_weights_current`, when supplied, must
  name existing columns.
- `trend_threshold` is recorded for `WASSERSTEIN_WINDOW_TREND`; `threshold` or
  `threshold_or_alpha` still owns the alarm rule.

Recommended scipy mapping:

```python
scipy.stats.wasserstein_distance(
    reference_values,
    current_values,
    u_weights=reference_weights,
    v_weights=current_weights,
)
```

If scipy is unavailable, the implementation may compute the unweighted exact
1D distance manually from sorted empirical CDFs. Weighted manual fallback is
not required in the first implementation; if weights are requested and scipy is
unavailable, return `severity="not_applicable"` with a warning.

## 6. Output Measurements

Return these canonical measurements for every successful supported run:

```text
WASSERSTEIN_DISTANCE: float
SAMPLE_SIZE_REFERENCE: int
SAMPLE_SIZE_CURRENT: int
```

Also include implementation metadata in `measurements` when available:

```text
DRIFT_ALARM_STATE: "drift_detected" | "normal" | "undetermined"
FEATURE_IMPORTANCE_OR_RANK: {"value_column": <column>, "rank": 1, "score": <distance>}
WINDOW_SIZE: {"reference": int, "current": int}
```

`FEATURE_IMPORTANCE_OR_RANK` is emitted as a trivial single-feature rank for
API consistency with the catalog mapping. A later multi-feature wrapper should
own true cross-feature ranking.

Do not emit these deferred canonical measurements in the first implementation:

```text
PROJECTION_COUNT
```

Result field mapping:

```text
drift_score = WASSERSTEIN_DISTANCE
p_value = None
test_statistic = WASSERSTEIN_DISTANCE
threshold = resolved threshold or None
```

## 7. Algorithm Steps

1. Normalize `params` to an empty dict when omitted.
2. Resolve `variant_id`; default to `WASSERSTEIN_1D_EXACT`.
3. Reject unsupported/deferred variants with `severity="not_applicable"` and a
   warning naming the variant and the missing input/calibration behavior.
4. Resolve threshold aliases, sample-size minima, value column, optional weight
   columns, and policy parameters.
5. Validate that both windows are supplied and are parseable timestamp pairs.
6. Validate required columns and numeric scalar value data.
7. Validate optional weight columns when supplied.
8. Convert and sort the DataFrame according to the common window handling
   contract.
9. Slice inclusive reference and current windows.
10. Drop rows with invalid timestamps, non-finite values, or invalid weights;
    record original and effective sample sizes.
11. If either effective sample is empty or below minimum, return not applicable.
12. Compute `WASSERSTEIN_DISTANCE` with `scipy.stats.wasserstein_distance`, or
    for `WASSERSTEIN_APPROX_HISTOGRAM`, compute equal-width histogram counts and
    pass bin centers with counts as weights.
    `WASSERSTEIN_WINDOW_TREND` uses the exact one-dimensional distance and emits
    the distance as the current trend point.
13. Convert the distance to a Python float and guard against NaN/inf.
14. Apply the drift decision rule from section 8.
15. Build `DriftResult` with method identity, variant, canonical measurements,
    counts, threshold, policy metadata, warnings, and concise interpretation
    text.

Interpretation text should state:

- which variant ran
- reference/current effective sample sizes
- Wasserstein distance value and original value unit context
- threshold and alarm state when a threshold is available
- that no p-value is produced by the first implementation
- any weighting, dropped-row, scale, or outlier-policy caution

## 8. Drift Decision Rule

Primary rule for `WASSERSTEIN_1D_EXACT`:

```text
if threshold is None:
    drift_detected = None
    severity = "watch"
    DRIFT_ALARM_STATE = "undetermined"
elif WASSERSTEIN_DISTANCE > threshold:
    drift_detected = True
    severity = "drift_detected"
    DRIFT_ALARM_STATE = "drift_detected"
else:
    drift_detected = False
    severity = "normal"
    DRIFT_ALARM_STATE = "normal"
```

Use strict `> threshold`, not `>= threshold`.

Rationale:

- Wasserstein distance is a distance score, not a hypothesis test in this first
  implementation.
- `threshold_or_alpha` is treated as a distance threshold for compatibility with
  the catalog parameter table. It must not be interpreted as a p-value alpha.
- If no threshold is supplied, returning `severity="watch"` preserves the useful
  distance measurement without claiming an alarm.

## 9. Warnings and Not-Applicable Conditions

Return `severity="not_applicable"` and `drift_detected=None` for:

- missing `time_col`
- missing resolved value column
- missing requested weight column
- unparseable reference/current windows
- omitted `reference_window` or `current_window`
- no rows in either sliced window before or after invalid-value filtering
- effective reference or current sample size below minimum
- unsupported `variant_id`
- sliced embedding variants
- nonnumeric scalar value data after coercion
- invalid `threshold`, `distance_order`, `normalization_policy`,
  `outlier_policy`, `nan_policy`, `exact_method`, `binning_policy`, or
  sample-size parameter
- invalid weights, including negative weights, non-finite weights, all-zero
  weight sum, or weights that are present only as object/list values
- current/reference window overlap when overlap policy is not explicitly defined
- weighted calculation requested while scipy is unavailable

Return a warning while still computing when:

- timestamps, values, or weights were dropped because they were invalid or
  non-finite
- no threshold was supplied, so distance is reported without a binary alarm
- optional sample weights are used, because weighted and unweighted distances
  are not directly comparable
- `threshold_or_alpha` is supplied and normalized to a distance threshold
- the value scale or unit changed upstream; the implementation can only warn
  when `params["input_unit"]` or similar metadata indicates a mismatch
- `trend_threshold` is supplied for a non-window-trend variant; it is recorded
  as a warning because `threshold` owns the alarm rule

Do not silently coerce categorical values, boolean flags, labels, embeddings, or
objects into a numeric Wasserstein detector.

## 10. Implementation Target

```text
module: drift_algorithm.methods.batchdistributioncomparison
function: detect_wasserstein_distance
```

The module should expose `detect_wasserstein_distance` through the package path
used by other batch distribution comparison implementations. If the concrete
package later separates one method per file, keep this public import path stable
or add a compatibility import.

Expected dependencies:

```text
pandas
numpy
scipy.stats.wasserstein_distance
```

Expected result object:

```text
DriftResult from drift_algorithm.docs/input_output_contracts.md equivalent code
contract
```

## 11. Verification Plan

Unit tests for the first implementation:

1. No-drift default exact case
   - Generate reference/current normal samples from the same distribution.
   - Assert `variant_id == "WASSERSTEIN_1D_EXACT"`.
   - Assert `WASSERSTEIN_DISTANCE`, `SAMPLE_SIZE_REFERENCE`, and
     `SAMPLE_SIZE_CURRENT` exist.
   - Assert `p_value is None`, `drift_score == test_statistic`, and
     `severity == "watch"` when no threshold is supplied.
2. Drift threshold case
   - Generate reference normal samples and current samples with a location
     shift.
   - Supply a deterministic threshold below the expected distance.
   - Assert `drift_detected is True`, `severity == "drift_detected"`,
     `DRIFT_ALARM_STATE == "drift_detected"`, and `threshold` is recorded.
3. Normal threshold case
   - Use similar reference/current samples and a threshold above the measured
     distance.
   - Assert `drift_detected is False`, `severity == "normal"`, and
     `DRIFT_ALARM_STATE == "normal"`.
4. Threshold alias routing
   - Supply `threshold_or_alpha`.
   - Assert it is recorded as the resolved distance threshold and a warning
     explains that it is not a p-value alpha.
5. Weight handling
   - Supply valid nonnegative reference/current weight columns.
   - Assert distance is returned and metadata records the weight columns.
   - Add invalid negative or all-zero weights and assert not applicable.
6. Not-applicable schema and window cases
   - Missing value column.
   - Missing windows.
   - Too-small effective samples.
   - Deferred variant such as `SLICED_WASSERSTEIN_EMBEDDING`.
   - Histogram variant with invalid `bin_count` or non-`equal_width`
     `binning_policy`.
   - Window-trend variant with non-`none` `binning_policy`.
   - Invalid policy such as `normalization_policy="standard"`.
   - Assert `severity == "not_applicable"`, `drift_detected is None`, and the
     warning identifies the cause.

Manual review before marking implementation complete:

- Confirm public function signature matches the common contract.
- Confirm canonical measurement names match
  `drift_method_variant_measurement_summary.csv`.
- Confirm deferred catalog variants fail explicitly instead of falling through
  to a misleading exact univariate calculation.
- Confirm `WASSERSTEIN_WINDOW_TREND` emits `WINDOW_TREND_DISTANCE` and
  `METHOD_POLICY.trend_policy`.
- Confirm Wasserstein distance is interpreted as an original-unit distance when
  `normalization_policy="none"`.
- Confirm `git diff` only changes
  `drift_algorithm/docs/method_designs/DM-002_wasserstein_distance.md`.
