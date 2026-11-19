# Drift Monitoring Servers Internal Implementation Design

## 1. 목적

이 문서는 새로 만들 서버들의 내부 구현 방법을 정리한다.

대상은 다음이다.

```text
Admin Server
Drift Server
Test Feeder Server
Chart Definition Artifact 연동
LLM Interpretation Server 연동
공통 DB / service layer / scheduler / clock
```

목표는 각 서버가 맡을 책임을 코드 구조로 명확히 나누는 것이다. 특히 Admin Server는 orchestration만 하고, 실제 데이터 처리와 drift 계산은 Drift Server의 service layer에서 수행한다.

## 2. 구현 원칙

| ID | 원칙 | 설명 |
| --- | --- | --- |
| IMP-001 | service class 우선 | 핵심 로직은 FastAPI endpoint 안에 직접 쓰지 않고 service class에 둔다. |
| IMP-002 | HTTP는 얇게 | endpoint는 요청 검증, service 호출, 응답 변환만 담당한다. |
| IMP-003 | repository 분리 | DB 접근은 repository class로 분리한다. |
| IMP-004 | scheduler 교체 가능 | real scheduler와 Harness logicalNow tick을 같은 service layer 위에서 동작하게 한다. |
| IMP-005 | clock 주입 | 운영은 `RealClock`, 자동 테스트는 Harness가 전달한 `logicalNow`를 기준으로 동작한다. |
| IMP-006 | registry 명시 | drift method runtime과 chart payload adapter는 key 기반 registry로 찾는다. |
| IMP-007 | vertical slice 우선 | 초기 구현은 `CASE-010 + ADWIN_MEAN_STREAM + CHART-STREAM-001` 하나를 end-to-end로 완성한다. |
| IMP-008 | 알고리즘 재사용 | Drift Server는 drift 알고리즘을 새로 구현하지 않고 `drift_algorithm_impl`의 기존 구현을 wrapper로 호출한다. |

## 3. 폴더 구조 초안

서버는 처음부터 별도 폴더와 별도 프로세스로 분리한다.

공통 규칙:

```text
서버 간 호출은 HTTP API client class를 통해 수행한다.
다른 서버의 service/repository를 import하지 않는다.
DB write는 각 서버가 소유한 schema에만 수행한다.
```

```text
admin_server/
  run_admin_server.cmd
  app/
    __init__.py
    main.py
    config.py
    schemas.py

    routers/
      __init__.py
      admin_router.py

    services/
      __init__.py
      source_admin_service.py
      adapter_admin_service.py
      method_admin_service.py
      chart_admin_service.py
      test_mode_service.py

    clients/
      __init__.py
      drift_server_client.py
      test_feeder_client.py
      llm_interpretation_client.py

  tests/
    test_admin_api_contract.py

drift_server/
  run_drift_server.cmd
  README.md
  requirements.md
  api_contracts.md
  server_interaction_scenarios.md
  internal_implementation_design.md

  app/
    __init__.py
    main.py
    config.py
    db.py
    clock.py
    schemas.py

    drift/
      __init__.py
      router.py
      service.py
      collector.py
      detector.py
      runtime_registry.py
      payload_registry.py

    adapters/
      __init__.py
      base.py
      test_db_numeric_stream.py

    repositories/
      __init__.py
      source_repository.py
      adapter_repository.py
      feature_repository.py
      bucket_repository.py
      method_repository.py
      event_repository.py
      analysis_chart_repository.py

    clients/
      __init__.py
      llm_interpretation_client.py
      drift_report_catalog_client.py

    schedulers/
      __init__.py
      real_scheduler.py
      manual_scheduler.py

    payload_adapters/
      __init__.py
      adwin_mean_stream_to_chart_stream_001.py

    runtime_methods/
      __init__.py
      adwin_mean_stream.py

  migrations/
    001_init_drift_server.sql

  tests/
    test_case010_vertical_slice.py
    test_collector_windowing.py
    test_payload_adapter.py

test_feeder_server/
  run_test_feeder_server.cmd
  app/
    __init__.py
    main.py
    config.py
    db.py
    clock.py
    schemas.py

    routers/
      __init__.py
      feeder_router.py

    services/
      __init__.py
      feeder_service.py
      csv_reader.py

    repositories/
      __init__.py
      raw_event_repository.py
      feed_state_repository.py

  migrations/
    001_init_test_source.sql

  tests/
    test_feeder_tick.py
```

