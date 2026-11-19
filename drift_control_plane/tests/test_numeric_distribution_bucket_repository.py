from __future__ import annotations

import json

from drift_server.app.repositories.bucket_repository import BucketRepository


class _FakeConn:
    def __init__(self, rows: list[dict[str, object]]) -> None:
        self.rows = rows

    def execute(self, query: str, params: tuple[object, ...]) -> "_FakeCursor":
        return _FakeCursor(self.rows)


class _FakeCursor:
    def __init__(self, rows: list[dict[str, object]]) -> None:
        self.rows = rows

    def fetchall(self) -> list[dict[str, object]]:
        return self.rows


def test_numeric_distribution_window_stats_preserves_pair_id_when_present() -> None:
    conn = _FakeConn(
        [
            {
                "event_time": "2026-06-30T23:00:00Z",
                "metric": 10.0,
                "payload_json": json.dumps({"score": "10.0", "period": "reference", "pair_id": "pair-001"}),
            }
        ]
    )

    stats = BucketRepository(conn).numeric_distribution_window_stats(
        "c004-paired",
        "2026-06-30T23:00:00Z",
        "2026-07-01T01:00:00Z",
    )

    assert stats["values"][0]["pair_id"] == "pair-001"


def test_multivariate_window_stats_preserves_configured_features() -> None:
    conn = _FakeConn(
        [
            {
                "event_time": "2026-12-01T00:00:00Z",
                "metric": 1.0,
                "payload_json": json.dumps({"x1": "1.0", "x2": "2.0", "x3": "3.0", "period": "reference"}),
            }
        ]
    )

    stats = BucketRepository(conn).multivariate_window_stats(
        "case-014",
        "2026-12-01T00:00:00Z",
        "2026-12-01T01:00:00Z",
        ["x1", "x2", "x3"],
    )

    assert stats["row_count"] == 1
    assert stats["feature_columns"] == ["x1", "x2", "x3"]
    assert stats["values"][0]["features"] == {"x1": 1.0, "x2": 2.0, "x3": 3.0}
