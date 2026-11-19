# DM-054 Text Domain Classifier Drift Design

## 1. Method Identity

- Method ID: `DM-054`
- Method name: `Text Domain Classifier Drift`
- Category: `DomainClassifierMethod`
- Method kind: `detector`
- Status: `구현 완료`
- Source catalog: `drift_methods_catalog.md`
- Source variant document: `algorithm_variants/text_domain_classifier_drift_algorithm_variants.md`

## 2. Purpose

This method answers the drift question represented by `Text Domain Classifier Drift` in the
catalog. Primary input from the catalog: text, text embedding, descriptor.
Primary output from the catalog: ROC-AUC, domain classifier statistic.

## 3. Supported Variants

- `TEXT_DOMAIN_CLASSIFIER_ROC_AUC`
- `TEXT_DOMAIN_CLASSIFIER_STAT_TEST`
- `TEXT_DESCRIPTOR_DRIFT`

## 4. Input Schema

Use the common `pandas.DataFrame` input boundary from
`../input_output_contracts.md`.

Supported schema:

```text
Common: `time`
Text classifier variants: `text_col`, `embedding_cols`, `feature_cols`, or `value_col`
Descriptor variant: `descriptor_cols` or `text_col`
```

The implementation must validate the concrete columns through `params` and
return `severity="not_applicable"` if the supplied schema cannot represent this
method's required input.

## 5. Parameters

Method-specific parameters come from `drift_method_parameter_guide.md` and the
variant source document. The implementation should at minimum support:

- `variant_id`: one of the supported variant IDs.
- `text_col`: raw text column for bag-of-words vectorization.
- `embedding_cols` or `feature_cols`: optional precomputed text embedding or
  descriptor vectors for classifier variants.
- `descriptor_cols`: numeric text descriptor columns for `TEXT_DESCRIPTOR_DRIFT`.
- `auc_threshold`: ROC-AUC threshold, default `0.75`.
- `alpha`: p-value threshold for stat-test and descriptor drift, default `0.05`.
- `probability_threshold`: current-class probability tail cutoff, default `0.7`.
- `max_features`: maximum bag-of-words vocabulary size, default `100`.
- `min_reference_size` and `min_current_size`: default `20`.

## 6. Output Measurements

Return canonical measurements where applicable:

- `DRIFT_ALARM_STATE`
- `P_VALUE`
- `TEST_STATISTIC`
- `ROC_AUC`
- `DOMAIN_CLASSIFIER_SCORE`
- `TEXT_DOMAIN_CLASSIFIER_STATISTIC`
- `TEXT_DESCRIPTOR_DRIFT`
- `SIGNIFICANT_DESCRIPTORS`
- `PROBABILITY_MEAN_REFERENCE`
- `PROBABILITY_MEAN_CURRENT`
- `PROBABILITY_MEAN_DELTA`
- `HIGH_CURRENT_PROBABILITY_RATE`
- `TEXT_FEATURE_COLUMNS`

Always include `SAMPLE_SIZE` or relevant effective count metadata when the
method compares reference/current windows.

## 7. Algorithm Steps

1. Validate required DataFrame columns and parameter names.
2. Convert `time` to datetime and sort by time.
3. Split reference/current windows.
4. Convert text to bag-of-words frequency vectors or use supplied numeric
   embedding/descriptor columns.
5. Compute the variant-specific statistic:
   - centroid-domain classifier ROC-AUC for raw text or embeddings
   - KS test over classifier current-class probabilities
   - feature-wise KS tests over numeric text descriptors
6. Apply the documented p-value or threshold rule.
7. Return `DriftResult` with canonical measurement keys and interpretation text.

## 8. Drift Decision Rule

Implemented rules:

- `TEXT_DOMAIN_CLASSIFIER_ROC_AUC`: drift when text-domain ROC-AUC is at least
  `auc_threshold`.
- `TEXT_DOMAIN_CLASSIFIER_STAT_TEST`: drift when classifier probability KS
  p-value is below `alpha`.
- `TEXT_DESCRIPTOR_DRIFT`: drift when the minimum descriptor KS p-value is below
  `alpha`.

## 9. Warnings and Not-Applicable Conditions

Return warnings for:

- missing required columns
- empty reference/current windows
- sample size below method minimum
- unsupported variant id
- text columns with no usable tokens
- non-numeric embedding or descriptor values after cleaning
- invalid AUC, alpha, probability, or vocabulary thresholds

## 10. Implementation Target

```text
module: drift_algorithm.methods.domainclassifiermethod
function: detect_text_domain_classifier_drift
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
`detect_text_domain_classifier_drift`.

Implemented behavior:

- `TEXT_DOMAIN_CLASSIFIER_ROC_AUC` vectorizes raw text with a deterministic
  bag-of-words representation, or consumes supplied embedding/feature columns,
  then evaluates centroid-domain ROC-AUC.
- `TEXT_DOMAIN_CLASSIFIER_STAT_TEST` compares current-class probability score
  distributions with a KS test.
- `TEXT_DESCRIPTOR_DRIFT` compares numeric text descriptors with feature-wise KS
  tests and reports significant descriptors.
- unsupported variants, missing columns, invalid windows, invalid numeric
  values, empty token vocabulary, invalid thresholds, and insufficient samples
  return `not_applicable`.

Verification:

```text
py_compile: passed
DM-054 pytest: 5 passed
domain-classifier regression pytest: 10 passed
implemented numeric, streaming, supervised, multivariate, representation, explanation, and domain-classifier pytest: 231 passed
```
