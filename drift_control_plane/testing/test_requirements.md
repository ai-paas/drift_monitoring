# Drift Server Test Requirements

## 1. 목적

이 문서는 drift monitoring 시스템의 테스트 요구사항을 정의한다.

문제의 핵심은 다음이다.

```text
chart와 drift method가 많아질수록 사람이 웹 UI를 열어 확인하는 방식으로는 문제를 찾기 어렵다.
브라우저 자동화에서 screenshot/pixel 비교만 사용하면 테스트가 불안정해진다.
```

따라서 v1 테스트 전략은 다음을 원칙으로 한다.

```text
UI 화면 자체보다 API response, chart payload, UI view-model state를 우선 검증한다.
브라우저 테스트는 smoke test와 test state 검증으로 제한한다.
```

## 2. 테스트 계층

테스트는 네 계층으로 나눈다.

```text
1. API contract test
2. analysis chart payload test
3. UI view-model state test
4. browser smoke test
```

각 계층의 목적은 다르다. 모든 문제를 브라우저 UI에서 찾으려고 하지 않는다.

## 3. API Contract Test

### 3.1 목적

Drift Server, Admin Server, Test Feeder Server가 문서화된 API contract를 지키는지 검증한다.

### 3.2 대상

```text
Admin Server API
Drift Server control API
Drift Server timeseries/view API
Test Feeder Server API
LLM Interpretation Server job API
Chart Builder existing endpoint 또는 v1 최소 wrapper
```

### 3.3 검증 항목

예:

```text
GET /api/sources/{source_id}/timeseries-data
```

검증:

```text
ok = true
sourceId 일치
series points 존재
bucket 개수 일치
empty bucket 표현 일치
event marker 존재
analysis chart link 존재
```

예:

```text
POST /api/drift/adapters/{adapter_id}/poll-once
```

검증:

```text
10분 window 하나만 처리
metric_bucket 중복 생성 없음
method_run 중복 생성 없음
drift_event 중복 생성 없음
adapter_state cursor 갱신
```

## 4. Analysis Chart Payload Test

### 4.1 목적

분석 chart가 받을 payload가 올바른지 검증한다.

차트가 화면에 어떻게 보이는지보다 먼저, 차트를 그릴 데이터가 정확한지를 확인한다.

### 4.2 대상 API

```text
GET /api/sources/{source_id}/events/{event_id}/analysis
GET /api/sources/{source_id}/events/{event_id}/analysis/{analysis_chart_id}
```

### 4.3 검증 항목

```text
chartId
analysisChartId
chartDefinitionId
payloadAdapterKey
chartDefinition 존재
chartPayload 존재
series 데이터 존재
drift marker 존재
highlight bucket 존재
baseline/current range 존재 여부
component별 required data 존재
```

### 4.4 Snapshot 정책

chart payload는 이미지 snapshot이 아니라 JSON snapshot으로 검증한다.

원칙:

```text
stable field만 snapshot에 포함한다.
timestamp, generatedAt, jobId처럼 매 실행 달라지는 값은 normalize한다.
array order가 의미 있는 경우에만 order를 검증한다.
float 값은 tolerance를 둔다.
```

## 5. UI View-Model State Test

### 5.1 목적

브라우저에서 UI가 API 응답을 제대로 받아 내부 상태로 변환했는지 검증한다.

UI test는 pixel을 비교하지 않고, test mode에서 노출한 view-model state를 읽는다.

테스트 모드에서는 UI의 자동 live polling을 끈다. 테스트 하네스가 명시적으로 refresh를 호출할 때만 API를 다시 조회한다.

예:

```text
/sources/case-010/timeseries?testMode=1&autoPoll=0
```

### 5.2 Test State Contract

UI는 테스트 모드에서만 다음 객체를 노출한다.

