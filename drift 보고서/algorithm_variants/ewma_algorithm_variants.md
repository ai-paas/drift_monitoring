# EWMA 알고리즘 변종 목록

## 1. 목적

이 문서는 `EWMA`를 하나의 고정된 detector로 보지 않고, drift monitoring에서 상황에 따라 선택해야 하는 **알고리즘 변종들의 family**로 정리한다.

핵심 목적은 다음이다.

```text
상황 조건 -> 적절한 EWMA 계열 변종 -> 출력 metric -> 주의사항 -> LLM 보고서 설명
```

---

## 2. EWMA의 위치

```text
methodFamily EWMA
       ├─ algorithmVariant EWMA_UNIVARIATE_CONTROL_CHART
       ├─ algorithmVariant EWMA_ONE_SIDED
       └─ algorithmVariant EWMA_BASELINE_REPLAY_THRESHOLD
```

`EWMA`는 exponentially weighted moving average control chart 계열에 속한다. 최근 관측값에 더 큰 가중치를 둔 평균이 관리 한계를 벗어나는지 감시한다.

---

## 3. 공통 개념

```text
methodFamily EWMA
  purpose ->
    최근 관측값에 더 큰 가중치를 둔 평균이 관리 한계를 벗어나는지 감시한다.

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

## 변종: EWMA_UNIVARIATE_CONTROL_CHART

`EWMA_UNIVARIATE_CONTROL_CHART`는 하나의 운영 지표를 시간 순서대로 추적하면서 최근 값에 더 큰 가중치를 둔 평균이 관리 한계를 벗어나는지 보는 변종이다. 원시 지표가 조금씩 나빠지는 gradual drift를 부드럽게 잡아내는 데 적합하다. 출력은 EWMA 값, 상한/하한 관리 한계, alarm 상태로 해석한다.

사용 상황:
- error rate, loss, confidence, latency처럼 단일 수치 지표를 지속적으로 감시할 때
- 급격한 spike보다 서서히 누적되는 변화 후보를 놓치고 싶지 않을 때
- baseline 기간의 평균, 분산, 관리 한계 산정 방식이 정해져 있을 때

해석 방법:
- EWMA 값은 최근 관측값을 더 크게 반영한 지표의 누적 추세다.
- EWMA 값이 UCL을 넘으면 상방 변화 후보, LCL 아래로 내려가면 하방 변화 후보로 본다.
- alarm이 발생한 시점은 원시 값 하나가 튄 시점이 아니라 누적 추세가 관리 한계를 벗어난 시점이다.
- 원시 시계열과 함께 보면 일시적 이상치인지 지속적 변화인지 더 분명하게 해석할 수 있다.

주의점:
- smoothing factor가 크면 빠르게 반응하지만 false alarm이 늘 수 있고, 작으면 안정적이지만 감지가 늦을 수 있다.
- 관리 한계는 운영 정책과 baseline calibration의 결과이지 모든 지표에 통하는 절대 기준이 아니다.
- label 없는 지표에서는 성능 저하를 단정하지 말고 지표 변화 신호로 표현한다.

보고서 문장 예시:

```text
단일 운영 지표를 EWMA_UNIVARIATE_CONTROL_CHART로 모니터링한 결과,
EWMA 값이 기준 관리 한계에 접근하거나 초과하는 구간이 확인됐다.
이는 최근 관측값을 반영한 누적 추세가 baseline 범위를 벗어나는 drift 후보 신호로 볼 수 있다.
다만 smoothing factor와 관리 한계 산정 방식에 따라 민감도가 달라지므로 원시 지표 추세를 함께 확인해야 한다.
```

---

## 변종: EWMA_ONE_SIDED

`EWMA_ONE_SIDED`는 관심 있는 방향의 변화만 감시하는 EWMA 변종이다. 예를 들어 오류율 증가는 위험하지만 오류율 감소는 alarm 대상이 아닐 때, 또는 confidence 감소만 운영 리스크로 볼 때 사용한다. 출력은 EWMA 값, 한쪽 관리 한계, 해당 방향의 alarm 여부로 읽는다.

사용 상황:
- 오류율 증가, latency 증가, confidence 감소처럼 악화 방향이 명확할 때
- 반대 방향 변화는 개선 또는 정상 변동으로 처리해도 되는 지표일 때
- 운영 정책상 alert를 한쪽 위험 방향에 집중하고 싶을 때

해석 방법:
- EWMA 값이 사전에 정한 위험 방향의 one-sided limit을 넘으면 drift 후보 alarm으로 본다.
- 반대 방향의 큰 변화는 이 변종의 alarm 조건이 아니므로 별도 분석 없이는 의미를 과장하지 않는다.
- alarm 시점은 지표가 위험 방향으로 누적 이동했다는 뜻이며, 개별 관측값 하나의 급변만을 의미하지 않는다.
- 보고서에서는 어떤 방향을 감시했는지 반드시 함께 적어야 한다.

주의점:
- 방향성 가설을 사전에 정하지 않으면 결과를 사후적으로 유리하게 해석할 위험이 있다.
- 양방향 변화가 모두 중요한 지표에는 two-sided 관리도를 쓰는 편이 적합하다.
- label 지연이나 지표 집계 지연이 있으면 alarm 시점과 실제 운영 변화 시점이 다를 수 있다.

보고서 문장 예시:

```text
악화 방향 지표를 EWMA_ONE_SIDED로 모니터링한 결과,
EWMA 값이 사전에 정의한 one-sided limit을 향해 상승하거나 초과했다.
이는 해당 지표가 위험 방향으로 누적 이동했다는 drift 후보 신호로 해석할 수 있다.
다만 반대 방향 변화는 이 설정의 탐지 대상이 아니며, 방향성 기준은 운영 정책에 근거해 해석해야 한다.
```

---

## 변종: EWMA_BASELINE_REPLAY_THRESHOLD

`EWMA_BASELINE_REPLAY_THRESHOLD`는 정규성 같은 이론 가정보다 과거 정상 기간을 다시 흘려보내며 경험적 관리 한계를 정하는 변종이다. baseline replay에서 기대 false alarm 수준을 맞춘 뒤, current 기간의 EWMA가 그 한계를 넘는지 본다. 출력은 empirical UCL/LCL, 목표 false alarm rate, current alarm 상태로 해석한다.

사용 상황:
- 지표 분포가 비정규적이거나 계절성, 운영 주기성이 있어 이론 관리 한계가 맞지 않을 때
- 과거 정상 기간 데이터가 충분하고 운영상 허용 가능한 false alarm rate를 정할 수 있을 때
- threshold를 실제 운영 데이터의 변동성에 맞춰 calibration하려 할 때

해석 방법:
- empirical UCL/LCL은 baseline replay에서 관측된 정상 변동 범위를 반영한 관리 한계다.
- current EWMA가 이 한계를 넘으면 과거 정상 변동으로 설명하기 어려운 변화 후보로 본다.
- 목표 false alarm rate가 낮을수록 threshold는 보수적이고, 높을수록 더 민감하게 반응한다.
- alarm 여부뿐 아니라 baseline replay에서 설정된 한계와 current EWMA의 거리도 함께 읽는다.

주의점:
- baseline 기간이 실제 정상 상태를 대표하지 못하면 threshold 자체가 왜곡된다.
- 운영 환경이 이미 바뀐 뒤의 기간을 baseline에 넣으면 drift 후보가 정상으로 흡수될 수 있다.
- 경험적 threshold는 선택한 기간과 replay 방식에 의존하므로 보편적 절대 기준처럼 표현하지 않는다.

보고서 문장 예시:

```text
과거 정상 기간을 replay해 EWMA_BASELINE_REPLAY_THRESHOLD 기준을 산정한 결과,
current EWMA 값이 경험적 관리 한계와 비교해 높은 구간을 보였다.
이는 과거 정상 변동 범위로 설명하기 어려운 지표 변화 후보로 해석할 수 있다.
다만 baseline 기간의 대표성과 목표 false alarm rate 설정이 threshold 신뢰도를 좌우하므로 해당 근거를 함께 확인해야 한다.
```

---

## SelectionRule 카탈로그

```text
selectionRule EWMA_DEFAULT_USE
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

> EWMA 카탈로그는 "이 방법이 무엇인가"가 아니라, "어떤 상황에서 어떤 변종을 선택하고 어떤 주의사항과 함께 설명해야 하는가"를 구조화한다.
