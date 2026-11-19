# Event Marker

Component key: `event_marker`

## 목적

alarm, warning, drift, retrain, replacement 같은 사건 시점을 차트 위에 표시한다.

## 주요 기능

- 수직선, 점, 아이콘, label로 이벤트 위치 표시
- 여러 event type 색상 구분
- metric 변화와 사건의 시간 관계 설명

## 입력 데이터 계약

이 component는 renderer가 직접 DB row를 읽기보다, chart render layer가 만든 `chart_input_json` 일부를 받는 것을 전제로 한다.

```json
{
  "component": "event_marker",
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
| `event_field` | event list 또는 event index |
| `event_type_field` | alarm, warning, retrain 등 유형 |
| `marker_style` | line, point, flag, band |
| `label_mode` | none, short, full |

## 파라미터 변경 시 화면 변화

- marker_style=line이면 시계열 전체와 사건 위치를 맞춰 보기 쉽다.
- label_mode=full이면 설명력은 높지만 화면이 복잡해진다.
- event_type_field를 쓰면 alarm과 retrain을 다른 색으로 구분한다.

## 렌더링 규칙

- `visible=false`이면 layout slot은 유지하되 component body는 렌더링하지 않는다.
- 필수 field가 없으면 빈 chart를 그리지 않고 `missing data` 상태를 반환한다.
- threshold, event, annotation류 component와 조합될 수 있도록 좌표 scale을 외부에서 주입받을 수 있어야 한다.
- 색상은 chart별로 직접 고정하지 않고 semantic token을 사용한다. 예: `reference`, `current`, `warning`, `drift`, `highlight`.

## 적용 Chart

- `CHART-ADAPT-001`
- `CHART-ADAPT-002`
- `CHART-ANNOT-001`
- `CHART-ANNOT-002`
- `CHART-ANOM-001`
- `CHART-BOCD-001`
- `CHART-CAT-001`
- `CHART-CAT-004`
- `CHART-CTRL-001`
- `CHART-CTRL-002`
- `CHART-CTRL-003`
- `CHART-EDF-003`
- `CHART-EDF-004`
- `CHART-ERR-001`
- `CHART-ERR-002`
- `CHART-ERR-003`
- `CHART-ERR-004`
- `CHART-ERR-005`
- `CHART-ERR-006`
- `CHART-EXPL-001`
- `CHART-GEN-001`
- `CHART-PROB-001`
- `CHART-PROB-002`
- `CHART-PROB-003`
- `CHART-REP-001`
- `CHART-REP-002`
- `CHART-REP-003`
- `CHART-STREAM-001`
- `CHART-STREAM-002`
- `CHART-STREAM-003`
- `CHART-STREAM-004`
- `CHART-STREAM-005`
- `CHART-TEXT-002`
- `CHART-UNC-001`
