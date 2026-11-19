# CHART-UNC-001 Guide

This chart explains uncertainty drift through lower confidence, rising entropy, and calibration degradation.

Read in this order:

1. Summary card: entropy `0.77`, ECE `0.12`, and class-C uncertainty.
2. Confidence distribution: current density shifts toward lower softmax confidence than baseline.
3. Entropy trend: entropy crosses threshold `0.55` around t=15 and rises.
4. Calibration curve: current calibration deviates from the perfect diagonal; class uncertainty bars provide context.
5. Notes/legend: use as context only.

The chart-level interpretation should connect confidence drop, entropy threshold crossing, and calibration degradation.

Do not claim model failure cause from uncertainty alone. Mention calibration set quality, label distribution, and class-specific sample size checks.
