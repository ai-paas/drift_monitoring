# Test Feeder Contract

## 1. 목적

이 문서는 Test Feeder Server가 테스트 CSV를 외부 source처럼 replay하여 `test_source` DB에 raw event를 넣는 방식을 정의한다.

Test Feeder는 운영 서버가 아니다. 테스트/데모에서 외부 데이터 소스에 시간이 지나며 데이터가 쌓이는 상황을 재현한다.

## 2. 기본 결정

```text
Test Feeder는 CSV row를 source event로 replay한다.
테스트 모드의 시간 source of truth는 Harness Clock이다.
Harness는 startTime, endTime, tickIntervalMinutes를 config로 확정한다.
Harness 내부 TimeDispatcher는 매 tick마다 변경된 절대 논리 시각(logicalNow)을 Test Feeder에 전달한다.
tick 호출 시 previousLogicalNow 이상 logicalNow 미만 구간의 row를 insert한다.
source_event_time = CSV row timestamp
event_time = Harness logicalNow 기반 canonical time
inserted_at = Harness가 전달한 logicalNow
payload_json = CSV row 전체 또는 v1 metric payload
```

v1 대상:

```text
dataset_case_id = CASE-010
source_id = case-010
feature = metric
```

## 3. Test Source Tables

### 3.1 test_source.raw_event

```sql
create table test_source.raw_event (
  raw_event_id text primary key,
  source_id text not null,
  dataset_case_id text,
  event_time timestamptz not null,
  source_event_time timestamptz,
  source_clock_offset_ms bigint,
  inserted_at timestamptz not null,
  payload_json jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);
```

권장 unique key:

```sql
create unique index uq_test_raw_event_source_time
on test_source.raw_event (source_id, event_time, raw_event_id);
```

v1에서는 CSV의 같은 `event_time`에 row가 하나라고 가정할 수 있다. 여러 row가 있을 가능성이 있으면 `raw_event_id`로 구분한다.

### 3.2 test_source.feed_state

```sql
create table test_source.feed_state (
  source_id text primary key,
  dataset_case_id text not null,
  csv_path text not null,
  event_time_column text,
  logical_cursor_time timestamptz,
  feed_status text not null default 'stopped',
  speed_factor integer not null default 60,
  started_at timestamptz,
  stopped_at timestamptz,
  last_tick_at timestamptz,
  inserted_row_count bigint not null default 0,
  last_error text,
  updated_at timestamptz not null default now()
);
```

`speed_factor = 60`은 데모에서 Harness가 `tickIntervalMinutes=1`인 tick을 real 1초 간격으로 발생시킬 수 있다는 의미로만 사용한다.
DB에 기록되는 시간 기준은 항상 Harness Clock의 `logicalNow`다.

## 4. Feed State

허용 상태:

```text
stopped
running
error
completed
```

상태 의미:

```text
stopped:
  feeder가 tick을 자동 실행하지 않음

running:
  TimeDispatcher tick 또는 데모 scheduler에 의해 row를 insert할 수 있음

error:
  CSV 읽기, parsing, DB insert 실패

completed:
  CSV 끝까지 replay 완료
```

## 5. Tick 규칙

Harness clock config:

```text
startTime
endTime
tickIntervalMinutes
```

tick 요청은 상대 분 값만 보내지 않고 절대 논리 시각을 포함한다.

```json
{
  "logicalNow": "2026-01-01T00:10:00Z",
  "previousLogicalNow": "2026-01-01T00:09:00Z",
  "tickIntervalMinutes": 1,
  "tickIndex": 10
}
```

처리:

```text
read_start = previousLogicalNow
read_end = logicalNow

rows = CSV rows where mapped canonical event_time >= read_start and mapped canonical event_time < read_end
insert rows into test_source.raw_event
feed_state.logical_cursor_time = logicalNow
feed_state.last_tick_at = logicalNow
feed_state.inserted_row_count += inserted rows
```

각 row 저장:

```text
source_event_time = CSV timestamp
event_time = Harness logicalNow 또는 replay interval 안에서 계산한 canonical time
source_clock_offset_ms = event_time - source_event_time
inserted_at = logicalNow
```

요청에 `previousLogicalNow`가 없으면 Test Feeder는 `feed_state.logical_cursor_time`을 read_start로 사용한다.
이 경우에도 요청에는 반드시 `logicalNow`가 있어야 한다.

빈 tick:

