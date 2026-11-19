(function () {
  const categories = ["A등급", "B등급", "C등급", "D등급", "기타", "미상"];
  const expected = [132, 210, 176, 112, 58, 32];
  const observed = [101, 194, 225, 139, 39, 22];
  const residuals = observed.map((o, i) => (o - expected[i]) / Math.sqrt(expected[i]));
  const contributions = observed.map((o, i) => ((o - expected[i]) ** 2) / expected[i]);
  const chiSquare = contributions.reduce((a, b) => a + b, 0);
  const df = categories.length - 1;
  const maxContributionIndex = contributions.reduce((best, v, i) => v > contributions[best] ? i : best, 0);
  const lowExpected = expected.filter(v => v < 5).length;

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

  function drawBarChart() {
    const svg = document.getElementById("barChart");
    const w = 630, h = 440;
    const margin = { top: 20, right: 22, bottom: 58, left: 62 };
    svg.setAttribute("viewBox", `0 0 ${w} ${h}`);
    const maxY = Math.ceil(Math.max(...expected, ...observed) / 50) * 50;
    const xSlot = (w - margin.left - margin.right) / categories.length;
    const y = scale(0, maxY, h - margin.bottom, margin.top);
    const plotW = w - margin.left - margin.right;
    const plotH = h - margin.top - margin.bottom;
    for (const t of [0, maxY / 4, maxY / 2, maxY * 3 / 4, maxY]) {
      svg.appendChild(svgEl("line", { class: "grid-line", x1: margin.left, x2: margin.left + plotW, y1: y(t), y2: y(t) }));
      text(svg, String(Math.round(t)), margin.left - 12, y(t) + 4, { class: "tick-text", "text-anchor": "end" });
    }
    svg.appendChild(svgEl("line", { class: "axis-line", x1: margin.left, x2: margin.left + plotW, y1: h - margin.bottom, y2: h - margin.bottom }));
    svg.appendChild(svgEl("line", { class: "axis-line", x1: margin.left, x2: margin.left, y1: margin.top, y2: h - margin.bottom }));
    text(svg, "category", margin.left + plotW / 2, h - 12, { class: "axis-label", "text-anchor": "middle" });
    text(svg, "빈도", 16, margin.top + plotH / 2, { class: "axis-label", "text-anchor": "middle", transform: `rotate(-90 16 ${margin.top + plotH / 2})` });

    for (let i = 0; i < categories.length; i += 1) {
      const left = margin.left + i * xSlot + 12;
      const bw = (xSlot - 28) / 2;
      svg.appendChild(svgEl("rect", { class: "expected-bar", x: left, y: y(expected[i]), width: bw, height: y(0) - y(expected[i]), rx: 3 }));
      svg.appendChild(svgEl("rect", { class: "observed-bar", x: left + bw + 5, y: y(observed[i]), width: bw, height: y(0) - y(observed[i]), rx: 3 }));
      text(svg, categories[i], left + bw + 2, h - margin.bottom + 24, { class: "tick-text", "text-anchor": "middle" });
    }
    text(svg, `기여 최대: ${categories[maxContributionIndex]}`, margin.left + 236, margin.top + 20, { class: "callout" });
  }

  function residualClass(v) {
    if (v > 1.5) return "res-high";
    if (v < -1.5) return "res-low";
    return "res-neutral";
  }

  function drawResidualChart() {
    const svg = document.getElementById("residualChart");
    const w = 472, h = 185;
    const margin = { top: 12, right: 22, bottom: 28, left: 76 };
    svg.setAttribute("viewBox", `0 0 ${w} ${h}`);
    const cellW = (w - margin.left - margin.right) / categories.length;
    const cellH = 48;
    categories.forEach((cat, i) => {
      const x = margin.left + i * cellW + 3;
      const y = 48;
      svg.appendChild(svgEl("rect", { class: residualClass(residuals[i]), x, y, width: cellW - 6, height: cellH, rx: 6 }));
      text(svg, residuals[i].toFixed(1), x + (cellW - 6) / 2, y + 29, { class: "bar-label", "text-anchor": "middle" });
      text(svg, cat, x + (cellW - 6) / 2, y + cellH + 22, { class: "tick-text", "text-anchor": "middle" });
    });
    text(svg, "과소", margin.left, 34, { class: "tick-text" });
    text(svg, "과대", w - margin.right - 32, 34, { class: "tick-text" });
    text(svg, "표준화 잔차 = (관측 - 기대) / sqrt(기대)", margin.left, 150, { class: "axis-label" });
  }

  function drawContributionChart() {
    const svg = document.getElementById("contributionChart");
    const w = 472, h = 185;
    const margin = { top: 8, right: 22, bottom: 28, left: 84 };
    svg.setAttribute("viewBox", `0 0 ${w} ${h}`);
    const rows = contributions
      .map((value, i) => ({ label: categories[i], value }))
      .sort((a, b) => b.value - a.value)
      .slice(0, 5);
    const maxValue = Math.max(...rows.map(r => r.value));
    const x = scale(0, maxValue * 1.18, margin.left, w - margin.right);
    const rowH = 27;
    rows.forEach((row, i) => {
      const y = margin.top + i * rowH + 10;
      text(svg, row.label, margin.left - 10, y + 10, { class: "tick-text", "text-anchor": "end" });
      svg.appendChild(svgEl("rect", { class: i === 0 ? "contrib-highlight" : "contrib-bar", x: margin.left, y, width: x(row.value) - margin.left, height: 16, rx: 4 }));
      text(svg, row.value.toFixed(1), x(row.value) + 7, y + 12, { class: "bar-label" });
    });
    svg.appendChild(svgEl("line", { class: "axis-line", x1: margin.left, x2: w - margin.right, y1: h - margin.bottom, y2: h - margin.bottom }));
    text(svg, "(O-E)^2 / E", margin.left + (w - margin.right - margin.left) / 2, h - 6, { class: "axis-label", "text-anchor": "middle" });
  }

  function drawSummary() {
    const rows = [
      ["Chi-square", chiSquare.toFixed(1)],
      ["df / p-value", `${df} / 0.003`],
      ["낮은 기대빈도", `${lowExpected}개`]
    ];
    document.getElementById("summary").innerHTML = rows.map(([label, value]) => `<div class="metric"><div class="label">${label}</div><div class="value">${value}</div></div>`).join("");
  }

  drawSummary();
  drawBarChart();
  drawResidualChart();
  drawContributionChart();
})();
