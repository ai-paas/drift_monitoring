# Mann-Whitney U Test 알고리즘 변종 목록

## 1. 목적

이 문서는 `Mann-Whitney U Test`를 하나의 고정된 detector로 보지 않고, drift monitoring에서 상황에 따라 선택해야 하는 **알고리즘 변종들의 family**로 정리한다.

핵심 목적은 다음이다.

```text
상황 조건 -> 적절한 Mann-Whitney U Test 계열 변종 -> 출력 metric -> 주의사항 -> LLM 보고서 설명
```

---

## 2. Mann-Whitney U Test의 위치

```text
methodFamily MANN_WHITNEY_U_TEST
       ├─ algorithmVariant MANN_WHITNEY_TWO_SIDED
       ├─ algorithmVariant MANN_WHITNEY_ONE_SIDED
       └─ algorithmVariant MANN_WHITNEY_EXACT
```

`Mann-Whitney U Test`는 drift monitoring method 계열에 속한다. Mann-Whitney U Test 계열을 drift monitoring 문맥에서 입력 데이터와 운영 목적에 따라 선택 가능한 변종으로 정리한다.

---

## 3. 공통 개념

```text
methodFamily MANN_WHITNEY_U_TEST
  purpose ->
    Mann-Whitney U Test 계열을 drift monitoring 문맥에서 입력 데이터와 운영 목적에 따라 선택 가능한 변종으로 정리한다.

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

## 변종: MANN_WHITNEY_TWO_SIDED

Reference와 current의 순위 분포가 양방향으로 달라졌는지 확인하는 Mann-Whitney U 기본 변종이다. 평균 대신 median 또는 위치 분포 차이를 비모수적으로 감지한다.

- 사용 상황: 수치형 feature가 정규성을 만족하지 않거나 outlier가 있어 t-test보다 순위 기반 비교가 적절할 때 사용한다.
- 해석 방법: p-value가 낮으면 current 값들이 reference보다 전반적으로 크거나 작아졌을 가능성을 포함한 분포 위치 변화 후보로 본다.
- 주의점: 두 집단의 분포 모양이 크게 다르면 단순 median shift로만 해석하기 어렵다.
- 보고서 문장 예시: "양측 Mann-Whitney U 검정에서 reference와 current의 순위 분포 차이가 나타나 수치형 feature drift 후보로 판단했다."

---

## 변종: MANN_WHITNEY_ONE_SIDED

Reference 대비 current가 증가 또는 감소하는 특정 방향의 순위 이동을 검정하는 Mann-Whitney U 변종이다. 운영상 관심 방향이 사전에 정해져 있을 때 사용한다.

- 사용 상황: 지연 시간 증가, 비용 상승, 점수 하락처럼 한쪽 방향의 변화만 경보 의미가 있을 때 적합하다.
- 해석 방법: 사전에 정한 방향의 p-value가 낮으면 current 분포가 그 방향으로 이동했다는 후보 신호로 본다.
- 주의점: 결과를 본 뒤 방향을 선택하면 유의성이 과장되므로 방향 가설은 분석 전에 고정해야 한다.
- 보고서 문장 예시: "단측 Mann-Whitney U 검정은 current 값이 기준 기간보다 증가한 방향의 순위 이동 후보를 보여준다."

---

## 변종: MANN_WHITNEY_EXACT

작은 표본에서 asymptotic 근사 대신 exact p-value를 사용하는 Mann-Whitney U 변종이다. 표본 수가 적어 근사 검정의 신뢰가 낮을 때 선택한다.

- 사용 상황: reference나 current window가 작고 순위 tie가 많지 않은 수치형 feature 비교에 적합하다.
- 해석 방법: exact p-value가 낮으면 작은 표본 조건에서도 두 기간 순위 분포가 다르다는 후보 신호로 해석한다.
- 주의점: tie가 많거나 표본이 커지면 exact 계산이 제한되거나 다른 보정 방식이 필요할 수 있다.
- 보고서 문장 예시: "작은 window 조건에서는 exact Mann-Whitney U 검정으로 근사 오차를 줄여 순위 분포 drift 후보를 확인했다."

---

## SelectionRule 카탈로그

```text
selectionRule MANN_WHITNEY_U_TEST_DEFAULT_USE
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

> Mann-Whitney U Test 카탈로그는 "이 방법이 무엇인가"가 아니라, "어떤 상황에서 어떤 변종을 선택하고 어떤 주의사항과 함께 설명해야 하는가"를 구조화한다.
