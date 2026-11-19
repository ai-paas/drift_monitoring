# Histogram View

Component key: `histogram_view`

## 목적

값을 bin으로 나누어 기준/현재의 빈도 또는 비율 차이를 보여준다.

## 주요 기능

- bin별 분포 이동 확인
- PSI, histogram intersection, chi-square류 해석에 적합
- threshold 주변 sample 증가 여부 확인

## 입력 데이터 계약

이 component는 renderer가 직접 DB row를 읽기보다, chart render layer가 만든 `chart_input_json` 일부를 받는 것을 전제로 한다.

```json
{
  "component": "histogram_view",
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
| `bin_field` | bin label 또는 bin range |
| `count_field` | 빈도 |
| `proportion_field` | 비율 |
| `bin_count` | 자동 bin 생성 시 bin 수 |
| `overlay_mode` | side_by_side, stacked, overlay |

## 파라미터 변경 시 화면 변화

- bin_count를 늘리면 세부 변화가 보이지만 noise도 커진다.
- overlay_mode=side_by_side이면 기준/현재 bin별 비교가 명확하다.
- proportion_field를 쓰면 sample size 차이 영향을 줄인다.

## 렌더링 규칙

- `visible=false`이면 layout slot은 유지하되 component body는 렌더링하지 않는다.
- 필수 field가 없으면 빈 chart를 그리지 않고 `missing data` 상태를 반환한다.
- threshold, event, annotation류 component와 조합될 수 있도록 좌표 scale을 외부에서 주입받을 수 있어야 한다.
- 색상은 chart별로 직접 고정하지 않고 semantic token을 사용한다. 예: `reference`, `current`, `warning`, `drift`, `highlight`.

## 적용 Chart

- `CHART-HIST-001`
- `CHART-MV-001`
- `CHART-MV-002`
- `CHART-MV-003`
- `CHART-MV-005`
- `CHART-PROB-001`
- `CHART-PROB-003`
- `CHART-PSI-001`
- `CHART-RANK-001`
