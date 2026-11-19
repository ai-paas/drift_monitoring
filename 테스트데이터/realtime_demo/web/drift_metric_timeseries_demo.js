(function () {
  "use strict";

  const dataset = window.DRIFT_METRIC_YEARLY_TEST_DATA;
  const query = new URLSearchParams(window.location.search);
  const liveEnabled = query.get("live") !== "0";
  const livePollMs = 5000;
  const dayMs = 24 * 60 * 60 * 1000;
  const rangePresets = ["24H", "7D", "30D", "3M", "1Y", "ALL"];
  const scaleModes = ["auto", "hour", "day", "month", "year"];
  const maxHourRangeMs = 7 * dayMs;
  const labels = {
    "24H": "24시간",
    "7D": "7일",
    "30D": "30일",
    "3M": "3개월",
    "1Y": "1년",
    ALL: "전체",
    auto: "자동",
    hour: "시간",
    day: "일",
    month: "월",
    year: "연"
  };
  const maxRenderedPoints = 1600;
  const interpretationJobEndpoint = "http://127.0.0.1:8767/api/interpret/chart/jobs";
  const analysisInterpretationQuestion = "이 분석 chart가 보여주는 상세한 드리프트 내용을 chart component별 그래프 근거와 함께 설명해줘.";

  const els = {};
  let state = makeInitialState();
  let navigatorDrag = null;
  let livePollTimer = null;
  let analysisRequestId = 0;
  let activeAnalysisChartNote = null;
  const analysisInterpretationCache = new Map();
  const analysisInterpretationRequests = new Map();

  function toDate(value) {
    return value instanceof Date ? value : new Date(value);
  }

  function toMs(value) {
    return toDate(value).getTime();
  }

  function iso(value) {
    return toDate(value).toISOString();
  }

  function formatDate(value) {
    return iso(value).slice(0, 10);
  }

  function formatDateTime(value) {
    return iso(value).replace(".000Z", "Z").replace("T", " ").slice(0, 16);
  }

  function directRangeEndDate(value) {
    return addMs(`${value}T00:00:00Z`, dayMs);
  }

  function dateInputEndValue(time) {
    if (time.rangePreset !== "CUSTOM") return formatDate(time.visibleDomain[1]);
    const end = toDate(time.visibleDomain[1]);
    if (
      end.getUTCHours() === 0 &&
      end.getUTCMinutes() === 0 &&
      end.getUTCSeconds() === 0 &&
      end.getUTCMilliseconds() === 0
    ) {
      return formatDate(addMs(end, -dayMs));
    }
    return formatDate(end);
  }

  function formatVisibleDomainEnd(time) {
    if (time.rangePreset !== "CUSTOM") return formatDateTime(time.visibleDomain[1]);
    const end = toDate(time.visibleDomain[1]);
    if (
      end.getUTCHours() === 0 &&
      end.getUTCMinutes() === 0 &&
      end.getUTCSeconds() === 0 &&
      end.getUTCMilliseconds() === 0
    ) {
      return `${dateInputEndValue(time)} 23:59`;
    }
    return formatDateTime(end);
  }

  function daysIn(domain) {
    return (toMs(domain[1]) - toMs(domain[0])) / dayMs;
  }

  function addMs(value, delta) {
    return new Date(toMs(value) + delta);
  }

  function addMonths(value, deltaMonths) {
    const date = toDate(value);
    return new Date(Date.UTC(date.getUTCFullYear(), date.getUTCMonth() + deltaMonths, date.getUTCDate()));
  }

  function startOfUtcDay(value) {
    const date = toDate(value);
    return new Date(Date.UTC(date.getUTCFullYear(), date.getUTCMonth(), date.getUTCDate()));
  }

  function startOfUtcWeek(value) {
    const date = startOfUtcDay(value);
    const day = date.getUTCDay();
    const offset = day === 0 ? -6 : 1 - day;
    return addMs(date, offset * dayMs);
  }

  function startOfUtcMonth(value) {
    const date = toDate(value);
    return new Date(Date.UTC(date.getUTCFullYear(), date.getUTCMonth(), 1));
  }

  function startOfUtcYear(value) {
    const date = toDate(value);
    return new Date(Date.UTC(date.getUTCFullYear(), 0, 1));
  }

  function clampDomain(domain, fullDomain) {
    const fullStart = toMs(fullDomain[0]);
    const fullEnd = toMs(fullDomain[1]);
    let start = toMs(domain[0]);
    let end = toMs(domain[1]);
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

  function clampDate(value, fullDomain) {
    return new Date(Math.max(toMs(fullDomain[0]), Math.min(toMs(value), toMs(fullDomain[1]))));
  }

  function presetSpan(preset) {
    const spans = {
      "24H": dayMs,
      "7D": 7 * dayMs,
      "30D": 30 * dayMs
    };
    return spans[preset] || null;
  }

  function presetExceedsHourLimit(preset) {
    if (preset === "24H" || preset === "7D") return false;
    return true;
  }

  function currentRangeExceedsHourLimit(time) {
    return toMs(time.visibleDomain[1]) - toMs(time.visibleDomain[0]) > maxHourRangeMs;
  }

  function presetDomain(preset, fullDomain, anchorStart = null) {
    const fullStart = toDate(fullDomain[0]);
    const fullEnd = toDate(fullDomain[1]);
    if (preset === "ALL") return [fullStart, fullEnd];
    let start = anchorStart ? clampDate(anchorStart, fullDomain) : fullStart;
    if (toMs(start) >= toMs(fullEnd)) start = addMs(fullEnd, -dayMs);
    let end = addMs(start, presetSpan(preset) || dayMs);
    if (preset === "3M") end = addMonths(start, 3);
    if (preset === "1Y") end = addMonths(start, 12);
    if (toMs(end) > toMs(fullEnd)) end = fullEnd;
    return [start, end];
  }

  function presetDomainEndingAt(preset, fullDomain, endValue, fallbackDomain) {
    const fullStart = toDate(fullDomain[0]);
    const fullEnd = toDate(fullDomain[1]);
    const end = clampDate(endValue || fullEnd, fullDomain);
    if (preset === "ALL") return [fullStart, end];
    if (preset === "3M") return clampDomain([addMonths(end, -3), end], fullDomain);
    if (preset === "1Y") return clampDomain([addMonths(end, -12), end], fullDomain);
    if (preset === "CUSTOM" && Array.isArray(fallbackDomain)) {
      const span = Math.max(toMs(fallbackDomain[1]) - toMs(fallbackDomain[0]), dayMs);
      return clampDomain([addMs(end, -span), end], fullDomain);
    }
    return clampDomain([addMs(end, -(presetSpan(preset) || 30 * dayMs)), end], fullDomain);
  }

  function resolveDisplayBucket(time) {
    if (time.scaleMode === "hour") return "1h";
    return "1d";
  }

  function resolveTickInterval(time) {
    const days = daysIn(time.visibleDomain);
    if (time.scaleMode === "hour") return days <= 2 ? "6h" : "1d";
    if (days <= 2) return "6h";
    if (time.scaleMode === "day") {
      return days <= 45 ? "1d" : "1w";
    }
    if (days <= 10) return "1d";
    if (days <= 45) return "1w";
    if (time.scaleMode === "month" || days <= 125) return "1M";
    if (days <= 730) return "3M";
    return "1y";
  }

  function resolveLabelFormat(time) {
    const tick = time.tickInterval;
    if (tick.endsWith("h")) return "MM-dd HH";
    if (tick.endsWith("d") || tick.endsWith("w")) return "MM-dd";
    if (tick.endsWith("M")) return "yyyy-MM";
    return "yyyy";
  }

  function tickContextLabel(time) {
    const tick = time.tickInterval;
    if (time.displayBucket === "1h" && tick === "1d") return "시간 데이터 · 일 구분선";
    if (tick.endsWith("h")) return "시간 데이터 · 6시간 구분선";
    if (tick === "1d") return "일 평균 데이터 · 일 구분선";
    if (tick === "1w") return "일 평균 데이터 · 주 구분선";
    if (tick === "1M") return "일 평균 데이터 · 월 구분선";
    if (tick === "3M") return "일 평균 데이터 · 분기 구분선";
    return "일 평균 데이터 · 연 구분선";
  }

  function chartWidthForTime(time) {
    const baseWidth = 1160;
    const days = daysIn(time.visibleDomain);
    if (time.scaleMode === "hour") {
      return Math.max(baseWidth, Math.ceil(days * 24 * 16));
    }
    if (time.scaleMode === "day") {
      return Math.max(baseWidth, Math.ceil(days * 24));
    }
    return baseWidth;
  }

  function makeInitialState() {
    const sourceDomain = dataset.fullDomain.map(toDate);
    const fullDomain = liveEnabled ? [sourceDomain[0], addMs(sourceDomain[0], dayMs)] : sourceDomain;
    const anchorDate = liveEnabled ? fullDomain[0] : addMonths(fullDomain[1], -12);
    const initialDomain = liveEnabled
      ? [fullDomain[0], addMs(fullDomain[0], dayMs)]
      : presetDomain("1Y", fullDomain, anchorDate);
    return normalizeState({
      registry: {
        modelId: dataset.modelId,
        features: dataset.features
      },
      time: {
        fullDomain,
        rangeAnchorDate: anchorDate,
        visibleDomain: initialDomain,
        rangePreset: liveEnabled ? "30D" : "1Y",
        scaleMode: "auto",
        sourceResolution: "1h",
        displayBucket: "1d",
        tickInterval: "3M",
        labelFormat: "yyyy-MM",
        navigatorSelection: initialDomain
      },
      dataStore: buildDataStore(),
      view: {
        primaryFeature: "embedding_distance",
        comparisonFeatures: [],
        panelOrder: ["embedding_distance"],
        hoverTimestamp: null,
        selectedEventKey: null,
        directRangeDraft: null,
        live: {
          enabled: liveEnabled,
          follow: liveEnabled,
          daysLoaded: liveEnabled ? 0 : null,
          lastDayEnd: null,
          status: liveEnabled ? "connecting" : "static",
          error: null,
          done: false
        }
      }
    });
  }

  function buildDataStore() {
    const byFeature = {};
    dataset.features.forEach((feature) => {
      if (liveEnabled) {
        byFeature[feature.featureId] = {
          series: [],
          seriesByResolution: { "1h": [], "1d": [] },
          events: [],
          sourceResolution: "1h",
          loadedDomain: [dataset.fullDomain[0], dataset.fullDomain[0]],
          status: "loading",
          error: null
        };
        return;
      }
      const byResolution = dataset.seriesByResolution?.[feature.featureId] || {};
      const dailySummary = byResolution["1d"] || dataset.series[feature.featureId] || [];
      byFeature[feature.featureId] = {
        series: dailySummary,
        seriesByResolution: byResolution,
        events: dataset.events[feature.featureId] || [],
        sourceResolution: "1h",
        loadedDomain: dataset.fullDomain,
        status: "loaded",
        error: null
      };
    });
    return { byFeature };
  }

  function seriesForDisplayBucket(store, bucket) {
    const byResolution = store?.seriesByResolution || {};
    if (byResolution[bucket]) return byResolution[bucket];
    return store?.series || [];
  }

  function mergeRows(existing, incoming) {
    const byKey = new Map();
    existing.concat(incoming || []).forEach((row) => {
      const key = [row.feature_id || row.featureId || "", row.resolution || "", row.bucket_start || ""].join("|");
      byKey.set(key, row);
    });
    return Array.from(byKey.values()).sort((a, b) => toMs(a.bucket_start) - toMs(b.bucket_start));
  }

  function mergeEvents(existing, incoming, featureId) {
    const byKey = new Map();
    existing.concat(incoming || []).forEach((event) => {
      const key = eventKey({ ...event, feature_id: featureId });
      byKey.set(key, event);
    });
    return Array.from(byKey.values()).sort((a, b) => toMs(a.start) - toMs(b.start));
  }

  function decimateSeries(rows, maxPoints) {
    if (rows.length <= maxPoints) return rows;
    const step = Math.ceil(rows.length / maxPoints);
    const result = [];
    for (let index = 0; index < rows.length; index += step) {
      const group = rows.slice(index, index + step);
      const valueRows = group.filter((row) => {
        const status = statusOf(row);
        return status !== "missing" && status !== "closed" && Number.isFinite(valueOf(row));
      });
      if (!valueRows.length) {
        result.push(group[0]);
        continue;
      }
      const count = valueRows.reduce((sum, row) => sum + (row.count || 0), 0);
      const weight = valueRows.reduce((sum, row) => sum + (row.count || 1), 0);
      const weightedSum = valueRows.reduce((sum, row) => sum + valueOf(row) * (row.count || 1), 0);
      result.push({
        ...valueRows[Math.floor(valueRows.length / 2)],
        bucket_start: group[0].bucket_start,
        bucket_end: group[group.length - 1].bucket_end || group[group.length - 1].bucket_start,
        count,
        mean: Number((weightedSum / Math.max(weight, 1)).toFixed(4)),
        min: Math.min(...valueRows.map((row) => row.min ?? valueOf(row))),
        max: Math.max(...valueRows.map((row) => row.max ?? valueOf(row))),
        status: valueRows.length < group.length ? "partial" : statusOf(valueRows[Math.floor(valueRows.length / 2)]),
        coverage: valueRows.length / group.length
      });
    }
    return result;
  }

  function featureIds(current) {
    return current.registry.features.map((feature) => feature.featureId);
  }

  function visibleFeatureIds(current) {
    return [current.view.primaryFeature].concat(current.view.comparisonFeatures);
  }

  function disableLiveFollow(next) {
    if (!next.view.live?.enabled) return;
    next.view.live = {
      ...next.view.live,
      follow: false
    };
  }

  function keepLiveFollowAtLatest(next) {
    if (!next.view.live?.enabled) return;
    next.view.live = {
      ...next.view.live,
      follow: true
    };
    next.time.visibleDomain = presetDomainEndingAt(next.time.rangePreset, next.time.fullDomain, next.time.fullDomain[1], next.time.visibleDomain);
    next.time.rangeAnchorDate = next.time.visibleDomain[0];
  }

  function normalizeState(input) {
    const next = {
      ...input,
      time: { ...input.time },
      view: { ...input.view }
    };
    const valid = featureIds(next);
    if (!valid.includes(next.view.primaryFeature)) next.view.primaryFeature = valid[0] || "";
    next.view.comparisonFeatures = next.view.comparisonFeatures
      .filter((featureId) => valid.includes(featureId))
      .filter((featureId) => featureId !== next.view.primaryFeature)
      .filter((featureId, index, list) => list.indexOf(featureId) === index)
      .slice(0, 5);
    next.time.visibleDomain = clampDomain(next.time.visibleDomain, next.time.fullDomain);
    if (next.time.scaleMode === "hour" && toMs(next.time.visibleDomain[1]) - toMs(next.time.visibleDomain[0]) > maxHourRangeMs) {
      const start = next.time.visibleDomain[0];
      next.time.visibleDomain = clampDomain([start, addMs(start, maxHourRangeMs)], next.time.fullDomain);
      next.time.rangePreset = next.time.rangePreset === "24H" || next.time.rangePreset === "7D" ? next.time.rangePreset : "CUSTOM";
    }
    next.time.rangeAnchorDate = clampDate(next.time.rangeAnchorDate || next.time.fullDomain[0], next.time.fullDomain);
    next.time.navigatorSelection = next.time.visibleDomain;
    next.time.displayBucket = resolveDisplayBucket(next.time);
    next.time.tickInterval = resolveTickInterval(next.time);
    next.time.labelFormat = resolveLabelFormat(next.time);
    next.view.panelOrder = visibleFeatureIds(next);
    return next;
  }

  function dispatch(action) {
    const next = {
      ...state,
      time: { ...state.time },
      view: { ...state.view },
      dataStore: { byFeature: { ...state.dataStore.byFeature } }
    };
    if (action.type === "SET_RANGE_PRESET") {
      next.time.rangePreset = action.preset;
      next.time.rangeAnchorDate = action.anchorStart ? toDate(action.anchorStart) : next.time.rangeAnchorDate;
      if (next.view.live?.enabled) {
        next.view.live = { ...next.view.live, follow: true };
        next.time.visibleDomain = presetDomainEndingAt(action.preset, next.time.fullDomain, next.time.fullDomain[1], next.time.visibleDomain);
        next.time.rangeAnchorDate = next.time.visibleDomain[0];
      } else {
        next.time.visibleDomain = presetDomain(action.preset, next.time.fullDomain, next.time.rangeAnchorDate);
      }
    }
    if (action.type === "SET_VISIBLE_DOMAIN") {
      disableLiveFollow(next);
      next.time.rangePreset = "CUSTOM";
      next.time.visibleDomain = [toDate(action.domain[0]), toDate(action.domain[1])];
      if (action.directRangeDraft) next.view.directRangeDraft = action.directRangeDraft;
      if (!action.directRangeDraft) next.view.directRangeDraft = null;
      if (action.resetScaleMode) next.time.scaleMode = "auto";
      next.view.selectedEventKey = action.selectedEventKey || null;
    }
    if (action.type === "FOCUS_EVENT_DOMAIN") {
      if (next.view.live?.enabled) {
        next.view.live = {
          ...next.view.live,
          follow: true
        };
      }
      next.time.rangePreset = "CUSTOM";
      next.time.visibleDomain = [toDate(action.domain[0]), toDate(action.domain[1])];
      next.time.rangeAnchorDate = next.time.visibleDomain[0];
      next.view.directRangeDraft = null;
      next.view.selectedEventKey = action.selectedEventKey || null;
    }
    if (action.type === "SET_RANGE_PRESET") {
      next.view.directRangeDraft = null;
    }
    if (action.type === "SET_SCALE_MODE") {
      next.time.scaleMode = action.scaleMode;
      keepLiveFollowAtLatest(next);
    }
    if (action.type === "SET_PRIMARY_FEATURE") {
      next.view.primaryFeature = action.featureId;
      keepLiveFollowAtLatest(next);
    }
    if (action.type === "ADD_COMPARISON_FEATURE") {
      if (action.featureId !== next.view.primaryFeature && !next.view.comparisonFeatures.includes(action.featureId)) {
        next.view.comparisonFeatures = next.view.comparisonFeatures.concat(action.featureId);
      }
      keepLiveFollowAtLatest(next);
    }
    if (action.type === "REMOVE_COMPARISON_FEATURE") {
      next.view.comparisonFeatures = next.view.comparisonFeatures.filter((featureId) => featureId !== action.featureId);
      keepLiveFollowAtLatest(next);
    }
    if (action.type === "LIVE_DATA_LOADED") {
      const payload = action.payload || {};
      if (Array.isArray(payload.features) && payload.features.length) {
        next.registry = {
          ...next.registry,
          features: payload.features
        };
      }
      if (Array.isArray(payload.fullDomain) && payload.fullDomain.length === 2) {
        next.time.fullDomain = payload.fullDomain.map(toDate);
      }
      next.view.live = {
        ...(next.view.live || {}),
        enabled: true,
        follow: next.view.live?.follow !== false,
        daysLoaded: payload.cursor ?? next.view.live?.daysLoaded ?? 0,
        lastDayEnd: payload.dayEnd || next.view.live?.lastDayEnd || null,
        status: payload.done ? "done" : "live",
        error: null,
        done: Boolean(payload.done)
      };
      if (payload.seriesByResolution) {
        Object.entries(payload.seriesByResolution).forEach(([featureId, byResolution]) => {
          const existing = next.dataStore.byFeature[featureId] || {
            series: [],
            seriesByResolution: {},
            events: [],
            sourceResolution: "1h",
            loadedDomain: payload.loadedDomain || payload.fullDomain,
            status: "loaded",
            error: null
          };
          const mergedByResolution = { ...(existing.seriesByResolution || {}) };
          Object.entries(byResolution || {}).forEach(([resolution, rows]) => {
            mergedByResolution[resolution] = mergeRows(mergedByResolution[resolution] || [], rows || []);
          });
          next.dataStore.byFeature[featureId] = {
            ...existing,
            series: mergeRows(existing.series || [], payload.series?.[featureId] || mergedByResolution["1d"] || []),
            seriesByResolution: mergedByResolution,
            events: mergeEvents(existing.events || [], payload.events?.[featureId] || [], featureId),
            loadedDomain: payload.loadedDomain || existing.loadedDomain,
            status: "loaded",
            error: null
          };
        });
      }
      if (payload.dayEnd && next.view.live?.follow !== false) {
        const end = toDate(payload.dayEnd);
        next.time.visibleDomain = presetDomainEndingAt(next.time.rangePreset, next.time.fullDomain, end, state.time.visibleDomain);
        next.time.rangeAnchorDate = next.time.visibleDomain[0];
        next.view.directRangeDraft = null;
      }
    }
    if (action.type === "LIVE_DATA_ERROR") {
      next.view.live = {
        ...(next.view.live || {}),
        enabled: true,
        status: "error",
        error: action.error || "live data request failed"
      };
    }
    if (action.type === "SET_HOVER_TIMESTAMP") {
      next.view.hoverTimestamp = action.timestamp;
    }
    if (action.type === "SET_SELECTED_EVENT") {
      next.view.selectedEventKey = action.eventKey || null;
      keepLiveFollowAtLatest(next);
    }
    state = normalizeState(next);
    render();
  }

  function eventCenter(event) {
    const start = toMs(event.start);
    const end = event.end ? toMs(event.end) : start;
    return new Date(start + Math.max(0, end - start) / 2);
  }

  function domainCenteredAtWithSpan(center, span) {
    return [addMs(center, -span / 2), addMs(center, span / 2)];
  }

  function eventFocusSpan(event) {
    const eventSpan = Math.max(event.end ? toMs(event.end) - toMs(event.start) : 0, dayMs);
    if (eventSpan <= dayMs) return 7 * dayMs;
    if (eventSpan <= 7 * dayMs) return 14 * dayMs;
    return 30 * dayMs;
  }

  function eventFocusDomain(event, fullDomain) {
    const eventStart = toDate(event.start);
    const eventEnd = toDate(event.end || addMs(eventStart, dayMs));
    let start = clampDate(eventStart, fullDomain);
    let end = clampDate(eventEnd, fullDomain);
    if (toMs(end) <= toMs(start)) end = clampDate(addMs(start, dayMs), fullDomain);
    const span = toMs(end) - toMs(start);
    const minSpan = Math.min(7 * dayMs, Math.max(dayMs, toMs(fullDomain[1]) - toMs(fullDomain[0])));
    if (span < minSpan) {
      const center = new Date((toMs(start) + toMs(end)) / 2);
      start = addMs(center, -minSpan / 2);
      end = addMs(center, minSpan / 2);
    }
    return clampDomain([start, end], fullDomain);
  }

  function eventKey(event) {
    return [event.feature_id || event.featureId || "", event.level || "", event.start || "", event.end || "", event.label || ""].join("|");
  }

  function allVisibleEvents(current) {
    const registry = metaById(current);
    return visibleFeatureIds(current)
      .flatMap((featureId) => {
        const store = current.dataStore.byFeature[featureId];
        return (store?.events || []).map((event) => ({
          ...event,
          featureId,
          featureLabel: registry[featureId]?.label || featureId,
          key: eventKey({ ...event, feature_id: featureId })
        }));
      })
      .sort((a, b) => toMs(a.start) - toMs(b.start) || String(a.featureLabel).localeCompare(String(b.featureLabel)));
  }

  function jumpToEvent(eventKeyValue) {
    const event = allVisibleEvents(state).find((item) => item.key === eventKeyValue);
    if (!event) return;
    dispatch({
      type: "FOCUS_EVENT_DOMAIN",
      domain: eventFocusDomain(event, state.time.fullDomain),
      selectedEventKey: event.key
    });
  }

  function statusOf(row) {
    return row.status || "observed";
  }

  function overlaps(start, end, domain) {
    const left = toMs(start);
    const right = end ? toMs(end) : left;
    return right > toMs(domain[0]) && left < toMs(domain[1]);
  }

  function valueOf(row) {
    return row.mean ?? row.value;
  }

  function rowPlotDate(row, domain) {
    const bucketStart = toMs(row.bucket_start);
    const bucketEnd = toMs(row.bucket_end || row.bucket_start);
    const visibleStart = toMs(domain[0]);
    const visibleEnd = toMs(domain[1]);
    if (bucketEnd > visibleStart && bucketStart < visibleEnd) {
      const clippedStart = Math.max(bucketStart, visibleStart);
      const clippedEnd = Math.min(bucketEnd, visibleEnd);
      return new Date(clippedStart + Math.max(0, clippedEnd - clippedStart) / 2);
    }
    return row.bucket_start;
  }

  function yDomain(rows) {
    const values = rows
      .filter((row) => statusOf(row) !== "missing" && statusOf(row) !== "closed")
      .map(valueOf)
      .filter((value) => Number.isFinite(value));
    if (!values.length) return null;
    const min = Math.min(...values);
    const max = Math.max(...values);
    const pad = Math.max((max - min) * 0.12, Math.abs(max) * 0.02, 0.01);
    return [min - pad, max + pad];
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
    let active = null;
    rows.forEach((row) => {
      const status = statusOf(row);
      if (status === "observed") summary.observedBuckets += 1;
      if (status === "missing") summary.missingBuckets += 1;
      if (status === "closed") summary.closedBuckets += 1;
      if (status === "imputed") summary.imputedBuckets += 1;
      if (status === "partial") summary.partialBuckets += 1;
      if (status !== "closed") summary.expectedBuckets += 1;
      if (!active || active.type !== status) {
        active = { type: status, from: row.bucket_start, to: row.bucket_end || row.bucket_start };
        summary.segments.push(active);
      } else {
        active.to = row.bucket_end || row.bucket_start;
      }
    });
    const usable = summary.observedBuckets + summary.imputedBuckets + summary.partialBuckets;
    summary.coverage = summary.expectedBuckets ? usable / summary.expectedBuckets : 0;
    summary.gapCount = summary.segments.filter((segment) => segment.type === "missing").length;
    return summary;
  }

  function metaById(current) {
    return Object.fromEntries(current.registry.features.map((feature) => [feature.featureId, feature]));
  }

  function buildRenderModel(current) {
    const registry = metaById(current);
    return visibleFeatureIds(current).map((featureId) => {
      const store = current.dataStore.byFeature[featureId];
      const selectedSeries = seriesForDisplayBucket(store, current.time.displayBucket);
      const visibleSeries = selectedSeries.filter((row) => overlaps(row.bucket_start, row.bucket_end, current.time.visibleDomain));
      const series = decimateSeries(visibleSeries, maxRenderedPoints);
      const events = (store?.events || []).filter((event) => overlaps(event.start, event.end, current.time.visibleDomain));
      const quality = summarizeQuality(series);
      const warningCount = events.filter((event) => event.level === "warning").length;
      const driftCount = events.filter((event) => event.level === "drift").length;
      return {
        featureId,
        feature: registry[featureId],
        series,
        events,
        yDomain: yDomain(series),
        quality,
        warningCount,
        driftCount,
        status: store?.status || "missing"
      };
    });
  }

  function xScale(domain, left, width) {
    const start = toMs(domain[0]);
    const span = Math.max(toMs(domain[1]) - start, 1);
    return (value) => left + ((toMs(value) - start) / span) * width;
  }

  function yScale(domain, top, height) {
    if (!domain) return () => top + height / 2;
    const span = Math.max(domain[1] - domain[0], 0.000001);
    return (value) => top + height - ((value - domain[0]) / span) * height;
  }

  function maxTicksForWidth(width) {
    return Math.max(12, Math.floor(width / 88));
  }

  function ticksForTime(time, width = 1160) {
    const [start, end] = time.visibleDomain.map(toDate);
    const result = [];
    const tick = time.tickInterval;
    const maxTicks = maxTicksForWidth(width);
    if (tick === "1M" || tick === "3M" || tick === "1y") {
      const stepMonths = tick === "1M" ? 1 : tick === "3M" ? 3 : 12;
      let cursor = tick === "1y" ? startOfUtcYear(start) : startOfUtcMonth(start);
      if (toMs(cursor) < toMs(start)) cursor = addMonths(cursor, stepMonths);
      result.push(start);
      while (toMs(cursor) < toMs(end)) {
        if (toMs(cursor) > toMs(start)) result.push(cursor);
        cursor = addMonths(cursor, stepMonths);
        if (result.length > maxTicks) break;
      }
      if (toMs(result[result.length - 1]) !== toMs(end)) result.push(end);
      return result;
    }
    const step = tick === "6h" ? 6 * 60 * 60 * 1000 : tick === "1w" ? 7 * dayMs : dayMs;
    let cursor = tick === "1w" ? startOfUtcWeek(start) : startOfUtcDay(start);
    if (tick === "6h") {
      cursor = new Date(Math.floor(toMs(start) / step) * step);
    }
    if (toMs(cursor) < toMs(start)) cursor = addMs(cursor, step);
    result.push(start);
    for (let t = toMs(cursor); t < toMs(end); t += step) {
      if (t > toMs(start)) result.push(new Date(t));
      if (result.length > maxTicks) break;
    }
    if (!result.length || toMs(result[result.length - 1]) < toMs(end)) result.push(end);
    return result;
  }

  function formatTick(date, format) {
    const year = date.getUTCFullYear();
    const month = String(date.getUTCMonth() + 1).padStart(2, "0");
    const day = String(date.getUTCDate()).padStart(2, "0");
    const hour = String(date.getUTCHours()).padStart(2, "0");
    if (format === "yyyy") return String(year);
    if (format === "yyyy-MM") return `${year}-${month}`;
    if (format === "MM-dd") return `${month}-${day}`;
    return `${month}-${day} ${hour}`;
  }

  function readableTicks(ticks, x, minGap = 58) {
    if (ticks.length <= 2) return ticks;
    const result = [ticks[0]];
    for (let index = 1; index < ticks.length - 1; index += 1) {
      const previous = result[result.length - 1];
      const next = ticks[index + 1];
      if (x(ticks[index]) - x(previous) >= minGap && x(next) - x(ticks[index]) >= minGap) {
        result.push(ticks[index]);
      }
    }
    const last = ticks[ticks.length - 1];
    if (x(last) - x(result[result.length - 1]) >= minGap) {
      result.push(last);
    } else if (result.length > 1) {
      result[result.length - 1] = last;
    }
    return result;
  }

  function mergeDuplicateTickLabels(ticks, format, x, minGap = 90) {
    return ticks.reduce((result, tick) => {
      const previous = result[result.length - 1];
      if (previous && formatTick(previous, format) === formatTick(tick, format) && x(tick) - x(previous) < minGap) {
        result[result.length - 1] = tick;
      } else {
        result.push(tick);
      }
      return result;
    }, []);
  }

  function plottableRows(rows) {
    return rows.filter((row) => {
      const status = statusOf(row);
      return status !== "missing" && status !== "closed" && Number.isFinite(valueOf(row));
    });
  }

  function linePath(rows, x, y, domain, options = {}) {
    const breakStatuses = new Set(options.breakStatuses || ["missing", "closed"]);
    let path = "";
    let open = false;
    rows.forEach((row) => {
      const status = statusOf(row);
      const value = valueOf(row);
      if (breakStatuses.has(status) || !Number.isFinite(value)) {
        open = false;
        return;
      }
      const command = open ? "L" : "M";
      path += `${command}${x(rowPlotDate(row, domain)).toFixed(2)},${y(value).toFixed(2)} `;
      open = true;
    });
    return path.trim();
  }

  function singleBucketSegmentPath(row, x, y, domain) {
    const value = valueOf(row);
    if (!Number.isFinite(value)) return "";
    const left = Math.max(toMs(row.bucket_start), toMs(domain[0]));
    const right = Math.min(toMs(row.bucket_end || row.bucket_start), toMs(domain[1]));
    if (right <= left) return "";
    const yValue = y(value).toFixed(2);
    return `M${x(new Date(left)).toFixed(2)},${yValue} L${x(new Date(right)).toFixed(2)},${yValue}`;
  }

  function imputedPath(rows, x, y, domain) {
    const paths = [];
    let index = 0;
    while (index < rows.length) {
      if (statusOf(rows[index]) !== "imputed" || !Number.isFinite(valueOf(rows[index]))) {
        index += 1;
        continue;
      }

      const segment = [];
      const previous = rows[index - 1];
      if (previous && !["missing", "closed", "imputed"].includes(statusOf(previous)) && Number.isFinite(valueOf(previous))) {
        segment.push(previous);
      }
      while (index < rows.length && statusOf(rows[index]) === "imputed" && Number.isFinite(valueOf(rows[index]))) {
        segment.push(rows[index]);
        index += 1;
      }
      const next = rows[index];
      if (next && !["missing", "closed", "imputed"].includes(statusOf(next)) && Number.isFinite(valueOf(next))) {
        segment.push(next);
      }
      if (segment.length >= 2) {
        paths.push(linePath(segment, x, y, domain, { breakStatuses: ["missing", "closed"] }));
      } else if (segment.length === 1) {
        paths.push(singleBucketSegmentPath(segment[0], x, y, domain));
      }
    }
    return paths.filter(Boolean).join(" ");
  }

  function escapeHtml(value) {
    return String(value ?? "").replace(/[&<>"']/g, (char) => ({
      "&": "&amp;",
      "<": "&lt;",
      ">": "&gt;",
      '"': "&quot;",
      "'": "&#39;"
    }[char]));
  }

  function renderPanel(panel, options = {}) {
    const width = options.width || chartWidthForTime(state.time);
    const height = options.height || 306;
    const clipId = `plotClip-${panel.featureId}-${width}-${height}`.replace(/[^a-zA-Z0-9_-]/g, "-");
    const missingPatternId = `${clipId}-missingPattern`;
    const closedPatternId = `${clipId}-closedPattern`;
    const margin = { top: 18, right: 26, bottom: 34, left: 72 };
    const plotW = width - margin.left - margin.right;
    const plotH = height - margin.top - margin.bottom;
    const x = xScale(state.time.visibleDomain, margin.left, plotW);
    const y = yScale(panel.yDomain, margin.top, plotH);
    const ticks = mergeDuplicateTickLabels(readableTicks(ticksForTime(state.time, width), x), state.time.labelFormat, x);
    const yTicks = panel.yDomain ? [panel.yDomain[0], (panel.yDomain[0] + panel.yDomain[1]) / 2, panel.yDomain[1]] : [];
    const hoverX = state.view.hoverTimestamp ? x(state.view.hoverTimestamp) : null;
    const eventFrame = (event) => {
      const x1 = Math.max(margin.left, x(event.start));
      const x2 = Math.min(width - margin.right, x(event.end || event.start));
      return {
        x1,
        x2,
        width: Math.max(3, x2 - x1)
      };
    };
    const eventBands = panel.events.map((event) => {
      const frame = eventFrame(event);
      const key = eventKey({ ...event, feature_id: panel.featureId });
      return `<rect class="event ${event.level}" data-event-key="${escapeHtml(key)}" x="${frame.x1.toFixed(2)}" y="${margin.top}" width="${frame.width.toFixed(2)}" height="${plotH}"><title>${escapeHtml(event.label || event.level)}</title></rect>`;
    }).join("");
    const selectedEventOverlay = panel.events
      .filter((event) => eventKey({ ...event, feature_id: panel.featureId }) === state.view.selectedEventKey)
      .map((event) => {
        const frame = eventFrame(event);
        const focusX = frame.x1;
        const focusWidth = frame.width;
        const centerX = Math.max(margin.left, Math.min(width - margin.right, focusX + focusWidth / 2));
        const label = event.label || event.level || "event";
        const labelX = Math.max(margin.left + 38, Math.min(centerX, width - margin.right - 38));
        return `
          <g class="selected-event-focus">
            <rect class="event selected" x="${focusX.toFixed(2)}" y="${margin.top}" width="${focusWidth.toFixed(2)}" height="${plotH}"></rect>
            <line class="event-boundary" x1="${centerX.toFixed(2)}" x2="${centerX.toFixed(2)}" y1="${margin.top}" y2="${height - margin.bottom}"></line>
            <text class="event-focus-label" x="${labelX.toFixed(2)}" y="${(margin.top + 18).toFixed(2)}" text-anchor="middle">${escapeHtml(label)}</text>
          </g>
        `;
      }).join("");
    const statusBands = panel.quality.segments
      .filter((segment) => segment.type === "missing" || segment.type === "closed")
      .map((segment) => {
        const x1 = x(segment.from);
        const x2 = x(segment.to);
        const width = Math.max(2, x2 - x1);
        const label = segment.type === "missing" ? "\uACB0\uCE21" : "\uBE44\uC6B4\uC601";
        const patternId = segment.type === "missing" ? missingPatternId : closedPatternId;
        const labelX = Math.max(margin.left + 18, Math.min(width / 2 + x1, margin.left + plotW - 18));
        const labelText = width >= 34
          ? `<text class="band-label ${segment.type}" x="${labelX.toFixed(2)}" y="${(margin.top + 22).toFixed(2)}" text-anchor="middle">${label}</text>`
          : "";
        return `<rect class="band ${segment.type}" fill="url(#${patternId})" x="${x1.toFixed(2)}" y="${margin.top}" width="${width.toFixed(2)}" height="${plotH}"></rect>${labelText}`;
      }).join("");
    const grid = yTicks.map((tick) => `<line class="grid-line" x1="${margin.left}" x2="${width - margin.right}" y1="${y(tick)}" y2="${y(tick)}"></line>`).join("");
    const yLabels = yTicks.map((tick) => `<text class="tick-label" x="${margin.left - 9}" y="${y(tick) + 4}" text-anchor="end">${formatNumber(tick)}</text>`).join("");
    const xLabels = ticks.map((tick, index) => {
      const tx = x(tick);
      const anchor = index === 0 ? "start" : index === ticks.length - 1 ? "end" : "middle";
      return `<g><line class="x-grid-line" x1="${tx}" x2="${tx}" y1="${margin.top}" y2="${height - margin.bottom}"></line><text class="tick-label" x="${tx}" y="${height - 11}" text-anchor="${anchor}">${formatTick(tick, state.time.labelFormat)}</text></g>`;
    }).join("");
    const validRows = plottableRows(panel.series);
    const lineClass = state.time.displayBucket === "1h" ? "series-line hourly" : "series-line";
    const solidRows = panel.series.filter((row) => !["missing", "closed", "imputed"].includes(statusOf(row)) && Number.isFinite(valueOf(row)));
    const path = solidRows.length <= 1
      ? ""
      : linePath(panel.series, x, y, state.time.visibleDomain, { breakStatuses: ["missing", "closed", "imputed"] });
    const specialPath = imputedPath(panel.series, x, y, state.time.visibleDomain);
    const sparseObservedMarkers = validRows.length <= 12 ? validRows.filter((row) => statusOf(row) === "observed") : [];
    const markerRows = panel.series
      .filter((row) => ["partial", "imputed"].includes(statusOf(row)) && Number.isFinite(valueOf(row)))
      .concat(sparseObservedMarkers);
    const markers = markerRows.map((row) => {
      const status = statusOf(row);
      return `<circle class="marker ${status}" cx="${x(rowPlotDate(row, state.time.visibleDomain)).toFixed(2)}" cy="${y(valueOf(row)).toFixed(2)}" r="${status === "partial" ? 4 : 3.5}"><title>${status}: ${formatDate(row.bucket_start)}</title></circle>`;
    }).join("");
    const empty = validRows.length === 0 ? `<text class="empty-message" x="${width / 2}" y="${height / 2}" text-anchor="middle">현재 범위에 관측 데이터가 없습니다</text>` : "";
    return `
      <svg class="chart-svg" viewBox="0 0 ${width} ${height}" style="width:${width}px;min-width:${width}px" data-feature-id="${panel.featureId}" role="img" aria-label="${escapeHtml(panel.feature?.label || panel.featureId)} 시계열">
        <defs>
          <clipPath id="${clipId}">
            <rect x="${margin.left}" y="${margin.top}" width="${plotW}" height="${plotH}"></rect>
          </clipPath>
          <pattern id="${missingPatternId}" width="8" height="8" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
            <rect width="8" height="8" class="pattern-missing-bg"></rect>
            <line class="pattern-missing-line" x1="0" y1="0" x2="0" y2="8"></line>
          </pattern>
          <pattern id="${closedPatternId}" width="8" height="8" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
            <rect width="8" height="8" class="pattern-closed-bg"></rect>
            <line class="pattern-closed-line" x1="0" y1="0" x2="0" y2="8"></line>
          </pattern>
        </defs>
        ${grid}
        ${xLabels}
        ${yLabels}
        <line class="axis-line" x1="${margin.left}" x2="${width - margin.right}" y1="${height - margin.bottom}" y2="${height - margin.bottom}"></line>
        <line class="axis-line" x1="${margin.left}" x2="${margin.left}" y1="${margin.top}" y2="${height - margin.bottom}"></line>
        <g clip-path="url(#${clipId})">
          ${eventBands}
          ${statusBands}
          ${selectedEventOverlay}
          ${path ? `<path class="${lineClass}" d="${path}"></path>` : ""}
          ${specialPath ? `<path class="series-line imputed" d="${specialPath}"></path>` : ""}
          ${markers}
          ${hoverX ? `<line class="hover-line" x1="${hoverX.toFixed(2)}" x2="${hoverX.toFixed(2)}" y1="${margin.top}" y2="${height - margin.bottom}"></line>` : ""}
        </g>
        <g class="axis-context">
          <rect class="axis-context-bg" x="${margin.left + 5}" y="${margin.top + 2}" width="212" height="18" rx="4"></rect>
          <text class="axis-context-label" x="${margin.left + 13}" y="${margin.top + 15}" text-anchor="start">${tickContextLabel(state.time)}</text>
        </g>
        ${empty}
        <rect class="hit-area" x="${margin.left}" y="${margin.top}" width="${plotW}" height="${plotH}" fill="transparent" data-feature-id="${panel.featureId}"></rect>
      </svg>
    `;
  }

  function formatNumber(value) {
    if (!Number.isFinite(value)) return "";
    if (Math.abs(value) >= 100) return String(Math.round(value));
    return value.toFixed(3).replace(/0+$/, "").replace(/\.$/, "");
  }

  function panelHtml(panel, options = {}) {
    const q = panel.quality;
    return `
      <article class="feature-panel" data-feature-id="${panel.featureId}">
        <header class="panel-head">
          <div>
            <h3 class="panel-title">${escapeHtml(panel.feature?.label || panel.featureId)}</h3>
            <div class="panel-meta">${escapeHtml(panel.featureId)} · ${escapeHtml(panel.feature?.unit || "")} · ${panel.status}</div>
          </div>
          <div class="quality">
            <span><strong>${Math.round(q.coverage * 100)}%</strong> coverage</span>
            <span>missing ${q.missingBuckets}</span>
            <span>closed ${q.closedBuckets}</span>
            <span>imputed ${q.imputedBuckets}</span>
            <span>partial ${q.partialBuckets}</span>
            <span>warning ${panel.warningCount}</span>
            <span>drift ${panel.driftCount}</span>
          </div>
        </header>
        ${renderPanel(panel, options)}
      </article>
    `;
  }

  function navigatorDomain() {
    return state.time.fullDomain;
  }

  function renderNavigator(renderModel) {
    const width = 1160;
    const height = 78;
    const clipId = "navigatorClip";
    const margin = { left: 62, right: 24, top: 16, bottom: 20 };
    const plotW = width - margin.left - margin.right;
    const full = navigatorDomain();
    const x = xScale(full, margin.left, plotW);
    const primary = renderModel[0];
    const fullPrimarySeries = primary
      ? seriesForDisplayBucket(state.dataStore.byFeature[primary.featureId], "1M")
          .concat(seriesForDisplayBucket(state.dataStore.byFeature[primary.featureId], "1d"))
          .filter((row, index, list) => list.findIndex((item) => item.bucket_start === row.bucket_start && item.resolution === row.resolution) === index)
          .filter((row) => overlaps(row.bucket_start, row.bucket_end, full))
      : [];
    const yDomainNav = primary ? yDomain(fullPrimarySeries.filter((row) => statusOf(row) !== "missing" && statusOf(row) !== "closed")) : null;
    const y = yScale(yDomainNav, margin.top, height - margin.top - margin.bottom);
    const line = primary ? linePath(fullPrimarySeries, x, y, full) : "";
    const visibleInNav = [
      new Date(Math.max(toMs(state.time.visibleDomain[0]), toMs(full[0]))),
      new Date(Math.min(toMs(state.time.visibleDomain[1]), toMs(full[1])))
    ];
    const hasVisibleOverlap = toMs(visibleInNav[1]) > toMs(visibleInNav[0]);
    const selX = hasVisibleOverlap ? x(visibleInNav[0]) : x(full[1]);
    const selW = hasVisibleOverlap ? Math.max(3, x(visibleInNav[1]) - selX) : 3;
    const compactSelection = selW > 180;
    const thumbW = compactSelection ? 96 : selW;
    const thumbX = compactSelection
      ? Math.max(margin.left, Math.min(selX + selW / 2 - thumbW / 2, width - margin.right - thumbW))
      : selX;
    const selectionMarkup = compactSelection
      ? `
          <rect class="navigator-selection compact" x="${thumbX.toFixed(2)}" y="${margin.top}" width="${thumbW.toFixed(2)}" height="${height - margin.top - margin.bottom}"></rect>
        `
      : `<rect class="navigator-selection" x="${thumbX.toFixed(2)}" y="${margin.top}" width="${thumbW.toFixed(2)}" height="${height - margin.top - margin.bottom}"></rect>`;
    els.navigator.innerHTML = `
      <svg viewBox="0 0 ${width} ${height}" role="img" aria-label="전체 기간 미니맵">
        <defs>
          <clipPath id="${clipId}">
            <rect x="${margin.left}" y="${margin.top}" width="${plotW}" height="${height - margin.top - margin.bottom}"></rect>
          </clipPath>
        </defs>
        <rect class="navigator-track" x="${margin.left}" y="${margin.top}" width="${plotW}" height="${height - margin.top - margin.bottom}"></rect>
        <g clip-path="url(#${clipId})">
          ${line ? `<path class="series-line" d="${line}"></path>` : ""}
          ${selectionMarkup}
        </g>
        <rect class="navigator-hit" x="${margin.left}" y="${margin.top}" width="${plotW}" height="${height - margin.top - margin.bottom}"></rect>
        <text class="tick-label" x="${margin.left}" y="${height - 4}" text-anchor="start">${formatDate(full[0])}</text>
        <text class="tick-label" x="${width - margin.right}" y="${height - 4}" text-anchor="end">${formatDate(full[1])}</text>
      </svg>
    `;
    bindNavigator();
  }

  function summaryText(renderModel) {
    const totals = renderModel.reduce((acc, panel) => {
      acc.warning += panel.warningCount;
      acc.drift += panel.driftCount;
      acc.missing += panel.quality.missingBuckets;
      acc.closed += panel.quality.closedBuckets;
      acc.imputed += panel.quality.imputedBuckets;
      acc.partial += panel.quality.partialBuckets;
      acc.expected += panel.quality.expectedBuckets;
      acc.usable += panel.quality.observedBuckets + panel.quality.imputedBuckets + panel.quality.partialBuckets;
      return acc;
    }, { warning: 0, drift: 0, missing: 0, closed: 0, imputed: 0, partial: 0, expected: 0, usable: 0 });
    const coverage = totals.expected ? Math.round((totals.usable / totals.expected) * 100) : 0;
    const hourLimit = state.time.scaleMode === "hour" ? " · 시간 축 최대 7일" : "";
    const live = state.view.live?.enabled
      ? ` · live ${state.view.live.status}${state.view.live.daysLoaded !== null ? ` ${state.view.live.daysLoaded}일` : ""}${state.view.live.follow === false ? " · 화면 고정" : ""}${state.view.live.error ? ` · ${state.view.live.error}` : ""}`
      : "";
    return `${formatDateTime(state.time.visibleDomain[0])} ~ ${formatVisibleDomainEnd(state.time)} · ${labels[state.time.scaleMode]} 축 · ${state.time.displayBucket} 평균${hourLimit} · coverage ${coverage}% · warning ${totals.warning} / drift ${totals.drift} · missing ${totals.missing} · closed ${totals.closed} · imputed ${totals.imputed} · partial ${totals.partial}${live}`;
  }

  function render() {
    const renderModel = buildRenderModel(state);
    els.stateSummary.textContent = summaryText(renderModel);
    syncControls();
    renderChips();
    renderEventList();
    els.panelStack.innerHTML = renderModel.map((panel) => panelHtml(panel)).join("");
    renderNavigator(renderModel);
    bindSvgHover(els.panelStack);
  }

  async function requestJson(url, options = {}) {
    const response = await fetch(url, {
      cache: "no-store",
      ...options
    });
    if (!response.ok) throw new Error(`${response.status} ${response.statusText}`);
    return response.json();
  }

  function sleep(ms) {
    return new Promise((resolve) => window.setTimeout(resolve, ms));
  }

  function noteText(note) {
    if (!note) return "";
    return [note.title, note.summary, note.detail].filter(Boolean).join("\n\n");
  }

  function splitSentences(text) {
    return String(text || "")
      .replace(/\s+/g, " ")
      .split(/(?<=[.!?。！？다]\.)\s+|(?<=다\.)\s+|(?<=다)\s+(?=[가-힣A-Z0-9])/)
      .map((item) => item.trim())
      .filter(Boolean);
  }

  function formattedChartNoteText(note) {
    if (!note) return "";
    const summary = String(note.summary || "").trim();
    const detail = String(note.detail || "").trim();
    const sentences = splitSentences(detail);
    const evidence = sentences.filter((sentence) => /좌측|우측|현재 데이터|정확도|accuracy|timeline|tree size|t=/.test(sentence));
    const reading = sentences.filter((sentence) => /판독|따라서|해석할 수|후보/.test(sentence));
    const caution = sentences.filter((sentence) => /다만|추가|확인|단정/.test(sentence));
    const intro = sentences.filter((sentence) => !evidence.includes(sentence) && !reading.includes(sentence) && !caution.includes(sentence));
    const sections = [];
    sections.push(note.title || "전체 해석");
    if (summary) sections.push(`요약\n- ${summary}`);
    if (intro.length) sections.push(`차트 목적\n${intro.slice(0, 2).map((item) => `- ${item}`).join("\n")}`);
    if (evidence.length) sections.push(`주요 근거\n${evidence.slice(0, 5).map((item) => `- ${item}`).join("\n")}`);
    if (reading.length) sections.push(`판독\n${reading.slice(0, 2).map((item) => `- ${item}`).join("\n")}`);
    if (caution.length) sections.push(`주의 및 추가 확인\n${caution.slice(0, 3).map((item) => `- ${item}`).join("\n")}`);
    return sections.filter(Boolean).join("\n\n");
  }

  function analysisInterpretationCacheKey(payload) {
    return JSON.stringify({
      chartId: payload?.chartId || "",
      title: payload?.title || "",
      data: payload?.data || {},
      question: analysisInterpretationQuestion
    });
  }

  function applyAnalysisInterpretation(payload, interpretation, pendingText = "") {
    const chartNote = interpretation?.chartNote || (pendingText ? { title: "해석", summary: pendingText, detail: "" } : null);
    const componentNotes = new Map((interpretation?.componentNotes || []).map((note) => [note.componentInstanceId, note]));
    const components = (payload.components || []).map((component) => ({
      ...component,
      interpretationNote: null
    }));
    const data = { ...(payload.data || {}) };
    if (chartNote) {
      components
        .filter((component) => component.componentType === "decision_card" && component.config?.card_style === "notes_legend")
        .forEach((component) => {
          const source = component.dataBinding?.source;
          if (!source) return;
          const currentNote = Array.isArray(data[source]) && data[source].length ? data[source][0] : {};
          data[source] = [{
            ...currentNote,
            title: chartNote.title || currentNote.title || "해석",
            text: noteText(chartNote) || currentNote.text || "",
            legend: Array.isArray(currentNote.legend) ? currentNote.legend : []
          }];
        });
    }
    const layout = payload.layout
      ? {
        ...payload.layout,
        areas: (payload.layout.areas || []).map((area) => {
          if (!area.description) return { ...area };
          const areaNotes = components
            .filter((component) => component.area === area.area && component.componentType !== "decision_card")
            .map((component) => componentNotes.get(component.componentInstanceId))
            .filter(Boolean);
          const description = areaNotes.length ? areaNotes.map(noteText).filter(Boolean).join("\n\n") : noteText(chartNote);
          return {
            ...area,
            description,
            noteLabel: description ? "해석" : ""
          };
        })
      }
      : payload.layout;
    return {
      ...payload,
      data,
      components,
      layout,
      interpretation: interpretation || (chartNote ? { chartNote, componentNotes: [] } : payload.interpretation)
    };
  }

  async function createAndPollAnalysisInterpretation(payload, cacheKey) {
    const createResponse = await fetch(interpretationJobEndpoint, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ payload, question: analysisInterpretationQuestion })
    });
    if (!createResponse.ok) throw new Error(`해석 서버 ${createResponse.status}`);
    let job = await createResponse.json();
    if (!job.ok) throw new Error(job.error || "해석 job 생성 실패");
    for (let attempt = 0; attempt < 90; attempt += 1) {
      if (job.status === "succeeded") {
        const result = job.result;
        if (!result?.ok) throw new Error(result?.error || "해석 결과 오류");
        analysisInterpretationCache.set(cacheKey, result);
        return result;
      }
      if (job.status === "failed") throw new Error(job.error || "해석 실패");
      await sleep(Math.min(1000 + attempt * 250, 3000));
      const pollResponse = await fetch(`${interpretationJobEndpoint}/${encodeURIComponent(job.jobId)}`);
      if (!pollResponse.ok) throw new Error(`해석 poll ${pollResponse.status}`);
      job = await pollResponse.json();
      if (!job.ok) throw new Error(job.error || "해석 poll 실패");
    }
    throw new Error("해석 job timeout");
  }

  async function fetchAnalysisInterpretation(payload) {
    if (!payload?.chartId) return null;
    const cacheKey = analysisInterpretationCacheKey(payload);
    if (analysisInterpretationCache.has(cacheKey)) return analysisInterpretationCache.get(cacheKey);
    if (analysisInterpretationRequests.has(cacheKey)) return analysisInterpretationRequests.get(cacheKey);
    const request = createAndPollAnalysisInterpretation(payload, cacheKey)
      .finally(() => {
        analysisInterpretationRequests.delete(cacheKey);
      });
    analysisInterpretationRequests.set(cacheKey, request);
    return request;
  }

  async function pollLiveDay() {
    if (!state.view.live?.enabled || state.view.live.done) return;
    try {
      const payload = await requestJson("/api/drift-metric-timeseries/live/next-day");
      if (!payload.ok) throw new Error(payload.error || "live data request failed");
      dispatch({ type: "LIVE_DATA_LOADED", payload });
    } catch (error) {
      dispatch({ type: "LIVE_DATA_ERROR", error: error.message || String(error) });
    }
  }

  async function startLivePolling() {
    if (!liveEnabled) return;
    try {
      await requestJson("/api/drift-metric-timeseries/live/reset", { method: "POST" });
    } catch (error) {
      dispatch({ type: "LIVE_DATA_ERROR", error: error.message || String(error) });
      return;
    }
    await pollLiveDay();
    livePollTimer = window.setInterval(pollLiveDay, livePollMs);
  }

  function renderEventList() {
    const events = allVisibleEvents(state);
    if (!events.length) {
      els.eventList.innerHTML = `<div class="event-empty">표시 중인 feature의 이벤트가 없습니다.</div>`;
      return;
    }
    els.eventList.innerHTML = events.map((event) => {
      const selected = event.key === state.view.selectedEventKey;
      const inRange = overlaps(event.start, event.end, state.time.visibleDomain);
      const period = `${formatDate(event.start)} ~ ${formatDate(event.end || event.start)}`;
      const score = Number.isFinite(event.score) ? ` · score ${formatNumber(event.score)}` : "";
      return `
        <article class="event-item ${escapeHtml(event.level || "warning")} ${selected ? "active" : ""} ${inRange ? "in-range" : ""}" data-event-key="${escapeHtml(event.key)}">
          <button class="event-jump" type="button" data-event-key="${escapeHtml(event.key)}">
          <span class="event-title">${escapeHtml(event.label || event.level || "event")}</span>
          <span class="event-feature">${escapeHtml(event.featureLabel)}</span>
          <span class="event-meta">${escapeHtml(event.level || "event")} · ${period}${score}</span>
          </button>
          <button class="event-analysis-link" type="button" data-analysis-event-key="${escapeHtml(event.key)}">분석 차트 보기</button>
        </article>
      `;
    }).join("");
  }

  function setAnalysisStatus(message) {
    if (els.analysisStatus) els.analysisStatus.textContent = message || "";
  }

  function setAnalysisInterpretationState(status) {
    const stateName = status || "idle";
    if (els.analysisChart) {
      els.analysisChart.classList.toggle("interpretation-pending", stateName === "pending");
      els.analysisChart.classList.toggle("interpretation-ready", stateName === "ready");
      els.analysisChart.classList.toggle("interpretation-failed", stateName === "failed");
    }
    if (!els.analysisChartNote) return;
    if (stateName === "idle") {
      els.analysisChartNote.hidden = true;
      els.analysisChartNote.disabled = true;
      els.analysisChartNote.textContent = "전체 해석";
      els.analysisChartNote.dataset.state = "idle";
      return;
    }
    els.analysisChartNote.hidden = false;
    els.analysisChartNote.disabled = stateName !== "ready";
    els.analysisChartNote.dataset.state = stateName;
    els.analysisChartNote.textContent = stateName === "pending"
      ? "전체 해석 준비 중"
      : stateName === "failed"
        ? "해석 실패"
        : "전체 해석";
  }

  async function showEventAnalysis(eventKeyValue) {
    const selected = allVisibleEvents(state).find((item) => item.key === eventKeyValue);
    if (!selected || !els.analysisPanel || !els.analysisChart) return;
    dispatch({ type: "SET_SELECTED_EVENT", eventKey: eventKeyValue });
    const requestId = ++analysisRequestId;
    els.analysisPanel.hidden = false;
    els.analysisChart.innerHTML = "";
    activeAnalysisChartNote = null;
    setAnalysisInterpretationState("idle");
    if (els.analysisTitle) {
      els.analysisTitle.textContent = `${selected.featureLabel || selected.featureId} - ${formatDate(selected.start)} 분석`;
    }
    setAnalysisStatus("분석 차트 데이터를 요청하는 중입니다.");
    try {
      const params = new URLSearchParams({
        featureId: selected.featureId,
        start: iso(selected.start),
        knownEnd: iso(state.time.fullDomain[1])
      });
      const response = await requestJson(`/api/drift-metric-timeseries/events/analyze?${params.toString()}`);
      if (requestId !== analysisRequestId) return;
      if (!response.ok) throw new Error(response.error || "analysis request failed");
      if (!window.ChartRuntime?.renderChartPayload) throw new Error("chart runtime is not loaded");
      const rawPayload = response.payload;
      setAnalysisInterpretationState("pending");
      window.ChartRuntime.renderChartPayload(els.analysisChart, applyAnalysisInterpretation(rawPayload, null, "LLM 해석을 생성하는 중입니다."));
      setAnalysisStatus("해석 서비스에 분석 chart를 전달했습니다.");
      const interpretation = await fetchAnalysisInterpretation(rawPayload);
      if (requestId !== analysisRequestId) return;
      activeAnalysisChartNote = interpretation?.chartNote || null;
      setAnalysisInterpretationState(activeAnalysisChartNote ? "ready" : "failed");
      window.ChartRuntime.renderChartPayload(els.analysisChart, applyAnalysisInterpretation(rawPayload, interpretation));
      setAnalysisStatus(`${rawPayload?.title || "분석 차트"} · ${interpretation?.chartNote?.provider || "rule"} 해석`);
    } catch (error) {
      if (requestId !== analysisRequestId) return;
      els.analysisChart.innerHTML = "";
      activeAnalysisChartNote = null;
      setAnalysisInterpretationState("failed");
      setAnalysisStatus(`분석 차트를 만들 수 없습니다: ${error.message || String(error)}`);
    }
  }

  function renderChips() {
    const registry = metaById(state);
    const chips = [`<span class="chip primary">${escapeHtml(registry[state.view.primaryFeature]?.label || state.view.primaryFeature)} · 기준</span>`]
      .concat(state.view.comparisonFeatures.map((featureId) => `
        <span class="chip">${escapeHtml(registry[featureId]?.label || featureId)}
          <button type="button" data-remove-feature="${featureId}" title="비교 feature 제거">×</button>
        </span>
      `));
    els.featureChips.innerHTML = chips.join("");
  }

  function syncControls() {
    const active = document.activeElement;
    els.primaryFeature.value = state.view.primaryFeature;
    els.comparisonFeature.innerHTML = state.registry.features
      .filter((feature) => feature.featureId !== state.view.primaryFeature && !state.view.comparisonFeatures.includes(feature.featureId))
      .map((feature) => `<option value="${feature.featureId}">${escapeHtml(feature.label)}</option>`)
      .join("");
    els.anchorDate.value = formatDate(state.time.rangeAnchorDate);
    const draft = state.view.directRangeDraft;
    if (active !== els.fromDate) els.fromDate.value = draft?.from || formatDate(state.time.visibleDomain[0]);
    if (active !== els.toDate) els.toDate.value = draft?.to || dateInputEndValue(state.time);
    els.rangeButtons.querySelectorAll("button").forEach((button) => button.classList.toggle("active", button.dataset.value === state.time.rangePreset));
    els.rangeButtons.querySelectorAll("button").forEach((button) => {
      const disabled = state.time.scaleMode === "hour" && presetExceedsHourLimit(button.dataset.value);
      button.disabled = disabled;
      button.title = disabled ? "시간 축에서는 최대 7일까지만 볼 수 있습니다" : "";
    });
    els.scaleButtons.querySelectorAll("button").forEach((button) => {
      const disabled = button.dataset.value === "hour" && currentRangeExceedsHourLimit(state.time);
      button.disabled = disabled;
      button.title = disabled ? "시간 스케일은 최대 7일 범위에서만 선택할 수 있습니다" : "";
      button.classList.toggle("active", button.dataset.value === state.time.scaleMode);
    });
  }

  function nearestRow(panel, timestamp) {
    let best = null;
    let bestDelta = Infinity;
    panel.series.forEach((row) => {
      if (statusOf(row) === "missing" || statusOf(row) === "closed") return;
      const delta = Math.abs(toMs(rowPlotDate(row, state.time.visibleDomain)) - timestamp);
      if (delta < bestDelta) {
        best = row;
        bestDelta = delta;
      }
    });
    return best;
  }

  function showTooltip(event, panel, row) {
    if (!row) {
      els.tooltip.hidden = true;
      return;
    }
    const status = statusOf(row);
    const events = panel.events.filter((item) => overlaps(item.start, item.end, [row.bucket_start, row.bucket_end || row.bucket_start]));
    els.tooltip.innerHTML = `
      <h4>${escapeHtml(panel.feature?.label || panel.featureId)}</h4>
      <div>${formatDate(row.bucket_start)} ~ ${formatDate(row.bucket_end || row.bucket_start)}</div>
      <div>값: ${Number.isFinite(valueOf(row)) ? formatNumber(valueOf(row)) : "없음"} ${escapeHtml(panel.feature?.unit || "")}</div>
      <div>상태: ${status} · coverage ${Math.round((row.coverage ?? 1) * 100)}%</div>
      <div>count: ${row.count ?? 0}</div>
      ${events.length ? `<div>event: ${events.map((item) => `${item.level} ${item.score ?? ""}`).join(", ")}</div>` : ""}
      ${row.reason ? `<div>${escapeHtml(row.reason)}</div>` : ""}
    `;
    els.tooltip.hidden = false;
    els.tooltip.style.left = `${Math.min(window.innerWidth - 300, event.clientX + 14)}px`;
    els.tooltip.style.top = `${Math.min(window.innerHeight - 160, event.clientY + 14)}px`;
  }

  function bindSvgHover(root) {
    root.querySelectorAll(".chart-svg").forEach((svg) => {
      svg.onmousemove = (event) => {
        const rect = svg.getBoundingClientRect();
        const viewBox = svg.viewBox?.baseVal;
        const width = viewBox?.width || 1160;
        const viewX = ((event.clientX - rect.left) / rect.width) * width;
        const x0 = 72;
        const x1 = width - 26;
        const ratio = Math.max(0, Math.min(1, (viewX - x0) / (x1 - x0)));
        const timestamp = new Date(toMs(state.time.visibleDomain[0]) + ratio * (toMs(state.time.visibleDomain[1]) - toMs(state.time.visibleDomain[0])));
        const featureId = svg.dataset.featureId;
        const panel = buildRenderModel(state).find((item) => item.featureId === featureId);
        const row = panel ? nearestRow(panel, toMs(timestamp)) : null;
        dispatch({ type: "SET_HOVER_TIMESTAMP", timestamp });
        if (panel) showTooltip(event, panel, row);
      };
      svg.onmouseleave = () => {
        els.tooltip.hidden = true;
        dispatch({ type: "SET_HOVER_TIMESTAMP", timestamp: null });
      };
    });
  }

  function initControls() {
    els.primaryFeature.innerHTML = dataset.features.map((feature) => `<option value="${feature.featureId}">${escapeHtml(feature.label)}</option>`).join("");
    els.rangeButtons.innerHTML = rangePresets.map((preset) => `<button type="button" data-value="${preset}">${labels[preset]}</button>`).join("");
    els.scaleButtons.innerHTML = scaleModes.map((scale) => `<button type="button" data-value="${scale}">${labels[scale]}</button>`).join("");
    els.anchorDate.value = formatDate(state.time.rangeAnchorDate);

    els.primaryFeature.addEventListener("change", () => dispatch({ type: "SET_PRIMARY_FEATURE", featureId: els.primaryFeature.value }));
    els.addComparison.addEventListener("click", () => {
      if (els.comparisonFeature.value) dispatch({ type: "ADD_COMPARISON_FEATURE", featureId: els.comparisonFeature.value });
    });
    els.rangeButtons.addEventListener("click", (event) => {
      const button = event.target.closest("button[data-value]");
      if (button) {
        if (button.disabled) return;
        const anchorStart = els.anchorDate.value ? `${els.anchorDate.value}T00:00:00Z` : null;
        dispatch({ type: "SET_RANGE_PRESET", preset: button.dataset.value, anchorStart });
      }
    });
    els.scaleButtons.addEventListener("click", (event) => {
      const button = event.target.closest("button[data-value]");
      if (button) {
        if (button.disabled) return;
        dispatch({ type: "SET_SCALE_MODE", scaleMode: button.dataset.value });
      }
    });
    const applyDirectDateRange = () => {
      if (!els.fromDate.value || !els.toDate.value) return;
      els.applyDateRange.focus();
      dispatch({
        type: "SET_VISIBLE_DOMAIN",
        domain: [`${els.fromDate.value}T00:00:00Z`, directRangeEndDate(els.toDate.value)],
        directRangeDraft: { from: els.fromDate.value, to: els.toDate.value },
        resetScaleMode: true
      });
    };
    els.applyDateRange.addEventListener("click", applyDirectDateRange);
    els.latestAnchor.addEventListener("click", () => {
      const span = toMs(state.time.visibleDomain[1]) - toMs(state.time.visibleDomain[0]);
      els.anchorDate.value = formatDate(addMs(state.time.fullDomain[1], -span));
      if (state.time.rangePreset !== "CUSTOM") {
        dispatch({ type: "SET_RANGE_PRESET", preset: state.time.rangePreset, anchorStart: `${els.anchorDate.value}T00:00:00Z` });
      }
    });
    els.featureChips.addEventListener("click", (event) => {
      const button = event.target.closest("[data-remove-feature]");
      if (button) dispatch({ type: "REMOVE_COMPARISON_FEATURE", featureId: button.dataset.removeFeature });
    });
    els.eventList.addEventListener("click", (event) => {
      const analysisButton = event.target.closest("[data-analysis-event-key]");
      if (analysisButton) {
        showEventAnalysis(analysisButton.dataset.analysisEventKey);
        return;
      }
      const button = event.target.closest("[data-event-key]");
      if (button) jumpToEvent(button.dataset.eventKey);
    });
    if (els.analysisChartNote) {
      els.analysisChartNote.addEventListener("click", () => {
        if (!activeAnalysisChartNote || !window.ChartRuntime?.showNotePopup) return;
        window.ChartRuntime.showNotePopup(formattedChartNoteText(activeAnalysisChartNote));
      });
    }
    els.closeAnalysis.addEventListener("click", () => {
      els.analysisPanel.hidden = true;
      els.analysisChart.innerHTML = "";
      activeAnalysisChartNote = null;
      setAnalysisInterpretationState("idle");
      setAnalysisStatus("");
    });
    els.analysisPanel.addEventListener("click", (event) => {
      if (event.target === els.analysisPanel) {
        els.analysisPanel.hidden = true;
        els.analysisChart.innerHTML = "";
        activeAnalysisChartNote = null;
        setAnalysisInterpretationState("idle");
        setAnalysisStatus("");
      }
    });
    document.addEventListener("keydown", (event) => {
      if (event.key === "Escape" && !els.analysisPanel.hidden) {
        els.analysisPanel.hidden = true;
        els.analysisChart.innerHTML = "";
        activeAnalysisChartNote = null;
        setAnalysisInterpretationState("idle");
        setAnalysisStatus("");
      }
    });
    els.openConfig.addEventListener("click", () => {
      els.configDialog.hidden = false;
    });
    els.closeConfig.addEventListener("click", () => {
      els.configDialog.hidden = true;
    });
    els.configDialog.addEventListener("click", (event) => {
      if (event.target === els.configDialog) els.configDialog.hidden = true;
    });
  }

  function domainCenteredAt(center) {
    const span = toMs(state.time.visibleDomain[1]) - toMs(state.time.visibleDomain[0]);
    return [addMs(center, -span / 2), addMs(center, span / 2)];
  }

  function dateFromNavigatorEvent(event, svg) {
    const rect = svg.getBoundingClientRect();
    const viewX = ((event.clientX - rect.left) / rect.width) * 1160;
    const left = 62;
    const right = 1160 - 24;
    const ratio = Math.max(0, Math.min(1, (viewX - left) / (right - left)));
    const domain = navigatorDomain();
    const start = toMs(domain[0]);
    const end = toMs(domain[1]);
    return new Date(start + ratio * (end - start));
  }

  function navigatorSelectionFrame(domain) {
    const width = 1160;
    const margin = { left: 62, right: 24 };
    const plotW = width - margin.left - margin.right;
    const navDomain = navigatorDomain();
    const x = xScale(navDomain, margin.left, plotW);
    const x1 = x(domain[0]);
    const x2 = x(domain[1]);
    return { x: x1, width: Math.max(3, x2 - x1) };
  }

  function previewNavigatorSelection(domain) {
    const selection = els.navigator.querySelector(".navigator-selection");
    if (!selection) return;
    const frame = navigatorSelectionFrame(clampDomain(domain, navigatorDomain()));
    const compact = selection.classList.contains("compact");
    const width = compact ? 96 : frame.width;
    const x = compact
      ? Math.max(62, Math.min(frame.x + frame.width / 2 - width / 2, 1160 - 24 - width))
      : frame.x;
    selection.setAttribute("x", x.toFixed(2));
    selection.setAttribute("width", width.toFixed(2));
  }

  function bindNavigator() {
    const svg = els.navigator.querySelector("svg");
    if (!svg) return;
    svg.onpointerdown = (event) => {
      event.preventDefault();
      svg.setPointerCapture(event.pointerId);
      const pendingDomain = domainCenteredAt(dateFromNavigatorEvent(event, svg));
      navigatorDrag = {
        pointerId: event.pointerId,
        svg,
        moved: false,
        pendingDomain
      };
      previewNavigatorSelection(pendingDomain);
    };
    svg.onpointermove = (event) => {
      if (!navigatorDrag || navigatorDrag.pointerId !== event.pointerId) return;
      navigatorDrag.pendingDomain = domainCenteredAt(dateFromNavigatorEvent(event, navigatorDrag.svg));
      navigatorDrag.moved = true;
      previewNavigatorSelection(navigatorDrag.pendingDomain);
    };
    svg.onpointerup = (event) => {
      if (navigatorDrag && navigatorDrag.pointerId === event.pointerId) {
        const pendingDomain = navigatorDrag.pendingDomain;
        navigatorDrag = null;
        try {
          svg.releasePointerCapture(event.pointerId);
        } catch (_error) {
          /* pointer may already be released */
        }
        dispatch({ type: "SET_VISIBLE_DOMAIN", domain: pendingDomain });
      }
    };
    svg.onpointercancel = () => {
      navigatorDrag = null;
      previewNavigatorSelection(state.time.visibleDomain);
    };
    svg.onclick = (event) => {
      if (navigatorDrag) return;
      dispatch({ type: "SET_VISIBLE_DOMAIN", domain: domainCenteredAt(dateFromNavigatorEvent(event, svg)) });
    };
  }

  function collectElements() {
    [
      "primaryFeature",
      "comparisonFeature",
      "addComparison",
      "rangeButtons",
      "scaleButtons",
      "anchorDate",
      "latestAnchor",
      "fromDate",
      "toDate",
      "applyDateRange",
      "stateSummary",
      "featureChips",
      "eventList",
      "panelStack",
      "navigator",
      "analysisPanel",
      "analysisTitle",
      "analysisStatus",
      "analysisChartNote",
      "analysisChart",
      "closeAnalysis",
      "tooltip",
      "openConfig",
      "configDialog",
      "closeConfig"
    ].forEach((id) => {
      els[id] = document.getElementById(id);
    });
  }

  collectElements();
  initControls();
  render();
  startLivePolling();
  window.driftMetricTimeseriesDemo = {
    dispatch,
    getState: () => state,
    buildRenderModel: () => buildRenderModel(state),
    pollLiveDay,
    stopLivePolling: () => {
      if (livePollTimer) window.clearInterval(livePollTimer);
      livePollTimer = null;
    }
  };
})();
