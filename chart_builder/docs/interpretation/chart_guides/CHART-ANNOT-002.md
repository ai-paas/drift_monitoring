# CHART-ANNOT-002 Guide

This chart explains approximation, projection, and quantile error annotations for approximate drift scoring.

Read in this order. Always lead with approximation reliability and error stability before emphasizing whether the drift score crosses the threshold:

1. Summary card: approximation error, projection count, and max quantile error.
2. Error band line chart: exact/reference score, approximate score, approximation error band, and drift threshold.
3. Projection stability bars: projection count, score spread, and tolerance line.
4. Quantile error bars: q25/q50/q75/tail error and target line. Explicitly state whether each important error is below or above the target.

The key judgment is not only whether the drift score crosses a threshold. Check whether approximation error could change the conclusion near the threshold, whether projection count is stable enough, and whether tail quantile error exceeds the target.

Do not treat approximate score as equally reliable as exact/reference score when error bands, projection spread, or tail error indicate uncertainty.
