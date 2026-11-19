# DM-042 Hotelling T2 Design

## 1. Method Identity

- Method ID: `DM-042`
- Method name: `Hotelling T2`
- Category: `MultivariateProcessControl`
- Method kind: `detector`
- Status: `확정`
- Source catalog: `drift_methods_catalog.md`
- Source variant document: `algorithm_variants/hotelling_t2_algorithm_variants.md`

## 2. Purpose

This method answers the drift question represented by `Hotelling T2` in the
catalog. Primary input from the catalog: multivariate numeric window.
Primary output from the catalog: T2 statistic, p-value/control limit.

## 3. Supported Variants

- `HOTELLING_T2_ONE_SAMPLE_PHASE_II`
- `HOTELLING_T2_TWO_SAMPLE`
- `REGULARIZED_HOTELLING_T2`

First implementation status:

- all three variants support multivariate numeric input via `feature_cols` or
  `embedding_cols`
- `HOTELLING_T2_TWO_SAMPLE` uses pooled covariance and the standard
  two-sample F approximation
- `HOTELLING_T2_ONE_SAMPLE_PHASE_II` compares current-window mean against the
  reference mean/covariance estimate
- `REGULARIZED_HOTELLING_T2` supports diagonal loading and shrinkage covariance
  regularization
- PCA preprocessing is not implemented in the first implementation

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
- `alpha` or `threshold_or_alpha`
- `control_limit`
- `min_reference_size`, `min_current_size`
- `covariance_estimator`
- `regularization_strength` or `shrinkage_alpha`
- `regularization_method`
- `sample_imbalance_warning_ratio`
- `condition_number_warning`

## 6. Output Measurements

Return canonical measurements where applicable:

- `CONTROL_LIMIT`
- `DRIFT_ALARM_STATE`
- `HOTELLING_T2_STATISTIC`
- `METHOD_POLICY`
- `P_VALUE`

Always include `SAMPLE_SIZE` or relevant effective count metadata when the
method compares reference/current windows.

First implementation canonical mapping:

- `HOTELLING_T2_STATISTIC`: standard or regularized T2 statistic
- `P_VALUE`: F-approximation p-value where available
- `CONTROL_LIMIT`: explicit control limit or alpha-derived F-approximation
  limit
- `DRIFT_ALARM_STATE`: `normal` or `drift_detected`
- `METHOD_POLICY`: covariance / regularization policy used

Additional measurements:

- `TEST_STATISTIC`
- `FEATURE_DIMENSION`
- `MEAN_DIFFERENCE_VECTOR`
- `FEATURE_COLUMNS`
- sample sizes

## 7. Algorithm Steps

1. Validate multivariate numeric feature columns.
2. Convert `time` to datetime, split reference/current windows, drop invalid
   timestamps or non-finite feature rows, and sort by time.
3. Convert reference/current windows to numeric matrices.
4. Estimate reference covariance, pooled covariance, or regularized covariance
   according to the variant.
5. Compute the T2 statistic from the mean difference vector.
6. Compute an F-approximation p-value/control limit where available, or compare
   against an explicit regularized control limit.
7. Return `DriftResult` with canonical measurement keys and interpretation
   text.

## 8. Drift Decision Rule

The first implementation uses these rules:

- two-sample T2: drift if `p_value < alpha` or `T2 > CONTROL_LIMIT`
- Phase II T2: drift if `p_value < alpha` or `T2 > CONTROL_LIMIT`
- regularized T2: drift if `T2 > CONTROL_LIMIT`; if no explicit control limit
  is supplied, an approximate alpha-derived limit is used and reported with a
  regularization warning

Defaults:

```text
alpha = 0.05
covariance_estimator = pooled
regularization_method = diagonal_loading
regularization_strength = 1e-6, or 1e-3 for REGULARIZED_HOTELLING_T2 when omitted
min_reference_size = feature_dimension + 2
min_current_size = feature_dimension + 2
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
- PCA preprocessing requested
- sample size too small for the selected F approximation
- ill-conditioned covariance matrices

## 10. Implementation Target

```text
module: drift_algorithm.methods.multivariateprocesscontrol
function: detect_hotelling_t2
```

## 11. Verification Plan

Implemented tests:

- two-sample no-drift multivariate window
- two-sample drift candidate
- one-sample Phase II explicit control limit
- regularized high-dimensional / singular covariance scenario
- validation and warning behavior

Current test file:

```text
tests/test_hotelling_t2.py
```
