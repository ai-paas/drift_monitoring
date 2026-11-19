# Drift Algorithm Input and Output Contracts

## 1. Purpose

This document defines the common Python-facing contract for all drift method
implementations. The public input type is `pandas.DataFrame`; method internals
may convert columns to `numpy.ndarray` for performance.

The default minute-level time series input is:

```python
pd.DataFrame({
    "time": pd.Series(..., dtype="datetime64[ns]"),
    "value": pd.Series(..., dtype="float64"),
})
```

All method implementations must accept explicit reference/current windows and
must return a common result object.

## 2. Common Function Shape

```python
def detect(
    data: pd.DataFrame,
    *,
    time_col: str = "time",
    value_col: str | None = "value",
    reference_window: tuple[str, str] | None = None,
    current_window: tuple[str, str] | None = None,
    params: dict | None = None,
) -> DriftResult:
    ...
```

`reference_window` and `current_window` are inclusive timestamp ranges. If a
streaming detector does not need an explicit reference window, it still accepts
the argument for API consistency and records how it was used in metadata.

## 3. Common Result Shape

```python
@dataclass
class DriftResult:
    method_id: str
    method_name: str
    method_category: str
    variant_id: str | None
    drift_detected: bool | None
    severity: str
    drift_score: float | None
    p_value: float | None
    test_statistic: float | None
    threshold: float | None
    measurements: dict[str, Any]
    interpretation: str
    warnings: list[str]
    metadata: dict[str, Any]
```

`severity` is one of:

```text
not_applicable
normal
watch
drift_candidate
drift_detected
error
```

`measurements` must use canonical measurement names from
`drift_measurements_catalog.csv` whenever possible, for example `P_VALUE`,
`KS_STATISTIC`, `WASSERSTEIN_DISTANCE`, `DRIFT_ALARM_STATE`, `WINDOW_SIZE`.

## 4. Window Handling

All batch methods use this flow:

1. Convert `time_col` to `datetime64[ns]`.
2. Sort by time.
3. Slice reference/current windows.
4. Drop rows that are invalid for the selected method.
5. Record original and effective sample sizes.

Streaming methods use this flow:

1. Convert `time_col` to `datetime64[ns]`.
2. Sort by time.
3. Iterate rows in time order.
4. Emit final state plus optional event history in `measurements`.

## 5. Data Schemas by Method Family

### Numeric Univariate

Required columns:

```text
time: datetime64[ns]
value: numeric
```

Used by KS, Wasserstein, t-test, F-test, Levene, AD/CvM/Kuiper/BWS,
Mann-Whitney, ADWIN, KSWIN, Page-Hinkley, CUSUM, EWMA, GMA, BOCD, SeqDrift,
SPRT numeric variants.

### Categorical or Count Distribution

Long format:

```text
time: datetime64[ns]
category: string
count: integer, optional
```

If `count` is absent, each row counts as one observation.

Used by Chi-square, Fisher, G-test, PSI categorical variants, KL/JS/Hellinger,
Total Variation, L-Infinity, Bhattacharyya, HINC.

### Probability Vector

Long format:

```text
time: datetime64[ns]
class: string
probability: float
```

Wide format is also allowed:

```text
time: datetime64[ns]
prob_<class_a>: float
prob_<class_b>: float
...
```

Rows are normalized per window before distance calculations unless
`params["already_normalized"]` is true.

### Multivariate Numeric

Required columns:

```text
time: datetime64[ns]
<feature_1>: numeric
<feature_2>: numeric
...
```

Feature columns are supplied through `params["feature_cols"]`.

Used by Energy Distance, MMD, LSDD, Hotelling T2, MEWMA, Mahalanobis Distance,
OCDD, Feature Map Drift, Autoencoder Representation Drift, Graph Embedding
Drift, Classifier-based embedding drift.

### Embedding

Preferred wide format:

```text
time: datetime64[ns]
emb_0: float
emb_1: float
...
```

Alternative object format:

```text
time: datetime64[ns]
embedding: list[float] | np.ndarray
```

The implementation normalizes both formats to a 2D `numpy.ndarray`.

### Label or Error Stream

Raw prediction format:

```text
time: datetime64[ns]
y_true: scalar
y_pred: scalar
```

Precomputed error format:

```text
time: datetime64[ns]
error: 0 | 1
```

Used by DDM, RDDM, EDDM, ECDD-WT, HDDM-A, HDDM-W, STEPD, HAT,
DriftRetrainingClassifier.

### Text

Raw text format:

```text
time: datetime64[ns]
text: string
```

Text with embedding:

```text
time: datetime64[ns]
text: string, optional
emb_0..emb_n or embedding
```

Text-only methods may use TF-IDF or descriptor features. Semantic methods should
prefer precomputed embeddings in the first implementation phase.

### SHAP or Explanation Matrix

Wide format:

```text
time: datetime64[ns]
shap_<feature_1>: float
shap_<feature_2>: float
...
```

Long format:

```text
time: datetime64[ns]
feature: string
shap_value: float
```

The first implementation phase assumes SHAP values are already computed.

## 6. Not Applicable Results

If a method cannot run because the supplied schema does not match the method
family, it must return a `DriftResult` with:

```text
drift_detected = None
severity = "not_applicable"
warnings = ["..."]
```

It must not silently coerce text, category, label, or embedding data into an
unrelated numeric detector.

