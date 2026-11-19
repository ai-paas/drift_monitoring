# Detector Statistic View

Component key: `detector_statistic_view`

## 목적

각 detector가 산출한 핵심 statistic, score, distance, evidence 값을 시계열이나 단일 panel로 보여준다.

## 주요 기능

- statistic 증가/감소 추세 확인
- threshold 또는 decision bound와 비교
- alarm 발생 전후의 evidence 축적 확인

## 입력 데이터 계약

이 component는 renderer가 직접 DB row를 읽기보다, chart render layer가 만든 `chart_input_json` 일부를 받는 것을 전제로 한다.

```json
{
  "component": "detector_statistic_view",
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
| `statistic_field` | score, distance, p-value, LLR 등 표시 대상 |
| `time_field` | window 또는 time index |
| `scale` | linear, log, normalized |
| `decision_direction` | higher_is_drift 또는 lower_is_drift |

## 파라미터 변경 시 화면 변화

- statistic_field를 바꾸면 같은 panel이 MMD score, PSI, PH statistic 등으로 재사용된다.
- scale=log이면 큰 값의 spike보다 작은 변화 구간을 더 잘 볼 수 있다.
- decision_direction이 lower_is_drift이면 threshold 해석 방향과 색상 규칙이 반대로 적용된다.

## 렌더링 규칙

- `visible=false`이면 layout slot은 유지하되 component body는 렌더링하지 않는다.
- 필수 field가 없으면 빈 chart를 그리지 않고 `missing data` 상태를 반환한다.
- threshold, event, annotation류 component와 조합될 수 있도록 좌표 scale을 외부에서 주입받을 수 있어야 한다.
- 색상은 chart별로 직접 고정하지 않고 semantic token을 사용한다. 예: `reference`, `current`, `warning`, `drift`, `highlight`.

## 적용 Chart

- `CHART-ANNOT-001`
- `CHART-ANNOT-002`
- `CHART-ANOM-001`
- `CHART-CAT-002`
- `CHART-CAT-003`
- `CHART-CTRL-001`
- `CHART-CTRL-002`
- `CHART-CTRL-003`
- `CHART-DIST-001`
- `CHART-DISTSHAPE-001`
- `CHART-ERR-003`
- `CHART-ERR-004`
- `CHART-EXPL-001`
- `CHART-GEN-001`
- `CHART-MV-001`
- `CHART-MV-002`
- `CHART-MV-003`
- `CHART-MV-004`
- `CHART-MV-005`
- `CHART-PROB-002`
- `CHART-PROB-003`
- `CHART-PSI-001`
- `CHART-REP-001`
- `CHART-REP-003`
- `CHART-STREAM-002`
- `CHART-STREAM-003`
- `CHART-STREAM-004`
- `CHART-TEXT-001`
- `CHART-TEXT-002`
