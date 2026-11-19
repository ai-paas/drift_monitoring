# Generic / Fallback 알고리즘 변종 목록

## 1. 목적

이 문서는 전용 chart family나 detector family가 아직 확정되지 않은 drift monitoring 결과를 임시로 보고할 때 사용하는 fallback 변종을 정의한다.

핵심 목적은 다음이다.

```text
불완전한 method metadata -> generic fallback 변종 -> 최소 보고 metric -> threshold/alarm 근거 -> 후속 분류 필요성
```

---

## 2. Generic / Fallback의 위치

```text
methodFamily Generic / Fallback
       └─ algorithmVariant GENERIC_METRIC_THRESHOLD_DRIFT
```

`Generic / Fallback`은 최종 detector family가 아니다. 운영 로그, 실험 단계 metric, 또는 외부 시스템에서 넘어온 drift score처럼 아직 KS, PSI, MMD, stream detector 등으로 분류되지 않은 신호를 report에 누락하지 않기 위한 임시 표현이다.

---

## 3. 공통 개념

```text
methodFamily Generic / Fallback
  purpose ->
    전용 detector family가 정해지기 전의 drift score 또는 alarm signal을 최소 공통 형식으로 설명한다.

  commonOutputs ->
    TEST_STATISTIC_OR_DISTANCE
    THRESHOLD
    ALARM_STATE_OPTIONAL
    REFERENCE_CURRENT_SUMMARY_OPTIONAL

  commonCautions ->
    generic fallback은 원인 분석이나 통계 검정 family를 확정하지 않는다.
    threshold 산정 방식, reference/current window, metric 정의를 반드시 함께 보고한다.
    후속 작업으로 전용 detector family와 chart family를 확정해야 한다.
```

---

## 변종: GENERIC_METRIC_THRESHOLD_DRIFT

`GENERIC_METRIC_THRESHOLD_DRIFT`는 전용 detector family가 아직 확정되지 않았지만 drift score, distance, alarm metric은 존재할 때 사용하는 임시 보고용 변종이다. 이 변종은 KS, PSI, MMD 같은 구체적 검정으로 해석하지 않고, metric trend와 threshold 초과 여부를 최소 공통 형식으로 정리한다. 핵심은 신호를 누락하지 않되, 원인이나 통계적 의미를 과도하게 확정하지 않는 것이다.

사용 상황:
- 외부 monitoring system에서 metric name, 값, threshold, alarm만 전달되는 경우
- 신규 detector를 실험 중이라 아직 method family와 전용 chart family가 정해지지 않은 경우
- 보고서에 reference/current 요약과 threshold 초과 여부를 빠르게 공유해야 하는 경우

해석 방법:
- metric value 또는 trend는 이름이 정의한 drift score의 변화 방향과 크기를 나타낸다.
- threshold는 통계 검정의 보편 기준이 아니라 경험적 기준, 운영 정책, 또는 calibration 결과로 구분해 읽는다.
- alarm state는 해당 기준을 초과했다는 운영 신호이며, 분포 검정의 p-value나 effect size로 해석하지 않는다.
- reference/current summary가 있으면 metric 상승이 어떤 입력 구간, feature, segment 변화와 함께 나타났는지 보조 설명한다.

주의점:
- fallback 결과를 특정 통계 검정이나 detector family의 결과처럼 말하면 안 된다.
- metric 정의, window 기준, threshold 산정 방식이 불명확하면 보고서 신뢰도가 낮아진다.
- 같은 metric이 반복적으로 사용되면 전용 method family, chart id, 해석 문서로 승격해야 한다.

보고서 문장 예시:

```text
전용 detector family가 아직 확정되지 않아 GENERIC_METRIC_THRESHOLD_DRIFT 형식으로 metric을 보고했다.
관측 metric은 current window에서 기준 threshold를 초과해 drift 후보 alarm으로 표시됐다.
이는 운영 기준상 추가 확인이 필요한 변화 신호지만, 특정 통계 검정의 유의성으로 해석하지 않는다.
후속 분석에서는 metric 정의, threshold 산정 방식, reference/current 데이터 차이를 먼저 확정해야 한다.
```

---

## 4. 선택 및 보고 가이드

```text
selectionRule GENERIC_FALLBACK_SELECTION
  if ->
    drift_metric_available
    and dedicated_method_family_unknown
    and report_should_not_drop_signal

  recommend ->
    GENERIC_METRIC_THRESHOLD_DRIFT

  because ->
    전용 detector family가 확정되기 전에도 metric trend와 threshold/alarm 근거를 최소 형식으로 설명할 수 있다.

  followUp ->
    운영 반복 사용 여부를 확인하고,
    반복 사용되는 metric은 전용 method family, chart id, interpretation guide로 분리한다.
```
