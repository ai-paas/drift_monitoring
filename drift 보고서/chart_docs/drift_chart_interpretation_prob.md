# Probability 계열 차트 해석 가이드

이 문서는 CHART-PROB chart id의 이미지와 해석 방법을 정리한다.

## CHART-PROB-001: 오른쪽 값 구간의 확률 증가와 KL 기여

![CHART-PROB-001](../charts/output/CHART-PROB-001.png)

### 차트 목적

`CHART-PROB-001`은 기준 구간과 현재 구간의 확률분포 차이를 KL Divergence 관점에서 확인하기 위한 차트다. KL Divergence처럼 기준 확률분포에서 기대한 확률과 현재 확률분포가 얼마나 달라졌는지를 비대칭적으로 측정하는 방법에 적합하다.

### 제목

오른쪽 값 구간의 확률 증가와 KL 기여

### 현재 상황 요약

현재 구간의 확률분포는 기준 구간보다 오른쪽 값 bin에서 더 많은 확률을 가진다. 특히 `1.2`, `1.6`, `0.8` bin의 현재 확률이 기준 확률보다 높아 KL 기여 상위 구간으로 나타난다. 다만 현재 window의 `KL(q||p)`는 `0.023`으로 관리 기준 `0.070` 아래에 있고, 직전 window에서 `0.086`까지 올랐다가 낮아진 상태다. 따라서 이 예시는 오른쪽 값 구간의 확률 증가가 관측되지만 현재 시점만 보면 강한 drift 확정이 아니라 완화 중인 분포 변화 후보로 해석한다.

이 차트는 다음 질문에 답한다.

```text
1. 현재 확률분포가 기준 확률분포와 어느 bin에서 달라졌는가?
2. divergence가 시간에 따라 증가하고 있는가?
3. 어떤 bin이 KL 값을 가장 크게 키웠는가?
```

### 차트 구성

왼쪽 패널은 확률분포 overlay다.

- 파란 막대는 기준 구간의 bin별 확률이다.
- 붉은 막대는 현재 구간의 bin별 확률이다.
- 초록 점선은 KL 기여도가 큰 bin의 확률 차이를 강조한다.
- 기준 확률이 낮은 bin에서 현재 확률이 높아지면 KL 기여가 커질 수 있다.

오른쪽 위 패널은 divergence 추세다.

- x축은 window 순서다.
- y축은 window별 KL Divergence다.
- 노란 점선은 관리 기준 또는 운영 threshold 예시다.
- 특정 window에서만 높아졌는지, 지속적으로 높아지는지 구분한다.

오른쪽 아래 패널은 기여 bin 순위다.

- 막대 길이는 `q log(q / p)` 형태의 bin별 KL 기여도다.
- 붉은 막대는 가장 큰 기여 bin이다.
- 상위 기여 bin은 보고서에서 “어느 값 구간이 drift 신호를 만들었는가”를 설명할 때 사용한다.

상단 요약 카드에는 다음 값이 표시된다.

- `KL(q||p)`: 현재 분포 q를 기준 분포 p와 비교한 KL Divergence
- `역방향 KL`: 기준 분포 p를 현재 분포 q와 비교한 KL Divergence
- `최대 기여 bin`: KL 값을 가장 크게 키운 bin

### 해석 순서

먼저 왼쪽 확률분포 overlay에서 기준 확률과 현재 확률이 크게 다른 bin을 확인한다. KL은 비대칭 지표이므로 `현재에서 많이 나타난 구간`과 `기준에서 기대한 확률`의 차이를 함께 봐야 한다.

그 다음 오른쪽 아래 기여 bin 순위를 본다.

```text
상위 기여 bin이 한두 개에 집중된다
  -> 특정 값 구간의 확률 증가가 divergence를 키운 것이다.

여러 bin이 고르게 기여한다
  -> 전체 분포 형태가 넓게 바뀐 후보로 본다.

기준 확률이 매우 낮은 bin이 상위에 있다
  -> smoothing, zero count, sample size 영향을 추가 확인한다.
```

마지막으로 divergence 추세를 확인한다. 현재 값이 작더라도 직전 window에서 급증했거나 threshold를 넘은 이력이 있으면 일시적 이상인지, 회복 중인지, 반복되는 패턴인지 확인해야 한다.

### Drift 후보 판단 기준

