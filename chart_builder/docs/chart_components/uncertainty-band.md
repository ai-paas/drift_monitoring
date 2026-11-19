# Uncertainty Band

Component key: `uncertainty_band`

## 목적

confidence interval, approximation error band, predictive uncertainty 범위를 면적으로 보여준다.

## 주요 기능

- 중심선 주변 불확실성 표현
- 허용 오차 초과 여부 확인
- approximation 또는 forecast 신뢰도 설명

## 입력 데이터 계약

이 component는 renderer가 직접 DB row를 읽기보다, chart render layer가 만든 `chart_input_json` 일부를 받는 것을 전제로 한다.

```json
{
  "component": "uncertainty_band",
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
| `lower_field` | 하한 |
| `upper_field` | 상한 |
| `center_field` | 중심선 |
| `band_opacity` | band 투명도 |
| `band_mode` | confidence_interval, error_range, prediction_interval |

## 파라미터 변경 시 화면 변화

- band_opacity를 높이면 불확실성 영역이 더 강하게 보인다.
- center_field가 없으면 범위만 표시된다.
- band_mode를 error_range로 쓰면 prediction보다 approximation 품질 해석에 맞춰진다.

## 렌더링 규칙

- `visible=false`이면 layout slot은 유지하되 component body는 렌더링하지 않는다.
- 필수 field가 없으면 빈 chart를 그리지 않고 `missing data` 상태를 반환한다.
- threshold, event, annotation류 component와 조합될 수 있도록 좌표 scale을 외부에서 주입받을 수 있어야 한다.
- 색상은 chart별로 직접 고정하지 않고 semantic token을 사용한다. 예: `reference`, `current`, `warning`, `drift`, `highlight`.

## 적용 Chart

- `CHART-ANNOT-002`
- `CHART-CAT-004`
- `CHART-EDF-004`
- `CHART-ERR-005`
- `CHART-MEAN-001`
- `CHART-MV-002`
- `CHART-PROB-003`
- `CHART-STREAM-004`
- `CHART-STREAM-005`
- `CHART-UNC-001`