```javascript
window.__DRIFT_TEST_STATE__ = {
  sourceId: "case-010",
  route: "/sources/case-010/timeseries",
  autoPollEnabled: false,
  apiLoaded: true,
  lastRenderOk: true,
  errors: [],
  pendingRequests: 0,
  pendingRenders: 0,
  lastRefreshAt: "2026-01-01T00:10:00Z",
  lastAction: "refreshTimeseries",

  timeseries: {
    pointCount: 12,
    emptyPointCount: 0,
    visibleRangeStart: "2026-01-01T00:00:00Z",
    visibleRangeEnd: "2026-01-01T02:00:00Z"
  },

  events: {
    eventCount: 1,
    visibleEventIds: ["evt-001"],
    selectedEventId: "evt-001"
  },

  analysis: {
    analysisChartIds: ["analysis-case010-adwin-stream"],
    selectedAnalysisChartId: "analysis-case010-adwin-stream",
    payloadLoaded: true
  },

  renderTargets: {
    timeseriesChartMounted: true,
    analysisChartMounted: true
  }
}
```

### 5.3 검증 항목

Playwright는 다음을 확인한다.

```text
window.__DRIFT_TEST_STATE__ 존재
autoPollEnabled = false
pendingRequests = 0
pendingRenders = 0
apiLoaded = true
lastRenderOk = true
errors.length = 0
timeseries.pointCount가 기대값 이상
events.eventCount가 기대값과 일치
selectedEventId가 기대값과 일치
analysisChartIds에 기대 chart 포함
payloadLoaded = true
chart mount target 존재
```

### 5.4 금지

다음 방식은 기본 검증으로 사용하지 않는다.

```text
전체 화면 screenshot pixel 비교
차트 색상 pixel 비교
텍스트 위치 pixel 비교
animation timing 의존
자동 live polling이 켜진 상태에서 event 클릭/analysis chart 열기
```

필요하면 대표 chart 몇 개만 visual regression test로 별도 운영한다.

## 6. UI Test Control API

### 6.1 목적

정기 polling과 테스트 조작이 충돌하지 않도록, UI는 테스트 모드에서만 명시적 제어 API를 노출한다.

운영 모드에서는 이 API를 노출하지 않는다.

### 6.2 Timeseries UI Test API

```javascript
window.__DRIFT_TEST_API__ = {
  refreshTimeseries: async () => {},
  refreshLive: async () => {},
  selectEvent: async (eventId) => {},
  openAnalysisChart: async (analysisChartId) => {},
  waitForIdle: async () => {},
  getState: () => window.__DRIFT_TEST_STATE__
}
```

요구사항:

```text
autoPoll=0이면 UI는 setInterval 기반 자동 polling을 시작하지 않는다.
refreshTimeseries는 full timeseries API를 한 번 호출한다.
refreshLive는 live delta API를 한 번 호출한다.
selectEvent는 eventId 기준으로 event 선택 상태를 만든다.
openAnalysisChart는 analysis chart panel/page를 연다.
waitForIdle은 pending network request와 render 작업이 끝날 때 resolve된다.
getState는 현재 view-model test state를 반환한다.
```

### 6.3 조작 순서

Playwright는 항상 다음 순서를 따른다.

```text
1. testMode=1&autoPoll=0으로 페이지 열기
2. waitForIdle
3. refreshTimeseries 또는 refreshLive 명시 호출
4. waitForIdle
5. selectEvent(eventId)
6. waitForIdle
7. openAnalysisChart(analysisChartId)
8. waitForIdle
9. getState로 검증
10. screenshot을 failure artifact 또는 참고용으로 저장
```

이 순서를 지키면 live update가 event list나 analysis panel을 중간에 재렌더링해서 테스트 조작과 충돌하는 문제를 줄일 수 있다.

## 7. Chart Runtime Test API

### 7.1 목적

API만으로는 analysis chart가 실제로 렌더링됐는지 알 수 없다.

따라서 chart runtime도 테스트 모드에서 렌더링 상태를 노출한다.

### 7.2 Chart Test API

```javascript
window.__CHART_TEST_API__ = {
  loadPayload: async (payload) => {},
  waitForRender: async () => {},
  getState: () => window.__CHART_TEST_STATE__
}
```

### 7.3 Chart Test State

```javascript
window.__CHART_TEST_STATE__ = {
  chartId: "CHART-STREAM-001",
  analysisChartId: "analysis-case010-adwin-stream",
  renderOk: true,
  renderError: null,
  autoPollEnabled: false,
  pendingRenders: 0,

  components: [
    {
      componentId: "main-timeseries",
      type: "line",
      mounted: true,
      dataPointCount: 120,
      visiblePointCount: 120,
      markerCount: 1,
      hasDriftMarker: true
    }
  ],

  layout: {
    width: 1280,
    height: 720,
    overflow: false,
    visibleComponentCount: 1
  }
}
```

