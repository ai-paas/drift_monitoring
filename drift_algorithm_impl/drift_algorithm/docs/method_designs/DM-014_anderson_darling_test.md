# DM-014 Anderson-Darling Test Design

## Sprint 49 Implementation Note

Sprint 49 promotes `ONE_SAMPLE_ANDERSON_DARLING` and `K_SAMPLE_ANDERSON_DARLING` from deferred status for the server demo path. They execute through `scipy.stats.anderson_ksamp` over reference/current windows and record `execution_policy="anderson_ksamp_reference_current"` in metadata. Older deferred-status notes in this document are superseded for the harness/runtime path.

## 1. Method Identity

- Method ID: `DM-014`
- Method name: `Anderson-Darling Test`
- Category: `BatchDistributionComparison`
- Method kind: `detector`
- Status: `확정`
- Source catalog: `drift_methods_catalog.md`
- Source variant document: `algorithm_variants/anderson_darling_test_algorithm_variants.md`
- Source parameter tables:
  - `drift_method_variant_links.csv`
  - `drift_method_variant_measurement_summary.csv`
  - `drift_method_variant_parameters.csv`
  - `drift_method_parameter_guide.md`

The first implementation is a univariate numeric batch detector. It compares
the empirical distribution of a current window against a reference window with
the Anderson-Darling k-sample statistic, using two samples by default.

## 2. Purpose

`Anderson-Darling Test` answers whether a numeric feature, model score,
residual, latency, loss, or other scalar signal has a different distribution in
the current window than in the reference window. The catalog input is `numeric
sample`; the catalog outputs are `AD statistic` and `p-value`.

Use this method when:

- the signal is scalar numeric data
- reference and current windows are both available
- tail differences matter, such as high-latency, high-risk, or low-confidence
  regions
- a p-value alarm rule is acceptable for the first implementation

Do not use this method for categorical labels, count tables, probability
vectors, embeddings, multivariate features, text, or supervised error streams.
Those belong to other method families or schemas.

## 3. Supported Variants

Supported for the first implementation:

- `TWO_SAMPLE_ANDERSON_DARLING`
  - Default variant.
  - Compares the reference and current numeric samples directly.
  - Uses the Anderson-Darling k-sample implementation with exactly two groups.
- `TAIL_SENSITIVE_AD`
  - Uses the same two-sample AD statistic and p-value.
  - Adds tail summary metadata so reports can explain whether the upper tail,
    lower tail, or both tails changed.
  - Does not introduce a separate tail-only test statistic in the first
    implementation.

Deferred variants that must return `severity="not_applicable"` until their
extra contracts are implemented:

- `ONE_SAMPLE_ANDERSON_DARLING`
  - Requires a named theoretical distribution and parameter policy. The common
    `(time, value)` window contract alone is not enough to compute a comparable
    p-value.
- `K_SAMPLE_ANDERSON_DARLING`
  - Requires three or more named sample groups, such as a `sample_group_col` or
    a structured `sample_groups` parameter. The first common function contract
    only owns reference/current windows.

Default variant selection:

```text
if params["variant_id"] is omitted:
    variant_id = "TWO_SAMPLE_ANDERSON_DARLING"
```

## 4. Input Schema

Use the common `pandas.DataFrame` input boundary from
`../input_output_contracts.md`.

Public function shape:

