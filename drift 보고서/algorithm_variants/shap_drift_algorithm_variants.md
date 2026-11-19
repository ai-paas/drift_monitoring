# SHAP Drift 알고리즘 변종 목록

## 1. 목적

이 문서는 `SHAP Drift`를 하나의 고정된 detector로 보지 않고, drift monitoring에서 상황에 따라 선택해야 하는 **알고리즘 변종들의 family**로 정리한다.

핵심 목적은 다음이다.

```text
상황 조건 -> 적절한 SHAP Drift 계열 변종 -> 출력 metric -> 주의사항 -> LLM 보고서 설명
```

---

## 2. SHAP Drift의 위치

```text
methodFamily SHAP_DRIFT
       ├─ algorithmVariant SHAP_VALUE_DISTRIBUTION_TEST
       ├─ algorithmVariant GLOBAL_IMPORTANCE_RANK_SHIFT
       └─ algorithmVariant CLASS_CONDITIONAL_SHAP_DRIFT
```

`SHAP Drift`는 feature attribution distribution drift 계열에 속한다. SHAP value 분포와 global importance가 시간에 따라 변했는지 감시한다.

---

## 3. 공통 개념

```text
methodFamily SHAP_DRIFT
  purpose ->
    SHAP value 분포와 global importance가 시간에 따라 변했는지 감시한다.

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

## 변종: SHAP_VALUE_DISTRIBUTION_TEST

Feature별 SHAP value 분포를 reference와 current로 비교해 모델 기여 패턴이 달라졌는지 보는 변종이다. 입력 feature 자체가 아니라 모델 설명값의 분포 변화에 초점을 둔다.

- 사용 상황: 모델 decision logic에 영향을 주는 feature contribution이 시간에 따라 달라졌는지 확인해야 할 때 적합하다.
- 해석 방법: 특정 feature의 SHAP distribution distance가 커지면 해당 feature가 예측에 기여하는 방식이 기준 기간과 달라진 후보로 본다.
- 주의점: SHAP background data, explainer 설정, 모델 버전이 바뀌면 drift처럼 보일 수 있으므로 같은 조건에서 비교한다.
- 보고서 문장 예시: "SHAP value 분포 검정에서 일부 feature의 기여 패턴이 기준 기간과 달라진 후보가 확인되었다."

---

## 변종: GLOBAL_IMPORTANCE_RANK_SHIFT

전체 SHAP importance 순위가 reference와 current 사이에서 어떻게 바뀌었는지 요약하는 변종이다. 모델 설명 drift를 보고서에서 간결하게 전달할 때 사용한다.

- 사용 상황: drift 원인 후보를 top feature 변화 중심으로 설명하거나 업무 담당자에게 중요 feature 순위 변화를 보여줄 때 적합하다.
- 해석 방법: 중요도 순위가 크게 오른 feature는 current 예측에서 상대적으로 더 큰 역할을 하게 된 후보로 본다.
- 주의점: 표본 수가 작으면 rank가 쉽게 흔들리므로 rank delta와 실제 importance 크기 변화를 함께 확인한다.
- 보고서 문장 예시: "Global SHAP importance 순위에서 상위 기여 feature 구성이 바뀌어 모델 설명 패턴 변화 후보가 나타났다."

---

## 변종: CLASS_CONDITIONAL_SHAP_DRIFT

Class별로 SHAP value 분포와 importance 변화를 따로 비교하는 변종이다. 전체 평균에서는 숨겨지는 class-specific behavior drift를 확인한다.

- 사용 상황: 분류 모델에서 특정 class의 예측 근거만 변했는지, 또는 민감 class의 설명 패턴을 별도로 감시해야 할 때 적합하다.
- 해석 방법: 특정 class의 SHAP distance나 importance shift가 커지면 그 class에 한정된 모델 기여 패턴 변화 후보로 본다.
- 주의점: class별 표본 수가 작거나 class imbalance가 커지면 SHAP 변화와 label shift 영향을 분리하기 어렵다.
- 보고서 문장 예시: "Class-conditional SHAP 분석에서 특정 class의 feature 기여 패턴이 기준과 다르게 이동한 후보가 확인되었다."

---

## SelectionRule 카탈로그

```text
selectionRule SHAP_DRIFT_DEFAULT_USE
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

> SHAP Drift 카탈로그는 "이 방법이 무엇인가"가 아니라, "어떤 상황에서 어떤 변종을 선택하고 어떤 주의사항과 함께 설명해야 하는가"를 구조화한다.
