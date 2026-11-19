# Drift Method Parameter Guide

## 1. 목적

이 문서는 `drift_method_variant_parameters.csv`를 바탕으로, drift 측정 방법별 파라미터와 하이퍼파라미터의 의미, 값 범위, 조절 효과를 정리한다.

LLM이 특정 method를 추천할 때 해당 method 섹션만 읽어도 판단할 수 있도록, `reference_window`, `current_window`, `input_signal`, `threshold_or_alpha` 같은 공통 파라미터도 method별로 반복 기술한다.

각 method 섹션의 파라미터 목록은 해당 method의 모든 algorithm variant에서 사용되는 파라미터의 합집합이다.

## 2. 해석 규칙

- 파라미터 값의 권장 범위는 일반적인 drift monitoring 관점의 범위다. 실제 라이브러리 구현은 더 좁거나 다른 범위를 요구할 수 있다.
- threshold, alpha, delta, confidence류 파라미터는 false alarm과 detection delay의 trade-off를 만든다.
- window, sample size, warmup류 파라미터는 안정성과 반응 속도의 trade-off를 만든다.
- model, embedding, preprocessing, policy류 파라미터가 바뀌면 이전 결과와 직접 비교하지 않는 것이 원칙이다.

## 1. ADWIN

적용 variant: ADWIN_MEAN_STREAM; ADWIN_ERROR_RATE; ADWIN_DISTANCE_STREAM

사용 파라미터 수: 13

- `base_distance_method`
  - 의미: 거리 계산 방식.
  - 값 범위: Wasserstein, cosine, euclidean, JS, MMD 등.
  - 조절 효과: 어떤 차이에 민감한지가 달라지므로 데이터 형태에 맞춰 선택한다.
- `clock`
  - 의미: streaming detector의 메모리, 업데이트 주기, reset/retention 정책.
  - 값 범위: count는 양의 정수, policy는 문자열.
  - 조절 효과: 메모리를 늘리면 안정적이나 느리고, reset을 자주 하면 빠르지만 기준이 자주 바뀐다.
- `current_window`
  - 의미: 비교 기준/현재 데이터 구간.
  - 값 범위: timestamp range, window id, 또는 sample set.
  - 조절 효과: reference를 길게 잡으면 안정적이지만 최신 정상 상태를 덜 반영하고, current를 짧게 잡으면 빠르지만 noise가 커진다.
- `delta`
  - 의미: drift/warning 판정 민감도.
  - 값 범위: 보통 0과 1 사이 또는 detector 고유 threshold.
  - 조절 효과: drift 기준을 엄격하게 하면 오경보는 줄지만 놓칠 수 있고, 완화하면 더 자주 alarm이 난다.
- `distance_window_size`
  - 의미: 계산에 사용하는 표본 또는 stream 길이.
  - 값 범위: 1 이상의 정수.
  - 조절 효과: 작으면 빠르고 민감하지만 noise가 크고, 크면 안정적이지만 detection delay가 늘어난다.
- `error_definition`
  - 의미: supervised error/performance stream 정의.
  - 값 범위: label 지연 처리 정책, 오류 정의, accuracy 계산 방식.
  - 조절 효과: label 처리 방식이 바뀌면 concept/performance drift 해석이 달라진다.
- `grace_period`
  - 의미: 계산에 사용하는 표본 또는 stream 길이.
  - 값 범위: 1 이상의 정수.
  - 조절 효과: 작으면 빠르고 민감하지만 noise가 크고, 크면 안정적이지만 detection delay가 늘어난다.
- `input_signal`
  - 의미: detector에 넣는 값.
  - 값 범위: feature, score, error_rate, loss, embedding, SHAP 등.
  - 조절 효과: 같은 method라도 입력 신호가 달라지면 drift 해석이 달라진다.
- `label_delay_policy`
  - 의미: supervised error/performance stream 정의.
  - 값 범위: label 지연 처리 정책, 오류 정의, accuracy 계산 방식.
  - 조절 효과: label 처리 방식이 바뀌면 concept/performance drift 해석이 달라진다.
- `max_buckets`
  - 의미: streaming detector의 메모리, 업데이트 주기, reset/retention 정책.
  - 값 범위: count는 양의 정수, policy는 문자열.
  - 조절 효과: 메모리를 늘리면 안정적이나 느리고, reset을 자주 하면 빠르지만 기준이 자주 바뀐다.
- `min_window_length`
  - 의미: 계산에 사용하는 표본 또는 stream 길이.
  - 값 범위: 1 이상의 정수.
  - 조절 효과: 작으면 빠르고 민감하지만 noise가 크고, 크면 안정적이지만 detection delay가 늘어난다.
- `reference_window`
  - 의미: 비교 기준/현재 데이터 구간.
  - 값 범위: timestamp range, window id, 또는 sample set.
  - 조절 효과: reference를 길게 잡으면 안정적이지만 최신 정상 상태를 덜 반영하고, current를 짧게 잡으면 빠르지만 noise가 커진다.
- `threshold_or_alpha`
  - 의미: 유의수준 또는 alarm 임계값.
  - 값 범위: 보통 0과 1 사이.
  - 조절 효과: 낮추면 보수적이고 false alarm이 줄지만 감지가 늦거나 약해지며, 높이면 민감해진다.

## 2. Anderson-Darling Test

적용 variant: ONE_SAMPLE_ANDERSON_DARLING; TWO_SAMPLE_ANDERSON_DARLING; K_SAMPLE_ANDERSON_DARLING; TAIL_SENSITIVE_AD

사용 파라미터 수: 8

- `current_window`
  - 의미: 비교 기준/현재 데이터 구간.
  - 값 범위: timestamp range, window id, 또는 sample set.
  - 조절 효과: reference를 길게 잡으면 안정적이지만 최신 정상 상태를 덜 반영하고, current를 짧게 잡으면 빠르지만 noise가 커진다.
- `distribution_family`
  - 의미: 통계 모델, 분포 가정, 가설 정의.
  - 값 범위: method별 분포명, 파라미터, H0/H1 정의.
  - 조절 효과: 가정이 바뀌면 p-value와 alarm 의미가 바뀐다.
- `input_signal`
  - 의미: detector에 넣는 값.
  - 값 범위: feature, score, error_rate, loss, embedding, SHAP 등.
  - 조절 효과: 같은 method라도 입력 신호가 달라지면 drift 해석이 달라진다.
- `p_value_method`
  - 의미: p-value 또는 검정 확률 계산 방식.
  - 값 범위: exact, asymptotic, permutation, bootstrap 등.
  - 조절 효과: exact는 작은 표본에서 정확하지만 느리고, asymptotic은 빠르지만 작은 표본에서 부정확할 수 있다.
- `reference_window`
  - 의미: 비교 기준/현재 데이터 구간.
  - 값 범위: timestamp range, window id, 또는 sample set.
  - 조절 효과: reference를 길게 잡으면 안정적이지만 최신 정상 상태를 덜 반영하고, current를 짧게 잡으면 빠르지만 noise가 커진다.
- `sample_groups`
  - 의미: 검정 또는 거리 계산에 들어가는 실제 표본/빈도/table.
  - 값 범위: 배열, count vector, contingency table.
  - 조절 효과: 표본 정의가 달라지면 결과가 달라지므로 filtering과 결측 처리 기준을 고정해야 한다.
- `significance_level`
  - 의미: 유의수준 또는 alarm 임계값.
  - 값 범위: 보통 0과 1 사이.
  - 조절 효과: 낮추면 보수적이고 false alarm이 줄지만 감지가 늦거나 약해지며, 높이면 민감해진다.
- `threshold_or_alpha`
  - 의미: 유의수준 또는 alarm 임계값.
  - 값 범위: 보통 0과 1 사이.
  - 조절 효과: 낮추면 보수적이고 false alarm이 줄지만 감지가 늦거나 약해지며, 높이면 민감해진다.

## 3. Autoencoder Representation Drift

적용 variant: LATENT_SPACE_DRIFT; RECONSTRUCTION_ERROR_DRIFT; AUTOENCODER_DOMAIN_CLASSIFIER

사용 파라미터 수: 10

- `current_window`
  - 의미: 비교 기준/현재 데이터 구간.
  - 값 범위: timestamp range, window id, 또는 sample set.
  - 조절 효과: reference를 길게 잡으면 안정적이지만 최신 정상 상태를 덜 반영하고, current를 짧게 잡으면 빠르지만 noise가 커진다.
- `encoder_version`
  - 의미: autoencoder/representation 모델 설정.
  - 값 범위: latent dimension과 epoch는 양의 정수, loss/optimizer는 이름.
  - 조절 효과: latent가 작으면 압축이 강하고, 크면 재구성은 쉬우나 drift 민감도가 약해질 수 있다.
- `input_signal`
  - 의미: detector에 넣는 값.
  - 값 범위: feature, score, error_rate, loss, embedding, SHAP 등.
  - 조절 효과: 같은 method라도 입력 신호가 달라지면 drift 해석이 달라진다.
- `latent_dim`
  - 의미: autoencoder/representation 모델 설정.
  - 값 범위: latent dimension과 epoch는 양의 정수, loss/optimizer는 이름.
  - 조절 효과: latent가 작으면 압축이 강하고, 크면 재구성은 쉬우나 drift 민감도가 약해질 수 있다.
- `reconstruction_loss`
  - 의미: autoencoder/representation 모델 설정.
  - 값 범위: latent dimension과 epoch는 양의 정수, loss/optimizer는 이름.
  - 조절 효과: latent가 작으면 압축이 강하고, 크면 재구성은 쉬우나 drift 민감도가 약해질 수 있다.
- `reference_window`
  - 의미: 비교 기준/현재 데이터 구간.
  - 값 범위: timestamp range, window id, 또는 sample set.
  - 조절 효과: reference를 길게 잡으면 안정적이지만 최신 정상 상태를 덜 반영하고, current를 짧게 잡으면 빠르지만 noise가 커진다.
- `scaling_policy`
  - 의미: feature, histogram, metric scale 정규화 방식.
  - 값 범위: none, standard, minmax, l2, probability 등.
  - 조절 효과: 정규화하면 feature 간 비교가 쉬워지지만 원 단위 해석은 약해진다.
- `threshold`
  - 의미: statistic, distance, score를 alarm으로 바꾸는 기준.
  - 값 범위: 측정값 scale에 따른 실수.
  - 조절 효과: 낮추면 민감도와 false alarm이 늘고, 높이면 안정적이지만 감지가 늦어진다.
- `threshold_or_alpha`
  - 의미: 유의수준 또는 alarm 임계값.
  - 값 범위: 보통 0과 1 사이.
  - 조절 효과: 낮추면 보수적이고 false alarm이 줄지만 감지가 늦거나 약해지며, 높이면 민감해진다.
- `training_epochs`
  - 의미: autoencoder/representation 모델 설정.
  - 값 범위: latent dimension과 epoch는 양의 정수, loss/optimizer는 이름.
  - 조절 효과: latent가 작으면 압축이 강하고, 크면 재구성은 쉬우나 drift 민감도가 약해질 수 있다.

## 4. Baumgartner-Weiss-Schindler Test

적용 variant: BWS_TWO_SAMPLE; BWS_EXACT_OR_ASYMPTOTIC; BWS_RANK_BASED

사용 파라미터 수: 9

- `alternative`
  - 의미: 양측/단측 또는 증가/감소 감시 방향.
  - 값 범위: two-sided, greater, less, up, down, both.
  - 조절 효과: 사전 방향성이 있으면 민감도를 높일 수 있지만, 사후 선택하면 해석이 왜곡된다.
- `asymptotic_method`
  - 의미: p-value 또는 검정 확률 계산 방식.
  - 값 범위: exact, asymptotic, permutation, bootstrap 등.
  - 조절 효과: exact는 작은 표본에서 정확하지만 느리고, asymptotic은 빠르지만 작은 표본에서 부정확할 수 있다.
- `current_window`
  - 의미: 비교 기준/현재 데이터 구간.
  - 값 범위: timestamp range, window id, 또는 sample set.
  - 조절 효과: reference를 길게 잡으면 안정적이지만 최신 정상 상태를 덜 반영하고, current를 짧게 잡으면 빠르지만 noise가 커진다.
- `exact_method`
  - 의미: p-value 또는 검정 확률 계산 방식.
  - 값 범위: exact, asymptotic, permutation, bootstrap 등.
  - 조절 효과: exact는 작은 표본에서 정확하지만 느리고, asymptotic은 빠르지만 작은 표본에서 부정확할 수 있다.
- `input_signal`
  - 의미: detector에 넣는 값.
  - 값 범위: feature, score, error_rate, loss, embedding, SHAP 등.
  - 조절 효과: 같은 method라도 입력 신호가 달라지면 drift 해석이 달라진다.
- `p_value_method`
  - 의미: p-value 또는 검정 확률 계산 방식.
  - 값 범위: exact, asymptotic, permutation, bootstrap 등.
  - 조절 효과: exact는 작은 표본에서 정확하지만 느리고, asymptotic은 빠르지만 작은 표본에서 부정확할 수 있다.
- `rank_tie_policy`
  - 의미: ties, continuity, missing value, small sample 보정 정책.
  - 값 범위: method별 policy 문자열 또는 boolean.
  - 조절 효과: 보정 정책은 p-value 안정성과 보수성에 영향을 준다.
- `reference_window`
  - 의미: 비교 기준/현재 데이터 구간.
  - 값 범위: timestamp range, window id, 또는 sample set.
  - 조절 효과: reference를 길게 잡으면 안정적이지만 최신 정상 상태를 덜 반영하고, current를 짧게 잡으면 빠르지만 noise가 커진다.
- `threshold_or_alpha`
  - 의미: 유의수준 또는 alarm 임계값.
  - 값 범위: 보통 0과 1 사이.
  - 조절 효과: 낮추면 보수적이고 false alarm이 줄지만 감지가 늦거나 약해지며, 높이면 민감해진다.

## 5. Bhattacharyya Distance

적용 variant: DISCRETE_BHATTACHARYYA_DISTANCE; GAUSSIAN_BHATTACHARYYA_DISTANCE; HISTOGRAM_BHATTACHARYYA_DISTANCE

사용 파라미터 수: 8

- `binning_policy`
  - 의미: 연속값을 구간화하거나 category bin을 정하는 방식.
  - 값 범위: 정책 문자열, bin 개수는 양의 정수.
  - 조절 효과: bin이 많으면 세밀하지만 표본 부족에 취약하고, 적으면 안정적이지만 세부 변화를 놓친다.
- `covariance_estimator`
  - 의미: 평균/공분산 기반 다변량 기준.
  - 값 범위: 벡터, 행렬, estimator 이름, 0 이상의 regularization 값.
  - 조절 효과: regularization과 robust estimator는 안정성을 높이지만 statistic scale을 바꾼다.
- `current_window`
  - 의미: 비교 기준/현재 데이터 구간.
  - 값 범위: timestamp range, window id, 또는 sample set.
  - 조절 효과: reference를 길게 잡으면 안정적이지만 최신 정상 상태를 덜 반영하고, current를 짧게 잡으면 빠르지만 noise가 커진다.
- `distribution_assumption`
  - 의미: 해당 method variant의 세부 설정값.
  - 값 범위: 구현 문서에서 정의한 enum, 정수, 실수 또는 구조화 값.
  - 조절 효과: 값 변경 시 detector 민감도, 계산 비용, 비교 가능성이 달라질 수 있으므로 변경 이력을 기록한다.
- `input_signal`
  - 의미: detector에 넣는 값.
  - 값 범위: feature, score, error_rate, loss, embedding, SHAP 등.
  - 조절 효과: 같은 method라도 입력 신호가 달라지면 drift 해석이 달라진다.
- `reference_window`
  - 의미: 비교 기준/현재 데이터 구간.
  - 값 범위: timestamp range, window id, 또는 sample set.
  - 조절 효과: reference를 길게 잡으면 안정적이지만 최신 정상 상태를 덜 반영하고, current를 짧게 잡으면 빠르지만 noise가 커진다.
- `smoothing_epsilon`
  - 의미: zero probability 또는 희소 category 보정.
  - 값 범위: 0 이상의 작은 실수 또는 정책.
  - 조절 효과: 값을 키우면 안정적이지만 작은 category 변화가 희석된다.
- `threshold_or_alpha`
  - 의미: 유의수준 또는 alarm 임계값.
  - 값 범위: 보통 0과 1 사이.
  - 조절 효과: 낮추면 보수적이고 false alarm이 줄지만 감지가 늦거나 약해지며, 높이면 민감해진다.

## 6. BOCD

적용 variant: BAYESIAN_ONLINE_CHANGE_POINT_GAUSSIAN; BOCD_HAZARD_RATE_VARIANT; BOCD_PREDICTIVE_PROBABILITY

사용 파라미터 수: 9

- `change_probability_threshold`
  - 의미: statistic, distance, score를 alarm으로 바꾸는 기준.
  - 값 범위: 측정값 scale에 따른 실수.
  - 조절 효과: 낮추면 민감도와 false alarm이 늘고, 높이면 안정적이지만 감지가 늦어진다.
- `current_window`
  - 의미: 비교 기준/현재 데이터 구간.
  - 값 범위: timestamp range, window id, 또는 sample set.
  - 조절 효과: reference를 길게 잡으면 안정적이지만 최신 정상 상태를 덜 반영하고, current를 짧게 잡으면 빠르지만 noise가 커진다.
- `hazard_function`
  - 의미: 통계 모델, 분포 가정, 가설 정의.
  - 값 범위: method별 분포명, 파라미터, H0/H1 정의.
  - 조절 효과: 가정이 바뀌면 p-value와 alarm 의미가 바뀐다.
- `input_signal`
  - 의미: detector에 넣는 값.
  - 값 범위: feature, score, error_rate, loss, embedding, SHAP 등.
  - 조절 효과: 같은 method라도 입력 신호가 달라지면 drift 해석이 달라진다.
- `likelihood_model`
  - 의미: 통계 모델, 분포 가정, 가설 정의.
  - 값 범위: method별 분포명, 파라미터, H0/H1 정의.
  - 조절 효과: 가정이 바뀌면 p-value와 alarm 의미가 바뀐다.
- `prior_distribution`
  - 의미: 통계 모델, 분포 가정, 가설 정의.
  - 값 범위: method별 분포명, 파라미터, H0/H1 정의.
  - 조절 효과: 가정이 바뀌면 p-value와 alarm 의미가 바뀐다.
- `reference_window`
  - 의미: 비교 기준/현재 데이터 구간.
  - 값 범위: timestamp range, window id, 또는 sample set.
  - 조절 효과: reference를 길게 잡으면 안정적이지만 최신 정상 상태를 덜 반영하고, current를 짧게 잡으면 빠르지만 noise가 커진다.
- `run_length_truncation`
  - 의미: 해당 method variant의 세부 설정값.
  - 값 범위: 구현 문서에서 정의한 enum, 정수, 실수 또는 구조화 값.
  - 조절 효과: 값 변경 시 detector 민감도, 계산 비용, 비교 가능성이 달라질 수 있으므로 변경 이력을 기록한다.
- `threshold_or_alpha`
  - 의미: 유의수준 또는 alarm 임계값.
  - 값 범위: 보통 0과 1 사이.
  - 조절 효과: 낮추면 보수적이고 false alarm이 줄지만 감지가 늦거나 약해지며, 높이면 민감해진다.

## 7. Chi-square Test

적용 variant: CHI_SQUARE_GOODNESS_OF_FIT; CHI_SQUARE_HOMOGENEITY; CHI_SQUARE_WITH_LOW_EXPECTED_COUNT_CAUTION

사용 파라미터 수: 11

- `category_smoothing`
  - 의미: zero probability 또는 희소 category 보정.
  - 값 범위: 0 이상의 작은 실수 또는 정책.
  - 조절 효과: 값을 키우면 안정적이지만 작은 category 변화가 희석된다.
- `contingency_table`
  - 의미: 검정 또는 거리 계산에 들어가는 실제 표본/빈도/table.
  - 값 범위: 배열, count vector, contingency table.
  - 조절 효과: 표본 정의가 달라지면 결과가 달라지므로 filtering과 결측 처리 기준을 고정해야 한다.
- `correction`
  - 의미: ties, continuity, missing value, small sample 보정 정책.
  - 값 범위: method별 policy 문자열 또는 boolean.
  - 조절 효과: 보정 정책은 p-value 안정성과 보수성에 영향을 준다.
- `current_window`
  - 의미: 비교 기준/현재 데이터 구간.
  - 값 범위: timestamp range, window id, 또는 sample set.
  - 조절 효과: reference를 길게 잡으면 안정적이지만 최신 정상 상태를 덜 반영하고, current를 짧게 잡으면 빠르지만 noise가 커진다.
- `degrees_of_freedom`
  - 의미: 통계 모델, 분포 가정, 가설 정의.
  - 값 범위: method별 분포명, 파라미터, H0/H1 정의.
  - 조절 효과: 가정이 바뀌면 p-value와 alarm 의미가 바뀐다.
- `expected_counts`
  - 의미: 검정 또는 거리 계산에 들어가는 실제 표본/빈도/table.
  - 값 범위: 배열, count vector, contingency table.
  - 조절 효과: 표본 정의가 달라지면 결과가 달라지므로 filtering과 결측 처리 기준을 고정해야 한다.
- `input_signal`
  - 의미: detector에 넣는 값.
  - 값 범위: feature, score, error_rate, loss, embedding, SHAP 등.
  - 조절 효과: 같은 method라도 입력 신호가 달라지면 drift 해석이 달라진다.
- `min_expected_count`
  - 의미: 해당 method variant의 세부 설정값.
  - 값 범위: 구현 문서에서 정의한 enum, 정수, 실수 또는 구조화 값.
  - 조절 효과: 값 변경 시 detector 민감도, 계산 비용, 비교 가능성이 달라질 수 있으므로 변경 이력을 기록한다.
- `observed_counts`
  - 의미: 검정 또는 거리 계산에 들어가는 실제 표본/빈도/table.
  - 값 범위: 배열, count vector, contingency table.
  - 조절 효과: 표본 정의가 달라지면 결과가 달라지므로 filtering과 결측 처리 기준을 고정해야 한다.
- `reference_window`
  - 의미: 비교 기준/현재 데이터 구간.
  - 값 범위: timestamp range, window id, 또는 sample set.
  - 조절 효과: reference를 길게 잡으면 안정적이지만 최신 정상 상태를 덜 반영하고, current를 짧게 잡으면 빠르지만 noise가 커진다.
- `threshold_or_alpha`
  - 의미: 유의수준 또는 alarm 임계값.
  - 값 범위: 보통 0과 1 사이.
  - 조절 효과: 낮추면 보수적이고 false alarm이 줄지만 감지가 늦거나 약해지며, 높이면 민감해진다.

## 8. Classifier 기반 embedding drift detection

