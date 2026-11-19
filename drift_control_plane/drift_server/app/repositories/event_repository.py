from __future__ import annotations

import json
from typing import Any

from .util import row_to_dict, rows_to_dicts


class EventRepository:
    def __init__(self, conn: Any) -> None:
        self.conn = conn

    # @managed-contract contract_id=repository.event.insert_event_once level=P0
    def insert_event_once(self, method_run_id: str, assignment: Any, bucket: dict[str, Any], output: dict[str, Any]) -> None:
        event = output.get("event") or {}
        event_id = f"event:{method_run_id}"
        self.conn.execute(
            """
            INSERT OR IGNORE INTO drift_event (
                event_id, method_run_id, assignment_id, source_id, adapter_id, feature_id,
                event_start, event_end, event_level, event_title, score, payload_json
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                event_id,
                method_run_id,
                assignment["assignment_id"],
                bucket["source_id"],
                bucket["adapter_id"],
                bucket["feature_id"],
                event.get("eventStart") or bucket["window_start"],
                event.get("eventEnd") or bucket["window_end"],
                event.get("eventLevel") or output["level"],
                event.get("eventTitle") or "Drift detected",
                output["score"],
                json.dumps(
                    {
                        "metrics": output["metrics"],
                        "diagnostics": output["diagnostics"],
                        "payloadHints": output["payloadHints"],
                        "event": event,
                    },
                    ensure_ascii=False,
                ),
            ),
        )

    # @managed-contract contract_id=repository.event.get_event level=P0
    def get_event(self, source_id: str, event_id: str) -> dict[str, Any] | None:
        row = self.conn.execute(
            "SELECT * FROM drift_event WHERE source_id = ? AND event_id = ?",
            (source_id, event_id),
        ).fetchone()
        return row_to_dict(row)

    def list_events(self, source_id: str, assignment_id: str | None = None) -> list[dict[str, Any]]:
        query = """
            SELECT event_id, method_run_id, assignment_id, source_id, adapter_id, feature_id,
                   event_start, event_end, event_level, event_title, score, payload_json, created_at
            FROM drift_event
            WHERE source_id = ?
        """
        params: list[Any] = [source_id]
        if assignment_id:
            query += " AND assignment_id = ?"
            params.append(assignment_id)
        query += " ORDER BY event_start, event_id"
        return rows_to_dicts(self.conn.execute(query, params).fetchall())

    def list_timeseries_events(self, source_id: str) -> list[Any]:
        return self.conn.execute(
            """
            SELECT event_id, method_run_id, assignment_id, feature_id, event_start, event_end,
                   event_level, event_title, score
            FROM drift_event
            WHERE source_id = ?
            ORDER BY event_start, event_id
            """,
            (source_id,),
        ).fetchall()

    def count_events(self, source_id: str, assignment_id: str | None = None) -> int:
        query = "SELECT COUNT(*) AS count FROM drift_event WHERE source_id = ?"
        params: list[Any] = [source_id]
        if assignment_id:
            query += " AND assignment_id = ?"
            params.append(assignment_id)
        return int(self.conn.execute(query, params).fetchone()["count"])
