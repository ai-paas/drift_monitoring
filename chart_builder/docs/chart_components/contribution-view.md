# Contribution View

Component key: `contribution_view`

## 목적

전체 drift score나 alarm에 어떤 feature, metric, descriptor가 가장 많이 기여했는지 보여준다.

## 주요 기능

- top contributor 강조
- 양/음 방향 기여도 구분
- 원인 후보 탐색을 위한 첫 화면 제공

## 입력 데이터 계약

이 component는 renderer가 직접 DB row를 읽기보다, chart render layer가 만든 `chart_input_json` 일부를 받는 것을 전제로 한다.

```json
{
  "component": "contribution_view",
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
| `contributor_field` | feature, metric, descriptor 이름 |
| `contribution_field` | 기여도 값 |
| `top_n` | 표시할 상위 항목 수 |
| `signed` | 양수/음수 기여를 구분할지 여부 |

## 파라미터 변경 시 화면 변화

- top_n을 줄이면 핵심 원인 후보만 남는다.
- signed=true이면 증가/감소 방향을 색상으로 나눌 수 있다.
- contribution_field를 absolute score로 바꾸면 방향성보다 크기 중심 해석이 된다.

## 렌더링 규칙

- `visible=false`이면 layout slot은 유지하되 component body는 렌더링하지 않는다.
- 필수 field가 없으면 빈 chart를 그리지 않고 `missing data` 상태를 반환한다.
- threshold, event, annotation류 component와 조합될 수 있도록 좌표 scale을 외부에서 주입받을 수 있어야 한다.
- 색상은 chart별로 직접 고정하지 않고 semantic token을 사용한다. 예: `reference`, `current`, `warning`, `drift`, `highlight`.

## 적용 Chart

- `CHART-CTRL-003`
- `CHART-MV-004`
- `CHART-PSI-001`
