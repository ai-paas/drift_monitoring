# Test Harness Implementation Design

## 1. 목적

테스트 하네스는 `drift_control_plane/api_contracts.md`에 정의된 서버 간 contract를 실제 실행 흐름에서 검증한다.

v1의 첫 목표는 다음이다.

```text
Headless Mode A로 CASE-010을 실행하고, API 호출 결과와 실패 원인을 runs/{run_id} artifact로 남긴다.
```

PyQt6 UI와 Harness Proxy는 그 다음 단계다. 테스트 로직은 UI에 넣지 않고, 항상 Harness Core가 소유한다.

## 2. 구현 원칙

```text
Harness Core는 headless로 실행 가능해야 한다.
PyQt6 UI는 Harness Core를 조작하는 관제 화면이다.
운영 서버 코드는 하네스에 의존하지 않는다.
서버 간 경계는 HTTP API contract로 검증한다.
테스트 결과는 운영 DB가 아니라 testing/runs/{run_id}에 저장한다.
테스트 모드의 시간 source of truth는 Harness Clock이다.
```

## 3. 모듈 구조

```text
drift_control_plane/testing/
  README.md
  test_requirements.md
  test_harness_implementation_design.md

  harness/
    __init__.py
    main.py
    config.py
    models.py
    harness_clock.py
    time_dispatcher.py
    scenario_runner.py
    artifact_store.py
    contract_validator.py

    clients/
      __init__.py
      http_client.py
      admin_client.py
      drift_client.py
      test_feeder_client.py

    scenarios/
      case010_mode_a.json

  runs/
    index.jsonl
    {run_id}/
```

후속 단계에서 추가할 모듈:

```text
harness/proxy/
  app.py
  router.py
  recorder.py
  stub_registry.py
  fault_rules.py

harness/ui/
  pyqt_app.py
  main_window.py
```

## 4. 핵심 컴포넌트

### 4.1 ScenarioRunner

`ScenarioRunner`는 하네스 실행의 중심이다.

책임:

```text
scenario 파일 로드
clock config 로드
run_id 생성
run artifact 폴더 생성
API client 초기화
scenario step 순차 실행
HarnessClock과 TimeDispatcher 호출
contract validation 호출
artifact 저장
summary.md, validation_report.json 생성
```

ScenarioRunner가 직접 시간을 생성하거나 서버에 시간을 전송하지 않는다. ScenarioRunner는 시나리오 단계 흐름을 조율하고, 시간 생성은 HarnessClock에, 시간 전송은 TimeDispatcher에 위임한다.

### 4.2 API Clients

서버별 client는 `api_contracts.md`의 endpoint를 감싼다.

```text
AdminClient
  /api/admin/...

DriftClient
  /api/health
  /api/drift/...
  /api/sources/...

TestFeederClient
  /api/test-feeder/...
```

v1 하네스는 표준 라이브러리 `urllib`만 사용한다. 응답은 `{ok,data,error}` envelope 기준으로 정규화하고, 호출 원문은 artifact에 저장한다.

### 4.3 ArtifactStore

모든 실행 결과는 `runs/{run_id}` 아래에 저장한다.

```text
run_manifest.json
scenario_steps.json
validation_report.json
summary.md

api_calls/
timeseries/
events/
analysis_payloads/
logs/
```

`runs/index.jsonl`에는 run metadata를 append한다.

### 4.4 ContractValidator

첫 버전에서는 lightweight validation만 수행한다.

검증 항목:

```text
HTTP 호출 성공 여부
JSON parse 가능 여부
신규 서버 envelope의 ok/data/error 필드 존재 여부
scenario에서 지정한 required path 존재 여부
```

후속 단계에서 JSON Schema 기반 검증으로 확장한다.

### 4.5 Harness Clock

Harness Clock은 테스트 모드의 기준 시계다.

config:

```text
startTime
endTime
tickIntervalMinutes
```

규칙:

```text
logicalNow는 startTime에서 시작한다.
Harness가 시작되면 logicalNow는 tickIntervalMinutes 단위로만 전진한다.
각 tick은 previousLogicalNow와 logicalNow를 가진다.
서버는 테스트 모드에서 자기 clock을 임의로 전진시키지 않는다.
모든 tick 요청과 관련 API call artifact에는 logicalNow를 기록한다.
```

HarnessClock은 시간을 만들기만 한다. 서버 API 호출은 하지 않는다.

### 4.6 TimeDispatcher

TimeDispatcher는 HarnessClock이 만든 tick을 서버에 전송한다.

입력:

```text
previousLogicalNow
logicalNow
tickIntervalMinutes
tickIndex
```

책임:

```text
Test Feeder Server에 logicalNow tick 전송
10분 logicalNow 경계에서 Drift Server poll-once 호출
필요한 경우 Admin Server에 test status용 logicalNow 통지
각 API call artifact에 logicalNow 기록
```

TimeDispatcher는 시간을 계산하지 않는다. 이미 생성된 HarnessClock tick을 서버별 API 요청으로 변환한다.

## 5. Headless Mode A 실행 흐름

Mode A는 proxy 없이 서버들이 직접 통신하는 방식이다. 하네스는 외부에서 API를 호출하고 결과를 기록한다.

```text
1. ScenarioRunner가 case010_mode_a.json을 읽는다.
2. run_id를 만들고 runs/{run_id}/ 폴더를 만든다.
3. Admin, Drift, Test Feeder health를 확인한다.
4. Admin test reset을 호출한다.
5. Test Feeder에 CASE-010 feeder를 등록한다.
6. Admin에 source를 등록한다.
7. Admin에 adapter를 등록한다.
8. Admin에 method assignment를 등록한다.
9. Admin에 analysis chart를 등록한다.
10. ScenarioRunner가 HarnessClock에 다음 tick을 요청한다.
11. HarnessClock이 next tick의 logicalNow를 반환한다.
12. TimeDispatcher가 logicalNow를 Test Feeder Server에 전송한다.
13. 10분 경계마다 TimeDispatcher가 logicalNow를 Drift Server poll-once에 전송한다.
14. Drift Server timeseries API를 조회한다.
15. event가 있으면 analysis payload API를 조회한다.
16. contract validation 결과를 기록한다.
17. summary.md와 validation_report.json을 생성한다.
```

서버가 아직 없거나 endpoint가 미구현이면 해당 단계에서 실패하고, 실패 response와 exception을 artifact로 남긴다.

## 6. CASE-010 Scenario

CASE-010은 stream numeric mean shift 데이터셋을 사용한다.

기본 식별자:

```text
sourceId: case-010
datasetCaseId: CASE-010
adapterId: case-010-adwin
assignmentId: assign-case010-adwin
analysisChartId: analysis-case010-adwin-stream
chartId: CHART-STREAM-001
runtimeMethodKey: adwin_mean_stream
payloadAdapterKey: adwin_mean_stream_to_chart_stream_001
```

기본 clock:

```text
startTime: 2026-01-01T00:00:00Z
endTime: 2026-01-01T00:20:00Z
tickIntervalMinutes: 1
pollEveryMinutes: 10
```

Harness가 생성하는 tick 예:

```json
{
  "previousLogicalNow": "2026-01-01T00:09:00Z",
  "logicalNow": "2026-01-01T00:10:00Z",
  "tickIntervalMinutes": 1,
  "tickIndex": 10
}
```

## 7. Mode B-D 확장 지점

Mode B-D는 같은 `ScenarioRunner`를 사용하되 URL 배선만 바꾼다.

```text
Mode A
  Admin -> Drift/TestFeeder 직접 호출
  Harness -> 각 서버 직접 호출

Mode B
  Admin/Drift의 downstream base URL을 Harness Proxy로 설정
  Harness Proxy가 실제 서버로 forward하고 request/response 기록

Mode C
  Harness Proxy가 특정 downstream 응답을 stub으로 반환

Mode D
  Harness Proxy가 timeout, 500, delay, malformed response를 주입
```

따라서 첫 구현에서 `ScenarioRunner`, `ArtifactStore`, `ContractValidator`, API client를 잘 분리해두면 Mode B-D를 추가해도 테스트 시나리오 자체는 크게 바뀌지 않는다.

## 8. 구현 순서

```text
TH-01 문서와 harness 패키지 생성
TH-02 ArtifactStore 구현
TH-03 API client 구현
TH-04 ContractValidator 구현
TH-05 ScenarioRunner Mode A 구현
TH-06 CASE-010 scenario 파일 작성
TH-07 실제 실행 시 runs/{run_id} artifact 생성 확인
TH-08 서버 구현이 붙으면 CASE-010 성공 조건 강화
TH-09 Harness Proxy Mode B 추가
TH-10 PyQt6 Harness UI 추가
```

## 9. 완료 기준

Headless Mode A의 1차 완료 기준:

```text
python -m testing.harness.main --scenario testing/harness/scenarios/case010_mode_a.json
```

위 명령이 다음을 수행해야 한다.

```text
runs/{run_id} 생성
run_manifest.json 생성
scenario_steps.json 생성
api_calls/*.json 생성
validation_report.json 생성
summary.md 생성
runs/index.jsonl append
```

서버가 준비되어 있지 않으면 성공으로 처리하지 않는다. 대신 어느 서버/endpoint에서 실패했는지 artifact로 남긴다.
