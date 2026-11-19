# Model Uncertainty Drift Chart Interpretation

## CHART-UNC-001

![CHART-UNC-001](../charts/output/CHART-UNC-001.png)

### 제목

확신도 하락과 엔트로피 상승으로 본 불확실성 드리프트

### 차트 목적

이 chart는 model uncertainty가 baseline 대비 증가했는지 설명한다. 이 예시에서는 current confidence 분포가 baseline보다 낮은 쪽으로 이동하고, entropy trend가 threshold `0.55`를 t=15에서 넘은 뒤 최종 `0.77`까지 상승한다.

Softmax confidence drift, entropy drift, predictive variance drift는 모델이 current sample에 대해 덜 확신하거나 더 불안정한 예측을 내는지를 본다. Confidence 분포, uncertainty trend, calibration curve, class별 uncertainty를 함께 확인해야 한다. 이 화면에서는 ECE `0.12`와 class C uncertainty `0.46`도 함께 표시되어 확신도 저하가 calibration 이탈과 특정 class 집중으로 이어지는지 확인할 수 있다.

이 차트는 다음 질문에 답한다.

```text
1. current confidence 분포가 baseline보다 낮은 쪽으로 이동했는가?
2. entropy 또는 predictive variance trend가 threshold를 넘는가?
3. calibration 이탈과 특정 class의 uncertainty 집중이 함께 나타나는가?
```

### 현재 상황 요약

이 예시에서는 baseline confidence가 높은 구간에 몰려 `0.82` bin에서 density `41`로 가장 높지만, current confidence는 `0.47` bin에서 density `38`로 peak가 왼쪽으로 이동한다. Entropy trend는 t=14의 `0.52`까지 threshold `0.55` 아래에 있다가 t=15의 `0.57`에서 alarm 구간으로 들어가고, t=24에는 `0.77`까지 상승한다. Calibration curve도 perfect line 아래에 있어 같은 confidence 구간에서 실제 정확도가 낮게 보이며, class별 uncertainty는 C가 `0.46`으로 A `0.19`, B `0.31`, D `0.28`보다 높다. 따라서 이 차트는 current 데이터에서 모델 확신도가 낮아지고 불확실성이 커진 drift 후보 상황을 보여준다.

### 패널별 확인

이 chart는 세 영역으로 구성된다.

```text
좌측
  - baseline/current confidence distribution
  - low-confidence region marker
  - baseline peak는 confidence 0.82의 density 41이고, current peak는 confidence 0.47의 density 38인지 확인한다.
  - current 분포가 0.50 이하 low-confidence 영역으로 이동했는지 본다.

우측 상단
  - entropy 또는 predictive variance trend
  - uncertainty threshold
  - entropy가 t=15의 0.57에서 threshold 0.55를 넘고, t=24의 0.77까지 지속 상승하는지 확인한다.

우측 하단
  - calibration curve
  - class별 uncertainty bar
  - calibration curve가 perfect line 아래로 내려가 confidence 대비 실제 정답률이 낮아지는지 본다.
  - class C uncertainty가 0.46으로 가장 높아 특정 class에 불확실성이 집중되는지 확인한다.
```

상단 요약 영역에는 entropy, ECE, alarm 시점을 표시한다.

### 해석 순서

먼저 좌측 confidence distribution에서 current confidence가 낮아졌는지 확인한다.

```text
confidence 분포가 baseline과 유사하다
  -> uncertainty drift 증거가 약하다.

current confidence가 낮은 영역으로 이동한다
  -> 모델 확신도 저하 후보로 본다.

confidence 하락과 entropy 상승이 함께 나타난다
  -> uncertainty drift 설명력이 높아진다.
```

그 다음 우측 상단 trend에서 entropy 또는 predictive variance가 threshold를 넘고 지속되는지 확인한다.

마지막으로 우측 하단 calibration curve와 class별 bar에서 miscalibration과 class-specific uncertainty가 집중되는지 확인한다.

### Drift 후보 판단 기준

Current confidence가 낮아지고 entropy 또는 predictive variance가 threshold를 지속적으로 넘으며, calibration curve가 perfect calibration에서 벗어나고 특정 class의 uncertainty가 높으면 model uncertainty drift 후보로 해석한다.

단, uncertainty drift는 성능 저하와 동일하지 않다. Label delay 때문에 실제 accuracy를 모를 수 있으며, 모델이 더 불확실해졌지만 아직 정확도는 유지될 수도 있다.

### 이 예시 차트의 해석

이 예시에서는 entropy가 `0.77`, ECE가 `0.12`, alarm 시점이 `t=15`로 표시되어 있다. 좌측 분포에서는 baseline confidence가 `0.82` 부근 density `41`로 높은 confidence에 집중되는 반면, current confidence는 `0.47` 부근 density `38`로 낮은 confidence 쪽에 집중된다.

우측 상단 trend는 entropy가 t=14의 `0.52`까지 threshold 아래에 있다가 t=15의 `0.57`에서 threshold `0.55`를 넘고, 이후 t=24의 `0.77`까지 계속 상승한다. 우측 하단에서는 calibration curve가 perfect line 아래로 이탈하고, class C의 uncertainty가 `0.46`으로 가장 높다. 따라서 이 예시는 model uncertainty가 증가한 drift 후보로 해석할 수 있다.

보고서 문장 예시는 다음과 같다.

```text
Model uncertainty 모니터링 결과 current confidence 분포는 낮은 영역으로 이동했고,
entropy는 t=15 이후 threshold를 초과해 최종 0.77까지 상승했다.
ECE는 0.12로 calibration 이탈이 확인되며 class C에서 uncertainty가 집중되었다.
이는 model uncertainty drift 후보로 해석할 수 있다.
```

### 금지해야 할 해석

이 차트만으로 다음을 단정하지 않는다.

```text
금지 1
  - uncertainty 증가만으로 accuracy 저하를 단정한다.

금지 2
  - calibration 이탈을 feature drift 원인으로 해석한다.

금지 3
  - class별 uncertainty를 보지 않고 전체 entropy만으로 운영 영향을 판단한다.

금지 4
  - temperature scaling, threshold, ensemble 설정을 확인하지 않는다.
```

Uncertainty drift는 모델 확신도의 변화 신호다. 실제 영향은 delayed label 성능, class별 error, calibration 재보정 결과와 함께 확인해야 한다.

### 추가 확인 항목

Model uncertainty drift 후보가 나타나면 다음을 추가 확인한다.

- softmax confidence, entropy, predictive variance 계산 방식
- temperature scaling 또는 calibration 방법
- ECE, Brier score, reliability diagram 변화
- class별 uncertainty와 class별 error rate
- label delay 이후 실제 accuracy 변화
- ensemble, MC dropout, Bayesian model 설정
- input feature drift 또는 class prior shift와의 관계

### 적합한 사용 대상

이 chart는 다음 method variant에 적합하다.

- `Model Uncertainty Drift / SOFTMAX_CONFIDENCE_DRIFT`
- `Model Uncertainty Drift / ENTROPY_DRIFT`
- `Model Uncertainty Drift / PREDICTIVE_VARIANCE_DRIFT`
