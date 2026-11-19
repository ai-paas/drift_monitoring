(function () {
  const layers = ["conv1", "block1", "block2", "block3", "head"];
  const channels = Array.from({ length: 12 }, (_, i) => `c${i + 1}`);
  const driftScores = [
    [0.12,0.18,0.16,0.20,0.24,0.22,0.19,0.25,0.28,0.21,0.18,0.16],
    [0.20,0.24,0.27,0.30,0.33,0.29,0.31,0.35,0.38,0.34,0.30,0.28],
    [0.31,0.36,0.42,0.48,0.54,0.57,0.62,0.66,0.59,0.52,0.45,0.40],
    [0.42,0.50,0.58,0.66,0.74,0.81,0.88,0.92,0.84,0.76,0.68,0.56],
    [0.28,0.33,0.38,0.44,0.49,0.52,0.55,0.58,0.53,0.47,0.40,0.35]
  ];
  const baseHist = [4,9,16,28,35,31,22,13,7,3];
  const currentHist = [2,5,9,16,24,31,34,27,18,9];
  const selectedLayer = "block3";
  const maxScore = 0.92;

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
  function color(v) {
    const low = [222, 233, 241];
    const mid = [201, 149, 47];
    const high = [185, 90, 80];
    const a = v < 0.55 ? low : mid;
    const b = v < 0.55 ? mid : high;
    const f = v < 0.55 ? v / 0.55 : (v - 0.55) / 0.45;
    const c = a.map((x, i) => Math.round(x + (b[i] - x) * f));
    return `rgb(${c[0]},${c[1]},${c[2]})`;
  }

  function drawSummary() {
    const rows = [
      ["max drift", maxScore.toFixed(2)],
      ["hot layer", selectedLayer],
      ["method", "MMD/KS"]
    ];
    document.getElementById("summary").innerHTML = rows.map(([label, value]) => `<div class="metric"><div class="label">${label}</div><div class="value">${value}</div></div>`).join("");
  }

  function drawHeatmap() {
    const svg = document.getElementById("heatmapChart");
    const w = 630, h = 440;
    const margin = { top: 30, right: 28, bottom: 72, left: 78 };
    const plotW = w - margin.left - margin.right;
    const plotH = h - margin.top - margin.bottom;
    const cellW = plotW / channels.length;
    const cellH = plotH / layers.length;
    svg.setAttribute("viewBox", `0 0 ${w} ${h}`);
    layers.forEach((layer, r) => {
      text(svg, layer, margin.left - 12, margin.top + r * cellH + cellH / 2 + 5, { class: "bar-label", "text-anchor": "end" });
      channels.forEach((channel, c) => {
        const score = driftScores[r][c];
        svg.appendChild(svgEl("rect", { class: "cell", x: margin.left + c * cellW, y: margin.top + r * cellH, width: cellW, height: cellH, fill: color(score) }));
        if (score >= 0.80) text(svg, score.toFixed(2), margin.left + c * cellW + cellW / 2, margin.top + r * cellH + cellH / 2 + 4, { class: "bar-label", "text-anchor": "middle" });
      });
    });
    for (const idx of [1, 4, 8, 12]) {
      text(svg, `c${idx}`, margin.left + (idx - 0.5) * cellW, h - margin.bottom + 24, { class: "tick-text", "text-anchor": "middle" });
    }
    svg.appendChild(svgEl("rect", { class: "layer-ring", x: margin.left, y: margin.top + 3 * cellH, width: plotW, height: cellH, rx: 3 }));
    svg.appendChild(svgEl("line", { class: "axis-line", x1: margin.left, x2: margin.left + plotW, y1: margin.top + plotH, y2: margin.top + plotH }));
    text(svg, "channel index", margin.left + plotW / 2, h - 16, { class: "axis-label", "text-anchor": "middle" });
    text(svg, "layer", 18, margin.top + plotH / 2, { class: "axis-label", "text-anchor": "middle", transform: `rotate(-90 18 ${margin.top + plotH / 2})` });
    text(svg, "block3 channels show concentrated drift", margin.left + 238, margin.top - 8, { class: "warning-text", "text-anchor": "middle" });
  }

  function drawActivation() {
    const svg = document.getElementById("activationChart");
    const w = 472, h = 185;
    const margin = { top: 12, right: 24, bottom: 34, left: 44 };
    const x = scale(0, baseHist.length, margin.left, w - margin.right);
    const y = scale(0, 40, h - margin.bottom, margin.top);
    const barW = (w - margin.left - margin.right) / baseHist.length;
    svg.setAttribute("viewBox", `0 0 ${w} ${h}`);
    for (const t of [0, 20, 40]) {
      svg.appendChild(svgEl("line", { class: "grid-line", x1: margin.left, x2: w - margin.right, y1: y(t), y2: y(t) }));
      text(svg, t.toString(), margin.left - 10, y(t) + 4, { class: "tick-text", "text-anchor": "end" });
    }
    baseHist.forEach((v, i) => {
      svg.appendChild(svgEl("rect", { class: "base-bar", x: x(i) + 2, y: y(v), width: barW * 0.42, height: y(0) - y(v), rx: 2 }));
      svg.appendChild(svgEl("rect", { class: "current-bar", x: x(i) + barW * 0.48, y: y(currentHist[i]), width: barW * 0.42, height: y(0) - y(currentHist[i]), rx: 2 }));
    });
    svg.appendChild(svgEl("line", { class: "axis-line", x1: margin.left, x2: w - margin.right, y1: h - margin.bottom, y2: h - margin.bottom }));
    text(svg, "activation bin", margin.left + 160, h - 8, { class: "axis-label", "text-anchor": "middle" });
    text(svg, "current activation shifts right", x(5), y(36), { class: "warning-text" });
  }

  function drawProjection() {
    const svg = document.getElementById("projectionChart");
    const w = 472, h = 185;
    const margin = { top: 12, right: 24, bottom: 34, left: 44 };
    const x = scale(-2.2, 2.8, margin.left, w - margin.right);
    const y = scale(-1.8, 1.8, h - margin.bottom, margin.top);
    svg.setAttribute("viewBox", `0 0 ${w} ${h}`);
    svg.appendChild(svgEl("line", { class: "grid-line", x1: margin.left, x2: w - margin.right, y1: y(0), y2: y(0) }));
    svg.appendChild(svgEl("line", { class: "grid-line", x1: x(0), x2: x(0), y1: margin.top, y2: h - margin.bottom }));
    for (let i = 0; i < 34; i += 1) {
      const bx = -1.35 + (i % 7) * 0.19 + Math.sin(i) * 0.08;
      const by = -0.35 + Math.floor(i / 7) * 0.17 + Math.cos(i * 1.7) * 0.08;
      const cx = 0.82 + (i % 7) * 0.21 + Math.sin(i * 1.3) * 0.08;
      const cy = 0.15 + Math.floor(i / 7) * 0.18 + Math.cos(i * 1.4) * 0.08;
      svg.appendChild(svgEl("circle", { class: "base-dot", cx: x(bx), cy: y(by), r: 4 }));
      svg.appendChild(svgEl("circle", { class: "current-dot", cx: x(cx), cy: y(cy), r: 4 }));
    }
    svg.appendChild(svgEl("line", { class: "axis-line", x1: margin.left, x2: w - margin.right, y1: h - margin.bottom, y2: h - margin.bottom }));
    text(svg, "UMAP-1", margin.left + 160, h - 8, { class: "axis-label", "text-anchor": "middle" });
    text(svg, "layer embedding separates", x(0.78), y(1.52), { class: "callout" });
  }

  drawSummary();
  drawHeatmap();
  drawActivation();
  drawProjection();
})();
