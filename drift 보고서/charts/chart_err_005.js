(function () {
  const diff = [0.01,0.02,0.01,0.03,0.02,0.04,0.05,0.05,0.06,0.07,0.08,0.09,0.10,0.12,0.13,0.15,0.16,0.18,0.20,0.22,0.24,0.27,0.29,0.32,0.35,0.38,0.41,0.43,0.45,0.47,0.49,0.50];
  const error = [0.08,0.08,0.09,0.09,0.10,0.10,0.11,0.12,0.12,0.13,0.14,0.15,0.16,0.17,0.19,0.20,0.22,0.23,0.25,0.27,0.29,0.31,0.33,0.35,0.38,0.40,0.42,0.43,0.44,0.45,0.46,0.47];
  const warningBound = 0.26;
  const driftBound = 0.36;
  const warningIndex = 22;
  const driftIndex = 26;
  const finalDiff = 0.50;

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
      ["final diff", finalDiff.toFixed(2)],
      ["warning", `t=${warningIndex}`],
      ["drift", `t=${driftIndex}`]
    ];
    document.getElementById("summary").innerHTML = rows.map(([label, value]) => `<div class="metric"><div class="label">${label}</div><div class="value">${value}</div></div>`).join("");
  }

  function drawBoundChart() {
    const svg = document.getElementById("boundChart");
    const w = 630, h = 440;
    const margin = { top: 24, right: 28, bottom: 62, left: 58 };
    const x = scale(1, diff.length, margin.left, w - margin.right);
    const y = scale(-0.10, 0.56, h - margin.bottom, margin.top);
    const plotW = w - margin.left - margin.right;
    svg.setAttribute("viewBox", `0 0 ${w} ${h}`);
    for (const t of [-0.1, 0, 0.2, 0.4]) {
      svg.appendChild(svgEl("line", { class: "grid-line", x1: margin.left, x2: margin.left + plotW, y1: y(t), y2: y(t) }));
      text(svg, t.toFixed(1), margin.left - 12, y(t) + 4, { class: "tick-text", "text-anchor": "end" });
    }
    svg.appendChild(svgEl("line", { class: "warning-line", x1: margin.left, x2: margin.left + plotW, y1: y(warningBound), y2: y(warningBound) }));
    svg.appendChild(svgEl("line", { class: "drift-line", x1: margin.left, x2: margin.left + plotW, y1: y(driftBound), y2: y(driftBound) }));
    svg.appendChild(svgEl("line", { class: "warning-line", x1: margin.left, x2: margin.left + plotW, y1: y(-warningBound), y2: y(-warningBound), opacity: "0.55" }));
    svg.appendChild(svgEl("path", { class: "diff-line", d: linePath(diff.map((v, i) => [x(i + 1), y(v)])) }));
    diff.forEach((v, i) => {
      if (i % 3 === 0 || i + 1 >= warningIndex) {
        svg.appendChild(svgEl("circle", { class: i + 1 >= driftIndex ? "drift-point" : "diff-point", cx: x(i + 1), cy: y(v), r: i + 1 >= driftIndex ? 4.8 : 3.5 }));
      }
    });
    for (const idx of [warningIndex, driftIndex]) {
      svg.appendChild(svgEl("line", { class: "state-line", x1: x(idx), x2: x(idx), y1: margin.top, y2: h - margin.bottom, opacity: idx === warningIndex ? "0.7" : "1" }));
    }
    svg.appendChild(svgEl("line", { class: "axis-line", x1: margin.left, x2: margin.left + plotW, y1: y(0), y2: y(0) }));
    svg.appendChild(svgEl("line", { class: "axis-line", x1: margin.left, x2: margin.left, y1: margin.top, y2: h - margin.bottom }));
    for (const t of [1, 8, 16, 24, 32]) {
      text(svg, t.toString(), x(t), h - margin.bottom + 24, { class: "tick-text", "text-anchor": "middle" });
    }
    text(svg, "time index", margin.left + plotW / 2, h - 12, { class: "axis-label", "text-anchor": "middle" });
    text(svg, "mean difference", 16, margin.top + 178, { class: "axis-label", "text-anchor": "middle", transform: `rotate(-90 16 ${margin.top + 178})` });
    text(svg, "warning bound", x(3), y(warningBound) - 8, { class: "warning-text" });
    text(svg, "drift bound", x(3), y(driftBound) - 8, { class: "drift-text" });
    text(svg, "recent mean exceeds Hoeffding bound", x(14), y(0.51), { class: "callout" });
  }

  function drawErrorChart() {
    const svg = document.getElementById("errorChart");
    const w = 472, h = 185;
    const margin = { top: 12, right: 22, bottom: 34, left: 48 };
    const x = scale(1, error.length, margin.left, w - margin.right);
    const y = scale(0, 0.52, h - margin.bottom, margin.top);
    const plotW = w - margin.left - margin.right;
    svg.setAttribute("viewBox", `0 0 ${w} ${h}`);
    for (const t of [0, 0.15, 0.30, 0.45]) {
      svg.appendChild(svgEl("line", { class: "grid-line", x1: margin.left, x2: margin.left + plotW, y1: y(t), y2: y(t) }));
      text(svg, t.toFixed(2), margin.left - 10, y(t) + 4, { class: "tick-text", "text-anchor": "end" });
    }
    svg.appendChild(svgEl("path", { class: "error-line", d: linePath(error.map((v, i) => [x(i + 1), y(v)])) }));
    svg.appendChild(svgEl("line", { class: "state-line", x1: x(driftIndex), x2: x(driftIndex), y1: margin.top, y2: h - margin.bottom }));
    for (const idx of [1, 8, 16, 24, 32]) {
      svg.appendChild(svgEl("circle", { class: "error-point", cx: x(idx), cy: y(error[idx - 1]), r: 3.5 }));
    }
    svg.appendChild(svgEl("line", { class: "axis-line", x1: margin.left, x2: margin.left + plotW, y1: h - margin.bottom, y2: h - margin.bottom }));
    text(svg, "weighted error trend", margin.left + 160, h - 8, { class: "axis-label", "text-anchor": "middle" });
    text(svg, "recent error 상승", x(19), y(0.43), { class: "drift-text" });
  }

  function drawTimeline() {
    const svg = document.getElementById("markerTimeline");
    const w = 472, h = 185;
    const margin = { top: 30, right: 24, bottom: 38, left: 48 };
    const x = scale(1, 32, margin.left, w - margin.right);
    const y = 68;
    svg.setAttribute("viewBox", `0 0 ${w} ${h}`);
    svg.appendChild(svgEl("rect", { class: "normal-fill", x: x(1), y, width: x(warningIndex) - x(1), height: 28, rx: 5 }));
    svg.appendChild(svgEl("rect", { class: "warning-fill", x: x(warningIndex), y, width: x(driftIndex) - x(warningIndex), height: 28, rx: 5 }));
    svg.appendChild(svgEl("rect", { class: "drift-fill", x: x(driftIndex), y, width: x(32) - x(driftIndex), height: 28, rx: 5 }));
    svg.appendChild(svgEl("rect", { class: "two-sided-fill", x: x(1), y: y + 48, width: x(32) - x(1), height: 18, rx: 5 }));
    svg.appendChild(svgEl("line", { class: "state-line", x1: x(driftIndex), x2: x(driftIndex), y1: margin.top, y2: h - margin.bottom }));
    svg.appendChild(svgEl("circle", { class: "drift-point", cx: x(driftIndex), cy: y + 14, r: 7 }));
    text(svg, "normal", x(11), y + 19, { class: "bar-label", "text-anchor": "middle" });
    text(svg, "warning", x(24), y + 19, { class: "bar-label", "text-anchor": "middle" });
    text(svg, "drift", x(29), y + 19, { class: "bar-label", "text-anchor": "middle" });
    text(svg, "two-sided guard band", x(16), y + 62, { class: "bar-label", "text-anchor": "middle" });
    for (const t of [1, 8, 16, 24, 32]) {
      text(svg, t.toString(), x(t), h - margin.bottom + 22, { class: "tick-text", "text-anchor": "middle" });
    }
    svg.appendChild(svgEl("line", { class: "axis-line", x1: margin.left, x2: w - margin.right, y1: h - margin.bottom, y2: h - margin.bottom }));
    text(svg, "HDDM warning and drift markers", margin.left + 180, h - 6, { class: "axis-label", "text-anchor": "middle" });
  }

  drawSummary();
  drawBoundChart();
  drawErrorChart();
  drawTimeline();
})();
