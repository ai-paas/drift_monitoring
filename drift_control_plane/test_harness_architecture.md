# Drift Server 테스트 하네스 및 Adapter 실행 구조

## 1. 목적

이 문서는 `drift_server`를 테스트 데이터, 테스트 DB, `drift_metric_timeseries` UI와 연결하기 위한 초기 구조를 정의한다.

목표는 다음이다.

- 외부 데이터 소스를 관리자 화면에서 등록한다.
- 등록된 source adapter를 실행하면 주기적으로 데이터를 가져온다.
- 테스트 모드에서는 `테스트데이터/` CSV를 테스트 DB에 빠르게 적재한다.
- `drift_server`는 테스트 DB에서 10분 logical window 단위로 데이터를 가져와 집계한다.
- `drift_metric_timeseries` UI는 `drift_server`가 만든 bucket/event를 조회한다.
- 테스트 하네스는 테스트 DB 초기화, 테스트 서버 실행, drift collector 실행, 상태 확인을 단순하게 관리한다.

## 2. 핵심 판단

관리자 서버가 하네스 역할을 맡는 방향은 적절하다.

다만 관리자 서버가 직접 CSV 파싱, DB 적재, adapter poll, detector 실행 로직을 모두 구현하면 구조가 빨리 복잡해진다. 따라서 관리자 서버는 다음 역할만 맡는다.

```text
관리자 서버 = orchestration layer
```

실제 동작은 독립 서버 또는 독립 실행 단위로 분리한다.

```text
Test Feeder Server
  테스트 CSV를 읽어 테스트 DB에 logical time 순서로 insert

Drift Server SourceAdapter
  외부 source에서 특정 logical window 데이터를 조회

Drift Server DriftCollector
  adapter를 호출해 10분 window를 가져오고 bucket 집계 저장

Drift Server DriftDetector
  집계된 bucket series에서 warning/drift event 생성

Scheduler
  real time 또는 simulated time 기준으로 feeder/collector를 주기 실행
```

관리자 서버는 이 서버들을 켜고 끄고 상태를 보여주는 API와 화면만 제공한다.

## 3. 전체 구성

```text
관리자 화면/Admin Server
  -> source 등록
  -> adapter 등록
  -> drift method별 analysis chart 등록
  -> test mode on/off
  -> 테스트 DB reset
  -> test feeder start/stop
  -> drift adapter start/stop
  -> 상태 조회

테스트 서버/Test Feeder
  -> 테스트데이터/CASE-*/data.csv.gz
  -> 테스트 DB raw_source_event insert

Drift Server
  -> SourceAdapter로 테스트 DB 조회
  -> 10분 logical window 집계
  -> bucket/event 저장
  -> drift_metric_timeseries API 제공

drift_metric_timeseries UI
  -> bucket/event 조회
  -> event analysis chart 요청
```

## 3.1 Control Plane과 Data Plane

역할 혼선을 막기 위해 서버들을 control plane과 data plane으로 분리한다.

```text
Control Plane
  관리자 서버/Admin Server

Data Plane
  테스트 데이터 feeder 또는 테스트 서버
  drift_server adapter
  drift_server collector
  drift_server detector
  drift_server timeseries/event API
```

관리자 서버는 control plane이다. 관리자 서버는 실행 대상을 등록하고, 켜고, 끄고, 상태를 조회한다.

관리자 서버가 직접 하면 안 되는 일:

```text
CSV row 직접 파싱/적재
10분 bucket 평균 계산
drift 알고리즘 실행
drift event 생성
timeseries chart용 데이터 직접 생성
```

이 작업은 data plane 서비스가 담당한다.

### 관리자 서버 책임

```text
source 등록/수정/삭제
adapter 등록/수정/삭제
`drift 보고서` DB의 method/variant/implementation 목록 조회
source별 drift method assignment 등록/수정/삭제
source method별 analysis chart registration 등록/수정/삭제
chart_builder를 통한 chart definition 생성 요청
chart payload adapter 선택/등록 요청
test mode on/off
테스트 DB reset 요청
feeder start/stop 요청
adapter start/stop 요청
catch-up 실행 요청
현재 상태 조회
오류 상태 조회
cursor/bucket/event count 조회
```

### 테스트 feeder 책임

```text
테스트 CSV 읽기
Harness logicalNow 기준 cursor 관리
tickIntervalMinutes 단위 raw event insert
테스트 source DB에 inserted_at 기록
feed status와 오류 기록
```

### drift server 책임

