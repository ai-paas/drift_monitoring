# Anomaly / Novelty Drift Chart Interpretation

## CHART-ANOM-001

![CHART-ANOM-001](../charts/output/CHART-ANOM-001.png)

### 제목

정상 영역 밖 샘플 증가와 이상치 드리프트 후보

### 차트 목적

이 chart는 OCDD 또는 novelty detector가 baseline 정상 영역 밖의 current sample을 outlier로 표시하는 흐름을 설명한다.

One-Class SVM, Isolation Forest, Autoencoder reconstruction 기반 detector는 정상 baseline의 support 또는 reconstruction pattern을 학습한다. Current sample의 anomaly score가 threshold를 넘고 outlier rate가 증가하면 novelty 기반 drift 후보로 해석한다. 이 예시에서는 anomaly score threshold가 `0.62`, anomaly rate threshold가 `0.20`, alarm 시점이 `t=14`, 상단 요약의 outlier rate가 `0.37`로 표시된다.

이 차트는 다음 질문에 답한다.

```text
1. current anomaly score 분포가 baseline보다 threshold 오른쪽으로 이동했는가?
2. anomaly rate가 시간에 따라 상승하고 alarm threshold를 넘었는가?
3. PCA/UMAP projection에서 outlier가 특정 current cluster에 집중되는가?
```

### 현재 상황 요약

현재 상황은 baseline 정상 영역을 학습한 novelty detector가 current sample 중 정상 영역 밖으로 벗어난 점들을 outlier로 표시하는 사례다. Baseline score 분포는 `0.25` 부근에서 밀도 `40`으로 가장 높고 `0.60` 이후에는 거의 사라지지만, current score 분포는 `0.50` 부근 밀도 `37`까지 오른쪽으로 이동하고 threshold `0.62` 이후에도 `0.65~0.90` 구간에 남아 있다. Outlier rate는 t=1의 `0.03`에서 t=14의 `0.22`로 올라 기준선 `0.20`을 넘고, 후반에는 `0.37~0.38` 수준까지 상승한다. Projection에서도 current outlier가 baseline cluster 밖의 current 영역에 모여 있으므로, 이 예시는 정상 영역 밖 current sample 증가에 따른 anomaly 기반 drift 후보로 읽는다.

### 패널별 확인

이 chart는 세 영역으로 구성된다.

```text
좌측
  - baseline anomaly score distribution
  - current anomaly score distribution
  - anomaly score threshold
  - baseline은 0.25 부근 밀도 40에 집중되고, current는 0.50 부근 밀도 37로 오른쪽에 놓인다.
  - threshold 0.62 오른쪽의 current 밀도가 0.65에서 20, 0.70에서 13처럼 남아 있는지 확인한다.

우측 상단
  - anomaly rate trend
  - rate threshold
  - alarm marker
  - outlier rate가 t=1의 0.03에서 t=14의 0.22로 올라 threshold 0.20을 넘는지 본다.
  - 이후 0.30, 0.35, 0.37 수준까지 지속 상승하는지 확인한다.

우측 하단
  - PCA/UMAP projection scatter
  - baseline normal, current normal, current outlier 구분
  - baseline normal은 좌측 cluster, current normal은 중앙~우측 cluster, current outlier는 더 오른쪽 위 영역에 모여 있는지 확인한다.
```

상단 요약 영역에는 outlier rate, anomaly score threshold, alarm 시점을 표시한다.

### 해석 순서

먼저 좌측 anomaly score distribution에서 current score가 threshold 방향으로 이동했는지 확인한다.

```text
baseline과 current score 분포가 겹친다
  -> novelty drift 증거가 약하다.

current score가 threshold 오른쪽으로 이동한다
  -> baseline support 밖의 sample 증가 후보로 본다.

threshold 초과 영역이 커진다
  -> outlier rate trend와 projection을 함께 확인한다.
```

그 다음 우측 상단 anomaly rate trend에서 outlier 비율이 일시적 spike인지 지속 상승인지 확인한다.

마지막으로 우측 하단 projection에서 outlier가 무작위로 흩어지는지, 특정 current cluster에 집중되는지 확인한다.

패널별로는 다음처럼 읽는다.

