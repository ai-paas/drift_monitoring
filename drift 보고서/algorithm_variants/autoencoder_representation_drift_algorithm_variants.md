# Autoencoder Representation Drift 알고리즘 변종 목록

## 1. 목적

이 문서는 `Autoencoder Representation Drift`를 하나의 고정된 detector로 보지 않고, drift monitoring에서 상황에 따라 선택해야 하는 **알고리즘 변종들의 family**로 정리한다.

핵심 목적은 다음이다.

```text
상황 조건 -> 적절한 Autoencoder Representation Drift 계열 변종 -> 출력 metric -> 주의사항 -> LLM 보고서 설명
```

---

## 2. Autoencoder Representation Drift의 위치

```text
methodFamily AUTOENCODER_REPRESENTATION_DRIFT
       ├─ algorithmVariant LATENT_SPACE_DRIFT
       ├─ algorithmVariant RECONSTRUCTION_ERROR_DRIFT
       └─ algorithmVariant AUTOENCODER_DOMAIN_CLASSIFIER
```

`Autoencoder Representation Drift`는 drift monitoring method 계열에 속한다. Autoencoder Representation Drift 계열을 drift monitoring 문맥에서 입력 데이터와 운영 목적에 따라 선택 가능한 변종으로 정리한다.

---

## 3. 공통 개념