```text
adapter source_cursor_time 관리
source adapter로 logical 10분 window 조회
10분 bucket 집계
bucket 저장
source별 method assignment 조회
`drift 보고서` DB의 algorithm implementation 기준으로 실행 함수 선택
할당된 drift method 실행
method run/result 저장
drift detector 실행
warning/drift event 저장
event에 등록된 analysis chart 조회
registered payload adapter로 chart runtime payload 생성
drift_metric_timeseries API 제공
event analysis payload 제공
```

### drift_metric_timeseries UI 책임

```text
drift server API에서 bucket/event 조회
시간 범위/scale/feature 선택 상태 관리
event 선택 시 analysis payload 요청
LLM interpretation server에 chart 해석 요청
```

### LLM interpretation server 책임

```text
chart payload와 component data 수신
drift ontology DB의 guide/context 조회
chart/component 해석 생성
drift 계산이나 data 수집은 수행하지 않음
```

## 3.2 실행 모드별 관계

같은 service layer를 두 가지 방식으로 실행한다.

### 운영/브라우저 데모 모드

서버 또는 background scheduler가 실제로 실행된다.

```text
Admin Server
  -> Feeder process/service start
  -> Drift Server adapter start

Feeder
  -> Harness logicalNow 기준 data insert

Drift Server
  -> 10분 logicalNow 경계마다 logical 10분 window poll

UI
  -> Drift Server API poll
```

### 자동 테스트 모드

운영 구조와 같은 server boundary를 검증하는 것이 우선이다. 따라서 자동 테스트도 가능하면 Admin Server API를 통해 Test Feeder Server와 Drift Server를 제어한다.

```text
Test Harness
  -> Admin Server API
  -> Test Feeder Server API
  -> Drift Server API
  -> assertion
```

단위 테스트에서는 각 서버 내부 service class를 직접 호출할 수 있다. 그러나 통합 테스트와 데모 테스트는 서버 간 API contract를 기준으로 한다.

## 4. 테스트 시간 모델

테스트에서는 실제 시간을 그대로 기다리지 않는다.

```text
Harness Clock이 startTime, endTime, tickIntervalMinutes를 가진다.
Harness는 tickIntervalMinutes 단위로 logicalNow를 생성한다.
Harness 내부 TimeDispatcher는 변경된 logicalNow를 서버들에게 전달한다.
```

자동 테스트에서는 실제 `sleep`을 사용하지 않는다.

```text
자동 테스트 하네스:
  tick sequence가 logicalNow를 생성
  10분 logicalNow 경계마다 TimeDispatcher가 Drift Server poll을 요청
  sleep 없음

브라우저 데모:
  Harness가 real timer로 logicalNow tick을 발생시킬 수 있음
  서버에 전달되는 기준값은 real time이 아니라 logicalNow
```

따라서 clock은 설정 가능해야 한다.

```text
RealClock
  운영 scheduler용

HarnessClock
  자동 테스트와 데모 tick source of truth
```

## 5. 데이터 수집 규칙

adapter는 Drift Server 내부 canonical event_time cursor를 가진다.

```text
adapter_state.source_cursor_time
```

정상 실행 중 한 번의 poll은 항상 한 window만 처리한다.

```text
read_start = source_cursor_time
read_end = source_cursor_time + 10분

rows = adapter.fetch(read_start, read_end)
bucket = aggregate(rows)
save(bucket)

source_cursor_time = read_end
```

외부 source 또는 테스트 DB에 `read_end` 이후 데이터가 이미 많이 쌓여 있어도 한 번에 모두 처리하지 않는다. 정상 poll에서는 cursor를 10분만 전진한다.

중단 후 재시작하는 catch-up 모드는 별도 정책이다.

```text
while source_cursor_time + 10분 <= available_logical_time:
  process_one_window()
```

catch-up도 window 단위 처리이며, raw data 전체를 한 번에 메모리에 올리지 않는다.

## 6. 테스트 DB 역할

테스트 DB는 외부 데이터 소스를 흉내낸다.

```text
테스트데이터 CSV
  -> CsvFeeder
  -> test_raw_source_event
  -> SourceAdapter
  -> drift_server bucket/event
```

테스트 DB는 drift_server의 내부 저장소와 분리하는 것이 좋다.

```text
test_source_db
  외부 source 역할
  raw event 저장

drift_server_db
  adapter state
  collected bucket
  detector result
  drift event
```

현재 v1 dev runtime에서는 같은 SQLite dev DB 안에서 logical table group만 분리한다.

```text
raw_event
adapter_state
metric_bucket
drift_event
```

## 7. 최소 테이블 초안

### 7.1 테스트 source raw event

```sql
test_source.raw_event
  source_id text
  event_time timestamptz
  source_event_time timestamptz
  source_clock_offset_ms bigint
  inserted_at timestamptz
  payload_json jsonb
```

