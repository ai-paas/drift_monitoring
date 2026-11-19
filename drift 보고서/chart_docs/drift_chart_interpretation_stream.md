# Stream Chart Interpretation Guide

## CHART-STREAM-001: ADWIN 경보 이후 스트림 평균 상승과 윈도 축소

![CHART-STREAM-001](../charts/output/CHART-STREAM-001.png)

### 제목

ADWIN 경보 이후 스트림 평균 상승과 윈도 축소

### 차트 목적

이 chart는 ADWIN이 stream에서 평균 상승을 감지한 시점과, 그 직후 adaptive window가 어떻게 축소되는지를 함께 설명한다.

ADWIN은 고정 window가 아니라 현재 stream을 유지하다가, window 내부의 과거 구간과 최근 구간 평균 차이가 통계적으로 커지면 오래된 구간을 버리고 drift alarm을 낸다. 따라서 이 chart는 stream metric이 언제 새 수준으로 올라갔는지, 그리고 detector가 그 변화에 맞춰 window를 어떻게 재구성했는지 읽는 데 사용한다.

### 현재 상황 요약

이 예시에서는 stream metric이 초반 0.31~0.40 근처에서 움직이다가 23번 시점 전후로 빠르게 상승한다. ADWIN은 time index `23`에서 drift alarm을 표시하고, 상단 요약에는 mean delta `+0.30`, p-value `0.009`가 함께 나온다. 경보 직후 adaptive window width가 `170`에서 `62`로 줄어 오래된 구간을 버린 뒤, metric은 0.68 이상 새 수준에서 안정된다.

이 차트가 답하는 질문은 다음과 같다.

```text
1. stream metric이 어느 시점부터 이전 평균보다 높은 수준으로 이동했는가?
2. ADWIN alarm 직후 adaptive window width가 실제로 축소되었는가?
3. alarm 전후 평균 차이 +0.30이 운영 기준 delta 0.20보다 충분히 큰가?
```

### 차트 구성

이 chart는 세 영역으로 구성된다. 좌측은 stream metric과 rolling mean, ADWIN alarm marker를 함께 보여준다. 우측 상단은 adaptive window width가 alarm 직후 `170`에서 `62`로 줄어드는 흐름을 보여주고, 우측 하단은 alarm 전 평균 `0.38`과 alarm 후 평균 `0.68`의 차이를 운영 기준 `0.20`과 비교한다.

### 패널별 확인

좌측 큰 패널은 stream metric과 rolling mean을 time index 축에서 함께 보여준다. 이 예시에서는 t=1~20 구간의 metric이 대체로 `0.31~0.43`에 머물다가, t=23의 ADWIN alarm 이후 `0.56`, `0.61`, `0.65`, `0.68`처럼 올라간다. rolling mean도 t=23 전후 `0.46`에서 이후 `0.64~0.76`까지 상승하므로, 단일 spike보다는 평균 수준 이동을 먼저 의심한다.

우측 상단 패널은 adaptive window width가 경보 전후 어떻게 바뀌는지 보여준다. width는 alarm 직전 `170`까지 넓어졌다가 t=23 직후 `62`로 급격히 줄고, 이후 `70`, `78`, `86`처럼 다시 확장된다. ADWIN이 평균 차이가 커진 오래된 구간을 버리고 새 구간 중심으로 윈도를 재구성한 흐름으로 읽는다.

우측 하단 패널은 alarm 전후 window 평균과 차이를 비교한다. alarm 전 평균은 `0.38`, alarm 후 평균은 `0.68`이며 delta는 `+0.30`이다. 기준선으로 표시된 운영 기준 `0.20`보다 delta가 크기 때문에, 평균 상승 폭이 단순 변동보다 큰지 판단하는 근거가 된다.

패널들을 함께 읽을 때는 alarm marker 하나만 보지 않는다. 좌측의 평균 상승, 우측 상단의 window 축소, 우측 하단의 delta `+0.30`과 p-value `0.009`가 같은 방향일 때 ADWIN 기반 stream drift 후보로 해석한다.

```text
alarm 이후 값이 이전 수준으로 곧 돌아온다
  -> 일시적 spike 또는 noise 가능성을 확인한다.

alarm 이후 새 평균 수준에서 안정된다
  -> stream drift 후보로 해석한다.

alarm이 여러 번 반복된다
  -> gradual drift 또는 recurring drift 가능성을 확인한다.
```

이 차트만으로 평균 상승의 원인이나 모델 성능 저하를 확정하지 않는다. alarm 시점 주변의 지연 적재, batch 크기 변화, outlier burst, smoothing 설정을 함께 확인해야 한다.

### 이 예시 차트의 해석

이 예시에서는 alarm index가 `23`, mean delta가 `+0.30`, p-value가 `0.009`로 표시되어 있다. 좌측 stream line에서는 23번 시점 주변부터 metric이 이전 평균 수준보다 높아지고 이후 `0.68~0.78` 범위의 새 수준에서 안정된다.

