# DM-020 F-test / Variance Test 계열 Design

## Sprint 49 Implementation Note

Sprint 49 promotes `ANOVA_F_TEST_GROUP_MEAN` and `MODEL_COMPARISON_F_TEST` from deferred status for the server demo path. `ANOVA_F_TEST_GROUP_MEAN` executes as one-way ANOVA over reference/current groups and records `execution_policy="one_way_anova_reference_current"`. `MODEL_COMPARISON_F_TEST` executes through the variance-ratio F engine and records `execution_policy="variance_ratio_reference_current"`. Older deferred-status notes in this document are superseded for the harness/runtime path.

## 1. Method Identity

- Method ID: `DM-020`
- Method name: `F-test / Variance Test 계열`
- Category: `BatchDistributionComparison`
- Method kind: `detector`
- Status: `확정`
- Source catalog: `drift_methods_catalog.md`
- Source variant document: `algorithm_variants/f_test_algorithm_variants.md`
- Source parameter tables:
  - `drift_method_variant_links.csv`
  - `drift_method_variant_measurement_summary.csv`
  - `drift_method_variant_parameters.csv`
  - `drift_method_parameter_guide.md`

The first implementation is a univariate numeric batch detector. It compares
the sample variance of a current `(time, value)` window against the sample
variance of a reference `(time, value)` window with an F distribution p-value.

## 2. Purpose

`F-test / Variance Test 계열` answers whether a scalar numeric monitoring
signal has a materially different variance in the current window than in the
reference window. The catalog input is `variance, model comparison statistic`;
the catalog outputs are `F statistic` and `p-value`.

Use the first implementation when:

- the signal is scalar numeric data such as score, latency, loss, residual,
  cost, confidence, calibration error, or a numeric feature
- reference and current windows are both available
- the monitoring question concerns variance or scale change rather than mean
  shift or full distribution change
- the data is sufficiently close to the normality/independence assumptions for
  a classical variance-ratio F-test to be useful as a screening signal
- a p-value alarm rule is acceptable for the first implementation

Do not use the first implementation for categorical labels, count tables,
probability vectors, embeddings, multivariate features, text, SHAP matrices,
supervised error streams, or direct model object comparison. Those require
other method families or a separate input schema.

## 3. Supported Variants

Supported for the first implementation:

- `F_TEST_EQUAL_VARIANCE`
  - Default and only computing variant in the first implementation.
  - Compares reference and current numeric samples directly.
  - Computes sample variances with `ddof=1`, F statistic, degrees of freedom,
    and p-value from the F distribution.
  - Supports two-sided and one-sided alternatives through an explicit
    `alternative` parameter.

Implementation-ready but deferred until a multi-group input contract is added:

- `ANOVA_F_TEST_GROUP_MEAN`
  - Conceptually valid for comparing means across three or more groups.
  - Requires a first-class `group_col`, `sample_group_col`, or structured
    `sample_groups` contract and group-level sample-size rules.
  - Must return `severity="not_applicable"` in the first implementation with a
    warning that the multi-group ANOVA contract is not implemented.

Conceptually valid but deferred until a model-comparison contract is approved:

- `MODEL_COMPARISON_F_TEST`
  - Requires nested model definitions or precomputed residual sums of squares,
    degrees of freedom, model identifiers, and validation of nested-model
    assumptions.
  - The common `(time, value)` reference/current window contract is not enough
    to define this variant.
  - Must return `severity="not_applicable"` in the first implementation with a
    warning that model-comparison inputs are not implemented.

Default variant selection:

```text
if params["variant_id"] is omitted:
    variant_id = "F_TEST_EQUAL_VARIANCE"
```

## 4. Input Schema

Use the common `pandas.DataFrame` input boundary from
`../input_output_contracts.md`.

Public function shape:

```python
def detect_f_test_variance_test(
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

Required DataFrame schema for `F_TEST_EQUAL_VARIANCE`:

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
min_reference_size: default 3
min_current_size: default 3
low_power_sample_size: default 20
```

The hard minimum is 3 because an unbiased sample variance needs at least two
observations and monitoring results with exactly two observations are too
unstable for this detector. If either effective sample size is below its
minimum, return `severity="not_applicable"` and do not compute a drift decision.

## 5. Parameters

