# Distance 계열 차트 해석 가이드

이 문서는 CHART-DIST chart id의 이미지와 해석 방법을 정리한다.

## CHART-DIST-001: 결제금액 분포의 오른쪽 이동과 거리 증가

![CHART-DIST-001](../charts/output/CHART-DIST-001.png)

### 제목

결제금액 분포의 오른쪽 이동과 거리 증가

### 차트 목적

`CHART-DIST-001`은 기준 구간과 현재 구간의 분포가 얼마나 이동했는지를 거리 기반으로 설명하기 위한 차트다. Wasserstein Distance처럼 기준 분포의 질량을 현재 분포로 옮기는 데 필요한 평균 이동량을 사용하는 drift 측정 방법에 적합하다.

이 차트는 다음 질문에 답한다.

```text
1. 현재 분포가 기준 분포 대비 어느 방향으로 이동했는가?
2. 이동 거리가 시간에 따라 증가하고 있는가?
3. 여러 feature 중 어떤 feature의 분포 이동 거리가 가장 큰가?
```

### 현재 상황 요약

현재 상황은 결제금액 feature의 현재 분포가 기준 분포보다 큰 값 쪽으로 이동하고, 최근 window에서 이동 거리가 관리 기준을 넘은 사례다. 기준 평균은 약 `-0.07`, 현재 평균은 약 `0.61`로 평균 이동은 `+0.68`이고, 중앙값도 `-0.06`에서 `0.58`로 올라간다. Wasserstein distance는 `0.68`이며 관리 기준 `0.30`을 넘는다. 상위 10% 분위수도 기준 `1.13`에서 현재 `1.99`로 `+0.86` 이동하므로, 중심부뿐 아니라 높은 값 구간에서도 이동이 확인된다. feature 거리 순위에서도 `결제금액`이 가장 크므로 이 feature의 covariate shift 후보로 해석한다.

### 차트 구성

왼쪽 패널은 기준/현재 분포 비교다.

- 파란 밀도는 기준 구간의 분포다.
- 붉은 밀도는 현재 구간의 분포다.
- 초록 점선은 분위수 이동의 예시를 보여준다.
- Wasserstein distance는 이러한 분위수 이동량을 평균한 값으로 해석할 수 있다.

오른쪽 위 패널은 거리 추세다.

- x축은 window 순서다.
- y축은 window별 Wasserstein distance다.
- 노란 점선은 관리 기준 또는 운영 threshold 예시다.
- 최근 window에서 거리가 계속 증가하면 일시적 노이즈보다 지속적 분포 이동 후보로 본다.

오른쪽 아래 패널은 feature 거리 순위다.

- 막대 길이는 feature별 Wasserstein distance다.
- 붉은 막대는 현재 window에서 가장 큰 이동 거리를 보인 feature다.
- 여러 feature가 동시에 커지면 데이터 소스나 segment 수준의 구조적 변화를 의심한다.

상단 요약 카드에는 다음 값이 표시된다.

- `Wasserstein`: 현재 대상 feature의 1D Wasserstein distance
- `평균 이동`: 현재 구간 평균에서 기준 구간 평균을 뺀 값
- `상위 10% 이동`: 상위 분위수 영역의 이동 크기

### 해석 순서

먼저 왼쪽 분포 overlay에서 이동 방향을 확인한다. 현재 분포가 기준보다 오른쪽으로 이동하면 값이 전반적으로 커진 것이고, 왼쪽으로 이동하면 작아진 것이다. Wasserstein distance는 이동의 방향이 아니라 이동 크기를 요약하므로, 방향은 overlay와 평균 이동을 함께 봐야 한다.

그 다음 오른쪽 위 추세를 확인한다.

```text
distance가 낮고 안정적이다
  -> 분포 이동 신호가 약하다.

distance가 threshold를 넘고 증가한다
  -> 최근 window에서 분포 이동 신호가 강화되고 있다.

distance가 한 번만 튄다
  -> 일시적 데이터 품질 문제 또는 outlier 영향인지 확인한다.
```

마지막으로 feature 거리 순위를 본다. 단일 feature만 크면 해당 feature의 전처리, 단위, source 변경을 먼저 확인한다. 여러 feature가 함께 크면 segment mix, 수집 시스템, population 구성 변화 같은 상위 원인을 검토한다.

