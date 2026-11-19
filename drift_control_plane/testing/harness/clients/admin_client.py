from __future__ import annotations

from typing import Any

from .http_client import HarnessHttpClient


class AdminClient:
    def __init__(self, http: HarnessHttpClient) -> None:
        self.http = http

    def health(self) -> Any:
        return self.http.get("/api/admin/health")

    def test_reset(self, source_id: str) -> Any:
        return self.http.post("/api/admin/test/reset", {"mode": "run", "sourceId": source_id, "force": True})

    def register_source(self, body: dict[str, Any]) -> Any:
        return self.http.post("/api/admin/sources", body)

    def register_adapter(self, body: dict[str, Any]) -> Any:
        return self.http.post("/api/admin/adapters", body)

    def adapter_status(self, adapter_id: str) -> Any:
        return self.http.get(f"/api/admin/adapters/{adapter_id}/status")

    def register_method_assignment(self, source_id: str, body: dict[str, Any]) -> Any:
        return self.http.post(f"/api/admin/sources/{source_id}/method-assignments", body)

    def register_analysis_chart(self, source_id: str, assignment_id: str, body: dict[str, Any]) -> Any:
        return self.http.post(f"/api/admin/sources/{source_id}/method-assignments/{assignment_id}/analysis-charts", body)

    def tick(self, logical_now: str, tick_index: int) -> Any:
        return self.http.post(
            "/api/admin/test/tick",
            {"logicalNow": logical_now, "tickIndex": tick_index},
        )
