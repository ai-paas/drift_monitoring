# Source Matching Guide

작성일: 2026-06-23

## 목적

이 문서는 원본 drift report chart를 공통 chart component 조합으로 재생성할 때, 원본과 최대한 비슷하게 보이도록 검토하고 수정하는 절차를 정의한다.

핵심 원칙은 다음과 같다.

```text
layout + component instances + data + config -> generated chart
```

Renderer에 특정 chart ID, 특정 tick 배열, 특정 문구, 특정 marker 위치를 하드코딩하지 않는다. 원본 재현에 필요한 값은 chart payload의 component `config`와 `data`에 저장한다.

## 단일 렌더링 엔진 원칙

drift report chart는 하나의 전용 렌더링 엔진으로 그린다.

```text
builder design payload
  layout + component instances + config + data
        ↓
chart_runtime/chart_runtime.js
        ↓
builder preview / generated site / standalone generated chart
```

역할 분리는 다음과 같다.

```text
chart_runtime/chart_runtime.js
  payload를 해석해 실제 chart DOM/SVG를 그리는 유일한 renderer

web/builder_prototype.js
  component 선택, 배치, 저장, config/data binding 편집 담당
  chart preview는 chart_runtime.js 호출

web/recreated_charts.js
  chart 목록, 검색, Open Original popup, issue 목록 담당
  chart body는 chart_runtime.js 호출

tools/generate_recreated_site.py
  saved design과 원본 metadata를 payload JS로 변환
  renderer JS/CSS를 생성하거나 덮어쓰지 않음
```

따라서 디자인 화면에서 잘 보이는 chart와 generated chart가 다르게 보이면, 먼저 두 화면이 같은 payload와 같은 `chart_runtime.js`를 쓰는지 확인한다. DOM을 복사해서 결과물을 만들지 않는다. 복사 대상은 디자인 화면의 DOM이 아니라 `layout + component instances + config + data` payload다.

## Engine / Config / Data 경계

엔진이 담당하는 것:

```text
layout grid 해석
area header / note popup / stageInset 처리
SVG viewBox, margin, scale, axis, tick 렌더링
line, bar, matrix, distribution, scatter, timeline, table, decision card 같은 reusable component
marker, annotation, background region, point highlight 같은 reusable primitive
null/missing value 처리
component가 영역을 채우는 공통 sizing 정책
```

config가 담당하는 것:

```text
area 위치, 크기, title, description, headerHeight, stageInset
view_box, margin, x/y domain, tick 배열, axis label 유무와 위치
series field, color/stroke class, point 표시 여부와 반지름
marker 위치, annotation 문구와 위치 보정
timeline role 색상 map, label 축약 map
component별 className과 일반 옵션
```

## Generated Chart Note 규칙

Generated chart의 panel 설명문은 반드시 `Note` 링크로 노트화한다.

원본 chart가 panel header에 설명문을 inline으로 직접 표시하더라도, generated chart에서는 긴 텍스트가 chart body를 밀거나 영역 밖으로 넘치는 문제가 생길 수 있으므로 inline 표시를 금지한다.

규칙:

```text
layout area의 description은 panel 본문에 직접 표시하지 않는다.
description은 area header의 Note 링크로만 노출한다.
Note 링크를 누르면 popup으로 description 전체를 보여준다.
generated standalone page에서는 chart 영역 보존이 원본 inline text 재현보다 우선한다.
```

허용되는 payload:

```json
{
  "area": "main",
  "title": "Approximation Error Band",
  "description": "Exact/reference score와 approx score가...",
  "headerHeight": 62,
  "stageInset": { "top": 76, "right": 16, "bottom": 16, "left": 16 }
}
```

금지되는 payload:

```json
{
  "area": "main",
  "descriptionMode": "inline"
}
```

비교 기록에는 다음처럼 남긴다.

```text
원본은 panel 설명문을 inline으로 표시하지만 generated는 overflow 방지를 위해 Note popup으로 노출한다.
이는 의도된 차이이며 chart 영역 보존을 우선한다.
```

data가 담당하는 것:

```text
series row 값
timeline segment start/end/state
summary metric label/value/displayValue
event row, marker row, comparison row
원본 chart에서 추출한 실제 수치와 한글/영문 문구
```

금지되는 경계 침범:

```text
chart_runtime.js에서 chart ID로 분기
chart_runtime.js에 특정 원본 chart 문구 삽입
chart_runtime.js에 특정 chart의 tick/marker/data 배열 삽입
generator가 chart_runtime.js 또는 recreated_charts.js를 문자열 상수로 재생성
builder 전용 DOM을 generated 결과물로 복사
```

## 금지사항

다음은 금지한다.

```text
renderer에서 CHART-ADAPT-001 같은 chart ID로 분기
renderer에 [1, 8, 16, 24, 32] 같은 chart-specific tick 하드코딩
renderer에 "alternate replacement restores accuracy" 같은 chart-specific 문구 하드코딩
renderer에 replacement, alarm, retrain 등 특정 도메인 이벤트만 특별 처리
원본 chart JS/CSS를 그대로 iframe처럼 재사용
데이터 값과 무관한 fixed drawing을 component로 위장
```

허용되는 방식은 다음이다.

```json
{
  "componentType": "performance_metric_view",
  "config": {
    "view_box": [630, 440],
    "margin": { "top": 24, "right": 28, "bottom": 62, "left": 58 },
    "x_ticks": [1, 8, 16, 24, 32],
    "y_ticks": [0.70, 0.78, 0.86, 0.94],
    "x_axis_label": "time index",
    "y_axis_label": "online accuracy"
  }
}
```

## 작업 순서

두 번째 chart부터도 반드시 이 순서로 진행한다.

1. 원본 HTML/CSS/JS를 읽는다.
2. 원본의 layout area를 식별한다.
3. 원본 chart별 데이터 배열과 상수를 추출한다.
4. 원본의 시각 규칙을 표로 정리한다.
5. `builder_charts.json`에 payload를 추가하거나 수정한다.
6. 재현에 필요한 시각 규칙은 component `config`로 옮긴다.
7. renderer는 config를 해석하는 일반 기능만 확장한다.
8. 생성 사이트를 재생성한다.
9. generated chart와 original popup을 비교한다.
10. 차이가 있으면 먼저 config로 해결한다.
11. config로 표현할 수 없는 반복 가능한 개념만 renderer 기능으로 승격한다.
12. 새 이슈나 판단 기준은 이 문서에 추가한다.

## 회귀 점검 규칙

chart layout이나 chart component renderer를 수정하면, 이미 맞춰 둔 chart도 처음부터 다시 점검한다.

특히 다음 변경은 회귀 점검을 반드시 유발한다.

```text
layout area 위치/크기/row/column/gap 변경
summary/header/notes 배치 방식 변경
component-stage inset 또는 overflow 정책 변경
공통 SVG renderer의 scale, tick, axis, point, marker, label 처리 변경
font size/class/stroke/color 같은 공통 CSS 변경
data missing/null 처리 변경
standalone generated page의 payload filtering/override 변경
```

회귀 점검 순서는 저장된 chart 순서를 따른다. 예를 들어 CHART-ADAPT-002를 맞추는 과정에서 공통 renderer나 source-compare layout을 수정했다면, 다음 chart로 넘어가기 전에 CHART-ADAPT-001부터 다시 원본과 생성본을 비교한다.

회귀 점검에서는 다음을 확인한다.

```text
summary가 원본 위치와 폭에 있는지
panel title / note link / chart body 위치가 원본과 같은 구조인지
각 component가 영역 밖으로 벗어나지 않는지
이전에 맞춘 tick, axis label, marker, annotation, font가 깨지지 않았는지
standalone page override가 payload layout을 왜곡하지 않는지
```

회귀 점검 중 새 차이를 찾으면 기존 chart라도 payload/config 또는 renderer 일반 기능을 수정하고, 다시 생성한 뒤 원본과 캡처 비교한다.

## 원본 분석 체크리스트

원본 chart마다 다음 항목을 기록한다.

```text
chart_id
original html/css/js path
layout size and panel arrangement
component list
data sources
viewBox per SVG
margin per SVG
x/y scale domain
x/y ticks
axis labels
series color and stroke width
point visibility and point radius
vertical/horizontal markers
background regions
annotations and callouts
timeline role colors and labels
bar labels and value labels
legend text and colors
notes/interpretation handling
known mismatch
```

## Config 우선 정책

원본 차이를 발견하면 먼저 payload config로 해결한다.

| 원본 차이 | config로 표현 |
|---|---|
| 축 숫자가 다름 | `x_ticks`, `y_ticks` |
| 축 라벨 위치가 다름 | `x_axis_label`, `y_axis_label`, `axis_label_x`, `axis_label_y` |
| 선 색/두께가 다름 | `line_class`, `secondary_line_class` |
| 점이 원본에는 없음 | `show_points: false`, `show_secondary_points: false` |
| 특정 위치에 수직선 | `vertical_markers` |
| 그래프 내부 문구 | `annotations` |
| timeline 색상이 다름 | `role_class_map` |
| timeline 라벨 축약이 다름 | `label_map` |
| 특정 이벤트에 원 표시 | `highlight_event_type`, `highlight_point`, `highlight_radius` |
| 원본에는 y축 라벨 없음 | `y_axis_label: false` |
| panel 제목/설명 때문에 chart 위치가 다름 | layout area의 `title`, `description`, `stageInset` |
| 긴 panel 설명을 직접 노출하지 않음 | `description`은 panel header의 `Note` 버튼으로 표시하고 popup에서 보여줌 |
| 원본 SVG가 panel 밖으로 일부 흘러나옴 | 비교용 layout/CSS에서 overflow 허용 + `stageInset.bottom` 음수 |

Renderer 수정은 다음 조건일 때만 한다.

```text
같은 개념이 여러 chart에서 반복된다.
config로 선언 가능한 일반 옵션이다.
특정 chart ID나 특정 문구를 모르고도 동작한다.
기존 chart의 config-driven 동작을 깨지 않는다.
```

## 공통 Config 필드

### Layout Area Header와 Stage

원본 chart가 panel header와 SVG body를 분리하는 경우, renderer에 chart별 위치를 하드코딩하지 않고 layout area에 metadata를 둔다.

```json
{
  "area": "main",
  "title": "Pre/Post Retraining Performance",
  "description": "Champion AUC...",
  "headerHeight": 76,
  "stageInset": { "top": 84, "right": 16, "bottom": -8, "left": 16 }
}
```

`stageInset`은 해당 area 안에서 component SVG를 배치하는 일반 옵션이다. 원본 CSS가 `overflow: visible`처럼 동작하는 chart는 source-compare CSS에서만 overflow를 허용하고, 그 필요성은 chart-specific 기록에 남긴다.

`description`은 panel에 직접 긴 문장으로 표시하지 않고 `Note` 버튼의 popup 내용으로 사용한다.

### 좌표계

```json
{
  "view_box": [630, 440],
  "margin": { "top": 24, "right": 28, "bottom": 62, "left": 58 }
}
```

### 축

```json
{
  "x_ticks": [1, 8, 16, 24, 32],
  "y_ticks": [0.70, 0.78, 0.86, 0.94],
  "x_axis_label": "time index",
  "y_axis_label": "validation AUC"
}
```

`x_ticks: []`는 x tick을 표시하지 않는다는 뜻이다.

`y_axis_label: false`는 y축 라벨을 표시하지 않는다는 뜻이다.

### 선과 점

```json
{
  "line_class": "champion-line",
  "secondary_line_class": "challenger-line",
  "show_points": true,
  "show_secondary_points": true,
  "point_sample_every": 3,
  "point_radius": 3.5
}
```

### Marker와 Annotation

```json
{
  "vertical_markers": [
    { "x": 24, "class": "retrain-line" }
  ],
  "horizontal_markers": [
    { "y": 0.84, "class": "baseline-line", "label": "target AUC 0.84" }
  ],
  "annotations": [
    { "text": "retrain event", "x": 24, "y": 0.72, "class": "callout-retrain" }
  ]
}
```

### Event Marker Overlay

```json
{
  "value_source_component_id": "CHART-ADAPT-002.performance.0",
  "highlight_event_type": "retrain",
  "highlight_point": true,
  "highlight_radius": 6,
  "annotation_label": "retrain event",
  "annotation_dx": 1,
  "annotation_dy_fraction": -0.1
}
```

### Timeline

```json
{
  "role_class_map": {
    "normal": "state-normal",
    "warning": "state-warning",
    "alarm": "state-drift",
    "retrain": "state-retrain"
  },
  "label_map": {
    "retrain_monitor": "retrain/monitor"
  },
  "marker_role": "retrain",
  "marker_position_field": "start",
  "marker_circle": true,
  "marker_radius": 6
}
```

## CSS Class 정책

색상과 stroke width도 renderer 코드가 아니라 class와 config 조합으로 표현한다.

```css
.champion-line { fill: none; stroke: var(--active); stroke-width: 3; vector-effect: non-scaling-stroke; }
.challenger-line { fill: none; stroke: var(--ok); stroke-width: 3; vector-effect: non-scaling-stroke; }
.alarm-line { stroke: var(--warning); stroke-width: 2.4; stroke-dasharray: 4 4; vector-effect: non-scaling-stroke; }
.retrain-line { stroke: var(--danger); stroke-width: 2.6; stroke-dasharray: 5 4; vector-effect: non-scaling-stroke; }
```

