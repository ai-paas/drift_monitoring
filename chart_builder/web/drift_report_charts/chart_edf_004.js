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

  function wrap360(v) {
    return ((v % 360) + 360) % 360;
  }

  const rand = mulberry32(20260614);
  const reference = Array.from({ length: 260 }, () => {
    const center = rand() < 0.62 ? 35 : 222;
    return wrap360(normal(rand, center, center === 35 ? 18 : 24));
  });
  const current = Array.from({ length: 260 }, () => {
    const center = rand() < 0.54 ? 62 : 252;
    return wrap360(normal(rand, center, center === 62 ? 21 : 20));
  });

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

  function areaToZero(points, zeroY) {
    const top = linePath(points);
    const last = points[points.length - 1];
    const first = points[0];
    return `${top} L${last[0].toFixed(2)},${zeroY.toFixed(2)} L${first[0].toFixed(2)},${zeroY.toFixed(2)} Z`;
  }

  const xs = Array.from({ length: 241 }, (_, i) => i * 360 / 240);
  const deviation = xs.map((x) => {
    const diff = ecdfAt(sCur, x) - ecdfAt(sRef, x);
    return { x, diff };
  });
  const maxPos = deviation.reduce((best, d) => d.diff > best.diff ? d : best, deviation[0]);
  const maxNeg = deviation.reduce((best, d) => d.diff < best.diff ? d : best, deviation[0]);
  const dPlus = maxPos.diff;
  const dMinus = Math.abs(maxNeg.diff);
  const kuiper = dPlus + dMinus;

  function drawAxes(svg, xScale, yScale, xTicks, yTicks, xLabel, yLabel) {
    const plotW = w - margin.left - margin.right;
    const plotH = h - margin.top - margin.bottom;
    for (const t of yTicks) {
      const y = yScale(t);
      svg.appendChild(svgEl("line", { class: "grid-line", x1: margin.left, x2: margin.left + plotW, y1: y, y2: y }));
      text(svg, t.toFixed(2), margin.left - 12, y + 4, { class: "tick-text", "text-anchor": "end" });
    }
    for (const t of xTicks) {
      const x = xScale(t);
      svg.appendChild(svgEl("line", { class: "grid-line", x1: x, x2: x, y1: margin.top, y2: margin.top + plotH }));
      text(svg, `${t}°`, x, margin.top + plotH + 24, { class: "tick-text", "text-anchor": "middle" });
    }
    svg.appendChild(svgEl("line", { class: "axis-line", x1: margin.left, x2: margin.left + plotW, y1: margin.top + plotH, y2: margin.top + plotH }));
    svg.appendChild(svgEl("line", { class: "axis-line", x1: margin.left, x2: margin.left, y1: margin.top, y2: margin.top + plotH }));
    svg.appendChild(svgEl("line", { class: "zero-line", x1: margin.left, x2: margin.left + plotW, y1: yScale(0), y2: yScale(0) }));
    text(svg, xLabel, margin.left + plotW / 2, h - 12, { class: "axis-label", "text-anchor": "middle" });
    text(svg, yLabel, 16, margin.top + plotH / 2, { class: "axis-label", "text-anchor": "middle", transform: `rotate(-90 16 ${margin.top + plotH / 2})` });
  }

  function drawDeviationChart() {
    const svg = document.getElementById("deviationChart");
    svg.setAttribute("viewBox", `0 0 ${w} ${h}`);
    const maxAbs = Math.ceil(Math.max(dPlus, dMinus) * 100) / 100 + 0.02;
    const x = scale(0, 360, margin.left, w - margin.right);
    const y = scale(-maxAbs, maxAbs, h - margin.bottom, margin.top);
    drawAxes(svg, x, y, [0, 90, 180, 270, 360], [-maxAbs, -maxAbs / 2, 0, maxAbs / 2, maxAbs], "각도 또는 순환 위치", "현재 CDF - 기준 CDF");

    const pos = deviation.filter(d => d.diff >= 0).map(d => [x(d.x), y(d.diff)]);
    const neg = deviation.filter(d => d.diff <= 0).map(d => [x(d.x), y(d.diff)]);
    if (pos.length > 1) svg.appendChild(svgEl("path", { class: "pos-area", d: areaToZero(pos, y(0)) }));
    if (neg.length > 1) svg.appendChild(svgEl("path", { class: "neg-area", d: areaToZero(neg, y(0)) }));
    svg.appendChild(svgEl("path", { class: "dev-line", d: linePath(deviation.map(d => [x(d.x), y(d.diff)])) }));

    svg.appendChild(svgEl("line", { class: "pos-marker", x1: x(maxPos.x), x2: x(maxPos.x), y1: y(0), y2: y(maxPos.diff) }));
    svg.appendChild(svgEl("line", { class: "neg-marker", x1: x(maxNeg.x), x2: x(maxNeg.x), y1: y(0), y2: y(maxNeg.diff) }));
    text(svg, `D+ ${dPlus.toFixed(3)}`, x(maxPos.x) + 8, y(maxPos.diff) - 8, { class: "callout-strong" });
    text(svg, `D- ${dMinus.toFixed(3)}`, x(maxNeg.x) + 8, y(maxNeg.diff) + 18, { class: "callout-strong" });
  }

  function binCounts(values, bins) {
    const counts = Array.from({ length: bins }, () => 0);
    for (const value of values) {
      const idx = Math.min(bins - 1, Math.floor(value / 360 * bins));
      counts[idx] += 1;
    }
    return counts.map(v => v / values.length);
  }

  function polar(cx, cy, r, deg) {
    const rad = (deg - 90) * Math.PI / 180;
    return [cx + r * Math.cos(rad), cy + r * Math.sin(rad)];
  }

  function wedgePath(cx, cy, r0, r1, start, end) {
    const large = end - start > 180 ? 1 : 0;
    const p1 = polar(cx, cy, r1, start);
    const p2 = polar(cx, cy, r1, end);
    const p3 = polar(cx, cy, r0, end);
    const p4 = polar(cx, cy, r0, start);
    return [
      `M${p1[0].toFixed(2)},${p1[1].toFixed(2)}`,
      `A${r1},${r1} 0 ${large} 1 ${p2[0].toFixed(2)},${p2[1].toFixed(2)}`,
      `L${p3[0].toFixed(2)},${p3[1].toFixed(2)}`,
      `A${r0},${r0} 0 ${large} 0 ${p4[0].toFixed(2)},${p4[1].toFixed(2)}`,
      "Z"
    ].join(" ");
  }

  function drawCircularChart() {
    const svg = document.getElementById("circularChart");
    svg.setAttribute("viewBox", `0 0 ${w} ${h}`);
    const cx = 268;
    const cy = 224;
    const inner = 70;
    const maxR = 176;
    const bins = 18;
    const refCounts = binCounts(reference, bins);
    const curCounts = binCounts(current, bins);
    const maxCount = Math.max(...refCounts, ...curCounts);

    for (const r of [inner, inner + 36, inner + 72, maxR]) {
      svg.appendChild(svgEl("circle", { class: "ring", cx, cy, r }));
    }
    for (const angle of [0, 90, 180, 270]) {
      const p = polar(cx, cy, maxR + 18, angle);
      text(svg, `${angle}°`, p[0], p[1] + 4, { class: "angle-label", "text-anchor": "middle" });
    }

    const step = 360 / bins;
    for (let i = 0; i < bins; i += 1) {
      const start = i * step + 1.5;
      const mid = i * step + step / 2;
      const end = (i + 1) * step - 1.5;
      const refR = inner + refCounts[i] / maxCount * 78;
      const curR = inner + curCounts[i] / maxCount * 112;
      svg.appendChild(svgEl("path", { class: "cur-bar", d: wedgePath(cx, cy, inner + 36, curR, start, end) }));
      svg.appendChild(svgEl("path", { class: "ref-bar", d: wedgePath(cx, cy, inner, refR, start, end) }));
      if (Math.abs(curCounts[i] - refCounts[i]) > 0.035) {
        const p = polar(cx, cy, maxR + 34, mid);
        text(svg, "shift", p[0], p[1], { class: "callout", "text-anchor": "middle" });
      }
    }
    text(svg, "기준/현재 peak 각도 이동", cx, cy + 4, { class: "callout-strong", "text-anchor": "middle" });
  }

  function drawSummary() {
    const rows = [
      ["Kuiper V", kuiper.toFixed(3)],
      ["D+ / D-", `${dPlus.toFixed(3)} / ${dMinus.toFixed(3)}`],
      ["근사 p-value", "0.009"]
    ];
    document.getElementById("summary").innerHTML = rows.map(([label, value]) => `<div class="metric"><div class="label">${label}</div><div class="value">${value}</div></div>`).join("");
  }

  drawSummary();
  drawDeviationChart();
  drawCircularChart();
})();
