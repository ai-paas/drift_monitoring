from __future__ import annotations

import json
from typing import Any


class BucketRepository:
    def __init__(self, conn: Any) -> None:
        self.conn = conn

    def first_event_time(self, source_id: str) -> str | None:
        row = self.conn.execute(
            "SELECT MIN(event_time) AS first_event_time FROM raw_event WHERE source_id = ?",
            (source_id,),
        ).fetchone()
        return row["first_event_time"] if row else None

    def window_stats(self, source_id: str, window_start: str, window_end: str) -> Any:
        return self.conn.execute(
            """
            SELECT COUNT(*) AS row_count, AVG(metric) AS mean_value, MIN(metric) AS min_value, MAX(metric) AS max_value
            FROM raw_event
            WHERE source_id = ? AND event_time >= ? AND event_time < ?
            """,
            (source_id, window_start, window_end),
        ).fetchone()

    # @managed-contract contract_id=repository.bucket.prediction_window_stats level=P0
    def prediction_window_stats(self, source_id: str, window_start: str, window_end: str) -> dict[str, Any]:
        rows = self.conn.execute(
            """
            SELECT event_time, payload_json
            FROM raw_event
            WHERE source_id = ? AND event_time >= ? AND event_time < ?
            ORDER BY event_time, row_index
            """,
            (source_id, window_start, window_end),
        ).fetchall()
        error_rows: list[dict[str, Any]] = []
        confidence_values: list[float] = []
        for row in rows:
            payload = json.loads(row["payload_json"])
            if payload.get("error") is not None:
                error = int(float(payload["error"]))
            elif payload.get("y_true") is not None and payload.get("y_pred") is not None:
                error = int(payload["y_true"] != payload["y_pred"])
            elif payload.get("label") is not None and payload.get("model_prediction") is not None:
                error = int(payload["label"] != payload["model_prediction"])
            else:
                error = int(float(payload.get("metric", 0)))
            item = {
                "time": row["event_time"],
                "error": error,
                "y_true": payload.get("y_true", payload.get("label")),
                "y_pred": payload.get("y_pred", payload.get("model_prediction")),
                "confidence": payload.get("confidence"),
            }
            if item["confidence"] is not None:
                confidence_values.append(float(item["confidence"]))
            error_rows.append(item)
        row_count = len(error_rows)
        error_count = sum(int(row["error"]) for row in error_rows)
        error_rate = (error_count / row_count) if row_count else None
        return {
            "row_count": row_count,
            "error_count": error_count,
            "error_rate": error_rate,
            "mean_confidence": (sum(confidence_values) / len(confidence_values)) if confidence_values else None,
            "errors": error_rows,
        }

    # @managed-contract contract_id=repository.bucket.numeric_distribution_window_stats level=P0
    def numeric_distribution_window_stats(self, source_id: str, window_start: str, window_end: str) -> dict[str, Any]:
        rows = self.conn.execute(
            """
            SELECT event_time, payload_json, metric
            FROM raw_event
            WHERE source_id = ? AND event_time >= ? AND event_time < ?
            ORDER BY event_time, row_index
            """,
            (source_id, window_start, window_end),
        ).fetchall()
        value_rows: list[dict[str, Any]] = []
        values: list[float] = []
        for row in rows:
            payload = json.loads(row["payload_json"])
            value = float(payload.get("score", payload.get("value", payload.get("metric", row["metric"]))))
            values.append(value)
            value_rows.append(
                {
                    "time": row["event_time"],
                    "value": value,
                    "period": payload.get("period"),
                    "bin": payload.get("score_bin"),
                    "binIndex": payload.get("bin_index"),
                    "pair_id": payload.get("pair_id"),
                }
            )
        return {
            "row_count": len(value_rows),
            "mean_value": (sum(values) / len(values)) if values else None,
            "min_value": min(values) if values else None,
            "max_value": max(values) if values else None,
            "values": value_rows,
        }

    # @managed-contract contract_id=repository.bucket.multivariate_window_stats level=P0
    def multivariate_window_stats(
        self,
        source_id: str,
        window_start: str,
        window_end: str,
        feature_columns: list[str],
        attribute_columns: list[str] | None = None,
    ) -> dict[str, Any]:
        rows = self.conn.execute(
            """
            SELECT event_time, payload_json, metric
            FROM raw_event
            WHERE source_id = ? AND event_time >= ? AND event_time < ?
            ORDER BY event_time, row_index
            """,
            (source_id, window_start, window_end),
        ).fetchall()
        value_rows: list[dict[str, Any]] = []
        metric_values: list[float] = []
        for row in rows:
            payload = json.loads(row["payload_json"])
            features: dict[str, float] = {}
            for column in feature_columns:
                if column in payload and payload[column] not in {None, ""}:
                    features[column] = float(payload[column])
            if not features:
                continue
            metric_value = float(payload.get("metric", row["metric"] or 0.0))
            metric_values.append(metric_value)
            value_rows.append(
                {
                    "time": row["event_time"],
                    "period": payload.get("period"),
                    "features": features,
                    "attributes": {
                        column: payload.get(column)
                        for column in (attribute_columns or [])
                        if column in payload and payload.get(column) not in {None, ""}
                    },
                    "metric": metric_value,
                }
            )
        return {
            "row_count": len(value_rows),
            "mean_value": (sum(metric_values) / len(metric_values)) if metric_values else None,
            "min_value": min(metric_values) if metric_values else None,
            "max_value": max(metric_values) if metric_values else None,
            "feature_columns": feature_columns,
            "attribute_columns": attribute_columns or [],
            "values": value_rows,
        }

    # @managed-contract contract_id=repository.bucket.categorical_count_window_stats level=P0
    def categorical_count_window_stats(self, source_id: str, window_start: str, window_end: str) -> dict[str, Any]:
        rows = self.conn.execute(
            """
            SELECT event_time, payload_json
            FROM raw_event
            WHERE source_id = ? AND event_time >= ? AND event_time < ?
            ORDER BY event_time, row_index
            """,
            (source_id, window_start, window_end),
        ).fetchall()
        value_rows: list[dict[str, Any]] = []
        total_count = 0.0
        for row in rows:
            payload = json.loads(row["payload_json"])
            category = payload.get("category", payload.get("label", payload.get("value")))
            if category is None:
                continue
            count = float(payload.get("count", 1.0) or 0.0)
            total_count += count
            value_rows.append(
                {
                    "time": row["event_time"],
                    "category": str(category),
                    "count": count,
                    "period": payload.get("period"),
                }
            )
        return {
            "row_count": len(value_rows),
            "mean_value": (total_count / len(value_rows)) if value_rows else None,
            "min_value": None,
            "max_value": None,
            "values": value_rows,
        }

    def insert_metric_bucket_once(self, bucket: dict[str, Any]) -> int:
        cursor = self.conn.execute(
            """
            INSERT OR IGNORE INTO metric_bucket (
                bucket_id, adapter_id, source_id, feature_id,
                window_start, window_end, row_count, mean_value, min_value, max_value,
                error_count, error_rate, mean_confidence, payload_json
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                bucket["bucket_id"],
                bucket["adapter_id"],
                bucket["source_id"],
                bucket["feature_id"],
                bucket["window_start"],
                bucket["window_end"],
                bucket["row_count"],
                bucket["mean_value"],
                bucket["min_value"],
                bucket["max_value"],
                bucket.get("error_count"),
                bucket.get("error_rate"),
                bucket.get("mean_confidence"),
                json.dumps(bucket.get("payload", {}), ensure_ascii=False),
            ),
        )
        return int(cursor.rowcount)

    def list_metric_buckets(self, source_id: str, feature_id: str = "metric") -> list[Any]:
        return self.conn.execute(
            """
            SELECT bucket_id, adapter_id, source_id, feature_id, window_start, window_end,
                   row_count, mean_value, min_value, max_value,
                   error_count, error_rate, mean_confidence, payload_json
            FROM metric_bucket
            WHERE source_id = ? AND feature_id = ?
            ORDER BY window_start
            """,
            (source_id, feature_id),
        ).fetchall()

    def list_debug_buckets(self, source_id: str, adapter_id: str | None = None) -> list[Any]:
        query = """
            SELECT bucket_id, adapter_id, source_id, feature_id, window_start, window_end,
                   row_count, mean_value, min_value, max_value,
                   error_count, error_rate, mean_confidence, payload_json
            FROM metric_bucket
            WHERE source_id = ?
        """
        params: list[Any] = [source_id]
        if adapter_id:
            query += " AND adapter_id = ?"
            params.append(adapter_id)
        query += " ORDER BY window_start"
        return self.conn.execute(query, params).fetchall()

    def count(self, source_id: str) -> int:
        row = self.conn.execute("SELECT COUNT(*) AS count FROM metric_bucket WHERE source_id = ?", (source_id,)).fetchone()
        return int(row["count"])

    def first_feature_id(self, source_id: str) -> str | None:
        row = self.conn.execute(
            """
            SELECT feature_id
            FROM metric_bucket
            WHERE source_id = ?
            ORDER BY window_start, feature_id
            LIMIT 1
            """,
            (source_id,),
        ).fetchone()
        return row["feature_id"] if row else None
