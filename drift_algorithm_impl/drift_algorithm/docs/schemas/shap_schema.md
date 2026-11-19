# SHAP and Explanation Schema

## Applies To

Explanation drift methods.

Examples: SHAP Drift and tree feature based drift detection.

## DataFrame Columns

Wide SHAP format:

```text
time: datetime64[ns]
shap_<feature_1>: float
shap_<feature_2>: float
...
```

Long SHAP format:

```text
time: datetime64[ns]
feature: string
shap_value: float
```

Tree/domain feature format:

```text
time: datetime64[ns]
<feature columns>
```

## Parameters

- `shap_cols`: optional for wide format
- `feature_col`: default `feature` for long format
- `shap_value_col`: default `shap_value`
- `class_col`: optional
- `top_k_features`: optional

## Validation

The first implementation phase assumes explanation values are already computed.
Changes in explainer type, background dataset, model version, or preprocessing
must be recorded because they can change SHAP values without operational drift.

