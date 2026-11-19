# CHART-ADAPT-001 Guide

This chart explains how a Hoeffding Adaptive Tree reacts to stream drift by detecting warning, growing an alternate tree, replacing structure, and recovering performance.

Read in this order:

1. Summary card: accuracy minimum, replacement time, and maximum alternate nodes.
2. Online accuracy trend: early stable accuracy, warning-period decline, minimum value, and post-replacement recovery.
3. Event markers: warning, alternate start, and replacement timing.
4. Detector state timeline: normal -> warning -> alternate -> replace sequence.
5. Tree-size trend: main tree size and alternate tree growth, maximum alternate nodes, and alternate reset after replacement.

Do not explain HAT adaptation from accuracy alone. Connect accuracy, event marker, state timeline, and tree-size evidence.

Do not infer root cause, long-term stability, or operational impact from this chart alone.
