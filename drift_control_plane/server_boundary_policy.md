# Drift Monitoring Server Boundary Policy

## 1. 목적

이 문서는 v1 구현에서 서버 간 경계와 호출 방식을 정의한다.

핵심 결정:

```text
서버 간 직접 DB 접근은 금지한다.
서버 간 호출은 명시적 API와 client class를 사용한다.
v1에서는 /api/internal/... endpoint를 만들지 않는다.
Admin Server는 사용자-facing control API만 제공하고, 실제 상태 저장은 소유 서버 API에 위임한다.
```

## 2. 서버 경계

v1 서버:

```text
Admin Server
Drift Server
Test Feeder Server
LLM Interpretation Server
```

각 서버는 자기 책임의 DB와 상태를 직접 관리한다.

```text
Admin Server:
  orchestration과 관리 화면/API

Drift Server:
  source, adapter, bucket, method_run, drift_event, analysis payload

Test Feeder Server:
  test_source raw_event/feed_state

LLM Interpretation Server:
  chart/component 해석

Chart Definition Artifact:
  서버 경계가 아니라 사전 생성된 snapshot/runtime payload template/catalog artifact
```

## 3. 직접 DB 접근 금지

서버 간 직접 DB 접근은 하지 않는다.

서버별 schema 소유권과 read/write 권한은 `database_ownership_policy.md`를 따른다.

금지:

```text
Admin Server가 Drift Server DB table을 직접 수정
Admin Server가 Test Feeder DB table을 직접 수정
Drift Server가 Test Feeder CSV를 직접 읽음
UI가 Drift Server DB를 직접 조회
```

허용:

```text
Admin Server -> Drift Server API
Admin Server -> Test Feeder Server API
UI -> Drift Server API
UI -> LLM Interpretation Server API
```

## 4. Client Class 사용

서버 간 HTTP 호출은 client class에 모은다.

```text
DriftServerClient
TestFeederClient
LlmInterpretationClient
DriftReportCatalogClient
```

client class 책임:

```text
base URL 관리
request/response schema 변환
응답 normalize
HTTP status 처리
timeout 처리
downstream 오류 변환
```

service code에서 임의로 HTTP 호출을 흩뿌리지 않는다.

## 5. Internal Endpoint 정책

v1에서는 `/api/internal/...` endpoint를 만들지 않는다.

이유:

```text
internal endpoint와 public/control endpoint가 중복될 수 있다.
서버 경계가 오히려 흐려진다.
v1에서는 필요한 제어 API를 정식 API로 정의하는 편이 단순하다.
```

예:

```text
Admin Server가 adapter poll을 유도해야 한다면
  /api/drift/adapters/{adapter_id}/poll-once 같은 명시적 control API를 둔다.

Admin Server가 reset을 요청해야 한다면
  Drift Server의 정식 reset API를 호출한다.
```

단, Drift Server 내부 scheduler는 외부 HTTP 없이 자기 service class를 직접 호출한다.

```text
Drift Server Scheduler
  -> DriftCollector.poll_once()
```

이것은 서버 내부 호출이므로 서버 경계 위반이 아니다.

## 6. 테스트 정책

단위 테스트:

```text
각 서버 내부 service/repository를 직접 호출 가능
```

통합 테스트:

```text
Admin Server
Test Feeder Server
Drift Server
LLM Interpretation Server

위 서버들을 띄우고 API contract 기준으로 검증
```

테스트 하네스는 운영 구조와 동일하게 API를 사용한다.

## 7. API 목록 기준

Endpoint 목록과 request/response schema는 `api_contracts.md`를 기준으로 한다.

이 문서는 API 목록을 반복하지 않는다. 서버 간 호출 방향과 저장 책임은 `api_ownership_and_call_routing.md`를 따른다.

## 8. 후속 검토

다음 상황이 오면 internal endpoint나 worker API를 재검토한다.

```text
server-to-server API와 public UI API를 분리해야 할 때
background worker를 별도 프로세스로 분리할 때
queue 기반 poll 작업이 필요할 때
운영 보안상 internal network endpoint가 필요할 때
```

## 9. 관련 이슈

```text
DRI-015 internal HTTP API와 service class 직접 호출 방식이 혼재됨
```

## 10. 관련 문서

```text
api_ownership_and_call_routing.md
api_contracts.md
server_interaction_scenarios.md
database_ownership_policy.md
```
