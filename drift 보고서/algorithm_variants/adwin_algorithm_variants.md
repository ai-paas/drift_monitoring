# ADWIN 알고리즘 변종 목록

## 1. 목적

이 문서는 `ADWIN`를 하나의 고정된 detector로 보지 않고, drift monitoring에서 상황에 따라 선택해야 하는 **알고리즘 변종들의 family**로 정리한다.

핵심 목적은 다음이다.

```text
상황 조건 -> 적절한 ADWIN 계열 변종 -> 출력 metric -> 주의사항 -> LLM 보고서 설명
```

---

## 2. ADWIN의 위치

```text
methodFamily ADWIN
       ├─ algorithmVariant ADWIN_MEAN_STREAM
       ├─ algorithmVariant ADWIN_ERROR_RATE
       └─ algorithmVariant ADWIN_DISTANCE_STREAM
```

`ADWIN`는 adaptive window streaming drift detector 계열에 속한다. 스트림에서 adaptive window를 유지하며 과거/최근 구간 평균 차이로 변화 시점을 감지한다.

---

## 3. 공통 개념

```text
methodFamily ADWIN
  purpose ->
    스트림에서 adaptive window를 유지하며 과거/최근 구간 평균 차이로 변화 시점을 감지한다.

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

## 변종: ADWIN_MEAN_STREAM

`ADWIN_MEAN_STREAM`은 시간 순서로 들어오는 연속형 숫자 지표의 평균 수준이 바뀌었는지를 감시하는 변종이다. 원본 feature, 모델 confidence, latency, loss 같은 값을 스트림으로 넣고, ADWIN이 adaptive window 안에서 과거 구간과 최근 구간의 평균 차이를 비교한다. 결과는 "평균 수준 변화가 감지된 시점"에 대한 drift 후보 신호로 읽어야 한다.

이 변종은 다음 상황에 적합하다.

- 연속형 metric이 시간 순서대로 안정적으로 수집된다.
- 평균 변화 자체가 운영상 중요한 신호다.
- 고정 window보다 변화 시점에 맞춰 window가 줄어들거나 늘어나는 adaptive monitoring이 필요하다.
- label 없이도 loss, confidence, latency, numeric KPI 같은 관측값의 변화 후보를 보고 싶다.

해석할 때는 `DRIFT_ALARM`과 `ADAPTIVE_WINDOW_WIDTH`를 함께 본다. Alarm은 최근 구간의 평균이 과거 adaptive window와 충분히 달라졌다고 ADWIN이 판단한 시점이다. Window width가 급격히 줄어들면 오래된 관측값을 버리고 최근 수준을 새 기준으로 삼기 시작했다는 뜻이다. 평균이 커졌는지 작아졌는지는 원 metric chart와 alarm 전후 평균을 함께 확인해야 한다.

주의할 점은 ADWIN이 평균 변화에 민감한 detector라는 점이다. 강한 계절성, 배치성 수집, 반복적인 주기 변동이 제거되지 않으면 운영 패턴을 drift 후보로 잘못 볼 수 있다. `delta` 설정은 false alarm과 detection delay를 좌우하므로, 보고서에서는 이 값을 보편적 기준이 아니라 운영 calibration 결과로 설명해야 한다. 이 결과만으로 원인이나 모델 성능 저하를 확정하지 않는다.

보고서 문장 예시는 다음과 같다.

```text
연속형 metric stream을 ADWIN_MEAN_STREAM으로 모니터링한 결과,
최근 adaptive window에서 평균 수준이 과거 구간과 달라지며 drift alarm이 발생했다.
이는 해당 metric의 시간적 평균 변화 후보 신호로 볼 수 있다.
다만 계절성, 수집 주기, delta 설정의 영향을 받을 수 있으므로
alarm 전후 원 metric 추세와 운영 이벤트를 함께 확인해야 한다.
```

---

## 변종: ADWIN_ERROR_RATE

`ADWIN_ERROR_RATE`는 온라인 분류 결과에서 정답 label이 도착한 뒤 계산한 오류 여부 또는 오류율 stream을 감시하는 변종이다. 입력은 원본 feature가 아니라 0/1 error, rolling error rate, misclassification indicator 같은 성능 신호다. 따라서 alarm은 데이터 분포 변화 자체가 아니라 supervised 성능 변화 후보로 해석한다.

이 변종은 다음 상황에 적합하다.

- 예측 이후 정답 label이 일정한 지연 안에 도착한다.
- classification error, wrong prediction flag, error rate를 시간 순서대로 만들 수 있다.
- 모델 성능 저하 후보를 운영 중 빠르게 감지해야 한다.
- concept drift 여부를 직접 단정하기보다 오류율 변화 기반의 supervised drift 후보를 선별하려 한다.

해석할 때는 `ERROR_RATE_WINDOW`와 `DRIFT_ALARM`을 분리해서 본다. `ERROR_RATE_WINDOW`는 adaptive window 안에서 관측된 오류 수준이며, alarm은 최근 오류율이 과거 window와 달라졌다는 신호다. 오류율이 상승하면 성능 악화 후보로 볼 수 있고, 오류율이 하락해도 데이터 구성이나 난이도 변화 신호일 수 있다. alarm 시점은 label이 도착한 시점 기준이므로 실제 입력 데이터 변화 시점보다 늦을 수 있다.

주의할 점은 label 지연, label 품질, class imbalance가 결과를 크게 흔든다는 것이다. 특정 class 비중이 바뀌면 오류율 변화가 concept drift 때문인지 class mix 변화 때문인지 분리하기 어렵다. error stream 정의도 명확해야 하며, top-1 오분류, threshold 기반 오답, human review label 중 무엇을 썼는지 보고서에 남겨야 한다. 이 변종의 결과만으로 업무 원인이나 feature drift를 확정하지 않는다.

보고서 문장 예시는 다음과 같다.

```text
온라인 분류 오류 stream을 ADWIN_ERROR_RATE로 모니터링한 결과,
최근 오류율 window가 과거 adaptive window 대비 달라지며 supervised drift alarm이 발생했다.
이는 모델 성능 변화 후보 신호로 볼 수 있다.
다만 label 지연, class imbalance, 오류 정의의 영향을 받을 수 있으므로
class별 오류율과 label 수집 상태를 함께 확인해야 한다.
```

---

## 변종: ADWIN_DISTANCE_STREAM

`ADWIN_DISTANCE_STREAM`은 원본 데이터 값을 바로 ADWIN에 넣는 변종이 아니다. 먼저 Wasserstein, MMD, PSI 같은 방법으로 window별 분포 차이 점수나 거리 값을 계산하고, 그 거리 값의 시간 흐름을 다시 ADWIN이 감시하는 방식이다.

이 변종은 다음 상황에 적합하다.

- 이미 window별 drift score 또는 distance가 계산되어 있다.
- 개별 window의 distance가 threshold를 한 번 넘었는지보다, distance stream이 어느 시점부터 지속적으로 커지는지가 중요하다.
- Wasserstein distance, MMD score, PSI score처럼 값 자체는 batch 비교 지표지만 운영에서는 streaming alarm이 필요하다.

해석할 때는 두 단계를 분리해야 한다. 첫 번째 단계는 원 detector가 만든 distance의 의미다. 예를 들어 Wasserstein distance가 커졌다면 기준 분포와 현재 분포의 위치나 모양이 달라졌다는 뜻이다. 두 번째 단계는 ADWIN이 그 distance stream에서 평균 수준의 변화를 감지했다는 뜻이다. 따라서 보고서에서는 "원본 feature가 ADWIN으로 직접 drift 판정되었다"가 아니라, "window별 분포 거리 값의 상승 흐름을 ADWIN이 감지했다"고 표현해야 한다.

출력은 보통 `DISTANCE_STREAM_ALARM`과 `WINDOW_WIDTH`로 읽는다. Alarm은 distance stream의 변화 시점을 나타내고, window width는 ADWIN이 변화 전후 구간을 분리하면서 adaptive window를 얼마나 줄이거나 유지했는지를 보여준다. Window width가 급격히 줄어들면 최근 distance 수준이 과거와 달라져 ADWIN이 오래된 구간을 버린 것으로 해석한다.

주의할 점은 원 detector의 threshold와 ADWIN threshold를 혼동하지 않는 것이다. Wasserstein, MMD, PSI의 threshold는 "분포 차이 자체가 큰가"를 판단하는 기준이고, ADWIN의 threshold 또는 delta는 "distance stream의 평균 변화가 통계적으로 충분한가"를 판단하는 기준이다. 두 기준은 같은 의미가 아니며, 하나가 작동했다고 다른 하나의 결론까지 자동으로 확정되는 것은 아니다.

보고서 문장 예시는 다음과 같다.

```text
Window별 Wasserstein distance를 ADWIN에 입력해 모니터링한 결과,
최근 구간의 distance 평균이 과거 adaptive window 대비 상승하면서
ADWIN distance-stream alarm이 발생했다.
이는 분포 거리 값의 시간적 증가가 감지된 사례이며,
실제 drift 원인은 원 distance chart와 feature/segment 분석으로 별도 확인해야 한다.
```

---

## SelectionRule 카탈로그

```text
selectionRule ADWIN_DEFAULT_USE
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

> ADWIN 카탈로그는 "이 방법이 무엇인가"가 아니라, "어떤 상황에서 어떤 변종을 선택하고 어떤 주의사항과 함께 설명해야 하는가"를 구조화한다.
