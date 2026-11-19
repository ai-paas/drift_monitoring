# HDDM-W 알고리즘 변종 목록

## 1. 목적

이 문서는 `HDDM-W`를 하나의 고정된 detector로 보지 않고, drift monitoring에서 상황에 따라 선택해야 하는 **알고리즘 변종들의 family**로 정리한다.

핵심 목적은 다음이다.

```text
상황 조건 -> 적절한 HDDM-W 계열 변종 -> 출력 metric -> 주의사항 -> LLM 보고서 설명
```

---

## 2. HDDM-W의 위치

```text
methodFamily HDDM_W
       ├─ algorithmVariant HDDM_W_WEIGHTED_AVERAGE
       ├─ algorithmVariant HDDM_W_WARNING_DRIFT
       └─ algorithmVariant HDDM_W_RECENT_ERROR_WEIGHTING
```

`HDDM-W`는 drift monitoring method 계열에 속한다. HDDM-W 계열을 drift monitoring 문맥에서 입력 데이터와 운영 목적에 따라 선택 가능한 변종으로 정리한다.

---

## 3. 공통 개념

```text
methodFamily HDDM_W
  purpose ->
    HDDM-W 계열을 drift monitoring 문맥에서 입력 데이터와 운영 목적에 따라 선택 가능한 변종으로 정리한다.

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

## 변종: HDDM_W_WEIGHTED_AVERAGE

`HDDM_W_WEIGHTED_AVERAGE`는 최근 관측치에 더 큰 가중치를 두는 weighted moving average 기반 HDDM-W 변종이다. HDDM-A보다 최근 변화에 민감하게 반응하도록 설계해, streaming error나 binary quality signal의 빠른 변화를 감시할 때 사용한다. 출력은 weighted mean, bound 또는 threshold, warning/drift alarm state로 해석한다.

사용 상황:
- 최근 error rate 변화에 빠르게 반응해야 하는 온라인 모델 monitoring에서
- 오래된 관측치보다 최근 stream의 상태를 더 중요하게 보고 싶을 때
- 급격한 변화뿐 아니라 최근 구간에서 누적되는 변화 후보를 민감하게 잡고 싶을 때

해석 방법:
- weighted mean이 기준 상태에서 threshold 이상 벗어나면 최근 stream 중심의 drift 후보로 본다.
- 동일한 raw signal이라도 가중치 설정에 따라 alarm 시점이 달라질 수 있다.
- alarm은 최근 관측치가 평균 계산에 크게 반영된 결과이므로, 최근 batch의 품질과 표본 수를 함께 본다.
- 보고서에는 가중 방식과 최근 변화 방향을 함께 설명한다.

주의점:
- 가중치가 너무 최근에 치우치면 일시 spike에도 민감하게 반응할 수 있다.
- 과거 안정 구간을 빨리 잊기 때문에 느린 장기 변화 해석에는 별도 지표가 필요할 수 있다.
- threshold와 weighting factor는 운영 false alarm 허용 수준에 맞춰 조정해야 한다.

보고서 문장 예시:

```text
HDDM_W_WEIGHTED_AVERAGE로 streaming error signal을 감시한 결과,
최근 관측치에 가중된 평균이 기준 threshold를 넘어 drift 후보 alarm이 발생했다.
이는 current stream의 최근 error 수준이 이전 상태와 달라졌을 가능성을 나타낸다.
다만 weighting factor가 alarm 민감도를 크게 좌우하므로, 최근 batch 품질과 threshold calibration 근거를 함께 확인해야 한다.
```

---

## 변종: HDDM_W_WARNING_DRIFT

`HDDM_W_WARNING_DRIFT`는 HDDM-W의 최근 가중 평균 변화에 대해 warning level과 drift level을 분리해 표시하는 변종이다. 최근 관측치 중심의 빠른 반응성과 단계적 alarm 체계를 함께 제공한다. 출력은 weighted warning state, weighted drift state, 감지 시점, 변화 방향으로 해석한다.

사용 상황:
- 최근 stream 변화에 민감하게 대응하되, warning과 drift를 분리해 운영 대응을 단계화해야 할 때
- drift alarm 전 샘플 보존, 로그 확대, 원인 분석 준비 같은 사전 조치를 하고 싶을 때
- 빠른 변화가 많은 환경에서 단일 alarm보다 severity level이 필요한 경우

해석 방법:
- warning은 최근 가중 평균이 주의 수준에 들어왔다는 조기 신호다.
- drift alarm은 더 강한 threshold를 통과한 상태이며, 후속 점검 우선순위가 높다.
- warning에서 drift까지의 시간과 raw metric 추세를 함께 보면 변화 속도를 설명할 수 있다.
- 보고서에는 weighted 방식의 warning/drift 기준을 구분해 적는다.

주의점:
- 최근 가중 방식 때문에 warning이 잦을 수 있으므로 운영 대응 정책이 필요하다.
- warning은 확정 신호가 아니라 관찰 강화 신호로 표현해야 한다.
- drift threshold를 너무 낮게 두면 일시적인 recent spike가 과대 해석될 수 있다.

보고서 문장 예시:

```text
HDDM_W_WARNING_DRIFT 결과, 최근 가중 평균이 warning 기준을 먼저 넘고 이후 drift 기준도 초과했다.
이는 recent stream 중심으로 error signal 변화가 커지고 있음을 나타내는 단계적 drift 후보 신호다.
warning은 관찰 강화, drift는 후속 점검 우선순위 상승 신호로 구분해 해석해야 한다.
다만 최근 가중치가 일시 spike를 크게 반영할 수 있으므로 raw metric 추세와 함께 확인해야 한다.
```

---

## 변종: HDDM_W_RECENT_ERROR_WEIGHTING

`HDDM_W_RECENT_ERROR_WEIGHTING`은 error indicator의 최근 관측치에 더 큰 비중을 두어 모델 오류 패턴 변화에 빠르게 반응하는 HDDM-W 변종이다. label이 순차적으로 들어오고 최근 오류 증가를 놓치지 않는 것이 중요한 supervised monitoring에 적합하다. 출력은 recent-weighted error rate, threshold 초과 여부, alarm state로 해석한다.

사용 상황:
- 온라인 예측 서비스에서 최근 label이 도착하는 즉시 error pattern 변화를 감시할 때
- 전체 누적 오류율은 안정적이지만 최근 window의 오류 증가가 중요한 경우
- retraining 후보 선별이나 rollback 검토를 위한 조기 error drift signal이 필요할 때

해석 방법:
- recent-weighted error rate가 기준보다 높아지면 최근 오류 패턴 악화 후보로 본다.
- weighted rate가 낮아지는 방향이면 최근 오류가 줄어든 변화로 해석할 수 있지만, 운영 목적에 따라 의미가 다르다.
- alarm은 최근 label/error 흐름의 변화 신호이며, feature distribution drift와는 구분한다.
- 보고서에는 label 도착 지연, 최근 window 크기, error 정의를 함께 명시한다.

주의점:
- label이 늦게 들어오면 최근 오류 가중치가 실제 운영 시점보다 뒤늦게 반영된다.
- error 정의나 평가 대상 population이 바뀌면 detector가 성능 변화가 아닌 평가 기준 변화를 감지할 수 있다.
- 소수의 최근 오류가 과도하게 반영되지 않도록 최소 표본 수 조건을 둬야 한다.

보고서 문장 예시:

```text
HDDM_W_RECENT_ERROR_WEIGHTING으로 최근 error signal을 감시한 결과,
recent-weighted error rate가 기준 threshold를 초과해 drift 후보 alarm이 발생했다.
이는 최근 label이 확인된 샘플에서 오류 패턴이 이전 상태와 달라졌을 가능성을 나타낸다.
다만 label 지연, 최근 window 표본 수, error 정의 변경 여부를 확인한 뒤 성능 저하 여부를 판단해야 한다.
```

---

## SelectionRule 카탈로그

```text
selectionRule HDDM_W_DEFAULT_USE
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

> HDDM-W 카탈로그는 "이 방법이 무엇인가"가 아니라, "어떤 상황에서 어떤 변종을 선택하고 어떤 주의사항과 함께 설명해야 하는가"를 구조화한다.
