# Drift Monitoring Server API Contracts

## 1. 목적

이 문서는 drift monitoring 구성에서 각 서버가 제공해야 할 API 목록과 요청/응답 구조를 정리한다.

대상 서버는 다음이다.

```text
Admin Server
  control plane. source, adapter, method assignment, analysis chart 등록과 테스트 orchestration 담당.

Drift Server
  data plane. data collection, bucket, method run, drift event, timeseries, event analysis payload 담당.

Test Feeder Server
  테스트 source 역할. CSV를 logical time 기준으로 test source DB에 적재.

Chart Definition Artifact
  이 control plane에서 직접 호출하는 서버가 아니라, 사전 생성된 chart definition snapshot과 runtime payload template으로 취급.

LLM Interpretation Server
  chart payload와 component data를 해석해 자연어 설명 생성.
```

## 2. 공통 응답 규칙

모든 API는 가능한 한 다음 형태를 따른다.

```json
{
  "ok": true,
  "data": {},
  "error": null
}
```

이 envelope는 신규 서버인 Admin Server, Drift Server, Test Feeder Server에 적용한다. 기존 LLM Interpretation Server 응답은 기존 형식을 유지할 수 있으며, 호출 client가 응답을 normalize한다.

오류 응답:

```json
{
  "ok": false,
  "data": null,
  "error": {
    "code": "NOT_FOUND",
    "message": "source not found",
    "details": {}
  }
}
```

시간 값은 ISO-8601 문자열을 사용한다.

```text
2026-07-01T00:10:00Z
```

테스트 모드의 시간은 Harness Clock이 source of truth다.

```text
Harness는 startTime, endTime, tickIntervalMinutes를 config로 확정한다.
Harness가 시작되면 logicalNow는 tickIntervalMinutes 단위로만 전진한다.
Harness 내부 TimeDispatcher가 매 tick마다 logicalNow를 필요한 서버들에게 명시적으로 전달한다.
서버는 테스트 모드에서 자기 clock을 임의로 전진시키지 않는다.
```

## 3. Admin Server API

Admin Server는 orchestration API를 제공한다. 실제 bucket 계산, drift method 실행, event 생성, chart payload 생성은 하지 않는다.

### 3.1 Health

```text
GET /api/admin/health
```

응답:

```json
{
  "ok": true,
  "data": {
    "database": false,
    "driftServer": true,
    "testFeederServer": true,
    "llmServer": true,
    "testMode": false
  },
  "error": null
}
```

### 3.2 Source 목록

```text
GET /api/admin/sources
```

응답:

```json
{
  "ok": true,
  "data": {
    "sources": [
      {
        "sourceId": "case-010",
        "title": "CASE-010 stream numeric mean shift",
        "sourceType": "test_db",
        "sourceUrl": "테스트데이터/CASE-010_stream_numeric_mean_shift/data.csv.gz",
        "status": "active"
      }
    ]
  },
  "error": null
}
```

### 3.3 Source 등록

```text
POST /api/admin/sources
```

요청:

```json
{
  "sourceId": "case-010",
  "title": "CASE-010 stream numeric mean shift",
  "description": "Synthetic stream numeric mean shift dataset",
  "sourceType": "test_db",
  "sourceUrl": "테스트데이터/CASE-010_stream_numeric_mean_shift/data.csv.gz",
  "sourceConfig": {
    "datasetCaseId": "CASE-010"
  }
}
```

응답:

```json
{
  "ok": true,
  "data": {
    "sourceId": "case-010"
  },
  "error": null
}
```

### 3.4 Source 수정/삭제

후속 API contract다. v1 구현 범위에서는 제외한다.

```text
PUT    /api/admin/sources/{source_id}
DELETE /api/admin/sources/{source_id}
```

수정 요청:

```json
{
  "title": "CASE-010 stream numeric mean shift",
  "description": "Updated description",
  "status": "active",
  "sourceConfig": {}
}
```

