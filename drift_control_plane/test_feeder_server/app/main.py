from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import pandas as pd
import uvicorn
from fastapi import FastAPI

from .response import error, ok
from .settings import TEST_FEEDER_SERVER_HOST, TEST_FEEDER_SERVER_PORT
from .state import state
from shared.dev_db import connect, reset_source


app = FastAPI(title="Sprint 1 Test Feeder Server")


def _parse_iso(value: str | None) -> datetime | None:
    if not value:
        return None
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed


@app.get("/api/test-feeder/health")
def health() -> dict[str, Any]:
    with connect() as conn:
        conn.execute("SELECT 1")
    return ok({"service": "test_feeder_server", "database": True, "state": "sqlite-dev"})


@app.post("/api/test-feeder/reset")
def reset(body: dict[str, Any] | None = None) -> dict[str, Any]:
    source_id = (body or {}).get("sourceId")
    dataset_cache = state.dataset_cache
    dataset_cache_paths = state.dataset_cache_paths
    state.reset()
    state.dataset_cache = dataset_cache
    state.dataset_cache_paths = dataset_cache_paths
    with connect() as conn:
        reset_source(conn, source_id)
    return ok({"sourceId": source_id, "reset": True})


@app.post("/api/test-feeder/feeders")
def register_feeder(body: dict[str, Any]) -> dict[str, Any]:
    source_id = body.get("sourceId")
    if not source_id:
        return error("SOURCE_ID_REQUIRED", "sourceId is required")
    start_time = body.get("startTime")
    try:
        replay_range = _prepare_replay_range(body)
    except (FileNotFoundError, ValueError) as exc:
        return error("FEEDER_DATA_UNAVAILABLE", str(exc), {"sourceId": source_id})
    state.feeders[source_id] = dict(body)
    state.replay_ranges[source_id] = replay_range
    state.cursor_indices[source_id] = replay_range[0]
    state.logical_cursor_time[source_id] = start_time
    state.inserted_rows[source_id] = 0
    state.future_rejected_rows[source_id] = 0
    with connect() as conn:
        conn.execute(
            """
            INSERT INTO feed_state (source_id, logical_cursor_time, inserted_rows, updated_at)
            VALUES (?, ?, 0, CURRENT_TIMESTAMP)
            ON CONFLICT(source_id) DO UPDATE SET
                logical_cursor_time = excluded.logical_cursor_time,
                inserted_rows = 0,
                future_rejected_rows = 0,
                updated_at = CURRENT_TIMESTAMP
            """,
            (source_id, start_time),
        )
        conn.commit()
    return ok(
        {
            "sourceId": source_id,
            "datasetCaseId": body.get("datasetCaseId"),
            "logicalCursorTime": start_time,
            "insertedRows": 0,
            "cachedRows": replay_range[1] - replay_range[0],
        }
    )


@app.post("/api/test-feeder/feeders/{source_id}/tick")
def tick(source_id: str, body: dict[str, Any]) -> dict[str, Any]:
    if source_id not in state.feeders:
        return error("FEEDER_NOT_FOUND", "feeder is not registered", {"sourceId": source_id})
    logical_now = body.get("logicalNow")
    logical_now_dt = _parse_iso(logical_now)
    if not logical_now_dt:
        return error("LOGICAL_NOW_REQUIRED", "logicalNow is required")
    inserted_now = _insert_available_rows(source_id, state.feeders[source_id], logical_now)
    state.inserted_rows[source_id] = _count_rows(source_id)
    state.logical_cursor_time[source_id] = logical_now
    with connect() as conn:
        conn.execute(
            """
            INSERT INTO feed_state (
                source_id, logical_cursor_time, inserted_rows, future_rejected_rows, updated_at
            )
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(source_id) DO UPDATE SET
                logical_cursor_time = excluded.logical_cursor_time,
                inserted_rows = excluded.inserted_rows,
                future_rejected_rows = excluded.future_rejected_rows,
                updated_at = CURRENT_TIMESTAMP
            """,
            (
                source_id,
                logical_now,
                state.inserted_rows[source_id],
                state.future_rejected_rows.get(source_id, 0),
            ),
        )
        conn.commit()
    return ok(
        {
            "sourceId": source_id,
            "logicalCursorTime": logical_now,
            "insertedRows": state.inserted_rows[source_id],
            "insertedRowsThisTick": inserted_now,
        }
    )


@app.get("/api/test-feeder/feeders/{source_id}/status")
def status(source_id: str) -> dict[str, Any]:
    if source_id not in state.feeders:
        return error("FEEDER_NOT_FOUND", "feeder is not registered", {"sourceId": source_id})
    return ok(
        {
            "sourceId": source_id,
            "logicalCursorTime": state.logical_cursor_time.get(source_id),
            "insertedRows": state.inserted_rows.get(source_id, 0),
            "futureRejectedRows": state.future_rejected_rows.get(source_id, 0),
            "cachedRows": _cached_row_count(source_id),
            "cursorIndex": state.cursor_indices.get(source_id),
            "status": "running",
        }
    )


