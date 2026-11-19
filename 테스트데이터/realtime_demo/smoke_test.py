from __future__ import annotations

import json
from pathlib import Path

import server


def main() -> None:
    server.STATE.reset()
    server.warmup("2026-06-25 00:00:00", 14 * 24 * 60)
    payload = server.STATE.live_payload()
    event_count = len(server.STATE.events)
    hourly_count = len(server.STATE.hourly)
    assert hourly_count == 14 * 24, hourly_count
    assert event_count >= 1, "expected at least one drift event"
    event = server.STATE.events[0]
    analysis = server.STATE.analysis_payloads[event["event_id"]]
    assert analysis["chartId"] == "CHART-STREAM-001"
    assert analysis["methodResult"]["drift_detected"] is True
    summary = {
        "hourly_count": hourly_count,
        "event_count": event_count,
        "first_event": event,
        "analysis_chart": analysis["chartId"],
        "adapter": analysis["adapter"],
        "live_payload_series_count": len(payload["seriesByResolution"]["case010_metric_mean"]["1h"]),
    }
    out = Path(__file__).resolve().parent / "data" / "smoke_test_result.json"
    out.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

