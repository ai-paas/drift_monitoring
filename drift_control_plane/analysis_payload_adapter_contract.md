# Analysis Payload Adapter Contract

## 1. 목적

이 문서는 Drift Server가 drift event에 대한 analysis chart payload를 만들 때 사용하는 payload adapter contract를 정의한다.

핵심 결정:

```text
payload adapter는 DB에 직접 접근하지 않는다.
DriftService가 필요한 context를 조회해 payload adapter에 전달한다.
payload adapter는 chart runtime이 읽을 chartPayload만 반환한다.
payload adapter는 chartDefinition을 수정하지 않는다.
```

## 2. 기본 흐름

```text
Event analysis API
  -> drift_event 조회
  -> source_method_assignment 조회
  -> method_run 조회
  -> source/feature/adapter 조회
  -> analysis_chart_registration 조회
  -> chart_definition_json snapshot 조회
  -> 주변 metric_bucket 조회
  -> payload_adapter_key로 adapter function 선택
  -> payload adapter에 context 전달
  -> chartPayload 반환
  -> chartDefinition + chartPayload 응답
```

## 3. Payload Adapter 책임

payload adapter가 하는 일:

```text
analysis context를 chart runtime payload 구조로 변환한다.
chart runtime과 LLM 서버가 읽는 layout, components, data를 만든다.
하위 호환을 위해 필요한 경우 legacy series, event marker, annotation, metadata도 함께 만든다.
method_run.result_json과 drift_event.payload_json을 chart payload에 반영한다.
```

payload adapter가 하지 않는 일:

```text
DB 조회
DB 저장
HTTP 호출
chartDefinition 수정
drift method 실행
LLM 해석 생성
```

## 4. Input Context Contract

표준 입력:

```json
{
  "source": {},
  "adapter": {},
  "feature": {},
  "assignment": {},
  "methodRun": {},
  "methodState": {},
  "driftEvent": {},
  "analysisChart": {},
  "chartDefinition": {},
  "buckets": [],
  "runtimeResult": {},
  "payloadAdapterConfig": {}
}
```

### 4.1 source

```json
{
  "sourceId": "case-010",
  "sourceTitle": "CASE-010 stream numeric mean shift",
  "sourceType": "test_db",
  "sourceUrl": "테스트데이터/CASE-010_stream_numeric_mean_shift/data.csv.gz"
}
```

### 4.2 feature

```json
{
  "featureId": "metric",
  "featureLabel": "Metric",
  "valueType": "numeric",
  "unit": null
}
```

### 4.3 assignment

```json
{
  "assignmentId": "assign-case010-adwin",
  "methodVariantId": 123,
  "algorithmImplementationId": 45,
  "runtimeMethodKey": "adwin_mean_stream",
  "params": {},
  "threshold": {},
  "windowConfig": {}
}
```

### 4.4 methodRun

```json
{
  "methodRunId": "run-001",
  "windowStart": "2026-01-01T00:00:00Z",
  "windowEnd": "2026-01-01T00:10:00Z",
  "runStatus": "success",
  "level": "drift",
  "score": 0.91,
  "result": {}
}
```

### 4.5 driftEvent

```json
{
  "eventId": "evt-001",
  "eventStart": "2026-01-01T00:00:00Z",
  "eventEnd": "2026-01-01T00:10:00Z",
  "level": "drift",
  "score": 0.91,
  "payload": {}
}
```

### 4.6 analysisChart

```json
{
  "analysisChartId": "analysis-case010-adwin-stream",
  "chartId": "CHART-STREAM-001",
  "chartDefinitionId": "chartdef-case010-adwin-stream",
  "payloadAdapterKey": "adwin_mean_stream_to_chart_stream_001"
}
```

### 4.7 chartDefinition

`chartDefinition`은 `analysis_chart_registration.chart_definition_json` snapshot에서 온다.

DriftService는 Chart Builder 서버를 직접 호출하지 않는다. snapshot이 없으면 event analysis context가 불완전한 것으로 처리하고, 등록 단계에서 snapshot을 보강해야 한다.

payload adapter는 이 값을 수정하지 않는다.

### 4.8 buckets

event analysis에 사용할 주변 bucket 목록이다.

정렬:

```text
bucket_start 오름차순
```

예:

```json
[
  {
    "bucketStart": "2026-01-01T00:00:00Z",
    "bucketEnd": "2026-01-01T00:10:00Z",
    "v": 0.42,
    "count": 10,
    "status": "ok",
    "payload": {}
  }
]
```

### 4.9 runtimeResult

`method_run.result_json`을 정규화한 값이다.

권장 구조:

```json
{
  "metrics": {},
  "diagnostics": {},
  "payloadHints": {},
  "event": {}
}
```

### 4.10 payloadAdapterConfig

`analysis_chart_registration.payload_adapter_config_json` 값이다.

chart별 window, baseline, annotation 옵션을 넣을 수 있다.

## 5. Output Contract

payload adapter는 chart runtime payload를 반환한다.

