# DM-019 t-test 계열 Design

## 1. Method Identity

- Method ID: `DM-019`
- Method name: `t-test 계열`
- Category: `BatchDistributionComparison`
- Method kind: `detector`
- Status: `확정`
- Source catalog: `drift_methods_catalog.md`
- Source variant document: `algorithm_variants/t_test_algorithm_variants.md`

## 2. Purpose

This method detects mean drift in a numeric monitoring signal. It answers the
question: did the current window's mean move away from a fixed baseline,
reference-window mean, independent reference sample, or paired before/after
sample?

Primary input from the catalog: numeric metric mean.
Primary output from the catalog: t statistic, p-value.

Report interpretation must describe this as a numeric mean-shift candidate, not
as confirmed root cause, performance degradation, or supervised concept drift.
Because t-tests focus on means, they must not be used as the only evidence for
distribution-shape, tail, variance, categorical, embedding, or label-dependent
drift.

## 3. Supported Variants

First implementation variants:

- `ONE_SAMPLE_T_TEST`
  - Tests whether the current-window mean differs from `baseline_mean`.
  - If `baseline_mean` is absent and `reference_window` is supplied, the first
    implementation may use the reference-window mean as the baseline and must
    add a warning that reference uncertainty is not modeled by a one-sample
    test.
  - Use when there is a fixed operational target, SLA baseline, historical
    stable mean, or explicitly accepted reference mean.
- `TWO_SAMPLE_STUDENT_T_TEST`
  - Tests independent reference and current samples under equal-variance
    assumption.
  - Default for independent two-window comparison only when
    `params["equal_var"] is True` or the caller explicitly selects this variant.
  - Use when sample sizes and variances are similar enough that pooled variance
    is an acceptable assumption.
- `WELCH_T_TEST`
  - Tests independent reference and current samples without equal-variance
    assumption.
  - Default variant for independent two-window comparison.
  - Use when sample sizes or variances may differ; this is the safer default for
    drift monitoring.
- `PAIRED_T_TEST`
  - Tests whether matched reference/current differences have non-zero mean.
  - Requires `params["pair_col"]` so rows can be aligned by the same entity,
    query, item, request, or other stable pairing key.
  - Use only when the same unit is measured in both windows. Do not use for
    independent samples.

Unsupported in the first implementation:

- multivariate samples or automatic multi-feature scanning
- categorical/count/probability-vector/embedding/text/label inputs
- robust trimmed t-test, permutation t-test, Bayesian t-test, or repeated
  measures beyond one reference value and one current value per pair
- automatic normality testing as a gate; normality concerns are warnings and
  interpretation caveats, not separate detectors in this method

## 4. Input Schema

Use the common `pandas.DataFrame` input boundary from
`../input_output_contracts.md`.

Required default numeric schema:

```text
pd.DataFrame columns:
  time: datetime64[ns] or datetime-coercible timestamp
  value: numeric scalar, non-boolean
```

Optional paired schema extension for `PAIRED_T_TEST`:

```text
pd.DataFrame columns:
  time: datetime64[ns] or datetime-coercible timestamp
  value: numeric scalar, non-boolean
  <pair_col>: stable scalar key present in both reference/current windows
```

Function arguments follow `../input_output_contracts.md`:

