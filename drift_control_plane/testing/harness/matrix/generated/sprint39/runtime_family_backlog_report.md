# Sprint39 Runtime Family Backlog

## Summary

- runtimeWrapperMissing: 173
- familyCount: 10

## Classification Counts

- dedicated_wrapper_required: 10
- generic_runtime_candidate: 111
- out_of_scope_for_demo: 16
- requires_new_input_contract: 36

## Families

### P1 distribution_ecdf_window (26 pairs, generic_runtime_candidate)

- genericRuntimeKey: generic_distribution_ecdf_window
- methodCount: 5
- chartCount: 7
- strategy: one generic runtime can cover two-sample ECDF/statistic style methods.
- topMethods: KS Test=13, Anderson-Darling Test=4, Epps-Singleton Test=3, Cramer-von Mises Test=3, Kuiper's Test=3
- topCharts: CHART-EDF-001=10, CHART-EDF-002=4, CHART-DISTSHAPE-001=3, CHART-EDF-003=3, CHART-EDF-004=3, CHART-ANNOT-001=2, CHART-ANNOT-002=1

### P1 rank_mean_variance_window (17 pairs, generic_runtime_candidate)

- genericRuntimeKey: generic_statistical_test_window
- methodCount: 5
- chartCount: 4
- strategy: one numeric reference/current statistical-test runtime can cover rank, mean, and variance comparison methods.
- topMethods: Mann-Whitney U / Wilcoxon Rank Sum Test=4, t-test 계열=4, Baumgartner-Weiss-Schindler Test=3, F-test / Variance Test 계열=3, Levene's Test=3
- topCharts: CHART-RANK-001=6, CHART-VAR-001=6, CHART-MEAN-001=4, CHART-ANNOT-001=1

### P1 categorical_contingency_window (10 pairs, generic_runtime_candidate)

- genericRuntimeKey: generic_categorical_contingency_window
- methodCount: 3
- chartCount: 3
- strategy: one categorical frequency/contingency runtime can cover chi-square, G-test, and Fisher style variants.
- topMethods: Fisher's Exact Test=4, Chi-square Test=3, G-test=3
- topCharts: CHART-CAT-001=6, CHART-CAT-004=3, CHART-ANNOT-001=1

### P2 streaming_control_chart (33 pairs, generic_runtime_candidate)

- genericRuntimeKey: generic_streaming_control_chart
- methodCount: 11
- chartCount: 10
- strategy: one numeric stream control-chart runtime can cover CUSUM, EWMA, GMA, ECDD/HDDM/STEPD style alarm outputs after method-specific statistic adapters.
- topMethods: CUSUM=6, EWMA=4, Geometric Moving Average=4, ECDD-WT=3, HDDM-A=3, HDDM-W=3, STEPD=3, MEWMA=2
- topCharts: CHART-CTRL-002=6, CHART-ERR-005=6, CHART-ANNOT-001=4, CHART-CTRL-001=4, CHART-ERR-004=3, CHART-ERR-006=3, CHART-CTRL-003=2, CHART-ERR-001=2

### P2 probability_distance_window (25 pairs, generic_runtime_candidate)

- genericRuntimeKey: generic_probability_distance_window
- methodCount: 8
- chartCount: 7
- strategy: one probability/category distance runtime can cover KL, JS, Hellinger, Bhattacharyya, TV, L-infinity, and HINC families.
- topMethods: KL Divergence=4, Jensen-Shannon Distance=4, Total Variation Distance=3, L-Infinity Distance=3, Histogram Intersection Normalized Complement=3, Hellinger Distance=3, Bhattacharyya Distance=3, PSI=2
- topCharts: CHART-PROB-002=7, CHART-PROB-001=4, CHART-CAT-002=3, CHART-CAT-003=3, CHART-HIST-001=3, CHART-PROB-003=3, CHART-PSI-001=2

### P3 streaming_change_point (9 pairs, dedicated_wrapper_required)

- genericRuntimeKey: n/a
- methodCount: 4
- chartCount: 4
- strategy: BOCD, SeqDrift, and SPRT require dedicated state/statistic wrappers before generic chart payload reuse.
- topMethods: BOCD=3, ADWIN=2, SeqDrift=2, SPRT=2
- topCharts: CHART-BOCD-001=3, CHART-STREAM-001=2, CHART-STREAM-004=2, CHART-STREAM-005=2

### P4 multivariate_embedding_distance (30 pairs, requires_new_input_contract)

- genericRuntimeKey: n/a
- methodCount: 10
- chartCount: 11
- strategy: requires feature matrix, embedding, kernel, or projection input contracts before runtime implementation.
- topMethods: MMD=4, Classifier 기반 embedding drift detection=3, Energy Distance=3, LSDD=3, Hotelling T2=3, Mahalanobis Distance=3, Feature Map Drift=3, Autoencoder Representation Drift=3
- topCharts: CHART-MV-002=4, CHART-CLS-001=3, CHART-MV-001=3, CHART-MV-003=3, CHART-MV-004=3, CHART-MV-005=3, CHART-REP-001=3, CHART-REP-002=3

### P5 model_explanation_or_retraining (16 pairs, out_of_scope_for_demo)

- genericRuntimeKey: n/a
- methodCount: 6
- chartCount: 6
- strategy: needs model lifecycle, explanation, anomaly, or retraining workflow contracts; defer for current datasource demo.
- topMethods: DriftRetrainingClassifier=3, OCDD=3, SHAP Drift=3, Model Uncertainty Drift=3, HAT=2, Tree Feature 기반 감지=2
- topCharts: CHART-ADAPT-002=3, CHART-ANOM-001=3, CHART-EXPL-001=3, CHART-UNC-001=3, CHART-ADAPT-001=2, CHART-EXPL-002=2

### P5 text_semantic_drift (6 pairs, requires_new_input_contract)

- genericRuntimeKey: n/a
- methodCount: 2
- chartCount: 2
- strategy: requires text/embedding source schema and projection/reproducibility contract.
- topMethods: LLM Query / Semantic Distance 기반 감지=3, Text Domain Classifier Drift=3
- topCharts: CHART-TEXT-001=3, CHART-TEXT-002=3

### P6 unclassified_dedicated_review (1 pairs, dedicated_wrapper_required)

- genericRuntimeKey: n/a
- methodCount: 1
- chartCount: 1
- strategy: manual review required before implementation.
- topMethods: Generic / Fallback=1
- topCharts: CHART-GEN-001=1
