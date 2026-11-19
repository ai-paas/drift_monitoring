from __future__ import annotations

import json
from typing import Any


# @managed-contract contract_id=runtime_methods.generic_metric_threshold.run_generic_metric_threshold level=P0
def run_generic_metric_threshold(assignment: Any, bucket: dict[str, Any], previous_state: dict[str, Any]) -> dict[str, Any]:
    params = json.loads(assignment["params_json"])
    current_mean = float(bucket["mean_value"])
    threshold = float(params.get("threshold", params.get("metricThreshold", 1.0)))
    direction = str(params.get("direction", "greater_equal")).lower()
    previous_mean = previous_state.get("lastMean")
    seen_buckets = int(previous_state.get("seenBuckets", 0)) + 1
    next_state = {
        "lastMean": current_mean,
        "previousMean": previous_mean,
        "seenBuckets": seen_buckets,
        "lastBucketEnd": bucket["window_end"],
    }

    drift_detected = _threshold_crossed(current_mean, threshold, direction)
    score = _score(current_mean, threshold, direction)
    event = None
    if drift_detected:
        event = {
            "eventStart": bucket["window_start"],
            "eventEnd": bucket["window_end"],
            "eventLevel": "drift",
            "eventTitle": "Generic metric threshold drift detected",
        }

    return {
        "runStatus": "success",
        "level": "drift" if drift_detected else "normal",
        "score": score,
        "event": event,
        "nextState": next_state,
        "metrics": {
            "mean": current_mean,
            "previousMean": previous_mean,
            "threshold": threshold,
            "measurements": {
                "DRIFT_ALARM_STATE": "drift_detected" if drift_detected else "normal",
                "CURRENT_VALUE": current_mean,
                "THRESHOLD": threshold,
                "DIRECTION": direction,
                "PROCESSED_COUNT": seen_buckets,
            },
        },
        "diagnostics": {
            "runtime": assignment["runtime_method_key"],
            "implementation": "deterministic_threshold",
            "algorithmImplAttempted": True,
            "algorithmImplSucceeded": True,
            "thresholdPolicy": direction,
        },
        "payloadHints": {"highlightBucketEnd": bucket["window_end"]},
    }


def _threshold_crossed(value: float, threshold: float, direction: str) -> bool:
    if direction in {"greater", "gt"}:
        return value > threshold
    if direction in {"less", "lt"}:
        return value < threshold
    if direction in {"less_equal", "lte", "le"}:
        return value <= threshold
    return value >= threshold


def _score(value: float, threshold: float, direction: str) -> float:
    if direction in {"less", "lt", "less_equal", "lte", "le"}:
        return max(0.0, threshold - value)
    return max(0.0, value - threshold)
