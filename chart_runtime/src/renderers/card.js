/*
 * Source candidate for card renderers and fallback components.
 *
 * This file is not imported by chart_runtime.js yet. Until a build step is
 * introduced, chart_runtime.js remains the browser artifact and source of truth.
 */

function createCardRenderers(deps) {
  const {
    dataFor,
    escapeHtml,
    svg,
    viewBoxFor
  } = deps;

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

  return Object.freeze({
    renderCard
  });
}

if (typeof module !== "undefined") {
  module.exports = { createCardRenderers };
}
