# Drift Method Runtime Contract

## 1. 목적

이 문서는 Drift Server가 drift method runtime function을 호출하는 표준 contract를 정의한다.

목표:

```text
stateful streaming detector와 lookback/batch detector를 하나의 호출 모델로 수용한다.
runtime function은 DB에 직접 접근하지 않는다.
method_run, method_state, drift_event 저장 책임은 DriftDetector가 가진다.
Drift Server는 drift 알고리즘 자체를 새로 구현하지 않고 drift_algorithm_impl의 기존 구현을 wrapper로 호출한다.
```

## 2. 기본 실행 흐름

```text
DriftDetector
  -> source_method_assignment 조회
  -> source_feature 조회
  -> method_state 조회
  -> new bucket 조회
  -> recent buckets 조회
  -> runtime function 호출
  -> method_run 저장
  -> method_state 갱신
  -> warning/drift이면 drift_event 생성
```

runtime function은 순수 계산 함수에 가깝게 유지한다.
v1에서 runtime function은 기존 `drift_algorithm_impl` 알고리즘을 Drift Server 표준 input/output contract에 맞게 감싸는 wrapper다.

```text
입력:
  assignment, source, feature, bucket, previous state, params, threshold

출력:
  run status, level, score, next state, event candidate, metrics, diagnostics
```

## 3. Method Type

v1 contract는 다음 method type을 수용한다.

```text
stateful_streaming
  previousState + newBucket 중심으로 처리한다.
  nextState 반환이 중요하다.
  입력 단위는 raw row가 아니라 bucket value다.
  예: ADWIN, Page-Hinkley

lookback_batch
  최근 N개 bucket을 보고 판단한다.
  previousState가 없어도 된다.
  예: rolling z-score, rolling mean comparison

baseline_comparison
  baseline period와 current period를 비교한다.
  windowConfig에 baseline/current 범위가 필요하다.
  예: PSI, KS, Wasserstein distance

supervised_performance
  label, prediction, error rate 등 supervised signal이 필요하다.
  v1 범위 밖이다.
```

v1 대상:

