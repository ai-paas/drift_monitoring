# TODO

## 2026-06-26 Drift Algorithm 구현 TODO

- 목표:
  - `drift_algorithm` 순차 구현 `DM-025 ~ DM-056` 범위를 완료했다.
  - 진행 방식은 계속 manager/worker로 유지한다.
  - worker는 method별 상세 설계서 작성, manager는 설계 검토 후 구현/테스트/진행 로그 갱신을 담당한다.

- 현재 완료:
  - `DM-025 LSDD`
  - `DM-003 Chi-square Test`
  - `DM-004 Fisher's Exact Test`
  - `DM-005 G-test`
  - `DM-006 PSI`
  - `DM-007 KL Divergence`
  - `DM-008 Jensen-Shannon Distance`
  - `DM-009 Hellinger Distance`
  - `DM-010 Total Variation Distance`
  - `DM-011 L-Infinity Distance`
  - `DM-012 Bhattacharyya Distance`
  - `DM-013 Histogram Intersection Normalized Complement`
  - `DM-034 SPRT`
  - `DM-026 ADWIN`
  - `DM-027 KSWIN`
  - `DM-028 Page-Hinkley Test`
  - `DM-029 CUSUM`
  - `DM-030 EWMA`
  - `DM-031 Geometric Moving Average`
  - `DM-032 BOCD`
  - `DM-033 SeqDrift`
  - `DM-035 DDM`
  - `DM-036 RDDM`
  - `DM-037 EDDM`
  - `DM-038 ECDD-WT`
  - `DM-039 HDDM-A`
  - `DM-040 HDDM-W`
  - `DM-041 STEPD`
  - `DM-042 Hotelling T2`
  - `DM-043 MEWMA`
  - `DM-044 Mahalanobis Distance`
  - `DM-045 OCDD`
  - `DM-046 Feature Map Drift`
  - `DM-047 Autoencoder Representation Drift`
  - `DM-048 Graph Embedding Drift`
  - `DM-049 LLM Query / Semantic Distance 기반 감지`
  - `DM-050 Model Uncertainty Drift`
  - `DM-051 SHAP Drift`
  - `DM-052 Tree Feature 기반 감지`
  - `DM-053 Classifier Embedding Drift Detection`
  - `DM-054 Text Domain Classifier Drift`
  - `DM-055 HAT`
  - `DM-056 DriftRetrainingClassifier`

- 다음 작업:
  - 일반 구현 범위 `DM-001 ~ DM-056`을 완료했다.
  - 다음 의사결정 대상은 구현 범위 확대, API 통합, 문서 정리, 또는 전체 regression 자동화다.

- 이어서 진행할 후보:
  - 보류 항목 없음

- 주의할 점:
  - streaming 계열은 현재 finite DataFrame replay contract로 통일한다.
  - p-value가 없는 control chart/streaming detector는 p-value를 만들지 않는다.
  - label/error stream, distance stream, empirical calibration이 필요한 variant는 별도 입력 계약이 없으면 `not_applicable`로 보류한다.
  - 공통 helper 변경 시 기존 구현 회귀 테스트를 실행한다.
  - `_prepare_adwin_stream`은 실제로 여러 streaming method가 공유하므로 추후 이름을 `_prepare_numeric_stream_replay`로 정리하는 방안을 검토한다.

