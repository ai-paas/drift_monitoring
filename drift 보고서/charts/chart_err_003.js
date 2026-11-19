(function () {
  const score = [1.00,0.99,0.98,0.97,0.98,0.96,0.95,0.94,0.92,0.91,0.89,0.88,0.86,0.84,0.82,0.80,0.78,0.76,0.74,0.72,0.70,0.68,0.66,0.63,0.60,0.57,0.54,0.51,0.49,0.47,0.45,0.44];
  const errorEvents = [3,8,13,17,20,22,24,25,27,28,29,30,31,32];
  const warningThreshold = 0.90;
  const driftThreshold = 0.75;
  const warningIndex = 11;
  const driftIndex = 19;
  const finalScore = 0.44;

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
      ["final score", finalScore.toFixed(2)],
      ["warning", `t=${warningIndex}`],
      ["drift", `t=${driftIndex}`]
    ];
    document.getElementById("summary").innerHTML = rows.map(([label, value]) => `<div class="metric"><div class="label">${label}</div><div class="value">${value}</div></div>`).join("");
  }

  function drawDistanceTrend() {
    const svg = document.getElementById("distanceTrend");
    const w = 630, h = 440;
    const margin = { top: 24, right: 28, bottom: 62, left: 58 };
    const x = scale(1, score.length, margin.left, w - margin.right);
    const y = scale(0.35, 1.05, h - margin.bottom, margin.top);
    const plotW = w - margin.left - margin.right;
    svg.setAttribute("viewBox", `0 0 ${w} ${h}`);
    for (const t of [0.4, 0.6, 0.8, 1.0]) {
      svg.appendChild(svgEl("line", { class: "grid-line", x1: margin.left, x2: margin.left + plotW, y1: y(t), y2: y(t) }));
      text(svg, t.toFixed(1), margin.left - 12, y(t) + 4, { class: "tick-text", "text-anchor": "end" });
    }
    svg.appendChild(svgEl("line", { class: "warning-line", x1: margin.left, x2: margin.left + plotW, y1: y(warningThreshold), y2: y(warningThreshold) }));
    svg.appendChild(svgEl("line", { class: "drift-line", x1: margin.left, x2: margin.left + plotW, y1: y(driftThreshold), y2: y(driftThreshold) }));
    svg.appendChild(svgEl("path", { class: "distance-line", d: linePath(score.map((v, i) => [x(i + 1), y(v)])) }));
    score.forEach((v, i) => {
      if (i % 3 === 0 || i + 1 >= warningIndex) {
        svg.appendChild(svgEl("circle", { class: i + 1 >= driftIndex ? "drift-point" : "distance-point", cx: x(i + 1), cy: y(v), r: i + 1 >= driftIndex ? 4.8 : 3.5 }));
      }
    });
    for (const idx of [warningIndex, driftIndex]) {
      svg.appendChild(svgEl("line", { class: "state-line", x1: x(idx), x2: x(idx), y1: margin.top, y2: h - margin.bottom, opacity: idx === warningIndex ? "0.7" : "1" }));
    }
    svg.appendChild(svgEl("line", { class: "axis-line", x1: margin.left, x2: margin.left + plotW, y1: h - margin.bottom, y2: h - margin.bottom }));
    svg.appendChild(svgEl("line", { class: "axis-line", x1: margin.left, x2: margin.left, y1: margin.top, y2: h - margin.bottom }));
    for (const t of [1, 8, 16, 24, 32]) {
      text(svg, t.toString(), x(t), h - margin.bottom + 24, { class: "tick-text", "text-anchor": "middle" });
    }
    text(svg, "time index", margin.left + plotW / 2, h - 12, { class: "axis-label", "text-anchor": "middle" });
    text(svg, "distance score ratio", 16, margin.top + 178, { class: "axis-label", "text-anchor": "middle", transform: `rotate(-90 16 ${margin.top + 178})` });
    text(svg, "warning 0.90", x(3), y(warningThreshold) - 8, { class: "warning-text" });
    text(svg, "drift 0.75", x(3), y(driftThreshold) - 8, { class: "drift-text" });
    text(svg, "오류 간격 감소", x(20), y(0.48), { class: "drift-text" });
  }

  function drawTimeline() {
    const svg = document.getElementById("timelineChart");
    const w = 472, h = 185;
    const margin = { top: 32, right: 24, bottom: 38, left: 48 };
    const x = scale(1, 32, margin.left, w - margin.right);
    const y = 74;
    svg.setAttribute("viewBox", `0 0 ${w} ${h}`);
    svg.appendChild(svgEl("rect", { class: "normal-fill", x: x(1), y, width: x(warningIndex) - x(1), height: 30, rx: 5 }));
    svg.appendChild(svgEl("rect", { class: "warning-fill", x: x(warningIndex), y, width: x(driftIndex) - x(warningIndex), height: 30, rx: 5 }));
    svg.appendChild(svgEl("rect", { class: "drift-fill", x: x(driftIndex), y, width: x(32) - x(driftIndex), height: 30, rx: 5 }));
    svg.appendChild(svgEl("line", { class: "state-line", x1: x(driftIndex), x2: x(driftIndex), y1: margin.top, y2: h - margin.bottom }));
    svg.appendChild(svgEl("circle", { class: "drift-point", cx: x(driftIndex), cy: y + 15, r: 7 }));
    text(svg, "normal", x(6), y + 20, { class: "bar-label", "text-anchor": "middle" });
    text(svg, "warning", x(15), y + 20, { class: "bar-label", "text-anchor": "middle" });
    text(svg, "drift", x(25), y + 20, { class: "bar-label", "text-anchor": "middle" });
    for (const t of [1, 8, 16, 24, 32]) {
      text(svg, t.toString(), x(t), h - margin.bottom + 22, { class: "tick-text", "text-anchor": "middle" });
    }
    svg.appendChild(svgEl("line", { class: "axis-line", x1: margin.left, x2: w - margin.right, y1: h - margin.bottom, y2: h - margin.bottom }));
    text(svg, "EDDM state timeline", margin.left + 180, h - 6, { class: "axis-label", "text-anchor": "middle" });
  }

  function drawEventRaster() {
    const svg = document.getElementById("eventRaster");
    const w = 472, h = 185;
    const margin = { top: 22, right: 24, bottom: 38, left: 48 };
    const x = scale(1, 32, margin.left, w - margin.right);
    svg.setAttribute("viewBox", `0 0 ${w} ${h}`);
    for (let row = 0; row < 4; row += 1) {
      const y = margin.top + row * 27;
      svg.appendChild(svgEl("line", { class: "grid-line", x1: margin.left, x2: w - margin.right, y1: y + 18, y2: y + 18 }));
      for (const t of errorEvents) {
        const jitter = ((t + row) % 4) * 2;
        const hot = t >= driftIndex;
        svg.appendChild(svgEl("line", { class: hot ? "event-mark hot" : "event-mark", x1: x(t), x2: x(t), y1: y + 2 + jitter, y2: y + 18 + jitter }));
      }
    }
    svg.appendChild(svgEl("line", { class: "state-line", x1: x(driftIndex), x2: x(driftIndex), y1: margin.top, y2: 138 }));
    svg.appendChild(svgEl("line", { class: "axis-line", x1: margin.left, x2: w - margin.right, y1: h - margin.bottom, y2: h - margin.bottom }));
    for (const t of [1, 8, 16, 24, 32]) {
      text(svg, t.toString(), x(t), h - margin.bottom + 22, { class: "tick-text", "text-anchor": "middle" });
    }
    text(svg, "error events become denser", margin.left + 165, h - 6, { class: "axis-label", "text-anchor": "middle" });
    text(svg, "밀집", x(26), margin.top + 16, { class: "drift-text" });
  }

  drawSummary();
  drawDistanceTrend();
  drawTimeline();
  drawEventRaster();
})();
