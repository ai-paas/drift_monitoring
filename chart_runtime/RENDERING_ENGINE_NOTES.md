# Rendering Engine Notes

작성일: 2026-06-24

이 문서는 `chart_runtime/chart_runtime.js`와 공통 렌더링 CSS를 수정할 때 생긴 정책, 변경 이유, 검증 기준을 누적한다. 목적은 원본 차트 매칭 과정에서 생긴 공통 엔진 변경을 차트별 임시 수정과 분리해 추적하는 것이다.

## 적용 범위

렌더링 엔진은 다음 파일을 중심으로 본다.

```text
chart_runtime/chart_runtime.js
chart_runtime/chart_runtime.css
chart_runtime/tests/component_visual_smoke.py
```

`chart_builder/builder_charts.json`의 `layout`, `components`, `data`, `config`는 입력 페이로드다. 엔진에는 특정 chart ID, 특정 원본 문구, 특정 데이터 배열을 직접 넣지 않는다.

## 기본 원칙

1. 차트별 차이는 가능하면 payload의 `config`와 `data`로 표현한다.
2. 여러 차트에서 반복되는 표현만 renderer 기능으로 승격한다.
3. 데이터가 늘거나 설정이 바뀌어도 SVG에 `NaN`, `undefined`, 음수 width/height가 나오지 않아야 한다.
4. 데이터가 많아서 고정 패널 안에 다 들어가지 않는 경우, 억지로 축소하거나 잘라내지 않고 패널 내부 스크롤로 접근 가능하게 한다.
5. 원본 차트와 픽셀 단위로 완전히 같을 필요는 없지만, 눈에 띄게 튀는 색상, 위치, 방향, 배경, 제목 언어는 맞춘다.

## 2026-06-24 변경 기록

### 컴포넌트 시각 스모크 테스트 추가

추가 파일:

```text
chart_runtime/tests/component_visual_smoke.py
```

역할:

```text
chart_builder/builder_charts.json에서 정식 CHART-* 페이로드를 읽는다.
컴포넌트 타입 + 스타일 조합별 샘플을 하나씩 고른다.
각 샘플에 대해 source, shifted-data, sparse-data, dense-data, compact-config 변형을 렌더링한다.
브라우저에서 실제 캡처를 생성한다.
렌더링 예외, 콘솔 오류, NaN/undefined/Infinity, 빈 캡처, SVG viewBox 이탈, 스크롤 불가 overflow를 검사한다.
결과를 HTML 리포트와 JSON 리포트로 남긴다.
```

실행 명령:

```powershell
python chart_runtime\tests\component_visual_smoke.py
```

출력:

```text
chart_runtime/test_results/component_visual_smoke/component_visual_smoke_report.html
chart_runtime/test_results/component_visual_smoke/component_visual_smoke_report.json
chart_runtime/test_results/component_visual_smoke/captures/
```

검증 기준은 자동 판정만으로 끝내지 않는다. HTML 리포트의 썸네일을 열어 사람이 한 번 훑어보고, 자동 검사에서 놓치는 이상한 그림도 확인한다.

### 데이터/config 변형 기준

현재 변형은 다음과 같다.

```text
source         원본 payload 그대로 렌더링
shifted-data   숫자 값을 같은 범위 안에서 이동시켜 축/색/막대 반응 확인
sparse-data    행 수를 줄이고 marker/annotation/tick을 새 데이터 범위에 맞춤
dense-data     행 수를 늘려 막대, 라벨, 복잡한 그래프의 overflow 대응 확인
compact-config viewBox와 margin을 줄여 작은 패널 대응 확인
```

주의:

```text
sparse-data는 데이터만 자르면 안 된다.
마커, 주석, point highlight, horizontal marker, diagonal marker, x tick도 새 데이터 범위에 맞게 조정해야 한다.
그렇지 않으면 renderer 문제가 아니라 테스트 입력 불일치가 된다.
```

