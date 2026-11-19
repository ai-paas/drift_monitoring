# Source Adapter Contract

## 1. 목적

이 문서는 Drift Server가 외부 source 또는 test source DB에서 데이터를 가져올 때 사용하는 SourceAdapter contract를 정의한다.

핵심 결정:

```text
SourceAdapter는 source fetch와 최소 정규화까지만 담당한다.
bucket aggregation은 DriftCollector가 담당한다. v1 기본 bucket resolution은 10분이다.
```

## 2. 책임 분리

### 2.1 SourceAdapter 책임

```text
source_config를 해석한다.
source에서 canonical event_time window에 해당하는 raw row를 조회한다.
source 원래 시간(source_event_time)을 canonical event_time으로 변환한다.
필요하면 visible_at 또는 inserted_at 기준으로 현재 보이는 row만 제한한다.
정기적으로 source server time을 읽어 Drift Server 기준 시각과의 차이를 갱신한다.
raw row에서 feature 값을 추출한다.
DriftCollector가 처리할 수 있는 normalized SourceRow 목록을 반환한다.
source에서 현재 처리 가능한 available_source_time을 반환한다.
```

### 2.2 DriftCollector 책임

```text
SourceAdapter.fetch() 호출
SourceRow를 feature별로 그룹화
numeric feature의 count/mean/min/max/stddev 계산
빈 window는 empty bucket 저장
metric_bucket 저장
adapter_state.source_cursor_time 갱신
DriftDetector 호출
```

SourceAdapter는 bucket을 저장하지 않는다. DriftDetector를 호출하지도 않는다.

### 2.3 Test DB bucket adapter types

DriftCollector는 test DB raw_event를 bucket으로 집계할 때 다음 adapter type을 지원한다.

```text
test_db_prediction_log_stream:
  raw_event payload의 error/confidence를 error-rate stream bucket으로 변환한다.

test_db_numeric_distribution_window:
  raw_event payload의 score/value/metric을 numeric distribution payload.values로 변환한다.
  payload에 pair_id가 있으면 paired statistical test용 선택 필드로 보존한다.

test_db_categorical_count_window:
  raw_event payload의 category/count/period를 categorical contingency payload.values로 변환한다.
  bucket feature_id는 category이다.
```

`test_db_categorical_count_window`의 bucket payload shape:

```json
{
  "values": [
    {
      "time": "2026-06-30T23:10:00Z",
      "category": "approved",
      "count": 40.0,
      "period": "reference"
    },
    {
      "time": "2026-07-01T00:10:00Z",
      "category": "declined",
      "count": 40.0,
      "period": "current"
    }
  ]
}
```

## 3. Adapter Interface

Python interface:

```python
class SourceAdapter:
    adapter_type: str

    def fetch(
        self,
        source_config: dict,
        start_time,
        end_time,
        visible_at=None,
    ) -> list[dict]:
        ...

    def available_time(self, source_config: dict):
        ...

    def check_clock(self, source_config: dict, reference_time):
        ...
```

`start_time`과 `end_time`은 Drift Server 내부 canonical `event_time` 기준이다.

구간:

```text
event_time >= start_time
event_time < end_time
```

`visible_at`은 테스트 source처럼 `inserted_at` 기준 visibility를 적용할 때 사용한다.

source 원래 timestamp는 `source_event_time`으로 보존한다. adapter는 source별 time mapping 정책에 따라 canonical `event_time`을 계산한다.

`check_clock()`은 source server가 제공하는 현재 시각을 읽고 Drift Server 기준 시각(`reference_time`)과 비교한다. 이 작업은 row fetch와 독립적으로 주기 실행할 수 있어야 한다.

## 4. SourceRow Output Contract

`fetch()`는 normalized SourceRow 목록을 반환한다.

```json
{
  "sourceId": "case-010",
  "eventTime": "2026-01-01T00:01:00Z",
  "sourceEventTime": "2025-12-31T23:59:00Z",
  "insertedAt": "2026-06-29T12:00:01Z",
  "sourceClockOffsetMs": 120000,
  "features": {
    "metric": 0.42
  },
  "payload": {}
}
```

필드:

```text
sourceId:
  data source id

eventTime:
  Drift Server 내부 canonical event time

sourceEventTime:
  source data가 원래 가진 발생 시간

insertedAt:
  source DB에 row가 들어온 시각. 없는 source에서는 null 가능

sourceClockOffsetMs:
  canonical eventTime과 sourceEventTime의 차이. 모르면 null 가능

features:
  feature_id -> normalized value

payload:
  원본 row 또는 추가 metadata
```

## 5. available_time()

`available_time()`은 source에서 현재 처리 가능한 최대 canonical `event_time`을 반환한다.

테스트 DB 예:

```sql
select max(event_time)
from test_source.raw_event
where source_id = :source_id
```

`visible_at` 기준을 적용해야 하는 source라면 다음처럼 제한할 수 있다.

```sql
select max(event_time)
from test_source.raw_event
where source_id = :source_id
  and inserted_at <= :visible_at
```

available_time은 catch-up에서 사용한다.

## 5.1 check_clock()

`check_clock()`은 source server clock과 Drift Server 기준 clock의 차이를 측정한다.

입력:

```text
source_config:
  source 접속 정보와 server time 조회 방법

reference_time:
  Drift Server 또는 Harness가 사용하는 현재 canonical 기준 시각
```

출력:

```json
{
  "sourceServerTime": "2026-01-01T00:08:00Z",
  "referenceTime": "2026-01-01T00:10:00Z",
  "sourceClockOffsetMs": 120000,
  "clockStatus": "ok",
  "clockErrorCode": null,
  "checkedAt": "2026-01-01T00:10:00Z"
}
```

계산식:

```text
sourceClockOffsetMs = referenceTime - sourceServerTime
```

정책:

```text
check_clock은 row가 들어오지 않아도 정기적으로 실행한다.
check_clock 결과는 adapter_state에 저장한다.
abs(sourceClockOffsetMs) > maxAllowedClockOffsetMs이면 adapter를 error 상태로 전환한다.
clock 오류 상태에서는 fetch/poll을 진행하지 않는다.
```

## 6. Time Mapping

SourceAdapter는 source별 시간 차이를 흡수해 Drift Server 내부 canonical time으로 변환한다.

기본 mode:

```text
운영 기본:
  observed_offset

테스트/데모 기본:
  harness_logical_time
```

입력 후보:

```text
source timestamp column
source timezone
configured clock offset
server received time
inserted_at
Harness logicalNow
```

출력:

```text
eventTime:
  Drift Server 내부 처리 기준 시간

sourceEventTime:
  source 원래 발생 시간

sourceClockOffsetMs:
  eventTime - sourceEventTime
```

### 6.1 Offset 계산 책임

adapter는 다음 중 하나의 방식으로 `eventTime`과 `sourceClockOffsetMs`를 결정해야 한다.

```text
configured:
  source_config.timeMapping.clockOffsetMs를 그대로 사용한다.

observed:
  source_event_time과 adapter/server 관측 시각의 차이를 row별로 계산한다.

source_provided:
  source가 제공한 server time, ingest time, sequence time을 사용한다.

hybrid:
  configured offset을 기본값으로 쓰고, observed offset이 허용 범위를 벗어나면 clock 오류로 처리한다.
```

계산식:

```text
sourceClockOffsetMs = eventTime - sourceEventTime
```

`sourceEventTime`이 없거나 신뢰할 수 없을 때:

```text
fixed_offset, observed_offset, harness_logical_time처럼 sourceEventTime이 필요한 mode:
  SourceAdapterClockError 발생
  clock_error_code = SOURCE_EVENT_TIME_MISSING

source_ingest_time처럼 sourceEventTime이 없어도 되는 mode:
  sourceEventTime = null
  sourceClockOffsetMs = null
  eventTime = ingest/server time 기준으로 생성
  payload.timeDiagnostics에 sourceEventTime missing 이유 기록
```

### 6.2 timeMapping mode

#### fixed_offset

source별 clock offset을 설정으로 고정한다.

```text
eventTime = sourceEventTime + clockOffsetMs
sourceClockOffsetMs = clockOffsetMs
```

사용 조건:

```text
source clock 차이를 운영자가 알고 있음
source clock drift가 작음
source timestamp를 분석용으로 신뢰할 수 있음
```

