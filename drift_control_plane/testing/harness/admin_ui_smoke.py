from __future__ import annotations

import time
from pathlib import Path
from typing import Any
from urllib.parse import urlencode
from urllib.request import Request, urlopen
import json

from .artifact_store import ArtifactStore


REPO_ROOT = Path(__file__).resolve().parents[3]
TIMESERIES_HTML = REPO_ROOT / "drift_metric_timeseries" / "web" / "drift_metric_timeseries_demo.html"


def run_admin_ui_anchor_smoke(
    admin_base_url: str,
    store: ArtifactStore,
    visible: bool = False,
    hold_seconds: int = 0,
    tick_delay_ms: int = 0,
    require_llm_provider: bool = False,
) -> dict[str, Any]:
    from playwright.sync_api import sync_playwright

    admin_query = urlencode({"tickDelayMs": tick_delay_ms}) if tick_delay_ms > 0 else ""
    url = f"{admin_base_url.rstrip('/')}/admin"
    if admin_query:
        url = f"{url}?{admin_query}"
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=not visible, slow_mo=250 if visible else 0)
        page = browser.new_page(viewport={"width": 1440, "height": 1000})
        page.set_default_timeout(60000)
        page.goto(url)
        page.wait_for_function("() => window.__ADMIN_UI_TEST_STATE__?.status === 'idle'")
        scenario = _fetch_anchor_scenario(admin_base_url)
        source_id = scenario.get("source", {}).get("sourceId") or "case-010"
        _post_json(admin_base_url, "/api/admin/test/reset", {"mode": "pre-ui", "sourceId": source_id, "force": True})
        timeseries_page = _open_timeseries_page(browser, store, source_id, visible, wait_for_data=False)
        _start_timeseries_refresh(timeseries_page)
        before_path = store.run_dir / "admin_ui" / "before.png"
        before_path.parent.mkdir(parents=True, exist_ok=True)
        page.screenshot(path=str(before_path), full_page=True)
        if visible:
            page.bring_to_front()
        page.locator("#runAnchor").click()
        if visible:
            timeseries_page.bring_to_front()
        progress = _watch_admin_and_timeseries_progress(page, timeseries_page, store, visible)
        state = page.evaluate("() => window.__ADMIN_UI_TEST_STATE__")
        after_path = store.run_dir / "admin_ui" / "after.png"
        page.screenshot(path=str(after_path), full_page=True)
        timeseries_state = _wait_for_timeseries_data(timeseries_page, store, source_id, visible)
        analysis_state = _open_analysis_chart(timeseries_page, store, visible, require_llm_provider=require_llm_provider)
        if visible and hold_seconds > 0:
            time.sleep(hold_seconds)
        if not visible:
            browser.close()

    store.write_json("admin_ui/state.json", _slim_admin_state(state))
    store.write_json("timeseries_ui/state.json", timeseries_state)
    store.write_json("timeseries_ui/analysis_state.json", _slim_analysis_state(analysis_state))
    store.write_json("timeseries_ui/progress.json", progress)
    store.write_json(
        "admin_ui/summary.json",
        {
            "status": state.get("status"),
            "eventId": state.get("eventId"),
            "counts": state.get("counts", {}),
            "timeSeriesUrl": state.get("timeSeriesUrl"),
            "timeSeriesSeriesCount": len(timeseries_state.get("series", {}).get("metric", [])),
            "timeSeriesEventCount": len(timeseries_state.get("events", {}).get("metric", [])),
            "analysisChartRendered": analysis_state.get("rendered"),
            "analysisChartStatus": analysis_state.get("statusText"),
            "interpretationReady": analysis_state.get("interpretationReady"),
            "interpretationButtonText": analysis_state.get("interpretationButtonText"),
            "interpretationPopupTextLength": analysis_state.get("interpretationPopupTextLength"),
            "interpretationProvider": analysis_state.get("interpretationProvider"),
            "interpretationProviders": analysis_state.get("interpretationProviders"),
            "interpretationJobStatus": analysis_state.get("interpretationJobStatus"),
            "interpretationJobDurationSeconds": analysis_state.get("interpretationJobDurationSeconds"),
            "interpretationRuleOnly": analysis_state.get("interpretationRuleOnly"),
            "visualGuard": analysis_state.get("visualGuard"),
            "error": state.get("error"),
            "beforeScreenshot": "admin_ui/before.png",
            "afterScreenshot": "admin_ui/after.png",
            "timeseriesScreenshot": "timeseries_ui/after.png",
            "analysisChartScreenshot": "timeseries_ui/analysis_chart.png",
            "timeseriesProgress": "timeseries_ui/progress.json",
            "visible": visible,
            "holdSeconds": hold_seconds,
            "tickDelayMs": tick_delay_ms,
            "requireLlmProvider": require_llm_provider,
        },
    )
    return state


