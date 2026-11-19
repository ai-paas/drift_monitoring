(function () {
  const widthEcdf = 650;
  const heightEcdf = 470;
  const widthHist = 390;
  const heightHist = 470;
  const margin = { top: 22, right: 24, bottom: 52, left: 58 };

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
    const z = Math.sqrt(-2 * Math.log(u1)) * Math.cos(2 * Math.PI * u2);
    return mean + sd * z;
  }

  const rand = mulberry32(20260611);
  const reference = Array.from({ length: 260 }, () => normal(rand, 0, 1.0));
  const current = Array.from({ length: 230 }, () => normal(rand, 0.45, 1.18));
  const all = reference.concat(current);
  const xMin = Math.floor(Math.min(...all) * 2) / 2;
  const xMax = Math.ceil(Math.max(...all) * 2) / 2;

  function sorted(values) {
    return values.slice().sort((a, b) => a - b);
  }

  function ecdfAt(sortedValues, x) {
    let lo = 0;
    let hi = sortedValues.length;
    while (lo < hi) {
      const mid = Math.floor((lo + hi) / 2);
      if (sortedValues[mid] <= x) lo = mid + 1;
      else hi = mid;
    }
    return lo / sortedValues.length;
  }

  function ksStatistic(a, b) {
    const sa = sorted(a);
    const sb = sorted(b);
    const points = sorted(Array.from(new Set(sa.concat(sb))));
    let best = { x: points[0], ref: 0, cur: 0, d: 0 };
    for (const x of points) {
      const ref = ecdfAt(sa, x);
      const cur = ecdfAt(sb, x);
      const d = Math.abs(ref - cur);
      if (d > best.d) best = { x, ref, cur, d };
    }
    const n1 = a.length;
    const n2 = b.length;
    const ne = (n1 * n2) / (n1 + n2);
    const lambda = (Math.sqrt(ne) + 0.12 + 0.11 / Math.sqrt(ne)) * best.d;
    const p = Math.min(1, Math.max(0, 2 * Math.exp(-2 * lambda * lambda)));
    return { ...best, p };
  }

  const ks = ksStatistic(reference, current);

  function scale(domainMin, domainMax, rangeMin, rangeMax) {
    return (value) => {
      const t = (value - domainMin) / (domainMax - domainMin);
      return rangeMin + t * (rangeMax - rangeMin);
    };
  }

  function linePath(points) {
    return points.map((p, i) => `${i === 0 ? "M" : "L"}${p[0].toFixed(2)},${p[1].toFixed(2)}`).join(" ");
  }

  function svgEl(tag, attrs = {}) {
    const el = document.createElementNS("http://www.w3.org/2000/svg", tag);
    for (const [k, v] of Object.entries(attrs)) el.setAttribute(k, v);
    return el;
  }

  function addText(svg, text, x, y, attrs = {}) {
    const el = svgEl("text", { x, y, ...attrs });
    el.textContent = text;
    svg.appendChild(el);
    return el;
  }

  function drawAxes(svg, w, h, xScale, yScale, xTicks, yTicks, xLabel, yLabel) {
    const plotW = w - margin.left - margin.right;
    const plotH = h - margin.top - margin.bottom;
    const g = svgEl("g");
    svg.appendChild(g);

    for (const t of yTicks) {
      const y = yScale(t);
      g.appendChild(svgEl("line", { class: "grid-line", x1: margin.left, x2: margin.left + plotW, y1: y, y2: y }));
      addText(g, t.toFixed(1), margin.left - 12, y + 4, { class: "tick text", "text-anchor": "end" });
    }
    for (const t of xTicks) {
      const x = xScale(t);
      g.appendChild(svgEl("line", { class: "grid-line", x1: x, x2: x, y1: margin.top, y2: margin.top + plotH }));
      addText(g, t.toFixed(1), x, margin.top + plotH + 24, { class: "tick text", "text-anchor": "middle" });
    }
    g.appendChild(svgEl("line", { x1: margin.left, x2: margin.left + plotW, y1: margin.top + plotH, y2: margin.top + plotH, stroke: "var(--axis)" }));
    g.appendChild(svgEl("line", { x1: margin.left, x2: margin.left, y1: margin.top, y2: margin.top + plotH, stroke: "var(--axis)" }));
    addText(g, xLabel, margin.left + plotW / 2, h - 12, { class: "axis-label", "text-anchor": "middle" });
    addText(g, yLabel, 16, margin.top + plotH / 2, { class: "axis-label", "text-anchor": "middle", transform: `rotate(-90 16 ${margin.top + plotH / 2})` });
  }

  function drawEcdf() {
    const svg = document.getElementById("ecdfChart");
    svg.setAttribute("viewBox", `0 0 ${widthEcdf} ${heightEcdf}`);
    const x = scale(xMin, xMax, margin.left, widthEcdf - margin.right);
    const y = scale(0, 1, heightEcdf - margin.bottom, margin.top);
    const xTicks = [xMin, xMin + (xMax - xMin) * 0.25, xMin + (xMax - xMin) * 0.5, xMin + (xMax - xMin) * 0.75, xMax];
    const yTicks = [0, 0.25, 0.5, 0.75, 1];
    drawAxes(svg, widthEcdf, heightEcdf, x, y, xTicks, yTicks, "특성값", "경험 CDF");

    const xs = Array.from({ length: 180 }, (_, i) => xMin + (xMax - xMin) * i / 179);
    const sRef = sorted(reference);
    const sCur = sorted(current);
    const refPts = xs.map(v => [x(v), y(ecdfAt(sRef, v))]);
    const curPts = xs.map(v => [x(v), y(ecdfAt(sCur, v))]);
    svg.appendChild(svgEl("path", { class: "ref-line", d: linePath(refPts) }));
    svg.appendChild(svgEl("path", { class: "cur-line", d: linePath(curPts) }));

    const gx = x(ks.x);
    const y1 = y(ks.ref);
    const y2 = y(ks.cur);
    svg.appendChild(svgEl("line", { class: "gap-line", x1: gx, x2: gx, y1: y1, y2: y2 }));
    svg.appendChild(svgEl("circle", { cx: gx, cy: y1, r: 4, fill: "var(--gap)" }));
    svg.appendChild(svgEl("circle", { cx: gx, cy: y2, r: 4, fill: "var(--gap)" }));
    addText(svg, `D = ${ks.d.toFixed(3)}`, Math.min(gx + 12, widthEcdf - 96), (y1 + y2) / 2 - 8, { class: "gap-label" });
  }

  function histogram(values, bins) {
    const step = (xMax - xMin) / bins;
    const counts = Array.from({ length: bins }, (_, i) => ({ x0: xMin + i * step, x1: xMin + (i + 1) * step, count: 0 }));
    for (const v of values) {
      const i = Math.max(0, Math.min(bins - 1, Math.floor((v - xMin) / step)));
      counts[i].count += 1;
    }
    return counts.map(b => ({ ...b, density: b.count / values.length / step }));
  }

  function drawHist() {
    const svg = document.getElementById("histChart");
    svg.setAttribute("viewBox", `0 0 ${widthHist} ${heightHist}`);
    const bins = 24;
    const refBins = histogram(reference, bins);
    const curBins = histogram(current, bins);
    const maxD = Math.max(...refBins.map(d => d.density), ...curBins.map(d => d.density)) * 1.08;
    const x = scale(xMin, xMax, margin.left, widthHist - margin.right);
    const y = scale(0, maxD, heightHist - margin.bottom, margin.top);
    const xTicks = [xMin, xMin + (xMax - xMin) / 2, xMax];
    const yTicks = [0, maxD / 2, maxD];
    drawAxes(svg, widthHist, heightHist, x, y, xTicks, yTicks, "특성값", "밀도");
    for (let i = 0; i < bins; i++) {
      const rb = refBins[i];
      const cb = curBins[i];
      const bx = x(rb.x0);
      const bw = Math.max(1, x(rb.x1) - x(rb.x0) - 1);
      svg.appendChild(svgEl("rect", { class: "bar-ref", x: bx, y: y(rb.density), width: bw, height: y(0) - y(rb.density) }));
      svg.appendChild(svgEl("rect", { class: "bar-cur", x: bx + bw * 0.18, y: y(cb.density), width: bw * 0.64, height: y(0) - y(cb.density) }));
    }
  }

  function drawSummary() {
    const summary = document.getElementById("summary");
    const rows = [
      ["KS 통계량", ks.d.toFixed(3)],
      ["근사 p-value", ks.p < 0.001 ? "<0.001" : ks.p.toFixed(3)],
      ["표본 수", `${reference.length} / ${current.length}`]
    ];
    summary.innerHTML = rows.map(([label, value]) => `<div class="metric"><div class="label">${label}</div><div class="value">${value}</div></div>`).join("");
  }

  drawSummary();
  drawEcdf();
  drawHist();
})();
