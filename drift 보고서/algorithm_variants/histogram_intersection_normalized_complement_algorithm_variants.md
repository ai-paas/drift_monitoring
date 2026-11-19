# Histogram Intersection Normalized Complement 알고리즘 변종 목록

## 1. 목적

이 문서는 `Histogram Intersection Normalized Complement`를 하나의 고정된 detector로 보지 않고, drift monitoring에서 상황에 따라 선택해야 하는 **알고리즘 변종들의 family**로 정리한다.

핵심 목적은 다음이다.

```text
상황 조건 -> 적절한 Histogram Intersection Normalized Complement 계열 변종 -> 출력 metric -> 주의사항 -> LLM 보고서 설명
```

---

## 2. Histogram Intersection Normalized Complement의 위치

```text
methodFamily HISTOGRAM_INTERSECTION_NORMALIZED_COMPLEMENT
       ├─ algorithmVariant HINC_CATEGORICAL
       ├─ algorithmVariant HINC_HISTOGRAM_NUMERIC
       └─ algorithmVariant HINC_IMAGE_FEATURE
```

`Histogram Intersection Normalized Complement`는 drift monitoring method 계열에 속한다. Histogram Intersection Normalized Complement 계열을 drift monitoring 문맥에서 입력 데이터와 운영 목적에 따라 선택 가능한 변종으로 정리한다.

---

## 3. 공통 개념

