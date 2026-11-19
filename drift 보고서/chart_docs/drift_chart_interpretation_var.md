# Variance Chart Interpretation Guide

## CHART-VAR-001: 현재 구간에서 커진 값의 변동성

![CHART-VAR-001](../charts/output/CHART-VAR-001.png)

### 차트 목적

이 chart는 기준 구간과 현재 구간의 값의 퍼짐, 즉 분산 또는 절대편차가 달라졌는지 보여준다.

F-test 계열은 분산비에 초점을 두고, Levene/Brown-Forsythe 계열은 중심값으로부터의 절대편차 차이에 초점을 둔다. 따라서 이 chart는 분포 폭, 분산비, 절대편차를 함께 보여주어 “중심이 움직였는가”가 아니라 “폭이 넓어졌는가 또는 좁아졌는가”를 해석하게 한다.

### 제목

현재 구간에서 커진 값의 변동성

### 현재 상황 요약

이 예시에서는 기준 구간과 현재 구간의 중심값이 각각 `52.0`, `52.6`으로 거의 비슷하지만 값의 퍼짐은 뚜렷하게 커졌다. 기준 분산 `42.3`이 현재 분산 `112.4`로 증가해 variance ratio가 `2.66`이고, 표준편차도 `6.5`에서 `10.6`으로 커진다. Levene 계열 p-value는 `0.012`, 중심값 기준 평균 절대편차는 `5.1`에서 `8.7`로 `+3.6` 증가하므로, 이 화면은 평균 상승보다 현재 구간의 변동성 확대를 먼저 의심해야 하는 분산 drift 후보 상황이다.

### 차트 구성

이 chart는 세 영역으로 구성된다.

```text
좌측
  - 기준 구간과 현재 구간의 violin/box plot
  - IQR, whisker, 중심선, 표준편차 라벨

우측 상단
  - 기준/현재 분산 bar
  - 표준편차와 variance ratio

우측 하단
  - 중심값 기준 평균 절대편차 비교
  - variance ratio 판단 기준선
```

상단 요약 영역에는 variance ratio, p-value, 절대편차 변화를 표시한다.

### 패널별 확인

좌측 분포 폭과 Box 비교 패널에서는 기준 구간의 whisker가 `39.5~64.0`인 반면 현재 구간은 `31.0~77.5`까지 넓어진다. IQR도 기준 `47.6~56.5`에서 현재 `44.0~61.8`로 확장되고, 중심값은 `52.0`과 `52.6`으로 큰 차이가 없으므로 위치 이동보다 폭 확대가 핵심 신호다.

우측 상단 분산 비교 패널에서는 기준 분산 `42.3`, 현재 분산 `112.4`가 막대로 표시된다. variance ratio `2.66x`는 현재 구간의 변동성이 기준보다 두 배 이상 커졌음을 요약하며, 표준편차 `6.5 -> 10.6`도 같은 방향을 지지한다.

우측 하단 절대편차 변화 패널에서는 중심값 기준 평균 절대편차가 `5.1`에서 `8.7`로 증가한다. variance ratio `2.66x`가 판단 기준선 `1.5x`를 넘고 Levene p-value가 `0.012`로 표시되므로, 분산비와 절대편차가 모두 현재 구간의 퍼짐 증가를 같은 방향으로 가리키는지 확인한다.

### 해석 순서

먼저 좌측 분포 패널에서 현재 구간의 폭이 기준 구간보다 넓어졌는지 또는 좁아졌는지 확인한다.

```text
현재 분포 폭이 넓어졌다
  -> 같은 평균 근처에서도 예측 입력 또는 score 변동성이 커졌을 수 있다.

현재 분포 폭이 좁아졌다
  -> population이 특정 범위로 압축되었을 수 있다.
```

그 다음 variance ratio와 p-value를 확인한다. Variance ratio가 1보다 크면 현재 구간 분산이 기준보다 크고, 1보다 작으면 현재 구간 분산이 작다.

마지막으로 절대편차 패널을 확인한다. Levene/Brown-Forsythe 계열에서는 평균 또는 중앙값 기준 절대편차가 실질적인 해석 단위다.

### Drift 후보 판단 기준

p-value가 관리 기준보다 작고, variance ratio 또는 절대편차 변화가 사전에 정한 운영 기준을 넘으며, 분포 폭 변화가 실제 업무 영향과 연결되면 분산 drift 후보로 해석한다. 단, 평균 이동만으로 분산 차이가 커 보이는 경우는 평균 chart와 함께 분리해서 해석해야 한다.

Levene/Brown-Forsythe 변종에서는 중심값 기준 절대편차 증가 또는 감소가 반복되는지 확인하고, F-test 변종에서는 정규성 또는 tail/outlier 민감도를 별도로 점검한다.

### 이 예시 차트의 해석

이 예시에서는 variance ratio가 `2.66`, p-value가 `0.012`, 절대편차 변화가 `+3.6`으로 표시되어 있다. 기준 구간 분산은 `42.3`, 현재 구간 분산은 `112.4`이며, 표준편차도 `6.5`에서 `10.6`으로 증가했다.

좌측 분포 패널에서도 현재 구간의 whisker와 IQR이 기준 구간보다 넓다. 따라서 이 예시는 중심 위치가 크게 달라졌다기보다 현재 구간의 변동성이 증가한 분산 drift 후보로 해석할 수 있다.

보고서 문장 예시는 다음과 같다.

```text
기준 구간과 현재 구간의 분산을 비교한 결과,
현재 구간 분산은 112.4로 기준 구간 42.3 대비 2.66배 높았다.
Levene 계열 p-value는 0.012이고 평균 절대편차도 5.1에서 8.7로 증가했다.
이는 현재 구간에서 값의 퍼짐이 커진 분산 drift 후보로 해석할 수 있다.
```

### 금지해야 할 해석

이 차트만으로 다음을 단정하지 않는다.

```text
금지 1
  - 분산 증가를 곧바로 평균 증가로 해석한다.

금지 2
  - 평균 이동 또는 이상치 몇 개가 만든 분산 증가를 전체 population 변화로 단정한다.

금지 3
  - F-test 결과를 정규성, tail, outlier 점검 없이 확정적으로 해석한다.

금지 4
  - 분산 변화가 곧바로 모델 성능 저하를 의미한다고 말한다.
```

분산 drift는 모델이 threshold, calibration, confidence, uncertainty에 민감할 때 중요해질 수 있으므로 모델 영향 확인이 필요하다.

### 추가 확인 항목

분산 drift 후보가 나타나면 다음을 추가 확인한다.

- 평균 이동과 분산 이동이 동시에 발생했는지 여부
- outlier, tail, clipping, winsorization 변경 여부
- 측정 단위, scaling, normalization 변경 여부
- segment별로 분산 증가가 특정 집단에 집중되는지 여부
- threshold 주변 sample 증가 또는 감소 여부
- label 확보 후 calibration, confidence, error rate 변화

### 적합한 사용 대상

이 chart는 다음 method variant에 적합하다.

- `F-test / Variance Test 계열 / F_TEST_EQUAL_VARIANCE`
- `F-test / Variance Test 계열 / ANOVA_F_TEST_GROUP_MEAN`
- `F-test / Variance Test 계열 / MODEL_COMPARISON_F_TEST`
- `Levene's Test / LEVENE_MEAN_CENTER`
- `Levene's Test / BROWN_FORSYTHE_MEDIAN_CENTER`
- `Levene's Test / TRIMMED_MEAN_LEVENE`