- 오늘 작업 기록:
  - `작업일지/2026-06-25.md`
  - `drift_algorithm/docs/progress_log.md`의 `2026-06-26 - DM-032 BOCD Implementation Loop`
  - `drift_algorithm/docs/progress_log.md`의 `2026-06-26 - DM-033 SeqDrift Implementation Loop`
  - `drift_algorithm/docs/progress_log.md`의 `2026-06-26 - DM-035 DDM Implementation Loop`
  - `drift_algorithm/docs/progress_log.md`의 `2026-06-26 - DM-036 RDDM Implementation Loop`
  - `drift_algorithm/docs/progress_log.md`의 `2026-06-26 - DM-037 EDDM Implementation Loop`
  - `drift_algorithm/docs/progress_log.md`의 `2026-06-26 - DM-038 ECDD-WT Implementation Loop`
  - `drift_algorithm/docs/progress_log.md`의 `2026-06-26 - DM-039 HDDM-A Implementation Loop`
  - `drift_algorithm/docs/progress_log.md`의 `2026-06-26 - DM-040 HDDM-W Implementation Loop`
  - `drift_algorithm/docs/progress_log.md`의 `2026-06-26 - DM-041 STEPD Implementation Loop`
  - `drift_algorithm/docs/progress_log.md`의 `2026-06-26 - DM-042 Hotelling T2 Implementation Loop`
  - `drift_algorithm/docs/progress_log.md`의 `2026-06-26 - DM-043 MEWMA Implementation Loop`
  - `drift_algorithm/docs/progress_log.md`의 `2026-06-26 - DM-044 Mahalanobis Distance Implementation Loop`
  - `drift_algorithm/docs/progress_log.md`의 `2026-06-26 - DM-045 OCDD Implementation Loop`
  - `drift_algorithm/docs/progress_log.md`의 `2026-06-26 - DM-046 Feature Map Drift Implementation Loop`
  - `drift_algorithm/docs/progress_log.md`의 `2026-06-26 - DM-047 Autoencoder Representation Drift Implementation Loop`
  - `drift_algorithm/docs/progress_log.md`의 `2026-06-26 - DM-048 Graph Embedding Drift Implementation Loop`
  - `drift_algorithm/docs/progress_log.md`의 `2026-06-26 - DM-049 LLM Query / Semantic Distance Implementation Loop`
  - `drift_algorithm/docs/progress_log.md`의 `2026-06-26 - DM-050 Model Uncertainty Drift Implementation Loop`
  - `drift_algorithm/docs/progress_log.md`의 `2026-06-26 - DM-051 SHAP Drift Implementation Loop`
  - `drift_algorithm/docs/progress_log.md`의 `2026-06-26 - DM-052 Tree Feature 기반 감지 Implementation Loop`
  - `drift_algorithm/docs/progress_log.md`의 `2026-06-26 - DM-053 Classifier Embedding Drift Detection Implementation Loop`
  - `drift_algorithm/docs/progress_log.md`의 `2026-06-26 - DM-054 Text Domain Classifier Drift Implementation Loop`
  - `drift_algorithm/docs/progress_log.md`의 `2026-06-26 - DM-055 HAT Implementation Loop`
  - `drift_algorithm/docs/progress_log.md`의 `2026-06-26 - DM-056 DriftRetrainingClassifier Implementation Loop`
  - `drift_algorithm/docs/progress_log.md`의 `2026-06-26 - DM-003 Chi-square Test Implementation Loop`
  - `drift_algorithm/docs/progress_log.md`의 `2026-06-26 - DM-004 Fisher's Exact Test Implementation Loop`
  - `drift_algorithm/docs/progress_log.md`의 `2026-06-26 - DM-005 G-test Implementation Loop`
  - `drift_algorithm/docs/progress_log.md`의 `2026-06-26 - DM-006 PSI Implementation Loop`

## 2026-06-25

- chart_builder 해석 서버의 chart component 해석은 그래프의 시각 부호를 먼저 설명해야 한다.
- 완료:
  - `interpretation_server.py`의 component rule note에 시각 요소 설명을 연결했다.
  - 온라인 정확도 component는 파란 실선, 둥근 관측 점, 붉은 세로 점선 event marker, 붉은 강조점을 설명한다.
  - 상태 timeline과 event marker component도 막대/점선/강조점 의미를 detail에 포함하도록 보정했다.
  - 서버 재시작 후 `CHART-ADAPT-001.accuracy.0` job 응답에서 시각 요소 설명이 포함되는 것을 확인했다.
- 남은 확인:
  - 브라우저 팝업에서 컴포넌트별 해석 버튼이 같은 문구를 표시하는지 화면으로 확인한다.
  - 전체 chart 해석이 component별 시각 요소 설명을 과도하게 생략하지 않는지 추가 샘플로 확인한다.

## 2026-06-25 Component LLM 해석 검증 TODO

- 목표:
  - 모든 chart component type에 실제 `dataBinding.source` 데이터를 붙인 payload를 만들고, chart 전체 해석 1회 호출 안에서 LLM이 각 component를 제대로 해석하는지 확인한다.
  - rule fallback으로 내려가는 graph/tabular component가 남아 있으면 prompt, guide, payload, schema 중 원인을 찾아 수정한다.
