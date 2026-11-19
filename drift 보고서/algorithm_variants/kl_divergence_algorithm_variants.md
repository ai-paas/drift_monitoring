# KL Divergence 알고리즘 변종 목록

## 1. 목적

이 문서는 `KL Divergence`를 하나의 고정된 detector로 보지 않고, drift monitoring에서 상황에 따라 선택해야 하는 **알고리즘 변종들의 family**로 정리한다.

핵심 목적은 다음이다.

```text
상황 조건 -> 적절한 KL Divergence 계열 변종 -> 출력 metric -> 주의사항 -> LLM 보고서 설명
```

---

## 2. KL Divergence의 위치

```text
methodFamily KL_DIVERGENCE
       ├─ algorithmVariant DISCRETE_KL_DIVERGENCE
       ├─ algorithmVariant HISTOGRAM_KL_DIVERGENCE
       ├─ algorithmVariant SMOOTHED_KL_DIVERGENCE
       └─ algorithmVariant SYMMETRIZED_KL
```

`KL Divergence`는 drift monitoring method 계열에 속한다. KL Divergence 계열을 drift monitoring 문맥에서 입력 데이터와 운영 목적에 따라 선택 가능한 변종으로 정리한다.

---

## 3. 공통 개념

```text
methodFamily KL_DIVERGENCE
  purpose ->
    KL Divergence 계열을 drift monitoring 문맥에서 입력 데이터와 운영 목적에 따라 선택 가능한 변종으로 정리한다.

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

## 변종: DISCRETE_KL_DIVERGENCE

`DISCRETE_KL_DIVERGENCE`는 reference 이산 확률분포를 기준으로 current 분포가 얼마나 다른지 KL divergence로 측정하는 변종이다. category나 discrete state별 확률 차이를 정보량 관점으로 요약하며, 방향성이 있는 divergence로 해석한다. 출력은 KL divergence, 항목별 기여도, alarm state로 읽는다.

사용 상황:
- category, state, token group처럼 이산 분포의 reference/current 차이를 정보량 관점으로 보고 싶을 때
- 기준 분포에서 current 분포가 얼마나 벗어났는지를 방향성 있게 측정해야 할 때
- category별 contribution을 통해 변화가 큰 항목을 설명하고 싶을 때

해석 방법:
- KL divergence가 0에 가까우면 current 분포가 reference와 유사하다.
- 값이 커질수록 current 분포를 reference 기준으로 설명하기 어려운 정도가 커진다.
- 항목별 contribution을 보면 어떤 category의 확률 변화가 divergence를 키웠는지 파악할 수 있다.
- alarm은 분포 drift 후보이며, 성능 저하나 원인 확정은 아니다.

주의점:
- KL은 비대칭이므로 `KL(reference || current)`와 `KL(current || reference)`의 의미가 다르다.
- current 또는 reference에 0 확률 bin이 있으면 smoothing 정책이 필요하다.
- rare category의 작은 확률 변화가 큰 contribution으로 나타날 수 있다.

보고서 문장 예시:

```text
DISCRETE_KL_DIVERGENCE로 이산 분포를 비교한 결과,
current 분포의 KL divergence가 기준 threshold를 초과했다.
이는 current category 구성이 reference 분포 기준에서 보기 어려워졌다는 drift 후보 신호다.
다만 KL 방향과 zero-bin smoothing 기준을 명시하고, 항목별 contribution을 함께 확인해야 한다.
```

---

## 변종: HISTOGRAM_KL_DIVERGENCE

`HISTOGRAM_KL_DIVERGENCE`는 numeric feature를 histogram bin 확률로 변환한 뒤 reference/current 분포 차이를 KL divergence로 계산하는 변종이다. 값 구간별 비중 변화가 기준 분포 대비 얼마나 정보량 차이를 만드는지 요약한다. 출력은 histogram KL divergence, bin별 contribution, alarm state로 해석한다.

사용 상황:
- 연속형 feature의 분포 변화가 어느 값 구간에서 커졌는지 설명하고 싶을 때
- histogram 기반 feature drift score와 bin contribution을 함께 보고해야 할 때
- 평균/분산 변화보다 전체 분포의 정보량 차이를 보고 싶을 때

해석 방법:
- KL divergence가 클수록 current histogram이 reference histogram 기준에서 멀다.
- bin별 contribution은 변화가 집중된 값 구간을 알려주는 보조 설명이다.
- threshold 초과는 numeric feature distribution drift 후보로 해석한다.
- 같은 feature의 시간별 divergence 추세를 보면 drift가 지속되는지 확인할 수 있다.

주의점:
- bin 경계, bin 수, clipping 정책에 따라 score가 달라진다.
- 빈 bin 또는 zero probability bin에는 smoothing이 필요하다.
- KL은 방향성이 있어 기준과 비교 대상의 순서를 보고서에 명시해야 한다.

보고서 문장 예시:

```text
HISTOGRAM_KL_DIVERGENCE로 numeric feature histogram을 비교한 결과,
current 분포의 KL divergence가 calibration threshold를 초과했다.
이는 특정 값 구간의 비중 변화로 인해 current 분포가 reference와 달라졌을 가능성을 나타낸다.
다만 binning 정책과 smoothing 방식이 score에 영향을 주므로, 주요 bin contribution과 함께 보고해야 한다.
```

---

## 변종: SMOOTHED_KL_DIVERGENCE

`SMOOTHED_KL_DIVERGENCE`는 zero probability bin이나 희귀 category 때문에 KL divergence가 무한대 또는 불안정해지는 문제를 줄이기 위해 smoothing을 적용하는 변종이다. 작은 epsilon, Laplace smoothing, prior mixing 등을 사용해 sparse distribution의 drift score를 안정화한다. 출력은 smoothed KL divergence, smoothing policy, alarm state로 해석한다.

사용 상황:
- reference/current 중 한쪽에만 나타나는 category나 bin이 많은 경우
- sparse categorical distribution, long-tail token, rare event type을 비교할 때
- KL score를 운영 threshold와 연결해야 해서 무한대 값을 피해야 할 때

해석 방법:
- smoothed KL이 클수록 smoothing 후에도 current 분포가 reference와 다르다는 뜻이다.
- smoothing policy가 score scale을 바꾸므로 threshold도 같은 정책으로 calibration해야 한다.
- zero-bin이 많아 score가 커졌는지, 실제 주요 category 변화가 컸는지 contribution으로 확인한다.
- alarm은 sparse distribution drift 후보이며, smoothing 민감도를 함께 봐야 한다.

주의점:
- smoothing 값이 너무 크면 실제 rare category 변화를 희석할 수 있다.
- smoothing 값이 너무 작으면 zero-bin 문제와 불안정성이 남는다.
- smoothing 방식이 바뀌면 이전 KL score와 직접 비교하지 않는다.

보고서 문장 예시:

```text
SMOOTHED_KL_DIVERGENCE로 sparse distribution을 비교한 결과,
smoothing 적용 후에도 KL divergence가 기준 threshold를 초과했다.
이는 zero-bin 보정을 고려해도 current 분포가 reference와 달라졌을 가능성을 나타낸다.
다만 smoothing 계수와 rare category contribution이 결과에 영향을 주므로 해당 정책을 함께 명시해야 한다.
```

---

## 변종: SYMMETRIZED_KL

`SYMMETRIZED_KL`은 양방향 KL divergence를 더하거나 평균내어 reference/current 분포 차이를 대칭 score로 만드는 변종이다. 단방향 KL의 순서 민감도를 줄이고, 두 분포 사이의 상호 차이를 하나의 값으로 보고할 때 사용한다. 출력은 symmetrized KL score, 양방향 KL component, alarm state로 해석한다.

사용 상황:
- KL 방향 선택이 보고서 해석을 혼란스럽게 만들 수 있는 경우
- reference와 current를 대칭적으로 비교하고 싶은 feature drift screening에서
- 양방향 divergence component를 함께 보고해 변화의 비대칭성을 확인하고 싶을 때

해석 방법:
- symmetrized KL이 클수록 두 분포가 서로 다르다는 신호가 강하다.
- 양방향 component 중 한쪽이 특히 크면 특정 분포에만 있는 bin/category가 영향을 준 것일 수 있다.
- threshold 초과는 분포 차이 후보로 해석하되, score는 JS처럼 bounded하지 않을 수 있다.
- 항목별 contribution과 smoothing 정책을 함께 봐야 변화 원인을 설명할 수 있다.

주의점:
- 대칭화해도 zero-bin 문제는 남으므로 smoothing 기준이 필요하다.
- score가 bounded하지 않으면 다른 distance 계열과 단순 비교하기 어렵다.
- symmetrized KL은 metric이 아니므로 거리로 표현할 때는 용어를 조심한다.

보고서 문장 예시:

```text
SYMMETRIZED_KL로 reference/current 분포를 대칭적으로 비교한 결과,
양방향 KL을 반영한 score가 기준 threshold를 초과했다.
이는 두 기간의 확률분포가 서로 달라졌을 가능성을 나타내는 drift 후보 신호다.
다만 score가 bounded distance는 아니며, zero-bin smoothing과 양방향 component를 함께 확인해야 한다.
```

---

## SelectionRule 카탈로그

```text
selectionRule KL_DIVERGENCE_DEFAULT_USE
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

> KL Divergence 카탈로그는 "이 방법이 무엇인가"가 아니라, "어떤 상황에서 어떤 변종을 선택하고 어떤 주의사항과 함께 설명해야 하는가"를 구조화한다.
