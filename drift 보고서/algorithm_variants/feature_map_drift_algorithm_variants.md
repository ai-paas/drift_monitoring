# Feature Map Drift 알고리즘 변종 목록

## 1. 목적

이 문서는 `Feature Map Drift`를 하나의 고정된 detector로 보지 않고, drift monitoring에서 상황에 따라 선택해야 하는 **알고리즘 변종들의 family**로 정리한다.

핵심 목적은 다음이다.

```text
상황 조건 -> 적절한 Feature Map Drift 계열 변종 -> 출력 metric -> 주의사항 -> LLM 보고서 설명
```

---

## 2. Feature Map Drift의 위치

```text
methodFamily FEATURE_MAP_DRIFT
       ├─ algorithmVariant MODEL_FEATURE_MAP_KS
       ├─ algorithmVariant MODEL_FEATURE_MAP_MMD
       └─ algorithmVariant LAYERWISE_FEATURE_MAP_DRIFT
```

`Feature Map Drift`는 drift monitoring method 계열에 속한다. Feature Map Drift 계열을 drift monitoring 문맥에서 입력 데이터와 운영 목적에 따라 선택 가능한 변종으로 정리한다.

---

## 3. 공통 개념

```text
methodFamily FEATURE_MAP_DRIFT
  purpose ->
    Feature Map Drift 계열을 drift monitoring 문맥에서 입력 데이터와 운영 목적에 따라 선택 가능한 변종으로 정리한다.

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

## 변종: MODEL_FEATURE_MAP_KS

`MODEL_FEATURE_MAP_KS`는 모델 내부 feature map 또는 embedding의 각 축에서 reference 기간과 current 기간의 분포가 달라졌는지 KS 검정으로 확인하는 변종이다. 원본 입력값이 아니라 모델이 만들어 낸 표현 공간을 보기 때문에, 입력 통계만으로는 잘 보이지 않는 내부 표현 변화 후보를 찾는 데 쓴다. 출력은 보통 feature별 KS statistic, p-value, 선택한 threshold 기준의 alarm 여부로 해석한다.

사용 상황:
- 이미지, 텍스트, 시계열 모델처럼 중간 feature map 또는 embedding을 안정적으로 추출할 수 있을 때
- reference 기간과 current 기간의 표본을 같은 전처리와 같은 모델 버전으로 비교할 때
- 어떤 feature 축에서 분포 변화 신호가 강한지 빠르게 선별하고 싶을 때

해석 방법:
- KS statistic이 클수록 해당 feature 축의 누적분포 차이가 크다는 뜻이다.
- p-value가 작으면 "두 기간의 feature 분포가 같다"는 가설을 기각할 근거가 강해진다.
- 여러 feature를 동시에 보면 가장 큰 statistic, 유의한 feature 비율, alarm feature 목록을 함께 읽어야 한다.
- 유의한 축이 많아졌다면 모델 내부 표현의 drift 후보로 볼 수 있지만, 그 자체가 성능 저하를 증명하지는 않는다.

주의점:
- feature 축을 많이 검사하면 우연히 유의하게 나오는 축이 늘어날 수 있으므로 다중 비교나 운영 threshold 근거를 함께 남긴다.
- 표본 수가 크면 작은 차이도 유의해질 수 있어 statistic 크기와 업무 영향도를 함께 확인한다.
- 모델 버전, 전처리, feature 추출 위치가 바뀌면 drift가 아니라 측정 조건 변화일 수 있다.

보고서 문장 예시:

```text
모델 feature map을 MODEL_FEATURE_MAP_KS로 비교한 결과,
current 기간의 일부 feature 축에서 KS statistic과 유의 신호가 reference 기간 대비 증가했다.
이는 모델 내부 표현 공간에서 분포 변화 후보가 관측된 것으로 해석할 수 있다.
다만 다중 feature 검정과 표본 수 영향이 있으므로, 주요 축의 효과 크기와 성능 지표 변화를 함께 확인해야 한다.
```

---

## 변종: MODEL_FEATURE_MAP_MMD

`MODEL_FEATURE_MAP_MMD`는 reference 기간과 current 기간의 feature map 전체 분포 차이를 MMD 거리로 요약하는 변종이다. KS가 feature 축별 차이를 따로 보는 방식이라면, MMD는 kernel을 통해 다차원 표현의 전체적인 분포 차이를 하나의 distance 또는 score로 읽는다. 출력은 MMD statistic, permutation 또는 calibration 기반 p-value/score, threshold 초과 여부로 보고한다.

사용 상황:
- feature 간 상관 구조나 다차원 embedding의 전체 이동을 보고 싶을 때
- 축별 검정보다 하나의 대표 drift score가 필요한 운영 모니터링일 때
- reference/current 표본을 같은 모델 버전의 같은 layer에서 추출할 수 있을 때

해석 방법:
- MMD 값이 커질수록 두 기간의 feature map 분포가 더 멀어졌다는 뜻이다.
- p-value 또는 empirical score가 threshold를 넘으면 feature 표현의 drift 후보 신호로 본다.
- score가 상승했더라도 어떤 feature가 원인인지는 직접 알려주지 않으므로, 필요하면 layer별 또는 feature별 후속 분석을 붙인다.
- 반복 window에서 MMD가 지속적으로 높으면 일시적 잡음보다 구조적 변화 가능성을 더 크게 본다.

주의점:
- kernel 종류와 bandwidth 선택이 민감도에 영향을 주므로 calibration 조건을 보고서에 남긴다.
- 표본 수가 부족하면 MMD 추정이 불안정하고, 표본 수가 매우 크면 작은 차이도 alarm으로 이어질 수 있다.
- MMD는 분포 간 거리 신호이지 업무 원인, 라벨 분포 변화, 성능 저하를 직접 확정하지 않는다.

보고서 문장 예시:

```text
모델 feature map을 MODEL_FEATURE_MAP_MMD로 모니터링한 결과,
current window의 MMD score가 기준 window 대비 상승해 threshold 근처 또는 초과 구간에 진입했다.
이는 다차원 표현 공간 전체에서 분포 변화 후보가 커졌다는 신호로 볼 수 있다.
다만 kernel 설정과 baseline calibration에 따른 민감도 차이가 있으므로, 원인 분석은 feature/layer별 후속 점검으로 보완해야 한다.
```

---

## 변종: LAYERWISE_FEATURE_MAP_DRIFT

`LAYERWISE_FEATURE_MAP_DRIFT`는 모델의 여러 layer에서 feature map drift score를 각각 계산해 변화가 어느 표현 단계에서 두드러지는지 보는 변종이다. 입력에 가까운 layer와 출력에 가까운 layer를 분리해 보면, 단순 입력 스타일 변화인지 모델의 고수준 표현까지 달라졌는지 구분하는 데 도움이 된다. 출력은 layer별 statistic 또는 distance, p-value/score, layer별 alarm 상태로 읽는다.

사용 상황:
- deep model에서 어느 layer부터 drift 후보가 나타나는지 추적하고 싶을 때
- 입력 drift와 task 표현 drift를 구분할 단서가 필요할 때
- 모델 구조와 feature 추출 layer가 고정되어 있고 layer별 baseline이 준비되어 있을 때

해석 방법:
- 앞쪽 layer에서만 score가 높으면 입력 형식, 노이즈, 전처리 차이 같은 저수준 변화 후보를 먼저 본다.
- 뒤쪽 layer까지 score가 높으면 모델의 task 관련 표현도 달라졌을 가능성을 더 크게 본다.
- 특정 layer만 alarm이면 해당 layer의 추출 위치, activation scale, 표본 수를 확인한 뒤 해석한다.
- layer별 신호를 시간 순서로 보면 변화가 확산되는지, 특정 구간에만 일시적으로 나타나는지 판단할 수 있다.

주의점:
- layer마다 activation 차원과 scale이 달라 score를 단순 비교하기 어렵다.
- 많은 layer를 동시에 보면 false alarm이 늘 수 있으므로 layer별 threshold 또는 요약 규칙이 필요하다.
- layerwise 결과는 원인 위치를 암시할 뿐이며, 데이터 수집 조건이나 모델 배포 변경 여부를 함께 확인해야 한다.

보고서 문장 예시:

```text
모델의 여러 layer feature map을 LAYERWISE_FEATURE_MAP_DRIFT로 비교한 결과,
current 기간에서 특정 layer의 drift score가 reference 기준보다 높게 나타났다.
이는 해당 표현 단계에서 분포 변화 후보가 관측된다는 뜻이며, 뒤쪽 layer까지 이어지는지는 별도로 확인해야 한다.
다만 layer별 scale과 threshold가 다르므로 layer 간 절대값 비교만으로 원인을 단정하지 않는다.
```

---

## SelectionRule 카탈로그

```text
selectionRule FEATURE_MAP_DRIFT_DEFAULT_USE
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

> Feature Map Drift 카탈로그는 "이 방법이 무엇인가"가 아니라, "어떤 상황에서 어떤 변종을 선택하고 어떤 주의사항과 함께 설명해야 하는가"를 구조화한다.
