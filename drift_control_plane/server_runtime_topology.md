# Server Runtime Topology

## 1. 목적

이 문서는 drift monitoring 시스템을 실행할 때 각 서버를 어떤 프로세스, 포트, 실행 스크립트, 환경 변수로 분리할지 정리한다.

핵심 결정은 다음이다.

```text
Admin Server, Drift Server, Test Feeder Server, LLM Interpretation Server는 별도 서버 프로세스로 분리한다.
Chart Builder는 이 control plane의 직접 실행/호출 대상이 아니며, chart catalog와 runtime payload template은 파일 artifact로 참조한다.
```

서버가 작아 보이는 단계에서도 한 프로세스 안에 합치지 않는다. API 경계가 구현 초기부터 고정되어야 이후 데이터 소스, drift method, chart, 테스트 하네스가 늘어날 때 구조가 흔들리지 않는다.

## 2. 서버 목록

아래 실행 스크립트 경로는 `drift_control_plane/` 루트 기준 상대경로다.

| 서버 | 기본 포트 | 기본 Base URL | 실행 스크립트 | 역할 |
| --- | ---: | --- | --- | --- |
| Admin Server | 8770 | `http://127.0.0.1:8770` | `admin_server/run_admin_server.cmd` | source/adapter/method/chart 등록, 테스트 모드 orchestration |
| Drift Server | 8771 | `http://127.0.0.1:8771` | `drift_server/run_drift_server.cmd` | adapter polling, bucket 생성, drift method 실행, event/timeseries/analysis API |
| Test Feeder Server | 8772 | `http://127.0.0.1:8772` | `test_feeder_server/run_test_feeder_server.cmd` | 테스트 CSV를 logical time 기준으로 `test_source` DB에 적재 |
| LLM Interpretation Server | 8767 | `http://127.0.0.1:8767` | `llm_interpretation_server/run_interpretation_server.cmd` | chart payload 기반 자연어 해석 job 생성/조회 |

Chart Builder 산출물은 이 폴더에서 직접 서버로 호출하지 않는다. Admin/Drift는 등록 시 전달된 `chartDefinition` snapshot, `chart_runtime/payloads/runtime_chart_payloads.json`, `drift 보고서/charts/method_data.js`를 기준으로 동작한다.

Admin Server는 `drift_metric_timeseries/web`을 `/admin/timeseries` 아래 정적 파일로 serve한다. 따라서 control plane 통합 실행 기준 timeseries UI URL은 `http://127.0.0.1:8770/admin/timeseries/drift_metric_timeseries_demo.html?...` 형식이다. 이 URL은 Drift API proxy용 `apiBase=http://127.0.0.1:8770`과 LLM job proxy용 `llmJobEndpoint=http://127.0.0.1:8770/api/admin/llm/interpret/chart/jobs`를 함께 전달한다.

### 2.1 선택적 Report Gallery Server

`http://127.0.0.1:8765` report gallery server는 필수 runtime server가 아니다. 기존 `drift 보고서` gallery server가 이미 떠 있으면 Admin Server의 `GET /api/admin/report/gallery-data`가 우선 조회할 수 있는 선택적 보조 소스다.

해당 서버가 없거나 응답에 실패하면 Admin Server는 `drift 보고서/charts/method_data.js`를 직접 읽어 fallback catalog를 만든다. 따라서 `run_all_servers.cmd`와 `run_all_servers.ps1`은 8765 report gallery server를 시작하지 않는다.

## 3. 포트 정책

기본 포트는 다음 범위를 사용한다.

```text
8767: 기존 LLM Interpretation Server
8765: 선택적 기존 Report Gallery Server. 필수 서버가 아니며 전체 실행 스크립트가 시작하지 않음
8770: 신규 Admin Server
8771: 신규 Drift Server
8772: 신규 Test Feeder Server
```

신규 서버는 `8770` 이후를 사용한다. 기존 서버의 기본 포트와 충돌하지 않게 Admin/Drift/Test Feeder를 배치한다.

포트가 이미 사용 중이면 운영자가 환경 변수로 override할 수 있다. 단, 문서와 기본 실행 스크립트의 기준 포트는 위 표를 따른다.

## 4. 환경 변수

### 4.1 서버 포트

```text
ADMIN_SERVER_PORT=8770
DRIFT_SERVER_PORT=8771
TEST_FEEDER_SERVER_PORT=8772
LLM_INTERPRETATION_SERVER_PORT=8767
```

LLM Interpretation Server는 `LLM_INTERPRETATION_SERVER_PORT`를 표준 포트 변수로 사용한다. 기존 호환을 위해 `llm_interpretation_server`는 `CHART_INTERPRETATION_PORT`도 fallback으로 허용한다.

### 4.2 서버 간 호출 URL

Admin Server:

```text
DRIFT_SERVER_BASE_URL=http://127.0.0.1:8771
TEST_FEEDER_BASE_URL=http://127.0.0.1:8772
LLM_INTERPRETATION_BASE_URL=http://127.0.0.1:8767
REPORT_GALLERY_BASE_URL=http://127.0.0.1:8765
```

`REPORT_GALLERY_BASE_URL`은 선택적 기존 report gallery server 조회용이다. 빈 문자열로 설정하면 Admin Server는 8765 조회를 건너뛰고 곧바로 `drift 보고서/charts/method_data.js` fallback을 사용한다.

