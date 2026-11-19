# CHART-ERR-005 Guide

This chart explains an HDDM error-rate drift alarm using mean-difference growth, Hoeffding bounds, and error trend.

Read in this order:

1. Summary card: final mean difference, warning time, and drift time.
2. Hoeffding bound chart: mean difference rising to `0.50`, crossing warning bound `0.26` at `t=22` and drift bound `0.36` at `t=26`.
3. Error trend: error rate rising from about `0.08` to `0.47`.
4. State timeline: normal, warning, then drift after `t=26`.
5. Notes/legend: use as context only.

The chart-level interpretation should explain that the recent/reference error mean difference expands beyond the configured bounds.

Do not infer which feature or upstream process caused the error-rate shift.
