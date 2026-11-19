# Error Rate Detector Chart Interpretation

## CHART-ERR-001

![CHART-ERR-001](../charts/output/CHART-ERR-001.png)

### 제목

오류율 상승과 DDM 드리프트 경보

### 차트 목적

이 chart는 DDM이 online error rate의 증가를 warning과 drift 단계로 구분해 감지하는 방식을 설명한다. 이 예시에서는 오류율이 초반 0.08~0.18 수준에서 시작해 마지막 0.46까지 올라가고, warning 기준 0.27과 drift 기준 0.36을 차례로 넘는다.

DDM은 현재 error rate의 `p + s`를 최소 error 상태의 `p_min + 2s_min`, `p_min + 3s_min` 기준과 비교한다. Warning 구간은 drift 전 후보 데이터를 보관하는 buffer 역할을 하며, drift threshold를 넘으면 error-rate detector 기반 drift 후보로 판단한다.

이 차트는 다음 질문에 답한다.

```text
1. error rate가 warning threshold를 넘는가?
2. warning buffer가 drift threshold 초과로 이어지는가?
3. drift alarm 이후 error rate 상승이 지속되는가?
```

### 현재 상황 요약

이 예시에서는 error rate가 t=21의 0.26까지는 warning 기준 0.27 바로 아래에 있다가 t=22에서 0.28로 올라 warning 상태가 시작된다. 이후 t=26에서 0.37로 drift 기준 0.36을 넘고, 마지막에는 0.46까지 상승한다. Warning buffer는 t=22부터 t=26 직전까지 유지되며, 단순한 일시적 spike가 아니라 기준선 초과가 drift alarm으로 이어지는 흐름을 보여준다.

### 패널별 확인

이 chart는 세 영역으로 구성된다.

```text
좌측
  - error rate trend
  - error rate가 0.08에서 0.46까지 증가하는지 본다.
  - warning threshold 0.27과 drift threshold 0.36을 차례로 넘는지 확인한다.
  - t=22 warning marker와 t=26 drift marker가 같은 상승 흐름 위에 있는지 확인한다.

우측 상단
  - p+s와 drift threshold의 margin
  - margin이 0보다 작을 때는 drift 기준 아래이고, 0을 넘으면 drift 기준 초과다.
  - 이 예시에서는 t=26 부근부터 margin이 0을 넘는다.

우측 하단
  - normal/warning/drift state timeline
  - t=1~21은 normal, t=22~25는 warning buffer, t=26 이후는 drift 상태로 읽는다.
```

상단 요약 영역에는 final error, warning start, drift alarm을 표시한다.

### 해석 순서

먼저 좌측 error rate trend에서 warning threshold와 drift threshold 초과 여부를 확인한다.

```text
error rate가 warning threshold 아래에 있다
  -> DDM 기준으로 정상 상태로 본다.

error rate가 warning threshold를 넘지만 drift threshold 아래에 있다
  -> warning buffer를 유지하며 추가 관측이 필요하다.

error rate가 drift threshold를 넘는다
  -> DDM drift 후보로 본다.
```

그 다음 우측 상단 threshold margin을 본다. Margin이 0을 넘는 시점은 drift threshold 초과 시점이다.

마지막으로 우측 하단 warning buffer timeline을 확인한다. Warning 구간이 짧게 끝나는지, drift 상태로 이어지는지에 따라 후속 조치가 달라진다.

### Drift 후보 판단 기준

Error rate가 warning threshold를 넘은 뒤 buffer 구간을 거쳐 drift threshold를 초과하고, 이후 error rate 상승이 지속되면 DDM 기반 drift 후보로 해석한다.

단, DDM은 label이 있어야 error rate를 계산할 수 있고, label 지연이 있으면 alarm 시점이 실제 drift 시점보다 늦게 보일 수 있다. Class-specific DDM을 사용할 때는 전체 error rate와 class별 error rate를 구분해 해석해야 한다.

### 이 예시 차트의 해석

이 예시에서는 final error가 `0.46`, warning start가 `t=22`, drift alarm이 `t=26`으로 표시되어 있다. 좌측 error trend는 t=22에서 warning threshold `0.27`을 넘고, t=26에서 drift threshold `0.36`을 초과한다.

우측 상단 margin chart에서는 t=26 부근부터 drift threshold 대비 margin이 0을 넘는다. 우측 하단 timeline에서는 normal 상태가 warning buffer를 거쳐 drift 상태로 전환된다. 따라서 이 예시는 error rate 상승이 DDM 기준 drift threshold를 넘은 drift 후보로 해석할 수 있다.

보고서 문장 예시는 다음과 같다.

```text
DDM으로 error rate stream을 모니터링한 결과,
t=22에서 warning threshold를 초과했고 t=26에서 drift threshold를 초과했다.
Final error rate는 0.46으로 상승했으며 warning buffer가 drift 상태로 이어졌다.
이는 error-rate detector 기준의 drift 후보로 해석할 수 있다.
```

### 금지해야 할 해석

이 차트만으로 다음을 단정하지 않는다.

```text
금지 1
  - DDM drift alarm만으로 원인 feature를 특정한다.

금지 2
  - label 지연과 label 품질을 확인하지 않고 alarm 시점을 해석한다.

금지 3
  - class imbalance가 큰 상황에서 전체 error rate만 보고 class별 영향을 단정한다.

금지 4
  - warning buffer 없이 단일 error spike를 drift로 단정한다.
```

