(function () {
  const values = [0.50,0.48,0.51,0.49,0.52,0.50,0.51,0.53,0.50,0.52,0.54,0.51,0.53,0.55,0.52,0.54,0.56,0.55,0.57,0.58,0.60,0.62,0.65,0.68,0.70,0.73,0.75,0.77,0.79,0.80,0.82,0.83,0.85,0.84,0.86,0.87];
  const referenceMean = 0.53;
  const evidence = [0.0,0.1,0.1,0.2,0.3,0.4,0.6,0.7,0.9,1.1,1.4,1.6,1.9,2.2,2.5,2.8,3.2,3.6,4.1,4.8,5.7,6.8,8.1,9.7,11.4,13.2,15.1,17.0,18.8,20.4,21.8,23.0,24.1,25.0,25.8,26.5];
  const bound = [7,7.2,7.4,7.6,7.8,8.0,8.2,8.4,8.6,8.8,9.0,9.2,9.4,9.6,9.8,10.0,10.2,10.4,10.6,10.8,11.0,11.2,11.4,11.6,11.8,12.0,12.2,12.4,12.6,12.8,13.0,13.2,13.4,13.6,13.8,14.0];
  const alarmIndex = 27;
  const maxEvidence = 26.5;
  const delay = 4;
  const delta = 0.34;

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
      ["evidence", maxEvidence.toFixed(1)],
      ["alarm index", alarmIndex.toString()],
      ["detect delay", `${delay} step`]
    ];
    document.getElementById("summary").innerHTML = rows.map(([label, value]) => `<div class="metric"><div class="label">${label}</div><div class="value">${value}</div></div>`).join("");
  }

  function drawStream() {
    const svg = document.getElementById("streamChart");
    const w = 630, h = 440;
    const margin = { top: 24, right: 28, bottom: 62, left: 58 };
    const x = scale(1, values.length, margin.left, w - margin.right);
    const y = scale(0.42, 0.90, h - margin.bottom, margin.top);
    const plotW = w - margin.left - margin.right;
    svg.setAttribute("viewBox", `0 0 ${w} ${h}`);
    for (const t of [0.5, 0.7, 0.9]) {
      svg.appendChild(svgEl("line", { class: "grid-line", x1: margin.left, x2: margin.left + plotW, y1: y(t), y2: y(t) }));
      text(svg, t.toFixed(1), margin.left - 12, y(t) + 4, { class: "tick-text", "text-anchor": "end" });
    }
    const pts = values.map((v, i) => [x(i + 1), y(v)]);
    svg.appendChild(svgEl("path", { class: "stream-line", d: linePath(pts) }));
    svg.appendChild(svgEl("line", { class: "mean-line", x1: margin.left, x2: margin.left + plotW, y1: y(referenceMean), y2: y(referenceMean) }));
    svg.appendChild(svgEl("line", { class: "alarm-line", x1: x(alarmIndex), x2: x(alarmIndex), y1: margin.top, y2: h - margin.bottom }));
    svg.appendChild(svgEl("circle", { class: "alarm-point", cx: x(alarmIndex), cy: y(values[alarmIndex - 1]), r: 7 }));
    svg.appendChild(svgEl("line", { class: "axis-line", x1: margin.left, x2: margin.left + plotW, y1: h - margin.bottom, y2: h - margin.bottom }));
    svg.appendChild(svgEl("line", { class: "axis-line", x1: margin.left, x2: margin.left, y1: margin.top, y2: h - margin.bottom }));
    for (const t of [1, 10, 20, 30, 36]) {
      text(svg, t.toString(), x(t), h - margin.bottom + 24, { class: "tick-text", "text-anchor": "middle" });
    }
    text(svg, "time index", margin.left + plotW / 2, h - 12, { class: "axis-label", "text-anchor": "middle" });
    text(svg, "value", 16, margin.top + 178, { class: "axis-label", "text-anchor": "middle", transform: `rotate(-90 16 ${margin.top + 178})` });
    text(svg, `reference mean ${referenceMean.toFixed(2)}`, x(3), y(referenceMean) - 8, { class: "callout" });
    text(svg, `alarm, delta +${delta.toFixed(2)}`, x(alarmIndex) + 8, y(0.82), { class: "warning-text" });
  }

  function drawBound() {
    const svg = document.getElementById("boundChart");
    const w = 472, h = 185;
    const margin = { top: 12, right: 22, bottom: 34, left: 48 };
    const x = scale(1, evidence.length, margin.left, w - margin.right);
    const y = scale(0, 30, h - margin.bottom, margin.top);
    const plotW = w - margin.left - margin.right;
    svg.setAttribute("viewBox", `0 0 ${w} ${h}`);
    for (const t of [0, 10, 20, 30]) {
      svg.appendChild(svgEl("line", { class: "grid-line", x1: margin.left, x2: margin.left + plotW, y1: y(t), y2: y(t) }));
      text(svg, t.toString(), margin.left - 10, y(t) + 4, { class: "tick-text", "text-anchor": "end" });
    }
    const evPts = evidence.map((v, i) => [x(i + 1), y(v)]);
    const boundPts = bound.map((v, i) => [x(i + 1), y(v)]);
    svg.appendChild(svgEl("path", { class: "bound-line", d: linePath(boundPts) }));
    svg.appendChild(svgEl("path", { class: "evidence-line", d: linePath(evPts) }));
    evPts.forEach(([cx, cy], i) => svg.appendChild(svgEl("circle", { class: evidence[i] > bound[i] ? "alarm-point" : "evidence-point", cx, cy, r: i + 1 >= alarmIndex ? 4.8 : 3.4 })));
    svg.appendChild(svgEl("line", { class: "axis-line", x1: margin.left, x2: margin.left + plotW, y1: h - margin.bottom, y2: h - margin.bottom }));
    text(svg, "time index", margin.left + 160, h - 8, { class: "axis-label", "text-anchor": "middle" });
    text(svg, "decision bound", w - margin.right - 100, y(13.2) - 6, { class: "warning-text" });
  }

  function drawTimeline() {
    const svg = document.getElementById("timelineChart");
    const w = 472, h = 185;
    const margin = { top: 32, right: 24, bottom: 38, left: 48 };
    const x = scale(1, 36, margin.left, w - margin.right);
    const y = 74;
    svg.setAttribute("viewBox", `0 0 ${w} ${h}`);
    svg.appendChild(svgEl("rect", { class: "state-monitor", x: x(1), y, width: x(22) - x(1), height: 30, rx: 5 }));
    svg.appendChild(svgEl("rect", { class: "state-warning", x: x(22), y, width: x(27) - x(22), height: 30, rx: 5 }));
    svg.appendChild(svgEl("rect", { class: "state-drift", x: x(27), y, width: x(36) - x(27), height: 30, rx: 5 }));
    svg.appendChild(svgEl("line", { class: "alarm-line", x1: x(alarmIndex), x2: x(alarmIndex), y1: margin.top, y2: h - margin.bottom }));
    svg.appendChild(svgEl("circle", { class: "alarm-point", cx: x(alarmIndex), cy: y + 15, r: 7 }));
    text(svg, "monitor", x(10), y + 20, { class: "bar-label", "text-anchor": "middle" });
    text(svg, "warning", x(24), y + 20, { class: "bar-label", "text-anchor": "middle" });
    text(svg, "drift", x(32), y + 20, { class: "bar-label", "text-anchor": "middle" });
    for (const t of [1, 10, 20, 30, 36]) {
      text(svg, t.toString(), x(t), h - margin.bottom + 22, { class: "tick-text", "text-anchor": "middle" });
    }
    svg.appendChild(svgEl("line", { class: "axis-line", x1: margin.left, x2: w - margin.right, y1: h - margin.bottom, y2: h - margin.bottom }));
    text(svg, "sequential decision timeline", margin.left + 180, h - 6, { class: "axis-label", "text-anchor": "middle" });
  }

  drawSummary();
  drawStream();
  drawBound();
  drawTimeline();
})();