적용 variant: DOMAIN_CLASSIFIER_ROC_AUC; DOMAIN_CLASSIFIER_PROBABILITY_DRIFT; CROSS_VALIDATED_DOMAIN_CLASSIFIER

사용 파라미터 수: 4

- `current_window`
  - 의미: 비교 기준/현재 데이터 구간.
  - 값 범위: timestamp range, window id, 또는 sample set.
  - 조절 효과: reference를 길게 잡으면 안정적이지만 최신 정상 상태를 덜 반영하고, current를 짧게 잡으면 빠르지만 noise가 커진다.
- `input_signal`
  - 의미: detector에 넣는 값.
  - 값 범위: feature, score, error_rate, loss, embedding, SHAP 등.
  - 조절 효과: 같은 method라도 입력 신호가 달라지면 drift 해석이 달라진다.
- `reference_window`
  - 의미: 비교 기준/현재 데이터 구간.
  - 값 범위: timestamp range, window id, 또는 sample set.
  - 조절 효과: reference를 길게 잡으면 안정적이지만 최신 정상 상태를 덜 반영하고, current를 짧게 잡으면 빠르지만 noise가 커진다.
- `threshold_or_alpha`
  - 의미: 유의수준 또는 alarm 임계값.
  - 값 범위: 보통 0과 1 사이.
  - 조절 효과: 낮추면 보수적이고 false alarm이 줄지만 감지가 늦거나 약해지며, 높이면 민감해진다.

## 9. Cramer-von Mises Test

적용 variant: ONE_SAMPLE_CVM; TWO_SAMPLE_CVM; K_SAMPLE_CVM

사용 파라미터 수: 7

- `alternative`
  - 의미: 양측/단측 또는 증가/감소 감시 방향.
  - 값 범위: two-sided, greater, less, up, down, both.
  - 조절 효과: 사전 방향성이 있으면 민감도를 높일 수 있지만, 사후 선택하면 해석이 왜곡된다.
- `current_window`
  - 의미: 비교 기준/현재 데이터 구간.
  - 값 범위: timestamp range, window id, 또는 sample set.
  - 조절 효과: reference를 길게 잡으면 안정적이지만 최신 정상 상태를 덜 반영하고, current를 짧게 잡으면 빠르지만 noise가 커진다.
- `input_signal`
  - 의미: detector에 넣는 값.
  - 값 범위: feature, score, error_rate, loss, embedding, SHAP 등.
  - 조절 효과: 같은 method라도 입력 신호가 달라지면 drift 해석이 달라진다.
- `p_value_method`
  - 의미: p-value 또는 검정 확률 계산 방식.
  - 값 범위: exact, asymptotic, permutation, bootstrap 등.
  - 조절 효과: exact는 작은 표본에서 정확하지만 느리고, asymptotic은 빠르지만 작은 표본에서 부정확할 수 있다.
- `reference_window`
  - 의미: 비교 기준/현재 데이터 구간.
  - 값 범위: timestamp range, window id, 또는 sample set.
  - 조절 효과: reference를 길게 잡으면 안정적이지만 최신 정상 상태를 덜 반영하고, current를 짧게 잡으면 빠르지만 noise가 커진다.
- `sample_groups`
  - 의미: 검정 또는 거리 계산에 들어가는 실제 표본/빈도/table.
  - 값 범위: 배열, count vector, contingency table.
  - 조절 효과: 표본 정의가 달라지면 결과가 달라지므로 filtering과 결측 처리 기준을 고정해야 한다.
- `threshold_or_alpha`
  - 의미: 유의수준 또는 alarm 임계값.
  - 값 범위: 보통 0과 1 사이.
  - 조절 효과: 낮추면 보수적이고 false alarm이 줄지만 감지가 늦거나 약해지며, 높이면 민감해진다.

## 10. CUSUM

적용 variant: ONE_SIDED_UPPER_CUSUM; ONE_SIDED_LOWER_CUSUM; TWO_SIDED_CUSUM; CUSUM_ON_DISTANCE_STREAM

사용 파라미터 수: 13

- `allowance_k`
  - 의미: control chart 또는 variance test의 기준 중심/분산/허용 편차.
  - 값 범위: metric scale의 실수, proportion은 0과 0.5 사이.
  - 조절 효과: 기준 중심이 잘못되면 정상 변화도 drift로 보일 수 있다.
- `base_distance_method`
  - 의미: 거리 계산 방식.
  - 값 범위: Wasserstein, cosine, euclidean, JS, MMD 등.
  - 조절 효과: 어떤 차이에 민감한지가 달라지므로 데이터 형태에 맞춰 선택한다.
- `current_window`
  - 의미: 비교 기준/현재 데이터 구간.
  - 값 범위: timestamp range, window id, 또는 sample set.
  - 조절 효과: reference를 길게 잡으면 안정적이지만 최신 정상 상태를 덜 반영하고, current를 짧게 잡으면 빠르지만 noise가 커진다.
- `decision_threshold_h`
  - 의미: statistic, distance, score를 alarm으로 바꾸는 기준.
  - 값 범위: 측정값 scale에 따른 실수.
  - 조절 효과: 낮추면 민감도와 false alarm이 늘고, 높이면 안정적이지만 감지가 늦어진다.
- `direction`
  - 의미: 양측/단측 또는 증가/감소 감시 방향.
  - 값 범위: two-sided, greater, less, up, down, both.
  - 조절 효과: 사전 방향성이 있으면 민감도를 높일 수 있지만, 사후 선택하면 해석이 왜곡된다.
- `direction_or_alternative`
  - 의미: 양측/단측 또는 증가/감소 감시 방향.
  - 값 범위: two-sided, greater, less, up, down, both.
  - 조절 효과: 사전 방향성이 있으면 민감도를 높일 수 있지만, 사후 선택하면 해석이 왜곡된다.
- `distance_window_size`
  - 의미: 계산에 사용하는 표본 또는 stream 길이.
  - 값 범위: 1 이상의 정수.
  - 조절 효과: 작으면 빠르고 민감하지만 noise가 크고, 크면 안정적이지만 detection delay가 늘어난다.
- `input_signal`
  - 의미: detector에 넣는 값.
  - 값 범위: feature, score, error_rate, loss, embedding, SHAP 등.
  - 조절 효과: 같은 method라도 입력 신호가 달라지면 drift 해석이 달라진다.
- `reference_window`
  - 의미: 비교 기준/현재 데이터 구간.
  - 값 범위: timestamp range, window id, 또는 sample set.
  - 조절 효과: reference를 길게 잡으면 안정적이지만 최신 정상 상태를 덜 반영하고, current를 짧게 잡으면 빠르지만 noise가 커진다.
- `reset_policy`
  - 의미: streaming detector의 메모리, 업데이트 주기, reset/retention 정책.
  - 값 범위: count는 양의 정수, policy는 문자열.
  - 조절 효과: 메모리를 늘리면 안정적이나 느리고, reset을 자주 하면 빠르지만 기준이 자주 바뀐다.
- `target_mean`
  - 의미: control chart 또는 variance test의 기준 중심/분산/허용 편차.
  - 값 범위: metric scale의 실수, proportion은 0과 0.5 사이.
  - 조절 효과: 기준 중심이 잘못되면 정상 변화도 drift로 보일 수 있다.
- `threshold_or_alpha`
  - 의미: 유의수준 또는 alarm 임계값.
  - 값 범위: 보통 0과 1 사이.
  - 조절 효과: 낮추면 보수적이고 false alarm이 줄지만 감지가 늦거나 약해지며, 높이면 민감해진다.
- `warmup_size`
  - 의미: 계산에 사용하는 표본 또는 stream 길이.
  - 값 범위: 1 이상의 정수.
  - 조절 효과: 작으면 빠르고 민감하지만 noise가 크고, 크면 안정적이지만 detection delay가 늘어난다.

## 11. DDM

적용 variant: DDM_STANDARD; DDM_WARNING_BUFFER; DDM_CLASS_SPECIFIC

사용 파라미터 수: 14

- `buffer_policy`
  - 의미: streaming detector의 메모리, 업데이트 주기, reset/retention 정책.
  - 값 범위: count는 양의 정수, policy는 문자열.
  - 조절 효과: 메모리를 늘리면 안정적이나 느리고, reset을 자주 하면 빠르지만 기준이 자주 바뀐다.
- `class_label`
  - 의미: 설명 기반 drift 계산 설정.
  - 값 범위: explainer 이름, background data, class label, top-k 정수.
  - 조절 효과: background와 explainer가 바뀌면 SHAP/importance 분포가 달라진다.
- `class_min_support`
  - 의미: 해당 method variant의 세부 설정값.
  - 값 범위: 구현 문서에서 정의한 enum, 정수, 실수 또는 구조화 값.
  - 조절 효과: 값 변경 시 detector 민감도, 계산 비용, 비교 가능성이 달라질 수 있으므로 변경 이력을 기록한다.
- `current_window`
  - 의미: 비교 기준/현재 데이터 구간.
  - 값 범위: timestamp range, window id, 또는 sample set.
  - 조절 효과: reference를 길게 잡으면 안정적이지만 최신 정상 상태를 덜 반영하고, current를 짧게 잡으면 빠르지만 noise가 커진다.
- `drift_level`
  - 의미: drift/warning 판정 민감도.
  - 값 범위: 보통 0과 1 사이 또는 detector 고유 threshold.
  - 조절 효과: drift 기준을 엄격하게 하면 오경보는 줄지만 놓칠 수 있고, 완화하면 더 자주 alarm이 난다.
- `error_definition`
  - 의미: supervised error/performance stream 정의.
  - 값 범위: label 지연 처리 정책, 오류 정의, accuracy 계산 방식.
  - 조절 효과: label 처리 방식이 바뀌면 concept/performance drift 해석이 달라진다.
- `input_signal`
  - 의미: detector에 넣는 값.
  - 값 범위: feature, score, error_rate, loss, embedding, SHAP 등.
  - 조절 효과: 같은 method라도 입력 신호가 달라지면 drift 해석이 달라진다.
- `label_delay_policy`
  - 의미: supervised error/performance stream 정의.
  - 값 범위: label 지연 처리 정책, 오류 정의, accuracy 계산 방식.
  - 조절 효과: label 처리 방식이 바뀌면 concept/performance drift 해석이 달라진다.
- `max_buffer_size`
  - 의미: streaming detector의 메모리, 업데이트 주기, reset/retention 정책.
  - 값 범위: count는 양의 정수, policy는 문자열.
  - 조절 효과: 메모리를 늘리면 안정적이나 느리고, reset을 자주 하면 빠르지만 기준이 자주 바뀐다.
- `min_num_instances`
  - 의미: 계산에 사용하는 표본 또는 stream 길이.
  - 값 범위: 1 이상의 정수.
  - 조절 효과: 작으면 빠르고 민감하지만 noise가 크고, 크면 안정적이지만 detection delay가 늘어난다.
- `multiple_testing_correction`
  - 의미: ties, continuity, missing value, small sample 보정 정책.
  - 값 범위: method별 policy 문자열 또는 boolean.
  - 조절 효과: 보정 정책은 p-value 안정성과 보수성에 영향을 준다.
- `reference_window`
  - 의미: 비교 기준/현재 데이터 구간.
  - 값 범위: timestamp range, window id, 또는 sample set.
  - 조절 효과: reference를 길게 잡으면 안정적이지만 최신 정상 상태를 덜 반영하고, current를 짧게 잡으면 빠르지만 noise가 커진다.
- `threshold_or_alpha`
  - 의미: 유의수준 또는 alarm 임계값.
  - 값 범위: 보통 0과 1 사이.
  - 조절 효과: 낮추면 보수적이고 false alarm이 줄지만 감지가 늦거나 약해지며, 높이면 민감해진다.
- `warning_level`
  - 의미: drift/warning 판정 민감도.
  - 값 범위: 보통 0과 1 사이 또는 detector 고유 threshold.
  - 조절 효과: drift 기준을 엄격하게 하면 오경보는 줄지만 놓칠 수 있고, 완화하면 더 자주 alarm이 난다.

## 12. DriftRetrainingClassifier

적용 variant: DRIFT_RETRAINING_WITH_ADWIN; DRIFT_RETRAINING_WITH_PAGE_HINKLEY; DRIFT_RETRAINING_CHAMPION_CHALLENGER

사용 파라미터 수: 11

- `base_classifier`
  - 의미: drift 감지와 재학습/운영 적응 정책.
  - 값 범위: detector/model 이름, metric 이름, 최소 표본 수.
  - 조절 효과: 자동 조치 민감도와 운영 리스크를 결정한다.
- `champion_challenger_policy`
  - 의미: drift 감지와 재학습/운영 적응 정책.
  - 값 범위: detector/model 이름, metric 이름, 최소 표본 수.
  - 조절 효과: 자동 조치 민감도와 운영 리스크를 결정한다.
- `current_window`
  - 의미: 비교 기준/현재 데이터 구간.
  - 값 범위: timestamp range, window id, 또는 sample set.
  - 조절 효과: reference를 길게 잡으면 안정적이지만 최신 정상 상태를 덜 반영하고, current를 짧게 잡으면 빠르지만 noise가 커진다.
- `drift_detector`
  - 의미: drift 감지와 재학습/운영 적응 정책.
  - 값 범위: detector/model 이름, metric 이름, 최소 표본 수.
  - 조절 효과: 자동 조치 민감도와 운영 리스크를 결정한다.
- `evaluation_metric`
  - 의미: drift 감지와 재학습/운영 적응 정책.
  - 값 범위: detector/model 이름, metric 이름, 최소 표본 수.
  - 조절 효과: 자동 조치 민감도와 운영 리스크를 결정한다.
- `input_signal`
  - 의미: detector에 넣는 값.
  - 값 범위: feature, score, error_rate, loss, embedding, SHAP 등.
  - 조절 효과: 같은 method라도 입력 신호가 달라지면 drift 해석이 달라진다.
- `min_retrain_samples`
  - 의미: drift 감지와 재학습/운영 적응 정책.
  - 값 범위: detector/model 이름, metric 이름, 최소 표본 수.
  - 조절 효과: 자동 조치 민감도와 운영 리스크를 결정한다.
- `reference_window`
  - 의미: 비교 기준/현재 데이터 구간.
  - 값 범위: timestamp range, window id, 또는 sample set.
  - 조절 효과: reference를 길게 잡으면 안정적이지만 최신 정상 상태를 덜 반영하고, current를 짧게 잡으면 빠르지만 noise가 커진다.
- `retrain_policy`
  - 의미: drift 감지와 재학습/운영 적응 정책.
  - 값 범위: detector/model 이름, metric 이름, 최소 표본 수.
  - 조절 효과: 자동 조치 민감도와 운영 리스크를 결정한다.
- `retrain_window_size`
  - 의미: 계산에 사용하는 표본 또는 stream 길이.
  - 값 범위: 1 이상의 정수.
  - 조절 효과: 작으면 빠르고 민감하지만 noise가 크고, 크면 안정적이지만 detection delay가 늘어난다.
- `threshold_or_alpha`
  - 의미: 유의수준 또는 alarm 임계값.
  - 값 범위: 보통 0과 1 사이.
  - 조절 효과: 낮추면 보수적이고 false alarm이 줄지만 감지가 늦거나 약해지며, 높이면 민감해진다.

## 13. ECDD-WT

적용 variant: ECDD_WT_STANDARD; ECDD_WT_WARNING_DRIFT; ECDD_WT_ERROR_STREAM

사용 파라미터 수: 9

- `current_window`
  - 의미: 비교 기준/현재 데이터 구간.
  - 값 범위: timestamp range, window id, 또는 sample set.
  - 조절 효과: reference를 길게 잡으면 안정적이지만 최신 정상 상태를 덜 반영하고, current를 짧게 잡으면 빠르지만 noise가 커진다.
- `drift_threshold`
  - 의미: drift/warning 판정 민감도.
  - 값 범위: 보통 0과 1 사이 또는 detector 고유 threshold.
  - 조절 효과: drift 기준을 엄격하게 하면 오경보는 줄지만 놓칠 수 있고, 완화하면 더 자주 alarm이 난다.
- `error_definition`
  - 의미: supervised error/performance stream 정의.
  - 값 범위: label 지연 처리 정책, 오류 정의, accuracy 계산 방식.
  - 조절 효과: label 처리 방식이 바뀌면 concept/performance drift 해석이 달라진다.
- `input_signal`
  - 의미: detector에 넣는 값.
  - 값 범위: feature, score, error_rate, loss, embedding, SHAP 등.
  - 조절 효과: 같은 method라도 입력 신호가 달라지면 drift 해석이 달라진다.
- `lambda`
  - 의미: EWMA/GMA/HDDM-W/ECDD 계열의 가중치 또는 smoothing factor.
  - 값 범위: 보통 0과 1 사이.
  - 조절 효과: 클수록 최근 값에 민감하고, 작을수록 완만하지만 감지가 늦다.
- `min_instances`
  - 의미: 계산에 사용하는 표본 또는 stream 길이.
  - 값 범위: 1 이상의 정수.
  - 조절 효과: 작으면 빠르고 민감하지만 noise가 크고, 크면 안정적이지만 detection delay가 늘어난다.
- `reference_window`
  - 의미: 비교 기준/현재 데이터 구간.
  - 값 범위: timestamp range, window id, 또는 sample set.
  - 조절 효과: reference를 길게 잡으면 안정적이지만 최신 정상 상태를 덜 반영하고, current를 짧게 잡으면 빠르지만 noise가 커진다.
- `threshold_or_alpha`
  - 의미: 유의수준 또는 alarm 임계값.
  - 값 범위: 보통 0과 1 사이.
  - 조절 효과: 낮추면 보수적이고 false alarm이 줄지만 감지가 늦거나 약해지며, 높이면 민감해진다.
- `warning_threshold`
  - 의미: drift/warning 판정 민감도.
  - 값 범위: 보통 0과 1 사이 또는 detector 고유 threshold.
  - 조절 효과: drift 기준을 엄격하게 하면 오경보는 줄지만 놓칠 수 있고, 완화하면 더 자주 alarm이 난다.

## 14. EDDM

적용 variant: EDDM_DISTANCE_BETWEEN_ERRORS; EDDM_WARNING_DRIFT; EDDM_GRADUAL_DRIFT

사용 파라미터 수: 8

- `current_window`
  - 의미: 비교 기준/현재 데이터 구간.
  - 값 범위: timestamp range, window id, 또는 sample set.
  - 조절 효과: reference를 길게 잡으면 안정적이지만 최신 정상 상태를 덜 반영하고, current를 짧게 잡으면 빠르지만 noise가 커진다.
- `drift_level`
  - 의미: drift/warning 판정 민감도.
  - 값 범위: 보통 0과 1 사이 또는 detector 고유 threshold.
  - 조절 효과: drift 기준을 엄격하게 하면 오경보는 줄지만 놓칠 수 있고, 완화하면 더 자주 alarm이 난다.
- `error_distance_metric`
  - 의미: 거리 계산 방식.
  - 값 범위: Wasserstein, cosine, euclidean, JS, MMD 등.
  - 조절 효과: 어떤 차이에 민감한지가 달라지므로 데이터 형태에 맞춰 선택한다.
- `input_signal`
  - 의미: detector에 넣는 값.
  - 값 범위: feature, score, error_rate, loss, embedding, SHAP 등.
  - 조절 효과: 같은 method라도 입력 신호가 달라지면 drift 해석이 달라진다.
- `min_num_errors`
  - 의미: one-class/outlier detector 설정.
  - 값 범위: contamination/nu는 보통 0과 1 사이, estimator와 sample 수는 양의 정수.
  - 조절 효과: contamination을 높이면 outlier 허용이 커지고, estimator 수가 많으면 안정적이지만 느리다.
- `reference_window`
  - 의미: 비교 기준/현재 데이터 구간.
  - 값 범위: timestamp range, window id, 또는 sample set.
  - 조절 효과: reference를 길게 잡으면 안정적이지만 최신 정상 상태를 덜 반영하고, current를 짧게 잡으면 빠르지만 noise가 커진다.
- `threshold_or_alpha`
  - 의미: 유의수준 또는 alarm 임계값.
  - 값 범위: 보통 0과 1 사이.
  - 조절 효과: 낮추면 보수적이고 false alarm이 줄지만 감지가 늦거나 약해지며, 높이면 민감해진다.
- `warning_level`
  - 의미: drift/warning 판정 민감도.
  - 값 범위: 보통 0과 1 사이 또는 detector 고유 threshold.
  - 조절 효과: drift 기준을 엄격하게 하면 오경보는 줄지만 놓칠 수 있고, 완화하면 더 자주 alarm이 난다.

## 15. Energy Distance

적용 variant: UNIVARIATE_ENERGY_DISTANCE; MULTIVARIATE_ENERGY_DISTANCE; ENERGY_DISTANCE_PERMUTATION_TEST

사용 파라미터 수: 8

- `current_window`
  - 의미: 비교 기준/현재 데이터 구간.
  - 값 범위: timestamp range, window id, 또는 sample set.
  - 조절 효과: reference를 길게 잡으면 안정적이지만 최신 정상 상태를 덜 반영하고, current를 짧게 잡으면 빠르지만 noise가 커진다.
- `distance_metric`
  - 의미: 거리 계산 방식.
  - 값 범위: Wasserstein, cosine, euclidean, JS, MMD 등.
  - 조절 효과: 어떤 차이에 민감한지가 달라지므로 데이터 형태에 맞춰 선택한다.
- `input_signal`
  - 의미: detector에 넣는 값.
  - 값 범위: feature, score, error_rate, loss, embedding, SHAP 등.
  - 조절 효과: 같은 method라도 입력 신호가 달라지면 drift 해석이 달라진다.
- `p_value_method`
  - 의미: p-value 또는 검정 확률 계산 방식.
  - 값 범위: exact, asymptotic, permutation, bootstrap 등.
  - 조절 효과: exact는 작은 표본에서 정확하지만 느리고, asymptotic은 빠르지만 작은 표본에서 부정확할 수 있다.
- `permutation_count`
  - 의미: permutation/bootstrap/random projection의 반복 수와 재현성 seed.
  - 값 범위: 반복 수는 1 이상의 정수, seed는 정수.
  - 조절 효과: 반복 수가 많으면 안정적이지만 느리고, seed를 고정하면 재현 가능하다.
- `random_seed`
  - 의미: permutation/bootstrap/random projection의 반복 수와 재현성 seed.
  - 값 범위: 반복 수는 1 이상의 정수, seed는 정수.
  - 조절 효과: 반복 수가 많으면 안정적이지만 느리고, seed를 고정하면 재현 가능하다.
- `reference_window`
  - 의미: 비교 기준/현재 데이터 구간.
  - 값 범위: timestamp range, window id, 또는 sample set.
  - 조절 효과: reference를 길게 잡으면 안정적이지만 최신 정상 상태를 덜 반영하고, current를 짧게 잡으면 빠르지만 noise가 커진다.
