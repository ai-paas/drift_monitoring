# Drift Measurement Interpretation Guide

## 1. 목적

이 문서는 `drift_measurements_catalog.csv`에 정리된 측정값을 drift monitoring 관점에서 해석하기 위한 설명 문서다. 표 형태의 단순 매핑이 아니라, 각 측정값이 어떤 상황에서 의미가 있고 어떤 과잉 해석을 피해야 하는지를 항목별로 적는다.

측정값을 해석할 때는 항상 다음 순서를 따른다.

```text
측정값 확인
  -> 산출 method와 variant 확인
  -> reference/current 또는 stream 문맥 확인
  -> sample size, window size, threshold, p-value 계산 방식 확인
  -> 가능한 drift 해석과 금지 해석 분리
  -> 추가 확인 항목 제시
```

이 문서는 다음 자료를 함께 반영한다.

- `drift_measurements_catalog.csv`
- `drift_method_variant_links.csv`
- `drift_methods_catalog.md`
- 각 method별 `*_algorithm_variants.md`
- SciPy 통계 검정 및 거리 함수 문서
- Evidently data drift 문서
- Alibi Detect drift detection 문서
- River streaming drift detector 문서
- scikit-learn novelty/outlier detection 및 ROC-AUC 문서
- SHAP 문서

## 2. 공통 해석 원칙

### 2.1 p-value는 drift 크기가 아니다

`P_VALUE`는 특정 귀무가설 아래에서 현재보다 극단적인 test statistic이 나올 확률을 나타낸다. Alibi Detect 문서도 drift detection을 two-sample hypothesis testing으로 설명하며, p-value가 임계값보다 작을 때 reference와 current 분포가 같다는 귀무가설을 기각한다고 설명한다.

drift 보고서에서는 p-value를 "차이가 통계적으로 유의한가"의 근거로 쓰되, 변화 크기는 별도 statistic 또는 distance로 설명해야 한다. 예를 들어 KS test에서는 p-value와 함께 `KS_STATISTIC`을, Wasserstein 계열에서는 `WASSERSTEIN_DISTANCE`를 같이 제시한다.

특히 sample size가 크면 작은 차이도 유의해질 수 있고, sample size가 작으면 실질적으로 큰 차이도 유의하지 않을 수 있다. 다수 feature를 동시에 검정하면 Bonferroni 또는 FDR 같은 다중 검정 보정 여부도 보고서에 남겨야 한다.

### 2.2 distance는 차이의 크기이지 원인이 아니다

`WASSERSTEIN_DISTANCE`, `JENSEN_SHANNON_DISTANCE`, `COSINE_DISTANCE`, `MAHALANOBIS_DISTANCE`, `CENTROID_SHIFT`는 reference와 current가 얼마나 다른지를 수치화한다. 이 값은 drift 후보 신호를 만들 수 있지만, 성능 저하나 원인을 직접 말하지 않는다.

예를 들어 SciPy의 Wasserstein distance 문서는 이 거리를 두 1차원 분포 사이의 optimal transport 또는 Earth mover's distance로 설명한다. 이는 "분포를 맞추기 위해 얼마나 이동해야 하는가"를 말하지만, 왜 이동했는지 또는 모델 성능에 어떤 영향을 주었는지는 별도 확인이 필요하다.

### 2.3 alarm은 조사 시작 신호다

`DRIFT_ALARM_STATE`, `WARNING_STATE`, `THRESHOLD_EXCEEDANCE`, `HYPOTHESIS_DECISION_STATE`는 detector가 사전에 정한 rule을 만족했다는 상태값이다. 이 값은 원인 분석을 시작하라는 신호이지, 원인이나 조치 자체가 아니다.

River의 ADWIN 문서는 adaptive window 내부의 과거/최근 sub-window 평균 비교로 change를 판단한다고 설명한다. 따라서 ADWIN alarm은 "현재 stream에서 window 평균 구조가 바뀌었다"는 신호로 해석해야 하며, 입력 신호가 feature인지 error rate인지 confidence인지에 따라 보고서 표현이 달라져야 한다.

### 2.4 threshold와 policy는 결과의 일부다

`CONTROL_LIMIT`, `SEQUENTIAL_BOUND`, `FALSE_ALARM_TARGET`, `METHOD_POLICY`, `PROJECTION_COUNT`, `APPROXIMATION_ERROR_BOUND`는 drift 자체의 크기라기보다 detector 결과의 신뢰도와 재현성을 결정하는 설정 또는 부가 정보다.

Evidently 문서도 drift threshold의 의미가 method마다 다르며, p-value threshold인지 distance threshold인지 구분해야 한다고 설명한다. 따라서 threshold 초과 여부만 보고하지 말고 threshold가 어떤 방식으로 정해졌는지 함께 남겨야 한다.

### 2.5 label 기반 측정값은 supervised 조건을 확인한다

`ERROR_RATE`, `ONLINE_OR_PRE_POST_PERFORMANCE`, DDM/RDDM/HDDM/STEPD류의 `WARNING_STATE`와 `DRIFT_ALARM_STATE`는 label 또는 error stream을 전제로 한다. label이 없거나 지연되는 환경에서는 concept drift 또는 performance drift를 확정하지 않는다.

feature distribution drift는 covariate shift 후보이고, prediction score drift는 prediction drift 후보이며, supervised concept drift 확정에는 label 또는 성능 검증이 필요하다.

## 3. 측정값별 해석

### MEAS-001 ADAPTATION_EVENT

`ADAPTATION_EVENT`는 detector가 단순히 drift를 감지한 것을 넘어 모델 또는 기준 상태를 바꾼 사건을 뜻한다. HAT의 alternate tree 생성/교체, RDDM의 reset event처럼 이전 기준과 이후 기준이 달라지는 시점이 여기에 해당한다.

값 형태: 범주형 event 값이다. 일반적으로 boolean flag, event type 문자열, 또는 timestamp와 함께 기록된다. 값의 예는 `alternate_tree_created`, `tree_replaced`, `reset_event`이며, 크고 작음을 비교하는 수치형 값이 아니다.

값 크기 해석: 높고 낮음의 개념이 없다. 해석은 이벤트 발생 여부, 이벤트 종류, 발생 시점, 전후 성능 변화로 한다. 이벤트 빈도를 별도로 집계한 경우에는 빈도가 높을수록 모델 또는 detector가 자주 적응했다는 뜻이며, 운영 안정성 점검이 필요하다.

drift 관점에서는 이 값을 "drift 대응 또는 적응이 발생한 시점"으로 해석한다. 이 이벤트 전후로 online accuracy, error rate, feature distribution, prediction distribution이 어떻게 바뀌었는지를 같이 봐야 한다.

주의할 점은 adaptation event가 성공을 의미하지 않는다는 것이다. 모델이 교체되었거나 detector가 reset되었다는 사실은 운영 로그의 경계선일 뿐이다. 보고서에서는 "적응 이벤트 이후 성능이 회복되었는지", "새 기준이 과거 기준과 비교 가능한지", "이벤트가 반복되는지"를 별도 검증 항목으로 제시한다.

### MEAS-002 ANOMALY_SCORE

`ANOMALY_SCORE`는 current sample이 reference 또는 정상 학습 데이터에서 얼마나 벗어나는지를 나타내는 점수다. scikit-learn의 novelty/outlier detection 문서는 새 관측값이 기존 관측값과 같은 분포에서 온 것으로 볼 수 있는지, 또는 outlier/novelty인지 판단하는 문제로 설명한다.

값 형태: 주로 실수형 점수다. 범위와 방향은 detector마다 다르다. 예를 들어 reconstruction error는 보통 0 이상의 실수이고 클수록 이상하지만, 일부 outlier detector의 score는 클수록 정상 또는 작을수록 이상으로 정의될 수 있다. 반드시 해당 method의 score direction을 함께 기록한다.

값 크기 해석: score 방향이 "클수록 이상"이면 낮은 값은 reference 정상 영역과 유사하다는 뜻이고 높은 값은 OOD 또는 anomaly 후보가 강하다는 뜻이다. 반대로 "클수록 정상"인 구현에서는 해석이 뒤집힌다. 보고서에는 반드시 `higher_is_more_anomalous` 같은 방향성 metadata를 둔다.

