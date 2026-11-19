# Embedding Schema

## Applies To

Embedding and representation drift methods.

Examples: OCDD, Feature Map Drift, Autoencoder Representation Drift, Graph
Embedding Drift, Classifier-based embedding drift, semantic distance methods.

## DataFrame Columns

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

## Parameters

- `embedding_cols`: optional when using wide format
- `embedding_col`: optional when using object format
- `embedding_model`: metadata
- `embedding_version`: metadata
- `normalization_policy`: optional

## Validation

Embedding dimensionality must be consistent across rows. The implementation
must record embedding model/version metadata when available because model
changes can mimic semantic drift.

