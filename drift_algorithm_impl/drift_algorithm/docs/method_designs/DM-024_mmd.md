# DM-024 MMD Design

## 1. Method Identity

- Method ID: `DM-024`
- Method name: `MMD`
- Category: `BatchDistributionComparison`
- Method kind: `detector`
- Status: `확정`
- Source catalog: `drift_methods_catalog.md`
- Source variant document: `algorithm_variants/mmd_algorithm_variants.md`
- Source parameter tables:
  - `drift_method_variant_links.csv`
  - `drift_method_variant_measurement_summary.csv`
  - `drift_method_variant_parameters.csv`
  - `drift_method_parameter_guide.md`

The first implementation is a univariate numeric batch detector. It compares a
reference `(time, value)` window with a current `(time, value)` window using
RBF-kernel Maximum Mean Discrepancy and returns an MMD score. It does not
produce a binary alarm unless a threshold is supplied or the optional
permutation p-value policy is explicitly enabled.

## 2. Purpose

`MMD` answers whether two numeric samples differ in kernel mean embedding
space. For the first implementation, it is a scalar numeric distribution drift
score for model scores, losses, latencies, residuals, confidence values, costs,
or other one-dimensional monitoring signals where a flexible kernel distance is
useful.

The catalog input is `embedding/vector sample`; the catalog output is
`MMD score, p-value optional`. This design intentionally narrows the first
implementation to scalar numeric `(time, value)` windows so the public contract
matches the existing `BatchDistributionComparison` implementation pattern.

Use the first implementation when:

- the monitored signal is one scalar numeric column
- reference and current windows are both available
- an RBF-kernel two-sample distance is desired
- a score-only result is acceptable, or the caller explicitly enables a
  threshold or permutation p-value

Do not use the first implementation for categorical labels, count tables,
probability vectors, raw embeddings, multivariate feature matrices, text, SHAP
matrices, graph embeddings, or supervised error streams. Those require another
method family or a future MMD contract.

## 3. Supported Variants

Supported for the first implementation:

- `KERNEL_MMD_BIASED`
  - Default variant.
  - Uses scalar numeric reference/current windows.
  - Computes the nonnegative biased squared MMD statistic:
    `mean(Kxx) + mean(Kyy) - 2 * mean(Kxy)`, including diagonal terms.
  - Returns score-only by default. No p-value and no binary alarm are produced
    unless a threshold or permutation p-value is explicitly requested.
  - Preferred first default because it is nonnegative, stable for monitoring
    dashboards, and easy to compare across windows when the kernel bandwidth
    policy is fixed.
- `KERNEL_MMD_UNBIASED`
  - Implementation-ready for the same univariate `(time, value)` contract.
  - Computes the unbiased squared MMD statistic by excluding within-sample
    diagonal terms.
  - Requires at least two effective values per window for the statistic and
    uses the same default sample-size minimum as the biased variant.
  - May be slightly negative from finite-sample variance; keep the signed
    value in `TEST_STATISTIC` and use it as the observed score. Do not clamp it
    unless manager review changes this policy.

Implementation-ready optional policy for both supported kernel variants:

- permutation p-value
  - Enabled by `p_value_method="permutation"`.
  - Recomputes the selected MMD statistic after randomly permuting the pooled
    sample into reference/current groups.
  - Uses strict `p_value < alpha` for binary decisions.
  - May be implemented in the same first code pass if runtime guardrails and
    tests are included; otherwise p-value requests must return
    `severity="not_applicable"` with a clear warning that permutation p-values
    are deferred.

Deferred until a separate contract is approved:

- `LINEAR_TIME_MMD`
  - Requires pair construction, approximation variance reporting, sample-order
    policy, and runtime/accuracy guardrails.
  - Must return `severity="not_applicable"` in the first implementation.
- `STREAMING_MMD`
  - Requires window maintenance, reservoir/reference refresh policy,
    update-frequency semantics, and event history output.
  - Must return `severity="not_applicable"` in the first implementation.