drift 관점에서는 anomaly score 자체보다 score 분포의 이동을 본다. 개별 샘플의 score가 높아졌다는 사실보다, current window에서 높은 score의 비율이 늘었는지, 특정 segment 또는 feature 조합에서 score가 집중되는지가 중요하다.

이 값은 label 없이도 빠르게 사용할 수 있지만, anomaly와 drift는 동일하지 않다. 데이터 품질 문제, schema 변경, outlier batch, 정상적인 신규 segment 유입도 anomaly score를 올릴 수 있다. 보고서에서는 "정상 경계 밖 샘플 증가" 또는 "OOD 후보 증가"로 표현하고 concept drift 확정 표현은 피한다.

### MEAS-003 APPROXIMATION_ERROR_BOUND

`APPROXIMATION_ERROR_BOUND`는 exact 계산 대신 approximate quantile, projection, sketch, histogram 같은 근사 계산을 쓴 경우의 오차 범위 또는 불확실성 정보다.

값 형태: 보통 0 이상의 실수형 오차 경계다. 단위는 원 측정값과 같거나 normalized error일 수 있다. 값이 작을수록 exact 계산에 가깝다는 뜻이지만, 어떤 확률 수준의 bound인지 구현별로 다를 수 있다.

값 크기 해석: 낮을수록 근사 결과를 더 신뢰할 수 있다. 높을수록 statistic 또는 distance가 threshold 근처에 있을 때 판정 불확실성이 커진다. error bound가 큰 경우 drift 여부를 단정하지 말고 exact 계산, 더 촘촘한 summary, 더 많은 projection으로 재확인한다.

drift 관점에서는 이 값을 drift 강도로 해석하지 않는다. 근사 결과가 threshold 근처에 있을 때 판정 신뢰도를 판단하는 보조 정보로 쓴다. 예를 들어 approximate KS statistic이 threshold를 아주 조금 넘었지만 error bound가 크다면, "drift 확정"보다 "재계산 또는 exact 방식 확인 필요"로 쓰는 편이 안전하다.

보고서에는 근사 알고리즘 이름, error bound 산정 방식, quantile error 또는 projection 수, exact 계산 가능 여부를 함께 남긴다.

### MEAS-004 BUFFERED_INSTANCE_COUNT

`BUFFERED_INSTANCE_COUNT`는 warning 또는 drift 구간에서 보관된 instance 수다. DDM류에서 warning state 이후의 데이터를 재학습 후보 또는 분석 대상으로 저장할 때 의미가 있다.

값 형태: 0 이상의 정수 count다. window 또는 warning 구간 단위로 집계된다. 범위 상한은 traffic 양, buffer policy, retention policy에 의해 결정된다.

값 크기 해석: 낮은 값은 분석 또는 재학습에 사용할 warning/drift 후보 데이터가 부족할 수 있음을 뜻한다. 높은 값은 충분한 분석 데이터가 있다는 뜻일 수 있지만, drift 강도가 크다는 뜻은 아니다. traffic 증가나 warning 지속 시간이 길어서 count가 커졌을 수 있다.

drift 관점에서는 이 값이 변화의 강도라기보다 조치 가능 데이터의 규모를 나타낸다. count가 충분하면 warning 구간 데이터로 feature 분포, class별 오류율, confusion matrix를 재분석할 수 있다. count가 너무 작으면 원인 분석 또는 재학습 판단에 불확실성이 크다.

주의할 점은 instance 수가 많다고 drift가 강하다는 뜻은 아니라는 것이다. warning이 오래 지속되었거나 운영 traffic이 많았기 때문일 수 있다.

### MEAS-005 CENTROID_SHIFT

`CENTROID_SHIFT`는 embedding 또는 vector representation의 중심이 reference 대비 얼마나 이동했는지를 나타낸다. LLM query, image embedding, model feature vector의 평균 위치 변화를 설명할 때 유용하다.

값 형태: 보통 0 이상의 실수형 거리다. Euclidean 기반이면 embedding scale에 영향을 받고, cosine 기반이면 0에서 2 사이의 거리 또는 0에서 1 사이의 유사도 변환값일 수 있다. 사용한 거리 정의를 반드시 명시한다.

값 크기 해석: 낮은 값은 reference와 current의 중심 위치가 비슷하다는 뜻이다. 높은 값은 embedding/vector 중심이 이동했다는 뜻이며 semantic/topic/user mix 변화 후보가 강해진다. 단, 중심 이동이 작아도 cluster 구조나 분산 변화는 존재할 수 있다.

drift 관점에서는 "표현 공간에서 중심이 이동했다"는 후보 신호다. topic mix 변화, 사용자군 변화, prompt 유형 변화, embedding model 변경, preprocessing 변경이 모두 centroid shift로 나타날 수 있다.

이 값만으로 전체 embedding distribution drift를 판단하면 안 된다. 중심은 같지만 분산, tail, cluster 구조가 달라질 수 있고, 반대로 소수 cluster 변화가 평균에 묻힐 수도 있다. 가능하면 cosine distance, MMD, classifier-based drift, PCA/UMAP 시각화를 함께 본다.

### MEAS-006 CLASSIFIER_CONFIDENCE

`CLASSIFIER_CONFIDENCE`는 reference/current를 구분하도록 학습한 domain classifier가 각 sample의 domain을 얼마나 확신하는지 나타낸다. Alibi Detect는 classifier-based drift detector를 reference와 test set을 구분하는 classifier를 학습하고, 성능이 random chance보다 유의하게 좋은지 보는 방식으로 설명한다.

값 형태: 보통 0에서 1 사이의 실수형 확률 또는 confidence score다. binary domain classifier에서는 reference/current 중 한 class에 대한 predicted probability로 기록되는 경우가 많다. calibration되지 않은 score일 수도 있으므로 probability로 해석 가능한지 확인한다.

값 크기 해석: 특정 domain class에 대한 confidence라면 0 또는 1에 가까울수록 classifier가 강하게 구분한다는 뜻이고, 0.5 근처는 불확실하다는 뜻이다. current class probability만 저장했다면 높은 값은 current로 구분하기 쉽다는 뜻이지만, 전체 drift 강도는 ROC-AUC와 함께 봐야 한다.

drift 관점에서는 confidence 분포가 높아지거나 양극화되면 reference/current 구분이 쉬워졌다는 신호일 수 있다. 다만 confidence는 classifier calibration, class imbalance, leakage, overfitting에 영향을 받는다.

보고서에서는 ROC-AUC, cross-validation 결과, train/test split 방식, leakage 점검을 함께 제시한다. confidence가 높다는 사실만으로 원인을 특정하지 않는다.

### MEAS-007 CONTROL_LIMIT

`CONTROL_LIMIT`는 EWMA, MEWMA, Hotelling T2, CUSUM, SPRT류에서 statistic이 정상 범위를 벗어났는지 판단하는 기준선이다.

값 형태: 실수형 threshold다. upper/lower limit이 있으면 두 개의 실수로 기록되고, one-sided detector는 하나의 경계값만 가질 수 있다. 단위와 범위는 비교 대상 statistic의 단위와 동일하다.

값 크기 해석: limit 자체의 높고 낮음은 drift 강도가 아니라 detector 민감도를 뜻한다. upper limit이 낮으면 alarm이 더 쉽게 발생할 수 있고, 높으면 더 큰 변화만 감지한다. lower limit은 방향이 반대다. 해석은 statistic과 limit의 차이, 초과 지속 시간으로 한다.

drift 관점에서는 control limit 자체가 측정값이라기보다 판정 기준이다. 기준 기간의 평균/분산, 목표 false alarm rate, 정상 기간 리플레이, domain cost에 따라 설정이 달라진다.

NIST 계열 control chart 해석에서는 control limit 초과를 special-cause variation 후보로 보고 조사한다. drift monitoring에서도 동일하게 "관리 한계 초과로 drift 후보 signal 발생"이라고 표현해야 한다. control limit를 넘었다고 즉시 재학습, 롤백, 원인 확정으로 연결하지 않는다.

