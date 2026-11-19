# DM-022 Energy Distance Design

## 1. Method Identity

- Method ID: `DM-022`
- Method name: `Energy Distance`
- Category: `BatchDistributionComparison`
- Method kind: `detector`
- Status: `확정`
- Source catalog: `drift_methods_catalog.md`
- Source variant document: `algorithm_variants/energy_distance_algorithm_variants.md`
- Source parameter tables:
  - `drift_method_variant_links.csv`
  - `drift_method_variant_measurement_summary.csv`
  - `drift_method_variant_parameters.csv`
  - `drift_method_parameter_guide.md`

The first implementation is a univariate numeric batch detector. It compares
the empirical distribution of a current `(time, value)` window against a
reference `(time, value)` window and returns the scalar Energy distance.

## 2. Purpose

`Energy Distance` answers whether a scalar numeric monitoring signal has moved
away from its reference distribution. It is useful for model scores, losses,
latencies, numeric features, residuals, costs, confidence values, or other
one-dimensional monitoring signals where the shape of the distribution matters.

The catalog input is `univariate 또는 multivariate sample`; the catalog output is
`energy distance, p-value optional`.

Use the first implementation when:

- the signal is scalar numeric data
- reference and current windows are both available
- the monitoring question is distribution distance, not a classical named
  hypothesis test
- a distance-only result is acceptable, or the caller explicitly enables a
  permutation p-value

Do not use the first implementation for categorical labels, count tables,
probability vectors, embeddings, multivariate feature matrices, text, SHAP
matrices, or supervised error streams. Those require other method families or a
future multivariate Energy Distance contract.

## 3. Supported Variants

Supported for the first implementation:

- `UNIVARIATE_ENERGY_DISTANCE`
  - Default variant.
  - Computes the one-dimensional Energy distance between reference and current
    numeric samples.
  - Uses `scipy.stats.energy_distance` when SciPy is available.
  - Returns distance only by default. No p-value is produced unless the caller
    selects the permutation policy described below.
- `ENERGY_DISTANCE_PERMUTATION_TEST`
  - Implementation-ready optional variant for the same univariate `(time,
    value)` input contract.
  - Computes the observed one-dimensional Energy distance, then estimates a
    p-value by randomly permuting the pooled samples into reference/current
    groups.
  - Uses the p-value rule `p_value < alpha` for drift decisions.
  - May be implemented in the same first code pass if runtime cost and test
    coverage are acceptable; otherwise it must return `not_applicable` with a
    clear warning that permutation p-values are deferred.

Deferred until a multivariate input and scaling contract is approved:

- `MULTIVARIATE_ENERGY_DISTANCE`
  - Requires `params["feature_cols"]` or embedding columns, two-dimensional
    numeric arrays, feature scaling policy, distance norm policy, and runtime
    guardrails.
  - `scipy.stats.energy_distance` is one-dimensional and is not sufficient for
    the catalog's multivariate variant.
  - Must return `severity="not_applicable"` in the first implementation rather
    than flattening, averaging, or independently testing feature columns.

Default variant selection:

```text
if params["variant_id"] is omitted:
    variant_id = "UNIVARIATE_ENERGY_DISTANCE"
```

## 4. Input Schema

Use the common `pandas.DataFrame` input boundary from
`../input_output_contracts.md`.

Public function shape:

```python
def detect_energy_distance(
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
value: numeric integer or floating dtype
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
6. Drop rows with invalid timestamps or non-finite values for calculation.
7. Record original and effective row counts in `metadata` and `measurements`.

Minimum effective sample sizes:

```text
UNIVARIATE_ENERGY_DISTANCE:
  min_reference_size: default 20
  min_current_size: default 20

ENERGY_DISTANCE_PERMUTATION_TEST:
  min_reference_size: default 20
  min_current_size: default 20
