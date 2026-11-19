# CHART-REP-001 Guide

This chart explains representation drift in a model layer using activation-change matrix, activation distribution, and projection evidence.

Read in this order:

1. Summary card: affected layer/block, activation shift, and status.
2. Matrix view: layer-by-feature or layer-by-direction cells with strongest activation changes.
3. Activation bars: baseline/current activation distribution and bins with increased or decreased mass.
4. Projection scatter: baseline/current cluster separation or overlap.
5. Notes/legend: use as supporting context only.

The chart-level interpretation should connect the active matrix cells with activation distribution change and projection separation. Do not claim model failure or feature semantics unless the payload explicitly identifies them.

