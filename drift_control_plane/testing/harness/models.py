from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


JsonDict = dict[str, Any]


@dataclass
class ApiCallRecord:
    call_id: str
    server: str
    method: str
    url: str
    request_json: JsonDict | None
    status_code: int | None
    response_json: Any
    error: str | None
    duration_ms: int


@dataclass
class StepResult:
    index: int
    action: str
    status: str
    started_at: str
    finished_at: str
    error: str | None = None
    details: JsonDict = field(default_factory=dict)


@dataclass
class ValidationResult:
    name: str
    status: str
    message: str
    details: JsonDict = field(default_factory=dict)

