# BOCD 알고리즘 변종 목록

## 1. 목적

이 문서는 `BOCD`를 하나의 고정된 detector로 보지 않고, drift monitoring에서 상황에 따라 선택해야 하는 **알고리즘 변종들의 family**로 정리한다.

핵심 목적은 다음이다.

```text
상황 조건 -> 적절한 BOCD 계열 변종 -> 출력 metric -> 주의사항 -> LLM 보고서 설명
```

---

## 2. BOCD의 위치

```text
methodFamily BOCD
       ├─ algorithmVariant BAYESIAN_ONLINE_CHANGE_POINT_GAUSSIAN
       ├─ algorithmVariant BOCD_HAZARD_RATE_VARIANT
       └─ algorithmVariant BOCD_PREDICTIVE_PROBABILITY
```

`BOCD`는 drift monitoring method 계열에 속한다. BOCD 계열을 drift monitoring 문맥에서 입력 데이터와 운영 목적에 따라 선택 가능한 변종으로 정리한다.

---

## 3. 공통 개념

```text
methodFamily BOCD
  purpose ->
    BOCD 계열을 drift monitoring 문맥에서 입력 데이터와 운영 목적에 따라 선택 가능한 변종으로 정리한다.

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

## 변종: BAYESIAN_ONLINE_CHANGE_POINT_GAUSSIAN

`BAYESIAN_ONLINE_CHANGE_POINT_GAUSSIAN`은 streaming signal이 Gaussian 관측 모델을 따른다고 보고, 새 관측치가 들어올 때마다 change point 가능성과 run length 분포를 갱신하는 BOCD 변종이다. 기준 window와 현재 window를 한 번에 비교하기보다 시간 순서대로 변화 시점을 추정한다. drift monitoring에서는 score, residual, KPI처럼 연속형 시계열의 평균이나 분산 구조가 갑자기 바뀌는지를 온라인으로 감시할 때 사용한다.

이 변종은 다음 상황에 적합하다.

- 관측치가 시간 순서대로 들어오며 alarm 시점이 중요하다.
- 연속형 signal이 Gaussian 관측 모델로 어느 정도 설명 가능하다.
- reference/current batch 비교보다 변화가 시작된 시점을 추정하고 싶다.
- 평균 또는 분산이 갑자기 바뀌는 운영 KPI, score, error stream을 모니터링한다.

해석할 때는 change point posterior, run length posterior, alarm state를 함께 본다. Change point posterior가 높아지는 시점은 최근 관측치가 이전 run과 같은 상태에서 생성됐다는 설명력이 낮아졌다는 뜻이다. Run length가 갑자기 짧아지면 모델이 새 구간의 시작 가능성을 높게 보고 있다는 신호다. Alarm은 posterior나 run length 기준이 운영 threshold를 넘었을 때의 정책적 판정으로 해석한다.

주의할 점은 Gaussian 관측 가정이 맞지 않으면 alarm이 과도하거나 늦게 발생할 수 있다는 것이다. BOCD는 변화 시점 후보를 제시하지만 업무 원인이나 모델 성능 저하를 확정하지 않는다. 초기 구간에서는 prior와 hyperparameter의 영향이 크고, noise가 큰 signal은 짧은 run length 변동이 자주 나타날 수 있다. Threshold, hazard 설정, 최소 지속 시간 기준을 보고서에 함께 남겨야 한다.

보고서 문장 예시는 다음과 같다.

```text
연속형 score stream을 BAYESIAN_ONLINE_CHANGE_POINT_GAUSSIAN으로 모니터링한 결과,
특정 시점 이후 change point posterior가 상승하고 추정 run length가 짧아졌다.
이는 해당 시점 부근에서 score 생성 분포가 바뀌었을 가능성을 나타내는 drift 후보 신호다.
다만 Gaussian 관측 가정과 hazard 설정의 영향을 받으므로,
동일 시점의 KPI, 배포 이력, segment별 분포를 함께 확인해야 한다.
```

---

## 변종: BOCD_HAZARD_RATE_VARIANT

`BOCD_HAZARD_RATE_VARIANT`는 BOCD에서 change point가 얼마나 자주 발생할 것으로 가정할지, 즉 hazard rate 설정을 명시적으로 조정하는 변종이다. 같은 관측 데이터라도 hazard가 높으면 변화 후보에 더 민감하게 반응하고, hazard가 낮으면 더 긴 안정 구간을 선호한다. drift monitoring에서는 false alarm 비용과 탐지 지연 비용을 운영 목적에 맞게 조정해야 할 때 사용한다.

이 변종은 다음 상황에 적합하다.

- 변화가 자주 발생하는 운영 환경과 드문 환경을 구분해 설정해야 한다.
- alarm 민감도와 안정성을 hazard rate로 조정하고 싶다.
- 배포, 캠페인, 계절 이벤트 등 변화 빈도에 대한 사전 지식이 있다.
- 동일한 stream에 대해 민감한 감시 모드와 보수적 감시 모드를 비교한다.

해석할 때는 alarm 발생 여부만 보지 말고 hazard 설정을 함께 읽어야 한다. Hazard가 높게 설정된 경우 posterior가 더 쉽게 change point 쪽으로 이동할 수 있으므로 빠른 감지에 유리하지만 false alarm이 늘 수 있다. Hazard가 낮으면 run length가 길게 유지되기 쉬워 안정적이지만 짧은 변화나 급격한 변화를 늦게 잡을 수 있다. 보고서에서는 posterior 상승이 데이터 신호 때문인지, 설정 민감도 때문인지 구분해 설명한다.

주의할 점은 hazard rate가 통계 모델의 사전 가정이지 관측된 변화 빈도 그 자체가 아니라는 것이다. 운영 환경이 바뀌었는데 hazard를 고정하면 alarm 품질이 달라질 수 있다. Hazard 조정으로 나온 alarm을 서로 비교할 때는 같은 threshold, 같은 관측 모델, 같은 전처리를 사용해야 한다. 변화가 감지되더라도 원인 확정에는 배포 이력, 데이터 파이프라인, 외부 이벤트 확인이 필요하다.

보고서 문장 예시는 다음과 같다.

```text
KPI stream을 BOCD_HAZARD_RATE_VARIANT로 모니터링한 결과,
현재 hazard 설정에서 change point posterior가 상승해 alarm 기준에 근접했다.
이는 최근 구간이 이전 run과 다른 상태일 가능성을 시사하는 drift 후보 신호다.
다만 hazard rate는 변화 빈도에 대한 사전 가정이므로,
민감도 설정별 결과와 실제 운영 이벤트를 함께 비교해야 한다.
```

---

## 변종: BOCD_PREDICTIVE_PROBABILITY

`BOCD_PREDICTIVE_PROBABILITY`는 새 관측치가 현재까지의 run length 가설들에서 얼마나 그럴듯한지를 predictive probability로 평가하는 BOCD 변종이다. Change point posterior를 직접 보는 대신, 최근 관측치의 예측 가능성이 낮아지는 패턴을 drift 후보 신호로 읽는다. drift monitoring에서는 alarm을 내기 전 이상한 관측치가 누적되는지, 또는 모델이 현재 상태를 계속 잘 설명하는지를 추적할 때 유용하다.

이 변종은 다음 상황에 적합하다.

- streaming signal에서 갑작스러운 예측 가능성 저하를 감시한다.
- change point alarm뿐 아니라 사전 warning score가 필요하다.
- 관측 모델이 현재 run을 얼마나 잘 설명하는지 시간별로 보고하고 싶다.
- posterior alarm이 늦게 뜨기 전에 low predictive probability 구간을 확인한다.

해석할 때는 predictive probability가 낮아지는 시점과 지속 시간을 함께 본다. 값이 낮다는 것은 현재까지의 run length 가설과 관측 모델이 새 값을 잘 설명하지 못한다는 뜻이다. 일회성 하락은 outlier일 수 있지만, 낮은 값이 여러 시점 반복되거나 change point posterior 상승과 동반되면 분포 변화 후보로 볼 수 있다. Threshold는 과거 안정 구간에서의 predictive probability 분포를 기준으로 정하는 것이 적절하다.

주의할 점은 predictive probability가 낮다고 해서 항상 구조적 drift를 의미하지는 않는다는 것이다. 단일 이상치, 수집 지연, missing 처리, seasonal spike도 같은 신호를 만들 수 있다. 관측 모델이 부적절하면 정상 구간에서도 probability가 낮게 나타날 수 있다. 이 변종은 warning 성격이 강하므로 alarm, run length, 후속 window 비교와 함께 해석해야 한다.

보고서 문장 예시는 다음과 같다.

```text
실시간 residual stream을 BOCD_PREDICTIVE_PROBABILITY로 모니터링한 결과,
최근 구간에서 predictive probability가 과거 안정 범위보다 낮게 유지됐다.
이는 현재 관측 모델이 새 값을 잘 설명하지 못한다는 drift 후보 또는 warning 신호다.
다만 일회성 이상치나 데이터 수집 지연도 같은 패턴을 만들 수 있으므로,
change point posterior와 원천 데이터 품질 점검을 함께 수행해야 한다.
```

---

## SelectionRule 카탈로그

```text
selectionRule BOCD_DEFAULT_USE
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

> BOCD 카탈로그는 "이 방법이 무엇인가"가 아니라, "어떤 상황에서 어떤 변종을 선택하고 어떤 주의사항과 함께 설명해야 하는가"를 구조화한다.
