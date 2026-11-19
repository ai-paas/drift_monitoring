# Todo

## 현재 작업 목표

`codex exec`를 사용해 chart interpretation server의 LLM polish 경로를 실제로 검증한다.
무한 반복을 피하기 위해 이번 작업은 아래 체크리스트만 수행하고, 실패 원인이 확인되면 원인을 기록한 뒤 멈춘다.

## 현재 상태

- Chart Builder prototype의 chart component 32개 구현 완료
- 미구현 component: 0개
- 기준 화면: `http://127.0.0.1:8766/builder_prototype.html`
- 재현 차트 화면: `http://127.0.0.1:8766/recreated_charts.html`
- 해석 서버: `http://127.0.0.1:8767/api/health`
- DB 연결: 정상
- rule 기반 `POST /api/interpret/chart`: 정상
- `codex` PowerShell shim(`codex.ps1`)은 execution policy로 막힘
- 사용 가능한 실행 경로: `C:\Users\jklee\AppData\Roaming\npm\codex.cmd exec --sandbox read-only --skip-git-repo-check --color never`
- `..\llm_interpretation_server\run_interpretation_server.cmd`는 `CODEX_EXEC_CMD`가 없으면 위 명령을 기본값으로 설정한다.

## 이번 진행 체크리스트

1. 완료: `codex.cmd` 실행 가능 여부 확인
2. 완료: `codex exec`에 전달할 짧은 고정 prompt로 단독 응답 확인
3. 완료: Python subprocess stdin 전달 시 UTF-8 인코딩 문제 확인 및 수정
4. 완료: `CODEX_EXEC_CMD`를 `codex.cmd exec` 기반 명령으로 설정하고 interpretation server 재시작
5. 완료: `GET /api/health`에서 `codexExec: True` 확인
6. 완료: `POST /api/interpret/chart`에서 component/chart provider가 `codex_exec`로 응답하는지 확인
7. 완료: CHART-ADAPT-001 end-to-end 테스트에서 component 6개와 chart note 모두 `codex_exec` 응답 확인

## 확인된 결과

- 단독 `codex exec` 테스트: 성공
- 서버 subprocess 방식 테스트: 성공
- 서버 health: `database: True`, `codexExec: True`
- CHART-ADAPT-001 API 응답:
  - `ok: true`
  - `componentNotes: 6`
  - component provider: `codex_exec` 6건
  - chart provider: `codex_exec`
  - chart severity: `candidate`
- chart detail은 LLM이 한국어 보고서 문체로 재작성한다.
- chart summary는 현재 rule 기반 summary를 유지하고, detail만 codex polish로 교체된다.

## 중단 조건

- 같은 실패가 2회 반복되면 더 반복하지 않는다.
- `codex exec`가 인증, 네트워크, 모델 접근 문제로 실패하면 서버 코드 수정으로 우회하지 않는다.
- chart layout, components, componentType, dataBinding은 이번 작업에서 수정하지 않는다.
- LLM 출력 schema 강제는 codex exec 연결 확인 뒤 별도 작업으로 진행한다.

## 완료된 component

- `distribution_summary_plot`
- `domain_specific_visual`
- `matrix_view`
- `model_diagnostic_curve`
- `quantile_view`
- `raw_signal_trend`
- `small_multiples`
- `uncertainty_band`
- `window_view`

## 최근 검증

- `node --check web\builder_prototype.js` 통과
- `node --check web\recreated_charts.js` 통과
- `interpretation_server.py` Python compile 통과
- 깨진 문자 패턴 검사 통과: `interpretation_server.py`, `web/recreated_charts.js`, `todo.md`
- `GET /api/health` 응답 정상, database 연결 정상, codex exec 활성화 정상
- `POST /api/interpret/chart` codex exec 기반 해석 응답 정상

## 다음 후보 작업

- LLM 출력 schema 강제
  - component note와 chart note의 허용 필드를 제한한다.
  - LLM은 notes data schema(`title`, `text`, `legend`, `caveats`)만 생성한다.
  - LLM이나 서버가 chart `layout`, `components`, `componentType`, `dataBinding`을 수정하지 못하게 한다.
  - LLM 출력은 JSON schema로 검증하고 실패 시 fallback note를 사용한다.
