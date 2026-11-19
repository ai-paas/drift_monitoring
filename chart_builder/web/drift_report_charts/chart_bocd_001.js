(function () {
  const times = Array.from({ length: 32 }, (_, i) => i + 1);
  const cpProb = times.map((t) => {
    const p1 = Math.exp(-Math.pow((t - 18) / 2.4, 2)) * 0.82;
    const p2 = Math.exp(-Math.pow((t - 27) / 2.0, 2)) * 0.56;
    return Math.min(0.94, 0.05 + p1 + p2);
  });
  const stream = [0.48,0.51,0.49,0.52,0.50,0.53,0.55,0.54,0.56,0.57,0.55,0.58,0.59,0.60,0.62,0.63,0.66,0.79,0.83,0.86,0.87,0.89,0.88,0.91,0.92,0.94,1.04,1.07,1.10,1.12,1.13,1.15];
  const changeIndex = 18;
  const secondaryIndex = 27;
  const peakProb = Math.max(...cpProb);

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
  function color(v) {
    const clamped = Math.max(0, Math.min(1, v));
    const low = [217, 230, 239];
    const mid = [201, 149, 47];
    const high = [185, 90, 80];
    const a = clamped < 0.55 ? low : mid;
    const b = clamped < 0.55 ? mid : high;
    const f = clamped < 0.55 ? clamped / 0.55 : (clamped - 0.55) / 0.45;
    const c = a.map((x, i) => Math.round(x + (b[i] - x) * f));
    return `rgb(${c[0]},${c[1]},${c[2]})`;
  }

  function drawSummary() {
    const rows = [
      ["peak cp prob", peakProb.toFixed(2)],
      ["primary change", `t=${changeIndex}`],
      ["run length", "reset"]
    ];
    document.getElementById("summary").innerHTML = rows.map(([label, value]) => `<div class="metric"><div class="label">${label}</div><div class="value">${value}</div></div>`).join("");
  }

  function drawCpHeatmap() {
    const svg = document.getElementById("cpHeatmap");
    const w = 630, h = 440;
    const margin = { top: 24, right: 28, bottom: 62, left: 58 };
    const plotW = w - margin.left - margin.right;
    const plotH = h - margin.top - margin.bottom;
    const cellW = plotW / cpProb.length;
    const rows = 12;
    const cellH = plotH / rows;
    svg.setAttribute("viewBox", `0 0 ${w} ${h}`);
    for (let r = 0; r < rows; r += 1) {
      for (let c = 0; c < cpProb.length; c += 1) {
        const bandCenter = 1 - (r + 0.5) / rows;
        const intensity = Math.max(0, cpProb[c] - Math.abs(bandCenter - cpProb[c]) * 0.65);
        svg.appendChild(svgEl("rect", {
          class: "cell",
          x: margin.left + c * cellW,
          y: margin.top + r * cellH,
          width: cellW,
          height: cellH,
          fill: color(intensity)
        }));
      }
    }
    svg.appendChild(svgEl("line", { class: "marker-line", x1: margin.left + (changeIndex - 0.5) * cellW, x2: margin.left + (changeIndex - 0.5) * cellW, y1: margin.top, y2: h - margin.bottom }));
    svg.appendChild(svgEl("line", { class: "marker-line", x1: margin.left + (secondaryIndex - 0.5) * cellW, x2: margin.left + (secondaryIndex - 0.5) * cellW, y1: margin.top, y2: h - margin.bottom, opacity: "0.75" }));
    svg.appendChild(svgEl("line", { class: "axis-line", x1: margin.left, x2: margin.left + plotW, y1: h - margin.bottom, y2: h - margin.bottom }));
    svg.appendChild(svgEl("line", { class: "axis-line", x1: margin.left, x2: margin.left, y1: margin.top, y2: h - margin.bottom }));
    for (const t of [1, 8, 16, 24, 32]) {
      text(svg, t.toString(), margin.left + (t - 0.5) * cellW, h - margin.bottom + 24, { class: "tick-text", "text-anchor": "middle" });
    }
    for (const [label, y] of [["0.0", h - margin.bottom], ["0.5", margin.top + plotH * 0.5], ["1.0", margin.top]]) {
      text(svg, label, margin.left - 12, y + 4, { class: "tick-text", "text-anchor": "end" });
    }
    text(svg, "time index", margin.left + plotW / 2, h - 12, { class: "axis-label", "text-anchor": "middle" });
    text(svg, "P(change point)", 16, margin.top + 178, { class: "axis-label", "text-anchor": "middle", transform: `rotate(-90 16 ${margin.top + 178})` });
    text(svg, "posterior spike", margin.left + (changeIndex - 3) * cellW, margin.top + 30, { class: "warning-text" });
  }

  function drawRunLength() {
    const svg = document.getElementById("runLengthHeatmap");
    const w = 472, h = 185;
    const margin = { top: 12, right: 22, bottom: 34, left: 48 };
    const cols = 32;
    const rows = 12;
    const plotW = w - margin.left - margin.right;
    const plotH = h - margin.top - margin.bottom;
    const cellW = plotW / cols;
    const cellH = plotH / rows;
    svg.setAttribute("viewBox", `0 0 ${w} ${h}`);
    for (let c = 0; c < cols; c += 1) {
      const t = c + 1;
      const expectedRun = t < changeIndex ? t : t < secondaryIndex ? t - changeIndex + 1 : t - secondaryIndex + 1;
      for (let r = 0; r < rows; r += 1) {
        const runBucket = rows - r;
        const distance = Math.abs(runBucket - expectedRun / 2.4);
        const resetBoost = (t === changeIndex || t === secondaryIndex) && r > rows - 3 ? 0.8 : 0;
        const intensity = Math.max(0.04, Math.exp(-distance * 0.8) * 0.85 + resetBoost);
        svg.appendChild(svgEl("rect", {
          class: "cell",
          x: margin.left + c * cellW,
          y: margin.top + r * cellH,
          width: cellW,
          height: cellH,
          fill: color(Math.min(1, intensity))
        }));
      }
    }
    svg.appendChild(svgEl("line", { class: "marker-line", x1: margin.left + (changeIndex - 0.5) * cellW, x2: margin.left + (changeIndex - 0.5) * cellW, y1: margin.top, y2: h - margin.bottom }));
    svg.appendChild(svgEl("line", { class: "axis-line", x1: margin.left, x2: margin.left + plotW, y1: h - margin.bottom, y2: h - margin.bottom }));
    text(svg, "run length posterior resets", margin.left + 142, h - 8, { class: "axis-label", "text-anchor": "middle" });
    text(svg, "reset", margin.left + (changeIndex + 1) * cellW, margin.top + 18, { class: "warning-text" });
  }

  function drawStreamTrend() {
    const svg = document.getElementById("streamTrend");
    const w = 472, h = 185;
    const margin = { top: 12, right: 22, bottom: 34, left: 48 };
    const x = scale(1, stream.length, margin.left, w - margin.right);
    const y = scale(0.40, 1.20, h - margin.bottom, margin.top);
    const plotW = w - margin.left - margin.right;
    svg.setAttribute("viewBox", `0 0 ${w} ${h}`);
    for (const t of [0.5, 0.8, 1.1]) {
      svg.appendChild(svgEl("line", { class: "grid-line", x1: margin.left, x2: margin.left + plotW, y1: y(t), y2: y(t) }));
      text(svg, t.toFixed(1), margin.left - 10, y(t) + 4, { class: "tick-text", "text-anchor": "end" });
    }
    svg.appendChild(svgEl("path", { class: "stream-line", d: linePath(stream.map((v, i) => [x(i + 1), y(v)])) }));
    svg.appendChild(svgEl("line", { class: "mean-line", x1: margin.left, x2: x(changeIndex), y1: y(0.55), y2: y(0.55) }));
    svg.appendChild(svgEl("line", { class: "mean-line", x1: x(changeIndex), x2: x(secondaryIndex), y1: y(0.87), y2: y(0.87) }));
    svg.appendChild(svgEl("line", { class: "mean-line", x1: x(secondaryIndex), x2: w - margin.right, y1: y(1.10), y2: y(1.10) }));
    for (const t of [changeIndex, secondaryIndex]) {
      svg.appendChild(svgEl("line", { class: "marker-line", x1: x(t), x2: x(t), y1: margin.top, y2: h - margin.bottom }));
      svg.appendChild(svgEl("circle", { class: "marker-point", cx: x(t), cy: y(stream[t - 1]), r: 6 }));
    }
    svg.appendChild(svgEl("line", { class: "axis-line", x1: margin.left, x2: margin.left + plotW, y1: h - margin.bottom, y2: h - margin.bottom }));
    text(svg, "stream with change markers", margin.left + 156, h - 8, { class: "axis-label", "text-anchor": "middle" });
    text(svg, "mean shift", x(19), y(1.05), { class: "warning-text" });
  }

  drawSummary();
  drawCpHeatmap();
  drawRunLength();
  drawStreamTrend();
})();
