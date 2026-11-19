# Chart Components

이 폴더는 53개 drift chart를 공통 구성요소 단위로 조립하기 위한 component 설명 문서다.

원천 매핑 파일:

```text
../chart_component_to_chart.csv
../chart_component_raw_to_chart.csv
```

각 문서는 component의 목적, 기능, 주요 파라미터, 파라미터 변경 시 화면 변화, 적용 chart를 설명한다.

## Implementation Documents

- [../../../chart_runtime/RENDERING_ENGINE_NOTES.md](../../../chart_runtime/RENDERING_ENGINE_NOTES.md): rendering engine 변경 기록, overflow/scroll 정책, visual smoke test 기준
- [../../../chart_runtime/RENDERING_ENGINE_CONFIG_DATA_GUIDE.md](../../../chart_runtime/RENDERING_ENGINE_CONFIG_DATA_GUIDE.md): runtime renderer, config, data binding 연결 구조
- [IMPLEMENTATION_GUIDE.md](./IMPLEMENTATION_GUIDE.md): semantic container와 responsive component 구현 기준
- [CHART_BUILDER_UI_DESIGN.md](./CHART_BUILDER_UI_DESIGN.md): component palette, 배치 container, properties panel 기반 Chart Builder UI 설계

## Component Index

| component | 적용 chart 수 | 문서 |
|---|---:|---|
| `adaptive_model_structure_view` | 2 | [adaptive-model-structure-view.md](./adaptive-model-structure-view.md) |
| `annotation_callout` | 4 | [annotation-callout.md](./annotation-callout.md) |
| `bar_chart` | 12 | [bar-chart.md](./bar-chart.md) |
| `comparison_table` | 2 | [comparison-table.md](./comparison-table.md) |
| `contribution_view` | 3 | [contribution-view.md](./contribution-view.md) |
| `control_chart` | 2 | [control-chart.md](./control-chart.md) |
| `cumulative_curve` | 5 | [cumulative-curve.md](./cumulative-curve.md) |
| `decision_card` | 2 | [decision-card.md](./decision-card.md) |
| `detector_statistic_view` | 29 | [detector-statistic-view.md](./detector-statistic-view.md) |
| `distance_metric_view` | 11 | [distance-metric-view.md](./distance-metric-view.md) |
| `distribution_summary_plot` | 4 | [distribution-summary-plot.md](./distribution-summary-plot.md) |
| `distribution_view` | 13 | [distribution-view.md](./distribution-view.md) |
| `domain_specific_visual` | 33 | [domain-specific-visual.md](./domain-specific-visual.md) |
| `drift_metric_timeseries` | new | [../../drift_metric_timeseries/docs/README.md](../../drift_metric_timeseries/docs/README.md) |
| `event_marker` | 34 | [event-marker.md](./event-marker.md) |
| `heatmap` | 5 | [heatmap.md](./heatmap.md) |
| `histogram_view` | 9 | [histogram-view.md](./histogram-view.md) |
| `matrix_view` | 1 | [matrix-view.md](./matrix-view.md) |
| `model_diagnostic_curve` | 6 | [model-diagnostic-curve.md](./model-diagnostic-curve.md) |
| `p_value_view` | 11 | [p-value-view.md](./p-value-view.md) |
| `performance_metric_view` | 14 | [performance-metric-view.md](./performance-metric-view.md) |
| `projection_scatter` | 12 | [projection-scatter.md](./projection-scatter.md) |
| `proportion_view` | 12 | [proportion-view.md](./proportion-view.md) |
| `quantile_view` | 2 | [quantile-view.md](./quantile-view.md) |
| `ranking_view` | 2 | [ranking-view.md](./ranking-view.md) |
| `raw_signal_trend` | 7 | [raw-signal-trend.md](./raw-signal-trend.md) |
| `reference_current_comparison` | 14 | [reference-current-comparison.md](./reference-current-comparison.md) |
| `small_multiples` | 1 | [small-multiples.md](./small-multiples.md) |
| `state_timeline` | 14 | [state-timeline.md](./state-timeline.md) |
| `threshold_line` | 31 | [threshold-line.md](./threshold-line.md) |
| `trend_line` | 30 | [trend-line.md](./trend-line.md) |
| `uncertainty_band` | 10 | [uncertainty-band.md](./uncertainty-band.md) |
| `window_view` | 13 | [window-view.md](./window-view.md) |

## Additional Guide

- [SOURCE_MATCHING_GUIDE.md](./SOURCE_MATCHING_GUIDE.md): 원본 chart와 generated component chart를 비교하며 config-driven 방식으로 맞추는 절차