```text
methodFamily AUTOENCODER_REPRESENTATION_DRIFT
  purpose ->
    Autoencoder Representation Drift 계열을 drift monitoring 문맥에서 입력 데이터와 운영 목적에 따라 선택 가능한 변종으로 정리한다.

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

## 변종: LATENT_SPACE_DRIFT

`LATENT_SPACE_DRIFT`는 autoencoder의 encoder가 만든 latent representation 분포가 기준 기간과 달라졌는지를 감시하는 변종이다. 원본 feature를 직접 비교하기보다, 모델이 압축한 저차원 표현 공간에서 reference와 current의 위치, 군집, 산포 변화를 본다. drift monitoring에서는 입력 패턴의 구조적 변화가 latent space에 반영되었는지 확인하는 신호로 사용한다.

이 변종은 다음 상황에 적합하다.

- feature 수가 많거나 상관 구조가 복잡해 원본 feature별 비교만으로 해석이 어렵다.
- autoencoder가 기준 기간 데이터로 학습되어 있고 encoder 출력이 안정적으로 저장된다.
- reference/current latent vector를 distance, MMD, classifier, embedding chart 등으로 비교할 수 있다.
- 원본 값의 작은 변화보다 전체 표현 구조 변화가 중요한 모니터링 목적이다.

해석할 때는 latent distance, distribution score, p-value, alarm을 "표현 공간의 변화"로 읽는다. distance나 score가 커지면 current sample의 latent vector가 기준 기간의 latent 분포에서 멀어졌다는 뜻이다. p-value가 있는 보조 검정을 쓰는 경우 통계적 유의성과 실제 embedding 이동 크기를 구분해야 한다. 2D projection 차트가 함께 있으면 어느 cluster나 방향에서 변화가 커졌는지 확인한다.

주의할 점은 latent space가 autoencoder 학습 상태에 의존한다는 것이다. autoencoder를 재학습했거나 encoder 버전이 바뀌면 latent 좌표 자체가 달라져 기간 비교가 무의미해질 수 있다. latent drift는 입력 구조 변화 후보이지, 어느 원본 feature가 원인인지 바로 알려주지 않는다. threshold는 기준 기간 calibration 결과로 설명하고, 원인 분석은 feature attribution이나 segment별 재검토로 보완해야 한다.

보고서 문장 예시는 다음과 같다.

```text
기준 기간과 현재 기간의 latent vector를 LATENT_SPACE_DRIFT로 비교한 결과,
current sample의 representation 분포가 기준 latent 분포에서 멀어지는 신호가 관측되었다.
이는 원본 feature 조합의 구조적 변화 후보로 볼 수 있다.
다만 encoder 버전과 threshold calibration의 영향을 받으므로
원본 feature별 변화와 segment별 embedding 차이를 함께 확인해야 한다.
```

---

## 변종: RECONSTRUCTION_ERROR_DRIFT

`RECONSTRUCTION_ERROR_DRIFT`는 autoencoder가 현재 데이터를 얼마나 잘 복원하는지를 기준 기간과 비교하는 변종이다. 기준 데이터 패턴을 잘 학습한 autoencoder라면, 현재 데이터가 기준 패턴에서 벗어날수록 reconstruction error가 커질 수 있다. drift monitoring에서는 복원 오차 분포의 상승 또는 모양 변화를 입력 패턴 변화 후보로 해석한다.

이 변종은 다음 상황에 적합하다.

- 기준 기간 데이터로 학습한 autoencoder를 고정해 current data를 평가한다.
- reconstruction error, squared error, absolute error, feature별 error를 window 단위로 저장한다.
- anomaly-like drift나 기준 패턴에서 벗어난 입력 증가를 감시한다.
- latent vector보다 복원 실패 정도가 운영 설명에 더 직접적이다.

해석할 때는 평균 reconstruction error, error distribution, threshold exceedance rate, alarm을 함께 본다. 평균 error가 상승하면 current sample이 기준 패턴보다 복원하기 어려워졌다는 뜻이다. exceedance rate가 늘면 기준 threshold를 넘는 case 비중이 커졌다는 신호다. p-value나 distance를 함께 쓰는 경우 error 분포 차이의 통계적 유의성과 error 증가의 업무상 크기를 분리해서 설명한다.

주의할 점은 reconstruction error가 반드시 성능 저하나 concept drift를 뜻하지 않는다는 것이다. 입력 scaling, missing value 처리, feature schema, autoencoder 버전이 바뀌면 error가 급격히 달라질 수 있다. autoencoder가 기준 기간의 rare pattern을 충분히 학습하지 못했다면 특정 정상 case도 높은 error를 보일 수 있다. threshold는 anomaly 또는 drift 운영 정책에 맞게 calibration한 값으로 보고해야 한다.

보고서 문장 예시는 다음과 같다.

```text
현재 데이터를 RECONSTRUCTION_ERROR_DRIFT로 평가한 결과,
reconstruction error 분포가 기준 기간 대비 상승하고 threshold 초과 비중이 늘었다.
이는 현재 입력이 기준 기간 패턴보다 복원하기 어려워진 drift 후보 신호다.
다만 전처리, feature schema, autoencoder 버전 변경의 영향을 받을 수 있으므로
오차가 큰 case와 feature별 reconstruction error를 추가 확인해야 한다.
```

---

## 변종: AUTOENCODER_DOMAIN_CLASSIFIER

`AUTOENCODER_DOMAIN_CLASSIFIER`는 autoencoder에서 얻은 latent representation이나 reconstruction feature를 사용해 reference와 current domain을 구분할 수 있는지 확인하는 변종이다. domain classifier의 성능이 우연 수준보다 높다면 두 기간의 표현이 구분 가능하다는 뜻이다. drift monitoring에서는 "현재 데이터가 기준 데이터와 분류될 만큼 달라졌는가"를 보는 classifier 기반 drift 후보 신호로 쓴다.

이 변종은 다음 상황에 적합하다.

- reference/current label을 domain label로 붙여 이진 classifier를 학습하거나 평가할 수 있다.
- 원본 feature 대신 autoencoder representation 기반으로 domain separability를 보고 싶다.
- drift score를 AUC, accuracy, log loss, domain probability로 표현하는 운영 방식이 필요하다.
- latent space drift의 존재를 classifier 관점에서 보조 검증하려 한다.

해석할 때는 domain classifier AUC, accuracy, calibration score, domain probability를 본다. AUC가 0.5에 가까우면 reference와 current를 잘 구분하지 못한다는 뜻이고, AUC가 높아질수록 두 domain이 표현 공간에서 분리된다는 신호다. domain probability가 특정 segment에서 높다면 그 segment가 current-like pattern을 강하게 가진다는 의미로 볼 수 있다. 이 값은 분포 구분 가능성을 말하며, 업무 원인을 직접 알려주는 값은 아니다.

주의할 점은 classifier가 과적합되면 drift 신호가 과장될 수 있다는 것이다. train/test split, cross-validation, class balance, reference/current sample size를 반드시 확인해야 한다. domain label은 기간 구분 label일 뿐 업무 정답 label이 아니므로, 높은 AUC를 성능 저하나 원인 확정으로 표현하면 안 된다. autoencoder와 domain classifier 중 어느 모델 버전으로 산출했는지도 보고서에 남긴다.

보고서 문장 예시는 다음과 같다.

```text
Autoencoder representation을 AUTOENCODER_DOMAIN_CLASSIFIER로 평가한 결과,
domain classifier가 reference와 current sample을 우연 수준보다 높게 구분했다.
이는 두 기간의 표현 분포가 classifier 관점에서 분리되는 drift 후보 신호다.
다만 classifier 과적합과 sample imbalance의 영향을 받을 수 있으므로
holdout 성능, segment별 domain probability, 원본 feature 변화를 함께 확인해야 한다.
```

---

## SelectionRule 카탈로그

```text
selectionRule AUTOENCODER_REPRESENTATION_DRIFT_DEFAULT_USE
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

> Autoencoder Representation Drift 카탈로그는 "이 방법이 무엇인가"가 아니라, "어떤 상황에서 어떤 변종을 선택하고 어떤 주의사항과 함께 설명해야 하는가"를 구조화한다.