- `threshold_or_alpha`
  - 의미: 유의수준 또는 alarm 임계값.
  - 값 범위: 보통 0과 1 사이.
  - 조절 효과: 낮추면 보수적이고 false alarm이 줄지만 감지가 늦거나 약해지며, 높이면 민감해진다.

## 16. Epps-Singleton Test

적용 variant: TWO_SAMPLE_EPPS_SINGLETON; DISCRETE_EPPS_SINGLETON; ASYMPTOTIC_EPPS_SINGLETON

사용 파라미터 수: 8

- `asymptotic_method`
  - 의미: p-value 또는 검정 확률 계산 방식.
  - 값 범위: exact, asymptotic, permutation, bootstrap 등.
  - 조절 효과: exact는 작은 표본에서 정확하지만 느리고, asymptotic은 빠르지만 작은 표본에서 부정확할 수 있다.
- `correction_policy`
  - 의미: ties, continuity, missing value, small sample 보정 정책.
  - 값 범위: method별 policy 문자열 또는 boolean.
  - 조절 효과: 보정 정책은 p-value 안정성과 보수성에 영향을 준다.
- `current_window`
  - 의미: 비교 기준/현재 데이터 구간.
  - 값 범위: timestamp range, window id, 또는 sample set.
  - 조절 효과: reference를 길게 잡으면 안정적이지만 최신 정상 상태를 덜 반영하고, current를 짧게 잡으면 빠르지만 noise가 커진다.
- `input_signal`
  - 의미: detector에 넣는 값.
  - 값 범위: feature, score, error_rate, loss, embedding, SHAP 등.
  - 조절 효과: 같은 method라도 입력 신호가 달라지면 drift 해석이 달라진다.
- `p_value_method`
  - 의미: p-value 또는 검정 확률 계산 방식.
  - 값 범위: exact, asymptotic, permutation, bootstrap 등.
  - 조절 효과: exact는 작은 표본에서 정확하지만 느리고, asymptotic은 빠르지만 작은 표본에서 부정확할 수 있다.
- `reference_window`
  - 의미: 비교 기준/현재 데이터 구간.
  - 값 범위: timestamp range, window id, 또는 sample set.
  - 조절 효과: reference를 길게 잡으면 안정적이지만 최신 정상 상태를 덜 반영하고, current를 짧게 잡으면 빠르지만 noise가 커진다.
- `t_points`
  - 의미: 해당 method variant의 세부 설정값.
  - 값 범위: 구현 문서에서 정의한 enum, 정수, 실수 또는 구조화 값.
  - 조절 효과: 값 변경 시 detector 민감도, 계산 비용, 비교 가능성이 달라질 수 있으므로 변경 이력을 기록한다.
- `threshold_or_alpha`
  - 의미: 유의수준 또는 alarm 임계값.
  - 값 범위: 보통 0과 1 사이.
  - 조절 효과: 낮추면 보수적이고 false alarm이 줄지만 감지가 늦거나 약해지며, 높이면 민감해진다.

## 17. EWMA

적용 variant: EWMA_UNIVARIATE_CONTROL_CHART; EWMA_ONE_SIDED; EWMA_BASELINE_REPLAY_THRESHOLD

사용 파라미터 수: 17

- `baseline_replay_period`
  - 의미: 해당 method variant의 세부 설정값.
  - 값 범위: 구현 문서에서 정의한 enum, 정수, 실수 또는 구조화 값.
  - 조절 효과: 값 변경 시 detector 민감도, 계산 비용, 비교 가능성이 달라질 수 있으므로 변경 이력을 기록한다.
- `center_line`
  - 의미: control chart 또는 variance test의 기준 중심/분산/허용 편차.
  - 값 범위: metric scale의 실수, proportion은 0과 0.5 사이.
  - 조절 효과: 기준 중심이 잘못되면 정상 변화도 drift로 보일 수 있다.
- `control_width`
  - 의미: statistic, distance, score를 alarm으로 바꾸는 기준.
  - 값 범위: 측정값 scale에 따른 실수.
  - 조절 효과: 낮추면 민감도와 false alarm이 늘고, 높이면 안정적이지만 감지가 늦어진다.
- `current_window`
  - 의미: 비교 기준/현재 데이터 구간.
  - 값 범위: timestamp range, window id, 또는 sample set.
  - 조절 효과: reference를 길게 잡으면 안정적이지만 최신 정상 상태를 덜 반영하고, current를 짧게 잡으면 빠르지만 noise가 커진다.
- `direction`
  - 의미: 양측/단측 또는 증가/감소 감시 방향.
  - 값 범위: two-sided, greater, less, up, down, both.
  - 조절 효과: 사전 방향성이 있으면 민감도를 높일 수 있지만, 사후 선택하면 해석이 왜곡된다.
- `direction_or_alternative`
  - 의미: 양측/단측 또는 증가/감소 감시 방향.
  - 값 범위: two-sided, greater, less, up, down, both.
  - 조절 효과: 사전 방향성이 있으면 민감도를 높일 수 있지만, 사후 선택하면 해석이 왜곡된다.
- `empirical_quantile`
  - 의미: 해당 method variant의 세부 설정값.
  - 값 범위: 구현 문서에서 정의한 enum, 정수, 실수 또는 구조화 값.
  - 조절 효과: 값 변경 시 detector 민감도, 계산 비용, 비교 가능성이 달라질 수 있으므로 변경 이력을 기록한다.
- `input_signal`
  - 의미: detector에 넣는 값.
  - 값 범위: feature, score, error_rate, loss, embedding, SHAP 등.
  - 조절 효과: 같은 method라도 입력 신호가 달라지면 drift 해석이 달라진다.
- `lambda`
  - 의미: EWMA/GMA/HDDM-W/ECDD 계열의 가중치 또는 smoothing factor.
  - 값 범위: 보통 0과 1 사이.
  - 조절 효과: 클수록 최근 값에 민감하고, 작을수록 완만하지만 감지가 늦다.
- `lcl`
  - 의미: statistic, distance, score를 alarm으로 바꾸는 기준.
  - 값 범위: 측정값 scale에 따른 실수.
  - 조절 효과: 낮추면 민감도와 false alarm이 늘고, 높이면 안정적이지만 감지가 늦어진다.
- `reference_window`
  - 의미: 비교 기준/현재 데이터 구간.
  - 값 범위: timestamp range, window id, 또는 sample set.
  - 조절 효과: reference를 길게 잡으면 안정적이지만 최신 정상 상태를 덜 반영하고, current를 짧게 잡으면 빠르지만 noise가 커진다.
- `sigma`
  - 의미: control chart 또는 variance test의 기준 중심/분산/허용 편차.
  - 값 범위: metric scale의 실수, proportion은 0과 0.5 사이.
  - 조절 효과: 기준 중심이 잘못되면 정상 변화도 drift로 보일 수 있다.
- `target_false_alarm_rate`
  - 의미: 해당 method variant의 세부 설정값.
  - 값 범위: 구현 문서에서 정의한 enum, 정수, 실수 또는 구조화 값.
  - 조절 효과: 값 변경 시 detector 민감도, 계산 비용, 비교 가능성이 달라질 수 있으므로 변경 이력을 기록한다.
- `threshold`
  - 의미: statistic, distance, score를 alarm으로 바꾸는 기준.
  - 값 범위: 측정값 scale에 따른 실수.
  - 조절 효과: 낮추면 민감도와 false alarm이 늘고, 높이면 안정적이지만 감지가 늦어진다.
- `threshold_or_alpha`
  - 의미: 유의수준 또는 alarm 임계값.
  - 값 범위: 보통 0과 1 사이.
  - 조절 효과: 낮추면 보수적이고 false alarm이 줄지만 감지가 늦거나 약해지며, 높이면 민감해진다.
- `ucl`
  - 의미: statistic, distance, score를 alarm으로 바꾸는 기준.
  - 값 범위: 측정값 scale에 따른 실수.
  - 조절 효과: 낮추면 민감도와 false alarm이 늘고, 높이면 안정적이지만 감지가 늦어진다.
- `warmup_size`
  - 의미: 계산에 사용하는 표본 또는 stream 길이.
  - 값 범위: 1 이상의 정수.
  - 조절 효과: 작으면 빠르고 민감하지만 noise가 크고, 크면 안정적이지만 detection delay가 늘어난다.

## 18. Feature Map Drift

적용 variant: MODEL_FEATURE_MAP_KS; MODEL_FEATURE_MAP_MMD; LAYERWISE_FEATURE_MAP_DRIFT

사용 파라미터 수: 10

- `aggregation_level`
  - 의미: 설명 기반 drift 계산 설정.
  - 값 범위: explainer 이름, background data, class label, top-k 정수.
  - 조절 효과: background와 explainer가 바뀌면 SHAP/importance 분포가 달라진다.
- `current_window`
  - 의미: 비교 기준/현재 데이터 구간.
  - 값 범위: timestamp range, window id, 또는 sample set.
  - 조절 효과: reference를 길게 잡으면 안정적이지만 최신 정상 상태를 덜 반영하고, current를 짧게 잡으면 빠르지만 noise가 커진다.
- `distance_method`
  - 의미: 거리 계산 방식.
  - 값 범위: Wasserstein, cosine, euclidean, JS, MMD 등.
  - 조절 효과: 어떤 차이에 민감한지가 달라지므로 데이터 형태에 맞춰 선택한다.
- `feature_extractor_version`
  - 의미: feature map 또는 이미지 표현 추출 설정.
  - 값 범위: layer 이름, extractor 버전, preprocessing 함수.
  - 조절 효과: 추출 지점이나 전처리가 바뀌면 측정값 비교 가능성이 깨진다.
- `input_signal`
  - 의미: detector에 넣는 값.
  - 값 범위: feature, score, error_rate, loss, embedding, SHAP 등.
  - 조절 효과: 같은 method라도 입력 신호가 달라지면 drift 해석이 달라진다.
- `model_layer`
  - 의미: feature map 또는 이미지 표현 추출 설정.
  - 값 범위: layer 이름, extractor 버전, preprocessing 함수.
  - 조절 효과: 추출 지점이나 전처리가 바뀌면 측정값 비교 가능성이 깨진다.
- `preprocessing_fn`
  - 의미: feature map 또는 이미지 표현 추출 설정.
  - 값 범위: layer 이름, extractor 버전, preprocessing 함수.
  - 조절 효과: 추출 지점이나 전처리가 바뀌면 측정값 비교 가능성이 깨진다.
- `reference_window`
  - 의미: 비교 기준/현재 데이터 구간.
  - 값 범위: timestamp range, window id, 또는 sample set.
  - 조절 효과: reference를 길게 잡으면 안정적이지만 최신 정상 상태를 덜 반영하고, current를 짧게 잡으면 빠르지만 noise가 커진다.
- `threshold`
  - 의미: statistic, distance, score를 alarm으로 바꾸는 기준.
  - 값 범위: 측정값 scale에 따른 실수.
  - 조절 효과: 낮추면 민감도와 false alarm이 늘고, 높이면 안정적이지만 감지가 늦어진다.
- `threshold_or_alpha`
  - 의미: 유의수준 또는 alarm 임계값.
  - 값 범위: 보통 0과 1 사이.
  - 조절 효과: 낮추면 보수적이고 false alarm이 줄지만 감지가 늦거나 약해지며, 높이면 민감해진다.

## 19. Fisher's Exact Test

적용 variant: TWO_BY_TWO_FISHER_EXACT; ONE_SIDED_FISHER_EXACT; EXTENDED_CONTINGENCY_EXACT_TEST

사용 파라미터 수: 9

- `alternative`
  - 의미: 양측/단측 또는 증가/감소 감시 방향.
  - 값 범위: two-sided, greater, less, up, down, both.
  - 조절 효과: 사전 방향성이 있으면 민감도를 높일 수 있지만, 사후 선택하면 해석이 왜곡된다.
- `contingency_table`
  - 의미: 검정 또는 거리 계산에 들어가는 실제 표본/빈도/table.
  - 값 범위: 배열, count vector, contingency table.
  - 조절 효과: 표본 정의가 달라지면 결과가 달라지므로 filtering과 결측 처리 기준을 고정해야 한다.
- `current_window`
  - 의미: 비교 기준/현재 데이터 구간.
  - 값 범위: timestamp range, window id, 또는 sample set.
  - 조절 효과: reference를 길게 잡으면 안정적이지만 최신 정상 상태를 덜 반영하고, current를 짧게 잡으면 빠르지만 noise가 커진다.
- `direction_or_alternative`
  - 의미: 양측/단측 또는 증가/감소 감시 방향.
  - 값 범위: two-sided, greater, less, up, down, both.
  - 조절 효과: 사전 방향성이 있으면 민감도를 높일 수 있지만, 사후 선택하면 해석이 왜곡된다.
- `exact_method`
  - 의미: p-value 또는 검정 확률 계산 방식.
  - 값 범위: exact, asymptotic, permutation, bootstrap 등.
  - 조절 효과: exact는 작은 표본에서 정확하지만 느리고, asymptotic은 빠르지만 작은 표본에서 부정확할 수 있다.
- `input_signal`
  - 의미: detector에 넣는 값.
  - 값 범위: feature, score, error_rate, loss, embedding, SHAP 등.
  - 조절 효과: 같은 method라도 입력 신호가 달라지면 drift 해석이 달라진다.
- `reference_window`
  - 의미: 비교 기준/현재 데이터 구간.
  - 값 범위: timestamp range, window id, 또는 sample set.
  - 조절 효과: reference를 길게 잡으면 안정적이지만 최신 정상 상태를 덜 반영하고, current를 짧게 잡으면 빠르지만 noise가 커진다.
- `threshold_or_alpha`
  - 의미: 유의수준 또는 alarm 임계값.
  - 값 범위: 보통 0과 1 사이.
  - 조절 효과: 낮추면 보수적이고 false alarm이 줄지만 감지가 늦거나 약해지며, 높이면 민감해진다.
- `workspace_or_exact_method`
  - 의미: p-value 또는 검정 확률 계산 방식.
  - 값 범위: exact, asymptotic, permutation, bootstrap 등.
  - 조절 효과: exact는 작은 표본에서 정확하지만 느리고, asymptotic은 빠르지만 작은 표본에서 부정확할 수 있다.

## 20. F-test / Variance Test 계열

적용 variant: F_TEST_EQUAL_VARIANCE; ANOVA_F_TEST_GROUP_MEAN; MODEL_COMPARISON_F_TEST

사용 파라미터 수: 9

- `alpha`
  - 의미: 유의수준 또는 alarm 임계값.
  - 값 범위: 보통 0과 1 사이.
  - 조절 효과: 낮추면 보수적이고 false alarm이 줄지만 감지가 늦거나 약해지며, 높이면 민감해진다.
- `alternative`
  - 의미: 양측/단측 또는 증가/감소 감시 방향.
  - 값 범위: two-sided, greater, less, up, down, both.
  - 조절 효과: 사전 방향성이 있으면 민감도를 높일 수 있지만, 사후 선택하면 해석이 왜곡된다.
- `current_window`
  - 의미: 비교 기준/현재 데이터 구간.
  - 값 범위: timestamp range, window id, 또는 sample set.
  - 조절 효과: reference를 길게 잡으면 안정적이지만 최신 정상 상태를 덜 반영하고, current를 짧게 잡으면 빠르지만 noise가 커진다.
- `degrees_of_freedom`
  - 의미: 통계 모델, 분포 가정, 가설 정의.
  - 값 범위: method별 분포명, 파라미터, H0/H1 정의.
  - 조절 효과: 가정이 바뀌면 p-value와 alarm 의미가 바뀐다.
- `input_signal`
  - 의미: detector에 넣는 값.
  - 값 범위: feature, score, error_rate, loss, embedding, SHAP 등.
  - 조절 효과: 같은 method라도 입력 신호가 달라지면 drift 해석이 달라진다.
- `reference_window`
  - 의미: 비교 기준/현재 데이터 구간.
  - 값 범위: timestamp range, window id, 또는 sample set.
  - 조절 효과: reference를 길게 잡으면 안정적이지만 최신 정상 상태를 덜 반영하고, current를 짧게 잡으면 빠르지만 noise가 커진다.
- `threshold_or_alpha`
  - 의미: 유의수준 또는 alarm 임계값.
  - 값 범위: 보통 0과 1 사이.
  - 조절 효과: 낮추면 보수적이고 false alarm이 줄지만 감지가 늦거나 약해지며, 높이면 민감해진다.
- `variance_current`
  - 의미: 해당 method variant의 세부 설정값.
  - 값 범위: 구현 문서에서 정의한 enum, 정수, 실수 또는 구조화 값.
  - 조절 효과: 값 변경 시 detector 민감도, 계산 비용, 비교 가능성이 달라질 수 있으므로 변경 이력을 기록한다.
- `variance_reference`
  - 의미: 해당 method variant의 세부 설정값.
  - 값 범위: 구현 문서에서 정의한 enum, 정수, 실수 또는 구조화 값.
  - 조절 효과: 값 변경 시 detector 민감도, 계산 비용, 비교 가능성이 달라질 수 있으므로 변경 이력을 기록한다.

## 21. Geometric Moving Average

적용 variant: GMA_CONTROL_CHART; GMA_ONE_SIDED; GMA_WITH_EMPIRICAL_LIMIT

사용 파라미터 수: 10

- `center_line`
  - 의미: control chart 또는 variance test의 기준 중심/분산/허용 편차.
  - 값 범위: metric scale의 실수, proportion은 0과 0.5 사이.
  - 조절 효과: 기준 중심이 잘못되면 정상 변화도 drift로 보일 수 있다.
- `control_limit`
  - 의미: statistic, distance, score를 alarm으로 바꾸는 기준.
  - 값 범위: 측정값 scale에 따른 실수.
  - 조절 효과: 낮추면 민감도와 false alarm이 늘고, 높이면 안정적이지만 감지가 늦어진다.
- `current_window`
  - 의미: 비교 기준/현재 데이터 구간.
  - 값 범위: timestamp range, window id, 또는 sample set.
  - 조절 효과: reference를 길게 잡으면 안정적이지만 최신 정상 상태를 덜 반영하고, current를 짧게 잡으면 빠르지만 noise가 커진다.
- `direction`
  - 의미: 양측/단측 또는 증가/감소 감시 방향.
  - 값 범위: two-sided, greater, less, up, down, both.
  - 조절 효과: 사전 방향성이 있으면 민감도를 높일 수 있지만, 사후 선택하면 해석이 왜곡된다.
- `direction_or_alternative`
  - 의미: 양측/단측 또는 증가/감소 감시 방향.
  - 값 범위: two-sided, greater, less, up, down, both.
  - 조절 효과: 사전 방향성이 있으면 민감도를 높일 수 있지만, 사후 선택하면 해석이 왜곡된다.
- `input_signal`
  - 의미: detector에 넣는 값.
  - 값 범위: feature, score, error_rate, loss, embedding, SHAP 등.
  - 조절 효과: 같은 method라도 입력 신호가 달라지면 drift 해석이 달라진다.
- `lambda`
  - 의미: EWMA/GMA/HDDM-W/ECDD 계열의 가중치 또는 smoothing factor.
  - 값 범위: 보통 0과 1 사이.
  - 조절 효과: 클수록 최근 값에 민감하고, 작을수록 완만하지만 감지가 늦다.
- `reference_window`
  - 의미: 비교 기준/현재 데이터 구간.
  - 값 범위: timestamp range, window id, 또는 sample set.
  - 조절 효과: reference를 길게 잡으면 안정적이지만 최신 정상 상태를 덜 반영하고, current를 짧게 잡으면 빠르지만 noise가 커진다.
- `threshold_or_alpha`
  - 의미: 유의수준 또는 alarm 임계값.
  - 값 범위: 보통 0과 1 사이.
  - 조절 효과: 낮추면 보수적이고 false alarm이 줄지만 감지가 늦거나 약해지며, 높이면 민감해진다.
- `warmup_size`
  - 의미: 계산에 사용하는 표본 또는 stream 길이.
  - 값 범위: 1 이상의 정수.
  - 조절 효과: 작으면 빠르고 민감하지만 noise가 크고, 크면 안정적이지만 detection delay가 늘어난다.

## 22. Graph Embedding Drift

적용 variant: GRAPH_EMBEDDING_MMD; GRAPH_EMBEDDING_CENTROID_SHIFT; NODE_REPRESENTATION_DRIFT

사용 파라미터 수: 9

- `current_window`
  - 의미: 비교 기준/현재 데이터 구간.
  - 값 범위: timestamp range, window id, 또는 sample set.
  - 조절 효과: reference를 길게 잡으면 안정적이지만 최신 정상 상태를 덜 반영하고, current를 짧게 잡으면 빠르지만 noise가 커진다.
- `distance_method`
  - 의미: 거리 계산 방식.
  - 값 범위: Wasserstein, cosine, euclidean, JS, MMD 등.
  - 조절 효과: 어떤 차이에 민감한지가 달라지므로 데이터 형태에 맞춰 선택한다.
- `graph_embedding_model`
  - 의미: text/embedding/domain classifier 구성.
  - 값 범위: 모델명, 버전, split 비율, cluster 수.
  - 조절 효과: 모델이나 vectorizer가 바뀌면 drift처럼 보일 수 있으므로 버전 고정이 중요하다.
- `input_signal`
  - 의미: detector에 넣는 값.
  - 값 범위: feature, score, error_rate, loss, embedding, SHAP 등.
  - 조절 효과: 같은 method라도 입력 신호가 달라지면 drift 해석이 달라진다.
- `node_or_graph_level`
  - 의미: graph embedding drift 계산 단위와 sampling.
  - 값 범위: 모델명, node/graph level, sampling policy.
  - 조절 효과: node-level은 국소 변화에, graph-level은 전체 구조 변화에 더 가깝다.
- `reference_window`
  - 의미: 비교 기준/현재 데이터 구간.
  - 값 범위: timestamp range, window id, 또는 sample set.
  - 조절 효과: reference를 길게 잡으면 안정적이지만 최신 정상 상태를 덜 반영하고, current를 짧게 잡으면 빠르지만 noise가 커진다.
- `sampling_policy`
  - 의미: graph embedding drift 계산 단위와 sampling.
  - 값 범위: 모델명, node/graph level, sampling policy.
  - 조절 효과: node-level은 국소 변화에, graph-level은 전체 구조 변화에 더 가깝다.
- `threshold`
  - 의미: statistic, distance, score를 alarm으로 바꾸는 기준.
  - 값 범위: 측정값 scale에 따른 실수.
  - 조절 효과: 낮추면 민감도와 false alarm이 늘고, 높이면 안정적이지만 감지가 늦어진다.
