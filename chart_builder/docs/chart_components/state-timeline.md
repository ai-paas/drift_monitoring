# State Timeline

Component key: `state_timeline`

## 목적

normal, warning, drift, retrain 등 detector 또는 workflow 상태가 시간에 따라 어떻게 바뀌는지 보여준다.

## 주요 기능

- 상태 구간을 색상 bar로 표시
- alarm marker와 결합
- detector가 어느 단계를 거쳐 drift로 갔는지 설명

## 입력 데이터 계약

이 component는 renderer가 직접 DB row를 읽기보다, chart render layer가 만든 `chart_input_json` 일부를 받는 것을 전제로 한다.

```json
{
  "component": "state_timeline",
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
| `time_field` | 시간 또는 window index |
| `state_field` | 상태값 |
| `state_palette` | 상태별 색상 |
| `segment_merge` | 연속 같은 상태를 하나의 segment로 합칠지 여부 |

## 파라미터 변경 시 화면 변화

- segment_merge=true이면 timeline이 간결해진다.
- state_palette를 운영 위험도 색상으로 바꾸면 warning/drift 해석이 명확해진다.
- state_field를 workflow status로 바꾸면 detector 상태가 아니라 운영 작업 상태 timeline이 된다.

## 렌더링 규칙

- `visible=false`이면 layout slot은 유지하되 component body는 렌더링하지 않는다.
- 필수 field가 없으면 빈 chart를 그리지 않고 `missing data` 상태를 반환한다.
- threshold, event, annotation류 component와 조합될 수 있도록 좌표 scale을 외부에서 주입받을 수 있어야 한다.
- 색상은 chart별로 직접 고정하지 않고 semantic token을 사용한다. 예: `reference`, `current`, `warning`, `drift`, `highlight`.

## 적용 Chart

- `CHART-ADAPT-001`
- `CHART-ADAPT-002`
- `CHART-ANOM-001`
- `CHART-CTRL-002`
- `CHART-ERR-001`
- `CHART-ERR-002`
- `CHART-ERR-003`
- `CHART-ERR-004`
- `CHART-ERR-005`
- `CHART-ERR-006`
- `CHART-HIST-001`
- `CHART-STREAM-003`
- `CHART-STREAM-004`
- `CHART-STREAM-005`
