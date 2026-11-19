# DM-053 Classifier 기반 embedding drift detection Design

## 1. Method Identity

- Method ID: `DM-053`
- Method name: `Classifier 기반 embedding drift detection`
- Category: `DomainClassifierMethod`
- Method kind: `detector`
- Status: `구현 완료`
- Source catalog: `drift_methods_catalog.md`
- Source variant document: `algorithm_variants/classifier_embedding_drift_algorithm_variants.md`

## 2. Purpose

This method answers the drift question represented by `Classifier 기반 embedding drift detection` in the
catalog. Primary input from the catalog: embedding vector with domain label.
Primary output from the catalog: ROC-AUC, domain classifier score.

## 3. Supported Variants

- `DOMAIN_CLASSIFIER_ROC_AUC`
- `DOMAIN_CLASSIFIER_PROBABILITY_DRIFT`
- `CROSS_VALIDATED_DOMAIN_CLASSIFIER`

## 4. Input Schema

Use the common `pandas.DataFrame` input boundary from
`../input_output_contracts.md`.

Supported schema:

```text
Common: `time`
Embedding matrix: `embedding_cols`, `feature_cols`, or `value_col`
```

The implementation must validate the concrete columns through `params` and
return `severity="not_applicable"` if the supplied schema cannot represent this
method's required input.

## 5. Parameters

Method-specific parameters come from `drift_method_parameter_guide.md` and the
variant source document. The implementation should at minimum support:

- `variant_id`: one of the supported variant IDs.
- `embedding_cols` or `feature_cols`: numeric embedding columns.
- `auc_threshold`: ROC-AUC threshold for classifier-based variants, default
  `0.75`.
- `alpha`: p-value threshold for probability drift, default `0.05`.
- `probability_threshold`: current-class probability tail cutoff, default `0.7`.
- `cv_folds`: blocked cross-validation fold count, default `3`.
- `min_reference_size`, `min_current_size`, and `min_fold_size`.

## 6. Output Measurements

Return canonical measurements where applicable:

- `DRIFT_ALARM_STATE`
- `P_VALUE`
- `TEST_STATISTIC`
- `ROC_AUC`
- `DOMAIN_CLASSIFIER_SCORE`
- `PROBABILITY_MEAN_REFERENCE`
- `PROBABILITY_MEAN_CURRENT`
- `PROBABILITY_MEAN_DELTA`
- `HIGH_CURRENT_PROBABILITY_RATE`
- `CROSS_VALIDATION_FOLD_SCORES`
- `ROC_AUC_STD`
- `REFERENCE_SAMPLE_SIZE`
- `CURRENT_SAMPLE_SIZE`
- `EMBEDDING_COLUMNS`

Always include `SAMPLE_SIZE` or relevant effective count metadata when the
method compares reference/current windows.

## 7. Algorithm Steps

1. Validate required DataFrame columns and parameter names.
2. Convert `time` to datetime and sort by time.
3. Split reference/current windows.
4. Convert embedding columns to numeric arrays and drop invalid rows with
   warnings.
5. Compute a deterministic centroid-domain score that separates current from
   reference along the centroid-difference direction.
6. Apply the variant-specific rule:
   - ROC-AUC variant compares score AUC with `auc_threshold`.
   - probability drift variant compares reference/current current-class
     probability distributions with a KS p-value.
   - cross-validated variant evaluates blocked folds and compares mean AUC with
     `auc_threshold`.
7. Return `DriftResult` with canonical measurement keys and interpretation text.

## 8. Drift Decision Rule

Implemented rules:

- `DOMAIN_CLASSIFIER_ROC_AUC`: drift when centroid-domain ROC-AUC is at least
  `auc_threshold`.
- `DOMAIN_CLASSIFIER_PROBABILITY_DRIFT`: drift when current-class probability
  KS p-value is below `alpha`.
- `CROSS_VALIDATED_DOMAIN_CLASSIFIER`: drift when blocked-fold mean ROC-AUC is
  at least `auc_threshold`.

## 9. Warnings and Not-Applicable Conditions

Return warnings for:

- missing required columns
- empty reference/current windows
- sample size below method minimum
- unsupported variant id
- non-numeric embedding values after cleaning
- invalid AUC, alpha, probability, or fold thresholds
- insufficient rows for requested cross-validation folds

## 10. Implementation Target

```text
module: drift_algorithm.methods.domainclassifiermethod
function: detect_classifier_embedding_drift_detection
```

## 11. Verification Plan

Create at least two tests when implementation starts:

1. no-drift synthetic data with similar reference/current windows
2. drift-candidate synthetic data that changes the statistic or alarm in the
   expected direction

The test must assert canonical measurement keys, warning behavior, and the
documented `drift_detected` rule.

## 12. Implementation Notes

Implemented in `drift_algorithm.methods.domainclassifiermethod` as
`detect_classifier_embedding_drift_detection`.

Implemented behavior:

- `DOMAIN_CLASSIFIER_ROC_AUC` reports reference/current separability using a
  dependency-free centroid-domain classifier score.
- `DOMAIN_CLASSIFIER_PROBABILITY_DRIFT` converts centroid scores to current-class
  probabilities and compares probability distributions with a KS test.
- `CROSS_VALIDATED_DOMAIN_CLASSIFIER` uses blocked folds to estimate out-of-fold
  ROC-AUC and fold variability.
- unsupported variants, missing columns, invalid windows, invalid embedding
  values, invalid thresholds, and insufficient samples return `not_applicable`.

Verification:

```text
py_compile: passed
DM-053 pytest: 5 passed
domain/explanation regression pytest: 15 passed
implemented numeric, streaming, supervised, multivariate, representation, explanation, and domain-classifier pytest: 226 passed
```
