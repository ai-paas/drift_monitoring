# Drift Server 데이터 소스 UI 및 API 구조

## 1. 목적

`drift_server`는 여러 데이터 소스에서 수집한 10분 단위 집계 데이터를 저장하고, 사용자가 데이터 소스별 시계열을 확인할 수 있는 화면과 API를 제공한다.

사용자는 drift server의 데이터 소스 목록 화면에서 등록된 source를 확인하고, 특정 source를 선택해 해당 source의 drift metric time-series chart를 연다.

## 2. 핵심 화면

### 2.1 데이터 소스 목록 화면

역할:

```text
drift_server에 등록된 데이터 소스 목록을 보여준다.
각 데이터 소스의 제목, 설명, URL, adapter 상태, 마지막 수집 시각, 최근 bucket 수, 최근 drift event 수를 보여준다.
데이터 소스를 클릭하면 해당 source의 시계열 chart 화면으로 이동한다.
```

예시 URL:

```text
/sources
```

표시 항목:

```text
source title
source id
source type
source URL
adapter status
last collected logical time
last poll real time
10분 bucket count
warning/drift event count
open chart link
```

### 2.2 데이터 소스별 시계열 화면

역할:

```text
선택한 데이터 소스의 10분 집계 데이터를 시계열 chart로 보여준다.
chart는 drift_metric_timeseries UI를 사용한다.
기본적으로 drift_server가 저장한 10분 bucket을 조회한다.
UI는 10분 간격으로 업데이트된 데이터를 가져와 화면을 갱신한다.
warning/drift event가 있으면 marker 또는 band로 표시한다.
```

예시 URL:

```text
/sources/{source_id}/timeseries
```

이 화면은 source별 고유 URL을 가진다. 사용자가 URL을 직접 열면 해당 source의 시계열 chart가 바로 나타나야 한다.

## 3. 데이터 흐름

```text
외부 데이터 소스 또는 테스트 DB
  -> SourceAdapter
  -> DriftCollector
  -> 10분 bucket 집계
  -> drift_server DB 저장
  -> source에 할당된 drift method 실행
  -> drift event 저장
  -> drift_metric_timeseries API
  -> source별 시계열 chart 화면
```

## 3.1 Drift Method 할당 흐름

관리자 서버는 데이터 소스별로 사용할 drift method를 지정한다.

하나의 데이터 소스에는 drift method를 0개, 1개, 또는 여러 개 할당할 수 있다.

```text
관리자 화면
  -> 데이터 소스 선택
  -> 사용할 drift method/variant 선택
  -> method별 parameter/threshold/window 설정
  -> method에 연결할 analysis chart 선택
  -> chart_builder로 chart definition 생성
  -> chart payload adapter 선택 또는 자동 매핑
  -> drift_server에 assignment 저장 요청
```

drift server는 미리 사용 가능한 drift method catalog와 구현체를 가지고 있다. 관리자 서버가 특정 source에 method를 할당하면, drift server는 해당 source의 새 10분 bucket이 생성될 때 할당된 method들을 실행한다.

```text
10분 bucket 저장
  -> source_method_assignment 조회
  -> method A 실행
  -> method B 실행
  -> method C 실행
  -> 각 method result 저장
  -> warning/drift 조건이면 drift_event 등록
```

중요한 책임 구분:

```text
관리자 서버
  어떤 source에 어떤 drift method를 쓸지 정한다.

drift server
  등록된 method 구현체를 보유한다.
  source별 assignment를 조회한다.
  bucket이 쌓이면 method를 실행한다.
  결과가 warning/drift이면 event를 생성한다.
```

관리자 서버가 drift 알고리즘을 직접 실행하지 않는다.

## 3.2 Analysis Chart 등록 흐름

drift event를 분석할 때 사용할 chart는 event 발생 시점에 임의로 새로 고르지 않는다. 관리자 서버가 source별 drift method assignment를 만들 때, 해당 method에 사용할 analysis chart도 함께 등록한다.

chart 목록도 `drift 보고서` DB에 미리 등록된 목록을 기준으로 한다. 관리자 서버는 선택한 drift method/variant에 연결 가능한 chart만 보여주고, 사용자가 "차트 생성"을 누르면 `chart_builder`를 호출해 chart definition을 만든다.

이때 chart definition만 등록하면 부족하다. drift server가 저장한 source bucket, method result, drift event 데이터를 해당 chart runtime이 읽을 수 있는 `payload`로 변환하는 함수도 함께 등록되어야 한다.

```text
관리자 서버
  -> source 선택
  -> drift method/variant 선택
  -> 연결 가능한 chart 목록 조회
  -> chart 생성 요청
  -> chart_builder가 chart definition 생성
  -> chart payload adapter 선택/등록
  -> drift_server에 source_method_assignment + analysis_chart_registration 저장
```

