# DM-023 Epps-Singleton Test Design

## Sprint 49 Implementation Note

Sprint 49 promotes `ASYMPTOTIC_EPPS_SINGLETON` from deferred status for the server demo path. It executes through `scipy.stats.epps_singleton_2samp` over reference/current windows and records `execution_policy="asymptotic_epps_singleton_reference_current"` in metadata. Older deferred-status notes in this document are superseded for the harness/runtime path.

## 1. Method Identity

- Method ID: `DM-023`
- Method name: `Epps-Singleton Test`
- Category: `BatchDistributionComparison`
- Method kind: `detector`
- Status: `확정`
- Source catalog: `drift_methods_catalog.md`
- Source variant document: `algorithm_variants/epps_singleton_test_algorithm_variants.md`
- Source parameter tables:
  - `drift_method_variant_links.csv`
  - `drift_method_variant_measurement_summary.csv`
  - `drift_method_variant_parameters.csv`
  - `drift_method_parameter_guide.md`

The first implementation is a univariate numeric batch detector. It compares a
reference `(time, value)` window with a current `(time, value)` window using the
two-sample Epps-Singleton test and returns a test statistic, p-value, and alarm
state.

## 2. Purpose

`Epps-Singleton Test` answers whether two scalar numeric samples plausibly come
from the same distribution. It uses empirical characteristic functions, so it is
useful as a distribution-shape test for model scores, losses, latencies,
numeric features, residuals, costs, confidence values, or discrete-like numeric
signals with repeated values.

The catalog input is `numeric 또는 discrete sample`; the catalog output is
`test statistic, p-value`.

Use the first implementation when:

- the monitored signal is one scalar numeric column
- reference and current windows are both available
- the question is two-window distribution drift, not root cause or supervised
  concept drift
- an asymptotic p-value from `scipy.stats.epps_singleton_2samp` is acceptable

Do not use the first implementation for categorical labels, count tables,
probability vectors, embeddings, multivariate feature matrices, text, SHAP
matrices, or supervised error streams. Those require other method families or a
future expanded contract.

## 3. Supported Variants

Supported for the first implementation:

- `TWO_SAMPLE_EPPS_SINGLETON`
  - Default variant.
  - Uses scalar numeric reference/current windows.
  - Calls `scipy.stats.epps_singleton_2samp(reference_values,
    current_values, t=<resolved_t_points>)`.
  - Uses the backend asymptotic p-value and the strict `p_value < alpha` drift
    rule.

Implementation-ready but opt-in in the same first-scope input contract:

- `DISCRETE_EPPS_SINGLETON`
  - Uses the same scalar numeric `(time, value)` contract.
  - Intended for integer, count, rounded, bucketized, or low-cardinality
    ordered numeric signals.
  - May call the same SciPy backend because the Epps-Singleton test can be used
    with continuous or discrete numeric samples.
  - Must add discrete/tie cautions and helper frequency metadata.
  - Must not accept string categories or count-table input in the first
    implementation. If the value column is not scalar numeric, return
    `not_applicable`.

Deferred until an explicit approximation contract is approved:

- `ASYMPTOTIC_EPPS_SINGLETON`
  - SciPy's backend already reports an asymptotic p-value for the two-sample
    test. That backend behavior is used by `TWO_SAMPLE_EPPS_SINGLETON`.
  - A separate `ASYMPTOTIC_EPPS_SINGLETON` variant is deferred because it needs
    explicit choices for approximation diagnostics, degrees-of-freedom
    reporting, small-sample correction policy, and high-volume screening
    guardrails.
  - The first implementation should return `severity="not_applicable"` for
    this variant with a warning that the named asymptotic screening variant is
    deferred, unless manager review explicitly decides to alias it to
    `TWO_SAMPLE_EPPS_SINGLETON`.

Default variant selection:

```text
if params["variant_id"] is omitted:
    variant_id = "TWO_SAMPLE_EPPS_SINGLETON"
```

## 4. Input Schema

Use the common `pandas.DataFrame` input boundary from
`../input_output_contracts.md`.

Public function shape:

```python
def detect_epps_singleton_test(
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

Rows are processed as follows:

1. Validate that `time_col` and the resolved value column exist.
2. Convert `time_col` with `pd.to_datetime(..., errors="coerce")`.
3. Convert the value column with `pd.to_numeric(..., errors="coerce")`.
4. Sort by `time_col`.
5. Slice inclusive reference/current windows.
6. Drop rows with invalid timestamps or non-finite values.
7. Record original and effective row counts in `metadata` and `measurements`.

Minimum effective sample sizes:

```text
min_reference_size: default 20
min_current_size: default 20
backend_hard_minimum: 5 values per window
```

SciPy requires enough values per sample for the Epps-Singleton statistic and
may fail for very small or degenerate samples. The implementation default is
20 because monitoring p-values are unstable at very small sizes. If either
effective sample size is below its minimum, return
`severity="not_applicable"` and do not compute a drift decision.

## 5. Parameters

Method-specific parameters come from `drift_method_parameter_guide.md`,
`drift_method_variant_parameters.csv`, and the variant source document.

Accepted `params` keys and defaults for the first implementation:

| Param | Type | Default | Applies to | Meaning |
|---|---:|---:|---|---|
| `variant_id` | string | `TWO_SAMPLE_EPPS_SINGLETON` | all | Variant selector. |
| `alpha` | float | `0.05` | supported variants | Significance level for the p-value drift rule. |
| `threshold_or_alpha` | float | optional | supported variants | Alias for `alpha`; must not conflict with `alpha` or `significance_level`. |
| `significance_level` | float | optional | supported variants | Alias for `alpha`; must not conflict with other alpha aliases. |
| `input_signal` | string | optional | all | Value column name only when `value_col is None`; otherwise metadata label. |
| `t_points` | sequence[float] | `(0.4, 0.8)` | supported variants | Characteristic-function evaluation points passed to SciPy as `t`. |
| `p_value_method` | string | `asymptotic` | supported variants | First implementation supports only `asymptotic`/`scipy_asymptotic`. |
| `correction_policy` | string | `scipy_default` | supported variants | Records that SciPy's internal small-sample/statistic correction policy is used. |
| `asymptotic_method` | string | `scipy` | deferred variant | Metadata only unless `ASYMPTOTIC_EPPS_SINGLETON` is later enabled. |
| `min_reference_size` | int | `20` | supported variants | Minimum effective reference sample size after invalid rows are dropped. |
| `min_current_size` | int | `20` | supported variants | Minimum effective current sample size after invalid rows are dropped. |
| `nan_policy` | string | `drop` | supported variants | First implementation supports `drop`/`omit` only. |
| `tie_unique_ratio_threshold` | float | `0.95` | supported variants | Adds a discrete/tie caution when pooled unique ratio is below this value. |
| `sample_imbalance_warning_ratio` | float | `10.0` | supported variants | Warn when larger sample size divided by smaller sample size exceeds this ratio. |
| `multiple_testing_correction` | string | `none` | supported variants | Recorded as metadata only. Correction is not applied inside this detector. |

Parameter rules:

- Resolve `alpha` from `alpha`, `threshold_or_alpha`, or
  `significance_level`; aliases must not conflict and must satisfy
  `0 < alpha < 1`.
- `t_points` must be a one-dimensional non-empty sequence of finite positive
  floats. Default to SciPy's documented default `(0.4, 0.8)`.
- Reject duplicated `t_points` values because they can make the covariance
  system singular or redundant.
- Warn when more than four `t_points` are supplied because the statistic
  dimensionality and singular-covariance risk increase.
- `p_value_method` must be `asymptotic`, `scipy`, or `scipy_asymptotic` in the
  first implementation. Exact, permutation, and bootstrap p-values are
  deferred.
- `correction_policy` must be `scipy_default` or `auto`. Do not implement a
  separate local correction in the first pass.
- `nan_policy` supports `drop` and `omit` as aliases for dropping invalid rows.
  Other values return `not_applicable`.
- `multiple_testing_correction != "none"` adds a warning and is recorded in
  metadata, but the p-value is not corrected by this detector.
- Reject or warn on unrelated params such as `feature_cols`, `embedding_cols`,
  `category_col`, `count_col`, label columns, classifier settings, covariance
  settings, projection settings, or binning settings.

## 6. Statistic, SciPy Backend, and P-value Policy

The first implementation should use SciPy directly:

```python
from scipy.stats import epps_singleton_2samp