새 chart에서 원본과 같은 스타일이 필요하면 먼저 기존 class를 재사용한다. 반복되는 스타일이면 class를 추가한다.

## Font 정책

Generated chart의 SVG 내부 텍스트는 현재 기본 `8px`이다.

적용 대상:

```text
axis tick
axis label
timeline label
annotation/callout
value/readout
generic label
```

Panel 제목, notes, sidebar 같은 application UI 텍스트는 이 정책의 대상이 아니다.

원본 chart마다 더 작은/큰 텍스트가 필요하면 renderer에 하드코딩하지 않고 config 또는 class로 조정한다.

## 비교 기준

원본과 generated를 비교할 때 다음 순서로 본다.

1. Layout area 위치와 비율
2. 각 component가 area를 채우는지
3. 데이터 곡선/막대/상태가 원본과 같은지
4. x/y scale domain
5. tick 값과 tick 개수
6. axis label 유무와 위치
7. series 색상과 두께
8. point 유무와 크기
9. marker line 위치와 스타일
10. annotation/callout 위치와 색상
11. timeline segment 색상과 라벨
12. text 크기와 겹침
13. legend/notes 표시 여부

## Issue 기록 방식

비교 중 문제가 생기면 다음 형식으로 이 문서나 chart-specific 작업 메모에 추가한다.

```text
Chart:
Component:
Observed mismatch:
Original behavior:
Generated behavior:
Decision:
  config change / renderer generalization / leave as known issue
Config added:
Renderer change:
Verification URL:
Commit:
```

## CHART-ADAPT-001에서 확정한 규칙

CHART-ADAPT-001 작업 중 확정한 사항:

```text
원본의 viewBox, margin, tick, label은 component config에 저장한다.
event marker는 overlay로 두되 원 표시/annotation은 config가 지시할 때만 그린다.
timeline의 role color와 label 축약은 role_class_map, label_map으로 저장한다.
Tree Size처럼 x tick이 없는 chart는 x_ticks: []로 명시한다.
y축 라벨이 없는 chart는 y_axis_label: false로 명시한다.
line color/stroke width는 line_class, secondary_line_class로 제어한다.
point 표시 여부는 show_points, show_secondary_points로 제어한다.
callout은 annotations 배열로 저장한다.
```

Renderer에는 다음 값이 있으면 안 된다.

```text
CHART-ADAPT-001
[1, 8, 16, 24, 32]
alternate replacement restores accuracy
node detector state timeline
```

이 값들은 payload/config에만 존재해야 한다.

## 다음 적용 대상

다음 대상은 `chart_adapt_002`다.

우선 원본에서 다음을 config로 추출한다.

```text
Pre/Post Retraining Performance
  champion/challenger series
  background pre/post region
  target AUC baseline
  alarm/retrain vertical marker
  alarm/retrain/promote point
  callout labels

Alarm & Retrain Timeline
  normal/warning/alarm/retrain segments
  alarm/retrain vertical marker and circles

Champion/Challenger
  horizontal comparison bars
  champion/challenger/latency colors
  value labels
```

Renderer에 필요한 일반 확장 후보:

```text
segmented secondary line for null values
background_regions config
horizontal_markers config
point_highlights config
comparison bar config
timeline multiple markers config
```

## CHART-ANNOT-001 진행 기록

ANNOT-001은 ADAPT 계열과 다른 원본 구조다.

```text
header summary
main large panel: One-sided Direction Overlay
right top panel: Upper vs Lower Test
right bottom panel: Variant Usage Matrix
bottom notes/legend
```

자동 변환 결과는 ADAPT-001 layout을 빌려 배치되어 원본과 거리가 컸다. 이에 따라 chart-specific DOM 복사가 아니라, 원본 HTML/CSS/JS에서 추출한 layout/config/data를 saved design payload로 추가했다.

payload/config로 저장한 값:

```text
baseline/current series
x/y ticks, y domain, viewBox, margin, axis labels
upper/lower fill 구간
upper/lower gap marker
upper/lower/baseline highlight point
upper/lower callout text
test card title/hypothesis/stat/decision rows
matrix method/direction/active rows
notes text와 legend labels/classes
```

runtime에 추가한 일반 기능:

```text
line component
  - fill_between: 두 series 사이의 특정 x 구간을 채움
  - gap_markers: 같은 x 위치에서 두 field 사이를 선으로 연결
  - point_highlights가 primary/secondary field 모두 참조 가능

matrix_view component
  - matrix_style: direction_dots
  - row/column/value data로 active/inactive dot matrix 렌더링

decision_card component
  - card_style: test_cards
  - data row의 title/hypothesis/stat/decision을 카드로 렌더링

domain_specific_visual component
  - card_style: notes_legend
  - data row의 note text와 legend 배열을 하단 notes panel로 렌더링
```

이 기능들은 특정 chart ID나 원본 문구를 runtime에 넣지 않고 config/data만 해석한다.

검증 URL:

```text
http://127.0.0.1:8766/chart_annot_001_generated.html?v=runtime3
http://127.0.0.1:8766/drift_report_charts/chart_annot_001.html?v=runtime3
```

현재 검증 한계:

```text
Chrome/Edge headless screenshot이 이 세션에서 파일을 생성하지 않아 자동 캡처 비교는 완료하지 못했다.
JS 문법 검사, payload 재생성, HTTP 제공 확인은 완료했다.
```

## CHART-ANNOT-002 진행 기록

ANNOT-002는 ANNOT-001과 같은 page layout 계열이지만 시각 요소가 다르다.

```text
header summary
main large panel: Approximation Error Band
right top panel: Projection Stability
right bottom panel: Quantile Error Detail
bottom notes/legend
```

payload/config로 저장한 값:

```text
exact/reference series
approx series
approx ± tolerance band
drift threshold horizontal marker
projection count별 spread
projection tolerance threshold
quantile별 absolute error
quantile target threshold
notes text와 legend labels/classes
```

runtime에 추가한 일반 기능:

```text
line component
  - primary_point_class, secondary_point_class, secondary_point_radius
  - fill_between으로 tolerance band 렌더링

bar_chart component
  - bar_style: vertical_threshold
  - threshold line, threshold label, over/normal bar class
  - bar_style: horizontal_threshold
  - horizontal error bars와 vertical target line
```

이 기능들은 특정 chart ID를 보지 않고 config/data만 해석한다.

검증 URL:

```text
http://127.0.0.1:8766/chart_annot_002_generated.html?v=runtime1
http://127.0.0.1:8766/drift_report_charts/chart_annot_002.html?v=runtime1
```

## CHART-ANOM-001 진행 기록

ANOM-001은 ANNOT 계열 page layout을 사용하지만 main chart가 line이 아니라 density distribution이다.

```text
header summary
main large panel: Anomaly Score Distribution
right top panel: Anomaly Rate Trend
right bottom panel: PCA/UMAP Projection
bottom notes/legend
```

payload/config로 저장한 값:

```text
baseline/current score density bins
anomaly score threshold vertical marker
outlier rate time series
outlier rate threshold horizontal marker
projection scatter x/y/group rows
notes text와 legend labels/classes
```

runtime에 추가한 일반 기능:

```text
distribution_view component
  - distribution_style: density_area
  - primary/secondary density area를 x/value field로 렌더링
  - vertical marker와 annotation 지원

projection_scatter component
  - viewBox/margin/x/y domain config
  - group_class_map, group_radius_map
  - crosshair grid와 annotation 지원
```

Generated chart의 panel 설명문은 가이드 규칙에 따라 Note popup으로만 노출한다.

검증 URL:

```text
http://127.0.0.1:8766/chart_anom_001_generated.html?v=runtime1
http://127.0.0.1:8766/drift_report_charts/chart_anom_001.html?v=runtime1
```

## CHART-ADAPT-002 진행 기록

1차 적용에서 다음 일반 기능을 renderer에 추가했다.

```text
line component
  - background_regions
  - horizontal_markers
  - point_highlights
  - null 값을 포함한 secondary line segmentation
  - null/undefined/빈 문자열은 숫자 0이 아니라 missing value로 처리

state_timeline component
  - markers 배열로 여러 marker line/circle 처리

bar/reference comparison component
  - series_fields 기반 multi-series horizontal bar
  - series_class_fields 기반 row별 bar class override

layout renderer
  - area별 title/description panel header
  - area별 stageInset
  - layout gridTemplateRows/gap
  - showAreaLabels false일 때 설계용 area label 숨김
```

이 기능들은 특정 chart ID나 특정 문구를 보지 않고 component config만 해석한다.

ADAPT-002 payload에는 다음 원본 규칙을 config로 저장했다.

```text
Pre/Post Retraining Performance
  - champion/challenger line class
  - pre/post background region
  - target AUC horizontal baseline
  - alarm/retrain vertical marker
  - alarm/retrain/promote point highlight
  - drift alarm / retrain event / challenger promoted annotation

Alarm & Retrain Timeline
  - role_class_map
  - normal/warning/alarm/retrain_monitor spans
  - alarm/retrain marker line and circle

Champion/Challenger
  - multi-series horizontal bars
  - champion/challenger series classes
  - latency row의 challenger bar class override
  - value labels
```

다음 육안 비교에서 확인할 항목:

```text
main chart의 background region 폭은 원본과 유사함
challenger line은 null을 0으로 처리하던 문제를 수정하여 t=21부터 시작함
alarm/retrain/promote point 위치와 크기는 원본과 유사함
panel title/description은 layout area metadata로 표시함
timeline과 comparison panel은 원본처럼 SVG가 panel 하단으로 일부 overflow되도록 stageInset을 조정함
comparison panel에서 latency row 색상은 원본처럼 별도 색으로 보임
사용자 요청에 따라 generated standalone 화면에서는 notes/generation notes를 숨김
```

남은 차이:

```text
timeline 하단 축선/일부 label의 위치와 두께는 원본 전용 SVG와 완전히 동일하지 않다.
comparison panel의 callout 문구는 공통 renderer annotation으로 표시되며 원본의 한글 문구와 완전히 같지는 않다.
notes 영역은 사용자 요청으로 generated standalone 화면에서 제외했으므로 원본 전체 페이지와 높이 구성이 다르다.
```

## CHART-ADAPT-001 회귀 점검 기록

ADAPT-002를 맞추는 과정에서 source-compare layout, panel header, note link, stageInset, summary displayValue, null 처리 등 공통 renderer/레이아웃 기능이 바뀌었다. 이에 따라 ADAPT-001을 다시 점검했다.

확인 및 수정 사항:

```text
summary area가 전체 폭으로 생성되던 문제를 원본처럼 오른쪽 header 영역으로 수정했다.
standalone generated page에서 rows: 6으로 강제하던 override를 제거했다.
ADAPT-001 generated page에도 source-compare layout을 적용했다.
panel title/description은 원본처럼 title + Note link 구조로 맞췄다.
replacement summary 값은 원본처럼 t=23 displayValue를 사용한다.
오른쪽 timeline/tree size component가 panel 밖으로 벗어나지 않도록 stageInset을 ADAPT-001에도 적용했다.
```

검증 URL:

```text
http://127.0.0.1:8766/chart_adapt_001_generated.html?v=layout2
```

## CHART-BOCD-001 Progress Record

```text
chart_id
  CHART-BOCD-001
original html/css/js path
  web/drift_report_charts/chart_bocd_001.html
  web/drift_report_charts/chart_bocd_001.css
  web/drift_report_charts/chart_bocd_001.js
layout size and panel arrangement
  1200x820 source-compare layout. Summary metrics at top right, large left heatmap, right top run-length heatmap, right bottom stream trend, bottom notes/legend.
component list
  decision_card summary
  heatmap matrix_style=heatmap_grid for change point probability
  heatmap matrix_style=heatmap_grid for run length posterior
  trend_line for stream trend
  domain_specific_visual notes_legend
data sources
  cp heatmap row value arrays extracted from the original cp probability formula
  run-length row value arrays extracted from original posterior intensity logic
  stream values copied from original stream array
viewBox per SVG
  cp heatmap 630x440
  run length posterior 472x185
  stream trend 472x185
margin per SVG
  cp heatmap top 24 right 28 bottom 62 left 58
  run length and stream top 12 right 22 bottom 34 left 48
x/y scale domain
  cp heatmap x t=1..32, y probability 0..1
  run length x t=1..32 with 12 posterior bands
  stream x t=1..32, y 0.40..1.20
x/y ticks
  cp heatmap x [1,8,16,24,32], y [0,0.5,1]
  stream y [0.5,0.8,1.1]
axis labels
  cp heatmap: time index / P(change point)
  run length: run length posterior resets caption
  stream: stream with change markers
series color and stroke width
  stream-line #2f6f9f stroke 2.8
  mean-line #3a8064 dashed stroke 2
point visibility and point radius
  stream base points hidden
  marker-point highlights at t=18 and t=27 radius 6
vertical/horizontal markers
  cp markers at t=18 and t=27
  run length marker at t=18
  stream markers at t=18 and t=27
  stream mean bands y=0.55 for t=1..18, y=0.87 for t=18..27, y=1.10 for t=27..32
annotations and callouts
  cp heatmap: posterior spike
  run length: reset
  stream: mean shift
timeline role colors and labels
  n/a
bar labels and value labels
  n/a
legend text and colors
  low posterior, medium, high posterior, change marker
notes/interpretation handling
  Panel descriptions are Note popup links. Bottom interpretation is notes_legend component data.
known mismatch
  The generated heatmaps use the common heatmap_grid renderer and payload value arrays, so cell geometry and palette interpolation are close but not pixel-identical to the original hand-coded SVG loops.
```