등록 단위는 다음 관계를 가진다.

```text
data source
  -> source_method_assignment
      -> drift method/variant
      -> analysis_chart_registration
          -> chart_definition_id
          -> payload_adapter_key
```

`payload_adapter_key`는 drift server 코드에서 실제 변환 함수를 찾기 위한 안정 key다. 이 함수는 다음 입력을 받아 chart runtime payload를 만든다.

```text
입력:
  source metadata
  source metric buckets
  method run/result
  drift event
  chart definition metadata

출력:
  chart_runtime이 렌더링할 수 있는 chart payload
```

따라서 event analysis 요청은 다음 순서로 처리된다.

```text
GET /api/sources/{source_id}/events/{event_id}/analysis
  -> drift_event 조회
  -> event의 assignment 조회
  -> assignment의 analysis_chart_registration 조회
  -> payload_adapter_key로 변환 함수 선택
  -> bucket/method_result/event 데이터를 chart payload로 변환
  -> chart definition + payload 반환
```

시계열 UI에서는 drift event가 왼쪽 목록 또는 event 패널에 표시되고, 그 아래에 등록된 analysis chart 링크가 표시된다. 사용자가 링크를 누르면 drift server가 위 과정을 통해 생성한 payload를 반환하고, chart runtime이 해당 분석 chart를 렌더링한다.

## 4. 데이터 소스 저장 모델

drift server는 데이터 소스 자체의 metadata와 source별 수집 결과를 모두 저장한다.

### 4.1 source registry

```sql
drift_server.data_source
  source_id text primary key
  source_title text
  source_description text
  source_type text
  source_url text
  status text
  source_config_json jsonb
  created_at timestamptz
  updated_at timestamptz
```

`source_url`은 사용자가 source를 식별하거나 외부 원천 위치를 확인하기 위한 URL이다. 테스트 데이터인 경우에는 파일 경로나 테스트 서버 URL이 들어갈 수 있다.

`data_source`에는 `adapter_id`를 두지 않는다. 하나의 data source에 여러 adapter가 붙을 수 있으므로, adapter는 `source_adapter.source_id`로 source를 참조한다.

### 4.2 source metric bucket

```sql
drift_server.metric_bucket
  source_id text
  adapter_id text
  feature_id text
  bucket_start timestamptz
  bucket_end timestamptz
  resolution text              -- 기본 10m
  count integer
  mean_value double precision
  min_value double precision
  max_value double precision
  status text
  payload_json jsonb
```

`bucket_start`와 `bucket_end`는 Drift Server 내부 canonical event_time 기준이다.
source 원래 발생 시간은 별도 source_event_time 또는 bucket payload 요약으로 보존한다.

### 4.3 source event

```sql
drift_server.drift_event
  event_id text primary key
  source_id text
  adapter_id text
  feature_id text
  event_start timestamptz
  event_end timestamptz
  level text                   -- normal, warning, drift
  score double precision
  method_code text
  variant_code text
  chart_code text
  payload_json jsonb
```

### 4.4 drift method runtime key

drift 알고리즘 목록은 이미 `drift 보고서` DB에 등록되어 있다. 따라서 관리자 서버와 drift server는 별도 독립 목록을 새로 만들지 않고, `drift 보고서` DB의 catalog를 기준으로 method를 선택한다.

기준 테이블:

```text
drift_method
algorithm_variant
method_variant
algorithm_implementation
```

관리자 서버의 method 선택 UI는 이 DB를 조회해 구성한다.

drift server는 같은 DB의 `algorithm_implementation` 또는 이에 대응하는 runtime registry를 보고 runtime wrapper를 찾는다. 이 wrapper는 `drift_algorithm_impl`의 기존 알고리즘 구현을 호출하고 Drift Server 표준 input/output contract로 변환한다.

1차 구현에서는 별도 `drift_method_runtime` 테이블을 만들지 않는다. 실행 함수는 drift server 코드의 runtime registry에서 `runtime_method_key`로 찾는다.

```python
RUNTIME_METHODS = {
    "adwin_mean_stream": run_adwin_mean_stream,
}
```

`runtime_method_key`는 drift server 코드에서 runtime wrapper를 찾기 위한 안정 key다. Drift Server는 ADWIN 같은 drift 알고리즘 자체를 새로 구현하지 않는다.

원칙:

```text
method/variant의 source of truth = drift 보고서 DB
실행 가능 여부 = algorithm_implementation + drift server runtime registry
관리자 서버는 DB에 등록된 method/variant만 선택 가능
source_method_assignment는 method_variant_id, algorithm_implementation_id, runtime_method_key를 함께 저장
```

### 4.5 source별 method assignment

관리자 서버가 데이터 소스에 drift method를 지정하면 이 테이블에 저장한다.

