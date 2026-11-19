(function () {
  const bins = [0.05,0.12,0.19,0.26,0.33,0.40,0.47,0.54,0.61,0.68,0.75,0.82,0.89,0.96];
  const baseConfidence = [0,0,1,2,4,7,10,15,22,30,37,41,35,22];
  const currentConfidence = [3,7,12,20,29,36,38,31,24,16,9,5,2,1];
  const entropyTrend = [0.22,0.23,0.24,0.24,0.26,0.27,0.28,0.30,0.33,0.36,0.39,0.43,0.47,0.52,0.57,0.61,0.65,0.68,0.70,0.72,0.74,0.75,0.76,0.77];
  const threshold = 0.55;
  const alarmIndex = 15;

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
      ["entropy", "0.77"],
      ["ECE", "0.12"],
      ["alarm", `t=${alarmIndex}`]
    ];
    document.getElementById("summary").innerHTML = rows.map(([label, value]) => `<div class="metric"><div class="label">${label}</div><div class="value">${value}</div></div>`).join("");
  }

  function drawDistribution() {
    const svg = document.getElementById("distributionChart");
    const w = 630, h = 440;
    const margin = { top: 24, right: 28, bottom: 62, left: 58 };
    const x = scale(0.05, 0.96, margin.left, w - margin.right);
    const y = scale(0, 44, h - margin.bottom, margin.top);
    const plotW = w - margin.left - margin.right;
    svg.setAttribute("viewBox", `0 0 ${w} ${h}`);
    for (const t of [0, 10, 20, 30, 40]) {
      svg.appendChild(svgEl("line", { class: "grid-line", x1: margin.left, x2: margin.left + plotW, y1: y(t), y2: y(t) }));
      text(svg, t.toString(), margin.left - 12, y(t) + 4, { class: "tick-text", "text-anchor": "end" });
    }
    const basePts = baseConfidence.map((v, i) => [x(bins[i]), y(v)]);
    const currentPts = currentConfidence.map((v, i) => [x(bins[i]), y(v)]);
    svg.appendChild(svgEl("path", { class: "base-area", d: areaPath(basePts, y(0)) }));
    svg.appendChild(svgEl("path", { class: "current-area", d: areaPath(currentPts, y(0)) }));
    svg.appendChild(svgEl("line", { class: "threshold-line", x1: x(0.50), x2: x(0.50), y1: margin.top, y2: h - margin.bottom }));
    svg.appendChild(svgEl("line", { class: "axis-line", x1: margin.left, x2: margin.left + plotW, y1: h - margin.bottom, y2: h - margin.bottom }));
    svg.appendChild(svgEl("line", { class: "axis-line", x1: margin.left, x2: margin.left, y1: margin.top, y2: h - margin.bottom }));
    for (const t of [0.10, 0.30, 0.50, 0.70, 0.90]) {
      text(svg, t.toFixed(2), x(t), h - margin.bottom + 24, { class: "tick-text", "text-anchor": "middle" });
    }
    text(svg, "softmax confidence", margin.left + plotW / 2, h - 12, { class: "axis-label", "text-anchor": "middle" });
    text(svg, "density", 16, margin.top + 178, { class: "axis-label", "text-anchor": "middle", transform: `rotate(-90 16 ${margin.top + 178})` });
    text(svg, "current confidence shifts lower", x(0.32), y(40), { class: "warning-text" });
    text(svg, "low-confidence region", x(0.51), y(34), { class: "warning-text" });
  }

  function drawTrend() {
    const svg = document.getElementById("trendChart");
    const w = 472, h = 185;
    const margin = { top: 12, right: 22, bottom: 34, left: 48 };
    const x = scale(1, entropyTrend.length, margin.left, w - margin.right);
    const y = scale(0.15, 0.82, h - margin.bottom, margin.top);
    const plotW = w - margin.left - margin.right;
    svg.setAttribute("viewBox", `0 0 ${w} ${h}`);
    for (const t of [0.2, 0.5, 0.8]) {
      svg.appendChild(svgEl("line", { class: "grid-line", x1: margin.left, x2: margin.left + plotW, y1: y(t), y2: y(t) }));
      text(svg, t.toFixed(1), margin.left - 10, y(t) + 4, { class: "tick-text", "text-anchor": "end" });
    }
    svg.appendChild(svgEl("line", { class: "threshold-line", x1: margin.left, x2: margin.left + plotW, y1: y(threshold), y2: y(threshold) }));
    svg.appendChild(svgEl("path", { class: "entropy-line", d: linePath(entropyTrend.map((v, i) => [x(i + 1), y(v)])) }));
    entropyTrend.forEach((v, i) => {
      if (i % 3 === 0 || i + 1 >= alarmIndex) svg.appendChild(svgEl("circle", { class: "entropy-point", cx: x(i + 1), cy: y(v), r: i + 1 >= alarmIndex ? 4.7 : 3.3 }));
    });
    svg.appendChild(svgEl("line", { class: "axis-line", x1: margin.left, x2: margin.left + plotW, y1: h - margin.bottom, y2: h - margin.bottom }));
    text(svg, "time index", margin.left + 160, h - 8, { class: "axis-label", "text-anchor": "middle" });
    text(svg, "threshold crossed", x(13), y(0.75), { class: "warning-text" });
  }

  function drawCalibration() {
    const svg = document.getElementById("calibrationChart");
    const w = 472, h = 185;
    const margin = { top: 16, right: 20, bottom: 34, left: 46 };
    const x = scale(0, 1, margin.left, margin.left + 162);
    const y = scale(0, 1, h - margin.bottom, margin.top);
    const cal = [[0.1,0.06],[0.3,0.21],[0.5,0.38],[0.7,0.52],[0.9,0.66]];
    svg.setAttribute("viewBox", `0 0 ${w} ${h}`);
    svg.appendChild(svgEl("line", { class: "perfect-line", x1: x(0), x2: x(1), y1: y(0), y2: y(1) }));
    svg.appendChild(svgEl("path", { class: "calibration-line", d: linePath(cal.map(([cx, cy]) => [x(cx), y(cy)])) }));
    cal.forEach(([cx, cy]) => svg.appendChild(svgEl("circle", { class: "current-point", cx: x(cx), cy: y(cy), r: 4 })));
    svg.appendChild(svgEl("line", { class: "axis-line", x1: margin.left, x2: margin.left + 162, y1: h - margin.bottom, y2: h - margin.bottom }));
    svg.appendChild(svgEl("line", { class: "axis-line", x1: margin.left, x2: margin.left, y1: margin.top, y2: h - margin.bottom }));
    text(svg, "calibration", margin.left + 78, h - 8, { class: "axis-label", "text-anchor": "middle" });

    const classes = [["A",0.19],["B",0.31],["C",0.46],["D",0.28]];
    const bx = scale(0, 0.5, 290, w - margin.right);
    classes.forEach(([label, value], i) => {
      const yy = 30 + i * 27;
      text(svg, label, 276, yy + 12, { class: "bar-label", "text-anchor": "end" });
      svg.appendChild(svgEl("rect", { class: i === 2 ? "bar-class" : "bar-base", x: 290, y: yy, width: bx(value) - 290, height: 14, rx: 3 }));
      text(svg, value.toFixed(2), bx(value) + 7, yy + 12, { class: "tick-text" });
    });
    text(svg, "class uncertainty", 360, h - 8, { class: "axis-label", "text-anchor": "middle" });
  }

  drawSummary();
  drawDistribution();
  drawTrend();
  drawCalibration();
})();
