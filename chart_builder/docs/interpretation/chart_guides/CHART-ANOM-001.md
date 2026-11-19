# CHART-ANOM-001 Guide

This chart explains novelty/anomaly drift: current samples move outside the baseline normal support.

Read in this order:

1. Summary card: outlier rate, anomaly score threshold, and alarm time.
2. Anomaly score distribution: baseline score distribution, current score distribution, threshold, and current tail mass beyond threshold.
3. Anomaly rate trend: rate over time, rate threshold, alarm crossing, and post-alarm persistence.
4. Projection scatter: baseline normal cluster, current normal cluster, and current outlier concentration.

The chart-level interpretation should connect score-distribution shift, rising outlier rate, threshold crossing, and outlier concentration in projection space.

Do not identify the root cause from outlier increase alone. Mention preprocessing, scaling, source/device/segment changes, new class inflow, and detector threshold settings as follow-up checks.
