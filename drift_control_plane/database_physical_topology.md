# Database Physical Topology

## 1. 목적

이 문서는 v1 구현에서 DB를 물리적으로 어떻게 배치할지 정리한다.

논리적인 소유권은 `database_ownership_policy.md`가 정의하고, 이 문서는 개발/테스트 환경에서 실제 DB instance, database, schema, connection string을 어떻게 둘지 결정한다.

## 2. 핵심 결정

현재 v1 dev runtime은 workspace-local SQLite DB를 사용한다.

```text
drift_control_plane/runtime/sprint2_dev.sqlite3
```

이 DB는 `shared/dev_db.py`의 `connect()`와 `ensure_schema()`가 생성/갱신한다. Drift Server와 Test Feeder Server health 응답의 `state`도 `sqlite-dev`다.

논리 소유권은 다음 table group으로 구분한다. SQLite에는 PostgreSQL schema가 없으므로 실제 table 이름에는 schema prefix를 붙이지 않는다.

```text
drift_server logical group
test_source logical group
managed_contract/dev metadata
```

PostgreSQL instance/database/schema 분리는 후속 전환 목표다. 현재 실행 기준으로 보지 않는다.

## 3. 왜 단일 SQLite DB인가

이 방식의 목적은 서버 경계를 약하게 만드는 것이 아니다.

```text
서버 경계: API와 code ownership으로 분리
DB 물리 구성: v1 dev runtime은 SQLite 단일 파일로 단순화
DB 논리 소유권: table group 단위로 분리
```

장점:

- 테스트 하네스 구성이 단순하다.
- Test Feeder와 Drift Server를 동시에 띄우는 end-to-end 테스트가 쉽다.
- `test_source`를 실제 외부 DB처럼 다루면서도 로컬 설정 부담이 낮다.
- 나중에 실제 외부 source DB로 바꿀 때는 adapter connection 설정만 바꾸면 된다.

## 4. Table Group별 소유 서버

| Table group | 소유 서버 | 용도 |
| --- | --- | --- |
| `adapter_state`, `metric_bucket`, `source_method_assignment`, `method_state`, `method_run`, `drift_event`, `analysis_chart_registration` | Drift Server | adapter, bucket, method_run, drift_event, analysis chart runtime state |
| `raw_event`, `feed_state` | Test Feeder Server | 테스트 raw event, feed state |
| `managed_contract` | 개발/검증 tooling | managed contract registry |

Admin Server는 v1에서 별도 schema를 갖지 않는다. 필요하면 후속 버전에서 `admin_server` schema를 추가한다.

## 5. 접근 규칙

### 5.1 Drift Server

허용:

```text
drift_server logical table group read/write
test_source logical table group read-only via SourceAdapter
```

금지:

```text
test_source logical table group write
```

Drift Server가 `test_source`를 읽는 것은 외부 source adapter가 source DB를 읽는 것과 같은 의미다.

### 5.2 Test Feeder Server

허용:

```text
test_source logical table group read/write
```

금지:

```text
drift_server logical table group read/write
```

### 5.3 Admin Server

허용:

```text
Drift Server API 호출
Test Feeder Server API 호출
LLM Interpretation Server API 호출
```

금지:

```text
drift_server logical table group direct write
test_source logical table group direct write
managed_contract direct mutation outside tooling
```

Admin Server가 catalog 조회를 위해 report artifact를 읽는 것은 가능하지만, v1에서는 가능하면 명시적인 catalog client 경유를 우선한다.

## 6. DB Path / Connection 정책

현재 v1 dev runtime은 connection string이 아니라 SQLite file path를 사용한다.

예:

```text
drift_control_plane/runtime/sprint2_dev.sqlite3
```

기본 경로는 `shared/dev_db.py`의 `DEFAULT_DB_PATH`다. 현재 `DRIFT_SERVER_DATABASE_URL`, `TEST_FEEDER_DATABASE_URL`, `DRIFT_REPORT_DATABASE_URL`은 실행 코드가 사용하지 않는다.

후속 PostgreSQL 전환 시에는 서버별 환경 변수를 도입할 수 있다.

```text
DRIFT_SERVER_DATABASE_URL
TEST_FEEDER_DATABASE_URL
DRIFT_REPORT_DATABASE_URL
```

그 전까지 코드와 문서는 SQLite dev DB를 현재 실행 기준으로 본다.

## 7. 권장 권한 모델

SQLite dev DB에서는 DB user 권한 분리가 없다.

후속 PostgreSQL 전환 시 repository/service 코드는 다음 권한 모델을 전제로 작성한다.

| DB user | 권한 |
| --- | --- |
| `drift_server_user` | `drift_server` read/write, `test_source` read-only, `drift_report` read-only |
| `test_feeder_user` | `test_source` read/write |
| `llm_interpretation_user` | `llm_interpretation` read/write, `drift_report` read-only |
| `admin_server_user` | optional `admin_server` read/write only |

## 8. Migration 배치

현재 v1 dev runtime은 migration SQL 파일을 실행하지 않고 `shared/dev_db.py`가 SQLite schema를 보장한다.

```text
shared/dev_db.py
  connect()
  ensure_schema()
  _seed_managed_contracts()
```

PostgreSQL migration/bootstrap 정책은 후속 전환 문서로 유지한다. 현재 실행 확인은 `runtime/sprint2_dev.sqlite3`와 health의 `sqlite-dev` 상태를 기준으로 한다.

## 9. 외부 Source DB로 전환할 때

v1에서는 `test_source` logical table group이 같은 SQLite DB 안에 있어도, Drift Server는 반드시 SourceAdapter 역할의 repository/service 경계를 통해 읽는다.

후속 버전에서 실제 외부 source DB를 붙일 때 바뀌는 것은 다음뿐이다.

```text
source_adapter.connection_config_json
adapter implementation
DB credential
```

`metric_bucket`, `method_run`, `drift_event`, timeseries API 구조는 바뀌지 않아야 한다.

## 10. 관련 문서

- `database_ownership_policy.md`
- `database_migration_policy.md`
- `server_runtime_topology.md`
- `source_adapter_contract.md`
- `test_feeder_contract.md`
- `data_source_event_schema.md`
- `internal_implementation_design.md`
