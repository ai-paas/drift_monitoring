from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Any


class DownstreamClient:
    def __init__(self, base_url: str, timeout_seconds: float) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds

    def get(self, path: str) -> dict[str, Any]:
        return self.request("GET", path)

    def post(self, path: str, body: dict[str, Any] | None = None) -> dict[str, Any]:
        return self.request("POST", path, body or {})

    def request(self, method: str, path: str, body: dict[str, Any] | None = None) -> dict[str, Any]:
        data = None
        headers = {"Accept": "application/json"}
        if body is not None:
            data = json.dumps(body).encode("utf-8")
            headers["Content-Type"] = "application/json"
        request = urllib.request.Request(f"{self.base_url}{path}", data=data, headers=headers, method=method)
        with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
            raw = response.read().decode("utf-8")
            return json.loads(raw) if raw else {}

    def health_ok(self, path: str) -> bool:
        try:
            response = self.get(path)
        except (OSError, urllib.error.URLError, TimeoutError, json.JSONDecodeError):
            return False
        return bool(response.get("ok"))
