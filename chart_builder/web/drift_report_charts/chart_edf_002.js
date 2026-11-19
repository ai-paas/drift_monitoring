(function () {
  const w = 535;
  const h = 450;
  const margin = { top: 22, right: 26, bottom: 52, left: 58 };

  function mulberry32(seed) {
    return function () {
      let t = seed += 0x6D2B79F5;
      t = Math.imul(t ^ t >>> 15, t | 1);
      t ^= t + Math.imul(t ^ t >>> 7, t | 61);
      return ((t ^ t >>> 14) >>> 0) / 4294967296;
    };
  }

  function normal(rand, mean, sd) {
    const u1 = Math.max(rand(), 1e-12);
    const u2 = rand();
    return mean + sd * Math.sqrt(-2 * Math.log(u1)) * Math.cos(2 * Math.PI * u2);
  }

  const rand = mulberry32(20260612);
  const reference = Array.from({ length: 260 }, () => normal(rand, 0, 1));
  const current = Array.from({ length: 260 }, () => {
    const base = normal(rand, 0.04, 0.94);
    if (rand() < 0.13) return base + normal(rand, 0, 2.2);
    return base;
  });
  const all = reference.concat(current);
  const xMin = Math.floor(Math.min(...all) * 2) / 2;
  const xMax = Math.ceil(Math.max(...all) * 2) / 2;

  function sorted(v) { return v.slice().sort((a, b) => a - b); }
  const sRef = sorted(reference);
  const sCur = sorted(current);

  function ecdfAt(sortedValues, x) {
    let lo = 0, hi = sortedValues.length;
    while (lo < hi) {
      const mid = Math.floor((lo + hi) / 2);
      if (sortedValues[mid] <= x) lo = mid + 1;
      else hi = mid;
    }
    return lo / sortedValues.length;
  }

  function quantile(sortedValues, p) {
    const idx = (sortedValues.length - 1) * p;
    const lo = Math.floor(idx);
    const hi = Math.ceil(idx);
    const t = idx - lo;
    return sortedValues[lo] * (1 - t) + sortedValues[hi] * t;
  }

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

  function drawAxes(svg, xScale, yScale, xTicks, yTicks, xLabel, yLabel) {
    const plotW = w - margin.left - margin.right;
    const plotH = h - margin.top - margin.bottom;
    for (const t of yTicks) {
      const y = yScale(t);
      svg.appendChild(svgEl("line", { class: "grid-line", x1: margin.left, x2: margin.left + plotW, y1: y, y2: y }));
      text(svg, t.toFixed(1), margin.left - 12, y + 4, { class: "tick-text", "text-anchor": "end" });
    }
    for (const t of xTicks) {
      const x = xScale(t);
      svg.appendChild(svgEl("line", { class: "grid-line", x1: x, x2: x, y1: margin.top, y2: margin.top + plotH }));
      text(svg, t.toFixed(1), x, margin.top + plotH + 24, { class: "tick-text", "text-anchor": "middle" });
    }
    svg.appendChild(svgEl("line", { class: "axis-line", x1: margin.left, x2: margin.left + plotW, y1: margin.top + plotH, y2: margin.top + plotH }));
    svg.appendChild(svgEl("line", { class: "axis-line", x1: margin.left, x2: margin.left, y1: margin.top, y2: margin.top + plotH }));
    text(svg, xLabel, margin.left + plotW / 2, h - 12, { class: "axis-label", "text-anchor": "middle" });
    text(svg, yLabel, 16, margin.top + plotH / 2, { class: "axis-label", "text-anchor": "middle", transform: `rotate(-90 16 ${margin.top + plotH / 2})` });
  }

  function tailScore() {
    const ps = [0.01, 0.02, 0.05, 0.95, 0.98, 0.99];
    const diffs = ps.map(p => Math.abs(quantile(sCur, p) - quantile(sRef, p)));
    return diffs.reduce((a, b) => a + b, 0) / diffs.length;
  }

  function drawTailChart() {
    const svg = document.getElementById("tailChart");
    svg.setAttribute("viewBox", `0 0 ${w} ${h}`);
    const x = scale(xMin, xMax, margin.left, w - margin.right);
    const y = scale(0, 1, h - margin.bottom, margin.top);
    drawAxes(svg, x, y, [xMin, 0, xMax], [0, 0.25, 0.5, 0.75, 1], "특성값", "경험 CDF");

    const q05 = quantile(sRef, 0.05);
    const q95 = quantile(sRef, 0.95);
    svg.appendChild(svgEl("rect", { class: "tail-band", x: margin.left, y: margin.top, width: x(q05) - margin.left, height: h - margin.top - margin.bottom }));
    svg.appendChild(svgEl("rect", { class: "tail-band", x: x(q95), y: margin.top, width: w - margin.right - x(q95), height: h - margin.top - margin.bottom }));
    text(svg, "하위 tail", margin.left + 8, margin.top + 16, { class: "tail-label" });
    text(svg, "상위 tail", w - margin.right - 64, margin.top + 16, { class: "tail-label" });

    const xs = Array.from({ length: 180 }, (_, i) => xMin + (xMax - xMin) * i / 179);
    const refPts = xs.map(v => [x(v), y(ecdfAt(sRef, v))]);
    const curPts = xs.map(v => [x(v), y(ecdfAt(sCur, v))]);
    svg.appendChild(svgEl("path", { class: "ref-line", d: linePath(refPts) }));
    svg.appendChild(svgEl("path", { class: "cur-line", d: linePath(curPts) }));
  }

  function drawQqChart() {
    const svg = document.getElementById("qqChart");
    svg.setAttribute("viewBox", `0 0 ${w} ${h}`);
    const qs = Array.from({ length: 39 }, (_, i) => 0.025 + i * 0.95 / 38);
    const pairs = qs.map(p => [quantile(sRef, p), quantile(sCur, p), p]);
    const minV = Math.floor(Math.min(...pairs.flatMap(d => [d[0], d[1]])) * 2) / 2;
    const maxV = Math.ceil(Math.max(...pairs.flatMap(d => [d[0], d[1]])) * 2) / 2;
    const x = scale(minV, maxV, margin.left, w - margin.right);
    const y = scale(minV, maxV, h - margin.bottom, margin.top);
    drawAxes(svg, x, y, [minV, 0, maxV], [minV, 0, maxV], "기준 분위수", "현재 분위수");
    svg.appendChild(svgEl("line", { class: "qq-ref", x1: x(minV), x2: x(maxV), y1: y(minV), y2: y(maxV) }));
    for (const [xr, yc, p] of pairs) {
      const r = p < 0.08 || p > 0.92 ? 5 : 3.5;
      svg.appendChild(svgEl("circle", { class: "qq-point", cx: x(xr), cy: y(yc), r }));
    }
    text(svg, "점선에서 멀수록 분위수 차이가 큼", margin.left + 8, margin.top + 16, { class: "tail-label" });
  }

  function drawSummary() {
    const tail = tailScore();
    const rows = [
      ["AD 통계량", "2.84"],
      ["근사 p-value", "0.012"],
      ["Tail 차이", tail.toFixed(2)]
    ];
    document.getElementById("summary").innerHTML = rows.map(([label, value]) => `<div class="metric"><div class="label">${label}</div><div class="value">${value}</div></div>`).join("");
  }

  drawSummary();
  drawTailChart();
  drawQqChart();
})();
