# CHART-STREAM-003 Guide

This chart explains a Page-Hinkley stream mean increase alarm.

Read in this order:

1. Summary card: PH statistic `25.5`, threshold `18.0`, and alarm index `29`.
2. Main stream: raw metric and running mean increase after the early baseline period.
3. PH statistic: statistic crosses threshold `18.0` and continues rising.
4. State timeline: normal changes to warning and then drift at the alarm.
5. Notes/legend: use as context only.

The chart-level interpretation should connect metric increase, PH threshold crossing, final statistic `25.5`, and timeline state transition.

Do not infer cause from PH statistic alone. Mention sensitivity parameters, direction assumption, and baseline stability as checks.
