# Chart Catalog와 Runtime Payload 연동 계약

이 문서는 `drift 보고서` DB의 chart catalog, `chart_runtime`의 canonical payload, Drift Server의 event analysis API가 어떤 계약으로 연결되어야 하는지 정의한다.

## 1. 결론

Drift Server는 chart를 임의로 생성하거나 `CHART-STREAM-001` 같은 chart id를 코드에 고정하면 안 된다.

Drift Server는 다음 순서로 chart를 결정해야 한다.

```text
data source
  -> source_method_assignment
  -> method_variant
  -> drift 보고서 DB.variant_chart
  -> drift 보고서 DB.chart_definition.chart_code
  -> chart_runtime payload template
  -> event analysis chartPayload
```

즉 "어떤 data source가 어떤 drift method를 쓰는가"가 정해지면, 그 method variant에 연결된 분석 chart 후보가 정해지고, event analysis 시 그 chart의 runtime payload template에 실제 데이터를 주입해서 보여준다.

## 2. Source of Truth

### 2.1 Drift 보고서 DB

`drift 보고서` DB는 chart catalog의 source of truth다.

관련 테이블:

- `chart_definition`
  - chart id와 차트 의미를 관리한다.
  - `chart_code`가 외부에서 사용하는 chart id다.
  - 예: `CHART-EDF-001`, `CHART-STREAM-001`, `CHART-RANK-001`
- `variant_chart`
  - method variant와 chart를 연결한다.
  - `is_primary_chart = true`인 chart가 해당 method variant의 기본 분석 chart다.
- `chart_asset`
  - HTML/CSS/JS/PNG/description 같은 산출물 경로를 관리한다.
- `chart_component_usage`
  - chart가 어떤 component를 사용하는지 관리한다.

Drift Server는 chart id 목록을 자체 코드에 하드코딩하지 않고, 이 catalog를 조회하거나 snapshot으로 받아야 한다.

### 2.2 Chart Runtime Payload

`chart_runtime/payloads/runtime_chart_payloads.json`은 chart runtime이 렌더링할 수 있는 canonical payload template 모음이다.

이 파일의 payload는 다음을 가진다.

- `chartId`
- `title`
- `layout`
- `components`
- `data`

운영 흐름에서 `layout`, `components`, `component config`, `dataBinding`은 template로 유지하고, Drift Server는 event analysis 시 `data`를 실제 분석 데이터로 교체한다.

## 3. Drift Server 책임

Drift Server의 책임은 chart를 그리는 것이 아니라, 선택된 chart가 요구하는 runtime payload를 만드는 것이다.

Drift Server가 해야 하는 일:

1. `source_method_assignment`에 method/variant 정보를 저장한다.
2. 해당 method variant에 연결된 analysis chart를 선택한다.
3. 선택 결과를 `analysis_chart_registration`에 저장한다.
4. event 발생 시 registration을 조회한다.
5. registration의 `chart_id`에 해당하는 runtime payload template을 찾는다.
6. payload adapter를 실행해 template의 `data`를 실제 bucket/event/method_run 데이터로 교체한다.
7. `chartDefinition`과 `chartPayload`를 event analysis API로 반환한다.

Drift Server가 하지 않는 일:

- chart runtime을 직접 실행하지 않는다.
- chart를 이미지로 렌더링하지 않는다.
- `chart_runtime.js`의 renderer 동작을 수정하지 않는다.
- chart catalog의 원본 정의를 임의로 변경하지 않는다.

## 4. Registration 계약

`analysis_chart_registration`은 source/method assignment와 chart runtime payload를 연결하는 실행 시점 계약이다.

필수 필드:

```text
analysis_chart_id
source_id
assignment_id
chart_id
chart_definition_id
chart_definition_json
payload_adapter_key
payload_adapter_config_json
enabled
```

의미:

- `chart_id`
  - `drift 보고서.chart_definition.chart_code`와 동일해야 한다.