Drift Server:

```text
LLM_INTERPRETATION_BASE_URL=http://127.0.0.1:8767
```

Test Feeder Server는 다른 서버를 직접 호출하지 않는다.

### 4.3 DB 연결

```text
SQLite dev DB: drift_control_plane/runtime/sprint2_dev.sqlite3
```

DB 접근 소유권은 `database_ownership_policy.md`를 따른다.
현재 v1 dev runtime의 물리 DB 배치는 workspace-local SQLite 파일이며, 상세 내용은 `database_physical_topology.md`를 따른다.

## 5. Health Check

각 서버는 다음 health endpoint를 기준으로 한다.

| 서버 | Health endpoint |
| --- | --- |
| Admin Server | `GET /api/admin/health` |
| Drift Server | `GET /api/health` |
| Test Feeder Server | `GET /api/test-feeder/health` |
| LLM Interpretation Server | `GET /api/health` |

Admin Server는 테스트 모드를 시작하기 전에 Drift Server와 Test Feeder Server health를 확인한다.

LLM Interpretation Server가 필요한 작업에서는 해당 서버 health를 먼저 확인하고, 실패하면 해석 job 생성 요청을 중단한다.

## 6. 시작 순서

권장 시작 순서:

```text
1. DB 준비
2. LLM Interpretation Server
3. Drift Server
4. Test Feeder Server
5. Admin Server
```

Admin Server가 가장 마지막에 뜨는 것이 좋다. Admin Server는 다른 서버를 호출하는 control plane이므로, 시작 시점에 의존 서버 health를 확인할 수 있어야 한다.

## 7. 테스트 모드 제어 관계

테스트 모드에서 Admin Server는 다음을 담당한다.

```text
Admin Server
  -> Test Feeder Server start/stop/status/tick/reset 호출
  -> Drift Server adapter start/stop/status/reset 호출
  -> Drift Server source/method/chart 등록 API 호출
  -> LLM Interpretation Server interpretation job 생성 호출
```

Admin Server는 Test Feeder나 Drift Server의 내부 함수를 직접 호출하지 않는다. 항상 HTTP API client를 통해 호출한다.

Test Feeder Server는 테스트 데이터를 생성하고 `test_source` DB에 기록하는 역할만 한다. Drift Server를 직접 호출하지 않는다.

Drift Server는 adapter를 통해 source DB에서 데이터를 읽고, 자기 schema에 bucket/method_run/drift_event를 기록한다. Test Feeder Server를 직접 제어하지 않는다.

## 8. 실행 스크립트 기준

v1 실행 스크립트는 `drift_control_plane` root 기준 import를 사용한다. 여기서 root는 저장소 최상위 `drift_llm_intepretation`이 아니라 `drift_control_plane/` 디렉터리다.

전체 실행:

```text
run_all_servers.cmd
run_all_servers.ps1
```

전체 실행 스크립트는 Admin/Drift/Test Feeder와 기존 LLM Interpretation Server를 함께 실행한다.
선택적 8765 Report Gallery Server는 전체 실행 스크립트의 필수 구성에 포함하지 않는다.

개별 실행:

```text
admin_server/run_admin_server.cmd
drift_server/run_drift_server.cmd
test_feeder_server/run_test_feeder_server.cmd
```

기존 LLM 실행 스크립트는 다음을 유지한다.

```text
llm_interpretation_server/run_interpretation_server.cmd
```

Admin/Drift/Test Feeder 실행 스크립트는 `drift_control_plane` root를 current directory로 설정한 뒤 다음 entrypoint를 실행한다.

```text
admin_server.app.main:app
drift_server.app.main:app
test_feeder_server.app.main:app
```

이 기준을 쓰는 이유는 Drift Server와 Test Feeder Server가 `drift_control_plane/shared` 패키지를 import하기 때문이다. 서버 하위 폴더를 current directory로 두고 `app.main:app`을 실행하면 `shared` import가 실패할 수 있다.

LLM Interpretation Server는 기존 sibling 폴더의 서버를 사용한다.

```text
C:\Users\jklee\PycharmProjects\drift_llm_intepretation\llm_interpretation_server\interpretation_server.py
```

## 9. 구현 시 주의 사항

- 서버 간 호출은 client class로 감싼다.
- 신규 서버 응답은 `{ok,data,error}` envelope를 사용한다.
- 기존 LLM 서버 응답은 그대로 둘 수 있으며, 호출 client가 normalize한다.
- Chart Builder 서버는 이 control plane에서 직접 호출하지 않는다. Chart catalog와 runtime payload template은 파일 artifact 기준으로 읽는다.
- 테스트 자동화에서 서버 프로세스를 직접 띄우더라도 검증은 API 기준으로 한다.
- 단위 테스트는 service class를 직접 호출할 수 있지만, 서버 경계 검증은 API 테스트로 한다.
- Admin Server는 orchestration 책임만 가진다. Drift 계산, bucket 생성, feeder tick 처리는 각 서버가 수행한다.

## 10. 관련 문서

- `server_boundary_policy.md`
- `database_ownership_policy.md`
- `database_physical_topology.md`
- `api_contracts.md`
- `server_interaction_scenarios.md`
- `test_harness_architecture.md`
- `implementation_scope_v1.md`
