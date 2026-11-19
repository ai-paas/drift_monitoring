# Label and Error Schema

## Applies To

Supervised concept/performance drift detectors and operational adaptation
methods.

Examples: DDM, RDDM, EDDM, ECDD-WT, HDDM-A, HDDM-W, STEPD, HAT,
DriftRetrainingClassifier.

## DataFrame Columns

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

Optional:

```text
label_time: datetime64[ns]
class_label: scalar
sample_weight: numeric
```

## Parameters

- `label_col`: default `y_true`
- `prediction_col`: default `y_pred`
- `error_col`: optional
- `positive_error_value`: default `1`
- `label_delay_policy`: optional

## Validation

If labels are absent or delayed beyond the analysis window, supervised detectors
must return `severity="not_applicable"` rather than pretending to detect concept
drift from unlabeled data.

