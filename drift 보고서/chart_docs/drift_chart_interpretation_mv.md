# Multivariate Chart Interpretation Guide

## CHART-MV-001: 기준·현재 구간의 다변량 분포 분리

![CHART-MV-001](../charts/output/CHART-MV-001.png)

### 제목

기준·현재 구간의 다변량 분포 분리

### 차트 목적

이 chart는 기준 구간과 현재 구간의 다변량 분포가 달라졌는지 설명한다.

Energy Distance 계열은 두 표본 집단 내부 거리와 집단 간 거리 구조를 비교해 분포 차이를 측정한다. 단일 feature의 평균이나 분산 변화가 작아도 여러 feature가 함께 움직이면 energy distance가 커질 수 있으므로, 이 chart는 다변량 covariate shift를 설명하는 데 적합하다.

이 차트는 다음 질문에 답한다.

```text
1. 기준 구간과 현재 구간의 sample이 projection 공간에서 분리되는가?
2. Energy distance가 최근 window에서 증가하거나 관리 기준을 넘는가?
3. 관측 statistic이 permutation null distribution의 상위 꼬리에 있는가?
```

### 차트 구성

이 chart는 세 영역으로 구성된다.

```text
좌측
  - 기준 구간과 현재 구간의 multivariate projection scatter
  - 각 집단의 대략적인 분포 영역
  - projection 중심 간 gap 표시

우측 상단
  - window별 Energy distance 추세
  - 운영 관리 기준 또는 threshold

우측 하단
  - permutation null distribution histogram
  - 관측 Energy distance statistic
  - permutation p-value
```

상단 요약 영역에는 Energy distance, permutation p-value, projection gap을 표시한다.

### 현재 상황 요약

이 예시에서는 현재 구간 sample이 기준 구간보다 projection 공간의 우상단으로 이동해 두 집단의 중심 간 gap이 `1.35`로 벌어진다. Energy distance는 마지막 window에서 `0.73`까지 올라 관리 기준 `0.45`를 넘고, permutation p-value는 `0.012`로 표시된다. 따라서 이 화면은 단일 feature 하나의 변화보다 여러 feature가 함께 움직여 기준 구간과 현재 구간의 결합 분포가 분리된 다변량 drift 후보 상황을 보여준다.

### 해석 순서

먼저 좌측 projection scatter에서 기준 sample과 현재 sample이 같은 공간에 섞이는지, 또는 특정 방향으로 분리되는지 확인한다.

```text
두 집단이 대부분 겹친다
  -> 다변량 분포 차이 신호가 약하다.

현재 집단이 특정 방향으로 이동했다
  -> 여러 feature가 함께 이동했을 가능성을 확인한다.

현재 집단이 여러 cluster로 갈라졌다
  -> segment mix 변화 또는 신규 population 유입을 의심한다.
```

그 다음 우측 상단의 window 추세를 본다. Energy distance가 일회성으로만 튀는지, 최근 window에서 반복적으로 관리 기준을 넘는지 구분한다.

마지막으로 우측 하단의 permutation null distribution을 확인한다. 관측 statistic이 귀무분포의 상위 꼬리에 있고 p-value가 운영 기준보다 작으면, 우연 변동보다 큰 다변량 분포 차이 후보로 해석한다.

### Drift 후보 판단 기준

Energy distance가 관리 기준을 넘고 상승 추세가 지속되며, permutation p-value가 기준보다 작고, projection scatter에서 기준/현재 sample의 분리가 확인되면 다변량 drift 후보로 해석한다.

단, projection scatter는 시각화를 위한 저차원 요약이므로 projection에서 겹친다고 해서 고차원 차이가 없다고 단정하지 않는다. 반대로 projection에서 분리되어 보여도 scale, outlier, embedding 방법의 영향을 함께 확인해야 한다.

### 패널별 확인

좌측 Projection Scatter에서는 기준 sample이 대체로 왼쪽 아래 영역에, 현재 sample이 오른쪽 위 영역에 배치된다. 기준 중심은 약 `(-0.45, -0.55)`, 현재 중심은 약 `(1.45, 1.45)` 방향으로 표시되어 있고, 화면 상단 요약의 projection gap은 `1.35`다. 두 집단이 완전히 겹치지 않고 현재 구간이 한 방향으로 이동해 있으므로 여러 feature 조합의 위치 변화가 distance 증가와 같은 방향인지 확인한다.

우측 상단 Energy Distance 추세에서는 window 값이 `0.18 -> 0.21 -> 0.25 -> 0.24 -> 0.31 -> 0.38 -> 0.47 -> 0.56 -> 0.64 -> 0.73`으로 움직인다. 관리 기준은 `0.45`이며, 7번째 window의 `0.47`부터 기준선을 넘은 뒤 마지막 window `0.73`까지 계속 커진다. 일회성 spike라기보다 최근 구간에서 거리 신호가 강화되는 흐름이다.

우측 하단 Permutation Null에서는 귀무분포 막대가 주로 `0.20~0.35` 주변에 몰려 있고, 관측 Energy distance `0.73`은 오른쪽 꼬리 바깥쪽에 세로선으로 표시된다. p-value `0.012`는 무작위 permutation으로 이 정도의 분리 신호가 나올 가능성이 작다는 보조 근거다.

### 이 예시 차트의 해석

