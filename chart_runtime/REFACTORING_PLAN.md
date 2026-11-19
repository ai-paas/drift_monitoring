# Chart Runtime 단계별 Refactoring 계획

## 목적

이 문서는 `chart_runtime`을 실제로 리팩터링하기 위한 실행 계획이다.

기본 원칙:

```text
1. 기존 payload를 깨지 않는다.
2. window.ChartRuntime public API를 유지한다.
3. 한 단계마다 검증 가능한 작은 변경만 한다.
4. React/TypeScript 전환은 이번 계획의 범위에 넣지 않는다.
5. 모든 단계는 canonical 53개 payload fixture로 검증한다.
```

관련 문서:

```text
CONCEPTS.md
RUNTIME_CONTRACT.md
PAYLOAD_RUNTIME_COMPATIBILITY.md
STRUCTURING_PROPOSAL.md
```

## 현재 기준선

현재 구조:

```text
chart_runtime/
  chart_runtime.js
  chart_runtime.css
  payloads/
    runtime_chart_payloads.json
  tests/
    component_visual_smoke.py
```

현재 테스트 fixture:

```text
payloads/runtime_chart_payloads.json
```

이 fixture는 `drift 보고서/charts` 원본 chart 53개와 1:1 대응한다.

## 공통 검증 명령

각 단계 완료 후 최소한 다음을 실행한다.

```powershell
node --check chart_runtime\chart_runtime.js
python -m py_compile chart_runtime\tests\component_visual_smoke.py
python chart_runtime\tests\component_visual_smoke.py
```

작업 중 빠른 확인:

```powershell
python chart_runtime\tests\component_visual_smoke.py --limit 10
```

generated chart viewer나 wrapper가 바뀐 경우:

```powershell
python chart_builder\tools\generate_recreated_site.py
node --check chart_builder\web\recreated_charts.js
```

drift metric analysis popup이 영향을 받는 경우:

```powershell
node --check drift_metric_timeseries\web\drift_metric_timeseries_demo.js
```

## 단계 0. 기준선 고정

목표:

```text
현재 runtime이 canonical fixture 53개를 기준으로 통과하는지 확인한다.
```

작업:

```text
1. full visual smoke test 실행
2. report HTML/JSON 경로 기록
3. 실패가 있으면 refactoring 전에 별도 이슈로 분리
```

완료 조건:

```text
component_visual_smoke.py full run 통과
또는 기존 실패가 명확히 기록됨
```

산출물:

```text
chart_runtime/test_results/component_visual_smoke/component_visual_smoke_report.html
chart_runtime/test_results/component_visual_smoke/component_visual_smoke_report.json
```

## 단계 1. Renderer Registry 도입

목표:

```text
renderComponent()의 componentType 분기를 registry lookup으로 바꾼다.
```

작업:

```text
1. chart_runtime.js 안에 COMPONENT_RENDERERS 상수 추가
2. 기존 if/includes 분기를 COMPONENT_RENDERERS lookup으로 교체
3. fallback은 기존과 동일하게 renderCard 유지
4. renderer 함수들은 아직 파일 분리하지 않음
```

예상 변경:

```js
const COMPONENT_RENDERERS = {
  trend_line: renderLine,
  raw_signal_trend: renderLine,
  detector_statistic_view: renderLine,
  bar_chart: renderBar,
  ranking_view: renderBar,
  heatmap: renderMatrix,
  projection_scatter: renderScatter,
  state_timeline: renderTimeline,
  threshold_line: renderThreshold,
  event_marker: renderEvents
};
```

주의:

```text
renderThreshold는 현재 payload 인자를 받지 않는다.
registry 호출부에서 renderer signature를 맞추거나 adapter를 둔다.
```

완료 조건:

```text
기존 53개 fixture 기준 smoke test 통과
PAYLOAD_RUNTIME_COMPATIBILITY.md의 renderer mapping과 코드가 일치
```

Rollback 기준:

```text
같은 payload에서 componentType fallback이 늘어나거나 chart rendering 결과가 바뀌면 이전 renderComponent()로 되돌린다.
```

## 단계 2. Component Spec 초안 추가

목표:

```text
componentType별 renderer family와 field 계약을 데이터로 표현하기 시작한다.
```

작업:

```text
1. chart_runtime.js 안에 COMPONENT_SPECS 상수 추가
2. 처음에는 render routing에 직접 사용하지 않고 validation/helper 용도로 둠
3. line/bar/scatter/timeline/matrix/distribution의 대표 field 계약 작성
4. CONCEPTS.md와 PAYLOAD_RUNTIME_COMPATIBILITY.md의 설명과 맞춤
```

