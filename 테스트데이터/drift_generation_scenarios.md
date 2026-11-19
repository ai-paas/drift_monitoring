# Drift 데이터 생성 시나리오

## 1. 공통 데이터 흐름

모든 대표 케이스는 같은 흐름을 따른다.

```text
case definition
  -> base reference distribution
  -> drift pattern selection
  -> windowed synthetic data
  -> method-specific input adapter
  -> method result / expected signal
  -> chart input payload
  -> chart-method row copies dataset reference
```

`chart_method_links.csv`의 188개 row는 직접 데이터를 소유하지 않는다. 각 row는 `dataset_case_id`, `drift_pattern`, `source_dataset_id`, `copy_from_dataset_id`를 통해 대표 데이터 산출물을 참조한다.

## 2. Drift 패턴 정의

### abrupt

특정 시점 이후 분포 또는 성능 지표가 계단식으로 바뀐다.

```text
t < drift_start: baseline
t >= drift_start: drifted
```

사용 대상: KS, PSI, ADWIN, CUSUM, Fisher, DDM, domain classifier처럼 차이를 명확히 보여야 하는 smoke test.

### gradual

window가 진행될수록 drift 강도가 선형 또는 sigmoid 형태로 커진다.

```text
drift_strength(t) = clip((t - drift_start) / transition_length, 0, 1)
current = (1 - strength) * baseline + strength * drifted
```

사용 대상: EWMA, Page-Hinkley, EDDM, PSI trend, representation drift trend.

### seasonal

캘린더 또는 반복 period에 따라 특정 계절 구간에서만 분포가 달라진다.

```text
season_factor = season_profile[month_or_week]
value = baseline + season_factor * seasonal_shift
```

사용 대상: 운영 데이터에서 정상 계절성을 drift로 오인하지 않는지 확인하는 케이스.

### cyclic

두 개 이상의 regime이 순환한다. 계절성과 달리 calendar 의미보다 반복 상태 전환을 검증한다.

```text
regime(t) = floor(t / cycle_length) mod regime_count
```

사용 대상: BOCD, KSWIN, control chart, graph/embedding drift처럼 반복 변화점 또는 regime reset을 보여야 하는 케이스.

## 3. 대표 케이스별 생성 방향

### CASE-001 numeric_location_shift

목표는 평균 또는 위치 이동이다. reference는 `N(0, 1)`, current는 drift 강도에 따라 `N(mu_t, 1)`로 만든다.

- abrupt: `mu_t = 0`에서 `0.7`로 점프
- gradual: `mu_t`를 `0 -> 0.7`로 8~12개 window 동안 증가
- seasonal: 특정 month/week에 `mu_t += 0.4`
- cyclic: `mu_t`가 `0`, `0.7`, `-0.3` regime을 반복

### CASE-002 numeric_tail_and_shape_change

중심은 유지하고 tail 또는 mode만 바꾼다. reference는 단봉 정규분포, current는 heavy-tail 또는 mixture 분포다.

- abrupt: drift 이후 `0.85*N(0,1) + 0.15*T(df=3)` 사용
- gradual: tail mixture weight를 증가
- seasonal: 특정 season에만 tail mixture weight 증가
- cyclic: dominant mode 위치를 반복 전환

### CASE-003 numeric_variance_spread

평균은 유지하고 분산만 바꾼다.

- abrupt: `std=1.0 -> 1.8`
- gradual: `std`를 window마다 증가
- seasonal: 특정 기간에만 고분산
- cyclic: normal volatility와 high volatility 반복

### CASE-004 binned_numeric_population_shift

raw numeric 값과 bin count를 함께 만든다. PSI, histogram, probability distance 계열에서 재사용한다.

- abrupt: low band mass를 high band로 이동
- gradual: band probability vector를 선형 보간
- seasonal: 특정 기간 high score band 비율 증가
- cyclic: low-risk, medium-risk, high-risk profile 반복

### CASE-005 categorical_proportion_shift

범주 라벨과 집계 count를 함께 만든다.

- abrupt: 60분 bucket 내부를 reference 30분/current 30분으로 나누고, drift 이후 current 쪽 `A/B/C/D` 비율을 `0.50/0.30/0.20/0.00`에서 `0.10/0.10/0.70/0.10`으로 변경
- gradual: category probability vector를 보간
- seasonal: 이 대표 smoke 데이터에서는 drift 직전 기준선이 흔들리지 않도록 제외
- cyclic: dominant category가 순환

