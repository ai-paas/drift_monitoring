# Page-Hinkley Test 알고리즘 변종 목록

## 1. 목적

이 문서는 `Page-Hinkley Test`를 하나의 고정된 detector로 보지 않고, drift monitoring에서 상황에 따라 선택해야 하는 **알고리즘 변종들의 family**로 정리한다.

핵심 목적은 다음이다.

```text
상황 조건 -> 적절한 Page-Hinkley Test 계열 변종 -> 출력 metric -> 주의사항 -> LLM 보고서 설명
```

---

## 2. Page-Hinkley Test의 위치

```text
methodFamily PAGE_HINKLEY_TEST
       ├─ algorithmVariant PAGE_HINKLEY_INCREASE
       └─ algorithmVariant PAGE_HINKLEY_DECREASE
```

`Page-Hinkley Test`는 sequential mean change detector 계열에 속한다. 평균의 누적 편차가 임계값을 넘는지 감시해 streaming mean shift를 감지한다.

---

## 3. 공통 개념

```text
methodFamily PAGE_HINKLEY_TEST
  purpose ->
    평균의 누적 편차가 임계값을 넘는지 감시해 streaming mean shift를 감지한다.

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

## 변종: PAGE_HINKLEY_INCREASE

Streaming metric의 평균이 기준보다 증가하는 방향으로 누적 편차를 쌓아 감시하는 Page-Hinkley 변종이다. 나빠지는 방향이 증가로 정의되는 metric에 사용한다.

- 사용 상황: loss, error rate, latency, anomaly rate처럼 값이 커질수록 위험한 지표의 평균 증가를 빠르게 감지할 때 적합하다.
- 해석 방법: PH statistic이 threshold를 넘으면 작은 증가가 누적되어 평균 상승 drift 후보가 발생한 것으로 본다.
- 주의점: `delta`와 threshold 설정이 민감도와 탐지 지연을 결정하므로 운영 기준과 함께 설명한다.
- 보고서 문장 예시: "Page-Hinkley 증가 방향 검정에서 누적 평균 상승 신호가 threshold를 넘어 성능 지표 악화 후보가 감지되었다."

---

## 변종: PAGE_HINKLEY_DECREASE

Streaming metric의 평균이 감소하는 방향으로 누적 편차를 감시하는 Page-Hinkley 변종이다. 나빠지는 방향이 하락으로 정의되는 metric에 사용한다.

- 사용 상황: confidence, recall, throughput, conversion rate처럼 값이 낮아질수록 위험한 지표의 평균 하락을 감지할 때 적합하다.
- 해석 방법: 감소 방향 PH statistic이 threshold를 넘으면 current 흐름에서 평균 하락이 누적되고 있다고 본다.
- 주의점: 어떤 metric은 하락이 개선일 수 있으므로 방향성과 비즈니스 의미를 사전에 고정해야 한다.
- 보고서 문장 예시: "Page-Hinkley 감소 방향 검정에서 confidence 평균 하락이 누적되어 drift 후보 알람이 발생했다."

---

## SelectionRule 카탈로그

```text
selectionRule PAGE_HINKLEY_TEST_DEFAULT_USE
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

> Page-Hinkley Test 카탈로그는 "이 방법이 무엇인가"가 아니라, "어떤 상황에서 어떤 변종을 선택하고 어떤 주의사항과 함께 설명해야 하는가"를 구조화한다.