### 7.4 검증 항목

```text
chartId 일치
analysisChartId 일치
renderOk = true
renderError = null
component mounted = true
dataPointCount > 0
drift marker 존재
layout.overflow = false
```

## 8. Browser Smoke Test

### 8.1 목적

브라우저에서 페이지가 최소한 정상 로드되고, API 호출과 렌더링이 실패하지 않는지 검증한다.

### 8.2 검증 항목

```text
페이지 로드 성공
console error 없음
network error 없음
timeseries chart container 존재
analysis chart container 존재
canvas/svg가 비어 있지 않음
test state가 기대값
```

### 8.3 Screenshot 사용 기준

Screenshot은 디버깅 artifact로 저장할 수 있다.

하지만 pass/fail 기준은 기본적으로 test state와 DOM 상태로 판단한다.

## 9. Test Case Matrix

테스트는 다음 조합으로 정의한다.

```text
dataset x adapter x drift method x analysis chart
```

v1 필수 matrix:

| ID | Dataset | Adapter | Drift Method | Analysis Chart |
| --- | --- | --- | --- | --- |
| TCASE-001 | CASE-010 stream numeric mean shift | test_db_numeric_stream | ADWIN_MEAN_STREAM | CHART-STREAM-001 |

각 test case는 다음 expected artifact를 가진다.

```text
expected_timeseries_summary.json
expected_drift_events.json
expected_analysis_payload.json
expected_ui_state.json
```

## 10. Test Harness Requirements

### 10.1 Harness 구성 원칙

Test harness는 두 층으로 나눈다.

```text
Harness Core
  scenario 실행
  서버 start/stop/status
  API 호출
  proxy/record/stub/fault injection
  artifact 저장
  contract 검증
  analyzer 실행

PyQt6 Harness UI
  Harness Core를 조작하는 관제 화면
  진행상황, API call timeline, payload, event, chart state, LLM result, failure artifact 표시
```

테스트 로직은 PyQt6 UI에 직접 넣지 않는다. Harness Core는 headless로도 실행 가능해야 한다.

### 10.2 서버 제어

Test harness는 운영 구조와 동일하게 API를 사용한다.

```text
Admin Server
Test Feeder Server
Drift Server
LLM Interpretation Server
```

단위 테스트는 service/repository를 직접 호출할 수 있다. 통합 테스트와 E2E 테스트는 API 기준으로 검증한다.

PyQt6 Harness UI는 다음을 제공한다.

```text
서버 start/stop/status
scenario 선택/실행/중지
logical time tick 진행
API call timeline 보기
request/response 보기
contract validation 결과 보기
drift event 목록 보기
analysis payload 보기
chart render state 보기
LLM result 보기
failure artifact 열기
```

### 10.3 Harness Proxy

복잡한 서버 간 contract를 검증하기 위해 Harness Proxy를 지원한다.

구조:

```text
A Server
  -> Harness Proxy for B
  -> Real B Server
```

예:

```text
Admin Server
  DRIFT_SERVER_BASE_URL=http://127.0.0.1:8801/proxy/drift

Harness Proxy
  -> http://127.0.0.1:8771
```

Harness Proxy 책임:

```text
request 기록
request schema 검증
real server로 forward
response 기록
response schema 검증
latency 측정
correlation_id 부여
scenario step과 API call 연결
오류/timeout/delay/malformed response 주입
```

Proxy는 관찰, 기록, contract 검증, 오류 주입을 위한 도구다. 운영 동작 자체를 바꾸는 주체가 되면 안 된다.

### 10.4 Test Mode A-D

테스트 하네스는 다음 네 가지 모드를 지원한다.

| Mode | 이름 | 설명 | 목적 |
| --- | --- | --- | --- |
| A | Direct Mode | 서버들이 서로 직접 호출한다. Harness는 외부에서 실행/조회만 한다. | 운영 구조와 가장 가까운 end-to-end 검증 |
| B | Proxy Record Mode | 서버 간 호출을 Harness Proxy가 중계하고 기록한다. | contract, request/response, latency, payload 흐름 검증 |
| C | Stub Mode | 특정 downstream 서버 대신 Harness가 fake response를 반환한다. | 호출 서버의 contract 준수와 오류 처리 검증 |
| D | Fault Injection Mode | Harness Proxy가 timeout, 500, delay, malformed response를 주입한다. | 장애/지연/비정상 응답 처리 검증 |

