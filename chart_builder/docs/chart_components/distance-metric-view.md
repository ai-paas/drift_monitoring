# Distance Metric View

Component key: `distance_metric_view`

## 목적

reference와 current 사이의 거리 또는 divergence를 feature/window별로 보여준다.

## 주요 기능

- Wasserstein, MMD, Energy distance, JS distance 등 거리 값 표시
- window별 거리 추세와 feature별 거리 순위 연결
- 분포 이동 크기를 정량적으로 설명

## 입력 데이터 계약

이 component는 renderer가 직접 DB row를 읽기보다, chart render layer가 만든 `chart_input_json` 일부를 받는 것을 전제로 한다.

```json
{
  "component": "distance_metric_view",
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
| `distance_field` | 거리 값 field |
| `group_field` | feature, segment, window 등 묶음 기준 |
| `normalize` | feature scale 보정 여부 |
| `baseline_distance` | 비교 기준 거리 |

## 파라미터 변경 시 화면 변화

- group_field를 feature로 두면 feature ranking chart가 된다.
- group_field를 window로 두면 drift score trend가 된다.
- normalize=true이면 scale이 큰 feature가 과도하게 강조되는 것을 줄인다.

## 렌더링 규칙

- `visible=false`이면 layout slot은 유지하되 component body는 렌더링하지 않는다.
- 필수 field가 없으면 빈 chart를 그리지 않고 `missing data` 상태를 반환한다.
- threshold, event, annotation류 component와 조합될 수 있도록 좌표 scale을 외부에서 주입받을 수 있어야 한다.
- 색상은 chart별로 직접 고정하지 않고 semantic token을 사용한다. 예: `reference`, `current`, `warning`, `drift`, `highlight`.

## 적용 Chart

- `CHART-CAT-002`
- `CHART-CAT-003`
- `CHART-DIST-001`
- `CHART-ERR-003`
- `CHART-MV-001`
- `CHART-MV-002`
- `CHART-MV-005`
- `CHART-PROB-002`
- `CHART-PROB-003`
- `CHART-REP-003`
- `CHART-TEXT-001`