## CHART-CAT-001 Progress Record

```text
chart_id
  CHART-CAT-001
original html/css/js path
  web/drift_report_charts/chart_cat_001.html
  web/drift_report_charts/chart_cat_001.css
  web/drift_report_charts/chart_cat_001.js
layout size and panel arrangement
  1200x820 source-compare layout. Summary metrics at top right, large left observed/expected grouped bar chart, right top standardized residual cells, right bottom chi-square contribution ranking, bottom notes/legend.
component list
  decision_card summary
  bar_chart bar_style=vertical_grouped for observed vs expected
  matrix_view matrix_style=category_cells for standardized residuals
  contribution_view bar_style=horizontal_ranked for chi-square contribution
  domain_specific_visual notes_legend
data sources
  categories A등급/B등급/C등급/D등급/기타/미상
  expected [132,210,176,112,58,32]
  observed [101,194,225,139,39,22]
  residual and contribution values computed from original formula
viewBox per SVG
  observed/expected 630x440
  residual cells 472x185
  contribution ranking 472x185
margin per SVG
  observed/expected top 20 right 22 bottom 58 left 62
  residual top 12 right 22 bottom 28 left 76
  contribution top 8 right 22 bottom 28 left 84
x/y scale domain
  observed/expected y 0..250
  contribution x 0..16.1
x/y ticks
  observed/expected y [0,63,125,188,250]
axis labels
  observed/expected: category / 빈도
  contribution: (O-E)^2 / E
series color and stroke width
  expected-bar rgba(36,107,159,0.62)
  observed-bar rgba(198,78,78,0.58)
point visibility and point radius
  n/a
vertical/horizontal markers
  n/a
annotations and callouts
  observed/expected callout: 기여 최대: C등급
timeline role colors and labels
  n/a
bar labels and value labels
  residual cells show residual values
  contribution bars show contribution values
legend text and colors
  기대 빈도, 관측 빈도, 과대 관측, 과소 관측
notes/interpretation handling
  Panel descriptions are Note popup links. Bottom interpretation is notes_legend component data.
runtime change
  Added generic bar_style=vertical_grouped, bar_style=horizontal_ranked, matrix_style=category_cells.
known mismatch
  Residual cell strip and contribution ranking are common-runtime approximations of the original hand-coded SVG layout. Geometry, value order, colors, and labels match closely, but text baseline and exact pixel spacing may differ.
```

## CHART-CAT-002 Progress Record

```text
chart_id
  CHART-CAT-002
original html/css/js path
  web/drift_report_charts/chart_cat_002.html
  web/drift_report_charts/chart_cat_002.css
  web/drift_report_charts/chart_cat_002.js
layout size and panel arrangement
  1200x820 source-compare layout. Summary metrics at top right, large left category proportion comparison, right top absolute delta ranking, right bottom total variation trend, bottom notes/legend.
component list
  decision_card summary
  proportion_view bar_style=vertical_grouped for reference/current proportions
  contribution_view bar_style=horizontal_ranked for absolute delta ranking
  trend_line for total variation trend
  domain_specific_visual notes_legend
data sources
  categories 검색/상세/장바구니/구매/반품/문의/리뷰
  reference [0.26,0.21,0.14,0.16,0.05,0.12,0.06]
  current [0.18,0.19,0.18,0.24,0.08,0.08,0.05]
  delta, absDelta, deltaLabel computed from current-reference
  tv trend [0.07,0.08,0.10,0.12,0.14,0.16,0.15]
viewBox per SVG
  proportion comparison 630x440
  absolute delta 472x185
  total variation trend 472x185
margin per SVG
  proportion top 20 right 22 bottom 70 left 58
  delta top 8 right 22 bottom 28 left 98
  trend top 12 right 18 bottom 34 left 48
x/y scale domain
  proportion y 0..0.30
  delta x 0..0.098
  trend y 0..0.24, x window 1..7
x/y ticks
  proportion y [0,0.10,0.20,0.30]
  trend y [0,0.15,0.24]
axis labels
  proportion: category / 비율
  delta: |현재 - 기준|
  trend: window
series color and stroke width
  ref-bar rgba(36,107,159,0.62)
  cur-bar rgba(198,78,78,0.58)
  delta-bar rgba(47,127,111,0.78)
  trend-line #2f7f6f stroke 3
point visibility and point radius
  trend-point radius 4 for every window
vertical/horizontal markers
  trend horizontal threshold y=0.15 with 관리 기준 label
annotations and callouts
  proportion callout: 최대 이동: 검색 -0.08
timeline role colors and labels
  n/a
bar labels and value labels
  delta ranking uses value_label_field=deltaLabel to display abs delta plus signed delta.
legend text and colors
  기준 비율, 현재 비율, 절대 Delta, 관리 기준
notes/interpretation handling
  Panel descriptions are Note popup links. Bottom interpretation is notes_legend component data.
runtime change
  horizontal_ranked now supports generic value_label_field/display_value_field for caller-provided value labels.
known mismatch
  Proportion bars, delta ranking, and TV trend use common runtime approximations. Data, ordering, colors, and labels match the original intent, but exact SVG text baseline and spacing may differ from the original hand-coded chart.
```

## CHART-CAT-003 Progress Record

```text
chart_id
  CHART-CAT-003
original html/css/js path
  web/drift_report_charts/chart_cat_003.html
  web/drift_report_charts/chart_cat_003.css
  web/drift_report_charts/chart_cat_003.js
layout size and panel arrangement
  1200x820 source-compare layout. Summary metrics at top right, large left category proportion comparison with max-category band, right top maximum delta ranking, right bottom L-infinity trend, bottom notes/legend.
component list
  decision_card summary
  proportion_view bar_style=vertical_grouped for reference/current proportions
  contribution_view bar_style=horizontal_ranked for max category deltas
  trend_line for L-infinity trend
  domain_specific_visual notes_legend
data sources
  categories 검색/상세/장바구니/구매/반품/문의/리뷰
  reference [0.28,0.20,0.13,0.15,0.05,0.13,0.06]
  current [0.16,0.19,0.15,0.23,0.08,0.12,0.07]
  delta, absDelta, deltaLabel computed from current-reference
  L-infinity trend [0.05,0.06,0.07,0.08,0.09,0.11,0.12]
viewBox per SVG
  proportion comparison 630x440
  max delta ranking 472x185
  L-infinity trend 472x185
margin per SVG
  proportion top 20 right 22 bottom 70 left 58
  max delta top 8 right 22 bottom 28 left 98
  trend top 12 right 18 bottom 34 left 48
x/y scale domain
  proportion y 0..0.32
  max delta x 0..0.146
  trend y 0..0.18, x window 1..7
x/y ticks
  proportion y [0,0.10,0.20,0.30]
  trend y [0,0.10,0.18]
axis labels
  proportion: category / 비율
  max delta: max |현재 - 기준|
  trend: window
series color and stroke width
  ref-bar rgba(36,107,159,0.62)
  cur-bar rgba(198,78,78,0.58)
  max-bar rgba(47,127,111,0.78)
  other-bar rgba(95,107,122,0.34)
  trend-line #2f7f6f stroke 3
point visibility and point radius
  trend-point radius 4 for every window
vertical/horizontal markers
  trend horizontal threshold y=0.10 with 관리 기준 label
background regions
  vertical_grouped category_highlights marks 검색 with highlight-band
annotations and callouts
  proportion callout: 최대 변화: 검색 -0.12
timeline role colors and labels
  n/a
bar labels and value labels
  max delta ranking uses value_label_field=deltaLabel to display abs delta plus signed delta.
legend text and colors
  기준 비율, 현재 비율, 최대 Delta, 관리 기준
notes/interpretation handling
  Panel descriptions are Note popup links. Bottom interpretation is notes_legend component data.
runtime change
  vertical_grouped now supports generic category_highlights entries by category or index.
known mismatch
  The highlighted category band and bar ranking use common runtime geometry, so exact x offsets and text baseline can differ from the original hand-coded SVG, while data, order, colors, threshold, and labels match the original intent.
```

## CHART-CAT-004 Progress Record

```text
chart_id
  CHART-CAT-004
original html/css/js path
  web/drift_report_charts/chart_cat_004.html
  web/drift_report_charts/chart_cat_004.css
  web/drift_report_charts/chart_cat_004.js
layout size and panel arrangement
  1200x820 source-compare layout. Summary metrics at top right, large left 2x2 contingency mosaic, right top event-rate comparison, right bottom odds-ratio forest plot, bottom notes/legend.
component list
  decision_card summary
  matrix_view matrix_style=mosaic_2x2
  proportion_view bar_style=vertical_grouped for event rates
  forest_plot for odds ratio and 95% CI
  domain_specific_visual notes_legend
data sources
  reference row event=6 nonevent=36 total=42 rate=14.3%
  current row event=14 nonevent=24 total=38 rate=36.8%
  Fisher p=0.018, one-sided p=0.009
  oddsRatio=3.50, ciLow=1.18, ciHigh=10.4
viewBox per SVG
  mosaic 630x440
  event-rate 472x185
  forest plot 472x185
margin per SVG
  mosaic top 32 right 36 bottom 52 left 70
  rate top 8 right 26 bottom 35 left 54
  forest top 20 right 28 bottom 42 left 60
x/y scale domain
  rate y 0..0.45
  forest log x 0.3..12
x/y ticks
  rate y [0,0.15,0.30,0.45] formatted as percent
  forest x [0.5,1,2,4,8]
axis labels
  rate y Event rate
  forest x 현재 event odds / 기준 event odds
series color and stroke width
  event-fill rgba(45,111,143,0.82)
  nonevent-fill rgba(201,215,223,0.92)
  ref-bar rgba(36,107,159,0.62)
  cur-bar rgba(198,78,78,0.58)
  or-line #b4554b stroke 5
point visibility and point radius
  odds-ratio point radius 8
vertical/horizontal markers
  forest null marker x=1 with threshold-line class
annotations and callouts
  mosaic caption two-sided p=0.018, one-sided p=0.009
  forest label OR 3.50 [1.18, 10.4], Null
runtime change
  matrix_style=mosaic_2x2 renders config-driven two-part mosaic rows.
  forest_plot renders log-scale interval/point/null marker.
  vertical_grouped supports row-driven series_class_fields, value_label_fields, category_sub_label_field, and y_tick_format=percent.
notes/interpretation handling
  Panel descriptions are Note popup links. Bottom interpretation is notes_legend component data.
known mismatch
  Mosaic rounded-rectangle clipping and text baselines are common-runtime approximations of the original hand-coded SVG. Forest plot uses the same log-domain/ticks/CI values but exact spacing can differ slightly.
```

## CHART-CLS-001 Progress Record

```text
chart_id
  CHART-CLS-001
original html/css/js path
  web/drift_report_charts/chart_cls_001.html
  web/drift_report_charts/chart_cls_001.css
  web/drift_report_charts/chart_cls_001.js
layout size and panel arrangement
  1200x820 source-compare layout. Summary metrics at top left header, large left domain-classifier ROC below, right top score distribution, right bottom feature importance plus projection, bottom notes/legend.
component list
  decision_card summary
  model_diagnostic_curve for ROC with area fill and random diagonal marker
  distribution_view distribution_style=density_area for baseline/current classifier scores
  feature_projection_view for feature-importance bars plus projection scatter
  domain_specific_visual notes_legend
data sources
  ROC points from original JS, AUC=0.89
  score bins 0.05..0.96 with baseline peak 38 at 0.19 and current peak 36 at 0.68
  feature importance emb_17=0.31, emb_04=0.24, emb_22=0.19, emb_09=0.14
  deterministic projection coordinates materialized from original JS into payload data
viewBox per SVG
  ROC 630x440
  score distribution 472x185
  feature/projection 472x185
margin per SVG
  ROC top 24 right 30 bottom 62 left 58
  score distribution top 14 right 24 bottom 34 left 46
x/y scale domain
  ROC x/y 0..1
  score distribution x 0.05..0.96, y 0..42
  projection x -1.7..2.3, y -1.2..1.4
x/y ticks
  ROC x/y [0,0.25,0.5,0.75,1]
  score distribution x [0.05,0.5,0.96], y [0,14,28,42]
axis labels
  ROC false positive rate / true positive rate
  score distribution domain probability
series color and stroke width
  roc-line #b95a50 stroke 3.2 with roc-fill rgba(185,90,80,0.10)
  base-area #2f6f9f and current-area #3a8064
  bar-feature rgba(201,149,47,0.78)
point visibility and point radius
  ROC dots sampled every 2 points plus last, radius 4
  projection baseline/current dots radius 4
vertical/horizontal markers
  ROC random diagonal marker uses random-line class
  score distribution vertical marker at 0.5 uses random-line class
annotations and callouts
  ROC AUC callout, score separation callout, emb_17 top annotation
runtime change
  renderLine supports generic area_under_line and diagonal_markers config.
  distribution density area supports y_axis_label=false.
  feature_projection_view is a config-driven composite renderer with feature bars and grouped scatter points.
  Follow-up visual audit added configurable feature_projection_view projection_frame_class and crosshair_class.
notes/interpretation handling
  Panel descriptions are original Korean Note popup links. Bottom interpretation is notes_legend component data with original Korean title/body.
known mismatch
  Follow-up fixed the feature/projection panel's dark scatter frame using generic projection frame and crosshair classes. Exact text baselines and scatter frame spacing can still differ slightly from the original hand-coded SVG while data, positions, classes, and panel structure match.
```

