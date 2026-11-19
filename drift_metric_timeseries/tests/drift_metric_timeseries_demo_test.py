from __future__ import annotations

from pathlib import Path

from playwright.sync_api import sync_playwright


ROOT = Path(__file__).resolve().parents[2]
PROJECT_DIR = ROOT / "drift_metric_timeseries"
DEMO = (PROJECT_DIR / "web" / "drift_metric_timeseries_demo.html").as_uri() + "?live=0"
SCREENSHOT = ROOT / "tmp_compare" / "drift_metric_timeseries_demo.png"
FLOW_SCREENSHOT = ROOT / "tmp_compare" / "drift_metric_timeseries_demo_flow.png"


def assert_equal(actual, expected, label: str) -> None:
    if actual != expected:
        raise AssertionError(f"{label}: expected {expected!r}, got {actual!r}")


def assert_contains(text: str, token: str, label: str) -> None:
    if token not in text:
        raise AssertionError(f"{label}: expected to contain {token!r}, got {text!r}")


def first_attr(page, selector: str, name: str) -> str:
    return page.evaluate(
        "([selector, name]) => document.querySelector(selector)?.getAttribute(name) || ''",
        [selector, name],
    )


def dom_click(page, selector: str) -> None:
    page.evaluate("selector => document.querySelector(selector)?.click()", selector)


def dispatch(page, action: dict) -> None:
    page.evaluate("action => window.driftMetricTimeseriesDemo.dispatch(action)", action)