- multivariate or embedding MMD under `KERNEL_MMD_BIASED` or
  `KERNEL_MMD_UNBIASED`
  - Requires `feature_cols` or `embedding_cols`, two-dimensional arrays,
    scaling policy, kernel bandwidth policy in feature space, and memory
    guardrails.
  - Must not be approximated by flattening, averaging columns, or independently
    testing each feature in the first implementation.

Default variant selection:

```text
if params["variant_id"] is omitted:
    variant_id = "KERNEL_MMD_BIASED"
```

## 4. Input Schema

Use the common `pandas.DataFrame` input boundary from
`../input_output_contracts.md`.

Public function shape:

```python
def detect_mmd(
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
KERNEL_MMD_BIASED:
  min_reference_size: default 20
  min_current_size: default 20

KERNEL_MMD_UNBIASED:
  min_reference_size: default 20
  min_current_size: default 20
  backend_hard_minimum: 2 values per window
```

The implementation default is 20 because MMD scores and permutation p-values
are unstable at very small sample sizes. If either effective sample size is
below its minimum, return `severity="not_applicable"` and do not compute a
drift decision.

## 5. Parameters

Method-specific parameters come from `drift_method_parameter_guide.md`,
`drift_method_variant_parameters.csv`, and the variant source document.

Accepted `params` keys and defaults for the first implementation:

| Param | Type | Default | Applies to | Meaning |
|---|---:|---:|---|---|
| `variant_id` | string | `KERNEL_MMD_BIASED` | all | Variant selector. |
| `kernel` | string | `rbf` | supported variants | Kernel function. First implementation supports only `rbf`/`gaussian`. |
| `kernel_bandwidth` | float or string | `median` | supported variants | RBF bandwidth sigma. Positive float, `median`, or `median_heuristic`. |
| `gamma` | float | optional | supported variants | Alias for RBF gamma. Must not conflict with `kernel_bandwidth`. |
| `bandwidth_policy` | string | `median` | supported variants | `median` or `fixed`; records how sigma was resolved. |
| `threshold` | float | optional | score-only mode | Optional score threshold for a binary alarm. |
| `threshold_or_alpha` | float | optional | all | Interpreted as score threshold for score-only mode and as alpha for permutation mode. |
| `alpha` | float | `0.05` | permutation mode | Significance level for permutation p-value. |
| `significance_level` | float | optional | permutation mode | Alias for `alpha`; must not conflict with other alpha aliases. |
| `input_signal` | string | optional | all | Value column name only when `value_col is None`; otherwise metadata label. |
| `p_value_method` | string | `none` | all | `none` for score-only result, or `permutation` for optional p-value. |
| `permutation_count` | int | `999` | permutation mode | Number of random permutations. Must be positive. |
| `random_seed` | int or None | `None` | permutation mode | Seed for reproducible permutations. |
| `permutation_alternative` | string | `greater` | permutation mode | Must be `greater`; larger MMD is more extreme. |
| `min_reference_size` | int | `20` | all | Minimum effective reference sample size after invalid rows are dropped. |
| `min_current_size` | int | `20` | all | Minimum effective current sample size after invalid rows are dropped. |
| `nan_policy` | string | `drop` | all | First implementation supports `drop`/`omit` only. |
| `sample_imbalance_warning_ratio` | float | `10.0` | all | Warn when larger sample size divided by smaller sample size exceeds this ratio. |
| `multiple_testing_correction` | string | `none` | all | Recorded as metadata only. Correction is not applied inside this detector. |

Parameter rules:

- `kernel` must be `rbf` or `gaussian`. Linear, polynomial, Laplacian, learned,
  and custom kernels are deferred.
- RBF kernel definition:

```text
K(x, y) = exp(-gamma * (x - y)^2)
gamma = 1 / (2 * sigma^2)
```

- `kernel_bandwidth` as a positive float means `sigma=<that value>`.
- `kernel_bandwidth="median"` or `"median_heuristic"` means compute sigma from
  the median of positive pairwise absolute distances in the pooled univariate
  sample. If all pairwise distances are zero, return `not_applicable` because
  the RBF bandwidth cannot be resolved.
- `gamma` is allowed only as an alternative to `kernel_bandwidth`. It must be a
  finite positive float. If both `gamma` and a numeric `kernel_bandwidth` are
  supplied, return `not_applicable` for conflicting bandwidth definitions.
