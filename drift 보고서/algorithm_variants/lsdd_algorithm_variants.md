# LSDD 알고리즘 변종 목록

## 1. 목적

이 문서는 `LSDD`를 하나의 고정된 detector로 보지 않고, drift monitoring에서 상황에 따라 선택해야 하는 **알고리즘 변종들의 family**로 정리한다.

핵심 목적은 다음이다.

```text
상황 조건 -> 적절한 LSDD 계열 변종 -> 출력 metric -> 주의사항 -> LLM 보고서 설명
```

---

## 2. LSDD의 위치

```text
methodFamily LSDD
       ├─ algorithmVariant LEAST_SQUARES_DENSITY_DIFFERENCE
       ├─ algorithmVariant LSDD_WITH_PREPROCESSING
       └─ algorithmVariant PERMUTATION_LSDD
```

`LSDD`는 drift monitoring method 계열에 속한다. LSDD 계열을 drift monitoring 문맥에서 입력 데이터와 운영 목적에 따라 선택 가능한 변종으로 정리한다.

---

## 3. 공통 개념

```text
methodFamily LSDD
  purpose ->
    LSDD 계열을 drift monitoring 문맥에서 입력 데이터와 운영 목적에 따라 선택 가능한 변종으로 정리한다.

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

## 변종: LEAST_SQUARES_DENSITY_DIFFERENCE

Reference와 current의 확률밀도 차이를 least-squares 방식으로 직접 추정하는 기본 LSDD 변종이다. 분포 전체의 차이를 하나의 거리 점수로 요약한다.

- 사용 상황: 수치형 또는 embedding feature에서 두 기간의 전체 분포 차이를 비모수적으로 감지하고 싶을 때 적합하다.
- 해석 방법: LSDD score가 커지면 current 분포가 reference 밀도와 더 멀어졌다는 drift 후보 신호로 본다.
- 주의점: kernel 폭, regularization, reference 표본 수에 민감하므로 threshold 산정 근거를 함께 남긴다.
- 보고서 문장 예시: "LSDD 점수가 상승해 current 구간의 feature 분포가 reference 밀도와 달라진 후보 신호가 확인되었다."

---

## 변종: LSDD_WITH_PREPROCESSING

Scaling, dimension reduction, embedding projection 같은 전처리를 거친 feature 공간에서 LSDD를 계산하는 변종이다. 원본 feature가 고차원이거나 scale 차이가 큰 경우에 사용한다.

- 사용 상황: feature scale이 제각각이거나 PCA, autoencoder, embedding 등 압축 표현에서 drift를 감지할 때 적합하다.
- 해석 방법: 동일한 전처리 파이프라인을 reference와 current에 적용한 뒤 LSDD score 변화로 분포 차이를 판단한다.
- 주의점: 전처리 모델을 current 데이터로 다시 학습하면 drift 신호가 희석되거나 왜곡될 수 있다.
- 보고서 문장 예시: "동일한 전처리 공간에서 계산한 LSDD가 증가해 압축 feature 분포의 drift 후보가 관측되었다."

---

## 변종: PERMUTATION_LSDD

Reference/current label을 섞는 permutation 절차로 LSDD score의 유의성을 추정하는 변종이다. 거리 점수 자체보다 통계적 유의성을 함께 보고해야 할 때 사용한다.

- 사용 상황: 운영 threshold가 아직 안정화되지 않았거나 표본 크기에 따른 LSDD score 변동을 보정해야 할 때 적합하다.
- 해석 방법: 관측 LSDD가 permutation null distribution의 상위 영역에 있으면 두 기간 분포 차이가 우연 수준을 넘는 후보로 본다.
- 주의점: permutation 횟수가 적으면 p-value 해상도가 낮고, 큰 데이터에서는 계산 비용이 커질 수 있다.
- 보고서 문장 예시: "Permutation LSDD에서 관측 거리 점수가 무작위 재배치 기준보다 커 분포 drift 후보의 통계적 근거가 확인되었다."

---

## SelectionRule 카탈로그

```text
selectionRule LSDD_DEFAULT_USE
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

> LSDD 카탈로그는 "이 방법이 무엇인가"가 아니라, "어떤 상황에서 어떤 변종을 선택하고 어떤 주의사항과 함께 설명해야 하는가"를 구조화한다.