우측 상단에서는 alarm 직후 adaptive window width가 `170` 수준에서 `62` 수준으로 줄었다가 다시 확장된다. 우측 하단에서는 alarm 전 평균 `0.38`과 alarm 후 평균 `0.68`의 차이가 `0.30`으로 운영 기준 `0.20`을 넘는다. 따라서 이 예시는 ADWIN이 stream 평균 상승을 감지한 drift 후보로 해석할 수 있다.

보고서 문장 예시는 다음과 같다.

```text
ADWIN으로 stream metric을 모니터링한 결과,
time index 23에서 drift alarm이 발생했다.
Alarm 전 window 평균은 0.38, alarm 후 평균은 0.68로 mean delta는 +0.30이었다.
Alarm 직후 adaptive window width가 크게 축소되었고 이후 metric이 새 수준에서 안정되어,
stream 평균 상승 drift 후보로 해석할 수 있다.
```

### 금지해야 할 해석

이 차트만으로 다음을 단정하지 않는다.

```text
금지 1
  - alarm 한 번만으로 장기 drift를 확정한다.

금지 2
  - stream metric 상승을 곧바로 모델 성능 악화로 단정한다.

금지 3
  - 데이터 지연 적재나 outlier burst 가능성을 확인하지 않는다.

금지 4
  - ADWIN window 축소를 데이터 손실로 해석한다.
```

ADWIN의 window 축소는 detector가 오래된 구간을 버리고 새 regime에 적응하는 동작이다. 운영 데이터 삭제나 원천 데이터 손실을 의미하지 않는다.

### 추가 확인 항목

ADWIN drift 후보가 나타나면 다음을 추가 확인한다.

- alarm 시점 주변의 데이터 적재 지연, 누락, batch 크기 변화
- metric smoothing, aggregation interval, stream ordering 변경 여부
- alarm 전후 segment/source/time 구성 변화
- ADWIN delta, min window length, clock 설정
- KSWIN, Page-Hinkley, DDM 계열 detector와의 합의 여부
- label 확보 후 성능 지표, error rate, calibration 변화

### 적합한 사용 대상

이 chart는 다음 method variant에 적합하다.

- `ADWIN / ADWIN_MEAN_STREAM`
- `ADWIN / ADWIN_ERROR_RATE`
- `ADWIN / ADWIN_DISTANCE_STREAM`

## CHART-STREAM-002: 최근 윈도 분포 이동과 KSWIN 경보

![CHART-STREAM-002](../charts/output/CHART-STREAM-002.png)

### 제목

최근 윈도 분포 이동과 KSWIN 경보

### 차트 목적

이 chart는 KSWIN이 stream에서 과거 window와 최근 window의 분포 차이를 어떻게 감지했는지 설명한다.

KSWIN은 sliding window 안에서 과거 sample과 최근 sample을 나누고, 두 sample의 경험 CDF 차이를 KS statistic으로 계산한다. 따라서 평균만 달라지는 변화뿐 아니라 분포 위치, scale, shape 변화가 stream에서 발생했는지 확인하는 데 적합하다.

이 예시 차트가 답하는 질문은 다음과 같다.

```text
1. 과거 window와 최근 window가 stream의 어느 구간을 비교하는가?
2. 최근 window의 값 분포가 과거 window보다 높은 쪽으로 이동했는가?
3. ECDF 최대 차이와 KS statistic이 threshold 초과를 함께 지지하는가?
```

### 현재 상황 요약

이 예시에서는 stream metric이 초반 `0.28~0.45` 수준에서 움직이다가 24번 이후 `0.52`, `0.57`, `0.61`, `0.67`처럼 높아진다. KSWIN은 과거 window `10~20`과 최근 window `24~34`를 비교하고, alarm index `28`에서 KS statistic `0.55`, p-value `0.011`을 표시한다.

우측 ECDF 비교에서는 최근 window의 CDF가 과거 window보다 오른쪽으로 이동해 있으며, x≈`0.51` 부근에서 최대 차이 `D=0.55`가 나타난다. 우측 하단에서도 KS statistic이 `0.12`에서 `0.55`까지 상승하고, 최근 비교 시점에서 threshold `0.36`을 넘는다. 따라서 이 예시는 최근 stream window의 분포가 과거 window 대비 높은 값 쪽으로 이동한 KSWIN drift 후보로 읽는다.

### 차트 구성

이 chart는 세 영역으로 구성된다.

```text
좌측
  - stream metric line
  - 과거 sliding window 영역
  - 최근 sliding window 영역
  - KSWIN alarm marker

우측 상단
  - 과거 window sample의 ECDF
  - 최근 window sample의 ECDF
  - 최대 CDF 차이 D

우측 하단
  - window 비교 시점별 KS statistic 추세
  - alarm threshold
```

상단 요약 영역에는 KS statistic, p-value, alarm index를 표시한다.

