# Chart Runtime Utility Inventory

작성일: 2026-06-30

이 문서는 `chart_runtime.js`의 helper 함수를 분리하기 전에 함수 성격을 분류한다.
목적은 다음 단계에서 `src/runtime/svg.js`, `src/runtime/utils.js` 같은 source 파일을 만들 때 무엇을 먼저 옮길지 판단하는 것이다.

## 분류 기준

```text
Pure utility
  입력값만으로 결과가 결정되고 DOM, 전역 상태, payload mutation에 의존하지 않는다.

SVG markup helper
  DOM을 직접 만지지는 않지만 SVG/HTML 문자열을 만든다.
  renderer와 함께 움직일 수 있으므로 pure utility와 구분한다.

DOM helper
  document, element, dataset, event, getBBox 같은 browser DOM API에 의존한다.
  build step 도입 전에는 chart_runtime.js에 남긴다.

Payload helper
  payload/component 구조를 읽는 얇은 helper다.
  순수 함수지만 payload contract와 가까워 registry/contract 모듈 후보로 본다.
```

## 2026-06-30 작은 Renderer source 후보 파일

6단계에서 다음 source 후보 파일을 만들었다.

```text
src/renderers/overlay.js
src/renderers/table.js
src/renderers/card.js
```

현재 source of truth는 여전히 `chart_runtime.js`다.
위 파일들은 아직 import되지 않는다.

분리 기준:

```text
1. overlay.js는 renderThreshold, renderEvents, renderBand를 담는다.
2. table.js는 renderTable을 담는다.
3. card.js는 renderCard와 fallback card 계열을 담는다.
4. renderer source 후보는 create...Renderers(deps) factory 형태로 helper 의존성을 명시한다.
5. 실제 routing은 COMPONENT_RENDERERS와 chart_runtime.js의 기존 함수가 계속 담당한다.
```

## 2026-06-30 중간 Renderer source 후보 파일

7단계에서 다음 source 후보 파일을 만들었다.

```text
src/renderers/matrix.js
src/renderers/scatter.js
src/renderers/timeline.js
```

현재 source of truth는 여전히 `chart_runtime.js`다.
위 파일들은 아직 import되지 않는다.

분리 기준:

```text
1. matrix.js는 renderMatrix를 담는다.
2. scatter.js는 renderScatter와 renderFeatureProjection을 담는다.
3. timeline.js는 renderTimeline을 담는다.
4. 함수 본문은 chart_runtime.js에서 기계적으로 추출해 source 후보로 둔다.
5. 실제 routing은 COMPONENT_RENDERERS와 chart_runtime.js의 기존 함수가 계속 담당한다.
```

## 2026-06-30 Distribution Renderer source 후보 파일

8단계에서 다음 source 후보 파일을 만들었다.

```text
src/renderers/distribution.js
```

현재 source of truth는 여전히 `chart_runtime.js`다.
위 파일은 아직 import되지 않는다.

분리 기준:

```text
1. distribution.js는 renderDistribution을 담는다.
2. distribution_view, histogram_view, distribution_summary_plot, quantile_view routing은 기존 COMPONENT_RENDERERS가 계속 담당한다.
3. 함수 본문은 chart_runtime.js에서 기계적으로 추출해 source 후보로 둔다.
4. distribution_style variant별 config 의미는 변경하지 않는다.
```

## 2026-06-30 Line/Bar Renderer source 후보 파일

9단계에서 다음 source 후보 파일을 만들었다.

```text
src/renderers/line.js
src/renderers/bar.js
```

현재 source of truth는 여전히 `chart_runtime.js`다.
위 파일들은 아직 import되지 않는다.

분리 기준:

```text
1. line.js는 renderLine을 담는다.
2. bar.js는 renderBar를 담는다.
3. line/bar는 가장 많은 chart가 의존하는 핵심 renderer이므로 실제 routing 전환은 별도 단계에서 다룬다.
4. 함수 본문은 chart_runtime.js에서 기계적으로 추출해 source 후보로 둔다.
5. trend_line, control_chart, bar_chart, ranking_view 등 기존 COMPONENT_RENDERERS routing은 chart_runtime.js가 계속 담당한다.
```

## 2026-06-30 CSS source 후보 파일

10단계에서 다음 source 후보 파일을 만들었다.

```text
src/styles/runtime-core.css
src/styles/chart-visuals.css
src/styles/popup.css
src/styles/viewer-shell.css
```

현재 source of truth는 여전히 `chart_runtime.css`다.
위 파일들은 아직 HTML에서 link되지 않는다.

분리 기준:

```text
1. runtime-core.css는 component-chart, chart-container, chart-area, component-stage 같은 runtime layout을 담는다.
2. chart-visuals.css는 SVG axis, line, bar, point, marker, swatch, label class를 담는다.
3. popup.css는 note popup과 component zoom popup을 담는다.
4. viewer-shell.css는 recreated viewer의 site, sidebar, workspace, issues, original-popup을 담는다.
5. 실제 CSS 로딩은 기존 chart_runtime.css가 계속 담당한다.
```

