# CHART-STREAM-002 Guide

This chart explains a KSWIN recent-window distribution shift.

Read in this order:

1. Summary card: KS statistic `0.55`, p-value `0.011`, and alarm index `28`.
2. Main stream: reference and current windows are highlighted in different time regions.
3. ECDF comparison: current and reference empirical CDF curves separate.
4. KS trend: statistic crosses threshold `0.36` and peaks near the alarm.
5. Notes/legend: use as context only.

The chart-level interpretation should connect the higher recent window values, ECDF gap, KS statistic `0.55`, p-value `0.011`, and threshold exceedance.

Do not claim why the distribution shifted from KSWIN alone. Mention window selection, autocorrelation, and repeated testing as checks.
