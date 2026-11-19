# Chart Container and Component Implementation Guide

작성일: 2026-06-17

## 1. 목적

이 문서는 53개 drift chart를 개별 HTML 파일이 아니라 공통 chart component와 semantic container 조립 방식으로 구현하기 위한 기준을 정의한다.

현재 차트 문서와 구현은 완전한 바둑판 grid가 아니다. 대부분 다음과 같은 의미 구역으로 구성되어 있다.

```text
header / summary
main large panel
side top panel
side bottom panel
notes / legend
```

따라서 구현 기준은 "모든 cell이 동일한 완전 grid"가 아니라, **semantic area를 grid 좌표로 저장하고 responsive renderer가 그 영역 안에 component를 맞춰 그리는 방식**이다.

## 2. 핵심 원칙

1. Chart는 container와 component instance의 조합이다.
2. 사용자는 `main`, `side_top`, `summary` 같은 의미 구역을 편집한다.
3. 시스템은 의미 구역을 내부적으로 `x`, `y`, `w`, `h` grid 좌표로 저장한다.
4. Component는 고정 px 크기를 갖지 않는다.
5. Component는 container가 제공하는 실제 `width`, `height`를 기준으로 다시 렌더링한다.
6. 작은 영역에서는 글씨가 그대로 남아 겹치지 않아야 한다.
7. 영역이 너무 작으면 component별 overflow policy에 따라 compact, hide label, scroll을 적용한다.
8. Chart별 특수 구현은 `domain_specific_visual`로 남기되, 가능한 경우 공통 component로 승격한다.

## 3. 전체 구조

```text
ChartPage
  ChartToolbar
  ChartContainer
    SemanticGridLayout
      ChartArea: summary
        ComponentRenderer: summary_metric_panel
      ChartArea: main
        ComponentRenderer: trend_line
        ComponentRenderer: threshold_line overlay
        ComponentRenderer: event_marker overlay
      ChartArea: side_top
        ComponentRenderer: bar_chart
      ChartArea: side_bottom
        ComponentRenderer: state_timeline
      ChartArea: notes
        ComponentRenderer: interpretation_text
```

보기 화면과 편집 화면은 같은 저장 schema를 사용하지만 UI는 다르게 구성한다.

Chart Builder의 build 결과는 코드 파일이 아니라 DB에 저장된 runtime render payload다.

```text
DB layout/config/data binding
  -> FastAPI runtime render payload API
  -> React Chart Renderer
  -> component registry에서 renderer 선택
  -> 화면에 chart 출력
```

초기 구현에서는 `chart_xxx.tsx` 같은 code generation을 하지 않는다.

```text
View mode
  - CSS Grid 기반 renderer
  - drag/resize 없음
  - responsive fitting 우선

Edit mode
  - react-grid-layout 또는 동등한 grid editor 사용
  - area 이동/크기 조절
  - component 배치/삭제/순서 변경
  - chart별 override 저장
```

## 4. Semantic Area 모델

현재 차트 문서에서 자주 나오는 구역은 다음과 같다.

| area_code | 역할 | 설명 |
|---|---|---|
| `summary` | summary | 상단 핵심 metric, 상태, decision 요약 |
| `main` | primary_visual | 가장 큰 주 chart 영역 |
| `side_top` | secondary_visual | 보조 chart 상단 |
| `side_bottom` | secondary_visual | 보조 chart 하단 |
| `notes` | interpretation | 해석 문장, 금지 해석, 추가 확인 항목 |
| `legend` | legend | 색상/series 설명 |
| `footer` | metadata | chart source, method, version 등 |

이 area는 사용자에게 보이는 편집 단위다.

저장은 다음처럼 grid 좌표로 한다.

```json
{
  "layoutType": "semantic_grid",
  "columns": 12,
  "rows": 8,
  "gap": 12,
  "areas": [
    { "area": "summary", "role": "summary", "x": 0, "y": 0, "w": 12, "h": 1 },
    { "area": "main", "role": "primary_visual", "x": 0, "y": 1, "w": 8, "h": 5 },
    { "area": "side_top", "role": "secondary_visual", "x": 8, "y": 1, "w": 4, "h": 2 },
    { "area": "side_bottom", "role": "secondary_visual", "x": 8, "y": 3, "w": 4, "h": 3 },
    { "area": "notes", "role": "interpretation", "x": 0, "y": 6, "w": 12, "h": 2 }
  ]
}
```

## 5. Layout Preset

