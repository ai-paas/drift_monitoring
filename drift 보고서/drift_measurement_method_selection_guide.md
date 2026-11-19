# Drift Measurement Method Selection Guide

## 1. 목적

이 문서는 같은 `canonical_measurement`를 여러 drift method가 산출할 때, 어떤 경우에 어떤 method를 써야 하는지와, 형식은 같지만 실제 의미가 어떻게 다른지를 정리한다.

예를 들어 `P_VALUE`는 여러 통계 검정에서 공통으로 나오지만, KS Test의 p-value와 Chi-square Test의 p-value는 같은 질문에 대한 답이 아니다. 둘 다 0에서 1 사이의 유의확률이지만, 입력 데이터, 귀무가설, 대립가설, 가정, 민감한 변화 유형이 다르다.

따라서 이 문서는 다음 질문에 답한다.

```text
같은 측정값 이름을 여러 method가 출력할 때
  - 정말 같은 의미인가?
  - 아니면 형식만 같은가?
  - 어떤 데이터/상황에서는 어떤 method를 골라야 하는가?
  - 보고서에서 어떻게 구분해 설명해야 하는가?
```

기준 데이터:

```text
drift_measurement_to_methods.csv
drift_method_variant_measurement_links.csv
drift_measurements_catalog.csv
drift_methods_catalog.md
```

## 2. 공통 원칙

### 2.1 같은 measurement라도 method context가 의미를 결정한다

`P_VALUE`, `TEST_STATISTIC`, `DRIFT_ALARM_STATE`처럼 여러 method에서 공통으로 나오는 값은 단독으로 해석하지 않는다.

항상 다음 식으로 해석한다.

```text
{method}의 {variant}가
{input data}에 대해
{null hypothesis 또는 threshold rule}을 적용해 산출한
{measurement}
```

따라서 `P_VALUE = 0.01`이라는 값만으로는 부족하다. `KS Test의 p-value 0.01`인지, `Chi-square Test의 p-value 0.01`인지, `Anderson-Darling Test의 p-value 0.01`인지에 따라 drift 의미가 달라진다.

### 2.2 cross-method 숫자 비교는 기본적으로 금지한다

서로 다른 method의 `TEST_STATISTIC` 또는 `P_VALUE`를 크기만으로 비교하지 않는다.

```text
금지:
  - KS statistic 0.2보다 Chi-square statistic 10이 크므로 Chi-square drift가 더 강하다.
  - Anderson-Darling p-value 0.03보다 t-test p-value 0.04가 크므로 전자가 더 중요한 drift다.

허용:
  - 각 method가 자기 가정 안에서 drift 후보 신호를 냈는지 비교한다.
  - 여러 method가 같은 feature와 같은 기간에서 일관되게 신호를 냈는지 본다.
  - p-value는 effect size, sample size, multiple testing correction과 함께 해석한다.
```

### 2.3 method 선택은 데이터 형태와 drift 질문에서 시작한다

method를 먼저 고르지 않는다. 먼저 질문을 정한다.

```text
질문 1: numeric 단변량 분포가 달라졌는가?
  -> KS, Anderson-Darling, Cramer-von Mises, Wasserstein, Energy Distance

질문 2: category/class 비율이 달라졌는가?
  -> Chi-square, Fisher's Exact, G-test, JS Distance, PSI, Total Variation

질문 3: stream 평균 또는 error rate가 시간에 따라 바뀌었는가?
  -> ADWIN, Page-Hinkley, CUSUM, EWMA, DDM/RDDM/HDDM

질문 4: 다변량 평균 또는 공분산 구조를 고려한 이탈인가?
  -> Hotelling T2, MEWMA, Mahalanobis Distance

질문 5: embedding/text/model representation이 달라졌는가?
  -> MMD, LSDD, classifier-based drift, semantic distance, feature map drift

질문 6: 모델의 설명 또는 의사결정 근거가 달라졌는가?
  -> SHAP Drift, Tree Feature 기반 감지
```

## 3. 측정값별 method 선택 및 의미 차이

### MEAS-001 ADAPTATION_EVENT

