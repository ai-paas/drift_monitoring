# Method Design Template

## 1. Method Identity

- Method ID:
- Method name:
- Category:
- Status:
- Source catalog:
- Source variant document:

## 2. Purpose

Describe what drift question this method answers.

## 3. Supported Variants

List variant ids and any implementation differences.

## 4. Input Schema

Define required and optional DataFrame columns.

```python
pd.DataFrame columns:
- time: datetime64[ns]
- ...
```

## 5. Parameters

List parameters, defaults, and tuning effects.

## 6. Output Measurements

List canonical measurement names returned in `DriftResult.measurements`.

## 7. Algorithm Steps

1. Validate input schema.
2. Split or stream data.
3. Compute method-specific statistic.
4. Apply threshold or significance rule.
5. Build `DriftResult`.

## 8. Drift Decision Rule

Define the exact rule for `drift_detected`.

## 9. Warnings and Not-Applicable Conditions

List conditions that should produce warnings or `severity="not_applicable"`.

## 10. Implementation Target

```text
module:
function:
```

## 11. Verification Plan

Describe synthetic or fixture data needed to test no-drift and drift cases.

