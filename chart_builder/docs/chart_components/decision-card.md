# Decision Card

Component key: `decision_card`

## 목적

검정 또는 detector의 최종 판단을 카드 형태로 압축해 보여준다.

## 주요 기능

- accept/reject, normal/warning/drift 같은 상태 표시
- 판단 근거 metric과 threshold를 함께 표시
- 보고서 문장으로 연결하기 쉬운 요약 제공

## 입력 데이터 계약

이 component는 renderer가 직접 DB row를 읽기보다, chart render layer가 만든 `chart_input_json` 일부를 받는 것을 전제로 한다.

```json
{
  "component": "decision_card",
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
| `decision_field` | 판정 상태 field |
| `primary_metric` | 판정 근거 값 |
| `threshold_field` | 기준값 |
| `status_palette` | 상태별 색상 매핑 |

## 파라미터 변경 시 화면 변화

- decision_field가 drift면 카드 색상과 강조 문구가 alarm 상태로 바뀐다.
- primary_metric을 p-value로 바꾸면 유의성 중심 카드가 된다.
- status_palette를 조정하면 운영 조직의 위험 등급 색상 체계에 맞출 수 있다.

## 렌더링 규칙

- `visible=false`이면 layout slot은 유지하되 component body는 렌더링하지 않는다.
- 필수 field가 없으면 빈 chart를 그리지 않고 `missing data` 상태를 반환한다.
- threshold, event, annotation류 component와 조합될 수 있도록 좌표 scale을 외부에서 주입받을 수 있어야 한다.
- 색상은 chart별로 직접 고정하지 않고 semantic token을 사용한다. 예: `reference`, `current`, `warning`, `drift`, `highlight`.

## 적용 Chart

- `CHART-STREAM-004`
- `CHART-STREAM-005`
