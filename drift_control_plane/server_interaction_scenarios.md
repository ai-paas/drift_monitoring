# Drift Monitoring Server Interaction Scenarios

## 1. 목적

이 문서는 drift monitoring 시스템에서 서버들이 어떤 사용 시나리오에서 어떤 순서로 API를 호출하는지 정리한다.

Endpoint 목록과 request/response schema의 source of truth는 `api_contracts.md`다. 이 문서는 시나리오별 호출 흐름만 설명한다.

대상 서버:

```text
Admin Server
Drift Server
Test Feeder Server
LLM Interpretation Server
drift_metric_timeseries UI
```

## 2. 사용 시나리오 목록

| ID | 시나리오 | 목적 |
| --- | --- | --- |
| SCN-001 | 시스템 상태 확인 | 각 서버와 DB 연결 상태를 확인한다. |
| SCN-002 | 테스트 모드 초기화 | 테스트 DB와 drift server 상태를 초기화한다. |
| SCN-003 | data source 등록 | 외부 또는 테스트 data source를 등록한다. |
| SCN-004 | source adapter 등록 | data source에서 데이터를 가져올 adapter를 등록한다. |
| SCN-005 | drift method assignment 등록 | data source에 사용할 drift method/variant를 지정한다. |
| SCN-006 | analysis chart 생성/등록 | method assignment에 분석용 chart와 payload adapter를 등록한다. |
| SCN-007 | 테스트 feeder 실행 | 테스트 CSV를 logical time 기준으로 테스트 DB에 적재한다. |
| SCN-008 | adapter 수집 실행 | drift server가 source에서 10분 window를 가져와 bucket을 만든다. |
| SCN-009 | drift 감지 및 event 생성 | bucket 생성 후 assigned drift method를 실행하고 drift event를 저장한다. |
| SCN-010 | source별 timeseries 화면 조회 | UI가 source의 bucket/event를 조회해 시계열 chart를 보여준다. |
| SCN-011 | live update | UI가 새 bucket/event만 반복 조회한다. |
| SCN-012 | drift event analysis chart 조회 | 사용자가 event의 analysis chart 링크를 눌러 분석 chart를 연다. |
| SCN-013 | LLM chart 해석 요청 | 분석 chart payload를 LLM interpretation server로 보내 해석을 생성한다. |
| SCN-014 | adapter 중단 후 catch-up | adapter가 중단된 뒤 재시작하면서 누락 window를 순차 처리한다. |
| SCN-015 | 자동 테스트 tick 실행 | 테스트 하네스가 sleep 없이 feeder/collector를 직접 tick으로 전진시킨다. |

## 3. SCN-001 시스템 상태 확인

관리자 화면이 처음 열릴 때 각 서버 상태를 확인한다.

```text
Admin UI
  -> Admin Server: GET /api/admin/health

Admin Server
  -> Drift Server: GET /api/health
  -> LLM Interpretation Server: GET /api/health
  -> Test Feeder Server: GET /api/test-feeder/health
```

응답에서 Admin Server는 서버별 연결 가능 여부와 test mode 상태를 합쳐 반환한다.

```json
{
  "ok": true,
  "data": {
    "database": true,
    "driftServer": true,
    "llmServer": true,
    "testFeeder": true,
    "testMode": true
  },
  "error": null
}
```

## 4. SCN-002 테스트 모드 초기화

테스트를 새로 시작할 때 테스트 DB와 drift server 상태를 비운다.

```text
Admin UI
  -> Admin Server: POST /api/admin/test-mode/enable
  -> Admin Server: POST /api/admin/test/reset

Admin Server
  -> Test Feeder Server: stop feeder if running
  -> Drift Server: stop adapter if running
  -> Test Feeder Server: POST /api/test-feeder/reset
  -> Drift Server: POST /api/drift/test/reset
```

reset 기본 mode는 `run`이다.

```json
{
  "mode": "run",
  "sourceId": "case-010",
  "force": false
}
```