이 예시에서는 Energy distance가 `0.73`, permutation p-value가 `0.012`, projection gap이 `1.35`로 표시되어 있다. 좌측 projection scatter에서 현재 sample은 기준 sample보다 우상단으로 이동하며 두 집단의 중심이 분리되어 있다.

우측 상단의 추세에서는 7번째 window부터 Energy distance가 관리 기준 `0.45`를 넘고, 이후 `0.47`, `0.56`, `0.64`, `0.73`으로 증가한다. 우측 하단의 permutation null distribution에서는 관측 statistic `0.73`이 귀무분포의 상위 꼬리 바깥쪽에 위치한다. 따라서 이 예시는 여러 feature가 함께 움직인 다변량 drift 후보로 해석할 수 있다.

보고서 문장 예시는 다음과 같다.

```text
기준 구간과 현재 구간의 다변량 분포를 Energy Distance로 비교한 결과,
관측 distance는 0.73, permutation p-value는 0.012로 나타났다.
Energy distance는 7번째 window부터 관리 기준 0.45를 넘고 마지막 window에서 0.73까지 증가했다.
Projection scatter에서도 현재 sample이 기준 sample보다 우상단으로 이동해 projection gap 1.35가 관측된다.
이는 단일 feature보다 여러 feature의 결합 분포가 변한 다변량 drift 후보로 해석할 수 있다.
```

### 금지해야 할 해석

이 차트만으로 다음을 단정하지 않는다.

```text
금지 1
  - 다변량 drift가 있다는 이유만으로 어떤 feature가 원인인지 단정한다.

금지 2
  - projection scatter의 2차원 분리만으로 고차원 분포 차이를 확정한다.

금지 3
  - scale 보정 여부를 확인하지 않고 feature 간 거리 기반 결과를 해석한다.

금지 4
  - p-value가 작다는 이유만으로 모델 성능 저하를 확정한다.
```

Energy distance는 거리 기반 방법이므로 feature scaling, embedding, outlier 처리에 민감할 수 있다. 원인 분석에는 feature별 drift chart와 segment 분석이 필요하다.

### 추가 확인 항목

다변량 drift 후보가 나타나면 다음을 추가 확인한다.

- feature scaling, normalization, embedding 생성 방식 변경 여부
- 단일 feature drift detector와의 합의 여부
- projection 방법과 random seed에 따른 시각화 안정성
- outlier 또는 신규 cluster가 distance를 주도하는지 여부
- segment, source, 시간대별 sample 구성 변화
- label 확보 후 성능 지표, calibration, error rate 변화

### 적합한 사용 대상

이 chart는 다음 method variant에 적합하다.

- `Energy Distance / UNIVARIATE_ENERGY_DISTANCE`
- `Energy Distance / MULTIVARIATE_ENERGY_DISTANCE`
- `Energy Distance / ENERGY_DISTANCE_PERMUTATION_TEST`

## CHART-MV-002: 커널 MMD로 본 임베딩 분포 변화

![CHART-MV-002](../charts/output/CHART-MV-002.png)

### 제목

커널 MMD로 본 임베딩 분포 변화

### 차트 목적

이 chart는 kernel MMD를 이용해 기준 구간과 현재 구간의 고차원 분포가 달라졌는지 설명한다.

MMD는 두 표본 집단을 kernel mean embedding으로 변환한 뒤 그 차이를 측정한다. 따라서 원본 feature 공간이나 embedding 공간에서 평균, 분산, cluster 구조가 복합적으로 달라질 때 유용하다. 특히 RBF kernel 같은 비선형 kernel을 사용하면 단순 선형 평균 차이보다 더 복잡한 분포 변화를 포착할 수 있다.

이 차트는 다음 질문에 답한다.

```text
1. 기준 구간과 현재 구간의 embedding 분포가 분리되는가?
2. MMD score가 최근 window에서 증가하거나 관리 기준을 넘는가?
3. 관측 MMD score가 permutation null distribution의 상위 꼬리에 있는가?
```

### 차트 구성

이 chart는 세 영역으로 구성된다.

```text
좌측
  - 기준 구간과 현재 구간의 embedding projection scatter
  - kernel bandwidth 영향 범위를 암시하는 분포 영역
  - 두 집단의 kernel mean embedding 차이 방향

우측 상단
  - window별 MMD score 추세
  - 운영 관리 기준 또는 threshold

우측 하단
  - permutation null distribution histogram
  - 관측 MMD score
  - permutation p-value
```

상단 요약 영역에는 MMD score, permutation p-value, kernel bandwidth를 표시한다.

### 현재 상황 요약

이 예시에서는 현재 구간 sample이 기준 구간보다 embedding projection의 우상단으로 이동한다. 기준 kernel 영역의 중심은 약 `(-0.4, 0.25)`, 현재 kernel 영역의 중심은 약 `(1.55, 1.75)`로 표시되어 두 집단의 중심과 cluster 영역이 부분적으로 분리된다. MMD score는 마지막 window에서 `0.36`까지 증가해 관리 기준 `0.18`을 넘고, permutation p-value는 `0.008`, kernel bandwidth는 `1.20`이다. 따라서 이 화면은 기준·현재 구간의 embedding 분포가 kernel mean embedding 관점에서 달라진 고차원 drift 후보 상황을 보여준다.

### 해석 순서

먼저 좌측 embedding projection에서 기준 sample과 현재 sample이 섞이는지, 또는 중심/cluster 구조가 달라지는지 확인한다.

