# Matrix View

Component key: `matrix_view`

## 목적

method와 condition, variant와 capability 같은 조합 관계를 matrix로 표시한다.

## 주요 기능

- 적용 가능/불가, 사용 권장 여부 표현
- 여러 method variant를 한 화면에서 비교
- 선택 규칙을 구조적으로 보여줌

## 입력 데이터 계약

이 component는 renderer가 직접 DB row를 읽기보다, chart render layer가 만든 `chart_input_json` 일부를 받는 것을 전제로 한다.

```json
{
  "component": "matrix_view",
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
| `row_field` | 행 기준 |
| `column_field` | 열 기준 |
| `cell_value_field` | cell 상태 |
| `cell_palette` | 상태별 색상 |

## 파라미터 변경 시 화면 변화

- cell_value_field가 boolean이면 단순 적용 matrix가 된다.
- score 값이면 heatmap형 matrix가 된다.
- row/column을 바꾸면 method 중심 또는 condition 중심 보기로 전환된다.

## 렌더링 규칙

- `visible=false`이면 layout slot은 유지하되 component body는 렌더링하지 않는다.
- 필수 field가 없으면 빈 chart를 그리지 않고 `missing data` 상태를 반환한다.
- threshold, event, annotation류 component와 조합될 수 있도록 좌표 scale을 외부에서 주입받을 수 있어야 한다.
- 색상은 chart별로 직접 고정하지 않고 semantic token을 사용한다. 예: `reference`, `current`, `warning`, `drift`, `highlight`.

## 적용 Chart

- `CHART-ANNOT-001`
