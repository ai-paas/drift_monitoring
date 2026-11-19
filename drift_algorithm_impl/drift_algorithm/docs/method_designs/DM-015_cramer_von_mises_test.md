# DM-015 Cramer-von Mises Test Design

## Sprint 49 Implementation Note

Sprint 49 promotes `ONE_SAMPLE_CVM` and `K_SAMPLE_CVM` from deferred status for the server demo path. They execute through `scipy.stats.cramervonmises_2samp` over reference/current windows and record `execution_policy="two_sample_cvm_reference_current"` in metadata. Older deferred-status notes in this document are superseded for the harness/runtime path.

## 1. Method Identity

- Method ID: `DM-015`
- Method name: `Cramer-von Mises Test`
- Category: `BatchDistributionComparison`
- Method kind: `detector`
- Status: `확정`
- Source catalog: `drift_methods_catalog.md`
- Source variant document: `algorithm_variants/cramer_von_mises_test_algorithm_variants.md`
- Source parameter tables:
  - `drift_method_variant_links.csv`
  - `drift_method_variant_measurement_summary.csv`
  - `drift_method_variant_parameters.csv`
  - `drift_method_parameter_guide.md`

The first implementation is a univariate numeric batch detector. It compares
the empirical cumulative distribution of a current window against a reference
window with the two-sample Cramer-von Mises statistic.

## 2. Purpose

`Cramer-von Mises Test` answers whether a scalar numeric monitoring signal has
a different overall distribution in the current window than in the reference
window. The catalog input is `numeric sample`; the catalog outputs are `CvM
statistic` and `p-value`.

Use this method when:

- the signal is scalar numeric data such as score, latency, loss, residual,
  confidence, calibration error, or a numeric feature
- reference and current windows are both available
- the monitoring question concerns full empirical distribution change, not only
  mean shift, variance shift, or one threshold crossing
- a p-value alarm rule is acceptable for the first implementation

Do not use this method for categorical labels, count tables, probability
vectors, embeddings, multivariate features, text, SHAP matrices, or supervised
error streams. Those require other method families or a separate input schema.

## 3. Supported Variants

Supported for the first implementation:

- `TWO_SAMPLE_CVM`
  - Default variant.
  - Compares reference and current numeric samples directly.
  - Uses the two-sample Cramer-von Mises statistic and p-value.
  - Maps to `scipy.stats.cramervonmises_2samp` when SciPy is available.

Deferred variants that must return `severity="not_applicable"` until their
extra contracts are implemented:

- `ONE_SAMPLE_CVM`
  - Requires a named theoretical CDF or fitted reference distribution and a
    clear parameter/fitting policy. The common `(time, value)` reference/current
    window contract is not enough to define the CDF call.
- `K_SAMPLE_CVM`
  - Requires three or more named sample groups, such as `sample_group_col` or a
    structured `sample_groups` parameter. The first common function contract
    owns only reference/current windows.

Default variant selection:

```text
if params["variant_id"] is omitted:
    variant_id = "TWO_SAMPLE_CVM"
```

## 4. Input Schema

Use the common `pandas.DataFrame` input boundary from
`../input_output_contracts.md`.

Public function shape:

```python
def detect_cramer_von_mises_test(
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

These are monitoring stability guards. If either effective sample size is below
its minimum, return `severity="not_applicable"` and do not compute a drift
decision.

## 5. Parameters

Method-specific parameters come from `drift_method_parameter_guide.md`,
`drift_method_variant_parameters.csv`, and the variant source document.

Accepted `params` keys and defaults for the first implementation:

| Param | Type | Default | Applies to | Meaning |
|---|---:|---:|---|---|
| `variant_id` | string | `TWO_SAMPLE_CVM` | all | Variant selector. Only `TWO_SAMPLE_CVM` computes in the first implementation. |
| `alpha` | float | `0.05` | supported variant | Canonical significance level for the p-value drift rule. |
| `threshold_or_alpha` | float | optional | supported variant | Alias for `alpha`; if both are supplied they must agree. |
| `significance_level` | float | optional | supported variant | Alias for `alpha`; if supplied with another alpha alias it must agree. |
| `alternative` | string | `two-sided` | supported variant | First implementation supports only `two-sided`/`both`. Directional alternatives return not applicable. |
| `p_value_method` | string | `auto` | supported variant | Accepted values: `auto`, `asymptotic`, `exact`. Passed to SciPy when supported by the installed version; otherwise `auto`/`asymptotic` are treated as the backend default and unsupported exact requests return not applicable. |
| `input_signal` | string | optional | supported variant | Value column name only when `value_col is None`; otherwise recorded as metadata label. |
| `sample_groups` | object | optional | deferred variants | Metadata only for the first implementation; does not enable k-sample execution. |
| `min_reference_size` | int | `20` | supported variant | Minimum effective reference sample size after invalid rows are dropped. |
| `min_current_size` | int | `20` | supported variant | Minimum effective current sample size after invalid rows are dropped. |
| `nan_policy` | string | `drop` | supported variant | First implementation supports `drop`/`omit` only. |
| `tie_policy` | string | `warn_only` | supported variant | First implementation computes with ties but warns because continuous-test interpretation is weaker. |
| `multiple_testing_correction` | string | `none` | supported variant | Recorded as metadata only. Correction is not applied inside this single-signal detector. |

Parameter rules:

- `alpha`, `threshold_or_alpha`, and `significance_level` must be numeric and
  satisfy `0 < value < 1`.
- Alpha aliases must not conflict. Conflicting values return
  `severity="not_applicable"`.
- `alternative` accepts `"two-sided"` and `"both"` only in the first
  implementation.
- `p_value_method="exact"` is allowed only if the installed SciPy backend can
  honor it for `cramervonmises_2samp`; otherwise return not applicable rather
  than silently changing the requested method.
- `nan_policy` supports `"drop"` and `"omit"` as aliases for dropping invalid
  rows. Other values return not applicable.
- `tie_policy` supports `"warn_only"` only.
- `multiple_testing_correction != "none"` adds a warning and is recorded in
  metadata, but the p-value is not corrected by this detector.
- Reject or warn on unrelated params such as `feature_cols`, `category_col`,
  `count_col`, `embedding_cols`, label columns, covariance settings,
  classifier settings, binning settings, or paired-sample settings.

Recommended SciPy mapping:

```python
scipy.stats.cramervonmises_2samp(
    reference_values,
    current_values,
    method=<resolved p_value_method when supported>,
)
```

Expected returned fields are `statistic` and `pvalue`. If SciPy is unavailable
or the installed version does not expose `cramervonmises_2samp`, return
`severity="error"` or `severity="watch"` according to the project convention
for missing optional dependencies, with `drift_detected=None` and a warning that
the CvM statistic and p-value could not be computed.

## 6. Output Measurements

`drift_method_variant_measurement_summary.csv` maps all DM-015 variants to:

```text
TEST_STATISTIC
P_VALUE
DRIFT_ALARM_STATE
```

Return these canonical measurements for every successful supported run:

```python
{
    "TEST_STATISTIC": <float CvM statistic>,
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
    "REFERENCE_MEAN": <float>,
    "CURRENT_MEAN": <float>,
    "REFERENCE_MEDIAN": <float>,
    "CURRENT_MEDIAN": <float>,
    "REFERENCE_Q25": <float>,
    "CURRENT_Q25": <float>,
    "REFERENCE_Q75": <float>,
    "CURRENT_Q75": <float>,
    "MEDIAN_DELTA": <current median - reference median>,
}
```

Top-level `DriftResult` field mapping:

```text
method_id = "DM-015"
method_name = "Cramer-von Mises Test"
method_category = "BatchDistributionComparison"
variant_id = "TWO_SAMPLE_CVM"
drift_score = TEST_STATISTIC
p_value = P_VALUE
test_statistic = TEST_STATISTIC
threshold = alpha
drift_detected = p_value < alpha when applicable
```

The mean, median, quartile, and median delta measurements are interpretation
helpers. They must not replace the p-value alarm rule.

Interpretation text should state:

- which variant ran
- reference/current effective sample sizes
- CvM statistic value
- p-value and alpha
- whether the result crossed the drift rule
- median or quartile movement as descriptive context when available
- that the result is a numeric distribution drift candidate, not proof of root
  cause, model performance degradation, or supervised concept drift

## 7. Algorithm Steps

1. Normalize `params` to an empty dict when omitted.
2. Resolve `variant_id`; default to `TWO_SAMPLE_CVM`.
3. Reject deferred or unknown variants with `severity="not_applicable"` and a
   warning naming the unsupported variant.
4. Resolve `alpha` and alpha aliases; require no conflicts and `0 < alpha < 1`.
5. Resolve `alternative`; require `two-sided`/`both`.
6. Resolve `p_value_method`, `nan_policy`, `tie_policy`,
   `multiple_testing_correction`, sample-size minima, and the value column.
7. Validate that both reference and current windows are supplied and parseable.
8. Validate required columns and scalar numeric value data. Boolean data is not
   valid numeric CvM input.
9. Convert and sort the DataFrame according to the common window handling
   contract.
10. Slice inclusive reference and current windows.
11. Drop rows with invalid timestamps or non-finite values; record original and
    effective counts.
12. If either effective sample is empty or below minimum, return not
    applicable.
13. Convert the two effective samples to one-dimensional
    `numpy.ndarray[float64]` objects.
14. Add warnings for ties, highly imbalanced sample sizes, autocorrelation
    concerns, and multiple-testing metadata when applicable.
15. Call `scipy.stats.cramervonmises_2samp` with the two arrays and the
    resolved method policy when supported.
16. Convert statistic and p-value to Python floats; guard against NaN/inf and
    p-values outside `[0, 1]`.
17. Compute descriptive summaries: effective sample counts, means, medians,
    25th/75th percentiles, and median delta.
18. Apply the drift decision rule from section 8.
19. Build `DriftResult` with method identity, variant, canonical measurements,
    helper summaries, counts, windows, parameters, warnings, and concise
    interpretation text.

## 8. Drift Decision Rule

Null hypothesis for the first implementation:

```text
reference and current numeric samples are drawn from the same distribution.
```

Alternative hypothesis:

```text
reference and current numeric samples are not drawn from the same distribution.
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