```text
두 집단이 넓게 겹친다
  -> kernel 기반 분포 차이 신호가 약할 수 있다.

현재 집단의 중심이 이동했다
  -> embedding 평균 또는 주요 feature 조합이 이동했을 수 있다.

현재 집단의 cluster 구조가 달라졌다
  -> segment mix 변화, 신규 topic, 신규 population 유입을 의심한다.
```

그 다음 우측 상단의 MMD score 추세를 본다. 최근 window에서 기준선을 반복적으로 넘으면 일시적 fluctuation보다 지속적 고차원 분포 변화 후보로 본다.

마지막으로 permutation null distribution을 확인한다. 관측 MMD score가 귀무분포의 상위 꼬리에 있고 p-value가 기준보다 작으면, label shuffle으로 설명되기 어려운 분포 차이 후보로 해석한다.

### Drift 후보 판단 기준

MMD score가 관리 기준을 넘고 상승 추세가 지속되며, permutation p-value가 기준보다 작고, embedding projection에서 기준/현재 sample의 중심 또는 cluster 구조 차이가 확인되면 kernel 기반 다변량 drift 후보로 해석한다.

단, MMD는 kernel 종류와 bandwidth에 민감하다. bandwidth가 너무 작으면 local noise에 민감하고, 너무 크면 세부 cluster 차이가 희석될 수 있으므로 kernel 설정을 함께 보고해야 한다.

### 패널별 확인

좌측 Embedding Projection Scatter에서는 기준 sample이 주로 왼쪽 아래와 중앙 영역에, 현재 sample이 오른쪽 위 영역에 배치된다. 기준 kernel 영역 중심은 약 `(-0.4, 0.25)`, 현재 kernel 영역 중심은 약 `(1.55, 1.75)`이며, 두 영역은 일부 겹치지만 현재 구간의 중심과 상단 cluster가 기준 구간보다 오른쪽 위로 이동해 있다. 이 이동 방향이 우측 MMD score 증가와 같은 방향인지 확인한다.

우측 상단 MMD Score 추세에서는 window 값이 `0.05 -> 0.06 -> 0.07 -> 0.08 -> 0.10 -> 0.14 -> 0.19 -> 0.25 -> 0.31 -> 0.36`으로 증가한다. 관리 기준은 `0.18`이고, 7번째 window의 `0.19`부터 기준선을 넘은 뒤 마지막 window `0.36`까지 계속 커진다. 일회성 spike보다 최근 window에서 kernel 기반 분포 차이 신호가 강화되는 흐름이다.

우측 하단 Permutation Null에서는 귀무분포 막대가 주로 `0.08~0.12` 부근에 몰려 있고, 관측 MMD score `0.36`은 표시 범위의 오른쪽 바깥쪽에 세로선으로 나타난다. p-value `0.008`은 permutation으로 이 정도의 MMD 차이가 나올 가능성이 작다는 보조 근거이며, bandwidth `1.20` 설정에서 해석해야 한다.

### 이 예시 차트의 해석

이 예시에서는 MMD score가 `0.36`, permutation p-value가 `0.008`, kernel bandwidth가 `1.20`으로 표시되어 있다. 좌측 embedding projection에서는 현재 sample이 기준 sample보다 우상단으로 이동했고, 기준 중심 약 `(-0.4, 0.25)`에서 현재 중심 약 `(1.55, 1.75)` 방향으로 kernel 영역이 분리되어 있다.

우측 상단의 추세에서는 7번째 window부터 MMD score가 관리 기준 `0.18`을 넘고, 이후 `0.19`, `0.25`, `0.31`, `0.36`으로 증가한다. 우측 하단의 permutation null distribution에서는 관측 MMD score `0.36`이 `0.08~0.12` 부근의 귀무분포에서 멀리 떨어진 오른쪽에 위치한다. 따라서 이 예시는 kernel mean embedding 차이가 커진 고차원 drift 후보로 해석할 수 있다.

보고서 문장 예시는 다음과 같다.

```text
기준 구간과 현재 구간의 embedding 분포를 Kernel MMD로 비교한 결과,
관측 MMD score는 0.36, permutation p-value는 0.008로 나타났다.
MMD score는 7번째 window부터 관리 기준 0.18을 넘고 마지막 window에서 0.36까지 증가했다.
Embedding projection에서도 기준 중심 약 (-0.4, 0.25)에서 현재 중심 약 (1.55, 1.75) 방향으로 이동했다.
이는 kernel 기반 고차원 분포 drift 후보로 해석할 수 있다.
```

### 금지해야 할 해석

이 차트만으로 다음을 단정하지 않는다.

```text
금지 1
  - MMD score가 크다는 이유만으로 어떤 feature가 원인인지 단정한다.

금지 2
  - kernel bandwidth 설정을 확인하지 않고 drift 강도를 절대 비교한다.

금지 3
  - projection scatter의 2차원 분리만으로 고차원 전체 구조를 확정한다.

금지 4
  - p-value가 작다는 이유만으로 모델 성능 저하를 확정한다.
```

MMD는 고차원 분포 차이를 요약하는 detector이므로, 원인 설명에는 feature별 detector, embedding 차원별 분석, segment 분석이 필요하다.

### 추가 확인 항목

MMD drift 후보가 나타나면 다음을 추가 확인한다.

