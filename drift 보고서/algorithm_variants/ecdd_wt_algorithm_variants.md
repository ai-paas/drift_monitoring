# ECDD-WT 알고리즘 변종 목록

## 1. 목적

이 문서는 `ECDD-WT`를 하나의 고정된 detector로 보지 않고, drift monitoring에서 상황에 따라 선택해야 하는 **알고리즘 변종들의 family**로 정리한다.

핵심 목적은 다음이다.

```text
상황 조건 -> 적절한 ECDD-WT 계열 변종 -> 출력 metric -> 주의사항 -> LLM 보고서 설명
```

---

## 2. ECDD-WT의 위치

```text
methodFamily ECDD_WT
       ├─ algorithmVariant ECDD_WT_STANDARD
       ├─ algorithmVariant ECDD_WT_WARNING_DRIFT
       └─ algorithmVariant ECDD_WT_ERROR_STREAM
```

`ECDD-WT`는 drift monitoring method 계열에 속한다. ECDD-WT 계열을 drift monitoring 문맥에서 입력 데이터와 운영 목적에 따라 선택 가능한 변종으로 정리한다.

---

## 3. 공통 개념

```text
methodFamily ECDD_WT
  purpose ->
    ECDD-WT 계열을 drift monitoring 문맥에서 입력 데이터와 운영 목적에 따라 선택 가능한 변종으로 정리한다.

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

## 변종: ECDD_WT_STANDARD

`ECDD_WT_STANDARD`는 분류 error stream에 EWMA 방식의 가중 평균을 적용해 오류율 증가를 감시하는 기본 ECDD-WT 변종이다. 최근 오류에 더 큰 가중치를 두기 때문에 갑작스러운 오류율 상승뿐 아니라 최근 구간의 성능 악화가 빠르게 반영된다. DDM처럼 label 기반 supervised detector이며, warning과 drift를 운영 threshold로 구분해 보고할 수 있다.

이 변종은 다음 상황에 적합하다.

- 예측 결과와 정답 label로 0/1 error stream을 만들 수 있다.
- 최근 오류 증가에 더 민감하게 반응하는 supervised drift 감시가 필요하다.
- EWMA 가중치, warning threshold, drift threshold를 calibration할 수 있다.
- label 지연과 class imbalance를 보고서에서 함께 설명할 수 있다.

해석할 때는 EWMA error statistic, warning state, drift state를 함께 본다. EWMA statistic이 warning threshold를 넘으면 조사 대상 성능 변화 신호로, drift threshold를 넘으면 오류율 기반 drift 후보 alarm으로 해석한다. 값이 커졌다는 사실은 최근 오류가 기준 수준보다 높게 누적 반영됐다는 뜻이며, 원인이나 업무 영향은 별도 분석으로 확인해야 한다.

주의할 점은 ECDD-WT가 label 품질과 error stream 정의에 직접 의존한다는 것이다. Label 지연이 길면 alarm이 늦게 나타나고, label 정책 변경은 실제 모델 변화 없이도 오류율을 바꿀 수 있다. EWMA 가중치를 크게 잡으면 최근 noise에 민감해지고, 작게 잡으면 변화 감지가 늦어질 수 있다. Threshold는 운영 정책 또는 calibration 결과로 보고하고 보편적 절대 기준처럼 쓰지 않는다.

보고서 문장 예시는 다음과 같다.

```text
binary error stream을 ECDD_WT_STANDARD로 모니터링한 결과,
EWMA error statistic이 기준 오류 수준 대비 상승해 drift threshold를 넘었다.
이는 최근 오류율이 높게 반영된 supervised 성능 변화 후보 신호로 볼 수 있다.
다만 label 지연과 EWMA 가중치 설정에 따라 alarm 민감도가 달라지므로,
label 품질과 segment별 오류율을 함께 확인해야 한다.
```

---

## 변종: ECDD_WT_WARNING_DRIFT

`ECDD_WT_WARNING_DRIFT`는 ECDD-WT의 출력 상태를 warning과 drift로 명확히 나누어 운영 대응 단계를 구분하는 변종이다. Warning은 최근 오류율이 조사 대상 수준에 들어왔다는 신호이고, drift는 더 높은 threshold를 넘은 alarm 상태다. 따라서 자동 조치보다 단계적 모니터링, 알림, 조사 workflow가 중요한 환경에 적합하다.

이 변종은 다음 상황에 적합하다.

- error stream 기반 감시에서 warning 알림과 drift alarm을 별도 정책으로 운영한다.
- warning 단계에서는 관찰 강화나 데이터 보관을 하고, drift 단계에서만 조치 검토를 시작한다.
- 최근 오류율 변화의 심각도를 단계별로 보고서에 남겨야 한다.
- warning threshold와 drift threshold의 calibration 근거를 설명할 수 있다.

해석할 때는 warning state와 drift state를 같은 alarm으로 합치지 않는다. EWMA error statistic이 warning threshold를 넘으면 "조사 필요" 단계이며, drift threshold를 넘으면 "성능 변화 후보 alarm" 단계로 해석한다. Warning에서 drift로 전환된 시점과 지속 시간을 함께 기록하면, 일시적 오류 증가와 지속적 악화를 구분하는 데 도움이 된다.

주의할 점은 warning이 drift 확정이 아니라는 것이다. Warning 상태를 자동 재학습이나 배포 중단과 곧바로 연결하면 false alarm 비용이 커질 수 있다. 반대로 warning을 무시하면 drift alarm 전의 데이터 품질 문제나 class별 악화를 놓칠 수 있다. Label 지연, class imbalance, batch 단위 traffic 변화가 warning 지속 시간과 drift 전환 여부에 영향을 줄 수 있다.

보고서 문장 예시는 다음과 같다.

```text
binary error stream을 ECDD_WT_WARNING_DRIFT로 모니터링한 결과,
EWMA error statistic이 warning threshold를 넘은 뒤 drift threshold에 도달했다.
이는 최근 오류율 상승이 조사 단계에서 성능 변화 후보 alarm 단계로 진행된 신호로 볼 수 있다.
다만 warning은 drift 확정이 아니며 label 지연과 traffic mix 변화의 영향을 받을 수 있으므로,
warning 지속 구간의 데이터 품질과 class별 오류율을 함께 점검해야 한다.
```

---

## 변종: ECDD_WT_ERROR_STREAM

`ECDD_WT_ERROR_STREAM`은 ECDD-WT를 적용하기 전에 error stream 자체의 정의와 품질을 중심에 두는 변종이다. 입력은 예측이 틀리면 1, 맞으면 0인 순차 error stream이며, detector는 이 stream의 최근 가중 오류율이 기준 수준을 넘는지를 본다. 따라서 feature drift가 아니라 실제 label이 붙은 예측 오류 변화에 초점을 맞춰 보고해야 한다.

이 변종은 다음 상황에 적합하다.

- 예측 결과와 label을 결합해 일관된 0/1 error stream을 만들 수 있다.
- 오류 정의가 업무적으로 명확하고, partial label이나 delayed label 처리 규칙이 있다.
- feature drift보다 model performance drift 후보를 우선 확인하고 싶다.
- error stream 생성 로직, 누락 label 처리, class별 표본 수를 함께 검토할 수 있다.

해석할 때는 error stream의 값 분포와 ECDD-WT statistic을 같이 본다. Error 값 1이 최근 구간에서 더 자주 나타나 EWMA statistic이 threshold를 넘으면, 최근 예측 오류가 기준보다 증가한 성능 변화 후보 신호로 해석한다. 이때 detector 출력은 오류율 변화 신호이지, 어떤 feature가 변했는지 또는 왜 틀렸는지를 직접 설명하지 않는다.

주의할 점은 error stream 생성 방식이 detector 결과를 결정한다는 것이다. Label이 늦게 들어오는 사례를 제외하거나 임시로 correct로 처리하면 오류율이 왜곡될 수 있다. Class imbalance가 있으면 전체 error stream이 다수 class 중심으로 움직이고, minority class 문제를 늦게 감지할 수 있다. 업무 정책 변경, label 기준 변경, ground truth 정정도 drift처럼 보일 수 있으므로 stream 정의 변경 이력을 함께 남긴다.

보고서 문장 예시는 다음과 같다.

```text
0/1 error stream을 ECDD_WT_ERROR_STREAM으로 모니터링한 결과,
최근 구간에서 error 값 1의 가중 평균이 상승해 ECDD-WT threshold를 넘었다.
이는 label 기반 예측 오류가 증가한 성능 변화 후보 신호로 볼 수 있다.
다만 delayed label 처리와 error stream 생성 규칙에 따라 결과가 달라질 수 있으므로,
누락 label 비율과 class별 error stream을 함께 확인해야 한다.
```

---

## SelectionRule 카탈로그

```text
selectionRule ECDD_WT_DEFAULT_USE
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

> ECDD-WT 카탈로그는 "이 방법이 무엇인가"가 아니라, "어떤 상황에서 어떤 변종을 선택하고 어떤 주의사항과 함께 설명해야 하는가"를 구조화한다.