DDM은 error rate 변화 detector다. 데이터 분포 변화, 입력 feature 변화, calibration 변화는 별도 chart와 함께 확인해야 한다.

### 추가 확인 항목

DDM drift 후보가 나타나면 다음을 추가 확인한다.

- label 지연과 error rate 산정 지연
- warning buffer에 포함된 sample 구성
- class별 error rate와 class imbalance 변화
- 최근 배포, threshold 변경, 운영 정책 변경
- DDM min error 기준의 초기화 여부
- RDDM, EDDM, ECDD-WT 등 다른 error-rate detector와의 합의 여부
- 입력 feature drift, PSI, KS, Wasserstein 등 데이터 drift chart와의 관계

### 적합한 사용 대상

이 chart는 다음 method variant에 적합하다.

- `DDM / DDM_STANDARD`
- `DDM / DDM_WARNING_BUFFER`
- `DDM / DDM_CLASS_SPECIFIC`

## CHART-ERR-002

![CHART-ERR-002](../charts/output/CHART-ERR-002.png)

### 제목

RDDM의 경보 구간 보존과 재설정 과정

### 차트 목적

이 chart는 RDDM이 DDM의 warning/drift 판단을 확장해 warning 구간의 sample을 보존하고, drift 확정 시 reactive reset으로 새 window를 구성하는 방식을 설명한다. 이 예시에서는 error rate가 초반 `0.07~0.19` 수준에서 점진적으로 올라 t=20의 `0.28`에서 warning 기준에 닿고, t=25의 `0.40`에서 drift 기준 `0.38`을 초과한다.

RDDM은 error rate 상승을 감지하는 점에서는 DDM과 유사하지만, warning 구간을 단순 대기 상태로 두지 않고 retained window로 관리한다. Drift가 확정되면 warning 구간의 정보를 활용해 reset 이후의 학습 또는 모니터링 window를 구성한다.

이 차트는 다음 질문에 답한다.

```text
1. error rate가 warning 구간을 거쳐 drift 상태로 전환되는가?
2. warning 구간의 retained window size가 어떻게 유지되는가?
3. DDM과 RDDM의 reset 대응이 어떻게 다른가?
```

### 현재 상황 요약

이 예시에서는 error rate가 t=20에서 warning threshold `0.28`에 도달하고 t=25에서 drift threshold `0.38`을 넘어 `0.40`까지 상승한다. 그 다음 t=26에서 reactive reset이 표시되며 error rate는 `0.42`를 찍은 뒤 t=28의 `0.36`, 마지막 t=32의 `0.29`까지 낮아진다. Retained window size는 warning 구간 동안 계속 커져 reset 직전 t=25에 `156`까지 증가하고, reset 직후 t=26에는 `44`로 축소된다. 따라서 이 차트는 RDDM이 warning 구간을 보존한 뒤 drift 확정 시 새 window로 전환하는 상황을 보여준다.

### 패널별 확인

이 chart는 세 영역으로 구성된다.

```text
좌측
  - error rate trend
  - error rate가 0.07에서 0.42까지 상승한 뒤 reset 이후 0.29까지 낮아지는지 본다.
  - warning threshold 0.28과 drift threshold 0.38을 순서대로 지나는지 확인한다.
  - t=20 warning, t=25 drift, t=26 reactive reset marker가 같은 상승 흐름 위에 있는지 확인한다.

우측 상단
  - retained window size trend
  - retained window가 t=20의 136에서 t=25의 156까지 증가한 뒤 t=26에 44로 축소되는지 본다.
  - reset 이후에는 48, 52, 58, 64, 70, 76처럼 새 window가 다시 쌓이는 흐름을 확인한다.

우측 하단
  - DDM/RDDM comparison timeline
  - DDM은 t=20~25 warning 이후 reset 상태로 넘어간다.
  - RDDM은 t=20~26 구간을 retain으로 유지한 뒤 reactive reset으로 전환된다.
```

상단 요약 영역에는 warning start, reactive reset, reset 직후 retained window 크기를 표시한다.

### 해석 순서

먼저 좌측 error rate trend에서 warning과 drift marker가 순차적으로 나타나는지 확인한다.

```text
warning 없이 drift marker만 나타난다
  -> 급격한 error spike 또는 threshold 민감도를 점검한다.

warning 구간이 유지된 뒤 drift marker가 나타난다
  -> RDDM의 retained window 활용 조건을 만족한다.

reactive reset 이후 error rate가 완화된다
  -> reset 이후 새 window에서 안정화 가능성을 확인한다.
```

그 다음 우측 상단 retained window size를 확인한다. Warning 구간에서 window가 보존되다가 reset 시점에 축소되는 패턴이 RDDM의 핵심이다.

마지막으로 우측 하단 비교 timeline에서 DDM과 RDDM의 차이를 확인한다. DDM이 drift 후 reset으로 끝나는 반면, RDDM은 warning 구간의 데이터를 retain하고 reactive reset으로 전환한다.

### Drift 후보 판단 기준

Error rate가 warning 구간을 거쳐 drift threshold를 넘고, retained window가 reset 시점에 축소되며, DDM/RDDM 비교에서 RDDM의 retain/reactive reset 흐름이 확인되면 RDDM 기반 drift 후보로 해석한다.

단, RDDM은 warning 구간의 sample 품질에 민감하다. Warning buffer가 오염되었거나 label 지연이 크면 reset 후 window 구성이 실제 drift 이후 분포를 잘 대표하지 못할 수 있다.