- kernel 종류와 bandwidth 설정
- biased/unbiased estimator 및 linear-time approximation 사용 여부
- embedding 모델 또는 feature normalization 변경 여부
- projection 방법과 random seed에 따른 시각화 안정성
- 특정 cluster, segment, source가 MMD score를 주도하는지 여부
- label 확보 후 성능 지표, calibration, confidence 변화

### 적합한 사용 대상

이 chart는 다음 method variant에 적합하다.

- `MMD / KERNEL_MMD_UNBIASED`
- `MMD / KERNEL_MMD_BIASED`
- `MMD / LINEAR_TIME_MMD`
- `MMD / STREAMING_MMD`

## CHART-MV-003: 밀도 차이로 본 신규 구간 유입과 기존 구간 감소

![CHART-MV-003](../charts/output/CHART-MV-003.png)

### 제목

밀도 차이로 본 신규 구간 유입과 기존 구간 감소

### 차트 목적

이 chart는 Least-Squares Density Difference 관점에서 기준 구간과 현재 구간의 밀도 차이가 어느 영역에서 발생하는지 설명한다.

LSDD는 기준 밀도와 현재 밀도의 차이를 직접 추정하므로, 단순히 두 집단이 다르다는 신호뿐 아니라 "어디에서 현재 sample 비중이 늘었고 어디에서 줄었는가"를 보여주는 데 적합하다. 따라서 drift 원인을 segment, embedding cluster, feature subspace 수준으로 좁혀야 할 때 유용하다.

이 차트는 다음 질문에 답한다.

```text
1. 현재 밀도가 기준보다 증가한 embedding 영역은 어디인가?
2. 현재 밀도가 기준보다 감소한 embedding 영역은 어디인가?
3. LSDD score가 최근 window에서 증가하고 permutation 기준을 만족하는가?
```

### 차트 구성

이 chart는 세 영역으로 구성된다.

```text
좌측
  - 기준 대비 현재 밀도 차이 heatmap
  - 붉은 영역: 현재 밀도 증가
  - 푸른 영역: 현재 밀도 감소

우측 상단
  - window별 LSDD score 추세
  - 운영 관리 기준 또는 threshold

우측 하단
  - permutation null distribution histogram
  - 관측 LSDD score
  - permutation p-value
```

상단 요약 영역에는 LSDD score, permutation p-value, 최대 밀도 delta를 표시한다.

### 현재 상황 요약

이 예시에서는 기준 구간보다 현재 구간의 sample 비중이 embedding 우상단 영역에서 늘고, 좌하단 영역에서는 줄어든다. LSDD score는 마지막 window에서 `0.34`까지 증가해 관리 기준 `0.17`을 넘고, permutation p-value는 `0.010`으로 표시된다. 좌측 heatmap의 최대 밀도 증가는 `+0.48`, 최대 감소는 `-0.30`이므로, 단순한 전체 이동보다 특정 embedding 영역의 유입 증가와 기존 영역의 감소가 함께 나타난 density difference drift 후보 상황으로 읽는다.

### 해석 순서

먼저 좌측 heatmap에서 밀도 증가 영역과 감소 영역을 확인한다.

```text
붉은 영역이 특정 cluster에 집중된다
  -> 해당 cluster 또는 segment 유입 증가를 의심한다.

푸른 영역이 기준 cluster 주변에 집중된다
  -> 기존 population 일부가 감소했을 수 있다.

증가/감소 영역이 넓게 퍼져 있다
  -> 전체 embedding 구조 변화 또는 preprocessing 변화를 점검한다.
```

그 다음 우측 상단의 LSDD score 추세를 본다. 최근 window에서 기준선을 반복적으로 넘고 상승하면 일시적 sample fluctuation보다 지속적 밀도 차이 후보로 본다.

마지막으로 permutation null distribution을 확인한다. 관측 LSDD score가 귀무분포의 상위 꼬리에 있고 p-value가 기준보다 작으면, random split으로 설명되기 어려운 밀도 차이 후보로 해석한다.

### Drift 후보 판단 기준

LSDD score가 관리 기준을 넘고 상승 추세가 지속되며, permutation p-value가 기준보다 작고, heatmap에서 현재 밀도 증가/감소 영역이 구조적으로 나타나면 density difference drift 후보로 해석한다.

단, density difference는 전처리, embedding scale, bandwidth 또는 basis 설정에 민감할 수 있다. heatmap 해석 전에는 동일한 feature/embedding 생성 방식과 sample weighting 여부를 확인해야 한다.

### 패널별 확인

좌측 Density Difference Heatmap에서는 x축 embedding 1이 `-2`에서 `3`, y축 embedding 2가 `-1`에서 `3`까지 표시된다. 우상단 영역은 붉은색으로 나타나며 현재 밀도 증가가 크고, 가장 큰 증가는 embedding 1 `2`, embedding 2 `2` 부근의 `+0.48`이다. 반대로 좌하단 기준 영역은 푸른색으로 표시되고, embedding 1 `-1`, embedding 2 `0` 부근에서 `-0.30`까지 내려간다. 이 패턴은 현재 sample이 우상단 영역에 더 많이 들어오고 기존 좌하단 영역의 비중은 줄었다는 뜻이다.

우측 상단 LSDD Score 추세에서는 window 값이 `0.04 -> 0.05 -> 0.06 -> 0.07 -> 0.09 -> 0.13 -> 0.18 -> 0.24 -> 0.30 -> 0.34`로 증가한다. 관리 기준은 `0.17`이며, 7번째 window의 `0.18`부터 기준선을 넘은 뒤 마지막 window `0.34`까지 계속 커진다. 일회성 변동보다 최근 구간에서 밀도 차이 신호가 강화되는 흐름이다.

