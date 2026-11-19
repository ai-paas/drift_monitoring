# Control Chart Interpretation Guide

## CHART-CTRL-001: 누적 편차로 확인하는 상방 평균 이동 경보

![CHART-CTRL-001](../charts/output/CHART-CTRL-001.png)

### 제목

누적 편차로 확인하는 상방 평균 이동 경보

### 차트 목적

이 chart는 CUSUM이 기준 평균 대비 작은 편차를 누적해 평균 shift를 감지하는 과정을 설명한다.

CUSUM은 단일 시점의 큰 변화보다, 기준선보다 조금 높은 값 또는 낮은 값이 반복될 때 빠르게 반응한다. 상방 CUSUM `C+`는 증가 방향 shift를, 하방 CUSUM `C-`는 감소 방향 shift를 설명한다.

이 차트는 다음 질문에 답한다.

```text
1. raw metric이 target mean 대비 한 방향으로 누적 이탈하는가?
2. C+ 또는 C- 중 어느 방향의 CUSUM이 control limit을 넘는가?
3. alarm이 일시적 spike가 아니라 누적 편차에 의해 발생했는가?
```

### 현재 상황 요약

현재 상황은 운영 metric이 target mean `0.53` 근처에서 시작했지만 중반 이후 계속 위쪽으로 이동하고, CUSUM이 이 작은 상방 편차들을 누적해 alarm을 낸 사례다. 좌측 raw metric은 t=16부터 `0.60` 이상으로 올라가고 t=25에는 `0.76` 수준에서 alarm marker가 표시된다. 우측 상단에서는 C+가 control limit `25`를 넘어 최종 `52.9`까지 증가하지만 C-는 `0.1` 수준에 머문다. 따라서 이 예시는 일시적인 spike가 아니라 기준선보다 높은 값이 반복되며 누적된 상방 평균 이동 후보로 해석한다.

### 차트 구성

이 chart는 세 영역으로 구성된다.

```text
좌측
  - raw metric trend
  - target mean
  - CUSUM alarm marker

우측 상단
  - positive CUSUM C+
  - negative CUSUM C-
  - control limit

우측 하단
  - C+ / C- 방향성 요약
  - 지배적인 shift 방향
```

상단 요약 영역에는 C+ max, C- max, raw metric shift를 표시한다.

### 해석 순서

먼저 좌측 raw metric trend에서 target mean보다 지속적으로 높은지 또는 낮은지 확인한다.

```text
target 주변에서 무작위로 흔들린다
  -> CUSUM drift 신호가 약하다.

target보다 조금 높은 값이 반복된다
  -> C+ 누적 증가를 확인한다.

target보다 조금 낮은 값이 반복된다
  -> C- 누적 증가를 확인한다.
```

그 다음 우측 상단 CUSUM control chart에서 C+ 또는 C-가 control limit을 넘는지 본다. C+가 넘으면 상방 평균 shift, C-가 넘으면 하방 평균 shift 후보로 해석한다.

마지막으로 우측 하단 방향성 요약에서 어느 방향의 누적 편차가 지배적인지 확인한다.

### Drift 후보 판단 기준

raw metric이 target mean 대비 한 방향으로 지속적으로 이탈하고, 해당 방향의 CUSUM이 control limit을 넘으며, 방향성 요약에서 C+ 또는 C-가 명확히 지배적이면 CUSUM drift 후보로 해석한다.

단, CUSUM은 target mean, allowance `k`, decision interval `h` 설정에 민감하다. target이 오래되었거나 seasonality가 있으면 false alarm이 늘 수 있다.

### 이 예시 차트의 해석

이 예시에서는 C+ max가 `52.9`, C- max가 `0.1`, shift가 `+0.29`로 표시되어 있다. 좌측 raw metric은 target `0.53`보다 지속적으로 높은 방향으로 이동하고, 25번 시점에서 상방 alarm이 표시된다.

패널별로는 다음처럼 읽는다.

```text
Raw Metric Trend
  - x축은 time index, y축은 관측 metric 값이다.
  - t=1~15에서는 metric이 0.49~0.58 범위에서 target 0.53 주변에 있다.
  - t=16 이후 0.60, 0.62, 0.67, 0.72처럼 target 위쪽 값이 반복되고 t=25에서 alarm marker가 나타난다.

CUSUM Control Chart
  - C+는 target보다 높은 편차를 누적한 상방 CUSUM이고, C-는 낮은 편차를 누적한 하방 CUSUM이다.
  - C+는 t=24~25 부근에서 control limit 25를 넘고 최종 52.9까지 증가한다.
  - C-는 최대 0.1에 머물러 하방 평균 이동 증거는 거의 없다.

Direction Summary
  - C+ 막대가 C- 막대보다 압도적으로 크다.
  - 방향성은 하방이 아니라 상방 평균 이동으로 읽어야 한다.
```

