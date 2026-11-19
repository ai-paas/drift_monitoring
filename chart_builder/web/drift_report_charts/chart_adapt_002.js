(function () {
  const champion = [0.88,0.88,0.87,0.87,0.86,0.86,0.85,0.84,0.83,0.82,0.81,0.79,0.78,0.77,0.76,0.75,0.74,0.74,0.73,0.73,0.74,0.75,0.76,0.77,0.77,0.78,0.78,0.79,0.79,0.80,0.80,0.81];
  const challenger = [null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,0.78,0.80,0.82,0.84,0.85,0.86,0.87,0.87,0.88,0.88,0.89,0.89];
  const alarmIndex = 18;
  const retrainIndex = 24;
  const promoteIndex = 27;

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
  function segmentedPath(values, x, y) {
    const segments = [];
    let current = [];
    values.forEach((v, i) => {
      if (v === null) {
        if (current.length) segments.push(current);
        current = [];
      } else {
        current.push([x(i + 1), y(v)]);
      }
    });
    if (current.length) segments.push(current);
    return segments;
  }

  function drawSummary() {
    const rows = [
      ["pre AUC", "0.74"],
      ["post AUC", "0.86"],
      ["retrain", `t=${retrainIndex}`]
    ];
    document.getElementById("summary").innerHTML = rows.map(([label, value]) => `<div class="metric"><div class="label">${label}</div><div class="value">${value}</div></div>`).join("");
  }

  function drawPerformance() {
    const svg = document.getElementById("performanceChart");
    const w = 630, h = 440;
    const margin = { top: 24, right: 30, bottom: 62, left: 58 };
    const x = scale(1, champion.length, margin.left, w - margin.right);
    const y = scale(0.70, 0.92, h - margin.bottom, margin.top);
    const plotW = w - margin.left - margin.right;
    svg.setAttribute("viewBox", `0 0 ${w} ${h}`);

    svg.appendChild(svgEl("rect", { x: margin.left, y: margin.top, width: x(retrainIndex) - margin.left, height: h - margin.top - margin.bottom, fill: "rgba(201,149,47,0.08)" }));
    svg.appendChild(svgEl("rect", { x: x(retrainIndex), y: margin.top, width: margin.left + plotW - x(retrainIndex), height: h - margin.top - margin.bottom, fill: "rgba(58,128,100,0.08)" }));

    for (const t of [0.72, 0.78, 0.84, 0.90]) {
      svg.appendChild(svgEl("line", { class: "grid-line", x1: margin.left, x2: margin.left + plotW, y1: y(t), y2: y(t) }));
      text(svg, t.toFixed(2), margin.left - 12, y(t) + 4, { class: "tick-text", "text-anchor": "end" });
    }
    svg.appendChild(svgEl("line", { class: "baseline-line", x1: margin.left, x2: margin.left + plotW, y1: y(0.84), y2: y(0.84) }));
    text(svg, "target AUC 0.84", margin.left + 10, y(0.84) - 8, { class: "axis-label" });

    svg.appendChild(svgEl("path", { class: "champion-line", d: linePath(champion.map((v, i) => [x(i + 1), y(v)])) }));
    segmentedPath(challenger, x, y).forEach((segment) => {
      svg.appendChild(svgEl("path", { class: "challenger-line", d: linePath(segment) }));
    });

    for (const idx of [alarmIndex, retrainIndex]) {
      svg.appendChild(svgEl("line", { class: idx === alarmIndex ? "alarm-line" : "retrain-line", x1: x(idx), x2: x(idx), y1: margin.top, y2: h - margin.bottom }));
    }

    champion.forEach((v, i) => {
      if (i % 3 === 0 || i + 1 === alarmIndex || i + 1 === retrainIndex) {
        svg.appendChild(svgEl("circle", { class: i + 1 === alarmIndex ? "alarm-point" : "champion-point", cx: x(i + 1), cy: y(v), r: i + 1 === alarmIndex ? 6 : 3.5 }));
      }
    });
    challenger.forEach((v, i) => {
      if (v !== null && (i % 2 === 0 || i + 1 === promoteIndex)) {
        svg.appendChild(svgEl("circle", { class: i + 1 === retrainIndex ? "retrain-point" : "challenger-point", cx: x(i + 1), cy: y(v), r: i + 1 === promoteIndex ? 6 : 3.5 }));
      }
    });

    svg.appendChild(svgEl("line", { class: "axis-line", x1: margin.left, x2: margin.left + plotW, y1: h - margin.bottom, y2: h - margin.bottom }));
    svg.appendChild(svgEl("line", { class: "axis-line", x1: margin.left, x2: margin.left, y1: margin.top, y2: h - margin.bottom }));
    for (const t of [1, 8, 16, 24, 32]) {
      text(svg, t.toString(), x(t), h - margin.bottom + 24, { class: "tick-text", "text-anchor": "middle" });
    }
    text(svg, "time index", margin.left + plotW / 2, h - 12, { class: "axis-label", "text-anchor": "middle" });
    text(svg, "validation AUC", 16, margin.top + 178, { class: "axis-label", "text-anchor": "middle", transform: `rotate(-90 16 ${margin.top + 178})` });
    text(svg, "drift alarm", x(alarmIndex) - 56, y(0.72) - 10, { class: "callout-alarm" });
    text(svg, "retrain event", x(retrainIndex) + 8, y(0.72) - 10, { class: "callout-retrain" });
    text(svg, "challenger promoted", x(promoteIndex) - 18, y(0.89) - 12, { class: "callout-win" });
  }

  function drawTimeline() {
    const svg = document.getElementById("timelineChart");
    const w = 472, h = 185;
    const margin = { top: 34, right: 24, bottom: 38, left: 48 };
    const x = scale(1, 32, margin.left, w - margin.right);
    const y = 76;
    svg.setAttribute("viewBox", `0 0 ${w} ${h}`);
    const spans = [
      ["state-normal", 1, 13, "normal", 7],
      ["state-warning", 13, alarmIndex, "warning", 15.4],
      ["state-drift", alarmIndex, retrainIndex, "alarm", 21],
      ["state-retrain", retrainIndex, 32, "retrain/monitor", 28]
    ];
    spans.forEach(([cls, start, end, label, mid]) => {
      svg.appendChild(svgEl("rect", { class: cls, x: x(start), y, width: x(end) - x(start), height: 30, rx: 5 }));
      text(svg, label, x(mid), y + 20, { class: "bar-label", "text-anchor": "middle" });
    });
    svg.appendChild(svgEl("line", { class: "alarm-line", x1: x(alarmIndex), x2: x(alarmIndex), y1: margin.top, y2: h - margin.bottom }));
    svg.appendChild(svgEl("line", { class: "retrain-line", x1: x(retrainIndex), x2: x(retrainIndex), y1: margin.top, y2: h - margin.bottom }));
    svg.appendChild(svgEl("circle", { class: "alarm-point", cx: x(alarmIndex), cy: y + 15, r: 6 }));
    svg.appendChild(svgEl("circle", { class: "retrain-point", cx: x(retrainIndex), cy: y + 15, r: 6 }));
    svg.appendChild(svgEl("line", { class: "axis-line", x1: margin.left, x2: w - margin.right, y1: h - margin.bottom, y2: h - margin.bottom }));
    text(svg, "workflow event timeline", margin.left + 178, h - 6, { class: "axis-label", "text-anchor": "middle" });
  }

  function drawComparison() {
    const svg = document.getElementById("comparisonChart");
    const w = 472, h = 185;
    const margin = { top: 14, right: 32, bottom: 36, left: 112 };
    const x = scale(0, 1, margin.left, w - margin.right);
    const rows = [
      ["AUC", 0.77, 0.87, "higher"],
      ["F1", 0.70, 0.82, "higher"],
      ["latency", 0.46, 0.53, "lower"]
    ];
    const y0 = 32;
    const gap = 42;
    svg.setAttribute("viewBox", `0 0 ${w} ${h}`);
    rows.forEach(([label, championValue, challengerValue, direction], i) => {
      const y = y0 + i * gap;
      text(svg, label, margin.left - 18, y + 14, { class: "bar-label", "text-anchor": "end" });
      svg.appendChild(svgEl("rect", { class: "bar-champion", x: margin.left, y, width: x(championValue) - margin.left, height: 13, rx: 3 }));
      svg.appendChild(svgEl("rect", { class: direction === "lower" ? "bar-latency" : "bar-challenger", x: margin.left, y: y + 17, width: x(challengerValue) - margin.left, height: 13, rx: 3 }));
      text(svg, championValue.toFixed(2), x(championValue) + 6, y + 11, { class: "tick-text" });
      text(svg, challengerValue.toFixed(2), x(challengerValue) + 6, y + 28, { class: "tick-text" });
    });
    text(svg, "champion", margin.left, h - 14, { class: "axis-label" });
    text(svg, "challenger", margin.left + 88, h - 14, { class: "callout-win" });
    text(svg, "승격 후보: 성능 개선, latency 영향 점검", margin.left + 132, 18, { class: "callout-win" });
  }

  drawSummary();
  drawPerformance();
  drawTimeline();
  drawComparison();
})();
