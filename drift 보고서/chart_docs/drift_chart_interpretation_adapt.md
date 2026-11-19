# Adaptive Model Drift Chart Interpretation

## CHART-ADAPT-001

![CHART-ADAPT-001](../charts/output/CHART-ADAPT-001.png)

### 차트 목적

이 chart는 Hoeffding Adaptive Tree가 stream drift를 감지하고 alternate tree를 성장시킨 뒤 replacement를 수행하는 흐름을 설명한다.

HAT는 node별 drift detector로 성능 저하를 감시한다. Warning 상태가 나타나면 alternate tree를 만들고, alternate tree가 main tree보다 나은 성능을 보이면 해당 subtree를 교체한다.

현재 상황은 운영 중인 HAT 모델이 스트리밍 데이터를 예측하다가 중간 구간에서 정확도가 떨어지고, 내부 detector가 이를 감지해 대체 tree를 키운 뒤 기존 tree 일부를 교체한 사례다. 초반에는 모델이 안정적이지만 `t=11` 이후 warning이 발생하고, `t=14`부터 alternate tree가 성장하며, `t=23` replacement 이후 accuracy가 회복된다.

이 예시 차트는 HAT가 실제로 어떤 순서로 반응했는지를 읽는 데 초점을 둔다. online accuracy는 초반 `0.91~0.92` 수준에서 시작해 warning 이후 계속 낮아지고, 최저 `0.72`까지 떨어진다. 그 사이 detector state는 `normal -> warning -> alternate -> replace`로 바뀌며, alternate tree node 수는 `64`까지 증가한 뒤 replacement 시점에 0으로 내려간다. 따라서 이 차트는 "성능이 떨어졌다"가 아니라 "성능 하락을 감지한 HAT가 대체 tree를 키우고 교체했는가"를 확인하는 화면이다.

이 차트는 다음 질문에 답한다.

```text
1. online accuracy가 하락하며 drift detector 상태가 바뀌는가?
2. warning 이후 alternate tree가 성장하는가?
3. replacement 이후 accuracy가 회복되고 tree size가 재구성되는가?
```

### 차트 구성

이 chart는 세 영역으로 구성된다.

```text
좌측
  - online accuracy trend
  - warning, alternate, replacement marker
  - 이 예시에서는 t=11 이후 하락이 이어져 t=19에서 accuracy가 0.72까지 내려가고, t=23 replacement 이후 다시 0.84 이상으로 회복된다.

우측 상단
  - detector state timeline
  - normal/warning/alternate/replace 상태
  - normal 구간은 안정 상태, warning 구간은 drift detector가 후보 신호를 낸 상태, alternate 구간은 대체 tree를 키우는 상태, replace 구간은 대체 tree가 main tree에 반영된 상태를 뜻한다.

우측 하단
  - main tree size trend
  - alternate tree size trend
  - replacement marker
  - alternate tree가 0에서 64 nodes까지 성장한 뒤 replacement에서 0으로 내려가고, main tree size가 57에서 42로 재구성되는지를 본다.
```

상단 요약 영역에는 accuracy min, replacement 시점, alternate tree node 수를 표시한다.

### 해석 순서

먼저 좌측 online accuracy trend에서 성능 하락과 replacement 이후 회복을 확인한다.

```text
accuracy가 안정적이다
  -> adaptive replacement 증거가 약하다.

accuracy가 하락하며 warning marker가 나타난다
  -> node detector가 drift 후보를 감지한 상태로 본다.

replacement 이후 accuracy가 회복된다
  -> alternate tree 교체가 유효했는지 확인한다.
```

그 다음 우측 상단 detector state timeline에서 상태 전환 순서를 확인한다. `normal`만 길게 유지되면 HAT가 적응 절차를 시작하지 않은 것이다. `warning`은 detector가 변화 후보를 감지했다는 뜻이고, `alternate`는 기존 subtree를 바로 버리지 않고 대체 tree를 병렬로 키우기 시작했다는 뜻이다. `replace`는 대체 tree가 충분히 좋아져 운영 tree 구조에 반영된 시점이다.

마지막으로 우측 하단 tree size trend에서 alternate tree가 실제로 성장했는지 확인한다. timeline에 `alternate`가 있어도 alternate node 수가 거의 늘지 않으면 적응 증거가 약하다. 이 예시처럼 alternate tree가 64 nodes까지 성장하고 replacement 시점에 0으로 내려가면, 대체 tree가 main tree에 흡수되었거나 교체가 완료된 것으로 읽는다.

### Drift 후보 판단 기준

Online accuracy가 하락하고 detector state가 warning에서 alternate로 전환되며, alternate tree size가 증가한 뒤 replacement marker가 나타나고 accuracy가 회복되면 HAT 기반 adaptive drift 대응 후보로 해석한다.

단, replacement는 drift 원인을 설명하는 것이 아니라 모델 구조가 stream 변화에 적응했다는 신호다. 교체가 과도하게 잦으면 detector 민감도나 stream noise를 점검해야 한다.