### 패널별 확인

좌측 큰 패널은 stream metric을 time index 축에서 보여주고, KSWIN이 비교하는 두 sliding window를 음영으로 표시한다. 과거 window는 `10~20` 구간으로 대체로 `0.34~0.42` 수준에 놓이고, 최근 window는 `24~34` 구간으로 `0.52~0.74`까지 높아진 구간을 포함한다. alarm marker는 index `28`에 찍혀 있으며, 이 시점의 stream 값은 `0.67`이다. 따라서 좌측 패널에서는 두 window가 같은 수준의 변동을 보는 것이 아니라, 상승 전 구간과 상승 후 구간을 비교한다는 점을 먼저 확인한다.

우측 상단 패널은 과거 window sample과 최근 window sample의 ECDF를 비교한다. 과거 window ECDF는 낮은 값 구간에서 빠르게 1.0에 가까워지지만, 최근 window ECDF는 같은 x값에서 더 낮게 머문다. 예를 들어 x=`0.50` 부근에서 과거 CDF는 `0.92`, 최근 CDF는 `0.24`로 벌어지고, 차트에는 x≈`0.51` 부근의 최대 차이 `D=0.55`가 표시된다. 이는 최근 sample이 과거 sample보다 큰 값 쪽에 더 많이 분포한다는 뜻이다.

우측 하단 패널은 window 비교가 진행되면서 KS statistic이 어떻게 변하는지 보여준다. KS statistic은 `0.12`, `0.14`, `0.16`처럼 낮게 시작해 후반에는 `0.39`, `0.48`, `0.55`로 올라간다. threshold는 `0.36`이며, 최근 세 비교 시점이 threshold 위에 표시된다. 단일 비교 한 번만 튄 것이 아니라 최근 비교 구간에서 통계량이 threshold를 넘고 증가했다는 점이 drift 후보 판단을 보강한다.

패널들을 함께 읽을 때는 alarm marker 하나만 보지 않는다. 좌측의 최근 window 상승 구간, 우측 상단의 ECDF 오른쪽 이동과 `D=0.55`, 우측 하단의 threshold `0.36` 초과가 같은 방향일 때 KSWIN 기반 stream 분포 이동 후보로 해석한다.

### Drift 후보 판단 기준

KS statistic이 threshold를 넘고 증가 추세를 보이며, ECDF 비교에서 과거/최근 window 사이의 최대 차이가 명확하고, 좌측 stream에서 최근 window가 다른 수준 또는 다른 분포 폭을 보이면 KSWIN stream drift 후보로 해석한다.

단, KSWIN은 window size, alpha, subsampling 방식에 민감하다. window가 너무 작으면 noise에 민감하고, 너무 크면 짧은 drift를 늦게 감지할 수 있다.

### 이 예시 차트의 해석

이 예시에서는 KS statistic이 `0.55`, p-value가 `0.011`, alarm index가 `28`로 표시되어 있다. 과거 window `10~20`은 stream 값이 `0.34~0.42` 수준인 구간이고, 최근 window `24~34`는 `0.52~0.74` 수준으로 올라간 구간이다.

우측 상단 ECDF 비교에서는 최근 window의 CDF가 과거 window보다 오른쪽으로 이동해 있으며 최대 차이 `D=0.55`가 나타난다. 우측 하단 KS statistic 추세에서도 최근 비교 시점에서 threshold `0.36`을 넘고 마지막 값이 `0.55`까지 상승한다. 따라서 이 예시는 stream 분포가 과거 window 대비 높은 값 쪽으로 이동한 KSWIN drift 후보로 해석할 수 있다.

보고서 문장 예시는 다음과 같다.

```text
KSWIN으로 stream metric을 모니터링한 결과,
alarm index 28에서 KS statistic은 0.55, p-value는 0.011로 나타났다.
과거 window 10~20은 0.34~0.42 수준에 머문 반면,
최근 window 24~34는 0.52~0.74 수준의 상승 구간을 포함했다.
ECDF 비교의 최대 차이 D=0.55와 KS statistic threshold 0.36 초과가 함께 나타나므로,
최근 stream 분포가 과거 구간보다 높은 값 쪽으로 이동한 drift 후보로 해석할 수 있다.
```

### 금지해야 할 해석

이 차트만으로 다음을 단정하지 않는다.

```text
금지 1
  - KS statistic 초과만으로 drift 원인을 특정 feature나 source로 단정한다.

금지 2
  - window size와 subsampling 설정을 확인하지 않고 민감도를 평가한다.

금지 3
  - stream ordering 오류나 batch 적재 영향 가능성을 배제한다.

금지 4
  - KSWIN alarm을 곧바로 모델 성능 저하로 해석한다.
```

KSWIN은 stream 분포 차이를 감지한다. 모델 영향은 label 확보 후 error rate, confidence, calibration 변화와 함께 확인해야 한다.

### 추가 확인 항목

