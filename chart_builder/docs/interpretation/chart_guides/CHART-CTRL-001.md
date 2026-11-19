# CHART-CTRL-001 Guide

This chart explains an upward CUSUM mean-shift alarm using raw metric trend, positive/negative CUSUM, and direction ranking.

Read in this order:

1. Summary card: C+ max, C- max, and shift amount.
2. Raw signal trend: metric level relative to the target mean and alarm marker.
3. CUSUM control chart: C+ and C- trajectories, control limit, and first/continued exceedance.
4. Direction ranking: whether upward C+ or downward C- dominates.
5. Notes/legend: use as context only.

The chart-level interpretation should connect raw metric staying above target, C+ crossing the control limit `25`, C+ max `52.9`, weak C- max `0.1`, and the upward-shift conclusion.

Do not claim the operational root cause from CUSUM alone. Check target mean, CUSUM parameters, seasonality, and segment composition before assigning cause.