## 4. 공통 구성 요소

### 4.1 Config

`app/config.py`

역할:

```text
SQLite dev DB path
test mode flag
logical time speed
LLM interpretation base URL
scheduler interval
```

초기 환경 변수 예:

```text
LLM_INTERPRETATION_BASE_URL
TEST_MODE
```

현재 Drift/Test Feeder DB는 `shared/dev_db.py`의 기본값인 `drift_control_plane/runtime/sprint2_dev.sqlite3`를 사용한다. `DRIFT_SERVER_DATABASE_URL`과 `DRIFT_REPORT_DATABASE_URL`은 현재 실행 코드의 필수 환경 변수가 아니다.

### 4.2 DB

`app/db.py`

역할:

```text
SQLite connection 생성
transaction helper 제공
repository factory 제공
```

초기 구현은 단순하게 시작한다.

```python
class Database:
    def execute(self, sql: str, params: dict | None = None): ...
    def fetch_one(self, sql: str, params: dict | None = None): ...
    def fetch_all(self, sql: str, params: dict | None = None): ...
    def transaction(self): ...
```

### 4.3 Clock

`app/clock.py`

```python
class Clock:
    def now(self): ...

class RealClock(Clock):
    def now(self): ...

class ManualClock(Clock):
    def now(self): ...
    def set_logical_now(self, logical_now): ...
```

테스트 모드에서 clock은 자체적으로 시간을 전진시키지 않는다. Harness Clock이 생성한 `logicalNow`를 API 요청으로 받고, feeder와 collector는 그 값을 기준으로 처리한다.

## 5. Admin Server 내부 구현

Admin Server는 control plane이다.

### 5.1 Router

`app/routers/admin_router.py`

담당 endpoint:

```text
GET  /api/admin/health
GET  /api/admin/sources
POST /api/admin/sources

GET  /api/admin/adapters
POST /api/admin/adapters
POST /api/admin/adapters/{adapter_id}/start
POST /api/admin/adapters/{adapter_id}/stop
POST /api/admin/adapters/{adapter_id}/catch-up
GET  /api/admin/adapters/{adapter_id}/status

GET  /api/admin/drift-methods
GET  /api/admin/sources/{source_id}/method-assignments
POST /api/admin/sources/{source_id}/method-assignments

GET  /api/admin/sources/{source_id}/method-assignments/{assignment_id}/available-charts
POST /api/admin/sources/{source_id}/method-assignments/{assignment_id}/analysis-charts

POST /api/admin/test-mode/enable
POST /api/admin/test-mode/disable
POST /api/admin/test/reset
POST /api/admin/test/tick
GET  /api/admin/test/status
```

### 5.2 Service

`app/admin/service.py`

주요 class:

```python
class AdminService:
    def register_source(...)
    def register_adapter(...)
    def start_adapter(...)
    def stop_adapter(...)
    def catch_up_adapter(...)
    def list_drift_methods(...)
    def register_method_assignment(...)
    def list_available_charts(...)
    def create_analysis_chart(...)
    def enable_test_mode(...)
    def reset_test_environment(...)
    def record_test_tick(...)
```

구현 규칙:

```text
source/adapter/method assignment 저장은 drift server repository/service에 위임한다.
chart definition은 요청 payload snapshot 또는 사전 생성 artifact를 사용해 Drift Server registration에 전달한다.
drift method 목록은 DriftReportCatalogClient에 위임한다.
test reset은 각 서버 reset API를 orchestration한다.
test tick은 Admin 관제 상태 기록용이며, FeederService와 DriftCollector 실행은 Harness TimeDispatcher가 각 서버 API를 직접 호출한다.
```

AdminService가 직접 하면 안 되는 일:

```text
CSV row 파싱
10분 bucket 계산
drift method 실행
drift_event 생성
chart payload 생성
```

## 6. Drift Server 내부 구현

Drift Server는 data plane이다.

### 6.1 Router

`app/drift/router.py`

담당 endpoint:

```text
GET /api/health
GET /api/sources/{source_id}/timeseries-data
GET /api/sources/{source_id}/events/{event_id}/analysis
```

후속 목표 endpoint:

```text
GET /api/sources
GET /api/sources/{source_id}
GET /api/sources/{source_id}/features
GET /api/sources/{source_id}/timeseries-live
GET /api/sources/{source_id}/events/{event_id}
GET /api/sources/{source_id}/events/{event_id}/analysis/{analysis_chart_id}
```

v1에서는 `/api/internal/...` endpoint를 만들지 않는다. 서버 간 호출은 정식 API와 client class를 사용한다.

```text
POST /api/drift/adapters/{adapter_id}/poll-once
POST /api/drift/adapters/{adapter_id}/catch-up
POST /api/drift/test/reset
```

위 control API는 필요할 때만 추가한다. Drift Server 내부 scheduler는 HTTP 없이 `DriftCollector.poll_once()`를 직접 호출한다.

### 6.2 DriftService

`app/drift/service.py`

역할:

```text
source 목록 조회
source 상세 조회
feature metadata 조회
timeseries data 조립
timeseries live update 조립
event 상세 조회
event analysis payload 생성
```

주요 method:

```python
class DriftService:
    def list_sources(...)
    def get_source(...)
    def list_features(source_id: str)
    def get_timeseries_data(source_id: str, from_time, to_time, resolution: str)
    def get_timeseries_live(source_id: str, since)
    def get_event(source_id: str, event_id: str)
    def build_event_analysis(source_id: str, event_id: str, analysis_chart_id: str | None)
```

### 6.3 DriftCollector

`app/drift/collector.py`

역할:

```text
adapter_state.source_cursor_time 읽기
read_start ~ read_end 계산
SourceAdapter.fetch 호출
10분 bucket 집계
metric_bucket 저장
adapter_state 갱신
DriftDetector 호출
```

핵심 method:

```python
class DriftCollector:
    def poll_once(self, adapter_id: str):
        ...

    def catch_up(self, adapter_id: str, available_source_time):
        ...
```

정상 poll 규칙:

```text
poll_once는 항상 10분 window 하나만 처리한다.
read_end 이후 source data가 많아도 무시한다.
```

catch-up 규칙:

```text
while source_cursor_time + 10분 <= available_source_time:
    poll_once(adapter_id)
```

### 6.4 SourceAdapter

`app/adapters/base.py`

```python
class SourceAdapter:
    adapter_type: str

    def fetch(self, source_config: dict, start_time, end_time) -> list[dict]:
        ...

    def available_time(self, source_config: dict):
        ...
```

초기 구현 adapter:

```text
app/adapters/test_db_numeric_stream.py
```

역할:

```text
test_source.raw_event에서 event_time >= start_time and event_time < end_time 조회
payload_json에서 metric 값 추출
collector가 집계 가능한 normalized SourceRow list 반환
```

SourceAdapter는 bucket aggregation을 수행하지 않는다. 10분 bucket의 count/mean/min/max/stddev 계산은 DriftCollector 책임이다. 자세한 contract는 `source_adapter_contract.md`를 따른다.

### 6.5 DriftDetector

`app/drift/detector.py`

역할:

```text
source_method_assignment 조회
method_state 조회
lookback bucket 조회
runtime_registry에서 drift method 함수 선택
method_run 저장
method_state 갱신
warning/drift면 drift_event 저장
```

```python
class DriftDetector:
    def run_for_new_bucket(self, source_id: str, adapter_id: str, feature_id: str, bucket_end):
        ...
```

### 6.6 Runtime Registry

`app/drift/runtime_registry.py`

역할:

```text
algorithm_implementation_id 또는 runtime_method_key로 runtime wrapper를 찾는다.
runtime wrapper는 drift_algorithm_impl의 기존 알고리즘 구현을 호출하고, Drift Server 표준 input/output contract로 변환한다.
```

초기 registry:

```python
RUNTIME_METHODS = {
    "adwin_mean_stream": run_adwin_mean_stream,
}
```

함수 signature:

```python
def run_adwin_mean_stream(input: dict) -> dict:
    return {
        "runStatus": "success",
        "level": "normal" | "warning" | "drift",
        "score": 0.0,
        "event": None,
        "nextState": {},
        "metrics": {},
        "diagnostics": {},
        "payloadHints": {}
    }
```

runtime function은 `drift_method_runtime_contract.md`의 input/output contract를 따른다. DB 조회/저장, HTTP 호출, event insert는 runtime function에서 수행하지 않는다.

주의:

```text
run_adwin_mean_stream은 ADWIN 알고리즘 자체를 새로 구현하는 함수가 아니다.
drift_algorithm_impl의 기존 ADWIN 구현을 호출하는 adapter/wrapper다.
```

### 6.7 Payload Registry

`app/drift/payload_registry.py`

역할:

```text
payload_adapter_key로 chart payload 변환 함수를 찾는다.
```

초기 registry:

```python
PAYLOAD_ADAPTERS = {
    "adwin_mean_stream_to_chart_stream_001": build_payload,
}
```

함수 signature:

```python
def build_payload(context: ChartPayloadContext) -> dict:
    ...
```

`ChartPayloadContext`:

```text
source
adapter
assignment
method_run
drift_event
metric_buckets
analysis_chart_registration
chart_definition
```

payload adapter는 `analysis_payload_adapter_contract.md`를 따른다. DB 조회/저장, HTTP 호출, chart definition 수정은 payload adapter에서 수행하지 않는다. DriftService가 context를 구성하고, payload adapter는 chart runtime payload만 반환한다.

## 7. Test Feeder Server 내부 구현

Test Feeder Server는 테스트 source를 흉내낸다.

### 7.1 Router

`app/feeder/router.py`

담당 endpoint:

```text
GET  /api/test-feeder/health
POST /api/test-feeder/feeders
POST /api/test-feeder/feeders/{source_id}/start
POST /api/test-feeder/feeders/{source_id}/stop
GET  /api/test-feeder/feeders/{source_id}/status
POST /api/test-feeder/feeders/{source_id}/tick
POST /api/test-feeder/reset
```

### 7.2 FeederService

`app/feeder/service.py`

역할:

```text
feed_state 등록
CSV cursor 관리
Harness logicalNow 기준 row insert
start/stop status 관리
reset 처리
```

주요 method:

```python
class FeederService:
    def register_feeder(...)
    def start(source_id: str)
    def stop(source_id: str)
    def tick(source_id: str, logical_now, previous_logical_now, tick_interval_minutes: int)
    def reset(source_id: str | None)
    def status(source_id: str)
```

### 7.3 CsvReader

`app/feeder/csv_reader.py`

역할:

```text
data.csv.gz 읽기
event_time 기준 row 선택
payload_json 생성
```

초기 구현은 CASE-010 하나를 명확히 지원한다.

```text
CSV row
  -> event_time
  -> payload_json.metric
```

이후 다른 CASE를 추가할 때 dataset별 mapper를 늘린다.

## 8. Chart Definition Artifact 연동 구현

이 control plane은 Chart Builder 서버를 직접 호출하지 않는다. chart definition은 등록 요청의 snapshot 또는 사전 생성 artifact로 취급한다.

### 8.1 Artifact Sources

기준 artifact:

```text
analysis_chart_registration.chart_definition_json
chart_runtime/payloads/runtime_chart_payloads.json
drift 보고서/charts/method_data.js
```

AdminService에서 사용한다.

```text
AdminService.create_analysis_chart()
  -> chart definition snapshot 준비
  -> Drift Server analysis chart registration API 호출
```

Admin Server의 `GET /api/admin/report/gallery-data`는 chart gallery 선택 데이터를 제공한다. `REPORT_GALLERY_BASE_URL`이 설정되어 있으면 선택적 기존 report gallery server의 `/api/gallery-data`를 먼저 조회하고, 비어 있거나 실패하면 `drift 보고서/charts/method_data.js`를 읽어 fallback catalog를 만든다. 8765 report gallery server는 필수 runtime dependency가 아니며 전체 실행 스크립트가 시작하지 않는다.

## 9. LLM Interpretation Server 연동 구현

LLM Interpretation Server는 이미 `llm_interpretation_server/`로 분리되어 있다.

### 9.1 LlmInterpretationClient

`app/clients/llm_interpretation_client.py`

```python
class LlmInterpretationClient:
    def create_chart_job(self, chart_id: str, chart_definition: dict, chart_payload: dict, context: dict) -> dict:
        ...

    def get_chart_job(self, job_id: str) -> dict:
        ...
```

책임:

```text
기존 LLM interpretation server 응답을 내부 표준 구조로 normalize
HTTP status 확인
downstream 오류를 표준 error로 변환
timeout 처리
```

