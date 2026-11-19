from __future__ import annotations

from typing import Any


def ok(data: Any) -> dict[str, Any]:
    return {"ok": True, "data": data, "error": None}


def error(code: str, message: str, details: dict[str, Any] | None = None) -> dict[str, Any]:
    return {"ok": False, "data": None, "error": {"code": code, "message": message, "details": details or {}}}
