# Raw Signal Trend

Component key: `raw_signal_trend`

## 목적

detector statistic 이전의 원 관측값 또는 운영 metric 흐름을 보여준다.

## 주요 기능

- stream value, raw metric, error rate, online accuracy 표시
- detector alarm이 실제 signal 변화와 맞는지 확인
- 일시 spike와 지속 trend 구분

## 입력 데이터 계약

이 component는 renderer가 직접 DB row를 읽기보다, chart render layer가 만든 `chart_input_json` 일부를 받는 것을 전제로 한다.

```json
{
  "component": "raw_signal_trend",
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
| `value_field` | 원 signal 값 |
| `reference_value` | 기준 평균 또는 기준선 |
| `smoothing_window` | 선택적 이동 평균 window |

## 파라미터 변경 시 화면 변화

- smoothing_window를 키우면 noise가 줄지만 급격한 변화가 늦게 보인다.
- reference_value를 표시하면 current signal이 기준에서 얼마나 벗어났는지 명확해진다.
- value_field를 error_rate로 바꾸면 성능 오류 stream chart가 된다.

## 렌더링 규칙

- `visible=false`이면 layout slot은 유지하되 component body는 렌더링하지 않는다.
- 필수 field가 없으면 빈 chart를 그리지 않고 `missing data` 상태를 반환한다.
- threshold, event, annotation류 component와 조합될 수 있도록 좌표 scale을 외부에서 주입받을 수 있어야 한다.
- 색상은 chart별로 직접 고정하지 않고 semantic token을 사용한다. 예: `reference`, `current`, `warning`, `drift`, `highlight`.

## 적용 Chart

- `CHART-ADAPT-001`
- `CHART-CTRL-001`
- `CHART-CTRL-002`
- `CHART-GEN-001`
- `CHART-STREAM-003`
- `CHART-STREAM-004`
- `CHART-STREAM-005`
