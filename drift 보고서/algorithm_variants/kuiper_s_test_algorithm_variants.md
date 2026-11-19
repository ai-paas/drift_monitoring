# Kuiper's Test 알고리즘 변종 목록

## 1. 목적

이 문서는 `Kuiper's Test`를 하나의 고정된 detector로 보지 않고, drift monitoring에서 상황에 따라 선택해야 하는 **알고리즘 변종들의 family**로 정리한다.

핵심 목적은 다음이다.

```text
상황 조건 -> 적절한 Kuiper's Test 계열 변종 -> 출력 metric -> 주의사항 -> LLM 보고서 설명
```

---

## 2. Kuiper's Test의 위치

```text
methodFamily KUIPER_S_TEST
       ├─ algorithmVariant KUIPER_TWO_SAMPLE
       ├─ algorithmVariant KUIPER_CIRCULAR_DATA
       └─ algorithmVariant KUIPER_ONE_SAMPLE
```

`Kuiper's Test`는 drift monitoring method 계열에 속한다. Kuiper's Test 계열을 drift monitoring 문맥에서 입력 데이터와 운영 목적에 따라 선택 가능한 변종으로 정리한다.

---

## 3. 공통 개념

```text
methodFamily KUIPER_S_TEST
  purpose ->
    Kuiper's Test 계열을 drift monitoring 문맥에서 입력 데이터와 운영 목적에 따라 선택 가능한 변종으로 정리한다.

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

## 변종: KUIPER_TWO_SAMPLE

`KUIPER_TWO_SAMPLE`은 reference/current 두 sample의 경험 CDF 차이를 위쪽 최대 차이와 아래쪽 최대 차이의 합으로 평가하는 Kuiper two-sample 변종이다. KS test와 비슷하지만 양쪽 방향 차이를 함께 더해 분포 전반의 이동과 순환형 구간 차이에 더 균형 있게 반응할 수 있다. 출력은 Kuiper statistic, p-value 또는 score, alarm state로 해석한다.

사용 상황:
- 단변량 분포를 reference/current로 비교하되, CDF 차이의 양방향 성분을 함께 보고 싶을 때
- KS의 최대 차이 하나보다 상하 방향 차이를 모두 반영한 score가 필요한 경우
- 시간대, 각도, 계절 위치처럼 순환적 성격이 있는 feature의 보조 검정으로

해석 방법:
- Kuiper statistic이 클수록 두 경험분포의 양방향 CDF 차이 합이 크다.
- p-value 또는 threshold 기준을 넘으면 reference/current 분포 차이 후보로 본다.
- statistic은 어느 한 방향 차이만이 아니라 위/아래 CDF gap을 함께 반영한다.
- 보고서에는 KS와 다른 Kuiper statistic의 구성, 즉 양방향 CDF 차이 합이라는 점을 적는다.

주의점:
- sample size가 작으면 p-value 또는 threshold calibration이 불안정할 수 있다.
- discrete 값이나 ties가 많으면 EDF 기반 p-value 해석에 주의한다.
- 분포가 달라졌다는 신호일 뿐 원인이나 성능 저하를 확정하지 않는다.

보고서 문장 예시:

```text
KUIPER_TWO_SAMPLE로 reference/current 분포를 비교한 결과,
양방향 CDF 차이를 합산한 Kuiper statistic이 기준 threshold를 초과했다.
이는 current 분포가 기준 기간과 달라졌을 가능성을 나타내는 drift 후보 신호다.
다만 어떤 값 구간에서 차이가 큰지는 CDF 차이와 분포 차트를 함께 확인해야 한다.
```

---

## 변종: KUIPER_CIRCULAR_DATA

`KUIPER_CIRCULAR_DATA`는 각도, 시각, 요일 주기, 계절 위치처럼 시작점과 끝점이 이어지는 circular data의 분포 차이를 Kuiper statistic으로 평가하는 변종이다. CDF 경계 선택에 덜 민감해 순환형 feature에서 KS보다 자연스러운 비교가 가능하다. 출력은 circular Kuiper statistic, p-value 또는 score, alarm state로 해석한다.

사용 상황:
- 시간대, day-of-week, 월중 위치, 방향각처럼 주기적으로 반복되는 feature를 비교할 때
- 23시와 0시처럼 경계 양쪽 값이 실제로는 가까운 데이터에서
- circular feature의 reference/current pattern 변화 후보를 감시할 때

해석 방법:
- statistic이 클수록 순환형 축에서 reference/current 분포 차이가 크다.
- alarm은 circular feature의 주기적 패턴이 기준과 달라졌다는 후보 신호다.
- 변화 원인은 원형 histogram 또는 phase별 비율 차이로 설명한다.
- 보고서에는 circular scale과 wrap-around 처리 기준을 명시한다.

주의점:
- circular encoding이 잘못되면 경계 근처 변화가 과장되거나 누락될 수 있다.
- binning한 circular feature라면 bin 경계와 smoothing 정책이 결과에 영향을 준다.
- p-value calibration은 일반 연속형 feature보다 구현과 sample size에 민감할 수 있다.

보고서 문장 예시:

```text
KUIPER_CIRCULAR_DATA로 시간대 분포를 비교한 결과,
current 기간의 circular pattern이 reference와 달라졌다는 alarm이 발생했다.
이는 하루 주기 내 특정 시간대 비중이 기준 기간과 달라졌을 가능성을 나타낸다.
다만 0시 경계의 wrap-around 처리와 원형 histogram 차이를 함께 확인해야 한다.
```

---

## 변종: KUIPER_ONE_SAMPLE

`KUIPER_ONE_SAMPLE`은 하나의 sample 경험분포를 사전에 지정된 기준 CDF와 Kuiper statistic으로 비교하는 one-sample 변종이다. 특히 circular distribution이나 기준 주기 패턴과 current sample의 차이를 점검할 때 유용하다. 출력은 Kuiper statistic, p-value 또는 score, alarm state로 해석한다.

사용 상황:
- current sample이 사전에 정의된 기준 분포나 주기 패턴을 따르는지 확인할 때
- reference sample 없이 이론 CDF 또는 정책상 baseline과 비교해야 할 때
- one-sample KS보다 양방향 CDF 차이를 균형 있게 반영하고 싶을 때

해석 방법:
- Kuiper statistic은 sample CDF와 기준 CDF의 위쪽/아래쪽 최대 차이를 합산한다.
- threshold 또는 p-value 기준을 넘으면 sample이 기준 분포와 다를 가능성이 있다.
- alarm은 지정 기준 분포와의 차이 후보이며 reference/current 두 기간 비교와는 구분한다.
- 보고서에는 기준 CDF가 어떻게 지정되었는지와 파라미터 추정 여부를 적는다.

주의점:
- 기준 분포 파라미터를 같은 sample에서 추정하면 p-value 해석이 달라질 수 있다.
- discrete 또는 tied data에서는 EDF 기반 검정 해석에 제한이 있다.
- one-sample 적합성 검토 결과를 곧바로 운영 원인이나 성능 문제로 연결하지 않는다.

보고서 문장 예시:

```text
KUIPER_ONE_SAMPLE로 current sample을 사전 지정 기준 분포와 비교한 결과,
Kuiper statistic이 기준 threshold를 초과했다.
이는 현재 sample이 기대한 기준 분포 또는 주기 패턴과 달라졌을 가능성을 나타낸다.
다만 기준 CDF의 정의와 파라미터 추정 여부를 확인한 뒤 해석해야 한다.
```

---

## SelectionRule 카탈로그

```text
selectionRule KUIPER_S_TEST_DEFAULT_USE
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

> Kuiper's Test 카탈로그는 "이 방법이 무엇인가"가 아니라, "어떤 상황에서 어떤 변종을 선택하고 어떤 주의사항과 함께 설명해야 하는가"를 구조화한다.
