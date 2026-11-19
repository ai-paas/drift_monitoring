# Explainability Drift Chart Interpretation

## CHART-EXPL-001

![CHART-EXPL-001](../charts/output/CHART-EXPL-001.png)

### 제목

risk_score 중심으로 바뀐 SHAP 설명 구조

### 차트 목적

이 chart는 SHAP value와 feature importance 순위가 baseline 대비 어떻게 달라졌는지 설명한다. 이 예시에서는 `risk_score`의 mean |SHAP|가 baseline `0.27`에서 current `0.36`으로 증가하고, 상단 요약에는 top shift `risk_score`, rank change `+3`, class heat `0.48`이 표시된다.

SHAP drift는 입력 feature 분포가 바뀌었는지뿐 아니라 모델이 예측에 사용하는 contribution 구조가 바뀌었는지 확인한다. 따라서 mean |SHAP| 순위, feature별 SHAP value distribution, class-wise SHAP heatmap을 함께 해석해야 한다. 이 화면에서는 `amount`가 `0.31`에서 `0.18`로 낮아지고, `channel`은 `0.17`에서 `0.24`로 높아져 feature contribution 구조가 함께 재배열된다.

이 차트는 다음 질문에 답한다.

```text
1. feature별 mean |SHAP| 중요도가 baseline 대비 바뀌었는가?
2. 주요 feature의 SHAP value distribution이 이동했는가?
3. 특정 class에서 SHAP drift가 집중되는가?
```

### 현재 상황 요약

이 예시에서는 baseline에서 `amount`와 `risk_score`가 각각 mean |SHAP| `0.31`, `0.27`로 가장 컸지만, current에서는 `risk_score`가 `0.36`으로 가장 높아지고 `channel`도 `0.24`까지 상승한다. 반대로 `amount`는 `0.18`, `tenure`는 `0.14`로 낮아진다. 우측 상단의 `risk_score` SHAP value distribution도 baseline peak가 `-0.04` 부근 density `36`인 반면 current peak는 `0.12` 부근 density `36`으로 양수 방향에 놓인다. 우측 하단 heatmap에서는 class C의 `risk_score`가 `0.48`로 가장 높고, class C `channel`도 `0.34`로 높아 특정 class에서 설명 변화가 집중된다. 따라서 이 차트는 모델의 설명 구조가 `risk_score`와 일부 class 중심으로 이동한 SHAP drift 후보 상황을 보여준다.

### 패널별 확인

이 chart는 세 영역으로 구성된다.

```text
좌측
  - baseline/current mean |SHAP| bar
  - rank change connector
  - `risk_score`가 0.27에서 0.36으로 증가하고, `channel`이 0.17에서 0.24로 증가하는지 확인한다.
  - `amount`가 0.31에서 0.18로 낮아져 baseline의 핵심 feature 비중이 약해지는지 본다.

우측 상단
  - 주요 feature의 SHAP value distribution
  - baseline/current 분포 비교
  - `risk_score` SHAP 분포가 baseline peak -0.04에서 current peak 0.12로 양수 방향 이동하는지 확인한다.

우측 하단
  - class-wise SHAP drift heatmap
  - feature x class drift score
  - class C의 `risk_score`가 0.48로 가장 높고, class C `channel` 0.34와 class B `risk_score` 0.36도 높은지 확인한다.
```

상단 요약 영역에는 top shift, rank change, class heat를 표시한다.

### 해석 순서

먼저 좌측 SHAP summary comparison에서 mean |SHAP|가 큰 feature와 순위가 이동한 feature를 확인한다.

```text
baseline/current bar가 비슷하다
  -> explanation drift 증거가 약하다.

특정 feature의 current mean |SHAP|가 크게 증가한다
  -> 해당 feature contribution 증가 후보로 본다.

중요도 순위가 크게 바뀐다
  -> global importance rank shift 후보로 본다.
```

그 다음 우측 상단 distribution에서 주요 feature의 SHAP value가 양수/음수 방향으로 이동했는지 확인한다.

마지막으로 우측 하단 class-wise heatmap에서 drift가 특정 class에 집중되는지 확인한다. Global summary와 class-wise heatmap이 같은 feature를 가리키면 설명력이 높다.

### Drift 후보 판단 기준

Mean |SHAP| 중요도 순위가 바뀌고, 주요 feature의 SHAP value distribution이 baseline 대비 이동하며, class-wise heatmap에서도 특정 class/feature drift가 확인되면 SHAP drift 후보로 해석한다.

단, SHAP drift는 feature contribution 변화 신호다. 데이터 drift, 모델 drift, label drift 중 어느 원인인지 바로 단정하면 안 된다.

### 이 예시 차트의 해석

