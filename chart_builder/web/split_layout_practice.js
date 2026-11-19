(function () {
  const canvas = document.getElementById("layoutCanvas");
  const selectedAreaLabel = document.getElementById("selectedAreaLabel");
  const statusText = document.getElementById("statusText");
  const newAreaNameInput = document.getElementById("newAreaNameInput");
  const layoutNameInput = document.getElementById("layoutNameInput");
  const savedLayoutSelect = document.getElementById("savedLayoutSelect");
  const treeViewer = document.getElementById("treeViewer");
  const gridViewer = document.getElementById("gridViewer");
  const splitVerticalButton = document.getElementById("splitVerticalButton");
  const splitHorizontalButton = document.getElementById("splitHorizontalButton");
  const saveLayoutButton = document.getElementById("saveLayoutButton");
  const loadLayoutButton = document.getElementById("loadLayoutButton");
  const deleteLayoutButton = document.getElementById("deleteLayoutButton");
  const resetButton = document.getElementById("resetButton");

  const minRatio = 0.14;
  let tree = leaf("main");
  let selectedArea = "main";
  let areaCounter = 2;
  let dragState = null;
  let savedLayouts = [];

  function leaf(area) {
    return { type: "leaf", area };
  }

  function split(direction, ratio, first, second) {
    return { type: "split", direction, ratio, first, second };
  }

  function clone(value) {
    return JSON.parse(JSON.stringify(value));
  }

  function layoutsApiUrl(layoutName) {
    const base = window.location.protocol === "http:" || window.location.protocol === "https:"
      ? `${window.location.origin}/api/chart-builder/layouts`
      : "http://127.0.0.1:8766/api/chart-builder/layouts";
    return layoutName ? `${base}/${encodeURIComponent(layoutName)}` : base;
  }

  function areaNames(node = tree, names = []) {
    if (node.type === "leaf") {
      names.push(node.area);
      return names;
    }
    areaNames(node.first, names);
    areaNames(node.second, names);
    return names;
  }

  function nextAreaName() {
    const rawName = newAreaNameInput.value.trim();
    const existing = new Set(areaNames());
    if (rawName && !existing.has(rawName)) {
      newAreaNameInput.value = "";
      return rawName;
    }
    let name = `area_${areaCounter}`;
    while (existing.has(name)) {
      areaCounter += 1;
      name = `area_${areaCounter}`;
    }
    areaCounter += 1;
    return name;
  }

  function replaceSelectedWithSplit(direction) {
    const newName = nextAreaName();
    const newLeaf = leaf(newName);
    const oldLeaf = leaf(selectedArea);
    const first = oldLeaf;
    const second = newLeaf;
    const next = split(direction, 0.5, first, second);
    const replaced = replaceLeaf(tree, selectedArea, next);
    if (!replaced) return;
    tree = replaced;
    selectedArea = newName;
    const label = direction === "vertical" ? "상하" : "좌우";
    setStatus(`${newName} 영역을 만들고 선택 영역을 ${label}로 분할했습니다.`);
    render();
  }

  function replaceLeaf(node, area, replacement) {
    if (node.type === "leaf") {
      return node.area === area ? clone(replacement) : null;
    }
    const first = replaceLeaf(node.first, area, replacement);
    if (first) return { ...node, first };
    const second = replaceLeaf(node.second, area, replacement);
    if (second) return { ...node, second };
    return null;
  }

  function setStatus(message) {
    statusText.textContent = message;
  }

  function render() {
    canvas.innerHTML = "";
    const leaves = [];
    const handles = [];
    collectRects(tree, { x: 0, y: 0, w: 1, h: 1 }, [], leaves, handles);
    leaves.forEach(renderArea);
    handles.forEach(renderHandle);
    selectedAreaLabel.textContent = selectedArea;
    treeViewer.value = JSON.stringify(tree, null, 2);
    gridViewer.value = JSON.stringify(toSemanticGrid(leaves), null, 2);
  }

  function collectRects(node, rect, path, leaves, handles) {
    if (node.type === "leaf") {
      leaves.push({ area: node.area, rect });
      return;
    }

    if (node.direction === "horizontal") {
      const firstW = rect.w * node.ratio;
      const secondW = rect.w - firstW;
      const firstRect = { x: rect.x, y: rect.y, w: firstW, h: rect.h };
      const secondRect = { x: rect.x + firstW, y: rect.y, w: secondW, h: rect.h };
      collectRects(node.first, firstRect, path.concat("first"), leaves, handles);
      collectRects(node.second, secondRect, path.concat("second"), leaves, handles);
      handles.push({
        direction: "horizontal",
        path,
        x: rect.x + firstW,
        y: rect.y,
        w: 0,
        h: rect.h,
        bounds: rect
      });
      return;
    }

    const firstH = rect.h * node.ratio;
    const secondH = rect.h - firstH;
    const firstRect = { x: rect.x, y: rect.y, w: rect.w, h: firstH };
    const secondRect = { x: rect.x, y: rect.y + firstH, w: rect.w, h: secondH };
    collectRects(node.first, firstRect, path.concat("first"), leaves, handles);
    collectRects(node.second, secondRect, path.concat("second"), leaves, handles);
    handles.push({
      direction: "vertical",
      path,
      x: rect.x,
      y: rect.y + firstH,
      w: rect.w,
      h: 0,
      bounds: rect
    });
  }

  function renderArea(item) {
    const el = document.createElement("article");
    const rect = item.rect;
    el.className = `area-box${item.area === selectedArea ? " selected" : ""}`;
    el.style.left = `${rect.x * 100}%`;
    el.style.top = `${rect.y * 100}%`;
    el.style.width = `${rect.w * 100}%`;
    el.style.height = `${rect.h * 100}%`;
    el.innerHTML = [
      '<header class="area-title">',
      `<span class="area-name">${escapeHtml(item.area)}</span>`,
      `<span class="area-size">${Math.round(rect.w * 100)}% x ${Math.round(rect.h * 100)}%</span>`,
      "</header>",
      '<div class="area-body">chart component container</div>'
    ].join("");
    el.addEventListener("click", () => {
      selectedArea = item.area;
      setStatus(`${item.area} 영역을 선택했습니다.`);
      render();
    });
    canvas.appendChild(el);
  }

  function renderHandle(item) {
    const handle = document.createElement("div");
    handle.className = `split-handle ${item.direction}`;
    handle.style.left = `${item.x * 100}%`;
    handle.style.top = `${item.y * 100}%`;
    if (item.direction === "horizontal") {
      handle.style.height = `${item.h * 100}%`;
    } else {
      handle.style.width = `${item.w * 100}%`;
    }
    handle.addEventListener("pointerdown", (event) => startDrag(event, item, handle));
    canvas.appendChild(handle);
  }

  function startDrag(event, item, handle) {
    dragState = {
      path: item.path,
      direction: item.direction,
      bounds: item.bounds,
      handle
    };
    handle.classList.add("dragging");
    handle.setPointerCapture(event.pointerId);
    window.addEventListener("pointermove", onDragMove);
    window.addEventListener("pointerup", onDragEnd, { once: true });
    event.preventDefault();
  }

  function onDragMove(event) {
    if (!dragState) return;
    const canvasRect = canvas.getBoundingClientRect();
    const x = (event.clientX - canvasRect.left) / canvasRect.width;
    const y = (event.clientY - canvasRect.top) / canvasRect.height;
    const bounds = dragState.bounds;
    let ratio;
    if (dragState.direction === "horizontal") {
      ratio = (x - bounds.x) / bounds.w;
    } else {
      ratio = (y - bounds.y) / bounds.h;
    }
    ratio = Math.max(minRatio, Math.min(1 - minRatio, ratio));
    updateNodeRatio(tree, dragState.path, ratio);
    render();
    setStatus(`Split ratio: ${Math.round(ratio * 100)}% / ${Math.round((1 - ratio) * 100)}%`);
  }

  function onDragEnd() {
    dragState = null;
    window.removeEventListener("pointermove", onDragMove);
  }

  function updateNodeRatio(node, path, ratio) {
    if (!path.length) {
      node.ratio = ratio;
      return;
    }
    updateNodeRatio(node[path[0]], path.slice(1), ratio);
  }

  function toSemanticGrid(leaves) {
    return {
      layoutType: "semantic_grid",
      columns: 12,
      rows: 8,
      areas: leaves.map((item) => {
        const rect = item.rect;
        return {
          area: item.area,
          role: item.area === "main" ? "primary_visual" : "secondary_visual",
          x: Math.round(rect.x * 12),
          y: Math.round(rect.y * 8),
          w: Math.max(1, Math.round(rect.w * 12)),
          h: Math.max(1, Math.round(rect.h * 8))
        };
      })
    };
  }

  function reset() {
    tree = leaf("main");
    selectedArea = "main";
    areaCounter = 2;
    newAreaNameInput.value = "side";
    setStatus("main 영역을 선택했습니다.");
    render();
  }

  async function loadSavedLayouts() {
    try {
      const response = await fetch(layoutsApiUrl());
      const result = await response.json();
      if (!response.ok || !result.ok) throw new Error(result.error || "layout load failed");
      savedLayouts = Array.isArray(result.layouts) ? result.layouts : [];
      renderSavedLayoutSelect();
    } catch (error) {
      savedLayouts = JSON.parse(window.localStorage.getItem("chart_builder_saved_layouts") || "[]");
      renderSavedLayoutSelect();
      setStatus(`서버 layout 목록을 불러오지 못해 localStorage를 사용합니다: ${error.message}`);
    }
  }

  function renderSavedLayoutSelect() {
    savedLayoutSelect.innerHTML = "";
    const placeholder = document.createElement("option");
    placeholder.value = "";
    placeholder.textContent = savedLayouts.length ? "저장 layout 선택" : "저장된 layout 없음";
    savedLayoutSelect.appendChild(placeholder);
    savedLayouts.forEach((item) => {
      const option = document.createElement("option");
      option.value = item.name;
      option.textContent = item.name;
      savedLayoutSelect.appendChild(option);
    });
  }

  async function saveCurrentLayout() {
    const name = layoutNameInput.value.trim() || savedLayoutSelect.value;
    if (!name) {
      setStatus("저장할 layout 이름을 입력하세요.");
      return;
    }
    const semanticGrid = JSON.parse(gridViewer.value);
    const layout = {
      ...semanticGrid,
      presetCode: "custom_saved",
      displayName: name,
      sourceSplitTree: clone(tree)
    };
    const body = { name, layout };
    try {
      const response = await fetch(layoutsApiUrl(), {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body)
      });
      const result = await response.json();
      if (!response.ok || !result.ok) throw new Error(result.error || "layout save failed");
      savedLayouts = result.layouts || [];
      window.localStorage.setItem("chart_builder_saved_layouts", JSON.stringify(savedLayouts));
      renderSavedLayoutSelect();
      savedLayoutSelect.value = name;
      layoutNameInput.value = "";
      setStatus(`${name} layout을 저장했습니다. Builder 화면의 Saved 콤보박스에서 선택할 수 있습니다.`);
    } catch (error) {
      savedLayouts = savedLayouts.filter((item) => item.name !== name).concat([body]);
      savedLayouts.sort((a, b) => String(a.name).localeCompare(String(b.name)));
      window.localStorage.setItem("chart_builder_saved_layouts", JSON.stringify(savedLayouts));
      renderSavedLayoutSelect();
      savedLayoutSelect.value = name;
      setStatus(`서버 저장 실패. localStorage에 저장했습니다: ${error.message}`);
    }
  }

  function loadSelectedLayout() {
    const name = savedLayoutSelect.value;
    const saved = savedLayouts.find((item) => item.name === name);
    if (!saved || !saved.layout) {
      setStatus("불러올 layout을 선택하세요.");
      return;
    }
    if (!saved.layout.sourceSplitTree) {
      setStatus("이 layout은 split tree 정보가 없어 Designer에서 재편집할 수 없습니다.");
      return;
    }
    tree = clone(saved.layout.sourceSplitTree);
    selectedArea = firstLeafName(tree) || "main";
    layoutNameInput.value = name;
    setStatus(`${name} layout을 Designer에 불러왔습니다.`);
    render();
  }

  function firstLeafName(node) {
    if (!node) return null;
    if (node.type === "leaf") return node.area;
    return firstLeafName(node.first) || firstLeafName(node.second);
  }

  async function deleteSelectedLayout() {
    const name = savedLayoutSelect.value;
    if (!name) {
      setStatus("삭제할 layout을 선택하세요.");
      return;
    }
    try {
      const response = await fetch(layoutsApiUrl(name), { method: "DELETE" });
      const result = await response.json();
      if (!response.ok || !result.ok) throw new Error(result.error || "layout delete failed");
      savedLayouts = result.layouts || [];
      window.localStorage.setItem("chart_builder_saved_layouts", JSON.stringify(savedLayouts));
      renderSavedLayoutSelect();
      setStatus(`${name} layout을 삭제했습니다.`);
    } catch (error) {
      savedLayouts = savedLayouts.filter((item) => item.name !== name);
      window.localStorage.setItem("chart_builder_saved_layouts", JSON.stringify(savedLayouts));
      renderSavedLayoutSelect();
      setStatus(`서버 삭제 실패. localStorage에서는 삭제했습니다: ${error.message}`);
    }
  }

  function escapeHtml(value) {
    return String(value)
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;");
  }

  splitVerticalButton.addEventListener("click", () => replaceSelectedWithSplit("vertical"));
  splitHorizontalButton.addEventListener("click", () => replaceSelectedWithSplit("horizontal"));
  saveLayoutButton.addEventListener("click", saveCurrentLayout);
  loadLayoutButton.addEventListener("click", loadSelectedLayout);
  deleteLayoutButton.addEventListener("click", deleteSelectedLayout);
  resetButton.addEventListener("click", reset);

  render();
  loadSavedLayouts();
})();
