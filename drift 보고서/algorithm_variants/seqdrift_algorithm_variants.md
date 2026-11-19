# SeqDrift 알고리즘 변종 목록

## 1. 목적

이 문서는 `SeqDrift`를 하나의 고정된 detector로 보지 않고, drift monitoring에서 상황에 따라 선택해야 하는 **알고리즘 변종들의 family**로 정리한다.

핵심 목적은 다음이다.

```text
상황 조건 -> 적절한 SeqDrift 계열 변종 -> 출력 metric -> 주의사항 -> LLM 보고서 설명
```

---

## 2. SeqDrift의 위치

```text
methodFamily SEQDRIFT
       ├─ algorithmVariant SEQDRIFT1
       └─ algorithmVariant SEQDRIFT2
```

`SeqDrift`는 sequential stream drift detector 계열에 속한다. 순차 bound와 sampling 전략으로 스트림 분포 또는 평균 변화 여부를 감지한다.

---

## 3. 공통 개념

```text
methodFamily SEQDRIFT
  purpose ->
    순차 bound와 sampling 전략으로 스트림 분포 또는 평균 변화 여부를 감지한다.

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

## 변종: SEQDRIFT1

Sequential bound를 사용해 streaming value나 error stream의 변화가 통계적 경계를 넘는지 확인하는 SeqDrift1 변종이다. 초기 SeqDrift 계열의 기본 감지 방식이다.

- 사용 상황: 값이 순차적으로 들어오는 stream에서 평균 또는 오류율 변화 후보를 빠르게 확인해야 할 때 적합하다.
- 해석 방법: sequential bound를 넘는 시점은 current stream이 이전 기준과 달라졌을 가능성이 커진 drift 알람으로 본다.
- 주의점: 사용한 SeqDrift 버전, bound 설정, 입력 stream 정의가 결과 해석에 직접 영향을 준다.
- 보고서 문장 예시: "SeqDrift1 sequential bound가 초과되어 streaming 지표의 변화 후보가 알람으로 기록되었다."

---

## 변종: SEQDRIFT2

개선된 sampling 또는 reservoir 전략을 사용해 stream 변화 감지를 수행하는 SeqDrift2 변종이다. 큰 stream에서 sudden drift와 gradual drift 후보를 모두 다루기 쉽다.

- 사용 상황: 전체 stream을 모두 보관하기 어렵고 sampling 정책으로 reference/current 비교를 유지해야 할 때 적합하다.
- 해석 방법: drift alarm은 sampling된 기준과 최근 stream 사이 차이가 설정된 경계를 넘었다는 신호로 본다.
- 주의점: sampling 정책의 재현성이 없으면 동일 데이터에서도 결과가 달라질 수 있으므로 seed, reservoir 크기, 갱신 정책을 남긴다.
- 보고서 문장 예시: "SeqDrift2는 reservoir sampling 기준에서 최근 stream이 기준과 달라진 후보를 감지했다."

---

## SelectionRule 카탈로그

```text
selectionRule SEQDRIFT_DEFAULT_USE
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

> SeqDrift 카탈로그는 "이 방법이 무엇인가"가 아니라, "어떤 상황에서 어떤 변종을 선택하고 어떤 주의사항과 함께 설명해야 하는가"를 구조화한다.
