from __future__ import annotations

from pathlib import Path
from typing import Any

from .artifact_store import ArtifactStore


REPO_ROOT = Path(__file__).resolve().parents[3]
TIMESERIES_HTML = REPO_ROOT / "drift_metric_timeseries" / "web" / "drift_metric_timeseries_demo.html"


# @managed-contract contract_id=harness.ui_smoke.run_timeseries_ui_smoke level=P1
def run_timeseries_ui_smoke(source_id: str, drift_base_url: str, store: ArtifactStore) -> dict[str, Any]:
    from playwright.sync_api import sync_playwright

    url = (
        TIMESERIES_HTML.as_uri()
        + f"?testMode=1&autoPoll=0&sourceId={source_id}&apiBase={drift_base_url}"
    )
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1440, "height": 1100})
        page.set_default_timeout(10000)
        page.goto(url)
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
        screenshot_path = store.run_dir / "ui_state" / "timeseries_ui.png"
        screenshot_path.parent.mkdir(parents=True, exist_ok=True)
        page.screenshot(path=str(screenshot_path), full_page=True)
        browser.close()

    store.write_json("ui_state/state.json", state)
    store.write_json(
        "ui_state/summary.json",
        {
            "sourceId": state.get("sourceId"),
            "seriesCount": len(state.get("series", {}).get("metric", [])),
            "eventCount": len(state.get("events", {}).get("metric", [])),
            "eventMarkerCount": len(state.get("eventMarkers", [])),
            "chartLinkCount": len(state.get("chartLinks", [])),
            "screenshot": "ui_state/timeseries_ui.png",
        },
    )
    return state