KL 값이 관리 기준을 넘고 기여 상위 bin의 sample count가 충분하면 확률분포 drift 후보로 해석한다. 기준 확률이 매우 낮은 bin은 smoothing과 zero count 영향을 먼저 확인한다.

### 패널별 확인

확률분포 Overlay:

- 기준 분포는 `-0.4` bin에서 `0.161`로 가장 높고, 현재 분포는 같은 bin에서 `0.130`으로 낮아진다.
- 반대로 오른쪽 구간의 현재 확률은 `0.8` bin `0.115`, `1.2` bin `0.096`, `1.6` bin `0.066`으로 기준 확률 `0.091`, `0.062`, `0.040`보다 높다.
- 이 패턴은 현재 구간에서 큰 값 쪽 관측 비중이 늘어났다는 뜻이다.

Divergence 추세:

- window별 KL은 `0.028 -> 0.034 -> 0.041 -> 0.038 -> 0.052 -> 0.071 -> 0.086 -> 0.023` 순서로 움직인다.
- 관리 기준은 `0.070`이고, window 6~7에서는 기준을 넘지만 현재 window에서는 `0.023`으로 기준 아래에 있다.
- 따라서 현재 값 하나만 보면 drift가 지속 중이라고 단정하기보다, 직전 상승 이후 완화 또는 회복 여부를 추가 window에서 확인해야 한다.

기여 Bin 순위:

- KL 기여도는 `1.2` bin이 `0.042`로 가장 크고, 그 다음 `1.6` bin `0.033`, `0.8` bin `0.027`, `2.0` bin `0.019` 순서다.
- 상위 기여 bin이 모두 오른쪽 값 구간에 몰려 있으므로, divergence의 원인은 전체적으로 무작위한 변화가 아니라 오른쪽 tail 쪽 확률 증가에 가깝다.
- 단, 기준 확률이 낮은 오른쪽 tail에서는 sample count와 smoothing 영향을 함께 확인해야 한다.

### 이 예시 차트의 해석

이 예시에서는 `KL(q||p)`가 `0.023`, 역방향 KL이 `0.062`, 최대 기여 bin이 `1.2`로 표시되어 있다. 현재 분포는 기준 분포보다 오른쪽 bin의 확률이 높아졌고, 특히 `1.2`, `1.6`, `0.8` 부근이 KL 기여 상위 구간으로 나타난다.

추세 패널에서는 직전 window에서 divergence가 관리 기준을 넘었다가 현재 window에서는 낮아진 모습이다. 따라서 이 예시는 오른쪽 값 구간의 확률 증가가 관측되지만, 현재 window만 보면 drift 강도는 관리 기준 아래로 완화된 사례로 해석할 수 있다.

보고서 문장 예시는 다음과 같다.

```text
기준 구간과 현재 구간을 KL Divergence 관점에서 비교한 결과,
KL(q||p)는 0.023, 역방향 KL은 0.062로 나타났다.
현재 구간은 기준 구간보다 1.2 이상 오른쪽 bin의 확률이 높아졌으며,
KL 기여도는 1.2 bin에서 가장 크게 나타났다.
다만 현재 window의 KL 값은 관리 기준 아래에 있으므로,
직전 window의 일시적 상승 이후 완화 중인 분포 변화 후보로 해석한다.
```

### 금지해야 할 해석

이 차트만으로 다음을 단정하지 않는다.

```text
금지 1
  - KL 값 하나만으로 drift 원인을 확정한다.

금지 2
  - KL(q||p)와 KL(p||q)를 같은 의미로 해석한다.

금지 3
  - zero count 또는 smoothing 영향을 확인하지 않고 rare bin 변화를 과대해석한다.

금지 4
  - 확률분포 차이가 곧바로 모델 성능 저하를 의미한다고 말한다.
```

KL Divergence는 비대칭 지표이며, binning과 smoothing 설정에 민감하다. 특히 기준 확률이 0에 가까운 구간에서는 작은 count 차이도 크게 보일 수 있다.

### 추가 확인 항목

KL 관점에서 확률분포 차이가 보이면 다음을 추가 확인한다.

- binning 기준, smoothing 값, zero count 처리 방식
- 기여 상위 bin의 sample count가 충분한지
- 같은 feature의 JS Distance, Hellinger Distance, PSI 결과
- 현재 window만의 일시적 spike인지 반복되는 패턴인지
- 기여 bin의 segment, source, 시간대 구성 변화
- label 확보 후 성능 지표, calibration, error rate 변화

