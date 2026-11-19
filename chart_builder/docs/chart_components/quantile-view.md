# Quantile View

Component key: `quantile_view`

## 목적

q25, q50, q75, tail quantile처럼 분위수별 이동이나 오차를 보여준다.

## 주요 기능

- 중앙값과 tail 변화 분리
- approximation error 또는 distribution tail drift 확인
- 분포 평균만으로 보이지 않는 변화 설명

## 입력 데이터 계약

이 component는 renderer가 직접 DB row를 읽기보다, chart render layer가 만든 `chart_input_json` 일부를 받는 것을 전제로 한다.

```json
{
  "component": "quantile_view",
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
| `quantile_field` | 분위수 label |
| `value_field` | 분위수 값 또는 오차 |
| `target_line` | 허용 오차 또는 목표 기준 |
| `tail_emphasis` | tail 분위수 강조 여부 |

## 파라미터 변경 시 화면 변화

- tail_emphasis=true이면 극단 구간 변화가 강조된다.
- target_line을 추가하면 approximation 허용 여부가 즉시 보인다.
- value_field를 delta로 바꾸면 분위수 이동량 chart가 된다.

## 렌더링 규칙

- `visible=false`이면 layout slot은 유지하되 component body는 렌더링하지 않는다.
- 필수 field가 없으면 빈 chart를 그리지 않고 `missing data` 상태를 반환한다.
- threshold, event, annotation류 component와 조합될 수 있도록 좌표 scale을 외부에서 주입받을 수 있어야 한다.
- 색상은 chart별로 직접 고정하지 않고 semantic token을 사용한다. 예: `reference`, `current`, `warning`, `drift`, `highlight`.

## 적용 Chart

- `CHART-ANNOT-002`
- `CHART-EDF-002`
