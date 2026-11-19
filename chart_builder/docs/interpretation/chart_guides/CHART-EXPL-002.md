# CHART-EXPL-002 Guide

This chart explains tree-feature drift evidence from feature importance, time/domain split counts, path structure, and segment proportions.

Read in this order:

1. Summary card: top feature `query_age`, time split count `18`, and current leaf share.
2. Feature bars: `query_age` importance `0.34` and time splits `18` dominate.
3. Path diagram: `query_age > 14d` and downstream mobile branch identify the current-heavy path.
4. Segment bars: segment `S4` is current-dominant at `82%` versus baseline `18%`.
5. Notes/legend: use as context only.

The chart-level interpretation should connect high split frequency with the current-dominant segment.

Do not treat the tree path as a causal rule without domain validation.
