(function () {
  const error = [0.07,0.08,0.09,0.08,0.10,0.09,0.11,0.10,0.12,0.13,0.12,0.14,0.15,0.16,0.18,0.19,0.21,0.24,0.26,0.28,0.30,0.32,0.34,0.37,0.40,0.42,0.43,0.36,0.33,0.31,0.30,0.29];
  const retained = [60,64,68,72,76,80,84,88,92,96,100,104,108,112,116,120,124,128,132,136,140,144,148,152,156,44,48,52,58,64,70,76];
  const warning = 0.28;
  const drift = 0.38;
  const warningIndex = 20;
  const driftIndex = 25;
  const resetIndex = 26;

  function scale(d0, d1, r0, r1) {
    return (v) => r0 + (v - d0) / (d1 - d0) * (r1 - r0);
  }
  function svgEl(tag, attrs = {}) {
    const el = document.createElementNS("http://www.w3.org/2000/svg", tag);
    for (const [k, v] of Object.entries(attrs)) el.setAttribute(k, v);
    return el;
  }
  function text(svg, value, x, y, attrs = {}) {
    const el = svgEl("text", { x, y, ...attrs });
    el.textContent = value;
    svg.appendChild(el);
  }
  function linePath(points) {
    return points.map((p, i) => `${i ? "L" : "M"}${p[0].toFixed(2)},${p[1].toFixed(2)}`).join(" ");
  }

  function drawSummary() {
    const rows = [
      ["warning start", `t=${warningIndex}`],
      ["reactive reset", `t=${resetIndex}`],
      ["retained window", "44"]
    ];
    document.getElementById("summary").innerHTML = rows.map(([label, value]) => `<div class="metric"><div class="label">${label}</div><div class="value">${value}</div></div>`).join("");
  }

  function drawErrorTrend() {
    const svg = document.getElementById("errorTrend");
    const w = 630, h = 440;
    const margin = { top: 24, right: 28, bottom: 62, left: 58 };
    const x = scale(1, error.length, margin.left, w - margin.right);
    const y = scale(0, 0.50, h - margin.bottom, margin.top);
    const plotW = w - margin.left - margin.right;
    svg.setAttribute("viewBox", `0 0 ${w} ${h}`);
    for (const t of [0, 0.1, 0.2, 0.3, 0.4, 0.5]) {
      svg.appendChild(svgEl("line", { class: "grid-line", x1: margin.left, x2: margin.left + plotW, y1: y(t), y2: y(t) }));
      text(svg, t.toFixed(1), margin.left - 12, y(t) + 4, { class: "tick-text", "text-anchor": "end" });
    }
    svg.appendChild(svgEl("line", { class: "warning-line", x1: margin.left, x2: margin.left + plotW, y1: y(warning), y2: y(warning) }));
    svg.appendChild(svgEl("line", { class: "drift-line", x1: margin.left, x2: margin.left + plotW, y1: y(drift), y2: y(drift) }));
    svg.appendChild(svgEl("path", { class: "error-line", d: linePath(error.map((v, i) => [x(i + 1), y(v)])) }));
    error.forEach((v, i) => {
      if (i % 3 === 0 || i + 1 >= warningIndex) {
        svg.appendChild(svgEl("circle", { class: i + 1 >= driftIndex && i + 1 <= resetIndex ? "drift-point" : "error-point", cx: x(i + 1), cy: y(v), r: i + 1 >= driftIndex && i + 1 <= resetIndex ? 5 : 3.5 }));
      }
    });
    for (const idx of [warningIndex, driftIndex, resetIndex]) {
      svg.appendChild(svgEl("line", { class: "reset-line", x1: x(idx), x2: x(idx), y1: margin.top, y2: h - margin.bottom, opacity: idx === warningIndex ? "0.7" : "1" }));
    }
    svg.appendChild(svgEl("line", { class: "axis-line", x1: margin.left, x2: margin.left + plotW, y1: h - margin.bottom, y2: h - margin.bottom }));
    svg.appendChild(svgEl("line", { class: "axis-line", x1: margin.left, x2: margin.left, y1: margin.top, y2: h - margin.bottom }));
    for (const t of [1, 8, 16, 24, 32]) {
      text(svg, t.toString(), x(t), h - margin.bottom + 24, { class: "tick-text", "text-anchor": "middle" });
    }
    text(svg, "time index", margin.left + plotW / 2, h - 12, { class: "axis-label", "text-anchor": "middle" });
    text(svg, "error rate", 16, margin.top + 178, { class: "axis-label", "text-anchor": "middle", transform: `rotate(-90 16 ${margin.top + 178})` });
    text(svg, "warning", x(4), y(warning) - 8, { class: "warning-text" });
    text(svg, "drift", x(4), y(drift) - 8, { class: "drift-text" });
    text(svg, "reactive reset", x(resetIndex) + 8, y(0.47), { class: "drift-text" });
  }

  function drawWindow() {
    const svg = document.getElementById("windowChart");
    const w = 472, h = 185;
    const margin = { top: 12, right: 22, bottom: 34, left: 48 };
    const x = scale(1, retained.length, margin.left, w - margin.right);
    const y = scale(30, 170, h - margin.bottom, margin.top);
    const plotW = w - margin.left - margin.right;
    svg.setAttribute("viewBox", `0 0 ${w} ${h}`);
    for (const t of [40, 80, 120, 160]) {
      svg.appendChild(svgEl("line", { class: "grid-line", x1: margin.left, x2: margin.left + plotW, y1: y(t), y2: y(t) }));
      text(svg, t.toString(), margin.left - 10, y(t) + 4, { class: "tick-text", "text-anchor": "end" });
    }
    svg.appendChild(svgEl("path", { class: "window-line", d: linePath(retained.map((v, i) => [x(i + 1), y(v)])) }));
    svg.appendChild(svgEl("line", { class: "reset-line", x1: x(resetIndex), x2: x(resetIndex), y1: margin.top, y2: h - margin.bottom }));
    retained.forEach((v, i) => {
      if (i % 4 === 0 || i + 1 === resetIndex) svg.appendChild(svgEl("circle", { class: "window-point", cx: x(i + 1), cy: y(v), r: i + 1 === resetIndex ? 5 : 3.5 }));
    });
    svg.appendChild(svgEl("line", { class: "axis-line", x1: margin.left, x2: margin.left + plotW, y1: h - margin.bottom, y2: h - margin.bottom }));
    text(svg, "retained window size", margin.left + 160, h - 8, { class: "axis-label", "text-anchor": "middle" });
    text(svg, "reset 후 축소", x(resetIndex) + 8, y(58), { class: "retained-text" });
  }

  function drawComparison() {
    const svg = document.getElementById("comparisonChart");
    const w = 472, h = 185;
    const margin = { top: 24, right: 24, bottom: 34, left: 82 };
    const x = scale(1, 32, margin.left, w - margin.right);
    svg.setAttribute("viewBox", `0 0 ${w} ${h}`);
    const rows = [
      { name: "DDM", y: 48, segments: [["normal", 1, 20, "normal-fill"], ["warning", 20, 25, "warning-fill"], ["reset", 25, 32, "ddm-fill"]] },
      { name: "RDDM", y: 104, segments: [["normal", 1, 20, "normal-fill"], ["retain", 20, 26, "retained-fill"], ["reactive", 26, 32, "drift-fill"]] }
    ];
    for (const row of rows) {
      text(svg, row.name, margin.left - 12, row.y + 20, { class: "bar-label", "text-anchor": "end" });
      for (const [label, start, end, cls] of row.segments) {
        svg.appendChild(svgEl("rect", { class: cls, x: x(start), y: row.y, width: x(end) - x(start), height: 30, rx: 5 }));
        text(svg, label, x((start + end) / 2), row.y + 20, { class: "bar-label", "text-anchor": "middle" });
      }
    }
    svg.appendChild(svgEl("line", { class: "reset-line", x1: x(resetIndex), x2: x(resetIndex), y1: margin.top, y2: 148 }));
    svg.appendChild(svgEl("line", { class: "axis-line", x1: margin.left, x2: w - margin.right, y1: h - margin.bottom, y2: h - margin.bottom }));
    for (const t of [1, 8, 16, 24, 32]) {
      text(svg, t.toString(), x(t), h - margin.bottom + 22, { class: "tick-text", "text-anchor": "middle" });
    }
    text(svg, "RDDM keeps warning data before reactive reset", margin.left + 170, h - 6, { class: "axis-label", "text-anchor": "middle" });
  }

  drawSummary();
  drawErrorTrend();
  drawWindow();
  drawComparison();
})();
