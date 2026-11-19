from __future__ import annotations

import csv

from fastapi.testclient import TestClient

import shared.dev_db as dev_db
from test_feeder_server.app.main import app
from test_feeder_server.app.state import state


def test_feeder_caches_replay_window_at_registration(tmp_path, monkeypatch) -> None:
    db_path = tmp_path / "test_feeder.sqlite3"
    monkeypatch.setattr(dev_db, "DEFAULT_DB_PATH", db_path)
    state.reset()

    csv_path = tmp_path / "case.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["timestamp", "metric"])
        writer.writeheader()
        for minute in range(10):
            writer.writerow(
                {
                    "timestamp": f"2026-07-01T00:{minute:02d}:00Z",
                    "metric": str(minute),
                }
            )

    client = TestClient(app)
    register = client.post(
        "/api/test-feeder/feeders",
        json={
            "sourceId": "cached-source",
            "datasetCaseId": "CASE-CACHED",
            "csvPath": str(csv_path),
            "startTime": "2026-07-01T00:02:00Z",
            "maxRows": 3,
            "replayWindow": {
                "start": "2026-07-01T00:02:00Z",
                "end": "2026-07-01T00:08:00Z",
            },
        },
    )

    assert register.json()["data"]["cachedRows"] == 3
    csv_path.unlink()

    first_tick = client.post(
        "/api/test-feeder/feeders/cached-source/tick",
        json={"logicalNow": "2026-07-01T00:04:00Z"},
    ).json()
    second_tick = client.post(
        "/api/test-feeder/feeders/cached-source/tick",
        json={"logicalNow": "2026-07-01T00:06:00Z"},
    ).json()

    assert first_tick["data"]["insertedRowsThisTick"] == 2
    assert first_tick["data"]["insertedRows"] == 2
    assert second_tick["data"]["insertedRowsThisTick"] == 1
    assert second_tick["data"]["insertedRows"] == 3
    assert client.get("/api/test-feeder/feeders/cached-source/status").json()["data"]["cachedRows"] == 3

    client.post("/api/test-feeder/reset", json={"sourceId": "cached-source"})
    warm_register = client.post(
        "/api/test-feeder/feeders",
        json={
            "sourceId": "cached-source",
            "datasetCaseId": "CASE-CACHED",
            "csvPath": str(csv_path),
            "startTime": "2026-07-01T00:02:00Z",
            "maxRows": 3,
            "replayWindow": {
                "start": "2026-07-01T00:02:00Z",
                "end": "2026-07-01T00:08:00Z",
            },
        },
    )
    assert warm_register.json()["data"]["cachedRows"] == 3
