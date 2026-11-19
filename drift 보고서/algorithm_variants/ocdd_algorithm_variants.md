# OCDD 알고리즘 변종 목록

## 1. 목적

이 문서는 `OCDD`를 하나의 고정된 detector로 보지 않고, drift monitoring에서 상황에 따라 선택해야 하는 **알고리즘 변종들의 family**로 정리한다.

핵심 목적은 다음이다.

```text
상황 조건 -> 적절한 OCDD 계열 변종 -> 출력 metric -> 주의사항 -> LLM 보고서 설명
```

---

## 2. OCDD의 위치

```text
methodFamily OCDD
       ├─ algorithmVariant ONE_CLASS_SVM_DRIFT
       ├─ algorithmVariant ISOLATION_FOREST_DRIFT_SCORE
       └─ algorithmVariant AUTOENCODER_RECONSTRUCTION_DRIFT
```

`OCDD`는 one-class drift/anomaly detector 계열에 속한다. 정상 기준으로 학습한 경계 밖 샘플 또는 anomaly score 증가를 drift 후보로 감지한다.

---

## 3. 공통 개념

```text
methodFamily OCDD
  purpose ->
    정상 기준으로 학습한 경계 밖 샘플 또는 anomaly score 증가를 drift 후보로 감지한다.

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

## 변종: ONE_CLASS_SVM_DRIFT

정상 reference feature vector로 one-class SVM 경계를 학습한 뒤 current 샘플이 경계 밖으로 나가는 비율을 감시하는 변종이다.

- 사용 상황: 라벨 없이 정상 입력 영역을 정의하고 out-of-distribution 샘플 증가를 감지할 때 적합하다.
- 해석 방법: anomaly score가 악화되거나 boundary violation rate가 높아지면 current 입력이 정상 기준 경계를 더 자주 벗어난다고 본다.
- 주의점: scale 전처리, `nu`, kernel `gamma` 설정에 매우 민감하므로 reference 기준 설정을 보고서에 남긴다.
- 보고서 문장 예시: "One-class SVM 기준에서 current 샘플의 정상 경계 이탈 비율이 증가해 OOD성 drift 후보가 관측되었다."

---

## 변종: ISOLATION_FOREST_DRIFT_SCORE

Isolation Forest로 계산한 anomaly score 분포와 outlier 비율이 current window에서 바뀌는지 보는 변종이다. 비선형 feature 공간의 이상 패턴 증가를 빠르게 screening한다.

- 사용 상황: 대용량 tabular feature나 embedding summary에서 labeled drift 검정 없이 이상 점수 추세를 보고 싶을 때 적합하다.
- 해석 방법: score 분포가 악화되거나 outlier rate가 상승하면 current 입력이 reference 정상 패턴과 다른 후보로 본다.
- 주의점: anomaly 증가는 drift 후보이지 원인 설명이 아니며, contamination 및 threshold calibration 이력을 함께 확인한다.
- 보고서 문장 예시: "Isolation Forest anomaly score 분포가 current window에서 악화되어 정상 패턴 밖 관측치 증가 후보가 확인되었다."

---

## 변종: AUTOENCODER_RECONSTRUCTION_DRIFT

정상 reference 데이터로 학습한 autoencoder의 reconstruction error를 current에서 추적하는 변종이다. 정상 표현으로 잘 복원되지 않는 입력 증가를 drift 후보로 본다.

- 사용 상황: 이미지, 센서, embedding, 고차원 feature처럼 비선형 정상 패턴을 압축 표현으로 학습할 수 있을 때 적합하다.
- 해석 방법: reconstruction error나 anomaly rate가 증가하면 current 입력이 학습된 정상 manifold에서 벗어났을 가능성이 높다고 본다.
- 주의점: 데이터 품질 문제, 입력 스케일 변경, autoencoder 재학습 이력이 error 증가처럼 보일 수 있다.
- 보고서 문장 예시: "Autoencoder reconstruction error가 기준보다 증가해 current 입력이 정상 표현으로 복원되기 어려운 drift 후보가 나타났다."

---

## SelectionRule 카탈로그

```text
selectionRule OCDD_DEFAULT_USE
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

> OCDD 카탈로그는 "이 방법이 무엇인가"가 아니라, "어떤 상황에서 어떤 변종을 선택하고 어떤 주의사항과 함께 설명해야 하는가"를 구조화한다.