### 스크롤 가능한 차트 패널

수정 파일:

```text
chart_runtime/chart_runtime.css
```

변경 의도:

```text
막대가 많거나 노드/행/라벨이 많아 고정 패널을 벗어날 때 차트를 잘라내지 않는다.
component-stage에 overflow:auto를 적용해 패널 내부에서 수평/수직 스크롤을 제공한다.
overlay는 포인터를 막지 않고 시각 요소가 잘리지 않도록 overflow:visible로 둔다.
```

현재 정책:

```text
.component-stage는 scroll container다.
.chart-svg는 viewBox 기준 기본 크기를 갖고, 필요한 경우 100%보다 커질 수 있다.
큰 SVG는 stage 내부에서 스크롤된다.
```

### SVG 자동 크기 보정

수정 파일:

```text
chart_runtime/chart_runtime.js
```

추가 개념:

```text
svg()가 viewBox의 폭/높이를 CSS 변수 --chart-svg-w, --chart-svg-h로 기록한다.
렌더 후 normalizeSvgSizing()이 SVG geometry를 검사한다.
도형이나 텍스트가 viewBox보다 넓거나 높으면 viewBox와 표시 크기를 확장한다.
확장된 SVG는 component-stage의 스크롤로 접근한다.
```

이 변경은 “도형을 패널 안으로 강제로 눌러 넣는 것”이 아니다. 차트 내용의 실제 크기를 인정하고, 패널은 viewport처럼 동작하게 한다.

## 현재 확인된 개선 필요 항목

`dense-data` 변형에서 다음 유형이 추가로 드러났다.

```text
violin_summary
  x_positions가 2개로 고정된 설정에서 행 수가 늘면 이후 행의 x 좌표가 NaN이 된다.
  renderer는 x_positions 길이가 데이터 행보다 짧으면 자동 배치로 fallback해야 한다.

mosaic_2x2
  행 수가 늘면 row height 계산이 음수가 될 수 있다.
  renderer는 최소 row height를 보장하고 필요한 경우 SVG 높이를 늘려야 한다.

horizontal bar 계열
  dense-data에서 라벨/막대가 viewBox 밖으로 커진다.
  스크롤 가능한 확장은 맞지만, 행 수 기반으로 SVG 높이를 늘리는 편이 더 자연스럽다.

line/event 계열
  dense-data에서 marker나 path가 기존 x/y domain을 벗어날 수 있다.
  데이터 범위 기반 domain 재계산과 config 우선순위가 의도대로인지 점검해야 한다.
```

## 2026-06-24 추가 테스트 반영

### DOM 부착 후 SVG sizing 재계산

문제:

```text
normalizeSvgSizing()을 DOM에 붙이기 전에 호출하면 일부 브라우저에서 getBBox()가 정확히 계산되지 않는다.
dense-data에서 실제 도형은 그려졌지만 SVG viewBox 확장이 적용되지 않아 bbox outside viewBox로 판정됐다.
```

해결:

```text
chart container를 componentChart에 append한 뒤 normalizeSvgSizing(componentChart)를 호출한다.
이후 실제 DOM에 붙은 SVG geometry 기준으로 viewBox와 CSS 표시 크기를 확장한다.
```

### 많은 x축 항목의 가로 확장

문제:

```text
vertical_grouped와 violin_summary는 dense-data에서 x축 항목이 많아지면 고정 폭 안에 모든 항목을 압축했다.
오류는 아니지만 사람이 보기에는 막대/violin이 지나치게 좁아져 정상 그래프로 보기 어렵다.
```

해결:

```text
vertical_grouped는 rows.length * min_slot_width 기준으로 SVG 폭을 늘린다.
violin_summary는 validRows.length * min_group_width 기준으로 SVG 폭을 늘린다.
늘어난 폭은 component-stage의 horizontal scroll로 접근한다.
```

### violin_summary x position fallback

문제:

```text
config.x_positions 길이가 데이터 행 수보다 짧으면 이후 행의 x 좌표가 NaN이 됐다.
```

해결:

```text
x_positions가 validRows.length 이상일 때만 config 값을 사용한다.
부족하면 데이터 행 수에 맞춰 자동 x 위치를 재계산한다.
```

### mosaic_2x2 row height 보정

문제:

```text
행 수가 늘어나면 row height 계산이 음수가 되어 SVG rect height 오류가 발생했다.
```

해결:

```text
row_height가 명시되지 않았거나 유효하지 않으면 최소 28px을 보장한다.
필요하면 SVG 전체 높이를 행 수에 맞춰 늘리고 vertical scroll로 접근한다.
```

검증:

```powershell
node --check chart_runtime\chart_runtime.js
python -m py_compile chart_runtime\tests\component_visual_smoke.py
python chart_runtime\tests\component_visual_smoke.py
```

결과:

```text
cases=210 pass=210 fail=0
report=chart_runtime/test_results/component_visual_smoke/component_visual_smoke_report.html
```

## 2026-06-24 컴포넌트 확대 팝업

문제:

```text
중앙 viewer에서 전체 chart layout을 보면 작은 area 안의 컴포넌트가 너무 작아 세부 라벨, 축, marker를 읽기 어렵다.
데이터가 많아 scroll이 생기는 컴포넌트는 원래 panel 크기 안에서만 보면 더 확인하기 어렵다.
```

해결:

```text
각 chart area에 확대 버튼을 추가한다.
확대 버튼을 누르면 해당 area의 component만 1x1 layout으로 다시 구성해 popup에 렌더링한다.
기본 component와 overlay component를 같은 area 안에서 함께 유지한다.
popup에서는 더 넓고 높은 viewport를 제공하고, 텍스트/summary/card 계열 CSS를 확대한다.
popup 안에서도 chart-stage overflow:auto 정책을 유지해 큰 SVG는 수평/수직 scroll로 접근한다.
```

구현 위치:

```text
chart_runtime/chart_runtime.js
  renderChartPayload()가 payload를 componentChart에 저장한다.
  renderComponentChart()가 area별 확대 버튼을 만든다.
  buildZoomPayload()가 선택 area만 포함하는 popup용 payload를 만든다.
  showComponentZoomPopup()이 popup을 만들고 ChartRuntime으로 다시 렌더링한다.

chart_runtime/chart_runtime.css
  .area-zoom-link
  .component-zoom-popup
  .component-zoom-panel
  .component-zoom-chart
  popup 전용 font/label/card 확대 규칙
```

검증:

```powershell
node --check chart_runtime\chart_runtime.js
node --check chart_builder\web\recreated_charts.js
python -m py_compile chart_runtime\tests\component_visual_smoke.py
python chart_runtime\tests\component_visual_smoke.py
```

결과:

```text
component zoom popup: visible
zoom components: base + overlay rendered
invalid token: false
console errors: none
cases=210 pass=210 fail=0
```

## Renderer 수정 시 기록 양식

엔진을 수정하면 아래 형식으로 이 문서에 추가한다.

```text
### YYYY-MM-DD 변경 제목

수정 파일:
- chart_runtime/chart_runtime.js
- chart_runtime/chart_runtime.css

문제:
- 어떤 컴포넌트/변형/원본 비교에서 문제가 보였는지 기록한다.

원인:
- config 문제인지, data 문제인지, renderer 일반화 부족인지 구분한다.

해결:
- renderer에 추가한 일반 규칙을 적는다.
- chart ID 기반 분기나 특정 데이터 하드코딩을 넣지 않았는지 확인한다.

검증:
- 실행한 명령과 pass/fail 수를 적는다.
- 리포트 경로를 적는다.
```

## 현재 검증 명령

기본 정적 검사:

```powershell
node --check chart_runtime\chart_runtime.js
python -m py_compile chart_runtime\tests\component_visual_smoke.py
```

