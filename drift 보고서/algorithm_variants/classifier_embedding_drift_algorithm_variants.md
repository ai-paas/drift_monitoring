# Classifier 기반 embedding drift detection 알고리즘 변종 목록

## 1. 목적

이 문서는 `Classifier 기반 embedding drift detection`를 하나의 고정된 detector로 보지 않고, drift monitoring에서 상황에 따라 선택해야 하는 **알고리즘 변종들의 family**로 정리한다.

핵심 목적은 다음이다.

```text
상황 조건 -> 적절한 Classifier 기반 embedding drift detection 계열 변종 -> 출력 metric -> 주의사항 -> LLM 보고서 설명
```

---

## 2. Classifier 기반 embedding drift detection의 위치

```text
methodFamily CLASSIFIER_EMBEDDING_DRIFT
       ├─ algorithmVariant DOMAIN_CLASSIFIER_ROC_AUC
       ├─ algorithmVariant DOMAIN_CLASSIFIER_PROBABILITY_DRIFT
       └─ algorithmVariant CROSS_VALIDATED_DOMAIN_CLASSIFIER
```

`Classifier 기반 embedding drift detection`는 drift monitoring method 계열에 속한다. Classifier 기반 embedding drift detection 계열을 drift monitoring 문맥에서 입력 데이터와 운영 목적에 따라 선택 가능한 변종으로 정리한다.

---

## 3. 공통 개념