```

The hard minimum for numeric calculation is two values per window, but the
implementation default is 20 because monitoring decisions and permutation
p-values are unstable at very small sample sizes. If either effective sample
size is below its minimum, return `severity="not_applicable"` and do not
compute a drift decision.

## 5. Parameters

Method-specific parameters come from `drift_method_parameter_guide.md`,
`drift_method_variant_parameters.csv`, and the variant source document.

Accepted `params` keys and defaults for the first implementation:

| Param | Type | Default | Applies to | Meaning |
|---|---:|---:|---|---|
| `variant_id` | string | `UNIVARIATE_ENERGY_DISTANCE` | all | Variant selector. |
| `threshold` | float | optional | distance-only variant | Optional nonnegative distance threshold for a binary alarm. |
| `threshold_or_alpha` | float | optional | all | Interpreted as distance threshold for distance-only mode and as alpha for permutation mode. |
| `alpha` | float | `0.05` | permutation variant | Significance level for permutation p-value. |
| `significance_level` | float | optional | permutation variant | Alias for `alpha`; must not conflict with other alpha aliases. |
| `input_signal` | string | optional | all | Value column name only when `value_col is None`; otherwise metadata label. |
| `distance_metric` | string | `energy` | all | Must be `energy` or `energy_distance` in the first implementation. |
| `p_value_method` | string | `none` | univariate; `permutation` for permutation variant | `none` returns distance only; `permutation` estimates a p-value. |
| `permutation_count` | int | `999` | permutation variant | Number of random permutations. Must be positive. |
| `random_seed` | int or None | `None` | permutation variant | Seed for reproducible permutations. |
| `permutation_alternative` | string | `greater` | permutation variant | Must be `greater`; larger distance is more extreme. |
| `min_reference_size` | int | `20` | all | Minimum effective reference sample size after invalid rows are dropped. |
| `min_current_size` | int | `20` | all | Minimum effective current sample size after invalid rows are dropped. |
| `nan_policy` | string | `drop` | all | First implementation supports `drop`/`omit` only. |
| `sample_imbalance_warning_ratio` | float | `10.0` | all | Warn when larger sample size divided by smaller sample size exceeds this ratio. |
| `multiple_testing_correction` | string | `none` | all | Recorded as metadata only. Correction is not applied inside this detector. |

Parameter rules:

- `distance_metric` must be `energy` or `energy_distance`.
- For `UNIVARIATE_ENERGY_DISTANCE`, default `p_value_method="none"` and no
  p-value is produced.
- For `UNIVARIATE_ENERGY_DISTANCE`, `threshold_or_alpha` is a distance
  threshold alias, not a p-value alpha. Add a warning when this alias is used
  so reports do not confuse threshold and significance.
- For `UNIVARIATE_ENERGY_DISTANCE`, `threshold` or `threshold_or_alpha` must be
  finite and `>= 0` when supplied.
- If no distance threshold is supplied for `UNIVARIATE_ENERGY_DISTANCE`, return
  `drift_detected=None`, `severity="watch"`, and
  `DRIFT_ALARM_STATE="undetermined"`.
- For `ENERGY_DISTANCE_PERMUTATION_TEST`, resolve `alpha` from `alpha`,
  `threshold_or_alpha`, or `significance_level`; aliases must not conflict and
  must satisfy `0 < alpha < 1`.
- For `ENERGY_DISTANCE_PERMUTATION_TEST`, `p_value_method` must be
  `permutation`; any `threshold` is recorded as metadata only and must not
  override the p-value decision in the first implementation.
- `permutation_count` must be a positive integer. Recommended default is `999`;
  tests may use a smaller count only when they assert deterministic behavior
  with a fixed `random_seed`.
- `nan_policy` supports `drop` and `omit` as aliases for dropping invalid rows.
  Other values return not applicable.
- `multiple_testing_correction != "none"` adds a warning and is recorded in
  metadata, but the p-value is not corrected by this detector.
- Reject or warn on unrelated params such as `feature_cols`, `embedding_cols`,
  `category_col`, `count_col`, label columns, classifier settings, covariance
  settings, projection settings, or binning settings.

## 6. Statistic and P-value Policy

Distance calculation for the first supported variant:

```python
from scipy.stats import energy_distance

distance = energy_distance(reference_values, current_values)
```

This function is the preferred backend for `UNIVARIATE_ENERGY_DISTANCE`. It
computes the one-dimensional Energy distance and does not produce a p-value.
If SciPy is unavailable or `scipy.stats.energy_distance` is missing, return
`severity="error"` or `severity="watch"` according to the project convention
for missing optional dependencies, with `drift_detected=None` and a clear
warning.

Permutation p-value policy for `ENERGY_DISTANCE_PERMUTATION_TEST`:

```text
observed_distance = energy_distance(reference_values, current_values)
pooled = concatenate(reference_values, current_values)
n_reference = len(reference_values)
for each permutation:
    shuffled = rng.permutation(pooled)
    perm_reference = shuffled[:n_reference]
    perm_current = shuffled[n_reference:]
    perm_distance = energy_distance(perm_reference, perm_current)
