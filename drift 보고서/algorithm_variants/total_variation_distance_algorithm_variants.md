# Total Variation Distance 알고리즘 변종 목록

## 1. 목적

이 문서는 `Total Variation Distance`를 하나의 고정된 detector로 보지 않고, drift monitoring에서 상황에 따라 선택해야 하는 **알고리즘 변종들의 family**로 정리한다.

핵심 목적은 다음이다.

```text
상황 조건 -> 적절한 Total Variation Distance 계열 변종 -> 출력 metric -> 주의사항 -> LLM 보고서 설명
```

---

## 2. Total Variation Distance의 위치

```text
methodFamily TOTAL_VARIATION_DISTANCE
       ├─ algorithmVariant CATEGORICAL_TOTAL_VARIATION
       ├─ algorithmVariant HISTOGRAM_TOTAL_VARIATION
       └─ algorithmVariant PROBABILITY_VECTOR_TOTAL_VARIATION
```

`Total Variation Distance`는 drift monitoring method 계열에 속한다. Total Variation Distance 계열을 drift monitoring 문맥에서 입력 데이터와 운영 목적에 따라 선택 가능한 변종으로 정리한다.

---

## 3. 공통 개념

```text
methodFamily TOTAL_VARIATION_DISTANCE
  purpose ->
    Total Variation Distance 계열을 drift monitoring 문맥에서 입력 데이터와 운영 목적에 따라 선택 가능한 변종으로 정리한다.

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

## 변종: CATEGORICAL_TOTAL_VARIATION

범주형 분포의 category 비율 차이를 total variation distance로 요약하는 변종이다. 두 기간 사이에서 바뀐 확률 질량의 총량을 직관적으로 보여준다.

- 사용 상황: 채널, 지역, 상품군, class 예측 비율처럼 category mix 변화가 중요한 경우에 적합하다.
- 해석 방법: 값이 0에 가까우면 분포가 유사하고, 커질수록 reference와 current category 비율 차이가 크다고 본다.
- 주의점: 희소 category와 신규 category 처리 방식에 민감하므로 category 병합 및 smoothing 정책을 명시한다.
- 보고서 문장 예시: "Categorical total variation distance가 상승해 current category 구성의 질량 이동이 커진 후보 신호가 확인되었다."

---

## 변종: HISTOGRAM_TOTAL_VARIATION

수치형 feature를 histogram bin으로 변환한 뒤 bin 비율의 total variation distance를 계산하는 변종이다.

- 사용 상황: 연속형 feature의 분포 변화 규모를 bin 기반으로 빠르게 비교해야 할 때 적합하다.
- 해석 방법: histogram total variation이 커지면 current 값들이 reference와 다른 구간에 더 많이 분포한다는 후보로 본다.
- 주의점: bin 폭, bin 범위, outlier clipping 정책에 따라 결과가 달라진다.
- 보고서 문장 예시: "Histogram total variation distance가 증가해 current 수치형 feature가 기준 구간 분포와 달라진 후보가 나타났다."

---

## 변종: PROBABILITY_VECTOR_TOTAL_VARIATION

모델 예측 확률 벡터나 class probability 평균 벡터의 차이를 total variation distance로 계산하는 변종이다.

- 사용 상황: class probability output, topic probability, ensemble vote 비율처럼 확률 벡터 자체의 이동을 감시할 때 적합하다.
- 해석 방법: 확률 벡터 total variation이 커지면 예측 분포 또는 soft assignment 구성이 기준과 달라졌다고 본다.
- 주의점: calibration 변경이나 class prior shift가 원인일 수 있으므로 실제 성능 저하와 구분한다.
- 보고서 문장 예시: "Probability vector total variation이 증가해 current 예측 확률 구성이 기준 기간과 달라진 후보 신호가 확인되었다."

---

## SelectionRule 카탈로그

```text
selectionRule TOTAL_VARIATION_DISTANCE_DEFAULT_USE
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

> Total Variation Distance 카탈로그는 "이 방법이 무엇인가"가 아니라, "어떤 상황에서 어떤 변종을 선택하고 어떤 주의사항과 함께 설명해야 하는가"를 구조화한다.
