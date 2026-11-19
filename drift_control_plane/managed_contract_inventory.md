# 핵심 계약 관리 목록

이 문서는 drift control plane에서 반드시 추적해야 하는 핵심 문서, 함수, 자료구조, JSON 계약을 정의한다.

루트 전체 관리 정책은 `../managed_contract_inventory.md`에 둔다. 이 파일은 중앙 DB와 drift control plane 내부 계약의 상세 기준이다.

## 관리 원칙

코드를 수정하기 전에는 먼저 이 문서와 `managed_contracts.csv`를 확인한다.

Codex가 코드를 수정할 때는 루트의 `CODEX_DEVELOPMENT_GUIDE.md`를 함께 따른다.

수정 대상이 `contract_level=P0` 또는 `contract_level=P1` 항목에 해당하면 다음 절차를 따른다.

1. 어떤 관리 항목이 영향을 받는지 확인한다.
2. 변경 사유와 예상 영향 범위를 정리한다.
3. 변경이 불가피하면 구현을 중단하고 사용자 동의를 먼저 받는다.
4. 동의 후 코드, 문서, 테스트, 등록 테이블을 함께 수정한다.
5. 변경 후 관련 contract test를 실행한다.

이 절차의 목적은 chart payload, drift method output, payload adapter, chart runtime 사이의 계약이 조용히 깨지는 것을 막는 것이다.

## 주석 마커 규칙

소스코드에서 관리 대상 함수, 자료구조, 상수 앞에는 `@managed-contract` 주석을 붙인다.

Python 예:

```python
# @managed-contract contract_id=payload_adapter.engine.BindingPayloadAdapter.build level=P0
def build(self, context: dict[str, Any]) -> dict[str, Any]:
    ...
```

JavaScript 예:

```javascript
// @managed-contract contract_id=chart_runtime.renderChartPayload level=P0
function renderChartPayload(target, payload) {
  ...
}
```

JSON 파일은 필드 내부에 주석을 넣을 수 없으므로 파일 옆 문서나 등록 테이블에서 관리한다.

## 등록 테이블

초기 등록 테이블은 `managed_contracts.csv`에 둔다. 이후 DB 테이블로 옮길 수 있다.

권장 DB 테이블 구조:

```sql
CREATE TABLE managed_contract (
  contract_id TEXT PRIMARY KEY,
  contract_level TEXT NOT NULL,
  contract_type TEXT NOT NULL,
  owner_module TEXT NOT NULL,
  file_path TEXT NOT NULL,
  qualified_name TEXT,
  source_of_truth_doc TEXT,
  input_contract TEXT,
  output_contract TEXT,
  dependent_tests TEXT,
  signature_hash TEXT,
  body_hash TEXT,
  content_hash TEXT,
  last_git_commit TEXT,
  status TEXT NOT NULL DEFAULT 'active',
  description TEXT
);
```

## P0 관리 대상

### Chart Payload

- `chart_runtime/payloads/runtime_chart_payloads.json`
- chart runtime이 실제로 그리는 공식 payload template이다.
- `chart_id`, `components`, `data`, `source`, `field`, `component type` 변경은 모두 계약 변경이다.

### Chart-Method Catalog

- `drift 보고서/charts/method_data.js`
- 어떤 drift method가 어떤 chart를 사용할 수 있는지 정의한다.
- payload adapter coverage의 기준 catalog이다.

### Payload Adapter

- `drift_server/app/payload_adapter/engine.py`
- `drift_server/app/payload_adapter/registry.py`
- `drift_server/app/payload_adapter/transformations.py`
- 관리 함수:
  - `BindingPayloadAdapter.build`
  - `BindingPayloadAdapter._validate_context_contract`
  - `BindingPayloadAdapter._validate_payload`
  - `build_payload`
  - `get_binding_spec`
  - `get_registered_binding_index`
  - `build_derived_rows`

### Payload Binding

- `drift_server/app/payload_adapter/bindings/*.json`
- method event/context와 chart payload data field 사이의 연결 정의다.

### Drift Runtime

- `drift_server/app/drift/runtime_registry.py`
- `drift_server/app/runtime_methods/adwin_mean_stream.py`
- 관리 함수와 자료구조:
  - `RUNTIME_METHODS`
  - `get_runtime_method`
  - `run_adwin_mean_stream`
  - `_convert_drift_result`
  - `_fallback_output`
  - `_normal_output`

### Drift Event Analysis

- `drift_server/app/drift/detector.py`
- `drift_server/app/drift/service.py`
- 관리 함수:
  - `DriftDetector.run_for_bucket`
  - `DriftDetector._run_assignment`
  - `DriftService.build_event_analysis`
  - `DriftService._build_analysis_context`
  - `_format_event`
  - `_format_bucket_for_payload`

### Chart Runtime Public API

- `chart_runtime/chart_runtime.js`
- 관리 함수와 자료구조:
  - `window.ChartRuntime`
  - `renderChartPayload`
  - `COMPONENT_RENDERERS`
  - `COMPONENT_SPECS`
  - `dataFor`
  - `rowsForSource`

### Repository/DB Boundary

- `drift_server/app/repositories/method_repository.py`
- `drift_server/app/repositories/event_repository.py`
- `drift_server/app/repositories/analysis_chart_repository.py`
- 관리 함수:
  - `upsert_assignment`
  - `insert_run_once`
  - `upsert_state`
  - `insert_event_once`
  - `get_event`
  - `upsert_registration`
  - `get_for_assignment`

### External API Boundary

- `drift_server/app/main.py`
- 관리 endpoint:
  - `register_source`
  - `register_adapter`
  - `register_method_assignment`
  - `register_analysis_chart`
  - `poll_once`
  - `timeseries_data`
  - `event_analysis`

## P0 문서

- `analysis_payload_adapter_contract.md`
- `chart_catalog_runtime_payload_contract.md`
- `drift_method_runtime_contract.md`
- `drift_event_model.md`
- `data_source_event_schema.md`
- `api_contracts.md`
- `timeseries_api_contract.md`
- `chart_runtime/RUNTIME_CONTRACT.md`
- `chart_runtime/PAYLOAD_RUNTIME_COMPATIBILITY.md`

## 변경 검토 기준

다음 변경은 사용자 승인 없이 진행하지 않는다.

- payload template의 `data` 구조 변경
- chart component type, renderer mapping 변경
- method output의 field name 또는 event schema 변경
- adapter binding의 source/field mapping 변경
- API request/response shape 변경
- DB table/column의 의미 변경
- runtime registry key 변경
- chart id, method key, binding key 변경

단순 내부 리팩터링이라도 위 항목의 signature, output shape, persisted data, public API에 영향을 주면 계약 변경으로 본다.

## Codex 변경 점검 규칙

Codex는 코드 변경 후 반드시 다음을 확인한다.

1. 변경 파일이 `managed_contracts.csv` 또는 DB `managed_contract`에 등록되어 있는지 확인한다.
2. 등록된 P0/P1 함수, 자료구조, endpoint, payload, browser global이 실제로 바뀌었는지 확인한다.
3. 변경이 기존 contract에 영향을 주는지 기준 문서와 artifact로 확인한다.
4. 새로 중요한 함수나 contract가 생겼으면 `@managed-contract` 주석을 붙이고 `managed_contracts.csv`에 등록한다.
5. 변경 결과 보고에 영향받은 contract, 새 등록 대상, 검증 결과를 포함한다.
