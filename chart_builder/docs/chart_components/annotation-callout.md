# Annotation Callout

Component key: `annotation_callout`

## 목적

차트의 특정 구간, 방향, 판단 근거를 짧은 문장이나 화살표/라벨로 강조한다.

## 주요 기능

- one-sided 방향, not counted 영역, exact check 필요 구간 표시
- 사용자가 해석해야 할 지점을 직접 지정
- 주요 오해를 줄이기 위한 보조 설명 제공

## 입력 데이터 계약

이 component는 renderer가 직접 DB row를 읽기보다, chart render layer가 만든 `chart_input_json` 일부를 받는 것을 전제로 한다.

```json
{
  "component": "annotation_callout",
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
| `anchor` | 라벨이 붙을 데이터 좌표 또는 element id |
| `text` | 표시 문구 |
| `direction` | up, down, left, right 같은 라벨 배치 방향 |
| `severity` | info, warning, critical 스타일 |

## 파라미터 변경 시 화면 변화

- anchor가 바뀌면 강조 위치가 달라진다.
- severity를 warning으로 바꾸면 색상과 시각적 우선순위가 커진다.
- direction을 바꾸면 라벨이 데이터 요소를 가리지 않도록 위치가 조정된다.

## 렌더링 규칙

- `visible=false`이면 layout slot은 유지하되 component body는 렌더링하지 않는다.
- 필수 field가 없으면 빈 chart를 그리지 않고 `missing data` 상태를 반환한다.
- threshold, event, annotation류 component와 조합될 수 있도록 좌표 scale을 외부에서 주입받을 수 있어야 한다.
- 색상은 chart별로 직접 고정하지 않고 semantic token을 사용한다. 예: `reference`, `current`, `warning`, `drift`, `highlight`.

## 적용 Chart

- `CHART-ANNOT-001`
- `CHART-CLS-001`
- `CHART-ERR-005`
- `CHART-STREAM-005`
