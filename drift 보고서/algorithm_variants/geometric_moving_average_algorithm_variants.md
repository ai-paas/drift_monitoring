# Geometric Moving Average 알고리즘 변종 목록

## 1. 목적

이 문서는 `Geometric Moving Average`를 하나의 고정된 detector로 보지 않고, drift monitoring에서 상황에 따라 선택해야 하는 **알고리즘 변종들의 family**로 정리한다.

핵심 목적은 다음이다.

```text
상황 조건 -> 적절한 Geometric Moving Average 계열 변종 -> 출력 metric -> 주의사항 -> LLM 보고서 설명
```

---

## 2. Geometric Moving Average의 위치

```text
methodFamily GEOMETRIC_MOVING_AVERAGE
       ├─ algorithmVariant GMA_CONTROL_CHART
       ├─ algorithmVariant GMA_ONE_SIDED
       └─ algorithmVariant GMA_WITH_EMPIRICAL_LIMIT
```

`Geometric Moving Average`는 drift monitoring method 계열에 속한다. Geometric Moving Average 계열을 drift monitoring 문맥에서 입력 데이터와 운영 목적에 따라 선택 가능한 변종으로 정리한다.

---

## 3. 공통 개념

```text
methodFamily GEOMETRIC_MOVING_AVERAGE
  purpose ->
    Geometric Moving Average 계열을 drift monitoring 문맥에서 입력 데이터와 운영 목적에 따라 선택 가능한 변종으로 정리한다.

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

## 변종: GMA_CONTROL_CHART

`GMA_CONTROL_CHART`는 관측 지표의 geometric moving average 통계량을 관리도 형태로 추적하는 streaming detector 변종이다. 최근 값에 더 큰 가중치를 두면서도 과거 정보를 완전히 버리지 않아, 점진적인 평균 이동이나 지속적인 작은 변화에 민감하게 반응한다. 출력은 GMA statistic, control limit, alarm state로 해석한다.

사용 상황:
- 오류율, 지연시간, 품질 점수처럼 시간 순서가 있는 운영 지표를 지속적으로 감시할 때
- 단일 큰 spike보다 누적되는 작은 변화나 점진적인 shift를 포착하고 싶을 때
- reference/current 배치 비교가 아니라 online monitoring 형태로 alarm을 운영할 때

해석 방법:
- GMA statistic이 관리 한계에 가까워지거나 초과하면 최근 관측값 흐름이 기준 상태에서 벗어났다는 후보 신호다.
- control limit은 운영 calibration 또는 과거 정상 구간에서 산정한 기준으로 해석한다.
- alarm state는 해당 시점의 통계량이 한계를 넘었다는 표시이며, 변화가 일시 spike인지 지속 shift인지는 trend로 확인한다.
- 보고서에서는 alarm 시점, GMA statistic 방향, control limit, alarm 전후 raw metric 변화를 함께 제시한다.

주의점:
- smoothing parameter가 크면 최근 변화에 민감하지만 false alarm이 늘 수 있고, 작으면 반응이 늦어질 수 있다.
- control limit 산정 구간이 실제 정상 상태를 대표하지 않으면 alarm 해석이 흔들린다.
- label이 없는 운영 지표에서는 성능 저하나 concept drift를 단정하지 않고 지표 변화 후보로 표현한다.

보고서 문장 예시:

```text
운영 지표를 GMA_CONTROL_CHART로 모니터링한 결과,
GMA statistic이 control limit에 근접하거나 초과하는 구간이 관측됐다.
이는 최근 지표 흐름이 기준 상태에서 점진적으로 벗어났을 가능성을 나타내는 drift 후보 신호다.
다만 smoothing parameter와 control limit 산정 방식에 따라 민감도가 달라지므로, alarm 전후 raw metric 추세를 함께 확인해야 한다.
```

---

## 변종: GMA_ONE_SIDED

`GMA_ONE_SIDED`는 GMA 통계량을 한쪽 방향 변화에 맞춰 감시하는 변종이다. 지표가 올라가는 경우만 위험하거나, 반대로 낮아지는 경우만 위험한 운영 지표에서 양방향 관리도보다 명확한 alarm 기준을 제공한다. 출력은 방향이 지정된 GMA statistic, one-sided control limit, alarm state로 해석한다.

사용 상황:
- 오류율, 지연시간, 불량률처럼 증가 방향만 drift 후보로 보고 싶을 때
- 성공률, 처리율, recall처럼 감소 방향만 위험 신호인 지표를 감시할 때
- 양방향 변화보다 운영상 관심 있는 방향의 조기 alarm이 더 중요한 streaming monitoring에서

해석 방법:
- 지정한 방향의 GMA statistic이 one-sided limit을 넘으면 해당 방향으로 누적 변화 후보가 생긴 것이다.
- alarm은 방향 조건과 threshold 조건이 동시에 충족됐다는 뜻이며, 반대 방향 변화는 이 변종의 주 관심 대상이 아니다.
- raw metric trend와 함께 보면 alarm이 일시 spike인지, 방향성 있는 지속 shift인지 구분할 수 있다.
- 보고서에는 upper 또는 lower 방향을 명시하고, 관측된 변화 방향이 설정 방향과 일치하는지 함께 적는다.

주의점:
- 방향을 잘못 설정하면 중요한 반대 방향 변화를 놓칠 수 있다.
- one-sided limit은 보편 기준이 아니라 정상 구간 calibration 또는 운영 정책으로 산정해야 한다.
- label 없는 지표에서는 model performance drift가 아니라 운영 지표의 방향성 변화 후보로 표현한다.

보고서 문장 예시:

```text
운영 지표를 GMA_ONE_SIDED로 모니터링한 결과,
지정한 upper 방향의 GMA statistic이 one-sided control limit을 초과했다.
이는 최근 지표가 기준 상태보다 상승하는 방향으로 누적 변화했을 가능성을 나타낸다.
다만 방향 설정과 control limit calibration에 따라 alarm 민감도가 달라지므로, raw metric 추세와 운영 이벤트를 함께 확인해야 한다.
```

---

## 변종: GMA_WITH_EMPIRICAL_LIMIT

`GMA_WITH_EMPIRICAL_LIMIT`는 이론적 control limit 대신 과거 정상 구간이나 bootstrap, replay 결과에서 얻은 경험적 한계를 사용하는 GMA 변종이다. 지표 분포가 정규 가정에 잘 맞지 않거나 운영상 허용 변동폭을 데이터 기반으로 정해야 할 때 유용하다. 출력은 GMA statistic, empirical limit, limit 초과 alarm으로 해석한다.

사용 상황:
- 정상 구간의 분포가 비대칭이거나 heavy-tail이라 이론적 관리 한계가 맞지 않을 때
- 과거 정상 운영 데이터를 replay해 false alarm 수준을 맞추고 싶을 때
- 업무 정책상 허용 가능한 변동폭을 통계 가정보다 경험 데이터 기준으로 정해야 할 때

해석 방법:
- GMA statistic이 empirical limit을 넘으면 과거 정상 구간에서 보기 어려운 누적 변화 후보가 발생한 것이다.
- empirical limit은 어떤 기간, 표본, replay 방식으로 산정했는지와 함께 읽어야 한다.
- alarm은 경험적 정상 범위 이탈 신호이며, 원인 또는 성능 저하 확정은 아니다.
- window별 limit 안정성과 alarm 재현성을 함께 보면 threshold가 과하게 민감한지 판단할 수 있다.

주의점:
- 정상 구간 자체에 drift나 계절성이 섞여 있으면 empirical limit이 왜곡된다.
- 운영 환경이 바뀌면 과거 limit을 그대로 쓰기 어렵고 재보정이 필요하다.
- empirical limit은 설명력이 좋지만 산정 방식이 불명확하면 보고서 재현성이 떨어진다.

보고서 문장 예시:

```text
GMA_WITH_EMPIRICAL_LIMIT로 운영 지표를 추적한 결과,
GMA statistic이 과거 정상 구간 replay에서 산정한 empirical limit을 초과했다.
이는 현재 지표 흐름이 경험적 정상 범위를 벗어난 drift 후보 신호로 해석할 수 있다.
다만 limit 산정 구간과 계절성 영향에 따라 결과가 달라질 수 있으므로, 정상 구간 정의와 재보정 필요성을 함께 보고해야 한다.
```

---

## SelectionRule 카탈로그

```text
selectionRule GEOMETRIC_MOVING_AVERAGE_DEFAULT_USE
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

> Geometric Moving Average 카탈로그는 "이 방법이 무엇인가"가 아니라, "어떤 상황에서 어떤 변종을 선택하고 어떤 주의사항과 함께 설명해야 하는가"를 구조화한다.