이 client는 UI server 또는 drift server가 직접 사용할 수 있다. 다만 drift server의 핵심 책임은 payload 생성까지이고, LLM 해석 생성은 LLM server의 책임이다.

## 10. Drift Report Catalog 연동

`drift 보고서` DB는 drift method와 chart catalog의 source of truth다.

### 10.1 DriftReportCatalogClient

`app/clients/drift_report_catalog_client.py`

역할:

```text
실행 가능한 drift method 목록 조회
method/variant에 연결 가능한 chart 목록 조회
chart/component/guide metadata 조회
```

주요 method:

```python
class DriftReportCatalogClient:
    def list_executable_methods(self) -> list[dict]:
        ...

    def list_charts_for_method(self, method_variant_id: int) -> list[dict]:
        ...

    def get_chart_metadata(self, chart_id: str) -> dict:
        ...
```

조회 기준:

```text
drift_method
method_variant
algorithm_variant
algorithm_implementation
variant_chart
chart_definition
chart_component_usage
```

## 11. Repository 설계

Repository는 SQL을 캡슐화한다.

### 11.1 SourceRepository

```python
class SourceRepository:
    def create_source(...)
    def update_source(...)
    def delete_source(...)
    def get_source(source_id: str)
    def list_sources(...)
```

### 11.2 AdapterRepository

```python
class AdapterRepository:
    def create_adapter(...)
    def get_adapter(adapter_id: str)
    def list_adapters(source_id: str | None)
    def update_status(adapter_id: str, status: str)
    def get_state(adapter_id: str)
    def update_state(...)
```

### 11.3 FeatureRepository

```python
class FeatureRepository:
    def create_feature(...)
    def upsert_feature(...)
    def list_features(source_id: str)
    def get_feature(source_id: str, feature_id: str)
    def set_enabled(source_id: str, feature_id: str, enabled: bool)
```

### 11.4 BucketRepository

```python
class BucketRepository:
    def insert_bucket(...)
    def list_buckets(source_id: str, feature_id: str, from_time, to_time)
    def list_recent_buckets(source_id: str, feature_id: str, until_time, limit: int)
    def count_buckets(adapter_id: str)
```

### 11.5 MethodRepository

```python
class MethodRepository:
    def create_assignment(...)
    def list_assignments(source_id: str)
    def list_enabled_assignments(source_id: str, adapter_id: str, feature_id: str)
    def get_method_state(assignment_id: str)
    def upsert_method_state(...)
    def insert_method_run(...)
    def get_method_run(method_run_id: str)
```

### 11.6 EventRepository

```python
class EventRepository:
    def create_event(...)
    def get_event(event_id: str)
    def list_events(source_id: str, from_time, to_time)
    def count_events(source_id: str)
```

### 11.7 AnalysisChartRepository

```python
class AnalysisChartRepository:
    def create_registration(...)
    def list_for_assignment(assignment_id: str)
    def list_for_event(event_id: str)
    def get_registration(analysis_chart_id: str)
    def update_chart_definition_snapshot(analysis_chart_id: str, chart_definition: dict)
    def get_payload_adapter(payload_adapter_key: str)
```

### 11.8 Test Feeder Server Repositories

```python
class RawEventRepository:
    def insert_raw_event(...)
    def list_raw_events(source_id: str, start_time, end_time)
    def reset_source(source_id: str)

class FeedStateRepository:
    def get_feed_state(source_id: str)
    def update_feed_state(...)
```

## 12. Scheduler 설계

### 12.1 RealScheduler

브라우저 데모 또는 운영 모드에서 사용한다.

```text
feeder interval = 1초 in test demo
collector interval = 10초 in test demo
collector interval = 10분 in production
```

```python
class RealScheduler:
    def start_feeder(source_id: str)
    def stop_feeder(source_id: str)
    def start_adapter(adapter_id: str)
    def stop_adapter(adapter_id: str)
```

### 12.2 HarnessTickDispatcher

자동 테스트에서 사용한다.

```python
class HarnessTickDispatcher:
    def tick(self, logical_now, previous_logical_now, tick_interval_minutes: int, run_collector_on_boundary: bool):
        ...
```

처리:

```text
Harness가 전달한 logicalNow를 clock에 설정
FeederService.tick(logicalNow) 호출
10분 logicalNow 경계면 DriftCollector.poll_once 호출
```

