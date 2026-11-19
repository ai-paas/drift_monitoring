# Runtime Payloads

This directory stores canonical chart payloads used by Chart Runtime.

- `runtime_chart_payloads.json`: canonical 53-chart payload set.

The payloads define chart layout, component instances, component config, data binding, and current sample data. To reuse a chart with new data, keep the layout/components/config stable and replace only the matching entries under `data`.