예상 형태:

```js
const COMPONENT_SPECS = {
  trend_line: {
    renderer: "line",
    requiredData: true,
    fieldContract: "line"
  },
  bar_chart: {
    renderer: "bar",
    requiredData: true,
    fieldContract: "bar"
  }
};
```

완료 조건:

```text
COMPONENT_RENDERERS에 있는 componentType이 COMPONENT_SPECS에도 존재
문서와 코드의 componentType 목록이 일치
smoke test 통과
```

Rollback 기준:

```text
SPEC가 runtime behavior를 바꾸면 안 된다. behavior 변경이 생기면 SPEC 사용을 중지하고 문서/데이터만 남긴다.
```

## 단계 3. Payload/Registry 검증 helper 추가

목표:

```text
canonical payload가 registry와 field 계약을 만족하는지 자동 확인한다.
```

작업:

```text
1. tests/validate_payload_registry.py 추가
2. payloads/runtime_chart_payloads.json 로드
3. 모든 componentType이 registry에 있는지 확인
4. 모든 component.area가 layout.areas에 있는지 확인
5. 모든 dataBinding.source가 payload.data에 있는지 확인
6. field contract가 명시된 component는 data row field 존재 여부 확인
```

주의:

```text
초기에는 warning과 error를 구분한다.
기존 payload 특성상 일부 optional field는 warning으로 처리한다.
```

완료 조건:

```text
validate_payload_registry.py 통과
component_visual_smoke.py 통과
README Validation 섹션에 새 명령 추가
```

검증 명령:

```powershell
python chart_runtime\tests\validate_payload_registry.py
```

## 단계 4. Pure Utility 분리 준비

목표:

```text
renderer와 무관한 순수 helper를 분리 가능한 단위로 정리한다.
```

작업:

```text
1. helper 함수들을 chart_runtime.js 상단에 그룹화
2. 함수 사이 의존성을 정리
3. DOM을 직접 만지는 helper와 순수 helper를 구분
4. 테스트 가능한 함수 목록 작성
```

대상 함수:

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
classForValue
heatmapColor
```

완료 조건:

```text
파일 분리는 아직 하지 않더라도 helper 섹션이 명확히 정리됨
smoke test 통과
```

## 단계 5. Pure Utility 파일 분리

목표:

```text
순수 helper를 src/runtime/svg.js 또는 src/runtime/utils.js로 분리한다.
```

작업:

```text
1. src/runtime/svg.js 생성
2. src/runtime/utils.js 생성 여부 결정
3. chart_runtime.js가 아직 browser artifact라면 build/concat 없이 바로 import를 쓰지 않는다.
4. 첫 단계에서는 source 분리만 하고 chart_runtime.js는 기존 동작 유지
```

선택지:

```text
A. build step 도입 전까지 src/는 참조용 source로만 둔다.
B. 간단한 concatenate script를 만들어 chart_runtime.js를 생성한다.
```

권장:

```text
이 단계에서는 A를 선택한다. 실제 bundle 생성은 단계 10에서 다룬다.
```

완료 조건:

```text
src/runtime/svg.js에 helper source 존재
chart_runtime.js 동작 유지
문서에 source-of-truth 전환 시점 명시
```

## 단계 6. 작은 Renderer부터 분리

목표:

```text
작고 독립적인 renderer를 먼저 분리해 renderer 파일 구조를 검증한다.
```

대상:

```text
renderThreshold
renderEvents
renderBand
renderTable
renderCard
```

작업:

```text
1. src/renderers/overlay.js 생성
2. src/renderers/table.js 생성
3. src/renderers/card.js 생성
4. chart_runtime.js와 동일한 함수 body를 유지
5. 실제 browser artifact 변경은 최소화
```

완료 조건:

```text
분리된 renderer source와 chart_runtime.js가 일치
smoke test 통과
```

## 단계 7. 중간 크기 Renderer 분리

목표:

```text
복잡도가 중간인 renderer family를 분리한다.
```

대상:

```text
renderTimeline
renderScatter
renderFeatureProjection
renderMatrix
```

주의:

```text
scatter/matrix 계열은 geometry helper 의존성이 많다.
분리 전 shared helper 의존성을 먼저 정리한다.
```

완료 조건:

```text
각 renderer family 단위 smoke case 통과
전체 smoke test 통과
```

## 단계 8. Distribution Renderer 분리

목표:

```text
renderDistribution을 별도 renderer family로 분리한다.
```

주의:

```text
distribution 계열은 histogram, density, violin, quantile 등 style variant가 많다.
variant별 config를 건드리지 않는다.
```

완료 조건:

```text
distribution_view
histogram_view
distribution_summary_plot
quantile_view
관련 smoke case 통과
전체 smoke test 통과
```

## 단계 9. Line/Bar Renderer 분리

목표:

```text
가장 큰 renderer family인 renderLine과 renderBar를 분리한다.
```

주의:

```text
line/bar는 가장 많은 chart가 의존한다.
작은 helper 추출 없이 바로 옮기지 않는다.
```

권장 순서:

```text
1. renderLine 내부 variant helper 추출
2. renderLine 분리
3. renderBar 내부 style variant helper 추출
4. renderBar 분리
```

완료 조건:

```text
전체 smoke test 통과
generated chart viewer 수동 확인
drift metric analysis popup 수동 확인
```

## 단계 10. CSS 분리

목표:

```text
chart_runtime.css를 책임별 CSS로 나눈다.
```

대상 파일:

```text
src/styles/runtime-core.css
src/styles/chart-visuals.css
src/styles/popup.css
src/styles/viewer-shell.css
```

분리 기준:

```text
runtime-core.css:
  component-chart, chart-container, chart-area, component-stage, chart-svg

