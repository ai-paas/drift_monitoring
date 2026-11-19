from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from .artifact_store import ArtifactStore


REPO_ROOT = Path(__file__).resolve().parents[3]
CHART_RUNTIME_HTML = REPO_ROOT / "chart_runtime" / "chart_runtime_smoke.html"


def merge_interpretation_into_chart_payload(analysis: Any, interpretation: Any) -> dict[str, Any]:
    data = analysis.get("data", {}) if isinstance(analysis, dict) else {}
    payload = deepcopy(data.get("chartPayload", {}) if isinstance(data, dict) else {})
    if isinstance(interpretation, dict) and interpretation:
        payload["interpretation"] = interpretation
        notes_by_component = {
            note.get("componentInstanceId"): note
            for note in interpretation.get("componentNotes", [])
            if isinstance(note, dict) and note.get("componentInstanceId")
        }
        for component in payload.get("components", []):
            if not isinstance(component, dict):
                continue
            note = notes_by_component.get(component.get("componentInstanceId"))
            if note:
                component["interpretationNote"] = note
    return payload


# @managed-contract contract_id=harness.chart_smoke.run_chart_runtime_smoke level=P1
def run_chart_runtime_smoke(payload: dict[str, Any], store: ArtifactStore) -> dict[str, Any]:
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1440, "height": 1100})
        page.set_default_timeout(10000)
        page.goto(CHART_RUNTIME_HTML.as_uri())
        state = page.evaluate(
            """
            (payload) => window.renderChartRuntimeSmokePayload(payload)
            """,
            payload,
        )
        page.wait_for_function("() => window.__CHART_TEST_STATE__?.renderStatus === 'rendered'")
        state = page.evaluate("() => window.__CHART_TEST_STATE__")
        screenshot_path = store.run_dir / "chart_test_state" / "chart_runtime.png"
        screenshot_path.parent.mkdir(parents=True, exist_ok=True)
        page.screenshot(path=str(screenshot_path), full_page=True)
        browser.close()

    store.write_json("chart_test_state/state.json", state)
    store.write_json(
        "chart_test_state/summary.json",
        {
            "chartId": state.get("chartId"),
            "componentCount": state.get("componentCount"),
            "dataSourceCount": state.get("dataSourceCount"),
            "checks": state.get("checks", {}),
            "dom": state.get("dom", {}),
            "screenshot": "chart_test_state/chart_runtime.png",
        },
    )
    return state
