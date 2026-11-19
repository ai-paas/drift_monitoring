# Drift Server Data Source / Event Table Schema

## 1. 목적

이 문서는 `drift_server`에서 data source와 연결된 adapter, bucket, drift method 실행, drift event, analysis chart 등록 테이블의 관계를 정리한다.

핵심 흐름은 다음이다.

```text
data_source
  -> source_adapter
  -> adapter_state
  -> source_feature
  -> metric_bucket
  -> source_method_assignment
  -> method_state
  -> method_run
  -> drift_event
  -> analysis_chart_registration
  -> chart_payload_adapter
```

`drift_method`, `algorithm_variant`, `method_variant`, `algorithm_implementation`, `chart_definition` 등 drift method와 chart catalog의 원본 정보는 `drift 보고서` DB가 source of truth다. `drift_server`의 테이블은 source별 실행 상태와 실행 결과를 저장한다.

## 2. 주요 엔티티 관계

```text
drift_server.data_source
  1:N drift_server.source_adapter
  1:N drift_server.source_feature

drift_server.source_adapter
  1:1 drift_server.adapter_state
  1:N drift_server.metric_bucket

drift_server.data_source
  1:N drift_server.source_method_assignment

drift_server.source_method_assignment
  N:1 drift 보고서 DB.method_variant
  N:1 drift 보고서 DB.algorithm_implementation
  1:1 drift_server.method_state
  1:N drift_server.method_run
  1:N drift_server.analysis_chart_registration

drift_server.method_run
  0:N drift_server.drift_event

drift_server.drift_event
  N:1 drift_server.data_source
  N:1 drift_server.source_adapter
  N:1 drift_server.source_method_assignment
  N:1 drift_server.method_run

drift_server.analysis_chart_registration
  N:1 drift_server.source_method_assignment
  N:1 drift 보고서 DB.chart_definition 또는 chart catalog
  N:1 drift_server.chart_payload_adapter
```

## 3. Source Registry

### 3.1 data_source

외부 데이터 소스 또는 테스트 데이터 소스를 등록한다.

```sql
create table drift_server.data_source (
  source_id text primary key,
  source_title text not null,
  source_description text,
  source_type text not null,
  source_url text,
  owner_label text,
  status text not null default 'active',
  source_config_json jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
```

`source_config_json`에는 source별 시간 보정 정책을 포함할 수 있다.

예:

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

시간 정책:

```text
event_time:
  Drift Server 내부 처리 기준 canonical time

source_event_time:
  source 원래 발생 시간

source_clock_offset_ms:
  event_time - source_event_time
```

Sprint 11 dev 구현에서는 test feeder와 adapter config에 다음 field를 사용한다.

```json
{
  "sourceClockOffsetMs": 120000,
  "maxSourceClockOffsetMs": 300000
}
```

해석:

```text
sourceClockOffsetMs:
  logical event_time - source_event_time

maxSourceClockOffsetMs:
  adapter가 허용하는 최대 절대 offset
```

예:

```text
source_id = case-010
source_type = test_db
source_url = 테스트데이터/CASE-010_stream_numeric_mean_shift/data.csv.gz
```

### 3.2 source_adapter

data source에서 데이터를 가져오는 adapter를 등록한다. 하나의 source에 여러 adapter가 붙을 수 있다.

```sql
create table drift_server.source_adapter (
  adapter_id text primary key,
  source_id text not null references drift_server.data_source(source_id),
  adapter_type text not null,
  adapter_title text,
  source_config_json jsonb not null default '{}'::jsonb,
  collection_interval_minutes integer not null default 10,
  aggregate_interval_minutes integer not null default 10,
  status text not null default 'stopped',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
```

### 3.3 adapter_state

adapter의 logical cursor와 실행 상태를 저장한다.