#### observed_offset

adapter가 row를 관측한 시각으로 offset을 계산한다.

```text
observedAt = adapter가 row를 fetch/receive한 canonical 시각
eventTime = observedAt
sourceClockOffsetMs = observedAt - sourceEventTime
```

사용 조건:

```text
source timestamp는 보존하되 내부 처리는 수신 시각 기준으로 하고 싶음
source별 clock skew를 진단하고 싶음
```

#### source_ingest_time

source가 제공하는 ingest/created_at/server_time을 canonical time으로 사용한다.

```text
eventTime = sourceIngestTime + optionalClockOffsetMs
sourceEventTime이 있으면 sourceClockOffsetMs = eventTime - sourceEventTime
sourceEventTime이 없으면 sourceClockOffsetMs = null
```

사용 조건:

```text
source_event_time보다 source의 ingest/server time이 더 안정적임
source DB에 inserted_at 또는 server_time 컬럼이 있음
source_event_time이 없는 source를 명시적으로 허용해야 함
```

#### harness_logical_time

테스트/데모에서 Harness logicalNow를 canonical time으로 사용한다.

```text
eventTime = logicalNow 또는 replay interval 내 canonical time
sourceClockOffsetMs = eventTime - sourceEventTime
```

사용 조건:

```text
테스트 재현성 우선
CSV timestamp와 내부 처리 시간을 분리해 검증
```

#### custom_adapter_mapping

adapter별 함수가 canonical time을 계산한다.

```text
eventTime = adapter-specific mapping(source row, source config, observedAt)
sourceClockOffsetMs = eventTime - sourceEventTime
```

사용 조건:

```text
source별 timestamp 구조가 복잡함
sequence number, partition offset, batch timestamp 등을 함께 고려해야 함
```

### 6.3 Offset 오류 처리

adapter는 payload 또는 diagnostics에 시간 보정 결과를 남길 수 있다. 단, clock offset이 허용 범위를 넘는 경우는 row 단위 invalid나 단순 경고가 아니다. 이 경우 source 시간 mapping 자체를 신뢰할 수 없으므로 adapter를 사용할 수 없는 상태로 처리한다.

권장 payload:

```json
{
  "timeDiagnostics": {
    "timeMappingMode": "observed_offset",
    "sourceEventTimePresent": true,
    "sourceClockOffsetMs": 120000,
    "offsetConfidence": "observed",
    "clockStatus": "ok",
    "clockErrorCode": null,
    "observedAt": "2026-01-01T00:10:00Z"
  }
}
```

중단 조건:

```text
abs(sourceClockOffsetMs) > configured maxAllowedClockOffsetMs
selected timeMapping mode에서 필요한 sourceEventTime이 없음
```

미래 데이터 처리:

```text
adapter는 source row를 canonical eventTime으로 먼저 변환한다.
변환된 eventTime이 현재 collector_tick_time 또는 visible_at보다 미래이면 그 row는 아직 사용하지 않는다.
미래 row는 invalid가 아니며 adapter 오류도 아니다.
해당 row는 나중에 collector_tick_time이 eventTime에 도달한 뒤 처리 대상이 된다.
```

중단 처리:

```text
SourceAdapterClockError 발생
error code = CLOCK_OFFSET_EXCEEDED 또는 SOURCE_EVENT_TIME_MISSING
source_adapter.status = error
adapter_state.last_error 저장
adapter_state.clock_status = error
adapter_state.clock_error_code 저장
adapter_state.last_source_clock_offset_ms 저장
fetch 결과를 성공 row로 반환하지 않음
DriftCollector는 bucket/method_run/drift_event를 만들지 않음
adapter_state.source_cursor_time은 전진하지 않음
```

