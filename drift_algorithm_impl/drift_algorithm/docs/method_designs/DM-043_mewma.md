# DM-043 MEWMA Design

## 1. Method Identity

- Method ID: `DM-043`
- Method name: `MEWMA`
- Category: `MultivariateProcessControl`
- Method kind: `detector`
- Status: `확정`
- Source catalog: `drift_methods_catalog.md`
- Source variant document: `algorithm_variants/mewma_algorithm_variants.md`

## 2. Purpose

This method answers the drift question represented by `MEWMA` in the
catalog. Primary input from the catalog: multivariate metric stream.
Primary output from the catalog: MEWMA statistic, control limit.

## 3. Supported Variants

- `MEWMA_STANDARD`
- `MEWMA_WITH_MAHALANOBIS_D2`

First implementation status:

- both variants support multivariate numeric input via `feature_cols` or
  `embedding_cols`
- MEWMA uses the reference window mean and covariance as the baseline
- `MEWMA_WITH_MAHALANOBIS_D2` exposes the same MEWMA statistic plus
  covariance-adjusted Mahalanobis D2
- optional regularized covariance is supported through diagonal loading

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

- `feature_cols` or `embedding_cols`
- `lambda` / `lambda_value`
- `alpha` or `threshold_or_alpha`
- `control_limit`
- `mean_vector_reference` (reserved; current implementation estimates from
  reference window)
- `covariance_estimator`
- `metric_scaling_policy`
- `regularization_strength`
- `min_reference_size`, `min_current_size`

## 6. Output Measurements

Return canonical measurements where applicable:

- `CONTROL_LIMIT`
- `DRIFT_ALARM_STATE`
- `MAHALANOBIS_DISTANCE`
- `MEWMA_STATISTIC`

Always include `SAMPLE_SIZE` or relevant effective count metadata when the
method compares reference/current windows.

First implementation canonical mapping:

- `MEWMA_STATISTIC`: maximum scaled MEWMA statistic observed during current
  replay
- `MAHALANOBIS_DISTANCE`: maximum unscaled Mahalanobis D2 of the MEWMA vector
- `CONTROL_LIMIT`: explicit limit or chi-square approximation from `alpha`
- `DRIFT_ALARM_STATE`: `normal` or `drift_detected`

Additional measurements:

- `TEST_STATISTIC`
- `FEATURE_DIMENSION`
- `FEATURE_COLUMNS`
- `LAMBDA`
- `FINAL_EWMA_VECTOR`
- `REFERENCE_MEAN_VECTOR`
- `ALARM_INDEX`, `ALARM_TIME`
- sample sizes

## 7. Algorithm Steps

1. Validate multivariate numeric feature columns.
2. Convert `time` to datetime, split reference/current windows, drop invalid
   timestamps or non-finite feature rows, and sort by time.
3. Estimate reference mean and covariance.
4. Optionally regularize the reference covariance.
5. Replay current rows chronologically and update the MEWMA vector.
6. Scale the Mahalanobis D2 by the finite-time MEWMA covariance factor.
7. Track the maximum statistic and first control-limit crossing.
8. Return `DriftResult` with canonical measurement keys and interpretation
   text.

## 8. Drift Decision Rule

The first implementation uses this MEWMA rule:

```text
z_t = lambda * x_t + (1 - lambda) * z_(t-1)
D2_t = (z_t - mu_ref)' Sigma_ref^-1 (z_t - mu_ref)
scale_t = lambda * (1 - (1 - lambda)^(2t)) / (2 - lambda)
MEWMA_t = D2_t / scale_t
drift if MEWMA_t > CONTROL_LIMIT
```

Defaults:

```text
lambda = 0.2
alpha = 0.01
control_limit = chi_square_quantile(1 - alpha, feature_dimension)
covariance_estimator = reference
metric_scaling_policy = covariance
regularization_strength = 1e-6
```

## 9. Warnings and Not-Applicable Conditions

Return warnings for:

- missing required columns
- empty reference/current windows
- sample size below method minimum
- unsupported variant id
- numerical instability such as singular covariance or zero-probability bins
- label-dependent methods called without labels or error stream
- missing feature columns
- fewer than two feature columns
- invalid lambda/control-limit/covariance parameter values
- ill-conditioned covariance matrices

## 10. Implementation Target

```text
module: drift_algorithm.methods.multivariateprocesscontrol
function: detect_mewma
```

## 11. Verification Plan

Implemented tests:

- no-drift multivariate stream
- drift-candidate multivariate stream
- Mahalanobis D2 variant with regularized covariance
- validation and warning behavior

Current test file:

```text
tests/test_mewma.py
```
