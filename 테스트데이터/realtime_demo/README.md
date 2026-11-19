# Realtime Drift Demo

실험 대상:

```text
dataset_case_id: CASE-010
chart_code: CHART-STREAM-001
method: ADWIN
variant_code: ADWIN_MEAN_STREAM
adapter_id: adwin_mean_stream_to_chart_stream_001
```

## 구성

- `server.py`: ingest API, hourly aggregation, ADWIN detector, event store, chart payload adapter, static web server
- `data_server.py`: 외부 데이터 서버. CASE-010 1분 데이터를 읽어 1초에 1건씩 drift 서버로 전송
- `replay_sender.py`: `CASE-010` 1분 데이터를 1초당 1건 또는 빠른 모드로 `/api/ingest`에 전송
- `smoke_test.py`: 서버를 같은 프로세스에서 실행하지 않고도 aggregate, detector, event, adapter를 검증
- `system_smoke_test.py`: data server -> drift server 흐름을 같은 프로세스에서 빠르게 검증
- `web/index.html`: `drift_metric_timeseries` 데모 화면
- `web/test_data.js`: CASE-010 feature registry 초기값

## 실행

Drift 서버:

```powershell
python 테스트데이터\realtime_demo\server.py --port 8771
```

브라우저:

```text
http://127.0.0.1:8771/index.html
```

외부 데이터 서버:

```powershell
python 테스트데이터\realtime_demo\data_server.py --port 8772
```

외부 데이터 서버에서 전송 시작:

```powershell
Invoke-RestMethod -Uri http://127.0.0.1:8772/api/start -Method POST -ContentType "application/json" -Body '{"target_url":"http://127.0.0.1:8771/api/ingest","start":"2026-01-01 00:00:00","interval_seconds":1}'
```

이 설정은 다음 의미다.

```text
data server 1초마다 1건 전송
drift server는 수신 1건을 테스트 데이터 1분으로 처리
drift server는 60건마다 1시간 aggregate 생성
timeseries chart는 5초마다 live API를 poll하며 hourly aggregate와 event를 갱신
```

빠른 14일 테스트 전송:

```powershell
Invoke-RestMethod -Uri http://127.0.0.1:8772/api/start -Method POST -ContentType "application/json" -Body '{"target_url":"http://127.0.0.1:8771/api/ingest","start":"2026-06-25 00:00:00","limit":20160,"interval_seconds":0}'
```

상태 확인:

```powershell
Invoke-RestMethod -Uri http://127.0.0.1:8772/api/status
Invoke-RestMethod -Uri http://127.0.0.1:8771/api/drift-demo/status
```

단일 CLI 송신기:

```powershell
python 테스트데이터\realtime_demo\replay_sender.py --url http://127.0.0.1:8771/api/ingest --start "2026-06-25 00:00:00" --limit 20160 --delay 1
```

빠른 테스트:

```powershell
python 테스트데이터\realtime_demo\replay_sender.py --url http://127.0.0.1:8771/api/ingest --start "2026-06-25 00:00:00" --limit 20160 --delay 0
```

스모크 테스트:

```powershell
python 테스트데이터\realtime_demo\smoke_test.py
```

Data server -> drift server 시스템 스모크 테스트:

```powershell
python 테스트데이터\realtime_demo\system_smoke_test.py
```

## 현재 검증 결과

`smoke_test.py` 기준:

```text
hourly aggregate: 336 rows
drift events: 4
first event window: 2026-07-01 00:00:00Z ~ 2026-07-02 00:00:00Z
analysis chart: CHART-STREAM-001
adapter: adwin_mean_stream_to_chart_stream_001 v1
```

`system_smoke_test.py` 기준:

```text
data server sent_count: 20,160 rows
simulated minutes: 20,160
simulated hours: 336
drift server hourly aggregate: 336 rows
drift events: 4
first event window: 2026-07-01 00:00:00Z ~ 2026-07-02 00:00:00Z
```

## Adapter 원칙

ADWIN 결과를 chart에 직접 넣지 않는다.

```text
ADWIN DriftResult
  -> adwin_mean_stream_to_chart_stream_001
  -> CHART-STREAM-001 runtime payload
```

이벤트에는 `methodResult`와 chart용 payload가 함께 저장된다. 이 구조를 다른 method/chart 조합에도 반복 적용한다.