source_config 예:

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
    "roundTo": "1m",
    "offsetConfidence": "configured_default"
  }
}
```

v1 테스트 adapter는 `timeMapping.mode = harness_logical_time`을 기본으로 한다. CSV timestamp를 `sourceEventTime`으로 보존하고, Harness logicalNow 또는 logicalNow 기반 replay time을 canonical `eventTime`으로 사용한다.

## 7. Feature Extraction

feature metadata는 `drift_server.source_feature`에 저장한다.

```text
source_id
feature_id
value_type
payload_path
enabled
```

adapter는 `payload_path`를 사용해 raw payload에서 feature 값을 추출한다.

예:

```text
payload_path = $.metric
```

v1에서는 JSONPath 전체 구현이 필요하지 않다. `$.metric`처럼 단순 top-level key만 지원해도 된다.

## 8. Aggregation Rule

aggregation은 DriftCollector가 수행한다.

numeric feature aggregation:

```text
row_count
mean_value
min_value
max_value
stddev_value
payload_json
```

bucket 구간:

```text
bucket_start = start_time
bucket_end = end_time
resolution = aggregate_interval. v1 default = 10m
```

bucket 구간은 canonical `event_time` 기준이다. source 원래 시간은 bucket payload에 요약 metadata로 남길 수 있다.

빈 window:

```text
row_count = 0
status = empty
```

정상 window:

```text
row_count > 0
status = ok
```

## 9. Invalid / Null Value 처리

v1 정책:

```text
feature value가 null이면 aggregation에서 제외한다.
numeric feature인데 숫자로 변환할 수 없으면 invalid count에 포함하고 aggregation에서 제외한다.
모든 row가 null/invalid면 empty가 아니라 status = invalid 또는 no_valid_value로 저장한다.
```

권장 bucket payload:

```json
{
  "rawRowCount": 10,
  "validValueCount": 8,
  "nullValueCount": 1,
  "invalidValueCount": 1
}
```

bucket row_count는 valid numeric value count로 둔다.

```text
row_count = validValueCount
```

## 10. v1 Adapter: test_db_numeric_stream

v1 adapter:

```text
adapter_type = test_db_numeric_stream
source table = test_source.raw_event
feature = metric
payload_path = $.metric
```

source_config 예:

```json
{
  "table": "test_source.raw_event",
  "timeColumn": "event_time",
  "sourceTimeColumn": "source_event_time",
  "insertedAtColumn": "inserted_at",
  "payloadColumn": "payload_json",
  "timeMapping": {
    "mode": "harness_logical_time"
  },
  "features": [
    {
      "featureId": "metric",
      "payloadPath": "$.metric",
      "valueType": "numeric"
    }
  ]
}
```

fetch query:

```sql
select source_id, event_time, source_event_time, inserted_at, source_clock_offset_ms, payload_json
from test_source.raw_event
where source_id = :source_id
  and event_time >= :start_time
  and event_time < :end_time
  and event_time <= :visible_at
  and inserted_at <= :visible_at
order by event_time asc;
```

normalized output:

```json
{
  "sourceId": "case-010",
  "eventTime": "2026-01-01T00:01:00Z",
  "sourceEventTime": "2026-01-01T00:01:00Z",
  "insertedAt": "2026-06-29T12:00:01Z",
  "sourceClockOffsetMs": 0,
  "features": {
    "metric": 0.42
  },
  "payload": {
    "metric": 0.42
  }
}
```

## 11. Error 처리

adapter fetch 실패:

```text
SourceAdapterError 발생
DriftCollector는 adapter_state.last_error 저장
source_cursor_time은 전진하지 않음
```

source clock offset 허용 범위 초과:

```text
SourceAdapterClockError 발생
source_adapter.status = error
adapter_state.clock_status = error
adapter_state.clock_error_code = CLOCK_OFFSET_EXCEEDED
adapter_state.last_source_clock_offset_ms 저장
source_cursor_time은 전진하지 않음
```

정기 clock check 실패:

```text
source server time 조회 실패면 adapter_state.last_error 저장
clock check에서 허용 범위 초과가 확인되면 source_adapter.status = error
clock_status = error
clock_error_code = CLOCK_OFFSET_EXCEEDED
이 상태에서는 다음 fetch/poll을 진행하지 않음
```

feature extraction 일부 실패:

```text
row 단위 invalidValueCount 증가
adapter fetch 자체는 성공으로 본다.
```

source schema 오류:

```text
필수 column 없음
payload column parse 불가
source_config 오류
```

이 경우 adapter fetch 실패로 처리한다.

## 12. 관련 문서

```text
time_and_cursor_model.md
data_source_event_schema.md
idempotency_and_locking.md
implementation_scope_v1.md
```