## CHART-CTRL-001 Progress Record

```text
chart_id
  CHART-CTRL-001
original html/css/js path
  web/drift_report_charts/chart_ctrl_001.html
  web/drift_report_charts/chart_ctrl_001.css
  web/drift_report_charts/chart_ctrl_001.js
layout size and panel arrangement
  1200x820 source-compare layout. Summary metrics are right-aligned in the top header with min width 430px. Large raw metric trend is left, CUSUM control chart is right top, direction summary is right bottom, notes/legend are bottom.
component list
  decision_card summary
  raw_signal_trend for raw metric with target and alarm marker
  control_chart for C+ and C- CUSUM lines with control limit
  ranking_view bar_style=horizontal_threshold for direction summary
  domain_specific_visual notes_legend
data sources
  raw metric length 32 from original JS, target=0.53
  C+ max 52.9, C- max 0.1, control limit 25, alarm index 25
  direction summary C+ 상방 52.9 and C- 하방 0.1
viewBox per SVG
  raw metric 630x440
  CUSUM control 472x185
  direction summary 472x185
margin per SVG
  raw metric top 24 right 28 bottom 62 left 58
  CUSUM top 12 right 22 bottom 34 left 48
  direction top 18 right 32 bottom 34 left 86
x/y scale domain
  raw x 1..32, y 0.45..0.90
  CUSUM x 1..32, y 0..56
  direction x 0..60
x/y ticks
  raw x [1,8,16,24,32], y [0.5,0.6,0.7,0.8,0.9]
  CUSUM y [0,20,40]
axis labels
  raw time index / metric
  CUSUM time index
series color and stroke width
  raw-line #2f6f9f stroke 2.6
  pos-line #b95a50 stroke 3
  neg-line #3a8064 stroke 3
  target-line and cusum-limit-line #c9952f dashed
  bar-pos rgba(185,90,80,0.74), bar-neg rgba(58,128,100,0.72)
point visibility and point radius
  raw alarm point radius 7 at t=25
  C+ sampled points every 3 plus alarm highlights t=25..32 radius 4.6
vertical/horizontal markers
  raw horizontal target 0.53 and vertical alarm t=25
  CUSUM horizontal control limit 25
annotations and callouts
  raw target 0.53 and 상방 CUSUM alarm
  CUSUM control limit 25
  direction caption 상방 변화가 지배적
runtime change
  No runtime behavior added. Existing renderLine horizontal/vertical markers, point_highlights, secondary line, and horizontal_threshold bars cover the chart.
notes/interpretation handling
  Panel descriptions are original Korean Note popup links. Bottom interpretation is notes_legend component data with original Korean title/body.
known mismatch
  CUSUM positive points use common sampled point handling plus configured alarm highlights, so exact duplicate point layering and text baselines may differ slightly from the original hand-coded SVG. Data, thresholds, positions, colors, and panel layout match the source intent.
```

## CHART-CTRL-002 Progress Record

```text
chart_id
  CHART-CTRL-002
original html/css/js path
  web/drift_report_charts/chart_ctrl_002.html
  web/drift_report_charts/chart_ctrl_002.css
  web/drift_report_charts/chart_ctrl_002.js
layout size and panel arrangement
  1200x820 source-compare layout. Summary metrics are right-aligned in the top header with min width 430px. Large raw metric plus EWMA chart is left, EWMA control chart is right top, alarm timeline is right bottom, notes/legend are bottom.
component list
  decision_card summary
  raw_signal_trend for raw metric plus EWMA secondary line
  control_chart for EWMA with UCL/LCL/center markers
  state_timeline for normal/warning/alarm intervals
  domain_specific_visual notes_legend
data sources
  raw metric and ewma length 32 from original JS
  center=0.50, UCL=0.72, LCL=0.28, alarmIndex=27
  lambda=0.20, final EWMA=0.80, shift=+0.30
  timeline normal 1..21, warning 21..27, alarm 27..32
viewBox per SVG
  raw/EWMA 630x440
  EWMA control 472x185
  timeline 472x185
margin per SVG
  raw/EWMA top 24 right 28 bottom 62 left 58
  EWMA control top 12 right 22 bottom 34 left 48
  timeline top 32 right 24 bottom 38 left 48
x/y scale domain
  raw/EWMA x 1..32, y 0.25..0.85
  EWMA control x 1..32, y 0.20..0.86
  timeline x 1..32
x/y ticks
  raw x [1,8,16,24,32], y [0.3,0.5,0.7]
  control y [0.3,0.5,0.7]
axis labels
  raw time index / metric
  control time index
  timeline EWMA alarm marker timeline
series color and stroke width
  raw-noise-line #2f6f9f stroke 2.3 opacity .82
  smooth-line #3a8064 stroke 3
  ewma-limit-line #c9952f dashed
  center-line #2b3640 dashed
  ewma-alarm-line #b95a50 dashed
point visibility and point radius
  raw chart alarm point radius 7 at EWMA t=27
  control chart sampled smooth points every 3 plus alarm highlights t=27..32 radius 4.8
vertical/horizontal markers
  raw center line at 0.50 and alarm vertical marker at t=27
  control UCL 0.72, LCL 0.28, center 0.50
annotations and callouts
  raw callout: EWMA가 raw noise를 완화해 상승 추세를 포착
  control label: UCL 0.72
runtime change
  No runtime behavior added. Existing renderLine secondary_value_field, horizontal_markers, vertical_markers, point_highlights, and state_timeline cover the chart.
notes/interpretation handling
  Panel descriptions are original Korean Note popup links. Bottom interpretation is notes_legend component data with original Korean title/body.
known mismatch
  EWMA control chart uses common sampled point handling plus configured alarm highlights, so exact point layering and text baselines can differ slightly from the original hand-coded SVG. Timeline labels are rendered by the common state_timeline component but preserve the same intervals, marker, colors, and labels.
```

## CHART-CTRL-003 Progress Record

```text
chart_id
  CHART-CTRL-003
original html/css/js path
  web/drift_report_charts/chart_ctrl_003.html
  web/drift_report_charts/chart_ctrl_003.css
  web/drift_report_charts/chart_ctrl_003.js
layout size and panel arrangement
  1200x820 source-compare layout. Summary metrics are right-aligned in the top header with min width 430px. Large MEWMA statistic control chart is left, metric contribution is right top, multivariate small multiples are right bottom, notes/legend are bottom.
component list
  decision_card summary
  control_chart for MEWMA statistic with UCL/alarm markers
  contribution_view bar_style=horizontal_ranked for contribution shares
  small_multiple_lines for aligned metric mini line rows
  domain_specific_visual notes_legend
data sources
  MEWMA statistic length 32 from original JS, UCL=12.0, alarmIndex=23, final=19.1
  contribution risk_score 38%, amount 24%, frequency 18%, latency 12%, region_mix 8%
  small multiple rows for risk_score, amount, frequency length 16 each
viewBox per SVG
  MEWMA statistic 630x440
  contribution 472x185
  small multiples 472x185
margin per SVG
  statistic top 24 right 28 bottom 62 left 58
  contribution top 14 right 32 bottom 26 left 96
  small multiples top 8 right 22 bottom 22 left 82
x/y scale domain
  statistic x 1..32, y 0..22
  contribution x 0..42
  small multiples x 1..16, y 0.35..0.72
x/y ticks
  statistic x [1,8,16,24,32], y [0,5,10,15,20]
axis labels
  statistic time index / MEWMA statistic
  contribution alarm contribution share
  small multiples time aligned metrics
series color and stroke width
  mewma-stat-line #2f6f9f stroke 3
  ewma-limit-line #c9952f dashed
  ewma-alarm-line #b95a50 dashed
  metric-line #3a8064, metric-line.alt #7d6fb2, metric-line.third #c9952f
  bar-fill rgba(58,128,100,0.78), hot rgba(185,90,80,0.80)
point visibility and point radius
  statistic sampled stat points plus alarm highlights from t=23 onward; alarm t=23 radius 7
vertical/horizontal markers
  statistic UCL 12.0 and vertical alarm t=23
  small multiples vertical alarm alignment at x about 12.2
annotations and callouts
  statistic UCL 12.0 and alarm crossing text
  small multiples 동시 상승 label
runtime change
  Adds generic small_multiple_lines renderer for config-driven series rows. It groups data by series, maps x/y domains from config, supports per-series classes, vertical markers, and captions.
  Follow-up visual audit extends generic horizontal_ranked with optional row_background_class for source row background rectangles.
notes/interpretation handling
  Panel descriptions are original Korean Note popup links. Bottom interpretation is notes_legend component data with original Korean title/body.
known mismatch
  Follow-up fixed contribution row background rectangles using generic horizontal_ranked row_background_class.
  Small multiples use the common small_multiple_lines renderer, so exact x marker position and text baselines can differ slightly from the original hand-coded SVG while data, colors, labels, and layout match.
```

## CHART-DIST-001 Progress Record

```text
chart_id
  CHART-DIST-001
original html/css/js path
  web/drift_report_charts/chart_dist_001.html
  web/drift_report_charts/chart_dist_001.css
  web/drift_report_charts/chart_dist_001.js
layout size and panel arrangement
  1200x820 source-compare layout. Summary metrics are right-aligned in the top header with min width 430px. Large reference/current distribution comparison is left, distance trend is right top, feature distance ranking is right bottom, notes/legend are bottom.
component list
  decision_card summary
  distribution_view distribution_style=density_area with quantile transport segment markers
  distance_metric_view for Wasserstein distance trend
  ranking_view bar_style=horizontal_ranked for feature distance ranking
  domain_specific_visual notes_legend
data sources
  Seeded reference/current samples from original JS are materialized as 50-point KDE density rows.
  Wasserstein distance=0.6791, mean shift=0.6791, q90 shift=0.8611.
  Reference mean -0.0719, current mean 0.6073, reference median -0.0598, current median 0.5822.
  Transport quantiles p=.25/.50/.75 use original quantile x0/x1 coordinates.
viewBox per SVG
  distribution 630x440
  distance trend 472x185
  ranking 472x185
margin per SVG
  distribution top 20 right 22 bottom 50 left 58
  trend top 12 right 18 bottom 34 left 48
  ranking top 8 right 22 bottom 28 left 112
x/y scale domain
  distribution x -3.5..4.5, y 0..0.4455
  trend x 1..9, y 0..0.8
  ranking x 0..0.8
x/y ticks
  distribution x [-3.5,0,4.5], y [0,0.1485,0.297,0.4455]
  trend y [0,0.3,0.8]
axis labels
  distribution 특성값 / 밀도
  trend window
  ranking distance
series color and stroke width
  ref-area rgba(36,107,159,0.22) stroke #246b9f 2.5
  cur-area rgba(198,78,78,0.22) stroke #c64e4e 2.5
  transport #2f7f6f dashed
  trend-line #2f7f6f stroke 3
  dist-bar rgba(47,127,111,0.75), dist-bar-highlight rgba(198,78,78,0.78)
point visibility and point radius
  transport endpoints radius 4
  trend points radius 4 each window
vertical/horizontal markers
  distribution quantile transport horizontal segments for p=.25/.50/.75
  trend horizontal management threshold at 0.30
annotations and callouts
  distribution: 분위수 이동량의 평균이 Wasserstein 거리
  trend: 관리 기준
runtime change
  distribution density_area supports generic segment_markers with x0/x1/y, line class, endpoint point class, and radius.
notes/interpretation handling
  Panel descriptions are original Korean Note popup links. Bottom interpretation is notes_legend component data with original Korean title/body.
known mismatch
  KDE density is materialized with 50 points instead of the original 160 DOM-generated points; overall shape, statistics, quantile transport lines, labels, and panel layout match. Ranking uses common horizontal_ranked geometry, so exact text baseline can differ slightly.
```

## CHART-DISTSHAPE-001 Progress Record

