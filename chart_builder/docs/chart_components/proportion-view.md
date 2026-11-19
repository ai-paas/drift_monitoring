# Proportion View

Component key: `proportion_view`

## 목적

category, class, topic, segment 비율이 기준 대비 어떻게 바뀌었는지 보여준다.

## 주요 기능

- stacked bar 또는 grouped bar로 비율 비교
- class prior shift, topic mix 변화 확인
- 증감 point 차이 표시

## 입력 데이터 계약

이 component는 renderer가 직접 DB row를 읽기보다, chart render layer가 만든 `chart_input_json` 일부를 받는 것을 전제로 한다.

```json
{
  "component": "proportion_view",
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
| `category_field` | 비율 category |
| `proportion_field` | 비율 값 |
| `series_field` | baseline/current |
| `display_mode` | stacked, grouped, delta |

## 파라미터 변경 시 화면 변화

- display_mode=delta이면 비율 자체보다 증감폭이 강조된다.
- stacked는 전체 composition을 보기 좋고 grouped는 category별 비교가 쉽다.
- category_field를 topic으로 바꾸면 topic drift chart가 된다.

## 렌더링 규칙

- `visible=false`이면 layout slot은 유지하되 component body는 렌더링하지 않는다.
- 필수 field가 없으면 빈 chart를 그리지 않고 `missing data` 상태를 반환한다.
- threshold, event, annotation류 component와 조합될 수 있도록 좌표 scale을 외부에서 주입받을 수 있어야 한다.
- 색상은 chart별로 직접 고정하지 않고 semantic token을 사용한다. 예: `reference`, `current`, `warning`, `drift`, `highlight`.

## 적용 Chart

- `CHART-CAT-001`
- `CHART-CAT-002`
- `CHART-CAT-003`
- `CHART-CAT-004`
- `CHART-CLS-001`
- `CHART-EXPL-001`
- `CHART-PROB-002`
- `CHART-STREAM-005`
- `CHART-TEXT-001`
- `CHART-TEXT-002`
- `CHART-UNC-001`
- `CHART-VAR-001`