```text
ADWIN_MEAN_STREAM
  methodType = stateful_streaming
  runtimeMethodKey = adwin_mean_stream

BAYESIAN_ONLINE_CHANGE_POINT_GAUSSIAN / BOCD_HAZARD_RATE_VARIANT / BOCD_PREDICTIVE_PROBABILITY
  methodType = stateful_streaming
  runtimeMethodKey = bocd_stream
  wrapper = drift_server/app/runtime_methods/bocd_stream.py
  algorithm = drift_algorithm.methods.streamingchangedetector.detect_bocd
  execution = bucket mean values are replayed as a finite numeric stream and split into reference/current windows for the algorithm implementation.
  supported chart demo coverage = CHART-BOCD-001

ONE_SIDED_UPPER_CUSUM / ONE_SIDED_LOWER_CUSUM / TWO_SIDED_CUSUM
  methodType = stateful_streaming
  runtimeMethodKey = cusum_stream
  wrapper = drift_server/app/runtime_methods/cusum_stream.py
  algorithm = drift_algorithm.methods.streamingchangedetector.detect_cusum
  execution = bucket mean values are replayed as a finite stream and split into reference/current windows for the algorithm implementation.
  supported chart demo coverage = CHART-ANNOT-001, CHART-CTRL-001

CUSUM_ON_DISTANCE_STREAM
  status = blocked
  reason = drift_algorithm_impl currently returns not_applicable until an upstream distance-stream input contract is approved.

EWMA_UNIVARIATE_CONTROL_CHART / EWMA_ONE_SIDED
  methodType = stateful_streaming
  runtimeMethodKey = ewma_stream
  wrapper = drift_server/app/runtime_methods/smoothing_control_stream.py
  algorithm = drift_algorithm.methods.streamingchangedetector.detect_ewma
  execution = bucket mean values are replayed as a finite stream and split into reference/current windows for the algorithm implementation.
  supported chart demo coverage = CHART-ANNOT-001, CHART-CTRL-002

GMA_CONTROL_CHART / GMA_ONE_SIDED
  methodType = stateful_streaming
  runtimeMethodKey = gma_stream
  wrapper = drift_server/app/runtime_methods/smoothing_control_stream.py
  algorithm = drift_algorithm.methods.streamingchangedetector.detect_geometric_moving_average
  execution = bucket mean values are replayed as a finite stream and split into reference/current windows for the algorithm implementation.
  supported chart demo coverage = CHART-ANNOT-001, CHART-CTRL-002

EWMA_BASELINE_REPLAY_THRESHOLD / GMA_WITH_EMPIRICAL_LIMIT
  status = blocked
  reason = drift_algorithm_impl currently returns not_applicable until empirical baseline replay calibration contracts are approved.

HDDM_A_HOEFFDING_BOUND / HDDM_A_WARNING_DRIFT / HDDM_A_TWO_SIDED
  methodType = supervised_performance
  runtimeMethodKey = hddm_a_error_rate_stream
  wrapper = drift_server/app/runtime_methods/hddm_error_rate_stream.py
  algorithm = drift_algorithm.methods.supervisedconceptdriftdetector.detect_hddm_a
  execution = prediction-log buckets provide error rows in payload.errors and are replayed as a finite error stream.
  supported chart demo coverage = CHART-ERR-005

HDDM_W_WEIGHTED_AVERAGE / HDDM_W_WARNING_DRIFT / HDDM_W_RECENT_ERROR_WEIGHTING
  methodType = supervised_performance
  runtimeMethodKey = hddm_w_error_rate_stream
  wrapper = drift_server/app/runtime_methods/hddm_error_rate_stream.py
  algorithm = drift_algorithm.methods.supervisedconceptdriftdetector.detect_hddm_w
  execution = prediction-log buckets provide error rows in payload.errors and are replayed as a finite error stream.
  supported chart demo coverage = CHART-ERR-005

ECDD_WT_STANDARD / ECDD_WT_WARNING_DRIFT / ECDD_WT_ERROR_STREAM
  methodType = supervised_performance
  runtimeMethodKey = ecdd_wt_error_rate_stream
  wrapper = drift_server/app/runtime_methods/ecdd_wt_error_rate_stream.py
  algorithm = drift_algorithm.methods.supervisedconceptdriftdetector.detect_ecdd_wt
  execution = prediction-log buckets provide error rows in payload.errors and are replayed as a finite error stream.
  supported chart demo coverage = CHART-ERR-004

DDM_WARNING_BUFFER / DDM_CLASS_SPECIFIC
  methodType = supervised_performance
  runtimeMethodKey = ddm_warning_buffer, ddm_class_specific
  wrapper = drift_server/app/runtime_methods/ddm_error_rate_stream.py
  algorithm = drift_algorithm.methods.supervisedconceptdriftdetector.detect_ddm
  execution = prediction-log buckets provide payload.errors rows. The wrapper preserves error, y_true, y_pred, and confidence fields and replays them as a finite supervised error stream.
  supported chart demo coverage = CHART-ERR-001

RDDM_REACTIVE_RESET
  methodType = supervised_performance
  runtimeMethodKey = rddm_reactive_reset
  wrapper = drift_server/app/runtime_methods/rddm_error_rate_stream.py
  algorithm = drift_algorithm.methods.supervisedconceptdriftdetector.detect_rddm
  execution = prediction-log buckets provide error rows in payload.errors and are replayed as a finite error stream.
  supported chart demo coverage = CHART-ERR-002

EDDM_WARNING_DRIFT / EDDM_GRADUAL_DRIFT
  methodType = supervised_performance
  runtimeMethodKey = eddm_warning_drift, eddm_gradual_drift
  wrapper = drift_server/app/runtime_methods/eddm_error_rate_stream.py
  algorithm = drift_algorithm.methods.supervisedconceptdriftdetector.detect_eddm
  execution = prediction-log buckets provide error rows in payload.errors and are replayed as a finite error stream.
  supported chart demo coverage = CHART-ERR-003

UNIVARIATE_ENERGY_DISTANCE / ENERGY_DISTANCE_PERMUTATION_TEST
  methodType = baseline_comparison
  runtimeMethodKey = energy_distance_window
  wrapper = drift_server/app/runtime_methods/generic_distribution_ecdf_window.py
  algorithm = drift_algorithm.methods.batchdistributioncomparison.detect_energy_distance
  execution = numeric distribution buckets provide payload.values with reference/current periods and are passed as a finite baseline/current comparison window.
  supported chart demo coverage = CHART-MV-001

MULTIVARIATE_ENERGY_DISTANCE
  status = blocked
  reason = drift_algorithm_impl currently returns not_applicable until a multivariate feature matrix input contract is approved.

LEAST_SQUARES_DENSITY_DIFFERENCE / PERMUTATION_LSDD
  methodType = baseline_comparison
  runtimeMethodKey = lsdd_window
  wrapper = drift_server/app/runtime_methods/generic_distribution_ecdf_window.py
  algorithm = drift_algorithm.methods.batchdistributioncomparison.detect_lsdd
  execution = numeric distribution buckets provide payload.values with reference/current periods and are passed as a finite baseline/current comparison window.
  supported chart demo coverage = CHART-MV-003

LSDD_WITH_PREPROCESSING
  status = blocked
  reason = drift_algorithm_impl currently returns not_applicable until a preprocessing input contract is approved.

KERNEL_MMD_BIASED / KERNEL_MMD_UNBIASED
  methodType = baseline_comparison
  runtimeMethodKey = mmd_window
  wrapper = drift_server/app/runtime_methods/generic_distribution_ecdf_window.py
  algorithm = drift_algorithm.methods.batchdistributioncomparison.detect_mmd
  execution = numeric distribution buckets provide payload.values with reference/current periods and are passed as a finite baseline/current comparison window.
  supported chart demo coverage = CHART-MV-002

LINEAR_TIME_MMD / STREAMING_MMD
  status = blocked
  reason = drift_algorithm_impl currently returns not_applicable until linear-time and streaming MMD input contracts are approved.

SEQDRIFT1 / SEQDRIFT2
  methodType = baseline_comparison
  runtimeMethodKey = seqdrift_numeric_window
  wrapper = drift_server/app/runtime_methods/seqdrift_numeric_window.py
  algorithm = drift_algorithm.methods.streamingchangedetector.detect_seqdrift
  execution = numeric distribution buckets provide payload.values with reference/current periods and are replayed as a finite SeqDrift stream.
  supported chart demo coverage = CHART-STREAM-004

SPRT_BERNOULLI_ERROR_RATE / SPRT_GAUSSIAN_MEAN_SHIFT
  methodType = stateful_streaming
  runtimeMethodKey = sprt_bernoulli_error_rate, sprt_gaussian_mean_shift
  wrapper = drift_server/app/runtime_methods/sprt_stream.py
  algorithm = drift_algorithm.methods.streamingchangedetector.detect_sprt
  execution = Bernoulli SPRT replays prediction-log payload.errors as a finite 0/1 stream. Gaussian SPRT replays numeric bucket mean_value as a finite mean-shift stream.
  supported chart demo coverage = CHART-STREAM-005

STEPD_ACCURACY_WINDOW / STEPD_WARNING_DRIFT / STEPD_SUPERVISED_STREAM
  methodType = supervised_performance
  runtimeMethodKey = stepd_error_rate_stream
  wrapper = drift_server/app/runtime_methods/stepd_error_rate_stream.py
  algorithm = drift_algorithm.methods.supervisedconceptdriftdetector.detect_stepd
  execution = prediction-log buckets provide error rows in payload.errors and are replayed as a finite error stream.
  supported chart demo coverage = CHART-ERR-006
```

