# Annotation Drift Chart Interpretation

## CHART-ANNOT-001

![CHART-ANNOT-001](../charts/output/CHART-ANNOT-001.png)

### 차트 목적

CHART-ANNOT-001의 현재 상황은 one-sided 변종이 `upper` 방향을 선언한 상태에서 current 곡선이 baseline보다 커지는 구간만 drift 후보로 볼 수 있는지 판단하는 사례다. 요약 metric은 direction `upper`, D+ gap `+0.11`, one-sided p-value `0.018`을 보여준다. 따라서 증가 방향 차이는 drift candidate로 볼 수 있지만, lower gap `-0.08`은 반대 방향 신호라서 이 upper one-sided 검정의 drift 증거로 계산하지 않는다.

이 chart는 one-sided, upper, lower 변종에서 drift 해석 방향을 명시하는 보조 annotation을 설명한다. 화면은 세 개의 읽기 영역으로 나뉜다. 좌측 큰 패널은 baseline/current 누적 곡선의 어느 구간이 upper 방향 증거이고 어느 구간이 lower 방향 증거인지 보여주며, 우측 상단은 upper/greater 검정과 lower/less 검정을 별도 판단 카드로 비교한다. 우측 하단은 이 방향성 annotation을 어떤 one-sided detector variant에 붙여 읽어야 하는지 method matrix로 정리한다.

One-sided 검정은 변화 크기뿐 아니라 대립가설의 방향이 맞는지가 중요하다. 같은 절대 차이라도 upper 방향 검정에서는 증가 방향의 차이만, lower 방향 검정에서는 감소 방향의 차이만 drift 증거로 해석한다.

예시 데이터에서는 direction이 `upper`로 선언되어 있고, 요약 metric은 D+ gap `+0.11`, one-sided p-value `0.018`이다. 따라서 좌측 패널의 upper 영역과 우측 상단의 upper 판단 카드를 먼저 읽어야 한다. lower gap `-0.08`은 반대 방향 신호를 설명하는 참고 정보이지, upper one-sided 변종의 drift 증거로 계산하지 않는다.

이 차트는 다음 질문에 답한다.

```text
1. 변종이 upper/greater 또는 lower/less 중 어느 방향을 선언했는가?
2. 관측된 차이가 선언된 one-sided 방향과 일치하는가?
3. 반대 방향 차이를 drift 증거로 잘못 해석하지 않았는가?
```

### 차트 구성

CHART-ANNOT-001은 세 영역으로 구성된다.

```text
좌측
  - baseline/current 누적 곡선
  - upper direction marker
  - lower direction marker
  - 반대 방향은 not counted로 표시

우측 상단
  - upper/greater one-sided 판단 카드
  - lower/less one-sided 판단 카드

우측 하단
  - KS, Fisher, Mann-Whitney U, CUSUM, EWMA/GMA 변종 적용 matrix
```

상단 요약 영역에는 선언된 direction, D+ gap, one-sided p-value를 표시한다.

### 해석 순서

CHART-ANNOT-001을 읽을 때는 먼저 변종 이름이나 설정에서 one-sided 방향을 확인한다.

```text
upper 또는 greater
  -> 현재 구간이 기준 구간보다 커지는 방향만 drift 증거로 본다.

lower 또는 less
  -> 현재 구간이 기준 구간보다 작아지는 방향만 drift 증거로 본다.

two-sided
  -> 이 annotation은 보조 설명이 아니며 양방향 차트를 사용한다.
```

그 다음 좌측 overlay에서 표시된 upper/lower marker가 실제로 대립가설 방향과 맞는지 확인한다.

마지막으로 우측 판단 카드에서 p-value와 방향이 함께 만족되는지 확인한다. p-value가 작아도 방향이 반대이면 해당 one-sided 검정의 drift 후보로 보지 않는다.

패널별로는 다음처럼 읽는다.

- **One-sided Direction Overlay**: baseline/current 누적 곡선을 비교해 index 12 부근에서 current가 baseline보다 높은 upper gap `+0.11`을 확인한다. lower 쪽에는 `-0.08` 차이가 있지만, 이 예시의 선언 방향은 upper이므로 lower 영역은 반대 방향 참고 신호다.
- **Upper vs Lower Test**: upper/greater 카드는 `D+ = +0.11`, `p=0.018`로 drift candidate를 표시한다. lower/less 카드는 `D- = -0.08`, `p=0.214`로 not counted이므로 같은 차트 안에서도 방향이 맞는 카드만 판단에 사용한다.
- **Variant Usage Matrix**: KS, Fisher, MWU, CUSUM, EWMA/GMA처럼 one-sided 방향을 선언하는 변종에 이 annotation을 붙여 읽는다. Two-sided 변종은 upper/lower 한쪽만 고르는 해석을 하지 않는다.

### Drift 후보 판단 기준

CHART-ANNOT-001에서는 선언된 one-sided 방향과 관측된 차이 방향이 일치하고, 해당 방향의 statistic 또는 p-value가 임계값을 넘으면 방향성 drift 후보로 해석한다.