def _fetch_anchor_scenario(admin_base_url: str) -> dict[str, Any]:
    with urlopen(f"{admin_base_url.rstrip('/')}/api/admin/anchor/case010/scenario", timeout=5) as response:
        payload = json.loads(response.read().decode("utf-8"))
    return payload.get("data", payload)


def _post_json(admin_base_url: str, path: str, body: dict[str, Any]) -> dict[str, Any]:
    data = json.dumps(body).encode("utf-8")
    request = Request(
        f"{admin_base_url.rstrip('/')}{path}",
        data=data,
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        method="POST",
    )
    with urlopen(request, timeout=5) as response:
        return json.loads(response.read().decode("utf-8"))


def _timeseries_url(source_id: str) -> str:
    query = urlencode(
        {
            "testMode": "1",
            "autoPoll": "0",
            "sourceId": source_id,
            "apiBase": "http://127.0.0.1:8771",
        }
    )
    return f"{TIMESERIES_HTML.as_uri()}?{query}"


def _open_timeseries_page(
    browser: Any,
    store: ArtifactStore,
    source_id: str,
    visible: bool,
    wait_for_data: bool = True,
) -> Any:
    url = _timeseries_url(source_id)
    page = browser.new_page(viewport={"width": 1440, "height": 1100})
    page.set_default_timeout(60000)
    page.goto(url)
    page.wait_for_function("() => Boolean(window.driftMetricTimeseriesDemo?.loadServerTimeseriesOnce)")
    before_path = store.run_dir / "timeseries_ui" / "before.png"
    before_path.parent.mkdir(parents=True, exist_ok=True)
    page.screenshot(path=str(before_path), full_page=True)
    if wait_for_data:
        _wait_for_timeseries_data(page, store, source_id, visible)
    if visible:
        page.bring_to_front()
    return page


def _start_timeseries_refresh(page: Any) -> None:
    page.evaluate(
        """
        () => {
          if (window.__HARNESS_TIMESERIES_REFRESH__) {
            window.clearInterval(window.__HARNESS_TIMESERIES_REFRESH__);
          }
          const refresh = () => window.driftMetricTimeseriesDemo?.loadServerTimeseriesOnce?.();
          refresh();
          window.__HARNESS_TIMESERIES_REFRESH__ = window.setInterval(refresh, 750);
        }
        """
    )


def _wait_for_timeseries_data(page: Any, store: ArtifactStore, source_id: str, visible: bool) -> dict[str, Any]:
    page.wait_for_function(
        """
        (sourceId) => {
          const state = window.__DRIFT_TEST_STATE__;
          if (!state || state.sourceId !== sourceId) return false;
          const series = state.series?.metric || [];
          const events = state.events?.metric || [];
          return series.length > 0 && events.length > 0 && state.ui?.analysisLinks > 0;
        }
        """,
        arg=source_id,
    )
    state = page.evaluate("() => window.__DRIFT_TEST_STATE__")
    state["url"] = _timeseries_url(source_id)
    screenshot_path = store.run_dir / "timeseries_ui" / "after.png"
    screenshot_path.parent.mkdir(parents=True, exist_ok=True)
    page.screenshot(path=str(screenshot_path), full_page=True)
    if visible:
        page.bring_to_front()
    return state