- **Anomaly Score Distribution**: baseline score는 `0.15~0.35` 구간에 주로 몰려 있고 `0.25`에서 밀도 `40`으로 가장 높다. Current score는 `0.40~0.60` 구간에 두껍게 나타나며 `0.50`에서 밀도 `37`을 보인다. Threshold `0.62` 오른쪽에도 current 밀도가 남아 있으므로 baseline 정상 support 밖의 sample이 늘어난 것으로 본다.
- **Anomaly Rate Trend**: outlier rate가 초반 `0.03~0.08` 수준에서 상승해 t=14의 `0.22`에서 기준선 `0.20`을 넘고, 후반에는 `0.37~0.38` 수준까지 올라간다. 일시적 spike가 아니라 지속 상승이면 novelty drift 후보 신호가 강해진다.
- **PCA/UMAP Projection**: baseline normal cluster와 current normal cluster가 분리되어 있고, 빨간 outlier 점들이 baseline 영역 밖 current cluster 쪽에 집중된다. 무작위 outlier보다 특정 current 영역 집중이 더 drift 후보에 가깝다.

### Drift 후보 판단 기준

Current anomaly score 분포가 threshold 오른쪽으로 이동하고 anomaly rate가 기준선을 지속적으로 넘으며, projection에서 outlier가 baseline support 밖의 current cluster에 집중되면 OCDD/novelty detector 기반 drift 후보로 해석한다.

단, outlier는 drift 원인을 설명하지 않는다. 센서 오류, 데이터 파이프라인 이상, 입력 scale 변화, 새로운 class 유입, label delay 같은 운영 원인도 함께 점검해야 한다.

### 이 예시 차트의 해석

이 예시에서는 상단 요약에 outlier rate `0.37`, anomaly score threshold `0.62`, alarm 시점 `t=14`가 표시되어 있다. 좌측 분포에서는 baseline anomaly score가 `0.25` 부근에 집중되는 반면 current score는 `0.50` 부근으로 오른쪽 이동하고, threshold `0.62`를 넘는 current 영역이 생긴다.

우측 상단 anomaly rate trend는 t=14의 `0.22`에서 threshold `0.20`을 넘은 뒤 `0.30`, `0.35`, `0.37~0.38` 수준으로 계속 상승한다. 우측 하단 projection에서는 outlier가 baseline cluster와 분리된 current 영역에 집중된다. 따라서 이 예시는 novelty detector가 baseline support 밖의 current sample 증가를 감지한 anomaly 기반 drift 후보로 해석할 수 있다.

보고서 문장 예시는 다음과 같다.

```text
OCDD 모니터링 결과 current anomaly score 분포는 baseline 대비 오른쪽으로 이동했고,
threshold 0.62 초과 sample이 증가했다.
Anomaly rate는 t=14 이후 기준선을 넘고 최종 0.37까지 상승했으며,
projection에서도 outlier가 current cluster에 집중되었다.
이는 novelty 기반 drift 후보로 해석할 수 있다.
```

### 금지해야 할 해석

이 차트만으로 다음을 단정하지 않는다.

```text
금지 1
  - outlier 증가만으로 입력 feature drift 원인을 특정한다.

금지 2
  - anomaly score threshold 설정을 확인하지 않고 detector 민감도를 평가한다.

금지 3
  - projection 분리만으로 실제 class drift 또는 label drift를 단정한다.

금지 4
  - pipeline 오류나 scale 변화 가능성을 배제한다.
```

OCDD/novelty detector는 baseline support 밖의 sample 증가를 보여준다. 실제 원인은 feature별 drift, source 변화, preprocessing 변경, 신규 segment 유입을 함께 확인해야 한다.

### 추가 확인 항목

OCDD/novelty drift 후보가 나타나면 다음을 추가 확인한다.

- anomaly score 정의와 threshold 산정 방식
- baseline 학습 기간의 정상성
- feature scaling, missing value, preprocessing 변경
- source, device, region, segment별 outlier rate
- One-Class SVM kernel/nu, Isolation Forest contamination, Autoencoder threshold 설정
- outlier sample의 feature contribution 또는 reconstruction error breakdown
- downstream accuracy, calibration, business metric 영향

### 적합한 사용 대상

이 chart는 다음 method variant에 적합하다.

- `OCDD / ONE_CLASS_SVM_DRIFT`
- `OCDD / ISOLATION_FOREST_DRIFT_SCORE`
- `OCDD / AUTOENCODER_RECONSTRUCTION_DRIFT`
