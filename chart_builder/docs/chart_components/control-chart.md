# Control Chart

Component key: `control_chart`

## 목적

통계량 또는 metric이 중심선과 관리한계선을 기준으로 정상 범위를 벗어나는지 보여준다.

## 주요 기능

- center line, UCL, LCL 표시
- CUSUM, EWMA, MEWMA 같은 control statistic 표시
- alarm 상태를 시계열로 확인

## 입력 데이터 계약

이 component는 renderer가 직접 DB row를 읽기보다, chart render layer가 만든 `chart_input_json` 일부를 받는 것을 전제로 한다.

```json
{
  "component": "control_chart",
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
| `statistic_field` | 표시할 control statistic |
| `center_value` | 중심선 |
| `ucl` | 상한 관리한계 |
| `lcl` | 하한 관리한계 |
| `smoothing` | EWMA/GMA 계열 smoothing 값 |

## 파라미터 변경 시 화면 변화

- ucl/lcl을 좁히면 alarm이 더 자주 발생하는 화면이 된다.
- smoothing을 높이면 최근 변화에 둔감하고 안정적인 선이 된다.
- center_value를 이동 평균으로 바꾸면 동적 기준선 control chart가 된다.

## 렌더링 규칙

- `visible=false`이면 layout slot은 유지하되 component body는 렌더링하지 않는다.
- 필수 field가 없으면 빈 chart를 그리지 않고 `missing data` 상태를 반환한다.
- threshold, event, annotation류 component와 조합될 수 있도록 좌표 scale을 외부에서 주입받을 수 있어야 한다.
- 색상은 chart별로 직접 고정하지 않고 semantic token을 사용한다. 예: `reference`, `current`, `warning`, `drift`, `highlight`.

## 적용 Chart

- `CHART-CTRL-001`
- `CHART-CTRL-002`