- `bandwidth_policy="fixed"` requires a numeric `kernel_bandwidth` or `gamma`.
  `bandwidth_policy="median"` uses the median heuristic.
- Default `p_value_method="none"` and no p-value is produced.
- In score-only mode, `threshold_or_alpha` is a score threshold alias, not a
  p-value alpha. Add a warning when this alias is used.
- In score-only mode, `threshold` or `threshold_or_alpha` must be finite and
  `>= 0` when supplied.
- If no score threshold is supplied in score-only mode, return
  `drift_detected=None`, `severity="watch"`, and
  `DRIFT_ALARM_STATE="undetermined"`.
- In permutation mode, resolve `alpha` from `alpha`, `threshold_or_alpha`, or
  `significance_level`; aliases must not conflict and must satisfy
  `0 < alpha < 1`.
- In permutation mode, any `threshold` is recorded as metadata only and must
  not override the p-value decision in the first implementation.
- `permutation_count` must be a positive integer. Recommended default is `999`;
  tests may use a smaller count only when deterministic behavior is asserted
  with a fixed `random_seed`.
- `nan_policy` supports `drop` and `omit` as aliases for dropping invalid rows.
  Other values return `not_applicable`.
- `multiple_testing_correction != "none"` adds a warning and is recorded in
  metadata, but the p-value is not corrected by this detector.
- Reject or warn on unrelated params such as `feature_cols`, `embedding_cols`,
  `category_col`, `count_col`, label columns, classifier settings, projection
  settings, `window_size`, `update_frequency`, or
  `linear_time_approximation`.

## 6. Statistic, Kernel, and P-value Policy

Normalize samples to one-dimensional arrays:

```python
reference_values = np.asarray(..., dtype=float)
current_values = np.asarray(..., dtype=float)
```

RBF kernel matrix helper:

```python
def rbf_kernel_1d(x: np.ndarray, y: np.ndarray, gamma: float) -> np.ndarray:
    return np.exp(-gamma * (x[:, None] - y[None, :]) ** 2)
```

Biased squared MMD:

```text
mmd2_biased = mean(Kxx) + mean(Kyy) - 2 * mean(Kxy)
```

Unbiased squared MMD:

```text
mmd2_unbiased =
    (sum(Kxx) - trace(Kxx)) / (n_reference * (n_reference - 1))
  + (sum(Kyy) - trace(Kyy)) / (n_current * (n_current - 1))
  - 2 * mean(Kxy)
```

Output policy:

- Report squared MMD as the primary statistic and score.
- Use canonical `TEST_STATISTIC` and method-specific `MMD_STATISTIC` for the
  same observed value.
- Also include `MMD_SQUARED` for clarity.
- Do not take the square root in the first implementation because the unbiased
  estimator can be negative.
- Guard against non-finite kernel values, non-finite MMD, and unexpected large
  memory allocation requirements.

Permutation p-value policy for supported kernel variants:

```text
observed_mmd = selected_mmd_statistic(reference_values, current_values, gamma)
pooled = concatenate(reference_values, current_values)
n_reference = len(reference_values)
for each permutation:
    shuffled = rng.permutation(pooled)
    perm_reference = shuffled[:n_reference]
    perm_current = shuffled[n_reference:]
    perm_mmd = selected_mmd_statistic(perm_reference, perm_current, gamma)
p_value = (1 + count(perm_mmd >= observed_mmd)) / (1 + permutation_count)
```

Use `>=` because larger MMD is more extreme. The add-one numerator and
denominator keep the estimated p-value nonzero and stable for finite
permutation counts. Reuse the bandwidth resolved from the observed pooled data
for all permutations; do not recompute the median bandwidth per permutation.

Do not use asymptotic p-values, bootstrap p-values, linear-time approximation,
or streaming alarms in the first implementation.

## 7. Output Measurements

`drift_method_variant_measurement_summary.csv` maps all DM-024 variants to:

```text
TEST_STATISTIC
P_VALUE
DRIFT_ALARM_STATE
```

Return these canonical measurements for every successful supported run:

```python
{
    "TEST_STATISTIC": <float observed squared MMD>,
    "P_VALUE": <float in [0, 1] or None>,
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
    "MMD_STATISTIC": <same float as TEST_STATISTIC>,
    "MMD_SQUARED": <same float as TEST_STATISTIC>,
    "KERNEL": "rbf",
    "KERNEL_BANDWIDTH": <resolved sigma>,
    "KERNEL_GAMMA": <resolved gamma>,
    "BANDWIDTH_POLICY": <"median" | "fixed">,
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
}
```

For score-only mode without a threshold:

```text
P_VALUE = None
DRIFT_ALARM_STATE = "undetermined"
```

For score-only mode with a threshold:

```text
P_VALUE = None
DRIFT_ALARM_STATE = "drift_detected" if mmd_score > threshold else "normal"
```

For permutation mode, also include:

```python
{
    "PERMUTATION_COUNT": <int>,
    "PERMUTATION_EXTREME_COUNT": <int>,
    "PERMUTATION_ALTERNATIVE": "greater",
}
```

Top-level `DriftResult` field mapping:

```text
method_id = "DM-024"
method_name = "MMD"
method_category = "BatchDistributionComparison"
variant_id = resolved variant id
drift_score = observed squared MMD
p_value = permutation p-value or None
test_statistic = observed squared MMD
threshold = score threshold for score-only mode, alpha for permutation mode
```

Interpretation text should state:

- which variant ran
- reference/current effective sample sizes
- observed squared MMD
- kernel, bandwidth policy, resolved sigma, and resolved gamma
- whether a score threshold or permutation p-value decision was used
- p-value, alpha, and permutation count when applicable
- mean/median/quartile movement as descriptive context when available
- that the result is a numeric distribution distance signal, not proof of root
  cause, model performance degradation, or supervised concept drift

## 8. Algorithm Steps

1. Normalize `params` to an empty dict when omitted.
2. Resolve `variant_id`; default to `KERNEL_MMD_BIASED`.
3. Reject unknown variants with `severity="not_applicable"` and a warning.
4. Reject `LINEAR_TIME_MMD` and `STREAMING_MMD` with
   `severity="not_applicable"` until their separate contracts are approved.
5. Reject multivariate/embedding requests through `feature_cols`,
   `embedding_cols`, or array-like values in the selected value column.
6. Resolve kernel, bandwidth/gamma policy, threshold or alpha policy,
   permutation settings, `nan_policy`, warning thresholds, sample-size minima,
   and the value column.
7. Validate that both reference and current windows are supplied and parseable.
8. Validate required columns and scalar numeric value data. Boolean data is not
   valid MMD input.
9. Convert and sort the DataFrame according to the common window handling
   contract.
10. Slice inclusive reference and current windows.
11. Drop rows with invalid timestamps or non-finite values; record original and
    effective counts.
12. If either effective sample is empty or below minimum, return not
    applicable.
13. Convert the two effective samples to one-dimensional
    `numpy.ndarray[float64]` objects.
14. Add warnings for invalid rows, highly imbalanced sample sizes, repeated or
    degenerate values, small samples that pass the hard minimum, and
    multiple-testing metadata when applicable.
15. Resolve RBF sigma and gamma from the documented bandwidth policy.
16. Compute `Kxx`, `Kyy`, and `Kxy` and the selected MMD statistic.
17. Convert the statistic to a Python float and guard against NaN/inf.
18. If `p_value_method="permutation"`, run the documented permutation loop
    with `numpy.random.default_rng(random_seed)` and compute the add-one
    p-value.
19. Compute descriptive summaries: effective sample counts, means, medians,
    25th/75th percentiles, mean delta, and median delta.
20. Apply the drift decision rule from section 9.
21. Build `DriftResult` with method identity, variant, canonical measurements,
    helper summaries, counts, windows, parameters, warnings, and concise
    interpretation text.

## 9. Drift Decision Rule

Score-only default for `KERNEL_MMD_BIASED` and `KERNEL_MMD_UNBIASED`:

```text
if threshold is None:
    drift_detected = None
    severity = "watch"
    DRIFT_ALARM_STATE = "undetermined"
elif mmd_score > threshold:
    drift_detected = True
    severity = "drift_detected"
    DRIFT_ALARM_STATE = "drift_detected"
else:
    drift_detected = False
    severity = "normal"
    DRIFT_ALARM_STATE = "normal"
```

