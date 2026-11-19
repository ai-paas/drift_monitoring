(function () {
  const values = [0.28,0.31,0.30,0.34,0.32,0.35,0.33,0.37,0.35,0.36,0.34,0.38,0.36,0.39,0.37,0.40,0.38,0.41,0.40,0.42,0.43,0.45,0.49,0.52,0.57,0.61,0.64,0.67,0.69,0.71,0.70,0.72,0.74,0.73,0.75,0.77];
  const refStart = 10;
  const refEnd = 20;
  const curStart = 24;
  const curEnd = 34;
  const ecdfX = [0.30,0.35,0.40,0.45,0.50,0.55,0.60,0.65,0.70,0.75];
  const refCdf = [0.10,0.28,0.52,0.78,0.92,0.98,1.00,1.00,1.00,1.00];
  const curCdf = [0.00,0.02,0.05,0.12,0.24,0.38,0.55,0.72,0.88,1.00];
  const ksTrend = [0.12,0.14,0.16,0.18,0.21,0.24,0.31,0.39,0.48,0.55];
  const threshold = 0.36;
  const ksStatistic = 0.55;
  const pValue = 0.011;
  const alarmIndex = 28;

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
  function stepPath(xs, ys, xScale, yScale) {
    let d = `M${xScale(xs[0]).toFixed(2)},${yScale(ys[0]).toFixed(2)}`;
    for (let i = 1; i < xs.length; i++) {
      d += `H${xScale(xs[i]).toFixed(2)}V${yScale(ys[i]).toFixed(2)}`;
    }
    return d;
  }

  function drawSummary() {
    const rows = [
      ["KS statistic", ksStatistic.toFixed(2)],
      ["p-value", pValue.toFixed(3)],
      ["alarm index", alarmIndex.toString()]
    ];
    document.getElementById("summary").innerHTML = rows.map(([label, value]) => `<div class="metric"><div class="label">${label}</div><div class="value">${value}</div></div>`).join("");
  }

  function drawStream() {
    const svg = document.getElementById("streamChart");
    const w = 630, h = 440;
    const margin = { top: 24, right: 28, bottom: 62, left: 58 };
    const x = scale(1, values.length, margin.left, w - margin.right);
    const y = scale(0.25, 0.82, h - margin.bottom, margin.top);
    const plotW = w - margin.left - margin.right;
    const plotH = h - margin.top - margin.bottom;
    svg.setAttribute("viewBox", `0 0 ${w} ${h}`);

    for (const t of [0.3, 0.5, 0.7]) {
      svg.appendChild(svgEl("line", { class: "grid-line", x1: margin.left, x2: margin.left + plotW, y1: y(t), y2: y(t) }));
      text(svg, t.toFixed(1), margin.left - 12, y(t) + 4, { class: "tick-text", "text-anchor": "end" });
    }
    svg.appendChild(svgEl("rect", { class: "ref-window", x: x(refStart), y: margin.top, width: x(refEnd) - x(refStart), height: plotH }));
    svg.appendChild(svgEl("rect", { class: "cur-window", x: x(curStart), y: margin.top, width: x(curEnd) - x(curStart), height: plotH }));
    const pts = values.map((v, i) => [x(i + 1), y(v)]);
    svg.appendChild(svgEl("path", { class: "stream-line", d: linePath(pts) }));
    svg.appendChild(svgEl("circle", { class: "alarm-point", cx: x(alarmIndex), cy: y(values[alarmIndex - 1]), r: 7 }));
    svg.appendChild(svgEl("line", { class: "threshold-line", x1: x(alarmIndex), x2: x(alarmIndex), y1: margin.top, y2: h - margin.bottom }));
    svg.appendChild(svgEl("line", { class: "axis-line", x1: margin.left, x2: margin.left + plotW, y1: h - margin.bottom, y2: h - margin.bottom }));
    svg.appendChild(svgEl("line", { class: "axis-line", x1: margin.left, x2: margin.left, y1: margin.top, y2: h - margin.bottom }));
    for (const t of [1, 10, 20, 30, 36]) {
      text(svg, t.toString(), x(t), h - margin.bottom + 24, { class: "tick-text", "text-anchor": "middle" });
    }
    text(svg, "time index", margin.left + plotW / 2, h - 12, { class: "axis-label", "text-anchor": "middle" });
    text(svg, "metric", 16, margin.top + 178, { class: "axis-label", "text-anchor": "middle", transform: `rotate(-90 16 ${margin.top + 178})` });
    text(svg, "과거 window", x(refStart) + 22, margin.top + 24, { class: "callout" });
    text(svg, "최근 window", x(curStart) + 22, margin.top + 24, { class: "warning" });
  }

  function drawEcdf() {
    const svg = document.getElementById("ecdfChart");
    const w = 472, h = 185;
    const margin = { top: 12, right: 22, bottom: 34, left: 48 };
    const x = scale(0.30, 0.75, margin.left, w - margin.right);
    const y = scale(0, 1, h - margin.bottom, margin.top);
    const plotW = w - margin.left - margin.right;
    svg.setAttribute("viewBox", `0 0 ${w} ${h}`);
    for (const t of [0, 0.5, 1.0]) {
      svg.appendChild(svgEl("line", { class: "grid-line", x1: margin.left, x2: margin.left + plotW, y1: y(t), y2: y(t) }));
      text(svg, t.toFixed(1), margin.left - 10, y(t) + 4, { class: "tick-text", "text-anchor": "end" });
    }
    svg.appendChild(svgEl("path", { class: "ref-line", d: stepPath(ecdfX, refCdf, x, y) }));
    svg.appendChild(svgEl("path", { class: "cur-line", d: stepPath(ecdfX, curCdf, x, y) }));
    svg.appendChild(svgEl("line", { class: "threshold-line", x1: x(0.51), x2: x(0.51), y1: y(0.30), y2: y(0.85) }));
    svg.appendChild(svgEl("line", { class: "axis-line", x1: margin.left, x2: margin.left + plotW, y1: h - margin.bottom, y2: h - margin.bottom }));
    text(svg, "sample value", margin.left + plotW / 2, h - 8, { class: "axis-label", "text-anchor": "middle" });
    text(svg, "D=0.55", x(0.52) + 8, y(0.58), { class: "warning" });
  }

  function drawKs() {
    const svg = document.getElementById("ksChart");
    const w = 472, h = 185;
    const margin = { top: 12, right: 22, bottom: 34, left: 48 };
    const x = scale(1, ksTrend.length, margin.left, w - margin.right);
    const y = scale(0, 0.65, h - margin.bottom, margin.top);
    const plotW = w - margin.left - margin.right;
    svg.setAttribute("viewBox", `0 0 ${w} ${h}`);
    for (const t of [0, 0.2, 0.4, 0.6]) {
      svg.appendChild(svgEl("line", { class: "grid-line", x1: margin.left, x2: margin.left + plotW, y1: y(t), y2: y(t) }));
      text(svg, t.toFixed(1), margin.left - 10, y(t) + 4, { class: "tick-text", "text-anchor": "end" });
    }
    svg.appendChild(svgEl("line", { class: "threshold-line", x1: margin.left, x2: margin.left + plotW, y1: y(threshold), y2: y(threshold) }));
    const pts = ksTrend.map((v, i) => [x(i + 1), y(v)]);
    svg.appendChild(svgEl("path", { class: "ks-line", d: linePath(pts) }));
    pts.forEach(([cx, cy], i) => svg.appendChild(svgEl("circle", { class: ksTrend[i] >= threshold ? "alarm-point" : "ks-point", cx, cy, r: i >= 7 ? 4.8 : 4 })));
    svg.appendChild(svgEl("line", { class: "axis-line", x1: margin.left, x2: margin.left + plotW, y1: h - margin.bottom, y2: h - margin.bottom }));
    text(svg, "window comparison", margin.left + 160, h - 8, { class: "axis-label", "text-anchor": "middle" });
    text(svg, "threshold 0.36", w - margin.right - 98, y(threshold) - 6, { class: "warning" });
  }

  drawSummary();
  drawStream();
  drawEcdf();
  drawKs();
})();