### 3.5 Adapter 목록

```text
GET /api/admin/adapters?sourceId=case-010
```

응답:

```json
{
  "ok": true,
  "data": {
    "adapters": [
      {
        "adapterId": "case-010-adwin",
        "sourceId": "case-010",
        "adapterType": "test_db_numeric_stream",
        "status": "running",
        "collectionIntervalMinutes": 10,
        "aggregateIntervalMinutes": 10
      }
    ]
  },
  "error": null
}
```

### 3.6 Adapter 등록

```text
POST /api/admin/adapters
```

요청:

```json
{
  "adapterId": "case-010-adwin",
  "sourceId": "case-010",
  "adapterType": "test_db_numeric_stream",
  "adapterTitle": "CASE-010 numeric stream adapter",
  "collectionIntervalMinutes": 10,
  "aggregateIntervalMinutes": 10,
  "sourceConfig": {
    "table": "test_source.raw_event",
    "timeColumn": "event_time",
    "valuePath": "$.metric"
  }
}
```

### 3.7 Adapter 실행/중지/상태

```text
POST /api/admin/adapters/{adapter_id}/start
POST /api/admin/adapters/{adapter_id}/stop
POST /api/admin/adapters/{adapter_id}/catch-up
GET  /api/admin/adapters/{adapter_id}/status
```

상태 응답:

```json
{
  "ok": true,
  "data": {
    "adapterId": "case-010-adwin",
    "status": "running",
    "sourceCursorTime": "2026-07-01T00:10:00Z",
    "availableSourceTime": "2026-07-01T00:20:00Z",
    "lastPollStartedAt": "2026-06-29T12:00:00Z",
    "lastPollFinishedAt": "2026-06-29T12:00:01Z",
    "lastError": null
  },
  "error": null
}
```

### 3.8 실행 가능한 Drift Method 목록

```text
GET /api/admin/drift-methods
```

이 API는 `drift 보고서` DB의 `drift_method`, `method_variant`, `algorithm_variant`, `algorithm_implementation`을 기준으로 목록을 만든다.

v1 구현에서는 Admin Server가 catalog read client를 통해 조회한다. 직접 DB write는 금지하며, 후속으로 별도 Catalog API가 생기면 이 API는 그 Catalog API를 호출하도록 바꿀 수 있다.

응답:

```json
{
  "ok": true,
  "data": {
    "methods": [
      {
        "methodVariantId": 123,
        "algorithmImplementationId": 45,
        "methodCode": "ADWIN",
        "variantCode": "ADWIN_MEAN_STREAM",
        "displayName": "ADWIN mean stream",
        "status": "active",
        "defaultParams": {
          "delta": 0.002
        }
      }
    ]
  },
  "error": null
}
```

### 3.9 Source별 Method Assignment

```text
GET  /api/admin/sources/{source_id}/method-assignments
POST /api/admin/sources/{source_id}/method-assignments
PUT  /api/admin/sources/{source_id}/method-assignments/{assignment_id}
DELETE /api/admin/sources/{source_id}/method-assignments/{assignment_id}
```

등록 요청:

```json
{
  "assignmentId": "assign-case010-adwin",
  "adapterId": "case-010-adwin",
  "featureId": "metric",
  "methodVariantId": 123,
  "algorithmImplementationId": 45,
  "runtimeMethodKey": "adwin_mean_stream",
  "params": {
    "delta": 0.002
  },
  "threshold": {
    "eventLevel": "drift"
  },
  "windowConfig": {
    "bucketResolution": "10m",
    "lookbackBuckets": 144
  },
  "enabled": true
}
```

### 3.10 연결 가능한 Analysis Chart 목록

```text
GET /api/admin/sources/{source_id}/method-assignments/{assignment_id}/available-charts
```

응답:

```json
{
  "ok": true,
  "data": {
    "charts": [
      {
        "chartId": "CHART-STREAM-001",
        "title": "Stream metric drift detail",
        "methodVariantId": 123,
        "recommendedPayloadAdapterKey": "adwin_mean_stream_to_chart_stream_001"
      }
    ]
  },
  "error": null
}
```

### 3.11 Analysis Chart 생성/등록

```text
POST /api/admin/sources/{source_id}/method-assignments/{assignment_id}/analysis-charts
```

요청:

```json
{
  "analysisChartId": "analysis-case010-adwin-stream",
  "chartId": "CHART-STREAM-001",
  "payloadAdapterKey": "adwin_mean_stream_to_chart_stream_001",
  "chartOptions": {
    "title": "CASE-010 ADWIN stream analysis"
  },
  "payloadAdapterConfig": {}
}
```

처리:

```text
Admin Server
  -> 요청 payload의 chart definition snapshot 기본값/보강
  -> Drift Server에 analysis_chart_registration 저장 요청
```

응답:

```json
{
  "ok": true,
  "data": {
    "analysisChartId": "analysis-case010-adwin-stream",
    "chartId": "CHART-STREAM-001",
    "chartDefinitionId": "chartdef-case010-adwin-stream",
    "chartDefinitionSnapshotSaved": true,
    "payloadAdapterKey": "adwin_mean_stream_to_chart_stream_001"
  },
  "error": null
}
```

### 3.12 테스트 모드 제어

```text
POST /api/admin/test-mode/enable
POST /api/admin/test-mode/disable
POST /api/admin/test/reset
GET  /api/admin/test/status
POST /api/admin/test/tick
```

`/api/admin/test/reset` 요청:

```json
{
  "mode": "run",
  "sourceId": "case-010",
  "force": false
}
```

`mode`는 `run`, `source`, `hard` 중 하나다. 기본값은 `run`이다. 1차 구현에서는 `run` reset을 필수 범위로 둔다.

`/api/admin/test/tick` 요청:

```json
{
  "logicalNow": "2026-01-01T00:10:00Z",
  "previousLogicalNow": "2026-01-01T00:09:00Z",
  "tickIntervalMinutes": 1,
  "tickIndex": 10,
  "runCollectorIfDue": true
}
```

`logicalNow`는 Harness Clock의 현재 절대 논리 시각이다. 이 endpoint는 Admin Server의 테스트 상태/관제용 입력으로 둔다. Test Feeder Server와 Drift Server에 대한 시간 전송은 Harness 내부 TimeDispatcher가 각 서버 API를 직접 호출하는 구조를 기본으로 한다.

### 3.13 Report Gallery Data

```text
GET /api/admin/report/gallery-data
```

이 endpoint는 Admin UI가 chart gallery 선택 데이터를 읽기 위한 Admin-owned read API다.

조회 순서:

```text
1. REPORT_GALLERY_BASE_URL이 비어 있지 않으면 선택적 기존 report gallery server의 /api/gallery-data 조회
2. 1번이 비활성화되었거나 실패하면 drift 보고서/charts/method_data.js fallback 사용
```

기본 `REPORT_GALLERY_BASE_URL`은 `http://127.0.0.1:8765`다. 8765 server는 필수 runtime dependency가 아니며, 전체 실행 스크립트가 시작하지 않는다.

응답:

```json
{
  "ok": true,
  "data": {
    "charts": [],
    "chartMethods": {},
    "methodDescriptions": {},
    "runtimeAliases": {},
    "source": {
      "type": "method_data_js_fallback"
    }
  },
  "error": null
}
```

## 4. Drift Server API

Drift Server는 data plane owner다.

API prefix는 목적별로 나눈다.

```text
/api/drift/...
  Admin Server가 호출하는 control/write API

/api/sources/...
  drift_metric_timeseries UI가 호출하는 read/view API
```

