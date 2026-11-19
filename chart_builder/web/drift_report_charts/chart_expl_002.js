(function () {
  const features = ["query_age", "region", "device", "amount", "channel", "tenure"];
  const importance = [0.34, 0.26, 0.18, 0.13, 0.08, 0.05];
  const timeSplits = [18, 13, 8, 5, 4, 2];
  const segments = [
    ["S1", 0.72, 0.28],
    ["S2", 0.54, 0.46],
    ["S3", 0.31, 0.69],
    ["S4", 0.18, 0.82]
  ];

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

  function drawSummary() {
    const rows = [
      ["top feature", "query_age"],
      ["time splits", "18"],
      ["current leaf", "82%"]
    ];
    document.getElementById("summary").innerHTML = rows.map(([label, value]) => `<div class="metric"><div class="label">${label}</div><div class="value">${value}</div></div>`).join("");
  }

  function drawImportance() {
    const svg = document.getElementById("importanceChart");
    const w = 630, h = 440;
    const margin = { top: 24, right: 46, bottom: 62, left: 94 };
    const xImp = scale(0, 0.38, margin.left, w - margin.right - 80);
    const xTime = scale(0, 20, margin.left, w - margin.right - 80);
    const rowH = 48;
    svg.setAttribute("viewBox", `0 0 ${w} ${h}`);
    for (const t of [0, 0.1, 0.2, 0.3]) {
      svg.appendChild(svgEl("line", { class: "grid-line", x1: xImp(t), x2: xImp(t), y1: margin.top, y2: h - margin.bottom }));
      text(svg, t.toFixed(1), xImp(t), h - margin.bottom + 24, { class: "tick-text", "text-anchor": "middle" });
    }
    features.forEach((feature, i) => {
      const y = margin.top + i * rowH + 12;
      text(svg, feature, margin.left - 10, y + 18, { class: "bar-label", "text-anchor": "end" });
      svg.appendChild(svgEl("rect", { class: "importance-bar", x: margin.left, y, width: xImp(importance[i]) - margin.left, height: 14, rx: 4 }));
      svg.appendChild(svgEl("rect", { class: "time-bar", x: margin.left, y: y + 19, width: xTime(timeSplits[i]) - margin.left, height: 14, rx: 4 }));
      text(svg, timeSplits[i].toString(), xTime(timeSplits[i]) + 8, y + 31, { class: "tick-text" });
    });
    svg.appendChild(svgEl("line", { class: "axis-line", x1: margin.left, x2: w - margin.right, y1: h - margin.bottom, y2: h - margin.bottom }));
    text(svg, "feature importance / time split count", margin.left + 238, h - 12, { class: "axis-label", "text-anchor": "middle" });
    text(svg, "query_age dominates time/domain split", xImp(0.13), margin.top - 5, { class: "warning-text" });
  }

  function drawPath() {
    const svg = document.getElementById("pathChart");
    const w = 472, h = 185;
    svg.setAttribute("viewBox", `0 0 ${w} ${h}`);
    const nodes = [
      { x: 170, y: 14, w: 150, h: 34, label: "query_age > 14d", cls: "node" },
      { x: 72, y: 78, w: 142, h: 34, label: "region = APAC", cls: "node" },
      { x: 272, y: 78, w: 142, h: 34, label: "device = mobile", cls: "node-current" },
      { x: 280, y: 132, w: 132, h: 30, label: "current 82%", cls: "node-current" }
    ];
    svg.appendChild(svgEl("line", { class: "path-line", x1: 245, y1: 48, x2: 143, y2: 78 }));
    svg.appendChild(svgEl("line", { class: "path-line", x1: 245, y1: 48, x2: 343, y2: 78 }));
    svg.appendChild(svgEl("line", { class: "path-line", x1: 343, y1: 112, x2: 346, y2: 132 }));
    nodes.forEach((n) => {
      svg.appendChild(svgEl("rect", { class: n.cls, x: n.x, y: n.y, width: n.w, height: n.h, rx: 6 }));
      text(svg, n.label, n.x + n.w / 2, n.y + n.h / 2 + 4, { class: "bar-label", "text-anchor": "middle" });
    });
    text(svg, "representative drift path", 236, 178, { class: "axis-label", "text-anchor": "middle" });
  }

  function drawSegment() {
    const svg = document.getElementById("segmentChart");
    const w = 472, h = 185;
    const margin = { top: 18, right: 24, bottom: 32, left: 52 };
    const barW = w - margin.left - margin.right;
    svg.setAttribute("viewBox", `0 0 ${w} ${h}`);
    segments.forEach(([name, base, current], i) => {
      const y = margin.top + i * 30;
      text(svg, name, margin.left - 10, y + 18, { class: "bar-label", "text-anchor": "end" });
      svg.appendChild(svgEl("rect", { class: "base-bar", x: margin.left, y: y + 4, width: barW * base, height: 16, rx: 4 }));
      svg.appendChild(svgEl("rect", { class: "current-bar", x: margin.left + barW * base, y: y + 4, width: barW * current, height: 16, rx: 4 }));
      text(svg, `${Math.round(current * 100)}%`, margin.left + barW * base + barW * current - 8, y + 17, { class: "bar-label", "text-anchor": "end" });
    });
    svg.appendChild(svgEl("line", { class: "axis-line", x1: margin.left, x2: w - margin.right, y1: h - margin.bottom, y2: h - margin.bottom }));
    text(svg, "baseline / current segment mix", margin.left + 170, h - 8, { class: "axis-label", "text-anchor": "middle" });
  }

  drawSummary();
  drawImportance();
  drawPath();
  drawSegment();
})();
