(function () {
  const values = [0.31,0.29,0.33,0.30,0.32,0.34,0.31,0.35,0.33,0.36,0.34,0.37,0.35,0.36,0.38,0.39,0.37,0.40,0.41,0.39,0.43,0.45,0.50,0.56,0.61,0.65,0.68,0.70,0.72,0.71,0.73,0.75,0.76,0.74,0.77,0.78];
  const rollingMean = [0.31,0.30,0.31,0.31,0.31,0.32,0.32,0.33,0.33,0.34,0.34,0.35,0.35,0.36,0.36,0.37,0.37,0.38,0.39,0.39,0.41,0.43,0.46,0.50,0.55,0.60,0.64,0.67,0.69,0.70,0.71,0.73,0.74,0.74,0.75,0.76];
  const alarmIndex = 23;
  const windowWidth = [120,122,125,127,130,132,135,138,140,142,145,148,150,152,154,156,158,160,162,164,166,168,170,62,70,78,86,94,104,112,120,128,136,144,152,160];
  const beforeMean = 0.38;
  const afterMean = 0.68;
  const deltaMean = afterMean - beforeMean;
  const pValue = 0.009;

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
      ["alarm index", alarmIndex.toString()],
      ["mean delta", `+${deltaMean.toFixed(2)}`],
      ["p-value", pValue.toFixed(3)]
    ];
    document.getElementById("summary").innerHTML = rows.map(([label, value]) => `<div class="metric"><div class="label">${label}</div><div class="value">${value}</div></div>`).join("");
  }

  function drawStream() {
    const svg = document.getElementById("streamChart");
    const w = 630, h = 440;
    const margin = { top: 24, right: 28, bottom: 62, left: 58 };
    const x = scale(1, values.length, margin.left, w - margin.right);
    const y = scale(0.2, 0.85, h - margin.bottom, margin.top);
    const plotW = w - margin.left - margin.right;
    svg.setAttribute("viewBox", `0 0 ${w} ${h}`);

    for (const t of [0.2, 0.4, 0.6, 0.8]) {
      svg.appendChild(svgEl("line", { class: "grid-line", x1: margin.left, x2: margin.left + plotW, y1: y(t), y2: y(t) }));
      text(svg, t.toFixed(1), margin.left - 12, y(t) + 4, { class: "tick-text", "text-anchor": "end" });
    }
    for (const t of [1, 10, 20, 30, 36]) {
      text(svg, t.toString(), x(t), h - margin.bottom + 24, { class: "tick-text", "text-anchor": "middle" });
    }
    const valuePts = values.map((v, i) => [x(i + 1), y(v)]);
    const meanPts = rollingMean.map((v, i) => [x(i + 1), y(v)]);
    svg.appendChild(svgEl("path", { class: "stream-line", d: linePath(valuePts) }));
    svg.appendChild(svgEl("path", { class: "mean-line", d: linePath(meanPts) }));
    svg.appendChild(svgEl("line", { class: "alarm-line", x1: x(alarmIndex), x2: x(alarmIndex), y1: margin.top, y2: h - margin.bottom }));
    svg.appendChild(svgEl("circle", { class: "alarm-point", cx: x(alarmIndex), cy: y(values[alarmIndex - 1]), r: 7 }));
    svg.appendChild(svgEl("line", { class: "axis-line", x1: margin.left, x2: margin.left + plotW, y1: h - margin.bottom, y2: h - margin.bottom }));
    svg.appendChild(svgEl("line", { class: "axis-line", x1: margin.left, x2: margin.left, y1: margin.top, y2: h - margin.bottom }));
    text(svg, "time index", margin.left + plotW / 2, h - 12, { class: "axis-label", "text-anchor": "middle" });
    text(svg, "metric", 16, margin.top + 178, { class: "axis-label", "text-anchor": "middle", transform: `rotate(-90 16 ${margin.top + 178})` });
    text(svg, "ADWIN alarm", x(alarmIndex) + 8, margin.top + 22, { class: "warning" });
    text(svg, "새 평균 수준으로 안정", x(27), y(0.77), { class: "callout" });
  }

  function drawWindow() {
    const svg = document.getElementById("windowChart");
    const w = 472, h = 185;
    const margin = { top: 12, right: 22, bottom: 34, left: 48 };
    const x = scale(1, windowWidth.length, margin.left, w - margin.right);
    const y = scale(40, 180, h - margin.bottom, margin.top);
    const plotW = w - margin.left - margin.right;
    svg.setAttribute("viewBox", `0 0 ${w} ${h}`);
    for (const t of [50, 100, 150]) {
      svg.appendChild(svgEl("line", { class: "grid-line", x1: margin.left, x2: margin.left + plotW, y1: y(t), y2: y(t) }));
      text(svg, t.toString(), margin.left - 10, y(t) + 4, { class: "tick-text", "text-anchor": "end" });
    }
    const pts = windowWidth.map((v, i) => [x(i + 1), y(v)]);
    svg.appendChild(svgEl("path", { class: "window-line", d: linePath(pts) }));
    pts.forEach(([cx, cy], i) => svg.appendChild(svgEl("circle", { class: i + 1 === alarmIndex ? "alarm-point" : "window-point", cx, cy, r: i + 1 === alarmIndex ? 5.5 : 3.6 })));
    svg.appendChild(svgEl("line", { class: "alarm-line", x1: x(alarmIndex), x2: x(alarmIndex), y1: margin.top, y2: h - margin.bottom }));
    svg.appendChild(svgEl("line", { class: "axis-line", x1: margin.left, x2: margin.left + plotW, y1: h - margin.bottom, y2: h - margin.bottom }));
    text(svg, "window width", margin.left + 160, h - 8, { class: "axis-label", "text-anchor": "middle" });
    text(svg, "alarm 후 window 축소", x(alarmIndex) + 8, y(70), { class: "warning" });
  }

  function drawMean() {
    const svg = document.getElementById("meanChart");
    const w = 472, h = 185;
    const margin = { top: 12, right: 32, bottom: 34, left: 58 };
    const y = scale(0, 0.85, h - margin.bottom, margin.top);
    const bars = [
      { label: "before", value: beforeMean, cls: "mean-bar-before" },
      { label: "after", value: afterMean, cls: "mean-bar-after" },
      { label: "delta", value: deltaMean, cls: "delta-bar" }
    ];
    svg.setAttribute("viewBox", `0 0 ${w} ${h}`);
    for (const t of [0, 0.3, 0.6]) {
      svg.appendChild(svgEl("line", { class: "grid-line", x1: margin.left, x2: w - margin.right, y1: y(t), y2: y(t) }));
      text(svg, t.toFixed(1), margin.left - 10, y(t) + 4, { class: "tick-text", "text-anchor": "end" });
    }
    bars.forEach((bar, i) => {
      const x = margin.left + i * 122 + 38;
      const barH = h - margin.bottom - y(bar.value);
      svg.appendChild(svgEl("rect", { class: bar.cls, x, y: y(bar.value), width: 58, height: barH, rx: 5 }));
      text(svg, bar.label, x + 29, h - margin.bottom + 20, { class: "tick-text", "text-anchor": "middle" });
      text(svg, bar.value.toFixed(2), x + 29, y(bar.value) - 8, { class: "bar-label", "text-anchor": "middle" });
    });
    svg.appendChild(svgEl("line", { class: "threshold-line", x1: margin.left, x2: w - margin.right, y1: y(0.20), y2: y(0.20) }));
    svg.appendChild(svgEl("line", { class: "axis-line", x1: margin.left, x2: w - margin.right, y1: h - margin.bottom, y2: h - margin.bottom }));
    text(svg, "운영 기준 delta 0.20", w - margin.right - 120, y(0.20) - 6, { class: "warning" });
  }

  drawSummary();
  drawStream();
  drawWindow();
  drawMean();
})();