- `threshold_or_alpha`
  - 의미: 유의수준 또는 alarm 임계값.
  - 값 범위: 보통 0과 1 사이.
  - 조절 효과: 낮추면 보수적이고 false alarm이 줄지만 감지가 늦거나 약해지며, 높이면 민감해진다.

## 23. G-test

적용 variant: LIKELIHOOD_RATIO_G_TEST_GOF; LIKELIHOOD_RATIO_G_TEST_INDEPENDENCE; G_TEST_WITH_SMALL_COUNT_CAUTION

사용 파라미터 수: 9

- `current_window`
  - 의미: 비교 기준/현재 데이터 구간.
  - 값 범위: timestamp range, window id, 또는 sample set.
  - 조절 효과: reference를 길게 잡으면 안정적이지만 최신 정상 상태를 덜 반영하고, current를 짧게 잡으면 빠르지만 noise가 커진다.
- `degrees_of_freedom`
  - 의미: 통계 모델, 분포 가정, 가설 정의.
  - 값 범위: method별 분포명, 파라미터, H0/H1 정의.
  - 조절 효과: 가정이 바뀌면 p-value와 alarm 의미가 바뀐다.
- `expected_counts`
  - 의미: 검정 또는 거리 계산에 들어가는 실제 표본/빈도/table.
  - 값 범위: 배열, count vector, contingency table.
  - 조절 효과: 표본 정의가 달라지면 결과가 달라지므로 filtering과 결측 처리 기준을 고정해야 한다.
- `input_signal`
  - 의미: detector에 넣는 값.
  - 값 범위: feature, score, error_rate, loss, embedding, SHAP 등.
  - 조절 효과: 같은 method라도 입력 신호가 달라지면 drift 해석이 달라진다.
- `lambda_or_log_likelihood_policy`
  - 의미: 해당 method variant의 세부 설정값.
  - 값 범위: 구현 문서에서 정의한 enum, 정수, 실수 또는 구조화 값.
  - 조절 효과: 값 변경 시 detector 민감도, 계산 비용, 비교 가능성이 달라질 수 있으므로 변경 이력을 기록한다.
- `min_expected_count`
  - 의미: 해당 method variant의 세부 설정값.
  - 값 범위: 구현 문서에서 정의한 enum, 정수, 실수 또는 구조화 값.
  - 조절 효과: 값 변경 시 detector 민감도, 계산 비용, 비교 가능성이 달라질 수 있으므로 변경 이력을 기록한다.
- `observed_counts`
  - 의미: 검정 또는 거리 계산에 들어가는 실제 표본/빈도/table.
  - 값 범위: 배열, count vector, contingency table.
  - 조절 효과: 표본 정의가 달라지면 결과가 달라지므로 filtering과 결측 처리 기준을 고정해야 한다.
- `reference_window`
  - 의미: 비교 기준/현재 데이터 구간.
  - 값 범위: timestamp range, window id, 또는 sample set.
  - 조절 효과: reference를 길게 잡으면 안정적이지만 최신 정상 상태를 덜 반영하고, current를 짧게 잡으면 빠르지만 noise가 커진다.
- `threshold_or_alpha`
  - 의미: 유의수준 또는 alarm 임계값.
  - 값 범위: 보통 0과 1 사이.
  - 조절 효과: 낮추면 보수적이고 false alarm이 줄지만 감지가 늦거나 약해지며, 높이면 민감해진다.

## 24. HAT

적용 variant: HAT_ADWIN_NODE_MONITORING; HAT_ALTERNATE_TREE_REPLACEMENT

사용 파라미터 수: 11

- `alternate_tree_policy`
  - 의미: 해당 method variant의 세부 설정값.
  - 값 범위: 구현 문서에서 정의한 enum, 정수, 실수 또는 구조화 값.
  - 조절 효과: 값 변경 시 detector 민감도, 계산 비용, 비교 가능성이 달라질 수 있으므로 변경 이력을 기록한다.
- `current_window`
  - 의미: 비교 기준/현재 데이터 구간.
  - 값 범위: timestamp range, window id, 또는 sample set.
  - 조절 효과: reference를 길게 잡으면 안정적이지만 최신 정상 상태를 덜 반영하고, current를 짧게 잡으면 빠르지만 noise가 커진다.
- `drift_detector`
  - 의미: drift 감지와 재학습/운영 적응 정책.
  - 값 범위: detector/model 이름, metric 이름, 최소 표본 수.
  - 조절 효과: 자동 조치 민감도와 운영 리스크를 결정한다.
- `grace_period`
  - 의미: 계산에 사용하는 표본 또는 stream 길이.
  - 값 범위: 1 이상의 정수.
  - 조절 효과: 작으면 빠르고 민감하지만 noise가 크고, 크면 안정적이지만 detection delay가 늘어난다.
- `input_signal`
  - 의미: detector에 넣는 값.
  - 값 범위: feature, score, error_rate, loss, embedding, SHAP 등.
  - 조절 효과: 같은 method라도 입력 신호가 달라지면 drift 해석이 달라진다.
- `label_delay_policy`
  - 의미: supervised error/performance stream 정의.
  - 값 범위: label 지연 처리 정책, 오류 정의, accuracy 계산 방식.
  - 조절 효과: label 처리 방식이 바뀌면 concept/performance drift 해석이 달라진다.
- `leaf_prediction`
  - 의미: 해당 method variant의 세부 설정값.
  - 값 범위: 구현 문서에서 정의한 enum, 정수, 실수 또는 구조화 값.
  - 조절 효과: 값 변경 시 detector 민감도, 계산 비용, 비교 가능성이 달라질 수 있으므로 변경 이력을 기록한다.
- `reference_window`
  - 의미: 비교 기준/현재 데이터 구간.
  - 값 범위: timestamp range, window id, 또는 sample set.
  - 조절 효과: reference를 길게 잡으면 안정적이지만 최신 정상 상태를 덜 반영하고, current를 짧게 잡으면 빠르지만 noise가 커진다.
- `split_confidence`
  - 의미: 해당 method variant의 세부 설정값.
  - 값 범위: 구현 문서에서 정의한 enum, 정수, 실수 또는 구조화 값.
  - 조절 효과: 값 변경 시 detector 민감도, 계산 비용, 비교 가능성이 달라질 수 있으므로 변경 이력을 기록한다.
- `threshold_or_alpha`
  - 의미: 유의수준 또는 alarm 임계값.
  - 값 범위: 보통 0과 1 사이.
  - 조절 효과: 낮추면 보수적이고 false alarm이 줄지만 감지가 늦거나 약해지며, 높이면 민감해진다.
- `tie_threshold`
  - 의미: statistic, distance, score를 alarm으로 바꾸는 기준.
  - 값 범위: 측정값 scale에 따른 실수.
  - 조절 효과: 낮추면 민감도와 false alarm이 늘고, 높이면 안정적이지만 감지가 늦어진다.

## 25. HDDM-A

적용 variant: HDDM_A_HOEFFDING_BOUND; HDDM_A_WARNING_DRIFT; HDDM_A_TWO_SIDED

사용 파라미터 수: 8

- `current_window`
  - 의미: 비교 기준/현재 데이터 구간.
  - 값 범위: timestamp range, window id, 또는 sample set.
  - 조절 효과: reference를 길게 잡으면 안정적이지만 최신 정상 상태를 덜 반영하고, current를 짧게 잡으면 빠르지만 noise가 커진다.
- `drift_confidence`
  - 의미: drift/warning 판정 민감도.
  - 값 범위: 보통 0과 1 사이 또는 detector 고유 threshold.
  - 조절 효과: drift 기준을 엄격하게 하면 오경보는 줄지만 놓칠 수 있고, 완화하면 더 자주 alarm이 난다.
- `input_signal`
  - 의미: detector에 넣는 값.
  - 값 범위: feature, score, error_rate, loss, embedding, SHAP 등.
  - 조절 효과: 같은 method라도 입력 신호가 달라지면 drift 해석이 달라진다.
- `min_instances`
  - 의미: 계산에 사용하는 표본 또는 stream 길이.
  - 값 범위: 1 이상의 정수.
  - 조절 효과: 작으면 빠르고 민감하지만 noise가 크고, 크면 안정적이지만 detection delay가 늘어난다.
- `reference_window`
  - 의미: 비교 기준/현재 데이터 구간.
  - 값 범위: timestamp range, window id, 또는 sample set.
  - 조절 효과: reference를 길게 잡으면 안정적이지만 최신 정상 상태를 덜 반영하고, current를 짧게 잡으면 빠르지만 noise가 커진다.
- `threshold_or_alpha`
  - 의미: 유의수준 또는 alarm 임계값.
  - 값 범위: 보통 0과 1 사이.
  - 조절 효과: 낮추면 보수적이고 false alarm이 줄지만 감지가 늦거나 약해지며, 높이면 민감해진다.
- `two_sided`
  - 의미: 양측/단측 또는 증가/감소 감시 방향.
  - 값 범위: two-sided, greater, less, up, down, both.
  - 조절 효과: 사전 방향성이 있으면 민감도를 높일 수 있지만, 사후 선택하면 해석이 왜곡된다.
- `warning_confidence`
  - 의미: drift/warning 판정 민감도.
  - 값 범위: 보통 0과 1 사이 또는 detector 고유 threshold.
  - 조절 효과: drift 기준을 엄격하게 하면 오경보는 줄지만 놓칠 수 있고, 완화하면 더 자주 alarm이 난다.

## 26. HDDM-W

적용 variant: HDDM_W_WEIGHTED_AVERAGE; HDDM_W_WARNING_DRIFT; HDDM_W_RECENT_ERROR_WEIGHTING

사용 파라미터 수: 9

- `current_window`
  - 의미: 비교 기준/현재 데이터 구간.
  - 값 범위: timestamp range, window id, 또는 sample set.
  - 조절 효과: reference를 길게 잡으면 안정적이지만 최신 정상 상태를 덜 반영하고, current를 짧게 잡으면 빠르지만 noise가 커진다.
- `drift_confidence`
  - 의미: drift/warning 판정 민감도.
  - 값 범위: 보통 0과 1 사이 또는 detector 고유 threshold.
  - 조절 효과: drift 기준을 엄격하게 하면 오경보는 줄지만 놓칠 수 있고, 완화하면 더 자주 alarm이 난다.
- `input_signal`
  - 의미: detector에 넣는 값.
  - 값 범위: feature, score, error_rate, loss, embedding, SHAP 등.
  - 조절 효과: 같은 method라도 입력 신호가 달라지면 drift 해석이 달라진다.
- `lambda`
  - 의미: EWMA/GMA/HDDM-W/ECDD 계열의 가중치 또는 smoothing factor.
  - 값 범위: 보통 0과 1 사이.
  - 조절 효과: 클수록 최근 값에 민감하고, 작을수록 완만하지만 감지가 늦다.
- `min_instances`
  - 의미: 계산에 사용하는 표본 또는 stream 길이.
  - 값 범위: 1 이상의 정수.
  - 조절 효과: 작으면 빠르고 민감하지만 noise가 크고, 크면 안정적이지만 detection delay가 늘어난다.
- `reference_window`
  - 의미: 비교 기준/현재 데이터 구간.
  - 값 범위: timestamp range, window id, 또는 sample set.
  - 조절 효과: reference를 길게 잡으면 안정적이지만 최신 정상 상태를 덜 반영하고, current를 짧게 잡으면 빠르지만 noise가 커진다.
- `threshold_or_alpha`
  - 의미: 유의수준 또는 alarm 임계값.
  - 값 범위: 보통 0과 1 사이.
  - 조절 효과: 낮추면 보수적이고 false alarm이 줄지만 감지가 늦거나 약해지며, 높이면 민감해진다.
- `two_sided`
  - 의미: 양측/단측 또는 증가/감소 감시 방향.
  - 값 범위: two-sided, greater, less, up, down, both.
  - 조절 효과: 사전 방향성이 있으면 민감도를 높일 수 있지만, 사후 선택하면 해석이 왜곡된다.
- `warning_confidence`
  - 의미: drift/warning 판정 민감도.
  - 값 범위: 보통 0과 1 사이 또는 detector 고유 threshold.
  - 조절 효과: drift 기준을 엄격하게 하면 오경보는 줄지만 놓칠 수 있고, 완화하면 더 자주 alarm이 난다.

## 27. Hellinger Distance

적용 variant: DISCRETE_HELLINGER_DISTANCE; HISTOGRAM_HELLINGER_DISTANCE; CATEGORICAL_HELLINGER_DISTANCE

사용 파라미터 수: 7

- `binning_policy`
  - 의미: 연속값을 구간화하거나 category bin을 정하는 방식.
  - 값 범위: 정책 문자열, bin 개수는 양의 정수.
  - 조절 효과: bin이 많으면 세밀하지만 표본 부족에 취약하고, 적으면 안정적이지만 세부 변화를 놓친다.
- `current_window`
  - 의미: 비교 기준/현재 데이터 구간.
  - 값 범위: timestamp range, window id, 또는 sample set.
  - 조절 효과: reference를 길게 잡으면 안정적이지만 최신 정상 상태를 덜 반영하고, current를 짧게 잡으면 빠르지만 noise가 커진다.
- `input_signal`
  - 의미: detector에 넣는 값.
  - 값 범위: feature, score, error_rate, loss, embedding, SHAP 등.
  - 조절 효과: 같은 method라도 입력 신호가 달라지면 drift 해석이 달라진다.
- `normalization_policy`
  - 의미: feature, histogram, metric scale 정규화 방식.
  - 값 범위: none, standard, minmax, l2, probability 등.
  - 조절 효과: 정규화하면 feature 간 비교가 쉬워지지만 원 단위 해석은 약해진다.
- `reference_window`
  - 의미: 비교 기준/현재 데이터 구간.
  - 값 범위: timestamp range, window id, 또는 sample set.
  - 조절 효과: reference를 길게 잡으면 안정적이지만 최신 정상 상태를 덜 반영하고, current를 짧게 잡으면 빠르지만 noise가 커진다.
- `smoothing_epsilon`
  - 의미: zero probability 또는 희소 category 보정.
  - 값 범위: 0 이상의 작은 실수 또는 정책.
  - 조절 효과: 값을 키우면 안정적이지만 작은 category 변화가 희석된다.
- `threshold_or_alpha`
  - 의미: 유의수준 또는 alarm 임계값.
  - 값 범위: 보통 0과 1 사이.
  - 조절 효과: 낮추면 보수적이고 false alarm이 줄지만 감지가 늦거나 약해지며, 높이면 민감해진다.

## 28. Histogram Intersection Normalized Complement

적용 variant: HINC_CATEGORICAL; HINC_HISTOGRAM_NUMERIC; HINC_IMAGE_FEATURE

사용 파라미터 수: 8

- `binning_policy`
  - 의미: 연속값을 구간화하거나 category bin을 정하는 방식.
  - 값 범위: 정책 문자열, bin 개수는 양의 정수.
  - 조절 효과: bin이 많으면 세밀하지만 표본 부족에 취약하고, 적으면 안정적이지만 세부 변화를 놓친다.
- `current_window`
  - 의미: 비교 기준/현재 데이터 구간.
  - 값 범위: timestamp range, window id, 또는 sample set.
  - 조절 효과: reference를 길게 잡으면 안정적이지만 최신 정상 상태를 덜 반영하고, current를 짧게 잡으면 빠르지만 noise가 커진다.
- `histogram_normalization`
  - 의미: feature, histogram, metric scale 정규화 방식.
  - 값 범위: none, standard, minmax, l2, probability 등.
  - 조절 효과: 정규화하면 feature 간 비교가 쉬워지지만 원 단위 해석은 약해진다.
- `image_feature_extractor`
  - 의미: feature map 또는 이미지 표현 추출 설정.
  - 값 범위: layer 이름, extractor 버전, preprocessing 함수.
  - 조절 효과: 추출 지점이나 전처리가 바뀌면 측정값 비교 가능성이 깨진다.
- `input_signal`
  - 의미: detector에 넣는 값.
  - 값 범위: feature, score, error_rate, loss, embedding, SHAP 등.
  - 조절 효과: 같은 method라도 입력 신호가 달라지면 drift 해석이 달라진다.
- `reference_window`
  - 의미: 비교 기준/현재 데이터 구간.
  - 값 범위: timestamp range, window id, 또는 sample set.
  - 조절 효과: reference를 길게 잡으면 안정적이지만 최신 정상 상태를 덜 반영하고, current를 짧게 잡으면 빠르지만 noise가 커진다.
- `threshold`
  - 의미: statistic, distance, score를 alarm으로 바꾸는 기준.
  - 값 범위: 측정값 scale에 따른 실수.
  - 조절 효과: 낮추면 민감도와 false alarm이 늘고, 높이면 안정적이지만 감지가 늦어진다.
- `threshold_or_alpha`
  - 의미: 유의수준 또는 alarm 임계값.
  - 값 범위: 보통 0과 1 사이.
  - 조절 효과: 낮추면 보수적이고 false alarm이 줄지만 감지가 늦거나 약해지며, 높이면 민감해진다.

## 29. Hotelling T2

적용 variant: HOTELLING_T2_ONE_SAMPLE_PHASE_II; HOTELLING_T2_TWO_SAMPLE; REGULARIZED_HOTELLING_T2

사용 파라미터 수: 14

- `alpha`
  - 의미: 유의수준 또는 alarm 임계값.
  - 값 범위: 보통 0과 1 사이.
  - 조절 효과: 낮추면 보수적이고 false alarm이 줄지만 감지가 늦거나 약해지며, 높이면 민감해진다.
- `control_limit`
  - 의미: statistic, distance, score를 alarm으로 바꾸는 기준.
  - 값 범위: 측정값 scale에 따른 실수.
  - 조절 효과: 낮추면 민감도와 false alarm이 늘고, 높이면 안정적이지만 감지가 늦어진다.
- `covariance_estimator`
  - 의미: 평균/공분산 기반 다변량 기준.
  - 값 범위: 벡터, 행렬, estimator 이름, 0 이상의 regularization 값.
  - 조절 효과: regularization과 robust estimator는 안정성을 높이지만 statistic scale을 바꾼다.
- `current_window`
  - 의미: 비교 기준/현재 데이터 구간.
  - 값 범위: timestamp range, window id, 또는 sample set.
  - 조절 효과: reference를 길게 잡으면 안정적이지만 최신 정상 상태를 덜 반영하고, current를 짧게 잡으면 빠르지만 noise가 커진다.
- `equal_covariance_assumption`
  - 의미: 평균/공분산 기반 다변량 기준.
  - 값 범위: 벡터, 행렬, estimator 이름, 0 이상의 regularization 값.
  - 조절 효과: regularization과 robust estimator는 안정성을 높이지만 statistic scale을 바꾼다.
- `input_signal`
  - 의미: detector에 넣는 값.
  - 값 범위: feature, score, error_rate, loss, embedding, SHAP 등.
  - 조절 효과: 같은 method라도 입력 신호가 달라지면 drift 해석이 달라진다.
- `mean_reference`
  - 의미: 평균/공분산 기반 다변량 기준.
  - 값 범위: 벡터, 행렬, estimator 이름, 0 이상의 regularization 값.
  - 조절 효과: regularization과 robust estimator는 안정성을 높이지만 statistic scale을 바꾼다.
- `pca_components`
  - 의미: 평균/공분산 기반 다변량 기준.
  - 값 범위: 벡터, 행렬, estimator 이름, 0 이상의 regularization 값.
  - 조절 효과: regularization과 robust estimator는 안정성을 높이지만 statistic scale을 바꾼다.
- `pooled_covariance`
  - 의미: 평균/공분산 기반 다변량 기준.
  - 값 범위: 벡터, 행렬, estimator 이름, 0 이상의 regularization 값.
  - 조절 효과: regularization과 robust estimator는 안정성을 높이지만 statistic scale을 바꾼다.
- `reference_window`
  - 의미: 비교 기준/현재 데이터 구간.
  - 값 범위: timestamp range, window id, 또는 sample set.
  - 조절 효과: reference를 길게 잡으면 안정적이지만 최신 정상 상태를 덜 반영하고, current를 짧게 잡으면 빠르지만 noise가 커진다.
- `regularization_method`
  - 의미: 평균/공분산 기반 다변량 기준.
  - 값 범위: 벡터, 행렬, estimator 이름, 0 이상의 regularization 값.
  - 조절 효과: regularization과 robust estimator는 안정성을 높이지만 statistic scale을 바꾼다.
- `regularization_strength`
  - 의미: 평균/공분산 기반 다변량 기준.
  - 값 범위: 벡터, 행렬, estimator 이름, 0 이상의 regularization 값.
  - 조절 효과: regularization과 robust estimator는 안정성을 높이지만 statistic scale을 바꾼다.
- `shrinkage_alpha`
  - 의미: 평균/공분산 기반 다변량 기준.
  - 값 범위: 벡터, 행렬, estimator 이름, 0 이상의 regularization 값.
  - 조절 효과: regularization과 robust estimator는 안정성을 높이지만 statistic scale을 바꾼다.
- `threshold_or_alpha`
  - 의미: 유의수준 또는 alarm 임계값.
  - 값 범위: 보통 0과 1 사이.
  - 조절 효과: 낮추면 보수적이고 false alarm이 줄지만 감지가 늦거나 약해지며, 높이면 민감해진다.

## 30. Jensen-Shannon Distance

적용 variant: JENSEN_SHANNON_DIVERGENCE; JENSEN_SHANNON_DISTANCE; MULTICLASS_PROBABILITY_JS; TEXT_TOPIC_JS

사용 파라미터 수: 4

- `current_window`
  - 의미: 비교 기준/현재 데이터 구간.
  - 값 범위: timestamp range, window id, 또는 sample set.
  - 조절 효과: reference를 길게 잡으면 안정적이지만 최신 정상 상태를 덜 반영하고, current를 짧게 잡으면 빠르지만 noise가 커진다.
- `input_signal`
  - 의미: detector에 넣는 값.
  - 값 범위: feature, score, error_rate, loss, embedding, SHAP 등.
  - 조절 효과: 같은 method라도 입력 신호가 달라지면 drift 해석이 달라진다.
- `reference_window`
  - 의미: 비교 기준/현재 데이터 구간.
  - 값 범위: timestamp range, window id, 또는 sample set.
  - 조절 효과: reference를 길게 잡으면 안정적이지만 최신 정상 상태를 덜 반영하고, current를 짧게 잡으면 빠르지만 noise가 커진다.
- `threshold_or_alpha`
  - 의미: 유의수준 또는 alarm 임계값.
  - 값 범위: 보통 0과 1 사이.
  - 조절 효과: 낮추면 보수적이고 false alarm이 줄지만 감지가 늦거나 약해지며, 높이면 민감해진다.

## 31. KL Divergence

적용 variant: DISCRETE_KL_DIVERGENCE; HISTOGRAM_KL_DIVERGENCE; SMOOTHED_KL_DIVERGENCE; SYMMETRIZED_KL