p_value = (1 + count(perm_distance >= observed_distance)) / (1 + permutation_count)
```

Use `>=` because larger Energy distance is more extreme. The add-one numerator
and denominator keep the estimated p-value nonzero and stable for finite
permutation counts.

Do not use asymptotic p-values in the first implementation. Do not use SciPy's
one-dimensional backend for `MULTIVARIATE_ENERGY_DISTANCE` by flattening a
matrix or concatenating feature columns.

## 7. Output Measurements

`drift_method_variant_measurement_summary.csv` maps all DM-022 variants to:

```text
TEST_STATISTIC
P_VALUE
DRIFT_ALARM_STATE
```

Return these canonical measurements for every successful supported run:

```python
{
    "TEST_STATISTIC": <float observed Energy distance>,
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
    "ENERGY_DISTANCE": <float observed Energy distance>,
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

For `UNIVARIATE_ENERGY_DISTANCE` without a threshold:

```text
P_VALUE = None
DRIFT_ALARM_STATE = "undetermined"
```

For `UNIVARIATE_ENERGY_DISTANCE` with a distance threshold:

```text
P_VALUE = None
DRIFT_ALARM_STATE = "drift_detected" if distance > threshold else "normal"
```

For `ENERGY_DISTANCE_PERMUTATION_TEST`, also include:

```python
{
    "PERMUTATION_COUNT": <int>,
    "PERMUTATION_EXTREME_COUNT": <int>,
    "PERMUTATION_ALTERNATIVE": "greater",
}
```

Top-level `DriftResult` field mapping:

```text
method_id = "DM-022"
method_name = "Energy Distance"
method_category = "BatchDistributionComparison"
variant_id = resolved variant id
drift_score = observed Energy distance
p_value = permutation p-value or None
test_statistic = observed Energy distance
threshold = distance threshold for distance-only mode, alpha for permutation mode
```

Interpretation text should state:

- which variant ran
- reference/current effective sample sizes
- observed Energy distance
- whether a distance threshold or permutation p-value decision was used
- p-value, alpha, and permutation count when applicable
- mean/median/quartile movement as descriptive context when available
- that the result is a numeric distribution distance signal, not proof of root
  cause, model performance degradation, or supervised concept drift

## 8. Algorithm Steps

1. Normalize `params` to an empty dict when omitted.
2. Resolve `variant_id`; default to `UNIVARIATE_ENERGY_DISTANCE`.
3. Reject unknown variants with `severity="not_applicable"` and a warning.
4. Reject `MULTIVARIATE_ENERGY_DISTANCE` with `severity="not_applicable"` until
   the multivariate input, scaling, and distance contracts are implemented.
5. Resolve `distance_metric`, `p_value_method`, threshold or alpha policy,
   permutation settings, `nan_policy`, warning thresholds, sample-size minima,
   and the value column.
6. Validate that both reference and current windows are supplied and parseable.
7. Validate required columns and scalar numeric value data. Boolean data is not
   valid Energy Distance input.
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
    autocorrelated time-series observations, and multiple-testing metadata when
    applicable.
14. Call `scipy.stats.energy_distance(reference_values, current_values)`.
15. Convert distance to a Python float and guard against NaN/inf or negative
    backend output.
16. If variant is `ENERGY_DISTANCE_PERMUTATION_TEST`, run the documented
    permutation loop with `numpy.random.default_rng(random_seed)` and compute
    the add-one p-value.
17. Compute descriptive summaries: effective sample counts, means, medians,
    25th/75th percentiles, and median delta.
18. Apply the drift decision rule from section 9.
19. Build `DriftResult` with method identity, variant, canonical measurements,
    helper summaries, counts, windows, parameters, warnings, and concise
    interpretation text.

## 9. Drift Decision Rule

Distance-only default for `UNIVARIATE_ENERGY_DISTANCE`:

```text
if threshold is None:
    drift_detected = None
    severity = "watch"
    DRIFT_ALARM_STATE = "undetermined"
elif energy_distance > threshold:
    drift_detected = True
    severity = "drift_detected"
    DRIFT_ALARM_STATE = "drift_detected"
else:
    drift_detected = False
    severity = "normal"
    DRIFT_ALARM_STATE = "normal"
```

Use strict `>` for the distance threshold. Equality is not drift.

Permutation p-value rule for `ENERGY_DISTANCE_PERMUTATION_TEST`:

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

- distance-only without threshold: "numeric distribution distance reported;
  binary alarm is undetermined because no threshold was supplied"
- distance-only with threshold and alarm: "numeric distribution distance drift
  candidate"
- permutation alarm: "numeric distribution drift candidate under permutation
  p-value"
- non-alarm: "no Energy Distance alarm under this window, variant, and
  threshold or alpha"
- not applicable: method was not applicable or calculation failed

The Energy distance is method-specific and scale-sensitive. It must not be
compared directly with KS, Wasserstein, Cramer-von Mises, MMD, or multivariate
statistics without method, scale, and variant context.

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
- `MULTIVARIATE_ENERGY_DISTANCE` until the multivariate contract is approved
- invalid `distance_metric`, threshold, alpha, alpha alias conflict,
  `p_value_method`, `permutation_count`, `random_seed`, `nan_policy`,
  sample-size parameter, or warning-ratio parameter
- `ENERGY_DISTANCE_PERMUTATION_TEST` with a p-value method other than
  `permutation`
- non-finite, negative, or otherwise invalid Energy distance from the backend
- non-finite p-value or p-value outside `[0, 1]`
- current/reference window overlap when overlap policy is not explicitly
  defined by the implementation

Return `severity="normal"`, `"watch"`, or `"drift_detected"` with warnings when
the method can still run but interpretation needs caution:

- timestamps or values were dropped because they were invalid or non-finite
- no distance threshold was supplied in distance-only mode
- `threshold_or_alpha` was interpreted as a distance threshold rather than a
  p-value alpha in distance-only mode
- reference/current sample sizes are highly imbalanced
- either effective sample size is small enough to make distance or permutation
  results unstable, even if it passes the hard minimum
- repeated, rounded, or tied values make the signal effectively discrete
- observations are repeated or autocorrelated time-series rows rather than
  independent samples
- strong outliers or scale changes may dominate the distance
- sample extraction, traffic mix, seasonality, or segment definitions differ
  between windows
- `permutation_count` is low, so p-value resolution is coarse
- `multiple_testing_correction` is not `"none"`; record that this detector does
  not apply correction internally

Unexpected backend exceptions should return `severity="error"` or `"watch"`
according to project convention, with `drift_detected=None` and a clear warning,
without raising through the public detector boundary.

Do not silently coerce categorical values, boolean flags, labels, embeddings,
lists, object arrays, or multivariate matrices into the univariate Energy
Distance detector.

## 11. Implementation Target

```text
module: drift_algorithm.methods.batchdistributioncomparison
function: detect_energy_distance
```

Expected dependencies:

```text
pandas
numpy
scipy.stats.energy_distance
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
- keep method-specific Energy Distance helpers private to the module unless
  another numeric batch method already shares the same helper
- record backend name, distance metric, threshold or alpha policy, permutation
  settings, value column, effective windows, sample-size metadata, and
  unsupported/deferred variant decisions so the result is auditable

Suggested private helper shape:

```python
def _energy_distance_not_applicable(
    variant_id: str | None,
    warning: str,
    metadata: dict[str, Any] | None = None,
    prior_warnings: list[str] | None = None,
) -> DriftResult:
    ...

def _resolve_energy_distance_decision_policy(
    variant_id: str,
    params: dict[str, Any],
) -> dict[str, Any]:
    """Return threshold/alpha/p-value policy for the selected variant."""

def _permutation_energy_distance_p_value(
    reference_values: np.ndarray,
    current_values: np.ndarray,
    *,
    permutation_count: int,
    random_seed: int | None,
) -> dict[str, float | int]:
    ...
```

Public contract:

- `detect_energy_distance` must be importable from
  `drift_algorithm.methods.batchdistributioncomparison`.
- The function must accept the common arguments exactly as shown in section 4.
- It must return `DriftResult`, never raw tuples or dictionaries.
- Validation failures must return `severity="not_applicable"` unless they are
  unexpected backend/runtime errors.
- Distance-only mode must not fabricate a p-value.
- Permutation mode must use the documented add-one p-value and strict
  `p_value < alpha` decision rule.

## 12. Verification Plan

Unit tests for the first implementation:

1. Default distance-only no-threshold case:
   - Generate reference/current numeric samples from the same distribution with
     a deterministic seed.
   - Omit `variant_id` and threshold.
   - Assert `variant_id == "UNIVARIATE_ENERGY_DISTANCE"`.
   - Assert `TEST_STATISTIC`, `ENERGY_DISTANCE`, `DRIFT_ALARM_STATE`,
     `SAMPLE_SIZE`, `SAMPLE_SIZE_REFERENCE`, and `SAMPLE_SIZE_CURRENT` exist.
   - Assert `p_value is None`, `drift_detected is None`,
     `severity == "watch"`, and `DRIFT_ALARM_STATE == "undetermined"`.
2. Distance-threshold normal case:
   - Use a high threshold above the observed distance.
   - Assert `drift_detected is False`, `severity == "normal"`,
     `threshold` equals the supplied threshold, and no p-value is reported.
3. Distance-threshold drift candidate:
   - Generate reference normal samples and current samples with a location,
     scale, or shape shift.
   - Use a threshold below the observed distance.
   - Assert `energy_distance > threshold`, `drift_detected is True`,
     `severity == "drift_detected"`, and `DRIFT_ALARM_STATE` is
     `"drift_detected"`.
4. Permutation p-value no-drift:
   - Select `ENERGY_DISTANCE_PERMUTATION_TEST` with fixed `random_seed` and a
     moderate `permutation_count`.
   - Generate samples from the same distribution.
   - Assert `P_VALUE` is in `[0, 1]`, permutation metadata exists, and
     `drift_detected is False` for a deterministic seed chosen to keep
     `p_value >= alpha`.
5. Permutation p-value drift candidate:
   - Select `ENERGY_DISTANCE_PERMUTATION_TEST`.
   - Generate current samples with a clear distribution shift.
   - Assert `p_value < alpha`, `drift_detected is True`, and
     `severity == "drift_detected"`.
6. Parameter alias and validation:
   - Assert `threshold_or_alpha` is treated as threshold in distance-only mode
     and as alpha in permutation mode.
   - Assert conflicting alpha aliases in permutation mode return
     `severity="not_applicable"`.
   - Assert invalid threshold, `distance_metric`, `p_value_method`,
     `permutation_count`, `nan_policy`, and sample-size settings return not
     applicable.
7. Schema and window validation:
   - Missing value column.
   - Non-numeric, boolean, object/list, embedding-like, or categorical value
     column.
   - Missing reference/current windows.
   - Empty current/reference slices.
   - Effective sample size below minimum.
   - Overlapping windows if no overlap policy is implemented.
8. Deferred multivariate variant:
   - `MULTIVARIATE_ENERGY_DISTANCE` with `feature_cols` returns
     `severity="not_applicable"` and a warning about the missing multivariate
     contract.
   - Assert it does not flatten or independently test feature columns.
9. Warning behavior:
   - NaN, infinity, and invalid timestamps are dropped with warnings and
     effective counts.
   - Imbalanced sample sizes produce a caution warning.
   - Low permutation count produces a coarse p-value warning.
   - `multiple_testing_correction != "none"` is recorded but not applied.
10. Backend failure:
    - Simulate missing/failed `scipy.stats.energy_distance`.
    - Assert the public detector returns `severity="error"` or `"watch"` with
      `drift_detected=None` and a clear warning.

Recommended commands after implementation:

```text
python -m py_compile drift_algorithm\methods\batchdistributioncomparison.py
python -m pytest tests\test_energy_distance.py
python -m pytest tests\test_wasserstein_distance.py tests\test_cramer_von_mises_test.py
```

Manual review before marking implementation complete:

- Confirm public function signature matches the common contract.
- Confirm canonical measurement names match
  `drift_method_variant_measurement_summary.csv`.
- Confirm distance-only mode leaves `p_value=None` and
  `drift_detected=None` when no threshold is supplied.
- Confirm permutation mode uses the documented add-one p-value and strict
  `p_value < alpha` rule.
- Confirm `MULTIVARIATE_ENERGY_DISTANCE` fails explicitly instead of flattening
  a feature matrix.
- Confirm interpretation text avoids root-cause, performance-degradation, and
  supervised concept-drift claims without labeled evidence.

## 13. Manager Review Points

- First implementation scope is intentionally limited to univariate numeric
  reference/current `(time, value)` windows.
- Default behavior is distance-only via `scipy.stats.energy_distance`; no
  p-value or binary alarm is produced unless a threshold or permutation variant
  is explicitly selected.
- `ENERGY_DISTANCE_PERMUTATION_TEST` is implementation-ready as an optional
  univariate extension with `permutation_count`, `random_seed`, and strict
  `p_value < alpha`.
- `MULTIVARIATE_ENERGY_DISTANCE` remains deferred until feature matrix,
  scaling, distance norm, and runtime contracts are approved.
- The public target is `detect_energy_distance` in
  `drift_algorithm.methods.batchdistributioncomparison`.
