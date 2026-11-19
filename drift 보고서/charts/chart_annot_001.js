(function () {
  const baseline = [0.12,0.18,0.24,0.30,0.38,0.45,0.52,0.58,0.64,0.70,0.75,0.80,0.84,0.88,0.91,0.94];
  const current = [0.08,0.12,0.17,0.23,0.30,0.38,0.46,0.55,0.63,0.71,0.79,0.86,0.91,0.95,0.98,0.99];
  const xValues = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16];
  const upperIndex = 12;
  const lowerIndex = 5;
  const upperGap = 0.11;
  const lowerGap = -0.08;

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
  function areaPath(topPoints, bottomPoints) {
    return `${linePath(topPoints)} L${bottomPoints.slice().reverse().map((p) => `${p[0].toFixed(2)},${p[1].toFixed(2)}`).join(" L")} Z`;
  }

  function drawSummary() {
    const rows = [
      ["direction", "upper"],
      ["D+ gap", "+0.11"],
      ["one-sided p", "0.018"]
    ];
    document.getElementById("summary").innerHTML = rows.map(([label, value]) => `<div class="metric"><div class="label">${label}</div><div class="value">${value}</div></div>`).join("");
  }

  function drawDirection() {
    const svg = document.getElementById("directionChart");
    const w = 630, h = 440;
    const margin = { top: 24, right: 30, bottom: 62, left: 58 };
    const x = scale(1, 16, margin.left, w - margin.right);
    const y = scale(0, 1, h - margin.bottom, margin.top);
    const plotW = w - margin.left - margin.right;
    svg.setAttribute("viewBox", `0 0 ${w} ${h}`);

    for (const t of [0, 0.25, 0.50, 0.75, 1.00]) {
      svg.appendChild(svgEl("line", { class: "grid-line", x1: margin.left, x2: margin.left + plotW, y1: y(t), y2: y(t) }));
      text(svg, t.toFixed(2), margin.left - 12, y(t) + 4, { class: "tick-text", "text-anchor": "end" });
    }

    const basePoints = baseline.map((v, i) => [x(xValues[i]), y(v)]);
    const currentPoints = current.map((v, i) => [x(xValues[i]), y(v)]);
    const upperAreaTop = current.slice(upperIndex - 3, upperIndex + 2).map((v, i) => [x(upperIndex - 2 + i), y(v)]);
    const upperAreaBottom = baseline.slice(upperIndex - 3, upperIndex + 2).map((v, i) => [x(upperIndex - 2 + i), y(v)]);
    const lowerAreaTop = baseline.slice(lowerIndex - 2, lowerIndex + 2).map((v, i) => [x(lowerIndex - 1 + i), y(v)]);
    const lowerAreaBottom = current.slice(lowerIndex - 2, lowerIndex + 2).map((v, i) => [x(lowerIndex - 1 + i), y(v)]);

    svg.appendChild(svgEl("path", { class: "upper-fill", d: areaPath(upperAreaTop, upperAreaBottom) }));
    svg.appendChild(svgEl("path", { class: "lower-fill", d: areaPath(lowerAreaTop, lowerAreaBottom) }));
    svg.appendChild(svgEl("path", { class: "baseline-line", d: linePath(basePoints) }));
    svg.appendChild(svgEl("path", { class: "current-line", d: linePath(currentPoints) }));

    svg.appendChild(svgEl("line", { class: "upper-line", x1: x(upperIndex), x2: x(upperIndex), y1: y(baseline[upperIndex - 1]), y2: y(current[upperIndex - 1]) }));
    svg.appendChild(svgEl("line", { class: "lower-line", x1: x(lowerIndex), x2: x(lowerIndex), y1: y(current[lowerIndex - 1]), y2: y(baseline[lowerIndex - 1]) }));
    svg.appendChild(svgEl("line", { class: "neutral-line", x1: margin.left, x2: margin.left + plotW, y1: y(0.5), y2: y(0.5) }));

    [upperIndex, lowerIndex].forEach((idx) => {
      svg.appendChild(svgEl("circle", { class: idx === upperIndex ? "upper-point" : "lower-point", cx: x(idx), cy: y(current[idx - 1]), r: 6 }));
      svg.appendChild(svgEl("circle", { class: "baseline-point", cx: x(idx), cy: y(baseline[idx - 1]), r: 4 }));
    });
    current.forEach((v, i) => {
      if (i % 3 === 0) svg.appendChild(svgEl("circle", { class: "current-point", cx: x(i + 1), cy: y(v), r: 3 }));
    });

    svg.appendChild(svgEl("line", { class: "axis-line", x1: margin.left, x2: margin.left + plotW, y1: h - margin.bottom, y2: h - margin.bottom }));
    svg.appendChild(svgEl("line", { class: "axis-line", x1: margin.left, x2: margin.left, y1: margin.top, y2: h - margin.bottom }));
    for (const t of [1, 4, 8, 12, 16]) {
      text(svg, t.toString(), x(t), h - margin.bottom + 24, { class: "tick-text", "text-anchor": "middle" });
    }
    text(svg, "ordered value / threshold index", margin.left + plotW / 2, h - 12, { class: "axis-label", "text-anchor": "middle" });
    text(svg, "cumulative probability", 16, margin.top + 178, { class: "axis-label", "text-anchor": "middle", transform: `rotate(-90 16 ${margin.top + 178})` });
    text(svg, "upper one-sided evidence: current > baseline", x(9.7), y(0.92), { class: "callout-upper" });
    text(svg, "opposite direction is not counted", x(2.3), y(0.20), { class: "callout-lower" });
  }

  function drawTestCards() {
    const svg = document.getElementById("testChart");
    const w = 472, h = 185;
    svg.setAttribute("viewBox", `0 0 ${w} ${h}`);
    const cards = [
      ["decision-pass", "Upper / greater", "H1: current is larger", "D+ = +0.11, p=0.018", "DRIFT CANDIDATE"],
      ["decision-fail", "Lower / less", "H1: current is smaller", "D- = -0.08, p=0.214", "not counted"]
    ];
    cards.forEach(([cls, title, h1, stat, decision], i) => {
      const x = 28 + i * 218;
      svg.appendChild(svgEl("rect", { class: cls, x, y: 34, width: 196, height: 108, rx: 8 }));
      text(svg, title, x + 16, 58, { class: "card-title" });
      text(svg, h1, x + 16, 84, { class: "card-text" });
      text(svg, stat, x + 16, 106, { class: "card-text" });
      text(svg, decision, x + 16, 128, { class: i === 0 ? "callout-upper" : "callout-lower" });
    });
    text(svg, "One-sided test must match declared direction", 236, 170, { class: "axis-label", "text-anchor": "middle" });
  }

  function drawMatrix() {
    const svg = document.getElementById("matrixChart");
    const w = 472, h = 185;
    svg.setAttribute("viewBox", `0 0 ${w} ${h}`);
    const methods = ["KS", "Fisher", "MWU", "CUSUM", "EWMA"];
    const cols = ["upper", "lower", "two-sided"];
    const startX = 116;
    const startY = 38;
    const cellW = 82;
    const cellH = 24;
    cols.forEach((col, i) => {
      svg.appendChild(svgEl("rect", { class: "matrix-head", x: startX + i * cellW, y: 12, width: cellW - 4, height: 22, rx: 4 }));
      text(svg, col, startX + i * cellW + 39, 27, { class: "tick-text", "text-anchor": "middle" });
    });
    methods.forEach((method, r) => {
      const y = startY + r * cellH;
      text(svg, method, 94, y + 16, { class: "bar-label", "text-anchor": "end" });
      cols.forEach((_, c) => {
        const active = c < 2;
        svg.appendChild(svgEl("circle", { class: active ? "matrix-on" : "matrix-off", cx: startX + c * cellW + 39, cy: y + 12, r: active ? 7 : 5 }));
      });
    });
    text(svg, "annotation applies when variant declares one-sided direction", 236, 170, { class: "axis-label", "text-anchor": "middle" });
  }

  drawSummary();
  drawDirection();
  drawTestCards();
  drawMatrix();
})();
