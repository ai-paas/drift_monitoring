(function () {
  const raw = [0.50,0.49,0.51,0.50,0.52,0.51,0.53,0.52,0.54,0.53,0.55,0.56,0.54,0.57,0.58,0.60,0.62,0.63,0.65,0.67,0.70,0.72,0.73,0.75,0.76,0.78,0.80,0.79,0.82,0.83,0.84,0.86];
  const pos = [0,0,0.1,0.1,0.3,0.4,0.7,0.9,1.3,1.6,2.1,2.7,3.0,3.8,4.7,5.8,7.1,8.5,10.2,12.1,14.5,17.1,19.8,22.8,25.9,29.3,33.0,36.4,40.2,44.2,48.4,52.9];
  const neg = [0,0.1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0];
  const target = 0.53;
  const limit = 25;
  const alarmIndex = 25;
  const cplus = 52.9;
  const cminus = 0.1;
  const shift = 0.29;

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
      ["C+ max", cplus.toFixed(1)],
      ["C- max", cminus.toFixed(1)],
      ["shift", `+${shift.toFixed(2)}`]
    ];
    document.getElementById("summary").innerHTML = rows.map(([label, value]) => `<div class="metric"><div class="label">${label}</div><div class="value">${value}</div></div>`).join("");
  }

  function drawRaw() {
    const svg = document.getElementById("rawChart");
    const w = 630, h = 440;
    const margin = { top: 24, right: 28, bottom: 62, left: 58 };
    const x = scale(1, raw.length, margin.left, w - margin.right);
    const y = scale(0.45, 0.90, h - margin.bottom, margin.top);
    const plotW = w - margin.left - margin.right;
    svg.setAttribute("viewBox", `0 0 ${w} ${h}`);
    for (const t of [0.5, 0.6, 0.7, 0.8, 0.9]) {
      svg.appendChild(svgEl("line", { class: "grid-line", x1: margin.left, x2: margin.left + plotW, y1: y(t), y2: y(t) }));
      text(svg, t.toFixed(1), margin.left - 12, y(t) + 4, { class: "tick-text", "text-anchor": "end" });
    }
    svg.appendChild(svgEl("line", { class: "mean-line", x1: margin.left, x2: margin.left + plotW, y1: y(target), y2: y(target) }));
    const pts = raw.map((v, i) => [x(i + 1), y(v)]);
    svg.appendChild(svgEl("path", { class: "raw-line", d: linePath(pts) }));
    svg.appendChild(svgEl("line", { class: "alarm-line", x1: x(alarmIndex), x2: x(alarmIndex), y1: margin.top, y2: h - margin.bottom }));
    svg.appendChild(svgEl("circle", { class: "alarm-point", cx: x(alarmIndex), cy: y(raw[alarmIndex - 1]), r: 7 }));
    svg.appendChild(svgEl("line", { class: "axis-line", x1: margin.left, x2: margin.left + plotW, y1: h - margin.bottom, y2: h - margin.bottom }));
    svg.appendChild(svgEl("line", { class: "axis-line", x1: margin.left, x2: margin.left, y1: margin.top, y2: h - margin.bottom }));
    for (const t of [1, 8, 16, 24, 32]) {
      text(svg, t.toString(), x(t), h - margin.bottom + 24, { class: "tick-text", "text-anchor": "middle" });
    }
    text(svg, "time index", margin.left + plotW / 2, h - 12, { class: "axis-label", "text-anchor": "middle" });
    text(svg, "metric", 16, margin.top + 178, { class: "axis-label", "text-anchor": "middle", transform: `rotate(-90 16 ${margin.top + 178})` });
    text(svg, `target ${target.toFixed(2)}`, x(2), y(target) - 8, { class: "callout" });
    text(svg, "상방 CUSUM alarm", x(alarmIndex) + 8, y(0.82), { class: "warning-text" });
  }

  function drawCusum() {
    const svg = document.getElementById("cusumChart");
    const w = 472, h = 185;
    const margin = { top: 12, right: 22, bottom: 34, left: 48 };
    const x = scale(1, pos.length, margin.left, w - margin.right);
    const y = scale(0, 56, h - margin.bottom, margin.top);
    const plotW = w - margin.left - margin.right;
    svg.setAttribute("viewBox", `0 0 ${w} ${h}`);
    for (const t of [0, 20, 40]) {
      svg.appendChild(svgEl("line", { class: "grid-line", x1: margin.left, x2: margin.left + plotW, y1: y(t), y2: y(t) }));
      text(svg, t.toString(), margin.left - 10, y(t) + 4, { class: "tick-text", "text-anchor": "end" });
    }
    svg.appendChild(svgEl("line", { class: "limit-line", x1: margin.left, x2: margin.left + plotW, y1: y(limit), y2: y(limit) }));
    svg.appendChild(svgEl("path", { class: "pos-line", d: linePath(pos.map((v, i) => [x(i + 1), y(v)])) }));
    svg.appendChild(svgEl("path", { class: "neg-line", d: linePath(neg.map((v, i) => [x(i + 1), y(v)])) }));
    pos.forEach((v, i) => {
      if (i % 3 === 0 || i + 1 >= alarmIndex) svg.appendChild(svgEl("circle", { class: v >= limit ? "alarm-point" : "pos-point", cx: x(i + 1), cy: y(v), r: v >= limit ? 4.6 : 3.4 }));
    });
    svg.appendChild(svgEl("line", { class: "axis-line", x1: margin.left, x2: margin.left + plotW, y1: h - margin.bottom, y2: h - margin.bottom }));
    text(svg, "time index", margin.left + 160, h - 8, { class: "axis-label", "text-anchor": "middle" });
    text(svg, "control limit 25", w - margin.right - 108, y(limit) - 6, { class: "warning-text" });
  }

  function drawDirection() {
    const svg = document.getElementById("summaryChart");
    const w = 472, h = 185;
    const margin = { top: 18, right: 32, bottom: 34, left: 86 };
    const rows = [
      { label: "C+ 상방", value: cplus, cls: "bar-pos" },
      { label: "C- 하방", value: cminus, cls: "bar-neg" }
    ];
    const x = scale(0, 60, margin.left, w - margin.right);
    svg.setAttribute("viewBox", `0 0 ${w} ${h}`);
    rows.forEach((row, i) => {
      const y = margin.top + i * 48 + 16;
      text(svg, row.label, margin.left - 8, y + 15, { class: "tick-text", "text-anchor": "end" });
      svg.appendChild(svgEl("rect", { class: row.cls, x: margin.left, y, width: Math.max(3, x(row.value) - margin.left), height: 22, rx: 5 }));
      text(svg, row.value.toFixed(1), x(row.value) + 8, y + 16, { class: "bar-label" });
    });
    svg.appendChild(svgEl("line", { class: "limit-line", x1: x(limit), x2: x(limit), y1: margin.top, y2: h - margin.bottom }));
    svg.appendChild(svgEl("line", { class: "axis-line", x1: margin.left, x2: w - margin.right, y1: h - margin.bottom, y2: h - margin.bottom }));
    text(svg, "상방 변화가 지배적", margin.left + 142, h - 8, { class: "warning-text", "text-anchor": "middle" });
  }

  drawSummary();
  drawRaw();
  drawCusum();
  drawDirection();
})();
