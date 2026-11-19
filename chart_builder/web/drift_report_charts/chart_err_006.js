(function () {
  const recent = [0.91,0.90,0.91,0.89,0.90,0.88,0.87,0.86,0.85,0.84,0.82,0.80,0.79,0.77,0.75,0.73,0.72,0.70,0.69,0.68,0.67,0.66,0.65,0.65,0.64,0.64,0.65,0.66,0.67,0.68];
  const overall = [0.91,0.91,0.91,0.91,0.90,0.90,0.90,0.90,0.89,0.89,0.89,0.88,0.88,0.87,0.87,0.86,0.86,0.85,0.84,0.84,0.83,0.82,0.82,0.81,0.80,0.80,0.79,0.79,0.78,0.78];
  const warningIndex = 15;
  const driftIndex = 20;
  const warnThreshold = 0.10;
  const driftThreshold = 0.15;

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
      ["recent acc", "0.68"],
      ["overall acc", "0.78"],
      ["drift", `t=${driftIndex}`]
    ];
    document.getElementById("summary").innerHTML = rows.map(([label, value]) => `<div class="metric"><div class="label">${label}</div><div class="value">${value}</div></div>`).join("");
  }

  function drawAccuracy() {
    const svg = document.getElementById("accuracyChart");
    const w = 630, h = 440;
    const margin = { top: 24, right: 30, bottom: 62, left: 58 };
    const x = scale(1, recent.length, margin.left, w - margin.right);
    const y = scale(0.58, 0.94, h - margin.bottom, margin.top);
    const plotW = w - margin.left - margin.right;
    svg.setAttribute("viewBox", `0 0 ${w} ${h}`);

    for (const t of [0.60, 0.70, 0.80, 0.90]) {
      svg.appendChild(svgEl("line", { class: "grid-line", x1: margin.left, x2: margin.left + plotW, y1: y(t), y2: y(t) }));
      text(svg, t.toFixed(2), margin.left - 12, y(t) + 4, { class: "tick-text", "text-anchor": "end" });
    }
    svg.appendChild(svgEl("path", { class: "recent-line", d: linePath(recent.map((v, i) => [x(i + 1), y(v)])) }));
    svg.appendChild(svgEl("path", { class: "overall-line", d: linePath(overall.map((v, i) => [x(i + 1), y(v)])) }));

    for (const idx of [warningIndex, driftIndex]) {
      svg.appendChild(svgEl("line", { class: idx === warningIndex ? "warning-line" : "marker-line", x1: x(idx), x2: x(idx), y1: margin.top, y2: h - margin.bottom }));
    }
    recent.forEach((v, i) => {
      if (i % 3 === 0 || i + 1 === warningIndex || i + 1 === driftIndex) {
        svg.appendChild(svgEl("circle", { class: i + 1 === driftIndex ? "drift-point" : i + 1 === warningIndex ? "warning-point" : "recent-point", cx: x(i + 1), cy: y(v), r: i + 1 === warningIndex || i + 1 === driftIndex ? 6 : 3.5 }));
      }
    });
    overall.forEach((v, i) => {
      if (i % 6 === 0) svg.appendChild(svgEl("circle", { class: "overall-point", cx: x(i + 1), cy: y(v), r: 3.5 }));
    });

    svg.appendChild(svgEl("line", { class: "axis-line", x1: margin.left, x2: margin.left + plotW, y1: h - margin.bottom, y2: h - margin.bottom }));
    svg.appendChild(svgEl("line", { class: "axis-line", x1: margin.left, x2: margin.left, y1: margin.top, y2: h - margin.bottom }));
    for (const t of [1, 8, 15, 22, 30]) {
      text(svg, t.toString(), x(t), h - margin.bottom + 24, { class: "tick-text", "text-anchor": "middle" });
    }
    text(svg, "stream index", margin.left + plotW / 2, h - 12, { class: "axis-label", "text-anchor": "middle" });
    text(svg, "accuracy", 16, margin.top + 178, { class: "axis-label", "text-anchor": "middle", transform: `rotate(-90 16 ${margin.top + 178})` });
    text(svg, "recent window drops below overall", x(10), y(0.91), { class: "callout" });
    text(svg, "warning", x(warningIndex) - 44, y(0.62), { class: "warning-text" });
    text(svg, "drift", x(driftIndex) + 8, y(0.62), { class: "drift-text" });
  }

  function drawThreshold() {
    const svg = document.getElementById("thresholdChart");
    const w = 472, h = 185;
    const margin = { top: 18, right: 24, bottom: 38, left: 48 };
    const gaps = overall.map((v, i) => Math.max(0, v - recent[i]));
    const x = scale(1, gaps.length, margin.left, w - margin.right);
    const y = scale(0, 0.22, h - margin.bottom, margin.top);
    const plotW = w - margin.left - margin.right;
    svg.setAttribute("viewBox", `0 0 ${w} ${h}`);
    for (const t of [0.00, 0.10, 0.15, 0.20]) {
      svg.appendChild(svgEl("line", { class: "grid-line", x1: margin.left, x2: margin.left + plotW, y1: y(t), y2: y(t) }));
      text(svg, t.toFixed(2), margin.left - 10, y(t) + 4, { class: "tick-text", "text-anchor": "end" });
    }
    svg.appendChild(svgEl("path", { class: "gap-line", d: linePath(gaps.map((v, i) => [x(i + 1), y(v)])) }));
    svg.appendChild(svgEl("line", { class: "warning-line", x1: margin.left, x2: margin.left + plotW, y1: y(warnThreshold), y2: y(warnThreshold) }));
    svg.appendChild(svgEl("line", { class: "drift-line", x1: margin.left, x2: margin.left + plotW, y1: y(driftThreshold), y2: y(driftThreshold) }));
    svg.appendChild(svgEl("circle", { class: "warning-point", cx: x(warningIndex), cy: y(gaps[warningIndex - 1]), r: 5 }));
    svg.appendChild(svgEl("circle", { class: "drift-point", cx: x(driftIndex), cy: y(gaps[driftIndex - 1]), r: 6 }));
    svg.appendChild(svgEl("line", { class: "axis-line", x1: margin.left, x2: margin.left + plotW, y1: h - margin.bottom, y2: h - margin.bottom }));
    text(svg, "overall - recent accuracy gap", margin.left + 170, h - 6, { class: "axis-label", "text-anchor": "middle" });
    text(svg, "warning", w - margin.right - 64, y(warnThreshold) - 6, { class: "warning-text" });
    text(svg, "drift", w - margin.right - 44, y(driftThreshold) - 6, { class: "drift-text" });
  }

  function drawState() {
    const svg = document.getElementById("stateChart");
    const w = 472, h = 185;
    const margin = { top: 34, right: 24, bottom: 38, left: 48 };
    const x = scale(1, 30, margin.left, w - margin.right);
    const y = 74;
    svg.setAttribute("viewBox", `0 0 ${w} ${h}`);
    const spans = [
      ["normal-fill", 1, warningIndex, "normal", 7],
      ["warning-fill", warningIndex, driftIndex, "warning", 17],
      ["drift-fill", driftIndex, 30, "drift", 25]
    ];
    spans.forEach(([cls, start, end, label, mid]) => {
      svg.appendChild(svgEl("rect", { class: cls, x: x(start), y, width: x(end) - x(start), height: 30, rx: 5 }));
      text(svg, label, x(mid), y + 20, { class: "bar-label", "text-anchor": "middle" });
    });
    svg.appendChild(svgEl("line", { class: "warning-line", x1: x(warningIndex), x2: x(warningIndex), y1: margin.top, y2: h - margin.bottom }));
    svg.appendChild(svgEl("line", { class: "marker-line", x1: x(driftIndex), x2: x(driftIndex), y1: margin.top, y2: h - margin.bottom }));
    svg.appendChild(svgEl("circle", { class: "warning-point", cx: x(warningIndex), cy: y + 15, r: 6 }));
    svg.appendChild(svgEl("circle", { class: "drift-point", cx: x(driftIndex), cy: y + 15, r: 6 }));
    svg.appendChild(svgEl("line", { class: "axis-line", x1: margin.left, x2: w - margin.right, y1: h - margin.bottom, y2: h - margin.bottom }));
    text(svg, "STEPD supervised state timeline", margin.left + 180, h - 6, { class: "axis-label", "text-anchor": "middle" });
  }

  drawSummary();
  drawAccuracy();
  drawThreshold();
  drawState();
})();
