(function () {
  const bins = ["0-20", "20-40", "40-60", "60-80", "80-100"];
  const reference = [0.12, 0.22, 0.30, 0.24, 0.12];
  const current = [0.07, 0.15, 0.26, 0.32, 0.20];
  const threshold = 0.10;
  const contributions = reference.map((r, i) => (current[i] - r) * Math.log(current[i] / r));
  const psi = contributions.reduce((s, v) => s + v, 0);
  const deltas = current.map((v, i) => v - reference[i]);
  const topIndex = contributions.reduce((best, v, i) => v > contributions[best] ? i : best, 0);
  const topDirection = deltas[topIndex] > 0 ? "증가" : "감소";

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

  function drawSummary() {
    const rows = [
      ["PSI", psi.toFixed(3)],
      ["상위 기여 bin", bins[topIndex]],
      ["주요 이동", `${topDirection} ${(Math.abs(deltas[topIndex]) * 100).toFixed(1)}pp`]
    ];
    document.getElementById("summary").innerHTML = rows.map(([label, value]) => `<div class="metric"><div class="label">${label}</div><div class="value">${value}</div></div>`).join("");
  }

  function drawBinChart() {
    const svg = document.getElementById("binChart");
    const w = 630, h = 440;
    const margin = { top: 22, right: 24, bottom: 70, left: 58 };
    const plotW = w - margin.left - margin.right;
    const y = scale(0, 0.38, h - margin.bottom, margin.top);
    const xSlot = plotW / bins.length;
    svg.setAttribute("viewBox", `0 0 ${w} ${h}`);

    for (const t of [0, 0.10, 0.20, 0.30]) {
      svg.appendChild(svgEl("line", { class: "grid-line", x1: margin.left, x2: margin.left + plotW, y1: y(t), y2: y(t) }));
      text(svg, `${Math.round(t * 100)}%`, margin.left - 12, y(t) + 4, { class: "tick-text", "text-anchor": "end" });
    }

    svg.appendChild(svgEl("line", { class: "axis-line", x1: margin.left, x2: margin.left + plotW, y1: h - margin.bottom, y2: h - margin.bottom }));
    svg.appendChild(svgEl("line", { class: "axis-line", x1: margin.left, x2: margin.left, y1: margin.top, y2: h - margin.bottom }));
    text(svg, "score band / feature bin", margin.left + plotW / 2, h - 12, { class: "axis-label", "text-anchor": "middle" });
    text(svg, "비율", 16, margin.top + 170, { class: "axis-label", "text-anchor": "middle", transform: `rotate(-90 16 ${margin.top + 170})` });

    bins.forEach((bin, i) => {
      const left = margin.left + i * xSlot + 14;
      const bw = (xSlot - 34) / 2;
      if (i === topIndex) {
        svg.appendChild(svgEl("rect", { class: "highlight-band", x: left - 7, y: margin.top, width: xSlot - 14, height: h - margin.top - margin.bottom, rx: 8 }));
      }
      svg.appendChild(svgEl("rect", { class: "ref-bar", x: left, y: y(reference[i]), width: bw, height: y(0) - y(reference[i]), rx: 3 }));
      svg.appendChild(svgEl("rect", { class: "cur-bar", x: left + bw + 5, y: y(current[i]), width: bw, height: y(0) - y(current[i]), rx: 3 }));
      text(svg, bin, left + bw + 3, h - margin.bottom + 24, { class: "tick-text", "text-anchor": "middle" });
      text(svg, `${deltas[i] > 0 ? "+" : ""}${(deltas[i] * 100).toFixed(0)}pp`, left + bw + 3, h - margin.bottom + 43, { class: "bar-label", "text-anchor": "middle" });
    });

    text(svg, `상위 기여: ${bins[topIndex]} bin`, margin.left + 220, margin.top + 20, { class: "callout" });
  }

  function drawContributionChart() {
    const svg = document.getElementById("contributionChart");
    const w = 472, h = 185;
    const margin = { top: 8, right: 24, bottom: 30, left: 72 };
    const rows = contributions.map((value, i) => ({ bin: bins[i], value, delta: deltas[i] })).sort((a, b) => b.value - a.value);
    const maxValue = Math.max(...rows.map(r => r.value));
    const x = scale(0, maxValue * 1.25, margin.left, w - margin.right);
    svg.setAttribute("viewBox", `0 0 ${w} ${h}`);

    rows.forEach((row, i) => {
      const y = margin.top + i * 27 + 5;
      text(svg, row.bin, margin.left - 8, y + 12, { class: "tick-text", "text-anchor": "end" });
      svg.appendChild(svgEl("rect", { class: i === 0 ? "top-contribution" : "contribution-bar", x: margin.left, y, width: x(row.value) - margin.left, height: 18, rx: 4 }));
      text(svg, `${row.value.toFixed(3)} (${row.delta > 0 ? "+" : ""}${(row.delta * 100).toFixed(0)}pp)`, x(row.value) + 7, y + 13, { class: "bar-label" });
    });

    svg.appendChild(svgEl("line", { class: "axis-line", x1: margin.left, x2: w - margin.right, y1: h - margin.bottom, y2: h - margin.bottom }));
    text(svg, "PSI contribution", margin.left + (w - margin.right - margin.left) / 2, h - 6, { class: "axis-label", "text-anchor": "middle" });
  }

  function drawTrendChart() {
    const svg = document.getElementById("trendChart");
    const w = 472, h = 185;
    const margin = { top: 12, right: 18, bottom: 34, left: 48 };
    const vals = [0.035, 0.044, 0.052, 0.071, 0.092, 0.118, psi];
    const yMax = 0.18;
    const x = scale(1, vals.length, margin.left, w - margin.right);
    const y = scale(0, yMax, h - margin.bottom, margin.top);
    const plotW = w - margin.left - margin.right;
    svg.setAttribute("viewBox", `0 0 ${w} ${h}`);

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
    text(svg, "관리 기준", w - margin.right - 58, y(threshold) - 7, { class: "callout" });
  }

  drawSummary();
  drawBinChart();
  drawContributionChart();
  drawTrendChart();
})();
