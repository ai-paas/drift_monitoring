from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from drift_server.app.diagnostics import diagnostic
from drift_server.app.db import get_connection
from drift_server.app.drift.detector import DriftDetector
from drift_server.app.repositories.adapter_state_repository import AdapterStateRepository
from drift_server.app.repositories.bucket_repository import BucketRepository


class DriftCollector:
    def poll_once(self, adapter_id: str, adapter: dict[str, Any], logical_now: str) -> dict[str, Any]:
        source_id = adapter["sourceId"]
        interval_minutes = int(adapter.get("aggregateIntervalMinutes") or adapter.get("collectionIntervalMinutes") or 10)
        logical_now_dt = _parse_iso(logical_now)
        buckets_created = 0
        processed_window: dict[str, str] | None = None
        diagnostics: list[dict[str, Any]] = []

        with get_connection() as conn:
            adapter_states = AdapterStateRepository(conn)
            buckets = BucketRepository(conn)
            detector = DriftDetector(conn)
            offset_diagnostics = _clock_offset_diagnostics(conn, source_id, adapter)
            if offset_diagnostics["unusable"]:
                diagnostics.append(
                    diagnostic(
                        "SOURCE_CLOCK_OFFSET_TOO_LARGE",
                        "error",
                        "source clock offset exceeds allowed threshold",
                        logical_now,
                        source_id,
                        adapter_id,
                        {
                            "maxSourceClockOffsetMs": offset_diagnostics["maxSourceClockOffsetMs"],
                            "maxObservedSourceClockOffsetMs": offset_diagnostics[
                                "maxObservedSourceClockOffsetMs"
                            ],
                            "rowCount": offset_diagnostics["rowCount"],
                        },
                    )
                )
                adapter_states.save_unusable(adapter_id, source_id, logical_now, diagnostics)
                conn.commit()
                return {
                    "outcome": "blocked",
                    "status": "unusable",
                    "processedWindow": None,
                    "bucketCreated": False,
                    "bucketsCreated": 0,
                    "rejectedRows": _future_rejected_rows(conn, source_id),
                    "diagnostics": diagnostics,
                }
            adapter_row = adapter_states.get(adapter_id)
            cursor_time = adapter_row["cursor_time"] if adapter_row else None
            if not cursor_time:
                first_event_time = buckets.first_event_time(source_id)
                if not first_event_time:
                    rejected_rows = _future_rejected_rows(conn, source_id)
                    if rejected_rows:
                        diagnostics.append(
                            diagnostic(
                                "FUTURE_EVENT_TIME_REJECTED",
                                "warning",
                                "normalized event_time is later than logicalNow and rows were rejected",
                                logical_now,
                                source_id,
                                adapter_id,
                                {"futureRejectedRows": rejected_rows},
                            )
                        )
                        status = "warning"
                    else:
                        diagnostics.append(
                            diagnostic(
                                "NO_SOURCE_DATA",
                                "warning",
                                "source has no available raw event rows",
                                logical_now,
                                source_id,
                                adapter_id,
                            )
                        )
                        status = "warning"
                    adapter_states.save_status(adapter_id, source_id, status, None, logical_now, diagnostics)
                    conn.commit()
                    return {
                        "outcome": "skipped",
                        "status": status,
                        "processedWindow": None,
                        "bucketCreated": False,
                        "bucketsCreated": 0,
                        "rejectedRows": rejected_rows,
                        "diagnostics": diagnostics,
                    }
                cursor_dt = _floor_to_interval(_parse_iso(first_event_time), interval_minutes)
            else:
                cursor_dt = _parse_iso(cursor_time)

            while cursor_dt + timedelta(minutes=interval_minutes) <= logical_now_dt:
                window_start_dt = cursor_dt
                window_end_dt = cursor_dt + timedelta(minutes=interval_minutes)
                window_start = _format_iso(window_start_dt)
                window_end = _format_iso(window_end_dt)
                bucket = _build_bucket(adapter, buckets, source_id, adapter_id, window_start, window_end)
                inserted = buckets.insert_metric_bucket_once(bucket)
                buckets_created += inserted
                if inserted:
                    detector.run_for_bucket(bucket)
                processed_window = {"start": window_start, "end": window_end}
                cursor_dt = window_end_dt

            rejected_rows = _future_rejected_rows(conn, source_id)
            if rejected_rows:
                diagnostics.append(
                    diagnostic(
                        "FUTURE_EVENT_TIME_REJECTED",
                        "warning",
                        "normalized event_time is later than logicalNow and rows were rejected",
                        logical_now,
                        source_id,
                        adapter_id,
                        {"futureRejectedRows": rejected_rows},
                    )
                )
                adapter_states.save_status(
                    adapter_id,
                    source_id,
                    "warning",
                    _format_iso(cursor_dt),
                    logical_now,
                    diagnostics,
                )
            else:
                adapter_states.save_poll_state(adapter_id, source_id, _format_iso(cursor_dt), logical_now)
            conn.commit()

        outcome = "processed" if processed_window is not None else "skipped"
        status = "warning" if diagnostics else "ready"
        return {
            "outcome": outcome,
            "status": status,
            "processedWindow": processed_window,
            "bucketCreated": buckets_created > 0,
            "bucketsCreated": buckets_created,
            "rejectedRows": rejected_rows,
            "diagnostics": diagnostics,
        }


