# Drift Server 요구사항 목록

## 1. 문서 목적

이 문서는 `drift_server`, 관리자 서버, 테스트 feeder, `drift_metric_timeseries` UI, analysis chart, LLM interpretation server 사이의 요구사항을 ID 단위로 정리한다.

요구사항 ID prefix는 다음 의미를 가진다.

```text
DSR-FR    기능 요구사항
DSR-DATA  데이터/DB 요구사항
DSR-API   API 요구사항
DSR-UI    UI 요구사항
DSR-TEST  테스트/하네스 요구사항
DSR-NFR   비기능/구조 요구사항
```

## 2. 기능 요구사항

| ID | 요구사항 | 설명 |
| --- | --- | --- |
| DSR-FR-001 | data source 등록 | 관리자 서버는 외부 데이터 소스 또는 테스트 데이터 소스를 등록할 수 있어야 한다. |
| DSR-FR-002 | source adapter 등록 | 관리자 서버는 data source에서 데이터를 가져올 adapter를 등록할 수 있어야 한다. |
| DSR-FR-003 | adapter 실행/중지 | 관리자 서버는 등록된 adapter를 실행, 중지, 상태 조회할 수 있어야 한다. |
| DSR-FR-004 | window 수집 | drift server는 adapter별로 canonical event_time 기준 aggregate interval window 하나를 수집해야 한다. v1 기본값은 10분이다. |
| DSR-FR-005 | bucket 집계 | drift server는 수집한 window 데이터를 feature별 bucket으로 집계해 저장해야 한다. v1 기본 resolution은 10분이다. |
| DSR-FR-020 | bucket 해상도 조정 | drift server는 V2에서 더 촘촘한 drift 감지를 위해 bucket resolution 또는 aggregate interval을 줄일 수 있어야 한다. |
| DSR-FR-006 | 정상 poll 제한 | 정상 poll 한 번은 항상 aggregate interval window 하나만 처리해야 하며, source에 더 많은 데이터가 쌓여 있어도 한 번에 모두 처리하지 않아야 한다. |
| DSR-FR-007 | catch-up 처리 | adapter 중단 후 재시작 시 명시적 catch-up 모드에서 누락된 window를 aggregate interval 단위로 순차 처리할 수 있어야 한다. |
| DSR-FR-008 | drift method 목록 조회 | 관리자 서버는 `drift 보고서` DB에 등록된 drift method, variant, implementation 목록을 조회해야 한다. |
| DSR-FR-009 | source별 drift method 할당 | 관리자 서버는 data source에 하나 이상의 drift method/variant를 할당할 수 있어야 한다. |
| DSR-FR-010 | method parameter 설정 | 관리자 서버는 source별 method assignment에 parameter, threshold, window 설정을 저장할 수 있어야 한다. |
| DSR-FR-011 | drift method 실행 | drift server는 새 bucket이 생성되면 source별 enabled assignment를 조회해 drift method를 실행해야 한다. |
| DSR-FR-012 | method run 저장 | drift server는 drift method 실행 입력 window, 상태, score, level, result를 저장해야 한다. |
| DSR-FR-013 | drift event 생성 | method result가 warning 또는 drift 조건을 만족하면 drift server는 drift event를 생성해야 한다. |
| DSR-FR-014 | source별 시계열 제공 | drift server는 data source별 bucket과 drift event를 `drift_metric_timeseries`가 사용할 수 있는 형태로 제공해야 한다. |
| DSR-FR-015 | event analysis chart 등록 | 관리자 서버는 source별 drift method assignment에 분석용 chart를 등록할 수 있어야 한다. |
| DSR-FR-016 | chart_builder 연동 | 관리자 서버는 미리 등록된 chart 목록에서 chart 생성을 요청하고, `chart_builder`를 통해 chart definition을 생성해야 한다. |
| DSR-FR-017 | payload adapter 등록 | analysis chart 등록 시 drift server 데이터에서 chart runtime payload를 만드는 `payload_adapter_key`를 함께 등록해야 한다. |
| DSR-FR-018 | event analysis payload 생성 | drift server는 drift event 분석 요청 시 등록된 payload adapter를 사용해 chart payload를 생성해야 한다. |
| DSR-FR-019 | LLM interpretation 연동 | UI는 analysis chart payload를 LLM interpretation server로 보내 chart/component 해석을 요청할 수 있어야 한다. |