단, 이 차트는 독립적인 drift 검정 결과가 아니라 기존 family 차트에 붙는 해석 annotation이다. 따라서 원본 차트의 표본 정의, statistic, p-value, control limit과 함께 확인해야 한다.

### 이 예시 차트의 해석

CHART-ANNOT-001 예시에서는 direction이 `upper`, D+ gap이 `+0.11`, one-sided p-value가 `0.018`로 표시되어 있다. 좌측 overlay에서 current 곡선이 upper marker 구간에서 baseline보다 높은 방향으로 벌어진다.

우측 상단 카드에서는 upper/greater 방향이 drift candidate로 표시되고, lower/less 방향은 p-value가 충분하지 않아 not counted로 표시된다. 따라서 이 예시는 upper one-sided 변종에서 증가 방향 drift 후보를 설명하는 annotation으로 해석할 수 있다.

보고서 문장 예시는 다음과 같다.

```text
해당 변종은 upper one-sided 대립가설을 사용한다.
관측된 차이는 current가 baseline보다 커지는 방향으로 나타났고,
D+ gap은 +0.11, one-sided p-value는 0.018이다.
따라서 증가 방향 drift 후보로 해석하며,
반대 방향 차이는 이 검정의 drift 증거로 계산하지 않는다.
```

### 금지해야 할 해석

CHART-ANNOT-001만으로 다음을 단정하지 않는다.

```text
금지 1
  - one-sided 결과를 two-sided 유의성으로 해석한다.

금지 2
  - 방향이 반대인 차이를 p-value만 보고 drift 후보로 해석한다.

금지 3
  - upper/lower marker를 원본 statistic 정의와 무관하게 붙인다.

금지 4
  - annotation만 보고 원본 chart family의 해석을 생략한다.
```

방향성 annotation은 기존 chart의 해석을 보완한다. 원본 statistic이 무엇을 측정하는지 먼저 확인해야 한다.

### 추가 확인 항목

CHART-ANNOT-001처럼 one-sided 방향성 annotation을 사용할 때는 다음을 추가 확인한다.

- variant 이름의 `ONE_SIDED`, `GREATER`, `LESS`, `UPPER`, `LOWER` 의미
- statistic 부호와 차이 방향의 정의
- p-value가 one-sided 기준인지 two-sided 기준인지 여부
- threshold marker가 원본 detector의 control limit과 일치하는지 여부
- 반대 방향 변화가 별도 위험 신호인지 여부
- 보고서 문장에서 증가/감소 방향을 명시했는지 여부

### 적합한 사용 대상

CHART-ANNOT-001은 다음 method variant에 적합하다.

- `KS Test / TWO_SAMPLE_KS_ONE_SIDED_GREATER`
- `KS Test / TWO_SAMPLE_KS_ONE_SIDED_LESS`
- `Fisher's Exact Test / ONE_SIDED_FISHER_EXACT`
- `Mann-Whitney U / Wilcoxon Rank Sum Test / MANN_WHITNEY_ONE_SIDED`
- `CUSUM / ONE_SIDED_UPPER_CUSUM`
- `CUSUM / ONE_SIDED_LOWER_CUSUM`
- `EWMA / EWMA_ONE_SIDED`
- `Geometric Moving Average / GMA_ONE_SIDED`

## CHART-ANNOT-002

![CHART-ANNOT-002](../charts/output/CHART-ANNOT-002.png)

### 차트 목적

현재 상황은 계산량을 줄이기 위해 exact/reference score 대신 approximate, sliced, quantile 계산을 사용하는 사례다. 요약 metric은 approximation error `0.03`, projection count `128`, quantile error max `0.022`를 보여준다. 좌측에서는 approximate score가 exact/reference score를 대체로 따라가지만 threshold `0.42` 근처에서는 오차가 판단을 흔들 수 있고, 우측 하단에서는 중앙 quantile error는 허용 범위 안이지만 tail error `0.041`이 target `0.03`을 넘는다.

이 chart는 approximate, sliced, quantile 변종에서 drift score와 함께 보고해야 하는 근사 오차 정보를 설명한다.

근사 기반 detector는 계산량을 줄이기 위해 projection, histogram approximation, quantile approximation을 사용한다. 이 경우 score가 threshold를 넘었는지뿐 아니라 approximation error, projection count, quantile error가 판단을 흔들 정도로 큰지도 함께 확인해야 한다.

이 차트는 다음 질문에 답한다.

```text
1. 근사 score가 reference 또는 exact score와 얼마나 차이 나는가?
2. sliced projection 수가 충분해 score 변동이 안정화되었는가?
3. quantile error가 threshold 근처 판단을 뒤집을 수 있을 만큼 큰가?
```

### 차트 구성

이 chart는 세 영역으로 구성된다.

```text
좌측
  - exact/reference drift score line
  - approximate/quantile drift score line
  - approximation error band
  - drift threshold line

우측 상단
  - projection count별 score spread
  - tolerance line

우측 하단
  - q25, q50, q75, tail quantile error
  - target error line
```

