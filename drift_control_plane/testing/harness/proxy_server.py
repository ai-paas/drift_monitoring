from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from itertools import count
from typing import Any

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.concurrency import run_in_threadpool

from .artifact_store import safe_name
from .proxy_runtime import active_proxy_run_dir


PROXY_TARGETS = {
    "admin": os.environ.get("HARNESS_PROXY_ADMIN_TARGET", "http://127.0.0.1:8770").rstrip("/"),
    "drift": os.environ.get("HARNESS_PROXY_DRIFT_TARGET", "http://127.0.0.1:8771").rstrip("/"),
    "test_feeder": os.environ.get("HARNESS_PROXY_TEST_FEEDER_TARGET", "http://127.0.0.1:8772").rstrip("/"),
    "llm": os.environ.get("HARNESS_PROXY_LLM_TARGET", "http://127.0.0.1:8767").rstrip("/"),
}

app = FastAPI(title="Harness Proxy Record Server")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
_call_seq = count(1)


# @managed-contract contract_id=harness.proxy_server.proxy_call level=P1
@app.api_route("/proxy/{server_name}/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def proxy_call(server_name: str, path: str, request: Request) -> Response:
    request_body = await request.body()
    return await run_in_threadpool(
        _proxy_call_sync,
        server_name,
        path,
        request.method,
        request.url.query,
        request.headers,
        request_body,
    )


def _proxy_call_sync(
    server_name: str,
    path: str,
    method: str,
    query: str,
    headers: Any,
    request_body: bytes,
) -> Response:
    call_number = next(_call_seq)
    target_base_url = PROXY_TARGETS.get(server_name)
    if not target_base_url:
        return Response(
            json.dumps({"ok": False, "error": f"unknown proxy target: {server_name}"}, ensure_ascii=False),
            status_code=404,
            media_type="application/json",
        )

    target_url = f"{target_base_url}/{path}"
    if query:
        target_url = f"{target_url}?{query}"

    request_json = _decode_json(request_body)
    request_headers = _forward_headers(headers)
    started = time.monotonic()
    status_code: int | None = None
    response_body = b""
    response_json: Any = None
    error: str | None = None

    try:
        upstream_request = urllib.request.Request(
            target_url,
            data=request_body if request_body else None,
            headers=request_headers,
            method=method,
        )
        with urllib.request.urlopen(upstream_request, timeout=10) as upstream_response:
            status_code = upstream_response.status
            response_body = upstream_response.read()
            response_json = _decode_json(response_body)
    except urllib.error.HTTPError as exc:
        status_code = exc.code
        response_body = exc.read()
        response_json = _decode_json(response_body)
        error = f"HTTPError: {exc.code} {exc.reason}"
    except Exception as exc:  # noqa: BLE001 - proxy record must preserve forwarding failures.
        status_code = 502
        response_json = {"ok": False, "error": f"{exc.__class__.__name__}: {exc}"}
        response_body = json.dumps(response_json, ensure_ascii=False).encode("utf-8")
        error = f"{exc.__class__.__name__}: {exc}"

    duration_ms = int((time.monotonic() - started) * 1000)
    _save_proxy_call(
        {
            "callId": f"{call_number:04d}",
            "server": server_name,
            "method": method,
            "proxyPath": f"/proxy/{server_name}/{path}",
            "targetUrl": target_url,
            "query": query,
            "requestJson": request_json,
            "statusCode": status_code,
            "responseJson": response_json,
            "error": error,
            "durationMs": duration_ms,
        }
    )
    return Response(
        content=response_body,
        status_code=status_code or 502,
        media_type="application/json",
    )


@app.get("/proxy-health")
def proxy_health() -> dict[str, Any]:
    return {"ok": True, "data": {"service": "harness_proxy", "targets": PROXY_TARGETS}}


def _forward_headers(headers: Any) -> dict[str, str]:
    forwarded = {"Accept": headers.get("accept", "application/json")}
    content_type = headers.get("content-type")
    if content_type:
        forwarded["Content-Type"] = content_type
    return forwarded


def _decode_json(raw: bytes) -> Any:
    if not raw:
        return None
    text = raw.decode("utf-8", errors="replace")
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return text


def _save_proxy_call(record: dict[str, Any]) -> None:
    run_dir = active_proxy_run_dir()
    if not run_dir:
        return
    proxy_calls_dir = run_dir / "proxy_calls"
    proxy_calls_dir.mkdir(parents=True, exist_ok=True)
    filename = f"{record['callId']}_{safe_name(record['server'])}_{safe_name(record['method'])}.json"
    (proxy_calls_dir / filename).write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