```text
methodFamily HISTOGRAM_INTERSECTION_NORMALIZED_COMPLEMENT
  purpose ->
    Histogram Intersection Normalized Complement 계열을 drift monitoring 문맥에서 입력 데이터와 운영 목적에 따라 선택 가능한 변종으로 정리한다.

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

## 변종: HINC_CATEGORICAL

`HINC_CATEGORICAL`은 category 확률분포의 histogram intersection을 계산한 뒤, normalized complement로 overlap 부족분을 drift score로 표현하는 변종이다. 값이 작으면 두 분포가 많이 겹치고, 값이 클수록 category composition이 덜 겹친다. 출력은 HINC score, category별 overlap, alarm state로 해석한다.

사용 상황:
- 범주형 feature의 reference/current 구성 overlap을 직관적으로 보고할 때
- 주요 category의 비중 이동이나 신규 category 유입을 drift 후보로 screening할 때
- 거리 점수와 함께 "얼마나 덜 겹치는지"를 설명하고 싶을 때

해석 방법:
- HINC score가 0에 가까우면 reference/current category 분포가 거의 겹친다.
- score가 threshold를 넘으면 category 구성 overlap이 부족해진 drift 후보로 본다.
- category별 min(reference, current) overlap을 보면 어느 category가 공통 부분을 줄였는지 설명할 수 있다.
- alarm은 feature composition 변화 신호이며, 모델 성능 영향은 별도 확인한다.

주의점:
- rare category와 unknown category 처리 기준이 달라지면 score가 과대평가될 수 있다.
- category set alignment가 맞지 않으면 overlap 계산이 왜곡된다.
- threshold는 정상 운영 구간의 score 분포로 calibration하는 편이 안정적이다.

보고서 문장 예시:

```text
HINC_CATEGORICAL로 category 분포 overlap을 비교한 결과,
normalized complement score가 기준 threshold를 초과했다.
이는 current 기간의 category 구성이 reference와 충분히 겹치지 않는 drift 후보 신호다.
다만 rare category grouping과 unknown 처리 기준이 동일한지 확인해야 한다.
```

---

## 변종: HINC_HISTOGRAM_NUMERIC

`HINC_HISTOGRAM_NUMERIC`은 numeric feature를 histogram bin으로 나누고 reference/current bin 확률의 intersection complement를 계산하는 변종이다. 값 구간별 분포가 얼마나 겹치지 않는지 score로 표현해 평균 이동, tail 변화, 특정 구간 비중 변화를 함께 감지한다. 출력은 HINC score, bin별 overlap 부족분, alarm state로 해석한다.

사용 상황:
- numeric feature의 분포 overlap 감소를 빠르게 screening할 때
- 평균은 비슷하지만 특정 값 구간의 비중이 달라지는 drift 후보를 찾을 때
- histogram 차트와 함께 직관적인 "겹치지 않는 비율"을 보고하고 싶을 때

해석 방법:
- HINC score가 커질수록 reference/current histogram의 겹치는 면적이 작다.
- threshold 초과는 numeric distribution shape 변화 후보로 해석한다.
- bin별 complement를 보면 drift가 중심 이동인지 tail 증가인지 설명할 수 있다.
- score는 bounded distance 성격이므로 서로 다른 feature의 상대 비교에도 보조적으로 쓸 수 있다.

주의점:
- binning 방식, clipping, scaling 변경이 score에 직접 영향을 준다.
- 표본 수가 적으면 bin별 확률이 불안정해져 score가 흔들릴 수 있다.
- 고차원 feature 전체를 한 score로 합칠 때는 feature별 가중 기준을 문서화해야 한다.

보고서 문장 예시:

```text
HINC_HISTOGRAM_NUMERIC으로 numeric feature histogram overlap을 비교한 결과,
current 분포의 normalized complement score가 기준보다 높게 나타났다.
이는 기준 기간과 겹치지 않는 값 구간의 비중이 증가한 drift 후보 신호다.
다만 bin 경계와 표본 수에 따라 결과가 달라질 수 있으므로, 주요 bin별 확률 차이를 함께 확인해야 한다.
```

---

## 변종: HINC_IMAGE_FEATURE

`HINC_IMAGE_FEATURE`는 이미지 feature, embedding, color/texture histogram 같은 시각 데이터 요약 분포의 overlap 감소를 normalized complement로 측정하는 변종이다. reference/current 이미지 입력의 시각적 구성이나 embedding bin 분포가 얼마나 달라졌는지 빠르게 screening한다. 출력은 image feature HINC score, feature/bin별 기여, alarm state로 해석한다.

사용 상황:
- 이미지 분류/검출 서비스에서 입력 이미지의 색상, 밝기, texture, embedding 분포 변화를 감시할 때
- 촬영 환경, 장비, 해상도, 전처리 변경으로 인한 input drift 후보를 찾을 때
- 이미지 원본을 직접 비교하기보다 요약 feature histogram overlap을 보고할 때

해석 방법:
- HINC score가 클수록 current 이미지 feature 분포가 reference와 덜 겹친다.
- feature/bin별 complement가 큰 영역은 변화가 집중된 시각 특성 후보를 나타낸다.
- alarm은 image input distribution 변화 후보이며, 모델 정확도 저하 확정은 아니다.
- 대표 이미지 샘플과 함께 보면 밝기 변화, 배경 변화, class mix 변화 등을 구분하기 쉽다.

주의점:
- embedding extractor나 image preprocessing 버전이 바뀌면 score 비교가 무의미해질 수 있다.
- class mix 변화와 촬영 조건 변화가 같은 score로 나타날 수 있어 샘플 검토가 필요하다.
- feature histogram 설계와 normalization 기준을 보고서에 남겨야 재현성이 유지된다.

보고서 문장 예시:

```text
HINC_IMAGE_FEATURE로 이미지 feature histogram overlap을 비교한 결과,
current 입력의 normalized complement score가 기준 threshold를 초과했다.
이는 최근 이미지 입력의 시각적 feature 구성이 reference와 덜 겹친다는 drift 후보 신호다.
다만 feature extractor와 전처리 버전이 동일한지 확인하고, 대표 이미지 샘플로 변화 유형을 검토해야 한다.
```

---

## SelectionRule 카탈로그

```text
selectionRule HISTOGRAM_INTERSECTION_NORMALIZED_COMPLEMENT_DEFAULT_USE
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

> Histogram Intersection Normalized Complement 카탈로그는 "이 방법이 무엇인가"가 아니라, "어떤 상황에서 어떤 변종을 선택하고 어떤 주의사항과 함께 설명해야 하는가"를 구조화한다.