해상도 확장 정책:

```text
stateful_streaming method는 별도 raw stream contract를 만들지 않는다.
더 촘촘한 online drift가 필요하면 bucket resolution 또는 aggregate_interval_minutes를 줄인다.
예: 10m bucket -> 1m bucket -> 10s bucket
ADWIN은 각 bucket의 대표값(meanValue 등)을 순차 입력으로 받는다.
```

## 4. Runtime Input Contract

표준 입력:

```json
{
  "assignment": {
    "assignmentId": "assign-case010-adwin",
    "sourceId": "case-010",
    "adapterId": "case-010-adwin",
    "featureId": "metric",
    "methodVariantId": 123,
    "algorithmImplementationId": 45,
    "runtimeMethodKey": "adwin_mean_stream",
    "params": {},
    "threshold": {},
    "windowConfig": {}
  },
  "source": {
    "sourceId": "case-010",
    "sourceType": "test_db",
    "sourceTitle": "CASE-010 stream numeric mean shift"
  },
  "feature": {
    "featureId": "metric",
    "featureLabel": "Metric",
    "valueType": "numeric",
    "unit": null
  },
  "newBucket": {
    "bucketId": "bucket-001",
    "bucketStart": "2026-01-01T00:00:00Z",
    "bucketEnd": "2026-01-01T00:10:00Z",
    "rowCount": 10,
    "meanValue": 0.42,
    "minValue": 0.31,
    "maxValue": 0.55,
    "stddevValue": 0.04,
    "status": "ok",
    "payload": {}
  },
  "recentBuckets": [],
  "previousState": {},
  "executionContext": {
    "methodRunId": "run-001",
    "windowStart": "2026-01-01T00:00:00Z",
    "windowEnd": "2026-01-01T00:10:00Z",
    "isEmptyBucket": false,
    "methodType": "stateful_streaming"
  }
}
```

### 4.1 assignment

`assignment`는 source에 어떤 method를 어떤 설정으로 적용할지 나타낸다.

필수 필드:

```text
assignmentId
sourceId
featureId
methodVariantId
runtimeMethodKey
params
threshold
windowConfig
```

`algorithmImplementationId`는 가능하면 포함한다. 단, catalog 또는 runtime registry가 아직 연결되지 않은 테스트에서는 null일 수 있다.

### 4.2 newBucket

이번 실행의 중심 bucket이다.

`stateful_streaming` method는 주로 `newBucket`과 `previousState`를 사용한다.
bucket resolution이 작아질수록 stateful streaming detector는 더 촘촘한 online stream에 가깝게 동작한다.

### 4.3 recentBuckets

lookback method가 사용할 최근 bucket 목록이다.

정렬:

```text
bucketStart 오름차순
```

`windowConfig.lookbackBuckets`에 따라 DriftDetector가 조회한다.

### 4.4 previousState

이전 실행 이후 저장된 detector state다.

저장 위치:

```text
drift_server.method_state.state_json
```

state가 없는 첫 실행에서는 `{}`를 전달한다.

### 4.5 executionContext

이번 실행의 runtime context다.

```text
methodRunId:
  DriftDetector가 생성한 실행 ID

windowStart/windowEnd:
  method_run window

isEmptyBucket:
  newBucket.rowCount = 0 또는 newBucket.status = empty

methodType:
  stateful_streaming | lookback_batch | baseline_comparison | supervised_performance
```

## 5. Runtime Output Contract

표준 출력:

```json
{
  "runStatus": "success",
  "level": "normal",
  "score": 0.0,
  "event": null,
  "nextState": {},
  "metrics": {},
  "diagnostics": {},
  "payloadHints": {}
}
```

### 5.1 runStatus

허용 값:

```text
success
skipped
error
```

runtime function에서 예외가 발생하면 DriftDetector가 잡아서 `method_run.run_status = error`로 저장한다.

### 5.2 level

허용 값:

```text
normal
warning
drift
unknown
```

event 생성 기준:

```text
level = warning 또는 drift
  -> drift_event 생성 후보
```

### 5.3 score

drift 정도를 나타내는 numeric score다.

method마다 의미가 다를 수 있으므로 `metrics`에 상세 값을 함께 넣는다.

### 5.4 event

runtime function은 event 후보 정보를 반환할 수 있다.

예:

```json
{
  "eventStart": "2026-01-01T00:00:00Z",
  "eventEnd": "2026-01-01T00:10:00Z",
  "eventLevel": "drift",
  "eventTitle": "ADWIN mean drift detected",
  "eventPayload": {}
}
```

`event`가 null이어도 `level`이 warning/drift이면 DriftDetector가 기본 event를 만든다.

기본 event 구간:

```text
event_start = method_run.window_start
event_end = method_run.window_end
```

### 5.5 nextState

다음 실행에 사용할 detector state다.

```text
stateful_streaming:
  nextState 반환 권장 또는 필수

lookback_batch:
  nextState 생략 가능
```

DriftDetector가 `method_state.state_json`에 저장한다.

### 5.6 metrics

method-specific numeric 결과다.

예:

```json
{
  "mean": 0.42,
  "adwinWidth": 128,
  "estimatedMean": 0.41,
  "delta": 0.002
}
```

`method_run.result_json`에 저장된다.

### 5.7 diagnostics

debugging 또는 해석 보조 정보다.

예:

```json
{
  "inputBucketCount": 1,
  "stateWasEmpty": false,
  "reason": "mean changed above threshold"
}
```