```python
def detect_anderson_darling_test(
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
`value_col is None`, resolve the numeric value column from
`params["input_signal"]`. The resolved value column must contain scalar numeric
values, not arrays, objects, strings, categories, booleans, labels, or
probability vectors.

Window contract:

```text
reference_window: inclusive (start_timestamp, end_timestamp)
current_window: inclusive (start_timestamp, end_timestamp)
```

Rows are processed as follows:

1. Validate that `time_col` and the resolved value column exist.
2. Convert `time_col` with `pd.to_datetime(..., errors="coerce")`.
3. Convert the value column with `pd.to_numeric(..., errors="coerce")`.
4. Sort by `time_col`.
5. Slice inclusive reference/current windows.
6. Drop rows with invalid timestamps or non-finite values for calculation.
7. Record original and effective row counts in `metadata` and `measurements`.

Minimum effective sample sizes:

```text
min_reference_size: default 20
min_current_size: default 20
```

These are implementation guards for stable monitoring behavior. If either
effective sample size is below its minimum, return
`severity="not_applicable"` and do not compute a drift decision.

## 5. Parameters

Accepted `params` keys and defaults:

```text
variant_id: "TWO_SAMPLE_ANDERSON_DARLING"
alpha: 0.05
threshold_or_alpha: optional alias for alpha
significance_level: optional alias for alpha
input_signal: optional value column name when value_col is None
p_value_method: "asymptotic"
distribution_family: "empirical"
sample_groups: optional metadata only in the first implementation
min_reference_size: 20
min_current_size: 20
nan_policy: "drop"
tail_quantiles: [0.05, 0.95]
tail_direction: "both"
multiple_testing_correction: "none"
```

Parameter rules:

- `alpha` must be numeric and satisfy `0 < alpha < 1`.
- `threshold_or_alpha`, when supplied, overrides `alpha`.
- `significance_level`, when supplied, is normalized to `alpha`; if both aliases
  are supplied with conflicting values, return not applicable.
- `p_value_method` supports `"asymptotic"` only in the first implementation.
- `distribution_family` must be `"empirical"` for supported variants.
- `nan_policy` supports `"drop"` only.
- `tail_quantiles` must contain two floats satisfying
  `0 < lower < upper < 1`; defaults are the 5th and 95th percentiles.
- `tail_direction` must be one of `"lower"`, `"upper"`, or `"both"`.
- `multiple_testing_correction` is recorded as metadata only. No correction is
  applied inside this single-feature method.

Recommended scipy mapping:

```python
scipy.stats.anderson_ksamp(
    [reference_values, current_values],
    midrank=True,
)
```

Use the returned statistic and p-value. If scipy is unavailable, return
`severity="error"` or `severity="watch"` according to the project convention for
missing optional dependencies, with `drift_detected=None` and a warning that the
AD statistic and p-value could not be computed.

## 6. Output Measurements

`drift_method_variant_measurement_summary.csv` maps all DM-014 variants to:

```text
TEST_STATISTIC
P_VALUE
DRIFT_ALARM_STATE
```

Return these canonical measurements for every successful supported run:

```text
TEST_STATISTIC: float
P_VALUE: float | None
DRIFT_ALARM_STATE: "drift_detected" | "normal" | "undetermined"
SAMPLE_SIZE_REFERENCE: int
SAMPLE_SIZE_CURRENT: int
WINDOW_SIZE: {"reference": int, "current": int}
```

For `TAIL_SENSITIVE_AD`, also include tail metadata:

```text
TAIL_QUANTILES: {"lower": float, "upper": float}
TAIL_COUNTS_REFERENCE: {"lower": int, "upper": int}
TAIL_COUNTS_CURRENT: {"lower": int, "upper": int}
TAIL_RATES_REFERENCE: {"lower": float, "upper": float}
TAIL_RATES_CURRENT: {"lower": float, "upper": float}
TAIL_RATE_DELTA: {"lower": float, "upper": float}
```

Tail thresholds are computed from the reference sample at `tail_quantiles`.
Lower-tail counts are values `<= reference_lower_quantile`; upper-tail counts
are values `>= reference_upper_quantile`.

Result field mapping:

```text
drift_score = TEST_STATISTIC
p_value = P_VALUE
test_statistic = TEST_STATISTIC
threshold = alpha
```

Interpretation text should state:

- which variant ran
- reference/current effective sample sizes
- AD statistic value
- p-value and alpha
- whether the result crossed the drift rule
- for `TAIL_SENSITIVE_AD`, which tail rate increased or decreased in the
  current window

## 7. Algorithm Steps

1. Normalize `params` to an empty dict when omitted.
2. Resolve `variant_id`; default to `TWO_SAMPLE_ANDERSON_DARLING`.
3. Reject deferred or unknown variants with `severity="not_applicable"` and a
   warning naming the unsupported variant.
4. Resolve `alpha`, `p_value_method`, `distribution_family`, sample-size
   minima, `nan_policy`, and the value column.
5. Validate that both reference and current windows are supplied and parseable.
6. Validate required columns and scalar numeric value data.
7. Convert and sort the DataFrame according to the common window handling
   contract.
8. Slice inclusive reference and current windows.
9. Drop rows with invalid timestamps or non-finite values; record original and
   effective counts.
10. If either effective sample is empty or below minimum, return not applicable.
11. Convert the two effective samples to one-dimensional `numpy.ndarray`
    objects with float dtype.
12. Call `scipy.stats.anderson_ksamp` with the two arrays.
13. Convert statistic and p-value to Python floats; guard against NaN/inf.
14. If scipy reports that the p-value is capped or floored, preserve the value
    but add a warning because the exact extremity is not known.
15. For `TAIL_SENSITIVE_AD`, compute reference-quantile tail thresholds and
    reference/current tail counts, rates, and deltas.
16. Apply the drift decision rule from section 8.
17. Build `DriftResult` with method identity, variant, canonical measurements,
    counts, windows, parameters, warnings, and concise interpretation text.

## 8. Drift Decision Rule

Primary rule for supported variants:

```text
if p_value is None:
    drift_detected = None
    severity = "watch"