이 예시에서는 top shift가 `risk_score`, rank change가 `+3`, class heat가 `0.48`로 표시되어 있다. 좌측 summary에서는 `risk_score`의 current mean |SHAP|가 `0.36`으로 baseline `0.27`보다 높아지고, `channel`도 `0.17`에서 `0.24`로 증가한다. 반면 `amount`는 `0.31`에서 `0.18`로 낮아져 baseline에서 크던 설명 비중이 약해진다.

우측 상단 distribution에서는 `risk_score` SHAP value가 current에서 양수 방향으로 이동한다. Baseline 분포는 `-0.04` 부근 density `36`이 peak이고, current 분포는 `0.12` 부근 density `36`이 peak다. 우측 하단 heatmap에서는 class C `risk_score`가 `0.48`로 가장 높고, class B `risk_score` `0.36`, class C `channel` `0.34`도 높다. 따라서 이 예시는 모델 설명 구조가 특정 feature와 class 중심으로 이동한 SHAP drift 후보로 해석할 수 있다.

보고서 문장 예시는 다음과 같다.

```text
SHAP drift 분석 결과, risk_score의 mean |SHAP| 중요도가 상승했고 rank change는 +3으로 나타났다.
risk_score의 SHAP value distribution은 current에서 양수 방향으로 이동했으며,
class-wise heatmap에서도 class B/C의 drift score가 높았다.
이는 explanation-level SHAP drift 후보로 해석할 수 있다.
```

### 금지해야 할 해석

이 차트만으로 다음을 단정하지 않는다.

```text
금지 1
  - SHAP 중요도 상승만으로 feature 원인 drift를 확정한다.

금지 2
  - SHAP value 분포 이동을 곧바로 모델 성능 저하로 해석한다.

금지 3
  - class-wise drift를 보지 않고 global SHAP summary만 보고 결론낸다.

금지 4
  - SHAP 계산 sample, background data, explainer 설정을 확인하지 않는다.
```

SHAP drift는 설명 구조의 변화다. 실제 원인과 영향은 feature drift, error rate, calibration, segment 분석과 함께 확인해야 한다.

### 추가 확인 항목

SHAP drift 후보가 나타나면 다음을 추가 확인한다.

- SHAP background dataset과 explainer 설정
- class별 sample 수와 class imbalance 변화
- feature별 입력 분포 drift
- global importance rank 변화의 반복성
- model version, feature engineering, preprocessing 변경
- 성능 지표, calibration, error rate 변화
- high drift feature의 segment별 업무 이벤트

### 적합한 사용 대상

이 chart는 다음 method variant에 적합하다.

- `SHAP Drift / SHAP_VALUE_DISTRIBUTION_TEST`
- `SHAP Drift / GLOBAL_IMPORTANCE_RANK_SHIFT`
- `SHAP Drift / CLASS_CONDITIONAL_SHAP_DRIFT`

## CHART-EXPL-002

![CHART-EXPL-002](../charts/output/CHART-EXPL-002.png)

### 제목

query_age 분기로 드러난 현재 구간 분리

### 차트 목적

이 chart는 tree 기반 domain classifier가 baseline/current 또는 time segment를 구분할 때 어떤 feature split을 사용하는지 설명한다. 이 예시에서는 `query_age`가 feature importance `0.34`, time split count `18`로 가장 높고, 대표 split path는 `query_age > 14d` 이후 `device = mobile` 조건에서 current `82%` leaf를 만든다.

Tree feature 기반 감지는 drift를 설명 가능한 split 조건으로 요약할 수 있다는 장점이 있다. Feature importance, time split count, 대표 split path, segment distribution을 함께 보면 어떤 feature와 segment가 drift 판정에 기여했는지 확인할 수 있다. 이 화면에서는 `region`도 importance `0.26`, time split `13`으로 높지만, 최종 current-dominant leaf는 `query_age`와 `device` 조건을 통해 만들어진다.

이 차트는 다음 질문에 답한다.

```text
1. domain/time 구분에 중요한 feature는 무엇인가?
2. time split이 특정 feature에 집중되는가?
3. 대표 split path가 current segment를 강하게 분리하는가?
```

### 현재 상황 요약

이 예시에서는 tree domain classifier가 baseline/current를 구분할 때 `query_age`를 가장 강한 분리 feature로 사용한다. 좌측 패널에서 `query_age`는 importance `0.34`와 time split `18`로 모두 1위이고, `region`은 importance `0.26`, time split `13`으로 뒤따른다. 우측 상단 split path는 `query_age > 14d`에서 먼저 나뉜 뒤 `device = mobile` 조건으로 current `82%` leaf에 도달한다. 우측 하단 segment distribution에서도 S1은 current `28%`지만 S4는 current `82%`로 높아, 이 차트는 특정 split 조건과 segment에서 current domain이 강하게 분리된 tree feature 기반 drift 후보 상황을 보여준다.

