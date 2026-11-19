# Histogram 계열 차트 해석 가이드

이 문서는 CHART-HIST chart id의 이미지와 해석 방법을 정리한다.

## CHART-HIST-001: 높은 값 구간 증가로 줄어든 히스토그램 겹침

![CHART-HIST-001](../charts/output/CHART-HIST-001.png)

### 차트 목적

`CHART-HIST-001`은 기준 구간과 현재 구간의 histogram이 얼마나 겹치는지 확인하기 위한 차트다. Histogram Intersection Normalized Complement, HINC, 계열처럼 bin별 공통 확률 질량을 합산하고, 그 보수값을 drift distance로 사용하는 방법에 적합하다.

### 제목

높은 값 구간 증가로 줄어든 히스토그램 겹침

### 현재 상황 요약

현재 histogram은 기준 histogram보다 높은 값 구간의 확률이 커지고 낮은 값 구간의 확률이 줄어든다. `20-30` bin은 `0.16`에서 `0.10`으로 줄어 손실 최대 bin이 되고, `70-80` bin은 `0.05`에서 `0.10`으로 늘어난다. 전체 intersection은 `0.820`, HINC는 `0.180`이며 현재 window는 관리 기준 `0.220` 아래에 있다. 따라서 이 예시는 높은 값 구간 증가로 histogram 겹침이 줄었지만, 현재 시점에서는 강한 drift 확정보다 완화 중인 분포 이동 후보로 해석한다.

이 차트는 다음 질문에 답한다.

```text
1. 기준 histogram과 현재 histogram이 어느 정도 겹치는가?
2. 어떤 bin에서 intersection이 유지되고, 어떤 bin에서 겹침이 줄었는가?
3. normalized complement가 시간에 따라 증가하고 있는가?
```

### 차트 구성

왼쪽 패널은 histogram overlay다.

- 파란 막대는 기준 구간의 bin별 확률이다.
- 붉은 막대는 현재 구간의 bin별 확률이다.
- 초록 막대는 두 분포의 bin별 intersection, 즉 `min(p, q)` 영역이다.
- 초록 영역이 줄어들수록 기준/현재 histogram의 공통 확률 질량이 줄어든다.

오른쪽 위 패널은 intersection 기여다.

- 막대 길이는 bin별 `min(p, q)` 값이다.
- 큰 막대는 기준/현재 분포가 여전히 많이 겹치는 bin이다.
- 작은 막대 또는 누락된 bin은 겹침이 줄어든 구간 후보로 본다.

오른쪽 아래 패널은 거리 추세다.

- y축은 `1 - histogram intersection` 형태의 normalized complement다.
- 값이 커질수록 histogram overlap이 줄어든다.
- 초록 점선은 관리 기준 또는 운영 threshold 예시다.

상단 요약 카드에는 다음 값이 표시된다.

- `HINC`: normalized complement 거리
- `Intersection`: 전체 histogram intersection 합
- `손실 최대 bin`: 기준/현재 확률 차이가 가장 큰 bin

### 해석 순서

먼저 HINC와 intersection 값을 함께 본다.

```text
Intersection이 높고 HINC가 낮다
  -> 기준/현재 histogram이 많이 겹친다.

Intersection이 낮고 HINC가 높다
  -> 공통 확률 질량이 줄어든 drift 후보다.

HINC가 추세적으로 증가한다
  -> histogram overlap 감소가 누적되고 있다.
```

그 다음 왼쪽 overlay에서 겹침이 줄어든 bin을 확인한다. 현재 분포가 오른쪽으로 이동하면 낮은 bin의 intersection은 줄고 높은 bin의 현재 확률은 증가할 수 있다.

마지막으로 오른쪽 위 intersection 기여를 확인한다. 많이 겹치는 bin과 겹침이 약해진 bin을 구분하면 보고서에서 “어느 구간은 유지되고, 어느 구간이 달라졌다”를 설명할 수 있다.

### Drift 후보 판단 기준

HINC가 관리 기준을 넘거나 상승 추세가 지속되고, 겹침이 줄어든 bin이 명확하면 histogram overlap 감소 drift 후보로 해석한다. binning 기준 변경 여부를 먼저 확인한다.

