# Representation Drift Chart Interpretation

## CHART-REP-001

![CHART-REP-001](../charts/output/CHART-REP-001.png)

### 제목

block3 활성 변화로 본 표현 드리프트

### 차트 목적

이 chart는 모델 내부 feature map 또는 layer activation의 분포 변화가 어느 layer와 channel에 집중되는지 설명한다. 이 예시에서는 `block3` layer가 hot layer로 표시되고, 최대 drift score는 `block3`의 `c8`에서 `0.92`까지 올라간다.

Feature map drift는 입력 feature의 원자료 분포 변화가 아니라 모델 내부 representation의 변화를 본다. 따라서 어떤 layer에서 drift score가 커지는지, activation distribution이 이동하는지, embedding projection에서 baseline과 current가 분리되는지를 함께 확인해야 한다. 이 화면에서는 `block3`의 `c6~c9`가 `0.81`, `0.88`, `0.92`, `0.84`로 높고, activation histogram도 baseline peak가 중간 bin에 있는 반면 current peak는 오른쪽 bin으로 이동한다.

이 차트는 다음 질문에 답한다.

```text
1. drift score가 특정 layer와 channel에 집중되는가?
2. 선택된 layer의 activation distribution이 baseline 대비 이동했는가?
3. layer embedding projection에서 baseline과 current가 분리되는가?
```

### 현재 상황 요약

이 예시에서는 전체 layer 중 `block3`에서 drift score가 가장 강하게 집중된다. `conv1`은 대체로 `0.12~0.28`, `block1`은 `0.20~0.38` 수준이지만, `block3`은 `c5~c10`에서 `0.74`, `0.81`, `0.88`, `0.92`, `0.84`, `0.76`처럼 높은 값이 이어진다. 선택 layer의 activation distribution도 baseline은 bin 5에서 `35`로 가장 높고 current는 bin 7에서 `34`로 오른쪽에 peak가 생긴다. Embedding projection에서도 baseline cluster는 왼쪽, current cluster는 오른쪽으로 분리되어 있어, 이 차트는 `block3` representation 수준에서 current 데이터가 baseline과 달라진 후보 상황을 보여준다.

### 패널별 확인

이 chart는 세 영역으로 구성된다.

```text
좌측
  - layerwise drift heatmap
  - channel별 drift score
  - high drift layer 강조
  - `block3` 행이 강조되고 `c6~c9` score가 0.81, 0.88, 0.92, 0.84로 높은지 확인한다.
  - `conv1`, `block1`보다 깊은 layer인 `block2`, `block3`, `head` 쪽으로 score가 커지는지도 함께 본다.

우측 상단
  - baseline/current activation distribution
  - activation shift 방향
  - baseline histogram은 bin 5에서 35로 가장 높고, current는 bin 7에서 34로 peak가 오른쪽에 놓인다.
  - heatmap의 hot layer와 같은 `block3` activation 이동인지 확인한다.

우측 하단
  - layer embedding projection scatter
  - baseline/current cluster 분리
  - baseline cluster는 왼쪽, current cluster는 오른쪽에 분리되어 representation 공간 이동을 보강하는지 확인한다.
```

상단 요약 영역에는 max drift, hot layer, method를 표시한다.

### 해석 순서

먼저 좌측 heatmap에서 drift score가 어느 layer와 channel에 집중되는지 확인한다.

```text
전 layer에 낮은 score가 고르게 분포한다
  -> representation drift 증거가 약하다.

특정 layer와 channel에 high score가 집중된다
  -> 해당 representation block의 drift 후보로 본다.

초기 layer부터 head까지 전반적으로 높다
  -> 입력 분포 변화 또는 전역 domain shift 가능성을 확인한다.
```

그 다음 우측 상단 activation distribution에서 baseline과 current가 이동했는지 확인한다. Heatmap의 high layer와 distribution 이동이 같은 layer 기준이면 drift 설명력이 높다.

마지막으로 우측 하단 embedding projection에서 baseline/current cluster가 분리되는지 확인한다. Projection 분리는 representation space의 구조적 변화 가능성을 보여준다.

### Drift 후보 판단 기준

Layerwise heatmap에서 특정 layer의 drift score가 높고, 해당 layer의 activation distribution이 baseline 대비 이동하며, embedding projection에서 baseline/current가 분리되면 feature map drift 후보로 해석한다.

