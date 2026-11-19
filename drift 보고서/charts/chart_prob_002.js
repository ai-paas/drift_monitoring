(function () {
  const categories = ["검색", "상세", "장바구니", "구매", "환불", "문의", "리뷰"];
  const reference = [0.24, 0.22, 0.15, 0.18, 0.05, 0.10, 0.06];
  const current = [0.17, 0.19, 0.18, 0.25, 0.08, 0.07, 0.06];
  const eps = 1e-12;
  const delta = current.map((v, i) => v - reference[i]);

  function kl(a, b) {
    return a.reduce((sum, v, i) => sum + v * Math.log((v + eps) / (b[i] + eps)), 0);
  }
  const midpoint = reference.map((v, i) => (v + current[i]) / 2);
  const jsDiv = 0.5 * kl(reference, midpoint) + 0.5 * kl(current, midpoint);
  const jsDist = Math.sqrt(jsDiv / Math.log(2));
  const hellinger = Math.sqrt(reference.reduce((sum, v, i) => sum + (Math.sqrt(v) - Math.sqrt(current[i])) ** 2, 0)) / Math.sqrt(2);
  const maxDeltaIndex = delta.reduce((best, v, i) => Math.abs(v) > Math.abs(delta[best]) ? i : best, 0);

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

  function drawDistribution() {
    const svg = document.getElementById("distributionChart");
    const w = 630, h = 440;
    const margin = { top: 20, right: 22, bottom: 70, left: 58 };
    svg.setAttribute("viewBox", `0 0 ${w} ${h}`);
    const maxP = Math.max(...reference, ...current) * 1.22;
    const xSlot = (w - margin.left - margin.right) / categories.length;
    const y = scale(0, maxP, h - margin.bottom, margin.top);
    const plotW = w - margin.left - margin.right;
    const plotH = h - margin.top - margin.bottom;

    for (const t of [0, 0.10, 0.20, 0.30]) {
      svg.appendChild(svgEl("line", { class: "grid-line", x1: margin.left, x2: margin.left + plotW, y1: y(t), y2: y(t) }));
      text(svg, t.toFixed(2), margin.left - 12, y(t) + 4, { class: "tick-text", "text-anchor": "end" });
    }
    svg.appendChild(svgEl("line", { class: "axis-line", x1: margin.left, x2: margin.left + plotW, y1: h - margin.bottom, y2: h - margin.bottom }));
    svg.appendChild(svgEl("line", { class: "axis-line", x1: margin.left, x2: margin.left, y1: margin.top, y2: h - margin.bottom }));
    text(svg, "category", margin.left + plotW / 2, h - 12, { class: "axis-label", "text-anchor": "middle" });
    text(svg, "확률", 16, margin.top + plotH / 2, { class: "axis-label", "text-anchor": "middle", transform: `rotate(-90 16 ${margin.top + plotH / 2})` });

    for (let i = 0; i < categories.length; i += 1) {
      const left = margin.left + i * xSlot + 8;
      const bw = (xSlot - 20) / 2;
      const overlap = Math.min(reference[i], current[i]);
      svg.appendChild(svgEl("rect", { class: "overlap-band", x: left, y: y(overlap), width: bw * 2 + 4, height: y(0) - y(overlap), rx: 4 }));
      svg.appendChild(svgEl("rect", { class: "ref-bar", x: left, y: y(reference[i]), width: bw, height: y(0) - y(reference[i]), rx: 3 }));
      svg.appendChild(svgEl("rect", { class: "cur-bar", x: left + bw + 4, y: y(current[i]), width: bw, height: y(0) - y(current[i]), rx: 3 }));
      text(svg, categories[i], left + bw + 2, h - margin.bottom + 24, { class: "tick-text", "text-anchor": "middle" });
    }
    text(svg, `최대 변화: ${categories[maxDeltaIndex]} ${delta[maxDeltaIndex] > 0 ? "+" : ""}${delta[maxDeltaIndex].toFixed(2)}`, margin.left + 248, margin.top + 20, { class: "callout" });
  }

  function drawTrend() {
    const svg = document.getElementById("trendChart");
    const w = 472, h = 185;
    const margin = { top: 12, right: 18, bottom: 34, left: 48 };
    svg.setAttribute("viewBox", `0 0 ${w} ${h}`);
    const jsVals = [0.08, 0.10, 0.11, 0.13, 0.16, 0.18, jsDist];
    const hellVals = [0.07, 0.09, 0.10, 0.12, 0.15, 0.17, hellinger];
    const threshold = 0.18;
    const yMax = 0.35;
    const x = scale(1, jsVals.length, margin.left, w - margin.right);
    const y = scale(0, yMax, h - margin.bottom, margin.top);
    const plotW = w - margin.left - margin.right;

    for (const t of [0, threshold, yMax]) {
      svg.appendChild(svgEl("line", { class: "grid-line", x1: margin.left, x2: margin.left + plotW, y1: y(t), y2: y(t) }));
      text(svg, t.toFixed(2), margin.left - 10, y(t) + 4, { class: "tick-text", "text-anchor": "end" });
    }
    svg.appendChild(svgEl("line", { class: "threshold-line", x1: margin.left, x2: margin.left + plotW, y1: y(threshold), y2: y(threshold) }));
    const jsPts = jsVals.map((v, i) => [x(i + 1), y(v)]);
    const hellPts = hellVals.map((v, i) => [x(i + 1), y(v)]);
    svg.appendChild(svgEl("path", { class: "js-line", d: linePath(jsPts) }));
    svg.appendChild(svgEl("path", { class: "hell-line", d: linePath(hellPts) }));
    jsPts.forEach(([cx, cy]) => svg.appendChild(svgEl("circle", { class: "trend-point js-point", cx, cy, r: 4 })));
    hellPts.forEach(([cx, cy]) => svg.appendChild(svgEl("circle", { class: "trend-point hell-point", cx, cy, r: 4 })));
    svg.appendChild(svgEl("line", { class: "axis-line", x1: margin.left, x2: margin.left + plotW, y1: h - margin.bottom, y2: h - margin.bottom }));
    svg.appendChild(svgEl("line", { class: "axis-line", x1: margin.left, x2: margin.left, y1: margin.top, y2: h - margin.bottom }));
    text(svg, "window", margin.left + plotW / 2, h - 8, { class: "axis-label", "text-anchor": "middle" });
    text(svg, "JS", w - margin.right - 76, margin.top + 18, { class: "callout" });
    text(svg, "Hellinger", w - margin.right - 76, margin.top + 36, { class: "bar-label" });
  }

  function drawDelta() {
    const svg = document.getElementById("deltaChart");
    const w = 472, h = 185;
    const margin = { top: 8, right: 24, bottom: 28, left: 98 };
    svg.setAttribute("viewBox", `0 0 ${w} ${h}`);
    const maxAbs = Math.max(...delta.map(v => Math.abs(v))) * 1.25;
    const x = scale(-maxAbs, maxAbs, margin.left, w - margin.right);
    const rowH = 21;
    const zero = x(0);
    svg.appendChild(svgEl("line", { class: "zero-line", x1: zero, x2: zero, y1: margin.top, y2: h - margin.bottom }));
    delta.forEach((value, i) => {
      const y = margin.top + i * rowH + 5;
      text(svg, categories[i], margin.left - 8, y + 10, { class: "tick-text", "text-anchor": "end" });
      const barX = value >= 0 ? zero : x(value);
      const width = Math.abs(x(value) - zero);
      svg.appendChild(svgEl("rect", { class: value >= 0 ? "delta-pos" : "delta-neg", x: barX, y, width, height: 14, rx: 4 }));
      text(svg, `${value >= 0 ? "+" : ""}${value.toFixed(2)}`, value >= 0 ? x(value) + 6 : x(value) - 6, y + 11, { class: "bar-label", "text-anchor": value >= 0 ? "start" : "end" });
    });
    svg.appendChild(svgEl("line", { class: "axis-line", x1: margin.left, x2: w - margin.right, y1: h - margin.bottom, y2: h - margin.bottom }));
    text(svg, "현재 확률 - 기준 확률", margin.left + (w - margin.right - margin.left) / 2, h - 6, { class: "axis-label", "text-anchor": "middle" });
  }

  function drawSummary() {
    const rows = [
      ["JS Distance", jsDist.toFixed(3)],
      ["Hellinger", hellinger.toFixed(3)],
      ["최대 Delta", `${categories[maxDeltaIndex]} ${delta[maxDeltaIndex] > 0 ? "+" : ""}${delta[maxDeltaIndex].toFixed(2)}`]
    ];
    document.getElementById("summary").innerHTML = rows.map(([label, value]) => `<div class="metric"><div class="label">${label}</div><div class="value">${value}</div></div>`).join("");
  }

  drawSummary();
  drawDistribution();
  drawTrend();
  drawDelta();
})();
