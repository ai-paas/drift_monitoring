# PSI Chart Interpretation Guide

## CHART-PSI-001: 상위 점수 구간 증가로 본 PSI 드리프트

![CHART-PSI-001](../charts/output/CHART-PSI-001.png)

### 차트 목적

이 chart는 기준 구간과 현재 구간의 bin 비율 차이를 Population Stability Index 관점에서 보여준다.

PSI는 score band, numeric bin, categorical bin처럼 discrete bin으로 나뉜 population 구성이 얼마나 달라졌는지 요약한다. 전체 PSI 값만 보는 대신, 어떤 bin이 PSI를 크게 만들었는지와 그 bin의 실제 비율 변화 방향을 함께 확인하는 것이 핵심이다.

### 제목

상위 점수 구간 증가로 본 PSI 드리프트

### 현재 상황 요약

이 예시에서는 현재 window의 PSI가 `0.123`으로 관리 기준 `0.10`을 넘었다. 기준 구간 대비 현재 구간에서 `80-100` score band가 `12%`에서 `20%`로 `+8pp` 증가했고, `60-80` band도 `24%`에서 `32%`로 `+8pp` 증가했다. 반대로 `20-40` band는 `22%`에서 `15%`로 `-7pp`, `0-20` band는 `12%`에서 `7%`로 `-5pp` 줄어 population이 낮은 score band에서 높은 score band로 이동한 PSI drift 후보 상황이다.

### 차트 구성

이 chart는 세 영역으로 구성된다.

```text
좌측
  - 기준 구간과 현재 구간의 bin별 비율 grouped bar
  - 상위 PSI 기여 bin 강조

우측 상단
  - bin별 PSI contribution 순위
  - 각 bin의 signed 비율 변화 표시

우측 하단
  - window별 PSI 추세
  - 관리 기준선 표시
```

상단 요약 영역에는 현재 window의 PSI, 상위 기여 bin, 주요 이동 방향과 크기를 표시한다.

### 패널별 확인

좌측 `Bin 비율 비교` 패널에서는 기준 비율과 현재 비율의 방향을 먼저 본다. 이 예시에서는 `80-100` bin이 `12% -> 20%`, `60-80` bin이 `24% -> 32%`로 각각 `+8pp` 증가하고, `20-40` bin은 `22% -> 15%`로 `-7pp` 감소한다. 따라서 단순한 한 bin 변동이 아니라 score band 상단으로 비중이 이동한 패턴인지 확인한다.

우측 상단 `PSI 기여도` 패널에서는 전체 PSI를 만든 bin 순위를 본다. `80-100` bin의 기여도는 `0.041`로 가장 크고, `0-20`과 `20-40` bin은 각각 약 `0.027`, `60-80` bin은 약 `0.023`, `40-60` bin은 약 `0.006` 수준이다. 같은 `+8pp` 증가라도 기준 비율이 낮은 `80-100` bin의 상대 변화가 더 커 전체 PSI에 더 크게 기여한다.

우측 하단 `PSI 추세` 패널에서는 최근 window의 PSI가 관리 기준을 넘는지 본다. PSI는 `0.035 -> 0.044 -> 0.052 -> 0.071 -> 0.092 -> 0.118 -> 0.123`으로 상승하며, 최근 두 window가 관리 기준 `0.10`을 초과한다. 이 흐름은 현재 window의 상위 score band 증가가 일시적 단일점보다 최근 강화된 population shift일 가능성을 보강한다.

### 해석 순서

먼저 상단 요약의 PSI 값과 추세 패널의 관리 기준 초과 여부를 확인한다.

```text
PSI가 관리 기준을 넘는다
  -> 기준 구간 대비 현재 population 구성이 의미 있게 달라졌을 가능성이 있다.

PSI가 상승 추세다
  -> population shift가 최근 window에서 강화되고 있다.
```

그 다음 PSI 기여도 패널에서 어떤 bin이 전체 PSI를 만들었는지 확인한다. PSI는 전체 점수 하나로 요약되지만, 실제 drift 해석은 상위 기여 bin의 증가/감소 방향으로 해야 한다.

마지막으로 좌측 bin 비율 비교에서 해당 bin의 기준 비율과 현재 비율 수준을 확인한다. 작은 bin의 급격한 변화, score 상위 band 쏠림, 하위 band 유입 감소처럼 모델 운영상 의미 있는 이동인지 판단한다.

### Drift 후보 판단 기준

PSI가 관리 기준을 넘거나 최근 window에서 상승 추세를 보이고, 상위 기여 bin에서 업무적으로 의미 있는 비율 이동이 확인되면 population drift 후보로 해석한다. 단, binning 기준, score calibration, category mapping, 표본 추출 방식이 기준 구간과 현재 구간에서 동일해야 한다.

Score band PSI에서는 상위 또는 하위 score band의 이동이 모델 threshold, 승인율, 추천 노출량, risk band 운영에 영향을 줄 수 있는지 함께 판단한다.

### 이 예시 차트의 해석

이 예시에서는 PSI가 `0.123`, 상위 기여 bin이 `80-100`, 주요 이동이 `증가 8.0pp`로 표시되어 있다. 기준 구간의 `80-100` bin 비율은 `12%`였지만 현재 구간에서는 `20%`로 증가했고, 해당 bin의 PSI 기여도는 `0.041`로 가장 크다.

PSI 추세는 `0.035`에서 `0.123`까지 상승했고 최근 window에서 관리 기준 `0.10`을 넘어 있다. 따라서 이 예시는 상위 score band로 population이 이동한 PSI drift 후보로 해석할 수 있다.

보고서 문장 예시는 다음과 같다.

```text
기준 구간과 현재 구간의 score band 분포를 PSI로 비교한 결과,
현재 window의 PSI는 0.123으로 관리 기준을 초과했다.
가장 큰 기여 bin은 80-100 band이며, 기준 12%에서 현재 20%로 8.0pp 증가했다.
이는 population이 상위 score band로 이동한 drift 후보로 해석할 수 있다.
```

### 금지해야 할 해석

이 차트만으로 다음을 단정하지 않는다.

```text
금지 1
  - PSI 값만 보고 어떤 bin이 변했는지 설명하지 않는다.

금지 2
  - score band 이동을 곧바로 모델 성능 향상 또는 저하로 단정한다.

금지 3
  - binning 기준이나 score calibration 변경 가능성을 확인하지 않고 drift로 확정한다.

금지 4
  - 전체 PSI가 낮다는 이유만으로 특정 중요 bin의 변화가 없다고 말한다.
```

PSI는 population shift를 설명하기 좋은 운영 지표지만, 원인과 영향은 bin 기여도, segment, 모델 score, label 기반 성능 지표를 함께 확인해야 한다.

### 추가 확인 항목

PSI가 커지면 다음을 추가 확인한다.

- binning 기준, score calibration, category mapping 변경 여부
- 상위 기여 bin의 sample count와 segment 구성
- score threshold, 승인율, 추천 노출량, risk band 운영 영향
- 같은 feature의 JS Distance, Total Variation, L-infinity 결과
- prediction drift와 feature drift가 같은 방향으로 나타나는지 여부
- label 확보 후 score band별 성능 지표, calibration, error rate 변화

### 적합한 사용 대상

이 chart는 다음 method variant에 적합하다.

- `PSI / NUMERIC_BINNED_PSI`
- `PSI / CATEGORICAL_PSI`
- `PSI / SCORE_BAND_PSI`
- `PSI / POPULATION_WEIGHTED_PSI`
