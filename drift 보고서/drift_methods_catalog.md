# Drift Monitoring Method Catalog

## 1. 목적

이 문서는 drift monitoring 후보들을 기준으로, 먼저 **drift monitoring 방법 자체의 목록**을 확정하기 위한 카탈로그다.

여기서 "방법"은 다음 중 하나로 정의한다.

```text
DriftMethod
  - reference/current 또는 streaming window를 입력으로 받아
  - drift 후보 신호, 검정 통계량, 거리, alarm state, 또는 변화 설명 feature를 산출하고
  - 보고서에서 독립적으로 해석 규칙을 가질 수 있는 항목
```

따라서 모든 통계량, 전처리, 모델 내부 표현을 무조건 별도 방법으로 보지 않는다.

```text
방법으로 승격
  - 독립 detector 또는 drift test로 사용할 수 있다.
  - 산출 통계와 해석 기준이 명확하다.
  - 변종을 가질 만큼 선택 조건이 있다.
  - 보고서 문장 생성에서 독립 item으로 참조할 수 있다.

방법이 아니라 구성요소로 보류
  - 다른 detector의 입력 representation 또는 전처리다.
  - 특정 방법의 변종으로 흡수하는 편이 자연스럽다.
  - 단독으로 drift 해석을 만들기 어렵다.
```

## 2. Method 분류 체계

```text
DriftMethod
  BatchDistributionComparison
  StreamingChangeDetector
  SupervisedConceptDriftDetector
  MultivariateProcessControl
  RepresentationDriftMethod
  ExplanationDriftMethod
  DomainClassifierMethod
  OperationalAdaptationMethod
```

주의:

```text
Metric과 Method는 분리한다.
예를 들어 Wasserstein distance는 metric이지만,
reference/current window 비교와 threshold rule을 포함하면 drift monitoring method로도 쓸 수 있다.
```

## 3. 확정 Drift Method 목록

### 3.1 BatchDistributionComparison

정적 reference/current window를 비교하는 drift method다.

| ID | Method | 주 입력 | 주 출력 | 상태 | 변종 문서 |
|---|---|---|---|---|---|
| DM-001 | KS Test | 숫자형 feature, score, embedding dimension | KS statistic, p-value | 확정 | `algorithm_variants/ks_test_algorithm_variants.md` |
| DM-002 | Wasserstein Distance | 숫자형 feature, score, embedding summary | distance, trend | 확정 | `algorithm_variants/wasserstein_distance_algorithm_variants.md` |
| DM-003 | Chi-square Test | 범주형 빈도, class distribution | chi-square statistic, p-value | 확정 | `algorithm_variants/chi_square_test_algorithm_variants.md` |
| DM-004 | Fisher's Exact Test | 작은 표본의 범주형 contingency table | exact p-value | 확정 | `algorithm_variants/fisher_s_exact_test_algorithm_variants.md` |
| DM-005 | G-test | 범주형 빈도, likelihood ratio | G statistic, p-value | 확정 | `algorithm_variants/g_test_algorithm_variants.md` |
| DM-006 | PSI | score band, numeric bin, category proportion | PSI score | 확정 | `algorithm_variants/psi_algorithm_variants.md` |
| DM-007 | KL Divergence | 확률분포, histogram, category distribution | KL divergence | 확정 | `algorithm_variants/kl_divergence_algorithm_variants.md` |
| DM-008 | Jensen-Shannon Distance | 확률분포, histogram, topic distribution | JS divergence/distance | 확정 | `algorithm_variants/js_distance_algorithm_variants.md` |
| DM-009 | Hellinger Distance | 확률분포, category distribution, histogram | Hellinger distance | 확정 | `algorithm_variants/hellinger_distance_algorithm_variants.md` |
| DM-010 | Total Variation Distance | category distribution, probability vector | total variation distance | 확정 | `algorithm_variants/total_variation_distance_algorithm_variants.md` |
| DM-011 | L-Infinity Distance | category distribution, probability vector | max absolute proportion delta | 확정 | `algorithm_variants/l_infinity_distance_algorithm_variants.md` |
| DM-012 | Bhattacharyya Distance | histogram, Gaussian summary, category distribution | Bhattacharyya distance | 확정 | `algorithm_variants/bhattacharyya_distance_algorithm_variants.md` |
| DM-013 | Histogram Intersection Normalized Complement | histogram, image feature histogram | normalized complement score | 확정 | `algorithm_variants/histogram_intersection_normalized_complement_algorithm_variants.md` |
| DM-014 | Anderson-Darling Test | numeric sample | AD statistic, p-value | 확정 | `algorithm_variants/anderson_darling_test_algorithm_variants.md` |
| DM-015 | Cramer-von Mises Test | numeric sample | CvM statistic, p-value | 확정 | `algorithm_variants/cramer_von_mises_test_algorithm_variants.md` |
| DM-016 | Kuiper's Test | numeric 또는 circular sample | Kuiper statistic, p-value | 확정 | `algorithm_variants/kuiper_s_test_algorithm_variants.md` |
| DM-017 | Baumgartner-Weiss-Schindler Test | rank 기반 two-sample 비교 | BWS statistic, p-value | 확정 | `algorithm_variants/baumgartner_weiss_schindler_test_algorithm_variants.md` |
| DM-018 | Mann-Whitney U / Wilcoxon Rank Sum Test | numeric sample | U statistic, p-value | 확정 | `algorithm_variants/mann_whitney_u_test_algorithm_variants.md` |
| DM-019 | t-test 계열 | numeric metric mean | t statistic, p-value | 확정 | `algorithm_variants/t_test_algorithm_variants.md` |
| DM-020 | F-test / Variance Test 계열 | variance, model comparison statistic | F statistic, p-value | 확정 | `algorithm_variants/f_test_algorithm_variants.md` |
| DM-021 | Levene's Test | numeric sample variance | Levene statistic, p-value | 확정 | `algorithm_variants/levene_s_test_algorithm_variants.md` |
| DM-022 | Energy Distance | univariate 또는 multivariate sample | energy distance, p-value optional | 확정 | `algorithm_variants/energy_distance_algorithm_variants.md` |
| DM-023 | Epps-Singleton Test | numeric 또는 discrete sample | test statistic, p-value | 확정 | `algorithm_variants/epps_singleton_test_algorithm_variants.md` |
| DM-024 | MMD | embedding/vector sample | MMD score, p-value optional | 확정 | `algorithm_variants/mmd_algorithm_variants.md` |
| DM-025 | LSDD | vector sample | density difference score | 확정 | `algorithm_variants/lsdd_algorithm_variants.md` |

