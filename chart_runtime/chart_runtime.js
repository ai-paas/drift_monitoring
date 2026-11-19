(() => {
  // Public entry point and DOM shell helpers.
  // @managed-contract contract_id=chart_runtime.renderChartPayload level=P0
  function renderChartPayload(target, payload) {
    const componentChart = typeof target === "string" ? document.querySelector(target) : target;
    if (!componentChart || !payload) return;
    componentChart.__chartRuntimePayload = payload;
    renderComponentChart(componentChart, payload);
    bindNotePopup(componentChart);
    updateChartTestState(componentChart, payload);
  }
  function escapeHtml(value) {
    return String(value).replaceAll("&", "&amp;").replaceAll("<", "&lt;").replaceAll(">", "&gt;").replaceAll('"', "&quot;");
  }

  function componentNoteForArea(instances) {
    const component = (instances || []).find((item) =>
      !item.isOverlay
      && item.area !== "notes"
      && item.componentType !== "domain_specific_visual"
      && item.interpretationNote
    );
    return noteTextFromObject(component?.interpretationNote);
  }

  function renderComponentChart(componentChart, payload) {
    const layout = payload.layout;
    const container = document.createElement("section");
    container.className = "chart-container";
    container.style.gridTemplateColumns = layout.gridTemplateColumns || `repeat(${layout.columns}, minmax(0, 1fr))`;
    container.style.gridTemplateRows = layout.gridTemplateRows || `repeat(${layout.rows}, minmax(0, 1fr))`;
    if (layout.gap) container.style.gap = layout.gap;
    layout.areas.forEach((area) => {
      const areaEl = document.createElement("article");
      areaEl.className = "chart-area";
      areaEl.dataset.area = area.area;
      areaEl.dataset.role = area.role || "";
      const instances = payload.components.filter((item) => item.area === area.area);
      const componentNote = componentNoteForArea(instances);
      if (area.title || area.description || componentNote) areaEl.classList.add("has-panel-head");
      if (area.className) areaEl.classList.add(area.className);
      areaEl.style.gridColumn = `${area.x + 1} / span ${area.w}`;
      areaEl.style.gridRow = `${area.y + 1} / span ${area.h}`;
      const inset = area.stageInset || {};
      const inlineDescription = area.description && area.descriptionMode === "inline" && !componentNote
        ? `<p>${escapeHtml(area.description)}</p>`
        : "";
      const noteText = componentNote || (area.descriptionMode !== "inline" ? area.description : "");
      const noteButton = noteText
        ? `<button class="note-link" type="button" data-note="${escapeHtml(noteText)}">${escapeHtml(area.noteLabel || "해석")}</button>`
        : "";
      const hasZoomableVisual = instances.some((item) => !item.isOverlay && item.componentType !== "decision_card")
        && area.role !== "summary";
      const zoomButton = hasZoomableVisual
        ? `<button class="area-zoom-link" type="button" data-area="${escapeHtml(area.area)}" title="컴포넌트 확대">확대</button>`
        : "";
      const head = area.title || area.description || noteButton
        ? `<div class="area-head" style="${area.headerHeight ? `height:${Number(area.headerHeight)}px` : ""}"><h2>${escapeHtml(area.title || "")}</h2><div class="area-actions">${inlineDescription}${noteButton}${zoomButton}</div></div>`
        : zoomButton
          ? `<button class="area-zoom-link area-zoom-floating" type="button" data-area="${escapeHtml(area.area)}" title="컴포넌트 확대">확대</button>`
        : "";
      const implicitHeaderInset = noteButton && !area.title && !area.description ? 28 : undefined;
      const stageStyle = [
        inset.top !== undefined ? `top:${Number(inset.top)}px` : implicitHeaderInset !== undefined ? `top:${implicitHeaderInset}px` : "",
        inset.right !== undefined ? `right:${Number(inset.right)}px` : "",
        inset.bottom !== undefined ? `bottom:${Number(inset.bottom)}px` : "",
        inset.left !== undefined ? `left:${Number(inset.left)}px` : ""
      ].filter(Boolean).join(";");
      const areaLabel = layout.showAreaLabels ? `<div class="area-label">${escapeHtml(area.area)}</div>` : "";
      areaEl.innerHTML = `<div class="area-body">${head}<div class="component-stage" style="${stageStyle}"></div><div class="component-overlay"></div>${areaLabel}</div>`;
      const stage = areaEl.querySelector(".component-stage");
      const overlayStage = areaEl.querySelector(".component-overlay");
      const baseComponents = instances.filter((item) => !item.isOverlay);
      const overlays = instances.filter((item) => item.isOverlay);
      if (baseComponents.length) {
        stage.innerHTML = wrapComponent(baseComponents[0], renderComponent(payload, baseComponents[0]));
        if (baseComponents.length > 1) {
          areaEl.dataset.overflowComponents = baseComponents.slice(1).map((item) => item.componentType).join(", ");
        }
      } else if (overlays.length) {
        stage.innerHTML = wrapComponent(overlays[0], renderComponent(payload, overlays[0]));
      }
      overlayStage.innerHTML = overlays.map((item) => wrapComponent(item, renderComponent(payload, item))).join("");
      container.appendChild(areaEl);
    });
    componentChart.innerHTML = "";
    componentChart.appendChild(container);
    normalizeSvgSizing(componentChart);
  }

  // Payload and component helper functions.
  function noteTextFromObject(note) {
    if (!note) return "";
    if (typeof note === "string") return note;
    return [note.title, note.summary, note.detail].filter(Boolean).join("\n\n");
  }

  function wrapComponent(instance, markup) {
    return `<div class="runtime-component" data-instance-id="${escapeHtml(instance.componentInstanceId || "")}" data-component-type="${escapeHtml(instance.componentType || "")}">${markup}</div>`;
  }

  // @managed-contract contract_id=chart_runtime.dataFor level=P0
  function dataFor(payload, instance) {
    return payload.data?.[instance.dataBinding?.source] || [];
  }

  // @managed-contract contract_id=chart_runtime.rowsForSource level=P0
  function rowsForSource(payload, source) {
    return payload.data?.[source] || [];
  }

  // @managed-contract contract_id=chart_runtime.buildChartTestState level=P1
  function buildChartTestState(componentChart, payload) {
    const components = Array.isArray(payload.components) ? payload.components : [];
    const data = payload.data && typeof payload.data === "object" ? payload.data : {};
    const dataBindings = components.map((component) => ({
      componentInstanceId: component.componentInstanceId || "",
      componentType: component.componentType || "",
      area: component.area || "",
      source: component.dataBinding?.source || "",
      xField: component.dataBinding?.xField || "",
      yField: component.dataBinding?.yField || "",
      rowCount: component.dataBinding?.source ? rowsForSource(payload, component.dataBinding.source).length : 0
    }));
    const componentNotes = Array.isArray(payload.interpretation?.componentNotes)
      ? payload.interpretation.componentNotes
      : components
        .filter((component) => component.interpretationNote)
        .map((component) => ({
          componentInstanceId: component.componentInstanceId || "",
          ...component.interpretationNote
        }));
    return {
      renderStatus: "rendered",
      chartId: payload.chartId || "",
      title: payload.title || "",
      layoutAreaCount: Array.isArray(payload.layout?.areas) ? payload.layout.areas.length : 0,
      componentCount: components.length,
      dataSourceCount: Object.keys(data).length,
      dataSources: Object.fromEntries(Object.entries(data).map(([source, rows]) => [
        source,
        Array.isArray(rows) ? rows.length : 0
      ])),
      components: components.map((component) => ({
        componentInstanceId: component.componentInstanceId || "",
        componentType: component.componentType || "",
        area: component.area || "",
        isOverlay: component.isOverlay === true,
        cardStyle: component.config?.card_style || "",
        hasInterpretationNote: Boolean(component.interpretationNote)
      })),
      dataBindings,
      componentNotes,
      checks: {
        hasTrendLineMetricSeries: dataBindings.some((binding) =>
          binding.componentType === "trend_line" && binding.source === "metric_series"
        ),
        hasEventMarker: components.some((component) => component.componentType === "event_marker"),
        hasNotesLegend: components.some((component) =>
          component.componentType === "decision_card" && component.config?.card_style === "notes_legend"
        ),
        hasLlmComponentNotes: componentNotes.length > 0
      },
      dom: {
        renderedComponentCount: componentChart.querySelectorAll(".runtime-component").length,
        areaCount: componentChart.querySelectorAll(".chart-area").length,
        notesLegendCount: componentChart.querySelectorAll(".notes-card").length
      }
    };
  }

  // @managed-contract contract_id=chart_runtime.window.__CHART_TEST_STATE__ level=P1
  function updateChartTestState(componentChart, payload) {
    window.__CHART_TEST_STATE__ = buildChartTestState(componentChart, payload);
  }

  // Component registry and payload contract metadata.
  // @managed-contract contract_id=chart_runtime.COMPONENT_RENDERERS level=P0
  const COMPONENT_RENDERERS = {
    trend_line: renderLine,
    raw_signal_trend: renderLine,
    detector_statistic_view: renderLine,
    distance_metric_view: renderLine,
    performance_metric_view: renderLine,
    control_chart: renderLine,
    cumulative_curve: renderLine,
    model_diagnostic_curve: renderLine,
    adaptive_model_structure_view: renderLine,
    bar_chart: renderBar,
    ranking_view: renderBar,
    contribution_view: renderBar,
    proportion_view: renderBar,
    reference_current_comparison: renderBar,
    p_value_view: renderBar,
    heatmap: renderMatrix,
    matrix_view: renderMatrix,
    forest_plot: renderForest,
    projection_scatter: renderScatter,
    feature_projection_view: renderFeatureProjection,
    node_link_diagram: renderNodeLink,
    tree_path_diagram: renderNodeLink,
    small_multiple_lines: renderSmallMultipleLines,
    circular_histogram: renderCircularHistogram,
    circular_histogram_view: renderCircularHistogram,
    event_raster: renderEventRaster,
    raster_view: renderEventRaster,
    distribution_view: renderDistribution,
    histogram_view: renderDistribution,
    distribution_summary_plot: renderDistribution,
    quantile_view: renderDistribution,
    state_timeline: renderTimeline,
    window_view: renderTimeline,
    threshold_line: (_payload, instance) => renderThreshold(instance),
    event_marker: renderEvents,
    uncertainty_band: renderBand,
    comparison_table: renderTable
  };

  // @managed-contract contract_id=chart_runtime.COMPONENT_SPECS level=P0
  const COMPONENT_SPECS = {
    trend_line: { renderer: "line", fieldContract: "line_series", requiresData: true },
    raw_signal_trend: { renderer: "line", fieldContract: "line_series", requiresData: true },
    detector_statistic_view: { renderer: "line", fieldContract: "line_series", requiresData: true },
    distance_metric_view: { renderer: "line", fieldContract: "line_series", requiresData: true },
    performance_metric_view: { renderer: "line", fieldContract: "line_series", requiresData: true },
    control_chart: { renderer: "line", fieldContract: "line_series", requiresData: true },
    cumulative_curve: { renderer: "line", fieldContract: "line_series", requiresData: true },
    model_diagnostic_curve: { renderer: "line", fieldContract: "line_series", requiresData: true },
    adaptive_model_structure_view: { renderer: "line", fieldContract: "line_series", requiresData: true },
    bar_chart: { renderer: "bar", fieldContract: "category_value", requiresData: true },
    ranking_view: { renderer: "bar", fieldContract: "category_value", requiresData: true },
    contribution_view: { renderer: "bar", fieldContract: "category_value", requiresData: true },
    proportion_view: { renderer: "bar", fieldContract: "category_value", requiresData: true },
    reference_current_comparison: { renderer: "bar", fieldContract: "category_value", requiresData: true },
    p_value_view: { renderer: "bar", fieldContract: "category_value", requiresData: true },
    heatmap: { renderer: "matrix", fieldContract: "matrix_cells", requiresData: true },
    matrix_view: { renderer: "matrix", fieldContract: "matrix_cells", requiresData: true },
    forest_plot: { renderer: "forest", fieldContract: "estimate_interval", requiresData: true },
    projection_scatter: { renderer: "scatter", fieldContract: "xy_points", requiresData: true },
    feature_projection_view: { renderer: "feature_projection", fieldContract: "projected_features", requiresData: true },
    node_link_diagram: { renderer: "node_link", fieldContract: "node_link", requiresData: true },
    tree_path_diagram: { renderer: "node_link", fieldContract: "node_link", requiresData: true },
    small_multiple_lines: { renderer: "small_multiple_lines", fieldContract: "line_series", requiresData: true },
    circular_histogram: { renderer: "circular_histogram", fieldContract: "polar_bins", requiresData: true },
    circular_histogram_view: { renderer: "circular_histogram", fieldContract: "polar_bins", requiresData: true },
    event_raster: { renderer: "event_raster", fieldContract: "event_rows", requiresData: true },
    raster_view: { renderer: "event_raster", fieldContract: "event_rows", requiresData: true },
    distribution_view: { renderer: "distribution", fieldContract: "distribution_rows", requiresData: true },
    histogram_view: { renderer: "distribution", fieldContract: "distribution_rows", requiresData: true },
    distribution_summary_plot: { renderer: "distribution", fieldContract: "distribution_rows", requiresData: true },
    quantile_view: { renderer: "distribution", fieldContract: "distribution_rows", requiresData: true },
    state_timeline: { renderer: "timeline", fieldContract: "time_ranges", requiresData: true },
    window_view: { renderer: "timeline", fieldContract: "time_ranges", requiresData: true },
    threshold_line: { renderer: "threshold", fieldContract: "threshold_config", requiresData: false, overlay: true },
    event_marker: { renderer: "event_marker", fieldContract: "event_rows", requiresData: true, overlay: true },
    uncertainty_band: { renderer: "band", fieldContract: "interval_band", requiresData: true, overlay: true },
    comparison_table: { renderer: "table", fieldContract: "table_rows", requiresData: true }
  };

  function renderComponent(payload, instance) {
    const renderer = COMPONENT_RENDERERS[instance.componentType] || renderCard;
    return renderer(payload, instance);
  }

  // Pure data, formatting, scale, and SVG markup helpers.
  function extent(rows, field) {
    const values = rows.map((row) => row[field]).filter(hasFiniteValue).map(Number);
    if (!values.length) return [0, 1];
    const min = Math.min(...values);
    const max = Math.max(...values);
    return min === max ? [min - 1, max + 1] : [min, max];
  }

  function formatNumber(value) {
    const num = Number(value);
    if (!Number.isFinite(num)) return "";
    if (Number.isInteger(num)) return String(num);
    if (Math.abs(num) >= 100) return num.toFixed(0);
    if (Math.abs(num) >= 10) return num.toFixed(1);
    return num.toFixed(2);
  }

  function formatByMode(value, mode) {
    if (mode === "percent") {
      const num = Number(value);
      return Number.isFinite(num) ? `${Math.round(num * 100)}%` : "";
    }
    if (mode === "fixed1") {
      const num = Number(value);
      return Number.isFinite(num) ? num.toFixed(1) : "";
    }
    if (mode === "fixed2") {
      const num = Number(value);
      return Number.isFinite(num) ? num.toFixed(2) : "";
    }
    if (mode === "fixed3") {
      const num = Number(value);
      return Number.isFinite(num) ? num.toFixed(3) : "";
    }
    return formatNumber(value);
  }

  function hasFiniteValue(value) {
    return value !== null && value !== undefined && value !== "" && Number.isFinite(Number(value));
  }

  function viewBoxFor(config, defaultW, defaultH) {
    const box = Array.isArray(config.view_box) ? config.view_box : [];
    const w = Number(box[0] ?? config.view_box_width ?? defaultW);
    const h = Number(box[1] ?? config.view_box_height ?? defaultH);
    return { w: Number.isFinite(w) ? w : defaultW, h: Number.isFinite(h) ? h : defaultH };
  }

  function marginFor(config, defaults) {
    const margin = config.margin || {};
    return {
      t: Number(margin.top ?? config.margin_top ?? defaults.t),
      r: Number(margin.right ?? config.margin_right ?? defaults.r),
      b: Number(margin.bottom ?? config.margin_bottom ?? defaults.b),
      l: Number(margin.left ?? config.margin_left ?? defaults.l)
    };
  }

  function ticksFor(min, max, configured, count = 5) {
    if (Array.isArray(configured)) {
      return configured.map(Number).filter(Number.isFinite);
    }
    if (count <= 1) return [min];
    return Array.from({ length: count }, (_, i) => min + ((max - min) * i) / (count - 1));
  }

  function path(points) {
    return points.map((p, i) => `${i ? "L" : "M"}${p[0].toFixed(1)},${p[1].toFixed(1)}`).join(" ");
  }

  function stepPath(points) {
    if (!points.length) return "";
    return points.slice(1).reduce((d, point) => `${d}H${point[0].toFixed(1)}V${point[1].toFixed(1)}`, `M${points[0][0].toFixed(1)},${points[0][1].toFixed(1)}`);
  }

  function svg(inner, viewBox = "0 0 360 220") {
    const parts = String(viewBox).split(/[ ,]+/).map(Number);
    const w = Number.isFinite(parts[2]) && parts[2] > 0 ? parts[2] : 360;
    const h = Number.isFinite(parts[3]) && parts[3] > 0 ? parts[3] : 220;
    return `<svg class="chart-svg" viewBox="${viewBox}" preserveAspectRatio="none" role="img" style="--chart-svg-w:${w}px;--chart-svg-h:${h}px">${inner}</svg>`;
  }

  // DOM measurement helpers.
  function normalizeSvgSizing(root) {
    if (!root || typeof root.querySelectorAll !== "function") return;
    root.querySelectorAll("svg.chart-svg").forEach((item) => {
      const viewBox = item.getAttribute("viewBox");
      if (!viewBox || typeof item.getBBox !== "function") return;
      const parts = viewBox.split(/[ ,]+/).map(Number);
      if (parts.length < 4 || parts.some((num) => !Number.isFinite(num))) return;
      const [vx, vy, vw, vh] = parts;
      let box;
      try {
        box = item.getBBox();
      } catch (error) {
        return;
      }
      if (!box || !Number.isFinite(box.x) || !Number.isFinite(box.y)) return;
      const pad = 18;
      const minX = Math.min(vx, box.x - pad);
      const minY = Math.min(vy, box.y - pad);
      const maxX = Math.max(vx + vw, box.x + box.width + pad);
      const maxY = Math.max(vy + vh, box.y + box.height + pad);
      const nextW = Math.ceil(maxX - minX);
      const nextH = Math.ceil(maxY - minY);
      if (nextW > vw + 2 || nextH > vh + 2 || minX < vx - 2 || minY < vy - 2) {
        item.setAttribute("viewBox", `${Math.floor(minX)} ${Math.floor(minY)} ${nextW} ${nextH}`);
      }
      item.style.setProperty("--chart-svg-w", `${Math.max(vw, nextW)}px`);
      item.style.setProperty("--chart-svg-h", `${Math.max(vh, nextH)}px`);
    });
  }

  function parseHexColor(value) {
    const raw = String(value || "").trim();
    const hex = raw.startsWith("#") ? raw.slice(1) : raw;
    if (/^[0-9a-f]{3}$/i.test(hex)) {
      return hex.split("").map((ch) => parseInt(ch + ch, 16));
    }
    if (/^[0-9a-f]{6}$/i.test(hex)) {
      return [0, 2, 4].map((index) => parseInt(hex.slice(index, index + 2), 16));
    }
    return [47, 111, 159];
  }

  function heatmapColor(value, config) {
    const min = Number(config.value_min ?? 0);
    const max = Number(config.value_max ?? 1);
    const normalized = Math.max(0, Math.min(1, (Number(value) - min) / (max - min || 1)));
    const stops = (Array.isArray(config.palette) && config.palette.length
      ? config.palette
      : [[0, "#d9e6ef"], [0.55, "#c9952f"], [1, "#b95a50"]]
    ).map((stop) => ({ at: Number(stop[0]), color: parseHexColor(stop[1]) }))
      .filter((stop) => Number.isFinite(stop.at))
      .sort((a, b) => a.at - b.at);
    if (!stops.length) stops.push({ at: 0, color: parseHexColor("#d9e6ef") }, { at: 1, color: parseHexColor("#b95a50") });
    const lower = [...stops].reverse().find((stop) => stop.at <= normalized) || stops[0];
    const upper = stops.find((stop) => stop.at >= normalized) || stops[stops.length - 1];
    const factor = lower === upper ? 0 : (normalized - lower.at) / (upper.at - lower.at || 1);
    const mixed = lower.color.map((channel, index) => Math.round(channel + (upper.color[index] - channel) * factor));
    return `rgb(${mixed[0]},${mixed[1]},${mixed[2]})`;
  }

  function classForValue(value, rules, fallback) {
    const num = Number(value);
    const match = (Array.isArray(rules) ? rules : []).find((rule) => {
      if (!rule || !rule.class) return false;
      if (rule.lt !== undefined && !(num < Number(rule.lt))) return false;
      if (rule.lte !== undefined && !(num <= Number(rule.lte))) return false;
      if (rule.gt !== undefined && !(num > Number(rule.gt))) return false;
      if (rule.gte !== undefined && !(num >= Number(rule.gte))) return false;
      if (rule.min !== undefined && !(num >= Number(rule.min))) return false;
      if (rule.max !== undefined && !(num <= Number(rule.max))) return false;
      return true;
    });
    return match?.class || fallback;
  }

  // Component renderers.
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

  function renderNodeLink(payload, instance) {
    const rows = dataFor(payload, instance);
    const { w, h } = viewBoxFor(instance.config, 472, 185);
    const idField = instance.config.id_field || "id";
    const labelField = instance.config.label_field || "label";
    const xField = instance.config.x_field || "x";
    const yField = instance.config.y_field || "y";
    const widthField = instance.config.width_field || "w";
    const heightField = instance.config.height_field || "h";
    const classField = instance.config.class_field || "class";
    const nodes = rows.filter((row) => hasFiniteValue(row[xField]) && hasFiniteValue(row[yField]));
    const nodeById = new Map(nodes.map((node) => [String(node[idField]), node]));
    const pointFor = (node, anchor) => {
      const x0 = Number(node[xField]);
      const y0 = Number(node[yField]);
      const nw = Number(node[widthField] ?? instance.config.node_width ?? 120);
      const nh = Number(node[heightField] ?? instance.config.node_height ?? 34);
      if (anchor === "top") return [x0 + nw / 2, y0];
      if (anchor === "bottom") return [x0 + nw / 2, y0 + nh];
      if (anchor === "left") return [x0, y0 + nh / 2];
      if (anchor === "right") return [x0 + nw, y0 + nh / 2];
      return [x0 + nw / 2, y0 + nh / 2];
    };
    const links = (instance.config.links || []).map((link) => {
      let x1 = Number(link.x1);
      let y1 = Number(link.y1);
      let x2 = Number(link.x2);
      let y2 = Number(link.y2);
      if (link.from && link.to) {
        const from = nodeById.get(String(link.from));
        const to = nodeById.get(String(link.to));
        if (!from || !to) return "";
        [x1, y1] = pointFor(from, link.from_anchor || "bottom");
        [x2, y2] = pointFor(to, link.to_anchor || "top");
      }
      if (![x1, y1, x2, y2].every(Number.isFinite)) return "";
      return `<line class="${escapeHtml(link.class || instance.config.link_class || "path-line")}" x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}"></line>`;
    }).join("");
    const body = nodes.map((node) => {
      const x0 = Number(node[xField]);
      const y0 = Number(node[yField]);
      const nw = Number(node[widthField] ?? instance.config.node_width ?? 120);
      const nh = Number(node[heightField] ?? instance.config.node_height ?? 34);
      const cls = node[classField] || instance.config.node_class || "node";
      return `<rect class="${escapeHtml(cls)}" x="${x0}" y="${y0}" width="${nw}" height="${nh}" rx="${Number(instance.config.node_radius ?? 6)}"></rect><text class="${escapeHtml(instance.config.node_label_class || "bar-label")}" x="${x0 + nw / 2}" y="${y0 + nh / 2 + Number(instance.config.node_label_dy ?? 4)}" text-anchor="middle">${escapeHtml(node[labelField] || "")}</text>`;
    }).join("");
    const annotations = (instance.config.annotations || []).map((annotation) => `<text class="${escapeHtml(annotation.class || "axis-label")}" x="${Number(annotation.x)}" y="${Number(annotation.y)}" text-anchor="${escapeHtml(annotation.anchor || "middle")}">${escapeHtml(annotation.text || "")}</text>`).join("");
    const caption = instance.config.caption ? `<text class="axis-label" x="${Number(instance.config.caption_x ?? (w / 2))}" y="${Number(instance.config.caption_y ?? (h - 7))}" text-anchor="middle">${escapeHtml(instance.config.caption)}</text>` : "";
    return svg(`${links}${body}${annotations}${caption}`, `0 0 ${w} ${h}`);
  }

  function renderSmallMultipleLines(payload, instance) {
    const rows = dataFor(payload, instance);
    const seriesField = instance.config.series_field || "series";
    const xField = instance.config.x_field || "time";
    const yField = instance.config.y_field || "value";
    const labelField = instance.config.label_field || seriesField;
    const classField = instance.config.class_field || "class";
    const seriesNames = Array.isArray(instance.config.series_order) && instance.config.series_order.length
      ? instance.config.series_order
      : [...new Set(rows.map((row) => row[seriesField]))];
    const { w, h } = viewBoxFor(instance.config, 472, 185);
    const m = marginFor(instance.config, { t: 8, r: 22, b: 22, l: 82 });
    const rowHeight = Number(instance.config.row_height ?? 48);
    const rowBaseOffset = Number(instance.config.row_base_offset ?? 36);
    const rowTopOffset = Number(instance.config.row_top_offset ?? 5);
    const xMin = Number.isFinite(Number(instance.config.x_min)) ? Number(instance.config.x_min) : Math.min(...rows.map((row) => Number(row[xField])).filter(Number.isFinite), 1);
    const xMax = Number.isFinite(Number(instance.config.x_max)) ? Number(instance.config.x_max) : Math.max(...rows.map((row) => Number(row[xField])).filter(Number.isFinite), 1);
    const yMin = Number.isFinite(Number(instance.config.y_min)) ? Number(instance.config.y_min) : Math.min(...rows.map((row) => Number(row[yField])).filter(Number.isFinite), 0);
    const yMax = Number.isFinite(Number(instance.config.y_max)) ? Number(instance.config.y_max) : Math.max(...rows.map((row) => Number(row[yField])).filter(Number.isFinite), 1);
    const x = (value) => m.l + ((Number(value) - xMin) / (xMax - xMin || 1)) * (w - m.l - m.r);
    const body = seriesNames.map((name, index) => {
      const seriesRows = rows.filter((row) => String(row[seriesField]) === String(name) && hasFiniteValue(row[xField]) && hasFiniteValue(row[yField]))
        .sort((a, b) => Number(a[xField]) - Number(b[xField]));
      if (!seriesRows.length) return "";
      const top = m.t + index * rowHeight;
      const base = top + rowBaseOffset;
      const y = (value) => base - ((Number(value) - yMin) / (yMax - yMin || 1)) * (rowBaseOffset - rowTopOffset);
      const lineClass = seriesRows[0][classField] || (instance.config.series_classes || [])[index] || "series-line";
      const label = seriesRows[0][labelField] ?? name;
      const points = seriesRows.map((row) => [x(row[xField]), y(row[yField])]);
      return `<line class="grid-line" x1="${m.l}" x2="${w - m.r}" y1="${base}" y2="${base}"></line>
        <path class="${escapeHtml(lineClass)}" d="${path(points)}"></path>
        <text class="${escapeHtml(instance.config.series_label_class || "mini-title")}" x="${m.l - Number(instance.config.label_dx ?? 10)}" y="${top + Number(instance.config.label_y_offset ?? 24)}" text-anchor="end">${escapeHtml(label)}</text>`;
    }).join("");
    const yStart = m.t + Number(instance.config.marker_y0_offset ?? 2);
    const yEnd = m.t + rowHeight * seriesNames.length - Number(instance.config.marker_y1_inset ?? 6);
    const verticalMarkers = (instance.config.vertical_markers || []).map((marker) => {
      const label = marker.label ? `<text class="${escapeHtml(marker.label_class || "warning-text")}" x="${x(marker.x) + Number(marker.label_dx ?? 10)}" y="${Number(marker.label_y ?? (m.t + 24))}">${escapeHtml(marker.label)}</text>` : "";
      return `<line class="${escapeHtml(marker.class || "marker-line")}" x1="${x(marker.x)}" x2="${x(marker.x)}" y1="${yStart}" y2="${yEnd}"></line>${label}`;
    }).join("");
    const annotations = (instance.config.annotations || []).map((annotation) => `<text class="${escapeHtml(annotation.class || "axis-label")}" x="${Number(annotation.x)}" y="${Number(annotation.y)}" text-anchor="${escapeHtml(annotation.anchor || "start")}">${escapeHtml(annotation.text || "")}</text>`).join("");
    const caption = instance.config.x_axis_label ? `<text class="axis-label" x="${Number(instance.config.axis_label_x ?? (m.l + (w - m.l - m.r) / 2))}" y="${Number(instance.config.axis_label_y ?? (h - 5))}" text-anchor="middle">${escapeHtml(instance.config.x_axis_label)}</text>` : "";
    return svg(`${body}${verticalMarkers}${annotations}${caption}`, `0 0 ${w} ${h}`);
  }

  function renderForest(payload, instance) {
    const rows = dataFor(payload, instance);
    const row = rows[0] || {};
    const valueField = instance.config.value_field || "value";
    const lowField = instance.config.low_field || "low";
    const highField = instance.config.high_field || "high";
    const value = Number(row[valueField] ?? instance.config.value ?? 1);
    const low = Number(row[lowField] ?? instance.config.low ?? value);
    const high = Number(row[highField] ?? instance.config.high ?? value);
    const { w, h } = viewBoxFor(instance.config, 472, 185);
    const m = marginFor(instance.config, { t: 20, r: 28, b: 42, l: 60 });
    const xMin = Number(instance.config.x_min || 0.3);
    const xMax = Number(instance.config.x_max || 12);
    const logMin = Math.log(xMin);
    const logMax = Math.log(xMax);
    const x = (num) => m.l + ((Math.log(Number(num)) - logMin) / (logMax - logMin || 1)) * (w - m.l - m.r);
    const y = Number(instance.config.point_y ?? 82);
    const ticks = Array.isArray(instance.config.x_ticks) ? instance.config.x_ticks : [0.5, 1, 2, 4, 8];
    const nullValue = Number(instance.config.null_value ?? 1);
    const grid = ticks.map((tick) => `<line class="grid-line" x1="${x(tick)}" x2="${x(tick)}" y1="${m.t}" y2="${h - m.b}"></line><text class="axis-tick" x="${x(tick)}" y="${h - 16}" text-anchor="middle">${formatNumber(tick)}</text>`).join("");
    const nullLine = `<line class="${escapeHtml(instance.config.null_line_class || "threshold-line")}" x1="${x(nullValue)}" x2="${x(nullValue)}" y1="${m.t}" y2="${h - m.b}"></line>`;
    const interval = `<line class="${escapeHtml(instance.config.interval_class || "or-line")}" x1="${x(low)}" x2="${x(high)}" y1="${y}" y2="${y}"></line>`;
    const point = `<circle class="${escapeHtml(instance.config.point_class || "or-point")}" cx="${x(value)}" cy="${y}" r="${Number(instance.config.point_radius || 8)}"></circle>`;
    const label = instance.config.label
      ? `<text class="${escapeHtml(instance.config.label_class || "warning")}" x="${x(value)}" y="${y + Number(instance.config.label_dy ?? -18)}" text-anchor="middle">${escapeHtml(instance.config.label)}</text>`
      : "";
    const axisLabel = instance.config.x_axis_label ? `<text class="axis-label" x="${m.l + (w - m.l - m.r) / 2}" y="${h - 4}" text-anchor="middle">${escapeHtml(instance.config.x_axis_label)}</text>` : "";
    const nullLabel = instance.config.null_label ? `<text class="callout" x="${x(nullValue) + Number(instance.config.null_label_dx ?? 6)}" y="${m.t + Number(instance.config.null_label_y ?? 12)}">${escapeHtml(instance.config.null_label)}</text>` : "";
    return svg(`${grid}${nullLine}${interval}${point}${label}${axisLabel}${nullLabel}`, `0 0 ${w} ${h}`);
  }

  function renderCircularHistogram(payload, instance) {
    const rows = dataFor(payload, instance);
    if (!rows.length) return renderCard(payload, instance);
    const startField = instance.config.start_field || "start";
    const endField = instance.config.end_field || "end";
    const midField = instance.config.mid_field || "mid";
    const primaryField = instance.config.primary_value_field || "reference";
    const secondaryField = instance.config.secondary_value_field || "current";
    const { w, h } = viewBoxFor(instance.config, 535, 450);
    const cx = Number(instance.config.cx ?? w / 2);
    const cy = Number(instance.config.cy ?? h / 2);
    const inner = Number(instance.config.inner_radius ?? 70);
    const maxR = Number(instance.config.max_radius ?? 176);
    const primarySpan = Number(instance.config.primary_radius_span ?? 78);
    const secondarySpan = Number(instance.config.secondary_radius_span ?? 112);
    const primaryInner = Number(instance.config.primary_inner_radius ?? (inner + Number(instance.config.primary_inner_offset ?? 0)));
    const secondaryInner = Number(instance.config.secondary_inner_radius ?? (inner + Number(instance.config.secondary_inner_offset ?? 36)));
    const primaryBase = Number(instance.config.primary_radius_base ?? (inner + Number(instance.config.primary_radius_base_offset ?? (primaryInner - inner))));
    const secondaryBase = Number(instance.config.secondary_radius_base ?? (inner + Number(instance.config.secondary_radius_base_offset ?? (secondaryInner - inner))));
    const primaryAllowInverted = Boolean(instance.config.allow_inverted_radius || instance.config.primary_allow_inverted_radius);
    const secondaryAllowInverted = Boolean(instance.config.allow_inverted_radius || instance.config.secondary_allow_inverted_radius);
    const primaryMinThickness = Number(instance.config.primary_min_bar_thickness ?? instance.config.min_bar_thickness ?? 0);
    const secondaryMinThickness = Number(instance.config.secondary_min_bar_thickness ?? instance.config.min_bar_thickness ?? 0);
    const maxValue = Number(instance.config.value_max) || Math.max(...rows.flatMap((row) => [Number(row[primaryField]) || 0, Number(row[secondaryField]) || 0]), 1);
    const polar = (radius, degrees) => {
      const radians = (Number(degrees) - 90) * Math.PI / 180;
      return [cx + radius * Math.cos(radians), cy + radius * Math.sin(radians)];
    };
    const wedgePath = (r0, r1, start, end) => {
      const large = Number(end) - Number(start) > 180 ? 1 : 0;
      const p1 = polar(r1, start);
      const p2 = polar(r1, end);
      const p3 = polar(r0, end);
      const p4 = polar(r0, start);
      return [
        `M${p1[0].toFixed(1)},${p1[1].toFixed(1)}`,
        `A${r1.toFixed(1)},${r1.toFixed(1)} 0 ${large} 1 ${p2[0].toFixed(1)},${p2[1].toFixed(1)}`,
        `L${p3[0].toFixed(1)},${p3[1].toFixed(1)}`,
        `A${r0.toFixed(1)},${r0.toFixed(1)} 0 ${large} 0 ${p4[0].toFixed(1)},${p4[1].toFixed(1)}`,
        "Z"
      ].join(" ");
    };
    const outerRadius = (innerRadius, baseRadius, span, value, allowInverted, minThickness) => {
      const scaled = baseRadius + ((Number(value) || 0) / (maxValue || 1)) * span;
      if (allowInverted) return scaled;
      return Math.max(innerRadius + minThickness, scaled);
    };
    const rings = (instance.config.rings || [inner, inner + 36, inner + 72, maxR])
      .map((radius) => `<circle class="${escapeHtml(instance.config.ring_class || "ring")}" cx="${cx}" cy="${cy}" r="${Number(radius)}"></circle>`)
      .join("");
    const angleLabels = (instance.config.angle_labels || [0, 90, 180, 270]).map((angle) => {
      const point = polar(maxR + Number(instance.config.angle_label_offset ?? 18), angle);
      return `<text class="${escapeHtml(instance.config.angle_label_class || "angle-label")}" x="${point[0]}" y="${point[1] + 4}" text-anchor="middle">${formatNumber(angle)}${escapeHtml(instance.config.angle_label_suffix || "°")}</text>`;
    }).join("");
    const bars = rows.map((row) => {
      const start = Number(row[startField]);
      const end = Number(row[endField]);
      const primaryR = outerRadius(primaryInner, primaryBase, primarySpan, row[primaryField], primaryAllowInverted, primaryMinThickness);
      const secondaryR = outerRadius(secondaryInner, secondaryBase, secondarySpan, row[secondaryField], secondaryAllowInverted, secondaryMinThickness);
      const primary = `<path class="${escapeHtml(instance.config.primary_bar_class || "ref-bar")}" d="${wedgePath(primaryInner, primaryR, start, end)}"></path>`;
      const secondary = `<path class="${escapeHtml(instance.config.secondary_bar_class || "cur-bar")}" d="${wedgePath(secondaryInner, secondaryR, start, end)}"></path>`;
      const labelField = instance.config.label_field || "label";
      const labelText = row[labelField];
      if (!labelText) return `${secondary}${primary}`;
      const point = polar(maxR + Number(instance.config.label_offset ?? 34), row[midField] ?? ((start + end) / 2));
      const label = `<text class="${escapeHtml(instance.config.label_class || "callout")}" x="${point[0]}" y="${point[1]}" text-anchor="middle">${escapeHtml(labelText)}</text>`;
      return `${secondary}${primary}${label}`;
    }).join("");
    const annotations = (instance.config.annotations || []).map((annotation) => `<text class="${escapeHtml(annotation.class || "callout")}" x="${Number(annotation.x)}" y="${Number(annotation.y)}" text-anchor="${escapeHtml(annotation.anchor || "start")}">${escapeHtml(annotation.text || "")}</text>`).join("");
    return svg(`${rings}${angleLabels}${bars}${annotations}`, `0 0 ${w} ${h}`);
  }

  function renderEventRaster(payload, instance) {
    const rows = dataFor(payload, instance);
    if (!rows.length) return renderCard(payload, instance);
    const xField = instance.config.x_field || instance.config.time_field || "time";
    const [xMinRaw, xMaxRaw] = extent(rows, xField);
    const xMin = Number.isFinite(Number(instance.config.x_min)) ? Number(instance.config.x_min) : xMinRaw;
    const xMax = Number.isFinite(Number(instance.config.x_max)) ? Number(instance.config.x_max) : xMaxRaw;
    const { w, h } = viewBoxFor(instance.config, 472, 185);
    const m = marginFor(instance.config, { t: 22, r: 24, b: 38, l: 48 });
    const x = (value) => m.l + ((Number(value) - xMin) / (xMax - xMin || 1)) * (w - m.l - m.r);
    const rowCount = Number(instance.config.row_count || 4);
    const rowGap = Number(instance.config.row_gap || 27);
    const rowStartY = Number(instance.config.row_start_y ?? m.t);
    const eventClass = instance.config.event_class || "event-mark";
    const hotClass = instance.config.hot_event_class || `${eventClass} hot`;
    const hotGte = Number(instance.config.hot_gte);
    const hotField = instance.config.hot_field;
    const jitterMod = Number(instance.config.jitter_mod || 4);
    const jitterStep = Number(instance.config.jitter_step || 2);
    const y1Offset = Number(instance.config.event_y1_offset ?? 2);
    const y2Offset = Number(instance.config.event_y2_offset ?? 18);
    const rowLines = Array.from({ length: rowCount }, (_, rowIndex) => {
      const y = rowStartY + rowIndex * rowGap;
      const grid = `<line class="grid-line" x1="${m.l}" x2="${w - m.r}" y1="${y + Number(instance.config.grid_y_offset ?? 18)}" y2="${y + Number(instance.config.grid_y_offset ?? 18)}"></line>`;
      const marks = rows.map((row) => {
        const value = Number(row[xField]);
        const jitter = ((value + rowIndex) % jitterMod) * jitterStep;
        const hot = hotField ? Boolean(row[hotField]) : Number.isFinite(hotGte) && value >= hotGte;
        return `<line class="${escapeHtml(hot ? hotClass : eventClass)}" x1="${x(value)}" x2="${x(value)}" y1="${y + y1Offset + jitter}" y2="${y + y2Offset + jitter}"></line>`;
      }).join("");
      return `${grid}${marks}`;
    }).join("");
    const markers = (instance.config.vertical_markers || []).map((marker) => `<line class="${escapeHtml(marker.class || "marker-line")}" x1="${x(marker.x)}" x2="${x(marker.x)}" y1="${Number(marker.y1 ?? m.t)}" y2="${Number(marker.y2 ?? (h - m.b))}"></line>`).join("");
    const xTicks = (instance.config.x_ticks || []).map((tick) => `<text class="axis-tick" x="${x(tick)}" y="${h - m.b + Number(instance.config.x_tick_dy ?? 22)}" text-anchor="middle">${formatNumber(tick)}</text>`).join("");
    const annotations = (instance.config.annotations || []).map((annotation) => `<text class="${escapeHtml(annotation.class || "axis-label")}" x="${x(annotation.x)}" y="${Number(annotation.y)}">${escapeHtml(annotation.text || "")}</text>`).join("");
    const axisLabel = instance.config.x_axis_label ? `<text class="axis-label" x="${Number(instance.config.axis_label_x ?? (m.l + (w - m.l - m.r) / 2))}" y="${Number(instance.config.axis_label_y ?? (h - 6))}" text-anchor="middle">${escapeHtml(instance.config.x_axis_label)}</text>` : "";
    return svg(`${rowLines}${markers}<line class="axis-line" x1="${m.l}" x2="${w - m.r}" y1="${h - m.b}" y2="${h - m.b}"></line>${xTicks}${axisLabel}${annotations}`, `0 0 ${w} ${h}`);
  }

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

  function renderTimeline(payload, instance) {
    const rows = dataFor(payload, instance);
    if (rows.some((row) => row.start !== undefined && row.end !== undefined)) {
      const startField = instance.config.start_field || "start";
      const endField = instance.config.end_field || "end";
      const roleField = instance.config.window_role_field || "role";
      const labelField = instance.config.window_id_field || "window";
      const [xMin, xMax] = [Math.min(...rows.map((row) => Number(row[startField]) || 0)), Math.max(...rows.map((row) => Number(row[endField]) || 1))];
      const { w, h } = viewBoxFor(instance.config, 360, 220);
      const m = marginFor(instance.config, { t: 32, r: 24, b: 38, l: 48 });
      const y0 = Number(instance.config.track_y ?? 86);
      const trackHeight = Number(instance.config.track_height ?? 28);
      const labelMap = instance.config.label_map || {};
      const roleClassMap = instance.config.role_class_map || {};
      const x = (v) => m.l + ((Number(v) - xMin) / (xMax - xMin || 1)) * (w - m.l - m.r);
      if (instance.config.track_field || instance.config.row_field) {
        const trackField = instance.config.track_field || instance.config.row_field;
        const trackOrder = Array.isArray(instance.config.track_order) && instance.config.track_order.length
          ? instance.config.track_order
          : [...new Set(rows.map((row) => row[trackField]))];
        const firstTrackY = Number(instance.config.first_track_y ?? y0);
        const trackGap = Number(instance.config.track_gap ?? 48);
        const trackY = (track) => {
          const index = Math.max(0, trackOrder.findIndex((item) => String(item) === String(track)));
          return firstTrackY + index * trackGap;
        };
        const body = rows.map((row) => {
          const role = String(row[roleField] || "normal");
          const cls = roleClassMap[role] || row.class || (role.includes("drift") ? "state-drift" : role.includes("warn") ? "state-warning" : "state-normal");
          const x0 = x(row[startField]);
          const width = Math.max(8, x(row[endField]) - x0);
          const y = trackY(row[trackField]);
          const rawLabel = String(row[labelField] || role);
          const compactLabel = labelMap[rawLabel] || rawLabel;
          const note = escapeHtml(`${row[trackField]} ${rawLabel}: ${row[startField] ?? ""}-${row[endField] ?? ""}`);
          return `<rect class="${escapeHtml(cls)}" x="${x0}" y="${y}" width="${width}" height="${trackHeight}" rx="5"></rect><text class="label timeline-label timeline-note-link" data-note="${note}" x="${x0 + width / 2}" y="${y + trackHeight * 0.67}" text-anchor="middle">${escapeHtml(compactLabel)}</text>`;
        }).join("");
        const trackLabels = trackOrder.map((track) => `<text class="${escapeHtml(instance.config.track_label_class || "bar-label")}" x="${Number(instance.config.track_label_x ?? (m.l - 12))}" y="${trackY(track) + trackHeight * 0.67}" text-anchor="end">${escapeHtml(track)}</text>`).join("");
        const timelineMarkers = (instance.config.markers || []).map((markerConfig) => {
          const markerX = Number.isFinite(Number(markerConfig.x)) ? x(markerConfig.x) : null;
          if (markerX === null) return "";
          const y1 = Number(markerConfig.y1 ?? m.t);
          const y2 = Number(markerConfig.y2 ?? (h - m.b));
          return `<line class="${escapeHtml(markerConfig.class || "marker-line")}" x1="${markerX}" x2="${markerX}" y1="${y1}" y2="${y2}"></line>`;
        }).join("");
        const xTicks = (instance.config.x_ticks || []).map((tick) => `<text class="axis-tick" x="${x(tick)}" y="${h - m.b + Number(instance.config.x_tick_dy ?? 22)}" text-anchor="middle">${formatNumber(tick)}</text>`).join("");
        const axisLabel = instance.config.axis_label ? `<text class="axis-label" x="${Number(instance.config.axis_label_x ?? (m.l + (w - m.l - m.r) / 2))}" y="${Number(instance.config.axis_label_y ?? (h - 6))}" text-anchor="middle">${escapeHtml(instance.config.axis_label)}</text>` : "";
        return svg(`${trackLabels}${body}${timelineMarkers}<line class="axis-line" x1="${m.l}" x2="${w - m.r}" y1="${h - m.b}" y2="${h - m.b}"></line>${xTicks}${axisLabel}`, `0 0 ${w} ${h}`);
      }
      const body = rows.map((row) => {
        const role = String(row[roleField] || "normal");
        const cls = roleClassMap[role] || (role.includes("drift") ? "state-drift" : role.includes("warn") ? "state-warning" : "state-normal");
        const x0 = x(row[startField]);
        const width = Math.max(8, x(row[endField]) - x0);
        const rawLabel = String(row[labelField] || role);
        const compactLabel = labelMap[rawLabel] || rawLabel;
        const note = escapeHtml(`${rawLabel}: ${row.start ?? ""}-${row.end ?? ""}`);
        return `<rect class="${cls}" x="${x0}" y="${y0}" width="${width}" height="${trackHeight}" rx="5"></rect><text class="label timeline-label timeline-note-link" data-note="${note}" x="${x0 + width / 2}" y="${y0 + trackHeight * 0.67}" text-anchor="middle">${escapeHtml(compactLabel)}</text>`;
      }).join("");
      const trackOverlays = (instance.config.track_overlays || []).map((overlay) => {
        const x0 = x(overlay.x0);
        const x1 = x(overlay.x1);
        const overlayY = Number(overlay.y ?? y0 - 22);
        const overlayHeight = Number(overlay.height ?? 12);
        const cls = overlay.class || "state-warning";
        const label = overlay.label
          ? `<text class="${escapeHtml(overlay.label_class || "bar-label")}" x="${(x0 + x1) / 2}" y="${overlayY + Number(overlay.label_dy ?? overlayHeight - 2)}" text-anchor="middle">${escapeHtml(overlay.label)}</text>`
          : "";
        return `<rect class="${escapeHtml(cls)}" x="${Math.min(x0, x1)}" y="${overlayY}" width="${Math.abs(x1 - x0)}" height="${overlayHeight}" rx="${Number(overlay.rx ?? 4)}"></rect>${label}`;
      }).join("");
      const timelineMarkers = (instance.config.markers || []).map((markerConfig) => {
        const markerPositionField = markerConfig.position_field || instance.config.marker_position_field || startField;
        const markerRow = markerConfig.role ? rows.find((row) => String(row[roleField] || row[labelField] || "") === markerConfig.role) : null;
        const markerX = markerRow ? x(markerRow[markerPositionField]) : Number.isFinite(Number(markerConfig.x)) ? x(markerConfig.x) : null;
        if (markerX === null) return "";
        return `<line class="${escapeHtml(markerConfig.class || "marker-line")}" x1="${markerX}" x2="${markerX}" y1="${m.t}" y2="${h - m.b}"></line>${markerConfig.circle ? `<circle class="${escapeHtml(markerConfig.circle_class || "replace-point")}" cx="${markerX}" cy="${y0 + trackHeight / 2}" r="${Number(markerConfig.radius) || 6}"></circle>` : ""}`;
      }).join("");
      const markerRole = instance.config.marker_role;
      const markerPositionField = instance.config.marker_position_field || startField;
      const markerRow = !timelineMarkers && markerRole ? rows.find((row) => String(row[roleField] || row[labelField] || "") === markerRole) : null;
      const markerX = markerRow ? x(markerRow[markerPositionField]) : null;
      const marker = timelineMarkers || (markerX === null ? "" : `<line class="marker-line" x1="${markerX}" x2="${markerX}" y1="${m.t}" y2="${h - m.b}"></line>${instance.config.marker_circle ? `<circle class="replace-point" cx="${markerX}" cy="${y0 + trackHeight / 2}" r="${Number(instance.config.marker_radius) || 6}"></circle>` : ""}`);
      const axisLabel = instance.config.axis_label ? `<text class="axis-label" x="${Number(instance.config.axis_label_x ?? (m.l + (w - m.l - m.r) / 2))}" y="${Number(instance.config.axis_label_y ?? (h - 6))}" text-anchor="middle">${escapeHtml(instance.config.axis_label)}</text>` : "";
      const xTicks = (instance.config.x_ticks || []).map((tick) => `<text class="axis-tick" x="${x(tick)}" y="${h - m.b + Number(instance.config.x_tick_dy ?? 22)}" text-anchor="middle">${formatNumber(tick)}</text>`).join("");
      return svg(`${trackOverlays}${body}${marker}<line class="axis-line" x1="${m.l}" x2="${w - m.r}" y1="${h - m.b}" y2="${h - m.b}"></line>${xTicks}${axisLabel}`, `0 0 ${w} ${h}`);
    }
    return svg(rows.map((row, i) => {
      const role = row.role || row.state || "normal";
      const cls = role.includes("drift") || role.includes("alarm") ? "state-drift" : role.includes("warn") || role.includes("current") ? "state-warning" : "state-normal";
      return `<rect class="${cls}" x="${36 + i * 72}" y="86" width="62" height="28" rx="5"></rect><text class="label" x="${67 + i * 72}" y="105" text-anchor="middle">${escapeHtml(row.window || row.state || role)}</text>`;
    }).join(""));
  }

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

  function renderTable(payload, instance) {
    const rows = dataFor(payload, instance);
    return `<table style="width:100%;border-collapse:collapse;font-size:12px">${rows.slice(0, 5).map((row) => `<tr><td style="padding:6px;border-bottom:1px solid #d7dde4">${escapeHtml(row.metric || "metric")}</td><td style="padding:6px;border-bottom:1px solid #d7dde4;text-align:right">${Number(row.current || row.value || 0).toFixed(2)}</td></tr>`).join("")}</table>`;
  }

  function renderCard(payload, instance) {
    const rows = dataFor(payload, instance);
    if (instance.config.card_style === "notes_legend") {
      const note = rows[0] || {};
      const legend = Array.isArray(note.legend) ? note.legend : [];
      return `<section class="notes-card">
        <div>
          <h2>${escapeHtml(note.title || instance.config.title || "")}</h2>
          <p>${escapeHtml(note.text || instance.config.text || "")}</p>
        </div>
        <div class="legend-list">${legend.map((item) => `<span><i class="${escapeHtml(item.class || "swatch")}"></i>${escapeHtml(item.label || "")}</span>`).join("")}</div>
      </section>`;
    }
    if (instance.componentType === "decision_card" && instance.config.card_style === "test_cards") {
      const { w, h } = viewBoxFor(instance.config, 472, 185);
      const cardWidth = Number(instance.config.card_width || 196);
      const cardHeight = Number(instance.config.card_height || 108);
      const startX = Number(instance.config.start_x || 28);
      const startY = Number(instance.config.start_y || 34);
      const gap = Number(instance.config.card_gap || 22);
      const body = rows.map((row, i) => {
        const x0 = startX + i * (cardWidth + gap);
        const cls = row.class || row.status_class || (i === 0 ? "decision-pass" : "decision-fail");
        const decisionClass = row.decision_class || (i === 0 ? "callout-upper" : "callout-lower");
        return `<rect class="${escapeHtml(cls)}" x="${x0}" y="${startY}" width="${cardWidth}" height="${cardHeight}" rx="8"></rect>
          <text class="card-title" x="${x0 + 16}" y="${startY + 24}">${escapeHtml(row.title || "")}</text>
          <text class="card-text" x="${x0 + 16}" y="${startY + 50}">${escapeHtml(row.hypothesis || "")}</text>
          <text class="card-text" x="${x0 + 16}" y="${startY + 72}">${escapeHtml(row.stat || "")}</text>
          <text class="${escapeHtml(decisionClass)}" x="${x0 + 16}" y="${startY + 94}">${escapeHtml(row.decision || "")}</text>`;
      }).join("");
      const caption = instance.config.caption ? `<text class="axis-label" x="${w / 2}" y="${h - 15}" text-anchor="middle">${escapeHtml(instance.config.caption)}</text>` : "";
      return svg(`${body}${caption}`, `0 0 ${w} ${h}`);
    }
    if (instance.componentType === "decision_card" && rows.length) {
      return `<div class="summary-grid">${rows.map((row) => {
        const value = row.displayValue ?? row.display_value;
        const numericValue = Number(row.value);
        const formatted = value !== undefined
          ? value
          : typeof row.value === "string"
            ? row.value
          : Number.isFinite(numericValue)
            ? numericValue.toFixed(numericValue < 1 ? 2 : 0)
            : row.value ?? "";
        const formattedText = String(formatted);
        const compactClass = formattedText.length > 12 ? " summary-metric-tiny" : formattedText.length > 6 ? " summary-metric-long" : "";
        return `<section class="summary-metric${compactClass}"><span>${escapeHtml(row.label || "metric")}</span><strong>${escapeHtml(formattedText)}</strong></section>`;
      }).join("")}</div>`;
    }
    return svg(`<rect x="18" y="18" width="324" height="176" rx="8" fill="#f8fafb" stroke="#d7dde4"></rect><text class="value" x="34" y="60">${escapeHtml(instance.componentType)}</text><text class="label" x="34" y="86">${escapeHtml(instance.config.visual_code || instance.config.label || "component summary")}</text>`);
  }


  // Popup and viewer interaction helpers.
  function bindNotePopup(componentChart) {
    if (componentChart.dataset.chartRuntimeNoteBound === "true") return;
    componentChart.dataset.chartRuntimeNoteBound = "true";
    componentChart.addEventListener("click", (event) => {
      const zoomTarget = event.target.closest(".area-zoom-link");
      if (zoomTarget) {
        const payload = componentChart.__chartRuntimePayload;
        const areaName = zoomTarget.dataset.area;
        if (payload && areaName) showComponentZoomPopup(payload, areaName);
        return;
      }
      const target = event.target.closest(".timeline-note-link, .note-link, .component-note-link, .chart-note-link");
      if (!target) return;
      showNotePopup(target.dataset.note || target.textContent || "");
    });
  }

  function buildZoomPayload(payload, areaName) {
    const sourceArea = (payload.layout?.areas || []).find((area) => area.area === areaName) || { area: areaName };
    const area = {
      ...sourceArea,
      area: "zoom",
      x: 0,
      y: 0,
      w: 1,
      h: 1,
      role: sourceArea.role || "primary_visual",
      headerHeight: sourceArea.title || sourceArea.description ? Math.max(48, Number(sourceArea.headerHeight || 54)) : 0,
      stageInset: {
        top: sourceArea.title || sourceArea.description ? Math.max(58, Number(sourceArea.headerHeight || 54) + 10) : 14,
        right: 18,
        bottom: 18,
        left: 18
      }
    };
    const components = (payload.components || [])
      .filter((component) => component.area === areaName)
      .map((component) => ({ ...component, area: "zoom" }));
    return {
      ...payload,
      chartId: `${payload.chartId || "chart"}:${areaName}`,
      title: sourceArea.title || payload.title || payload.chartId || "Component",
      layout: {
        layoutType: "component_zoom",
        columns: 1,
        rows: 1,
        gridTemplateColumns: "1fr",
        gridTemplateRows: "1fr",
        gap: "0",
        showAreaLabels: false,
        areas: [area]
      },
      components,
      data: payload.data || {}
    };
  }

  function showComponentZoomPopup(payload, areaName) {
    let popup = document.getElementById("componentZoomPopup");
    if (!popup) {
      popup = document.createElement("div");
      popup.id = "componentZoomPopup";
      popup.className = "component-zoom-popup";
      popup.hidden = true;
      popup.innerHTML = `
        <section class="component-zoom-panel" role="dialog" aria-modal="true" aria-labelledby="componentZoomTitle">
          <header class="component-zoom-head">
            <div>
              <p class="eyebrow">component zoom</p>
              <h2 id="componentZoomTitle"></h2>
            </div>
            <button class="open-link component-zoom-close" type="button">닫기</button>
          </header>
          <div id="componentZoomChart" class="component-chart component-zoom-chart"></div>
        </section>`;
      popup.addEventListener("click", (event) => {
        if (event.target === popup || event.target.closest(".component-zoom-close")) closeComponentZoomPopup();
      });
      document.addEventListener("keydown", (event) => {
        if (event.key === "Escape" && popup && !popup.hidden) closeComponentZoomPopup();
      });
      document.body.appendChild(popup);
    }
    const sourceArea = (payload.layout?.areas || []).find((area) => area.area === areaName) || {};
    const title = sourceArea.title || areaName;
    popup.querySelector("#componentZoomTitle").textContent = `${payload.chartId || "chart"} - ${title}`;
    popup.hidden = false;
    renderChartPayload(popup.querySelector("#componentZoomChart"), buildZoomPayload(payload, areaName));
    popup.querySelector(".component-zoom-close").focus();
  }

  function closeComponentZoomPopup() {
    const popup = document.getElementById("componentZoomPopup");
    if (!popup) return;
    popup.hidden = true;
    const chart = popup.querySelector("#componentZoomChart");
    if (chart) chart.innerHTML = "";
  }

  function showNotePopup(text) {
    let popup = document.getElementById("chartNotePopup");
    if (!popup) {
      popup = document.createElement("div");
      popup.id = "chartNotePopup";
      popup.className = "note-popup";
      popup.innerHTML = '<div class="note-popup-panel"><button class="note-popup-close" type="button">닫기</button><div class="note-popup-body"></div></div>';
      popup.addEventListener("click", (event) => {
        if (event.target === popup || event.target.closest(".note-popup-close")) popup.hidden = true;
      });
      document.body.appendChild(popup);
    }
    popup.querySelector(".note-popup-body").textContent = text;
    popup.hidden = false;
  }

  // Browser global API.
  // @managed-contract contract_id=chart_runtime.window.ChartRuntime level=P0
  window.ChartRuntime = {
    renderChartPayload,
    showNotePopup,
    showComponentZoomPopup
  };
})();
