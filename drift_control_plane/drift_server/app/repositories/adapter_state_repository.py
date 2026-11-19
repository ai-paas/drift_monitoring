from __future__ import annotations

from typing import Any

from drift_server.app.diagnostics import decode_diagnostics, encode_diagnostics


class AdapterStateRepository:
    def __init__(self, conn: Any) -> None:
        self.conn = conn

    def get(self, adapter_id: str) -> Any:
        return self.conn.execute("SELECT * FROM adapter_state WHERE adapter_id = ?", (adapter_id,)).fetchone()

    def upsert_ready(self, adapter_id: str, source_id: str) -> None:
        self.conn.execute(
            """
            INSERT INTO adapter_state (adapter_id, source_id, cursor_time, status, poll_count, updated_at)
            VALUES (?, ?, NULL, 'ready', 0, CURRENT_TIMESTAMP)
            ON CONFLICT(adapter_id) DO UPDATE SET
                source_id = excluded.source_id,
                status = 'ready',
                diagnostics_json = '[]',
                updated_at = CURRENT_TIMESTAMP
            """,
            (adapter_id, source_id),
        )

    def save_poll_state(self, adapter_id: str, source_id: str, cursor_time: str | None, logical_now: str) -> None:
        self.conn.execute(
            """
            INSERT INTO adapter_state (
                adapter_id, source_id, cursor_time, status, poll_count, last_logical_now, diagnostics_json, updated_at
            )
            VALUES (?, ?, ?, 'ready', 1, ?, '[]', CURRENT_TIMESTAMP)
            ON CONFLICT(adapter_id) DO UPDATE SET
                source_id = excluded.source_id,
                cursor_time = excluded.cursor_time,
                status = 'ready',
                poll_count = poll_count + 1,
                last_logical_now = excluded.last_logical_now,
                diagnostics_json = '[]',
                updated_at = CURRENT_TIMESTAMP
            """,
            (adapter_id, source_id, cursor_time, logical_now),
        )

    def save_unusable(
        self,
        adapter_id: str,
        source_id: str,
        logical_now: str,
        diagnostics: list[dict[str, Any]] | dict[str, Any],
    ) -> None:
        self.save_status(adapter_id, source_id, "unusable", None, logical_now, diagnostics)

    def save_status(
        self,
        adapter_id: str,
        source_id: str,
        status: str,
        cursor_time: str | None,
        logical_now: str,
        diagnostics: list[dict[str, Any]] | dict[str, Any] | None,
    ) -> None:
        self.conn.execute(
            """
            INSERT INTO adapter_state (
                adapter_id, source_id, cursor_time, status, poll_count, last_logical_now, diagnostics_json, updated_at
            )
            VALUES (?, ?, ?, ?, 1, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(adapter_id) DO UPDATE SET
                source_id = excluded.source_id,
                cursor_time = excluded.cursor_time,
                status = excluded.status,
                poll_count = poll_count + 1,
                last_logical_now = excluded.last_logical_now,
                diagnostics_json = excluded.diagnostics_json,
                updated_at = CURRENT_TIMESTAMP
            """,
            (adapter_id, source_id, cursor_time, status, logical_now, encode_diagnostics(diagnostics)),
        )

    def public_row(self, row: Any) -> dict[str, Any]:
        data = dict(row)
        return {
            "adapterId": data.get("adapter_id"),
            "sourceId": data.get("source_id"),
            "cursorTime": data.get("cursor_time"),
            "cursor_time": data.get("cursor_time"),
            "status": data.get("status"),
            "pollCount": data.get("poll_count"),
            "poll_count": data.get("poll_count"),
            "lastLogicalNow": data.get("last_logical_now"),
            "last_logical_now": data.get("last_logical_now"),
            "diagnostics": decode_diagnostics(data.get("diagnostics_json")),
            "diagnostics_json": data.get("diagnostics_json"),
            "updatedAt": data.get("updated_at"),
            "updated_at": data.get("updated_at"),
        }