```sql
create table drift_server.adapter_state (
  adapter_id text primary key references drift_server.source_adapter(adapter_id),
  source_cursor_time timestamptz,
  available_source_time timestamptz,
  last_poll_started_at timestamptz,
  last_poll_finished_at timestamptz,
  last_success_at timestamptz,
  last_error text,
  clock_status text not null default 'unknown',
  clock_error_code text,
  last_source_clock_offset_ms bigint,
  min_source_clock_offset_ms bigint,
  max_source_clock_offset_ms bigint,
  avg_source_clock_offset_ms double precision,
  offset_sample_count bigint not null default 0,
  last_clock_check_at timestamptz,
  last_source_server_time timestamptz,
  last_clock_reference_time timestamptz,
  updated_at timestamptz not null default now()
);
```

`source_cursor_time`은 다음 poll에서 읽을 시작 시각이다. 정상 poll에서는 항상 `source_cursor_time`부터 aggregate interval window 하나만 처리한다. v1 기본값은 10분이다.

clock 오류 정책:

```text
abs(source_clock_offset_ms) > maxAllowedClockOffsetMs이면 adapter는 사용 불가 상태다.
source_event_time이 필요한 mode에서 source_event_time이 없으면 adapter는 사용 불가 상태다.
이 경우 source_adapter.status = error로 전환한다.
adapter_state.clock_status = error
adapter_state.clock_error_code = CLOCK_OFFSET_EXCEEDED 또는 SOURCE_EVENT_TIME_MISSING
adapter_state.last_source_clock_offset_ms에 마지막 측정 offset을 저장한다.
adapter_state.last_error에 상세 원인을 저장한다.
adapter_state.source_cursor_time은 전진하지 않는다.
```

Sprint 11 dev SQLite 구현에서는 `adapter_state.status = 'unusable'`로 저장하고,
`diagnostics_json`에 다음 값을 기록한다.

```json
{
  "code": "SOURCE_CLOCK_OFFSET_TOO_LARGE",
  "maxSourceClockOffsetMs": 300000,
  "maxObservedSourceClockOffsetMs": 1800000,
  "rowCount": 0,
  "unusable": true
}
```

clock check 저장 정책:

```text
adapter는 row fetch와 별개로 source server time을 정기적으로 조회한다.
source_clock_offset_ms = last_clock_reference_time - last_source_server_time
last_clock_check_at에 측정 시각을 저장한다.
last_source_server_time에 source가 반환한 server time을 저장한다.
last_clock_reference_time에 비교 기준으로 사용한 Drift Server/Harness 시간을 저장한다.
min/max/avg_source_clock_offset_ms와 offset_sample_count는 최근 offset 요약이다.
```

### 3.4 source_feature

data source에서 drift 감지와 시계열 UI에 노출할 feature metadata를 저장한다.

```sql
create table drift_server.source_feature (
  source_id text not null references drift_server.data_source(source_id),
  feature_id text not null,
  feature_label text not null,
  value_type text not null,
  unit text,
  payload_path text,
  enabled boolean not null default true,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  primary key (source_id, feature_id)
);
```

`payload_path`는 adapter가 raw event payload에서 값을 추출할 때 사용할 경로다. 예:

```text
payload_path = $.metric
```

초기 구현에서는 source 등록 또는 adapter 등록 시 feature를 명시적으로 등록한다. 이후에는 adapter가 raw event schema를 보고 feature 후보를 자동 발견하는 방식도 추가할 수 있다.

### 3.5 Test Source Schema

테스트 모드에서는 `test_source` schema가 외부 source를 흉내낸다.

#### 3.5.1 test_source.raw_event

```sql
create table test_source.raw_event (
  raw_event_id text primary key,
  source_id text not null,
  dataset_case_id text,
  event_time timestamptz not null,
  source_event_time timestamptz,
  source_clock_offset_ms bigint,
  inserted_at timestamptz not null,
  collected_at timestamptz,
  payload_json jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);
```