단, representation drift는 모델 내부 변화 신호다. 입력 feature drift, label drift, 성능 저하 원인과 1:1로 대응한다고 단정하면 안 된다.

### 이 예시 차트의 해석

이 예시에서는 max drift가 `0.92`, hot layer가 `block3`, method가 `MMD/KS`로 표시되어 있다. 좌측 heatmap에서 `block3`의 `c8`이 `0.92`로 가장 높고, 주변 `c6`, `c7`, `c9`도 각각 `0.81`, `0.88`, `0.84`로 높다. `block2`의 최대값은 `0.66`, `head`의 최대값은 `0.58`이므로 가장 강한 변화는 `block3` 중간 channel에 집중된 것으로 읽는다.

우측 상단 activation distribution에서는 baseline histogram이 bin 5의 `35`에서 가장 높고 current histogram은 bin 7의 `34`에서 가장 높아, current activation이 baseline보다 오른쪽으로 이동한다. 우측 하단 projection에서도 baseline과 current embedding cluster가 좌우로 분리된다. 따라서 이 예시는 `block3` feature map representation에서 drift가 발생한 후보로 해석할 수 있다.

보고서 문장 예시는 다음과 같다.

```text
Feature map drift 분석 결과, block3 layer에서 최대 drift score 0.92가 관찰되었다.
해당 layer의 activation distribution은 baseline 대비 오른쪽으로 이동했으며,
embedding projection에서도 baseline/current cluster가 분리되었다.
이는 block3 representation 수준의 drift 후보로 해석할 수 있다.
```

### 금지해야 할 해석

이 차트만으로 다음을 단정하지 않는다.

```text
금지 1
  - high drift layer만으로 원인 입력 feature를 특정한다.

금지 2
  - projection 분리만으로 모델 성능 저하를 단정한다.

금지 3
  - layer별 activation normalization 차이를 확인하지 않고 score를 비교한다.

금지 4
  - KS/MMD score를 layer 간 동일한 의미의 절대 수치로만 해석한다.
```

Feature map drift는 representation 변화의 위치를 찾는 도구다. 원인 분석과 성능 영향 평가는 별도 검증이 필요하다.

### 추가 확인 항목

Feature map drift 후보가 나타나면 다음을 추가 확인한다.

- layer별 activation normalization 방식
- channel별 high drift score의 반복성
- batch/source/time segment별 activation 차이
- 입력 feature drift 및 image/text preprocessing 변경
- downstream performance, error rate, calibration 변화
- KS와 MMD 결과의 합의 여부
- embedding projection의 차원 축소 방식과 random seed 안정성

### 적합한 사용 대상

이 chart는 다음 method variant에 적합하다.

- `Feature Map Drift / MODEL_FEATURE_MAP_KS`
- `Feature Map Drift / MODEL_FEATURE_MAP_MMD`
- `Feature Map Drift / LAYERWISE_FEATURE_MAP_DRIFT`

## CHART-REP-002

![CHART-REP-002](../charts/output/CHART-REP-002.png)

### 제목

복원 오차 증가로 본 오토인코더 표현 드리프트

### 차트 목적

이 chart는 autoencoder 기반 representation drift에서 reconstruction error와 latent space 분리가 어떻게 함께 나타나는지 설명한다. 이 예시에서는 current reconstruction error 분포가 baseline보다 오른쪽으로 이동하고, trend가 threshold `0.36`을 t=23에서 초과한다.

Autoencoder는 baseline representation을 잘 복원하도록 학습된다. Current 데이터의 reconstruction error가 커지고 latent projection이 baseline과 분리되면, 모델이 학습한 representation manifold에서 current 데이터가 벗어났을 가능성이 있다. 이 화면에서는 상단 요약에 p95 error `0.51`, threshold `0.36`, latent AUC `0.84`가 표시되어 reconstruction error 증가와 latent 분리가 함께 나타난다.

이 차트는 다음 질문에 답한다.

```text
1. current reconstruction error distribution이 baseline보다 오른쪽으로 이동했는가?
2. error trend가 threshold를 지속적으로 초과하는가?
3. latent projection에서 baseline/current cluster가 분리되는가?
```

### 현재 상황 요약

