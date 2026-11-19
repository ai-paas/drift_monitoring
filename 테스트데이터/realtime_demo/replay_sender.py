from __future__ import annotations

import argparse
import csv
import gzip
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[2]
DATA_PATH = ROOT / "테스트데이터" / "CASE-010_stream_numeric_mean_shift" / "data.csv.gz"


def parse_time(value: str) -> datetime:
    dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def post_json(url: str, payload: dict[str, object]) -> dict[str, object]:
    data = json.dumps(payload).encode("utf-8")
    request = Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")
    with urlopen(request, timeout=10) as response:
        return json.loads(response.read().decode("utf-8"))


def iter_rows(start: str | None, limit: int | None):
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


def main() -> None:
    parser = argparse.ArgumentParser(description="Replay CASE-010 rows into realtime demo ingest API.")
    parser.add_argument("--url", default="http://127.0.0.1:8771/api/ingest")
    parser.add_argument("--start", default="2026-06-25 00:00:00")
    parser.add_argument("--limit", type=int, default=14 * 24 * 60)
    parser.add_argument("--delay", type=float, default=1.0, help="Seconds between rows. Use 0 for fast test.")
    args = parser.parse_args()
    for index, row in enumerate(iter_rows(args.start, args.limit), start=1):
        response = post_json(
            args.url,
            {
                "timestamp": row["timestamp"],
                "case_id": row["case_id"],
                "sample_id": row["sample_id"],
                "metric": float(row["metric"]),
            },
        )
        if response.get("event"):
            print(f"event {response['event']['event_id']} at row {index}")
        if index % 60 == 0:
            print(f"sent {index} rows; hourly_count={response.get('hourly_count')}")
        if args.delay:
            time.sleep(args.delay)


if __name__ == "__main__":
    main()

