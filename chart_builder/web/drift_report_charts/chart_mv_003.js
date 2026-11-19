(function () {
  const xBins = [-2, -1, 0, 1, 2, 3];
  const yBins = [-1, 0, 1, 2, 3];
  const diffGrid = [
    [-0.18, -0.22, -0.12, 0.02, 0.08, 0.05],
    [-0.24, -0.30, -0.18, 0.05, 0.15, 0.10],
    [-0.12, -0.16, -0.04, 0.18, 0.34, 0.22],
    [0.02, 0.04, 0.15, 0.32, 0.48, 0.36],
    [0.04, 0.08, 0.18, 0.28, 0.40, 0.30]
  ];
  const trend = [0.04, 0.05, 0.06, 0.07, 0.09, 0.13, 0.18, 0.24, 0.30, 0.34];
  const threshold = 0.17;
  const nullBins = [
    { label: "0.03", value: 6 }, { label: "0.05", value: 14 }, { label: "0.07", value: 25 },
    { label: "0.09", value: 30 }, { label: "0.11", value: 22 }, { label: "0.13", value: 13 },
    { label: "0.15", value: 7 }, { label: "0.17", value: 3 }, { label: "0.19", value: 1 },
    { label: "0.21", value: 1 }
  ];
  const observed = 0.34;
  const pValue = 0.010;
  const maxDensityDelta = 0.48;

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
  function diffColor(value) {
    const a = Math.min(0.72, 0.18 + Math.abs(value) * 1.1);
    return value >= 0 ? `rgba(185, 90, 80, ${a})` : `rgba(47, 111, 159, ${a})`;
  }

  function drawSummary() {
    const rows = [
      ["LSDD score", observed.toFixed(2)],
      ["Permutation p-value", pValue.toFixed(3)],
      ["최대 밀도 delta", `+${maxDensityDelta.toFixed(2)}`]
    ];
    document.getElementById("summary").innerHTML = rows.map(([label, value]) => `<div class="metric"><div class="label">${label}</div><div class="value">${value}</div></div>`).join("");
  }

  function drawHeatmap() {
    const svg = document.getElementById("heatmapChart");
    const w = 630, h = 440;
    const margin = { top: 24, right: 34, bottom: 62, left: 58 };
    const plotW = w - margin.left - margin.right;
    const plotH = h - margin.top - margin.bottom;
    const cellW = plotW / xBins.length;
    const cellH = plotH / yBins.length;
    const x = scale(-2, 3, margin.left + cellW / 2, margin.left + plotW - cellW / 2);
    const y = scale(-1, 3, h - margin.bottom - cellH / 2, margin.top + cellH / 2);
    svg.setAttribute("viewBox", `0 0 ${w} ${h}`);

    diffGrid.forEach((row, rowIndex) => {
      row.forEach((value, colIndex) => {
        svg.appendChild(svgEl("rect", {
          x: margin.left + colIndex * cellW,
          y: margin.top + (diffGrid.length - 1 - rowIndex) * cellH,
          width: cellW,
          height: cellH,
          fill: diffColor(value)
        }));
      });
    });
    for (let i = 0; i <= xBins.length; i++) {
      svg.appendChild(svgEl("line", { class: "grid-line", x1: margin.left + i * cellW, x2: margin.left + i * cellW, y1: margin.top, y2: margin.top + plotH }));
    }
    for (let i = 0; i <= yBins.length; i++) {
      svg.appendChild(svgEl("line", { class: "grid-line", x1: margin.left, x2: margin.left + plotW, y1: margin.top + i * cellH, y2: margin.top + i * cellH }));
    }
    svg.appendChild(svgEl("ellipse", { class: "contour-decrease", cx: x(-1.1), cy: y(0.0), rx: 130, ry: 84, transform: `rotate(-12 ${x(-1.1)} ${y(0.0)})` }));
    svg.appendChild(svgEl("ellipse", { class: "contour-increase", cx: x(1.9), cy: y(2.1), rx: 142, ry: 92, transform: `rotate(18 ${x(1.9)} ${y(2.1)})` }));
    xBins.forEach(v => text(svg, v.toString(), x(v), h - margin.bottom + 24, { class: "tick-text", "text-anchor": "middle" }));
    yBins.forEach(v => text(svg, v.toString(), margin.left - 12, y(v) + 4, { class: "tick-text", "text-anchor": "end" }));
    svg.appendChild(svgEl("line", { class: "axis-line", x1: margin.left, x2: margin.left + plotW, y1: h - margin.bottom, y2: h - margin.bottom }));
    svg.appendChild(svgEl("line", { class: "axis-line", x1: margin.left, x2: margin.left, y1: margin.top, y2: h - margin.bottom }));
    text(svg, "embedding 1", margin.left + plotW / 2, h - 12, { class: "axis-label", "text-anchor": "middle" });
    text(svg, "embedding 2", 16, margin.top + 178, { class: "axis-label", "text-anchor": "middle", transform: `rotate(-90 16 ${margin.top + 178})` });
    text(svg, "현재 밀도 증가 영역", x(1.45), y(2.95), { class: "warning" });
    text(svg, "현재 밀도 감소 영역", x(-1.95), y(1.25), { class: "callout" });
  }

  function drawTrend() {
    const svg = document.getElementById("trendChart");
    const w = 472, h = 185;
    const margin = { top: 12, right: 22, bottom: 34, left: 48 };
    const x = scale(1, trend.length, margin.left, w - margin.right);
    const y = scale(0, 0.40, h - margin.bottom, margin.top);
    const plotW = w - margin.left - margin.right;
    svg.setAttribute("viewBox", `0 0 ${w} ${h}`);
    for (const t of [0, 0.10, 0.20, 0.30, 0.40]) {
      svg.appendChild(svgEl("line", { class: "grid-line", x1: margin.left, x2: margin.left + plotW, y1: y(t), y2: y(t) }));
      text(svg, t.toFixed(2), margin.left - 10, y(t) + 4, { class: "tick-text", "text-anchor": "end" });
    }
    svg.appendChild(svgEl("line", { class: "threshold-line", x1: margin.left, x2: margin.left + plotW, y1: y(threshold), y2: y(threshold) }));
    const pts = trend.map((v, i) => [x(i + 1), y(v)]);
    svg.appendChild(svgEl("path", { class: "lsdd-line", d: linePath(pts) }));
    pts.forEach(([cx, cy], i) => svg.appendChild(svgEl("circle", { class: "lsdd-point", cx, cy, r: i >= 6 ? 4.8 : 4 })));
    svg.appendChild(svgEl("line", { class: "axis-line", x1: margin.left, x2: margin.left + plotW, y1: h - margin.bottom, y2: h - margin.bottom }));
    text(svg, "window", margin.left + plotW / 2, h - 8, { class: "axis-label", "text-anchor": "middle" });
    text(svg, "관리 기준 0.17", w - margin.right - 92, y(threshold) - 6, { class: "warning" });
  }

  function drawNull() {
    const svg = document.getElementById("nullChart");
    const w = 472, h = 185;
    const margin = { top: 8, right: 26, bottom: 34, left: 48 };
    const maxValue = Math.max(...nullBins.map(r => r.value));
    const x = scale(0, nullBins.length, margin.left, w - margin.right);
    const y = scale(0, maxValue * 1.2, h - margin.bottom, margin.top);
    const obsX = scale(0.03, 0.36, margin.left, w - margin.right)(observed);
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
    text(svg, "observed 0.34", obsX - 4, margin.top + 14, { class: "warning", "text-anchor": "end" });
    text(svg, `p=${pValue.toFixed(3)}`, obsX - 4, margin.top + 31, { class: "warning", "text-anchor": "end" });
    text(svg, "permutation LSDD score", margin.left + 168, h - 6, { class: "axis-label", "text-anchor": "middle" });
  }

  drawSummary();
  drawHeatmap();
  drawTrend();
  drawNull();
})();