### 적합한 사용 대상

이 chart는 다음 method variant에 적합하다.

- `KL Divergence / DISCRETE_KL_DIVERGENCE`
- `KL Divergence / HISTOGRAM_KL_DIVERGENCE`
- `KL Divergence / SMOOTHED_KL_DIVERGENCE`
- `KL Divergence / SYMMETRIZED_KL`

다만 symmetrized KL 변종에서는 `KL(q||p)`와 `KL(p||q)`를 모두 표시하고, 두 방향의 차이가 큰 경우 비대칭 원인을 별도로 설명해야 한다.

## CHART-PROB-002: 탐색 감소와 구매 증가로 보는 카테고리 비중 변화

![CHART-PROB-002](../charts/output/CHART-PROB-002.png)

### 차트 목적

`CHART-PROB-002`는 기준 구간과 현재 구간의 확률분포 차이를 bounded symmetric distance 관점에서 확인하기 위한 차트다. Jensen-Shannon Distance와 Hellinger Distance처럼 값 범위가 제한되어 있고 두 분포의 순서를 바꿔도 같은 의미로 해석하기 쉬운 방법에 적합하다.

### 제목

탐색 감소와 구매 증가로 보는 카테고리 비중 변화

### 현재 상황 요약

현재 구간에서는 `검색` 비중이 `0.24`에서 `0.17`로 줄고, `구매` 비중이 `0.18`에서 `0.25`로 늘어난다. `JS Distance`는 `0.121`, `Hellinger`는 `0.101`로 표시되며, 두 값 모두 관리 기준 `0.18` 아래에 있다. 따라서 이 예시는 category mix 변화가 관측되지만 현재 window에서는 강한 drift라기보다 탐색 단계 감소와 구매 단계 증가가 남아 있는 완화 구간으로 해석한다.

이 차트는 다음 질문에 답한다.

```text
1. 두 확률분포가 전체적으로 얼마나 멀어졌는가?
2. bounded distance가 시간에 따라 증가하고 있는가?
3. 어떤 category의 확률이 늘고 줄어 drift 신호를 만들었는가?
```

### 차트 구성

왼쪽 패널은 확률분포 overlay다.

- 파란 막대는 기준 구간의 category별 확률이다.
- 붉은 막대는 현재 구간의 category별 확률이다.
- 옅은 초록 영역은 두 분포가 겹치는 확률 질량을 보조적으로 보여준다.
- 기준 대비 현재 확률이 크게 달라진 category는 delta bar에서 다시 확인한다.

오른쪽 위 패널은 bounded 거리 추세다.

- 초록 선은 JS Distance 추세다.
- 붉은 선은 Hellinger Distance 추세다.
- y축은 0에서 1 사이 bounded distance다.
- 노란 점선은 관리 기준 또는 운영 threshold 예시다.

오른쪽 아래 패널은 category delta다.

- x축은 `현재 확률 - 기준 확률`이다.
- 오른쪽 초록 막대는 현재 확률이 증가한 category다.
- 왼쪽 노란 막대는 현재 확률이 감소한 category다.
- delta가 큰 category는 drift 설명 문장의 핵심 후보가 된다.

상단 요약 카드에는 다음 값이 표시된다.

- `JS Distance`: Jensen-Shannon divergence를 bounded distance 형태로 변환한 값
- `Hellinger`: 두 확률분포의 제곱근 공간 거리
- `최대 Delta`: 기준 대비 현재 확률 변화가 가장 큰 category

### 해석 순서

먼저 상단 요약의 JS Distance와 Hellinger 값을 확인한다.

```text
값이 0에 가깝다
  -> 두 확률분포가 유사하다.

값이 커진다
  -> 두 확률분포의 겹침이 줄고 있다.

JS와 Hellinger가 같은 방향으로 증가한다
  -> 확률분포 변화 신호가 비교적 일관적이다.
```

그 다음 오른쪽 아래 delta bar를 본다. bounded distance는 전체 차이를 요약하지만, 어떤 category가 늘고 줄었는지는 delta를 봐야 설명할 수 있다.

마지막으로 왼쪽 분포 overlay에서 delta가 큰 category의 실제 확률 수준을 확인한다. 작은 category의 상대 변화와 큰 category의 절대 변화는 운영 해석이 다를 수 있다.

