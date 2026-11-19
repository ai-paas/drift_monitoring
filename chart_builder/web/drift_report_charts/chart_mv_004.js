(function () {
  const referencePoints = [
    [-1.9, -0.9], [-1.6, -0.3], [-1.4, -1.2], [-1.1, -0.7], [-0.9, 0.0],
    [-0.6, -0.8], [-0.4, -0.2], [-0.1, -1.0], [0.1, -0.5], [0.3, 0.2],
    [0.5, -0.6], [0.7, 0.0], [0.9, -0.8], [1.1, -0.2], [1.3, 0.4],
    [-1.2, 0.5], [-0.7, 0.8], [0.0, 0.7], [0.7, 1.0], [1.2, 0.8]
  ];
  const currentPoints = [
    [0.2, 0.4], [0.5, 1.0], [0.8, 1.5], [1.0, 0.8], [1.3, 1.8],
    [1.5, 1.1], [1.8, 2.0], [2.0, 1.4], [2.3, 2.1], [2.5, 1.3],
    [2.7, 2.4], [3.0, 1.7], [3.2, 2.5], [2.1, 2.8], [1.4, 2.5]
  ];
  const t2Trend = [4.2, 5.1, 6.0, 5.8, 7.4, 9.2, 12.5, 16.8, 21.4, 25.7];
  const ucl = 14.0;
  const contributions = [
    { label: "소득", value: 36 },
    { label: "거래금액", value: 28 },
    { label: "이용빈도", value: 18 },
    { label: "연체일수", value: 11 },
    { label: "나이", value: 7 }
  ];
  const t2Value = 25.7;
  const pValue = 0.004;
  const meanShift = 1.62;

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
      ["Hotelling T2", t2Value.toFixed(1)],
      ["p-value", pValue.toFixed(3)],
      ["평균 shift", meanShift.toFixed(2)]
    ];
    document.getElementById("summary").innerHTML = rows.map(([label, value]) => `<div class="metric"><div class="label">${label}</div><div class="value">${value}</div></div>`).join("");
  }

  function drawPca() {
    const svg = document.getElementById("pcaChart");
    const w = 630, h = 440;
    const margin = { top: 24, right: 28, bottom: 62, left: 58 };
    const x = scale(-2.5, 3.5, margin.left, w - margin.right);
    const y = scale(-1.6, 3.1, h - margin.bottom, margin.top);
    const plotW = w - margin.left - margin.right;
    const plotH = h - margin.top - margin.bottom;
    const refMean = [-0.2, -0.1];
    const curMean = [1.9, 1.8];
    svg.setAttribute("viewBox", `0 0 ${w} ${h}`);

    for (const t of [-2, -1, 0, 1, 2, 3]) {
      svg.appendChild(svgEl("line", { class: "grid-line", x1: x(t), x2: x(t), y1: margin.top, y2: margin.top + plotH }));
      text(svg, t.toString(), x(t), h - margin.bottom + 24, { class: "tick-text", "text-anchor": "middle" });
    }
    for (const t of [-1, 0, 1, 2, 3]) {
      svg.appendChild(svgEl("line", { class: "grid-line", x1: margin.left, x2: margin.left + plotW, y1: y(t), y2: y(t) }));
      text(svg, t.toString(), margin.left - 12, y(t) + 4, { class: "tick-text", "text-anchor": "end" });
    }
    svg.appendChild(svgEl("ellipse", { class: "ref-ellipse", cx: x(refMean[0]), cy: y(refMean[1]), rx: 198, ry: 116, transform: `rotate(18 ${x(refMean[0])} ${y(refMean[1])})` }));
    referencePoints.forEach(([px, py]) => svg.appendChild(svgEl("circle", { class: "ref-point", cx: x(px), cy: y(py), r: 5 })));
    currentPoints.forEach(([px, py]) => svg.appendChild(svgEl("circle", { class: "cur-point", cx: x(px), cy: y(py), r: 5 })));
    svg.appendChild(svgEl("line", { class: "mean-line", x1: x(refMean[0]), y1: y(refMean[1]), x2: x(curMean[0]), y2: y(curMean[1]) }));
    svg.appendChild(svgEl("circle", { class: "mean-point-ref", cx: x(refMean[0]), cy: y(refMean[1]), r: 7 }));
    svg.appendChild(svgEl("circle", { class: "mean-point-cur", cx: x(curMean[0]), cy: y(curMean[1]), r: 7 }));
    svg.appendChild(svgEl("line", { class: "axis-line", x1: margin.left, x2: margin.left + plotW, y1: h - margin.bottom, y2: h - margin.bottom }));
    svg.appendChild(svgEl("line", { class: "axis-line", x1: margin.left, x2: margin.left, y1: margin.top, y2: h - margin.bottom }));
    text(svg, "PC1", margin.left + plotW / 2, h - 12, { class: "axis-label", "text-anchor": "middle" });
    text(svg, "PC2", 16, margin.top + 178, { class: "axis-label", "text-anchor": "middle", transform: `rotate(-90 16 ${margin.top + 178})` });
    text(svg, "현재 평균 중심이 기준 타원 밖으로 이동", x(1.1), y(2.85), { class: "warning" });
  }

  function drawControl() {
    const svg = document.getElementById("controlChart");
    const w = 472, h = 185;
    const margin = { top: 12, right: 22, bottom: 34, left: 48 };
    const x = scale(1, t2Trend.length, margin.left, w - margin.right);
    const y = scale(0, 30, h - margin.bottom, margin.top);
    const plotW = w - margin.left - margin.right;
    svg.setAttribute("viewBox", `0 0 ${w} ${h}`);
    for (const t of [0, 10, 20, 30]) {
      svg.appendChild(svgEl("line", { class: "grid-line", x1: margin.left, x2: margin.left + plotW, y1: y(t), y2: y(t) }));
      text(svg, t.toString(), margin.left - 10, y(t) + 4, { class: "tick-text", "text-anchor": "end" });
    }
    svg.appendChild(svgEl("line", { class: "threshold-line", x1: margin.left, x2: margin.left + plotW, y1: y(ucl), y2: y(ucl) }));
    const pts = t2Trend.map((v, i) => [x(i + 1), y(v)]);
    svg.appendChild(svgEl("path", { class: "t2-line", d: linePath(pts) }));
    pts.forEach(([cx, cy], i) => svg.appendChild(svgEl("circle", { class: t2Trend[i] > ucl ? "alert-point" : "t2-point", cx, cy, r: i >= 7 ? 4.8 : 4 })));
    svg.appendChild(svgEl("line", { class: "axis-line", x1: margin.left, x2: margin.left + plotW, y1: h - margin.bottom, y2: h - margin.bottom }));
    text(svg, "window", margin.left + plotW / 2, h - 8, { class: "axis-label", "text-anchor": "middle" });
    text(svg, "UCL 14.0", w - margin.right - 68, y(ucl) - 6, { class: "warning" });
  }

  function drawContribution() {
    const svg = document.getElementById("contributionChart");
    const w = 472, h = 185;
    const margin = { top: 8, right: 32, bottom: 30, left: 86 };
    const maxValue = Math.max(...contributions.map(r => r.value));
    const x = scale(0, maxValue * 1.18, margin.left, w - margin.right);
    svg.setAttribute("viewBox", `0 0 ${w} ${h}`);
    contributions.forEach((row, i) => {
      const y = margin.top + i * 27 + 2;
      text(svg, row.label, margin.left - 8, y + 15, { class: "tick-text", "text-anchor": "end" });
      svg.appendChild(svgEl("rect", { class: i === 0 ? "top-contrib-bar" : "contrib-bar", x: margin.left, y, width: x(row.value) - margin.left, height: 18, rx: 4 }));
      text(svg, `${row.value}%`, x(row.value) + 7, y + 14, { class: "bar-label" });
    });
    svg.appendChild(svgEl("line", { class: "axis-line", x1: margin.left, x2: w - margin.right, y1: h - margin.bottom, y2: h - margin.bottom }));
    text(svg, "T2 contribution", margin.left + 150, h - 6, { class: "axis-label", "text-anchor": "middle" });
  }

  drawSummary();
  drawPca();
  drawControl();
  drawContribution();
})();
