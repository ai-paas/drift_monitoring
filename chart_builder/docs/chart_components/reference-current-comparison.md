# Reference Current Comparison

Component key: `reference_current_comparison`

## 목적

기준 구간과 현재 구간을 명시적으로 비교하는 모든 component의 공통 의미를 정의한다.

## 주요 기능

- baseline/reference와 current series 구분
- 같은 scale에서 직접 비교
- drift 해석의 기본 문맥 제공

## 입력 데이터 계약

이 component는 renderer가 직접 DB row를 읽기보다, chart render layer가 만든 `chart_input_json` 일부를 받는 것을 전제로 한다.

```json
{
  "component": "reference_current_comparison",
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
| `reference_label` | 기준 구간 label |
| `current_label` | 현재 구간 label |
| `reference_color` | 기준 색상 |
| `current_color` | 현재 색상 |
| `comparison_mode` | overlay, side_by_side, delta |

## 파라미터 변경 시 화면 변화

- comparison_mode=overlay이면 분포 겹침이 잘 보인다.
- side_by_side는 category나 bin 비교에 적합하다.
- delta는 변화량만 강조해 원래 크기 정보는 줄어든다.

## 렌더링 규칙

- `visible=false`이면 layout slot은 유지하되 component body는 렌더링하지 않는다.
- 필수 field가 없으면 빈 chart를 그리지 않고 `missing data` 상태를 반환한다.
- threshold, event, annotation류 component와 조합될 수 있도록 좌표 scale을 외부에서 주입받을 수 있어야 한다.
- 색상은 chart별로 직접 고정하지 않고 semantic token을 사용한다. 예: `reference`, `current`, `warning`, `drift`, `highlight`.

## 적용 Chart

- `CHART-ANNOT-001`
- `CHART-ANNOT-002`
- `CHART-ANOM-001`
- `CHART-CLS-001`
- `CHART-EXPL-001`
- `CHART-EXPL-002`
- `CHART-GEN-001`
- `CHART-REP-001`
- `CHART-REP-002`
- `CHART-REP-003`
- `CHART-STREAM-004`
- `CHART-TEXT-001`
- `CHART-TEXT-002`
- `CHART-UNC-001`
