# Distribution Summary Plot

Component key: `distribution_summary_plot`

## 목적

box, violin, spread plot처럼 분포의 중심, 산포, tail을 요약한다.

## 주요 기능

- median, IQR, outlier, density shape 확인
- rank/비모수 검정 결과와 함께 사용
- 분포 전체를 간결하게 비교

## 입력 데이터 계약

이 component는 renderer가 직접 DB row를 읽기보다, chart render layer가 만든 `chart_input_json` 일부를 받는 것을 전제로 한다.

```json
{
  "component": "distribution_summary_plot",
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
| `plot_type` | box, violin, box_violin |
| `group_field` | baseline/current 또는 segment |
| `value_field` | 분포를 만들 numeric field |
| `show_outliers` | outlier 표시 여부 |

## 파라미터 변경 시 화면 변화

- plot_type=violin이면 shape 차이가 더 잘 보이고 box이면 요약 통계가 선명해진다.
- show_outliers=false이면 tail 이상치보다 중심 분포가 강조된다.
- group_field를 segment로 바꾸면 segment별 drift 비교가 된다.

## 렌더링 규칙

- `visible=false`이면 layout slot은 유지하되 component body는 렌더링하지 않는다.
- 필수 field가 없으면 빈 chart를 그리지 않고 `missing data` 상태를 반환한다.
- threshold, event, annotation류 component와 조합될 수 있도록 좌표 scale을 외부에서 주입받을 수 있어야 한다.
- 색상은 chart별로 직접 고정하지 않고 semantic token을 사용한다. 예: `reference`, `current`, `warning`, `drift`, `highlight`.

## 적용 Chart

- `CHART-ANNOT-002`
- `CHART-MEAN-001`
- `CHART-RANK-001`
- `CHART-VAR-001`
