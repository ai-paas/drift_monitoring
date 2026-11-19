# Database Migration Policy

## 1. 목적

이 문서는 v1에서 DB table을 어떤 방식으로 생성하고, drift report catalog artifact와 테스트 reset을 어떻게 분리할지 정의한다.

## 2. 핵심 결정

현재 v1 dev runtime에서는 migration framework를 도입하지 않는다.

```text
Alembic 같은 migration framework는 후속으로 미룬다.
v1 dev runtime은 workspace-local SQLite DB와 shared/dev_db.py로 table을 준비한다.
반복 테스트 초기화는 migration 재실행이 아니라 reset API로 수행한다.
```

이 결정은 v1의 목표가 운영 migration 체계 완성이 아니라 `CASE-010` vertical slice를 빠르게 end-to-end로 검증하는 것이기 때문이다.

## 3. 파일 배치

현재 v1 dev runtime 기준 파일 배치:

```text
runtime/
  sprint2_dev.sqlite3

shared/
  dev_db.py
```

`shared/dev_db.py`의 `connect()`가 SQLite file을 열고, `ensure_schema()`가 필요한 table을 생성/보강한다.

## 4. 실행 주체

SQLite dev DB table 보장은 서버가 connection을 열 때 수행된다.

정책:

```text
Drift Server/Test Feeder Server는 shared.dev_db.connect()를 통해 SQLite schema를 보장한다.
Admin Server는 migration runner가 아니다.
운영 PostgreSQL migration은 현재 v1 dev runtime 범위가 아니다.
```

서버 health는 현재 dev DB 상태를 `sqlite-dev`로 반환한다.

## 5. Bootstrap 실행 순서

현재 dev DB 준비 순서:

```text
1. 서버 또는 tooling이 shared.dev_db.connect() 호출
2. runtime/sprint2_dev.sqlite3 생성 또는 open
3. ensure_schema()가 raw_event, feed_state, metric_bucket, method_run 등 table 생성/보강
4. managed_contracts.csv를 managed_contract table에 seed
5. reset API로 반복 테스트 실행 데이터 초기화
```

v1 seed data:

```text
source type:
  test_db_numeric_stream

drift method:
  ADWIN_MEAN_STREAM

runtime_method_key:
  adwin_mean_stream

analysis chart:
  CHART-STREAM-001

payload_adapter_key:
  adwin_mean_stream_to_chart_stream_001
```

## 6. Drift Report Catalog 위치

`drift 보고서/charts/method_data.js`와 관련 report artifact는 chart-method catalog의 source of truth다.

정책:

```text
현재 v1 dev runtime은 별도 drift_report PostgreSQL import를 요구하지 않는다.
Admin/report gallery는 report artifact를 read-only로 사용한다.
Drift Server payload adapter는 chart_runtime payload template과 report method_data artifact를 read-only로 사용한다.
```

PostgreSQL 기반 drift_report import는 후속 전환 작업으로 둔다.

## 7. Migration SQL 작성 규칙

후속 PostgreSQL 전환 시 SQL 파일은 가능한 한 재실행 가능하게 작성한다.

권장:

```sql
create schema if not exists drift_server;
create table if not exists drift_server.data_source (...);
create index if not exists ...;
```

주의:

```text
기존 column 변경, rename, destructive migration은 bootstrap SQL에 섞지 않는다.
운영 migration 이력이 필요해지는 시점에 migration framework 도입을 다시 결정한다.
```

## 8. Migration과 Reset의 경계

Migration 또는 schema bootstrap은 구조 생성용이다.

```text
table 생성
index/constraint 생성
seed data 생성
```

Reset은 실행 데이터 초기화용이다.

```text
raw_event 삭제
feed_state cursor/status 초기화
adapter_state cursor/status/error 초기화
metric_bucket 삭제
method_state/method_run/drift_event 삭제
```

반복 테스트에서 DB를 초기화할 때 SQLite schema 생성을 다시 실행하는 대신 Admin Server의 reset API를 통해 Test Feeder Server와 Drift Server reset API를 호출한다.

## 9. 테스트 반복 실행 정책

테스트 반복 실행 흐름:

```text
1. 서버 시작 또는 tooling 실행으로 SQLite dev DB 준비
2. source/adapter/method/chart 등록
3. 테스트 실행
4. run reset API 호출
5. feeder/adapter 재시작
6. 테스트 재실행
```

SQLite table 생성/보강은 connection 시 자동 수행된다. DB 구조가 바뀐 경우에는 `shared/dev_db.py`와 managed contract seed를 함께 검토한다.

## 10. 실패 처리

Bootstrap 또는 schema 보장 실패 시 정책:

```text
중간 실패를 숨기지 않는다.
실패한 step과 SQL/script path를 출력한다.
부분 생성된 schema를 자동 삭제하지 않는다.
재실행 가능하도록 SQL은 if not exists 중심으로 작성한다.
```

테스트 reset 실패 시 정책:

```text
실행 중 feeder/adapter가 있으면 reset을 거부한다.
force reset은 v1에서 선택 사항이다.
reset 실패는 migration 재실행으로 복구하지 않는다.
```

## 11. 후속 Migration Framework 도입 기준

다음 조건 중 하나가 현실화되면 Alembic 같은 migration framework 도입을 다시 검토한다.

```text
운영 DB에 data-preserving schema 변경이 필요하다.
column rename/type change가 필요하다.
서버별 migration 이력을 추적해야 한다.
rollback 전략이 필요하다.
개발자 여러 명이 동시에 schema 변경을 추가한다.
```

v1에서는 이 조건들이 아직 핵심 범위가 아니다.

## 12. 관련 문서

- `database_physical_topology.md`
- `database_ownership_policy.md`
- `reset_policy.md`
- `implementation_scope_v1.md`
- `internal_implementation_design.md`
