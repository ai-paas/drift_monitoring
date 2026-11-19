from __future__ import annotations

import json
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

from ..artifact_store import ArtifactStore
from ..models import ApiCallRecord


class HarnessHttpClient:
    def __init__(self, server_name: str, base_url: str, artifact_store: ArtifactStore, timeout_seconds: float = 10) -> None:
        self.server_name = server_name
        self.base_url = base_url.rstrip("/")
        self.artifact_store = artifact_store
        self.timeout_seconds = timeout_seconds
        self._call_seq = 0

    def get(self, path: str, query: dict[str, Any] | None = None) -> Any:
        return self.request("GET", path, None, query)

    def post(self, path: str, body: dict[str, Any] | None = None) -> Any:
        return self.request("POST", path, body, None)

    def request(self, method: str, path: str, body: dict[str, Any] | None, query: dict[str, Any] | None) -> Any:
        self._call_seq += 1
        call_id = f"{self._call_seq:04d}"
        url = self._build_url(path, query)
        request_data = None
        headers = {"Accept": "application/json"}
        if body is not None:
            request_data = json.dumps(body).encode("utf-8")
            headers["Content-Type"] = "application/json"

        started = time.monotonic()
        status_code: int | None = None
        response_json: Any = None
        error: str | None = None

        try:
            request = urllib.request.Request(url, data=request_data, headers=headers, method=method)
            with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
                status_code = response.status
                raw = response.read().decode("utf-8")
                response_json = json.loads(raw) if raw else None
        except urllib.error.HTTPError as exc:
            status_code = exc.code
            raw = exc.read().decode("utf-8", errors="replace")
            try:
                response_json = json.loads(raw) if raw else None
            except json.JSONDecodeError:
                response_json = raw
            error = f"HTTPError: {exc.code} {exc.reason}"
        except Exception as exc:  # noqa: BLE001 - artifact must record connection failures.
            error = f"{exc.__class__.__name__}: {exc}"

        duration_ms = int((time.monotonic() - started) * 1000)
        record = ApiCallRecord(
            call_id=call_id,
            server=self.server_name,
            method=method,
            url=url,
            request_json=body,
            status_code=status_code,
            response_json=response_json,
            error=error,
            duration_ms=duration_ms,
        )
        self.artifact_store.save_api_call(record)

        if error:
            raise RuntimeError(f"{self.server_name} {method} {path} failed: {error}")
        return response_json

    def _build_url(self, path: str, query: dict[str, Any] | None) -> str:
        url = f"{self.base_url}{path}"
        if query:
            url = f"{url}?{urllib.parse.urlencode(query)}"
        return url