### 이 예시 차트의 해석

이 예시에서는 warning start가 `t=20`, reactive reset이 `t=26`, reset 직후 retained window가 `44`로 표시되어 있다. 좌측 error trend는 t=20의 error rate `0.28`에서 warning threshold `0.28`에 도달하고, t=25의 `0.40`에서 drift threshold `0.38`을 초과한다. t=26에서는 error rate가 `0.42`로 최고점에 도달하지만 reset 이후 t=28의 `0.36`, t=32의 `0.29`까지 완만하게 낮아진다.

우측 상단 retained window size는 warning 구간에서 t=20의 `136`부터 t=25의 `156`까지 증가하다가 reactive reset 시점인 t=26에 `44`로 급격히 축소된다. 우측 하단 비교 timeline에서는 RDDM이 DDM과 달리 warning 구간을 retain한 뒤 reactive reset으로 전환되는 구조를 보여준다. 따라서 이 예시는 RDDM이 warning buffer를 활용해 drift 이후 window를 재구성한 사례로 해석할 수 있다.

보고서 문장 예시는 다음과 같다.

```text
RDDM 모니터링 결과 t=20에서 warning 상태가 시작되고,
t=25에서 error rate 0.40이 drift threshold 0.38을 초과했다.
t=26에서 reactive reset이 수행되면서 retained window size는
156에서 44로 축소되었고, error rate는 이후 0.29까지 낮아졌다.
이는 RDDM 기준 error-rate drift 후보로 해석할 수 있다.
```

### 금지해야 할 해석

이 차트만으로 다음을 단정하지 않는다.

```text
금지 1
  - retained window 축소만으로 drift를 단정한다.

금지 2
  - warning buffer의 label 품질을 확인하지 않고 reset 효과를 평가한다.

금지 3
  - RDDM과 DDM의 차이를 단순 threshold 차이로만 설명한다.

금지 4
  - reset 이후 error rate 완화를 원인 해결로 단정한다.
```

RDDM은 warning 구간 보존과 reactive reset을 통해 error-rate drift에 대응한다. Drift 원인과 성능 회복 여부는 별도 분석이 필요하다.

### 추가 확인 항목

RDDM drift 후보가 나타나면 다음을 추가 확인한다.

- retained window에 포함된 sample 수와 label 품질
- warning 구간의 class/source/time 구성
- reactive reset 조건과 reset 후 window 초기화 방식
- DDM 대비 false alarm 감소 또는 detection delay 변화
- label 지연이 reset 시점에 미치는 영향
- EDDM, ECDD-WT, HDDM 등 다른 error detector와의 합의 여부
- 입력 feature drift와 모델 성능 지표 변화

### 적합한 사용 대상

이 chart는 다음 method variant에 적합하다.

- `RDDM / RDDM_STANDARD`
- `RDDM / RDDM_REACTIVE_RESET`

## CHART-ERR-003

![CHART-ERR-003](../charts/output/CHART-ERR-003.png)

### 제목

오류 간격 축소로 나타난 점진적 성능 저하

### 차트 목적

이 chart는 EDDM이 오류 사이의 거리(distance between errors)를 이용해 점진적 성능 저하를 감지하는 방식을 설명한다. 이 예시에서는 distance score가 처음 `1.00`에서 마지막 `0.44`까지 낮아지고, warning 기준 `0.90`은 `t=11`, drift 기준 `0.75`는 `t=19`에 차례로 통과한다.

EDDM은 단순 error rate보다 오류 사이 간격의 변화에 주목한다. 오류가 점점 자주 발생하면 오류 사이 거리가 짧아지고, distance score ratio가 warning 또는 drift 기준 아래로 내려간다. 이 화면에서는 error event가 초반 `t=3, 8, 13, 17`처럼 떨어져 있다가 후반 `t=27~32`에서 매 시점 발생하며 score 하락을 뒷받침한다.

이 차트는 다음 질문에 답한다.

```text
1. 오류 사이 간격 기반 score가 점진적으로 낮아지는가?
2. score가 warning 기준을 지나 drift 기준 아래로 내려가는가?
3. error event raster에서 오류 발생이 실제로 촘촘해지는가?
```

### 현재 상황 요약

이 예시에서는 오류 간격 score가 초반 `1.00~0.91` 수준에서 완만히 내려가다가 `t=11`에 `0.89`가 되어 warning 기준 `0.90` 아래로 내려간다. 이후 `t=19`의 score `0.74`가 drift 기준 `0.75`보다 낮아지고, 마지막에는 `0.44`까지 하락한다. Error event raster도 초반에는 4~5 time index 간격으로 나타나지만, drift 이후에는 `t=20, 22, 24, 25, 27, 28, 29, 30, 31, 32`처럼 촘촘해진다. 따라서 이 차트는 갑작스러운 단일 spike보다 오류 발생 간격이 지속적으로 짧아진 점진적 성능 저하 상황을 보여준다.

### 패널별 확인

이 chart는 세 영역으로 구성된다.

```text
좌측
  - 오류 간격 score trend
  - score가 1.00에서 0.44까지 내려가는지 본다.
  - warning threshold 0.90과 drift threshold 0.75를 순서대로 지나는지 확인한다.
  - t=11 warning marker와 t=19 drift marker가 같은 하락 흐름 위에 있는지 확인한다.

우측 상단
  - normal/warning/drift state timeline
  - t=1~10은 normal, t=11~18은 warning, t=19 이후는 drift 상태로 읽는다.
  - warning 구간이 drift 상태로 이어지는지 확인한다.

우측 하단
  - error event raster
  - 초반 오류 event는 t=3, 8, 13, 17처럼 간격을 두고 나타난다.
  - drift 이후에는 t=20, 22, 24, 25와 t=27~32 연속 event가 보이는지 확인한다.
```

