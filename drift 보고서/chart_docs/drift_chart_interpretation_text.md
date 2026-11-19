# Text Drift Chart Interpretation

## CHART-TEXT-001

![CHART-TEXT-001](../charts/output/CHART-TEXT-001.png)

### 제목

쿼리 의미 공간 이동과 토픽 비중 변화

### 차트 목적

이 chart는 LLM query의 semantic drift를 embedding space, semantic distance, topic mix, domain classifier 관점에서 함께 설명한다. 이 예시에서는 centroid cosine distance가 threshold `0.36`을 t=22에서 넘고, 최종 `0.58`까지 상승한다.

LLM query drift는 단어 빈도 변화만으로 판단하기 어렵다. Query embedding cluster가 이동하고 centroid distance가 커지며 topic 비중이 달라지는지 확인해야 한다. 이 화면에서는 세 번째 topic 비중이 baseline `0.20`에서 current `0.48`로 `+28pt` 증가하고, domain classifier AUC도 `0.82`로 표시되어 baseline/current 구분 가능성이 함께 나타난다.

이 차트는 다음 질문에 답한다.

```text
1. baseline/current query embedding cluster가 분리되는가?
2. semantic distance trend가 threshold를 넘는가?
3. topic proportion과 domain classifier가 drift를 지지하는가?
```

### 현재 상황 요약

이 예시에서는 baseline query embedding cluster가 왼쪽에 있고 current query embedding cluster가 오른쪽으로 이동해 두 군집이 분리되어 보인다. Semantic distance trend는 t=21의 `0.35`까지 threshold `0.36` 아래에 있다가 t=22의 `0.37`에서 threshold를 넘고, t=32에는 `0.58`까지 상승한다. Topic proportion은 baseline에서 topic 1/2/3이 `0.48`, `0.32`, `0.20`이지만 current에서는 `0.22`, `0.30`, `0.48`로 바뀌어 topic 3이 `+28pt` 증가한다. ROC AUC `0.82`도 baseline/current query를 구분할 수 있음을 보강하므로, 이 차트는 LLM query의 의미 공간과 주제 구성이 함께 이동한 semantic drift 후보 상황을 보여준다.

### 패널별 확인

이 chart는 세 영역으로 구성된다.

```text
좌측
  - query embedding projection scatter
  - baseline/current cluster
  - centroid shift line
  - baseline cluster는 왼쪽, current cluster는 오른쪽에 분리되어 있는지 확인한다.
  - centroid line이 baseline 중심에서 current 중심으로 이어져 의미 공간 중심 이동을 나타내는지 본다.

우측 상단
  - semantic distance trend
  - threshold line
  - cosine distance가 t=22의 0.37에서 threshold 0.36을 넘고, t=32의 0.58까지 지속 상승하는지 확인한다.

우측 하단
  - topic proportion stacked bar
  - optional domain classifier ROC curve
  - topic 3 비중이 baseline 0.20에서 current 0.48로 +28pt 증가하는지 본다.
  - ROC AUC 0.82가 embedding/topic 변화와 같은 방향의 baseline/current 구분 신호인지 확인한다.
```

상단 요약 영역에는 cosine distance, topic shift, domain AUC를 표시한다.

### 해석 순서

먼저 좌측 embedding projection에서 baseline/current query cluster가 분리되는지 확인한다.

```text
두 cluster가 대부분 겹친다
  -> semantic drift 증거가 약하다.

current cluster가 한 방향으로 이동한다
  -> query 의미 공간의 중심 이동 후보로 본다.

cluster가 여러 갈래로 분리된다
  -> topic별 segment drift를 추가 확인한다.
```

그 다음 semantic distance trend가 threshold를 넘는지 본다. 일시적 spike인지, 지속적으로 threshold 위에 있는지 구분해야 한다.

마지막으로 topic proportion과 domain classifier ROC를 확인한다. Topic mix 변화와 높은 domain AUC가 함께 나타나면 semantic drift 설명력이 높다.

### Drift 후보 판단 기준

Embedding projection에서 baseline/current cluster가 분리되고, centroid cosine distance가 threshold를 지속적으로 넘으며, topic mix와 domain classifier가 같은 방향의 변화를 지지하면 LLM query semantic drift 후보로 해석한다.

단, embedding model 변경, prompt template 변경, tokenizer/preprocessing 변경이 있으면 semantic drift처럼 보일 수 있다.

### 이 예시 차트의 해석

이 예시에서는 cosine distance가 `0.58`, topic shift가 `+28pt`, domain AUC가 `0.82`로 표시되어 있다. 좌측 projection에서는 current query embedding cluster가 baseline보다 오른쪽으로 이동해 분리되고, centroid shift line이 두 cluster 중심의 이동을 보여준다.

