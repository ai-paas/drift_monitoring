from __future__ import annotations

import json
from typing import Any

from .util import row_to_dict


class AnalysisChartRepository:
    def __init__(self, conn: Any) -> None:
        self.conn = conn

    # @managed-contract contract_id=repository.analysis_chart.upsert_registration level=P0
    def upsert_registration(
        self,
        source_id: str,
        assignment_id: str,
        analysis_chart_id: str,
        chart_id: str,
        chart_definition_id: str,
        chart_definition: dict[str, Any],
        payload_adapter_key: str,
        payload_adapter_config: dict[str, Any],
    ) -> None:
        self.conn.execute(
            """
            INSERT INTO analysis_chart_registration (
                analysis_chart_id, source_id, assignment_id, chart_id, chart_definition_id,
                chart_definition_json, payload_adapter_key, payload_adapter_config_json, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(analysis_chart_id) DO UPDATE SET
                source_id = excluded.source_id,
                assignment_id = excluded.assignment_id,
                chart_id = excluded.chart_id,
                chart_definition_id = excluded.chart_definition_id,
                chart_definition_json = excluded.chart_definition_json,
                payload_adapter_key = excluded.payload_adapter_key,
                payload_adapter_config_json = excluded.payload_adapter_config_json,
                updated_at = CURRENT_TIMESTAMP
            """,
            (
                analysis_chart_id,
                source_id,
                assignment_id,
                chart_id,
                chart_definition_id,
                json.dumps(chart_definition, ensure_ascii=False),
                payload_adapter_key,
                json.dumps(payload_adapter_config, ensure_ascii=False),
            ),
        )

    # @managed-contract contract_id=repository.analysis_chart.get_for_assignment level=P0
    def get_for_assignment(self, source_id: str, assignment_id: str) -> dict[str, Any] | None:
        row = self.conn.execute(
            """
            SELECT *
            FROM analysis_chart_registration
            WHERE source_id = ? AND assignment_id = ?
            ORDER BY created_at DESC
            LIMIT 1
            """,
            (source_id, assignment_id),
        ).fetchone()
        return row_to_dict(row)

    def count(self, source_id: str) -> int:
        row = self.conn.execute(
            "SELECT COUNT(*) AS count FROM analysis_chart_registration WHERE source_id = ?",
            (source_id,),
        ).fetchone()
        return int(row["count"])