### Drift 후보 판단 기준

JS/Hellinger 같은 bounded distance가 관리 기준을 넘고 delta 상위 category가 명확하면 category probability drift 후보로 해석한다. category 정의나 mapping 변경으로 설명되는지 확인한다.

### 패널별 확인

확률분포 Overlay:

- 기준 구간에서는 `검색` `0.24`, `상세` `0.22`처럼 탐색 단계 비중이 가장 크다.
- 현재 구간에서는 `검색`이 `0.17`로 줄고, `구매`가 `0.18`에서 `0.25`로 늘어난다.
- `장바구니`는 `0.15 -> 0.18`, `환불`은 `0.05 -> 0.08`로 증가하지만, `리뷰`는 `0.06`으로 변하지 않는다.

Bounded 거리 추세:

- JS Distance는 `0.08 -> 0.10 -> 0.11 -> 0.13 -> 0.16 -> 0.18 -> 0.121` 순서로 움직인다.
- Hellinger는 `0.07 -> 0.09 -> 0.10 -> 0.12 -> 0.15 -> 0.17 -> 0.101` 순서로 움직인다.
- 직전 window에서는 JS가 관리 기준 `0.18`에 닿았지만, 현재 window에서는 JS `0.121`, Hellinger `0.101`로 기준 아래에 있다.

Category Delta:

- 가장 큰 증가는 `구매 +0.07`이고, 가장 큰 감소는 `검색 -0.07`이다.
- `상세 -0.03`, `문의 -0.03` 감소와 `장바구니 +0.03`, `환불 +0.03` 증가도 함께 나타난다.
- delta가 탐색 단계 감소와 전환 단계 증가로 나뉘므로, 단일 category 이상이라기보다 category mix 이동 후보로 읽는다.

### 이 예시 차트의 해석

이 예시에서는 JS Distance가 `0.121`, Hellinger Distance가 `0.101`, 최대 delta가 `구매 +0.07`로 표시되어 있다. 두 bounded distance 모두 0에 가까운 편이지만, 최근 window에서 관리 기준에 근접했던 이력이 있고 현재도 기준 대비 category mix 변화가 남아 있다.

Category delta를 보면 `구매`와 `장바구니`, `환불`의 현재 확률이 증가했고, `검색`, `상세`, `문의`의 확률은 감소했다. 이는 사용자의 행동 단계 분포가 탐색 단계에서 구매/전환 단계 쪽으로 일부 이동한 후보로 해석할 수 있다.

보고서 문장 예시는 다음과 같다.

```text
기준 구간과 현재 구간의 category 확률분포를 JS/Hellinger 관점에서 비교한 결과,
JS Distance는 0.121, Hellinger Distance는 0.101로 나타났다.
현재 구간에서는 구매 category 확률이 기준 대비 0.07 증가했고,
검색과 상세 category 확률은 감소했다.
이는 전체 category mix가 탐색 중심에서 구매/전환 단계 쪽으로 일부 이동한 후보로 해석할 수 있다.
```

### 금지해야 할 해석

이 차트만으로 다음을 단정하지 않는다.

```text
금지 1
  - category mix 변화가 곧바로 성능 저하를 의미한다고 말한다.

금지 2
  - JS Distance와 Hellinger Distance가 같다고 해석한다.

금지 3
  - delta가 큰 category를 원인으로 확정한다.

금지 4
  - label 없이 concept drift가 발생했다고 확정한다.
```

JS/Hellinger 계열은 KL보다 안정적으로 해석하기 쉽지만, 원인 분석은 category 정의, 수집 정책, segment 구성 변화와 함께 확인해야 한다.

### 추가 확인 항목

Bounded 확률 거리가 커지면 다음을 추가 확인한다.

- category 정의, mapping, unknown 처리 변경 여부
- delta가 큰 category의 sample count와 segment 구성
- 같은 feature의 KL Divergence, PSI, Total Variation Distance 결과
- window별 변화가 일시적 spike인지 지속적 추세인지
- category 변화가 모델 입력 feature나 score 분포에 미친 영향
- label 확보 후 성능 지표, calibration, error rate 변화

### 적합한 사용 대상

이 chart는 다음 method variant에 적합하다.

