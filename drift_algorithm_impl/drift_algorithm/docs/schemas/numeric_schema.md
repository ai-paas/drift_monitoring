# Numeric Schema

## Applies To

Numeric distribution tests, numeric distance methods, and many streaming
detectors.

Examples: KS, Wasserstein, Anderson-Darling, Cramer-von Mises, Mann-Whitney,
t-test, F-test, Levene, ADWIN, KSWIN, Page-Hinkley, CUSUM, EWMA, BOCD, SeqDrift.

## DataFrame Columns

```text
time: datetime64[ns]
value: numeric
```

Optional:

```text
sample_weight: numeric
segment: string
```

## Parameters

- `value_col`: default `value`
- `alpha`: default `0.05` for p-value tests
- `threshold`: optional detector threshold
- `min_reference_size`: default method-specific
- `min_current_size`: default method-specific

## Validation

The implementation must drop missing or non-finite values and record effective
sample sizes. If either window becomes empty, return `severity="not_applicable"`.