우측 상단 semantic distance trend는 t=21의 `0.35`까지 threshold 아래에 있다가 t=22의 `0.37`에서 threshold `0.36`을 넘고, 이후 t=32의 `0.58`까지 계속 상승한다. 우측 하단 topic bar에서는 세 번째 topic 비중이 baseline `0.20`에서 current `0.48`로 증가하고, ROC curve는 domain classifier AUC `0.82`로 baseline/current를 구분할 수 있음을 보여준다. 따라서 이 예시는 LLM query semantic drift 후보로 해석할 수 있다.

보고서 문장 예시는 다음과 같다.

```text
LLM query embedding 분석 결과, baseline/current query cluster가 분리되었고
centroid cosine distance는 0.58로 threshold를 초과했다.
Topic proportion도 주요 topic에서 +28pt 이동했으며 domain classifier AUC는 0.82였다.
이는 LLM query semantic drift 후보로 해석할 수 있다.
```

### 금지해야 할 해석

이 차트만으로 다음을 단정하지 않는다.

```text
금지 1
  - embedding projection 분리만으로 업무 원인을 단정한다.

금지 2
  - embedding model 또는 prompt template 변경 여부를 확인하지 않는다.

금지 3
  - topic label 품질을 확인하지 않고 topic shift를 원인으로 말한다.

금지 4
  - domain classifier AUC만으로 사용자 의도 변화를 확정한다.
```

Semantic drift는 query 의미 공간의 변화 신호다. 실제 사용자 의도, 품질 영향, retrieval 성능 변화는 별도 검증이 필요하다.

### 추가 확인 항목

LLM query semantic drift 후보가 나타나면 다음을 추가 확인한다.

- embedding model, prompt template, preprocessing 변경
- query language, locale, channel, source 변화
- topic labeling 품질과 topic별 sample 예시
- retrieval hit rate, answer quality, fallback rate 변화
- domain classifier feature leakage 여부
- time segment별 semantic distance 안정성
- 사람이 검토한 query intent sample

### 적합한 사용 대상

이 chart는 다음 method variant에 적합하다.

- `LLM Query / Semantic Distance 기반 감지 / QUERY_CENTROID_COSINE_SHIFT`
- `LLM Query / Semantic Distance 기반 감지 / TEXT_DOMAIN_CLASSIFIER_DRIFT`
- `LLM Query / Semantic Distance 기반 감지 / TOPIC_DISTRIBUTION_SHIFT`

## CHART-TEXT-002

![CHART-TEXT-002](../charts/output/CHART-TEXT-002.png)

### 제목

도메인 분류기로 본 텍스트 구성 변화

### 차트 목적

이 chart는 text domain classifier가 baseline과 current text를 얼마나 잘 구분하는지로 text domain drift를 설명한다. 이 예시에서는 ROC AUC가 `0.89`, KS score가 `0.47`, top descriptor가 `refund`로 표시된다.

Domain classifier는 두 기간 또는 두 domain의 text sample을 구분하도록 학습된다. 분류 성능이 높고 score distribution이 분리되면, text representation 또는 descriptor 구성에 의미 있는 차이가 있을 가능성이 있다. 이 화면에서는 baseline classifier score가 낮은 구간에, current score가 높은 구간에 집중되고 `refund policy` descriptor drift가 `0.32`로 가장 크다.

이 차트는 다음 질문에 답한다.

```text
1. domain classifier ROC AUC가 높은가?
2. baseline/current classifier score distribution이 분리되는가?
3. 어떤 text descriptor가 drift에 크게 기여하는가?
```

### 현재 상황 요약

이 예시에서는 domain classifier ROC curve가 random diagonal보다 크게 위에 있으며 AUC가 `0.89`로 baseline/current text를 잘 구분한다. Score distribution은 baseline이 `0.19` 부근 density `34`에서 가장 높고, current는 `0.68` 부근 density `35`에서 가장 높아 낮은 score와 높은 score로 분리된다. Descriptor drift bar에서는 `refund policy`가 `0.32`로 가장 크고, 그 다음 `enterprise SSO` `0.25`, `invoice issue` `0.18` 순서로 나타난다. 따라서 이 차트는 분류기가 두 text domain을 구분할 수 있고, 그 차이가 일부 업무 descriptor와 embedding 분리로도 보강되는 text domain drift 후보 상황을 보여준다.

### 패널별 확인

이 chart는 세 영역으로 구성된다.