KSWIN drift 후보가 나타나면 다음을 추가 확인한다.

- window size, stat size, alpha, subsampling 설정
- stream ordering, batch 적재, 지연 데이터 유입 여부
- alarm 전후 segment/source/time 구성 변화
- ADWIN, Page-Hinkley 등 다른 stream detector와의 합의 여부
- 최근 window의 outlier 또는 tail sample 증가 여부
- label 확보 후 성능 지표, error rate, calibration 변화

### 적합한 사용 대상

이 chart는 다음 method variant에 적합하다.

- `KSWIN / KSWIN_STANDARD`
- `KSWIN / KSWIN_WITH_SUBSAMPLING`
- `KSWIN / KSWIN_NUMERIC_STREAM`

## CHART-STREAM-003: Page-Hinkley 기반 스트림 평균 상승 경보

![CHART-STREAM-003](../charts/output/CHART-STREAM-003.png)

### 제목

Page-Hinkley 기반 스트림 평균 상승 경보

### 차트 목적

이 chart는 Page-Hinkley Test가 stream 평균 상승을 누적 편차로 감지하고, warning 상태가 drift 경보로 이어지는 과정을 설명한다.

Page-Hinkley는 관측값과 누적 평균 사이의 편차를 순차적으로 누적하고, 그 누적 통계량이 threshold를 넘으면 drift alarm을 발생시킨다. 따라서 갑작스러운 step change뿐 아니라 점진적으로 평균이 한 방향으로 이동하는 stream drift를 설명하는 데 적합하다.

이 예시 차트가 답하는 질문은 다음과 같다.

```text
1. stream metric이 어느 시점부터 이전 수준보다 계속 높아지는가?
2. Page-Hinkley statistic이 threshold 18.0을 언제 넘는가?
3. warning 상태가 drift alarm으로 이어지는 흐름이 실제로 나타나는가?
```

### 현재 상황 요약

이 예시에서는 stream metric이 초반 `0.42~0.53` 수준에서 천천히 움직이다가 t=20 이후 상승 속도가 커진다. 값은 t=20의 `0.53`에서 t=29의 `0.76`, 마지막 t=36의 `0.84`까지 올라가며, running mean도 `0.48`에서 `0.72`까지 뒤따라 상승한다.

Page-Hinkley statistic은 초반 `0.1~5.3` 수준에서 누적되다가 t=29에 `19.6`으로 threshold `18.0`을 처음 넘고, 최종 `25.5`까지 증가한다. 상태 timeline은 t=1~21 normal, t=22~28 warning, t=29~36 drift로 이어진다. 따라서 이 예시는 단기 spike가 아니라 평균이 점진적으로 올라가며 Page-Hinkley가 경보를 낸 stream drift 후보로 읽는다.

### 차트 구성

이 chart는 세 영역으로 구성된다.

```text
좌측
  - stream metric
  - running mean
  - Page-Hinkley alarm marker

우측 상단
  - Page-Hinkley statistic line
  - alarm threshold

우측 하단
  - normal/warning/drift state timeline
  - alarm marker
```

상단 요약 영역에는 PH statistic, threshold, alarm index를 표시한다.

### 패널별 확인

좌측 큰 패널은 stream metric과 running mean을 time index 축에서 함께 보여준다. 이 예시에서는 t=1~19 구간의 metric이 대체로 `0.40~0.52`에 머물고, t=20 이후 `0.53`, `0.55`, `0.57`, `0.60`, `0.63`처럼 연속적으로 상승한다. alarm marker가 있는 t=29의 값은 `0.76`이며, 마지막 t=36에서는 `0.84`까지 올라간다. running mean도 t=20의 `0.48`에서 t=29의 `0.62`, t=36의 `0.72`로 상승하므로 단일 outlier보다 평균 수준 이동을 먼저 본다.

우측 상단 패널은 Page-Hinkley statistic과 threshold를 비교한다. 통계량은 t=20까지 `5.3`으로 threshold `18.0`보다 낮지만, 이후 누적 속도가 커져 t=28에 `17.5`, t=29에 `19.6`으로 threshold를 넘는다. 최종 값은 `25.5`로 threshold보다 `7.5` 높다. 이 패널에서는 detector가 어느 시점에 누적 편차를 drift 증거로 충분하다고 판단했는지 확인한다.

우측 하단 패널은 상태 전환 순서를 보여준다. t=1~21은 normal, t=22~28은 warning, t=29~36은 drift로 표시된다. warning 구간이 먼저 나타난 뒤 t=29 drift marker와 함께 상태가 바뀌므로, 평균 상승이 점진적으로 누적되다가 경보로 확정된 흐름으로 읽는다.

패널들을 함께 읽을 때는 PH statistic 초과만 보지 않는다. 좌측의 metric 상승, running mean 상승, 우측 상단의 threshold `18.0` 초과, 우측 하단의 warning -> drift 전환이 같은 방향일 때 Page-Hinkley 기반 평균 상승 drift 후보로 해석한다.

