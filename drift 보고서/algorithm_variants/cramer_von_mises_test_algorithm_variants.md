# Cramer-von Mises Test 알고리즘 변종 목록

## 1. 목적

이 문서는 `Cramer-von Mises Test`를 하나의 고정된 detector로 보지 않고, drift monitoring에서 상황에 따라 선택해야 하는 **알고리즘 변종들의 family**로 정리한다.

핵심 목적은 다음이다.

```text
상황 조건 -> 적절한 Cramer-von Mises Test 계열 변종 -> 출력 metric -> 주의사항 -> LLM 보고서 설명
```

---

## 2. Cramer-von Mises Test의 위치

```text
methodFamily CRAMER_VON_MISES_TEST
       ├─ algorithmVariant ONE_SAMPLE_CVM
       ├─ algorithmVariant TWO_SAMPLE_CVM
       └─ algorithmVariant K_SAMPLE_CVM
```

`Cramer-von Mises Test`는 drift monitoring method 계열에 속한다. Cramer-von Mises Test 계열을 drift monitoring 문맥에서 입력 데이터와 운영 목적에 따라 선택 가능한 변종으로 정리한다.

---

## 3. 공통 개념

```text
methodFamily CRAMER_VON_MISES_TEST
  purpose ->
    Cramer-von Mises Test 계열을 drift monitoring 문맥에서 입력 데이터와 운영 목적에 따라 선택 가능한 변종으로 정리한다.

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

## 변종: ONE_SAMPLE_CVM

`ONE_SAMPLE_CVM`은 현재 표본이 사전에 정의한 기준 누적분포함수와 같은 분포에서 나왔는지를 Cramer-von Mises statistic으로 검정하는 변종이다. 기준 분포가 이론 분포, 학습 기간의 fitted distribution, 또는 운영 정책상 정한 reference distribution으로 명확할 때 사용한다. 전체 분포의 누적 차이를 보므로 특정 한 지점의 차이보다 분포 전반의 어긋남을 감지하는 데 적합하다.

이 변종은 다음 상황에 적합하다.

- 비교 대상이 하나의 current sample과 고정된 기준 분포다.
- score, latency, confidence, calibration error처럼 연속형 또는 순서형 신호를 감시한다.
- 기준 누적분포함수 또는 fitted distribution의 출처가 명확하다.
- p-value와 함께 전체 분포가 기준과 얼마나 어긋나는지 보고해야 한다.

해석할 때는 Cramer-von Mises statistic과 p-value를 함께 본다. Statistic이 클수록 current empirical distribution과 기준 누적분포 사이의 차이가 크다는 뜻이다. p-value가 유의수준보다 작으면 current sample이 기준 분포와 같다는 가정에 맞지 않는 통계적 신호로 볼 수 있다. 효과 크기는 statistic의 크기, 기준 대비 분위수 이동, 실제 운영 metric 차이로 별도 확인한다.

주의할 점은 기준 분포가 현재 운영 조건을 대표하지 못하면 검정 결과가 drift가 아니라 baseline 정의 문제를 반영할 수 있다는 것이다. 표본 수가 작으면 tail 차이를 안정적으로 보기 어렵고, 표본 수가 매우 크면 작은 차이도 유의해질 수 있다. 데이터가 독립 동일분포라는 가정이 약한 시계열이나 중복 샘플에서는 window 구성과 sampling 방식을 함께 보고해야 한다. 검정 결과만으로 원인이나 성능 영향을 확정하지 않는다.

보고서 문장 예시는 다음과 같다.

```text
현재 window의 score 분포를 ONE_SAMPLE_CVM으로 기준 누적분포와 비교한 결과,
Cramer-von Mises statistic이 커지고 p-value가 유의수준보다 낮게 나타났다.
이는 현재 score 분포가 기준 분포와 같다는 가정에 맞지 않는 drift 후보 신호다.
다만 기준 분포의 대표성과 표본 수 효과가 결과에 영향을 줄 수 있으므로,
분위수 변화와 운영 metric 차이를 함께 확인해야 한다.
```

---

## 변종: TWO_SAMPLE_CVM

`TWO_SAMPLE_CVM`은 reference sample과 current sample의 경험적 누적분포가 같은지 비교하는 변종이다. 고정된 이론 분포를 가정하지 않고 두 기간의 관측값을 직접 비교한다는 점에서 one-sample 방식과 다르다. drift monitoring에서는 연속형 score나 numeric feature가 기준 기간 대비 전체 분포 형태에서 달라졌는지 확인할 때 사용한다.

이 변종은 다음 상황에 적합하다.

- reference window와 current window의 관측 sample을 직접 비교한다.
- 기준 분포를 parametric하게 정의하기 어렵지만 reference sample은 충분히 확보돼 있다.
- 평균 차이뿐 아니라 분산, tail, 분위수 이동을 포함한 전체 분포 차이를 보고 싶다.
- numeric feature, model score, latency 같은 연속형 monitoring 신호를 비교한다.

해석할 때는 Cramer-von Mises statistic과 p-value가 두 경험적 분포의 누적 차이를 얼마나 지지하는지 본다. Statistic이 클수록 reference와 current의 누적분포 차이가 크다는 뜻이다. p-value가 낮으면 두 sample이 같은 분포에서 나왔다는 가정과 맞지 않는 신호로 해석한다. 어느 구간이 차이를 주도하는지는 empirical CDF, 분위수 차이, density plot을 함께 확인한다.

주의할 점은 reference/current sample이 서로 독립적이고 같은 sampling 기준으로 추출됐는지 확인해야 한다는 것이다. 계절성, traffic mix, segment 구성 변화가 있으면 분포 차이가 모델 drift가 아니라 sampling 조건 차이일 수 있다. 표본 수가 크면 작은 차이도 유의할 수 있으므로 p-value와 실제 분위수 차이를 구분해 보고한다. 결과는 분포 변화 후보이며, 원인과 성능 영향은 후속 분석으로 확인해야 한다.

보고서 문장 예시는 다음과 같다.

```text
reference와 current score sample을 TWO_SAMPLE_CVM으로 비교한 결과,
Cramer-von Mises statistic이 상승하고 p-value가 유의수준 아래로 나타났다.
이는 두 기간의 score 분포가 같다는 가정과 맞지 않는 분포 변화 후보 신호다.
다만 traffic mix와 segment 구성 차이가 영향을 줄 수 있으므로,
empirical CDF와 분위수별 차이를 함께 확인해야 한다.
```

---

## 변종: K_SAMPLE_CVM

`K_SAMPLE_CVM`은 세 개 이상 sample group의 분포가 모두 같은지 비교하는 Cramer-von Mises 계열 변종이다. 여러 시간 window, region, channel, model version의 numeric signal을 동시에 비교할 때 사용한다. pairwise 비교를 반복하기 전에 전체 group 중 적어도 일부 분포가 다른지 screening하는 역할을 한다.

이 변종은 다음 상황에 적합하다.

- 세 개 이상의 기간 또는 segment 분포를 한 번에 비교한다.
- window별 score 분포가 특정 시점부터 달라졌는지 확인하고 싶다.
- region, channel, cohort별 numeric feature 분포 동질성을 점검한다.
- 전체 검정 이후 어떤 group이 차이를 주도하는지 후속 pairwise 분석을 계획한다.

해석할 때는 k-sample Cramer-von Mises statistic과 p-value를 먼저 본다. Statistic이 크고 p-value가 낮으면 모든 group이 같은 분포를 가진다는 가정과 맞지 않는 신호로 해석한다. 이 결과만으로 어느 group이 문제인지 알 수 없으므로 group별 empirical CDF, 분위수, pairwise comparison을 통해 차이가 집중된 window나 segment를 찾아야 한다.

주의할 점은 group 수가 많아질수록 표본 수 불균형과 다중 비교 문제가 커진다는 것이다. 전체 검정 후 pairwise 분석을 할 때는 유의수준 조정이나 운영 threshold 기준을 명확히 해야 한다. segment 정의가 시간에 따라 바뀌었거나 sample extraction 기준이 다르면 분포 차이가 drift가 아니라 데이터 구성 변경일 수 있다. p-value는 통계적 유의성이고, 운영상 의미 있는 변화인지는 효과 크기와 metric 차이로 별도 판단한다.

보고서 문장 예시는 다음과 같다.

```text
여러 monitoring window의 score 분포를 K_SAMPLE_CVM으로 비교한 결과,
k-sample statistic이 커지고 p-value가 유의수준보다 낮게 나타났다.
이는 모든 window의 score 분포가 동일하다는 가정과 맞지 않는 drift 후보 신호다.
다만 어느 window가 차이를 주도하는지는 전체 검정만으로 알 수 없으므로,
window별 empirical CDF와 후속 pairwise 비교를 함께 확인해야 한다.
```

---

## SelectionRule 카탈로그

```text
selectionRule CRAMER_VON_MISES_TEST_DEFAULT_USE
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

> Cramer-von Mises Test 카탈로그는 "이 방법이 무엇인가"가 아니라, "어떤 상황에서 어떤 변종을 선택하고 어떤 주의사항과 함께 설명해야 하는가"를 구조화한다.