- `chart_definition_id`
  - chart catalog 원본 추적용 ID다.
- `chart_definition_json`
  - 등록 시점 chart definition snapshot이다.
- `payload_adapter_key`
  - 이 chart에 실제 데이터를 주입하는 adapter key다.
- `payload_adapter_config_json`
  - chart별 field mapping, window 선택, threshold 표시 방식 등 adapter 설정이다.

## 5. Runtime Payload Template 계약

Runtime payload template은 다음처럼 사용한다.

```text
template.chartId
template.layout
template.components
template.dataBinding
```

위 값들은 chart 모양과 component 구조를 정의한다.

event analysis 시 Drift Server는 다음만 바꾼다.

```text
payload.data
payload.metadata
payload.eventMarkers
payload.annotations
```

신규 구조에서는 `payload.data`가 canonical이다. `eventMarkers`, `annotations`는 호환 필드로 둘 수 있지만, 신규 renderer/LLM 연동은 `layout/components/data`를 기준으로 한다.

## 5.1 Method/Event와 Payload 사이의 Binding 계약

`payload_adapter`는 chart별 Python 코드를 계속 늘리는 방식으로 구현하지 않는다.

기본 원칙:

```text
drift method output/event context
  -> declarative binding spec
  -> chart runtime payload template
```

binding spec은 다음을 선언한다.

```text
methodVariantKey
chartId
methodEventContract
payloadTemplate
dataBindings
dataContracts
```

의미:

- `methodEventContract`
  - drift method/event context가 반드시 제공해야 하는 값이다.
  - 예: event id, event start/end, level, score, method run id
- `payloadTemplate`
  - chart runtime이 요구하는 layout/components/config/dataBinding 구조다.
- `dataBindings`
  - `buckets`, `driftEvent`, `methodRun`, `runtimeResult` 같은 Drift Server context를 `payload.data[...]`로 변환하는 규칙이다.
- `dataContracts`
  - 각 `payload.data[source]` row가 반드시 가져야 하는 field 목록이다.

초기 구현 위치:

```text
drift_control_plane/drift_server/app/payload_adapter/
  engine.py
  registry.py
  bindings/*.json
```

운영 단계에서는 이 binding spec을 `drift 보고서` DB의 `variant_measurement`, `variant_chart`, `chart_definition.input_contract_json`, `chart_component.input_contract_json`과 대조해 검증한다.

## 6. Chart 선택 규칙

기본 선택 규칙:

1. `source_method_assignment.method_variant_id`가 있으면 해당 variant를 기준으로 한다.
2. `variant_chart.is_primary_chart = true`인 active chart를 우선 선택한다.
3. primary chart가 없으면 `display_order`가 가장 낮은 active chart를 선택한다.
4. 사용자가 명시적으로 chart를 선택한 경우, 해당 chart가 method variant에 연결되어 있는지 검증한다.
5. 연결되지 않은 chart는 기본적으로 거부한다.

예외:

- 실험 모드에서는 `CHART-GEN-001` 같은 fallback chart를 허용할 수 있다.
- fallback 사용 여부는 응답 metadata에 명시해야 한다.

## 7. Event Analysis 실행 흐름

```text
GET /api/sources/{source_id}/events/{event_id}/analysis
  -> drift_event 조회
  -> method_run 조회
  -> source_method_assignment 조회
  -> analysis_chart_registration 조회
  -> chart_id 확인
  -> runtime payload template 조회
  -> payload_adapter_key로 adapter 선택
  -> bucket/event/method result를 template.data에 주입
  -> chartDefinition + chartPayload 반환
```

응답의 핵심 구조:

```json
{
  "chartId": "CHART-STREAM-001",
  "chartDefinitionId": "chartdef-or-db-id",
  "chartDefinition": {},
  "chartPayload": {
    "chartId": "CHART-STREAM-001",
    "layout": {},
    "components": [],
    "data": {},
    "metadata": {}
  }
}
```

