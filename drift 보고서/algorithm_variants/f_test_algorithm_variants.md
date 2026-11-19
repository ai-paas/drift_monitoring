# F-test 알고리즘 변종 목록

## 1. 목적

이 문서는 `F-test`를 하나의 고정된 detector로 보지 않고, drift monitoring에서 상황에 따라 선택해야 하는 **알고리즘 변종들의 family**로 정리한다.

핵심 목적은 다음이다.

```text
상황 조건 -> 적절한 F-test 계열 변종 -> 출력 metric -> 주의사항 -> LLM 보고서 설명
```

---

## 2. F-test의 위치

```text
methodFamily F_TEST
       ├─ algorithmVariant F_TEST_EQUAL_VARIANCE
       ├─ algorithmVariant ANOVA_F_TEST_GROUP_MEAN
       └─ algorithmVariant MODEL_COMPARISON_F_TEST
```

`F-test`는 drift monitoring method 계열에 속한다. F-test 계열을 drift monitoring 문맥에서 입력 데이터와 운영 목적에 따라 선택 가능한 변종으로 정리한다.

---

## 3. 공통 개념

```text
methodFamily F_TEST
  purpose ->
    F-test 계열을 drift monitoring 문맥에서 입력 데이터와 운영 목적에 따라 선택 가능한 변종으로 정리한다.

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

## 변종: F_TEST_EQUAL_VARIANCE

`F_TEST_EQUAL_VARIANCE`는 reference 기간과 current 기간의 분산이 같은지 비교하는 F-test 변종이다. 평균이 비슷해 보여도 값의 퍼짐이 달라지면 모델 입력의 안정성이나 운영 지표의 변동성이 달라졌을 수 있다. 출력은 F statistic, p-value, 유의수준 또는 운영 threshold 기준의 alarm으로 해석한다.

사용 상황:
- 단일 수치형 feature, score, latency, 비용처럼 분산 변화가 중요한 지표를 비교할 때
- 평균 변화보다 변동성 증가, 극단값 확대, 품질 편차 증가를 먼저 확인하고 싶을 때
- t-test나 평균 비교 결과를 해석하기 전에 등분산 가정이 유지되는지 확인할 때

해석 방법:
- F statistic은 두 기간의 표본 분산 비율을 나타내며, 1에서 멀어질수록 분산 차이 근거가 커진다.
- p-value가 작으면 reference/current 분산이 같다는 가설을 기각할 통계적 근거가 강하다.
- alarm은 p-value 또는 분산 비율이 운영 기준을 넘었는지 나타내며, 실제 영향은 지표 단위와 변동성 크기를 함께 본다.
- 분산이 커진 경우에는 box plot, quantile, 극단값 비율을 같이 확인하면 변화 구간을 설명하기 쉽다.

주의점:
- 정규성 가정에 민감하므로 분포가 심하게 치우치거나 outlier가 많으면 Levene 계열 같은 robust 검정을 함께 검토한다.
- p-value는 유의성 지표이고 분산 변화의 업무 영향을 직접 말해주지는 않는다.
- 표본 수가 작으면 분산 추정이 불안정하고, 표본 수가 매우 크면 작은 차이도 유의하게 나올 수 있다.

보고서 문장 예시:

```text
수치형 지표의 reference/current 분산을 F_TEST_EQUAL_VARIANCE로 비교한 결과,
F statistic과 p-value가 두 기간의 변동성 차이 가능성을 보였다.
이는 평균 변화와 별개로 값의 퍼짐이 달라졌을 수 있다는 drift 후보 신호다.
다만 outlier와 분포 비대칭에 민감하므로, box plot과 robust 분산 검정을 함께 확인해야 한다.
```

---

## 변종: ANOVA_F_TEST_GROUP_MEAN

`ANOVA_F_TEST_GROUP_MEAN`은 세 개 이상 group, segment, time window의 평균이 모두 같다고 볼 수 있는지 평가하는 ANOVA F-test 변종이다. 단순 reference/current 두 기간 비교를 넘어 여러 운영 구간 사이에서 평균 수준이 달라지는지 screening할 때 사용한다. 출력 F statistic은 group 간 평균 차이가 group 내부 변동에 비해 얼마나 큰지 요약한다.

사용 상황:
- 여러 날짜, 지역, 고객 segment, 모델 버전별 평균 지표를 한 번에 비교할 때
- 단일 current window보다 여러 window를 놓고 평균 drift 후보가 어디서 시작됐는지 보고 싶을 때
- 평균 차이의 통계적 유의성을 보고서 보조 근거로 제시해야 할 때

해석 방법:
- F statistic이 클수록 group 간 평균 차이가 group 내부 변동보다 크다는 뜻이다.
- p-value가 작으면 모든 group 평균이 같다는 가설을 기각할 근거가 강하다.
- alarm은 ANOVA 결과가 운영 기준을 넘었다는 screening 신호이며, 어떤 group이 달라졌는지는 사후 비교나 group별 평균 차이로 확인한다.
- drift 설명에서는 유의성, 평균 차이 크기, 영향을 받은 group을 분리해 보고한다.

주의점:
- ANOVA는 독립성, 등분산성, 잔차 분포 가정의 영향을 받는다.
- 유의한 결과가 나와도 어느 group이 원인인지는 F-test만으로 확정할 수 없다.
- group별 표본 수가 크게 다르거나 outlier가 많으면 p-value가 왜곡될 수 있어 robust 요약을 함께 본다.

보고서 문장 예시:

```text
여러 운영 구간의 평균 지표를 ANOVA_F_TEST_GROUP_MEAN으로 비교한 결과,
F statistic과 p-value가 group 간 평균 차이 가능성을 보였다.
이는 특정 기간 또는 segment에서 평균 수준이 달라졌을 수 있다는 drift 후보 신호다.
다만 원인 group은 ANOVA만으로 확정할 수 없으므로, 사후 비교와 group별 effect size를 함께 확인해야 한다.
```

---

## 변종: MODEL_COMPARISON_F_TEST

`MODEL_COMPARISON_F_TEST`는 제한된 모델과 더 복잡한 모델의 설명력이 유의하게 다른지 비교하는 F-test 변종이다. Drift monitoring에서는 시간, segment, drift indicator를 추가한 모델이 기존 모델보다 잔차를 의미 있게 줄이는지 확인해 변화 후보를 설명할 수 있다. 출력은 model comparison F statistic, p-value, 선택한 비교 기준의 alarm으로 읽는다.

사용 상황:
- reference/current indicator를 추가했을 때 예측 오차나 잔차 설명력이 개선되는지 확인할 때
- 운영 구간, 정책 변경, 모델 버전 변수가 결과 지표를 설명하는지 보조 분석할 때
- 단순 분포 검정보다 모델 기반으로 변화 신호를 보고서에 설명해야 할 때

해석 방법:
- F statistic이 클수록 추가 변수 또는 복잡한 모델이 잔차를 더 많이 설명한다는 근거가 커진다.
- p-value가 작으면 제한 모델 대비 확장 모델의 개선이 우연이라고 보기 어렵다는 뜻이다.
- alarm은 모델 비교 결과가 사전 기준을 넘었다는 신호이며, drift 원인을 확정하는 증거는 아니다.
- 보고서에서는 어떤 변수를 추가한 비교인지, 잔차 또는 성능 지표가 얼마나 개선됐는지 함께 적는다.

주의점:
- 비교 대상 모델은 nested 구조여야 하며, 모델 사양이 부적절하면 F-test 해석이 약해진다.
- 설명력이 개선됐다고 해서 운영 원인이나 concept drift가 자동으로 확정되지는 않는다.
- 과적합, 다중공선성, 표본 구간 선택에 따라 p-value가 달라질 수 있다.

보고서 문장 예시:

```text
기준 모델과 drift indicator를 포함한 확장 모델을 MODEL_COMPARISON_F_TEST로 비교한 결과,
확장 모델의 설명력 개선이 통계적으로 유의한 후보 신호로 나타났다.
이는 기간 또는 segment 정보가 결과 지표 변화를 설명할 가능성을 시사한다.
다만 모델 비교 결과만으로 원인을 확정할 수 없으므로, 변수 정의와 잔차 진단을 함께 검토해야 한다.
```

---

## SelectionRule 카탈로그

```text
selectionRule F_TEST_DEFAULT_USE
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

> F-test 카탈로그는 "이 방법이 무엇인가"가 아니라, "어떤 상황에서 어떤 변종을 선택하고 어떤 주의사항과 함께 설명해야 하는가"를 구조화한다.