모드별 원칙:

```text
Mode A는 반드시 유지한다. Proxy가 실제 통신 문제를 가리는 것을 방지한다.
Mode B는 contract와 artifact 추적의 기본 모드로 사용한다.
Mode C는 downstream 서버 없이 caller를 독립 검증할 때 사용한다.
Mode D는 복구/오류 처리 요구사항 검증에 사용한다.
```

### 10.5 시간 제어

실제 시간을 기다리지 않는다.

```text
Harness Clock이 startTime, endTime, tickIntervalMinutes를 가진다.
Harness가 시작되면 logicalNow는 tickIntervalMinutes 단위로만 전진한다.
Harness 내부 TimeDispatcher는 매 tick마다 변경된 logicalNow를 서버 API 요청에 포함한다.
10 logical minutes 경계는 collector poll-once 대상이다.
```

테스트 흐름:

```text
1. run reset
2. source/adapter/method/chart 등록
3. Harness Clock이 다음 logicalNow 생성
4. TimeDispatcher가 logicalNow를 포함해 feeder tick 호출
5. 10분 경계에서 TimeDispatcher가 logicalNow를 포함해 poll-once 호출
6. API 결과 검증
7. UI test state 검증
```

### 10.6 UI 제어

Test harness는 운영 UI의 자동 polling에 의존하지 않는다.

```text
timeseries UI는 testMode=1&autoPoll=0으로 연다.
analysis chart runtime도 testMode=1&autoPoll=0으로 연다.
하네스가 refresh/select/open/loadPayload를 명시적으로 호출한다.
각 조작 사이에 waitForIdle 또는 waitForRender를 호출한다.
```

### 10.7 Artifact 저장

Harness Core는 run_id 기준으로 모든 산출물을 저장한다.

예:

```text
testing/runs/{run_id}/
  run_manifest.json
  scenario_steps.json
  api_calls/
  proxy_calls/
  timeseries/
  events/
  analysis_payloads/
  chart_test_state/
  ui_state/
  llm/
  browser/
  validation_report.json
```

PyQt6 Harness UI는 저장된 artifact를 조회하고 비교할 수 있어야 한다.

테스트 결과는 운영 DB, `drift_server` schema, `test_source` schema에 저장하지 않는다. v1에서는 파일 artifact 저장소를 사용한다.

## 11. Test Result Storage

### 11.1 저장 위치

테스트 결과는 다음 위치에 저장한다.

```text
testing/runs/
  index.jsonl
  {run_id}/
```

`run_id`는 시간, scenario, mode를 포함해 사람이 식별 가능하게 만든다.

예:

```text
20260701_143000_case010_modeB
```

### 11.2 Run Directory 구조

```text
testing/runs/
  20260701_143000_case010_modeB/
    run_manifest.json
    scenario_steps.json
    validation_report.json
    summary.md

    api_calls/
    proxy_calls/
    timeseries/
    events/
    analysis_payloads/
    chart_test_state/
    ui_state/
    llm/
    browser/
    logs/
```

### 11.3 파일 역할

```text
run_manifest.json
  run_id, scenario_id, mode, server URLs, git/version info, started_at, config

scenario_steps.json
  단계별 실행 상태, started_at, finished_at, status, error

validation_report.json
  contract 검증 결과, expected/actual 비교 결과, pass/fail 요약

summary.md
  사람이 읽는 요약 리포트
```

세부 디렉터리:

```text
api_calls/
  Admin/Drift/TestFeeder/LLM API 직접 호출 request/response

proxy_calls/
  Mode B-D에서 Harness Proxy가 기록한 request/response

timeseries/
  timeseries-data, timeseries-live response snapshot

events/
  drift_event 목록, event detail

analysis_payloads/
  event별 analysis chart payload JSON

chart_test_state/
  window.__CHART_TEST_STATE__ 저장

ui_state/
  window.__DRIFT_TEST_STATE__ 저장

llm/
  LLM request, response, job result

browser/
  screenshot, console log, network failure log

logs/
  server start/stop log, harness log
```

