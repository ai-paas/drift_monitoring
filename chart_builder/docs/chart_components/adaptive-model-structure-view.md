# Adaptive Model Structure View

Component key: `adaptive_model_structure_view`

## 목적

adaptive tree, champion/challenger, alternate model처럼 모델 구조가 drift 대응 과정에서 어떻게 바뀌는지 보여준다.

## 주요 기능

- main model과 alternate model의 크기 또는 성능 변화 표시
- replacement, promotion, retraining 같은 구조 변경 이벤트 표시
- 모델 구조 변화와 성능 회복 여부를 함께 해석

## 입력 데이터 계약

이 component는 renderer가 직접 DB row를 읽기보다, chart render layer가 만든 `chart_input_json` 일부를 받는 것을 전제로 한다.

```json
{
  "component": "adaptive_model_structure_view",
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
| `structure_metric` | tree_size, node_count, model_version_count 등 구조 크기 지표 |
| `primary_series` | 운영 모델 series |
| `secondary_series` | alternate/challenger model series |
| `event_types` | replacement, promotion, retrain 등의 표시 대상 이벤트 |

## 파라미터 변경 시 화면 변화

- structure_metric을 바꾸면 y축 의미가 tree size에서 model count 등으로 바뀐다.
- secondary_series를 끄면 단일 모델 구조 추세만 남는다.
- event_types에 replacement만 남기면 구조 변경 중 실제 교체 시점만 강조된다.

## 렌더링 규칙

- `visible=false`이면 layout slot은 유지하되 component body는 렌더링하지 않는다.
- 필수 field가 없으면 빈 chart를 그리지 않고 `missing data` 상태를 반환한다.
- threshold, event, annotation류 component와 조합될 수 있도록 좌표 scale을 외부에서 주입받을 수 있어야 한다.
- 색상은 chart별로 직접 고정하지 않고 semantic token을 사용한다. 예: `reference`, `current`, `warning`, `drift`, `highlight`.

## 적용 Chart

- `CHART-ADAPT-001`
- `CHART-ADAPT-002`
