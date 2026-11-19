# Tree Feature 기반 감지 알고리즘 변종 목록

## 1. 목적

이 문서는 `Tree Feature 기반 감지`를 하나의 고정된 detector로 보지 않고, drift monitoring에서 상황에 따라 선택해야 하는 **알고리즘 변종들의 family**로 정리한다.

핵심 목적은 다음이다.

```text
상황 조건 -> 적절한 Tree Feature 기반 감지 계열 변종 -> 출력 metric -> 주의사항 -> LLM 보고서 설명
```

---

## 2. Tree Feature 기반 감지의 위치

```text
methodFamily TREE_FEATURE_DRIFT
       ├─ algorithmVariant TIME_FEATURE_SPLIT_DETECTOR
       └─ algorithmVariant DOMAIN_CLASSIFIER_TREE
```

`Tree Feature 기반 감지`는 time feature based tree drift heuristic 계열에 속한다. 시간 피처가 tree split이나 importance에 반복 등장하는지를 drift 후보 신호로 사용한다.

---

## 3. 공통 개념

```text
methodFamily TREE_FEATURE_DRIFT
  purpose ->
    시간 피처가 tree split이나 importance에 반복 등장하는지를 drift 후보 신호로 사용한다.

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

## 변종: TIME_FEATURE_SPLIT_DETECTOR

시간 또는 기간 indicator feature가 tree split에 반복적으로 사용되는지 확인하는 heuristic 변종이다. 시간 자체가 데이터를 잘 구분한다면 temporal covariate shift 후보로 본다.

- 사용 상황: drift 시점 후보를 빠르게 탐색하거나, 시간 feature가 feature space를 나누는 강한 단서인지 확인할 때 적합하다.
- 해석 방법: time split count가 많고 split depth가 얕을수록 시간에 따라 데이터 구조가 달라졌다는 보조 신호로 해석한다.
- 주의점: 통계 검정처럼 단독 확정 근거로 쓰지 말고, 다른 drift detector와 교차 확인한다.
- 보고서 문장 예시: "Tree split에서 time feature가 반복적으로 상위 분기에 등장해 시간대별 feature 구조 변화 후보가 나타났다."

---

## 변종: DOMAIN_CLASSIFIER_TREE

Reference/current 여부를 label로 두고 tree classifier가 두 기간을 구분할 수 있는지 보는 변종이다. 구분에 기여한 feature와 split rule을 drift 원인 후보로 제시한다.

- 사용 상황: 분포 차이 자체뿐 아니라 어떤 feature가 두 기간을 가르는지 설명 가능한 단서가 필요할 때 적합하다.
- 해석 방법: 검증 ROC-AUC가 높고 특정 feature importance가 크면 그 feature가 reference/current 차이를 설명하는 후보라고 본다.
- 주의점: 학습/검증 분리, 시간 누수, target leakage를 확인해야 하며 classifier 성능만으로 원인을 확정하지 않는다.
- 보고서 문장 예시: "Domain classifier tree가 reference와 current를 구분했으며, 상위 split feature가 drift 설명 후보로 제시되었다."

---

## SelectionRule 카탈로그

```text
selectionRule TREE_FEATURE_DRIFT_DEFAULT_USE
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

> Tree Feature 기반 감지 카탈로그는 "이 방법이 무엇인가"가 아니라, "어떤 상황에서 어떤 변종을 선택하고 어떤 주의사항과 함께 설명해야 하는가"를 구조화한다.
