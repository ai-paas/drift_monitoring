# CUSUM 알고리즘 변종 목록

## 1. 목적

이 문서는 `CUSUM`를 하나의 고정된 detector로 보지 않고, drift monitoring에서 상황에 따라 선택해야 하는 **알고리즘 변종들의 family**로 정리한다.

핵심 목적은 다음이다.

```text
상황 조건 -> 적절한 CUSUM 계열 변종 -> 출력 metric -> 주의사항 -> LLM 보고서 설명
```

---

## 2. CUSUM의 위치

```text
methodFamily CUSUM
       ├─ algorithmVariant ONE_SIDED_UPPER_CUSUM
       ├─ algorithmVariant ONE_SIDED_LOWER_CUSUM
       ├─ algorithmVariant TWO_SIDED_CUSUM
       └─ algorithmVariant CUSUM_ON_DISTANCE_STREAM
```

`CUSUM`는 cumulative sum control chart 계열에 속한다. 기준 평균 대비 누적 편차가 decision threshold를 넘는지 감시한다.

---

## 3. 공통 개념

```text
methodFamily CUSUM
  purpose ->
    기준 평균 대비 누적 편차가 decision threshold를 넘는지 감시한다.

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

## 변종: ONE_SIDED_UPPER_CUSUM

`ONE_SIDED_UPPER_CUSUM`은 기준 평균보다 높은 방향의 작은 변화가 누적되는지를 감시하는 CUSUM 변종이다. 단일 window에서 큰 spike가 없어도 loss, error rate, latency처럼 증가가 위험 신호인 metric이 지속적으로 높아질 때 alarm을 낼 수 있다. 따라서 변화 방향이 명확히 "상승하면 나쁨"으로 정의된 운영 지표에 적합하다.

이 변종은 다음 상황에 적합하다.

- error rate, loss, latency, reject rate처럼 증가가 품질 저하 신호인 metric을 감시한다.
- 단발성 이상치보다 기준 대비 작은 상승이 지속되는지를 보고 싶다.
- reference mean, allowance parameter, decision threshold를 운영 기준 또는 calibration으로 정할 수 있다.
- alarm 시점 이후 어떤 window에서 누적 편차가 threshold를 넘었는지 보고해야 한다.

해석할 때는 positive CUSUM 값과 alarm state를 함께 본다. Positive CUSUM은 각 시점의 metric이 기준 평균과 allowance를 초과한 정도를 누적한 값이며, threshold를 넘으면 상승 방향 변화가 지속됐다는 alarm으로 해석한다. Alarm 시점은 drift가 처음 발생한 정확한 원인 시점이 아니라, 누적 증거가 운영 threshold를 넘은 시점으로 보고한다.

주의할 점은 reference mean과 allowance parameter 설정이 결과에 직접 영향을 준다는 것이다. Threshold는 보편적 절대 기준이 아니라 false alarm 허용 수준이나 과거 정상 구간 calibration 결과로 설명해야 한다. 계절성, 배치 크기 변화, traffic mix 변화가 있으면 metric 상승이 입력 drift가 아니라 운영 조건 변화일 수 있다. CUSUM 결과만으로 성능 저하 원인을 확정하지 않고 후속 원인 분석을 연결한다.

보고서 문장 예시는 다음과 같다.

```text
error rate를 ONE_SIDED_UPPER_CUSUM으로 모니터링한 결과,
positive CUSUM이 기준 평균 대비 상승 편차를 누적해 decision threshold를 넘었다.
이는 error rate가 작은 폭으로 지속 상승한 성능 변화 후보 신호로 볼 수 있다.
다만 threshold는 과거 정상 구간 calibration에 따른 운영 기준이므로,
traffic mix와 배포 이력, segment별 error rate를 함께 확인해야 한다.
```

---

## 변종: ONE_SIDED_LOWER_CUSUM

`ONE_SIDED_LOWER_CUSUM`은 기준 평균보다 낮은 방향의 작은 변화가 누적되는지를 감시하는 CUSUM 변종이다. Confidence, throughput, acceptance rate처럼 감소가 위험 신호인 metric에서 단발성 하락보다 지속적인 하방 편차를 찾는 데 사용한다. 좋은 방향과 나쁜 방향이 도메인 기준으로 명확히 정해져 있을 때 해석이 안정적이다.

이 변종은 다음 상황에 적합하다.

- confidence, throughput, recall, acceptance rate처럼 감소가 품질 저하 신호인 metric을 감시한다.
- metric의 하락이 일시적인 noise인지 지속적인 변화인지 구분하고 싶다.
- reference mean과 하방향 allowance, decision threshold를 사전에 정의할 수 있다.
- alarm 발생 시점과 하방향 누적 편차의 크기를 보고해야 한다.

해석할 때는 negative CUSUM 값과 alarm state를 확인한다. Negative CUSUM은 각 시점의 metric이 기준 평균보다 낮은 방향으로 벗어난 정도를 누적한 값이며, threshold를 넘으면 감소 방향 변화가 지속됐다는 alarm으로 해석한다. 값이 커졌다는 표현보다 "하방향 누적 편차가 커졌다"는 식으로 방향을 명확히 쓰는 것이 좋다.

주의할 점은 metric에 따라 감소가 항상 나쁜 신호가 아닐 수 있다는 것이다. 예를 들어 latency 감소는 개선일 수 있으므로, 이 변종을 쓰기 전에 감소 방향이 위험이라는 도메인 정의가 필요하다. Threshold와 allowance는 calibration 근거를 함께 보고해야 하며, traffic volume 감소나 데이터 수집 지연이 metric 하락처럼 보일 수 있다. Alarm은 원인 확정이 아니라 추가 확인이 필요한 변화 후보다.

보고서 문장 예시는 다음과 같다.

```text
confidence score를 ONE_SIDED_LOWER_CUSUM으로 모니터링한 결과,
negative CUSUM이 기준 평균 대비 하방향 편차를 누적해 decision threshold를 넘었다.
이는 confidence가 지속적으로 낮아진 성능 변화 후보 신호로 볼 수 있다.
다만 감소 방향이 위험이라는 metric 정의와 threshold calibration 근거를 확인해야 하며,
데이터 수집 지연이나 traffic volume 변화도 함께 점검해야 한다.
```

---

## 변종: TWO_SIDED_CUSUM

`TWO_SIDED_CUSUM`은 기준 평균 대비 상승 방향과 하락 방향의 누적 편차를 동시에 감시하는 변종이다. 변화 방향을 사전에 특정하기 어렵거나, 증가와 감소가 모두 운영상 중요한 score에 사용한다. Positive CUSUM과 negative CUSUM을 함께 산출하므로 어느 방향에서 threshold를 넘었는지까지 보고해야 한다.

이 변종은 다음 상황에 적합하다.

- calibration score, prediction score summary, feature mean처럼 양방향 변화가 모두 의미 있는 metric을 감시한다.
- 증가와 감소 중 어느 쪽이 먼저 나타날지 알기 어렵다.
- 한쪽 방향만 보면 놓칠 수 있는 지속적 shift를 탐지하고 싶다.
- alarm state와 함께 변화 방향을 보고서에 명확히 남겨야 한다.

해석할 때는 positive CUSUM, negative CUSUM, alarm state를 분리해서 읽는다. Positive CUSUM이 threshold를 넘으면 기준보다 높은 방향의 지속 편차를, negative CUSUM이 threshold를 넘으면 기준보다 낮은 방향의 지속 편차를 의미한다. 두 방향 중 어느 값이 alarm을 유발했는지와 alarm 시점의 window를 함께 기록해야 drift 후보의 방향을 설명할 수 있다.

주의할 점은 양방향 감시는 한쪽 감시보다 alarm 기회가 많아 false alarm 가능성이 커질 수 있다는 것이다. Threshold는 양방향 감시 구조에 맞게 calibration해야 하며, 단일 threshold를 기계적으로 재사용하면 alarm 빈도가 의도보다 높아질 수 있다. Metric의 자연 변동성, 계절성, 배포 이벤트가 양방향 CUSUM을 흔들 수 있으므로 reference 기간과 window 정의를 함께 보고한다. Alarm만으로 원인과 성능 영향을 확정하지 않는다.

보고서 문장 예시는 다음과 같다.

```text
calibration metric을 TWO_SIDED_CUSUM으로 모니터링한 결과,
positive CUSUM과 negative CUSUM 중 한 방향의 누적 편차가 decision threshold를 넘었다.
이는 기준 평균 대비 지속적인 score shift가 발생한 drift 후보 신호로 볼 수 있다.
다만 양방향 감시는 false alarm 기회가 늘 수 있으므로,
방향별 threshold calibration과 alarm 발생 window의 운영 이벤트를 함께 확인해야 한다.
```

---

## 변종: CUSUM_ON_DISTANCE_STREAM

`CUSUM_ON_DISTANCE_STREAM`은 원천 feature나 error stream이 아니라, Wasserstein distance, PSI, MMD처럼 window별로 계산된 drift distance의 누적 편차를 감시하는 변종이다. 개별 window의 distance가 한 번 커지는지를 보는 것이 아니라, distance가 기준 수준보다 계속 높게 유지되는지를 CUSUM 방식으로 확인한다. 따라서 작은 분포 차이가 여러 window에 걸쳐 누적되는 상황을 drift 후보 신호로 포착하는 데 적합하다.

이 변종은 다음 상황에 적합하다.

- reference window와 current window 사이의 distance score가 주기적으로 산출된다.
- 단일 distance spike보다 distance의 지속적 상승 또는 누적 편차가 중요한 운영 질문이다.
- 원 feature별 원인보다 전체 분포 변화 후보를 먼저 screening하고 싶다.
- distance 산출 window와 CUSUM 누적 window를 분리해서 기록할 수 있다.

해석할 때는 `DISTANCE_CUSUM`과 `ALARM_STATE`를 함께 본다. `DISTANCE_CUSUM`은 window별 distance가 기준 수준을 초과한 정도를 누적한 값이며, threshold를 넘으면 분포 거리의 상승 편차가 지속됐다는 alarm으로 해석한다. 여기서 alarm은 distance 자체가 큰 한 시점이 아니라, distance stream의 누적 증거가 운영 threshold를 넘은 시점이다.

주의할 점은 distance 산출 방식의 변동성이 CUSUM 결과에 그대로 들어간다는 것이다. 표본 수가 작은 window, feature scaling 변경, category cardinality 변화가 있으면 distance가 불안정해질 수 있다. Threshold는 보편적 기준이 아니라 distance metric과 window 설계에 맞춘 calibration 결과로 설명해야 한다. 이 결과만으로 어떤 feature가 원인인지 또는 성능 저하가 발생했는지는 확정하지 않는다.

보고서 문장 예시는 다음과 같다.

```text
window별 Wasserstein distance를 CUSUM_ON_DISTANCE_STREAM으로 모니터링한 결과,
DISTANCE_CUSUM이 기준 distance 수준 대비 상승 편차를 누적해 alarm threshold를 넘었다.
이는 단발성 spike보다 분포 거리의 지속적 증가가 관찰된 drift 후보 신호로 볼 수 있다.
다만 distance 산출 window의 표본 수와 feature scaling 변화에 민감할 수 있으므로,
원 feature별 distance와 운영 이벤트를 함께 확인해야 한다.
```

---

## SelectionRule 카탈로그

```text
selectionRule CUSUM_DEFAULT_USE
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

> CUSUM 카탈로그는 "이 방법이 무엇인가"가 아니라, "어떤 상황에서 어떤 변종을 선택하고 어떤 주의사항과 함께 설명해야 하는가"를 구조화한다.