Method-specific parameters come from `drift_method_parameter_guide.md`,
`drift_method_variant_parameters.csv`, and the variant source document.

Accepted `params` keys and defaults for the first implementation:

| Param | Type | Default | Applies to | Meaning |
|---|---:|---:|---|---|
| `variant_id` | string | `F_TEST_EQUAL_VARIANCE` | all | Variant selector. Only `F_TEST_EQUAL_VARIANCE` computes in the first implementation. |
| `alpha` | float | `0.05` | supported variant | Canonical significance level for the p-value drift rule. |
| `threshold_or_alpha` | float | optional | supported variant | Alias for `alpha`; if both are supplied they must agree. |
| `significance_level` | float | optional | supported variant | Alias for `alpha`; if supplied with another alpha alias it must agree. |
| `alternative` | string | `two-sided` | supported variant | Accepted values: `two-sided`, `both`, `greater`, `less`, `current_greater`, `current_less`, `reference_greater`, `reference_less`. |
| `variance_ratio_definition` | string | `current_over_reference` | supported variant | Defines the reported raw variance ratio and default F numerator. |
| `p_value_method` | string | `scipy` | supported variant | Accepted values: `scipy`, `f_distribution`, `local`. `scipy` and `f_distribution` both use the F CDF/SF; `local` is the fallback implementation. |
| `input_signal` | string | optional | supported variant | Value column name only when `value_col is None`; otherwise recorded as metadata label. |
| `min_reference_size` | int | `3` | supported variant | Minimum effective reference sample size after invalid rows are dropped. |
| `min_current_size` | int | `3` | supported variant | Minimum effective current sample size after invalid rows are dropped. |
| `low_power_sample_size` | int | `20` | supported variant | Warn when either effective sample is below this count but still above the hard minimum. |
| `nan_policy` | string | `drop` | supported variant | First implementation supports `drop`/`omit` only. |
| `normality_warning_policy` | string | `warn_only` | supported variant | Warn that F-test variance p-values are sensitive to non-normality. No normality pre-test gates execution. |
| `zero_variance_policy` | string | `not_applicable` | supported variant | Accepted value for first implementation: `not_applicable`. Zero sample variance prevents a valid variance-ratio p-value. |
| `sample_imbalance_warning_ratio` | float | `10.0` | supported variant | Warn when larger sample size divided by smaller sample size exceeds this ratio. |
| `multiple_testing_correction` | string | `none` | supported variant | Recorded as metadata only. Correction is not applied inside this single-signal detector. |
| `group_col` / `sample_group_col` / `sample_groups` | object | optional | deferred ANOVA | Recognized only to explain why `ANOVA_F_TEST_GROUP_MEAN` is deferred. |
| `restricted_model` / `full_model` / `rss_restricted` / `rss_full` / `df_restricted` / `df_full` | object | optional | deferred model comparison | Recognized only to explain why `MODEL_COMPARISON_F_TEST` is deferred. |

Parameter rules:

- `alpha`, `threshold_or_alpha`, and `significance_level` must be numeric and
  satisfy `0 < value < 1`.
- Alpha aliases must not conflict. Conflicting values return
  `severity="not_applicable"`.
- `alternative="two-sided"` and `"both"` are aliases.
- `alternative="greater"` and `"current_greater"` mean the current variance is
  tested as larger than the reference variance.
- `alternative="less"` and `"current_less"` mean the current variance is tested
  as smaller than the reference variance.
- `alternative="reference_greater"` is the same direction as
  `current_less`; `alternative="reference_less"` is the same direction as
  `current_greater`.
- `variance_ratio_definition` supports `current_over_reference` only in the
  first implementation. Other definitions return not applicable so statistic
  direction and p-value direction are never ambiguous.
- `p_value_method="scipy"` should use `scipy.stats.f` when SciPy is available.
  `p_value_method="f_distribution"` is an explicit alias for the same policy.
  `p_value_method="local"` uses a local F CDF/SF implementation only if the
  project already provides or approves one; otherwise return
  `severity="error"` or `severity="watch"` with `drift_detected=None`.
- `nan_policy` supports `"drop"` and `"omit"` as aliases for dropping invalid
  rows. Other values return not applicable.
- `normality_warning_policy` supports `"warn_only"` only. The detector should
  not run a separate normality test in the first implementation.
