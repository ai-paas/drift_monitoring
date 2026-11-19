# Distribution Shape Chart Interpretation Guide

## CHART-DISTSHAPE-001: 현재 분포의 오른쪽 어깨와 다봉성 변화

![CHART-DISTSHAPE-001](../charts/output/CHART-DISTSHAPE-001.png)

### 차트 목적

이 chart는 기준 구간과 현재 구간의 분포 형태가 달라졌는지 설명한다. 이 예시에서는 기준 분포가 feature value 50 부근에서 가장 높은 단봉형에 가깝지만, 현재 분포는 65 부근 봉우리가 커지고 오른쪽 shoulder가 생긴 형태를 보인다.

Epps-Singleton 계열은 empirical characteristic function 차이를 이용해 평균, 분산, skew, tail, modality 변화가 섞인 분포 차이를 포착한다. 따라서 이 chart는 단순 평균 이동이나 분산 증가가 아니라 "분포의 모양 자체가 달라졌는가"를 확인하는 데 사용한다.

이 차트는 다음 질문에 답한다.

```text
1. 현재 분포가 기준 분포와 다른 형태를 보이는가?
2. 어떤 frequency 영역에서 characteristic function 차이가 큰가?
3. Epps-Singleton statistic과 p-value가 drift 후보 판단 기준을 만족하는가?
```

### 제목

현재 분포의 오른쪽 어깨와 다봉성 변화

### 현재 상황 요약

이 예시의 Epps-Singleton statistic은 `12.8`, p-value는 `0.006`이다. ECF 차이는 `t=2.0`에서 가장 크며 real component 차이는 `0.24`, imaginary component 차이는 `0.19`로 표시된다. 같은 주파수의 통계량 기여도는 `0.094`로 가장 크다.

분포 overlay에서는 기준 밀도가 50에서 `0.96`으로 가장 높고 이후 감소하지만, 현재 밀도는 65에서 `0.90`까지 올라간다. 따라서 단순히 평균만 오른쪽으로 이동했다기보다 현재 구간에 오른쪽 shoulder와 다봉성 변화가 함께 나타난 사례로 읽는다.

### 차트 구성

이 chart는 세 영역으로 구성된다.

```text
좌측
  - 기준 구간과 현재 구간의 density overlay
  - 기준 peak 50, 현재 peak 65 부근의 형태 차이
  - 오른쪽 shoulder와 다봉성 변화 표시

우측 상단
  - frequency t별 ECF real component 차이
  - frequency t별 ECF imaginary component 차이

우측 하단
  - frequency별 Epps-Singleton statistic 기여도
  - 가장 큰 기여 frequency t=2.0 강조
```

상단 요약 영역에는 ES statistic `12.8`, p-value `0.006`, 최대 ECF 차이가 발생한 `t=2.0`을 표시한다.

### 패널별 확인

좌측 분포 비교 패널에서는 기준 분포와 현재 분포의 봉우리 위치와 폭을 먼저 본다. 기준 분포는 45~55 구간에서 높고 50에서 `0.96`까지 올라가지만, 현재 분포는 45~50에서 낮아진 뒤 60~70 구간에서 다시 커져 65에서 `0.90`을 기록한다.

우측 상단 ECF 차이 패널에서는 frequency별 real/imaginary 차이를 본다. `t=2.0`에서 real diff `0.24`, imaginary diff `0.19`가 동시에 커지고, `t=2.5`에서도 real diff `0.21`, imaginary diff `0.16`이 남아 있어 중간 frequency 영역의 형태 차이가 두드러진다.

우측 하단 통계량 기여 패널에서는 어떤 frequency가 ES statistic을 가장 많이 만드는지 본다. `t=2.0`의 기여도는 `0.094`로 가장 크고, 다음으로 `t=2.5`가 `0.070`, `t=1.5`가 `0.055` 수준이다. p-value `0.006`과 함께 보면 이 예시는 분포 형태 drift 후보에 가깝다.

### 해석 순서

먼저 좌측 분포 overlay에서 기준 구간과 현재 구간의 형태 차이를 확인한다.