사용 파라미터 수: 9

- `binning_policy`
  - 의미: 연속값을 구간화하거나 category bin을 정하는 방식.
  - 값 범위: 정책 문자열, bin 개수는 양의 정수.
  - 조절 효과: bin이 많으면 세밀하지만 표본 부족에 취약하고, 적으면 안정적이지만 세부 변화를 놓친다.
- `current_window`
  - 의미: 비교 기준/현재 데이터 구간.
  - 값 범위: timestamp range, window id, 또는 sample set.
  - 조절 효과: reference를 길게 잡으면 안정적이지만 최신 정상 상태를 덜 반영하고, current를 짧게 잡으면 빠르지만 noise가 커진다.
- `input_signal`
  - 의미: detector에 넣는 값.
  - 값 범위: feature, score, error_rate, loss, embedding, SHAP 등.
  - 조절 효과: 같은 method라도 입력 신호가 달라지면 drift 해석이 달라진다.
- `log_base`
  - 의미: 해당 method variant의 세부 설정값.
  - 값 범위: 구현 문서에서 정의한 enum, 정수, 실수 또는 구조화 값.
  - 조절 효과: 값 변경 시 detector 민감도, 계산 비용, 비교 가능성이 달라질 수 있으므로 변경 이력을 기록한다.
- `normalization_policy`
  - 의미: feature, histogram, metric scale 정규화 방식.
  - 값 범위: none, standard, minmax, l2, probability 등.
  - 조절 효과: 정규화하면 feature 간 비교가 쉬워지지만 원 단위 해석은 약해진다.
- `reference_window`
  - 의미: 비교 기준/현재 데이터 구간.
  - 값 범위: timestamp range, window id, 또는 sample set.
  - 조절 효과: reference를 길게 잡으면 안정적이지만 최신 정상 상태를 덜 반영하고, current를 짧게 잡으면 빠르지만 noise가 커진다.
- `smoothing_epsilon`
  - 의미: zero probability 또는 희소 category 보정.
  - 값 범위: 0 이상의 작은 실수 또는 정책.
  - 조절 효과: 값을 키우면 안정적이지만 작은 category 변화가 희석된다.
- `threshold_or_alpha`
  - 의미: 유의수준 또는 alarm 임계값.
  - 값 범위: 보통 0과 1 사이.
  - 조절 효과: 낮추면 보수적이고 false alarm이 줄지만 감지가 늦거나 약해지며, 높이면 민감해진다.
- `zero_probability_policy`
  - 의미: zero probability 또는 희소 category 보정.
  - 값 범위: 0 이상의 작은 실수 또는 정책.
  - 조절 효과: 값을 키우면 안정적이지만 작은 category 변화가 희석된다.

## 32. KS Test

적용 variant: ONE_SAMPLE_KS_KNOWN_CDF; TWO_SAMPLE_KS_TWO_SIDED; TWO_SAMPLE_KS_ONE_SIDED_GREATER; TWO_SAMPLE_KS_ONE_SIDED_LESS; TWO_SAMPLE_KS_EXACT_PVALUE; TWO_SAMPLE_KS_ASYMPTOTIC_PVALUE; KS_WITH_TIES_OR_DISCRETE_CAUTION; LILLIEFORS_RELATED_ONE_SAMPLE; HIGHER_ORDER_KS; TWO_SAMPLE_KS_APPROX_QUANTILE

사용 파라미터 수: 21

- `alternative`
  - 의미: 양측/단측 또는 증가/감소 감시 방향.
  - 값 범위: two-sided, greater, less, up, down, both.
  - 조절 효과: 사전 방향성이 있으면 민감도를 높일 수 있지만, 사후 선택하면 해석이 왜곡된다.
- `approximation_error_bound`
  - 의미: 대용량/근사 계산 설정.
  - 값 범위: count는 양의 정수, error는 0 이상의 실수, policy는 문자열.
  - 조절 효과: 근사 오차와 계산 비용의 trade-off를 만든다.
- `asymptotic_method`
  - 의미: p-value 또는 검정 확률 계산 방식.
  - 값 범위: exact, asymptotic, permutation, bootstrap 등.
  - 조절 효과: exact는 작은 표본에서 정확하지만 느리고, asymptotic은 빠르지만 작은 표본에서 부정확할 수 있다.
- `current_window`
  - 의미: 비교 기준/현재 데이터 구간.
  - 값 범위: timestamp range, window id, 또는 sample set.
  - 조절 효과: reference를 길게 잡으면 안정적이지만 최신 정상 상태를 덜 반영하고, current를 짧게 잡으면 빠르지만 noise가 커진다.
- `direction_or_alternative`
  - 의미: 양측/단측 또는 증가/감소 감시 방향.
  - 값 범위: two-sided, greater, less, up, down, both.
  - 조절 효과: 사전 방향성이 있으면 민감도를 높일 수 있지만, 사후 선택하면 해석이 왜곡된다.
- `distribution_parameters`
  - 의미: 통계 모델, 분포 가정, 가설 정의.
  - 값 범위: method별 분포명, 파라미터, H0/H1 정의.
  - 조절 효과: 가정이 바뀌면 p-value와 alarm 의미가 바뀐다.
- `exact_method`
  - 의미: p-value 또는 검정 확률 계산 방식.
  - 값 범위: exact, asymptotic, permutation, bootstrap 등.
  - 조절 효과: exact는 작은 표본에서 정확하지만 느리고, asymptotic은 빠르지만 작은 표본에서 부정확할 수 있다.
- `input_signal`
  - 의미: detector에 넣는 값.
  - 값 범위: feature, score, error_rate, loss, embedding, SHAP 등.
  - 조절 효과: 같은 method라도 입력 신호가 달라지면 drift 해석이 달라진다.
- `multiple_testing_correction`
  - 의미: ties, continuity, missing value, small sample 보정 정책.
  - 값 범위: method별 policy 문자열 또는 boolean.
  - 조절 효과: 보정 정책은 p-value 안정성과 보수성에 영향을 준다.
- `p_value_method`
  - 의미: p-value 또는 검정 확률 계산 방식.
  - 값 범위: exact, asymptotic, permutation, bootstrap 등.
  - 조절 효과: exact는 작은 표본에서 정확하지만 느리고, asymptotic은 빠르지만 작은 표본에서 부정확할 수 있다.
- `p_value_method=asymptotic`
  - 의미: 해당 method variant의 세부 설정값.
  - 값 범위: 구현 문서에서 정의한 enum, 정수, 실수 또는 구조화 값.
  - 조절 효과: 값 변경 시 detector 민감도, 계산 비용, 비교 가능성이 달라질 수 있으므로 변경 이력을 기록한다.
- `p_value_method=exact`
  - 의미: 해당 method variant의 세부 설정값.
  - 값 범위: 구현 문서에서 정의한 enum, 정수, 실수 또는 구조화 값.
  - 조절 효과: 값 변경 시 detector 민감도, 계산 비용, 비교 가능성이 달라질 수 있으므로 변경 이력을 기록한다.
- `permutation_or_bootstrap_fallback`
  - 의미: 해당 method variant의 세부 설정값.
  - 값 범위: 구현 문서에서 정의한 enum, 정수, 실수 또는 구조화 값.
  - 조절 효과: 값 변경 시 detector 민감도, 계산 비용, 비교 가능성이 달라질 수 있으므로 변경 이력을 기록한다.
- `quantile_error`
  - 의미: 대용량/근사 계산 설정.
  - 값 범위: count는 양의 정수, error는 0 이상의 실수, policy는 문자열.
  - 조절 효과: 근사 오차와 계산 비용의 trade-off를 만든다.
- `reference_cdf`
  - 의미: 통계 모델, 분포 가정, 가설 정의.
  - 값 범위: method별 분포명, 파라미터, H0/H1 정의.
  - 조절 효과: 가정이 바뀌면 p-value와 alarm 의미가 바뀐다.
- `reference_window`
  - 의미: 비교 기준/현재 데이터 구간.
  - 값 범위: timestamp range, window id, 또는 sample set.
  - 조절 효과: reference를 길게 잡으면 안정적이지만 최신 정상 상태를 덜 반영하고, current를 짧게 잡으면 빠르지만 noise가 커진다.
- `sample_current`
  - 의미: 검정 또는 거리 계산에 들어가는 실제 표본/빈도/table.
  - 값 범위: 배열, count vector, contingency table.
  - 조절 효과: 표본 정의가 달라지면 결과가 달라지므로 filtering과 결측 처리 기준을 고정해야 한다.
- `sample_reference`
  - 의미: 검정 또는 거리 계산에 들어가는 실제 표본/빈도/table.
  - 값 범위: 배열, count vector, contingency table.
  - 조절 효과: 표본 정의가 달라지면 결과가 달라지므로 filtering과 결측 처리 기준을 고정해야 한다.
- `summary_method`
  - 의미: 대용량/근사 계산 설정.
  - 값 범위: count는 양의 정수, error는 0 이상의 실수, policy는 문자열.
  - 조절 효과: 근사 오차와 계산 비용의 trade-off를 만든다.
- `threshold_or_alpha`
  - 의미: 유의수준 또는 alarm 임계값.
  - 값 범위: 보통 0과 1 사이.
  - 조절 효과: 낮추면 보수적이고 false alarm이 줄지만 감지가 늦거나 약해지며, 높이면 민감해진다.
- `tie_policy`
  - 의미: ties, continuity, missing value, small sample 보정 정책.
  - 값 범위: method별 policy 문자열 또는 boolean.
  - 조절 효과: 보정 정책은 p-value 안정성과 보수성에 영향을 준다.

## 33. KSWIN

적용 variant: KSWIN_STANDARD; KSWIN_WITH_SUBSAMPLING; KSWIN_NUMERIC_STREAM

사용 파라미터 수: 9

- `alpha`
  - 의미: 유의수준 또는 alarm 임계값.
  - 값 범위: 보통 0과 1 사이.
  - 조절 효과: 낮추면 보수적이고 false alarm이 줄지만 감지가 늦거나 약해지며, 높이면 민감해진다.
- `current_window`
  - 의미: 비교 기준/현재 데이터 구간.
  - 값 범위: timestamp range, window id, 또는 sample set.
  - 조절 효과: reference를 길게 잡으면 안정적이지만 최신 정상 상태를 덜 반영하고, current를 짧게 잡으면 빠르지만 noise가 커진다.
- `data_points`
  - 의미: 검정 또는 거리 계산에 들어가는 실제 표본/빈도/table.
  - 값 범위: 배열, count vector, contingency table.
  - 조절 효과: 표본 정의가 달라지면 결과가 달라지므로 filtering과 결측 처리 기준을 고정해야 한다.
- `input_signal`
  - 의미: detector에 넣는 값.
  - 값 범위: feature, score, error_rate, loss, embedding, SHAP 등.
  - 조절 효과: 같은 method라도 입력 신호가 달라지면 drift 해석이 달라진다.
- `reference_window`
  - 의미: 비교 기준/현재 데이터 구간.
  - 값 범위: timestamp range, window id, 또는 sample set.
  - 조절 효과: reference를 길게 잡으면 안정적이지만 최신 정상 상태를 덜 반영하고, current를 짧게 잡으면 빠르지만 noise가 커진다.
- `seed`
  - 의미: permutation/bootstrap/random projection의 반복 수와 재현성 seed.
  - 값 범위: 반복 수는 1 이상의 정수, seed는 정수.
  - 조절 효과: 반복 수가 많으면 안정적이지만 느리고, seed를 고정하면 재현 가능하다.
- `stat_size`
  - 의미: 계산에 사용하는 표본 또는 stream 길이.
  - 값 범위: 1 이상의 정수.
  - 조절 효과: 작으면 빠르고 민감하지만 noise가 크고, 크면 안정적이지만 detection delay가 늘어난다.
- `threshold_or_alpha`
  - 의미: 유의수준 또는 alarm 임계값.
  - 값 범위: 보통 0과 1 사이.
  - 조절 효과: 낮추면 보수적이고 false alarm이 줄지만 감지가 늦거나 약해지며, 높이면 민감해진다.
- `window_size`
  - 의미: 계산에 사용하는 표본 또는 stream 길이.
  - 값 범위: 1 이상의 정수.
  - 조절 효과: 작으면 빠르고 민감하지만 noise가 크고, 크면 안정적이지만 detection delay가 늘어난다.

## 34. Kuiper's Test

적용 variant: KUIPER_TWO_SAMPLE; KUIPER_CIRCULAR_DATA; KUIPER_ONE_SAMPLE

사용 파라미터 수: 7

- `alternative`
  - 의미: 양측/단측 또는 증가/감소 감시 방향.
  - 값 범위: two-sided, greater, less, up, down, both.
  - 조절 효과: 사전 방향성이 있으면 민감도를 높일 수 있지만, 사후 선택하면 해석이 왜곡된다.
- `circular_data_policy`
  - 의미: 해당 method variant의 세부 설정값.
  - 값 범위: 구현 문서에서 정의한 enum, 정수, 실수 또는 구조화 값.
  - 조절 효과: 값 변경 시 detector 민감도, 계산 비용, 비교 가능성이 달라질 수 있으므로 변경 이력을 기록한다.
- `current_window`
  - 의미: 비교 기준/현재 데이터 구간.
  - 값 범위: timestamp range, window id, 또는 sample set.
  - 조절 효과: reference를 길게 잡으면 안정적이지만 최신 정상 상태를 덜 반영하고, current를 짧게 잡으면 빠르지만 noise가 커진다.
- `input_signal`
  - 의미: detector에 넣는 값.
  - 값 범위: feature, score, error_rate, loss, embedding, SHAP 등.
  - 조절 효과: 같은 method라도 입력 신호가 달라지면 drift 해석이 달라진다.
- `p_value_method`
  - 의미: p-value 또는 검정 확률 계산 방식.
  - 값 범위: exact, asymptotic, permutation, bootstrap 등.
  - 조절 효과: exact는 작은 표본에서 정확하지만 느리고, asymptotic은 빠르지만 작은 표본에서 부정확할 수 있다.
- `reference_window`
  - 의미: 비교 기준/현재 데이터 구간.
  - 값 범위: timestamp range, window id, 또는 sample set.
  - 조절 효과: reference를 길게 잡으면 안정적이지만 최신 정상 상태를 덜 반영하고, current를 짧게 잡으면 빠르지만 noise가 커진다.
- `threshold_or_alpha`
  - 의미: 유의수준 또는 alarm 임계값.
  - 값 범위: 보통 0과 1 사이.
  - 조절 효과: 낮추면 보수적이고 false alarm이 줄지만 감지가 늦거나 약해지며, 높이면 민감해진다.

## 35. Levene's Test

적용 variant: LEVENE_MEAN_CENTER; BROWN_FORSYTHE_MEDIAN_CENTER; TRIMMED_MEAN_LEVENE

사용 파라미터 수: 8

- `alpha`
  - 의미: 유의수준 또는 alarm 임계값.
  - 값 범위: 보통 0과 1 사이.
  - 조절 효과: 낮추면 보수적이고 false alarm이 줄지만 감지가 늦거나 약해지며, 높이면 민감해진다.
- `alternative`
  - 의미: 양측/단측 또는 증가/감소 감시 방향.
  - 값 범위: two-sided, greater, less, up, down, both.
  - 조절 효과: 사전 방향성이 있으면 민감도를 높일 수 있지만, 사후 선택하면 해석이 왜곡된다.
- `center`
  - 의미: control chart 또는 variance test의 기준 중심/분산/허용 편차.
  - 값 범위: metric scale의 실수, proportion은 0과 0.5 사이.
  - 조절 효과: 기준 중심이 잘못되면 정상 변화도 drift로 보일 수 있다.
- `current_window`
  - 의미: 비교 기준/현재 데이터 구간.
  - 값 범위: timestamp range, window id, 또는 sample set.
  - 조절 효과: reference를 길게 잡으면 안정적이지만 최신 정상 상태를 덜 반영하고, current를 짧게 잡으면 빠르지만 noise가 커진다.
- `input_signal`
  - 의미: detector에 넣는 값.
  - 값 범위: feature, score, error_rate, loss, embedding, SHAP 등.
  - 조절 효과: 같은 method라도 입력 신호가 달라지면 drift 해석이 달라진다.
- `proportiontocut`
  - 의미: control chart 또는 variance test의 기준 중심/분산/허용 편차.
  - 값 범위: metric scale의 실수, proportion은 0과 0.5 사이.
  - 조절 효과: 기준 중심이 잘못되면 정상 변화도 drift로 보일 수 있다.
- `reference_window`
  - 의미: 비교 기준/현재 데이터 구간.
  - 값 범위: timestamp range, window id, 또는 sample set.
  - 조절 효과: reference를 길게 잡으면 안정적이지만 최신 정상 상태를 덜 반영하고, current를 짧게 잡으면 빠르지만 noise가 커진다.
- `threshold_or_alpha`
  - 의미: 유의수준 또는 alarm 임계값.
  - 값 범위: 보통 0과 1 사이.
  - 조절 효과: 낮추면 보수적이고 false alarm이 줄지만 감지가 늦거나 약해지며, 높이면 민감해진다.

## 36. L-Infinity Distance

적용 variant: CATEGORICAL_L_INFINITY; PROBABILITY_VECTOR_L_INFINITY; BINNED_NUMERIC_L_INFINITY

사용 파라미터 수: 8

- `category_set`
  - 의미: 검정 또는 거리 계산에 들어가는 실제 표본/빈도/table.
  - 값 범위: 배열, count vector, contingency table.
  - 조절 효과: 표본 정의가 달라지면 결과가 달라지므로 filtering과 결측 처리 기준을 고정해야 한다.
- `current_window`
  - 의미: 비교 기준/현재 데이터 구간.
  - 값 범위: timestamp range, window id, 또는 sample set.
  - 조절 효과: reference를 길게 잡으면 안정적이지만 최신 정상 상태를 덜 반영하고, current를 짧게 잡으면 빠르지만 noise가 커진다.
- `input_signal`
  - 의미: detector에 넣는 값.
  - 값 범위: feature, score, error_rate, loss, embedding, SHAP 등.
  - 조절 효과: 같은 method라도 입력 신호가 달라지면 drift 해석이 달라진다.
- `max_delta_threshold`
  - 의미: drift/warning 판정 민감도.
  - 값 범위: 보통 0과 1 사이 또는 detector 고유 threshold.
  - 조절 효과: drift 기준을 엄격하게 하면 오경보는 줄지만 놓칠 수 있고, 완화하면 더 자주 alarm이 난다.
- `normalization_policy`
  - 의미: feature, histogram, metric scale 정규화 방식.
  - 값 범위: none, standard, minmax, l2, probability 등.
  - 조절 효과: 정규화하면 feature 간 비교가 쉬워지지만 원 단위 해석은 약해진다.
- `reference_window`
  - 의미: 비교 기준/현재 데이터 구간.
  - 값 범위: timestamp range, window id, 또는 sample set.
  - 조절 효과: reference를 길게 잡으면 안정적이지만 최신 정상 상태를 덜 반영하고, current를 짧게 잡으면 빠르지만 noise가 커진다.
- `smoothing_epsilon`
  - 의미: zero probability 또는 희소 category 보정.
  - 값 범위: 0 이상의 작은 실수 또는 정책.
  - 조절 효과: 값을 키우면 안정적이지만 작은 category 변화가 희석된다.
- `threshold_or_alpha`
  - 의미: 유의수준 또는 alarm 임계값.
  - 값 범위: 보통 0과 1 사이.
  - 조절 효과: 낮추면 보수적이고 false alarm이 줄지만 감지가 늦거나 약해지며, 높이면 민감해진다.

## 37. LLM Query / Semantic Distance 기반 감지

적용 variant: QUERY_CENTROID_COSINE_SHIFT; TEXT_DOMAIN_CLASSIFIER_DRIFT; TOPIC_DISTRIBUTION_SHIFT

사용 파라미터 수: 12

- `cluster_count`
  - 의미: text/embedding/domain classifier 구성.
  - 값 범위: 모델명, 버전, split 비율, cluster 수.
  - 조절 효과: 모델이나 vectorizer가 바뀌면 drift처럼 보일 수 있으므로 버전 고정이 중요하다.
- `current_window`
  - 의미: 비교 기준/현재 데이터 구간.
  - 값 범위: timestamp range, window id, 또는 sample set.
  - 조절 효과: reference를 길게 잡으면 안정적이지만 최신 정상 상태를 덜 반영하고, current를 짧게 잡으면 빠르지만 noise가 커진다.
- `distance_method`
  - 의미: 거리 계산 방식.
  - 값 범위: Wasserstein, cosine, euclidean, JS, MMD 등.
  - 조절 효과: 어떤 차이에 민감한지가 달라지므로 데이터 형태에 맞춰 선택한다.
- `domain_classifier_model`
  - 의미: text/embedding/domain classifier 구성.
  - 값 범위: 모델명, 버전, split 비율, cluster 수.
  - 조절 효과: 모델이나 vectorizer가 바뀌면 drift처럼 보일 수 있으므로 버전 고정이 중요하다.
- `embedding_model`
  - 의미: text/embedding/domain classifier 구성.
  - 값 범위: 모델명, 버전, split 비율, cluster 수.
  - 조절 효과: 모델이나 vectorizer가 바뀌면 drift처럼 보일 수 있으므로 버전 고정이 중요하다.
- `embedding_version`
  - 의미: text/embedding/domain classifier 구성.
  - 값 범위: 모델명, 버전, split 비율, cluster 수.
  - 조절 효과: 모델이나 vectorizer가 바뀌면 drift처럼 보일 수 있으므로 버전 고정이 중요하다.
- `input_signal`
  - 의미: detector에 넣는 값.
  - 값 범위: feature, score, error_rate, loss, embedding, SHAP 등.
  - 조절 효과: 같은 method라도 입력 신호가 달라지면 drift 해석이 달라진다.
- `normalization_policy`
  - 의미: feature, histogram, metric scale 정규화 방식.
  - 값 범위: none, standard, minmax, l2, probability 등.
  - 조절 효과: 정규화하면 feature 간 비교가 쉬워지지만 원 단위 해석은 약해진다.
- `reference_window`
  - 의미: 비교 기준/현재 데이터 구간.
  - 값 범위: timestamp range, window id, 또는 sample set.
  - 조절 효과: reference를 길게 잡으면 안정적이지만 최신 정상 상태를 덜 반영하고, current를 짧게 잡으면 빠르지만 noise가 커진다.
- `roc_auc_threshold`
  - 의미: statistic, distance, score를 alarm으로 바꾸는 기준.
  - 값 범위: 측정값 scale에 따른 실수.
  - 조절 효과: 낮추면 민감도와 false alarm이 늘고, 높이면 안정적이지만 감지가 늦어진다.