서버 분리 원칙상 Drift Server DB를 Admin Server가 직접 수정하지 않는다.

결과:

```text
test_source.raw_event 비움
test_source.feed_state 초기화
drift_server.adapter_state 초기화
drift_server.metric_bucket 비움
drift_server.method_state 비움
drift_server.method_run 비움
drift_server.drift_event 비움
```

run reset에서는 다음 등록 정보는 보존한다.

```text
data_source
source_feature
source_adapter
source_method_assignment
analysis_chart_registration
chart_payload_adapter
```

## 5. SCN-003 Data Source 등록

관리자가 외부 또는 테스트 data source를 등록한다.

```text
Admin UI
  -> Admin Server: POST /api/admin/sources

Admin Server
  -> Drift Server: POST /api/drift/sources
```

요청 예:

```json
{
  "sourceId": "case-010",
  "title": "CASE-010 stream numeric mean shift",
  "sourceType": "test_db",
  "sourceUrl": "테스트데이터/CASE-010_stream_numeric_mean_shift/data.csv.gz",
  "sourceConfig": {
    "datasetCaseId": "CASE-010"
  }
}
```

결과:

```text
drift_server.data_source 생성
```

## 6. SCN-004 Source Adapter 등록

관리자가 data source에 adapter를 연결한다.

```text
Admin UI
  -> Admin Server: POST /api/admin/adapters

Admin Server
  -> Drift Server: POST /api/drift/adapters
```

요청 예:

```json
{
  "adapterId": "case-010-adwin",
  "sourceId": "case-010",
  "adapterType": "test_db_numeric_stream",
  "collectionIntervalMinutes": 10,
  "aggregateIntervalMinutes": 10,
  "sourceConfig": {
    "table": "test_source.raw_event",
    "timeColumn": "event_time",
    "valuePath": "$.metric"
  }
}
```

결과:

```text
drift_server.source_adapter 생성
drift_server.adapter_state 생성
```

## 7. SCN-005 Drift Method Assignment 등록

관리자가 source에서 사용할 drift method를 선택한다.

```text
Admin UI
  -> Admin Server: GET /api/admin/drift-methods

Admin Server
  -> drift 보고서 DB 조회
      drift_method
      method_variant
      algorithm_variant
      algorithm_implementation

Admin UI
  -> Admin Server: POST /api/admin/sources/{source_id}/method-assignments

Admin Server
  -> Drift Server: POST /api/drift/sources/{source_id}/method-assignments
```

결과:

```text
drift_server.source_method_assignment 생성
```

중요한 점:

```text
관리자 서버는 method를 선택하고 저장만 요청한다.
drift 알고리즘 실행은 drift server가 bucket 생성 후 수행한다.
```

## 8. SCN-006 Analysis Chart 생성/등록

관리자가 method assignment에 분석용 chart를 등록한다.

```text
Admin UI
  -> Admin Server: GET /api/admin/sources/{source_id}/method-assignments/{assignment_id}/available-charts

Admin Server
  -> catalog read client로 method/variant와 연결된 chart 목록 조회
  -> Drift Server 또는 local registry에서 payload adapter 가능 여부 조회

Admin UI
  -> Admin Server: POST /api/admin/sources/{source_id}/method-assignments/{assignment_id}/analysis-charts

Admin Server
  -> 요청 payload 또는 사전 생성 artifact에서 chart definition snapshot 준비
  -> Drift Server: POST /api/drift/sources/{source_id}/method-assignments/{assignment_id}/analysis-charts
```

Drift Server 등록 요청:

```json
{
  "analysisChartId": "analysis-case010-adwin-stream",
  "chartId": "CHART-STREAM-001",
  "chartDefinitionId": "chartdef-case010-adwin-stream",
  "chartDefinition": {},
  "payloadAdapterKey": "adwin_mean_stream_to_chart_stream_001",
  "payloadAdapterConfig": {}
}
```

결과:

```text
drift_server.analysis_chart_registration 생성
chart definition snapshot 저장
```

