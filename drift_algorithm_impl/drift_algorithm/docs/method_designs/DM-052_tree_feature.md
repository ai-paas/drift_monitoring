# DM-052 Tree Feature 기반 감지 Design

## 1. Method Identity

- Method ID: `DM-052`
- Method name: `Tree Feature 기반 감지`
- Category: `ExplanationDriftMethod`
- Method kind: `detector`
- Status: `구현 완료`
- Source catalog: `drift_methods_catalog.md`
- Source variant document: `algorithm_variants/tree_feature_drift_algorithm_variants.md`

## 2. Purpose

This method answers the drift question represented by `Tree Feature 기반 감지` in the
catalog. Primary input from the catalog: time feature가 포함된 tabular data.
Primary output from the catalog: time split count, feature importance.

## 3. Supported Variants

- `TIME_FEATURE_SPLIT_DETECTOR`
- `DOMAIN_CLASSIFIER_TREE`

## 4. Input Schema

Use the common `pandas.DataFrame` input boundary from
`../input_output_contracts.md`.

Supported schema:

```text
Common: `time`
Wide numeric feature matrix: `feature_cols` or `value_col`
TIME_FEATURE_SPLIT_DETECTOR: `time_feature_col` included in `feature_cols`
```

The implementation must validate the concrete columns through `params` and
return `severity="not_applicable"` if the supplied schema cannot represent this
method's required input.

## 5. Parameters

Method-specific parameters come from `drift_method_parameter_guide.md` and the
variant source document. The implementation should at minimum support:

- `variant_id`: one of the supported variant IDs.
- `feature_cols`: numeric feature columns used by the tree-style detector.
- `time_feature_col`: time/period indicator feature for
  `TIME_FEATURE_SPLIT_DETECTOR`.
- `auc_threshold`: ROC-AUC threshold for `DOMAIN_CLASSIFIER_TREE`, default
  `0.75`.
- `split_accuracy_threshold`: split accuracy threshold for
  `TIME_FEATURE_SPLIT_DETECTOR`, default `0.75`.
- `min_reference_size` and `min_current_size`: default `20`.

## 6. Output Measurements

Return canonical measurements where applicable:

- `FEATURE_IMPORTANCE_OR_RANK`
- `ROC_AUC`
- `TREE_SPLIT_SIGNAL`
- `TEST_STATISTIC`
- `DRIFT_ALARM_STATE`
- `THRESHOLD`
- `METHOD_POLICY`
- `REFERENCE_SAMPLE_SIZE`
- `CURRENT_SAMPLE_SIZE`
- `FEATURE_COLUMNS`

Always include `SAMPLE_SIZE` or relevant effective count metadata when the
method compares reference/current windows.

## 7. Algorithm Steps

1. Validate required DataFrame columns and parameter names.
2. Convert `time` to datetime and sort by time.
3. Split reference/current windows.
4. Convert feature columns to numeric arrays and drop invalid rows with warnings.
5. Compute feature-wise decision-stump separation scores against the
   reference/current domain label.
6. Apply the variant rule:
   - time feature split detector: the configured time feature must be the best
     split and exceed split accuracy threshold.
   - domain classifier tree: the best feature's univariate ROC-AUC must exceed
     `auc_threshold`.
7. Return `DriftResult` with canonical measurement keys and interpretation text.

## 8. Drift Decision Rule

Implemented rules:

- `TIME_FEATURE_SPLIT_DETECTOR`: drift when `time_feature_col` is the best
  univariate split and its split accuracy is at least `split_accuracy_threshold`.
- `DOMAIN_CLASSIFIER_TREE`: drift when the best univariate domain classifier
  ROC-AUC is at least `auc_threshold`.

## 9. Warnings and Not-Applicable Conditions

Return warnings for:

- missing required columns
- empty reference/current windows
- sample size below method minimum
- unsupported variant id
- non-numeric feature values after cleaning
- `TIME_FEATURE_SPLIT_DETECTOR` called without `time_feature_col` in
  `feature_cols`
- invalid AUC or split thresholds

## 10. Implementation Target

```text
module: drift_algorithm.methods.explanationdriftmethod
function: detect_tree_feature
```

## 11. Verification Plan

Create at least two tests when implementation starts:

1. no-drift synthetic data with similar reference/current windows
2. drift-candidate synthetic data that changes the statistic or alarm in the
   expected direction

The test must assert canonical measurement keys, warning behavior, and the
documented `drift_detected` rule.

## 12. Implementation Notes

Implemented in `drift_algorithm.methods.explanationdriftmethod` as
`detect_tree_feature`.

Implemented behavior:

- `TIME_FEATURE_SPLIT_DETECTOR` uses a deterministic decision-stump surrogate and
  reports whether the configured time/period feature is the top shallow split.
- `DOMAIN_CLASSIFIER_TREE` uses the best univariate stump as a dependency-free
  tree classifier surrogate for reference/current separability.
- feature importance is reported as normalized domain separation strength with
  split threshold, split direction, split accuracy, and ROC-AUC metadata.
- unsupported variants, missing columns, invalid thresholds, invalid windows,
  invalid feature values, and insufficient samples return `not_applicable`.

Verification:

```text
py_compile: passed
DM-052 pytest: 5 passed
explanation regression pytest: 10 passed
implemented numeric, streaming, supervised, multivariate, representation, and explanation pytest: 221 passed
```