Admin Server는 관리 화면용 API를 제공하지만, `drift_server` schema에 직접 쓰지 않는다. source/adapter/method/chart 등록은 Drift Server의 `/api/drift/...` control API가 저장한다.

### 4.1 Health

```text
GET /api/health
```

응답:

```json
{
  "ok": true,
  "data": {
    "database": true,
    "scheduler": true
  },
  "error": null
}
```

Drift Server는 analysis chart 등록 시 `chartDefinitionId`와 함께 chart definition snapshot을 저장한다. Event analysis API는 저장된 snapshot을 사용한다. 이 control plane은 Chart Builder Server를 직접 호출하지 않는다.

### 4.2 Control API: Source 등록/수정/삭제

Admin Server가 호출한다.

```text
GET    /api/drift/sources
POST   /api/drift/sources
```

다음은 후속 API contract다. v1 구현 범위에서는 제외한다.

```text
PUT    /api/drift/sources/{source_id}
DELETE /api/drift/sources/{source_id}
```

처리:

```text
POST는 drift_server.data_source 생성
PUT/DELETE는 후속 구현에서 수정/삭제 또는 비활성화 처리
drift_server.source_feature 초기 등록
```

### 4.3 Control API: Adapter 등록/실행/상태

Admin Server가 호출한다.

```text
GET  /api/drift/adapters?sourceId=case-010
POST /api/drift/adapters
POST /api/drift/adapters/{adapter_id}/start
POST /api/drift/adapters/{adapter_id}/stop
POST /api/drift/adapters/{adapter_id}/catch-up
POST /api/drift/adapters/{adapter_id}/poll-once
GET  /api/drift/adapters/{adapter_id}/status
```

`poll-once`는 10분 window 하나를 처리한다. 테스트 모드에서는 Harness TimeDispatcher가 10분 `logicalNow` 경계에서 호출하고, 수동 점검에도 사용할 수 있다.

### 4.4 Control API: Method Assignment

Admin Server가 호출한다.

```text
POST /api/drift/sources/{source_id}/method-assignments
GET  /api/drift/sources/{source_id}/method-assignments
```

처리:

```text
drift_server.source_method_assignment 생성
drift_server.method_state 초기 row 생성
```

### 4.5 Control API: Analysis Chart Registration

Admin Server가 호출한다.

```text
POST /api/drift/sources/{source_id}/method-assignments/{assignment_id}/analysis-charts
GET  /api/drift/sources/{source_id}/method-assignments/{assignment_id}/analysis-charts
```

처리:

```text
drift_server.analysis_chart_registration 저장
chart_definition_id 저장
chart_definition_json snapshot 저장
payload_adapter_key 저장
```

### 4.6 Control API: Test Reset

Admin Server가 호출한다.

```text
POST /api/drift/test/reset
```

Drift Server 실행 데이터만 reset한다. Test Feeder의 `test_source` reset은 Test Feeder Server API가 수행한다.

### 4.7 View API: Source 목록

```text
GET /api/sources
```

응답:

```json
{
  "ok": true,
  "data": {
    "sources": [
      {
        "sourceId": "case-010",
        "title": "CASE-010 stream numeric mean shift",
        "sourceType": "test_db",
        "sourceUrl": "테스트데이터/CASE-010_stream_numeric_mean_shift/data.csv.gz",
        "adapterStatus": "running",
        "lastCollectedTime": "2026-07-01T00:10:00Z",
        "bucketCount": 144,
        "warningCount": 2,
        "driftCount": 1,
        "timeseriesUrl": "/sources/case-010/timeseries"
      }
    ]
  },
  "error": null
}
```

### 4.8 View API: Source 상세

```text
GET /api/sources/{source_id}
```

후속 목표 API다. 현재 v1 dev runtime에는 별도 구현되어 있지 않다.

응답:

```json
{
  "ok": true,
  "data": {
    "sourceId": "case-010",
    "title": "CASE-010 stream numeric mean shift",
    "sourceType": "test_db",
    "sourceUrl": "테스트데이터/CASE-010_stream_numeric_mean_shift/data.csv.gz",
    "adapters": [],
    "features": []
  },
  "error": null
}
```

### 4.9 View API: Source Feature Metadata

```text
GET /api/sources/{source_id}/features
```

후속 목표 API다. 현재 v1 dev runtime에는 별도 구현되어 있지 않으며, feature metadata는 `/api/sources/{source_id}/timeseries-data` 응답의 `features` field로 제공된다.

응답:

```json
{
  "ok": true,
  "data": {
    "features": [
      {
        "featureId": "metric",
        "label": "Metric",
        "valueType": "numeric",
        "unit": null
      }
    ]
  },
  "error": null
}
```

### 4.10 View API: Timeseries Data

```text
GET /api/sources/{source_id}/timeseries-data?from=2026-01-01T00:00:00Z&to=2026-07-01T00:10:00Z&resolution=10m
```

응답:

```json
{
  "ok": true,
  "data": {
    "sourceId": "case-010",
    "modelId": "case-010",
    "fullDomain": ["2026-01-01T00:00:00Z", "2026-07-01T00:10:00Z"],
    "features": [
      {
        "featureId": "metric",
        "label": "Metric",
        "valueType": "numeric",
        "unit": null
      }
    ],
    "series": {
      "metric": [
        {
          "t": "2026-07-01T00:00:00Z",
          "bucketStart": "2026-06-30T23:50:00Z",
          "bucketEnd": "2026-07-01T00:00:00Z",
          "v": 0.42,
          "count": 10,
          "status": "ok"
        }
      ]
    },
    "events": {
      "metric": [
        {
          "eventId": "evt-001",
          "t": "2026-07-01T00:10:00Z",
          "eventStart": "2026-07-01T00:00:00Z",
          "eventEnd": "2026-07-01T00:10:00Z",
          "level": "drift",
          "score": 0.91,
          "analysisCharts": [
            {
              "analysisChartId": "analysis-case010-adwin-stream",
              "chartId": "CHART-STREAM-001",
              "url": "/sources/case-010/events/evt-001/analysis/analysis-case010-adwin-stream"
            }
          ]
        }
      ]
    },
    "pollIntervalMs": 600000
  },
  "error": null
}
```

### 4.11 View API: Timeseries Live Update

```text
GET /api/sources/{source_id}/timeseries-live?since=2026-07-01T00:00:00Z
```

후속 목표 API다. 현재 v1 dev runtime의 UI live 동작은 `/api/sources/{source_id}/timeseries-data` 반복 조회를 기준으로 한다.

응답:

```json
{
  "ok": true,
  "data": {
    "sourceId": "case-010",
    "resolution": "10m",
    "since": "2026-07-01T00:00:00Z",
    "seriesDelta": {},
    "eventsDelta": {},
    "nextSince": "2026-07-01T00:10:00Z"
  },
  "error": null
}
```

### 4.12 View API: Event 상세

```text
GET /api/sources/{source_id}/events/{event_id}
```

후속 목표 API다. 현재 v1 dev runtime에서는 event marker 상세가 `/timeseries-data` 응답의 `events` field에 포함되고, analysis payload는 `/events/{event_id}/analysis`로 조회한다.

응답:

```json
{
  "ok": true,
  "data": {
    "eventId": "evt-001",
    "sourceId": "case-010",
    "assignmentId": "assign-case010-adwin",
    "methodRunId": "run-001",
    "featureId": "metric",
    "eventStart": "2026-07-01T00:00:00Z",
    "eventEnd": "2026-07-01T00:10:00Z",
    "level": "drift",
    "score": 0.91,
    "analysisCharts": []
  },
  "error": null
}
```

### 4.13 View API: Event Analysis Payload

```text
GET /api/sources/{source_id}/events/{event_id}/analysis
```