### 이 예시 차트의 해석

이 예시에서는 accuracy min이 `0.72`, replacement 시점이 `t=23`, alternate tree node 수가 `64`로 표시되어 있다. 좌측 accuracy trend는 초반 `0.91~0.92`에서 시작해 t=11 warning 이후 계속 떨어지고, t=19에서 `0.72`까지 낮아진다. t=23 replacement 이후에는 `0.84`, `0.86`, `0.88`, `0.90` 수준으로 회복된다.

우측 상단 timeline에서는 t=1~10 normal, t=11~13 warning, t=14~22 alternate, t=23 이후 replace 상태가 순차적으로 나타난다. 이는 detector가 먼저 이상 후보를 감지하고, 곧바로 replacement하지 않고 alternate tree를 키운 뒤 교체했다는 흐름을 보여준다. 우측 하단 tree size trend에서는 alternate tree가 t=11부터 성장해 t=22에서 `64` nodes에 도달하고, t=23 replacement에서 0으로 내려간다. 동시에 main tree size는 `57`에서 `42`로 줄어 재구성된다. 따라서 이 예시는 HAT가 alternate tree replacement로 drift 후보 구간에 적응한 사례로 해석할 수 있다.

보고서 문장 예시는 다음과 같다.

```text
HAT 모니터링 결과 online accuracy는 최저 0.72까지 하락했고,
t=23에서 alternate tree replacement가 수행되었다.
Replacement 이전 alternate tree는 64 nodes까지 성장했으며,
replacement 이후 accuracy는 회복되는 패턴을 보였다.
이는 HAT 기반 adaptive drift 대응 후보로 해석할 수 있다.
```

### 금지해야 할 해석

이 차트만으로 다음을 단정하지 않는다.

```text
금지 1
  - replacement 발생만으로 drift 원인을 특정한다.

금지 2
  - accuracy 회복을 장기 성능 안정화로 단정한다.

금지 3
  - alternate tree가 자주 생기는 원인을 stream drift로만 해석한다.

금지 4
  - detector state와 tree size를 보지 않고 accuracy만으로 HAT 적응을 설명한다.
```

HAT replacement는 적응 동작의 결과다. 실제 drift 원인과 운영 영향은 feature drift, error rate, segment 분석과 함께 확인해야 한다.

### 추가 확인 항목

HAT adaptive drift 후보가 나타나면 다음을 추가 확인한다.

- node별 drift detector 설정과 confidence
- alternate tree 생성/교체/삭제 횟수
- replacement 전후 validation 또는 delayed label 성능
- tree size 증가로 인한 latency, memory 영향
- replacement가 집중된 feature split 또는 segment
- ADWIN, DDM 등 detector 신호와의 합의 여부
- 배포, 정책, source 변화 이벤트

### 적합한 사용 대상

이 chart는 다음 method variant에 적합하다.

- `HAT / HAT_ADWIN_NODE_MONITORING`
- `HAT / HAT_ALTERNATE_TREE_REPLACEMENT`

## CHART-ADAPT-002

![CHART-ADAPT-002](../charts/output/CHART-ADAPT-002.png)

### 차트 목적

현재 상황은 운영 중인 champion 모델의 검증 AUC가 점진적으로 하락하다가 drift alarm이 발생하고, 그 뒤 재학습된 challenger 모델이 기존 champion보다 나은 성능을 보이는지 검토하는 사례다. 초반에는 champion AUC가 0.88 수준으로 안정적이지만 t=18 전후 0.74까지 내려가고, t=24 retrain event 이후 challenger가 0.86 이상으로 회복된다. 이 차트는 재학습이 실제 성능 회복 후보인지, 그리고 challenger를 승격하기 전에 latency와 delayed label 검증을 확인해야 하는지를 함께 보여준다.

이 chart는 drift alarm 이후 retraining workflow가 실제로 성능 회복으로 이어졌는지 설명한다.

DriftRetrainingClassifier는 drift detector가 alarm을 발생시키면 재학습 후보를 만들고, 기존 champion 모델과 challenger 모델을 비교한다. Challenger가 검증 성능에서 우세하고 운영 제약을 만족하면 승격 후보가 된다.

이 차트는 다음 질문에 답한다.

```text
1. retraining 이전 champion 성능이 하락하며 drift alarm이 발생했는가?
2. alarm 이후 retrain event가 명확히 기록되었는가?
3. challenger가 champion보다 성능을 회복시키며 승격 후보가 되었는가?
```

### 차트 구성

이 chart는 세 영역으로 구성된다.

```text
좌측
  - pre/post retraining validation AUC line
  - drift alarm marker
  - retrain event marker
  - challenger promotion marker

우측 상단
  - alarm and retrain workflow event timeline
  - normal/warning/alarm/retrain-monitor 상태

우측 하단
  - champion/challenger AUC, F1, latency 비교
```

상단 요약 영역에는 pre AUC, post AUC, retrain 시점을 표시한다.

### 해석 순서

