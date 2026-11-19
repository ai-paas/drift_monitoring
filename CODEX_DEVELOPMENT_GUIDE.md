# Codex 개발 가이드

이 문서는 Codex가 이 저장소에서 코드를 수정할 때 반드시 따를 절차를 정의한다.

## 1. 핵심 계약 우선 확인

코드 변경을 시작하기 전에 먼저 변경 대상 파일이 핵심 계약 관리 대상인지 확인한다.

확인 기준:

```text
drift_control_plane/managed_contracts.csv
drift_control_plane/runtime/sprint2_dev.sqlite3 managed_contract 테이블
managed_contract_inventory.md
drift_control_plane/managed_contract_inventory.md
```

변경 파일이 `managed_contract`에 등록된 `file_path`와 일치하거나, 등록된 `qualified_name` 주변 코드를 수정한다면 해당 변경은 관리 대상이다.

## 2. P0/P1 변경 절차

`contract_level=P0` 항목을 수정해야 하면 구현을 중단하고 사용자 동의를 먼저 받아야 한다.

`contract_level=P1` 항목을 수정해야 하면 영향 범위를 먼저 검토한다. signature, input/output shape, public API, persisted data, payload 구조, 테스트 상태 contract가 바뀔 가능성이 있으면 사용자 동의를 먼저 받아야 한다.

변경 전 검토 항목:

```text
어떤 contract_id가 영향을 받는가
기존 입력 계약이 바뀌는가
기존 출력 계약이 바뀌는가
호출자가 기대하는 field/key/name이 바뀌는가
DB 저장 구조나 payload shape가 바뀌는가
기준 문서와 테스트가 함께 갱신되어야 하는가
```

## 3. 변경 후 계약 영향 확인

코드 변경 후에는 반드시 변경된 파일을 `managed_contract` 목록과 다시 대조한다.

확인 결과는 다음 기준으로 정리한다.

```text
기존 등록 항목 중 실제 변경된 항목
등록된 파일 안에서 바뀌었지만 등록 함수 자체는 바뀌지 않은 항목
새로 중요해졌지만 아직 DB에 등록되지 않은 항목
contract 영향 없음으로 판단한 근거
실행한 검증 테스트와 결과
```

계약 영향이 없다고 판단하려면 다음 중 하나 이상의 근거가 있어야 한다.

```text
기존 public signature가 유지됨
기존 request/response shape가 유지됨
기존 DB column/key 의미가 유지됨
기존 browser/global API가 additive change로만 확장됨
기존 regression test와 관련 contract test가 통과함
artifact에서 기존 field가 유지됨을 확인함
```

## 4. 새 중요 함수와 자료구조 등록

구현 중 새로 중요한 함수, 자료구조, 상수, browser global, JSON/CSV 계약, 테스트 상태 contract가 생기면 반드시 관리 대상으로 등록한다.

등록 대상 예:

```text
서버/API 경계 함수
payload 변환 adapter
chart runtime public API
UI state/action/render model
window.__... 형태의 browser test/control API
drift method input/output 구조
DB seed, migration, repository boundary
Harness smoke test entrypoint
```

등록 절차:

```text
1. 소스코드 바로 앞에 @managed-contract 주석을 붙인다.
2. drift_control_plane/managed_contracts.csv에 행을 추가한다.
3. DB seed를 실행하거나 connect()를 통해 managed_contract 테이블에 반영되게 한다.
4. source_of_truth_doc와 dependent_tests를 지정한다.
5. 필요하면 기준 문서를 새로 만들거나 갱신한다.
```

Python 예:

```python
# @managed-contract contract_id=example.module.important_function level=P1
def important_function(value: dict[str, object]) -> dict[str, object]:
    ...
```

JavaScript 예:

```javascript
// @managed-contract contract_id=example.ui.window_api level=P1
window.exampleUiApi = {
  getState
};
```

## 5. 문서와 DB 동기화

코드가 바뀌었는데 기준 문서가 기존 contract를 설명하고 있으면 문서를 함께 고친다.

반대로 문서가 맞고 코드가 다른 경우에는 코드 수정 여부를 사용자에게 확인한다.

특히 다음 문서는 P0 source of truth로 본다.

```text
drift_control_plane/api_contracts.md
drift_control_plane/timeseries_api_contract.md
drift_control_plane/analysis_payload_adapter_contract.md
drift_control_plane/drift_method_runtime_contract.md
chart_runtime/RUNTIME_CONTRACT.md
chart_runtime/PAYLOAD_RUNTIME_COMPATIBILITY.md
```

## 6. Codex 응답 규칙

작업 완료 보고에는 다음을 포함한다.

```text
변경된 P0/P1 항목
새로 등록해야 하는 관리 대상
contract 영향 여부
실행한 테스트와 결과
남은 문서/DB 등록 작업
```

중요 계약 변경 가능성이 있으면 구현을 계속하지 말고 사용자에게 먼저 확인한다.