- `Jensen-Shannon Distance / JENSEN_SHANNON_DIVERGENCE`
- `Jensen-Shannon Distance / JENSEN_SHANNON_DISTANCE`
- `Jensen-Shannon Distance / MULTICLASS_PROBABILITY_JS`
- `Jensen-Shannon Distance / TEXT_TOPIC_JS`
- `Hellinger Distance / DISCRETE_HELLINGER_DISTANCE`
- `Hellinger Distance / HISTOGRAM_HELLINGER_DISTANCE`
- `Hellinger Distance / CATEGORICAL_HELLINGER_DISTANCE`

## CHART-PROB-003: 오른쪽 이동으로 줄어든 기준·현재 분포 겹침

![CHART-PROB-003](../charts/output/CHART-PROB-003.png)

### 차트 목적

`CHART-PROB-003`은 기준 구간과 현재 구간의 확률분포가 얼마나 겹치는지, 그리고 그 overlap 감소가 얼마나 큰지를 확인하기 위한 차트다. Bhattacharyya Distance처럼 두 분포의 유사도 또는 겹침 감소를 중심으로 해석하는 방법에 적합하다.

### 제목

오른쪽 이동으로 줄어든 기준·현재 분포 겹침

### 현재 상황 요약

현재 분포는 기준 분포보다 오른쪽 bin의 확률이 커지고 왼쪽 bin의 확률이 줄어든다. `1.5` bin은 `0.06`에서 `0.115`로 늘고, `1` bin은 `0.11`에서 `0.16`으로 늘며, 반대로 `-1` bin은 `0.13`에서 `0.08`로 줄어든다. 두 분포의 overlap 계수는 `0.820`, Bhattacharyya distance는 `0.023`이고 현재 값은 관리 기준 `0.030` 아래에 있다. 따라서 이 예시는 오른쪽 이동으로 겹침이 줄었지만, 현재 window에서는 강한 분리 확정보다 완만한 overlap 감소 후보로 해석한다.

이 차트는 다음 질문에 답한다.

```text
1. 기준 분포와 현재 분포가 어느 정도 겹치는가?
2. overlap 감소가 시간에 따라 커지고 있는가?
3. 어느 bin에서 기준/현재 확률 차이가 가장 커졌는가?
```

### 차트 구성

왼쪽 패널은 확률분포 overlay다.

- 파란 막대는 기준 구간의 bin별 확률이다.
- 붉은 막대는 현재 구간의 bin별 확률이다.
- 초록 막대는 두 분포가 공통으로 갖는 overlap 영역이다.
- overlap 영역이 작아질수록 두 분포가 덜 겹친다.

오른쪽 위 패널은 overlap 계수다.

- 초록 영역은 겹치는 확률 질량 비율이다.
- 노란 영역은 겹치지 않는 확률 질량 비율이다.
- Bhattacharyya coefficient는 두 확률분포의 유사도를 제곱근 확률 공간에서 요약한다.

오른쪽 아래 패널은 거리 추세다.

- x축은 window 순서다.
- y축은 Bhattacharyya distance다.
- 노란 선이 상승하면 분포 overlap이 줄어드는 방향의 drift 신호가 강화되는 것이다.
- 초록 점선은 관리 기준 또는 운영 threshold 예시다.

상단 요약 카드에는 다음 값이 표시된다.

- `Bhattacharyya`: Bhattacharyya distance
- `Overlap 계수`: bin별 `min(기준 확률, 현재 확률)`의 합
- `BC 계수`: Bhattacharyya coefficient

### 해석 순서

먼저 overlap 계수를 본다.

```text
overlap 계수가 1에 가깝다
  -> 두 확률분포가 많이 겹친다.

overlap 계수가 낮아진다
  -> 두 확률분포의 공통 영역이 줄어든다.

Bhattacharyya distance가 커진다
  -> 분포 유사도가 낮아지고 분리 신호가 커진다.
```

그 다음 왼쪽 overlay에서 overlap이 줄어든 위치를 확인한다. 기준 분포의 peak와 현재 분포의 peak가 서로 어긋나면 overlap이 줄고 distance가 커진다.

마지막으로 거리 추세를 본다. 현재 distance가 작아도 최근 window에서 상승하고 있다면, 분포 분리가 진행 중인지 추가 확인한다.

### Drift 후보 판단 기준

Bhattacharyya distance가 관리 기준을 넘거나 overlap 계수 감소가 지속되면 분포 분리 drift 후보로 해석한다. overlap 감소가 특정 bin에 집중되는지 함께 확인한다.

