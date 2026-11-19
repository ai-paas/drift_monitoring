# Heatmap

Component key: `heatmap`

## 목적

feature, class, segment, time bucket의 값을 색상 강도로 비교한다.

## 주요 기능

- 다차원 drift pattern을 압축 표시
- 큰 값 또는 위험 cell 강조
- matrix 형태의 차이를 빠르게 탐색

## 입력 데이터 계약

이 component는 renderer가 직접 DB row를 읽기보다, chart render layer가 만든 `chart_input_json` 일부를 받는 것을 전제로 한다.

```json
{
  "component": "heatmap",
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
| `x_field` | 열 기준 |
| `y_field` | 행 기준 |
| `value_field` | 색상으로 표현할 값 |
| `color_scale` | sequential, diverging, categorical |
| `highlight_threshold` | 강조 기준값 |

## 파라미터 변경 시 화면 변화

- color_scale=diverging이면 증가/감소 방향이 동시에 보인다.
- highlight_threshold를 낮추면 더 많은 cell이 위험 후보로 표시된다.
- x_field를 time으로 바꾸면 temporal heatmap이 된다.

## 렌더링 규칙

- `visible=false`이면 layout slot은 유지하되 component body는 렌더링하지 않는다.
- 필수 field가 없으면 빈 chart를 그리지 않고 `missing data` 상태를 반환한다.
- threshold, event, annotation류 component와 조합될 수 있도록 좌표 scale을 외부에서 주입받을 수 있어야 한다.
- 색상은 chart별로 직접 고정하지 않고 semantic token을 사용한다. 예: `reference`, `current`, `warning`, `drift`, `highlight`.

## 적용 Chart

- `CHART-BOCD-001`
- `CHART-EXPL-001`
- `CHART-MV-003`
- `CHART-REP-001`
- `CHART-REP-003`
