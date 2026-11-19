# Anderson-Darling Test 알고리즘 변종 목록

## 1. 목적

이 문서는 `Anderson-Darling Test`를 하나의 고정된 detector로 보지 않고, drift monitoring에서 상황에 따라 선택해야 하는 **알고리즘 변종들의 family**로 정리한다.

핵심 목적은 다음이다.

```text
상황 조건 -> 적절한 Anderson-Darling Test 계열 변종 -> 출력 metric -> 주의사항 -> LLM 보고서 설명
```

---

## 2. Anderson-Darling Test의 위치

```text
methodFamily ANDERSON_DARLING_TEST
       ├─ algorithmVariant ONE_SAMPLE_ANDERSON_DARLING
       ├─ algorithmVariant TWO_SAMPLE_ANDERSON_DARLING
       ├─ algorithmVariant K_SAMPLE_ANDERSON_DARLING
       └─ algorithmVariant TAIL_SENSITIVE_AD
```

`Anderson-Darling Test`는 drift monitoring method 계열에 속한다. Anderson-Darling Test 계열을 drift monitoring 문맥에서 입력 데이터와 운영 목적에 따라 선택 가능한 변종으로 정리한다.

---

## 3. 공통 개념

```text
methodFamily ANDERSON_DARLING_TEST
  purpose ->
    Anderson-Darling Test 계열을 drift monitoring 문맥에서 입력 데이터와 운영 목적에 따라 선택 가능한 변종으로 정리한다.

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

## 변종: ONE_SAMPLE_ANDERSON_DARLING

`ONE_SAMPLE_ANDERSON_DARLING`은 현재 관측값 표본이 사전에 정한 기준 분포를 따르는지 확인하는 변종이다. reference sample과 current sample을 직접 비교하기보다, 정규분포나 과거 calibration으로 정한 이론 분포를 기준으로 current sample의 적합도를 본다. drift monitoring에서는 기준 분포에서 벗어난 정도를 분포 변화 후보 신호로 사용한다.

이 변종은 다음 상황에 적합하다.

- 비교할 reference sample이 없고 기준 이론 분포 또는 calibration 분포가 정의되어 있다.
- 단일 feature나 score가 특정 분포 가정을 유지하는지 점검해야 한다.
- 운영 기준선이 평균과 분산 같은 분포 파라미터로 관리된다.
- current window가 기준 분포에서 벗어났는지 빠르게 screening하려 한다.

해석할 때는 Anderson-Darling statistic과 p-value를 구분한다. Statistic이 클수록 관측 표본과 기준 분포의 차이가 크다는 뜻이며, 특히 누적분포의 양쪽 꼬리 차이에 민감하다. p-value는 기준 분포 가정 아래에서 이 정도 차이가 우연히 나타날 가능성을 나타내는 통계적 유의성이다. p-value가 작아도 실제 업무 영향의 크기는 별도 효과 크기나 차트로 확인해야 한다.

주의할 점은 기준 분포가 잘못 정의되면 검정 결과도 의미가 약해진다는 것이다. 표본 수가 매우 크면 작은 차이도 유의하게 나올 수 있고, 표본 수가 작으면 실제 차이를 놓칠 수 있다. 추정한 파라미터를 같은 데이터에서 다시 검정에 쓰는 경우 p-value 해석이 보수적이지 않을 수 있다. 이 결과만으로 원인이나 모델 성능 저하를 확정하지 않는다.

보고서 문장 예시는 다음과 같다.

```text
현재 window의 score 분포를 ONE_SAMPLE_ANDERSON_DARLING으로 기준 분포와 비교한 결과,
Anderson-Darling statistic이 커지고 p-value가 유의수준 아래로 내려갔다.
이는 현재 표본이 사전 기준 분포에서 벗어난 drift 후보 신호로 볼 수 있다.
다만 기준 분포 설정과 sample size의 영향을 받으므로
분포 차트와 운영 기준선 정의를 함께 확인해야 한다.
```

---

## 변종: TWO_SAMPLE_ANDERSON_DARLING

`TWO_SAMPLE_ANDERSON_DARLING`은 reference window와 current window의 두 표본이 같은 분포에서 왔는지 비교하는 변종이다. 이론 분포를 가정하기보다 두 기간의 경험적 분포를 직접 비교한다. drift monitoring에서는 current 분포가 reference 분포와 달라졌는지 확인하는 기본적인 두 기간 비교 신호로 쓴다.

이 변종은 다음 상황에 적합하다.

- 기준 기간과 현재 기간의 raw value 또는 score sample이 모두 있다.
- 평균뿐 아니라 분포 모양, 산포, 꼬리 차이까지 비교하고 싶다.
- 단일 feature, model score, residual, probability output의 reference/current 차이를 screening한다.
- 동일한 수집 방식으로 만든 두 window를 비교할 수 있다.

해석할 때는 test statistic이 두 경험적 누적분포의 차이를 요약한다는 점을 먼저 본다. 값이 클수록 reference와 current의 분포 차이가 크다는 신호이며, Anderson-Darling 계열은 꼬리 영역 차이에 Kolmogorov-Smirnov보다 더 민감하게 반응할 수 있다. p-value는 "두 표본이 같은 분포에서 왔다"는 귀무가설 아래의 통계적 유의성이다. p-value가 작으면 drift 후보로 볼 수 있지만, 차이가 어느 구간에서 났는지는 histogram, ECDF, quantile 비교로 확인해야 한다.

주의할 점은 두 표본의 수집 조건이 달라지면 검정이 운영 변화까지 함께 잡는다는 것이다. sample size가 크면 미세한 차이도 유의하게 나오며, 반복 검정하는 feature가 많으면 다중검정 보정이나 우선순위 기준이 필요하다. reference window가 이미 불안정하면 current 차이를 drift로 해석하기 어렵다. 결과는 분포 변화 후보이지 원인 확정이나 성능 저하 확정이 아니다.

보고서 문장 예시는 다음과 같다.

```text
기준 window와 현재 window를 TWO_SAMPLE_ANDERSON_DARLING으로 비교한 결과,
검정 통계량이 증가하고 p-value가 유의수준 아래로 내려갔다.
이는 두 기간의 경험적 분포가 같다는 가정과 맞지 않는 drift 후보 신호다.
다만 차이가 발생한 구간과 업무 원인은
ECDF, quantile, segment별 비교로 추가 확인해야 한다.
```

---

## 변종: K_SAMPLE_ANDERSON_DARLING

`K_SAMPLE_ANDERSON_DARLING`은 세 개 이상 기간이나 segment의 표본 분포가 모두 같은지 한 번에 비교하는 변종이다. 단순히 reference와 current만 비교하지 않고, 여러 window나 여러 집단 사이에 분포 차이가 존재하는지를 screening한다. drift monitoring에서는 변화가 특정 기간 하나의 문제가 아니라 시간대, region, cohort 등 여러 그룹 사이의 분포 불일치인지 확인할 때 유용하다.

이 변종은 다음 상황에 적합하다.

- 세 개 이상 time window를 동시에 비교한다.
- 여러 segment, cohort, region, channel의 score 분포가 같은지 확인한다.
- 어느 한 pair를 미리 고르기 어렵고 전체 차이 존재 여부를 먼저 보고 싶다.
- pairwise test를 반복하기 전에 drift 후보가 있는 그룹 묶음을 선별하려 한다.

해석할 때는 k-sample statistic이 모든 그룹의 경험적 분포 차이를 종합한 값이라는 점을 본다. statistic이 크고 p-value가 작으면 "모든 그룹 분포가 같다"는 가정과 맞지 않는다는 뜻이다. 그러나 이 결과만으로 어느 두 그룹이 다른지는 알 수 없으므로, 사후 pairwise 비교나 그룹별 ECDF 차트가 필요하다. p-value는 전체 차이의 통계적 유의성을 말하고, 업무상 영향 크기는 그룹별 차이 크기로 별도 판단한다.

주의할 점은 그룹 수가 많고 sample size가 불균형하면 일부 큰 그룹이나 특이 그룹이 결과를 주도할 수 있다는 것이다. 같은 데이터를 여러 방식으로 나눠 반복 검정하면 false alarm이 늘 수 있다. segment 정의가 운영 정책 변경을 반영한다면, 검정 결과는 데이터 drift와 운영 segmentation 효과를 함께 포함한다. 전체 유의 결과를 모든 그룹의 drift로 확대 해석하지 않는다.

보고서 문장 예시는 다음과 같다.

```text
여러 기간의 score sample을 K_SAMPLE_ANDERSON_DARLING으로 비교한 결과,
전체 분포 동일성 가정이 기각되는 수준의 p-value가 관측되었다.
이는 적어도 일부 기간 또는 segment에서 분포 변화 후보가 있음을 시사한다.
다만 어떤 그룹이 차이를 주도했는지는
pairwise 비교와 그룹별 ECDF 차트로 별도 확인해야 한다.
```

---

## 변종: TAIL_SENSITIVE_AD

`TAIL_SENSITIVE_AD`는 Anderson-Darling 계열의 꼬리 민감도를 drift monitoring 목적에 맞게 강조해 사용하는 변종이다. 평균 부근보다 상위 또는 하위 tail의 변화가 중요할 때, reference/current 분포 차이가 극단값 영역에서 커지는지를 중점적으로 본다. 예측 score의 낮은 confidence tail, latency 상위 tail, risk score 상위 tail처럼 운영 리스크가 tail에 집중될 때 적합하다.

이 변종은 다음 상황에 적합하다.

- 상위 또는 하위 quantile 변화가 평균 변화보다 중요하다.
- latency p95/p99, high-risk score, low-confidence prediction 같은 tail 지표를 감시한다.
- 극단값 증가가 운영 장애, 심사 부담, 모델 신뢰도 저하 후보로 이어질 수 있다.
- 일반 two-sample 비교에서 평균 차이는 작지만 tail 차이를 놓치고 싶지 않다.

해석할 때는 test statistic과 p-value를 tail 차이의 후보 신호로 읽는다. statistic이 커지면 reference와 current의 누적분포 차이가 특히 꼬리 영역에서 커졌을 가능성이 있다. p-value는 통계적 유의성일 뿐, tail에서 실제로 얼마나 많은 case가 늘었는지는 quantile, exceedance rate, tail count로 확인해야 한다. alarm 또는 유의 결과가 나오면 어느 tail 방향이 문제인지 상위/하위 구간을 분리해서 본다.

주의할 점은 tail sample 수가 적으면 결과가 불안정하다는 것이다. 극단값 처리, clipping, winsorizing, missing value 정책이 바뀌면 tail-sensitive 결과가 크게 달라질 수 있다. tail 변화는 rare event 증가 신호일 수 있지만, 그 자체로 성능 저하나 업무 손실을 확정하지 않는다. threshold는 운영 리스크 기준이나 calibration 기준으로 설명해야 한다.

보고서 문장 예시는 다음과 같다.

```text
score 분포의 꼬리 영역을 TAIL_SENSITIVE_AD로 비교한 결과,
current window에서 tail 차이에 민감한 검정 통계량이 증가했다.
이는 평균 수준 변화보다 극단 구간의 분포 변화 후보가 두드러진다는 신호로 볼 수 있다.
다만 tail 표본 수와 이상값 처리 정책의 영향을 받으므로
quantile별 변화와 tail case 목록을 함께 확인해야 한다.
```

---

## SelectionRule 카탈로그

```text
selectionRule ANDERSON_DARLING_TEST_DEFAULT_USE
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

> Anderson-Darling Test 카탈로그는 "이 방법이 무엇인가"가 아니라, "어떤 상황에서 어떤 변종을 선택하고 어떤 주의사항과 함께 설명해야 하는가"를 구조화한다.
