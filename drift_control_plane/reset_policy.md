# Drift Server Test Reset Policy

## 1. 목적

이 문서는 테스트 모드에서 reset API가 어떤 데이터를 삭제하거나 보존하는지 정의한다.

핵심 결정:

```text
기본 reset mode는 run reset이다.
run reset은 실행 데이터만 초기화하고 source/adapter/method/chart 등록 정보는 보존한다.
reset은 migration/bootstrap 재실행을 대체하지 않는다. migration은 DB 구조 생성용이고 reset은 반복 테스트 실행 데이터 초기화용이다.
```

## 2. Reset Mode

테스트 reset은 세 가지 mode를 가진다.

```text
run
  테스트 실행 데이터만 삭제/초기화한다.

source
  특정 source에 연결된 실행 데이터와 등록 정보를 삭제한다.

hard
  테스트 관련 데이터를 전체 초기화한다.
```

## 3. API

```text
POST /api/admin/test/reset
```

요청:

```json
{
  "mode": "run",
  "sourceId": "case-010"
}
```

필드:

```text
mode:
  run | source | hard

sourceId:
  선택 값. 지정하면 해당 source만 reset한다.
  hard mode에서는 생략 가능하다.
```

기본값:

```text
mode = run
```

## 4. Run Reset

run reset은 테스트를 다시 실행하기 위해 실행 데이터만 초기화한다.

삭제 또는 초기화 대상:

```text
test_source.raw_event
test_source.feed_state cursor/status
drift_server.adapter_state cursor/status/error
drift_server.metric_bucket
drift_server.method_state
drift_server.method_run
drift_server.drift_event
```

보존 대상:

```text
drift_server.data_source
drift_server.source_feature
drift_server.source_adapter
drift_server.source_method_assignment
drift_server.analysis_chart_registration
drift_server.chart_payload_adapter
```

run reset 후에는 source/adapter/method/chart를 다시 등록하지 않고 바로 feeder와 adapter를 다시 시작할 수 있어야 한다.

## 5. Source Reset

source reset은 특정 source와 관련된 등록 정보까지 삭제한다.

삭제 대상:

```text
test_source.raw_event where source_id = :source_id
test_source.feed_state where source_id = :source_id

drift_server.drift_event where source_id = :source_id
drift_server.method_run where source_id = :source_id
drift_server.method_state where source_id = :source_id
drift_server.metric_bucket where source_id = :source_id
drift_server.analysis_chart_registration where source_id = :source_id
drift_server.source_method_assignment where source_id = :source_id
drift_server.adapter_state for adapters of source_id
drift_server.source_adapter where source_id = :source_id
drift_server.source_feature where source_id = :source_id
drift_server.data_source where source_id = :source_id
```

보존 대상:

```text
drift_server.chart_payload_adapter
drift 보고서 DB catalog
LLM guide DB data
```

source reset은 특정 source를 완전히 다시 등록하고 싶을 때 사용한다.

## 6. Hard Reset

hard reset은 테스트 환경 전체를 초기화한다.

삭제 대상:

```text
test_source.raw_event
test_source.feed_state

drift_server.drift_event
drift_server.method_run
drift_server.method_state
drift_server.metric_bucket
drift_server.analysis_chart_registration
drift_server.source_method_assignment
drift_server.adapter_state
drift_server.source_adapter
drift_server.source_feature
drift_server.data_source
```

보존 대상:

```text
drift_server.chart_payload_adapter
drift 보고서 DB catalog
chart_builder catalog
LLM guide DB data
```

`chart_payload_adapter`는 code function registry에 가까우므로 hard reset에서도 기본 보존한다. adapter registry까지 삭제해야 하는 경우는 별도 maintenance 작업으로 둔다.

## 7. Reset 실행 순서

foreign key 관계를 고려해 자식 테이블부터 삭제한다.

권장 순서:

```text
drift_event
method_run
method_state
metric_bucket
analysis_chart_registration
source_method_assignment
adapter_state
source_adapter
source_feature
data_source
```

run reset에서는 등록 테이블을 삭제하지 않는다.

## 8. 실행 중 Reset 방지

reset 전에 관련 feeder와 adapter를 중지해야 한다.

정책:

```text
reset 요청
  -> Admin Server가 feeder stop 요청
  -> Admin Server가 adapter stop 요청
  -> 상태가 stopped인지 확인
  -> reset 실행
```

실행 중인 adapter가 있으면 reset은 실패하거나 `force=true`일 때만 진행한다.

요청 예:

```json
{
  "mode": "run",
  "sourceId": "case-010",
  "force": false
}
```

## 9. 응답

```json
{
  "ok": true,
  "data": {
    "mode": "run",
    "sourceId": "case-010",
    "deleted": {
      "rawEvents": 120,
      "metricBuckets": 12,
      "methodRuns": 12,
      "driftEvents": 1
    },
    "preserved": {
      "sources": 1,
      "adapters": 1,
      "assignments": 1,
      "analysisCharts": 1
    }
  },
  "error": null
}
```

## 10. 1차 구현 범위

1차 구현에서는 다음만 필수다.

```text
run reset
sourceId 지정 run reset
실행 중 reset 방지
```

`source`와 `hard` mode는 API contract에는 포함하되, 구현은 후속으로 미룰 수 있다.

## 11. 관련 이슈

```text
DRI-011 테스트 reset 정책 불명확
```

## 12. 관련 문서

```text
database_migration_policy.md
database_physical_topology.md
```
