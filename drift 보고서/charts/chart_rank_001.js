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

  const rand = mulberry32(20260615);
  const reference = Array.from({ length: 220 }, () => normal(rand, 0, 1.0));
  const current = Array.from({ length: 220 }, () => {
    const base = normal(rand, 0.42, 1.08);
    return rand() < 0.08 ? base + normal(rand, 0.6, 0.55) : base;
  });
  const allValues = reference.concat(current);
  const yMin = Math.floor(Math.min(...allValues) * 2) / 2;
  const yMax = Math.ceil(Math.max(...allValues) * 2) / 2;

  function sorted(v) { return v.slice().sort((a, b) => a - b); }
  function quantile(values, p) {
    const s = sorted(values);
    const idx = (s.length - 1) * p;
    const lo = Math.floor(idx);
    const hi = Math.ceil(idx);
    const t = idx - lo;
    return s[lo] * (1 - t) + s[hi] * t;
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

  function drawAxes(svg, xTicks, yScale, yTicks, xLabel, yLabel) {
    const plotW = w - margin.left - margin.right;
    const plotH = h - margin.top - margin.bottom;
    for (const t of yTicks) {
      const y = yScale(t);
      svg.appendChild(svgEl("line", { class: "grid-line", x1: margin.left, x2: margin.left + plotW, y1: y, y2: y }));
      text(svg, t.toFixed(1), margin.left - 12, y + 4, { class: "tick-text", "text-anchor": "end" });
    }
    for (const tick of xTicks) {
      text(svg, tick.label, tick.x, margin.top + plotH + 26, { class: "tick-text", "text-anchor": "middle" });
    }
    svg.appendChild(svgEl("line", { class: "axis-line", x1: margin.left, x2: margin.left + plotW, y1: margin.top + plotH, y2: margin.top + plotH }));
    svg.appendChild(svgEl("line", { class: "axis-line", x1: margin.left, x2: margin.left, y1: margin.top, y2: margin.top + plotH }));
    text(svg, xLabel, margin.left + plotW / 2, h - 12, { class: "axis-label", "text-anchor": "middle" });
    text(svg, yLabel, 16, margin.top + plotH / 2, { class: "axis-label", "text-anchor": "middle", transform: `rotate(-90 16 ${margin.top + plotH / 2})` });
  }

  function kde(values, grid, bandwidth) {
    const c = 1 / (bandwidth * Math.sqrt(2 * Math.PI));
    return grid.map((x) => values.reduce((sum, v) => {
      const z = (x - v) / bandwidth;
      return sum + c * Math.exp(-0.5 * z * z);
    }, 0) / values.length);
  }

  function violinPath(cx, values, yScale, maxWidth, className, svg) {
    const grid = Array.from({ length: 96 }, (_, i) => yMin + (yMax - yMin) * i / 95);
    const dens = kde(values, grid, 0.32);
    const maxD = Math.max(...dens);
    const right = grid.map((g, i) => [cx + dens[i] / maxD * maxWidth, yScale(g)]);
    const left = grid.slice().reverse().map((g, i) => {
      const d = dens[dens.length - 1 - i];
      return [cx - d / maxD * maxWidth, yScale(g)];
    });
    svg.appendChild(svgEl("path", { class: className, d: `${linePath(right)} L${linePath(left).slice(1)} Z` }));
  }

  function drawBox(svg, cx, values, yScale, className) {
    const q1 = quantile(values, 0.25);
    const med = quantile(values, 0.5);
    const q3 = quantile(values, 0.75);
    const low = quantile(values, 0.05);
    const high = quantile(values, 0.95);
    const boxW = 58;
    svg.appendChild(svgEl("line", { class: "whisker", x1: cx, x2: cx, y1: yScale(low), y2: yScale(high) }));
    svg.appendChild(svgEl("line", { class: "whisker", x1: cx - 18, x2: cx + 18, y1: yScale(low), y2: yScale(low) }));
    svg.appendChild(svgEl("line", { class: "whisker", x1: cx - 18, x2: cx + 18, y1: yScale(high), y2: yScale(high) }));
    svg.appendChild(svgEl("rect", { class: className, x: cx - boxW / 2, y: yScale(q3), width: boxW, height: yScale(q1) - yScale(q3), rx: 4 }));
    svg.appendChild(svgEl("line", { class: "median-line", x1: cx - boxW / 2, x2: cx + boxW / 2, y1: yScale(med), y2: yScale(med) }));
  }

  function rankData() {
    const combined = reference.map(v => ({ v, group: "ref" })).concat(current.map(v => ({ v, group: "cur" }))).sort((a, b) => a.v - b.v);
    combined.forEach((d, i) => { d.rank = i + 1; });
    const rankSumCur = combined.filter(d => d.group === "cur").reduce((sum, d) => sum + d.rank, 0);
    const n1 = reference.length;
    const n2 = current.length;
    const uCur = rankSumCur - n2 * (n2 + 1) / 2;
    return { combined, uCur, auc: uCur / (n1 * n2), rankSumCur };
  }

  const ranks = rankData();

  function drawDistributionChart() {
    const svg = document.getElementById("distributionChart");
    svg.setAttribute("viewBox", `0 0 ${w} ${h}`);
    const y = scale(yMin, yMax, h - margin.bottom, margin.top);
    const refX = 205;
    const curX = 350;
    drawAxes(svg, [{ x: refX, label: "기준 구간" }, { x: curX, label: "현재 구간" }], y, [yMin, -1, 0, 1, yMax], "그룹", "관측값");
    violinPath(refX, reference, y, 46, "violin-ref", svg);
    violinPath(curX, current, y, 46, "violin-cur", svg);
    drawBox(svg, refX, reference, y, "box-ref");
    drawBox(svg, curX, current, y, "box-cur");
    const refMed = quantile(reference, 0.5);
    const curMed = quantile(current, 0.5);
    svg.appendChild(svgEl("line", { class: "threshold-line", x1: refX + 38, x2: curX - 38, y1: y(refMed), y2: y(curMed) }));
    text(svg, `중앙값 차이 ${(curMed - refMed).toFixed(2)}`, 270, y((refMed + curMed) / 2) - 10, { class: "callout", "text-anchor": "middle" });
  }

  function drawRankChart() {
    const svg = document.getElementById("rankChart");
    svg.setAttribute("viewBox", `0 0 ${w} ${h}`);
    const bins = 12;
    const maxRank = reference.length + current.length;
    const binW = maxRank / bins;
    const refBins = Array.from({ length: bins }, () => 0);
    const curBins = Array.from({ length: bins }, () => 0);
    for (const d of ranks.combined) {
      const idx = Math.min(bins - 1, Math.floor((d.rank - 1) / binW));
      if (d.group === "ref") refBins[idx] += 1;
      else curBins[idx] += 1;
    }
    const maxCount = Math.max(...refBins, ...curBins);
    const x = scale(1, maxRank, margin.left, w - margin.right);
    const y = scale(0, maxCount + 4, h - margin.bottom, margin.top);
    const plotW = w - margin.left - margin.right;
    const plotH = h - margin.top - margin.bottom;
    for (const t of [0, Math.round((maxCount + 4) / 2), maxCount + 4]) {
      svg.appendChild(svgEl("line", { class: "grid-line", x1: margin.left, x2: margin.left + plotW, y1: y(t), y2: y(t) }));
      text(svg, String(t), margin.left - 12, y(t) + 4, { class: "tick-text", "text-anchor": "end" });
    }
    for (const t of [1, 110, 220, 330, 440]) {
      const xx = x(t);
      svg.appendChild(svgEl("line", { class: "grid-line", x1: xx, x2: xx, y1: margin.top, y2: margin.top + plotH }));
      text(svg, String(t), xx, margin.top + plotH + 24, { class: "tick-text", "text-anchor": "middle" });
    }
    svg.appendChild(svgEl("line", { class: "axis-line", x1: margin.left, x2: margin.left + plotW, y1: margin.top + plotH, y2: margin.top + plotH }));
    svg.appendChild(svgEl("line", { class: "axis-line", x1: margin.left, x2: margin.left, y1: margin.top, y2: margin.top + plotH }));
    text(svg, "결합 순위", margin.left + plotW / 2, h - 12, { class: "axis-label", "text-anchor": "middle" });
    text(svg, "빈도", 16, margin.top + plotH / 2, { class: "axis-label", "text-anchor": "middle", transform: `rotate(-90 16 ${margin.top + plotH / 2})` });

    const barGap = 3;
    const barSlot = plotW / bins;
    for (let i = 0; i < bins; i += 1) {
      const left = margin.left + i * barSlot + 5;
      const bw = (barSlot - 14) / 2;
      svg.appendChild(svgEl("rect", { class: "rank-ref", x: left, y: y(refBins[i]), width: bw, height: y(0) - y(refBins[i]) }));
      svg.appendChild(svgEl("rect", { class: "rank-cur", x: left + bw + barGap, y: y(curBins[i]), width: bw, height: y(0) - y(curBins[i]) }));
    }
    const balance = curBins.map((v, i) => {
      const total = v + refBins[i];
      const share = total ? v / total : 0.5;
      return [margin.left + i * barSlot + barSlot / 2, y(share * maxCount)];
    });
    svg.appendChild(svgEl("path", { class: "rank-balance", d: linePath(balance) }));
    text(svg, "현재 구간이 높은 순위에 더 많이 분포", margin.left + 208, margin.top + 22, { class: "callout" });
  }

  function drawSummary() {
    const medianDiff = quantile(current, 0.5) - quantile(reference, 0.5);
    const rows = [
      ["Mann-Whitney U", Math.round(ranks.uCur).toLocaleString("ko-KR")],
      ["순위 AUC", ranks.auc.toFixed(3)],
      ["중앙값 차이", medianDiff.toFixed(2)]
    ];
    document.getElementById("summary").innerHTML = rows.map(([label, value]) => `<div class="metric"><div class="label">${label}</div><div class="value">${value}</div></div>`).join("");
  }

  drawSummary();
  drawDistributionChart();
  drawRankChart();
})();
