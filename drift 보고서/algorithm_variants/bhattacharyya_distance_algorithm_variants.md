# Bhattacharyya Distance 알고리즘 변종 목록

## 1. 목적

이 문서는 `Bhattacharyya Distance`를 하나의 고정된 detector로 보지 않고, drift monitoring에서 상황에 따라 선택해야 하는 **알고리즘 변종들의 family**로 정리한다.

핵심 목적은 다음이다.

```text
상황 조건 -> 적절한 Bhattacharyya Distance 계열 변종 -> 출력 metric -> 주의사항 -> LLM 보고서 설명
```

---

## 2. Bhattacharyya Distance의 위치

```text
methodFamily BHATTACHARYYA_DISTANCE
       ├─ algorithmVariant DISCRETE_BHATTACHARYYA_DISTANCE
       ├─ algorithmVariant GAUSSIAN_BHATTACHARYYA_DISTANCE
       └─ algorithmVariant HISTOGRAM_BHATTACHARYYA_DISTANCE
```

`Bhattacharyya Distance`는 drift monitoring method 계열에 속한다. Bhattacharyya Distance 계열을 drift monitoring 문맥에서 입력 데이터와 운영 목적에 따라 선택 가능한 변종으로 정리한다.

---

## 3. 공통 개념

```text
methodFamily BHATTACHARYYA_DISTANCE
  purpose ->
    Bhattacharyya Distance 계열을 drift monitoring 문맥에서 입력 데이터와 운영 목적에 따라 선택 가능한 변종으로 정리한다.

  commonOutputs ->
    TEST_STATISTIC_OR_DISTANCE
    P_VALUE_OR_SCORE_OPTIONAL
    ALARM_STATE_OPTIONAL

  commonCautions ->
    detector 결과만으로 원인, 성능 저하, concept drift를 확정하지 않는다.
    reference 기간, current 기간, sample size, threshold 근거를 함께 보고한다.
    label이 없으면 supervised concept drift 또는 performance drift 확정 표현을 피한다.
```

---

## 변종: DISCRETE_BHATTACHARYYA_DISTANCE

`DISCRETE_BHATTACHARYYA_DISTANCE`는 범주형 값이나 이미 이산화된 구간별 비율을 기준으로 reference 분포와 current 분포의 겹침 정도를 비교하는 변종이다. 두 분포가 많이 겹치면 distance가 작고, 특정 category의 비중이 달라져 겹침이 줄어들면 distance가 커진다. drift monitoring에서는 channel, region, class, bucket 같은 discrete signal의 구성비 변화를 빠르게 screening하는 데 사용한다.

이 변종은 다음 상황에 적합하다.

- 입력이 범주형 feature, class label, error type, bucket id처럼 discrete category로 정의된다.
- reference/current 기간의 category별 count 또는 probability table을 비교한다.
- 특정 category mix 변화가 모델 입력 또는 운영 KPI에 영향을 줄 수 있다.
- p-value보다 분포 간 overlap 감소를 distance score로 보고하고 싶다.

해석할 때는 Bhattacharyya coefficient와 distance의 방향을 구분한다. Coefficient가 1에 가까울수록 두 discrete 분포가 많이 겹치고, 0에 가까울수록 겹침이 작다. Distance는 보통 coefficient가 작아질수록 커지므로, distance 상승은 category 구성비가 기준 기간과 멀어졌다는 뜻이다. 어떤 category가 변화를 만들었는지는 category별 비중 차이와 contribution을 함께 확인해야 한다.

주의할 점은 distance가 커졌다는 사실만으로 어떤 업무 원인이 발생했는지 알 수 없다는 것이다. 희소 category가 많거나 current count가 작으면 작은 count 변동도 distance에 크게 보일 수 있다. reference와 current에서 category 정의, unknown 처리, rare category 묶음 기준이 같아야 한다. threshold는 과거 안정 기간의 변동폭이나 운영 calibration으로 정해야 하며 보편적 절대 기준처럼 쓰지 않는다.

보고서 문장 예시는 다음과 같다.

```text
기준 기간과 현재 기간의 category 구성비를 DISCRETE_BHATTACHARYYA_DISTANCE로 비교한 결과,
Bhattacharyya distance가 기준 변동 범위보다 크게 상승했다.
이는 category mix의 겹침이 줄어든 분포 변화 후보 신호로 볼 수 있다.
다만 희소 category와 unknown 처리의 영향이 있을 수 있으므로,
category별 비중 차이와 데이터 수집 조건을 함께 확인해야 한다.
```

---

## 변종: GAUSSIAN_BHATTACHARYYA_DISTANCE

`GAUSSIAN_BHATTACHARYYA_DISTANCE`는 reference와 current의 연속형 신호를 각각 Gaussian 분포로 요약해 평균과 분산 차이를 하나의 distance로 비교하는 변종이다. 원자료 전체를 직접 비교하기보다 각 기간의 mean, variance 또는 covariance 구조가 얼마나 달라졌는지를 본다. drift monitoring에서는 score, embedding component, KPI처럼 연속형 값이 대략 단봉형 분포를 보일 때 간결한 분포 변화 지표로 사용한다.

이 변종은 다음 상황에 적합하다.

- 연속형 feature나 score의 reference/current 분포를 평균과 분산 중심으로 비교한다.
- 데이터가 단봉형이고 Gaussian 근사가 운영상 충분히 설명 가능하다.
- 여러 numerical signal을 가벼운 distance score로 반복 모니터링한다.
- p-value보다 분포 요약치 변화의 크기를 추적하고 싶다.

