# Drift Server 통합 테스트 안정화 기준

이 문서는 `drift_control_plane`을 기준으로 통합 테스트를 운영할 때 테스트가 불필요하게 실패하거나 멈추지 않도록 지켜야 하는 기준을 정의한다.

통합 테스트의 목적은 단일 모듈의 내부 구현을 확인하는 것이 아니라 다음 흐름 전체가 깨지지 않았는지 확인하는 것이다.

```text
drift method 실행
  -> drift event 생성
  -> chart-method binding 선택
  -> payload adapter 변환
  -> chart_runtime payload 계약 검증
  -> timeseries UI 렌더링/상호작용 검증
```

## 1. 통합 테스트의 기준 위치

통합 테스트의 기준점은 `drift_control_plane`이다.

다른 폴더의 테스트를 실행하더라도 결과는 `drift_control_plane`의 통합 품질 기준으로 해석한다.

```text
drift_control_plane
  payload adapter 계약 테스트
  chart-method coverage 테스트
  realtime smoke 테스트
  drift_metric_timeseries browser smoke 테스트 실행 기준

drift_algorithm_impl
  drift method 단위 테스트

drift_metric_timeseries
  UI browser smoke 테스트 대상
```

## 2. 필수 테스트 묶음

통합 확인 시 최소한 다음 테스트를 실행한다.

```powershell
cd drift_control_plane
python tools\check_payload_adapter_coverage.py
python -m pytest
```

```powershell
cd ..\drift_algorithm_impl
python -m pytest tests
```

```powershell
cd ..\drift_metric_timeseries
python tests\drift_metric_timeseries_harness_test.py
python tests\drift_metric_timeseries_demo_test.py
```

```powershell
cd ..
python 테스트데이터\realtime_demo\smoke_test.py
python 테스트데이터\realtime_demo\system_smoke_test.py
```

## 3. Payload Adapter 테스트 기준

`tools/check_payload_adapter_coverage.py`는 다음을 검증해야 한다.

```text
method_data.js의 chart-method catalog를 읽는다.
runtime_chart_payloads.json의 chart template을 읽는다.
모든 chart-method 쌍이 binding으로 등록되어 있는지 확인한다.
각 binding으로 chart runtime payload를 생성한다.
component.dataBinding.source가 payload.data에 존재하는지 확인한다.
dataContracts.requiredFields가 row에 존재하는지 확인한다.
```

현재 기대값은 다음과 같다.

```text
chartCountInMethodCatalog: 53
runtimeTemplateChartCount: 53
chartMethodPairCount: 188
registeredBindingCount: 188
passedBindingPairCount: 188
failedBindingPairCount: 0
missingBindingPairCount: 0
missingRuntimeTemplateCount: 0
```

이 값이 바뀌면 단순히 테스트 숫자만 수정하지 말고 다음을 먼저 확인한다.

```text
chart catalog가 바뀌었는가?
runtime payload template이 추가/삭제되었는가?
chart-method registration이 바뀌었는가?
payload adapter binding spec이 추가/삭제되었는가?
```

## 4. Chart Runtime Payload 의미 검증 기준

chart runtime smoke 테스트의 `passed`는 단순히 JavaScript 오류 없이 component가 생성되었다는 뜻이어서는 안 된다.

앞으로 분석 chart 테스트는 다음 3단계를 모두 통과해야 한다.

```text
1. payload contract 검증
2. axis/data fit 검증
3. visual smoke 검증
```

### 4.1 Payload contract 검증

각 chart는 `payload.data` source별로 최소 row 수와 field type을 가져야 한다.

예를 들어 `CHART-PSI-001`은 다음 계약을 만족해야 한다.

```text
chart.CHART-PSI-001.summary
  최소 3개 row
  label, value 또는 displayValue 존재

chart.CHART-PSI-001.bins
  최소 2개 row
  reference: number
  current: number
  label 또는 category 존재

chart.CHART-PSI-001.contrib
  최소 1개 row
  value 또는 contribution: number

chart.CHART-PSI-001.trend
  최소 3개 row
  window: number
  psi: number

chart.CHART-PSI-001.notes
  최소 1개 row
  title 또는 text 존재
```

이 검증은 runtime renderer가 실제 의미 있는 그래프를 그릴 수 있는 입력인지 확인하기 위한 것이다.

다음 상태는 실패로 본다.

```text
line/trend chart에 row가 1개뿐인 경우
x축 field가 renderer가 요구하는 숫자형이 아닌 경우
y축 field가 숫자가 아닌 경우
bar chart의 value field가 없거나 모두 비어 있는 경우
notes만 존재하고 main/side visual data가 비어 있는 경우
```

### 4.2 Axis/data fit 검증

payload data가 chart config의 고정 축 범위 안에 들어가는지 검증해야 한다.

다음 상태는 실패로 본다.