처음부터 모든 chart를 자유 배치로 만들지 않는다. 현재 chart의 관례적인 구성을 preset으로 둔다.

| preset_code | 용도 |
|---|---|
| `default_3_panel` | main + side_top + side_bottom + summary + notes |
| `single_main_with_summary` | 큰 chart 하나와 상단 요약 |
| `two_vertical_panels` | 위/아래 두 chart 비교 |
| `three_equal_panels` | 세 보조 chart를 동일 비중으로 표시 |
| `timeline_top_detail_bottom` | timeline과 detail chart 조합 |
| `main_with_legend_notes` | main chart + legend + notes |
| `dashboard_2x2` | 네 개 panel을 균등 배치 |

Chart는 preset을 기본으로 사용하고, 수정이 필요하면 chart별 override를 저장한다.

```text
chart_layout_preset
  -> chart_layout_area
  -> chart_layout_override optional
```

## 6. Component Instance 모델

Component type은 `chart_components/*.md`에서 정의한 component key를 사용한다.

예:

```json
{
  "componentInstanceId": "CHART-CTRL-002.main.ewma",
  "componentType": "trend_line",
  "area": "main",
  "zIndex": 10,
  "isOverlay": false,
  "config": {
    "x_field": "time_index",
    "y_field": "ewma_value",
    "series_field": null,
    "show_points": false
  },
  "dataBinding": {
    "source": "algorithm_result",
    "time_index": "result.value_json.time",
    "ewma_value": "result.value_json.ewma"
  }
}
```

Overlay component는 같은 area 안에서 좌표계를 공유한다.

```json
{
  "componentType": "threshold_line",
  "area": "main",
  "isOverlay": true,
  "zIndex": 20,
  "config": {
    "threshold_value": 2.8,
    "threshold_type": "upper",
    "line_style": "dashed",
    "label": "UCL"
  }
}
```

## 7. Responsive Rendering Contract

모든 chart component는 같은 props 계약을 따른다.

```ts
type ChartComponentProps = {
  width: number;
  height: number;
  data: unknown[];
  config: Record<string, unknown>;
  theme: ChartTheme;
  scaleContext?: ScaleContext;
  interaction?: InteractionContext;
};
```

Renderer는 다음 규칙을 지켜야 한다.

```text
1. width/height가 바뀌면 다시 계산한다.
2. 고정 SVG width/height를 내부 상수로 사용하지 않는다.
3. SVG는 viewBox와 실제 container size를 함께 사용한다.
4. margin, tick count, font size는 width/height에 따라 계산한다.
5. label이 겹치면 rotate, ellipsis, hide, tooltip 중 하나를 적용한다.
6. 너무 작으면 compact mode로 전환한다.
```

## 8. Responsive Frame

모든 component는 `ResponsiveFrame` 안에서 렌더링한다.

```text
ResponsiveFrame
  - ResizeObserver로 실제 영역 크기 측정
  - width/height를 component에 전달
  - min readable size 확인
  - overflow policy 적용
```

권장 상태:

| mode | 조건 | 동작 |
|---|---|---|
| `normal` | 충분한 width/height | 전체 axis, label, legend 표시 |
| `compact` | 공간 부족 | tick 수 감소, 보조 label 숨김 |
| `summary_only` | 매우 작음 | 핵심 값과 상태만 표시 |
| `scroll` | 내용 유지 필요 | 내부 가로/세로 scroll 허용 |
| `missing_data` | 필수 field 없음 | 빈 chart 대신 상태 메시지 표시 |

예:

```ts
function getRenderMode(width: number, height: number) {
  if (width < 180 || height < 120) return "summary_only";
  if (width < 320 || height < 220) return "compact";
  return "normal";
}
```

### 8.1 Prototype에서 확인된 필수 수정사항

`builder_prototype.html` 구현 중 다음 문제가 확인되었고, 이후 프로토타입과 본 구현에서도 같은 규칙을 지켜야 한다.

#### Component가 container 높이를 제대로 받지 못해 세로가 잘리는 문제

문제:

```text
single component를 감싸는 wrapper가 명확한 height를 갖지 않으면
component 내부 SVG stage가 실제 area 높이보다 작게 계산된다.
그 결과 chart가 container에 꽉 차지 않거나 세로가 잘려 보인다.
```

해결 규칙:

```text
area body는 명확한 height context를 가져야 한다.
component wrapper는 width: 100%, height: 100%를 가져야 한다.
single component도 stack container 안에서 렌더링해 높이 계산 경로를 통일한다.
component card 내부는 absolute inset이 아니라 grid row 구조를 우선한다.
title row와 chart stage row를 분리한다.
chart stage는 minmax(0, 1fr) 영역을 사용한다.
```

