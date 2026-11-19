(function () {
  const values = [0.42,0.40,0.43,0.41,0.44,0.45,0.43,0.46,0.45,0.47,0.46,0.48,0.47,0.49,0.48,0.50,0.49,0.51,0.52,0.53,0.55,0.57,0.60,0.63,0.66,0.69,0.71,0.74,0.76,0.78,0.79,0.81,0.80,0.82,0.83,0.84];
  const runningMean = [0.42,0.41,0.42,0.42,0.42,0.43,0.43,0.43,0.43,0.44,0.44,0.45,0.45,0.45,0.45,0.46,0.46,0.47,0.47,0.48,0.49,0.50,0.51,0.53,0.54,0.56,0.58,0.60,0.62,0.64,0.65,0.67,0.68,0.69,0.70,0.72];
  const phStat = [0.1,0.2,0.3,0.4,0.6,0.8,1.0,1.2,1.5,1.7,2.0,2.3,2.5,2.8,3.1,3.4,3.8,4.2,4.7,5.3,6.1,7.0,8.2,9.6,11.3,13.1,15.2,17.5,19.6,21.2,22.4,23.5,24.0,24.6,25.1,25.5];
  const threshold = 18.0;
  const alarmIndex = 29;
  const maxStat = 25.5;
  const meanShift = 0.31;

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
      ["PH statistic", maxStat.toFixed(1)],
      ["threshold", threshold.toFixed(1)],
      ["alarm index", alarmIndex.toString()]
    ];
    document.getElementById("summary").innerHTML = rows.map(([label, value]) => `<div class="metric"><div class="label">${label}</div><div class="value">${value}</div></div>`).join("");
  }

  function drawStream() {
    const svg = document.getElementById("streamChart");
    const w = 630, h = 440;
    const margin = { top: 24, right: 28, bottom: 62, left: 58 };
    const x = scale(1, values.length, margin.left, w - margin.right);
    const y = scale(0.35, 0.88, h - margin.bottom, margin.top);
    const plotW = w - margin.left - margin.right;
    svg.setAttribute("viewBox", `0 0 ${w} ${h}`);

    for (const t of [0.4, 0.6, 0.8]) {
      svg.appendChild(svgEl("line", { class: "grid-line", x1: margin.left, x2: margin.left + plotW, y1: y(t), y2: y(t) }));
      text(svg, t.toFixed(1), margin.left - 12, y(t) + 4, { class: "tick-text", "text-anchor": "end" });
    }
    const valuePts = values.map((v, i) => [x(i + 1), y(v)]);
    const meanPts = runningMean.map((v, i) => [x(i + 1), y(v)]);
    svg.appendChild(svgEl("path", { class: "stream-line", d: linePath(valuePts) }));
    svg.appendChild(svgEl("path", { class: "mean-line", d: linePath(meanPts) }));
    svg.appendChild(svgEl("line", { class: "alarm-line", x1: x(alarmIndex), x2: x(alarmIndex), y1: margin.top, y2: h - margin.bottom }));
    svg.appendChild(svgEl("circle", { class: "alarm-point", cx: x(alarmIndex), cy: y(values[alarmIndex - 1]), r: 7 }));
    svg.appendChild(svgEl("line", { class: "axis-line", x1: margin.left, x2: margin.left + plotW, y1: h - margin.bottom, y2: h - margin.bottom }));
    svg.appendChild(svgEl("line", { class: "axis-line", x1: margin.left, x2: margin.left, y1: margin.top, y2: h - margin.bottom }));
    for (const t of [1, 10, 20, 30, 36]) {
      text(svg, t.toString(), x(t), h - margin.bottom + 24, { class: "tick-text", "text-anchor": "middle" });
    }
    text(svg, "time index", margin.left + plotW / 2, h - 12, { class: "axis-label", "text-anchor": "middle" });
    text(svg, "metric", 16, margin.top + 178, { class: "axis-label", "text-anchor": "middle", transform: `rotate(-90 16 ${margin.top + 178})` });
    text(svg, "Page-Hinkley alarm", x(alarmIndex) + 8, margin.top + 24, { class: "warning-text" });
    text(svg, `평균 shift +${meanShift.toFixed(2)}`, x(21), y(0.82), { class: "callout" });
  }

  function drawPh() {
    const svg = document.getElementById("phChart");
    const w = 472, h = 185;
    const margin = { top: 12, right: 22, bottom: 34, left: 48 };
    const x = scale(1, phStat.length, margin.left, w - margin.right);
    const y = scale(0, 28, h - margin.bottom, margin.top);
    const plotW = w - margin.left - margin.right;
    svg.setAttribute("viewBox", `0 0 ${w} ${h}`);
    for (const t of [0, 10, 20]) {
      svg.appendChild(svgEl("line", { class: "grid-line", x1: margin.left, x2: margin.left + plotW, y1: y(t), y2: y(t) }));
      text(svg, t.toString(), margin.left - 10, y(t) + 4, { class: "tick-text", "text-anchor": "end" });
    }
    svg.appendChild(svgEl("line", { class: "threshold-line", x1: margin.left, x2: margin.left + plotW, y1: y(threshold), y2: y(threshold) }));
    const pts = phStat.map((v, i) => [x(i + 1), y(v)]);
    svg.appendChild(svgEl("path", { class: "ph-line", d: linePath(pts) }));
    pts.forEach(([cx, cy], i) => svg.appendChild(svgEl("circle", { class: phStat[i] >= threshold ? "alarm-point" : "ph-point", cx, cy, r: i + 1 >= alarmIndex ? 4.8 : 3.6 })));
    svg.appendChild(svgEl("line", { class: "axis-line", x1: margin.left, x2: margin.left + plotW, y1: h - margin.bottom, y2: h - margin.bottom }));
    text(svg, "time index", margin.left + 160, h - 8, { class: "axis-label", "text-anchor": "middle" });
    text(svg, "threshold 18.0", w - margin.right - 100, y(threshold) - 6, { class: "warning-text" });
  }

  function drawTimeline() {
    const svg = document.getElementById("timelineChart");
    const w = 472, h = 185;
    const margin = { top: 32, right: 24, bottom: 38, left: 48 };
    const x = scale(1, 36, margin.left, w - margin.right);
    const y = 74;
    svg.setAttribute("viewBox", `0 0 ${w} ${h}`);
    svg.appendChild(svgEl("rect", { class: "state-normal", x: x(1), y, width: x(22) - x(1), height: 30, rx: 5 }));
    svg.appendChild(svgEl("rect", { class: "state-warning", x: x(22), y, width: x(29) - x(22), height: 30, rx: 5 }));
    svg.appendChild(svgEl("rect", { class: "state-drift", x: x(29), y, width: x(36) - x(29), height: 30, rx: 5 }));
    svg.appendChild(svgEl("line", { class: "alarm-line", x1: x(alarmIndex), x2: x(alarmIndex), y1: margin.top, y2: h - margin.bottom }));
    svg.appendChild(svgEl("circle", { class: "alarm-point", cx: x(alarmIndex), cy: y + 15, r: 7 }));
    text(svg, "normal", x(10), y + 20, { class: "bar-label", "text-anchor": "middle" });
    text(svg, "warning", x(25), y + 20, { class: "bar-label", "text-anchor": "middle" });
    text(svg, "drift", x(33), y + 20, { class: "bar-label", "text-anchor": "middle" });
    for (const t of [1, 10, 20, 30, 36]) {
      text(svg, t.toString(), x(t), h - margin.bottom + 22, { class: "tick-text", "text-anchor": "middle" });
    }
    svg.appendChild(svgEl("line", { class: "axis-line", x1: margin.left, x2: w - margin.right, y1: h - margin.bottom, y2: h - margin.bottom }));
    text(svg, "alarm marker timeline", margin.left + 170, h - 6, { class: "axis-label", "text-anchor": "middle" });
  }

  drawSummary();
  drawStream();
  drawPh();
  drawTimeline();
})();