```text
좌측
  - domain classifier ROC curve
  - random baseline diagonal
  - AUC 요약
  - ROC curve가 diagonal보다 위에 있고 AUC 0.89로 표시되는지 확인한다.
  - FPR 0.20에서 TPR 0.71, FPR 0.34에서 TPR 0.84처럼 낮은 false positive 구간에서도 분리력이 있는지 본다.

우측 상단
  - baseline/current classifier score distribution
  - score 분포 분리 여부
  - baseline score는 0.19 부근 density 34에 집중되고, current score는 0.68 부근 density 35에 집중되는지 확인한다.
  - 두 분포가 낮은 score와 높은 score로 나뉘는지 본다.

우측 하단
  - top text descriptor drift bar
  - embedding projection scatter 요약
  - `refund policy`가 0.32로 가장 크고 `enterprise SSO` 0.25, `invoice issue` 0.18이 뒤따르는지 확인한다.
  - 작은 embedding projection에서도 baseline/current 점들이 분리되는지 함께 본다.
```

상단 요약 영역에는 ROC AUC, KS score, top descriptor를 표시한다.

### 해석 순서

먼저 좌측 ROC curve에서 domain classifier가 baseline/current를 구분하는지 확인한다.

```text
ROC가 diagonal에 가깝다
  -> domain 차이를 분류기가 거의 구분하지 못한다.

ROC가 좌상단으로 휘고 AUC가 높다
  -> baseline/current text domain 차이가 크다.

AUC가 높지만 descriptor가 설명되지 않는다
  -> leakage 또는 proxy feature 가능성을 확인한다.
```

그 다음 우측 상단 score distribution을 확인한다. Baseline score가 낮고 current score가 높게 분리되면 classifier drift 신호가 명확하다.

마지막으로 descriptor drift bar와 embedding projection을 확인한다. 어떤 descriptor가 drift에 기여했는지와 embedding 분리가 같은 방향인지 확인한다.

### Drift 후보 판단 기준

Domain classifier ROC AUC가 높고, score distribution이 baseline/current로 분리되며, top descriptor drift와 embedding projection 분리가 함께 확인되면 text domain classifier drift 후보로 해석한다.

단, classifier가 text 길이, formatting, logging artifact, template 변경 같은 비의미적 차이를 학습했을 수 있으므로 descriptor와 sample 검토가 필요하다.

### 이 예시 차트의 해석

이 예시에서는 ROC AUC가 `0.89`, KS score가 `0.47`, top descriptor가 `refund`로 표시되어 있다. 좌측 ROC curve는 random diagonal보다 크게 위에 있고, FPR `0.20`에서 TPR `0.71`, FPR `0.34`에서 TPR `0.84`까지 올라 classifier가 baseline/current를 잘 구분한다.

우측 상단 score distribution도 baseline은 `0.19` 부근 density `34`의 낮은 score에, current는 `0.68` 부근 density `35`의 높은 score에 집중되어 분리된다. 우측 하단 descriptor bar에서는 `refund policy`가 `0.32`로 가장 큰 drift descriptor로 나타나고, `enterprise SSO` `0.25`, `invoice issue` `0.18`이 뒤따른다. 작은 embedding projection에서도 baseline/current 분리가 보인다. 따라서 이 예시는 text domain classifier 기반 drift 후보로 해석할 수 있다.

보고서 문장 예시는 다음과 같다.

```text
Text domain classifier 분석 결과 ROC AUC는 0.89, KS score는 0.47로 나타났다.
Classifier score distribution은 baseline/current로 분리되었고,
top descriptor는 refund policy였다.
이는 text domain classifier 기반 drift 후보로 해석할 수 있다.
```

### 금지해야 할 해석

이 차트만으로 다음을 단정하지 않는다.

```text
금지 1
  - classifier AUC만으로 사용자 의도 변화를 단정한다.

금지 2
  - text length, template, logging field 같은 leakage를 확인하지 않는다.

금지 3
  - descriptor drift bar만으로 업무 원인을 확정한다.

금지 4
  - classifier 학습/검증 split을 확인하지 않고 성능 수치를 신뢰한다.
```

Domain classifier drift는 두 text domain의 구분 가능성을 보여준다. 실제 의미 변화와 품질 영향은 sample review와 downstream metric으로 확인해야 한다.

### 추가 확인 항목

Text domain classifier drift 후보가 나타나면 다음을 추가 확인한다.

- train/test split과 time leakage 여부
- text length, language, channel, template 변경
- top descriptor별 sample 예시
- embedding model 또는 tokenizer 변경 여부
- retrieval quality, answer quality, fallback rate 변화
- semantic distance, topic shift chart와의 합의 여부
- 사람이 검토한 current query intent sample

### 적합한 사용 대상

이 chart는 다음 method variant에 적합하다.

- `Text Domain Classifier Drift / TEXT_DOMAIN_CLASSIFIER_ROC_AUC`
- `Text Domain Classifier Drift / TEXT_DOMAIN_CLASSIFIER_STAT_TEST`
- `Text Domain Classifier Drift / TEXT_DESCRIPTOR_DRIFT`
