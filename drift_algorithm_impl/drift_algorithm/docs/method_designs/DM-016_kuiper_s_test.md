# DM-016 Kuiper's Test Design

## Sprint 49 Implementation Note

Sprint 49 promotes `KUIPER_CIRCULAR_DATA` and `KUIPER_ONE_SAMPLE` from deferred status for the server demo path. They execute through the local two-sample Kuiper engine over reference/current windows and record `execution_policy="two_sample_kuiper_reference_current"` in metadata. Older deferred-status notes in this document are superseded for the harness/runtime path.

## 1. Method Identity

- Method ID: `DM-016`
- Method name: `Kuiper's Test`
- Category: `BatchDistributionComparison`
- Method kind: `detector`
- Status: `확정`
- Source catalog: `drift_methods_catalog.md`
- Source variant document: `algorithm_variants/kuiper_s_test_algorithm_variants.md`
- Source parameter tables:
  - `drift_method_variant_links.csv`
  - `drift_method_variant_measurement_summary.csv`
  - `drift_method_variant_parameters.csv`
  - `drift_method_parameter_guide.md`

The first implementation is a univariate numeric batch detector. It compares
the empirical cumulative distribution of a current window against a reference
window with a two-sample Kuiper statistic.

## 2. Purpose

`Kuiper's Test` answers whether a scalar numeric monitoring signal has a
different distribution in the current window than in the reference window. The
catalog input is `numeric 또는 circular sample`; the catalog outputs are
`Kuiper statistic` and `p-value`.

Use this method when:

- the signal is scalar numeric data such as score, latency, loss, residual,
  confidence, calibration error, or a numeric feature
- reference and current windows are both available
- the monitoring question concerns full empirical distribution change
- upper and lower empirical CDF gaps should both contribute to the score
- a permutation p-value or explicit statistic threshold is acceptable

Do not use the first implementation for categorical labels, count tables,
probability vectors, embeddings, multivariate features, text, SHAP matrices,
supervised error streams, or true circular features that require wrap-around
normalization. Those require other method families or a later Kuiper variant
contract.

## 3. Supported Variants

Supported for the first implementation:

- `KUIPER_TWO_SAMPLE`
  - Default variant.
  - Compares reference and current numeric samples directly.
  - Computes the two-sample Kuiper statistic from empirical CDF gaps.
  - Uses a local implementation because SciPy does not provide a stable public
    two-sample Kuiper test function.
  - Uses permutation p-value by default; can use a threshold-only policy when
    explicitly requested.

Deferred variants that must return `severity="not_applicable"` until their
extra contracts are implemented:

- `KUIPER_CIRCULAR_DATA`
  - Requires an explicit circular value scale, period, phase origin, and
    wrap-around policy. The common numeric `(time, value)` contract alone is
    not enough to distinguish ordinary scalar values from circular coordinates.
- `KUIPER_ONE_SAMPLE`
  - Requires a named theoretical CDF, a fitted baseline distribution, or a
    fixed reference CDF plus a clear parameter estimation policy. The first
    reference/current window contract is a two-sample contract, not a one-sample
    goodness-of-fit contract.

Default variant selection:

```text
if params["variant_id"] is omitted:
    variant_id = "KUIPER_TWO_SAMPLE"
```

## 4. Input Schema

Use the common `pandas.DataFrame` input boundary from
`../input_output_contracts.md`.

Public function shape:

```python
def detect_kuiper_s_test(
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
values, not arrays, objects, strings, categories, booleans, labels, circular
phase strings, or probability vectors.

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
| `variant_id` | string | `KUIPER_TWO_SAMPLE` | all | Variant selector. Only `KUIPER_TWO_SAMPLE` computes in the first implementation. |
| `alpha` | float | `0.05` | supported variant | Canonical significance level for the permutation p-value drift rule. |
| `threshold_or_alpha` | float | optional | supported variant | Alias for `alpha` when `decision_policy="p_value"`; statistic threshold when `decision_policy="threshold"`. |
| `significance_level` | float | optional | supported variant | Alias for `alpha`; if supplied with another alpha alias it must agree. |
| `alternative` | string | `two-sided` | supported variant | First implementation supports only `two-sided`/`both`; Kuiper already combines positive and negative CDF gaps. |
| `p_value_method` | string | `permutation` | supported variant | Accepted values: `permutation`, `none`. `none` requires threshold-based decision. |
| `decision_policy` | string | `p_value` | supported variant | Accepted values: `p_value`, `threshold`. |
| `threshold` | float | optional | supported variant | Required when `decision_policy="threshold"`; compared against the Kuiper statistic. |
| `input_signal` | string | optional | supported variant | Value column name only when `value_col is None`; otherwise recorded as metadata label. |
| `min_reference_size` | int | `20` | supported variant | Minimum effective reference sample size after invalid rows are dropped. |
| `min_current_size` | int | `20` | supported variant | Minimum effective current sample size after invalid rows are dropped. |
| `nan_policy` | string | `drop` | supported variant | First implementation supports `drop`/`omit` only. |
| `tie_policy` | string | `warn_only` | supported variant | First implementation computes with ties but warns because continuous-test p-value interpretation is weaker. |
| `permutation_count` | int | `999` | supported variant | Number of label permutations for the Monte Carlo p-value. |
| `random_seed` | int | optional | supported variant | Seed for reproducible permutations. |
| `permutation_max_total_size` | int | `5000` | supported variant | Guardrail for the default permutation implementation. Larger samples return not applicable unless threshold mode is used. |
| `circular_data_policy` | string | `not_supported` | deferred variants | Must remain `not_supported` for the first implementation. |
| `multiple_testing_correction` | string | `none` | supported variant | Recorded as metadata only. Correction is not applied inside this single-signal detector. |

Parameter rules:

- `alpha`, `threshold_or_alpha` as alpha, and `significance_level` must be
  numeric and satisfy `0 < value < 1`.
- Alpha aliases must not conflict. Conflicting values return
  `severity="not_applicable"`.
- `decision_policy="p_value"` requires `p_value_method="permutation"` and uses
  `p_value < alpha`.
- `decision_policy="threshold"` requires a finite nonnegative `threshold` or
  `threshold_or_alpha` interpreted as the statistic threshold; p-value may be
  omitted.
- `alternative` accepts `"two-sided"` and `"both"` only in the first
  implementation.
- `p_value_method="none"` is allowed only with `decision_policy="threshold"`.
- `nan_policy` supports `"drop"` and `"omit"` as aliases for dropping invalid
  rows. Other values return not applicable.
- `tie_policy` supports `"warn_only"` only.
- `permutation_count` and `permutation_max_total_size` must be positive
  integers.
- `circular_data_policy` must be `"not_supported"` unless
  `KUIPER_CIRCULAR_DATA` is later implemented.
- `multiple_testing_correction != "none"` adds a warning and is recorded in
  metadata, but the p-value is not corrected by this detector.
- Reject or warn on unrelated params such as `feature_cols`, `category_col`,
  `count_col`, `embedding_cols`, label columns, covariance settings,
  classifier settings, binning settings, or paired-sample settings.

Statistic implementation policy:

```text
pooled_sorted = sorted unique values from reference and current
F_ref(x) = fraction of reference values <= x
F_cur(x) = fraction of current values <= x
D_plus = max_x(F_ref(x) - F_cur(x))
D_minus = max_x(F_cur(x) - F_ref(x))
KUIPER_STATISTIC = D_plus + D_minus
```

Use vectorized `numpy.searchsorted` or equivalent sorted-array logic. The
statistic is in `[0, 2]`; for ordinary two-sample EDF comparisons it is usually
in `[0, 1]`, but the implementation should not hard-code a narrower range
unless mathematically guaranteed by the chosen evaluation grid.

P-value policy:

```text
observed = kuiper_statistic(reference, current)
for each permutation:
    shuffle pooled values
    split into reference-sized and current-sized groups
    compute permuted Kuiper statistic