현재 v1 dev runtime은 event에 등록된 analysis chart 1개를 기본으로 사용한다. `GET /api/sources/{source_id}/events/{event_id}/analysis/{analysis_chart_id}`는 후속 목표 API다.

응답:

```json
{
  "ok": true,
  "data": {
    "sourceId": "case-010",
    "eventId": "evt-001",
    "assignmentId": "assign-case010-adwin",
    "analysisChartId": "analysis-case010-adwin-stream",
    "chartId": "CHART-STREAM-001",
    "chartDefinitionId": "chartdef-case010-adwin-stream",
    "payloadAdapterKey": "adwin_mean_stream_to_chart_stream_001",
    "chartDefinition": {},
    "chartPayload": {}
  },
  "error": null
}
```

### 4.14 Collector Control API

v1에서는 `/api/internal/...` endpoint를 만들지 않는다. 외부 서버가 Drift Server를 제어해야 하는 경우에는 정식 control API를 둔다.

v1에서 다음 control API를 사용한다.

```text
POST /api/drift/adapters/{adapter_id}/poll-once
POST /api/drift/adapters/{adapter_id}/catch-up
```

Drift Server 내부 scheduler는 HTTP 없이 `DriftCollector.poll_once()` service class를 직접 호출한다.

## 5. Test Feeder Server API

Test Feeder Server는 테스트 모드에서만 사용한다. 운영 source에는 필요 없다.

### 5.1 Health

```text
GET /api/test-feeder/health
```

### 5.2 Feeder 등록

```text
POST /api/test-feeder/feeders
```

요청:

```json
{
  "sourceId": "case-010",
  "datasetCaseId": "CASE-010",
  "csvPath": "테스트데이터/CASE-010_stream_numeric_mean_shift/data.csv.gz",
  "speedFactor": 60,
  "startTime": "2026-01-01T00:00:00Z"
}
```

### 5.3 Feeder 실행/중지/상태

```text
POST /api/test-feeder/feeders/{source_id}/start
POST /api/test-feeder/feeders/{source_id}/stop
GET  /api/test-feeder/feeders/{source_id}/status
```

상태 응답:

```json
{
  "ok": true,
  "data": {
    "sourceId": "case-010",
    "datasetCaseId": "CASE-010",
    "status": "running",
    "logicalCursorTime": "2026-07-01T00:10:00Z",
    "insertedRows": 260000,
    "lastError": null
  },
  "error": null
}
```

### 5.4 Tick

```text
POST /api/test-feeder/feeders/{source_id}/tick
```

요청:

```json
{
  "logicalNow": "2026-01-01T00:10:00Z",
  "previousLogicalNow": "2026-01-01T00:09:00Z",
  "tickIntervalMinutes": 1,
  "tickIndex": 10
}
```

응답:

```json
{
  "ok": true,
  "data": {
    "sourceId": "case-010",
    "logicalCursorTime": "2026-01-01T00:10:00Z",
    "insertedRows": 1
  },
  "error": null
}
```

### 5.5 Reset

```text
POST /api/test-feeder/reset
```

요청:

```json
{
  "sourceId": "case-010",
  "clearRawEvents": true,
  "resetCursor": true
}
```

## 6. Chart Definition Artifact

이 control plane은 Chart Builder Server API를 직접 사용하지 않는다.

v1에서 필요한 chart definition과 catalog 정보는 다음 artifact를 기준으로 한다.

```text
analysis_chart_registration.chart_definition_json
chart_runtime/payloads/runtime_chart_payloads.json
drift 보고서/charts/method_data.js
```

Admin Server는 선택 가능한 chart catalog를 `GET /api/admin/report/gallery-data`로 제공한다. 이 endpoint는 선택적 기존 report gallery server를 우선 조회할 수 있지만, 필수 기준은 `drift 보고서/charts/method_data.js` fallback artifact다. Drift Server는 analysis chart 등록 시 전달받은 snapshot을 저장하고, event analysis payload adapter는 저장된 snapshot과 runtime payload template을 사용한다.