### Drift 후보 판단 기준

Wasserstein distance가 관리 기준을 넘거나 상승 추세가 지속되고, 분포 overlay에서 이동 방향이 명확하면 분포 이동 drift 후보로 해석한다. feature별 scale 차이와 정규화 여부를 함께 확인한다.

### 이 예시 차트의 해석

이 예시에서는 Wasserstein distance가 `0.68`, 평균 이동이 `0.68`, 상위 10% 이동이 `0.86`으로 표시되어 있다. 현재 분포가 기준 분포보다 오른쪽으로 이동했고, 상위 분위수에서도 이동 폭이 더 크게 나타난다.

패널별로는 다음처럼 읽는다.

```text
기준/현재 분포 비교
  - 파란 밀도는 기준 분포, 붉은 밀도는 현재 분포다.
  - 기준 평균은 -0.07, 현재 평균은 0.61이고 중앙값은 -0.06에서 0.58로 이동한다.
  - 상위 10% 분위수도 1.13에서 1.99로 올라가 높은 값 구간의 이동이 더 크다.

거리 추세
  - window별 distance는 0.12, 0.16 수준에서 시작해 최근 0.68까지 상승한다.
  - 관리 기준 0.30을 중간 이후 넘고 계속 증가하므로 일시적 spike보다 지속적 이동 가능성을 본다.

Feature 거리 순위
  - 결제금액 distance가 0.68로 가장 크다.
  - 접속시간 0.41, 방문빈도 0.34도 함께 높아지는지 보면 단일 feature 문제인지 segment/source 변화인지 구분하는 데 도움이 된다.
```

거리 추세 패널에서는 최근 window로 갈수록 distance가 증가하고 관리 기준을 넘는다. Feature 거리 순위에서도 `결제금액`의 이동 거리가 가장 크다. 따라서 이 예시는 특정 numeric feature에서 분포 위치가 오른쪽으로 이동하고, 최근 window에서 이동 신호가 강화되는 사례로 해석할 수 있다.

보고서 문장 예시는 다음과 같다.

```text
기준 구간과 현재 구간을 Wasserstein Distance 관점에서 비교한 결과,
대상 feature의 Wasserstein distance는 0.68로 나타났다.
분포 overlay에서는 현재 구간이 기준 구간보다 오른쪽으로 이동했으며,
최근 window에서 distance가 관리 기준을 초과하고 증가하는 추세가 관측된다.
Feature 거리 순위에서는 결제금액 feature가 가장 큰 이동 거리를 보였다.
이는 해당 feature의 covariate shift 후보로 해석할 수 있다.
```

### 금지해야 할 해석

이 차트만으로 다음을 단정하지 않는다.

```text
금지 1
  - distance가 크다는 이유만으로 모델 성능 저하를 확정한다.

금지 2
  - feature 이동의 원인을 특정 source 변경으로 단정한다.

금지 3
  - 방향 정보를 overlay 없이 distance 값만으로 해석한다.

금지 4
  - 여러 feature 비교에서 scale 차이를 보정하지 않고 순위를 단정한다.
```

Wasserstein distance는 feature scale의 영향을 받는다. feature별 비교에서는 표준화, 단위, clipping, winsorization 여부를 함께 확인해야 한다.

### 추가 확인 항목

Wasserstein distance가 커지면 다음을 추가 확인한다.

- feature 단위, scaling, normalization 변경 여부
- outlier, clipping, missing value 대체 정책 변화
- 이동 거리가 큰 feature의 segment, source, 시간대 구성 변화
- KS Test, PSI, Cramer-von Mises Test 등 다른 detector와의 합의 여부
- feature별 scale 보정 또는 normalized distance 적용 여부
- label 확보 후 성능 지표, calibration, error rate 변화

### 적합한 사용 대상

이 chart는 다음 method variant에 적합하다.

- `Wasserstein Distance / WASSERSTEIN_1D_EXACT`
- `Wasserstein Distance / WASSERSTEIN_WINDOW_TREND`
- `Wasserstein Distance / SLICED_WASSERSTEIN_EMBEDDING`
- `Wasserstein Distance / WASSERSTEIN_APPROX_HISTOGRAM`

다만 sliced 또는 approximate 변종에서는 projection count, approximation error, histogram binning 설정을 caption 또는 보조 패널에 추가해야 한다.


