# Sprint 17 V2 Catalog Inventory

## 1. 목적

이 문서는 V2 Catalog-driven 확장을 시작하기 전에 현재 repo에 흩어져 있는 catalog 원천을 정리한다.

V1은 `CASE-010 + adwin_mean_stream + CHART-STREAM-001` 중심으로 동작했다. V2에서는 dataset, adapter, method, chart 조합을 늘려야 하므로 어떤 파일이 source of truth인지 먼저 고정한다.

## 2. Catalog Source of Truth

| Catalog | 현재 원천 | 역할 | Sprint 17 판단 |
| --- | --- | --- | --- |
| Dataset catalog | `테스트데이터/representative_dataset_cases.csv` | 대표 drift dataset case 16개 | V2 상위 dataset 후보 원천 |
| Dataset-method-chart mapping | `테스트데이터/chart_method_dataset_mapping.csv` | 188개 chart-method pair를 dataset case에 연결 | V2 compatibility 후보 원천 |
| Chart-method catalog | `테스트데이터/chart_method_links.csv` | chart와 method variant 188개 연결 | method x chart compatibility 원천 |
| Runtime chart payloads | `chart_runtime/payloads/runtime_chart_payloads.json` | 53개 chart runtime payload template | chart runtime template 원천 |
| Payload adapter bindings | `drift_control_plane/drift_server/app/payload_adapter/bindings/*.json` | method event/context를 chart payload data source에 연결 | server payload binding 원천 |
| Payload adapter coverage | `drift_control_plane/testing/payload_adapter_coverage_report.json` | 188개 binding coverage 결과 | binding completeness evidence |
| Harness scenarios | `drift_control_plane/testing/harness/scenarios/*.json` | 현재 실행 가능한 E2E scenario | executable matrix row 원천 |
| Runtime method registry | `drift_control_plane/drift_server/app/drift/runtime_registry.py` | 실제 server가 실행할 runtime method key | executable method 원천 |

## 3. 현재 수량

| 항목 | 수량 | 확인 결과 |
| --- | ---: | --- |
| representative dataset case | 16 | `CASE-001` ~ `CASE-016` |
| chart runtime template | 53 | `runtime_chart_payloads.json` |
| chart-method pair | 188 | `chart_method_links.csv` |
| registered payload binding | 188 | coverage report 기준 |
| passed payload binding | 188 | coverage report 기준 |
| executable runtime method | 1 | `adwin_mean_stream` |
| harness scenario | 7 | `case010_mode_a/b`, `case011`~`case015` |

## 4. Dataset Inventory

| Case | Signal | Target chart families | Target method categories | V2 상태 |
| --- | --- | --- | --- | --- |
| CASE-001 | numeric location shift | EDF, DIST, MEAN, RANK, DISTSHAPE | BatchDistributionComparison | catalog 후보 |
| CASE-002 | numeric tail/shape change | EDF, DISTSHAPE, PROB, HIST | BatchDistributionComparison | catalog 후보 |
| CASE-003 | variance/scale change | VAR, MEAN, RANK | BatchDistributionComparison | catalog 후보 |
| CASE-004 | bin proportion shift | PSI, HIST, PROB, CAT | BatchDistributionComparison | catalog 후보 |
| CASE-005 | categorical mix shift | CAT, PROB, PSI, TEXT | BatchDistributionComparison, RepresentationDriftMethod | catalog 후보 |
| CASE-006 | binary event rate change | CAT, STREAM, ERR | BatchDistributionComparison, StreamingChangeDetector, SupervisedConceptDriftDetector | catalog 후보 |
| CASE-007 | probability vector shift | PROB, CAT | BatchDistributionComparison | catalog 후보 |
| CASE-008 | embedding centroid shift | MV, REP, CLS, TEXT | BatchDistributionComparison, RepresentationDriftMethod, DomainClassifierMethod | catalog 후보 |
| CASE-009 | anomaly/density change | ANOM, MV, REP, UNC | RepresentationDriftMethod, MultivariateProcessControl | catalog 후보 |
| CASE-010 | online mean shift | STREAM, CTRL, BOCD | StreamingChangeDetector | V1 executable |
| CASE-011 | error/performance degradation | ERR, ADAPT, STREAM, UNC | SupervisedConceptDriftDetector, OperationalAdaptationMethod, StreamingChangeDetector | V2 candidate |
| CASE-012 | supervised concept boundary shift | ERR, CLS, EXPL | SupervisedConceptDriftDetector, DomainClassifierMethod, ExplanationDriftMethod | V2 candidate |
| CASE-013 | text topic/semantic shift | TEXT, PROB, CAT, REP | RepresentationDriftMethod, DomainClassifierMethod | V2 candidate |
| CASE-014 | explanation importance shift | EXPL, ANNOT | ExplanationDriftMethod | V2 candidate |
| CASE-015 | annotation label quality shift | ANNOT, UNC, CLS | DomainClassifierMethod, RepresentationDriftMethod | V2 candidate |
| CASE-016 | graph/feature-map representation shift | REP, MV, ANOM | RepresentationDriftMethod | catalog 후보 |

## 5. Executable vs Catalog Candidate

현재 V2 catalog 후보는 많지만, 실제 Drift Server runtime registry에서 실행 가능한 method는 `adwin_mean_stream` 하나다.

```text
executable:
  runtimeMethodKey = adwin_mean_stream
  methodVariantKey = ADWIN_MEAN_STREAM
  chartId = CHART-STREAM-001
  payloadAdapterKey = adwin_mean_stream_to_chart_stream_001

candidate only:
  chart_method_dataset_mapping.csv에 존재하지만 runtime registry에 아직 없음
  payload binding coverage는 통과했지만 실제 detector execution은 아직 없음
```

## 6. CASE-011 주의점

현재 Harness의 `case011_mode_a.json`은 실제 ADWIN success path 검증을 위해 `CASE-011_long_stream_numeric_mean_shift` 데이터를 사용한다.

반면 대표 dataset catalog의 `CASE-011`은 `stream_error_rate_and_performance`다. 즉, 이름은 같지만 목적이 다르다.

```text
V1/Sprint 8~16 CASE-011:
  목적 = real ADWIN long stream success path
  method = adwin_mean_stream
  chart = CHART-STREAM-001

V2 representative CASE-011:
  목적 = error/performance degradation catalog 확장
  후보 chart = ERR, ADAPT, STREAM, UNC
  후보 method = DDM, EDDM, HDDM, HAT, retraining 등
```

Sprint 18 이후에는 이 혼동을 줄이기 위해 V1 technical scenario id와 V2 representative dataset id를 분리해야 한다.

## 7. Coverage Gap

| 영역 | 현재 상태 | Gap |
| --- | --- | --- |
| Chart runtime template | 53개 있음 | visual smoke는 가능 |
| Payload adapter binding | 188개 있음, coverage pass | actual method output과 연결한 E2E는 제한적 |
| Runtime method | 1개 실행 가능 | V2 method 확장 전 registry/wrapper 추가 필요 |
| Harness matrix | 단일 scenario 실행 가능 | matrix row 반복 실행기 없음 |
| PyQt6 UI | scenario 단건 실행/조회 가능 | matrix run 목록/요약 없음 |

