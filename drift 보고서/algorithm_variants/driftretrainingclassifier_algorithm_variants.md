# DriftRetrainingClassifier 알고리즘 변종 목록

## 1. 목적

이 문서는 `DriftRetrainingClassifier`를 하나의 고정된 detector로 보지 않고, drift monitoring에서 상황에 따라 선택해야 하는 **알고리즘 변종들의 family**로 정리한다.

핵심 목적은 다음이다.

```text
상황 조건 -> 적절한 DriftRetrainingClassifier 계열 변종 -> 출력 metric -> 주의사항 -> LLM 보고서 설명
```

---

## 2. DriftRetrainingClassifier의 위치

```text
methodFamily DRIFTRETRAININGCLASSIFIER
       ├─ algorithmVariant DRIFT_RETRAINING_WITH_ADWIN
       ├─ algorithmVariant DRIFT_RETRAINING_WITH_PAGE_HINKLEY
       └─ algorithmVariant DRIFT_RETRAINING_CHAMPION_CHALLENGER
```

`DriftRetrainingClassifier`는 drift monitoring method 계열에 속한다. DriftRetrainingClassifier 계열을 drift monitoring 문맥에서 입력 데이터와 운영 목적에 따라 선택 가능한 변종으로 정리한다.

---

## 3. 공통 개념

