# CHART-VAR-001 Guide

This chart explains variance drift where the center is stable but current spread is larger.

Read in this order:

1. Summary card: variance ratio `2.66`, p-value `0.012`, and absolute deviation change `+3.6`.
2. Violin summary: current range, quartiles, and SD are wider while center remains near baseline.
3. Variance bars: variance increases from `42.3` to `112.4`.
4. Deviation bars: current absolute deviation rises from `5.1` to `8.7`.
5. Notes/legend: use as context only.

The chart-level interpretation should connect stable center, wider current distribution, variance ratio `2.66`, Levene p-value `0.012`, and absolute deviation increase.

Do not confuse variance drift with mean shift or outlier-only drift. Mention tail/outlier and mean-shift checks.
