# 루트 전체 핵심 계약 관리 목록

이 문서는 `C:\Users\jklee\PycharmProjects\drift_llm_intepretation` 아래 전체 폴더를 대상으로 핵심 계약 관리 범위를 정의한다.

## 중앙 관리 위치

중앙 관리 테이블은 `drift_control_plane`의 SQLite DB에 둔다.

- CSV 원본: `drift_control_plane/managed_contracts.csv`
- DB 테이블: `managed_contract`
- DB 생성/seed 코드: `drift_control_plane/shared/dev_db.py`
- 상세 정책: `drift_control_plane/managed_contract_inventory.md`
- Codex 개발 절차: `CODEX_DEVELOPMENT_GUIDE.md`

루트 전체에서 코드 수정이 발생하면 먼저 중앙 CSV/DB의 `contract_id`, `file_path`, `qualified_name`에 해당하는지 확인한다.

## 적용 범위

관리 대상 폴더는 다음과 같다.

- `chart_builder`
- `chart_runtime`
- `drift 보고서`
- `drift_algorithm_impl`
- `drift_control_plane`
- `drift_metric_timeseries`
- 루트 문서 `드리프트_모니터링_시스템_구성도_및_흐름.md`

`llm_interpretation_server`, `테스트데이터`, `tmp_compare`는 현재 핵심 계약 원본으로 보지 않는다. 이후 API 또는 DB 계약이 생기면 별도 등록한다.

## 수정 전 승인 규칙

다음 항목을 수정해야 하면 구현을 멈추고 사용자 동의를 먼저 받는다.

- `contract_level=P0` 항목
- payload template, chart-method catalog, method output schema
- chart runtime public API 또는 component renderer registry
- drift event, method run, analysis payload, timeseries API shape
- drift algorithm public result structure 또는 server에서 직접 호출하는 algorithm function
- chart builder가 생성하는 runtime payload 구조
- drift metric timeseries UI의 state/action/render model 계약

`contract_level=P1` 항목은 변경 전 영향 범위를 보고하고, 계약 변경 가능성이 있으면 사용자 동의를 받는다.

## 루트 전체 P0/P1 범위

### Root System Document

- `드리프트_모니터링_시스템_구성도_및_흐름.md`
- 전체 시스템 명명, 데이터 흐름, chart engine/runtime 관계의 상위 문서다.

### Chart Runtime

- `chart_runtime/payloads/runtime_chart_payloads.json`
- `chart_runtime/chart_runtime.js`
- payload와 rendering engine 사이의 최종 실행 계약이다.

### Drift Control Plane

- `drift_control_plane/managed_contracts.csv`
- `drift_control_plane/shared/dev_db.py`
- `drift_control_plane/drift_server/app/payload_adapter/*`
- `drift_control_plane/drift_server/app/runtime_methods/*`
- `drift_control_plane/drift_server/app/drift/*`
- `drift_control_plane/drift_server/app/repositories/*`
- `drift_control_plane/drift_server/app/main.py`

### Drift Report

- `drift 보고서/charts/method_data.js`
- chart id와 drift method variant 연결 catalog다.

### Drift Algorithm Implementation

- `drift_algorithm_impl/drift_algorithm/core/result.py`
- `drift_algorithm_impl/drift_algorithm/core/windows.py`
- `drift_algorithm_impl/drift_algorithm/methods/streamingchangedetector.py`
- server runtime wrapper가 직접 사용하는 algorithm result와 ADWIN 계열 함수는 P0다.

### Chart Builder

- `chart_builder/web/builder_prototype.js`
- `chart_builder/web/recreated_chart_payloads.js`
- `chart_builder/web/recreated_charts.js`
- `chart_builder/tools/generate_recreated_site.py`
- builder가 생성하는 runtime payload 구조와 preview/render 흐름은 P1로 관리한다.

### Drift Metric Timeseries

- `drift_metric_timeseries/web/drift_metric_timeseries_demo.js`
- `drift_metric_timeseries/web/drift_metric_timeseries_harness.js`
- `drift_metric_timeseries/web/drift_metric_timeseries_test_data.js`
- state/action/render model, event analysis chart 표시 계약은 P1로 관리한다.
