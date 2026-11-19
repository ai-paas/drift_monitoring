# STEPD 알고리즘 변종 목록

## 1. 목적

이 문서는 `STEPD`를 하나의 고정된 detector로 보지 않고, drift monitoring에서 상황에 따라 선택해야 하는 **알고리즘 변종들의 family**로 정리한다.

핵심 목적은 다음이다.

```text
상황 조건 -> 적절한 STEPD 계열 변종 -> 출력 metric -> 주의사항 -> LLM 보고서 설명
```

---

## 2. STEPD의 위치

```text
methodFamily STEPD
       ├─ algorithmVariant STEPD_ACCURACY_WINDOW
       ├─ algorithmVariant STEPD_WARNING_DRIFT
       └─ algorithmVariant STEPD_SUPERVISED_STREAM
```

`STEPD`는 drift monitoring method 계열에 속한다. STEPD 계열을 drift monitoring 문맥에서 입력 데이터와 운영 목적에 따라 선택 가능한 변종으로 정리한다.

---

## 3. 공통 개념

```text
methodFamily STEPD
  purpose ->
    STEPD 계열을 drift monitoring 문맥에서 입력 데이터와 운영 목적에 따라 선택 가능한 변종으로 정리한다.

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

## 변종: STEPD_ACCURACY_WINDOW

최근 window와 과거 window의 accuracy 차이를 검정해 supervised performance drift 후보를 감지하는 STEPD 기본 변종이다. 라벨이 지연 없이 들어오는 stream에서 성능 변화를 직접 본다.

- 사용 상황: online classification에서 정확도 저하가 운영상 중요한 경보 조건일 때 적합하다.
- 해석 방법: 최근 window accuracy가 기준 window보다 유의하게 낮아지면 모델 성능 변화 후보로 본다.
- 주의점: 라벨 지연, class imbalance, window 크기 변화가 accuracy 비교를 왜곡할 수 있다.
- 보고서 문장 예시: "STEPD accuracy window 검정에서 최근 window 정확도가 기준보다 낮아져 supervised drift 후보가 감지되었다."

---

## 변종: STEPD_WARNING_DRIFT

Warning 단계와 drift 단계를 나누어 accuracy 변화의 심각도를 구분하는 STEPD 변종이다. 단일 알람보다 사전 경고와 확정 알람을 분리해 운영한다.

- 사용 상황: 재학습이나 조사를 바로 실행하기 전에 warning 상태로 추세를 관찰해야 할 때 적합하다.
- 해석 방법: warning은 성능 저하 가능성, drift는 더 강한 성능 변화 신호로 구분해 해석한다.
- 주의점: warning threshold와 drift threshold를 분리해 calibration하지 않으면 과도한 알람이 발생할 수 있다.
- 보고서 문장 예시: "STEPD가 warning 상태에서 drift 상태로 전환되어 accuracy 저하 신호의 강도가 높아졌다."

---

## 변종: STEPD_SUPERVISED_STREAM

예측 결과와 실제 라벨이 순차적으로 들어오는 supervised stream에 STEPD를 적용하는 변종이다. 오류 여부 stream을 구성해 성능 drift를 추적한다.

- 사용 상황: 라벨 수집이 가능하고, stream 순서에 따라 모델 성능을 계속 감시해야 하는 운영 환경에 적합하다.
- 해석 방법: 오류율 또는 accuracy 기반 검정 통계가 threshold를 넘으면 supervised performance drift 후보로 본다.
- 주의점: 라벨이 없는 기간에는 적용할 수 없고, 라벨 지연이 있으면 알람 시점과 실제 drift 시점이 어긋날 수 있다.
- 보고서 문장 예시: "Supervised stream STEPD는 라벨 기반 오류 흐름에서 current 구간 성능 변화 후보를 감지했다."

---

## SelectionRule 카탈로그

```text
selectionRule STEPD_DEFAULT_USE
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

> STEPD 카탈로그는 "이 방법이 무엇인가"가 아니라, "어떤 상황에서 어떤 변종을 선택하고 어떤 주의사항과 함께 설명해야 하는가"를 구조화한다.
