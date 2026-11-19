from __future__ import annotations

from typing import Any

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from shared.dev_db import reset_source

from .db import get_connection
from .drift.collector import DriftCollector
from .drift.payload_registry import PayloadAdapterNotFound
from .drift.service import DriftService, PayloadAdapterError, PayloadContextInvalid
from .repositories.adapter_state_repository import AdapterStateRepository
from .repositories.analysis_chart_repository import AnalysisChartRepository
from .repositories.bucket_repository import BucketRepository
from .repositories.event_repository import EventRepository
from .repositories.method_repository import MethodRepository
from .response import error, ok
from .settings import DRIFT_SERVER_HOST, DRIFT_SERVER_PORT
from .state import state


app = FastAPI(title="Sprint 1 Drift Server")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
collector = DriftCollector()
service = DriftService(state)


@app.get("/api/health")
def health() -> dict[str, Any]:
    with get_connection() as conn:
        conn.execute("SELECT 1")
    return ok({"service": "drift_server", "database": True, "state": "sqlite-dev"})


@app.post("/api/drift/test/reset")
def test_reset(body: dict[str, Any] | None = None) -> dict[str, Any]:
    source_id = (body or {}).get("sourceId")
    state.reset()
    with get_connection() as conn:
        reset_source(conn, source_id)
    return ok({"sourceId": source_id, "reset": True})


# @managed-contract contract_id=api.register_source level=P0
@app.post("/api/drift/sources")
def register_source(body: dict[str, Any]) -> dict[str, Any]:
    source_id = body.get("sourceId")
    if not source_id:
        return error("SOURCE_ID_REQUIRED", "sourceId is required")
    state.sources[source_id] = dict(body)
    return ok({"sourceId": source_id})


# @managed-contract contract_id=api.register_adapter level=P0
@app.post("/api/drift/adapters")
def register_adapter(body: dict[str, Any]) -> dict[str, Any]:
    adapter_id = body.get("adapterId")
    source_id = body.get("sourceId")
    if not adapter_id:
        return error("ADAPTER_ID_REQUIRED", "adapterId is required")
    if not source_id:
        return error("SOURCE_ID_REQUIRED", "sourceId is required")
    state.adapters[adapter_id] = dict(body)
    with get_connection() as conn:
        AdapterStateRepository(conn).upsert_ready(adapter_id, source_id)
        conn.commit()
    return ok({"adapterId": adapter_id, "sourceId": source_id})


# @managed-contract contract_id=api.register_method_assignment level=P0
@app.post("/api/drift/sources/{source_id}/method-assignments")
def register_method_assignment(source_id: str, body: dict[str, Any]) -> dict[str, Any]:
    assignment_id = body.get("assignmentId")
    if not assignment_id:
        return error("ASSIGNMENT_ID_REQUIRED", "assignmentId is required")
    payload = dict(body)
    payload["sourceId"] = source_id
    state.method_assignments[assignment_id] = payload
    with get_connection() as conn:
        MethodRepository(conn).upsert_assignment(source_id, payload)
        conn.commit()
    return ok({"assignmentId": assignment_id, "sourceId": source_id})


# @managed-contract contract_id=api.register_analysis_chart level=P0
@app.post("/api/drift/sources/{source_id}/method-assignments/{assignment_id}/analysis-charts")
def register_analysis_chart(source_id: str, assignment_id: str, body: dict[str, Any]) -> dict[str, Any]:
    analysis_chart_id = body.get("analysisChartId") or "analysis-case010-adwin-stream"
    chart_id = body.get("chartId") or "CHART-STREAM-001"
    chart_definition_id = body.get("chartDefinitionId") or "chartdef-case010-adwin-stream"
    payload_adapter_key = body.get("payloadAdapterKey") or "adwin_mean_stream_to_chart_stream_001"
    chart_definition = body.get("chartDefinition") or _default_chart_definition(chart_id, body)
    payload_adapter_config = body.get("payloadAdapterConfig") or {}
    state.analysis_charts[analysis_chart_id] = {
        **body,
        "sourceId": source_id,
        "assignmentId": assignment_id,
        "analysisChartId": analysis_chart_id,
        "chartId": chart_id,
        "chartDefinitionId": chart_definition_id,
        "chartDefinition": chart_definition,
        "payloadAdapterKey": payload_adapter_key,
        "payloadAdapterConfig": payload_adapter_config,
    }
    with get_connection() as conn:
        AnalysisChartRepository(conn).upsert_registration(
            source_id,
            assignment_id,
            analysis_chart_id,
            chart_id,
            chart_definition_id,
            chart_definition,
            payload_adapter_key,
            payload_adapter_config,
        )
        conn.commit()
    return ok(
        {
            "analysisChartId": analysis_chart_id,
            "chartId": chart_id,
            "chartDefinitionId": chart_definition_id,
            "chartDefinitionSnapshotSaved": True,
            "payloadAdapterKey": payload_adapter_key,
        }
    )


