(function () {
  const roc = [[0,0],[0.03,0.18],[0.07,0.34],[0.12,0.49],[0.20,0.64],[0.31,0.77],[0.46,0.87],[0.64,0.94],[0.82,0.98],[1,1]];
  const scoreBins = [0.05,0.12,0.19,0.26,0.33,0.40,0.47,0.54,0.61,0.68,0.75,0.82,0.89,0.96];
  const baseDensity = [26,34,38,31,22,13,7,3,1,0,0,0,0,0];
  const currentDensity = [0,0,1,2,5,9,15,23,31,36,33,24,13,5];
  const features = [["emb_17",0.31],["emb_04",0.24],["emb_22",0.19],["emb_09",0.14]];

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
      ["ROC-AUC", "0.89"],
      ["score gap", "0.41"],
      ["top feature", "emb_17"]
    ];
    document.getElementById("summary").innerHTML = rows.map(([label, value]) => `<div class="metric"><div class="label">${label}</div><div class="value">${value}</div></div>`).join("");
  }

  function drawRoc() {
    const svg = document.getElementById("rocChart");
    const w = 630, h = 440;
    const margin = { top: 24, right: 30, bottom: 62, left: 58 };
    const x = scale(0, 1, margin.left, w - margin.right);
    const y = scale(0, 1, h - margin.bottom, margin.top);
    const plotW = w - margin.left - margin.right;
    svg.setAttribute("viewBox", `0 0 ${w} ${h}`);
    for (const t of [0, 0.25, 0.5, 0.75, 1]) {
      svg.appendChild(svgEl("line", { class: "grid-line", x1: margin.left, x2: margin.left + plotW, y1: y(t), y2: y(t) }));
      text(svg, t.toFixed(2), margin.left - 12, y(t) + 4, { class: "tick-text", "text-anchor": "end" });
      text(svg, t.toFixed(2), x(t), h - margin.bottom + 24, { class: "tick-text", "text-anchor": "middle" });
    }
    const rocPoints = roc.map(([fpr, tpr]) => [x(fpr), y(tpr)]);
    svg.appendChild(svgEl("path", { class: "roc-fill", d: `${linePath(rocPoints)} L${x(1)},${y(0)} L${x(0)},${y(0)} Z` }));
    svg.appendChild(svgEl("line", { class: "random-line", x1: x(0), x2: x(1), y1: y(0), y2: y(1) }));
    svg.appendChild(svgEl("path", { class: "roc-line", d: linePath(rocPoints) }));
    rocPoints.forEach((p, i) => {
      if (i % 2 === 0 || i === rocPoints.length - 1) svg.appendChild(svgEl("circle", { class: "current-dot", cx: p[0], cy: p[1], r: 4 }));
    });
    svg.appendChild(svgEl("line", { class: "axis-line", x1: margin.left, x2: margin.left + plotW, y1: h - margin.bottom, y2: h - margin.bottom }));
    svg.appendChild(svgEl("line", { class: "axis-line", x1: margin.left, x2: margin.left, y1: margin.top, y2: h - margin.bottom }));
    text(svg, "false positive rate", margin.left + plotW / 2, h - 12, { class: "axis-label", "text-anchor": "middle" });
    text(svg, "true positive rate", 16, margin.top + 178, { class: "axis-label", "text-anchor": "middle", transform: `rotate(-90 16 ${margin.top + 178})` });
    text(svg, "domain classifier separates periods: AUC 0.89", x(0.22), y(0.92), { class: "callout" });
  }

  function drawScore() {
    const svg = document.getElementById("scoreChart");
    const w = 472, h = 185;
    const margin = { top: 14, right: 24, bottom: 34, left: 46 };
    const x = scale(0.05, 0.96, margin.left, w - margin.right);
    const y = scale(0, 42, h - margin.bottom, margin.top);
    svg.setAttribute("viewBox", `0 0 ${w} ${h}`);
    const basePts = baseDensity.map((v, i) => [x(scoreBins[i]), y(v)]);
    const curPts = currentDensity.map((v, i) => [x(scoreBins[i]), y(v)]);
    svg.appendChild(svgEl("path", { class: "base-area", d: areaPath(basePts, y(0)) }));
    svg.appendChild(svgEl("path", { class: "current-area", d: areaPath(curPts, y(0)) }));
    svg.appendChild(svgEl("line", { class: "random-line", x1: x(0.5), x2: x(0.5), y1: margin.top, y2: h - margin.bottom }));
    svg.appendChild(svgEl("line", { class: "axis-line", x1: margin.left, x2: w - margin.right, y1: h - margin.bottom, y2: h - margin.bottom }));
    text(svg, "domain probability", margin.left + 174, h - 8, { class: "axis-label", "text-anchor": "middle" });
    text(svg, "score distributions separated", x(0.36), y(38), { class: "callout" });
  }

  function drawImportance() {
    const svg = document.getElementById("importanceChart");
    const w = 472, h = 185;
    const margin = { top: 16, right: 20, bottom: 34, left: 72 };
    const x = scale(0, 0.34, margin.left, margin.left + 180);
    svg.setAttribute("viewBox", `0 0 ${w} ${h}`);
    features.forEach(([name, value], i) => {
      const y = 24 + i * 25;
      text(svg, name, margin.left - 12, y + 12, { class: "bar-label", "text-anchor": "end" });
      svg.appendChild(svgEl("rect", { class: "bar-feature", x: margin.left, y, width: x(value) - margin.left, height: 14, rx: 3 }));
      text(svg, value.toFixed(2), x(value) + 7, y + 12, { class: "tick-text" });
    });
    const px = scale(-1.7, 2.3, 292, w - margin.right);
    const py = scale(-1.2, 1.4, h - margin.bottom, margin.top + 4);
    for (let i = 0; i < 24; i += 1) {
      const bx = -1.0 + (i % 6) * 0.13 + Math.sin(i) * 0.05;
      const by = -0.28 + Math.floor(i / 6) * 0.15 + Math.cos(i) * 0.05;
      const cx = 0.55 + (i % 6) * 0.17 + Math.sin(i * 1.4) * 0.05;
      const cy = 0.10 + Math.floor(i / 6) * 0.16 + Math.cos(i * 1.2) * 0.05;
      svg.appendChild(svgEl("circle", { class: "base-dot", cx: px(bx), cy: py(by), r: 3.5 }));
      svg.appendChild(svgEl("circle", { class: "current-dot", cx: px(cx), cy: py(cy), r: 3.5 }));
    }
    svg.appendChild(svgEl("line", { class: "axis-line", x1: margin.left, x2: margin.left + 180, y1: h - margin.bottom, y2: h - margin.bottom }));
    svg.appendChild(svgEl("line", { class: "grid-line", x1: 292, x2: w - margin.right, y1: py(0), y2: py(0) }));
    text(svg, "importance", margin.left + 86, h - 8, { class: "axis-label", "text-anchor": "middle" });
    text(svg, "projection split", 364, h - 8, { class: "axis-label", "text-anchor": "middle" });
  }

  drawSummary();
  drawRoc();
  drawScore();
  drawImportance();
})();