```text
해당 구간에 CSV row가 없어도 logical_cursor_time은 read_end로 전진한다.
inserted_row_count는 변하지 않는다.
feed_status는 유지한다.
```

CSV 끝에 도달하면:

```text
feed_status = completed
```

## 6. inserted_at 규칙

`inserted_at`은 row가 test source DB에 보이기 시작한 시각이다.

테스트 모드:

```text
inserted_at = logicalNow
```

데모 모드:

```text
Harness가 real timer로 tick을 발생시키더라도 inserted_at은 Harness logicalNow를 사용한다.
```

Drift Server SourceAdapter는 테스트 source에서 다음 조건으로 visible row를 제한한다.

```text
inserted_at <= collector_tick_time
```

## 7. CSV Payload Mapping

v1에서는 CSV row 전체를 `payload_json`에 보존하고, drift에 필요한 metric도 top-level key로 둔다.

권장 payload:

```json
{
  "metric": 0.42,
  "raw": {
    "columnA": "...",
    "columnB": "..."
  }
}
```

`SourceAdapter`는 `payload_path = $.metric`으로 값을 읽는다.

## 8. CASE-010 Mapping

v1 대상:

```text
dataset_case_id = CASE-010
adapter_type = test_db_numeric_stream
feature_id = metric
payload_path = $.metric
```

CSV timestamp column은 CASE-010 metadata 또는 CSV header를 보고 결정한다. 구현 시 우선순위:

```text
1. metadata.json에 명시된 time column
2. timestamp
3. event_time
4. time
```

metric column 우선순위:

```text
1. metadata.json에 명시된 metric/value column
2. metric
3. value
4. y
```

CASE-010은 CSV timestamp와 Harness logical time이 같은 기준으로 생성된 테스트 데이터일 수 있다. 그래도 저장 정책은 분리한다.

```text
source_event_time:
  CSV timestamp

event_time:
  Drift Server 내부 canonical time
```

## 9. Server API 동작

### 9.1 Feeder 등록

```text
POST /api/test-feeder/feeders
```

동작:

```text
feed_state 생성 또는 갱신
logical_cursor_time 초기화
feed_status = stopped
```

초기 cursor:

```text
요청 startTime이 있으면 startTime
없으면 CSV 첫 event_time
```

### 9.2 Start

```text
POST /api/test-feeder/feeders/{source_id}/start
```

동작:

```text
feed_status = running
started_at = now
last_error = null
```

### 9.3 Stop

```text
POST /api/test-feeder/feeders/{source_id}/stop
```

동작:

```text
feed_status = stopped
stopped_at = now
```

### 9.4 Tick

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

동작:

```text
feed_status가 running이 아니면 기본적으로 실패
force=true가 있으면 단일 tick 허용 가능
```

v1에서는 `running` 상태에서만 tick을 허용한다.

### 9.5 Status

```text
GET /api/test-feeder/feeders/{source_id}/status
```

응답:

```json
{
  "ok": true,
  "data": {
    "sourceId": "case-010",
    "datasetCaseId": "CASE-010",
    "status": "running",
    "logicalCursorTime": "2026-01-01T00:10:00Z",
    "insertedRowCount": 10,
    "lastTickAt": "2026-01-01T00:10:00Z",
    "lastError": null
  },
  "error": null
}
```

### 9.6 Reset

```text
POST /api/test-feeder/reset
```

동작:

```text
test_source.raw_event 삭제
feed_state logical_cursor_time 초기화
feed_state inserted_row_count = 0
feed_state feed_status = stopped
last_error = null
```

reset 상세 정책은 `reset_policy.md`를 따른다.

## 10. Error 처리

CSV 파일 없음:

```text
feed_status = error
last_error 저장
```

CSV parse 실패:

```text
feed_status = error
last_error 저장
해당 tick transaction rollback
logical_cursor_time 유지
```

DB insert 실패:

```text
feed_status = error
last_error 저장
logical_cursor_time 유지
```

일부 row 변환 실패:

```text
v1에서는 tick 실패로 처리한다.
후속에서는 invalid row skip 정책을 둘 수 있다.
```

## 11. Transaction 규칙

tick은 transaction 단위로 처리한다.

```text
begin transaction
  feed_state 조회
  CSV rows 선택
  raw_event insert
  feed_state 갱신
commit
```

실패하면 rollback하고 cursor를 전진하지 않는다.

## 12. 관련 문서

```text
source_adapter_contract.md
time_and_cursor_model.md
reset_policy.md
implementation_scope_v1.md
```
