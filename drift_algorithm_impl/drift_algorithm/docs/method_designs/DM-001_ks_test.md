# DM-001 KS Test Design

## Sprint 49 Implementation Note

Sprint 49 promotes `ONE_SAMPLE_KS_KNOWN_CDF`, `LILLIEFORS_RELATED_ONE_SAMPLE`, `HIGHER_ORDER_KS`, and `TWO_SAMPLE_KS_APPROX_QUANTILE` from deferred status for the server demo path. They execute through the two-sample KS engine over reference/current windows and record `execution_policy="two_sample_ks_reference_current"` in metadata. Older deferred-status notes in this document are superseded for the harness/runtime path.

## 1. Method Identity

- Method ID: `DM-001`
- Method name: `KS Test`
- Category: `BatchDistributionComparison`
- Method kind: `detector`
- Status: `확정`
- Source catalog: `drift_methods_catalog.md`
- Source variant document: `algorithm_variants/ks_test_algorithm_variants.md`
- Source parameter tables:
  - `drift_method_variant_links.csv`
  - `drift_method_variant_measurement_summary.csv`
  - `drift_method_variant_parameters.csv`
  - `drift_method_parameter_guide.md`

The first implementation is a univariate numeric batch detector. It compares a
reference window and a current window by the maximum absolute difference between
their empirical cumulative distribution functions (ECDFs).

## 2. Purpose

`KS Test` answers whether a numeric feature, score, or single embedding
dimension has a different distribution in the current window than in the
reference window. The primary catalog input is a numeric signal, and the primary
catalog outputs are `KS_STATISTIC` and `P_VALUE`.

Use this method when:

- the signal is continuous or close to continuous numeric data
- both reference and current samples are available
- the main question is distribution drift, not only mean shift or variance shift
- a p-value-based alarm rule is acceptable for the first implementation

Do not use the first implementation for categorical labels, count tables,
probability vectors, text, multivariate vectors, label/error streams, or
streaming KSWIN behavior. Those belong to other schemas or methods.

## 3. Supported Variants

Supported for the first implementation:

- `TWO_SAMPLE_KS_TWO_SIDED`
  - Default variant.
  - Uses `alternative="two-sided"`.
  - Recommended by the KS selection guide for default feature drift when the
    drift direction is unknown.
- `TWO_SAMPLE_KS_ONE_SIDED_GREATER`
  - Uses `alternative="greater"`.
  - Requires a documented prior directional hypothesis.
- `TWO_SAMPLE_KS_ONE_SIDED_LESS`
  - Uses `alternative="less"`.
  - Requires a documented prior directional hypothesis.
- `TWO_SAMPLE_KS_EXACT_PVALUE`
  - Same two-sample statistic, with `p_value_method="exact"`.
  - Appropriate when sample sizes are small or p-value precision is decision
    critical.
- `TWO_SAMPLE_KS_ASYMPTOTIC_PVALUE`
  - Same two-sample statistic, with `p_value_method="asymp"`.
  - Appropriate for large-scale or repeated monitoring.
- `KS_WITH_TIES_OR_DISCRETE_CAUTION`
  - Uses the two-sample KS calculation but adds warnings when ties or low
    unique-value ratios make classical continuous-KS p-value interpretation
    weak.

Deferred variants that must return `severity="not_applicable"` until explicitly
implemented:

- `ONE_SAMPLE_KS_KNOWN_CDF`
- `LILLIEFORS_RELATED_ONE_SAMPLE`
- `HIGHER_ORDER_KS`
- `TWO_SAMPLE_KS_APPROX_QUANTILE`

Default variant selection:

```text
if params["variant_id"] is omitted:
    variant_id = "TWO_SAMPLE_KS_TWO_SIDED"
```

## 4. Input Schema

Use the common `pandas.DataFrame` boundary from
`../input_output_contracts.md`.

Public function shape:

```python
def detect_ks_test(
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

These defaults are implementation guards, not statistical guarantees. If either
effective sample size is below its minimum, return `severity="not_applicable"`
and do not compute a drift decision.

## 5. Parameters

Accepted `params` keys and defaults:

```text
variant_id: "TWO_SAMPLE_KS_TWO_SIDED"
alpha: 0.05
threshold_or_alpha: optional alias for alpha
alternative: derived from variant_id unless explicitly supplied
p_value_method: "auto"
min_reference_size: 20
min_current_size: 20
input_signal: optional value column name when value_col is None
tie_policy: "warn_only"
tie_unique_ratio_threshold: 0.95
multiple_testing_correction: "none"
direction_or_alternative: optional alias for alternative
nan_policy: "drop"
```

Parameter rules:

- `alpha` must be numeric and satisfy `0 < alpha < 1`.
- `threshold_or_alpha`, when supplied, overrides `alpha`.
- `alternative` must be one of `two-sided`, `greater`, or `less`.
- `direction_or_alternative`, when supplied, is normalized to `alternative`.
- `p_value_method` must be one of `auto`, `exact`, or `asymp`.
- `TWO_SAMPLE_KS_EXACT_PVALUE` forces `p_value_method="exact"`.
- `TWO_SAMPLE_KS_ASYMPTOTIC_PVALUE` forces `p_value_method="asymp"`.
- One-sided variants force their documented `alternative` unless an explicit
  conflicting `alternative` is passed; conflicting values are not applicable.
- `multiple_testing_correction` is accepted only for metadata in the first
  implementation. No correction is applied unless a later multi-feature wrapper
  owns the family-wise procedure.
- `tie_policy` supports `warn_only` only in the first implementation.

Recommended scipy mapping:

```python
scipy.stats.ks_2samp(
    reference_values,
    current_values,
    alternative=alternative,
    method=p_value_method,  # "auto", "exact", or "asymp"
)
```

If scipy is unavailable, the implementation may compute `KS_STATISTIC` manually
from sorted ECDFs, but it must return `P_VALUE=None`, `drift_detected=None`,
`severity="watch"`, and a warning that p-value calculation was unavailable.

## 6. Output Measurements

Return these canonical measurements for every successful supported run:

```text
KS_STATISTIC: float
P_VALUE: float | None
SAMPLE_SIZE_REFERENCE: int
SAMPLE_SIZE_CURRENT: int
```

Also include implementation metadata in `measurements` when available:

```text
TEST_STATISTIC: same value as KS_STATISTIC for generic consumers
DRIFT_ALARM_STATE: "drift_detected" | "normal" | "undetermined"
WINDOW_SIZE: {"reference": int, "current": int}
```

For `KS_WITH_TIES_OR_DISCRETE_CAUTION`, the canonical measurements remain
`KS_STATISTIC` and `P_VALUE`; add a warning and metadata fields:

```text
metadata["tie_policy"] = "warn_only"
metadata["reference_unique_ratio"] = ...
metadata["current_unique_ratio"] = ...
metadata["combined_unique_ratio"] = ...
```

Result field mapping:

```text
drift_score = KS_STATISTIC
p_value = P_VALUE
test_statistic = KS_STATISTIC
threshold = alpha
```

`APPROXIMATION_ERROR_BOUND` is not emitted in the first implementation because
`TWO_SAMPLE_KS_APPROX_QUANTILE` is deferred.

## 7. Algorithm Steps

1. Normalize `params` to an empty dict when omitted.
2. Resolve `variant_id`; default to `TWO_SAMPLE_KS_TWO_SIDED`.
3. Reject unsupported/deferred variants with `severity="not_applicable"` and a
   warning naming the unsupported variant.
4. Resolve `alpha`, `alternative`, `p_value_method`, sample-size minima, and
   value column.
5. Validate that both windows are supplied and are parseable timestamp pairs.
6. Validate required columns and numeric scalar value data.
7. Convert and sort the DataFrame according to the common window handling
   contract.
8. Slice inclusive reference and current windows.
9. Drop rows with invalid timestamps or non-finite values; record original and
   effective sample sizes.
10. If either effective sample is empty or below minimum, return not applicable.
11. For `KS_WITH_TIES_OR_DISCRETE_CAUTION`, or for any supported variant where
    ties are detected, compute unique ratios and append warnings when
    `combined_unique_ratio < tie_unique_ratio_threshold`.
12. Call `scipy.stats.ks_2samp` with the resolved `alternative` and
    `p_value_method`.
13. Convert statistic and p-value to Python floats; guard against NaN/inf.
14. Apply the drift decision rule from section 8.
15. Build `DriftResult` with method identity, variant, canonical measurements,
    counts, p-value method, alternative, windows, warnings, and concise
    interpretation text.

Interpretation text should state:

- which variant ran
- reference/current effective sample sizes
- KS statistic value
- p-value and alpha when p-value is available
- whether the result crossed the drift rule
- any tie/discrete-data caution

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

`KS_WITH_TIES_OR_DISCRETE_CAUTION` uses the same rule, but if tie warnings are
present and the p-value crosses alpha, set:

```text
drift_detected = True
severity = "drift_candidate"
```

This preserves the signal while making clear that the classical continuous-KS
p-value should be treated cautiously. If no tie warning is present, use the
normal supported-variant rule.

One-sided interpretation must follow scipy KS semantics:

- `alternative="greater"` tests whether the reference CDF is greater than the
  current CDF at some point.
- `alternative="less"` tests whether the reference CDF is less than the current
  CDF at some point.

Do not translate one-sided results into "value increased" or "value decreased"
without additional quantile or CDF-difference context.

## 9. Warnings and Not-Applicable Conditions

Return `severity="not_applicable"` and `drift_detected=None` for:

- missing `time_col`
- missing resolved value column
- unparseable reference/current windows
- omitted `reference_window` or `current_window`
- no rows in either sliced window before or after invalid-value filtering
- effective reference or current sample size below minimum
- unsupported `variant_id`
- deferred one-sample, Lilliefors, higher-order, or approximate-quantile variants
- nonnumeric scalar value data after coercion
- invalid `alpha`, `alternative`, `p_value_method`, `tie_policy`, or sample-size
  parameter
- conflicting explicit `alternative` for a forced one-sided variant
- current/reference window overlap when overlap policy is not explicitly defined

Return a warning while still computing when:

- timestamps or values were dropped because they were invalid or non-finite
- ties are present in either sample
- `combined_unique_ratio < tie_unique_ratio_threshold`
- sample size is very large and `p_value_method="exact"` may be slow
- `multiple_testing_correction` is not `none`; record that the first
  implementation does not apply correction internally
- scipy is unavailable and only the statistic can be computed

Do not silently coerce categorical values, boolean flags, labels, embeddings, or
objects into a numeric KS detector.

## 10. Implementation Target

```text
module: drift_algorithm.methods.batchdistributioncomparison
function: detect_ks_test
```

The module should expose `detect_ks_test` through the package path used by other
method implementations. If the concrete package later separates one method per
file, keep this public import path stable or add a compatibility import.

Expected dependencies:

```text
pandas
numpy
scipy.stats.ks_2samp
```

Expected result object:

```text
DriftResult from drift_algorithm.docs/input_output_contracts.md equivalent code
contract
```

## 11. Verification Plan

Unit tests for the first implementation:

1. No-drift default two-sided case
   - Generate reference/current normal samples from the same distribution.
   - Assert `variant_id == "TWO_SAMPLE_KS_TWO_SIDED"`.
   - Assert `KS_STATISTIC`, `TEST_STATISTIC`, `P_VALUE`,
     `SAMPLE_SIZE_REFERENCE`, and `SAMPLE_SIZE_CURRENT` exist.
   - Assert `drift_detected is False` for a deterministic seed chosen to keep
     `p_value >= 0.05`.
2. Drift candidate two-sided case
   - Generate reference normal samples and current samples with a location shift.
   - Assert `p_value < alpha`, `drift_detected is True`, and
     `severity == "drift_detected"`.
3. One-sided parameter routing
   - Run `TWO_SAMPLE_KS_ONE_SIDED_GREATER` and
     `TWO_SAMPLE_KS_ONE_SIDED_LESS`.
   - Assert the resolved `alternative` is recorded in metadata and conflicting
     explicit alternatives return not applicable.
4. Exact/asymptotic p-value routing
   - Run `TWO_SAMPLE_KS_EXACT_PVALUE` and
     `TWO_SAMPLE_KS_ASYMPTOTIC_PVALUE`.
   - Assert `metadata["p_value_method"]` is `exact` and `asymp` respectively.
5. Ties/discrete caution
   - Use repeated integer-like values.
   - Assert the KS statistic and p-value are returned, warnings mention ties or
     discrete caution, and a crossing p-value yields `severity="drift_candidate"`.
6. Not-applicable schema and window cases
   - Missing value column.
   - Missing windows.
   - Too-small effective samples.
   - Deferred variant such as `ONE_SAMPLE_KS_KNOWN_CDF`.
   - Assert `severity == "not_applicable"`, `drift_detected is None`, and the
     warning identifies the cause.

Manual review before marking implementation complete:

- Confirm public function signature matches the common contract.
- Confirm canonical measurement names match
  `drift_method_variant_measurement_summary.csv`.
- Confirm unsupported catalog variants fail explicitly instead of falling through
  to a misleading two-sample calculation.
- Confirm `git diff` only changes files owned by the relevant work unit.
