# Trend Line

Component key: `trend_line`

## 목적

시간, window, projection count 등 순서 축을 따라 값이 어떻게 변하는지 선으로 보여준다.

## 주요 기능

- 증가/감소 방향 파악
- smoothing 또는 여러 series 비교
- event marker, threshold line과 결합 가능

## 입력 데이터 계약

이 component는 renderer가 직접 DB row를 읽기보다, chart render layer가 만든 `chart_input_json` 일부를 받는 것을 전제로 한다.

```json
{
  "component": "trend_line",
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
| `x_field` | 순서 또는 시간 축 |
| `y_field` | 표시 값 |
| `series_field` | 여러 선 구분 |
| `interpolation` | linear, step, smooth |
| `show_points` | 점 표시 여부 |

## 파라미터 변경 시 화면 변화

- interpolation=step이면 상태성 metric이나 window별 값을 계단형으로 볼 수 있다.
- show_points=true이면 실제 관측 window가 명확해진다.
- series_field를 지정하면 baseline/current 또는 champion/challenger 선이 함께 보인다.

## 렌더링 규칙

- `visible=false`이면 layout slot은 유지하되 component body는 렌더링하지 않는다.
- 필수 field가 없으면 빈 chart를 그리지 않고 `missing data` 상태를 반환한다.
- threshold, event, annotation류 component와 조합될 수 있도록 좌표 scale을 외부에서 주입받을 수 있어야 한다.
- 색상은 chart별로 직접 고정하지 않고 semantic token을 사용한다. 예: `reference`, `current`, `warning`, `drift`, `highlight`.

## 적용 Chart

- `CHART-ADAPT-001`
- `CHART-ADAPT-002`
- `CHART-ANNOT-001`
- `CHART-ANNOT-002`
- `CHART-ANOM-001`
- `CHART-BOCD-001`
- `CHART-CLS-001`
- `CHART-CTRL-001`
- `CHART-CTRL-002`
- `CHART-CTRL-003`
- `CHART-ERR-001`
- `CHART-ERR-002`
- `CHART-ERR-003`
- `CHART-ERR-004`
- `CHART-ERR-005`
- `CHART-ERR-006`
- `CHART-EXPL-001`
- `CHART-EXPL-002`
- `CHART-GEN-001`
- `CHART-REP-001`
- `CHART-REP-002`
- `CHART-REP-003`
- `CHART-STREAM-001`
- `CHART-STREAM-002`
- `CHART-STREAM-003`
- `CHART-STREAM-004`
- `CHART-STREAM-005`
- `CHART-TEXT-001`
- `CHART-TEXT-002`
- `CHART-UNC-001`
