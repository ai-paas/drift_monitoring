# Threshold Line

Component key: `threshold_line`

## 목적

판정 기준, 허용 오차, control limit, alpha 기준 등을 선으로 표시한다.

## 주요 기능

- 값이 기준을 넘는지 즉시 확인
- 상한/하한/중심선 모두 표현
- alarm marker와 함께 drift 판단 근거 제공

## 입력 데이터 계약

이 component는 renderer가 직접 DB row를 읽기보다, chart render layer가 만든 `chart_input_json` 일부를 받는 것을 전제로 한다.

```json
{
  "component": "threshold_line",
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
| `threshold_value` | 기준값 |
| `threshold_type` | upper, lower, two_sided, center |
| `line_style` | solid, dashed, dotted |
| `label` | 선 옆 표시 문구 |

## 파라미터 변경 시 화면 변화

- threshold_type=lower이면 값이 아래로 내려갈 때 위험으로 해석된다.
- two_sided이면 UCL/LCL 두 선이 생긴다.
- line_style을 dashed로 두면 data series와 구분하기 쉽다.

## 렌더링 규칙

- `visible=false`이면 layout slot은 유지하되 component body는 렌더링하지 않는다.
- 필수 field가 없으면 빈 chart를 그리지 않고 `missing data` 상태를 반환한다.
- threshold, event, annotation류 component와 조합될 수 있도록 좌표 scale을 외부에서 주입받을 수 있어야 한다.
- 색상은 chart별로 직접 고정하지 않고 semantic token을 사용한다. 예: `reference`, `current`, `warning`, `drift`, `highlight`.

## 적용 Chart

- `CHART-ANNOT-002`
- `CHART-ANOM-001`
- `CHART-CAT-002`
- `CHART-CTRL-001`
- `CHART-CTRL-002`
- `CHART-CTRL-003`
- `CHART-DIST-001`
- `CHART-ERR-001`
- `CHART-ERR-002`
- `CHART-ERR-003`
- `CHART-ERR-004`
- `CHART-ERR-005`
- `CHART-ERR-006`
- `CHART-GEN-001`
- `CHART-HIST-001`
- `CHART-MV-001`
- `CHART-MV-002`
- `CHART-MV-003`
- `CHART-MV-004`
- `CHART-MV-005`
- `CHART-PROB-001`
- `CHART-PROB-002`
- `CHART-PROB-003`
- `CHART-REP-002`
- `CHART-REP-003`
- `CHART-STREAM-002`
- `CHART-STREAM-003`
- `CHART-STREAM-004`
- `CHART-STREAM-005`
- `CHART-TEXT-001`
- `CHART-UNC-001`