## 3. 데이터/DB 요구사항

| ID | 요구사항 | 설명 |
| --- | --- | --- |
| DSR-DATA-001 | data_source 저장 | drift server는 data source id, title, description, type, URL, status, config를 저장해야 한다. |
| DSR-DATA-002 | source_adapter 저장 | drift server는 adapter id, source id, adapter type, source config, 수집/집계 interval, status를 저장해야 한다. |
| DSR-DATA-003 | adapter_state 저장 | drift server는 adapter별 source cursor time, available source time, 마지막 poll 상태, 오류를 저장해야 한다. |
| DSR-DATA-004 | source_feature 저장 | drift server는 source별 feature id, label, value type, unit, payload path, enabled 상태를 저장해야 한다. |
| DSR-DATA-005 | metric_bucket 저장 | drift server는 source, adapter, feature, bucket start/end, count, mean/min/max/stddev, payload를 저장해야 한다. |
| DSR-DATA-013 | source 원본 시간 보존 | drift server/test source는 source 원래 발생 시간인 source_event_time과 내부 처리 시간인 canonical event_time을 분리해 저장해야 한다. |
| DSR-DATA-014 | source 시간 보정 | source별 시간 차이는 source_config 또는 adapter_config의 timeMapping/clockOffset 설정으로 보정할 수 있어야 한다. |
| DSR-DATA-015 | adapter offset 계산 | source adapter는 source_event_time과 canonical event_time의 차이를 source_clock_offset_ms로 계산하거나 설정값으로 채워야 한다. |
| DSR-DATA-016 | offset 오류 처리 | source adapter는 source clock offset이 허용 범위를 벗어나거나 필요한 source_event_time이 누락되면 adapter를 error 상태로 전환하고 처리를 중단해야 한다. |
| DSR-DATA-017 | 기본 timeMapping mode | 운영 기본 timeMapping은 observed_offset, 테스트/데모 기본 timeMapping은 harness_logical_time이어야 한다. |
| DSR-DATA-018 | source_event_time 누락 허용 범위 | source_event_time은 이를 필요로 하는 mode에서는 필수이며, source_ingest_time처럼 명시적으로 허용한 mode에서만 null일 수 있다. |
| DSR-DATA-019 | 미래 event_time 제외 | canonical 변환 후 event_time이 collector_tick_time보다 미래이면 해당 row는 아직 처리하지 않고 이후 tick/poll에서 처리해야 한다. |
| DSR-DATA-020 | 정기 clock check | source adapter는 row 수집과 별개로 source server time을 정기 조회해 Drift Server/Harness 기준 시각과의 offset을 adapter_state에 저장해야 한다. |
| DSR-DATA-021 | adapter offset summary | drift server는 adapter_state에 최근 source clock offset의 last/min/max/avg/count와 마지막 clock check 시각을 저장해야 한다. |
| DSR-DATA-006 | source_method_assignment 저장 | drift server는 source별 method variant, algorithm implementation, feature, params, threshold, window config를 저장해야 한다. |
| DSR-DATA-007 | method_state 저장 | drift server는 상태형 detector의 내부 상태와 마지막 처리 bucket 시각을 assignment별로 저장해야 한다. |
| DSR-DATA-008 | method_run 저장 | drift server는 assignment별 실행 window, status, score, level, result, error를 저장해야 한다. |
| DSR-DATA-009 | drift_event 저장 | drift server는 event가 source, adapter, assignment, method_run과 연결되도록 저장해야 한다. |
| DSR-DATA-022 | drift_event 자동 병합 금지 | drift server는 겹치는 window 또는 인접 window에서 drift가 반복 감지되어도 method_run이 다르면 별도 drift_event로 저장해야 한다. |
| DSR-DATA-010 | analysis_chart_registration 저장 | drift server는 assignment별 chart id, chart definition id, chart builder job id, payload adapter key를 저장해야 한다. |
| DSR-DATA-011 | chart_payload_adapter 저장 | drift server는 chart/method 조합에 사용할 payload 변환 함수 key와 contract를 저장해야 한다. |
| DSR-DATA-012 | drift catalog source of truth | drift method와 chart catalog 원본은 `drift 보고서` DB를 기준으로 해야 하며, drift server는 이를 중복 catalog로 재정의하지 않아야 한다. |

