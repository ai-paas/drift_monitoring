/*
 * Source candidate for small overlay renderers.
 *
 * This file is not imported by chart_runtime.js yet. Until a build step is
 * introduced, chart_runtime.js remains the browser artifact and source of truth.
 */

function createOverlayRenderers(deps) {
  const {
    dataFor,
    escapeHtml,
    extent,
    marginFor,
    path,
    svg,
    viewBoxFor
  } = deps;

  function renderThreshold(instance) {
    const value = Number(instance.config.threshold_value || 0.68);
    const y = 180 - value * 120;
    return svg(`<line class="threshold" x1="32" x2="334" y1="${y}" y2="${y}"></line><text class="value" x="238" y="${y - 8}">threshold ${value.toFixed(2)}</text>`);
  }

  function renderEvents(payload, instance) {
    const rows = dataFor(payload, instance);
    const xField = instance.config.time_field || "time";
    const xMin = Number(instance.config.x_min || Math.min(...rows.map((row) => Number(row[xField]) || 1), 1));
    const xMax = Number(instance.config.x_max || Math.max(...rows.map((row) => Number(row[xField]) || 1), 1));
    const { w, h } = viewBoxFor(instance.config, 360, 220);
    const m = marginFor(instance.config, { l: 42, r: 16, t: 18, b: 30 });
    const x = (v) => m.l + ((Number(v) - xMin) / (xMax - xMin || 1)) * (w - m.l - m.r);
    const base = instance.config.value_source_component_id
      ? payload.components.find((item) => item.componentInstanceId === instance.config.value_source_component_id)
      : payload.components.find((item) => item.area === instance.area && !item.isOverlay && ["trend_line","raw_signal_trend","detector_statistic_view","distance_metric_view","performance_metric_view","control_chart","cumulative_curve","model_diagnostic_curve","adaptive_model_structure_view"].includes(item.componentType));
    const yField = base?.config.value_field || base?.config.y_field || base?.config.statistic_field || "value";
    const baseRows = base ? dataFor(payload, base) : [];
    const [yMinRaw, yMaxRaw] = extent(baseRows, yField);
    const yMin = base && Number.isFinite(Number(base.config.y_min)) ? Number(base.config.y_min) : yMinRaw;
    const yMax = base && Number.isFinite(Number(base.config.y_max)) ? Number(base.config.y_max) : yMaxRaw;
    const y = (v) => m.t + (1 - ((Number(v) - yMin) / (yMax - yMin || 1))) * (h - m.t - m.b);
    const markers = rows.map((row) => `<line class="marker-line" x1="${x(row[xField])}" x2="${x(row[xField])}" y1="${m.t}" y2="${h - m.b}"></line>`).join("");
    const highlightType = String(instance.config.highlight_event_type || "");
    const eventTypeField = instance.config.event_type_field || "event_type";
    const highlights = rows.map((row) => {
      const eventType = String(row[eventTypeField] || row.label || "");
      if (!highlightType || eventType !== highlightType) return "";
      const point = baseRows.find((item) => Number(item[xField]) === Number(row[xField]));
      if (!point) return "";
      const cx = x(row[xField]);
      const cy = y(point[yField]);
      const textX = x(Number(row[xField]) + Number(instance.config.annotation_dx || 0));
      const textY = y(Math.min(yMax, Number(point[yField]) + (yMax - yMin) * Number(instance.config.annotation_dy_fraction || 0)));
      const label = row.annotation_label || instance.config.annotation_label || "";
      return `${instance.config.highlight_point ? `<circle class="replace-point" cx="${cx}" cy="${cy}" r="${Number(instance.config.highlight_radius) || 6}"></circle>` : ""}${label ? `<text class="warning-text" x="${textX}" y="${textY}">${escapeHtml(label)}</text>` : ""}`;
    }).join("");
    return svg(`${markers}${highlights}`, `0 0 ${w} ${h}`);
  }

  function renderBand(payload, instance) {
    const rows = dataFor(payload, instance);
    const upper = rows.map((row) => [30 + Number(row.time || 1) * 25, 180 - Number(row.upper || 0.5) * 120]);
    const lower = rows.map((row) => [30 + Number(row.time || 1) * 25, 180 - Number(row.lower || 0.3) * 120]);
    const center = rows.map((row) => [30 + Number(row.time || 1) * 25, 180 - Number(row.center || 0.4) * 120]);
    return svg(`<path class="band" d="${path(upper)} ${lower.slice().reverse().map((p) => `L${p[0]},${p[1]}`).join(" ")} Z"></path><path class="series-line" d="${path(center)}"></path>`);
  }

  return Object.freeze({
    renderThreshold,
    renderEvents,
    renderBand
  });
}

if (typeof module !== "undefined") {
  module.exports = { createOverlayRenderers };
}