chart-visuals.css:
  axis, line, bar, point, state, swatch, marker, label

popup.css:
  note popup, component zoom popup

viewer-shell.css:
  site, sidebar, workspace, chart-list, issues, original-popup
```

주의:

```text
최종 chart_runtime.css는 기존 class behavior를 유지해야 한다.
viewer-shell.css를 runtime에서 바로 제거하지 말고, application 쪽으로 옮기는 별도 단계로 둔다.
```

완료 조건:

```text
CSS split 후 최종 chart_runtime.css 생성 또는 유지
visual smoke screenshot 비교
viewer/generated/analysis popup 수동 확인
```

## 단계 11. 간단한 Build/Bundle 도입 여부 결정

목표:

```text
src/ 분리 파일을 browser-facing chart_runtime.js/css로 만드는 방법을 결정한다.
```

선택지:

```text
A. 수동 유지
B. 간단한 concatenate script
C. esbuild/rollup 같은 작은 bundler
```

권장:

```text
초기에는 B 또는 C 중 작은 쪽을 선택한다.
React/TypeScript를 도입하지 않는 동안은 과한 toolchain을 피한다.
```

완료 조건:

```text
chart_runtime.js
chart_runtime.css
파일명은 유지
기존 HTML script/link 경로 변경 없음
build 명령 문서화
```

## 단계 12. Application Shell 분리

목표:

```text
runtime core와 recreated chart viewer shell의 CSS/JS 책임을 분리한다.
```

작업:

```text
1. viewer-shell.css를 chart_builder/web 쪽으로 이동할지 결정
2. recreated_charts.html이 viewer shell CSS를 별도로 로드
3. chart_runtime.css는 chart 렌더링 core에 집중
```

주의:

```text
drift_metric_timeseries는 runtime core만 필요하다.
viewer shell style이 analysis popup에 흘러들지 않게 한다.
```

완료 조건:

```text
recreated chart viewer 정상
generated chart page 정상
drift metric analysis popup 정상
smoke test 통과
```

## 단계별 우선순위 요약

실행 순서:

```text
0. 기준선 full smoke test
1. Renderer Registry 도입
2. Component Spec 초안 추가
3. Payload/Registry 검증 helper 추가
4. Pure Utility 정리
5. Pure Utility 파일 분리
6. 작은 Renderer 분리
7. 중간 Renderer 분리
8. Distribution Renderer 분리
9. Line/Bar Renderer 분리
10. CSS 분리
11. Build/Bundle 도입 여부 결정
12. Application Shell 분리
```

가장 먼저 할 구현 작업:

```text
단계 1. Renderer Registry 도입
```

이유:

```text
변경 범위가 작다.
payload/runtime 계약 관리 효과가 크다.
renderer 파일 분리의 기반이 된다.
문서화한 registry 개념을 실제 코드로 옮기는 첫 단계다.
```

## 완료 정의

전체 refactoring이 완료되었다고 볼 수 있는 상태:

```text
componentType mapping이 registry로 관리된다.
field contract가 validation에 쓰인다.
payload fixture 53개가 자동 검증된다.
renderer family가 파일 단위로 분리된다.
CSS가 runtime core와 viewer shell로 분리된다.
window.ChartRuntime API는 유지된다.
기존 generated chart와 drift metric analysis popup이 그대로 동작한다.
```
