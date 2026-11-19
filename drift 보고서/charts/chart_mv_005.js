(function () {
  const points = [
    [-1.8, -0.8, 1.2], [-1.5, -0.3, 1.5], [-1.2, 0.2, 1.8], [-0.9, -0.7, 1.6],
    [-0.6, 0.3, 2.0], [-0.3, -0.4, 1.9], [0.0, 0.1, 1.4], [0.3, -0.6, 2.1],
    [0.6, 0.2, 2.3], [0.9, -0.2, 2.6], [1.1, 0.6, 3.0], [1.4, 0.9, 3.4],
    [1.7, 1.2, 4.1], [2.0, 1.4, 4.8], [2.3, 1.7, 5.6], [2.6, 2.0, 6.2],
    [2.9, 1.6, 5.8], [3.1, 2.3, 6.9], [1.9, 2.4, 5.2], [2.5, 2.7, 6.5]
  ];
  const trend = [2.1, 2.3, 2.4, 2.8, 3.1, 3.6, 4.2, 4.9, 5.5, 6.1];
  const threshold = 4.5;
  const histBins = [
    { label: "1", value: 5 }, { label: "2", value: 8 }, { label: "3", value: 11 },
    { label: "4", value: 9 }, { label: "5", value: 6 }, { label: "6", value: 4 },
    { label: "7", value: 2 }
  ];
  const meanDistance = 6.1;
  const exceedRate = 0.22;
  const maxDistance = 6.9;

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
  function pointClass(distance) {
    return distance >= threshold ? "alert-point" : "distance-point";
  }
  function pointRadius(distance) {
    return 4 + Math.min(4, distance * 0.55);
  }

  function drawSummary() {
    const rows = [
      ["평균 distance", meanDistance.toFixed(1)],
      ["초과 비중", `${Math.round(exceedRate * 100)}%`],
      ["최대 distance", maxDistance.toFixed(1)]
    ];
    document.getElementById("summary").innerHTML = rows.map(([label, value]) => `<div class="metric"><div class="label">${label}</div><div class="value">${value}</div></div>`).join("");
  }

  function drawPca() {
    const svg = document.getElementById("pcaChart");
    const w = 630, h = 440;
    const margin = { top: 24, right: 28, bottom: 62, left: 58 };
    const x = scale(-2.3, 3.4, margin.left, w - margin.right);
    const y = scale(-1.2, 3.0, h - margin.bottom, margin.top);
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
    svg.appendChild(svgEl("ellipse", { class: "normal-ellipse", cx: x(0.0), cy: y(0.0), rx: 205, ry: 120, transform: `rotate(18 ${x(0.0)} ${y(0.0)})` }));
    points.forEach(([px, py, d]) => svg.appendChild(svgEl("circle", { class: pointClass(d), cx: x(px), cy: y(py), r: pointRadius(d) })));
    svg.appendChild(svgEl("line", { class: "threshold-line", x1: x(0.0), y1: y(0.0), x2: x(2.55), y2: y(2.0) }));
    svg.appendChild(svgEl("line", { class: "axis-line", x1: margin.left, x2: margin.left + plotW, y1: h - margin.bottom, y2: h - margin.bottom }));
    svg.appendChild(svgEl("line", { class: "axis-line", x1: margin.left, x2: margin.left, y1: margin.top, y2: h - margin.bottom }));
    text(svg, "PC1", margin.left + plotW / 2, h - 12, { class: "axis-label", "text-anchor": "middle" });
    text(svg, "PC2", 16, margin.top + 178, { class: "axis-label", "text-anchor": "middle", transform: `rotate(-90 16 ${margin.top + 178})` });
    text(svg, "threshold 초과 sample이 우상단에 집중", x(1.45), y(2.75), { class: "warning" });
  }

  function drawTrend() {
    const svg = document.getElementById("trendChart");
    const w = 472, h = 185;
    const margin = { top: 12, right: 22, bottom: 34, left: 48 };
    const x = scale(1, trend.length, margin.left, w - margin.right);
    const y = scale(0, 7, h - margin.bottom, margin.top);
    const plotW = w - margin.left - margin.right;
    svg.setAttribute("viewBox", `0 0 ${w} ${h}`);
    for (const t of [0, 2, 4, 6]) {
      svg.appendChild(svgEl("line", { class: "grid-line", x1: margin.left, x2: margin.left + plotW, y1: y(t), y2: y(t) }));
      text(svg, t.toString(), margin.left - 10, y(t) + 4, { class: "tick-text", "text-anchor": "end" });
    }
    svg.appendChild(svgEl("line", { class: "threshold-line", x1: margin.left, x2: margin.left + plotW, y1: y(threshold), y2: y(threshold) }));
    const pts = trend.map((v, i) => [x(i + 1), y(v)]);
    svg.appendChild(svgEl("path", { class: "distance-line", d: linePath(pts) }));
    pts.forEach(([cx, cy], i) => svg.appendChild(svgEl("circle", { class: trend[i] >= threshold ? "alert-point" : "distance-point", cx, cy, r: i >= 7 ? 4.8 : 4 })));
    svg.appendChild(svgEl("line", { class: "axis-line", x1: margin.left, x2: margin.left + plotW, y1: h - margin.bottom, y2: h - margin.bottom }));
    text(svg, "window", margin.left + plotW / 2, h - 8, { class: "axis-label", "text-anchor": "middle" });
    text(svg, "threshold 4.5", w - margin.right - 92, y(threshold) - 6, { class: "warning" });
  }

  function drawHistogram() {
    const svg = document.getElementById("histChart");
    const w = 472, h = 185;
    const margin = { top: 8, right: 26, bottom: 34, left: 48 };
    const maxValue = Math.max(...histBins.map(r => r.value));
    const x = scale(0, histBins.length, margin.left, w - margin.right);
    const y = scale(0, maxValue * 1.2, h - margin.bottom, margin.top);
    const thresholdX = scale(0.5, 7.5, margin.left, w - margin.right)(threshold);
    svg.setAttribute("viewBox", `0 0 ${w} ${h}`);
    histBins.forEach((row, i) => {
      const barX = x(i) + 5;
      const barW = x(i + 1) - x(i) - 10;
      const barH = h - margin.bottom - y(row.value);
      svg.appendChild(svgEl("rect", { class: Number(row.label) >= 5 ? "tail-bar" : "hist-bar", x: barX, y: y(row.value), width: barW, height: barH, rx: 3 }));
      text(svg, row.label, barX + barW / 2, h - margin.bottom + 20, { class: "tick-text", "text-anchor": "middle" });
    });
    svg.appendChild(svgEl("line", { class: "threshold-line", x1: thresholdX, x2: thresholdX, y1: margin.top, y2: h - margin.bottom }));
    svg.appendChild(svgEl("line", { class: "axis-line", x1: margin.left, x2: w - margin.right, y1: h - margin.bottom, y2: h - margin.bottom }));
    text(svg, "threshold", thresholdX + 6, margin.top + 16, { class: "warning" });
    text(svg, "Mahalanobis distance", margin.left + 168, h - 6, { class: "axis-label", "text-anchor": "middle" });
  }

  drawSummary();
  drawPca();
  drawTrend();
  drawHistogram();
})();
