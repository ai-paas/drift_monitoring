# DM-021 Levene's Test Design

## 1. Method Identity

- Method ID: `DM-021`
- Method name: `Levene's Test`
- Category: `BatchDistributionComparison`
- Method kind: `detector`
- Status: `확정`
- Source catalog: `drift_methods_catalog.md`
- Source variant document: `algorithm_variants/levene_s_test_algorithm_variants.md`

## 2. Purpose

This method detects variance or scale drift in a single numeric monitoring
signal by comparing the dispersion of reference and current windows. It answers
the question: did the current window's variability change enough to reject the
null hypothesis that reference and current have equal variance?

Primary input from the catalog: numeric sample variance.
Primary output from the catalog: Levene statistic, p-value.

Report interpretation must describe the result as a numeric variance/scale
drift candidate. It must not claim root cause, model performance degradation,
or supervised concept drift without additional labeled evidence. Levene's Test
does not directly test mean shift, full distribution shape, category mix,
embedding drift, or label-dependent performance drift.

## 3. Supported Variants

First implementation variants:

- `LEVENE_MEAN_CENTER`
  - Uses the mean as the group center.
  - Maps to SciPy `scipy.stats.levene(..., center="mean")`.
  - Use when outliers are not expected to dominate and mean-centered
    variability is the operational target.
- `BROWN_FORSYTHE_MEDIAN_CENTER`
  - Uses the median as the group center.
  - Maps to SciPy `scipy.stats.levene(..., center="median")`.
  - Default variant for independent two-window monitoring because it is more
    robust to outliers and heavy-tailed numeric signals.
- `TRIMMED_MEAN_LEVENE`
  - Uses a trimmed mean as the group center.
  - Maps to SciPy `scipy.stats.levene(..., center="trimmed",
    proportiontocut=<value>)`.
  - Use when some extreme values should be downweighted but median-centered
    testing is considered too conservative.

Unsupported in the first implementation:

- one-sample variance comparison against a fixed variance
- more than two groups or automatic multi-segment scanning
- paired/repeated-measure variance tests
- multivariate covariance equality tests
- categorical/count/probability-vector/embedding/text/label inputs
- permutation/bootstrap p-values or multiple-testing correction inside this
  detector

## 4. Input Schema

Use the common `pandas.DataFrame` input boundary from
`../input_output_contracts.md`.

Required default numeric schema:

```text
pd.DataFrame columns:
  time: datetime64[ns] or datetime-coercible timestamp
  value: numeric scalar, non-boolean
```

Function arguments follow `../input_output_contracts.md`:

```python
def detect_levene_s_test(
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
- `reference_window` and `current_window` are both required.
- Sort by `time_col` before slicing.
- Slice inclusive timestamp windows.
- Within each sliced window, coerce `value_col` to numeric and drop missing,
  NaN, positive infinity, and negative infinity values.
- Convert effective values to one-dimensional `numpy.ndarray[float64]`.
- Preserve original/effective sample sizes, dropped counts, selected window
  bounds, and reference/current variance summaries in `metadata` and
  `measurements`.
- Return `severity="not_applicable"` with `drift_detected=None` if the supplied
  schema cannot represent a numeric two-window variance comparison.

## 5. Parameters

Method-specific parameters come from `drift_method_parameter_guide.md`,
`drift_method_variant_parameters.csv`, and the variant source document.

Required/optional params for the first implementation:

| Param | Type | Default | Applies to | Meaning |
|---|---:|---:|---|---|
| `variant_id` | string | `BROWN_FORSYTHE_MEDIAN_CENTER` | all | One of the supported variant IDs. |
| `alpha` | float | `0.05` | all | Significance level for the p-value drift rule. Alias `threshold_or_alpha` may be accepted, but `alpha` is canonical in implementation code. |
| `center` | string | variant-derived | all | Backend center policy: `mean`, `median`, or `trimmed`. Caller value must not contradict the selected variant. |
| `proportiontocut` | float | `0.05` | trimmed only | Fraction cut from each tail for `TRIMMED_MEAN_LEVENE`. Must satisfy `0 <= proportiontocut < 0.5`. Ignored for mean/median variants unless supplied inconsistently. |
| `alternative` | string | `two-sided` | all | Catalog parameter retained for API consistency. First implementation supports only `two-sided`; `greater`, `less`, `up`, or `down` return `not_applicable` unless a future backend adds one-sided support. |
| `input_signal` | string | `value` | all | Metadata label for the monitored numeric signal. Does not change `value_col`; callers should use the function argument for column selection. |
| `min_reference_size` | int | `3` | all | Minimum effective reference sample size after invalid rows are dropped. |
| `min_current_size` | int | `3` | all | Minimum effective current sample size after invalid rows are dropped. |
| `variance_ratio_warning_threshold` | float | `4.0` | all | Adds a caution warning when larger sample variance divided by smaller positive sample variance exceeds this value. |
| `small_sample_warning_threshold` | int | `10` | all | Adds a low-power warning when either effective window has fewer than this many values but still passes the hard minimum. |
| `nan_policy` | string | `omit` | all | First implementation supports `omit`. `propagate` or `raise` may return `not_applicable` if not implemented. |

Variant default resolution:

- `LEVENE_MEAN_CENTER`: force `center="mean"` and ignore
  `proportiontocut`.
- `BROWN_FORSYTHE_MEDIAN_CENTER`: force `center="median"` and ignore
  `proportiontocut`.
- `TRIMMED_MEAN_LEVENE`: force `center="trimmed"` and pass
  `proportiontocut` to the backend. Default `proportiontocut=0.05`.

Reject or warn on params unrelated to this method, such as `feature_cols`,
`category_col`, `count_col`, `embedding_cols`, label columns, covariance
settings, binning settings, projection settings, classifier settings, or
paired-sample settings.

## 6. Output Measurements

Return canonical measurements in `DriftResult.measurements`:

- `DRIFT_ALARM_STATE`
- `P_VALUE`
- `TEST_STATISTIC`
- `SAMPLE_SIZE`

Measurement payload:

```python
{
    "TEST_STATISTIC": <float Levene W statistic>,
    "P_VALUE": <float in [0, 1]>,
    "DRIFT_ALARM_STATE": <bool>,
    "SAMPLE_SIZE": {
        "reference": <effective_reference_n>,
        "current": <effective_current_n>,
        "dropped_reference": <dropped_reference_n>,
        "dropped_current": <dropped_current_n>,
    },
    "REFERENCE_VARIANCE": <float sample variance with ddof=1>,
    "CURRENT_VARIANCE": <float sample variance with ddof=1>,
    "VARIANCE_RATIO": <max variance / min positive variance or None>,
    "REFERENCE_CENTER": <float mean/median/trimmed mean used for summary>,
    "CURRENT_CENTER": <float mean/median/trimmed mean used for summary>,
    "CENTER_POLICY": <"mean" | "median" | "trimmed">,
    "PROPORTION_TO_CUT": <float or None>,
}
```

Top-level `DriftResult` fields:

- `method_id="DM-021"`
- `method_name="Levene's Test"`
- `method_category="BatchDistributionComparison"`
- `variant_id=<resolved variant>`
- `test_statistic=<Levene W statistic>`
- `p_value=<p-value>`
- `drift_score=<test statistic>`
- `threshold=<alpha>`
- `drift_detected=<p_value < alpha>` when applicable

`REFERENCE_VARIANCE`, `CURRENT_VARIANCE`, `VARIANCE_RATIO`,
`REFERENCE_CENTER`, `CURRENT_CENTER`, `CENTER_POLICY`, and
`PROPORTION_TO_CUT` are helper measurements for interpretation. They are not
catalog canonical measurements and must not replace the canonical p-value alarm
rule.

## 7. Algorithm Steps

1. Merge `params` with defaults and resolve `variant_id`.
2. Validate `variant_id`; unsupported variants return `not_applicable`.
3. Resolve `alpha` from `params["alpha"]` or `params["threshold_or_alpha"]`;
   require `0 < alpha < 1`.
4. Resolve `center` from the selected variant. If the caller supplies a
   contradictory `center`, return `not_applicable` with an explicit warning.
5. Resolve `alternative`; require `two-sided` for the first implementation.
6. Validate `proportiontocut` for `TRIMMED_MEAN_LEVENE`; require
   `0 <= proportiontocut < 0.5`.
7. Validate `min_reference_size`, `min_current_size`, `nan_policy`, and warning
   thresholds.
8. Validate `time_col`, `value_col`, `reference_window`, and `current_window`.
9. Convert `time_col` to datetime, sort by time, and slice inclusive reference
   and current windows.
10. Coerce `value_col` to numeric within each window and apply
    `nan_policy="omit"` by dropping missing and non-finite values. Record
    original/effective counts and dropped counts.
11. Enforce `min_reference_size` and `min_current_size`.
12. Reject degenerate windows where either effective window has fewer than two
    distinct finite values and both sample variances are zero, because the
    backend statistic/p-value is not informative for variance drift.
13. Build `reference_values` and `current_values` as 1D `numpy.ndarray[float64]`.
14. Call `scipy.stats.levene(reference_values, current_values,
    center=<resolved_center>, proportiontocut=<resolved_proportiontocut>)`.
15. Convert backend statistic and p-value to finite floats. Non-finite
    statistic or p-value returns `not_applicable` unless a future backend
    documents a non-significant degenerate result.
16. Compute summary values:
    - effective sample counts
    - sample variances with `ddof=1`
    - variance ratio using the larger variance divided by the smaller positive
      variance
    - reference/current centers using the resolved center policy
17. Add caution warnings when assumptions are fragile:
    - invalid values were dropped
    - either effective sample size is below `small_sample_warning_threshold`
    - variance ratio exceeds `variance_ratio_warning_threshold`
    - heavy tails, outliers, autocorrelation, or repeated observations may
      affect interpretation
    - multiple numeric signals were tested outside this function without
      correction
18. Set `drift_detected = p_value < alpha`.
19. Set severity:
    - `drift_detected` when `drift_detected is True`
    - `normal` when `drift_detected is False`
    - `not_applicable` for validation/precondition failures
    - `error` only for unexpected calculation failures
20. Build interpretation text:
    - include variant, center policy, Levene statistic, p-value, alpha,
      reference/current variances, variance ratio, and effective sample sizes
    - describe a positive alarm as a variance/scale drift candidate
    - avoid mean-shift, full-distribution, root-cause, and performance claims
      without additional evidence
21. Return `DriftResult` with canonical measurement keys, warnings, and
    metadata.

## 8. Drift Decision Rule

Null hypothesis for all first implementation variants:

```text
reference and current windows have equal variance/scale under the selected
center policy.
```

Alternative hypothesis:

```text
reference and current windows do not have equal variance/scale.
```

Implementation rule:

```python
drift_detected = p_value < alpha
```

Default `alpha` is `0.05`. Equality is not drift: `p_value == alpha` returns
`False`.

For report wording:

- `drift_detected=True`: "numeric variance/scale drift candidate"
- `drift_detected=False`: "no statistically significant variance/scale change
  under this window, variant, and alpha"
- `drift_detected=None`: method was not applicable or calculation failed

The decision rule is based on p-value only. Variance ratio and center summaries
qualify effect size and direction, but must not override the alarm state in the
first implementation.

## 9. Warnings and Not-Applicable Conditions

Return `severity="not_applicable"` and `drift_detected=None` for:

- missing `time_col` or `value_col`
- non-datetime-coercible `time_col`
- non-numeric or boolean `value_col`
- missing `reference_window` or `current_window`
- empty reference or current window after slicing
- no finite numeric values after invalid rows are handled
- effective sample size below `min_reference_size` or `min_current_size`
- unsupported `variant_id`
- invalid `alpha`, `center`, `alternative`, `proportiontocut`, `nan_policy`,
  `min_reference_size`, or `min_current_size`
- supplied `center` contradicts the selected variant
- both windows are constant or otherwise degenerate such that variance
  comparison is not informative
- backend returns non-finite p-value or statistic

Return `severity="normal"` or `severity="drift_detected"` with warnings when the
method can still run but interpretation needs caution:

- invalid rows were dropped from either window
- effective sample size is small, so power and p-value stability may be weak
- reference/current sample sizes are highly imbalanced
- variance ratio is large and should be reported as effect-size context
- mean-centered variant is selected for data with possible outliers or
  heavy-tailed behavior
- trimmed variant uses a non-default `proportiontocut`
- repeated or autocorrelated time-series observations may violate independence
- multiple features were tested outside this function without correction
- `P_VALUE` and `TEST_STATISTIC` are not comparable to other method families
  without method and variant context

Unexpected backend exceptions should return `severity="error"` with the
exception class/message in warnings or metadata, without raising through the
public detector boundary.

## 10. Implementation Target

```text
module: drift_algorithm.methods.batchdistributioncomparison
function: detect_levene_s_test
```

Expected dependencies:

- `pandas` for input normalization and window slicing
- `numpy` for finite numeric arrays, summaries, and validation helpers
- `scipy.stats.levene` for Levene/Brown-Forsythe statistic and p-value

Helper functions should follow existing batch method patterns in
`drift_algorithm.methods.batchdistributioncomparison`:

- use the common `DriftResult` dataclass
- use `not_applicable_result` for validation failures when possible
- keep method-specific helpers private to the module unless they are already
  shared by another numeric batch method
- record backend center policy, backend function name, `alpha`,
  `proportiontocut`, effective window bounds, and sample-size metadata so the
  result is auditable

## 11. Verification Plan

Create focused tests when implementation starts:

1. Default Brown-Forsythe no-drift:
   - reference/current generated from the same numeric distribution
   - omit `variant_id` and assert
     `variant_id="BROWN_FORSYTHE_MEDIAN_CENTER"`
   - assert `P_VALUE`, `TEST_STATISTIC`, `DRIFT_ALARM_STATE=False`,
     `drift_detected=False`, `severity="normal"`, and sample-size metadata.
2. Brown-Forsythe drift candidate:
   - current generated with a materially larger variance than reference
   - assert `p_value < 0.05`, `severity="drift_detected"`, canonical
     measurements, reference/current variances, and variance ratio.
3. Mean-centered variant:
   - explicitly select `LEVENE_MEAN_CENTER`
   - assert backend metadata records `center="mean"`
   - use outlier-prone data and assert a caution warning recommends robust
     interpretation or Brown-Forsythe comparison.
4. Trimmed variant:
   - explicitly select `TRIMMED_MEAN_LEVENE` with `proportiontocut=0.1`
   - assert backend metadata records `center="trimmed"` and
     `proportiontocut=0.1`
   - invalid `proportiontocut >= 0.5` returns `not_applicable`.
5. Parameter validation:
   - invalid `alpha`
   - unsupported one-sided `alternative`
   - contradictory `center` for the selected variant
   - unsupported `variant_id`
   - unsupported `nan_policy` if not implemented.
6. Schema/window validation:
   - missing value column
   - non-numeric or boolean value column
   - missing reference/current windows
   - empty current/reference slices
   - sample size below minimum
   - all-constant or degenerate windows.
7. Warning behavior:
   - NaN/non-finite values are dropped with warnings and effective counts
   - small but valid samples produce low-power warnings
   - imbalanced sample sizes produce caution metadata
   - unrelated params such as `category_col` or `embedding_cols` are rejected or
     warned according to the implementation policy.

The test must assert canonical measurement keys, warning behavior, and the
documented `drift_detected` rule.

Recommended commands after implementation:

```text
python -m py_compile drift_algorithm\methods\batchdistributioncomparison.py
python -m pytest tests\test_levene_s_test.py
python -m pytest tests\test_f_test_variance_test.py tests\test_t_test.py
```
