# L-Infinity Distance 알고리즘 변종 목록

## 1. 목적

이 문서는 `L-Infinity Distance`를 하나의 고정된 detector로 보지 않고, drift monitoring에서 상황에 따라 선택해야 하는 **알고리즘 변종들의 family**로 정리한다.

핵심 목적은 다음이다.

```text
상황 조건 -> 적절한 L-Infinity Distance 계열 변종 -> 출력 metric -> 주의사항 -> LLM 보고서 설명
```

---

## 2. L-Infinity Distance의 위치

```text
methodFamily L_INFINITY_DISTANCE
       ├─ algorithmVariant CATEGORICAL_L_INFINITY
       ├─ algorithmVariant PROBABILITY_VECTOR_L_INFINITY
       └─ algorithmVariant BINNED_NUMERIC_L_INFINITY
```

`L-Infinity Distance`는 drift monitoring method 계열에 속한다. L-Infinity Distance 계열을 drift monitoring 문맥에서 입력 데이터와 운영 목적에 따라 선택 가능한 변종으로 정리한다.

---

## 3. 공통 개념

```text
methodFamily L_INFINITY_DISTANCE
  purpose ->
    L-Infinity Distance 계열을 drift monitoring 문맥에서 입력 데이터와 운영 목적에 따라 선택 가능한 변종으로 정리한다.

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

## 변종: CATEGORICAL_L_INFINITY

`CATEGORICAL_L_INFINITY`는 category별 reference/current 비율 차이 중 가장 큰 절대 차이를 L-infinity distance로 요약하는 변종이다. 전체 분포 차이의 평균적 크기보다 "가장 많이 변한 category"를 빠르게 찾는 데 적합하다. 출력은 max absolute proportion difference, 해당 category, alarm state로 해석한다.

사용 상황:
- 범주형 feature에서 특정 category 비중 급변을 즉시 찾고 싶을 때
- 전체 distance는 작아도 하나의 category 변화가 운영상 중요한 경우
- category별 비율표와 함께 가장 큰 변화 항목을 보고서에 제시해야 할 때

해석 방법:
- L-infinity distance는 모든 category 비율 차이 중 최대 절대값이다.
- threshold를 넘으면 적어도 하나의 category가 기준보다 크게 변했다는 drift 후보로 본다.
- 함께 반환되는 max category를 보면 어떤 항목이 alarm을 주도했는지 설명할 수 있다.
- 다른 category들의 누적 변화는 이 score에 덜 반영되므로 별도 분포 지표를 함께 볼 수 있다.

주의점:
- 단일 category의 표본 수가 작으면 우연 변동이 max score를 만들 수 있다.
- long-tail category가 많으면 rare category grouping 정책이 중요하다.
- 전체 분포가 넓게 조금씩 변하는 경우에는 L1, JS, chi-square 같은 지표가 더 잘 보일 수 있다.

보고서 문장 예시:

```text
CATEGORICAL_L_INFINITY로 category 비율 변화를 비교한 결과,
가장 크게 변한 category의 비율 차이가 threshold를 초과했다.
이는 current 기간에서 특정 category 비중이 기준 기간과 크게 달라졌을 가능성을 나타낸다.
다만 rare category의 표본 수와 grouping 기준을 함께 확인해야 한다.
```

---

## 변종: PROBABILITY_VECTOR_L_INFINITY

`PROBABILITY_VECTOR_L_INFINITY`는 두 probability vector의 각 성분 차이 중 최대 절대값을 drift score로 사용하는 변종이다. 모델 class probability, topic distribution, segment probability처럼 확률 벡터 형태의 출력에서 가장 크게 변한 성분을 찾는다. 출력은 max probability difference, max component, alarm state로 해석한다.

사용 상황:
- 다중분류 probability vector나 topic vector의 성분별 변화 중 최대 변화를 감시할 때
- 전체 분포 distance보다 특정 class 또는 topic의 급변이 중요할 때
- bounded하고 직관적인 max difference score가 필요한 dashboard에서

해석 방법:
- score가 0이면 두 probability vector가 동일하고, 커질수록 최소 한 성분의 차이가 크다.
- alarm은 특정 probability component가 reference 대비 크게 변했다는 후보 신호다.
- max component를 함께 보면 어떤 class, topic, segment가 변화의 중심인지 설명할 수 있다.
- 전체적인 분포 재배열은 L-infinity 하나만으로 부족할 수 있어 JS 또는 TV distance와 함께 본다.

주의점:
- probability calibration이나 model version이 바뀌면 component difference가 drift처럼 보일 수 있다.
- 작은 class의 확률 변화가 업무적으로 큰 의미인지 별도 판단해야 한다.
- sum-to-one 제약 때문에 한 성분 변화가 다른 성분 변화와 연결되어 나타난다.

보고서 문장 예시:

```text
PROBABILITY_VECTOR_L_INFINITY로 예측 확률 벡터를 비교한 결과,
특정 class의 probability 차이가 기준 threshold를 초과했다.
이는 current 기간에서 해당 class 확률 성분이 reference 대비 크게 변했을 가능성을 나타낸다.
다만 모델 calibration 또는 버전 변경 영향이 없는지 함께 확인해야 한다.
```

---

## 변종: BINNED_NUMERIC_L_INFINITY

`BINNED_NUMERIC_L_INFINITY`는 numeric feature를 bin으로 나눈 뒤 reference/current bin 비율 차이 중 최대 절대 차이를 계산하는 변종이다. 값 구간별 변화 중 가장 크게 달라진 구간을 빠르게 식별한다. 출력은 max bin proportion difference, max bin range, alarm state로 해석한다.

사용 상황:
- numeric feature에서 특정 값 구간의 비중 급변을 감시하고 싶을 때
- 평균 변화보다 tail bin, high-value bin, low-value bin의 비율 변화가 중요한 경우
- histogram chart와 함께 가장 큰 bin 차이를 보고해야 할 때

해석 방법:
- L-infinity score는 모든 bin 비율 차이 중 가장 큰 절대값이다.
- threshold 초과는 최소 하나의 값 구간에서 current 비중이 기준과 크게 다르다는 뜻이다.
- max bin range를 보면 변화가 중심부인지 tail인지 설명할 수 있다.
- 전체 분포의 넓은 변화는 이 score만으로 충분히 드러나지 않을 수 있다.

주의점:
- bin 경계와 bin 수에 따라 max bin이 바뀔 수 있다.
- 표본 수가 적은 bin에서는 우연 변동이 커질 수 있다.
- outlier나 clipping 정책 변경이 특정 bin 차이를 크게 만들 수 있다.

보고서 문장 예시:

```text
BINNED_NUMERIC_L_INFINITY로 numeric feature histogram을 비교한 결과,
특정 값 구간의 bin 비율 차이가 threshold를 초과했다.
이는 current 기간에서 해당 값 범위의 관측 비중이 기준 기간과 크게 달라졌을 가능성을 나타낸다.
다만 binning 정책과 outlier 처리 기준이 동일한지 확인해야 한다.
```

---

## SelectionRule 카탈로그

```text
selectionRule L_INFINITY_DISTANCE_DEFAULT_USE
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

> L-Infinity Distance 카탈로그는 "이 방법이 무엇인가"가 아니라, "어떤 상황에서 어떤 변종을 선택하고 어떤 주의사항과 함께 설명해야 하는가"를 구조화한다.
