from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone

from playwright.sync_api import sync_playwright


ROOT = Path(__file__).resolve().parents[2]
PROJECT_DIR = ROOT / "drift_metric_timeseries"
HARNESS = (PROJECT_DIR / "web" / "drift_metric_timeseries_harness.html").as_uri()


def fail(message: str) -> None:
    raise AssertionError(message)


def dispatch(page, action: dict) -> None:
    page.evaluate("action => window.driftMetricTimeseriesHarness.dispatch(action)", action)


def state(page) -> dict:
    return page.evaluate("() => window.driftMetricTimeseriesHarness.getState()")


def render_model(page) -> list[dict]:
    return page.evaluate("() => window.driftMetricTimeseriesHarness.buildRenderModel()")


def assert_invariants(page, label: str) -> None:
    current = state(page)
    panels = render_model(page)
    time = current["time"]
    view = current["view"]
    full_start, full_end = time["fullDomain"]
    visible_start, visible_end = time["visibleDomain"]
    if visible_start < full_start or visible_end > full_end:
      fail(f"{label}: visibleDomain escaped fullDomain")
    if visible_start >= visible_end:
      fail(f"{label}: visibleDomain start must be before end")

    expected_order = [view["primaryFeature"], *view["comparisonFeatures"]]
    if view["panelOrder"] != expected_order:
      fail(f"{label}: panelOrder mismatch {view['panelOrder']} != {expected_order}")
    if len(view["comparisonFeatures"]) != len(set(view["comparisonFeatures"])):
      fail(f"{label}: duplicate comparison features")
    if view["primaryFeature"] in view["comparisonFeatures"]:
      fail(f"{label}: primary feature leaked into comparison list")
    if len(panels) != len(expected_order):
      fail(f"{label}: render panel count mismatch")
    if panels:
      x_domain = panels[0]["xDomain"]
      tick = panels[0]["tickInterval"]
      bucket = panels[0]["displayBucket"]
      for panel in panels:
        if panel["xDomain"] != x_domain:
          fail(f"{label}: shared xDomain mismatch")
        if panel["tickInterval"] != tick:
          fail(f"{label}: shared tick mismatch")
        if panel["displayBucket"] != bucket:
          fail(f"{label}: shared display bucket mismatch")


def iso_date(value) -> str:
    if isinstance(value, datetime):
        return value.astimezone(timezone.utc).strftime("%Y-%m-%d")
    return str(value)[:10]


