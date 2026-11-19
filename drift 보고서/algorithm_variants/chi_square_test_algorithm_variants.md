# Chi-square Test 알고리즘 변종 목록

## 1. 목적

이 문서는 `Chi-square Test`를 하나의 고정된 detector로 보지 않고, drift monitoring에서 상황에 따라 선택해야 하는 **알고리즘 변종들의 family**로 정리한다.

핵심 목적은 다음이다.

```text
상황 조건 -> 적절한 Chi-square Test 계열 변종 -> 출력 metric -> 주의사항 -> LLM 보고서 설명
```

---

## 2. Chi-square Test의 위치

```text
methodFamily CHI_SQUARE_TEST
       ├─ algorithmVariant CHI_SQUARE_GOODNESS_OF_FIT
       ├─ algorithmVariant CHI_SQUARE_HOMOGENEITY
       └─ algorithmVariant CHI_SQUARE_WITH_LOW_EXPECTED_COUNT_CAUTION
```

`Chi-square Test`는 drift monitoring method 계열에 속한다. Chi-square Test 계열을 drift monitoring 문맥에서 입력 데이터와 운영 목적에 따라 선택 가능한 변종으로 정리한다.

---

## 3. 공통 개념

```text
methodFamily CHI_SQUARE_TEST
  purpose ->
    Chi-square Test 계열을 drift monitoring 문맥에서 입력 데이터와 운영 목적에 따라 선택 가능한 변종으로 정리한다.

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

## 변종: CHI_SQUARE_GOODNESS_OF_FIT

`CHI_SQUARE_GOODNESS_OF_FIT`은 현재 관측된 범주별 count가 사전에 정한 기대 분포 또는 기준 비율과 맞는지를 검정하는 변종이다. reference 기간의 비율, 정책상 기대 비율, 또는 학습 당시 category mix를 expected count로 두고 current count가 얼마나 벗어났는지 평가한다. drift monitoring에서는 현재 데이터의 category 구성비가 기준 구성과 달라졌는지를 빠르게 확인하는 데 사용한다.

이 변종은 다음 상황에 적합하다.

- current window의 category count를 하나의 기준 expected distribution과 비교한다.
- 학습 데이터, reference 기간, 정책 기준 비율이 명확하게 정의돼 있다.
- category mix 변화가 입력 데이터 drift 후보인지 확인하고 싶다.
- p-value와 함께 어느 category가 기대보다 많거나 적은지 보고해야 한다.

해석할 때는 chi-square statistic, 자유도, p-value, category별 residual을 함께 본다. Statistic이 클수록 관측 count와 기대 count의 차이가 크다는 뜻이다. p-value가 유의수준보다 작으면 현재 count가 기대 분포와 같다는 가정과 맞지 않는 통계적 신호로 볼 수 있다. 어느 category가 변화를 주도했는지는 observed count, expected count, standardized residual을 확인해야 한다.

주의할 점은 기대 count가 너무 작으면 chi-square 근사가 불안정해질 수 있다는 것이다. 희소 category는 묶거나 별도 검정을 고려해야 하며, expected distribution의 출처와 적용 기간이 현재 운영 조건과 맞는지도 확인해야 한다. 표본 수가 매우 크면 작은 비율 차이도 유의해질 수 있으므로 효과 크기와 실제 비중 차이를 함께 보고한다. 검정 결과만으로 모델 성능 저하나 업무 원인을 확정하지 않는다.

보고서 문장 예시는 다음과 같다.

```text
현재 window의 category count를 CHI_SQUARE_GOODNESS_OF_FIT으로 기준 비율과 비교한 결과,
chi-square statistic이 커지고 p-value가 유의수준보다 낮게 나타났다.
이는 현재 category 구성비가 기준 분포와 같다는 가정에 맞지 않는 drift 후보 신호다.
다만 기대 count가 작은 category와 표본 수 효과가 있을 수 있으므로,
category별 observed/expected 차이와 standardized residual을 함께 확인해야 한다.
```

---

## 변종: CHI_SQUARE_HOMOGENEITY

`CHI_SQUARE_HOMOGENEITY`는 두 개 이상 집단의 category 분포가 같은지 비교하는 변종이다. drift monitoring에서는 보통 reference window와 current window의 범주별 count table을 만들고, 두 기간의 category 구성비가 동질적인지 검정한다. 적합도 검정이 하나의 관측 분포를 고정된 기대 분포와 비교한다면, 동질성 검정은 여러 기간이나 segment의 관측 분포를 서로 비교한다는 점이 다르다.

이 변종은 다음 상황에 적합하다.

- reference/current 기간의 category count table을 직접 비교한다.
- 여러 segment, region, channel 사이의 category mix가 같은지 확인한다.
- 기준 expected distribution을 고정하기보다 관측 집단 간 차이를 보고 싶다.
- category 분포 변화가 특정 기간 또는 집단에서만 나타나는지 확인한다.

해석할 때는 chi-square statistic과 p-value가 집단 간 category 비율 차이를 얼마나 지지하는지 본다. Statistic이 클수록 집단별 category 구성비가 서로 다르다는 신호가 강하다. p-value가 유의수준보다 작으면 집단들이 같은 category 분포를 가진다는 가정과 맞지 않는다고 해석한다. 변화가 어느 기간이나 category에서 발생했는지는 contingency table의 셀별 residual과 비율 차이로 확인한다.

주의할 점은 각 셀의 expected count가 충분하지 않으면 검정 결과가 불안정해진다는 것이다. category가 너무 많거나 희소하면 category 병합, 기간 확장, exact test 같은 대안을 고려해야 한다. 표본 수가 큰 경우 작은 구성비 차이도 유의할 수 있으므로 Cramer's V 같은 효과 크기나 실제 비율 차이를 함께 보는 것이 좋다. 이 검정은 category 분포 차이만 말해주며 원인이나 성능 영향을 확정하지 않는다.

보고서 문장 예시는 다음과 같다.

```text
기준 기간과 현재 기간의 category count table을 CHI_SQUARE_HOMOGENEITY로 비교한 결과,
chi-square statistic이 상승하고 p-value가 유의수준 아래로 나타났다.
이는 두 기간의 category 구성비가 동질적이라는 가정과 맞지 않는 drift 후보 신호다.
다만 희소 셀과 표본 수 효과가 검정에 영향을 줄 수 있으므로,
셀별 residual, 실제 비율 차이, segment별 원천 데이터를 함께 확인해야 한다.
```

---

## 변종: CHI_SQUARE_WITH_LOW_EXPECTED_COUNT_CAUTION

`CHI_SQUARE_WITH_LOW_EXPECTED_COUNT_CAUTION`은 Chi-square 검정을 쓰되, 기대 count가 작은 셀이 결과를 흔들 수 있음을 명시적으로 다루는 변종이다. 범주 수가 많거나 일부 category가 희소한 데이터에서 reference/current 분포 차이를 screening할 때 사용한다. 이 변종의 핵심은 검정 결과 자체보다, 기대 count 조건을 함께 보고해 p-value를 과신하지 않도록 하는 데 있다.

이 변종은 다음 상황에 적합하다.

- reference/current category count table에 희소 category가 포함돼 있다.
- 일부 expected count가 작지만, 운영상 category를 임의로 제거하기 어렵다.
- Chi-square statistic과 p-value를 drift 후보 screening 지표로 쓰되, 검정 가정의 취약성을 함께 보고해야 한다.
- category 병합, 기간 확장, exact test 같은 대안 검토 여부를 보고서에 남기고 싶다.

해석할 때는 chi-square statistic과 p-value를 기대 count 조건과 함께 읽어야 한다. Statistic이 크거나 p-value가 낮더라도 expected count가 작은 셀이 많으면 통계적 유의성은 불안정할 수 있다. 따라서 alarm이나 drift 후보 신호를 해석할 때는 전체 검정 결과뿐 아니라 셀별 observed/expected count, standardized residual, 희소 category의 비중을 함께 확인한다.

주의할 점은 이 변종이 희소 count 문제를 해결하는 방법이 아니라, 그 위험을 드러내는 보고 방식이라는 것이다. 기대 count가 낮은 셀이 많으면 category 병합, reference 기간 확장, exact test 또는 permutation 기반 검정을 검토해야 한다. 표본 수가 작으면 p-value가 불안정하고, 표본 수가 매우 크면 작은 구성비 차이도 유의해질 수 있으므로 실제 비율 차이와 운영 영향은 별도로 확인한다. 검정 결과만으로 모델 성능 저하나 원인을 확정하지 않는다.

보고서 문장 예시는 다음과 같다.

```text
희소 category를 포함한 기준 기간과 현재 기간의 count table을 CHI_SQUARE_WITH_LOW_EXPECTED_COUNT_CAUTION으로 비교한 결과,
chi-square statistic과 p-value는 category 구성비 차이 가능성을 보였다.
이는 분포 변화 후보 신호로 볼 수 있지만, 일부 셀의 expected count가 낮아 검정 근사가 불안정할 수 있다.
따라서 category 병합 전후 결과, 셀별 observed/expected 차이, 실제 비율 차이를 함께 확인해야 한다.
```

---

## SelectionRule 카탈로그

```text
selectionRule CHI_SQUARE_TEST_DEFAULT_USE
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

> Chi-square Test 카탈로그는 "이 방법이 무엇인가"가 아니라, "어떤 상황에서 어떤 변종을 선택하고 어떤 주의사항과 함께 설명해야 하는가"를 구조화한다.
