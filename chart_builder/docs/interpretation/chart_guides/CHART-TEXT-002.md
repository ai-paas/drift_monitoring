# CHART-TEXT-002 Guide

This chart explains text domain-classifier drift through ROC separability, score distribution separation, and descriptor projection.

Read in this order:

1. Summary card: ROC AUC `0.89`, KS score `0.47`, and descriptor drift `refund-policy`.
2. ROC curve: classifier curve sits above the random diagonal.
3. Score distribution: baseline and current classifier-score densities separate.
4. Descriptor projection: important descriptors and projection groups show current/baseline separation.
5. Notes/legend: use as context only.

The chart-level interpretation should connect ROC AUC `0.89`, KS score `0.47`, score distribution separation, and refund-policy descriptor drift.

Do not equate classifier separability with production impact. Mention label leakage, descriptor stability, and class balance checks.
