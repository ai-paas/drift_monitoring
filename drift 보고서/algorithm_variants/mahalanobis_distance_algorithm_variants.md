# Mahalanobis Distance 알고리즘 변종 목록

## 1. 목적

이 문서는 `Mahalanobis Distance`를 하나의 고정된 detector로 보지 않고, drift monitoring에서 상황에 따라 선택해야 하는 **알고리즘 변종들의 family**로 정리한다.

핵심 목적은 다음이다.

```text
상황 조건 -> 적절한 Mahalanobis Distance 계열 변종 -> 출력 metric -> 주의사항 -> LLM 보고서 설명
```

---

## 2. Mahalanobis Distance의 위치

```text
methodFamily MAHALANOBIS_DISTANCE
       ├─ algorithmVariant SAMPLE_MAHALANOBIS_OUTLIER
       ├─ algorithmVariant WINDOW_MEAN_MAHALANOBIS
       └─ algorithmVariant ROBUST_MAHALANOBIS
```

`Mahalanobis Distance`는 covariance-aware distance 계열에 속한다. 기준 평균과 공분산을 고려해 샘플 또는 window가 얼마나 벗어났는지 측정한다.

---

## 3. 공통 개념

```text
methodFamily MAHALANOBIS_DISTANCE
  purpose ->
    기준 평균과 공분산을 고려해 샘플 또는 window가 얼마나 벗어났는지 측정한다.

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

## 변종: SAMPLE_MAHALANOBIS_OUTLIER

개별 샘플이 reference 평균과 공분산 구조에서 얼마나 멀리 떨어져 있는지 Mahalanobis distance로 측정하는 변종이다. 샘플 단위 outlier screening에 초점을 둔다.

- 사용 상황: 다변량 feature 조합상 드문 관측치가 증가하는지 모니터링할 때 적합하다.
- 해석 방법: 개별 distance가 threshold를 넘으면 해당 샘플이 reference 분포의 정상 타원 영역 밖에 있을 가능성이 높다고 본다.
- 주의점: 개별 outlier가 발생했다고 곧바로 전체 분포 drift로 단정하지 말고 window 단위 빈도와 함께 본다.
- 보고서 문장 예시: "Mahalanobis outlier 점수 기준으로 current 구간에서 reference 공분산 구조와 맞지 않는 샘플 후보가 증가했다."

---

## 변종: WINDOW_MEAN_MAHALANOBIS

Current window의 평균 벡터가 reference 평균에서 얼마나 벗어났는지 공분산을 고려해 계산하는 변종이다. 개별 샘플보다 기간 단위 평균 이동을 본다.

- 사용 상황: 여러 feature가 함께 움직이는 평균 shift를 감지하거나 Hotelling T2 결과를 직관적 거리로 설명할 때 적합하다.
- 해석 방법: window D2가 커지거나 threshold를 넘으면 current window 평균이 reference의 다변량 중심에서 이탈한 후보로 본다.
- 주의점: window 크기가 작으면 평균 추정이 불안정하고, 공분산 역행렬 추정이 나쁘면 거리가 과장될 수 있다.
- 보고서 문장 예시: "Window 평균 Mahalanobis distance가 기준선을 넘어 current 기간의 다변량 평균 이동 후보가 관측되었다."

---

## 변종: ROBUST_MAHALANOBIS

Robust covariance estimator를 사용해 outlier가 reference 평균과 공분산을 왜곡하는 영향을 줄인 Mahalanobis 변종이다.

- 사용 상황: 기준 기간에도 일부 이상치가 섞여 있거나 classical covariance가 불안정한 feature 세트에 적합하다.
- 해석 방법: robust D2가 커지면 outlier 영향을 완화한 기준에서도 current 관측치 또는 window가 멀어졌다고 본다.
- 주의점: robust estimator 종류와 contamination 가정에 따라 결과가 달라지므로 classical distance와 단순 수치 비교를 피한다.
- 보고서 문장 예시: "Robust Mahalanobis distance 기준에서도 current 구간의 이탈 신호가 유지되어 기준 기간 outlier만으로 설명되기 어렵다."

---

## SelectionRule 카탈로그

```text
selectionRule MAHALANOBIS_DISTANCE_DEFAULT_USE
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

> Mahalanobis Distance 카탈로그는 "이 방법이 무엇인가"가 아니라, "어떤 상황에서 어떤 변종을 선택하고 어떤 주의사항과 함께 설명해야 하는가"를 구조화한다.
