(function () {
  const distance = [0.08,0.09,0.10,0.11,0.10,0.12,0.13,0.14,0.16,0.17,0.18,0.19,0.21,0.22,0.24,0.25,0.27,0.29,0.31,0.33,0.35,0.37,0.40,0.42,0.45,0.47,0.49,0.51,0.53,0.54,0.56,0.58];
  const threshold = 0.36;
  const alarmIndex = 22;
  const topics = {
    baseline: [0.48, 0.32, 0.20],
    current: [0.22, 0.30, 0.48]
  };

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
      ["cosine dist", "0.58"],
      ["topic shift", "+28pt"],
      ["domain AUC", "0.82"]
    ];
    document.getElementById("summary").innerHTML = rows.map(([label, value]) => `<div class="metric"><div class="label">${label}</div><div class="value">${value}</div></div>`).join("");
  }

  function drawProjection() {
    const svg = document.getElementById("projectionChart");
    const w = 630, h = 440;
    const margin = { top: 24, right: 28, bottom: 62, left: 58 };
    const x = scale(-2.4, 3.0, margin.left, w - margin.right);
    const y = scale(-2.0, 2.0, h - margin.bottom, margin.top);
    const baseCentroid = [-0.85, -0.12];
    const currentCentroid = [1.15, 0.40];
    svg.setAttribute("viewBox", `0 0 ${w} ${h}`);
    for (const t of [-2, -1, 0, 1, 2]) {
      svg.appendChild(svgEl("line", { class: "grid-line", x1: x(t), x2: x(t), y1: margin.top, y2: h - margin.bottom }));
      svg.appendChild(svgEl("line", { class: "grid-line", x1: margin.left, x2: w - margin.right, y1: y(t * 0.8), y2: y(t * 0.8) }));
    }
    for (let i = 0; i < 48; i += 1) {
      const bx = -1.45 + (i % 8) * 0.17 + Math.sin(i * 1.3) * 0.10;
      const by = -0.58 + Math.floor(i / 8) * 0.17 + Math.cos(i * 1.1) * 0.10;
      const cx = 0.66 + (i % 8) * 0.21 + Math.sin(i * 1.6) * 0.12;
      const cy = 0.03 + Math.floor(i / 8) * 0.18 + Math.cos(i * 1.2) * 0.11;
      svg.appendChild(svgEl("circle", { class: "base-dot", cx: x(bx), cy: y(by), r: 4 }));
      svg.appendChild(svgEl("circle", { class: "current-dot", cx: x(cx), cy: y(cy), r: 4 }));
    }
    svg.appendChild(svgEl("line", { class: "centroid-line", x1: x(baseCentroid[0]), y1: y(baseCentroid[1]), x2: x(currentCentroid[0]), y2: y(currentCentroid[1]) }));
    svg.appendChild(svgEl("circle", { class: "alarm-point", cx: x(currentCentroid[0]), cy: y(currentCentroid[1]), r: 7 }));
    svg.appendChild(svgEl("line", { class: "axis-line", x1: margin.left, x2: w - margin.right, y1: h - margin.bottom, y2: h - margin.bottom }));
    svg.appendChild(svgEl("line", { class: "axis-line", x1: margin.left, x2: margin.left, y1: margin.top, y2: h - margin.bottom }));
    text(svg, "UMAP-1", margin.left + 250, h - 12, { class: "axis-label", "text-anchor": "middle" });
    text(svg, "UMAP-2", 18, margin.top + 178, { class: "axis-label", "text-anchor": "middle", transform: `rotate(-90 18 ${margin.top + 178})` });
    text(svg, "query embedding clusters separate", x(0.20), y(1.58), { class: "warning-text" });
  }

  function drawDistance() {
    const svg = document.getElementById("distanceChart");
    const w = 472, h = 185;
    const margin = { top: 12, right: 22, bottom: 34, left: 48 };
    const x = scale(1, distance.length, margin.left, w - margin.right);
    const y = scale(0, 0.65, h - margin.bottom, margin.top);
    const plotW = w - margin.left - margin.right;
    svg.setAttribute("viewBox", `0 0 ${w} ${h}`);
    for (const t of [0, 0.2, 0.4, 0.6]) {
      svg.appendChild(svgEl("line", { class: "grid-line", x1: margin.left, x2: margin.left + plotW, y1: y(t), y2: y(t) }));
      text(svg, t.toFixed(1), margin.left - 10, y(t) + 4, { class: "tick-text", "text-anchor": "end" });
    }
    svg.appendChild(svgEl("line", { class: "threshold-line", x1: margin.left, x2: margin.left + plotW, y1: y(threshold), y2: y(threshold) }));
    svg.appendChild(svgEl("path", { class: "distance-line", d: linePath(distance.map((v, i) => [x(i + 1), y(v)])) }));
    distance.forEach((v, i) => {
      if (i % 4 === 0 || i + 1 >= alarmIndex) {
        svg.appendChild(svgEl("circle", { class: i + 1 >= alarmIndex ? "alarm-point" : "distance-point", cx: x(i + 1), cy: y(v), r: i + 1 >= alarmIndex ? 4.8 : 3.4 }));
      }
    });
    svg.appendChild(svgEl("line", { class: "axis-line", x1: margin.left, x2: margin.left + plotW, y1: h - margin.bottom, y2: h - margin.bottom }));
    text(svg, "centroid cosine distance", margin.left + 165, h - 8, { class: "axis-label", "text-anchor": "middle" });
    text(svg, "threshold exceeded", x(19), y(0.56), { class: "warning-text" });
  }

  function drawTopicRoc() {
    const svg = document.getElementById("topicRocChart");
    const w = 472, h = 185;
    svg.setAttribute("viewBox", `0 0 ${w} ${h}`);
    const barX = 78, barW = 150, rowH = 26;
    const colors = ["bar-a", "bar-b", "bar-c"];
    [["baseline", topics.baseline, 42], ["current", topics.current, 82]].forEach(([label, values, y]) => {
      text(svg, label, barX - 10, y + 18, { class: "bar-label", "text-anchor": "end" });
      let x0 = barX;
      values.forEach((v, i) => {
        const width = barW * v;
        svg.appendChild(svgEl("rect", { class: colors[i], x: x0, y, width, height: rowH, rx: i === 0 ? 4 : 0 }));
        x0 += width;
      });
    });
    text(svg, "topic mix", barX + 88, 132, { class: "axis-label", "text-anchor": "middle" });

    const rocX = 294, rocY = 24, rocW = 136, rocH = 118;
    svg.appendChild(svgEl("line", { class: "grid-line", x1: rocX, x2: rocX + rocW, y1: rocY + rocH, y2: rocY }));
    svg.appendChild(svgEl("line", { class: "axis-line", x1: rocX, x2: rocX + rocW, y1: rocY + rocH, y2: rocY + rocH }));
    svg.appendChild(svgEl("line", { class: "axis-line", x1: rocX, x2: rocX, y1: rocY, y2: rocY + rocH }));
    const rocPts = [[0,0],[0.08,0.35],[0.18,0.58],[0.34,0.75],[0.55,0.88],[1,1]].map(([a,b]) => [rocX + a * rocW, rocY + rocH - b * rocH]);
    svg.appendChild(svgEl("path", { class: "roc-line", d: linePath(rocPts) }));
    text(svg, "ROC AUC 0.82", rocX + 76, rocY + 14, { class: "warning-text", "text-anchor": "middle" });
    text(svg, "domain classifier", rocX + 78, 166, { class: "axis-label", "text-anchor": "middle" });
  }

  drawSummary();
  drawProjection();
  drawDistance();
  drawTopicRoc();
})();
