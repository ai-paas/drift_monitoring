# Drift Algorithm Implementation Guide

## 1. Implementation Principles

1. Use `pandas.DataFrame` as the public input boundary.
2. Convert validated numeric data to `numpy.ndarray` inside each detector.
3. Keep method output aligned with `drift_measurements_catalog.csv`.
4. Treat detector alarms as investigation signals, not root-cause conclusions.
5. Return warnings instead of raising for statistical limitations such as small
   sample size, ties, missing labels, or singular covariance.
6. Raise exceptions only for programmer errors such as an unknown method id or
   malformed configuration.

## 2. Package Layout

```text
drift_algorithm/
  __init__.py
  core/
    result.py
    schema.py
    windows.py
    registry.py
  methods/
    batch_distribution.py
    categorical_distribution.py
    streaming.py
    supervised.py
    multivariate.py
    representation.py
    text.py
    explanation.py
    operational.py
  docs/
    input_output_contracts.md
    implementation_guide.md
    method_designs/
```

## 3. Design Before Code

Every implemented method must have a matching Markdown design file under:

```text
drift_algorithm/docs/method_designs/DM-XXX_<method_slug>.md
```

The design file must define:

- input schema
- parameter schema
- output measurements
- algorithm steps
- drift decision rule
- warnings and not-applicable conditions
- implementation module/function target

## 4. Dependency Policy

Initial implementation should rely on widely available Python scientific
libraries when present:

- `numpy`
- `pandas`
- `scipy`
- `scikit-learn`

If an optional dependency is missing, the method should either use a local
fallback or return a clear not-applicable/error result depending on whether the
dependency is required.

## 5. Manager Review Checklist

For each method implementation:

1. The method design exists and names the source documents.
2. Input validation follows the documented schema.
3. Returned measurement keys match canonical measurement names.
4. `drift_detected` is derived from a documented threshold or p-value rule.
5. Warnings cover sample size, missing values, label availability, or numerical
   instability where relevant.
6. Tests include at least one no-drift and one drift-candidate example when
   feasible.

