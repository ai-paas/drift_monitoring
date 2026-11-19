(function () {
  const summaryEl = document.getElementById("summary");

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

  const rand = mulberry32(20260616);
  const reference = Array.from({ length: 320 }, () => normal(rand, 0, 0.92));
  const current = Array.from({ length: 320 }, () => {
    const base = normal(rand, 0.46, 1.02);
    return rand() < 0.12 ? base + normal(rand, 0.7, 0.4) : base;
  });

  function sorted(v) { return v.slice().sort((a, b) => a - b); }
  function quantile(values, p) {
    const s = sorted(values);
    const idx = (s.length - 1) * p;
    const lo = Math.floor(idx);
    const hi = Math.ceil(idx);
    const t = idx - lo;
    return s[lo] * (1 - t) + s[hi] * t;
  }
  function mean(values) { return values.reduce((a, b) => a + b, 0) / values.length; }
  function wasserstein1d(a, b) {
    const sa = sorted(a);
    const sb = sorted(b);
    const n = Math.min(sa.length, sb.length);
    let sum = 0;
    for (let i = 0; i < n; i += 1) sum += Math.abs(sa[i] - sb[i]);
    return sum / n;
  }

  const distance = wasserstein1d(reference, current);
  const meanShift = mean(current) - mean(reference);
  const q90Shift = quantile(current, 0.9) - quantile(reference, 0.9);

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

  function kde(values, grid, bandwidth) {
    const c = 1 / (bandwidth * Math.sqrt(2 * Math.PI));
    return grid.map((x) => values.reduce((sum, v) => {
      const z = (x - v) / bandwidth;
      return sum + c * Math.exp(-0.5 * z * z);
    }, 0) / values.length);
  }

  function drawDistribution() {
    const svg = document.getElementById("distributionChart");
    const w = 630, h = 440;
    const margin = { top: 20, right: 22, bottom: 50, left: 58 };
    svg.setAttribute("viewBox", `0 0 ${w} ${h}`);
    const all = reference.concat(current);
    const xMin = Math.floor(Math.min(...all) * 2) / 2;
    const xMax = Math.ceil(Math.max(...all) * 2) / 2;
    const grid = Array.from({ length: 160 }, (_, i) => xMin + (xMax - xMin) * i / 159);
    const refD = kde(reference, grid, 0.26);
    const curD = kde(current, grid, 0.28);
    const yMax = Math.max(...refD, ...curD) * 1.18;
    const x = scale(xMin, xMax, margin.left, w - margin.right);
    const y = scale(0, yMax, h - margin.bottom, margin.top);
    const plotW = w - margin.left - margin.right;
    const plotH = h - margin.top - margin.bottom;

    for (const t of [0, yMax / 3, yMax * 2 / 3, yMax]) {
      svg.appendChild(svgEl("line", { class: "grid-line", x1: margin.left, x2: margin.left + plotW, y1: y(t), y2: y(t) }));
      text(svg, t.toFixed(2), margin.left - 12, y(t) + 4, { class: "tick-text", "text-anchor": "end" });
    }
    for (const t of [xMin, 0, xMax]) {
      svg.appendChild(svgEl("line", { class: "grid-line", x1: x(t), x2: x(t), y1: margin.top, y2: margin.top + plotH }));
      text(svg, t.toFixed(1), x(t), margin.top + plotH + 24, { class: "tick-text", "text-anchor": "middle" });
    }
    svg.appendChild(svgEl("line", { class: "axis-line", x1: margin.left, x2: margin.left + plotW, y1: margin.top + plotH, y2: margin.top + plotH }));
    svg.appendChild(svgEl("line", { class: "axis-line", x1: margin.left, x2: margin.left, y1: margin.top, y2: margin.top + plotH }));
    text(svg, "특성값", margin.left + plotW / 2, h - 12, { class: "axis-label", "text-anchor": "middle" });
    text(svg, "밀도", 16, margin.top + plotH / 2, { class: "axis-label", "text-anchor": "middle", transform: `rotate(-90 16 ${margin.top + plotH / 2})` });

    const refPts = grid.map((g, i) => [x(g), y(refD[i])]);
    const curPts = grid.map((g, i) => [x(g), y(curD[i])]);
    svg.appendChild(svgEl("path", { class: "ref-area", d: areaPath(refPts, h - margin.bottom) }));
    svg.appendChild(svgEl("path", { class: "cur-area", d: areaPath(curPts, h - margin.bottom) }));

    for (const p of [0.25, 0.5, 0.75]) {
      const r = quantile(reference, p);
      const c = quantile(current, p);
      const yy = y(yMax * (0.76 - p * 0.22));
      svg.appendChild(svgEl("line", { class: "transport", x1: x(r), x2: x(c), y1: yy, y2: yy }));
      svg.appendChild(svgEl("circle", { class: "trend-point", cx: x(r), cy: yy, r: 4 }));
      svg.appendChild(svgEl("circle", { class: "trend-point", cx: x(c), cy: yy, r: 4 }));
    }
    text(svg, "분위수 이동량의 평균이 Wasserstein 거리", margin.left + 156, margin.top + 22, { class: "transport-label" });
  }

  function drawTrend() {
    const svg = document.getElementById("trendChart");
    const w = 472, h = 185;
    const margin = { top: 12, right: 18, bottom: 34, left: 48 };
    svg.setAttribute("viewBox", `0 0 ${w} ${h}`);
    const vals = [0.12, 0.16, 0.14, 0.19, 0.24, 0.31, 0.37, 0.46, distance];
    const threshold = 0.30;
    const trendMax = Math.ceil(Math.max(...vals, threshold) * 10) / 10 + 0.1;
    const x = scale(1, vals.length, margin.left, w - margin.right);
    const y = scale(0, trendMax, h - margin.bottom, margin.top);
    const plotW = w - margin.left - margin.right;
    for (const t of [0, threshold, trendMax]) {
      svg.appendChild(svgEl("line", { class: "grid-line", x1: margin.left, x2: margin.left + plotW, y1: y(t), y2: y(t) }));
      text(svg, t.toFixed(1), margin.left - 10, y(t) + 4, { class: "tick-text", "text-anchor": "end" });
    }
    svg.appendChild(svgEl("line", { class: "threshold-line", x1: margin.left, x2: margin.left + plotW, y1: y(threshold), y2: y(threshold) }));
    const pts = vals.map((v, i) => [x(i + 1), y(v)]);
    svg.appendChild(svgEl("path", { class: "trend-line", d: linePath(pts) }));
    pts.forEach(([cx, cy]) => svg.appendChild(svgEl("circle", { class: "trend-point", cx, cy, r: 4 })));
    svg.appendChild(svgEl("line", { class: "axis-line", x1: margin.left, x2: margin.left + plotW, y1: h - margin.bottom, y2: h - margin.bottom }));
    svg.appendChild(svgEl("line", { class: "axis-line", x1: margin.left, x2: margin.left, y1: margin.top, y2: h - margin.bottom }));
    text(svg, "window", margin.left + plotW / 2, h - 8, { class: "axis-label", "text-anchor": "middle" });
    text(svg, "관리 기준", w - margin.right - 56, y(threshold) - 7, { class: "transport-label" });
  }

  function drawRanking() {
    const svg = document.getElementById("rankingChart");
    const w = 472, h = 185;
    const margin = { top: 8, right: 22, bottom: 28, left: 112 };
    svg.setAttribute("viewBox", `0 0 ${w} ${h}`);
    const rows = [
      ["결제금액", distance],
      ["접속시간", 0.41],
      ["방문빈도", 0.34],
      ["상품수", 0.27],
      ["할인율", 0.19]
    ];
    const maxValue = Math.max(...rows.map((row) => row[1]));
    const xMax = Math.ceil(maxValue * 10) / 10 + 0.1;
    const x = scale(0, xMax, margin.left, w - margin.right);
    const rowH = 27;
    rows.forEach(([label, value], i) => {
      const y = margin.top + i * rowH + 10;
      text(svg, label, margin.left - 10, y + 10, { class: "tick-text", "text-anchor": "end" });
      svg.appendChild(svgEl("rect", { class: i === 0 ? "bar-highlight" : "bar", x: margin.left, y, width: x(value) - margin.left, height: 16, rx: 4 }));
      text(svg, value.toFixed(2), x(value) + 7, y + 12, { class: "bar-label" });
    });
    svg.appendChild(svgEl("line", { class: "axis-line", x1: margin.left, x2: w - margin.right, y1: h - margin.bottom, y2: h - margin.bottom }));
    text(svg, "distance", margin.left + (w - margin.right - margin.left) / 2, h - 6, { class: "axis-label", "text-anchor": "middle" });
  }

  function drawSummary() {
    const rows = [
      ["Wasserstein", distance.toFixed(2)],
      ["평균 이동", meanShift.toFixed(2)],
      ["상위 10% 이동", q90Shift.toFixed(2)]
    ];
    summaryEl.innerHTML = rows.map(([label, value]) => `<div class="metric"><div class="label">${label}</div><div class="value">${value}</div></div>`).join("");
  }

  drawSummary();
  drawDistribution();
  drawTrend();
  drawRanking();
})();