`event_time`은 테스트 source에서도 Drift Server 내부 canonical time이다.
CSV timestamp 같은 원래 데이터 시간은 `source_event_time`에 보존한다.
`inserted_at`은 test source DB에 row가 보이기 시작한 Harness logicalNow다.
Sprint 11 dev SQLite 구현에서는 같은 의미의 수집 시각을 `collected_at`으로 저장한다.

시간 정규화 정책:

```text
event_time = source_event_time + sourceClockOffsetMs
source_clock_offset_ms = sourceClockOffsetMs
collected_at = row를 수집한 Harness logicalNow
```

future row 정책:

```text
정규화된 event_time이 현재 Harness logicalNow보다 미래이면 해당 row는 bucket/method_run 입력으로 사용하지 않는다.
test feeder는 rejected count를 futureRejectedRows로 노출한다.
```

#### 3.5.2 test_source.feed_state

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

자세한 replay 규칙은 `test_feeder_contract.md`를 따른다.

## 4. Bucket / Feature Data

### 4.1 metric_bucket

adapter가 가져온 raw data를 설정된 resolution 단위로 집계한 결과다. v1 기본값은 10분이다.

bucket 시간은 source 원래 시간이 아니라 canonical `event_time` 기준이다.

```sql
create table drift_server.metric_bucket (
  bucket_id text primary key,
  source_id text not null references drift_server.data_source(source_id),
  adapter_id text not null references drift_server.source_adapter(adapter_id),
  feature_id text not null,
  bucket_start timestamptz not null,
  bucket_end timestamptz not null,
  resolution text not null default '10m',
  row_count integer not null default 0,
  mean_value double precision,
  min_value double precision,
  max_value double precision,
  stddev_value double precision,
  status text not null default 'ok',
  payload_json jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  unique (adapter_id, feature_id, bucket_start, bucket_end, resolution)
);
```

resolution 정책:

```text
v1 기본 resolution = 10m
V2에서 더 촘촘한 ADWIN/online drift가 필요하면 resolution 또는 aggregate_interval_minutes를 줄인다.
raw row 직접 입력 contract를 별도로 만들지 않고 더 작은 bucket stream으로 처리한다.
```

`payload_json`에는 chart나 algorithm이 추가로 필요로 하는 원본 집계값과 source time 요약을 보존한다.

예:

```json
{
  "sourceTime": {
    "minSourceEventTime": "2025-12-31T23:58:00Z",
    "maxSourceEventTime": "2026-01-01T00:08:00Z",
    "minSourceClockOffsetMs": 120000,
    "maxSourceClockOffsetMs": 120000
  }
}
```

## 5. Drift Method Assignment / Run

### 5.1 source_method_assignment

관리자 서버가 source에 drift method를 할당한 정보다.

```sql
create table drift_server.source_method_assignment (
  assignment_id text primary key,
  source_id text not null references drift_server.data_source(source_id),
  adapter_id text references drift_server.source_adapter(adapter_id),
  feature_id text not null,
  method_variant_id bigint not null,
  algorithm_implementation_id bigint,
  runtime_method_key text,
  params_json jsonb not null default '{}'::jsonb,
  threshold_json jsonb not null default '{}'::jsonb,
  window_config_json jsonb not null default '{}'::jsonb,
  enabled boolean not null default true,
  display_order integer not null default 0,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
```

`method_variant_id`와 `algorithm_implementation_id`는 `drift 보고서` DB의 값을 참조한다. 같은 PostgreSQL instance라면 foreign key를 둘 수 있지만, 초기 구현에서는 느슨한 참조로 두어도 된다.

### 5.2 method_state

상태형 drift detector의 내부 상태를 저장한다. ADWIN 같은 streaming detector는 이전 bucket까지의 detector state가 필요하므로 `method_run`만으로는 충분하지 않다.

```sql
create table drift_server.method_state (
  assignment_id text primary key references drift_server.source_method_assignment(assignment_id),
  source_id text not null references drift_server.data_source(source_id),
  adapter_id text references drift_server.source_adapter(adapter_id),
  feature_id text not null,
  state_json jsonb not null default '{}'::jsonb,
  last_bucket_end timestamptz,
  updated_at timestamptz not null default now()
);
```

