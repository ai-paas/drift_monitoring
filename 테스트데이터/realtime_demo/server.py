from __future__ import annotations

import argparse
import csv
import gzip
import json
import math
import sys
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parents[2]
DEMO_ROOT = Path(__file__).resolve().parent
WEB_ROOT = DEMO_ROOT / "web"
DATA_ROOT = DEMO_ROOT / "data"
ALGORITHM_ROOT = ROOT / "drift_algorithm_impl"
if str(ALGORITHM_ROOT) not in sys.path:
    sys.path.insert(0, str(ALGORITHM_ROOT))

import pandas as pd

from drift_algorithm.methods.streamingchangedetector import detect_adwin


FEATURE_ID = "case010_metric_mean"
CASE_ID = "CASE-010"
CHART_CODE = "CHART-STREAM-001"
METHOD_NAME = "ADWIN"
VARIANT_CODE = "ADWIN_MEAN_STREAM"


def parse_time(value: str) -> datetime:
    normalized = value.replace("Z", "+00:00")
    dt = datetime.fromisoformat(normalized)
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def iso_z(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def std(values: list[float]) -> float:
    if len(values) < 2:
        return 0.0
    m = mean(values)
    return math.sqrt(sum((item - m) ** 2 for item in values) / (len(values) - 1))


class DemoState:
    def __init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        self.raw_buffer: list[dict[str, Any]] = []
        self.hourly: list[dict[str, Any]] = []
        self.events: list[dict[str, Any]] = []
        self.analysis_payloads: dict[str, dict[str, Any]] = {}
        self.last_event_hour: datetime | None = None
        self.next_event_seq = 1
        self.live_cursor_day = 0

    def ingest(self, point: dict[str, Any]) -> dict[str, Any]:
        timestamp = parse_time(str(point["timestamp"]))
        metric = float(point["metric"])
        self.raw_buffer.append(
            {
                "timestamp": timestamp,
                "sample_id": str(point.get("sample_id", "")),
                "metric": metric,
            }
        )
        aggregate = None
        event = None
        if len(self.raw_buffer) >= 60:
            aggregate = self._flush_hour()
            event = self._maybe_detect()
        return {
            "accepted": True,
            "raw_buffer_size": len(self.raw_buffer),
            "hourly_count": len(self.hourly),
            "aggregate": aggregate,
            "event": event,
        }

    def _flush_hour(self) -> dict[str, Any]:
        rows = self.raw_buffer[:60]
        self.raw_buffer = self.raw_buffer[60:]
        values = [float(row["metric"]) for row in rows]
        start = rows[0]["timestamp"].replace(minute=0, second=0, microsecond=0)
        end = start + timedelta(hours=1)
        row = {
            "feature_id": FEATURE_ID,
            "bucket_start": iso_z(start),
            "bucket_end": iso_z(end),
            "resolution": "1h",
            "unit": "score",
            "count": len(values),
            "mean": round(mean(values), 6),
            "min": round(min(values), 6),
            "max": round(max(values), 6),
            "std": round(std(values), 6),
            "status": "observed",
            "coverage": 1.0,
        }
        self.hourly.append(row)
        return row

    def _maybe_detect(self) -> dict[str, Any] | None:
        if len(self.hourly) < 96:
            return None
        current_end = parse_time(self.hourly[-1]["bucket_end"])
        if current_end < parse_time("2026-07-02T00:00:00Z"):
            return None
        if self.last_event_hour and current_end - self.last_event_hour < timedelta(hours=24):
            return None

        current_start = current_end - timedelta(hours=24)
        reference_end = current_start - timedelta(milliseconds=1)
        reference_start = current_start - timedelta(hours=72)
        frame = pd.DataFrame(
            {
                "time": [row["bucket_start"] for row in self.hourly],
                "value": [row["mean"] for row in self.hourly],
            }
        )
        result = detect_adwin(
            frame,
            time_col="time",
            value_col="value",
            reference_window=(iso_z(reference_start), iso_z(reference_end)),
            current_window=(iso_z(current_start), iso_z(current_end)),
            params={
                "variant_id": VARIANT_CODE,
                "delta": 0.05,
                "clock": 1,
                "min_window_length": 8,
                "grace_period": 16,
                "record_events": True,
            },
        )
        if not result.drift_detected:
            return None
        event_id = f"EVT-{self.next_event_seq:06d}"
        self.next_event_seq += 1
        payload = self._build_analysis_payload(
            event_id=event_id,
            result=result,
            reference_start=reference_start,
            reference_end=reference_end,
            current_start=current_start,
            current_end=current_end,
        )
        event = {
            "event_id": event_id,
            "feature_id": FEATURE_ID,
            "label": f"{METHOD_NAME} drift",
            "level": "drift",
            "start": iso_z(current_start),
            "end": iso_z(current_end),
            "score": result.measurements.get("ALARM_COUNT", 1),
            "chart_code": CHART_CODE,
            "method_name": METHOD_NAME,
            "variant_code": VARIANT_CODE,
            "summary_text": result.interpretation,
        }
        self.events.append(event)
        self.analysis_payloads[event_id] = payload
        self.last_event_hour = current_end
        (DATA_ROOT / "analysis_payloads").mkdir(parents=True, exist_ok=True)
        (DATA_ROOT / "analysis_payloads" / f"{event_id}.json").write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return event

    def _window_rows(self, start: datetime, end: datetime) -> list[dict[str, Any]]:
        return [row for row in self.hourly if start <= parse_time(row["bucket_start"]) <= end]

    def _build_analysis_payload(
        self,
        *,
        event_id: str,
        result: Any,
        reference_start: datetime,
        reference_end: datetime,
        current_start: datetime,
        current_end: datetime,
    ) -> dict[str, Any]:
        display_start = reference_start
        display_rows = self._window_rows(display_start, current_end)
        reference_rows = self._window_rows(reference_start, reference_end)
        current_rows = self._window_rows(current_start, current_end)
        ref_mean = mean([row["mean"] for row in reference_rows])
        cur_mean = mean([row["mean"] for row in current_rows])
        delta = cur_mean - ref_mean
        series = [
            {
                "x": index + 1,
                "time": row["bucket_start"],
                "value": row["mean"],
                "rolling_mean": mean([item["mean"] for item in display_rows[max(0, index - 5) : index + 1]]),
                "window_width": max(8, 96 - min(index, 48)),
            }
            for index, row in enumerate(display_rows)
        ]
        alarm_x = len(series)
        return {
            "chartId": CHART_CODE,
            "title": f"{CHART_CODE} - {METHOD_NAME} {VARIANT_CODE}",
            "eventId": event_id,
            "layout": {
                "columns": 3,
                "rows": 2,
                "gridTemplateColumns": "2fr 1fr 1fr",
                "areas": [
                    {"area": "stream", "x": 0, "y": 0, "w": 2, "h": 2, "title": "스트림 평균 상승", "role": "main"},
                    {"area": "window", "x": 2, "y": 0, "w": 1, "h": 1, "title": "적응형 윈도 폭"},
                    {"area": "summary", "x": 2, "y": 1, "w": 1, "h": 1, "title": "경보 전후 평균", "role": "summary"},
                ],
            },
            "data": {
                "stream": series,
                "window": [{"x": row["x"], "value": row["window_width"]} for row in series],
                "means": [
                    {"label": "reference", "value": round(ref_mean, 6)},
                    {"label": "current", "value": round(cur_mean, 6)},
                    {"label": "delta", "value": round(delta, 6)},
                ],
                "events": [{"x": alarm_x, "label": "ADWIN alarm", "level": "drift"}],
            },
            "components": [
                {
                    "area": "stream",
                    "componentType": "trend_line",
                    "componentInstanceId": "stream_metric",
                    "dataBinding": {"source": "stream", "x": "x", "y": "value"},
                    "interpretationNote": {
                        "title": "stream metric",
                        "summary": "reference/current hourly mean stream and ADWIN alarm point.",
                    },
                },
                {
                    "area": "stream",
                    "componentType": "trend_line",
                    "componentInstanceId": "rolling_mean",
                    "dataBinding": {"source": "stream", "x": "x", "y": "rolling_mean"},
                    "isOverlay": True,
                },
                {
                    "area": "stream",
                    "componentType": "event_marker",
                    "componentInstanceId": "alarm_marker",
                    "dataBinding": {"source": "events", "x": "x"},
                    "isOverlay": True,
                },
                {
                    "area": "window",
                    "componentType": "window_view",
                    "componentInstanceId": "adwin_window",
                    "dataBinding": {"source": "window", "x": "x", "y": "value"},
                },
                {
                    "area": "summary",
                    "componentType": "bar_chart",
                    "componentInstanceId": "mean_delta",
                    "dataBinding": {"source": "means", "x": "label", "y": "value"},
                },
            ],
            "methodResult": {
                "drift_detected": result.drift_detected,
                "severity": result.severity,
                "threshold": result.threshold,
                "measurements": result.measurements,
                "interpretation": result.interpretation,
                "warnings": result.warnings,
            },
            "adapter": {
                "adapter_id": "adwin_mean_stream_to_chart_stream_001",
                "adapter_version": "v1",
            },
        }

    def live_payload(self) -> dict[str, Any]:
        if not self.hourly:
            domain = ["2026-01-01T00:00:00.000Z", "2026-01-02T00:00:00.000Z"]
        else:
            domain = [self.hourly[0]["bucket_start"], self.hourly[-1]["bucket_end"]]
        return {
            "ok": True,
            "features": [
                {
                    "featureId": FEATURE_ID,
                    "label": "CASE-010 metric mean",
                    "unit": "score",
                    "description": "CASE-010 hourly metric mean from realtime ingest",
                    "defaultYScale": "auto",
                    "missingPolicy": {"calendarMode": "always", "showClosed": False, "allowImputed": False},
                }
            ],
            "fullDomain": domain,
            "loadedDomain": domain,
            "dayEnd": domain[1],
            "cursor": len(self.hourly),
            "done": False,
            "series": {FEATURE_ID: self.hourly},
            "seriesByResolution": {FEATURE_ID: {"1h": self.hourly, "1d": daily_summary(self.hourly)}},
            "events": {FEATURE_ID: self.events},
        }


STATE = DemoState()


def daily_summary(hourly: list[dict[str, Any]]) -> list[dict[str, Any]]:
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in hourly:
        groups[row["bucket_start"][:10]].append(row)
    result = []
    for day, rows in sorted(groups.items()):
        values = [row["mean"] for row in rows]
        result.append(
            {
                "feature_id": FEATURE_ID,
                "bucket_start": f"{day}T00:00:00.000Z",
                "bucket_end": iso_z(parse_time(f"{day}T00:00:00Z") + timedelta(days=1)),
                "resolution": "1d",
                "unit": "score",
                "count": sum(int(row["count"]) for row in rows),
                "mean": round(mean(values), 6),
                "min": round(min(values), 6),
                "max": round(max(values), 6),
                "status": "observed",
                "coverage": 1.0,
            }
        )
    return result


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, directory=str(WEB_ROOT), **kwargs)

    def do_OPTIONS(self) -> None:
        self.send_response(204)
        self._cors_headers()
        self.end_headers()

    def do_POST(self) -> None:
        if self.path == "/api/ingest":
            self._json(STATE.ingest(self._read_json()))
            return
        if self.path == "/api/drift-metric-timeseries/live/reset":
            payload = self._read_json_if_present()
            if payload.get("reset") is True:
                STATE.reset()
            self._json({"ok": True})
            return
        if self.path == "/api/drift-demo/reset":
            STATE.reset()
            self._json({"ok": True})
            return
        self.send_error(404)

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/api/health":
            self._json({"ok": True, "service": "realtime-drift-demo"})
            return
        if parsed.path == "/api/drift-demo/status":
            self._json(
                {
                    "ok": True,
                    "case_id": CASE_ID,
                    "chart_code": CHART_CODE,
                    "method_name": METHOD_NAME,
                    "variant_code": VARIANT_CODE,
                    "raw_buffer_size": len(STATE.raw_buffer),
                    "hourly_count": len(STATE.hourly),
                    "event_count": len(STATE.events),
                    "first_hour": STATE.hourly[0]["bucket_start"] if STATE.hourly else None,
                    "latest_hour": STATE.hourly[-1]["bucket_end"] if STATE.hourly else None,
                    "latest_event": STATE.events[-1] if STATE.events else None,
                }
            )
            return
        if parsed.path == "/api/drift-metric-timeseries/live/next-day":
            self._json(STATE.live_payload())
            return
        if parsed.path == "/api/drift-metric-timeseries/events/analyze":
            self._json(self._analysis_response(parse_qs(parsed.query)))
            return
        if parsed.path.startswith("/api/events/") and parsed.path.endswith("/analysis"):
            event_id = parsed.path.split("/")[3]
            payload = STATE.analysis_payloads.get(event_id)
            self._json({"ok": bool(payload), "payload": payload, "error": None if payload else "unknown event"})
            return
        return super().do_GET()

    def _analysis_response(self, query: dict[str, list[str]]) -> dict[str, Any]:
        start = query.get("start", [""])[0]
        event = next((item for item in STATE.events if item["start"] == start), None)
        if not event:
            event = STATE.events[-1] if STATE.events else None
        if not event:
            return {"ok": False, "error": "no drift event has been detected yet"}
        return {"ok": True, "payload": STATE.analysis_payloads[event["event_id"]]}

    def _read_json(self) -> dict[str, Any]:
        length = int(self.headers.get("Content-Length", "0"))
        return json.loads(self.rfile.read(length).decode("utf-8"))

    def _read_json_if_present(self) -> dict[str, Any]:
        length = int(self.headers.get("Content-Length", "0"))
        if length <= 0:
            return {}
        body = self.rfile.read(length).decode("utf-8").strip()
        if not body:
            return {}
        return json.loads(body)

    def _json(self, payload: dict[str, Any]) -> None:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(200)
        self._cors_headers()
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _cors_headers(self) -> None:
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")


