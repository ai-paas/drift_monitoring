# DM-017 Baumgartner-Weiss-Schindler Test Design

## Sprint 49 Implementation Note

Sprint 49 promotes `BWS_EXACT_OR_ASYMPTOTIC` from deferred status for the server demo path. It executes through the local permutation BWS engine over reference/current windows and records `execution_policy="permutation_bws_reference_current"` in metadata. Older deferred-status notes in this document are superseded for the harness/runtime path.

## 1. Method Identity

- Method ID: `DM-017`
- Method name: `Baumgartner-Weiss-Schindler Test`
- Category: `BatchDistributionComparison`
- Method kind: `detector`
- Status: `confirmed`
- Source catalog: `drift_methods_catalog.md`
- Source variant document:
  `algorithm_variants/baumgartner_weiss_schindler_test_algorithm_variants.md`
- Source parameter tables:
  - `drift_method_variant_links.csv`
  - `drift_method_variant_measurement_summary.csv`
  - `drift_method_variant_parameters.csv`
  - `drift_method_parameter_guide.md`

The first implementation is a univariate numeric batch detector. It compares a
reference window and current window with a rank-based Baumgartner-Weiss-
Schindler style two-sample statistic.

## 2. Purpose

`Baumgartner-Weiss-Schindler Test` answers whether a scalar numeric monitoring
signal has a different distribution in the current window than in the reference
window. The catalog input is rank-based two-sample comparison; the catalog
outputs are BWS statistic and p-value.

Use this method when:

- the signal is scalar numeric data such as score, latency, loss, residual,
  confidence, calibration error, or a numeric feature
- reference and current windows are both available
- the monitoring question concerns full distribution change rather than only
  mean, variance, or one threshold crossing
- rank-based sensitivity to cumulative distribution differences is acceptable
- a permutation p-value or externally calibrated statistic threshold is
  acceptable for the first implementation

Do not use the first implementation for categorical labels, count tables,
probability vectors, embeddings, multivariate features, text, SHAP matrices, or
supervised error streams. Those require other method families or schemas.

## 3. Supported Variants

Supported for the first implementation:

- `BWS_TWO_SAMPLE`
  - Default variant.
  - Compares reference and current numeric samples directly.
  - Computes a local rank-based BWS two-sample statistic.
  - Uses permutation p-value by default because SciPy does not provide a stable
    public BWS test function.
  - Can use threshold-only decision mode when explicitly requested.
- `BWS_RANK_BASED`
  - Alias-style supported variant in the first implementation.
  - Runs the same local two-sample rank statistic and p-value policy as
    `BWS_TWO_SAMPLE`.
  - Exists to preserve the catalog distinction that the detector is explicitly
    rank-based.

Deferred variants that must return `severity="not_applicable"` until their
extra contract is approved:

- `BWS_EXACT_OR_ASYMPTOTIC`
  - The variant is conceptually valid but not implementation-ready as an exact
    or asymptotic p-value backend in the first phase.
  - Exact BWS p-values require a reviewed finite-sample distribution or dynamic
    programming/enumeration policy, tie behavior, maximum sample-size guardrail,
    and validation fixtures.
  - Asymptotic BWS p-values require an approved approximation formula and
    calibration checks.
  - Until that review is complete, requests for this variant must not silently
    fall back to permutation under the exact/asymptotic name.

Default variant selection:

```text
if params["variant_id"] is omitted:
    variant_id = "BWS_TWO_SAMPLE"
```

## 4. Input Schema

Use the common `pandas.DataFrame` input boundary from
`../input_output_contracts.md`.

Public function shape:

```python
def detect_baumgartner_weiss_schindler_test(
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
| `variant_id` | string | `BWS_TWO_SAMPLE` | all | Variant selector. `BWS_TWO_SAMPLE` and `BWS_RANK_BASED` compute in the first implementation. |
| `alpha` | float | `0.05` | supported variants | Canonical significance level for the permutation p-value drift rule. |
| `threshold_or_alpha` | float | optional | supported variants | Alias for `alpha` in p-value mode; statistic threshold in threshold mode. |
| `significance_level` | float | optional | supported variants | Alias for `alpha`; if supplied with another alpha alias it must agree. |
| `alternative` | string | `two-sided` | supported variants | First implementation supports only `two-sided`/`both`; BWS is treated as an omnibus distribution test. |
| `p_value_method` | string | `permutation` | supported variants | Accepted values: `permutation`, `none`. `none` requires threshold decision mode. |
| `decision_policy` | string | `p_value` | supported variants | Accepted values: `p_value`, `threshold`. |
| `threshold` | float | optional | supported variants | Required when `decision_policy="threshold"`; compared against the BWS statistic. |
| `input_signal` | string | optional | supported variants | Value column name only when `value_col is None`; otherwise recorded as metadata label. |
| `min_reference_size` | int | `20` | supported variants | Minimum effective reference sample size after invalid rows are dropped. |
| `min_current_size` | int | `20` | supported variants | Minimum effective current sample size after invalid rows are dropped. |
| `nan_policy` | string | `drop` | supported variants | First implementation supports `drop`/`omit` only. |
| `rank_tie_policy` | string | `average_rank_warn` | supported variants | Use average ranks for ties and warn that continuous-test interpretation is weaker. |
| `tie_policy` | string | optional | supported variants | Alias for `rank_tie_policy`; accepted value is `warn_only` or `average_rank_warn`. |
| `permutation_count` | int | `999` | supported variants | Number of label permutations for the Monte Carlo p-value. |
| `random_seed` | int | optional | supported variants | Seed for reproducible permutations. |
| `permutation_max_total_size` | int | `5000` | supported variants | Guardrail for the default permutation implementation. |
| `low_power_sample_size` | int | `50` | supported variants | Warn when either effective sample is below this count but still above the hard minimum. |
| `sample_imbalance_warning_ratio` | float | `10.0` | supported variants | Warn when larger sample size divided by smaller sample size exceeds this ratio. |
| `exact_method` | string | optional | deferred variant | Not supported in the first implementation. |
| `asymptotic_method` | string | optional | deferred variant | Not supported in the first implementation. |
| `multiple_testing_correction` | string | `none` | supported variants | Recorded as metadata only. Correction is not applied inside this single-signal detector. |

Parameter rules:

- `alpha`, `threshold_or_alpha` as alpha, and `significance_level` must be
  numeric and satisfy `0 < value < 1`.
- Alpha aliases must not conflict. Conflicting values return
  `severity="not_applicable"`.
- `decision_policy="p_value"` requires `p_value_method="permutation"` and uses
  `p_value < alpha`.
- `decision_policy="threshold"` requires a finite nonnegative `threshold` or
  `threshold_or_alpha` interpreted as the statistic threshold.
- `p_value_method="none"` is allowed only with `decision_policy="threshold"`.
- `alternative` accepts `"two-sided"` and `"both"` only in the first
  implementation.
- `nan_policy` supports `"drop"` and `"omit"` as aliases for dropping invalid
  rows. Other values return not applicable.
- `rank_tie_policy` supports `"average_rank_warn"` only. `tie_policy` may be
  accepted as an alias for existing module consistency.
- `permutation_count`, `permutation_max_total_size`,
  `min_reference_size`, `min_current_size`, and `low_power_sample_size` must be
  positive integers.
- `sample_imbalance_warning_ratio` must be numeric and at least `1`.
- `multiple_testing_correction != "none"` adds a warning and is recorded in
  metadata, but the p-value is not corrected by this detector.
- `exact_method` and `asymptotic_method` are valid catalog parameters only for
  the deferred `BWS_EXACT_OR_ASYMPTOTIC` variant. Supplying either with a
  supported first-phase variant should add a warning that the local permutation
  backend is used instead.
- Reject or warn on unrelated params such as `feature_cols`, `category_col`,
  `count_col`, `embedding_cols`, label columns, covariance settings,
  classifier settings, binning settings, or paired-sample settings.

## 6. Statistic and P-value Policy

SciPy does not expose a standard public `baumgartner_weiss_schindler` or `bws`
two-sample test function. The first implementation must therefore use a local
statistic and an explicit p-value policy.

Statistic definition for two samples with sizes `n` and `m`:

```text
N = n + m
pooled_ranks = average ranks of pooled reference/current values, 1-based
R_i = pooled rank of the i-th sorted reference value
S_j = pooled rank of the j-th sorted current value

B_ref = (1 / n) * sum_i [
    ((R_i - ((N + 1) * i / n)) ** 2)
    / (((i / (n + 1)) * (1 - i / (n + 1))) * (m * (N + 1) / n))
]

B_cur = (1 / m) * sum_j [
    ((S_j - ((N + 1) * j / m)) ** 2)
    / (((j / (m + 1)) * (1 - j / (m + 1))) * (n * (N + 1) / m))
]

