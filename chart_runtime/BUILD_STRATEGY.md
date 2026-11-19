# Chart Runtime Build Strategy

작성일: 2026-06-30

## 결정

현재 단계에서는 `chart_runtime.js`와 `chart_runtime.css`를 계속 브라우저용 artifact이자 source of truth로 유지한다.

```text
선택: A. 수동 유지 + source 후보 검증
```

즉, 지금은 `src/runtime`, `src/renderers`, `src/styles`를 바로 concat하거나 bundle해서 artifact를 생성하지 않는다.

## 이유

```text
1. 현재 src JavaScript 파일은 실제 module source가 아니라 create...Renderers(deps) 형태의 source 후보이다.
2. 단순 concat으로는 현재 chart_runtime.js와 동일한 IIFE artifact를 만들 수 없다.
3. src/styles도 역할별 후보 파일이지만 아직 HTML link 경로는 chart_runtime.css 하나로 고정되어 있다.
4. 기존 generated chart page, recreated viewer, drift metric analysis popup은 chart_runtime.js/css 경로를 전제로 동작한다.
5. React/TypeScript 또는 bundler 도입 여부가 아직 결정되지 않았다.
```

따라서 11단계에서는 build 도입을 보류하고, source 후보가 깨지지 않았는지 확인하는 검증 명령을 추가한다.

## 현재 검증 명령

```powershell
python chart_runtime\tools\verify_source_candidates.py
```

이 명령은 다음을 확인한다.

```text
chart_runtime.js 문법 검사
src/**/*.js 문법 검사
chart_runtime.css 존재 여부
src/styles/*.css 존재 여부
필수 source 후보 파일 존재 여부
```

## Artifact 계약

외부 HTML과 application은 계속 아래 파일만 직접 로드한다.

```text
chart_runtime.js
chart_runtime.css
```

다음 파일들은 아직 직접 로드하지 않는다.

```text
src/runtime/*.js
src/renderers/*.js
src/styles/*.css
```

## 전환 기준

실제 build/bundle을 도입하려면 먼저 다음 조건을 만족해야 한다.

```text
1. src JavaScript 파일이 source of truth가 될 구조로 바뀐다.
2. chart_runtime.js를 생성하는 build script가 artifact를 안정적으로 재생성한다.
3. chart_runtime.css를 생성하는 CSS concat 또는 bundle 순서가 확정된다.
4. generated chart, recreated viewer, drift metric analysis popup이 같은 artifact 경로로 계속 동작한다.
5. full visual smoke test가 통과한다.
```

## 다음 후보

source-of-truth 전환 시점에는 다음 중 하나를 선택한다.

```text
B. Python 또는 Node 기반 concatenate script
C. esbuild/rollup 같은 작은 bundler
```

현재 vanilla JavaScript 구조에서는 B가 가장 작은 변화다.
React/TypeScript 전환을 시작한다면 C를 다시 검토한다.

## Application Shell

application shell 분리는 build 도입과 별도로 다룬다.
현재는 `chart_runtime.css`가 viewer shell selector까지 포함하지만, 장기적으로는 `chart_builder` application shell CSS로 이동한다.

상세 기준:

```text
APPLICATION_SHELL_BOUNDARY.md
```