### 패널별 확인

Histogram Overlay:

- 기준 histogram은 `30-40` bin `0.19`, `40-50` bin `0.18`, `20-30` bin `0.16`에 많이 분포한다.
- 현재 histogram은 `50-60` bin `0.17`, `60-70` bin `0.13`, `70-80` bin `0.10`, `80-90` bin `0.06`처럼 높은 값 구간 비중이 늘어난다.
- 가장 큰 차이는 `20-30` bin `-0.06`, `70-80` bin `+0.05`, `10-20`과 `30-40` bin `-0.04`에서 나타난다.

Intersection 기여:

- 전체 intersection은 `0.820`으로 기준/현재 histogram의 공통 확률 질량이 82.0% 남아 있다.
- `40-50`, `30-40`, `50-60`처럼 중심부 bin은 여전히 많이 겹친다.
- 반대로 `20-30` 감소와 `70-80`, `80-90` 증가는 겹침을 줄이는 방향으로 작동한다.

거리 추세:

- HINC는 `0.11 -> 0.13 -> 0.15 -> 0.18 -> 0.21 -> 0.24 -> 0.18` 순서로 움직인다.
- 직전 window에서는 관리 기준 `0.22`를 넘었지만 현재 window에서는 `0.18`로 내려온다.
- 따라서 histogram overlap 감소가 한때 강해졌으나 현재는 기준 아래로 완화됐는지 추가 window를 확인해야 한다.

### 이 예시 차트의 해석

이 예시에서는 HINC가 `0.180`, intersection이 `0.820`, 손실 최대 bin이 `20-30`으로 표시되어 있다. 기준 구간과 현재 구간은 여전히 82% 정도의 histogram overlap을 갖지만, 현재 분포가 높은 bin 쪽으로 이동하면서 일부 낮은 bin의 겹침이 줄어든다.

거리 추세 패널에서는 normalized complement가 직전 window에서 관리 기준을 넘었다가 현재 window에서 다시 기준 아래로 내려온다. 따라서 이 예시는 histogram overlap 감소가 관측되지만, 현재 시점에서는 완화 중인 분포 이동 후보로 해석할 수 있다.

보고서 문장 예시는 다음과 같다.

```text
기준 구간과 현재 구간의 histogram intersection을 비교한 결과,
HINC는 0.180, intersection은 0.820으로 나타났다.
현재 구간은 높은 값 bin 쪽 확률이 증가하면서 기준 histogram과의 overlap이 감소했다.
직전 window에서 normalized complement가 관리 기준을 넘었지만 현재는 기준 아래로 내려와,
완화 중인 histogram 기반 분포 이동 후보로 해석할 수 있다.
```

### 금지해야 할 해석

이 차트만으로 다음을 단정하지 않는다.

```text
금지 1
  - histogram overlap 감소가 곧바로 모델 성능 저하를 의미한다고 말한다.

금지 2
  - binning 기준의 영향을 확인하지 않고 drift 크기를 확정한다.

금지 3
  - intersection이 높은 bin만 보고 전체 drift가 없다고 단정한다.

금지 4
  - 단일 feature histogram 변화로 전체 데이터 drift를 확정한다.
```

Histogram intersection 계열은 binning에 민감하다. bin 폭, 경계, clipping, outlier 처리 기준을 함께 확인해야 한다.

### 추가 확인 항목

Histogram intersection 변화가 보이면 다음을 추가 확인한다.

- binning 기준, bin 폭, 경계 설정
- normalized histogram인지 raw count histogram인지
- 손실이 큰 bin의 sample count와 segment 구성
- 같은 feature의 Wasserstein Distance, PSI, KL Divergence 결과
- outlier, clipping, scaling 정책 변경 여부
- label 확보 후 성능 지표, calibration, error rate 변화

### 적합한 사용 대상

이 chart는 다음 method variant에 적합하다.

- `Histogram Intersection Normalized Complement / HINC_CATEGORICAL`
- `Histogram Intersection Normalized Complement / HINC_HISTOGRAM_NUMERIC`
- `Histogram Intersection Normalized Complement / HINC_IMAGE_FEATURE`