이 예시에서는 baseline reconstruction error 분포가 `0.14` 부근 밀도 `38`에서 가장 높고, current 분포는 `0.26` 부근 밀도 `37`로 오른쪽에 peak가 생긴다. Threshold `0.36` 오른쪽에도 current density가 `0.38`에서 `9`, `0.41`에서 `4`로 남아 있어 current tail이 baseline보다 커진다. Error trend는 t=1의 `0.10`에서 t=23의 `0.37`로 올라 threshold `0.36`을 넘고, t=32에는 `0.54`까지 상승한다. Latent projection에서도 baseline cluster와 current cluster가 분리되어, 이 차트는 autoencoder가 학습한 baseline manifold에서 current representation이 벗어난 후보 상황을 보여준다.

### 패널별 확인

이 chart는 세 영역으로 구성된다.

```text
좌측
  - baseline/current reconstruction error distribution
  - threshold line
  - baseline peak는 error 0.14의 density 38이고, current peak는 error 0.26의 density 37인지 확인한다.
  - threshold 0.36 오른쪽에 current tail이 남아 있는지 본다.

우측 상단
  - reconstruction error trend
  - threshold 초과 marker
  - error trend가 t=1의 0.10에서 t=23의 0.37로 올라 threshold 0.36을 넘는지 확인한다.
  - threshold 초과 후 t=32의 0.54까지 지속 상승하는지 본다.

우측 하단
  - latent projection scatter
  - baseline/current cluster 분리
  - baseline cluster는 왼쪽, current cluster는 오른쪽에 분리되어 error 증가를 representation 공간에서도 보강하는지 확인한다.
```

상단 요약 영역에는 p95 error, threshold, latent AUC를 표시한다.

### 해석 순서

먼저 좌측 reconstruction error distribution을 확인한다.

```text
baseline과 current 분포가 겹친다
  -> autoencoder reconstruction 기준 drift 증거가 약하다.

current 분포가 threshold 오른쪽으로 이동한다
  -> reconstruction error 증가 후보로 본다.

current tail만 threshold를 넘는다
  -> 일부 segment 또는 outlier 집중 가능성을 확인한다.
```

그 다음 우측 상단 trend에서 error가 일시적으로 튄 것인지, threshold 위에서 지속되는지 확인한다.

마지막으로 우측 하단 latent projection에서 baseline/current cluster가 분리되는지 확인한다. Error 증가와 latent 분리가 함께 나타나면 representation drift 설명력이 높다.

### Drift 후보 판단 기준

Current reconstruction error distribution이 baseline보다 높고 threshold 초과 비율이 커지며, error trend가 threshold 위로 지속되고, latent projection에서 baseline/current가 분리되면 autoencoder representation drift 후보로 해석한다.

단, reconstruction error는 scaling, autoencoder 용량, threshold 산정 방식에 민감하다. 모델이 과소적합 또는 과적합이면 drift가 아닌 reconstruction 품질 문제로 보일 수 있다.

### 이 예시 차트의 해석

이 예시에서는 p95 error가 `0.51`, threshold가 `0.36`, latent AUC가 `0.84`로 표시되어 있다. 좌측 distribution에서 baseline reconstruction error는 `0.14` 부근에서 density `38`로 가장 높고, current reconstruction error는 `0.26` 부근에서 density `37`로 가장 높다. Current 분포는 threshold `0.36` 오른쪽에도 tail이 남아 baseline보다 큰 reconstruction error 구간이 늘어난다.

우측 상단 trend에서는 reconstruction error가 t=22의 `0.35`까지는 threshold 아래에 있다가 t=23의 `0.37`에서 threshold `0.36`을 초과하고, 이후 t=32의 `0.54`까지 상승한다. 우측 하단 latent projection에서는 baseline과 current cluster가 분리되어 있다. 따라서 이 예시는 autoencoder가 학습한 baseline manifold에서 current representation이 벗어난 drift 후보로 해석할 수 있다.

보고서 문장 예시는 다음과 같다.

```text
Autoencoder representation drift 분석 결과,
current reconstruction error의 p95는 0.51로 threshold 0.36을 초과했다.
Error trend도 threshold 위에서 지속되었고,
latent projection에서는 baseline/current cluster 분리가 확인되었다.
이는 autoencoder representation drift 후보로 해석할 수 있다.
```

