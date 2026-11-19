# Wasserstein Distance 알고리즘 변종 목록

## 1. 목적

이 문서는 `Wasserstein Distance`를 하나의 고정된 detector로 보지 않고, drift monitoring에서 상황에 따라 선택해야 하는 **알고리즘 변종들의 family**로 정리한다.

핵심 목적은 다음이다.

```text
상황 조건 -> 적절한 Wasserstein Distance 계열 변종 -> 출력 metric -> 주의사항 -> LLM 보고서 설명
```

---

## 2. Wasserstein Distance의 위치

```text
methodFamily WASSERSTEIN_DISTANCE
       ├─ algorithmVariant WASSERSTEIN_1D_EXACT
       ├─ algorithmVariant WASSERSTEIN_WINDOW_TREND
       ├─ algorithmVariant SLICED_WASSERSTEIN_EMBEDDING
       └─ algorithmVariant WASSERSTEIN_APPROX_HISTOGRAM
```

`Wasserstein Distance`는 거리 기반 reference/current 분포 비교 계열에 속한다. 분포를 서로 맞추기 위해 필요한 이동 비용 또는 질량 이동 크기로 drift 규모를 측정한다.

---

## 3. 공통 개념

```text
methodFamily WASSERSTEIN_DISTANCE
  purpose ->
    분포를 서로 맞추기 위해 필요한 이동 비용 또는 질량 이동 크기로 drift 규모를 측정한다.

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

## 변종: WASSERSTEIN_1D_EXACT

단변량 연속형 feature 또는 score의 reference/current sample을 직접 비교해 1D Wasserstein distance를 계산하는 변종이다.

- 사용 상황: feature별 drift ranking이나 score, confidence 분포의 이동 크기를 설명해야 할 때 적합하다.
- 해석 방법: 거리가 클수록 두 분포를 맞추기 위해 더 큰 값 이동이 필요하다는 의미로 drift 규모 후보를 판단한다.
- 주의점: feature 단위와 scale에 민감하므로 scaling 여부와 원 단위를 함께 보고한다.
- 보고서 문장 예시: "1D Wasserstein distance가 큰 feature는 current 분포가 기준 분포에서 값 방향으로 많이 이동한 후보로 해석된다."

---

## 변종: WASSERSTEIN_WINDOW_TREND

슬라이딩 window마다 Wasserstein distance를 계산해 시간에 따른 거리 추세와 threshold 초과 지속성을 감시하는 변종이다.

- 사용 상황: gradual drift, recurring drift, 일시적 spike와 지속적 변화의 구분이 필요한 운영 모니터링에 적합하다.
- 해석 방법: distance trend가 상승하거나 threshold 초과가 여러 window에서 유지되면 분포 변화가 지속되는 후보로 본다.
- 주의점: reference 기간이 안정적이지 않으면 trend 기준이 흔들리므로 정상 기간 replay나 과거 백분위수로 threshold를 calibration한다.
- 보고서 문장 예시: "Wasserstein distance가 여러 window에서 상승해 단발성 변동보다 지속적 분포 이동 후보가 강하게 나타났다."

---

## 변종: SLICED_WASSERSTEIN_EMBEDDING

고차원 embedding을 여러 1D projection으로 나눈 뒤 각 projection의 Wasserstein distance를 평균해 근사하는 변종이다.

- 사용 상황: 텍스트, 이미지, representation embedding처럼 고차원 분포를 직접 비교하기 어려울 때 적합하다.
- 해석 방법: sliced Wasserstein distance가 커지면 여러 투영 방향에서 embedding 분포가 기준과 달라졌다는 후보로 본다.
- 주의점: projection 수와 random seed에 따라 값이 달라질 수 있으므로 재현 가능한 설정을 기록한다.
- 보고서 문장 예시: "Sliced Wasserstein distance가 증가해 고차원 embedding 분포가 여러 projection 기준에서 이동한 후보가 확인되었다."

---

## 변종: WASSERSTEIN_APPROX_HISTOGRAM

대용량 데이터에서 sample-level 정렬 대신 histogram 또는 bin 요약으로 Wasserstein distance를 근사 계산하는 변종이다.

- 사용 상황: 많은 feature를 운영 dashboard에서 빠르게 screening하거나 실시간 계산 비용을 줄여야 할 때 적합하다.
- 해석 방법: approximate distance가 커지면 bin 요약 기준에서 reference와 current 분포 이동이 커진 후보로 본다.
- 주의점: bin 폭, bin 범위, clipping 정책이 결과에 영향을 주므로 정확한 sample-level distance와 직접 비교하지 않는다.
- 보고서 문장 예시: "Histogram 근사 Wasserstein distance 기준으로 대량 feature screening에서 분포 이동 후보가 식별되었다."

---

## SelectionRule 카탈로그

```text
selectionRule WASSERSTEIN_DISTANCE_DEFAULT_USE
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

> Wasserstein Distance 카탈로그는 "이 방법이 무엇인가"가 아니라, "어떤 상황에서 어떤 변종을 선택하고 어떤 주의사항과 함께 설명해야 하는가"를 구조화한다.