def _parse_iso(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _format_iso(value: datetime) -> str:
    return value.replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _floor_to_interval(value: datetime, interval_minutes: int) -> datetime:
    minute = value.minute - (value.minute % interval_minutes)
    return value.replace(minute=minute, second=0, microsecond=0)


def _clock_offset_diagnostics(conn: Any, source_id: str, adapter: dict[str, Any]) -> dict[str, Any]:
    source_config = adapter.get("sourceConfig") or {}
    max_offset_ms = int(source_config.get("maxSourceClockOffsetMs") or source_config.get("max_source_clock_offset_ms") or 300000)
    configured_offset_ms = abs(int(source_config.get("sourceClockOffsetMs") or source_config.get("source_clock_offset_ms") or 0))
    row = conn.execute(
        """
        SELECT MAX(ABS(source_clock_offset_ms)) AS max_abs_offset_ms, COUNT(*) AS row_count
        FROM raw_event
        WHERE source_id = ?
        """,
        (source_id,),
    ).fetchone()
    max_abs_offset_ms = max(int(row["max_abs_offset_ms"] or 0) if row else 0, configured_offset_ms)
    return {
        "code": "SOURCE_CLOCK_OFFSET_TOO_LARGE" if max_abs_offset_ms > max_offset_ms else "OK",
        "maxSourceClockOffsetMs": max_offset_ms,
        "maxObservedSourceClockOffsetMs": max_abs_offset_ms,
        "rowCount": int(row["row_count"] or 0) if row else 0,
        "unusable": max_abs_offset_ms > max_offset_ms,
    }


def _future_rejected_rows(conn: Any, source_id: str) -> int:
    row = conn.execute(
        "SELECT future_rejected_rows FROM feed_state WHERE source_id = ?",
        (source_id,),
    ).fetchone()
    return int(row["future_rejected_rows"] or 0) if row else 0


# @managed-contract contract_id=drift_collector._build_bucket level=P0
def _build_bucket(
    adapter: dict[str, Any],
    buckets: BucketRepository,
    source_id: str,
    adapter_id: str,
    window_start: str,
    window_end: str,
) -> dict[str, Any]:
    adapter_type = adapter.get("adapterType")
    if adapter_type == "test_db_prediction_log_stream":
        stats = buckets.prediction_window_stats(source_id, window_start, window_end)
        return {
            "bucket_id": f"{adapter_id}:error_rate:{window_start}:{window_end}",
            "adapter_id": adapter_id,
            "source_id": source_id,
            "feature_id": "error_rate",
            "window_start": window_start,
            "window_end": window_end,
            "row_count": int(stats["row_count"]),
            "mean_value": stats["error_rate"],
            "min_value": None,
            "max_value": None,
            "error_count": stats["error_count"],
            "error_rate": stats["error_rate"],
            "mean_confidence": stats["mean_confidence"],
            "payload": {"errors": stats["errors"]},
        }
    if adapter_type == "test_db_numeric_distribution_window":
        stats = buckets.numeric_distribution_window_stats(source_id, window_start, window_end)
        return {
            "bucket_id": f"{adapter_id}:score:{window_start}:{window_end}",
            "adapter_id": adapter_id,
            "source_id": source_id,
            "feature_id": "score",
            "window_start": window_start,
            "window_end": window_end,
            "row_count": int(stats["row_count"]),
            "mean_value": stats["mean_value"],
            "min_value": stats["min_value"],
            "max_value": stats["max_value"],
            "payload": {"values": stats["values"]},
        }
    if adapter_type == "test_db_multivariate_window":
        source_config = adapter.get("sourceConfig") or {}
        feature_columns = source_config.get("featureColumns") or source_config.get("feature_columns") or ["x1", "x2", "x3"]
        attribute_columns = source_config.get("attributeColumns") or source_config.get("attribute_columns") or []
        stats = buckets.multivariate_window_stats(
            source_id, window_start, window_end, list(feature_columns), list(attribute_columns)
        )
        return {
            "bucket_id": f"{adapter_id}:multivariate:{window_start}:{window_end}",
            "adapter_id": adapter_id,
            "source_id": source_id,
            "feature_id": "multivariate",
            "window_start": window_start,
            "window_end": window_end,
            "row_count": int(stats["row_count"]),
            "mean_value": stats["mean_value"],
            "min_value": stats["min_value"],
            "max_value": stats["max_value"],
            "payload": {
                "values": stats["values"],
                "featureColumns": stats["feature_columns"],
                "attributeColumns": stats.get("attribute_columns", []),
            },
        }
    if adapter_type == "test_db_categorical_count_window":
        stats = buckets.categorical_count_window_stats(source_id, window_start, window_end)
        return {
            "bucket_id": f"{adapter_id}:category:{window_start}:{window_end}",
            "adapter_id": adapter_id,
            "source_id": source_id,
            "feature_id": "category",
            "window_start": window_start,
            "window_end": window_end,
            "row_count": int(stats["row_count"]),
            "mean_value": stats["mean_value"],
            "min_value": stats["min_value"],
            "max_value": stats["max_value"],
            "payload": {"values": stats["values"]},
        }

    stats = buckets.window_stats(source_id, window_start, window_end)
    return {
        "bucket_id": f"{adapter_id}:metric:{window_start}:{window_end}",
        "adapter_id": adapter_id,
        "source_id": source_id,
        "feature_id": "metric",
        "window_start": window_start,
        "window_end": window_end,
        "row_count": int(stats["row_count"]),
        "mean_value": stats["mean_value"],
        "min_value": stats["min_value"],
        "max_value": stats["max_value"],
        "payload": {},
    }