전체 시각 스모크:

```powershell
python chart_runtime\tests\component_visual_smoke.py
```

리포트 확인:

```text
chart_runtime/test_results/component_visual_smoke/component_visual_smoke_report.html
```

## 2026-06-30 Renderer Registry 도입

수정 파일:

```text
chart_runtime/chart_runtime.js
```

문제:

```text
componentType -> renderer 연결이 renderComponent()의 if/includes 분기 안에 하드코딩되어 있었다.
이 구조는 문서화된 componentType mapping과 runtime routing이 어긋날 위험이 있고, renderer 파일 분리의 기준점이 부족했다.
```

해결:

```text
COMPONENT_RENDERERS registry를 추가했다.
renderComponent()는 componentType으로 registry를 조회하고, 없으면 기존처럼 renderCard fallback을 사용한다.
threshold_line은 기존 renderThreshold(instance) signature를 유지하기 위해 adapter를 사용한다.
renderer 함수 자체와 payload contract는 변경하지 않았다.
```

검증:

```powershell
node --check chart_runtime\chart_runtime.js
python -m py_compile chart_runtime\tests\component_visual_smoke.py
python chart_runtime\tests\component_visual_smoke.py
```

결과:

```text
cases=210 pass=210 fail=0
report=chart_runtime/test_results/component_visual_smoke/component_visual_smoke_report.html
```

## 2026-06-30 Component Spec 초안 추가

수정 파일:

```text
chart_runtime/chart_runtime.js
```

문제:

```text
COMPONENT_RENDERERS는 componentType과 renderer 함수의 연결만 표현한다.
하지만 payload와 runtime의 계약을 유지하려면 각 componentType이 어떤 renderer 계열, 어떤 field contract, data 필요 여부, overlay 여부를 갖는지도 별도로 추적해야 한다.
```

해결:

```text
COMPONENT_SPECS를 추가했다.
현재는 runtime routing에 사용하지 않는 계약 메타데이터이며, 각 componentType의 renderer family와 fieldContract 이름을 기록한다.
다음 단계에서 payload/registry 검증 helper가 COMPONENT_RENDERERS와 COMPONENT_SPECS의 불일치를 검사하도록 연결한다.
```

검증 기준:

```text
이번 단계는 렌더링 동작을 바꾸지 않아야 한다.
node syntax check와 전체 component visual smoke test가 이전과 동일하게 통과해야 한다.
```

## 2026-06-30 Payload/Registry 검증 helper 추가

수정 파일:

```text
chart_runtime/tests/validate_payload_registry.py
chart_runtime/README.md
```

문제:

```text
canonical payload fixture가 runtime registry와 맞는지 확인하는 별도 검증 단계가 없었다.
componentType 누락, layout area 불일치, dataBinding.source 누락 같은 계약 위반은 실제 렌더링 실패까지 가야 발견될 수 있었다.
```

해결:

```text
validate_payload_registry.py를 추가했다.
이 스크립트는 chart_runtime.js의 COMPONENT_RENDERERS와 COMPONENT_SPECS를 읽고, payloads/runtime_chart_payloads.json의 53개 payload를 검사한다.
검사 항목은 registry/spec 일치, fieldContract 이름 유효성, component.area와 layout.areas 관계, dataBinding.source 존재 여부, 대표 field 후보 존재 여부다.
decision_card와 domain_specific_visual은 기존 renderCard fallback 타입으로 허용한다.
notes처럼 layout에 배치되지 않을 수 있는 보조 영역은 warning으로 둔다.
fieldContract의 세부 field 후보도 초기에는 warning으로 둔다.
```

검증:

```powershell
python chart_runtime\tests\validate_payload_registry.py
```

결과:

```text
payloads=53 components=262 registryTypes=37 specs=37 warnings=39 errors=0
```

## 2026-06-30 Pure Utility 분리 준비

수정 파일:

```text
chart_runtime/chart_runtime.js
chart_runtime/UTILITY_INVENTORY.md
chart_runtime/README.md
```

문제:

```text
chart_runtime.js 안에서 public entry point, payload helper, pure utility, DOM helper, renderer, popup interaction이 한 파일에 섞여 있다.
바로 파일을 나누면 browser artifact와 public API를 깨뜨릴 위험이 있으므로 먼저 함수 성격과 이동 순서를 명확히 해야 한다.
```

해결:

```text
chart_runtime.js에 섹션 경계 주석을 추가했다.
UTILITY_INVENTORY.md를 추가해 pure utility, SVG markup helper, payload helper, DOM helper를 분류했다.
이번 단계에서는 함수 구현과 호출 순서를 바꾸지 않고, 다음 source 파일 분리의 기준만 만든다.
```

검증 기준:

```text
동작 변경이 없어야 한다.
node syntax check, payload registry validation, component visual smoke test가 모두 통과해야 한다.
```

## 2026-06-30 Pure Utility source 후보 파일 추가

수정 파일:

```text
chart_runtime/src/runtime/README.md
chart_runtime/src/runtime/utils.js
chart_runtime/src/runtime/format.js
chart_runtime/src/runtime/svg.js
chart_runtime/src/runtime/color.js
chart_runtime/README.md
chart_runtime/UTILITY_INVENTORY.md
```

문제:

```text
helper 분류는 끝났지만, 실제 파일 분리 후보가 없어 다음 단계에서 어떤 source layout으로 이동할지 확인하기 어려웠다.
```

해결:

```text
src/runtime 아래에 pure utility source 후보 파일을 추가했다.
utils.js, format.js, svg.js, color.js로 나누어 현재 chart_runtime.js 안의 helper 의미를 옮겨 적었다.
다만 아직 chart_runtime.js에서 import하지 않으며, browser artifact의 source of truth는 chart_runtime.js로 유지한다.
```

검증 기준:

```text
새 source 후보 파일도 node syntax check를 통과해야 한다.
현재 runtime 동작은 바뀌지 않아야 하므로 payload registry validation과 component visual smoke test가 기존과 동일하게 통과해야 한다.
```

## 2026-06-30 작은 Renderer source 후보 파일 추가

수정 파일:

```text
chart_runtime/src/renderers/README.md
chart_runtime/src/renderers/overlay.js
chart_runtime/src/renderers/table.js
chart_runtime/src/renderers/card.js
chart_runtime/README.md
chart_runtime/UTILITY_INVENTORY.md
```

문제:

```text
renderer 분리 대상은 정해졌지만 실제 source layout과 helper 의존성 표현 방식이 없었다.
특히 overlay/table/card 계열은 작지만 dataFor, svg, escapeHtml 같은 helper에 의존하므로 전역 함수 의존을 그대로 옮기면 구조화 효과가 작다.
```

해결:

```text
src/renderers 아래에 작은 renderer source 후보 파일을 추가했다.
overlay.js는 renderThreshold, renderEvents, renderBand 후보를 담는다.
table.js는 renderTable 후보를 담는다.
card.js는 renderCard 후보를 담는다.
각 파일은 create...Renderers(deps) factory 형태로 helper 의존성을 명시한다.
아직 chart_runtime.js에서 import하지 않으며, 실제 source of truth는 chart_runtime.js로 유지한다.
```

검증 기준:

```text
새 renderer source 후보 파일도 node syntax check를 통과해야 한다.
현재 runtime 동작은 바뀌지 않아야 하므로 payload registry validation과 component visual smoke test가 기존과 동일하게 통과해야 한다.
```

## 2026-06-30 중간 Renderer source 후보 파일 추가

수정 파일:

```text
chart_runtime/src/renderers/matrix.js
chart_runtime/src/renderers/scatter.js
chart_runtime/src/renderers/timeline.js
chart_runtime/src/renderers/README.md
chart_runtime/README.md
chart_runtime/UTILITY_INVENTORY.md
```

