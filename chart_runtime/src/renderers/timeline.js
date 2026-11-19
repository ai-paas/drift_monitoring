/*
 * Source candidate for medium-size renderers.
 *
 * This file is not imported by chart_runtime.js yet. Until a build step is
 * introduced, chart_runtime.js remains the browser artifact and source of truth.
 */

function createTimelineRenderers(deps) {
  const {
    dataFor,
    escapeHtml,
    formatNumber,
    marginFor,
    svg,
    viewBoxFor
  } = deps;
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

  return Object.freeze({
    renderTimeline
  });
}

if (typeof module !== "undefined") {
  module.exports = { createTimelineRenderers };
}
