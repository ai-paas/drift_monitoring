# EDDM 알고리즘 변종 목록

## 1. 목적

이 문서는 `EDDM`를 하나의 고정된 detector로 보지 않고, drift monitoring에서 상황에 따라 선택해야 하는 **알고리즘 변종들의 family**로 정리한다.

핵심 목적은 다음이다.

```text
상황 조건 -> 적절한 EDDM 계열 변종 -> 출력 metric -> 주의사항 -> LLM 보고서 설명
```

---

## 2. EDDM의 위치

```text
methodFamily EDDM
       ├─ algorithmVariant EDDM_DISTANCE_BETWEEN_ERRORS
       ├─ algorithmVariant EDDM_WARNING_DRIFT
       └─ algorithmVariant EDDM_GRADUAL_DRIFT
```

`EDDM`는 drift monitoring method 계열에 속한다. EDDM 계열을 drift monitoring 문맥에서 입력 데이터와 운영 목적에 따라 선택 가능한 변종으로 정리한다.

---

## 3. 공통 개념

```text
methodFamily EDDM
  purpose ->
    EDDM 계열을 drift monitoring 문맥에서 입력 데이터와 운영 목적에 따라 선택 가능한 변종으로 정리한다.

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

## 변종: EDDM_DISTANCE_BETWEEN_ERRORS

`EDDM_DISTANCE_BETWEEN_ERRORS`는 모델 예측 오류가 발생하는 간격을 추적해, 오류 사이 거리가 짧아지는지 보는 변종이다. 정상 상태에서는 오류가 드문드문 발생하다가 성능이 흔들리면 오류 간격이 줄어든다는 가정에 기반한다. 출력은 오류 간 거리의 평균과 표준편차 기반 score, warning 또는 drift 상태로 해석한다.

사용 상황:
- 정답 label이 들어와 예측별 error stream을 만들 수 있을 때
- 단순 오류율보다 오류 발생 간격의 변화로 gradual performance drift를 보고 싶을 때
- 오류가 너무 드물지 않아 거리 통계가 안정적으로 계산될 만큼 사례가 쌓일 때

해석 방법:
- 오류 사이 거리가 짧아지면 모델이 더 자주 틀리는 방향의 성능 변화 후보로 본다.
- EDDM score가 과거 최대 기준보다 낮아지면 warning 또는 drift 상태로 전환될 수 있다.
- warning은 변화 가능성이 커진 상태이고, drift alarm은 재학습이나 원인 점검을 검토할 수준의 신호다.
- error stream 기반 결과이므로 입력 분포 변화보다 실제 예측 실패 패턴 변화를 더 직접적으로 반영한다.

주의점:
- label 지연이 있으면 alarm 시점이 실제 변화 시점보다 늦게 보일 수 있다.
- class imbalance가 크면 특정 class 오류가 전체 distance 통계를 지배할 수 있다.
- 오류 수가 적은 초기 구간이나 매우 높은 정확도 구간에서는 distance 추정이 불안정하다.

보고서 문장 예시:

```text
예측 오류 스트림을 EDDM_DISTANCE_BETWEEN_ERRORS로 모니터링한 결과,
오류 사이 거리가 기준 상태보다 짧아지는 방향의 변화가 관측됐다.
이는 모델 오류가 더 자주 발생하는 성능 변화 후보 신호로 해석할 수 있다.
다만 label 지연과 class imbalance가 error stream에 영향을 줄 수 있으므로 class별 오류 패턴을 함께 확인해야 한다.
```

---

## 변종: EDDM_WARNING_DRIFT

`EDDM_WARNING_DRIFT`는 drift alarm 전에 warning 상태를 따로 보고해 운영자가 변화 후보를 조기에 관찰하도록 하는 변종이다. 오류 간격 score가 약해지기 시작하면 warning으로 표시하고, 더 강한 기준을 넘으면 drift alarm으로 구분한다. 출력은 warning 상태, drift 상태, 각 상태에 진입한 시점으로 해석한다.

사용 상황:
- 즉시 조치보다 사전 관찰과 데이터 확보가 중요한 운영 환경일 때
- drift alarm 전에 후보 구간을 따로 저장하거나 원인 분석을 시작하고 싶을 때
- label 기반 error stream이 안정적으로 들어오고 warning threshold 정책이 정해져 있을 때

해석 방법:
- warning은 drift 확정이 아니라 오류 간격 변화가 감지되기 시작했다는 예비 신호다.
- warning 이후 drift alarm으로 이어지면 변화 후보의 강도와 지속성이 커졌다고 본다.
- warning이 사라지면 일시적 변동일 수 있으므로 해당 구간의 원시 오류율과 class 분포를 함께 본다.
- 보고서에는 warning 시점과 drift alarm 시점을 분리해 적어야 운영 대응 이력이 명확해진다.

주의점:
- warning threshold를 너무 민감하게 두면 불필요한 관찰 구간이 많아진다.
- label 지연이 큰 시스템에서는 warning이 이미 지나간 운영 상황을 뒤늦게 보여줄 수 있다.
- warning 상태만으로 재학습을 결정하기보다 추가 데이터, 오류 유형, 비즈니스 영향도를 확인한다.

보고서 문장 예시:

```text
예측 오류 스트림을 EDDM_WARNING_DRIFT로 추적한 결과,
drift alarm 이전에 warning 상태로 전환되는 구간이 확인됐다.
이는 오류 발생 간격이 정상 기준보다 짧아지기 시작한 성능 변화 후보 신호로 볼 수 있다.
다만 warning은 확정 alarm이 아니므로, 해당 구간의 오류 유형과 label 수집 지연을 함께 검토해야 한다.
```

---

## 변종: EDDM_GRADUAL_DRIFT

`EDDM_GRADUAL_DRIFT`는 갑작스러운 오류율 급등보다 오류 간격이 서서히 짧아지는 패턴을 잡는 데 초점을 둔 변종이다. 모델 성능이 한 번에 무너지는 것이 아니라 데이터 조건 변화나 사용자 행동 변화로 천천히 악화될 때 유용하다. 출력은 error distance 기반 score의 장기 하락, warning/drift 상태, 변화가 누적된 구간으로 해석한다.

사용 상황:
- 오류율이 서서히 높아지는지 장기간 감시해야 할 때
- 계절성, 정책 변화, 데이터 수집 변화처럼 점진적 운영 변화가 의심될 때
- label이 일정한 지연 안에 들어와 시간 순서 error stream을 유지할 수 있을 때

해석 방법:
- score가 천천히 낮아지고 warning 상태가 길어지면 gradual drift 후보로 본다.
- drift alarm은 누적된 오류 간격 변화가 기준보다 충분히 커졌다는 신호다.
- 단기 spike와 구분하려면 원시 오류율, moving average, warning 지속 시간을 함께 본다.
- 변화 구간 전후의 class 구성과 입력 segment를 비교하면 어떤 영역에서 성능 변화가 커졌는지 확인할 수 있다.

주의점:
- 빠른 abrupt drift 탐지에는 반응이 늦을 수 있다.
- label 수집 방식이 바뀌면 실제 성능 변화가 없어도 error distance가 변할 수 있다.
- 오류가 특정 소수 class에 집중되면 전체 gradual drift처럼 보일 수 있으므로 segment별 확인이 필요하다.

보고서 문장 예시:

```text
예측 오류 스트림을 EDDM_GRADUAL_DRIFT로 모니터링한 결과,
오류 간격 score가 여러 window에 걸쳐 낮아지는 흐름을 보였다.
이는 오류 발생 빈도가 점진적으로 증가하는 성능 변화 후보 신호로 해석할 수 있다.
다만 abrupt drift에는 민감도가 다를 수 있고, label 지연과 class별 오류 집중 여부를 함께 확인해야 한다.
```

---

## SelectionRule 카탈로그

```text
selectionRule EDDM_DEFAULT_USE
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

> EDDM 카탈로그는 "이 방법이 무엇인가"가 아니라, "어떤 상황에서 어떤 변종을 선택하고 어떤 주의사항과 함께 설명해야 하는가"를 구조화한다.