```text
chart_id
  CHART-DISTSHAPE-001
original html/css/js path
  web/drift_report_charts/chart_distshape_001.html
  web/drift_report_charts/chart_distshape_001.css
  web/drift_report_charts/chart_distshape_001.js
layout size and panel arrangement
  1200x820 source-compare layout. Summary metrics are right-aligned in the top header with min width 430px. Large distribution comparison is left, ECF difference is right top, statistic contribution is right bottom, notes/legend are bottom.
component list
  decision_card summary
  distribution_view distribution_style=density_area with reference/current areas and optional difference band
  distance_metric_view for ECF real/imaginary component differences
  contribution_view bar_style=horizontal_ranked for Epps-Singleton contribution ranking
  domain_specific_visual notes_legend
data sources
  Density rows use original xValues/referenceDensity/currentDensity arrays plus abs(current-reference) as difference.
  ECF rows use original frequencies, realDiff, and imagDiff arrays.
  Contribution values are realDiff^2 + imagDiff^2 sorted by original JS rule.
  ES statistic=12.8, p-value=0.006, top contribution t=2.0.
viewBox per SVG
  distribution 630x440
  ECF 472x185
  contribution 472x185
margin per SVG
  distribution top 24 right 28 bottom 62 left 58
  ECF top 12 right 22 bottom 34 left 48
  contribution top 8 right 22 bottom 30 left 70
x/y scale domain
  distribution x 18..82, y 0..1.05
  ECF x 0.5..3.0, y -0.03..0.27
  contribution x 0..0.1172
x/y ticks
  distribution x [20,40,60,80], y [0,0.25,0.50,0.75,1.0]
  ECF y [0,0.10,0.20]
axis labels
  distribution feature value / density
  ECF frequency t
  contribution stat=12.8, p=0.006 annotation
series color and stroke width
  ref-area rgba(36,107,159,0.22) stroke #246b9f 2.5
  cur-area rgba(198,78,78,0.22) stroke #c64e4e 2.5
  diff-band rgba(58,128,100,0.13)
  real-line #3a8064 stroke 3, imag-line #b95a50 stroke 3
  stat-bar rgba(58,128,100,0.76), top-stat-bar rgba(185,90,80,0.76)
point visibility and point radius
  ECF real/imaginary points radius 4 at every frequency.
vertical/horizontal markers
  ECF zero-line at y=0.
annotations and callouts
  distribution: 현재 분포는 65 부근 봉우리와 오른쪽 shoulder가 커짐
  ECF: Real diff / Imag diff
runtime change
  distribution density_area supports generic difference_value_field and difference_area_class to draw a third area-under-baseline layer before primary and secondary areas.
notes/interpretation handling
  Panel descriptions are original Korean Note popup links. Bottom notes_legend keeps the original Korean title 현재 상황 요약 and body text.
known mismatch
  Distribution callout alignment uses common annotation positioning rather than original text-anchor=middle. Contribution bars use common horizontal_ranked geometry, so row baselines can differ slightly while data, layout, colors, and labels match.
```

## CHART-EDF-001 Progress Record

```text
chart_id
  CHART-EDF-001
original html/css/js path
  web/drift_report_charts/chart_edf_001.html
  web/drift_report_charts/chart_edf_001.css
  web/drift_report_charts/chart_edf_001.js
layout size and panel arrangement
  1200x820 source-compare layout. Summary metrics are right-aligned in the top header with min width 430px. Large empirical CDF comparison is left, histogram comparison is right, notes/legend are bottom.
component list
  decision_card summary
  cumulative_curve for reference/current empirical CDFs with KS gap marker
  histogram_view distribution_style=histogram_overlay for continuous reference/current density bins
  domain_specific_visual notes_legend
data sources
  Original seeded normal samples are materialized into ECDF rows and 24 histogram bins.
  KS statistic=0.2169, p-value=0.0000157, max gap at x=0.7444 with reference CDF 0.8038 and current CDF 0.5870.
  Summary rows preserve original displays: KS 통계량 0.217, 근사 p-value <0.001, 표본 수 260 / 230.
viewBox per SVG
  ECDF 650x470
  histogram 390x470
margin per SVG
  both top 22 right 24 bottom 52 left 58
x/y scale domain
  ECDF x -2.5..4, y 0..1
  histogram x -2.5..4, y 0..0.5061
x/y ticks
  ECDF x [-2.5,-0.875,0.75,2.375,4], y [0,0.25,0.5,0.75,1]
  histogram x [-2.5,0.75,4], y [0,0.253,0.5061]
axis labels
  특성값 / 경험 CDF
  특성값 / 밀도
series color and stroke width
  ref-line #246b9f stroke 3
  cur-line #c64e4e stroke 3
  gap-line #2f9b73 stroke 3 dashed
  bar-ref rgba(36,107,159,0.52)
  bar-cur rgba(198,78,78,0.46)
point visibility and point radius
  ECDF lines suppress sampled points; KS gap endpoints use gap-point radius 4.
vertical/horizontal markers
  ECDF gap marker at x=0.7444 between reference/current CDF values.
annotations and callouts
  D = 0.217 label near the KS gap.
runtime change
  renderLine gap_markers support optional point_class/r endpoint circles.
  distribution renderer supports generic histogram_overlay with x0/x1 fields, primary/secondary density fields, bar classes, width fractions, offsets, and continuous axes.
notes/interpretation handling
  Panel descriptions are original Korean Note popup links. Bottom notes_legend keeps original Korean title 해석 and body text.
known mismatch
  Follow-up fixed ECDF materialization to use the original 180 sampling points plus one exact KS marker helper row.
  Follow-up fixed ECDF/histogram tick labels with generic fixed1 tick formatting.
```

## CHART-EDF-002 Progress Record

```text
chart_id
  CHART-EDF-002
original html/css/js path
  web/drift_report_charts/chart_edf_002.html
  web/drift_report_charts/chart_edf_002.css
  web/drift_report_charts/chart_edf_002.js
layout size and panel arrangement
  1200x820 source-compare layout. Summary metrics are right-aligned in the top header with min width 430px. Tail-weighted CDF comparison is left, QQ comparison is right, notes/legend are bottom.
component list
  decision_card summary
  cumulative_curve for reference/current empirical CDFs with lower/upper tail background regions
  projection_scatter for QQ points with diagonal reference line
  domain_specific_visual notes_legend
data sources
  Original seeded samples are materialized into 91 ECDF rows and 39 QQ quantile pairs.
  Tail score=0.4996, reference q05=-1.8566, q95=1.7185.
  Reference q98/q99=2.3753/2.6009, current q98/q99=3.1020/3.6081.
  Summary rows preserve original displays: AD 통계량 2.84, 근사 p-value 0.012, Tail 차이 0.50.
viewBox per SVG
  Tail CDF 535x450
  QQ 535x450
margin per SVG
  both top 22 right 26 bottom 52 left 58
x/y scale domain
  Tail CDF x -5..7, y 0..1
  QQ x -2.5..3, y -2.5..3
x/y ticks
  Tail CDF x [-5,0,7], y [0,0.25,0.5,0.75,1]
  QQ x [-2.5,0,3], y [-2.5,0,3]
axis labels
  Tail CDF 특성값 / 경험 CDF
  QQ 기준 분위수 / 현재 분위수
series color and stroke width
  ref-line #246b9f stroke 3
  cur-line #c64e4e stroke 3
  tail-band rgba(122,93,199,0.10)
  qq-point rgba(198,78,78,0.72), qq-ref #246b9f dashed
point visibility and point radius
  Tail CDF suppresses sampled points. QQ points use radius 5 in tails and 3.5 in the middle.
vertical/horizontal markers
  Tail CDF lower and upper tail bands use background_regions from reference q05/q95.
  QQ uses diagonal_markers for y=x.
annotations and callouts
  Tail CDF lower/upper tail labels.
  QQ: 점선에서 멀수록 분위수 차이가 큼.
runtime change
  Scatter renderer supports generic x/y ticks, y axis labels, diagonal_markers, and data-space annotations. Tail bands use existing line background_regions.
notes/interpretation handling
  Panel descriptions are original Korean Note popup links. Bottom notes_legend keeps original Korean title 해석 and body text.
known mismatch
  Follow-up fixed Tail CDF materialization to use the original 180 sampling points.
  Follow-up fixed Tail CDF and QQ ticks with generic fixed1 tick formatting; tail band labels and QQ annotation remain config-positioned in source data space.
```

## CHART-EDF-003 Progress Record

```text
chart_id
  CHART-EDF-003
original html/css/js path
  web/drift_report_charts/chart_edf_003.html
  web/drift_report_charts/chart_edf_003.css
  web/drift_report_charts/chart_edf_003.js
layout size and panel arrangement
  1200x820 source-compare layout. Summary metrics are right-aligned in the top header with min width 430px. Empirical CDF comparison is left, cumulative squared CDF difference is right, notes/legend are bottom.
component list
  decision_card summary
  cumulative_curve for reference/current empirical CDFs with repeated CDF gap markers
  cumulative_curve for CvM cumulative contribution with area_under_line and contribution band
  domain_specific_visual notes_legend
data sources
  Original seeded samples are materialized into 62 CDF rows and 62 cumulative contribution rows.
  CvM raw area=0.01351, scaled statistic=1.8914, strongest CDF gap at x=0.0685 with reference CDF 0.5500 and current CDF 0.4357.
  Summary rows preserve original displays: CvM 통계량 1.89, 근사 p-value 0.018, 누적 면적 0.014.
viewBox per SVG
  CDF 535x450
  cumulative contribution 535x450
margin per SVG
  both top 22 right 26 bottom 52 left 58
x/y scale domain
  CDF x -3..3, y 0..1
  cumulative x -3..3, y 0..0.02
x/y ticks
  CDF x [-3,0,3], y [0,0.25,0.5,0.75,1]
  cumulative x [-3,0,3], y [0,0.005,0.010,0.015,0.020]
axis labels
  CDF 특성값 / 경험 CDF
  cumulative 특성값 / 누적 제곱 차이
series color and stroke width
  ref-line #246b9f stroke 3
  cur-line #c64e4e stroke 3
  gap-marker #d8a13a dashed
  cvm-area rgba(47,127,111,0.16), cvm-line #2f7f6f stroke 3
point visibility and point radius
  Both line charts suppress sampled points. CDF gap markers are vertical dashed markers without endpoint points.
vertical/horizontal markers
  CDF gap_markers at repeated mid-range x values where abs(CDF difference) is above the original threshold.
  Cumulative chart highlights the strongest contribution region with background_regions.
annotations and callouts
  CDF: 여러 구간의 작은 CDF 차이를 함께 누적
  cumulative: 기여 증가 구간
runtime change
  No new runtime behavior. Uses existing cumulative_curve line renderer support for secondary lines, gap_markers, area_under_line, background_regions, and annotations.
notes/interpretation handling
  Panel descriptions are original Korean Note popup links. Bottom notes_legend keeps original Korean title 해석 and body text.
known mismatch
  Follow-up fixed CDF and cumulative curves to use the original 220 sampling rows.
  Follow-up fixed CDF/cumulative tick labels with generic fixed1/fixed3 tick formatting.
```

## CHART-EDF-004 Progress Record

```text
chart_id
  CHART-EDF-004
original html/css/js path
  web/drift_report_charts/chart_edf_004.html
  web/drift_report_charts/chart_edf_004.css
  web/drift_report_charts/chart_edf_004.js
layout size and panel arrangement
  1200x820 source-compare layout. Summary metrics are right-aligned in the top header with min width 430px. ECDF positive/negative deviation chart is left, circular histogram is right, notes/legend are bottom.
component list
  decision_card summary
  cumulative_curve for current CDF - reference CDF with signed positive/negative area fills
  circular_histogram for reference/current polar histogram bins
  domain_specific_visual notes_legend
data sources
  Original seeded circular samples are materialized into 73 deviation rows and 18 polar histogram bins.
  Kuiper V=0.3769, D+=0.0115 at 322.5 degrees, D-=0.3654 at 49.5 degrees.
  Summary rows preserve original displays: Kuiper V 0.377, D+ / D- 0.012 / 0.365, 근사 p-value 0.009.
viewBox per SVG
  deviation 535x450
  circular histogram 535x450
margin per SVG
  deviation top 22 right 26 bottom 52 left 58
x/y scale domain
  deviation x 0..360, y -0.39..0.39
  circular histogram uses cx=268, cy=224, inner radius=70, max radius=176
x/y ticks
  deviation x [0,90,180,270,360], y [-0.39,-0.195,0,0.195,0.39]
axis labels
  deviation 각도 또는 순환 위치 / 현재 CDF - 기준 CDF
series color and stroke width
  dev-line #2c3642 stroke 2.5
  pos-area rgba(47,127,111,0.16), neg-area rgba(216,161,58,0.18)
  pos-marker #2f7f6f dashed, neg-marker #d8a13a dashed
  circular ref-bar rgba(36,107,159,0.48), cur-bar rgba(198,78,78,0.52)
point visibility and point radius
  Deviation line suppresses sampled points.
vertical/horizontal markers
  Deviation chart marks D+ at 322.5 degrees and D- at 49.5 degrees.
  Circular histogram uses 18 angle bins with reference/current radial bars.
annotations and callouts
  D+ 0.012, D- 0.365 labels.
  circular chart center label: 기준/현재 peak 각도 이동.
runtime change
  Line renderer supports generic signed_area_under_line with positive/negative classes and x_tick_suffix.
  Adds generic circular_histogram renderer for polar binned comparisons with configurable angle fields, value fields, radii, rings, labels, and annotations.
  Manager review fix: circular_histogram now supports generic per-series radius bases, inner radii, min thickness, and inverted radius wedges. EDF-004 uses secondary_radius_base_offset=0 with secondary_allow_inverted_radius=true so current red bins remain visible alongside reference blue bins.
notes/interpretation handling
  Panel descriptions are original Korean Note popup links. Bottom notes_legend keeps original Korean title 해석 and body text.
known mismatch
  Follow-up fixed deviation curve materialization to use the original 241 sampling rows.
  Follow-up fixed D+/D- markers to render zero-to-diff lines through generic gap_markers; circular histogram still uses generic polar label offsets for shift labels.
```

