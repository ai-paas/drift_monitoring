# DM-056 DriftRetrainingClassifier Design

## 1. Method Identity

- Method ID: `DM-056`
- Method name: `DriftRetrainingClassifier`
- Category: `OperationalAdaptationMethod`
- Method kind: `operational`
- Status: `구현 완료`
- Source catalog: `drift_methods_catalog.md`
- Source variant document: `algorithm_variants/driftretrainingclassifier_algorithm_variants.md`

## 2. Purpose

This method answers the drift question represented by `DriftRetrainingClassifier` in the
catalog. Primary input from the catalog: base classifier, drift detector, labeled stream.
Primary output from the catalog: retraining event, post-retrain metric.

## 3. Supported Variants

- `DRIFT_RETRAINING_WITH_ADWIN`
- `DRIFT_RETRAINING_WITH_PAGE_HINKLEY`
- `DRIFT_RETRAINING_CHAMPION_CHALLENGER`

## 4. Input Schema

Use the common `pandas.DataFrame` input boundary from
`../input_output_contracts.md`.

Supported schema:

```text
Common: `time`
Metric stream: `metric_col`, `error_col`, or `value_col`
Label stream: `y_true`/`y_pred`
Champion/challenger: `champion_metric_col` and `challenger_metric_col`
Optional operational fields: `retraining_event_col`, `model_promoted_col`
```

The implementation must validate the concrete columns through `params` and
return `severity="not_applicable"` if the supplied schema cannot represent this
method's required input.

## 5. Parameters

Method-specific parameters come from `drift_method_parameter_guide.md` and the
variant source document. The implementation should at minimum support:

- `variant_id`: one of the supported variant IDs.
- `metric_col`, `error_col`, or `value_col`: numeric performance stream.
- `y_true` and `y_pred`: optional labels used to derive a 0/1 error metric.
- `metric_direction`: `higher_is_worse` or lower-is-worse style metric
  direction.
- `threshold` and `warning_threshold`: alarm thresholds for stream variants.
- `delta`: Page-Hinkley tolerance term.
- `champion_metric_col`, `challenger_metric_col`, and `uplift_threshold`.
- `retraining_event_col` and `model_promoted_col`.
- `min_reference_size` and `min_current_size`.

## 6. Output Measurements

Return canonical measurements where applicable:

- `DRIFT_ALARM_STATE`
- `P_VALUE`
- `TEST_STATISTIC`
- `RETRAINING_EVENT`
- `ADAPTATION_EVENT`
- `ONLINE_OR_PRE_POST_PERFORMANCE`
- `RETRAINING_CANDIDATE_WINDOW`
- `PROMOTION_DECISION`
- `CHAMPION_CHALLENGER_UPLIFT`
- `REFERENCE_METRIC_MEAN`
- `CURRENT_METRIC_MEAN`
- `METRIC_MEAN_DELTA`

Always include `SAMPLE_SIZE` or relevant effective count metadata when the
method compares reference/current windows.

## 7. Algorithm Steps

1. Validate required DataFrame columns and parameter names.
2. Convert `time` to datetime and sort by time.
3. Split reference/current windows.
4. Derive or validate the performance metric stream.
5. Replay the operational retraining policy:
   - ADWIN-style variant compares current/reference metric mean movement.
   - Page-Hinkley-style variant accumulates sustained metric degradation.
   - Champion/challenger variant compares model metrics and promotion flags.
6. Apply threshold, uplift, and event rules.
7. Return `DriftResult` with canonical measurement keys and interpretation text.

## 8. Drift Decision Rule

Implemented rules:

- `DRIFT_RETRAINING_WITH_ADWIN`: drift when directional current/reference metric
  delta exceeds `threshold` or retraining event flags are observed.
- `DRIFT_RETRAINING_WITH_PAGE_HINKLEY`: drift when cumulative Page-Hinkley-style
  metric degradation exceeds `threshold` or retraining event flags are observed.
- `DRIFT_RETRAINING_CHAMPION_CHALLENGER`: drift when challenger uplift exceeds
  `uplift_threshold` or model promotion flags are observed.

## 9. Warnings and Not-Applicable Conditions

Return warnings for:

- missing required columns
- empty reference/current windows
- sample size below method minimum
- unsupported variant id
- missing metric or label stream inputs
- missing champion/challenger metric columns for champion/challenger variant
- non-numeric metric values after cleaning
- invalid thresholds or sample-size settings

## 10. Implementation Target

```text
module: drift_algorithm.methods.operationaladaptationmethod
function: detect_driftretrainingclassifier
```

## 11. Verification Plan

Create at least two tests when implementation starts:

1. no-drift synthetic data with similar reference/current windows
2. drift-candidate synthetic data that changes the statistic or alarm in the
   expected direction

The test must assert canonical measurement keys, warning behavior, and the
documented `drift_detected` rule.

## 12. Implementation Notes

Implemented in `drift_algorithm.methods.operationaladaptationmethod` as
`detect_driftretrainingclassifier`.

Implemented behavior:

- `DRIFT_RETRAINING_WITH_ADWIN` replays metric mean movement as an ADWIN-style
  retraining trigger surrogate.
- `DRIFT_RETRAINING_WITH_PAGE_HINKLEY` replays sustained metric degradation with
  a Page-Hinkley-style cumulative statistic.
- `DRIFT_RETRAINING_CHAMPION_CHALLENGER` compares champion and challenger
  metrics and promotion flags.
- this implementation does not train, retrain, deploy, or promote a model; it
  consumes finite operational logs.
- unsupported variants, missing columns, invalid windows, invalid metric values,
  invalid thresholds, and insufficient samples return `not_applicable`.

Verification:

```text
py_compile: passed
DM-056 pytest: 5 passed
operational regression pytest: 10 passed
implemented numeric, streaming, supervised, multivariate, representation, explanation, domain-classifier, and operational pytest: 241 passed
```
