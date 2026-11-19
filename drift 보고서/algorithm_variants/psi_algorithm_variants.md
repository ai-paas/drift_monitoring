# PSI 알고리즘 변종 목록

## 1. 목적

이 문서는 `PSI`를 하나의 고정된 detector로 보지 않고, drift monitoring에서 상황에 따라 선택해야 하는 **알고리즘 변종들의 family**로 정리한다.

핵심 목적은 다음이다.

```text
상황 조건 -> 적절한 PSI 계열 변종 -> 출력 metric -> 주의사항 -> LLM 보고서 설명
```

---

## 2. PSI의 위치

```text
methodFamily PSI
       ├─ algorithmVariant NUMERIC_BINNED_PSI
       ├─ algorithmVariant CATEGORICAL_PSI
       ├─ algorithmVariant SCORE_BAND_PSI
       └─ algorithmVariant POPULATION_WEIGHTED_PSI
```

`PSI`는 drift monitoring method 계열에 속한다. PSI 계열을 drift monitoring 문맥에서 입력 데이터와 운영 목적에 따라 선택 가능한 변종으로 정리한다.

---

## 3. 공통 개념

```text
methodFamily PSI
  purpose ->
    PSI 계열을 drift monitoring 문맥에서 입력 데이터와 운영 목적에 따라 선택 가능한 변종으로 정리한다.

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

## 변종: NUMERIC_BINNED_PSI

수치형 feature를 구간으로 나눈 뒤 reference와 current의 bin 비율 차이를 PSI로 계산하는 기본 변종이다. 운영 리포트에서 feature 분포 변화를 설명하기 쉽다.

- 사용 상황: age, score, amount, latency처럼 연속형 또는 순서형 값의 구간별 비중 변화를 감시할 때 적합하다.
- 해석 방법: PSI가 커지면 current의 bin 구성 비율이 reference와 달라졌다는 drift 후보로 본다.
- 주의점: bin 경계와 smoothing 정책에 민감하므로 reference 기준 binning을 고정하고 빈 bin 처리 방식을 기록한다.
- 보고서 문장 예시: "수치형 bin PSI가 상승해 current 구간의 feature 값 분포가 기준 기간의 구간 구성과 달라진 후보 신호가 확인되었다."

---

## 변종: CATEGORICAL_PSI

범주형 feature의 category 비율 변화를 PSI로 계산하는 변종이다. 지역, 채널, 상품군, 사용자 segment처럼 category mix 변화가 중요한 경우에 사용한다.

- 사용 상황: reference/current 사이 category 구성 비율이 바뀌었는지 업무 담당자가 바로 이해해야 할 때 적합하다.
- 해석 방법: 특정 category의 비중 변화가 PSI에 크게 기여하면 해당 category mix가 drift 후보의 중심이라고 본다.
- 주의점: 신규 category, 희소 category, category 병합 정책이 PSI를 크게 흔들 수 있으므로 처리 기준을 명시한다.
- 보고서 문장 예시: "범주형 PSI에서 일부 category 비중 변화가 크게 나타나 current 집단 구성 변화 후보가 확인되었다."

---

## 변종: SCORE_BAND_PSI

모델 score나 risk score를 업무상 의미 있는 score band로 나누어 PSI를 계산하는 변종이다. feature 원본보다 모델 출력 분포의 이동을 추적한다.

- 사용 상황: 승인/거절, 위험 등급, 신용 score band처럼 decision threshold 주변의 population 이동을 감시할 때 적합하다.
- 해석 방법: 고위험 또는 저위험 band 비율이 기준과 달라지면 모델 입력 population 또는 scoring 결과의 drift 후보로 본다.
- 주의점: score calibration이나 모델 버전이 바뀌면 PSI 변화가 데이터 drift가 아니라 scoring 체계 변경일 수 있다.
- 보고서 문장 예시: "Score band PSI가 증가해 current 기간의 모델 score 구간별 population 구성이 기준과 달라졌다."

---

## 변종: POPULATION_WEIGHTED_PSI

Segment별 중요도나 population weight를 반영해 PSI를 계산하는 변종이다. 단순 전체 PSI보다 업무 영향이 큰 집단의 변화를 더 크게 반영한다.

- 사용 상황: 고객군, 지역, 상품군마다 운영 중요도나 표본 대표성이 달라 weighted monitoring이 필요한 경우에 적합하다.
- 해석 방법: weighted PSI가 높으면 단순 비중 변화뿐 아니라 중요한 segment에서 drift 후보가 발생했다고 본다.
- 주의점: weight 산정 근거가 바뀌면 PSI 추세도 바뀌므로 weight 버전과 적용 기준을 함께 기록한다.
- 보고서 문장 예시: "Population-weighted PSI 기준으로 업무 영향도가 큰 segment에서 기준 대비 구성 변화 후보가 확인되었다."

---

## SelectionRule 카탈로그

```text
selectionRule PSI_DEFAULT_USE
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

> PSI 카탈로그는 "이 방법이 무엇인가"가 아니라, "어떤 상황에서 어떤 변종을 선택하고 어떤 주의사항과 함께 설명해야 하는가"를 구조화한다.