### 5.8 payloadHints

analysis chart payload adapter가 참고할 수 있는 힌트다.

예:

```json
{
  "highlightBucketStart": "2026-01-01T00:00:00Z",
  "baselineRange": ["2026-01-01T00:00:00Z", "2026-01-01T12:00:00Z"]
}
```

## 6. Runtime Function Signature

Python function signature:

```python
def run_method(input: dict) -> dict:
    ...
```

v1 ADWIN 예:

```python
def run_adwin_mean_stream(input: dict) -> dict:
    ...
```

이 함수는 ADWIN 알고리즘 자체 구현이 아니다. `drift_algorithm_impl`에 이미 있는 구현을 호출하고, 입력/출력을 이 문서의 contract로 변환한다.

runtime registry:

```python
RUNTIME_METHODS = {
    "adwin_mean_stream": run_adwin_mean_stream,
    "generic_distribution_ecdf_window": run_generic_distribution_ecdf_window,
    "generic_probability_distance_window": run_generic_probability_distance_window,
    "anderson_darling_window": run_generic_distribution_ecdf_window,
    "cramer_von_mises_window": run_generic_distribution_ecdf_window,
    "epps_singleton_window": run_generic_distribution_ecdf_window,
    "energy_distance_window": run_generic_distribution_ecdf_window,
    "univariate_energy_distance": run_generic_distribution_ecdf_window,
    "energy_distance_permutation_test": run_generic_distribution_ecdf_window,
    "lsdd_window": run_generic_distribution_ecdf_window,
    "least_squares_density_difference": run_generic_distribution_ecdf_window,
    "permutation_lsdd": run_generic_distribution_ecdf_window,
    "mmd_window": run_generic_distribution_ecdf_window,
    "kernel_mmd_biased": run_generic_distribution_ecdf_window,
    "kernel_mmd_unbiased": run_generic_distribution_ecdf_window,
    "generic_statistical_test_window": run_generic_statistical_test_window,
    "baumgartner_weiss_schindler_window": run_generic_statistical_test_window,
    "f_test_variance_window": run_generic_statistical_test_window,
    "generic_categorical_contingency_window": run_generic_categorical_contingency_window,
    "chi_square_window": run_generic_categorical_contingency_window,
    "fisher_exact_window": run_generic_categorical_contingency_window,
    "g_test_window": run_generic_categorical_contingency_window,
    "probability_distance_window": run_generic_probability_distance_window,
    "kl_divergence_window": run_generic_probability_distance_window,
    "jensen_shannon_window": run_generic_probability_distance_window,
    "hellinger_window": run_generic_probability_distance_window,
    "total_variation_window": run_generic_probability_distance_window,
    "l_infinity_window": run_generic_probability_distance_window,
    "bhattacharyya_window": run_generic_probability_distance_window,
    "hinc_window": run_generic_probability_distance_window,
    "ks_test_window": run_generic_distribution_ecdf_window,
    "kuiper_window": run_generic_distribution_ecdf_window,
    "levene_window": run_generic_statistical_test_window,
    "mann_whitney_window": run_generic_statistical_test_window,
    "kswin_numeric_window": run_kswin_numeric_window,
    "kswin_numeric_stream": run_kswin_numeric_window,
    "kswin_standard": run_kswin_numeric_window,
    "kswin_with_subsampling": run_kswin_numeric_window,
    "page_hinkley_stream": run_page_hinkley_stream,
    "page_hinkley_decrease": run_page_hinkley_stream,
    "page_hinkley_increase": run_page_hinkley_stream,
    "t_test_window": run_generic_statistical_test_window,
    "wasserstein_numeric_window": run_wasserstein_numeric_window,
    "wasserstein_1d_exact": run_wasserstein_numeric_window,
    "wasserstein_approx_histogram": run_wasserstein_numeric_window,
    "wasserstein_window_trend": run_wasserstein_numeric_window,
}
```

Variant alias keys are additive. They route catalog-level method variants to the same runtime wrapper while preserving
the wrapper output shape defined by this contract.

runtime function은 다음을 하지 않는다.

```text
DB 조회
DB 저장
HTTP 호출
drift_event insert
method_state 직접 저장
method_run 직접 저장
```

## 7. Method State 갱신 규칙

DriftDetector가 `nextState`를 저장한다.

성공 시:

```text
runStatus = success
  -> method_state.state_json = output.nextState
  -> method_state.last_bucket_end = input.executionContext.windowEnd
```

skipped 시:

```text
runStatus = skipped
  -> 기본적으로 method_state 갱신하지 않음
```

error 시:

```text
runStatus = error
  -> method_state 갱신하지 않음
```

runtime function이 `nextState`를 반환하지 않으면:

```text
stateful_streaming:
  error 또는 diagnostics warning 처리

lookback_batch:
  허용
```

## 8. Method Run 저장 규칙

DriftDetector가 `method_run`을 저장한다.

저장 내용:

```text
assignment_id
source_id
adapter_id
feature_id
window_start
window_end
input_bucket_count
run_status
score
level
result_json
error_message
```

`result_json` 권장 구조:

```json
{
  "metrics": {},
  "diagnostics": {},
  "payloadHints": {},
  "event": {}
}
```

## 9. Drift Event 생성 규칙

DriftDetector가 event를 생성한다.

조건:

```text
output.level in (warning, drift)
```

생성 규칙:

```text
output.event.eventStart가 있으면 사용
없으면 method_run.window_start 사용

output.event.eventEnd가 있으면 사용
없으면 method_run.window_end 사용

output.event.eventPayload가 있으면 drift_event.payload_json에 포함
output.metrics/diagnostics/payloadHints도 payload_json에 포함 가능
```

v1 idempotency:

