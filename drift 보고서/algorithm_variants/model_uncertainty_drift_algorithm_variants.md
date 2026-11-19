# Model Uncertainty Drift 알고리즘 변종 목록

## 1. 목적

이 문서는 `Model Uncertainty Drift`를 하나의 고정된 detector로 보지 않고, drift monitoring에서 상황에 따라 선택해야 하는 **알고리즘 변종들의 family**로 정리한다.

핵심 목적은 다음이다.

```text
상황 조건 -> 적절한 Model Uncertainty Drift 계열 변종 -> 출력 metric -> 주의사항 -> LLM 보고서 설명
```

---

## 2. Model Uncertainty Drift의 위치

```text
methodFamily MODEL_UNCERTAINTY_DRIFT
       ├─ algorithmVariant SOFTMAX_CONFIDENCE_DRIFT
       ├─ algorithmVariant ENTROPY_DRIFT
       └─ algorithmVariant PREDICTIVE_VARIANCE_DRIFT
```

`Model Uncertainty Drift`는 drift monitoring method 계열에 속한다. Model Uncertainty Drift 계열을 drift monitoring 문맥에서 입력 데이터와 운영 목적에 따라 선택 가능한 변종으로 정리한다.

---

## 3. 공통 개념

```text
methodFamily MODEL_UNCERTAINTY_DRIFT
  purpose ->
    Model Uncertainty Drift 계열을 drift monitoring 문맥에서 입력 데이터와 운영 목적에 따라 선택 가능한 변종으로 정리한다.

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

## 변종: SOFTMAX_CONFIDENCE_DRIFT

모델 예측의 최대 softmax confidence 분포가 reference와 current 사이에서 달라졌는지 보는 변종이다. 라벨 없이도 모델이 입력을 얼마나 확신하는지의 변화를 감시한다.

- 사용 상황: 분류 모델에서 current 입력에 대한 confidence가 전반적으로 낮아지거나 비정상적으로 높아지는지 확인할 때 적합하다.
- 해석 방법: confidence 평균, 분위수, 낮은 confidence 비율이 기준과 달라지면 입력 분포 또는 모델 신뢰도 변화 후보로 본다.
- 주의점: softmax confidence는 calibration이 나쁠 수 있으므로 실제 성능 저하를 확정하지 않는다.
- 보고서 문장 예시: "Current 구간에서 softmax confidence 분포가 기준과 달라져 모델 불확실성 drift 후보가 나타났다."

---

## 변종: ENTROPY_DRIFT

예측 확률분포의 entropy를 비교해 모델 불확실성이 증가하거나 감소했는지 감시하는 변종이다. 단일 confidence보다 전체 class 확률 분포의 퍼짐을 본다.

- 사용 상황: 다중 클래스 모델에서 current 입력이 여러 클래스 사이에 더 모호하게 분포하는지 확인할 때 적합하다.
- 해석 방법: entropy가 상승하면 예측 불확실성 증가, entropy가 하락하면 과도한 확신 또는 class mix 변화 후보로 해석한다.
- 주의점: class imbalance나 prior shift만으로도 entropy가 바뀔 수 있으므로 class별 분포와 함께 확인한다.
- 보고서 문장 예시: "예측 entropy가 기준 기간보다 상승해 current 입력에 대한 모델 판단이 더 불확실해진 후보 신호가 관측되었다."

---

## 변종: PREDICTIVE_VARIANCE_DRIFT

앙상블, MC dropout, Bayesian model 등에서 얻은 예측 variance를 비교하는 변종이다. 모델 내부 불확실성 또는 epistemic uncertainty 변화에 초점을 둔다.

- 사용 상황: 예측 반복값이나 여러 모델 출력이 있어 current 구간의 predictive variance를 계산할 수 있을 때 적합하다.
- 해석 방법: predictive variance가 커지면 모델이 current 입력 영역에 대해 덜 익숙하거나 더 불안정하게 예측하는 후보 신호로 본다.
- 주의점: variance 추정 방식과 sampling 횟수에 민감하며, regression target scale 변화와 구분해야 한다.
- 보고서 문장 예시: "Predictive variance가 증가해 current 구간에서 모델 예측 불확실성이 커진 drift 후보가 확인되었다."

---

## SelectionRule 카탈로그

```text
selectionRule MODEL_UNCERTAINTY_DRIFT_DEFAULT_USE
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

> Model Uncertainty Drift 카탈로그는 "이 방법이 무엇인가"가 아니라, "어떤 상황에서 어떤 변종을 선택하고 어떤 주의사항과 함께 설명해야 하는가"를 구조화한다.