- 현재까지 확인:
  - 분석 chart 3개 테스트 완료:
    - `CHART-ADAPT-001`
    - `CHART-CTRL-001`
    - `CHART-MV-002`
  - 추가 대표 chart 테스트 완료:
    - `CHART-CAT-001`
    - `CHART-CLS-001`
    - `CHART-BOCD-001`
    - `CHART-CAT-004`
    - `CHART-EDF-004`
    - `CHART-ADAPT-002`
    - `CHART-CTRL-003`
    - `CHART-ERR-003`
    - `CHART-EXPL-002`
    - `CHART-MEAN-001`
  - 누락됐던 `bar_chart`, `contribution_view`, `heatmap`, `matrix_view`, `trend_line`은 prompt 보강 후 `provider=codex_exec`로 재검증했다.
- 남은 작업:
  - recreated chart payload 전체를 대상으로 chart별 queue 해석 job을 순차 실행한다.
  - 각 component instance별로 다음 항목을 기록한다.
    - `chartId`
    - `componentInstanceId`
    - `componentType`
    - `dataBinding.source`
    - data row count
    - `provider`
    - summary/detail에 실제 수치 또는 category가 포함되는지
    - 선, 점, 막대, 색상, cell, marker, band, node, edge 등 시각 요소 설명이 포함되는지
  - `domain_specific_visual` 중 notes/legend 역할만 하는 component는 graph evidence 대상에서 제외한다.
  - graph/tabular evidence가 있는데 `provider=rule`이거나 componentNote가 누락된 경우 실패로 기록한다.
  - 실패 component type은 DB guide와 `chart_interpretation` prompt를 보강한 뒤 같은 chart를 재테스트한다.
- 완료 기준:
  - 데이터가 있는 모든 graph/tabular component instance가 chart 전체 해석 1회 호출 결과의 `componentNotes`에 포함된다.
  - 해당 note의 `provider`가 `codex_exec`이다.
  - 해석 문장에 현재 payload의 실제 데이터 값, category, 구간, marker 또는 시각 부호가 최소 하나 이상 반영된다.
  - 전체 결과를 작업일지에 chart/component type별로 요약한다.

## 2026-06-22

- 탐지 방법 변종 설명 보완을 계속 진행한다.
- 현재 진행 상황:
  - 전체 변종 설명: `167개`
  - 완료: `167개`
  - 남음: `0개`
- 진행 방식:
  - manager/worker 방식으로 5개 또는 10개씩 작업한다.
  - worker는 지정된 `algorithm_variants/*_algorithm_variants.md` 파일과 변종 섹션만 수정한다.
  - manager는 diff 검토, 화면용 설명 데이터 재생성, DB 반영, 검증 후 commit한다.
- 각 묶음의 필수 검증:
  - `python charts\generate_description_html.py`
  - 범위 밖 자동 생성 차트 파일 복원
  - `python db\import_drift_db.py`
  - `docker cp db\load_data.sql lci-postgres:/tmp/drift_load_data.sql`
  - `docker exec lci-postgres psql -U postgres -d drift_monitoring -v ON_ERROR_STOP=1 -f /tmp/drift_load_data.sql`
  - `node --check charts\gallery.js`
  - `git diff --check`
  - PostgreSQL `document_section`에서 수정한 변종 heading 확인
- 다음 후보 작업:
  - 탐지 방법 변종 설명 보완은 파일 기준 `167개` 모두 완료했다.
  - 추가 작업은 화면 확인 중 발견되는 문구 보정 또는 누락 링크 보정이 있을 때만 진행한다.
- 웹에서 설명이 사용자가 읽기 쉬운지 계속 확인한다.
- URL:

```text
http://127.0.0.1:8765/gallery.html
```

## 2026-06-12

- 차트 작업은 기준 문서의 모든 chart id 구현을 완료했다.
- 기준 문서: `chart_docs/drift_method_variant_chart_guide.md`
- 차트 작성 후 반영 위치:
  - 원본 코드: `charts/`
  - PNG 이미지: `charts/output/`
  - 해석 문서: `chart_docs/drift_chart_interpretation_guide.md`에서 family별 문서 확인
- 작성 방식:
  - HTML/CSS/JS로 차트 원본을 만든다.
  - 차트 제목, 축, 범례, 해석 문구는 가능한 한 한글로 작성한다.
  - Chrome headless로 PNG를 생성한다.
  - 생성된 PNG를 확인한 뒤 해석 문서에 이미지와 해석 방법을 추가한다.