TEST_STATISTIC = 0.5 * (B_ref + B_cur)
```

Implementation notes:

- Sort reference and current values independently before assigning `i` and `j`.
- Assign average pooled ranks for ties. Ties are allowed but must produce a
  warning because the continuous-rank null interpretation is weaker.
- The statistic is nonnegative. Larger values indicate stronger rank-based
  distribution difference, but the value is method-specific and must not be
  compared directly with KS, Anderson-Darling, CvM, Kuiper, or Mann-Whitney
  statistics.
- If implementation review determines the denominator convention must be
  adjusted to match a specific published BWS normalization, update this design
  before coding tests. Do not mix normalizations across p-value calibration
  fixtures.

Default p-value policy:

```text
observed = bws_statistic(reference, current)
for each permutation:
    shuffle pooled values
    split into reference-sized and current-sized groups
    compute permuted BWS statistic
p_value = (count(permuted_statistic >= observed) + 1) / (permutation_count + 1)
```

This permutation policy is the first implementation default because it is
explicit, reproducible with `random_seed`, and supports unequal sample sizes.
It is slower than an asymptotic formula but avoids pretending that a SciPy exact
or asymptotic backend exists.

Exact/asymptotic policy:

- `p_value_method="exact"` is not supported for first implementation supported
  variants.
- `p_value_method="asymptotic"` is not supported for first implementation
  supported variants.
- `BWS_EXACT_OR_ASYMPTOTIC` returns not applicable until exact and asymptotic
  backends are separately reviewed.
- Threshold mode is allowed only when the caller supplies an externally
  calibrated statistic threshold.

## 7. Output Measurements

`drift_method_variant_measurement_summary.csv` maps all DM-017 variants to:

```text
TEST_STATISTIC
P_VALUE
DRIFT_ALARM_STATE
```

Return these canonical measurements for every successful supported run:

```python
{
    "TEST_STATISTIC": <float BWS statistic>,
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
    "BWS_REFERENCE_COMPONENT": <float>,
    "BWS_CURRENT_COMPONENT": <float>,
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
method_id = "DM-017"
method_name = "Baumgartner-Weiss-Schindler Test"
method_category = "BatchDistributionComparison"
variant_id = "BWS_TWO_SAMPLE" or "BWS_RANK_BASED"
drift_score = TEST_STATISTIC
p_value = P_VALUE
test_statistic = TEST_STATISTIC
threshold = alpha for p-value mode, statistic threshold for threshold mode
drift_detected = p_value < alpha or TEST_STATISTIC > threshold when applicable
```

The BWS components and descriptive summaries are interpretation helpers. They
must not replace the documented alarm rule.

Interpretation text should state:

- which variant ran
- reference/current effective sample sizes
- BWS statistic value
- p-value and alpha, or statistic threshold when threshold mode is used
- whether the result crossed the drift rule
- median or quartile movement as descriptive context when available
- that the result is a numeric distribution drift candidate, not proof of root
  cause, model performance degradation, or supervised concept drift

## 8. Algorithm Steps

1. Normalize `params` to an empty dict when omitted.
2. Resolve `variant_id`; default to `BWS_TWO_SAMPLE`.
3. Reject `BWS_EXACT_OR_ASYMPTOTIC` and unknown variants with
   `severity="not_applicable"` and a warning naming the unsupported variant.
4. Resolve `decision_policy`, `alpha` and alpha aliases, `threshold`,
   `alternative`, `p_value_method`, `nan_policy`, `rank_tie_policy`,
   `permutation_count`, `random_seed`, sample-size minima, and the value
   column.
5. Validate that both reference and current windows are supplied and parseable.
6. Validate required columns and scalar numeric value data. Boolean data is not
   valid numeric BWS input.
7. Convert and sort the DataFrame according to the common window handling
   contract.
8. Slice inclusive reference and current windows.
9. Drop rows with invalid timestamps or non-finite values; record original and
   effective counts.
10. If either effective sample is empty or below minimum, return not
    applicable.
11. Convert the two effective samples to one-dimensional
    `numpy.ndarray[float64]` objects.
12. Add warnings for ties, highly imbalanced sample sizes, low-power sample
    sizes, autocorrelation concerns, low permutation count, and
    multiple-testing metadata when applicable.
13. Compute the local BWS statistic, `BWS_REFERENCE_COMPONENT`, and
    `BWS_CURRENT_COMPONENT`.
14. If `decision_policy="p_value"`, compute the permutation p-value with the
    documented plus-one correction. Enforce `permutation_max_total_size` before
    running permutations.
15. If `decision_policy="threshold"`, skip p-value unless explicitly requested
    by a future design and compare the statistic to the resolved threshold.
16. Convert statistic, p-value, and component values to Python floats; guard
    against NaN/inf and p-values outside `[0, 1]`.
17. Compute descriptive summaries: effective sample counts, means, medians,
    25th/75th percentiles, and median delta.
18. Apply the drift decision rule from section 9.
19. Build `DriftResult` with method identity, variant, canonical measurements,
    helper summaries, counts, windows, parameters, warnings, and concise
    interpretation text.

## 9. Drift Decision Rule

Null hypothesis for the first implementation:

```text
reference and current numeric samples are exchangeable draws from the same
continuous distribution.
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
- unsupported `decision_policy`, `alternative`, `p_value_method`,
  `nan_policy`, `rank_tie_policy`, `tie_policy`, `min_reference_size`,
  `min_current_size`, `low_power_sample_size`, `permutation_count`,
  `permutation_max_total_size`, `sample_imbalance_warning_ratio`, or
  `random_seed`
- `decision_policy="threshold"` without a finite nonnegative threshold
- `decision_policy="p_value"` with total effective sample size above
  `permutation_max_total_size`
- `p_value_method="exact"` or `"asymptotic"` for first-phase supported variants
- current/reference window overlap when overlap policy is not explicitly
  defined by the implementation
- `BWS_EXACT_OR_ASYMPTOTIC` until exact/asymptotic p-value contracts are
  approved
- local calculation returns non-finite statistic, non-finite p-value, or
  p-value outside `[0, 1]`

Return `severity="normal"` or `severity="drift_detected"` with warnings when the
method can still run but interpretation needs caution:

- timestamps or values were dropped because they were invalid or non-finite
- duplicate values or ties are present, requiring average ranks and weakening
  continuous-distribution interpretation
- reference/current sample sizes are highly imbalanced
- `permutation_count` is low enough that Monte Carlo p-value resolution is
  coarse
- either effective sample size is below `low_power_sample_size`
- observations are repeated or autocorrelated time-series rows rather than
  independent samples
- sample extraction, traffic mix, seasonality, or segment definitions differ
  between windows
- `multiple_testing_correction` is not `"none"`; record that this detector does
  not apply correction internally
- threshold mode is used; warn that the threshold must come from external
  calibration and is not a p-value
- `exact_method` or `asymptotic_method` is supplied with a supported first-phase
  variant but ignored in favor of the documented local permutation backend

Unexpected implementation exceptions should return `severity="error"` or
`"watch"` according to project convention, with `drift_detected=None` and a
clear warning, without raising through the public detector boundary.

Do not silently coerce categorical values, boolean flags, labels, embeddings,
lists, or objects into the numeric BWS detector.

## 11. Implementation Target

```text
module: drift_algorithm.methods.batchdistributioncomparison
function: detect_baumgartner_weiss_schindler_test
```

The module should expose `detect_baumgartner_weiss_schindler_test` through the
same package path used by the other batch distribution methods. If the concrete
package later separates one method per file, keep this public import path stable
or add a compatibility import.

Expected dependencies:

```text
pandas
numpy
```

No SciPy dependency is required for the first BWS implementation because the
two-sample statistic and permutation p-value are implemented locally.

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
- keep method-specific BWS statistic and permutation helpers private to the
  module unless another numeric batch method later shares them
- record local backend name, decision policy, p-value method, permutation count,
  random seed, `alpha`, threshold, value column, effective windows, sample-size
  metadata, and unsupported/deferred variant decisions so the result is
  auditable

Suggested private helper shape:

```python
def _bws_two_sample_statistic(
    reference_values: np.ndarray,
    current_values: np.ndarray,
) -> tuple[float, float, float]:
    """Return statistic, reference_component, current_component."""

def _bws_permutation_p_value(
    reference_values: np.ndarray,
    current_values: np.ndarray,
    *,
    observed_statistic: float,
    permutation_count: int,
    random_seed: int | None,
) -> float:
    ...
```

## 12. Verification Plan

Unit tests for the first implementation:

1. Default two-sample no-drift:
   - Generate reference/current numeric samples from the same distribution with
     a deterministic seed.
   - Omit `variant_id` and assert `variant_id == "BWS_TWO_SAMPLE"`.
   - Assert `TEST_STATISTIC`, `P_VALUE`, `DRIFT_ALARM_STATE`, `SAMPLE_SIZE`,
     `SAMPLE_SIZE_REFERENCE`, `SAMPLE_SIZE_CURRENT`,
     `BWS_REFERENCE_COMPONENT`, and `BWS_CURRENT_COMPONENT` exist.
   - Assert `drift_detected is False` and `severity == "normal"` for a seed
     chosen to keep `p_value >= 0.05`.
2. Rank-based supported variant:
   - Run the same data with `variant_id="BWS_RANK_BASED"`.
   - Assert it uses the same local statistic/p-value policy as
     `BWS_TWO_SAMPLE` and records the requested variant id.
3. Two-sample drift candidate:
   - Generate reference normal samples and current samples with a location,
     scale, or shape shift.
   - Use a deterministic `random_seed` and enough `permutation_count` for a
     stable test.
   - Assert `p_value < alpha`, `drift_detected is True`,
     `severity == "drift_detected"`, and canonical measurements are populated.
4. Threshold decision mode:
   - Supply `decision_policy="threshold"`, `p_value_method="none"`, and a fixed
     threshold.
   - Assert p-value is `None`, `DRIFT_ALARM_STATE` follows
     `TEST_STATISTIC > threshold`, and threshold mode warning/metadata are
     recorded.
5. Statistic helper correctness:
   - Compare a tiny hand-calculated fixture against expected BWS statistic,
     reference component, and current component.
   - Assert identical samples produce a small statistic and a high permutation
     p-value under a deterministic seed.
   - Assert tied data uses average ranks and records a tie warning.
6. Parameter alias and validation:
   - Assert `threshold_or_alpha` and `significance_level` route to `alpha` in
     p-value mode.
   - Assert `threshold_or_alpha` routes to statistic threshold in threshold
     mode.
   - Assert conflicting alpha aliases return `severity="not_applicable"`.
   - Assert unsupported `alternative`, `p_value_method`, `rank_tie_policy`, and
     malformed permutation settings return not applicable.
7. Schema and window validation:
   - Missing value column.
   - Non-numeric, boolean, object/list, or categorical value column.
   - Missing reference/current windows.
   - Empty current/reference slices.
   - Effective sample size below minimum.
   - Overlapping windows if no overlap policy is implemented.
8. Deferred variants:
   - `BWS_EXACT_OR_ASYMPTOTIC` returns `severity="not_applicable"` with a
     warning about missing exact/asymptotic p-value backend approval.
   - Requests for `p_value_method="exact"` or `"asymptotic"` return not
     applicable for supported first-phase variants.
9. Warning behavior:
   - NaN, infinity, and invalid timestamps are dropped with warnings and
     effective counts.
   - Ties/repeated values compute with a caution warning.
   - Highly imbalanced sample sizes produce warning metadata.
   - Low `permutation_count` produces a Monte Carlo resolution warning.
   - `multiple_testing_correction != "none"` is recorded but not applied.
10. Permutation guardrail:
    - Set total effective sample size above `permutation_max_total_size` in
      p-value mode and assert not applicable.
    - Assert the same data can run in threshold mode when a threshold is
      supplied.
11. Backend/local failure:
    - Simulate a local helper exception or non-finite statistic.
    - Assert the public detector returns `severity="error"` or `"watch"` with
      `drift_detected=None` and a clear warning.

Recommended commands after implementation:

```text
python -m py_compile drift_algorithm\methods\batchdistributioncomparison.py
python -m pytest tests\test_baumgartner_weiss_schindler_test.py
python -m pytest tests\test_kuiper_s_test.py tests\test_cramer_von_mises_test.py
```

Manual review before marking implementation complete:

- Confirm public function signature matches the common contract.
- Confirm canonical measurement names match
  `drift_method_variant_measurement_summary.csv`.
- Confirm `BWS_EXACT_OR_ASYMPTOTIC` and exact/asymptotic p-value requests fail
  explicitly instead of falling through to permutation under a misleading name.
- Confirm the local statistic normalization is locked to the same formula used
  by tests and p-value calibration.
- Confirm permutation p-value uses the plus-one correction and records
  reproducibility metadata.
- Confirm interpretation text avoids root-cause, performance-degradation, and
  supervised concept-drift claims without labeled evidence.
- Confirm `git diff` only changes
  `drift_algorithm/docs/method_designs/DM-017_baumgartner_weiss_schindler_test.md`.

## 13. Manager Review Points

- First implementation scope is intentionally limited to univariate numeric
  reference/current `(time, value)` windows.
- `BWS_TWO_SAMPLE` and `BWS_RANK_BASED` are implementation-ready through a local
  rank statistic plus permutation p-value.
- `BWS_EXACT_OR_ASYMPTOTIC`, `p_value_method="exact"`, and
  `p_value_method="asymptotic"` are deferred until the exact/asymptotic backend
  and calibration fixtures are approved.
- SciPy is not treated as the BWS backend.
- Threshold mode is allowed only as an explicit fallback with an externally
  calibrated statistic threshold.
- The public target is `detect_baumgartner_weiss_schindler_test` in
  `drift_algorithm.methods.batchdistributioncomparison`.
- Drift decision is strictly `p_value < alpha` in p-value mode or
  `TEST_STATISTIC > threshold` in threshold mode; descriptive summaries do not
  override the alarm.