상단 요약 영역에는 final score, warning 시점, drift 시점을 표시한다.

### 해석 순서

먼저 좌측 distance score trend를 확인한다.

```text
distance score가 1 근처에서 안정적이다
  -> 오류 사이 간격이 baseline과 유사하다.

distance score가 warning 기준 아래로 내려간다
  -> 오류 발생 간격이 줄어드는 초기 징후로 본다.

distance score가 drift 기준 아래로 내려간다
  -> gradual error-rate drift 후보로 본다.
```

그 다음 우측 상단 timeline에서 normal, warning, drift 상태가 순차적으로 전환되는지 확인한다.

마지막으로 우측 하단 error event raster를 확인한다. Drift 이후 error event가 촘촘해지면 distance score 하락이 실제 error event 밀집과 일치한다.

### Drift 후보 판단 기준

Distance-between-errors score가 warning 기준 아래로 먼저 하락하고 이후 drift 기준 아래로 내려가며, error event raster에서도 오류 발생 간격이 짧아지는 패턴이 확인되면 EDDM 기반 drift 후보로 해석한다.

단, EDDM은 gradual drift에 민감하지만 갑작스러운 일회성 error spike에는 과잉 반응하거나 반대로 늦게 반응할 수 있다. Label 지연과 error event 정의도 반드시 확인해야 한다.

### 이 예시 차트의 해석

이 예시에서는 final score가 `0.44`, warning 시점이 `t=11`, drift 시점이 `t=19`로 표시되어 있다. 좌측 trend에서 distance score는 `1.00` 근처에서 시작해 `t=10`의 `0.91`까지는 warning 기준 바로 위에 있다가, `t=11`의 `0.89`에서 warning threshold `0.90` 아래로 내려간다. 이후 `t=19`의 `0.74`에서 drift threshold `0.75`를 통과하고 마지막 `t=32`에는 `0.44`까지 낮아진다.

우측 상단 timeline에서는 `t=1~10` normal 상태가 `t=11~18` warning을 거쳐 `t=19` 이후 drift 상태로 전환된다. 우측 하단 raster에서는 초반 오류 event가 `t=3, 8, 13, 17`처럼 넓게 떨어져 있으나, drift 이후에는 `t=20, 22, 24, 25, 27, 28, 29, 30, 31, 32`처럼 밀도가 높아진다. 특히 `t=27~32`는 매 시점 오류가 표시되어 score 하락이 실제 error event 간격 축소와 일치한다. 따라서 이 예시는 오류 사이 간격이 줄어드는 점진적 error-rate drift 후보로 해석할 수 있다.

보고서 문장 예시는 다음과 같다.

```text
EDDM으로 오류 사이 간격을 모니터링한 결과,
distance score는 t=11에서 warning 기준 0.90 아래로 내려갔고
t=19에서 drift 기준 0.75 아래로 하락했다.
Error event raster에서도 drift 이후 오류 발생 간격이 촘촘해졌다.
이는 gradual error-rate drift 후보로 해석할 수 있다.
```

### 금지해야 할 해석

이 차트만으로 다음을 단정하지 않는다.

```text
금지 1
  - error event 밀집만으로 원인 feature를 특정한다.

금지 2
  - label 지연을 확인하지 않고 error event 시점을 실제 발생 시점으로 해석한다.

금지 3
  - EDDM drift를 갑작스러운 concept drift로 단정한다.

금지 4
  - class별 error event 분포를 보지 않고 전체 오류 증가만 해석한다.
```

EDDM은 오류 사이 간격의 변화에 초점을 둔다. 입력 데이터 drift, calibration 변화, class-specific error 변화는 별도 chart와 함께 확인해야 한다.

### 추가 확인 항목

EDDM drift 후보가 나타나면 다음을 추가 확인한다.

- error event 정의와 label 지연
- 오류 사이 거리의 평균과 표준편차 산정 방식
- warning/drift threshold 설정
- class별 error event raster
- gradual drift가 의심되는 운영 이벤트 또는 데이터 source 변화
- DDM, RDDM, ECDD-WT, HDDM 등 다른 error detector와의 합의 여부
- 모델 성능 지표, calibration, feature drift chart와의 관계

### 적합한 사용 대상

이 chart는 다음 method variant에 적합하다.

- `EDDM / EDDM_DISTANCE_BETWEEN_ERRORS`
- `EDDM / EDDM_WARNING_DRIFT`
- `EDDM / EDDM_GRADUAL_DRIFT`

## CHART-ERR-004

![CHART-ERR-004](../charts/output/CHART-ERR-004.png)

### 제목

ECDD 통계량 상승과 오류율 드리프트 감지

### 차트 목적

이 chart는 ECDD-WT가 error stream을 weighted statistic으로 누적해 control chart 방식으로 drift를 감지하는 방법을 설명한다. 이 예시에서는 ECDD statistic이 초반 `0.18~0.31` 수준에서 시작해 마지막 `1.28`까지 상승하고, warning limit `0.72`와 drift limit `0.95`를 순서대로 넘는다.

