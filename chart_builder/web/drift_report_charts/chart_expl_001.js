(function () {
  const features = ["amount", "risk_score", "tenure", "channel", "region", "device"];
  const baseImp = [0.31, 0.27, 0.22, 0.17, 0.13, 0.10];
  const currentImp = [0.18, 0.36, 0.14, 0.24, 0.19, 0.12];
  const shapX = [-0.36,-0.28,-0.20,-0.12,-0.04,0.04,0.12,0.20,0.28,0.36];
  const baseDensity = [2,5,12,24,36,31,18,8,3,1];
  const currentDensity = [1,3,7,14,22,31,36,29,18,8];
  const heatmap = [
    [0.12,0.22,0.18,0.16,0.14,0.10],
    [0.18,0.36,0.21,0.29,0.22,0.16],
    [0.16,0.48,0.20,0.34,0.31,0.19]
  ];

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
  function areaPath(points, baseY) {
    return `${linePath(points)} L${points[points.length - 1][0].toFixed(2)},${baseY.toFixed(2)} L${points[0][0].toFixed(2)},${baseY.toFixed(2)} Z`;
  }
  function heatColor(v) {
    const low = [222, 233, 241];
    const mid = [201, 149, 47];
    const high = [185, 90, 80];
    const f = Math.min(1, v / 0.50);
    const a = f < 0.55 ? low : mid;
    const b = f < 0.55 ? mid : high;
    const g = f < 0.55 ? f / 0.55 : (f - 0.55) / 0.45;
    const c = a.map((x, i) => Math.round(x + (b[i] - x) * g));
    return `rgb(${c[0]},${c[1]},${c[2]})`;
  }

  function drawSummary() {
    const rows = [
      ["top shift", "risk_score"],
      ["rank change", "+3"],
      ["class heat", "0.48"]
    ];
    document.getElementById("summary").innerHTML = rows.map(([label, value]) => `<div class="metric"><div class="label">${label}</div><div class="value">${value}</div></div>`).join("");
  }

  function drawSummaryChart() {
    const svg = document.getElementById("summaryChart");
    const w = 630, h = 440;
    const margin = { top: 24, right: 28, bottom: 62, left: 92 };
    const x = scale(0, 0.42, margin.left, w - margin.right);
    const rowH = 48;
    svg.setAttribute("viewBox", `0 0 ${w} ${h}`);
    for (const t of [0, 0.1, 0.2, 0.3, 0.4]) {
      svg.appendChild(svgEl("line", { class: "grid-line", x1: x(t), x2: x(t), y1: margin.top, y2: h - margin.bottom }));
      text(svg, t.toFixed(1), x(t), h - margin.bottom + 24, { class: "tick-text", "text-anchor": "middle" });
    }
    features.forEach((feature, i) => {
      const y = margin.top + i * rowH + 14;
      text(svg, feature, margin.left - 10, y + 17, { class: "bar-label", "text-anchor": "end" });
      svg.appendChild(svgEl("rect", { class: "base-bar", x: margin.left, y, width: x(baseImp[i]) - margin.left, height: 13, rx: 4 }));
      svg.appendChild(svgEl("rect", { class: "current-bar", x: margin.left, y: y + 18, width: x(currentImp[i]) - margin.left, height: 13, rx: 4 }));
      if (Math.abs(currentImp[i] - baseImp[i]) > 0.08) {
        svg.appendChild(svgEl("line", { class: "rank-line", x1: x(baseImp[i]), y1: y + 6, x2: x(currentImp[i]), y2: y + 24 }));
      }
    });
    svg.appendChild(svgEl("line", { class: "axis-line", x1: margin.left, x2: w - margin.right, y1: h - margin.bottom, y2: h - margin.bottom }));
    text(svg, "mean |SHAP|", margin.left + 245, h - 12, { class: "axis-label", "text-anchor": "middle" });
    text(svg, "risk_score and channel gain importance", x(0.17), margin.top - 5, { class: "warning-text" });
  }

  function drawDistribution() {
    const svg = document.getElementById("distributionChart");
    const w = 472, h = 185;
    const margin = { top: 12, right: 24, bottom: 34, left: 44 };
    const x = scale(-0.38, 0.38, margin.left, w - margin.right);
    const y = scale(0, 40, h - margin.bottom, margin.top);
    const baseY = y(0);
    svg.setAttribute("viewBox", `0 0 ${w} ${h}`);
    for (const t of [0, 20, 40]) {
      svg.appendChild(svgEl("line", { class: "grid-line", x1: margin.left, x2: w - margin.right, y1: y(t), y2: y(t) }));
      text(svg, t.toString(), margin.left - 10, y(t) + 4, { class: "tick-text", "text-anchor": "end" });
    }
    svg.appendChild(svgEl("line", { class: "axis-line", x1: x(0), x2: x(0), y1: margin.top, y2: h - margin.bottom }));
    svg.appendChild(svgEl("path", { class: "base-area", d: areaPath(baseDensity.map((v, i) => [x(shapX[i]), y(v)]), baseY) }));
    svg.appendChild(svgEl("path", { class: "current-area", d: areaPath(currentDensity.map((v, i) => [x(shapX[i]), y(v)]), baseY) }));
    svg.appendChild(svgEl("line", { class: "axis-line", x1: margin.left, x2: w - margin.right, y1: h - margin.bottom, y2: h - margin.bottom }));
    text(svg, "risk_score SHAP value", margin.left + 160, h - 8, { class: "axis-label", "text-anchor": "middle" });
    text(svg, "current shifts positive", x(0.03), y(36), { class: "warning-text" });
  }

  function drawHeatmap() {
    const svg = document.getElementById("classHeatmap");
    const w = 472, h = 185;
    const margin = { top: 18, right: 16, bottom: 34, left: 70 };
    const classes = ["class A", "class B", "class C"];
    const cellW = (w - margin.left - margin.right) / features.length;
    const cellH = 35;
    svg.setAttribute("viewBox", `0 0 ${w} ${h}`);
    classes.forEach((cls, r) => {
      text(svg, cls, margin.left - 10, margin.top + r * cellH + 23, { class: "bar-label", "text-anchor": "end" });
      features.forEach((feature, c) => {
        const v = heatmap[r][c];
        svg.appendChild(svgEl("rect", { class: "cell", x: margin.left + c * cellW, y: margin.top + r * cellH, width: cellW, height: cellH, fill: heatColor(v) }));
        if (v >= 0.34) text(svg, v.toFixed(2), margin.left + c * cellW + cellW / 2, margin.top + r * cellH + 22, { class: "bar-label", "text-anchor": "middle" });
      });
    });
    ["amount", "risk", "tenure", "channel", "region", "device"].forEach((f, i) => {
      text(svg, f, margin.left + i * cellW + cellW / 2, h - margin.bottom + 18, { class: "tick-text", "text-anchor": "middle" });
    });
    svg.appendChild(svgEl("line", { class: "axis-line", x1: margin.left, x2: w - margin.right, y1: h - margin.bottom, y2: h - margin.bottom }));
    text(svg, "class-wise SHAP drift", margin.left + 162, h - 6, { class: "axis-label", "text-anchor": "middle" });
  }

  drawSummary();
  drawSummaryChart();
  drawDistribution();
  drawHeatmap();
})();
