# Performance Metric View

Component key: `performance_metric_view`

## 목적

accuracy, AUC, F1, latency, error rate, confidence, entropy 같은 운영 성능/품질 지표를 보여준다.

## 주요 기능

- 성능 저하 또는 불확실성 증가 추세 확인
- pre/post retraining 비교
- model impact 판단의 보조 근거 제공

## 입력 데이터 계약

이 component는 renderer가 직접 DB row를 읽기보다, chart render layer가 만든 `chart_input_json` 일부를 받는 것을 전제로 한다.

```json
{
  "component": "performance_metric_view",
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
| `metric_field` | 표시 metric |
| `direction` | higher_is_better 또는 lower_is_better |
| `baseline_value` | 비교 기준값 |
| `target_value` | 운영 목표값 |

## 파라미터 변경 시 화면 변화

- direction이 lower_is_better이면 latency/error rate처럼 낮을수록 좋은 지표로 해석된다.
- target_value를 표시하면 단순 변화보다 SLA 위반 여부가 강조된다.
- metric_field를 entropy로 바꾸면 성능이 아니라 uncertainty 관점이 된다.

## 렌더링 규칙

- `visible=false`이면 layout slot은 유지하되 component body는 렌더링하지 않는다.
- 필수 field가 없으면 빈 chart를 그리지 않고 `missing data` 상태를 반환한다.
- threshold, event, annotation류 component와 조합될 수 있도록 좌표 scale을 외부에서 주입받을 수 있어야 한다.
- 색상은 chart별로 직접 고정하지 않고 semantic token을 사용한다. 예: `reference`, `current`, `warning`, `drift`, `highlight`.

## 적용 Chart

- `CHART-ADAPT-001`
- `CHART-ADAPT-002`
- `CHART-CAT-004`
- `CHART-CLS-001`
- `CHART-ERR-001`
- `CHART-ERR-002`
- `CHART-ERR-004`
- `CHART-ERR-006`
- `CHART-GEN-001`
- `CHART-MEAN-001`
- `CHART-RANK-001`
- `CHART-STREAM-005`
- `CHART-TEXT-002`
- `CHART-UNC-001`