### Drift 후보 판단 기준

raw stream이 한 방향으로 이동하고, Page-Hinkley statistic이 threshold를 넘으며, alarm timeline에서 warning 이후 drift 상태가 나타나면 평균 변화 기반 stream drift 후보로 해석한다.

단, Page-Hinkley는 delta, lambda, alpha 같은 민감도 설정에 영향을 받는다. 설정이 너무 민감하면 작은 trend에도 alarm이 발생하고, 너무 둔감하면 drift 감지가 늦어질 수 있다.

### 이 예시 차트의 해석

이 예시에서는 PH statistic이 `25.5`, threshold가 `18.0`, alarm index가 `29`로 표시되어 있다. 좌측 stream에서는 metric이 t=20의 `0.53` 이후 꾸준히 올라 t=29에는 `0.76`, t=36에는 `0.84`에 도달한다. running mean도 `0.48`에서 `0.72`까지 상승한다.

우측 상단 PH statistic은 t=28의 `17.5`까지 threshold 아래에 있다가 t=29의 `19.6`에서 threshold `18.0`을 넘고, 마지막에는 `25.5`까지 증가한다. 우측 하단 timeline에서는 t=22부터 warning 상태가 시작되고 t=29부터 drift 상태로 전환된다. 따라서 이 예시는 stream 평균이 점진적으로 상승한 Page-Hinkley drift 후보로 해석할 수 있다.

보고서 문장 예시는 다음과 같다.

```text
Page-Hinkley Test로 stream metric을 모니터링한 결과,
time index 29에서 PH statistic이 19.6으로 threshold 18.0을 처음 초과했다.
최종 PH statistic은 25.5였고, stream metric은 t=20의 0.53에서 t=36의 0.84까지 상승했다.
Running mean도 0.48에서 0.72로 올라갔으며, timeline은 t=22 warning 이후 t=29 drift 상태로 전환되었다.
이는 평균 상승 방향의 gradual stream drift 후보로 해석할 수 있다.
```

### 금지해야 할 해석

이 차트만으로 다음을 단정하지 않는다.

```text
금지 1
  - PH statistic 초과만으로 drift 원인을 특정 source로 단정한다.

금지 2
  - 민감도 파라미터를 확인하지 않고 alarm 품질을 평가한다.

금지 3
  - 단기 spike와 gradual mean shift를 구분하지 않는다.

금지 4
  - stream 평균 변화가 곧바로 모델 성능 저하를 의미한다고 말한다.
```

Page-Hinkley는 평균 변화 detector다. 분포 형태 변화, 분산 변화, error rate 변화는 별도 chart와 detector로 확인해야 한다.

### 추가 확인 항목

Page-Hinkley drift 후보가 나타나면 다음을 추가 확인한다.

- delta, lambda, alpha, min_instances 등 민감도 설정
- alarm 전후 stream ordering, batch 적재, 지연 데이터 유입 여부
- gradual drift인지 abrupt drift인지 구분
- ADWIN, KSWIN, CUSUM 등 다른 stream detector와의 합의 여부
- segment/source/time별 평균 변화 집중 여부
- label 확보 후 성능 지표, error rate, calibration 변화

### 적합한 사용 대상

이 chart는 다음 method variant에 적합하다.

- `Page-Hinkley Test / PAGE_HINKLEY_INCREASE`
- `Page-Hinkley Test / PAGE_HINKLEY_DECREASE`

## CHART-STREAM-004: SeqDrift 순차 검정의 스트림 상승 경보

![CHART-STREAM-004](../charts/output/CHART-STREAM-004.png)

### 제목

SeqDrift 순차 검정의 스트림 상승 경보

### 차트 목적

이 chart는 SeqDrift 계열 detector가 stream 값을 순차적으로 읽으면서 reference mean 대비 상승 증거가 decision bound를 넘는지 설명한다.

SeqDrift는 stream을 순차적으로 읽으면서 reference 구간 대비 현재 구간의 통계적 차이가 충분히 커졌는지 평가한다. 누적 evidence가 decision bound를 넘으면 drift alarm이 발생한다. 따라서 stream 변화가 시간 순서에 따라 점진적으로 쌓이는 상황을 설명하는 데 적합하다.

이 예시 차트가 답하는 질문은 다음과 같다.

```text
1. stream 값이 reference mean 대비 어느 방향으로 이동하는가?
2. sequential evidence가 decision bound를 넘어 drift alarm을 낸 시점은 언제인가?
3. warning 구간과 drift 구간이 몇 step의 탐지 지연으로 이어지는가?
```

### 현재 상황 요약

이 예시에서는 stream 값이 초반 `0.48~0.56` 수준에서 reference mean `0.53` 주변을 오가다가 t=20 이후 `0.58`, `0.60`, `0.62`, `0.65`처럼 연속 상승한다. SeqDrift는 t=22부터 warning 상태를 표시하고, t=27에서 drift alarm을 표시한다. Alarm 시점의 stream 값은 `0.75`이며, reference mean `0.53` 대비 delta는 `+0.34`로 표시된다.

