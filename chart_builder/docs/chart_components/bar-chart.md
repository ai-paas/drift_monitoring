# Bar Chart

Component key: `bar_chart`

## 목적

category, feature, metric별 값을 막대 길이로 비교한다.

## 주요 기능

- 기여도, 비율, score, error, 성능 지표 등을 category 축으로 비교
- top item 또는 threshold 초과 항목 강조
- horizontal/vertical 방향 모두 지원 가능

## 입력 데이터 계약

이 component는 renderer가 직접 DB row를 읽기보다, chart render layer가 만든 `chart_input_json` 일부를 받는 것을 전제로 한다.

```json
{
  "component": "bar_chart",
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
| `orientation` | vertical 또는 horizontal |
| `category_field` | 막대 label로 사용할 field |
| `value_field` | 막대 길이로 사용할 numeric field |
| `highlight_rule` | max_value, threshold_exceeded, selected_category 등 강조 규칙 |
| `sort_order` | none, ascending, descending, value_desc |

## 파라미터 변경 시 화면 변화

- orientation을 horizontal로 바꾸면 긴 category 이름을 읽기 쉬운 ranking형 화면이 된다.
- value_field를 contribution_value에서 proportion으로 바꾸면 기여도 chart가 비율 chart로 바뀐다.
- highlight_rule을 threshold_exceeded로 바꾸면 가장 큰 값이 아니라 기준 초과 막대가 강조된다.

## 렌더링 규칙

- `visible=false`이면 layout slot은 유지하되 component body는 렌더링하지 않는다.
- 필수 field가 없으면 빈 chart를 그리지 않고 `missing data` 상태를 반환한다.
- threshold, event, annotation류 component와 조합될 수 있도록 좌표 scale을 외부에서 주입받을 수 있어야 한다.
- 색상은 chart별로 직접 고정하지 않고 semantic token을 사용한다. 예: `reference`, `current`, `warning`, `drift`, `highlight`.

## 적용 Chart

- `CHART-CAT-003`
- `CHART-CAT-004`
- `CHART-CLS-001`
- `CHART-CTRL-003`
- `CHART-EXPL-001`
- `CHART-EXPL-002`
- `CHART-PROB-002`
- `CHART-PSI-001`
- `CHART-TEXT-001`
- `CHART-TEXT-002`
- `CHART-UNC-001`
- `CHART-VAR-001`