### CASE-006 binary_event_rate_shift

2x2 table, event stream, supervised error stream에 모두 쓸 수 있게 row-level binary event를 만든다.

- abrupt: event probability `0.08 -> 0.42`
- gradual: event probability를 천천히 증가
- seasonal: 이 대표 smoke 데이터에서는 drift 직전 기준선이 올라가지 않도록 제외
- cyclic: event probability가 low/high regime 반복

### CASE-007 probability_vector_shift

명시적 probability vector를 만든다. 필요하면 vector에서 categorical row를 sampling한다.

- abrupt: 60분 bucket 내부를 reference 30분/current 30분으로 나누고, drift 이후 current 쪽 `p0/p1/p2/p3/p4` class band 비율을 `0.40/0.25/0.20/0.10/0.05`에서 `0.10/0.10/0.20/0.35/0.25`로 변경
- gradual: 두 vector 사이를 보간
- seasonal: 이 대표 smoke 데이터에서는 drift 직전 기준선이 흔들리지 않도록 제외
- cyclic: class mass가 순환 이동

### CASE-008 multivariate_embedding_shift

2D/16D/64D embedding을 함께 만들고, chart용 2D projection을 저장한다.

- abrupt: centroid를 특정 방향으로 이동
- gradual: centroid가 window마다 이동
- seasonal: seasonal offset vector 추가
- cyclic: latent space에서 원형 경로를 이동

### CASE-009 multivariate_local_density_or_anomaly

대부분은 기준 cluster를 유지하고 일부 novel cluster 또는 outlier만 추가한다.

- abrupt: drift 이후 novel cluster 추가
- gradual: novel cluster weight 증가
- seasonal: 특정 기간 anomaly pocket 생성
- cyclic: known cluster와 novel cluster가 교대로 우세

### CASE-010 stream_numeric_mean_shift

timestamped numeric stream을 생성한다. online detector와 control chart의 기본 케이스다.

- abrupt: stream level step change
- gradual: ramp change
- seasonal: weekly/monthly stream level
- cyclic: sinusoidal 또는 regime-cycle stream

### CASE-011 stream_error_rate_and_performance

`y_true`, `y_pred`, `probability`, `error`, `confidence`, `timestamp`를 포함한 prediction log를 만든다.

- abrupt: error rate 급증
- gradual: accuracy decay
- seasonal: 특정 period 성능 저하
- cyclic: easy/hard period 반복

### CASE-012 supervised_concept_boundary_shift

feature와 label rule 자체가 바뀌는 concept drift다.

- abrupt: label boundary 즉시 변경
- gradual: old rule과 new rule을 확률적으로 blending
- seasonal: season별 label rule
- cyclic: 두 label rule 반복

### CASE-013 text_topic_semantic_shift

text row, topic label, embedding을 함께 만든다.

- abrupt: dominant topic 교체
- gradual: topic proportion 변경
- seasonal: season topic 증가
- cyclic: topic family 순환

### CASE-014 explanation_importance_shift

feature attribution vector를 만든다.

- abrupt: top feature group 교체
- gradual: 새 feature importance 증가
- seasonal: 특정 feature group seasonal dominance
- cyclic: dominant explanation group 반복

### CASE-015 annotation_label_quality_shift

annotator, label, confidence, disagreement, quality score를 만든다.

- abrupt: label policy 또는 annotator pool 변경
- gradual: label noise 증가
- seasonal: annotator mix 변경
- cyclic: labeling policy 반복

### CASE-016 graph_or_feature_map_representation_shift

graph/node 또는 feature-map layer metadata가 붙은 embedding을 만든다.

- abrupt: 특정 node group/layer shift
- gradual: subgroup shift strength 증가
- seasonal: subgraph activation 증가
- cyclic: active subgraph 또는 feature-map region 반복

## 4. 다음 작업

1. `chart_method_dataset_mapping.csv`에 각 188개 row의 `dataset_case_id`를 배정한다.
2. 케이스별 generator spec을 JSON/YAML로 분리한다.
3. 대표 케이스별 seed 데이터와 expected measurement 방향을 만든다.
4. 복사 대상 row는 `copy_from_dataset_id`만 지정하고 같은 raw data를 재사용한다.