### MEAS-008 COSINE_DISTANCE

`COSINE_DISTANCE`는 embedding vector 또는 centroid 간 방향 차이를 나타낸다. 텍스트, LLM query, semantic embedding에서는 크기보다 방향이 의미 표현과 더 관련될 수 있어 자주 쓰인다.

값 형태: 실수형 거리다. 일반적인 cosine distance는 `1 - cosine_similarity`로 계산되며 보통 0에서 2 사이에 놓인다. embedding이 non-negative이거나 normalized semantic embedding이면 실무적으로 0에서 1 사이에 주로 나타날 수 있지만, 범위 가정은 구현을 확인한다.

값 크기 해석: 낮은 값은 reference와 current embedding 방향이 유사하다는 뜻이다. 높은 값은 의미 방향 또는 centroid 방향이 달라졌다는 뜻이다. 0에 가까울수록 semantic shift 신호가 약하고, threshold 대비 높을수록 query intent/topic 변화 후보가 강하다.

drift 관점에서는 query intent, topic, 표현 의미의 이동 후보로 해석한다. 특히 centroid cosine distance가 증가하면 현재 query 묶음의 평균 의미 방향이 reference와 달라졌을 가능성이 있다.

주의할 점은 cosine distance가 embedding model과 preprocessing에 매우 민감하다는 것이다. embedding model 버전, tokenizer, normalization, language mix, prompt template 변경이 있으면 실제 사용자 의미 변화가 없어도 distance가 달라질 수 있다. concept drift 확정 표현은 피하고 "semantic distribution shift 후보"로 쓴다.

### MEAS-009 CUSUM_STATISTIC

`CUSUM_STATISTIC`은 기준 평균 대비 편차를 누적한 값이다. CUSUM은 작은 지속적 변화에 민감하도록 설계된 순차 change detection 방식이다.

값 형태: 실수형 순차 통계량이다. upper/lower CUSUM은 보통 0 이상의 값으로 누적되며, reset rule에 따라 0으로 되돌아갈 수 있다. 단위는 표준화 여부에 따라 원 metric 단위 또는 z-score 단위가 된다.

값 크기 해석: 낮은 값 또는 0 근처 값은 기준 평균 대비 누적 편차가 크지 않다는 뜻이다. 높은 값은 한 방향의 작은 편차가 지속적으로 누적되었다는 뜻이며 threshold에 가까워질수록 drift alarm 가능성이 커진다. upper/lower CUSUM은 방향을 분리해서 해석한다.

drift 관점에서는 단발성 spike보다 누적되는 편향을 찾는 데 적합하다. loss, error rate, latency, confidence 같은 metric이 조금씩 지속적으로 나빠질 때 유용하다.

해석할 때는 방향이 중요하다. upper CUSUM은 증가 방향, lower CUSUM은 감소 방향 변화에 대응한다. 기준 평균, allowance parameter, decision threshold가 잘못 설정되면 정상적인 계절성이나 운영 주기에도 alarm이 날 수 있다. 보고서에는 원시 metric trend와 CUSUM curve를 함께 제시한다.

### MEAS-010 DISTANCE_TREND

`DISTANCE_TREND`는 window별 distance가 시간에 따라 어떻게 변하는지 나타낸다.

값 형태: 시간 index와 실수형 distance 값의 sequence다. 각 원소는 보통 0 이상의 실수이며, distance 종류에 따라 상한이 없거나 0에서 1 사이로 bounded될 수 있다. 단일 scalar가 아니라 time series로 저장하는 것이 좋다.

값 크기 해석: 낮은 구간이 지속되면 reference와 current 차이가 baseline 수준이라는 뜻이다. 값이 높아지거나 상승 추세가 지속되면 drift 후보가 강해진다. 단발성 높은 값은 blip일 수 있으므로 지속 시간과 반복성을 함께 본다.

drift 관점에서는 단일 시점의 distance보다 trend가 더 중요할 때가 많다. 일시적인 spike인지, 점진적으로 증가하는지, threshold 위에서 지속되는지, 다시 baseline으로 회복되는지를 본다.

이 값은 recurring/seasonal drift와 operational event를 구분하는 데 도움이 된다. 특정 배포, 캠페인, 데이터 수집 정책 변경과 같은 이벤트 로그를 같은 timeline에 겹쳐 확인한다. distance trend가 증가해도 label 기반 성능 변화가 없으면 "covariate shift 후보" 수준으로 표현한다.

### MEAS-011 DRIFT_ALARM_STATE

`DRIFT_ALARM_STATE`는 detector가 drift 조건을 만족했는지를 나타내는 상태값이다. River의 ADWIN, Page-Hinkley, KSWIN 문서 모두 `drift_detected` 같은 상태를 제공한다.

값 형태: boolean 또는 범주형 상태값이다. 최소 형태는 `true/false`이며, 일부 detector는 `none`, `warning`, `drift`처럼 multi-state로 제공한다. 크기 비교 대상이 아니며 발생 시점과 함께 기록해야 한다.

값 크기 해석: boolean 값에는 높고 낮음이 없다. `false`는 detector rule이 발동하지 않았다는 뜻이고, `true`는 rule이 발동했다는 뜻이다. multi-state라면 일반적으로 `normal < warning < drift`처럼 운영 심각도 순서를 둘 수 있지만, 이 순서는 문서화해야 한다.

drift 관점에서는 이 값을 "detector rule이 발동했다"는 사실로 해석한다. 어떤 입력 신호에 detector를 적용했는지가 핵심이다. 입력이 error rate이면 supervised performance/concept drift 후보가 될 수 있지만, 입력이 feature value이면 covariate shift 후보에 가깝다.

보고서에서는 alarm 시점, detector variant, threshold, window size, 입력 신호, alarm 전후 원시 지표를 함께 적는다. alarm 자체를 원인으로 쓰지 않는다.

### MEAS-012 ERROR_RATE

`ERROR_RATE`는 예측 오류의 비율이다. DDM, RDDM, HDDM, STEPD 같은 supervised drift detector에서 핵심 입력이자 산출값이다.

값 형태: 0에서 1 사이의 실수형 비율이다. percentage로 표현하면 0에서 100 사이가 된다. window 단위, cumulative 단위, class별 단위가 섞이지 않도록 denominator와 집계 구간을 명시한다.

값 크기 해석: 낮은 값은 오류가 적다는 뜻이고 높은 값은 모델 성능 악화 후보가 강하다는 뜻이다. reference 대비 current error rate가 상승하면 performance drift 또는 supervised concept drift 후보로 해석할 수 있다. class imbalance가 있으면 전체 error rate보다 class별 error rate를 우선 확인한다.

drift 관점에서는 performance drift 또는 supervised concept drift 후보를 판단하는 강한 신호다. feature drift와 달리 label이 반영되므로 모델이 실제로 틀리는 비율이 변했는지 볼 수 있다.

그러나 label 지연, label 품질, class imbalance, data mix 변화가 error rate를 왜곡할 수 있다. 전체 error rate만 보지 말고 class별 오류율, confusion matrix, segment별 error rate, label coverage를 함께 본다.

### MEAS-013 EWMA_VALUE

`EWMA_VALUE`는 최근 관측값에 더 큰 가중치를 둔 이동 평균이다. EWMA control chart는 작은 평균 shift를 감지하는 데 유용한 방식으로 널리 쓰인다.

값 형태: 실수형 time series 값이다. 단위는 입력 metric과 같다. 입력이 error rate이면 0에서 1 사이일 수 있고, loss나 latency이면 해당 metric의 범위를 따른다.

값 크기 해석: 입력 metric의 의미에 따라 방향이 달라진다. loss, error rate, latency의 EWMA가 높아지면 악화 후보이고, confidence나 accuracy의 EWMA가 낮아지면 악화 후보일 수 있다. center line과 control limit 대비 상대 위치로 해석한다.

