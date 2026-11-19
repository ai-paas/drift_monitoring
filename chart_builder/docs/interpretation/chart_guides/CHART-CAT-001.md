# CHART-CAT-001 Guide

This chart explains categorical drift with a chi-square style expected-vs-observed comparison.

Read in this order:

1. Summary card: chi-square statistic, degrees of freedom/p-value, and low expected-frequency count.
2. Observed vs expected grouped bars: categories with observed counts above expected and below expected.
3. Standardized residual matrix: strongest positive and negative residuals.
4. Contribution ranking: categories contributing most to the chi-square statistic.
5. Notes/legend: use as context only.

The chart-level interpretation should connect C/D grade increases, A/other/unknown decreases, residual direction, and contribution size. Mention low expected-frequency count because it affects whether the chi-square approximation is reliable.

Do not claim a business cause from category count shifts alone. Treat this as categorical distribution drift evidence requiring segment, label, and data collection checks.
