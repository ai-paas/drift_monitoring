# 실시간 Drift 탐지 데모 시나리오 및 구현 방안

## 1. 목적

188개 chart-method 연결 중 하나를 선택해, 테스트 데이터가 실시간으로 들어오고 drift 알고리즘이 이벤트를 발생시키며, 시계열 차트와 분석 차트가 이 이벤트를 연동해 보여주는 end-to-end 데모를 만든다.

이 데모의 핵심 역할은 다음을 검증하는 것이다.

```text
synthetic test data
  -> realtime ingest
  -> hourly aggregation
  -> drift detection
  -> event store
  -> timeseries event list
  -> linked analysis chart
```

## 2. 전체 시나리오

테스트 데이터는 2026년 1월 1일부터 2026년 12월 31일까지 1분 단위로 만들어져 있다. 데모에서는 이 데이터를 가속 재생한다.

```text
실제 1초 = 테스트 데이터 1분
실제 60초 = 테스트 데이터 1시간
```

외부 송신 서버는 1초에 한 행씩 데이터를 웹서버로 보낸다. 웹서버는 60건을 모아 1시간 집계값을 만들고, 이 집계값을 시계열 차트가 읽을 수 있는 형태로 저장한다.

drift detector는 데이터 성격에 맞는 window를 사용해 주기적으로 drift 여부를 판단한다. drift가 탐지되면 이벤트를 저장한다. 시계열 차트는 저장된 이벤트를 읽어 왼쪽 이벤트 목록에 표시한다. 사용자가 이벤트를 선택하면 해당 이벤트에 연결된 분석 차트가 열리고, 분석 결과 payload를 읽어 상세 차트를 그린다.

## 3. 첫 구현 추천 대상

첫 end-to-end 구현은 stream 계열이 가장 적합하다.

```text
dataset_case_id: CASE-010
case_name: stream_numeric_mean_shift
chart-method 후보: CHART-STREAM-001 / ADWIN
대안 후보: CHART-CTRL-001 / CUSUM
```

추천 이유:

- `CASE-010`은 이미 timestamped numeric stream이다.
- 실시간 수신, 1시간 집계, drift window 탐지 흐름과 자연스럽게 맞는다.
- stream/control chart 계열은 이벤트 발생 시점을 시계열 위에 표시하기 쉽다.
- ADWIN/CUSUM/Page-Hinkley 계열은 drift event를 만들기 좋은 알고리즘이다.

단, 구현체 복사 난이도에 따라 최종 method는 `drift_algorithm_impl` 내부에서 실제 구현이 가장 명확한 것을 선택한다.

## 4. 구성 요소

### 4.0 Method-result to chart-payload adapter

drift method가 만드는 결과와 분석 chart가 요구하는 데이터 포맷은 다를 수 있다. 이 둘을 직접 연결하지 않는다.

반드시 중간에 adapter 계층을 둔다.

```text
drift method result
  -> method result normalizer
  -> analysis context builder
  -> chart payload adapter
  -> chart-specific analysis payload
  -> analysis chart
```

이 원칙은 중요하다. method는 탐지 결과를 만들고, chart는 자기 payload 계약에 맞는 데이터를 그린다. 이벤트 저장 시에는 원본 method 결과와 chart용 payload를 모두 저장한다.

```json
{
  "event_id": "EVT-000001",
  "chart_code": "CHART-STREAM-001",
  "method_name": "ADWIN",
  "variant_code": "ADWIN_MEAN_STREAM",
  "raw_method_result": {
    "detected": true,
    "statistic": 0.31,
    "threshold": 0.20
  },
  "analysis_payload": {
    "chart_code": "CHART-STREAM-001",
    "series": [],
    "markers": [],
    "windows": {},
    "detector": {},
    "summary": {}
  },
  "adapter_id": "adwin_mean_stream_to_chart_stream_001",
  "adapter_version": "v1"
}
```

따라서 chart-method mapping은 장기적으로 다음 정보를 가져야 한다.

```text
method_result_schema
chart_payload_schema
adapter_id
adapter_version
adapter_status
```

현재 단계는 전체 drift 운영 서버를 바로 만드는 것이 아니다. 지금은 하나의 chart-method 조합을 골라 end-to-end 흐름이 되는지 연습하고 검증한다. 모든 method와 chart 연결이 adapter를 통해 원활하게 동작한다는 확신이 생기면, 그 후 실제 drift 관리 서버 구조를 정리해 구현한다.

### 4.1 외부 데이터 송신 서버

역할:

```text
테스트데이터/CASE-010_*/data.csv.gz
  -> 1초마다 1 row 읽기
  -> ingest API로 POST
```

송신 payload 예:

```json
{
  "timestamp": "2026-07-01 00:00:00",
  "case_id": "CASE-010",
  "sample_id": "CASE-010-260640",
  "metric": 0.82,
  "target_level": 0.80,
  "threshold": 0.68,
  "period": "current"
}
```

송신 서버는 데모용이므로 다음 기능만 있으면 충분하다.

- 시작/중지
- 재생 속도 설정
- 특정 timestamp부터 재생
- 마지막 전송 위치 기록

### 4.2 수신 웹서버

역할:

```text
POST /api/ingest
  -> raw point 저장
  -> 60건마다 hourly aggregate 생성
  -> detector에 새 aggregate/window 전달
```

저장 대상:

- raw minute-equivalent point
- hourly aggregate
- detector result
- drift event
- analysis payload

초기 구현은 SQLite 또는 JSONL로 충분하다. 운영 확장 시 PostgreSQL로 옮긴다.

### 4.3 1시간 집계기

60건이 모이면 하나의 hourly point를 만든다.

집계 예:

```text
hour_start
count
metric_mean
metric_std
metric_min
metric_max
event_count
last_source_timestamp
```

시계열 차트는 raw 1초 데이터를 직접 보지 않고 hourly aggregate를 읽는다.

### 4.4 Drift detector

detector는 hourly aggregate 기준으로 실행한다.

추천 window:

```text
reference_window: 최근 drift 이전 안정 구간 72시간
current_window: 최근 24시간
minimum_points: 24 hourly points
detection_interval: hourly aggregate 생성 시마다
```

CASE-010의 경우 stream mean shift이므로 detector 입력은 `metric_mean`이 된다.

탐지 결과 예:

```json
{
  "detected": true,
  "method": "ADWIN",
  "variant_code": "ADWIN_MEAN_STREAM",
  "statistic": 0.31,
  "threshold": 0.20,
  "p_value": 0.009,
  "reference_mean": 0.51,
  "current_mean": 0.79,
  "drift_direction": "increase"
}
```

### 4.5 Event store

drift가 탐지되면 이벤트를 저장한다.

필수 필드:

```text
event_id
event_time
case_id
source_dataset_id
chart_code
method_name
variant_code
detector_status
severity
reference_window_start
reference_window_end
current_window_start
current_window_end
summary_text
analysis_payload_path 또는 analysis_payload_json
created_at
```

이벤트는 중복 폭주를 막기 위해 cooldown을 둔다.

```text
same method + same chart + same direction 기준
cooldown: 6시간 또는 24시간
```

### 4.6 시계열 차트

`drift_metric_timeseries`의 기존 시계열 차트를 가져와 실시간 모니터링 화면으로 사용한다.

역할:

- hourly aggregate 표시
- threshold 또는 baseline 표시
- 왼쪽 이벤트 목록 표시
- 이벤트 선택 시 분석 차트 열기

필요 API:

```text
GET /api/timeseries?case_id=CASE-010
GET /api/events?case_id=CASE-010
GET /api/events/{event_id}
```

### 4.7 분석 차트

분석 차트는 188개 연결 중 선택한 chart를 사용한다. chart는 `chart_builder`의 chart design을 기반으로 생성하거나 복사한다.

역할:

- 이벤트에 저장된 analysis payload를 읽는다.
- reference/current window를 비교한다.
- detector statistic, threshold, drift direction을 보여준다.
- 시계열 차트에서 선택한 이벤트와 같은 event_id를 기준으로 로드된다.

필요 API:

```text
GET /api/events/{event_id}/analysis
```

## 5. 저장 구조 초안

초기 파일 기반 저장 구조:

```text
realtime_demo/
  data/
    raw_points.jsonl
    hourly_points.jsonl
    drift_events.jsonl
    analysis_payloads/
      EVT-000001.json
  server/
    app.py
  sender/
    replay_sender.py
  web/
    timeseries/
    analysis_chart/
```

DB 기반으로 갈 경우 최소 테이블:

```sql
raw_stream_point(
  raw_point_id,
  source_timestamp,
  received_at,
  case_id,
  sample_id,
  payload_json
)

hourly_metric_point(
  hourly_point_id,
  case_id,
  hour_start,
  count,
  metric_mean,
  metric_std,
  metric_min,
  metric_max,
  source_start,
  source_end
)

drift_event(
  event_id,
  case_id,
  event_time,
  chart_code,
  method_name,
  variant_code,
  severity,
  reference_window_start,
  reference_window_end,
  current_window_start,
  current_window_end,
  result_json,
  analysis_payload_json,
  created_at
)
```

## 6. 구현 순서

### Step 1. 대상 chart-method 선정

`테스트데이터/chart_method_dataset_mapping.csv`에서 `CASE-010`에 배정된 row 중 하나를 선택한다.

우선 후보:

```text
CHART-STREAM-001 / ADWIN / ADWIN_MEAN_STREAM
CHART-CTRL-001 / CUSUM / ONE_SIDED_UPPER_CUSUM
CHART-STREAM-003 / Page-Hinkley Test / PAGE_HINKLEY_INCREASE
```

선정 기준:

- `drift_algorithm_impl`에 구현체가 있는가
- `chart_builder`에서 대응 chart design을 만들기 쉬운가
- 이벤트 발생 시점을 시계열에서 설명하기 쉬운가

### Step 2. method 구현 복사

`drift_algorithm_impl`에서 선정 method 구현을 demo server 내부로 복사하거나 import 가능한 구조로 연결한다.

권장:

```text
처음에는 복사
이후 공통 패키지 import로 변경
```

복사 시 확인할 것:

- 입력 스키마
- window 단위 호출 방식
- 반환 metric 이름
- threshold/alarm 필드
- 에러 처리

### Step 3. chart 생성

`chart_builder`의 chart design을 사용해 선정 chart를 생성한다.

출력물:

```text
analysis_chart.html
analysis_chart.css
analysis_chart.js
```

이 chart는 정적 예시 데이터가 아니라 `/api/events/{event_id}/analysis`를 호출해 payload를 읽어야 한다.

### Step 4. timeseries chart 연결

`drift_metric_timeseries`에서 시계열 차트를 가져온다.

필요 수정:

- `/api/timeseries` polling
- `/api/events` polling
- 이벤트 목록 UI
- 이벤트 클릭 시 분석 차트 열기

### Step 5. 외부 송신 서버 작성

`CASE-010` 데이터의 `data.csv.gz`를 읽고 1초마다 ingest API에 보낸다.

개발 모드에서는 속도를 빠르게 조정할 수 있게 한다.

```text
--speed 60  # 실제 1초에 테스트 60분 전송 같은 가속 옵션
```

### Step 6. end-to-end 검증

검증 항목:

- 데이터가 1초마다 수신되는가
- 60건마다 hourly point가 생기는가
- 시계열 차트에 hourly point가 추가되는가
- drift_start 이후 detector가 이벤트를 만드는가
- 이벤트가 왼쪽 목록에 나타나는가
- 이벤트 클릭 시 분석 차트가 열리는가
- 분석 차트가 같은 event_id의 analysis payload를 표시하는가

## 7. 주요 인터페이스

### ingest

```http
POST /api/ingest
Content-Type: application/json
```

```json
{
  "timestamp": "2026-07-01 00:00:00",
  "case_id": "CASE-010",
  "sample_id": "CASE-010-260640",
  "metric": 0.82
}
```

### timeseries

```http
GET /api/timeseries?case_id=CASE-010
```

```json
{
  "points": [
    {
      "hour_start": "2026-07-01 00:00:00",
      "metric_mean": 0.78,
      "metric_std": 0.05
    }
  ]
}
```

### events

```http
GET /api/events?case_id=CASE-010
```

```json
{
  "events": [
    {
      "event_id": "EVT-000001",
      "event_time": "2026-07-02 03:00:00",
      "chart_code": "CHART-STREAM-001",
      "method_name": "ADWIN",
      "variant_code": "ADWIN_MEAN_STREAM",
      "severity": "drift",
      "summary_text": "current window mean increased from 0.51 to 0.79"
    }
  ]
}
```

### analysis

```http
GET /api/events/EVT-000001/analysis
```

```json
{
  "event_id": "EVT-000001",
  "chart_code": "CHART-STREAM-001",
  "method": {
    "name": "ADWIN",
    "variant_code": "ADWIN_MEAN_STREAM"
  },
  "reference_window": {
    "start": "2026-06-28 03:00:00",
    "end": "2026-07-01 03:00:00",
    "mean": 0.51
  },
  "current_window": {
    "start": "2026-07-01 03:00:00",
    "end": "2026-07-02 03:00:00",
    "mean": 0.79
  },
  "detector": {
    "statistic": 0.28,
    "threshold": 0.20,
    "detected": true
  },
  "series": []
}
```

## 8. 구현상 주의점

1. 테스트 데이터의 timestamp는 2026년 실제 시각이고, 데모 재생 시각은 현재 wall-clock이다. 두 시간을 혼동하지 않는다.
2. 시계열 차트는 raw 1초 수신 데이터가 아니라 hourly aggregate를 본다.
3. drift detector window도 hourly aggregate 기준으로 잡는다.
4. 이벤트 중복 생성을 막기 위해 cooldown이 필요하다.
5. 분석 chart는 chart-method mapping의 `chart_code`, `method_name`, `variant_code`를 이벤트에 저장해 재현 가능하게 한다.
6. method 구현 복사는 첫 데모용이고, 장기적으로는 `drift_algorithm_impl`을 패키지처럼 import하는 방식이 낫다.