result = epps_singleton_2samp(
    reference_values,
    current_values,
    t=resolved_t_points,
)
test_statistic = float(result.statistic)
p_value = float(result.pvalue)
```

Backend policy:

- `scipy.stats.epps_singleton_2samp` is the required backend for supported
  first-scope variants.
- If SciPy or `epps_singleton_2samp` is unavailable, return `severity="error"`
  or `severity="watch"` according to project convention, with
  `drift_detected=None` and a clear warning.
- Do not locally reimplement the Epps-Singleton statistic in the first pass.
- Do not fabricate p-values from a threshold or distance rule.
- Record `backend="scipy.stats.epps_singleton_2samp"`, resolved `t_points`,
  `p_value_method`, and `correction_policy` in metadata.

P-value policy:

```text
p_value_method = "asymptotic" by default
p_value must be finite and in [0, 1]
drift_detected = p_value < alpha
```

The SciPy p-value is interpreted as the two-sample Epps-Singleton asymptotic
p-value under the null hypothesis that the reference and current samples come
from the same distribution. The implementation must use strict `< alpha`; a
p-value equal to alpha is not drift.

## 7. Output Measurements

`drift_method_variant_measurement_summary.csv` maps all DM-023 variants to:

```text
TEST_STATISTIC
P_VALUE
DRIFT_ALARM_STATE
```

Return these canonical measurements for every successful supported run:

```python
{
    "TEST_STATISTIC": <float Epps-Singleton statistic>,
    "P_VALUE": <float in [0, 1]>,
    "DRIFT_ALARM_STATE": <"drift_detected" | "normal">,
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
    "EPPS_SINGLETON_STATISTIC": <same float as TEST_STATISTIC>,
    "REFERENCE_MEAN": <float>,
    "CURRENT_MEAN": <float>,
    "REFERENCE_MEDIAN": <float>,
    "CURRENT_MEDIAN": <float>,
    "REFERENCE_Q25": <float>,
    "CURRENT_Q25": <float>,
    "REFERENCE_Q75": <float>,
    "CURRENT_Q75": <float>,
    "MEAN_DELTA": <current mean - reference mean>,
    "MEDIAN_DELTA": <current median - reference median>,
    "REFERENCE_UNIQUE_RATIO": <float>,
    "CURRENT_UNIQUE_RATIO": <float>,
    "COMBINED_UNIQUE_RATIO": <float>,
    "T_POINTS": <list[float]>,
}
```

For `DISCRETE_EPPS_SINGLETON`, also include helper metadata when feasible:

```python
{
    "DISCRETE_VALUE_COUNT_REFERENCE": <int>,
    "DISCRETE_VALUE_COUNT_CURRENT": <int>,
    "DISCRETE_TOP_VALUE_FREQUENCIES": {
        "reference": <list of value/count pairs>,
        "current": <list of value/count pairs>,
    },
}
```

Top-level `DriftResult` field mapping:

```text
method_id = "DM-023"
method_name = "Epps-Singleton Test"
method_category = "BatchDistributionComparison"
variant_id = resolved variant id
drift_score = test_statistic
p_value = p_value
test_statistic = test_statistic
threshold = alpha
drift_detected = p_value < alpha
```

Interpretation text should state:

- which variant ran
- reference/current effective sample sizes
- Epps-Singleton statistic, p-value, alpha, and `t_points`
- whether the strict p-value rule fired
- mean/median/quartile movement as descriptive context when available
- discrete/tie cautions when repeated values are common
- that the result is a numeric distribution drift candidate, not proof of root
  cause, model performance degradation, or supervised concept drift

## 8. Algorithm Steps

1. Normalize `params` to an empty dict when omitted.
2. Resolve `variant_id`; default to `TWO_SAMPLE_EPPS_SINGLETON`.
3. Reject unknown variants with `severity="not_applicable"` and a warning.
4. Reject `ASYMPTOTIC_EPPS_SINGLETON` with `severity="not_applicable"` until
   the named asymptotic screening contract is approved.
5. Resolve `alpha`, `t_points`, `p_value_method`, `correction_policy`,
   `nan_policy`, warning thresholds, sample-size minima, and the value column.
6. Validate that both reference and current windows are supplied and parseable.
7. Validate required columns and scalar numeric value data. Boolean data is not
   valid Epps-Singleton input.
8. Convert and sort the DataFrame according to the common window handling
   contract.
9. Slice inclusive reference and current windows.
10. Drop rows with invalid timestamps or non-finite values; record original and
    effective counts.
11. If either effective sample is empty or below minimum, return not
    applicable.
12. Convert the two effective samples to one-dimensional
    `numpy.ndarray[float64]` objects.
13. Add warnings for invalid rows, highly imbalanced sample sizes, repeated or
    discrete-like values, small samples that pass the hard minimum, and
    multiple-testing metadata when applicable.
14. For `DISCRETE_EPPS_SINGLETON`, verify the values are numeric integer,
    rounded, or low-cardinality numeric values; otherwise allow the test to run
    only as `TWO_SAMPLE_EPPS_SINGLETON`.
15. Call `scipy.stats.epps_singleton_2samp(reference_values, current_values,
    t=resolved_t_points)`.
16. Convert statistic and p-value to Python floats and guard against NaN/inf or
    p-value outside `[0, 1]`.
17. Compute descriptive summaries: effective sample counts, means, medians,
    25th/75th percentiles, deltas, unique ratios, and optional discrete
    frequency summaries.
18. Apply the drift decision rule from section 9.
19. Build `DriftResult` with method identity, variant, canonical measurements,
    helper summaries, counts, windows, parameters, warnings, and concise
    interpretation text.

## 9. Drift Decision Rule

Null hypothesis:

```text
reference and current windows come from the same distribution.
```

Implementation rule for successful supported runs:

```python
drift_detected = p_value < alpha
```

Default `alpha` is `0.05`. Equality is not drift:
`p_value == alpha` returns `False`.

Severity and alarm state:

```text
if p_value < alpha:
    drift_detected = True
    severity = "drift_detected"
    DRIFT_ALARM_STATE = "drift_detected"
