# Generic Drift Chart Interpretation

## CHART-GEN-001

![CHART-GEN-001](../charts/output/CHART-GEN-001.png)

### 제목

임시 지표 상승으로 확인한 일반 드리프트 후보

### 차트 목적

이 chart는 아직 특정 chart family가 정해지지 않은 method를 설명하기 위한 기본 fallback chart다. 이 예시에서는 generic drift metric이 threshold `0.45`를 t=15에서 넘고 최종 `0.68`까지 상승한다.

전용 chart가 없더라도 drift report에는 최소한 metric trend, reference/current distribution, threshold 또는 alarm marker가 필요하다. 이 chart는 method-specific chart가 추가되기 전까지 공통 해석 틀을 제공한다. 이 화면에서는 current distribution이 reference보다 오른쪽으로 이동하고, evidence summary도 final metric `0.68`, threshold `0.45`, effect size `0.52`, p-value score `0.91`을 함께 보여준다.

이 차트는 다음 질문에 답한다.

```text
1. drift metric이 시간에 따라 threshold를 넘는가?
2. reference/current distribution이 같은 방향의 이동을 보이는가?
3. alarm marker와 evidence summary가 drift 후보 판단을 뒷받침하는가?
```

### 현재 상황 요약

이 예시에서는 drift metric이 t=1의 `0.12`에서 점진적으로 증가해 t=14의 `0.43`까지 threshold `0.45` 아래에 있다가, t=15의 `0.48`에서 alarm 구간으로 들어간다. 이후 metric은 계속 올라 t=22에 `0.68`로 마무리된다. Reference distribution은 `0.33` 부근 density `38`에서 가장 높고, current distribution은 `0.54` 부근 density `37`로 오른쪽에 peak가 생긴다. 우측 하단 evidence summary도 final metric `0.68`과 effect size `0.52`가 threshold 초과를 뒷받침하므로, 이 차트는 전용 family가 아직 없는 method에 대해 최소한의 generic drift 후보를 표시한 상황으로 읽는다.

### 패널별 확인

이 chart는 세 영역으로 구성된다.

```text
좌측
  - generic drift metric trend
  - threshold line
  - alarm marker
  - metric이 t=15의 0.48에서 threshold 0.45를 넘고 t=22의 0.68까지 상승하는지 확인한다.
  - threshold 초과가 단일 spike가 아니라 alarm 이후 지속되는지 본다.

우측 상단
  - reference/current distribution overlay
  - reference peak는 0.33의 density 38이고, current peak는 0.54의 density 37인지 확인한다.
  - current 분포가 reference보다 오른쪽으로 이동해 trend 상승과 같은 방향인지 본다.

우측 하단
  - final metric
  - threshold
  - effect size
  - p-value score 또는 confidence score
  - final metric 0.68, threshold 0.45, effect size 0.52, p-value score 0.91이 서로 threshold 초과 판단을 지지하는지 확인한다.
```

상단 요약 영역에는 metric, threshold, alarm 시점을 표시한다.

### 해석 순서

먼저 좌측 metric trend에서 score가 threshold를 넘는지 확인한다.

```text
metric이 threshold 아래에 있다
  -> drift 후보 증거가 약하다.

metric이 threshold를 넘지만 distribution 이동이 없다
  -> metric 정의와 threshold 설정을 다시 확인한다.

metric과 distribution 이동이 같은 방향이다
  -> generic drift 후보로 본다.
```

그 다음 우측 상단 distribution overlay에서 reference/current 차이가 trend와 일관되는지 확인한다.

마지막으로 우측 하단 evidence summary에서 final metric, threshold, effect size, p-value score가 서로 모순되지 않는지 확인한다.

### Drift 후보 판단 기준

Drift metric trend가 threshold를 넘고 alarm marker가 표시되며, reference/current distribution이 같은 방향으로 이동하고 evidence summary가 threshold 초과를 뒷받침하면 generic drift 후보로 해석한다.

단, 이 chart는 전용 family chart가 없는 경우의 fallback이다. Method의 통계량, p-value, distance 정의, window 구조가 명확해지면 반드시 더 구체적인 chart family로 대체해야 한다.

### 이 예시 차트의 해석

이 예시에서는 metric이 `0.68`, threshold가 `0.45`, alarm 시점이 `t=15`로 표시되어 있다. 좌측 trend는 t=14의 `0.43`까지 threshold 아래에 있다가 t=15의 `0.48`에서 threshold `0.45`를 넘고, alarm 이후에도 t=22의 `0.68`까지 상승한다.

우측 상단 distribution은 reference가 `0.33` 부근 density `38`에 집중되는 반면 current는 `0.54` 부근 density `37`로 오른쪽 이동한다. 우측 하단 evidence summary도 final metric `0.68`, effect size `0.52`, p-value score `0.91`로 threshold 초과를 뒷받침한다. 따라서 이 예시는 전용 chart family가 아직 없는 method의 generic drift 후보로 해석할 수 있다.

보고서 문장 예시는 다음과 같다.

```text
Generic drift metric은 t=15에서 threshold 0.45를 초과했고
최종 값은 0.68까지 상승했다.
Reference/current distribution도 current 방향으로 이동했으므로
전용 chart family가 정의되기 전까지는 generic drift 후보로 해석한다.
```

### 금지해야 할 해석

이 차트만으로 다음을 단정하지 않는다.

```text
금지 1
  - generic chart를 method-specific chart와 같은 해석력으로 본다.

금지 2
  - metric 정의 없이 threshold 초과만 보고 원인을 단정한다.

금지 3
  - p-value, distance, score를 같은 단위로 혼합해 해석한다.

금지 4
  - 전용 family chart가 필요한데 fallback chart로 계속 유지한다.
```

Generic chart는 보고서 공백을 막는 최소 공통 형식이다. 장기적으로는 method family에 맞는 전용 chart로 전환해야 한다.

### 추가 확인 항목

Generic drift 후보가 나타나면 다음을 추가 확인한다.

- metric의 정의와 단위
- threshold 산정 방식
- reference/current window 정의
- p-value, confidence, effect size의 의미
- sample size와 missing/duplicate 처리
- method-specific chart family로 승격 가능 여부
- downstream model 성능 또는 business metric 영향

### 적합한 사용 대상

이 chart는 다음 상황에 적합하다.

- 특정 chart family가 아직 정해지지 않은 method
- metric trend와 threshold만 우선 설명해야 하는 초기 report
- method-specific visualization을 설계하기 전의 임시 fallback
