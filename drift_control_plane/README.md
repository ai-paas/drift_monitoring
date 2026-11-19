# Drift Control Plane

This folder contains the control plane for drift monitoring servers.

It groups the executable servers and shared test harness around the actual `drift_server` application package.

## Naming

이 저장 영역에서는 `drift_control_plane`과 `drift_server`를 다음처럼 구분한다.

```text
drift_control_plane/
  서버 묶음과 통합 테스트를 관리하는 control-plane 루트

drift_control_plane/drift_server/
  실제 Drift Server 애플리케이션 패키지

drift_server
  문맥에 따라 내부 Python package, API server 이름, 또는 DB schema 이름
```

문서에서 상위 루트를 말할 때는 `drift_control_plane`이라고 쓰고, 실제 앱 코드를 말할 때만 `drift_server/app/...` 또는 `drift_control_plane/drift_server/app/...`라고 쓴다.

Responsibilities:

- run and coordinate `admin_server`, `drift_server`, and `test_feeder_server`
- manage shared contracts, test harnesses, and integration smoke tests
- keep drift method runtime, event, timeseries, and chart payload contracts together
- expose the actual Drift Server app under `drift_server/`

## Implementation Reading Order

구현할 때는 아래 문서를 먼저 본다.

1. [implementation_scope_v1.md](./implementation_scope_v1.md): v1에서 구현할 것과 제외할 것
2. [development_phases_v1.md](./development_phases_v1.md): v1 구현 phase와 단계별 완료 기준
3. [개발 방법론.md](./개발%20방법론.md): Harness Iteration 기반 개발 방식
4. [계획/README.md](./계획/README.md): 단계별 상세 계획 문서 목록
5. [server_runtime_topology.md](./server_runtime_topology.md): 서버 프로세스, 포트, 실행 스크립트
6. [api_contracts.md](./api_contracts.md): endpoint 목록과 request/response schema의 source of truth
7. [api_ownership_and_call_routing.md](./api_ownership_and_call_routing.md): caller, downstream routing, 저장 책임
8. [data_source_event_schema.md](./data_source_event_schema.md): drift_server/test_source 핵심 테이블
9. [internal_implementation_design.md](./internal_implementation_design.md): 폴더 구조와 service/repository 구현 방향

## Source Of Truth

문서가 겹칠 때는 다음 기준을 따른다.

| 관심사 | 기준 문서 |
| --- | --- |
| v1 포함/제외 범위 | [implementation_scope_v1.md](./implementation_scope_v1.md) |
| v1 개발 단계 | [development_phases_v1.md](./development_phases_v1.md) |
| 개발 방법론 | [개발 방법론.md](./개발%20방법론.md) |
| 단계별 상세 계획 | [계획/README.md](./계획/README.md) |
| Sprint 1 계획 | [계획/sprint_1/README.md](./계획/sprint_1/README.md) |
| V0-V5 전체 로드맵 | [계획/V0-V5_전체_로드맵.md](./계획/V0-V5_전체_로드맵.md) |
| API endpoint와 payload | [api_contracts.md](./api_contracts.md) |
| API 호출 방향과 DB write owner | [api_ownership_and_call_routing.md](./api_ownership_and_call_routing.md) |
| 시나리오별 호출 흐름 | [server_interaction_scenarios.md](./server_interaction_scenarios.md) |
| DB/schema 설계 | [data_source_event_schema.md](./data_source_event_schema.md), [database_ownership_policy.md](./database_ownership_policy.md), [database_physical_topology.md](./database_physical_topology.md) |
| 테스트 reset | [reset_policy.md](./reset_policy.md) |
| 테스트 자동화 전략 | [testing/test_requirements.md](./testing/test_requirements.md) |
| 테스트 하네스 구현 구조 | [testing/test_harness_implementation_design.md](./testing/test_harness_implementation_design.md) |

## Design Notes