관련 method:

```text
HAT
RDDM
```

`ADAPTATION_EVENT`는 형식상 event 값이지만, HAT와 RDDM에서 의미가 다르다.

HAT에서 이 값은 online tree가 alternate tree를 만들거나 기존 tree를 교체한 사건이다. 즉 detector가 감지한 변화가 모델 구조의 적응으로 이어졌다는 뜻이다. 이 경우 해석의 중심은 "교체 전후 online performance가 좋아졌는가", "alternate tree가 어떤 데이터 구간에서 생성되었는가"다.

RDDM에서 이 값은 기준 window 또는 detector 상태가 reset되는 사건에 가깝다. 모델 구조 변경이 아니라 detector의 기준 상태가 바뀌는 것이다. 따라서 "모델이 적응했다"가 아니라 "detector 기준이 갱신되었다"로 표현해야 한다.

선택 기준:

```text
HAT를 쓸 때:
  labeled online learning 모델 자체가 drift에 적응해야 할 때
  tree replacement를 운영 로그로 추적하고 싶을 때

RDDM event를 볼 때:
  DDM 계열 detector의 오래된 기준 누적 문제를 완화하고 싶을 때
  warning/drift 후 detector state reset을 추적하고 싶을 때
```

보고서 주의:

```text
ADAPTATION_EVENT는 성공이 아니라 사건이다.
HAT event와 RDDM reset event를 같은 의미의 모델 개선으로 합치지 않는다.
```

### MEAS-007 CONTROL_LIMIT

관련 method:

```text
EWMA
Hotelling T2
MEWMA
SPRT
```

`CONTROL_LIMIT`는 모두 threshold처럼 보이지만 method마다 기준이 다르다.

EWMA의 control limit는 단변량 metric의 지수 가중 이동 평균이 정상 변동 범위를 벗어났는지 판단하는 경계다. loss, error rate, confidence처럼 하나의 metric이 점진적으로 움직이는지 볼 때 쓴다.

MEWMA의 control limit는 여러 metric의 결합 EWMA statistic에 대한 경계다. 단일 metric은 안정적으로 보이지만 여러 metric이 함께 움직이는 경우를 잡기 위한 것이다.

Hotelling T2의 control limit는 다변량 평균 벡터가 reference 평균/공분산 구조에서 벗어났는지 판단하는 기준이다. 평균 shift 중심이며, stream smoothing보다는 multivariate mean comparison에 가깝다.

SPRT의 decision boundary는 control chart limit라기보다 H0/H1 순차 의사결정 경계다. 사전에 정의한 귀무가설과 대립가설 중 어느 쪽을 선택할지 결정한다.

선택 기준:

```text
단일 metric의 gradual drift:
  EWMA

여러 metric이 함께 조금씩 움직이는 drift:
  MEWMA

다변량 feature 평균 벡터 shift:
  Hotelling T2

명시적인 H0/H1과 빠른 순차 의사결정:
  SPRT
```

보고서 주의:

```text
CONTROL_LIMIT라는 이름이 같아도 서로 다른 statistic의 경계다.
EWMA limit, MEWMA limit, T2 limit, SPRT boundary를 같은 숫자 scale로 비교하지 않는다.
```

### MEAS-011 DRIFT_ALARM_STATE

관련 method:

```text
ADWIN
Anderson-Darling Test
Autoencoder Representation Drift
Baumgartner-Weiss-Schindler Test
Bhattacharyya Distance
BOCD
Chi-square Test
Classifier 기반 embedding drift detection
Cramer-von Mises Test
CUSUM
DDM
DriftRetrainingClassifier
ECDD-WT
EDDM
Energy Distance
Epps-Singleton Test
EWMA
F-test
Feature Map Drift
Fisher's Exact Test
G-test
Geometric Moving Average
Graph Embedding Drift
HAT
HDDM-A
HDDM-W
Hellinger Distance
Histogram Intersection Normalized Complement
Hotelling T2
Jensen-Shannon Distance
KL Divergence
KSWIN
Kuiper's Test
L-Infinity Distance
Levene's Test
LLM Query / Semantic Distance 기반 감지
LSDD
Mahalanobis Distance
Mann-Whitney U / Wilcoxon Rank Sum Test
MEWMA
MMD
Model Uncertainty Drift
OCDD
Page-Hinkley Test
PSI
RDDM
SeqDrift
SHAP Drift
SPRT
STEPD
t-test 계열
Text Domain Classifier Drift
Total Variation Distance
Tree Feature 기반 감지
Wasserstein Distance
```

