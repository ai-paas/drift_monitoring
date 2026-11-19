# CHART-ERR-006 Guide

This chart explains a STEPD-style supervised performance drift using recent accuracy, overall accuracy, and their gap.

Read in this order:

1. Summary card: recent accuracy, overall accuracy, and gap.
2. Accuracy comparison: recent accuracy falls from about `0.91` to `0.64` while overall accuracy declines more slowly.
3. Gap chart: gap crosses warning threshold `0.12` at `t=15` and drift threshold `0.15` around `t=20`.
4. State timeline: normal, warning, then drift after `t=20`.
5. Notes/legend: use as context only.

The chart-level interpretation should connect recent accuracy underperforming the historical baseline with the gap threshold crossing.

Do not call this a covariate drift proof; it is supervised performance evidence.
