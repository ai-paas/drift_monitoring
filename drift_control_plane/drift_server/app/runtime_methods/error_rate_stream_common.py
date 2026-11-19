from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any


# @managed-contract contract_id=runtime_methods.error_rate_stream_common.bucket_error_points level=P1
def bucket_error_points(bucket: dict[str, Any]) -> list[dict[str, Any]]:
    payload = bucket.get("payload") or {}
    if isinstance(payload, str):
        payload = json.loads(payload)
    rows = payload.get("errors") or []
    return [
        {
            "time": row.get("time") or bucket["window_end"],
            "error": int(float(row.get("error", 0))),
            "bucketId": bucket["bucket_id"],
        }
        for row in rows
    ]


def append_error_points(
    previous_state: dict[str, Any], bucket_errors: list[dict[str, Any]], params: dict[str, Any]
) -> list[dict[str, Any]]:
    points = list(previous_state.get("points", []))
    existing = {(point.get("bucketId"), point.get("time")) for point in points}
    for point in bucket_errors:
        key = (point.get("bucketId"), point.get("time"))
        if key not in existing:
            points.append(point)
            existing.add(key)
    max_state_points = int(params.get("maxStatePoints", 2000))
    return points[-max_state_points:]


def bucket_error_rate(bucket: dict[str, Any], bucket_errors: list[dict[str, Any]]) -> float:
    if bucket.get("error_rate") is not None:
        return float(bucket["error_rate"])
    if bucket_errors:
        return sum(point["error"] for point in bucket_errors) / len(bucket_errors)
    return 0.0


def next_error_state(
    previous_state: dict[str, Any], bucket: dict[str, Any], points: list[dict[str, Any]], error_rate: float
) -> dict[str, Any]:
    return {
        "lastErrorRate": error_rate,
        "previousErrorRate": previous_state.get("lastErrorRate"),
        "seenBuckets": int(previous_state.get("seenBuckets", 0)) + 1,
        "lastBucketEnd": bucket["window_end"],
        "points": points,
    }


def ensure_algorithm_impl_path() -> None:
    configured = os.environ.get("DRIFT_ALGORITHM_IMPL_PATH")
    candidates = []
    if configured:
        candidates.append(Path(configured))
    candidates.append(Path(__file__).resolve().parents[4] / "drift_algorithm_impl")

    for candidate in candidates:
        if candidate.exists():
            candidate_text = str(candidate)
            if candidate_text not in sys.path:
                sys.path.insert(0, candidate_text)
            break


def fallback_output(
    assignment: Any,
    bucket: dict[str, Any],
    next_state: dict[str, Any],
    error_rate: float,
    previous_error_rate: Any,
    params: dict[str, Any],
    diagnostics: dict[str, Any],
    detector_label: str,
) -> dict[str, Any]:
    if previous_error_rate is None:
        return normal_output(
            assignment,
            bucket,
            next_state,
            error_rate,
            previous_error_rate,
            "state initialized",
            {"implementation": "deterministic_fallback", **diagnostics},
        )
    threshold = float(params.get("errorRateShiftThreshold", 0.15))
    score = max(0.0, error_rate - float(previous_error_rate))
    level = "drift" if score >= threshold else "normal"
    event = None
    if level == "drift":
        event = {
            "eventStart": bucket["window_start"],
            "eventEnd": bucket["window_end"],
            "eventLevel": "drift",
            "eventTitle": f"{detector_label} error-rate drift detected",
        }
    return {
        "runStatus": "success",
        "level": level,
        "score": score,
        "event": event,
        "nextState": next_state,
        "metrics": {
            "errorRate": error_rate,
            "previousErrorRate": previous_error_rate,
            "threshold": threshold,
            "measurements": {},
        },
        "diagnostics": {
            "runtime": assignment["runtime_method_key"],
            "implementation": "deterministic_fallback",
            "reason": "error-rate shift detected" if level == "drift" else "error-rate shift below threshold",
            **diagnostics,
        },
        "payloadHints": {"highlightBucketEnd": bucket["window_end"]},
    }


def normal_output(
    assignment: Any,
    bucket: dict[str, Any],
    next_state: dict[str, Any],
    error_rate: float,
    previous_error_rate: Any,
    reason: str,
    diagnostics: dict[str, Any],
) -> dict[str, Any]:
    return {
        "runStatus": "success",
        "level": "normal",
        "score": 0.0,
        "event": None,
        "nextState": next_state,
        "metrics": {
            "errorRate": error_rate,
            "previousErrorRate": previous_error_rate,
            "threshold": None,
            "measurements": {},
        },
        "diagnostics": {
            "runtime": assignment["runtime_method_key"],
            "reason": reason,
            **diagnostics,
        },
        "payloadHints": {"highlightBucketEnd": bucket["window_end"]},
    }