drift 관점에서는 loss, error rate, confidence, latency처럼 연속 metric이 점진적으로 변하는지 확인할 때 사용한다. 원시값이 noisy해도 EWMA는 완만한 추세를 드러낼 수 있다.

smoothing factor가 크면 최근 변화에 민감하고, 작으면 노이즈를 줄이는 대신 감지가 늦어진다. 보고서에는 EWMA value만 쓰지 말고 원시 metric, smoothing factor, control limit를 함께 표시한다.

### MEAS-014 FALSE_ALARM_TARGET

`FALSE_ALARM_TARGET`은 detector가 정상 상태에서 허용하려는 오경보 수준이다. Alibi Detect의 online detector 문서는 expected run-time과 detection delay 사이에 trade-off가 있다고 설명한다.

값 형태: 보통 0에서 1 사이의 실수형 확률 또는 rate다. 어떤 구현에서는 expected run length, expected run-time처럼 양의 실수/정수 규모로 표현할 수 있다. 확률인지 run length인지 단위를 명확히 구분한다.

값 크기 해석: 확률형 false alarm target은 낮을수록 보수적인 detector를 의미하고, 높을수록 민감하지만 오경보가 늘 수 있다. expected run length 형태라면 값이 클수록 정상 상태에서 alarm까지 더 오래 걸리도록 calibration했다는 뜻이다.

drift 관점에서는 운영 민감도 설정이다. false alarm target을 낮게 잡으면 안정적이지만 drift를 늦게 잡을 수 있고, 높게 잡으면 빨리 감지하지만 불필요한 조사와 재학습이 늘 수 있다.

이 값은 drift 크기가 아니다. 보고서에서는 "이 detector는 false alarm target을 어떤 수준으로 calibration했다"는 운영 조건으로 기록한다.

### MEAS-015 FEATURE_IMPORTANCE_OR_RANK

`FEATURE_IMPORTANCE_OR_RANK`는 drift 설명 후보가 되는 feature의 중요도, 순위, 변화량이다. SHAP drift, tree feature 기반 감지, domain classifier 기반 설명에서 나온다.

값 형태: 중요도 score는 보통 0 이상의 실수이고, rank는 1부터 시작하는 정수 순위다. rank delta는 음수/양수 정수일 수 있고, importance delta는 실수형 변화량일 수 있다. score scale은 method마다 다르므로 같은 method 안에서 비교한다.

값 크기 해석: importance score가 높을수록 해당 feature가 drift 설명 또는 domain 구분에 더 크게 기여했을 가능성이 있다. rank 값은 숫자가 낮을수록 더 중요한 순위다. importance delta가 크면 contribution 변화가 큰 feature 후보지만, causal 원인이라는 뜻은 아니다.

drift 관점에서는 원인 후보를 좁히는 데 사용한다. 어떤 feature가 reference/current 구분에 크게 기여했는지, 어떤 feature의 contribution ranking이 바뀌었는지 설명할 수 있다.

주의할 점은 feature importance가 causality를 의미하지 않는다는 것이다. proxy feature, correlated feature, leakage feature가 높은 importance를 가질 수 있다. 보고서에서는 "원인 후보 feature" 또는 "추가 확인이 필요한 feature"로 표현한다.

### MEAS-016 HOTELLING_T2_STATISTIC

`HOTELLING_T2_STATISTIC`은 다변량 평균 벡터의 shift를 공분산 구조까지 고려해 측정하는 통계량이다.

값 형태: 0 이상의 실수형 통계량이다. regularized T2도 0 이상이지만 classical T2와 scale이 다를 수 있다. p-value 또는 control limit와 함께 해석해야 하며 단독 절대값의 범위는 데이터 차원과 covariance에 의존한다.

값 크기 해석: 낮은 값은 current 평균 벡터가 reference 평균/공분산 구조 안에 있다는 뜻이고, 높은 값은 다변량 평균 shift 후보가 강하다는 뜻이다. control limit를 넘으면 alarm 후보지만, covariance 불안정성이 있으면 과대 해석하지 않는다.

drift 관점에서는 여러 numeric feature 또는 embedding summary feature가 함께 이동했는지 확인할 때 사용한다. 단변량 detector가 각각 작은 변화만 보일 때도, 상관 구조를 고려한 다변량 평균 변화는 유의할 수 있다.

해석에는 공분산 안정성이 중요하다. feature 수가 sample size에 비해 크거나 covariance가 ill-conditioned이면 T2 statistic이 불안정해진다. regularized T2를 쓴 경우 classical T2와 scale이 다를 수 있으므로 threshold calibration을 별도로 보고한다.

### MEAS-017 HYPOTHESIS_DECISION_STATE

`HYPOTHESIS_DECISION_STATE`는 SPRT 같은 순차 검정에서 H0 또는 H1 중 어느 쪽으로 결론을 냈는지 나타낸다.

값 형태: 범주형 상태값이다. 일반적인 값은 `continue`, `accept_h0`, `accept_h1` 또는 `reject_h0` 같은 문자열이다. numeric confidence가 아니라 decision state이므로 사전 정의한 가설과 함께 저장한다.

값 크기 해석: 높고 낮음의 개념이 없다. `continue`는 아직 충분한 증거가 없다는 뜻이고, `accept_h1` 또는 `reject_h0`는 사전에 정의한 변화 가설을 지지한다는 뜻이다. 상태의 심각도는 H1이 무엇인지에 따라 달라진다.

drift 관점에서는 "사전에 정의한 변화 가설"에 대한 판단이다. 예를 들어 오류율이 2%에서 5%로 증가했다는 대립가설을 두고 순차적으로 데이터를 보며 결정할 수 있다.

이 값은 H0/H1이 무엇인지 모르면 해석할 수 없다. 보고서에는 null hypothesis, alternative hypothesis, alpha/beta, expected effect size를 반드시 함께 남긴다.

### MEAS-018 JENSEN_SHANNON_DISTANCE

`JENSEN_SHANNON_DISTANCE`는 두 확률분포의 차이를 symmetric하고 bounded하게 표현하는 거리 계열 측정값이다. Evidently는 categorical 또는 numerical distribution drift에서 Jensen-Shannon distance를 사용할 수 있다고 설명한다.

값 형태: 실수형 거리다. SciPy의 `jensenshannon`은 Jensen-Shannon divergence의 제곱근을 반환하며, 로그 base 설정에 따라 범위가 달라진다. base 2이면 일반적으로 0에서 1 사이이고, 값이 클수록 분포 차이가 크다.

값 크기 해석: 낮은 값은 두 probability distribution이 유사하다는 뜻이다. 높은 값은 category, topic, prediction class 비율 차이가 크다는 뜻이다. threshold를 넘으면 drift 후보로 볼 수 있지만, binning과 smoothing 정책에 따라 값이 달라진다.

drift 관점에서는 category distribution, prediction class distribution, topic distribution처럼 확률 벡터 형태의 분포 비교에 적합하다. KL divergence보다 해석이 안정적인 경우가 많지만, binning과 smoothing 정책에 영향을 받는다.

보고서에서는 어떤 probability vector를 비교했는지, zero probability를 어떻게 처리했는지, threshold가 어떻게 정해졌는지 함께 적는다.

### MEAS-019 KS_STATISTIC

`KS_STATISTIC`은 두 경험 CDF 사이의 최대 차이다. SciPy의 `ks_2samp` 문서는 two-sided KS statistic을 두 empirical distribution function 사이의 최대 절대 차이로 설명한다.

값 형태: 보통 0에서 1 사이의 실수형 통계량이다. 0은 empirical CDF 차이가 없음을 뜻하고, 1에 가까울수록 최대 CDF 차이가 크다. approximate 또는 higher-order variant는 이름이 같아도 scale이 달라질 수 있으므로 variant를 확인한다.

값 크기 해석: 낮은 값은 두 단변량 경험분포가 유사하다는 뜻이다. 높은 값은 CDF의 어떤 구간에서 reference/current 차이가 크다는 뜻이다. p-value가 작고 statistic도 크면 drift 신호가 강하지만, sample size와 ties/discrete 여부를 함께 확인한다.