## 8. 현재 구현과의 차이

현재 Drift Server 구현은 아직 이 계약을 완전히 따르지 않는다.

현재 상태:

- `CHART-STREAM-001`이 기본값으로 코드에 고정되어 있다.
- `payload_adapter_key`도 `adwin_mean_stream_to_chart_stream_001` 중심이다.
- `chart_runtime/payloads/runtime_chart_payloads.json`을 catalog/template store로 조회하지 않는다.
- `drift 보고서` DB의 `chart_definition`, `variant_chart`를 실제 선택 로직에 사용하지 않는다.

필요한 변경:

1. Drift Server에 chart catalog client 또는 repository를 추가한다.
2. `method_variant_id -> chart_id` 선택 로직을 추가한다.
3. `chart_id -> runtime payload template` 조회 로직을 추가한다.
4. payload adapter가 template 기반으로 `data`만 교체하도록 바꾼다.
5. registration API가 선택된 chart와 payload adapter의 호환성을 검증한다.
6. test harness가 `CHART-STREAM-001` 고정 검증이 아니라 catalog 기반 선택을 검증한다.

## 9. 깨지면 안 되는 계약

다음 조건이 깨지면 chart는 정상적으로 렌더링될 수 없다.

1. `analysis_chart_registration.chart_id`가 runtime payload template의 `chartId`와 다르다.
2. component의 `dataBinding.source`가 `chartPayload.data`에 없다.
3. payload adapter가 component가 요구하는 field를 만들지 않는다.
4. method variant에 연결되지 않은 chart를 선택한다.
5. `chartDefinition`과 `chartPayload.chartId`가 서로 다르다.
6. runtime이 지원하지 않는 `componentType`을 payload가 사용한다.

따라서 Drift Server는 event analysis 응답 전에 최소한 다음 검증을 수행해야 한다.

```text
chartPayload.chartId == analysis_chart_registration.chart_id
chartPayload.layout exists
chartPayload.components not empty
chartPayload.data exists
for each component.dataBinding.source:
  source exists in chartPayload.data
componentType is supported by chart_runtime
```

## 10. 현재 Payload Adapter 등록 상태

현재 `drift_server.app.payload_adapter`는 `drift 보고서/charts/method_data.js`에 정의된 chart-method catalog와
`chart_runtime/payloads/runtime_chart_payloads.json`에 정의된 runtime payload template을 기준으로 binding을 등록한다.

등록 방식은 두 종류다.

```text
명시 binding
  bindings/*.json에 직접 정의된 binding이다.
  method event contract, dataBindings, dataContracts를 사람이 명시한다.

자동 binding
  명시 binding이 없는 chart-method 쌍에 대해 registry.py가 생성한다.
  binding key 형식은 auto__{methodVariantKey}__{chartId} 이다.
```

자동 binding도 단순 등록만 하는 것이 아니라 component의 `dataBinding.source`와 config의 `*_field` 값을 읽어
다음 공통 변환 타입 중 하나를 연결한다.

```text
event_summary
analysis_note
event_timeline
metric_series
reference_current_distribution
projection_points
matrix_values
category_contribution
```

따라서 현재 기준으로 188개 chart-method 쌍은 모두 다음 계약을 가진다.

```text
methodVariantKey
chartId
payloadAdapterKey
methodEventContract.requiredContextPaths
payloadTemplate
dataBindings[].targetDataSource
dataBindings[].transform
dataBindings[].fields
dataContracts[].requiredFields
```

테스트 기준 현재 상태:

```text
chart count: 53
chart-method pair count: 188
registered binding count: 188
passed binding pair count: 188
failed binding pair count: 0
```

주의할 점은 자동 binding은 runtime payload를 깨지 않게 하는 기본 변환 계약이라는 점이다.
실제 운영 의미까지 고정하려면 method family별로 자동 binding을 명시 binding으로 승격해야 한다.
