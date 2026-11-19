# Drift Monitoring API Response Policy

## 1. 목적

이 문서는 drift monitoring 시스템의 API 응답 형식과 오류 처리 규칙을 정의한다.

핵심 결정:

```text
신규 서버는 {ok, data, error} envelope를 사용한다.
기존 서버 응답은 억지로 바꾸지 않고 client layer에서 normalize한다.
```

## 2. 적용 범위

### 2.1 신규 서버

다음 서버는 공통 응답 envelope를 사용한다.

```text
Admin Server
Drift Server
Test Feeder Server
```

공통 응답:

```json
{
  "ok": true,
  "data": {},
  "error": null
}
```

오류 응답:

```json
{
  "ok": false,
  "data": null,
  "error": {
    "code": "NOT_FOUND",
    "message": "source not found",
    "details": {}
  }
}
```

### 2.2 기존 서버

다음 서버는 기존 응답을 유지한다.

```text
LLM Interpretation Server
```

예:

```json
{
  "ok": true,
  "database": true,
  "codexExec": true
}
```

기존 서버 응답은 각 client class에서 신규 서버 내부 표준 구조로 normalize한다.

## 3. Error Object

`error`는 다음 구조를 가진다.

```json
{
  "code": "ERROR_CODE",
  "message": "Human readable message",
  "details": {}
}
```

필드:

```text
code:
  stable machine-readable error code

message:
  사람이 읽을 수 있는 짧은 설명

details:
  sourceId, adapterId, fieldErrors 등 추가 context
```

## 4. 권장 Error Code

```text
VALIDATION_ERROR
NOT_FOUND
CONFLICT
LOCKED
DOWNSTREAM_UNAVAILABLE
PAYLOAD_ADAPTER_ERROR
DRIFT_METHOD_ERROR
SOURCE_ADAPTER_ERROR
RESET_NOT_ALLOWED
INTERNAL_ERROR
```

## 5. HTTP Status Code

권장 매핑:

```text
200 OK
  요청이 정상 처리됨

400 Bad Request
  요청 형식 또는 validation 오류

404 Not Found
  source, adapter, event 등 resource 없음

409 Conflict
  unique key conflict, 이미 등록된 resource, 상태 충돌

423 Locked
  adapter poll lock 획득 실패 또는 실행 중 reset 불가

500 Internal Server Error
  예상하지 못한 서버 오류

502 Bad Gateway
  downstream server가 잘못된 응답 반환

503 Service Unavailable
  downstream server 연결 불가 또는 일시적 사용 불가
```

비즈니스 오류도 가능하면 HTTP status와 `error.code`를 함께 맞춘다.

## 6. Client Normalize 책임

외부 서버 호출은 직접 `requests` 또는 HTTP client를 흩뿌리지 않고 client class에 모은다.

대상 client:

```text
LlmInterpretationClient
DriftReportCatalogClient
TestFeederClient
DriftServerClient
```

client class 책임:

```text
HTTP status 확인
서버별 응답 형식 normalize
downstream 오류를 표준 error로 변환
timeout/retry 정책 적용
```

예:

```python
class LlmInterpretationClient:
    def health(self) -> dict:
        raw = self.http.get("/api/health")
        return {
            "ok": bool(raw.get("ok")),
            "data": {
                "database": raw.get("database"),
                "codexExec": raw.get("codexExec"),
            },
            "error": None,
        }
```

## 7. API 문서 작성 규칙

신규 API 문서에는 다음을 명시한다.

```text
endpoint
request body
success response
error response 또는 주요 error code
관련 state transition
```

기존 서버 API는 실제 응답을 그대로 기록하고, 필요하면 "client normalize 후 내부 표현"을 별도로 적는다.

## 8. 1차 구현 범위

1차 구현 필수:

```text
Admin Server response envelope
Drift Server response envelope
Test Feeder Server response envelope
LLM Interpretation Client normalize
```

후속:

```text
모든 error code 세분화
retry/backoff 표준화
request id / trace id
structured logging 연동
```

## 9. 관련 이슈

```text
DRI-004 API 공통 응답 envelope와 기존 LLM server 응답 형식이 다름
```
