# Payload Runtime Compatibility

This document defines the compatibility rules between Chart Runtime Payloads and the Chart Runtime Engine.

`RUNTIME_CONTRACT.md` defines the payload shape. This document explains how to keep that contract stable while payloads, chart definitions, data producers, and runtime renderers evolve.

## Compatibility Boundary

The runtime can render a chart only when these two sides agree:

```text
Chart Runtime Payload
  layout + components + config + dataBinding + data

Chart Runtime Engine
  layout parser + component renderer selection + data/config interpretation
```

If either side changes without the other side remaining compatible, the chart may render incorrectly or fail to render.

## Required Payload Shape

Every renderable payload must include:

```text
payload.chartId
payload.layout.areas[]
payload.components[]
payload.data
```

Every `layout.areas[]` item must include:

```text
area
role
x
y
w
h
```

Every `components[]` item must include:

```text
componentInstanceId
componentType
area
config
dataBinding
```

Every data-backed component must have:

```text
component.dataBinding.source
payload.data[component.dataBinding.source]
```

If `dataBinding.source` is missing or points to a missing `payload.data` key, the runtime receives an empty row array for that component.

## Renderer Selection Contract

`componentType` is the stable key used by `chart_runtime.js` to select a renderer. Payload producers must not rename a `componentType` unless the runtime supports the new name.

Current renderer mapping:

| componentType | renderer |
|---|---|
| `trend_line` | `renderLine` |
| `raw_signal_trend` | `renderLine` |
| `detector_statistic_view` | `renderLine` |
| `distance_metric_view` | `renderLine` |
| `performance_metric_view` | `renderLine` |
| `control_chart` | `renderLine` |
| `cumulative_curve` | `renderLine` |
| `model_diagnostic_curve` | `renderLine` |
| `adaptive_model_structure_view` | `renderLine` |
| `bar_chart` | `renderBar` |
| `ranking_view` | `renderBar` |
| `contribution_view` | `renderBar` |
| `proportion_view` | `renderBar` |
| `reference_current_comparison` | `renderBar` |
| `p_value_view` | `renderBar` |
| `heatmap` | `renderMatrix` |
| `matrix_view` | `renderMatrix` |
| `forest_plot` | `renderForest` |
| `projection_scatter` | `renderScatter` |
| `feature_projection_view` | `renderFeatureProjection` |
| `node_link_diagram` | `renderNodeLink` |
| `tree_path_diagram` | `renderNodeLink` |
| `small_multiple_lines` | `renderSmallMultipleLines` |
| `circular_histogram` | `renderCircularHistogram` |
| `circular_histogram_view` | `renderCircularHistogram` |
| `event_raster` | `renderEventRaster` |
| `raster_view` | `renderEventRaster` |
| `distribution_view` | `renderDistribution` |
| `histogram_view` | `renderDistribution` |
| `distribution_summary_plot` | `renderDistribution` |
| `quantile_view` | `renderDistribution` |
| `state_timeline` | `renderTimeline` |
| `window_view` | `renderTimeline` |
| `threshold_line` | `renderThreshold` |
| `event_marker` | `renderEvents` |
| `uncertainty_band` | `renderBand` |
| `comparison_table` | `renderTable` |
| other component types | `renderCard` fallback |

The fallback exists for resilience, not as a contract for new visual components. New visual `componentType` values should be explicitly mapped.

## Field Binding Contract

Renderers resolve field names from `config` first, then from conventional defaults. `dataBinding` must still be preserved because Builder, validation, and future data producers need it as schema metadata.

Common field defaults:

| renderer family | important field config | default |
|---|---|---|
| line-like | `time_field`, `x_field` | `time` |
| line-like | `value_field`, `y_field`, `statistic_field` | `value` |
| line-like | `secondary_value_field` | optional |
| bar-like | `category_field` | `category` or `label` depending on style |
| bar-like | `value_field` | `value` |
| matrix-like | `x_field`, `column_field` | `column` |
| matrix-like | `y_field`, `row_field` | `row` |
| matrix-like | `value_field`, `cell_value_field` | `value` |
| scatter | `x_field` | `x` |
| scatter | `y_field` | `y` |
| distribution | `value_field`, `count_field` | `value` |
| timeline | `start`, `end`, `state` row fields | data rows must provide timeline intervals |

Compatibility rule:

```text
If a runtime renderer reads config.x_field = "score",
then every row in payload.data[source] used by that component should provide score when that field is required.
```

## Data Contract

`payload.data` is a map of source key to row array.

```json
{
  "data": {
    "chart.CHART-001.main": [
      { "time": 1, "value": 0.42 }
    ]
  }
}
```

Rows should use JSON-native values:

```text
string
number
boolean
null
array/object only when a renderer explicitly supports nested values
```

Numeric drawing fields should be finite numbers or numeric strings. Renderers are expected to avoid `NaN` geometry, but payload producers should not rely on fallback behavior for required numeric fields.

## Layout Contract

`layout.areas[]` defines where components are placed. A component's `area` must match an existing `layout.areas[].area`.

The runtime may:

```text
create DOM regions from layout.areas
apply title/description/headerHeight/stageInset/className
render zoom popups using a derived one-area payload
```

The runtime must not:

```text
rewrite saved layout geometry
move components to a different area
add or remove component instances
change componentType
change dataBinding
```

## Overlay Contract

Overlay components render in the same area as their base component.

Examples:

```text
trend_line + threshold_line
trend_line + event_marker
line-like component + uncertainty_band
```

Overlay payload rules:

```text
isOverlay: true
area: same area as base visual
zIndex: higher than base component when ordering matters
```

`event_marker` may use `config.value_source_component_id` to bind itself to a specific base component. If that id is missing, it falls back to the first compatible non-overlay component in the same area.

## Runtime Change Rules

Allowed runtime changes:

```text
add a reusable renderer option
add support for a new componentType with explicit mapping
harden missing/null/invalid values
improve sizing, overflow, scroll, or zoom behavior
preserve existing config/data behavior
```

Forbidden runtime changes:

```text
branch on a specific chartId
hardcode chart-specific ticks, labels, marker positions, or data arrays
silently mutate layout, components, componentType, area, or dataBinding
reinterpret axis ticks as thresholds without explicit config
make one application screen's state part of the runtime contract
```

## Payload Producer Rules

Payload producers include Builder, generated chart tooling, drift server, and analysis popups.

They must:

```text
preserve componentInstanceId stability
preserve componentType names
preserve dataBinding.source keys
provide payload.data for every data-backed component
place chart-specific visual constants in config or data
use runtime overrides only for instance-scoped config/theme values
```

They must not:

```text
expect runtime to infer missing required data fields
change componentType to get chart-specific behavior
store screen-specific UI state in runtime payload
overwrite saved chart definitions when only event data changes
```

## Compatibility Checklist

Before changing a saved payload, generated payload, or runtime renderer:

```text
1. Does every component.area exist in layout.areas?
2. Does every data-backed component have dataBinding.source?
3. Does payload.data contain each referenced source?
4. Do data rows contain the fields named in config/dataBinding?
5. Is componentType supported by renderComponent()?
6. Are overlay components in the same area as their base visual?
7. Are chart-specific ticks, labels, markers, and annotations stored in config/data?
8. Did the runtime avoid chartId-specific branches?
9. Did validation include syntax checks and visual smoke tests?
```

Minimum validation:

```powershell
node --check chart_runtime\chart_runtime.js
python -m py_compile chart_runtime\tests\component_visual_smoke.py
python chart_runtime\tests\component_visual_smoke.py
```

When generated chart pages are affected:

```powershell
python chart_builder\tools\generate_recreated_site.py
node --check chart_builder\web\recreated_charts.js
```
