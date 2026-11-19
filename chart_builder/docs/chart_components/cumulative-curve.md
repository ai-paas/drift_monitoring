# Cumulative Curve

Component key: `cumulative_curve`

## 목적

ECDF, CDF, 누적 score처럼 누적 형태의 곡선을 기준/현재 또는 여러 조건으로 비교한다.

## 주요 기능

- 분포 전체의 위치 이동과 shape 차이 확인
- KS D statistic처럼 최대 간격 표시 가능
- tail 영역 차이 확인

## 입력 데이터 계약

이 component는 renderer가 직접 DB row를 읽기보다, chart render layer가 만든 `chart_input_json` 일부를 받는 것을 전제로 한다.

```json
{
  "component": "cumulative_curve",
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
| `x_field` | 정렬된 값 또는 threshold index |
| `y_field` | 누적 확률 또는 누적 비율 |
| `series` | baseline/current 등 표시 series |
| `gap_marker` | 최대 차이 구간 표시 여부 |

## 파라미터 변경 시 화면 변화

- series를 하나만 두면 기준 곡선만 보이고 비교 해석은 약해진다.
- gap_marker를 켜면 KS류 해석처럼 최대 차이 위치가 강조된다.
- x_field를 score로 바꾸면 classifier score CDF 비교가 된다.

## 렌더링 규칙

- `visible=false`이면 layout slot은 유지하되 component body는 렌더링하지 않는다.
- 필수 field가 없으면 빈 chart를 그리지 않고 `missing data` 상태를 반환한다.
- threshold, event, annotation류 component와 조합될 수 있도록 좌표 scale을 외부에서 주입받을 수 있어야 한다.
- 색상은 chart별로 직접 고정하지 않고 semantic token을 사용한다. 예: `reference`, `current`, `warning`, `drift`, `highlight`.

## 적용 Chart

- `CHART-EDF-001`
- `CHART-EDF-002`
- `CHART-EDF-003`
- `CHART-EDF-004`
- `CHART-STREAM-002`
