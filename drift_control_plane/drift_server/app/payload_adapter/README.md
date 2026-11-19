# Payload Adapter Binding Engine

이 패키지는 Drift Server의 drift method event/context를 chart runtime payload로 변환한다.

핵심 계약은 다음 흐름이다.

```text
drift method event/context
  -> payload adapter binding spec
  -> chart_runtime payload template
  -> chart_runtime rendering
```

## 구성

```text
engine.py
  binding spec을 실행한다.
  method event contract를 검증하고 payload.data를 만든다.

registry.py
  chart-method 쌍을 binding key로 등록한다.
  명시 binding이 있으면 JSON 파일을 사용하고, 없으면 catalog 기반 자동 binding spec을 만든다.

transformations.py
  자동 binding spec에서 사용하는 공통 변환 함수를 제공한다.

bindings/*.json
  명시적으로 관리하는 method-chart binding spec이다.
```

## 등록 방식

현재 등록 대상은 `drift 보고서/charts/method_data.js`의 chart-method catalog와
`chart_runtime/payloads/runtime_chart_payloads.json`의 chart template을 기준으로 한다.

등록 규칙은 다음과 같다.

1. `bindings/*.json`에 명시 binding이 있으면 그 binding을 우선 사용한다.
2. 명시 binding이 없는 chart-method 쌍은 `auto__{methodVariantKey}__{chartId}` 형식으로 자동 등록한다.
3. 자동 binding은 chart component의 `dataBinding.source`와 config의 `*_field` 값을 읽어 `dataBindings`와 `dataContracts`를 만든다.
4. 각 data source에는 `transform` 이름이 들어가며, 이 이름이 실제 row 생성 방법을 결정한다.

## 변환 타입

자동 binding에서 사용하는 변환 타입은 다음과 같다.

```text
event_summary
  event id, level, score, method를 summary row로 만든다.

analysis_note
  chart notes 영역에 들어갈 title/text row를 만든다.

event_timeline
  eventStart/eventEnd를 start/end/time/window 필드에 연결한다.

metric_series
  context.buckets가 있으면 bucket row를 만들고, 없으면 driftEvent score 기반 row를 만든다.

reference_current_distribution
  reference/current/baseline, histogram, density 계열 필드를 채운다.

projection_points
  reference/current 두 그룹의 x/y projection row를 만든다.

matrix_values
  heatmap/matrix component의 values 필드를 만든다.

category_contribution
  category, feature, metric, contribution, distance 계열 필드를 만든다.
```

## 현재 상태

커버리지 테스트 기준:

```text
chart count: 53
chart-method pair count: 188
registered binding count: 188
passed binding pair count: 188
failed binding pair count: 0
```

명시 binding은 실제 method별 의미 변환을 고정한 계약이고, 자동 binding은 runtime payload 계약을 깨지 않도록 공통 변환 타입으로 등록한 기본 계약이다.

운영 품질을 높이려면 자동 binding을 method family별 명시 binding으로 점진적으로 승격해야 한다.
