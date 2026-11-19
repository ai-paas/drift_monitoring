(function () {
  const categories = ["검색", "상세", "장바구니", "구매", "환불", "문의", "리뷰"];
  const reference = [0.28, 0.20, 0.13, 0.15, 0.05, 0.13, 0.06];
  const current = [0.16, 0.19, 0.15, 0.23, 0.08, 0.12, 0.07];
  const deltas = current.map((v, i) => v - reference[i]);
  const absDeltas = deltas.map(Math.abs);
  const maxIndex = absDeltas.reduce((best, v, i) => v > absDeltas[best] ? i : best, 0);
  const lInf = absDeltas[maxIndex];
  const direction = deltas[maxIndex] > 0 ? "증가" : "감소";

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

  function drawProportionChart() {
    const svg = document.getElementById("proportionChart");
    const w = 630, h = 440;
    const margin = { top: 20, right: 22, bottom: 70, left: 58 };
    svg.setAttribute("viewBox", `0 0 ${w} ${h}`);
    const maxP = 0.32;
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
    text(svg, "비율", 16, margin.top + plotH / 2, { class: "axis-label", "text-anchor": "middle", transform: `rotate(-90 16 ${margin.top + plotH / 2})` });

    for (let i = 0; i < categories.length; i += 1) {
      const left = margin.left + i * xSlot + 8;
      const bw = (xSlot - 20) / 2;
      if (i === maxIndex) {
        svg.appendChild(svgEl("rect", { class: "highlight-band", x: left - 5, y: margin.top, width: xSlot - 10, height: h - margin.top - margin.bottom, rx: 8 }));
      }
      svg.appendChild(svgEl("rect", { class: "ref-bar", x: left, y: y(reference[i]), width: bw, height: y(0) - y(reference[i]), rx: 3 }));
      svg.appendChild(svgEl("rect", { class: "cur-bar", x: left + bw + 4, y: y(current[i]), width: bw, height: y(0) - y(current[i]), rx: 3 }));
      text(svg, categories[i], left + bw + 2, h - margin.bottom + 24, { class: "tick-text", "text-anchor": "middle" });
    }
    text(svg, `최대 변화: ${categories[maxIndex]} ${deltas[maxIndex] > 0 ? "+" : ""}${deltas[maxIndex].toFixed(2)}`, margin.left + 220, margin.top + 20, { class: "callout" });
  }

  function drawMaxDeltaChart() {
    const svg = document.getElementById("maxDeltaChart");
    const w = 472, h = 185;
    const margin = { top: 8, right: 22, bottom: 28, left: 98 };
    svg.setAttribute("viewBox", `0 0 ${w} ${h}`);
    const rows = absDeltas.map((value, i) => ({ label: categories[i], value, signed: deltas[i] })).sort((a, b) => b.value - a.value);
    const maxValue = Math.max(...rows.map(r => r.value));
    const x = scale(0, maxValue * 1.22, margin.left, w - margin.right);
    const rowH = 21;
    rows.forEach((row, i) => {
      const y = margin.top + i * rowH + 5;
      text(svg, row.label, margin.left - 8, y + 10, { class: "tick-text", "text-anchor": "end" });
      svg.appendChild(svgEl("rect", { class: i === 0 ? "max-bar" : "other-bar", x: margin.left, y, width: x(row.value) - margin.left, height: 14, rx: 4 }));
      text(svg, `${row.value.toFixed(2)} (${row.signed > 0 ? "+" : ""}${row.signed.toFixed(2)})`, x(row.value) + 7, y + 11, { class: "bar-label" });
    });
    svg.appendChild(svgEl("line", { class: "axis-line", x1: margin.left, x2: w - margin.right, y1: h - margin.bottom, y2: h - margin.bottom }));
    text(svg, "max |현재 - 기준|", margin.left + (w - margin.right - margin.left) / 2, h - 6, { class: "axis-label", "text-anchor": "middle" });
  }

  function drawTrend() {
    const svg = document.getElementById("trendChart");
    const w = 472, h = 185;
    const margin = { top: 12, right: 18, bottom: 34, left: 48 };
    svg.setAttribute("viewBox", `0 0 ${w} ${h}`);
    const vals = [0.05, 0.06, 0.07, 0.08, 0.09, 0.11, lInf];
    const threshold = 0.10;
    const yMax = 0.18;
    const x = scale(1, vals.length, margin.left, w - margin.right);
    const y = scale(0, yMax, h - margin.bottom, margin.top);
    const plotW = w - margin.left - margin.right;
    for (const t of [0, threshold, yMax]) {
      svg.appendChild(svgEl("line", { class: "grid-line", x1: margin.left, x2: margin.left + plotW, y1: y(t), y2: y(t) }));
      text(svg, t.toFixed(2), margin.left - 10, y(t) + 4, { class: "tick-text", "text-anchor": "end" });
    }
    svg.appendChild(svgEl("line", { class: "threshold-line", x1: margin.left, x2: margin.left + plotW, y1: y(threshold), y2: y(threshold) }));
    const pts = vals.map((v, i) => [x(i + 1), y(v)]);
    svg.appendChild(svgEl("path", { class: "trend-line", d: linePath(pts) }));
    pts.forEach(([cx, cy]) => svg.appendChild(svgEl("circle", { class: "trend-point", cx, cy, r: 4 })));
    svg.appendChild(svgEl("line", { class: "axis-line", x1: margin.left, x2: margin.left + plotW, y1: h - margin.bottom, y2: h - margin.bottom }));
    svg.appendChild(svgEl("line", { class: "axis-line", x1: margin.left, x2: margin.left, y1: margin.top, y2: h - margin.bottom }));
    text(svg, "window", margin.left + plotW / 2, h - 8, { class: "axis-label", "text-anchor": "middle" });
    text(svg, "관리 기준", w - margin.right - 56, y(threshold) - 7, { class: "callout" });
  }

  function drawSummary() {
    const rows = [
      ["L-infinity", lInf.toFixed(3)],
      ["최대 category", categories[maxIndex]],
      ["변화 방향", `${direction} ${deltas[maxIndex].toFixed(2)}`]
    ];
    document.getElementById("summary").innerHTML = rows.map(([label, value]) => `<div class="metric"><div class="label">${label}</div><div class="value">${value}</div></div>`).join("");
  }

  drawSummary();
  drawProportionChart();
  drawMaxDeltaChart();
  drawTrend();
})();
