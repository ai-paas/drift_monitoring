(function () {
  "use strict";

  const dataset = window.DRIFT_METRIC_YEARLY_TEST_DATA;
  const dayMs = 24 * 60 * 60 * 1000;

  function toDate(value) {
    return value instanceof Date ? value : new Date(value);
  }

  function toIsoDateTime(value) {
    if (!value) return "null";
    return toDate(value).toISOString().replace(".000Z", "Z");
  }

  function formatDate(value) {
    if (!value) return "null";
    return toIsoDateTime(value).slice(0, 10);
  }

  function rangeMs(domain) {
    return toDate(domain[1]).getTime() - toDate(domain[0]).getTime();
  }

  function addMs(value, delta) {
    return new Date(toDate(value).getTime() + delta);
  }

  function addMonths(value, months) {
    const date = toDate(value);
    return new Date(Date.UTC(date.getUTCFullYear(), date.getUTCMonth() + months, date.getUTCDate()));
  }

  function clampDomain(domain, fullDomain) {
    const fullStart = toDate(fullDomain[0]).getTime();
    const fullEnd = toDate(fullDomain[1]).getTime();
    let start = toDate(domain[0]).getTime();
    let end = toDate(domain[1]).getTime();
    const span = Math.max(end - start, dayMs);
    if (start < fullStart) {
      start = fullStart;
      end = Math.min(fullEnd, start + span);
    }
    if (end > fullEnd) {
      end = fullEnd;
      start = Math.max(fullStart, end - span);
    }
    if (start >= end) {
      start = Math.max(fullStart, end - dayMs);
    }
    return [new Date(start), new Date(end)];
  }

  function presetDomain(preset, fullDomain) {
    const fullStart = toDate(fullDomain[0]);
    const fullEnd = toDate(fullDomain[1]);
    if (preset === "ALL") return [fullStart, fullEnd];
    const spans = {
      "24H": dayMs,
      "7D": 7 * dayMs,
      "30D": 30 * dayMs,
      "3M": 92 * dayMs,
      "1Y": 365 * dayMs
    };
    return [addMs(fullEnd, -spans[preset]), fullEnd];
  }

  function resolveDisplayBucket(time) {
    if (time.scaleMode === "hour") return "1h";
    if (time.scaleMode === "day") return "1d";
    if (time.scaleMode === "month") return "1M";
    if (time.scaleMode === "year") return "1M";
    const days = rangeMs(time.visibleDomain) / dayMs;
    if (days <= 2) return "1h";
    if (days <= 90) return "1d";
    return "1M";
  }

  function resolveTickInterval(time) {
    const days = rangeMs(time.visibleDomain) / dayMs;
    if (time.scaleMode === "hour" || days <= 2) return "6h";
    if (time.scaleMode === "day" || days <= 45) return "1w";
    if (time.scaleMode === "month" || days <= 730) return "3M";
    return "1y";
  }

  function resolveLabelFormat(time) {
    const tick = time.tickInterval;
    if (tick.endsWith("h")) return "MM-dd HH:00";
    if (tick.endsWith("d") || tick.endsWith("w")) return "MM-dd";
    if (tick.endsWith("M")) return "yyyy-MM";
    return "yyyy";
  }

  function makeInitialState() {
    const fullDomain = dataset.fullDomain.map(toDate);
    return normalizeState({
      registry: {
        modelId: dataset.modelId,
        features: dataset.features
      },
      time: {
        fullDomain,
        visibleDomain: presetDomain("1Y", fullDomain),
        rangePreset: "1Y",
        scaleMode: "year",
        sourceResolution: "1M",
        displayBucket: "1M",
        tickInterval: "3M",
        labelFormat: "yyyy-MM",
        navigatorSelection: presetDomain("1Y", fullDomain),
        dataRequestKey: ""
      },
      dataStore: buildDataStore(),
      view: {
        primaryFeature: "embedding_distance",
        comparisonFeatures: [],
        panelOrder: ["embedding_distance"],
        hoverTimestamp: null,
        expanded: false
      },
      syncLog: ["INIT: yearly test data loaded"]
    });
  }

  function buildDataStore() {
    const byFeature = {};
    dataset.features.forEach((feature) => {
      byFeature[feature.featureId] = {
        series: dataset.series[feature.featureId] || [],
        events: dataset.events[feature.featureId] || [],
        sourceResolution: "1M",
        loadedDomain: dataset.fullDomain,
        status: "loaded",
        error: null
      };
    });
    return { byFeature };
  }

  function featureIds(state) {
    return state.registry.features.map((feature) => feature.featureId);
  }

  function visibleFeatureIds(state) {
    return [state.view.primaryFeature].concat(state.view.comparisonFeatures);
  }

  function normalizeState(state) {
    const next = {
      ...state,
      time: { ...state.time },
      view: { ...state.view },
      syncLog: state.syncLog.slice(-10)
    };
    const valid = featureIds(next);
    if (!valid.includes(next.view.primaryFeature)) {
      next.view.primaryFeature = valid[0] || "";
      next.syncLog.push("SYNC: invalid primary feature fallback applied");
    }
    next.view.comparisonFeatures = next.view.comparisonFeatures
      .filter((featureId) => valid.includes(featureId))
      .filter((featureId) => featureId !== next.view.primaryFeature)
      .filter((featureId, index, list) => list.indexOf(featureId) === index);

    next.time.visibleDomain = clampDomain(next.time.visibleDomain, next.time.fullDomain);
    next.time.navigatorSelection = next.time.visibleDomain;
    next.time.displayBucket = resolveDisplayBucket(next.time);
    next.time.tickInterval = resolveTickInterval(next.time);
    next.time.labelFormat = resolveLabelFormat(next.time);
    next.time.dataRequestKey = [
      toIsoDateTime(next.time.visibleDomain[0]),
      toIsoDateTime(next.time.visibleDomain[1]),
      next.time.sourceResolution
    ].join("|");
    next.view.panelOrder = visibleFeatureIds(next);
    return next;
  }

  function dispatch(action) {
    state = reducer(state, action);
    render();
  }

  function reducer(current, action) {
    const next = {
      ...current,
      time: { ...current.time },
      view: { ...current.view },
      dataStore: {
        byFeature: { ...current.dataStore.byFeature }
      },
      syncLog: current.syncLog.concat(action.type)
    };

    if (action.type === "SET_RANGE_PRESET") {
      next.time.rangePreset = action.preset;
      next.time.visibleDomain = presetDomain(action.preset, next.time.fullDomain);
    }
    if (action.type === "SET_VISIBLE_DOMAIN") {
      next.time.visibleDomain = [toDate(action.domain[0]), toDate(action.domain[1])];
      next.time.rangePreset = "CUSTOM";
    }
    if (action.type === "SET_SCALE_MODE") {
      next.time.scaleMode = action.scaleMode;
    }
    if (action.type === "SET_PRIMARY_FEATURE") {
      next.view.primaryFeature = action.featureId;
    }
    if (action.type === "PAN_BY_DELTA") {
      const span = rangeMs(next.time.visibleDomain);
      const delta = span * action.direction;
      next.time.visibleDomain = [addMs(next.time.visibleDomain[0], delta), addMs(next.time.visibleDomain[1], delta)];
      next.time.rangePreset = "CUSTOM";
    }
    if (action.type === "ADD_COMPARISON_FEATURE") {
      if (action.featureId !== next.view.primaryFeature && !next.view.comparisonFeatures.includes(action.featureId)) {
        next.view.comparisonFeatures = next.view.comparisonFeatures.concat(action.featureId);
      }
    }
    if (action.type === "REMOVE_LAST_COMPARISON_FEATURE") {
      next.view.comparisonFeatures = next.view.comparisonFeatures.slice(0, -1);
    }
    if (action.type === "SET_FEATURE_STATUS") {
      const existing = next.dataStore.byFeature[action.featureId];
      if (existing) {
        next.dataStore.byFeature[action.featureId] = {
          ...existing,
          status: action.status,
          error: action.status === "error" ? "simulated feature request error" : null
        };
      }
    }
    if (action.type === "SET_HOVER_MIDDLE") {
      const mid = toDate(next.time.visibleDomain[0]).getTime() + rangeMs(next.time.visibleDomain) / 2;
      next.view.hoverTimestamp = new Date(mid);
    }
    if (action.type === "CLEAR_HOVER") {
      next.view.hoverTimestamp = null;
    }
    if (action.type === "TOGGLE_EXPANDED") {
      next.view.expanded = !next.view.expanded;
      next.syncLog.push("SYNC: popup size would recalculate derived ticks without changing visibleDomain");
    }
    return normalizeState(next);
  }

  function overlaps(start, end, domain) {
    const left = toDate(start).getTime();
    const right = end ? toDate(end).getTime() : left;
    return right >= toDate(domain[0]).getTime() && left <= toDate(domain[1]).getTime();
  }

  function yDomain(rows) {
    const values = rows
      .filter((row) => row.status !== "missing" && row.status !== "closed")
      .map((row) => row.mean ?? row.value)
      .filter((value) => Number.isFinite(value));
    if (!values.length) return null;
    const min = Math.min(...values);
    const max = Math.max(...values);
    const pad = Math.max((max - min) * 0.12, Math.abs(max) * 0.02, 0.01);
    return [Number((min - pad).toFixed(4)), Number((max + pad).toFixed(4))];
  }

  function bucketStatus(row) {
    return row.status || "observed";
  }

  function summarizeQuality(rows) {
    const summary = {
      expectedBuckets: 0,
      observedBuckets: 0,
      missingBuckets: 0,
      closedBuckets: 0,
      imputedBuckets: 0,
      partialBuckets: 0,
      coverage: 1,
      gapCount: 0,
      segments: []
    };
    let activeSegment = null;
    rows.forEach((row) => {
      const status = bucketStatus(row);
      if (status === "observed") summary.observedBuckets += 1;
      if (status === "missing") summary.missingBuckets += 1;
      if (status === "closed") summary.closedBuckets += 1;
      if (status === "imputed") summary.imputedBuckets += 1;
      if (status === "partial") summary.partialBuckets += 1;
      if (status !== "closed") summary.expectedBuckets += 1;

      if (!activeSegment || activeSegment.type !== status) {
        activeSegment = {
          type: status,
          from: row.bucket_start,
          to: row.bucket_end || row.bucket_start
        };
        summary.segments.push(activeSegment);
      } else {
        activeSegment.to = row.bucket_end || row.bucket_start;
      }
    });
    const usable = summary.observedBuckets + summary.imputedBuckets + summary.partialBuckets;
    summary.coverage = summary.expectedBuckets ? Number((usable / summary.expectedBuckets).toFixed(3)) : 0;
    summary.gapCount = summary.segments.filter((segment) => segment.type === "missing").length;
    return summary;
  }

  function buildRenderModel(current) {
    const registryById = Object.fromEntries(current.registry.features.map((feature) => [feature.featureId, feature]));
    return visibleFeatureIds(current).map((featureId) => {
      const store = current.dataStore.byFeature[featureId];
      const series = (store?.series || []).filter((row) => overlaps(row.bucket_start, row.bucket_end, current.time.visibleDomain));
      const events = (store?.events || []).filter((event) => overlaps(event.start, event.end, current.time.visibleDomain));
      const quality = summarizeQuality(series);
      const warningCount = events.filter((event) => event.level === "warning").length;
      const driftCount = events.filter((event) => event.level === "drift").length;
      return {
        featureId,
        label: registryById[featureId]?.label || featureId,
        unit: registryById[featureId]?.unit || "",
        xDomain: current.time.visibleDomain.map(formatDate).join(" ~ "),
        yDomain: yDomain(series),
        visiblePoints: series.filter((row) => {
          const status = bucketStatus(row);
          return status !== "missing" && status !== "closed" && Number.isFinite(row.mean ?? row.value);
        }).length,
        visibleEvents: events.length,
        warningCount,
        driftCount,
        quality,
        status: store?.status || "missing",
        displayBucket: current.time.displayBucket,
        tickInterval: current.time.tickInterval
      };
    });
  }

  function jsonView(value) {
    return JSON.stringify(value, function (_key, item) {
      return item instanceof Date ? toIsoDateTime(item) : item;
    }, 2);
  }

  function render() {
    const renderModel = buildRenderModel(state);
    function dataStoreQuality(store) {
      return summarizeQuality(store.series || []);
    }
    document.getElementById("statusLine").textContent = [
      state.registry.modelId,
      `${formatDate(state.time.visibleDomain[0])} ~ ${formatDate(state.time.visibleDomain[1])}`,
      `${state.time.scaleMode} scale`,
      `${state.view.panelOrder.length} feature panel`
    ].join(" · ");

    document.getElementById("registryView").textContent = jsonView({
      modelId: state.registry.modelId,
      features: state.registry.features.map((feature) => ({
        featureId: feature.featureId,
        label: feature.label,
        unit: feature.unit
      }))
    });
    document.getElementById("timeView").textContent = jsonView(state.time);
    document.getElementById("dataStoreView").textContent = jsonView(Object.fromEntries(
      Object.entries(state.dataStore.byFeature).map(([featureId, store]) => {
        const quality = dataStoreQuality(store);
        return [featureId, {
          status: store.status,
          sourceResolution: store.sourceResolution,
          loadedDomain: store.loadedDomain,
          bucketCount: store.series.length,
          eventCount: store.events.length,
          quality: {
            coverage: quality.coverage,
            observed: quality.observedBuckets,
            missing: quality.missingBuckets,
            closed: quality.closedBuckets,
            imputed: quality.imputedBuckets,
            partial: quality.partialBuckets,
            gapCount: quality.gapCount
          },
          error: store.error
        }];
      })
    ));
    document.getElementById("viewStateView").textContent = jsonView(state.view);
    document.getElementById("syncLogView").textContent = state.syncLog.slice(-16).join("\n");
    document.getElementById("renderModelView").innerHTML = renderModel.map((panel) => `
      <section class="render-panel">
        <h3>${panel.label} <span>(${panel.featureId})</span></h3>
        <dl>
          <dt>status</dt><dd>${panel.status}</dd>
          <dt>xDomain</dt><dd>${panel.xDomain}</dd>
          <dt>yDomain</dt><dd>${panel.yDomain ? panel.yDomain.join(" ~ ") + " " + panel.unit : "none"}</dd>
          <dt>visible points</dt><dd>${panel.visiblePoints}</dd>
          <dt>coverage</dt><dd>${Math.round(panel.quality.coverage * 100)}% · expected ${panel.quality.expectedBuckets} · observed ${panel.quality.observedBuckets}</dd>
          <dt>bucket status</dt><dd>missing ${panel.quality.missingBuckets} · closed ${panel.quality.closedBuckets} · imputed ${panel.quality.imputedBuckets} · partial ${panel.quality.partialBuckets}</dd>
          <dt>gap segments</dt><dd>${panel.quality.gapCount}</dd>
          <dt>segments</dt><dd>${panel.quality.segments.map((segment) => `${segment.type}:${formatDate(segment.from)}~${formatDate(segment.to)}`).join(" | ") || "none"}</dd>
          <dt>visible events</dt><dd>${panel.visibleEvents}
            <span class="warning">warning ${panel.warningCount}</span> /
            <span class="drift">drift ${panel.driftCount}</span>
          </dd>
          <dt>shared tick</dt><dd>${panel.tickInterval}</dd>
          <dt>display bucket</dt><dd>${panel.displayBucket}</dd>
        </dl>
      </section>
    `).join("");
  }

  document.addEventListener("click", (event) => {
    const button = event.target.closest("button[data-action]");
    if (!button) return;
    const action = button.dataset.action;
    if (action === "preset") dispatch({ type: "SET_RANGE_PRESET", preset: button.dataset.value });
    if (action === "scale") dispatch({ type: "SET_SCALE_MODE", scaleMode: button.dataset.value });
    if (action === "pan") dispatch({ type: "PAN_BY_DELTA", direction: Number(button.dataset.value) });
    if (action === "add-feature") dispatch({ type: "ADD_COMPARISON_FEATURE", featureId: button.dataset.value });
    if (action === "remove-last") dispatch({ type: "REMOVE_LAST_COMPARISON_FEATURE" });
    if (action === "status") dispatch({ type: "SET_FEATURE_STATUS", featureId: button.dataset.feature, status: button.dataset.value });
    if (action === "hover") dispatch({ type: "SET_HOVER_MIDDLE" });
    if (action === "clear-hover") dispatch({ type: "CLEAR_HOVER" });
    if (action === "expanded") dispatch({ type: "TOGGLE_EXPANDED" });
  });

  let state = makeInitialState();
  // @managed-contract contract_id=drift_metric_timeseries.harness_window_api level=P1
  window.driftMetricTimeseriesHarness = {
    dispatch,
    getState: () => state,
    buildRenderModel: () => buildRenderModel(state)
  };
  render();
})();
