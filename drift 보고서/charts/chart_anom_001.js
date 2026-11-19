(function () {
  const bins = [0.05,0.10,0.15,0.20,0.25,0.30,0.35,0.40,0.45,0.50,0.55,0.60,0.65,0.70,0.75,0.80,0.85,0.90];
  const baseDensity = [6,14,26,36,40,34,24,14,8,4,2,1,0,0,0,0,0,0];
  const currentDensity = [0,1,3,6,10,15,22,29,34,37,34,28,20,13,8,5,3,1];
  const rate = [0.03,0.04,0.04,0.05,0.05,0.06,0.07,0.08,0.09,0.11,0.13,0.16,0.19,0.22,0.24,0.27,0.30,0.32,0.34,0.35,0.36,0.37,0.37,0.38];
  const thresholdScore = 0.62;
  const rateThreshold = 0.20;
  const alarmIndex = 14;

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
      ["outlier rate", "0.37"],
      ["threshold", thresholdScore.toFixed(2)],
      ["alarm", `t=${alarmIndex}`]
    ];
    document.getElementById("summary").innerHTML = rows.map(([label, value]) => `<div class="metric"><div class="label">${label}</div><div class="value">${value}</div></div>`).join("");
  }

  function drawScore() {
    const svg = document.getElementById("scoreChart");
    const w = 630, h = 440;
    const margin = { top: 24, right: 28, bottom: 62, left: 58 };
    const x = scale(0.05, 0.90, margin.left, w - margin.right);
    const y = scale(0, 44, h - margin.bottom, margin.top);
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
    svg.appendChild(svgEl("line", { class: "threshold-line", x1: x(thresholdScore), x2: x(thresholdScore), y1: margin.top, y2: h - margin.bottom }));

    svg.appendChild(svgEl("line", { class: "axis-line", x1: margin.left, x2: margin.left + plotW, y1: h - margin.bottom, y2: h - margin.bottom }));
    svg.appendChild(svgEl("line", { class: "axis-line", x1: margin.left, x2: margin.left, y1: margin.top, y2: h - margin.bottom }));
    for (const t of [0.10, 0.30, 0.50, 0.70, 0.90]) {
      text(svg, t.toFixed(2), x(t), h - margin.bottom + 24, { class: "tick-text", "text-anchor": "middle" });
    }
    text(svg, "anomaly score", margin.left + plotW / 2, h - 12, { class: "axis-label", "text-anchor": "middle" });
    text(svg, "density", 16, margin.top + 178, { class: "axis-label", "text-anchor": "middle", transform: `rotate(-90 16 ${margin.top + 178})` });
    text(svg, "current shifts into novelty region", x(0.36), y(41), { class: "warning-text" });
    text(svg, "threshold 0.62", x(thresholdScore) + 10, y(34), { class: "warning-text" });
  }

  function drawRate() {
    const svg = document.getElementById("rateChart");
    const w = 472, h = 185;
    const margin = { top: 12, right: 22, bottom: 34, left: 48 };
    const x = scale(1, rate.length, margin.left, w - margin.right);
    const y = scale(0, 0.42, h - margin.bottom, margin.top);
    const plotW = w - margin.left - margin.right;
    svg.setAttribute("viewBox", `0 0 ${w} ${h}`);
    for (const t of [0.0, 0.2, 0.4]) {
      svg.appendChild(svgEl("line", { class: "grid-line", x1: margin.left, x2: margin.left + plotW, y1: y(t), y2: y(t) }));
      text(svg, t.toFixed(1), margin.left - 10, y(t) + 4, { class: "tick-text", "text-anchor": "end" });
    }
    svg.appendChild(svgEl("line", { class: "threshold-line", x1: margin.left, x2: margin.left + plotW, y1: y(rateThreshold), y2: y(rateThreshold) }));
    svg.appendChild(svgEl("path", { class: "rate-line", d: linePath(rate.map((v, i) => [x(i + 1), y(v)])) }));
    rate.forEach((v, i) => {
      if (i % 3 === 0 || i + 1 >= alarmIndex) svg.appendChild(svgEl("circle", { class: i + 1 >= alarmIndex ? "rate-point" : "normal-point", cx: x(i + 1), cy: y(v), r: i + 1 >= alarmIndex ? 4.7 : 3.3 }));
    });
    svg.appendChild(svgEl("line", { class: "axis-line", x1: margin.left, x2: margin.left + plotW, y1: h - margin.bottom, y2: h - margin.bottom }));
    text(svg, "time index", margin.left + 160, h - 8, { class: "axis-label", "text-anchor": "middle" });
    text(svg, "rate threshold", x(12), y(rateThreshold) - 7, { class: "warning-text" });
  }

  function drawProjection() {
    const svg = document.getElementById("projectionChart");
    const w = 472, h = 185;
    const margin = { top: 12, right: 24, bottom: 34, left: 44 };
    const x = scale(-2.4, 3.0, margin.left, w - margin.right);
    const y = scale(-1.8, 1.8, h - margin.bottom, margin.top);
    svg.setAttribute("viewBox", `0 0 ${w} ${h}`);
    svg.appendChild(svgEl("line", { class: "grid-line", x1: margin.left, x2: w - margin.right, y1: y(0), y2: y(0) }));
    svg.appendChild(svgEl("line", { class: "grid-line", x1: x(0), x2: x(0), y1: margin.top, y2: h - margin.bottom }));
    for (let i = 0; i < 34; i += 1) {
      const bx = -1.35 + (i % 7) * 0.18 + Math.sin(i) * 0.07;
      const by = -0.35 + Math.floor(i / 7) * 0.18 + Math.cos(i * 1.4) * 0.07;
      const cx = 0.35 + (i % 6) * 0.23 + Math.sin(i * 1.3) * 0.08;
      const cy = 0.18 + Math.floor(i / 6) * 0.16 + Math.cos(i * 1.1) * 0.08;
      svg.appendChild(svgEl("circle", { class: "base-dot", cx: x(bx), cy: y(by), r: 4 }));
      svg.appendChild(svgEl("circle", { class: "current-dot", cx: x(cx), cy: y(cy), r: 4 }));
    }
    for (let i = 0; i < 13; i += 1) {
      const ox = 1.68 + (i % 5) * 0.20 + Math.sin(i * 1.8) * 0.08;
      const oy = 0.72 + Math.floor(i / 5) * 0.20 + Math.cos(i * 1.3) * 0.08;
      svg.appendChild(svgEl("circle", { class: "outlier-dot", cx: x(ox), cy: y(oy), r: 5 }));
    }
    svg.appendChild(svgEl("line", { class: "axis-line", x1: margin.left, x2: w - margin.right, y1: h - margin.bottom, y2: h - margin.bottom }));
    text(svg, "projection-1", margin.left + 160, h - 8, { class: "axis-label", "text-anchor": "middle" });
    text(svg, "outliers outside baseline", x(0.45), y(1.45), { class: "callout" });
  }

  drawSummary();
  drawScore();
  drawRate();
  drawProjection();
})();
