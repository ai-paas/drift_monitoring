# LLM Query / Semantic Distance 기반 감지 알고리즘 변종 목록

## 1. 목적

이 문서는 `LLM Query / Semantic Distance 기반 감지`를 하나의 고정된 detector로 보지 않고, drift monitoring에서 상황에 따라 선택해야 하는 **알고리즘 변종들의 family**로 정리한다.

핵심 목적은 다음이다.

```text
상황 조건 -> 적절한 LLM Query / Semantic Distance 기반 감지 계열 변종 -> 출력 metric -> 주의사항 -> LLM 보고서 설명
```

---

## 2. LLM Query / Semantic Distance 기반 감지의 위치

```text
methodFamily LLM_QUERY_SEMANTIC_DISTANCE
       ├─ algorithmVariant QUERY_CENTROID_COSINE_SHIFT
       ├─ algorithmVariant TEXT_DOMAIN_CLASSIFIER_DRIFT
       └─ algorithmVariant TOPIC_DISTRIBUTION_SHIFT
```

`LLM Query / Semantic Distance 기반 감지`는 semantic embedding drift 계열에 속한다. LLM query, prompt, text embedding의 의미론적 분포 변화를 감지한다.

---

## 3. 공통 개념

```text
methodFamily LLM_QUERY_SEMANTIC_DISTANCE
  purpose ->
    LLM query, prompt, text embedding의 의미론적 분포 변화를 감지한다.

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

## 변종: QUERY_CENTROID_COSINE_SHIFT

Query embedding의 reference 중심과 current 중심 사이 cosine distance를 측정하는 변종이다. 사용자 질문의 평균적인 의미 방향이 달라졌는지 빠르게 확인한다.

- 사용 상황: LLM 서비스에서 질문 주제, 의도, 업무 도메인의 중심이 이동했는지 감시할 때 적합하다.
- 해석 방법: cosine distance 또는 centroid shift가 커지면 current query 집합의 평균 의미가 reference와 멀어졌다고 본다.
- 주의점: embedding model, tokenizer, 전처리, 언어 비율이 바뀌면 실제 사용자 변화가 없어도 거리가 커질 수 있다.
- 보고서 문장 예시: "Query centroid cosine distance가 증가해 current 기간의 질문 의미 중심이 기준 기간과 다른 방향으로 이동한 후보 신호가 확인되었다."

---

## 변종: TEXT_DOMAIN_CLASSIFIER_DRIFT

Reference와 current 텍스트를 구분하는 보조 classifier를 학습해 두 기간이 얼마나 쉽게 분리되는지 보는 변종이다. 텍스트 분포 변화가 단순 거리보다 복합적일 때 유용하다.

- 사용 상황: prompt 유형, 표현 방식, topic mix, 사용자군 변화가 함께 섞여 있을 가능성이 있을 때 적합하다.
- 해석 방법: ROC-AUC나 분류 confidence가 높으면 두 기간의 텍스트 표현이 classifier 관점에서 구분 가능하다는 신호로 본다.
- 주의점: 시간 정보, 중복 문장, label leakage, 과적합을 통제하지 않으면 drift가 과장될 수 있다.
- 보고서 문장 예시: "텍스트 도메인 classifier가 reference와 current query를 높은 수준으로 구분해 의미적 입력 분포 변화 후보를 제시했다."

---

## 변종: TOPIC_DISTRIBUTION_SHIFT

Query를 topic 또는 cluster로 나눈 뒤 reference와 current의 구성 비율 변화를 비교하는 변종이다. 개별 문장보다 질문 유형의 mix 변화에 초점을 둔다.

- 사용 상황: 서비스 문의 유형, 업무 카테고리, intent cluster의 비중 변화를 운영 리포트로 설명해야 할 때 적합하다.
- 해석 방법: 특정 topic 비율의 증가/감소나 topic distribution distance가 커지면 의미적 구성 변화 후보로 본다.
- 주의점: topic model 버전, cluster 수, topic label이 바뀌면 비율 비교가 깨지므로 같은 모델 기준에서 비교한다.
- 보고서 문장 예시: "Current 기간에는 일부 query topic의 비중이 기준 기간과 달라져 LLM 입력 intent mix 변화 후보가 나타났다."

---

## SelectionRule 카탈로그

```text
selectionRule LLM_QUERY_SEMANTIC_DISTANCE_DEFAULT_USE
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

> LLM Query / Semantic Distance 기반 감지 카탈로그는 "이 방법이 무엇인가"가 아니라, "어떤 상황에서 어떤 변종을 선택하고 어떤 주의사항과 함께 설명해야 하는가"를 구조화한다.