```python
def detect_t_test(
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

Validation rules:

- `time_col` must exist and be convertible with `pd.to_datetime`.
- `value_col` must exist, be scalar numeric, and not be boolean.
- `current_window` is required for all variants.
- `reference_window` is required for `TWO_SAMPLE_STUDENT_T_TEST`,
  `WELCH_T_TEST`, and `PAIRED_T_TEST`.
- `ONE_SAMPLE_T_TEST` requires either `params["baseline_mean"]` or
  `reference_window`.
- Sort by `time_col` before slicing.
- Slice inclusive timestamp windows and then drop missing or non-finite values.
- Convert effective values to one-dimensional `numpy.ndarray[float64]`.
- Preserve original/effective sample sizes, dropped counts, means, variances,
  and selected window bounds in `metadata` and `measurements`.
- For `PAIRED_T_TEST`, align reference/current rows by `pair_col`, require one
  effective reference and one effective current value per retained key, and run
  the test on aligned arrays in deterministic key order.
- Return `severity="not_applicable"` with `drift_detected=None` if the supplied
  schema cannot represent the required numeric mean-comparison input.

## 5. Parameters

Method-specific parameters come from `drift_method_parameter_guide.md`,
`drift_method_variant_parameters.csv`, and the variant source document.

Required/optional params for the first implementation:

| Param | Type | Default | Applies to | Meaning |
|---|---:|---:|---|---|
| `variant_id` | string | `WELCH_T_TEST` | all | One of the supported variant IDs. |
| `alpha` | float | `0.05` | all | Significance level for the p-value drift rule. Alias `threshold_or_alpha` may be accepted, but `alpha` is canonical in implementation code. |
| `alternative` | string | `two-sided` | all | `two-sided`, `greater`, or `less` as accepted by SciPy. With reference/current orientation, `greater` means the first tested sample or difference has a greater mean under the backend definition. |
| `direction_or_alternative` | string | `None` | all | User-facing alias. Supports `current_increase`, `current_decrease`, `increase`, `decrease`, `up`, `down`, or backend alternatives `greater`/`less`. |
| `baseline_mean` | float | `None` | one-sample | Fixed mean used as `popmean`. If absent, reference mean may be used with warning. |
| `allow_reference_mean_as_baseline` | bool | `True` | one-sample | Allows current sample to be tested against reference-window mean when `baseline_mean` is absent. |
| `equal_var` | bool | variant-derived | Student/Welch | `True` for Student two-sample, `False` for Welch. Caller value must not contradict selected variant. |
| `paired` | bool | variant-derived | all | `True` only for `PAIRED_T_TEST`; caller value must not contradict selected variant. |
| `pair_col` | string | `None` | paired | Column used to match reference/current observations. Required for paired variant. |
| `nan_policy` | string | `omit` | all | `omit`, `propagate`, or `raise`. First implementation should support `omit`; `propagate`/`raise` may return `not_applicable` if not implemented. |
| `confidence_level` | float | `0.95` | all | Optional confidence interval level recorded in metadata when a mean-difference CI is computed. Must be between 0 and 1. |
| `multiple_testing_correction` | string | `none` | all | Metadata only for single-call implementation. Supported value is `none`; other values return `not_applicable` unless implemented by a higher-level multi-feature runner. |
| `min_reference_size` | int | `2` | two-sample/paired/reference-baseline one-sample | Minimum effective reference sample size. |
| `min_current_size` | int | `2` | all | Minimum effective current sample size. |
| `variance_ratio_warning_threshold` | float | `4.0` | Student/Welch | Warn when larger sample variance divided by smaller sample variance exceeds this value. |
| `sample_imbalance_warning_ratio` | float | `10.0` | two-sample | Warn when max sample size divided by min sample size exceeds this value. |

Variant default resolution:

- `ONE_SAMPLE_T_TEST`: `paired=False`; `equal_var` ignored; use
  `baseline_mean` as `popmean` or reference effective mean as fallback baseline.
- `TWO_SAMPLE_STUDENT_T_TEST`: `paired=False`; force `equal_var=True`; backend
  samples are `a=reference_values`, `b=current_values`.
- `WELCH_T_TEST`: `paired=False`; force `equal_var=False`; backend samples are
  `a=reference_values`, `b=current_values`.
- `PAIRED_T_TEST`: `paired=True`; `equal_var` ignored; backend arrays are
  aligned `reference_values` and `current_values` by `pair_col`.

Direction alias normalization:

- `current_increase`, `increase`, or `up` means current mean is expected to be
  greater than reference/baseline.
- `current_decrease`, `decrease`, or `down` means current mean is expected to be
  less than reference/baseline.
- For `ONE_SAMPLE_T_TEST`, normalize current increase to backend
  `alternative="greater"` and current decrease to `alternative="less"` because
  the tested sample is current.
- For independent two-sample tests, the backend is called as
  `a=reference, b=current`; normalize current increase to backend
  `alternative="less"` and current decrease to backend
  `alternative="greater"`.
- For paired tests using `scipy.stats.ttest_rel(a=reference, b=current)`,
  normalize current increase to backend `alternative="less"` and current
  decrease to backend `alternative="greater"` because the backend evaluates
  `mean(a - b)`.

Reject or warn on params unrelated to this method, such as `feature_cols`,
`category_col`, `count_col`, `embedding_cols`, label columns, covariance
settings, binning settings, projection settings, or classifier settings.

## 6. Output Measurements

Return canonical measurements in `DriftResult.measurements`:

- `DRIFT_ALARM_STATE`
- `P_VALUE`
- `TEST_STATISTIC`
- `SAMPLE_SIZE`

Measurement payload:

```python
{
    "TEST_STATISTIC": <float t statistic>,
    "P_VALUE": <float in [0, 1]>,
    "DRIFT_ALARM_STATE": <bool>,
    "SAMPLE_SIZE": {
        "reference": <effective_reference_n or None>,
        "current": <effective_current_n>,
        "paired": <effective_pair_count or None>,
        "dropped_reference": <dropped_reference_n>,
        "dropped_current": <dropped_current_n>,
        "dropped_unpaired": <dropped_unpaired_n or None>,
    },
    "REFERENCE_MEAN": <float or None>,
    "CURRENT_MEAN": <float>,
    "MEAN_DIFFERENCE": <current_mean - reference_or_baseline_mean>,
    "REFERENCE_VARIANCE": <float or None>,
    "CURRENT_VARIANCE": <float>,
    "BASELINE_MEAN": <float or None>,
    "CONFIDENCE_INTERVAL": {
        "level": <confidence_level>,
        "low": <float>,
        "high": <float>,
    } | None,
}
```

Top-level `DriftResult` fields:

- `method_id="DM-019"`
- `method_name="t-test 계열"`
- `method_category="BatchDistributionComparison"`
- `variant_id=<resolved variant>`
- `test_statistic=<t statistic>`
- `p_value=<p-value>`
- `drift_score=<abs(mean difference)>`
- `threshold=<alpha>`
- `drift_detected=<p_value < alpha>` when applicable

`REFERENCE_MEAN`, `CURRENT_MEAN`, `MEAN_DIFFERENCE`, variance fields, and
confidence interval are helper measurements for interpretation. They are not
catalog canonical measurements and must not replace the canonical alarm rule.

## 7. Algorithm Steps

1. Merge `params` with defaults and resolve `variant_id`.
2. Validate `variant_id`; unsupported variants return `not_applicable`.
3. Resolve `alpha` from `params["alpha"]` or `params["threshold_or_alpha"]`;
   require `0 < alpha < 1`.
4. Resolve `alternative` from variant defaults, `alternative`, or
   `direction_or_alternative`; validate against `two-sided`, `greater`, `less`.
5. Validate `confidence_level`, `multiple_testing_correction`, `nan_policy`,
   `equal_var`, and `paired` consistency with the selected variant.
6. Validate `time_col`, `value_col`, and required windows.
7. Convert `time_col` to datetime, sort by time, and slice inclusive windows.
8. Coerce `value_col` to numeric for the sliced rows and apply `nan_policy`.
   The first implementation should drop missing/non-finite values for
   `nan_policy="omit"` and record dropped counts.
9. For `ONE_SAMPLE_T_TEST`:
   - build current effective array
   - resolve `baseline_mean` from params or reference effective mean
   - enforce `min_current_size`
   - if using reference mean as baseline, enforce `min_reference_size` and add
     a warning about one-sample baseline uncertainty
   - call `scipy.stats.ttest_1samp(current_values, popmean=baseline_mean,
     alternative=<resolved>)`
10. For `TWO_SAMPLE_STUDENT_T_TEST`:
    - build reference/current effective arrays
    - enforce `min_reference_size` and `min_current_size`
    - call `scipy.stats.ttest_ind(reference_values, current_values,
      equal_var=True, alternative=<resolved>)`
11. For `WELCH_T_TEST`:
    - build reference/current effective arrays
    - enforce `min_reference_size` and `min_current_size`
    - call `scipy.stats.ttest_ind(reference_values, current_values,
      equal_var=False, alternative=<resolved>)`
12. For `PAIRED_T_TEST`:
    - require `pair_col`
    - validate `pair_col` exists and is non-null after slicing
    - reduce to one reference and one current value per pair; duplicate pair
      keys return `not_applicable` unless a future `pair_aggregation` policy is
      implemented
    - align arrays by sorted pair key
    - enforce `min_reference_size`, `min_current_size`, and at least two
      retained pairs
    - call `scipy.stats.ttest_rel(reference_values, current_values,
      alternative=<resolved>)`
13. Convert backend statistic and p-value to finite floats. Non-finite statistic
    or p-value returns `not_applicable` unless the all-values-identical case
    produces a documented non-significant result from the backend.
14. Compute sample summaries: effective counts, means, sample variances,
    `MEAN_DIFFERENCE`, and optional confidence interval if straightforward for
    the selected variant.
15. Add caution warnings when assumptions are fragile:
    - Student test variance ratio exceeds `variance_ratio_warning_threshold`
    - independent sample sizes are highly imbalanced
    - very small samples pass the minimum but have weak power
    - outliers or heavy tails cannot be ruled out from this method alone
    - one-sample fallback baseline used reference mean
16. Set `drift_detected = p_value < alpha`.
17. Set severity:
    - `drift_detected` when `drift_detected is True`
    - `normal` when `drift_detected is False`
    - `not_applicable` for validation/precondition failures
    - `error` only for unexpected calculation failures
18. Build interpretation text:
    - include variant, alternative direction, t statistic, p-value, alpha,
      current/reference or baseline means, mean difference, and effective
      sample sizes
    - describe the result as a mean-shift drift candidate when the rule fires
    - avoid distribution-wide, variance-only, root-cause, or performance claims
      without additional evidence
19. Return `DriftResult` with canonical measurement keys, warnings, and
    metadata.

## 8. Drift Decision Rule

The null hypothesis depends on variant:

- `ONE_SAMPLE_T_TEST`: current mean equals `baseline_mean`.
- `TWO_SAMPLE_STUDENT_T_TEST`: reference and current means are equal, assuming
  equal variances.
- `WELCH_T_TEST`: reference and current means are equal, not assuming equal
  variances.
- `PAIRED_T_TEST`: mean paired difference is zero.

The alternative is determined by `alternative` after direction normalization:

- `two-sided`: mean differs in either direction.
- current increase aliases: current mean is greater than reference/baseline.
- current decrease aliases: current mean is less than reference/baseline.

Implementation rule:

```python
drift_detected = p_value < alpha
```

Default `alpha` is `0.05`. Equality is not drift: `p_value == alpha` returns
`False`.

For report wording:

- `drift_detected=True`: "numeric mean drift candidate"
- `drift_detected=False`: "no statistically significant mean shift under this
  window, variant, and alpha"
- `drift_detected=None`: method was not applicable or calculation failed

The decision rule is based on p-value only. Mean difference and confidence
interval qualify effect size and direction, but must not override the alarm
state in the first implementation.

## 9. Warnings and Not-Applicable Conditions

Return `severity="not_applicable"` and `drift_detected=None` for:

- missing `time_col` or `value_col`
- non-datetime-coercible `time_col`
- non-numeric or boolean `value_col`
- missing `current_window`
- missing `reference_window` for independent or paired variants
- one-sample variant without `baseline_mean` and without permitted reference
  mean fallback
- empty reference or current window after slicing when required
- no finite numeric values after invalid rows are handled
- effective sample size below `min_reference_size` or `min_current_size`
- unsupported `variant_id`
- invalid `alpha`, `alternative`, `confidence_level`, `nan_policy`,
  `multiple_testing_correction`, `equal_var`, or `paired` setting
- `PAIRED_T_TEST` without `pair_col`
- `pair_col` missing from the DataFrame
- duplicate pair keys in either window when no pair aggregation policy exists
- fewer than two retained pairs for paired test
- no overlapping pair keys between reference and current windows
- all retained paired differences are non-finite
- backend returns non-finite p-value or statistic outside a documented
  non-significant degenerate case

Return `severity="normal"` or `severity="drift_detected"` with warnings when the
method can still run but interpretation needs caution:

- invalid rows were dropped from either window
- one-sample variant used reference mean as a fixed baseline
- Student test selected despite large reference/current variance ratio
- sample sizes are highly imbalanced
- sample size is small, so power and normality approximation may be weak
- repeated or autocorrelated time-series observations may violate independence
- outliers or heavy tails may dominate the mean and t statistic
- multiple features were tested outside this function without correction
- `P_VALUE` and `TEST_STATISTIC` are not comparable to other method families
  without method and variant context

Unexpected backend exceptions should return `severity="error"` with the
exception class/message in warnings or metadata, without raising through the
public detector boundary.

## 10. Implementation Target

```text
module: drift_algorithm.methods.batchdistributioncomparison
function: detect_t_test
```

Expected dependencies:

- `pandas` for input normalization and window slicing
- `numpy` for finite numeric arrays, summaries, and pair alignment helpers
- `scipy.stats.ttest_1samp`, `scipy.stats.ttest_ind`, and
  `scipy.stats.ttest_rel` for t statistic and p-value calculation

Helper functions should follow existing batch method patterns in
`drift_algorithm.methods.batchdistributioncomparison`:

- use the common `DriftResult` dataclass
- use `not_applicable_result` for validation failures when possible
- keep method-specific helpers private to the module unless shared by an
  already implemented method
- record backend orientation and normalized alternative in `metadata` so
  one-sided interpretation is auditable

## 11. Verification Plan

Create focused tests when implementation starts:

1. Welch no-drift default:
   - reference/current generated from the same numeric distribution
   - omit `variant_id` and assert default `variant_id="WELCH_T_TEST"`
   - assert `P_VALUE`, `TEST_STATISTIC`, `DRIFT_ALARM_STATE=False`,
     `drift_detected=False`, and sample-size metadata.
2. Welch drift candidate:
   - current mean shifted enough to produce `p_value < 0.05`
   - assert `severity="drift_detected"`, canonical measurements, means, and
     mean difference.
3. Student variant:
   - explicitly select `TWO_SAMPLE_STUDENT_T_TEST`
   - assert backend metadata records `equal_var=True`
   - use high variance-ratio data and assert the documented warning appears.
4. One-sample variant:
   - call with fixed `baseline_mean` and shifted current values
   - assert p-value rule, `BASELINE_MEAN`, `CURRENT_MEAN`, and
     `MEAN_DIFFERENCE`
   - call without `baseline_mean` but with `reference_window` and assert the
     reference-baseline warning appears.
5. Paired variant:
   - provide `pair_col` with matching keys and before/after values
   - assert paired sample count, deterministic alignment metadata, and expected
     p-value direction
   - duplicate pair keys or no overlapping keys return `not_applicable`.
6. One-sided direction:
   - current increase alias maps to the correct backend alternative for
     one-sample, Welch/Student, and paired variants
   - opposite direction is not significant for the same shifted data.
7. Validation:
   - missing value column
   - non-numeric value column
   - missing windows
   - empty current/reference slices
   - sample size below minimum
   - unsupported variant
   - invalid alpha and alternative.
8. Warning behavior:
   - NaN/non-finite values are dropped with warnings and effective counts
   - imbalanced sample sizes produce caution metadata
   - unrelated params such as `category_col` or `embedding_cols` are rejected or
     warned according to the implementation policy.

The test must assert canonical measurement keys, warning behavior, and the
documented `drift_detected` rule.

Recommended commands after implementation:

```text
python -m py_compile drift_algorithm\methods\batchdistributioncomparison.py
python -m pytest tests\test_t_test.py
python -m pytest tests\test_mann_whitney_u_wilcoxon_rank_sum_test.py tests\test_ks_test.py
```
