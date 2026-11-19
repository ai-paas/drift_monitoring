# CHART-BOCD-001 Guide

This chart explains Bayesian online change point detection with posterior probability, run length reset, and the observed stream.

Read in this order:

1. Summary card: peak change point probability, primary change time, and run length reset.
2. Change point posterior heatmap: strongest posterior spike, secondary peak, and marker alignment.
3. Run length posterior heatmap: whether posterior mass resets around the primary change time.
4. Stream trend: level before and after the marked changes, including segment mean markers.
5. Notes/legend: use as context only.

The chart-level interpretation should connect posterior concentration near `t=18`, run length reset, and stream level shift. Mention the secondary peak around `t=27` only as weaker follow-up evidence unless its posterior is comparable to the primary spike.

Do not infer the business/root cause from BOCD output alone. Treat this as a drift/change-point candidate that requires segment, feature, and label checks.