### 금지해야 할 해석

이 차트만으로 다음을 단정하지 않는다.

```text
금지 1
  - reconstruction error 증가만으로 원인 feature를 특정한다.

금지 2
  - autoencoder threshold 산정 방식을 확인하지 않고 drift 강도를 비교한다.

금지 3
  - latent projection 분리만으로 성능 저하를 단정한다.

금지 4
  - autoencoder 재학습 여부와 preprocessing 변화를 확인하지 않는다.
```

Autoencoder representation drift는 baseline manifold와 current representation의 차이를 보여준다. 원인 feature와 모델 영향은 별도 검증이 필요하다.

### 추가 확인 항목

Autoencoder representation drift 후보가 나타나면 다음을 추가 확인한다.

- reconstruction error threshold 산정 방식
- autoencoder 학습 기간과 baseline 대표성
- input scaling, normalization, preprocessing 변경
- latent projection의 차원 축소 방식과 seed 안정성
- error가 큰 sample의 source/time/segment 구성
- domain classifier AUC와 latent separation의 일관성
- downstream performance, calibration, error rate 변화

### 적합한 사용 대상

이 chart는 다음 method variant에 적합하다.

- `Autoencoder Representation Drift / LATENT_SPACE_DRIFT`
- `Autoencoder Representation Drift / RECONSTRUCTION_ERROR_DRIFT`
- `Autoencoder Representation Drift / AUTOENCODER_DOMAIN_CLASSIFIER`

## CHART-REP-003

![CHART-REP-003](../charts/output/CHART-REP-003.png)

### 제목

그래프 임베딩 분리와 허브 노드 드리프트

### 차트 목적

이 chart는 graph embedding drift가 graph-level representation과 node-level representation에서 어떻게 나타나는지 설명한다. 이 예시에서는 graph-level distance가 threshold `0.40`을 t=15에서 넘고, 최종 `0.67`까지 상승한다.

Graph embedding drift는 전체 graph embedding의 centroid shift나 MMD 증가뿐 아니라, 특정 node group의 drift score가 집중되는지도 함께 확인해야 한다. Graph-level distance만 보면 어느 부분 구조가 바뀌었는지 알기 어렵기 때문이다. 이 화면에서는 node drift score가 `hub` group에서 최대 `0.70`, `bridge` group에서 최대 `0.66`까지 높아져, graph 전체 이동과 특정 node group 변화가 함께 나타난다.

이 차트는 다음 질문에 답한다.

```text
1. current graph embedding이 baseline cluster에서 분리되는가?
2. drift score가 특정 node group 또는 시간 구간에 집중되는가?
3. graph-level distance trend가 threshold를 넘고 지속되는가?
```

### 현재 상황 요약

이 예시에서는 current graph embedding cluster가 baseline cluster의 오른쪽으로 분리되어 graph-level representation이 이동한 것처럼 보인다. 우측 상단 heatmap에서는 `hub` group의 drift score가 후반으로 갈수록 `0.48`, `0.62`, `0.70`까지 커지고, `bridge` group도 `0.43`, `0.58`, `0.66`으로 높아진다. 우측 하단 distance trend는 t=14의 `0.37`까지 threshold `0.40` 아래에 있다가 t=15의 `0.42`에서 alarm 구간으로 들어가고, 이후 t=24의 `0.67`까지 상승한다. 따라서 이 차트는 graph embedding 분리와 hub/bridge node group의 drift score 집중이 함께 나타난 graph representation drift 후보 상황을 보여준다.

### 패널별 확인

이 chart는 세 영역으로 구성된다.

```text
좌측
  - baseline graph embedding projection
  - current graph embedding projection
  - high-drift bridge node marker
  - baseline cluster는 왼쪽, current cluster는 오른쪽에 분리되어 있는지 확인한다.
  - current cluster 안에서 bridge node marker가 강조되어 node-level 변화 후보를 가리키는지 본다.

우측 상단
  - node group별 drift score heatmap
  - core, hub, bridge, leaf, new group
  - `hub` group이 t4~t6에서 0.48, 0.62, 0.70으로 높아지는지 확인한다.
  - `bridge` group도 t4~t6에서 0.43, 0.58, 0.66으로 올라 hub와 함께 후반 변화가 집중되는지 본다.

우측 하단
  - graph-level MMD 또는 centroid distance trend
  - distance threshold
  - alarm 이후 지속 구간
  - distance가 t=15의 0.42에서 threshold 0.40을 넘고, t=24의 0.67까지 지속 상승하는지 확인한다.
```