p_value = (count(permuted_statistic >= observed) + 1) / (permutation_count + 1)
```

This permutation policy is the first implementation default because there is no
project-approved SciPy backend for two-sample Kuiper p-values. It is slower than
an asymptotic approximation but is explicit, reproducible with `random_seed`,
and works for unequal sample sizes. If `permutation_count` is too small, add a
warning that the p-value has high Monte Carlo error.

## 6. Output Measurements

`drift_method_variant_measurement_summary.csv` maps all DM-016 variants to:

```text
TEST_STATISTIC
P_VALUE
DRIFT_ALARM_STATE
```

Return these canonical measurements for every successful supported run:

```python
{
    "TEST_STATISTIC": <float Kuiper statistic>,
    "P_VALUE": <float in [0, 1] | None>,
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
    "KUIPER_D_PLUS": <float>,
    "KUIPER_D_MINUS": <float>,
    "REFERENCE_MEAN": <float>,
    "CURRENT_MEAN": <float>,
    "REFERENCE_MEDIAN": <float>,
    "CURRENT_MEDIAN": <float>,
    "REFERENCE_Q25": <float>,
    "CURRENT_Q25": <float>,
    "REFERENCE_Q75": <float>,
    "CURRENT_Q75": <float>,
    "MEDIAN_DELTA": <current median - reference median>,
    "PERMUTATION_COUNT": <int | None>,
}
```

Top-level `DriftResult` field mapping:

```text
method_id = "DM-016"
method_name = "Kuiper's Test"
method_category = "BatchDistributionComparison"
variant_id = "KUIPER_TWO_SAMPLE"
drift_score = TEST_STATISTIC
p_value = P_VALUE
test_statistic = TEST_STATISTIC
threshold = alpha for p-value mode, statistic threshold for threshold mode
drift_detected = p_value < alpha or TEST_STATISTIC > threshold when applicable
```

The D-plus, D-minus, mean, median, quartile, and median delta measurements are
interpretation helpers. They must not replace the documented alarm rule.

Interpretation text should state:

- which variant ran
- reference/current effective sample sizes
- Kuiper statistic value
- D-plus and D-minus values when available
- p-value and alpha, or statistic threshold when threshold mode is used
- whether the result crossed the drift rule
- median or quartile movement as descriptive context when available
- that the result is a numeric distribution drift candidate, not proof of root
  cause, model performance degradation, or supervised concept drift

## 7. Algorithm Steps

1. Normalize `params` to an empty dict when omitted.
2. Resolve `variant_id`; default to `KUIPER_TWO_SAMPLE`.
3. Reject deferred or unknown variants with `severity="not_applicable"` and a
   warning naming the unsupported variant.
4. Resolve `decision_policy`, `alpha` and alpha aliases, `threshold`,
   `alternative`, `p_value_method`, `nan_policy`, `tie_policy`,
   `permutation_count`, `random_seed`, sample-size minima, and the value column.
5. Validate that both reference and current windows are supplied and parseable.
6. Validate required columns and scalar numeric value data. Boolean data is not
   valid numeric Kuiper input.
7. Convert and sort the DataFrame according to the common window handling
   contract.
8. Slice inclusive reference and current windows.
9. Drop rows with invalid timestamps or non-finite values; record original and
   effective counts.
10. If either effective sample is empty or below minimum, return not
    applicable.
11. Convert the two effective samples to one-dimensional
    `numpy.ndarray[float64]` objects.
12. Add warnings for ties, highly imbalanced sample sizes, autocorrelation
    concerns, low permutation count, and multiple-testing metadata when
    applicable.
13. Compute the local two-sample Kuiper statistic, `KUIPER_D_PLUS`, and
    `KUIPER_D_MINUS`.
14. If `decision_policy="p_value"`, compute the permutation p-value with the
    documented plus-one correction. Enforce `permutation_max_total_size` before
    running permutations.
15. If `decision_policy="threshold"`, skip p-value unless explicitly enabled in
    a future version and compare the statistic to the resolved threshold.
16. Convert statistic, p-value, D-plus, and D-minus to Python floats; guard
    against NaN/inf and p-values outside `[0, 1]`.
17. Compute descriptive summaries: effective sample counts, means, medians,
    25th/75th percentiles, and median delta.
18. Apply the drift decision rule from section 8.
19. Build `DriftResult` with method identity, variant, canonical measurements,
    helper summaries, counts, windows, parameters, warnings, and concise
    interpretation text.

## 8. Drift Decision Rule

Null hypothesis for the first implementation:

```text
reference and current numeric samples are exchangeable draws from the same
distribution.
```

Alternative hypothesis:

```text
reference and current numeric samples are not drawn from the same distribution.
```

Primary rule for `decision_policy="p_value"`:

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

Fallback rule for `decision_policy="threshold"`:

```text
if threshold is None:
    drift_detected = None
    severity = "watch"
elif TEST_STATISTIC > threshold:
    drift_detected = True
    severity = "drift_detected"
else:
    drift_detected = False
    severity = "normal"
