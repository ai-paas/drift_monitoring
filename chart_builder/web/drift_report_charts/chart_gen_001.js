(function () {
  const metric = [0.12,0.13,0.14,0.15,0.16,0.17,0.19,0.21,0.24,0.27,0.30,0.34,0.38,0.43,0.48,0.53,0.58,0.61,0.64,0.66,0.67,0.68];
  const threshold = 0.45;
  const alarmIndex = 15;
  const bins = [0.05,0.12,0.19,0.26,0.33,0.40,0.47,0.54,0.61,0.68,0.75,0.82,0.89];
  const refDensity = [4,10,20,31,38,34,24,14,7,3,1,0,0];
  const curDensity = [0,1,3,7,13,21,30,37,35,25,15,8,3];

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
      ["metric", "0.68"],
      ["threshold", threshold.toFixed(2)],
      ["alarm", `t=${alarmIndex}`]
    ];
    document.getElementById("summary").innerHTML = rows.map(([label, value]) => `<div class="metric-card"><div class="label">${label}</div><div class="value">${value}</div></div>`).join("");
  }

  function drawTrend() {
    const svg = document.getElementById("trendChart");
    const w = 630, h = 440;
    const margin = { top: 24, right: 30, bottom: 62, left: 58 };
    const x = scale(1, metric.length, margin.left, w - margin.right);
    const y = scale(0, 0.75, h - margin.bottom, margin.top);
    const plotW = w - margin.left - margin.right;
    svg.setAttribute("viewBox", `0 0 ${w} ${h}`);
    for (const t of [0.0, 0.2, 0.4, 0.6]) {
      svg.appendChild(svgEl("line", { class: "grid-line", x1: margin.left, x2: margin.left + plotW, y1: y(t), y2: y(t) }));
      text(svg, t.toFixed(1), margin.left - 12, y(t) + 4, { class: "tick-text", "text-anchor": "end" });
    }
    svg.appendChild(svgEl("line", { class: "threshold-line", x1: margin.left, x2: margin.left + plotW, y1: y(threshold), y2: y(threshold) }));
    svg.appendChild(svgEl("line", { class: "alarm-line", x1: x(alarmIndex), x2: x(alarmIndex), y1: margin.top, y2: h - margin.bottom }));
    svg.appendChild(svgEl("path", { class: "metric-line", d: linePath(metric.map((v, i) => [x(i + 1), y(v)])) }));
    metric.forEach((v, i) => {
      if (i % 2 === 0 || i + 1 >= alarmIndex) {
        svg.appendChild(svgEl("circle", { class: i + 1 >= alarmIndex ? "alarm-point" : "metric-point", cx: x(i + 1), cy: y(v), r: i + 1 >= alarmIndex ? 4.8 : 3.4 }));
      }
    });
    svg.appendChild(svgEl("line", { class: "axis-line", x1: margin.left, x2: margin.left + plotW, y1: h - margin.bottom, y2: h - margin.bottom }));
    svg.appendChild(svgEl("line", { class: "axis-line", x1: margin.left, x2: margin.left, y1: margin.top, y2: h - margin.bottom }));
    for (const t of [1, 6, 12, 18, 22]) {
      text(svg, t.toString(), x(t), h - margin.bottom + 24, { class: "tick-text", "text-anchor": "middle" });
    }
    text(svg, "time window", margin.left + plotW / 2, h - 12, { class: "axis-label", "text-anchor": "middle" });
    text(svg, "generic drift metric", 16, margin.top + 178, { class: "axis-label", "text-anchor": "middle", transform: `rotate(-90 16 ${margin.top + 178})` });
    text(svg, "threshold crossed", x(12.5), y(0.61), { class: "warning-text" });
    text(svg, "fallback chart until method-specific chart exists", x(2.2), y(0.70), { class: "callout" });
  }

  function drawDistribution() {
    const svg = document.getElementById("distributionChart");
    const w = 472, h = 185;
    const margin = { top: 16, right: 24, bottom: 34, left: 46 };
    const x = scale(0.05, 0.89, margin.left, w - margin.right);
    const y = scale(0, 42, h - margin.bottom, margin.top);
    svg.setAttribute("viewBox", `0 0 ${w} ${h}`);
    const refPts = refDensity.map((v, i) => [x(bins[i]), y(v)]);
    const curPts = curDensity.map((v, i) => [x(bins[i]), y(v)]);
    svg.appendChild(svgEl("path", { class: "ref-area", d: areaPath(refPts, y(0)) }));
    svg.appendChild(svgEl("path", { class: "cur-area", d: areaPath(curPts, y(0)) }));
    svg.appendChild(svgEl("line", { class: "axis-line", x1: margin.left, x2: w - margin.right, y1: h - margin.bottom, y2: h - margin.bottom }));
    text(svg, "metric value distribution", margin.left + 174, h - 8, { class: "axis-label", "text-anchor": "middle" });
    text(svg, "current shifts right", x(0.42), y(38), { class: "warning-text" });
  }

  function drawEvidence() {
    const svg = document.getElementById("summaryChart");
    const w = 472, h = 185;
    const margin = { top: 20, right: 28, bottom: 34, left: 118 };
    const rows = [
      ["final metric", 0.68, "bar-current"],
      ["threshold", 0.45, "bar-metric"],
      ["effect size", 0.52, "bar-current"],
      ["p-value score", 0.91, "bar-current"]
    ];
    const x = scale(0, 1, margin.left, w - margin.right);
    svg.setAttribute("viewBox", `0 0 ${w} ${h}`);
    rows.forEach(([label, value, cls], i) => {
      const y = 28 + i * 28;
      text(svg, label, margin.left - 14, y + 12, { class: "bar-label", "text-anchor": "end" });
      svg.appendChild(svgEl("rect", { class: cls, x: margin.left, y, width: x(value) - margin.left, height: 14, rx: 3 }));
      text(svg, value.toFixed(2), x(value) + 7, y + 12, { class: "tick-text" });
    });
    svg.appendChild(svgEl("line", { class: "axis-line", x1: margin.left, x2: w - margin.right, y1: h - margin.bottom, y2: h - margin.bottom }));
    text(svg, "normalized evidence", margin.left + 150, h - 8, { class: "axis-label", "text-anchor": "middle" });
  }

  drawSummary();
  drawTrend();
  drawDistribution();
  drawEvidence();
})();
