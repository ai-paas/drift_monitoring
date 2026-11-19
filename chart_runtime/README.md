# Chart Runtime

`chart_runtime` is the shared rendering kernel for Chart Builder, generated chart pages, recreated chart viewer, and drift metric analysis popups.

Applications may call the runtime, but should not patch runtime behavior for one screen or one chart. Runtime changes must preserve the payload contract described in [RUNTIME_CONTRACT.md](./RUNTIME_CONTRACT.md).

## Files

- `chart_runtime.js`: shared payload renderer and component renderers
- `chart_runtime.css`: shared chart layout, component, popup, and SVG styles
- `src/runtime/`: future source candidates for pure utility modules; not imported by `chart_runtime.js` yet
- `src/renderers/`: future source candidates for small and medium renderer modules; not imported by `chart_runtime.js` yet
- `src/styles/`: future source candidates for split CSS modules; not linked by generated HTML yet
- `RUNTIME_CONTRACT.md`: required payload shape and stability boundary
- `CONCEPTS.md`: Chart Runtime에서 사용하는 핵심 개념과 용어 정의
- `PAYLOAD_RUNTIME_COMPATIBILITY.md`: compatibility rules between payload producers and runtime renderers
- `STRUCTURING_PROPOSAL.md`: 현재 vanilla runtime의 모듈 구조화 제안과 단계별 migration 계획
- `REFACTORING_PLAN.md`: 구조화 제안을 실제 작업 순서로 나눈 단계별 refactoring 계획
- `UTILITY_INVENTORY.md`: helper 함수 분리 전 pure utility, payload helper, DOM helper 분류
- `BUILD_STRATEGY.md`: build/bundle 도입 여부 결정과 현재 artifact 유지 전략
- `APPLICATION_SHELL_BOUNDARY.md`: runtime core와 recreated viewer application shell의 책임 경계
- `RENDERING_ENGINE_CONFIG_DATA_GUIDE.md`: config/data binding guide
- `RENDERING_ENGINE_NOTES.md`: runtime change log and validation notes
- `tests/component_visual_smoke.py`: visual smoke test for component/config variants
- `payloads/runtime_chart_payloads.json`: canonical 53-chart runtime payload set copied from Chart Builder generated payloads
- `tools/capture_payload_charts.py`: capture full rendered chart images for every canonical payload

## Allowed Runtime Changes

- General component renderer capability used by multiple charts
- Payload `config` option interpretation
- Data binding, sizing, overflow, popup, and NaN/invalid geometry hardening
- Runtime config override support that does not mutate saved chart definitions

## Forbidden Runtime Changes

- Branching on a specific `chartId`
- Hardcoding one chart's text, ticks, markers, colors, or data arrays
- Depending on Builder-only UI state
- Silently rewriting saved `layout`, `components`, `componentType`, or `dataBinding`

## Validation

```powershell
node --check chart_runtime\chart_runtime.js
python chart_runtime\tools\verify_source_candidates.py
python chart_runtime\tools\verify_application_shell_boundary.py
python chart_runtime\tests\validate_payload_registry.py
python -m py_compile chart_runtime\tests\component_visual_smoke.py
python chart_runtime\tests\component_visual_smoke.py
python chart_runtime\tools\capture_payload_charts.py
```

The visual smoke test uses `payloads\runtime_chart_payloads.json` by default. To test another payload set:

```powershell
python chart_runtime\tests\component_visual_smoke.py --payloads path\to\payloads.json
```
