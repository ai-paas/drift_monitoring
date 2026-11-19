# CHART-STREAM-005 Guide

This chart explains an SPRT decision for increasing error rate.

Read in this order:

1. Summary card: final LLR `16.0`, alpha/beta `0.05 / 0.10`, and alarm index `25`.
2. LLR trend: log likelihood ratio crosses the H1 acceptance boundary.
3. Error-rate trend: error rate rises toward and above `0.30`.
4. State timeline: continue changes to review and then H1 decision at the alarm.
5. Notes/legend: use as context only.

The chart-level interpretation should connect rising error rate, H1 boundary crossing at t=25, and final LLR `16.0`.

Do not treat SPRT as causal proof. Mention error labeling quality, H0/H1 parameter choice, and sequential testing assumptions as checks.