drift 관점에서는 단변량 연속형 feature, score, confidence 분포의 변화 여부를 볼 때 유용하다. statistic이 클수록 CDF 어느 지점에서 reference/current 차이가 크다는 뜻이다.

주의할 점은 KS가 단변량 marginal 변화에 초점을 둔다는 것이다. embedding 전체의 joint distribution drift를 dimension별 KS만으로 확정하면 안 된다. ties가 많거나 discrete data이면 classical p-value 해석도 약해질 수 있다.

### MEAS-020 LOG_LIKELIHOOD_RATIO

`LOG_LIKELIHOOD_RATIO`는 SPRT 계열에서 관측 stream이 H0보다 H1을 얼마나 더 지지하는지 누적한 값이다.

값 형태: 음수, 0, 양수를 모두 가질 수 있는 실수형 누적 통계량이다. 양수 방향이 H1 지지를 의미하는지, 음수 방향이 H0 지지를 의미하는지는 구현과 정의를 확인한다. decision boundary와 함께 해석한다.

값 크기 해석: H1 방향으로 값이 커질수록 변화 가설을 지지하는 누적 증거가 강해진다. H0 방향으로 멀어지면 변화가 없다는 가설을 더 지지한다. 0 근처는 증거가 약하거나 양쪽 가설을 구분하기 어려운 상태다.

drift 관점에서는 순차적으로 증거가 쌓이는 과정을 보여준다. error rate 증가, 평균 shift 같은 명시적 가설이 있을 때 빠른 의사결정에 쓸 수 있다.

이 값은 가설 정의에 종속적이다. 같은 stream이라도 H1을 어떤 변화 크기로 두었는지에 따라 ratio가 달라진다. 보고서에서는 로그 우도비의 방향, decision boundary, H0/H1 설정을 함께 설명한다.

### MEAS-021 MAHALANOBIS_DISTANCE

`MAHALANOBIS_DISTANCE`는 기준 평균과 공분산을 고려해 sample 또는 window가 얼마나 벗어났는지 나타낸다. scikit-learn 문서는 robust covariance 기반 outlyingness 측정에서 Mahalanobis distance가 사용될 수 있다고 설명한다.

값 형태: 0 이상의 실수형 거리 또는 squared distance다. `D`와 `D2`를 구분해야 한다. squared Mahalanobis distance는 차원과 분포 가정에 따라 chi-square 계열 threshold와 연결될 수 있지만, robust/regularized 방식에서는 별도 calibration이 필요하다.

값 크기 해석: 낮은 값은 reference 평균과 공분산 구조 안에 가까이 있다는 뜻이다. 높은 값은 다변량 이탈 또는 outlier 후보가 강하다는 뜻이다. threshold를 넘는 샘플 비율이 증가하면 covariate shift 또는 OOD 증가 후보로 해석한다.

drift 관점에서는 scale과 feature correlation을 고려한 다변량 이탈 정도를 보는 데 적합하다. feature 간 상관을 무시한 Euclidean distance보다 운영 feature vector 해석에 유리할 수 있다.

다만 covariance 추정이 핵심 약점이다. reference에 outlier가 섞였거나 sample size 대비 feature dimension이 크면 distance가 왜곡된다. robust covariance를 썼는지, regularization을 했는지, PCA 등 축소를 했는지 같이 보고한다.

### MEAS-022 METHOD_POLICY

`METHOD_POLICY`는 binning, regularization, robust covariance, sampling, tie handling 같은 method 설정을 뜻한다.

값 형태: 구조화된 범주형 metadata다. 문자열, enum, JSON-like parameter set으로 저장하는 것이 적합하다. 예시는 `bin_count=20`, `regularization=shrinkage`, `tie_policy=warn_only`, `sampling=random_projection`이다.

값 크기 해석: 대부분 크고 작음의 순서 해석이 없다. 다만 `bin_count`, `projection_count`, `sample_size`처럼 내부 numeric parameter는 별도 의미가 있다. 이 항목은 drift 강도가 아니라 결과 재현성과 비교 가능성을 설명한다.

drift 관점에서는 이 값이 결과 비교 가능성을 좌우한다. 예를 들어 PSI나 JS distance는 binning 정책에 따라 값이 달라지고, robust Mahalanobis는 covariance 정책에 따라 distance scale이 달라진다.

이 값은 drift score가 아니라 재현성 metadata다. 보고서에는 method policy를 별도 설정 항목으로 남기고, 서로 다른 policy로 계산된 결과를 직접 비교하지 않는다.

### MEAS-023 MEWMA_STATISTIC

`MEWMA_STATISTIC`은 EWMA를 다변량으로 확장한 control statistic이다.

값 형태: 0 이상의 실수형 다변량 control statistic이다. 포함 metric 수, scaling, covariance 추정 방식에 따라 값의 scale이 달라진다. control limit와 함께 해석해야 한다.

값 크기 해석: 낮은 값은 여러 metric의 결합 상태가 baseline에 가깝다는 뜻이다. 높은 값은 다변량 gradual shift 후보가 강하다는 뜻이며 control limit 초과 시 alarm으로 해석할 수 있다. 높은 값이 어느 metric 때문인지 contribution 분석이 필요하다.

drift 관점에서는 여러 metric이 동시에 조금씩 움직이는 gradual drift를 잡는 데 유용하다. 단일 metric은 control limit 안에 있어도 결합 통계량이 limit을 넘을 수 있다.

해석할 때는 어떤 metric들이 포함되었는지, scaling을 어떻게 했는지, covariance matrix가 안정적인지 확인한다. MEWMA alarm 이후에는 기여 metric 분석이 필요하다. 단순히 "전체 시스템 drift"라고 쓰기보다 "여러 metric의 결합 변화가 관리 한계를 넘었다"로 표현한다.

### MEAS-024 ONLINE_OR_PRE_POST_PERFORMANCE

`ONLINE_OR_PRE_POST_PERFORMANCE`는 online accuracy, retraining 전후 metric, HAT 교체 전후 성능처럼 운영 조치와 연결되는 성능 측정값이다.

값 형태: metric에 따라 실수형 비율, score, loss, count가 될 수 있다. accuracy/F1/AUC는 보통 0에서 1 사이이고, loss/latency는 0 이상의 실수이며 상한은 metric 정의에 따른다. 반드시 metric name과 단위를 함께 기록한다.

값 크기 해석: metric별 방향이 다르다. accuracy, F1, AUC는 낮아질수록 성능 악화 후보이고, loss, error, latency는 높아질수록 악화 후보일 수 있다. pre/post 비교에서는 같은 평가 조건인지 먼저 확인한다.

drift 관점에서는 detector가 감지한 변화가 실제 모델 품질에 영향을 주었는지 확인하는 데 중요하다. feature drift와 달리 성능 결과를 직접 포함하므로 운영 의사결정에 더 가까운 증거다.

그러나 pre/post 비교는 데이터 난이도, label mix, traffic segment, seasonality가 같다는 보장이 없다. 보고서에서는 비교 window와 평가 데이터 조건을 명시하고, 가능한 경우 동일 기준 데이터 또는 delayed label 기반으로 재평가한다.

### MEAS-025 OUTLIER_FLAG

`OUTLIER_FLAG`는 개별 샘플이 정상 경계 밖인지 여부를 나타낸다.

값 형태: boolean 또는 이진 범주형 값이다. 예시는 `true/false`, `inlier/outlier`, `1/-1`이다. scikit-learn 일부 novelty detector는 inlier를 `1`, outlier를 `-1`로 표현하므로 mapping을 명시한다.

값 크기 해석: boolean 또는 label 값이므로 높고 낮음의 수치 해석은 하지 않는다. `outlier=true` 또는 `-1`이 많아질수록 window 수준의 anomaly rate 증가로 이어질 수 있다. 개별 flag 하나는 drift 증거가 아니다.

drift 관점에서는 sample-level 신호다. 개별 outlier는 항상 발생할 수 있으므로 하나의 flag를 drift로 해석하지 않는다. 대신 window 단위 outlier rate, anomaly score distribution, outlier cluster를 본다.

