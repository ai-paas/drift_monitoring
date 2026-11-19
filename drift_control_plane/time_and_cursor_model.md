# Drift Server Time and Cursor Model

## 1. 목적

이 문서는 Test Feeder, 외부 source, Drift Server collector, catch-up, timeseries UI가 공유해야 하는 시간/커서 모델을 정의한다.

핵심 목표는 다음이다.

```text
source에 데이터가 더 많이 쌓여 있어도
drift server의 정상 poll 한 번은
source_cursor_time 기준 10분 canonical event_time window 하나만 처리한다.
```

운영/테스트 공통 시간 원칙:

```text
Drift Server 내부 처리 시간은 canonical event_time으로 통일한다.
canonical event_time은 Drift Server/Harness가 쓰는 내부 논리 시간이다.
data source의 원래 발생 시각은 source_event_time으로 별도 보존한다.
bucket/window/cursor/method_run/drift_event는 source_event_time이 아니라 canonical event_time 기준으로 처리한다.
source별 clock 차이는 source_config 또는 adapter_config의 time mapping 정책으로 보정한다.
adapter는 정기적으로 source server time과 Drift Server 기준 시각을 비교해 source clock offset 상태를 갱신한다.
```

테스트 모드의 시간 source of truth는 Harness Clock이다.

```text
Harness가 시작할 때 startTime, endTime, tickIntervalMinutes를 config로 확정한다.
Harness Clock은 startTime에서 시작해 tickIntervalMinutes 단위로만 전진한다.
Harness 내부 TimeDispatcher는 매 tick마다 변경된 절대 논리 시각(logicalNow)을 서버들에게 전달한다.
서버는 테스트 모드에서 자기 시간을 임의로 전진시키지 않고 Harness가 전달한 logicalNow를 기준으로 처리한다.
```

## 2. 시간 용어 정의

### 2.1 event_time

Drift Server 내부에서 사용하는 canonical event time이다.

`event_time`은 모든 수집 window, bucket, method run, drift event의 기준 시간이다. 운영 source의 timestamp가 제각각이어도 Drift Server 내부에서는 `event_time` 하나로 통일해 처리한다.

예:

```text
Harness logicalNow
server_received_at을 minute 단위로 정렬한 시간
source_event_time + configured offset
adapter가 source별 시간 정책에 따라 변환한 canonical time
```

Drift Server의 bucket window는 `event_time` 기준으로 계산한다.

### 2.2 source_event_time

source data 자체가 가진 원래 발생 시간이다.

예:

```text
CSV row timestamp
외부 inference event 발생 시각
model input/output이 생성된 시각
```

`source_event_time`은 분석과 추적을 위해 보존하지만, Drift Server 내부 window 기준으로 직접 쓰지 않는다.

### 2.3 inserted_at

row가 source DB에 실제로 들어온 시각이다.

테스트 모드에서는 Test Feeder가 test source DB에 row를 insert한 시각이다.

```text
event_time:
  Drift Server 내부 처리 기준 시간

source_event_time:
  row가 원래 source에서 발생했다고 기록된 시간

inserted_at:
  그 row가 source DB에 보이기 시작한 시각
```

### 2.4 source_clock_offset_ms

source의 원래 시간과 Drift Server 내부 canonical time 사이의 차이다.

```text
source_clock_offset_ms = event_time - source_event_time
```

이 값은 source별로 고정 설정할 수도 있고, adapter가 row별로 계산해 metadata에 남길 수도 있다.
또한 adapter는 row 수집과 별개로 source server의 현재 시각을 정기 조회해 최근 offset 상태를 adapter_state에 저장한다.

용도:

```text
source server clock skew 진단
source별 시간 보정 정책 검증
운영 장애 분석
원본 시간 기준 재분석
```

### 2.5 source_cursor_time

Drift Server가 다음 poll에서 읽을 canonical `event_time` 시작점이다.

저장 위치:

```text
drift_server.adapter_state.source_cursor_time
```

정상 poll이 성공하면 `source_cursor_time`은 10분 전진한다.

### 2.6 available_source_time

SourceAdapter가 현재 source에서 확인한 최대 처리 가능 canonical `event_time`이다.