## Pure Utility 후보

| 함수 | 역할 | 분리 후보 |
| --- | --- | --- |
| `escapeHtml` | 문자열 HTML escape | `src/runtime/utils.js` |
| `extent` | 숫자 field의 min/max 계산 | `src/runtime/scales.js` 또는 `utils.js` |
| `formatNumber` | 숫자 표시 형식 결정 | `src/runtime/format.js` |
| `formatByMode` | percent/fixed 표시 형식 결정 | `src/runtime/format.js` |
| `hasFiniteValue` | 숫자로 해석 가능한 값 판정 | `src/runtime/utils.js` |
| `viewBoxFor` | config에서 SVG viewBox 크기 계산 | `src/runtime/svg.js` |
| `marginFor` | config/default margin 병합 | `src/runtime/svg.js` |
| `ticksFor` | 축 tick 배열 생성 | `src/runtime/scales.js` |
| `path` | point 배열을 SVG path 문자열로 변환 | `src/runtime/svg.js` |
| `stepPath` | step line SVG path 문자열 생성 | `src/runtime/svg.js` |
| `parseHexColor` | hex color를 RGB 배열로 변환 | `src/runtime/color.js` |
| `heatmapColor` | 값과 palette로 heatmap 색상 계산 | `src/runtime/color.js` |
| `classForValue` | threshold rule에 맞는 CSS class 선택 | `src/runtime/utils.js` |

## SVG Markup Helper 후보

| 함수 | 역할 | 분리 후보 |
| --- | --- | --- |
| `svg` | 공통 `<svg class="chart-svg">` 문자열 생성 | `src/runtime/svg.js` |
| `wrapComponent` | runtime component wrapper HTML 생성 | renderer shell 또는 `src/runtime/domMarkup.js` |

`svg`는 DOM을 직접 만지지 않으므로 분리 가능하다.
다만 현재 renderer 대부분이 `svg()`를 직접 호출하므로 renderer 파일 분리 전까지는 `chart_runtime.js`에 남긴다.

## Payload Helper 후보

| 함수 | 역할 | 분리 후보 |
| --- | --- | --- |
| `dataFor` | component의 `dataBinding.source`로 rows 조회 | `src/runtime/payload.js` |
| `rowsForSource` | source 이름으로 rows 조회 | `src/runtime/payload.js` |
| `noteTextFromObject` | interpretation note 객체를 표시 문자열로 변환 | `src/runtime/payload.js` |
| `componentNoteForArea` | area component 목록에서 note 추출 | `src/runtime/payload.js` |

이 함수들은 순수 함수에 가깝지만 payload contract를 직접 읽는다.
따라서 일반 utility보다는 payload/contract module로 분리하는 편이 낫다.

## DOM Helper

| 함수 | 역할 | 유지 위치 |
| --- | --- | --- |
| `renderChartPayload` | public entry point, target element 조회 | browser shell |
| `renderComponentChart` | layout area DOM 구성 | browser shell |
| `normalizeSvgSizing` | DOM에 붙은 SVG geometry 측정 | browser shell |
| `bindNotePopup` | click event binding | viewer interaction |
| `buildZoomPayload` | zoom popup용 payload 재구성 | viewer interaction 또는 payload helper |
| `showComponentZoomPopup` | zoom popup DOM 생성/표시 | viewer interaction |
| `closeComponentZoomPopup` | zoom popup 닫기 | viewer interaction |
| `showNotePopup` | note popup DOM 생성/표시 | viewer interaction |

`normalizeSvgSizing`은 계산 로직이 있어도 `getBBox()`와 실제 DOM 부착 상태에 의존한다.
따라서 pure utility로 분류하지 않는다.

## 다음 단계 적용 원칙

```text
1. 먼저 source 파일만 만들고, chart_runtime.js의 browser artifact 동작은 유지한다.
2. build/bundle이 도입되기 전까지 chart_runtime.js를 import 기반으로 바꾸지 않는다.
3. pure utility는 DOM helper보다 먼저 분리한다.
4. renderer 분리는 overlay/table/card처럼 작은 renderer부터 시작한다.
5. public API인 window.ChartRuntime은 마지막까지 유지한다.
```

## 2026-06-30 Source 후보 파일

5단계에서 다음 source 후보 파일을 만들었다.

```text
src/runtime/utils.js
src/runtime/format.js
src/runtime/svg.js
src/runtime/color.js
```

현재 source of truth는 여전히 `chart_runtime.js`다.
위 파일들은 아직 import되지 않으며, build step도 없다.

전환 기준:

```text
1. source 후보 파일의 helper가 chart_runtime.js와 의미상 동일해야 한다.
2. node syntax check가 통과해야 한다.
3. chart_runtime.js를 생성하거나 bundle하는 전략이 결정되어야 한다.
4. source-of-truth 전환 커밋에서는 generated artifact와 source 파일의 관계를 문서화해야 한다.
```