- `zero_variance_policy` supports `"not_applicable"` only. Infinite or zero
  variance-ratio outputs should not be reported as valid F-test p-values.
- `min_reference_size`, `min_current_size`, and `low_power_sample_size` must be
  positive integers; the sample-size minima must be at least 3.
- `sample_imbalance_warning_ratio` must be numeric and at least `1`.
- `multiple_testing_correction != "none"` adds a warning and is recorded in
  metadata, but the p-value is not corrected by this detector.
- Reject or warn on unrelated params such as `feature_cols`, `category_col`,
  `count_col`, `embedding_cols`, label columns, classifier settings, binning
  settings, or paired-sample settings.

## 6. Statistic and P-value Policy

Sample variance policy:

```text
variance_reference = np.var(reference_values, ddof=1)
variance_current = np.var(current_values, ddof=1)
df_reference = n_reference - 1
df_current = n_current - 1
variance_ratio = variance_current / variance_reference
```

The reported `variance_ratio` is always `current_over_reference` in the first
implementation. This makes interpretation stable:

```text
variance_ratio > 1 means current variance is larger than reference variance
variance_ratio < 1 means current variance is smaller than reference variance
variance_ratio = 1 means equal sample variances
```

F statistic and p-value policy by alternative:

```text
current_greater:
    F = variance_current / variance_reference
    df_num = df_current
    df_den = df_reference
    p_value = survival_function_F(F, df_num, df_den)

current_less:
    F = variance_current / variance_reference
    df_num = df_current
    df_den = df_reference
    p_value = cdf_F(F, df_num, df_den)

two-sided:
    F_directional = variance_current / variance_reference
    p_lower = cdf_F(F_directional, df_current, df_reference)
    p_upper = survival_function_F(F_directional, df_current, df_reference)
    p_value = min(1.0, 2.0 * min(p_lower, p_upper))
    TEST_STATISTIC = max(variance_current, variance_reference)
                     / min(variance_current, variance_reference)
    STATISTIC_DEFINITION = "larger_variance_over_smaller_variance"
```

For one-sided alternatives, `TEST_STATISTIC` is the directional
`current_over_reference` F statistic. For `two-sided`, `TEST_STATISTIC` is
reported as the nonnegative extremity ratio `larger_variance_over_smaller`
because the statistic should increase as evidence against equal variance
increases. The directional `current_over_reference` ratio must still be
returned separately as `VARIANCE_RATIO`.

Recommended SciPy mapping:

```python
from scipy.stats import f

f.cdf(f_statistic, df_num, df_den)
f.sf(f_statistic, df_num, df_den)
```

Dependency policy:

- Prefer `scipy.stats.f` when SciPy is available, matching the existing batch
  method dependency policy.
- A local F distribution implementation is acceptable only if a project-local
  statistics helper already exists or is added with tests during implementation.
- Do not approximate the p-value with a normal, chi-square, bootstrap, or
  permutation method under the `F_TEST_EQUAL_VARIANCE` name unless this design
  is updated first.

## 7. Output Measurements

`drift_method_variant_measurement_summary.csv` maps all DM-020 variants to:

```text
TEST_STATISTIC
P_VALUE
DRIFT_ALARM_STATE
```

Return these canonical measurements for every successful supported run:

```python
{
    "TEST_STATISTIC": <float F statistic>,
    "P_VALUE": <float in [0, 1]>,
    "DRIFT_ALARM_STATE": <"drift_detected" | "normal" | "undetermined">,
    "SAMPLE_SIZE": {
        "reference": <effective_reference_n>,
        "current": <effective_current_n>,
        "dropped_reference": <dropped_reference_n>,
        "dropped_current": <dropped_current_n>,
    },
    "SAMPLE_SIZE_REFERENCE": <effective_reference_n>,
    "SAMPLE_SIZE_CURRENT": <effective_current_n>,
    "WINDOW_SIZE": {
        "reference": <effective_reference_n>,
        "current": <effective_current_n>,
    },
    "VARIANCE_REFERENCE": <float>,
    "VARIANCE_CURRENT": <float>,
    "VARIANCE_RATIO": <current variance / reference variance>,
    "VARIANCE_RATIO_ABS": <larger variance / smaller variance>,
    "DEGREES_OF_FREEDOM": {
        "reference": <effective_reference_n - 1>,
        "current": <effective_current_n - 1>,
        "numerator": <df used in TEST_STATISTIC p-value calculation>,
        "denominator": <df used in TEST_STATISTIC p-value calculation>,
    },
    "REFERENCE_MEAN": <float>,
    "CURRENT_MEAN": <float>,
    "REFERENCE_STD": <float>,
    "CURRENT_STD": <float>,
}
```