보고서에서는 "개별 이상 샘플"과 "분포 변화"를 구분한다. 특정 outlier 예시는 원인 분석에는 유용하지만, drift 판정에는 집계 통계가 필요하다.

### MEAS-026 OUTLIER_OR_ANOMALY_RATE

`OUTLIER_OR_ANOMALY_RATE`는 current window에서 이상 샘플 또는 정상 경계 위반 샘플의 비율이다.

값 형태: 0에서 1 사이의 실수형 비율이다. percentage로 표현하면 0에서 100 사이가 된다. denominator는 current window sample count이며, 결측/필터링 후 유효 표본 기준인지 명시한다.

값 크기 해석: 낮은 값은 대부분의 current sample이 정상 경계 안에 있다는 뜻이다. 높은 값은 OOD 또는 anomaly sample 비율이 증가했다는 뜻이다. reference 정상 기간의 rate와 비교해 높아졌는지 보는 것이 중요하다.

drift 관점에서는 OCDD, novelty detection, isolation forest 기반 감지에서 reference보다 current가 정상 영역 밖으로 더 많이 나가는지 보는 신호다. anomaly score보다 운영 dashboard에 넣기 쉽다.

이 비율이 증가하면 OOD 후보 또는 covariate shift 후보로 볼 수 있다. 하지만 threshold 설정, contamination assumption, reference 정상성, scaling에 민감하다. 성능 저하 확정 표현은 label 기반 검증 후에만 사용한다.

### MEAS-027 P_VALUE

`P_VALUE`는 통계 검정의 유의확률이다. SciPy와 Alibi Detect 문서 모두 p-value를 test statistic의 극단성에 대한 확률로 설명하고, threshold보다 작으면 귀무가설을 기각하는 방식으로 사용한다.

값 형태: 0에서 1 사이의 실수형 확률이다. exact, asymptotic, permutation, bootstrap 등 계산 방식이 다르면 같은 statistic에서도 값이 달라질 수 있다. corrected p-value라면 보정 방법을 함께 표시한다.

값 크기 해석: 낮은 p-value는 귀무가설, 보통 "reference와 current가 같은 분포"라는 가설에 반하는 증거가 강하다는 뜻이다. 높은 p-value는 귀무가설을 기각할 근거가 부족하다는 뜻이지, 두 분포가 동일함을 증명하는 것은 아니다. p-value는 효과 크기가 아니다.

drift 관점에서는 reference/current가 같은 분포라는 가설을 기각할 근거로 쓴다. 하지만 p-value는 변화 크기, 운영 영향, 원인을 말하지 않는다.

보고서에는 p-value 계산 방식(exact/asymptotic/permutation), sample size, multiple testing correction, effect size를 함께 남긴다. "p-value가 작으므로 drift 가능성이 있다"는 허용되지만, "p-value가 작으므로 성능이 저하됐다"는 금지한다.

### MEAS-028 PAGE_HINKLEY_STATISTIC

`PAGE_HINKLEY_STATISTIC`은 평균 변화에 대한 순차 누적 통계량이다. River 문서는 Page-Hinkley가 현재까지의 관측값과 평균을 이용하고 warning zone 없이 change detection만 제공한다고 설명한다.

값 형태: 실수형 순차 통계량이다. 방향 설정에 따라 증가, 감소, 양방향 통계가 있을 수 있고, threshold와 비교해 alarm을 낸다. 값의 절대 범위는 입력 metric scale과 forgetting factor에 의존한다.

값 크기 해석: 낮은 값은 누적 평균 변화 신호가 약하다는 뜻이다. 높은 값은 Page-Hinkley가 감시하는 방향의 평균 변화 증거가 누적되었다는 뜻이며 threshold에 가까울수록 alarm 가능성이 커진다. 방향 설정이 `up`, `down`, `both` 중 무엇인지 확인한다.

drift 관점에서는 streaming metric의 평균이 증가하거나 감소하는 change point를 감지할 때 쓴다. loss, error rate, confidence, latency처럼 시간 순서가 중요한 metric에 적합하다.

threshold, delta, forgetting factor, monitoring direction을 함께 해석해야 한다. 계절성이나 운영 주기가 있는 데이터는 먼저 detrending하거나 같은 시즌과 비교한다.

### MEAS-029 PROJECTION_COUNT

`PROJECTION_COUNT`는 sliced Wasserstein, random projection 기반 embedding drift 같은 근사 방식에서 사용한 projection 수다.

값 형태: 1 이상의 정수다. projection 기반 detector의 configuration output이며, 값이 클수록 계산량이 늘어난다. drift 크기와 직접적인 대소 관계를 갖지 않는다.

값 크기 해석: 낮은 projection count는 계산이 빠르지만 projection 방향에 따른 누락 위험이 크다. 높은 projection count는 근사 안정성을 높일 수 있지만 비용이 증가한다. 이 값은 drift 강도가 아니라 근사 품질 설정이다.

drift 관점에서는 점수가 아니라 근사 품질과 재현성 정보다. projection 수가 많으면 다양한 방향의 차이를 볼 수 있지만 계산 비용이 증가한다. projection 수가 적으면 특정 방향의 drift를 놓칠 수 있다.

보고서에는 projection count, random seed, projection 방식, 반복 실행 안정성을 함께 기록한다.

### MEAS-030 RECONSTRUCTION_ERROR

`RECONSTRUCTION_ERROR`는 autoencoder가 input 또는 representation을 얼마나 잘 복원하지 못했는지 나타낸다.

값 형태: 보통 0 이상의 실수형 error다. MSE, MAE, negative log-likelihood 등 error 정의에 따라 단위와 scale이 달라진다. window 평균, percentile, sample-level error를 구분한다.

값 크기 해석: 낮은 값은 autoencoder가 current sample을 정상 패턴처럼 잘 재구성했다는 뜻이다. 높은 값은 정상 manifold에서 벗어난 후보가 강하다는 뜻이다. threshold 대비 높은 sample 비율이나 error distribution shift를 함께 본다.

drift 관점에서는 정상 reference로 학습한 representation manifold에서 current sample이 벗어났는지 보는 신호다. 이미지, sensor, embedding data에서 비선형 정상 패턴의 변화 후보를 찾는 데 쓸 수 있다.

주의할 점은 reconstruction error 증가가 항상 semantic drift를 의미하지 않는다는 것이다. noise, compression, preprocessing 변경, resolution 변경, missing value 처리도 error를 키울 수 있다. latent drift, anomaly rate, raw sample inspection을 함께 본다.

### MEAS-031 ROC_AUC

`ROC_AUC`는 domain classifier가 reference와 current를 구분하는 능력을 나타낸다. scikit-learn은 ROC-AUC를 prediction score 기반 ROC curve 아래 면적으로 제공하며, Evidently의 text content drift도 domain classifier의 ROC-AUC를 drift score로 사용할 수 있다고 설명한다.

값 형태: 일반적으로 0에서 1 사이의 실수형 score다. binary domain classifier에서는 0.5가 random 수준이고 1에 가까울수록 구분력이 높다. score 방향이 뒤집힌 경우 0.5보다 낮게 나올 수 있으므로 class label mapping을 확인한다.

값 크기 해석: 0.5 근처는 reference/current를 잘 구분하지 못한다는 뜻이고, 1에 가까울수록 구분이 쉽다는 뜻이다. drift 관점에서는 높은 AUC가 분포 차이 신호를 강화한다. 단, leakage나 overfitting이 있으면 값이 높아도 신뢰할 수 없다.

drift 관점에서는 AUC가 0.5에 가까우면 reference/current 구분이 어렵고, 1에 가까울수록 구분이 쉽다. 즉 distribution shift 신호가 강할 수 있다.

하지만 AUC가 높아도 원인은 알 수 없다. 또한 classifier가 leakage feature, timestamp, ID, preprocessing artifact를 이용했을 수 있다. cross-validation, held-out evaluation, feature importance, leakage check를 함께 수행한다.

### MEAS-032 SAMPLE_SIZE

`SAMPLE_SIZE`는 reference/current 표본 수다.

