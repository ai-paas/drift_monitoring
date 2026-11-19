from __future__ import annotations

import json
import sqlite3

from drift_server.app.repositories.bucket_repository import BucketRepository


def test_prediction_window_stats_derives_error_from_label_and_model_prediction() -> None:
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute(
        """
        CREATE TABLE raw_event (
            source_id TEXT NOT NULL,
            event_time TEXT NOT NULL,
            row_index INTEGER NOT NULL,
            metric REAL,
            payload_json TEXT NOT NULL
        )
        """
    )
    rows = [
        ("case-012-dataset", "2026-09-01T00:00:00Z", 0, 0.0, {"label": 1, "model_prediction": 1}),
        ("case-012-dataset", "2026-09-01T00:01:00Z", 1, 0.0, {"label": 0, "model_prediction": 1}),
        ("case-012-dataset", "2026-09-01T00:02:00Z", 2, 0.0, {"label": 1, "model_prediction": 0}),
    ]
    conn.executemany(
        """
        INSERT INTO raw_event (source_id, event_time, row_index, metric, payload_json)
        VALUES (?, ?, ?, ?, ?)
        """,
        [(source_id, event_time, row_index, metric, json.dumps(payload)) for source_id, event_time, row_index, metric, payload in rows],
    )

    stats = BucketRepository(conn).prediction_window_stats(
        "case-012-dataset",
        "2026-09-01T00:00:00Z",
        "2026-09-01T00:03:00Z",
    )

    assert stats["row_count"] == 3
    assert stats["error_count"] == 2
    assert stats["error_rate"] == 2 / 3
    assert [row["error"] for row in stats["errors"]] == [0, 1, 1]
    assert [row["y_true"] for row in stats["errors"]] == [1, 0, 1]
    assert [row["y_pred"] for row in stats["errors"]] == [1, 1, 0]

