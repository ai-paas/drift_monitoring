# Energy Distance 알고리즘 변종 목록

## 1. 목적

이 문서는 `Energy Distance`를 하나의 고정된 detector로 보지 않고, drift monitoring에서 상황에 따라 선택해야 하는 **알고리즘 변종들의 family**로 정리한다.

핵심 목적은 다음이다.

```text
상황 조건 -> 적절한 Energy Distance 계열 변종 -> 출력 metric -> 주의사항 -> LLM 보고서 설명
```

---

## 2. Energy Distance의 위치

```text
methodFamily ENERGY_DISTANCE
       ├─ algorithmVariant UNIVARIATE_ENERGY_DISTANCE
       ├─ algorithmVariant MULTIVARIATE_ENERGY_DISTANCE
       └─ algorithmVariant ENERGY_DISTANCE_PERMUTATION_TEST
```

`Energy Distance`는 drift monitoring method 계열에 속한다. Energy Distance 계열을 drift monitoring 문맥에서 입력 데이터와 운영 목적에 따라 선택 가능한 변종으로 정리한다.

---

## 3. 공통 개념

```text
methodFamily ENERGY_DISTANCE
  purpose ->
    Energy Distance 계열을 drift monitoring 문맥에서 입력 데이터와 운영 목적에 따라 선택 가능한 변종으로 정리한다.

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

## 변종: UNIVARIATE_ENERGY_DISTANCE

`UNIVARIATE_ENERGY_DISTANCE`는 하나의 수치형 지표에 대해 reference 분포와 current 분포 사이의 거리를 계산하는 Energy Distance 변종이다. 평균 차이뿐 아니라 분포의 폭, 꼬리, 비대칭 변화까지 하나의 distance 값으로 요약해 drift 후보를 선별한다. 출력 distance는 차이의 크기를 나타내는 신호이며, p-value나 alarm이 있으면 통계적 유의성 또는 운영 기준 통과 여부를 함께 읽는다.

사용 상황:
- 단일 feature, score, latency, 금액처럼 한 개 수치 지표의 분포 변화를 추적할 때
- 평균은 비슷하지만 분산, 꼬리, 극단값 비중이 달라졌는지 보고 싶을 때
- 여러 feature를 각각 독립적으로 screening한 뒤 변화가 큰 지표를 보고서에 올릴 때

해석 방법:
- distance 값이 클수록 reference/current 단변량 분포가 더 멀어졌다는 뜻이다.
- p-value가 제공되면 관측된 distance가 우연한 표본 변동으로 보기 어려운지 판단하는 유의성 지표로 해석한다.
- alarm은 사전에 정한 threshold나 calibration 기준을 넘었는지 나타내며, 절대적인 drift 판정 기준으로 일반화하지 않는다.
- distance가 커진 지표는 histogram, quantile, 평균/분산 변화와 함께 보면 어떤 구간이 달라졌는지 설명할 수 있다.

주의점:
- distance는 분포 차이의 존재와 크기를 요약하지만, 변화 원인을 직접 알려주지는 않는다.
- 단위와 scale의 영향을 받으므로 feature별 distance를 비교할 때는 표준화나 calibration 기준을 확인해야 한다.
- 표본 수가 작거나 극단값이 많은 지표에서는 distance가 불안정할 수 있어 robust summary를 함께 확인한다.

보고서 문장 예시:

```text
단일 수치 지표를 UNIVARIATE_ENERGY_DISTANCE로 비교한 결과,
Energy distance가 기준 window 대비 증가해 reference/current 분포 간 거리가 커졌다.
이는 해당 지표의 값 분포가 달라졌을 가능성을 나타내는 drift 후보 신호다.
다만 원인은 distance만으로 확정할 수 없으므로, quantile 변화와 데이터 수집 조건을 함께 확인해야 한다.
```

---

## 변종: MULTIVARIATE_ENERGY_DISTANCE

`MULTIVARIATE_ENERGY_DISTANCE`는 여러 feature를 하나의 벡터로 묶어 reference/current의 결합분포 차이를 측정하는 변종이다. 개별 feature만 보면 작아 보이는 변화라도 feature 조합이나 상관 구조가 달라졌을 때 drift 후보로 잡아낼 수 있다. 출력 distance는 다변량 공간에서 두 표본 구름이 얼마나 달라졌는지를 요약한다.

사용 상황:
- 여러 입력 feature가 함께 움직이며 모델 입력 분포를 구성할 때
- feature 간 관계, 조합 패턴, segment 구조 변화가 중요한 모니터링 대상일 때
- 단변량 검정에서 뚜렷한 변화가 없지만 모델 입력 전체의 상태 변화를 확인하고 싶을 때

해석 방법:
- distance 값이 클수록 reference/current의 다변량 결합분포가 더 멀어졌다는 의미다.
- p-value가 있으면 관측된 다변량 distance가 우연한 표본 변동으로 설명되기 어려운지 판단한다.
- alarm은 전체 feature 묶음에서 변화 후보가 기준을 넘었다는 신호이며, 어떤 feature가 원인인지는 별도 분석이 필요하다.
- 후속 해석에서는 feature별 contribution, 단변량 distance, PCA/embedding 시각화 등을 함께 사용해 변화 위치를 좁힌다.

주의점:
- feature scale이 다르면 큰 단위의 feature가 distance를 지배할 수 있으므로 정규화 기준을 확인해야 한다.
- 차원이 높고 표본 수가 부족하면 distance 추정이 불안정하거나 해석력이 떨어질 수 있다.
- 다변량 alarm은 모델 성능 저하를 직접 의미하지 않으므로 label 기반 성능 지표와 분리해 설명한다.

보고서 문장 예시:

```text
주요 입력 feature 벡터를 MULTIVARIATE_ENERGY_DISTANCE로 비교한 결과,
다변량 Energy distance가 운영 기준보다 커져 결합분포 변화 후보가 관측됐다.
이는 feature 조합 또는 상관 구조가 reference 기간과 달라졌을 가능성을 시사한다.
다만 변화 위치와 업무 영향은 feature별 분해와 성능 지표를 함께 확인해야 한다.
```

---

## 변종: ENERGY_DISTANCE_PERMUTATION_TEST

`ENERGY_DISTANCE_PERMUTATION_TEST`는 관측된 Energy Distance가 우연한 표본 배정으로도 나올 수 있는지 permutation으로 평가하는 검정형 변종이다. distance 값 자체는 분포 차이의 크기를 요약하고, permutation p-value는 그 차이가 통계적으로 이례적인지 판단하는 기준을 제공한다. 분포 가정에 덜 의존해 reference/current 비교의 유의성을 확인하고 싶을 때 유용하다.

사용 상황:
- 표본 분포 형태를 가정하기 어렵고, 비모수적으로 유의성을 확인하고 싶을 때
- 단변량 또는 다변량 Energy Distance 결과에 p-value를 붙여 보고서 근거를 강화할 때
- threshold를 고정하기보다 현재 표본 구성에서 관측 distance가 얼마나 이례적인지 평가할 때

해석 방법:
- observed distance가 클수록 실제 reference/current 라벨로 나눴을 때 두 표본의 분포 차이가 크다는 뜻이다.
- permutation p-value는 라벨을 무작위로 섞었을 때 observed distance 이상이 나오는 비율로 해석한다.
- p-value가 작으면 두 기간의 분포 차이가 우연한 표본 분할만으로 설명되기 어렵다는 근거가 강하다.
- alarm은 permutation p-value 또는 observed distance가 운영 기준을 통과했는지 나타내며, distance 크기와 유의성을 분리해 보고한다.

주의점:
- permutation 횟수가 적으면 p-value 해상도가 낮아지고 결과 변동이 커질 수 있다.
- 계산 비용이 커질 수 있어 feature 수, 표본 수, 반복 횟수에 맞는 운영 한계를 정해야 한다.
- reference/current 표본이 서로 독립적이고 동일한 수집 규칙을 따른다는 전제가 깨지면 permutation p-value 해석이 약해진다.

보고서 문장 예시:

```text
reference/current 표본을 ENERGY_DISTANCE_PERMUTATION_TEST로 평가한 결과,
observed Energy distance와 permutation p-value가 분포 변화 후보를 지지했다.
이는 무작위 표본 배정으로는 현재 차이가 잘 설명되지 않는다는 통계적 신호로 볼 수 있다.
다만 permutation 반복 수와 표본 수에 따라 p-value 안정성이 달라지므로, 반복 설정과 수집 조건을 함께 보고해야 한다.
```

---

## SelectionRule 카탈로그

```text
selectionRule ENERGY_DISTANCE_DEFAULT_USE
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

> Energy Distance 카탈로그는 "이 방법이 무엇인가"가 아니라, "어떤 상황에서 어떤 변종을 선택하고 어떤 주의사항과 함께 설명해야 하는가"를 구조화한다.