중요한 점:

```text
analysis chart는 반드시 payload adapter와 함께 등록한다.
event 발생 시 임의 chart를 새로 만들지 않는다.
```

## 9. SCN-007 테스트 Feeder 실행

테스트 모드에서 CSV 데이터를 logical time 기준으로 테스트 DB에 넣는다.

```text
Admin UI
  -> Admin Server: POST /api/admin/test/feeders/{source_id}/start

Admin Server
  -> Test Feeder Server: POST /api/test-feeder/feeders
  -> Test Feeder Server: POST /api/test-feeder/feeders/{source_id}/start
```

브라우저 데모 모드:

```text
Test Feeder Scheduler
  -> Harness Clock이 생성한 logicalNow로 CsvFeeder.tick(logicalNow)
  -> test_source.raw_event insert
```

자동 테스트 모드:

```text
Test Harness
  -> startTime/endTime/tickIntervalMinutes로 logicalNow sequence 생성
  -> CsvFeeder.tick(logicalNow)
```

## 10. SCN-008 Adapter 수집 실행

관리자가 adapter를 실행한다.

```text
Admin UI
  -> Admin Server: POST /api/admin/adapters/{adapter_id}/start

Admin Server
  -> Drift Server: POST /api/drift/adapters/{adapter_id}/start
```

브라우저 데모 모드:

```text
Drift Server Scheduler
  -> 매 10초마다 DriftCollector.poll_once(adapter_id)
```

운영 모드:

```text
Drift Server Scheduler
  -> 매 10분마다 DriftCollector.poll_once(adapter_id)
```

수집 규칙:

```text
read_start = adapter_state.source_cursor_time
read_end = read_start + 10분
rows = adapter.fetch(read_start, read_end)
bucket = aggregate(rows)
save(metric_bucket)
adapter_state.source_cursor_time = read_end
```

## 11. SCN-009 Drift 감지 및 Event 생성

bucket 저장 후 drift server가 source에 할당된 method를 실행한다.

```text
DriftCollector
  -> metric_bucket 저장
  -> source_method_assignment 조회
  -> DriftDetector.run(assignment, recent_buckets)
  -> method_run 저장
  -> warning/drift 조건이면 drift_event 저장
```

관련 저장 결과:

```text
drift_server.metric_bucket
drift_server.method_run
drift_server.drift_event
```

이 과정에는 Admin Server가 개입하지 않는다.

## 12. SCN-010 Source별 Timeseries 화면 조회

사용자가 source별 URL을 연다.

```text
Browser
  -> Drift Server: GET /sources/{source_id}/timeseries

drift_metric_timeseries UI
  -> Drift Server: GET /api/sources/{source_id}/timeseries-data?from=...&to=...&resolution=10m
```

현재 v1 dev runtime에서 source metadata와 feature metadata는 `timeseries-data` 응답의 `sourceId`, `modelId`, `features` field로 함께 전달된다. 별도 `/api/sources/{source_id}`와 `/features` endpoint는 후속 목표 API다.

응답에는 bucket series와 event 목록이 포함된다.

event 응답에는 등록된 analysis chart link가 포함되어야 한다.

```json
{
  "eventId": "evt-001",
  "level": "drift",
  "analysisCharts": [
    {
      "analysisChartId": "analysis-case010-adwin-stream",
      "chartId": "CHART-STREAM-001",
      "url": "/sources/case-010/events/evt-001/analysis/analysis-case010-adwin-stream"
    }
  ]
}
```

## 13. SCN-011 Live Update

현재 v1 dev runtime에서 timeseries UI live 동작은 `/timeseries-data`를 반복 조회한다.

```text
drift_metric_timeseries UI
  -> Drift Server: 반복 GET /api/sources/{source_id}/timeseries-data?resolution=10m
```

`/api/sources/{source_id}/timeseries-live?since=...`는 후속 목표 API다.

운영 모드:

```text
poll interval = 600000ms
```

테스트 데모 모드:

```text
poll interval = 10000ms
```

응답:

```json
{
  "ok": true,
  "data": {
    "buckets": [],
    "events": [],
    "nextSince": "2026-07-01T00:10:00Z"
  },
  "error": null
}
```

## 14. SCN-012 Drift Event Analysis Chart 조회

사용자가 event 아래의 analysis chart link를 누른다.

```text
drift_metric_timeseries UI
  -> Drift Server: GET /api/sources/{source_id}/events/{event_id}/analysis
```

Drift Server 내부 처리:

```text
drift_event 조회
source_method_assignment 조회
analysis_chart_registration 조회
chart_definition_json snapshot 조회
snapshot이 없으면 payload context incomplete 오류 처리
chart_payload_adapter 조회
payload_adapter_key로 code function 선택
metric_bucket + method_run + drift_event 조회
chart runtime payload 생성
chart definition + chart payload 반환
```

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

## 15. SCN-013 LLM Chart 해석 요청

analysis chart가 렌더링된 뒤, UI 또는 chart runtime이 LLM interpretation server에 해석을 요청한다.

```text
drift_metric_timeseries UI 또는 analysis chart UI
  -> LLM Interpretation Server: POST /api/interpret/chart/jobs
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

LLM Interpretation Server 내부 처리:

```text
chart/component guide 조회
chart-specific guide 조회
LLM 호출
job result 저장 또는 반환
```

결과 조회:

```text
GET /api/interpret/chart/jobs/{job_id}
```

## 16. SCN-014 Adapter 중단 후 Catch-up

adapter가 중단되었다가 다시 켜진다.

```text
Admin UI
  -> Admin Server: POST /api/admin/adapters/{adapter_id}/catch-up

Admin Server
  -> Drift Server: POST /api/drift/adapters/{adapter_id}/catch-up
```

Drift Server 처리:

```text
while source_cursor_time + 10분 <= available_source_time:
  process_one_window()
```

중요한 제한:

```text
catch-up도 10분 window 단위로 순차 처리한다.
raw data 전체를 한 번에 메모리에 올리지 않는다.
```

## 17. SCN-015 자동 테스트 Tick 실행

자동 테스트에서는 여러 서버 프로세스를 띄우지 않고 service class를 직접 호출한다.

```text
Test Harness
  -> AdminService.reset_test_environment()
  -> AdminService.register_source()
  -> AdminService.register_adapter()
  -> AdminService.register_method_assignment()
  -> AdminService.register_analysis_chart()

for logicalNow in harness_clock.iter_ticks():
  -> CsvFeeder.tick(logicalNow)
  -> if logicalNow is 10분 경계:
       DriftCollector.poll_once(adapter_id, logicalNow)
```

검증:

```text
metric_bucket count == 6
method_run count > 0
drift_event count >= expected
event analysis payload 생성 가능
```

## 18. 1차 End-to-End 시나리오

초기 구현에서 가장 먼저 검증할 시나리오는 다음이다.

```text
CASE-010
  -> test feeder가 Harness logicalNow 기준으로 데이터 적재
  -> test_db_numeric_stream adapter
  -> 10분 metric bucket 생성
  -> ADWIN_MEAN_STREAM 실행
  -> drift_event 생성
  -> CHART-STREAM-001 analysis payload 생성
  -> LLM interpretation job 생성
```

필수 API 호출 순서:

```text
POST /api/admin/test-mode/enable
POST /api/admin/test/reset
POST /api/admin/sources
POST /api/admin/adapters
GET  /api/admin/drift-methods
POST /api/admin/sources/{source_id}/method-assignments
POST /api/admin/sources/{source_id}/method-assignments/{assignment_id}/analysis-charts
POST /api/admin/test/feeders/{source_id}/start
POST /api/admin/adapters/{adapter_id}/start

GET /api/sources/{source_id}/timeseries-data
GET /api/sources/{source_id}/events/{event_id}/analysis
POST /api/interpret/chart/jobs
```
