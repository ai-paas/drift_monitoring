# Chart Runtime 구조화 제안

## 목적

이 문서는 현재 vanilla JavaScript 기반 `chart_runtime`을 유지하면서, 내부 구조를 어떻게 나눌지 제안한다.

이 문서에서 사용하는 핵심 용어는 [CONCEPTS.md](./CONCEPTS.md)에 정리한다. 특히 `registry`는 `componentType`과 renderer, field 계약을 모아둔 중앙 등록표를 뜻한다.

React/TypeScript 전환은 이번 문서의 범위가 아니다. 지금 목표는 다음 세 가지다.

```text
1. chart_runtime.js와 chart_runtime.css의 복잡도를 낮춘다.
2. payload/runtime 계약을 유지하기 쉽게 만든다.
3. 나중에 React/TypeScript runtime으로 전환하더라도 재사용 가능한 구조를 준비한다.
```

## 현재 상태

현재 runtime의 핵심 파일은 다음이다.

```text
chart_runtime.js
chart_runtime.css
tests/component_visual_smoke.py
```

`chart_runtime.js`는 현재 다음 책임을 모두 갖고 있다.

```text
public API
layout 렌더링
componentType 라우팅
data 조회 helper
SVG helper
모든 component renderer
note popup
zoom popup
zoom payload 생성
```

`chart_runtime.css`는 현재 다음 스타일을 모두 갖고 있다.

```text
runtime layout style
component stage/overlay style
chart visual class
viewer/application shell style
popup style
chart별로 재사용되는 visual class
```

이 구조는 prototype 단계에서는 동작하지만, Chart Builder, generated chart page, recreated chart viewer, drift metric analysis popup이 함께 쓰는 공통 엔진으로는 너무 조밀하다.

## 해결해야 할 문제

### 1. JS 파일 하나에 책임이 너무 많다

`chart_runtime.js`는 runtime orchestration과 모든 component renderer를 동시에 담당한다.

위험:

```text
작은 renderer 수정이 layout, popup, data binding, 다른 renderer에 영향을 줄 수 있다.
```

### 2. renderer mapping이 데이터로 중앙화되어 있지 않다

현재 `componentType -> renderer` 연결은 `renderComponent()` 안에 하드코딩되어 있다.

위험:

```text
문서, validation, runtime routing이 서로 어긋날 수 있다.
```

### 3. field 계약이 renderer 함수 안에 숨어 있다

`x_field`, `value_field`, `category_field`, fallback field 이름 같은 규칙이 각 renderer 내부에 들어 있다.

위험:

```text
Builder와 drift server가 렌더링 전에 payload를 안정적으로 검증하기 어렵다.
```

### 4. CSS에 runtime core와 application shell이 섞여 있다

현재 runtime CSS에는 sidebar, workspace, list, viewer popup 같은 화면 shell style도 포함되어 있다.

위험:

```text
chart 렌더링만 필요한 application이 불필요한 viewer layout style까지 상속받는다.
```

### 5. chart visual class 관리가 어려워지고 있다

line, bar, swatch, state, marker, chart별 변형 class가 많다.

위험:

```text
class 중복과 CSS override 순서를 추적하기 어려워진다.
```

## 구조화 목표

구조화 작업은 다음을 만족해야 한다.

```text
현재 browser script 사용 방식을 유지한다.
window.ChartRuntime public API를 유지한다.
기존 payload를 계속 렌더링할 수 있어야 한다.
chartId별 runtime 분기를 만들지 않는다.
runtime orchestration과 renderer 구현을 분리한다.
componentType mapping을 명시적인 registry로 만든다.
field 계약을 validation에 활용할 수 있게 한다.
CSS를 책임별로 나눈다.
점진적 migration이 가능해야 한다.
```

구조화 작업에서 하지 않을 것:

```text
지금 바로 React로 rewrite하지 않는다.
generated chart payload 형식을 바꾸지 않는다.
drift_metric_timeseries의 analysis payload 형식을 바꾸지 않는다.
첫 단계부터 무거운 build system을 도입하지 않는다.
ChartRuntime.renderChartPayload public contract를 바꾸지 않는다.
```

## 제안 디렉터리 구조

최종적으로는 다음 구조를 목표로 한다.

```text
chart_runtime/
  chart_runtime.js
  chart_runtime.css

  src/
    index.js
    runtime/
      renderChartPayload.js
      layout.js
      dataBinding.js
      registry.js
      svg.js
      popup.js
      zoom.js
    renderers/
      line.js
      bar.js
      matrix.js
      scatter.js
      distribution.js
      timeline.js
      card.js
      table.js
      overlay.js
    styles/
      runtime-core.css
      chart-visuals.css
      popup.css
      viewer-shell.css
    specs/
      componentRegistry.js
      fieldContracts.js

  tests/
    component_visual_smoke.py
```

