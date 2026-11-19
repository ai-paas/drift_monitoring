# Drift Algorithm Schema Overview

## Purpose

The public input boundary is `pandas.DataFrame`, but drift methods operate on
different logical data families. This document maps method categories to those
families.

## Schema Families

| Schema family | Typical columns | Method categories |
|---|---|---|
| Numeric | `time`, `value` | Batch numeric tests, streaming detectors |
| Categorical | `time`, `category`, `count` | Count/frequency tests and categorical distances |
| Probability | `time`, `class`, `probability` or wide `prob_*` | KL, JS, Hellinger, TV, L-infinity |
| Multivariate | `time`, feature columns | Energy, MMD, LSDD, Hotelling T2, MEWMA, Mahalanobis |
| Embedding | `time`, `emb_*` or `embedding` | Representation and classifier-based drift |
| Label/Error | `time`, `y_true`, `y_pred` or `error` | DDM/RDDM/EDDM/HDDM/STEPD/HAT |
| Text | `time`, `text`, optional embedding | LLM query and text domain classifier drift |
| SHAP/Explanation | `time`, `shap_*` or long SHAP rows | SHAP and tree/explanation drift |

## Schema Versioning

Initial schema version is `v1`. Add a new schema version only when a breaking
change is made to required columns or result semantics. Additive optional
columns do not require a new version.

## Input Signal

Every request should record an `input_signal` in metadata, for example:

```text
feature
score
error_rate
embedding
text
shap_value
prediction_distribution
```

The same method can have different interpretation depending on `input_signal`.
For example, ADWIN on `error_rate` is supervised performance drift; ADWIN on a
feature value is numeric stream drift.