따라서 이 예시는 raw metric의 평균이 위쪽으로 이동한 상방 CUSUM drift 후보로 해석할 수 있다. 다만 CUSUM alarm은 평균 이동 시점을 알려주는 신호이지, 어떤 source나 feature가 원인인지 또는 모델 성능이 떨어졌는지를 직접 설명하지 않는다.

보고서 문장 예시는 다음과 같다.

```text
CUSUM으로 raw metric을 모니터링한 결과,
C+ 누적 편차가 52.9까지 증가해 control limit 25를 초과했다.
반면 C-는 0.1 수준으로 낮아 하방 변화 신호는 약했다.
Raw metric도 target mean 0.53 대비 지속적으로 높은 수준을 보여,
상방 평균 shift 기반 drift 후보로 해석할 수 있다.
```

### 금지해야 할 해석

이 차트만으로 다음을 단정하지 않는다.

```text
금지 1
  - CUSUM alarm만으로 drift 원인을 특정 source로 단정한다.

금지 2
  - target mean, k, h 설정을 확인하지 않고 alarm 민감도를 평가한다.

금지 3
  - seasonality 또는 운영 주기 변화를 배제하지 않는다.

금지 4
  - 평균 shift가 곧바로 모델 성능 저하를 의미한다고 말한다.
```

CUSUM은 누적 평균 shift 감지에 강하지만, 분포 형태나 tail 변화는 별도 chart로 확인해야 한다.

### 추가 확인 항목

CUSUM drift 후보가 나타나면 다음을 추가 확인한다.

- target mean 산정 기간과 최신성
- allowance `k`, decision interval `h`, reset 방식
- one-sided 또는 two-sided 설정
- seasonality, 주기성, 배치 처리 변화
- ADWIN, Page-Hinkley, EWMA 등 다른 control chart와의 합의 여부
- label 확보 후 성능 지표, error rate, calibration 변화

### 적합한 사용 대상

이 chart는 다음 method variant에 적합하다.

- `CUSUM / ONE_SIDED_UPPER_CUSUM`
- `CUSUM / ONE_SIDED_LOWER_CUSUM`
- `CUSUM / TWO_SIDED_CUSUM`
- `CUSUM / CUSUM_ON_DISTANCE_STREAM`

## CHART-CTRL-002: EWMA 평활화로 확인하는 점진적 상방 평균 이동

![CHART-CTRL-002](../charts/output/CHART-CTRL-002.png)

### 제목

EWMA 평활화로 확인하는 점진적 상방 평균 이동

### 차트 목적

이 chart는 EWMA 또는 Geometric Moving Average가 noisy metric에서 작은 평균 변화를 어떻게 부드럽게 감지하는지 설명한다.

EWMA/GMA는 최근 관측값에 더 큰 가중치를 주고 과거 관측값의 영향은 점차 줄인다. 따라서 raw metric이 noisy하더라도 smoothed average가 지속적으로 UCL 또는 LCL 방향으로 이동하면 평균 drift 후보를 빠르게 파악할 수 있다.

이 차트는 다음 질문에 답한다.

```text
1. raw metric의 noise 속에서 smoothed average가 어느 방향으로 이동하는가?
2. EWMA/GMA 값이 UCL 또는 LCL을 넘는가?
3. warning 상태가 alarm 상태로 이어지는가?
```

### 현재 상황 요약

현재 상황은 운영 metric이 단일 시점 spike로 튄 것이 아니라, noisy한 관측값 속에서 평균 수준이 점진적으로 위쪽으로 이동한 사례다. 좌측 패널의 raw metric은 t=1~15에는 대체로 `0.48~0.57` 범위에 있지만 t=16 이후 `0.59`, `0.63`, `0.68`, `0.73`처럼 높은 값이 반복된다. EWMA는 lambda `0.20`으로 이 변화를 부드럽게 따라가며 t=27 부근에서 UCL `0.72`를 넘고 final `0.80`까지 상승한다. 우측 하단 timeline도 normal에서 warning을 거쳐 alarm으로 이어지므로, 이 예시는 noisy metric의 점진적 상방 평균 이동 후보로 해석한다.