`DRIFT_ALARM_STATE`는 가장 조심해야 하는 공통 측정값이다. 거의 모든 method가 최종적으로 `alarm true/false` 또는 `drift detected/not detected`를 만들 수 있기 때문이다.

하지만 alarm의 의미는 method가 보는 신호에 따라 다르다.

```text
KS alarm:
  단변량 numeric distribution 차이 후보

Chi-square alarm:
  categorical frequency 또는 class prior 변화 후보

ADWIN alarm:
  stream window 평균 변화 후보

DDM alarm:
  label 기반 error rate 변화 후보

MMD alarm:
  multivariate 또는 embedding distribution 변화 후보

SHAP Drift alarm:
  model explanation distribution 변화 후보

Domain classifier alarm:
  reference/current를 classifier가 구분할 수 있다는 신호
```

선택 기준:

```text
alarm을 만들 method는 입력 신호에 맞춘다.

feature distribution:
  KS, Wasserstein, PSI, JS, MMD

prediction/class distribution:
  Chi-square, JS, PSI, Total Variation

streaming metric:
  ADWIN, CUSUM, EWMA, Page-Hinkley

label 기반 error stream:
  DDM, RDDM, EDDM, HDDM, STEPD

embedding/text:
  MMD, LSDD, classifier-based drift, semantic distance

model explanation:
  SHAP Drift, Tree Feature 기반 감지
```

보고서 주의:

```text
DRIFT_ALARM_STATE만 단독으로 보고하지 않는다.
반드시 method, variant, input signal, threshold rule을 함께 쓴다.
```

### MEAS-012 ERROR_RATE

관련 method:

```text
ADWIN
DDM
RDDM
```

`ERROR_RATE`는 모두 오류율이지만, method별 역할이 다르다.

DDM에서 error rate는 detector의 핵심 통계다. 오류율과 표준편차가 과거 최소 기준보다 얼마나 커졌는지로 warning/drift를 판단한다.

RDDM에서도 error rate는 핵심 통계지만, 오래된 인스턴스 누적 문제를 완화하기 위해 reset/retention logic이 붙는다. 따라서 DDM의 error rate와 RDDM의 error rate는 같은 입력을 공유하더라도 detector state update 방식이 다르다.

ADWIN에서 error rate는 ADWIN에 넣는 가능한 stream input 중 하나다. ADWIN 자체는 mean change detector이므로 error stream을 넣으면 supervised performance drift 후보가 되고, confidence나 loss를 넣으면 다른 의미가 된다.

선택 기준:

```text
classification error stream 전용 concept drift detector:
  DDM

DDM의 오래된 기준 누적 문제를 줄이고 싶을 때:
  RDDM

error rate 외에도 loss, confidence 등 generic numeric stream을 같은 방식으로 감시하고 싶을 때:
  ADWIN
```

보고서 주의:

```text
ERROR_RATE는 label 품질과 label 지연에 민감하다.
ADWIN(error_rate)와 DDM(error_rate)는 같은 오류율을 보더라도 detector logic이 다르다.
```

### MEAS-015 FEATURE_IMPORTANCE_OR_RANK

관련 method:

```text
SHAP Drift
Tree Feature 기반 감지
Classifier 기반 embedding drift detection
```

`FEATURE_IMPORTANCE_OR_RANK`는 모두 feature ranking처럼 보이지만, 무엇에 대한 중요도인지가 다르다.

SHAP Drift에서 feature importance는 모델 예측에 대한 contribution 변화다. 즉 모델이 어떤 feature를 예측 근거로 더 많이 또는 다르게 쓰는지 보여준다.

