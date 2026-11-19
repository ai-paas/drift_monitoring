# CHART-CTRL-002 Guide

This chart explains a gradual upward mean shift through raw values, EWMA smoothing, control limits, and a state timeline.

Read in this order:

1. Summary card: EWMA max, alarm time, and estimated shift.
2. Raw/EWMA trend: raw metric movement and smoothed EWMA movement over time.
3. Control chart: EWMA relative to center line, UCL, and LCL.
4. State timeline: normal, warning, and alarm intervals.
5. Notes/legend: use as context only.

The chart-level interpretation should connect the raw metric increase, EWMA smoothing lag, crossing of the upper control limit, and transition from normal to warning to alarm.

Do not claim a root cause from EWMA alone. Mention that smoothing parameter, baseline center line, control limits, seasonality, and segment composition should be checked.
