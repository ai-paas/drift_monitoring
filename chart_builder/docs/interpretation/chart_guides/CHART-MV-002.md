# CHART-MV-002 Guide

This chart explains multivariate embedding drift with kernel MMD, a baseline/current projection, and a null distribution.

Read in this order:

1. Summary card: MMD value, p-value, and decision or status.
2. Projection scatter: baseline/current point clouds, overlap, separation, and concentration.
3. MMD trend: window-level MMD movement and threshold or recent peak if present.
4. Null histogram: observed statistic position relative to the null distribution.
5. Notes/legend: use as supporting context only.

The chart-level interpretation should connect projection separation with MMD magnitude and null-distribution evidence. A drift/candidate judgment needs the explicit p-value, threshold, or decision card evidence; projection separation alone is not enough.

