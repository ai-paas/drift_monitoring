/*
 * Source candidate for medium-size renderers.
 *
 * This file is not imported by chart_runtime.js yet. Until a build step is
 * introduced, chart_runtime.js remains the browser artifact and source of truth.
 */

function createMatrixRenderers(deps) {
  const {
    classForValue,
    dataFor,
    escapeHtml,
    formatByMode,
    formatNumber,
    hasFiniteValue,
    heatmapColor,
    marginFor,
    svg,
    viewBoxFor
  } = deps;
  function renderMatrix(payload, instance) {
    const rows = dataFor(payload, instance);
    const xField = instance.config.x_field || instance.config.column_field || "column";
    const yField = instance.config.y_field || instance.config.row_field || "row";
    const valueField = instance.config.value_field || instance.config.cell_value_field || "value";
    if (instance.config.matrix_style === "heatmap_grid") {
      const valuesField = instance.config.values_field || "values";
      const rowValueRows = rows.filter((row) => Array.isArray(row[valuesField]));
      const xValues = Array.isArray(instance.config.x_values)
        ? instance.config.x_values
        : [...new Set(rows.map((row) => row[xField]))];
      const yValues = Array.isArray(instance.config.y_values)
        ? instance.config.y_values
        : (rowValueRows.length ? rowValueRows.map((row) => row[yField]) : [...new Set(rows.map((row) => row[yField]))]);
      const { w, h } = viewBoxFor(instance.config, 472, 185);
      const m = marginFor(instance.config, { t: 18, r: 24, b: 38, l: 48 });
      const plotW = w - m.l - m.r;
      const plotH = h - m.t - m.b;
      const cellW = plotW / Math.max(1, xValues.length);
      const cellH = plotH / Math.max(1, yValues.length);
      const xIndex = (value) => xValues.findIndex((item) => String(item) === String(value));
      const xCenter = (value) => {
        const index = xIndex(value);
        if (index >= 0) return m.l + (index + 0.5) * cellW;
        const xMin = Number(instance.config.x_min ?? xValues[0] ?? 0);
        const xMax = Number(instance.config.x_max ?? xValues[xValues.length - 1] ?? 1);
        return m.l + ((Number(value) - xMin) / (xMax - xMin || 1)) * plotW;
      };
      const yPosition = (value) => {
        const yMin = Number(instance.config.y_min ?? 0);
        const yMax = Number(instance.config.y_max ?? 1);
        return m.t + (1 - ((Number(value) - yMin) / (yMax - yMin || 1))) * plotH;
      };
      const rowMap = new Map(rows.map((row) => [`${row[xField]}::${row[yField]}`, row]));
      const cells = yValues.map((yy, r) => xValues.map((xx, c) => {
        const value = rowValueRows.length
          ? rowValueRows[r]?.[valuesField]?.[c]
          : rowMap.get(`${xx}::${yy}`)?.[valueField];
        return `<rect class="${escapeHtml(instance.config.cell_class || "cell")}" x="${m.l + c * cellW}" y="${m.t + r * cellH}" width="${cellW}" height="${cellH}" fill="${heatmapColor(value ?? 0, instance.config)}"></rect>`;
      }).join("")).join("");
      const rowHighlights = (instance.config.row_highlights || []).map((highlight) => {
        const index = yValues.findIndex((value) => String(value) === String(highlight.row));
        if (index < 0) return "";
        return `<rect class="${escapeHtml(highlight.class || "layer-ring")}" x="${m.l}" y="${m.t + index * cellH}" width="${plotW}" height="${cellH}" rx="${Number(highlight.rx ?? 3)}"></rect>`;
      }).join("");
      const cellValueLabels = instance.config.show_cell_values ? yValues.map((yy, r) => xValues.map((xx, c) => {
        const value = rowValueRows.length
          ? rowValueRows[r]?.[valuesField]?.[c]
          : rowMap.get(`${xx}::${yy}`)?.[valueField];
        if (!hasFiniteValue(value)) return "";
        const minValue = Number(instance.config.cell_value_min ?? -Infinity);
        if (Number(value) < minValue) return "";
        return `<text class="${escapeHtml(instance.config.cell_value_class || "bar-label")}" x="${m.l + (c + 0.5) * cellW}" y="${m.t + (r + 0.5) * cellH + Number(instance.config.cell_value_dy ?? 4)}" text-anchor="middle">${formatByMode(Number(value), instance.config.cell_value_format)}</text>`;
      }).join("")).join("") : "";
      const xLabels = instance.config.show_x_labels ? xValues.map((xx, i) => {
        const labels = instance.config.x_labels || [];
        const label = labels[i] ?? xx;
        return `<text class="${escapeHtml(instance.config.x_label_class || "axis-tick")}" x="${m.l + (i + 0.5) * cellW}" y="${Number(instance.config.x_label_y ?? (h - m.b + 18))}" text-anchor="middle">${escapeHtml(label)}</text>`;
      }).join("") : "";
      const yLabels = instance.config.show_y_labels ? yValues.map((yy, i) => {
        const labels = instance.config.y_labels || [];
        const label = labels[i] ?? yy;
        return `<text class="${escapeHtml(instance.config.y_label_class || "bar-label")}" x="${Number(instance.config.y_label_x ?? (m.l - 10))}" y="${m.t + (i + 0.5) * cellH + Number(instance.config.y_label_dy ?? 5)}" text-anchor="end">${escapeHtml(label)}</text>`;
      }).join("") : "";
      const xTicks = Array.isArray(instance.config.x_ticks) ? instance.config.x_ticks : [];
      const yTicks = Array.isArray(instance.config.y_ticks) ? instance.config.y_ticks : [];
      const verticalMarkers = (instance.config.vertical_markers || []).map((marker) => {
        const opacity = marker.opacity !== undefined ? ` opacity="${Number(marker.opacity)}"` : "";
        return `<line class="${escapeHtml(marker.class || "marker-line")}" x1="${xCenter(marker.x)}" x2="${xCenter(marker.x)}" y1="${m.t}" y2="${h - m.b}"${opacity}></line>`;
      }).join("");
      const ellipses = (instance.config.ellipses || []).map((ellipseConfig) => {
        const cx = xCenter(ellipseConfig.x);
        const cy = yPosition(ellipseConfig.y);
        const rx = Number(ellipseConfig.rx ?? 20);
        const ry = Number(ellipseConfig.ry ?? 12);
        const rotate = Number(ellipseConfig.rotate ?? 0);
        const transform = rotate ? ` transform="rotate(${rotate} ${cx} ${cy})"` : "";
        return `<ellipse class="${escapeHtml(ellipseConfig.class || "scatter-ellipse")}" cx="${cx}" cy="${cy}" rx="${rx}" ry="${ry}"${transform}></ellipse>`;
      }).join("");
      const annotations = (instance.config.annotations || []).map((annotation) => {
        const annotationClass = annotation.class || "callout";
        const yValue = annotation.y ?? 0.5;
        return `<text class="${escapeHtml(annotationClass)}" x="${xCenter(annotation.x)}" y="${yPosition(yValue)}">${escapeHtml(annotation.text || "")}</text>`;
      }).join("");
      const axisX = `<line class="axis-line" x1="${m.l}" x2="${m.l + plotW}" y1="${h - m.b}" y2="${h - m.b}"></line>`;
      const axisY = instance.config.show_y_axis === false ? "" : `<line class="axis-line" x1="${m.l}" x2="${m.l}" y1="${m.t}" y2="${h - m.b}"></line>`;
      const xAxisLabel = instance.config.x_axis_label ? `<text class="axis-label" x="${Number(instance.config.axis_label_x ?? (m.l + plotW / 2))}" y="${Number(instance.config.axis_label_y ?? (h - 12))}" text-anchor="middle">${escapeHtml(instance.config.x_axis_label)}</text>` : "";
      const yAxisLabel = instance.config.y_axis_label ? `<text class="axis-label" x="${Number(instance.config.y_axis_label_x ?? 16)}" y="${Number(instance.config.y_axis_label_y ?? (m.t + plotH / 2))}" text-anchor="middle" transform="rotate(-90 ${Number(instance.config.y_axis_label_x ?? 16)} ${Number(instance.config.y_axis_label_y ?? (m.t + plotH / 2))})">${escapeHtml(instance.config.y_axis_label)}</text>` : "";
      const caption = instance.config.caption ? `<text class="axis-label" x="${Number(instance.config.caption_x ?? (m.l + plotW / 2))}" y="${Number(instance.config.caption_y ?? (h - 8))}" text-anchor="middle">${escapeHtml(instance.config.caption)}</text>` : "";
      return svg(`${cells}${rowHighlights}${cellValueLabels}${ellipses}${yLabels}${xLabels}${verticalMarkers}${axisX}${axisY}
        ${xTicks.map((tick) => `<text class="axis-tick" x="${xCenter(tick)}" y="${h - m.b + 24}" text-anchor="middle">${formatNumber(tick)}</text>`).join("")}
        ${yTicks.map((tick) => `<text class="axis-tick" x="${m.l - 12}" y="${yPosition(tick) + 4}" text-anchor="end">${formatNumber(tick)}</text>`).join("")}
        ${xAxisLabel}${yAxisLabel}${caption}${annotations}`, `0 0 ${w} ${h}`);
    }
    if (instance.config.matrix_style === "category_cells") {
      const categoryField = instance.config.category_field || xField || "category";
      const { w, h } = viewBoxFor(instance.config, 472, 185);
      const m = marginFor(instance.config, { t: 12, r: 22, b: 28, l: 76 });
      const cellW = Number(instance.config.cell_width || ((w - m.l - m.r) / Math.max(1, rows.length)));
      const cellH = Number(instance.config.cell_height || 48);
      const startX = Number(instance.config.start_x ?? m.l);
      const startY = Number(instance.config.start_y ?? 48);
      const rules = instance.config.class_rules || [];
      const cells = rows.map((row, i) => {
        const x0 = startX + i * cellW + Number(instance.config.cell_gap ?? 3);
        const value = Number(row[valueField]) || 0;
        const cls = row.class || classForValue(value, rules, instance.config.cell_class || "cell");
        const width = cellW - Number(instance.config.cell_gap ?? 3) * 2;
        return `<rect class="${escapeHtml(cls)}" x="${x0}" y="${startY}" width="${width}" height="${cellH}" rx="${Number(instance.config.cell_radius ?? 6)}"></rect>
          <text class="bar-label" x="${x0 + width / 2}" y="${startY + Number(instance.config.value_text_y ?? 29)}" text-anchor="middle">${formatNumber(value)}</text>
          <text class="axis-tick" x="${x0 + width / 2}" y="${startY + cellH + Number(instance.config.category_text_y ?? 22)}" text-anchor="middle">${escapeHtml(row[categoryField])}</text>`;
      }).join("");
      const labels = (instance.config.labels || []).map((label) => `<text class="${escapeHtml(label.class || "axis-tick")}" x="${Number(label.x)}" y="${Number(label.y)}">${escapeHtml(label.text || "")}</text>`).join("");
      const caption = instance.config.caption ? `<text class="axis-label" x="${Number(instance.config.caption_x ?? startX)}" y="${Number(instance.config.caption_y ?? (h - 35))}">${escapeHtml(instance.config.caption)}</text>` : "";
      return svg(`${labels}${cells}${caption}`, `0 0 ${w} ${h}`);
    }
    if (instance.config.matrix_style === "mosaic_2x2") {
      const labelField = instance.config.label_field || "label";
      const eventField = instance.config.event_field || "event";
      const noneventField = instance.config.nonevent_field || "nonevent";
      let { w, h } = viewBoxFor(instance.config, 630, 440);
      const m = marginFor(instance.config, { t: 32, r: 36, b: 52, l: 70 });
      const plotW = w - m.l - m.r;
      const rowGap = Number(instance.config.row_gap || 28);
      const configuredRowH = Number(instance.config.row_height);
      const rowH = Number.isFinite(configuredRowH) && configuredRowH > 0
        ? configuredRowH
        : Math.max(28, (h - m.t - m.b - rowGap * Math.max(0, rows.length - 1)) / Math.max(1, rows.length));
      h = Math.max(h, Math.ceil(m.t + m.b + rows.length * rowH + rowGap * Math.max(0, rows.length - 1)));
      const eventTitle = instance.config.event_title ? `<text class="title-text" x="${m.l + 18}" y="${m.t - 11}">${escapeHtml(instance.config.event_title)}</text>` : "";
      const noneventTitle = instance.config.nonevent_title ? `<text class="title-text" x="${m.l + plotW - 18}" y="${m.t - 11}" text-anchor="end">${escapeHtml(instance.config.nonevent_title)}</text>` : "";
      const currentLabel = instance.config.current_label;
      const body = rows.map((row, i) => {
        const y0 = m.t + i * (rowH + rowGap);
        const event = Number(row[eventField]) || 0;
        const nonevent = Number(row[noneventField]) || 0;
        const total = event + nonevent || 1;
        const eventW = plotW * event / total;
        const noneventW = plotW - eventW;
        const eventRate = event / total;
        const label = row[labelField] || "";
        const outline = currentLabel !== undefined && String(label) === String(currentLabel)
          ? `<rect class="${escapeHtml(instance.config.current_outline_class || "current-outline")}" x="${m.l - 2}" y="${y0 - 2}" width="${plotW + 4}" height="${rowH + 4}" rx="8"></rect>`
          : "";
        return `<text class="title-text" x="${m.l - 14}" y="${y0 + rowH / 2 + 5}" text-anchor="end">${escapeHtml(label)}  n=${total}</text>
          <rect class="${escapeHtml(instance.config.event_class || "event-fill")}" x="${m.l}" y="${y0}" width="${eventW}" height="${rowH}" rx="7"></rect>
          <rect class="${escapeHtml(instance.config.nonevent_class || "nonevent-fill")}" x="${m.l + eventW}" y="${y0}" width="${noneventW}" height="${rowH}" rx="7"></rect>
          ${outline}
          <text class="cell-label" x="${m.l + eventW / 2}" y="${y0 + rowH / 2 - 3}" text-anchor="middle">${event}${escapeHtml(instance.config.count_suffix || "")}</text>
          <text class="cell-label" x="${m.l + eventW / 2}" y="${y0 + rowH / 2 + 17}" text-anchor="middle">${(eventRate * 100).toFixed(1)}%</text>
          <text class="cell-label dark" x="${m.l + eventW + noneventW / 2}" y="${y0 + rowH / 2 - 3}" text-anchor="middle">${nonevent}${escapeHtml(instance.config.count_suffix || "")}</text>
          <text class="cell-label dark" x="${m.l + eventW + noneventW / 2}" y="${y0 + rowH / 2 + 17}" text-anchor="middle">${((1 - eventRate) * 100).toFixed(1)}%</text>`;
      }).join("");
      const caption = instance.config.caption ? `<text class="callout" x="${Number(instance.config.caption_x ?? (m.l + plotW / 2))}" y="${Number(instance.config.caption_y ?? (h - 18))}" text-anchor="middle">${escapeHtml(instance.config.caption)}</text>` : "";
      return svg(`${eventTitle}${noneventTitle}${body}${caption}`, `0 0 ${w} ${h}`);
    }
    const xs = [...new Set(rows.map((row) => row[xField]))].slice(0, 6);
    const ys = [...new Set(rows.map((row) => row[yField]))].slice(0, 6);
    if (instance.config.matrix_style === "direction_dots") {
      const { w, h } = viewBoxFor(instance.config, 472, 185);
      const startX = Number(instance.config.start_x || 116);
      const startY = Number(instance.config.start_y || 38);
      const cellW = Number(instance.config.cell_width || 82);
      const cellH = Number(instance.config.cell_height || 24);
      const header = xs.map((xx, i) => `<rect class="matrix-head" x="${startX + i * cellW}" y="12" width="${cellW - 4}" height="22" rx="4"></rect><text class="axis-tick" x="${startX + i * cellW + (cellW - 4) / 2}" y="27" text-anchor="middle">${escapeHtml(xx)}</text>`).join("");
      const body = ys.map((yy, r) => {
        const yyPos = startY + r * cellH;
        const cells = xs.map((xx, c) => {
          const item = rows.find((row) => row[xField] === xx && row[yField] === yy);
          const active = item ? Boolean(item[valueField]) : false;
          return `<circle class="${active ? "matrix-on" : "matrix-off"}" cx="${startX + c * cellW + (cellW - 4) / 2}" cy="${yyPos + 12}" r="${active ? 7 : 5}"></circle>`;
        }).join("");
        return `<text class="bar-label" x="${startX - 22}" y="${yyPos + 16}" text-anchor="end">${escapeHtml(yy)}</text>${cells}`;
      }).join("");
      const caption = instance.config.caption ? `<text class="axis-label" x="${w / 2}" y="${h - 15}" text-anchor="middle">${escapeHtml(instance.config.caption)}</text>` : "";
      return svg(`${header}${body}${caption}`, `0 0 ${w} ${h}`);
    }
    return svg(ys.map((yy, r) => xs.map((xx, c) => {
      const item = rows.find((row) => row[xField] === xx && row[yField] === yy);
      const value = item ? Number(item[valueField]) || 0 : 0;
      const color = `rgba(47,111,159,${0.18 + Math.min(0.75, Math.abs(value))})`;
      return `<rect class="cell" x="${78 + c * 40}" y="${24 + r * 26}" width="36" height="22" rx="4" fill="${color}"></rect>`;
    }).join("")).join(""));
  }

  return Object.freeze({
    renderMatrix
  });
}

if (typeof module !== "undefined") {
  module.exports = { createMatrixRenderers };
}
