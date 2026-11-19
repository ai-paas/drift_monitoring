# Model Diagnostic Curve

Component key: `model_diagnostic_curve`

## 목적

ROC, calibration, reliability curve처럼 모델 진단 곡선을 보여준다.

## 주요 기능

- domain classifier 성능 확인
- calibration 이탈 확인
- drift detector가 모델 score를 이용할 때 보조 근거 제공

## 입력 데이터 계약

이 component는 renderer가 직접 DB row를 읽기보다, chart render layer가 만든 `chart_input_json` 일부를 받는 것을 전제로 한다.

```json
{
  "component": "model_diagnostic_curve",
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
| `curve_type` | roc, calibration, reliability |
| `x_field` | curve x축 |
| `y_field` | curve y축 |
| `reference_line` | diagonal 또는 perfect calibration line |

## 파라미터 변경 시 화면 변화

- curve_type=roc이면 domain 구분 가능성을 보고, calibration이면 예측 확률 신뢰도를 본다.
- reference_line을 켜면 이상적인 기준에서 얼마나 벗어났는지 명확해진다.
- x/y field를 바꾸면 PR curve 같은 다른 진단 곡선도 표현 가능하다.

## 렌더링 규칙

- `visible=false`이면 layout slot은 유지하되 component body는 렌더링하지 않는다.
- 필수 field가 없으면 빈 chart를 그리지 않고 `missing data` 상태를 반환한다.
- threshold, event, annotation류 component와 조합될 수 있도록 좌표 scale을 외부에서 주입받을 수 있어야 한다.
- 색상은 chart별로 직접 고정하지 않고 semantic token을 사용한다. 예: `reference`, `current`, `warning`, `drift`, `highlight`.

## 적용 Chart

- `CHART-ADAPT-002`
- `CHART-CLS-001`
- `CHART-RANK-001`
- `CHART-TEXT-001`
- `CHART-TEXT-002`
- `CHART-UNC-001`
