# Ranking View

Component key: `ranking_view`

## 목적

feature, category, segment를 drift score 또는 distance 순서로 정렬해 보여준다.

## 주요 기능

- 상위 drift 후보 빠른 탐색
- 원인 후보 prioritization
- 여러 item 중 어디를 먼저 볼지 결정

## 입력 데이터 계약

이 component는 renderer가 직접 DB row를 읽기보다, chart render layer가 만든 `chart_input_json` 일부를 받는 것을 전제로 한다.

```json
{
  "component": "ranking_view",
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
| `item_field` | 순위 대상 |
| `score_field` | 정렬 기준 |
| `top_n` | 표시할 항목 수 |
| `tie_breaker` | 동점 처리 기준 |

## 파라미터 변경 시 화면 변화

- top_n을 줄이면 보고서용 핵심 항목만 남는다.
- score_field를 p-value로 쓰면 정렬 방향을 낮은 값 우선으로 바꿔야 한다.
- tie_breaker를 sample_size로 두면 신뢰도 높은 항목이 우선된다.

## 렌더링 규칙

- `visible=false`이면 layout slot은 유지하되 component body는 렌더링하지 않는다.
- 필수 field가 없으면 빈 chart를 그리지 않고 `missing data` 상태를 반환한다.
- threshold, event, annotation류 component와 조합될 수 있도록 좌표 scale을 외부에서 주입받을 수 있어야 한다.
- 색상은 chart별로 직접 고정하지 않고 semantic token을 사용한다. 예: `reference`, `current`, `warning`, `drift`, `highlight`.

## 적용 Chart

- `CHART-EXPL-001`
- `CHART-RANK-001`
