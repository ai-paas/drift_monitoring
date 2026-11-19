from __future__ import annotations

import json
from typing import Any

from .util import row_to_dict, rows_to_dicts


class MethodRepository:
    def __init__(self, conn: Any) -> None:
        self.conn = conn

    # @managed-contract contract_id=repository.method.upsert_assignment level=P0
    def upsert_assignment(self, source_id: str, payload: dict[str, Any]) -> None:
        self.conn.execute(
            """
            INSERT INTO source_method_assignment (
                assignment_id, source_id, adapter_id, feature_id, runtime_method_key,
                params_json, threshold_json, window_config_json, enabled, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(assignment_id) DO UPDATE SET
                source_id = excluded.source_id,
                adapter_id = excluded.adapter_id,
                feature_id = excluded.feature_id,
                runtime_method_key = excluded.runtime_method_key,
                params_json = excluded.params_json,
                threshold_json = excluded.threshold_json,
                window_config_json = excluded.window_config_json,
                enabled = excluded.enabled,
                updated_at = CURRENT_TIMESTAMP
            """,
            (
                payload["assignmentId"],
                source_id,
                payload.get("adapterId"),
                payload.get("featureId", "metric"),
                payload.get("runtimeMethodKey"),
                json.dumps(payload.get("params", {}), ensure_ascii=False),
                json.dumps(payload.get("threshold", {}), ensure_ascii=False),
                json.dumps(payload.get("windowConfig", {}), ensure_ascii=False),
                1 if payload.get("enabled", True) else 0,
            ),
        )

    def list_enabled_assignments(self, source_id: str, adapter_id: str, feature_id: str) -> list[Any]:
        return self.conn.execute(
            """
            SELECT *
            FROM source_method_assignment
            WHERE source_id = ? AND adapter_id = ? AND feature_id = ? AND enabled = 1
            ORDER BY assignment_id
            """,
            (source_id, adapter_id, feature_id),
        ).fetchall()

    def get_state_row(self, assignment_id: str) -> Any:
        return self.conn.execute("SELECT * FROM method_state WHERE assignment_id = ?", (assignment_id,)).fetchone()

    def get_state(self, assignment_id: str) -> dict[str, Any] | None:
        return row_to_dict(self.get_state_row(assignment_id))

    # @managed-contract contract_id=repository.method.upsert_state level=P0
    def upsert_state(self, assignment_id: str, state: dict[str, Any], bucket_id: str, bucket_end: str) -> None:
        self.conn.execute(
            """
            INSERT INTO method_state (assignment_id, state_json, last_bucket_id, last_bucket_end, updated_at)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(assignment_id) DO UPDATE SET
                state_json = excluded.state_json,
                last_bucket_id = excluded.last_bucket_id,
                last_bucket_end = excluded.last_bucket_end,
                updated_at = CURRENT_TIMESTAMP
            """,
            (assignment_id, json.dumps(state, ensure_ascii=False), bucket_id, bucket_end),
        )

    def method_run_exists(self, method_run_id: str) -> bool:
        row = self.conn.execute("SELECT 1 FROM method_run WHERE method_run_id = ?", (method_run_id,)).fetchone()
        return row is not None

    # @managed-contract contract_id=repository.method.insert_run_once level=P0
    def insert_run_once(
        self,
        method_run_id: str,
        assignment: Any,
        bucket: dict[str, Any],
        run_status: str,
        level: str,
        score: float | None,
        result: dict[str, Any],
        error_message: str | None,
    ) -> None:
        self.conn.execute(
            """
            INSERT OR IGNORE INTO method_run (
                method_run_id, assignment_id, source_id, adapter_id, feature_id, bucket_id,
                window_start, window_end, run_status, level, score, input_bucket_count,
                result_json, error_message
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?, ?)
            """,
            (
                method_run_id,
                assignment["assignment_id"],
                bucket["source_id"],
                bucket["adapter_id"],
                bucket["feature_id"],
                bucket["bucket_id"],
                bucket["window_start"],
                bucket["window_end"],
                run_status,
                level,
                score,
                json.dumps(result, ensure_ascii=False),
                error_message,
            ),
        )

    def get_run(self, method_run_id: str) -> dict[str, Any] | None:
        row = self.conn.execute("SELECT * FROM method_run WHERE method_run_id = ?", (method_run_id,)).fetchone()
        return row_to_dict(row)

    def list_runs(self, source_id: str, assignment_id: str | None = None) -> list[dict[str, Any]]:
        query = """
            SELECT method_run_id, assignment_id, source_id, adapter_id, feature_id, bucket_id,
                   window_start, window_end, run_status, level, score, input_bucket_count,
                   result_json, error_message, created_at
            FROM method_run
            WHERE source_id = ?
        """
        params: list[Any] = [source_id]
        if assignment_id:
            query += " AND assignment_id = ?"
            params.append(assignment_id)
        query += " ORDER BY window_start, method_run_id"
        return rows_to_dicts(self.conn.execute(query, params).fetchall())

    def count_runs(self, source_id: str, assignment_id: str | None = None) -> int:
        query = "SELECT COUNT(*) AS count FROM method_run WHERE source_id = ?"
        params: list[Any] = [source_id]
        if assignment_id:
            query += " AND assignment_id = ?"
            params.append(assignment_id)
        return int(self.conn.execute(query, params).fetchone()["count"])
