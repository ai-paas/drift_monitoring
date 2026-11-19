# CHART-EXPL-001 Guide

This chart explains explanation-level drift using SHAP importance shifts, SHAP value distribution movement, and class-level heatmap evidence.

Read in this order:

1. Summary card: top shifted feature, rank change, and class heat.
2. Feature bars: `risk_score` increases from `0.27` to `0.36`, while `amount` decreases from `0.31` to `0.18`.
3. SHAP distribution: `risk_score` peak moves from negative baseline values toward positive current values.
4. Heatmap: class C has the strongest `risk_score` heat at `0.48`.
5. Notes/legend: use as context only.

The chart-level interpretation should distinguish explanation drift from direct performance failure.

Do not infer causal feature effects from SHAP changes alone.