@app.get("/api/test-feeder/debug/raw-events")
def debug_raw_events(sourceId: str) -> dict[str, Any]:
    with connect() as conn:
        rows = conn.execute(
            """
            SELECT source_id, row_index, source_event_time, event_time, collected_at,
                   source_clock_offset_ms, metric, payload_json
            FROM raw_event
            WHERE source_id = ?
            ORDER BY row_index
            """,
            (sourceId,),
        ).fetchall()
    return ok(
        {
            "sourceId": sourceId,
            "count": len(rows),
            "futureRejectedRows": state.future_rejected_rows.get(sourceId, 0),
            "rows": [dict(row) for row in rows],
        }
    )


# @managed-contract contract_id=test_feeder._insert_available_rows level=P0
def _insert_available_rows(source_id: str, feeder: dict[str, Any], logical_now: str) -> int:
    inserted = 0
    source_clock_offset_ms = int(feeder.get("sourceClockOffsetMs") or feeder.get("source_clock_offset_ms") or 0)
    logical_now_dt = _parse_iso(logical_now)
    if logical_now_dt is None:
        raise ValueError("logicalNow is required")
    dataset = _load_dataset(feeder)
    replay_start, replay_end = state.replay_ranges.get(source_id) or _prepare_replay_range(feeder)
    cursor_index = max(state.cursor_indices.get(source_id, replay_start), replay_start)
    cutoff_dt = _ready_source_cutoff(logical_now_dt, source_clock_offset_ms)
    next_index = min(dataset["event_times"].searchsorted(_to_utc_timestamp(cutoff_dt), side="left"), replay_end)
    if next_index < cursor_index:
        next_index = cursor_index
    future_rejected = _future_rejected_count(dataset, cursor_index, replay_end, logical_now_dt, source_clock_offset_ms)
    with connect() as conn:
        frame = dataset["frame"]
        for position in range(cursor_index, next_index):
            row = _row_dict(frame.iloc[position])
            row_index = int(frame.iloc[position]["__row_index__"])
            source_event_time = str(frame.iloc[position]["__source_event_time__"])
            source_event_dt = dataset["event_datetimes"][position]
            normalized_event_time = _format_iso(source_event_dt + timedelta(milliseconds=source_clock_offset_ms))
            payload = _payload_from_row(row, normalized_event_time, logical_now, source_clock_offset_ms)
            metric = float(payload.get("metric", payload.get("error", 0.0)))
            cursor = conn.execute(
                """
                INSERT OR IGNORE INTO raw_event (
                    source_id,
                    row_index,
                    source_event_time,
                    event_time,
                    collected_at,
                    source_clock_offset_ms,
                    metric,
                    payload_json
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    source_id,
                    row_index,
                    source_event_time,
                    normalized_event_time,
                    logical_now,
                    source_clock_offset_ms,
                    metric,
                    json.dumps(payload, ensure_ascii=False),
                ),
            )
            inserted += cursor.rowcount
        conn.commit()
    state.cursor_indices[source_id] = next_index
    state.future_rejected_rows[source_id] = future_rejected
    return inserted


def _prepare_replay_range(feeder: dict[str, Any]) -> tuple[int, int]:
    source_id = feeder.get("sourceId")
    dataset = _load_dataset(feeder)
    replay_window = feeder.get("replayWindow") or {}
    replay_start_dt = _parse_iso(replay_window.get("start"))
    replay_end_dt = _parse_iso(replay_window.get("end"))
    start_index = 0
    end_index = len(dataset["frame"])
    if replay_start_dt:
        start_index = int(dataset["event_times"].searchsorted(_to_utc_timestamp(replay_start_dt), side="left"))
    if replay_end_dt:
        end_index = int(dataset["event_times"].searchsorted(_to_utc_timestamp(replay_end_dt), side="left"))
    max_rows = int(feeder.get("maxRows") or 0)
    if max_rows:
        end_index = min(end_index, start_index + max_rows)
    replay_range = (start_index, end_index)
    if source_id:
        state.replay_ranges[source_id] = replay_range
        state.cursor_indices[source_id] = start_index
    return replay_range


def _load_dataset(feeder: dict[str, Any]) -> dict[str, Any]:
    csv_path = _resolve_path(feeder.get("csvPath"))
    path_key = str(csv_path.resolve() if csv_path.exists() else csv_path.absolute())
    cached_key = state.dataset_cache_paths.get(path_key)
    if cached_key and cached_key in state.dataset_cache:
        return state.dataset_cache[cached_key]
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")
    stat = csv_path.stat()
    cache_key = f"{csv_path.resolve()}::{stat.st_mtime_ns}::{stat.st_size}"
    if cache_key in state.dataset_cache:
        return state.dataset_cache[cache_key]
    frame = pd.read_csv(csv_path, dtype=str, keep_default_na=False)
    time_column = "source_event_time" if "source_event_time" in frame.columns else "timestamp"
    if time_column not in frame.columns:
        raise ValueError("CSV requires source_event_time or timestamp column")
    event_times = pd.to_datetime(frame[time_column], utc=True, errors="coerce")
    valid_mask = event_times.notna()
    frame = frame.loc[valid_mask].copy()
    event_times = event_times.loc[valid_mask]
    frame["__row_index__"] = frame.index.astype(int) + 1
    frame["__source_event_time__"] = frame[time_column]
    frame["__event_time__"] = event_times
    frame.sort_values("__event_time__", inplace=True, kind="mergesort")
    frame.reset_index(drop=True, inplace=True)
    dataset = {
        "path": csv_path,
        "frame": frame,
        "event_times": frame["__event_time__"],
        "event_datetimes": [item.to_pydatetime() for item in frame["__event_time__"]],
    }
    state.dataset_cache = {cache_key: dataset}
    state.dataset_cache_paths = {path_key: cache_key}
    return dataset


def _cached_row_count(source_id: str) -> int:
    replay_range = state.replay_ranges.get(source_id)
    if not replay_range:
        return 0
    return replay_range[1] - replay_range[0]


def _ready_source_cutoff(logical_now_dt: datetime, source_clock_offset_ms: int) -> datetime:
    offset_ready = logical_now_dt - timedelta(milliseconds=source_clock_offset_ms)
    return min(logical_now_dt, offset_ready)


def _future_rejected_count(
    dataset: dict[str, Any],
    cursor_index: int,
    replay_end: int,
    logical_now_dt: datetime,
    source_clock_offset_ms: int,
) -> int:
    if source_clock_offset_ms <= 0:
        return 0
    source_ready_index = min(dataset["event_times"].searchsorted(_to_utc_timestamp(logical_now_dt), side="left"), replay_end)
    normalized_ready_index = min(
        dataset["event_times"].searchsorted(
            _to_utc_timestamp(logical_now_dt - timedelta(milliseconds=source_clock_offset_ms)),
            side="left",
        ),
        replay_end,
    )
    return max(0, source_ready_index - max(cursor_index, normalized_ready_index))


def _row_dict(row: Any) -> dict[str, str]:
    return {
        str(key): str(value)
        for key, value in row.to_dict().items()
        if not str(key).startswith("__")
    }


def _to_utc_timestamp(value: datetime) -> pd.Timestamp:
    return pd.Timestamp(value).tz_convert("UTC")


def _payload_from_row(
    row: dict[str, str], normalized_event_time: str, logical_now: str, source_clock_offset_ms: int
) -> dict[str, Any]:
    source_event_time = row.get("source_event_time") or row.get("timestamp")
    payload: dict[str, Any] = {
        **row,
        "sourceEventTime": source_event_time,
        "eventTime": normalized_event_time,
        "collectedAt": logical_now,
        "sourceClockOffsetMs": source_clock_offset_ms,
    }
    if "metric" in row:
        payload["metric"] = float(row["metric"])
    if "score" in row:
        payload["score"] = float(row["score"])
        payload.setdefault("metric", float(payload["score"]))
    if "error" in row:
        payload["error"] = int(float(row["error"]))
        payload["metric"] = float(payload["error"])
    if "event" in row:
        payload["event"] = int(float(row["event"]))
        payload.setdefault("metric", float(payload["event"]))
    probability_vector = {
        column: float(row[column])
        for column in ("p0", "p1", "p2", "p3", "p4")
        if row.get(column) not in {None, ""}
    }
    if probability_vector:
        payload["probabilityVector"] = probability_vector
        payload.setdefault("metric", probability_vector.get("p3", max(probability_vector.values())))
    for metric_column in (
        "x",
        "value",
        "category_weight_c",
        "centroid_x",
        "anomaly_score",
        "concept_score",
        "technical_topic_weight",
        "importance_b",
        "label_noise_probability",
        "activation",
        "semantic_x",
        "annotation_confidence",
        "representation_shift",
    ):
        if row.get(metric_column) not in {None, ""}:
            payload[metric_column] = float(row[metric_column])
            payload.setdefault("metric", float(row[metric_column]))
            break
    if "confidence" in row:
        payload["confidence"] = float(row["confidence"])
    if "error_probability" in row:
        payload["errorProbability"] = float(row["error_probability"])
    return payload


def _count_rows(source_id: str) -> int:
    with connect() as conn:
        row = conn.execute("SELECT COUNT(*) AS count FROM raw_event WHERE source_id = ?", (source_id,)).fetchone()
    return int(row["count"])


def _resolve_path(value: str | None) -> Path:
    if not value:
        raise ValueError("csvPath is required")
    path = Path(value)
    if path.is_absolute():
        return path
    candidates = [
        Path.cwd() / path,
        Path(__file__).resolve().parents[2] / path,
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return candidates[0]


def _format_iso(value: datetime) -> str:
    return value.replace(microsecond=0).isoformat().replace("+00:00", "Z")


if __name__ == "__main__":
    uvicorn.run(app, host=TEST_FEEDER_SERVER_HOST, port=TEST_FEEDER_SERVER_PORT)
