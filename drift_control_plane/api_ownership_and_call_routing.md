# API Ownership and Call Routing

## 1. 목적

이 문서는 v1 구현에서 API 호출 방향과 저장 책임을 고정한다.

Endpoint 목록과 request/response schema의 source of truth는 `api_contracts.md`다. 이 문서는 endpoint를 다시 나열하지 않고, 누가 누구를 호출하고 어느 서버가 상태를 저장하는지만 정의한다.

## 2. 핵심 결정

```text
Admin Server는 사용자-facing control API를 제공한다.
실제 상태 저장과 실행은 소유 서버 API가 수행한다.
Admin Server는 orchestration만 한다.
```

관리 화면에서 호출하는 API는 Admin Server에 모은다. 단, Admin Server는 `drift_server` 또는 `test_source` schema를 직접 수정하지 않는다.

기본 흐름:

```text
Admin UI
  -> Admin Server API
  -> Admin Service orchestration
  -> 소유 서버 API 호출
  -> 소유 서버가 자기 DB/schema에 저장
```

## 3. Source of Truth

| 관심사 | 기준 문서 |
| --- | --- |
| Endpoint 목록, request/response schema | `api_contracts.md` |
| API caller/owner/downstream 방향 | 이 문서 |
| 사용자 시나리오별 호출 순서 | `server_interaction_scenarios.md` |
| 서버 경계 원칙과 금지 사항 | `server_boundary_policy.md` |
| DB/schema read/write 권한 | `database_ownership_policy.md` |

## 4. 서버별 책임

| 서버 | API 역할 | DB write owner |
| --- | --- | --- |
| Admin Server | 관리자 화면용 control API, orchestration | v1에서는 없음 |
| Drift Server | source/adapter/method/chart 등록 저장, bucket/event/timeseries/analysis API | `drift_server` schema |
| Test Feeder Server | feeder 등록/start/stop/tick/reset | `test_source` schema |
| LLM Interpretation Server | interpretation job 생성/조회 | LLM interpretation storage |
| drift_metric_timeseries UI | Drift Server read API 호출 | DB write 없음 |

## 5. 허용 호출 방향

```text
Admin UI -> Admin Server

Admin Server -> Drift Server
Admin Server -> Test Feeder Server
Admin Server -> LLM Interpretation Server

drift_metric_timeseries UI -> Drift Server
drift_metric_timeseries UI -> LLM Interpretation Server

Drift Server -> LLM Interpretation Server
```

Chart Builder는 이 control plane의 직접 downstream이 아니다. v1 기본 흐름은 registration 시점에 전달된 chart definition snapshot을 Drift Server에 저장하고, event analysis 조회 시 그 snapshot과 `chart_runtime` payload template/catalog artifact를 사용한다.

선택적 기존 Report Gallery Server(`REPORT_GALLERY_BASE_URL`, 기본 `http://127.0.0.1:8765`)는 Admin Server의 chart gallery catalog 조회 보조 소스일 뿐이다. 해당 서버가 없으면 Admin Server는 `drift 보고서/charts/method_data.js` fallback을 사용하며, 8765는 필수 호출 방향이나 전체 실행 topology에 포함하지 않는다.

## 6. 금지 호출/접근

```text
Admin Server -> drift_server DB direct write
Admin Server -> test_source DB direct write
Admin Server -> drift_event direct insert
Admin Server -> metric_bucket direct delete

Test Feeder Server -> Drift Server
Test Feeder Server -> drift_server DB

LLM Interpretation Server -> drift_server DB
UI -> DB direct access
```

## 7. 주요 Routing

### 7.1 Source/Adapter/Method 등록

```text
Admin UI
  -> Admin Server
  -> Drift Server
  -> drift_server schema 저장
```

Source 수정/삭제 API는 후속 contract이며 v1 구현 범위에서는 제외한다.

### 7.2 Test Feeder 제어

```text
Admin UI 또는 test harness
  -> Admin Server
  -> Test Feeder Server
  -> test_source schema 저장/초기화
```

Test Feeder Server는 Drift Server를 호출하지 않는다.

### 7.3 Reset

```text
Admin UI
  -> Admin Server
  -> Test Feeder Server reset
  -> Drift Server reset
```

Admin Server가 직접 DB delete를 실행하지 않는다.

권장 순서:

```text
1. feeder stop
2. adapter stop
3. Test Feeder reset
4. Drift Server reset
5. status 확인
```

### 7.4 Tick

```text
Admin UI/test harness
  -> Admin Server
  -> Test Feeder Server tick
  -> Drift Server poll-once
     단, 10분 경계에 도달했거나 명시적으로 runCollector=true인 경우
```

Test Feeder tick은 source DB에 raw event를 넣는다. Drift poll은 source DB에서 10분 window를 읽어 bucket/method_run/event를 만든다.

### 7.5 Analysis Chart Registration

```text
Admin UI
  -> Admin Server
  -> Drift Server analysis chart registration 저장
```

Drift Server가 저장하는 것:

```text
analysis_chart_registration.chart_definition_id
analysis_chart_registration.chart_definition_json
analysis_chart_registration.payload_adapter_key
```

Admin Server는 chart registration row를 직접 insert하지 않는다.
Admin Server는 Chart Builder 서버를 직접 호출하지 않는다. 필요한 chart definition은 요청 payload의 snapshot 또는 사전 생성된 artifact를 통해 전달한다.

### 7.6 Catalog 조회

v1에서는 Admin Server가 catalog read client를 통해 drift report catalog를 조회한다. 직접 DB write는 금지한다.

Admin UI의 report gallery catalog는 `GET /api/admin/report/gallery-data`를 통해 조회한다. 이 Admin endpoint는 선택적 `REPORT_GALLERY_BASE_URL` 조회가 실패하면 `drift 보고서/charts/method_data.js`를 읽어 동일한 gallery 선택 흐름을 유지한다.

후속으로 별도 Catalog API가 생기면 Admin Server는 그 API를 호출하도록 바꿀 수 있다.

## 8. 구현 체크리스트

```text
Admin endpoint에는 DB write repository를 두지 않는다.
Admin service는 downstream client class만 사용한다.
Drift control API와 UI read API prefix를 분리한다.
Test Feeder API는 Drift Server를 모른다.
Endpoint 목록과 payload schema는 api_contracts.md만 보고 구현한다.
reset/tick/chart registration은 이 문서의 routing 순서를 따른다.
```

## 9. 관련 문서

- `api_contracts.md`
- `server_boundary_policy.md`
- `server_interaction_scenarios.md`
- `database_ownership_policy.md`
- `reset_policy.md`
- `test_harness_architecture.md`
