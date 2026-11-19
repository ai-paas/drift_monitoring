# t-test 알고리즘 변종 목록

## 1. 목적

이 문서는 `t-test`를 하나의 고정된 detector로 보지 않고, drift monitoring에서 상황에 따라 선택해야 하는 **알고리즘 변종들의 family**로 정리한다.

핵심 목적은 다음이다.

```text
상황 조건 -> 적절한 t-test 계열 변종 -> 출력 metric -> 주의사항 -> LLM 보고서 설명
```

---

## 2. t-test의 위치

```text
methodFamily T_TEST
       ├─ algorithmVariant ONE_SAMPLE_T_TEST
       ├─ algorithmVariant TWO_SAMPLE_STUDENT_T_TEST
       ├─ algorithmVariant WELCH_T_TEST
       └─ algorithmVariant PAIRED_T_TEST
```

`t-test`는 drift monitoring method 계열에 속한다. t-test 계열을 drift monitoring 문맥에서 입력 데이터와 운영 목적에 따라 선택 가능한 변종으로 정리한다.

---

## 3. 공통 개념

```text
methodFamily T_TEST
  purpose ->
    t-test 계열을 drift monitoring 문맥에서 입력 데이터와 운영 목적에 따라 선택 가능한 변종으로 정리한다.

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

## 변종: ONE_SAMPLE_T_TEST

Current window의 평균이 사전에 정한 기준 평균 또는 reference 평균과 다른지 검정하는 단일표본 t-test 변종이다.

- 사용 상황: 기준 평균이 명확한 latency, score, loss 등 수치형 metric의 평균 이동을 확인할 때 적합하다.
- 해석 방법: p-value가 낮고 평균 차이가 운영상 의미 있는 방향이면 평균 drift 후보로 본다.
- 주의점: 표본 독립성, 정규성 근사, outlier 영향을 확인해야 하며 기준 평균의 산정 기간을 명시한다.
- 보고서 문장 예시: "단일표본 t-test에서 current 평균이 기준 평균과 유의하게 달라져 평균 drift 후보가 관측되었다."

---

## 변종: TWO_SAMPLE_STUDENT_T_TEST

Reference와 current 두 독립 표본의 평균을 비교하고, 두 집단의 분산이 같다고 가정하는 Student two-sample t-test 변종이다.

- 사용 상황: 두 기간의 sample size와 분산이 비슷하고 평균 shift를 단순하게 확인할 때 적합하다.
- 해석 방법: 검정 통계량과 p-value가 평균 차이를 지지하면 current 평균이 reference와 달라진 후보로 본다.
- 주의점: 등분산 가정이 맞지 않으면 Welch t-test를 우선 검토한다.
- 보고서 문장 예시: "Student two-sample t-test에서 current 평균이 reference와 달라진 평균 drift 후보가 확인되었다."

---

## 변종: WELCH_T_TEST

Reference와 current의 분산이 다를 수 있다고 보고 자유도를 보정해 평균 차이를 검정하는 Welch t-test 변종이다.

- 사용 상황: 두 기간의 분산이나 표본 수가 다르고, 평균 shift를 비교해야 할 때 적합하다.
- 해석 방법: Welch p-value가 낮으면 등분산을 가정하지 않아도 평균 차이가 있다는 drift 후보로 해석한다.
- 주의점: heavy-tail 또는 강한 outlier가 있으면 순위 기반 검정이나 robust 통계를 함께 확인한다.
- 보고서 문장 예시: "Welch t-test는 분산 차이를 허용한 조건에서도 current 평균 변화 후보가 유지됨을 보여준다."

---

## 변종: PAIRED_T_TEST

동일한 대상, 동일한 query, 또는 매칭된 샘플의 before/after 차이를 비교하는 paired t-test 변종이다. 독립 표본이 아니라 짝지어진 차이의 평균을 검정한다.

- 사용 상황: 같은 사용자군, 같은 item, 같은 입력에 대해 reference와 current 값이 대응될 때 적합하다.
- 해석 방법: 짝별 차이의 평균이 0과 유의하게 다르면 매칭 조건에서 평균 변화 후보가 있다고 본다.
- 주의점: 잘못 매칭된 샘플을 paired로 처리하면 결과가 왜곡되므로 pairing 기준을 보고서에 남긴다.
- 보고서 문장 예시: "Paired t-test에서 매칭 샘플의 평균 차이가 유의하게 나타나 동일 대상 기준의 변화 후보가 확인되었다."

---

## SelectionRule 카탈로그

```text
selectionRule T_TEST_DEFAULT_USE
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

> t-test 카탈로그는 "이 방법이 무엇인가"가 아니라, "어떤 상황에서 어떤 변종을 선택하고 어떤 주의사항과 함께 설명해야 하는가"를 구조화한다.