def load_case_rows(start: str | None = None, limit: int | None = None) -> list[dict[str, Any]]:
    path = ROOT / "테스트데이터" / "CASE-010_stream_numeric_mean_shift" / "data.csv.gz"
    rows: list[dict[str, Any]] = []
    start_dt = parse_time(start) if start else None
    with gzip.open(path, "rt", encoding="utf-8", newline="") as file:
        for row in csv.DictReader(file):
            ts = parse_time(row["timestamp"])
            if start_dt and ts < start_dt:
                continue
            rows.append(row)
            if limit and len(rows) >= limit:
                break
    return rows


def warmup(start: str, minutes: int) -> None:
    for row in load_case_rows(start=start, limit=minutes):
        STATE.ingest({"timestamp": row["timestamp"], "sample_id": row["sample_id"], "metric": row["metric"]})


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8771)
    parser.add_argument("--warmup-start", default=None)
    parser.add_argument("--warmup-minutes", type=int, default=0)
    args = parser.parse_args()
    if args.warmup_start and args.warmup_minutes:
        warmup(args.warmup_start, args.warmup_minutes)
    server = ThreadingHTTPServer((args.host, args.port), Handler)
    print(f"Realtime drift demo: http://{args.host}:{args.port}/index.html")
    server.serve_forever()


if __name__ == "__main__":
    main()
