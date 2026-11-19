from __future__ import annotations

import json
from typing import Any


def diagnostic(
    code: str,
    severity: str,
    message: str,
    logical_now: str,
    source_id: str,
    adapter_id: str,
    details: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "code": code,
        "severity": severity,
        "message": message,
        "logicalNow": logical_now,
        "sourceId": source_id,
        "adapterId": adapter_id,
        "details": details or {},
    }


def encode_diagnostics(diagnostics: list[dict[str, Any]] | dict[str, Any] | None) -> str:
    if diagnostics is None:
        return "[]"
    if isinstance(diagnostics, dict):
        diagnostics = [diagnostics]
    return json.dumps(diagnostics, ensure_ascii=False, sort_keys=True)


def decode_diagnostics(value: str | None) -> list[dict[str, Any]]:
    if not value:
        return []
    try:
        decoded = json.loads(value)
    except json.JSONDecodeError:
        return [
            {
                "code": "DIAGNOSTICS_DECODE_ERROR",
                "severity": "warning",
                "message": "diagnostics_json is not valid JSON",
                "logicalNow": None,
                "sourceId": None,
                "adapterId": None,
                "details": {"raw": value},
            }
        ]
    if isinstance(decoded, list):
        return [item for item in decoded if isinstance(item, dict)]
    if isinstance(decoded, dict) and not decoded:
        return []
    if isinstance(decoded, dict):
        return [decoded]
    return []