```text
method_run_id당 drift_event 최대 1개
겹치는 event_start/event_end를 가진 event도 method_run이 다르면 별도 drift_event로 저장
DriftDetector는 drift_event를 자동 merge/extend/suppress하지 않음
```

## 10. Empty Bucket 처리

기본 정책:

```text
newBucket.status = empty 또는 rowCount = 0
  -> runtime function 실행하지 않음
  -> method_run.run_status = skipped
  -> method_run.level = unknown
  -> method_state 갱신하지 않음
  -> drift_event 생성하지 않음
```

method별로 empty bucket 처리가 필요하면 다음 설정으로 허용할 수 있다.

```json
{
  "windowConfig": {
    "allowEmptyBucket": true
  }
}
```

`allowEmptyBucket = true`이면 DriftDetector가 runtime function을 호출한다.

## 11. ADWIN_MEAN_STREAM v1 Contract

v1 ADWIN runtime:

```text
runtimeMethodKey = adwin_mean_stream
methodType = stateful_streaming
input value = newBucket.meanValue
state = previousState
```

V2에서 더 빠른 ADWIN 반응이 필요하면 raw row를 직접 입력하는 별도 contract를 만들지 않고, `metric_bucket.resolution`과 adapter의 `aggregate_interval_minutes`를 줄인다.

입력 bucket이 empty면 기본적으로 skipped 처리한다.

출력 예:

```json
{
  "runStatus": "success",
  "level": "drift",
  "score": 0.91,
  "event": {
    "eventLevel": "drift",
    "eventTitle": "ADWIN mean drift detected"
  },
  "nextState": {
    "windowValues": [],
    "estimatedMean": 0.52
  },
  "metrics": {
    "estimatedMean": 0.52,
    "delta": 0.002,
    "width": 128
  },
  "diagnostics": {
    "reason": "mean shift detected"
  },
  "payloadHints": {
    "highlightBucketEnd": "2026-01-01T00:10:00Z"
  }
}
```

초기 구현에서도 Drift Server 안에 ADWIN 알고리즘을 새로 넣지 않는다. 기존 `drift_algorithm_impl` 구현을 호출하되, wrapper는 이 contract를 반드시 지켜야 한다.

## 12. 관련 테이블

```text
drift_server.source_method_assignment
drift_server.method_state
drift_server.method_run
drift_server.drift_event
drift_server.metric_bucket
```

## 13. Multivariate Process Window Contract

Sprint 60 adds an additive multivariate bucket/runtime path for Hotelling T2 and Mahalanobis Distance.

```text
adapterType = test_db_multivariate_window
bucket.feature_id = multivariate
payload.featureColumns = configured feature column list
payload.values[] = { time, period, features, metric }
runtimeMethodKey = hotelling_t2_window | mahalanobis_window | multivariate_process_window
```

Supported variants:

```text
MEWMA_STANDARD
MEWMA_WITH_MAHALANOBIS_D2
HOTELLING_T2_ONE_SAMPLE_PHASE_II
HOTELLING_T2_TWO_SAMPLE
REGULARIZED_HOTELLING_T2
SAMPLE_MAHALANOBIS_OUTLIER
WINDOW_MEAN_MAHALANOBIS
ROBUST_MAHALANOBIS
```

The wrapper calls `drift_algorithm_impl.drift_algorithm.methods.multivariateprocesscontrol` and converts a successful `DriftResult` into the standard Drift Server output shape:

```json
{
  "runStatus": "success",
  "level": "normal | drift",
  "score": 0.0,
  "event": null,
  "nextState": {
    "lastBucketEnd": "2026-12-01T02:00:00Z",
    "seenBuckets": 1,
    "lastRowCount": 50
  },
  "metrics": {
    "statistic": 0.0,
    "threshold": null,
    "measurements": {}
  },
  "diagnostics": {
    "runtime": "hotelling_t2_window",
    "implementation": "drift_algorithm_impl_multivariate_process_control",
    "algorithmImplAttempted": true,
    "algorithmImplSucceeded": true
  },
  "payloadHints": {
    "highlightBucketEnd": "2026-12-01T02:00:00Z"
  }
}
```

Existing single-metric, numeric-distribution, prediction-log, and categorical-count bucket shapes are unchanged.

## 14. Model Uncertainty Window Contract

Sprint 64 adds an additive model-uncertainty bucket/runtime path for representation drift variants that compare reference and current prediction uncertainty distributions.

```text
adapterType = test_db_multivariate_window
bucket.feature_id = multivariate
payload.featureColumns = configured probability, prediction, variance, or metric columns
payload.values[] = { time, period, features, metric }
runtimeMethodKey = softmax_confidence_drift | entropy_drift | predictive_variance_drift | model_uncertainty_window
```

Supported variants:

```text
SOFTMAX_CONFIDENCE_DRIFT
ENTROPY_DRIFT
PREDICTIVE_VARIANCE_DRIFT
```

The wrapper calls `drift_algorithm_impl.drift_algorithm.methods.representationdriftmethod.detect_model_uncertainty_drift` and converts a successful `DriftResult` into the standard Drift Server output shape:

```json
{
  "runStatus": "success",
  "level": "normal | drift",
  "score": 0.0,
  "event": null,
  "nextState": {
    "lastBucketEnd": "2027-01-01T02:00:00Z",
    "seenBuckets": 1,
    "lastRowCount": 60
  },
  "metrics": {
    "statistic": 0.0,
    "threshold": null,
    "measurements": {}
  },
  "diagnostics": {
    "runtime": "model_uncertainty_window",
    "implementation": "drift_algorithm_impl_model_uncertainty",
    "algorithmImplAttempted": true,
    "algorithmImplSucceeded": true
  },
  "payloadHints": {
    "highlightBucketEnd": "2027-01-01T02:00:00Z"
  }
}
```