Use strict `>` for the score threshold. Equality is not drift.

Permutation p-value rule:

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

- score-only without threshold: "RBF-kernel MMD score reported; binary alarm is
  undetermined because no threshold was supplied"
- score-only with threshold and alarm: "numeric distribution drift candidate
  under the MMD score threshold"
- permutation alarm: "numeric distribution drift candidate under the MMD
  permutation p-value rule"
- non-alarm: "no MMD alarm under this window, kernel, bandwidth, and threshold
  or alpha"
- not applicable: method was not applicable or calculation failed

The MMD statistic is method-specific and depends on kernel, bandwidth, sample
sizes, and variant. It must not be compared directly with KS, Wasserstein,
Cramer-von Mises, Energy Distance, Epps-Singleton, or multivariate statistics
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
- `LINEAR_TIME_MMD` and `STREAMING_MMD` until their contracts are approved
- `feature_cols`, `embedding_cols`, object embeddings, list-valued rows, or
  other multivariate requests in the first implementation
- invalid `kernel`, `kernel_bandwidth`, `gamma`, `bandwidth_policy`,
  threshold, alpha, alpha alias conflict, `p_value_method`,
  `permutation_count`, `random_seed`, `nan_policy`, sample-size parameter, or
  warning-ratio parameter
- all pooled values are identical when median bandwidth is requested
- expected kernel matrix size exceeds a documented runtime guardrail, if one is
  added during implementation
- p-value methods other than `none` or `permutation`
- non-finite MMD statistic
- non-finite p-value or p-value outside `[0, 1]`
- current/reference window overlap when overlap policy is not explicitly
  defined by the implementation

Return `severity="normal"`, `"watch"`, or `"drift_detected"` with warnings when
the method can still run but interpretation needs caution:

- timestamps or values were dropped because they were invalid or non-finite
- no score threshold was supplied in score-only mode
- `threshold_or_alpha` was interpreted as a score threshold rather than a
  p-value alpha in score-only mode
- reference/current sample sizes are highly imbalanced
- either effective sample size is small enough to make the statistic or
  permutation result unstable, even if it passes the hard minimum
- repeated, rounded, or tied values make the signal effectively discrete
- the median heuristic bandwidth is very small or very large relative to the
  value scale
- observations are repeated or autocorrelated time-series rows rather than
  independent samples
- strong outliers or scale changes may dominate the RBF kernel comparison
- sample extraction, traffic mix, seasonality, or segment definitions differ
  between windows
- `permutation_count` is low, so p-value resolution is coarse
- `multiple_testing_correction` is not `"none"`; record that this detector does
  not apply correction internally

Unexpected backend or numeric exceptions should return `severity="error"` or
`"watch"` according to project convention, with `drift_detected=None` and a
clear warning, without raising through the public detector boundary.

Do not silently coerce categorical values, boolean flags, labels, embeddings,
lists, object arrays, count tables, or multivariate matrices into the
univariate MMD detector.

## 11. Implementation Target

```text
module: drift_algorithm.methods.batchdistributioncomparison
function: detect_mmd
```

Expected dependencies:

```text
pandas
numpy
```

No SciPy backend is required for the first implementation because the
univariate RBF-kernel MMD statistic can be implemented directly with NumPy.

Expected result object:

```text
DriftResult from drift_algorithm/docs/input_output_contracts.md equivalent code
contract
```

Helper functions should follow existing patterns in
`drift_algorithm.methods.batchdistributioncomparison`:

- add `MMD_METHOD_ID = "DM-024"` and `MMD_METHOD_NAME = "MMD"`
- define `SUPPORTED_MMD_VARIANTS` for `KERNEL_MMD_BIASED` and
  `KERNEL_MMD_UNBIASED`
- define `DEFERRED_MMD_VARIANTS` for `LINEAR_TIME_MMD` and `STREAMING_MMD`
- use the common `DriftResult` dataclass
- use `not_applicable_result` or a method-specific not-applicable helper for
  validation failures