### 차트 구성

이 chart는 세 영역으로 구성된다.

```text
좌측
  - raw metric trend
  - EWMA/GMA smoothed average
  - center line
  - alarm marker

우측 상단
  - EWMA/GMA control chart
  - UCL, LCL, center line

우측 하단
  - normal/warning/alarm state timeline
  - alarm marker
```

상단 요약 영역에는 EWMA final, lambda, shift를 표시한다.

### 해석 순서

먼저 좌측 raw metric과 smoothed average를 함께 본다.

```text
raw metric만 튀고 EWMA가 안정적이다
  -> 일시적 noise 또는 outlier일 가능성이 높다.

EWMA가 점진적으로 UCL 방향으로 이동한다
  -> 상방 평균 shift 후보로 본다.

EWMA가 점진적으로 LCL 방향으로 이동한다
  -> 하방 평균 shift 후보로 본다.
```

그 다음 우측 상단 control chart에서 EWMA/GMA 값이 UCL 또는 LCL을 넘는지 확인한다. UCL 초과는 상방 drift 후보, LCL 미만은 하방 drift 후보로 해석한다.

마지막으로 우측 하단 timeline에서 warning 상태가 alarm 상태로 이어지는지 확인한다. Alarm 직전 warning 구간이 있으면 점진적 변화 가능성이 높다.

### Drift 후보 판단 기준

EWMA/GMA smoothed average가 UCL 또는 LCL을 넘고, raw metric도 같은 방향의 수준 변화를 보이며, timeline에서 warning 이후 alarm 상태가 나타나면 smoothing control chart 기반 drift 후보로 해석한다.

단, EWMA/GMA는 lambda, control limit 산정 방식, baseline replay threshold 설정에 민감하다. lambda가 크면 raw metric에 민감하고, 작으면 변화 감지가 늦어질 수 있다.

### 이 예시 차트의 해석

이 예시에서는 EWMA final이 `0.80`, lambda가 `0.20`, shift가 `+0.30`으로 표시되어 있다. 좌측 패널에서 raw metric은 noisy하지만 전반적으로 상승하고, EWMA는 이를 부드럽게 따라가며 상방으로 이동한다.

패널별로는 다음처럼 읽는다.

```text
Raw Metric + Smoothed Average
  - raw metric은 매 시점의 관측값이고, EWMA는 최근 값에 가중치를 더 둔 평활화 평균이다.
  - t=1~15 구간에서는 raw metric이 0.48~0.57 범위에서 흔들리고 EWMA도 0.50~0.55 수준에 머문다.
  - t=16 이후 raw metric이 0.59, 0.61, 0.68, 0.73, 0.80처럼 위쪽 값으로 이동하면서 EWMA도 0.56에서 0.80까지 올라간다.

EWMA Control Chart
  - center line은 0.50, UCL은 0.72, LCL은 0.28이다.
  - EWMA는 t=27 부근부터 UCL 0.72 이상으로 표시되고 final 값은 0.80이다.
  - LCL 방향 변화는 없으므로 하방 drift가 아니라 상방 평균 이동 후보로 읽는다.

Alarm Timeline
  - t=1~20은 normal, t=21~26은 warning, t=27 이후는 alarm 상태로 표시된다.
  - warning 구간을 거쳐 alarm으로 넘어가므로 일시적 spike보다 누적된 평균 이동 가능성이 높다.
```

따라서 이 예시는 noisy metric의 상방 평균 shift를 EWMA가 감지한 drift 후보로 해석할 수 있다. 다만 EWMA alarm은 평활화 평균의 control limit 초과 신호이며, drift 원인이나 모델 성능 저하 여부는 별도 분석으로 확인해야 한다.

보고서 문장 예시는 다음과 같다.

```text
EWMA control chart로 raw metric을 모니터링한 결과,
EWMA final 값은 0.80으로 UCL 0.72를 초과했다.
Raw metric은 noisy하지만 전반적으로 상승했고,
EWMA smoothing 결과도 같은 방향의 지속적 이동을 보였다.
이는 noisy metric의 상방 평균 drift 후보로 해석할 수 있다.
```

### 금지해야 할 해석

이 차트만으로 다음을 단정하지 않는다.