def _watch_admin_and_timeseries_progress(admin_page: Any, timeseries_page: Any, store: ArtifactStore, visible: bool) -> list[dict[str, Any]]:
    progress: list[dict[str, Any]] = []
    last_counts: tuple[int, int] | None = None
    deadline = time.time() + 90
    snapshot_index = 0
    while time.time() < deadline:
        admin_state = admin_page.evaluate("() => window.__ADMIN_UI_TEST_STATE__ || {}")
        timeseries_state = timeseries_page.evaluate("() => window.__DRIFT_TEST_STATE__ || {}")
        series_count = len(timeseries_state.get("series", {}).get("metric", []))
        event_count = len(timeseries_state.get("events", {}).get("metric", []))
        counts = (series_count, event_count)
        if counts != last_counts:
            snapshot_name = f"timeseries_ui/progress_{snapshot_index:02d}_series{series_count}_events{event_count}.png"
            timeseries_page.screenshot(path=str(store.run_dir / snapshot_name), full_page=True)
            progress.append(
                {
                    "index": snapshot_index,
                    "adminStatus": admin_state.get("status"),
                    "seriesCount": series_count,
                    "eventCount": event_count,
                    "screenshot": snapshot_name,
                }
            )
            snapshot_index += 1
            last_counts = counts
        if admin_state.get("status") in {"passed", "failed"}:
            return progress
        if visible:
            timeseries_page.bring_to_front()
        time.sleep(1)
    raise TimeoutError("Admin UI did not finish within 90 seconds")


def _open_analysis_chart(page: Any, store: ArtifactStore, visible: bool, require_llm_provider: bool = False) -> dict[str, Any]:
    interpretation_jobs: list[dict[str, Any]] = []

    def record_interpretation_response(response: Any) -> None:
        if "/api/interpret/chart/jobs" not in response.url:
            return
        try:
            payload = response.json()
        except Exception as exc:  # noqa: BLE001
            payload = {"ok": False, "error": f"{exc.__class__.__name__}: {exc}"}
        interpretation_jobs.append(
            {
                "url": response.url,
                "status": response.status,
                "receivedAt": time.time(),
                "payload": payload,
            }
        )

    page.on("response", record_interpretation_response)
    page.locator("[data-analysis-event-key]").first.click()
    page.wait_for_function(
        """
        () => {
          const panel = document.querySelector('#analysisPanel');
          const chart = document.querySelector('#analysisChart');
          return panel && !panel.hidden && chart && chart.children.length > 0;
        }
        """,
        timeout=90000,
    )
    status_text = page.locator("#analysisStatus").inner_text(timeout=5000)
    rendered = page.evaluate(
        """
        () => {
          const chart = document.querySelector('#analysisChart');
          const classes = Array.from(chart?.querySelectorAll('[class]') || []).flatMap((node) => {
            const style = window.getComputedStyle(node);
            return String(node.getAttribute('class') || '').split(/\\s+/).filter(Boolean).map((className) => ({
              tag: node.tagName.toLowerCase(),
              className,
              fill: style.fill,
              stroke: style.stroke
            }));
          });
          return {
            childCount: chart ? chart.children.length : 0,
            textLength: chart ? chart.innerText.length : 0,
            hasSvg: Boolean(chart?.querySelector('svg')),
            hasCanvas: Boolean(chart?.querySelector('canvas')),
            hasRuntimeError: /분석 차트를 만들 수 없습니다|error|failed/i.test(chart?.innerText || ''),
            classes
          };
        }
        """
    )
    screenshot_path = store.run_dir / "timeseries_ui" / "analysis_chart.png"
    page.screenshot(path=str(screenshot_path), full_page=True)
    interpretation_state = _open_interpretation_note(
        page,
        store,
        visible,
        interpretation_jobs,
        require_llm_provider=require_llm_provider,
    )
    visual_guard = _assert_chart_visual_guard(page)
    if visible:
        page.bring_to_front()
    return {
        "rendered": rendered.get("childCount", 0) > 0 and not rendered.get("hasRuntimeError") and visual_guard.get("ok"),
        "statusText": status_text,
        **interpretation_state,
        "dom": rendered,
        "visualGuard": visual_guard,
        "screenshot": "timeseries_ui/analysis_chart.png",
    }


