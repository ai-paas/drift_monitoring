# Drift Metric Timeseries

This folder contains the standalone project for the `drift_metric_timeseries` graph.

It owns the long-range drift metric timeseries UI, live polling demo, state-model harness, and component-specific requirements/design documents. It uses the shared chart runtime only for the event analysis popup.

## Structure

```text
docs/   requirements, state model, UI notes, integration design
web/    demo, harness, CSS/JS, sample yearly data
tests/  Playwright demo and harness tests
```

## Runtime URLs

### Control Plane Integrated Mode

현재 control plane 통합 실행 기준 URL은 Admin Server가 serve하는 `/admin/timeseries/...` 경로다.

```text
http://127.0.0.1:8770/admin/timeseries/drift_metric_timeseries_demo.html?testMode=1&autoPoll=1&pollMs=1500&sourceId=case-010&apiBase=http://127.0.0.1:8770&llmJobEndpoint=http://127.0.0.1:8770/api/admin/llm/interpret/chart/jobs
```

Admin UI에서 datasource를 연결하면 같은 형식의 URL을 자동 생성한다.

통합 모드 API:

```text
GET /api/sources/{source_id}/timeseries-data?resolution=10m
GET /api/sources/{source_id}/events/{event_id}/analysis
POST /api/admin/llm/interpret/chart/jobs
GET /api/admin/llm/interpret/chart/jobs/{job_id}
```

위 URL에서 `apiBase=http://127.0.0.1:8770`을 사용하면 Admin Server가 Drift Server read API를 proxy한다. Drift Server를 직접 호출하려면 `apiBase=http://127.0.0.1:8771`을 사용할 수 있다.

LLM 해석 job endpoint는 `llmJobEndpoint` query로 지정한다. Control plane 통합 실행에서는 Admin Server proxy인 `/api/admin/llm/interpret/chart/jobs`를 사용한다. Standalone으로 LLM 서버를 직접 호출하려면 `llmApiBase=http://127.0.0.1:8767` 또는 `llmJobEndpoint=http://127.0.0.1:8767/api/interpret/chart/jobs`를 지정한다. 값을 생략하면 기존 호환을 위해 `http://127.0.0.1:8767/api/interpret/chart/jobs`를 사용한다.

### Standalone Static Validation

브라우저 정적 검증은 파일 URL 또는 테스트 스크립트의 `as_uri()` 경로를 사용한다. 이때 서버 live API를 호출하지 않도록 `live=0`을 붙인다.

```text
file:///.../drift_metric_timeseries/web/drift_metric_timeseries_demo.html?live=0
file:///.../drift_metric_timeseries/web/drift_metric_timeseries_harness.html
```

### Legacy Chart Builder Demo Bridge

When `chart_builder_server.py` is running:

```text
http://127.0.0.1:8766/drift_metric_timeseries/drift_metric_timeseries_demo.html
http://127.0.0.1:8766/drift_metric_timeseries/drift_metric_timeseries_harness.html
```

이 경로는 과거 standalone demo bridge 호환용이다. 현재 control plane 통합 실행 기준 URL은 아니다.

Legacy demo bridge API:

```text
/api/drift-metric-timeseries/live/reset
/api/drift-metric-timeseries/live/metadata
/api/drift-metric-timeseries/live/next-day
/api/drift-metric-timeseries/events/analyze
```

## Validation

```powershell
python -m py_compile drift_metric_timeseries\tests\drift_metric_timeseries_demo_test.py drift_metric_timeseries\tests\drift_metric_timeseries_harness_test.py
python drift_metric_timeseries\tests\drift_metric_timeseries_harness_test.py
python drift_metric_timeseries\tests\drift_metric_timeseries_demo_test.py
```
