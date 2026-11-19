from __future__ import annotations

from typing import Any

from drift_server.app.payload_adapter import build_payload as build_bound_payload


def _display_value(value: Any) -> str:
    if isinstance(value, float):
        return f"{value:.4f}"
    return str(value)


def build_payload(context: dict[str, Any]) -> dict[str, Any]:
    payload = build_bound_payload(context, "adwin_mean_stream_to_chart_stream_001")
    event = context["driftEvent"]
    points = [
        {
            "t": bucket["bucketEnd"],
            "v": bucket["v"],
            "windowStart": bucket["bucketStart"],
            "windowEnd": bucket["bucketEnd"],
            "rowCount": bucket["count"],
        }
        for bucket in context["buckets"]
    ]
    for row in payload["data"].get("chart.CHART-STREAM-001.summary", []):
        if row.get("label") == "score":
            row["displayValue"] = _display_value(event["score"])
    payload["title"] = (context["analysisChart"].get("chartOptions") or {}).get("title", payload["title"])
    payload["series"] = [{"seriesId": "metric_mean", "label": "Metric mean", "points": points}]
    payload["eventMarkers"] = [
        {
            "eventId": event["eventId"],
            "t": event["eventEnd"],
            "level": event["level"],
            "score": event["score"],
        }
    ]
    payload["annotations"] = [
        {
            "type": "event-window",
            "start": event["eventStart"],
            "end": event["eventEnd"],
            "level": event["level"],
        }
    ]
    return payload