우측 상단에서는 sequential evidence가 t=27의 `15.1`에서 decision bound `12.2`를 넘고, 마지막 t=36에는 `26.5`까지 증가한다. 우측 하단 timeline은 t=1~22 monitoring, t=22~27 warning, t=27~36 drift로 이어진다. 따라서 이 예시는 reference mean보다 높은 stream 수준이 누적되면서 SeqDrift가 4 step detect delay로 drift 후보를 낸 상황으로 읽는다.

### 차트 구성

이 chart는 세 영역으로 구성된다.

```text
좌측
  - stream value trend
  - reference mean
  - drift alarm marker

우측 상단
  - sequential evidence line
  - decision bound line

우측 하단
  - monitoring/warning/drift state timeline
  - alarm marker
```

상단 요약 영역에는 evidence, alarm index, detect delay를 표시한다.

### 패널별 확인

좌측 큰 패널은 stream value와 reference mean을 time index 축에서 함께 보여준다. 이 예시에서는 t=1~19 구간의 값이 대체로 `0.48~0.57` 범위에서 움직이고 reference mean `0.53` 주변에 머문다. t=20 이후에는 `0.58`, `0.60`, `0.62`, `0.65`, `0.68`처럼 상승이 이어지고, alarm marker가 찍힌 t=27의 값은 `0.75`다. 차트의 주석은 alarm 시점 delta를 `+0.34`로 표시하므로, 단일 spike보다 기준 평균 위로 누적되는 상승 흐름을 먼저 확인한다.

우측 상단 패널은 sequential evidence와 decision bound를 비교한다. Evidence는 초반 `0.0~4.8` 수준으로 bound 아래에 있다가 t=22부터 `6.8`, `8.1`, `9.7`, `11.4`, `13.2`처럼 빠르게 증가한다. t=27에서 evidence `15.1`이 bound `12.2`를 넘고, 이후 마지막 t=36에는 evidence `26.5`와 bound `14.0`으로 격차가 더 커진다. 이 패널에서는 순차 검정이 어느 시점부터 변화 증거를 충분하다고 판단했는지 읽는다.

우측 하단 패널은 상태 전환 순서를 보여준다. t=1~22는 monitoring, t=22~27은 warning, t=27~36은 drift로 표시된다. 상단 요약의 detect delay `4 step`은 warning 이후 drift alarm까지 지연이 있었음을 의미한다. Warning이 먼저 나타난 뒤 t=27에서 drift 상태로 바뀌므로, 값 상승이 누적 evidence로 쌓인 뒤 경보로 확정된 흐름으로 읽는다.

패널들을 함께 읽을 때는 alarm marker 하나만 보지 않는다. 좌측의 reference mean `0.53` 대비 상승, 우측 상단의 evidence `15.1` 대 bound `12.2` 초과, 우측 하단의 warning -> drift 전환과 detect delay `4 step`이 같은 방향일 때 SeqDrift 기반 stream 상승 drift 후보로 해석한다.

### Drift 후보 판단 기준

stream 값이 reference mean 대비 지속적으로 이동하고, sequential evidence가 decision bound를 넘으며, timeline에서 warning 이후 drift 상태가 표시되면 SeqDrift 기반 stream drift 후보로 해석한다.

단, SeqDrift는 bound 설정, reference window, reservoir 또는 sample 유지 방식에 영향을 받는다. drift 민감도와 탐지 지연을 함께 보고해야 한다.

### 이 예시 차트의 해석

이 예시에서는 evidence가 `26.5`, alarm index가 `27`, detect delay가 `4 step`으로 표시되어 있다. 좌측 stream value trend에서는 값이 t=20의 `0.58` 이후 계속 상승해 t=27에는 `0.75`, t=36에는 `0.87`에 도달한다. Reference mean은 `0.53`이고, alarm 시점에는 delta가 `+0.34` 수준으로 확대된다.

우측 상단에서는 t=27의 sequential evidence `15.1`이 decision bound `12.2`를 넘은 뒤 계속 증가해 마지막에는 `26.5`까지 도달한다. 우측 하단 timeline에서는 t=22부터 warning 상태가 시작되고 t=27부터 drift 상태로 전환된다. 따라서 이 예시는 reference mean 대비 stream 값이 상승하며 누적 evidence가 bound를 넘은 SeqDrift drift 후보로 해석할 수 있다.

보고서 문장 예시는 다음과 같다.

```text
SeqDrift로 stream metric을 순차 모니터링한 결과,
time index 27에서 sequential evidence 15.1이 decision bound 12.2를 초과했다.
Stream 값은 reference mean 0.53 대비 지속적으로 상승해 t=27에 0.75에 도달했고,
alarm 시점의 delta는 +0.34, detect delay는 4 step으로 나타났다.
이는 reference 구간 대비 현재 stream 수준이 상승한 순차 검정 기반 drift 후보로 해석할 수 있다.
```

