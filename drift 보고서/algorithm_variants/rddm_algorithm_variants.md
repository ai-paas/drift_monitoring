# RDDM 알고리즘 변종 목록

## 1. 목적

이 문서는 `RDDM`를 하나의 고정된 detector로 보지 않고, drift monitoring에서 상황에 따라 선택해야 하는 **알고리즘 변종들의 family**로 정리한다.

핵심 목적은 다음이다.

```text
상황 조건 -> 적절한 RDDM 계열 변종 -> 출력 metric -> 주의사항 -> LLM 보고서 설명
```

---

## 2. RDDM의 위치

```text
methodFamily RDDM
       ├─ algorithmVariant RDDM_STANDARD
       └─ algorithmVariant RDDM_REACTIVE_RESET
```

`RDDM`는 DDM 개선 계열 계열에 속한다. DDM의 오래된 인스턴스 누적과 warning 구간 처리 문제를 완화한다.

---

## 3. 공통 개념

```text
methodFamily RDDM
  purpose ->
    DDM의 오래된 인스턴스 누적과 warning 구간 처리 문제를 완화한다.

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

## 변종: RDDM_STANDARD

DDM의 오래된 정상 기준 누적 문제를 완화해 long-running stream의 오류율 변화를 감지하는 RDDM 기본 변종이다. Warning 구간과 retained window를 관리해 변화에 더 반응하도록 설계된다.

- 사용 상황: 라벨이 순차적으로 들어오고, 오랫동안 운영된 모델의 error stream에서 recurring drift나 새로운 drift를 감지해야 할 때 적합하다.
- 해석 방법: warning state는 오류율 악화 가능성, drift state는 기준보다 오류율 변화가 충분히 커진 상태로 본다.
- 주의점: 라벨 없는 stream에는 직접 적용하기 어렵고, 오래된 instance 삭제/유지 정책이 민감도와 지연을 바꾼다.
- 보고서 문장 예시: "RDDM이 warning 이후 drift 상태로 전환되어 장기 운영 stream에서 오류율 변화 후보가 감지되었다."

---

## 변종: RDDM_REACTIVE_RESET

Drift 감지 후 detector 기준을 재설정해 새로운 오류율 수준에 빠르게 적응하는 RDDM 변종이다. Reset 이벤트 자체를 운영 로그와 재학습 후보로 함께 다룬다.

- 사용 상황: drift 알람 이후 current regime에 맞춰 모니터링 기준을 다시 잡아야 하는 온라인 운영 환경에 적합하다.
- 해석 방법: reset event는 기준 변경이 발생했음을 의미하고, post-reset error rate는 새 기준에서 안정화 여부를 확인하는 지표로 본다.
- 주의점: reset은 과거 기준과의 직접 비교를 끊으므로 audit을 위해 reset 시점, 사유, 이전 상태를 반드시 기록한다.
- 보고서 문장 예시: "RDDM reactive reset이 발생해 drift 이후 새 오류율 기준으로 모니터링 상태가 재설정되었다."

---

## SelectionRule 카탈로그

```text
selectionRule RDDM_DEFAULT_USE
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

> RDDM 카탈로그는 "이 방법이 무엇인가"가 아니라, "어떤 상황에서 어떤 변종을 선택하고 어떤 주의사항과 함께 설명해야 하는가"를 구조화한다.
