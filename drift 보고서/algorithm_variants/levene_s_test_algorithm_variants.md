# Levene's Test 알고리즘 변종 목록

## 1. 목적

이 문서는 `Levene's Test`를 하나의 고정된 detector로 보지 않고, drift monitoring에서 상황에 따라 선택해야 하는 **알고리즘 변종들의 family**로 정리한다.

핵심 목적은 다음이다.

```text
상황 조건 -> 적절한 Levene's Test 계열 변종 -> 출력 metric -> 주의사항 -> LLM 보고서 설명
```

---

## 2. Levene's Test의 위치

```text
methodFamily LEVENE_S_TEST
       ├─ algorithmVariant LEVENE_MEAN_CENTER
       ├─ algorithmVariant BROWN_FORSYTHE_MEDIAN_CENTER
       └─ algorithmVariant TRIMMED_MEAN_LEVENE
```

`Levene's Test`는 drift monitoring method 계열에 속한다. Levene's Test 계열을 drift monitoring 문맥에서 입력 데이터와 운영 목적에 따라 선택 가능한 변종으로 정리한다.

---

## 3. 공통 개념

```text
methodFamily LEVENE_S_TEST
  purpose ->
    Levene's Test 계열을 drift monitoring 문맥에서 입력 데이터와 운영 목적에 따라 선택 가능한 변종으로 정리한다.

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

## 변종: LEVENE_MEAN_CENTER

평균을 중심값으로 삼아 각 그룹의 절대 편차를 비교하는 기본 Levene 검정이다. Reference와 current 구간의 분산 또는 변동성이 달라졌는지 확인할 때 사용한다.

- 사용 상황: 수치형 feature의 평균 주변 변동성 변화가 운영상 중요한 경우에 적합하다.
- 해석 방법: p-value가 작거나 검정 통계량이 커지면 두 기간의 분산이 같다는 가설을 기각하는 방향의 신호로 본다.
- 주의점: 평균 중심 방식은 outlier와 비대칭 분포에 민감하므로 heavy-tail 데이터에서는 Brown-Forsythe 변종과 함께 확인한다.
- 보고서 문장 예시: "평균 중심 Levene 검정에서 current 구간의 변동성이 reference와 달라졌다는 분산 drift 후보 신호가 관측되었다."

---

## 변종: BROWN_FORSYTHE_MEDIAN_CENTER

중앙값을 중심값으로 사용하는 Levene 계열 변종이다. 이상치나 긴 꼬리 분포 때문에 평균 중심 검정이 흔들릴 수 있는 feature의 분산 drift 확인에 사용한다.

- 사용 상황: 청구 금액, 지연 시간, 사용량처럼 일부 큰 값이 자주 섞이는 수치형 feature에 적합하다.
- 해석 방법: 중앙값 기준 절대 편차의 차이가 커지고 p-value가 낮으면 reference와 current의 변동성 구조가 달라졌다고 본다.
- 주의점: 중앙값 중심은 robust하지만 분산 변화의 방향과 원인을 직접 알려주지는 않는다.
- 보고서 문장 예시: "Brown-Forsythe 검정은 이상치 영향을 줄인 조건에서도 current 구간 변동성 변화가 남아 있음을 시사한다."

---

## 변종: TRIMMED_MEAN_LEVENE

일부 극단값을 절단한 평균을 중심값으로 쓰는 Levene 변종이다. 평균 중심과 중앙값 중심의 중간 성격으로, outlier 영향을 줄이면서도 평균 주변 변동성 변화를 보고 싶을 때 사용한다.

- 사용 상황: extreme value가 일부 존재하지만 중앙값만으로는 변화 민감도가 부족한 수치형 feature에 적합하다.
- 해석 방법: 절단 평균 기준 편차의 그룹 차이가 유의하면 current 구간의 분산 또는 scale 변화 후보로 해석한다.
- 주의점: trimming 비율을 바꾸면 결과가 달라질 수 있으므로 보고서에 절단 정책을 함께 남긴다.
- 보고서 문장 예시: "절단 평균 Levene 검정은 극단값 일부를 제외한 후에도 변동성 drift 후보가 유지되는지 확인하는 보조 검정으로 사용했다."

---

## SelectionRule 카탈로그

```text
selectionRule LEVENE_S_TEST_DEFAULT_USE
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

> Levene's Test 카탈로그는 "이 방법이 무엇인가"가 아니라, "어떤 상황에서 어떤 변종을 선택하고 어떤 주의사항과 함께 설명해야 하는가"를 구조화한다.