예:

```text
select max(event_time) from test_source.raw_event
```

catch-up은 `available_source_time`을 기준으로 어디까지 처리할 수 있는지 판단한다.

### 2.7 collector_tick_time

Drift Server가 `poll_once`를 실행할 기회를 얻은 시각이다.

운영 모드:

```text
collector_tick_time = real clock now
```

테스트 모드:

```text
collector_tick_time = Harness가 전달한 logicalNow
```

테스트 모드에서 `collector_tick_time`은 "현재 몇 시 몇 분인가"를 명확히 나타내는 절대 논리 시각이다.
상대 전진값만으로 판단하지 않는다.

### 2.8 bucket_start / bucket_end

Drift Server가 저장하는 집계 bucket의 canonical `event_time` 구간이다. v1 기본 bucket 크기는 10분이다.

```text
bucket_start = source_cursor_time
bucket_end = source_cursor_time + aggregate_interval
```

구간은 half-open interval이다.

```text
event_time >= bucket_start
event_time < bucket_end
```

### 2.9 last_poll_started_at / last_poll_finished_at

Drift Server collector가 poll을 시작/종료한 실제 또는 테스트 clock 시각이다.

저장 위치:

```text
drift_server.adapter_state.last_poll_started_at
drift_server.adapter_state.last_poll_finished_at
```

이 값은 canonical `event_time`이나 source data의 `source_event_time`이 아니라 collector 실행 기록이다.

## 3. Source Time Mapping 규칙

SourceAdapter는 source별 원래 시간을 Drift Server 내부 canonical time으로 변환한다.

기본 원칙:

```text
source_event_time은 절대 덮어쓰지 않고 보존한다.
event_time은 Drift Server 내부 처리를 위한 canonical time으로 생성한다.
window/cursor/bucket은 event_time만 사용한다.
source_event_time은 분석/추적/진단용 metadata로 사용한다.
```

source별 time mapping 설정 예:

```json
{
  "timeMapping": {
    "mode": "observed_offset",
    "sourceTimeColumn": "event_time",
    "sourceTimezone": "UTC",
    "clockOffsetMs": 120000,
    "maxAllowedClockOffsetMs": 300000,
    "clockCheckIntervalSeconds": 60,
    "sourceServerTimeQuery": "select now()",
    "roundTo": "1m"
  }
}
```

기본 mode:

```text
운영 기본:
  observed_offset

테스트/데모 기본:
  harness_logical_time
```

지원할 수 있는 mode:

```text
fixed_offset:
  event_time = source_event_time + clockOffsetMs

observed_offset:
  event_time = adapter/server observed_at
  source_clock_offset_ms = observed_at - source_event_time

source_ingest_time:
  event_time = server_received_at 또는 inserted_at
  source_event_time이 없으면 source_clock_offset_ms = null

harness_logical_time:
  event_time = Harness logicalNow

custom_adapter_mapping:
  adapter별 규칙으로 event_time 계산
```

offset 계산 책임:

```text
SourceAdapter는 source_event_time을 읽고 canonical event_time을 계산한다.
SourceAdapter는 event_time - source_event_time 값을 source_clock_offset_ms로 기록한다.
선택된 timeMapping mode가 source_event_time을 필요로 하는데 source_event_time이 없거나 신뢰할 수 없으면 adapter clock 오류로 처리한다.
source_ingest_time처럼 source_event_time이 없어도 되는 mode에서는 source_event_time = null, source_clock_offset_ms = null을 허용한다.
```

offset 결정 방식:

```text
configured:
  운영자가 설정한 clockOffsetMs 사용

observed:
  adapter/server가 row를 관측한 시각과 source_event_time 차이를 계산

source_provided:
  source가 제공한 server time 또는 ingest time 사용

hybrid:
  configured offset을 기본값으로 사용하고 observed offset으로 drift 여부 진단
```

clock 오류 정책:

```text
abs(source_clock_offset_ms) > maxAllowedClockOffsetMs이면 adapter를 사용할 수 없는 상태로 본다.
source_event_time이 필요한 mode에서 source_event_time이 없으면 adapter를 사용할 수 없는 상태로 본다.
이 상황은 row 단위 invalid나 단순 경고가 아니라 SourceAdapterClockError다.
DriftCollector는 해당 poll을 실패로 처리하고 bucket/method_run/drift_event를 만들지 않는다.
source_cursor_time은 전진하지 않는다.
source_adapter.status는 error로 전환하고 adapter_state.last_error, clock_status, clock_error_code에 원인을 기록한다.
```

정기 clock check 정책:

```text
SourceAdapter는 row fetch와 별개로 source server time을 정기 조회한다.
source_clock_offset_ms = reference_time - source_server_time으로 계산한다.
reference_time은 운영 모드에서는 Drift Server 기준 현재 시각, 테스트 모드에서는 Harness logicalNow다.
check 결과는 adapter_state에 저장한다.
허용 범위를 넘으면 adapter를 error 상태로 전환하고 이후 poll을 진행하지 않는다.
row가 없는 source도 clock check 대상이다.
```

미래 데이터 정책:

```text
SourceAdapter는 source 시간을 canonical event_time으로 변환한 뒤 미래 여부를 판단한다.
변환된 event_time이 collector_tick_time 또는 visible_at보다 미래이면 해당 row는 아직 사용하지 않는다.
미래 row는 invalid가 아니고 adapter 오류도 아니다.
collector_tick_time이 event_time에 도달한 뒤 같은 window 처리에서 사용한다.
```

v1 테스트 모드:

```text
timeMapping.mode = harness_logical_time
source_event_time = CSV row timestamp
event_time = Harness logicalNow 기반 canonical time
inserted_at = Harness logicalNow
```

운영 모드 기본 권장:

```text
timeMapping.mode = observed_offset
source_event_time = source payload timestamp
server_received_at = Drift Server 또는 source adapter가 row를 관측한 시간
event_time = observedAt을 roundTo 단위로 정렬한 canonical time
source_clock_offset_ms = event_time - source_event_time
```

## 4. 정상 수집 규칙

정상 poll 1회는 항상 aggregate interval window 하나만 처리한다. v1 기본값은 10분이다.

```text
read_start = adapter_state.source_cursor_time
read_end = read_start + aggregate_interval
```

SourceAdapter는 다음 조건으로 row를 가져온다.

```text
event_time >= read_start
event_time < read_end
event_time <= collector_tick_time
```

여기서 `event_time`은 source 원래 시간이 아니라 Drift Server canonical time이다.

테스트 DB처럼 `inserted_at`이 있는 source에서는 현재 collector가 볼 수 있는 row만 가져온다.

```text
inserted_at <= collector_tick_time
```

따라서 테스트 source 조회 조건은 다음과 같다.

```sql
where source_id = :source_id
  and event_time >= :read_start
  and event_time < :read_end
  and event_time <= :collector_tick_time
  and inserted_at <= :collector_tick_time
```

정상 poll은 source에 `read_end` 이후 데이터가 이미 쌓여 있어도 한 번에 처리하지 않는다.

```text
source에 20분 데이터가 있어도
normal poll 1회 = aggregate interval window 하나
```

## 5. Cursor Advance 규칙

poll이 성공하면 cursor는 항상 `read_end`로 전진한다.

```text
adapter_state.source_cursor_time = read_end
```

성공의 의미:

```text
source 조회 성공
bucket 저장 성공
method 실행 및 event 생성 단계가 정상 종료 또는 기록 가능한 오류로 종료
```

source 조회 자체가 실패하면 cursor를 전진하지 않는다.

```text
source DB 연결 실패
query 실패
adapter fetch 실패
```

이 경우:

```text
adapter_state.last_error 저장
source_cursor_time 유지
```

## 6. 빈 Window 처리 정책

빈 aggregate interval window도 bucket을 저장한다. v1 기본값은 10분이다.

정책:

```text
row가 0개여도 metric_bucket row를 만든다.
row_count = 0
status = empty
cursor는 read_end로 전진한다.
```

예:

```text
metric_bucket
  bucket_start = 2026-07-01T00:00:00Z
  bucket_end   = 2026-07-01T00:10:00Z
  row_count    = 0
  status       = empty
```

