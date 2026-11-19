(function () {
  const rows = [
    { label: "기준", event: 6, nonevent: 36 },
    { label: "현재", event: 14, nonevent: 24 }
  ];
  const alpha = 0.05;
  const pValue = 0.018;
  const oneSidedP = 0.009;
  const oddsRatio = (rows[1].event * rows[0].nonevent) / (rows[1].nonevent * rows[0].event);
  const ciLow = 1.18;
  const ciHigh = 10.40;

  function scale(d0, d1, r0, r1) {
    return (v) => r0 + (v - d0) / (d1 - d0) * (r1 - r0);
  }
  function logScale(d0, d1, r0, r1) {
    const l0 = Math.log(d0);
    const l1 = Math.log(d1);
    return (v) => r0 + (Math.log(v) - l0) / (l1 - l0) * (r1 - r0);
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

  function rate(row) {
    return row.event / (row.event + row.nonevent);
  }

  function drawSummary() {
    const currentRate = rate(rows[1]);
    const referenceRate = rate(rows[0]);
    const diff = currentRate - referenceRate;
    const items = [
      ["Fisher p-value", pValue.toFixed(3)],
      ["Odds ratio", oddsRatio.toFixed(2)],
      ["Event rate 변화", `+${(diff * 100).toFixed(1)}pp`]
    ];
    document.getElementById("summary").innerHTML = items.map(([label, value]) => `<div class="metric"><div class="label">${label}</div><div class="value">${value}</div></div>`).join("");
  }

  function drawMosaic() {
    const svg = document.getElementById("mosaicChart");
    const w = 630, h = 440;
    const margin = { top: 32, right: 36, bottom: 52, left: 70 };
    const plotW = w - margin.left - margin.right;
    const rowGap = 28;
    const rowH = (h - margin.top - margin.bottom - rowGap) / 2;
    svg.setAttribute("viewBox", `0 0 ${w} ${h}`);

    text(svg, "Event", margin.left + 18, margin.top - 11, { class: "title-text" });
    text(svg, "Non-event", margin.left + plotW - 18, margin.top - 11, { class: "title-text", "text-anchor": "end" });

    rows.forEach((row, i) => {
      const y = margin.top + i * (rowH + rowGap);
      const total = row.event + row.nonevent;
      const eventW = plotW * row.event / total;
      const nonEventW = plotW - eventW;
      text(svg, `${row.label}  n=${total}`, margin.left - 14, y + rowH / 2 + 5, { class: "title-text", "text-anchor": "end" });
      svg.appendChild(svgEl("rect", { class: "event-fill", x: margin.left, y, width: eventW, height: rowH, rx: 7 }));
      svg.appendChild(svgEl("rect", { class: "nonevent-fill", x: margin.left + eventW, y, width: nonEventW, height: rowH, rx: 7 }));
      if (row.label === "현재") {
        svg.appendChild(svgEl("rect", { class: "current-outline", x: margin.left - 2, y: y - 2, width: plotW + 4, height: rowH + 4, rx: 8 }));
      }
      text(svg, `${row.event}건`, margin.left + eventW / 2, y + rowH / 2 - 3, { class: "cell-label", "text-anchor": "middle" });
      text(svg, `${(rate(row) * 100).toFixed(1)}%`, margin.left + eventW / 2, y + rowH / 2 + 17, { class: "cell-label", "text-anchor": "middle" });
      text(svg, `${row.nonevent}건`, margin.left + eventW + nonEventW / 2, y + rowH / 2 - 3, { class: "cell-label dark", "text-anchor": "middle" });
      text(svg, `${((1 - rate(row)) * 100).toFixed(1)}%`, margin.left + eventW + nonEventW / 2, y + rowH / 2 + 17, { class: "cell-label dark", "text-anchor": "middle" });
    });

    text(svg, `two-sided p=${pValue.toFixed(3)}, one-sided p=${oneSidedP.toFixed(3)}`, margin.left + plotW / 2, h - 18, { class: "callout", "text-anchor": "middle" });
  }

  function drawRateChart() {
    const svg = document.getElementById("rateChart");
    const w = 472, h = 185;
    const margin = { top: 8, right: 26, bottom: 35, left: 54 };
    const y = scale(0, 0.45, h - margin.bottom, margin.top);
    const plotW = w - margin.left - margin.right;
    svg.setAttribute("viewBox", `0 0 ${w} ${h}`);

    for (const t of [0, 0.15, 0.30, 0.45]) {
      svg.appendChild(svgEl("line", { class: "grid-line", x1: margin.left, x2: margin.left + plotW, y1: y(t), y2: y(t) }));
      text(svg, `${Math.round(t * 100)}%`, margin.left - 10, y(t) + 4, { class: "tick-text", "text-anchor": "end" });
    }

    rows.forEach((row, i) => {
      const bw = 72;
      const x = margin.left + 74 + i * 150;
      const r = rate(row);
      svg.appendChild(svgEl("rect", { class: i === 0 ? "ref-bar" : "cur-bar", x, y: y(r), width: bw, height: y(0) - y(r), rx: 5 }));
      text(svg, `${(r * 100).toFixed(1)}%`, x + bw / 2, y(r) - 8, { class: "title-text", "text-anchor": "middle" });
      text(svg, row.label, x + bw / 2, h - 10, { class: "axis-label", "text-anchor": "middle" });
      text(svg, `event ${row.event}/${row.event + row.nonevent}`, x + bw / 2, y(0) - 8, { class: "tick-text", "text-anchor": "middle" });
    });

    svg.appendChild(svgEl("line", { class: "axis-line", x1: margin.left, x2: margin.left + plotW, y1: h - margin.bottom, y2: h - margin.bottom }));
    text(svg, "Event rate", 16, 82, { class: "axis-label", "text-anchor": "middle", transform: "rotate(-90 16 82)" });
  }

  function drawForest() {
    const svg = document.getElementById("forestChart");
    const w = 472, h = 185;
    const margin = { top: 20, right: 28, bottom: 42, left: 60 };
    const x = logScale(0.3, 12, margin.left, w - margin.right);
    const y = 82;
    svg.setAttribute("viewBox", `0 0 ${w} ${h}`);

    for (const tick of [0.5, 1, 2, 4, 8]) {
      svg.appendChild(svgEl("line", { class: "grid-line", x1: x(tick), x2: x(tick), y1: margin.top, y2: h - margin.bottom }));
      text(svg, tick.toString(), x(tick), h - 16, { class: "tick-text", "text-anchor": "middle" });
    }
    svg.appendChild(svgEl("line", { class: "threshold-line", x1: x(1), x2: x(1), y1: margin.top, y2: h - margin.bottom }));
    svg.appendChild(svgEl("line", { class: "or-line", x1: x(ciLow), x2: x(ciHigh), y1: y, y2: y }));
    svg.appendChild(svgEl("circle", { class: "or-point", cx: x(oddsRatio), cy: y, r: 8 }));
    text(svg, `OR ${oddsRatio.toFixed(2)}  [${ciLow.toFixed(2)}, ${ciHigh.toFixed(1)}]`, x(oddsRatio), y - 18, { class: "warning", "text-anchor": "middle" });
    text(svg, "현재 event odds / 기준 event odds", margin.left + (w - margin.right - margin.left) / 2, h - 4, { class: "axis-label", "text-anchor": "middle" });
    text(svg, "Null", x(1) + 6, margin.top + 12, { class: "callout" });
  }

  drawSummary();
  drawMosaic();
  drawRateChart();
  drawForest();
})();