```text
max(data.y) > config.y_max 인데 y_max가 고정되어 있는 경우
min(data.y) < config.y_min 인데 y_min이 고정되어 있는 경우
data.x가 config.x_min ~ config.x_max 밖에 있는 경우
고정 x_max 또는 y_max가 runtime sample 값에만 맞고 실제 method output을 담지 못하는 경우
bar/contribution value가 config.x_max보다 커서 막대가 화면 밖으로 나가는 경우
```

단, 의도적으로 clip을 사용하는 chart라면 chart별 contract에 clip 정책과 기대 동작을 명시해야 한다.

### 4.3 Visual smoke 검증

chart runtime smoke는 DOM component 수만 확인하면 안 된다.

component type별로 실제 SVG 요소가 존재하는지 확인해야 한다.

```text
line-like component
  path가 존재해야 한다.
  point가 2개 이상이거나 path 길이가 의미 있게 커야 한다.

bar-like component
  rect가 존재해야 한다.
  주요 rect의 width 또는 height가 0보다 충분히 커야 한다.

distribution-like component
  density, interval, box, histogram 등 핵심 도형이 존재해야 한다.

matrix/heatmap component
  cell rect 또는 cell text가 존재해야 한다.

notes component
  notes만 렌더링되고 main visual이 비어 있으면 실패해야 한다.
```

가능하면 screenshot 기반으로 chart area의 non-background pixel 비율도 확인한다.
예를 들어 main/side visual area가 거의 흰색 배경만 가지고 있으면 `rendered`가 아니라 `visually_empty`로 분류한다.

### 4.4 Auto adapter 사용 시 추가 검증

`auto__...` payload adapter는 chart template의 component field를 보고 transform을 추론한다.
따라서 runtime 오류 없이 payload를 만들 수 있어도 method 의미와 맞지 않을 수 있다.

auto adapter를 사용하는 chart-method 쌍은 반드시 다음을 추가 확인한다.

```text
chart별 data source가 기대 transform으로 매핑되었는가?
trend/timeline/summary/contribution이 서로 뒤섞이지 않았는가?
method output의 핵심 지표가 chart의 핵심 visual area에 들어갔는가?
runtime template의 sample용 고정 축이 실제 method output을 가리지 않는가?
```

대표 사례:

```text
NUMERIC_BINNED_PSI + CHART-PSI-001
  trend source는 event_timeline이 아니라 psi_trend여야 한다.
  trend.window는 숫자여야 한다.
  trend.psi는 숫자여야 한다.
  PSI score가 sample y_max를 넘으면 축을 동적으로 조정해야 한다.
```

### 4.5 Harness 결과 해석 기준

앞으로 `chartRuntimeSmokeStatus=passed`는 다음을 모두 의미해야 한다.

```text
component가 렌더링되었다.
payload data source와 required field가 존재한다.
chart별 semantic contract를 만족한다.
data가 축 범위 안에 들어간다.
주요 visual component가 실제 도형을 그렸다.
screenshot이 생성되었고 주요 chart area가 비어 있지 않다.
```

이 중 일부만 확인한 경우에는 `passed` 대신 더 좁은 상태명을 사용한다.

```text
rendered_only
contract_passed
axis_fit_passed
visual_passed
visually_empty
```

## 5. Browser Smoke 테스트 작성 기준

브라우저 테스트는 실제 UI 렌더링을 확인하되, 불필요하게 Playwright actionability 대기에 묶이면 안 된다.

### 5.1 정적 테스트와 live 테스트를 분리한다

정적 UI smoke 테스트는 live polling에 의존하지 않는다.

```text
정적 테스트: drift_metric_timeseries_demo.html?live=0
live 테스트: realtime_demo smoke/system smoke 또는 별도 live browser test
```

정적 테스트에서 live mode를 기본값으로 사용하면 다음 문제가 생긴다.

```text
초기 fullDomain이 live window로 축소된다.
초기 event list가 비어 있을 수 있다.
polling 타이밍에 따라 테스트 결과가 흔들린다.
```

따라서 `drift_metric_timeseries_demo_test.py` 같은 정적 browser smoke 테스트는 반드시 `?live=0`을 명시한다.

### 5.2 전체 state를 브라우저 밖으로 가져오지 않는다

Playwright에서 다음처럼 큰 객체 전체를 가져오면 테스트가 느려지거나 멈출 수 있다.

```python
page.evaluate("() => window.driftMetricTimeseriesDemo.getState()")
```

대신 필요한 조각만 가져온다.

```python
page.evaluate("() => window.driftMetricTimeseriesDemo.getState().time")
page.evaluate("() => window.driftMetricTimeseriesDemo.getState().view")
```

특히 timeseries data, dataStore, chart payload, render model 전체를 반복적으로 Python으로 가져오는 것은 피한다.

### 5.3 UI 설정 변경은 공개 dispatch API를 우선 사용한다