권장 CSS 구조:

```css
.area-body {
  min-width: 0;
  min-height: 0;
  overflow: hidden;
}

.component-stack {
  display: grid;
  grid-auto-rows: minmax(0, 1fr);
  height: 100%;
  overflow: hidden;
}

.component-card {
  display: grid;
  grid-template-rows: auto minmax(0, 1fr);
  width: 100%;
  height: 100%;
  min-width: 0;
  min-height: 0;
  overflow: hidden;
}

.component-stage {
  min-width: 0;
  min-height: 0;
  overflow: hidden;
}
```

#### 임의 최소 크기로 SVG를 키워 container에 맞지 않는 문제

문제:

```text
renderer에서 width/height를 Math.max(120, measuredWidth)처럼 보정하면
작은 container에서도 chart가 최소 크기로 렌더링되어 잘리거나 scroll처럼 보인다.
```

해결 규칙:

```text
component renderer는 container가 제공한 실제 width/height를 그대로 사용한다.
가독성 보정은 크기 자체를 키우는 방식이 아니라 render mode로 처리한다.
```

권장 방식:

```ts
const width = Math.max(1, Math.floor(rect.width));
const height = Math.max(1, Math.floor(rect.height));
const mode = getRenderMode(width, height);
```

금지 방식:

```ts
const width = Math.max(120, Math.floor(rect.width));
const height = Math.max(90, Math.floor(rect.height));
```

#### 작은 영역에서 글씨가 그대로 남아 겹치는 문제

해결 규칙:

```text
font size는 width/height에 따라 clamp한다.
normal/compact/summary_only 모드를 반드시 둔다.
compact 이하에서는 tick, axis label, point label을 줄이거나 숨긴다.
```

#### summary_only mode에서 핵심 label까지 숨겨지는 문제

Prototype에서 `threshold_line`을 작은 `side_top` 영역에 배치했을 때 `threshold: 0.68` label이 사라지는 문제가 있었다.

원인:

```text
side_top 영역이 작음
-> renderer가 summary_only mode로 전환됨
-> 기존 threshold_line은 summary_only에서 label을 렌더링하지 않음
-> threshold 값이라는 핵심 정보가 사라짐
```

해결 규칙:

```text
summary_only mode는 모든 글자를 숨기는 모드가 아니다.
component의 핵심 의미를 구성하는 primary label/value는 반드시 남긴다.
보조 tick, axis label, legend, point label은 숨길 수 있다.
```

Component별 primary label/value 예:

| component | summary_only에서도 유지해야 하는 정보 |
|---|---|
| `threshold_line` | threshold label과 threshold value |
| `event_marker` | event type 또는 event count |
| `state_timeline` | 최종 state 또는 state counts |
| `bar_chart` | top category와 top value |
| `trend_line` | latest value 또는 start/end delta |
| `detector_statistic_view` | latest statistic과 decision direction |
| `p_value_view` | p-value와 alpha |
| `performance_metric_view` | primary metric value와 방향 |

권장 구현:

```ts
type RenderMode = "normal" | "compact" | "summary_only";

type LabelPriority = "primary" | "secondary" | "decorative";
```

```text
normal
  -> primary + secondary + decorative label 표시

compact
  -> primary + 일부 secondary label 표시

summary_only
  -> primary label/value만 표시
```

금지:

```ts
if (mode !== "summary_only") {
  renderPrimaryValue();
}
```

권장:

```ts
renderPrimaryValue({ compact: mode !== "normal" });

if (mode === "normal") {
  renderAxisLabels();
  renderLegend();
}
```

작은 영역에서 primary label이 잘리지 않도록 다음도 적용한다.

```text
fontSize = clamp(8, min(width, height) * ratio, 12)
label x/y 좌표는 chart area 안으로 clamp한다.
긴 label은 축약명 또는 ellipsis를 사용한다.
```

이 규칙은 모든 component renderer에 적용한다.

#### 최소 판독 가능 크기보다 작은 영역에서 항목이 잘리는 문제

Prototype에서 `bar_chart`를 높이가 낮은 panel에 배치했을 때 마지막 category label인 `device`가 잘리는 문제가 있었다.

원인:

```text
bar_chart는 항목별 최소 row height가 필요함
-> 영역 높이가 row 수 * 최소 row height보다 작음
-> renderer가 SVG height는 작은 영역 높이로 유지함
-> 마지막 row가 SVG viewBox 밖으로 나가거나 overflow hidden으로 잘림
```

