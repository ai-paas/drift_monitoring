(function () {
  const bins = ["0-10", "10-20", "20-30", "30-40", "40-50", "50-60", "60-70", "70-80", "80-90", "90+"];
  const reference = [0.06, 0.10, 0.16, 0.19, 0.18, 0.14, 0.09, 0.05, 0.02, 0.01];
  const currentRaw = [0.03, 0.06, 0.10, 0.15, 0.17, 0.17, 0.13, 0.10, 0.06, 0.03];
  const total = currentRaw.reduce((a, b) => a + b, 0);
  const current = currentRaw.map(v => v / total);
  const intersection = reference.map((p, i) => Math.min(p, current[i]));
  const intersectionScore = intersection.reduce((a, b) => a + b, 0);
  const hinc = 1 - intersectionScore;
  const maxLossIndex = reference
    .map((p, i) => Math.abs(p - current[i]))
    .reduce((best, v, i, arr) => v > arr[best] ? i : best, 0);

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

  function drawHistogram() {
    const svg = document.getElementById("histogramChart");
    const w = 630, h = 440;
    const margin = { top: 20, right: 22, bottom: 58, left: 58 };
    svg.setAttribute("viewBox", `0 0 ${w} ${h}`);
    const maxP = Math.max(...reference, ...current) * 1.25;
    const xSlot = (w - margin.left - margin.right) / bins.length;
    const y = scale(0, maxP, h - margin.bottom, margin.top);
    const plotW = w - margin.left - margin.right;
    const plotH = h - margin.top - margin.bottom;

    for (const t of [0, 0.05, 0.10, 0.15, 0.20]) {
      svg.appendChild(svgEl("line", { class: "grid-line", x1: margin.left, x2: margin.left + plotW, y1: y(t), y2: y(t) }));
      text(svg, t.toFixed(2), margin.left - 12, y(t) + 4, { class: "tick-text", "text-anchor": "end" });
    }
    svg.appendChild(svgEl("line", { class: "axis-line", x1: margin.left, x2: margin.left + plotW, y1: h - margin.bottom, y2: h - margin.bottom }));
    svg.appendChild(svgEl("line", { class: "axis-line", x1: margin.left, x2: margin.left, y1: margin.top, y2: h - margin.bottom }));
    text(svg, "histogram bin", margin.left + plotW / 2, h - 12, { class: "axis-label", "text-anchor": "middle" });
    text(svg, "확률", 16, margin.top + plotH / 2, { class: "axis-label", "text-anchor": "middle", transform: `rotate(-90 16 ${margin.top + plotH / 2})` });

    for (let i = 0; i < bins.length; i += 1) {
      const left = margin.left + i * xSlot + 5;
      const bw = (xSlot - 16) / 2;
      svg.appendChild(svgEl("rect", { class: "ref-bar", x: left, y: y(reference[i]), width: bw, height: y(0) - y(reference[i]), rx: 3 }));
      svg.appendChild(svgEl("rect", { class: "cur-bar", x: left + bw + 5, y: y(current[i]), width: bw, height: y(0) - y(current[i]), rx: 3 }));
      svg.appendChild(svgEl("rect", { class: "overlap-bar", x: left + bw * 0.48, y: y(intersection[i]), width: bw * 1.06, height: y(0) - y(intersection[i]), rx: 3 }));
      if (i % 2 === 0) {
        text(svg, bins[i], left + bw, h - margin.bottom + 24, { class: "tick-text", "text-anchor": "middle" });
      }
    }
    text(svg, `intersection ${intersectionScore.toFixed(2)} / complement ${hinc.toFixed(2)}`, margin.left + 188, margin.top + 20, { class: "callout" });
  }

  function drawIntersection() {
    const svg = document.getElementById("intersectionChart");
    const w = 472, h = 185;
    const margin = { top: 8, right: 22, bottom: 28, left: 92 };
    svg.setAttribute("viewBox", `0 0 ${w} ${h}`);
    const rows = intersection
      .map((value, i) => ({ label: bins[i], value }))
      .sort((a, b) => b.value - a.value)
      .slice(0, 5);
    const maxValue = Math.max(...rows.map(r => r.value));
    const x = scale(0, maxValue * 1.2, margin.left, w - margin.right);
    const rowH = 27;
    rows.forEach((row, i) => {
      const y = margin.top + i * rowH + 10;
      text(svg, row.label, margin.left - 10, y + 10, { class: "tick-text", "text-anchor": "end" });
      svg.appendChild(svgEl("rect", { class: i === 0 ? "bar-highlight" : "bar", x: margin.left, y, width: x(row.value) - margin.left, height: 16, rx: 4 }));
      text(svg, row.value.toFixed(2), x(row.value) + 7, y + 12, { class: "bar-label" });
    });
    svg.appendChild(svgEl("line", { class: "axis-line", x1: margin.left, x2: w - margin.right, y1: h - margin.bottom, y2: h - margin.bottom }));
    text(svg, "min(p, q)", margin.left + (w - margin.right - margin.left) / 2, h - 6, { class: "axis-label", "text-anchor": "middle" });
  }

  function drawTrend() {
    const svg = document.getElementById("trendChart");
    const w = 472, h = 185;
    const margin = { top: 12, right: 18, bottom: 34, left: 48 };
    svg.setAttribute("viewBox", `0 0 ${w} ${h}`);
    const vals = [0.11, 0.13, 0.15, 0.18, 0.21, 0.24, hinc];
    const threshold = 0.22;
    const yMax = 0.34;
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
      ["HINC", hinc.toFixed(3)],
      ["Intersection", intersectionScore.toFixed(3)],
      ["손실 최대 bin", bins[maxLossIndex]]
    ];
    document.getElementById("summary").innerHTML = rows.map(([label, value]) => `<div class="metric"><div class="label">${label}</div><div class="value">${value}</div></div>`).join("");
  }

  drawSummary();
  drawHistogram();
  drawIntersection();
  drawTrend();
})();
