from __future__ import annotations

import sqlite3

from shared import dev_db


def test_connect_initializes_schema_once_per_process_db_path(tmp_path, monkeypatch) -> None:
    db_path = tmp_path / "dev.sqlite3"
    seed_calls = 0

    def fake_seed(conn: sqlite3.Connection) -> None:
        nonlocal seed_calls
        seed_calls += 1

    monkeypatch.setattr(dev_db, "_seed_managed_contracts", fake_seed)
    dev_db._SCHEMA_INITIALIZED_DB_PATHS.discard(str(db_path.resolve()))

    with dev_db.connect(db_path) as conn:
        conn.execute("INSERT INTO feed_state (source_id) VALUES ('source-a')")
        conn.commit()
    with dev_db.connect(db_path) as conn:
        row = conn.execute("SELECT COUNT(*) AS count FROM feed_state").fetchone()

    assert seed_calls == 1
    assert row["count"] == 1