값 형태: 0 이상의 정수 count다. reference sample size와 current sample size를 별도 필드로 저장한다. 결측 제거, 필터링, class별 subset 적용 후의 effective sample size도 필요할 수 있다.

값 크기 해석: 낮은 sample size는 검정력 부족과 불안정한 distance 추정을 의미할 수 있다. 높은 sample size는 안정성을 높이지만 p-value가 매우 작은 차이에도 민감해질 수 있다. 크고 작음 자체가 drift가 아니라 통계 신뢰도와 민감도 조건이다.

drift 관점에서는 거의 모든 통계 해석의 전제다. p-value, confidence interval, exact/asymptotic 선택, threshold 안정성, false positive rate 해석이 sample size에 따라 달라진다.

보고서에는 reference sample size와 current sample size를 분리해 적는다. window size와 결측 제거 후 유효 표본 수도 함께 기록한다. 표본 수 없이 p-value 또는 distance만 보고하는 것은 피한다.

### MEAS-033 SEQUENTIAL_BOUND

`SEQUENTIAL_BOUND`는 SeqDrift, SPRT, KSWIN 등 순차 detector에서 alarm 여부를 판단하는 경계다.

값 형태: 실수형 threshold 또는 시간에 따라 변하는 threshold sequence다. bound는 보통 양의 실수지만, upper/lower boundary를 함께 쓰는 detector에서는 두 경계가 존재할 수 있다.

값 크기 해석: bound가 낮으면 detector가 더 민감해져 alarm이 쉽게 발생할 수 있다. bound가 높으면 더 큰 변화가 필요하므로 false alarm은 줄지만 detection delay가 늘 수 있다. statistic과 bound의 상대적 거리로 해석한다.

drift 관점에서는 "현재 statistic이 시간이 흐르며 boundary를 넘었는가"를 보는 기준이다. River KSWIN 문서는 sliding window에서 최근 window와 과거 sample window에 KS test를 적용하고, empirical distribution distance가 alpha와 statistic window size로 정해지는 bound를 넘으면 drift로 판단한다고 설명한다.

bound는 민감도와 지연을 동시에 결정한다. 보고서에는 alpha, window size, stat size, expected run-time 또는 false alarm target을 함께 남긴다.

### MEAS-034 SHAP_DRIFT_DISTANCE

`SHAP_DRIFT_DISTANCE`는 SHAP value 분포 또는 class별 SHAP contribution의 변화 정도다. SHAP 문서는 SHAP을 model output 설명을 위한 game-theoretic approach로 설명한다.

값 형태: 사용하는 distance/test에 따라 실수형 거리 또는 p-value가 될 수 있다. SHAP value 자체는 음수/양수 실수이고, 그 분포 차이를 요약한 drift distance는 보통 0 이상의 실수다. class별 값이면 class label을 함께 기록한다.

값 크기 해석: distance형이면 낮을수록 SHAP 분포가 유사하고 높을수록 모델 contribution 변화 후보가 강하다. p-value형이면 낮을수록 SHAP 분포 차이에 대한 통계적 근거가 강하다. SHAP value 자체의 양/음은 feature가 예측을 올리는지 낮추는지의 방향이며 drift distance와 구분한다.

drift 관점에서는 모델의 의사결정 근거가 달라졌는지 보는 explanation drift 신호다. feature value distribution은 비슷해도 모델이 해당 feature를 사용하는 방식이 바뀌거나, class별 contribution이 달라질 수 있다.

그러나 SHAP 변화는 실제 정답 관계 변화의 증거가 아니다. background dataset, explainer type, model version, feature preprocessing 변경이 SHAP distribution을 바꿀 수 있다. 보고서에서는 "decision logic 변화 후보"로 쓰고 label 기반 성능 확인을 요구한다.

### MEAS-035 STANDARD_DEVIATION

`STANDARD_DEVIATION`은 DDM류에서 error rate의 불확실성을 계산하거나, control chart에서 정상 변동성을 추정하는 데 쓰인다.

값 형태: 0 이상의 실수형 통계량이다. 오류율 표준편차이면 0에서 0.5 사이일 수 있지만, 일반 metric의 표준편차는 원 metric scale을 따른다. sample standard deviation인지 standard error인지 구분한다.

값 크기 해석: 낮은 값은 해당 window 또는 기준 추정이 안정적이라는 뜻일 수 있다. 높은 값은 metric 변동성이 크거나 sample size가 작아 threshold가 불안정할 수 있음을 뜻한다. 단독 drift score가 아니라 error rate/control limit 해석의 보조값이다.

drift 관점에서는 독립적인 drift score가 아니다. error rate와 함께 warning/drift threshold를 구성하는 보조 통계다.

표준편차가 커졌다면 signal 자체가 불안정하거나 sample size가 작을 수 있다. 보고서에서는 threshold 계산의 구성요소로 설명하고, 단독으로 drift라고 표현하지 않는다.

### MEAS-036 TEST_STATISTIC

`TEST_STATISTIC`은 Anderson-Darling, Cramer-von Mises, Chi-square, Fisher, G-test, Levene, t-test 등 특정 검정에서 산출되는 일반 검정량이다.

값 형태: 검정별 실수형 통계량이다. 일부 검정량은 0 이상이고, t-statistic처럼 음수/양수를 가질 수 있는 것도 있다. scale과 방향은 method마다 다르므로 반드시 method name과 함께 저장한다.

값 크기 해석: 많은 검정에서 statistic이 클수록 귀무가설과의 불일치가 커지지만, 모든 검정에 일반화하면 안 된다. t-statistic처럼 부호가 방향을 나타내는 경우도 있다. 항상 해당 method의 p-value, alternative hypothesis, statistic definition과 함께 해석한다.

drift 관점에서는 각 method의 귀무가설과 함께 해석해야 한다. test statistic이 크다는 말은 대체로 귀무가설과 덜 일치한다는 뜻이지만, statistic scale은 검정마다 다르다.

서로 다른 test statistic을 직접 크기 비교하지 않는다. 예를 들어 Chi-square statistic과 Anderson-Darling statistic은 같은 scale이 아니다. 보고서에는 method name, null hypothesis, p-value 또는 threshold를 함께 쓴다.

### MEAS-037 THRESHOLD_EXCEEDANCE

`THRESHOLD_EXCEEDANCE`는 statistic 또는 distance가 사전에 정의한 threshold를 넘었는지 여부다.

값 형태: boolean 또는 범주형 상태값이다. 예시는 `true/false`, `exceeded/not_exceeded`, `above/below`이다. threshold와 margin을 함께 저장하면 해석력이 좋아진다.

값 크기 해석: boolean 자체에는 높고 낮음이 없다. `true`는 threshold를 넘었다는 뜻이고 `false`는 넘지 않았다는 뜻이다. 별도로 exceedance margin을 저장한다면 margin이 클수록 threshold 초과 정도가 크다.

drift 관점에서는 binary state로 사용하기 쉽지만 정보 손실이 크다. threshold를 얼마나 넘었는지, 몇 window 동안 지속되었는지, 정상 기간에서도 비슷한 초과가 있었는지를 함께 봐야 한다.

threshold가 경험적 기준인지, 이론적 control limit인지, 도메인 비용 기반 기준인지 구분한다. 초과 여부만으로 자동 재학습이나 롤백을 결정하지 않는다.

### MEAS-038 TOPIC_PROPORTION_DELTA

`TOPIC_PROPORTION_DELTA`는 topic 또는 intent category 비율이 reference 대비 얼마나 바뀌었는지 나타낸다.

값 형태: 실수형 비율 차이 또는 category별 vector다. 개별 topic delta는 -1에서 1 사이이고, 절대 변화량은 0에서 1 사이다. 전체 topic distribution은 각 비율이 0에서 1 사이이며 합이 1이 되도록 정규화한다.

값 크기 해석: delta가 양수이면 해당 topic 비율이 증가했고, 음수이면 감소했다는 뜻이다. 절대값이 클수록 topic mix 변화가 크다. 전체 drift 해석은 개별 topic delta뿐 아니라 전체 distribution distance와 함께 한다.