### 3.2 StreamingChangeDetector

시간 순서로 들어오는 stream에서 변화 시점 또는 alarm state를 산출하는 drift method다.

| ID | Method | 주 입력 | 주 출력 | 상태 | 변종 문서 |
|---|---|---|---|---|---|
| DM-026 | ADWIN | numeric stream, error stream, score stream | adaptive window, alarm | 확정 | `algorithm_variants/adwin_algorithm_variants.md` |
| DM-027 | KSWIN | numeric stream | KS-window alarm | 확정 | `algorithm_variants/kswin_algorithm_variants.md` |
| DM-028 | Page-Hinkley Test | numeric stream | PH statistic, alarm | 확정 | `algorithm_variants/page_hinkley_test_algorithm_variants.md` |
| DM-029 | CUSUM | numeric metric stream | cumulative sum, alarm | 확정 | `algorithm_variants/cusum_algorithm_variants.md` |
| DM-030 | EWMA | numeric metric stream | EWMA value, control limit, alarm | 확정 | `algorithm_variants/ewma_algorithm_variants.md` |
| DM-031 | Geometric Moving Average | numeric metric stream | GMA statistic, control limit | 확정 | `algorithm_variants/geometric_moving_average_algorithm_variants.md` |
| DM-032 | BOCD | numeric stream, probabilistic time series | change point probability | 확정 | `algorithm_variants/bocd_algorithm_variants.md` |
| DM-033 | SeqDrift | numeric stream, error stream | sequential bound, alarm | 확정 | `algorithm_variants/seqdrift_algorithm_variants.md` |
| DM-034 | SPRT | Bernoulli 또는 numeric stream | likelihood ratio decision | 확정 | `algorithm_variants/sprt_algorithm_variants.md` |

### 3.3 SupervisedConceptDriftDetector

label 또는 error stream을 전제로 concept drift 또는 performance drift 후보를 감지하는 방법이다.

| ID | Method | 주 입력 | 주 출력 | 상태 | 변종 문서 |
|---|---|---|---|---|---|
| DM-035 | DDM | classification error stream | warning state, drift state | 확정 | `algorithm_variants/ddm_algorithm_variants.md` |
| DM-036 | RDDM | classification error stream | warning state, drift state | 확정 | `algorithm_variants/rddm_algorithm_variants.md` |
| DM-037 | EDDM | distance between errors | warning state, drift state | 확정 | `algorithm_variants/eddm_algorithm_variants.md` |
| DM-038 | ECDD-WT | classification error stream | control statistic, warning/drift | 확정 | `algorithm_variants/ecdd_wt_algorithm_variants.md` |
| DM-039 | HDDM-A | classification error stream | Hoeffding-bound alarm | 확정 | `algorithm_variants/hddm_a_algorithm_variants.md` |
| DM-040 | HDDM-W | weighted error stream | weighted Hoeffding alarm | 확정 | `algorithm_variants/hddm_w_algorithm_variants.md` |
| DM-041 | STEPD | recent/overall accuracy window | warning state, drift state | 확정 | `algorithm_variants/stepd_algorithm_variants.md` |