- `threshold_or_alpha`
  - 의미: 유의수준 또는 alarm 임계값.
  - 값 범위: 보통 0과 1 사이.
  - 조절 효과: 낮추면 보수적이고 false alarm이 줄지만 감지가 늦거나 약해지며, 높이면 민감해진다.
- `topic_model`
  - 의미: text/embedding/domain classifier 구성.
  - 값 범위: 모델명, 버전, split 비율, cluster 수.
  - 조절 효과: 모델이나 vectorizer가 바뀌면 drift처럼 보일 수 있으므로 버전 고정이 중요하다.

## 38. LSDD

적용 variant: LEAST_SQUARES_DENSITY_DIFFERENCE; LSDD_WITH_PREPROCESSING; PERMUTATION_LSDD

사용 파라미터 수: 11

- `current_window`
  - 의미: 비교 기준/현재 데이터 구간.
  - 값 범위: timestamp range, window id, 또는 sample set.
  - 조절 효과: reference를 길게 잡으면 안정적이지만 최신 정상 상태를 덜 반영하고, current를 짧게 잡으면 빠르지만 noise가 커진다.
- `input_signal`
  - 의미: detector에 넣는 값.
  - 값 범위: feature, score, error_rate, loss, embedding, SHAP 등.
  - 조절 효과: 같은 method라도 입력 신호가 달라지면 drift 해석이 달라진다.
- `kernel`
  - 의미: kernel 기반 detector의 유사도 함수와 폭.
  - 값 범위: kernel은 rbf/linear 등, bandwidth/gamma는 양의 실수.
  - 조절 효과: bandwidth가 작으면 국소 차이에 민감하고, 크면 전역 차이에 민감하다.
- `kernel_bandwidth`
  - 의미: kernel 기반 detector의 유사도 함수와 폭.
  - 값 범위: kernel은 rbf/linear 등, bandwidth/gamma는 양의 실수.
  - 조절 효과: bandwidth가 작으면 국소 차이에 민감하고, 크면 전역 차이에 민감하다.
- `n_centers`
  - 의미: control chart 또는 variance test의 기준 중심/분산/허용 편차.
  - 값 범위: metric scale의 실수, proportion은 0과 0.5 사이.
  - 조절 효과: 기준 중심이 잘못되면 정상 변화도 drift로 보일 수 있다.
- `permutation_count`
  - 의미: permutation/bootstrap/random projection의 반복 수와 재현성 seed.
  - 값 범위: 반복 수는 1 이상의 정수, seed는 정수.
  - 조절 효과: 반복 수가 많으면 안정적이지만 느리고, seed를 고정하면 재현 가능하다.
- `preprocessing_fn`
  - 의미: feature map 또는 이미지 표현 추출 설정.
  - 값 범위: layer 이름, extractor 버전, preprocessing 함수.
  - 조절 효과: 추출 지점이나 전처리가 바뀌면 측정값 비교 가능성이 깨진다.
- `random_seed`
  - 의미: permutation/bootstrap/random projection의 반복 수와 재현성 seed.
  - 값 범위: 반복 수는 1 이상의 정수, seed는 정수.
  - 조절 효과: 반복 수가 많으면 안정적이지만 느리고, seed를 고정하면 재현 가능하다.
- `reference_window`
  - 의미: 비교 기준/현재 데이터 구간.
  - 값 범위: timestamp range, window id, 또는 sample set.
  - 조절 효과: reference를 길게 잡으면 안정적이지만 최신 정상 상태를 덜 반영하고, current를 짧게 잡으면 빠르지만 noise가 커진다.
- `regularization_lambda`
  - 의미: 해당 method variant의 세부 설정값.
  - 값 범위: 구현 문서에서 정의한 enum, 정수, 실수 또는 구조화 값.
  - 조절 효과: 값 변경 시 detector 민감도, 계산 비용, 비교 가능성이 달라질 수 있으므로 변경 이력을 기록한다.
- `threshold_or_alpha`
  - 의미: 유의수준 또는 alarm 임계값.
  - 값 범위: 보통 0과 1 사이.
  - 조절 효과: 낮추면 보수적이고 false alarm이 줄지만 감지가 늦거나 약해지며, 높이면 민감해진다.

## 39. Mahalanobis Distance

적용 variant: SAMPLE_MAHALANOBIS_OUTLIER; WINDOW_MEAN_MAHALANOBIS; ROBUST_MAHALANOBIS

사용 파라미터 수: 12

- `covariance_estimator`
  - 의미: 평균/공분산 기반 다변량 기준.
  - 값 범위: 벡터, 행렬, estimator 이름, 0 이상의 regularization 값.
  - 조절 효과: regularization과 robust estimator는 안정성을 높이지만 statistic scale을 바꾼다.
- `current_window`
  - 의미: 비교 기준/현재 데이터 구간.
  - 값 범위: timestamp range, window id, 또는 sample set.
  - 조절 효과: reference를 길게 잡으면 안정적이지만 최신 정상 상태를 덜 반영하고, current를 짧게 잡으면 빠르지만 noise가 커진다.
- `distance_threshold`
  - 의미: statistic, distance, score를 alarm으로 바꾸는 기준.
  - 값 범위: 측정값 scale에 따른 실수.
  - 조절 효과: 낮추면 민감도와 false alarm이 늘고, 높이면 안정적이지만 감지가 늦어진다.
- `input_signal`
  - 의미: detector에 넣는 값.
  - 값 범위: feature, score, error_rate, loss, embedding, SHAP 등.
  - 조절 효과: 같은 method라도 입력 신호가 달라지면 drift 해석이 달라진다.
- `mean_reference`
  - 의미: 평균/공분산 기반 다변량 기준.
  - 값 범위: 벡터, 행렬, estimator 이름, 0 이상의 regularization 값.
  - 조절 효과: regularization과 robust estimator는 안정성을 높이지만 statistic scale을 바꾼다.
- `reference_window`
  - 의미: 비교 기준/현재 데이터 구간.
  - 값 범위: timestamp range, window id, 또는 sample set.
  - 조절 효과: reference를 길게 잡으면 안정적이지만 최신 정상 상태를 덜 반영하고, current를 짧게 잡으면 빠르지만 noise가 커진다.
- `regularization_strength`
  - 의미: 평균/공분산 기반 다변량 기준.
  - 값 범위: 벡터, 행렬, estimator 이름, 0 이상의 regularization 값.
  - 조절 효과: regularization과 robust estimator는 안정성을 높이지만 statistic scale을 바꾼다.
- `robust_estimator`
  - 의미: 평균/공분산 기반 다변량 기준.
  - 값 범위: 벡터, 행렬, estimator 이름, 0 이상의 regularization 값.
  - 조절 효과: regularization과 robust estimator는 안정성을 높이지만 statistic scale을 바꾼다.
- `scaling_policy`
  - 의미: feature, histogram, metric scale 정규화 방식.
  - 값 범위: none, standard, minmax, l2, probability 등.
  - 조절 효과: 정규화하면 feature 간 비교가 쉬워지지만 원 단위 해석은 약해진다.
- `step_size`
  - 의미: 해당 method variant의 세부 설정값.
  - 값 범위: 구현 문서에서 정의한 enum, 정수, 실수 또는 구조화 값.
  - 조절 효과: 값 변경 시 detector 민감도, 계산 비용, 비교 가능성이 달라질 수 있으므로 변경 이력을 기록한다.
- `threshold_or_alpha`
  - 의미: 유의수준 또는 alarm 임계값.
  - 값 범위: 보통 0과 1 사이.
  - 조절 효과: 낮추면 보수적이고 false alarm이 줄지만 감지가 늦거나 약해지며, 높이면 민감해진다.
- `window_size`
  - 의미: 계산에 사용하는 표본 또는 stream 길이.
  - 값 범위: 1 이상의 정수.
  - 조절 효과: 작으면 빠르고 민감하지만 noise가 크고, 크면 안정적이지만 detection delay가 늘어난다.

## 40. Mann-Whitney U / Wilcoxon Rank Sum Test

적용 variant: MANN_WHITNEY_TWO_SIDED; MANN_WHITNEY_ONE_SIDED; MANN_WHITNEY_EXACT

사용 파라미터 수: 10

- `alternative`
  - 의미: 양측/단측 또는 증가/감소 감시 방향.
  - 값 범위: two-sided, greater, less, up, down, both.
  - 조절 효과: 사전 방향성이 있으면 민감도를 높일 수 있지만, 사후 선택하면 해석이 왜곡된다.
- `continuity_correction`
  - 의미: one-class/outlier detector 설정.
  - 값 범위: contamination/nu는 보통 0과 1 사이, estimator와 sample 수는 양의 정수.
  - 조절 효과: contamination을 높이면 outlier 허용이 커지고, estimator 수가 많으면 안정적이지만 느리다.
- `current_window`
  - 의미: 비교 기준/현재 데이터 구간.
  - 값 범위: timestamp range, window id, 또는 sample set.
  - 조절 효과: reference를 길게 잡으면 안정적이지만 최신 정상 상태를 덜 반영하고, current를 짧게 잡으면 빠르지만 noise가 커진다.
- `direction_or_alternative`
  - 의미: 양측/단측 또는 증가/감소 감시 방향.
  - 값 범위: two-sided, greater, less, up, down, both.
  - 조절 효과: 사전 방향성이 있으면 민감도를 높일 수 있지만, 사후 선택하면 해석이 왜곡된다.
- `exact_method`
  - 의미: p-value 또는 검정 확률 계산 방식.
  - 값 범위: exact, asymptotic, permutation, bootstrap 등.
  - 조절 효과: exact는 작은 표본에서 정확하지만 느리고, asymptotic은 빠르지만 작은 표본에서 부정확할 수 있다.
- `input_signal`
  - 의미: detector에 넣는 값.
  - 값 범위: feature, score, error_rate, loss, embedding, SHAP 등.
  - 조절 효과: 같은 method라도 입력 신호가 달라지면 drift 해석이 달라진다.
- `p_value_method`
  - 의미: p-value 또는 검정 확률 계산 방식.
  - 값 범위: exact, asymptotic, permutation, bootstrap 등.
  - 조절 효과: exact는 작은 표본에서 정확하지만 느리고, asymptotic은 빠르지만 작은 표본에서 부정확할 수 있다.
- `reference_window`
  - 의미: 비교 기준/현재 데이터 구간.
  - 값 범위: timestamp range, window id, 또는 sample set.
  - 조절 효과: reference를 길게 잡으면 안정적이지만 최신 정상 상태를 덜 반영하고, current를 짧게 잡으면 빠르지만 noise가 커진다.
- `threshold_or_alpha`
  - 의미: 유의수준 또는 alarm 임계값.
  - 값 범위: 보통 0과 1 사이.
  - 조절 효과: 낮추면 보수적이고 false alarm이 줄지만 감지가 늦거나 약해지며, 높이면 민감해진다.
- `tie_correction`
  - 의미: ties, continuity, missing value, small sample 보정 정책.
  - 값 범위: method별 policy 문자열 또는 boolean.
  - 조절 효과: 보정 정책은 p-value 안정성과 보수성에 영향을 준다.

## 41. MEWMA

적용 variant: MEWMA_STANDARD; MEWMA_WITH_MAHALANOBIS_D2

사용 파라미터 수: 10

- `control_limit`
  - 의미: statistic, distance, score를 alarm으로 바꾸는 기준.
  - 값 범위: 측정값 scale에 따른 실수.
  - 조절 효과: 낮추면 민감도와 false alarm이 늘고, 높이면 안정적이지만 감지가 늦어진다.
- `covariance_estimator`
  - 의미: 평균/공분산 기반 다변량 기준.
  - 값 범위: 벡터, 행렬, estimator 이름, 0 이상의 regularization 값.
  - 조절 효과: regularization과 robust estimator는 안정성을 높이지만 statistic scale을 바꾼다.
- `current_window`
  - 의미: 비교 기준/현재 데이터 구간.
  - 값 범위: timestamp range, window id, 또는 sample set.
  - 조절 효과: reference를 길게 잡으면 안정적이지만 최신 정상 상태를 덜 반영하고, current를 짧게 잡으면 빠르지만 noise가 커진다.
- `input_signal`
  - 의미: detector에 넣는 값.
  - 값 범위: feature, score, error_rate, loss, embedding, SHAP 등.
  - 조절 효과: 같은 method라도 입력 신호가 달라지면 drift 해석이 달라진다.
- `lambda`
  - 의미: EWMA/GMA/HDDM-W/ECDD 계열의 가중치 또는 smoothing factor.
  - 값 범위: 보통 0과 1 사이.
  - 조절 효과: 클수록 최근 값에 민감하고, 작을수록 완만하지만 감지가 늦다.
- `mean_vector_reference`
  - 의미: 평균/공분산 기반 다변량 기준.
  - 값 범위: 벡터, 행렬, estimator 이름, 0 이상의 regularization 값.
  - 조절 효과: regularization과 robust estimator는 안정성을 높이지만 statistic scale을 바꾼다.
- `metric_scaling_policy`
  - 의미: feature, histogram, metric scale 정규화 방식.
  - 값 범위: none, standard, minmax, l2, probability 등.
  - 조절 효과: 정규화하면 feature 간 비교가 쉬워지지만 원 단위 해석은 약해진다.
- `reference_window`
  - 의미: 비교 기준/현재 데이터 구간.
  - 값 범위: timestamp range, window id, 또는 sample set.
  - 조절 효과: reference를 길게 잡으면 안정적이지만 최신 정상 상태를 덜 반영하고, current를 짧게 잡으면 빠르지만 noise가 커진다.
- `regularization_strength`
  - 의미: 평균/공분산 기반 다변량 기준.
  - 값 범위: 벡터, 행렬, estimator 이름, 0 이상의 regularization 값.
  - 조절 효과: regularization과 robust estimator는 안정성을 높이지만 statistic scale을 바꾼다.
- `threshold_or_alpha`
  - 의미: 유의수준 또는 alarm 임계값.
  - 값 범위: 보통 0과 1 사이.
  - 조절 효과: 낮추면 보수적이고 false alarm이 줄지만 감지가 늦거나 약해지며, 높이면 민감해진다.

## 42. MMD

적용 variant: KERNEL_MMD_UNBIASED; KERNEL_MMD_BIASED; LINEAR_TIME_MMD; STREAMING_MMD

사용 파라미터 수: 12

- `current_window`
  - 의미: 비교 기준/현재 데이터 구간.
  - 값 범위: timestamp range, window id, 또는 sample set.
  - 조절 효과: reference를 길게 잡으면 안정적이지만 최신 정상 상태를 덜 반영하고, current를 짧게 잡으면 빠르지만 noise가 커진다.
- `input_signal`
  - 의미: detector에 넣는 값.
  - 값 범위: feature, score, error_rate, loss, embedding, SHAP 등.
  - 조절 효과: 같은 method라도 입력 신호가 달라지면 drift 해석이 달라진다.
- `kernel`
  - 의미: kernel 기반 detector의 유사도 함수와 폭.
  - 값 범위: kernel은 rbf/linear 등, bandwidth/gamma는 양의 실수.
  - 조절 효과: bandwidth가 작으면 국소 차이에 민감하고, 크면 전역 차이에 민감하다.
- `kernel_bandwidth`
  - 의미: kernel 기반 detector의 유사도 함수와 폭.
  - 값 범위: kernel은 rbf/linear 등, bandwidth/gamma는 양의 실수.
  - 조절 효과: bandwidth가 작으면 국소 차이에 민감하고, 크면 전역 차이에 민감하다.
- `linear_time_approximation`
  - 의미: 대용량/근사 계산 설정.
  - 값 범위: count는 양의 정수, error는 0 이상의 실수, policy는 문자열.
  - 조절 효과: 근사 오차와 계산 비용의 trade-off를 만든다.
- `p_value_method`
  - 의미: p-value 또는 검정 확률 계산 방식.
  - 값 범위: exact, asymptotic, permutation, bootstrap 등.
  - 조절 효과: exact는 작은 표본에서 정확하지만 느리고, asymptotic은 빠르지만 작은 표본에서 부정확할 수 있다.
- `permutation_count`
  - 의미: permutation/bootstrap/random projection의 반복 수와 재현성 seed.
  - 값 범위: 반복 수는 1 이상의 정수, seed는 정수.
  - 조절 효과: 반복 수가 많으면 안정적이지만 느리고, seed를 고정하면 재현 가능하다.
- `random_seed`
  - 의미: permutation/bootstrap/random projection의 반복 수와 재현성 seed.
  - 값 범위: 반복 수는 1 이상의 정수, seed는 정수.
  - 조절 효과: 반복 수가 많으면 안정적이지만 느리고, seed를 고정하면 재현 가능하다.
- `reference_window`
  - 의미: 비교 기준/현재 데이터 구간.
  - 값 범위: timestamp range, window id, 또는 sample set.
  - 조절 효과: reference를 길게 잡으면 안정적이지만 최신 정상 상태를 덜 반영하고, current를 짧게 잡으면 빠르지만 noise가 커진다.
- `threshold_or_alpha`
  - 의미: 유의수준 또는 alarm 임계값.
  - 값 범위: 보통 0과 1 사이.
  - 조절 효과: 낮추면 보수적이고 false alarm이 줄지만 감지가 늦거나 약해지며, 높이면 민감해진다.
- `update_frequency`
  - 의미: 대용량/근사 계산 설정.
  - 값 범위: count는 양의 정수, error는 0 이상의 실수, policy는 문자열.
  - 조절 효과: 근사 오차와 계산 비용의 trade-off를 만든다.
- `window_size`
  - 의미: 계산에 사용하는 표본 또는 stream 길이.
  - 값 범위: 1 이상의 정수.
  - 조절 효과: 작으면 빠르고 민감하지만 noise가 크고, 크면 안정적이지만 detection delay가 늘어난다.

## 43. Model Uncertainty Drift

적용 variant: SOFTMAX_CONFIDENCE_DRIFT; ENTROPY_DRIFT; PREDICTIVE_VARIANCE_DRIFT

사용 파라미터 수: 9

- `aggregation_window`
  - 의미: 계산에 사용하는 표본 또는 stream 길이.
  - 값 범위: 1 이상의 정수.
  - 조절 효과: 작으면 빠르고 민감하지만 noise가 크고, 크면 안정적이지만 detection delay가 늘어난다.
- `calibration_policy`
  - 의미: 해당 method variant의 세부 설정값.
  - 값 범위: 구현 문서에서 정의한 enum, 정수, 실수 또는 구조화 값.
  - 조절 효과: 값 변경 시 detector 민감도, 계산 비용, 비교 가능성이 달라질 수 있으므로 변경 이력을 기록한다.
- `confidence_threshold`
  - 의미: statistic, distance, score를 alarm으로 바꾸는 기준.
  - 값 범위: 측정값 scale에 따른 실수.
  - 조절 효과: 낮추면 민감도와 false alarm이 늘고, 높이면 안정적이지만 감지가 늦어진다.
- `current_window`
  - 의미: 비교 기준/현재 데이터 구간.
  - 값 범위: timestamp range, window id, 또는 sample set.
  - 조절 효과: reference를 길게 잡으면 안정적이지만 최신 정상 상태를 덜 반영하고, current를 짧게 잡으면 빠르지만 noise가 커진다.
- `entropy_base`
  - 의미: 해당 method variant의 세부 설정값.
  - 값 범위: 구현 문서에서 정의한 enum, 정수, 실수 또는 구조화 값.
  - 조절 효과: 값 변경 시 detector 민감도, 계산 비용, 비교 가능성이 달라질 수 있으므로 변경 이력을 기록한다.
- `input_signal`
  - 의미: detector에 넣는 값.
  - 값 범위: feature, score, error_rate, loss, embedding, SHAP 등.
  - 조절 효과: 같은 method라도 입력 신호가 달라지면 drift 해석이 달라진다.
- `reference_window`
  - 의미: 비교 기준/현재 데이터 구간.
  - 값 범위: timestamp range, window id, 또는 sample set.
  - 조절 효과: reference를 길게 잡으면 안정적이지만 최신 정상 상태를 덜 반영하고, current를 짧게 잡으면 빠르지만 noise가 커진다.
- `threshold_or_alpha`
  - 의미: 유의수준 또는 alarm 임계값.
  - 값 범위: 보통 0과 1 사이.
  - 조절 효과: 낮추면 보수적이고 false alarm이 줄지만 감지가 늦거나 약해지며, 높이면 민감해진다.
- `uncertainty_metric`
  - 의미: 해당 method variant의 세부 설정값.
  - 값 범위: 구현 문서에서 정의한 enum, 정수, 실수 또는 구조화 값.
  - 조절 효과: 값 변경 시 detector 민감도, 계산 비용, 비교 가능성이 달라질 수 있으므로 변경 이력을 기록한다.

## 44. OCDD

적용 variant: ONE_CLASS_SVM_DRIFT; ISOLATION_FOREST_DRIFT_SCORE; AUTOENCODER_RECONSTRUCTION_DRIFT

사용 파라미터 수: 20

- `anomaly_threshold`
  - 의미: statistic, distance, score를 alarm으로 바꾸는 기준.
  - 값 범위: 측정값 scale에 따른 실수.
  - 조절 효과: 낮추면 민감도와 false alarm이 늘고, 높이면 안정적이지만 감지가 늦어진다.
- `contamination`
  - 의미: one-class/outlier detector 설정.
  - 값 범위: contamination/nu는 보통 0과 1 사이, estimator와 sample 수는 양의 정수.
  - 조절 효과: contamination을 높이면 outlier 허용이 커지고, estimator 수가 많으면 안정적이지만 느리다.
- `current_window`
  - 의미: 비교 기준/현재 데이터 구간.
  - 값 범위: timestamp range, window id, 또는 sample set.
  - 조절 효과: reference를 길게 잡으면 안정적이지만 최신 정상 상태를 덜 반영하고, current를 짧게 잡으면 빠르지만 noise가 커진다.
- `gamma`
  - 의미: kernel 기반 detector의 유사도 함수와 폭.
  - 값 범위: kernel은 rbf/linear 등, bandwidth/gamma는 양의 실수.
  - 조절 효과: bandwidth가 작으면 국소 차이에 민감하고, 크면 전역 차이에 민감하다.
- `input_signal`
  - 의미: detector에 넣는 값.
  - 값 범위: feature, score, error_rate, loss, embedding, SHAP 등.
  - 조절 효과: 같은 method라도 입력 신호가 달라지면 drift 해석이 달라진다.
- `kernel`
  - 의미: kernel 기반 detector의 유사도 함수와 폭.
  - 값 범위: kernel은 rbf/linear 등, bandwidth/gamma는 양의 실수.
  - 조절 효과: bandwidth가 작으면 국소 차이에 민감하고, 크면 전역 차이에 민감하다.
