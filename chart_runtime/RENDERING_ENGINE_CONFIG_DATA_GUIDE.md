# Rendering Engine, Config, Data Binding Guide

작성일: 2026-06-24

이 문서는 현재 chart builder의 생성 차트가 어떤 흐름으로 렌더링되는지, `config`와 `data`가 렌더링 엔진에 어떻게 연결되는지 정리한다. 변경 이력은 `RENDERING_ENGINE_NOTES.md`에 계속 누적하고, 이 문서는 구조와 사용 규칙을 설명하는 기준 문서로 유지한다.

## 1. 전체 흐름

현재 생성 차트는 다음 흐름으로 만들어진다.

```text
chart_builder/builder_charts.json
  layout + components + data + config
        |
        v
chart_builder/tools/generate_recreated_site.py
        |
        v
chart_builder/web/recreated_chart_payloads.js
chart_builder/web/chart_*.html
        |
        v
chart_runtime/chart_runtime.js
        |
        v
generated chart DOM/SVG
```

중앙 viewer는 다음 파일을 사용한다.

```text
chart_builder/web/recreated_charts.html
chart_builder/web/recreated_charts.js
chart_runtime/chart_runtime.css
chart_builder/web/recreated_chart_payloads.js
chart_runtime/chart_runtime.js
```

개별 generated chart 페이지도 같은 runtime/CSS를 사용한다.

```text
chart_builder/web/chart_anom_001_generated.html
  -> chart_runtime/chart_runtime.js
  -> chart_runtime/chart_runtime.css
  -> web/generated_chart_page.css
```

따라서 공통 렌더링 동작을 바꾸려면 보통 `chart_runtime/chart_runtime.js`와 `chart_runtime/chart_runtime.css`를 수정한다. 특정 chart의 위치, 축, tick, 문구, 데이터 범위는 가능하면 `chart_builder/builder_charts.json`의 payload에서 조정한다.

중요한 재사용 원칙:

```text
이미 만들어진 chart payload를 다른 화면에서 재사용할 때는 layout/components/config/text를 유지하고 data를 교체한다.
고객사, feature, 이벤트 시점에 따라 config 값이 달라져야 하면 저장된 payload를 수정하지 않고 runtime config override로 분리한다.
새 데이터가 들어왔을 때 축이나 marker가 맞지 않으면 서버에서 payload 정의를 덮어쓰지 말고 runtime override, component renderer, saved chart contract 중 어디의 책임인지 분리해서 고친다.
```

예를 들어 `drift_metric_timeseries`의 이벤트 분석 팝업은 재생성 차트를 새로 조립하는 기능이 아니다. 기존 payload에 이벤트 시점의 분석 data만 주입해 렌더링해야 한다. 상세 기준은 [../drift_metric_timeseries/docs/analysis_chart_integration.md](../drift_metric_timeseries/docs/analysis_chart_integration.md)를 따른다.

## 2. Payload 구조

하나의 chart payload는 크게 네 부분이다.

```json
{
  "chartId": "CHART-ANOM-001",
  "title": "...",
  "originalPath": "./drift_report_charts/chart_anom_001.html",
  "layout": {},
  "components": [],
  "data": {}
}
```

역할:

| field | 역할 |
|---|---|
| `chartId` | 차트 식별자 |
| `title` | viewer와 generated page 제목 |
| `originalPath` | 원본 chart popup iframe 경로 |
| `layout` | 화면 영역과 grid 배치 |
| `components` | 각 영역에 놓일 component instance 목록 |
| `data` | component가 참조할 row 배열 사전 |

렌더링 엔진은 `layout.areas`를 순회하면서 area DOM을 만들고, 해당 area에 매핑된 `components`를 렌더링한다.

## 3. Layout Area

`layout.areas`는 chart의 의미 구역이다.

```json
{
  "area": "side_bottom",
  "role": "secondary_visual",
  "x": 7,
  "y": 2,
  "w": 5,
  "h": 1,
  "title": "차원축소 투영",
  "description": "빨간 outlier가...",
  "headerHeight": 65,
  "stageInset": {
    "top": 64,
    "right": 16,
    "bottom": -18,
    "left": 16
  }
}
```

중요 필드:

| field | 설명 |
|---|---|
| `area` | component의 `area`와 연결되는 key |
| `role` | `summary`, `primary_visual`, `secondary_visual`, `notes` 등 의미 역할 |
| `x`, `y`, `w`, `h` | 12-column grid 안의 위치와 크기 |
| `title` | area header 제목 |
| `description` | Note popup 내용 |
| `headerHeight` | header가 차지하는 높이 |
| `stageInset` | chart drawing stage의 top/right/bottom/left inset |
| `className` | area에 추가할 CSS class |

`stageInset`은 실제 그래프가 그려지는 `.component-stage`의 위치를 정한다. 축 label이 아래에서 잘리거나 header와 겹치면 먼저 이 값을 조정한다.

주의:

```text
description은 generated chart에서 inline 본문으로 표시하지 않고 Note popup으로 표시한다.
숫자 요약 영역(role: summary)에는 확대 버튼을 표시하지 않는다.
```

## 4. Component Instance

component instance는 어떤 renderer를 쓸지, 어떤 data source를 읽을지, 어떤 config로 그릴지를 정의한다.

```json
{
  "componentInstanceId": "CHART-ANOM-001.projection.0",
  "componentType": "projection_scatter",
  "area": "side_bottom",
  "isOverlay": false,
  "zIndex": 10,
  "config": {},
  "dataBinding": {
    "source": "chart.CHART-ANOM-001.projection",
    "x_field": "x",
    "y_field": "y",
    "group_field": "group"
  }
}
```

중요 필드:

| field | 설명 |
|---|---|
| `componentInstanceId` | instance 식별자. overlay가 base component를 참조할 때도 사용한다. |
| `componentType` | runtime renderer 선택 key |
| `area` | 렌더링될 layout area |
| `isOverlay` | true이면 base component 위에 겹쳐 그린다 |
| `zIndex` | logical ordering 용도 |
| `config` | renderer 옵션 |
| `dataBinding` | `payload.data`의 source와 field mapping |

`chart_runtime.js`의 `renderComponent()`는 `componentType`을 보고 renderer를 선택한다.

```text
trend_line, performance_metric_view, control_chart -> renderLine
bar_chart, ranking_view, contribution_view -> renderBar
projection_scatter -> renderScatter
matrix_view, heatmap -> renderMatrix
distribution_view, histogram_view -> renderDistribution
state_timeline, window_view -> renderTimeline
decision_card -> renderCard
```

## 5. Data Binding

`dataBinding.source`는 `payload.data`의 key를 가리킨다.

```json
"dataBinding": {
  "source": "chart.CHART-ANOM-001.projection"
}
```

연결되는 data:

```json
"data": {
  "chart.CHART-ANOM-001.projection": [
    { "x": -1.2, "y": 0.3, "group": "baseline" },
    { "x": 1.6, "y": 0.5, "group": "current" },
    { "x": 2.6, "y": 1.2, "group": "outlier" }
  ]
}
```

runtime의 기본 조회 함수:

```text
dataFor(payload, instance)
  -> payload.data[instance.dataBinding.source]
```

field 이름은 renderer가 `config`와 `dataBinding`을 같이 본다. 현재 대부분의 renderer는 `config` 우선, 없으면 기본 field명을 사용한다.

예:

```text
projection_scatter
  x_field: config.x_field || "x"
  y_field: config.y_field || "y"
  group_field: config.group_field || "group"

line 계열
  x_field: config.time_field || config.x_field || "time"
  y_field: config.value_field || config.y_field || config.statistic_field || "value"

bar 계열
  category_field: config.category_field || "category"
  value_field: config.value_field || "value"
```

권장:

```text
field mapping은 config와 dataBinding에 모두 넣어도 된다.
renderer가 실제로 읽는 값은 대부분 config이므로 config 누락을 피한다.
dataBinding은 schema 설명과 future builder/editor 연결을 위해 유지한다.
```

## 6. Config의 역할

`config`는 renderer의 시각 규칙을 data와 분리해 저장하는 영역이다.

대표 config:

```json
{
  "view_box": [472, 185],
  "margin": { "top": 12, "right": 24, "bottom": 42, "left": 44 },
  "x_min": -2.4,
  "x_max": 3,
  "y_min": -1.8,
  "y_max": 1.8,
  "x_ticks": [-2.4, 0.3, 3],
  "y_ticks": [-1, 0, 1],
  "x_axis_label": "projection-1",
  "x_tick_dy": 6,
  "axis_label_y": 164,
  "group_class_map": {
    "baseline": "base-dot",
    "current": "current-dot",
    "outlier": "outlier-dot"
  }
}
```

주요 범주:

| 범주 | 예 |
|---|---|
| geometry | `view_box`, `margin`, `stageInset` |
| domain | `x_min`, `x_max`, `y_min`, `y_max` |
| axis/tick | `x_ticks`, `y_ticks`, `x_tick_dy`, `axis_label_y`, `y_tick_format` |
| field mapping | `x_field`, `value_field`, `series_fields` |
| style class | `line_class`, `bar_class`, `group_class_map` |
| marker/annotation | `vertical_markers`, `horizontal_markers`, `annotations` |
| responsive behavior | `min_slot_width`, `min_group_width`, `row_height` |

원칙:

```text
chart-specific tick, marker, annotation 문구는 config에 둔다.
chart_runtime.js에 특정 chartId로 분기하지 않는다.
여러 차트에 필요한 기능만 renderer 옵션으로 일반화한다.
```

## 7. Overlay 연결

overlay component는 같은 area의 base component 위에 그려진다.

예:

```json
{
  "componentType": "event_marker",
  "area": "main",
  "isOverlay": true,
  "config": {
    "value_source_component_id": "CHART-ADAPT-001.accuracy.0",
    "highlight_event_type": "replacement"
  },
  "dataBinding": {
    "source": "chart.CHART-ADAPT-001.events"
  }
}
```

동작:

```text
base component는 .component-stage에 렌더링된다.
overlay component는 .component-overlay에 렌더링된다.
overlay가 y 좌표를 맞춰야 하면 value_source_component_id로 base component의 domain/field를 참조한다.
```

확대 팝업에서도 base component와 overlay는 같은 area 안에 같이 유지된다.

## 8. Sizing과 Overflow

현재 엔진은 작은 패널에서 내용을 무조건 잘라내지 않는다.

정책:

```text
component-stage는 overflow:auto다.
SVG가 viewBox보다 커지거나 데이터가 많으면 SVG 자체 크기를 키운다.
넓거나 높은 SVG는 panel 안에서 scroll로 접근한다.
```

관련 코드:

```text
svg()
  viewBox 폭/높이를 CSS 변수 --chart-svg-w, --chart-svg-h로 기록한다.

normalizeSvgSizing()
  DOM에 붙은 뒤 SVG geometry를 검사한다.
  도형/text가 viewBox 밖으로 나가면 viewBox와 표시 크기를 확장한다.
```

data가 많을 때의 renderer별 대응:

| renderer | 대응 |
|---|---|
| `vertical_grouped` | `rows.length * min_slot_width` 기준으로 SVG 폭 확장 |
| `violin_summary` | `validRows.length * min_group_width` 기준으로 SVG 폭 확장 |
| `mosaic_2x2` | 최소 row height 보장, 필요 시 SVG 높이 확장 |
| horizontal bar 계열 | 큰 내용은 stage scroll로 접근 |

## 9. 확대 팝업

각 visual area에는 `확대` 버튼이 생긴다. 단, 숫자 summary 영역은 제외한다.

확대 제외:

```text
area.role === "summary"
decision_card만 있는 숫자 요약 영역
```

동작:

```text
사용자가 확대 버튼 클릭
  -> showComponentZoomPopup(payload, areaName)
  -> buildZoomPayload(payload, areaName)
  -> 선택 area만 1x1 layout으로 재구성
  -> ChartRuntime.renderChartPayload()로 popup 안에 다시 렌더링
```

장점:

```text
작은 side panel의 축/라벨/marker를 크게 확인할 수 있다.
overlay까지 함께 보인다.
popup에서도 scroll 정책이 유지된다.
```

## 10. Generator와 Viewer

`chart_builder/tools/generate_recreated_site.py`는 `chart_builder/builder_charts.json`을 읽어 viewer용 JS payload와 개별 generated HTML을 만든다.

실행:

```powershell
python chart_builder\tools\generate_recreated_site.py
```

출력:

```text
chart_builder/web/recreated_chart_payloads.js
chart_builder/web/chart_*_generated.html
```

viewer:

```text
chart_builder/web/recreated_charts.html
  left: chart list
  center: generated component chart
  button: original popup
  area button: component zoom popup
```

local URL:

```text
http://127.0.0.1:8050/recreated_charts.html
```

## 11. Visual Smoke Test

시각 스모크 테스트는 component별로 data/config 변형을 만들어 실제 브라우저에서 캡처한다.

실행:

```powershell
python chart_runtime\tests\component_visual_smoke.py
```

검사:

```text
렌더링 예외
console error
NaN / undefined / Infinity
빈 캡처
SVG geometry 이상
scroll 불가 overflow
```

변형:

| variant | 목적 |
|---|---|
| `source` | 실제 payload 그대로 |
| `shifted-data` | 숫자 값 변화 반응 |
| `sparse-data` | 적은 row와 보정된 marker/tick |
| `dense-data` | 많은 row와 overflow/scroll 반응 |
| `compact-config` | 작은 viewBox/margin 반응 |

결과:

```text
chart_runtime/test_results/component_visual_smoke/component_visual_smoke_report.html
chart_runtime/test_results/component_visual_smoke/component_visual_smoke_report.json
chart_runtime/test_results/component_visual_smoke/captures/
```

자동 통과만으로 끝내지 않고, report HTML의 dense-data와 compact-config 캡처는 사람이 훑어본다.

## 12. 수정 판단 기준

문제가 보이면 다음 순서로 판단한다.

1. data가 잘못됐는가?
   - field 누락, numeric field 문자열, 빈 source, source key 오류
2. data와 config가 같이 바뀌어야 하는가?
   - sparse-data에서 marker/tick이 원래 domain을 가리키는 경우
3. config로 해결 가능한가?
   - margin, tick, axis label, annotation 위치, class 조정
4. renderer 일반화가 필요한가?
   - 여러 차트에서 반복되는 overflow, sizing, NaN 방어
5. CSS 정책 문제인가?
   - scroll, popup, panel sizing, text scale

금지:

```text
chart_runtime.js에서 특정 chartId로 분기
renderer에 원본 chart 문구 하드코딩
renderer에 특정 데이터 배열 하드코딩
generated HTML을 직접 손으로 수정해서 source payload와 불일치시키기
```

허용:

```text
builder_charts.json config/data 수정
renderer option 추가
공통 CSS 정책 추가
visual smoke test 강화
문서 업데이트
```

## 13. 최근 사례: CHART-ANOM-001 Projection Scatter

문제:

```text
CHART-ANOM-001의 "차원축소 투영"에서 x축 tick 숫자와 x축 label이 겹쳤다.
왼쪽 아래에서는 y축 최소 tick과 x축 최소 tick도 가까웠다.
```

해결:

```text
projection_scatter renderer에 x_tick_dy config를 추가했다.
CHART-ANOM-001 projection config에서 margin.bottom, x_tick_dy, axis_label_y를 조정했다.
y_ticks를 [-1, 0, 1]로 명시해 모서리 tick 혼잡도를 낮췄다.
side_bottom stageInset.bottom을 음수로 조정해 작은 panel에서도 x축 label이 보이게 했다.
```

검증:

```text
tick과 projection-1 label bbox 분리 확인
NaN/undefined 없음
component_visual_smoke: cases=210 pass=210 fail=0
```

## 14. 필수 검증 명령

렌더링 엔진, config, data를 바꾼 뒤 최소한 다음을 실행한다.

```powershell
python -c "import json; json.load(open('chart_builder/builder_charts.json', encoding='utf-8')); print('json ok')"
python chart_builder\tools\generate_recreated_site.py
node --check chart_runtime\chart_runtime.js
node --check chart_builder\web\recreated_charts.js
python -m py_compile chart_runtime\tests\component_visual_smoke.py
python chart_runtime\tests\component_visual_smoke.py
```

필요하면 Playwright로 특정 chart를 직접 캡처한다.

```text
chart_runtime/test_results/<test_name>/captures/<chart_id>_<area>_*.png
```