def _open_interpretation_note(
    page: Any,
    store: ArtifactStore,
    visible: bool,
    interpretation_jobs: list[dict[str, Any]],
    require_llm_provider: bool = False,
) -> dict[str, Any]:
    page.wait_for_function(
        """
        () => {
          const button = document.querySelector('#analysisChartNote');
          return button && !button.hidden && !button.disabled && button.dataset.state === 'ready';
        }
        """,
        timeout=120000,
    )
    button_text = page.locator("#analysisChartNote").inner_text(timeout=5000)
    page.locator("#analysisChartNote").click()
    page.wait_for_function(
        """
        () => {
          const popup = document.querySelector('.note-popup');
          const body = document.querySelector('.note-popup-body');
          return popup && !popup.hidden && body && body.textContent.trim().length > 40;
        }
        """,
        timeout=30000,
    )
    note = page.evaluate(
        """
        () => {
          const body = document.querySelector('.note-popup-body');
          const text = body?.textContent?.trim() || '';
          return {
            popupVisible: Boolean(body && !document.querySelector('.note-popup')?.hidden),
            text,
            textLength: text.length
          };
        }
        """
    )
    metadata = _interpretation_job_metadata(interpretation_jobs)
    store.write_json(
        "timeseries_ui/interpretation_note.json",
        {
            "buttonText": button_text,
            "popupVisible": note.get("popupVisible"),
            "textLength": note.get("textLength"),
            "textPreview": str(note.get("text", ""))[:500],
            **metadata,
        },
    )
    store.write_json("timeseries_ui/interpretation_jobs.json", _slim_interpretation_jobs(interpretation_jobs))
    if require_llm_provider and metadata.get("ruleOnly"):
        raise AssertionError(f"interpretation provider is rule-only: {metadata.get('providers')}")
    screenshot_path = store.run_dir / "timeseries_ui" / "interpretation_note.png"
    page.screenshot(path=str(screenshot_path), full_page=True)
    if visible:
        page.bring_to_front()
    return {
        "interpretationReady": bool(note.get("popupVisible")) and int(note.get("textLength") or 0) > 40,
        "interpretationButtonText": button_text,
        "interpretationPopupTextLength": note.get("textLength"),
        "interpretationProvider": metadata.get("provider"),
        "interpretationProviders": metadata.get("providers"),
        "interpretationJobStatus": metadata.get("jobStatus"),
        "interpretationJobDurationSeconds": metadata.get("jobDurationSeconds"),
        "interpretationRuleOnly": metadata.get("ruleOnly"),
        "interpretationPopupScreenshot": "timeseries_ui/interpretation_note.png",
        "interpretationNoteArtifact": "timeseries_ui/interpretation_note.json",
    }


def _interpretation_job_metadata(interpretation_jobs: list[dict[str, Any]]) -> dict[str, Any]:
    payloads = [item.get("payload") for item in interpretation_jobs if isinstance(item.get("payload"), dict)]
    final_payload = None
    for payload in reversed(payloads):
        if payload.get("result"):
            final_payload = payload
            break
    if final_payload is None and payloads:
        final_payload = payloads[-1]
    result = final_payload.get("result") if isinstance(final_payload, dict) else None
    providers = sorted(set(_providers_in(result))) if isinstance(result, dict) else []
    job_duration = None
    if isinstance(final_payload, dict):
        started = final_payload.get("startedAt")
        finished = final_payload.get("finishedAt")
        if isinstance(started, (int, float)) and isinstance(finished, (int, float)):
            job_duration = round(float(finished) - float(started), 3)
    provider = "mixed" if len(providers) > 1 else providers[0] if providers else None
    return {
        "provider": provider,
        "providers": providers,
        "jobStatus": final_payload.get("status") if isinstance(final_payload, dict) else None,
        "jobDurationSeconds": job_duration,
        "ruleOnly": bool(providers) and set(providers) == {"rule"},
        "jobResponseCount": len(interpretation_jobs),
    }