- `latent_dim`
  - 의미: autoencoder/representation 모델 설정.
  - 값 범위: latent dimension과 epoch는 양의 정수, loss/optimizer는 이름.
  - 조절 효과: latent가 작으면 압축이 강하고, 크면 재구성은 쉬우나 drift 민감도가 약해질 수 있다.
- `max_features`
  - 의미: one-class/outlier detector 설정.
  - 값 범위: contamination/nu는 보통 0과 1 사이, estimator와 sample 수는 양의 정수.
  - 조절 효과: contamination을 높이면 outlier 허용이 커지고, estimator 수가 많으면 안정적이지만 느리다.
- `max_samples`
  - 의미: one-class/outlier detector 설정.
  - 값 범위: contamination/nu는 보통 0과 1 사이, estimator와 sample 수는 양의 정수.
  - 조절 효과: contamination을 높이면 outlier 허용이 커지고, estimator 수가 많으면 안정적이지만 느리다.
- `n_estimators`
  - 의미: one-class/outlier detector 설정.
  - 값 범위: contamination/nu는 보통 0과 1 사이, estimator와 sample 수는 양의 정수.
  - 조절 효과: contamination을 높이면 outlier 허용이 커지고, estimator 수가 많으면 안정적이지만 느리다.
- `normal_reference_window`
  - 의미: one-class/outlier detector 설정.
  - 값 범위: contamination/nu는 보통 0과 1 사이, estimator와 sample 수는 양의 정수.
  - 조절 효과: contamination을 높이면 outlier 허용이 커지고, estimator 수가 많으면 안정적이지만 느리다.
- `nu`
  - 의미: one-class/outlier detector 설정.
  - 값 범위: contamination/nu는 보통 0과 1 사이, estimator와 sample 수는 양의 정수.
  - 조절 효과: contamination을 높이면 outlier 허용이 커지고, estimator 수가 많으면 안정적이지만 느리다.
- `optimizer`
  - 의미: autoencoder/representation 모델 설정.
  - 값 범위: latent dimension과 epoch는 양의 정수, loss/optimizer는 이름.
  - 조절 효과: latent가 작으면 압축이 강하고, 크면 재구성은 쉬우나 drift 민감도가 약해질 수 있다.
- `random_seed`
  - 의미: permutation/bootstrap/random projection의 반복 수와 재현성 seed.
  - 값 범위: 반복 수는 1 이상의 정수, seed는 정수.
  - 조절 효과: 반복 수가 많으면 안정적이지만 느리고, seed를 고정하면 재현 가능하다.
- `reconstruction_loss`
  - 의미: autoencoder/representation 모델 설정.
  - 값 범위: latent dimension과 epoch는 양의 정수, loss/optimizer는 이름.
  - 조절 효과: latent가 작으면 압축이 강하고, 크면 재구성은 쉬우나 drift 민감도가 약해질 수 있다.
- `reconstruction_threshold`
  - 의미: statistic, distance, score를 alarm으로 바꾸는 기준.
  - 값 범위: 측정값 scale에 따른 실수.
  - 조절 효과: 낮추면 민감도와 false alarm이 늘고, 높이면 안정적이지만 감지가 늦어진다.
- `reference_window`
  - 의미: 비교 기준/현재 데이터 구간.
  - 값 범위: timestamp range, window id, 또는 sample set.
  - 조절 효과: reference를 길게 잡으면 안정적이지만 최신 정상 상태를 덜 반영하고, current를 짧게 잡으면 빠르지만 noise가 커진다.
- `scaling_policy`
  - 의미: feature, histogram, metric scale 정규화 방식.
  - 값 범위: none, standard, minmax, l2, probability 등.
  - 조절 효과: 정규화하면 feature 간 비교가 쉬워지지만 원 단위 해석은 약해진다.
- `threshold_or_alpha`
  - 의미: 유의수준 또는 alarm 임계값.
  - 값 범위: 보통 0과 1 사이.
  - 조절 효과: 낮추면 보수적이고 false alarm이 줄지만 감지가 늦거나 약해지며, 높이면 민감해진다.
- `training_epochs`
  - 의미: autoencoder/representation 모델 설정.
  - 값 범위: latent dimension과 epoch는 양의 정수, loss/optimizer는 이름.
  - 조절 효과: latent가 작으면 압축이 강하고, 크면 재구성은 쉬우나 drift 민감도가 약해질 수 있다.

## 45. Page-Hinkley Test

적용 variant: PAGE_HINKLEY_INCREASE; PAGE_HINKLEY_DECREASE

사용 파라미터 수: 10

- `alpha`
  - 의미: 유의수준 또는 alarm 임계값.
  - 값 범위: 보통 0과 1 사이.
  - 조절 효과: 낮추면 보수적이고 false alarm이 줄지만 감지가 늦거나 약해지며, 높이면 민감해진다.
- `current_window`
  - 의미: 비교 기준/현재 데이터 구간.
  - 값 범위: timestamp range, window id, 또는 sample set.
  - 조절 효과: reference를 길게 잡으면 안정적이지만 최신 정상 상태를 덜 반영하고, current를 짧게 잡으면 빠르지만 noise가 커진다.
- `delta`
  - 의미: drift/warning 판정 민감도.
  - 값 범위: 보통 0과 1 사이 또는 detector 고유 threshold.
  - 조절 효과: drift 기준을 엄격하게 하면 오경보는 줄지만 놓칠 수 있고, 완화하면 더 자주 alarm이 난다.
- `direction`
  - 의미: 양측/단측 또는 증가/감소 감시 방향.
  - 값 범위: two-sided, greater, less, up, down, both.
  - 조절 효과: 사전 방향성이 있으면 민감도를 높일 수 있지만, 사후 선택하면 해석이 왜곡된다.
- `input_signal`
  - 의미: detector에 넣는 값.
  - 값 범위: feature, score, error_rate, loss, embedding, SHAP 등.
  - 조절 효과: 같은 method라도 입력 신호가 달라지면 drift 해석이 달라진다.
- `min_instances`
  - 의미: 계산에 사용하는 표본 또는 stream 길이.
  - 값 범위: 1 이상의 정수.
  - 조절 효과: 작으면 빠르고 민감하지만 noise가 크고, 크면 안정적이지만 detection delay가 늘어난다.
- `reference_window`
  - 의미: 비교 기준/현재 데이터 구간.
  - 값 범위: timestamp range, window id, 또는 sample set.
  - 조절 효과: reference를 길게 잡으면 안정적이지만 최신 정상 상태를 덜 반영하고, current를 짧게 잡으면 빠르지만 noise가 커진다.
- `reset_policy`
  - 의미: streaming detector의 메모리, 업데이트 주기, reset/retention 정책.
  - 값 범위: count는 양의 정수, policy는 문자열.
  - 조절 효과: 메모리를 늘리면 안정적이나 느리고, reset을 자주 하면 빠르지만 기준이 자주 바뀐다.
- `threshold`
  - 의미: statistic, distance, score를 alarm으로 바꾸는 기준.
  - 값 범위: 측정값 scale에 따른 실수.
  - 조절 효과: 낮추면 민감도와 false alarm이 늘고, 높이면 안정적이지만 감지가 늦어진다.
- `threshold_or_alpha`
  - 의미: 유의수준 또는 alarm 임계값.
  - 값 범위: 보통 0과 1 사이.
  - 조절 효과: 낮추면 보수적이고 false alarm이 줄지만 감지가 늦거나 약해지며, 높이면 민감해진다.

## 46. PSI

적용 variant: NUMERIC_BINNED_PSI; CATEGORICAL_PSI; SCORE_BAND_PSI; POPULATION_WEIGHTED_PSI

사용 파라미터 수: 10

- `bin_count`
  - 의미: 연속값을 구간화하거나 category bin을 정하는 방식.
  - 값 범위: 정책 문자열, bin 개수는 양의 정수.
  - 조절 효과: bin이 많으면 세밀하지만 표본 부족에 취약하고, 적으면 안정적이지만 세부 변화를 놓친다.
- `bin_edges`
  - 의미: 연속값을 구간화하거나 category bin을 정하는 방식.
  - 값 범위: 정책 문자열, bin 개수는 양의 정수.
  - 조절 효과: bin이 많으면 세밀하지만 표본 부족에 취약하고, 적으면 안정적이지만 세부 변화를 놓친다.
- `binning_policy`
  - 의미: 연속값을 구간화하거나 category bin을 정하는 방식.
  - 값 범위: 정책 문자열, bin 개수는 양의 정수.
  - 조절 효과: bin이 많으면 세밀하지만 표본 부족에 취약하고, 적으면 안정적이지만 세부 변화를 놓친다.
- `current_window`
  - 의미: 비교 기준/현재 데이터 구간.
  - 값 범위: timestamp range, window id, 또는 sample set.
  - 조절 효과: reference를 길게 잡으면 안정적이지만 최신 정상 상태를 덜 반영하고, current를 짧게 잡으면 빠르지만 noise가 커진다.
- `expected_distribution`
  - 의미: 해당 method variant의 세부 설정값.
  - 값 범위: 구현 문서에서 정의한 enum, 정수, 실수 또는 구조화 값.
  - 조절 효과: 값 변경 시 detector 민감도, 계산 비용, 비교 가능성이 달라질 수 있으므로 변경 이력을 기록한다.
- `input_signal`
  - 의미: detector에 넣는 값.
  - 값 범위: feature, score, error_rate, loss, embedding, SHAP 등.
  - 조절 효과: 같은 method라도 입력 신호가 달라지면 drift 해석이 달라진다.
- `minimum_bin_count`
  - 의미: 연속값을 구간화하거나 category bin을 정하는 방식.
  - 값 범위: 정책 문자열, bin 개수는 양의 정수.
  - 조절 효과: bin이 많으면 세밀하지만 표본 부족에 취약하고, 적으면 안정적이지만 세부 변화를 놓친다.
- `psi_threshold`
  - 의미: statistic, distance, score를 alarm으로 바꾸는 기준.
  - 값 범위: 측정값 scale에 따른 실수.
  - 조절 효과: 낮추면 민감도와 false alarm이 늘고, 높이면 안정적이지만 감지가 늦어진다.
- `reference_window`
  - 의미: 비교 기준/현재 데이터 구간.
  - 값 범위: timestamp range, window id, 또는 sample set.
  - 조절 효과: reference를 길게 잡으면 안정적이지만 최신 정상 상태를 덜 반영하고, current를 짧게 잡으면 빠르지만 noise가 커진다.
- `threshold_or_alpha`
  - 의미: 유의수준 또는 alarm 임계값.
  - 값 범위: 보통 0과 1 사이.
  - 조절 효과: 낮추면 보수적이고 false alarm이 줄지만 감지가 늦거나 약해지며, 높이면 민감해진다.

## 47. RDDM

적용 variant: RDDM_STANDARD; RDDM_REACTIVE_RESET

사용 파라미터 수: 11

- `current_window`
  - 의미: 비교 기준/현재 데이터 구간.
  - 값 범위: timestamp range, window id, 또는 sample set.
  - 조절 효과: reference를 길게 잡으면 안정적이지만 최신 정상 상태를 덜 반영하고, current를 짧게 잡으면 빠르지만 noise가 커진다.
- `drift_level`
  - 의미: drift/warning 판정 민감도.
  - 값 범위: 보통 0과 1 사이 또는 detector 고유 threshold.
  - 조절 효과: drift 기준을 엄격하게 하면 오경보는 줄지만 놓칠 수 있고, 완화하면 더 자주 alarm이 난다.
- `input_signal`
  - 의미: detector에 넣는 값.
  - 값 범위: feature, score, error_rate, loss, embedding, SHAP 등.
  - 조절 효과: 같은 method라도 입력 신호가 달라지면 drift 해석이 달라진다.
- `max_concept_size`
  - 의미: streaming detector의 메모리, 업데이트 주기, reset/retention 정책.
  - 값 범위: count는 양의 정수, policy는 문자열.
  - 조절 효과: 메모리를 늘리면 안정적이나 느리고, reset을 자주 하면 빠르지만 기준이 자주 바뀐다.
- `min_concept_size`
  - 의미: streaming detector의 메모리, 업데이트 주기, reset/retention 정책.
  - 값 범위: count는 양의 정수, policy는 문자열.
  - 조절 효과: 메모리를 늘리면 안정적이나 느리고, reset을 자주 하면 빠르지만 기준이 자주 바뀐다.
- `min_num_instances`
  - 의미: 계산에 사용하는 표본 또는 stream 길이.
  - 값 범위: 1 이상의 정수.
  - 조절 효과: 작으면 빠르고 민감하지만 noise가 크고, 크면 안정적이지만 detection delay가 늘어난다.
- `reference_window`
  - 의미: 비교 기준/현재 데이터 구간.
  - 값 범위: timestamp range, window id, 또는 sample set.
  - 조절 효과: reference를 길게 잡으면 안정적이지만 최신 정상 상태를 덜 반영하고, current를 짧게 잡으면 빠르지만 noise가 커진다.
- `reset_policy`
  - 의미: streaming detector의 메모리, 업데이트 주기, reset/retention 정책.
  - 값 범위: count는 양의 정수, policy는 문자열.
  - 조절 효과: 메모리를 늘리면 안정적이나 느리고, reset을 자주 하면 빠르지만 기준이 자주 바뀐다.
- `retention_policy`
  - 의미: streaming detector의 메모리, 업데이트 주기, reset/retention 정책.
  - 값 범위: count는 양의 정수, policy는 문자열.
  - 조절 효과: 메모리를 늘리면 안정적이나 느리고, reset을 자주 하면 빠르지만 기준이 자주 바뀐다.
- `threshold_or_alpha`
  - 의미: 유의수준 또는 alarm 임계값.
  - 값 범위: 보통 0과 1 사이.
  - 조절 효과: 낮추면 보수적이고 false alarm이 줄지만 감지가 늦거나 약해지며, 높이면 민감해진다.
- `warning_level`
  - 의미: drift/warning 판정 민감도.
  - 값 범위: 보통 0과 1 사이 또는 detector 고유 threshold.
  - 조절 효과: drift 기준을 엄격하게 하면 오경보는 줄지만 놓칠 수 있고, 완화하면 더 자주 alarm이 난다.

## 48. SeqDrift

적용 variant: SEQDRIFT1; SEQDRIFT2

사용 파라미터 수: 10

- `block_size`
  - 의미: streaming detector의 메모리, 업데이트 주기, reset/retention 정책.
  - 값 범위: count는 양의 정수, policy는 문자열.
  - 조절 효과: 메모리를 늘리면 안정적이나 느리고, reset을 자주 하면 빠르지만 기준이 자주 바뀐다.
- `bound_type`
  - 의미: streaming detector의 메모리, 업데이트 주기, reset/retention 정책.
  - 값 범위: count는 양의 정수, policy는 문자열.
  - 조절 효과: 메모리를 늘리면 안정적이나 느리고, reset을 자주 하면 빠르지만 기준이 자주 바뀐다.
- `current_window`
  - 의미: 비교 기준/현재 데이터 구간.
  - 값 범위: timestamp range, window id, 또는 sample set.
  - 조절 효과: reference를 길게 잡으면 안정적이지만 최신 정상 상태를 덜 반영하고, current를 짧게 잡으면 빠르지만 noise가 커진다.
- `delta`
  - 의미: drift/warning 판정 민감도.
  - 값 범위: 보통 0과 1 사이 또는 detector 고유 threshold.
  - 조절 효과: drift 기준을 엄격하게 하면 오경보는 줄지만 놓칠 수 있고, 완화하면 더 자주 alarm이 난다.
- `input_signal`
  - 의미: detector에 넣는 값.
  - 값 범위: feature, score, error_rate, loss, embedding, SHAP 등.
  - 조절 효과: 같은 method라도 입력 신호가 달라지면 drift 해석이 달라진다.
- `random_seed`
  - 의미: permutation/bootstrap/random projection의 반복 수와 재현성 seed.
  - 값 범위: 반복 수는 1 이상의 정수, seed는 정수.
  - 조절 효과: 반복 수가 많으면 안정적이지만 느리고, seed를 고정하면 재현 가능하다.
- `reference_window`
  - 의미: 비교 기준/현재 데이터 구간.
  - 값 범위: timestamp range, window id, 또는 sample set.
  - 조절 효과: reference를 길게 잡으면 안정적이지만 최신 정상 상태를 덜 반영하고, current를 짧게 잡으면 빠르지만 noise가 커진다.
- `reservoir_size`
  - 의미: streaming detector의 메모리, 업데이트 주기, reset/retention 정책.
  - 값 범위: count는 양의 정수, policy는 문자열.
  - 조절 효과: 메모리를 늘리면 안정적이나 느리고, reset을 자주 하면 빠르지만 기준이 자주 바뀐다.
- `sampling_policy`
  - 의미: graph embedding drift 계산 단위와 sampling.
  - 값 범위: 모델명, node/graph level, sampling policy.
  - 조절 효과: node-level은 국소 변화에, graph-level은 전체 구조 변화에 더 가깝다.
- `threshold_or_alpha`
  - 의미: 유의수준 또는 alarm 임계값.
  - 값 범위: 보통 0과 1 사이.
  - 조절 효과: 낮추면 보수적이고 false alarm이 줄지만 감지가 늦거나 약해지며, 높이면 민감해진다.

## 49. SHAP Drift

적용 variant: SHAP_VALUE_DISTRIBUTION_TEST; GLOBAL_IMPORTANCE_RANK_SHIFT; CLASS_CONDITIONAL_SHAP_DRIFT

사용 파라미터 수: 11

- `aggregation_level`
  - 의미: 설명 기반 drift 계산 설정.
  - 값 범위: explainer 이름, background data, class label, top-k 정수.
  - 조절 효과: background와 explainer가 바뀌면 SHAP/importance 분포가 달라진다.
- `background_dataset`
  - 의미: 설명 기반 drift 계산 설정.
  - 값 범위: explainer 이름, background data, class label, top-k 정수.
  - 조절 효과: background와 explainer가 바뀌면 SHAP/importance 분포가 달라진다.
- `class_label`
  - 의미: 설명 기반 drift 계산 설정.
  - 값 범위: explainer 이름, background data, class label, top-k 정수.
  - 조절 효과: background와 explainer가 바뀌면 SHAP/importance 분포가 달라진다.
- `current_window`
  - 의미: 비교 기준/현재 데이터 구간.
  - 값 범위: timestamp range, window id, 또는 sample set.
  - 조절 효과: reference를 길게 잡으면 안정적이지만 최신 정상 상태를 덜 반영하고, current를 짧게 잡으면 빠르지만 noise가 커진다.
- `distance_method`
  - 의미: 거리 계산 방식.
  - 값 범위: Wasserstein, cosine, euclidean, JS, MMD 등.
  - 조절 효과: 어떤 차이에 민감한지가 달라지므로 데이터 형태에 맞춰 선택한다.
- `explainer_type`
  - 의미: 설명 기반 drift 계산 설정.
  - 값 범위: explainer 이름, background data, class label, top-k 정수.
  - 조절 효과: background와 explainer가 바뀌면 SHAP/importance 분포가 달라진다.
- `input_signal`
  - 의미: detector에 넣는 값.
  - 값 범위: feature, score, error_rate, loss, embedding, SHAP 등.
  - 조절 효과: 같은 method라도 입력 신호가 달라지면 drift 해석이 달라진다.
- `reference_window`
  - 의미: 비교 기준/현재 데이터 구간.
  - 값 범위: timestamp range, window id, 또는 sample set.
  - 조절 효과: reference를 길게 잡으면 안정적이지만 최신 정상 상태를 덜 반영하고, current를 짧게 잡으면 빠르지만 noise가 커진다.
- `shap_value_type`
  - 의미: 설명 기반 drift 계산 설정.
  - 값 범위: explainer 이름, background data, class label, top-k 정수.
  - 조절 효과: background와 explainer가 바뀌면 SHAP/importance 분포가 달라진다.
- `threshold_or_alpha`
  - 의미: 유의수준 또는 alarm 임계값.
  - 값 범위: 보통 0과 1 사이.
  - 조절 효과: 낮추면 보수적이고 false alarm이 줄지만 감지가 늦거나 약해지며, 높이면 민감해진다.
- `top_k_features`
  - 의미: 설명 기반 drift 계산 설정.
  - 값 범위: explainer 이름, background data, class label, top-k 정수.
  - 조절 효과: background와 explainer가 바뀌면 SHAP/importance 분포가 달라진다.

## 50. SPRT

적용 variant: SPRT_BERNOULLI_ERROR_RATE; SPRT_GAUSSIAN_MEAN_SHIFT

사용 파라미터 수: 11

- `alpha`
  - 의미: 유의수준 또는 alarm 임계값.
  - 값 범위: 보통 0과 1 사이.
  - 조절 효과: 낮추면 보수적이고 false alarm이 줄지만 감지가 늦거나 약해지며, 높이면 민감해진다.
- `alternative_hypothesis`
  - 의미: 양측/단측 또는 증가/감소 감시 방향.
  - 값 범위: two-sided, greater, less, up, down, both.
  - 조절 효과: 사전 방향성이 있으면 민감도를 높일 수 있지만, 사후 선택하면 해석이 왜곡된다.
- `beta`
  - 의미: 해당 method variant의 세부 설정값.
  - 값 범위: 구현 문서에서 정의한 enum, 정수, 실수 또는 구조화 값.
  - 조절 효과: 값 변경 시 detector 민감도, 계산 비용, 비교 가능성이 달라질 수 있으므로 변경 이력을 기록한다.
- `current_window`
  - 의미: 비교 기준/현재 데이터 구간.
  - 값 범위: timestamp range, window id, 또는 sample set.
  - 조절 효과: reference를 길게 잡으면 안정적이지만 최신 정상 상태를 덜 반영하고, current를 짧게 잡으면 빠르지만 noise가 커진다.
- `decision_boundaries`
  - 의미: statistic, distance, score를 alarm으로 바꾸는 기준.
  - 값 범위: 측정값 scale에 따른 실수.
  - 조절 효과: 낮추면 민감도와 false alarm이 늘고, 높이면 안정적이지만 감지가 늦어진다.
- `effect_size`
  - 의미: 통계 모델, 분포 가정, 가설 정의.
  - 값 범위: method별 분포명, 파라미터, H0/H1 정의.
  - 조절 효과: 가정이 바뀌면 p-value와 alarm 의미가 바뀐다.
- `input_signal`
  - 의미: detector에 넣는 값.
  - 값 범위: feature, score, error_rate, loss, embedding, SHAP 등.
  - 조절 효과: 같은 method라도 입력 신호가 달라지면 drift 해석이 달라진다.
- `likelihood_model`
  - 의미: 통계 모델, 분포 가정, 가설 정의.
  - 값 범위: method별 분포명, 파라미터, H0/H1 정의.
  - 조절 효과: 가정이 바뀌면 p-value와 alarm 의미가 바뀐다.