Top-level `DriftResult` field mapping:

```text
method_id = "DM-020"
method_name = "F-test / Variance Test 계열"
method_category = "BatchDistributionComparison"
variant_id = "F_TEST_EQUAL_VARIANCE"
drift_score = TEST_STATISTIC
p_value = P_VALUE
test_statistic = TEST_STATISTIC
threshold = alpha
drift_detected = p_value < alpha when applicable
```

The variance, standard deviation, and mean summaries are interpretation
helpers. They must not replace the documented p-value alarm rule.

Interpretation text should state:

- which variant ran
- reference/current effective sample sizes
- reference and current sample variances
- reported variance ratio and alternative
- F statistic, degrees of freedom, p-value, and alpha
- whether the result crossed the drift rule
- that the result is a numeric variance/scale drift candidate, not proof of
  root cause, model performance degradation, or supervised concept drift
- that the classical F-test is sensitive to non-normality and outliers

## 8. Algorithm Steps

1. Normalize `params` to an empty dict when omitted.
2. Resolve `variant_id`; default to `F_TEST_EQUAL_VARIANCE`.
3. Reject deferred or unknown variants with `severity="not_applicable"` and a
   warning naming the unsupported variant.
4. Resolve `alpha` and alpha aliases; require no conflicts and `0 < alpha < 1`.
5. Resolve `alternative`, `variance_ratio_definition`, `p_value_method`,
   `nan_policy`, `normality_warning_policy`, `zero_variance_policy`,
   `multiple_testing_correction`, sample-size minima, warning thresholds, and
   the value column.
6. Validate that both reference and current windows are supplied and parseable.
7. Validate required columns and scalar numeric value data. Boolean data is not
   valid numeric F-test input.
8. Convert and sort the DataFrame according to the common window handling
   contract.
9. Slice inclusive reference and current windows.
10. Drop rows with invalid timestamps or non-finite values; record original and
    effective counts.
11. If either effective sample is empty or below minimum, return not
    applicable.
12. Convert the two effective samples to one-dimensional
    `numpy.ndarray[float64]` objects.
13. Compute unbiased sample variances with `ddof=1` and degrees of freedom
    `n - 1`.
14. If either variance is zero, negative, or non-finite, return not applicable
    because the variance-ratio F-test p-value is undefined or degenerate.
15. Add warnings for F-test normality sensitivity, outlier sensitivity, low
    sample size, highly imbalanced sample sizes, autocorrelation concerns, and
    multiple-testing metadata when applicable.
16. Compute `VARIANCE_RATIO`, `VARIANCE_RATIO_ABS`, `TEST_STATISTIC`, numerator
    and denominator degrees of freedom, and p-value according to section 6.
17. Convert statistic and p-value to Python floats; guard against NaN/inf and
    p-values outside `[0, 1]`.
18. Compute descriptive summaries: effective sample counts, means, variances,
    and standard deviations.
19. Apply the drift decision rule from section 9.
20. Build `DriftResult` with method identity, variant, canonical measurements,
    helper summaries, counts, windows, parameters, warnings, and concise
    interpretation text.

## 9. Drift Decision Rule

Null hypothesis for `F_TEST_EQUAL_VARIANCE`:

```text
reference and current numeric samples have equal population variance.
```

Alternative hypotheses:

```text
two-sided: current and reference variances differ.
current_greater: current variance is greater than reference variance.
current_less: current variance is less than reference variance.
```

Primary rule:

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

Use strict `< alpha`, not `<= alpha`. Equality is not drift.

For report wording:

- `drift_detected=True`: "numeric variance/scale drift candidate"
- `drift_detected=False`: "no statistically significant variance change under
  this window, alternative, and alpha"
- `drift_detected=None`: method was not applicable or calculation failed

