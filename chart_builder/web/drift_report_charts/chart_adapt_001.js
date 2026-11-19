(function () {
  const accuracy = [0.91,0.92,0.91,0.90,0.91,0.90,0.89,0.88,0.86,0.84,0.82,0.80,0.78,0.77,0.76,0.75,0.74,0.73,0.72,0.73,0.75,0.78,0.81,0.84,0.86,0.88,0.89,0.90,0.91,0.91,0.92,0.92];
  const mainSize = [18,20,22,24,25,27,29,31,34,36,38,40,42,44,46,48,50,52,54,55,56,57,42,43,45,47,49,51,53,54,55,56];
  const altSize = [0,0,0,0,0,0,0,0,0,0,4,8,12,17,22,28,34,40,46,52,58,64,0,0,0,0,0,0,0,0,0,0];
  const warningIndex = 11;
  const alternateIndex = 14;
  const replaceIndex = 23;

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
      ["accuracy min", "0.72"],
      ["replacement", `t=${replaceIndex}`],
      ["alt nodes", "64"]
    ];
    document.getElementById("summary").innerHTML = rows.map(([label, value]) => `<div class="metric"><div class="label">${label}</div><div class="value">${value}</div></div>`).join("");
  }

  function drawAccuracy() {
    const svg = document.getElementById("accuracyChart");
    const w = 630, h = 440;
    const margin = { top: 24, right: 28, bottom: 62, left: 58 };
    const x = scale(1, accuracy.length, margin.left, w - margin.right);
    const y = scale(0.68, 0.94, h - margin.bottom, margin.top);
    const plotW = w - margin.left - margin.right;
    svg.setAttribute("viewBox", `0 0 ${w} ${h}`);
    for (const t of [0.70, 0.78, 0.86, 0.94]) {
      svg.appendChild(svgEl("line", { class: "grid-line", x1: margin.left, x2: margin.left + plotW, y1: y(t), y2: y(t) }));
      text(svg, t.toFixed(2), margin.left - 12, y(t) + 4, { class: "tick-text", "text-anchor": "end" });
    }
    svg.appendChild(svgEl("path", { class: "accuracy-line", d: linePath(accuracy.map((v, i) => [x(i + 1), y(v)])) }));
    accuracy.forEach((v, i) => {
      if (i % 3 === 0 || i + 1 >= warningIndex) {
        svg.appendChild(svgEl("circle", { class: i + 1 === replaceIndex ? "replace-point" : "accuracy-point", cx: x(i + 1), cy: y(v), r: i + 1 === replaceIndex ? 7 : 3.5 }));
      }
    });
    for (const idx of [warningIndex, alternateIndex, replaceIndex]) {
      svg.appendChild(svgEl("line", { class: "marker-line", x1: x(idx), x2: x(idx), y1: margin.top, y2: h - margin.bottom, opacity: idx === replaceIndex ? "1" : "0.65" }));
    }
    svg.appendChild(svgEl("line", { class: "axis-line", x1: margin.left, x2: margin.left + plotW, y1: h - margin.bottom, y2: h - margin.bottom }));
    svg.appendChild(svgEl("line", { class: "axis-line", x1: margin.left, x2: margin.left, y1: margin.top, y2: h - margin.bottom }));
    for (const t of [1, 8, 16, 24, 32]) {
      text(svg, t.toString(), x(t), h - margin.bottom + 24, { class: "tick-text", "text-anchor": "middle" });
    }
    text(svg, "time index", margin.left + plotW / 2, h - 12, { class: "axis-label", "text-anchor": "middle" });
    text(svg, "online accuracy", 16, margin.top + 178, { class: "axis-label", "text-anchor": "middle", transform: `rotate(-90 16 ${margin.top + 178})` });
    text(svg, "alternate replacement restores accuracy", x(15), y(0.91), { class: "warning-text" });
  }

  function drawState() {
    const svg = document.getElementById("stateChart");
    const w = 472, h = 185;
    const margin = { top: 32, right: 24, bottom: 38, left: 48 };
    const x = scale(1, 32, margin.left, w - margin.right);
    const y = 74;
    svg.setAttribute("viewBox", `0 0 ${w} ${h}`);
    svg.appendChild(svgEl("rect", { class: "state-normal", x: x(1), y, width: x(warningIndex) - x(1), height: 30, rx: 5 }));
    svg.appendChild(svgEl("rect", { class: "state-warning", x: x(warningIndex), y, width: x(alternateIndex) - x(warningIndex), height: 30, rx: 5 }));
    svg.appendChild(svgEl("rect", { class: "state-alt", x: x(alternateIndex), y, width: x(replaceIndex) - x(alternateIndex), height: 30, rx: 5 }));
    svg.appendChild(svgEl("rect", { class: "state-replace", x: x(replaceIndex), y, width: x(32) - x(replaceIndex), height: 30, rx: 5 }));
    svg.appendChild(svgEl("line", { class: "marker-line", x1: x(replaceIndex), x2: x(replaceIndex), y1: margin.top, y2: h - margin.bottom }));
    svg.appendChild(svgEl("circle", { class: "replace-point", cx: x(replaceIndex), cy: y + 15, r: 7 }));
    noteLink(svg, "normal", "normal: t=1~10", x(6), y + 20);
    noteLink(svg, "warn", "warning: t=11~13", x(12.5), y + 20);
    noteLink(svg, "alt", "alternate tree active: t=14~22", x(18), y + 20);
    noteLink(svg, "repl", "replacement after t=23", x(27), y + 20);
    svg.appendChild(svgEl("line", { class: "axis-line", x1: margin.left, x2: w - margin.right, y1: h - margin.bottom, y2: h - margin.bottom }));
    text(svg, "node detector state timeline", margin.left + 180, h - 6, { class: "axis-label", "text-anchor": "middle" });
  }

  function noteLink(svg, label, note, x, y) {
    const el = svgEl("text", { class: "bar-label note-link", x, y, "text-anchor": "middle", "data-note": note });
    el.textContent = label;
    svg.appendChild(el);
  }

  function ensureNotePopup() {
    let popup = document.getElementById("notePopup");
    if (popup) return popup;
    popup = document.createElement("div");
    popup.id = "notePopup";
    popup.className = "note-popup";
    popup.hidden = true;
    popup.innerHTML = '<div class="note-popup-panel"><button class="note-popup-close" type="button">Close</button><div class="note-popup-body"></div></div>';
    popup.addEventListener("click", (event) => {
      if (event.target === popup || event.target.closest(".note-popup-close")) popup.hidden = true;
    });
    document.body.appendChild(popup);
    return popup;
  }

  document.addEventListener("click", (event) => {
    const target = event.target.closest(".note-link, .panel-note-link");
    if (!target) return;
    const popup = ensureNotePopup();
    popup.querySelector(".note-popup-body").textContent = target.dataset.note || target.textContent;
    popup.hidden = false;
  });

  function drawTreeSize() {
    const svg = document.getElementById("treeSizeChart");
    const w = 472, h = 185;
    const margin = { top: 12, right: 22, bottom: 34, left: 48 };
    const x = scale(1, 32, margin.left, w - margin.right);
    const y = scale(0, 70, h - margin.bottom, margin.top);
    const plotW = w - margin.left - margin.right;
    svg.setAttribute("viewBox", `0 0 ${w} ${h}`);
    for (const t of [0, 20, 40, 60]) {
      svg.appendChild(svgEl("line", { class: "grid-line", x1: margin.left, x2: margin.left + plotW, y1: y(t), y2: y(t) }));
      text(svg, t.toString(), margin.left - 10, y(t) + 4, { class: "tick-text", "text-anchor": "end" });
    }
    svg.appendChild(svgEl("path", { class: "main-line", d: linePath(mainSize.map((v, i) => [x(i + 1), y(v)])) }));
    svg.appendChild(svgEl("path", { class: "alt-line", d: linePath(altSize.map((v, i) => [x(i + 1), y(v)])) }));
    svg.appendChild(svgEl("line", { class: "marker-line", x1: x(replaceIndex), x2: x(replaceIndex), y1: margin.top, y2: h - margin.bottom }));
    svg.appendChild(svgEl("line", { class: "axis-line", x1: margin.left, x2: margin.left + plotW, y1: h - margin.bottom, y2: h - margin.bottom }));
    text(svg, "main / alternate tree size", margin.left + 160, h - 8, { class: "axis-label", "text-anchor": "middle" });
    text(svg, "alternate grows", x(13), y(60), { class: "callout" });
  }

  drawSummary();
  drawAccuracy();
  drawState();
  drawTreeSize();
})();