```json
{
  "chartId": "CHART-STREAM-001",
  "title": "CASE-011 ADWIN stream analysis",
  "sourceId": "case-010",
  "eventId": "evt-001",
  "featureId": "metric",
  "layout": {
    "areas": []
  },
  "components": [],
  "data": {},
  "series": [],
  "eventMarkers": [],
  "annotations": [],
  "metadata": {}
}
```

필드:

```text
chartId:
  target chart id

sourceId/eventId/featureId:
  trace metadata

layout:
  chart runtime이 component를 배치할 area 목록

components:
  chart runtime과 LLM 서버가 해석할 component instance 목록

data:
  component dataBinding.source가 참조하는 row set

series:
  legacy chart consumer 호환용 primary data series

eventMarkers:
  legacy chart consumer 호환용 drift event marker

annotations:
  legacy chart consumer 호환용 threshold, detected region, baseline/current range 등

metadata:
  method, score, diagnostics, display hints
```

`layout/components/data`가 canonical output이다. `series/eventMarkers/annotations`는 Sprint 10 기준으로 유지하지만 신규 chart runtime이나 LLM 연동은 이 legacy field에 의존하지 않는다.

## 6. Bucket Window 선택

DriftService가 payload adapter 호출 전에 bucket window를 선택한다.

기본 정책:

```text
event_end 기준 앞뒤 window를 조회한다.
lookbackBuckets는 assignment.window_config_json을 우선 사용한다.
없으면 v1 기본 144 buckets를 사용한다.
```

v1 기본:

```text
before = 144 buckets
after = 0 buckets
```

후속:

```text
event 이후 N buckets 포함
baseline/current range 지정
chart별 bucket window config
```

## 7. v1 Adapter: adwin_mean_stream_to_chart_stream_001

v1 payload adapter:

```text
payload_adapter_key = adwin_mean_stream_to_chart_stream_001
chart_id = CHART-STREAM-001
method = ADWIN_MEAN_STREAM
```

입력:

```text
source
feature = metric
methodRun.result.metrics
driftEvent.payload
buckets around event
chartDefinition snapshot
```

출력:

```json
{
  "chartId": "CHART-STREAM-001",
  "title": "CASE-010 ADWIN stream analysis",
  "sourceId": "case-010",
  "eventId": "evt-001",
  "featureId": "metric",
  "layout": {
    "areas": [
      {"area": "main", "title": "Metric stream"},
      {"area": "summary", "title": "Event summary"},
      {"area": "notes", "title": "Interpretation notes"}
    ]
  },
  "components": [
    {
      "componentInstanceId": "CHART-STREAM-001.metric_stream",
      "componentType": "trend_line",
      "area": "main",
      "config": {"time_field": "time", "value_field": "value"},
      "dataBinding": {"source": "metric_series"}
    },
    {
      "componentInstanceId": "CHART-STREAM-001.drift_marker",
      "componentType": "event_marker",
      "area": "main",
      "dataBinding": {"source": "event_markers"}
    },
    {
      "componentInstanceId": "CHART-STREAM-001.event_summary",
      "componentType": "decision_card",
      "area": "summary",
      "dataBinding": {"source": "event_summary"}
    },
    {
      "componentInstanceId": "CHART-STREAM-001.notes",
      "componentType": "decision_card",
      "area": "notes",
      "config": {"card_style": "notes_legend"},
      "dataBinding": {"source": "analysis_note"}
    }
  ],
  "data": {
    "metric_series": [],
    "event_markers": [],
    "event_summary": [],
    "analysis_note": []
  },
  "series": [
    {
      "seriesId": "metric_mean",
      "label": "Metric mean",
      "points": []
    }
  ],
  "eventMarkers": [
    {
      "eventId": "evt-001",
      "t": "2026-01-01T00:10:00Z",
      "level": "drift",
      "score": 0.91
    }
  ],
  "annotations": [],
  "metadata": {
    "runtimeMethodKey": "adwin_mean_stream",
    "score": 0.91,
    "metrics": {}
  }
}
```

## 8. Error 처리

payload adapter 오류:

```text
DriftService가 error를 잡는다.
event analysis API는 ok=false를 반환한다.
error.code = PAYLOAD_ADAPTER_ERROR
```

chartDefinition 없음:

```text
snapshot 없음
chart definition snapshot 누락
  -> error.code = CHART_DEFINITION_NOT_FOUND
```

필수 context 누락:

```text
error.code = PAYLOAD_CONTEXT_INVALID
```

## 9. Registry

payload adapter는 key 기반 registry에서 찾는다.

```python
PAYLOAD_ADAPTERS = {
    "adwin_mean_stream_to_chart_stream_001": build_adwin_mean_stream_chart_stream_001,
}
```

function signature:

```python
def build_adwin_mean_stream_chart_stream_001(context: dict) -> dict:
    ...
```

## 10. 관련 문서

```text
drift_event_model.md
drift_method_runtime_contract.md
timeseries_api_contract.md
data_source_event_schema.md
implementation_scope_v1.md
```