우측 하단 Permutation Null에서는 귀무분포 막대가 주로 `0.07~0.13` 부근에 몰려 있고, 관측 LSDD score `0.34`는 표시 범위의 오른쪽 끝에 세로선으로 나타난다. p-value `0.010`은 random split으로 이 정도의 밀도 차이가 나올 가능성이 작다는 보조 근거다.

### 이 예시 차트의 해석

이 예시에서는 LSDD score가 `0.34`, permutation p-value가 `0.010`, 최대 밀도 delta가 `+0.48`로 표시되어 있다. 좌측 heatmap에서는 우상단 embedding 영역에서 현재 밀도가 증가하고, 좌하단 기준 영역에서는 현재 밀도가 감소한다. 특히 증가 영역의 최대값은 `+0.48`, 감소 영역의 최저값은 `-0.30`으로 나타나 증가와 감소가 한쪽 방향으로 동시에 형성되어 있다.

우측 상단 추세에서는 7번째 window부터 LSDD score가 관리 기준 `0.17`을 넘고, 이후 `0.18`, `0.24`, `0.30`, `0.34`로 증가한다. 우측 하단 permutation null distribution에서는 관측 LSDD score `0.34`가 `0.07~0.13` 부근의 귀무분포에서 멀리 떨어진 오른쪽에 위치한다. 따라서 이 예시는 기존 population 일부가 줄고 신규 또는 증가 segment가 우상단 영역에 집중된 density difference drift 후보로 해석할 수 있다.

보고서 문장 예시는 다음과 같다.

```text
기준 구간과 현재 구간의 밀도 차이를 LSDD로 비교한 결과,
관측 LSDD score는 0.34, permutation p-value는 0.010으로 나타났다.
Density difference heatmap에서는 우상단 embedding 영역의 현재 밀도 증가가 최대 +0.48,
좌하단 영역의 현재 밀도 감소가 최저 -0.30으로 함께 관측된다.
LSDD score는 7번째 window부터 관리 기준 0.17을 넘고 마지막 window에서 0.34까지 증가했다.
이는 특정 embedding cluster의 유입 증가와 기존 cluster 비중 감소가 동반된 drift 후보로 해석할 수 있다.
```

### 금지해야 할 해석

이 차트만으로 다음을 단정하지 않는다.

```text
금지 1
  - heatmap의 붉은 영역을 곧바로 특정 업무 segment로 단정한다.

금지 2
  - preprocessing 또는 embedding scale 변경 가능성을 배제한다.

금지 3
  - density 추정 설정을 확인하지 않고 작은 국소 영역 차이를 과해석한다.

금지 4
  - p-value가 작다는 이유만으로 모델 성능 저하를 확정한다.
```

LSDD는 밀도 차이 위치를 설명하는 데 강점이 있지만, 해당 영역이 어떤 원천 feature나 segment를 의미하는지는 별도 drill-down 분석이 필요하다.

### 추가 확인 항목

LSDD drift 후보가 나타나면 다음을 추가 확인한다.

- embedding 또는 feature preprocessing 변경 여부
- density difference 추정의 bandwidth, basis, regularization 설정
- 붉은 영역과 푸른 영역에 해당하는 sample의 segment/source/time 분포
- MMD, Energy Distance, feature별 drift chart와의 합의 여부
- sample weighting 또는 class imbalance 변화 여부
- label 확보 후 성능 지표, calibration, confidence 변화

### 적합한 사용 대상

이 chart는 다음 method variant에 적합하다.

- `LSDD / LEAST_SQUARES_DENSITY_DIFFERENCE`
- `LSDD / LSDD_WITH_PREPROCESSING`
- `LSDD / PERMUTATION_LSDD`

## CHART-MV-004: 다변량 평균 벡터의 기준 범위 이탈

![CHART-MV-004](../charts/output/CHART-MV-004.png)

### 제목

다변량 평균 벡터의 기준 범위 이탈

### 차트 목적

이 chart는 Hotelling T2 관점에서 여러 feature의 평균 벡터가 기준 구간 대비 이동했는지 설명한다.

Hotelling T2는 단일 feature 평균 차이가 아니라 feature 간 공분산 구조를 고려한 다변량 평균 shift를 측정한다. 따라서 여러 feature가 함께 움직이거나, 개별 feature 변화는 작지만 결합 방향의 이동이 큰 경우를 탐지하는 데 적합하다.

이 차트는 다음 질문에 답한다.

```text
1. 현재 window의 평균 벡터가 기준 평균 중심에서 얼마나 멀어졌는가?
2. T2 statistic이 control limit을 넘는 window가 반복되는가?
3. 평균 shift에 가장 크게 기여한 feature는 무엇인가?
```

### 차트 구성

이 chart는 세 영역으로 구성된다.

```text
좌측
  - 기준 구간과 현재 구간의 PCA scatter
  - 기준 구간의 정상 변동 타원
  - 기준 평균 중심과 현재 평균 중심의 이동 방향

우측 상단
  - window별 Hotelling T2 statistic 추세
  - UCL 또는 운영 관리 기준

우측 하단
  - feature별 T2 contribution 순위
  - 평균 shift를 주도한 feature 강조
```

