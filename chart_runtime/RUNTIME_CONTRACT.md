# Runtime Contract

The runtime renders a chart from this contract:

```text
payload.layout + payload.components + payload.data + component config
```

The runtime is shared by Builder previews, generated chart pages, recreated chart viewer, and analysis popups. It must remain chart-agnostic.

For compatibility rules, renderer mapping, payload producer rules, and validation checklists, see [PAYLOAD_RUNTIME_COMPATIBILITY.md](./PAYLOAD_RUNTIME_COMPATIBILITY.md).

## Payload

Required top-level fields:

- `chartId`: stable chart identifier
- `layout`: semantic grid layout
- `components`: component instance list
- `data`: data source map keyed by `dataBinding.source`

Optional fields such as `title`, `originalPath`, and `reproduction` are application metadata. The renderer must not require application-specific metadata to draw the chart.

## Layout Area

Each `layout.areas[]` item defines a semantic render region:

- `area`: stable area key
- `role`: semantic role such as `summary`, `primary_visual`, `secondary_visual`, `interpretation`
- `x`, `y`, `w`, `h`: grid position
- `title`, `description`, `headerHeight`, `stageInset`, `className`: optional display metadata

The runtime may interpret area metadata, but must not rewrite layout geometry for a specific chart.

## Component Instance

Each `components[]` item defines one renderer instance:

- `componentInstanceId`: stable instance id
- `componentType`: renderer selection key
- `area`: target layout area
- `isOverlay`: whether the instance overlays another component
- `zIndex`: overlay/display ordering hint
- `config`: renderer options
- `dataBinding`: data source and field mapping

The runtime chooses a renderer by `componentType`. It must not change `componentType`, move components between areas, or add/remove component instances.

## Data Binding

`dataBinding.source` points to `payload.data[source]`. Renderers should read fields from `config` first when the existing renderer contract does so, then fall back to conventional field names.

Saved chart definitions should keep `dataBinding` even when a renderer currently reads equivalent field names from `config`; Builder and later validation depend on that schema information.

## Config

`config` stores chart-specific visual parameters:

- geometry: `view_box`, `margin`, `stageInset`
- domain: `x_min`, `x_max`, `y_min`, `y_max`
- axis/tick: `x_ticks`, `y_ticks`, labels, tick offsets
- field mapping: `x_field`, `y_field`, `value_field`, `series_fields`
- style classes: line/bar/group class maps
- marker/annotation definitions
- responsive and overflow hints

Chart-specific ticks, marker positions, annotation text, and class choices belong in payload config or data, not in `chart_runtime.js`.

## Runtime Overrides

Runtime overrides may be applied immediately before rendering for tenant, feature, or event-specific values. Overrides must be instance-id scoped and must not mutate saved payload files.

Allowed override targets:

- component `config` values such as thresholds, markers, domains, labels
- theme values

Forbidden override targets:

- `layout`
- `components`
- `componentType`
- `area`
- `dataBinding`

## Stability Rule

A runtime change is acceptable only when it is a reusable renderer capability or a common stability fix. If a change requires knowing a specific chart id or original source text, it belongs in payload data/config instead.
