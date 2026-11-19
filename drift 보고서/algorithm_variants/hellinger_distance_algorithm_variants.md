# Hellinger Distance 알고리즘 변종 목록

## 1. 목적

이 문서는 `Hellinger Distance`를 하나의 고정된 detector로 보지 않고, drift monitoring에서 상황에 따라 선택해야 하는 **알고리즘 변종들의 family**로 정리한다.

핵심 목적은 다음이다.

```text
상황 조건 -> 적절한 Hellinger Distance 계열 변종 -> 출력 metric -> 주의사항 -> LLM 보고서 설명
```

---

## 2. Hellinger Distance의 위치

```text
methodFamily HELLINGER_DISTANCE
       ├─ algorithmVariant DISCRETE_HELLINGER_DISTANCE
       ├─ algorithmVariant HISTOGRAM_HELLINGER_DISTANCE
       └─ algorithmVariant CATEGORICAL_HELLINGER_DISTANCE
```

`Hellinger Distance`는 drift monitoring method 계열에 속한다. Hellinger Distance 계열을 drift monitoring 문맥에서 입력 데이터와 운영 목적에 따라 선택 가능한 변종으로 정리한다.

---

## 3. 공통 개념

```text
methodFamily HELLINGER_DISTANCE
  purpose ->
    Hellinger Distance 계열을 drift monitoring 문맥에서 입력 데이터와 운영 목적에 따라 선택 가능한 변종으로 정리한다.

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

## 변종: DISCRETE_HELLINGER_DISTANCE

`DISCRETE_HELLINGER_DISTANCE`는 reference/current의 이산 확률분포 차이를 Hellinger distance로 계산하는 변종이다. category, bin, discrete state별 확률 벡터를 비교해 두 분포가 얼마나 겹치지 않는지 0과 1 사이 거리로 요약한다. 출력은 Hellinger distance, threshold 초과 여부, alarm state로 해석한다.

사용 상황:
- 범주형 또는 이산화된 feature의 reference/current 분포 차이를 비교할 때
- 분포 간 overlap 감소를 직관적인 bounded distance로 보고하고 싶을 때
- p-value보다 효과 크기 중심의 drift score가 필요한 screening에서

해석 방법:
- distance가 0에 가까우면 두 이산 분포가 거의 유사하고, 1에 가까울수록 overlap이 작다.
- threshold를 넘으면 기준 분포와 다른 구성 변화 후보로 해석한다.
- category별 확률 차이를 함께 보면 distance를 키운 항목을 설명할 수 있다.
- alarm은 분포 차이 신호이며, 원인 또는 성능 저하 확정은 아니다.

주의점:
- 드문 category의 확률 추정이 불안정하면 distance가 흔들릴 수 있다.
- reference/current에서 category set이 다르면 missing category 처리 기준을 맞춰야 한다.
- threshold는 업무 허용 변동폭이나 정상 구간 replay로 calibration해야 한다.

보고서 문장 예시:

```text
DISCRETE_HELLINGER_DISTANCE로 이산 분포를 비교한 결과,
reference/current 간 Hellinger distance가 기준 threshold를 초과했다.
이는 current 기간의 category 확률 구성이 기준 기간과 달라졌을 가능성을 나타낸다.
다만 낮은 빈도 category의 영향과 category 정의 변경 여부를 함께 확인해야 한다.
```

---

## 변종: HISTOGRAM_HELLINGER_DISTANCE

`HISTOGRAM_HELLINGER_DISTANCE`는 연속형 numeric feature를 histogram으로 이산화한 뒤 reference/current bin 확률의 Hellinger distance를 계산하는 변종이다. 평균 변화뿐 아니라 분포 모양, 꼬리, 특정 구간의 비중 변화까지 하나의 bounded distance로 요약한다. 출력은 histogram distance, bin별 기여, alarm state로 해석한다.

사용 상황:
- numeric feature의 전체 분포 형태가 기준 기간과 달라졌는지 확인할 때
- 평균/분산만으로 설명하기 어려운 구간별 비중 변화를 감시할 때
- feature drift report에서 bounded distance와 histogram 시각화를 함께 제시하고 싶을 때

해석 방법:
- Hellinger distance가 클수록 reference/current histogram overlap이 작다.
- threshold 초과는 numeric feature 분포 형태가 달라졌다는 drift 후보 신호다.
- bin별 확률 차이를 보면 어느 값 구간에서 변화가 컸는지 설명할 수 있다.
- raw histogram과 함께 보면 outlier, tail 증가, 중심 이동을 구분할 수 있다.

주의점:
- bin 경계와 bin 수 선택에 따라 distance가 달라진다.
- current 표본이 적으면 일부 bin 확률이 불안정해질 수 있다.
- feature scale 변경, clipping, missing 처리 변경이 distance를 키울 수 있다.

보고서 문장 예시:

```text
HISTOGRAM_HELLINGER_DISTANCE로 numeric feature 분포를 비교한 결과,
reference/current histogram 간 distance가 threshold를 초과했다.
이는 current 기간의 값 구간별 비중이 기준 기간과 달라졌을 가능성을 나타낸다.
다만 binning 정책과 표본 수에 따라 score가 달라질 수 있으므로, 주요 bin의 확률 차이를 함께 확인해야 한다.
```

---

## 변종: CATEGORICAL_HELLINGER_DISTANCE

`CATEGORICAL_HELLINGER_DISTANCE`는 category별 빈도를 확률분포로 변환해 reference/current의 category composition 차이를 Hellinger distance로 측정하는 변종이다. 신규 category, 사라진 category, 주요 category 비중 변화를 안정적인 0~1 거리로 요약한다. 출력은 categorical Hellinger distance, category별 확률 차이, alarm state로 해석한다.

사용 상황:
- channel, region, device, product type 같은 명목형 feature의 구성 변화를 감시할 때
- 신규 category 유입이나 long-tail category 비중 변화가 drift 후보인지 확인할 때
- category별 비율 차이를 거리 score와 함께 보고해야 할 때

해석 방법:
- distance가 커질수록 category composition overlap이 줄어든다.
- 신규 category나 사라진 category는 distance를 키우는 주요 원인이 될 수 있다.
- alarm이 발생하면 category별 reference/current 비율표로 어느 항목이 바뀌었는지 확인한다.
- 결과는 feature distribution drift 후보로 표현하고 성능 영향은 별도 평가한다.

주의점:
- category normalization, rare category grouping, unknown 처리 기준이 일관되어야 한다.
- low-count category가 많으면 score가 우연 변동에 민감할 수 있다.
- category label 재매핑이나 전처리 변경은 실제 drift처럼 보일 수 있다.

보고서 문장 예시:

```text
CATEGORICAL_HELLINGER_DISTANCE로 category 구성을 비교한 결과,
current 기간의 category 확률분포가 reference 대비 의미 있게 멀어졌다.
이는 일부 category의 유입 비중 또는 long-tail 구성이 달라졌을 가능성을 나타낸다.
다만 rare category 처리와 unknown 매핑 기준이 동일한지 확인한 뒤 drift 후보로 보고해야 한다.
```

---

## SelectionRule 카탈로그

```text
selectionRule HELLINGER_DISTANCE_DEFAULT_USE
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

> Hellinger Distance 카탈로그는 "이 방법이 무엇인가"가 아니라, "어떤 상황에서 어떤 변종을 선택하고 어떤 주의사항과 함께 설명해야 하는가"를 구조화한다.