이 dispatcher는 Harness 내부 TimeDispatcher 또는 서버 단위 테스트에서 쓰는 실행 모델이다. Admin Server가 서버 간 tick을 중계하는 모델이 아니다.

## 13. 초기 Vertical Slice 구현 순서

### 13.1 1단계: DB와 repository

```text
shared/dev_db.py
drift_control_plane/drift_server/migrations/001_init_drift_server.sql
SourceRepository
AdapterRepository
FeatureRepository
BucketRepository
MethodRepository
EventRepository
AnalysisChartRepository

test_feeder_server/migrations/001_init_test_source.sql
RawEventRepository
FeedStateRepository
```

### 13.2 2단계: 테스트 feeder

```text
CASE-010 CSV reader
FeederService.register_feeder
FeederService.tick
test_source.raw_event insert
```

### 13.3 3단계: adapter와 collector

```text
test_db_numeric_stream adapter
DriftCollector.poll_once
10분 bucket aggregation
adapter_state.source_cursor_time update
```

### 13.4 4단계: drift method 실행

```text
drift_algorithm_impl 기존 ADWIN 구현 확인
adwin_mean_stream wrapper
RuntimeRegistry
DriftDetector
method_run 저장
drift_event 저장
```

Drift Server 안에 CASE-010 검증용 임시 ADWIN 구현을 새로 두지 않는다. 기존 `drift_algorithm_impl` 구현을 호출하고, 필요한 차이는 wrapper에서 입력/출력 contract 변환으로 해결한다.

### 13.5 5단계: analysis chart payload

```text
analysis_chart_registration 저장
chart_definition_json snapshot 저장
adwin_mean_stream_to_chart_stream_001 payload adapter
DriftService.build_event_analysis
```

### 13.6 6단계: API endpoint

```text
Admin router 최소 API
Drift router 최소 API
Feeder router 최소 API
```

### 13.7 7단계: end-to-end test

```text
test_case010_vertical_slice.py
  reset
  register source
  register adapter
  register assignment
  register analysis chart
  HarnessClock logicalNow를 60분 구간까지 전진
  assert bucket count
  assert method_run count
  assert drift_event count
  assert event analysis payload
```

## 14. 실패 처리

### 14.1 Feeder 오류

```text
CSV 파일 없음
CSV row parse 실패
DB insert 실패
```

처리:

```text
feed_state.feed_status = error
feed_state.last_error 저장
Admin status에서 노출
```

### 14.2 Adapter 오류

```text
source DB 연결 실패
window 조회 실패
payload 값 추출 실패
```

처리:

```text
adapter_state.last_error 저장
source_cursor_time은 성공한 window 이후로만 전진
```

### 14.3 Drift Method 오류

```text
method_run.run_status = error
method_run.error_message 저장
drift_event는 생성하지 않음
```

### 14.4 Payload Adapter 오류

```text
event analysis API는 ok=false 반환
error.code = PAYLOAD_ADAPTER_ERROR
event와 method_run 원본은 보존
```

## 15. 테스트 전략

| 테스트 | 범위 |
| --- | --- |
| repository test | 각 repository CRUD와 query 검증 |
| feeder test | CASE-010 CSV에서 Harness logicalNow 기준 row insert 검증 |
| collector test | 10분 window 하나만 처리하는 규칙 검증 |
| catch-up test | 누락 window를 10분 단위로 순차 처리하는지 검증 |
| detector test | assignment 조회, method_run 저장, event 생성 검증 |
| payload adapter test | ADWIN event를 CHART-STREAM-001 payload로 변환 검증 |
| API test | 핵심 endpoint 응답 contract 검증 |
| vertical slice test | CASE-010 end-to-end 검증 |

## 16. 구현 시 주의점

1. AdminService에 데이터 처리 로직을 넣지 않는다.
2. endpoint에서 SQL을 직접 실행하지 않는다.
3. `payload_adapter_key` 없이 analysis chart를 등록하지 않는다.
4. `poll_once`에서 10분 window를 두 개 이상 처리하지 않는다.
5. catch-up은 명시적으로 호출된 경우에만 여러 window를 처리한다.
6. drift method와 chart catalog는 `drift 보고서` DB를 기준으로 한다.
7. 자동 테스트에서는 sleep을 사용하지 않는다.
8. 첫 구현은 CASE-010 vertical slice를 통과시키는 데 집중한다.