- `drift_detected=True`: "numeric distribution drift candidate"
- `drift_detected=False`: "no statistically significant numeric distribution
  change under this window, variant, and alpha"
- `drift_detected=None`: method was not applicable or calculation failed

The CvM statistic is method-specific. A larger statistic generally means
stronger cumulative distribution difference, but it must not be compared
directly with KS, Anderson-Darling, Mann-Whitney, chi-square, or Wasserstein
values without method and variant context.

## 9. Warnings and Not-Applicable Conditions

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
- unsupported `alternative`, `p_value_method`, `nan_policy`, `tie_policy`,
  `min_reference_size`, or `min_current_size`
- current/reference window overlap when overlap policy is not explicitly
  defined by the implementation
- `ONE_SAMPLE_CVM` without a fully specified theoretical or fitted CDF contract
- `K_SAMPLE_CVM` without a first-class multi-group input contract
- backend returns non-finite statistic, non-finite p-value, or p-value outside
  `[0, 1]`

Return `severity="normal"` or `severity="drift_detected"` with warnings when the
method can still run but interpretation needs caution:

- timestamps or values were dropped because they were invalid or non-finite
- duplicate values or ties are present, weakening continuous-distribution
  interpretation
- reference/current sample sizes are highly imbalanced
- either effective sample size is below a configurable low-power warning
  threshold, if implemented
- observations are repeated or autocorrelated time-series rows rather than
  independent samples
- sample extraction, traffic mix, seasonality, or segment definitions differ
  between windows
- `multiple_testing_correction` is not `"none"`; record that this detector does
  not apply correction internally
- the selected SciPy method is approximate/asymptotic and the sample size is
  small

Unexpected backend exceptions should return `severity="error"` with the
exception class/message in warnings or metadata, without raising through the
public detector boundary.

Do not silently coerce categorical values, boolean flags, labels, embeddings,
lists, or objects into the numeric Cramer-von Mises detector.

## 10. Implementation Target

```text
module: drift_algorithm.methods.batchdistributioncomparison
function: detect_cramer_von_mises_test
```

The module should expose `detect_cramer_von_mises_test` through the same package
path used by the other batch distribution methods. If the concrete package later
separates one method per file, keep this public import path stable or add a
compatibility import.

Expected dependencies:

```text
pandas
numpy
scipy.stats.cramervonmises_2samp
```

Expected result object:

```text
DriftResult from drift_algorithm/docs/input_output_contracts.md equivalent code
contract
```

Helper functions should follow existing patterns in
`drift_algorithm.methods.batchdistributioncomparison`:

- use the common `DriftResult` dataclass
- use `not_applicable_result` or method-specific not-applicable helpers for
  validation failures
- use the existing numeric window preparation helper where it matches this
  contract
- keep method-specific helpers private to the module unless another numeric
  batch method already shares the same helper
- record backend function name, backend method policy, `alpha`, value column,
  effective windows, sample-size metadata, and unsupported/deferred variant
  decisions so the result is auditable

## 11. Verification Plan

Unit tests for the first implementation:

1. Default two-sample no-drift:
   - Generate reference/current numeric samples from the same distribution with
     a deterministic seed.
   - Omit `variant_id` and assert `variant_id == "TWO_SAMPLE_CVM"`.
   - Assert `TEST_STATISTIC`, `P_VALUE`, `DRIFT_ALARM_STATE`, `SAMPLE_SIZE`,
     `SAMPLE_SIZE_REFERENCE`, and `SAMPLE_SIZE_CURRENT` exist.
   - Assert `drift_detected is False` and `severity == "normal"` for a seed
     chosen to keep `p_value >= 0.05`.
2. Two-sample drift candidate:
   - Generate reference normal samples and current samples with a location,
     scale, or shape shift.
   - Assert `p_value < alpha`, `drift_detected is True`,
     `severity == "drift_detected"`, and canonical measurements are populated.
3. Parameter alias and validation:
   - Assert `threshold_or_alpha` and `significance_level` route to `alpha`.
   - Assert conflicting alpha aliases return `severity="not_applicable"`.
   - Assert unsupported one-sided `alternative` returns not applicable.
   - Assert unsupported `p_value_method` returns not applicable.
4. Schema and window validation:
   - Missing value column.
   - Non-numeric, boolean, object/list, or categorical value column.
   - Missing reference/current windows.
   - Empty current/reference slices.
   - Effective sample size below minimum.
   - Overlapping windows if no overlap policy is implemented.
5. Deferred variants:
   - `ONE_SAMPLE_CVM` returns `severity="not_applicable"` with a warning about
     missing CDF/fitted distribution contract.
   - `K_SAMPLE_CVM` returns `severity="not_applicable"` with a warning about
     missing multi-group input contract.
6. Warning behavior:
   - NaN, infinity, and invalid timestamps are dropped with warnings and
     effective counts.
   - Ties/repeated values compute with a caution warning.
   - Highly imbalanced sample sizes produce warning metadata.
   - `multiple_testing_correction != "none"` is recorded but not applied.
7. Backend failure:
   - Simulate missing/failed `cramervonmises_2samp`.
   - Assert the public detector returns `severity="error"` or `"watch"` with
     `drift_detected=None` and a clear warning.

Recommended commands after implementation:

```text
python -m py_compile drift_algorithm\methods\batchdistributioncomparison.py
python -m pytest tests\test_cramer_von_mises_test.py
python -m pytest tests\test_anderson_darling_test.py tests\test_levene_s_test.py
```

Manual review before marking implementation complete:

- Confirm public function signature matches the common contract.
- Confirm canonical measurement names match
  `drift_method_variant_measurement_summary.csv`.
- Confirm deferred variants fail explicitly instead of falling through to a
  misleading two-sample calculation.
- Confirm interpretation text avoids root-cause, performance-degradation, and
  supervised concept-drift claims without labeled evidence.
- Confirm `git diff` only changes
  `drift_algorithm/docs/method_designs/DM-015_cramer_von_mises_test.md`.

## 12. Manager Review Points

- First implementation scope is intentionally limited to two-sample univariate
  numeric `(time, value)` CvM.
- `ONE_SAMPLE_CVM` and `K_SAMPLE_CVM` remain cataloged variants but are deferred
  until their CDF or multi-group contracts are approved.
- The public target is `detect_cramer_von_mises_test` in
  `drift_algorithm.methods.batchdistributioncomparison`.
- Drift decision is strictly `p_value < alpha`; descriptive summaries do not
  override the alarm.
