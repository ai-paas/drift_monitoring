(function () {
  const rocPtsRaw = [[0,0],[0.04,0.32],[0.10,0.54],[0.20,0.71],[0.34,0.84],[0.52,0.92],[0.75,0.97],[1,1]];
  const scoreX = [0.05,0.12,0.19,0.26,0.33,0.40,0.47,0.54,0.61,0.68,0.75,0.82,0.89,0.96];
  const baseScore = [22,28,34,31,24,16,9,5,2,1,0,0,0,0];
  const currentScore = [0,0,1,2,4,8,14,22,31,35,30,21,12,5];
  const descriptors = [
    ["refund policy", 0.32],
    ["enterprise SSO", 0.25],
    ["invoice issue", 0.18],
    ["API latency", 0.14],
    ["legacy flow", 0.11]
  ];

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
    return `${linePath(points)} L${points[points.length - 1][0].toFixed(2)},${baseY.toFixed(2)} L${points[0][0].toFixed(2)},${baseY.toFixed(2)} Z`;
  }

  function drawSummary() {
    const rows = [
      ["ROC AUC", "0.89"],
      ["KS score", "0.47"],
      ["top descriptor", "refund"]
    ];
    document.getElementById("summary").innerHTML = rows.map(([label, value]) => `<div class="metric"><div class="label">${label}</div><div class="value">${value}</div></div>`).join("");
  }

  function drawRoc() {
    const svg = document.getElementById("rocChart");
    const w = 630, h = 440;
    const margin = { top: 28, right: 42, bottom: 62, left: 68 };
    const x = scale(0, 1, margin.left, w - margin.right);
    const y = scale(0, 1, h - margin.bottom, margin.top);
    const plotW = w - margin.left - margin.right;
    svg.setAttribute("viewBox", `0 0 ${w} ${h}`);
    for (const t of [0, 0.25, 0.5, 0.75, 1]) {
      svg.appendChild(svgEl("line", { class: "grid-line", x1: x(t), x2: x(t), y1: margin.top, y2: h - margin.bottom }));
      svg.appendChild(svgEl("line", { class: "grid-line", x1: margin.left, x2: margin.left + plotW, y1: y(t), y2: y(t) }));
      text(svg, t.toFixed(2), x(t), h - margin.bottom + 24, { class: "tick-text", "text-anchor": "middle" });
      text(svg, t.toFixed(2), margin.left - 12, y(t) + 4, { class: "tick-text", "text-anchor": "end" });
    }
    svg.appendChild(svgEl("line", { class: "diag-line", x1: x(0), y1: y(0), x2: x(1), y2: y(1) }));
    const pts = rocPtsRaw.map(([a,b]) => [x(a), y(b)]);
    svg.appendChild(svgEl("path", { class: "roc-line", d: linePath(pts) }));
    pts.forEach(([cx, cy], i) => {
      if (i > 0 && i < pts.length - 1) svg.appendChild(svgEl("circle", { class: "current-dot", cx, cy, r: 4.5 }));
    });
    svg.appendChild(svgEl("line", { class: "axis-line", x1: margin.left, x2: margin.left + plotW, y1: h - margin.bottom, y2: h - margin.bottom }));
    svg.appendChild(svgEl("line", { class: "axis-line", x1: margin.left, x2: margin.left, y1: margin.top, y2: h - margin.bottom }));
    text(svg, "false positive rate", margin.left + plotW / 2, h - 12, { class: "axis-label", "text-anchor": "middle" });
    text(svg, "true positive rate", 18, margin.top + 178, { class: "axis-label", "text-anchor": "middle", transform: `rotate(-90 18 ${margin.top + 178})` });
    text(svg, "domain classifier separates text domains (AUC 0.89)", x(0.38), y(0.88), { class: "callout" });
  }

  function drawScoreDistribution() {
    const svg = document.getElementById("scoreChart");
    const w = 472, h = 185;
    const margin = { top: 12, right: 24, bottom: 34, left: 44 };
    const x = scale(0, 1, margin.left, w - margin.right);
    const y = scale(0, 40, h - margin.bottom, margin.top);
    const baseY = y(0);
    svg.setAttribute("viewBox", `0 0 ${w} ${h}`);
    for (const t of [0, 20, 40]) {
      svg.appendChild(svgEl("line", { class: "grid-line", x1: margin.left, x2: w - margin.right, y1: y(t), y2: y(t) }));
      text(svg, t.toString(), margin.left - 10, y(t) + 4, { class: "tick-text", "text-anchor": "end" });
    }
    const basePts = baseScore.map((v, i) => [x(scoreX[i]), y(v)]);
    const currentPts = currentScore.map((v, i) => [x(scoreX[i]), y(v)]);
    svg.appendChild(svgEl("path", { class: "base-area", d: areaPath(basePts, baseY) }));
    svg.appendChild(svgEl("path", { class: "current-area", d: areaPath(currentPts, baseY) }));
    svg.appendChild(svgEl("line", { class: "axis-line", x1: margin.left, x2: w - margin.right, y1: h - margin.bottom, y2: h - margin.bottom }));
    text(svg, "domain classifier score", margin.left + 160, h - 8, { class: "axis-label", "text-anchor": "middle" });
    text(svg, "score distributions separate", x(0.39), y(36), { class: "warning-text" });
  }

  function drawDescriptor() {
    const svg = document.getElementById("descriptorChart");
    const w = 472, h = 185;
    const barX = 120, barW = 150;
    svg.setAttribute("viewBox", `0 0 ${w} ${h}`);
    descriptors.forEach(([name, value], i) => {
      const y = 14 + i * 23;
      svg.appendChild(svgEl("rect", { class: i === 0 ? "bar-fill hot" : "bar-fill", x: barX, y: y + 4, width: barW * value / 0.34, height: 14, rx: 4 }));
      text(svg, name, barX - 8, y + 16, { class: "bar-label", "text-anchor": "end" });
      text(svg, value.toFixed(2), barX + barW * value / 0.34 + 8, y + 16, { class: "tick-text" });
    });
    const x0 = 318, y0 = 24;
    for (let i = 0; i < 18; i += 1) {
      svg.appendChild(svgEl("circle", { class: "base-dot", cx: x0 + (i % 6) * 11, cy: y0 + 70 + Math.floor(i / 6) * 10 + Math.sin(i) * 4, r: 3.5 }));
      svg.appendChild(svgEl("circle", { class: "current-dot", cx: x0 + 45 + (i % 6) * 11, cy: y0 + 28 + Math.floor(i / 6) * 10 + Math.cos(i) * 4, r: 3.5 }));
    }
    text(svg, "descriptor drift", barX + 76, 154, { class: "axis-label", "text-anchor": "middle" });
    text(svg, "embedding split", x0 + 72, 154, { class: "axis-label", "text-anchor": "middle" });
  }

  drawSummary();
  drawRoc();
  drawScoreDistribution();
  drawDescriptor();
})();
