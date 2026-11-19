# Multivariate Schema

## Applies To

Multivariate distribution comparison and process-control methods.

Examples: Energy Distance, MMD, LSDD, Hotelling T2, MEWMA, Mahalanobis Distance.

## DataFrame Columns

```text
time: datetime64[ns]
<feature_1>: numeric
<feature_2>: numeric
...
```

Feature columns are supplied through `params["feature_cols"]`.

## Parameters

- `feature_cols`: required
- `scaling_policy`: optional
- `covariance_estimator`: optional
- `regularization`: optional
- `permutation_count`: optional for permutation p-values

## Validation

The implementation must verify that all feature columns are numeric and that the
effective matrix has enough rows for the selected statistic. Singular covariance
should produce a warning and use documented regularization if available.

