# Comparison Table

Component key: `comparison_table`

## 목적

두 개 이상의 모델, 기간, detector, metric 값을 행/열 구조로 비교한다.

## 주요 기능

- champion/challenger 또는 pre/post 비교
- 여러 metric을 같은 scale이 아닌 원값으로 표시
- 차트보다 정확한 숫자 확인에 적합

## 입력 데이터 계약

이 component는 renderer가 직접 DB row를 읽기보다, chart render layer가 만든 `chart_input_json` 일부를 받는 것을 전제로 한다.

```json
{
  "component": "comparison_table",
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
| `row_field` | 행 label |
| `columns` | 표시할 metric 목록 |
| `compare_baseline` | baseline 또는 reference column |
| `delta_mode` | absolute, percent, point_diff |

## 파라미터 변경 시 화면 변화

- columns를 늘리면 표의 정보량은 늘지만 작은 panel에서는 가독성이 떨어진다.
- delta_mode를 percent로 바꾸면 상대 개선/악화 중심으로 보인다.
- compare_baseline을 끄면 단순 metric table이 된다.

## 렌더링 규칙

- `visible=false`이면 layout slot은 유지하되 component body는 렌더링하지 않는다.
- 필수 field가 없으면 빈 chart를 그리지 않고 `missing data` 상태를 반환한다.
- threshold, event, annotation류 component와 조합될 수 있도록 좌표 scale을 외부에서 주입받을 수 있어야 한다.
- 색상은 chart별로 직접 고정하지 않고 semantic token을 사용한다. 예: `reference`, `current`, `warning`, `drift`, `highlight`.

## 적용 Chart

- `CHART-ERR-002`
- `CHART-EXPL-002`