This contract reuses the multivariate bucket payload shape from Sprint 60 and does not change existing single-metric, numeric-distribution, prediction-log, categorical-count, or multivariate-process bucket contracts.

`runtimeMethodKey=softmax_confidence_drift` has dedicated incremental state behavior. Reference rows from successive buckets build a bounded baseline, and current rows build a bounded comparison window. Once both configured minimum sample sizes are available, the runtime invokes the same model-uncertainty algorithm using the accumulated reference/current rows. The default limits are 5,000 reference rows and 1,000 current rows and can be overridden with `referenceSampleLimit` and `currentSampleLimit`. Other model-uncertainty runtime keys continue to evaluate only the current bucket payload.

## 15. OCDD Window Contract

Sprint 65 adds an additive OCDD bucket/runtime path for anomaly-score drift variants that compare reference and current representation feature vectors.

```text
adapterType = test_db_multivariate_window
bucket.feature_id = multivariate
payload.featureColumns = configured representation or embedding feature columns
payload.values[] = { time, period, features, metric }
runtimeMethodKey = one_class_svm_drift | isolation_forest_drift_score | autoencoder_reconstruction_drift | ocdd_window
```

Supported variants:

```text
ONE_CLASS_SVM_DRIFT
ISOLATION_FOREST_DRIFT_SCORE
AUTOENCODER_RECONSTRUCTION_DRIFT
```

The wrapper calls `drift_algorithm_impl.drift_algorithm.methods.representationdriftmethod.detect_ocdd` and converts a successful `DriftResult` into the standard Drift Server output shape.

This contract reuses the multivariate bucket payload shape from Sprint 60 and does not change existing bucket contracts.

## 16. Classifier Embedding Window Contract

Sprint 66 adds an additive classifier-embedding bucket/runtime path for domain-classifier drift variants that compare reference and current embedding feature vectors.

```text
adapterType = test_db_multivariate_window
bucket.feature_id = multivariate
payload.featureColumns = configured embedding feature columns
payload.values[] = { time, period, features, metric }
runtimeMethodKey = domain_classifier_roc_auc | domain_classifier_probability_drift | cross_validated_domain_classifier | classifier_embedding_window
```

Supported variants:

```text
DOMAIN_CLASSIFIER_ROC_AUC
DOMAIN_CLASSIFIER_PROBABILITY_DRIFT
CROSS_VALIDATED_DOMAIN_CLASSIFIER
```

The wrapper calls `drift_algorithm_impl.drift_algorithm.methods.domainclassifiermethod.detect_classifier_embedding_drift_detection` and converts a successful `DriftResult` into the standard Drift Server output shape.

This contract reuses the multivariate bucket payload shape from Sprint 60 and does not change existing bucket contracts.

## 17. SHAP Window Contract

Sprint 67 adds an additive SHAP bucket/runtime path for explanation drift variants that compare reference and current SHAP value vectors.

```text
adapterType = test_db_multivariate_window
bucket.feature_id = multivariate
payload.featureColumns = configured SHAP value columns
payload.attributeColumns = optional non-numeric attribute columns such as class labels
payload.values[] = { time, period, features, attributes, metric }
runtimeMethodKey = shap_value_distribution_test | global_importance_rank_shift | class_conditional_shap_drift | shap_window
```

Supported variants:

```text
SHAP_VALUE_DISTRIBUTION_TEST
GLOBAL_IMPORTANCE_RANK_SHIFT
CLASS_CONDITIONAL_SHAP_DRIFT
```

The wrapper calls `drift_algorithm_impl.drift_algorithm.methods.explanationdriftmethod.detect_shap_drift` and converts a successful `DriftResult` into the standard Drift Server output shape.

`attributes` and `attributeColumns` are additive to the multivariate payload shape. Existing consumers that only read `features` and `featureColumns` remain unchanged.

## 18. Feature Map Window Contract

Sprint 68 adds an additive feature-map bucket/runtime path for representation drift variants that compare reference and current model feature-map vectors.

```text
adapterType = test_db_multivariate_window
bucket.feature_id = multivariate
payload.featureColumns = configured feature-map activation columns
payload.values[] = { time, period, features, metric }
runtimeMethodKey = model_feature_map_ks | model_feature_map_mmd | layerwise_feature_map_drift | feature_map_window
```

Supported variants:

```text
MODEL_FEATURE_MAP_KS
MODEL_FEATURE_MAP_MMD
LAYERWISE_FEATURE_MAP_DRIFT
```

The wrapper calls `drift_algorithm_impl.drift_algorithm.methods.representationdriftmethod.detect_feature_map_drift` and converts a successful `DriftResult` into the standard Drift Server output shape.

This contract reuses the multivariate bucket payload shape from Sprint 60 and does not change existing bucket contracts.

## 19. Autoencoder Representation Window Contract

Sprint 69 adds an additive autoencoder-representation bucket/runtime path for representation drift variants that compare reference and current latent or reconstruction-derived vectors.

```text
adapterType = test_db_multivariate_window
bucket.feature_id = multivariate
payload.featureColumns = configured latent or reconstruction input columns
payload.values[] = { time, period, features, metric }
runtimeMethodKey = latent_space_drift | reconstruction_error_drift | autoencoder_domain_classifier | autoencoder_representation_window
```

Supported variants:

```text
LATENT_SPACE_DRIFT
RECONSTRUCTION_ERROR_DRIFT
AUTOENCODER_DOMAIN_CLASSIFIER
```

The wrapper calls `drift_algorithm_impl.drift_algorithm.methods.representationdriftmethod.detect_autoencoder_representation_drift` and converts a successful `DriftResult` into the standard Drift Server output shape.