# @managed-contract contract_id=api.poll_once level=P0
@app.post("/api/drift/adapters/{adapter_id}/poll-once")
def poll_once(adapter_id: str, body: dict[str, Any] | None = None) -> dict[str, Any]:
    if adapter_id not in state.adapters:
        return error("ADAPTER_NOT_FOUND", "adapter is not registered", {"adapterId": adapter_id})
    state.poll_count[adapter_id] += 1
    logical_now = (body or {}).get("logicalNow")
    if not logical_now:
        return error("LOGICAL_NOW_REQUIRED", "logicalNow is required")
    result = collector.poll_once(adapter_id, state.adapters[adapter_id], logical_now)
    return ok(
        {
            "adapterId": adapter_id,
            "sourceId": state.adapters[adapter_id]["sourceId"],
            "logicalNow": logical_now,
            "outcome": result.get("outcome"),
            "status": result.get("status"),
            "processedWindow": result["processedWindow"],
            "bucketCreated": result["bucketCreated"],
            "bucketsCreated": result["bucketsCreated"],
            "rejectedRows": result.get("rejectedRows", 0),
            "diagnostics": result.get("diagnostics", []),
            "pollCount": state.poll_count[adapter_id],
        }
    )


# @managed-contract contract_id=api.timeseries_data level=P0
@app.get("/api/sources/{source_id}/timeseries-data")
def timeseries_data(source_id: str, resolution: str = "10m") -> dict[str, Any]:
    return ok(service.get_timeseries_data(source_id, resolution))


# @managed-contract contract_id=api.event_analysis level=P0
@app.get("/api/sources/{source_id}/events/{event_id}/analysis")
def event_analysis(source_id: str, event_id: str) -> dict[str, Any]:
    try:
        return ok(service.build_event_analysis(source_id, event_id))
    except KeyError:
        return error("DRIFT_EVENT_NOT_FOUND", "drift event is not found", {"sourceId": source_id, "eventId": event_id})
    except PayloadContextInvalid as exc:
        return error("PAYLOAD_CONTEXT_INVALID", "event analysis context is incomplete", exc.details)
    except PayloadAdapterNotFound as exc:
        return error("PAYLOAD_ADAPTER_NOT_FOUND", "payload adapter is not registered", {"key": str(exc)})
    except PayloadAdapterError as exc:
        return error("PAYLOAD_ADAPTER_ERROR", "payload adapter failed", {"message": exc.message})


@app.get("/api/drift/adapters/{adapter_id}/status")
def adapter_status(adapter_id: str) -> dict[str, Any]:
    with get_connection() as conn:
        repo = AdapterStateRepository(conn)
        row = repo.get(adapter_id)
    if row is None:
        return error("ADAPTER_STATE_NOT_FOUND", "adapter state is not found", {"adapterId": adapter_id})
    return ok(repo.public_row(row))


@app.get("/api/drift/debug/buckets")
def debug_buckets(sourceId: str, adapterId: str | None = None) -> dict[str, Any]:
    with get_connection() as conn:
        rows = BucketRepository(conn).list_debug_buckets(sourceId, adapterId)
    return ok({"sourceId": sourceId, "adapterId": adapterId, "count": len(rows), "rows": [dict(row) for row in rows]})


@app.get("/api/drift/debug/method-runs")
def debug_method_runs(sourceId: str, assignmentId: str | None = None) -> dict[str, Any]:
    with get_connection() as conn:
        rows = MethodRepository(conn).list_runs(sourceId, assignmentId)
    return ok({"sourceId": sourceId, "assignmentId": assignmentId, "count": len(rows), "rows": rows})


@app.get("/api/drift/debug/drift-events")
def debug_drift_events(sourceId: str, assignmentId: str | None = None) -> dict[str, Any]:
    with get_connection() as conn:
        rows = EventRepository(conn).list_events(sourceId, assignmentId)
    return ok({"sourceId": sourceId, "assignmentId": assignmentId, "count": len(rows), "rows": rows})


@app.get("/api/drift/debug/method-state/{assignment_id}")
def debug_method_state(assignment_id: str) -> dict[str, Any]:
    with get_connection() as conn:
        row = MethodRepository(conn).get_state(assignment_id)
    if row is None:
        return error("METHOD_STATE_NOT_FOUND", "method state is not found", {"assignmentId": assignment_id})
    return ok(row)


@app.get("/api/drift/debug/counts")
def debug_counts(sourceId: str, adapterId: str | None = None, assignmentId: str | None = None) -> dict[str, Any]:
    return ok(service.get_counts(sourceId, adapterId, assignmentId))


def _default_chart_definition(chart_id: str, body: dict[str, Any]) -> dict[str, Any]:
    return {
        "chartId": chart_id,
        "title": body.get("chartOptions", {}).get("title", "CASE-010 ADWIN stream analysis"),
        "xField": "t",
        "yField": "v",
        "series": ["metric_mean"],
    }


if __name__ == "__main__":
    uvicorn.run(app, host=DRIFT_SERVER_HOST, port=DRIFT_SERVER_PORT)