문제:

```text
matrix, scatter, feature projection, timeline 계열은 small renderer보다 길고 geometry/helper 의존성이 많다.
바로 runtime routing을 import 기반으로 바꾸면 helper 의존성 누락이나 browser artifact 깨짐이 발생하기 쉽다.
```

해결:

```text
chart_runtime.js에서 renderMatrix, renderScatter, renderFeatureProjection, renderTimeline 본문을 기계적으로 추출해 source 후보 파일로 추가했다.
matrix.js, scatter.js, timeline.js는 create...Renderers(deps) factory 형태로 helper 의존성을 명시한다.
아직 chart_runtime.js에서 import하지 않으며, 실제 source of truth는 chart_runtime.js로 유지한다.
```

검증 기준:

```text
새 renderer source 후보 파일도 node syntax check를 통과해야 한다.
현재 runtime 동작은 바뀌지 않아야 하므로 payload registry validation과 component visual smoke test가 기존과 동일하게 통과해야 한다.
```

## 2026-06-30 Distribution Renderer source 후보 파일 추가

수정 파일:

```text
chart_runtime/src/renderers/distribution.js
chart_runtime/src/renderers/README.md
chart_runtime/UTILITY_INVENTORY.md
```

문제:

```text
renderDistribution은 histogram_overlay, density_area, violin_summary 등 variant가 많아 별도 renderer family로 분리할 필요가 있다.
다만 variant별 config 의미가 넓어서 바로 runtime routing을 import 기반으로 바꾸면 기존 payload와 어긋날 위험이 있다.
```

해결:

```text
chart_runtime.js에서 renderDistribution 본문을 기계적으로 추출해 src/renderers/distribution.js source 후보로 추가했다.
createDistributionRenderers(deps) factory 형태로 helper 의존성을 명시했다.
아직 chart_runtime.js에서 import하지 않으며, 실제 source of truth는 chart_runtime.js로 유지한다.
```

검증 기준:

```text
distribution.js가 node syntax check를 통과해야 한다.
현재 runtime 동작은 바뀌지 않아야 하므로 payload registry validation과 component visual smoke test가 기존과 동일하게 통과해야 한다.
```

## 2026-06-30 Line/Bar Renderer source 후보 파일 추가

수정 파일:

```text
chart_runtime/src/renderers/line.js
chart_runtime/src/renderers/bar.js
chart_runtime/src/renderers/README.md
chart_runtime/UTILITY_INVENTORY.md
```

문제:

```text
renderLine과 renderBar는 가장 많은 chart가 의존하는 핵심 renderer다.
line/bar 계열은 variant와 config option이 많아 바로 runtime routing을 import 기반으로 바꾸면 regression 위험이 크다.
```

해결:

```text
chart_runtime.js에서 renderLine과 renderBar 본문을 기계적으로 추출해 source 후보 파일로 추가했다.
line.js는 createLineRenderers(deps), bar.js는 createBarRenderers(deps) factory 형태로 helper 의존성을 명시한다.
아직 chart_runtime.js에서 import하지 않으며, 실제 source of truth는 chart_runtime.js로 유지한다.
```

검증 기준:

```text
line.js와 bar.js가 node syntax check를 통과해야 한다.
현재 runtime 동작은 바뀌지 않아야 하므로 payload registry validation과 component visual smoke test가 기존과 동일하게 통과해야 한다.
```

## 2026-06-30 CSS source 후보 파일 추가

수정 파일:

```text
chart_runtime/src/styles/README.md
chart_runtime/src/styles/runtime-core.css
chart_runtime/src/styles/chart-visuals.css
chart_runtime/src/styles/popup.css
chart_runtime/src/styles/viewer-shell.css
chart_runtime/README.md
chart_runtime/UTILITY_INVENTORY.md
```

문제:

```text
chart_runtime.css가 runtime core, SVG visual, popup, recreated viewer shell 책임을 모두 담고 있다.
바로 CSS link 경로를 바꾸면 generated chart와 recreated viewer, analysis popup을 동시에 깨뜨릴 수 있다.
```

해결:

```text
src/styles 아래에 역할별 CSS source 후보 파일을 추가했다.
현재 HTML은 여전히 chart_runtime.css를 link하며, source of truth도 chart_runtime.css로 유지한다.
source 후보는 다음 build/bundle 단계에서 concat 또는 bundle 전략을 결정할 때 기준으로 사용한다.
```

검증 기준:

```text
현재 runtime 동작은 바뀌지 않아야 한다.
payload registry validation과 component visual smoke test가 기존과 동일하게 통과해야 한다.
```

## 2026-06-30 Build/Bundle 전략 결정

수정 파일:

```text
chart_runtime/BUILD_STRATEGY.md
chart_runtime/tools/verify_source_candidates.py
chart_runtime/README.md
```

결정:

```text
현재는 chart_runtime.js와 chart_runtime.css를 계속 browser artifact이자 source of truth로 유지한다.
src/ 파일은 source 후보로 검증하되, 아직 concat/bundle로 artifact를 생성하지 않는다.
```

이유:

```text
src JavaScript 파일은 create...Renderers(deps) factory 형태의 후보 파일이므로 단순 concat으로 현재 IIFE artifact를 만들 수 없다.
src/styles CSS도 역할별 후보지만 HTML link 경로는 아직 chart_runtime.css 하나로 고정되어 있다.
```

해결:

```text
BUILD_STRATEGY.md를 추가해 A. 수동 유지 + source 후보 검증 전략을 명시했다.
tools/verify_source_candidates.py를 추가해 artifact와 src 후보 파일의 존재 여부, JavaScript syntax, CSS 후보 파일 상태를 검증한다.
```

검증:

```powershell
python chart_runtime\tools\verify_source_candidates.py
```

## 2026-06-30 Application Shell 책임 경계 문서화

수정 파일:

```text
chart_runtime/APPLICATION_SHELL_BOUNDARY.md
chart_runtime/tools/verify_application_shell_boundary.py
chart_runtime/README.md
chart_runtime/BUILD_STRATEGY.md
```

결정:

```text
현재 단계에서는 recreated viewer와 generated chart page의 HTML link 경로를 바꾸지 않는다.
chart_runtime.css는 당분간 viewer shell selector를 포함해 기존 HTML을 계속 지원한다.
장기적으로 viewer-shell.css는 chart_builder application shell 쪽으로 이관한다.
```

이유:

```text
recreated_charts.html과 generated chart page들이 chart_runtime.css 하나를 전제로 한다.
drift metric analysis popup은 viewer shell style을 가져가면 안 되므로, 실제 이관은 chart_builder template 변경과 함께 별도 단계에서 진행해야 한다.
```

검증:

```powershell
python chart_runtime\tools\verify_application_shell_boundary.py
```

## 2026-06-30 전체 Payload Chart 캡처 추가

수정 파일:

```text
chart_runtime/tools/capture_payload_charts.py
chart_runtime/README.md
```

목적:

```text
canonical payload 53개를 각각 전체 chart로 렌더링하고, chart 단위 PNG 캡처를 생성한다.
component_visual_smoke.py는 component/style/variant smoke case 중심이고, 이 스크립트는 payload 하나가 만드는 전체 chart 화면을 확인하기 위한 도구다.
```

실행:

```powershell
python chart_runtime\tools\capture_payload_charts.py
```

출력:

```text
chart_runtime/test_results/full_payload_chart_captures/captures/
chart_runtime/test_results/full_payload_chart_captures/full_payload_chart_captures.html
chart_runtime/test_results/full_payload_chart_captures/full_payload_chart_captures.json
```

검증 결과:

```text
payloads=53 pass=53 fail=0
```

