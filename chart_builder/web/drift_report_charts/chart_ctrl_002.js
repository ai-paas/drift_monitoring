(function () {
  const raw = [0.48,0.52,0.49,0.51,0.50,0.54,0.49,0.53,0.52,0.55,0.51,0.56,0.54,0.57,0.55,0.59,0.61,0.58,0.63,0.64,0.66,0.68,0.69,0.71,0.73,0.74,0.76,0.75,0.78,0.80,0.79,0.82];
  const ewma = [0.50,0.51,0.50,0.51,0.50,0.52,0.51,0.52,0.52,0.53,0.52,0.54,0.54,0.55,0.55,0.56,0.58,0.58,0.60,0.61,0.63,0.65,0.66,0.68,0.70,0.71,0.73,0.74,0.75,0.77,0.78,0.80];
  const center = 0.50;
  const ucl = 0.72;
  const lcl = 0.28;
  const alarmIndex = 27;
  const lambda = 0.20;
  const finalEwma = 0.80;
  const shift = 0.30;

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
      ["EWMA final", finalEwma.toFixed(2)],
      ["lambda", lambda.toFixed(2)],
      ["shift", `+${shift.toFixed(2)}`]
    ];
    document.getElementById("summary").innerHTML = rows.map(([label, value]) => `<div class="metric"><div class="label">${label}</div><div class="value">${value}</div></div>`).join("");
  }

  function drawRaw() {
    const svg = document.getElementById("rawChart");
    const w = 630, h = 440;
    const margin = { top: 24, right: 28, bottom: 62, left: 58 };
    const x = scale(1, raw.length, margin.left, w - margin.right);
    const y = scale(0.25, 0.85, h - margin.bottom, margin.top);
    const plotW = w - margin.left - margin.right;
    svg.setAttribute("viewBox", `0 0 ${w} ${h}`);
    for (const t of [0.3, 0.5, 0.7]) {
      svg.appendChild(svgEl("line", { class: "grid-line", x1: margin.left, x2: margin.left + plotW, y1: y(t), y2: y(t) }));
      text(svg, t.toFixed(1), margin.left - 12, y(t) + 4, { class: "tick-text", "text-anchor": "end" });
    }
    svg.appendChild(svgEl("line", { class: "center-line", x1: margin.left, x2: margin.left + plotW, y1: y(center), y2: y(center) }));
    svg.appendChild(svgEl("path", { class: "raw-line", d: linePath(raw.map((v, i) => [x(i + 1), y(v)])) }));
    svg.appendChild(svgEl("path", { class: "smooth-line", d: linePath(ewma.map((v, i) => [x(i + 1), y(v)])) }));
    svg.appendChild(svgEl("line", { class: "alarm-line", x1: x(alarmIndex), x2: x(alarmIndex), y1: margin.top, y2: h - margin.bottom }));
    svg.appendChild(svgEl("circle", { class: "alarm-point", cx: x(alarmIndex), cy: y(ewma[alarmIndex - 1]), r: 7 }));
    svg.appendChild(svgEl("line", { class: "axis-line", x1: margin.left, x2: margin.left + plotW, y1: h - margin.bottom, y2: h - margin.bottom }));
    svg.appendChild(svgEl("line", { class: "axis-line", x1: margin.left, x2: margin.left, y1: margin.top, y2: h - margin.bottom }));
    for (const t of [1, 8, 16, 24, 32]) {
      text(svg, t.toString(), x(t), h - margin.bottom + 24, { class: "tick-text", "text-anchor": "middle" });
    }
    text(svg, "time index", margin.left + plotW / 2, h - 12, { class: "axis-label", "text-anchor": "middle" });
    text(svg, "metric", 16, margin.top + 178, { class: "axis-label", "text-anchor": "middle", transform: `rotate(-90 16 ${margin.top + 178})` });
    text(svg, "EWMA가 raw noise를 완화해 상승 추세를 포착", x(10), y(0.80), { class: "callout" });
  }

  function drawControl() {
    const svg = document.getElementById("controlChart");
    const w = 472, h = 185;
    const margin = { top: 12, right: 22, bottom: 34, left: 48 };
    const x = scale(1, ewma.length, margin.left, w - margin.right);
    const y = scale(0.20, 0.86, h - margin.bottom, margin.top);
    const plotW = w - margin.left - margin.right;
    svg.setAttribute("viewBox", `0 0 ${w} ${h}`);
    for (const t of [0.3, 0.5, 0.7]) {
      svg.appendChild(svgEl("line", { class: "grid-line", x1: margin.left, x2: margin.left + plotW, y1: y(t), y2: y(t) }));
      text(svg, t.toFixed(1), margin.left - 10, y(t) + 4, { class: "tick-text", "text-anchor": "end" });
    }
    svg.appendChild(svgEl("line", { class: "limit-line", x1: margin.left, x2: margin.left + plotW, y1: y(ucl), y2: y(ucl) }));
    svg.appendChild(svgEl("line", { class: "limit-line", x1: margin.left, x2: margin.left + plotW, y1: y(lcl), y2: y(lcl) }));
    svg.appendChild(svgEl("line", { class: "center-line", x1: margin.left, x2: margin.left + plotW, y1: y(center), y2: y(center) }));
    const pts = ewma.map((v, i) => [x(i + 1), y(v)]);
    svg.appendChild(svgEl("path", { class: "smooth-line", d: linePath(pts) }));
    pts.forEach(([cx, cy], i) => {
      if (i % 3 === 0 || ewma[i] >= ucl) svg.appendChild(svgEl("circle", { class: ewma[i] >= ucl ? "alarm-point" : "smooth-point", cx, cy, r: ewma[i] >= ucl ? 4.8 : 3.4 }));
    });
    svg.appendChild(svgEl("line", { class: "axis-line", x1: margin.left, x2: margin.left + plotW, y1: h - margin.bottom, y2: h - margin.bottom }));
    text(svg, "time index", margin.left + 160, h - 8, { class: "axis-label", "text-anchor": "middle" });
    text(svg, "UCL 0.72", w - margin.right - 70, y(ucl) - 6, { class: "warning-text" });
  }

  function drawTimeline() {
    const svg = document.getElementById("timelineChart");
    const w = 472, h = 185;
    const margin = { top: 32, right: 24, bottom: 38, left: 48 };
    const x = scale(1, 32, margin.left, w - margin.right);
    const y = 74;
    svg.setAttribute("viewBox", `0 0 ${w} ${h}`);
    svg.appendChild(svgEl("rect", { class: "state-normal", x: x(1), y, width: x(21) - x(1), height: 30, rx: 5 }));
    svg.appendChild(svgEl("rect", { class: "state-warning", x: x(21), y, width: x(27) - x(21), height: 30, rx: 5 }));
    svg.appendChild(svgEl("rect", { class: "state-alarm", x: x(27), y, width: x(32) - x(27), height: 30, rx: 5 }));
    svg.appendChild(svgEl("line", { class: "alarm-line", x1: x(alarmIndex), x2: x(alarmIndex), y1: margin.top, y2: h - margin.bottom }));
    svg.appendChild(svgEl("circle", { class: "alarm-point", cx: x(alarmIndex), cy: y + 15, r: 7 }));
    text(svg, "normal", x(10), y + 20, { class: "bar-label", "text-anchor": "middle" });
    text(svg, "warning", x(24), y + 20, { class: "bar-label", "text-anchor": "middle" });
    text(svg, "alarm", x(30), y + 20, { class: "bar-label", "text-anchor": "middle" });
    for (const t of [1, 8, 16, 24, 32]) {
      text(svg, t.toString(), x(t), h - margin.bottom + 22, { class: "tick-text", "text-anchor": "middle" });
    }
    svg.appendChild(svgEl("line", { class: "axis-line", x1: margin.left, x2: w - margin.right, y1: h - margin.bottom, y2: h - margin.bottom }));
    text(svg, "EWMA alarm marker timeline", margin.left + 180, h - 6, { class: "axis-label", "text-anchor": "middle" });
  }

  drawSummary();
  drawRaw();
  drawControl();
  drawTimeline();
})();
