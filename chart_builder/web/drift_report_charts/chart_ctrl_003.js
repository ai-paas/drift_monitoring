(function () {
  const stat = [3.1,3.4,3.0,3.8,4.2,3.7,4.5,5.1,4.8,5.4,5.9,6.2,6.8,7.1,7.5,8.0,8.6,9.2,9.8,10.3,11.1,11.8,12.6,13.4,14.1,15.0,15.8,16.9,17.5,18.2,18.6,19.1];
  const ucl = 12.0;
  const alarmIndex = 23;
  const contributions = [
    ["risk_score", 38],
    ["amount", 24],
    ["frequency", 18],
    ["latency", 12],
    ["region_mix", 8]
  ];
  const small = [
    { name: "risk_score", values: [0.42,0.43,0.41,0.44,0.45,0.46,0.47,0.48,0.50,0.51,0.53,0.54,0.56,0.58,0.60,0.62], cls: "metric-line" },
    { name: "amount", values: [0.51,0.50,0.52,0.51,0.53,0.54,0.55,0.57,0.58,0.60,0.61,0.63,0.64,0.66,0.68,0.69], cls: "metric-line alt" },
    { name: "frequency", values: [0.38,0.39,0.38,0.40,0.39,0.41,0.42,0.43,0.45,0.46,0.47,0.49,0.50,0.51,0.52,0.54], cls: "metric-line third" }
  ];

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
      ["MEWMA final", "19.1"],
      ["UCL", ucl.toFixed(1)],
      ["Top metric", "risk_score"]
    ];
    document.getElementById("summary").innerHTML = rows.map(([label, value]) => `<div class="metric"><div class="label">${label}</div><div class="value">${value}</div></div>`).join("");
  }

  function drawStatChart() {
    const svg = document.getElementById("statChart");
    const w = 630, h = 440;
    const margin = { top: 24, right: 28, bottom: 62, left: 58 };
    const x = scale(1, stat.length, margin.left, w - margin.right);
    const y = scale(0, 22, h - margin.bottom, margin.top);
    const plotW = w - margin.left - margin.right;
    svg.setAttribute("viewBox", `0 0 ${w} ${h}`);
    for (const t of [0, 5, 10, 15, 20]) {
      svg.appendChild(svgEl("line", { class: "grid-line", x1: margin.left, x2: margin.left + plotW, y1: y(t), y2: y(t) }));
      text(svg, t.toString(), margin.left - 12, y(t) + 4, { class: "tick-text", "text-anchor": "end" });
    }
    svg.appendChild(svgEl("line", { class: "limit-line", x1: margin.left, x2: margin.left + plotW, y1: y(ucl), y2: y(ucl) }));
    svg.appendChild(svgEl("path", { class: "stat-line", d: linePath(stat.map((v, i) => [x(i + 1), y(v)])) }));
    stat.forEach((v, i) => {
      if (i % 3 === 0 || v >= ucl) {
        svg.appendChild(svgEl("circle", { class: v >= ucl ? "alarm-point" : "stat-point", cx: x(i + 1), cy: y(v), r: v >= ucl ? 4.8 : 3.6 }));
      }
    });
    svg.appendChild(svgEl("line", { class: "alarm-line", x1: x(alarmIndex), x2: x(alarmIndex), y1: margin.top, y2: h - margin.bottom }));
    svg.appendChild(svgEl("circle", { class: "alarm-point", cx: x(alarmIndex), cy: y(stat[alarmIndex - 1]), r: 7 }));
    svg.appendChild(svgEl("line", { class: "axis-line", x1: margin.left, x2: margin.left + plotW, y1: h - margin.bottom, y2: h - margin.bottom }));
    svg.appendChild(svgEl("line", { class: "axis-line", x1: margin.left, x2: margin.left, y1: margin.top, y2: h - margin.bottom }));
    for (const t of [1, 8, 16, 24, 32]) {
      text(svg, t.toString(), x(t), h - margin.bottom + 24, { class: "tick-text", "text-anchor": "middle" });
    }
    text(svg, "time index", margin.left + plotW / 2, h - 12, { class: "axis-label", "text-anchor": "middle" });
    text(svg, "MEWMA statistic", 16, margin.top + 178, { class: "axis-label", "text-anchor": "middle", transform: `rotate(-90 16 ${margin.top + 178})` });
    text(svg, "UCL 12.0", w - margin.right - 68, y(ucl) - 8, { class: "warning-text" });
    text(svg, "alarm: multivariate statistic crosses UCL", x(12), y(20.5), { class: "callout" });
  }

  function drawContribution() {
    const svg = document.getElementById("contributionChart");
    const w = 472, h = 185;
    const margin = { top: 14, right: 32, bottom: 26, left: 96 };
    const x = scale(0, 42, margin.left, w - margin.right);
    svg.setAttribute("viewBox", `0 0 ${w} ${h}`);
    contributions.forEach(([name, value], i) => {
      const y = margin.top + i * 27;
      svg.appendChild(svgEl("rect", { class: "row-bg", x: margin.left, y: y + 3, width: w - margin.left - margin.right, height: 16, rx: 4 }));
      svg.appendChild(svgEl("rect", { class: i === 0 ? "bar-fill hot" : "bar-fill", x: margin.left, y: y + 3, width: x(value) - margin.left, height: 16, rx: 4 }));
      text(svg, name, margin.left - 10, y + 16, { class: "bar-label", "text-anchor": "end" });
      text(svg, `${value}%`, x(value) + 8, y + 16, { class: "tick-text" });
    });
    svg.appendChild(svgEl("line", { class: "axis-line", x1: margin.left, x2: w - margin.right, y1: h - margin.bottom, y2: h - margin.bottom }));
    text(svg, "alarm contribution share", margin.left + 132, h - 6, { class: "axis-label", "text-anchor": "middle" });
  }

  function drawSmallMultiples() {
    const svg = document.getElementById("smallMultiples");
    const w = 472, h = 185;
    const margin = { top: 8, right: 22, bottom: 22, left: 82 };
    const rowH = 48;
    svg.setAttribute("viewBox", `0 0 ${w} ${h}`);
    small.forEach((series, row) => {
      const top = margin.top + row * rowH;
      const base = top + 36;
      const x = scale(1, series.values.length, margin.left, w - margin.right);
      const y = scale(0.35, 0.72, base, top + 5);
      svg.appendChild(svgEl("line", { class: "grid-line", x1: margin.left, x2: w - margin.right, y1: base, y2: base }));
      svg.appendChild(svgEl("path", { class: series.cls, d: linePath(series.values.map((v, i) => [x(i + 1), y(v)])) }));
      text(svg, series.name, margin.left - 10, top + 24, { class: "mini-title", "text-anchor": "end" });
    });
    svg.appendChild(svgEl("line", { class: "alarm-line", x1: 356, x2: 356, y1: margin.top + 2, y2: margin.top + rowH * 3 - 6 }));
    text(svg, "동시 상승", 366, 31, { class: "warning-text" });
    text(svg, "time aligned metrics", margin.left + 150, h - 5, { class: "axis-label", "text-anchor": "middle" });
  }

  drawSummary();
  drawStatChart();
  drawContribution();
  drawSmallMultiples();
})();
