/*
 * Source candidate for distribution renderers.
 *
 * This file is not imported by chart_runtime.js yet. Until a build step is
 * introduced, chart_runtime.js remains the browser artifact and source of truth.
 */

function createDistributionRenderers(deps) {
  const {
    dataFor,
    escapeHtml,
    extent,
    formatByMode,
    formatNumber,
    hasFiniteValue,
    marginFor,
    path,
    renderCard,
    svg,
    ticksFor,
    viewBoxFor
  } = deps;

  function renderDistribution(payload, instance) {
    const rows = dataFor(payload, instance);
    const valueField = instance.config.value_field || instance.config.count_field || "value";
    if (instance.config.distribution_style === "violin_summary") {
      const validRows = rows.filter((row) => Array.isArray(row.density) && hasFiniteValue(row.mean));
      if (!validRows.length) return renderCard(payload, instance);
      const lowField = instance.config.low_field || "low";
      const highField = instance.config.high_field || "high";
      const q1Field = instance.config.q1_field || "q1";
      const q3Field = instance.config.q3_field || "q3";
      const medianField = instance.config.median_field || "median";
      const meanField = instance.config.mean_field || "mean";
      const labelField = instance.config.label_field || "label";
      const classField = instance.config.class_field || "class";
      let { w, h } = viewBoxFor(instance.config, 630, 440);
      const m = marginFor(instance.config, { t: 22, r: 28, b: 60, l: 58 });
      const minGroupW = Number(instance.config.min_group_width ?? 92);
      w = Math.max(w, Math.ceil(m.l + m.r + validRows.length * minGroupW));
      const plotW = w - m.l - m.r;
      const plotH = h - m.t - m.b;
      const values = validRows.flatMap((row) => row.density.map((point) => Number(point[0])).concat([row[lowField], row[highField], row[q1Field], row[q3Field], row[medianField], row[meanField]])).filter(Number.isFinite);
      const yMin = Number.isFinite(Number(instance.config.y_min)) ? Number(instance.config.y_min) : Math.min(...values);
      const yMax = Number.isFinite(Number(instance.config.y_max)) ? Number(instance.config.y_max) : Math.max(...values);
      const y = (v) => m.t + (1 - ((Number(v) - yMin) / (yMax - yMin || 1))) * plotH;
      const yTicks = ticksFor(yMin, yMax, instance.config.y_ticks, 5);
      const xPositions = Array.isArray(instance.config.x_positions) && instance.config.x_positions.length >= validRows.length
        ? instance.config.x_positions
        : validRows.map((_, i) => m.l + plotW * ((i + 1) / (validRows.length + 1)));
      const widthScale = Number(instance.config.density_width ?? 72);
      const boxWidth = Number(instance.config.box_width ?? 68);
      const meanWidth = Number(instance.config.mean_width ?? 84);
      const defaultClasses = instance.config.violin_classes || ["ref-fill", "cur-fill"];
      const violinPath = (density, xCenter) => {
        const right = density.map((point) => [xCenter + Number(point[1]) * widthScale, y(point[0])]);
        const left = density.slice().reverse().map((point) => [xCenter - Number(point[1]) * widthScale, y(point[0])]);
        return right.concat(left).map((point, i) => `${i ? "L" : "M"}${point[0].toFixed(2)},${point[1].toFixed(2)}`).join(" ") + "Z";
      };
      const grid = yTicks.map((tick) => `<line class="grid-line" x1="${m.l}" x2="${m.l + plotW}" y1="${y(tick)}" y2="${y(tick)}"></line><text class="axis-tick" x="${m.l - 12}" y="${y(tick) + 4}" text-anchor="end">${formatByMode(tick, instance.config.y_tick_format)}</text>`).join("");
      const groups = validRows.map((row, i) => {
        const x0 = Number(row.x ?? xPositions[i]);
        const cls = row[classField] || defaultClasses[i] || "distribution-summary-violin";
        const label = row[labelField] || "";
        const meanLabel = row.meanLabel || row.mean_label || `${label} mean ${Number(row[meanField]).toFixed(1)}`;
        const meanLabelDy = Number(instance.config.mean_label_dy ?? -10);
        const showMeanLabel = instance.config.show_mean_labels !== false && meanLabelDy > -500;
        return `<path class="${escapeHtml(cls)}" d="${violinPath(row.density, x0)}"></path>
          <line class="${escapeHtml(instance.config.whisker_class || "axis-line")}" x1="${x0}" x2="${x0}" y1="${y(row[lowField])}" y2="${y(row[highField])}"></line>
          <rect class="${escapeHtml(row.box_class || instance.config.box_class || "summary-box")}" x="${x0 - boxWidth / 2}" y="${y(row[q3Field])}" width="${boxWidth}" height="${Math.max(0, y(row[q1Field]) - y(row[q3Field]))}" rx="${Number(instance.config.box_radius ?? 4)}"></rect>
          <line class="${escapeHtml(instance.config.median_class || "median-line")}" x1="${x0 - boxWidth / 2}" x2="${x0 + boxWidth / 2}" y1="${y(row[medianField])}" y2="${y(row[medianField])}"></line>
          <line class="${escapeHtml(instance.config.mean_line_class || "mean-line-solid")}" x1="${x0 - meanWidth / 2}" x2="${x0 + meanWidth / 2}" y1="${y(row[meanField])}" y2="${y(row[meanField])}"></line>
          ${instance.config.show_mean_points ? `<circle class="${escapeHtml(instance.config.mean_point_class || "mean-point")}" cx="${x0}" cy="${y(row[meanField])}" r="${Number(instance.config.mean_point_radius ?? 5)}"></circle>` : ""}
          ${showMeanLabel ? `<text class="${escapeHtml(instance.config.mean_label_class || "callout")}" x="${x0}" y="${y(row[meanField]) + meanLabelDy}" text-anchor="middle">${escapeHtml(meanLabel)}</text>` : ""}
          <text class="${escapeHtml(instance.config.group_label_class || "title-text")}" x="${x0}" y="${Number(instance.config.group_label_y ?? (h - 22))}" text-anchor="middle">${escapeHtml(label)}</text>`;
      }).join("");
      const connectors = (instance.config.connectors || []).map((connector) => {
        const fromIndex = Number(connector.from_index ?? 0);
        const toIndex = Number(connector.to_index ?? 1);
        const fromRow = validRows[fromIndex];
        const toRow = validRows[toIndex];
        const field = connector.field || medianField;
        if (!fromRow || !toRow || !hasFiniteValue(fromRow[field]) || !hasFiniteValue(toRow[field])) return "";
        const x1 = Number(connector.x1 ?? fromRow.x ?? xPositions[fromIndex]) + Number(connector.x1_offset ?? 0);
        const x2 = Number(connector.x2 ?? toRow.x ?? xPositions[toIndex]) + Number(connector.x2_offset ?? 0);
        return `<line class="${escapeHtml(connector.class || "threshold-line")}" x1="${x1}" x2="${x2}" y1="${y(fromRow[field])}" y2="${y(toRow[field])}"></line>`;
      }).join("");
      const annotations = (instance.config.annotations || []).map((annotation) => `<text class="${escapeHtml(annotation.class || "axis-label")}" x="${Number(annotation.x)}" y="${Number(annotation.y)}" text-anchor="${escapeHtml(annotation.anchor || "middle")}">${escapeHtml(annotation.text || "")}</text>`).join("");
      const xAxis = `<line class="axis-line" x1="${m.l}" x2="${m.l + plotW}" y1="${h - m.b}" y2="${h - m.b}"></line>`;
      const yAxis = `<line class="axis-line" x1="${m.l}" x2="${m.l}" y1="${m.t}" y2="${h - m.b}"></line>`;
      const yLabel = instance.config.y_axis_label === false ? "" : `<text class="axis-label" x="${Number(instance.config.y_axis_label_x ?? 16)}" y="${Number(instance.config.y_axis_label_y ?? (m.t + plotH / 2))}" text-anchor="middle" transform="rotate(-90 ${Number(instance.config.y_axis_label_x ?? 16)} ${Number(instance.config.y_axis_label_y ?? (m.t + plotH / 2))})">${escapeHtml(instance.config.y_axis_label || valueField)}</text>`;
      return svg(`${grid}${xAxis}${yAxis}${groups}${connectors}${yLabel}${annotations}`, `0 0 ${w} ${h}`);
    }
    if (instance.config.distribution_style === "histogram_overlay") {
      const x0Field = instance.config.x0_field || "x0";
      const x1Field = instance.config.x1_field || "x1";
      const primaryField = instance.config.primary_value_field || "reference";
      const secondaryField = instance.config.secondary_value_field || "current";
      const overlapField = instance.config.overlap_value_field || instance.config.intersection_value_field;
      const validRows = rows.filter((row) => hasFiniteValue(row[x0Field]) && hasFiniteValue(row[x1Field]) && (hasFiniteValue(row[primaryField]) || hasFiniteValue(row[secondaryField]) || (overlapField && hasFiniteValue(row[overlapField]))));
      if (!validRows.length) return renderCard(payload, instance);
      const xMin = Number.isFinite(Number(instance.config.x_min)) ? Number(instance.config.x_min) : Math.min(...validRows.map((row) => Number(row[x0Field])));
      const xMax = Number.isFinite(Number(instance.config.x_max)) ? Number(instance.config.x_max) : Math.max(...validRows.map((row) => Number(row[x1Field])));
      const yValues = validRows.flatMap((row) => [row[primaryField], row[secondaryField], overlapField ? row[overlapField] : undefined]).filter(hasFiniteValue).map(Number);
      const yMin = Number.isFinite(Number(instance.config.y_min)) ? Number(instance.config.y_min) : 0;
      const yMax = Number.isFinite(Number(instance.config.y_max)) ? Number(instance.config.y_max) : Math.max(...yValues, 1);
      const { w, h } = viewBoxFor(instance.config, 390, 470);
      const m = marginFor(instance.config, { t: 22, r: 24, b: 52, l: 58 });
      const plotW = w - m.l - m.r;
      const plotH = h - m.t - m.b;
      const x = (v) => m.l + ((Number(v) - xMin) / (xMax - xMin || 1)) * plotW;
      const y = (v) => m.t + (1 - ((Number(v) - yMin) / (yMax - yMin || 1))) * plotH;
      const yTicks = ticksFor(yMin, yMax, instance.config.y_ticks, 3);
      const xTicks = ticksFor(xMin, xMax, instance.config.x_ticks, 3);
      const primaryClass = instance.config.primary_bar_class || "bar-ref";
      const secondaryClass = instance.config.secondary_bar_class || "bar-cur";
      const overlapClass = instance.config.overlap_bar_class || "overlap-bar";
      const primaryClassField = instance.config.primary_class_field || instance.config.bar_class_field;
      const secondaryClassField = instance.config.secondary_class_field;
      const overlapClassField = instance.config.overlap_class_field;
      const primaryWidth = Number(instance.config.primary_width_fraction ?? 0.96);
      const secondaryWidth = Number(instance.config.secondary_width_fraction ?? 0.64);
      const secondaryOffset = Number(instance.config.secondary_offset_fraction ?? 0.18);
      const overlapWidth = Number(instance.config.overlap_width_fraction ?? 0.52);
      const overlapOffset = Number(instance.config.overlap_offset_fraction ?? 0.24);
      const radius = Number(instance.config.bar_radius ?? 0);
      const bars = validRows.map((row) => {
        const x0 = x(row[x0Field]);
        const x1 = x(row[x1Field]);
        const binW = Math.max(1, x1 - x0 - Number(instance.config.bin_gap ?? 1));
        const primaryRowClass = primaryClassField && row[primaryClassField] ? row[primaryClassField] : primaryClass;
        const secondaryRowClass = secondaryClassField && row[secondaryClassField] ? row[secondaryClassField] : secondaryClass;
        const overlapRowClass = overlapClassField && row[overlapClassField] ? row[overlapClassField] : overlapClass;
        const primary = hasFiniteValue(row[primaryField])
          ? `<rect class="${escapeHtml(primaryRowClass)}" x="${x0}" y="${y(row[primaryField])}" width="${Math.max(1, binW * primaryWidth)}" height="${Math.max(0, y(0) - y(row[primaryField]))}" rx="${radius}"></rect>`
          : "";
        const secondary = hasFiniteValue(row[secondaryField])
          ? `<rect class="${escapeHtml(secondaryRowClass)}" x="${x0 + binW * secondaryOffset}" y="${y(row[secondaryField])}" width="${Math.max(1, binW * secondaryWidth)}" height="${Math.max(0, y(0) - y(row[secondaryField]))}" rx="${radius}"></rect>`
          : "";
        const overlap = overlapField && hasFiniteValue(row[overlapField])
          ? `<rect class="${escapeHtml(overlapRowClass)}" x="${x0 + binW * overlapOffset}" y="${y(row[overlapField])}" width="${Math.max(1, binW * overlapWidth)}" height="${Math.max(0, y(0) - y(row[overlapField]))}" rx="${radius}"></rect>`
          : "";
        return `${primary}${secondary}${overlap}`;
      }).join("");
      const connectorField = instance.config.connector_value_field;
      const connectorMin = Number(instance.config.connector_min ?? 0);
      const connectors = connectorField ? validRows.map((row) => {
        if (!hasFiniteValue(row[connectorField]) || Number(row[connectorField]) <= connectorMin || !hasFiniteValue(row[primaryField]) || !hasFiniteValue(row[secondaryField])) return "";
        const x0 = x(row[x0Field]);
        const x1 = x(row[x1Field]);
        const binW = Math.max(1, x1 - x0 - Number(instance.config.bin_gap ?? 1));
        const connectorX = x0 + binW * Number(instance.config.connector_x_fraction ?? (secondaryOffset + secondaryWidth / 2));
        return `<line class="${escapeHtml(row.connector_class || instance.config.connector_class || "connector-line")}" x1="${connectorX}" x2="${connectorX}" y1="${y(row[primaryField])}" y2="${y(row[secondaryField])}"></line>`;
      }).join("") : "";
      const xTickLabels = Array.isArray(instance.config.x_tick_labels) ? instance.config.x_tick_labels : [];
      const verticalMarkers = (instance.config.vertical_markers || []).map((marker) => `<line class="${escapeHtml(marker.class || "marker-line")}" x1="${x(marker.x)}" x2="${x(marker.x)}" y1="${Number(marker.y1 ?? m.t)}" y2="${Number(marker.y2 ?? (h - m.b))}"></line>${marker.label ? `<text class="${escapeHtml(marker.label_class || "axis-label")}" x="${x(marker.x) + Number(marker.label_dx ?? -4)}" y="${Number(marker.label_y ?? (m.t + 14))}" text-anchor="${escapeHtml(marker.label_anchor || "end")}">${escapeHtml(marker.label)}</text>` : ""}`).join("");
      const annotations = (instance.config.annotations || []).map((annotation) => `<text class="${escapeHtml(annotation.class || "axis-label")}" x="${x(annotation.x)}" y="${y(annotation.y)}">${escapeHtml(annotation.text || "")}</text>`).join("");
      return svg(`
        ${yTicks.map((tick) => `<line class="grid-line" x1="${m.l}" x2="${m.l + plotW}" y1="${y(tick)}" y2="${y(tick)}"></line><text class="axis-tick" x="${m.l - 12}" y="${y(tick) + 4}" text-anchor="end">${formatByMode(tick, instance.config.y_tick_format)}</text>`).join("")}
        ${xTicks.map((tick, index) => `<line class="grid-line" x1="${x(tick)}" x2="${x(tick)}" y1="${m.t}" y2="${m.t + plotH}"></line><text class="axis-tick" x="${x(tick)}" y="${m.t + plotH + 24}" text-anchor="middle">${escapeHtml(xTickLabels[index] ?? formatByMode(tick, instance.config.x_tick_format))}</text>`).join("")}
        ${bars}
        ${connectors}
        ${verticalMarkers}
        <line class="axis-line" x1="${m.l}" x2="${m.l + plotW}" y1="${h - m.b}" y2="${h - m.b}"></line>
        <line class="axis-line" x1="${m.l}" x2="${m.l}" y1="${m.t}" y2="${h - m.b}"></line>
        <text class="axis-label" x="${m.l + plotW / 2}" y="${h - 12}" text-anchor="middle">${escapeHtml(instance.config.x_axis_label || x0Field)}</text>
        ${instance.config.y_axis_label === false ? "" : `<text class="axis-label" x="16" y="${m.t + plotH / 2}" text-anchor="middle" transform="rotate(-90 16 ${m.t + plotH / 2})">${escapeHtml(instance.config.y_axis_label || "density")}</text>`}
        ${annotations}`, `0 0 ${w} ${h}`);
    }
    if (instance.config.distribution_style === "density_area") {
      const xField = instance.config.x_field || "x";
      const primaryField = instance.config.primary_value_field || "baseline";
      const secondaryField = instance.config.secondary_value_field || "current";
      const differenceField = instance.config.difference_value_field;
      const primaryRows = rows.filter((row) => hasFiniteValue(row[xField]) && hasFiniteValue(row[primaryField]));
      if (!primaryRows.length) return renderCard(payload, instance);
      const secondaryRows = rows.filter((row) => hasFiniteValue(row[xField]) && hasFiniteValue(row[secondaryField]));
      const differenceRows = differenceField
        ? rows.filter((row) => hasFiniteValue(row[xField]) && hasFiniteValue(row[differenceField]))
        : [];
      const [xMinRaw, xMaxRaw] = extent(rows, xField);
      const yValues = rows.flatMap((row) => [row[primaryField], row[secondaryField], differenceField ? row[differenceField] : undefined]).filter(hasFiniteValue).map(Number);
      const yMin = Number.isFinite(Number(instance.config.y_min)) ? Number(instance.config.y_min) : 0;
      const yMax = Number.isFinite(Number(instance.config.y_max)) ? Number(instance.config.y_max) : Math.max(...yValues, 1);
      const xMin = Number.isFinite(Number(instance.config.x_min)) ? Number(instance.config.x_min) : xMinRaw;
      const xMax = Number.isFinite(Number(instance.config.x_max)) ? Number(instance.config.x_max) : xMaxRaw;
      const { w, h } = viewBoxFor(instance.config, 630, 440);
      const m = marginFor(instance.config, { t: 24, r: 28, b: 62, l: 58 });
      const x = (v) => m.l + ((Number(v) - xMin) / (xMax - xMin || 1)) * (w - m.l - m.r);
      const y = (v) => m.t + (1 - ((Number(v) - yMin) / (yMax - yMin || 1))) * (h - m.t - m.b);
      const area = (seriesRows, field, cls) => {
        const pts = seriesRows.map((row) => [x(row[xField]), y(row[field])]);
        if (!pts.length) return "";
        const baseY = y(yMin);
        return `<path class="${escapeHtml(cls)}" d="${path(pts)} L${pts[pts.length - 1][0].toFixed(1)},${baseY.toFixed(1)} L${pts[0][0].toFixed(1)},${baseY.toFixed(1)} Z"></path>`;
      };
      const plotW = w - m.l - m.r;
      const plotH = h - m.t - m.b;
      const yTicks = ticksFor(yMin, yMax, instance.config.y_ticks, 5);
      const xTicks = ticksFor(xMin, xMax, instance.config.x_ticks, 5);
      const verticalMarkers = (instance.config.vertical_markers || []).map((marker) => `<line class="${escapeHtml(marker.class || "threshold-line")}" x1="${x(marker.x)}" x2="${x(marker.x)}" y1="${m.t}" y2="${h - m.b}"></line>${marker.label ? `<text class="${escapeHtml(marker.label_class || "warning-text")}" x="${x(marker.x) + Number(marker.label_dx ?? 10)}" y="${y(marker.label_y ?? yMax * 0.78)}">${escapeHtml(marker.label)}</text>` : ""}`).join("");
      const segmentMarkers = (instance.config.segment_markers || []).map((marker) => {
        const markerY = y(marker.y);
        const markerClass = marker.class || "marker-line";
        const pointClass = marker.point_class || "marker-point";
        const radius = Number(marker.r ?? 4);
        return `<line class="${escapeHtml(markerClass)}" x1="${x(marker.x0)}" x2="${x(marker.x1)}" y1="${markerY}" y2="${markerY}"></line>
          <circle class="${escapeHtml(pointClass)}" cx="${x(marker.x0)}" cy="${markerY}" r="${radius}"></circle>
          <circle class="${escapeHtml(pointClass)}" cx="${x(marker.x1)}" cy="${markerY}" r="${radius}"></circle>`;
      }).join("");
      const annotations = (instance.config.annotations || []).map((annotation) => `<text class="${escapeHtml(annotation.class || "axis-label")}" x="${x(annotation.x)}" y="${y(annotation.y)}">${escapeHtml(annotation.text || "")}</text>`).join("");
      return svg(`
        ${yTicks.map((tick) => `<line class="grid-line" x1="${m.l}" x2="${m.l + plotW}" y1="${y(tick)}" y2="${y(tick)}"></line><text class="axis-tick" x="${m.l - 12}" y="${y(tick) + 4}" text-anchor="end">${formatNumber(tick)}</text>`).join("")}
        ${area(differenceRows, differenceField, instance.config.difference_area_class || "difference-area")}
        ${area(primaryRows, primaryField, instance.config.primary_area_class || "base-area")}
        ${area(secondaryRows, secondaryField, instance.config.secondary_area_class || "current-area")}
        ${segmentMarkers}
        ${verticalMarkers}
        <line class="axis-line" x1="${m.l}" x2="${m.l + plotW}" y1="${h - m.b}" y2="${h - m.b}"></line>
        <line class="axis-line" x1="${m.l}" x2="${m.l}" y1="${m.t}" y2="${h - m.b}"></line>
        ${xTicks.map((tick) => `<text class="axis-tick" x="${x(tick)}" y="${h - m.b + 24}" text-anchor="middle">${formatNumber(tick)}</text>`).join("")}
        <text class="axis-label" x="${m.l + plotW / 2}" y="${h - 12}" text-anchor="middle">${escapeHtml(instance.config.x_axis_label || xField)}</text>
        ${instance.config.y_axis_label === false ? "" : `<text class="axis-label" x="16" y="${m.t + plotH / 2}" text-anchor="middle" transform="rotate(-90 16 ${m.t + plotH / 2})">${escapeHtml(instance.config.y_axis_label || "density")}</text>`}
        ${annotations}`, `0 0 ${w} ${h}`);
    }
    const groups = [...new Set(rows.map((row) => row.group || "value"))].slice(0, 2);
    const values = rows.map((row) => Number(row[valueField])).filter(Number.isFinite);
    const max = Math.max(...values, 1);
    return svg(rows.slice(0, 18).map((row, i) => {
      const h = (Number(row[valueField]) || 0) / max * 120;
      const group = groups.indexOf(row.group || "value");
      return `<rect class="bar${group === 1 ? " hot" : ""}" x="${36 + i * 16}" y="${176 - h}" width="10" height="${h}" rx="2"></rect>`;
    }).join("") + `<line class="axis-line" x1="28" x2="340" y1="176" y2="176"></line>`);
  }

  return Object.freeze({
    renderDistribution
  });
}

if (typeof module !== "undefined") {
  module.exports = { createDistributionRenderers };
}