ECDD-WT는 최근 error에 더 큰 영향을 주는 weighted statistic을 사용한다. 따라서 raw error rate가 서서히 상승하더라도 statistic이 warning limit과 drift limit을 순차적으로 넘으면 error-rate drift 후보를 빠르게 포착할 수 있다. 이 화면에서는 weighted error rate도 `0.07`에서 `0.45`까지 함께 상승해, statistic 초과가 단순 계산상 잡음이 아니라 error stream 악화와 같은 방향임을 확인한다.

이 차트는 다음 질문에 답한다.

```text
1. ECDD statistic이 warning limit을 넘는가?
2. ECDD statistic이 drift limit까지 초과하는가?
3. weighted error rate trend도 같은 방향으로 상승하는가?
```

### 현재 상황 요약

이 예시에서는 ECDD statistic이 t=21의 `0.68`까지는 warning limit `0.72` 아래에 있다가 t=22에서 `0.73`으로 올라 warning 상태가 시작된다. 이후 t=26의 statistic `0.98`이 drift limit `0.95`를 초과하고, 마지막 t=32에는 `1.28`까지 상승한다. Weighted error rate도 t=1의 `0.07`에서 t=22의 `0.31`, t=26의 `0.38`, t=32의 `0.45`로 꾸준히 높아진다. 따라서 이 차트는 최근 오류에 가중치를 둔 ECDD-WT 통계량이 error stream의 누적 악화를 warning 이후 drift 후보로 포착한 상황을 보여준다.

### 패널별 확인

이 chart는 세 영역으로 구성된다.

```text
좌측
  - ECDD statistic control chart
  - statistic이 0.18에서 1.28까지 상승하는지 본다.
  - warning limit 0.72와 drift limit 0.95를 차례로 넘는지 확인한다.
  - t=22 warning marker와 t=26 drift marker가 같은 상승 흐름 위에 있는지 확인한다.

우측 상단
  - weighted error rate trend
  - weighted error rate가 0.07에서 0.45까지 증가하는지 본다.
  - drift marker가 표시된 t=26의 error rate가 0.38이고 이후 0.45까지 계속 높아지는지 확인한다.

우측 하단
  - normal/warning/drift state timeline
  - t=1~21은 normal, t=22~25는 warning, t=26 이후는 drift 상태로 읽는다.
  - warning 구간이 짧게 사라지지 않고 drift 상태로 이어지는지 확인한다.
```

상단 요약 영역에는 final statistic, warning 시점, drift 시점을 표시한다.

### 해석 순서

먼저 좌측 ECDD statistic control chart에서 statistic이 warning limit과 drift limit을 넘는지 확인한다.

```text
statistic이 warning limit 아래에 있다
  -> weighted error stream 기준 정상 상태로 본다.

statistic이 warning limit을 넘지만 drift limit 아래에 있다
  -> warning 상태로 보고 추가 관측이 필요하다.

statistic이 drift limit을 넘는다
  -> ECDD-WT drift 후보로 본다.
```

그 다음 우측 상단 error rate trend를 확인한다. Statistic 상승이 실제 weighted error rate 증가와 같은 방향인지 확인해야 한다.

마지막으로 우측 하단 state timeline에서 warning 상태가 drift 상태로 이어지는지 확인한다.

### Drift 후보 판단 기준

ECDD statistic이 warning limit을 넘은 뒤 drift limit을 초과하고, weighted error rate trend도 같은 기간 상승하며, timeline이 drift 상태로 전환되면 ECDD-WT 기반 drift 후보로 해석한다.

단, ECDD-WT는 weighting parameter와 control limit 산정 방식에 민감하다. Weight가 너무 크면 최근 error spike에 과민하고, 너무 작으면 gradual drift 감지가 늦어질 수 있다.

### 이 예시 차트의 해석

이 예시에서는 final statistic이 `1.28`, warning 시점이 `t=22`, drift 시점이 `t=26`으로 표시되어 있다. 좌측 control chart에서 ECDD statistic은 t=1의 `0.18`에서 시작해 t=21의 `0.68`까지 warning limit 아래에 머물다가, t=22의 `0.73`에서 warning limit `0.72`를 초과한다. 이후 t=26의 `0.98`에서 drift limit `0.95`를 넘고, t=32에는 `1.28`까지 상승한다.

우측 상단 weighted error rate도 같은 기간 꾸준히 상승한다. Error rate는 t=1의 `0.07`에서 t=22의 `0.31`, t=26의 `0.38`, t=32의 `0.45`로 높아져 statistic 상승과 방향이 일치한다. 우측 하단 timeline에서는 `t=1~21` normal 상태가 `t=22~25` warning을 거쳐 `t=26` 이후 drift 상태로 전환된다. 따라서 이 예시는 weighted error stream의 상승을 ECDD-WT statistic이 drift로 감지한 사례로 해석할 수 있다.

보고서 문장 예시는 다음과 같다.

```text
ECDD-WT로 error stream을 모니터링한 결과,
ECDD statistic은 t=22에서 warning limit 0.72를 초과했고
t=26에서 drift limit 0.95를 초과했다.
Weighted error rate도 같은 기간 상승했으므로
weighted error-rate detector 기반 drift 후보로 해석할 수 있다.
```

### 금지해야 할 해석

이 차트만으로 다음을 단정하지 않는다.

```text
금지 1
  - ECDD statistic 초과만으로 원인 feature를 특정한다.

금지 2
  - weighting parameter를 확인하지 않고 민감도를 평가한다.

금지 3
  - control limit 산정 기간과 baseline 상태를 확인하지 않는다.

금지 4
  - 최근 error spike 하나만 보고 지속적 drift로 단정한다.
```

