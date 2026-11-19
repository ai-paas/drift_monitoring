# CHART-CAT-004 Guide

This chart explains a small-sample binary category/event shift using Fisher's exact test, event rates, and an odds ratio interval.

Read in this order:

1. Summary card: Fisher p-value, odds ratio, and event-rate change.
2. 2x2 mosaic: reference/current event and non-event counts.
3. Event-rate bars: reference rate versus current rate.
4. Forest plot: odds ratio, confidence interval, and null OR=1.
5. Notes/legend: use as context only.

The chart-level interpretation should connect reference `6/42` versus current `14/38`, event-rate increase, Fisher p-value, odds ratio `3.50`, and confidence interval `[1.18, 10.4]` excluding null.

Do not infer event cause from Fisher test output alone. Treat it as a small-sample event-rate drift candidate and check collection, segment, exposure, and label definitions.
