# Graph Embedding Drift 알고리즘 변종 목록

## 1. 목적

이 문서는 `Graph Embedding Drift`를 하나의 고정된 detector로 보지 않고, drift monitoring에서 상황에 따라 선택해야 하는 **알고리즘 변종들의 family**로 정리한다.

핵심 목적은 다음이다.

```text
상황 조건 -> 적절한 Graph Embedding Drift 계열 변종 -> 출력 metric -> 주의사항 -> LLM 보고서 설명
```

---

## 2. Graph Embedding Drift의 위치

```text
methodFamily GRAPH_EMBEDDING_DRIFT
       ├─ algorithmVariant GRAPH_EMBEDDING_MMD
       ├─ algorithmVariant GRAPH_EMBEDDING_CENTROID_SHIFT
       └─ algorithmVariant NODE_REPRESENTATION_DRIFT
```

`Graph Embedding Drift`는 drift monitoring method 계열에 속한다. Graph Embedding Drift 계열을 drift monitoring 문맥에서 입력 데이터와 운영 목적에 따라 선택 가능한 변종으로 정리한다.

---

## 3. 공통 개념

```text
methodFamily GRAPH_EMBEDDING_DRIFT
  purpose ->
    Graph Embedding Drift 계열을 drift monitoring 문맥에서 입력 데이터와 운영 목적에 따라 선택 가능한 변종으로 정리한다.

  commonOutputs ->
    TEST_STATISTIC_OR_DISTANCE
    P_VALUE_OR_SCORE_OPTIONAL
    ALARM_STATE_OPTIONAL

  commonCautions ->
    detector 결과만으로 원인, 성능 저하, concept drift를 확정하지 않는다.
    reference 기간, current 기간, sample size, threshold 근거를 함께 보고한다.
    label이 없으면 supervised concept drift 또는 performance drift 확정 표현을 피한다.
```

---

## 변종: GRAPH_EMBEDDING_MMD

`GRAPH_EMBEDDING_MMD`는 graph를 embedding vector로 변환한 뒤 reference/current embedding 분포 차이를 MMD로 측정하는 변종이다. 노드와 edge 구조가 복잡해 원본 graph를 직접 비교하기 어려울 때, embedding 공간에서 graph 상태가 얼마나 달라졌는지 요약한다. 출력 MMD score는 두 기간의 graph representation 분포가 분리되는 정도로 해석한다.

사용 상황:
- 거래 네트워크, 지식 그래프, 사용자-아이템 graph처럼 구조적 관계 변화가 중요한 데이터에서
- graph neural network나 node2vec 계열 embedding을 운영 모니터링 신호로 사용할 때
- graph 전체의 representation 분포가 reference 기간과 달라졌는지 screening할 때

해석 방법:
- MMD score가 클수록 reference/current graph embedding 분포가 더 달라졌다는 뜻이다.
- p-value나 permutation 결과가 있으면 관측 MMD가 우연한 표본 변동으로 보기 어려운지 판단한다.
- alarm은 embedding 분포 변화가 운영 기준을 넘었다는 신호이며, 어떤 node나 edge가 원인인지는 별도 분석이 필요하다.
- projection scatter, group별 score, graph-level trend를 함께 보면 변화가 특정 node group에 집중됐는지 설명할 수 있다.

주의점:
- embedding 모델이나 차원이 바뀌면 score 비교 기준도 달라지므로 같은 embedding pipeline에서 비교해야 한다.
- MMD는 representation 분포 차이를 말할 뿐 graph 구조 변화의 업무 원인을 직접 알려주지 않는다.
- 표본 graph 수나 node 수가 적으면 score가 불안정할 수 있어 calibration과 반복 검증이 필요하다.

보고서 문장 예시:

```text
graph embedding을 GRAPH_EMBEDDING_MMD로 비교한 결과,
current embedding 분포의 MMD score가 기준 기간보다 높아졌다.
이는 graph representation 공간에서 구조 또는 관계 패턴 변화 후보가 관측됐다는 의미다.
다만 변화 원인은 MMD만으로 확정할 수 없으므로, node group별 score와 graph 생성 조건을 함께 확인해야 한다.
```

---

## 변종: GRAPH_EMBEDDING_CENTROID_SHIFT

`GRAPH_EMBEDDING_CENTROID_SHIFT`는 reference/current graph embedding의 중심점이 얼마나 이동했는지 측정하는 변종이다. 전체 분포 형태보다 embedding cloud의 평균 위치 변화가 주요 관심일 때 간단하고 설명 가능한 drift score로 사용할 수 있다. 출력 centroid distance는 graph representation의 대표 위치가 기준 대비 얼마나 이동했는지를 나타낸다.

사용 상황:
- graph embedding의 전체 평균 위치 이동을 빠르게 추적하고 싶을 때
- 운영 대시보드에서 graph-level drift trend를 단순한 거리 지표로 보고해야 할 때
- node group이나 graph batch별 중심 이동을 비교해 변화가 큰 구간을 선별할 때