상단 요약 영역에는 approximation error, projection count, quantile error max를 표시한다.

### 해석 순서

먼저 좌측 error band에서 approximate score가 exact/reference score를 안정적으로 따라가는지 확인한다.

```text
approximation error가 작다
  -> 원본 drift score 판단을 신뢰할 수 있다.

threshold 근처에서 approximation error가 크다
  -> drift 여부가 뒤집힐 수 있으므로 exact 계산이나 projection 증가가 필요하다.

approximate score만 있고 error 정보가 없다
  -> 근사 변종의 판단 신뢰도를 설명하기 어렵다.
```

그 다음 우측 상단 projection stability에서 projection count가 증가할수록 spread가 tolerance 아래로 내려가는지 확인한다.

마지막으로 우측 하단 quantile error에서 중앙 quantile뿐 아니라 tail quantile 오차가 허용 범위를 넘는지 확인한다.

패널별로는 다음처럼 읽는다.

- **Approximation Error Band**: exact/reference line과 approximate/quantile line이 time window 전반에서 비슷하게 움직이는지 본다. Drift threshold `0.42` 근처에서는 approximation band가 판단 경계와 겹치므로, score가 threshold 바로 근처라면 exact 계산으로 재확인해야 한다.
- **Projection Stability**: projection count가 `16`, `32`일 때는 score spread가 tolerance `0.04`보다 크지만, `128` 이상에서는 tolerance 아래로 내려가 안정화된다. 따라서 이 예시에서는 `128+ projections stable` 구간부터 sliced approximation을 더 신뢰할 수 있다.
- **Quantile Error Detail**: q25, q50, q75 error는 target `0.03` 안에 있지만 tail error는 `0.041`로 target을 넘는다. 평균적인 분포 판단은 가능해도 tail risk나 extreme quantile 결론은 추가 projection 또는 exact 계산으로 재검증해야 한다.

### Drift 후보 판단 기준

근사 score가 원본 chart의 threshold를 넘고, approximation error와 quantile error가 허용 범위 안에 있으며, projection count 증가에 따라 score spread가 안정화되면 approximate/sliced/quantile 기반 drift 후보로 해석한다.

단, score가 threshold에 매우 가깝거나 tail quantile error가 큰 경우에는 근사 오차 때문에 판단이 뒤집힐 수 있다. 이때는 projection 수를 늘리거나 exact/reference 계산으로 재검증해야 한다.

### 이 예시 차트의 해석

이 예시에서는 approximation error가 `0.03`, projection count가 `128`, quantile error max가 `0.022`로 표시되어 있다. 좌측 차트에서 approximate line은 exact/reference line을 대체로 따라가며 error band가 drift threshold 주변을 표시한다.

우측 상단에서는 projection count가 128 이상일 때 spread가 tolerance 아래로 내려가 안정화된다. 우측 하단에서는 q25, q50, q75 error가 target 안에 있지만 tail error는 target을 넘는다. 따라서 이 예시는 전반 score 판단은 신뢰 가능하지만 tail 기반 해석은 추가 확인이 필요한 근사 annotation 사례로 해석할 수 있다.

보고서 문장 예시는 다음과 같다.

```text
근사 기반 drift score는 reference score와 평균 0.03 수준의 차이를 보였다.
Sliced projection count가 128 이상일 때 score spread는 tolerance 아래로 안정화되었다.
다만 tail quantile error가 target을 초과하므로,
tail-sensitive 결론은 projection 증가 또는 exact 계산으로 재검증해야 한다.
```

### 금지해야 할 해석

이 차트만으로 다음을 단정하지 않는다.

```text
금지 1
  - approximate score만 보고 exact score와 동일한 신뢰도로 해석한다.

금지 2
  - projection count가 낮은 결과를 안정화된 sliced distance로 해석한다.

금지 3
  - 평균 quantile error가 작다는 이유로 tail error를 무시한다.

금지 4
  - threshold 근처의 근사 오차 가능성을 보고서에서 생략한다.
```

근사/투영 annotation은 drift score의 계산 신뢰도를 설명한다. 원본 chart의 statistic 해석과 별개로 오차 관리를 함께 보고해야 한다.

### 추가 확인 항목

근사/투영 annotation을 사용할 때는 다음을 추가 확인한다.

- exact/reference 계산 가능 여부
- approximation error의 정의와 허용 기준
- projection count, random seed, 반복 횟수
- quantile bin 수와 tail quantile error
- threshold 근처 window의 재계산 결과
- histogram binning 또는 sketch 알고리즘 설정
- score 변동이 보고서 결론을 뒤집는지 여부

### 적합한 사용 대상

이 chart는 다음 method variant에 적합하다.

- `KS Test / TWO_SAMPLE_KS_APPROX_QUANTILE`
- `Wasserstein Distance / SLICED_WASSERSTEIN_EMBEDDING`
- `Wasserstein Distance / WASSERSTEIN_APPROX_HISTOGRAM`
