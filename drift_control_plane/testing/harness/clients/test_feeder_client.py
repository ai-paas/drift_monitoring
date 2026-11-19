from __future__ import annotations

from typing import Any

from .http_client import HarnessHttpClient


class TestFeederClient:
    def __init__(self, http: HarnessHttpClient) -> None:
        self.http = http

    def health(self) -> Any:
        return self.http.get("/api/test-feeder/health")

    def register_feeder(self, body: dict[str, Any]) -> Any:
        return self.http.post("/api/test-feeder/feeders", body)

    def reset(self, source_id: str) -> Any:
        return self.http.post("/api/test-feeder/reset", {"sourceId": source_id, "force": True})

    def tick(self, source_id: str, logical_now: str, tick_index: int) -> Any:
        return self.http.post(
            f"/api/test-feeder/feeders/{source_id}/tick",
            {"logicalNow": logical_now, "tickIndex": tick_index},
        )

    def status(self, source_id: str) -> Any:
        return self.http.get(f"/api/test-feeder/feeders/{source_id}/status")

    def raw_events(self, source_id: str) -> Any:
        return self.http.get("/api/test-feeder/debug/raw-events", {"sourceId": source_id})
