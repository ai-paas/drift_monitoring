(function () {
  const referencePoints = [
    [-2.1, -0.5], [-1.8, -0.1], [-1.5, -0.8], [-1.2, 0.2], [-1.0, -0.4],
    [-0.7, 0.4], [-0.5, -0.2], [-0.2, 0.1], [0.0, -0.5], [0.2, 0.4],
    [0.5, -0.1], [0.7, 0.5], [0.9, -0.4], [1.0, 0.2], [1.2, 0.7],
    [-1.4, 0.9], [-0.9, 1.1], [-0.1, 1.0], [0.6, 1.2], [1.2, 1.3]
  ];
  const currentPoints = [
    [-0.8, 0.1], [-0.5, 0.8], [-0.2, 1.3], [0.1, 0.5], [0.4, 1.7],
    [0.8, 0.9], [1.0, 1.8], [1.4, 1.1], [1.8, 1.7], [2.1, 0.8],
    [2.3, 1.9], [2.6, 1.2], [2.8, 2.1], [3.0, 1.4], [3.2, 2.3],
    [0.5, 2.4], [1.1, 2.7], [1.9, 2.8], [2.6, 2.9], [3.1, 2.8]
  ];
  const trend = [0.05, 0.06, 0.07, 0.08, 0.10, 0.14, 0.19, 0.25, 0.31, 0.36];
  const threshold = 0.18;
  const nullBins = [
    { label: "0.02", value: 5 }, { label: "0.04", value: 12 }, { label: "0.06", value: 22 },
    { label: "0.08", value: 28 }, { label: "0.10", value: 24 }, { label: "0.12", value: 16 },
    { label: "0.14", value: 9 }, { label: "0.16", value: 5 }, { label: "0.18", value: 2 },
    { label: "0.20", value: 1 }
  ];
  const observed = 0.36;
  const pValue = 0.008;
  const bandwidth = 1.20;

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
      ["MMD score", observed.toFixed(2)],
      ["Permutation p-value", pValue.toFixed(3)],
      ["Kernel bandwidth", bandwidth.toFixed(2)]
    ];
    document.getElementById("summary").innerHTML = rows.map(([label, value]) => `<div class="metric"><div class="label">${label}</div><div class="value">${value}</div></div>`).join("");
  }

  function drawEmbedding() {
    const svg = document.getElementById("embeddingChart");
    const w = 630, h = 440;
    const margin = { top: 24, right: 28, bottom: 62, left: 58 };
    const x = scale(-2.5, 3.5, margin.left, w - margin.right);
    const y = scale(-1.2, 3.2, h - margin.bottom, margin.top);
    const plotW = w - margin.left - margin.right;
    const plotH = h - margin.top - margin.bottom;
    svg.setAttribute("viewBox", `0 0 ${w} ${h}`);

    for (const t of [-2, -1, 0, 1, 2, 3]) {
      svg.appendChild(svgEl("line", { class: "grid-line", x1: x(t), x2: x(t), y1: margin.top, y2: margin.top + plotH }));
      text(svg, t.toString(), x(t), h - margin.bottom + 24, { class: "tick-text", "text-anchor": "middle" });
    }
    for (const t of [-1, 0, 1, 2, 3]) {
      svg.appendChild(svgEl("line", { class: "grid-line", x1: margin.left, x2: margin.left + plotW, y1: y(t), y2: y(t) }));
      text(svg, t.toString(), margin.left - 12, y(t) + 4, { class: "tick-text", "text-anchor": "end" });
    }
    svg.appendChild(svgEl("line", { class: "axis-line", x1: margin.left, x2: margin.left + plotW, y1: h - margin.bottom, y2: h - margin.bottom }));
    svg.appendChild(svgEl("line", { class: "axis-line", x1: margin.left, x2: margin.left, y1: margin.top, y2: h - margin.bottom }));
    svg.appendChild(svgEl("ellipse", { class: "ref-kernel", cx: x(-0.4), cy: y(0.25), rx: 185, ry: 102, transform: `rotate(12 ${x(-0.4)} ${y(0.25)})` }));
    svg.appendChild(svgEl("ellipse", { class: "cur-kernel", cx: x(1.55), cy: y(1.75), rx: 178, ry: 114, transform: `rotate(18 ${x(1.55)} ${y(1.75)})` }));
    referencePoints.forEach(([px, py]) => svg.appendChild(svgEl("circle", { class: "ref-point", cx: x(px), cy: y(py), r: 5 })));
    currentPoints.forEach(([px, py]) => svg.appendChild(svgEl("circle", { class: "cur-point", cx: x(px), cy: y(py), r: 5 })));
    svg.appendChild(svgEl("line", { class: "threshold-line", x1: x(-0.4), y1: y(0.25), x2: x(1.55), y2: y(1.75) }));
    text(svg, "embedding 1", margin.left + plotW / 2, h - 12, { class: "axis-label", "text-anchor": "middle" });
    text(svg, "embedding 2", 16, margin.top + 178, { class: "axis-label", "text-anchor": "middle", transform: `rotate(-90 16 ${margin.top + 178})` });
    text(svg, "kernel mean embedding 차이 확대", x(1.0), y(3.0), { class: "callout" });
  }

  function drawTrend() {
    const svg = document.getElementById("trendChart");
    const w = 472, h = 185;
    const margin = { top: 12, right: 22, bottom: 34, left: 48 };
    const x = scale(1, trend.length, margin.left, w - margin.right);
    const y = scale(0, 0.42, h - margin.bottom, margin.top);
    const plotW = w - margin.left - margin.right;
    svg.setAttribute("viewBox", `0 0 ${w} ${h}`);

    for (const t of [0, 0.10, 0.20, 0.30, 0.40]) {
      svg.appendChild(svgEl("line", { class: "grid-line", x1: margin.left, x2: margin.left + plotW, y1: y(t), y2: y(t) }));
      text(svg, t.toFixed(2), margin.left - 10, y(t) + 4, { class: "tick-text", "text-anchor": "end" });
    }
    svg.appendChild(svgEl("line", { class: "threshold-line", x1: margin.left, x2: margin.left + plotW, y1: y(threshold), y2: y(threshold) }));
    const pts = trend.map((v, i) => [x(i + 1), y(v)]);
    svg.appendChild(svgEl("path", { class: "mmd-line", d: linePath(pts) }));
    pts.forEach(([cx, cy], i) => svg.appendChild(svgEl("circle", { class: "mmd-point", cx, cy, r: i >= 6 ? 4.8 : 4 })));
    svg.appendChild(svgEl("line", { class: "axis-line", x1: margin.left, x2: margin.left + plotW, y1: h - margin.bottom, y2: h - margin.bottom }));
    text(svg, "window", margin.left + plotW / 2, h - 8, { class: "axis-label", "text-anchor": "middle" });
    text(svg, "관리 기준 0.18", w - margin.right - 92, y(threshold) - 6, { class: "warning" });
  }

  function drawNull() {
    const svg = document.getElementById("nullChart");
    const w = 472, h = 185;
    const margin = { top: 8, right: 26, bottom: 34, left: 48 };
    const maxValue = Math.max(...nullBins.map(r => r.value));
    const x = scale(0, nullBins.length, margin.left, w - margin.right);
    const y = scale(0, maxValue * 1.2, h - margin.bottom, margin.top);
    const obsX = scale(0.02, 0.38, margin.left, w - margin.right)(observed);
    svg.setAttribute("viewBox", `0 0 ${w} ${h}`);

    nullBins.forEach((row, i) => {
      const barX = x(i) + 4;
      const barW = x(i + 1) - x(i) - 8;
      const barH = h - margin.bottom - y(row.value);
      svg.appendChild(svgEl("rect", { class: i >= 7 ? "tail-bar" : "null-bar", x: barX, y: y(row.value), width: barW, height: barH, rx: 3 }));
      if (i % 2 === 0) text(svg, row.label, barX + barW / 2, h - margin.bottom + 20, { class: "tick-text", "text-anchor": "middle" });
    });
    svg.appendChild(svgEl("line", { class: "observed-line", x1: obsX, x2: obsX, y1: margin.top, y2: h - margin.bottom }));
    svg.appendChild(svgEl("line", { class: "axis-line", x1: margin.left, x2: w - margin.right, y1: h - margin.bottom, y2: h - margin.bottom }));
    text(svg, "observed 0.36", obsX - 4, margin.top + 14, { class: "warning", "text-anchor": "end" });
    text(svg, `p=${pValue.toFixed(3)}`, obsX - 4, margin.top + 31, { class: "warning", "text-anchor": "end" });
    text(svg, "permutation MMD score", margin.left + 168, h - 6, { class: "axis-label", "text-anchor": "middle" });
  }

  drawSummary();
  drawEmbedding();
  drawTrend();
  drawNull();
})();
