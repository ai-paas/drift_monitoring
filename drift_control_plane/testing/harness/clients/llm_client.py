from __future__ import annotations

from typing import Any

from .http_client import HarnessHttpClient


class LlmClient:
    def __init__(self, http: HarnessHttpClient) -> None:
        self.http = http

    def health(self) -> Any:
        return self.http.get("/api/health")

    def create_chart_job(self, request: dict[str, Any]) -> Any:
        return self.http.post("/api/interpret/chart/jobs", request)

    def get_chart_job(self, job_id: str) -> Any:
        return self.http.get(f"/api/interpret/chart/jobs/{job_id}")