사용 원칙:

```text
상태형 detector:
  method_state를 읽고 새 bucket을 반영한 뒤 method_state를 갱신한다.

lookback 재계산형 detector:
  method_state를 쓰지 않거나, 마지막 처리 bucket marker만 저장한다.
```

`method_run.result_json`은 실행 결과 기록이고, `method_state.state_json`은 다음 실행에 필요한 detector 내부 상태다. 두 테이블의 목적을 분리한다.

### 5.3 method_run

각 logical window 또는 lookback window에 대한 drift method 실행 결과다.

window_start/window_end는 canonical `event_time` 기준이다.

```sql
create table drift_server.method_run (
  method_run_id text primary key,
  assignment_id text not null references drift_server.source_method_assignment(assignment_id),
  source_id text not null references drift_server.data_source(source_id),
  adapter_id text references drift_server.source_adapter(adapter_id),
  feature_id text not null,
  window_start timestamptz not null,
  window_end timestamptz not null,
  input_bucket_count integer not null default 0,
  run_status text not null,
  score double precision,
  level text,
  started_at timestamptz not null default now(),
  finished_at timestamptz,
  result_json jsonb not null default '{}'::jsonb,
  error_message text,
  unique (assignment_id, window_start, window_end)
);
```

`level`은 method 실행 결과의 판정값이다. 예: `normal`, `warning`, `drift`.

## 6. Drift Event

### 6.1 drift_event

warning 또는 drift 조건을 만족한 사건을 저장한다.

event_start/event_end는 canonical `event_time` 기준이다.

```sql
create table drift_server.drift_event (
  event_id text primary key,
  source_id text not null references drift_server.data_source(source_id),
  adapter_id text references drift_server.source_adapter(adapter_id),
  assignment_id text references drift_server.source_method_assignment(assignment_id),
  method_run_id text references drift_server.method_run(method_run_id),
  feature_id text not null,
  event_start timestamptz not null,
  event_end timestamptz not null,
  level text not null,
  score double precision,
  method_variant_id bigint,
  algorithm_implementation_id bigint,
  event_status text not null default 'open',
  payload_json jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (method_run_id)
);
```

event는 `source_id`, `assignment_id`, `method_run_id`를 통해 어떤 data source의 어떤 drift method 실행에서 발생했는지 추적할 수 있어야 한다.

event 병합 정책:

```text
unique(method_run_id)는 같은 method_run에서 event가 중복 생성되는 것을 막기 위한 제약이다.
서로 다른 method_run에서 생성된 drift_event는 event_start/event_end가 겹쳐도 별도 row로 저장한다.
drift_server는 저장 단계에서 event merge, extend, suppress를 수행하지 않는다.
```

## 7. Analysis Chart / Payload Adapter

### 7.1 analysis_chart_registration

source별 drift method assignment에 연결된 analysis chart 등록 정보다.

```sql
create table drift_server.analysis_chart_registration (
  analysis_chart_id text primary key,
  assignment_id text not null references drift_server.source_method_assignment(assignment_id),
  source_id text not null references drift_server.data_source(source_id),
  chart_id text not null,
  chart_definition_id text,
  chart_definition_json jsonb,
  chart_builder_job_id text,
  payload_adapter_key text not null,
  payload_adapter_config_json jsonb not null default '{}'::jsonb,
  enabled boolean not null default true,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
```

하나의 assignment에 여러 analysis chart를 붙일 수도 있지만, 초기 구현에서는 하나의 assignment에 하나의 기본 analysis chart를 두는 것이 단순하다.

`chart_definition_id`는 chart_builder 쪽 원본 chart definition을 추적하기 위한 ID다.

`chart_definition_json`은 등록 시점의 chart definition snapshot이다. Event analysis API는 기본적으로 이 snapshot을 사용한다. snapshot이 없을 때만 chart_builder에서 `chart_definition_id`로 조회하고, 성공하면 snapshot을 저장한다.