먼저 좌측 performance line에서 retraining 이전 성능 하락과 alarm 시점을 확인한다.

```text
성능이 안정적이고 alarm이 없다
  -> retraining workflow 증거가 약하다.

성능 하락 후 drift alarm이 나타난다
  -> retraining trigger 후보로 본다.

retrain event 이후 challenger 성능이 회복된다
  -> retraining workflow가 drift 대응에 기여했는지 확인한다.
```

그 다음 우측 상단 timeline에서 warning, alarm, retrain, monitoring이 순차적으로 이어지는지 확인한다.

마지막으로 우측 하단 champion/challenger 비교에서 AUC와 F1이 개선되고 latency 증가가 운영 허용 범위인지 확인한다.

패널별로는 다음처럼 읽는다.

- **Pre/Post Retraining Performance**: champion AUC가 t=1~8에는 0.88~0.84 수준을 유지하다가 t=18 전후 0.74까지 낮아진다. t=18 drift alarm과 t=24 retrain event가 이 하락 구간 위에 표시되고, t=24 이후 challenger 선이 0.84, 0.86, 0.87, 0.89 수준으로 올라가는지 본다.
- **Alarm & Retrain Timeline**: 상태가 normal(t=1~13) → warning(t=13~18) → alarm(t=18~24) → retrain/monitor(t=24 이후) 순서로 이어지는지 확인한다. 이 순서가 맞아야 단순 성능 변동이 아니라 drift alarm이 재학습 절차로 연결된 사례로 해석할 수 있다.
- **Champion/Challenger**: challenger는 AUC 0.87, F1 0.82로 champion의 AUC 0.77, F1 0.70보다 높다. 다만 latency도 0.46에서 0.53으로 증가하므로, 성능 개선만 보고 자동 승격하지 말고 운영 지연 허용 범위를 함께 판단한다.

### Drift 후보 판단 기준

Champion 성능이 하락하고 drift alarm이 발생한 뒤 retrain event가 기록되며, challenger가 champion보다 높은 검증 성능을 보이고 post-retraining 성능이 목표선 이상으로 회복되면 retraining workflow 기반 drift 대응 후보로 해석한다.

단, retraining 성공은 drift 원인을 설명하지 않는다. 모델 승격 전에는 delayed label, holdout 성능, segment별 오류율, latency와 배포 리스크를 함께 확인해야 한다.

### 이 예시 차트의 해석

이 예시에서는 pre AUC가 `0.74`, post AUC가 `0.86`, retrain 시점이 `t=24`로 표시되어 있다. 좌측 performance line은 champion 성능이 drift alarm 전후로 하락하다가 retrain event 이후 challenger 성능이 회복되는 패턴을 보인다.

우측 상단 timeline은 normal, warning, alarm, retrain/monitor 순서로 workflow가 진행되었음을 보여준다. 우측 하단 비교에서는 challenger가 AUC와 F1에서 champion보다 높고 latency는 다소 증가한다. 따라서 이 예시는 drift alarm 이후 재학습과 challenger 승격 검토가 필요한 retraining workflow 사례로 해석할 수 있다.

보고서 문장 예시는 다음과 같다.

```text
Drift retraining workflow 모니터링 결과 champion의 validation AUC는
alarm 전후 0.74까지 하락했고, t=24에서 retrain event가 발생했다.
Challenger는 post-retraining AUC 0.86으로 회복되었으며 F1도 개선되었다.
Latency 증가는 별도 운영 기준으로 확인해야 하지만,
성능 관점에서는 challenger 승격 후보로 해석할 수 있다.
```

### 금지해야 할 해석

이 차트만으로 다음을 단정하지 않는다.

```text
금지 1
  - challenger 성능 개선만으로 drift 원인을 특정한다.

금지 2
  - retrain event 발생을 자동 승격으로 해석한다.

금지 3
  - post AUC 회복을 장기 운영 안정성으로 단정한다.

금지 4
  - latency, segment 성능, delayed label 검증 없이 challenger를 champion보다 항상 우수하다고 해석한다.
```

Retraining workflow는 drift 대응 절차를 보여준다. 실제 배포 판단은 성능 개선과 운영 제약을 모두 만족해야 한다.

### 추가 확인 항목

Drift retraining workflow 후보가 나타나면 다음을 추가 확인한다.

- drift detector 종류와 alarm threshold
- retraining window와 학습 데이터 freshness
- challenger holdout, delayed label, backtest 성능
- segment별 AUC, F1, calibration, error rate
- latency, memory, 비용 증가 여부
- champion rollback 기준과 canary 배포 결과
- alarm, retrain, promotion 이벤트의 감사 로그

### 적합한 사용 대상

이 chart는 다음 method variant에 적합하다.

- `DriftRetrainingClassifier / DRIFT_RETRAINING_WITH_ADWIN`
- `DriftRetrainingClassifier / DRIFT_RETRAINING_WITH_PAGE_HINKLEY`
- `DriftRetrainingClassifier / DRIFT_RETRAINING_CHAMPION_CHALLENGER`
