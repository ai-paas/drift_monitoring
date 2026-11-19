(function () {
  const bins = [0.02,0.05,0.08,0.11,0.14,0.17,0.20,0.23,0.26,0.29,0.32,0.35,0.38,0.41];
  const baseDensity = [3,9,18,31,38,34,25,15,8,4,2,1,0,0];
  const currentDensity = [0,1,3,7,12,18,26,33,37,34,26,17,9,4];
  const trend = [0.10,0.11,0.10,0.12,0.13,0.12,0.14,0.15,0.16,0.17,0.18,0.19,0.21,0.22,0.24,0.25,0.27,0.28,0.30,0.31,0.33,0.35,0.37,0.39,0.42,0.44,0.46,0.47,0.49,0.51,0.52,0.54];
  const threshold = 0.36;
  const alarmIndex = 23;

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

  function drawSummary() {
    const rows = [
      ["p95 error", "0.51"],
      ["threshold", threshold.toFixed(2)],
      ["latent AUC", "0.84"]
    ];
    document.getElementById("summary").innerHTML = rows.map(([label, value]) => `<div class="metric"><div class="label">${label}</div><div class="value">${value}</div></div>`).join("");
  }

  function drawDistribution() {
    const svg = document.getElementById("distributionChart");
    const w = 630, h = 440;
    const margin = { top: 24, right: 28, bottom: 62, left: 58 };
    const x = scale(0.02, 0.42, margin.left, w - margin.right);
    const y = scale(0, 42, h - margin.bottom, margin.top);
    const plotW = w - margin.left - margin.right;
    svg.setAttribute("viewBox", `0 0 ${w} ${h}`);
    for (const t of [0, 10, 20, 30, 40]) {
      svg.appendChild(svgEl("line", { class: "grid-line", x1: margin.left, x2: margin.left + plotW, y1: y(t), y2: y(t) }));
      text(svg, t.toString(), margin.left - 12, y(t) + 4, { class: "tick-text", "text-anchor": "end" });
    }
    const basePts = baseDensity.map((v, i) => [x(bins[i]), y(v)]);
    const currentPts = currentDensity.map((v, i) => [x(bins[i]), y(v)]);
    svg.appendChild(svgEl("path", { class: "base-area", d: areaPath(basePts, y(0)) }));
    svg.appendChild(svgEl("path", { class: "current-area", d: areaPath(currentPts, y(0)) }));
    svg.appendChild(svgEl("line", { class: "threshold-line", x1: x(threshold), x2: x(threshold), y1: margin.top, y2: h - margin.bottom }));
    svg.appendChild(svgEl("line", { class: "axis-line", x1: margin.left, x2: margin.left + plotW, y1: h - margin.bottom, y2: h - margin.bottom }));
    svg.appendChild(svgEl("line", { class: "axis-line", x1: margin.left, x2: margin.left, y1: margin.top, y2: h - margin.bottom }));
    for (const t of [0.05, 0.15, 0.25, 0.35]) {
      text(svg, t.toFixed(2), x(t), h - margin.bottom + 24, { class: "tick-text", "text-anchor": "middle" });
    }
    text(svg, "reconstruction error", margin.left + plotW / 2, h - 12, { class: "axis-label", "text-anchor": "middle" });
    text(svg, "density", 16, margin.top + 178, { class: "axis-label", "text-anchor": "middle", transform: `rotate(-90 16 ${margin.top + 178})` });
    text(svg, "current error distribution shifts right", x(0.19), y(39), { class: "warning-text" });
    text(svg, "threshold 0.36", x(threshold) + 10, y(34), { class: "warning-text" });
  }

  function drawTrend() {
    const svg = document.getElementById("trendChart");
    const w = 472, h = 185;
    const margin = { top: 12, right: 22, bottom: 34, left: 48 };
    const x = scale(1, trend.length, margin.left, w - margin.right);
    const y = scale(0.05, 0.58, h - margin.bottom, margin.top);
    const plotW = w - margin.left - margin.right;
    svg.setAttribute("viewBox", `0 0 ${w} ${h}`);
    for (const t of [0.1, 0.3, 0.5]) {
      svg.appendChild(svgEl("line", { class: "grid-line", x1: margin.left, x2: margin.left + plotW, y1: y(t), y2: y(t) }));
      text(svg, t.toFixed(1), margin.left - 10, y(t) + 4, { class: "tick-text", "text-anchor": "end" });
    }
    svg.appendChild(svgEl("line", { class: "threshold-line", x1: margin.left, x2: margin.left + plotW, y1: y(threshold), y2: y(threshold) }));
    svg.appendChild(svgEl("path", { class: "trend-line", d: linePath(trend.map((v, i) => [x(i + 1), y(v)])) }));
    trend.forEach((v, i) => {
      if (i % 4 === 0 || i + 1 >= alarmIndex) svg.appendChild(svgEl("circle", { class: i + 1 >= alarmIndex ? "alarm-point" : "trend-point", cx: x(i + 1), cy: y(v), r: i + 1 >= alarmIndex ? 4.8 : 3.4 }));
    });
    svg.appendChild(svgEl("line", { class: "axis-line", x1: margin.left, x2: margin.left + plotW, y1: h - margin.bottom, y2: h - margin.bottom }));
    text(svg, "time index", margin.left + 160, h - 8, { class: "axis-label", "text-anchor": "middle" });
    text(svg, "threshold exceeded", x(21), y(0.52), { class: "warning-text" });
  }

  function drawLatent() {
    const svg = document.getElementById("latentChart");
    const w = 472, h = 185;
    const margin = { top: 12, right: 24, bottom: 34, left: 44 };
    const x = scale(-2.4, 3.0, margin.left, w - margin.right);
    const y = scale(-1.8, 1.8, h - margin.bottom, margin.top);
    svg.setAttribute("viewBox", `0 0 ${w} ${h}`);
    svg.appendChild(svgEl("line", { class: "grid-line", x1: margin.left, x2: w - margin.right, y1: y(0), y2: y(0) }));
    svg.appendChild(svgEl("line", { class: "grid-line", x1: x(0), x2: x(0), y1: margin.top, y2: h - margin.bottom }));
    for (let i = 0; i < 36; i += 1) {
      const bx = -1.25 + (i % 6) * 0.20 + Math.sin(i) * 0.07;
      const by = -0.18 + Math.floor(i / 6) * 0.14 + Math.cos(i * 1.5) * 0.07;
      const cx = 0.86 + (i % 6) * 0.26 + Math.sin(i * 1.4) * 0.09;
      const cy = 0.22 + Math.floor(i / 6) * 0.15 + Math.cos(i * 1.2) * 0.08;
      svg.appendChild(svgEl("circle", { class: "base-dot", cx: x(bx), cy: y(by), r: 4 }));
      svg.appendChild(svgEl("circle", { class: "current-dot", cx: x(cx), cy: y(cy), r: 4 }));
    }
    svg.appendChild(svgEl("line", { class: "axis-line", x1: margin.left, x2: w - margin.right, y1: h - margin.bottom, y2: h - margin.bottom }));
    text(svg, "latent-1", margin.left + 160, h - 8, { class: "axis-label", "text-anchor": "middle" });
    text(svg, "latent clusters separate", x(0.78), y(1.48), { class: "callout" });
  }

  drawSummary();
  drawDistribution();
  drawTrend();
  drawLatent();
})();
