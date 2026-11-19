# Classifier-based Drift Chart Interpretation

## CHART-CLS-001

![CHART-CLS-001](../charts/output/CHART-CLS-001.png)

### 제목

도메인 분류기로 확인한 임베딩 분리

### 차트 목적

이 chart는 domain classifier가 baseline과 current sample을 얼마나 잘 구분하는지로 embedding 또는 feature space drift를 설명한다. 이 예시에서는 ROC-AUC가 `0.89`, score gap이 `0.41`, top feature가 `emb_17`로 표시된다.

Domain classifier 기반 drift detection은 sample에 시점 label을 붙여 `baseline`과 `current`를 구분하도록 학습한다. ROC-AUC가 random 기준보다 높고 score distribution이 분리되면 두 기간의 representation이 달라졌다는 증거로 본다. 이 화면에서는 baseline score가 낮은 probability 구간에, current score가 높은 probability 구간에 집중되고 `emb_17` importance가 `0.31`로 가장 높다.

이 차트는 다음 질문에 답한다.

```text
1. domain classifier ROC-AUC가 random 기준 0.5보다 충분히 높은가?
2. baseline/current domain score distribution이 분리되는가?
3. 중요한 embedding feature와 projection 분리가 같은 방향을 설명하는가?
```

### 현재 상황 요약

이 예시에서는 domain classifier ROC curve가 random diagonal보다 위에 있어 baseline/current sample을 구분한다. Score distribution은 baseline이 `0.19` 부근 density `38`에서 가장 높고, current는 `0.68` 부근 density `36`에서 가장 높아 probability 0.5 기준을 사이에 두고 분리된다. 우측 하단에서는 `emb_17` importance가 `0.31`, `emb_04`가 `0.24`로 높고, 작은 embedding projection에서도 baseline cluster는 왼쪽, current cluster는 오른쪽으로 분리된다. 따라서 이 차트는 domain classifier가 두 기간의 embedding 또는 feature space 차이를 감지한 classifier-based drift 후보 상황을 보여준다.

### 패널별 확인

이 chart는 세 영역으로 구성된다.

```text
좌측
  - domain classifier ROC curve
  - random classifier diagonal
  - ROC-AUC annotation
  - ROC curve가 random diagonal보다 위에 있고 ROC-AUC 0.89로 표시되는지 확인한다.
  - FPR 0.31에서 TPR 0.77, FPR 0.46에서 TPR 0.87처럼 classifier가 두 domain을 구분하는지 본다.

우측 상단
  - baseline/current domain probability distribution
  - probability 0.5 기준선
  - baseline score는 0.19 부근 density 38, current score는 0.68 부근 density 36에 집중되는지 확인한다.
  - probability 0.5 기준선 양쪽으로 두 분포가 나뉘는지 본다.

우측 하단
  - feature importance bar
  - embedding projection scatter
  - `emb_17` 0.31, `emb_04` 0.24가 주요 feature로 나타나는지 확인한다.
  - embedding projection에서 baseline/current cluster가 좌우로 분리되는지 본다.
```

상단 요약 영역에는 ROC-AUC, score gap, top feature를 표시한다.

### 해석 순서

먼저 ROC curve에서 domain classifier가 baseline/current를 실제로 구분하는지 확인한다.

```text
ROC-AUC가 0.5 근처다
  -> classifier-based drift 증거가 약하다.

ROC-AUC가 높다
  -> 두 기간의 feature 또는 embedding 분포가 구분 가능하다고 본다.

cross-validation AUC도 높다
  -> 과적합 가능성이 낮아진다.
```

그 다음 score distribution에서 baseline과 current probability가 양쪽으로 분리되는지 확인한다.

마지막으로 feature importance와 embedding projection에서 어떤 feature 또는 embedding 축이 분리를 설명하는지 확인한다.

### Drift 후보 판단 기준

Domain classifier ROC-AUC가 높고, baseline/current score distribution이 분리되며, 중요 feature와 embedding projection도 같은 분리 방향을 보이면 classifier-based embedding drift 후보로 해석한다.

단, domain classifier는 drift 원인을 직접 설명하지 않는다. 데이터 누수, train/test split 오류, class prior shift, sampling bias가 classifier 성능을 높일 수 있으므로 반드시 검증해야 한다.

### 이 예시 차트의 해석

이 예시에서는 ROC-AUC가 `0.89`, score gap이 `0.41`, top feature가 `emb_17`로 표시되어 있다. 좌측 ROC curve는 random diagonal보다 크게 위에 있고, FPR `0.31`에서 TPR `0.77`, FPR `0.46`에서 TPR `0.87`까지 올라 domain classifier가 baseline/current를 잘 구분한다.

우측 상단 score distribution은 baseline이 `0.19` 부근 density `38`의 낮은 probability에, current가 `0.68` 부근 density `36`의 높은 probability에 집중된다. 우측 하단에서는 `emb_17` importance가 `0.31`, `emb_04`가 `0.24`로 주요 feature로 나타나고 embedding projection도 baseline/current cluster 분리를 보인다. 따라서 이 예시는 classifier-based embedding drift 후보로 해석할 수 있다.

보고서 문장 예시는 다음과 같다.

```text
Domain classifier 기반 drift 분석 결과 baseline/current 구분 ROC-AUC는 0.89였다.
Domain probability distribution은 두 기간에서 분리되었고,
중요 feature는 emb_17, emb_04 순으로 나타났다.
Embedding projection에서도 cluster 분리가 확인되어 classifier-based embedding drift 후보로 해석할 수 있다.
```

### 금지해야 할 해석

이 차트만으로 다음을 단정하지 않는다.

```text
금지 1
  - 높은 ROC-AUC만으로 실제 원인 feature를 확정한다.

금지 2
  - data leakage 또는 split 오류 가능성을 확인하지 않는다.

금지 3
  - class prior shift를 feature drift와 혼동한다.

금지 4
  - cross-validation 없이 단일 classifier 성능만으로 drift를 확정한다.
```

Classifier 기반 drift는 구분 가능성을 보여준다. 원인 설명은 feature별 분포, segment 분석, downstream 성능 변화를 함께 확인해야 한다.

### 추가 확인 항목

Classifier-based drift 후보가 나타나면 다음을 추가 확인한다.

- time split, train/test split, leakage 여부
- cross-validated domain classifier 성능
- class prior, segment mix, source mix 변화
- feature importance 안정성
- embedding projection seed와 차원 축소 방식
- permutation test 또는 holdout domain classifier 결과
- downstream model accuracy, calibration, error rate 변화

### 적합한 사용 대상

이 chart는 다음 method variant에 적합하다.

- `Classifier 기반 embedding drift detection / DOMAIN_CLASSIFIER_ROC_AUC`
- `Classifier 기반 embedding drift detection / DOMAIN_CLASSIFIER_PROBABILITY_DRIFT`
- `Classifier 기반 embedding drift detection / CROSS_VALIDATED_DOMAIN_CLASSIFIER`
