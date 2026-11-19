# CHART-ERR-004 Guide

This chart explains an ECDD weighted error-rate drift alarm using a statistic control chart, weighted error-rate trend, and state timeline.

Read in this order:

1. Summary card: final statistic, warning time, and drift time.
2. ECDD control chart: statistic rising to `1.28`, crossing warning limit `0.72` at `t=22` and drift limit `0.95` at `t=26`.
3. Error-rate trend: weighted error rate rising from about `0.07` to `0.45`.
4. State timeline: normal, warning, then drift after `t=26`.
5. Notes/legend: use as context only.

The chart-level interpretation should connect statistic exceedance with the weighted error-rate increase.

Do not treat ECDD as an unsupervised distribution test; it is evidence from the error stream.