```sql
drift_server.source_method_assignment
  assignment_id text primary key
  source_id text
  adapter_id text
  feature_id text
  method_variant_id bigint
  algorithm_implementation_id bigint
  runtime_method_key text
  params_json jsonb
  threshold_json jsonb
  window_config_json jsonb
  enabled boolean
  display_order integer
  created_at timestamptz
  updated_at timestamptz
```

하나의 source에 여러 assignment가 있을 수 있다.

예:

```text
source_id = case-010
  assignment 1: ADWIN_MEAN_STREAM on feature metric
  assignment 2: CUSUM_UPPER on feature metric
  assignment 3: EWMA_ONE_SIDED on feature metric
```

### 4.6 source method별 analysis chart 등록

관리자 서버가 chart_builder를 통해 생성한 analysis chart와 payload 변환 함수를 저장한다.

```sql
drift_server.analysis_chart_registration
  analysis_chart_id text primary key
  assignment_id text
  source_id text
  chart_id text
  chart_definition_id text
  chart_builder_job_id text
  payload_adapter_key text
  payload_adapter_config_json jsonb
  enabled boolean
  created_at timestamptz
  updated_at timestamptz
```

`chart_id`는 `drift 보고서` DB의 chart catalog에 등록된 chart code 또는 chart definition 식별자를 가리킨다.

`chart_definition_id`는 chart_builder가 생성한 구체 chart definition을 가리킨다.

`payload_adapter_key`는 drift server의 adapter registry에서 실제 payload 변환 함수를 찾기 위한 key다.

초기 구현에서 payload adapter registry가 필요하면 다음처럼 둔다.

```sql
drift_server.chart_payload_adapter
  payload_adapter_key text primary key
  chart_id text
  method_variant_id bigint
  algorithm_implementation_id bigint
  input_contract_json jsonb
  output_contract_json jsonb
  status text
```

이 테이블도 chart catalog의 source of truth가 아니다. 어떤 chart와 method 조합에 어떤 변환 함수를 쓸 수 있는지 알려주는 실행 보조 정보다.

### 4.7 method run/result

각 bucket 또는 window에 대해 method 실행 결과를 저장한다.

```sql
drift_server.method_run
  method_run_id text primary key
  assignment_id text
  source_id text
  feature_id text
  window_start timestamptz
  window_end timestamptz
  run_status text
  started_at timestamptz
  finished_at timestamptz
  result_json jsonb
  error_message text
```

결과가 event 조건을 만족하면 `drift_event`를 생성한다.

## 5. Drift Server API 초안

### 5.1 데이터 소스 목록

```text
GET /api/sources
```

응답 예:

```json
{
  "ok": true,
  "sources": [
    {
      "sourceId": "case-010",
      "title": "CASE-010 stream numeric mean shift",
      "sourceType": "test_db",
      "sourceUrl": "테스트데이터/CASE-010_stream_numeric_mean_shift/data.csv.gz",
      "adapterId": "case-010-adwin",
      "adapterStatus": "running",
      "lastCollectedTime": "2026-07-01T00:10:00Z",
      "lastPollTime": "2026-06-29T12:00:10Z",
      "bucketCount": 144,
      "warningCount": 2,
      "driftCount": 1,
      "timeseriesUrl": "/sources/case-010/timeseries"
    }
  ]
}
```

### 5.2 데이터 소스 상세

```text
GET /api/sources/{source_id}
```

후속 목표 API다. 현재 v1 dev runtime에서는 별도 구현하지 않고 `/api/sources/{source_id}/timeseries-data` 응답의 `sourceId`, `modelId`, `features` field를 사용한다.

### 5.3 source별 feature metadata

```text
GET /api/sources/{source_id}/features
```

후속 목표 API다. 현재 v1 dev runtime에서는 feature selector metadata가 `/timeseries-data` 응답의 `features` field에 포함된다.

### 5.3.1 source별 drift method assignment

```text
GET /api/sources/{source_id}/method-assignments
POST /api/sources/{source_id}/method-assignments
PUT /api/sources/{source_id}/method-assignments/{assignment_id}
DELETE /api/sources/{source_id}/method-assignments/{assignment_id}
```

관리자 서버가 호출하는 API다.

`GET`은 현재 source에 할당된 drift method 목록을 반환한다.

`POST`는 source에 새 drift method를 할당한다.

예:

```json
{
  "methodVariantId": 123,
  "algorithmImplementationId": 45,
  "featureId": "metric",
  "params": {
    "delta": 0.002
  },
  "threshold": {
    "eventLevel": "drift"
  },
  "windowConfig": {
    "bucketResolution": "10m",
    "lookbackBuckets": 144
  },
  "analysisChart": {
    "chartId": "CHART-STREAM-001",
    "chartDefinitionId": "chartdef-case010-adwin-stream",
    "payloadAdapterKey": "adwin_mean_stream_to_chart_stream_001"
  },
  "enabled": true
}
```

