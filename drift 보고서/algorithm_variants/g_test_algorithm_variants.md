# G-test 알고리즘 변종 목록

## 1. 목적

이 문서는 `G-test`를 하나의 고정된 detector로 보지 않고, drift monitoring에서 상황에 따라 선택해야 하는 **알고리즘 변종들의 family**로 정리한다.

핵심 목적은 다음이다.

```text
상황 조건 -> 적절한 G-test 계열 변종 -> 출력 metric -> 주의사항 -> LLM 보고서 설명
```

---

## 2. G-test의 위치

```text
methodFamily G_TEST
       ├─ algorithmVariant LIKELIHOOD_RATIO_G_TEST_GOF
       ├─ algorithmVariant LIKELIHOOD_RATIO_G_TEST_INDEPENDENCE
       └─ algorithmVariant G_TEST_WITH_SMALL_COUNT_CAUTION
```

`G-test`는 drift monitoring method 계열에 속한다. G-test 계열을 drift monitoring 문맥에서 입력 데이터와 운영 목적에 따라 선택 가능한 변종으로 정리한다.

---

## 3. 공통 개념

```text
methodFamily G_TEST
  purpose ->
    G-test 계열을 drift monitoring 문맥에서 입력 데이터와 운영 목적에 따라 선택 가능한 변종으로 정리한다.

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

## 변종: LIKELIHOOD_RATIO_G_TEST_GOF

`LIKELIHOOD_RATIO_G_TEST_GOF`는 관측 category 빈도가 기대 분포와 얼마나 다른지 likelihood ratio statistic으로 평가하는 goodness-of-fit 변종이다. Chi-square goodness-of-fit과 비슷한 목적이지만, 로그 likelihood 기반으로 관측 빈도와 기대 빈도의 괴리를 요약한다. 출력은 G statistic, p-value, category별 기여도, alarm state로 해석한다.

사용 상황:
- current category 분포가 기준 비율, 정책상 기대 비율, 과거 reference 비율과 달라졌는지 확인할 때
- 유입 채널, 지역, 기기, 오류 유형처럼 범주형 구성 변화가 중요한 monitoring에서
- chi-square 결과와 함께 likelihood ratio 관점의 보조 근거를 제시하고 싶을 때

해석 방법:
- G statistic이 클수록 관측 빈도와 기대 빈도의 차이가 크다는 뜻이다.
- p-value가 작으면 관측 분포가 기대 분포와 같다는 가설을 기각할 근거가 강하다.
- category별 기여도를 보면 어떤 category가 전체 G statistic을 주도했는지 설명할 수 있다.
- alarm은 전체 범주 구성 변화 후보이며, 업무 원인은 category별 증감 방향으로 후속 해석한다.

주의점:
- 기대 빈도가 너무 작은 category가 많으면 근사 p-value가 불안정할 수 있다.
- p-value는 전체 분포 차이의 유의성이고, 변화 크기와 업무 영향은 비율 차이로 따로 설명해야 한다.
- category 정의나 집계 기준이 바뀌면 drift가 아니라 전처리 변경을 반영할 수 있다.

보고서 문장 예시:

```text
current category 빈도를 LIKELIHOOD_RATIO_G_TEST_GOF로 기대 분포와 비교한 결과,
G statistic과 p-value가 범주 구성 변화 후보를 보였다.
이는 일부 category의 관측 비율이 기준 비율과 달라졌을 가능성을 나타낸다.
다만 기대 빈도가 낮은 category에서는 근사 p-value가 불안정할 수 있으므로, category별 기여도와 비율 차이를 함께 확인해야 한다.
```

---

## 변종: LIKELIHOOD_RATIO_G_TEST_INDEPENDENCE

`LIKELIHOOD_RATIO_G_TEST_INDEPENDENCE`는 두 범주형 변수의 독립성이 유지되는지 likelihood ratio 방식으로 평가하는 G-test 변종이다. Drift monitoring에서는 기간과 category, segment와 event type, 모델 버전과 오류 유형처럼 두 축의 관계가 달라졌는지 확인할 때 쓴다. 출력은 G statistic, p-value, cell별 기여도, alarm state로 해석한다.

사용 상황:
- reference/current 기간에 따라 category 구성이나 event type 분포가 달라졌는지 확인할 때
- 고객 segment와 결과 label, 지역과 오류 유형처럼 두 범주 축의 관계 변화를 보고 싶을 때
- contingency table의 전체 관계 변화와 주요 cell 기여도를 함께 보고해야 할 때

해석 방법:
- G statistic이 클수록 두 범주 축이 독립이라는 가정에서 관측 table이 더 멀다는 뜻이다.
- p-value가 작으면 두 변수의 관계가 우연한 독립 구조로 보기 어렵다는 근거가 강하다.
- cell별 contribution이나 standardized residual을 보면 어떤 조합이 관계 변화를 주도했는지 설명할 수 있다.
- alarm은 전체 table 수준의 관계 변화 후보이며, 특정 원인은 cell별 분해로 확인한다.

주의점:
- 낮은 기대 빈도 셀이 많으면 근사 p-value가 왜곡될 수 있다.
- table 전체 유의성은 어느 cell이 문제인지 직접 알려주지 않는다.
- 표본 수가 매우 크면 작은 관계 변화도 유의해질 수 있어 효과 크기와 비율 차이를 함께 봐야 한다.

보고서 문장 예시:

```text
기간과 category의 contingency table을 LIKELIHOOD_RATIO_G_TEST_INDEPENDENCE로 평가한 결과,
G statistic과 p-value가 두 축의 관계 변화 후보를 보였다.
이는 current 기간에서 특정 category 조합의 빈도 구조가 기준 기간과 달라졌을 가능성을 나타낸다.
다만 전체 p-value만으로 원인 조합을 확정할 수 없으므로, cell별 contribution과 기대 빈도 조건을 함께 검토해야 한다.
```

---

## 변종: G_TEST_WITH_SMALL_COUNT_CAUTION

`G_TEST_WITH_SMALL_COUNT_CAUTION`은 G-test를 적용하되 기대 빈도가 낮은 category나 sparse cell 때문에 해석 주의가 필요한 상황을 명시하는 변종이다. G statistic과 p-value를 계산하더라도 근사 조건이 약하면 결과를 단정하지 않고, category 통합, exact test, bootstrap 같은 보완 확인을 권장한다. 출력은 G statistic, p-value, low-count 경고, alarm state로 해석한다.

사용 상황:
- 범주 수가 많고 일부 category의 관측치 또는 기대 빈도가 매우 낮을 때
- long-tail category, 희귀 event type, 신규 category가 섞인 current window를 비교할 때
- G-test 결과를 보고하되 low-count limitation을 함께 표시해야 할 때

해석 방법:
- G statistic과 p-value는 전체 범주 구성 차이 후보를 요약하지만, low-count 경고가 있으면 신뢰도를 낮춰 읽는다.
- 낮은 count category가 statistic을 주도하는지 contribution table로 확인한다.
- alarm이 있더라도 exact test나 category grouping 후 재검증이 필요할 수 있다.
- 보고서에는 몇 개 category가 low-count 조건에 걸렸는지와 보완 검증 계획을 함께 적는다.

주의점:
- sparse table에서는 p-value가 실제 유의수준과 어긋날 수 있다.
- low-count category를 무리하게 해석하면 희귀 이벤트의 우연 변동을 drift로 과대평가할 수 있다.
- category 통합을 하면 해석 단위가 바뀌므로 통합 기준을 문서화해야 한다.

보고서 문장 예시:

```text
범주형 빈도를 G_TEST_WITH_SMALL_COUNT_CAUTION으로 비교한 결과,
G statistic은 기준 대비 구성 변화 후보를 보였지만 일부 category의 기대 빈도가 낮았다.
따라서 이 결과는 drift 후보 screening으로만 해석하고, sparse cell 영향을 고려해야 한다.
후속 확인에서는 낮은 count category의 통합 기준과 exact test 또는 bootstrap 재검증 결과를 함께 보고해야 한다.
```

---

## SelectionRule 카탈로그

```text
selectionRule G_TEST_DEFAULT_USE
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

> G-test 카탈로그는 "이 방법이 무엇인가"가 아니라, "어떤 상황에서 어떤 변종을 선택하고 어떤 주의사항과 함께 설명해야 하는가"를 구조화한다.
