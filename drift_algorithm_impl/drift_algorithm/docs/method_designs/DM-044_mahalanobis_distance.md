# DM-044 Mahalanobis Distance Design

## 1. Method Identity

- Method ID: `DM-044`
- Method name: `Mahalanobis Distance`
- Category: `MultivariateProcessControl`
- Method kind: `detector`
- Status: `확정`
- Source catalog: `drift_methods_catalog.md`
- Source variant document: `algorithm_variants/mahalanobis_distance_algorithm_variants.md`

## 2. Purpose

This method answers the drift question represented by `Mahalanobis Distance` in the
catalog. Primary input from the catalog: multivariate feature, embedding summary.
Primary output from the catalog: D2 distance, outlier/window score.

## 3. Supported Variants

- `SAMPLE_MAHALANOBIS_OUTLIER`
- `WINDOW_MEAN_MAHALANOBIS`
- `ROBUST_MAHALANOBIS`

## 4. Input Schema

Use the common `pandas.DataFrame` input boundary from
`../input_output_contracts.md`.

Required schema:

```text
multivariate_schema.md or embedding_schema.md. Required: `time` plus feature/embedding columns supplied through params.
```

The implementation must validate the concrete columns through `params` and
return `severity="not_applicable"` if the supplied schema cannot represent this
method's required input.

## 5. Parameters

Method-specific parameters come from `drift_method_parameter_guide.md` and the
variant source document. The implementation should at minimum support:

- `alpha` or threshold parameter when the method uses a p-value or alarm limit.
- `min_reference_size` and `min_current_size` for batch methods.
- `feature_cols`, `category_col`, `count_col`, `embedding_cols`, or label/error
  column names when applicable.

## 6. Output Measurements

Return canonical measurements where applicable:

- `MAHALANOBIS_DISTANCE`
- `METHOD_POLICY`
- `OUTLIER_FLAG`
- `THRESHOLD_EXCEEDANCE`

Always include `SAMPLE_SIZE` or relevant effective count metadata when the
method compares reference/current windows.

## 7. Algorithm Steps

1. Validate required DataFrame columns and parameter names.
2. Convert `time` to datetime and sort by time.
3. Split reference/current windows or iterate the stream according to the method
   category.
4. Convert validated values to `numpy.ndarray` when numeric calculation starts.
5. Compute the method-specific statistic, distance, score, alarm state, or event.
6. Apply the documented p-value, threshold, control-limit, or policy rule.
7. Return `DriftResult` with canonical measurement keys and interpretation text.

## 8. Drift Decision Rule

The first implementation should use the variant document's default rule when it
is explicit. If no default is explicit, use:

- p-value methods: `p_value < params.get("alpha", 0.05)`
- distance/score methods: compare with `params["threshold"]`; if absent, return
  score with `drift_detected=None`
- streaming alarm methods: final detector alarm state
- supervised methods: warning/drift state from the detector logic

## 9. Warnings and Not-Applicable Conditions

Return warnings for:

- missing required columns
- empty reference/current windows
- sample size below method minimum
- unsupported variant id
- numerical instability such as singular covariance or zero-probability bins
- label-dependent methods called without labels or error stream

## 10. Implementation Target

```text
module: drift_algorithm.methods.multivariateprocesscontrol
function: detect_mahalanobis_distance
```

## 11. Verification Plan

Create at least two tests when implementation starts:

1. no-drift synthetic data with similar reference/current windows
2. drift-candidate synthetic data that changes the statistic or alarm in the
   expected direction

The test must assert canonical measurement keys, warning behavior, and the
documented `drift_detected` rule.

## 12. Implementation Notes

Implemented in `drift_algorithm.methods.multivariateprocesscontrol` as
`detect_mahalanobis_distance`.

Supported first-pass behavior:

- `WINDOW_MEAN_MAHALANOBIS`
  - reference-window mean/covariance defines the baseline
  - current-window mean is scored as Mahalanobis D2 against the baseline
  - explicit `threshold` / `control_limit` is used when supplied
  - otherwise a chi-square D2 limit from `alpha` and feature dimension is used
- `SAMPLE_MAHALANOBIS_OUTLIER`
  - each current sample is scored against the reference baseline
  - reports max D2, outlier count, and outlier fraction
  - drift is true when any sample exceeds the D2 threshold unless
    `outlier_fraction_threshold` is supplied
- `ROBUST_MAHALANOBIS`
  - uses median center and MAD-based diagonal covariance
  - intended as a deterministic robust approximation without adding new
    dependencies

Common measurements include:

- `MAHALANOBIS_DISTANCE`
- `MAHALANOBIS_D2`
- `P_VALUE`
- `CONTROL_LIMIT`
- `METHOD_POLICY`
- `OUTLIER_FLAG`
- `THRESHOLD_EXCEEDANCE`
- `OUTLIER_COUNT`
- `OUTLIER_FRACTION`
- `SAMPLE_SIZE_REFERENCE`
- `SAMPLE_SIZE_CURRENT`
- `FEATURE_DIMENSION`

Not-applicable behavior covers unsupported variants, missing or univariate
feature input, invalid windows, insufficient sample sizes, invalid threshold /
alpha configuration, and non-finite numeric inputs after cleaning.

## 13. Verification Result

Checks run:

```powershell
python -m py_compile drift_algorithm\methods\multivariateprocesscontrol.py tests\test_mahalanobis_distance.py
python -m pytest tests\test_mahalanobis_distance.py -q
python -m pytest tests\test_hotelling_t2.py tests\test_mewma.py tests\test_mahalanobis_distance.py -q
python -m pytest tests\test_ks_test.py tests\test_wasserstein_distance.py tests\test_mann_whitney_u_wilcoxon_rank_sum_test.py tests\test_t_test.py tests\test_levene_s_test.py tests\test_anderson_darling_test.py tests\test_cramer_von_mises_test.py tests\test_kuiper_s_test.py tests\test_baumgartner_weiss_schindler_test.py tests\test_f_test_variance_test.py tests\test_energy_distance.py tests\test_epps_singleton_test.py tests\test_mmd.py tests\test_lsdd.py tests\test_adwin.py tests\test_kswin.py tests\test_page_hinkley_test.py tests\test_cusum.py tests\test_ewma.py tests\test_geometric_moving_average.py tests\test_bocd.py tests\test_seqdrift.py tests\test_ddm.py tests\test_rddm.py tests\test_eddm.py tests\test_ecdd_wt.py tests\test_hddm_a.py tests\test_hddm_w.py tests\test_stepd.py tests\test_hotelling_t2.py tests\test_mewma.py tests\test_mahalanobis_distance.py -q
```

Results:

```text
py_compile: passed
DM-044 pytest: 5 passed
multivariate process control pytest: 14 passed
implemented numeric, streaming, supervised, and multivariate pytest: 181 passed
```