### 금지해야 할 해석

이 차트만으로 다음을 단정하지 않는다.

```text
금지 1
  - evidence가 bound를 넘었다는 이유만으로 drift 원인을 확정한다.

금지 2
  - reference window와 bound 설정을 확인하지 않고 detector 민감도를 평가한다.

금지 3
  - detect delay를 데이터 지연 적재와 혼동한다.

금지 4
  - stream 값 변화가 곧바로 모델 성능 저하를 의미한다고 말한다.
```

SeqDrift는 순차 검정 기반 alarm을 제공한다. 원인 설명과 모델 영향 평가는 별도의 segment 분석과 성능 지표 확인이 필요하다.

### 추가 확인 항목

SeqDrift drift 후보가 나타나면 다음을 추가 확인한다.

- decision bound, significance level, reference window 설정
- reservoir 또는 sample 유지 방식
- detect delay와 업무 허용 지연 기준
- alarm 전후 stream ordering, batch 적재, 지연 데이터 유입 여부
- ADWIN, KSWIN, Page-Hinkley 등 다른 stream detector와의 합의 여부
- label 확보 후 성능 지표, error rate, calibration 변화

### 적합한 사용 대상

이 chart는 다음 method variant에 적합하다.

- `SeqDrift / SEQDRIFT1`
- `SeqDrift / SEQDRIFT2`

## CHART-STREAM-005: SPRT의 오류율 상승 가설 채택 과정

![CHART-STREAM-005](../charts/output/CHART-STREAM-005.png)

### 제목

SPRT의 오류율 상승 가설 채택 과정

### 차트 목적

이 chart는 SPRT가 H0와 H1의 likelihood ratio를 순차적으로 비교해 오류율 상승 가설을 채택하는 과정을 설명한다.

SPRT는 각 관측값이 H0, H1 중 어느 가설을 더 지지하는지 log likelihood ratio로 누적한다. LLR이 상한 boundary를 넘으면 H1, 즉 drift 또는 변화 가설을 채택하고, 하한 boundary를 넘으면 H0를 유지한다. 따라서 error rate 상승, 평균 shift 등 명확한 대립가설을 두고 빠르게 순차 판정해야 할 때 적합하다.

이 예시 차트가 답하는 질문은 다음과 같다.

```text
1. 오류율 stream이 H1에서 가정한 높은 오류율 방향으로 이동하는가?
2. LLR이 accept H1 boundary 10.8을 어느 시점에 넘는가?
3. decision timeline이 continue -> review -> accept H1 순서로 전환되는가?
```

### 현재 상황 요약

이 예시에서는 오류율이 초반 `0.08~0.15` 수준에서 시작해 후반에는 `0.35~0.40` 수준까지 상승한다. SPRT의 log likelihood ratio는 초반 `-0.8~0.9` 범위에서 0 근처를 오가다가 계속 증가해 t=25에서 `11.0`으로 accept H1 boundary `10.8`을 처음 넘는다. 최종 LLR은 `16.0`이고, alpha/beta는 `0.05 / 0.10`, 최종 decision은 `accept H1`로 표시된다.

우측 하단 timeline은 t=1~18 continue, t=18~25 review, t=25~32 accept H1로 이어진다. 따라서 이 차트는 단일 오류율 spike가 아니라 오류율 상승 증거가 순차적으로 누적되어 SPRT가 H1, 즉 오류율 상승 가설을 채택한 drift 후보 상황으로 읽는다.

### 차트 구성

이 chart는 세 영역으로 구성된다.

```text
좌측
  - log likelihood ratio trend
  - accept H1 upper boundary
  - accept H0 lower boundary
  - decision marker

우측 상단
  - stream error rate 또는 metric trend
  - H1 방향 기준선

우측 하단
  - continue/review/accept H1 decision timeline
```

상단 요약 영역에는 final LLR, alpha/beta, 최종 decision을 표시한다.

### 패널별 확인

좌측 큰 패널은 time index별 log likelihood ratio와 accept H1/H0 boundary를 함께 보여준다. 이 예시에서는 LLR이 t=1의 `-0.4`에서 t=4의 `-0.8`까지 낮아진 뒤, t=10의 `0.9`, t=18의 `5.0`, t=24의 `10.2`처럼 꾸준히 증가한다. t=25에서는 LLR `11.0`이 H1 경계 `10.8`을 처음 넘고, 마지막 t=32에서는 `16.0`까지 올라간다. 하한 H0 boundary는 `-2.2`이지만 LLR은 이 선 아래로 내려가지 않으므로, H0 유지보다 H1 채택 방향의 증거가 누적된 흐름으로 읽는다.