해석 방법:
- centroid distance가 클수록 current embedding의 대표 위치가 reference 중심에서 더 멀어졌다는 뜻이다.
- threshold 초과 alarm은 중심 이동이 calibration 기준보다 크다는 운영 신호로 해석한다.
- 방향 벡터를 함께 보면 어떤 embedding 축 또는 projection 방향으로 이동했는지 설명할 수 있다.
- group별 centroid shift를 비교하면 변화가 전체 graph인지 특정 node group인지 구분하는 데 도움이 된다.

주의점:
- 중심 이동만 보기 때문에 분산, 다봉성, 꼬리 변화처럼 평균 위치가 거의 변하지 않는 drift는 놓칠 수 있다.
- embedding scale과 정렬 방식이 달라지면 centroid distance 비교가 무의미해질 수 있다.
- 중심 이동은 원인 확정이 아니라 representation 변화 후보이므로 graph 구조 지표와 함께 해석한다.

보고서 문장 예시:

```text
graph embedding 중심을 GRAPH_EMBEDDING_CENTROID_SHIFT로 추적한 결과,
current centroid가 reference centroid에서 의미 있게 멀어진 후보 신호가 관측됐다.
이는 graph representation의 대표 위치가 기준 기간과 달라졌을 가능성을 나타낸다.
다만 분포 형태 변화는 별도로 확인해야 하므로, MMD와 node group별 drift score를 함께 검토해야 한다.
```

---

## 변종: NODE_REPRESENTATION_DRIFT

`NODE_REPRESENTATION_DRIFT`는 graph 전체가 아니라 node 또는 node group의 embedding representation이 reference 기간과 달라졌는지 감시하는 변종이다. 전체 graph-level score가 크지 않아도 특정 node type, 커뮤니티, 중요 node 집합에서만 변화가 발생할 수 있으므로 국소적인 drift 후보를 찾는 데 쓴다. 출력은 node group별 distance, score, alarm, 또는 ranking 형태로 해석한다.

사용 상황:
- 특정 node type, 고객 집단, 상품군, 지역 graph segment의 representation 변화가 중요한 경우
- graph-level drift보다 어느 node group이 변화를 주도했는지 설명해야 할 때
- downstream 모델이 특정 node embedding에 민감하고 group별 영향 분석이 필요한 경우

해석 방법:
- node 또는 group별 drift score가 클수록 해당 representation이 reference 대비 더 많이 달라졌다는 뜻이다.
- ranking은 변화가 큰 node group의 우선순위를 제시하며, threshold 초과 항목은 후속 분석 후보로 본다.
- alarm은 해당 node group 변화가 운영 기준을 넘었다는 신호이며, 전체 graph drift와 별도로 보고할 수 있다.
- projection scatter와 group heatmap을 함께 보면 변화가 집중된 영역과 방향을 설명하기 쉽다.

주의점:
- node 매칭, 신규 node 유입, 삭제 node 처리 방식이 달라지면 representation 변화 해석이 왜곡될 수 있다.
- group별 표본 수가 작으면 score ranking이 불안정할 수 있다.
- node representation drift는 모델 성능 저하나 업무 원인을 직접 확정하지 않으므로 downstream metric과 연결해 확인한다.

보고서 문장 예시:

```text
node embedding을 NODE_REPRESENTATION_DRIFT로 분석한 결과,
일부 node group의 representation score가 기준보다 높게 나타났다.
이는 전체 graph보다 특정 node 집단에서 변화가 집중됐을 가능성을 보여주는 drift 후보 신호다.
다만 node 구성 변화와 신규 node 유입의 영향을 받을 수 있으므로, group별 표본 수와 downstream 성능을 함께 확인해야 한다.
```

---

## SelectionRule 카탈로그

```text
selectionRule GRAPH_EMBEDDING_DRIFT_DEFAULT_USE
  if ->
    input_signal_matches_method_assumption
    and reference_or_baseline_is_defined

  recommend ->
    대표 변종 중 운영 목적에 맞는 variant

  because ->
    같은 method family 안에서도 입력 신호, window 구성, threshold 목적에 따라 해석이 달라진다.

  caveat ->
    detector 결과만으로 성능 저하, concept drift, 원인을 확정하지 않는다.
```

---

## LLM 추천을 위한 최종 구조

```text
상황 조건
  -> selection rule
  -> algorithm variant 추천
  -> output metric 설명
  -> caveat 설명
  -> report guidance 생성
```

한 문장으로 정리하면:

> Graph Embedding Drift 카탈로그는 "이 방법이 무엇인가"가 아니라, "어떤 상황에서 어떤 변종을 선택하고 어떤 주의사항과 함께 설명해야 하는가"를 구조화한다.
