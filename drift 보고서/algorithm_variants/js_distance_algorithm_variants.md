# JS Distance 알고리즘 변종 목록

## 1. 목적

이 문서는 `JS Distance`를 하나의 고정된 detector로 보지 않고, drift monitoring에서 상황에 따라 선택해야 하는 **알고리즘 변종들의 family**로 정리한다.

핵심 목적은 다음이다.

```text
상황 조건 -> 적절한 JS Distance 계열 변종 -> 출력 metric -> 주의사항 -> LLM 보고서 설명
```

---

## 2. JS Distance의 위치

```text
methodFamily JS_DISTANCE
       ├─ algorithmVariant JENSEN_SHANNON_DIVERGENCE
       ├─ algorithmVariant JENSEN_SHANNON_DISTANCE
       ├─ algorithmVariant MULTICLASS_PROBABILITY_JS
       └─ algorithmVariant TEXT_TOPIC_JS
```

`JS Distance`는 drift monitoring method 계열에 속한다. JS Distance 계열을 drift monitoring 문맥에서 입력 데이터와 운영 목적에 따라 선택 가능한 변종으로 정리한다.

---

## 3. 공통 개념

```text
methodFamily JS_DISTANCE
  purpose ->
    JS Distance 계열을 drift monitoring 문맥에서 입력 데이터와 운영 목적에 따라 선택 가능한 변종으로 정리한다.

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

## 변종: JENSEN_SHANNON_DIVERGENCE

`JENSEN_SHANNON_DIVERGENCE`는 reference/current 확률분포를 평균 분포와 각각 비교해 대칭적이고 bounded한 divergence로 요약하는 JS 계열 변종이다. KL divergence보다 0 확률 문제에 덜 취약하고 두 분포의 차이를 안정적으로 비교할 수 있다. 출력은 JS divergence, threshold 초과 여부, alarm state로 해석한다.

사용 상황:
- category, histogram, probability vector처럼 합이 1인 분포를 reference/current로 비교할 때
- KL divergence의 비대칭성과 zero-bin 민감도를 줄이고 싶을 때
- 여러 feature의 drift score를 bounded scale로 screening하고 싶을 때

해석 방법:
- JS divergence가 0에 가까우면 두 분포가 유사하고, 값이 커질수록 분포 차이가 크다.
- threshold를 넘으면 분포 구성 변화 후보로 해석한다.
- divergence 자체는 방향을 알려주지 않으므로 항목별 확률 차이를 함께 확인한다.
- alarm은 feature distribution drift 후보이며 원인 또는 성능 저하 확정은 아니다.

주의점:
- log base와 normalization 방식에 따라 score 범위가 달라질 수 있다.
- smoothing이나 zero-bin 처리 기준을 reference/current에 동일하게 적용해야 한다.
- 표본 수가 적은 category가 많으면 확률 추정 불안정성이 score에 반영된다.

보고서 문장 예시:

```text
JENSEN_SHANNON_DIVERGENCE로 reference/current 확률분포를 비교한 결과,
JS divergence가 기준 threshold를 초과했다.
이는 current 기간의 분포 구성이 reference와 달라졌을 가능성을 나타내는 drift 후보 신호다.
다만 log base, smoothing 기준, 항목별 확률 차이를 함께 확인해야 한다.
```

---

## 변종: JENSEN_SHANNON_DISTANCE

`JENSEN_SHANNON_DISTANCE`는 JS divergence의 제곱근을 사용해 metric 성질을 갖는 distance로 분포 차이를 표현하는 변종이다. divergence보다 거리 해석이 직관적이며, 분포 간 유사도 비교나 clustering 보조 지표로 쓰기 좋다. 출력은 JS distance, threshold 초과 여부, alarm state로 해석한다.

사용 상황:
- 분포 차이를 divergence보다 distance 형태로 보고하고 싶을 때
- 여러 분포 또는 여러 feature 간 상대적 거리 비교가 필요한 경우
- threshold 기반 drift screening에서 bounded distance score를 쓰고 싶을 때

해석 방법:
- distance가 0이면 두 분포가 같고, 커질수록 reference/current 분포 차이가 크다.
- threshold 초과는 두 분포가 운영상 허용 범위보다 멀어졌다는 drift 후보 신호다.
- score가 커진 원인은 category/bin별 확률 차이로 분해해 설명한다.
- distance는 방향성이 없으므로 증가/감소 해석은 별도 비율표를 사용한다.

주의점:
- divergence와 distance를 혼용하면 threshold와 scale이 달라져 비교가 어렵다.
- log base와 normalization 정책을 보고서에 남겨야 재현성이 유지된다.
- sparse distribution에서는 smoothing 정책이 distance에 영향을 준다.

보고서 문장 예시:

```text
JENSEN_SHANNON_DISTANCE로 reference/current 분포 간 거리를 계산한 결과,
distance가 calibration threshold를 초과했다.
이는 current 분포가 기준 분포에서 운영상 의미 있게 멀어진 drift 후보 신호다.
다만 이 score는 방향을 직접 말해주지 않으므로, 주요 category 또는 bin별 확률 차이를 함께 제시해야 한다.
```

---

## 변종: MULTICLASS_PROBABILITY_JS

`MULTICLASS_PROBABILITY_JS`는 다중분류 모델의 예측 확률 벡터 또는 class probability distribution을 JS score로 비교하는 변종이다. label이 없어도 모델이 current 데이터에 부여하는 class 확률 구성이 reference와 달라졌는지 확인할 수 있다. 출력은 JS divergence 또는 distance, class별 확률 차이, alarm state로 해석한다.

사용 상황:
- 다중분류 모델에서 predicted probability 또는 predicted class mix 변화가 중요한 경우
- label 도착 전에도 모델 출력 분포 drift 후보를 감시하고 싶을 때
- class별 confidence 구성이나 class prior 변화 가능성을 screening할 때

해석 방법:
- JS score가 커지면 current 예측 확률 분포가 reference보다 달라졌다는 뜻이다.
- class별 평균 확률 차이를 보면 어떤 class가 score 증가를 주도했는지 설명할 수 있다.
- alarm은 prediction distribution drift 후보이며 실제 정답 분포 변화 또는 성능 저하 확정은 아니다.
- confidence shift와 class mix shift를 구분하려면 top class 비율과 entropy도 함께 본다.

주의점:
- 모델 버전이 바뀌면 probability calibration이 달라져 score 비교가 어려울 수 있다.
- label이 없으면 concept drift나 accuracy degradation을 확정할 수 없다.
- class imbalance가 큰 경우 작은 class 확률 변화의 업무 의미를 별도로 판단해야 한다.

보고서 문장 예시:

```text
MULTICLASS_PROBABILITY_JS로 모델 예측 확률 분포를 비교한 결과,
current 기간의 JS score가 기준 threshold를 초과했다.
이는 모델 출력의 class probability 구성이 reference와 달라졌을 가능성을 나타낸다.
다만 label이 없는 상태에서는 성능 저하를 확정할 수 없으므로, class별 확률 차이와 calibration 변경 여부를 함께 확인해야 한다.
```

---

## 변종: TEXT_TOPIC_JS

`TEXT_TOPIC_JS`는 텍스트 데이터의 topic distribution, intent distribution, token category distribution을 JS score로 비교하는 변종이다. reference/current 텍스트 입력의 주제 구성이나 의미 영역이 달라졌는지 label 없이도 screening할 수 있다. 출력은 topic-level JS score, topic별 비율 차이, alarm state로 해석한다.

사용 상황:
- 문의, 리뷰, 검색어, 문서 입력의 주제 구성이 기간별로 달라지는지 감시할 때
- topic model, intent classifier, embedding cluster 비율을 drift signal로 쓰는 경우
- 텍스트 도메인 변화가 downstream 모델 성능에 영향을 줄 수 있는지 조기 점검할 때

해석 방법:
- JS score가 커질수록 current topic composition이 reference와 달라졌다는 뜻이다.
- topic별 비율 차이를 보면 증가한 주제와 감소한 주제를 설명할 수 있다.
- alarm은 텍스트 입력 domain 또는 topic mix 변화 후보이며, 모델 실패 원인 확정은 아니다.
- 대표 문서 샘플을 함께 확인하면 score 변화가 실제 주제 변화인지 전처리 변경인지 구분하기 쉽다.

주의점:
- topic model이나 intent classifier 버전이 바뀌면 이전 score와 직접 비교하기 어렵다.
- 짧은 텍스트나 다국어 혼합 입력에서는 topic 확률이 불안정할 수 있다.
- 개인정보 제거, tokenization, stopword 정책 변경이 topic distribution을 바꿀 수 있다.

보고서 문장 예시:

```text
TEXT_TOPIC_JS로 reference/current 텍스트 topic 분포를 비교한 결과,
current 기간의 JS score가 기준보다 높아 topic mix 변화 후보가 관측됐다.
이는 최근 입력 텍스트의 주제 구성이 기준 기간과 달라졌을 가능성을 나타낸다.
다만 topic 모델 버전과 전처리 정책이 동일한지 확인하고, 주요 topic별 대표 문서를 함께 검토해야 한다.
```

---

## SelectionRule 카탈로그

```text
selectionRule JS_DISTANCE_DEFAULT_USE
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

> JS Distance 카탈로그는 "이 방법이 무엇인가"가 아니라, "어떤 상황에서 어떤 변종을 선택하고 어떤 주의사항과 함께 설명해야 하는가"를 구조화한다.
