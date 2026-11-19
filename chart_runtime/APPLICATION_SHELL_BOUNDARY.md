# Application Shell Boundary

작성일: 2026-06-30

## 결정

`chart_runtime`의 장기 책임은 chart payload를 렌더링하는 runtime core에 둔다.
recreated chart viewer의 sidebar, chart list, workspace, issues panel, original chart popup 같은 application shell은 장기적으로 `chart_builder` 쪽 책임으로 분리한다.

현재 단계에서는 실제 HTML link 경로를 바꾸지 않는다.

```text
현재 browser artifact:
  chart_runtime.js
  chart_runtime.css

현재 HTML link/script 경로:
  ../../chart_runtime/chart_runtime.css
  ../../chart_runtime/chart_runtime.js
```

## 책임 경계

`chart_runtime`이 계속 책임지는 영역:

```text
payload rendering
component area layout
component stage and overlay
SVG chart visual classes
note popup
component zoom popup
window.ChartRuntime public API
```

`chart_builder` application shell로 이동할 영역:

```text
recreated chart viewer page shell
sidebar
search input
chart list
workspace header
issues panel
original chart popup
single generated chart page wrapper
```

## 현재 source 후보

CSS source 후보는 이미 다음처럼 분리되어 있다.

```text
src/styles/runtime-core.css
src/styles/chart-visuals.css
src/styles/popup.css
src/styles/viewer-shell.css
```

여기서 `viewer-shell.css`가 `chart_builder` 쪽으로 이관될 application shell 후보이다.
다만 현재 source of truth는 여전히 `chart_runtime.css`다.

## 왜 바로 이동하지 않는가

```text
1. recreated_charts.html과 53개 generated chart page가 chart_runtime.css 하나를 전제로 한다.
2. generated page는 chart_builder 도구가 다시 생성할 수 있으므로 template 수정과 재생성 순서가 필요하다.
3. drift metric analysis popup은 viewer shell 스타일을 가져가면 안 되고 runtime core만 필요하다.
4. build/bundle 전략이 아직 source-of-truth 전환까지 가지 않았다.
```

따라서 application shell 파일 이동은 `chart_builder` 변경과 함께 별도 작업으로 진행한다.

## 이관 절차

권장 순서:

```text
1. chart_builder/web/recreated_viewer_shell.css를 만든다.
2. chart_runtime/src/styles/viewer-shell.css 내용을 chart_builder 쪽 shell CSS로 옮긴다.
3. recreated_charts.html이 chart_runtime.css와 recreated_viewer_shell.css를 함께 link하도록 바꾼다.
4. generated chart page template도 같은 방식으로 바꾼다.
5. chart_runtime.css에서 viewer shell selector를 제거할 수 있는지 확인한다.
6. generated chart page, recreated viewer, drift metric analysis popup을 각각 검증한다.
```

## 완료 기준

application shell이 완전히 분리되었다고 보려면 다음을 만족해야 한다.

```text
chart_runtime.css에는 runtime core, chart visuals, runtime popup만 남는다.
viewer shell selector는 chart_builder/web 쪽 CSS에 있다.
generated chart page와 recreated viewer는 기존처럼 보인다.
drift metric analysis popup은 viewer shell CSS 없이 정상 동작한다.
component visual smoke test가 통과한다.
```

## 현재 검증

현재는 이관 전 상태이므로 다음을 검증한다.

```powershell
python chart_runtime\tools\verify_application_shell_boundary.py
```

검증 의미:

```text
viewer-shell.css source 후보가 존재한다.
chart_runtime.css에는 아직 viewer shell selector가 남아 있어 현재 HTML 경로가 깨지지 않는다.
runtime-core.css와 popup.css에는 대표 viewer shell selector가 섞이지 않는다.
```
