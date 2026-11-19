# Drift Monitoring Database Ownership Policy

## 1. 목적

이 문서는 서버별 DB/schema 소유권과 접근 권한을 정의한다.

핵심 결정:

```text
각 서버는 자기 책임의 schema만 write한다.
서버 간 상태 변경은 DB 직접 접근이 아니라 API를 통해 수행한다.
```

## 2. Schema / Storage 목록

```text
drift_server schema
  Drift Server가 소유하는 source, adapter, bucket, method_run, drift_event, analysis chart 저장소

test_source schema
  Test Feeder Server가 소유하는 테스트 raw event/feed state 저장소

drift 보고서 DB/schema
  drift method, algorithm variant, chart catalog, guide source of truth

LLM guide/catalog DB
  LLM interpretation guide/context 저장소
```

현재 v1 dev runtime은 `drift_control_plane/runtime/sprint2_dev.sqlite3` SQLite DB를 사용한다. 아래 이름은 물리 schema가 아니라 논리 소유권 group이다.

```text
drift_server
test_source
drift_report
llm_interpretation
```

SQLite dev DB에는 서버별 DB user 권한 분리가 없다. 코드 구조는 논리 소유권과 read/write 경계 분리를 전제로 작성한다.

상세 물리 구성은 `database_physical_topology.md`를 따른다.

## 3. 서버별 권한 요약

| Server | drift_server schema | test_source schema | drift 보고서 DB | LLM guide DB |
| --- | --- | --- | --- | --- |
| Admin Server | API only | API only | read 또는 Catalog API | no direct |
| Drift Server | read/write owner | read via SourceAdapter | read | no direct |
| Test Feeder Server | no direct | read/write owner | no direct | no direct |
| LLM Interpretation Server | no direct | no direct | read as guide/catalog context | read owner |
| drift_metric_timeseries UI | API only | no direct | no direct | API only |

## 4. Admin Server

Admin Server는 control plane이다.

허용:

```text
Drift Server API 호출
Test Feeder Server API 호출
LLM Server health/status API 호출
drift 보고서 DB read 또는 Catalog API 조회
```

금지:

```text
drift_server schema 직접 write
test_source schema 직접 write
drift_event 직접 생성
metric_bucket 직접 삭제
feed_state 직접 수정
```

Admin Server가 별도 admin 설정 DB를 갖는 것은 허용한다. 예:

```text
admin user/session
UI preference
server registry
```

v1에서는 별도 admin DB 없이 각 서버 API를 orchestration해도 된다.

## 5. Drift Server

Drift Server는 `drift_server` schema owner다.

허용:

```text
drift_server schema read/write
test_source schema read via SourceAdapter
drift 보고서 DB read
chart definition snapshot read/write in drift_server schema
```

금지:

```text
test_source schema write
CSV 직접 읽기
LLM guide DB 직접 write
```

Drift Server가 `test_source`를 읽는 것은 외부 source adapter가 source DB를 읽는 것과 같은 의미다.

## 6. Test Feeder Server

Test Feeder Server는 `test_source` schema owner다.

허용:

```text
test_source.raw_event read/write
test_source.feed_state read/write
테스트 CSV read
```

금지:

```text
drift_server schema read/write
drift 보고서 DB direct access
LLM guide DB direct access
```

Test Feeder는 drift detection을 알지 못한다. 단지 source DB에 raw event를 쌓는다.

## 7. Chart Definition Artifact

이 control plane은 Chart Builder 서버나 chart_builder storage를 직접 사용하지 않는다.

허용:

```text
Drift Server가 analysis_chart_registration.chart_definition_json snapshot 저장
payload adapter가 chart_runtime payload template artifact read
Admin Server가 drift 보고서 chart catalog artifact read
```

금지:

```text
Admin/Drift Server -> chart_builder storage direct access
Admin/Drift Server -> Chart Builder Server direct call
```

v1에서 chart definition 원본은 사전 생성된 artifact 또는 등록 요청의 snapshot으로 취급한다.

## 8. LLM Interpretation Server

LLM Interpretation Server는 chart/component 해석을 담당한다.

허용:

```text
LLM guide/catalog DB read
drift 보고서 DB read as guide/context source
```

금지:

```text
drift_server schema direct access
test_source schema direct access
drift calculation
event creation
```

LLM Server는 chart payload를 입력으로 받아 해석만 생성한다.

## 9. UI

`drift_metric_timeseries` UI는 DB에 직접 접근하지 않는다.

허용:

```text
Drift Server API
LLM Interpretation Server API
```

금지:

```text
DB direct access
test_source direct access
drift 보고서 DB direct access
```

## 10. DB 연결 권장

현재 v1 dev runtime은 SQLite file path를 사용한다.

예:

```text
drift_control_plane/runtime/sprint2_dev.sqlite3
```

후속 PostgreSQL 전환 또는 운영 통합 테스트에서는 서버별 DB user를 분리하는 것이 좋다. 그 경우 `DRIFT_SERVER_DATABASE_URL`, `TEST_FEEDER_DATABASE_URL`, `ADMIN_DATABASE_URL`, `LLM_INTERPRETATION_DATABASE_URL` 같은 connection string 정책을 다시 적용한다.

## 11. Reset과 권한

Admin Server는 reset을 orchestration한다.

```text
Admin Server
  -> Test Feeder Server reset API
  -> Drift Server reset API
```

Admin Server가 직접 `delete from drift_server.metric_bucket` 또는 `delete from test_source.raw_event`를 수행하지 않는다.

## 12. 관련 문서

```text
database_physical_topology.md
server_boundary_policy.md
reset_policy.md
data_source_event_schema.md
test_feeder_contract.md
source_adapter_contract.md
```
