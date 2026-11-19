# Sprint39 Runtime Family Backlog

## Summary

- runtimeWrapperMissing: 48
- familyCount: 6

## Classification Counts

- dedicated_wrapper_required: 5
- generic_runtime_candidate: 3
- out_of_scope_for_demo: 16
- requires_new_input_contract: 24

## Families

### P2 streaming_control_chart (3 pairs, generic_runtime_candidate)

- genericRuntimeKey: generic_streaming_control_chart
- methodCount: 3
- chartCount: 2
- strategy: one numeric stream control-chart runtime can cover CUSUM, EWMA, GMA, ECDD/HDDM/STEPD style alarm outputs after method-specific statistic adapters.
- topMethods: CUSUM=1, EWMA=1, Geometric Moving Average=1
- topCharts: CHART-CTRL-002=2, CHART-CTRL-001=1

### P3 streaming_change_point (4 pairs, dedicated_wrapper_required)

- genericRuntimeKey: n/a
- methodCount: 2
- chartCount: 2
- strategy: BOCD, SeqDrift, and SPRT require dedicated state/statistic wrappers before generic chart payload reuse.
- topMethods: ADWIN=2, SPRT=2
- topCharts: CHART-STREAM-001=2, CHART-STREAM-005=2

### P4 multivariate_embedding_distance (18 pairs, requires_new_input_contract)

- genericRuntimeKey: n/a
- methodCount: 8
- chartCount: 9
- strategy: requires feature matrix, embedding, kernel, or projection input contracts before runtime implementation.
- topMethods: Classifier 기반 embedding drift detection=3, Feature Map Drift=3, Autoencoder Representation Drift=3, Graph Embedding Drift=3, Wasserstein Distance=2, MMD=2, Energy Distance=1, LSDD=1
- topCharts: CHART-CLS-001=3, CHART-REP-001=3, CHART-REP-002=3, CHART-REP-003=3, CHART-MV-002=2, CHART-ANNOT-002=1, CHART-DIST-001=1, CHART-MV-001=1

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
