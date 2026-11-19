# HDDM-A 알고리즘 변종 목록

## 1. 목적

이 문서는 `HDDM-A`를 하나의 고정된 detector로 보지 않고, drift monitoring에서 상황에 따라 선택해야 하는 **알고리즘 변종들의 family**로 정리한다.

핵심 목적은 다음이다.

```text
상황 조건 -> 적절한 HDDM-A 계열 변종 -> 출력 metric -> 주의사항 -> LLM 보고서 설명
```

---

## 2. HDDM-A의 위치

```text
methodFamily HDDM_A
       ├─ algorithmVariant HDDM_A_HOEFFDING_BOUND
       ├─ algorithmVariant HDDM_A_WARNING_DRIFT
       └─ algorithmVariant HDDM_A_TWO_SIDED
```

`HDDM-A`는 drift monitoring method 계열에 속한다. HDDM-A 계열을 drift monitoring 문맥에서 입력 데이터와 운영 목적에 따라 선택 가능한 변종으로 정리한다.

---

## 3. 공통 개념

```text
methodFamily HDDM_A
  purpose ->
    HDDM-A 계열을 drift monitoring 문맥에서 입력 데이터와 운영 목적에 따라 선택 가능한 변종으로 정리한다.

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

## 변종: HDDM_A_HOEFFDING_BOUND

`HDDM_A_HOEFFDING_BOUND`는 Hoeffding bound를 이용해 streaming error 또는 binary signal의 평균 변화가 통계적으로 보기 어려운 수준인지 감시하는 HDDM-A 변종이다. 과거 누적 구간과 최근 구간의 평균 차이를 bound와 비교해 drift 후보를 찾는다. 출력은 mean difference, Hoeffding bound, warning/drift alarm state로 해석한다.

사용 상황:
- 온라인 모델의 error indicator, hit/miss, binary quality flag처럼 순차적으로 들어오는 이진 신호를 감시할 때
- 고정 reference window보다 누적 streaming evidence 기반의 변화를 보고 싶을 때
- abrupt drift 또는 비교적 명확한 평균 변화 후보를 조기에 찾고 싶을 때

해석 방법:
- 최근 평균과 기준 평균의 차이가 Hoeffding bound를 넘으면 우연 변동으로 보기 어려운 drift 후보로 본다.
- bound가 작아질수록 누적 표본 근거가 강해져 작은 변화도 감지될 수 있다.
- alarm은 평균 변화의 통계적 신호이며, 원인이나 성능 저하 확정은 아니다.
- 보고서에는 관측한 error rate 변화 방향, 감지 시점, bound 설정을 함께 적는다.

주의점:
- 입력이 독립적인 순차 관측이라는 가정이 약하면 alarm 해석이 흔들릴 수 있다.
- label 지연이 있거나 error indicator 품질이 낮으면 detector 결과도 지연되거나 왜곡된다.
- delta, warning threshold, drift threshold는 false alarm 수준에 맞춰 calibration해야 한다.

보고서 문장 예시:

```text
HDDM_A_HOEFFDING_BOUND로 streaming error signal을 감시한 결과,
최근 구간의 평균 변화가 Hoeffding bound를 초과해 drift 후보 alarm이 발생했다.
이는 current stream의 error 발생 수준이 이전 누적 기준과 달라졌을 가능성을 나타낸다.
다만 detector 결과만으로 원인이나 성능 저하를 확정하지 않고, label 지연과 threshold calibration 근거를 함께 확인해야 한다.
```

---

## 변종: HDDM_A_WARNING_DRIFT

`HDDM_A_WARNING_DRIFT`는 HDDM-A의 warning level과 drift level을 분리해 streaming 변화의 심각도를 단계적으로 표시하는 변종이다. warning은 변화 후보가 커지고 있음을, drift는 더 강한 기준을 넘었음을 의미한다. 출력은 warning state, drift state, 감지 시점, 평균 변화량으로 해석한다.

사용 상황:
- 즉시 모델 교체보다 사전 점검, 샘플 보존, 원인 분석 준비가 필요한 운영 monitoring에서
- alarm을 warning과 drift로 나누어 대응 우선순위를 정해야 할 때
- error rate 변화가 누적되는지 관찰하면서 조기 경보를 받고 싶을 때

해석 방법:
- warning은 drift 확정이 아니라 최근 평균 변화가 주의 구간에 들어왔다는 신호다.
- drift alarm은 warning보다 강한 threshold를 통과한 상태로, 후속 대응을 검토할 수준의 변화 후보로 본다.
- warning에서 drift로 이어지는 시간 간격은 변화가 빠르게 커졌는지 판단하는 보조 정보다.
- 보고서에는 warning 발생 시점과 drift 발생 시점을 구분해 적는다.

주의점:
- warning이 반드시 drift로 이어지는 것은 아니므로 과잉 대응을 피해야 한다.
- warning threshold가 낮으면 민감하지만 false alarm이 늘 수 있다.
- operational action과 연결하려면 warning/drift별 대응 정책이 사전에 정의되어야 한다.

보고서 문장 예시:

```text
HDDM_A_WARNING_DRIFT 감시 결과, 먼저 warning 상태가 발생한 뒤 drift 기준도 초과했다.
이는 streaming error 평균이 기준 상태에서 벗어나는 방향으로 누적되고 있음을 보여주는 단계적 신호다.
warning은 사전 점검 신호, drift는 더 강한 변화 후보 신호로 구분해 해석해야 한다.
다만 threshold 민감도와 label 지연 영향을 확인한 뒤 운영 대응 여부를 결정해야 한다.
```

---

## 변종: HDDM_A_TWO_SIDED

`HDDM_A_TWO_SIDED`는 streaming 평균이 증가하거나 감소하는 양쪽 방향 모두에서 Hoeffding bound를 적용하는 HDDM-A 변종이다. 오류율 증가뿐 아니라 성공률, 승인율, 품질 score처럼 상승과 하락 모두 운영상 의미가 있을 때 사용한다. 출력은 변화 방향, mean difference, two-sided alarm state로 해석한다.

사용 상황:
- 지표가 상승해도 하락해도 데이터 생성 과정 변화 후보가 되는 경우
- error indicator뿐 아니라 binary conversion, approval, success flag 등 방향 해석이 업무별로 달라지는 신호를 감시할 때
- 단방향 detector를 쓰기 전에 변화 방향을 탐색적으로 확인하고 싶을 때

해석 방법:
- 양의 mean difference alarm은 최근 평균이 기준보다 높아진 변화 후보를 뜻한다.
- 음의 mean difference alarm은 최근 평균이 기준보다 낮아진 변화 후보를 뜻한다.
- two-sided 설정에서는 p-value 또는 threshold 해석이 단방향보다 보수적일 수 있다.
- 보고서에는 alarm 여부뿐 아니라 상승/하락 방향을 반드시 함께 적는다.

주의점:
- 방향별 업무 의미가 다르므로 alarm 방향을 원인 또는 성능 저하로 바로 번역하지 않는다.
- 양방향 감시는 단방향 감시보다 false alarm 관리 기준이 달라질 수 있다.
- 지표 정의가 바뀌면 상승/하락 방향 해석도 달라질 수 있다.

보고서 문장 예시:

```text
HDDM_A_TWO_SIDED로 streaming binary signal을 감시한 결과,
최근 평균이 기준 평균보다 낮아지는 방향에서 two-sided alarm이 발생했다.
이는 current stream의 평균 수준이 이전 누적 기준과 달라졌을 가능성을 나타낸다.
다만 상승과 하락의 업무 의미가 다르므로, 지표 정의와 방향별 운영 영향을 분리해 해석해야 한다.
```

---

## SelectionRule 카탈로그

```text
selectionRule HDDM_A_DEFAULT_USE
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

> HDDM-A 카탈로그는 "이 방법이 무엇인가"가 아니라, "어떤 상황에서 어떤 변종을 선택하고 어떤 주의사항과 함께 설명해야 하는가"를 구조화한다.