해결 규칙:

```text
component는 "축소 가능한 요소"와 "최소 판독 크기가 필요한 요소"를 구분한다.
항목 row, primary label, 주요 value처럼 더 줄이면 읽을 수 없는 요소는 최소 크기를 가진다.
container가 이 최소 크기보다 작으면 chart 자체를 더 축소하지 않고 내부 scroll을 만든다.
```

권장 구현:

```ts
type ReadableSize = {
  minRenderWidth: number;
  minRenderHeight: number;
  overflowX: boolean;
  overflowY: boolean;
};
```

```text
1. ResponsiveFrame이 container의 실제 width/height를 측정한다.
2. component renderer가 데이터 개수와 label 길이를 기준으로 minRenderWidth/minRenderHeight를 계산한다.
3. 실제 영역이 최소 판독 크기보다 작으면 render surface를 최소 판독 크기로 만든다.
4. stage에는 overflow-x/overflow-y: auto를 적용한다.
5. 실제 영역이 충분하면 render surface는 area를 100% 채운다.
```

예: `bar_chart`

```text
min row height = 22px
top/bottom margin = 30px
data rows = 5
minRenderHeight = 5 * 22 + 30 = 140px

area stage height가 96px이면:
  chart를 96px에 억지로 찌그러뜨리지 않음
  render surface height를 140px로 유지
  stage에 세로 scroll 생성
```

가로도 같은 규칙을 적용한다.

```text
긴 category label, 많은 x-axis tick, 많은 heatmap column 등으로
최소 판독 width가 필요한 경우 render surface width를 유지하고 가로 scroll을 만든다.
```

금지:

```text
항목 row height를 8px 이하로 줄여 label을 읽을 수 없게 만드는 것
primary label/value를 숨겨서 chart 의미를 없애는 것
SVG viewBox 밖으로 element가 나가게 둔 뒤 overflow hidden으로 자르는 것
```

이 규칙은 `bar_chart`, `ranking_view`, `heatmap`, `table_view`, 긴 x-axis를 가진 `trend_line`에 우선 적용한다.

## 9. Text Fitting Policy

차트가 줄어들 때 글씨가 예전 크기로 남아 겹치면 안 된다.

공통 정책:

```text
fontSize = clamp(9, min(width, height) * ratio, 14)
axis label은 compact mode에서 숨긴다.
tick label은 최대 개수를 제한한다.
긴 category label은 ellipsis 처리한다.
중요 label은 tooltip 또는 side detail로 보낸다.
```

권장 label policy:

| policy | 설명 |
|---|---|
| `show` | 항상 표시 |
| `ellipsis` | 한 줄 말줄임 |
| `wrap` | 영역 안에서 줄바꿈 |
| `rotate` | x축 label 회전 |
| `hide_when_compact` | compact 이하에서 숨김 |
| `tooltip_only` | 화면에는 점/막대만 표시하고 hover 시 표시 |

## 10. Overflow Policy

각 area와 component는 overflow 정책을 가진다.

```json
{
  "overflowPolicy": "fit_or_scroll",
  "minWidth": 280,
  "minHeight": 180
}
```

정책:

| policy | 동작 |
|---|---|
| `fit` | 영역에 맞춰 모든 것을 축소/생략 |
| `scroll_x` | 가로로 긴 category/series를 scroll |
| `scroll_y` | 항목 수가 많은 ranking/bar를 세로 scroll |
| `fit_or_scroll` | 최소 가독성보다 작으면 scroll 생성 |
| `clip_for_overlay` | overlay는 area 밖으로 나가지 않게 clip |

`bar_chart`, `ranking_view`, `heatmap`은 항목 수가 많아질 수 있으므로 scroll 정책을 허용한다.

`event_marker`, `threshold_line`, `annotation_callout`은 overlay component이므로 기본은 clip이다.

## 11. Layout Editor

수정 가능한 컨테이너는 다음 기능을 제공해야 한다.

```text
area 선택
area 이동
area 크기 조절
area 추가
area 삭제
area role 변경
component instance를 area에 배치
component overlay 여부 변경
component z-index 변경
component config 수정
reset to preset
save as chart override
```

권장 구현:

```text
React + TypeScript
react-grid-layout: edit mode의 drag/resize
CSS Grid: view mode renderer
ResizeObserver: area 크기 측정
SVG React renderer: component drawing
```

