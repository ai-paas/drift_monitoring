# KSWIN 알고리즘 변종 목록

## 1. 목적

이 문서는 `KSWIN`를 하나의 고정된 detector로 보지 않고, drift monitoring에서 상황에 따라 선택해야 하는 **알고리즘 변종들의 family**로 정리한다.

핵심 목적은 다음이다.

```text
상황 조건 -> 적절한 KSWIN 계열 변종 -> 출력 metric -> 주의사항 -> LLM 보고서 설명
```

---

## 2. KSWIN의 위치

```text
methodFamily KSWIN
       ├─ algorithmVariant KSWIN_STANDARD
       ├─ algorithmVariant KSWIN_WITH_SUBSAMPLING
       └─ algorithmVariant KSWIN_NUMERIC_STREAM
```

`KSWIN`는 drift monitoring method 계열에 속한다. KSWIN 계열을 drift monitoring 문맥에서 입력 데이터와 운영 목적에 따라 선택 가능한 변종으로 정리한다.

---

## 3. 공통 개념

```text
methodFamily KSWIN
  purpose ->
    KSWIN 계열을 drift monitoring 문맥에서 입력 데이터와 운영 목적에 따라 선택 가능한 변종으로 정리한다.

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

## 변종: KSWIN_STANDARD

`KSWIN_STANDARD`는 sliding window 안에서 과거 reference 부분과 최근 current 부분을 나누고, 두 부분의 분포 차이를 KS test로 감시하는 표준 KSWIN 변종이다. 순차적으로 들어오는 numeric signal에서 최근 분포가 이전 window와 달라졌는지 빠르게 screening한다. 출력은 KS statistic, p-value 또는 score, drift alarm state로 해석한다.

사용 상황:
- 단변량 numeric stream에서 최근 window의 분포 변화 후보를 감시할 때
- 고정 reference 기간보다 streaming window 내부의 과거/최근 비교가 필요한 경우
- label 없이 feature value 또는 score signal의 online drift 후보를 찾고 싶을 때

해석 방법:
- KS statistic이 커지고 p-value가 작아지면 window 내부의 과거 부분과 최근 부분이 다른 분포일 가능성이 커진다.
- alarm은 최근 stream 분포가 sliding window 기준에서 달라졌다는 후보 신호다.
- drift 시점은 detector가 alarm을 낸 window 끝 지점으로 보고, 실제 변화 시작점은 별도 분석이 필요하다.
- 보고서에는 window size, reference/current split 방식, alpha 기준을 함께 적는다.

주의점:
- window size와 alpha 설정에 따라 민감도와 false alarm이 크게 달라진다.
- stream의 자기상관, 계절성, batch 효과가 있으면 KS p-value 해석이 약해질 수 있다.
- label 없는 feature drift 신호이므로 성능 저하나 원인 확정으로 표현하지 않는다.

보고서 문장 예시:

```text
KSWIN_STANDARD로 numeric stream을 감시한 결과,
sliding window 내부의 과거 구간과 최근 구간 사이 KS 차이가 기준을 초과했다.
이는 최근 입력 분포가 직전 window 기준과 달라졌을 가능성을 나타내는 drift 후보 신호다.
다만 window size와 alpha 설정에 따라 alarm 민감도가 달라지므로, 원시 추세와 함께 확인해야 한다.
```

---

## 변종: KSWIN_WITH_SUBSAMPLING

`KSWIN_WITH_SUBSAMPLING`은 KSWIN의 sliding window 비교에서 reference 또는 current 부분을 subsampling해 계산 비용과 memory 부담을 줄이는 변종이다. 대량 stream이나 고빈도 signal에서 빠른 drift screening을 유지하면서 KS 비교를 수행한다. 출력은 sampled KS statistic, p-value 또는 score, alarm state로 해석한다.

사용 상황:
- stream 속도가 높아 전체 window를 매번 비교하기 어려운 경우
- edge 또는 online 환경에서 memory와 latency 제약이 있는 경우
- 빠른 후보 탐지를 먼저 하고 alarm 발생 시 정밀 재검증을 수행하려는 운영에서

해석 방법:
- sampled KS statistic이 기준을 넘으면 subsample 기준의 최근 분포 변화 후보로 본다.
- 같은 stream이라도 sampling seed와 sampling rate에 따라 statistic이 달라질 수 있다.
- alarm은 빠른 screening 신호이며, 중요한 alarm은 전체 window 또는 더 큰 sample로 재확인한다.
- 보고서에는 sampling rate, seed 정책, 재검증 여부를 명시한다.

주의점:
- subsampling은 작은 drift를 놓치거나 일시 spike를 과대평가할 수 있다.
- sampling 정책이 바뀌면 이전 score와 직접 비교하기 어렵다.
- rare event가 중요한 stream에서는 subsampling이 rare pattern을 누락할 수 있다.

보고서 문장 예시:

```text
KSWIN_WITH_SUBSAMPLING으로 고빈도 numeric stream을 감시한 결과,
subsampled window 비교에서 KS 기반 drift 후보 alarm이 발생했다.
이는 최근 stream 분포가 과거 window와 달라졌을 가능성을 빠르게 screening한 결과다.
다만 subsampling에 따른 오차가 있으므로, 중요한 alarm은 전체 window 또는 더 큰 sample로 재검증해야 한다.
```

---

## 변종: KSWIN_NUMERIC_STREAM

`KSWIN_NUMERIC_STREAM`은 연속형 또는 준연속형 numeric stream에 KSWIN을 적용하는 변종이다. feature value, model score, latency, loss proxy처럼 시간순으로 들어오는 숫자 신호의 분포 변화 후보를 감시한다. 출력은 window별 KS statistic, p-value 또는 score, alarm state로 해석한다.

사용 상황:
- 센서값, 거래 금액, 모델 confidence, response time 같은 numeric signal을 online monitoring할 때
- 평균 변화뿐 아니라 분포 모양이나 tail 변화까지 감시하고 싶을 때
- current window가 직전 stream 상태와 달라졌는지 label 없이 확인해야 할 때

해석 방법:
- alarm은 최근 numeric stream의 경험분포가 이전 window 구간과 달라졌다는 후보 신호다.
- KS statistic이 커진 구간의 raw trend와 quantile 변화를 함께 보면 변화 유형을 설명할 수 있다.
- score 추세가 지속 상승하면 단발성 spike보다 구조적 분포 변화 가능성이 크다.
- 보고서에는 감시 대상 numeric signal의 정의와 window 설정을 함께 적는다.

주의점:
- numeric stream에 강한 계절성이나 주기성이 있으면 window 비교가 반복 alarm을 낼 수 있다.
- ties가 많거나 discretized metric이면 KS p-value 해석이 약해질 수 있다.
- 분포 변화가 business impact로 이어지는지는 metric 의미에 따라 별도 평가한다.

보고서 문장 예시:

```text
KSWIN_NUMERIC_STREAM으로 모델 score stream을 감시한 결과,
최근 window의 경험분포가 이전 window와 달라졌다는 KS 기반 alarm이 발생했다.
이는 score 분포의 위치 또는 형태가 최근 구간에서 변했을 가능성을 나타낸다.
다만 계절성, batch 처리 효과, ties 여부를 확인한 뒤 drift 후보로 보고해야 한다.
```

---

## SelectionRule 카탈로그

```text
selectionRule KSWIN_DEFAULT_USE
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

> KSWIN 카탈로그는 "이 방법이 무엇인가"가 아니라, "어떤 상황에서 어떤 변종을 선택하고 어떤 주의사항과 함께 설명해야 하는가"를 구조화한다.