- [test_harness_architecture.md](./test_harness_architecture.md): test DB, test feeder, adapter registration, admin orchestration, and accelerated logical-time harness design
- [integrated_test_stability_policy.md](./integrated_test_stability_policy.md): integrated test bundle, browser smoke stability rules, and failure triage policy
- [testing/test_requirements.md](./testing/test_requirements.md): API/payload/view-model/browser smoke test requirements and automation strategy
- [testing/test_harness_implementation_design.md](./testing/test_harness_implementation_design.md): test harness module structure, Mode A flow, and extension points for Mode B-D
- [drift_server_ui_and_api.md](./drift_server_ui_and_api.md): data source list, source-specific timeseries URL, bucket/event APIs, and UI relationship
- [data_source_event_schema.md](./data_source_event_schema.md): data source, adapter, bucket, method run, drift event, analysis chart, and payload adapter table relationships
- [time_and_cursor_model.md](./time_and_cursor_model.md): event time, inserted time, source cursor, poll tick, empty window, and catch-up rules
- [test_feeder_contract.md](./test_feeder_contract.md): test CSV replay, feed state, tick, inserted_at, raw_event, and CASE-010 mapping contract
- [source_adapter_contract.md](./source_adapter_contract.md): source adapter fetch/normalization contract and collector aggregation responsibility
- [idempotency_and_locking.md](./idempotency_and_locking.md): adapter poll locking and idempotency rules for bucket, method run, and drift event creation
- [drift_method_runtime_contract.md](./drift_method_runtime_contract.md): runtime input/output contract for stateful streaming and lookback drift methods
- [drift_event_model.md](./drift_event_model.md): drift event lifecycle, deduplication, severity, time range, payload, and analysis chart linkage
- [timeseries_api_contract.md](./timeseries_api_contract.md): source feature, full timeseries, live delta, series point, empty bucket, and event marker response contract
- [analysis_payload_adapter_contract.md](./analysis_payload_adapter_contract.md): event analysis context and chart runtime payload adapter input/output contract
- [reset_policy.md](./reset_policy.md): test reset modes and deletion/preservation rules for run, source, and hard reset
- [api_response_policy.md](./api_response_policy.md): response envelope, error object, HTTP status, and client normalization rules
- [implementation_scope_v1.md](./implementation_scope_v1.md): v1 CASE-010 vertical-slice scope, exclusions, and acceptance criteria
- [development_phases_v1.md](./development_phases_v1.md): v1 implementation phases, phase outputs, and completion criteria
- [개발 방법론.md](./개발%20방법론.md): Harness Iteration method where test harness expansion and server implementation advance together
- [계획/README.md](./계획/README.md): v1 phase index and per-phase implementation plans
- [계획/sprint_1/README.md](./계획/sprint_1/README.md): Sprint 1 harness iteration plan for Mode A contract skeleton
- [server_runtime_topology.md](./server_runtime_topology.md): server process separation, default ports, run scripts, environment variables, and startup order
- [server_boundary_policy.md](./server_boundary_policy.md): server boundary, direct DB access, client class, and internal endpoint policy
- [database_ownership_policy.md](./database_ownership_policy.md): server-specific schema ownership and database read/write access policy
- [database_physical_topology.md](./database_physical_topology.md): v1 SQLite dev DB layout and future PostgreSQL transition policy
- [database_migration_policy.md](./database_migration_policy.md): v1 SQL bootstrap, drift report import, migration ownership, and reset separation policy
- [requirements.md](./requirements.md): requirement IDs for drift server, admin orchestration, test harness, timeseries UI, and analysis chart integration
- [api_contracts.md](./api_contracts.md): API contracts for admin server, drift server, test feeder, chart definition artifacts, and LLM interpretation server
- [api_ownership_and_call_routing.md](./api_ownership_and_call_routing.md): endpoint ownership, caller, downstream routing, and DB write responsibility policy
- [server_interaction_scenarios.md](./server_interaction_scenarios.md): usage scenarios and server-to-server API call flows
- [internal_implementation_design.md](./internal_implementation_design.md): internal module, service, repository, scheduler, registry, and vertical-slice implementation design
- [design_review_issues.md](./design_review_issues.md): open design review issues to revisit before or during implementation

## Local Run

`drift_control_plane` root에서 서버를 실행한다. `run_all_servers.cmd`와 `run_all_servers.ps1`도 자기 위치인 `drift_control_plane`을 working directory로 잡고 Admin/Drift/Test Feeder 서버를 시작한다.

```powershell
cd C:\Users\jklee\PycharmProjects\drift_llm_intepretation\drift_control_plane
.\run_all_servers.ps1
```

또는 개별 서버를 실행한다.

```powershell
python -m uvicorn admin_server.app.main:app --host 127.0.0.1 --port 8770
python -m uvicorn drift_server.app.main:app --host 127.0.0.1 --port 8771
python -m uvicorn test_feeder_server.app.main:app --host 127.0.0.1 --port 8772
```

health endpoint:

```text
Admin Server:       http://127.0.0.1:8770/api/admin/health
Drift Server:       http://127.0.0.1:8771/api/health
Test Feeder Server: http://127.0.0.1:8772/api/test-feeder/health
LLM Server:         http://127.0.0.1:8767/api/health
```

통합 timeseries UI:

```text
http://127.0.0.1:8770/admin/timeseries/drift_metric_timeseries_demo.html?testMode=1&autoPoll=1&pollMs=1500&sourceId=case-010&apiBase=http://127.0.0.1:8770&llmJobEndpoint=http://127.0.0.1:8770/api/admin/llm/interpret/chart/jobs
```

Admin UI는 datasource 연결 후 위 형식의 `/admin/timeseries/...` 링크를 생성한다. `apiBase`는 Admin의 Drift API proxy를, `llmJobEndpoint`는 Admin의 LLM job proxy를 가리킨다. `drift_metric_timeseries`의 과거 `http://127.0.0.1:8766/drift_metric_timeseries/...` 경로는 standalone/legacy demo bridge 용도이며 control plane 통합 실행 기준 URL이 아니다.

하네스 실행:

```powershell
python -m testing.harness.main --scenario testing/harness/scenarios/case010_mode_a.json
python -m testing.harness.main --scenario testing/harness/scenarios/case011_mode_a.json
```

서버 기동까지 한 프로세스에서 함께 검증하려면 다음을 사용한다.

```powershell
python -m testing.harness.run_with_servers --scenario testing/harness/scenarios/case010_mode_a.json
python -m testing.harness.run_with_servers --scenario testing/harness/scenarios/case011_mode_a.json
```

## Future Scope

- human verification workflow for ambiguous drift cases
