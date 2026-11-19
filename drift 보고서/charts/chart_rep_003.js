(function () {
  const distance = [0.08,0.09,0.10,0.09,0.11,0.12,0.13,0.16,0.18,0.21,0.25,0.29,0.33,0.37,0.42,0.46,0.50,0.54,0.57,0.60,0.62,0.64,0.66,0.67];
  const threshold = 0.40;
  const alarmIndex = 15;
  const heatmap = [
    [0.18,0.22,0.26,0.31,0.35,0.38],
    [0.20,0.24,0.33,0.48,0.62,0.70],
    [0.14,0.18,0.27,0.43,0.58,0.66],
    [0.10,0.16,0.20,0.29,0.36,0.44],
    [0.12,0.15,0.18,0.24,0.28,0.31]
  ];
  const groups = ["core", "hub", "bridge", "leaf", "new"];

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
      ["distance", "0.67"],
      ["node max", "0.70"],
      ["alarm", `t=${alarmIndex}`]
    ];
    document.getElementById("summary").innerHTML = rows.map(([label, value]) => `<div class="metric"><div class="label">${label}</div><div class="value">${value}</div></div>`).join("");
  }

  function drawProjection() {
    const svg = document.getElementById("projectionChart");
    const w = 630, h = 440;
    const margin = { top: 24, right: 28, bottom: 62, left: 58 };
    const x = scale(-2.4, 3.2, margin.left, w - margin.right);
    const y = scale(-1.8, 1.9, h - margin.bottom, margin.top);
    const plotW = w - margin.left - margin.right;
    svg.setAttribute("viewBox", `0 0 ${w} ${h}`);
    for (const t of [-1, 0, 1]) {
      svg.appendChild(svgEl("line", { class: "grid-line", x1: margin.left, x2: margin.left + plotW, y1: y(t), y2: y(t) }));
      text(svg, t.toString(), margin.left - 12, y(t) + 4, { class: "tick-text", "text-anchor": "end" });
    }
    svg.appendChild(svgEl("line", { class: "grid-line", x1: x(0), x2: x(0), y1: margin.top, y2: h - margin.bottom }));
    for (let i = 0; i < 42; i += 1) {
      const bx = -1.45 + (i % 7) * 0.18 + Math.sin(i * 1.1) * 0.08;
      const by = -0.48 + Math.floor(i / 7) * 0.18 + Math.cos(i) * 0.08;
      svg.appendChild(svgEl("circle", { class: "base-dot", cx: x(bx), cy: y(by), r: 4 }));
    }
    for (let i = 0; i < 42; i += 1) {
      const cx = 0.72 + (i % 7) * 0.22 + Math.sin(i * 1.3) * 0.08;
      const cy = 0.16 + Math.floor(i / 7) * 0.18 + Math.cos(i * 1.4) * 0.08;
      const cls = i % 7 === 2 || i % 7 === 3 ? "bridge-dot" : "current-dot";
      svg.appendChild(svgEl("circle", { class: cls, cx: x(cx), cy: y(cy), r: cls === "bridge-dot" ? 5 : 4 }));
    }
    svg.appendChild(svgEl("line", { class: "axis-line", x1: margin.left, x2: margin.left + plotW, y1: h - margin.bottom, y2: h - margin.bottom }));
    svg.appendChild(svgEl("line", { class: "axis-line", x1: margin.left, x2: margin.left, y1: margin.top, y2: h - margin.bottom }));
    text(svg, "embedding projection-1", margin.left + plotW / 2, h - 12, { class: "axis-label", "text-anchor": "middle" });
    text(svg, "embedding projection-2", 16, margin.top + 178, { class: "axis-label", "text-anchor": "middle", transform: `rotate(-90 16 ${margin.top + 178})` });
    text(svg, "current graph embeddings separate from baseline", x(-0.08), y(1.58), { class: "callout" });
    text(svg, "bridge nodes high drift", x(1.42), y(1.18), { class: "warning-text" });
  }

  function drawHeatmap() {
    const svg = document.getElementById("heatmapChart");
    const w = 472, h = 185;
    const margin = { top: 20, right: 20, bottom: 34, left: 70 };
    const cellW = 56;
    const cellH = 22;
    svg.setAttribute("viewBox", `0 0 ${w} ${h}`);
    heatmap.forEach((row, r) => {
      text(svg, groups[r], margin.left - 12, margin.top + r * cellH + 16, { class: "bar-label", "text-anchor": "end" });
      row.forEach((v, c) => {
        const cls = v > 0.55 ? "cell-high" : v > 0.32 ? "cell-mid" : "cell-low";
        svg.appendChild(svgEl("rect", { class: cls, x: margin.left + c * cellW, y: margin.top + r * cellH, width: cellW - 4, height: cellH - 4, rx: 4 }));
        if (v > 0.55) text(svg, v.toFixed(2), margin.left + c * cellW + 26, margin.top + r * cellH + 13, { class: "bar-label", "text-anchor": "middle" });
      });
    });
    for (let c = 0; c < 6; c += 1) {
      text(svg, `t${c + 1}`, margin.left + c * cellW + 26, h - 18, { class: "tick-text", "text-anchor": "middle" });
    }
    text(svg, "node group drift score", margin.left + 164, h - 4, { class: "axis-label", "text-anchor": "middle" });
  }

  function drawDistance() {
    const svg = document.getElementById("distanceChart");
    const w = 472, h = 185;
    const margin = { top: 12, right: 22, bottom: 34, left: 48 };
    const x = scale(1, distance.length, margin.left, w - margin.right);
    const y = scale(0, 0.75, h - margin.bottom, margin.top);
    const plotW = w - margin.left - margin.right;
    svg.setAttribute("viewBox", `0 0 ${w} ${h}`);
    for (const t of [0.0, 0.3, 0.6]) {
      svg.appendChild(svgEl("line", { class: "grid-line", x1: margin.left, x2: margin.left + plotW, y1: y(t), y2: y(t) }));
      text(svg, t.toFixed(1), margin.left - 10, y(t) + 4, { class: "tick-text", "text-anchor": "end" });
    }
    svg.appendChild(svgEl("line", { class: "threshold-line", x1: margin.left, x2: margin.left + plotW, y1: y(threshold), y2: y(threshold) }));
    svg.appendChild(svgEl("path", { class: "distance-line", d: linePath(distance.map((v, i) => [x(i + 1), y(v)])) }));
    distance.forEach((v, i) => {
      if (i % 3 === 0 || i + 1 >= alarmIndex) svg.appendChild(svgEl("circle", { class: "distance-point", cx: x(i + 1), cy: y(v), r: i + 1 >= alarmIndex ? 4.8 : 3.4 }));
    });
    svg.appendChild(svgEl("line", { class: "axis-line", x1: margin.left, x2: margin.left + plotW, y1: h - margin.bottom, y2: h - margin.bottom }));
    text(svg, "graph-level distance", margin.left + 160, h - 8, { class: "axis-label", "text-anchor": "middle" });
    text(svg, "threshold crossed", x(13), y(0.62), { class: "warning-text" });
  }

  drawSummary();
  drawProjection();
  drawHeatmap();
  drawDistance();
})();
