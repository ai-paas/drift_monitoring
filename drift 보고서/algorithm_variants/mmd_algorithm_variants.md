# MMD 알고리즘 변종 목록

## 1. 목적

이 문서는 `MMD`를 하나의 고정된 detector로 보지 않고, drift monitoring에서 상황에 따라 선택해야 하는 **알고리즘 변종들의 family**로 정리한다.

핵심 목적은 다음이다.

```text
상황 조건 -> 적절한 MMD 계열 변종 -> 출력 metric -> 주의사항 -> LLM 보고서 설명
```

---

## 2. MMD의 위치

```text
methodFamily MMD
       ├─ algorithmVariant KERNEL_MMD_UNBIASED
       ├─ algorithmVariant KERNEL_MMD_BIASED
       ├─ algorithmVariant LINEAR_TIME_MMD
       └─ algorithmVariant STREAMING_MMD
```

`MMD`는 drift monitoring method 계열에 속한다. MMD 계열을 drift monitoring 문맥에서 입력 데이터와 운영 목적에 따라 선택 가능한 변종으로 정리한다.

---

## 3. 공통 개념

```text
methodFamily MMD
  purpose ->
    MMD 계열을 drift monitoring 문맥에서 입력 데이터와 운영 목적에 따라 선택 가능한 변종으로 정리한다.

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

## 변종: KERNEL_MMD_UNBIASED

Kernel 함수로 두 표본 분포의 평균 embedding 차이를 추정하되, 대각항을 제외해 편향을 줄인 MMD 변종이다. 표본 수가 충분하고 검정 통계의 통계적 성질을 중시할 때 사용한다.

- 사용 상황: reference/current 표본을 배치로 비교하고, kernel 기반 비모수 two-sample test를 엄밀하게 적용할 때 적합하다.
- 해석 방법: unbiased MMD가 커지면 두 기간의 feature 분포가 kernel 공간에서 멀어진 drift 후보로 본다.
- 주의점: 작은 표본에서는 추정값 변동이 크고 음수에 가까운 값이 나올 수 있으므로 permutation 또는 bootstrap 기준과 함께 본다.
- 보고서 문장 예시: "Unbiased kernel MMD가 기준 분포 대비 증가해 current feature 분포의 비모수 drift 후보가 확인되었다."

---

## 변종: KERNEL_MMD_BIASED

대각항을 포함해 항상 0 이상인 형태로 계산하는 biased MMD 변종이다. 점수의 안정성과 직관적인 거리 해석을 우선할 때 사용한다.

- 사용 상황: 운영 대시보드에서 MMD score를 지속적으로 추적하거나 음수 추정값 없이 거리 크기를 보고해야 할 때 적합하다.
- 해석 방법: biased MMD score가 reference 기준 threshold를 넘으면 current 분포가 기준 분포와 달라졌다는 후보 신호로 본다.
- 주의점: 이름처럼 finite sample bias가 있으므로 절대값 자체보다 동일 설정에서의 상대 변화와 threshold 초과 여부를 본다.
- 보고서 문장 예시: "Biased kernel MMD score가 상승해 동일 kernel 설정에서 current 분포가 기준보다 멀어진 것으로 해석된다."

---

## 변종: LINEAR_TIME_MMD

전체 pairwise kernel 계산 대신 표본 쌍을 제한해 선형 시간에 근사 MMD를 계산하는 변종이다. 대용량 데이터에서 계산 비용을 줄이는 데 초점을 둔다.

- 사용 상황: reference/current 표본 수가 커서 quadratic MMD 계산이 운영 시간 안에 끝나기 어려울 때 적합하다.
- 해석 방법: linear-time MMD가 반복적으로 높아지면 큰 표본에서도 분포 차이가 유지되는 drift 후보로 본다.
- 주의점: 근사 분산이 커질 수 있으므로 단일 window보다 여러 window 추세와 confidence interval을 함께 확인한다.
- 보고서 문장 예시: "Linear-time MMD가 여러 window에서 높게 유지되어 대용량 표본 조건에서도 분포 변화 후보가 관측되었다."

---

## 변종: STREAMING_MMD

Streaming window나 reservoir를 사용해 MMD를 계속 갱신하는 변종이다. 배치 검정보다 실시간 또는 준실시간 drift monitoring에 맞춰져 있다.

- 사용 상황: 데이터가 계속 유입되고 current window를 이동시키며 reference와 비교해야 할 때 적합하다.
- 해석 방법: streaming MMD가 control threshold를 넘거나 지속적으로 상승하면 최근 유입 분포가 기준과 달라지는 후보로 본다.
- 주의점: window 크기, reservoir 갱신 정책, reference refresh 정책이 결과에 직접 영향을 준다.
- 보고서 문장 예시: "Streaming MMD가 최근 window에서 기준선을 넘어 유입 데이터 분포의 변화 후보를 실시간으로 포착했다."

---

## SelectionRule 카탈로그

```text
selectionRule MMD_DEFAULT_USE
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

> MMD 카탈로그는 "이 방법이 무엇인가"가 아니라, "어떤 상황에서 어떤 변종을 선택하고 어떤 주의사항과 함께 설명해야 하는가"를 구조화한다.
