# CHART-CLS-001 Guide

This chart explains classifier-based drift using a domain classifier ROC curve, domain-score distribution, and feature/projection evidence.

Read in this order:

1. Summary card: ROC-AUC, score gap, and top feature.
2. ROC curve: separation from random diagonal and AUC annotation.
3. Domain score distributions: baseline/current separation around the 0.5 reference.
4. Feature importance and projection: top embedding feature and baseline/current point separation.
5. Notes/legend: use as context only.

The chart-level interpretation should connect high ROC-AUC, separated domain probability scores, and top feature/projection evidence. Explain that classifier separability is drift evidence but does not by itself identify the operational root cause.

Do not infer semantic meaning from embedding feature names alone. Treat `emb_17` as an explanation candidate requiring feature-level or segment-level follow-up.