The F statistic is method-specific. A larger two-sided statistic means a larger
variance ratio, but it must not be compared directly with t-test, Levene,
Anderson-Darling, BWS, KS, or model-comparison F statistics without method and
variant context.

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
- unsupported or deferred `variant_id`
- invalid `alpha` or conflicting alpha aliases
- unsupported `alternative`, `variance_ratio_definition`, `p_value_method`,
  `nan_policy`, `normality_warning_policy`, `zero_variance_policy`,
  `min_reference_size`, `min_current_size`, `low_power_sample_size`, or
  `sample_imbalance_warning_ratio`
- zero, negative, or non-finite reference/current sample variance
- non-finite statistic, non-finite p-value, or p-value outside `[0, 1]`
- current/reference window overlap when overlap policy is not explicitly
  defined by the implementation
- `ANOVA_F_TEST_GROUP_MEAN` until the multi-group sample contract is approved
- `MODEL_COMPARISON_F_TEST` until nested-model or residual-summary inputs are
  approved

Return `severity="normal"` or `severity="drift_detected"` with warnings when the
method can still run but interpretation needs caution:

- timestamps or values were dropped because they were invalid or non-finite
- either effective sample size is below `low_power_sample_size`
- reference/current sample sizes are highly imbalanced
- repeated, rounded, or tied values suggest the signal may be discrete
- observations are repeated or autocorrelated time-series rows rather than
  independent samples
- strong outliers may dominate the variance ratio
- the F-test p-value assumes approximate normality of the underlying samples
- sample extraction, traffic mix, seasonality, or segment definitions differ
  between windows
- `multiple_testing_correction` is not `"none"`; record that this detector does
  not apply correction internally

Unexpected backend exceptions should return `severity="error"` or `"watch"`
according to project convention, with `drift_detected=None` and a clear warning,
without raising through the public detector boundary.

Do not silently coerce categorical values, boolean flags, labels, embeddings,
lists, or objects into the numeric F-test detector.

## 11. Implementation Target

```text
module: drift_algorithm.methods.batchdistributioncomparison
function: detect_f_test_variance_test
```

The module should expose `detect_f_test_variance_test` through the same package
path used by the other batch distribution methods. If the concrete package
later separates one method per file, keep this public import path stable or add
a compatibility import.

Expected dependencies:

```text
pandas
numpy
scipy.stats.f
```

Expected result object:

```text
DriftResult from drift_algorithm/docs/input_output_contracts.md equivalent code
contract
```

Helper functions should follow existing patterns in
`drift_algorithm.methods.batchdistributioncomparison`:

- use the common `DriftResult` dataclass
- use `not_applicable_result` or a method-specific not-applicable helper for
  validation failures
- use `prepare_numeric_windows` where it matches this contract
- keep method-specific F-test helpers private to the module unless another
  numeric batch method later shares them
- record backend name, alternative, p-value method, statistic definition,
  variance-ratio definition, `alpha`, value column, effective windows,
  sample-size metadata, degrees of freedom, and unsupported/deferred variant
  decisions so the result is auditable

Suggested private helper shape:

```python
def _f_test_equal_variance_statistic(
    reference_values: np.ndarray,
    current_values: np.ndarray,
    *,
    alternative: str,
) -> dict[str, float | int | str]:
    """Return variances, ratio, statistic, dfs, and statistic definition."""

def _f_distribution_p_value(
    f_statistic: float,
    *,
    df_num: int,
    df_den: int,
    alternative: str,
    directional_ratio: float,
) -> float:
    ...
```

## 12. Verification Plan

Unit tests for the first implementation:

1. Default no-drift two-sided case:
   - Generate reference/current numeric samples from the same normal
     distribution with a deterministic seed.
   - Omit `variant_id` and assert `variant_id == "F_TEST_EQUAL_VARIANCE"`.
   - Assert `TEST_STATISTIC`, `P_VALUE`, `DRIFT_ALARM_STATE`, `SAMPLE_SIZE`,
     `SAMPLE_SIZE_REFERENCE`, `SAMPLE_SIZE_CURRENT`, `VARIANCE_REFERENCE`,
     `VARIANCE_CURRENT`, `VARIANCE_RATIO`, and `DEGREES_OF_FREEDOM` exist.
   - Assert `drift_detected is False` and `severity == "normal"` for a seed
     chosen to keep `p_value >= 0.05`.