상단 요약 영역에는 Hotelling T2, p-value, 평균 shift 크기를 표시한다.

### 현재 상황 요약

이 예시에서는 현재 window의 Hotelling T2가 `25.7`로 UCL `14.0`을 크게 넘고, p-value는 `0.004`, 평균 shift는 `1.62`로 표시된다. PCA scatter에서는 기준 평균 중심 약 `(-0.2, -0.1)`에서 현재 평균 중심 약 `(1.9, 1.8)` 방향으로 이동해 현재 중심이 기준 정상 변동 타원 밖에 놓인다. T2 추세도 8번째 window의 `16.8`부터 UCL을 넘은 뒤 `21.4`, `25.7`로 증가하므로, 단일 관측치의 튐보다 최근 window에서 다변량 평균 벡터가 기준 범위 밖으로 이동한 drift 후보 상황으로 읽는다.

### 해석 순서

먼저 좌측 PCA scatter에서 현재 sample과 현재 평균 중심이 기준 정상 변동 타원 안에 있는지 확인한다.

```text
현재 평균 중심이 기준 타원 안에 있다
  -> 다변량 평균 shift 신호가 약하다.

현재 평균 중심이 기준 타원 가장자리로 이동했다
  -> 경계 수준의 평균 shift 후보로 본다.

현재 평균 중심이 기준 타원 밖으로 이동했다
  -> 기준 공분산 구조 대비 평균 벡터가 유의하게 이동했을 가능성이 높다.
```

그 다음 우측 상단의 T2 control chart를 확인한다. T2 statistic이 UCL을 한 번 넘었는지, 최근 window에서 반복적으로 넘는지 구분한다. 반복 초과는 지속적인 다변량 평균 shift 후보로 해석한다.

마지막으로 우측 하단의 contribution bar를 본다. contribution이 큰 feature는 평균 벡터 이동을 가장 많이 설명하는 후보이므로, 해당 feature의 단변량 평균 chart와 segment별 평균 변화를 함께 확인한다.

### Drift 후보 판단 기준

Hotelling T2가 UCL을 넘고 최근 window에서 상승 또는 반복 초과가 나타나며, PCA scatter에서 현재 평균 중심이 기준 정상 변동 범위 밖으로 이동하고, contribution 상위 feature가 업무적으로 의미 있는 평균 변화를 보이면 다변량 평균 drift 후보로 해석한다.

단, Hotelling T2는 공분산 추정, feature scaling, 정규성, 표본 수에 민감하다. 고차원/소표본 환경에서는 regularized T2 또는 차원 축소 기반 검정을 함께 고려해야 한다.

### 패널별 확인

좌측 PCA Scatter에서는 기준 sample이 기준 평균 중심 약 `(-0.2, -0.1)` 주변과 정상 변동 타원 안팎에 분포하고, 현재 sample은 우상단 영역으로 치우쳐 있다. 현재 평균 중심은 약 `(1.9, 1.8)`에 표시되어 기준 타원 밖에 놓이며, 평균 중심 연결선은 기준 구간에서 현재 구간으로 이동한 방향을 보여준다. 이 패널은 T2 값이 커진 이유가 평균 벡터의 공동 이동과 같은 방향인지 먼저 확인하는 영역이다.

우측 상단 T2 Control Chart에서는 window 값이 `4.2 -> 5.1 -> 6.0 -> 5.8 -> 7.4 -> 9.2 -> 12.5 -> 16.8 -> 21.4 -> 25.7`로 움직인다. UCL은 `14.0`이며, 8번째 window의 `16.8`부터 UCL을 넘은 뒤 마지막 window `25.7`까지 계속 증가한다. 따라서 이 예시는 한 번의 임계값 초과보다 최근 3개 window에서 평균 shift 신호가 강화되는 흐름이다.

우측 하단 Feature Contribution에서는 `소득`이 `36%`, `거래금액`이 `28%`, `이용빈도`가 `18%`, `연체일수`가 `11%`, `나이`가 `7%`로 표시된다. 상위 두 feature인 소득과 거래금액만 합쳐 `64%`를 차지하므로, 평균 벡터 이동을 설명할 때는 이 두 feature의 단변량 평균 변화와 segment별 차이를 우선 확인한다.

### 이 예시 차트의 해석

이 예시에서는 Hotelling T2가 `25.7`, p-value가 `0.004`, 평균 shift가 `1.62`로 표시되어 있다. 좌측 PCA scatter에서 현재 평균 중심 약 `(1.9, 1.8)`은 기준 평균 중심 약 `(-0.2, -0.1)`에서 우상단으로 이동했고, 기준 정상 변동 타원 밖에 놓인다.

우측 상단 control chart에서는 T2 statistic이 8번째 window부터 UCL `14.0`을 넘고, 이후 `16.8`, `21.4`, `25.7`로 증가한다. 우측 하단 contribution bar에서는 `소득` `36%`, `거래금액` `28%`, `이용빈도` `18%`가 평균 shift의 주요 기여 항목으로 나타난다. 따라서 이 예시는 기준 공분산 구조 대비 여러 feature의 평균 벡터가 함께 이동한 다변량 평균 drift 후보로 해석할 수 있다.

보고서 문장 예시는 다음과 같다.