- chart summary도 codex 결과로 갱신할지, 현재처럼 rule summary + codex detail 구조를 유지할지 결정
- 한 chart당 codex 호출 수가 많으므로 caching 또는 chart-level 단일 호출 구조 검토
- 브라우저에서 `recreated_charts.html`을 열어 해석 버튼/팝업 렌더링 확인
- 저장된 chart payload와 신규 component default config 호환성 확인
- component별 properties schema form 전환
- chart 저장 validation 추가
## 확인된 해석 품질 문제

- CHART-ADAPT-001 codex exec 해석은 숫자 인용 자체는 payload와 대체로 일치한다.
- 그러나 `performance_metric_view`의 online accuracy를 `0.92 >= 0.86`이라는 이유로 drift 후보라고 해석한 것은 잘못된 가능성이 높다.
  - accuracy는 높을수록 좋은 지표이며, 기준 미달/하락을 위험으로 봐야 한다.
  - 현재 서버는 y축 tick `0.86`을 threshold처럼 추정하고 `latest >= threshold`를 candidate로 처리한다.
- `adaptive_model_structure_view`도 y축 tick `40`을 threshold처럼 추정해 `tree size 56 >= 40`을 drift 후보로 판단한다.
  - tree size y tick은 축 눈금일 가능성이 높고 drift threshold로 볼 근거가 없다.
- event marker와 state timeline 해석은 payload 근거와 대체로 일치한다.
- 다음 수정 우선순위: `threshold_from_config()`가 y축 tick을 threshold로 추정하지 않게 하고, component별 metric direction/decision rule을 명시적으로 사용한다.
## 현재 추가 작업: LLM 해석 일반 지침

- 추가: `docs/chart_interpretation_llm_guide.md`
- 목적: LLM이 drift 판정부터 말하지 않고 component role, visual encoding, current evidence, reading rule, caution 순서로 해석하게 한다.
- 서버 반영: `interpretation_server.py`가 component knowledge, rule, signal, data sample을 함께 `codex exec` prompt에 전달한다.
- 함께 수정: y-axis tick을 threshold로 추정하지 않도록 `threshold_from_config()`에서 y_ticks 기반 추정을 제거한다.
## component 단독 해석 테스트 결과

- 대상: `CHART-ADAPT-001.accuracy.0` / `performance_metric_view`
- 결과: 성공
- provider: `codex_exec`
- 개선 확인:
  - component가 무엇을 보여주는지 먼저 설명한다.
  - x축 `time index`, y축 `online accuracy`, data field `time/value`를 설명한다.
  - 현재 payload의 32개 시점, 최신값 0.92, 직전값 0.92, 최근 보합 추세를 설명한다.
  - y축 눈금 0.70/0.78/0.86/0.94를 threshold로 보지 말라고 명시한다.
  - severity는 `normal`로 바뀌었고, `0.92 >= 0.86`을 drift 후보로 해석하던 문제는 사라졌다.

## chart 전체 해석 테스트 결과

- 대상: `CHART-ADAPT-001` 전체 chart endpoint
- 결과: HTTP client timeout
- 원인 추정: 한 chart 요청에서 component별 `codex exec`를 순차로 여러 번 호출한 뒤 chart-level `codex exec`를 추가 호출하기 때문에 시간이 과도하게 길어진다.
- 중단 결정: 같은 전체 chart 호출을 반복하지 않는다.
- 다음 수정 우선순위:
  - chart endpoint에서는 component별 codex 호출을 매번 수행하지 않고 rule/component explanation context를 모아 chart-level codex 1회 호출로 줄인다.
  - 또는 component note cache를 도입한다.
  - UI 호출에는 timeout/fallback 상태를 명시한다.
## 현재 작업: chart 전체 codex exec 1회 호출화

목표: `POST /api/interpret/chart`가 component 수만큼 `codex exec`를 반복하지 않고 chart-level `codex exec` 1회만 호출하게 한다.

