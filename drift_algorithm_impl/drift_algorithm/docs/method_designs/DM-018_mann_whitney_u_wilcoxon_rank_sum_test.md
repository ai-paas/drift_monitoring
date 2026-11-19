# DM-018 Mann-Whitney U / Wilcoxon Rank Sum Test Design

## 1. Method Identity

- Method ID: `DM-018`
- Method name: `Mann-Whitney U / Wilcoxon Rank Sum Test`
- Category: `BatchDistributionComparison`
- Method kind: `detector`
- Status: `확정`
- Source catalog: `drift_methods_catalog.md`
- Source variant document: `algorithm_variants/mann_whitney_u_test_algorithm_variants.md`

## 2. Purpose

This method detects rank/location drift between a reference numeric sample and
a current numeric sample. It is the rank-based, non-parametric alternative to a
two-sample mean test when the monitoring question is whether current values are
systematically higher, lower, or otherwise shifted relative to the reference
window.

Primary input from the catalog: numeric sample.
Primary output from the catalog: U statistic, p-value.

Report interpretation must describe this as a distribution rank/location shift
candidate, not as confirmed root cause, performance degradation, or supervised
concept drift. If the two windows have very different distribution shapes, the
result must not be summarized as a simple median shift without an additional
effect-size or distribution-shape check.

## 3. Supported Variants

First implementation variants:

- `MANN_WHITNEY_TWO_SIDED`
  - Default variant.
  - Uses `alternative="two-sided"`.
  - Use when the monitoring question is whether current values have shifted in
    either direction relative to reference.
- `MANN_WHITNEY_ONE_SIDED`
  - Uses `alternative="greater"` or `alternative="less"` from params.
  - Use only when the operating direction is fixed before seeing the result,
    for example latency increase or score decrease monitoring.
- `MANN_WHITNEY_EXACT`
  - Uses exact p-value calculation for small, tie-free windows.
  - First implementation should run this variant only when both effective
    sample sizes are at or below `exact_max_sample_size` and no ties are present.
    If ties are present or sample sizes exceed the exact limit, return
    `severity="not_applicable"` unless `params["exact_fallback"]` explicitly
    requests fallback to asymptotic calculation.

Unsupported in the first implementation:

- paired Wilcoxon signed-rank test; this method is two independent samples only
- multivariate samples
- categorical/count inputs
- automatic multi-feature scanning; call the detector once per numeric signal

## 4. Input Schema

Use the common `pandas.DataFrame` input boundary from
`../input_output_contracts.md`.

Required schema:

```text
pd.DataFrame columns:
  time: datetime64[ns] or datetime-coercible timestamp
  value: numeric scalar
```

Function arguments follow `../input_output_contracts.md`:

