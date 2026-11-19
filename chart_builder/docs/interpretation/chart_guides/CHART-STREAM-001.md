# CHART-STREAM-001 Guide

This chart explains an ADWIN stream drift alarm through stream mean increase and adaptive window shrinkage.

Read in this order:

1. Summary card: alarm index `23`, mean delta `+0.30`, and p-value `0.009`.
2. Main stream: raw metric and rolling mean rise after the alarm marker.
3. Window-width trend: adaptive window shrinks after the alarm.
4. Mean bars: before and after means differ by more than the operational delta threshold `0.20`.
5. Notes/legend: use as context only.

The chart-level interpretation should connect t=23 alarm, before/after mean increase, p-value, and window reduction.

Do not treat ADWIN as causal diagnosis. Mention window configuration, recent sample size, seasonality, and metric definition as checks.