### 5.3.2 실행 가능한 drift method 목록

```text
GET /api/drift-methods
```

관리자 서버가 method 선택 UI를 구성할 때 사용한다.

응답은 `drift 보고서` DB에 등록된 method/variant 중 drift server가 실제 실행 가능한 항목만 포함한다.

조회 기준:

```text
drift_method
  -> method_variant
  -> algorithm_variant
  -> algorithm_implementation
```

`algorithm_implementation.status = active`인 항목을 우선 노출한다. 구현체가 아직 없는 method/variant는 관리자 화면에서 비활성 또는 "구현 예정"으로 표시할 수 있다.

### 5.4 source별 시계열 데이터

```text
GET /api/sources/{source_id}/timeseries-data?from=...&to=...&resolution=10m
```

응답은 `drift_metric_timeseries`가 읽기 쉬운 구조로 반환한다.

```json
{
  "ok": true,
  "sourceId": "case-010",
  "modelId": "case-010",
  "features": [],
  "fullDomain": ["2026-01-01T00:00:00Z", "2026-07-01T00:10:00Z"],
  "series": {
    "metric": []
  },
  "events": {
    "metric": []
  },
  "pollIntervalMs": 600000
}
```

테스트 모드에서는 `pollIntervalMs`가 더 짧을 수 있다.

```text
운영 모드: 10분 = 600000ms
테스트 데모 모드: 10초 = 10000ms
```

### 5.5 source별 live update

```text
GET /api/sources/{source_id}/timeseries-live?since=...
```

후속 목표 API다. 현재 v1 dev runtime에서는 UI가 `/timeseries-data`를 반복 조회해 최신 bucket/event 상태를 확인한다.

후속 구현에서는 이 API가 마지막으로 UI가 받은 `bucket_end` 이후의 bucket/event만 반환한다.

### 5.6 event analysis

```text
GET /api/sources/{source_id}/events/{event_id}/analysis
```

선택한 drift event에 대한 analysis chart runtime payload를 반환한다.

응답은 등록된 analysis chart와 payload adapter를 사용해 만든다.

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

## 6. 화면 URL과 API 관계

```text
/sources
  -> 후속 목표: GET /api/sources

/sources/{source_id}/timeseries
  -> GET /api/sources/{source_id}/timeseries-data
  -> 반복 GET /api/sources/{source_id}/timeseries-data
  -> 후속 목표: GET /api/sources/{source_id}
  -> 후속 목표: GET /api/sources/{source_id}/features
  -> 후속 목표: GET /api/sources/{source_id}/timeseries-live

event click
  -> GET /api/sources/{source_id}/events/{event_id}/analysis
  -> registered payload adapter로 chart payload 생성
  -> LLM interpretation server /api/interpret/chart/jobs
```

## 7. 업데이트 주기

drift server는 adapter별로 10분 logical window를 처리한다.

```text
adapter poll
  -> source_cursor_time ~ source_cursor_time + 10분 데이터 조회
  -> 10분 bucket 저장
  -> event 계산
```

UI는 저장된 bucket을 조회한다. UI가 직접 외부 데이터 소스를 읽지 않는다.

```text
drift_metric_timeseries UI
  -> drift_server API
  -> drift_server DB의 bucket/event 조회
```

운영 모드에서는 10분마다 새 bucket이 생기는 것이 기본이다.

테스트 모드에서는 logical 10분이 real 10초로 압축될 수 있으므로, UI poll interval도 테스트 설정에 맞춰 짧아질 수 있다.

## 8. 책임 분리

### drift server가 하는 일

```text
데이터 소스 metadata 저장
adapter 상태 저장
drift 보고서 DB의 drift method/variant/implementation catalog 조회
source별 drift method assignment 저장
source method별 analysis chart registration 저장
registered payload adapter로 event analysis payload 생성
10분 bucket 저장
할당된 drift method 실행
method run/result 저장
drift event 저장
source별 timeseries API 제공
source별 화면 URL 제공
event analysis payload 제공
```

### drift server가 하지 않는 일

```text
관리자 화면에서 source 등록 UI 자체를 소유하지 않음
테스트 CSV를 직접 source처럼 계속 feed하지 않음
LLM 해석을 직접 생성하지 않음
chart runtime 내부 렌더링 로직을 직접 수정하지 않음
```

관리자 서버는 source와 adapter를 등록/실행/중지한다.

관리자 서버는 source별 drift method assignment도 등록/수정/삭제한다.

테스트 feeder는 테스트 데이터를 source DB에 넣는다.

drift server는 등록된 adapter를 통해 source DB 또는 외부 source에서 데이터를 가져와 bucket/event를 만든다.