## 4. API 요구사항

| ID | 요구사항 | 설명 |
| --- | --- | --- |
| DSR-API-001 | source 목록 API | drift server는 등록된 data source 목록과 상태, bucket/event count, timeseries URL을 반환해야 한다. |
| DSR-API-002 | source 상세 API | drift server는 특정 source의 metadata, adapter state, feature 목록을 반환해야 한다. |
| DSR-API-003 | source feature API | drift server는 `drift_metric_timeseries` feature selector에 필요한 metadata를 반환해야 한다. |
| DSR-API-004 | method assignment API | drift server는 source별 method assignment CRUD API를 제공해야 한다. |
| DSR-API-005 | executable method API | drift server 또는 관리자 서버는 실행 가능한 drift method 목록을 `drift 보고서` DB 기준으로 제공해야 한다. |
| DSR-API-006 | timeseries data API | drift server는 source별 bucket/event 전체 또는 범위 조회 API를 제공해야 한다. |
| DSR-API-007 | timeseries live API | drift server는 마지막 수신 시점 이후의 bucket/event만 반환하는 live update API를 제공해야 한다. |
| DSR-API-008 | event analysis API | drift server는 event id를 받아 등록된 analysis chart와 chart payload를 반환해야 한다. |
| DSR-API-009 | admin orchestration API | 관리자 서버는 source, adapter, method assignment, test mode, feeder, adapter 실행 상태를 제어하는 API를 제공해야 한다. |

## 5. UI 요구사항

| ID | 요구사항 | 설명 |
| --- | --- | --- |
| DSR-UI-001 | data source 목록 화면 | drift server UI 또는 연결 UI는 등록된 data source 목록, URL, adapter 상태, bucket/event count를 보여줘야 한다. |
| DSR-UI-002 | source별 timeseries 화면 | 사용자가 source URL을 열면 해당 source의 `drift_metric_timeseries` chart가 표시되어야 한다. |
| DSR-UI-003 | drift event 표시 | timeseries 화면은 warning/drift event를 marker, band, 또는 event list로 표시해야 한다. |
| DSR-UI-004 | analysis chart 링크 표시 | drift event 아래에는 해당 event에 등록된 analysis chart 링크가 표시되어야 한다. |
| DSR-UI-005 | analysis chart 표시 | 사용자가 analysis chart 링크를 누르면 drift server가 생성한 chart payload로 분석 chart가 렌더링되어야 한다. |
| DSR-UI-006 | 관리자 method 선택 화면 | 관리자 화면은 `drift 보고서` DB에 등록된 실행 가능한 method/variant/implementation을 선택할 수 있게 해야 한다. |
| DSR-UI-007 | 관리자 chart 생성 화면 | 관리자 화면은 선택한 method에 연결 가능한 chart 목록을 보여주고 chart 생성/등록을 실행할 수 있어야 한다. |

## 6. 테스트/하네스 요구사항

| ID | 요구사항 | 설명 |
| --- | --- | --- |
| DSR-TEST-001 | 테스트 source DB | 테스트 DB는 외부 데이터 소스를 흉내내며 raw event를 저장해야 한다. |
| DSR-TEST-002 | CSV feeder | 테스트 feeder는 `테스트데이터/CASE-*` CSV를 읽어 Harness Clock의 `logicalNow`에 맞춰 테스트 DB에 넣어야 한다. |
| DSR-TEST-003 | Harness Clock | 하네스는 `startTime`, `endTime`, `tickIntervalMinutes`를 기준으로 논리 시간을 생성하고 매 tick마다 서버에 `logicalNow`를 전달해야 한다. |
| DSR-TEST-004 | manual clock | 자동 테스트에서는 sleep 없이 Harness Clock tick loop로 logical time을 전진해야 한다. |
| DSR-TEST-005 | 테스트 reset | 관리자 서버 또는 하네스는 테스트 DB, drift server bucket/event/state를 초기화할 수 있어야 한다. |
| DSR-TEST-006 | service class 직접 호출 | 자동 테스트는 여러 서버 프로세스를 띄우지 않고 feeder, collector, detector service class를 직접 호출할 수 있어야 한다. |
| DSR-TEST-007 | 대표 vertical slice | 초기 테스트는 `CASE-010 + ADWIN_MEAN_STREAM + CHART-STREAM-001` 조합으로 end-to-end 흐름을 검증해야 한다. |