범위:
- component 단독 endpoint `/api/interpret/component`는 그대로 component 1개 codex 해석을 유지한다.
- chart endpoint 내부에서는 component note를 rule 기반으로 생성한다.
- chart-level prompt에는 component knowledge, rule 기반 component notes, signal, data sample을 모두 포함한다.
- chart layout, components, componentType, dataBinding은 수정하지 않는다.

완료 조건:
- `interpretation_server.py` compile 통과
- `GET /api/health`에서 `codexExec: True`
- `POST /api/interpret/chart`가 타임아웃 없이 반환
- 응답에서 component provider는 `rule`, chart provider는 `codex_exec`
- CHART-ADAPT-001 전체 응답이 component 설명/증거를 포함하고 y축 눈금을 threshold로 오인하지 않음
## chart 전체 codex exec 1회 호출화 결과

- `POST /api/interpret/chart` 구조 변경 완료
- component 단독 endpoint는 component 1개에 대해 codex exec 유지
- chart endpoint는 component note를 rule 기반으로 생성하고 chart-level codex exec를 1회만 호출
- CHART-ADAPT-001 전체 호출 결과:
  - elapsed: 약 18.9초
  - component provider: `rule` 6건
  - chart provider: `codex_exec`
  - timeout 없음
- 개선 확인:
  - chart detail은 component 역할, 현재 증거, cross-component 흐름을 설명한다.
  - y축 눈금을 threshold로 오인하지 않는다.
  - accuracy 하락(t=19 0.72), replacement(t=23), 이후 회복 흐름을 데이터 근거로 설명한다.
- 남은 이슈:
  - chart summary는 아직 rule 기반 summary라 `drift 후보 신호가 뚜렷하다`처럼 강한 문구가 남는다.
  - 다음 수정 후보: chart-level codex detail의 첫 문장을 summary로 사용하거나, rule summary를 `event/state 전환과 회복 흐름이 관찰된다`처럼 보수적으로 변경한다.
## 현재 작업: chart summary codex 결과 사용

목표: chart-level `codex_exec`가 성공하면 `chartNote.summary`도 기존 rule summary가 아니라 codex 결과에서 생성한다.

범위:
- JSON schema 강제는 이번 작업에서 하지 않는다.
- 우선 codex detail의 첫 의미 있는 문장을 summary로 사용한다.
- component note summary는 그대로 rule 기반 유지한다.

완료 조건:
- `interpretation_server.py` compile 통과
- `POST /api/interpret/chart` 성공
- `chartProvider: codex_exec`
- `chartSummary`가 더 이상 기존 rule 문구(`drift 후보 신호가 뚜렷하다`)를 그대로 사용하지 않음
## chart summary codex 결과 사용 결과

- 구현 완료: chart-level `codex_exec`가 성공하면 `chartNote.summary`를 codex detail의 첫 의미 있는 문장에서 추출한다.
- CHART-ADAPT-001 테스트 결과:
  - elapsed: 약 15.4초
  - chart provider: `codex_exec`
  - component provider: `rule` 6건
  - 기존 rule summary 문구 `drift 후보 신호가 뚜렷하다`는 더 이상 사용되지 않음
  - 새 summary: `CHART-ADAPT-001은 Hoeffding Adaptive Tree가 online accuracy 하락을 감지한 뒤 warning, alternate tree 성장, replacement로 이어지는 적응 과정을 설명하는 chart다`
- 남은 후보 작업:
  - summary 문장 끝 punctuation 보정
  - 향후 JSON schema로 `{summary, detail}`을 직접 받도록 변경
## 현재 작업: codex JSON summary/detail schema

목표: chart-level codex 응답을 자유 텍스트가 아니라 `{summary, detail}` JSON으로 받아 `chartNote.summary`와 `chartNote.detail`에 명확히 반영한다.

범위:
- 우선 chart-level codex 응답에 적용한다.
- component 단독 endpoint는 기존 text polish 구조를 유지한다.
- JSON 파싱 실패 시 기존 자유 텍스트 fallback을 사용한다.

완료 조건:
- JSON schema 파일 추가
- `interpretation_server.py` compile 통과
- `POST /api/interpret/chart` 성공
- `chartProvider: codex_exec`
- `summary`와 `detail`이 JSON 필드 기반으로 분리됨
- summary 문장 끝 punctuation 보정
## codex JSON summary/detail schema 결과

