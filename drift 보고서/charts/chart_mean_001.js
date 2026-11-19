(function () {
  const reference = {
    label: "기준",
    mean: 51.2,
    ci: [49.6, 52.8],
    q1: 45.5,
    median: 50.8,
    q3: 56.4,
    low: 36.5,
    high: 66.0,
    density: [
      [36, 0.18], [40, 0.42], [44, 0.72], [48, 0.95], [52, 1.00],
      [56, 0.78], [60, 0.45], [64, 0.22], [68, 0.08]
    ]
  };
  const current = {
    label: "현재",
    mean: 57.8,
    ci: [55.9, 59.7],
    q1: 51.2,
    median: 57.4,
    q3: 63.8,
    low: 42.0,
    high: 74.5,
    density: [
      [42, 0.12], [46, 0.30], [50, 0.58], [54, 0.86], [58, 1.00],
      [62, 0.88], [66, 0.58], [70, 0.32], [74, 0.12]
    ]
  };
  const pValue = 0.004;
  const cohenD = 0.72;
  const meanDiff = current.mean - reference.mean;
  const alpha = 0.05;
  const effectThreshold = 0.50;

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
      ["평균 차이", `+${meanDiff.toFixed(1)}`],
      ["p-value", pValue.toFixed(3)],
      ["Cohen's d", cohenD.toFixed(2)]
    ];
    document.getElementById("summary").innerHTML = rows.map(([label, value]) => `<div class="metric"><div class="label">${label}</div><div class="value">${value}</div></div>`).join("");
  }

  function drawDistribution() {
    const svg = document.getElementById("distributionChart");
    const w = 630, h = 440;
    const margin = { top: 22, right: 28, bottom: 60, left: 58 };
    const y = scale(34, 78, h - margin.bottom, margin.top);
    const plotW = w - margin.left - margin.right;
    svg.setAttribute("viewBox", `0 0 ${w} ${h}`);

    for (const t of [40, 50, 60, 70]) {
      svg.appendChild(svgEl("line", { class: "grid-line", x1: margin.left, x2: margin.left + plotW, y1: y(t), y2: y(t) }));
      text(svg, t.toString(), margin.left - 12, y(t) + 4, { class: "tick-text", "text-anchor": "end" });
    }
    svg.appendChild(svgEl("line", { class: "axis-line", x1: margin.left, x2: margin.left + plotW, y1: h - margin.bottom, y2: h - margin.bottom }));
    svg.appendChild(svgEl("line", { class: "axis-line", x1: margin.left, x2: margin.left, y1: margin.top, y2: h - margin.bottom }));
    text(svg, "feature value", 16, margin.top + 180, { class: "axis-label", "text-anchor": "middle", transform: `rotate(-90 16 ${margin.top + 180})` });

    [
      { group: reference, x: margin.left + 185, cls: "ref-fill" },
      { group: current, x: margin.left + 390, cls: "cur-fill" }
    ].forEach(({ group, x, cls }) => {
      svg.appendChild(svgEl("path", { class: cls, d: violinPath(group.density, x, y, 72) }));
      svg.appendChild(svgEl("line", { class: "axis-line", x1: x, x2: x, y1: y(group.low), y2: y(group.high) }));
      svg.appendChild(svgEl("rect", { class: "box", x: x - 34, y: y(group.q3), width: 68, height: y(group.q1) - y(group.q3), rx: 4 }));
      svg.appendChild(svgEl("line", { class: "median-line", x1: x - 34, x2: x + 34, y1: y(group.median), y2: y(group.median) }));
      svg.appendChild(svgEl("line", { class: "mean-line", x1: x - 42, x2: x + 42, y1: y(group.mean), y2: y(group.mean) }));
      text(svg, `${group.label} mean ${group.mean.toFixed(1)}`, x, y(group.mean) - 10, { class: "callout", "text-anchor": "middle" });
      text(svg, group.label, x, h - 22, { class: "title-text", "text-anchor": "middle" });
    });

    text(svg, `평균 이동: +${meanDiff.toFixed(1)}`, margin.left + plotW / 2, margin.top + 18, { class: "callout", "text-anchor": "middle" });
  }

  function drawCI() {
    const svg = document.getElementById("ciChart");
    const w = 472, h = 185;
    const margin = { top: 16, right: 30, bottom: 38, left: 50 };
    const x = scale(46, 62, margin.left, w - margin.right);
    svg.setAttribute("viewBox", `0 0 ${w} ${h}`);

    for (const t of [48, 52, 56, 60]) {
      svg.appendChild(svgEl("line", { class: "grid-line", x1: x(t), x2: x(t), y1: margin.top, y2: h - margin.bottom }));
      text(svg, t.toString(), x(t), h - 16, { class: "tick-text", "text-anchor": "middle" });
    }
    [
      { group: reference, y: 62, cls: "ci-line-ref" },
      { group: current, y: 112, cls: "ci-line-cur" }
    ].forEach(({ group, y: rowY, cls }) => {
      text(svg, group.label, margin.left - 12, rowY + 4, { class: "title-text", "text-anchor": "end" });
      svg.appendChild(svgEl("line", { class: cls, x1: x(group.ci[0]), x2: x(group.ci[1]), y1: rowY, y2: rowY }));
      svg.appendChild(svgEl("circle", { class: "mean-point", cx: x(group.mean), cy: rowY, r: 7 }));
      text(svg, `${group.mean.toFixed(1)} [${group.ci[0]}, ${group.ci[1]}]`, x(group.mean), rowY - 15, { class: "bar-label", "text-anchor": "middle" });
    });
    svg.appendChild(svgEl("line", { class: "axis-line", x1: margin.left, x2: w - margin.right, y1: h - margin.bottom, y2: h - margin.bottom }));
    text(svg, "mean value", margin.left + (w - margin.right - margin.left) / 2, h - 4, { class: "axis-label", "text-anchor": "middle" });
  }

  function drawEffect() {
    const svg = document.getElementById("effectChart");
    const w = 472, h = 185;
    const margin = { top: 15, right: 28, bottom: 32, left: 112 };
    svg.setAttribute("viewBox", `0 0 ${w} ${h}`);
    const rows = [
      { label: "Cohen's d", value: cohenD, max: 1.2, threshold: effectThreshold, cls: "effect-bar", text: cohenD.toFixed(2) },
      { label: "1 - p-value", value: 1 - pValue, max: 1.0, threshold: 1 - alpha, cls: "pvalue-bar", text: `p=${pValue.toFixed(3)}` }
    ];
    rows.forEach((row, i) => {
      const y = margin.top + i * 62 + 18;
      const x = scale(0, row.max, margin.left, w - margin.right);
      text(svg, row.label, margin.left - 10, y + 12, { class: "title-text", "text-anchor": "end" });
      svg.appendChild(svgEl("line", { class: "grid-line", x1: margin.left, x2: w - margin.right, y1: y + 9, y2: y + 9 }));
      svg.appendChild(svgEl("line", { class: "threshold-line", x1: x(row.threshold), x2: x(row.threshold), y1: y - 10, y2: y + 30 }));
      svg.appendChild(svgEl("rect", { class: row.cls, x: margin.left, y, width: x(row.value) - margin.left, height: 18, rx: 4 }));
      const labelAttrs = row.label === "1 - p-value" ? { class: "bar-label", "text-anchor": "end" } : { class: "bar-label" };
      const labelX = row.label === "1 - p-value" ? x(row.value) - 7 : x(row.value) + 7;
      text(svg, row.text, labelX, y + 13, labelAttrs);
    });
    text(svg, "효과크기 기준 / p-value 기준", margin.left + 130, h - 6, { class: "axis-label", "text-anchor": "middle" });
  }

  drawSummary();
  drawDistribution();
  drawCI();
  drawEffect();
})();