def run_tests() -> None:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1440, "height": 1100})
        page.goto(HARNESS)
        page.wait_for_selector("#timeView")

        assert_invariants(page, "initial")

        scenarios = [
            ("all domain", {"type": "SET_RANGE_PRESET", "preset": "ALL"}),
            ("add token", {"type": "ADD_COMPARISON_FEATURE", "featureId": "token_length"}),
            ("add refusal", {"type": "ADD_COMPARISON_FEATURE", "featureId": "refusal_rate"}),
            ("add duplicate refusal", {"type": "ADD_COMPARISON_FEATURE", "featureId": "refusal_rate"}),
            ("add latency", {"type": "ADD_COMPARISON_FEATURE", "featureId": "latency_ms"}),
            ("scale hour", {"type": "SET_SCALE_MODE", "scaleMode": "hour"}),
            ("preset 24h", {"type": "SET_RANGE_PRESET", "preset": "24H"}),
            ("pan previous", {"type": "PAN_BY_DELTA", "direction": -1}),
            ("pan next", {"type": "PAN_BY_DELTA", "direction": 1}),
            ("set refusal loading", {"type": "SET_FEATURE_STATUS", "featureId": "refusal_rate", "status": "loading"}),
            ("set refusal error", {"type": "SET_FEATURE_STATUS", "featureId": "refusal_rate", "status": "error"}),
            ("hover", {"type": "SET_HOVER_MIDDLE"}),
            ("expanded", {"type": "TOGGLE_EXPANDED"}),
            ("scale month", {"type": "SET_SCALE_MODE", "scaleMode": "month"}),
            ("preset 1y", {"type": "SET_RANGE_PRESET", "preset": "1Y"}),
            ("remove last", {"type": "REMOVE_LAST_COMPARISON_FEATURE"}),
        ]
        for label, action in scenarios:
            dispatch(page, action)
            assert_invariants(page, label)

        after_duplicate = state(page)
        if after_duplicate["view"]["comparisonFeatures"].count("refusal_rate") > 1:
            fail("duplicate feature was not removed")

        refusal_status = state(page)["dataStore"]["byFeature"]["refusal_rate"]["status"]
        if refusal_status != "error":
            fail(f"feature status should remain error, got {refusal_status}")

        before_primary_change = state(page)["time"]["visibleDomain"]
        dispatch(page, {"type": "SET_PRIMARY_FEATURE", "featureId": "token_length"})
        assert_invariants(page, "primary change")
        after_primary_change = state(page)
        if after_primary_change["time"]["visibleDomain"] != before_primary_change:
            fail("primary feature change should not mutate visibleDomain")
        if "token_length" in after_primary_change["view"]["comparisonFeatures"]:
            fail("primary feature should be removed from comparisonFeatures")

        dispatch(page, {"type": "SET_VISIBLE_DOMAIN", "domain": ["2018-01-01T00:00:00Z", "2030-01-01T00:00:00Z"]})
        assert_invariants(page, "wide custom clamp")
        full_domain = state(page)["time"]["fullDomain"]
        clamped = state(page)["time"]["visibleDomain"]
        if iso_date(clamped[0]) != iso_date(full_domain[0]) or iso_date(clamped[1]) != iso_date(full_domain[1]):
            fail(f"wide custom domain should clamp to fullDomain, got {clamped}")

        dispatch(page, {"type": "SET_VISIBLE_DOMAIN", "domain": ["2025-09-01T00:00:00Z", "2026-02-01T00:00:00Z"]})
        dispatch(page, {"type": "SET_PRIMARY_FEATURE", "featureId": "embedding_distance"})
        assert_invariants(page, "event overlap domain")
        embedding = next(panel for panel in render_model(page) if panel["featureId"] == "embedding_distance")
        if embedding["driftCount"] < 1:
            fail("expected embedding drift event in 2025-09..2026-02 window")
        quality = embedding["quality"]
        if quality["missingBuckets"] < 2:
            fail(f"expected missing buckets in embedding gap window, got {quality}")
        if quality["imputedBuckets"] < 1:
            fail(f"expected imputed bucket in embedding gap window, got {quality}")
        if quality["gapCount"] < 1:
            fail(f"expected at least one missing gap segment, got {quality}")
        if quality["coverage"] >= 1:
            fail(f"coverage should be below 100% when missing buckets exist, got {quality}")
        if embedding["visiblePoints"] >= quality["expectedBuckets"]:
            fail("visiblePoints should not count missing buckets as real points")

        dispatch(page, {"type": "SET_VISIBLE_DOMAIN", "domain": ["2025-07-01T00:00:00Z", "2025-09-01T00:00:00Z"]})
        assert_invariants(page, "partial closed window")
        embedding = next(panel for panel in render_model(page) if panel["featureId"] == "embedding_distance")
        quality = embedding["quality"]
        if quality["partialBuckets"] < 1 or quality["closedBuckets"] < 1:
            fail(f"expected partial and closed buckets in 2025-07..2025-09, got {quality}")
        if quality["expectedBuckets"] != quality["observedBuckets"] + quality["missingBuckets"] + quality["imputedBuckets"] + quality["partialBuckets"]:
            fail(f"closed buckets should be excluded from expected denominator, got {quality}")

        dispatch(page, {"type": "SET_VISIBLE_DOMAIN", "domain": ["2026-03-01T00:00:00Z", "2026-05-01T00:00:00Z"]})
        dispatch(page, {"type": "SET_PRIMARY_FEATURE", "featureId": "refusal_rate"})
        assert_invariants(page, "refusal missing partial window")
        refusal = next(panel for panel in render_model(page) if panel["featureId"] == "refusal_rate")
        if refusal["quality"]["missingBuckets"] < 1 or refusal["quality"]["partialBuckets"] < 1:
            fail(f"expected refusal missing and partial buckets, got {refusal['quality']}")

        browser.close()


if __name__ == "__main__":
    run_tests()
    print("drift_metric_timeseries harness tests PASS")