우측 상단 패널은 Bernoulli error rate stream을 보여준다. 오류율은 초반 t=1~10에서 `0.07~0.13` 수준에 머물다가 t=16 이후 `0.20`, `0.22`, `0.24`, `0.27`처럼 올라간다. t=22에서 `0.30`에 도달하고 t=23 이후에는 `0.31~0.40` 범위로 H1 방향 기준선 `0.30` 이상에 머문다. 이 패널은 LLR 상승이 실제 오류율 증가 흐름과 같은 방향인지 확인하는 보조 근거다.

우측 하단 패널은 순차 판정 상태 전환을 보여준다. t=1~18은 continue, t=18~25는 review, t=25~32는 accept H1로 표시된다. t=25의 decision marker는 좌측 패널에서 LLR이 H1 경계를 넘는 시점과 일치한다. 따라서 판정 timeline은 detector가 충분한 증거 전에는 검정을 계속하다가, 검토 구간을 거쳐 H1 채택으로 전환했음을 보여준다.

패널들을 함께 읽을 때는 accept H1 표시만 보지 않는다. 좌측의 LLR `11.0` 대 H1 경계 `10.8` 초과, 우측 상단의 오류율 `0.08 -> 0.40` 상승, 우측 하단의 continue -> review -> accept H1 전환이 같은 방향일 때 SPRT 기반 오류율 상승 drift 후보로 해석한다.

```text
LLR이 0 주변에서 흔들린다
  -> 아직 H0/H1 중 어느 쪽 evidence도 충분하지 않다.

LLR이 상한 boundary 방향으로 증가한다
  -> H1, 즉 drift 가설을 지지하는 evidence가 누적되고 있다.

LLR이 하한 boundary 방향으로 감소한다
  -> H0 유지 evidence가 누적되고 있다.
```

### Drift 후보 판단 기준

LLR이 accept H1 boundary를 넘고, stream metric이 H1에서 정의한 방향으로 이동하며, decision timeline이 accept H1 상태로 전환되면 SPRT 기반 drift 후보로 해석한다.

단, SPRT는 H0/H1 가설 설정, alpha, beta, likelihood model에 강하게 의존한다. H1이 실제 운영 drift 형태와 맞지 않으면 LLR 해석이 왜곡될 수 있다.

### 이 예시 차트의 해석

이 예시에서는 final LLR이 `16.0`, alpha/beta가 `0.05 / 0.10`, decision이 `accept H1`로 표시되어 있다. 좌측 LLR trend는 초기에 0 근처에서 움직이다가 점차 증가해 t=25에서 `11.0`으로 accept H1 boundary `10.8`을 넘는다.

우측 상단 error rate stream에서는 오류율이 t=1의 `0.08`에서 t=32의 `0.40`까지 상승하고, t=22 이후 `0.30` 기준선 이상에 머문다. 우측 하단 timeline에서도 t=1~18 continue, t=18~25 review, t=25~32 accept H1로 전환된다. 따라서 이 예시는 오류율 상승 가설을 지지하는 evidence가 누적되어 SPRT가 drift 후보를 판정한 사례로 해석할 수 있다.

보고서 문장 예시는 다음과 같다.

```text
SPRT로 error rate stream을 순차 검정한 결과,
LLR은 t=25에서 11.0으로 accept H1 boundary 10.8을 처음 초과했고 최종 16.0까지 증가했다.
Error rate는 0.08에서 0.40까지 상승했으며 t=22 이후 0.30 기준선 이상에 머물렀다.
Decision timeline은 continue -> review -> accept H1 상태로 전환되었다.
이는 error rate 상승 방향의 순차 가설 검정 기반 drift 후보로 해석할 수 있다.
```

### 금지해야 할 해석

이 차트만으로 다음을 단정하지 않는다.

```text
금지 1
  - H1 채택만으로 drift 원인을 특정 feature로 단정한다.

금지 2
  - H0/H1 가설과 likelihood model을 확인하지 않고 LLR을 해석한다.

금지 3
  - alpha/beta 설정에 따른 false alarm, miss risk를 보고하지 않는다.

금지 4
  - error rate 상승을 원인 분석 없이 데이터 drift로만 해석한다.
```

SPRT는 사전에 정의한 가설을 빠르게 판정하는 detector다. drift 원인과 모델 영향은 별도 분석이 필요하다.

### 추가 확인 항목

SPRT drift 후보가 나타나면 다음을 추가 확인한다.

- H0/H1 error rate 또는 mean shift 가정
- alpha, beta, decision boundary 설정
- likelihood model이 실제 metric 분포와 맞는지 여부
- label 지연과 error rate 계산 시점
- ADWIN, Page-Hinkley, DDM 등 다른 detector와의 합의 여부
- alarm 전후 segment/source/time 구성 변화

### 적합한 사용 대상

이 chart는 다음 method variant에 적합하다.

- `SPRT / SPRT_BERNOULLI_ERROR_RATE`
- `SPRT / SPRT_GAUSSIAN_MEAN_SHIFT`