This contract reuses the multivariate bucket payload shape from Sprint 60 and does not change existing bucket contracts.

## 20. Graph Embedding Window Contract

Sprint 70 adds an additive graph-embedding bucket/runtime path for representation drift variants that compare reference and current graph or node embedding vectors.

```text
adapterType = test_db_multivariate_window
bucket.feature_id = multivariate
payload.featureColumns = configured graph embedding columns
payload.attributeColumns = optional non-numeric node group columns
payload.values[] = { time, period, features, attributes, metric }
runtimeMethodKey = graph_embedding_mmd | graph_embedding_centroid_shift | node_representation_drift | graph_embedding_window
```

Supported variants:

```text
GRAPH_EMBEDDING_MMD
GRAPH_EMBEDDING_CENTROID_SHIFT
NODE_REPRESENTATION_DRIFT
```

The wrapper calls `drift_algorithm_impl.drift_algorithm.methods.representationdriftmethod.detect_graph_embedding_drift` and converts a successful `DriftResult` into the standard Drift Server output shape.

This contract reuses the multivariate bucket payload shape from Sprint 60 and the additive `attributes` payload extension from Sprint 67. Existing consumers that only read `features` and `featureColumns` remain unchanged.

## 21. LLM Query Semantic Window Contract

Sprint 71 adds an additive LLM-query semantic bucket/runtime path for embedding and topic-shift variants.

```text
adapterType = test_db_multivariate_window
bucket.feature_id = multivariate
payload.featureColumns = configured embedding columns
payload.attributeColumns = optional non-numeric topic/category columns
payload.values[] = { time, period, features, attributes, metric }
runtimeMethodKey = query_centroid_cosine_shift | text_domain_classifier_drift | topic_distribution_shift | llm_query_semantic_window
```

Supported variants:

```text
QUERY_CENTROID_COSINE_SHIFT
TEXT_DOMAIN_CLASSIFIER_DRIFT
TOPIC_DISTRIBUTION_SHIFT
```

The wrapper calls `drift_algorithm_impl.drift_algorithm.methods.representationdriftmethod.detect_llm_query_semantic_distance` and converts a successful `DriftResult` into the standard Drift Server output shape.

This contract reuses the multivariate bucket payload shape from Sprint 60 and the additive `attributes` payload extension from Sprint 67. Existing consumers that only read `features` and `featureColumns` remain unchanged.

## 22. Text Domain Classifier Window Contract

Sprint 72 adds an additive text-domain-classifier bucket/runtime path for text domain classifier and descriptor drift variants.

```text
adapterType = test_db_multivariate_window
bucket.feature_id = multivariate
payload.featureColumns = configured embedding or descriptor columns
payload.values[] = { time, period, features, metric }
runtimeMethodKey = text_domain_classifier_roc_auc | text_domain_classifier_stat_test | text_descriptor_drift | text_domain_classifier_window
```

Supported variants:

```text
TEXT_DOMAIN_CLASSIFIER_ROC_AUC
TEXT_DOMAIN_CLASSIFIER_STAT_TEST
TEXT_DESCRIPTOR_DRIFT
```

The wrapper calls `drift_algorithm_impl.drift_algorithm.methods.domainclassifiermethod.detect_text_domain_classifier_drift` and converts a successful `DriftResult` into the standard Drift Server output shape.

This contract reuses the multivariate bucket payload shape from Sprint 60. Existing consumers that only read `features` and `featureColumns` remain unchanged.

## 23. Drift Retraining Window Contract

Sprint 73 adds an additive operational-adaptation bucket/runtime path for DriftRetrainingClassifier variants that replay reference/current operational metric windows.

```text
adapterType = test_db_multivariate_window
bucket.feature_id = multivariate
payload.featureColumns = configured metric, champion, challenger, retraining, and promotion columns
payload.values[] = { time, period, features, metric }
runtimeMethodKey = drift_retraining_with_adwin | drift_retraining_with_page_hinkley | drift_retraining_champion_challenger | drift_retraining_window
```

Supported variants:

```text
DRIFT_RETRAINING_WITH_ADWIN
DRIFT_RETRAINING_WITH_PAGE_HINKLEY
DRIFT_RETRAINING_CHAMPION_CHALLENGER
```

The wrapper calls `drift_algorithm_impl.drift_algorithm.methods.operationaladaptationmethod.detect_driftretrainingclassifier` and converts a successful `DriftResult` into the standard Drift Server output shape.

This contract reuses the multivariate bucket payload shape from Sprint 60. Existing consumers that only read other runtime keys remain unchanged.

## 24. HAT Window Contract

Sprint 74 adds an additive operational-adaptation bucket/runtime path for HAT variants that replay reference/current adaptive tree monitoring logs.

```text
adapterType = test_db_multivariate_window
bucket.feature_id = multivariate
payload.featureColumns = configured error, accuracy, alternate-created, and replacement columns
payload.attributeColumns = optional node/group columns
payload.values[] = { time, period, features, attributes, metric }
runtimeMethodKey = hat_adwin_node_monitoring | hat_alternate_tree_replacement | hat_window
```

Supported variants:

```text
HAT_ADWIN_NODE_MONITORING
HAT_ALTERNATE_TREE_REPLACEMENT
```

The wrapper calls `drift_algorithm_impl.drift_algorithm.methods.operationaladaptationmethod.detect_hat` and converts a successful `DriftResult` into the standard Drift Server output shape.

This contract reuses the multivariate bucket payload shape from Sprint 60 and the additive `attributes` payload extension from Sprint 67. Existing consumers that only read `features` and `featureColumns` remain unchanged.

## 25. Control Variant Runtime Contract

Sprint 75 promotes additional control-chart variants through existing numeric stream runtime wrappers.