Tree Feature 기반 감지에서 importance는 time feature 또는 domain-separating split이 tree 구조에서 얼마나 중요했는지를 뜻한다. 이것은 데이터가 시간에 따라 구분 가능해졌다는 보조 신호다.

Classifier 기반 embedding drift detection에서 importance는 reference/current domain classifier가 두 기간을 구분하는 데 사용한 feature 또는 embedding dimension의 중요도다. 이는 drift 설명 후보이지 원인 확정이 아니다.

선택 기준:

```text
모델 의사결정 근거 변화:
  SHAP Drift

시간 feature가 데이터 구조를 구분하는지 확인:
  Tree Feature 기반 감지

reference/current를 구분하는 feature 후보 찾기:
  Classifier 기반 embedding drift detection
```

보고서 주의:

```text
feature importance는 causal importance가 아니다.
같은 feature 이름이 높게 나와도 SHAP 중요도, tree split 중요도, domain classifier 중요도는 서로 다른 질문에 답한다.
```

### MEAS-021 MAHALANOBIS_DISTANCE

관련 method:

```text
Mahalanobis Distance
MEWMA
```

`MAHALANOBIS_DISTANCE`는 공분산 구조를 고려한 거리라는 공통점이 있다. 그러나 독립 distance method로 쓰는 경우와 MEWMA 내부 통계로 쓰는 경우의 의미가 다르다.

Mahalanobis Distance method에서는 sample 또는 window mean이 reference 평균/공분산에서 얼마나 벗어났는지 직접 측정한다. outlier detection, 다변량 covariate shift 후보 탐지에 적합하다.

MEWMA에서 Mahalanobis D2는 지수 가중 평균 벡터가 기준 상태에서 얼마나 벗어났는지를 나타내는 내부 control statistic 또는 보조 statistic이다. 여기서는 time smoothing과 multivariate process control 문맥이 중요하다.

선택 기준:

```text
정적 reference/current 다변량 이탈:
  Mahalanobis Distance

여러 metric의 시간적 gradual drift:
  MEWMA with Mahalanobis D2
```

보고서 주의:

```text
Mahalanobis distance라는 이름이 같아도,
sample/window distance인지 EWMA-smoothed vector distance인지 구분한다.
```

### MEAS-022 METHOD_POLICY

관련 method:

```text
Hotelling T2
OCDD
Wasserstein Distance
SeqDrift
```

`METHOD_POLICY`는 측정값이라기보다 산출값 해석을 좌우하는 설정 정보다.

Hotelling T2에서는 regularization policy가 공분산 역행렬 안정화에 영향을 준다. 같은 데이터라도 regularization 강도에 따라 T2 scale과 threshold가 달라질 수 있다.

OCDD에서는 normal boundary를 어떻게 학습했는지, anomaly threshold를 어떻게 정했는지, contamination이나 scaling을 어떻게 처리했는지가 중요하다.

Wasserstein Distance에서는 binning, approximate quantile, projection 정책이 distance 값에 영향을 준다.

SeqDrift에서는 reservoir sampling 또는 sequential bound 설정이 감지 지연과 false alarm에 영향을 준다.

선택 기준:

```text
METHOD_POLICY를 method 선택 기준으로 쓰기보다,
선택한 method의 재현성과 비교 가능성을 보장하기 위한 필수 metadata로 기록한다.
```

보고서 주의:

```text
METHOD_POLICY가 다르면 같은 canonical measurement라도 직접 비교하지 않는다.
```

### MEAS-027 P_VALUE

관련 method:

```text
Anderson-Darling Test
Baumgartner-Weiss-Schindler Test
Chi-square Test
Cramer-von Mises Test
Epps-Singleton Test
F-test / Variance Test 계열
Fisher's Exact Test
G-test
KS Test
Kuiper's Test
Levene's Test
Mann-Whitney U / Wilcoxon Rank Sum Test
t-test 계열
MMD
LSDD
Energy Distance
Total Variation Distance
Text Domain Classifier Drift
```

`P_VALUE`는 형식은 같지만 실제 의미는 method의 귀무가설에 의해 결정된다.

