# Drift Server Timeseries API Contract

## 1. 목적

이 문서는 `drift_metric_timeseries` UI가 Drift Server에서 source별 bucket/event를 조회할 때 사용하는 API 응답 구조를 정의한다.

핵심 결정:

```text
Drift Server는 DB row를 그대로 반환하지 않는다.
drift_metric_timeseries UI가 바로 사용할 수 있는 view model을 반환한다.
```

## 2. 대상 API

현재 v1 dev runtime에서 구현된 timeseries UI 연동 API:

```text
GET /api/sources/{source_id}/timeseries-data
GET /api/sources/{source_id}/events/{event_id}/analysis
```

후속 목표 API:

```text
GET /api/sources/{source_id}/features
GET /api/sources/{source_id}/timeseries-live
GET /api/sources
```

현재 `drift_metric_timeseries` UI는 `/timeseries-data` 응답 안의 `features`, `series`, `events`를 사용하고, event marker 선택 시 `/events/{event_id}/analysis`를 호출한다.

## 3. Feature Metadata

현재 v1 dev runtime에는 별도 `GET /api/sources/{source_id}/features` endpoint가 없다. feature metadata는 `/timeseries-data` 응답의 `features` field에 포함된다.

후속 목표 endpoint:

```text
GET /api/sources/{source_id}/features
```

응답:

```json
{
  "ok": true,
  "data": {
    "sourceId": "case-010",
    "features": [
      {
        "featureId": "metric",
        "label": "Metric",
        "valueType": "numeric",
        "unit": null,
        "enabled": true
      }
    ]
  },
  "error": null
}
```

후속 구현에서는 feature metadata를 source feature registry에서 만들 수 있다.

## 4. Timeseries Data

```text
GET /api/sources/{source_id}/timeseries-data?from=...&to=...&resolution=10m
```

응답:

```json
{
  "ok": true,
  "data": {
    "sourceId": "case-010",
    "modelId": "case-010",
    "resolution": "10m",
    "pollIntervalMs": 600000,
    "features": [
      {
        "featureId": "metric",
        "label": "Metric",
        "valueType": "numeric",
        "unit": null
      }
    ],
    "fullDomain": ["2026-01-01T00:00:00Z", "2026-01-01T01:00:00Z"],
    "series": {
      "metric": [
        {
          "t": "2026-01-01T00:10:00Z",
          "bucketStart": "2026-01-01T00:00:00Z",
          "bucketEnd": "2026-01-01T00:10:00Z",
          "v": 0.42,
          "count": 10,
          "status": "ok"
        }
      ]
    },
    "events": {
      "metric": [
        {
          "eventId": "evt-001",
          "t": "2026-01-01T00:10:00Z",
          "eventStart": "2026-01-01T00:00:00Z",
          "eventEnd": "2026-01-01T00:10:00Z",
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
      ]
    }
  },
  "error": null
}
```

## 5. Series Point

series point는 `metric_bucket`에서 만든다.

```json
{
  "t": "2026-01-01T00:10:00Z",
  "bucketStart": "2026-01-01T00:00:00Z",
  "bucketEnd": "2026-01-01T00:10:00Z",
  "v": 0.42,
  "count": 10,
  "status": "ok"
}
```

필드:

```text
t:
  chart에서 point를 찍는 대표 시간. 기본 bucketEnd.

bucketStart/bucketEnd:
  Drift Server 내부 canonical event_time window.

v:
  numeric value. 기본 mean_value.

count:
  valid numeric value count.

status:
  ok | empty | invalid | no_valid_value
```

## 6. Empty Bucket 표현

empty bucket은 series에 포함한다.

```json
{
  "t": "2026-01-01T00:20:00Z",
  "bucketStart": "2026-01-01T00:10:00Z",
  "bucketEnd": "2026-01-01T00:20:00Z",
  "v": null,
  "count": 0,
  "status": "empty"
}
```

이유:

```text
처리 안 됨과 데이터 없음이 구분된다.
UI가 빈 구간을 명확히 표현할 수 있다.
live update cursor가 안정적으로 전진한다.
```

## 7. Event Marker

event marker는 `drift_event`에서 만든다.

```json
{
  "eventId": "evt-001",
  "t": "2026-01-01T00:10:00Z",
  "eventStart": "2026-01-01T00:00:00Z",
  "eventEnd": "2026-01-01T00:10:00Z",
  "level": "drift",
  "score": 0.91,
  "analysisCharts": []
}
```

필드:

```text
t:
  UI marker 위치. 기본 eventEnd.

eventStart/eventEnd:
  drift_event의 canonical event_time range.

level:
  warning | drift

score:
  drift score.

analysisCharts:
  event의 assignment에 등록된 analysis chart 링크 목록.
```

analysis chart link는 `drift_event.payload_json`에 저장하지 않고, 조회 시 `analysis_chart_registration`에서 조립한다.

## 8. Timeseries Live

현재 v1 dev runtime에는 별도 `timeseries-live` endpoint가 없다. UI live 동작은 `/timeseries-data`를 반복 조회하는 방식으로 구성한다.

후속 목표 endpoint:

```text
GET /api/sources/{source_id}/timeseries-live?since=2026-01-01T00:10:00Z
```

응답:

```json
{
  "ok": true,
  "data": {
    "sourceId": "case-010",
    "resolution": "10m",
    "since": "2026-01-01T00:10:00Z",
    "nextSince": "2026-01-01T00:20:00Z",
    "seriesDelta": {
      "metric": [
        {
          "t": "2026-01-01T00:20:00Z",
          "bucketStart": "2026-01-01T00:10:00Z",
          "bucketEnd": "2026-01-01T00:20:00Z",
          "v": null,
          "count": 0,
          "status": "empty"
        }
      ]
    },
    "eventsDelta": {
      "metric": []
    }
  },
  "error": null
}
```

`since` 기준:

```text
bucket_end > since 인 bucket 반환
event_end > since 인 event 반환
```

`nextSince`:

```text
응답에 포함된 bucket/event 중 가장 큰 시간
없으면 요청 since 그대로 반환
```

UI는 다음 요청에 `nextSince`를 사용한다.

## 9. pollIntervalMs

`pollIntervalMs`는 Drift Server가 응답한다.

운영 모드:

```text
600000
```

테스트 데모 모드:

```text
10000
```

자동 테스트에서는 UI polling을 사용하지 않아도 된다.

## 10. Query Parameter

`timeseries-data`:

```text
from:
  optional ISO timestamp

to:
  optional ISO timestamp

resolution:
  v1은 10m만 지원
```

`timeseries-live`:

```text
since:
  optional ISO timestamp
  없으면 source의 last collected bucket 이후 또는 초기 domain부터 반환할 수 있다.
```

현재 v1 dev runtime에서는 `resolution=10m`만 사용한다. `timeseries-live` parameter는 후속 endpoint용이다.

## 11. v1 제한

v1 제외:

```text
별도 /api/sources 목록 endpoint
별도 /api/sources/{source_id}/features endpoint
별도 /api/sources/{source_id}/timeseries-live delta endpoint
multi-resolution aggregation
server-side downsampling
multi-source overlay
advanced event grouping
event acknowledge/resolve 상태 반영
```

## 12. 관련 문서

```text
drift_event_model.md
time_and_cursor_model.md
data_source_event_schema.md
implementation_scope_v1.md
```
