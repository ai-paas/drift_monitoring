# Renderer Source Candidates

작성일: 2026-06-30

이 폴더는 `chart_runtime.js`의 renderer를 파일 단위로 나누기 위한 source 후보 영역이다.

현재 상태:

```text
chart_runtime.js가 실제 브라우저 artifact이자 source of truth다.
src/renderers/*.js는 아직 chart_runtime.js에서 import하지 않는다.
build/concat/bundle 단계도 아직 없다.
```

현재 파일:

```text
overlay.js  renderThreshold, renderEvents, renderBand 후보
table.js    renderTable 후보
card.js     renderCard 후보
matrix.js   renderMatrix 후보
scatter.js  renderScatter, renderFeatureProjection 후보
timeline.js renderTimeline 후보
distribution.js renderDistribution 후보
line.js    renderLine 후보
bar.js     renderBar 후보
```

설계 방식:

```text
각 파일은 create...Renderers(deps) factory를 제공한다.
renderer가 사용하는 helper는 전역 이름에 의존하지 않고 deps로 명시한다.
```

source-of-truth 전환 전까지의 규칙:

```text
1. 실제 렌더링 동작을 바꾸려면 chart_runtime.js를 먼저 수정한다.
2. source 후보 파일은 chart_runtime.js와 의미상 같은 동작을 유지한다.
3. build/bundle 전략이 정해질 때까지 import 연결은 하지 않는다.
```