### 3.4 MultivariateProcessControl

다변량 숫자 feature 또는 여러 metric의 결합 변화를 감지하는 방법이다.

| ID | Method | 주 입력 | 주 출력 | 상태 | 변종 문서 |
|---|---|---|---|---|---|
| DM-042 | Hotelling T2 | multivariate numeric window | T2 statistic, p-value/control limit | 확정 | `algorithm_variants/hotelling_t2_algorithm_variants.md` |
| DM-043 | MEWMA | multivariate metric stream | MEWMA statistic, control limit | 확정 | `algorithm_variants/mewma_algorithm_variants.md` |
| DM-044 | Mahalanobis Distance | multivariate feature, embedding summary | D2 distance, outlier/window score | 확정 | `algorithm_variants/mahalanobis_distance_algorithm_variants.md` |

### 3.5 RepresentationDriftMethod

이미지, 텍스트, embedding, model representation 같은 고차원 표현을 대상으로 drift를 감지하는 방법이다.

| ID | Method | 주 입력 | 주 출력 | 상태 | 변종 문서 |
|---|---|---|---|---|---|
| DM-045 | OCDD | feature vector, embedding vector | anomaly score, boundary violation rate | 확정 | `algorithm_variants/ocdd_algorithm_variants.md` |
| DM-046 | Feature Map Drift | model intermediate feature map | layerwise drift score | 확정 | `algorithm_variants/feature_map_drift_algorithm_variants.md` |
| DM-047 | Autoencoder Representation Drift | latent vector, reconstruction error | latent drift score, reconstruction error | 확정 | `algorithm_variants/autoencoder_representation_drift_algorithm_variants.md` |
| DM-048 | Graph Embedding Drift | graph/node embedding | embedding drift score | 확정 | `algorithm_variants/graph_embedding_drift_algorithm_variants.md` |
| DM-049 | LLM Query / Semantic Distance 기반 감지 | text/query embedding, topic distribution | semantic distance, topic shift | 확정 | `algorithm_variants/llm_query_semantic_distance_algorithm_variants.md` |
| DM-050 | Model Uncertainty Drift | confidence, entropy, uncertainty score | uncertainty distribution drift | 확정 | `algorithm_variants/model_uncertainty_drift_algorithm_variants.md` |

### 3.6 ExplanationDriftMethod

모델 설명 또는 의사결정 근거의 변화 자체를 감지하는 방법이다.

| ID | Method | 주 입력 | 주 출력 | 상태 | 변종 문서 |
|---|---|---|---|---|---|
| DM-051 | SHAP Drift | SHAP value matrix | SHAP distribution shift, importance shift | 확정 | `algorithm_variants/shap_drift_algorithm_variants.md` |
| DM-052 | Tree Feature 기반 감지 | time feature가 포함된 tabular data | time split count, feature importance | 확정 | `algorithm_variants/tree_feature_drift_algorithm_variants.md` |

### 3.7 DomainClassifierMethod

reference/current 구분 모델을 학습해 분포 차이를 탐지하거나 설명하는 방법이다.

| ID | Method | 주 입력 | 주 출력 | 상태 | 변종 문서 |
|---|---|---|---|---|---|
| DM-053 | Classifier 기반 embedding drift detection | embedding vector with domain label | ROC-AUC, domain classifier score | 확정 | `algorithm_variants/classifier_embedding_drift_algorithm_variants.md` |
| DM-054 | Text Domain Classifier Drift | text, text embedding, descriptor | ROC-AUC, domain classifier statistic | 확정 | `algorithm_variants/text_domain_classifier_drift_algorithm_variants.md` |

### 3.8 OperationalAdaptationMethod

순수 detector라기보다 drift detection 결과를 모델 적응 또는 운영 판단에 연결하는 방법이다. 독립 방법으로 두되, `Detector`보다는 `OperationalMethod`로 태깅한다.

| ID | Method | 주 입력 | 주 출력 | 상태 | 변종 문서 |
|---|---|---|---|---|---|
| DM-055 | HAT | labeled stream | drift state, alternate tree replacement, online accuracy | 확정 | `algorithm_variants/hat_algorithm_variants.md` |
| DM-056 | DriftRetrainingClassifier | base classifier, drift detector, labeled stream | retraining event, post-retrain metric | 운영 방법 | `algorithm_variants/driftretrainingclassifier_algorithm_variants.md` |