else:
    drift_detected = False
    severity = "normal"
    DRIFT_ALARM_STATE = "normal"
```

If the test runs but important interpretation cautions are present, such as
very low unique ratio or heavy ties in the discrete variant, the implementation
may use `severity="drift_candidate"` for a positive alarm if that matches the
project's established severity convention. It must still set
`drift_detected=True` only from `p_value < alpha`.

For report wording:

- `drift_detected=True`: "numeric distribution drift candidate under the
  Epps-Singleton p-value rule"
- `drift_detected=False`: "no statistically significant Epps-Singleton alarm
  under this window, variant, `t_points`, and alpha"
- `drift_detected=None`: method was not applicable or calculation failed

The statistic magnitude is method-specific and depends on `t_points`, sample
sizes, and backend policy. It must not be compared directly with KS,
Wasserstein, Cramer-von Mises, Energy Distance, MMD, or multivariate statistics
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
- `ASYMPTOTIC_EPPS_SINGLETON` until the named asymptotic screening contract is
  approved
- `DISCRETE_EPPS_SINGLETON` called with nonnumeric categories or count tables
- invalid `alpha`, alpha alias conflict, `t_points`, `p_value_method`,
  `correction_policy`, `nan_policy`, sample-size parameter, or warning-ratio
  parameter
- exact, permutation, or bootstrap p-value requests in the first implementation
- non-finite statistic or p-value from the backend
- p-value outside `[0, 1]`
- backend failure caused by singular covariance, degenerate samples, or invalid
  characteristic-function points
- current/reference window overlap when overlap policy is not explicitly
  defined by the implementation

Return `severity="normal"`, `"drift_candidate"`, or `"drift_detected"` with
warnings when the method can still run but interpretation needs caution:

- timestamps or values were dropped because they were invalid or non-finite
- either effective sample size is below a small-sample warning threshold, even
  if it passes the hard minimum
- reference/current sample sizes are highly imbalanced
- repeated, rounded, tied, or low-cardinality values make the input
  discrete-like
- `DISCRETE_EPPS_SINGLETON` is used and a few values dominate the frequency
  table
- more than four `t_points` are supplied
- observations are repeated or autocorrelated time-series rows rather than
  independent samples
- strong outliers or scale changes may dominate the characteristic-function
  comparison
- sample extraction, traffic mix, seasonality, or segment definitions differ
  between windows
- `multiple_testing_correction` is not `"none"`; record that this detector does
  not apply correction internally

Unexpected backend exceptions should return `severity="error"` or `"watch"`
according to project convention, with `drift_detected=None` and a clear warning,
without raising through the public detector boundary.

Do not silently coerce categorical values, boolean flags, labels, embeddings,
lists, object arrays, count tables, or multivariate matrices into the
univariate Epps-Singleton detector.

## 11. Implementation Target

```text
module: drift_algorithm.methods.batchdistributioncomparison
function: detect_epps_singleton_test
```

Expected dependencies:

```text
pandas
numpy
scipy.stats.epps_singleton_2samp
```

Expected result object:

```text
DriftResult from drift_algorithm/docs/input_output_contracts.md equivalent code
contract
```

Helper functions should follow existing patterns in
`drift_algorithm.methods.batchdistributioncomparison`:

- add `EPPS_SINGLETON_METHOD_ID = "DM-023"` and
  `EPPS_SINGLETON_METHOD_NAME = "Epps-Singleton Test"`
- define `SUPPORTED_EPPS_SINGLETON_VARIANTS` for
  `TWO_SAMPLE_EPPS_SINGLETON` and optionally `DISCRETE_EPPS_SINGLETON`
- define `DEFERRED_EPPS_SINGLETON_VARIANTS` for
  `ASYMPTOTIC_EPPS_SINGLETON`
- use the common `DriftResult` dataclass
- use `not_applicable_result` or a method-specific not-applicable helper for
  validation failures
- use `prepare_numeric_windows` where it matches this contract
- keep method-specific Epps-Singleton helpers private to the module unless
  another numeric batch method already shares the same helper
- record backend name, alpha policy, `t_points`, p-value method, correction
  policy, value column, effective windows, sample-size metadata, and
  unsupported/deferred variant decisions so the result is auditable

Suggested private helper shape:

```python
def _epps_singleton_not_applicable(
    variant_id: str | None,
    warning: str,
    metadata: dict[str, Any] | None = None,
    prior_warnings: list[str] | None = None,
) -> DriftResult:
    ...

