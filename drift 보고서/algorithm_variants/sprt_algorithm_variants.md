# SPRT 알고리즘 변종 목록

## 1. 목적

이 문서는 `SPRT`를 하나의 고정된 detector로 보지 않고, drift monitoring에서 상황에 따라 선택해야 하는 **알고리즘 변종들의 family**로 정리한다.

핵심 목적은 다음이다.

```text
상황 조건 -> 적절한 SPRT 계열 변종 -> 출력 metric -> 주의사항 -> LLM 보고서 설명
```

---

## 2. SPRT의 위치

```text
methodFamily SPRT
       ├─ algorithmVariant SPRT_BERNOULLI_ERROR_RATE
       └─ algorithmVariant SPRT_GAUSSIAN_MEAN_SHIFT
```

`SPRT`는 Sequential Probability Ratio Test 계열에 속한다. 순차적으로 들어오는 관측값으로 두 가설의 likelihood ratio가 경계에 도달하는지 판단한다.

---

## 3. 공통 개념

```text
methodFamily SPRT
  purpose ->
    순차적으로 들어오는 관측값으로 두 가설의 likelihood ratio가 경계에 도달하는지 판단한다.

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

## 변종: SPRT_BERNOULLI_ERROR_RATE

오류 여부를 Bernoulli stream으로 보고, 오류율이 사전에 정의한 대립가설 수준으로 증가했는지 순차 likelihood ratio로 검정하는 SPRT 변종이다.

- 사용 상황: online performance guardrail, canary 배포, A/B 모니터링에서 오류율 악화를 빠르게 판정해야 할 때 적합하다.
- 해석 방법: log-likelihood ratio가 상단 경계에 도달하면 H1 오류율 쪽 근거가 충분하다고 보고, 하단 경계에 도달하면 H0 유지로 본다.
- 주의점: H0/H1 오류율, alpha, beta를 사전에 정해야 하며, 결과를 본 뒤 가설을 바꾸면 순차 검정의 의미가 깨진다.
- 보고서 문장 예시: "Bernoulli SPRT가 사전 정의한 오류율 증가 가설의 경계에 도달해 online 성능 악화 후보를 알렸다."

---

## 변종: SPRT_GAUSSIAN_MEAN_SHIFT

정규 근사가 가능한 numeric metric의 평균이 지정한 크기만큼 이동했는지 순차적으로 검정하는 SPRT 변종이다.

- 사용 상황: latency, loss, score summary처럼 연속형 metric의 평균 변화 크기를 사전에 정의할 수 있을 때 적합하다.
- 해석 방법: log-likelihood ratio가 decision boundary를 넘으면 설정한 평균 shift 가설에 대한 순차 근거가 충분하다고 본다.
- 주의점: 분산 추정과 평균 shift 크기 가정이 결과를 좌우하며, heavy-tail 분포에서는 false alarm 가능성이 커진다.
- 보고서 문장 예시: "Gaussian SPRT가 정의된 평균 shift 경계에 도달해 numeric metric의 순차 변화 후보를 감지했다."

---

## SelectionRule 카탈로그

```text
selectionRule SPRT_DEFAULT_USE
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

> SPRT 카탈로그는 "이 방법이 무엇인가"가 아니라, "어떤 상황에서 어떤 변종을 선택하고 어떤 주의사항과 함께 설명해야 하는가"를 구조화한다.
