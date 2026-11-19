# DM-048 Graph Embedding Drift Design

## 1. Method Identity

- Method ID: `DM-048`
- Method name: `Graph Embedding Drift`
- Category: `RepresentationDriftMethod`
- Method kind: `detector`
- Status: `확정`
- Source catalog: `drift_methods_catalog.md`
- Source variant document: `algorithm_variants/graph_embedding_drift_algorithm_variants.md`

## 2. Purpose

This method answers the drift question represented by `Graph Embedding Drift` in the
catalog. Primary input from the catalog: graph/node embedding.
Primary output from the catalog: embedding drift score.

## 3. Supported Variants

- `GRAPH_EMBEDDING_MMD`
- `GRAPH_EMBEDDING_CENTROID_SHIFT`
- `NODE_REPRESENTATION_DRIFT`

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
function: detect_graph_embedding_drift
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
`detect_graph_embedding_drift`.

Supported first-pass behavior:

- `GRAPH_EMBEDDING_MMD`
  - standardizes graph embedding vectors by reference-window mean and standard
    deviation
  - computes RBF-kernel MMD
  - supports optional permutation p-value calibration through
    `permutation_count`
- `GRAPH_EMBEDDING_CENTROID_SHIFT`
  - computes standardized reference/current centroid shift
  - also reports centroid cosine distance
  - uses explicit `threshold` when supplied, otherwise a reference distance
    quantile from `alpha`
- `NODE_REPRESENTATION_DRIFT`
  - uses `node_group_col` / `group_col` when supplied
  - computes groupwise centroid shift and group alarm states
  - falls back to row-level distance from the reference centroid when no group
    column is supplied

Common measurements include:

- `TEST_STATISTIC`
- `P_VALUE`
- `DRIFT_ALARM_STATE`
- `GRAPH_EMBEDDING_DRIFT_SCORE`
- `CENTROID_SHIFT`
- `COSINE_DISTANCE`
- `NODE_GROUP_SCORES`
- `TOP_NODE_GROUP`
- `SAMPLE_SIZE_REFERENCE`
- `SAMPLE_SIZE_CURRENT`
- `FEATURE_DIMENSION`

Not-applicable behavior covers unsupported variants, missing embedding or group
columns, invalid windows, insufficient sample sizes, invalid alpha / threshold /
bandwidth / permutation settings, and node groups that do not meet
`min_group_size`.

## 13. Verification Result

Checks run:

```powershell
python -m py_compile drift_algorithm\methods\representationdriftmethod.py tests\test_graph_embedding_drift.py
python -m pytest tests\test_graph_embedding_drift.py -q
python -m pytest tests\test_ocdd.py tests\test_feature_map_drift.py tests\test_autoencoder_representation_drift.py tests\test_graph_embedding_drift.py -q
python -m pytest tests\test_ks_test.py tests\test_wasserstein_distance.py tests\test_mann_whitney_u_wilcoxon_rank_sum_test.py tests\test_t_test.py tests\test_levene_s_test.py tests\test_anderson_darling_test.py tests\test_cramer_von_mises_test.py tests\test_kuiper_s_test.py tests\test_baumgartner_weiss_schindler_test.py tests\test_f_test_variance_test.py tests\test_energy_distance.py tests\test_epps_singleton_test.py tests\test_mmd.py tests\test_lsdd.py tests\test_adwin.py tests\test_kswin.py tests\test_page_hinkley_test.py tests\test_cusum.py tests\test_ewma.py tests\test_geometric_moving_average.py tests\test_bocd.py tests\test_seqdrift.py tests\test_ddm.py tests\test_rddm.py tests\test_eddm.py tests\test_ecdd_wt.py tests\test_hddm_a.py tests\test_hddm_w.py tests\test_stepd.py tests\test_hotelling_t2.py tests\test_mewma.py tests\test_mahalanobis_distance.py tests\test_ocdd.py tests\test_feature_map_drift.py tests\test_autoencoder_representation_drift.py tests\test_graph_embedding_drift.py -q
```

Results:

```text
py_compile: passed
DM-048 pytest: 5 passed
representation regression pytest: 20 passed
implemented numeric, streaming, supervised, multivariate, and representation pytest: 201 passed
```
