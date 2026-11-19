# CHART-ERR-003 Guide

This chart explains gradual performance degradation through a shrinking error-interval score, state transitions, and error event concentration.

Read in this order:

1. Summary card: final score, warning time, and drift time.
2. Score trend: score falling from `1.00` to `0.44`.
3. State timeline: normal until `t=11`, warning until `t=19`, then drift.
4. Error events: errors become dense after `t=20`, with continuous events at `t=27` through `t=32`.
5. Notes/legend: use as context only.

The chart-level interpretation should connect the falling score, warning threshold crossing at `t=11`, drift threshold crossing at `t=19`, and late error-event concentration.

Do not claim a root cause for the rising error rate from this chart alone.
