# Drift Algorithm Implementation Workflow

## 1. Purpose

This document defines how drift method implementation work must proceed.

The rule is:

```text
document -> design detail -> implementation -> test -> manager review -> next method
```

No method should be implemented before its method design document is detailed
enough to define input schema, parameters, output measurements, drift decision
rule, and verification cases.

## 2. Roles

### Worker

The worker produces a bounded task result.

Worker responsibilities:

- update only the assigned method design or implementation files
- follow the common contracts in `input_output_contracts.md`
- preserve canonical method and measurement names
- add or update tests when code changes
- report changed files and unresolved questions

The worker must not:

- change unrelated method designs
- reinterpret method count
- add fallback methods as catalog methods
- change public input/output contracts without manager review

### Manager

The manager reviews and integrates the worker result.

Manager responsibilities:

- check the result against source documents
- check that canonical measurements match the CSV catalog
- check schema and result consistency
- run feasible syntax/tests
- review diff before continuing
- decide whether the method is ready for the next implementation batch

## 3. Source Order

Use source documents in this order:

1. `drift_methods_catalog.md`
2. `drift_method_variant_links.csv`
3. `drift_method_variant_measurement_summary.csv`
4. `drift_method_variant_measurement_links.csv`
5. `drift_method_variant_parameters.csv`
6. `drift_method_parameter_guide.md`
7. `algorithm_variants/*_algorithm_variants.md`
8. `drift_measurements_interpretation_guide.md`
9. `drift_measurement_method_selection_guide.md`

If sources disagree, stop and record the mismatch in the progress log before
implementing.

## 4. Work Unit Definition

A normal work unit is one method or a small group of closely related methods.

Recommended first batches:

1. `DM-001 KS Test`
2. `DM-002 Wasserstein Distance`
3. `DM-018 Mann-Whitney U / Wilcoxon Rank Sum Test`
4. `DM-019 t-test 계열`
5. `DM-021 Levene's Test`

Streaming detectors and supervised detectors should start only after the common
result, window, and schema helpers are stable.

## 5. Per-Method Workflow

### Step 1. Detail Method Design

Update:

```text
drift_algorithm/docs/method_designs/DM-XXX_<method>.md
```

The design must include:

- exact DataFrame schema
- supported variants for first implementation
- parameters and defaults
- canonical output measurements
- algorithm steps
- `drift_detected` rule
- warning and not-applicable conditions
- test cases
- implementation target

### Step 2. Manager Design Review

Manager checks:

- method id/name/category match `drift_methods_catalog.md`
- variants match `drift_method_variant_links.csv`
- output measurements match measurement CSVs
- schema family is correct
- drift decision rule is explicit
- tests cover no-drift and drift-candidate cases

### Step 3. Implement Core or Method Code

Implementation should update only assigned files under:

```text
drift_algorithm/core/
drift_algorithm/methods/
tests/
```

All public method functions use `pandas.DataFrame` and return `DriftResult`.

### Step 4. Run Checks

Minimum checks:

```powershell
python -m py_compile <changed python files>
python -m pytest <relevant tests>
```

If pytest is not available or no tests exist yet, record that explicitly in
`progress_log.md`.

### Step 5. Manager Implementation Review

Manager checks:

- code follows method design
- result keys are canonical
- warning paths are tested or manually checked
- no unrelated files were changed
- implementation gaps are recorded

### Step 6. Progress Log Update

Every completed work unit updates:

```text
drift_algorithm/docs/progress_log.md
```

The log entry must include:

- date
- method ids
- files changed
- checks run
- manager decision
- next method candidate

## 6. Done Criteria

A method is implementation-ready when:

- method design is detailed and manager-reviewed
- required dependencies are known
- output measurements are mapped
- no-drift and drift-candidate test cases are defined

A method is implemented when:

- code exists
- tests or feasible checks pass
- manager review accepts the result
- limitations are documented

## 7. Current Next Step

Start with:

```text
DM-001 KS Test
```

Reason:

- numeric `(time, value)` input matches the user's base data assumption
- output measurements are clear: `KS_STATISTIC`, `P_VALUE`
- SciPy implementation path is direct
- it establishes the first full document-code-test loop