range, scale, primary feature 같은 상태 변경은 UI button click보다 공개 dispatch API를 우선 사용한다.

```python
page.evaluate(
    "action => window.driftMetricTimeseriesDemo.dispatch(action)",
    {"type": "SET_RANGE_PRESET", "preset": "7D"},
)
```

브라우저 click으로만 검증해야 하는 대상은 다음처럼 실제 상호작용 자체가 테스트 목적일 때로 제한한다.

```text
event item click
navigator drag/click
tooltip hover
dialog open/close
responsive overflow
```

이렇게 구분하지 않으면 dialog, hidden panel, disabled button, animation 때문에 테스트가 불필요하게 실패하거나 대기할 수 있다.

### 5.4 hidden/disabled UI를 클릭하지 않는다

설정 dialog 안에 있는 control은 dialog가 열린 상태에서만 클릭 가능하다.

테스트에서 control을 클릭해야 한다면 다음을 먼저 확인한다.

```text
configDialog가 열려 있는가?
대상 button이 visible인가?
대상 button이 disabled가 아닌가?
현재 scale/range 조합에서 해당 button이 허용되는가?
```

비활성화 동작을 검증할 때는 Playwright `click()`이 actionability 대기를 하므로 주의한다.
비활성 button 클릭이 무시되는지를 확인하려면 DOM click 또는 dispatch 불가 조건 검증을 사용한다.

### 5.5 테스트 데이터 날짜를 하드코딩할 때는 source fixture와 함께 갱신한다

테스트 데이터의 `fullDomain`, event window, missing/partial/closed/imputed 구간이 바뀌면 날짜 기반 테스트도 같이 바뀌어야 한다.

예를 들어 다음 검증은 테스트 데이터와 강하게 결합되어 있다.

```text
embedding drift event window
missing bucket window
imputed bucket window
partial bucket window
closed bucket window
```

날짜를 직접 하드코딩할 경우 문서 또는 주석에 어떤 fixture 구간을 전제로 하는지 남긴다.
가능하면 `getState().dataStore.byFeature[feature].events` 또는 series status에서 구간을 찾아 검증한다.

### 5.6 Browser smoke 테스트는 빠르게 실패해야 한다

브라우저 테스트는 한 지점에서 30초 이상 대기하면 원인 파악이 어렵다.

권장 기준:

```python
page.set_default_timeout(5000)
```

긴 대기가 필요한 경우에는 이유를 주석으로 남긴다.

## 6. Realtime smoke 테스트 기준

`테스트데이터/realtime_demo` 테스트는 UI browser smoke와 다른 목적을 가진다.

검증 대상:

```text
minute data replay
hourly aggregation
drift event 생성
analysis payload 생성
CHART-STREAM-001 연결
```

기대값 예:

```text
hourly_count: 336
event_count >= 1
analysis_chart: CHART-STREAM-001
adapter: adwin_mean_stream_to_chart_stream_001
```

이 테스트는 live 흐름 검증이고, 정적 UI 테스트를 대체하지 않는다.

## 7. 실패 시 판단 순서

통합 테스트가 실패하면 다음 순서로 판단한다.

```text
1. 실제 계약이 깨졌는가?
   chartId, payload.data source, requiredFields, method event contract 확인

2. 테스트 fixture가 바뀌었는가?
   fullDomain, event window, status bucket 구간 확인

3. browser test가 UI 상태를 잘못 전제했는가?
   live/static mode, dialog open 상태, hidden/disabled control 확인

4. Playwright가 큰 객체 변환이나 actionability 대기에 걸렸는가?
   getState 전체 조회, locator click, get_attribute 대기 확인

5. 기대값만 오래되었는가?
   테스트 데이터를 기준으로 기대 날짜/카운트를 갱신
```

실패를 없애기 위해 검증 자체를 제거해서는 안 된다.
대신 검증 대상을 다음처럼 분리한다.

```text
계약 검증: drift_server pytest / payload adapter coverage
계산 검증: drift_algorithm_impl pytest
정적 UI 검증: drift_metric_timeseries demo/harness with live=0
live 흐름 검증: realtime_demo smoke/system smoke
```

## 8. 이번 실패에서 확정한 규칙

이번 테스트 안정화 과정에서 확정한 규칙은 다음과 같다.

```text
drift_metric_timeseries_demo_test.py는 정적 테스트이므로 ?live=0을 사용한다.
Playwright에서 getState() 전체를 가져오지 않는다.
range/scale 변경은 dispatch API를 사용한다.
event click, navigator drag, tooltip hover처럼 실제 UI 상호작용이 목적일 때만 click/mouse를 사용한다.
날짜 기대값은 현재 fixture의 fullDomain/event/status window와 맞아야 한다.
```

이 규칙을 어기면 테스트가 실제 버그가 없어도 멈추거나 실패할 가능성이 높다.
