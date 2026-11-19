(function () {
  const llr = [-0.4,-0.7,-0.5,-0.8,-0.4,-0.2,0.1,0.3,0.6,0.9,1.3,1.7,2.0,2.4,2.9,3.5,4.2,5.0,5.9,6.8,7.7,8.6,9.4,10.2,11.0,11.8,12.6,13.4,14.1,14.8,15.4,16.0];
  const errorRate = [0.08,0.09,0.07,0.10,0.08,0.09,0.11,0.10,0.12,0.13,0.14,0.15,0.16,0.17,0.18,0.20,0.22,0.24,0.25,0.27,0.29,0.30,0.31,0.32,0.34,0.35,0.36,0.35,0.37,0.38,0.39,0.40];
  const upper = 10.8;
  const lower = -2.2;
  const decisionIndex = 25;
  const alpha = 0.05;
  const beta = 0.10;
  const finalLlr = 16.0;

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
      ["final LLR", finalLlr.toFixed(1)],
      ["alpha / beta", `${alpha.toFixed(2)} / ${beta.toFixed(2)}`],
      ["decision", "accept H1"]
    ];
    document.getElementById("summary").innerHTML = rows.map(([label, value]) => `<div class="metric"><div class="label">${label}</div><div class="value">${value}</div></div>`).join("");
  }

  function drawLlr() {
    const svg = document.getElementById("llrChart");
    const w = 630, h = 440;
    const margin = { top: 24, right: 28, bottom: 62, left: 58 };
    const x = scale(1, llr.length, margin.left, w - margin.right);
    const y = scale(-4, 18, h - margin.bottom, margin.top);
    const plotW = w - margin.left - margin.right;
    svg.setAttribute("viewBox", `0 0 ${w} ${h}`);
    for (const t of [-4, 0, 5, 10, 15]) {
      svg.appendChild(svgEl("line", { class: "grid-line", x1: margin.left, x2: margin.left + plotW, y1: y(t), y2: y(t) }));
      text(svg, t.toString(), margin.left - 12, y(t) + 4, { class: "tick-text", "text-anchor": "end" });
    }
    svg.appendChild(svgEl("line", { class: "upper-line", x1: margin.left, x2: margin.left + plotW, y1: y(upper), y2: y(upper) }));
    svg.appendChild(svgEl("line", { class: "lower-line", x1: margin.left, x2: margin.left + plotW, y1: y(lower), y2: y(lower) }));
    const pts = llr.map((v, i) => [x(i + 1), y(v)]);
    svg.appendChild(svgEl("path", { class: "llr-line", d: linePath(pts) }));
    pts.forEach(([cx, cy], i) => svg.appendChild(svgEl("circle", { class: i + 1 >= decisionIndex ? "decision-point" : "llr-point", cx, cy, r: i + 1 >= decisionIndex ? 4.8 : 3.5 })));
    svg.appendChild(svgEl("line", { class: "alarm-line", x1: x(decisionIndex), x2: x(decisionIndex), y1: margin.top, y2: h - margin.bottom }));
    svg.appendChild(svgEl("line", { class: "axis-line", x1: margin.left, x2: margin.left + plotW, y1: h - margin.bottom, y2: h - margin.bottom }));
    svg.appendChild(svgEl("line", { class: "axis-line", x1: margin.left, x2: margin.left, y1: margin.top, y2: h - margin.bottom }));
    for (const t of [1, 8, 16, 24, 32]) {
      text(svg, t.toString(), x(t), h - margin.bottom + 24, { class: "tick-text", "text-anchor": "middle" });
    }
    text(svg, "time index", margin.left + plotW / 2, h - 12, { class: "axis-label", "text-anchor": "middle" });
    text(svg, "log likelihood ratio", 16, margin.top + 178, { class: "axis-label", "text-anchor": "middle", transform: `rotate(-90 16 ${margin.top + 178})` });
    text(svg, "accept H1 boundary", x(3), y(upper) - 8, { class: "warning-text" });
    text(svg, "accept H0 boundary", x(3), y(lower) + 16, { class: "callout" });
  }

  function drawError() {
    const svg = document.getElementById("errorChart");
    const w = 472, h = 185;
    const margin = { top: 12, right: 22, bottom: 34, left: 48 };
    const x = scale(1, errorRate.length, margin.left, w - margin.right);
    const y = scale(0, 0.45, h - margin.bottom, margin.top);
    const plotW = w - margin.left - margin.right;
    svg.setAttribute("viewBox", `0 0 ${w} ${h}`);
    for (const t of [0, 0.15, 0.30, 0.45]) {
      svg.appendChild(svgEl("line", { class: "grid-line", x1: margin.left, x2: margin.left + plotW, y1: y(t), y2: y(t) }));
      text(svg, t.toFixed(2), margin.left - 10, y(t) + 4, { class: "tick-text", "text-anchor": "end" });
    }
    const pts = errorRate.map((v, i) => [x(i + 1), y(v)]);
    svg.appendChild(svgEl("path", { class: "error-line", d: linePath(pts) }));
    svg.appendChild(svgEl("line", { class: "upper-line", x1: margin.left, x2: margin.left + plotW, y1: y(0.30), y2: y(0.30) }));
    svg.appendChild(svgEl("line", { class: "alarm-line", x1: x(decisionIndex), x2: x(decisionIndex), y1: margin.top, y2: h - margin.bottom }));
    svg.appendChild(svgEl("line", { class: "axis-line", x1: margin.left, x2: margin.left + plotW, y1: h - margin.bottom, y2: h - margin.bottom }));
    text(svg, "error rate", margin.left + 160, h - 8, { class: "axis-label", "text-anchor": "middle" });
    text(svg, "H1 방향 증가", x(21), y(0.36), { class: "warning-text" });
  }

  function drawDecision() {
    const svg = document.getElementById("decisionChart");
    const w = 472, h = 185;
    const margin = { top: 32, right: 24, bottom: 38, left: 48 };
    const x = scale(1, 32, margin.left, w - margin.right);
    const y = 74;
    svg.setAttribute("viewBox", `0 0 ${w} ${h}`);
    svg.appendChild(svgEl("rect", { class: "state-continue", x: x(1), y, width: x(18) - x(1), height: 30, rx: 5 }));
    svg.appendChild(svgEl("rect", { class: "state-review", x: x(18), y, width: x(25) - x(18), height: 30, rx: 5 }));
    svg.appendChild(svgEl("rect", { class: "state-h1", x: x(25), y, width: x(32) - x(25), height: 30, rx: 5 }));
    svg.appendChild(svgEl("line", { class: "alarm-line", x1: x(decisionIndex), x2: x(decisionIndex), y1: margin.top, y2: h - margin.bottom }));
    svg.appendChild(svgEl("circle", { class: "decision-point", cx: x(decisionIndex), cy: y + 15, r: 7 }));
    text(svg, "continue", x(9), y + 20, { class: "bar-label", "text-anchor": "middle" });
    text(svg, "review", x(21), y + 20, { class: "bar-label", "text-anchor": "middle" });
    text(svg, "accept H1", x(29), y + 20, { class: "bar-label", "text-anchor": "middle" });
    for (const t of [1, 8, 16, 24, 32]) {
      text(svg, t.toString(), x(t), h - margin.bottom + 22, { class: "tick-text", "text-anchor": "middle" });
    }
    svg.appendChild(svgEl("line", { class: "axis-line", x1: margin.left, x2: w - margin.right, y1: h - margin.bottom, y2: h - margin.bottom }));
    text(svg, "sequential decision timeline", margin.left + 180, h - 6, { class: "axis-label", "text-anchor": "middle" });
  }

  drawSummary();
  drawLlr();
  drawError();
  drawDecision();
})();
