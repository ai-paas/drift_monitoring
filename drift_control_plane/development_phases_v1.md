# Drift Server Development Phases v1

## 1. 목적

이 문서는 v1 구현을 작은 단계로 나누어 정리한다.

v1의 최종 목표는 `CASE-010` 하나를 end-to-end로 실행하고 검증하는 것이다.

```text
CASE-010
  -> Test Feeder
  -> test_source DB
  -> Drift Server bucket
  -> drift_algorithm_impl ADWIN wrapper
  -> drift_event
  -> timeseries UI
  -> analysis chart payload
  -> LLM interpretation
  -> test harness 검증
```

## 2. 단계 목록

| Phase | 이름 | 목적 |
| --- | --- | --- |
| V1-00 | 문서/요구사항 기준 고정 | 구현 기준 문서와 source of truth 확정 |
| V1-01 | 서버 scaffold + health | Admin/Drift/Test Feeder 서버 분리 실행 |
| V1-02 | DB bootstrap + migration | v1 schema/table 생성 |
| V1-03 | 기본 control API | source/adapter/method/chart/reset API skeleton |
| V1-04 | Test Feeder CSV replay | CASE-010 CSV를 logical time 기준으로 적재 |
| V1-05 | Drift adapter + collector + bucket | 10분 window 수집과 bucket 저장 |
| V1-06 | Drift method wrapper + event | 기존 `drift_algorithm_impl` 호출과 event 생성 |
| V1-07 | Timeseries API + UI 연결 | timeseries-data/live API와 UI 표시 |
| V1-08 | Analysis chart payload | CHART-STREAM-001 registration/payload |
| V1-09 | LLM interpretation 연동 | analysis payload 기반 LLM job 생성 |
| V1-10 | Test Harness Core | scenario runner, recorder, analyzer |
| V1-11 | PyQt6 Harness UI + Proxy modes | 관제 UI와 Mode A-D 지원 |
| V1-12 | CASE-010 E2E 검증 | 전체 end-to-end 실행과 리포트 생성 |

## 3. V1-00 문서/요구사항 기준 고정

### 목표

```text
구현자가 따라야 할 기준 문서를 확정한다.
```

### 완료 기준

```text
README에 implementation reading order가 있다.
api_contracts.md가 endpoint/payload source of truth다.
implementation_scope_v1.md가 v1 포함/제외 범위를 정의한다.
testing/test_requirements.md가 테스트 요구사항을 정의한다.
```

## 4. V1-01 서버 scaffold + health

### 목표

```text
Admin Server, Drift Server, Test Feeder Server를 별도 프로세스로 띄운다.
```

### 구현 항목

```text
admin_server/
  run_admin_server.cmd
  app/main.py

drift_server/
  run_drift_server.cmd
  app/main.py

test_feeder_server/
  run_test_feeder_server.cmd
  app/main.py
```

### 완료 기준

```text
Admin Server: http://127.0.0.1:8770/api/admin/health
Drift Server: http://127.0.0.1:8771/api/health
Test Feeder Server: http://127.0.0.1:8772/api/test-feeder/health
```

각 health API는 `{ok,data,error}` envelope를 반환한다.

## 5. V1-02 DB bootstrap + migration

### 목표

```text
v1에 필요한 schema/table을 생성한다.
```

### 구현 항목

```text
scripts/bootstrap_dev_db.ps1
scripts/bootstrap_dev_db.cmd
drift_control_plane/drift_server/migrations/001_init_drift_server.sql
test_feeder_server/migrations/001_init_test_source.sql
```

### 완료 기준

```text
drift_server schema 생성
test_source schema 생성
v1 필수 테이블 생성
bootstrap script 재실행 가능
```

## 6. V1-03 기본 control API

### 목표

Admin Server가 사용자-facing control API를 제공하고, 실제 저장은 소유 서버 API가 담당하는 구조를 만든다.

### 구현 항목

```text
source 등록/조회
adapter 등록/상태
method assignment 등록/조회
analysis chart registration skeleton
run reset skeleton
```

### 완료 기준

```text
Admin API가 Drift/Test Feeder API를 client로 호출한다.
Admin Server가 drift_server/test_source DB에 직접 write하지 않는다.
```

## 7. V1-04 Test Feeder CSV replay

### 목표

CASE-010 CSV를 logical time 기준으로 `test_source.raw_event`에 적재한다.

### 구현 항목

```text
CSV reader
FeederService.register_feeder
FeederService.tick
test_source.raw_event insert
test_source.feed_state update
```

### 완료 기준

```text
Harness Clock의 tickIntervalMinutes 기본값은 1분
tick 요청은 logicalNow를 포함한다.
source_event_time = CSV timestamp
event_time = canonical time
inserted_at = Harness logicalNow
feed_state cursor가 중복 없이 갱신된다.
```

## 8. V1-05 Drift adapter + collector + bucket

### 목표

Drift Server가 `test_source`에서 10분 window를 읽어 `metric_bucket`을 저장한다.

### 구현 항목

```text
test_db_numeric_stream SourceAdapter
DriftCollector.poll_once
10분 bucket aggregation
empty bucket 저장
adapter_state cursor 갱신
idempotency 처리
```

### 완료 기준

```text
poll_once는 window 하나만 처리한다.
같은 window를 두 번 처리해도 metric_bucket 중복이 없다.
데이터가 없으면 status=empty bucket이 저장된다.
```

