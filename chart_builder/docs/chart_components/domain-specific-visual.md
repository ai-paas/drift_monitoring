# Domain Specific Visual

Component key: `domain_specific_visual`

## 목적

아직 공통 컴포넌트로 일반화하지 않은 차트별 특수 시각 요소를 나타낸다.

## 주요 기능

- 특정 알고리즘이나 도메인에만 있는 표현 보존
- 향후 공통 component 후보를 찾기 위한 임시 분류
- 완전한 일반화 이전의 escape hatch 역할

## 입력 데이터 계약

이 component는 renderer가 직접 DB row를 읽기보다, chart render layer가 만든 `chart_input_json` 일부를 받는 것을 전제로 한다.

```json
{
  "component": "domain_specific_visual",
  "data": [],
  "config": {}
}
```

## 주요 파라미터

| 파라미터 | 설명 |
|---|---|
| `title` | component 제목. 비우면 chart section 제목이나 chart_definition의 표시명을 사용한다. |
| `position` | layout 내 위치. 예: main, side_top, side_bottom, summary, overlay. |
| `data_source` | algorithm_result, chart_input_json, static_example 중 어떤 데이터를 읽을지 지정한다. |
| `visible` | false이면 component를 렌더링하지 않는다. |
| `visual_code` | 특수 시각화 식별자 |
| `input_schema` | 해당 시각화에 필요한 입력 구조 |
| `fallback_component` | 대체 가능한 일반 component |
| `generalization_candidate` | 공통화 후보 여부 |

## 파라미터 변경 시 화면 변화

- fallback_component를 지정하면 특수 renderer가 없을 때 일반 chart로 대체된다.
- generalization_candidate=true이면 다음 component 정규화 대상이 된다.
- input_schema를 명확히 하면 나중에 별도 component로 승격하기 쉽다.

## 렌더링 규칙

- `visible=false`이면 layout slot은 유지하되 component body는 렌더링하지 않는다.
- 필수 field가 없으면 빈 chart를 그리지 않고 `missing data` 상태를 반환한다.
- threshold, event, annotation류 component와 조합될 수 있도록 좌표 scale을 외부에서 주입받을 수 있어야 한다.
- 색상은 chart별로 직접 고정하지 않고 semantic token을 사용한다. 예: `reference`, `current`, `warning`, `drift`, `highlight`.

## 적용 Chart

- `CHART-ANNOT-001`
- `CHART-CAT-001`
- `CHART-CAT-002`
- `CHART-CAT-003`
- `CHART-CAT-004`
- `CHART-CLS-001`
- `CHART-CTRL-001`
- `CHART-DIST-001`
- `CHART-DISTSHAPE-001`
- `CHART-EDF-001`
- `CHART-EDF-002`
- `CHART-EDF-003`
- `CHART-EDF-004`
- `CHART-ERR-001`
- `CHART-ERR-002`
- `CHART-EXPL-002`
- `CHART-GEN-001`
- `CHART-MEAN-001`
- `CHART-MV-001`
- `CHART-MV-003`
- `CHART-MV-004`
- `CHART-MV-005`
- `CHART-PROB-001`
- `CHART-PROB-002`
- `CHART-PROB-003`
- `CHART-PSI-001`
- `CHART-RANK-001`
- `CHART-REP-001`
- `CHART-REP-003`
- `CHART-STREAM-001`
- `CHART-STREAM-003`
- `CHART-STREAM-005`
- `CHART-VAR-001`
