# Baumgartner-Weiss-Schindler Test 알고리즘 변종 목록

## 1. 목적

이 문서는 `Baumgartner-Weiss-Schindler Test`를 하나의 고정된 detector로 보지 않고, drift monitoring에서 상황에 따라 선택해야 하는 **알고리즘 변종들의 family**로 정리한다.

핵심 목적은 다음이다.

```text
상황 조건 -> 적절한 Baumgartner-Weiss-Schindler Test 계열 변종 -> 출력 metric -> 주의사항 -> LLM 보고서 설명
```

---

## 2. Baumgartner-Weiss-Schindler Test의 위치

```text
methodFamily BAUMGARTNER_WEISS_SCHINDLER_TEST
       ├─ algorithmVariant BWS_TWO_SAMPLE
       ├─ algorithmVariant BWS_EXACT_OR_ASYMPTOTIC
       └─ algorithmVariant BWS_RANK_BASED
```

`Baumgartner-Weiss-Schindler Test`는 drift monitoring method 계열에 속한다. Baumgartner-Weiss-Schindler Test 계열을 drift monitoring 문맥에서 입력 데이터와 운영 목적에 따라 선택 가능한 변종으로 정리한다.

---

## 3. 공통 개념

```text
methodFamily BAUMGARTNER_WEISS_SCHINDLER_TEST
  purpose ->
    Baumgartner-Weiss-Schindler Test 계열을 drift monitoring 문맥에서 입력 데이터와 운영 목적에 따라 선택 가능한 변종으로 정리한다.

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

## 변종: BWS_TWO_SAMPLE

`BWS_TWO_SAMPLE`은 기준 기간과 현재 기간의 두 표본이 같은 분포에서 왔는지 rank 기반으로 비교하는 변종이다. Baumgartner-Weiss-Schindler 검정은 두 표본의 순위 구조와 누적분포 차이를 이용해 위치, 산포, 분포 모양 변화를 함께 감지한다. drift monitoring에서는 reference/current 분포가 달라졌는지를 비모수 방식으로 screening하는 신호로 사용한다.

이 변종은 다음 상황에 적합하다.

- reference window와 current window의 연속형 또는 순서형 sample을 비교한다.
- 분포 형태를 강하게 가정하기 어렵고 비모수 검정이 필요하다.
- 평균 차이뿐 아니라 분포 모양이나 tail 차이도 함께 보고 싶다.
- feature, score, residual, KPI 값의 두 기간 분포 차이를 보고서용 보조 통계로 제시한다.

해석할 때는 BWS statistic과 p-value를 구분한다. Statistic이 클수록 두 표본의 rank 기반 분포 차이가 크다는 뜻이다. p-value가 유의수준보다 작으면 두 표본이 같은 분포에서 왔다는 가정과 맞지 않는다는 통계적 신호로 볼 수 있다. 다만 어느 값 구간에서 차이가 났는지는 statistic만으로 알기 어렵기 때문에 histogram, ECDF, quantile 변화와 함께 읽어야 한다.

주의할 점은 이 검정이 분포 차이의 존재를 말할 뿐 원인을 알려주지는 않는다는 것이다. sample size가 매우 크면 작은 차이도 유의해질 수 있고, sample size가 작으면 실제 차이를 놓칠 수 있다. reference/current의 수집 조건, 필터링, 결측 처리 방식이 다르면 그 차이가 drift 후보로 나타날 수 있다. p-value threshold는 운영 정책이나 calibration 기준으로 설명해야 하며 보편적 절대 기준처럼 쓰지 않는다.

보고서 문장 예시는 다음과 같다.

```text
기준 window와 현재 window의 score sample을 BWS_TWO_SAMPLE로 비교한 결과,
BWS statistic이 증가하고 p-value가 유의수준 아래로 내려갔다.
이는 두 기간의 rank 기반 분포가 같다는 가정과 맞지 않는 drift 후보 신호다.
다만 차이가 발생한 값 구간과 업무 원인은
ECDF, quantile 비교, segment별 분석으로 추가 확인해야 한다.
```

---

## 변종: BWS_EXACT_OR_ASYMPTOTIC

`BWS_EXACT_OR_ASYMPTOTIC`은 Baumgartner-Weiss-Schindler 검정에서 p-value를 계산할 때 표본 규모에 따라 exact 방식 또는 asymptotic 근사를 선택하는 변종이다. 검정의 핵심은 두 표본의 rank 기반 분포 차이를 보는 것이지만, 이 변종은 특히 p-value 산출 방식의 신뢰성과 계산 비용을 함께 관리하는 데 초점이 있다. drift monitoring에서는 작은 window와 큰 window가 섞여 있는 운영 환경에서 같은 검정 결과를 일관되게 설명하기 위해 사용한다.

이 변종은 다음 상황에 적합하다.

- reference/current window의 sample 수가 작아 exact p-value가 필요한 구간이 있다.
- sample 수가 커서 exact 계산이 비싸고 asymptotic 근사를 사용해야 한다.
- 동일한 feature나 score를 여러 window 크기로 반복 비교한다.
- p-value를 보고서에 제시해야 하므로 계산 방식의 전환 기준을 남겨야 한다.

해석할 때는 BWS statistic과 p-value 계산 방식을 함께 확인한다. Statistic이 클수록 두 기간의 rank 기반 분포 차이가 크다는 뜻이다. Exact p-value는 작은 표본에서 이산적인 순위 조합을 더 직접적으로 반영하고, asymptotic p-value는 표본이 충분히 클 때 근사 분포로 유의성을 평가한다. p-value가 유의수준보다 작으면 같은 분포라는 가정과 맞지 않는 drift 후보 신호로 해석하되, statistic 크기와 실제 분포 차이의 위치를 별도로 확인해야 한다.

주의할 점은 exact와 asymptotic 선택이 drift의 종류를 바꾸는 것이 아니라 유의성 계산 방식을 바꾼다는 것이다. 표본 수가 경계 근처에 있으면 계산 방식 전환 때문에 p-value가 약간 달라질 수 있다. 큰 표본에서는 매우 작은 차이도 유의해질 수 있으므로 효과 크기나 quantile 변화와 함께 보고해야 한다. threshold와 exact/asymptotic 전환 기준은 운영 정책 또는 라이브러리 설정으로 명시하는 것이 좋다.

보고서 문장 예시는 다음과 같다.

```text
기준 window와 현재 window의 feature 값을 BWS_EXACT_OR_ASYMPTOTIC으로 비교한 결과,
BWS statistic이 기준 대비 커지고 p-value가 유의수준 아래로 내려갔다.
이는 두 기간의 rank 기반 분포가 같다는 가정과 맞지 않는 drift 후보 신호다.
다만 p-value는 표본 수에 따라 exact 또는 asymptotic 방식으로 계산되므로,
window 크기와 실제 분포 차이는 quantile 비교로 함께 확인해야 한다.
```

---

## 변종: BWS_RANK_BASED

`BWS_RANK_BASED`는 원값의 절대 크기보다 두 표본을 합친 뒤의 순위 구조를 중심으로 분포 차이를 평가하는 변종이다. 평균만 비교하는 방식보다 위치 이동, 산포 변화, tail 변화에 민감할 수 있으며, 분포 형태를 정규분포로 가정하기 어려운 모니터링 신호에 유용하다. drift monitoring에서는 값의 스케일이 변하거나 이상치가 포함된 상황에서도 reference/current 차이를 비모수적으로 확인하는 보조 검정으로 사용한다.

이 변종은 다음 상황에 적합하다.

- 연속형 또는 순서형 feature, score, residual의 두 기간 분포를 비교한다.
- 값의 분포가 비대칭이거나 정규성 가정을 두기 어렵다.
- 평균 변화보다 순위 기반 누적분포 차이를 보고 싶다.
- 여러 feature를 같은 기준으로 screening해 drift 후보를 좁힌다.

해석할 때는 순위 기반 statistic이 커졌는지와 p-value가 유의수준보다 작은지를 함께 본다. Statistic이 크다는 것은 reference sample과 current sample의 순위가 서로 섞이지 않고 특정 구간에서 벌어졌다는 뜻으로 볼 수 있다. p-value가 작으면 두 표본이 같은 분포라는 가정과 맞지 않는다는 통계적 신호다. 어느 구간의 순위가 달라졌는지는 ECDF, box plot, 분위수 변화로 확인해야 한다.

주의할 점은 rank 기반 검정이 원값 차이의 업무적 크기를 직접 말해주지는 않는다는 것이다. 작은 수치 변화라도 표본 수가 많으면 통계적으로 유의할 수 있고, tie가 많은 이산형 값에서는 순위 처리 방식이 결과에 영향을 줄 수 있다. 결측값 제거, clipping, binning 같은 전처리가 reference/current에 동일하게 적용됐는지 확인해야 한다. 검정 결과만으로 모델 성능 저하나 원인 변수를 확정하지 않는다.

보고서 문장 예시는 다음과 같다.

```text
기준 기간과 현재 기간의 예측 score를 BWS_RANK_BASED로 비교한 결과,
순위 기반 BWS statistic이 상승하고 p-value가 유의수준보다 낮게 나타났다.
이는 두 기간의 score 분포 순위 구조가 달라졌다는 drift 후보 신호로 볼 수 있다.
다만 실제 영향 구간과 업무 원인은 ECDF, 분위수, segment별 비교로 추가 확인해야 한다.
```

---

## SelectionRule 카탈로그

```text
selectionRule BAUMGARTNER_WEISS_SCHINDLER_TEST_DEFAULT_USE
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

> Baumgartner-Weiss-Schindler Test 카탈로그는 "이 방법이 무엇인가"가 아니라, "어떤 상황에서 어떤 변종을 선택하고 어떤 주의사항과 함께 설명해야 하는가"를 구조화한다.