## 9. V1-06 Drift method wrapper + event

### 목표

기존 `drift_algorithm_impl`의 ADWIN 구현을 wrapper로 호출하고 drift event를 생성한다.

### 구현 항목

```text
RuntimeRegistry
adwin_mean_stream wrapper
method_state 저장/복원
method_run 저장
drift_event 생성
```

### 완료 기준

```text
Drift Server는 ADWIN 알고리즘 자체를 새로 구현하지 않는다.
runtime_method_key=adwin_mean_stream으로 wrapper를 찾는다.
wrapper는 drift_method_runtime_contract.md의 input/output contract를 따른다.
drift 조건 충족 시 drift_event가 생성된다.
```

## 10. V1-07 Timeseries API + UI 연결

### 목표

drift_metric_timeseries UI가 source별 시계열과 drift event를 볼 수 있게 한다.

### 구현 항목

```text
GET /api/sources/{source_id}/timeseries-data
event marker
analysis chart link
```

후속 목표 API:

```text
GET /api/sources
GET /api/sources/{source_id}/timeseries-live
GET /api/sources/{source_id}/events/{event_id}
```

### 완료 기준

```text
timeseries-data가 full view model을 반환한다.
UI live 동작은 timeseries-data 반복 조회로 최신 bucket/event를 확인한다.
UI가 event marker와 analysis chart link를 표시한다.
```

## 11. V1-08 Analysis chart payload

### 목표

drift event에 대해 CHART-STREAM-001 analysis payload를 생성한다.

### 구현 항목

```text
analysis_chart_registration
chart_definition_id 저장
chart_definition_json snapshot 저장
payload_adapter_key 저장
adwin_mean_stream_to_chart_stream_001 payload adapter
event analysis API
```

### 완료 기준

```text
event analysis API가 chartDefinition과 chartPayload를 반환한다.
chart payload는 JSON snapshot test가 가능하다.
payload adapter는 DB/HTTP에 직접 접근하지 않는다.
```

## 12. V1-09 LLM interpretation 연동

### 목표

analysis payload를 LLM Interpretation Server로 보내 해석 job을 생성한다.

### 구현 항목

```text
LLM Interpretation client
POST /api/interpret/chart/jobs
GET /api/interpret/chart/jobs/{job_id}
LLM request/response artifact 저장
```

### 완료 기준

```text
analysis payload 기반 job 생성 가능
job status/result 조회 가능
테스트 하네스가 LLM request/response를 저장한다.
```

## 13. V1-10 Test Harness Core

### 목표

headless로 실행 가능한 테스트 엔진을 만든다.

### 구현 항목

```text
scenario runner
server controller
API client
Harness Proxy
artifact recorder
contract validator
analyzer
```

### 완료 기준

```text
PyQt6 UI 없이 scenario 실행 가능
runs/{run_id} artifact 저장
index.jsonl append
validation_report.json 생성
summary.md 생성
```

## 14. V1-11 PyQt6 Harness UI + Proxy modes

### 목표

테스트 진행 상황과 artifact를 확인할 수 있는 관제 UI를 만든다.

### 구현 항목

```text
서버 start/stop/status
scenario 선택/실행/중지
logical time tick
API call timeline
request/response viewer
event/payload/chart state/LLM result viewer
Mode A Direct
Mode B Proxy Record
Mode C Stub
Mode D Fault Injection
```

### 완료 기준

```text
PyQt6 UI가 Harness Core를 조작한다.
Mode A-D를 선택해 실행할 수 있다.
과거 run artifact를 조회할 수 있다.
```

## 15. V1-12 CASE-010 E2E 검증

### 목표

CASE-010을 end-to-end로 실행하고 자동 검증한다.

### 완료 기준

```text
Test Feeder가 logical time으로 데이터를 넣는다.
Drift Server가 bucket을 만든다.
drift_algorithm_impl ADWIN wrapper가 실행된다.
drift_event가 생성된다.
timeseries UI state가 검증된다.
analysis chart payload가 검증된다.
chart runtime state가 검증된다.
LLM interpretation job이 생성된다.
validation_report.json과 summary.md가 생성된다.
```

## 16. 단계별 산출물

| Phase | 주요 산출물 |
| --- | --- |
| V1-01 | server folders, run scripts, health APIs |
| V1-02 | bootstrap scripts, migration SQL |
| V1-03 | control API routers/clients |
| V1-04 | Test Feeder service/repository |
| V1-05 | SourceAdapter, collector, bucket repository |
| V1-06 | RuntimeRegistry, ADWIN wrapper, event creation |
| V1-07 | timeseries API, UI integration |
| V1-08 | payload adapter, analysis API |
| V1-09 | LLM client, job artifact |
| V1-10 | headless Harness Core, run artifacts |
| V1-11 | PyQt6 Harness UI, proxy modes |
| V1-12 | CASE-010 validation report |

## 17. 구현 순서 원칙

```text
각 phase는 독립적으로 검증 가능해야 한다.
phase를 건너뛰어 다음 phase를 구현하지 않는다.
테스트 인프라 V1-10/V1-11은 본 시스템 기능과 분리해 구현한다.
drift 알고리즘은 새로 구현하지 않고 drift_algorithm_impl을 호출한다.
```