예를 들어 KS Test의 p-value는 단변량 continuous distribution의 경험 CDF 차이에 대한 유의확률이다. Chi-square Test의 p-value는 categorical frequency table의 차이에 대한 유의확률이다. t-test의 p-value는 평균 차이에 대한 유의확률이고, Levene's Test의 p-value는 분산 차이에 대한 유의확률이다.

따라서 p-value는 통합 measurement로 관리할 수 있지만, method context 없이 비교하면 안 된다.

선택 기준:

```text
numeric distribution 전체 모양:
  KS, Anderson-Darling, Cramer-von Mises, Epps-Singleton

tail 차이에 민감:
  Anderson-Darling

평균 차이:
  t-test 계열

분산 차이:
  Levene's Test, F-test 계열

rank/location shift:
  Mann-Whitney U / Wilcoxon Rank Sum

categorical frequency:
  Chi-square, Fisher's Exact, G-test

multivariate/kernel distribution:
  MMD, LSDD, Energy Distance

text/domain classifier:
  Text Domain Classifier Drift
```

보고서 주의:

```text
P_VALUE는 "같은 종류의 검정 안에서"만 비교한다.
여러 method의 p-value를 한 줄에 나열할 때는 각 method의 질문을 함께 적는다.
```

### MEAS-031 ROC_AUC

관련 method:

```text
LLM Query / Semantic Distance 기반 감지
Text Domain Classifier Drift
```

`ROC_AUC`는 reference/current domain classifier가 두 데이터 집합을 얼마나 잘 구분하는지를 나타낸다.

LLM Query / Semantic Distance 기반 감지에서 ROC-AUC는 query embedding 또는 text representation을 이용해 reference/current query를 구분할 수 있는지 보는 신호다. 이는 semantic 또는 intent distribution shift 후보로 해석한다.

Text Domain Classifier Drift에서 ROC-AUC는 raw text 또는 text descriptor를 바탕으로 두 기간 text를 구분할 수 있는지 보는 신호다. Evidently 문서는 text content drift에서 domain classifier ROC-AUC를 drift score로 사용할 수 있다고 설명한다.

선택 기준:

```text
embedding 기반 query semantic drift:
  LLM Query / Semantic Distance 기반 감지

raw text content 또는 text descriptor drift:
  Text Domain Classifier Drift
```

보고서 주의:

```text
ROC_AUC가 높으면 두 dataset을 구분하기 쉽다는 뜻이지,
무엇이 원인인지 자동으로 알려주지는 않는다.
classifier leakage와 overfitting을 반드시 확인한다.
```

### MEAS-036 TEST_STATISTIC

관련 method:

```text
Anderson-Darling Test
Baumgartner-Weiss-Schindler Test
Chi-square Test
Cramer-von Mises Test
Epps-Singleton Test
F-test / Variance Test 계열
Fisher's Exact Test
G-test
KS Test
Kuiper's Test
Levene's Test
Mann-Whitney U / Wilcoxon Rank Sum Test
t-test 계열
```

`TEST_STATISTIC`은 가장 일반적인 산출값이다. 하지만 method별 scale, 방향, null hypothesis가 다르기 때문에 통합 의미는 "검정량" 정도로만 유지해야 한다.

KS statistic은 CDF 최대 차이다. Chi-square statistic은 기대 빈도 대비 관측 빈도 차이의 누적량이다. t statistic은 평균 차이를 표준오차로 나눈 값이다. Levene statistic은 variance equality를 보기 위한 검정량이다.

선택 기준:

```text
TEST_STATISTIC 자체로 method를 고르지 않는다.
먼저 어떤 차이를 보고 싶은지 정한다.

분포 전체 차이:
  KS, Anderson-Darling, Cramer-von Mises

평균 차이:
  t-test

분산 차이:
  Levene, F-test

범주형 빈도 차이:
  Chi-square, G-test, Fisher's Exact

rank 기반 위치 차이:
  Mann-Whitney U
```

보고서 주의:

```text
서로 다른 TEST_STATISTIC 값을 크기 비교하지 않는다.
항상 method name과 p-value 또는 threshold를 함께 둔다.
```

