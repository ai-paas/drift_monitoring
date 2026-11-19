# DM-055 HAT Design

## 1. Method Identity

- Method ID: `DM-055`
- Method name: `HAT`
- Category: `OperationalAdaptationMethod`
- Method kind: `operational`
- Status: `구현 완료`
- Source catalog: `drift_methods_catalog.md`
- Source variant document: `algorithm_variants/hat_algorithm_variants.md`

## 2. Purpose

This method answers the drift question represented by `HAT` in the
catalog. Primary input from the catalog: labeled stream.
Primary output from the catalog: drift state, alternate tree replacement, online accuracy.

## 3. Supported Variants

- `HAT_ADWIN_NODE_MONITORING`
- `HAT_ALTERNATE_TREE_REPLACEMENT`

## 4. Input Schema

Use the common `pandas.DataFrame` input boundary from
`../input_output_contracts.md`.

Supported schema:

```text
Common: `time`
Error stream: `error_col` or `value_col`
Label stream: `y_true`/`y_pred`
Optional operational fields: `node_col`, `online_accuracy_col`,
`alternate_created_col`, `replacement_col`
```

The implementation must validate the concrete columns through `params` and
return `severity="not_applicable"` if the supplied schema cannot represent this
method's required input.

## 5. Parameters

Method-specific parameters come from `drift_method_parameter_guide.md` and the
variant source document. The implementation should at minimum support:

- `variant_id`: one of the supported variant IDs.
- `error_col` or `value_col`: 0/1 error stream.
- `y_true` and `y_pred`: optional labels used to derive the error stream.
- `node_col`: optional HAT node/leaf identifier.
- `online_accuracy_col`: optional online accuracy log column.
- `alternate_created_col`: optional alternate tree creation event flag.
- `replacement_col`: optional tree replacement event flag.
- `warning_delta` and `drift_delta`: current-vs-reference error-rate delta
  thresholds.
- `min_reference_size`, `min_current_size`, and `min_node_size`.

## 6. Output Measurements

Return canonical measurements where applicable:

- `ADAPTATION_EVENT`
- `DRIFT_ALARM_STATE`
- `ONLINE_OR_PRE_POST_PERFORMANCE`
- `NODE_DRIFT_STATE`
- `NODE_ALARM_COUNT`
- `HAT_STATISTIC`
- `TEST_STATISTIC`
- `WARNING_STATE`
- `REFERENCE_ERROR_RATE`
- `CURRENT_ERROR_RATE`
- `ERROR_RATE_DELTA`

Always include `SAMPLE_SIZE` or relevant effective count metadata when the
method compares reference/current windows.

## 7. Algorithm Steps

1. Validate required DataFrame columns and parameter names.
2. Convert `time` to datetime and sort by time.
3. Split reference/current windows.
4. Derive or validate the 0/1 error stream.
5. Replay current HAT monitoring logs:
   - node monitoring compares node/current error-rate deltas against reference.
   - alternate tree replacement counts alternate/replacement event flags and
     summarizes pre/post performance.
6. Apply `warning_delta` and `drift_delta` event rules.
7. Return `DriftResult` with canonical measurement keys and interpretation text.

## 8. Drift Decision Rule

Implemented rules:

- `HAT_ADWIN_NODE_MONITORING`: drift when current error-rate delta or any node
  error-rate delta is at least `drift_delta`; warning when delta is at least
  `warning_delta`.
- `HAT_ALTERNATE_TREE_REPLACEMENT`: drift when alternate/replacement events are
  observed or current error-rate delta exceeds `drift_delta`.

## 9. Warnings and Not-Applicable Conditions

Return warnings for:

- missing required columns
- empty reference/current windows
- sample size below method minimum
- unsupported variant id
- missing label or error stream inputs
- non-binary error stream values
- invalid thresholds or sample-size settings
- too few node rows for node-level state calculation

## 10. Implementation Target

```text
module: drift_algorithm.methods.operationaladaptationmethod
function: detect_hat
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
`detect_hat`.

Implemented behavior:

- `HAT_ADWIN_NODE_MONITORING` replays logged labels/errors and reports global and
  node-level drift states using error-rate delta thresholds.
- `HAT_ALTERNATE_TREE_REPLACEMENT` summarizes alternate tree creation and branch
  replacement event flags with online/pre-post performance metadata.
- this implementation does not train a Hoeffding Adaptive Tree; it consumes
  finite operational logs.
- unsupported variants, missing columns, invalid windows, non-binary errors,
  invalid thresholds, and insufficient samples return `not_applicable`.

Verification:

```text
py_compile: passed
DM-055 pytest: 5 passed
operational/domain regression pytest: 15 passed
implemented numeric, streaming, supervised, multivariate, representation, explanation, domain-classifier, and operational pytest: 236 passed
```
