# Hotelling T2 알고리즘 변종 목록

## 1. 목적

이 문서는 `Hotelling T2`를 하나의 고정된 detector로 보지 않고, drift monitoring에서 상황에 따라 선택해야 하는 **알고리즘 변종들의 family**로 정리한다.

핵심 목적은 다음이다.

```text
상황 조건 -> 적절한 Hotelling T2 계열 변종 -> 출력 metric -> 주의사항 -> LLM 보고서 설명
```

---

## 2. Hotelling T2의 위치

```text
methodFamily HOTELLING_T2
       ├─ algorithmVariant HOTELLING_T2_ONE_SAMPLE_PHASE_II
       ├─ algorithmVariant HOTELLING_T2_TWO_SAMPLE
       └─ algorithmVariant REGULARIZED_HOTELLING_T2
```

`Hotelling T2`는 다변량 평균 shift 검정 계열에 속한다. 공분산 구조를 고려해 다변량 평균 벡터가 reference와 달라졌는지 감시한다.

---

## 3. 공통 개념

```text
methodFamily HOTELLING_T2
  purpose ->
    공분산 구조를 고려해 다변량 평균 벡터가 reference와 달라졌는지 감시한다.

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

## 변종: HOTELLING_T2_ONE_SAMPLE_PHASE_II

`HOTELLING_T2_ONE_SAMPLE_PHASE_II`는 현재 관측 벡터 또는 current window 평균을 기존 정상 기준 평균/공분산과 비교하는 Phase II monitoring 변종이다. 여러 numeric feature의 상관 구조를 반영해 단변량 평균 변화로는 놓칠 수 있는 다변량 평균 shift를 감시한다. 출력은 T2 statistic, control limit, alarm state로 해석한다.

사용 상황:
- 정상 기준 기간에서 평균 벡터와 공분산 행렬을 미리 추정해 둔 경우
- 운영 중 들어오는 다변량 numeric feature 또는 embedding 요약 벡터를 감시할 때
- feature 간 상관을 고려한 multivariate mean shift 신호가 필요한 경우

해석 방법:
- T2 statistic이 control limit을 넘으면 current 벡터가 정상 기준 평균/공분산 구조에서 보기 어려운 위치에 있다는 뜻이다.
- statistic이 클수록 공분산을 고려한 기준 평균과의 거리가 크다.
- alarm은 다변량 평균 shift 후보이며, 어떤 feature가 원인인지는 contribution 분석이 필요하다.
- 보고서에는 기준 기간, control limit 산정 방식, 주요 feature contribution을 함께 적는다.

주의점:
- 정상 기준 공분산 추정이 불안정하면 T2 statistic도 불안정하다.
- feature 수가 표본 수에 비해 많으면 공분산 역행렬 계산이 어렵다.
- 정규성 가정이 크게 깨지면 control limit 해석이 약해질 수 있다.

보고서 문장 예시:

```text
HOTELLING_T2_ONE_SAMPLE_PHASE_II로 current window 평균을 정상 기준과 비교한 결과,
T2 statistic이 control limit을 초과해 다변량 평균 shift 후보가 관측됐다.
이는 여러 feature의 상관 구조를 고려했을 때 current 상태가 기준 평균에서 멀어졌음을 의미한다.
다만 공분산 추정 안정성과 주요 feature contribution을 함께 확인해야 한다.
```

---

## 변종: HOTELLING_T2_TWO_SAMPLE

`HOTELLING_T2_TWO_SAMPLE`은 reference window와 current window의 다변량 평균 벡터 차이를 직접 검정하는 Hotelling T2 변종이다. 두 기간의 feature 평균이 공분산 구조를 고려했을 때 같은지 평가한다. 출력은 T2 statistic, p-value, 평균 차이 방향, alarm state로 해석한다.

사용 상황:
- batch drift report에서 reference/current 기간의 다변량 numeric feature 평균을 비교할 때
- 단일 정상 기준이 아니라 두 window를 같은 조건에서 직접 비교하고 싶을 때
- 여러 feature의 작은 평균 변화가 결합되어 의미 있는 차이를 만드는지 확인할 때

해석 방법:
- T2 statistic이 클수록 두 window 평균 벡터 차이가 공분산 대비 크다.
- p-value가 작으면 reference/current 평균 벡터가 같다는 가설을 기각할 근거가 강하다.
- alarm은 두 기간의 다변량 평균 차이 후보이며, feature별 차이를 따로 분해해야 한다.
- 보고서에는 window 기간, 표본 수, 평균 차이가 큰 feature를 함께 제시한다.

주의점:
- 두 window의 공분산이 크게 다르면 pooled covariance 기반 해석이 약해진다.
- 정규성 가정과 표본 수 조건이 부족하면 p-value가 불안정할 수 있다.
- 통계적으로 유의해도 업무 영향은 feature별 변화 크기로 별도 판단해야 한다.

보고서 문장 예시:

```text
HOTELLING_T2_TWO_SAMPLE로 reference/current window를 비교한 결과,
T2 statistic과 p-value가 두 기간의 다변량 평균 벡터 차이 후보를 보였다.
이는 여러 numeric feature의 평균 조합이 기준 기간과 달라졌을 가능성을 나타낸다.
다만 공분산 동질성 가정과 feature별 평균 차이를 함께 확인해야 한다.
```

---

## 변종: REGULARIZED_HOTELLING_T2

`REGULARIZED_HOTELLING_T2`는 feature 수가 많거나 표본 수가 부족해 공분산 역행렬이 불안정할 때 regularization을 적용하는 Hotelling T2 변종이다. shrinkage, diagonal loading, PCA 후 T2 같은 방식으로 공분산 추정을 안정화해 다변량 평균 shift를 감시한다. 출력은 regularized T2 statistic, regularization policy, threshold 또는 alarm state로 해석한다.

사용 상황:
- 고차원 feature, embedding, 센서 다변량 벡터처럼 차원이 표본 수에 비해 큰 경우
- 일반 Hotelling T2에서 공분산 행렬이 singular 또는 ill-conditioned인 경우
- 공분산 안정화를 거친 다변량 평균 shift score가 필요한 monitoring에서

해석 방법:
- regularized T2가 calibration된 threshold를 넘으면 안정화된 공분산 기준에서 평균 shift 후보로 본다.
- regularization은 statistic scale을 바꾸므로 일반 T2 threshold와 직접 비교하지 않는다.
- feature contribution은 regularization 방식에 따라 해석 단위가 달라질 수 있다.
- 보고서에는 사용한 regularization 방식과 threshold 산정 방법을 명시한다.

주의점:
- regularization 강도 선택 근거가 없으면 alarm 민감도 해석이 어렵다.
- shrinkage가 강하면 실제 feature 간 상관 구조 일부를 희석할 수 있다.
- PCA나 embedding 축소를 쓴 경우 원 feature 수준 원인 해석이 제한될 수 있다.

보고서 문장 예시:

```text
REGULARIZED_HOTELLING_T2로 고차원 feature 평균을 비교한 결과,
regularized T2 statistic이 calibration threshold를 초과했다.
이는 공분산 안정화를 적용한 기준에서도 current 평균 벡터가 reference와 달라졌을 가능성을 나타낸다.
다만 regularization 강도와 threshold 산정 방식이 결과 민감도에 영향을 주므로 보고서에 함께 명시해야 한다.
```

---

## SelectionRule 카탈로그

```text
selectionRule HOTELLING_T2_DEFAULT_USE
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

> Hotelling T2 카탈로그는 "이 방법이 무엇인가"가 아니라, "어떤 상황에서 어떤 변종을 선택하고 어떤 주의사항과 함께 설명해야 하는가"를 구조화한다.
