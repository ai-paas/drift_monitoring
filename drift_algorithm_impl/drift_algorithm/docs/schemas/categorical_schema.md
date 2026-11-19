# Categorical Schema

## Applies To

Categorical frequency tests and probability-distance methods.

Examples: Chi-square, Fisher's Exact, G-test, categorical PSI, KL, JS,
Hellinger, Total Variation, L-Infinity.

## DataFrame Columns

```text
time: datetime64[ns]
category: string
count: integer, optional
```

If `count` is absent, each row is treated as one observation.

## Parameters

- `category_col`: default `category`
- `count_col`: optional
- `smoothing_epsilon`: optional for zero-probability bins
- `rare_category_policy`: optional category merge policy
- `min_expected_count`: optional warning threshold

## Validation

Reference and current category sets must be aligned before computing tests or
distances. Missing categories are filled with zero count before smoothing.

