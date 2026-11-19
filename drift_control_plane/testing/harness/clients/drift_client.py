from __future__ import annotations

from typing import Any

from .http_client import HarnessHttpClient


class DriftClient:
    def __init__(self, http: HarnessHttpClient) -> None:
        self.http = http

    def health(self) -> Any:
        return self.http.get("/api/health")

    def poll_once(self, adapter_id: str, logical_now: str | None = None) -> Any:
        body = {"logicalNow": logical_now} if logical_now else {}
        return self.http.post(f"/api/drift/adapters/{adapter_id}/poll-once", body)

    def timeseries_data(self, source_id: str) -> Any:
        return self.http.get(f"/api/sources/{source_id}/timeseries-data", {"resolution": "10m"})

    def analysis(self, source_id: str, event_id: str) -> Any:
        return self.http.get(f"/api/sources/{source_id}/events/{event_id}/analysis")

    def adapter_status(self, adapter_id: str) -> Any:
        return self.http.get(f"/api/drift/adapters/{adapter_id}/status")

    def buckets(self, source_id: str, adapter_id: str | None = None) -> Any:
        params = {"sourceId": source_id}
        if adapter_id:
            params["adapterId"] = adapter_id
        return self.http.get("/api/drift/debug/buckets", params)

    def method_runs(self, source_id: str, assignment_id: str | None = None) -> Any:
        params = {"sourceId": source_id}
        if assignment_id:
            params["assignmentId"] = assignment_id
        return self.http.get("/api/drift/debug/method-runs", params)

    def drift_events(self, source_id: str, assignment_id: str | None = None) -> Any:
        params = {"sourceId": source_id}
        if assignment_id:
            params["assignmentId"] = assignment_id
        return self.http.get("/api/drift/debug/drift-events", params)

    def method_state(self, assignment_id: str) -> Any:
        return self.http.get(f"/api/drift/debug/method-state/{assignment_id}")

    def counts(self, source_id: str, adapter_id: str | None = None, assignment_id: str | None = None) -> Any:
        params = {"sourceId": source_id}
        if adapter_id:
            params["adapterId"] = adapter_id
        if assignment_id:
            params["assignmentId"] = assignment_id
        return self.http.get("/api/drift/debug/counts", params)