- use `prepare_numeric_windows` where it matches this contract
- keep method-specific MMD helpers private to the module unless another method
  already shares the same helper
- record backend name (`numpy`), kernel, bandwidth policy, resolved sigma,
  resolved gamma, threshold or alpha policy, permutation settings, value
  column, effective windows, sample-size metadata, and unsupported/deferred
  variant decisions so the result is auditable

Suggested private helper shape:

```python
def _mmd_not_applicable(
    variant_id: str | None,
    warning: str,
    metadata: dict[str, Any] | None = None,
    prior_warnings: list[str] | None = None,
) -> DriftResult:
    ...

def _resolve_mmd_bandwidth(
    reference_values: np.ndarray,
    current_values: np.ndarray,
    params: dict[str, Any],
) -> dict[str, float | str]:
    """Return resolved sigma, gamma, and bandwidth policy."""

def _mmd_rbf_statistic(
    reference_values: np.ndarray,
    current_values: np.ndarray,
    *,
    gamma: float,
    variant_id: str,
) -> float:
    ...

def _permutation_mmd_p_value(
    reference_values: np.ndarray,
    current_values: np.ndarray,
    *,
    gamma: float,
    variant_id: str,
    observed_mmd: float,
    permutation_count: int,
    random_seed: int | None,
) -> dict[str, float | int]:
    ...
```

Public contract:

- `detect_mmd` must be importable from
  `drift_algorithm.methods.batchdistributioncomparison`.
- The function must accept the common arguments exactly as shown in section 4.
- It must return `DriftResult`, never raw tuples or dictionaries.
- Validation failures must return `severity="not_applicable"` unless they are
  unexpected numeric/runtime errors.
- Score-only mode must not fabricate a p-value.
- Permutation mode must use the documented add-one p-value and strict
  `p_value < alpha` decision rule.
- Multivariate, embedding, linear-time, and streaming requests must be explicit
  `not_applicable` results in the first implementation.

## 12. Verification Plan

Unit tests for the first implementation:

1. Default score-only no-threshold case:
   - Generate reference/current numeric samples from the same distribution with
     a deterministic seed.
   - Omit `variant_id`, threshold, and p-value settings.
   - Assert `variant_id == "KERNEL_MMD_BIASED"`.
   - Assert `TEST_STATISTIC`, `MMD_STATISTIC`, `MMD_SQUARED`,
     `DRIFT_ALARM_STATE`, `SAMPLE_SIZE`, `SAMPLE_SIZE_REFERENCE`, and
     `SAMPLE_SIZE_CURRENT` exist.
   - Assert `p_value is None`, `drift_detected is None`,
     `severity == "watch"`, and `DRIFT_ALARM_STATE == "undetermined"`.
2. Score-threshold normal case:
   - Use a high threshold above the observed MMD score.
   - Assert `drift_detected is False`, `severity == "normal"`,
     `threshold` equals the supplied threshold, and no p-value is reported.
3. Score-threshold drift candidate:
   - Generate reference normal samples and current samples with a clear
     location, scale, or shape shift.
   - Use a threshold below the observed MMD score.
   - Assert `mmd_score > threshold`, `drift_detected is True`,
     `severity == "drift_detected"`, and `DRIFT_ALARM_STATE` is
     `"drift_detected"`.
4. Unbiased variant:
   - Select `KERNEL_MMD_UNBIASED`.
   - Assert the statistic is finite, may be negative for no-drift data, and is
     not clamped.
   - Assert hard minimum behavior when either window has fewer than two
     effective rows.
5. Bandwidth policy:
   - Assert default median heuristic records resolved `KERNEL_BANDWIDTH` and
     `KERNEL_GAMMA`.
   - Assert numeric `kernel_bandwidth` and `gamma` produce consistent metadata.
   - Assert all-identical values under median bandwidth return
     `severity="not_applicable"`.
   - Assert conflicting `gamma` and numeric `kernel_bandwidth` return
     `not_applicable`.
6. Permutation p-value no-drift:
   - Use `p_value_method="permutation"` with fixed `random_seed` and a moderate
     `permutation_count`.
   - Generate samples from the same distribution.
   - Assert `P_VALUE` is in `[0, 1]`, permutation metadata exists, and
     `drift_detected is False` for a deterministic seed chosen to keep
     `p_value >= alpha`.