- 추가: `docs/chart_interpretation_output_schema.json`
- 구현: chart-level codex prompt가 `{summary, detail}` JSON object 하나만 출력하도록 요구한다.
- 구현: 서버가 codex 응답 JSON을 파싱해 `chartNote.summary`와 `chartNote.detail`에 분리 반영한다.
- fallback: JSON 파싱 실패 시 기존 자유 텍스트 fallback을 사용한다.
- CHART-ADAPT-001 테스트 결과:
  - elapsed: 약 18.6초
  - chart provider: `codex_exec`
  - component provider: `rule` 6건
  - summary punctuation: 정상
  - summary/detail 분리: 정상
  - summary: `CHART-ADAPT-001은 online accuracy 하락, detector 상태 전환, alternate tree 성장 및 t=23 replacement 이후 회복 패턴을 함께 보여주는 HAT 적응 과정 차트다.`
## 현재 작업: chart interpretation queue API

목표: chart-level `codex exec` 호출을 HTTP 요청 안에서 직접 오래 기다리지 않고, 서버 내부 queue에 job으로 넣고 단일 worker가 순차 처리하게 한다.

범위:
- in-memory queue/result cache로 시작한다.
- 기존 동기식 `/api/interpret/chart`는 호환을 위해 유지한다.
- 새 endpoint 추가:
  - `POST /api/interpret/chart/jobs`: job 생성 또는 payload hash cache hit 반환
  - `GET /api/interpret/chart/jobs/{job_id}`: queued/running/succeeded/failed 상태와 결과 조회
- worker는 한 번에 하나의 codex exec job만 처리한다.
- `web/recreated_charts.js`는 job 생성 후 polling 방식으로 변경한다.

완료 조건:
- `interpretation_server.py` compile 통과
- `web/recreated_charts.js` node check 통과
- health 정상
- job 생성 API가 즉시 job id를 반환
- polling 결과가 `succeeded`와 chart result를 반환
- UI 호출 경로가 `/api/interpret/chart/jobs`를 사용
## chart interpretation queue API 결과

- 구현 완료: in-memory queue + single worker + payload hash cache
- 새 endpoint:
  - `POST /api/interpret/chart/jobs`
  - `GET /api/interpret/chart/jobs/{job_id}`
- 기존 동기 endpoint `/api/interpret/chart`는 호환용으로 유지
- UI 변경: `web/recreated_charts.js`가 job 생성 후 polling으로 결과를 가져온다.
- CHART-ADAPT-001 job 테스트 결과:
  - create response: `queued`, job id 반환 즉시 성공
  - polling: `running` 후 `succeeded`
  - elapsed: 약 16.7초
  - chart provider: `codex_exec`
  - component provider: `rule` 6건
  - 같은 payload 재요청 시 기존 succeeded job을 즉시 반환
- 남은 후보 작업:
  - job store를 DB 테이블로 영속화
  - 오래된 in-memory job 정리 TTL 추가
  - UI polling timeout 문구 개선
## 현재 작업: chart/question cache key 정규화

목표: 같은 chart, 같은 시점 payload, 같은 질문이면 이미 생성된 LLM 응답을 cache에서 반환한다.

범위:
- cache key는 payload 전체를 그대로 쓰지 않고 transient field를 제거한 normalized payload + optional question으로 만든다.
- 제거 대상 예: `requestNonce`, `_requestNonce`, `cacheBust`, `_cacheBust`.
- `POST /api/interpret/chart/jobs`는 optional `question`을 받는다.
- 같은 key의 queued/running/succeeded job은 새 job을 만들지 않고 기존 job을 반환한다.
- question이 있으면 chart-level codex context에 포함한다.
## chart/question cache key 정규화 결과

- 구현 완료: cache key를 normalized payload + question으로 생성한다.
- `requestNonce`, `_requestNonce`, `cacheBust`, `_cacheBust`는 cache key에서 제외한다.
- `POST /api/interpret/chart/jobs`는 optional `question`을 받는다.
- chart-level codex context에 `userQuestion`을 포함한다.
- 검증:
  - 같은 chart payload와 같은 question, 다른 `requestNonce` 요청이 같은 `jobId`를 반환한다.
  - 정상 한국어 question도 UTF-8로 보존된다.
  - cache hit job id: `9f762602-f391-47c6-9135-d29e7cd40df4`
