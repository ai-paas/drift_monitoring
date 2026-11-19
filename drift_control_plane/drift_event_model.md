# Drift Event Model

## 1. 목적

이 문서는 Drift Server가 drift method 실행 결과로 생성하는 `drift_event`의 생성 규칙, 상태, 중복 방지, 시간 범위, payload 구조를 정의한다.

v1 목표:

```text
단순하고 재현 가능한 event 생성 모델을 사용한다.
event merge, acknowledge, resolve workflow는 후속으로 미룬다.
```

## 2. Event 생성 조건

DriftDetector는 runtime output을 보고 event 생성 여부를 결정한다.

생성 조건:

```text
runtime output level = warning 또는 drift
```

생성하지 않는 조건:

```text
level = normal
level = unknown
runStatus = skipped
runStatus = error
empty bucket 기본 skipped
```

## 3. Event Lifecycle

v1에서는 event를 생성할 때 항상 `open` 상태로 저장한다.

```text
event_status = open
```

v1에서 상태 변경 API는 만들지 않는다.

후속 상태 후보:

```text
acknowledged
resolved
ignored
```

후속으로 human verification workflow를 넣을 때 상태 전이를 확장한다.

## 4. Dedup 정책

v1에서는 `method_run_id`당 최대 하나의 drift_event를 생성한다.

```text
unique(method_run_id)
```

같은 drift가 다음 window에서도 계속 감지되면 새 `method_run`이 생기므로 새 `drift_event`도 생성된다.

```text
00:00~00:10 drift -> event A
00:10~00:20 drift -> event B
```

v1에서는 인접 event를 병합하거나 기존 open event를 extend하지 않는다. 시간이 겹치는 event도 자동 병합하지 않는다.

겹치는 window 예:

```text
00:00~00:50 drift -> event A
00:10~01:00 drift -> event B
```

이 경우 event A와 event B는 같은 source/feature/method에서 발생했더라도 서로 다른 `method_run`의 결과이므로 별도 `drift_event`로 저장한다.

정책:

```text
overlapping drift_event 허용
nearby drift_event 허용
same source + same feature + same method event도 method_run이 다르면 별도 event
automatic merge 없음
automatic extend 없음
automatic suppress 없음
```

이 정책은 drift가 계속 감지되는 상태를 숨기지 않기 위한 것이다. 이벤트가 많아지는 문제는 저장 단계에서 해결하지 않고, 후속 UI/API view layer에서 grouping/filtering으로 다룬다.

후속 검토:

```text
same assignment + same feature + nearby window event merge
open event event_end extend
event group id
incident model
view-layer event grouping/filtering
```

## 5. Level / Severity

v1 event level:

```text
warning
drift
```

`critical`은 v1에서 사용하지 않는다.

`level`은 runtime output의 `level`을 따른다.

```text
output.level = warning -> drift_event.level = warning
output.level = drift   -> drift_event.level = drift
```

## 6. Event Time Range

event time range는 Drift Server 내부 canonical `event_time` 기준이다.
source 원래 발생 시간은 event payload 또는 연결된 bucket payload의 `source_event_time` 요약으로 보존한다.

우선순위:

```text
1. runtime output event.eventStart / event.eventEnd가 있으면 사용
2. 없으면 method_run.window_start / method_run.window_end 사용
```

기본값:

```text
event_start = method_run.window_start
event_end = method_run.window_end
```

runtime method가 더 정확한 drift point를 알고 있다면 event range를 직접 제안할 수 있다.

예:

```json
{
  "event": {
    "eventStart": "2026-01-01T00:06:00Z",
    "eventEnd": "2026-01-01T00:10:00Z"
  }
}
```

## 7. Event Payload

`drift_event.payload_json`에는 event 해석과 chart payload 생성에 필요한 method 결과 요약을 저장한다.

권장 구조:

```json
{
  "event": {
    "eventTitle": "ADWIN mean drift detected",
    "eventPayload": {}
  },
  "method": {
    "methodVariantId": 123,
    "algorithmImplementationId": 45,
    "runtimeMethodKey": "adwin_mean_stream"
  },
  "score": 0.91,
  "metrics": {},
  "diagnostics": {},
  "payloadHints": {}
}
```

저장 원칙:

```text
runtime output.event
runtime output.metrics
runtime output.diagnostics
runtime output.payloadHints
score
method identifiers
```

analysis chart link는 `payload_json`에 저장하지 않는다. 조회 시 `analysis_chart_registration`을 통해 조립한다.

## 8. Analysis Chart 연결

event는 `assignment_id`를 통해 analysis chart registration과 연결된다.

```text
drift_event.assignment_id
  -> source_method_assignment.assignment_id
  -> analysis_chart_registration.assignment_id
```

timeseries API는 event를 반환할 때 등록된 analysis chart 목록을 함께 조립한다.

```json
{
  "eventId": "evt-001",
  "level": "drift",
  "score": 0.91,
  "analysisCharts": [
    {
      "analysisChartId": "analysis-case010-adwin-stream",
      "chartId": "CHART-STREAM-001",
      "url": "/sources/case-010/events/evt-001/analysis/analysis-case010-adwin-stream"
    }
  ]
}
```

## 9. Event 생성 Transaction

event 생성은 method_run 저장과 같은 logical processing 안에서 수행한다.

권장 흐름:

```text
runtime output 수신
method_run 저장
if level in (warning, drift):
  insert drift_event on conflict(method_run_id) do nothing
```

`method_run_id` unique constraint로 중복 생성을 막는다.

## 10. v1 제외 범위

v1에서 제외:

```text
event acknowledge API
event resolve API
event ignore API
event merge/extend
event group/incident model
critical severity
human verification workflow
```

## 11. 관련 문서

```text
drift_method_runtime_contract.md
idempotency_and_locking.md
data_source_event_schema.md
implementation_scope_v1.md
```
