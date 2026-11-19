# Projection Scatter

Component key: `projection_scatter`

## 목적

embedding, PCA, UMAP 등 고차원 representation을 2D로 투영해 cluster 이동을 보여준다.

## 주요 기능

- baseline/current cluster 분리 확인
- centroid shift line 표시
- representation drift 또는 semantic drift 해석

## 입력 데이터 계약

이 component는 renderer가 직접 DB row를 읽기보다, chart render layer가 만든 `chart_input_json` 일부를 받는 것을 전제로 한다.

```json
{
  "component": "projection_scatter",
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
| `x_field` | 투영 x좌표 |
| `y_field` | 투영 y좌표 |
| `group_field` | baseline/current 또는 class |
| `centroid` | centroid 표시 여부 |
| `sample_limit` | 표시 sample 수 |

## 파라미터 변경 시 화면 변화

- sample_limit을 줄이면 렌더링은 빨라지지만 밀도 감각이 약해진다.
- centroid=true이면 전체 이동 방향이 명확해진다.
- group_field를 class로 바꾸면 class별 representation 분리를 볼 수 있다.

## 렌더링 규칙

- `visible=false`이면 layout slot은 유지하되 component body는 렌더링하지 않는다.
- 필수 field가 없으면 빈 chart를 그리지 않고 `missing data` 상태를 반환한다.
- threshold, event, annotation류 component와 조합될 수 있도록 좌표 scale을 외부에서 주입받을 수 있어야 한다.
- 색상은 chart별로 직접 고정하지 않고 semantic token을 사용한다. 예: `reference`, `current`, `warning`, `drift`, `highlight`.

## 적용 Chart

- `CHART-ANNOT-002`
- `CHART-ANOM-001`
- `CHART-CLS-001`
- `CHART-MV-001`
- `CHART-MV-002`
- `CHART-MV-004`
- `CHART-MV-005`
- `CHART-REP-001`
- `CHART-REP-002`
- `CHART-REP-003`
- `CHART-TEXT-001`
- `CHART-TEXT-002`
