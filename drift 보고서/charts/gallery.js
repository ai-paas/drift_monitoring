(function () {
  let families = [];
  let chartDescriptions = {};
  let chartMethods = {};
  let methodDescriptions = {};
  const CHART_ASSET_VERSION = "20260623-method-scroll";

  const chartTree = document.getElementById("chartTree");
  const chartFrame = document.getElementById("chartFrame");
  const descriptionPanel = document.getElementById("descriptionPanel");
  const descriptionContent = document.getElementById("descriptionContent");
  const methodPanel = document.getElementById("methodPanel");
  const frameShell = document.getElementById("frameShell");
  const chartFrameStage = document.getElementById("chartFrameStage");
  const chartWorkspace = document.getElementById("chartWorkspace");
  const methodWorkspace = document.getElementById("methodWorkspace");
  const selectedFamily = document.getElementById("selectedFamily");
  const selectedTitle = document.getElementById("selectedTitle");
  const mainChartTab = document.getElementById("mainChartTab");
  const mainMethodTab = document.getElementById("mainMethodTab");
  const chartViewTab = document.getElementById("chartViewTab");
  const chartDescriptionTab = document.getElementById("chartDescriptionTab");
  const methodButton = document.getElementById("methodButton");
  const chartListButton = document.getElementById("chartListButton");
  const leftHandle = document.getElementById("leftHandle");
  const rightHandle = document.getElementById("rightHandle");
  const methodDialog = document.getElementById("methodDialog");
  const methodDialogChart = document.getElementById("methodDialogChart");
  const methodList = document.getElementById("methodList");
  const methodCloseButton = document.getElementById("methodCloseButton");
  const chartDialog = document.getElementById("chartDialog");
  const chartDialogMethod = document.getElementById("chartDialogMethod");
  const chartList = document.getElementById("chartList");
  const chartCloseButton = document.getElementById("chartCloseButton");
  const chartSelectorButton = document.getElementById("chartSelectorButton");
  const chartSelectorDialog = document.getElementById("chartSelectorDialog");
  const chartSelectorCloseButton = document.getElementById("chartSelectorCloseButton");
  const chartExampleSelect = document.getElementById("chartExampleSelect");
  const chartSelectorInput = document.getElementById("chartSelectorInput");
  const chartSelectorRequestButton = document.getElementById("chartSelectorRequestButton");
  const chartSelectorStatus = document.getElementById("chartSelectorStatus");
  const chartSelectorResult = document.getElementById("chartSelectorResult");
  const chartExplainButton = document.getElementById("chartExplainButton");
  const chartExplainDialog = document.getElementById("chartExplainDialog");
  const chartExplainCloseButton = document.getElementById("chartExplainCloseButton");
  const chartExplainChartId = document.getElementById("chartExplainChartId");
  const chartExplainMessages = document.getElementById("chartExplainMessages");
  const chartExplainInput = document.getElementById("chartExplainInput");
  const chartExplainRequestButton = document.getElementById("chartExplainRequestButton");
  const chartExplainStatus = document.getElementById("chartExplainStatus");
  const searchInput = document.getElementById("searchInput");
  const totalCount = document.getElementById("totalCount");
  const methodTree = document.getElementById("methodTree");
  const methodSearchInput = document.getElementById("methodSearchInput");
  const methodCount = document.getElementById("methodCount");
  let activeButton = null;
  let activeMethodButton = null;
  let activeChart = null;
  let activeMethod = null;
  let activeMainMode = "chart";
  let activeChartMode = "chart";
  let chartExplainMessagesByChart = {};

  function chartIdToDescriptionFile(chartId) {
    return `./descriptions/${chartId.toLowerCase().replaceAll("-", "_")}_desc.html`;
  }

  function chartAssetUrl(path) {
    const separator = path.includes("?") ? "&" : "?";
    return `./${path}${separator}v=${encodeURIComponent(CHART_ASSET_VERSION)}`;
  }

  function setMainMode(mode) {
    activeMainMode = mode;
    const isChart = mode === "chart";
    mainChartTab.classList.toggle("active", isChart);
    mainMethodTab.classList.toggle("active", !isChart);
    mainChartTab.setAttribute("aria-selected", isChart ? "true" : "false");
    mainMethodTab.setAttribute("aria-selected", isChart ? "false" : "true");
    chartWorkspace.hidden = !isChart;
    methodWorkspace.hidden = isChart;
    updateHeader();
    resizeFrame();
  }

  function updateHeader() {
    if (activeMainMode === "method") {
      selectedFamily.textContent = "탐지 방법";
      selectedTitle.textContent = activeMethod || "탐지 방법 설명";
      return;
    }
    if (activeChart) {
      selectedFamily.textContent = activeChart.family;
      selectedTitle.textContent = `${activeChart.chart[0]} - ${activeChart.chart[1]}`;
    }
  }

  function setChartMode(mode) {
    activeChartMode = mode;
    const isChart = mode === "chart";
    chartViewTab.classList.toggle("active", isChart);
    chartDescriptionTab.classList.toggle("active", !isChart);
    chartViewTab.setAttribute("aria-selected", isChart ? "true" : "false");
    chartDescriptionTab.setAttribute("aria-selected", isChart ? "false" : "true");
    chartFrame.hidden = !isChart;
    descriptionPanel.hidden = isChart;
    frameShell.classList.toggle("description-mode", !isChart);
    resizeFrame();
  }

  function selectChart(family, chart, button = null) {
    if (activeButton) activeButton.classList.remove("active");
    activeButton = button;
    if (activeButton) activeButton.classList.add("active");
    activeChart = { family, chart };
    chartFrame.src = chartAssetUrl(chart[2]);
    loadDescription(chart[0]);
    resetMethodPanel(chart[0]);
    updateHeader();
  }

  function loadDescription(chartId) {
    descriptionContent.innerHTML = chartDescriptions[chartId] || "<p>설명 문서를 불러오지 못했습니다.</p>";
    descriptionPanel.scrollTop = 0;
  }

  function escapeHtml(value) {
    return String(value)
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#039;");
  }

  function findChartById(chartId) {
    for (const [family, charts] of families) {
      const chart = charts.find((item) => item[0] === chartId);
      if (chart) return { family, chart };
    }
    return null;
  }

  function findChartButton(chartId) {
    return chartTree.querySelector(`.chart-button[data-chart-id="${chartId}"]`);
  }

  function resetMethodPanel(chartId) {
    activeMethod = null;
    activeMethodButton = null;
    methodPanel.innerHTML = [
      `<p class="chart-id">${escapeHtml(chartId)}</p>`,
      "<h1>탐지 방법 설명</h1>",
      "<p>오른쪽 <strong>탐지 방법</strong> 전체 목록에서 항목을 선택하면 이 탭에 상세 설명이 표시됩니다.</p>"
    ].join("");
  }

  function openMethodDialog() {
    if (!activeChart) return;
    const chartId = activeChart.chart[0];
    const methods = chartMethods[chartId] || [];
    methodDialogChart.textContent = chartId;
    if (methods.length) {
      methodList.innerHTML = [
        `<p class="method-count">${methods.length}개 탐지 방법이 이 차트에 연결됩니다.</p>`,
        ...methods.map((item) => {
          const method = escapeHtml(item.method);
          const description = escapeHtml(item.description);
          return `<button class="method-item" type="button" data-method="${method}"><span class="method-name">${method}</span><span class="method-desc">${description}</span></button>`;
        })
      ].join("");
    } else {
      methodList.innerHTML = '<p class="empty-methods">연결된 탐지 방법이 없습니다.</p>';
    }
    methodDialog.hidden = false;
    methodCloseButton.focus();
  }

  function closeMethodDialog() {
    if (methodDialog.hidden) return;
    methodDialog.hidden = true;
    methodButton.focus();
  }

  function chartsForMethod(method) {
    return Object.entries(chartMethods)
      .filter(([, methods]) => methods.some((item) => item.method === method))
      .map(([chartId]) => findChartById(chartId))
      .filter(Boolean);
  }

  function openChartDialog() {
    if (!activeMethod) {
      chartDialogMethod.textContent = "탐지 방법";
      chartList.innerHTML = '<p class="empty-methods">먼저 오른쪽 탐지 방법 목록에서 항목을 선택하세요.</p>';
    } else {
      const charts = chartsForMethod(activeMethod);
      chartDialogMethod.textContent = activeMethod;
      if (charts.length) {
        chartList.innerHTML = [
          `<p class="method-count">${charts.length}개 차트가 이 탐지 방법에 연결됩니다.</p>`,
          ...charts.map(({ family, chart }) => {
            const chartId = escapeHtml(chart[0]);
            const title = escapeHtml(chart[1]);
            return `<button class="method-item chart-dialog-item" type="button" data-chart-id="${chartId}"><span class="method-name">${chartId} - ${title}</span><span class="method-desc">${escapeHtml(family)}</span></button>`;
          })
        ].join("");
      } else {
        chartList.innerHTML = '<p class="empty-methods">연결된 차트가 없습니다.</p>';
      }
    }
    chartDialog.hidden = false;
    chartCloseButton.focus();
  }

  function closeChartDialog() {
    if (chartDialog.hidden) return;
    chartDialog.hidden = true;
    chartListButton.focus();
  }

  function selectChartById(chartId) {
    const found = findChartById(chartId);
    if (!found) return;
    selectChart(found.family, found.chart, findChartButton(chartId));
    setMainMode("chart");
    setChartMode("chart");
    closeChartDialog();
  }

  function chartSelectorApiUrl() {
    if (window.location.protocol === "http:" || window.location.protocol === "https:") {
      return `${window.location.origin}/api/select-chart`;
    }
    return "http://127.0.0.1:8765/api/select-chart";
  }

  function chartExplainApiUrl() {
    if (window.location.protocol === "http:" || window.location.protocol === "https:") {
      return `${window.location.origin}/api/explain-chart`;
    }
    return "http://127.0.0.1:8765/api/explain-chart";
  }

  function galleryDataApiUrl() {
    if (window.location.protocol === "http:" || window.location.protocol === "https:") {
      return `${window.location.origin}/api/gallery-data`;
    }
    return "http://127.0.0.1:8765/api/gallery-data";
  }

  function buildFamilies(charts) {
    const groups = new Map();
    charts.forEach((item) => {
      const family = item.family || "기타 계열";
      if (!groups.has(family)) groups.set(family, []);
      groups.get(family).push([
        item.chartId,
        item.title || item.chartId,
        item.htmlPath || `${item.chartId.toLowerCase().replaceAll("-", "_")}.html`
      ]);
      chartDescriptions[item.chartId] = item.descriptionHtml || "";
    });
    return Array.from(groups.entries()).map(([family, chartList]) => [family, chartList]);
  }

  async function loadGalleryData() {
    chartTree.innerHTML = '<p class="empty-methods">DB에서 차트 목록을 불러오는 중입니다.</p>';
    methodTree.innerHTML = '<p class="empty-methods">DB에서 탐지 방법을 불러오는 중입니다.</p>';
    totalCount.textContent = "0";
    methodCount.textContent = "0";
    try {
      const response = await fetch(galleryDataApiUrl(), { headers: { "Accept": "application/json" } });
      const payload = await response.json();
      if (!response.ok || !payload.ok) {
        throw new Error(payload.error || "갤러리 DB 데이터를 불러오지 못했습니다.");
      }
      const data = payload.data || {};
      chartDescriptions = {};
      families = buildFamilies(Array.isArray(data.charts) ? data.charts : []);
      chartMethods = data.chartMethods || {};
      methodDescriptions = data.methodDescriptions || {};
      renderTree();
      renderMethodTree();
      applyInitialHash();
      updateCollapseHandles();
      resizeFrame();
    } catch (error) {
      const message = escapeHtml(error.message || String(error));
      chartTree.innerHTML = `<p class="empty-methods">DB 연결 실패: ${message}</p>`;
      methodTree.innerHTML = '<p class="empty-methods">서버와 PostgreSQL 상태를 확인하세요.</p>';
      descriptionContent.innerHTML = [
        '<p class="chart-id">DB 연결 실패</p>',
        '<h1>갤러리 데이터를 불러오지 못했습니다.</h1>',
        `<p>${message}</p>`,
        '<p>서버 실행 전 PostgreSQL DB를 만들고 import를 완료해야 합니다.</p>'
      ].join("");
      setChartMode("description");
      updateCollapseHandles();
    }
  }

  function openChartSelectorDialog() {
    chartSelectorDialog.hidden = false;
    chartSelectorInput.focus();
  }

  function closeChartSelectorDialog() {
    if (chartSelectorDialog.hidden) return;
    chartSelectorDialog.hidden = true;
    chartSelectorButton.focus();
  }

  function currentChartId() {
    return activeChart ? activeChart.chart[0] : "";
  }

  function currentChartTitle() {
    return activeChart ? activeChart.chart[1] : "";
  }

  function currentExplainMessages() {
    const chartId = currentChartId();
    if (!chartId) return [];
    if (!chartExplainMessagesByChart[chartId]) {
      chartExplainMessagesByChart[chartId] = [];
    }
    return chartExplainMessagesByChart[chartId];
  }

  function renderExplainMessages() {
    const messages = currentExplainMessages();
    if (!messages.length) {
      chartExplainMessages.innerHTML = [
        '<div class="explain-empty">',
        '<h3>현재 차트에 대해 질문하세요.</h3>',
        '<p>차트 화면, 설명 문서, 연결된 탐지 방법을 기준으로 Codex가 답변합니다.</p>',
        '</div>'
      ].join("");
      return;
    }
    chartExplainMessages.innerHTML = messages.map((message) => [
      `<article class="explain-message ${message.role === "user" ? "user" : "assistant"}">`,
      `<p class="explain-role">${message.role === "user" ? "질문" : "답변"}</p>`,
      `<div>${escapeHtml(message.content).replaceAll("\n", "<br>")}</div>`,
      "</article>"
    ].join("")).join("");
    chartExplainMessages.scrollTop = chartExplainMessages.scrollHeight;
  }

  function openChartExplainDialog() {
    if (!activeChart) return;
    chartExplainChartId.textContent = `${currentChartId()} / ${currentChartTitle()}`;
    renderExplainMessages();
    chartExplainDialog.hidden = false;
    chartExplainInput.focus();
  }

  function closeChartExplainDialog() {
    if (chartExplainDialog.hidden) return;
    chartExplainDialog.hidden = true;
    chartExplainButton.focus();
  }

  async function requestChartExplanation() {
    const chartId = currentChartId();
    const question = chartExplainInput.value.trim();
    if (!chartId) return;
    if (!question) {
      chartExplainStatus.textContent = "질문을 입력하세요.";
      chartExplainInput.focus();
      return;
    }
    const messages = currentExplainMessages();
    messages.push({ role: "user", content: question });
    chartExplainInput.value = "";
    renderExplainMessages();
    chartExplainRequestButton.disabled = true;
    chartExplainStatus.textContent = "Codex CLI에 현재 차트 설명을 질문 중입니다.";
    try {
      const response = await fetch(chartExplainApiUrl(), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          chartId,
          question,
          history: messages.slice(-8, -1)
        })
      });
      const payload = await response.json();
      if (!response.ok || !payload.ok) {
        throw new Error(payload.error || "차트 설명 요청에 실패했습니다.");
      }
      messages.push({ role: "assistant", content: payload.answer || "답변을 받지 못했습니다." });
      chartExplainStatus.textContent = "답변을 받았습니다.";
    } catch (error) {
      messages.push({ role: "assistant", content: `요청 실패: ${error.message || String(error)}` });
      chartExplainStatus.textContent = "요청 실패";
    } finally {
      chartExplainRequestButton.disabled = false;
      renderExplainMessages();
    }
  }

  function renderChartSelectorResult(result) {
    const chartId = result.chartId || "";
    const alternatives = Array.isArray(result.alternatives) ? result.alternatives : [];
    chartSelectorResult.hidden = false;
    chartSelectorResult.innerHTML = [
      `<h3>${escapeHtml(chartId)} - ${escapeHtml(result.chartTitle || "추천 차트")}</h3>`,
      `<p><strong>계열</strong> ${escapeHtml(result.family || "")}</p>`,
      `<p>${escapeHtml(result.reason || "")}</p>`,
      alternatives.length
        ? `<p><strong>대안</strong> ${alternatives.map((item) => `${escapeHtml(item.chartId || "")}: ${escapeHtml(item.reason || "")}`).join(" / ")}</p>`
        : "",
      chartId ? `<button class="method-button selected-chart-link" type="button" data-selected-chart-id="${escapeHtml(chartId)}">이 차트 열기</button>` : ""
    ].join("");
  }

  async function requestChartSelection() {
    const request = chartSelectorInput.value.trim();
    if (!request) {
      chartSelectorStatus.textContent = "요청 내용을 입력하세요.";
      chartSelectorInput.focus();
      return;
    }
    chartSelectorRequestButton.disabled = true;
    chartSelectorStatus.textContent = "Codex CLI에 요청 중입니다. 잠시 기다려 주세요.";
    chartSelectorResult.hidden = true;
    try {
      const response = await fetch(chartSelectorApiUrl(), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ request })
      });
      const payload = await response.json();
      if (!response.ok || !payload.ok) {
        throw new Error(payload.error || "차트 추천 요청에 실패했습니다.");
      }
      renderChartSelectorResult(payload.result || {});
      chartSelectorStatus.textContent = "추천 결과를 받았습니다.";
    } catch (error) {
      chartSelectorResult.hidden = false;
      chartSelectorResult.innerHTML = [
        "<h3>요청 실패</h3>",
        `<p>${escapeHtml(error.message || String(error))}</p>`,
        "<p>서버를 실행한 뒤 다시 요청하세요: python charts\\chart_selector_server.py</p>"
      ].join("");
      chartSelectorStatus.textContent = "요청 실패";
    } finally {
      chartSelectorRequestButton.disabled = false;
    }
  }

  function selectMethod(method, button = null) {
    const selected = methodDescriptions[method];
    activeMethod = method;
    if (activeMethodButton) activeMethodButton.classList.remove("active");
    if (button) {
      activeMethodButton = button;
      activeMethodButton.classList.add("active");
    }
    methodPanel.innerHTML = selected
      ? selected.html
      : `<p class="chart-id">탐지 방법</p><h1>${escapeHtml(method)}</h1><p>이 탐지 방법의 상세 설명을 찾지 못했습니다.</p>`;
    closeMethodDialog();
    setMainMode("method");
    updateHeader();
    methodPanel.scrollTop = 0;
  }

  function methodFamilyName(method) {
    const parts = method.split("/").map((part) => part.trim());
    return parts.length > 1 ? parts.slice(0, -1).join(" / ") : "기타";
  }

  function allMethods() {
    const methodMap = new Map();
    Object.values(chartMethods).forEach((methods) => {
      methods.forEach((item) => {
        if (!methodMap.has(item.method)) {
          methodMap.set(item.method, item);
        }
      });
    });
    return Array.from(methodMap.values()).sort((a, b) => a.method.localeCompare(b.method));
  }

  function renderMethodTree() {
    const methods = allMethods();
    const query = methodSearchInput.value.trim().toLowerCase();
    const groups = new Map();
    methods.forEach((item) => {
      const haystack = `${item.method} ${item.description}`.toLowerCase();
      if (query && !haystack.includes(query)) return;
      const family = methodFamilyName(item.method);
      if (!groups.has(family)) groups.set(family, []);
      groups.get(family).push(item);
    });

    methodTree.innerHTML = "";
    let visible = 0;
    groups.forEach((items, family) => {
      visible += items.length;
      const details = document.createElement("details");
      details.className = "family";
      details.open = false;

      const summary = document.createElement("summary");
      summary.innerHTML = `<span class="family-name">${escapeHtml(family)}</span><span class="family-count">${items.length}</span>`;
      details.appendChild(summary);

      const list = document.createElement("div");
      list.className = "method-tree-list";
      items.forEach((item) => {
        const button = document.createElement("button");
        button.type = "button";
        button.className = "method-tree-button";
        button.dataset.method = item.method;
        button.innerHTML = `<span class="method-tree-name">${escapeHtml(item.method)}</span><span class="method-tree-desc">${escapeHtml(item.description)}</span>`;
        button.addEventListener("click", () => selectMethod(item.method, button));
        list.appendChild(button);
      });
      details.appendChild(list);
      methodTree.appendChild(details);
    });
    methodCount.textContent = visible.toString();

    if (!visible) {
      methodTree.innerHTML = '<p class="empty-methods">연결된 탐지 방법이 없습니다.</p>';
    }
  }

  function renderTree() {
    chartTree.innerHTML = "";
    const total = families.reduce((sum, family) => sum + family[1].length, 0);
    totalCount.textContent = total.toString();
    families.forEach(([family, charts]) => {
      const details = document.createElement("details");
      details.className = "family";
      details.open = false;
      details.dataset.family = family.toLowerCase();

      const summary = document.createElement("summary");
      summary.innerHTML = `<span class="family-name">${family}</span><span class="family-count">${charts.length}</span>`;
      details.appendChild(summary);

      const list = document.createElement("div");
      list.className = "chart-list";
      charts.forEach((chart) => {
        const button = document.createElement("button");
        button.type = "button";
        button.className = "chart-button";
        button.dataset.chartId = chart[0];
        button.dataset.search = `${family} ${chart[0]} ${chart[1]}`.toLowerCase();
        button.innerHTML = `<span class="chart-id">${chart[0]}</span><span class="chart-title">${chart[1]}</span>`;
        button.addEventListener("click", () => selectChart(family, chart, button));
        list.appendChild(button);
      });
      details.appendChild(list);
      chartTree.appendChild(details);
    });
    const first = chartTree.querySelector(".chart-button");
    if (first) first.click();
  }

  function filterTree() {
    const query = searchInput.value.trim().toLowerCase();
    let visible = 0;
    chartTree.querySelectorAll(".family").forEach((familyEl) => {
      let familyVisible = false;
      familyEl.querySelectorAll(".chart-button").forEach((button) => {
        const match = !query || button.dataset.search.includes(query);
        button.hidden = !match;
        if (match) {
          visible += 1;
          familyVisible = true;
        }
      });
      familyEl.hidden = !familyVisible;
      if (query && familyVisible) familyEl.open = true;
    });
    totalCount.textContent = visible.toString();
  }

  function resizeFrame() {
    if (activeMainMode !== "chart" || activeChartMode !== "chart") {
      chartFrameStage.style.width = "1200px";
      chartFrameStage.style.height = "820px";
      chartFrameStage.style.left = "0";
      chartFrame.style.transform = "scale(1)";
      frameShell.style.overflow = "hidden";
      return;
    }
    const availableW = frameShell.clientWidth;
    const expandedWorkAreaW = Math.max(availableW, window.innerWidth - 92);
    const safeScale = Math.max(0.52, Math.min(1.5, expandedWorkAreaW / 1200));
    const scaledW = 1200 * safeScale;
    const scaledH = 820 * safeScale;
    const offsetX = Math.max(0, (availableW - scaledW) / 2);
    chartFrameStage.style.width = `${scaledW}px`;
    chartFrameStage.style.height = `${scaledH}px`;
    chartFrameStage.style.left = `${offsetX}px`;
    chartFrame.style.transform = `scale(${safeScale})`;
    frameShell.style.overflow = "auto";
  }

  function updateCollapseHandles() {
    const leftCollapsed = document.body.classList.contains("left-collapsed");
    const rightCollapsed = document.body.classList.contains("right-collapsed");
    leftHandle.textContent = leftCollapsed ? "›" : "‹";
    rightHandle.textContent = rightCollapsed ? "‹" : "›";
    leftHandle.setAttribute("aria-label", leftCollapsed ? "차트 목록 펼치기" : "차트 목록 접기");
    rightHandle.setAttribute("aria-label", rightCollapsed ? "탐지 방법 목록 펼치기" : "탐지 방법 목록 접기");
    leftHandle.setAttribute("aria-expanded", leftCollapsed ? "false" : "true");
    rightHandle.setAttribute("aria-expanded", rightCollapsed ? "false" : "true");
    resizeFrame();
  }

  function applyInitialHash() {
    if (window.location.hash.startsWith("#method=")) {
      selectMethod(decodeURIComponent(window.location.hash.slice("#method=".length)));
    } else if (window.location.hash === "#description") {
      setMainMode("chart");
      setChartMode("description");
    } else if (window.location.hash === "#method") {
      setMainMode("method");
    } else if (window.location.hash === "#methods") {
      openMethodDialog();
    } else if (window.location.hash === "#collapsed") {
      document.body.classList.add("left-collapsed", "right-collapsed");
      updateCollapseHandles();
    }
  }

  searchInput.addEventListener("input", filterTree);
  methodSearchInput.addEventListener("input", () => {
    renderMethodTree();
  });
  mainChartTab.addEventListener("click", () => setMainMode("chart"));
  mainMethodTab.addEventListener("click", () => setMainMode("method"));
  chartViewTab.addEventListener("click", () => setChartMode("chart"));
  chartDescriptionTab.addEventListener("click", () => setChartMode("description"));
  methodButton.addEventListener("click", openMethodDialog);
  chartListButton.addEventListener("click", openChartDialog);
  chartSelectorButton.addEventListener("click", openChartSelectorDialog);
  chartSelectorCloseButton.addEventListener("click", closeChartSelectorDialog);
  chartExampleSelect.addEventListener("change", () => {
    if (chartExampleSelect.value) {
      chartSelectorInput.value = chartExampleSelect.value;
      chartSelectorInput.focus();
    }
  });
  chartSelectorRequestButton.addEventListener("click", requestChartSelection);
  chartExplainButton.addEventListener("click", openChartExplainDialog);
  chartExplainCloseButton.addEventListener("click", closeChartExplainDialog);
  chartExplainRequestButton.addEventListener("click", requestChartExplanation);
  chartExplainInput.addEventListener("keydown", (event) => {
    if ((event.ctrlKey || event.metaKey) && event.key === "Enter") {
      requestChartExplanation();
    }
  });
  chartSelectorResult.addEventListener("click", (event) => {
    const button = event.target instanceof HTMLElement ? event.target.closest("[data-selected-chart-id]") : null;
    if (button instanceof HTMLElement && button.dataset.selectedChartId) {
      selectChartById(button.dataset.selectedChartId);
      closeChartSelectorDialog();
    }
  });
  leftHandle.addEventListener("click", () => {
    document.body.classList.toggle("left-collapsed");
    updateCollapseHandles();
  });
  rightHandle.addEventListener("click", () => {
    document.body.classList.toggle("right-collapsed");
    updateCollapseHandles();
  });
  methodCloseButton.addEventListener("click", closeMethodDialog);
  chartCloseButton.addEventListener("click", closeChartDialog);
  methodDialog.addEventListener("click", (event) => {
    if (event.target instanceof HTMLElement && event.target.dataset.closeMethods !== undefined) {
      closeMethodDialog();
    }
    const button = event.target instanceof HTMLElement ? event.target.closest(".method-item") : null;
    if (button instanceof HTMLElement && button.dataset.method) {
      selectMethod(button.dataset.method);
    }
  });
  chartDialog.addEventListener("click", (event) => {
    if (event.target instanceof HTMLElement && event.target.dataset.closeCharts !== undefined) {
      closeChartDialog();
    }
    const button = event.target instanceof HTMLElement ? event.target.closest(".chart-dialog-item") : null;
    if (button instanceof HTMLElement && button.dataset.chartId) {
      selectChartById(button.dataset.chartId);
    }
  });
  chartSelectorDialog.addEventListener("click", (event) => {
    if (event.target instanceof HTMLElement && event.target.dataset.closeChartSelector !== undefined) {
      closeChartSelectorDialog();
    }
  });
  chartExplainDialog.addEventListener("click", (event) => {
    if (event.target instanceof HTMLElement && event.target.dataset.closeChartExplain !== undefined) {
      closeChartExplainDialog();
    }
  });
  window.addEventListener("keydown", (event) => {
    if (event.key === "Escape") {
      closeMethodDialog();
      closeChartDialog();
      closeChartSelectorDialog();
      closeChartExplainDialog();
    }
  });
  window.addEventListener("resize", resizeFrame);
  chartFrame.addEventListener("load", resizeFrame);

  loadGalleryData();
})();
