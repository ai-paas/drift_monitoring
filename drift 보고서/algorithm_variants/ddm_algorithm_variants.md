# DDM 알고리즘 변종 목록

## 1. 목적

이 문서는 `DDM`를 하나의 고정된 detector로 보지 않고, drift monitoring에서 상황에 따라 선택해야 하는 **알고리즘 변종들의 family**로 정리한다.

핵심 목적은 다음이다.

```text
상황 조건 -> 적절한 DDM 계열 변종 -> 출력 metric -> 주의사항 -> LLM 보고서 설명
```

---

## 2. DDM의 위치

```text
methodFamily DDM
       ├─ algorithmVariant DDM_STANDARD
       ├─ algorithmVariant DDM_WARNING_BUFFER
       └─ algorithmVariant DDM_CLASS_SPECIFIC
```

`DDM`는 error-rate statistical process concept drift detector 계열에 속한다. 분류 오류율과 표준편차가 과거 최소 기준에서 벗어나는지 감시한다.

---

## 3. 공통 개념

```text
methodFamily DDM
  purpose ->
    분류 오류율과 표준편차가 과거 최소 기준에서 벗어나는지 감시한다.

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

## 변종: DDM_STANDARD

`DDM_STANDARD`는 분류 결과가 맞았는지 틀렸는지를 0/1 error stream으로 받아 오류율과 표준편차의 증가를 감시하는 기본 DDM 변종이다. 과거에 관찰된 최소 오류 수준을 기준으로 현재 오류율이 warning 또는 drift threshold에 접근하는지를 판단한다. 따라서 label이 순차적으로 들어오는 online classification에서 sudden concept drift 후보를 감시할 때 적합하다.

이 변종은 다음 상황에 적합하다.

- 예측 직후 또는 지연 후에 정답 label이 확보되어 binary error stream을 만들 수 있다.
- 전체 오류율의 급격한 상승을 warning state와 drift state로 구분하고 싶다.
- feature 분포 변화보다 supervised performance 변화 후보가 중요한 monitoring 목적이다.
- label 지연과 label 품질을 운영 로그로 확인할 수 있다.

해석할 때는 `ERROR_RATE`, `STD`, `WARNING_STATE`, `DRIFT_STATE`를 함께 읽는다. 오류율과 표준편차의 합이 과거 최소 기준보다 커지면 warning state로, 더 높은 threshold를 넘으면 drift state로 해석한다. Warning은 조사와 관찰 강화가 필요한 단계이며, drift state는 오류율 기반의 성능 변화 후보 alarm으로 보고한다.

주의할 점은 DDM이 label 기반 supervised detector라는 것이다. Label이 지연되거나 특정 구간의 label 품질이 낮으면 detector가 실제 모델 변화가 아니라 label 수집 문제에 반응할 수 있다. Class imbalance가 심하면 전체 오류율이 minority class 저하를 가릴 수 있고, 반대로 작은 class의 오류 몇 건이 전체 판단을 흔들 수 있다. DDM 결과만으로 concept drift 원인을 확정하지 않고 feature drift, 배포 이력, segment별 오류율을 함께 확인해야 한다.

보고서 문장 예시는 다음과 같다.

```text
binary error stream을 DDM_STANDARD로 모니터링한 결과,
ERROR_RATE와 STD 조합이 과거 최소 오류 기준 대비 증가해 drift state에 도달했다.
이는 label 기반 오류율이 상승한 supervised drift 후보 신호로 볼 수 있다.
다만 label 지연, label 품질, class imbalance의 영향을 받을 수 있으므로,
동일 기간의 feature 분포 변화와 segment별 오류율을 함께 확인해야 한다.
```

---

## 변종: DDM_WARNING_BUFFER

`DDM_WARNING_BUFFER`는 DDM의 warning state가 시작된 이후의 instance를 별도 buffer에 보관해, drift alarm 이후 조사나 재학습 후보 데이터로 활용하는 변종이다. 탐지 로직의 핵심은 DDM과 같지만, warning 구간을 운영 대응 단위로 명시적으로 남긴다는 점이 다르다. 따라서 drift 발생 여부뿐 아니라 어떤 데이터를 재검토하거나 재학습 후보로 삼을지 함께 관리할 때 적합하다.

이 변종은 다음 상황에 적합하다.

- warning state 이후의 입력, 예측, label을 보관해 후속 분석에 쓰고 싶다.
- warning과 drift를 같은 의미로 취급하지 않고 운영 대응 단계를 분리해야 한다.
- 재학습 후보 데이터의 시작 시점과 포함 범위를 재현 가능하게 남겨야 한다.
- label 기반 error stream이 있고 warning buffer 저장 정책을 운영상 정의할 수 있다.

해석할 때는 `WARNING_START`, `BUFFERED_INSTANCES`, `DRIFT_STATE`를 분리해서 본다. `WARNING_START`는 오류율 변화가 조사 대상 수준에 들어간 시점이며, `BUFFERED_INSTANCES`는 그 이후 보관된 데이터 후보를 의미한다. `DRIFT_STATE`가 켜진 경우에만 drift alarm으로 보고하고, warning 자체는 drift 확정이 아니라 관찰 강화와 데이터 보관 신호로 설명한다.

주의할 점은 buffer 정책이 결과 해석과 재현성에 영향을 준다는 것이다. Warning 해제 시 buffer를 비울지, drift alarm 이후 어디까지 포함할지, label 지연 데이터를 어떻게 보정할지 사전에 정해야 한다. Warning 구간의 instance가 모두 drift 원인 데이터라는 뜻은 아니며, class imbalance나 traffic mix 변화가 buffer 구성을 왜곡할 수 있다. 자동 재학습으로 연결할 때는 validation 성능과 데이터 품질 검사를 별도로 둔다.

보고서 문장 예시는 다음과 같다.

```text
binary error stream을 DDM_WARNING_BUFFER로 모니터링한 결과,
WARNING_START 이후의 instance가 buffer에 저장되었고 이후 DRIFT_STATE가 활성화되었다.
이는 오류율 변화가 조사 단계에서 drift 후보 alarm 단계로 진행된 신호로 볼 수 있다.
다만 warning buffer는 재학습 확정 데이터가 아니라 후보 데이터이므로,
label 지연 보정과 class별 오류율 검토 후 재학습 사용 여부를 판단해야 한다.
```

---

## 변종: DDM_CLASS_SPECIFIC

`DDM_CLASS_SPECIFIC`은 전체 error stream을 하나로 합치지 않고 class별 오류율 흐름을 따로 감시하는 DDM 변종이다. 전체 정확도는 안정적으로 보여도 특정 class, 특히 minority class에서 오류율이 먼저 악화되는 경우를 보기 위해 사용한다. 따라서 모델 성능 저하 후보를 전체 평균이 아니라 class별 관점에서 설명해야 할 때 적합하다.

이 변종은 다음 상황에 적합하다.

- class별 label과 예측 결과가 충분히 축적되어 class error stream을 만들 수 있다.
- minority class, high-risk class, 규제상 중요한 class의 오류 증가를 별도로 감시해야 한다.
- 전체 오류율 평균이 특정 class의 악화를 가릴 수 있는 불균형 데이터다.
- class별 alarm을 보고서에서 별도 근거로 설명할 필요가 있다.

해석할 때는 `CLASS_ERROR_RATE`와 `CLASS_DRIFT_STATE`를 class별로 읽는다. 특정 class의 오류율과 표준편차가 해당 class의 과거 최소 기준 대비 threshold를 넘으면, 그 class에서 성능 변화 후보 alarm이 발생한 것으로 해석한다. 여러 class 중 어느 class에서 먼저 alarm이 발생했는지와 해당 class의 표본 수를 함께 보고해야 한다.

주의할 점은 class별 표본 수가 작을수록 오류율 변동성이 커진다는 것이다. 여러 class를 동시에 감시하면 다중 비교로 인한 false alarm 가능성이 커지며, minority class는 label 지연 몇 건만으로도 drift state가 흔들릴 수 있다. Class별 alarm은 전체 모델이 나빠졌다는 확정이 아니라 특정 class 오류 패턴 변화 후보로 표현해야 한다. Feature 분포, class prior 변화, annotation 정책 변경을 함께 확인한다.

보고서 문장 예시는 다음과 같다.

```text
class별 error stream을 DDM_CLASS_SPECIFIC으로 모니터링한 결과,
특정 class의 CLASS_ERROR_RATE가 과거 최소 오류 기준 대비 증가해 CLASS_DRIFT_STATE에 도달했다.
이는 전체 평균보다 해당 class에서 먼저 나타난 오류 패턴 변화 후보 신호로 볼 수 있다.
다만 class별 표본 수 부족과 다중 감시로 false alarm 가능성이 있으므로,
class prior 변화와 label 품질, segment별 성능을 함께 확인해야 한다.
```

---

## SelectionRule 카탈로그

```text
selectionRule DDM_DEFAULT_USE
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

> DDM 카탈로그는 "이 방법이 무엇인가"가 아니라, "어떤 상황에서 어떤 변종을 선택하고 어떤 주의사항과 함께 설명해야 하는가"를 구조화한다.