ECDD-WT는 weighted error stream detector다. 데이터 분포 변화, class별 error 변화, calibration 변화는 별도 chart와 함께 확인해야 한다.

### 추가 확인 항목

ECDD-WT drift 후보가 나타나면 다음을 추가 확인한다.

- weighting parameter와 decay 설정
- warning/drift control limit 산정 방식
- baseline 기간의 error rate 안정성
- label 지연과 error stream 계산 시점
- class별 weighted error trend
- DDM, RDDM, EDDM, HDDM 등 다른 error detector와의 합의 여부
- 입력 feature drift와 모델 성능 지표 변화

### 적합한 사용 대상

이 chart는 다음 method variant에 적합하다.

- `ECDD-WT / ECDD_WT_STANDARD`
- `ECDD-WT / ECDD_WT_WARNING_DRIFT`
- `ECDD-WT / ECDD_WT_ERROR_STREAM`

## CHART-ERR-005

![CHART-ERR-005](../charts/output/CHART-ERR-005.png)

### 제목

평균 오류 차이 확대로 보는 HDDM 드리프트 경보

### 차트 목적

이 chart는 HDDM-A와 HDDM-W가 reference window와 recent window의 error mean 차이를 Hoeffding bound와 비교해 drift를 감지하는 방식을 설명한다. 이 예시에서는 mean difference가 초반 `0.01~0.08` 수준에서 시작해 마지막 `0.50`까지 상승하고, warning bound `0.26`과 drift bound `0.36`을 차례로 넘는다.

HDDM-A는 평균 차이를 직접 비교하고, HDDM-W는 최근 관측에 더 큰 가중치를 둔 weighted average를 사용할 수 있다. Two-sided 설정에서는 상방 error 증가뿐 아니라 하방 변화도 guard band로 함께 감시한다. 이 화면에서는 error trend도 `0.08`에서 `0.47`까지 상승해, mean difference의 bound 초과가 최근 오류 증가 방향과 일치한다.

이 차트는 다음 질문에 답한다.

```text
1. recent mean과 reference mean의 차이가 warning bound를 넘는가?
2. mean difference가 drift bound까지 초과하는가?
3. error 또는 weighted error trend도 같은 방향으로 이동하는가?
```

### 현재 상황 요약

이 예시에서는 mean difference가 t=21의 `0.24`까지는 warning bound `0.26` 아래에 있다가 t=22에서 `0.27`로 올라 warning 상태가 시작된다. 이후 t=26의 `0.38`이 drift bound `0.36`을 초과하고, 마지막 t=32에는 `0.50`까지 커진다. Error trend도 t=1의 `0.08`에서 t=22의 `0.31`, t=26의 `0.40`, t=32의 `0.47`로 계속 상승한다. 따라서 이 차트는 recent window의 오류 평균이 reference window보다 커지는 흐름이 Hoeffding bound를 넘어 HDDM drift 후보로 전환된 상황을 보여준다.

### 패널별 확인

이 chart는 세 영역으로 구성된다.

```text
좌측
  - Hoeffding bound chart
  - mean difference가 0.01에서 0.50까지 증가하는지 본다.
  - warning bound 0.26과 drift bound 0.36을 순서대로 넘는지 확인한다.
  - t=22 warning marker와 t=26 drift marker가 같은 상승 흐름 위에 있는지 확인한다.
  - lower guard band가 함께 표시되지만, 이 예시의 실제 변화는 상방 error 증가 방향이다.

우측 상단
  - error 또는 weighted error trend
  - error trend가 0.08에서 0.47까지 상승하는지 본다.
  - drift marker가 표시된 t=26의 error가 0.40이고 이후 0.47까지 계속 높아지는지 확인한다.

우측 하단
  - warning/drift marker timeline
  - t=1~21은 normal, t=22~25는 warning, t=26 이후는 drift 상태로 읽는다.
  - two-sided guard band 표시는 하방 변화도 감시할 수 있음을 뜻하지만, 현재 예시의 drift 판단은 상방 차이 초과에서 나온다.
```

상단 요약 영역에는 final difference, warning 시점, drift 시점을 표시한다.

### 해석 순서

먼저 좌측 Hoeffding bound chart에서 mean difference가 warning bound와 drift bound를 넘는지 확인한다.

```text
mean difference가 bound 아래에 있다
  -> reference와 recent window의 error 평균 차이가 통계적으로 충분하지 않다.

mean difference가 warning bound를 넘는다
  -> error 평균 shift 후보로 보고 추가 관측한다.

mean difference가 drift bound를 넘는다
  -> HDDM 기준 drift 후보로 본다.
```

그 다음 우측 상단 error trend를 확인한다. Bound 초과가 실제 error 또는 weighted error 상승과 같은 방향인지 확인해야 한다.

마지막으로 우측 하단 timeline에서 warning 이후 drift marker가 나타나는지, two-sided 설정이 필요한지 확인한다.

### Drift 후보 판단 기준

Mean difference가 warning bound를 넘은 뒤 drift bound를 초과하고, error 또는 weighted error trend가 같은 기간 상승하며, marker timeline이 drift 상태로 전환되면 HDDM 기반 drift 후보로 해석한다.