### 패널별 확인

확률분포 Overlay:

- 기준 분포는 `0` bin `0.19`, `-0.5` bin `0.17`, `0.5` bin `0.16` 주변에 많이 겹친다.
- 현재 분포는 `1` bin `0.16`, `1.5` bin `0.115`, `2` bin `0.07`로 오른쪽 구간 확률이 커진다.
- 가장 큰 차이는 `1.5` bin `+0.055`, `-1` bin `-0.050`, `1` bin `+0.050`에서 나타난다.

Overlap 계수:

- overlap 계수는 `0.820`으로 두 분포의 공통 확률 질량이 82.0% 남아 있음을 뜻한다.
- Bhattacharyya coefficient는 `0.977`로 아직 유사도가 높지만, 1에서 조금 낮아진 상태다.
- 확률 차이 최대 bin은 `1.5`이며, 이 bin의 현재 확률 증가가 overlap 감소를 가장 크게 만든다.

거리 추세:

- Bhattacharyya distance는 `0.010 -> 0.014 -> 0.018 -> 0.020 -> 0.026 -> 0.031 -> 0.023` 순서로 움직인다.
- 직전 window에서는 관리 기준 `0.030`을 넘었지만 현재 window에서는 `0.023`으로 내려온다.
- 따라서 분포 분리 신호가 한때 강해졌으나 현재는 기준 아래로 완화된 상태인지 추가 window로 확인해야 한다.

### 이 예시 차트의 해석

이 예시에서는 Bhattacharyya distance가 `0.023`, overlap 계수가 `0.820`, BC 계수가 `0.977`로 표시되어 있다. 두 분포는 아직 상당 부분 겹치지만, 현재 분포가 기준 분포보다 오른쪽 bin 쪽으로 일부 이동하면서 overlap이 줄어든 모습이다.

거리 추세 패널에서는 최근 window에서 Bhattacharyya distance가 관리 기준 근처까지 상승했다가 현재 window에서 소폭 낮아졌다. 따라서 이 예시는 분포 분리 신호가 관측되지만, 아직 강한 분리보다는 완만한 overlap 감소 후보로 해석할 수 있다.

보고서 문장 예시는 다음과 같다.

```text
기준 구간과 현재 구간의 확률분포를 Bhattacharyya 관점에서 비교한 결과,
Bhattacharyya distance는 0.023, overlap 계수는 0.820으로 나타났다.
현재 분포는 기준 분포보다 오른쪽 bin 쪽 확률이 증가하면서 overlap이 일부 감소했다.
다만 두 분포의 겹침이 아직 82.0% 수준으로 남아 있으므로,
완만한 분포 분리 후보로 해석한다.
```

### 금지해야 할 해석

이 차트만으로 다음을 단정하지 않는다.

```text
금지 1
  - overlap 감소가 곧바로 모델 성능 저하를 의미한다고 말한다.

금지 2
  - overlap 계수와 Bhattacharyya coefficient를 같은 값으로 해석한다.

금지 3
  - binning 또는 smoothing 영향을 확인하지 않고 분포 분리를 확정한다.

금지 4
  - 단일 feature의 overlap 감소로 전체 데이터 drift를 확정한다.
```

Bhattacharyya 계열은 overlap 감소를 직관적으로 보여주지만, binning 기준과 sample size, feature scale에 따라 값이 달라질 수 있다.

### 추가 확인 항목

Bhattacharyya distance가 커지면 다음을 추가 확인한다.

- binning 기준, smoothing, zero count 처리 방식
- overlap 감소가 큰 bin의 sample count와 segment 구성
- 같은 feature의 Hellinger Distance, JS Distance, KL Divergence 결과
- window별 추세가 일시적 변화인지 지속적 분리인지
- 기준/현재 peak 위치가 데이터 수집 정책 변경과 연결되는지
- label 확보 후 성능 지표, calibration, error rate 변화

### 적합한 사용 대상

이 chart는 다음 method variant에 적합하다.

- `Bhattacharyya Distance / DISCRETE_BHATTACHARYYA_DISTANCE`
- `Bhattacharyya Distance / GAUSSIAN_BHATTACHARYYA_DISTANCE`
- `Bhattacharyya Distance / HISTOGRAM_BHATTACHARYYA_DISTANCE`


