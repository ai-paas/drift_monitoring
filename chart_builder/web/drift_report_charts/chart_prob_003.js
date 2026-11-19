(function () {
  const bins = ["<-2", "-1.5", "-1", "-0.5", "0", "0.5", "1", "1.5", "2", ">2.5"];
  const reference = [0.05, 0.08, 0.13, 0.17, 0.19, 0.16, 0.11, 0.06, 0.03, 0.02];
  const currentRaw = [0.025, 0.045, 0.08, 0.13, 0.16, 0.17, 0.16, 0.115, 0.07, 0.045];
  const total = currentRaw.reduce((a, b) => a + b, 0);
  const current = currentRaw.map(v => v / total);
  const overlap = reference.map((p, i) => Math.min(p, current[i]));
  const overlapCoefficient = overlap.reduce((a, b) => a + b, 0);
  const bhattacharyyaCoefficient = reference.reduce((sum, p, i) => sum + Math.sqrt(p * current[i]), 0);
  const bhattacharyyaDistance = -Math.log(bhattacharyyaCoefficient);
  const maxLostIndex = reference
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

  function drawDistribution() {
    const svg = document.getElementById("distributionChart");
    const w = 630, h = 440;
    const margin = { top: 20, right: 22, bottom: 58, left: 58 };
    svg.setAttribute("viewBox", `0 0 ${w} ${h}`);
    const maxP = Math.max(...reference, ...current) * 1.24;
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
    text(svg, "확률 bin", margin.left + plotW / 2, h - 12, { class: "axis-label", "text-anchor": "middle" });
    text(svg, "확률", 16, margin.top + plotH / 2, { class: "axis-label", "text-anchor": "middle", transform: `rotate(-90 16 ${margin.top + plotH / 2})` });

    for (let i = 0; i < bins.length; i += 1) {
      const left = margin.left + i * xSlot + 5;
      const bw = (xSlot - 16) / 2;
      svg.appendChild(svgEl("rect", { class: "ref-bar", x: left, y: y(reference[i]), width: bw, height: y(0) - y(reference[i]), rx: 3 }));
      svg.appendChild(svgEl("rect", { class: "cur-bar", x: left + bw + 5, y: y(current[i]), width: bw, height: y(0) - y(current[i]), rx: 3 }));
      svg.appendChild(svgEl("rect", { class: "overlap-bar", x: left + bw * 0.48, y: y(overlap[i]), width: bw * 1.06, height: y(0) - y(overlap[i]), rx: 3 }));
      if (i % 2 === 0) {
        text(svg, bins[i], left + bw, h - margin.bottom + 24, { class: "tick-text", "text-anchor": "middle" });
      }
    }
    text(svg, `Overlap 계수 ${overlapCoefficient.toFixed(2)}`, margin.left + 244, margin.top + 20, { class: "callout" });
  }

  function drawOverlap() {
    const svg = document.getElementById("overlapChart");
    const w = 472, h = 185;
    const margin = { top: 12, right: 22, bottom: 30, left: 46 };
    svg.setAttribute("viewBox", `0 0 ${w} ${h}`);
    const barX = margin.left;
    const barY = 60;
    const barW = w - margin.left - margin.right;
    const barH = 34;
    svg.appendChild(svgEl("rect", { class: "overlap-bg", x: barX, y: barY, width: barW, height: barH, rx: 8 }));
    svg.appendChild(svgEl("rect", { class: "overlap-fill", x: barX, y: barY, width: barW * overlapCoefficient, height: barH, rx: 8 }));
    svg.appendChild(svgEl("rect", { class: "missing-fill", x: barX + barW * overlapCoefficient, y: barY, width: barW * (1 - overlapCoefficient), height: barH, rx: 8 }));
    text(svg, "겹침", barX, barY - 12, { class: "callout" });
    text(svg, `${(overlapCoefficient * 100).toFixed(1)}%`, barX + barW * overlapCoefficient - 8, barY + 23, { class: "bar-label", "text-anchor": "end" });
    text(svg, "비겹침", barX + barW - 54, barY - 12, { class: "bar-label" });
    text(svg, `Bhattacharyya coefficient ${bhattacharyyaCoefficient.toFixed(3)}`, barX, 132, { class: "tick-text" });
    text(svg, `확률 차이 최대 bin: ${bins[maxLostIndex]}`, barX, 154, { class: "tick-text" });
  }

  function drawTrend() {
    const svg = document.getElementById("trendChart");
    const w = 472, h = 185;
    const margin = { top: 12, right: 18, bottom: 34, left: 48 };
    svg.setAttribute("viewBox", `0 0 ${w} ${h}`);
    const vals = [0.010, 0.014, 0.018, 0.020, 0.026, 0.031, bhattacharyyaDistance];
    const threshold = 0.030;
    const yMax = 0.060;
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
      ["Bhattacharyya", bhattacharyyaDistance.toFixed(3)],
      ["Overlap 계수", overlapCoefficient.toFixed(3)],
      ["BC 계수", bhattacharyyaCoefficient.toFixed(3)]
    ];
    document.getElementById("summary").innerHTML = rows.map(([label, value]) => `<div class="metric"><div class="label">${label}</div><div class="value">${value}</div></div>`).join("");
  }

  drawSummary();
  drawDistribution();
  drawOverlap();
  drawTrend();
})();