해석할 때는 distance가 평균 이동과 분산 변화의 합성 신호라는 점을 먼저 본다. Distance가 작으면 두 기간의 Gaussian 요약 분포가 많이 겹친다는 뜻이고, distance가 커지면 평균, 분산, covariance 중 하나 이상이 기준과 달라졌다는 뜻이다. 단변량에서는 평균 차이와 표준편차 변화를 같이 확인하고, 다변량에서는 covariance 변화나 특정 component의 기여를 함께 확인해야 한다.

주의할 점은 Gaussian 근사가 맞지 않는 heavy-tail, 다봉형, 강한 skew 분포에서는 distance 해석이 왜곡될 수 있다는 것이다. 이상치가 평균과 분산을 크게 바꾸면 실제 대다수 sample의 변화보다 distance가 크게 나타날 수 있다. 표본 수가 작으면 variance 추정이 불안정해진다. 이 값은 통계적 유의성 자체가 아니라 분포 요약 간 거리이므로 threshold와 alarm 기준은 과거 안정 구간으로 calibration해야 한다.

보고서 문장 예시는 다음과 같다.

```text
기준 기간과 현재 기간의 numerical score를 GAUSSIAN_BHATTACHARYYA_DISTANCE로 비교한 결과,
Gaussian 요약 분포 간 distance가 과거 안정 구간보다 상승했다.
이는 평균 또는 분산 구조가 기준 기간과 달라진 분포 변화 후보 신호다.
다만 분포가 비정규적이거나 이상치가 포함되면 distance가 과대 해석될 수 있으므로,
평균, 표준편차, 분위수 변화를 함께 확인해야 한다.
```

---

## 변종: HISTOGRAM_BHATTACHARYYA_DISTANCE

`HISTOGRAM_BHATTACHARYYA_DISTANCE`는 연속형 값을 같은 bin으로 나눈 뒤, reference histogram과 current histogram의 겹침 정도를 distance로 비교하는 변종이다. Gaussian 가정을 두지 않고 값 구간별 비중 변화를 반영할 수 있어, 분포 모양이나 tail 변화까지 보고 싶은 경우에 적합하다. drift monitoring에서는 feature, score, residual의 값 구간 이동을 직관적으로 설명하는 보조 지표로 사용한다.

이 변종은 다음 상황에 적합하다.

- 연속형 신호를 공통 bin으로 나눠 reference/current histogram을 비교한다.
- 분포가 비정규적이거나 다봉형이라 Gaussian 요약만으로 부족하다.
- 특정 값 구간의 비중 증가, 감소, tail 변화가 중요한 운영 질문이다.
- 차트에서 histogram과 distance를 함께 제시해 사용자가 변화 구간을 확인하게 한다.

해석할 때는 distance 상승을 histogram overlap 감소로 읽는다. 같은 bin 정의에서 reference와 current의 비중이 비슷하면 distance가 작고, 특정 bin으로 current sample이 몰리거나 tail bin 비중이 늘면 distance가 커진다. 이 값은 어느 구간에서 차이가 났는지를 직접 요약하지 않으므로, bin별 비중 차이와 누적분포를 함께 봐야 한다.

주의할 점은 bin 경계와 bin 개수가 결과에 직접 영향을 준다는 것이다. 너무 적은 bin은 변화를 숨길 수 있고, 너무 많은 bin은 표본 부족으로 noise를 키울 수 있다. reference/current에 같은 bin 경계, 같은 clipping, 같은 결측 처리 기준을 적용해야 한다. Distance가 커졌다고 해서 모델 성능 저하나 업무 원인이 확정되는 것은 아니며, threshold는 과거 안정 구간에서 calibration해야 한다.

보고서 문장 예시는 다음과 같다.

```text
기준 기간과 현재 기간의 feature histogram을 HISTOGRAM_BHATTACHARYYA_DISTANCE로 비교한 결과,
histogram 간 distance가 상승해 두 분포의 overlap이 감소했다.
이는 특정 값 구간의 비중이 기준 기간과 달라진 drift 후보 신호로 볼 수 있다.
다만 결과는 bin 경계와 표본 수의 영향을 받으므로,
bin별 비중 차이와 tail 구간 변화를 함께 확인해야 한다.
```

---

## SelectionRule 카탈로그

```text
selectionRule BHATTACHARYYA_DISTANCE_DEFAULT_USE
  if ->
    input_signal_matches_method_assumption
    and reference_or_baseline_is_defined

  recommend ->
    대표 변종 중 운영 목적에 맞는 variant

  because ->
    같은 method family 안에서도 입력 신호, window 구성, threshold 목적에 따라 해석이 달라진다.

  caveat ->
    detector 결과만으로 성능 저하, concept drift, 원인을 확정하지 않는다.
```

---

## LLM 추천을 위한 최종 구조

```text
상황 조건
  -> selection rule
  -> algorithm variant 추천
  -> output metric 설명
  -> caveat 설명
  -> report guidance 생성
```

한 문장으로 정리하면:

> Bhattacharyya Distance 카탈로그는 "이 방법이 무엇인가"가 아니라, "어떤 상황에서 어떤 변종을 선택하고 어떤 주의사항과 함께 설명해야 하는가"를 구조화한다.