## CHART-ERR-001 Progress Record

```text
chart_id
  CHART-ERR-001
source files
  web/drift_report_charts/chart_err_001.html
  web/drift_report_charts/chart_err_001.css
  web/drift_report_charts/chart_err_001.js
layout mapping
  summary: x=7 y=0 w=5 h=1, matching original right-aligned 430px summary card group.
  main: x=0 y=1 w=7 h=2 for 오류율 추세.
  side_top: x=7 y=1 w=5 h=1 for 드리프트 기준 초과 여유.
  side_bottom: x=7 y=2 w=5 h=1 for 경고 버퍼 타임라인.
  notes: x=0 y=3 w=12 h=1.
data mapping
  Original 32 error-rate values are stored in chart.CHART-ERR-001.error with margin=error-0.36.
  Summary preserves final error 0.46, warning start t=22, drift alarm t=26.
  Timeline stores normal 1-22, warning 22-26, drift 26-32.
language preservation
  Panel descriptions and bottom notes preserve original Korean text. Generated panel descriptions are Note links/popups, not inline paragraphs.
runtime change
  state_timeline supports generic track_overlays and x_ticks for warning-buffer strips and timeline tick labels.
  No chart ID branch added.
style mapping
  Added reusable DDM-style classes for error-line, warning-line, drift-line, state-line, error/drift points, normal/warning/drift/buffer fills, and matching legend swatches.
known mismatch
  Generated panel descriptions are Note links by project rule, while original displays inline header paragraphs.
```

## CHART-HIST-001 Progress Record

```
source files read
  web/drift_report_charts/chart_hist_001.html
  web/drift_report_charts/chart_hist_001.css
  web/drift_report_charts/chart_hist_001.js
generated files
  web/chart_hist_001_generated.html
  builder_charts.json payload entry CHART-HIST-001
layout mapping
  Original 1200x820 chart shell maps to semantic_grid rows 76/250/250/146.
  Summary metrics stay at the original right-top area x=7 y=0 w=5 h=1.
  Main histogram spans left two rows; Intersection and distance trend panels stack on the right; notes span the bottom.
data mapping
  Original histogram bins, reference probabilities, current probabilities, intersection min(p,q), HINC trend, and summary metrics are stored in chart.CHART-HIST-001.* data sources.
  Original Korean panel descriptions and notes are preserved in payload text.
runtime/config boundary
  histogram_overlay now has generic overlap_value_field/intersection_value_field support for a third overlap bar series.
  histogram_overlay also accepts x_tick_labels and annotations for categorical bin labels and callouts.
style mapping
  Added reusable overlap-bar/swatch-overlap and distance-trend-line/distance-trend-point classes to shared generated and builder CSS.
known mismatch
  Generated panel descriptions are Note links by project rule, while original displays inline header paragraphs.
```

## CHART-ERR-002 Progress Record

```text
chart_id
  CHART-ERR-002
source files
  web/drift_report_charts/chart_err_002.html
  web/drift_report_charts/chart_err_002.css
  web/drift_report_charts/chart_err_002.js
layout mapping
  summary: x=7 y=0 w=5 h=1, matching original right-aligned 430px summary card group.
  main: x=0 y=1 w=7 h=2 for RDDM 오류율과 reset.
  side_top: x=7 y=1 w=5 h=1 for 보존 윈도 크기.
  side_bottom: x=7 y=2 w=5 h=1 for DDM과 RDDM 비교.
  notes: x=0 y=3 w=12 h=1.
data mapping
  Original 32 error-rate values and retained-window values are stored in chart.CHART-ERR-002.series.
  Summary preserves warning start t=20, reactive reset t=26, retained window 44.
  Comparison stores DDM and RDDM as multi-track timeline segments.
language preservation
  Panel descriptions and bottom notes preserve original Korean text. Generated panel descriptions are Note links/popups, not inline paragraphs.
runtime change
  state_timeline supports generic track_field/track_order multi-track segments for DDM/RDDM comparison timelines.
  No chart ID branch added.
style mapping
  Reuses DDM/RDDM classes for error-line, warning-line, drift-line, reset-line, window-line, normal/warning/drift/retained fills, and matching legend swatches.
known mismatch
  Generated panel descriptions are Note links by project rule, while original displays inline header paragraphs.
```

## CHART-ERR-003 Progress Record

```text
chart_id
  CHART-ERR-003
source files
  web/drift_report_charts/chart_err_003.html
  web/drift_report_charts/chart_err_003.css
  web/drift_report_charts/chart_err_003.js
layout mapping
  summary: x=7 y=0 w=5 h=1, matching original right-aligned 430px summary card group.
  main: x=0 y=1 w=7 h=2 for 오류 간격 점수 하락.
  side_top: x=7 y=1 w=5 h=1 for 상태 전환 구간.
  side_bottom: x=7 y=2 w=5 h=1 for 오류 이벤트 밀집.
  notes: x=0 y=3 w=12 h=1.
data mapping
  Original 32 EDDM distance-score values are stored in chart.CHART-ERR-003.score.
  Original 14 error event times are stored in chart.CHART-ERR-003.events.
  Summary preserves final score 0.44, warning t=11, drift t=19.
language preservation
  Panel descriptions and bottom notes preserve original Korean text. Generated panel descriptions are Note links/popups, not inline paragraphs.
runtime change
  Added generic event_raster/raster_view renderer for repeated event-marker strips with configurable row count, jitter, hot threshold, markers, ticks, and annotations.
  No chart ID branch added.
style mapping
  Added reusable distance-score line/point, event-marker, and matching legend swatch classes.
known mismatch
  Generated panel descriptions are Note links by project rule, while original displays inline header paragraphs.
```

## CHART-ERR-004 Progress Record

```text
chart_id
  CHART-ERR-004
source files
  web/drift_report_charts/chart_err_004.html
  web/drift_report_charts/chart_err_004.css
  web/drift_report_charts/chart_err_004.js
layout mapping
  summary: x=7 y=0 w=5 h=1, matching original right-aligned 430px summary card group.
  main: x=0 y=1 w=7 h=2 for ECDD Statistic Control Chart.
  side_top: x=7 y=1 w=5 h=1 for Error Rate Trend.
  side_bottom: x=7 y=2 w=5 h=1 for Warning / Drift State.
  notes: x=0 y=3 w=12 h=1.
data mapping
  Original 32 ECDD statistic values and weighted error-rate values are stored in chart.CHART-ERR-004.series.
  Summary preserves final statistic 1.28, warning t=22, drift t=26.
  Timeline stores normal 1-22, warning 22-26, drift 26-32.
language preservation
  Panel descriptions and bottom notes preserve original Korean text. Generated panel descriptions are Note links/popups, not inline paragraphs.
runtime change
  trend_line/control_chart vertical_markers now support generic opacity, used for the warning state line.
  No chart ID branch added.
style mapping
  Added reusable weighted-error line/point and legend swatch classes so ERR-004 can keep the original green error-rate series without changing existing error-line semantics.
known mismatch
  Generated panel descriptions are Note links by project rule, while original displays inline header paragraphs.
```

## CHART-ERR-005 Progress Record

```text
chart_id
  CHART-ERR-005
source files
  web/drift_report_charts/chart_err_005.html
  web/drift_report_charts/chart_err_005.css
  web/drift_report_charts/chart_err_005.js
layout mapping
  summary: x=7 y=0 w=5 h=1, matching original right-aligned 430px summary card group.
  main: x=0 y=1 w=7 h=2 for Hoeffding Bound Chart.
  side_top: x=7 y=1 w=5 h=1 for Error / Weighted Error Trend.
  side_bottom: x=7 y=2 w=5 h=1 for Warning / Drift Markers.
  notes: x=0 y=3 w=12 h=1.
data mapping
  Original 32 mean-difference values and error-trend values are stored in chart.CHART-ERR-005.series.
  Summary preserves final diff 0.50, warning t=22, drift t=26.
  Timeline stores normal 1-22, warning 22-26, drift 26-32, plus the two-sided guard band as a configured track overlay.
language preservation
  Panel descriptions and bottom notes preserve original Korean text. Generated panel descriptions are Note links/popups, not inline paragraphs.
runtime change
  trend_line/control_chart horizontal_markers now support generic opacity and x_axis_y for zero-axis placement.
  No chart ID branch added.
style mapping
  Added reusable mean-diff line/point, error-trend swatch, and two-sided-fill classes.
known mismatch
  Generated panel descriptions are Note links by project rule, while original displays inline header paragraphs.
```

## CHART-ERR-006 Progress Record

```text
chart_id
  CHART-ERR-006
source files
  web/drift_report_charts/chart_err_006.html
  web/drift_report_charts/chart_err_006.css
  web/drift_report_charts/chart_err_006.js
layout mapping
  summary: x=7 y=0 w=5 h=1, matching original right-aligned 430px summary card group.
  main: x=0 y=1 w=7 h=2 for Recent vs Overall Accuracy.
  side_top: x=7 y=1 w=5 h=1 for STEPD Threshold Chart.
  side_bottom: x=7 y=2 w=5 h=1 for State Timeline.
  notes: x=0 y=3 w=12 h=1.
data mapping
  Original 30 recent accuracy and overall accuracy values are stored in chart.CHART-ERR-006.series.
  Gap values are stored in the same rows as overall - recent accuracy.
  Summary preserves recent acc 0.68, overall acc 0.78, drift t=20.
  Timeline stores normal 1-15, warning 15-20, drift 20-30.
language preservation
  Panel descriptions and bottom notes preserve original Korean text. Generated panel descriptions are Note links/popups, not inline paragraphs.
runtime change
  No runtime behavior added. Existing secondary line, marker, point_highlights, and state_timeline options cover the chart.
  No chart ID branch added.
style mapping
  Added reusable recent/overall accuracy line, point, and legend swatch classes.
manager follow-up
  Removed unintended SVG default path fill from the reusable gap-line class by setting fill:none in generated and builder CSS.
  CHART-ERR-006 side_top payload keeps only line, warning/drift horizontal markers, and point_highlights; no area/fill config is used.
  Follow-up visual check found the side_top gap series should be a blue solid line like the original; payload now reuses the generic distance-line/distance-point classes while keeping warning/drift marker points.
known mismatch
  Generated panel descriptions are Note links by project rule, while original displays inline header paragraphs.
```

## CHART-EXPL-001 Progress Record

```text
chart_id
  CHART-EXPL-001
source files
  web/drift_report_charts/chart_expl_001.html
  web/drift_report_charts/chart_expl_001.css
  web/drift_report_charts/chart_expl_001.js
layout mapping
  summary: x=7 y=0 w=5 h=1, matching original right-aligned 430px summary card group.
  main: x=0 y=1 w=7 h=2 for SHAP Summary Comparison.
  side_top: x=7 y=1 w=5 h=1 for SHAP Value Distribution.
  side_bottom: x=7 y=2 w=5 h=1 for Class-wise SHAP Heatmap.
  notes: x=0 y=3 w=12 h=1.
data mapping
  Original feature importance rows are stored in chart.CHART-EXPL-001.features.
  Original risk_score SHAP density arrays are stored in chart.CHART-EXPL-001.distribution.
  Original class x feature heat values are stored in chart.CHART-EXPL-001.heatmap.
  Summary preserves top shift risk_score, rank change +3, and class heat 0.48.
language preservation
  Panel descriptions and bottom notes preserve original Korean text. Generated panel descriptions are Note links/popups, not inline paragraphs.
runtime change
  Added generic bar_style=horizontal_grouped with config-driven rank_connectors.
  Added generic heatmap_grid x/y label and conditional cell value label options.
  No chart ID branch added.
style mapping
  Added reusable baseline/current bar, rank-line, red current area, shift, and heat swatch classes.
known mismatch
  Generated panel descriptions are Note links by project rule, while original displays inline header paragraphs.
```

## CHART-EXPL-002 Progress Record

