# Drift Server Idempotency and Locking

## 1. 목적

이 문서는 Drift Server collector, bucket 저장, drift method 실행, drift event 생성에서 중복 실행을 방지하는 정책을 정의한다.

핵심 목표:

```text
같은 adapter의 같은 10분 window가 동시에 두 번 처리되지 않게 한다.
이미 처리한 window를 다시 처리해도 bucket/method_run/drift_event가 중복 생성되지 않게 한다.
```

## 2. 기본 결정

1차 구현에서는 다음 정책을 사용한다.

```text
poll lock:
  adapter_state row를 DB transaction 안에서 SELECT ... FOR UPDATE로 잠근다.

bucket idempotency:
  unique(adapter_id, feature_id, bucket_start, bucket_end, resolution)

method_run idempotency:
  unique(assignment_id, window_start, window_end)

drift_event idempotency:
  초기에는 unique(method_run_id)
```

lease field 기반 분산 lock은 후속 확장으로 둔다.

## 3. Poll Lock

### 3.1 Lock 대상

adapter별 poll은 `drift_server.adapter_state` row를 기준으로 잠근다.

```sql
select *
from drift_server.adapter_state
where adapter_id = :adapter_id
for update;
```

이 lock은 하나의 DB transaction 안에서 유지된다.

### 3.2 poll_once transaction 흐름

```text
begin transaction
  adapter_state row select for update
  read_start = source_cursor_time
  read_end = read_start + 10분
  source rows fetch
  bucket upsert/insert
  method_run insert 또는 skip/retry
  drift_event insert 또는 skip
  adapter_state.source_cursor_time = read_end
commit
```

source fetch가 긴 작업이 될 수 있으면 transaction이 오래 열린다. 1차 구현에서는 단순성을 우선한다. 이후 source fetch 비용이 커지면 lease 방식으로 전환을 검토한다.

### 3.3 Lock 실패

같은 adapter에 대해 이미 poll이 실행 중이면 두 번째 poll은 DB lock 대기 또는 timeout이 발생할 수 있다.

정책:

```text
lock timeout이면 이번 poll은 skip한다.
adapter_state.last_error에 lock timeout을 기록하지 않는다.
운영 로그에는 debug/info 수준으로 남긴다.
```

lock timeout은 source 장애가 아니라 동시 실행 방지에 따른 정상적인 skip으로 본다.

## 4. Bucket Idempotency

### 4.1 Unique Key

```sql
alter table drift_server.metric_bucket
add constraint uq_metric_bucket_window
unique (adapter_id, feature_id, bucket_start, bucket_end, resolution);
```

같은 adapter/feature/window/resolution bucket은 하나만 존재한다.

### 4.2 Insert 정책

정상 처리:

```text
insert metric_bucket
```

이미 존재하는 경우:

```text
기존 bucket을 반환하고 새로 계산한 값을 덮어쓰지 않는다.
```

권장 SQL:

```sql
insert into drift_server.metric_bucket (...)
values (...)
on conflict (adapter_id, feature_id, bucket_start, bucket_end, resolution)
do nothing
returning *;
```

`returning`이 비어 있으면 기존 bucket을 조회한다.

### 4.3 Empty Bucket

빈 window도 같은 unique key를 사용한다.

```text
row_count = 0
status = empty
```

빈 bucket이 이미 있으면 새로 만들지 않는다.

## 5. Method Run Idempotency

### 5.1 Unique Key

```sql
alter table drift_server.method_run
add constraint uq_method_run_window
unique (assignment_id, window_start, window_end);
```

assignment별 window 실행 결과는 하나만 존재한다.

### 5.2 Already Success

이미 성공한 `method_run`이 있으면 재실행하지 않는다.

```text
existing method_run.run_status = success
  -> skip
  -> existing method_run 반환
```

### 5.3 Already Error

이미 error 상태인 `method_run`이 있으면 retry를 허용한다.

정책:

```text
existing method_run.run_status = error
  -> 같은 method_run row를 retrying/running으로 갱신
  -> detector 재실행
  -> 결과를 같은 method_run row에 저장
```

이렇게 하면 동일 window에 여러 error run이 쌓이지 않는다.

### 5.4 Running 상태

이미 running 상태인 `method_run`이 있으면 현재 실행은 skip한다.

```text
existing method_run.run_status = running
  -> skip
```

후속 구현에서 stale running timeout을 둘 수 있다.

## 6. Drift Event Idempotency

### 6.1 초기 정책

1차 구현에서는 method_run 하나가 최대 하나의 drift_event를 만든다.

```sql
alter table drift_server.drift_event
add constraint uq_drift_event_method_run
unique (method_run_id);
```

### 6.2 Event 생성 규칙

```text
method_run.level in (warning, drift)
  -> drift_event insert

method_run.level = normal
  -> drift_event 생성하지 않음
```

이미 event가 있으면 새로 만들지 않고 기존 event를 반환한다.

### 6.3 후속 확장

한 method_run에서 여러 feature 또는 여러 event segment를 생성해야 하는 algorithm이 생기면 unique key를 확장한다.

후보:

```text
unique(method_run_id, feature_id, event_start, event_end, level)
```

1차 구현에서는 단순성을 위해 `unique(method_run_id)`를 사용한다.

## 7. Cursor Advance와 Idempotency

cursor는 window 처리가 기록 가능한 상태까지 진행된 뒤 전진한다.

정책:

```text
bucket 저장 성공
method_run 성공 또는 error 기록 성공
drift_event 생성 또는 skip 완료
  -> source_cursor_time = read_end
```

source fetch 실패나 DB transaction 실패가 발생하면 cursor를 전진하지 않는다.

```text
source_cursor_time remains read_start
```

다음 poll은 같은 window를 다시 시도한다.

unique key가 있기 때문에 일부 insert가 성공한 뒤 retry되어도 중복 row가 생기지 않아야 한다.

## 8. Catch-up과 Idempotency

catch-up은 여러 window를 처리하지만, 각 window는 `poll_once`와 같은 idempotent 처리 함수를 사용한다.

```text
while source_cursor_time + 10분 <= available_source_time:
  process_one_window_idempotently()
```

catch-up 중 실패하면 해당 window에서 중단한다.

```text
성공한 window:
  cursor 전진

실패한 window:
  cursor 유지
  catch-up 중단
```

## 9. 권장 DB Constraint

```sql
alter table drift_server.metric_bucket
add constraint uq_metric_bucket_window
unique (adapter_id, feature_id, bucket_start, bucket_end, resolution);

alter table drift_server.method_run
add constraint uq_method_run_window
unique (assignment_id, window_start, window_end);

alter table drift_server.drift_event
add constraint uq_drift_event_method_run
unique (method_run_id);
```

## 10. 후속 검토: Lease 기반 Lock

다음 상황이 오면 lease 기반 lock을 추가 검토한다.

```text
Drift Server worker가 여러 instance로 늘어남
source fetch가 오래 걸려 DB transaction lock 유지 시간이 부담됨
poll 작업을 background queue로 분산해야 함
worker crash 후 lock 복구가 필요함
```

후보 필드:

```sql
drift_server.adapter_state
  lease_owner text
  lease_expires_at timestamptz
  processing_window_start timestamptz
  processing_window_end timestamptz
```

1차 구현에서는 이 필드를 만들지 않는다.

## 11. 관련 이슈

```text
DRI-009 collector 동시 실행/중복 실행 방지 누락
DRI-008 시간/커서 모델 정의 부족
```