2. Variance-increase drift candidate:
   - Generate reference normal samples with standard deviation 1 and current
     samples with standard deviation 2 or larger.
   - Use `alternative="current_greater"` or default `two-sided`.
   - Assert `VARIANCE_RATIO > 1`, `p_value < alpha`,
     `drift_detected is True`, and `severity == "drift_detected"`.
3. Variance-decrease one-sided case:
   - Generate reference samples with larger variance than current samples.
   - Use `alternative="current_less"`.
   - Assert `VARIANCE_RATIO < 1`, p-value follows the lower-tail F CDF, and
     canonical measurements are populated.
4. Two-sided p-value symmetry:
   - Swap reference/current samples and assert the two-sided p-value is the
     same within floating tolerance.
   - Assert `VARIANCE_RATIO` inverts while `VARIANCE_RATIO_ABS` and
     `TEST_STATISTIC` remain stable.
5. Parameter alias and validation:
   - Assert `threshold_or_alpha` and `significance_level` route to `alpha`.
   - Assert conflicting alpha aliases return `severity="not_applicable"`.
   - Assert unsupported `alternative`, `variance_ratio_definition`,
     `p_value_method`, `nan_policy`, and malformed sample-size settings return
     not applicable.
6. Schema and window validation:
   - Missing value column.
   - Non-numeric, boolean, object/list, or categorical value column.
   - Missing reference/current windows.
   - Empty current/reference slices.
   - Effective sample size below minimum.
   - Overlapping windows if no overlap policy is implemented.
7. Degenerate variance cases:
   - Reference zero variance.
   - Current zero variance.
   - Both windows constant.
   - Assert not applicable, `drift_detected is None`, and warning names the
     zero-variance cause.
8. Deferred variants:
   - `ANOVA_F_TEST_GROUP_MEAN` returns `severity="not_applicable"` with a
     warning about the missing multi-group contract.
   - `MODEL_COMPARISON_F_TEST` returns `severity="not_applicable"` with a
     warning about the missing nested-model or residual-summary contract.
9. Warning behavior:
   - NaN, infinity, and invalid timestamps are dropped with warnings and
     effective counts.
   - Low sample size above the hard minimum produces a low-power warning.
   - Highly imbalanced sample sizes produce warning metadata.
   - Tied or repeated values produce a discreteness caution.
   - `multiple_testing_correction != "none"` is recorded but not applied.
10. Backend failure:
    - Simulate missing/failed `scipy.stats.f`.
    - Assert the public detector returns `severity="error"` or `"watch"` with
      `drift_detected=None` and a clear warning unless an approved local F
      distribution helper is available.

Recommended commands after implementation:

```text
python -m py_compile drift_algorithm\methods\batchdistributioncomparison.py
python -m pytest tests\test_f_test_variance_test.py
python -m pytest tests\test_t_test.py tests\test_levene_s_test.py
```

Manual review before marking implementation complete:

- Confirm public function signature matches the common contract.
- Confirm canonical measurement names match
  `drift_method_variant_measurement_summary.csv`.
- Confirm `ANOVA_F_TEST_GROUP_MEAN` and `MODEL_COMPARISON_F_TEST` fail
  explicitly instead of falling through to the equal-variance calculation.
- Confirm one-sided alternatives use the documented current/reference variance
  ratio direction.
- Confirm the two-sided p-value is symmetric under swapping reference/current.
- Confirm interpretation text avoids root-cause, performance-degradation, and
  supervised concept-drift claims without labeled evidence.
- Confirm `git diff` only changes
  `drift_algorithm/docs/method_designs/DM-020_f_test_variance_test.md`.

## 13. Manager Review Points

- First implementation scope is intentionally limited to univariate numeric
  reference/current `(time, value)` windows and `F_TEST_EQUAL_VARIANCE`.
- `ANOVA_F_TEST_GROUP_MEAN` is implementation-ready in concept but deferred
  until a multi-group input contract is approved.
- `MODEL_COMPARISON_F_TEST` is deferred until nested-model or residual-summary
  inputs, degrees-of-freedom rules, and validation fixtures are approved.
- Prefer `scipy.stats.f` for F CDF/SF; use a local F distribution only if a
  reviewed project helper exists or is added with tests.
- Report `VARIANCE_RATIO` as `current_variance / reference_variance`; use
  strict `p_value < alpha` for drift decisions.
- The public target is `detect_f_test_variance_test` in
  `drift_algorithm.methods.batchdistributioncomparison`.
