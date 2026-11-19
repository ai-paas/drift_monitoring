# CHART-MV-005 Guide

This chart explains covariance or distance-based multivariate drift through PCA projection, distance trend, and distance histogram.

Read in this order:

1. Summary card: distance/statistic, limit or p-value, and status.
2. PCA projection: current samples that move away from the reference cloud, including any radius or outlier encoding.
3. Distance trend: window-level distance movement and threshold crossing if present.
4. Histogram: how many samples fall into higher-distance bins.
5. Notes/legend: use as supporting context only.

The chart-level interpretation should connect high-distance current concentration with the distance trend and histogram. Treat covariance or spread change as evidence to investigate unless the payload contains an explicit decision threshold or p-value.