### MEAS-040 WARNING_STATE

관련 method:

```text
DDM
RDDM
```

`WARNING_STATE`는 drift 확정 전 경고 상태다. DDM과 RDDM 모두 warning state를 사용할 수 있지만, RDDM은 DDM의 오래된 인스턴스 누적 문제를 완화하기 위한 개선 logic이 포함된다.

DDM warning은 오류율과 표준편차가 과거 최소 기준보다 올라가 drift 가능성이 커진 상태다. RDDM warning은 유사한 error stream 기반 경고지만, 오래된 기준을 어떻게 유지/삭제할지에 대한 정책이 더 중요하다.

선택 기준:

```text
기본 supervised error stream warning:
  DDM

long-running stream, recurring drift, 오래된 기준 누적 완화:
  RDDM
```

보고서 주의:

```text
WARNING_STATE는 drift state가 아니다.
warning 구간 데이터 보관, label 품질 확인, class별 오류율 분석의 trigger로 쓴다.
```

### MEAS-042 WINDOW_SIZE

관련 method:

```text
ADWIN
RDDM
```

`WINDOW_SIZE`는 method별로 의미가 다르다.

ADWIN의 window size는 adaptive window의 현재 폭이다. ADWIN은 stream에서 window를 조정하면서 과거/최근 평균 차이를 감지하므로, window가 줄어드는 것은 최근 데이터가 과거와 달라졌다는 신호일 수 있다.

RDDM의 retained window size는 error stream detector가 오래된 인스턴스를 얼마나 유지하는지와 관련된다. 이는 detector memory와 민감도에 영향을 준다.

선택 기준:

```text
generic numeric stream의 adaptive window 변화:
  ADWIN

supervised error stream에서 오래된 기준 유지/삭제 상태:
  RDDM
```

보고서 주의:

```text
WINDOW_SIZE는 drift score가 아니다.
ADWIN width와 RDDM retained window size를 같은 의미로 비교하지 않는다.
```

## 4. 권장 보고서 표현

### 4.1 같은 measurement, 다른 method

```text
두 방법 모두 P_VALUE를 산출하지만, 검정하는 귀무가설이 다르다.
KS Test는 단변량 경험분포 차이를 보고, Chi-square Test는 범주형 빈도 차이를 본다.
따라서 두 p-value를 직접 크기 비교하지 않고, 각 데이터 형태에 맞는 drift 후보 신호로 해석한다.
```

### 4.2 alarm state 보고

```text
DRIFT_ALARM_STATE가 발생했다는 사실만으로는 해석이 부족하다.
이번 alarm은 ADWIN에 error_rate stream을 입력해 산출된 것이므로,
streaming error rate의 평균 변화 후보로 해석한다.
feature drift 또는 concept drift 확정 여부는 별도 검증이 필요하다.
```

### 4.3 distance 계열 보고

```text
Wasserstein Distance와 Mahalanobis Distance는 모두 거리형 측정값이지만,
전자는 단변량 또는 분포 이동 크기에 가깝고,
후자는 공분산 구조를 고려한 다변량 이탈 정도에 가깝다.
따라서 동일한 "distance 증가" 표현을 쓰더라도 데이터 형태와 기준 분포 가정을 함께 설명한다.
```

## 5. 정리

같은 측정값을 여러 drift method가 출력하는 것은 중복이 아니다. 대부분 다음 둘 중 하나다.

```text
1. 형식은 같지만 다른 통계 질문에 답한다.
   예: P_VALUE, TEST_STATISTIC, DRIFT_ALARM_STATE

2. 같은 수학적 개념이지만 method 문맥이 다르다.
   예: CONTROL_LIMIT, MAHALANOBIS_DISTANCE, WINDOW_SIZE
```

따라서 mindmap이나 보고서 생성 시스템에서는 measurement만 저장하지 말고 다음 연결을 항상 유지해야 한다.

```text
DriftMethod
  -> AlgorithmVariant
  -> RawMeasurement
  -> CanonicalMeasurement
  -> InterpretationRule
```

