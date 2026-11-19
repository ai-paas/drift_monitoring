# CHART-STREAM-004 Guide

This chart explains a SeqDrift sequential stream alarm.

Read in this order:

1. Summary card: final evidence `26.5`, alarm index `27`, and reference mean `0.53`.
2. Main stream: values rise above reference mean `0.53`.
3. Evidence trend: sequential evidence exceeds the decision bound.
4. State timeline: monitor changes to warning and then drift around t=27.
5. Notes/legend: use as context only.

The chart-level interpretation should connect value increase above the reference mean, evidence-bound crossing, and the t=27 drift decision.

Do not infer root cause from SeqDrift alone. Mention reference mean, decision bound calibration, and stream dependence as checks.
