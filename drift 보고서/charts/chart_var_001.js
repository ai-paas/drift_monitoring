(function () {
  const reference = {
    label: "기준",
    variance: 42.3,
    sd: 6.5,
    center: 52.0,
    q1: 47.6,
    median: 52.1,
    q3: 56.5,
    low: 39.5,
    high: 64.0,
    absDev: 5.1,
    density: [
      [39, 0.10], [43, 0.36], [47, 0.72], [51, 0.98], [55, 0.88],
      [59, 0.52], [63, 0.20], [67, 0.06]
    ]
  };
  const current = {
    label: "현재",
    variance: 112.4,
    sd: 10.6,
    center: 52.6,
    q1: 44.0,
    median: 52.3,
    q3: 61.8,
    low: 31.0,
    high: 77.5,
    absDev: 8.7,
    density: [
      [31, 0.07], [37, 0.24], [43, 0.52], [49, 0.76], [55, 0.82],
      [61, 0.66], [67, 0.39], [73, 0.18], [78, 0.06]
    ]
  };
  const varianceRatio = current.variance / reference.variance;
  const pValue = 0.012;
  const ratioThreshold = 1.5;
  const absDevChange = current.absDev - reference.absDev;

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
  function violinPath(data, xCenter, yScale, width) {
    const right = data.map(([v, d]) => [xCenter + d * width, yScale(v)]);
    const left = data.slice().reverse().map(([v, d]) => [xCenter - d * width, yScale(v)]);
    return right.concat(left).map((p, i) => `${i ? "L" : "M"}${p[0].toFixed(2)},${p[1].toFixed(2)}`).join(" ") + "Z";
  }

  function drawSummary() {
    const rows = [
      ["Variance ratio", varianceRatio.toFixed(2)],
      ["p-value", pValue.toFixed(3)],
      ["절대편차 변화", `+${absDevChange.toFixed(1)}`]
    ];
    document.getElementById("summary").innerHTML = rows.map(([label, value]) => `<div class="metric"><div class="label">${label}</div><div class="value">${value}</div></div>`).join("");
  }

  function drawSpread() {
    const svg = document.getElementById("spreadChart");
    const w = 630, h = 440;
    const margin = { top: 22, right: 28, bottom: 60, left: 58 };
    const y = scale(28, 82, h - margin.bottom, margin.top);
    const plotW = w - margin.left - margin.right;
    svg.setAttribute("viewBox", `0 0 ${w} ${h}`);

    for (const t of [30, 40, 50, 60, 70, 80]) {
      svg.appendChild(svgEl("line", { class: "grid-line", x1: margin.left, x2: margin.left + plotW, y1: y(t), y2: y(t) }));
      text(svg, t.toString(), margin.left - 12, y(t) + 4, { class: "tick-text", "text-anchor": "end" });
    }
    svg.appendChild(svgEl("line", { class: "axis-line", x1: margin.left, x2: margin.left + plotW, y1: h - margin.bottom, y2: h - margin.bottom }));
    svg.appendChild(svgEl("line", { class: "axis-line", x1: margin.left, x2: margin.left, y1: margin.top, y2: h - margin.bottom }));
    text(svg, "feature value", 16, margin.top + 178, { class: "axis-label", "text-anchor": "middle", transform: `rotate(-90 16 ${margin.top + 178})` });

    [
      { group: reference, x: margin.left + 185, cls: "ref-fill" },
      { group: current, x: margin.left + 390, cls: "cur-fill" }
    ].forEach(({ group, x, cls }) => {
      svg.appendChild(svgEl("path", { class: cls, d: violinPath(group.density, x, y, 74) }));
      svg.appendChild(svgEl("line", { class: "axis-line", x1: x, x2: x, y1: y(group.low), y2: y(group.high) }));
      svg.appendChild(svgEl("rect", { class: "box", x: x - 35, y: y(group.q3), width: 70, height: y(group.q1) - y(group.q3), rx: 4 }));
      svg.appendChild(svgEl("line", { class: "median-line", x1: x - 35, x2: x + 35, y1: y(group.median), y2: y(group.median) }));
      svg.appendChild(svgEl("line", { class: "center-line", x1: x - 44, x2: x + 44, y1: y(group.center), y2: y(group.center) }));
      const labelY = group.label === "현재" ? y(group.high) + 18 : y(group.high) - 10;
      text(svg, `${group.label} SD ${group.sd.toFixed(1)}`, x, labelY, { class: group.label === "현재" ? "warning" : "callout", "text-anchor": "middle" });
      text(svg, group.label, x, h - 22, { class: "title-text", "text-anchor": "middle" });
    });

    text(svg, `분산비 ${varianceRatio.toFixed(2)}x: 현재 구간의 폭이 넓어짐`, margin.left + plotW / 2, margin.top + 12, { class: "callout", "text-anchor": "middle" });
  }

  function drawVariance() {
    const svg = document.getElementById("varianceChart");
    const w = 472, h = 185;
    const margin = { top: 12, right: 26, bottom: 36, left: 74 };
    const y = scale(0, 130, h - margin.bottom, margin.top);
    const plotW = w - margin.left - margin.right;
    svg.setAttribute("viewBox", `0 0 ${w} ${h}`);

    for (const t of [0, 50, 100]) {
      svg.appendChild(svgEl("line", { class: "grid-line", x1: margin.left, x2: margin.left + plotW, y1: y(t), y2: y(t) }));
      text(svg, t.toString(), margin.left - 10, y(t) + 4, { class: "tick-text", "text-anchor": "end" });
    }
    [
      { group: reference, x: margin.left + 80, cls: "ref-bar" },
      { group: current, x: margin.left + 230, cls: "cur-bar" }
    ].forEach(({ group, x, cls }) => {
      svg.appendChild(svgEl("rect", { class: cls, x, y: y(group.variance), width: 74, height: y(0) - y(group.variance), rx: 5 }));
      text(svg, group.variance.toFixed(1), x + 37, y(group.variance) - 8, { class: "bar-label", "text-anchor": "middle" });
      text(svg, `${group.label} SD ${group.sd.toFixed(1)}`, x + 37, h - 12, { class: "axis-label", "text-anchor": "middle" });
    });
    svg.appendChild(svgEl("line", { class: "axis-line", x1: margin.left, x2: margin.left + plotW, y1: h - margin.bottom, y2: h - margin.bottom }));
    text(svg, `variance ratio = ${varianceRatio.toFixed(2)}x`, margin.left + plotW / 2, margin.top + 15, { class: "callout", "text-anchor": "middle" });
  }

  function drawDeviation() {
    const svg = document.getElementById("deviationChart");
    const w = 472, h = 185;
    const margin = { top: 16, right: 28, bottom: 34, left: 118 };
    const x = scale(0, 10, margin.left, w - margin.right);
    svg.setAttribute("viewBox", `0 0 ${w} ${h}`);

    [
      { label: "기준 |x-center|", value: reference.absDev, cls: "ref-bar" },
      { label: "현재 |x-center|", value: current.absDev, cls: "deviation-bar" },
      { label: "분산비", value: varianceRatio, cls: "ratio-bar" }
    ].forEach((row, i) => {
      const y = margin.top + i * 43 + 10;
      const valueForScale = row.label === "분산비" ? row.value * 2.5 : row.value;
      text(svg, row.label, margin.left - 10, y + 12, { class: "title-text", "text-anchor": "end" });
      svg.appendChild(svgEl("line", { class: "grid-line", x1: margin.left, x2: w - margin.right, y1: y + 9, y2: y + 9 }));
      if (row.label === "분산비") {
        svg.appendChild(svgEl("line", { class: "threshold-line", x1: x(ratioThreshold * 2.5), x2: x(ratioThreshold * 2.5), y1: y - 8, y2: y + 28 }));
      }
      svg.appendChild(svgEl("rect", { class: row.cls, x: margin.left, y, width: x(valueForScale) - margin.left, height: 18, rx: 4 }));
      text(svg, row.label === "분산비" ? `${row.value.toFixed(2)}x` : row.value.toFixed(1), x(valueForScale) + 7, y + 13, { class: "bar-label" });
    });
    text(svg, `Levene p=${pValue.toFixed(3)}`, margin.left + 130, h - 6, { class: "axis-label", "text-anchor": "middle" });
  }

  drawSummary();
  drawSpread();
  drawVariance();
  drawDeviation();
})();
