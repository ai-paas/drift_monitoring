# Text Domain Classifier Drift 알고리즘 변종 목록

## 1. 목적

이 문서는 `Text Domain Classifier Drift`를 하나의 고정된 detector로 보지 않고, drift monitoring에서 상황에 따라 선택해야 하는 **알고리즘 변종들의 family**로 정리한다.

핵심 목적은 다음이다.

```text
상황 조건 -> 적절한 Text Domain Classifier Drift 계열 변종 -> 출력 metric -> 주의사항 -> LLM 보고서 설명
```

---

## 2. Text Domain Classifier Drift의 위치

```text
methodFamily TEXT_DOMAIN_CLASSIFIER_DRIFT
       ├─ algorithmVariant TEXT_DOMAIN_CLASSIFIER_ROC_AUC
       ├─ algorithmVariant TEXT_DOMAIN_CLASSIFIER_STAT_TEST
       └─ algorithmVariant TEXT_DESCRIPTOR_DRIFT
```

`Text Domain Classifier Drift`는 drift monitoring method 계열에 속한다. Text Domain Classifier Drift 계열을 drift monitoring 문맥에서 입력 데이터와 운영 목적에 따라 선택 가능한 변종으로 정리한다.

---

## 3. 공통 개념

```text
methodFamily TEXT_DOMAIN_CLASSIFIER_DRIFT
  purpose ->
    Text Domain Classifier Drift 계열을 drift monitoring 문맥에서 입력 데이터와 운영 목적에 따라 선택 가능한 변종으로 정리한다.

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

## 변종: TEXT_DOMAIN_CLASSIFIER_ROC_AUC

Reference와 current 텍스트를 구분하는 domain classifier를 학습하고 ROC-AUC로 분리 가능성을 평가하는 변종이다.

- 사용 상황: query, prompt, 문서 텍스트의 표현 분포가 두 기간 사이에 달라졌는지 하나의 판별 성능으로 요약할 때 적합하다.
- 해석 방법: ROC-AUC가 0.5에서 멀어질수록 classifier가 두 기간 텍스트를 구분하기 쉽다는 drift 후보로 본다.
- 주의점: 중복 문장, 시간 marker, 데이터 누수, 과적합이 있으면 drift가 과장될 수 있다.
- 보고서 문장 예시: "Text domain classifier의 ROC-AUC가 높아 reference와 current 텍스트가 구분 가능한 수준으로 달라진 후보 신호가 확인되었다."

---

## 변종: TEXT_DOMAIN_CLASSIFIER_STAT_TEST

Domain classifier의 예측 score나 embedding descriptor에 통계 검정을 적용해 텍스트 도메인 차이를 평가하는 변종이다.

- 사용 상황: ROC-AUC뿐 아니라 score 분포 차이의 p-value나 threshold 기반 경보가 필요한 경우에 적합하다.
- 해석 방법: score 분포 검정 결과가 유의하면 classifier 관점의 텍스트 분포 차이가 우연 수준을 넘는 후보로 본다.
- 주의점: 검정 대상 score가 검증 데이터에서 산출되었는지 확인하고, 학습 데이터 score로 검정하지 않는다.
- 보고서 문장 예시: "Text domain classifier score 분포 검정에서 두 기간 텍스트 표현 차이가 통계적으로 유의한 후보로 나타났다."

---

## 변종: TEXT_DESCRIPTOR_DRIFT

문장 길이, 언어 비율, token 수, embedding norm, topic label 같은 text descriptor의 분포 변화를 감지하는 변종이다.

- 사용 상황: classifier의 black-box 점수보다 어떤 텍스트 속성이 바뀌었는지 설명 가능한 단서를 얻고 싶을 때 적합하다.
- 해석 방법: 특정 descriptor의 평균, 비율, 분포가 기준과 달라지면 텍스트 입력 특성 변화 후보로 본다.
- 주의점: descriptor drift는 semantic drift의 보조 신호이며, 텍스트 의미 변화 자체를 단독으로 확정하지 않는다.
- 보고서 문장 예시: "Text descriptor 분석에서 current query의 길이와 topic 구성 비율이 기준과 달라진 후보가 확인되었다."

---

## SelectionRule 카탈로그

```text
selectionRule TEXT_DOMAIN_CLASSIFIER_DRIFT_DEFAULT_USE
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

> Text Domain Classifier Drift 카탈로그는 "이 방법이 무엇인가"가 아니라, "어떤 상황에서 어떤 변종을 선택하고 어떤 주의사항과 함께 설명해야 하는가"를 구조화한다.
