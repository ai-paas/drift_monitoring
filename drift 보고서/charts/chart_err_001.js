(function () {
  const error = [0.08,0.09,0.08,0.10,0.09,0.10,0.11,0.10,0.12,0.13,0.12,0.14,0.15,0.16,0.17,0.18,0.19,0.21,0.22,0.24,0.26,0.28,0.30,0.33,0.35,0.37,0.39,0.41,0.42,0.44,0.45,0.46];
  const warning = 0.27;
  const drift = 0.36;
  const warningIndex = 22;
  const driftIndex = 26;
  const finalError = 0.46;

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
      ["final error", finalError.toFixed(2)],
      ["warning start", `t=${warningIndex}`],
      ["drift alarm", `t=${driftIndex}`]
    ];
    document.getElementById("summary").innerHTML = rows.map(([label, value]) => `<div class="metric"><div class="label">${label}</div><div class="value">${value}</div></div>`).join("");
  }

  function drawErrorTrend() {
    const svg = document.getElementById("errorTrend");
    const w = 630, h = 440;
    const margin = { top: 24, right: 28, bottom: 62, left: 58 };
    const x = scale(1, error.length, margin.left, w - margin.right);
    const y = scale(0, 0.52, h - margin.bottom, margin.top);
    const plotW = w - margin.left - margin.right;
    svg.setAttribute("viewBox", `0 0 ${w} ${h}`);
    for (const t of [0, 0.1, 0.2, 0.3, 0.4, 0.5]) {
      svg.appendChild(svgEl("line", { class: "grid-line", x1: margin.left, x2: margin.left + plotW, y1: y(t), y2: y(t) }));
      text(svg, t.toFixed(1), margin.left - 12, y(t) + 4, { class: "tick-text", "text-anchor": "end" });
    }
    svg.appendChild(svgEl("line", { class: "warning-line", x1: margin.left, x2: margin.left + plotW, y1: y(warning), y2: y(warning) }));
    svg.appendChild(svgEl("line", { class: "drift-line", x1: margin.left, x2: margin.left + plotW, y1: y(drift), y2: y(drift) }));
    svg.appendChild(svgEl("path", { class: "error-line", d: linePath(error.map((v, i) => [x(i + 1), y(v)])) }));
    error.forEach((v, i) => {
      if (i % 3 === 0 || i + 1 >= warningIndex) {
        svg.appendChild(svgEl("circle", { class: i + 1 >= driftIndex ? "drift-point" : "error-point", cx: x(i + 1), cy: y(v), r: i + 1 >= driftIndex ? 4.8 : 3.6 }));
      }
    });
    for (const idx of [warningIndex, driftIndex]) {
      svg.appendChild(svgEl("line", { class: "state-line", x1: x(idx), x2: x(idx), y1: margin.top, y2: h - margin.bottom }));
    }
    svg.appendChild(svgEl("line", { class: "axis-line", x1: margin.left, x2: margin.left + plotW, y1: h - margin.bottom, y2: h - margin.bottom }));
    svg.appendChild(svgEl("line", { class: "axis-line", x1: margin.left, x2: margin.left, y1: margin.top, y2: h - margin.bottom }));
    for (const t of [1, 8, 16, 24, 32]) {
      text(svg, t.toString(), x(t), h - margin.bottom + 24, { class: "tick-text", "text-anchor": "middle" });
    }
    text(svg, "time index", margin.left + plotW / 2, h - 12, { class: "axis-label", "text-anchor": "middle" });
    text(svg, "error rate", 16, margin.top + 178, { class: "axis-label", "text-anchor": "middle", transform: `rotate(-90 16 ${margin.top + 178})` });
    text(svg, "warning threshold", x(3), y(warning) - 8, { class: "warning-text" });
    text(svg, "drift threshold", x(3), y(drift) - 8, { class: "drift-text" });
    text(svg, "drift alarm", x(driftIndex) + 12, y(0.47), { class: "drift-text" });
  }

  function drawThreshold() {
    const svg = document.getElementById("thresholdChart");
    const w = 472, h = 185;
    const margin = { top: 12, right: 24, bottom: 34, left: 58 };
    const x = scale(1, error.length, margin.left, w - margin.right);
    const y = scale(-0.12, 0.28, h - margin.bottom, margin.top);
    const marginToDrift = error.map((v) => v - drift);
    const plotW = w - margin.left - margin.right;
    svg.setAttribute("viewBox", `0 0 ${w} ${h}`);
    for (const t of [-0.1, 0, 0.1, 0.2]) {
      svg.appendChild(svgEl("line", { class: "grid-line", x1: margin.left, x2: margin.left + plotW, y1: y(t), y2: y(t) }));
      text(svg, t.toFixed(1), margin.left - 10, y(t) + 4, { class: "tick-text", "text-anchor": "end" });
    }
    svg.appendChild(svgEl("line", { class: "drift-line", x1: margin.left, x2: margin.left + plotW, y1: y(0), y2: y(0) }));
    svg.appendChild(svgEl("path", { class: "error-line", d: linePath(marginToDrift.map((v, i) => [x(i + 1), y(v)])) }));
    svg.appendChild(svgEl("line", { class: "state-line", x1: x(driftIndex), x2: x(driftIndex), y1: margin.top, y2: h - margin.bottom }));
    svg.appendChild(svgEl("line", { class: "axis-line", x1: margin.left, x2: margin.left + plotW, y1: h - margin.bottom, y2: h - margin.bottom }));
    text(svg, "p+s minus drift threshold", margin.left + 158, h - 8, { class: "axis-label", "text-anchor": "middle" });
    text(svg, "0 초과: drift", x(19), y(0.18), { class: "drift-text" });
  }

  function drawTimeline() {
    const svg = document.getElementById("bufferTimeline");
    const w = 472, h = 185;
    const margin = { top: 32, right: 24, bottom: 38, left: 48 };
    const x = scale(1, 32, margin.left, w - margin.right);
    const y = 74;
    svg.setAttribute("viewBox", `0 0 ${w} ${h}`);
    svg.appendChild(svgEl("rect", { class: "normal-fill", x: x(1), y, width: x(warningIndex) - x(1), height: 30, rx: 5 }));
    svg.appendChild(svgEl("rect", { class: "warning-fill", x: x(warningIndex), y, width: x(driftIndex) - x(warningIndex), height: 30, rx: 5 }));
    svg.appendChild(svgEl("rect", { class: "drift-fill", x: x(driftIndex), y, width: x(32) - x(driftIndex), height: 30, rx: 5 }));
    svg.appendChild(svgEl("rect", { class: "buffer-fill", x: x(warningIndex), y: y - 22, width: x(driftIndex) - x(warningIndex), height: 12, rx: 4 }));
    svg.appendChild(svgEl("line", { class: "state-line", x1: x(driftIndex), x2: x(driftIndex), y1: margin.top, y2: h - margin.bottom }));
    svg.appendChild(svgEl("circle", { class: "drift-point", cx: x(driftIndex), cy: y + 15, r: 7 }));
    text(svg, "normal", x(11), y + 20, { class: "bar-label", "text-anchor": "middle" });
    text(svg, "warning", x(24), y + 20, { class: "bar-label", "text-anchor": "middle" });
    text(svg, "drift", x(29), y + 20, { class: "bar-label", "text-anchor": "middle" });
    text(svg, "buffer", x(24), y - 12, { class: "bar-label", "text-anchor": "middle" });
    for (const t of [1, 8, 16, 24, 32]) {
      text(svg, t.toString(), x(t), h - margin.bottom + 22, { class: "tick-text", "text-anchor": "middle" });
    }
    svg.appendChild(svgEl("line", { class: "axis-line", x1: margin.left, x2: w - margin.right, y1: h - margin.bottom, y2: h - margin.bottom }));
    text(svg, "DDM state timeline", margin.left + 180, h - 6, { class: "axis-label", "text-anchor": "middle" });
  }

  drawSummary();
  drawErrorTrend();
  drawThreshold();
  drawTimeline();
})();