상단 요약 영역에는 final graph distance, node drift score max, alarm 시점을 표시한다.

### 해석 순서

먼저 좌측 graph embedding projection에서 baseline/current graph가 분리되는지 확인한다.

```text
baseline과 current embedding이 겹친다
  -> graph representation drift 증거가 약하다.

current embedding cluster가 이동한다
  -> graph-level representation shift 후보로 본다.

bridge 또는 hub node가 high drift로 표시된다
  -> 구조적 연결 변화 가능성을 확인한다.
```

그 다음 우측 상단 heatmap에서 drift score가 특정 node group에 집중되는지 확인한다.

마지막으로 우측 하단 distance trend에서 MMD 또는 centroid distance가 threshold를 넘고 일시 spike가 아니라 지속되는지 확인한다.

### Drift 후보 판단 기준

Current graph embedding이 baseline cluster에서 분리되고, node drift score heatmap에서 특정 node group의 score가 높으며, graph-level distance trend가 threshold를 지속적으로 넘으면 graph embedding drift 후보로 해석한다.

단, graph embedding은 graph size, node sampling, edge construction, embedding algorithm seed에 민감하다. 구조 변화가 실제 drift인지 graph extraction pipeline 변화인지 반드시 확인해야 한다.

### 이 예시 차트의 해석

이 예시에서는 graph-level distance가 `0.67`, node drift score max가 `0.70`, alarm 시점이 `t=15`로 표시되어 있다. 좌측 projection에서는 current graph embedding이 baseline cluster 오른쪽으로 이동하고 bridge node 일부가 high drift로 표시된다.

우측 상단 heatmap에서는 `hub` group이 후반 시간 구간에서 `0.48`, `0.62`, `0.70`까지 올라 가장 높고, `bridge` group도 `0.43`, `0.58`, `0.66`으로 함께 높다. 우측 하단 distance trend는 t=14의 `0.37`까지 threshold `0.40` 아래에 있다가 t=15의 `0.42`에서 threshold를 넘고, 이후 t=24의 `0.67`까지 계속 상승한다. 따라서 이 예시는 graph embedding과 node representation이 함께 이동한 graph representation drift 후보로 해석할 수 있다.

보고서 문장 예시는 다음과 같다.

```text
Graph embedding drift 분석 결과 current graph embedding은 baseline cluster에서 분리되었고,
graph-level distance는 t=15 이후 threshold를 초과해 최종 0.67까지 상승했다.
Node drift heatmap에서는 hub와 bridge group의 score가 높게 나타났다.
이는 graph representation drift 후보로 해석할 수 있다.
```

### 금지해야 할 해석

이 차트만으로 다음을 단정하지 않는다.

```text
금지 1
  - embedding projection 분리만으로 graph 구조 drift를 확정한다.

금지 2
  - node drift score 집중을 원인 node 확정으로 해석한다.

금지 3
  - graph size 또는 sampling 변화 여부를 확인하지 않는다.

금지 4
  - embedding algorithm seed와 projection 안정성을 확인하지 않는다.
```

Graph embedding drift는 representation 변화의 신호다. 실제 graph 구조 변화는 edge distribution, node attribute drift, community 변화와 함께 확인해야 한다.

### 추가 확인 항목

Graph embedding drift 후보가 나타나면 다음을 추가 확인한다.

- graph construction rule과 edge filtering 변경 여부
- graph size, density, degree distribution 변화
- node/edge attribute drift
- embedding algorithm, seed, dimension, normalization 설정
- hub, bridge, community별 drift score
- graph-level MMD, centroid shift, domain classifier 결과의 합의 여부
- downstream graph task 성능 변화

### 적합한 사용 대상

이 chart는 다음 method variant에 적합하다.

- `Graph Embedding Drift / GRAPH_EMBEDDING_MMD`
- `Graph Embedding Drift / GRAPH_EMBEDDING_CENTROID_SHIFT`
- `Graph Embedding Drift / NODE_REPRESENTATION_DRIFT`