### 7.2 chart_payload_adapter

drift server 데이터에서 chart runtime payload를 만드는 변환 함수 registry다.

```sql
create table drift_server.chart_payload_adapter (
  payload_adapter_key text primary key,
  chart_id text not null,
  method_variant_id bigint,
  algorithm_implementation_id bigint,
  adapter_title text,
  input_contract_json jsonb not null default '{}'::jsonb,
  output_contract_json jsonb not null default '{}'::jsonb,
  status text not null default 'active',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
```

이 테이블은 chart catalog가 아니다. 특정 method/chart 조합에 대해 어떤 code function을 호출할지 알려주는 실행 보조 registry다.

예:

```text
payload_adapter_key = adwin_mean_stream_to_chart_stream_001
chart_id = CHART-STREAM-001
method_variant_id = ADWIN_MEAN_STREAM의 method_variant_id
```

## 8. Event Analysis 조회 흐름

```text
GET /api/sources/{source_id}/events/{event_id}/analysis
  -> drift_event 조회
  -> source_method_assignment 조회
  -> analysis_chart_registration 조회
  -> chart_definition_json snapshot 조회
  -> snapshot이 없으면 chart_builder에서 chart_definition_id 조회 후 snapshot 저장
  -> chart_payload_adapter 조회
  -> payload_adapter_key로 code function 선택
  -> metric_bucket + method_run + drift_event를 chart payload로 변환
  -> chart definition + chart payload 반환
```

반환 예:

```json
{
  "ok": true,
  "sourceId": "case-010",
  "eventId": "evt-001",
  "assignmentId": "assign-case010-adwin",
  "analysisChartId": "analysis-case010-adwin-stream",
  "chartId": "CHART-STREAM-001",
  "chartDefinitionId": "chartdef-case010-adwin-stream",
  "payloadAdapterKey": "adwin_mean_stream_to_chart_stream_001",
  "chartPayload": {}
}
```

## 9. 최소 인덱스

초기 구현에서 필요한 인덱스는 다음 정도면 충분하다.

```sql
create index on drift_server.source_adapter (source_id);
create index on drift_server.source_feature (source_id, enabled);
create index on drift_server.metric_bucket (source_id, feature_id, bucket_start);
create index on drift_server.metric_bucket (adapter_id, feature_id, bucket_start);
create index on drift_server.source_method_assignment (source_id, enabled);
create index on drift_server.method_state (source_id, feature_id, last_bucket_end);
create index on drift_server.method_run (assignment_id, window_end);
create index on drift_server.method_run (source_id, feature_id, window_end);
create index on drift_server.drift_event (source_id, event_end);
create index on drift_server.drift_event (assignment_id, event_end);
create index on drift_server.analysis_chart_registration (assignment_id, enabled);
create index on drift_server.chart_payload_adapter (chart_id, status);
```

## 10. 초기 구현 원칙

1. `data_source`는 외부 원천을 설명한다.
2. `source_adapter`는 데이터를 가져오는 실행 단위다.
3. `source_feature`는 source에서 drift 감지와 UI에 사용할 feature metadata를 저장한다.
4. `metric_bucket`은 drift server가 소유하는 bucket 집계 결과다. v1 기본 resolution은 10분이다.
5. `source_method_assignment`는 source에 어떤 drift method를 적용할지 저장한다.
6. `method_state`는 상태형 detector의 다음 실행에 필요한 내부 상태를 저장한다.
7. `method_run`은 drift method 실행 로그와 결과다.
8. `drift_event`는 warning/drift로 노출할 사건이다.
9. `analysis_chart_registration`은 event 분석에 사용할 chart를 assignment 단위로 연결한다.
10. `chart_payload_adapter`는 chart payload 변환 함수 registry다.
11. drift method와 chart catalog 원본은 `drift 보고서` DB에 둔다.
