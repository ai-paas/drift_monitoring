(() => {
  const payloads = window.RECREATED_CHART_PAYLOADS || [];
  const list = document.getElementById("chartList");
  const search = document.getElementById("searchInput");
  const chartTitle = document.getElementById("chartTitle");
  const chartStatus = document.getElementById("chartStatus");
  const originalLink = document.getElementById("originalLink");
  const componentChart = document.getElementById("componentChart");
  const issueList = document.getElementById("issueList");
  const INTERPRETATION_JOB_ENDPOINT = "http://127.0.0.1:8767/api/interpret/chart/jobs";
  const interpretationCache = new Map();
  let originalPopup = null;
  let chartNoteButton = null;
  let interpretationStatus = null;
  let activeId = payloads[0]?.chartId || "";
  let activePayload = null;

  function escapeHtml(value) {
    return String(value).replaceAll("&", "&amp;").replaceAll("<", "&lt;").replaceAll(">", "&gt;").replaceAll('"', "&quot;");
  }

  function ensureInterpretationControls() {
    if (!originalLink || interpretationStatus) return;
    interpretationStatus = document.createElement("span");
    interpretationStatus.className = "interpretation-status";
    interpretationStatus.textContent = "";
    originalLink.insertAdjacentElement("afterend", interpretationStatus);
  }

  function noteText(note) {
    if (!note) return "";
    return [note.title, note.summary, note.detail].filter(Boolean).join("\n\n");
  }

  function applyInterpretation(payload, interpretation) {
    const componentNotes = new Map((interpretation.componentNotes || []).map((note) => [note.componentInstanceId, note]));
    return {
      ...payload,
      interpretation,
      components: (payload.components || []).map((component) => ({
        ...component,
        interpretationNote: componentNotes.get(component.componentInstanceId) || component.interpretationNote
      })),
      layout: {
        ...payload.layout,
        areas: (payload.layout?.areas || []).map((area) => ({ ...area }))
      }
    };
  }

  function sleep(ms) {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }

  async function fetchInterpretation(payload) {
    if (!payload?.chartId) return null;
    if (interpretationCache.has(payload.chartId)) return interpretationCache.get(payload.chartId);
    const createResponse = await fetch(INTERPRETATION_JOB_ENDPOINT, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ payload })
    });
    if (!createResponse.ok) throw new Error(`interpretation job server ${createResponse.status}`);
    const job = await createResponse.json();
    if (!job.ok) throw new Error(job.error || "interpretation job failed");
    if (interpretationStatus) interpretationStatus.textContent = job.status === "succeeded" ? "?? ??" : "?? ??";
    let current = job;
    for (let attempt = 0; attempt < 90; attempt += 1) {
      if (current.status === "succeeded") {
        const result = current.result;
        if (!result?.ok) throw new Error(result?.error || "interpretation result failed");
        interpretationCache.set(payload.chartId, result);
        return result;
      }
      if (current.status === "failed") throw new Error(current.error || "interpretation failed");
      if (interpretationStatus) interpretationStatus.textContent = current.status === "running" ? "?? ?? ?" : "?? ??";
      await sleep(Math.min(1000 + attempt * 250, 3000));
      const pollResponse = await fetch(`${INTERPRETATION_JOB_ENDPOINT}/${encodeURIComponent(current.jobId)}`);
      if (!pollResponse.ok) throw new Error(`interpretation job poll ${pollResponse.status}`);
      current = await pollResponse.json();
      if (!current.ok) throw new Error(current.error || "interpretation job poll failed");
    }
    throw new Error("interpretation job timeout");
  }

  function renderList() {
    if (!list || !search) return;
    const q = search.value.trim().toLowerCase();
    list.innerHTML = "";
    payloads
      .filter((payload) => {
        const title = payload.title || "";
        const components = payload.components || [];
        return !q
          || payload.chartId.toLowerCase().includes(q)
          || title.toLowerCase().includes(q)
          || components.some((item) => item.componentType.includes(q));
      })
      .forEach((payload) => {
        const button = document.createElement("button");
        button.className = `chart-button${payload.chartId === activeId ? " active" : ""}`;
        button.type = "button";
        button.innerHTML = `<strong>${payload.chartId}</strong><span>${escapeHtml((payload.components || []).map((item) => item.componentType).join(", "))}</span>`;
        button.addEventListener("click", () => selectChart(payload.chartId));
        list.appendChild(button);
      });
  }

  // @managed-contract contract_id=chart_builder.recreated_charts.selectChart level=P1
  function selectChart(chartId) {
    activeId = chartId;
    const payload = payloads.find((item) => item.chartId === chartId) || payloads[0];
    if (!payload) return;
    ensureInterpretationControls();
    activePayload = payload;
    if (chartTitle) chartTitle.textContent = `${payload.chartId} - ${(payload.title || "").replace(/^.*? - /, "")}`;
    if (chartStatus) {
      const layoutName = payload.layout?.displayName || payload.layout?.presetCode || "saved layout";
      chartStatus.textContent = `${payload.reproduction?.status || "unknown"} reproduction - ${layoutName}`;
    }
    if (originalLink) {
      originalLink.dataset.originalPath = payload.originalPath || "";
      originalLink.title = `${payload.chartId} 원본 차트 보기`;
    }
    if (issueList) {
      issueList.innerHTML = (payload.reproduction?.issues || []).map((issue) => `<li>${escapeHtml(issue)}</li>`).join("");
    }
    window.ChartRuntime.renderChartPayload(componentChart, payload);
    if (chartNoteButton) chartNoteButton.hidden = true;
    if (interpretationStatus) interpretationStatus.textContent = "해석 중";
    fetchInterpretation(payload)
      .then((interpretation) => {
        if (!interpretation || activeId !== payload.chartId) return;
        const interpretedPayload = applyInterpretation(payload, interpretation);
        activePayload = interpretedPayload;
        window.ChartRuntime.renderChartPayload(componentChart, interpretedPayload);
        if (chartNoteButton) {
          chartNoteButton.hidden = !interpretation.chartNote;
          chartNoteButton.dataset.note = noteText(interpretation.chartNote);
        }
        if (interpretationStatus) interpretationStatus.textContent = `${interpretation.chartNote?.provider || "rule"} 해석`;
      })
      .catch((error) => {
        if (interpretationStatus) interpretationStatus.textContent = `해석 실패: ${error.message}`;
      });
    renderList();
  }

  if (search) search.addEventListener("input", renderList);
  if (originalLink) {
    originalLink.addEventListener("click", () => {
      if (!activePayload) return;
      const originalUrl = new URL(activePayload.originalPath, window.location.href);
      originalUrl.searchParams.set("v", Date.now().toString());
      showOriginalPopup(activePayload, originalUrl);
    });
  }

  renderList();
  selectChart(activeId);

  function showOriginalPopup(payload, originalUrl) {
    if (!originalPopup) {
      originalPopup = document.createElement("div");
      originalPopup.id = "originalChartPopup";
      originalPopup.className = "original-popup";
      originalPopup.hidden = true;
      originalPopup.innerHTML = `
        <section class="original-popup-panel" role="dialog" aria-modal="true" aria-labelledby="originalPopupTitle">
          <header class="original-popup-head">
            <div>
              <p class="eyebrow">original chart</p>
              <h2 id="originalPopupTitle"></h2>
            </div>
            <div class="original-popup-actions">
              <a id="originalPopupOpen" class="open-link" target="_blank" rel="noopener">새 탭</a>
              <button id="originalPopupClose" class="open-link" type="button">닫기</button>
            </div>
          </header>
          <iframe id="originalPopupFrame" class="original-popup-frame" title="Original chart"></iframe>
        </section>`;
      originalPopup.addEventListener("click", (event) => {
        if (event.target === originalPopup || event.target.closest("#originalPopupClose")) closeOriginalPopup();
      });
      document.addEventListener("keydown", (event) => {
        if (event.key === "Escape" && originalPopup && !originalPopup.hidden) closeOriginalPopup();
      });
      document.body.appendChild(originalPopup);
    }
    originalPopup.querySelector("#originalPopupTitle").textContent = `${payload.chartId} 원본 차트`;
    originalPopup.querySelector("#originalPopupOpen").href = originalUrl.toString();
    originalPopup.querySelector("#originalPopupFrame").src = originalUrl.toString();
    originalPopup.hidden = false;
    originalPopup.querySelector("#originalPopupClose").focus();
  }

  function closeOriginalPopup() {
    if (!originalPopup) return;
    originalPopup.hidden = true;
    const frame = originalPopup.querySelector("#originalPopupFrame");
    if (frame) frame.removeAttribute("src");
    if (originalLink) originalLink.focus();
  }
})();