```text
methodFamily CLASSIFIER_EMBEDDING_DRIFT
  purpose ->
    Classifier 기반 embedding drift detection 계열을 drift monitoring 문맥에서 입력 데이터와 운영 목적에 따라 선택 가능한 변종으로 정리한다.

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

## 변종: DOMAIN_CLASSIFIER_ROC_AUC

`DOMAIN_CLASSIFIER_ROC_AUC`는 embedding을 입력으로 받아 각 샘플이 reference인지 current인지 구분하는 domain classifier를 학습하고, 그 구분 성능을 ROC AUC로 읽는 변종이다. AUC가 0.5에 가까우면 두 기간의 embedding 분포를 classifier가 거의 구분하지 못했다는 뜻이고, 1.0에 가까울수록 두 분포가 구분 가능하다는 신호가 강하다. drift monitoring에서는 label 없이 embedding 분포 변화 후보를 빠르게 확인하는 데 적합하다.

이 변종은 다음 상황에 적합하다.

- reference window와 current window의 embedding 벡터를 같은 feature space에서 비교한다.
- 업무 label이 아직 없거나 label 지연이 있어 입력 분포 변화부터 확인해야 한다.
- 분포 차이를 하나의 score로 요약해 threshold 또는 calibration 기준과 비교하고 싶다.
- feature별 원인 분석보다 전체 embedding 공간에서 두 기간이 구분되는지 먼저 보고 싶다.

해석할 때는 domain classifier의 ROC AUC, 검증 방식, threshold 기준을 함께 본다. AUC가 0.5보다 충분히 높고 calibration 기준을 넘으면 reference/current embedding을 구분할 수 있다는 뜻이므로 drift 후보 신호로 해석한다. 다만 AUC는 업무 성능 저하의 직접 지표가 아니며, classifier가 어느 embedding 축이나 sample segment에서 차이를 학습했는지는 별도 분석이 필요하다.

주의할 점은 domain classifier가 두 분포를 구분했다는 사실이 원인이나 운영 영향을 확정하지 않는다는 것이다. reference/current 표본 수 불균형, 중복 샘플, 시간 누수, classifier 과적합은 AUC를 왜곡할 수 있다. threshold는 운영 정책이나 과거 정상 구간 calibration 결과로 설명해야 하며, 보편적인 절대 기준처럼 쓰지 않는다. label이 없으면 concept drift나 performance drift를 단정하지 않고 입력 embedding 분포 변화 후보로 표현한다.

보고서 문장 예시는 다음과 같다.

```text
reference와 current embedding을 DOMAIN_CLASSIFIER_ROC_AUC로 비교한 결과,
domain classifier의 ROC AUC가 정상 구간 calibration 기준보다 높게 나타났다.
이는 두 기간의 embedding 분포가 classifier에 의해 구분되는 drift 후보 신호로 볼 수 있다.
다만 표본 수 불균형과 classifier 과적합 가능성이 있으므로,
검증 분할 방식과 segment별 embedding 차이를 함께 확인해야 한다.
```

---

## 변종: DOMAIN_CLASSIFIER_PROBABILITY_DRIFT

`DOMAIN_CLASSIFIER_PROBABILITY_DRIFT`는 domain classifier가 출력한 current 소속 확률의 분포를 drift score로 해석하는 변종이다. 단순히 AUC 하나만 보는 대신, 각 샘플이 얼마나 current 쪽으로 치우쳐 예측되는지와 그 확률 분포가 시간에 따라 어떻게 이동하는지를 본다. embedding 분포 변화가 특정 sample군에 집중되는지 확인할 때 유용하다.

이 변종은 다음 상황에 적합하다.

- domain classifier의 확률 score를 샘플 단위 또는 segment 단위로 추적하고 싶다.
- 전체 AUC보다 current 확률의 평균, 분위수, tail 비중 변화가 더 중요한 운영 질문이다.
- drift 후보가 일부 사용자군, region, category에 집중되는지 확인해야 한다.
- score 분포를 chart나 report에서 window별로 비교하고 싶다.

해석할 때는 current-class probability의 평균, 중앙값, 분위수, 높은 확률 구간의 비중을 함께 본다. Current 소속 확률이 reference 대비 전반적으로 높아지면 classifier가 현재 window 샘플을 더 쉽게 구분한다는 뜻이므로 embedding 분포 변화 신호로 볼 수 있다. Segment별 확률 분포 차이가 크면 전체 drift score보다 어느 집단이 변화를 주도하는지에 초점을 맞춰 해석한다.

주의할 점은 classifier probability가 잘 calibration돼 있지 않으면 확률값 자체를 절대 확률처럼 해석하기 어렵다는 것이다. 모델 과적합, class imbalance, reference/current sampling 방식이 확률 분포를 왜곡할 수 있다. Probability drift는 원인 설명이 아니라 구분 score의 이동이므로, 업무 원인과 성능 영향은 feature attribution, segment 분석, 후속 label 기반 평가로 확인해야 한다.

보고서 문장 예시는 다음과 같다.

```text
reference와 current embedding에 대해 DOMAIN_CLASSIFIER_PROBABILITY_DRIFT를 적용한 결과,
current 소속 확률의 평균과 상위 분위수 비중이 기준 window보다 높아졌다.
이는 현재 샘플이 domain classifier에서 current 쪽으로 더 강하게 구분되는 분포 변화 후보 신호다.
다만 확률 calibration과 class imbalance의 영향을 받을 수 있으므로,
segment별 score 분포와 후속 label 기반 성능 지표를 함께 확인해야 한다.
```

---

## 변종: CROSS_VALIDATED_DOMAIN_CLASSIFIER

`CROSS_VALIDATED_DOMAIN_CLASSIFIER`는 domain classifier 기반 drift 탐지를 교차검증 또는 holdout 검증으로 평가해 과적합 영향을 줄이는 변종이다. reference/current를 구분하는 classifier가 학습 데이터에서만 잘 맞는지, 보지 않은 fold에서도 일관되게 구분하는지를 확인한다. 표본 수가 제한적이거나 embedding 차원이 높아 classifier가 쉽게 과적합할 수 있는 상황에서 중요하다.

이 변종은 다음 상황에 적합하다.

- embedding 차원이 높고 reference/current sample 수가 충분히 크지 않다.
- 단일 train/test split 결과가 우연한 분할에 민감할 수 있다.
- domain classifier AUC, accuracy, log loss 같은 score의 평균과 fold 간 변동성을 함께 보고하고 싶다.
- drift alarm을 내기 전에 classifier 기반 신호의 재현성을 확인해야 한다.

해석할 때는 fold별 score의 평균, 표준편차, 최저/최고값을 함께 본다. 모든 fold에서 AUC나 구분 score가 calibration 기준보다 높으면 reference/current embedding 차이가 안정적으로 포착된다고 해석할 수 있다. 반대로 평균은 높지만 fold 간 편차가 크면 특정 split이나 sample군에 의존한 신호일 수 있으므로 drift 후보의 신뢰도를 낮춰 해석한다.

주의할 점은 교차검증이 시간 누수나 sampling bias를 자동으로 해결하지 않는다는 것이다. 시간 순서가 중요한 monitoring에서는 random split보다 시간 기반 split 또는 blocked split이 필요할 수 있다. 같은 사용자나 문서가 여러 fold에 중복되면 score가 과대평가될 수 있으며, class imbalance가 크면 stratification 또는 가중치 설정을 보고해야 한다. 이 변종도 label 없이 성능 저하를 확정하지 않는다.

보고서 문장 예시는 다음과 같다.

```text
CROSS_VALIDATED_DOMAIN_CLASSIFIER로 reference/current embedding 구분 성능을 검증한 결과,
fold별 ROC AUC가 일관되게 calibration 기준을 상회했다.
이는 단일 분할에만 의존하지 않는 embedding 분포 변화 후보 신호로 해석할 수 있다.
다만 시간 누수, 중복 샘플, fold 간 score 편차가 결과를 왜곡할 수 있으므로,
분할 방식과 fold별 score 분포를 함께 보고해야 한다.
```

---

## SelectionRule 카탈로그

```text
selectionRule CLASSIFIER_EMBEDDING_DRIFT_DEFAULT_USE
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

> Classifier 기반 embedding drift detection 카탈로그는 "이 방법이 무엇인가"가 아니라, "어떤 상황에서 어떤 변종을 선택하고 어떤 주의사항과 함께 설명해야 하는가"를 구조화한다.