```text
현재 분포가 기준보다 단순히 오른쪽 또는 왼쪽으로 이동했다
  -> 평균 이동 chart 또는 Wasserstein chart와 함께 해석한다.

현재 분포의 봉우리가 늘거나 shoulder가 생겼다
  -> modality 또는 segment mix 변화 가능성을 확인한다.

현재 분포의 한쪽 tail이 두꺼워졌다
  -> tail risk, outlier, 상위/하위 segment 유입 여부를 확인한다.
```

그 다음 우측 상단의 ECF 차이를 본다. 특정 frequency에서 real 또는 imaginary component 차이가 커지면, 해당 주파수 성분에서 두 분포의 형태가 다르다는 뜻이다. 여러 frequency에서 차이가 함께 커지면 단일 위치 이동보다 복합적인 형태 변화일 가능성이 높다.

마지막으로 우측 하단의 통계량 기여도를 확인한다. 가장 큰 기여 frequency가 어디인지 확인하고, p-value가 운영 기준보다 작은지 함께 본다.

### Drift 후보 판단 기준

p-value가 관리 기준보다 작고, 분포 overlay에서 다봉성, shoulder, 비대칭, tail 변화가 관측되며, ECF 차이나 statistic 기여도가 특정 frequency에 집중되거나 여러 frequency에서 일관되게 커지면 distribution shape drift 후보로 해석한다.

단, 표본 수가 작거나 binning/smoothing 방식이 달라진 경우에는 분포 형태 차이가 과장될 수 있으므로 sample size와 전처리 조건을 함께 확인한다.

### 이 예시 차트의 해석

이 예시에서는 ES statistic이 `12.8`, p-value가 `0.006`으로 표시되어 있다. 좌측 분포 overlay에서는 기준 분포가 50 부근에서 단봉형 peak를 보이는 반면, 현재 분포는 65 부근에서 더 큰 봉우리를 만들고 오른쪽 shoulder가 나타난다.

ECF 차이 패널에서는 real component와 imaginary component가 모두 `t=2.0`에서 가장 크다. 통계량 기여도 패널에서도 `t=2.0`의 기여도 `0.094`가 가장 크므로, 이 예시는 현재 구간에서 분포 형태가 기준 구간과 달라진 distribution shape drift 후보로 해석할 수 있다.

보고서 문장 예시는 다음과 같다.

```text
기준 구간과 현재 구간을 Epps-Singleton 관점에서 비교한 결과,
ES statistic은 12.8, p-value는 0.006으로 나타났다.
분포 overlay에서는 기준 peak가 50 부근에 있는 반면 현재 peak는 65 부근에서 커졌고,
ECF 차이는 t=2.0에서 real 0.24, imaginary 0.19로 가장 크게 나타났다.
이는 단순 평균 이동보다 분포 형태 변화가 동반된 drift 후보로 해석할 수 있다.
```

### 금지해야 할 해석

이 차트만으로 다음을 단정하지 않는다.

```text
금지 1
  - p-value가 작다는 이유만으로 모델 성능 저하를 확정한다.

금지 2
  - 분포 형태 차이를 특정 segment 유입 원인으로 바로 단정한다.

금지 3
  - smoothing 또는 density 추정 설정을 확인하지 않고 다봉성을 확정한다.

금지 4
  - 평균 이동, 분산 변화, tail 변화 중 어떤 원인이 지배적인지 분리하지 않고 하나로 해석한다.
```

Epps-Singleton 계열은 복합적인 분포 형태 차이를 잘 포착하지만, 차이의 원인을 자동으로 분해해 주지는 않는다. 평균, 분산, tail, segment 분석을 함께 확인해야 한다.

### 추가 확인 항목

distribution shape drift 후보가 나타나면 다음을 추가 확인한다.

- 표본 수와 window 크기가 충분한지 여부
- density smoothing, histogram binning, clipping 설정 변화
- 평균 이동 chart, 분산 chart, Wasserstein chart와의 합의 여부
- 특정 segment, source, 시간대에서 다봉성 또는 shoulder 변화가 집중되는지 여부
- outlier 또는 tail sample 증가 여부
- label 확보 후 성능 지표, calibration, confidence 변화

### 적합한 사용 대상

이 chart는 다음 method variant에 적합하다.

- `Epps-Singleton Test / TWO_SAMPLE_EPPS_SINGLETON`
- `Epps-Singleton Test / DISCRETE_EPPS_SINGLETON`
- `Epps-Singleton Test / ASYMPTOTIC_EPPS_SINGLETON`