단, HDDM은 window 크기, confidence parameter, one-sided/two-sided 설정, weighting 방식에 민감하다. Window가 너무 작으면 bound가 불안정하고, 너무 크면 drift 감지가 늦어질 수 있다.

### 이 예시 차트의 해석

이 예시에서는 final diff가 `0.50`, warning 시점이 `t=22`, drift 시점이 `t=26`으로 표시되어 있다. 좌측 Hoeffding bound chart에서 mean difference는 t=1의 `0.01`에서 시작해 t=21의 `0.24`까지 warning bound 아래에 있다가, t=22의 `0.27`에서 warning bound `0.26`을 넘는다. 이후 t=26의 `0.38`에서 drift bound `0.36`을 초과하고, t=32에는 `0.50`까지 커진다.

우측 상단 error trend도 같은 기간 상승한다. Error는 t=1의 `0.08`에서 t=22의 `0.31`, t=26의 `0.40`, t=32의 `0.47`로 높아져 mean difference 상승과 방향이 일치한다. 우측 하단 timeline에서는 `t=1~21` normal 상태가 `t=22~25` warning을 거쳐 `t=26` 이후 drift 상태로 전환되고, two-sided guard band가 함께 표시된다. 따라서 이 예시는 recent error mean이 reference 대비 통계적으로 커진 HDDM drift 후보로 해석할 수 있다.

보고서 문장 예시는 다음과 같다.

```text
HDDM으로 reference window와 recent window의 error mean을 비교한 결과,
mean difference는 t=22에서 warning bound 0.26을 초과했고
t=26에서 drift bound 0.36을 초과했다.
Weighted error trend도 같은 기간 상승했으므로
Hoeffding-bound 기반 error-rate drift 후보로 해석할 수 있다.
```

### 금지해야 할 해석

이 차트만으로 다음을 단정하지 않는다.

```text
금지 1
  - bound 초과만으로 원인 feature를 특정한다.

금지 2
  - confidence parameter와 window size를 확인하지 않고 민감도를 평가한다.

금지 3
  - one-sided/two-sided 설정을 구분하지 않고 방향성을 해석한다.

금지 4
  - weighted average 사용 여부를 확인하지 않고 HDDM-A와 HDDM-W를 같은 방식으로 설명한다.
```

HDDM은 error mean 차이의 통계적 bound 초과를 감지한다. 입력 데이터 drift, class별 error 변화, calibration 변화는 별도 분석이 필요하다.

### 추가 확인 항목

HDDM drift 후보가 나타나면 다음을 추가 확인한다.

- reference/recent window 크기
- Hoeffding bound confidence parameter
- one-sided 또는 two-sided 설정
- HDDM-A 평균 비교인지 HDDM-W weighted average인지 여부
- warning/drift marker 전후 class별 error 변화
- DDM, RDDM, EDDM, ECDD-WT 등 다른 error detector와의 합의 여부
- 입력 feature drift와 모델 성능 지표 변화

### 적합한 사용 대상

이 chart는 다음 method variant에 적합하다.

- `HDDM-A / HDDM_A_HOEFFDING_BOUND`
- `HDDM-A / HDDM_A_WARNING_DRIFT`
- `HDDM-A / HDDM_A_TWO_SIDED`
- `HDDM-W / HDDM_W_WEIGHTED_AVERAGE`
- `HDDM-W / HDDM_W_WARNING_DRIFT`
- `HDDM-W / HDDM_W_RECENT_ERROR_WEIGHTING`

## CHART-ERR-006

![CHART-ERR-006](../charts/output/CHART-ERR-006.png)

### 제목

최근 정확도 하락으로 본 STEPD 드리프트 전환

### 차트 목적

이 chart는 STEPD가 recent window accuracy와 overall historical accuracy를 비교해 supervised stream drift를 감지하는 방식을 설명한다. 이 예시에서는 recent accuracy가 초반 `0.91`에서 t=26의 `0.64`까지 낮아진 뒤 마지막 `0.68`로 일부 회복되고, overall accuracy는 `0.91`에서 `0.78`까지 더 완만하게 하락한다.

STEPD는 최근 구간의 정답/오답 결과가 전체 구간의 성능보다 유의하게 나빠지는지를 본다. Recent accuracy가 overall accuracy보다 지속적으로 낮아지고 gap이 warning/drift threshold를 넘으면 error-rate drift 후보로 해석한다. 이 화면에서는 overall - recent accuracy gap이 t=15에서 `0.12`로 warning threshold `0.10`을 넘고, t=20에서 `0.16`으로 drift threshold `0.15`를 초과한다.

이 차트는 다음 질문에 답한다.

```text
1. recent accuracy가 overall accuracy보다 지속적으로 낮아지는가?
2. overall - recent accuracy gap이 warning threshold를 넘는가?
3. gap이 drift threshold까지 초과하며 state가 drift로 전환되는가?
```

### 현재 상황 요약

이 예시에서는 recent accuracy와 overall accuracy가 모두 t=1의 `0.91`에서 시작하지만, recent accuracy가 더 빠르게 떨어진다. t=15에는 recent accuracy `0.75`, overall accuracy `0.87`로 gap이 `0.12`가 되어 warning 상태가 시작된다. t=20에는 recent accuracy `0.68`, overall accuracy `0.84`로 gap이 `0.16`까지 벌어져 drift 상태로 전환된다. 이후 recent accuracy는 t=26의 `0.64`까지 낮아진 뒤 t=30에는 `0.68`로 일부 회복되지만, 이 차트는 최근 supervised 성능 저하가 전체 기준 대비 유의하게 커진 구간을 STEPD가 drift 후보로 표시한 상황을 보여준다.

