from __future__ import annotations

import json

from drift_server.app.repositories.bucket_repository import BucketRepository


class _FakeConn:
    def __init__(self, rows: list[dict[str, object]]) -> None:
        self.rows = rows
        self.calls: list[tuple[str, tuple[object, ...]]] = []

    def execute(self, query: str, params: tuple[object, ...]) -> "_FakeCursor":
        self.calls.append((query, params))
        return _FakeCursor(self.rows)


class _FakeCursor:
    def __init__(self, rows: list[dict[str, object]]) -> None:
        self.rows = rows

    def fetchall(self) -> list[dict[str, object]]:
        return self.rows


def test_categorical_count_window_stats_builds_category_count_payload() -> None:
    conn = _FakeConn(
        [
            {
                "event_time": "2026-06-30T23:10:00Z",
                "payload_json": json.dumps({"category": "approved", "count": "40", "period": "reference"}),
            },
            {
                "event_time": "2026-07-01T00:10:00Z",
                "payload_json": json.dumps({"category": "declined", "count": "40", "period": "current"}),
            },
        ]
    )

    stats = BucketRepository(conn).categorical_count_window_stats(
        "c004-cat",
        "2026-06-30T23:00:00Z",
        "2026-07-01T01:00:00Z",
    )

    assert stats["row_count"] == 2
    assert stats["mean_value"] == 40.0
    assert stats["values"] == [
        {
            "time": "2026-06-30T23:10:00Z",
            "category": "approved",
            "count": 40.0,
            "period": "reference",
        },
        {
            "time": "2026-07-01T00:10:00Z",
            "category": "declined",
            "count": 40.0,
            "period": "current",
        },
    ]
