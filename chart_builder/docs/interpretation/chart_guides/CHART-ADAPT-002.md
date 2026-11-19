# CHART-ADAPT-002 Guide

This chart explains a drift retraining workflow: champion performance declines, an alarm triggers retraining, and a challenger model is compared before promotion.

Read in this order:

1. Summary card: pre AUC, post AUC, and retrain time.
2. Performance trend: champion line, challenger line, target line, alarm marker, retrain marker, and latest values.
3. Workflow timeline: normal -> warning -> alarm -> retrain/monitor sequence.
4. Champion/challenger comparison: AUC, F1, latency, and tradeoffs.

Connect performance decline, alarm timing, retraining, challenger recovery, and latency tradeoff.

Do not equate retraining with automatic promotion. Promotion requires delayed labels, holdout/backtest checks, segment performance, latency, and rollback criteria.