```

Use strict `> threshold`, not `>= threshold`. Equality is not drift.

For report wording:

- `drift_detected=True`: "numeric distribution drift candidate"
- `drift_detected=False`: "no statistically significant numeric distribution
  change under this window, variant, and decision policy"
- `drift_detected=None`: method was not applicable, threshold was missing, or
  calculation failed

The Kuiper statistic is method-specific. A larger statistic generally means
larger combined upward and downward empirical CDF gaps, but it must not be
compared directly with KS, Anderson-Darling, Cramer-von Mises, chi-square,
Wasserstein, or circular Kuiper values without method and variant context.

## 9. Warnings and Not-Applicable Conditions

Return `severity="not_applicable"` and `drift_detected=None` for:

- missing `time_col`
- missing resolved value column
- non-datetime-coercible `time_col`
- nonnumeric, boolean, object, array, category, label, embedding, circular
  phase string, or text value data
- omitted or unparseable `reference_window` or `current_window`
- empty reference or current window after slicing
- no finite numeric values after invalid rows are handled
- effective reference or current sample size below minimum
- unsupported or deferred `variant_id`
- invalid `alpha` or conflicting alpha aliases
- unsupported `decision_policy`, `alternative`, `p_value_method`,
  `nan_policy`, `tie_policy`, `min_reference_size`, `min_current_size`,
  `permutation_count`, `permutation_max_total_size`, or `random_seed`
- `decision_policy="threshold"` without a finite nonnegative threshold
- `decision_policy="p_value"` with total effective sample size above
  `permutation_max_total_size`, unless the implementation later adds an
  approved approximation
- current/reference window overlap when overlap policy is not explicitly
  defined by the implementation
- `KUIPER_CIRCULAR_DATA` without an approved circular scale, period, origin,
  and wrap-around contract
- `KUIPER_ONE_SAMPLE` without a fully specified theoretical or fitted CDF
  contract
- backend or local calculation returns non-finite statistic, non-finite p-value,
  or p-value outside `[0, 1]`

Return `severity="normal"` or `severity="drift_detected"` with warnings when the
method can still run but interpretation needs caution:

- timestamps or values were dropped because they were invalid or non-finite
- duplicate values or ties are present, weakening continuous-distribution
  interpretation
- reference/current sample sizes are highly imbalanced
- `permutation_count` is low enough that Monte Carlo p-value resolution is
  coarse
- either effective sample size is below a configurable low-power warning
  threshold, if implemented
- observations are repeated or autocorrelated time-series rows rather than
  independent samples
- sample extraction, traffic mix, seasonality, or segment definitions differ
  between windows
- `multiple_testing_correction` is not `"none"`; record that this detector does
  not apply correction internally
- threshold mode is used; warn that the threshold must come from external
  calibration and is not a p-value

Unexpected implementation exceptions should return `severity="error"` or
`severity="watch"` according to project convention, with `drift_detected=None`
and a clear warning, without raising through the public detector boundary.

Do not silently coerce categorical values, boolean flags, labels, embeddings,
lists, objects, or circular phase labels into the numeric Kuiper detector.

## 10. Implementation Target

```text
module: drift_algorithm.methods.batchdistributioncomparison
function: detect_kuiper_s_test
```

The module should expose `detect_kuiper_s_test` through the same package path
used by the other batch distribution methods. If the concrete package later
separates one method per file, keep this public import path stable or add a
compatibility import.

Expected dependencies:

```text
pandas
numpy
```

No SciPy dependency is required for the first Kuiper implementation because the
two-sample statistic and permutation p-value are implemented locally.

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
- use `prepare_numeric_windows` where it matches this contract
- keep method-specific Kuiper statistic and permutation helpers private to the
  module unless another numeric batch method later shares them
- record local backend name, decision policy, p-value method, permutation count,
  random seed, `alpha`, threshold, value column, effective windows, sample-size
  metadata, and unsupported/deferred variant decisions so the result is
  auditable

Suggested private helper shape:

```python
def _kuiper_two_sample_statistic(
    reference_values: np.ndarray,
    current_values: np.ndarray,
) -> tuple[float, float, float]:
    """Return statistic, d_plus, d_minus."""

def _kuiper_permutation_p_value(
    reference_values: np.ndarray,
    current_values: np.ndarray,
    *,
    observed_statistic: float,
    permutation_count: int,
    random_seed: int | None,
) -> float:
    ...