```text
기준 구간과 현재 구간의 다변량 평균 벡터를 Hotelling T2로 비교한 결과,
현재 window의 T2 statistic은 25.7로 UCL 14.0을 초과했고 p-value는 0.004였다.
T2는 8번째 window부터 16.8, 21.4, 25.7로 UCL을 연속 초과했다.
PCA scatter에서도 평균 중심이 약 (-0.2, -0.1)에서 (1.9, 1.8)로 이동해 기준 타원 밖에 위치했다.
contribution 분석에서는 소득 36%와 거래금액 28%가 평균 shift를 주도했다.
이는 기준 공분산 구조 대비 다변량 평균 벡터가 이동한 drift 후보로 해석할 수 있다.
```

### 금지해야 할 해석

이 차트만으로 다음을 단정하지 않는다.

```text
금지 1
  - T2 초과만으로 어떤 단일 feature가 drift 원인이라고 단정한다.

금지 2
  - 공분산 추정과 scaling 조건을 확인하지 않고 T2 값을 절대 비교한다.

금지 3
  - PCA 2차원 scatter만 보고 전체 고차원 평균 이동을 확정한다.

금지 4
  - 다변량 평균 shift가 곧바로 모델 성능 저하를 의미한다고 말한다.
```

Hotelling T2는 평균 벡터 이동에 초점을 둔다. 분산 변화, cluster 변화, tail 변화는 별도 chart로 분리해 확인해야 한다.

### 추가 확인 항목

Hotelling T2 drift 후보가 나타나면 다음을 추가 확인한다.

- feature scaling, normalization, missing value 처리 변경 여부
- 공분산 행렬 추정 안정성과 regularization 필요성
- contribution 상위 feature의 단변량 평균 chart
- segment/source/time별 평균 shift 집중 여부
- 분산 drift 또는 covariance drift가 함께 발생했는지 여부
- label 확보 후 성능 지표, calibration, confidence 변화

### 적합한 사용 대상

이 chart는 다음 method variant에 적합하다.

- `Hotelling T2 / HOTELLING_T2_ONE_SAMPLE_PHASE_II`
- `Hotelling T2 / HOTELLING_T2_TWO_SAMPLE`
- `Hotelling T2 / REGULARIZED_HOTELLING_T2`

## CHART-MV-005: 기준 공분산 범위 밖 고거리 샘플 집중

![CHART-MV-005](../charts/output/CHART-MV-005.png)

### 제목

기준 공분산 범위 밖 고거리 샘플 집중

### 차트 목적

이 chart는 기준 평균과 공분산 구조를 기준으로 sample 또는 window 평균이 얼마나 이탈했는지 설명한다.

Mahalanobis distance는 feature 간 상관과 scale을 고려한 거리다. 단순 Euclidean distance와 달리 기준 분포에서 흔한 방향의 변화는 작게, 드문 방향의 변화는 크게 볼 수 있다. 따라서 공분산 기반 정상 영역에서 벗어난 sample, window, outlier cluster를 설명하는 데 적합하다.

이 차트는 다음 질문에 답한다.

```text
1. 현재 sample 중 기준 공분산 구조에서 멀어진 점이 어디에 있는가?
2. window별 평균 Mahalanobis distance가 threshold를 넘고 증가하는가?
3. threshold를 넘는 sample 비중이 커졌는가?
```

### 차트 구성

이 chart는 세 영역으로 구성된다.

```text
좌측
  - PCA projection scatter
  - 기준 정상 변동 타원
  - Mahalanobis distance가 높은 sample 강조

우측 상단
  - window별 평균 Mahalanobis distance 추세
  - 운영 threshold 또는 관리 기준

우측 하단
  - sample별 Mahalanobis distance histogram
  - threshold 초과 영역
  - 초과 sample 비중
```

상단 요약 영역에는 평균 distance, threshold 초과 비중, 최대 distance를 표시한다.

### 현재 상황 요약

이 예시에서는 평균 Mahalanobis distance가 `6.1`로 threshold `4.5`를 넘고, 최대 distance는 `6.9`까지 올라간다. Window 추세는 `2.1`에서 시작해 8번째 window의 `4.9`부터 threshold를 넘은 뒤 `5.5`, `6.1`로 계속 증가한다. PCA scatter에서는 threshold 초과 sample이 기준 정상 타원의 우상단 방향에 몰려 있고, histogram에서는 전체 sample의 `22%`가 threshold 오른쪽 tail에 놓인다. 따라서 이 화면은 기준 공분산 구조에서 드문 방향으로 sample cluster가 이동한 공분산 기반 이탈 drift 후보 상황을 보여준다.

### 해석 순서

먼저 좌측 PCA scatter에서 높은 distance sample이 기준 정상 타원 밖의 어느 방향에 몰려 있는지 확인한다.

```text
높은 distance sample이 소수 outlier에만 있다
  -> 데이터 품질, 이상치, 수집 오류를 먼저 확인한다.

높은 distance sample이 특정 방향에 군집한다
  -> 신규 segment 또는 특정 feature 조합의 구조적 변화를 의심한다.

전체 sample의 distance가 넓게 증가한다
  -> 공분산 구조 또는 전처리 변경 가능성을 확인한다.
```

그 다음 우측 상단의 distance 추세를 본다. 평균 distance가 threshold 아래에서 안정적이면 이탈 신호가 약하다. 최근 window에서 threshold를 넘고 상승하면 공분산 기반 이탈 신호가 강화된 것으로 본다.

마지막으로 우측 하단 histogram에서 threshold 초과 sample 비중을 확인한다. 평균 distance가 커도 초과 sample이 극소수이면 outlier 중심 해석이 필요하고, 초과 비중이 넓게 증가하면 population 수준 변화 후보로 해석한다.

