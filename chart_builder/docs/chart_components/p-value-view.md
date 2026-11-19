# P Value View

Component key: `p_value_view`

## 목적

통계 검정의 p-value와 유의수준을 시각적으로 비교한다.

## 주요 기능

- alpha 기준선 표시
- p-value가 낮을수록 drift evidence가 커지는 방향 명시
- 여러 feature 또는 window의 p-value 비교

## 입력 데이터 계약

이 component는 renderer가 직접 DB row를 읽기보다, chart render layer가 만든 `chart_input_json` 일부를 받는 것을 전제로 한다.

```json
{
  "component": "p_value_view",
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
| `p_value_field` | p-value 값 |
| `alpha` | 유의수준 |
| `transform` | none 또는 -log10 |
| `multiple_testing_adjustment` | none, bonferroni, fdr |

## 파라미터 변경 시 화면 변화

- transform=-log10이면 작은 p-value 차이가 크게 보인다.
- alpha를 낮추면 더 엄격한 drift 후보 기준이 된다.
- multiple_testing_adjustment를 켜면 feature가 많을 때 과탐지를 줄인다.

## 렌더링 규칙

- `visible=false`이면 layout slot은 유지하되 component body는 렌더링하지 않는다.
- 필수 field가 없으면 빈 chart를 그리지 않고 `missing data` 상태를 반환한다.
- threshold, event, annotation류 component와 조합될 수 있도록 좌표 scale을 외부에서 주입받을 수 있어야 한다.
- 색상은 chart별로 직접 고정하지 않고 semantic token을 사용한다. 예: `reference`, `current`, `warning`, `drift`, `highlight`.

## 적용 Chart

- `CHART-CAT-001`
- `CHART-EDF-001`
- `CHART-EDF-002`
- `CHART-EDF-003`
- `CHART-EDF-004`
- `CHART-EXPL-001`
- `CHART-GEN-001`
- `CHART-MEAN-001`
- `CHART-MV-001`
- `CHART-MV-002`
- `CHART-MV-003`
