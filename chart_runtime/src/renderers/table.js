/*
 * Source candidate for table renderers.
 *
 * This file is not imported by chart_runtime.js yet. Until a build step is
 * introduced, chart_runtime.js remains the browser artifact and source of truth.
 */

function createTableRenderers(deps) {
  const { dataFor, escapeHtml } = deps;

  function renderTable(payload, instance) {
    const rows = dataFor(payload, instance);
    return `<table style="width:100%;border-collapse:collapse;font-size:12px">${rows.slice(0, 5).map((row) => `<tr><td style="padding:6px;border-bottom:1px solid #d7dde4">${escapeHtml(row.metric || "metric")}</td><td style="padding:6px;border-bottom:1px solid #d7dde4;text-align:right">${Number(row.current || row.value || 0).toFixed(2)}</td></tr>`).join("")}</table>`;
  }

  return Object.freeze({
    renderTable
  });
}

if (typeof module !== "undefined") {
  module.exports = { createTableRenderers };
}
