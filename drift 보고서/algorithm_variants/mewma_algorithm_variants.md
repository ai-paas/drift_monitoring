# MEWMA 알고리즘 변종 목록

## 1. 목적

이 문서는 `MEWMA`를 하나의 고정된 detector로 보지 않고, drift monitoring에서 상황에 따라 선택해야 하는 **알고리즘 변종들의 family**로 정리한다.

핵심 목적은 다음이다.

```text
상황 조건 -> 적절한 MEWMA 계열 변종 -> 출력 metric -> 주의사항 -> LLM 보고서 설명
```

---

## 2. MEWMA의 위치

```text
methodFamily MEWMA
       ├─ algorithmVariant MEWMA_STANDARD
       └─ algorithmVariant MEWMA_WITH_MAHALANOBIS_D2
```

`MEWMA`는 multivariate EWMA control chart 계열에 속한다. 여러 metric의 EWMA 벡터와 공분산 구조를 이용해 다변량 gradual drift를 감시한다.

---

## 3. 공통 개념

```text
methodFamily MEWMA
  purpose ->
    여러 metric의 EWMA 벡터와 공분산 구조를 이용해 다변량 gradual drift를 감시한다.

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

## 변종: MEWMA_STANDARD

여러 metric의 EWMA 벡터를 함께 추적해 다변량 평균 변화가 control limit을 넘는지 보는 기본 MEWMA 변종이다. 단일 지표로는 약하지만 여러 지표가 동시에 조금씩 움직이는 drift에 유용하다.

- 사용 상황: 성능 지표, feature 요약값, embedding summary처럼 서로 상관된 여러 신호를 함께 감시할 때 적합하다.
- 해석 방법: MEWMA statistic이 control limit을 넘으면 여러 신호의 누적 변화가 기준 공분산 구조에서 벗어난 후보로 본다.
- 주의점: 공분산 추정이 불안정하면 경보가 과민하거나 둔감해질 수 있으므로 reference window와 smoothing 계수를 함께 보고한다.
- 보고서 문장 예시: "MEWMA statistic이 관리한계를 초과해 여러 지표가 결합된 형태의 gradual drift 후보가 관측되었다."

---

## 변종: MEWMA_WITH_MAHALANOBIS_D2

MEWMA 벡터가 reference 중심에서 얼마나 멀어졌는지 Mahalanobis D2 형태로 해석하는 변종이다. 경보 여부뿐 아니라 다변량 거리 추세를 설명할 때 사용한다.

- 사용 상황: MEWMA 경보를 공분산 보정 거리로 설명하거나 기여 feature 분석과 연결해야 할 때 적합하다.
- 해석 방법: D2가 커질수록 EWMA로 누적된 current 상태가 reference 중심에서 멀어진 것으로 본다.
- 주의점: scale 정규화와 공분산 추정 방식에 따라 D2 크기가 달라지므로 서로 다른 설정의 값을 직접 비교하지 않는다.
- 보고서 문장 예시: "MEWMA의 Mahalanobis D2가 상승해 누적된 다변량 상태가 기준 중심에서 멀어지는 흐름을 보였다."

---

## SelectionRule 카탈로그

```text
selectionRule MEWMA_DEFAULT_USE
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

> MEWMA 카탈로그는 "이 방법이 무엇인가"가 아니라, "어떤 상황에서 어떤 변종을 선택하고 어떤 주의사항과 함께 설명해야 하는가"를 구조화한다.
