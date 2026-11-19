# LLM Interpretation Server

This folder contains the standalone chart/component interpretation service.

## Role

The server receives chart runtime payloads and returns Korean report-style interpretation notes.

It does not design charts, render charts, or calculate drift. It reads interpretation knowledge from the drift ontology database and combines that knowledge with the current chart payload.

## Knowledge Sources

Primary source of truth:

```text
drift 보고서 PostgreSQL DB
```

The server reads:

- `chart_interpretation_guide` for chart-level guides
- `chart_component_interpretation_rule` for component-level rules
- `document_section` and `section_entity_link` for general, chart-specific, and component-specific guide text
- `chart_definition` and `chart_component` for catalog context

Local files in `docs/prompts/` are only prompt templates used to assemble LLM requests. They are not the source of chart or component interpretation knowledge.

## Run

```powershell
cd "C:\Users\jklee\PycharmProjects\drift_llm_intepretation\llm_interpretation_server"
.\run_interpretation_server.cmd
```

Open:

```text
http://127.0.0.1:8767/api/health
```

Environment variables:

```text
LLM_INTERPRETATION_SERVER_PORT
DRIFT_DB_HOST
DRIFT_DB_PORT
DRIFT_DB_NAME
DRIFT_DB_USER
DRIFT_DB_PASSWORD
LLM_API_ENDPOINT
LLM_MODEL
LLM_API_KEY (선택)
LLM_TIMEOUT_SECONDS (기본값 90)
LLM_RETRY_COUNT (기본값 1)
```

`CHART_INTERPRETATION_PORT` is still accepted as a backward-compatible fallback when `LLM_INTERPRETATION_SERVER_PORT` is not set.

The interpretation server calls an OpenAI-compatible Chat Completions endpoint with an HTTP POST. It does not require an SDK. The default endpoint is `http://127.0.0.1:8001/v1/chat/completions`, and the default model is `gpt-oss-120b`. The request uses `temperature=0`, `max_tokens=6000`, and `reasoning_effort=low`. An API key is sent only when `LLM_API_KEY` is non-empty. A failed request is retried once; if both attempts fail, the existing rule-based interpretation fallback is retained.

## API

```text
GET  /api/health
POST /api/interpret/component
POST /api/interpret/chart
POST /api/interpret/chart/jobs
GET  /api/interpret/chart/jobs/{job_id}
```