## 7. 비기능/구조 요구사항

| ID | 요구사항 | 설명 |
| --- | --- | --- |
| DSR-NFR-001 | control/data plane 분리 | 관리자 서버는 control plane이고, feeder/adapter/collector/detector/timeseries API는 data plane으로 분리되어야 한다. |
| DSR-NFR-002 | 관리자 서버 책임 제한 | 관리자 서버는 CSV 파싱, bucket 계산, drift 알고리즘 실행, event 생성, chart payload 생성 로직을 직접 수행하지 않아야 한다. |
| DSR-NFR-003 | drift server 책임 | drift server는 adapter state, bucket, method run, drift event, analysis payload 생성과 timeseries/event API를 책임진다. |
| DSR-NFR-004 | LLM server 책임 제한 | LLM interpretation server는 chart/component 해석만 수행하고 drift 계산이나 데이터 수집은 하지 않아야 한다. |
| DSR-NFR-005 | payload adapter 명시성 | analysis chart는 반드시 payload adapter와 함께 등록되어야 하며, 암묵적 chart payload 변환에 의존하지 않아야 한다. |
| DSR-NFR-006 | chart catalog 제한 | 관리자는 미리 등록된 chart 목록에서만 analysis chart를 생성/등록해야 한다. |
| DSR-NFR-007 | incremental processing | drift server는 window 단위 incremental processing을 기본으로 하며, 대량 raw data를 한 번에 메모리에 올리지 않아야 한다. |
| DSR-NFR-008 | canonical time 사용 | 내부 window/cursor/bucket/event 처리는 source 원래 시간이 아니라 canonical event_time으로 통일해야 한다. |
| DSR-NFR-010 | 원본 시간 추적 | source_event_time과 source_clock_offset_ms는 분석/진단을 위해 보존해야 한다. |
| DSR-NFR-011 | clock 오류 fail-fast | source_clock_offset_ms가 허용 범위를 넘으면 row 단위 invalid나 경고만으로 처리하지 않고 adapter 사용 불가 상태로 전환해야 한다. |
| DSR-NFR-012 | row 비수신 시 clock 감시 | row가 들어오지 않아도 adapter clock check는 정기적으로 수행되어야 한다. |
| DSR-NFR-013 | streaming detector 입력 단위 | ADWIN 같은 stateful streaming detector도 raw row가 아니라 bucket 대표값을 입력으로 받으며, online성은 bucket 해상도 축소로 조정해야 한다. |
| DSR-NFR-014 | event grouping 지연 | drift_event merge, extend, suppress, incident grouping은 저장 단계에서 수행하지 않고 후속 UI/API view layer 기능으로 분리해야 한다. |
| DSR-NFR-009 | 독립 실행 가능한 service layer | feeder, adapter, collector, detector는 HTTP 없이도 직접 호출 가능한 service class로 구현해야 한다. |

## 8. 초기 구현 범위

초기 구현은 모든 method와 chart를 한 번에 지원하지 않는다. 다음 vertical slice를 먼저 구현한다.

```text
dataset case: CASE-010 stream numeric mean shift
drift method: ADWIN_MEAN_STREAM
analysis chart: CHART-STREAM-001
payload adapter: adwin_mean_stream_to_chart_stream_001
```

이 범위에서 다음 acceptance를 만족하면 1차 구현이 완료된 것으로 본다.

| ID | Acceptance |
| --- | --- |
| DSR-AC-001 | 테스트 feeder가 CASE-010 CSV를 Harness Clock `logicalNow`에 맞춰 테스트 DB에 넣는다. |
| DSR-AC-002 | drift server가 10분 logicalNow 경계마다 10분 window 하나를 가져와 metric bucket을 저장한다. |
| DSR-AC-003 | ADWIN assignment가 등록되고 bucket 생성 후 method_run이 저장된다. |
| DSR-AC-004 | drift 조건 충족 시 drift_event가 생성된다. |
| DSR-AC-005 | source별 timeseries API가 bucket/event를 반환한다. |
| DSR-AC-006 | event analysis API가 CHART-STREAM-001용 chart payload를 반환한다. |
| DSR-AC-007 | analysis payload는 LLM interpretation server에 전달 가능한 chart runtime payload 구조를 가진다. |
