(function () {
  const xValues = [20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80];
  const referenceDensity = [0.03, 0.08, 0.18, 0.36, 0.62, 0.84, 0.96, 0.86, 0.62, 0.36, 0.18, 0.08, 0.03];
  const currentDensity = [0.05, 0.12, 0.25, 0.42, 0.54, 0.50, 0.38, 0.46, 0.70, 0.90, 0.72, 0.38, 0.14];
  const frequencies = [0.5, 1.0, 1.5, 2.0, 2.5, 3.0];
  const realDiff = [0.05, 0.11, 0.18, 0.24, 0.21, 0.14];
  const imagDiff = [0.03, 0.08, 0.15, 0.19, 0.16, 0.10];
  const contributions = frequencies.map((f, i) => ({
    label: `t=${f.toFixed(1)}`,
    value: realDiff[i] * realDiff[i] + imagDiff[i] * imagDiff[i],
    real: realDiff[i],
    imag: imagDiff[i]
  }));
  const statistic = 12.8;
  const pValue = 0.006;
  const top = contributions.reduce((best, row, i) => row.value > contributions[best].value ? i : best, 0);

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
    return linePath(points) + `L${points[points.length - 1][0].toFixed(2)},${baseY.toFixed(2)}L${points[0][0].toFixed(2)},${baseY.toFixed(2)}Z`;
  }

  function drawSummary() {
    const rows = [
      ["ES statistic", statistic.toFixed(1)],
      ["p-value", pValue.toFixed(3)],
      ["최대 ECF 차이", contributions[top].label]
    ];
    document.getElementById("summary").innerHTML = rows.map(([label, value]) => `<div class="metric"><div class="label">${label}</div><div class="value">${value}</div></div>`).join("");
  }

  function drawDistribution() {
    const svg = document.getElementById("distributionChart");
    const w = 630, h = 440;
    const margin = { top: 24, right: 28, bottom: 62, left: 58 };
    const x = scale(18, 82, margin.left, w - margin.right);
    const y = scale(0, 1.05, h - margin.bottom, margin.top);
    const plotW = w - margin.left - margin.right;
    svg.setAttribute("viewBox", `0 0 ${w} ${h}`);

    for (const t of [0, 0.25, 0.50, 0.75, 1.0]) {
      svg.appendChild(svgEl("line", { class: "grid-line", x1: margin.left, x2: margin.left + plotW, y1: y(t), y2: y(t) }));
      text(svg, t.toFixed(2), margin.left - 12, y(t) + 4, { class: "tick-text", "text-anchor": "end" });
    }
    for (const t of [20, 40, 60, 80]) {
      text(svg, t.toString(), x(t), h - margin.bottom + 24, { class: "tick-text", "text-anchor": "middle" });
    }
    svg.appendChild(svgEl("line", { class: "axis-line", x1: margin.left, x2: margin.left + plotW, y1: h - margin.bottom, y2: h - margin.bottom }));
    svg.appendChild(svgEl("line", { class: "axis-line", x1: margin.left, x2: margin.left, y1: margin.top, y2: h - margin.bottom }));

    const refPts = xValues.map((v, i) => [x(v), y(referenceDensity[i])]);
    const curPts = xValues.map((v, i) => [x(v), y(currentDensity[i])]);
    const diffPts = xValues.map((v, i) => [x(v), y(Math.abs(currentDensity[i] - referenceDensity[i]))]);
    svg.appendChild(svgEl("path", { class: "diff-band", d: areaPath(diffPts, y(0)) }));
    svg.appendChild(svgEl("path", { class: "ref-area", d: areaPath(refPts, y(0)) }));
    svg.appendChild(svgEl("path", { class: "cur-area", d: areaPath(curPts, y(0)) }));

    text(svg, "feature value", margin.left + plotW / 2, h - 12, { class: "axis-label", "text-anchor": "middle" });
    text(svg, "density", 16, margin.top + 175, { class: "axis-label", "text-anchor": "middle", transform: `rotate(-90 16 ${margin.top + 175})` });
    text(svg, "현재 분포는 65 부근 봉우리와 오른쪽 shoulder가 커짐", margin.left + plotW / 2, margin.top + 18, { class: "callout", "text-anchor": "middle" });
  }

  function drawEcf() {
    const svg = document.getElementById("ecfChart");
    const w = 472, h = 185;
    const margin = { top: 12, right: 22, bottom: 34, left: 48 };
    const x = scale(0.5, 3.0, margin.left, w - margin.right);
    const y = scale(-0.03, 0.27, h - margin.bottom, margin.top);
    const plotW = w - margin.left - margin.right;
    svg.setAttribute("viewBox", `0 0 ${w} ${h}`);

    for (const t of [0, 0.10, 0.20]) {
      svg.appendChild(svgEl("line", { class: t === 0 ? "zero-line" : "grid-line", x1: margin.left, x2: margin.left + plotW, y1: y(t), y2: y(t) }));
      text(svg, t.toFixed(2), margin.left - 10, y(t) + 4, { class: "tick-text", "text-anchor": "end" });
    }
    const realPts = frequencies.map((f, i) => [x(f), y(realDiff[i])]);
    const imagPts = frequencies.map((f, i) => [x(f), y(imagDiff[i])]);
    svg.appendChild(svgEl("path", { class: "real-line", d: linePath(realPts) }));
    svg.appendChild(svgEl("path", { class: "imag-line", d: linePath(imagPts) }));
    realPts.forEach(([cx, cy]) => svg.appendChild(svgEl("circle", { class: "real-point", cx, cy, r: 4 })));
    imagPts.forEach(([cx, cy]) => svg.appendChild(svgEl("circle", { class: "imag-point", cx, cy, r: 4 })));
    svg.appendChild(svgEl("line", { class: "axis-line", x1: margin.left, x2: margin.left + plotW, y1: h - margin.bottom, y2: h - margin.bottom }));
    text(svg, "frequency t", margin.left + plotW / 2, h - 8, { class: "axis-label", "text-anchor": "middle" });
    text(svg, "Real diff", w - margin.right - 88, margin.top + 18, { class: "callout" });
    text(svg, "Imag diff", w - margin.right - 88, margin.top + 38, { class: "warning" });
  }

  function drawStat() {
    const svg = document.getElementById("statChart");
    const w = 472, h = 185;
    const margin = { top: 8, right: 22, bottom: 30, left: 70 };
    const rows = contributions.slice().sort((a, b) => b.value - a.value);
    const maxValue = Math.max(...rows.map(r => r.value));
    const x = scale(0, maxValue * 1.25, margin.left, w - margin.right);
    svg.setAttribute("viewBox", `0 0 ${w} ${h}`);

    rows.forEach((row, i) => {
      const y = margin.top + i * 23 + 5;
      text(svg, row.label, margin.left - 8, y + 11, { class: "tick-text", "text-anchor": "end" });
      svg.appendChild(svgEl("rect", { class: i === 0 ? "top-stat-bar" : "stat-bar", x: margin.left, y, width: x(row.value) - margin.left, height: 16, rx: 4 }));
      text(svg, row.value.toFixed(3), x(row.value) + 7, y + 12, { class: "bar-label" });
    });
    svg.appendChild(svgEl("line", { class: "axis-line", x1: margin.left, x2: w - margin.right, y1: h - margin.bottom, y2: h - margin.bottom }));
    text(svg, `stat=${statistic.toFixed(1)}, p=${pValue.toFixed(3)}`, margin.left + 150, h - 6, { class: "axis-label", "text-anchor": "middle" });
  }

  drawSummary();
  drawDistribution();
  drawEcf();
  drawStat();
})();
