/*
 * Source candidate for high-traffic line/bar renderers.
 *
 * This file is not imported by chart_runtime.js yet. Until a build step is
 * introduced, chart_runtime.js remains the browser artifact and source of truth.
 */

function createLineRenderers(deps) {
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
    rowsForSource,
    stepPath,
    svg,
    ticksFor,
    viewBoxFor
  } = deps;

  function renderLine(payload, instance) {
    const rows = dataFor(payload, instance);
    const xField = instance.config.time_field || instance.config.x_field || "time";
    const yField = instance.config.value_field || instance.config.y_field || instance.config.statistic_field || "value";
    const secondaryField = instance.config.secondary_value_field;
    const primaryRows = rows.filter((row) => hasFiniteValue(row[xField]) && hasFiniteValue(row[yField]));
    if (!primaryRows.length) return renderCard(payload, instance);
    const secondaryRows = secondaryField
      ? primaryRows.filter((row) => hasFiniteValue(row[secondaryField]))
      : [];
    const [xMinRaw, xMaxRaw] = extent(primaryRows, xField);
    const xMin = Number.isFinite(Number(instance.config.x_min)) ? Number(instance.config.x_min) : xMinRaw;
    const xMax = Number.isFinite(Number(instance.config.x_max)) ? Number(instance.config.x_max) : xMaxRaw;
    const [yMinRaw, yMaxRaw] = extent(primaryRows, yField);
    const [y2MinRaw, y2MaxRaw] = secondaryRows.length ? extent(secondaryRows, secondaryField) : [yMinRaw, yMaxRaw];
    const yMin = Number.isFinite(Number(instance.config.y_min)) ? Number(instance.config.y_min) : Math.min(0, yMinRaw, y2MinRaw);
    const yMax = Number.isFinite(Number(instance.config.y_max)) ? Number(instance.config.y_max) : Math.max(yMaxRaw, y2MaxRaw) * 1.08;
    const { w, h } = viewBoxFor(instance.config, 360, 220);
    const m = marginFor(instance.config, { l: 42, r: 16, t: 18, b: 30 });
    const x = (v) => m.l + ((Number(v) - xMin) / (xMax - xMin || 1)) * (w - m.l - m.r);
    const y = (v) => m.t + (1 - ((Number(v) - yMin) / (yMax - yMin || 1))) * (h - m.t - m.b);
    const pts = primaryRows.map((row) => [x(row[xField]), y(row[yField])]);
    const pathForLine = (points) => instance.config.line_interpolation === "step" || instance.config.curve === "step"
      ? stepPath(points)
      : path(points);
    const sampleEvery = Math.max(1, Number(instance.config.point_sample_every) || Math.ceil(primaryRows.length / 16));
    const pointRadius = Number(instance.config.point_radius) || 2.4;
    const pointClassField = instance.config.point_class_field;
    const pointRadiusField = instance.config.point_radius_field || instance.config.point_r_field;
    const primaryDots = instance.config.show_points === false ? "" : primaryRows.map((row, i) => (
      i % sampleEvery === 0 || i === primaryRows.length - 1
        ? `<circle class="${escapeHtml(pointClassField && row[pointClassField] ? row[pointClassField] : instance.config.primary_point_class || "series-point")}" cx="${x(row[xField])}" cy="${y(row[yField])}" r="${Number(pointRadiusField && row[pointRadiusField] !== undefined ? row[pointRadiusField] : pointRadius)}"></circle>`
        : ""
    )).join("");
    const primaryLineClass = instance.config.line_class || "series-line";
    const secondaryLineClass = instance.config.secondary_line_class || "secondary-line";
    const backgroundRegions = (instance.config.background_regions || []).map((region) => {
      const x0 = x(region.x0);
      const x1 = x(region.x1);
      return `<rect x="${Math.min(x0, x1)}" y="${m.t}" width="${Math.abs(x1 - x0)}" height="${h - m.t - m.b}" fill="${escapeHtml(region.fill || "rgba(47,111,159,.08)")}"></rect>`;
    }).join("");
    const lineSegments = (field, lineClass) => {
      const segments = [];
      let current = [];
      primaryRows.forEach((row) => {
        if (!hasFiniteValue(row[field])) {
          if (current.length) segments.push(current);
          current = [];
        } else {
          current.push([x(row[xField]), y(row[field])]);
        }
      });
      if (current.length) segments.push(current);
      return segments.map((segment) => `<path class="${escapeHtml(lineClass)}" d="${pathForLine(segment)}"></path>`).join("");
    };
    const secondary = secondaryRows.length
      ? lineSegments(secondaryField, secondaryLineClass)
      : "";
    const secondaryDots = secondaryRows.length && instance.config.show_secondary_points !== false
      ? secondaryRows.map((row, i) => (
        i % sampleEvery === 0 || i === secondaryRows.length - 1
          ? `<circle class="${escapeHtml(instance.config.secondary_point_class || "secondary-point")}" cx="${x(row[xField])}" cy="${y(row[secondaryField])}" r="${Number(instance.config.secondary_point_radius) || 2.2}"></circle>`
          : ""
      )).join("")
      : "";
    const fillBetween = (instance.config.fill_between || []).map((band) => {
      const upperField = band.upper_field || band.top_field || yField;
      const lowerField = band.lower_field || band.bottom_field || secondaryField;
      if (!lowerField) return "";
      const x0 = Number.isFinite(Number(band.x0)) ? Number(band.x0) : xMin;
      const x1 = Number.isFinite(Number(band.x1)) ? Number(band.x1) : xMax;
      const bandRows = primaryRows.filter((row) => {
        const xv = Number(row[xField]);
        return xv >= Math.min(x0, x1) && xv <= Math.max(x0, x1) && hasFiniteValue(row[upperField]) && hasFiniteValue(row[lowerField]);
      });
      if (bandRows.length < 2) return "";
      const top = bandRows.map((row) => [x(row[xField]), y(row[upperField])]);
      const bottom = bandRows.map((row) => [x(row[xField]), y(row[lowerField])]);
      return `<path class="${escapeHtml(band.class || "band")}" d="${pathForLine(top)} ${bottom.slice().reverse().map((p) => `L${p[0].toFixed(1)},${p[1].toFixed(1)}`).join(" ")} Z"></path>`;
    }).join("");
    const areaUnderLine = instance.config.area_under_line ? (() => {
      const area = instance.config.area_under_line;
      const baseline = Number.isFinite(Number(area.baseline)) ? Number(area.baseline) : yMin;
      const baseY = y(baseline);
      return `<path class="${escapeHtml(area.class || "band")}" d="${pathForLine(pts)} L${pts[pts.length - 1][0].toFixed(1)},${baseY.toFixed(1)} L${pts[0][0].toFixed(1)},${baseY.toFixed(1)} Z"></path>`;
    })() : "";
    const signedAreaUnderLine = instance.config.signed_area_under_line ? (() => {
      const area = instance.config.signed_area_under_line;
      const baseline = Number.isFinite(Number(area.baseline)) ? Number(area.baseline) : 0;
      const baseY = y(baseline);
      const makeSegments = (predicate) => {
        const segments = [];
        let current = [];
        primaryRows.forEach((row) => {
          const value = Number(row[yField]);
          if (predicate(value)) {
            current.push([x(row[xField]), y(value)]);
          } else {
            if (current.length > 1) segments.push(current);
            current = [];
          }
        });
        if (current.length > 1) segments.push(current);
        return segments;
      };
      const areaPaths = (segments, cls) => segments.map((segment) => `<path class="${escapeHtml(cls)}" d="${path(segment)} L${segment[segment.length - 1][0].toFixed(1)},${baseY.toFixed(1)} L${segment[0][0].toFixed(1)},${baseY.toFixed(1)} Z"></path>`).join("");
      return `${areaPaths(makeSegments((value) => value >= baseline), area.positive_class || "positive-area")}${areaPaths(makeSegments((value) => value <= baseline), area.negative_class || "negative-area")}`;
    })() : "";
    const plotW = w - m.l - m.r;
    const plotH = h - m.t - m.b;
    const yTicks = ticksFor(yMin, yMax, instance.config.y_ticks, 4);
    const xTicks = ticksFor(xMin, xMax, instance.config.x_ticks, 5);
    const xLabel = instance.config.x_axis_label || xField;
    const yLabel = instance.config.y_axis_label || instance.config.label || yField;
    const verticalMarkers = (instance.config.vertical_markers || []).map((marker) => {
      const markerClass = marker.class || "marker-line";
      const opacity = marker.opacity !== undefined ? ` opacity="${Number(marker.opacity)}"` : "";
      return `<line class="${escapeHtml(markerClass)}" x1="${x(marker.x)}" x2="${x(marker.x)}" y1="${m.t}" y2="${h - m.b}"${opacity}></line>`;
    }).join("");
    const diagonalMarkers = (instance.config.diagonal_markers || []).map((marker) => {
      const markerClass = marker.class || "marker-line";
      return `<line class="${escapeHtml(markerClass)}" x1="${x(marker.x0)}" x2="${x(marker.x1)}" y1="${y(marker.y0)}" y2="${y(marker.y1)}"></line>`;
    }).join("");
    const gapMarkers = (instance.config.gap_markers || []).map((marker) => {
      const upperField = marker.upper_field || marker.top_field || yField;
      const lowerField = marker.lower_field || marker.bottom_field || secondaryField;
      const row = primaryRows.find((item) => Number(item[xField]) === Number(marker.x));
      if (!row || !lowerField || !hasFiniteValue(row[upperField]) || !hasFiniteValue(row[lowerField])) return "";
      const markerClass = marker.class || "marker-line";
      const endpointClass = marker.point_class;
      const endpointRadius = Number(marker.r ?? 4);
      const endpoints = endpointClass
        ? `<circle class="${escapeHtml(endpointClass)}" cx="${x(row[xField])}" cy="${y(row[upperField])}" r="${endpointRadius}"></circle><circle class="${escapeHtml(endpointClass)}" cx="${x(row[xField])}" cy="${y(row[lowerField])}" r="${endpointRadius}"></circle>`
        : "";
      return `<line class="${escapeHtml(markerClass)}" x1="${x(row[xField])}" x2="${x(row[xField])}" y1="${y(row[upperField])}" y2="${y(row[lowerField])}"></line>${endpoints}`;
    }).join("");
    const horizontalMarkers = (instance.config.horizontal_markers || []).map((marker) => {
      const markerClass = marker.class || "threshold";
      const x0 = hasFiniteValue(marker.x0) ? x(marker.x0) : m.l;
      const x1 = hasFiniteValue(marker.x1) ? x(marker.x1) : m.l + plotW;
      const labelX = hasFiniteValue(marker.label_x) ? x(marker.label_x) : Math.min(x0, x1);
      const opacity = marker.opacity !== undefined ? ` opacity="${Number(marker.opacity)}"` : "";
      const label = marker.label ? `<text class="${escapeHtml(marker.label_class || "axis-label")}" x="${labelX}" y="${y(marker.y) + Number(marker.label_dy ?? -8)}">${escapeHtml(marker.label)}</text>` : "";
      return `<line class="${escapeHtml(markerClass)}" x1="${x0}" x2="${x1}" y1="${y(marker.y)}" y2="${y(marker.y)}"${opacity}></line>${label}`;
    }).join("");
    const annotations = (instance.config.annotations || []).map((annotation) => {
      const annotationClass = annotation.class || "callout";
      return `<text class="${escapeHtml(annotationClass)}" x="${x(annotation.x)}" y="${y(annotation.y)}">${escapeHtml(annotation.text || "")}</text>`;
    }).join("");
    const pointHighlights = (instance.config.point_highlights || []).map((point) => {
      const field = point.field || yField;
      const row = primaryRows.find((item) => Number(item[xField]) === Number(point.x));
      if (!row || !hasFiniteValue(row[field])) return "";
      return `<circle class="${escapeHtml(point.class || "series-point")}" cx="${x(row[xField])}" cy="${y(row[field])}" r="${Number(point.r) || pointRadius}"></circle>`;
    }).join("");
    const pixelBars = (instance.config.pixel_bars || []).map((barConfig) => {
      const source = barConfig.source;
      const barRows = source ? rowsForSource(payload, source) : rows;
      const categoryField = barConfig.category_field || "label";
      const valueField = barConfig.value_field || "value";
      const x0 = Number(barConfig.x ?? 0);
      const y0 = Number(barConfig.y ?? 0);
      const max = Number(barConfig.x_max ?? Math.max(...barRows.map((row) => Number(row[valueField]) || 0), 1));
      const width = Number(barConfig.width ?? 120);
      const rowGap = Number(barConfig.row_gap ?? 24);
      const barH = Number(barConfig.bar_height ?? 14);
      const threshold = Number(barConfig.threshold ?? Number.NaN);
      const xFor = (value) => x0 + (Number(value) / (max || 1)) * width;
      const body = barRows.map((row, i) => {
        const value = Number(row[valueField]) || 0;
        const yy = y0 + i * rowGap;
        const cls = row.class || (Number.isFinite(threshold) && value > threshold ? barConfig.over_class : barConfig.bar_class) || "bar";
        const label = `<text class="${escapeHtml(barConfig.label_class || "bar-label")}" x="${x0 - Number(barConfig.label_dx ?? 14)}" y="${yy + barH - 2}" text-anchor="end">${escapeHtml(row[categoryField] || "")}</text>`;
        const valueText = barConfig.show_values === false ? "" : `<text class="${escapeHtml(barConfig.value_label_class || "axis-tick")}" x="${xFor(value) + Number(barConfig.value_label_dx ?? 7)}" y="${yy + barH - 2}">${escapeHtml(row.displayValue ?? row.display_value ?? formatNumber(value))}</text>`;
        return `${label}<rect class="${escapeHtml(cls)}" x="${x0}" y="${yy}" width="${Math.max(0, xFor(value) - x0)}" height="${barH}" rx="${Number(barConfig.radius ?? 3)}"></rect>${valueText}`;
      }).join("");
      const caption = barConfig.caption ? `<text class="${escapeHtml(barConfig.caption_class || "axis-label")}" x="${Number(barConfig.caption_x ?? (x0 + width / 2))}" y="${Number(barConfig.caption_y ?? (h - 8))}" text-anchor="middle">${escapeHtml(barConfig.caption)}</text>` : "";
      return `${body}${caption}`;
    }).join("");
    const axisLabelX = Number(instance.config.axis_label_x ?? (m.l + plotW / 2));
    const axisLabelY = Number(instance.config.axis_label_y ?? (h - 12));
    const xAxisY = hasFiniteValue(instance.config.x_axis_y) ? y(instance.config.x_axis_y) : h - m.b;
    return svg(`${backgroundRegions}
      ${yTicks.map((tick) => `<line class="grid-line" x1="${m.l}" x2="${m.l + plotW}" y1="${y(tick)}" y2="${y(tick)}"></line>`).join("")}
      ${horizontalMarkers}
      ${fillBetween}
      ${areaUnderLine}
      ${signedAreaUnderLine}
      ${diagonalMarkers}
      ${instance.config.show_line === false ? "" : `<path class="${escapeHtml(primaryLineClass)}" d="${pathForLine(pts)}"></path>`}
      ${secondary}
      ${primaryDots}
      ${secondaryDots}
      ${verticalMarkers}
      ${gapMarkers}
      ${pointHighlights}
      ${pixelBars}
      <line class="axis-line" x1="${m.l}" x2="${m.l + plotW}" y1="${xAxisY}" y2="${xAxisY}"></line>
      <line class="axis-line" x1="${m.l}" x2="${m.l}" y1="${m.t}" y2="${h - m.b}"></line>
      ${yTicks.map((tick) => `<text class="axis-tick" x="${m.l - 12}" y="${y(tick) + 4}" text-anchor="end">${formatByMode(tick, instance.config.y_tick_format)}</text>`).join("")}
      ${xTicks.map((tick) => `<text class="axis-tick" x="${x(tick)}" y="${h - m.b + 24}" text-anchor="middle">${formatByMode(tick, instance.config.x_tick_format)}${escapeHtml(instance.config.x_tick_suffix || "")}</text>`).join("")}
      <text class="axis-label" x="${axisLabelX}" y="${axisLabelY}" text-anchor="middle">${escapeHtml(xLabel)}</text>
      ${instance.config.y_axis_label === false ? "" : `<text class="axis-label" x="16" y="${m.t + plotH / 2}" text-anchor="middle" transform="rotate(-90 16 ${m.t + plotH / 2})">${escapeHtml(yLabel)}</text>`}
      ${annotations}`, `0 0 ${w} ${h}`);
  }

  return Object.freeze({
    renderLine
  });
}

if (typeof module !== "undefined") {
  module.exports = { createLineRenderers };
}
