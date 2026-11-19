/*
 * Source candidate for medium-size renderers.
 *
 * This file is not imported by chart_runtime.js yet. Until a build step is
 * introduced, chart_runtime.js remains the browser artifact and source of truth.
 */

function createScatterRenderers(deps) {
  const {
    dataFor,
    escapeHtml,
    extent,
    formatByMode,
    formatNumber,
    hasFiniteValue,
    marginFor,
    svg,
    ticksFor,
    viewBoxFor
  } = deps;
  function renderScatter(payload, instance) {
    const rows = dataFor(payload, instance);
    const xField = instance.config.x_field || "x";
    const yField = instance.config.y_field || "y";
    const groupField = instance.config.group_field || "group";
    const [xMinRaw, xMaxRaw] = extent(rows, xField);
    const [yMinRaw, yMaxRaw] = extent(rows, yField);
    const xMin = Number.isFinite(Number(instance.config.x_min)) ? Number(instance.config.x_min) : xMinRaw;
    const xMax = Number.isFinite(Number(instance.config.x_max)) ? Number(instance.config.x_max) : xMaxRaw;
    const yMin = Number.isFinite(Number(instance.config.y_min)) ? Number(instance.config.y_min) : yMinRaw;
    const yMax = Number.isFinite(Number(instance.config.y_max)) ? Number(instance.config.y_max) : yMaxRaw;
    const { w, h } = viewBoxFor(instance.config, 472, 185);
    const m = marginFor(instance.config, { t: 12, r: 24, b: 34, l: 44 });
    const x = (v) => m.l + ((Number(v) - xMin) / (xMax - xMin || 1)) * (w - m.l - m.r);
    const y = (v) => m.t + (1 - ((Number(v) - yMin) / (yMax - yMin || 1))) * (h - m.t - m.b);
    const groupClassMap = instance.config.group_class_map || {};
    const groupRadiusMap = instance.config.group_radius_map || {};
    const plotW = w - m.l - m.r;
    const plotH = h - m.t - m.b;
    const xTicks = ticksFor(xMin, xMax, instance.config.x_ticks, 3);
    const yTicks = ticksFor(yMin, yMax, instance.config.y_ticks, 3);
    const grid = instance.config.crosshair === false
      ? `${yTicks.map((tick) => `<line class="grid-line" x1="${m.l}" x2="${m.l + plotW}" y1="${y(tick)}" y2="${y(tick)}"></line>`).join("")}${xTicks.map((tick) => `<line class="grid-line" x1="${x(tick)}" x2="${x(tick)}" y1="${m.t}" y2="${m.t + plotH}"></line>`).join("")}`
      : `<line class="grid-line" x1="${m.l}" x2="${w - m.r}" y1="${y(0)}" y2="${y(0)}"></line><line class="grid-line" x1="${x(0)}" x2="${x(0)}" y1="${m.t}" y2="${h - m.b}"></line>`;
    const diagonalMarkers = (instance.config.diagonal_markers || []).map((marker) => {
      const markerClass = marker.class || "marker-line";
      return `<line class="${escapeHtml(markerClass)}" x1="${x(marker.x0)}" x2="${x(marker.x1)}" y1="${y(marker.y0)}" y2="${y(marker.y1)}"></line>`;
    }).join("");
    const ellipses = (instance.config.ellipses || []).map((ellipseConfig) => {
      const cx = x(ellipseConfig.x);
      const cy = y(ellipseConfig.y);
      const rx = Number(ellipseConfig.rx ?? 20);
      const ry = Number(ellipseConfig.ry ?? 12);
      const rotate = Number(ellipseConfig.rotate ?? 0);
      const transform = rotate ? ` transform="rotate(${rotate} ${cx} ${cy})"` : "";
      return `<ellipse class="${escapeHtml(ellipseConfig.class || "scatter-ellipse")}" cx="${cx}" cy="${cy}" rx="${rx}" ry="${ry}"${transform}></ellipse>`;
    }).join("");
    const dots = rows.map((row) => {
      const group = String(row[groupField] || "value");
      const cls = groupClassMap[group] || "scatter";
      const r = Number(row.r ?? groupRadiusMap[group] ?? instance.config.point_radius ?? 5);
      return `<circle class="${escapeHtml(cls)}" cx="${x(row[xField])}" cy="${y(row[yField])}" r="${r}"></circle>`;
    }).join("");
    const pointHighlights = (instance.config.point_highlights || []).map((point) => {
      if (!hasFiniteValue(point.x) || !hasFiniteValue(point.y)) return "";
      return `<circle class="${escapeHtml(point.class || "alarm-point")}" cx="${x(point.x)}" cy="${y(point.y)}" r="${Number(point.r ?? point.radius ?? 6)}"></circle>`;
    }).join("");
    const annotations = (instance.config.annotations || []).map((annotation) => `<text class="${escapeHtml(annotation.class || "axis-label")}" x="${x(annotation.x)}" y="${y(annotation.y)}">${escapeHtml(annotation.text || "")}</text>`).join("");
    const xTickDy = Number(instance.config.x_tick_dy ?? 18);
    const xAxisLabel = instance.config.x_axis_label ? `<text class="axis-label" x="${Number(instance.config.axis_label_x ?? (m.l + plotW / 2))}" y="${Number(instance.config.axis_label_y ?? (h - 5))}" text-anchor="middle">${escapeHtml(instance.config.x_axis_label)}</text>` : "";
    const yAxisLabel = instance.config.y_axis_label ? `<text class="axis-label" x="${Number(instance.config.y_axis_label_x ?? 16)}" y="${Number(instance.config.y_axis_label_y ?? (m.t + plotH / 2))}" text-anchor="middle" transform="rotate(-90 ${Number(instance.config.y_axis_label_x ?? 16)} ${Number(instance.config.y_axis_label_y ?? (m.t + plotH / 2))})">${escapeHtml(instance.config.y_axis_label)}</text>` : "";
    const tickLabels = `${xTicks.map((tick) => `<text class="axis-tick" x="${x(tick)}" y="${h - m.b + xTickDy}" text-anchor="middle">${formatByMode(tick, instance.config.x_tick_format)}</text>`).join("")}${yTicks.map((tick) => `<text class="axis-tick" x="${m.l - 12}" y="${y(tick) + 4}" text-anchor="end">${formatByMode(tick, instance.config.y_tick_format)}</text>`).join("")}`;
    return svg(`${grid}${ellipses}${diagonalMarkers}${dots}${pointHighlights}<line class="axis-line" x1="${m.l}" x2="${w - m.r}" y1="${h - m.b}" y2="${h - m.b}"></line><line class="axis-line" x1="${m.l}" x2="${m.l}" y1="${m.t}" y2="${h - m.b}"></line>${tickLabels}${xAxisLabel}${yAxisLabel}${annotations}`, `0 0 ${w} ${h}`);
  }

  function renderFeatureProjection(payload, instance) {
    const rows = dataFor(payload, instance);
    const kindField = instance.config.kind_field || "kind";
    const featureKind = instance.config.feature_kind || "feature";
    const pointKind = instance.config.point_kind || "point";
    const featureRows = rows.filter((row) => String(row[kindField]) === String(featureKind));
    const pointRows = rows.filter((row) => String(row[kindField]) === String(pointKind));
    const featureNameField = instance.config.feature_name_field || "feature";
    const featureValueField = instance.config.feature_value_field || "value";
    const pointXField = instance.config.point_x_field || "x";
    const pointYField = instance.config.point_y_field || "y";
    const pointGroupField = instance.config.point_group_field || "group";
    const { w, h } = viewBoxFor(instance.config, 472, 185);
    const featureArea = instance.config.feature_area || {};
    const projectionArea = instance.config.projection_area || {};
    const featureX0 = Number(featureArea.x ?? 72);
    const featureY0 = Number(featureArea.y ?? 24);
    const featureW = Number(featureArea.width ?? 180);
    const featureMax = Number(featureArea.x_max ?? Math.max(...featureRows.map((row) => Number(row[featureValueField]) || 0), 1));
    const featureRowGap = Number(featureArea.row_gap ?? 25);
    const featureBarH = Number(featureArea.bar_height ?? 15);
    const featureX = (value) => featureX0 + (Number(value) / (featureMax || 1)) * featureW;
    const featureBars = featureRows.map((row, i) => {
      const y0 = featureY0 + i * featureRowGap;
      const value = Number(row[featureValueField]) || 0;
      const valueText = row.display_value ?? row.displayValue ?? formatNumber(value);
      return `<text class="axis-tick" x="${featureX0 - 9}" y="${y0 + featureBarH - 3}" text-anchor="end">${escapeHtml(row[featureNameField] || "")}</text>
        <rect class="${escapeHtml(instance.config.feature_bar_class || "bar")}" x="${featureX0}" y="${y0}" width="${Math.max(0, featureX(value) - featureX0)}" height="${featureBarH}" rx="${Number(featureArea.bar_radius ?? 3)}"></rect>
        <text class="bar-label" x="${featureX(value) + 7}" y="${y0 + featureBarH - 3}">${escapeHtml(valueText)}</text>`;
    }).join("");
    const projectionX0 = Number(projectionArea.x0 ?? 292);
    const projectionX1 = Number(projectionArea.x1 ?? (w - 20));
    const projectionY0 = Number(projectionArea.y0 ?? 20);
    const projectionY1 = Number(projectionArea.y1 ?? (h - 34));
    const xMin = Number(projectionArea.x_min ?? instance.config.x_min ?? -1);
    const xMax = Number(projectionArea.x_max ?? instance.config.x_max ?? 1);
    const yMin = Number(projectionArea.y_min ?? instance.config.y_min ?? -1);
    const yMax = Number(projectionArea.y_max ?? instance.config.y_max ?? 1);
    const px = (value) => projectionX0 + ((Number(value) - xMin) / (xMax - xMin || 1)) * (projectionX1 - projectionX0);
    const py = (value) => projectionY0 + (1 - ((Number(value) - yMin) / (yMax - yMin || 1))) * (projectionY1 - projectionY0);
    const groupClassMap = instance.config.group_class_map || {};
    const projectionFrameClass = instance.config.projection_frame_class || "small-panel-frame";
    const projectionFrame = instance.config.projection_frame === false ? "" : `<rect class="${escapeHtml(projectionFrameClass)}" x="${projectionX0}" y="${projectionY0}" width="${projectionX1 - projectionX0}" height="${projectionY1 - projectionY0}"></rect>`;
    const crosshairClass = instance.config.crosshair_class || "grid-line";
    const crosshair = instance.config.crosshair === false ? "" : `<line class="${escapeHtml(crosshairClass)}" x1="${projectionX0}" x2="${projectionX1}" y1="${py(0)}" y2="${py(0)}"></line><line class="${escapeHtml(crosshairClass)}" x1="${px(0)}" x2="${px(0)}" y1="${projectionY0}" y2="${projectionY1}"></line>`;
    const dots = pointRows.map((row) => {
      const group = String(row[pointGroupField] || "value");
      const cls = groupClassMap[group] || row.class || "scatter";
      const cx = instance.config.point_coordinate_mode === "pixel" ? Number(row[pointXField]) : px(row[pointXField]);
      const cy = instance.config.point_coordinate_mode === "pixel" ? Number(row[pointYField]) : py(row[pointYField]);
      return `<circle class="${escapeHtml(cls)}" cx="${cx}" cy="${cy}" r="${Number(row.r ?? instance.config.point_radius ?? 4.5)}"></circle>`;
    }).join("");
    const labels = (instance.config.labels || []).map((label) => `<text class="${escapeHtml(label.class || "axis-label")}" x="${Number(label.x)}" y="${Number(label.y)}" text-anchor="${escapeHtml(label.anchor || "start")}">${escapeHtml(label.text || "")}</text>`).join("");
    const annotations = (instance.config.annotations || []).map((annotation) => `<text class="${escapeHtml(annotation.class || "axis-label")}" x="${Number(annotation.x)}" y="${Number(annotation.y)}" text-anchor="${escapeHtml(annotation.anchor || "start")}">${escapeHtml(annotation.text || "")}</text>`).join("");
    return svg(`${labels}${featureBars}<line class="axis-line" x1="${featureX0}" x2="${featureX0 + featureW}" y1="${Number(featureArea.axis_y ?? (h - 34))}" y2="${Number(featureArea.axis_y ?? (h - 34))}"></line>${projectionFrame}${crosshair}${dots}${annotations}`, `0 0 ${w} ${h}`);
  }

  return Object.freeze({
    renderScatter,
    renderFeatureProjection
  });
}

if (typeof module !== "undefined") {
  module.exports = { createScatterRenderers };
}