## 4. 변종으로 흡수할 항목

다음 항목은 별도 drift method로 두지 않고 상위 method의 algorithm variant로 흡수한다.

| 항목 | 흡수 대상 | 이유 |
|---|---|---|
| Welch's T-test | DM-019 t-test 계열 | Welch는 unequal variance 조건의 t-test 변종이다. |
| Wilcoxon Rank Sum Test | DM-018 Mann-Whitney U / Wilcoxon Rank Sum Test | 두 이름이 같은 rank-sum 계열을 가리키므로 하나로 합친다. |
| Streaming MMD | DM-024 MMD | streaming 방식은 MMD의 운영 변종이다. |
| Incremental KS Test | DM-001 KS Test 또는 DM-027 KSWIN | incremental/windowed 방식은 KS 계열의 streaming 변종이다. |
| Earth Mover's Distance | DM-002 Wasserstein Distance | 일반적으로 1-Wasserstein/EMD 계열로 함께 관리한다. |
| Empirical MMD | DM-024 MMD | MMD 추정 방식의 변종이다. |
| Cosine Distance | DM-049 LLM Query / Semantic Distance 기반 감지 또는 DM-053 Classifier 기반 embedding drift detection | embedding 방향 차이를 재는 metric이며, 단독 method보다 semantic/embedding drift method의 산출 metric으로 둔다. |
| Euclidean Distance | DM-044 Mahalanobis Distance 또는 DM-049 LLM Query / Semantic Distance 기반 감지 | vector 중심 이동을 재는 metric이며, scale/covariance 처리 여부에 따라 상위 distance method의 변종으로 둔다. |
| Z-test | DM-019 t-test 계열 또는 별도 proportion/mean test 후보 | 초안에는 도구 제공 목록에만 있어 우선 t-test/비율 검정 변종 후보로 보류한다. |

## 5. 구성요소로 보류할 항목

다음 항목은 drift method가 아니라 representation, preprocessing, 입력 신호, 또는 detector 내부 구성요소로 둔다.

| 항목 | 분류 | 이유 |
|---|---|---|
| PCA 기반 차원 축소 | PreprocessingComponent | drift를 산출하기보다 다른 detector 전에 차원을 줄이는 역할이 중심이다. |
| Sparse Random Projection | PreprocessingComponent | projection 후 KS/MMD/classifier 등을 적용하는 구성요소다. |
| Autoencoder latent representation | RepresentationComponent | 단독 method가 아니라 `Autoencoder Representation Drift`의 입력 표현이다. |
| model feature maps | RepresentationComponent | 단독 method가 아니라 `Feature Map Drift`의 입력 표현이다. |
| softmax outputs | SignalType | prediction drift 또는 uncertainty drift의 입력 신호다. |
| predicted class labels | SignalType | Chi-square, JS, PSI 등 범주형 drift method의 입력 신호다. |
| model uncertainty | SignalType 또는 MethodFamily | 단독 지표는 entropy/confidence이고, 방법으로는 `Model Uncertainty Drift`로 관리한다. |
| transformer embedding for text | RepresentationComponent | `LLM Query / Semantic Distance` 또는 `Text Domain Classifier Drift`의 입력 표현이다. |
| graph embedding for graph data | RepresentationComponent | `Graph Embedding Drift`의 입력 표현이다. |

## 6. 현재 확정 수량

```text
확정 DriftMethod
  - BatchDistributionComparison: 25
  - StreamingChangeDetector: 9
  - SupervisedConceptDriftDetector: 7
  - MultivariateProcessControl: 3
  - RepresentationDriftMethod: 6
  - ExplanationDriftMethod: 2
  - DomainClassifierMethod: 2
  - OperationalAdaptationMethod: 2

총계
  - 56개
```

단, `DM-056 DriftRetrainingClassifier`는 순수 detector가 아니라 운영 적응 방법이다. detector만 세면 55개다.

## 7. 다음 작업 규칙

변종 문서를 정리할 때는 이 문서를 기준으로 한다.

```text
1. 이 목록의 Method ID를 먼저 부여한다.
2. 각 Method마다 algorithm variant 문서를 하나 둔다.
3. 변종으로 흡수할 항목은 별도 method 문서를 만들지 않는다.
4. 구성요소로 보류한 항목은 MethodComponent 문서나 Representation 문서로 분리한다.
5. mindmap에는 DriftMethod와 MethodComponent를 다른 item type으로 넣는다.
```

따라서 기존 `algorithm_variants` 디렉터리의 62개 문서는 그대로 최종 method 수를 의미하지 않는다. 이 카탈로그 기준으로는 중복/변종/구성요소를 정리한 뒤 56개 method를 기준 목록으로 사용한다.
