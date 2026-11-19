# Runtime Style Source Candidates

작성일: 2026-06-30

이 폴더는 `chart_runtime.css`를 역할별 CSS로 나누기 위한 source 후보 영역이다.

현재 상태:

```text
chart_runtime.css가 실제 브라우저 artifact이자 source of truth다.
src/styles/*.css는 아직 HTML에서 link하지 않는다.
build/concat/bundle 단계도 아직 없다.
```

현재 파일:

```text
runtime-core.css    chart layout, component area, stage, card shell
chart-visuals.css   SVG axis, line, bar, point, marker, swatch, label styles
popup.css           note popup, component zoom popup
viewer-shell.css    recreated viewer shell, sidebar, workspace, original popup
```

분리 기준:

```text
runtime-core.css는 generated chart가 독립 실행될 때도 필요한 최소 layout이다.
chart-visuals.css는 renderer가 출력하는 SVG class의 시각 표현이다.
popup.css는 ChartRuntime이 직접 생성하는 popup UI다.
viewer-shell.css는 recreated chart viewer application shell에 가깝다.
```

주의:

```text
이 파일을 수정해도 현재 chart rendering 결과는 바뀌지 않는다.
동작 변경이 필요하면 같은 변경을 chart_runtime.css에 먼저 반영해야 한다.
source of truth 전환은 build/bundle 전략을 정한 뒤 별도 단계에서 수행한다.
```