```text
methodFamily DRIFTRETRAININGCLASSIFIER
  purpose ->
    DriftRetrainingClassifier 계열을 drift monitoring 문맥에서 입력 데이터와 운영 목적에 따라 선택 가능한 변종으로 정리한다.

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

## 변종: DRIFT_RETRAINING_WITH_ADWIN

`DRIFT_RETRAINING_WITH_ADWIN`은 classifier의 예측 성능 신호를 ADWIN 기반 detector로 감시하고, alarm이 발생하면 최근 window를 재학습 후보로 연결하는 변종이다. ADWIN은 데이터 stream의 평균 변화에 맞춰 window를 적응적으로 줄이거나 나누므로, 고정 window보다 변화 시점 주변의 최근 데이터를 빠르게 반영한다. 따라서 오류율, loss, reward처럼 순차적으로 들어오는 성능 신호에서 재학습 검토 시점을 자동화하고 싶을 때 적합하다.

이 변종은 다음 상황에 적합하다.

- 예측 결과와 label 또는 성능 proxy가 순차적으로 들어와 error/loss stream을 만들 수 있다.
- 운영 환경의 정상 변동 폭이 일정하지 않아 adaptive window가 필요하다.
- drift alarm 이후 최근 데이터를 재학습 후보로 모아 검증 pipeline에 넘기고 싶다.
- ADWIN delta, 최소 window 크기, 재학습 trigger 정책을 calibration할 수 있다.

해석할 때는 ADWIN alarm, 현재 window 크기 변화, 재학습 후보 window를 함께 본다. Alarm은 성능 신호의 평균이 이전 window와 통계적으로 달라졌다는 뜻이며, 곧바로 새 모델이 더 좋다는 뜻은 아니다. Window가 급격히 줄어든 시점은 detector가 최근 데이터를 더 강하게 반영하기 시작한 구간으로 보고, 재학습 후보 데이터의 시작점과 함께 기록한다.

주의할 점은 ADWIN의 민감도가 delta와 stream 정의에 크게 좌우된다는 것이다. Label 지연이 있으면 alarm 시점이 실제 운영 변화보다 늦게 보일 수 있고, error stream이 class imbalance에 영향을 받으면 재학습 후보도 특정 class에 치우칠 수 있다. 재학습은 alarm만으로 확정하지 말고 champion 대비 offline validation, segment 성능, 데이터 품질 검사를 통과해야 한다. 이 변종은 성능 변화 후보와 재학습 검토 시점을 제공하지, 원인이나 개선 효과를 보장하지 않는다.

보고서 문장 예시는 다음과 같다.

```text
classifier error stream을 DRIFT_RETRAINING_WITH_ADWIN으로 모니터링한 결과,
ADWIN alarm과 window 축소가 관찰되어 최근 구간이 재학습 후보로 표시되었다.
이는 오류율 평균이 이전 stream 구간과 달라진 성능 변화 후보 신호로 볼 수 있다.
다만 label 지연과 delta calibration의 영향을 받을 수 있으므로,
재학습 전 champion 대비 offline validation과 class별 성능 검토가 필요하다.
```

---

## 변종: DRIFT_RETRAINING_WITH_PAGE_HINKLEY

`DRIFT_RETRAINING_WITH_PAGE_HINKLEY`는 classifier의 error, loss, latency 같은 성능 stream에서 평균 수준의 지속적 상승을 Page-Hinkley 방식으로 감시하고, alarm을 재학습 검토 신호로 사용하는 변종이다. 단발성 spike보다 누적 편차가 threshold를 넘는지를 보므로, 성능 저하가 천천히 누적되는 상황을 잡는 데 유리하다. 재학습 trigger를 drift 후보 alarm과 분리해 검증 단계로 넘기는 운영에 적합하다.

이 변종은 다음 상황에 적합하다.

- error rate나 loss처럼 증가가 위험 신호인 성능 metric을 stream으로 감시한다.
- 급격한 한 번의 이상치보다 작은 악화가 계속 쌓이는지를 보고 싶다.
- Page-Hinkley threshold, delta, burn-in 기간을 운영 기준에 맞춰 설정할 수 있다.
- alarm 이후 최근 구간을 재학습 후보로 추출하되 자동 배포 전 검증 단계를 둔다.

해석할 때는 Page-Hinkley 누적 통계, threshold 초과 여부, alarm 시점을 함께 본다. 누적 통계가 threshold를 넘으면 성능 metric이 기준 수준 대비 지속적으로 악화됐다는 후보 신호로 해석한다. Alarm 시점은 변화 원인이 시작된 정확한 시점이 아니라 누적 증거가 충분해진 시점이며, 재학습 후보 window는 그 전후 구간으로 별도 정의해야 한다.

주의할 점은 이 변종이 방향성 있는 변화에 민감하다는 것이다. Metric 정의상 증가가 위험인지 먼저 확인해야 하며, traffic mix나 배치 지연으로 인한 metric 상승도 alarm을 만들 수 있다. Threshold를 낮게 잡으면 재학습 후보가 과도하게 생성되고, 높게 잡으면 실제 성능 저하 대응이 늦어질 수 있다. Label 기반 stream이라면 label 지연과 class imbalance를 반드시 함께 보고한다.

보고서 문장 예시는 다음과 같다.

```text
classifier loss stream을 DRIFT_RETRAINING_WITH_PAGE_HINKLEY로 모니터링한 결과,
Page-Hinkley 누적 통계가 기준 threshold를 넘어 재학습 검토 alarm이 발생했다.
이는 loss가 작은 폭으로 지속 상승한 성능 변화 후보 신호로 볼 수 있다.
다만 threshold와 delta 설정, traffic mix 변화에 따라 alarm 민감도가 달라지므로,
재학습 전 최근 window의 데이터 품질과 champion 대비 검증 성능을 확인해야 한다.
```

---

## 변종: DRIFT_RETRAINING_CHAMPION_CHALLENGER

`DRIFT_RETRAINING_CHAMPION_CHALLENGER`는 현재 운영 모델(champion)과 재학습 후보 모델(challenger)을 같은 evaluation window에서 비교해 교체 여부를 판단하는 변종이다. Drift detector alarm을 재학습 시작 신호로 쓰더라도, 최종 판단은 challenger가 champion보다 충분히 안정적으로 나은지에 둔다. 따라서 drift 후보 탐지와 모델 교체 결정을 분리해 운영 리스크를 낮추고 싶을 때 적합하다.

이 변종은 다음 상황에 적합하다.

- 재학습 후보 모델을 만들 수 있고 champion과 동일한 기준으로 평가할 수 있다.
- drift alarm 이후 바로 교체하지 않고 challenger 검증 단계를 두어야 한다.
- accuracy, loss, calibration, business metric 등 교체 기준을 사전에 정의할 수 있다.
- traffic shadowing, holdout 검증, segment별 비교 결과를 보고서에 남길 수 있다.

해석할 때는 champion metric, challenger metric, uplift 또는 degradation, promotion decision을 함께 본다. Challenger가 전체 metric뿐 아니라 주요 segment에서도 champion보다 안정적으로 나을 때만 교체 후보로 해석한다. Drift alarm이 있어도 challenger가 개선을 보이지 않으면 "drift 후보는 관찰됐지만 교체 근거는 부족"하다고 보고한다.

주의할 점은 champion-challenger 비교가 데이터 분할과 평가 지연에 민감하다는 것이다. 같은 기간, 같은 label 품질, 같은 traffic mix에서 비교하지 않으면 uplift가 모델 개선이 아니라 평가 조건 차이일 수 있다. Class imbalance가 있으면 전체 평균 uplift가 minority class degradation을 숨길 수 있으므로 segment별 guardrail을 둔다. Challenger 승리는 원인 확정이 아니라 배포 검토 근거이며, 실제 교체는 rollback 계획과 온라인 모니터링을 포함해야 한다.

보고서 문장 예시는 다음과 같다.

```text
drift 후보 구간에서 DRIFT_RETRAINING_CHAMPION_CHALLENGER를 적용한 결과,
challenger 모델이 evaluation window에서 champion 대비 주요 성능 metric 개선을 보였다.
이는 재학습 후보 모델을 배포 검토 대상으로 올릴 수 있는 운영 신호로 볼 수 있다.
다만 같은 label 품질과 traffic mix에서 비교했는지, minority class 성능 저하가 없는지 확인한 뒤
promotion decision과 rollback 계획을 별도로 확정해야 한다.
```

---

## SelectionRule 카탈로그

```text
selectionRule DRIFTRETRAININGCLASSIFIER_DEFAULT_USE
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

> DriftRetrainingClassifier 카탈로그는 "이 방법이 무엇인가"가 아니라, "어떤 상황에서 어떤 변종을 선택하고 어떤 주의사항과 함께 설명해야 하는가"를 구조화한다.