elif p_value < alpha:
    drift_detected = True
    severity = "drift_detected"
else:
    drift_detected = False
    severity = "normal"
```

Use strict `< alpha`, not `<= alpha`.

`TAIL_SENSITIVE_AD` uses the same p-value rule. Tail metadata is explanatory; it
does not override the AD p-value decision in the first implementation.

Interpret the AD statistic only within this method and variant. A larger AD
statistic generally means stronger evidence against equal distributions, with
relatively high sensitivity to tail differences, but it must not be compared
directly with KS, Cramer-von Mises, chi-square, or other test statistics.

## 9. Warnings and Not-Applicable Conditions

Return `severity="not_applicable"` and `drift_detected=None` for:

- missing `time_col`
- missing resolved value column
- omitted or unparseable `reference_window` or `current_window`
- no rows in either sliced window before or after invalid-value filtering
- effective reference or current sample size below minimum
- unsupported or deferred `variant_id`
- nonnumeric scalar value data after coercion
- invalid `alpha`, alias conflict, `p_value_method`, `distribution_family`,
  `nan_policy`, `tail_quantiles`, `tail_direction`, or sample-size parameter
- current/reference window overlap when overlap policy is not explicitly defined
- `ONE_SAMPLE_ANDERSON_DARLING` without a fully specified theoretical
  distribution contract
- `K_SAMPLE_ANDERSON_DARLING` without a first-class multi-group input contract

Return a warning while still computing when:

- timestamps or values were dropped because they were invalid or non-finite
- duplicate values or ties are common enough to make continuous-distribution
  interpretation weaker
- scipy reports a capped or floored p-value
- `multiple_testing_correction` is not `"none"`; record that this method does
  not apply correction internally
- `TAIL_SENSITIVE_AD` has too few observations in one or both tails to explain
  the tail direction confidently

Do not silently coerce categorical values, boolean flags, labels, embeddings,
lists, or objects into the numeric Anderson-Darling detector.

## 10. Implementation Target

```text
module: drift_algorithm.methods.batchdistributioncomparison
function: detect_anderson_darling_test
```

The module should expose `detect_anderson_darling_test` through the package path
used by other method implementations. If the concrete package later separates
one method per file, keep this public import path stable or add a compatibility
import.

Expected dependencies:

```text
pandas
numpy
scipy.stats.anderson_ksamp
```

Expected result object:

```text
DriftResult from drift_algorithm/docs/input_output_contracts.md equivalent code
contract
```

## 11. Verification Plan

Unit tests for the first implementation:

1. No-drift default two-sample case
   - Generate reference/current normal samples from the same distribution.
   - Assert `variant_id == "TWO_SAMPLE_ANDERSON_DARLING"`.
   - Assert `TEST_STATISTIC`, `P_VALUE`, `DRIFT_ALARM_STATE`,
     `SAMPLE_SIZE_REFERENCE`, and `SAMPLE_SIZE_CURRENT` exist.
   - Assert `drift_detected is False` for a deterministic seed chosen to keep
     `p_value >= 0.05`.
2. Drift candidate two-sample case
   - Generate reference normal samples and current samples with a location or
     scale shift.
   - Assert `p_value < alpha`, `drift_detected is True`, and
     `severity == "drift_detected"`.
3. Tail-sensitive metadata case
   - Use `TAIL_SENSITIVE_AD` with current data containing more upper-tail
     observations than the reference distribution.
   - Assert the AD measurements exist and `TAIL_RATE_DELTA["upper"] > 0`.
   - Assert tail metadata does not override the p-value decision rule.
4. Parameter alias and validation case
   - Assert `threshold_or_alpha` and `significance_level` route to `alpha`.
   - Assert conflicting alias values return `severity="not_applicable"`.
5. Not-applicable schema and window cases
   - Missing value column.
   - Missing windows.
   - Too-small effective samples.
   - Deferred variants `ONE_SAMPLE_ANDERSON_DARLING` and
     `K_SAMPLE_ANDERSON_DARLING`.
   - Assert `severity == "not_applicable"`, `drift_detected is None`, and the
     warning identifies the cause.
6. Warning behavior
   - Include invalid timestamps, NaN/inf values, repeated values, and
     `multiple_testing_correction != "none"`.
   - Assert computation proceeds when enough valid data remains and warnings are
     recorded.

Manual review before marking implementation complete:

- Confirm public function signature matches the common contract.
- Confirm canonical measurement names match
  `drift_method_variant_measurement_summary.csv`.
- Confirm deferred variants fail explicitly instead of falling through to a
  misleading two-sample calculation.
- Confirm `git diff` only changes
  `drift_algorithm/docs/method_designs/DM-014_anderson_darling_test.md`.