초기에는 `chart_runtime.js`와 `chart_runtime.css`를 계속 browser-facing artifact로 유지한다. `src/`는 점진적으로 소스 모듈을 분리하는 위치로 사용한다. build step은 나중에 필요할 때 도입한다.

## 모듈별 책임

### `src/index.js`

public API entrypoint.

역할:

```text
ChartRuntime export
window.ChartRuntime 연결
renderChartPayload(target, payload) 계약 유지
```

### `src/runtime/renderChartPayload.js`

최상위 렌더링 orchestration.

역할:

```text
target element 확인
chart root에 payload 저장
layout renderer 호출
popup binding
렌더링 후 SVG sizing normalize
```

### `src/runtime/layout.js`

semantic grid와 area 렌더링.

역할:

```text
layout.areas 렌더링
base component와 overlay component를 area에 배치
area title/description/headerHeight/stageInset/className 적용
component wrapper DOM 생성
```

### `src/runtime/registry.js`

renderer lookup.

역할:

```text
componentType을 renderer 함수에 연결
지원 componentType 목록 제공
fallback 동작 명시
```

예:

```js
const COMPONENT_RENDERERS = {
  trend_line: renderLine,
  performance_metric_view: renderLine,
  bar_chart: renderBar,
  projection_scatter: renderScatter,
  state_timeline: renderTimeline
};
```

### `src/runtime/dataBinding.js`

data 조회와 field resolve helper.

역할:

```text
dataFor(payload, instance)
rowsForSource(payload, source)
resolveField(config, binding, candidates, fallback)
source 존재 여부 validation
```

### `src/runtime/svg.js`

공통 SVG utility.

역할:

```text
svg()
viewBoxFor()
marginFor()
extent()
ticksFor()
path()
stepPath()
formatNumber()
normalizeSvgSizing()
```

### `src/runtime/popup.js`

note popup 처리.

역할:

```text
note popup click binding
note popup 표시
note popup 닫기
application별 popup 동작과 분리
```

### `src/runtime/zoom.js`

component zoom 처리.

역할:

```text
buildZoomPayload()
showComponentZoomPopup()
closeComponentZoomPopup()
```

### `src/renderers/*`

component renderer family.

역할:

```text
한 renderer family를 담당한다.
shared helper를 통해 config/data를 읽는다.
SVG/HTML markup을 반환한다.
직접 DOM mutation을 하지 않는다.
chartId별 분기를 만들지 않는다.
```

초기 분리 후보:

```text
line.js          renderLine
bar.js           renderBar
matrix.js        renderMatrix
scatter.js       renderScatter, renderFeatureProjection
distribution.js  renderDistribution
timeline.js      renderTimeline
card.js          renderCard
table.js         renderTable
overlay.js       renderThreshold, renderEvents, renderBand
network.js       renderNodeLink, renderForest
special.js       renderCircularHistogram, renderEventRaster, renderSmallMultipleLines
```

## Component Registry와 Field Contract

runtime은 renderer mapping과 field expectation을 명시적인 데이터로 가져야 한다.

제안 registry 형태:

```js
const COMPONENT_SPECS = {
  trend_line: {
    renderer: "line",
    requiredData: true,
    fields: {
      x: ["time_field", "x_field"],
      y: ["value_field", "y_field", "statistic_field"],
      secondaryY: ["secondary_value_field"]
    },
    defaults: {
      x: "time",
      y: "value"
    }
  },
  bar_chart: {
    renderer: "bar",
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

활용:

```text
renderComponent가 registry lookup으로 renderer를 찾는다.
Builder가 지원 component type 목록을 가져올 수 있다.
payload validator가 누락 data field를 찾을 수 있다.
문서와 registry의 불일치를 줄일 수 있다.
```

## CSS 구조화

현재 `chart_runtime.css`는 책임별로 나눌 필요가 있다.

제안 파일:

```text
styles/runtime-core.css
styles/chart-visuals.css
styles/popup.css
styles/viewer-shell.css
```

### `runtime-core.css`

chart rendering layout의 핵심 스타일만 둔다.

```text
.component-chart
.chart-container
.chart-area
.area-body
.component-stage
.component-overlay
.runtime-component
.chart-svg
```

### `chart-visuals.css`

재사용 가능한 chart drawing class를 둔다.

```text
axis/grid
line class
bar class
point class
state class
swatch class
label
marker
```

### `popup.css`

runtime이 직접 소유하는 popup style을 둔다.

```text
note popup
component zoom popup
popup button
popup chart surface
```

### `viewer-shell.css`

recreated chart viewer나 demo page에 속하는 화면 shell style을 둔다.

```text
.site
.sidebar
.workspace
.chart-list
.chart-button
.issues
.original-popup
```

viewer shell style은 장기적으로 runtime core CSS가 아니라 해당 application 쪽으로 이동하는 것이 맞다.

## Migration Plan

### Phase 1. 계약 문서화와 고정

현재 상태:

```text
RUNTIME_CONTRACT.md 존재
PAYLOAD_RUNTIME_COMPATIBILITY.md 존재
```

다음 작업:

```text
componentType mapping 문서와 코드 일치 유지
새 renderer 동작 추가 시 compatibility 문서 갱신
```

### Phase 2. Registry 추출

생성:

```text
src/runtime/registry.js
src/specs/componentRegistry.js
```

변경:

```text
renderComponent()가 registry lookup을 사용한다.
fallback renderer는 renderCard로 유지한다.
기존 componentType 동작은 바꾸지 않는다.
```

검증:

```powershell
node --check chart_runtime\chart_runtime.js
python chart_runtime\tests\component_visual_smoke.py
```

### Phase 3. 순수 utility 추출

먼저 다음 helper를 분리한다.

```text
escapeHtml
formatNumber
formatByMode
hasFiniteValue
extent
viewBoxFor
marginFor
ticksFor
path
stepPath
svg
normalizeSvgSizing
```

이유:

```text
결합도가 낮고 검증하기 쉽다.
```

### Phase 4. Renderer family 분리

renderer 함수는 family 단위로 하나씩 이동한다.

권장 순서:

```text
1. renderThreshold/renderEvents/renderBand
2. renderTable/renderCard
3. renderTimeline
4. renderScatter/renderFeatureProjection
5. renderMatrix
6. renderDistribution
7. renderLine
8. renderBar
```

이유:

```text
작거나 독립적인 renderer부터 옮긴다.
renderBar와 renderLine은 config/style 변형이 많기 때문에 뒤로 둔다.
```

### Phase 5. CSS 분리

JS renderer 동작이 안정된 뒤 CSS를 분리한다.

이유:

```text
CSS 분리는 JavaScript가 같아도 visual regression을 만들 수 있다.
```

검증:

```text
component visual smoke screenshot 전후 비교
generated chart viewer 확인
drift metric analysis popup 확인
```

### Phase 6. 선택적 build step 도입

source file이 충분히 분리된 뒤에만 도입한다.

```text
작은 bundler 또는 concatenate script 도입
최종 산출물 이름은 유지:
  chart_runtime.js
  chart_runtime.css
```

이렇게 하면 application들은 기존 runtime 파일을 그대로 로드할 수 있다.

## Refactor 중 지켜야 할 호환성 규칙

바꾸면 안 되는 것:

```text
window.ChartRuntime
ChartRuntime.renderChartPayload(target, payload)
payload shape
componentType 이름
dataBinding.source 동작
기존 payload config가 참조하는 CSS class
generated chart URL
```

도입하면 안 되는 것:

```text
chartId별 runtime branch
Builder 전용 state에 의존하는 renderer 동작
payload.layout 또는 payload.components의 암묵적 mutation
```

허용되는 것:

```text
내부 파일 분리
registry lookup
shared helper 추출
validation helper 추가
최종 bundled CSS class 동작을 유지하는 CSS 파일 분리
```

## 검증 체크리스트

각 phase 이후 최소 검증:

```powershell
node --check chart_runtime\chart_runtime.js
python -m py_compile chart_runtime\tests\component_visual_smoke.py
python chart_runtime\tests\component_visual_smoke.py
```

generated chart wrapper나 viewer code가 바뀐 경우:

```powershell
python chart_builder\tools\generate_recreated_site.py
node --check chart_builder\web\recreated_charts.js
```

drift metric analysis popup에 영향이 있는 경우:

```powershell
node --check drift_metric_timeseries\web\drift_metric_timeseries_demo.js
```

수동 확인:

```text
recreated chart viewer 열기
generated chart page 하나 이상 열기
drift metric analysis popup 열기
component zoom popup 확인
note popup 확인
dense-data와 compact-config smoke capture 확인
```

## 첫 번째 Refactor 추천

첫 구현 작업은 작게 시작한다.

```text
renderComponent()에서 component registry를 분리한다.
renderer 함수들은 아직 chart_runtime.js 안에 둔다.
renderComponent()만 registry lookup으로 바꾼다.
문서화된 componentType이 모두 mapping되어 있는지 확인하는 smoke check를 추가한다.
```

이 작업은 대규모 rewrite 없이도 즉시 contract 관리 효과를 준다.

## 이후 React/TypeScript 경로

React/TypeScript 전환은 vanilla runtime이 구조화된 뒤 검토한다.

그때도 이 구조는 그대로 도움이 된다.

```text
component registry는 TypeScript metadata가 된다.
renderer family는 React component가 된다.
field contract는 TypeScript type 또는 JSON schema가 된다.
현재 payload contract는 계속 재사용한다.
```

그 전까지 runtime은 안정적인 browser-loadable JavaScript engine으로 유지한다.
