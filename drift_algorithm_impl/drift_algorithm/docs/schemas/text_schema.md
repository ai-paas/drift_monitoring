# Text Schema

## Applies To

Text and LLM query drift methods.

Examples: LLM Query / Semantic Distance, Text Domain Classifier Drift.

## DataFrame Columns

Raw text:

```text
time: datetime64[ns]
text: string
```

Text with embeddings:

```text
time: datetime64[ns]
text: string, optional
emb_0..emb_n or embedding
```

## Parameters

- `text_col`: default `text`
- `embedding_cols` or `embedding_col`: optional
- `vectorizer`: optional for text-only classifier methods
- `descriptor_cols`: optional
- `topic_col`: optional

## Validation

Text-only implementations must guard against leakage through timestamp, IDs, or
preprocessing artifacts. Semantic methods should prefer precomputed embeddings
for the first implementation phase.

