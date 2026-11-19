# Drift Server Implementation Scope v1

## 1. 목적

이 문서는 1차 구현 범위를 명확히 제한한다.

목표는 전체 시스템을 한 번에 완성하는 것이 아니라, 하나의 대표 시나리오를 end-to-end로 동작시키는 것이다.

```text
CASE-010
  -> Test Feeder Server
  -> test_source DB
  -> Drift Server adapter/collector
  -> 10분 metric bucket
  -> ADWIN_MEAN_STREAM method_run
  -> drift_event
  -> CHART-STREAM-001 event analysis payload
  -> LLM Interpretation Server chart job
```

## 2. v1 목표

v1의 성공 기준은 다음이다.

```text
테스트 CSV가 logical time 기준으로 test_source DB에 들어간다.
Drift Server가 10분 window 단위로 데이터를 수집한다.
bucket이 저장된다.
기존 drift_algorithm_impl의 ADWIN_MEAN_STREAM 구현이 wrapper를 통해 실행된다.
drift_event가 생성된다.
event analysis API가 CHART-STREAM-001 payload를 반환한다.
LLM interpretation job을 생성할 수 있다.
```

## 3. 포함 서버

v1에서 사용하는 서버:

```text
Admin Server
  source/adapter/method/chart/test orchestration

Drift Server
  adapter, collector, detector, bucket/event/timeseries/event analysis API

Test Feeder Server
  CASE-010 CSV를 test_source DB에 logical time 기준 insert

Chart Definition Artifact
  CHART-STREAM-001 chart definition snapshot과 runtime payload template을 artifact로 사용

LLM Interpretation Server
  기존 llm_interpretation_server를 사용해 chart interpretation job 생성
```

서버는 처음부터 별도 프로세스로 본다.

기본 런타임 토폴로지는 다음을 따른다.

```text
Admin Server: 8770
Drift Server: 8771
Test Feeder Server: 8772
LLM Interpretation Server: 8767
```

상세 포트, 실행 스크립트, 환경 변수는 `server_runtime_topology.md`를 따른다.

## 4. 포함 Dataset / Method / Chart

v1 대상:

```text
dataset:
  CASE-010 stream numeric mean shift

feature:
  metric

adapter_type:
  test_db_numeric_stream

drift method:
  ADWIN_MEAN_STREAM

runtime_method_key:
  adwin_mean_stream

analysis chart:
  CHART-STREAM-001

payload_adapter_key:
  adwin_mean_stream_to_chart_stream_001
```

Drift Server는 drift 알고리즘 자체를 새로 구현하지 않는다. `drift_algorithm_impl/`에 이미 구현된 알고리즘을 호출하는 runtime registry와 wrapper만 둔다.

## 5. 포함 DB 테이블

현재 v1 dev runtime의 물리 DB 구성은 workspace-local SQLite 파일이다.
DB 구조 생성/보강은 `shared/dev_db.py`의 `ensure_schema()`가 수행한다. 반복 테스트 초기화는 DB 재생성이 아니라 reset API를 사용한다.

```text
drift_control_plane/runtime/sprint2_dev.sqlite3
```

v1에서 필요한 테이블:

```text
raw_event
feed_state
adapter_state
metric_bucket
source_method_assignment
method_state
method_run
drift_event
analysis_chart_registration
managed_contract
```

`drift 보고서` artifact와 `chart_runtime` payload template은 method/chart catalog와 chart payload template의 source of truth로 사용한다.

## 6. 포함 API

### 6.1 Admin Server

```text
GET  /api/admin/health

POST /api/admin/sources
GET  /api/admin/sources

POST /api/admin/adapters
POST /api/admin/adapters/{adapter_id}/start
POST /api/admin/adapters/{adapter_id}/stop
GET  /api/admin/adapters/{adapter_id}/status

GET  /api/admin/drift-methods
POST /api/admin/sources/{source_id}/method-assignments
GET  /api/admin/sources/{source_id}/method-assignments

GET  /api/admin/sources/{source_id}/method-assignments/{assignment_id}/available-charts
POST /api/admin/sources/{source_id}/method-assignments/{assignment_id}/analysis-charts

POST /api/admin/test-mode/enable
POST /api/admin/test-mode/disable
POST /api/admin/test/reset
POST /api/admin/test/feeders/{source_id}/start
POST /api/admin/test/feeders/{source_id}/stop
POST /api/admin/test/tick
GET  /api/admin/test/status
```

### 6.2 Drift Server

```text
GET /api/health

GET /api/sources/{source_id}/timeseries-data
GET /api/sources/{source_id}/events/{event_id}/analysis
```

후속 목표 API:

```text
GET /api/sources
GET /api/sources/{source_id}
GET /api/sources/{source_id}/features
GET /api/sources/{source_id}/timeseries-live
GET /api/sources/{source_id}/events/{event_id}
GET /api/sources/{source_id}/events/{event_id}/analysis/{analysis_chart_id}
```

### 6.3 Test Feeder Server

```text
GET  /api/test-feeder/health
POST /api/test-feeder/feeders
POST /api/test-feeder/feeders/{source_id}/start
POST /api/test-feeder/feeders/{source_id}/stop
GET  /api/test-feeder/feeders/{source_id}/status
POST /api/test-feeder/feeders/{source_id}/tick
POST /api/test-feeder/reset
```

### 6.4 Chart Definition Artifact

v1에서는 Chart Builder 서버를 직접 호출하지 않는다. 필수 artifact는 다음이다.

```text
analysis_chart_registration.chart_definition_json
chart_runtime/payloads/runtime_chart_payloads.json
drift 보고서/charts/method_data.js
```

