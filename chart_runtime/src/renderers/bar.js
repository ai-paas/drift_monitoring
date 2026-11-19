/*
 * Source candidate for high-traffic line/bar renderers.
 *
 * This file is not imported by chart_runtime.js yet. Until a build step is
 * introduced, chart_runtime.js remains the browser artifact and source of truth.
 */

function createBarRenderers(deps) {
  const {
    dataFor,
    escapeHtml,
    formatByMode,
    formatNumber,
    hasFiniteValue,
    marginFor,
    renderCard,
    svg,
    ticksFor,
    viewBoxFor
  } = deps;

  function renderBar(payload, instance) {
    const rows = dataFor(payload, instance);
    if (instance.config.bar_style === "horizontal_intervals") {
      const categoryField = instance.config.category_field || "label";
      const valueField = instance.config.value_field || "value";
      const lowField = instance.config.low_field || "low";
      const highField = instance.config.high_field || "high";
      const classField = instance.config.class_field || "class";
      const valueLabelField = instance.config.value_label_field || "valueLabel";
      const validRows = rows.filter((row) => hasFiniteValue(row[valueField]) && hasFiniteValue(row[lowField]) && hasFiniteValue(row[highField]));
      if (!validRows.length) return renderCard(payload, instance);
      const { w, h } = viewBoxFor(instance.config, 472, 185);
      const m = marginFor(instance.config, { t: 16, r: 30, b: 38, l: 50 });
      const xMin = Number.isFinite(Number(instance.config.x_min)) ? Number(instance.config.x_min) : Math.min(...validRows.map((row) => Number(row[lowField])));
      const xMax = Number.isFinite(Number(instance.config.x_max)) ? Number(instance.config.x_max) : Math.max(...validRows.map((row) => Number(row[highField])));
      const x = (value) => m.l + ((Number(value) - xMin) / (xMax - xMin || 1)) * (w - m.l - m.r);
      const ticks = ticksFor(xMin, xMax, instance.config.x_ticks, 4);
      const grid = ticks.map((tick) => `<line class="grid-line" x1="${x(tick)}" x2="${x(tick)}" y1="${m.t}" y2="${h - m.b}"></line><text class="axis-tick" x="${x(tick)}" y="${h - 16}" text-anchor="middle">${formatByMode(tick, instance.config.x_tick_format)}</text>`).join("");
      const rowGap = Number(instance.config.row_gap || 50);
      const firstY = Number(instance.config.first_y || 62);
      const pointClass = instance.config.point_class || "mean-point";
      const intervals = validRows.map((row, i) => {
        const y0 = Number(row.y ?? (firstY + i * rowGap));
        const cls = row[classField] || instance.config.interval_class || "ci-line";
        const label = valueLabelField && row[valueLabelField] !== undefined
          ? row[valueLabelField]
          : `${formatNumber(row[valueField])} [${formatNumber(row[lowField])}, ${formatNumber(row[highField])}]`;
        return `<text class="${escapeHtml(instance.config.category_label_class || "title-text")}" x="${m.l - 12}" y="${y0 + 4}" text-anchor="end">${escapeHtml(row[categoryField])}</text>
          <line class="${escapeHtml(cls)}" x1="${x(row[lowField])}" x2="${x(row[highField])}" y1="${y0}" y2="${y0}"></line>
          <circle class="${escapeHtml(row.point_class || pointClass)}" cx="${x(row[valueField])}" cy="${y0}" r="${Number(row.r ?? instance.config.point_radius ?? 7)}"></circle>
          <text class="${escapeHtml(instance.config.value_label_class || "bar-label")}" x="${x(row[valueField])}" y="${y0 + Number(instance.config.value_label_dy ?? -15)}" text-anchor="middle">${escapeHtml(label)}</text>`;
      }).join("");
      const axisLabel = instance.config.x_axis_label ? `<text class="axis-label" x="${Number(instance.config.axis_label_x ?? (m.l + (w - m.l - m.r) / 2))}" y="${Number(instance.config.axis_label_y ?? (h - 4))}" text-anchor="middle">${escapeHtml(instance.config.x_axis_label)}</text>` : "";
      const annotations = (instance.config.annotations || []).map((annotation) => `<text class="${escapeHtml(annotation.class || "axis-label")}" x="${Number(annotation.x)}" y="${Number(annotation.y)}">${escapeHtml(annotation.text || "")}</text>`).join("");
      return svg(`${grid}${intervals}<line class="axis-line" x1="${m.l}" x2="${w - m.r}" y1="${h - m.b}" y2="${h - m.b}"></line>${axisLabel}${annotations}`, `0 0 ${w} ${h}`);
    }
    if (instance.config.bar_style === "vertical_grouped") {
      const categoryField = instance.config.category_field || "category";
      const series = instance.config.series_fields || ["expected", "observed"];
      const classes = instance.config.series_classes || [];
      let { w, h } = viewBoxFor(instance.config, 630, 440);
      const m = marginFor(instance.config, { t: 20, r: 22, b: 58, l: 62 });
      const minSlotW = Number(instance.config.min_slot_width ?? 58);
      w = Math.max(w, Math.ceil(m.l + m.r + rows.length * minSlotW));
      const plotW = w - m.l - m.r;
      const plotH = h - m.t - m.b;
      const maxValue = Number(instance.config.y_max) || Math.max(...rows.flatMap((row) => series.map((field) => Number(row[field]) || 0)), 1);
      const yMax = Number(instance.config.y_tick_max) || maxValue;
      const y = (value) => m.t + (1 - (Number(value) / (yMax || 1))) * plotH;
      const slotW = plotW / Math.max(1, rows.length);
      const groupPad = Number(instance.config.group_padding ?? 12);
      const barGap = Number(instance.config.bar_gap ?? 5);
      const barW = Number(instance.config.bar_width ?? ((slotW - groupPad * 2 - barGap * (series.length - 1)) / Math.max(1, series.length)));
      const yTicks = ticksFor(0, yMax, instance.config.y_ticks, 5);
      const grid = yTicks.map((tick) => `<line class="grid-line" x1="${m.l}" x2="${m.l + plotW}" y1="${y(tick)}" y2="${y(tick)}"></line><text class="axis-tick" x="${m.l - 12}" y="${y(tick) + 4}" text-anchor="end">${formatByMode(tick, instance.config.y_tick_format)}</text>`).join("");
      const xValueMin = Number.isFinite(Number(instance.config.x_min)) ? Number(instance.config.x_min) : 0;
      const xValueMax = Number.isFinite(Number(instance.config.x_max)) ? Number(instance.config.x_max) : Math.max(1, rows.length);
      const xValue = (value) => m.l + ((Number(value) - xValueMin) / (xValueMax - xValueMin || 1)) * plotW;
      const xValueTicks = (instance.config.x_value_ticks || []).map((tick) => {
        const value = typeof tick === "object" ? tick.value : tick;
        const label = typeof tick === "object" && tick.label !== undefined ? tick.label : formatNumber(value);
        const xx = xValue(value);
        return `<line class="grid-line" x1="${xx}" x2="${xx}" y1="${m.t}" y2="${h - m.b}"></line><text class="axis-tick" x="${xx}" y="${h - m.b + Number(instance.config.x_value_tick_dy ?? 24)}" text-anchor="middle">${escapeHtml(label)}</text>`;
      }).join("");
      const categoryHighlights = Array.isArray(instance.config.category_highlights) ? instance.config.category_highlights : [];
      const classFields = instance.config.series_class_fields || [];
      const valueLabelFields = instance.config.value_label_fields || [];
      const bars = rows.map((row, i) => {
        const groupLeft = m.l + i * slotW + groupPad;
        const highlight = categoryHighlights.filter((item) => String(item.category) === String(row[categoryField]) || Number(item.index) === i).map((item) => {
          const x0 = m.l + i * slotW + Number(item.dx ?? 4);
          const width = slotW - Number(item.dx ?? 4) * 2;
          return `<rect class="${escapeHtml(item.class || "highlight-band")}" x="${x0}" y="${Number(item.y ?? m.t)}" width="${width}" height="${Number(item.height ?? plotH)}" rx="${Number(item.rx ?? 8)}"></rect>`;
        }).join("");
        const body = series.map((field, s) => {
          const value = Number(row[field]) || 0;
          const x0 = groupLeft + s * (barW + barGap);
          const barClass = classFields[s] && row[classFields[s]] ? row[classFields[s]] : classes[s] || "bar";
          const labelField = valueLabelFields[s];
          const valueLabel = labelField && row[labelField] !== undefined ? row[labelField] : formatNumber(value);
          const valueText = instance.config.show_value_labels ? `<text class="${escapeHtml(instance.config.value_label_class || "title-text")}" x="${x0 + barW / 2}" y="${y(value) + Number(instance.config.value_label_dy ?? -8)}" text-anchor="middle">${escapeHtml(valueLabel)}</text>` : "";
          return `<rect class="${escapeHtml(barClass)}" x="${x0}" y="${y(value)}" width="${barW}" height="${h - m.b - y(value)}" rx="${Number(instance.config.bar_radius ?? 3)}"></rect>${valueText}`;
        }).join("");
        const labelX = groupLeft + ((barW * series.length) + (barGap * (series.length - 1))) / 2;
        const subLabel = instance.config.category_sub_label_field && row[instance.config.category_sub_label_field] !== undefined
          ? `<text class="axis-tick" x="${labelX}" y="${h - m.b + Number(instance.config.category_sub_label_y ?? -8)}" text-anchor="middle">${escapeHtml(row[instance.config.category_sub_label_field])}</text>`
          : "";
        const showCategory = !instance.config.hide_category_labels && (!instance.config.label_every || i % Number(instance.config.label_every) === 0);
        const categoryLabel = showCategory ? `<text class="axis-tick" x="${labelX}" y="${h - m.b + 24}" text-anchor="middle">${escapeHtml(row[categoryField])}</text>` : "";
        return `${highlight}${body}${subLabel}${categoryLabel}`;
      }).join("");
      const renderOverlayBars = (order) => (instance.config.overlay_bars || [])
        .filter((overlay) => (overlay.render_order || "after_bars") === order)
        .map((overlay) => rows.map((row, i) => {
        const valueField = overlay.value_field || overlay.field;
        if (!valueField || !hasFiniteValue(row[valueField])) return "";
        const groupLeft = m.l + i * slotW + groupPad;
        const baseX = groupLeft + Number(overlay.x_offset_bar_width ?? 0) * barW + Number(overlay.x_offset ?? 0);
        const width = Number(overlay.width_bar_width ?? 1) * barW + Number(overlay.width_adjust ?? 0);
        const value = Number(row[valueField]) || 0;
        return `<rect class="${escapeHtml(overlay.class || "overlap-bar")}" x="${baseX}" y="${y(value)}" width="${width}" height="${h - m.b - y(value)}" rx="${Number(overlay.radius ?? instance.config.bar_radius ?? 3)}"></rect>`;
      }).join("")).join("");
      const backgroundOverlayBars = renderOverlayBars("before_bars");
      const foregroundOverlayBars = renderOverlayBars("after_bars");
      const gapLines = (instance.config.gap_lines || []).map((gap) => rows.map((row, i) => {
        const fromField = gap.from_field || series[0];
        const toField = gap.to_field || series[1];
        if (!hasFiniteValue(row[fromField]) || !hasFiniteValue(row[toField])) return "";
        const diff = Math.abs(Number(row[toField]) - Number(row[fromField]));
        if (hasFiniteValue(gap.min) && diff < Number(gap.min)) return "";
        if (gap.positive_only && !(Number(row[toField]) > Number(row[fromField]))) return "";
        const groupLeft = m.l + i * slotW + groupPad;
        const fromIndex = Math.max(0, series.indexOf(fromField));
        const toIndex = Math.max(0, series.indexOf(toField));
        const x0 = groupLeft + fromIndex * (barW + barGap) + barW / 2;
        const x1 = groupLeft + toIndex * (barW + barGap) + barW / 2;
        return `<line class="${escapeHtml(gap.class || "contrib-line")}" x1="${x0}" x2="${x1}" y1="${y(row[fromField])}" y2="${y(row[toField])}"></line>`;
      }).join("")).join("");
      const overlayLines = (instance.config.overlay_lines || []).map((line) => {
        const field = line.value_field || line.field || "value";
        const points = rows.map((row, i) => {
          if (!hasFiniteValue(row[field])) return null;
          const groupLeft = m.l + i * slotW + groupPad;
          const labelX = groupLeft + ((barW * series.length) + (barGap * (series.length - 1))) / 2;
          return [labelX, y(row[field])];
        }).filter(Boolean);
        if (points.length < 2) return "";
        const pointClass = line.point_class;
        const radius = Number(line.point_radius ?? 0);
        const dots = pointClass && radius > 0
          ? points.map(([cx, cy]) => `<circle class="${escapeHtml(pointClass)}" cx="${cx}" cy="${cy}" r="${radius}"></circle>`).join("")
          : "";
        return `<path class="${escapeHtml(line.class || "trend-line")}" d="${path(points)}"></path>${dots}`;
      }).join("");
      const annotations = (instance.config.annotations || []).map((annotation) => `<text class="${escapeHtml(annotation.class || "axis-label")}" x="${annotation.x}" y="${annotation.y}">${escapeHtml(annotation.text || "")}</text>`).join("");
      const xAxisLabel = instance.config.x_axis_label ? `<text class="axis-label" x="${Number(instance.config.axis_label_x ?? (m.l + plotW / 2))}" y="${Number(instance.config.axis_label_y ?? (h - 12))}" text-anchor="middle">${escapeHtml(instance.config.x_axis_label)}</text>` : "";
      const yAxisLabel = instance.config.y_axis_label ? `<text class="axis-label" x="${Number(instance.config.y_axis_label_x ?? 16)}" y="${Number(instance.config.y_axis_label_y ?? (m.t + plotH / 2))}" text-anchor="middle" transform="rotate(-90 ${Number(instance.config.y_axis_label_x ?? 16)} ${Number(instance.config.y_axis_label_y ?? (m.t + plotH / 2))})">${escapeHtml(instance.config.y_axis_label)}</text>` : "";
      return svg(`${grid}${xValueTicks}${backgroundOverlayBars}${bars}${foregroundOverlayBars}${gapLines}${overlayLines}
        <line class="axis-line" x1="${m.l}" x2="${m.l + plotW}" y1="${h - m.b}" y2="${h - m.b}"></line>
        <line class="axis-line" x1="${m.l}" x2="${m.l}" y1="${m.t}" y2="${h - m.b}"></line>
        ${xAxisLabel}${yAxisLabel}${annotations}`, `0 0 ${w} ${h}`);
    }
    if (instance.config.bar_style === "horizontal_ranked") {
      const categoryField = instance.config.category_field || "category";
      const valueField = instance.config.value_field || "value";
      const { w, h } = viewBoxFor(instance.config, 472, 185);
      const m = marginFor(instance.config, { t: 8, r: 22, b: 28, l: 84 });
      const limit = Number(instance.config.limit || rows.length);
      const sorted = (instance.config.preserve_order
        ? rows.slice()
        : rows.slice().sort((a, b) => Number(b[valueField] || 0) - Number(a[valueField] || 0))
      ).slice(0, limit);
      const maxValue = Number(instance.config.x_max) || Math.max(...sorted.map((row) => Number(row[valueField]) || 0), 1);
      const x = (value) => m.l + (Number(value) / (maxValue || 1)) * (w - m.l - m.r);
      const rowGap = Number(instance.config.row_gap || 27);
      const firstY = Number(instance.config.first_y || 18);
      const barH = Number(instance.config.bar_height || 16);
      const bars = sorted.map((row, i) => {
        const y0 = firstY + i * rowGap;
        const value = Number(row[valueField]) || 0;
        const cls = row.class || (i === 0 ? instance.config.highlight_class : instance.config.bar_class) || "bar";
        const valueLabelField = instance.config.value_label_field || instance.config.display_value_field;
        const valueLabel = valueLabelField && row[valueLabelField] !== undefined ? row[valueLabelField] : formatNumber(value);
        const rowBg = instance.config.row_background_class
          ? `<rect class="${escapeHtml(instance.config.row_background_class)}" x="${m.l}" y="${y0}" width="${w - m.l - m.r}" height="${barH}" rx="${Number(instance.config.row_background_radius ?? instance.config.bar_radius ?? 4)}"></rect>`
          : "";
        return `<text class="axis-tick" x="${m.l - 10}" y="${y0 + barH - 4}" text-anchor="end">${escapeHtml(row[categoryField])}</text>${rowBg}<rect class="${escapeHtml(cls)}" x="${m.l}" y="${y0}" width="${Math.max(0, x(value) - m.l)}" height="${barH}" rx="${Number(instance.config.bar_radius ?? 4)}"></rect><text class="bar-label" x="${x(value) + 7}" y="${y0 + barH - 4}">${escapeHtml(valueLabel)}</text>`;
      }).join("");
      const caption = instance.config.caption ? `<text class="axis-label" x="${m.l + (w - m.l - m.r) / 2}" y="${h - 6}" text-anchor="middle">${escapeHtml(instance.config.caption)}</text>` : "";
      const annotations = (instance.config.annotations || []).map((annotation) => `<text class="${escapeHtml(annotation.class || "axis-label")}" x="${annotation.x}" y="${annotation.y}">${escapeHtml(annotation.text || "")}</text>`).join("");
      return svg(`${bars}<line class="axis-line" x1="${m.l}" x2="${w - m.r}" y1="${h - m.b}" y2="${h - m.b}"></line>${caption}${annotations}`, `0 0 ${w} ${h}`);
    }
    if (instance.config.bar_style === "horizontal_diverging") {
      const categoryField = instance.config.category_field || "category";
      const valueField = instance.config.value_field || "value";
      const valueLabelField = instance.config.value_label_field || instance.config.display_value_field;
      const { w, h } = viewBoxFor(instance.config, 472, 185);
      const m = marginFor(instance.config, { t: 8, r: 24, b: 28, l: 98 });
      const maxAbs = Number(instance.config.x_abs_max) || Math.max(...rows.map((row) => Math.abs(Number(row[valueField]) || 0)), 1);
      const x = (value) => m.l + ((Number(value) + maxAbs) / (maxAbs * 2 || 1)) * (w - m.l - m.r);
      const zero = x(0);
      const rowGap = Number(instance.config.row_gap || 21);
      const firstY = Number(instance.config.first_y || 13);
      const barH = Number(instance.config.bar_height || 14);
      const bars = rows.map((row, i) => {
        const value = Number(row[valueField]) || 0;
        const y0 = firstY + i * rowGap;
        const x0 = value >= 0 ? zero : x(value);
        const width = Math.abs(x(value) - zero);
        const cls = row.class || (value >= 0 ? instance.config.positive_class : instance.config.negative_class) || "bar";
        const valueLabel = valueLabelField && row[valueLabelField] !== undefined ? row[valueLabelField] : formatByMode(value, instance.config.value_label_format);
        const labelX = value >= 0 ? x(value) + Number(instance.config.value_label_dx ?? 6) : x(value) - Number(instance.config.value_label_dx ?? 6);
        return `<text class="axis-tick" x="${m.l - 8}" y="${y0 + barH - 3}" text-anchor="end">${escapeHtml(row[categoryField])}</text><rect class="${escapeHtml(cls)}" x="${x0}" y="${y0}" width="${Math.max(0, width)}" height="${barH}" rx="${Number(instance.config.bar_radius ?? 4)}"></rect><text class="${escapeHtml(instance.config.value_label_class || "bar-label")}" x="${labelX}" y="${y0 + barH - 3}" text-anchor="${value >= 0 ? "start" : "end"}">${escapeHtml(valueLabel)}</text>`;
      }).join("");
      const caption = instance.config.caption ? `<text class="axis-label" x="${m.l + (w - m.l - m.r) / 2}" y="${h - 6}" text-anchor="middle">${escapeHtml(instance.config.caption)}</text>` : "";
      return svg(`<line class="${escapeHtml(instance.config.zero_line_class || "zero-line")}" x1="${zero}" x2="${zero}" y1="${m.t}" y2="${h - m.b}"></line>${bars}<line class="axis-line" x1="${m.l}" x2="${w - m.r}" y1="${h - m.b}" y2="${h - m.b}"></line>${caption}`, `0 0 ${w} ${h}`);
    }
    if (instance.config.bar_style === "horizontal_grouped") {
      const categoryField = instance.config.category_field || "category";
      const series = instance.config.series_fields || ["baseline", "current"];
      const classes = instance.config.series_classes || [];
      const { w, h } = viewBoxFor(instance.config, 630, 440);
      const m = marginFor(instance.config, { t: 24, r: 28, b: 62, l: 92 });
      const plotW = w - m.l - m.r;
      const values = rows.flatMap((row) => series.map((field) => Number(row[field]) || 0));
      const xMax = Number(instance.config.x_max) || Math.max(...values, 1);
      const seriesMaxes = instance.config.series_x_maxes || [];
      const x = (value, seriesIndex = 0) => {
        const max = Number(seriesMaxes[seriesIndex] ?? xMax) || xMax || 1;
        return m.l + (Number(value) / max) * plotW;
      };
      const rowGap = Number(instance.config.row_gap || 48);
      const firstY = Number(instance.config.first_y ?? (m.t + 14));
      const barH = Number(instance.config.bar_height || 13);
      const seriesGap = Number(instance.config.series_gap ?? 5);
      const yFor = (rowIndex, seriesIndex) => firstY + rowIndex * rowGap + seriesIndex * (barH + seriesGap);
      const xTicks = ticksFor(0, xMax, instance.config.x_ticks, 5);
      const grid = xTicks.map((tick) => `<line class="grid-line" x1="${x(tick, 0)}" x2="${x(tick, 0)}" y1="${m.t}" y2="${h - m.b}"></line><text class="axis-tick" x="${x(tick, 0)}" y="${h - m.b + 24}" text-anchor="middle">${formatByMode(tick, instance.config.x_tick_format)}</text>`).join("");
      const connectors = (instance.config.rank_connectors || []).map((connector) => {
        const fromField = connector.from_field || series[0];
        const toField = connector.to_field || series[1];
        const minDelta = Number(connector.min_abs_delta ?? connector.min_delta ?? 0);
        const fromIndex = Math.max(0, series.indexOf(fromField));
        const toIndex = Math.max(0, series.indexOf(toField));
        return rows.map((row, i) => {
          if (!hasFiniteValue(row[fromField]) || !hasFiniteValue(row[toField])) return "";
          const fromValue = Number(row[fromField]);
          const toValue = Number(row[toField]);
          if (Math.abs(toValue - fromValue) < minDelta) return "";
          return `<line class="${escapeHtml(connector.class || "rank-line")}" x1="${x(fromValue, fromIndex)}" y1="${yFor(i, fromIndex) + barH / 2}" x2="${x(toValue, toIndex)}" y2="${yFor(i, toIndex) + barH / 2}"></line>`;
        }).join("");
      }).join("");
      const bars = rows.map((row, i) => {
        const labelY = yFor(i, 0) + Number(instance.config.category_label_dy ?? 17);
        const body = series.map((field, s) => {
          const value = Number(row[field]) || 0;
          const barClass = classes[s] || "bar";
          const labelFields = instance.config.series_value_label_fields || [];
          const labelField = labelFields[s];
          const valueLabel = labelField && row[labelField] !== undefined ? row[labelField] : formatByMode(value, instance.config.value_label_format);
          const label = instance.config.show_series_value_labels
            ? `<text class="${escapeHtml(instance.config.value_label_class || "axis-tick")}" x="${x(value, s) + Number(instance.config.value_label_dx ?? 8)}" y="${yFor(i, s) + barH + Number(instance.config.value_label_dy ?? -2)}">${escapeHtml(valueLabel)}</text>`
            : "";
          return `<rect class="${escapeHtml(barClass)}" x="${m.l}" y="${yFor(i, s)}" width="${Math.max(0, x(value, s) - m.l)}" height="${barH}" rx="${Number(instance.config.bar_radius ?? 4)}"></rect>${label}`;
        }).join("");
        return `<text class="bar-label" x="${m.l - 10}" y="${labelY}" text-anchor="end">${escapeHtml(row[categoryField])}</text>${body}`;
      }).join("");
      const annotations = (instance.config.annotations || []).map((annotation) => `<text class="${escapeHtml(annotation.class || "axis-label")}" x="${Number(annotation.x)}" y="${Number(annotation.y)}">${escapeHtml(annotation.text || "")}</text>`).join("");
      const xAxisLabel = instance.config.x_axis_label ? `<text class="axis-label" x="${Number(instance.config.axis_label_x ?? (m.l + plotW / 2))}" y="${Number(instance.config.axis_label_y ?? (h - 12))}" text-anchor="middle">${escapeHtml(instance.config.x_axis_label)}</text>` : "";
      return svg(`${grid}${bars}${connectors}
        <line class="axis-line" x1="${m.l}" x2="${m.l + plotW}" y1="${h - m.b}" y2="${h - m.b}"></line>
        ${xAxisLabel}${annotations}`, `0 0 ${w} ${h}`);
    }
    if (instance.config.bar_style === "horizontal_stacked") {
      const categoryField = instance.config.category_field || "category";
      const series = instance.config.series_fields || ["baseline", "current"];
      const classes = instance.config.series_classes || [];
      const { w, h } = viewBoxFor(instance.config, 472, 185);
      const m = marginFor(instance.config, { t: 18, r: 24, b: 32, l: 52 });
      const plotW = w - m.l - m.r;
      const rowGap = Number(instance.config.row_gap || 30);
      const firstY = Number(instance.config.first_y ?? (m.t + 4));
      const barH = Number(instance.config.bar_height || 16);
      const totalValue = (row) => series.reduce((sum, field) => sum + (Number(row[field]) || 0), 0) || 1;
      const bars = rows.map((row, i) => {
        const y0 = firstY + i * rowGap;
        const background = instance.config.background_class
          ? `<rect class="${escapeHtml(instance.config.background_class)}" x="${m.l}" y="${y0}" width="${plotW}" height="${barH}" rx="${Number(instance.config.background_radius ?? instance.config.bar_radius ?? 4)}"></rect>`
          : "";
        let offset = 0;
        const segments = series.map((field, s) => {
          const value = Number(row[field]) || 0;
          const width = plotW * value / totalValue(row);
          const x0 = m.l + offset;
          offset += width;
          return `<rect class="${escapeHtml(classes[s] || "bar")}" x="${x0}" y="${y0}" width="${Math.max(0, width)}" height="${barH}" rx="${Number(instance.config.bar_radius ?? 4)}"></rect>`;
        }).join("");
        const labelSeriesIndex = Number(instance.config.value_label_series_index ?? (series.length - 1));
        const labelField = instance.config.value_label_field;
        const labelValue = labelField && row[labelField] !== undefined
          ? row[labelField]
          : formatByMode(Number(row[series[labelSeriesIndex]]) || 0, instance.config.value_label_format || "percent");
        const labelEnd = m.l + series.slice(0, labelSeriesIndex + 1).reduce((sum, field) => sum + (plotW * (Number(row[field]) || 0) / totalValue(row)), 0);
        const labelX = instance.config.value_label_position === "segment_end"
          ? labelEnd - Number(instance.config.value_label_dx ?? 8)
          : m.l + plotW - Number(instance.config.value_label_dx ?? 8);
        const categoryLabel = instance.config.hide_category_label ? "" : `<text class="bar-label" x="${m.l - 10}" y="${y0 + barH - 2}" text-anchor="end">${escapeHtml(row[categoryField])}</text>`;
        return `${categoryLabel}${background}${segments}<text class="${escapeHtml(instance.config.value_label_class || "bar-label")}" x="${labelX}" y="${y0 + barH - 3}" text-anchor="end">${escapeHtml(labelValue)}</text>`;
      }).join("");
      const caption = instance.config.caption ? `<text class="axis-label" x="${Number(instance.config.caption_x ?? (m.l + plotW / 2))}" y="${Number(instance.config.caption_y ?? (h - 8))}" text-anchor="middle">${escapeHtml(instance.config.caption)}</text>` : "";
      const annotations = (instance.config.annotations || []).map((annotation) => `<text class="${escapeHtml(annotation.class || "axis-label")}" x="${Number(annotation.x)}" y="${Number(annotation.y)}" text-anchor="${escapeHtml(annotation.anchor || "start")}">${escapeHtml(annotation.text || "")}</text>`).join("");
      return svg(`${bars}<line class="axis-line" x1="${m.l}" x2="${w - m.r}" y1="${h - m.b}" y2="${h - m.b}"></line>${caption}${annotations}`, `0 0 ${w} ${h}`);
    }
    if (instance.config.bar_style === "vertical_threshold") {
      const categoryField = instance.config.category_field || "category";
      const valueField = instance.config.value_field || "value";
      const threshold = Number(instance.config.threshold ?? instance.config.threshold_value ?? 0);
      const { w, h } = viewBoxFor(instance.config, 472, 185);
      const m = marginFor(instance.config, { t: 20, r: 30, b: 38, l: 58 });
      const yMax = Number(instance.config.y_max) || Math.max(...rows.map((row) => Number(row[valueField]) || 0), threshold, 1);
      const x = (i) => m.l + ((i) / Math.max(1, rows.length - 1)) * (w - m.l - m.r);
      const y = (v) => m.t + (1 - (Number(v) / (yMax || 1))) * (h - m.t - m.b);
      const thresholdLine = Number.isFinite(threshold) ? `<line class="${escapeHtml(instance.config.threshold_class || "tolerance-line")}" x1="${m.l}" x2="${w - m.r}" y1="${y(threshold)}" y2="${y(threshold)}"></line>${instance.config.threshold_label ? `<text class="axis-label" x="${m.l + 8}" y="${y(threshold) - 7}">${escapeHtml(instance.config.threshold_label)}</text>` : ""}` : "";
      const bars = rows.map((row, i) => {
        const value = Number(row[valueField]) || 0;
        const barClass = row.class || (threshold && value > threshold ? instance.config.over_class : instance.config.bar_class) || "bar";
        const barX = x(i) - Number(instance.config.bar_width || 18);
        const barW = Number(instance.config.bar_width || 36);
        return `<rect class="${escapeHtml(barClass)}" x="${barX}" y="${y(value)}" width="${barW}" height="${h - m.b - y(value)}" rx="4"></rect><text class="axis-tick" x="${x(i)}" y="${h - m.b + 22}" text-anchor="middle">${escapeHtml(row[categoryField])}</text>`;
      }).join("");
      const caption = instance.config.caption ? `<text class="axis-label" x="${m.l + (w - m.l - m.r) / 2}" y="${h - 6}" text-anchor="middle">${escapeHtml(instance.config.caption)}</text>` : "";
      const annotations = (instance.config.annotations || []).map((annotation) => `<text class="${escapeHtml(annotation.class || "axis-label")}" x="${annotation.x}" y="${annotation.y}">${escapeHtml(annotation.text || "")}</text>`).join("");
      return svg(`${thresholdLine}${bars}<line class="axis-line" x1="${m.l}" x2="${w - m.r}" y1="${h - m.b}" y2="${h - m.b}"></line>${caption}${annotations}`, `0 0 ${w} ${h}`);
    }
    if (instance.config.bar_style === "horizontal_threshold") {
      const categoryField = instance.config.category_field || "category";
      const valueField = instance.config.value_field || "value";
      const valueLabelField = instance.config.value_label_field || instance.config.display_value_field;
      const thresholdField = instance.config.threshold_field;
      const threshold = Number(instance.config.threshold ?? instance.config.threshold_value ?? 0);
      const { w, h } = viewBoxFor(instance.config, 472, 185);
      const m = marginFor(instance.config, { t: 24, r: 40, b: 38, l: 88 });
      const xMax = Number(instance.config.x_max) || Math.max(...rows.flatMap((row) => [Number(row[valueField]) || 0, thresholdField ? Number(row[thresholdField]) || 0 : threshold]), 1);
      const x = (v) => m.l + (Number(v) / (xMax || 1)) * (w - m.l - m.r);
      const thresholdLine = !thresholdField && Number.isFinite(threshold) ? `<line class="${escapeHtml(instance.config.threshold_class || "limit-line")}" x1="${x(threshold)}" x2="${x(threshold)}" y1="${m.t - 2}" y2="${h - m.b}"></line>${instance.config.threshold_label ? `<text class="${escapeHtml(instance.config.threshold_label_class || "callout")}" x="${x(threshold) + 6}" y="${m.t - 6}">${escapeHtml(instance.config.threshold_label)}</text>` : ""}` : "";
      const rowGap = Number(instance.config.row_gap || 27);
      const firstY = Number(instance.config.first_y || 40);
      const barH = Number(instance.config.bar_height || 14);
      const bars = rows.map((row, i) => {
        const value = Number(row[valueField]) || 0;
        const y0 = firstY + i * rowGap;
        const rowThreshold = thresholdField && hasFiniteValue(row[thresholdField]) ? Number(row[thresholdField]) : threshold;
        const barClass = row.class || (rowThreshold && value > rowThreshold ? instance.config.over_class : instance.config.bar_class) || "bar";
        const valueLabel = valueLabelField && row[valueLabelField] !== undefined ? row[valueLabelField] : formatNumber(value);
        const rowThresholdLine = thresholdField && Number.isFinite(rowThreshold)
          ? `<line class="${escapeHtml(row.threshold_class || instance.config.threshold_class || "limit-line")}" x1="${x(rowThreshold)}" x2="${x(rowThreshold)}" y1="${y0 - Number(instance.config.threshold_y_pad ?? 10)}" y2="${y0 + barH + Number(instance.config.threshold_y_pad ?? 12)}"></line>`
          : "";
        return `<text class="bar-label" x="${m.l - 16}" y="${y0 + barH - 3}" text-anchor="end">${escapeHtml(row[categoryField])}</text>${rowThresholdLine}<rect class="${escapeHtml(barClass)}" x="${m.l}" y="${y0}" width="${Math.max(0, x(value) - m.l)}" height="${barH}" rx="3"></rect><text class="axis-tick" x="${x(value) + Number(instance.config.value_label_dx ?? 7)}" y="${y0 + barH - 2}">${escapeHtml(valueLabel)}</text>`;
      }).join("");
      const caption = instance.config.caption ? `<text class="axis-label" x="${m.l + (w - m.l - m.r) / 2}" y="${h - 6}" text-anchor="middle">${escapeHtml(instance.config.caption)}</text>` : "";
      return svg(`${thresholdLine}${bars}<line class="axis-line" x1="${m.l}" x2="${w - m.r}" y1="${h - m.b}" y2="${h - m.b}"></line>${caption}`, `0 0 ${w} ${h}`);
    }
    if (Array.isArray(instance.config.series_fields) && instance.config.series_fields.length) {
      const categoryField = instance.config.category_field || "category";
      const series = instance.config.series_fields;
      const labels = instance.config.series_labels || series;
      const classes = instance.config.series_classes || [];
      const classFields = instance.config.series_class_fields || [];
      const valueMax = Number(instance.config.x_max) || Math.max(...rows.flatMap((row) => series.map((field) => Number(row[field]) || 0)), 1);
      const { w, h } = viewBoxFor(instance.config, 472, 185);
      const m = marginFor(instance.config, { t: 14, r: 32, b: 36, l: 112 });
      const x = (v) => m.l + (Number(v) / (valueMax || 1)) * (w - m.l - m.r);
      const rowGap = Number(instance.config.row_gap || 42);
      const barH = Number(instance.config.bar_height || 13);
      const firstY = Number(instance.config.first_y || 32);
      const body = rows.map((row, i) => {
        const y0 = firstY + i * rowGap;
        const bars = series.map((field, s) => {
          const y = y0 + s * (barH + 4);
          const value = Number(row[field]) || 0;
          const rowClass = classFields[s] ? row[classFields[s]] : "";
          return `<rect class="${escapeHtml(rowClass || classes[s] || "bar")}" x="${m.l}" y="${y}" width="${Math.max(0, x(value) - m.l)}" height="${barH}" rx="3"></rect><text class="axis-tick" x="${x(value) + 6}" y="${y + barH - 2}">${formatNumber(value)}</text>`;
        }).join("");
        return `<text class="label" x="${m.l - 18}" y="${y0 + barH + 1}" text-anchor="end">${escapeHtml(row[categoryField])}</text>${bars}`;
      }).join("");
      const legend = labels.map((label, i) => `<text class="${escapeHtml(classes[i]?.replace("bar-", "callout-") || "axis-label")}" x="${m.l + i * 88}" y="${h - 14}">${escapeHtml(label)}</text>`).join("");
      const annotations = (instance.config.annotations || []).map((annotation) => `<text class="${escapeHtml(annotation.class || "axis-label")}" x="${annotation.x}" y="${annotation.y}">${escapeHtml(annotation.text || "")}</text>`).join("");
      return svg(`${body}${legend}${annotations}`, `0 0 ${w} ${h}`);
    }
    const categoryField = instance.config.category_field || instance.config.item_field || instance.config.metric_field || "category";
    const valueField = instance.config.value_field || instance.config.score_field || instance.config.distance_field || "value";
    const sorted = rows.slice(0, 7).sort((a, b) => Number(b[valueField]) - Number(a[valueField]));
    const max = Math.max(...sorted.map((row) => Number(row[valueField]) || 0), 1);
    const rowH = 24;
    return svg(sorted.map((row, i) => {
      const y = 18 + i * rowH;
      const w = (Number(row[valueField]) || 0) / max * 220;
      return `<text class="label" x="78" y="${y + 13}" text-anchor="end">${escapeHtml(row[categoryField] || `item ${i+1}`)}</text><rect class="bar${i===0 ? " hot" : ""}" x="86" y="${y}" width="${w}" height="16" rx="4"></rect>`;
    }).join(""));
  }

  return Object.freeze({
    renderBar
  });
}

if (typeof module !== "undefined") {
  module.exports = { createBarRenderers };
}
