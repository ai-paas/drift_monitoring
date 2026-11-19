# Drift Server Design Review Issues

## 1. 목적

이 문서는 현재 `drift_server` 설계 문서들을 검토하면서 드러난 이슈를 추적하기 위한 목록이다.

지금 당장 설계를 모두 수정하지 않고, 이후 구현 또는 추가 설계 단계에서 하나씩 검토한다.

상태 값:

```text
open       아직 검토/수정하지 않음
accepted   수정하기로 결정함
deferred   후속 단계로 미룸
closed     반영 완료
rejected   수정하지 않기로 결정함
```

심각도:

```text
high    구현 전에 정리하지 않으면 구조가 흔들릴 가능성이 큼
medium  구현 중 혼선을 만들 수 있음
low     문서 정합성 또는 후속 개선 사항
```

## 2. 이슈 목록

| ID | 심각도 | 상태 | 이슈 | 영향 |
| --- | --- | --- | --- | --- |
| DRI-001 | high | accepted | 서버 분리 수준이 문서마다 다름 | 처음부터 서버를 분리하는 방향으로 결정 |
| DRI-002 | high | accepted | DB schema 문서 간 `data_source`와 `source_adapter` 관계가 다름 | `data_source 1:N source_adapter`로 결정 |
| DRI-003 | medium | accepted | `source_method_assignment`가 문서마다 `runtime_method_id` 또는 `method_variant_id` 중심으로 다름 | `method_variant_id + algorithm_implementation_id + runtime_method_key`로 통일 |
| DRI-004 | medium | accepted | API 공통 응답 envelope와 기존 LLM server 응답 형식이 다름 | 신규 서버는 `{ok,data,error}`, 기존 서버 응답은 client normalize로 결정 |
| DRI-005 | medium | accepted | 1차 구현 범위에 과한 기능이 섞여 있음 | `implementation_scope_v1.md`로 CASE-010 vertical slice 범위 확정 |
| DRI-006 | high | accepted | `source_feature` 테이블이 없음 | `source_feature` 테이블을 추가하는 방향으로 결정 |
| DRI-007 | high | accepted | streaming drift method의 detector state 저장 구조가 없음 | `method_state` 테이블을 추가하는 방향으로 결정 |
| DRI-008 | high | accepted | 시간/커서 모델 정의가 부족함 | `time_and_cursor_model.md`로 정의하고 빈 window는 empty bucket 저장으로 결정 |
| DRI-009 | high | accepted | collector 동시 실행/중복 실행 방지 정책이 없음 | `idempotency_and_locking.md`로 lock/idempotency 정책 정의 |
| DRI-010 | medium | accepted | chart definition 저장 위치가 불명확함 | `chart_definition_id`와 `chart_definition_json` snapshot을 함께 저장하기로 결정 |
| DRI-011 | medium | accepted | 테스트 reset 정책이 넓고 불명확함 | `reset_policy.md`로 run/source/hard reset 정책 정의 |
| DRI-012 | low | deferred | README에 human verification workflow가 현재 범위 밖인데 포함되어 있음 | v1 범위에서 제외하고 future scope로 이동 |
| DRI-013 | medium | accepted | Test Feeder Server를 별도 서버로 볼지 내부 모듈로 볼지 불명확함 | 별도 서버로 두고 Admin Server가 테스트 모드에서 제어하는 방향으로 결정 |
| DRI-014 | medium | accepted | Chart Builder Server API 범위가 과할 수 있음 | v1 control plane에서는 Chart Builder 서버를 직접 호출하지 않고 chart definition artifact/snapshot을 사용 |
| DRI-015 | medium | accepted | internal HTTP API와 service class 직접 호출 방식이 혼재됨 | v1에서는 서버 간 정식 API/client 사용, `/api/internal/...` 제외로 결정 |
| DRI-016 | medium | deferred | 추천 chart payload의 실제 metric 기반 보정 검증 데이터가 부족함 | CHART-ERR-005처럼 template 고정값이 실제 분석 chart에 남는 문제를 막기 위해 10개 유형의 추천 테스트 데이터로 payload config, summary, axis, marker를 검증해야 함 |

## 3. 상세 이슈

### DRI-001 서버 분리 수준 불일치

현재 문서에는 다음 두 방향이 함께 존재한다.

```text
방향 A:
  Admin Server, Drift Server, Test Feeder Server, LLM Interpretation Server를 각각 서버처럼 표현

방향 B:
  1차 구현은 drift_server 단일 프로세스 안에 admin/feeder/drift service module을 둠
```

결정:

```text
처음부터 서버를 분리한다.

Admin Server:
  control plane

Drift Server:
  data plane. collection, bucket, detector, event, timeseries, analysis payload 담당

Test Feeder Server:
  테스트/데모용 외부 source simulator

LLM Interpretation Server:
  chart/component 해석
```

관련 문서:

```text
api_contracts.md
server_interaction_scenarios.md
internal_implementation_design.md
test_harness_architecture.md
```

### DRI-002 `data_source` / `source_adapter` 관계 불일치

`drift_server_ui_and_api.md`에는 `data_source` 안에 `adapter_id`가 들어간 예가 있고, `data_source_event_schema.md`는 `data_source 1:N source_adapter` 구조다.

결정:

```text
data_source에는 adapter_id를 두지 않는다.
source_adapter가 source_id를 가진다.
하나의 source에 여러 adapter를 허용한다.
```

### DRI-003 `source_method_assignment` key 불일치

문서에 따라 다음 표현이 섞여 있다.

```text
runtime_method_id
method_variant_id
algorithm_implementation_id
runtime_method_key
```

결정:

```text
source_method_assignment:
  method_variant_id
  algorithm_implementation_id
  runtime_method_key

runtime_method_id는 1차 구현에서 사용하지 않는다.
drift_method_runtime 테이블도 1차 구현에서 만들지 않는다.
실행 함수는 drift server 코드의 runtime registry에서 runtime_method_key로 찾는다.
```

### DRI-004 API 응답 envelope 불일치

신규 API 문서는 `{ok,data,error}` envelope를 권장하지만, 기존 LLM interpretation server는 다른 health 응답을 사용한다.

결정:

```text
신규 drift_server API:
  {ok,data,error} 사용

기존 llm_interpretation_server:
  기존 응답 유지
  client에서 adapter layer로 흡수

신규 Admin/Drift/Test Feeder API:
  {ok,data,error} 사용
```

### DRI-005 1차 구현 범위 과다

현재 문서에는 1차 구현에 꼭 필요하지 않은 항목이 섞여 있다.

후속 후보:

```text
source DELETE/PUT 전체 구현
별도 Test Feeder Server
Chart Builder Server 직접 연동
internal HTTP API 전체
human verification workflow
여러 analysis chart 동시 등록
```

결정:

```text
1차 구현은 CASE-010 + ADWIN_MEAN_STREAM + CHART-STREAM-001 vertical slice에 필요한 것만 구현한다.
```

상세 포함/제외 범위와 acceptance criteria는 `implementation_scope_v1.md`에 둔다.

### DRI-006 `source_feature` 테이블 누락

현재 assignment와 UI는 `feature_id`를 사용하지만 feature metadata 저장 테이블이 없다.

결정:

```sql
drift_server.source_feature
  source_id text
  feature_id text
  feature_label text
  value_type text
  unit text
  payload_path text
  enabled boolean
  created_at timestamptz
  updated_at timestamptz
```

검토 포인트:

```text
feature를 source 등록 시 수동 등록할지
adapter가 최초 수집 시 자동 발견할지
테스트 데이터 CASE별 feature mapping을 어디에 둘지
```

### DRI-007 detector state 저장 구조 누락

ADWIN 같은 streaming drift detector는 내부 상태가 중요하다.

결정:

```sql
drift_server.method_state
  assignment_id text primary key
  source_id text
  adapter_id text
  feature_id text
  state_json jsonb
  last_bucket_end timestamptz
  updated_at timestamptz
```

검토 포인트:

```text
상태형 detector와 lookback 재계산형 detector를 같은 interface로 다룰지
method_state snapshot을 method_run마다 저장할지
재시작 후 detector state 복구를 어디까지 보장할지
```

### DRI-008 시간/커서 모델 정의 부족

현재 문서에는 여러 시간 개념이 등장한다.

```text
event_time
inserted_at
source_cursor_time
available_source_time
last_poll_started_at
last_poll_finished_at
logical time
real time
```

결정:

```text
event_time:
  Drift Server 내부 처리 기준 canonical time

source_event_time:
  source data 자체의 원래 발생 시간

inserted_at:
  source DB에 row가 들어온 실제 또는 테스트 삽입 시각

source_cursor_time:
  drift server가 다음에 처리할 canonical event_time 시작점

available_source_time:
  source adapter가 현재 확인한 최대 event_time

collector tick:
  drift server가 poll 기회를 얻은 real/manual clock 시각

빈 window:
  row_count = 0, status = empty인 bucket을 저장하고 cursor를 전진한다.
```

상세 정의는 `time_and_cursor_model.md`에 둔다.

### DRI-009 collector 동시 실행/중복 실행 방지 누락

같은 adapter에 대해 `poll_once`가 동시에 두 번 실행되면 중복 bucket과 event가 생길 수 있다.

결정:

```text
poll lock:
  adapter_state row를 transaction 안에서 SELECT ... FOR UPDATE

metric_bucket:
  unique(adapter_id, feature_id, bucket_start, bucket_end, resolution)

method_run:
  unique(assignment_id, window_start, window_end)

drift_event:
  1차 구현에서는 unique(method_run_id)
```

상세 정의는 `idempotency_and_locking.md`에 둔다.