## 7. LLM Interpretation Server API

LLM Interpretation Server는 이미 별도 폴더로 분리되어 있으며, chart/component 해석을 담당한다.

### 7.1 Health

```text
GET /api/health
```

응답:

```json
{
  "ok": true,
  "database": true,
  "codexExec": true
}
```

### 7.2 Chart Interpretation Job 생성

```text
POST /api/interpret/chart/jobs
```

요청:

```json
{
  "chartId": "CHART-STREAM-001",
  "chartDefinition": {},
  "chartPayload": {},
  "components": [],
  "context": {
    "sourceId": "case-010",
    "eventId": "evt-001",
    "methodCode": "ADWIN",
    "variantCode": "ADWIN_MEAN_STREAM"
  }
}
```

응답:

```json
{
  "ok": true,
  "jobId": "interp-job-001",
  "status": "queued"
}
```

### 7.3 Chart Interpretation Job 조회

```text
GET /api/interpret/chart/jobs/{job_id}
```

응답:

```json
{
  "ok": true,
  "jobId": "interp-job-001",
  "status": "completed",
  "result": {
    "summary": "",
    "componentNotes": [],
    "warnings": []
  }
}
```

## 8. 서버 간 호출 흐름

### 8.1 관리자 등록 흐름

```text
Admin UI
  -> Admin Server: POST /api/admin/sources
  -> Admin Server: POST /api/admin/adapters
  -> Admin Server: GET /api/admin/drift-methods
  -> Admin Server: POST /api/admin/sources/{source_id}/method-assignments
  -> Admin Server: GET available-charts
  -> Admin Server: POST analysis-charts
      -> Admin/Drift Server: chart definition snapshot 저장
      -> Drift Server: save analysis_chart_registration
```

### 8.2 테스트 실행 흐름

```text
Harness Server
  -> Admin Server: control API contract 검증과 관제 상태 조회
  -> Test Feeder Server: tick(logicalNow)
  -> Drift Server: poll-once(logicalNow 기준)

Drift Server
  -> bucket/method_run/drift_event 저장
```

단위 테스트에서는 같은 service class를 직접 호출할 수 있다. 통합 테스트와 테스트 하네스는 운영 구조와 동일하게 HTTP API contract를 기준으로 검증한다.

### 8.3 UI 조회 흐름

```text
drift_metric_timeseries UI
  -> Drift Server: GET /api/sources/{source_id}/timeseries-data
  -> Drift Server: GET /api/sources/{source_id}/events/{event_id}/analysis
  -> LLM Interpretation Server: POST /api/interpret/chart/jobs
```

## 9. 초기 구현 API 범위

1차 구현은 다음 API만 구현해도 end-to-end 검증이 가능하다.

```text
Admin Server
  POST /api/admin/sources
  POST /api/admin/adapters
  GET  /api/admin/drift-methods
  POST /api/admin/sources/{source_id}/method-assignments
  POST /api/admin/sources/{source_id}/method-assignments/{assignment_id}/analysis-charts
  POST /api/admin/test/reset
  POST /api/admin/test/tick

Drift Server
  POST /api/drift/sources
  POST /api/drift/adapters
  POST /api/drift/sources/{source_id}/method-assignments
  POST /api/drift/sources/{source_id}/method-assignments/{assignment_id}/analysis-charts
  POST /api/drift/adapters/{adapter_id}/poll-once
  POST /api/drift/test/reset
  GET  /api/sources/{source_id}/timeseries-data
  GET  /api/sources/{source_id}/events/{event_id}/analysis

Test Feeder
  POST /api/test-feeder/feeders
  POST /api/test-feeder/feeders/{source_id}/tick
  POST /api/test-feeder/reset

LLM Interpretation
  POST /api/interpret/chart/jobs
```
