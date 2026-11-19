(function () {
  const reference = [0.055, 0.071, 0.095, 0.128, 0.161, 0.152, 0.125, 0.091, 0.062, 0.040, 0.024, 0.016];
  const currentRaw = [0.035, 0.047, 0.070, 0.102, 0.130, 0.141, 0.134, 0.115, 0.096, 0.066, 0.039, 0.025];
  const sumCur = currentRaw.reduce((a, b) => a + b, 0);
  const current = currentRaw.map(v => v / sumCur);
  const labels = ["<-2.0", "-1.6", "-1.2", "-0.8", "-0.4", "0.0", "0.4", "0.8", "1.2", "1.6", "2.0", ">2.4"];
  const eps = 1e-9;
  const contributions = current.map((q, i) => q * Math.log((q + eps) / (reference[i] + eps)));
  const kl = contributions.reduce((a, b) => a + b, 0);
  const reverseContrib = reference.map((p, i) => p * Math.log((p + eps) / (current[i] + eps)));
  const reverseKl = reverseContrib.reduce((a, b) => a + b, 0);
  const topIndex = contributions.reduce((best, v, i) => v > contributions[best] ? i : best, 0);

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

  function drawDistribution() {
    const svg = document.getElementById("distributionChart");
    const w = 630, h = 440;
    const margin = { top: 20, right: 22, bottom: 58, left: 58 };
    svg.setAttribute("viewBox", `0 0 ${w} ${h}`);
    const maxP = Math.max(...reference, ...current) * 1.22;
    const xSlot = (w - margin.left - margin.right) / reference.length;
    const y = scale(0, maxP, h - margin.bottom, margin.top);
    const plotW = w - margin.left - margin.right;
    const plotH = h - margin.top - margin.bottom;

    for (const t of [0, 0.05, 0.10, 0.15, 0.20]) {
      svg.appendChild(svgEl("line", { class: "grid-line", x1: margin.left, x2: margin.left + plotW, y1: y(t), y2: y(t) }));
      text(svg, t.toFixed(2), margin.left - 12, y(t) + 4, { class: "tick-text", "text-anchor": "end" });
    }
    svg.appendChild(svgEl("line", { class: "axis-line", x1: margin.left, x2: margin.left + plotW, y1: h - margin.bottom, y2: h - margin.bottom }));
    svg.appendChild(svgEl("line", { class: "axis-line", x1: margin.left, x2: margin.left, y1: margin.top, y2: h - margin.bottom }));
    text(svg, "확률 bin", margin.left + plotW / 2, h - 12, { class: "axis-label", "text-anchor": "middle" });
    text(svg, "확률", 16, margin.top + plotH / 2, { class: "axis-label", "text-anchor": "middle", transform: `rotate(-90 16 ${margin.top + plotH / 2})` });

    for (let i = 0; i < reference.length; i += 1) {
      const left = margin.left + i * xSlot + 5;
      const bw = (xSlot - 14) / 2;
      svg.appendChild(svgEl("rect", { class: "ref-bar", x: left, y: y(reference[i]), width: bw, height: y(0) - y(reference[i]), rx: 3 }));
      svg.appendChild(svgEl("rect", { class: "cur-bar", x: left + bw + 4, y: y(current[i]), width: bw, height: y(0) - y(current[i]), rx: 3 }));
      if (i % 2 === 0) {
        text(svg, labels[i], left + bw, h - margin.bottom + 24, { class: "tick-text", "text-anchor": "middle" });
      }
      if (contributions[i] > 0.012) {
        const refCx = left + bw / 2;
        const curCx = left + bw + 4 + bw / 2;
        svg.appendChild(svgEl("line", { class: "contrib-line", x1: refCx, x2: curCx, y1: y(reference[i]), y2: y(current[i]) }));
      }
    }
    const topX = margin.left + topIndex * xSlot + xSlot / 2;
    text(svg, `기여 최대 bin: ${labels[topIndex]}`, topX - 54, margin.top + 18, { class: "callout" });
  }

  function drawTrend() {
    const svg = document.getElementById("trendChart");
    const w = 472, h = 185;
    const margin = { top: 12, right: 18, bottom: 34, left: 48 };
    svg.setAttribute("viewBox", `0 0 ${w} ${h}`);
    const vals = [0.028, 0.034, 0.041, 0.038, 0.052, 0.071, 0.086, kl];
    const threshold = 0.070;
    const yMax = Math.ceil(Math.max(...vals, threshold) * 100) / 100 + 0.02;
    const x = scale(1, vals.length, margin.left, w - margin.right);
    const y = scale(0, yMax, h - margin.bottom, margin.top);
    const plotW = w - margin.left - margin.right;
    for (const t of [0, threshold, yMax]) {
      svg.appendChild(svgEl("line", { class: "grid-line", x1: margin.left, x2: margin.left + plotW, y1: y(t), y2: y(t) }));
      text(svg, t.toFixed(2), margin.left - 10, y(t) + 4, { class: "tick-text", "text-anchor": "end" });
    }
    svg.appendChild(svgEl("line", { class: "threshold-line", x1: margin.left, x2: margin.left + plotW, y1: y(threshold), y2: y(threshold) }));
    const pts = vals.map((v, i) => [x(i + 1), y(v)]);
    svg.appendChild(svgEl("path", { class: "trend-line", d: linePath(pts) }));
    pts.forEach(([cx, cy]) => svg.appendChild(svgEl("circle", { class: "trend-point", cx, cy, r: 4 })));
    svg.appendChild(svgEl("line", { class: "axis-line", x1: margin.left, x2: margin.left + plotW, y1: h - margin.bottom, y2: h - margin.bottom }));
    svg.appendChild(svgEl("line", { class: "axis-line", x1: margin.left, x2: margin.left, y1: margin.top, y2: h - margin.bottom }));
    text(svg, "window", margin.left + plotW / 2, h - 8, { class: "axis-label", "text-anchor": "middle" });
    text(svg, "관리 기준", w - margin.right - 56, y(threshold) - 7, { class: "callout" });
  }

  function drawContrib() {
    const svg = document.getElementById("contribChart");
    const w = 472, h = 185;
    const margin = { top: 8, right: 22, bottom: 28, left: 112 };
    svg.setAttribute("viewBox", `0 0 ${w} ${h}`);
    const rows = contributions
      .map((value, i) => ({ label: labels[i], value }))
      .sort((a, b) => b.value - a.value)
      .slice(0, 5);
    const maxValue = Math.max(...rows.map(r => r.value));
    const x = scale(0, maxValue * 1.18, margin.left, w - margin.right);
    const rowH = 27;
    rows.forEach((row, i) => {
      const y = margin.top + i * rowH + 10;
      text(svg, row.label, margin.left - 10, y + 10, { class: "tick-text", "text-anchor": "end" });
      svg.appendChild(svgEl("rect", { class: i === 0 ? "bar-highlight" : "bar", x: margin.left, y, width: x(row.value) - margin.left, height: 16, rx: 4 }));
      text(svg, row.value.toFixed(3), x(row.value) + 7, y + 12, { class: "bar-label" });
    });
    svg.appendChild(svgEl("line", { class: "axis-line", x1: margin.left, x2: w - margin.right, y1: h - margin.bottom, y2: h - margin.bottom }));
    text(svg, "q log(q / p)", margin.left + (w - margin.right - margin.left) / 2, h - 6, { class: "axis-label", "text-anchor": "middle" });
  }

  function drawSummary() {
    const rows = [
      ["KL(q||p)", kl.toFixed(3)],
      ["역방향 KL", reverseKl.toFixed(3)],
      ["최대 기여 bin", labels[topIndex]]
    ];
    document.getElementById("summary").innerHTML = rows.map(([label, value]) => `<div class="metric"><div class="label">${label}</div><div class="value">${value}</div></div>`).join("");
  }

  drawSummary();
  drawDistribution();
  drawTrend();
  drawContrib();
})();
