(function () {
  const exact = [0.06,0.07,0.08,0.10,0.11,0.13,0.17,0.22,0.28,0.34,0.39,0.43,0.46,0.49,0.51,0.52];
  const approx = [0.05,0.08,0.07,0.11,0.10,0.14,0.16,0.20,0.27,0.33,0.36,0.40,0.44,0.46,0.48,0.50];
  const tolerance = 0.04;

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
      ["approx error", "0.03"],
      ["projections", "128"],
      ["q error max", "0.022"]
    ];
    document.getElementById("summary").innerHTML = rows.map(([label, value]) => `<div class="metric"><div class="label">${label}</div><div class="value">${value}</div></div>`).join("");
  }

  function drawError() {
    const svg = document.getElementById("errorChart");
    const w = 630, h = 440;
    const margin = { top: 24, right: 30, bottom: 62, left: 58 };
    const x = scale(1, exact.length, margin.left, w - margin.right);
    const y = scale(0, 0.58, h - margin.bottom, margin.top);
    const plotW = w - margin.left - margin.right;
    svg.setAttribute("viewBox", `0 0 ${w} ${h}`);

    for (const t of [0.00, 0.15, 0.30, 0.45]) {
      svg.appendChild(svgEl("line", { class: "grid-line", x1: margin.left, x2: margin.left + plotW, y1: y(t), y2: y(t) }));
      text(svg, t.toFixed(2), margin.left - 12, y(t) + 4, { class: "tick-text", "text-anchor": "end" });
    }

    const upper = approx.map((v, i) => [x(i + 1), y(v + tolerance)]);
    const lower = approx.map((v, i) => [x(i + 1), y(Math.max(0, v - tolerance))]);
    svg.appendChild(svgEl("path", { class: "band-fill", d: areaPath(upper, lower) }));
    svg.appendChild(svgEl("path", { class: "exact-line", d: linePath(exact.map((v, i) => [x(i + 1), y(v)])) }));
    svg.appendChild(svgEl("path", { class: "approx-line", d: linePath(approx.map((v, i) => [x(i + 1), y(v)])) }));
    svg.appendChild(svgEl("line", { class: "limit-line", x1: margin.left, x2: margin.left + plotW, y1: y(0.42), y2: y(0.42) }));
    text(svg, "drift threshold", margin.left + 10, y(0.42) - 8, { class: "callout" });

    exact.forEach((v, i) => {
      if (i % 3 === 0 || i > 10) {
        svg.appendChild(svgEl("circle", { class: "exact-point", cx: x(i + 1), cy: y(v), r: 3.5 }));
      }
    });
    approx.forEach((v, i) => {
      if (i % 3 === 1 || i > 10) {
        const err = Math.abs(v - exact[i]);
        svg.appendChild(svgEl("circle", { class: err > tolerance ? "warn-point" : "approx-point", cx: x(i + 1), cy: y(v), r: err > tolerance ? 5 : 3.5 }));
      }
    });

    svg.appendChild(svgEl("line", { class: "axis-line", x1: margin.left, x2: margin.left + plotW, y1: h - margin.bottom, y2: h - margin.bottom }));
    svg.appendChild(svgEl("line", { class: "axis-line", x1: margin.left, x2: margin.left, y1: margin.top, y2: h - margin.bottom }));
    for (const t of [1, 4, 8, 12, 16]) {
      text(svg, t.toString(), x(t), h - margin.bottom + 24, { class: "tick-text", "text-anchor": "middle" });
    }
    text(svg, "time window", margin.left + plotW / 2, h - 12, { class: "axis-label", "text-anchor": "middle" });
    text(svg, "distance / statistic", 16, margin.top + 178, { class: "axis-label", "text-anchor": "middle", transform: `rotate(-90 16 ${margin.top + 178})` });
    text(svg, "approximation band within tolerance", x(6), y(0.54), { class: "ok-text" });
    text(svg, "threshold region requires exact check", x(10.5), y(0.47), { class: "callout" });
  }

  function drawProjection() {
    const svg = document.getElementById("projectionChart");
    const w = 472, h = 185;
    const margin = { top: 20, right: 30, bottom: 38, left: 58 };
    const counts = [16, 32, 64, 128, 256];
    const spread = [0.081, 0.054, 0.035, 0.022, 0.019];
    const x = scale(0, counts.length - 1, margin.left, w - margin.right);
    const y = scale(0, 0.09, h - margin.bottom, margin.top);
    svg.setAttribute("viewBox", `0 0 ${w} ${h}`);
    svg.appendChild(svgEl("line", { class: "tolerance-line", x1: margin.left, x2: w - margin.right, y1: y(0.04), y2: y(0.04) }));
    text(svg, "tolerance 0.04", margin.left + 8, y(0.04) - 7, { class: "axis-label" });
    spread.forEach((v, i) => {
      const barX = x(i) - 18;
      const barH = h - margin.bottom - y(v);
      svg.appendChild(svgEl("rect", { class: v > 0.04 ? "bar-over" : "bar-projection", x: barX, y: y(v), width: 36, height: barH, rx: 4 }));
      text(svg, counts[i].toString(), x(i), h - margin.bottom + 22, { class: "tick-text", "text-anchor": "middle" });
    });
    svg.appendChild(svgEl("line", { class: "axis-line", x1: margin.left, x2: w - margin.right, y1: h - margin.bottom, y2: h - margin.bottom }));
    text(svg, "projection count", margin.left + 178, h - 6, { class: "axis-label", "text-anchor": "middle" });
    text(svg, "128+ projections stable", x(3) - 48, y(0.076), { class: "ok-text" });
  }

  function drawQuantile() {
    const svg = document.getElementById("quantileChart");
    const w = 472, h = 185;
    const margin = { top: 24, right: 40, bottom: 38, left: 88 };
    const rows = [
      ["q25", 0.014],
      ["q50", 0.018],
      ["q75", 0.022],
      ["tail", 0.041]
    ];
    const x = scale(0, 0.05, margin.left, w - margin.right);
    svg.setAttribute("viewBox", `0 0 ${w} ${h}`);
    svg.appendChild(svgEl("line", { class: "limit-line", x1: x(0.03), x2: x(0.03), y1: 22, y2: h - margin.bottom }));
    text(svg, "target 0.03", x(0.03) + 6, 18, { class: "callout" });
    rows.forEach(([label, value], i) => {
      const y = 40 + i * 27;
      text(svg, label, margin.left - 16, y + 11, { class: "bar-label", "text-anchor": "end" });
      svg.appendChild(svgEl("rect", { class: value > 0.03 ? "bar-over" : "bar-error", x: margin.left, y, width: x(value) - margin.left, height: 14, rx: 3 }));
      text(svg, value.toFixed(3), x(value) + 7, y + 12, { class: "tick-text" });
    });
    svg.appendChild(svgEl("line", { class: "axis-line", x1: margin.left, x2: w - margin.right, y1: h - margin.bottom, y2: h - margin.bottom }));
    text(svg, "quantile absolute error", margin.left + 150, h - 6, { class: "axis-label", "text-anchor": "middle" });
  }

  drawSummary();
  drawError();
  drawProjection();
  drawQuantile();
})();
