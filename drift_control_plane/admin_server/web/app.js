const steps = [
  "health",
  "reset",
  "register_feeder",
  "register_source",
  "register_adapter",
  "register_method",
  "register_chart",
  "replay_and_poll",
  "timeseries",
  "debug_counts",
  "analysis_payload",
  "llm_interpretation"
];

const query = new URLSearchParams(window.location.search);
const initialTickDelayMs = Math.max(Number(query.get("tickDelayMs") || 200), 0);
const initialReplayProfileId = query.get("replayProfile") || "demo_4h";
let timeseriesWindow = null;

const RUNTIME_METHOD_BY_VARIANT = {
  ADWIN_MEAN_STREAM: "adwin_mean_stream",
  ADWIN_ERROR_RATE: "adwin_error_rate",
  ADWIN_DISTANCE_STREAM: "adwin_distance_stream",
  WASSERSTEIN_1D_EXACT: "wasserstein_numeric_window",
  WASSERSTEIN_APPROX_HISTOGRAM: "wasserstein_numeric_window",
  WASSERSTEIN_WINDOW_TREND: "wasserstein_numeric_window",
  SLICED_WASSERSTEIN_EMBEDDING: "sliced_wasserstein_embedding",
  NUMERIC_BINNED_PSI: "psi_numeric_binned",
  CATEGORICAL_PSI: "psi_numeric_binned",
  SCORE_BAND_PSI: "psi_numeric_binned",
  POPULATION_WEIGHTED_PSI: "psi_numeric_binned",
  DDM_STANDARD: "ddm_error_rate_stream",
  DDM_WARNING_BUFFER: "ddm_warning_buffer",
  DDM_CLASS_SPECIFIC: "ddm_class_specific",
  RDDM_STANDARD: "rddm_error_rate_stream",
  RDDM_REACTIVE_RESET: "rddm_reactive_reset",
  EDDM_DISTANCE_BETWEEN_ERRORS: "eddm_error_rate_stream",
  EDDM_WARNING_DRIFT: "eddm_warning_drift",
  EDDM_GRADUAL_DRIFT: "eddm_gradual_drift",
  GENERIC_METRIC_THRESHOLD_DRIFT: "generic_metric_threshold_drift",
  TIME_FEATURE_SPLIT_DETECTOR: "time_feature_split_detector",
  DOMAIN_CLASSIFIER_TREE: "domain_classifier_tree"
};

const state = {
  status: "loading",
  scenario: null,
  connections: [],
  connectionPresets: [],
  selectedConnectionId: null,
  replayProfileId: initialReplayProfileId,
  chartCatalog: { charts: [], chartMethods: {}, runtimeAliases: {}, source: null },
  steps: Object.fromEntries(steps.map((name) => [name, { status: "pending" }])),
  counts: {},
  eventId: null,
  latest: null,
  timeSeriesUrl: null,
  error: null
};

window.__ADMIN_UI_TEST_STATE__ = state;

function el(id) {
  return document.getElementById(id);
}

function value(id) {
  return el(id).value.trim();
}

function numberValue(id, fallback = 0) {
  const raw = value(id);
  if (raw === "") return fallback;
  const parsed = Number(raw);
  return Number.isFinite(parsed) ? parsed : fallback;
}

function checked(id) {
  return el(id).checked;
}

function setValue(id, next) {
  const target = el(id);
  const value = next ?? "";
  if (target.tagName === "SELECT" && value && !Array.from(target.options).some((option) => option.value === value)) {
    target.add(new Option(value, value));
  }
  target.value = value;
}

function setChecked(id, next) {
  el(id).checked = Boolean(next);
}

function selectedChartItem() {
  const chartId = value("chartId");
  return state.chartCatalog.charts.find((item) => item.chartId === chartId) || null;
}

function setLatest(next) {
  state.latest = next;
  el("artifactView").textContent = JSON.stringify(next, null, 2);
}

function connectionKey(scenario) {
  return `${scenario.source?.sourceId || "source"}::${scenario.adapter?.adapterId || "adapter"}`;
}

function upsertConnection(scenario, status = "draft", options = {}) {
  const key = connectionKey(scenario);
  const next = {
    key,
    status,
    timeseriesUrl: scenario.source?.sourceId ? buildTimeseriesUrl(scenario.source.sourceId) : null,
    source: { ...(scenario.source || {}) },
    feeder: { ...(scenario.feeder || {}) },
    adapter: { ...(scenario.adapter || {}) },
    tick: { ...(scenario.tick || {}) },
    replayProfiles: scenario.replayProfiles || scenario._adminConnection?.replayProfiles || [],
    recommendedAnalyses: scenario.recommendedAnalyses || scenario._adminConnection?.recommendedAnalyses || []
  };
  const index = state.connections.findIndex((item) => item.key === key);
  if (index >= 0) state.connections[index] = { ...state.connections[index], ...next };
  else state.connections.push(next);
  const shouldSelect = options.select !== false || !state.selectedConnectionId;
  if (shouldSelect) state.selectedConnectionId = key;
  renderConnections();
  renderRecommendedAnalyses();
  return next;
}

function scenarioWithConnection(connection) {
  const base = collectScenario();
  return {
    ...base,
    source: { ...base.source, ...(connection?.source || {}) },
    feeder: { ...base.feeder, ...(connection?.feeder || {}) },
    adapter: { ...base.adapter, ...(connection?.adapter || {}) },
    tick: { ...base.tick, ...(connection?.tick || {}) },
    replayProfiles: connection?.replayProfiles || base.replayProfiles || [],
    recommendedAnalyses: connection?.recommendedAnalyses || []
  };
}

function selectedReplayProfileId() {
  return value("replayProfile") || state.replayProfileId || "demo_4h";
}

function replayProfileForScenario(scenario, profileId = selectedReplayProfileId()) {
  const profiles = scenario?.replayProfiles || scenario?._adminConnection?.replayProfiles || [];
  return profiles.find((profile) => profile.profileId === profileId) || profiles[0] || null;
}

function applyReplayProfile(scenario, profileId = selectedReplayProfileId()) {
  const profile = replayProfileForScenario(scenario, profileId);
  if (!profile) return scenario;
  state.replayProfileId = profile.profileId;
  setValue("replayProfile", profile.profileId);
  return {
    ...scenario,
    feeder: {
      ...(scenario.feeder || {}),
      startTime: profile.startTime,
      maxRows: profile.maxRows,
      replayWindow: {
        start: profile.startTime,
        end: profile.endTime
      }
    },
    adapter: {
      ...(scenario.adapter || {}),
      aggregateIntervalMinutes: profile.aggregateIntervalMinutes
    },
    tick: {
      ...(scenario.tick || {}),
      logicalMinutesPerTick: profile.logicalMinutesPerTick,
      tickCount: profile.tickCount,
      pollEveryTicks: profile.pollEveryTicks
    },
    replayProfile: profile
  };
}

function renderConnections() {
  const list = el("connectionList");
  if (!state.connections.length) {
    list.innerHTML = `<div class="connection-empty">등록된 connection이 없습니다.</div>`;
    return;
  }
  list.innerHTML = state.connections.map((connection) => {
    const source = connection.source || {};
    const adapter = connection.adapter || {};
    const active = connection.key === state.selectedConnectionId;
    const registered = connection.status === "registered";
    const timeseriesUrl = connection.timeseriesUrl || (source.sourceId ? buildTimeseriesUrl(source.sourceId) : "");
    return `
      <button class="connection-item ${active ? "active" : ""} ${registered ? "registered" : ""}" type="button" data-connection-key="${connection.key}">
        <span class="connection-title">${escapeHtml(source.title || source.sourceId || "Untitled datasource")}</span>
        <span class="connection-meta">${escapeHtml(source.sourceId || "-")} · ${escapeHtml(adapter.adapterType || "-")}</span>
        <span class="connection-path">${escapeHtml(timeseriesUrl || source.sourceUrl || connection.feeder?.csvPath || "")}</span>
        <span class="connection-badges">
          <span class="badge ${registered ? "ok" : ""}">${registered ? "registered" : "draft"}</span>
          <span class="badge">${escapeHtml(adapter.adapterId || "adapter")}</span>
        </span>
      </button>
    `;
  }).join("");
}

