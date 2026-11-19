# DM-050 Model Uncertainty Drift Design

## 1. Method Identity

- Method ID: `DM-050`
- Method name: `Model Uncertainty Drift`
- Category: `RepresentationDriftMethod`
- Method kind: `detector`
- Status: `구현 완료`
- Source catalog: `drift_methods_catalog.md`
- Source variant document: `algorithm_variants/model_uncertainty_drift_algorithm_variants.md`

## 2. Purpose

This method answers the drift question represented by `Model Uncertainty Drift` in the
catalog. Primary input from the catalog: confidence, entropy, uncertainty score.
Primary output from the catalog: uncertainty distribution drift.

## 3. Supported Variants

- `SOFTMAX_CONFIDENCE_DRIFT`
- `ENTROPY_DRIFT`
- `PREDICTIVE_VARIANCE_DRIFT`

## 4. Input Schema

Use the common `pandas.DataFrame` input boundary from
`../input_output_contracts.md`.

Supported schemas:

```text
Common: `time`
SOFTMAX_CONFIDENCE_DRIFT: `confidence_col`, `probability_cols`, or `value_col`
ENTROPY_DRIFT: `probability_cols`
PREDICTIVE_VARIANCE_DRIFT: `variance_col`, `prediction_cols`, or `value_col`
```

The implementation must validate the concrete columns through `params` and
return `severity="not_applicable"` if the supplied schema cannot represent this
method's required input.

## 5. Parameters

Method-specific parameters come from `drift_method_parameter_guide.md` and the
variant source document. The implementation should at minimum support:

- `variant_id`: one of the supported variant IDs.
- `alpha`: p-value decision threshold, default `0.05`.
- `reference_start`, `reference_end`, `current_start`, `current_end`, or
  `split_time`: common reference/current window selectors.
- `confidence_col`, `probability_cols`, `variance_col`, `prediction_cols`, or
  `value_col`: variant-specific uncertainty inputs.
- `confidence_threshold`: low-confidence rate cutoff for confidence variants,
  default `0.8`.
- `entropy_base`: optional logarithm base for entropy values.
- `min_reference_size` and `min_current_size`: default `20`.

## 6. Output Measurements

Return canonical measurements where applicable:

- `DRIFT_ALARM_STATE`
- `P_VALUE`
- `TEST_STATISTIC`
- `THRESHOLD`
- `METHOD_POLICY`
- `UNCERTAINTY_MEAN_REFERENCE`
- `UNCERTAINTY_MEAN_CURRENT`
- `UNCERTAINTY_MEAN_DELTA`
- `LOW_CONFIDENCE_RATE_REFERENCE`
- `LOW_CONFIDENCE_RATE_CURRENT`
- `REFERENCE_SAMPLE_SIZE`
- `CURRENT_SAMPLE_SIZE`
- `FEATURE_COLUMNS`

Always include `SAMPLE_SIZE` or relevant effective count metadata when the
method compares reference/current windows.

## 7. Algorithm Steps

1. Validate required DataFrame columns and parameter names.
2. Convert `time` to datetime and sort by time.
3. Split reference/current windows or iterate the stream according to the method
   category.
4. Convert the selected confidence, probability, variance, or prediction columns
   to numeric arrays.
5. Derive the variant-specific uncertainty series:
   - confidence drift: `1 - confidence`
   - entropy drift: row-wise predictive entropy
   - predictive variance drift: supplied variance or row-wise prediction
     variance
6. Run a two-sample Kolmogorov-Smirnov test over reference/current uncertainty
   scores.
7. Apply `p_value < alpha`.
7. Return `DriftResult` with canonical measurement keys and interpretation text.

## 8. Drift Decision Rule

The first implementation should use the variant document's default rule when it
is explicit. If no default is explicit, use:

```text
drift_detected = p_value < alpha
```

The implementation records this as `METHOD_POLICY="ks_pvalue"` and
`THRESHOLD=alpha`.

## 9. Warnings and Not-Applicable Conditions

Return warnings for:

- missing required columns
- empty reference/current windows
- sample size below method minimum
- unsupported variant id
- non-numeric or invalid confidence/probability/variance values
- invalid probability rows for entropy
- invalid `confidence_threshold` or `alpha`

## 10. Implementation Target

```text
module: drift_algorithm.methods.representationdriftmethod
function: detect_model_uncertainty_drift
```

## 11. Verification Plan

Create at least two tests when implementation starts:

1. no-drift synthetic data with similar reference/current windows
2. drift-candidate synthetic data that changes the statistic or alarm in the
   expected direction

The test must assert canonical measurement keys, warning behavior, and the
documented `drift_detected` rule.

## 12. Implementation Notes

Implemented in `drift_algorithm.methods.representationdriftmethod` as
`detect_model_uncertainty_drift`.

Implemented behavior:

- `SOFTMAX_CONFIDENCE_DRIFT` accepts a confidence column, probability columns, or
  value column and compares uncertainty scores `1 - confidence`.
- `ENTROPY_DRIFT` accepts probability columns and compares row-wise predictive
  entropy.
- `PREDICTIVE_VARIANCE_DRIFT` accepts a variance column, prediction columns, or
  value column and compares predictive variance scores.
- all variants use a two-sample KS p-value decision rule.
- unsupported variants, missing columns, invalid windows, invalid numeric input,
  and insufficient samples return `not_applicable`.

Verification:

```text
py_compile: passed
DM-050 pytest: 5 passed
representation regression pytest: 30 passed
```
