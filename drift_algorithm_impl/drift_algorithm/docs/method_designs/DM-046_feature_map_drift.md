# DM-046 Feature Map Drift Design

## 1. Method Identity

- Method ID: `DM-046`
- Method name: `Feature Map Drift`
- Category: `RepresentationDriftMethod`
- Method kind: `detector`
- Status: `확정`
- Source catalog: `drift_methods_catalog.md`
- Source variant document: `algorithm_variants/feature_map_drift_algorithm_variants.md`

## 2. Purpose

This method answers the drift question represented by `Feature Map Drift` in the
catalog. Primary input from the catalog: model intermediate feature map.
Primary output from the catalog: layerwise drift score.

## 3. Supported Variants

- `MODEL_FEATURE_MAP_KS`
- `MODEL_FEATURE_MAP_MMD`
- `LAYERWISE_FEATURE_MAP_DRIFT`

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

- `DRIFT_ALARM_STATE`
- `P_VALUE`
- `TEST_STATISTIC`

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
module: drift_algorithm.methods.representationdriftmethod
function: detect_feature_map_drift
```

## 11. Verification Plan

Create at least two tests when implementation starts:

1. no-drift synthetic data with similar reference/current windows
2. drift-candidate synthetic data that changes the statistic or alarm in the
   expected direction

The test must assert canonical measurement keys, warning behavior, and the
documented `drift_detected` rule.

## 12. Implementation Notes

Implemented in `drift_algorithm.methods.representationdriftmethod` as
`detect_feature_map_drift`.

Supported first-pass behavior:

- `MODEL_FEATURE_MAP_KS`
  - runs axis-wise two-sample KS tests for each feature-map column
  - reports the maximum KS statistic, minimum p-value, significant feature
    count, and significant feature fraction
- `MODEL_FEATURE_MAP_MMD`
  - computes RBF-kernel MMD over the full feature-map vector
  - supports optional permutation p-value calibration through
    `permutation_count`
  - uses median pairwise distance as the default kernel bandwidth
- `LAYERWISE_FEATURE_MAP_DRIFT`
  - accepts `layer_feature_cols` as a mapping of layer name to feature columns
  - computes layer-level MMD for multi-feature layers and KS for single-feature
    layers
  - reports per-layer statistics, p-values, and alarm states

Threshold behavior:

- p-value variants use `p_value < alpha` for the final drift decision
- MMD without permutation p-value uses explicit `threshold`; if no threshold is
  supplied the score is reported with threshold `0.0`
- `threshold_or_alpha` is accepted as an `alpha` alias

Common measurements include:

- `TEST_STATISTIC`
- `P_VALUE`
- `DRIFT_ALARM_STATE`
- `FEATURE_MAP_DRIFT_SCORE`
- `MAX_FEATURE_STATISTIC`
- `SIGNIFICANT_FEATURE_COUNT`
- `SIGNIFICANT_FEATURE_FRACTION`
- `LAYERWISE_SCORES`
- `SAMPLE_SIZE_REFERENCE`
- `SAMPLE_SIZE_CURRENT`
- `FEATURE_DIMENSION`

Not-applicable behavior covers unsupported variants, missing or univariate
feature input, invalid windows, insufficient sample sizes, invalid alpha /
threshold / bandwidth / permutation settings, and duplicate layer feature
columns.

## 13. Verification Result

Checks run:

```powershell
python -m py_compile drift_algorithm\methods\representationdriftmethod.py tests\test_feature_map_drift.py
python -m pytest tests\test_feature_map_drift.py -q
python -m pytest tests\test_ocdd.py tests\test_feature_map_drift.py -q
python -m pytest tests\test_ks_test.py tests\test_wasserstein_distance.py tests\test_mann_whitney_u_wilcoxon_rank_sum_test.py tests\test_t_test.py tests\test_levene_s_test.py tests\test_anderson_darling_test.py tests\test_cramer_von_mises_test.py tests\test_kuiper_s_test.py tests\test_baumgartner_weiss_schindler_test.py tests\test_f_test_variance_test.py tests\test_energy_distance.py tests\test_epps_singleton_test.py tests\test_mmd.py tests\test_lsdd.py tests\test_adwin.py tests\test_kswin.py tests\test_page_hinkley_test.py tests\test_cusum.py tests\test_ewma.py tests\test_geometric_moving_average.py tests\test_bocd.py tests\test_seqdrift.py tests\test_ddm.py tests\test_rddm.py tests\test_eddm.py tests\test_ecdd_wt.py tests\test_hddm_a.py tests\test_hddm_w.py tests\test_stepd.py tests\test_hotelling_t2.py tests\test_mewma.py tests\test_mahalanobis_distance.py tests\test_ocdd.py tests\test_feature_map_drift.py -q
```

Results:

```text
py_compile: passed
DM-046 pytest: 5 passed
representation regression pytest: 10 passed
implemented numeric, streaming, supervised, multivariate, and representation pytest: 191 passed
```