```text
금지 1
  - raw metric spike 하나만으로 EWMA drift를 단정한다.

금지 2
  - lambda와 control limit 산정 방식을 확인하지 않고 민감도를 평가한다.

금지 3
  - baseline 기간이 현재 운영 조건과 같은지 확인하지 않는다.

금지 4
  - EWMA alarm이 곧바로 모델 성능 저하를 의미한다고 말한다.
```

EWMA/GMA는 평균 수준 변화를 smoothing해서 감지한다. 분산 변화, tail 변화, population mix 변화는 별도 chart와 함께 확인해야 한다.

### 추가 확인 항목

EWMA/GMA drift 후보가 나타나면 다음을 추가 확인한다.

- lambda 또는 geometric decay 설정
- UCL/LCL 산정 방식과 baseline 기간
- one-sided 또는 two-sided control chart 설정
- seasonality, 주기성, batch 처리 변화
- CUSUM, Page-Hinkley, ADWIN 등 다른 detector와의 합의 여부
- label 확보 후 성능 지표, error rate, calibration 변화

### 적합한 사용 대상

이 chart는 다음 method variant에 적합하다.

- `EWMA / EWMA_UNIVARIATE_CONTROL_CHART`
- `EWMA / EWMA_ONE_SIDED`
- `EWMA / EWMA_BASELINE_REPLAY_THRESHOLD`
- `Geometric Moving Average / GMA_CONTROL_CHART`
- `Geometric Moving Average / GMA_ONE_SIDED`
- `Geometric Moving Average / GMA_WITH_EMPIRICAL_LIMIT`

## CHART-CTRL-003: MEWMA로 확인하는 여러 지표의 동시 상승 경보

![CHART-CTRL-003](../charts/output/CHART-CTRL-003.png)

### 제목

MEWMA로 확인하는 여러 지표의 동시 상승 경보

### 차트 목적

이 chart는 MEWMA가 여러 metric을 동시에 smoothing한 뒤 하나의 multivariate statistic으로 control limit 초과를 감지하는 방식을 설명한다.

MEWMA는 개별 metric 하나만 보는 control chart가 아니라 metric vector의 공동 이동을 추적한다. 따라서 단일 metric의 변화가 약하더라도 여러 metric이 같은 기간에 함께 이동하면 MEWMA statistic이 상승할 수 있다.

이 차트는 다음 질문에 답한다.

```text
1. MEWMA statistic이 UCL을 넘는가?
2. alarm 시점에 어떤 metric이 statistic 상승에 가장 크게 기여했는가?
3. small multiples에서 여러 metric이 같은 기간에 함께 이동하는가?
```

### 현재 상황 요약

현재 상황은 단일 지표 하나가 튄 것이 아니라 여러 운영 metric이 같은 기간에 함께 위쪽으로 움직이면서 MEWMA 다변량 statistic이 control limit을 넘은 사례다. 좌측 control chart에서 MEWMA statistic은 초반 `3.1~8.0` 수준에서 점진적으로 올라가 t=23 부근에 UCL `12.0`을 넘고 final `19.1`까지 상승한다. 우측 contribution bar는 alarm 시점의 기여가 `risk_score` 38%, `amount` 24%, `frequency` 18%에 집중되어 있음을 보여준다. 우측 하단 small multiples에서도 세 지표가 같은 구간에서 함께 상승하므로, 이 예시는 여러 metric vector의 공동 이동에 의한 다변량 drift 후보로 해석한다.

### 차트 구성

이 chart는 세 영역으로 구성된다.

```text
좌측
  - MEWMA statistic trend
  - UCL
  - alarm marker

우측 상단
  - alarm 시점의 metric contribution bar
  - top contributing metric

우측 하단
  - 주요 metric별 small multiples
  - alarm 구간의 time-aligned movement
```

상단 요약 영역에는 MEWMA final, UCL, top metric을 표시한다.

### 해석 순서

먼저 좌측 control chart에서 MEWMA statistic의 흐름을 확인한다.

```text
MEWMA statistic이 UCL 아래에서 안정적이다
  -> 다변량 평균 vector의 변화 증거가 약하다.

MEWMA statistic이 점진적으로 상승한 뒤 UCL을 넘는다
  -> 여러 metric의 누적 이동에 의한 drift 후보로 본다.

MEWMA statistic이 급격히 튄 뒤 바로 회복한다
  -> 일시적 multivariate outlier 가능성을 먼저 확인한다.
```

그 다음 우측 상단 contribution bar를 확인한다. 특정 metric의 contribution이 지나치게 크면 그 metric이 alarm의 주된 원인일 수 있다.