```python
def detect_mann_whitney_u_wilcoxon_rank_sum_test(
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
- `reference_window` and `current_window` are required inclusive timestamp
  ranges for this batch method.
- Sort by `time_col` before slicing.
- Slice the two windows independently, then drop rows where `value_col` is
  missing or non-finite.
- Convert effective reference/current values to one-dimensional
  `numpy.ndarray[float64]`.
- Preserve original and effective sample sizes in `metadata` and
  `measurements`.
- Return `severity="not_applicable"` with `drift_detected=None` if the supplied
  schema cannot represent the required numeric two-window input.

## 5. Parameters

Method-specific parameters come from `drift_method_parameter_guide.md`,
`drift_method_variant_parameters.csv`, and the variant source document.

Required/optional params for the first implementation:

| Param | Type | Default | Applies to | Meaning |
|---|---:|---:|---|---|
| `variant_id` | string | `MANN_WHITNEY_TWO_SIDED` | all | One of the supported variant IDs. |
| `alpha` | float | `0.05` | all | Significance level for the p-value drift rule. Alias `threshold_or_alpha` may be accepted, but `alpha` is canonical in implementation code. |
| `alternative` | string | variant-derived | all | `two-sided`, `greater`, or `less`. |
| `direction_or_alternative` | string | `None` | one-sided | User-facing direction alias. Supports `current_increase`, `current_decrease`, `increase`, `decrease`, `up`, `down`, or backend alternatives `greater`/`less`. |
| `p_value_method` | string | `auto` | all | `auto`, `asymptotic`, or `exact`. Variant-specific defaults resolve this value. |
| `tie_correction` | bool | `True` | asymptotic/two-sided/one-sided | Whether tied ranks are allowed with asymptotic tie correction. Exact variant requires no ties. |
| `continuity_correction` | bool | `True` | asymptotic/two-sided/one-sided | Apply continuity correction for asymptotic p-value calculation. |
| `exact_method` | string | `scipy` | exact | Exact p-value engine/policy name recorded in metadata. |
| `exact_max_sample_size` | int | `8` | exact/auto | Maximum effective size in each window for exact calculation. |
| `exact_fallback` | string | `not_applicable` | exact | `not_applicable` or `asymptotic` when exact preconditions fail. |
| `min_reference_size` | int | `5` | all | Minimum effective reference sample size. |
| `min_current_size` | int | `5` | all | Minimum effective current sample size. |

Variant default resolution:

- `MANN_WHITNEY_TWO_SIDED`: `alternative="two-sided"`,
  `p_value_method="auto"`, asymptotic calculation unless `auto` selects exact
  under the exact preconditions.
- `MANN_WHITNEY_ONE_SIDED`: require direction. Because the statistical backend
  is called as `x=reference, y=current`, normalize user-facing current increase
  aliases (`current_increase`, `increase`, `up`) to backend
  `alternative="less"` and current decrease aliases (`current_decrease`,
  `decrease`, `down`) to backend `alternative="greater"`. If the caller passes
  raw backend alternatives `greater` or `less`, preserve them and record that
  orientation in metadata. If direction is absent, return `not_applicable`.
- `MANN_WHITNEY_EXACT`: force `p_value_method="exact"` unless the caller
  requests `exact_fallback="asymptotic"` and exact preconditions fail.

Reject or warn on params unrelated to this method, such as `feature_cols`,
`category_col`, `count_col`, `embedding_cols`, label columns, covariance
settings, or binning settings.

## 6. Output Measurements

Return canonical measurements in `DriftResult.measurements`:

- `DRIFT_ALARM_STATE`
- `P_VALUE`
- `TEST_STATISTIC`
- `SAMPLE_SIZE`

Measurement payload:

```python
{
    "TEST_STATISTIC": <float U statistic>,
    "P_VALUE": <float in [0, 1]>,
    "DRIFT_ALARM_STATE": <bool>,
    "SAMPLE_SIZE": {
        "reference": <effective_reference_n>,
        "current": <effective_current_n>,
        "dropped_reference": <dropped_reference_n>,
        "dropped_current": <dropped_current_n>,
    },
    "MANN_WHITNEY_U_STATISTIC": <same float as TEST_STATISTIC>,
    "RANK_BISERIAL_CORRELATION": <optional float effect-size helper>,
}
```

Top-level `DriftResult` fields:

- `method_id="DM-018"`
- `method_name="Mann-Whitney U / Wilcoxon Rank Sum Test"`
- `method_category="BatchDistributionComparison"`
- `variant_id=<resolved variant>`
- `test_statistic=<U statistic>`
- `p_value=<p-value>`
- `drift_score=<rank_biserial_correlation abs value if computed, else U statistic>`
- `threshold=<alpha>`
- `drift_detected=<p_value < alpha>` when applicable

`RANK_BISERIAL_CORRELATION` is not a catalog canonical measurement, so it is an
optional helper only. If included, it must be described as effect-size context,
not as the alarm rule.

## 7. Algorithm Steps

1. Merge `params` with defaults and resolve `variant_id`.
2. Validate `variant_id`; unsupported variants return `not_applicable`.
3. Resolve `alpha` from `params["alpha"]` or `params["threshold_or_alpha"]`;
   require `0 < alpha < 1`.
4. Resolve `alternative`:
   - two-sided variant -> `two-sided`
   - one-sided variant -> normalized caller direction, required
   - exact variant -> caller value or `two-sided`
5. Validate `time_col`, `value_col`, `reference_window`, and `current_window`.
6. Convert `time_col` to datetime, sort by time, and slice inclusive windows.
7. Drop invalid numeric values from each window and record original/effective
   counts.
8. Enforce `min_reference_size` and `min_current_size`.
9. Check ties across the pooled effective sample with duplicate numeric values.
10. Resolve p-value method:
    - `exact` for `MANN_WHITNEY_EXACT`
    - `exact` for `auto` only when both effective sample sizes are less than or
      equal to `exact_max_sample_size` and there are no ties
    - otherwise `asymptotic`
11. If exact was requested but exact preconditions fail:
    - return `not_applicable` when `exact_fallback="not_applicable"`
    - warn and use asymptotic when `exact_fallback="asymptotic"`
12. Call the statistical backend with:
    - `x=<reference_values>`
    - `y=<current_values>`
    - `alternative=<resolved alternative>`
    - `method=<resolved p_value_method>`
    - `use_continuity=<continuity_correction>` for asymptotic mode
13. Store the returned U statistic and p-value. The U statistic must be the
    statistic for the reference sample as returned by the backend.
14. Optionally compute rank-biserial correlation as
    `1 - (2 * U_reference) / (n_reference * n_current)` or the equivalent
    documented orientation; record the orientation in metadata.
15. Set `drift_detected = p_value < alpha`.
16. Set severity:
    - `drift_detected` when `drift_detected is True`
    - `normal` when `drift_detected is False`
    - `not_applicable` for validation/precondition failures
    - `error` only for unexpected calculation failures
17. Build interpretation text:
    - include variant, alternative, U statistic, p-value, alpha, effective
      sample sizes, and whether the rank/location shift rule fired
    - for one-sided variants, name the pre-specified direction
    - avoid causal or performance degradation claims without labels
18. Return `DriftResult` with canonical measurement keys, warnings, and metadata.

## 8. Drift Decision Rule

The null hypothesis is that reference and current samples come from the same
rank distribution, with the alternative determined by variant:

- `two-sided`: current and reference rank distributions differ in either
  direction.
- `greater`: reference values tend to be greater than current values if the
  backend uses `x=reference, y=current`; use this only when that orientation is
  explicitly intended.
- `less`: reference values tend to be less than current values if the backend
  uses `x=reference, y=current`; this corresponds to current values tending to
  increase relative to reference.

Implementation rule:

```python
drift_detected = p_value < alpha
```

Default `alpha` is `0.05`. Equality is not drift: `p_value == alpha` returns
`False`.

For report wording:

- `drift_detected=True`: "rank/location distribution drift candidate"
- `drift_detected=False`: "no statistically significant rank/location shift
  under this window and alpha"
- `drift_detected=None`: method was not applicable or calculation failed

The decision rule is based on p-value only. Effect-size helpers and sample
summaries may qualify interpretation but must not override the alarm state.

## 9. Warnings and Not-Applicable Conditions

Return `severity="not_applicable"` and `drift_detected=None` for:

- missing `time_col` or `value_col`
- non-datetime-coercible `time_col`
- non-numeric or boolean `value_col`
- missing `reference_window` or `current_window`
- empty reference or current window after slicing
- no finite numeric values after invalid rows are dropped
- effective sample size below `min_reference_size` or `min_current_size`
- unsupported `variant_id`
- one-sided variant without a pre-specified direction
- invalid `alpha`, `alternative`, `p_value_method`, or fallback policy
- exact variant with ties or sample size above `exact_max_sample_size` when
  `exact_fallback="not_applicable"`

Return `severity="normal"` or `severity="drift_detected"` with warnings when the
method can still run but interpretation needs caution:

- invalid rows were dropped from either window
- asymptotic p-value was used because exact mode was not appropriate
- ties were present; asymptotic tie correction was used
- sample sizes are very imbalanced, for example max(n) / min(n) > 10
- all values in both windows are identical; p-value should be non-significant
  and interpretation should note that no rank separation exists
- one-sided alternative direction may be easy to invert because the backend is
  called as `x=reference, y=current`; include orientation metadata

Unexpected backend exceptions should return `severity="error"` with the
exception class/message in warnings or metadata, without raising through the
public detector boundary.

## 10. Implementation Target

```text
module: drift_algorithm.methods.batchdistributioncomparison
function: detect_mann_whitney_u_wilcoxon_rank_sum_test
```

Expected dependencies:

- `pandas` for input normalization and window slicing
- `numpy` for finite numeric arrays and tie checks
- `scipy.stats.mannwhitneyu` for U statistic and p-value calculation

Helper functions should follow existing batch method patterns in
`drift_algorithm.methods.batchdistributioncomparison`:

- use the common `DriftResult` dataclass
- use `not_applicable_result` for validation failures when possible
- keep method-specific helpers private to the module unless shared by an already
  implemented method

## 11. Verification Plan

Create focused tests when implementation starts:

1. Two-sided no-drift:
   - reference/current generated from the same numeric distribution
   - assert `variant_id`, `P_VALUE`, `TEST_STATISTIC`,
     `DRIFT_ALARM_STATE=False`, `drift_detected=False`, and sample-size
     metadata.
2. Two-sided drift candidate:
   - current values shifted upward enough to produce `p_value < 0.05`
   - assert `severity="drift_detected"` and canonical measurements.
3. One-sided direction:
   - call with direction representing current increase and confirm the expected
     one-sided p-value is significant
   - call with the opposite direction and confirm it is not significant.
4. Exact variant:
   - small tie-free samples use exact method and record method metadata
   - tied or oversized samples return `not_applicable` by default.
5. Validation:
   - missing value column
   - non-numeric value column
   - missing windows
   - empty current/reference slices
   - sample size below minimum
   - unsupported variant.
6. Warning behavior:
   - NaN/non-finite values are dropped with warnings and effective counts
   - tied data in asymptotic mode reports tie-correction caution.

The test must assert canonical measurement keys, warning behavior, and the
documented `drift_detected` rule.

Recommended commands after implementation:

```text
python -m py_compile drift_algorithm\methods\batchdistributioncomparison.py
python -m pytest tests\test_mann_whitney_u_wilcoxon_rank_sum_test.py
python -m pytest tests\test_ks_test.py tests\test_wasserstein_distance.py
```
