# Chart Runtime 개념 목록

이 문서는 `chart_runtime`에서 사용하는 핵심 용어를 정리한다. 새 용어를 도입할 때는 이 문서에 먼저 정의하고, 다른 문서에서는 같은 의미로 사용한다.

## Chart Runtime Engine

Chart Runtime Engine은 Chart Runtime Payload를 입력으로 받아 실제 chart DOM/SVG를 렌더링하는 공통 엔진이다.

현재 구현:

```text
chart_runtime/chart_runtime.js
chart_runtime/chart_runtime.css
```

주요 책임:

```text
layout area 생성
component instance 배치
componentType에 따른 renderer 선택
payload.data와 config를 사용한 SVG/HTML 생성
overlay, popup, zoom, overflow 처리
```

## Chart Runtime Payload

Chart Runtime Payload는 Chart Runtime Engine이 chart를 렌더링하기 위해 받는 실행용 데이터 구조다.

기본 구성:

```text
chartId
layout
components
data
```

의미:

```text
layout      chart 영역 구조
components  어떤 component를 어느 area에 배치할지
config      component별 렌더링 설정
dataBinding component가 어떤 data source와 field를 읽을지
data        실제 row 데이터
```

## Payload Contract

Payload Contract는 Chart Runtime Payload와 Chart Runtime Engine 사이의 약속이다.

예:

```text
components[].componentType은 runtime이 아는 componentType이어야 한다.
components[].area는 layout.areas[].area 중 하나여야 한다.
components[].dataBinding.source는 payload.data[source]와 연결되어야 한다.
renderer가 요구하는 field는 data row에 존재해야 한다.
```

이 계약이 깨지면 chart는 비어 보이거나, 일부 component가 fallback으로 렌더링되거나, SVG가 잘못 그려질 수 있다.

## Component Type

Component Type은 payload에서 component renderer를 선택하기 위한 stable key다.

예:

```text
trend_line
bar_chart
projection_scatter
state_timeline
threshold_line
event_marker
```

payload 예:

```json
{
  "componentType": "bar_chart"
}
```

runtime은 이 값을 보고 어떤 renderer를 사용할지 결정한다.

## Component Instance

Component Instance는 특정 chart 안에 배치된 component 하나를 뜻한다.

예:

```json
{
  "componentInstanceId": "CHART-001.main.bar.0",
  "componentType": "bar_chart",
  "area": "main",
  "config": {},
  "dataBinding": {}
}
```

같은 `componentType`도 chart 안에서 여러 번 배치될 수 있으므로, 각 instance는 `componentInstanceId`로 구분한다.

## Renderer

Renderer는 component instance를 실제 SVG/HTML markup으로 바꾸는 함수다.

예:

```text
renderLine
renderBar
renderScatter
renderTimeline
renderDistribution
renderCard
```

Renderer는 보통 다음을 입력으로 받는다.

```text
payload
component instance
```

그리고 다음을 수행한다.

```text
dataBinding.source로 rows 조회
config에서 field/style/domain/tick/marker 설정 읽기
SVG/HTML markup 생성
```

## Registry

Registry는 `componentType`과 renderer, field 계약을 모아둔 중앙 등록표다.

간단한 형태:

```js
const COMPONENT_RENDERERS = {
  trend_line: renderLine,
  performance_metric_view: renderLine,
  bar_chart: renderBar,
  ranking_view: renderBar,
  projection_scatter: renderScatter,
  state_timeline: renderTimeline,
  threshold_line: renderThreshold,
  event_marker: renderEvents
};
```

의미:

```text
payload에 componentType = "bar_chart"가 있으면 renderBar로 그린다.
payload에 componentType = "trend_line"이 있으면 renderLine으로 그린다.
```

확장된 형태:

```js
const COMPONENT_SPECS = {
  bar_chart: {
    renderer: renderBar,
    requiredData: true,
    fields: {
      category: ["category_field"],
      value: ["value_field"]
    },
    defaults: {
      category: "category",
      value: "value"
    }
  }
};
```

Registry가 필요한 이유:

```text
지원 componentType 목록을 한 곳에서 관리한다.
renderComponent()의 if 분기를 줄인다.
문서와 코드의 불일치를 줄인다.
payload validation에 사용할 수 있다.
나중에 renderer 파일을 분리하기 쉬워진다.
```

현재 상태:

```text
registry가 별도 파일로 분리되어 있지는 않다.
componentType -> renderer 연결은 chart_runtime.js의 renderComponent() 안에 하드코딩되어 있다.
구조화 첫 단계에서 이 mapping을 registry로 분리하는 것을 권장한다.
```

## Field Contract

Field Contract는 renderer가 data row에서 어떤 field를 읽는지에 대한 약속이다.

예:

```text
line 계열:
  x field = config.time_field 또는 config.x_field, 기본값 time
  y field = config.value_field 또는 config.y_field, 기본값 value

bar 계열:
  category field = config.category_field, 기본값 category 또는 label
  value field = config.value_field, 기본값 value
```

이 계약은 payload validation에 필요하다.

예:

```text
bar_chart의 config.value_field가 "score"이면
payload.data[source]의 각 row에는 score field가 있어야 한다.
```

## Data Binding

Data Binding은 component가 어떤 data source와 field를 읽을지 설명하는 payload 영역이다.

예:

```json
{
  "dataBinding": {
    "source": "chart.CHART-001.main",
    "category_field": "feature",
    "value_field": "score"
  }
}
```

`source`는 반드시 `payload.data`의 key와 연결된다.

```json
{
  "data": {
    "chart.CHART-001.main": [
      { "feature": "age", "score": 0.42 }
    ]
  }
}
```

## Config

Config는 renderer가 chart를 어떻게 그릴지 결정하는 component별 설정이다.

예:

```text
view_box
margin
x_min, x_max, y_min, y_max
x_ticks, y_ticks
x_field, y_field, value_field
line_class, bar_class
vertical_markers
annotations
```

원칙:

```text
chart별 tick, marker, annotation, label, style 차이는 runtime 코드가 아니라 config/data에 둔다.
```

## Layout Area

Layout Area는 chart 화면의 의미 구역이다.

예:

```text
summary
main
side_top
side_bottom
notes
legend
```

payload에서는 grid 좌표로 저장된다.

```json
{
  "area": "main",
  "role": "primary_visual",
  "x": 0,
  "y": 1,
  "w": 8,
  "h": 5
}
```

## Overlay Component

Overlay Component는 같은 area의 base component 위에 겹쳐 그리는 component다.

예:

```text
trend_line + threshold_line
trend_line + event_marker
line component + uncertainty_band
```

payload 예:

```json
{
  "componentType": "threshold_line",
  "area": "main",
  "isOverlay": true,
  "zIndex": 20
}
```

Overlay component는 같은 area의 base component와 좌표계를 공유해야 한다.

## Runtime Override

Runtime Override는 저장된 chart definition을 바꾸지 않고, 렌더링 직전에 일부 config나 theme 값을 덮어쓰는 방식이다.

허용 대상:

```text
component config 값
threshold
marker
domain
label
theme 값
```

금지 대상:

```text
layout
components
componentType
area
dataBinding
```

## Visual Smoke Test

Visual Smoke Test는 payload와 runtime renderer가 여러 data/config 변형에서도 깨지지 않는지 확인하는 브라우저 기반 시각 테스트다.

현재 파일:

```text
tests/component_visual_smoke.py
```

검사 대상:

```text
렌더링 예외
console error
NaN/undefined/Infinity
빈 캡처
SVG geometry 이상
overflow/scroll 문제
```

## Generated Chart

Generated Chart는 `chart_builder/builder_charts.json`의 payload를 기반으로 생성된 정적 chart page다.

흐름:

```text
chart_builder/builder_charts.json
  -> chart_builder/tools/generate_recreated_site.py
  -> chart_builder/web/recreated_chart_payloads.js
  -> chart_builder/web/chart_*_generated.html
  -> chart_runtime/chart_runtime.js
```

Generated Chart도 Chart Runtime Engine을 사용하므로, payload/runtime 계약을 반드시 지켜야 한다.