def _resolve_epps_singleton_alpha(params: dict[str, Any]) -> float:
    """Resolve alpha aliases and reject conflicts."""

def _resolve_epps_singleton_t_points(params: dict[str, Any]) -> tuple[float, ...]:
    """Return validated positive finite characteristic-function points."""

def _epps_singleton_discrete_metadata(
    reference_values: np.ndarray,
    current_values: np.ndarray,
) -> dict[str, Any]:
    ...
```

Public contract:

- `detect_epps_singleton_test` must be importable from
  `drift_algorithm.methods.batchdistributioncomparison`.
- The function must accept the common arguments exactly as shown in section 4.
- It must return `DriftResult`, never raw tuples or dictionaries.
- Validation failures must return `severity="not_applicable"` unless they are
  unexpected backend/runtime errors.
- Supported variants must use `scipy.stats.epps_singleton_2samp`.
- The drift decision must use the documented strict `p_value < alpha` rule.

## 12. Verification Plan

Unit tests for the first implementation:

1. Default no-drift:
   - Generate reference/current numeric samples from the same distribution with
     a deterministic seed.
   - Omit `variant_id`.
   - Assert `variant_id == "TWO_SAMPLE_EPPS_SINGLETON"`.
   - Assert `TEST_STATISTIC`, `EPPS_SINGLETON_STATISTIC`, `P_VALUE`,
     `DRIFT_ALARM_STATE`, `SAMPLE_SIZE`, `SAMPLE_SIZE_REFERENCE`, and
     `SAMPLE_SIZE_CURRENT` exist.
   - Assert `p_value` is in `[0, 1]`, `drift_detected is False`, and
     `severity == "normal"` for a deterministic seed chosen to keep
     `p_value >= alpha`.
2. Default drift candidate:
   - Generate reference normal samples and current samples with a clear
     location, scale, or shape shift.
   - Assert `p_value < alpha`, `drift_detected is True`,
     `severity == "drift_detected"` or `"drift_candidate"` by project
     convention, and `DRIFT_ALARM_STATE == "drift_detected"`.
3. Custom `t_points`:
   - Pass `t_points=[0.4, 0.8, 1.2]`.
   - Assert metadata and measurements record the resolved list.
   - Invalid empty, nonnumeric, non-finite, nonpositive, or duplicated
     `t_points` return `not_applicable`.
4. Alpha alias and p-value policy:
   - Assert `threshold_or_alpha` and `significance_level` are interpreted as
     alpha.
   - Assert conflicting alpha aliases return `severity="not_applicable"`.
   - Assert `p_value_method="asymptotic"` and `"scipy_asymptotic"` work.
   - Assert exact, permutation, bootstrap, or unknown p-value methods return
     `not_applicable`.
5. Discrete variant:
   - Use integer or bucketized numeric samples with repeated values.
   - Assert the detector can run with `DISCRETE_EPPS_SINGLETON`, reports
     canonical measurements, and adds tie/discrete warnings plus unique-ratio
     metadata.
   - Assert string categories or count-table columns return `not_applicable`.
6. Deferred asymptotic variant:
   - `ASYMPTOTIC_EPPS_SINGLETON` returns `severity="not_applicable"` with a
     warning about the deferred named asymptotic screening contract.
7. Schema and window validation:
   - Missing value column.
   - Non-numeric, boolean, object/list, embedding-like, or categorical value
     column.
   - Missing reference/current windows.
   - Empty current/reference slices.
   - Effective sample size below minimum.
   - Overlapping windows if no overlap policy is implemented.
8. Warning behavior:
   - NaN, infinity, and invalid timestamps are dropped with warnings and
     effective counts.
   - Imbalanced sample sizes produce a caution warning.
   - Low unique ratio produces a discrete/tie caution.
   - `multiple_testing_correction != "none"` is recorded but not applied.
9. Backend failure:
   - Simulate missing/failed `scipy.stats.epps_singleton_2samp` or singular
     backend output.
   - Assert the public detector returns `severity="error"` or `"watch"` with
     `drift_detected=None` and a clear warning.

Recommended commands after implementation:

```text
python -m py_compile drift_algorithm\methods\batchdistributioncomparison.py
python -m pytest tests\test_epps_singleton_test.py
python -m pytest tests\test_energy_distance.py tests\test_levene_s_test.py
```

Manual review before marking implementation complete:

- Confirm public function signature matches the common contract.
- Confirm canonical measurement names match
  `drift_method_variant_measurement_summary.csv`.
- Confirm supported variants call `scipy.stats.epps_singleton_2samp`.
- Confirm resolved `t_points` default to `(0.4, 0.8)` and are recorded.
- Confirm the decision rule is strict `p_value < alpha`.
- Confirm `DISCRETE_EPPS_SINGLETON` does not accept nonnumeric categories or
  count tables.
- Confirm `ASYMPTOTIC_EPPS_SINGLETON` is either explicitly deferred or manager
  approved as an alias before implementation.
- Confirm interpretation text avoids root-cause, performance-degradation, and
  supervised concept-drift claims without labeled evidence.

## 13. Manager Review Points

- First implementation scope is intentionally limited to univariate numeric
  reference/current `(time, value)` windows.
- Default variant is `TWO_SAMPLE_EPPS_SINGLETON` using
  `scipy.stats.epps_singleton_2samp` with `t_points=(0.4, 0.8)`.
- Drift decision is p-value based only: strict `p_value < alpha`, default
  `alpha=0.05`.
- `DISCRETE_EPPS_SINGLETON` is implementation-ready only for discrete-like
  numeric values; categorical/count-table input remains out of scope.
- `ASYMPTOTIC_EPPS_SINGLETON` remains deferred as a separately named screening
  variant unless manager review approves aliasing it to the SciPy-backed
  two-sample variant.
- The public target is `detect_epps_singleton_test` in
  `drift_algorithm.methods.batchdistributioncomparison`.
