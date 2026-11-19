# Component Guide: Distribution And Histogram

Applies to `distribution_view`, `histogram_view`, `distribution_summary_plot`, and `quantile_view`.

Explain:

- what the x-axis value represents,
- what the y-axis height, density, count, or proportion represents,
- reference/current, baseline/current, null/observed, or group comparisons,
- distribution shift, overlap, tail mass, mode change, and threshold markers,
- concrete bin or quantile values when available.

If a vertical marker is present, call it a threshold only when the label or config defines it as threshold, target, or limit.

Do not infer root cause or model failure from distribution shift alone.
