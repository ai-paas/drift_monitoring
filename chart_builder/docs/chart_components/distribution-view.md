# Distribution View

Component key: `distribution_view`

## 목적

기준/현재의 연속형 분포를 density, area, curve 형태로 비교한다.

## 주요 기능

- 분포 위치 이동, 폭 변화, tail 변화 확인
- reference/current overlay 제공
- distance metric의 시각적 근거 제공

## 입력 데이터 계약

이 component는 renderer가 직접 DB row를 읽기보다, chart render layer가 만든 `chart_input_json` 일부를 받는 것을 전제로 한다.

```json
{
  "component": "distribution_view",
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
| `value_field` | 분포 대상 numeric field |
| `series_field` | baseline/current 구분 |
| `density_method` | kde, histogram_density, empirical |
| `opacity` | 겹침 영역 투명도 |

## 파라미터 변경 시 화면 변화

- density_method를 kde로 쓰면 부드럽지만 세부 bin 변화는 약해진다.
- opacity를 낮추면 겹침 영역을 더 쉽게 볼 수 있다.
- series_field를 segment로 바꾸면 여러 segment 분포 비교가 된다.

## 렌더링 규칙

- `visible=false`이면 layout slot은 유지하되 component body는 렌더링하지 않는다.
- 필수 field가 없으면 빈 chart를 그리지 않고 `missing data` 상태를 반환한다.
- threshold, event, annotation류 component와 조합될 수 있도록 좌표 scale을 외부에서 주입받을 수 있어야 한다.
- 색상은 chart별로 직접 고정하지 않고 semantic token을 사용한다. 예: `reference`, `current`, `warning`, `drift`, `highlight`.

## 적용 Chart

- `CHART-ANOM-001`
- `CHART-CLS-001`
- `CHART-DISTSHAPE-001`
- `CHART-EXPL-001`
- `CHART-EXPL-002`
- `CHART-GEN-001`
- `CHART-MV-001`
- `CHART-MV-002`
- `CHART-MV-003`
- `CHART-REP-001`
- `CHART-REP-002`
- `CHART-TEXT-002`
- `CHART-UNC-001`