```text
chart_id
  CHART-EXPL-002
source files
  web/drift_report_charts/chart_expl_002.html
  web/drift_report_charts/chart_expl_002.css
  web/drift_report_charts/chart_expl_002.js
layout mapping
  summary: x=7 y=0 w=5 h=1, matching original right-aligned 430px summary card group.
  main: x=0 y=1 w=7 h=2 for Feature Importance + Time Split Count.
  side_top: x=7 y=1 w=5 h=1 for Split Path Diagram.
  side_bottom: x=7 y=2 w=5 h=1 for Segment Distribution.
  notes: x=0 y=3 w=12 h=1.
data mapping
  Original feature importance and time split count arrays are stored in chart.CHART-EXPL-002.features.
  Original split path nodes are stored in chart.CHART-EXPL-002.path; link relationships remain config-driven.
  Original segment baseline/current ratios are stored in chart.CHART-EXPL-002.segments.
  Summary preserves top feature query_age, time splits 18, and current leaf 82%.
language preservation
  Panel descriptions and bottom notes preserve original Korean text. Generated panel descriptions are Note links/popups, not inline paragraphs.
runtime change
  Added generic node_link_diagram for config/data-driven node-link path diagrams.
  Added generic horizontal_stacked bars for segment composition.
  Extended horizontal_grouped bars with series_x_maxes and optional series value labels.
  No chart ID branch added.
style mapping
  Added reusable importance/time bars, node/current-node, path-line, and importance/time swatch classes.
known mismatch
  Generated panel descriptions are Note links by project rule, while original displays inline header paragraphs.
```

## CHART-GEN-001 Progress Record

```text
chart_id
  CHART-GEN-001
source files
  web/drift_report_charts/chart_gen_001.html
  web/drift_report_charts/chart_gen_001.css
  web/drift_report_charts/chart_gen_001.js
layout mapping
  summary: x=7 y=0 w=5 h=1, matching original right-aligned 430px summary card group.
  main: x=0 y=1 w=7 h=2 for Metric Trend with Threshold.
  side_top: x=7 y=1 w=5 h=1 for Reference / Current Distribution.
  side_bottom: x=7 y=2 w=5 h=1 for Alarm Evidence Summary.
  notes: x=0 y=3 w=12 h=1.
data mapping
  Original 22-point generic metric series is stored in chart.CHART-GEN-001.metric.
  Original reference/current density arrays are stored in chart.CHART-GEN-001.distribution.
  Original evidence summary rows are stored in chart.CHART-GEN-001.evidence in source order.
  Summary preserves metric 0.68, threshold 0.45, and alarm t=15.
language preservation
  Panel descriptions and bottom notes preserve original Korean text. Generated panel descriptions are Note links/popups, not inline paragraphs.
runtime change
  Reused trend_line, density_area, and horizontal_ranked bar renderers.
  Added generic preserve_order to horizontal_ranked bars so source-order evidence rows are not value-sorted.
  No chart ID branch added.
style mapping
  Added reusable generic metric line/point, reference/current area, evidence bar, and metric swatch classes.
known mismatch
  Generated panel descriptions are Note links by project rule, while original displays inline header paragraphs.
```

## CHART-MEAN-001 Progress Record

```text
chart_id
  CHART-MEAN-001
source files
  web/drift_report_charts/chart_mean_001.html
  web/drift_report_charts/chart_mean_001.css
  web/drift_report_charts/chart_mean_001.js
layout mapping
  summary: x=7 y=0 w=5 h=1, matching original right-aligned 430px summary card group.
  main: x=0 y=1 w=7 h=2 for distribution and mean-position violin/box summaries.
  side_top: x=7 y=1 w=5 h=1 for mean 95% confidence intervals.
  side_bottom: x=7 y=2 w=5 h=1 for p-value/effect-size threshold bars.
  notes: x=0 y=3 w=12 h=1.
data mapping
  Original reference/current means, confidence intervals, quartiles, whiskers, and density arrays are stored in chart.CHART-MEAN-001.distribution and .ci.
  Original p-value, Cohen's d, alpha, and effect threshold are stored in chart.CHART-MEAN-001.effect with normalized bar scores.
  Summary preserves mean difference +6.6, p-value 0.004, and Cohen's d 0.72.
language preservation
  Original Korean panel descriptions and bottom notes are preserved in payload text. Generated panel descriptions are Note links/popups, not inline paragraphs.
runtime change
  Added generic distribution_style=violin_summary for config/data-driven violin, box, median, and mean summary plots.
  Added generic bar_style=horizontal_intervals for multiple confidence intervals.
  Extended horizontal_threshold bars with row-specific threshold_field and value_label_field support.
  No chart ID branch added.
style mapping
  Added reusable reference/current violin fill, summary box, solid mean line, median line, CI line, mean point, effect/p-value bar, and mean swatch classes.
known mismatch
  Generated panel descriptions are Note links by project rule, while original displays inline header paragraphs.
```

## CHART-MV-001 Progress Record

```text
chart_id
  CHART-MV-001
source files
  web/drift_report_charts/chart_mv_001.html
  web/drift_report_charts/chart_mv_001.css
  web/drift_report_charts/chart_mv_001.js
layout/data mapping
  Summary remains right-top x=7 y=0 w=5 h=1.
  Main projection scatter uses original 20 reference and 20 current points plus config-driven ellipses and center-gap line.
  Side panels store original energy-distance trend and permutation null bins, observed statistic, and p-value.
runtime boundary
  Added generic projection_scatter ellipses support.
  Extended histogram_overlay with row class fields and vertical marker labels for observed-statistic overlays.
  No chart ID branch added.
known mismatch
  Generated panel descriptions are Note links by project rule, while original displays inline header paragraphs.
```

## CHART-MV-002 Progress Record

```text
chart_id
  CHART-MV-002
source files
  web/drift_report_charts/chart_mv_002.html
  web/drift_report_charts/chart_mv_002.css
  web/drift_report_charts/chart_mv_002.js
layout/data mapping
  Summary remains right-top x=7 y=0 w=5 h=1.
  Main embedding projection scatter uses original 20 reference and 20 current points plus config-driven kernel ellipses and center-gap line.
  Side panels store original MMD score trend, threshold 0.18, permutation null bins, observed MMD 0.36, and p-value 0.008.
runtime boundary
  Reused common projection_scatter, distance_metric_view, histogram_overlay, and notes_legend components.
  Fixed generic notes_legend precedence so decision_card summary rendering does not consume notes rows.
  Standalone generated pages are now emitted by the generator for every designed payload.
  No chart ID branch added.
style mapping
  Added reusable kernel ellipse and MMD line/point/swatch classes.
known mismatch
  Generated panel descriptions are Note links by project rule, while original displays inline header paragraphs.
```

## CHART-MV-003 Progress Record

```text
chart_id
  CHART-MV-003
source files
  web/drift_report_charts/chart_mv_003.html
  web/drift_report_charts/chart_mv_003.css
  web/drift_report_charts/chart_mv_003.js
layout/data mapping
  Summary remains right-top x=7 y=0 w=5 h=1.
  Main density-difference heatmap stores original 5x6 diffGrid values using matrix_style=heatmap_grid.
  Side panels store original LSDD score trend, threshold 0.17, permutation null bins, observed value 0.34, and p-value 0.010.
runtime boundary
  Extended generic heatmap_grid with config-driven ellipses for contour overlays.
  Reused distance_metric_view, histogram_overlay, and notes_legend components.
  No chart ID branch added.
style mapping
  Added reusable increase/decrease swatches, contour ellipse classes, and LSDD line/point classes.
known mismatch
  Generated panel descriptions are Note links by project rule, while original displays inline header paragraphs.
```

## CHART-MV-004 Progress Record

```text
chart_id
  CHART-MV-004
source files
  web/drift_report_charts/chart_mv_004.html
  web/drift_report_charts/chart_mv_004.css
  web/drift_report_charts/chart_mv_004.js
layout/data mapping
  Summary remains right-top x=7 y=0 w=5 h=1.
  Main PCA scatter stores original reference/current points plus mean_ref/mean_cur marker rows and a config-driven mean shift line.
  Side panels store original Hotelling T2 trend, UCL 14.0, alert points, and contribution bars.
runtime boundary
  Reused projection_scatter group class/radius maps for mean markers instead of chart-specific drawing.
  Reused control_chart line renderer and horizontal_ranked contribution bars.
  No chart ID branch added.
style mapping
  Added reusable mean shift, T2 line/point, alert point, top contribution bar, and T2 swatch classes.
known mismatch
  Generated panel descriptions are Note links by project rule, while original displays inline header paragraphs.
```

## CHART-MV-005 Progress Record

```text
chart_id
  CHART-MV-005
source files
  web/drift_report_charts/chart_mv_005.html
  web/drift_report_charts/chart_mv_005.css
  web/drift_report_charts/chart_mv_005.js
layout/data mapping
  Summary remains right-top x=7 y=0 w=5 h=1.
  Main PCA scatter stores original Mahalanobis-distance points with data-driven radius and low/high threshold classes.
  Side panels store original mean distance trend, threshold 4.5, distance histogram bins, exceed rate 22%, and maximum distance 6.9.
runtime boundary
  Reused projection_scatter row radius support, distance_metric_view, histogram_overlay, and notes_legend components.
  No chart ID branch added.
style mapping
  Added reusable normal ellipse, distance point, distance tail histogram bar, and distance swatch classes.
known mismatch
  Generated panel descriptions are Note links by project rule, while original displays inline header paragraphs.
```

## CHART-PROB-001 Progress Record

```text
chart_id
  CHART-PROB-001
source files
  web/drift_report_charts/chart_prob_001.html
  web/drift_report_charts/chart_prob_001.css
  web/drift_report_charts/chart_prob_001.js
layout/data mapping
  Summary remains right-top x=7 y=0 w=5 h=1.
  Main probability overlay stores original reference/current bin probabilities and positive KL contribution gap lines.
  Side panels store original KL trend, threshold 0.070, top contribution bins, reverse KL, and top bin 1.2.
runtime boundary
  Extended generic vertical_grouped bars with label_every, gap_lines, and positive_only gap filtering.
  Fixed generic vertical_grouped y-axis scaling so small probability y_max values are respected.
  Reused distance_metric_view, horizontal_ranked bars, and notes_legend components.
  No chart ID branch added.
style mapping
  Added reusable divergence swatch, contribution gap line, and highlighted contribution bar classes.
known mismatch
  Generated panel descriptions are Note links by project rule, while original displays inline header paragraphs.
```

## CHART-PROB-002 Progress Record

```text
chart_id
  CHART-PROB-002
source files
  web/drift_report_charts/chart_prob_002.html
  web/drift_report_charts/chart_prob_002.css
  web/drift_report_charts/chart_prob_002.js
layout/data mapping
  Summary remains right-top x=7 y=0 w=5 h=1.
  Main probability overlay stores original category reference/current probabilities for 검색, 상세, 장바구니, 구매, 환불, 문의, 리뷰.
  Side panels store original JS/Hellinger bounded-distance trend and category delta rows.
  Summary preserves JS Distance 0.121, Hellinger 0.101, and 최대 Delta 구매 +0.07.
runtime boundary
  Added generic bar_style=horizontal_diverging for signed category deltas.
  Reused vertical_grouped bars, distance_metric_view secondary line, and notes_legend.
  Follow-up visual audit reused generic vertical_grouped overlay_bars with render_order=before_bars to draw the source overlap band behind each category pair.
  No chart ID branch added.
style mapping
  Added reusable Hellinger line/point and positive/negative delta classes.
known mismatch
  Follow-up fixed the main overlap band using generic overlay_bars.
  Generated panel descriptions are Note links by project rule, while original displays inline header paragraphs.
```

## CHART-PROB-003 Progress Record

```text
chart_id
  CHART-PROB-003
source files
  web/drift_report_charts/chart_prob_003.html
  web/drift_report_charts/chart_prob_003.css
  web/drift_report_charts/chart_prob_003.js
layout/data mapping
  Summary remains right-top x=7 y=0 w=5 h=1.
  Main probability overlay stores original bin reference/current/overlap probabilities for <-2 through >2.5.
  Side panels store overlap/missing stacked breakdown, Bhattacharyya coefficient text, max-difference bin, and Bhattacharyya distance trend.
  Summary preserves Bhattacharyya distance 0.023, overlap coefficient 0.820, and BC coefficient 0.977.
runtime boundary
  Reused vertical_grouped bars, horizontal_stacked bars, distance_metric_view, and notes_legend.
  Follow-up visual audit added generic vertical_grouped overlay_bars so the overlap rectangle can be centered over grouped bars without chart-specific runtime code.
  Follow-up visual audit extended generic horizontal_stacked with background bars, segment-end labels, hidden category labels, and coordinate annotations for source-style overlap progress panels.
  No chart ID branch added.
style mapping
  Added reusable overlap fill/missing fill classes.
known mismatch
  Follow-up fixed the main overlap rectangle using generic overlay_bars.
  Follow-up fixed the side overlap progress panel using generic horizontal_stacked options.
  Generated panel descriptions are Note links by project rule, while original displays inline header paragraphs.
```

## CHART-PSI-001 Progress Record

```text
chart_id
  CHART-PSI-001
source files
  web/drift_report_charts/chart_psi_001.html
  web/drift_report_charts/chart_psi_001.css
  web/drift_report_charts/chart_psi_001.js
layout/data mapping
  Summary remains right-top x=7 y=0 w=5 h=1.
  Main bin comparison stores original reference/current score-band ratios and delta labels.
  Side panels store sorted PSI contribution rows and PSI trend with threshold 0.10.
  Summary preserves PSI 0.123, top contribution bin 80-100, and 주요 이동 증가 8.0pp.
runtime boundary
  Reused vertical_grouped bars with category_highlights, horizontal_ranked contribution bars, distance_metric_view threshold line, and notes_legend.
  No chart ID branch added.
style mapping
  Added reusable top-contribution and highlight-band classes.
known mismatch
  Generated panel descriptions are Note links by project rule, while original displays inline header paragraphs.
```

