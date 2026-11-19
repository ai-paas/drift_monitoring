# Repository Instructions for Codex

이 저장소에서 작업할 때는 별도 요청이 없어도 이 문서를 우선 적용한다.

## 1. 개발 가이드 준수

코드, 문서, 테스트, 설정을 수정하기 전에는 루트의 `CODEX_DEVELOPMENT_GUIDE.md`를 따른다.

특히 다음 기준 파일과 등록 목록을 확인한다.

- `CODEX_DEVELOPMENT_GUIDE.md`
- `managed_contract_inventory.md`
- `drift_control_plane/managed_contract_inventory.md`
- `drift_control_plane/managed_contracts.csv`
- `drift_control_plane/runtime/sprint2_dev.sqlite3`의 `managed_contract` 테이블이 필요한 경우

## 2. Managed Contract 변경 규칙

- `contract_level=P0` 항목을 수정해야 하면 구현을 중단하고 사용자 동의를 먼저 받는다.
- `contract_level=P1` 항목도 signature, input/output shape, public API, persisted data, payload 구조에 영향이 있으면 사용자 동의를 먼저 받는다.
- 변경 후에는 영향받은 contract, 새 등록 대상, contract 영향 여부, 실행한 테스트와 결과를 보고한다.
- 새로 중요한 API, 함수, 자료구조, browser global, JSON/CSV 계약, repository boundary, 테스트 상태 contract가 생기면 `@managed-contract` 주석과 `managed_contracts.csv` 등록 필요 여부를 검토한다.

## 3. 작업 로그 작성

작업을 완료하면 반드시 `logs/` 폴더에 작업 로그를 남긴다.

로그에는 최소한 다음을 기록한다.

- 작업 일시
- 요청 또는 작업 목적
- 추가한 파일
- 수정한 파일
- 삭제한 파일
- 추가한 함수, 클래스, endpoint, public API
- 수정한 함수, 클래스, endpoint, public API
- managed contract 영향 여부
- 실행한 검증 또는 테스트
- 남은 후속 작업

권장 파일명:

```text
logs/YYYY-MM-DD_short-task-name.md
```

같은 날짜에 같은 주제의 로그가 이미 있으면 숫자 suffix를 붙인다.

## 4. Chart Gallery Change Gate

`drift 보고서/` 아래 chart gallery 코드나 chart interpretation text를 변경하기 전에는 관련 chart authoring guide를 확인한다.

- `drift 보고서/chart_docs/drift_chart_title_authoring_guide.md`
- `drift 보고서/chart_docs/drift_chart_explanation_authoring_guide.md`

chart title 또는 explanation을 수정할 때는 사용자가 명시적으로 더 넓은 일괄 수정을 요청하지 않는 한 한 번에 하나의 chart만 수정한다.

## 5. Chart Update Rules

- chart component 목록을 나열하는 제목 대신 명확한 한국어 보고서형 제목을 사용한다.
- chart type의 일반 목적만 설명하지 말고, 현재 example data가 무엇을 보여주는지 설명한다.
- chart data에서 보이는 구체 값을 포함한다.
- chart를 수정할 때 chart iframe view에 중복으로 보이는 내부 chart ID/title block을 제거한다.
- matching interpretation document와 method-variant chart guide를 함께 갱신한다.
- chart gallery가 database에서 title 또는 selection reason을 읽는 경우 live database 값도 갱신한다.
- `drift 보고서/charts/gallery.html`과 `drift 보고서/charts/gallery.js`의 chart asset cache version을 갱신한다.

## 6. Chart Verification

chart update 후 가능한 검증을 수행한다.

- `drift 보고서/charts/gallery.js` JavaScript syntax check
- 수정한 `drift 보고서/charts/chart_*.js` JavaScript syntax check
- server HTML에서 기존 title/duplicate ID가 사라지고 새 explanation이 보이는지 확인
- database에서 chart title과 variant mapping text가 갱신되었는지 확인
- commit 전 `git diff` 확인

완료된 chart update는 가능하면 chart 단위로 분리해 commit한다.
