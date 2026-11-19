from __future__ import annotations

import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import data_server
import server


def main() -> None:
    server.STATE.reset()
    original_post_json = data_server.post_json

    def local_post_json(url, payload):
        return server.STATE.ingest(payload)

    data_server.post_json = local_post_json
    data_server.STATE.start(
        {
            "target_url": "local-test",
            "start": "2026-06-25 00:00:00",
            "limit": 14 * 24 * 60,
            "interval_seconds": 0,
        }
    )
    try:
        while data_server.STATE.status()["running"]:
            time.sleep(0.01)
    finally:
        data_server.post_json = original_post_json

    drift_status = server.STATE.live_payload()
    sender_status = data_server.STATE.status()
    event_count = len(server.STATE.events)
    assert sender_status["sent_count"] == 14 * 24 * 60, sender_status
    assert len(server.STATE.hourly) == 14 * 24, len(server.STATE.hourly)
    assert event_count >= 1, "expected drift event"
    result = {
        "sender": sender_status,
        "drift_server": {
            "hourly_count": len(server.STATE.hourly),
            "event_count": event_count,
            "first_event": server.STATE.events[0],
            "live_series_count": len(drift_status["seriesByResolution"]["case010_metric_mean"]["1h"]),
        },
    }
    out = Path(__file__).resolve().parent / "data" / "system_smoke_test_result.json"
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