function selectedConnection() {
  return state.connections.find((candidate) => candidate.key === state.selectedConnectionId) || null;
}

function currentDatasetCaseId() {
  return value("datasetCaseId") || state.scenario?.source?.sourceConfig?.datasetCaseId || selectedConnection()?.source?.sourceConfig?.datasetCaseId || "";
}

function methodDisplayForRecommendation(recommendation) {
  const variant = String(recommendation?.methodVariantKey || "").toUpperCase();
  const methods = state.chartCatalog.chartMethods?.[recommendation?.chartId] || [];
  const match = methods.find((item) => methodVariantKey(item.method) === variant);
  return match?.method || recommendation?.method || recommendation?.methodVariantKey || "";
}

function recommendationsForConnection(connection = selectedConnection()) {
  return Array.isArray(connection?.recommendedAnalyses) ? connection.recommendedAnalyses : [];
}

function renderRecommendedAnalyses() {
  const connection = selectedConnection();
  const recommendations = recommendationsForConnection(connection);
  const title = el("recommendedAnalysisTitle");
  const list = el("recommendedAnalysisList");
  const button = el("applyTopRecommendation");
  if (!connection) {
    title.textContent = "connection을 선택하세요.";
    list.innerHTML = `<div class="picker-empty">왼쪽에서 connection을 선택하면 추천 chart/method 조합이 표시됩니다.</div>`;
    button.disabled = true;
    updateCompatibilityWarning();
    return;
  }
  if (!recommendations.length) {
    title.textContent = `${connection.source?.sourceConfig?.datasetCaseId || connection.source?.sourceId || "dataset"} 추천 없음`;
    list.innerHTML = `<div class="picker-empty">등록된 추천 조합이 없습니다. chart/method를 수동으로 선택할 수 있습니다.</div>`;
    button.disabled = true;
    updateCompatibilityWarning();
    return;
  }
  const datasetCaseId = connection.source?.sourceConfig?.datasetCaseId || "";
  title.textContent = `${datasetCaseId || connection.source?.sourceId} 추천 조합 ${recommendations.length}개`;
  button.disabled = false;
  list.innerHTML = recommendations.map((recommendation, index) => {
    const method = methodDisplayForRecommendation(recommendation);
    const rank = recommendation.rank || (index === 0 ? "recommended" : "alternative");
    const runtime = recommendation.runtimeMethodKey || runtimeMethodForVariant(method || recommendation.methodVariantKey);
    const isActive = value("chartId") === recommendation.chartId
      && methodVariantKey(value("compatibleMethod")) === String(recommendation.methodVariantKey || "").toUpperCase();
    return `
      <div class="recommendation-item ${escapeHtml(rank)} ${isActive ? "active" : ""}" data-recommendation-index="${index}">
        <div>
          <span class="recommendation-title">${escapeHtml(recommendation.chartId)} + ${escapeHtml(method || recommendation.methodVariantKey)}</span>
          <span class="recommendation-meta">${isActive ? "선택됨 · " : ""}${escapeHtml(rank)} · ${escapeHtml(runtime || "runtime 확인 필요")} · 대표 ${escapeHtml(recommendation.representativeCaseId || "-")}</span>
          <span class="recommendation-reason">${escapeHtml(recommendation.reason || "")}</span>
          ${isActive ? `<span class="recommendation-hint">적용은 아래 선택 조합 등록 버튼을 누르십시오.</span>` : ""}
        </div>
        <button class="${isActive ? "primary" : "secondary"}" type="button" data-apply-recommendation="${index}">${isActive ? "선택됨" : "이 추천 선택"}</button>
      </div>
    `;
  }).join("");
  updateCompatibilityWarning();
}

async function applyRecommendation(recommendation, options = {}) {
  if (!recommendation?.chartId || !recommendation?.methodVariantKey) return null;
  selectChart(recommendation.chartId);
  const method = methodDisplayForRecommendation(recommendation);
  if (method) selectCompatibleMethod(method);
  const scenario = materializeSelectionForCurrentConnection(recommendation);
  updateCompatibilityWarning(recommendation);
  setLatest({
    appliedRecommendation: {
      chartId: recommendation.chartId,
      methodVariantKey: recommendation.methodVariantKey,
      representativeCaseId: recommendation.representativeCaseId,
      reason: recommendation.reason,
      auto: Boolean(options.auto)
    },
    scenario,
    calibratedParams: recommendation.calibratedParams || null,
    calibratedWindowConfig: recommendation.calibratedWindowConfig || null
  });
  return scenario;
}

async function applyTopRecommendation(options = {}) {
  const recommendation = recommendationsForConnection()[0];
  if (!recommendation) return null;
  return applyRecommendation(recommendation, options);
}

function selectedRecommendationForPair() {
  const chartId = value("chartId");
  const variant = methodVariantKey(value("compatibleMethod"));
  return recommendationsForConnection().find(
    (item) => item.chartId === chartId && String(item.methodVariantKey || "").toUpperCase() === variant
  ) || null;
}

function materializeSelectionForCurrentConnection(recommendation = selectedRecommendationForPair()) {
  const current = collectScenario();
  const chartId = value("chartId") || recommendation?.chartId || current.analysisChart.chartId;
  const method = value("compatibleMethod") || methodDisplayForRecommendation(recommendation);
  const variant = methodVariantKey(method || recommendation?.methodVariantKey);
  const runtime = recommendation?.runtimeMethodKey
    || runtimeMethodForVariant(method || recommendation?.methodVariantKey)
    || current.methodAssignment.runtimeMethodKey;
  const payloadAdapterKey = payloadAdapterForChartAndRuntime(chartId, runtime, variant) || value("payloadAdapterKey") || current.analysisChart.payloadAdapterKey;
  const chart = selectedChartItem();
  const chartTitle = value("chartTitle") || chart?.title || current.analysisChart.chartOptions?.title || chartId;
  const methodSeed = {
    ...current.methodAssignment,
    runtimeMethodKey: runtime,
    params: current.methodAssignment.params,
    windowConfig: current.methodAssignment.windowConfig
  };
  const windowConfig = methodWindowConfigForCurrentConnection(methodSeed, current, recommendation);
  const aggregateIntervalMinutes = aggregateIntervalMinutesForWindowConfig(
    windowConfig,
    Number(current.adapter.aggregateIntervalMinutes || current.adapter.collectionIntervalMinutes || 10)
  );
  let next = {
    ...current,
    source: current.source,
    feeder: current.feeder,
    adapter: {
      ...current.adapter,
      aggregateIntervalMinutes
    },
    methodAssignment: {
      ...current.methodAssignment,
      adapterId: current.adapter.adapterId,
      sourceId: current.source.sourceId,
      runtimeMethodKey: runtime,
      featureId: featureIdForAdapterType(current.adapter?.adapterType, current.methodAssignment.featureId),
      params: methodParamsForCurrentConnection(methodSeed, current, recommendation),
      windowConfig,
      enabled: current.methodAssignment.enabled
    },
    analysisChart: {
      ...current.analysisChart,
      chartId,
      payloadAdapterKey,
      chartOptions: {
        ...(current.analysisChart.chartOptions || {}),
        title: chartTitle
      },
      payloadAdapterConfig: current.analysisChart.payloadAdapterConfig || {}
    }
  };
  const profileId = replayProfileIdForRecommendation(current, recommendation, windowConfig);
  if (profileId) next = applyReplayProfile(next, profileId);
  populateScenario(next, false);
  state.selectedConnectionId = connectionKey(current);
  renderConnections();
  renderRecommendedAnalyses();
  setTimeseriesUrl(current.source.sourceId ? buildTimeseriesUrl(current.source.sourceId) : null);
  return collectScenario();
}