```text
adapterType = test_db_numeric_stream
bucket.feature_id = metric
bucket.mean_value = numeric aggregate for the current bucket
runtimeMethodKey = cusum_on_distance_stream | ewma_baseline_replay_threshold | gma_with_empirical_limit
```

Supported variants:

```text
CUSUM_ON_DISTANCE_STREAM
EWMA_BASELINE_REPLAY_THRESHOLD
GMA_WITH_EMPIRICAL_LIMIT
```

The wrappers reuse the existing CUSUM/EWMA/GMA Drift Server output shape and call `drift_algorithm_impl.drift_algorithm.methods.streamingchangedetector` detectors. Sprint 75 makes these variants executable in the algorithm implementation by treating the current harness numeric stream as the approved finite replay signal for demo/runtime validation.

Existing runtime keys and their output shape remain unchanged.

## 26. Sliced Wasserstein Runtime Contract

Sprint 76 promotes `SLICED_WASSERSTEIN_EMBEDDING` through the existing numeric distribution runtime wrapper.

```text
adapterType = test_db_numeric_distribution_window
bucket.feature_id = score
payload.values[] = { time, period, value }
runtimeMethodKey = sliced_wasserstein_embedding
```

The implementation treats the finite replay value stream as a single projected embedding dimension and calls `drift_algorithm_impl.drift_algorithm.methods.batchdistributioncomparison.detect_wasserstein_distance`.

Supported variant:

```text
SLICED_WASSERSTEIN_EMBEDDING
```

Existing Wasserstein runtime output shape remains unchanged. The algorithm metadata adds `projection_policy=single_projected_numeric_stream` and `projection_count=1` for this finite replay path.

## 27. Multivariate Distribution Variant Runtime Contract

Sprint 77 promotes additional multivariate distribution variants through the existing generic distribution runtime wrapper.

```text
adapterType = test_db_numeric_distribution_window
bucket.feature_id = score
payload.values[] = { time, period, value }
runtimeMethodKey = multivariate_energy_distance | linear_time_mmd | streaming_mmd | lsdd_with_preprocessing
```

Supported variants:

```text
MULTIVARIATE_ENERGY_DISTANCE
LINEAR_TIME_MMD
STREAMING_MMD
LSDD_WITH_PREPROCESSING
```

The implementation treats the finite replay value stream as a single projected numeric dimension and calls the existing `drift_algorithm_impl.drift_algorithm.methods.batchdistributioncomparison` detectors through `run_generic_distribution_ecdf_window`.

Existing generic distribution runtime output shape remains unchanged. The algorithm metadata adds projection/runtime policy fields such as `projection_policy`, `projection_count`, `runtime_policy`, and `preprocessing_policy` for this finite replay path.

Explicit `feature_cols`, `embedding_cols`, or callable preprocessing inputs remain out of scope for this runtime path.

## 28. ADWIN Projected Stream Runtime Contract

Sprint 78 promotes additional ADWIN stream variants through the existing ADWIN numeric stream runtime wrapper.

```text
adapterType = test_db_numeric_stream
bucket.feature_id = metric
bucket.mean_value = numeric aggregate for the current bucket
runtimeMethodKey = adwin_error_rate | adwin_distance_stream
```

Supported variants:

```text
ADWIN_ERROR_RATE
ADWIN_DISTANCE_STREAM
```

The implementation treats the finite replay bucket mean stream as a projected numeric stream. `ADWIN_ERROR_RATE` records `stream_semantics=projected_error_rate_stream`, and `ADWIN_DISTANCE_STREAM` records `stream_semantics=projected_distance_stream`.

Existing ADWIN runtime output shape remains unchanged. Raw `y_true`/`y_pred` supervised inputs and explicit distance-window construction remain out of scope for this projected demo/runtime path.

## 29. 관련 정책 문서

```text
time_and_cursor_model.md
idempotency_and_locking.md
implementation_scope_v1.md
```

## 30. Generic Metric Threshold Runtime Contract

Sprint 79 promotes the generic fallback threshold variant through a deterministic threshold runtime wrapper.

```text
adapterType = test_db_numeric_stream
bucket.feature_id = metric
bucket.mean_value = numeric aggregate for the current bucket
runtimeMethodKey = generic_metric_threshold_drift
```

Supported variant:

```text
GENERIC_METRIC_THRESHOLD_DRIFT
```

The wrapper evaluates the current bucket mean against `params.threshold` with `params.direction`.
It emits the standard Drift Server output shape with `metrics.measurements` containing `DRIFT_ALARM_STATE`, `CURRENT_VALUE`, `THRESHOLD`, `DIRECTION`, and `PROCESSED_COUNT`.

The runtime is deterministic and records `diagnostics.implementation=deterministic_threshold`.
No existing runtime key or payload shape is changed.

## 31. Tree Feature Runtime Contract

Sprint 80 promotes the Tree Feature explanation drift variants through a multivariate window runtime wrapper.

```text
adapterType = test_db_multivariate_window
bucket.feature_id = multivariate
payload.values[] = { time, period, features, attributes, metric }
runtimeMethodKey = time_feature_split_detector | domain_classifier_tree
```

Supported variants:

```text
TIME_FEATURE_SPLIT_DETECTOR
DOMAIN_CLASSIFIER_TREE
```

The wrapper calls `drift_algorithm_impl.drift_algorithm.methods.explanationdriftmethod.detect_tree_feature`.
For `TIME_FEATURE_SPLIT_DETECTOR`, the wrapper can synthesize `period_indicator` from reference/current period labels when the source bucket does not persist that feature column.

The output follows the standard Drift Server runtime shape and records `diagnostics.implementation=drift_algorithm_impl_tree_feature`.
No existing runtime key or payload shape is changed.
