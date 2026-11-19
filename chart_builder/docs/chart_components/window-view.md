# Window View

Component key: `window_view`

## 목적

reference window, current window, sliding window 같은 분석 구간을 명시한다.

## 주요 기능

- window index 또는 기간 표시
- baseline/current 구간 경계 표현
- stream detector의 window adaptation 설명

## 입력 데이터 계약

이 component는 renderer가 직접 DB row를 읽기보다, chart render layer가 만든 `chart_input_json` 일부를 받는 것을 전제로 한다.

```json
{
  "component": "window_view",
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
| `window_id_field` | window 식별자 |
| `start_field` | 구간 시작 |
| `end_field` | 구간 종료 |
| `window_role_field` | reference, current, warning 등 역할 |
| `show_boundaries` | 경계선 표시 여부 |

## 파라미터 변경 시 화면 변화

- show_boundaries=true이면 구간 전환 시점이 뚜렷해진다.
- window_role_field를 쓰면 reference/current를 색상으로 구분한다.
- start/end 대신 window_id만 쓰면 compact한 window sequence view가 된다.

## 렌더링 규칙

- `visible=false`이면 layout slot은 유지하되 component body는 렌더링하지 않는다.
- 필수 field가 없으면 빈 chart를 그리지 않고 `missing data` 상태를 반환한다.
- threshold, event, annotation류 component와 조합될 수 있도록 좌표 scale을 외부에서 주입받을 수 있어야 한다.
- 색상은 chart별로 직접 고정하지 않고 semantic token을 사용한다. 예: `reference`, `current`, `warning`, `drift`, `highlight`.

## 적용 Chart

- `CHART-CAT-003`
- `CHART-DIST-001`
- `CHART-ERR-002`
- `CHART-MV-001`
- `CHART-MV-002`
- `CHART-MV-003`
- `CHART-MV-004`
- `CHART-MV-005`
- `CHART-PROB-001`
- `CHART-PROB-003`
- `CHART-PSI-001`
- `CHART-STREAM-001`
- `CHART-STREAM-002`
