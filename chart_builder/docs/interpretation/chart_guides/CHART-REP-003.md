# CHART-REP-003 Guide

This chart explains graph representation drift through embedding separation, node-group drift scores, and graph-level distance.

Read in this order:

1. Summary card: graph distance `0.67`, node max `0.70`, and bridge score `0.66`.
2. Projection scatter: baseline, current, and bridge graph embeddings are separated.
3. Node heatmap: hub and bridge node groups have the strongest late drift scores.
4. Distance trend: graph-level distance rises and crosses threshold `0.40`.
5. Notes/legend: use as context only.

The chart-level interpretation should connect current graph embedding separation, hub/bridge concentration, and distance threshold exceedance.

Do not infer graph-domain root cause from embedding distance alone. Mention that graph size, sampling, node alignment, and embedding training stability should be checked.