### 6.5 LLM Interpretation 연동

```text
GET  /api/health
POST /api/interpret/chart/jobs
GET  /api/interpret/chart/jobs/{job_id}
```

## 7. 포함 구현 정책

v1에서 반드시 적용할 정책:

```text
서버 분리:
  Admin / Drift / Test Feeder / LLM 서버 분리
  서버 간 직접 DB 접근 금지
  각 서버는 자기 책임 schema만 write
  Admin Server는 사용자-facing control API만 제공하고 실제 저장은 Drift/Test Feeder/LLM API에 위임

시간/커서:
  poll_once는 10분 window 하나만 처리
  empty window는 empty bucket으로 저장

source adapter:
  SourceAdapter는 fetch와 최소 정규화만 담당
  10분 bucket aggregation은 DriftCollector 책임
  v1 adapter는 test_db_numeric_stream

test feeder:
  Test Feeder는 CSV를 source event처럼 replay
  Harness Clock이 전달한 logicalNow 기준으로 replay
  tickIntervalMinutes 기본값은 1분
  source_event_time은 CSV timestamp
  event_time은 Drift Server 내부 canonical time
  inserted_at은 Harness logicalNow

중복 방지:
  adapter_state row select for update
  metric_bucket unique key
  method_run unique key
  drift_event unique(method_run_id)

chart definition:
  chart_definition_id + chart_definition_json snapshot 저장

reset:
  run reset 필수 구현
  source reset / hard reset은 API contract만 두고 후속 구현 가능

API response:
  신규 서버는 {ok,data,error}
  기존 서버 응답은 client normalize

drift method runtime:
  drift_method_runtime_contract.md의 input/output contract 준수
  drift_algorithm_impl의 기존 알고리즘 구현을 호출하는 wrapper만 구현
  ADWIN 알고리즘 자체를 Drift Server 안에서 다시 구현하지 않음
  v1 ADWIN 입력은 10분 bucket meanValue
  V2의 더 촘촘한 ADWIN은 raw stream contract가 아니라 bucket resolution 축소로 처리
  runtime function은 DB에 직접 접근하지 않음
  method_state/method_run/drift_event 저장은 DriftDetector 책임

timeseries API:
  DB row가 아니라 drift_metric_timeseries용 view model 반환
  empty bucket은 series point로 포함
  live API는 seriesDelta/eventsDelta 반환

analysis payload adapter:
  payload adapter는 DB에 직접 접근하지 않음
  DriftService가 context를 구성해 전달
  payload adapter는 chartPayload만 생성
  chartDefinition은 snapshot을 사용하고 수정하지 않음
```

## 8. v1 제외 범위

다음은 v1에서 제외한다.

```text
source PUT/DELETE
adapter DELETE
source reset 실제 구현
hard reset 실제 구현
human verification workflow
event acknowledge/resolve/ignore API
event merge/extend
event group/incident model
여러 analysis chart 동시 등록 UI
여러 dataset CASE 자동 지원
모든 drift method runtime 지원
drift_algorithm_impl에 없는 알고리즘 신규 구현
분산 lease lock
stale running recovery
chart builder 신규 전체 API
운영용 auth/permission
고급 대시보드 UI
운영 배포/스케일링 설계
```

## 9. Acceptance Criteria

| ID | 기준 |
| --- | --- |
| V1-AC-001 | Admin Server가 CASE-010 source를 등록할 수 있다. |
| V1-AC-002 | Harness가 Test Feeder Server에 logicalNow tick을 직접 보낼 수 있고, Admin Server는 테스트 관제 API를 제공한다. |
| V1-AC-003 | Test Feeder Server가 Harness Clock의 logicalNow에 맞춰 CASE-010 CSV row를 `test_source.raw_event`에 넣는다. |
| V1-AC-004 | Drift Server가 `test_db_numeric_stream` adapter로 10분 window 하나를 가져온다. |
| V1-AC-005 | Drift Server가 10분 metric bucket을 저장한다. |
| V1-AC-006 | 빈 window는 `status=empty`, `row_count=0` bucket으로 저장된다. |
| V1-AC-007 | ADWIN_MEAN_STREAM assignment가 등록된다. |
| V1-AC-008 | Drift Server가 `runtime_method_key=adwin_mean_stream`으로 `drift_algorithm_impl`의 기존 구현을 호출한다. |
| V1-AC-009 | Drift Server wrapper가 표준 runtime input/output contract를 따른다. |
| V1-AC-010 | `method_state`와 `method_run`이 저장된다. |
| V1-AC-011 | drift 조건 충족 시 `drift_event`가 생성된다. |
| V1-AC-012 | `/timeseries-data`가 bucket/event를 반환한다. |
| V1-AC-013 | UI live 동작은 `/timeseries-data` 반복 조회로 bucket/event 최신 상태를 확인한다. |
| V1-AC-014 | analysis chart registration에 `chart_definition_id`와 `chart_definition_json` snapshot이 저장된다. |
| V1-AC-015 | event analysis API가 CHART-STREAM-001 chart payload를 반환한다. |
| V1-AC-016 | LLM Interpretation Server에 chart interpretation job을 생성할 수 있다. |
| V1-AC-017 | run reset 후 등록 정보는 보존되고 실행 데이터만 삭제된다. |
| V1-AC-018 | 같은 window를 두 번 처리해도 bucket/method_run/drift_event가 중복 생성되지 않는다. |

## 10. 관련 이슈

```text
DRI-005 1차 구현 범위 과다
```