- `null_hypothesis`
  - 의미: 통계 모델, 분포 가정, 가설 정의.
  - 값 범위: method별 분포명, 파라미터, H0/H1 정의.
  - 조절 효과: 가정이 바뀌면 p-value와 alarm 의미가 바뀐다.
- `reference_window`
  - 의미: 비교 기준/현재 데이터 구간.
  - 값 범위: timestamp range, window id, 또는 sample set.
  - 조절 효과: reference를 길게 잡으면 안정적이지만 최신 정상 상태를 덜 반영하고, current를 짧게 잡으면 빠르지만 noise가 커진다.
- `threshold_or_alpha`
  - 의미: 유의수준 또는 alarm 임계값.
  - 값 범위: 보통 0과 1 사이.
  - 조절 효과: 낮추면 보수적이고 false alarm이 줄지만 감지가 늦거나 약해지며, 높이면 민감해진다.

## 51. STEPD

적용 variant: STEPD_ACCURACY_WINDOW; STEPD_WARNING_DRIFT; STEPD_SUPERVISED_STREAM

사용 파라미터 수: 10

- `accuracy_definition`
  - 의미: supervised error/performance stream 정의.
  - 값 범위: label 지연 처리 정책, 오류 정의, accuracy 계산 방식.
  - 조절 효과: label 처리 방식이 바뀌면 concept/performance drift 해석이 달라진다.
- `alpha_drift`
  - 의미: drift/warning 판정 민감도.
  - 값 범위: 보통 0과 1 사이 또는 detector 고유 threshold.
  - 조절 효과: drift 기준을 엄격하게 하면 오경보는 줄지만 놓칠 수 있고, 완화하면 더 자주 alarm이 난다.
- `alpha_warning`
  - 의미: drift/warning 판정 민감도.
  - 값 범위: 보통 0과 1 사이 또는 detector 고유 threshold.
  - 조절 효과: drift 기준을 엄격하게 하면 오경보는 줄지만 놓칠 수 있고, 완화하면 더 자주 alarm이 난다.
- `current_window`
  - 의미: 비교 기준/현재 데이터 구간.
  - 값 범위: timestamp range, window id, 또는 sample set.
  - 조절 효과: reference를 길게 잡으면 안정적이지만 최신 정상 상태를 덜 반영하고, current를 짧게 잡으면 빠르지만 noise가 커진다.
- `input_signal`
  - 의미: detector에 넣는 값.
  - 값 범위: feature, score, error_rate, loss, embedding, SHAP 등.
  - 조절 효과: 같은 method라도 입력 신호가 달라지면 drift 해석이 달라진다.
- `min_instances`
  - 의미: 계산에 사용하는 표본 또는 stream 길이.
  - 값 범위: 1 이상의 정수.
  - 조절 효과: 작으면 빠르고 민감하지만 noise가 크고, 크면 안정적이지만 detection delay가 늘어난다.
- `reference_window`
  - 의미: 비교 기준/현재 데이터 구간.
  - 값 범위: timestamp range, window id, 또는 sample set.
  - 조절 효과: reference를 길게 잡으면 안정적이지만 최신 정상 상태를 덜 반영하고, current를 짧게 잡으면 빠르지만 noise가 커진다.
- `step_size`
  - 의미: 해당 method variant의 세부 설정값.
  - 값 범위: 구현 문서에서 정의한 enum, 정수, 실수 또는 구조화 값.
  - 조절 효과: 값 변경 시 detector 민감도, 계산 비용, 비교 가능성이 달라질 수 있으므로 변경 이력을 기록한다.
- `threshold_or_alpha`
  - 의미: 유의수준 또는 alarm 임계값.
  - 값 범위: 보통 0과 1 사이.
  - 조절 효과: 낮추면 보수적이고 false alarm이 줄지만 감지가 늦거나 약해지며, 높이면 민감해진다.
- `window_size`
  - 의미: 계산에 사용하는 표본 또는 stream 길이.
  - 값 범위: 1 이상의 정수.
  - 조절 효과: 작으면 빠르고 민감하지만 noise가 크고, 크면 안정적이지만 detection delay가 늘어난다.

## 52. Text Domain Classifier Drift

적용 variant: TEXT_DOMAIN_CLASSIFIER_ROC_AUC; TEXT_DOMAIN_CLASSIFIER_STAT_TEST; TEXT_DESCRIPTOR_DRIFT

사용 파라미터 수: 11

- `classifier_model`
  - 의미: text/embedding/domain classifier 구성.
  - 값 범위: 모델명, 버전, split 비율, cluster 수.
  - 조절 효과: 모델이나 vectorizer가 바뀌면 drift처럼 보일 수 있으므로 버전 고정이 중요하다.
- `current_window`
  - 의미: 비교 기준/현재 데이터 구간.
  - 값 범위: timestamp range, window id, 또는 sample set.
  - 조절 효과: reference를 길게 잡으면 안정적이지만 최신 정상 상태를 덜 반영하고, current를 짧게 잡으면 빠르지만 noise가 커진다.
- `embedding_model`
  - 의미: text/embedding/domain classifier 구성.
  - 값 범위: 모델명, 버전, split 비율, cluster 수.
  - 조절 효과: 모델이나 vectorizer가 바뀌면 drift처럼 보일 수 있으므로 버전 고정이 중요하다.
- `input_signal`
  - 의미: detector에 넣는 값.
  - 값 범위: feature, score, error_rate, loss, embedding, SHAP 등.
  - 조절 효과: 같은 method라도 입력 신호가 달라지면 drift 해석이 달라진다.
- `random_seed`
  - 의미: permutation/bootstrap/random projection의 반복 수와 재현성 seed.
  - 값 범위: 반복 수는 1 이상의 정수, seed는 정수.
  - 조절 효과: 반복 수가 많으면 안정적이지만 느리고, seed를 고정하면 재현 가능하다.
- `reference_window`
  - 의미: 비교 기준/현재 데이터 구간.
  - 값 범위: timestamp range, window id, 또는 sample set.
  - 조절 효과: reference를 길게 잡으면 안정적이지만 최신 정상 상태를 덜 반영하고, current를 짧게 잡으면 빠르지만 noise가 커진다.
- `roc_auc_threshold`
  - 의미: statistic, distance, score를 alarm으로 바꾸는 기준.
  - 값 범위: 측정값 scale에 따른 실수.
  - 조절 효과: 낮추면 민감도와 false alarm이 늘고, 높이면 안정적이지만 감지가 늦어진다.
- `statistical_test_alpha`
  - 의미: 유의수준 또는 alarm 임계값.
  - 값 범위: 보통 0과 1 사이.
  - 조절 효과: 낮추면 보수적이고 false alarm이 줄지만 감지가 늦거나 약해지며, 높이면 민감해진다.
- `text_vectorizer`
  - 의미: text/embedding/domain classifier 구성.
  - 값 범위: 모델명, 버전, split 비율, cluster 수.
  - 조절 효과: 모델이나 vectorizer가 바뀌면 drift처럼 보일 수 있으므로 버전 고정이 중요하다.
- `threshold_or_alpha`
  - 의미: 유의수준 또는 alarm 임계값.
  - 값 범위: 보통 0과 1 사이.
  - 조절 효과: 낮추면 보수적이고 false alarm이 줄지만 감지가 늦거나 약해지며, 높이면 민감해진다.
- `validation_split`
  - 의미: text/embedding/domain classifier 구성.
  - 값 범위: 모델명, 버전, split 비율, cluster 수.
  - 조절 효과: 모델이나 vectorizer가 바뀌면 drift처럼 보일 수 있으므로 버전 고정이 중요하다.

## 53. Total Variation Distance

적용 variant: CATEGORICAL_TOTAL_VARIATION; HISTOGRAM_TOTAL_VARIATION; PROBABILITY_VECTOR_TOTAL_VARIATION

사용 파라미터 수: 7

- `category_set`
  - 의미: 검정 또는 거리 계산에 들어가는 실제 표본/빈도/table.
  - 값 범위: 배열, count vector, contingency table.
  - 조절 효과: 표본 정의가 달라지면 결과가 달라지므로 filtering과 결측 처리 기준을 고정해야 한다.
- `current_window`
  - 의미: 비교 기준/현재 데이터 구간.
  - 값 범위: timestamp range, window id, 또는 sample set.
  - 조절 효과: reference를 길게 잡으면 안정적이지만 최신 정상 상태를 덜 반영하고, current를 짧게 잡으면 빠르지만 noise가 커진다.
- `input_signal`
  - 의미: detector에 넣는 값.
  - 값 범위: feature, score, error_rate, loss, embedding, SHAP 등.
  - 조절 효과: 같은 method라도 입력 신호가 달라지면 drift 해석이 달라진다.
- `normalization_policy`
  - 의미: feature, histogram, metric scale 정규화 방식.
  - 값 범위: none, standard, minmax, l2, probability 등.
  - 조절 효과: 정규화하면 feature 간 비교가 쉬워지지만 원 단위 해석은 약해진다.
- `reference_window`
  - 의미: 비교 기준/현재 데이터 구간.
  - 값 범위: timestamp range, window id, 또는 sample set.
  - 조절 효과: reference를 길게 잡으면 안정적이지만 최신 정상 상태를 덜 반영하고, current를 짧게 잡으면 빠르지만 noise가 커진다.
- `smoothing_epsilon`
  - 의미: zero probability 또는 희소 category 보정.
  - 값 범위: 0 이상의 작은 실수 또는 정책.
  - 조절 효과: 값을 키우면 안정적이지만 작은 category 변화가 희석된다.
- `threshold_or_alpha`
  - 의미: 유의수준 또는 alarm 임계값.
  - 값 범위: 보통 0과 1 사이.
  - 조절 효과: 낮추면 보수적이고 false alarm이 줄지만 감지가 늦거나 약해지며, 높이면 민감해진다.

## 54. Tree Feature 기반 감지

적용 variant: TIME_FEATURE_SPLIT_DETECTOR; DOMAIN_CLASSIFIER_TREE

사용 파라미터 수: 12

- `current_window`
  - 의미: 비교 기준/현재 데이터 구간.
  - 값 범위: timestamp range, window id, 또는 sample set.
  - 조절 효과: reference를 길게 잡으면 안정적이지만 최신 정상 상태를 덜 반영하고, current를 짧게 잡으면 빠르지만 noise가 커진다.
- `domain_label_definition`
  - 의미: tree 기반 감지 모델과 시간/domain label 정의.
  - 값 범위: 모델명, depth 정수, leaf 최소 표본 수, feature 이름.
  - 조절 효과: 깊은 tree는 민감하지만 과적합 위험이 크고, 얕은 tree는 안정적이지만 세부 drift를 놓친다.
- `feature_importance_method`
  - 의미: 설명 기반 drift 계산 설정.
  - 값 범위: explainer 이름, background data, class label, top-k 정수.
  - 조절 효과: background와 explainer가 바뀌면 SHAP/importance 분포가 달라진다.
- `input_signal`
  - 의미: detector에 넣는 값.
  - 값 범위: feature, score, error_rate, loss, embedding, SHAP 등.
  - 조절 효과: 같은 method라도 입력 신호가 달라지면 drift 해석이 달라진다.
- `max_depth`
  - 의미: tree 기반 감지 모델과 시간/domain label 정의.
  - 값 범위: 모델명, depth 정수, leaf 최소 표본 수, feature 이름.
  - 조절 효과: 깊은 tree는 민감하지만 과적합 위험이 크고, 얕은 tree는 안정적이지만 세부 drift를 놓친다.
- `min_samples_leaf`
  - 의미: tree 기반 감지 모델과 시간/domain label 정의.
  - 값 범위: 모델명, depth 정수, leaf 최소 표본 수, feature 이름.
  - 조절 효과: 깊은 tree는 민감하지만 과적합 위험이 크고, 얕은 tree는 안정적이지만 세부 drift를 놓친다.
- `random_seed`
  - 의미: permutation/bootstrap/random projection의 반복 수와 재현성 seed.
  - 값 범위: 반복 수는 1 이상의 정수, seed는 정수.
  - 조절 효과: 반복 수가 많으면 안정적이지만 느리고, seed를 고정하면 재현 가능하다.
- `reference_window`
  - 의미: 비교 기준/현재 데이터 구간.
  - 값 범위: timestamp range, window id, 또는 sample set.
  - 조절 효과: reference를 길게 잡으면 안정적이지만 최신 정상 상태를 덜 반영하고, current를 짧게 잡으면 빠르지만 noise가 커진다.
- `threshold_or_alpha`
  - 의미: 유의수준 또는 alarm 임계값.
  - 값 범위: 보통 0과 1 사이.
  - 조절 효과: 낮추면 보수적이고 false alarm이 줄지만 감지가 늦거나 약해지며, 높이면 민감해진다.
- `time_feature_name`
  - 의미: tree 기반 감지 모델과 시간/domain label 정의.
  - 값 범위: 모델명, depth 정수, leaf 최소 표본 수, feature 이름.
  - 조절 효과: 깊은 tree는 민감하지만 과적합 위험이 크고, 얕은 tree는 안정적이지만 세부 drift를 놓친다.
- `tree_model`
  - 의미: tree 기반 감지 모델과 시간/domain label 정의.
  - 값 범위: 모델명, depth 정수, leaf 최소 표본 수, feature 이름.
  - 조절 효과: 깊은 tree는 민감하지만 과적합 위험이 크고, 얕은 tree는 안정적이지만 세부 drift를 놓친다.
- `validation_split`
  - 의미: text/embedding/domain classifier 구성.
  - 값 범위: 모델명, 버전, split 비율, cluster 수.
  - 조절 효과: 모델이나 vectorizer가 바뀌면 drift처럼 보일 수 있으므로 버전 고정이 중요하다.

## 55. t-test 계열

적용 variant: ONE_SAMPLE_T_TEST; TWO_SAMPLE_STUDENT_T_TEST; WELCH_T_TEST; PAIRED_T_TEST

사용 파라미터 수: 10

- `alternative`
  - 의미: 양측/단측 또는 증가/감소 감시 방향.
  - 값 범위: two-sided, greater, less, up, down, both.
  - 조절 효과: 사전 방향성이 있으면 민감도를 높일 수 있지만, 사후 선택하면 해석이 왜곡된다.
- `confidence_level`
  - 의미: 해당 method variant의 세부 설정값.
  - 값 범위: 구현 문서에서 정의한 enum, 정수, 실수 또는 구조화 값.
  - 조절 효과: 값 변경 시 detector 민감도, 계산 비용, 비교 가능성이 달라질 수 있으므로 변경 이력을 기록한다.
- `current_window`
  - 의미: 비교 기준/현재 데이터 구간.
  - 값 범위: timestamp range, window id, 또는 sample set.
  - 조절 효과: reference를 길게 잡으면 안정적이지만 최신 정상 상태를 덜 반영하고, current를 짧게 잡으면 빠르지만 noise가 커진다.
- `equal_var`
  - 의미: 해당 method variant의 세부 설정값.
  - 값 범위: 구현 문서에서 정의한 enum, 정수, 실수 또는 구조화 값.
  - 조절 효과: 값 변경 시 detector 민감도, 계산 비용, 비교 가능성이 달라질 수 있으므로 변경 이력을 기록한다.
- `input_signal`
  - 의미: detector에 넣는 값.
  - 값 범위: feature, score, error_rate, loss, embedding, SHAP 등.
  - 조절 효과: 같은 method라도 입력 신호가 달라지면 drift 해석이 달라진다.
- `multiple_testing_correction`
  - 의미: ties, continuity, missing value, small sample 보정 정책.
  - 값 범위: method별 policy 문자열 또는 boolean.
  - 조절 효과: 보정 정책은 p-value 안정성과 보수성에 영향을 준다.
- `nan_policy`
  - 의미: ties, continuity, missing value, small sample 보정 정책.
  - 값 범위: method별 policy 문자열 또는 boolean.
  - 조절 효과: 보정 정책은 p-value 안정성과 보수성에 영향을 준다.
- `paired`
  - 의미: 해당 method variant의 세부 설정값.
  - 값 범위: 구현 문서에서 정의한 enum, 정수, 실수 또는 구조화 값.
  - 조절 효과: 값 변경 시 detector 민감도, 계산 비용, 비교 가능성이 달라질 수 있으므로 변경 이력을 기록한다.
- `reference_window`
  - 의미: 비교 기준/현재 데이터 구간.
  - 값 범위: timestamp range, window id, 또는 sample set.
  - 조절 효과: reference를 길게 잡으면 안정적이지만 최신 정상 상태를 덜 반영하고, current를 짧게 잡으면 빠르지만 noise가 커진다.
- `threshold_or_alpha`
  - 의미: 유의수준 또는 alarm 임계값.
  - 값 범위: 보통 0과 1 사이.
  - 조절 효과: 낮추면 보수적이고 false alarm이 줄지만 감지가 늦거나 약해지며, 높이면 민감해진다.

## 56. Wasserstein Distance

적용 variant: WASSERSTEIN_1D_EXACT; WASSERSTEIN_WINDOW_TREND; SLICED_WASSERSTEIN_EMBEDDING; WASSERSTEIN_APPROX_HISTOGRAM

사용 파라미터 수: 20

- `bin_count`
  - 의미: 연속값을 구간화하거나 category bin을 정하는 방식.
  - 값 범위: 정책 문자열, bin 개수는 양의 정수.
  - 조절 효과: bin이 많으면 세밀하지만 표본 부족에 취약하고, 적으면 안정적이지만 세부 변화를 놓친다.
- `bin_edges`
  - 의미: 연속값을 구간화하거나 category bin을 정하는 방식.
  - 값 범위: 정책 문자열, bin 개수는 양의 정수.
  - 조절 효과: bin이 많으면 세밀하지만 표본 부족에 취약하고, 적으면 안정적이지만 세부 변화를 놓친다.
- `binning_policy`
  - 의미: 연속값을 구간화하거나 category bin을 정하는 방식.
  - 값 범위: 정책 문자열, bin 개수는 양의 정수.
  - 조절 효과: bin이 많으면 세밀하지만 표본 부족에 취약하고, 적으면 안정적이지만 세부 변화를 놓친다.
- `current_window`
  - 의미: 비교 기준/현재 데이터 구간.
  - 값 범위: timestamp range, window id, 또는 sample set.
  - 조절 효과: reference를 길게 잡으면 안정적이지만 최신 정상 상태를 덜 반영하고, current를 짧게 잡으면 빠르지만 noise가 커진다.
- `distance_order`
  - 의미: 거리 계산 방식.
  - 값 범위: Wasserstein, cosine, euclidean, JS, MMD 등.
  - 조절 효과: 어떤 차이에 민감한지가 달라지므로 데이터 형태에 맞춰 선택한다.
- `exact_method`
  - 의미: p-value 또는 검정 확률 계산 방식.
  - 값 범위: exact, asymptotic, permutation, bootstrap 등.
  - 조절 효과: exact는 작은 표본에서 정확하지만 느리고, asymptotic은 빠르지만 작은 표본에서 부정확할 수 있다.
- `input_signal`
  - 의미: detector에 넣는 값.
  - 값 범위: feature, score, error_rate, loss, embedding, SHAP 등.
  - 조절 효과: 같은 method라도 입력 신호가 달라지면 drift 해석이 달라진다.
- `normalization_policy`
  - 의미: feature, histogram, metric scale 정규화 방식.
  - 값 범위: none, standard, minmax, l2, probability 등.
  - 조절 효과: 정규화하면 feature 간 비교가 쉬워지지만 원 단위 해석은 약해진다.
- `outlier_policy`
  - 의미: 표본 가중치와 outlier 처리 방식.
  - 값 범위: weight vector, winsorize/remove/keep 정책.
  - 조절 효과: 가중치와 outlier 처리가 distance와 ranking을 크게 바꿀 수 있다.
- `projection_count`
  - 의미: 대용량/근사 계산 설정.
  - 값 범위: count는 양의 정수, error는 0 이상의 실수, policy는 문자열.
  - 조절 효과: 근사 오차와 계산 비용의 trade-off를 만든다.
- `projection_distribution`
  - 의미: 대용량/근사 계산 설정.
  - 값 범위: count는 양의 정수, error는 0 이상의 실수, policy는 문자열.
  - 조절 효과: 근사 오차와 계산 비용의 trade-off를 만든다.
- `quantile_error`
  - 의미: 대용량/근사 계산 설정.
  - 값 범위: count는 양의 정수, error는 0 이상의 실수, policy는 문자열.
  - 조절 효과: 근사 오차와 계산 비용의 trade-off를 만든다.
- `random_seed`
  - 의미: permutation/bootstrap/random projection의 반복 수와 재현성 seed.
  - 값 범위: 반복 수는 1 이상의 정수, seed는 정수.
  - 조절 효과: 반복 수가 많으면 안정적이지만 느리고, seed를 고정하면 재현 가능하다.
- `reference_window`
  - 의미: 비교 기준/현재 데이터 구간.
  - 값 범위: timestamp range, window id, 또는 sample set.
  - 조절 효과: reference를 길게 잡으면 안정적이지만 최신 정상 상태를 덜 반영하고, current를 짧게 잡으면 빠르지만 noise가 커진다.
- `sample_weights_current`
  - 의미: 표본 가중치와 outlier 처리 방식.
  - 값 범위: weight vector, winsorize/remove/keep 정책.
  - 조절 효과: 가중치와 outlier 처리가 distance와 ranking을 크게 바꿀 수 있다.
- `sample_weights_reference`
  - 의미: 표본 가중치와 outlier 처리 방식.
  - 값 범위: weight vector, winsorize/remove/keep 정책.
  - 조절 효과: 가중치와 outlier 처리가 distance와 ranking을 크게 바꿀 수 있다.
- `step_size`
  - 의미: 해당 method variant의 세부 설정값.
  - 값 범위: 구현 문서에서 정의한 enum, 정수, 실수 또는 구조화 값.
  - 조절 효과: 값 변경 시 detector 민감도, 계산 비용, 비교 가능성이 달라질 수 있으므로 변경 이력을 기록한다.
- `threshold_or_alpha`
  - 의미: 유의수준 또는 alarm 임계값.
  - 값 범위: 보통 0과 1 사이.
  - 조절 효과: 낮추면 보수적이고 false alarm이 줄지만 감지가 늦거나 약해지며, 높이면 민감해진다.
- `trend_threshold`
  - 의미: statistic, distance, score를 alarm으로 바꾸는 기준.
  - 값 범위: 측정값 scale에 따른 실수.
  - 조절 효과: 낮추면 민감도와 false alarm이 늘고, 높이면 안정적이지만 감지가 늦어진다.
- `window_size`
  - 의미: 계산에 사용하는 표본 또는 stream 길이.
  - 값 범위: 1 이상의 정수.
  - 조절 효과: 작으면 빠르고 민감하지만 noise가 크고, 크면 안정적이지만 detection delay가 늘어난다.