### Drift 후보 판단 기준

평균 Mahalanobis distance가 threshold를 넘고 최근 window에서 상승하며, threshold 초과 sample 비중이 운영 기준보다 커지고, PCA scatter에서 고거리 sample이 특정 방향 또는 cluster로 나타나면 공분산 기반 이탈 drift 후보로 해석한다.

단, Mahalanobis distance는 공분산 추정과 feature scaling에 민감하다. 공분산 행렬이 불안정하거나 고차원 소표본이면 robust covariance 또는 regularization 기반 변종을 함께 고려해야 한다.

### 패널별 확인

좌측 PCA Scatter에서는 기준 정상 변동 타원이 PC1 `0.0`, PC2 `0.0` 주변에 표시되고, sample의 Mahalanobis distance가 클수록 붉은 점으로 강조된다. Threshold `4.5` 이상인 sample은 주로 PC1 `2.0~3.1`, PC2 `1.4~2.7`의 우상단 영역에 모인다. 최대 distance `6.9` sample도 이 영역에 있으므로, 이 예시에서는 고거리 sample이 단순히 흩어진 outlier라기보다 특정 방향의 cluster처럼 보이는지 확인한다.

우측 상단 Distance 추세에서는 window 값이 `2.1 -> 2.3 -> 2.4 -> 2.8 -> 3.1 -> 3.6 -> 4.2 -> 4.9 -> 5.5 -> 6.1`로 증가한다. Threshold는 `4.5`이며, 8번째 window의 `4.9`부터 기준선을 넘은 뒤 마지막 window `6.1`까지 상승한다. 최근 3개 window가 연속으로 threshold를 넘기 때문에 일회성 spike보다 공분산 기반 이탈 신호가 강화되는 흐름으로 읽는다.

우측 하단 Distance Histogram에서는 distance bin `1~4`에 정상권 sample이 주로 분포하고, threshold `4.5` 오른쪽의 bin `5~7`이 tail 영역으로 강조된다. 이 tail 영역의 초과 비중은 `22%`로 표시된다. 평균 distance가 높아진 이유가 극소수 outlier 때문인지, 아니면 threshold 초과 sample 비중이 넓게 늘었는지 이 패널에서 함께 확인한다.

### 이 예시 차트의 해석

이 예시에서는 평균 Mahalanobis distance가 `6.1`, threshold 초과 비중이 `22%`, 최대 distance가 `6.9`로 표시되어 있다. 좌측 PCA scatter에서 threshold 초과 sample은 기준 정상 타원의 우상단 방향에 집중되어 있다.

우측 상단 추세에서는 평균 distance가 `2.1`에서 시작해 8번째 window `4.9`부터 threshold `4.5`를 넘고, 이후 `5.5`, `6.1`로 증가한다. 우측 하단 histogram에서도 threshold 오른쪽 tail 영역의 sample 비중이 `22%`로 표시된다. 따라서 이 예시는 기준 공분산 구조에서 벗어난 sample이 특정 방향에 집중되는 공분산 기반 이탈 drift 후보로 해석할 수 있다.

보고서 문장 예시는 다음과 같다.

```text
기준 평균과 공분산 구조를 기준으로 Mahalanobis distance를 계산한 결과,
현재 window의 평균 distance는 6.1로 threshold 4.5를 초과했다.
Window 추세는 8번째 window의 4.9부터 threshold를 넘고 마지막 window에서 6.1까지 증가했다.
Distance histogram에서는 전체 sample의 22%가 threshold를 넘었고,
PCA scatter에서는 최대 distance 6.9를 포함한 고거리 sample이 우상단 방향에 집중되어 있다.
이는 기준 공분산 구조에서 벗어난 sample cluster가 증가한 drift 후보로 해석할 수 있다.
```

### 금지해야 할 해석

이 차트만으로 다음을 단정하지 않는다.

```text
금지 1
  - distance가 큰 sample을 모두 오류 데이터로 단정한다.

금지 2
  - 공분산 추정 안정성을 확인하지 않고 threshold 초과를 확정적으로 해석한다.

금지 3
  - PCA 2차원 위치만으로 전체 고차원 이탈 방향을 단정한다.

금지 4
  - 높은 distance가 곧바로 모델 성능 저하를 의미한다고 말한다.
```

Mahalanobis distance는 공분산 기반 이탈을 요약한다. 원인 설명에는 feature contribution, segment 분석, 단변량 drift chart가 필요하다.

### 추가 확인 항목

Mahalanobis distance drift 후보가 나타나면 다음을 추가 확인한다.

- feature scaling, normalization, missing value 처리 변경 여부
- 공분산 행렬 추정 안정성과 robust covariance 필요성
- threshold 초과 sample의 segment/source/time 분포
- 고거리 sample이 특정 feature 조합에 의해 발생하는지 여부
- Hotelling T2, MMD, Energy Distance와의 합의 여부
- label 확보 후 성능 지표, calibration, confidence 변화

### 적합한 사용 대상

이 chart는 다음 method variant에 적합하다.

- `Mahalanobis Distance / SAMPLE_MAHALANOBIS_OUTLIER`
- `Mahalanobis Distance / WINDOW_MEAN_MAHALANOBIS`
- `Mahalanobis Distance / ROBUST_MAHALANOBIS`