이 정책을 쓰는 이유:

```text
해당 window를 처리했다는 사실이 남는다.
처리 안 됨과 데이터 없음이 구분된다.
catch-up/retry 판단이 쉬워진다.
중복 실행 방지에 유리하다.
UI에서 빈 구간을 명확히 표현할 수 있다.
```

빈 bucket에 대해서는 기본적으로 drift method를 실행하지 않는다. 다만 특정 method가 빈 window를 입력으로 처리해야 한다면 assignment 설정으로 허용할 수 있다.

## 7. Harness Clock 기반 테스트 시간 모델

테스트 모드에서는 Harness Clock이 논리 시간의 주인이다.

```text
clockStartTime = 2026-01-01T00:00:00Z
clockEndTime = 2026-01-01T01:00:00Z
tickIntervalMinutes = 1
```

Harness가 시작되면 시간은 반드시 `tickIntervalMinutes` 단위로만 전진한다.

```text
00:00 -> 00:01 -> 00:02 -> ... -> 01:00
```

각 tick에서 Harness 내부 TimeDispatcher는 변경된 절대 논리 시각을 서버들에게 전달한다.

```text
logicalNow = 2026-01-01T00:01:00Z
logicalNow = 2026-01-01T00:02:00Z
...
logicalNow = 2026-01-01T00:10:00Z
```

권장 tick payload:

```json
{
  "clock": {
    "startTime": "2026-01-01T00:00:00Z",
    "endTime": "2026-01-01T01:00:00Z",
    "tickIntervalMinutes": 1,
    "logicalNow": "2026-01-01T00:10:00Z",
    "previousLogicalNow": "2026-01-01T00:09:00Z",
    "tickIndex": 10
  }
}
```

Test Feeder는 CSV row의 `source_event_time`을 읽고, Harness logicalNow 기준으로 canonical `event_time`을 부여해 `test_source.raw_event`에 넣는다.
Drift Server는 `logicalNow`를 collector visibility 기준으로 사용한다.

테스트 브라우저 데모에서 real-time 재생이 필요하면 Harness가 real timer로 tick을 발생시킬 수 있다. 이 경우에도 서버에 전달되는 값의 기준은 real clock이 아니라 Harness Clock의 `logicalNow`다.

자동 테스트에서는 sleep을 사용하지 않는다. HarnessClock이 config에 정의된 tick sequence를 즉시 만들고, TimeDispatcher가 각 tick의 `logicalNow`를 서버에 전달한다.

## 8. Source Visibility 규칙

source에 row가 있다는 것과 Drift Server가 그 row를 볼 수 있다는 것은 다르다.

운영 source:

```text
SourceAdapter가 조회 시점에 반환하는 row가 visible row다.
inserted_at이 없을 수도 있다.
```

테스트 source:

```text
inserted_at <= collector_tick_time인 row만 visible row다.
테스트 모드에서는 collector_tick_time = Harness logicalNow다.
```

이 규칙 때문에 테스트에서 다음 상황이 가능하다.

```text
Test Feeder가 source DB에 logical 20분까지 넣어둠
Drift Server collector는 아직 한 번만 poll함
Drift Server는 0~10분 window만 처리
다음 poll에서 10~20분 window 처리
```

## 9. Catch-up 규칙

catch-up은 명시적으로 호출된 경우에만 여러 window를 처리한다.

```text
POST /api/admin/adapters/{adapter_id}/catch-up
```

Drift Server 내부 처리:

```text
while source_cursor_time + aggregate_interval <= available_source_time:
  process_one_window()
```

catch-up도 window 단위 처리다.

```text
raw data 전체를 한 번에 메모리에 올리지 않는다.
한 loop에서 aggregate interval window 하나만 처리한다.
각 window 처리 성공 후 cursor를 전진한다.
```

catch-up 중 특정 window에서 source 조회 실패가 발생하면 중단한다.

```text
last_error 저장
source_cursor_time은 실패한 window 시작점 유지
```

## 10. Adapter State 필드

권장 필드:

```sql
drift_server.adapter_state
  adapter_id text primary key
  source_cursor_time timestamptz
  available_source_time timestamptz
  last_poll_started_at timestamptz
  last_poll_finished_at timestamptz
  last_success_at timestamptz
  last_error text
  clock_status text
  clock_error_code text
  last_source_clock_offset_ms bigint
  min_source_clock_offset_ms bigint
  max_source_clock_offset_ms bigint
  avg_source_clock_offset_ms double precision
  offset_sample_count bigint
  last_clock_check_at timestamptz
  last_source_server_time timestamptz
  last_clock_reference_time timestamptz
  updated_at timestamptz
```

각 필드 의미:

```text
source_cursor_time:
  다음에 처리할 canonical event_time 시작점

available_source_time:
  source adapter가 마지막으로 확인한 최대 canonical event_time

last_poll_started_at:
  collector poll 시작 시각

last_poll_finished_at:
  collector poll 종료 시각

last_success_at:
  마지막 성공 poll 종료 시각

last_error:
  마지막 실패 메시지

clock_status:
  마지막 시간 mapping 상태. 예: ok, error

clock_error_code:
  시간 mapping 실패 원인. 예: CLOCK_OFFSET_EXCEEDED, SOURCE_EVENT_TIME_MISSING

last_source_clock_offset_ms:
  마지막으로 계산한 source_clock_offset_ms

min_source_clock_offset_ms:
  최근 집계 구간에서 관측한 최소 source_clock_offset_ms

max_source_clock_offset_ms:
  최근 집계 구간에서 관측한 최대 source_clock_offset_ms

avg_source_clock_offset_ms:
  최근 집계 구간에서 관측한 평균 source_clock_offset_ms

offset_sample_count:
  최근 집계 구간에 반영한 offset sample 수

last_clock_check_at:
  마지막 source clock check를 수행한 시각

last_source_server_time:
  마지막 clock check에서 source가 반환한 현재 시각

last_clock_reference_time:
  마지막 clock check에서 비교 기준으로 사용한 Drift Server/Harness 시각
```

## 11. 예시 시나리오

### 10.1 정상 10분 수집

```text
source_cursor_time = 2026-01-01T00:00:00Z

poll_once
  read_start = 2026-01-01T00:00:00Z
  read_end   = 2026-01-01T00:10:00Z
  fetch 00:00 <= canonical event_time < 00:10
  save bucket 00:00~00:10
  source_cursor_time = 00:10
```

### 10.2 source가 20분 앞서 있는 경우

```text
source has rows until 00:20
source_cursor_time = 00:00

first poll:
  process 00:00~00:10 only
  cursor = 00:10

second poll:
  process 00:10~00:20 only
  cursor = 00:20
```

정상 poll은 첫 번째 poll에서 20분치를 한꺼번에 처리하지 않는다.

### 10.3 빈 window

```text
source_cursor_time = 00:20
source has no rows in 00:20~00:30

poll:
  fetch row_count = 0
  save empty bucket 00:20~00:30
  cursor = 00:30
```

### 10.4 source 조회 실패

```text
source_cursor_time = 00:30
adapter fetch failed

poll:
  save last_error
  cursor remains 00:30
```

다음 poll은 다시 00:30~00:40을 시도한다.

### 10.5 중단 후 catch-up

```text
source_cursor_time = 00:30
available_source_time = 01:00

catch-up:
  process 00:30~00:40
  process 00:40~00:50
  process 00:50~01:00
```

## 12. 중복 실행 방지와의 관계

이 문서는 시간/커서 의미를 정의한다. 동시 실행과 중복 실행 방지는 별도 이슈인 `DRI-009`에서 다룬다.

다만 이 시간 모델은 다음 unique key와 잘 맞아야 한다.

```text
metric_bucket:
  unique(adapter_id, feature_id, bucket_start, bucket_end, resolution)

method_run:
  unique(assignment_id, window_start, window_end)

drift_event:
  method_run_id 기준 중복 생성 방지
```

## 13. 관련 이슈

```text
DRI-008 시간/커서 모델 정의 부족
DRI-009 collector 동시 실행/중복 실행 방지 누락
```