7. Permutation p-value drift candidate:
   - Use `p_value_method="permutation"`.
   - Generate current samples with a clear distribution shift.
   - Assert `p_value < alpha`, `drift_detected is True`, and
     `severity == "drift_detected"`.
8. Parameter alias and validation:
   - Assert `threshold_or_alpha` is treated as threshold in score-only mode and
     as alpha in permutation mode.
   - Assert conflicting alpha aliases in permutation mode return
     `severity="not_applicable"`.
   - Assert invalid `kernel`, bandwidth, threshold, `p_value_method`,
     `permutation_count`, `nan_policy`, and sample-size settings return not
     applicable.
9. Schema and window validation:
   - Missing value column.
   - Non-numeric, boolean, object/list, embedding-like, or categorical value
     column.
   - Missing reference/current windows.
   - Empty current/reference slices.
   - Effective sample size below minimum.
   - Overlapping windows if no overlap policy is implemented.
10. Deferred variants and multivariate requests:
    - `LINEAR_TIME_MMD` returns `severity="not_applicable"` with a warning
      about the deferred approximation contract.
    - `STREAMING_MMD` returns `severity="not_applicable"` with a warning about
      the deferred streaming contract.
    - Supplying `feature_cols`, `embedding_cols`, or array-like row values
      returns `not_applicable` and does not flatten or independently test
      feature columns.
11. Warning behavior:
    - NaN, infinity, and invalid timestamps are dropped with warnings and
      effective counts.
    - Imbalanced sample sizes produce a caution warning.
    - Low permutation count produces a coarse p-value warning.
    - `multiple_testing_correction != "none"` is recorded but not applied.
12. Numeric failure:
    - Simulate non-finite kernel output, non-finite statistic, or matrix-size
      guardrail breach.
    - Assert the public detector returns `severity="error"`, `"watch"`, or
      `not_applicable` according to project convention with
      `drift_detected=None` and a clear warning.

Recommended commands after implementation:

```text
python -m py_compile drift_algorithm\methods\batchdistributioncomparison.py
python -m pytest tests\test_mmd.py
python -m pytest tests\test_energy_distance.py tests\test_epps_singleton_test.py
```

Manual review before marking implementation complete:

- Confirm public function signature matches the common contract.
- Confirm canonical measurement names match
  `drift_method_variant_measurement_summary.csv`.
- Confirm default variant is `KERNEL_MMD_BIASED`.
- Confirm default kernel is RBF and bandwidth defaults to the median
  heuristic.
- Confirm score-only mode leaves `p_value=None` and `drift_detected=None` when
  no threshold is supplied.
- Confirm permutation mode uses the documented add-one p-value and strict
  `p_value < alpha` rule.
- Confirm `KERNEL_MMD_UNBIASED` preserves signed finite-sample values.
- Confirm linear-time, streaming, multivariate, and embedding requests fail
  explicitly instead of being silently coerced into scalar numeric MMD.
- Confirm interpretation text avoids root-cause, performance-degradation, and
  supervised concept-drift claims without labeled evidence.

## 13. Manager Review Points

- First implementation scope is intentionally limited to univariate numeric
  reference/current `(time, value)` windows even though the catalog mentions
  embedding/vector samples.
- Default variant is `KERNEL_MMD_BIASED` with RBF kernel, median-heuristic
  bandwidth, and squared MMD as the score.
- Default output is score-only: no p-value and no binary alarm unless a score
  threshold or permutation p-value is explicitly selected.
- `KERNEL_MMD_UNBIASED` is implementation-ready for the same scalar contract;
  signed finite-sample values should be preserved.
- Permutation p-value is implementation-ready as an optional policy with fixed
  observed bandwidth, `permutation_count`, `random_seed`, and strict
  `p_value < alpha`.
- `LINEAR_TIME_MMD`, `STREAMING_MMD`, multivariate feature matrices, and
  embeddings remain deferred until separate contracts are approved.
- The public target is `detect_mmd` in
  `drift_algorithm.methods.batchdistributioncomparison`.
