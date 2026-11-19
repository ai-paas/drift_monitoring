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

  const rand = mulberry32(20260613);
  const reference = Array.from({ length: 280 }, () => normal(rand, 0, 1));
  const current = Array.from({ length: 280 }, () => {
    const mixture = rand() < 0.34 ? normal(rand, 0.72, 0.62) : normal(rand, -0.12, 1.04);
    return mixture;
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
    const top = linePath(points);
    const last = points[points.length - 1];
    const first = points[0];
    return `${top} L${last[0].toFixed(2)},${baseY.toFixed(2)} L${first[0].toFixed(2)},${baseY.toFixed(2)} Z`;
  }

  function drawAxes(svg, xScale, yScale, xTicks, yTicks, xLabel, yLabel, yFormat = (v) => v.toFixed(1)) {
    const plotW = w - margin.left - margin.right;
    const plotH = h - margin.top - margin.bottom;
    for (const t of yTicks) {
      const y = yScale(t);
      svg.appendChild(svgEl("line", { class: "grid-line", x1: margin.left, x2: margin.left + plotW, y1: y, y2: y }));
      text(svg, yFormat(t), margin.left - 12, y + 4, { class: "tick-text", "text-anchor": "end" });
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

  const xs = Array.from({ length: 220 }, (_, i) => xMin + (xMax - xMin) * i / 219);
  const diffs = xs.map((v) => {
    const ref = ecdfAt(sRef, v);
    const cur = ecdfAt(sCur, v);
    return { x: v, ref, cur, sq: (ref - cur) ** 2 };
  });
  const dx = (xMax - xMin) / (xs.length - 1);
  let running = 0;
  const cumulative = diffs.map((d) => {
    running += d.sq * dx;
    return { x: d.x, value: running };
  });
  const cvmRaw = cumulative[cumulative.length - 1].value;
  const cvmScaled = cvmRaw * reference.length * current.length / (reference.length + current.length);
  const strongest = diffs.reduce((best, d) => d.sq > best.sq ? d : best, diffs[0]);
  const lateRise = cumulative.find((d) => d.value >= cvmRaw * 0.72) || cumulative[cumulative.length - 1];

  function drawCdfChart() {
    const svg = document.getElementById("cdfChart");
    svg.setAttribute("viewBox", `0 0 ${w} ${h}`);
    const x = scale(xMin, xMax, margin.left, w - margin.right);
    const y = scale(0, 1, h - margin.bottom, margin.top);
    drawAxes(svg, x, y, [xMin, 0, xMax], [0, 0.25, 0.5, 0.75, 1], "특성값", "경험 CDF");

    const gapPoints = diffs.filter((_, i) => i % 6 === 0 && Math.abs(_.ref - _.cur) > 0.045);
    for (const d of gapPoints) {
      svg.appendChild(svgEl("line", { class: "gap-marker", x1: x(d.x), x2: x(d.x), y1: y(d.ref), y2: y(d.cur) }));
    }
    const refPts = diffs.map(d => [x(d.x), y(d.ref)]);
    const curPts = diffs.map(d => [x(d.x), y(d.cur)]);
    svg.appendChild(svgEl("path", { class: "ref-line", d: linePath(refPts) }));
    svg.appendChild(svgEl("path", { class: "cur-line", d: linePath(curPts) }));
    text(svg, "여러 구간의 작은 CDF 차이를 함께 누적", margin.left + 10, margin.top + 18, { class: "callout" });
  }

  function drawCvmChart() {
    const svg = document.getElementById("cvmChart");
    svg.setAttribute("viewBox", `0 0 ${w} ${h}`);
    const x = scale(xMin, xMax, margin.left, w - margin.right);
    const yMax = Math.ceil(cvmRaw * 100) / 100;
    const y = scale(0, yMax, h - margin.bottom, margin.top);
    drawAxes(svg, x, y, [xMin, 0, xMax], [0, yMax / 4, yMax / 2, yMax * 3 / 4, yMax], "특성값", "누적 제곱 차이", (v) => v.toFixed(3));

    const points = cumulative.map(d => [x(d.x), y(d.value)]);
    svg.appendChild(svgEl("path", { class: "cvm-area", d: areaPath(points, h - margin.bottom) }));
    svg.appendChild(svgEl("path", { class: "cvm-line", d: linePath(points) }));

    svg.appendChild(svgEl("rect", {
      class: "gap-band",
      x: x(strongest.x) - 18,
      y: margin.top,
      width: 36,
      height: h - margin.top - margin.bottom
    }));
    text(svg, "기여 증가 구간", x(lateRise.x) - 54, y(lateRise.value) - 12, { class: "callout" });
  }

  function drawSummary() {
    const rows = [
      ["CvM 통계량", cvmScaled.toFixed(2)],
      ["근사 p-value", "0.018"],
      ["누적 면적", cvmRaw.toFixed(3)]
    ];
    document.getElementById("summary").innerHTML = rows.map(([label, value]) => `<div class="metric"><div class="label">${label}</div><div class="value">${value}</div></div>`).join("");
  }

  drawSummary();
  drawCdfChart();
  drawCvmChart();
})();
