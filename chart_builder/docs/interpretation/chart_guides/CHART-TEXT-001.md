# CHART-TEXT-001 Guide

This chart explains semantic text drift through embedding movement, centroid distance, topic mix, and a small domain-classifier ROC.

Read in this order:

1. Summary card: cosine distance `0.58`, topic shift `+28pt`, and domain AUC `0.82`.
2. Projection scatter: baseline and current query embeddings separate and centroid movement is visible.
3. Distance trend: centroid cosine distance rises and exceeds threshold `0.36` after t=22.
4. Topic mix and ROC: topic 3 grows from `20%` to `48%`; domain classifier AUC is `0.82`.
5. Notes/legend: use as context only.

The chart-level interpretation should connect embedding separation, distance threshold exceedance, topic mix shift, and domain-classifier separability.

Do not claim the semantic cause from embeddings alone. Mention vocabulary sampling, topic-label stability, and domain classifier leakage checks.
