# Component Guide: Line-Like Metric Components

Applies to `trend_line`, `raw_signal_trend`, `performance_metric_view`, `distance_metric_view`, `detector_statistic_view`, `control_chart`, `cumulative_curve`, `model_diagnostic_curve`, and `adaptive_model_structure_view`.

Explain these elements when present:

- x-axis field and y-axis field.
- main line meaning.
- sampled points or highlighted points.
- secondary line meaning.
- horizontal marker meaning. Call it a threshold only when config, label, or rule says threshold, limit, target, baseline, UCL, LCL, or bound.
- vertical marker or event overlay meaning.
- first/latest/min/max values, crossing point, event point, and post-event direction.

Do not infer drift from a high value alone. Explain metric direction and decision rule first.
