(function () {
  const families = [
    ["EDF 계열", [
      ["CHART-EDF-001", "KS ECDF overlay", "chart_edf_001.html"],
      ["CHART-EDF-002", "Anderson-Darling tail ECDF", "chart_edf_002.html"],
      ["CHART-EDF-003", "Cramer-von Mises CDF distance", "chart_edf_003.html"],
      ["CHART-EDF-004", "Kuiper CDF directional deviation", "chart_edf_004.html"]
    ]],
    ["Rank 계열", [["CHART-RANK-001", "Rank / box violin comparison", "chart_rank_001.html"]]],
    ["Distance 계열", [["CHART-DIST-001", "Wasserstein distance trend", "chart_dist_001.html"]]],
    ["Probability 계열", [
      ["CHART-PROB-001", "Probability score distribution", "chart_prob_001.html"],
      ["CHART-PROB-002", "Calibration probability drift", "chart_prob_002.html"],
      ["CHART-PROB-003", "Probability class shift", "chart_prob_003.html"]
    ]],
    ["Histogram 계열", [["CHART-HIST-001", "Histogram bin distribution", "chart_hist_001.html"]]],
    ["Category 계열", [
      ["CHART-CAT-001", "Categorical proportion bar", "chart_cat_001.html"],
      ["CHART-CAT-002", "Category chi-square contribution", "chart_cat_002.html"],
      ["CHART-CAT-003", "High-cardinality category drift", "chart_cat_003.html"],
      ["CHART-CAT-004", "Fisher exact contingency", "chart_cat_004.html"]
    ]],
    ["PSI 계열", [["CHART-PSI-001", "Population Stability Index", "chart_psi_001.html"]]],
    ["Mean 계열", [["CHART-MEAN-001", "Mean shift confidence interval", "chart_mean_001.html"]]],
    ["Variance 계열", [["CHART-VAR-001", "Variance ratio drift", "chart_var_001.html"]]],
    ["Distribution Shape 계열", [["CHART-DISTSHAPE-001", "Skewness / kurtosis shape drift", "chart_distshape_001.html"]]],
    ["Multivariate 계열", [
      ["CHART-MV-001", "Energy distance", "chart_mv_001.html"],
      ["CHART-MV-002", "Kernel MMD", "chart_mv_002.html"],
      ["CHART-MV-003", "LSDD density difference", "chart_mv_003.html"],
      ["CHART-MV-004", "PCA / covariance drift", "chart_mv_004.html"],
      ["CHART-MV-005", "Multi-feature contribution", "chart_mv_005.html"]
    ]],
    ["Stream 계열", [
      ["CHART-STREAM-001", "ADWIN window adaptation", "chart_stream_001.html"],
      ["CHART-STREAM-002", "Page-Hinkley cumulative score", "chart_stream_002.html"],
      ["CHART-STREAM-003", "KSWIN sliding window", "chart_stream_003.html"],
      ["CHART-STREAM-004", "HDDM-style streaming state", "chart_stream_004.html"],
      ["CHART-STREAM-005", "Stream detector comparison", "chart_stream_005.html"]
    ]],
    ["Control Chart 계열", [
      ["CHART-CTRL-001", "CUSUM control chart", "chart_ctrl_001.html"],
      ["CHART-CTRL-002", "EWMA / GMA control chart", "chart_ctrl_002.html"],
      ["CHART-CTRL-003", "Control limit timeline", "chart_ctrl_003.html"]
    ]],
    ["BOCD 계열", [["CHART-BOCD-001", "Bayesian online change point", "chart_bocd_001.html"]]],
    ["Error Rate Detector 계열", [
      ["CHART-ERR-001", "DDM error rate", "chart_err_001.html"],
      ["CHART-ERR-002", "RDDM retained warning window", "chart_err_002.html"],
      ["CHART-ERR-003", "EDDM distance between errors", "chart_err_003.html"],
      ["CHART-ERR-004", "ECDD weighted statistic", "chart_err_004.html"],
      ["CHART-ERR-005", "HDDM Hoeffding bound", "chart_err_005.html"],
      ["CHART-ERR-006", "STEPD accuracy window", "chart_err_006.html"]
    ]],
    ["Anomaly / Novelty 계열", [["CHART-ANOM-001", "OCDD novelty detector", "chart_anom_001.html"]]],
    ["Representation Drift 계열", [
      ["CHART-REP-001", "Feature map drift", "chart_rep_001.html"],
      ["CHART-REP-002", "Autoencoder representation drift", "chart_rep_002.html"],
      ["CHART-REP-003", "Graph embedding drift", "chart_rep_003.html"]
    ]],
    ["Text Drift 계열", [
      ["CHART-TEXT-001", "LLM query semantic drift", "chart_text_001.html"],
      ["CHART-TEXT-002", "Text domain classifier drift", "chart_text_002.html"]
    ]],
    ["Classifier-based Drift 계열", [["CHART-CLS-001", "Domain classifier embedding drift", "chart_cls_001.html"]]],
    ["Model Uncertainty 계열", [["CHART-UNC-001", "Model uncertainty drift", "chart_unc_001.html"]]],
    ["Explainability Drift 계열", [
      ["CHART-EXPL-001", "SHAP drift", "chart_expl_001.html"],
      ["CHART-EXPL-002", "Tree feature drift", "chart_expl_002.html"]
    ]],
    ["Adaptive Model 계열", [
      ["CHART-ADAPT-001", "HAT adaptive replacement", "chart_adapt_001.html"],
      ["CHART-ADAPT-002", "Retraining workflow", "chart_adapt_002.html"]
    ]],
    ["Annotation 계열", [
      ["CHART-ANNOT-001", "Directional one-sided annotation", "chart_annot_001.html"],
      ["CHART-ANNOT-002", "Approximation projection annotation", "chart_annot_002.html"]
    ]],
    ["Generic / Fallback 계열", [["CHART-GEN-001", "Generic drift fallback", "chart_gen_001.html"]]]
  ];

  const chartTree = document.getElementById("chartTree");
  const chartFrame = document.getElementById("chartFrame");
  const descriptionPanel = document.getElementById("descriptionPanel");
  const methodPanel = document.getElementById("methodPanel");
  const frameShell = document.getElementById("frameShell");
  const chartWorkspace = document.getElementById("chartWorkspace");
  const methodWorkspace = document.getElementById("methodWorkspace");
  const selectedFamily = document.getElementById("selectedFamily");
  const selectedTitle = document.getElementById("selectedTitle");
  const mainChartTab = document.getElementById("mainChartTab");
  const mainMethodTab = document.getElementById("mainMethodTab");
  const chartViewTab = document.getElementById("chartViewTab");
  const chartDescriptionTab = document.getElementById("chartDescriptionTab");
  const methodButton = document.getElementById("methodButton");
  const leftHandle = document.getElementById("leftHandle");
  const rightHandle = document.getElementById("rightHandle");
  const methodDialog = document.getElementById("methodDialog");
  const methodDialogChart = document.getElementById("methodDialogChart");
  const methodList = document.getElementById("methodList");
  const methodCloseButton = document.getElementById("methodCloseButton");
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

  function chartIdToDescriptionFile(chartId) {
    return `./descriptions/${chartId.toLowerCase().replaceAll("-", "_")}_desc.html`;
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

  function selectChart(family, chart, button) {
    if (activeButton) activeButton.classList.remove("active");
    activeButton = button;
    activeButton.classList.add("active");
    activeChart = { family, chart };
    chartFrame.src = `./${chart[2]}`;
    loadDescription(chart[0]);
    resetMethodPanel(chart[0]);
    updateHeader();
  }

  function loadDescription(chartId) {
    const descriptions = window.CHART_DESCRIPTIONS || {};
    descriptionPanel.innerHTML = descriptions[chartId] || "<p>설명 문서를 불러오지 못했습니다.</p>";
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
    const methods = (window.CHART_METHODS || {})[chartId] || [];
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

  function selectMethod(method, button = null) {
    const descriptions = window.METHOD_DESCRIPTIONS || {};
    const selected = descriptions[method];
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
    Object.values(window.CHART_METHODS || {}).forEach((methods) => {
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
      chartFrame.style.transform = "scale(1)";
      frameShell.style.overflow = "hidden";
      return;
    }
    const availableW = frameShell.clientWidth;
    const availableH = frameShell.clientHeight;
    const scale = Math.min(availableW / 1200, availableH / 820);
    const safeScale = Math.max(0.52, Math.min(1, scale));
    chartFrame.style.transform = `scale(${safeScale})`;
    frameShell.style.overflow = safeScale < 0.99 ? "hidden" : "auto";
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

  searchInput.addEventListener("input", filterTree);
  methodSearchInput.addEventListener("input", () => {
    renderMethodTree();
  });
  mainChartTab.addEventListener("click", () => setMainMode("chart"));
  mainMethodTab.addEventListener("click", () => setMainMode("method"));
  chartViewTab.addEventListener("click", () => setChartMode("chart"));
  chartDescriptionTab.addEventListener("click", () => setChartMode("description"));
  methodButton.addEventListener("click", openMethodDialog);
  leftHandle.addEventListener("click", () => {
    document.body.classList.toggle("left-collapsed");
    updateCollapseHandles();
  });
  rightHandle.addEventListener("click", () => {
    document.body.classList.toggle("right-collapsed");
    updateCollapseHandles();
  });
  methodCloseButton.addEventListener("click", closeMethodDialog);
  methodDialog.addEventListener("click", (event) => {
    if (event.target instanceof HTMLElement && event.target.dataset.closeMethods !== undefined) {
      closeMethodDialog();
    }
    const button = event.target instanceof HTMLElement ? event.target.closest(".method-item") : null;
    if (button instanceof HTMLElement && button.dataset.method) {
      selectMethod(button.dataset.method);
    }
  });
  window.addEventListener("keydown", (event) => {
    if (event.key === "Escape") closeMethodDialog();
  });
  window.addEventListener("resize", resizeFrame);
  chartFrame.addEventListener("load", resizeFrame);

  renderTree();
  renderMethodTree();
  updateCollapseHandles();
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
  resizeFrame();
})();