CSV 컬럼을 모두 정규화하지 않고, 초기에는 `payload_json`에 보존한다. 자주 쓰는 값만 adapter에서 추출한다.

### 7.2 테스트 feeder state

```sql
test_source.feed_state
  source_id text primary key
  dataset_case_id text
  csv_path text
  logical_cursor_time timestamptz
  feed_status text
  speed_factor integer
  updated_at timestamptz
```

### 7.3 adapter registry

```sql
drift_server.source_adapter
  adapter_id text primary key
  source_id text
  adapter_type text
  source_config_json jsonb
  collection_interval_minutes integer
  aggregate_interval_minutes integer
  status text
  created_at timestamptz
  updated_at timestamptz
```

### 7.4 adapter state

```sql
drift_server.adapter_state
  adapter_id text primary key
  source_cursor_time timestamptz
  last_poll_started_at timestamptz
  last_poll_finished_at timestamptz
  last_error text
```

### 7.5 collected metric bucket

```sql
drift_server.metric_bucket
  adapter_id text
  feature_id text
  bucket_start timestamptz
  bucket_end timestamptz
  count integer
  mean_value double precision
  min_value double precision
  max_value double precision
  status text
  payload_json jsonb
```

### 7.6 drift event

```sql
drift_server.drift_event
  event_id text primary key
  adapter_id text
  feature_id text
  event_start timestamptz
  event_end timestamptz
  level text
  score double precision
  method_code text
  variant_code text
  chart_code text
  payload_json jsonb
```

## 8. 관리자 서버 API 초안

관리자 서버는 운영 모드와 테스트 모드를 모두 제어한다.

```text
GET  /api/admin/sources
POST /api/admin/sources

GET  /api/admin/adapters
POST /api/admin/adapters
POST /api/admin/adapters/{adapter_id}/start
POST /api/admin/adapters/{adapter_id}/stop
GET  /api/admin/adapters/{adapter_id}/status

POST /api/admin/test-mode/enable
POST /api/admin/test-mode/disable
POST /api/admin/test/reset
POST /api/admin/test/feeders/{source_id}/start
POST /api/admin/test/feeders/{source_id}/stop
POST /api/admin/test/tick
GET  /api/admin/test/status
```

`/api/admin/test/tick`은 Admin 관제 상태 기록용이다. 실제 시간 전송과 feeder/collector 실행은 Harness 내부 TimeDispatcher가 각 서버 API를 직접 호출한다.

```json
{
  "logicalNow": "2026-01-01T00:10:00Z",
  "previousLogicalNow": "2026-01-01T00:09:00Z",
  "tickIntervalMinutes": 1,
  "tickIndex": 10
}
```

## 9. 자동 테스트 하네스 흐름

자동 테스트는 두 단계로 나눈다.

```text
단위 테스트:
  각 서버 내부 service class를 직접 호출

통합 테스트:
  Admin Server, Test Feeder Server, Drift Server를 띄우고 API contract 기준으로 검증
```

통합 테스트의 흐름은 다음과 같다.

```python
def test_case_010_adwin_stream(api):
    api.admin.reset_test_environment()

    source = api.admin.register_test_source(
        source_id="case-010",
        dataset_case_id="CASE-010",
        csv_path="테스트데이터/CASE-010_stream_numeric_mean_shift/data.csv.gz",
    )

    adapter = api.admin.register_adapter(
        adapter_id="case-010-adwin",
        source_id=source.source_id,
        adapter_type="test_db_numeric_stream",
        collection_interval_minutes=10,
    )

    api.admin.start_feeder(source.source_id)
    api.admin.start_adapter(adapter.adapter_id)

    for tick in harness_clock.iter_ticks():
        api.test_feeder.tick(tick)
        if tick.logical_now is 10분 경계:
            api.drift.poll_once(adapter.adapter_id, tick)

    assert api.drift.metric_bucket_count(adapter.adapter_id) == 6
```

브라우저 데모에서도 같은 서버 API를 사용한다.

## 10. 구현 원칙

1. 관리자 서버는 orchestration만 한다.
2. 각 서버 내부의 feeder, adapter, collector, detector 로직은 service class로 만든다.
3. 자동 테스트는 실제 시간 sleep을 쓰지 않는다.
4. 브라우저 데모만 real scheduler를 사용한다.
5. 정상 poll은 항상 10분 logical window 하나만 처리한다.
6. catch-up은 명시적으로 start/restart 시나리오에서만 여러 window를 처리한다.
7. raw data는 테스트 source DB에 있고, drift_server는 집계 bucket과 event를 저장한다.
8. 서버 간 통합 테스트와 데모는 API contract를 기준으로 한다.
9. `drift_metric_timeseries`는 drift_server API만 본다.