def run() -> None:
    SCREENSHOT.parent.mkdir(exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1440, "height": 1150})
        page.set_default_timeout(5000)
        page.goto(DEMO)
        page.wait_for_selector(".feature-panel")

        initial_panels = page.locator(".feature-panel").count()
        assert_equal(initial_panels, 1, "initial panel count")
        initial_view = page.evaluate("() => window.driftMetricTimeseriesDemo.getState().view")
        assert_equal(initial_view["primaryFeature"], "embedding_distance", "initial primary feature")
        assert_equal(initial_view["comparisonFeatures"], [], "initial comparison features")
        assert_equal(page.locator("#eventList .event-item").count(), 2, "initial primary event count")
        assert_equal(page.locator("#configDialog[hidden]").count(), 1, "settings dialog initially hidden")
        dom_click(page, "#openConfig")
        assert_equal(page.locator("#configDialog:not([hidden])").count(), 1, "settings dialog opens")

        for preset in ["24H", "7D", "30D", "3M", "1Y", "ALL"]:
            dispatch(page, {"type": "SET_RANGE_PRESET", "preset": preset})
            time_state = page.evaluate("() => window.driftMetricTimeseriesDemo.getState().time")
            assert_equal(time_state["rangePreset"], preset, f"range preset {preset}")
            active = page.locator(f'#rangeButtons button[data-value="{preset}"].active').count()
            assert_equal(active, 1, f"active range button {preset}")
            if preset != "ALL":
                start_date = str(time_state["visibleDomain"][0])[:10]
                anchor_date = str(time_state["rangeAnchorDate"])[:10]
                assert_equal(start_date, anchor_date, f"{preset} preset starts at anchor date")

        dispatch(page, {"type": "SET_RANGE_PRESET", "preset": "7D"})
        for scale in ["auto", "hour", "day", "month", "year"]:
            dispatch(page, {"type": "SET_SCALE_MODE", "scaleMode": scale})
            time_state = page.evaluate("() => window.driftMetricTimeseriesDemo.getState().time")
            assert_equal(time_state["scaleMode"], scale, f"scale mode {scale}")
            active = page.evaluate(
                "scale => document.querySelector(`#scaleButtons button[data-value=\"${scale}\"]`)?.classList.contains('active') ? 1 : 0",
                scale,
            )
            assert_equal(active, 1, f"active scale button {scale}")

        dispatch(page, {"type": "SET_RANGE_PRESET", "preset": "24H"})
        dispatch(page, {"type": "SET_SCALE_MODE", "scaleMode": "hour"})
        hour_model = page.evaluate("() => window.driftMetricTimeseriesDemo.buildRenderModel()")
        if len(hour_model[0]["series"]) < 20:
            raise AssertionError(f"24H hour scale should render hourly data, got {len(hour_model[0]['series'])} rows")
        hour_path = first_attr(page, "#panelStack .feature-panel .series-line", "d")
        if "L" not in hour_path:
            raise AssertionError("24H hour scale should draw a line with multiple hourly points")

        page.fill("#anchorDate", "2025-06-24")
        dispatch(page, {"type": "SET_RANGE_PRESET", "preset": "7D", "anchorStart": "2025-06-24T00:00:00Z"})
        dispatch(page, {"type": "SET_SCALE_MODE", "scaleMode": "hour"})
        seven_day_hour_state = page.evaluate("() => window.driftMetricTimeseriesDemo.getState().time")
        assert_equal(seven_day_hour_state["displayBucket"], "1h", "7D hour scale display bucket")
        assert_equal(seven_day_hour_state["tickInterval"], "1d", "7D hour scale tick interval")
        seven_day_hour_model = page.evaluate("() => window.driftMetricTimeseriesDemo.buildRenderModel()")
        if len(seven_day_hour_model[0]["series"]) < 24 * 6:
            raise AssertionError(f"7D hour scale should render hourly data, got {len(seven_day_hour_model[0]['series'])} rows")
        first_path = first_attr(page, "#panelStack .feature-panel .series-line", "d")
        if "L" not in first_path:
            raise AssertionError("7D hour scale should draw a line with multiple hourly points")
        tick_text = page.evaluate(
            """
            () => Array.from(document.querySelectorAll('#panelStack .feature-panel:first-child .tick-label'))
              .map((node) => node.textContent || '')
            """
        )
        if not any("06-25" in item or "06-26" in item for item in tick_text):
            raise AssertionError(f"7D hour scale labels were not rendered, got {tick_text}")

        page.fill("#anchorDate", "2025-06-04")
        dispatch(page, {"type": "SET_RANGE_PRESET", "preset": "7D", "anchorStart": "2025-06-04T00:00:00Z"})
        dispatch(page, {"type": "SET_SCALE_MODE", "scaleMode": "hour"})
        early_hour_state = page.evaluate("() => window.driftMetricTimeseriesDemo.getState().time")
        assert_equal(str(early_hour_state["visibleDomain"][0])[:10], "2025-06-04", "early 7D hour start")
        assert_equal(early_hour_state["displayBucket"], "1h", "early 7D hour display bucket")
        early_hour_model = page.evaluate("() => window.driftMetricTimeseriesDemo.buildRenderModel()")
        if len(early_hour_model[0]["series"]) < 24 * 6:
            raise AssertionError(f"early 7D hour scale should render hourly data, got {len(early_hour_model[0]['series'])} rows")
        early_hour_path = first_attr(page, "#panelStack .feature-panel .series-line", "d")
        if "L" not in early_hour_path:
            raise AssertionError("early 7D hour scale should draw a line with multiple hourly points")

        page.fill("#anchorDate", "2025-06-04")
        dispatch(page, {"type": "SET_RANGE_PRESET", "preset": "7D", "anchorStart": "2025-06-04T00:00:00Z"})
        dispatch(page, {"type": "SET_SCALE_MODE", "scaleMode": "year"})
        seven_day_year_state = page.evaluate("() => window.driftMetricTimeseriesDemo.getState().time")
        assert_equal(seven_day_year_state["displayBucket"], "1d", "7D year scale display bucket")
        seven_day_year_model = page.evaluate("() => window.driftMetricTimeseriesDemo.buildRenderModel()")
        if len(seven_day_year_model[0]["series"]) < 6:
            raise AssertionError(f"7D year scale should render daily averages, got {len(seven_day_year_model[0]['series'])} rows")
        daily_path = first_attr(page, "#panelStack .feature-panel .series-line", "d")
        if "L" not in daily_path:
            raise AssertionError("7D year scale should draw a daily-average line")

        dispatch(page, {"type": "SET_SCALE_MODE", "scaleMode": "day"})
        dispatch(page, {"type": "SET_RANGE_PRESET", "preset": "3M"})
        disabled_hour = page.locator('#scaleButtons button[data-value="hour"]:disabled').count()
        assert_equal(disabled_hour, 1, "3M range disables hour scale")
        before_forbidden_scale = page.evaluate("() => window.driftMetricTimeseriesDemo.getState().time.scaleMode")
        page.locator('#scaleButtons button[data-value="hour"]').click(force=True)
        after_forbidden_scale = page.evaluate("() => window.driftMetricTimeseriesDemo.getState().time.scaleMode")
        assert_equal(after_forbidden_scale, before_forbidden_scale, "disabled hour scale click ignored")

        dispatch(page, {"type": "SET_RANGE_PRESET", "preset": "7D"})
        dispatch(page, {"type": "SET_SCALE_MODE", "scaleMode": "hour"})
        disabled_30d = page.locator('#rangeButtons button[data-value="30D"]:disabled').count()
        disabled_all = page.locator('#rangeButtons button[data-value="ALL"]:disabled').count()
        if disabled_30d != 1 or disabled_all != 1:
            raise AssertionError("hour scale should disable ranges longer than 7 days")
        before_forbidden_range = page.evaluate("() => window.driftMetricTimeseriesDemo.getState().time.visibleDomain")
        page.locator('#rangeButtons button[data-value="30D"]').click(force=True)
        after_forbidden_range = page.evaluate("() => window.driftMetricTimeseriesDemo.getState().time.visibleDomain")
        if before_forbidden_range != after_forbidden_range:
            raise AssertionError("disabled 30D range changed hour-scale visibleDomain")

        page.select_option("#comparisonFeature", "token_length")
        page.locator("#addComparison").click()
        view_state = page.evaluate("() => window.driftMetricTimeseriesDemo.getState().view")
        assert_equal(view_state["comparisonFeatures"], ["token_length"], "token comparison added")
        assert_equal(page.locator(".feature-panel").count(), 2, "two panels after token add")
        assert_equal(page.locator("#eventList .event-item").count(), 3, "comparison event count added")
        dom_click(page, "#closeConfig")
        event_key = first_attr(page, "#eventList .event-item", "data-event-key")
        before_event_domain = page.evaluate("() => window.driftMetricTimeseriesDemo.getState().time.visibleDomain")
        dom_click(page, "#eventList .event-item")
        after_event_state = page.evaluate("() => window.driftMetricTimeseriesDemo.getState().time")
        if before_event_domain == after_event_state["visibleDomain"]:
            raise AssertionError("event click did not move visible domain")
        if after_event_state["rangePreset"] != "CUSTOM":
            raise AssertionError("event click should set custom visible domain")
        active_event_key = first_attr(page, "#eventList .event-item.active", "data-event-key")
        assert_equal(active_event_key, event_key, "clicked event becomes active")
        dom_click(page, "#openConfig")

        page.select_option("#comparisonFeature", "refusal_rate")
        page.locator("#addComparison").click()
        view_state = page.evaluate("() => window.driftMetricTimeseriesDemo.getState().view")
        assert_equal(view_state["comparisonFeatures"], ["token_length", "refusal_rate"], "refusal comparison added")

        dom_click(page, "#closeConfig")
        dom_click(page, '[data-remove-feature="token_length"]')
        view_state = page.evaluate("() => window.driftMetricTimeseriesDemo.getState().view")
        assert_equal(view_state["comparisonFeatures"], ["refusal_rate"], "token comparison removed")
        dom_click(page, "#openConfig")

        page.select_option("#comparisonFeature", "token_length")
        page.locator("#addComparison").click()
        view_state = page.evaluate("() => window.driftMetricTimeseriesDemo.getState().view")
        assert_equal(view_state["comparisonFeatures"], ["refusal_rate", "token_length"], "token comparison re-added")

        page.select_option("#primaryFeature", "token_length")
        view_state = page.evaluate("() => window.driftMetricTimeseriesDemo.getState().view")
        assert_equal(view_state["primaryFeature"], "token_length", "primary changed to token")
        if "token_length" in view_state["comparisonFeatures"]:
            raise AssertionError("primary feature should not remain in comparisonFeatures")

        page.select_option("#primaryFeature", "embedding_distance")
        page.select_option("#comparisonFeature", "token_length")
        page.locator("#addComparison").click()
        dispatch(page, {"type": "SET_SCALE_MODE", "scaleMode": "year"})
        dispatch(page, {"type": "SET_RANGE_PRESET", "preset": "ALL"})
        page.wait_for_timeout(100)

        panels = page.locator(".feature-panel").count()
        missing_bands = page.locator(".band.missing").count()
        drift_events = page.locator(".event.drift").count()
        summary = page.locator("#stateSummary").inner_text()
        assert_contains(summary, "coverage", "summary coverage")
        assert_contains(summary, "missing", "summary missing")
        assert_contains(summary, "drift", "summary drift")
        plot_clip_ok = page.evaluate(
            """
            () => Array.from(document.querySelectorAll('#panelStack .chart-svg')).every((svg) => {
              const clip = svg.querySelector('clipPath rect');
              const clipBox = clip.getBBox();
              return Array.from(svg.querySelectorAll('g[clip-path] .series-line, g[clip-path] .band, g[clip-path] .event, g[clip-path] .marker')).every((node) => {
                const box = node.getBBox();
                return box.x + box.width >= clipBox.x - 1
                  && box.x <= clipBox.x + clipBox.width + 1
                  && box.y + box.height >= clipBox.y - 1
                  && box.y <= clipBox.y + clipBox.height + 1;
              });
            })
            """
        )
        if not plot_clip_ok:
            raise AssertionError("plot elements are not constrained to clip area")
        navigator_clip_ok = page.evaluate(
            """
            () => {
              const svg = document.querySelector('#navigator svg');
              const clip = svg.querySelector('clipPath rect').getBBox();
              return Array.from(svg.querySelectorAll('g[clip-path] .series-line, g[clip-path] .navigator-selection')).every((node) => {
                const box = node.getBBox();
                return box.x + box.width >= clip.x - 1
                  && box.x <= clip.x + clip.width + 1
                  && box.y + box.height >= clip.y - 1
                  && box.y <= clip.y + clip.height + 1;
              });
            }
            """
        )
        if not navigator_clip_ok:
            raise AssertionError("navigator elements are not constrained to clip area")

        page.fill("#fromDate", "2025-11-01")
        page.fill("#toDate", "2026-02-01")
        page.locator("#applyDateRange").click()
        custom_state = page.evaluate("() => window.driftMetricTimeseriesDemo.getState().time")
        assert_equal(custom_state["rangePreset"], "CUSTOM", "custom date range")
        model = page.evaluate("() => window.driftMetricTimeseriesDemo.buildRenderModel()")
        if model[0]["quality"]["missingBuckets"] < 2:
            raise AssertionError("missing buckets were not reflected in custom range")
        if page.locator(".band.missing").count() < 1:
            raise AssertionError("missing band disappeared after custom date range")
        panel_text = page.locator(".feature-panel").first.inner_text()
        assert_contains(panel_text, "missing", "panel quality missing text")
        assert_contains(panel_text, "coverage", "panel quality coverage text")

        page.fill("#fromDate", "2025-06-23")
        page.fill("#toDate", "2025-06-24")
        page.locator("#applyDateRange").click()
        inclusive_state = page.evaluate("() => window.driftMetricTimeseriesDemo.getState().time")
        assert_equal(str(inclusive_state["visibleDomain"][0])[:10], "2025-06-23", "inclusive direct start")
        assert_equal(str(inclusive_state["visibleDomain"][1])[:10], "2025-06-25", "inclusive direct end")
        assert_equal(page.locator("#toDate").input_value(), "2025-06-24", "inclusive direct end input")
        inclusive_model = page.evaluate("() => window.driftMetricTimeseriesDemo.buildRenderModel()")
        if len(inclusive_model[0]["series"]) < 2:
            raise AssertionError(f"inclusive direct range should include both selected days, got {len(inclusive_model[0]['series'])} rows")

        page.fill("#anchorDate", "2025-04-01")
        dispatch(page, {"type": "SET_RANGE_PRESET", "preset": "3M", "anchorStart": "2025-04-01T00:00:00Z"})
        anchored = page.evaluate("() => window.driftMetricTimeseriesDemo.getState().time")
        anchored_start = str(anchored["visibleDomain"][0])[:10]
        anchored_end = str(anchored["visibleDomain"][1])[:10]
        assert_equal(anchored["rangePreset"], "3M", "anchored preset range")
        assert_equal(anchored_start, "2025-04-01", "anchored preset start date")
        assert_equal(anchored_end, "2025-07-01", "anchored preset end date")
        assert_equal(str(anchored["rangeAnchorDate"])[:10], "2025-04-01", "anchor date state")

        page.fill("#anchorDate", "2025-05-01")
        dispatch(page, {"type": "SET_RANGE_PRESET", "preset": "3M", "anchorStart": "2025-05-01T00:00:00Z"})
        month_tick_state = page.evaluate("() => window.driftMetricTimeseriesDemo.getState().time")
        assert_equal(month_tick_state["tickInterval"], "1M", "3M range uses monthly ticks")
        x_grid_count = page.locator("#panelStack .feature-panel").first.locator(".x-grid-line").count()
        if x_grid_count < 4:
            raise AssertionError(f"expected monthly x-grid lines, got {x_grid_count}")
        tick_text = page.evaluate(
            """
            () => Array.from(document.querySelectorAll('#panelStack .feature-panel:first-child .tick-label'))
              .map((node) => node.textContent || '')
            """
        )
        if not any("2025-06" in item for item in tick_text):
            raise AssertionError(f"expected month label 2025-06 in x-axis labels, got {tick_text}")

        dom_click(page, "#closeConfig")
        nav = page.locator("#navigator svg")
        nav.scroll_into_view_if_needed()
        nav_box = nav.bounding_box()
        if not nav_box:
            raise AssertionError("navigator has no bounding box")
        selection_before_drag = page.evaluate(
            "() => document.querySelector('#navigator .navigator-selection').getAttribute('x')"
        )
        page.mouse.move(nav_box["x"] + nav_box["width"] * 0.25, nav_box["y"] + nav_box["height"] * 0.45)
        page.mouse.down()
        page.mouse.move(nav_box["x"] + nav_box["width"] * 0.45, nav_box["y"] + nav_box["height"] * 0.45, steps=8)
        selection_during_drag = page.evaluate(
            "() => document.querySelector('#navigator .navigator-selection').getAttribute('x')"
        )
        page.mouse.up()
        if selection_before_drag == selection_during_drag:
            raise AssertionError("navigator selection did not preview movement during drag")
        before_nav = page.evaluate("() => window.driftMetricTimeseriesDemo.getState().time.visibleDomain")
        page.mouse.click(nav_box["x"] + nav_box["width"] * 0.65, nav_box["y"] + nav_box["height"] * 0.45)
        after_nav = page.evaluate("() => window.driftMetricTimeseriesDemo.getState().time.visibleDomain")
        if before_nav == after_nav:
            raise AssertionError("navigator click did not move visibleDomain")

        svg = page.locator(".chart-svg").first
        box = svg.bounding_box()
        if not box:
            raise AssertionError("chart svg has no bounding box")
        page.mouse.move(box["x"] + box["width"] * 0.45, box["y"] + box["height"] * 0.45)
        page.wait_for_timeout(100)
        tooltip_visible = page.locator("#tooltip:not([hidden])").count()
        hover_state = page.evaluate("() => window.driftMetricTimeseriesDemo.getState().view.hoverTimestamp")

        page.set_viewport_size({"width": 720, "height": 900})
        page.wait_for_timeout(100)
        overflow = page.evaluate("() => document.documentElement.scrollWidth > document.documentElement.clientWidth + 2")
        if overflow:
            raise AssertionError("page has horizontal overflow at compact width")

        assert_equal(page.locator("#configDialog[hidden]").count(), 1, "settings dialog closes")
        page.screenshot(path=str(FLOW_SCREENSHOT), full_page=True)
        page.screenshot(path=str(SCREENSHOT), full_page=True)
        browser.close()

    if panels != 3:
        raise AssertionError(f"expected 3 normal panels, got {panels}")
    if missing_bands < 1 or drift_events < 1:
        raise AssertionError("missing bands or drift event bands were not rendered")
    if "coverage" not in summary or "missing" not in summary:
        raise AssertionError("summary does not include coverage/missing information")
    if tooltip_visible != 1 or not hover_state:
        raise AssertionError("hover tooltip/sync failed")


if __name__ == "__main__":
    run()
    print("drift_metric_timeseries demo tests PASS")
    print(f"screenshot: {SCREENSHOT}")
    print(f"flow screenshot: {FLOW_SCREENSHOT}")