## 2026-06-25 drift_metric_timeseries 분석 chart 해석 서비스 연결
- 완료: `drift_metric_timeseries/web/drift_metric_timeseries_demo.js`의 이벤트 분석 chart 렌더링 경로를 해석 서버 job API(`http://127.0.0.1:8767/api/interpret/chart/jobs`)에 연결했다.
- 동작: 분석 payload를 받은 직후 notes-card 텍스트를 "LLM 해석을 생성하는 중입니다."로 대체해 렌더링하고, job 완료 후 `chartNote`를 notes-card 본문에 넣고 `componentNotes`를 각 chart component의 `interpretationNote`로 붙여 다시 렌더링한다.
- 캐시: 프론트는 chartId/title/data/question 기준으로 동일 분석 payload 해석 결과를 메모리 캐시한다. 서버도 payload/question hash cache를 사용한다.
- 검증: `node --check drift_metric_timeseries/web/drift_metric_timeseries_demo.js` 통과. `8766/api/health`, `8767/api/health` 정상. `embedding_distance` 분석 payload로 해석 job 호출 성공, `provider=codex_exec`, componentNotes 5개, UTF-8 한글 summary 정상 확인.

## 2026-06-25 drift_metric_timeseries 분석 chart note 보정
- 문제: 분석 chart의 area note에 `CHART-ADAPT-001` 템플릿의 정적 설명(`t=1~8에는 accuracy...`)이 남아 있어 LLM 해석보다 먼저 보였다. 이 문구는 현재 `토큰 길이 - 2025-01-01 분석` 데이터와 맞지 않는다.
- 수정: `applyAnalysisInterpretation()`에서 기존 `layout.area.description`을 그대로 사용하지 않고, 대기 중에는 "LLM 해석을 생성하는 중입니다.", 완료 후에는 해석 서버가 반환한 component/chart note로 대체한다.
- 수정: `chart_runtime/chart_runtime.js`의 깨진 component note 버튼 텍스트(`??`, `???? ??`)를 `해석`, `컴포넌트 해석`으로 교체했다.
- 수정: `drift_metric_timeseries_demo.html` cache version을 `v=60`으로 올렸다.
- 검증: `node --check` 통과(`drift_metric_timeseries_demo.js`, `chart_runtime.js`). 서버 HTML/JS 응답의 한글 UTF-8 escape 정상 확인.
## 2026-06-25 drift_metric_timeseries 해석 버튼 중복 제거
- 문제: 분석 chart에서 area header의 `해석` 버튼과 component overlay의 `해석` 버튼이 동시에 생성되어 확대 버튼 옆과 그래프 위 등 여러 위치에 표시됐다.
- 수정: `drift_metric_timeseries_demo.js`의 분석 payload 적용 경로에서 `component.interpretationNote`를 null로 두고, `layout.area.description`도 비워 runtime note 버튼을 만들지 않게 했다.
- 결과: 분석 chart에서는 별도 해석 버튼을 만들지 않고 notes-card 본문만 해석 서버 결과로 대체한다.
- 수정: cache version을 `v=61`로 올렸다.
- 검증: `node --check drift_metric_timeseries_demo.js` 통과, 서버 HTML `v=61` 반영 확인.
## 2026-06-25 drift_metric_timeseries area note 버튼 복구
- 문제: 중복 해석 버튼 제거 과정에서 확대 버튼 옆 area note 버튼까지 사라졌다.
- 수정: component별 `interpretationNote`는 계속 null로 두어 그래프 위 버튼은 만들지 않고, 기존 description이 있던 area에는 `chartNote`를 `description`으로 넣어 확대 버튼 옆 `해석` 버튼을 다시 표시한다.
- 수정: cache version을 `v=62`로 올렸다.
- 검증: `node --check drift_metric_timeseries_demo.js` 통과, 서버 HTML `v=62` 반영 확인.
## 2026-06-25 drift_metric_timeseries area note를 component note로 변경
- 문제: `온라인 정확도 추세` 같은 component area의 `해석` 버튼이 해당 component 해석이 아니라 `CHART-ADAPT-001` chart-level 종합 해석을 표시했다.
- 원인: `applyAnalysisInterpretation()`에서 모든 area description에 `chartNote`를 넣고 있었다.
- 수정: component area는 해당 area의 non-decision component에 대응하는 `componentNotes`를 description으로 사용한다. component overlay 버튼은 계속 만들지 않는다.
- 결과: 확대 버튼 옆 `해석` 버튼은 유지하되, 클릭 시 area/component별 note를 보여준다.
- 수정: cache version을 `v=63`으로 올렸다.
- 검증: `node --check drift_metric_timeseries_demo.js` 통과, 서버 HTML `v=63` 반영 확인.
## 2026-06-25 drift_metric_timeseries chart 전체 해석 버튼 추가
- 요구: chart 전체 해석 버튼은 component area 해석 버튼과 별도로 있어야 한다.
- 수정: 분석 패널 상단 상태 영역 옆에 `전체 해석` 버튼(`analysisChartNote`)을 추가했다.
- 동작: 해석 job 완료 후 `chartNote`가 있으면 `전체 해석` 버튼을 표시하고, 클릭 시 chart-level note popup을 연다.
- 구분: area header의 `해석` 버튼은 계속 component/area note를 표시한다.
- 수정: cache version을 `v=64`로 올렸다.
- 검증: `node --check drift_metric_timeseries_demo.js` 통과, 서버 HTML `v=64`와 `analysisChartNote` 반영 확인.
## 2026-06-25 chart 전체 해석 popup 가독성 개선
- 문제: `전체 해석` popup이 chartNote의 summary/detail을 한 덩어리 문단으로 표시해 읽기 빡빡했다.
- 수정: `formattedChartNoteText()`를 추가해 전체 해석을 `요약`, `차트 목적`, `주요 근거`, `판독`, `주의 및 추가 확인` 섹션으로 나눠 표시한다.
- 수정: note popup 폭을 720px로 넓히고, body에 `white-space: pre-wrap`, 스크롤, line-height를 적용했다.
- 수정: cache version을 `v=65`로 올렸다.
- 검증: `node --check drift_metric_timeseries_demo.js` 통과, 서버 HTML `v=65` 반영 확인.
## 2026-06-25 drift_metric_timeseries 해석 요청 in-flight dedupe
- 문제: 같은 분석 chart를 열 때마다 브라우저가 같은 해석 job 생성 요청을 반복할 수 있다.
- 수정: `analysisInterpretationRequests` Map을 추가해 같은 payload/question cache key의 진행 중 Promise를 재사용한다.
- 동작: 이미 완료된 결과는 `analysisInterpretationCache`에서 반환하고, 진행 중인 요청은 새 POST 없이 기존 Promise를 공유한다. 완료/실패 후 in-flight Map에서 제거한다.
- 서버 dedupe: 기존 interpretation server의 payload/question hash 기반 job dedupe와 함께 이중 방어로 동작한다.
- 수정: cache version을 `v=66`으로 올렸다.
- 검증: `node --check drift_metric_timeseries_demo.js` 통과, 서버 HTML `v=66` 반영 확인.
## 2026-06-25 drift_metric_timeseries 해석 버튼 pending/ready 상태 표시
- 요구: 분석 chart를 열 때 자동으로 해석 요청을 큐에 넣고, 응답 전에는 해석 버튼을 흐리게 표시했다가 응답 후 색을 바꾼다.
- 수정: `setAnalysisInterpretationState(idle|pending|ready|failed)`를 추가했다.
- 동작: 분석 payload 렌더 직후 `pending` 상태로 전체 해석 버튼을 `전체 해석 준비 중` disabled 상태로 표시하고, area note 버튼은 흐리게/클릭 불가 처리한다.
- 동작: 해석 결과 수신 후 `ready` 상태로 전체 해석 버튼과 area note 버튼을 파란 계열 활성 상태로 표시한다.
- 동작: 실패 시 `failed` 상태로 흐리게 표시한다. 닫기/배경 클릭/ESC에서는 `idle`로 초기화한다.
- 수정: cache version을 `v=67`로 올렸다.
- 검증: `node --check drift_metric_timeseries_demo.js` 통과, 서버 HTML `v=67` 반영 확인.
## 2026-06-25 chart-level 해석 component 근거 종합 강화
- 문제: chart-level 해석이 chart id/template 중심으로 작성되어 `온라인 정확도 추세`, `감지기 상태 타임라인`, `트리 크기 추세` 등 각 component 해석을 충분히 종합하지 못했다.
- 원인: `chart_note()` draft가 `chart_interpretation_guide.interpretation_template_text`를 먼저 넣어 stale/example 숫자가 LLM 근거처럼 사용될 수 있었다.
- 수정: chart guide template 문구를 current evidence에서 제거하고, `componentContexts[].ruleNote`, `signal`, `dataSample`을 source of truth로 명시했다.
- 수정: `component_chart_context()`에 `areaTitle`, `areaRole`을 추가해 component 의미를 더 잘 전달한다.
- 수정: LLM prompt에 chart synthesis requirements를 추가해 component별 근거 → cross-component temporal/order synthesis → caution 순서로 작성하게 했다.
- 수정: `docs/chart_interpretation_llm_guide.md`에 componentContexts/ruleNote/signal/dataSample 기반 종합 원칙과 adaptive tree chart 판독 원칙을 명시했다.
- 재시작: 8767 해석 서버를 재시작해 in-memory cache를 초기화했다. 새 PID는 9972.
- 검증: AST syntax parse 통과. `GET /api/health` 정상(`database: True`, `codexExec: True`). `token_length` 2025-01-01 분석 payload job 성공.
- 검증 결과: 새 chartNote는 `최신 값 0.72`, `이벤트 t=1`, `normal→warning→alternate→replace`, `트리 보조값 64.0` 등 component별 현재 근거를 사용했고, 이전 template 값 중심 설명은 사라졌다.
## 2026-06-25 component-level 해석 형식성 검토 및 개선
- 검토 대상: `token_length`, `2025-01-01` 분석 payload의 `componentNotes`.
- 발견 문제: component note가 rule 기반으로 `최신 값/최근 추세`, `상태 흐름`, `이벤트 시점` 정도만 말해 형식적이었다. `domain_specific_visual` notes 영역도 그래프 component처럼 해석되고 있었다.
- 수정: `line_signal()`에 first/min/max/minX/maxX/totalChange/secondaryFirst/secondaryMax를 추가했다.
- 수정: `timeline_signal()`에 role별 start/end segment를 추가했다.
- 수정: `event_signal()`에 event type/time/label 세부 정보를 추가했다.
- 수정: `component_note_text()`를 component type별로 구체화했다.
  - `performance_metric_view`: 시작값, 최신값, 최근 변화, 최솟값/최댓값 위치, 임계값 부재 시 해석 한계 설명.
  - `adaptive_model_structure_view`: main tree 변화와 secondary/alternate tree 최신/최대값 설명.
  - `state_timeline`: 상태 전환 순서와 각 상태 구간 설명.
  - `event_marker`: event type과 time 표시.
  - `notes` area: 그래프가 아니라 보조 notes 영역이므로 전체 해석 근거에서 제외해야 함을 명시.
- 재시작: 8767 해석 서버를 재시작해 cache 초기화. 새 PID는 10624.
- 검증: AST syntax parse 통과, health 정상. `token_length` 분석 job 성공.
- 검증 결과: `온라인 정확도`는 시작 0.749→최신 0.72 감소, 최솟값 t=32, 최댓값 t=10을 설명한다. `트리 크기`는 main 48→28 감소와 secondary 최신/최대 64를 설명한다. `상태 타임라인`은 normal/warning/alternate/replace 구간을 설명한다.
- 남은 관찰: `replacement@1`, `normal(1~1)`처럼 이벤트 index가 압축되어 보이는 것은 분석 payload 생성 로직의 event index 스케일링 결과다. 필요하면 날짜 기반 표시를 추가로 보강한다.
