# Small Multiples

Component key: `small_multiples`

## 목적

여러 metric 또는 feature의 작은 chart를 같은 축/형식으로 반복 표시한다.

## 주요 기능

- metric별 time-aligned movement 비교
- 많은 feature를 한 화면에서 균일하게 확인
- 한 feature만 큰지 전체적으로 움직이는지 구분

## 입력 데이터 계약

이 component는 renderer가 직접 DB row를 읽기보다, chart render layer가 만든 `chart_input_json` 일부를 받는 것을 전제로 한다.

```json
{
  "component": "small_multiples",
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
| `facet_field` | 작은 chart를 나눌 기준 |
| `value_field` | 각 chart의 y값 |
| `shared_scale` | 모든 panel이 같은 축을 쓰는지 여부 |
| `max_panels` | 표시할 panel 수 |

## 파라미터 변경 시 화면 변화

- shared_scale=true이면 feature 간 크기 비교가 가능하다.
- shared_scale=false이면 각 feature의 내부 변화가 더 잘 보인다.
- max_panels를 줄이면 top feature 중심 dashboard가 된다.

## 렌더링 규칙

- `visible=false`이면 layout slot은 유지하되 component body는 렌더링하지 않는다.
- 필수 field가 없으면 빈 chart를 그리지 않고 `missing data` 상태를 반환한다.
- threshold, event, annotation류 component와 조합될 수 있도록 좌표 scale을 외부에서 주입받을 수 있어야 한다.
- 색상은 chart별로 직접 고정하지 않고 semantic token을 사용한다. 예: `reference`, `current`, `warning`, `drift`, `highlight`.

## 적용 Chart

- `CHART-CTRL-003`