마지막으로 우측 하단 small multiples에서 여러 metric이 같은 시점에 같은 방향으로 이동하는지 본다. Contribution이 큰 metric과 small multiples의 변동 시점이 일치하면 alarm 원인을 더 구체적으로 설명할 수 있다.

### Drift 후보 판단 기준

MEWMA statistic이 UCL을 넘고, contribution bar에서 하나 이상의 metric이 alarm을 설명하며, small multiples에서도 같은 기간의 동시 이동이 보이면 다변량 smoothing control chart 기반 drift 후보로 해석한다.

단, MEWMA는 metric scaling, covariance 추정, smoothing parameter, Mahalanobis D2 사용 여부에 민감하다. Metric scale이 맞지 않으면 특정 metric의 기여도가 과대 표시될 수 있다.

### 이 예시 차트의 해석

이 예시에서는 MEWMA final이 `19.1`, UCL이 `12.0`, top metric이 `risk_score`로 표시되어 있다. 좌측 control chart에서 MEWMA statistic은 점진적으로 상승하다가 23번째 index 부근에서 UCL을 넘는다.

패널별로는 다음처럼 읽는다.

```text
MEWMA Statistic Control Chart
  - x축은 time index, y축은 smoothing된 multivariate statistic이다.
  - statistic은 t=1의 3.1에서 시작해 t=16에는 8.0, t=23에는 12.6으로 올라간다.
  - UCL 12.0을 t=23 부근에서 넘고 final 19.1까지 계속 상승하므로 alarm 이후에도 변화가 유지되는지 본다.

Metric Contribution
  - alarm statistic 상승에 어떤 metric이 많이 기여했는지 비율로 보여준다.
  - risk_score가 38%로 가장 크고 amount 24%, frequency 18%가 뒤따른다.
  - latency 12%, region_mix 8%도 일부 기여하지만 주된 설명 축은 risk_score, amount, frequency다.

Multivariate Small Multiples
  - risk_score, amount, frequency를 같은 시간 축에 나란히 보여준다.
  - 세 지표가 모두 후반 구간에서 올라가므로 단일 지표 spike보다 공동 이동 가능성이 크다.
  - contribution이 큰 지표와 small multiples의 상승 시점이 맞는지 함께 확인한다.
```

따라서 이 예시는 단일 metric spike가 아니라 여러 metric의 공동 이동으로 인한 다변량 drift 후보로 해석할 수 있다. 다만 contribution은 원인 확정이 아니라 alarm 설명을 돕는 분해 결과이므로, scaling, covariance 추정, segment 구성 변화를 함께 확인해야 한다.

보고서 문장 예시는 다음과 같다.

```text
MEWMA control chart에서 multivariate statistic은 19.1로 UCL 12.0을 초과했다.
Alarm contribution은 risk_score 38%, amount 24%, frequency 18% 순으로 집중되었고,
small multiples에서도 동일 구간의 동시 상승이 확인되었다.
이는 여러 metric의 공동 이동에 의한 다변량 smoothing drift 후보로 해석할 수 있다.
```

### 금지해야 할 해석

이 차트만으로 다음을 단정하지 않는다.

```text
금지 1
  - top contribution metric 하나만 drift 원인이라고 단정한다.

금지 2
  - metric scaling과 covariance 추정 방식을 확인하지 않고 contribution을 비교한다.

금지 3
  - MEWMA alarm을 개별 metric control chart alarm과 같은 의미로 해석한다.

금지 4
  - Mahalanobis D2 기반 statistic인지 확인하지 않고 거리 크기를 비교한다.
```

MEWMA는 다변량 평균 vector의 이동을 요약한다. 개별 metric의 분산 변화, tail 변화, category mix 변화는 별도 chart와 함께 확인해야 한다.

### 추가 확인 항목

MEWMA drift 후보가 나타나면 다음을 추가 확인한다.

- metric standardization 또는 normalization 방식
- covariance matrix 산정 기간과 regularization 여부
- smoothing parameter와 control limit 산정 방식
- Mahalanobis D2 사용 여부
- top contribution metric의 원자료 trend와 업무 이벤트
- 단변량 control chart, PSI, Wasserstein, energy distance 등 다른 detector와의 합의 여부
- label 확보 후 성능 지표, calibration, error rate 변화

### 적합한 사용 대상

이 chart는 다음 method variant에 적합하다.

- `MEWMA / MEWMA_STANDARD`
- `MEWMA / MEWMA_WITH_MAHALANOBIS_D2`