편집 UI는 완전한 cell editor처럼 보이기보다 semantic area editor처럼 보여야 한다.

```text
사용자에게 보이는 것:
  main
  side_top
  side_bottom
  summary
  notes

DB에 저장되는 것:
  x, y, w, h
```

## 12. DB 설계 추가안

현재 `chart_definition`, `chart_asset`, `variant_chart`에 더해 다음 테이블을 추가한다.

### 12.1 `chart_component_type`

| 컬럼 | 설명 |
|---|---|
| `component_type_id` | PK |
| `component_code` | `bar_chart`, `trend_line` 등 stable key |
| `display_name` | 표시명 |
| `description` | component 목적 |
| `default_config_json` | 기본 config |
| `parameter_schema_json` | config schema |
| `status` | active/deprecated |

### 12.2 `chart_layout_preset`

| 컬럼 | 설명 |
|---|---|
| `layout_preset_id` | PK |
| `preset_code` | `default_3_panel` 등 |
| `display_name` | 표시명 |
| `columns` | grid column 수 |
| `rows` | grid row 수 |
| `gap_px` | area 간격 |
| `description` | 용도 |

### 12.3 `chart_layout_area`

| 컬럼 | 설명 |
|---|---|
| `layout_area_id` | PK |
| `layout_preset_id` | FK |
| `area_code` | `main`, `side_top` 등 |
| `role` | primary_visual, secondary_visual 등 |
| `x`, `y`, `w`, `h` | grid 좌표 |
| `min_w`, `min_h` | 최소 크기 |
| `overflow_policy` | fit, scroll_x 등 |

### 12.4 `chart_component_instance`

| 컬럼 | 설명 |
|---|---|
| `component_instance_id` | PK |
| `chart_definition_id` | FK |
| `component_code` | component type |
| `area_code` | 배치 area |
| `display_order` | 같은 area 내 순서 |
| `z_index` | overlay 순서 |
| `is_overlay` | overlay 여부 |
| `config_json` | chart별 config |
| `data_binding_json` | algorithm_result 또는 chart_input_json binding |
| `overflow_policy` | instance별 overflow override |

### 12.5 `chart_layout_override`

| 컬럼 | 설명 |
|---|---|
| `chart_definition_id` | FK |
| `layout_json` | chart별 수정 layout |
| `updated_at` | 수정 시각 |
| `updated_by` | 수정자 |

## 13. API 설계

FastAPI 백엔드에 다음 API를 추가한다.

```text
GET  /api/chart-layouts/presets
GET  /api/charts/{chart_id}/layout
PUT  /api/charts/{chart_id}/layout
GET  /api/chart-components/types
GET  /api/charts/{chart_id}/components
PUT  /api/charts/{chart_id}/components
POST /api/charts/{chart_id}/render-preview
```

보기 화면은 다음 payload를 받으면 된다.

```json
{
  "chartId": "CHART-CTRL-002",
  "layout": {
    "columns": 12,
    "rows": 8,
    "areas": []
  },
  "components": [],
  "data": {}
}
```

## 14. 구현 순서

1. DB에 component/layout schema 추가
2. `chart_component_to_chart.csv`와 `chart_components/*.md`를 import
3. 현재 53개 chart의 기본 preset을 매핑
4. `GET /api/charts/{chart_id}/layout` 구현
5. React view renderer 구현
6. `ResponsiveFrame` 구현
7. `bar_chart`, `trend_line`, `threshold_line`, `event_marker`부터 구현
8. semantic area editor 구현
9. chart별 override 저장 구현
10. 기존 iframe chart를 점진적으로 component chart로 대체

## 15. 첫 MVP 범위

처음부터 32개 component를 모두 구현하지 않는다.

우선순위는 재사용 빈도가 높은 component부터다.

```text
event_marker
threshold_line
trend_line
detector_statistic_view
bar_chart
state_timeline
reference_current_comparison
distribution_view
```

이 8개만으로도 상당수 chart의 main structure를 재현할 수 있다.

## 16. 성공 기준

MVP 성공 기준:

```text
1. 하나의 chart가 DB layout + component config로 렌더링된다.
2. area 크기를 바꾸면 component가 width/height에 맞춰 다시 그려진다.
3. label이 겹치거나 고정 크기로 남지 않는다.
4. 너무 작은 area는 compact 또는 scroll mode로 전환된다.
5. layout editor에서 main/side/summary area를 이동/크기 조절할 수 있다.
6. 저장 후 다시 열면 같은 layout이 복원된다.
```