### DRI-010 chart definition 저장 위치 불명확

`analysis_chart_registration`에는 `chart_definition_id`만 있고, event analysis API는 `chartDefinition`을 반환한다.

결정:

```text
analysis_chart_registration:
  chart_definition_id text
  chart_definition_json jsonb
  chart_builder_job_id text

event analysis:
  기본은 chart_definition_json snapshot 사용
  snapshot이 없으면 chart_builder에서 chart_definition_id로 조회
  조회 성공 시 snapshot 저장
```

### DRI-011 테스트 reset 정책 불명확

테스트 reset이 무엇을 삭제하는지 명확하지 않다.

결정:

```text
run reset:
  raw_event/feed_state/bucket/method_run/drift_event/adapter_state만 초기화
  source/adapter/assignment/chart registration은 보존

source reset:
  특정 source에 연결된 실행 데이터만 삭제

hard reset:
  테스트 관련 데이터를 전체 초기화
```

기본값은 `run` reset이다. 상세 정의는 `reset_policy.md`에 둔다.

### DRI-012 human verification workflow 범위 초과

README의 planned responsibilities에 human verification workflow가 포함되어 있지만 현재 요구사항과 설계 범위에는 없다.

결정:

```text
v1에서는 제외한다.
README의 Planned responsibilities에서는 제거한다.
Future Scope에만 기록한다.
```

### DRI-013 Test Feeder Server 분리 여부

Test Feeder는 테스트용 외부 데이터 소스를 흉내내는 서버다. 운영 source는 아니지만, drift server와 분리된 외부 source simulator로 취급한다.

결정:

```text
Test Feeder Server는 별도 서버/프로세스로 둔다.

Admin Server는 테스트 모드에서 Test Feeder Server를 제어한다.

Admin Server가 제공할 제어:
  test mode enable/disable
  feeder register
  feeder start
  feeder stop
  feeder status
  feeder reset
  feeder tick

Drift Server는 Test Feeder의 CSV를 직접 읽지 않는다.
Drift Server는 Test Feeder가 test_source DB에 넣은 데이터를 SourceAdapter를 통해 가져온다.
```

### DRI-014 Chart Builder Server API 범위 과다

초기 문서에는 관리자 서버가 chart_builder를 호출한다는 방향이 있었지만, 현재 v1 control plane에서는 직접 호출하지 않는다.

결정:

```text
Chart Builder 서버를 v1 control plane의 직접 downstream으로 두지 않음
chart definition은 사전 생성 artifact 또는 registration request snapshot으로 전달
Drift Server는 analysis_chart_registration.chart_definition_json snapshot을 사용
chart_runtime/payloads/runtime_chart_payloads.json과 drift 보고서/charts/method_data.js를 artifact 기준으로 참조
```

### DRI-015 internal HTTP API와 service 직접 호출 혼재

문서에는 `POST /api/internal/...` API가 여러 곳에 등장하지만, 내부 구현 설계는 service class 직접 호출을 권장한다.

결정:

```text
v1:
  /api/internal/... endpoint는 만들지 않는다.
  서버 간 호출은 정식 API와 client class를 사용한다.
  Admin Server는 Drift Server DB나 Test Feeder DB를 직접 수정하지 않는다.
  각 서버 내부 scheduler/service는 자기 프로세스 안의 service class를 직접 호출할 수 있다.

후속:
  worker 분리, internal network, queue 기반 실행이 필요할 때 internal endpoint를 재검토한다.
```

## 4. 우선 검토 순서

구현 전에 우선순위를 둔다면 다음 순서가 적절하다.

```text
1. DRI-001 서버 분리 수준
2. DRI-002 DB schema 관계
3. DRI-006 source_feature
4. DRI-008 시간/커서 모델
5. DRI-009 중복 실행 방지
6. DRI-007 detector state
7. DRI-010 chart definition 저장 위치
8. DRI-011 reset 정책
```

DRI-005, DRI-012, DRI-014, DRI-015는 1차 구현 범위를 줄이는 과정에서 함께 정리한다.

### DRI-016 추천 chart payload 실제 metric 기반 검증 데이터 부족

CASE-012의 CHART-ERR-005 분석 chart에서 template 고정값이 실제 HDDM 결과값 대신 표시되는 문제가 확인되었다.

이번에는 CHART-ERR-005 payload adapter 보정만 적용했지만, 다른 추천 chart와 다른 입력 데이터에서도 같은 유형의 문제가 재발할 수 있다.

결정:

```text
지금 즉시 10개 추천 테스트 데이터를 만들거나 자동화하지 않는다.

후속 이슈로 남긴다.

후속 검증 범위:
  추천 chart 10개 유형의 테스트 데이터 준비
  chart별 payload adapter가 실제 metric 기반으로 config를 보정하는지 확인
  summary, axis, threshold/marker, selection reason이 template 고정값에 머물지 않는지 확인
  회귀 테스트로 고정
```