def _slim_interpretation_jobs(interpretation_jobs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    slim_jobs: list[dict[str, Any]] = []
    for item in interpretation_jobs:
        payload = item.get("payload") if isinstance(item.get("payload"), dict) else {}
        result = payload.get("result") if isinstance(payload.get("result"), dict) else {}
        chart_note = result.get("chartNote") if isinstance(result.get("chartNote"), dict) else {}
        slim_jobs.append(
            {
                "url": item.get("url"),
                "httpStatus": item.get("status"),
                "receivedAt": item.get("receivedAt"),
                "ok": payload.get("ok"),
                "jobId": payload.get("jobId"),
                "jobStatus": payload.get("status"),
                "payloadHash": payload.get("payloadHash"),
                "startedAt": payload.get("startedAt"),
                "finishedAt": payload.get("finishedAt"),
                "chartNoteProvider": chart_note.get("provider"),
                "providers": sorted(set(_providers_in(result))) if result else [],
                "error": payload.get("error"),
            }
        )
    return slim_jobs


def _slim_analysis_state(analysis_state: dict[str, Any]) -> dict[str, Any]:
    dom = analysis_state.get("dom") if isinstance(analysis_state.get("dom"), dict) else {}
    visual_guard = analysis_state.get("visualGuard") if isinstance(analysis_state.get("visualGuard"), dict) else {}
    providers = analysis_state.get("interpretationProviders")
    provider_list = [str(item) for item in providers] if isinstance(providers, list) else []
    unscoped = visual_guard.get("unscopedRuntimeStyles")
    unscoped_list = [str(item) for item in unscoped] if isinstance(unscoped, list) else []
    black_shapes = visual_guard.get("blackVisibleShapes")
    return {
        "rendered": bool(analysis_state.get("rendered")),
        "statusText": str(analysis_state.get("statusText") or ""),
        "interpretationReady": bool(analysis_state.get("interpretationReady")),
        "interpretationButtonText": str(analysis_state.get("interpretationButtonText") or ""),
        "interpretationPopupTextLength": int(analysis_state.get("interpretationPopupTextLength") or 0),
        "interpretationProvider": str(analysis_state.get("interpretationProvider") or ""),
        "interpretationProviders": provider_list,
        "interpretationJobStatus": str(analysis_state.get("interpretationJobStatus") or ""),
        "interpretationJobDurationSeconds": float(analysis_state.get("interpretationJobDurationSeconds") or 0),
        "interpretationRuleOnly": bool(analysis_state.get("interpretationRuleOnly")),
        "interpretationPopupScreenshot": str(analysis_state.get("interpretationPopupScreenshot") or ""),
        "interpretationNoteArtifact": str(analysis_state.get("interpretationNoteArtifact") or ""),
        "screenshot": str(analysis_state.get("screenshot") or ""),
        "dom": {
            "childCount": int(dom.get("childCount") or 0),
            "textLength": int(dom.get("textLength") or 0),
            "hasSvg": bool(dom.get("hasSvg")),
            "hasCanvas": bool(dom.get("hasCanvas")),
            "hasRuntimeError": bool(dom.get("hasRuntimeError")),
        },
        "visualGuard": {
            "ok": bool(visual_guard.get("ok")),
            "unscopedRuntimeStyles": unscoped_list,
            "mainLineCount": int(visual_guard.get("mainLineCount") or 0),
            "mainLineOk": bool(visual_guard.get("mainLineOk")),
            "blackVisibleShapeCount": len(black_shapes) if isinstance(black_shapes, list) else 0,
        },
    }


def _providers_in(value: Any) -> list[str]:
    providers: list[str] = []
    if isinstance(value, dict):
        provider = value.get("provider")
        if isinstance(provider, str) and provider:
            providers.append(provider)
        for item in value.values():
            providers.extend(_providers_in(item))
    elif isinstance(value, list):
        for item in value:
            providers.extend(_providers_in(item))
    return providers


def _slim_admin_state(state: dict[str, Any]) -> dict[str, Any]:
    counts = state.get("counts") if isinstance(state.get("counts"), dict) else {}
    latest = state.get("latest") if isinstance(state.get("latest"), dict) else {}
    steps = state.get("steps") if isinstance(state.get("steps"), list) else []
    return {
        "status": str(state.get("status") or ""),
        "eventId": str(state.get("eventId") or ""),
        "error": str(state.get("error") or "") if state.get("error") else None,
        "timeSeriesUrl": str(state.get("timeSeriesUrl") or ""),
        "counts": {
            "rawEventCount": int(counts.get("rawEventCount") or 0),
            "bucketCount": int(counts.get("bucketCount") or 0),
            "methodRunCount": int(counts.get("methodRunCount") or 0),
            "eventCount": int(counts.get("eventCount") or 0),
        },
        "latest": {
            "sourceId": str(latest.get("sourceId") or ""),
            "adapterId": str(latest.get("adapterId") or ""),
            "assignmentId": str(latest.get("assignmentId") or ""),
            "chartId": str(latest.get("chartId") or ""),
        },
        "steps": [
            {
                "id": str(step.get("id") or ""),
                "status": str(step.get("status") or ""),
                "message": str(step.get("message") or ""),
            }
            for step in steps
            if isinstance(step, dict)
        ],
    }


def _assert_chart_visual_guard(page: Any) -> dict[str, Any]:
    guard = page.evaluate(
        """
        () => {
          const normalize = (value) => String(value || '').replace(/\\s+/g, '').toLowerCase();
          const isBlack = (value) => ['rgb(0,0,0)', 'rgba(0,0,0,1)', '#000', '#000000', 'black'].includes(normalize(value));
          const isVisiblePaint = (value, opacity) => {
            const normalized = normalize(value);
            const alpha = Number.parseFloat(opacity || '1');
            return normalized && normalized !== 'none' && normalized !== 'transparent' && alpha > 0.01;
          };
          const describe = (node, style) => ({
            tag: node.tagName.toLowerCase(),
            className: node.getAttribute('class') || '',
            fill: style.fill,
            stroke: style.stroke,
            fillOpacity: style.fillOpacity,
            strokeOpacity: style.strokeOpacity,
            strokeWidth: style.strokeWidth
          });
          const linkHrefs = Array.from(document.querySelectorAll('link[rel="stylesheet"]')).map((link) => link.href || '');
          const unscopedRuntimeStyles = linkHrefs.filter((href) => href.includes('chart_runtime') && href.includes('chart-visuals.css'));
          const mainLines = Array.from(document.querySelectorAll('.chart-main .series-line'));
          const mainLineOk = mainLines.some((line) => {
            const style = window.getComputedStyle(line);
            return isVisiblePaint(style.stroke, style.strokeOpacity)
              && !isBlack(style.stroke)
              && Number.parseFloat(style.strokeWidth || '0') > 0.5;
          });
          const visibleShapeSelector = [
            '#analysisChart path',
            '#analysisChart rect',
            '#analysisChart circle',
            '#analysisChart ellipse',
            '#analysisChart polygon',
            '#analysisChart polyline'
          ].join(',');
          const blackVisibleShapes = Array.from(document.querySelectorAll(visibleShapeSelector)).filter((node) => {
            const style = window.getComputedStyle(node);
            const tag = node.tagName.toLowerCase();
            const fillBlack = tag !== 'polyline' && isBlack(style.fill) && isVisiblePaint(style.fill, style.fillOpacity);
            const strokeBlack = isBlack(style.stroke)
              && isVisiblePaint(style.stroke, style.strokeOpacity)
              && Number.parseFloat(style.strokeWidth || '0') > 0;
            return fillBlack || strokeBlack;
          }).map((node) => describe(node, window.getComputedStyle(node)));
          return {
            ok: unscopedRuntimeStyles.length === 0 && mainLineOk && blackVisibleShapes.length === 0,
            unscopedRuntimeStyles,
            mainLineCount: mainLines.length,
            mainLineOk,
            blackVisibleShapes
          };
        }
        """
    )
    errors = []
    if guard.get("unscopedRuntimeStyles"):
        errors.append(f"unscoped runtime CSS loaded: {guard['unscopedRuntimeStyles']}")
    if not guard.get("mainLineOk"):
        errors.append(f"main timeseries line is not visibly rendered; lineCount={guard.get('mainLineCount')}")
    if guard.get("blackVisibleShapes"):
        errors.append(f"analysis chart has black visible shapes: {guard['blackVisibleShapes'][:5]}")
    if errors:
        raise AssertionError("; ".join(errors))
    return guard