function updateCompatibilityWarning(recommendation = selectedRecommendationForPair()) {
  const warning = el("compatibilityWarning");
  if (!warning) return;
  const datasetCaseId = currentDatasetCaseId();
  const chartId = value("chartId");
  const variant = methodVariantKey(value("compatibleMethod"));
  if (!datasetCaseId || !chartId || !variant) {
    warning.textContent = "";
    warning.classList.remove("visible", "info");
    return;
  }
  if (recommendation) {
    if (recommendation.representativeCaseId && recommendation.representativeCaseId !== datasetCaseId) {
      warning.textContent = `추천 조합 선택됨: ${chartId} + ${variant}. ${datasetCaseId}에 적용하도록 등록되어 있지만, 검증 scenario는 ${recommendation.representativeCaseId} 기반입니다. ${recommendation.reason || ""}`;
      warning.classList.add("visible", "info");
      return;
    }
    warning.textContent = `추천 조합 선택됨: ${chartId} + ${variant}. ${recommendation.reason || ""}`;
    warning.classList.add("visible", "info");
    return;
  }
  warning.textContent = `${datasetCaseId}의 추천 목록에 없는 조합입니다. 실행은 가능하지만 데이터 의미와 chart/method 해석이 약할 수 있습니다.`;
  warning.classList.remove("info");
  warning.classList.add("visible");
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function renderSteps() {
  const list = el("stepList");
  list.innerHTML = "";
  for (const name of steps) {
    const row = document.createElement("li");
    const step = state.steps[name];
    row.className = step.status;
    row.innerHTML = `<i class="dot"></i><span>${name}</span><span class="step-status">${step.status}</span>`;
    list.appendChild(row);
  }
}

function setStep(name, status, details = null) {
  state.steps[name] = { status, details };
  renderSteps();
  if (details) setLatest(details);
}

function resetSteps() {
  for (const name of steps) setStep(name, "pending");
}

function setStatus(status, subtitle) {
  state.status = status;
  el("runStatus").textContent = status;
  el("runSubtitle").textContent = subtitle || "";
}

function setCounts(counts) {
  state.counts = { ...state.counts, ...counts };
  el("rawCount").textContent = state.counts.rawEventCount ?? "-";
  el("bucketCount").textContent = state.counts.bucketCount ?? "-";
  el("runCount").textContent = state.counts.methodRunCount ?? "-";
  el("eventCount").textContent = state.counts.eventCount ?? "-";
}

function buildTimeseriesUrl(sourceId) {
  const url = new URL("/admin/timeseries/drift_metric_timeseries_demo.html", window.location.origin);
  url.searchParams.set("testMode", "1");
  url.searchParams.set("autoPoll", "1");
  url.searchParams.set("pollMs", "1500");
  url.searchParams.set("sourceId", sourceId);
  url.searchParams.set("apiBase", window.location.origin);
  url.searchParams.set("llmJobEndpoint", `${window.location.origin}/api/admin/llm/interpret/chart/jobs`);
  return url.href;
}

function currentTickDelayMs() {
  return Math.max(numberValue("tickDelayMs", initialTickDelayMs), 0);
}

function openTimeseriesForCurrentSource() {
  const sourceId = value("sourceId");
  if (!sourceId) throw new Error("Connection preset을 먼저 Add해서 datasource를 선택하세요.");
  const url = buildTimeseriesUrl(sourceId);
  setTimeseriesUrl(url);
  timeseriesWindow = window.open(url, "drift_metric_timeseries_live", "noreferrer");
  if (timeseriesWindow) timeseriesWindow.focus();
  return url;
}

function setTimeseriesUrl(url) {
  state.timeSeriesUrl = url;
  const link = el("timeseriesLink");
  link.href = url || "#";
  link.textContent = url || "datasource 연결 후 생성됩니다.";
}

function updateConnectionSummary() {
  const title = value("sourceTitle") || value("sourceId") || "선택된 datasource 없음";
  const adapter = value("adapterId") || "adapter 미선택";
  const adapterType = value("adapterType") || "adapter type 미선택";
  const path = value("sourceUrl") || value("csvPath") || "URL/path 미설정";
  el("connectionSummaryTitle").textContent = title;
  el("connectionSummaryMeta").textContent = `${value("sourceId") || "-"} · ${adapter} · ${adapterType} · ${path}`;
}

async function request(path, options = {}) {
  const response = await fetch(path, {
    ...options,
    headers: {
      "Accept": "application/json",
      "Content-Type": "application/json",
      ...(options.headers || {})
    }
  });
  const text = await response.text();
  const data = text ? JSON.parse(text) : {};
  if (!response.ok || data.ok === false) {
    throw new Error(`${path} failed: ${JSON.stringify(data)}`);
  }
  return data;
}

async function post(path, body) {
  return request(path, { method: "POST", body: JSON.stringify(body || {}) });
}

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function getHealth() {
  const health = await request("/api/admin/health");
  const data = health.data || {};
  el("healthAdmin").textContent = "ok";
  el("healthDrift").textContent = data.driftServer ? "ok" : "fail";
  el("healthFeeder").textContent = data.testFeederServer ? "ok" : "fail";
  el("healthLlm").textContent = data.llmServer ? "ok" : "fail";
  return health;
}

function populateScenario(scenario, updateConnection = true) {
  state.scenario = scenario;
  const source = scenario.source || {};
  const feeder = scenario.feeder || {};
  const adapter = scenario.adapter || {};
  const method = scenario.methodAssignment || {};
  const chart = scenario.analysisChart || {};

  setValue("sourceId", source.sourceId);
  setValue("sourceTitle", source.title);
  setValue("sourceType", source.sourceType || "test_db");
  setValue("sourceUrl", source.sourceUrl);
  setValue("sourceDescription", source.description);
  setValue("datasetCaseId", source.sourceConfig?.datasetCaseId || feeder.datasetCaseId);

  setValue("adapterId", adapter.adapterId);
  setValue("adapterType", adapter.adapterType || "test_db_numeric_stream");
  setValue("collectionIntervalMinutes", adapter.collectionIntervalMinutes);
  setValue("aggregateIntervalMinutes", adapter.aggregateIntervalMinutes);
  setValue("startTime", feeder.startTime);
  setValue("replayEnd", feeder.replayWindow?.end);
  setValue("csvPath", feeder.csvPath || source.sourceUrl);
  setValue("valuePath", adapter.sourceConfig?.valuePath || "$.metric");
  updateConnectionSummary();

  setValue("assignmentId", method.assignmentId);
  setValue("featureId", method.featureId || "metric");
  setValue("runtimeMethodKey", method.runtimeMethodKey || "adwin_mean_stream");
  setValue("eventLevel", method.threshold?.eventLevel || "drift");
  setValue("delta", method.params?.delta);
  setValue("meanShiftThreshold", method.params?.meanShiftThreshold);
  setValue("bucketResolution", method.windowConfig?.bucketResolution || "10m");
  setValue("lookbackBuckets", method.windowConfig?.lookbackBuckets || 144);
  setChecked("useAlgorithmImpl", method.params?.useAlgorithmImpl);
  setChecked("methodEnabled", method.enabled !== false);

  setValue("analysisChartId", chart.analysisChartId);
  setValue("chartId", chart.chartId || "CHART-STREAM-001");
  setValue("payloadAdapterKey", chart.payloadAdapterKey);
  setValue("chartTitle", chart.chartOptions?.title);
  updateCompatibleMethods();
  updateChartPreview();
  renderRecommendedAnalyses();

  if (updateConnection) upsertConnection(scenario, "draft");
  setTimeseriesUrl(source.sourceId ? buildTimeseriesUrl(source.sourceId) : null);
  setLatest({ loadedScenario: scenario.scenarioId || "draft", scenario: collectScenario() });
}

function populateConnection(connection) {
  if (!connection) return;
  const scenario = scenarioWithConnection(connection);
  populateScenario({
    ...state.scenario,
    ...scenario,
    source: scenario.source,
    feeder: scenario.feeder,
    adapter: scenario.adapter,
    recommendedAnalyses: scenario.recommendedAnalyses || connection.recommendedAnalyses || []
  }, false);
  state.selectedConnectionId = connection.key;
  renderConnections();
  renderRecommendedAnalyses();
  setTimeseriesUrl(connection.timeseriesUrl || buildTimeseriesUrl(connection.source?.sourceId || value("sourceId")));
}

function connectionDatasetCaseId(current) {
  return current.source?.sourceConfig?.datasetCaseId || current.feeder?.datasetCaseId || "";
}

function connectionValueColumn(current) {
  const valuePath = current.adapter?.sourceConfig?.valuePath || "";
  const match = String(valuePath).match(/^\$\.([A-Za-z0-9_]+)$/);
  return match?.[1] || "metric";
}

function connectionFeatureColumns(current) {
  const featureColumns = current.adapter?.sourceConfig?.featureColumns || [];
  if (Array.isArray(featureColumns) && featureColumns.length) return featureColumns;
  const valueColumn = connectionValueColumn(current);
  return valueColumn ? [valueColumn] : [];
}

function runtimeUsesFeatureColumns(runtime) {
  return [
    "isolation_forest_drift_score",
    "one_class_svm_drift",
    "autoencoder_reconstruction_drift",
    "sliced_wasserstein_embedding",
    "linear_time_mmd",
    "mmd_window",
    "kernel_mmd_biased",
    "kernel_mmd_unbiased",
    "multivariate_process_window",
    "mewma_window",
    "mahalanobis_window",
    "hotelling_t2_window",
    "shap_window",
    "global_importance_rank_shift",
    "shap_value_distribution_test",
    "feature_map_window",
    "model_feature_map_mmd",
    "model_feature_map_ks",
    "graph_embedding_window",
    "graph_embedding_mmd",
    "llm_query_semantic_window",
    "topic_distribution_shift",
    "query_centroid_cosine_shift"
  ].includes(runtime);
}

function runtimeUsesWindowBucket(runtime, adapterType) {
  if (String(adapterType || "").endsWith("_window")) return true;
  return [
    "psi_numeric_binned",
    "wasserstein_numeric_window",
    "kswin_numeric_window",
    "generic_distribution_ecdf_window",
    "generic_statistical_test_window",
    "generic_probability_distance_window",
    "generic_categorical_contingency_window",
    "model_uncertainty_window",
    "isolation_forest_drift_score",
    "one_class_svm_drift",
    "autoencoder_reconstruction_drift",
    "shap_window",
    "feature_map_window",
    "graph_embedding_window",
    "llm_query_semantic_window"
  ].includes(runtime);
}

function methodParamsForCurrentConnection(method, current, recommendation = null) {
  const params = { ...(method.params || current.methodAssignment.params || {}) };
  if (recommendation?.calibratedParams) Object.assign(params, recommendation.calibratedParams);
  const runtime = method.runtimeMethodKey || runtimeMethodForVariant(value("compatibleMethod"));
  const variant = methodVariantKey(value("compatibleMethod"));
  const featureColumns = connectionFeatureColumns(current);
  const valueColumn = connectionValueColumn(current);
  if (params.variant_id || runtime) params.variant_id = variant || params.variant_id;
  if (recommendation?.calibratedParams && !Object.hasOwn(recommendation.calibratedParams, "useAlgorithmImpl")) {
    delete params.useAlgorithmImpl;
  }
  if (runtimeUsesFeatureColumns(runtime) && featureColumns.length) {
    params.feature_cols = featureColumns;
    if (Array.isArray(params.featureColumns)) params.featureColumns = featureColumns;
  }
  if (Array.isArray(params.feature_cols) && featureColumns.length) params.feature_cols = featureColumns;
  if (params.value_col && valueColumn) params.value_col = valueColumn;
  if (params.valueColumn && valueColumn) params.valueColumn = valueColumn;
  if (params.score_col && valueColumn) params.score_col = valueColumn;
  if (params.scoreColumn && valueColumn) params.scoreColumn = valueColumn;
  const datasetCaseId = connectionDatasetCaseId(current);
  if (!recommendation?.calibratedParams && datasetCaseId === "CASE-009" && runtime === "isolation_forest_drift_score") {
    params.anomaly_rate_threshold = 0.1;
    params.min_reference_size = Math.min(Number(params.min_reference_size || 20), 20);
    params.min_current_size = Math.min(Number(params.min_current_size || 20), 20);
  }
  return params;
}

function methodWindowConfigForCurrentConnection(method, current, recommendation = null) {
  const windowConfig = { ...(method.windowConfig || current.methodAssignment.windowConfig || {}) };
  if (recommendation?.calibratedWindowConfig) Object.assign(windowConfig, recommendation.calibratedWindowConfig);
  const aggregate = Number(current.adapter?.aggregateIntervalMinutes || 0);
  const runtime = method.runtimeMethodKey || runtimeMethodForVariant(value("compatibleMethod"));
  const adapterType = current.adapter?.adapterType || "";
  if (!recommendation?.calibratedWindowConfig && aggregate > 0 && runtimeUsesWindowBucket(runtime, adapterType)) {
    windowConfig.bucketResolution = `${aggregate}m`;
    if (aggregate >= 60 || runtimeUsesFeatureColumns(runtime)) windowConfig.lookbackBuckets = 1;
  }
  return windowConfig;
}

function aggregateIntervalMinutesForWindowConfig(windowConfig, fallback = 10) {
  const resolution = String(windowConfig?.bucketResolution || "");
  const match = resolution.match(/^(\d+)\s*m$/i);
  if (!match) return fallback;
  const minutes = Number(match[1]);
  return Number.isFinite(minutes) && minutes > 0 ? minutes : fallback;
}

function featureIdForAdapterType(adapterType, fallback = "metric") {
  if (adapterType === "test_db_prediction_log_stream") return "error_rate";
  if (adapterType === "test_db_numeric_distribution_window") return "score";
  if (adapterType === "test_db_multivariate_window") return "multivariate";
  if (adapterType === "test_db_categorical_count_window") return "category";
  return fallback || "metric";
}

function replayProfileIdForRecommendation(current, recommendation, windowConfig) {
  const profiles = current.replayProfiles || current._adminConnection?.replayProfiles || [];
  if (!profiles.length) return null;
  if (recommendation?.replayProfileId && profiles.some((profile) => profile.profileId === recommendation.replayProfileId)) {
    return recommendation.replayProfileId;
  }
  const selectedProfileId = selectedReplayProfileId();
  if (selectedProfileId && profiles.some((profile) => profile.profileId === selectedProfileId)) {
    return selectedProfileId;
  }
  const resolutionMinutes = aggregateIntervalMinutesForWindowConfig(windowConfig, 0);
  if (resolutionMinutes > 0) {
    const compatibleProfile = profiles.find((profile) => Number(profile.aggregateIntervalMinutes || 0) === resolutionMinutes)
      || profiles.find((profile) => Number(profile.aggregateIntervalMinutes || 0) > resolutionMinutes);
    if (compatibleProfile) return compatibleProfile.profileId;
  }
  if (resolutionMinutes >= 1440) {
    return profiles.find((profile) => profile.profileId === "long_horizon_120d")?.profileId
      || profiles.find((profile) => Number(profile.aggregateIntervalMinutes || 0) >= 1440)?.profileId
      || null;
  }
  return null;
}

function populateSelectionScenario(preset, recommendation = null) {
  const current = collectScenario();
  const method = preset.methodAssignment || {};
  const chart = preset.analysisChart || {};
  const windowConfig = methodWindowConfigForCurrentConnection(method, current, recommendation);
  let next = {
    ...current,
    scenarioId: current.scenarioId,
    title: current.title,
    source: current.source,
    feeder: current.feeder,
    adapter: current.adapter,
    methodAssignment: {
      ...current.methodAssignment,
      ...method,
      assignmentId: current.methodAssignment.assignmentId,
      adapterId: current.adapter.adapterId,
      sourceId: current.source.sourceId,
      featureId: featureIdForAdapterType(current.adapter?.adapterType, method.featureId || current.methodAssignment.featureId),
      params: methodParamsForCurrentConnection(method, current, recommendation),
      threshold: method.threshold || current.methodAssignment.threshold,
      windowConfig,
      enabled: method.enabled ?? current.methodAssignment.enabled
    },
    analysisChart: {
      ...current.analysisChart,
      ...chart,
      analysisChartId: current.analysisChart.analysisChartId,
      chartOptions: chart.chartOptions || current.analysisChart.chartOptions,
      payloadAdapterConfig: chart.payloadAdapterConfig || current.analysisChart.payloadAdapterConfig
    },
    tick: current.tick
  };
  const profileId = replayProfileIdForRecommendation(current, recommendation, windowConfig);
  if (profileId) next = applyReplayProfile(next, profileId);
  populateScenario(next, false);
  state.selectedConnectionId = connectionKey(current);
  renderConnections();
  renderRecommendedAnalyses();
  setTimeseriesUrl(current.source.sourceId ? buildTimeseriesUrl(current.source.sourceId) : null);
  setLatest({
    loadedSelectionScenario: preset.scenarioId || "selection_preset",
    preservedConnection: {
      sourceId: current.source.sourceId,
      adapterId: current.adapter.adapterId
    },
    appliedRecommendation: recommendation,
    scenario: collectScenario()
  });
}

function collectScenario() {
  const sourceId = value("sourceId");
  const adapterId = value("adapterId");
  const assignmentId = value("assignmentId");
  const datasetCaseId = value("datasetCaseId");
  const csvPath = value("csvPath");
  const startTime = value("startTime");
  const replayEnd = value("replayEnd");
  const baseAdapterConfig = state.scenario?.adapter?.sourceConfig || {};
  const baseMethodParams = state.scenario?.methodAssignment?.params || {};
  const runtimeMethodKey = value("runtimeMethodKey");
  const methodParams = {
    ...baseMethodParams,
    delta: numberValue("delta", 0.002),
    meanShiftThreshold: numberValue("meanShiftThreshold", 0.05)
  };
  if (checked("useAlgorithmImpl")) {
    methodParams.useAlgorithmImpl = true;
  } else if (
    Object.hasOwn(baseMethodParams, "useAlgorithmImpl")
    && baseMethodParams.useAlgorithmImpl === false
    && !runtimeUsesWindowBucket(runtimeMethodKey, value("adapterType"))
  ) {
    methodParams.useAlgorithmImpl = false;
  } else {
    delete methodParams.useAlgorithmImpl;
  }
  return {
    scenarioId: state.scenario?.scenarioId || "admin_custom",
    mode: "A",
    title: state.scenario?.title || "Admin configured scenario",
    source: {
      sourceId,
      title: value("sourceTitle"),
      description: value("sourceDescription"),
      sourceType: value("sourceType"),
      sourceUrl: value("sourceUrl") || csvPath,
      sourceConfig: { datasetCaseId }
    },
    feeder: {
      sourceId,
      datasetCaseId,
      csvPath,
      speedFactor: state.scenario?.feeder?.speedFactor || 60,
      startTime,
      maxRows: state.scenario?.feeder?.maxRows || 0,
      replayWindow: { start: startTime, end: replayEnd }
    },
    adapter: {
      adapterId,
      sourceId,
      adapterType: value("adapterType"),
      adapterTitle: `${value("sourceTitle") || sourceId} adapter`,
      collectionIntervalMinutes: numberValue("collectionIntervalMinutes", 10),
      aggregateIntervalMinutes: numberValue("aggregateIntervalMinutes", 10),
      sourceConfig: {
        ...baseAdapterConfig,
        table: "test_source.raw_event",
        timeColumn: baseAdapterConfig.timeColumn || "event_time",
        valuePath: value("valuePath") || "$.metric"
      }
    },
    methodAssignment: {
      assignmentId,
      adapterId,
      featureId: value("featureId") || "metric",
      methodVariantId: state.scenario?.methodAssignment?.methodVariantId || 123,
      algorithmImplementationId: state.scenario?.methodAssignment?.algorithmImplementationId || 45,
      runtimeMethodKey,
      params: methodParams,
      threshold: { eventLevel: value("eventLevel") || "drift" },
      windowConfig: {
        bucketResolution: value("bucketResolution") || "10m",
        lookbackBuckets: numberValue("lookbackBuckets", 144)
      },
      enabled: checked("methodEnabled")
    },
    analysisChart: {
      analysisChartId: value("analysisChartId"),
      chartId: value("chartId"),
      payloadAdapterKey: value("payloadAdapterKey"),
      chartOptions: { title: value("chartTitle") },
      payloadAdapterConfig: {}
    },
    replayProfiles: state.scenario?.replayProfiles || [],
    replayProfile: replayProfileForScenario(state.scenario),
    tick: state.scenario?.tick || {
      logicalMinutesPerTick: 10,
      tickCount: 24,
      pollEveryTicks: 1
    },
    recommendedAnalyses: recommendationsForConnection()
  };
}

async function loadChartCatalog() {
  const payload = await request("/api/admin/report/gallery-data");
  const data = payload.data || {};
  state.chartCatalog = {
    charts: Array.isArray(data.charts) ? data.charts : [],
    chartMethods: data.chartMethods || {},
    runtimeAliases: data.runtimeAliases || {},
    source: data.source || null
  };
  renderChartOptions();
  updateCompatibleMethods();
  updateChartPreview();
  renderRecommendedAnalyses();
  setLatest({ chartCatalog: state.chartCatalog.source, chartCount: state.chartCatalog.charts.length });
}

function renderChartOptions() {
  const current = value("chartId") || "CHART-STREAM-001";
  const query = value("chartSearch").toLowerCase();
  const charts = state.chartCatalog.charts
    .filter((item) => {
      const haystack = `${item.chartId} ${item.title || ""} ${item.family || ""}`.toLowerCase();
      return !query || haystack.includes(query);
    })
    .slice(0, 120);
  if (!charts.some((item) => item.chartId === current)) {
    const selected = state.chartCatalog.charts.find((item) => item.chartId === current);
    if (selected) charts.unshift(selected);
  }
  el("chartId").innerHTML = charts.length
    ? charts.map((item) => `<option value="${escapeHtml(item.chartId)}">${escapeHtml(item.chartId)} - ${escapeHtml(item.title || item.chartId)}</option>`).join("")
    : `<option value="${escapeHtml(current)}">${escapeHtml(current)}</option>`;
  if (charts.some((item) => item.chartId === current)) setValue("chartId", current);
  renderChartPicker(charts, current);
}

function updateCompatibleMethods() {
  const chartId = value("chartId");
  const methods = state.chartCatalog.chartMethods?.[chartId] || [];
  const current = value("compatibleMethod");
  el("compatibleMethod").innerHTML = methods.length
    ? methods.map((item) => `<option value="${escapeHtml(item.method)}">${escapeHtml(item.method)}</option>`).join("")
    : `<option value="">연결 가능한 method 없음</option>`;
  if (methods.length) {
    const supported = methods.find((item) => runtimeMethodForVariant(item.method));
    const method = methods.some((item) => item.method === current && runtimeMethodForVariant(item.method))
      ? current
      : supported?.method || methods[0].method || "";
    setValue("compatibleMethod", method);
    if (runtimeMethodForVariant(method)) applyCompatibleMethod(method);
  }
  const supportedCount = methods.filter((item) => runtimeMethodForVariant(item.method)).length;
  const summary = methods.length
    ? `${supportedCount}/${methods.length} executable method(s): ${methods.slice(0, 2).map((item) => item.method).join(" / ")}`
    : "연결 가능한 method가 catalog에 없습니다.";
  el("chartMethodSummary").textContent = summary;
  renderMethodPicker(methods, value("compatibleMethod"));
  updateCompatibilityWarning();
}

function renderChartPicker(charts, current) {
  el("chartPickerCount").textContent = String(charts.length);
  const list = el("chartPickerList");
  if (!charts.length) {
    list.innerHTML = `<div class="picker-empty">검색 조건에 맞는 분석 차트가 없습니다.</div>`;
    return;
  }
  list.innerHTML = charts.map((item) => {
    const chartId = item.chartId || "";
    const methods = state.chartCatalog.chartMethods?.[chartId] || [];
    return `
      <button class="picker-item ${chartId === current ? "active" : ""}" type="button" data-chart-id="${escapeHtml(chartId)}">
        <span class="picker-title">${escapeHtml(chartId)} - ${escapeHtml(item.title || chartId)}</span>
        <span class="picker-meta">${escapeHtml(item.family || "chart")} · ${methods.length} method(s)</span>
      </button>
    `;
  }).join("");
}

function renderMethodPicker(methods, current) {
  el("methodPickerCount").textContent = String(methods.length);
  const list = el("methodPickerList");
  if (!methods.length) {
    list.innerHTML = `<div class="picker-empty">선택된 차트에 연결 가능한 drift method가 없습니다.</div>`;
    return;
  }
  list.innerHTML = methods.map((item) => {
    const method = item.method || "";
    const runtime = runtimeMethodForVariant(method);
    const reason = item.selectionReason || item.reason || item.description || "";
    return `
      <button class="picker-item ${method === current ? "active" : ""}" type="button" data-method="${escapeHtml(method)}">
        <span class="picker-title">${escapeHtml(method)}</span>
        <span class="picker-meta">${escapeHtml(runtime ? `${runtime} · 등록 가능` : "현재 drift server runtime 미지원")}</span>
        ${reason ? `<span class="picker-reason">${escapeHtml(reason)}</span>` : ""}
      </button>
    `;
  }).join("");
}

function selectChart(chartId) {
  if (!chartId) return;
  setValue("chartId", chartId);
  renderChartOptions();
  updateCompatibleMethods();
  updateChartPreview();
}

function selectCompatibleMethod(method) {
  if (!method) return;
  setValue("compatibleMethod", method);
  if (runtimeMethodForVariant(method)) applyCompatibleMethod(method);
  renderMethodPicker(state.chartCatalog.chartMethods?.[value("chartId")] || [], method);
  updateSelectionSummary();
  updateCompatibilityWarning();
}

function methodVariantKey(method) {
  return String(method || "").split("/").pop().trim().toUpperCase();
}

// @managed-contract contract_id=admin_ui.loadScenarioForCurrentSelection level=P1
async function loadScenarioForCurrentSelection(recommendation = null) {
  const chartId = value("chartId");
  const variant = methodVariantKey(value("compatibleMethod"));
  if (!chartId || !variant) return null;
  const effectiveRecommendation = recommendation || selectedRecommendationForPair();
  const response = await request(
    `/api/admin/report/scenario-for-selection?chartId=${encodeURIComponent(chartId)}&methodVariantKey=${encodeURIComponent(variant)}`
  );
  if (!response.data) return null;
  populateSelectionScenario(response.data, effectiveRecommendation);
  setStatus("scenario_loaded", `${chartId} + ${variant} preset loaded for current connection`);
  return response.data;
}

function updateSelectionSummary() {
  const chartId = value("chartId") || "차트 미선택";
  const method = value("compatibleMethod") || "메소드 미선택";
  const runtime = runtimeMethodForVariant(method) || "runtime 미지원";
  el("selectionSummary").textContent = `${chartId} + ${method} (${runtime})`;
}

function applyCompatibleMethod(method) {
  const variant = String(method || "").split("/").pop().trim();
  const runtime = runtimeMethodForVariant(variant);
  if (runtime) setValue("runtimeMethodKey", runtime);
  const adapterKey = payloadAdapterForChartAndRuntime(value("chartId"), runtime, variant);
  if (adapterKey) setValue("payloadAdapterKey", adapterKey);
  renderRecommendedAnalyses();
}

function runtimeMethodForVariant(variant) {
  const raw = String(variant || "").split("/").pop().trim();
  const catalogKey = raw.toUpperCase();
  const aliases = state.chartCatalog?.runtimeAliases || {};
  if (aliases[catalogKey]) return aliases[catalogKey];
  if (RUNTIME_METHOD_BY_VARIANT[catalogKey]) return RUNTIME_METHOD_BY_VARIANT[catalogKey];
  const runtimeKey = raw.toLowerCase();
  const runtimeValues = [...Object.values(aliases), ...Object.values(RUNTIME_METHOD_BY_VARIANT)];
  if (runtimeValues.includes(runtimeKey)) return runtimeKey;
  return "";
}

function payloadAdapterForChartAndRuntime(chartId, runtime, variant) {
  if (chartId === "CHART-STREAM-001" && runtime === "adwin_mean_stream") return "adwin_mean_stream_to_chart_stream_001";
  const variantKey = String(variant || "").split("/").pop().trim().toUpperCase();
  if (!runtime || !chartId || !variantKey) return "";
  return `auto__${variantKey}__${chartId}`;
}

function reportChartUrl(item) {
  const htmlPath = item?.htmlPath || `${value("chartId").toLowerCase().replaceAll("-", "_")}.html`;
  const cleanPath = String(htmlPath).replace(/^\.?\//, "");
  return `/admin/report/charts/${cleanPath}`;
}

function updateChartPreview() {
  const item = selectedChartItem();
  const chartId = value("chartId");
  const title = item?.title || chartId;
  const url = reportChartUrl(item);
  const normalizedTitle = String(title || "").trim();
  el("chartPreviewTitle").textContent = normalizedTitle.startsWith(`${chartId} -`) || normalizedTitle === chartId
    ? normalizedTitle
    : `${chartId} - ${normalizedTitle}`;
  el("chartCatalogSource").textContent = state.chartCatalog.source?.type || "catalog";
  el("openReportChart").href = url;
  if (title) setValue("chartTitle", title);
  updateSelectionSummary();
  updateCompatibilityWarning();
}

function ticksFromScenario(scenario) {
  const start = new Date(scenario.feeder.startTime);
  const tick = scenario.tick;
  const result = [];
  for (let i = 1; i <= tick.tickCount; i += 1) {
    const when = new Date(start.getTime() + i * tick.logicalMinutesPerTick * 60000);
    result.push({ index: i, logicalNow: when.toISOString().replace(".000Z", "Z") });
  }
  return result;
}

function firstEventId(timeseries) {
  const events = timeseries?.data?.events || {};
  for (const rows of Object.values(events)) {
    if (Array.isArray(rows) && rows.length && rows[0].eventId) return rows[0].eventId;
  }
  return null;
}

function seriesPointCount(timeseries) {
  const series = timeseries?.data?.series || {};
  return Object.values(series).reduce((total, rows) => total + (Array.isArray(rows) ? rows.length : 0), 0);
}

async function pollLlmJob(jobId) {
  let latest = null;
  for (let i = 0; i < 90; i += 1) {
    latest = await request(`/api/admin/llm/interpret/chart/jobs/${jobId}`);
    if (["succeeded", "failed"].includes(latest.status)) return latest;
    await sleep(Math.min(1000 + i * 250, 3000));
  }
  return latest;
}

function testAnchorPreset(scenario) {
  const title = "CASE-010 stream_numeric_mean_shift test anchor";
  return {
    ...scenario,
    source: {
      ...scenario.source,
      title,
      description: "Admin smoke-test connection anchored around the expected CASE-010 drift window."
    }
  };
}

async function loadConnectionPresets() {
  const [anchorResponse, testDataResponse] = await Promise.all([
    request("/api/admin/anchor/case010/scenario"),
    request("/api/admin/test-data/connections")
  ]);
  const anchorPreset = testAnchorPreset(anchorResponse.data);
  const testDataPresets = testDataResponse.data?.connections || [];
  state.connectionPresets = [anchorPreset, ...testDataPresets];
  const menu = el("connectionMenu");
  menu.innerHTML = [
    `<option value="">Connection preset 선택</option>`,
    ...state.connectionPresets.map((scenario) => {
      const sourceId = scenario.source?.sourceId || "";
      const title = scenario.source?.title || sourceId || "Dataset preset";
      return `<option value="preset:${escapeHtml(sourceId)}">${escapeHtml(title)}</option>`;
    })
  ].join("");
  setLatest({ loadedConnectionPresets: state.connectionPresets.length });
  return state.connectionPresets;
}

async function ensureScenarioReady() {
  if (value("sourceId") && value("adapterId") && value("assignmentId")) return;
  throw new Error("Connection preset을 선택하고 Add를 눌러 connection을 먼저 선택하세요.");
}

async function addConnectionFromMenu() {
  const mode = value("connectionMenu");
  if (!mode) {
    throw new Error("Connection preset을 선택하세요.");
  }
  if (mode.startsWith("preset:")) {
    const sourceId = mode.slice("preset:".length);
    const preset = state.connectionPresets.find((item) => item.source?.sourceId === sourceId);
    const scenario = applyReplayProfile(preset);
    if (!scenario) throw new Error(`Connection preset not found: ${sourceId}`);
    populateScenario(scenario);
    const connection = upsertConnection(scenario, "dataset");
    await applyTopRecommendation({ auto: true });
    setLatest({ addedConnection: connectionKey(scenario), scenario });
    return;
  }
  throw new Error(`Unsupported connection menu option: ${mode}`);
}

async function resetScenario() {
  const scenario = collectScenario();
  const result = await post("/api/admin/test/reset", { mode: "manual", sourceId: scenario.source.sourceId, force: true });
  setLatest(result);
  setStatus("idle", "reset complete");
}

async function registerSource() {
  const scenario = collectScenario();
  const result = await post("/api/admin/sources", scenario.source);
  upsertConnection(scenario, "draft");
  setTimeseriesUrl(buildTimeseriesUrl(scenario.source.sourceId));
  setLatest(result);
  return result;
}

async function registerFeeder() {
  const scenario = collectScenario();
  const result = await post("/api/admin/test/feeders", scenario.feeder);
  upsertConnection(scenario, "draft");
  setLatest(result);
  return result;
}

async function registerAdapter() {
  const scenario = collectScenario();
  const result = await post("/api/admin/adapters", scenario.adapter);
  upsertConnection(scenario, "registered");
  setLatest(result);
  return result;
}

async function registerMethod() {
  const scenario = collectScenario();
  const result = await post(`/api/admin/sources/${scenario.source.sourceId}/method-assignments`, scenario.methodAssignment);
  setLatest(result);
  return result;
}

async function registerChart() {
  const scenario = collectScenario();
  const result = await post(
    `/api/admin/sources/${scenario.source.sourceId}/method-assignments/${scenario.methodAssignment.assignmentId}/analysis-charts`,
    scenario.analysisChart
  );
  setLatest(result);
  return result;
}

async function registerSelection() {
  await ensureScenarioReady();
  materializeSelectionForCurrentConnection(selectedRecommendationForPair());
  const runtime = runtimeMethodForVariant(value("compatibleMethod"));
  if (!runtime) {
    throw new Error(`선택한 method는 현재 drift server runtime으로 등록할 수 없습니다: ${value("compatibleMethod")}`);
  }
  setStatus("registering", "선택한 drift method와 analysis chart를 등록 중");
  const methodResult = await registerMethod();
  const chartResult = await registerChart();
  const timeseriesUrl = buildTimeseriesUrl(value("sourceId"));
  setTimeseriesUrl(timeseriesUrl);
  upsertConnection(collectScenario(), "registered");
  const result = {
    ok: true,
    registeredSelection: {
      sourceId: value("sourceId"),
      assignmentId: value("assignmentId"),
      chartId: value("chartId"),
      method: value("compatibleMethod"),
      runtimeMethodKey: value("runtimeMethodKey"),
      timeseriesUrl
    },
    methodResult,
    chartResult
  };
  setStatus("registered", `${value("chartId")} + ${value("runtimeMethodKey")}`);
  setLatest(result);
  return result;
}

async function replayAndPoll() {
  const scenario = collectScenario();
  const sourceId = scenario.source.sourceId;
  const adapterId = scenario.adapter.adapterId;
  const ticks = ticksFromScenario(scenario);
  for (const item of ticks) {
    setStatus("running", `tick ${item.index}/${ticks.length} replay ${item.logicalNow}`);
    await post(`/api/admin/test/feeders/${sourceId}/tick`, { logicalNow: item.logicalNow, tickIndex: item.index });
    await post("/api/admin/test/tick", { logicalNow: item.logicalNow, tickIndex: item.index });
    if (item.index % scenario.tick.pollEveryTicks === 0) {
      await post(`/api/admin/drift/adapters/${adapterId}/poll-once`, { logicalNow: item.logicalNow });
    }
    const delayMs = currentTickDelayMs();
    if (delayMs > 0) await sleep(delayMs);
  }
  const result = { ok: true, tickCount: scenario.tick.tickCount };
  setLatest(result);
  return result;
}

async function refreshCounts(scenario) {
  const sourceId = scenario.source.sourceId;
  const adapterId = scenario.adapter.adapterId;
  const assignmentId = scenario.methodAssignment.assignmentId;
  const raw = await request(`/api/admin/test/raw-events/${sourceId}`);
  const buckets = await request(`/api/admin/drift/debug/buckets?sourceId=${sourceId}&adapterId=${adapterId}`);
  const runs = await request(`/api/admin/drift/debug/method-runs?sourceId=${sourceId}&assignmentId=${assignmentId}`);
  const events = await request(`/api/admin/drift/debug/drift-events?sourceId=${sourceId}&assignmentId=${assignmentId}`);
  setCounts({
    rawEventCount: raw.data?.count ?? 0,
    bucketCount: buckets.data?.count ?? 0,
    methodRunCount: runs.data?.count ?? 0,
    eventCount: events.data?.count ?? 0
  });
  return { raw, buckets, runs, events };
}

async function runAnchor() {
  el("runAnchor").disabled = true;
  state.error = null;
  resetSteps();
  setCounts({ rawEventCount: "-", bucketCount: "-", methodRunCount: "-", eventCount: "-" });
  setStatus("running", "datasource, adapter, method, chart 연결 실행 중");
  if (checked("openTimeseriesBeforeRun") && value("sourceId")) {
    openTimeseriesForCurrentSource();
  }
  try {
    await ensureScenarioReady();
    materializeSelectionForCurrentConnection(selectedRecommendationForPair());
    setStep("health", "running");
    setStep("health", "passed", await getHealth());

    const scenario = collectScenario();
    state.scenario = scenario;
    const sourceId = scenario.source.sourceId;
    const assignmentId = scenario.methodAssignment.assignmentId;
    setTimeseriesUrl(buildTimeseriesUrl(sourceId));

    setStep("reset", "running");
    setStep("reset", "passed", await post("/api/admin/test/reset", { mode: "run", sourceId, force: true }));

    setStep("register_feeder", "running");
    setStep("register_feeder", "passed", await registerFeeder());

    setStep("register_source", "running");
    setStep("register_source", "passed", await registerSource());

    setStep("register_adapter", "running");
    setStep("register_adapter", "passed", await registerAdapter());

    setStep("register_method", "running");
    setStep("register_method", "passed", await registerMethod());

    setStep("register_chart", "running");
    setStep("register_chart", "passed", await registerChart());

    setStep("replay_and_poll", "running");
    setStep("replay_and_poll", "passed", await replayAndPoll());

    setStep("timeseries", "running");
    const timeseries = await request(`/api/admin/drift/timeseries/${sourceId}`);
    state.eventId = firstEventId(timeseries);
    const timeseriesPointCount = seriesPointCount(timeseries);
    if (timeseriesPointCount <= 0) {
      setStep("timeseries", "failed", timeseries);
      throw new Error(
        `No timeseries points in response for sourceId=${sourceId}, assignmentId=${assignmentId}, chartId=${scenario.analysisChart.chartId}.`
      );
    }
    setStep("timeseries", state.eventId ? "passed" : "no_drift", timeseries);

    setStep("debug_counts", "running");
    const counts = await refreshCounts(scenario);
    setStep("debug_counts", "passed", counts);

    if (!state.eventId) {
      const noDrift = {
        ok: true,
        sourceId,
        assignmentId,
        chartId: scenario.analysisChart.chartId,
        reason: "No drift event was detected for this data and method combination.",
        timeseriesPointCount,
        counts: {
          rawEventCount: counts.raw.data?.count ?? 0,
          bucketCount: counts.buckets.data?.count ?? 0,
          methodRunCount: counts.runs.data?.count ?? 0,
          eventCount: counts.events.data?.count ?? 0
        }
      };
      setStep("analysis_payload", "skipped", noDrift);
      setStep("llm_interpretation", "skipped", noDrift);
      setStatus("no_drift", `${value("chartId")} + ${value("runtimeMethodKey")} completed without drift event`);
      setLatest(noDrift);
      return;
    }

    setStep("analysis_payload", "running");
    const analysis = await request(`/api/admin/drift/events/${sourceId}/${state.eventId}/analysis`);
    setStep("analysis_payload", "passed", analysis);

    setStep("llm_interpretation", "running");
    const payload = analysis.data?.chartPayload || {};
    const created = await post("/api/admin/llm/interpret/chart/jobs", {
      eventId: analysis.data?.eventId,
      sourceId: analysis.data?.sourceId,
      analysisChartId: analysis.data?.analysisChartId,
      chartId: analysis.data?.chartId,
      payload,
      question: "이 drift event analysis chart를 한국어로 요약하고 해석상 주의점을 설명해 주세요."
    });
    const job = await pollLlmJob(created.jobId);
    setStep("llm_interpretation", job.status === "succeeded" ? "passed" : "failed", job);
    if (job.status !== "succeeded") throw new Error("LLM job did not succeed");

    setStatus("passed", `eventId=${state.eventId}`);
  } catch (error) {
    state.error = String(error);
    setStatus("failed", String(error));
    setLatest({ error: String(error), state });
  } finally {
    el("runAnchor").disabled = false;
  }
}

function bind(id, handler) {
  el(id).addEventListener("click", async () => {
    try {
      el(id).disabled = true;
      await handler();
    } catch (error) {
      state.error = String(error);
      setStatus("failed", String(error));
      setLatest({ error: String(error) });
    } finally {
      el(id).disabled = false;
    }
  });
}

bind("addConnection", addConnectionFromMenu);
bind("refreshHealth", async () => setLatest(await getHealth()));
bind("resetScenario", resetScenario);
bind("registerSource", registerSource);
bind("registerFeeder", registerFeeder);
bind("registerAdapter", registerAdapter);
bind("registerMethod", registerMethod);
bind("registerChart", registerChart);
bind("registerSelection", registerSelection);
bind("refreshChartCatalog", loadChartCatalog);
bind("runReplay", replayAndPoll);
bind("openTimeseries", async () => openTimeseriesForCurrentSource());
bind("applyTopRecommendation", async () => applyTopRecommendation());
el("runAnchor").addEventListener("click", runAnchor);
el("chartSearch").addEventListener("input", () => {
  renderChartOptions();
  updateCompatibleMethods();
  updateChartPreview();
});
el("chartId").addEventListener("change", () => {
  updateCompatibleMethods();
  updateChartPreview();
});
el("compatibleMethod").addEventListener("change", async () => {
  selectCompatibleMethod(value("compatibleMethod"));
  materializeSelectionForCurrentConnection(selectedRecommendationForPair());
});
el("chartPickerList").addEventListener("click", (event) => {
  const item = event.target.closest("[data-chart-id]");
  if (!item) return;
  selectChart(item.dataset.chartId);
});
el("methodPickerList").addEventListener("click", async (event) => {
  const item = event.target.closest("[data-method]");
  if (!item) return;
  selectCompatibleMethod(item.dataset.method);
  materializeSelectionForCurrentConnection(selectedRecommendationForPair());
});
el("recommendedAnalysisList").addEventListener("click", async (event) => {
  const item = event.target.closest("[data-apply-recommendation]");
  if (!item) return;
  const recommendation = recommendationsForConnection()[Number(item.dataset.applyRecommendation)];
  try {
    await applyRecommendation(recommendation);
  } catch (error) {
    setLatest({ recommendationApplyError: String(error) });
  }
});
el("replayProfile").addEventListener("change", () => {
  state.replayProfileId = selectedReplayProfileId();
  const sourceId = value("connectionMenu").startsWith("preset:") ? value("connectionMenu").slice("preset:".length) : "";
  const preset = state.connectionPresets.find((item) => item.source?.sourceId === sourceId);
  if (preset) {
    setLatest({ selectedReplayProfile: state.replayProfileId, preset: preset.source?.sourceId });
  }
});
["sourceId", "sourceTitle", "sourceUrl", "csvPath", "adapterId", "adapterType"].forEach((id) => {
  el(id).addEventListener("input", updateConnectionSummary);
  el(id).addEventListener("change", updateConnectionSummary);
});
el("connectionList").addEventListener("click", async (event) => {
  const item = event.target.closest("[data-connection-key]");
  if (!item) return;
  state.selectedConnectionId = item.dataset.connectionKey;
  const connection = state.connections.find((candidate) => candidate.key === state.selectedConnectionId);
  populateConnection(connection);
  try {
    await applyTopRecommendation({ auto: true });
  } catch (error) {
    setLatest({ recommendationApplyError: String(error) });
  }
});

renderSteps();
renderConnections();
setTimeseriesUrl(null);
setValue("tickDelayMs", initialTickDelayMs);
setValue("replayProfile", initialReplayProfileId);
loadChartCatalog()
  .catch((error) => setLatest({ chartCatalogError: String(error) }))
  .then(loadConnectionPresets)
  .then(getHealth)
  .then(setLatest)
  .catch((error) => setLatest({ error: String(error) }));