### 패널별 확인

이 chart는 세 영역으로 구성된다.

```text
좌측
  - recent accuracy trend
  - overall accuracy trend
  - recent accuracy가 0.91에서 0.64까지 하락한 뒤 마지막 0.68로 일부 회복되는지 본다.
  - overall accuracy는 0.91에서 0.78까지 완만히 내려가므로 두 선의 간격이 커지는지 확인한다.
  - t=15 warning marker와 t=20 drift marker가 recent accuracy가 overall보다 낮아지는 흐름 위에 있는지 확인한다.

우측 상단
  - overall - recent accuracy gap
  - warning threshold
  - drift threshold
  - gap이 t=15에서 0.12로 warning threshold 0.10을 넘고, t=20에서 0.16으로 drift threshold 0.15를 초과하는지 본다.

우측 하단
  - normal/warning/drift state timeline
  - t=1~14는 normal, t=15~19는 warning, t=20 이후는 drift 상태로 읽는다.
  - warning 상태가 단일 marker로 끝나지 않고 drift 전환으로 이어지는지 확인한다.
```

상단 요약 영역에는 recent accuracy, overall accuracy, drift 시점을 표시한다.

### 해석 순서

먼저 좌측 accuracy trend에서 recent accuracy가 overall accuracy보다 낮아지는지 확인한다.

```text
recent accuracy가 overall accuracy와 비슷하다
  -> STEPD drift 증거가 약하다.

recent accuracy가 지속적으로 낮아진다
  -> supervised performance degradation 후보로 본다.

warning 이후 drift marker가 나타난다
  -> gap threshold 초과가 누적된 상태로 본다.
```

그 다음 우측 상단 threshold chart에서 gap이 warning threshold와 drift threshold를 순서대로 넘는지 확인한다.

마지막으로 우측 하단 timeline에서 normal, warning, drift 상태 전환이 실제 marker와 일치하는지 확인한다.

### Drift 후보 판단 기준

Recent accuracy가 overall accuracy보다 지속적으로 낮고, overall - recent accuracy gap이 warning threshold를 넘은 뒤 drift threshold까지 초과하며, state timeline이 drift로 전환되면 STEPD 기반 supervised error-rate drift 후보로 해석한다.

단, STEPD는 label이 필요한 detector다. Delayed label, label noise, class imbalance 변화가 있으면 recent accuracy 저하가 실제 모델 drift인지 데이터 수집/라벨링 문제인지 추가 확인해야 한다.

### 이 예시 차트의 해석

이 예시에서는 recent accuracy가 `0.68`, overall accuracy가 `0.78`, drift 시점이 `t=20`으로 표시되어 있다. 좌측 accuracy trend에서 recent accuracy는 t=1의 `0.91`에서 t=15의 `0.75`, t=20의 `0.68`, t=26의 `0.64`까지 내려간 뒤 t=30에 `0.68`로 일부 회복된다. Overall accuracy는 t=1의 `0.91`에서 t=15의 `0.87`, t=20의 `0.84`, t=30의 `0.78`로 더 천천히 낮아진다.

우측 상단 threshold chart에서는 overall - recent accuracy gap이 t=15에서 `0.12`가 되어 warning threshold `0.10`을 넘고, t=20에서 `0.16`으로 drift threshold `0.15`를 초과한다. 우측 하단 timeline도 `t=1~14` normal, `t=15~19` warning, `t=20` 이후 drift로 전환된다. 따라서 이 예시는 최근 supervised performance가 전체 기준 대비 유의하게 나빠진 STEPD drift 후보로 해석할 수 있다.

보고서 문장 예시는 다음과 같다.

```text
STEPD 모니터링 결과 recent accuracy는 0.68까지 하락했고
overall accuracy 0.78 대비 gap이 drift threshold를 초과했다.
t=15에서 warning 상태가 시작되고 t=20에서 drift 상태로 전환되었으므로
supervised error-rate drift 후보로 해석할 수 있다.
```

### 금지해야 할 해석

이 차트만으로 다음을 단정하지 않는다.

```text
금지 1
  - accuracy 저하만으로 입력 feature drift를 단정한다.

금지 2
  - label delay와 label quality를 확인하지 않고 STEPD 결과를 확정한다.

금지 3
  - class별 accuracy 차이를 보지 않고 전체 accuracy만으로 운영 영향을 판단한다.

금지 4
  - warning 상태를 drift 확정으로 해석한다.
```

STEPD는 supervised error-rate detector다. 성능 저하의 원인을 설명하려면 feature drift, label drift, class mix 변화, calibration 변화를 함께 분석해야 한다.

### 추가 확인 항목

STEPD drift 후보가 나타나면 다음을 추가 확인한다.

- recent/overall window 크기와 업데이트 방식
- label delay와 label noise 여부
- class별 accuracy, precision, recall 변화
- warning/drift threshold 설정
- DDM, RDDM, EDDM, ECDD, HDDM 등 다른 error detector와의 합의 여부
- 입력 feature drift 또는 class prior shift
- 배포, 정책, 데이터 수집 이벤트

### 적합한 사용 대상

이 chart는 다음 method variant에 적합하다.

- `STEPD / STEPD_ACCURACY_WINDOW`
- `STEPD / STEPD_WARNING_DRIFT`
- `STEPD / STEPD_SUPERVISED_STREAM`
