# BOCD Chart Interpretation

## CHART-BOCD-001

![CHART-BOCD-001](../charts/output/CHART-BOCD-001.png)

### 제목

온라인 변화점 확률과 스트림 수준 변화 확인

### 차트 목적

이 chart는 Bayesian Online Change Point Detection이 stream을 순차적으로 관측하면서 change point probability와 run length posterior를 갱신하는 방식을 설명한다.

BOCD는 특정 시점이 새로운 segment의 시작일 확률과 현재 run length의 posterior 분포를 함께 본다. 따라서 단순 trend 변화뿐 아니라 posterior가 reset되는 구조를 확인해야 한다.

이 차트는 다음 질문에 답한다.

```text
1. change point probability가 특정 시점에 집중되는가?
2. run length posterior가 해당 시점에서 reset되는가?
3. stream trend에서 같은 시점의 수준 변화가 관찰되는가?
```

### 현재 상황 요약

현재 상황은 BOCD가 운영 stream을 순차적으로 관측하다가 t=18 부근에서 새로운 segment가 시작됐을 가능성을 높게 본 사례다. 좌측 heatmap에서는 change point probability가 t=18에서 0.87까지 올라가고, 우측 상단 run length posterior는 같은 시점에서 낮은 run length로 reset된다. 우측 하단 stream trend도 t=18 이후 평균 수준이 0.55에서 0.87로 상승하므로, 이 예시는 posterior 변화와 실제 stream 수준 변화가 같은 시점에 맞물린 online change point 후보로 해석한다. t=27에는 보조 peak와 평균 1.10 수준으로의 추가 상승이 있어 두 번째 segment 변화 가능성도 함께 점검해야 한다.

### 차트 구성

이 chart는 세 영역으로 구성된다.

```text
좌측
  - change point probability heatmap
  - primary/secondary change marker

우측 상단
  - run length posterior heatmap
  - reset marker

우측 하단
  - stream trend
  - segment mean line
  - change point marker
```

상단 요약 영역에는 peak change point probability, primary change point, run length 상태를 표시한다.

### 해석 순서

먼저 좌측 heatmap에서 change point probability가 특정 시간대에 집중되는지 확인한다.

```text
posterior가 전 구간에 낮게 퍼져 있다
  -> 명확한 change point 증거가 약하다.

posterior가 한두 시점에 강하게 집중된다
  -> 해당 시점을 change point 후보로 본다.

posterior peak가 여러 번 반복된다
  -> segment가 여러 차례 바뀌었거나 hazard rate가 과민할 수 있다.
```

그 다음 우측 상단 run length posterior에서 change point 후보 시점에 run length가 낮은 값으로 reset되는지 확인한다.

마지막으로 우측 하단 stream trend에서 같은 시점에 평균 또는 분포 수준의 변화가 있는지 확인한다. Posterior peak와 stream marker가 맞물리면 BOCD alarm의 설명력이 높다.

### Drift 후보 판단 기준

Change point probability가 높고, run length posterior가 reset되며, stream trend에서 같은 시점의 수준 변화가 보이면 BOCD 기반 drift 후보로 해석한다.

단, BOCD는 hazard rate, predictive probability model, prior, 관측 noise 가정에 민감하다. Hazard rate가 높으면 change point 후보가 과도하게 자주 발생할 수 있고, predictive model이 실제 stream 분포와 맞지 않으면 posterior가 왜곡될 수 있다.

### 이 예시 차트의 해석

이 예시에서는 peak change point probability가 `0.87`, primary change point가 `t=18`, run length 상태가 `reset`으로 표시되어 있다.

패널별로는 다음처럼 읽는다.

```text
Change Point Probability Heatmap
  - x축은 time index, 색 강도는 해당 시점이 change point일 posterior probability를 뜻한다.
  - t=18에서 가장 진한 posterior spike가 나타나며 probability가 0.87까지 올라간다.
  - t=27 부근에도 보조 peak가 있으므로 한 번의 변화만이 아니라 추가 segment 변화 가능성도 본다.

Run Length Posterior
  - run length는 현재 segment가 얼마나 오래 이어졌는지에 대한 posterior 분포다.
  - t=18에서 posterior mass가 낮은 run length로 이동하면 이전 segment가 끝나고 새 segment가 시작됐다는 신호다.
  - change point probability peak와 run length reset이 같은 시점에 맞아야 BOCD 변화점 후보로 볼 수 있다.

Stream Trend
  - 관측 stream 값은 t=1~17에서 0.48~0.66 범위에 있고 평균선은 약 0.55 수준이다.
  - t=18 이후 값이 0.79, 0.83, 0.86대로 올라가며 평균선이 0.87 수준으로 이동한다.
  - t=27 이후에는 1.04, 1.07, 1.10 이상으로 한 단계 더 상승해 평균선이 1.10 수준으로 이동한다.
```

따라서 이 예시는 online Bayesian posterior가 stream의 segment 변화를 포착한 drift 후보로 해석할 수 있다. 다만 t=18과 t=27의 변화가 어떤 feature, source, 정책, 계절성, 데이터 품질 문제 때문인지는 이 차트만으로 확정하지 않는다.

보고서 문장 예시는 다음과 같다.

```text
BOCD 결과 change point probability는 t=18에서 0.87로 가장 높게 나타났다.
같은 시점에서 run length posterior가 reset되었고,
stream trend도 t=18 이후 평균 수준이 상승했다.
이는 Bayesian online change point posterior와 실제 stream 변화가 일치한 drift 후보로 해석할 수 있다.
```

### 금지해야 할 해석

이 차트만으로 다음을 단정하지 않는다.

```text
금지 1
  - posterior peak 하나만으로 운영 원인을 확정한다.

금지 2
  - hazard rate와 predictive model 설정을 확인하지 않고 민감도를 평가한다.

금지 3
  - run length posterior reset 없이 change point probability만 해석한다.

금지 4
  - BOCD change point를 곧바로 모델 성능 저하로 단정한다.
```

BOCD는 stream segment 변화 시점을 추정한다. 원인 feature, 성능 영향, 재학습 필요 여부는 별도 분석이 필요하다.

### 추가 확인 항목

BOCD drift 후보가 나타나면 다음을 추가 확인한다.

- hazard rate 또는 hazard function 설정
- predictive probability model과 likelihood 가정
- prior와 초기 run length 분포
- posterior peak threshold와 false alarm 기준
- change point 전후 segment의 feature/source/time 구성 변화
- ADWIN, Page-Hinkley, CUSUM 등 다른 stream detector와의 합의 여부
- label 확보 후 성능 지표, error rate, calibration 변화

### 적합한 사용 대상

이 chart는 다음 method variant에 적합하다.

- `BOCD / BAYESIAN_ONLINE_CHANGE_POINT_GAUSSIAN`
- `BOCD / BOCD_HAZARD_RATE_VARIANT`
- `BOCD / BOCD_PREDICTIVE_PROBABILITY`