```

## 11. Verification Plan

Unit tests for the first implementation:

1. Default two-sample no-drift:
   - Generate reference/current numeric samples from the same distribution with
     a deterministic seed.
   - Omit `variant_id` and assert `variant_id == "KUIPER_TWO_SAMPLE"`.
   - Assert `TEST_STATISTIC`, `P_VALUE`, `DRIFT_ALARM_STATE`, `SAMPLE_SIZE`,
     `SAMPLE_SIZE_REFERENCE`, `SAMPLE_SIZE_CURRENT`, `KUIPER_D_PLUS`, and
     `KUIPER_D_MINUS` exist.
   - Assert `drift_detected is False` and `severity == "normal"` for a seed
     chosen to keep `p_value >= 0.05`.
2. Two-sample drift candidate:
   - Generate reference normal samples and current samples with a location,
     scale, or shape shift.
   - Use a deterministic `random_seed` and enough `permutation_count` for a
     stable test.
   - Assert `p_value < alpha`, `drift_detected is True`,
     `severity == "drift_detected"`, and canonical measurements are populated.
3. Threshold decision mode:
   - Supply `decision_policy="threshold"`, `p_value_method="none"`, and a fixed
     threshold.
   - Assert p-value is `None`, `DRIFT_ALARM_STATE` follows
     `TEST_STATISTIC > threshold`, and threshold mode warning/metadata are
     recorded.
4. Statistic helper correctness:
   - Compare hand-calculated tiny arrays against expected `D_plus`, `D_minus`,
     and `TEST_STATISTIC`.
   - Assert identical samples produce statistic `0`.
5. Parameter alias and validation:
   - Assert `threshold_or_alpha` and `significance_level` route to `alpha` in
     p-value mode.
   - Assert `threshold_or_alpha` routes to statistic threshold in threshold
     mode.
   - Assert conflicting alpha aliases return `severity="not_applicable"`.
   - Assert unsupported `alternative` and `p_value_method` return not
     applicable.
6. Schema and window validation:
   - Missing value column.
   - Non-numeric, boolean, object/list, circular phase label, or categorical
     value column.
   - Missing reference/current windows.
   - Empty current/reference slices.
   - Effective sample size below minimum.
   - Overlapping windows if no overlap policy is implemented.
7. Deferred variants:
   - `KUIPER_CIRCULAR_DATA` returns `severity="not_applicable"` with a warning
     about missing circular scale/period/origin contract.
   - `KUIPER_ONE_SAMPLE` returns `severity="not_applicable"` with a warning
     about missing CDF/fitted distribution contract.
8. Warning behavior:
   - NaN, infinity, and invalid timestamps are dropped with warnings and
     effective counts.
   - Ties/repeated values compute with a caution warning.
   - Highly imbalanced sample sizes produce warning metadata.
   - Low `permutation_count` produces a Monte Carlo resolution warning.
   - `multiple_testing_correction != "none"` is recorded but not applied.
9. Permutation guardrail:
   - Set total effective sample size above `permutation_max_total_size` in
     p-value mode and assert not applicable.
   - Assert the same data can run in threshold mode when a threshold is
     supplied.
10. Backend/local failure:
   - Simulate a local helper exception or non-finite statistic.
   - Assert the public detector returns `severity="error"` or `"watch"` with
     `drift_detected=None` and a clear warning.

Recommended commands after implementation:

```text
python -m py_compile drift_algorithm\methods\batchdistributioncomparison.py
python -m pytest tests\test_kuiper_s_test.py
python -m pytest tests\test_cramer_von_mises_test.py tests\test_anderson_darling_test.py
```

Manual review before marking implementation complete:

- Confirm public function signature matches the common contract.
- Confirm canonical measurement names match
  `drift_method_variant_measurement_summary.csv`.
- Confirm `KUIPER_CIRCULAR_DATA` and `KUIPER_ONE_SAMPLE` fail explicitly
  instead of falling through to a misleading numeric two-sample calculation.
- Confirm the local statistic evaluates both upward and downward EDF gaps.
- Confirm permutation p-value uses the plus-one correction and records
  reproducibility metadata.
- Confirm interpretation text avoids root-cause, performance-degradation, and
  supervised concept-drift claims without labeled evidence.
- Confirm `git diff` only changes
  `drift_algorithm/docs/method_designs/DM-016_kuiper_s_test.md`.

## 12. Manager Review Points

- First implementation scope is intentionally limited to two-sample univariate
  numeric `(time, value)` Kuiper.
- `KUIPER_CIRCULAR_DATA` and `KUIPER_ONE_SAMPLE` remain cataloged variants but
  are deferred until circular-coordinate or CDF contracts are approved.
- SciPy is not treated as the p-value backend; the design calls for a local EDF
  statistic plus permutation p-value by default.
- Threshold mode is allowed only as an explicit fallback with an externally
  calibrated statistic threshold.
- The public target is `detect_kuiper_s_test` in
  `drift_algorithm.methods.batchdistributioncomparison`.
- Drift decision is strictly `p_value < alpha` in p-value mode or
  `TEST_STATISTIC > threshold` in threshold mode; descriptive summaries do not
  override the alarm.