### 11.4 Run Index

PyQt6 Harness UI가 과거 run을 빠르게 조회할 수 있도록 `index.jsonl`을 둔다.

한 줄에 하나의 run metadata를 기록한다.

예:

```json
{"runId":"20260701_143000_case010_modeB","scenarioId":"TCASE-001","mode":"B","status":"failed","startedAt":"2026-07-01T14:30:00+09:00","durationMs":82341,"summaryPath":"20260701_143000_case010_modeB/summary.md"}
```

### 11.5 저장 원칙

```text
상세 결과는 파일 artifact로 저장한다.
운영 DB schema와 테스트 결과 schema를 섞지 않는다.
실패한 run은 폴더째 보관할 수 있어야 한다.
CI에서는 runs/{run_id} 폴더를 artifact로 업로드할 수 있어야 한다.
매 실행마다 summary.md와 validation_report.json을 생성한다.
```

## 12. Failure Artifact

테스트 실패 시 다음 artifact를 저장한다.

```text
API response JSON
analysis payload JSON
UI test state JSON
chart test state JSON
browser console log
network failure log
screenshot
```

Screenshot은 원인 분석용이지 기본 판정 기준이 아니다.

## 13. Acceptance Criteria

| ID | 기준 |
| --- | --- |
| TEST-AC-001 | CASE-010 API contract test가 브라우저 없이 통과한다. |
| TEST-AC-002 | CHART-STREAM-001 analysis payload JSON snapshot test가 통과한다. |
| TEST-AC-003 | UI가 테스트 모드에서 `window.__DRIFT_TEST_STATE__`를 노출한다. |
| TEST-AC-004 | Playwright가 screenshot 비교 없이 UI state를 검증할 수 있다. |
| TEST-AC-005 | Browser smoke test가 console/network error 없이 통과한다. |
| TEST-AC-006 | 실패 시 API response, payload, UI state, console log, screenshot이 artifact로 남는다. |
| TEST-AC-007 | 테스트 모드에서 timeseries UI의 자동 polling을 끌 수 있다. |
| TEST-AC-008 | Playwright가 `window.__DRIFT_TEST_API__`로 refresh/select/open을 명시적으로 제어할 수 있다. |
| TEST-AC-009 | Chart runtime이 `window.__CHART_TEST_STATE__`로 렌더링 상태를 노출한다. |
| TEST-AC-010 | Harness Core는 PyQt6 UI 없이 headless로 scenario를 실행할 수 있다. |
| TEST-AC-011 | PyQt6 Harness UI는 서버 제어, scenario 실행, API timeline, artifact 조회를 제공한다. |
| TEST-AC-012 | Harness Proxy는 request/response 기록과 schema 검증을 수행한다. |
| TEST-AC-013 | Mode A Direct Mode로 proxy 없는 end-to-end 검증을 수행할 수 있다. |
| TEST-AC-014 | Mode B Proxy Record Mode로 서버 간 contract와 payload 흐름을 기록할 수 있다. |
| TEST-AC-015 | Mode C Stub Mode로 downstream fake response를 주입할 수 있다. |
| TEST-AC-016 | Mode D Fault Injection Mode로 timeout/500/delay/malformed response를 주입할 수 있다. |
| TEST-AC-017 | 테스트 결과는 `testing/runs/{run_id}`에 파일 artifact로 저장된다. |
| TEST-AC-018 | `testing/runs/index.jsonl`에 run metadata가 append된다. |
| TEST-AC-019 | 각 run은 `run_manifest.json`, `scenario_steps.json`, `validation_report.json`, `summary.md`를 생성한다. |
| TEST-AC-020 | PyQt6 Harness UI가 `index.jsonl`을 읽어 과거 run과 artifact를 조회할 수 있다. |

## 14. 구현 원칙

```text
테스트는 chart 이미지를 맞히는 것이 아니라 chart에 들어간 데이터와 UI 상태를 검증한다.
많은 chart/method 조합은 JSON contract와 snapshot으로 자동화한다.
브라우저는 최종 smoke와 state 확인에만 사용한다.
테스트 모드 UI에서는 자동 polling을 끄고 하네스가 명시적으로 refresh한다.
테스트 결과는 운영 DB가 아니라 runs/{run_id} 파일 artifact로 저장한다.
```