drift 관점에서는 LLM query drift, user intent shift, campaign/seasonal topic 변화 후보를 설명하는 데 유용하다. category distribution drift로 볼 수 있으므로 JS distance, PSI, Chi-square 같은 분포 비교와 연결할 수 있다.

주의할 점은 topic model 자체가 안정적이어야 한다는 것이다. topic 수, topic labeling, embedding model, clustering 방식이 바뀌면 비율 변화가 실제 query 변화가 아닐 수 있다.

### MEAS-039 TREE_SPLIT_SIGNAL

`TREE_SPLIT_SIGNAL`은 time feature split count, split depth, split rule처럼 tree model이 reference/current 또는 time segment를 구분하는 데 사용한 구조적 신호다.

값 형태: 혼합형이다. split count와 split depth는 0 이상의 정수, feature importance는 실수형 score, split rule은 문자열 또는 구조화된 rule이다. 한 필드에 섞지 말고 세부 필드로 나누는 것이 좋다.

값 크기 해석: time split count가 높거나 time feature가 얕은 depth에서 반복 사용되면 temporal structure 변화 후보가 강해진다. feature importance가 높을수록 tree가 해당 feature를 reference/current 구분에 많이 사용했다는 뜻이다. split rule 문자열은 크기 비교하지 않는다.

drift 관점에서는 temporal covariate shift 또는 drift 시점 후보를 찾는 보조 설명이다. time feature가 상위 split에 자주 등장하면 데이터 구조가 시간에 따라 달라졌을 가능성이 있다.

이 값은 강한 통계 검정이 아니다. tree의 random seed, hyperparameter, leakage, feature correlation에 영향을 받는다. 보고서에서는 "시간 피처 기반 보조 신호"로 표현하고, 분포 검정 또는 시각화로 보강한다.

### MEAS-040 WARNING_STATE

`WARNING_STATE`는 drift 전 단계의 경고 상태다. DDM류에서 warning zone은 drift 확정 전 데이터 보관과 추가 관찰을 위한 상태로 쓰인다.

값 형태: boolean 또는 범주형 상태값이다. 예시는 `normal`, `warning`, `drift` 중 `warning` 상태 또는 별도 `warning=true` flag다. 발생 시작 시점과 종료 시점을 함께 기록하는 것이 좋다.

값 크기 해석: boolean에는 높고 낮음이 없다. multi-state로 보면 일반적으로 `normal`보다 `warning`이 더 높은 조사 필요 상태이고, `drift`는 warning보다 강한 상태다. 이 순서는 detector 설계에 따라 명시해야 한다.

drift 관점에서는 immediate action보다 monitoring intensification에 가깝다. warning 구간의 데이터를 저장하고, 이후 drift state로 전환되는지 또는 정상으로 회복되는지 본다.

warning을 drift 확정으로 쓰지 않는다. 보고서에서는 "경고 구간 진입"과 "drift state 진입"을 분리한다.

### MEAS-041 WASSERSTEIN_DISTANCE

`WASSERSTEIN_DISTANCE`는 두 분포를 서로 맞추는 데 필요한 이동 비용을 나타내는 거리다. SciPy 문서는 1D Wasserstein distance를 Earth mover's distance 또는 optimal transport distance로 설명하고, CDF 차이의 적분과 동등하게 볼 수 있다고 설명한다.

값 형태: 0 이상의 실수형 거리다. 상한은 일반적으로 없고 feature 단위와 scale에 의존한다. normalized Wasserstein을 쓰는 구현에서는 0에서 1 근처의 값으로 scaling될 수 있으므로 raw/normalized 여부를 구분한다.

값 크기 해석: 낮은 값은 두 분포의 위치와 질량 이동이 작다는 뜻이다. 높은 값은 분포가 더 많이 이동했다는 뜻이며 covariate/prediction distribution shift 후보가 강해진다. feature scale에 민감하므로 서로 다른 feature 간 직접 비교는 normalization 없이는 피한다.

drift 관점에서는 feature 값 또는 score 분포가 얼마나 이동했는지 설명하기 좋다. p-value보다 effect size에 가까운 성격이어서 "변화 크기"를 보고서에 쓰기 좋다.

다만 단위와 scale에 영향을 받는다. feature scaling, clipping, outlier, binning, approximate calculation 여부를 함께 확인한다. distance 증가를 성능 저하 또는 원인으로 직접 쓰지 않는다.

### MEAS-042 WINDOW_SIZE

`WINDOW_SIZE`는 adaptive 또는 sliding window detector가 비교에 사용한 데이터 범위다. ADWIN의 `width`, KSWIN의 `window_size`, stat window, retained window size 등이 여기에 포함된다.

값 형태: 1 이상의 정수 count가 기본이다. 시간 기반 window라면 duration 문자열 또는 timestamp range가 될 수 있다. adaptive detector에서는 stream 진행 중 값이 변하는 time series metadata로 저장된다.

값 크기 해석: 작은 window는 최근 변화에 민감하지만 noise와 false alarm에 취약하다. 큰 window는 안정적이지만 감지가 늦어질 수 있다. ADWIN처럼 adaptive window가 갑자기 줄어드는 경우 최근 데이터가 과거 window와 달라졌다는 신호일 수 있다.

drift 관점에서는 detector 민감도와 지연을 해석하는 데 필요하다. 작은 window는 빠르게 반응하지만 noise와 false alarm에 취약하고, 큰 window는 안정적이지만 sudden drift 감지가 늦어질 수 있다.

window size 자체가 drift는 아니다. 보고서에서는 alarm과 함께 "이 detector는 어느 기간 또는 몇 개 sample을 기준으로 판단했는가"를 설명하는 metadata로 사용한다.

## 4. 보고서 생성 문장 원칙

검정 기반 측정값은 다음 형식으로 쓴다.

```text
{method_name}에서 {test_statistic}와 {p_value}를 산출한 결과,
reference와 current가 같은 분포라는 가설을 기각할 근거가 관측되었다.
다만 표본 수, 다중 검정 보정, 효과 크기 지표를 함께 고려해야 한다.
```

거리 기반 측정값은 다음 형식으로 쓴다.

```text
{method_name}의 {distance_measurement}가 기준 기간 대비 증가했다.
이는 분포 또는 표현 공간의 차이가 커졌다는 drift 후보 신호이며,
성능 저하나 원인 확정은 label 기반 성능 검증과 운영 이벤트 확인 이후에 판단한다.
```

순차 detector 측정값은 다음 형식으로 쓴다.

```text
{method_name}에서 {alarm_state}가 발생했다.
이 alarm은 {input_signal}의 시간적 변화 신호이며,
alarm 전후 window, threshold 설정, 원시 metric 추세를 함께 확인해야 한다.
```

설명 기반 측정값은 다음 형식으로 쓴다.

```text
{explanation_measurement}는 모델이 사용하는 feature contribution 또는 decision logic의 변화 후보를 보여준다.
이는 원인 후보를 좁히는 설명 신호이며, 실제 concept drift 확정에는 label 또는 성능 지표 확인이 필요하다.
```

## 5. 참고 자료

- SciPy `ks_2samp`: https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.ks_2samp.html
- SciPy `wasserstein_distance`: https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.wasserstein_distance.html
- SciPy `jensenshannon`: https://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.distance.jensenshannon.html
- Evidently Data Drift Preset: https://docs.evidentlyai.com/metrics/preset_data_drift
- Evidently Customize Data Drift: https://docs.evidentlyai.com/metrics/customize_data_drift
- Alibi Detect Drift Detection: https://docs.seldon.ai/alibi-detect/cd
- River ADWIN: https://riverml.xyz/latest/api/drift/ADWIN/
- River PageHinkley: https://riverml.xyz/latest/api/drift/PageHinkley/
- River KSWIN: https://riverml.xyz/latest/api/drift/KSWIN/
- scikit-learn Novelty and Outlier Detection: https://scikit-learn.org/stable/modules/outlier_detection.html
- scikit-learn ROC-AUC: https://scikit-learn.org/stable/modules/generated/sklearn.metrics.roc_auc_score.html
- SHAP documentation: https://shap.readthedocs.io/en/latest/
