# Epps-Singleton Test 알고리즘 변종 목록

## 1. 목적

이 문서는 `Epps-Singleton Test`를 하나의 고정된 detector로 보지 않고, drift monitoring에서 상황에 따라 선택해야 하는 **알고리즘 변종들의 family**로 정리한다.

핵심 목적은 다음이다.

```text
상황 조건 -> 적절한 Epps-Singleton Test 계열 변종 -> 출력 metric -> 주의사항 -> LLM 보고서 설명
```

---

## 2. Epps-Singleton Test의 위치

```text
methodFamily EPPS_SINGLETON_TEST
       ├─ algorithmVariant TWO_SAMPLE_EPPS_SINGLETON
       ├─ algorithmVariant DISCRETE_EPPS_SINGLETON
       └─ algorithmVariant ASYMPTOTIC_EPPS_SINGLETON
```

`Epps-Singleton Test`는 drift monitoring method 계열에 속한다. Epps-Singleton Test 계열을 drift monitoring 문맥에서 입력 데이터와 운영 목적에 따라 선택 가능한 변종으로 정리한다.

---

## 3. 공통 개념

```text
methodFamily EPPS_SINGLETON_TEST
  purpose ->
    Epps-Singleton Test 계열을 drift monitoring 문맥에서 입력 데이터와 운영 목적에 따라 선택 가능한 변종으로 정리한다.

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

## 변종: TWO_SAMPLE_EPPS_SINGLETON

`TWO_SAMPLE_EPPS_SINGLETON`은 reference 표본과 current 표본이 같은 분포에서 왔는지 Epps-Singleton 검정으로 비교하는 기본 두 표본 변종이다. 평균만 비교하는 것이 아니라 경험적 특성함수 기반으로 분포 모양 차이를 보므로, 위치 변화와 형태 변화 후보를 함께 감지하는 데 쓴다. 출력은 test statistic, p-value, 설정한 유의수준 또는 threshold 기준의 alarm 여부로 해석한다.

사용 상황:
- reference/current 두 기간의 수치형 표본을 직접 비교할 수 있을 때
- 평균 차이뿐 아니라 분산, 꼬리, 분포 형태 변화까지 보고 싶을 때
- KS 검정만으로는 민감도가 충분하지 않거나 discrete/continuous 특성이 섞인 지표를 보조 검정으로 확인할 때

해석 방법:
- test statistic이 클수록 두 표본의 분포 차이를 설명하는 근거가 커진다.
- p-value가 작으면 두 기간이 같은 분포라는 가설을 기각할 근거가 강하다는 뜻이다.
- p-value는 통계적 유의성이고, 실제 운영 영향은 분포 차이의 크기와 지표 의미를 따로 봐야 한다.
- 여러 지표에 반복 적용할 경우 유의한 지표 수와 effect size 요약을 함께 제시한다.

주의점:
- 표본 수가 작으면 검정력이 낮아 실제 차이가 있어도 유의하지 않을 수 있다.
- 표본 수가 매우 크면 작은 차이도 유의해질 수 있으므로 p-value만으로 drift 강도를 말하지 않는다.
- reference/current 기간의 수집 조건, 결측 처리, 전처리 방식이 다르면 검정 결과가 운영 변화가 아닌 측정 조건 차이를 반영할 수 있다.

보고서 문장 예시:

```text
reference/current 표본을 TWO_SAMPLE_EPPS_SINGLETON으로 비교한 결과,
test statistic과 p-value가 두 기간의 분포 차이 가능성을 시사했다.
이는 해당 수치 지표에서 분포 변화 후보가 관측됐다는 의미로 해석할 수 있다.
다만 p-value는 유의성 지표이므로, 실제 영향은 effect size와 지표의 업무 의미를 함께 검토해야 한다.
```

---

## 변종: DISCRETE_EPPS_SINGLETON

`DISCRETE_EPPS_SINGLETON`은 값이 몇 개의 구간이나 정수형 수준에 모이는 지표를 reference/current 두 표본으로 비교하는 Epps-Singleton 변종이다. 연속형이라고 가정하기 어려운 카운트, 등급, bucketized score처럼 동점과 반복값이 많은 신호에서 분포 변화 후보를 확인하는 데 적합하다. 검정 결과는 discrete 입력에서 두 기간의 값 분포가 얼마나 달라졌는지를 보여주는 보조 통계로 읽는다.

사용 상황:
- 이벤트 수, 요청 횟수, 오류 건수처럼 정수형 또는 카운트형 지표를 기간별로 비교할 때
- score가 구간화되어 있거나 등급, 단계, bucket 값으로 저장되어 동점이 많이 발생할 때
- 범주형 라벨 자체보다는 순서나 크기 의미가 있는 discrete 수치 신호의 분포 변화를 보고 싶을 때

해석 방법:
- test statistic이 클수록 reference와 current의 discrete 값 분포가 서로 다르다는 근거가 커진다.
- p-value가 작으면 두 기간이 같은 분포라는 가설을 기각할 통계적 근거가 강하다는 뜻이다.
- alarm은 설정한 유의수준이나 운영 threshold를 넘었는지에 대한 표시이며, 그 자체가 원인 확정은 아니다.
- 특정 값 구간의 빈도 변화와 함께 보면 어떤 discrete 수준에서 변화가 집중됐는지 설명하기 쉽다.

주의점:
- 값의 종류가 너무 적거나 한 값에 관측치가 몰리면 검정 결과가 일부 빈도 변화에 크게 좌우될 수 있다.
- 표본 수가 작으면 p-value가 불안정할 수 있으므로 구간별 빈도표나 비율 차이를 함께 확인한다.
- discrete 값의 정의나 bucket 경계가 reference/current 사이에서 바뀌면 분포 변화가 운영 변화가 아니라 전처리 변경을 반영할 수 있다.

보고서 문장 예시:

```text
정수형 또는 구간화된 입력 지표를 DISCRETE_EPPS_SINGLETON으로 비교한 결과,
test statistic과 p-value가 reference/current 값 분포의 차이 가능성을 보였다.
이는 특정 discrete 수준의 빈도 구성이 달라졌다는 drift 후보 신호로 해석할 수 있다.
다만 bucket 정의와 표본 수의 영향을 받을 수 있으므로, 값별 비율 변화와 전처리 변경 여부를 함께 확인해야 한다.
```

---

## 변종: ASYMPTOTIC_EPPS_SINGLETON

`ASYMPTOTIC_EPPS_SINGLETON`은 충분한 표본에서 Epps-Singleton 검정통계량의 근사 분포를 사용해 reference/current 차이를 판단하는 변종이다. permutation이나 bootstrap을 매번 돌리기 어려운 대량 모니터링에서 빠르게 p-value와 alarm을 산출하는 데 쓴다. 핵심은 계산 효율이지만, 근사 p-value가 신뢰되려면 표본 수와 입력 분포 조건이 뒷받침되어야 한다.

사용 상황:
- 비교할 feature나 window가 많아 반복 검정을 빠르게 수행해야 할 때
- reference/current 표본 수가 근사 검정을 사용할 만큼 충분히 확보되어 있을 때
- 운영 대시보드나 배치 리포트에서 일관된 유의수준 기준으로 drift 후보를 선별할 때

해석 방법:
- test statistic은 두 표본의 경험적 특성함수 차이를 요약한 값이며, 값이 클수록 분포 차이 근거가 커진다.
- p-value는 asymptotic 근사를 통해 계산된 통계적 유의성 지표로 읽는다.
- alarm은 p-value 또는 statistic이 운영 기준을 넘었는지 나타내며, 여러 지표를 screening한 뒤 우선순위를 정하는 데 사용할 수 있다.
- 유의한 결과가 많을 때는 단일 p-value보다 반복 검정 수, effect size, 영향을 받는 feature 묶음을 함께 해석한다.

주의점:
- 표본 수가 작거나 분포가 매우 치우친 경우 asymptotic p-value가 실제 유의수준과 어긋날 수 있다.
- 대규모 표본에서는 작은 차이도 유의하게 나올 수 있으므로 p-value만으로 drift 강도를 표현하지 않는다.
- 많은 feature에 동시에 적용하면 우연히 유의한 결과가 늘어날 수 있어 다중 비교 보정이나 후속 검토 기준이 필요하다.

보고서 문장 예시:

```text
reference/current window를 ASYMPTOTIC_EPPS_SINGLETON으로 screening한 결과,
근사 p-value와 test statistic이 일부 지표에서 분포 변화 후보를 가리켰다.
이는 대량 모니터링에서 우선 확인할 feature를 좁히는 신호로 볼 수 있다.
다만 표본 수와 다중 검정 영향을 받으므로, effect size와 후속 검정을 함께 검토해야 한다.
```

---

## SelectionRule 카탈로그

```text
selectionRule EPPS_SINGLETON_TEST_DEFAULT_USE
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

> Epps-Singleton Test 카탈로그는 "이 방법이 무엇인가"가 아니라, "어떤 상황에서 어떤 변종을 선택하고 어떤 주의사항과 함께 설명해야 하는가"를 구조화한다.