### 패널별 확인

이 chart는 세 영역으로 구성된다.

```text
좌측
  - feature importance bar
  - time split count bar
  - `query_age`가 importance 0.34, time split 18로 가장 높은지 확인한다.
  - `region` 0.26/13, `device` 0.18/8처럼 뒤따르는 feature와 격차를 함께 본다.

우측 상단
  - representative split path diagram
  - current-dominant leaf
  - `query_age > 14d` 이후 `device = mobile` 조건으로 current 82% leaf가 만들어지는지 확인한다.
  - `region = APAC` 분기와 비교해 어떤 path가 current를 더 강하게 분리하는지 본다.

우측 하단
  - segment별 baseline/current distribution comparison
  - S1 current 28%, S2 46%, S3 69%, S4 82%처럼 current 비중이 segment별로 증가하는지 확인한다.
```

상단 요약 영역에는 top feature, time splits, current leaf 비율을 표시한다.

### 해석 순서

먼저 좌측 feature importance와 time split count를 확인한다.

```text
importance가 낮고 split count도 낮다
  -> 해당 feature의 drift 설명력은 약하다.

importance와 split count가 모두 높다
  -> drift를 구분하는 핵심 feature 후보로 본다.

time split count만 높다
  -> 시간 proxy 또는 logging artifact 가능성을 확인한다.
```

그 다음 우측 상단 split path diagram에서 실제 tree가 어떤 조건으로 current segment를 분리하는지 확인한다.

마지막으로 우측 하단 segment distribution에서 split leaf가 baseline/current를 얼마나 다르게 포함하는지 확인한다.

### Drift 후보 판단 기준

Tree classifier의 top feature importance가 높고, time split count가 해당 feature에 집중되며, representative split path가 current-dominant leaf를 만들고, segment distribution에서 current 비율이 크게 높으면 tree feature 기반 drift 후보로 해석한다.

단, tree classifier는 time leakage, logging artifact, sampling bias를 쉽게 학습할 수 있다. Split 조건이 실제 의미 있는 feature 변화인지 반드시 검토해야 한다.

### 이 예시 차트의 해석

이 예시에서는 top feature가 `query_age`, time splits가 `18`, current leaf가 `82%`로 표시되어 있다. 좌측 패널에서 `query_age`는 feature importance `0.34`와 time split count `18`이 모두 가장 높다. `region`은 `0.26`과 `13`, `device`는 `0.18`과 `8`로 뒤따르므로, tree가 current domain을 구분할 때 `query_age`와 일부 보조 feature를 함께 사용한 것으로 읽는다.

우측 상단 split path는 `query_age > 14d` 이후 `device = mobile` 조건에서 current `82%` leaf를 만든다. 우측 하단 segment distribution에서도 S1은 current `28%`, S2는 `46%`, S3는 `69%`, S4는 `82%`로 표시되어 S4 segment가 current 중심으로 바뀐다. 따라서 이 예시는 tree classifier가 특정 feature split으로 current domain을 강하게 분리한 drift 후보로 해석할 수 있다.

보고서 문장 예시는 다음과 같다.

```text
Tree domain classifier 분석 결과, query_age가 가장 높은 feature importance를 보였고
time split count도 18회로 가장 많았다.
대표 split path는 query_age > 14d 및 device = mobile 조건에서 current 82% leaf를 만들었다.
이는 tree feature 기반 drift 후보로 해석할 수 있다.
```

### 금지해야 할 해석

이 차트만으로 다음을 단정하지 않는다.

```text
금지 1
  - top split feature만으로 실제 drift 원인을 확정한다.

금지 2
  - time leakage 여부를 확인하지 않고 time split을 의미 있는 drift로 해석한다.

금지 3
  - tree classifier의 overfitting 여부를 확인하지 않는다.

금지 4
  - split path 하나만 보고 전체 population drift를 단정한다.
```

Tree feature 기반 감지는 설명 가능한 후보를 제공한다. 실제 원인과 영향은 segment sample review와 다른 drift chart로 확인해야 한다.

### 추가 확인 항목

Tree feature 기반 drift 후보가 나타나면 다음을 추가 확인한다.

- time leakage, logging artifact, sampling policy 변경
- tree depth, min leaf size, validation AUC
- split path별 sample 수와 class/source 구성
- top feature의 원자료 분포 변화
- 다른 domain classifier와 embedding drift chart의 합의 여부
- downstream performance, calibration, error rate 변화
- drift segment의 업무 이벤트와 배포 이력

### 적합한 사용 대상

이 chart는 다음 method variant에 적합하다.

- `Tree Feature 기반 감지 / TIME_FEATURE_SPLIT_DETECTOR`
- `Tree Feature 기반 감지 / DOMAIN_CLASSIFIER_TREE`
