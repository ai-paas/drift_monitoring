# ADL

이 폴더는 `drift_llm_intepretation` 시스템의 Architecture Description Language 산출물을 둔다.

현재 원칙은 새 전용 언어를 만들지 않고 다음 언어를 조합하는 것이다.

- PlusCal/TLA+: 서버, UI, polling, tick, 비동기 요청, DB 상태 전이, invariant
- CUE: API response, chart payload, method output, datasource-adapter binding, payload adapter binding, managed contract row schema
- Mermaid 또는 Structurizr DSL: 사람이 읽는 시스템 구조도, sequence, component view

## 문서

- [ARCHITECTURE_DESCRIPTION_LANGUAGE_GUIDE.md](./ARCHITECTURE_DESCRIPTION_LANGUAGE_GUIDE.md): ADL 언어 조합, 작성 규칙, 파일 배치, managed contract 연계 기준

## 초기 산출물

### Diagrams

- [diagrams/system_context.mmd](./diagrams/system_context.mmd): 전체 모듈과 서버 관계
- [diagrams/control_plane_sequence.mmd](./diagrams/control_plane_sequence.mmd): Admin/Test Feeder/Drift Server polling 흐름
- [diagrams/event_analysis_payload_flow.mmd](./diagrams/event_analysis_payload_flow.mmd): drift event에서 chart payload/rendering까지
- [diagrams/timeseries_ui_flow.mmd](./diagrams/timeseries_ui_flow.mmd): timeseries UI polling과 event selection
- [diagrams/managed_contract_map.mmd](./diagrams/managed_contract_map.mmd): P0/P1 contract 위치

### CUE

- [cue/timeseries_api.cue](./cue/timeseries_api.cue): timeseries API response shape
- [cue/source_adapter_binding.cue](./cue/source_adapter_binding.cue): datasource와 adapter의 1:1 binding shape
- [cue/event_analysis_api.cue](./cue/event_analysis_api.cue): event analysis response shape
- [cue/chart_payload.cue](./cue/chart_payload.cue): ChartRuntime payload shape
- [cue/runtime_method_output.cue](./cue/runtime_method_output.cue): drift runtime method output shape
- [cue/managed_contract.cue](./cue/managed_contract.cue): managed contract row shape

### PlusCal/TLA+

- [tla/DriftControlPlane.tla](./tla/DriftControlPlane.tla): feeder/poll/runtime/event 상태 전이 초안
- [tla/DriftControlPlane.cfg](./tla/DriftControlPlane.cfg): DriftControlPlane model check 설정
- [tla/EventAnalysisFlow.tla](./tla/EventAnalysisFlow.tla): event analysis payload 생성 상태 전이 초안
- [tla/EventAnalysisFlow.cfg](./tla/EventAnalysisFlow.cfg): EventAnalysisFlow model check 설정

## 권장 하위 구조

ADL 산출물은 다음 구조를 사용한다.

```text
ADL/
  diagrams/
    system_context.mmd
    control_plane_sequence.mmd
    event_analysis_payload_flow.mmd
    timeseries_ui_flow.mmd
    managed_contract_map.mmd
  cue/
    source_adapter_binding.cue
    timeseries_api.cue
    event_analysis_api.cue
    chart_payload.cue
    runtime_method_output.cue
    managed_contract.cue
  tla/
    DriftControlPlane.tla
    DriftControlPlane.cfg
    EventAnalysisFlow.tla
    EventAnalysisFlow.cfg
```

## Contract 기준

이 폴더의 문서는 처음에는 설명용 산출물이다. 특정 CUE schema, TLA+ invariant, diagram이 테스트나 release gate, 또는 P0/P1 source-of-truth 역할을 하게 되면 `drift_control_plane/managed_contracts.csv` 등록 여부를 검토한다.

## 검증

portable 검증 도구는 `ADL/tools/` 아래에 둔다. 루트 디렉터리에서 다음 명령으로 CUE schema 평가와 TLA+ TLC model check를 실행한다.

```powershell
.\ADL\run_adl_checks.ps1
```

PowerShell 실행 정책으로 스크립트 실행이 막히면 다음처럼 실행한다.

```powershell
powershell -ExecutionPolicy Bypass -File .\ADL\run_adl_checks.ps1
```
