from __future__ import annotations

import argparse
import csv
import gzip
import json
import threading
import time
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[2]
DATA_PATH = ROOT / "테스트데이터" / "CASE-010_stream_numeric_mean_shift" / "data.csv.gz"
DEFAULT_TARGET_URL = "http://127.0.0.1:8771/api/ingest"


def parse_time(value: str) -> datetime:
    dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def post_json(url: str, payload: dict[str, Any]) -> dict[str, Any]:
    data = json.dumps(payload).encode("utf-8")
    request = Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")
    with urlopen(request, timeout=10) as response:
        return json.loads(response.read().decode("utf-8"))


def iter_case_rows(start: str | None, limit: int | None):
    start_dt = parse_time(start) if start else None
    sent = 0
    with gzip.open(DATA_PATH, "rt", encoding="utf-8", newline="") as file:
        for row in csv.DictReader(file):
            if start_dt and parse_time(row["timestamp"]) < start_dt:
                continue
            yield row
            sent += 1
            if limit and sent >= limit:
                return


class SenderState:
    def __init__(self) -> None:
        self.lock = threading.Lock()
        self.thread: threading.Thread | None = None
        self.stop_event = threading.Event()
        self.running = False
        self.target_url = DEFAULT_TARGET_URL
        self.start_timestamp = "2026-01-01 00:00:00"
        self.limit: int | None = None
        self.interval_seconds = 1.0
        self.sent_count = 0
        self.hourly_count = 0
        self.event_count = 0
        self.latest_source_timestamp: str | None = None
        self.latest_error: str | None = None
        self.latest_event: dict[str, Any] | None = None
        self.started_at: float | None = None
        self.finished_at: float | None = None

    def status(self) -> dict[str, Any]:
        with self.lock:
            return {
                "ok": True,
                "running": self.running,
                "target_url": self.target_url,
                "start_timestamp": self.start_timestamp,
                "limit": self.limit,
                "interval_seconds": self.interval_seconds,
                "sent_count": self.sent_count,
                "simulated_minutes_sent": self.sent_count,
                "simulated_hours_completed": self.sent_count // 60,
                "hourly_count": self.hourly_count,
                "event_count": self.event_count,
                "latest_source_timestamp": self.latest_source_timestamp,
                "latest_event": self.latest_event,
                "latest_error": self.latest_error,
                "started_at": self.started_at,
                "finished_at": self.finished_at,
            }

    def start(self, payload: dict[str, Any]) -> dict[str, Any]:
        with self.lock:
            if self.running:
                return {"ok": False, "error": "sender is already running"}
            self.target_url = str(payload.get("target_url") or DEFAULT_TARGET_URL)
            self.start_timestamp = str(payload.get("start") or "2026-01-01 00:00:00")
            self.limit = int(payload["limit"]) if payload.get("limit") is not None else None
            self.interval_seconds = float(payload.get("interval_seconds", 1.0))
            self.sent_count = 0
            self.hourly_count = 0
            self.event_count = 0
            self.latest_source_timestamp = None
            self.latest_error = None
            self.latest_event = None
            self.started_at = time.time()
            self.finished_at = None
            self.stop_event.clear()
            self.running = True
            self.thread = threading.Thread(target=self._run, daemon=True)
            self.thread.start()
        return {"ok": True, "status": self.status()}

    def stop(self) -> dict[str, Any]:
        self.stop_event.set()
        return {"ok": True, "status": self.status()}

    def _run(self) -> None:
        try:
            for row in iter_case_rows(self.start_timestamp, self.limit):
                if self.stop_event.is_set():
                    break
                response = post_json(
                    self.target_url,
                    {
                        "timestamp": row["timestamp"],
                        "case_id": row["case_id"],
                        "sample_id": row["sample_id"],
                        "metric": float(row["metric"]),
                    },
                )
                with self.lock:
                    self.sent_count += 1
                    self.hourly_count = int(response.get("hourly_count") or self.hourly_count)
                    self.latest_source_timestamp = row["timestamp"]
                    if response.get("event"):
                        self.event_count += 1
                        self.latest_event = response["event"]
                if self.interval_seconds > 0:
                    time.sleep(self.interval_seconds)
        except Exception as exc:  # noqa: BLE001 - demo server records external send failures.
            with self.lock:
                self.latest_error = str(exc)
        finally:
            with self.lock:
                self.running = False
                self.finished_at = time.time()


STATE = SenderState()


class Handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self) -> None:
        self.send_response(204)
        self._cors_headers()
        self.end_headers()

    def do_GET(self) -> None:
        if self.path == "/api/health":
            self._json({"ok": True, "service": "case-010-data-server"})
            return
        if self.path == "/api/status":
            self._json(STATE.status())
            return
        self.send_error(404)

    def do_POST(self) -> None:
        if self.path == "/api/start":
            self._json(STATE.start(self._read_json_if_present()))
            return
        if self.path == "/api/stop":
            self._json(STATE.stop())
            return
        self.send_error(404)

    def _read_json_if_present(self) -> dict[str, Any]:
        length = int(self.headers.get("Content-Length", "0"))
        if length <= 0:
            return {}
        body = self.rfile.read(length).decode("utf-8").strip()
        return json.loads(body) if body else {}

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


def main() -> None:
    parser = argparse.ArgumentParser(description="CASE-010 external data server.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8772)
    parser.add_argument("--auto-start", action="store_true")
    parser.add_argument("--target-url", default=DEFAULT_TARGET_URL)
    parser.add_argument("--start", default="2026-01-01 00:00:00")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--interval-seconds", type=float, default=1.0)
    args = parser.parse_args()
    if args.auto_start:
        STATE.start(
            {
                "target_url": args.target_url,
                "start": args.start,
                "limit": args.limit,
                "interval_seconds": args.interval_seconds,
            }
        )
    server = ThreadingHTTPServer((args.host, args.port), Handler)
    print(f"CASE-010 data server: http://{args.host}:{args.port}/api/status")
    server.serve_forever()


if __name__ == "__main__":
    main()