## CHART-RANK-001 Progress Record

```text
chart_id
  CHART-RANK-001
source files
  web/drift_report_charts/chart_rank_001.html
  web/drift_report_charts/chart_rank_001.css
  web/drift_report_charts/chart_rank_001.js
layout/data mapping
  Source two-column layout is mapped to summary x=7 y=0 w=5 h=1, main x=0 y=1 w=6 h=1, side_top x=6 y=1 w=6 h=1, notes x=0 y=2 w=12 h=1.
  Distribution panel stores deterministic source-sample violin density summaries, quantiles, whiskers, and medians using the same mulberry32 seed semantics as the original JS.
  Rank panel stores original 12 combined-rank bins and a data-driven current-share balance line.
  Summary preserves Mann-Whitney U 31,551, rank AUC 0.652, and median difference 0.57.
runtime boundary
  Added generic vertical_grouped overlay_lines so categorical bar charts can draw payload-defined line overlays.
  Follow-up visual audit added generic vertical_grouped x_value_ticks for source rank ticks and generic violin_summary connectors for median-to-median source lines.
  Reused violin_summary distribution renderer, vertical_grouped bars, and notes_legend.
  No chart ID branch added.
style mapping
  Added reusable violin/box/whisker, rank bar, and rank-balance classes.
known mismatch
  Follow-up fixed combined-rank x ticks using generic x_value_ticks.
  Follow-up fixed the sloped median-difference connector using generic violin_summary connectors.
  Generated panel descriptions are Note links by project rule, while original displays inline header paragraphs.
```

## CHART-STREAM-004 Progress Record

```text
chart_id
  CHART-STREAM-004
source files
  web/drift_report_charts/chart_stream_004.html
  web/drift_report_charts/chart_stream_004.css
  web/drift_report_charts/chart_stream_004.js
layout/data mapping
  Summary remains right-top x=7 y=0 w=5 h=1.
  Main stream trend stores the original 36 values, reference mean 0.53, alarm t=27, delta callout, and original x/y ticks.
  Side evidence chart stores original evidence and bound arrays with alarm-highlighted late points.
  Side timeline stores monitor 1-22, warning 22-27, and drift 27-36 segments.
runtime boundary
  Reused trend_line, state_timeline, and notes_legend renderers.
  Follow-up visual audit added generic trend_line point_class_field/point_radius_field so evidence points after alarm render natively instead of as overlay duplicates.
  No chart ID branch added.
style mapping
  Added reusable evidence/bound line and evidence point classes plus source swatches.
known mismatch
  Generated panel descriptions are Note links by project rule, while original displays inline header paragraphs.
  Follow-up fixed evidence points after the alarm using generic trend_line row point classes.
```

## CHART-STREAM-005 Progress Record

```text
chart_id
  CHART-STREAM-005
source files
  web/drift_report_charts/chart_stream_005.html
  web/drift_report_charts/chart_stream_005.css
  web/drift_report_charts/chart_stream_005.js
layout/data mapping
  Summary remains right-top x=7 y=0 w=5 h=1.
  Main LLR chart stores original 32 LLR values, H1/H0 boundaries 10.8/-2.2, decision t=25, and original ticks.
  Side error-rate trend stores original 32 error-rate values with the 0.30 guide and t=25 marker.
  Side timeline stores continue 1-18, review 18-25, and accept H1 25-32 segments.
runtime boundary
  Reused trend_line, state_timeline, and notes_legend renderers.
  Follow-up visual audit added generic trend_line point_class_field/point_radius_field so decision-period points render natively instead of as overlay duplicates.
  No chart ID branch added.
style mapping
  Added reusable LLR, decision point, and upper/lower boundary classes.
known mismatch
  Generated panel descriptions are Note links by project rule, while original displays inline header paragraphs.
  Follow-up fixed decision-period points using generic trend_line row point classes.
```

## CHART-TEXT-001 Progress Record

```text
chart_id
  CHART-TEXT-001
source files
  web/drift_report_charts/chart_text_001.html
  web/drift_report_charts/chart_text_001.css
  web/drift_report_charts/chart_text_001.js
layout/data mapping
  Summary remains right-top x=7 y=0 w=5 h=1.
  Main projection stores the original deterministic 48 baseline and 48 current embedding points as data rows.
  Centroid shift is represented by a config-driven diagonal marker from (-0.85,-0.12) to (1.15,0.40).
  Side distance trend stores the original 32 cosine-distance values, threshold 0.36, alarm start t=22, and matching ticks.
  Side topic panel stores baseline/current topic proportions and overlays the original mini ROC curve.
runtime boundary
  Reused projection_scatter, trend_line, horizontal_stacked bars, cumulative_curve overlay, and notes_legend.
  Follow-up visual audit added generic projection_scatter point_highlights for source centroid alarm dots.
  No chart ID branch added.
style mapping
  Added reusable centroid and topic segment classes.
known mismatch
  Generated panel descriptions are Note links by project rule, while original displays inline header paragraphs.
  Follow-up fixed the current centroid alarm dot using generic projection_scatter point_highlights.
```

## CHART-TEXT-002 Progress Record

```text
chart_id
  CHART-TEXT-002
source files
  web/drift_report_charts/chart_text_002.html
  web/drift_report_charts/chart_text_002.css
  web/drift_report_charts/chart_text_002.js
layout/data mapping
  Summary remains right-top x=7 y=0 w=5 h=1.
  Main ROC stores the original eight ROC points, diagonal random baseline, AUC callout, and 0.00-1.00 ticks.
  Side score distribution stores original baseline/current classifier-score arrays.
  Side descriptor/projection panel stores original descriptor weights and deterministic embedding split points.
runtime boundary
  Reused cumulative_curve, density_area, feature_projection_view, and notes_legend.
  Follow-up visual audit added generic feature_projection_view point_coordinate_mode=pixel for source screen-coordinate embedding loops.
  No chart ID branch added.
style mapping
  Added reusable green domain ROC class and descriptor swatch.
known mismatch
  Generated panel descriptions are Note links by project rule, while original displays inline header paragraphs.
  Follow-up fixed the side embedding split with source screen-coordinate points and a chart-specific current-dot class to avoid shared CSS class conflicts.
```

## CHART-UNC-001 Progress Record

```text
chart_id
  CHART-UNC-001
source files
  web/drift_report_charts/chart_unc_001.html
  web/drift_report_charts/chart_unc_001.css
  web/drift_report_charts/chart_unc_001.js
layout/data mapping
  Summary remains right-top x=7 y=0 w=5 h=1.
  Main confidence distribution stores original 14 confidence bins with baseline/current counts and low-confidence marker at 0.50.
  Side uncertainty trend stores original 24 entropy values, threshold 0.55, and alarm t=15.
  Side calibration/class panel stores original calibration curve plus class A-D uncertainty bars.
runtime boundary
  Reused density_area, trend_line, cumulative_curve overlay, horizontal_threshold overlay, and notes_legend.
  Follow-up visual audit extended generic cumulative_curve/trend_line rendering with pixel_bars so the calibration curve and class uncertainty bars render inside one source-style SVG.
  No chart ID branch added.
style mapping
  Added reusable entropy, calibration, perfect-line, and class bar classes.
known mismatch
  Generated panel descriptions are Note links by project rule, while original displays inline header paragraphs.
  Follow-up fixed calibration/class bars as a single SVG using generic pixel_bars.
```

## CHART-VAR-001 Progress Record

```text
chart_id
  CHART-VAR-001
source files
  web/drift_report_charts/chart_var_001.html
  web/drift_report_charts/chart_var_001.css
  web/drift_report_charts/chart_var_001.js
layout/data mapping
  Summary remains right-top x=7 y=0 w=5 h=1.
  Main violin/box summary stores original reference/current variance, SD, center, quartiles, whiskers, absolute deviation, and density arrays.
  Side variance panel stores original 42.3 and 112.4 variance values with SD labels.
  Side deviation panel stores original absolute deviations 5.1/8.7, variance ratio 2.66x, p-value 0.012, and ratio threshold scaling.
runtime boundary
  Reused violin_summary distribution, vertical_grouped bars, horizontal_threshold bars, and notes_legend.
  No chart ID branch added.
style mapping
  Reused existing ref/current violin, center, median, ref/current bar, ratio, and deviation classes.
known mismatch
  Generated panel descriptions are Note links by project rule, while original displays inline header paragraphs.
  Follow-up verified the side deviation panel uses the same source scaling: variance ratio 2.66x is stored as 6.65 on the shared 0-10 axis and the 1.5x threshold is stored as 3.75.
```

## CHART-REP-001 Progress Record

```text
chart_id
  CHART-REP-001
source files
  web/drift_report_charts/chart_rep_001.html
  web/drift_report_charts/chart_rep_001.css
  web/drift_report_charts/chart_rep_001.js
layout/data mapping
  Summary remains right-top x=7 y=0 w=5 h=1.
  Main layerwise heatmap stores original 5 layer x 12 channel drift scores, block3 row outline, c1/c4/c8/c12 labels, and high-value labels.
  Side panels store original baseline/current activation bins and computed baseline/current embedding projection points.
runtime boundary
  Added generic heatmap_grid row_highlights for config-driven selected-row outlines.
  No chart ID branch added.
known mismatch
  Generated panel descriptions are Note links by project rule, while original displays inline header paragraphs.
```

## CHART-REP-002 Progress Record

```text
chart_id
  CHART-REP-002
source files
  web/drift_report_charts/chart_rep_002.html
  web/drift_report_charts/chart_rep_002.css
  web/drift_report_charts/chart_rep_002.js
layout/data mapping
  Summary remains right-top x=7 y=0 w=5 h=1.
  Main density_area stores original reconstruction-error bins, baseline/current densities, threshold 0.36, and source annotations.
  Side panels store original 32-point error trend and computed latent projection points.
runtime boundary
  Reused density_area, trend_line, and projection_scatter renderers.
  No chart ID branch added.
known mismatch
  Generated panel descriptions are Note links by project rule, while original displays inline header paragraphs.
```

## CHART-REP-003 Progress Record

```text
chart_id
  CHART-REP-003
source files
  web/drift_report_charts/chart_rep_003.html
  web/drift_report_charts/chart_rep_003.css
  web/drift_report_charts/chart_rep_003.js
layout/data mapping
  Summary remains right-top x=7 y=0 w=5 h=1.
  Main projection_scatter stores computed baseline/current/bridge graph embedding points.
  Side panels store original node drift heatmap and 24-point graph-level distance trend with threshold 0.40.
runtime boundary
  Reused projection_scatter, heatmap_grid, and distance_metric_view renderers.
  No chart ID branch added.
known mismatch
  Generated panel descriptions are Note links by project rule, while original displays inline header paragraphs.
```

## CHART-STREAM-001 Progress Record

```text
chart_id
  CHART-STREAM-001
source files
  web/drift_report_charts/chart_stream_001.html
  web/drift_report_charts/chart_stream_001.css
  web/drift_report_charts/chart_stream_001.js
layout/data mapping
  Summary remains right-top x=7 y=0 w=5 h=1.
  Main trend stores original stream metric and rolling mean values, ADWIN alarm marker at t=23, and source callouts.
  Side panels store original adaptive window width and before/after/delta mean bars.
runtime boundary
  Reused trend_line and vertical_threshold bar renderers.
  No chart ID branch added.
known mismatch
  Generated panel descriptions are Note links by project rule, while original displays inline header paragraphs.
```

## CHART-STREAM-002 Progress Record

```text
chart_id
  CHART-STREAM-002
source files
  web/drift_report_charts/chart_stream_002.html
  web/drift_report_charts/chart_stream_002.css
  web/drift_report_charts/chart_stream_002.js
layout/data mapping
  Summary remains right-top x=7 y=0 w=5 h=1.
  Main trend stores original stream values, reference/current window background regions, and KSWIN alarm marker at t=28.
  Side panels store original reference/current ECDF rows and KS statistic trend with threshold 0.36.
runtime boundary
  Added generic line_interpolation=step for config-driven ECDF step paths.
  No chart ID branch added.
known mismatch
  Generated panel descriptions are Note links by project rule, while original displays inline header paragraphs.
```

## CHART-STREAM-003 Progress Record

```text
chart_id
  CHART-STREAM-003
source files
  web/drift_report_charts/chart_stream_003.html
  web/drift_report_charts/chart_stream_003.css
  web/drift_report_charts/chart_stream_003.js
layout/data mapping
  Summary remains right-top x=7 y=0 w=5 h=1.
  Main trend stores original raw stream and running mean values with Page-Hinkley alarm marker at t=29.
  Side panels store original PH statistic trend, threshold 18.0, and normal/warning/drift state timeline.
runtime boundary
  Reused trend_line and state_timeline renderers.
  No chart ID branch added.
known mismatch
  Generated panel descriptions are Note links by project rule, while original displays inline header paragraphs.
```
