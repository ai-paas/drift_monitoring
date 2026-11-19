# Chart Builder Prototype

This folder contains the standalone chart builder prototype split out from the drift report gallery project.

## Run

Recommended foreground run:

```powershell
cd "C:\Users\jklee\PycharmProjects\drift_llm_intepretation\chart_builder"
.\run_chart_builder.cmd
```

Open:

```text
http://127.0.0.1:8766/builder_prototype.html
```

Split layout practice page:

```text
http://127.0.0.1:8766/split_layout_practice.html
```

Use this page as the Layout Designer. Create a split layout, enter a layout name, and save it. Then return to the Chart Builder page and select the saved layout from the `Saved` combo box.

Health check:

```powershell
Invoke-RestMethod -Uri http://127.0.0.1:8766/api/health
```

Expected response:

```text
ok service                 backend
-- -------                 -------
True chart-builder-prototype fastapi
```

## Runbook

### Keep the server running

`run_chart_builder.cmd` starts a blocking web server process. Do not run it through a command wrapper that has a short timeout, because the wrapper may stop the server even though startup succeeded.

When using an automation tool, prefer one of these patterns:

```powershell
# Interactive terminal: easiest and most reliable
.\run_chart_builder.cmd
```

```powershell
# Background process from PowerShell
Start-Process -WindowStyle Hidden -FilePath ".\run_chart_builder.cmd"
```

After starting in the background, verify with the health check instead of assuming that process creation means the web server is ready:

```powershell
Invoke-RestMethod -Uri http://127.0.0.1:8766/api/health
```

### Diagnose startup problems

If the page does not open, check in this order:

1. Verify the server:

```powershell
Invoke-RestMethod -Uri http://127.0.0.1:8766/api/health
```

2. Verify the HTML route:

```powershell
(Invoke-WebRequest -Uri http://127.0.0.1:8766/builder_prototype.html -UseBasicParsing).StatusCode
```

Expected status code:

```text
200
```

3. Check whether port `8766` is already in use:

```powershell
netstat -ano | Select-String -Pattern ":8766"
```

If startup logs show `WinError 10048`, another process is already bound to `127.0.0.1:8766`. In that case, either use the already-running server or start this server on another port:

```powershell
$env:CHART_BUILDER_PORT = "8767"
.\run_chart_builder.cmd
```

Then open:

```text
http://127.0.0.1:8767/builder_prototype.html
```

### Known execution pitfall

The server may appear to "fail" if it is launched by a tool command with a short timeout. In that case, the server starts correctly, prints `Uvicorn running on http://127.0.0.1:8766`, and then the wrapper terminates it when the timeout expires.

The reliable signal is the health endpoint:

```powershell
Invoke-RestMethod -Uri http://127.0.0.1:8766/api/health
```

The server exposes:

- `GET /api/health`
- `GET /api/chart-builder/prototype`
- `PUT /api/chart-builder/prototype`
- `GET /api/chart-builder/layouts`
- `PUT /api/chart-builder/layouts`
- `DELETE /api/chart-builder/layouts/{layout_name}`
- `GET /api/chart-builder/charts`
- `PUT /api/chart-builder/charts`
- `DELETE /api/chart-builder/charts/{chart_name}`
- `GET /api/charts/CHART-PROTOTYPE-001/runtime-render-payload`

Saved prototype payload is written to `builder_prototype_payload.json` in this folder.
Saved named layouts are written to `builder_layouts.json` in this folder.
Saved named charts are written to `builder_charts.json` in this folder.

## Chart Runtime

Builder 컴포넌트는 팔레트에서 선택한 뒤 영역을 클릭하거나 영역으로 드래그해 배치합니다.
일반 컴포넌트는 대상 영역의 기존 기본 컴포넌트를 교체하고, overlay 컴포넌트는
기본 컴포넌트가 있으면 그 위에 추가됩니다. 배치된 컴포넌트를 클릭하면 속성을 선택합니다.

`buildRuntimePayload`는 모든 `sampleData` 항목을 `sample.<이름>`으로 전달하며,
차트에 명시된 `data` 값이 샘플보다 우선합니다. 이전 이름인
`sample.reference_current`, `sample.p_values`도 유지합니다.
Adaptive Model Structure의 기존 `primary_series_field`/`secondary_series_field`는
미리보기에서 Runtime의 `value_field`/`secondary_value_field`로 연결합니다.
저장된 원본 설정은 변경하지 않습니다. 영역명은 제목으로 한 번 표시합니다.

팔레트의 Builder 전용 설정(예: distance_field, p_value_field, facet_field)은
기존 Builder 전용 렌더러로 미리보기를 그립니다. 공용 Runtime은 영역과 컴포넌트
wrapper를 만들고, Builder는 해당 wrapper의 내용과 ResizeObserver 갱신을 담당합니다.
샘플 binding을 사용하거나 팔레트의 기본 설정 키를 모두 가진 컴포넌트에만 적용합니다.
가져온 보고서 차트처럼 Runtime 설정을 사용하는 컴포넌트는 공용 렌더링을 유지합니다.
이 호환 처리는 Builder 미리보기용이며 공용 Runtime의 registry/API를 변경하지 않습니다.

배치 회귀 검증은 Chrome과 `playwright-core`가 있는 환경에서 다음과 같이 실행합니다.
기존 저장 데이터를 변경하는 API는 테스트 중 차단합니다.

```bash
BUILDER_URL=http://127.0.0.1:8766/builder_prototype.html node chart_builder/tests/placement_browser_test.cjs
BUILDER_URL=http://127.0.0.1:8766/builder_prototype.html node chart_builder/tests/all_components_browser_test.cjs
```

필요하면 `NODE_PATH`로 `playwright-core` 설치 위치를, `CHROME_PATH`로 Chrome 실행 파일을 지정합니다.
전체 테스트에 `BUILDER_ARTIFACT_DIR`을 지정하면 32개 컴포넌트의 모음 이미지와 JSON 결과를 저장합니다.

Shared chart rendering code lives in `../chart_runtime/`.

The Builder, recreated chart viewer, generated chart pages, and drift metric analysis popup all load the same runtime:

```text
../chart_runtime/chart_runtime.js
../chart_runtime/chart_runtime.css
```

Runtime changes should be treated as a separate task. See:

```text
../chart_runtime/README.md
../chart_runtime/RUNTIME_CONTRACT.md
```
