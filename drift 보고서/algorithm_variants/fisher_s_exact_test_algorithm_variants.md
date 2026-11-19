# Fisher's Exact Test 알고리즘 변종 목록

## 1. 목적

이 문서는 `Fisher's Exact Test`를 하나의 고정된 detector로 보지 않고, drift monitoring에서 상황에 따라 선택해야 하는 **알고리즘 변종들의 family**로 정리한다.

핵심 목적은 다음이다.

```text
상황 조건 -> 적절한 Fisher's Exact Test 계열 변종 -> 출력 metric -> 주의사항 -> LLM 보고서 설명
```

---

## 2. Fisher's Exact Test의 위치

```text
methodFamily FISHER_S_EXACT_TEST
       ├─ algorithmVariant TWO_BY_TWO_FISHER_EXACT
       ├─ algorithmVariant ONE_SIDED_FISHER_EXACT
       └─ algorithmVariant EXTENDED_CONTINGENCY_EXACT_TEST
```

`Fisher's Exact Test`는 drift monitoring method 계열에 속한다. Fisher's Exact Test 계열을 drift monitoring 문맥에서 입력 데이터와 운영 목적에 따라 선택 가능한 변종으로 정리한다.

---

## 3. 공통 개념

```text
methodFamily FISHER_S_EXACT_TEST
  purpose ->
    Fisher's Exact Test 계열을 drift monitoring 문맥에서 입력 데이터와 운영 목적에 따라 선택 가능한 변종으로 정리한다.

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

## 변종: TWO_BY_TWO_FISHER_EXACT

`TWO_BY_TWO_FISHER_EXACT`는 reference/current 두 기간과 event/non-event 두 상태로 만든 2x2 contingency table을 Fisher exact test로 비교하는 변종이다. 표본 수가 작거나 기대 빈도가 낮아 chi-square 근사가 불안정할 때 event rate 변화 후보를 확인하는 데 쓴다. 출력은 p-value, odds ratio, event rate 차이, alarm state로 해석한다.

사용 상황:
- 승인/거절, 성공/실패, 오류/정상처럼 이진 event 비율을 reference/current로 비교할 때
- 작은 표본 또는 희귀 event 때문에 chi-square test보다 exact test가 필요한 경우
- event rate 변화와 odds ratio를 함께 보고서에 제시해야 할 때

해석 방법:
- p-value가 작으면 reference/current의 event 비율이 같다는 가설을 기각할 근거가 강하다.
- odds ratio가 1보다 크면 current에서 event odds가 높아졌고, 1보다 작으면 낮아진 방향으로 해석한다.
- event rate 차이는 실제 변화 크기를 설명하는 지표이며, p-value와 별도로 보고한다.
- alarm은 exact test 또는 운영 기준을 통과했다는 screening 신호로 보고, 업무 원인은 후속 확인한다.

주의점:
- p-value는 통계적 유의성이고 event rate 차이의 업무 영향은 별도 판단이 필요하다.
- 표본 수가 매우 작으면 odds ratio 신뢰구간이 넓어 방향 해석을 조심해야 한다.
- 2x2 table 정의가 바뀌거나 event label 기준이 달라지면 기간 비교가 무의미해진다.

보고서 문장 예시:

```text
reference/current의 2x2 event table을 TWO_BY_TWO_FISHER_EXACT로 비교한 결과,
p-value와 odds ratio가 event 비율 변화 후보를 가리켰다.
이는 current 기간의 이진 event 발생 구조가 기준 기간과 달라졌을 가능성을 나타낸다.
다만 표본 수가 작아 신뢰구간이 넓을 수 있으므로, event rate 차이와 데이터 정의 변경 여부를 함께 확인해야 한다.
```

---

## 변종: ONE_SIDED_FISHER_EXACT

`ONE_SIDED_FISHER_EXACT`는 2x2 contingency table에서 event 비율이 특정 방향으로 증가했는지 또는 감소했는지를 Fisher exact test로 확인하는 변종이다. 양방향 차이가 아니라 운영상 위험한 방향이 미리 정해져 있을 때 사용한다. 출력은 one-sided p-value, odds ratio 방향, event rate 차이, alarm state로 해석한다.

사용 상황:
- 장애율, 부정거래율, 불량률처럼 증가 방향만 위험 신호인 event를 감시할 때
- 성공률, 전환율, 승인율처럼 감소 방향만 운영상 문제인 지표를 비교할 때
- 사전에 정한 방향성 가설이 있고 그 방향의 작은 표본 exact test가 필요한 경우

해석 방법:
- one-sided p-value가 작고 관측 방향이 설정 방향과 일치하면 방향성 event rate 변화 후보로 본다.
- odds ratio는 방향을 확인하는 보조 지표이며, upper 가설에서는 1보다 큰지, lower 가설에서는 1보다 작은지 본다.
- alarm은 방향 조건과 유의성 또는 threshold 조건을 함께 만족했다는 표시다.
- 보고서에는 검정 방향을 명시하고 반대 방향 변화는 이 변종의 가설 밖이라는 점을 적는다.

주의점:
- 데이터를 본 뒤 방향을 정하면 p-value 해석이 왜곡되므로 방향은 사전에 정해야 한다.
- 반대 방향 변화나 양방향 차이를 놓칠 수 있으므로 모니터링 목적과 가설 방향이 맞는지 확인한다.
- 표본 수가 작으면 방향은 보이더라도 신뢰구간이 넓을 수 있다.

보고서 문장 예시:

```text
event 비율을 ONE_SIDED_FISHER_EXACT로 비교한 결과,
사전에 설정한 증가 방향에서 one-sided p-value가 기준을 통과했다.
이는 current 기간의 event odds가 기준 기간보다 높아졌을 가능성을 나타내는 방향성 drift 후보 신호다.
다만 검정 방향은 사전에 정의돼야 하며, odds ratio 신뢰구간과 event 정의 변경 여부를 함께 확인해야 한다.
```

---

## 변종: EXTENDED_CONTINGENCY_EXACT_TEST

`EXTENDED_CONTINGENCY_EXACT_TEST`는 2x2를 넘는 작은 contingency table에서 범주 분포나 교차 구조가 달라졌는지 exact 방식으로 평가하는 변종이다. 범주 수가 여러 개지만 표본 수가 작아 asymptotic chi-square 근사를 신뢰하기 어려울 때 사용한다. 출력은 exact p-value, table별 비율 차이, alarm state로 해석한다.

사용 상황:
- 여러 category의 reference/current 빈도 구성을 비교하되 기대 빈도가 낮은 셀이 많은 경우
- segment와 event type처럼 두 범주 축의 독립성 또는 구성 변화를 작은 표본에서 확인할 때
- chi-square/G-test 결과를 exact 방식으로 보완해야 할 때

해석 방법:
- exact p-value가 작으면 관측 table이 기준 가정에서 보기 어려운 구성이라는 근거가 강하다.
- 어떤 셀이 변화를 만들었는지는 p-value가 아니라 category별 비율 차이와 residual 요약으로 확인한다.
- alarm은 전체 table 수준의 변화 후보이며, 특정 category 원인은 후속 분해가 필요하다.
- 보고서에는 table 크기, 낮은 count가 있는 셀, 변화가 큰 category를 함께 제시한다.

주의점:
- table 크기가 커지면 exact 계산 비용이 커지고 결과 해석도 복잡해진다.
- sparse cell이 많으면 일부 category 통합이나 별도 검토가 필요할 수 있다.
- 전체 p-value만으로 어떤 category가 drift를 유발했는지 단정하지 않는다.

보고서 문장 예시:

```text
작은 표본의 다범주 contingency table을 EXTENDED_CONTINGENCY_EXACT_TEST로 평가한 결과,
exact p-value가 reference/current 구성 차이 후보를 지지했다.
이는 여러 category의 빈도 구성이 기준 기간과 달라졌을 가능성을 나타낸다.
다만 전체 table 검정만으로 원인 category를 확정할 수 없으므로, 셀별 비율 차이와 낮은 count 셀을 함께 확인해야 한다.
```

---

## SelectionRule 카탈로그

```text
selectionRule FISHER_S_EXACT_TEST_DEFAULT_USE
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

> Fisher's Exact Test 카탈로그는 "이 방법이 무엇인가"가 아니라, "어떤 상황에서 어떤 변종을 선택하고 어떤 주의사항과 함께 설명해야 하는가"를 구조화한다.
