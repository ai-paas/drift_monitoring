# KS_TEST 알고리즘 변종 목록

## 1. 목적

이 문서는 `KS_TEST`를 하나의 고정된 알고리즘으로 보지 않고, drift monitoring에서 상황에 따라 선택해야 하는 **알고리즘 변종들의 family**로 정리한다.

핵심 목적은 다음이다.

```text
상황 조건 → 적절한 KS 계열 변종 → 출력 metric → 주의사항 → LLM 보고서 설명
```

즉 LLM이 단순히 “KS test를 쓰라”고 말하는 것이 아니라,

```text
이 상황이면 two-sample two-sided KS를 쓰고,
이 상황이면 one-sided KS를 쓰며,
이 상황이면 exact p-value를 쓰고,
ties/discrete data가 많으면 classical KS p-value 해석을 조심하라.
```

처럼 추천할 수 있게 만드는 것이 목표다.

---

## 2. KS_TEST의 위치

```text
methodFamily EDF_BASED_DISTRIBUTION_TEST
  └─ methodFamily KS_TEST
       ├─ algorithmVariant ONE_SAMPLE_KS_KNOWN_CDF
       ├─ algorithmVariant TWO_SAMPLE_KS_TWO_SIDED
       ├─ algorithmVariant TWO_SAMPLE_KS_ONE_SIDED_GREATER
       ├─ algorithmVariant TWO_SAMPLE_KS_ONE_SIDED_LESS
       ├─ algorithmVariant TWO_SAMPLE_KS_EXACT_PVALUE
       ├─ algorithmVariant TWO_SAMPLE_KS_ASYMPTOTIC_PVALUE
       ├─ algorithmVariant KS_WITH_TIES_OR_DISCRETE_CAUTION
       ├─ algorithmVariant LILLIEFORS_RELATED_ONE_SAMPLE
       ├─ algorithmVariant HIGHER_ORDER_KS
       └─ algorithmVariant TWO_SAMPLE_KS_APPROX_QUANTILE
```

`KS_TEST`는 경험분포함수, EDF, 기반 검정 계열에 속한다. 일반적으로 경험 CDF 사이의 최대 차이를 사용해 분포 차이를 측정한다.

---

## 3. 공통 개념

```text
methodFamily KS_TEST
  belongsTo -> EDF_BASED_DISTRIBUTION_TEST

  purpose ->
    경험분포함수 사이의 최대 차이를 이용해 분포 차이를 측정한다.

  strengths ->
    비모수적이다.
    단변량 연속형 feature의 reference/current 분포 비교에 단순하고 강력하다.
    결과 해석이 비교적 쉽다.

  weaknesses ->
    discrete data 또는 ties가 많은 데이터에서는 p-value 해석이 약해질 수 있다.
    tail 차이에 특별히 민감한 검정은 아니다.
    다변량 분포 변화에는 직접 적합하지 않다.
    sample size가 크면 작은 차이도 통계적으로 유의하게 나올 수 있다.

  commonOutputs ->
    KS_STATISTIC
    P_VALUE
```

---

## 4. 변종 1: ONE_SAMPLE_KS_KNOWN_CDF

`ONE_SAMPLE_KS_KNOWN_CDF`는 하나의 sample 경험분포를 사전에 완전히 지정된 이론 CDF와 비교하는 one-sample KS 변종이다. drift monitoring에서는 특정 feature가 운영상 기대한 기준 분포를 계속 따르는지 점검할 때 사용한다. 출력은 KS statistic, p-value, alarm state로 해석한다.

사용 상황:
- 기준 분포의 CDF와 파라미터가 사전에 고정되어 있을 때
- feature 값이 정규분포, 지수분포, 사전 정의된 정책 분포를 따르는지 확인할 때
- reference sample이 아니라 이론적 baseline과 current sample을 비교해야 할 때

해석 방법:
- KS statistic은 sample 경험 CDF와 기준 CDF 사이의 최대 차이다.
- p-value가 작으면 sample이 지정된 CDF를 따른다는 가설을 기각할 근거가 강하다.
- alarm은 이론 기준 분포와의 차이 후보이며, 어떤 구간에서 차이가 큰지는 CDF 차이 위치로 확인한다.
- 보고서에는 기준 CDF와 파라미터가 어떻게 정해졌는지 함께 적는다.

주의점:
- 기준 분포의 파라미터를 같은 sample에서 추정했다면 일반 one-sample KS p-value를 그대로 쓰면 안 된다.
- discrete 값이나 ties가 많으면 p-value 해석이 약해질 수 있다.
- drift 판단은 지정된 이론 분포와의 차이에 한정하고 reference/current 변화로 확대 해석하지 않는다.

보고서 문장 예시:

```text
ONE_SAMPLE_KS_KNOWN_CDF로 current sample의 경험분포를 사전 지정 CDF와 비교한 결과,
KS statistic과 p-value가 기준 분포와의 차이 후보를 보였다.
이는 현재 sample이 운영상 기대한 이론 분포에서 벗어났을 가능성을 나타낸다.
다만 기준 CDF의 파라미터가 사전에 고정되어 있었는지 확인해야 한다.
```

---

## 5. 변종 2: TWO_SAMPLE_KS_TWO_SIDED

`TWO_SAMPLE_KS_TWO_SIDED`는 reference sample과 current sample의 경험 CDF 사이 최대 차이를 양방향으로 평가하는 기본 KS drift 변종이다. 변화 방향을 미리 정하지 않고 단변량 연속형 feature의 분포가 달라졌는지 확인할 때 사용한다. 출력은 KS statistic, p-value, 최대 차이 위치, alarm state로 해석한다.

사용 상황:
- reference/current window가 있고 단변량 연속형 feature 분포를 비교할 때
- 값이 증가했는지 감소했는지보다 전체 분포 변화 여부가 중요한 경우
- feature drift monitoring의 기본 screening 지표가 필요할 때

해석 방법:
- KS statistic이 클수록 두 경험 CDF의 최대 차이가 크다.
- p-value가 작으면 reference/current가 같은 분포에서 왔다는 가설을 기각할 근거가 강하다.
- 최대 차이 위치를 보면 어느 값 구간에서 두 CDF가 가장 벌어졌는지 알 수 있다.
- alarm은 분포 변화 후보이며, 이동 방향과 업무 영향은 CDF/분포 차트로 보완한다.

주의점:
- KS는 분포 차이를 알려주지만 평균 증가/감소 방향을 직접 요약하지 않는다.
- sample size가 크면 작은 차이도 유의하게 나올 수 있어 효과 크기를 함께 봐야 한다.
- categorical/discrete feature나 ties가 많은 feature에서는 p-value 해석에 주의한다.

보고서 문장 예시:

```text
TWO_SAMPLE_KS_TWO_SIDED로 reference/current window를 비교한 결과,
두 경험분포함수 사이 최대 차이가 기준을 초과했다.
이는 current 기간의 단변량 feature 분포가 기준 기간과 달라졌을 가능성을 나타낸다.
다만 변화 방향은 KS statistic만으로 단정하지 않고 CDF 차이 위치와 분포 차트를 함께 확인해야 한다.
```

LLM 추천 예시:

```text
연속형 단변량 feature이고 reference/current window가 있으며 변화 방향을 모르는 경우, TWO_SAMPLE_KS_TWO_SIDED를 기본 선택으로 추천한다.
```

---

## 6. 변종 3: TWO_SAMPLE_KS_ONE_SIDED_GREATER

`TWO_SAMPLE_KS_ONE_SIDED_GREATER`는 reference/current 경험 CDF 차이를 `alternative = greater` 방향으로만 평가하는 one-sided KS 변종이다. 변화 방향에 대한 사전 가설이 있을 때 양방향 검정보다 초점을 좁혀 감시한다. 출력은 one-sided KS statistic, p-value, alarm state로 해석한다.

사용 상황:
- 분포 변화 방향을 사전에 정했고 그 방향만 검정하고 싶을 때
- 운영상 특정 방향 변화가 위험 신호로 정의되어 있을 때
- two-sided 결과보다 방향성 가설에 맞춘 p-value가 필요한 경우

해석 방법:
- p-value가 작으면 사전에 정한 `greater` CDF 방향의 차이가 우연으로 보기 어렵다는 근거가 강하다.
- `greater`는 CDF 기준 방향이므로 feature 값의 직관적 증가/감소와 반드시 일치하지 않는다.
- alarm은 방향성 분포 차이 후보이며, 값의 변화 방향은 CDF와 quantile 차이로 확인한다.
- 보고서에는 `alternative = greater`를 사용한 이유를 명시한다.

주의점:
- 데이터를 본 뒤 방향을 정하면 p-value 해석이 왜곡된다.
- CDF 방향과 값 크기 방향을 혼동하면 보고서 해석이 반대로 될 수 있다.
- 반대 방향 변화는 이 변종의 주 검정 대상이 아니다.

보고서 문장 예시:

```text
TWO_SAMPLE_KS_ONE_SIDED_GREATER로 사전 정의한 방향의 CDF 차이를 검정한 결과,
one-sided p-value가 기준을 통과했다.
이는 current 분포가 지정한 CDF 방향으로 reference와 달라졌을 가능성을 나타낸다.
다만 greater는 CDF 기준 방향이므로, 값의 증가/감소 해석은 quantile 차이와 함께 확인해야 한다.
```

---

## 7. 변종 4: TWO_SAMPLE_KS_ONE_SIDED_LESS

`TWO_SAMPLE_KS_ONE_SIDED_LESS`는 reference/current 경험 CDF 차이를 `alternative = less` 방향으로만 평가하는 one-sided KS 변종이다. `greater`와 반대 방향의 사전 가설이 있을 때 사용한다. 출력은 one-sided KS statistic, p-value, alarm state로 해석한다.

사용 상황:
- 사전에 `less` 방향의 CDF 차이가 운영상 관심 방향으로 정의되어 있을 때
- 특정 feature 분포가 한쪽 방향으로 이동하는지만 검정하고 싶을 때
- 방향성 drift rule을 명확히 문서화해 운영 alarm과 연결해야 할 때

해석 방법:
- p-value가 작으면 `less` 방향의 CDF 차이가 통계적으로 보기 어려운 수준이라는 뜻이다.
- `less` 역시 CDF 기준 방향이므로 값 크기 증가/감소와 별도로 해석한다.
- alarm은 지정 방향의 분포 차이 후보이며, 실제 값 구간 변화는 CDF 차트로 설명한다.
- 보고서에는 방향을 사전에 정했다는 점과 CDF 기준 의미를 적는다.

주의점:
- 반대 방향 차이가 커도 이 one-sided 검정에서는 중심 신호가 아닐 수 있다.
- CDF 방향 설명 없이 "값이 감소했다"처럼 단정하면 오해가 생길 수 있다.
- 방향 선택 근거가 없으면 two-sided KS를 우선 고려한다.

보고서 문장 예시:

```text
TWO_SAMPLE_KS_ONE_SIDED_LESS로 지정 방향의 분포 차이를 검정한 결과,
one-sided KS p-value가 기준보다 낮았다.
이는 current 분포가 사전에 정의한 less CDF 방향으로 reference와 달라졌을 가능성을 나타낸다.
다만 less의 의미는 CDF 기준이므로, 값의 실제 이동 방향은 CDF와 quantile 비교로 설명해야 한다.
```

---

## 8. 변종 5: TWO_SAMPLE_KS_EXACT_PVALUE

`TWO_SAMPLE_KS_EXACT_PVALUE`는 two-sample KS statistic에 대해 exact p-value 계산 방식을 사용하는 변종이다. 표본 수가 작거나 중간 정도이고 p-value가 보고서 판단이나 audit에 직접 쓰일 때 적합하다. 출력은 KS statistic, exact p-value, alarm state로 해석한다.

사용 상황:
- current window가 작아 asymptotic 근사 p-value가 불안정할 수 있을 때
- p-value 자체가 의사결정 기준에 직접 들어가는 audit 가능한 보고서에서
- 계산 비용보다 p-value 정확성이 더 중요한 batch 분석에서

해석 방법:
- KS statistic은 두 경험 CDF의 최대 차이를 나타내고, exact p-value는 해당 표본 크기에서 그 차이가 얼마나 드문지 평가한다.
- exact p-value가 작으면 reference/current 분포 차이 후보로 본다.
- asymptotic 방식과 결과가 다를 수 있으므로 사용한 p-value 방법을 보고서에 적는다.
- alarm은 exact p-value 기준을 통과한 분포 차이 후보이다.

주의점:
- 표본이 매우 크면 exact 계산 비용이나 수치 안정성이 문제가 될 수 있다.
- ties가 많거나 discrete 값이면 exact p-value라도 classical KS 해석이 약해질 수 있다.
- 구현 라이브러리마다 exact 계산 기준이 다를 수 있어 버전 기록이 필요하다.

보고서 문장 예시:

```text
TWO_SAMPLE_KS_EXACT_PVALUE로 reference/current 분포를 비교한 결과,
exact p-value가 기준보다 낮아 분포 차이 후보가 관측됐다.
이는 작은 또는 중간 표본 조건에서 asymptotic 근사 대신 exact 방식을 적용한 결과다.
다만 ties가 많은 데이터에서는 exact p-value 해석도 주의해야 한다.
```

---

## 9. 변종 6: TWO_SAMPLE_KS_ASYMPTOTIC_PVALUE

`TWO_SAMPLE_KS_ASYMPTOTIC_PVALUE`는 표본 수가 충분히 크다고 보고 KS statistic의 asymptotic p-value를 사용하는 변종이다. 많은 feature를 반복적으로 빠르게 screening해야 하는 운영 monitoring에 적합하다. 출력은 KS statistic, asymptotic p-value, alarm state로 해석한다.

사용 상황:
- reference/current 표본 수가 충분히 크고 반복 계산 비용을 줄여야 할 때
- 대량 feature drift screening에서 빠른 p-value 계산이 필요한 경우
- 실시간 또는 준실시간 monitoring에서 exact 계산 비용이 부담될 때

해석 방법:
- KS statistic이 클수록 경험 CDF 최대 차이가 크고, asymptotic p-value가 작을수록 차이 근거가 강하다.
- alarm은 asymptotic 근사 기준에서 분포 변화 후보로 감지된 상태다.
- 표본 수가 크면 아주 작은 차이도 유의해질 수 있으므로 statistic 크기와 분포 차트도 함께 본다.
- 보고서에는 exact가 아니라 asymptotic p-value를 사용했다고 명시한다.

주의점:
- 작은 표본에서는 exact 방식과 p-value가 달라질 수 있다.
- p-value가 alert threshold에 직접 쓰이면 계산 방식 변경 시 비교 가능성이 깨진다.
- ties/discrete feature에서는 asymptotic p-value 해석이 더 약해질 수 있다.

보고서 문장 예시:

```text
TWO_SAMPLE_KS_ASYMPTOTIC_PVALUE로 대량 feature screening을 수행한 결과,
해당 feature의 KS statistic과 asymptotic p-value가 drift 후보 기준을 통과했다.
이는 reference/current 경험분포 사이의 최대 차이가 운영 threshold를 넘었다는 뜻이다.
다만 표본 수가 커 작은 차이도 유의해질 수 있으므로 효과 크기와 CDF 차이를 함께 확인해야 한다.
```

---

## 10. 변종 7: KS_WITH_TIES_OR_DISCRETE_CAUTION

`KS_WITH_TIES_OR_DISCRETE_CAUTION`은 동일값, 반올림 값, discrete 값이 많은 feature에 KS statistic을 보조 신호로 쓰되 p-value 해석 주의를 명시하는 변종이다. classical KS test의 연속분포 가정이 약해지는 상황을 문서화하기 위한 안전한 보고 방식이다. 출력은 KS statistic, caution flag, p-value with caution으로 해석한다.

사용 상황:
- 연속형처럼 보이지만 측정 해상도 때문에 동일값이 많은 feature를 감시할 때
- discrete 또는 ordinal 값을 숫자처럼 비교해야 하는 임시 screening에서
- KS statistic은 참고하되 p-value를 강하게 해석하면 안 되는 경우

해석 방법:
- KS statistic은 경험 CDF 최대 차이를 보조적으로 보여준다.
- p-value는 classical KS 가정이 약하므로 확정적 유의성 근거가 아니라 caution과 함께 읽는다.
- alarm이 있으면 permutation, bootstrap, chi-square, discrete distribution test 같은 대안을 검토한다.
- 보고서에는 ties 또는 discrete 특성 때문에 해석 제한이 있음을 반드시 적는다.

주의점:
- categorical feature를 숫자로 인코딩한 뒤 KS p-value를 주 검정처럼 쓰면 오해가 생긴다.
- 동일값이 많으면 KS의 distribution-free p-value 성질이 약해질 수 있다.
- 대체 검정으로 확인하지 않으면 false alarm 또는 missed signal 위험이 남는다.

보고서 문장 예시:

```text
KS_WITH_TIES_OR_DISCRETE_CAUTION으로 해당 feature를 확인한 결과,
KS statistic은 reference/current CDF 차이 후보를 보였지만 동일값이 많아 p-value 해석에는 제한이 있다.
따라서 이 결과는 drift 후보 screening 신호로만 사용하고,
필요 시 permutation 또는 discrete distribution test로 보완 검증해야 한다.
```

---

## 11. 변종 8: LILLIEFORS_RELATED_ONE_SAMPLE

`LILLIEFORS_RELATED_ONE_SAMPLE`은 one-sample KS로 정규분포나 지수분포 적합성을 보려는데 기준 분포의 파라미터를 같은 sample에서 추정한 경우를 위한 관련 변종이다. 일반 one-sample KS p-value가 더 이상 그대로 맞지 않으므로 Lilliefors 계열 보정이나 대체 p-value를 사용한다. 출력은 test statistic, adjusted p-value, assumption check result로 해석한다.

사용 상황:
- sample 평균과 표준편차를 추정한 뒤 정규분포 적합성을 검토할 때
- rate 파라미터를 sample에서 추정한 지수분포 적합성을 확인할 때
- drift detector 적용 전 feature 분포 가정을 점검해야 할 때

해석 방법:
- p-value는 일반 KS가 아니라 파라미터 추정 효과를 반영한 보정 결과로 읽는다.
- p-value가 작으면 추정된 이론 분포로 sample을 설명하기 어렵다는 신호다.
- 이 변종은 reference/current drift 비교가 아니라 one-sample goodness-of-fit 검토에 가깝다.
- 보고서에는 파라미터를 데이터에서 추정했다는 점을 명시한다.

주의점:
- 일반 one-sample KS p-value와 혼용하면 유의성 해석이 틀릴 수 있다.
- reference/current 두 표본 drift 비교가 목적이면 two-sample KS 계열을 사용한다.
- 정규성 검토 결과만으로 데이터 drift나 모델 성능 저하를 확정하지 않는다.

보고서 문장 예시:

```text
LILLIEFORS_RELATED_ONE_SAMPLE로 sample의 분포 적합성을 검토한 결과,
파라미터를 같은 데이터에서 추정했기 때문에 일반 one-sample KS가 아니라 보정된 p-value를 사용했다.
이 결과는 feature가 추정된 기준 분포를 따르는지에 대한 가정 점검 신호다.
reference/current drift 비교 결과로 해석하지 않도록 주의해야 한다.
```

---

## 12. 변종 9: HIGHER_ORDER_KS

`HIGHER_ORDER_KS`는 classical KS가 보는 최대 CDF 차이를 확장해 tail 차이나 고차적 분포 차이에 더 민감하게 반응하도록 설계한 KS 계열 변종이다. 운영상 tail 변화가 중요하거나 classical KS의 민감도 한계를 보완해야 할 때 보조 detector로 사용한다. 출력은 higher-order KS statistic, optional p-value, alarm state로 해석한다.

사용 상황:
- 극단값, tail risk, rare high-value 구간 변화가 중요한 feature를 감시할 때
- classical KS가 충분히 민감하지 않은 분포 차이를 보완하고 싶을 때
- Anderson-Darling 같은 tail-sensitive 검정과 함께 후보 신호를 비교할 때

해석 방법:
- higher-order statistic이 클수록 확장된 기준에서 reference/current CDF 차이가 크다.
- alarm은 classical KS보다 특정 구간 또는 tail 차이에 민감한 drift 후보 신호일 수 있다.
- p-value가 optional이거나 구현별로 다를 수 있어 threshold calibration 근거가 중요하다.
- 보고서에는 classical KS와 다른 확장 변형이라는 점을 명시한다.

주의점:
- classical KS보다 직관적 설명이 어렵고 구현별 정의가 다를 수 있다.
- 운영 threshold를 별도로 calibration하지 않으면 alarm 민감도를 판단하기 어렵다.
- 해석 가능성이 중요한 표준 보고서에서는 classical KS나 Anderson-Darling과 함께 제시하는 편이 안전하다.

보고서 문장 예시:

```text
HIGHER_ORDER_KS로 reference/current 분포를 비교한 결과,
확장 KS statistic이 calibration threshold를 초과했다.
이는 classical KS가 놓칠 수 있는 tail 또는 고차적 분포 차이 후보를 나타낸다.
다만 이 변종은 구현과 threshold 정의에 따라 해석이 달라지므로, classical KS 결과와 함께 보고하는 것이 적절하다.
```

---

## 13. 변종 10: TWO_SAMPLE_KS_APPROX_QUANTILE

`TWO_SAMPLE_KS_APPROX_QUANTILE`은 매우 큰 데이터에서 전체 정렬 기반 KS 계산 비용을 줄이기 위해 approximate quantile 또는 approximate CDF를 사용하는 two-sample KS 변종이다. 분산 처리나 streaming/batch 대량 monitoring에서 빠른 screening용으로 적합하다. 출력은 approximate KS statistic, optional approximate p-value, approximation error bound로 해석한다.

사용 상황:
- Spark, 분산 batch, 대규모 feature store에서 전체 정렬 비용이 큰 경우
- 수많은 feature를 빠르게 screening하고 후보만 후속 정밀 검정하려는 경우
- approximate quantile summary를 이미 운영 지표로 관리하는 환경에서

해석 방법:
- approximate KS statistic은 근사 CDF 사이의 최대 차이를 나타낸다.
- threshold 초과는 대용량 환경에서의 drift 후보 screening 신호로 읽는다.
- exact KS와 다를 수 있으므로 근사 오차 또는 quantile error 설정을 함께 확인한다.
- audit나 최종 판정에는 후보 feature를 exact 계산 또는 더 정밀한 방법으로 재검증할 수 있다.

주의점:
- exact KS가 아니므로 p-value와 statistic이 근사 오차의 영향을 받는다.
- 근사 오차를 허용할 수 없는 규제/audit 보고서에는 단독 사용을 피한다.
- quantile sketch 설정이 바뀌면 이전 score와 비교 가능성이 달라진다.

보고서 문장 예시:

```text
TWO_SAMPLE_KS_APPROX_QUANTILE로 대용량 reference/current 데이터를 screening한 결과,
approximate KS statistic이 기준 threshold를 초과했다.
이는 근사 CDF 기준에서 current 분포가 reference와 달라졌을 가능성을 나타낸다.
다만 approximate quantile 기반 결과이므로, 근사 오차 설정과 필요 시 exact 재검증 결과를 함께 보고해야 한다.
```

---

## 14. KS와 함께 고려할 관련 EDF 계열

다음은 KS의 직접 version이라기보다, 같은 EDF 기반 goodness-of-fit / two-sample test 계열의 대안이다.

```text
methodFamily EDF_BASED_TEST
  variants ->
    KS_TEST
    CRAMER_VON_MISES_TEST
    ANDERSON_DARLING_TEST
    KUIPER_TEST
```

### Anderson-Darling

```text
useWhen ->
  tail 차이가 중요할 때

reason ->
  Anderson-Darling 계열은 tail 영역 차이에 더 민감하게 설계된다.
```

### Cramér-von Mises

```text
useWhen ->
  최대 차이 하나보다 전체 CDF 차이의 누적 정도를 보고 싶을 때
```

### Kuiper test

```text
useWhen ->
  circular data 또는 양쪽 방향 차이를 균형 있게 보고 싶을 때
```

LLM 추천 문장:

```text
KS는 최대 CDF 차이에 민감하지만 tail 차이나 여러 구간에 퍼진 차이가 중요하면 Anderson-Darling 또는 Cramér-von Mises 계열을 함께 검토한다.
```

---

## 15. SelectionRule 카탈로그

### 15.1 기본 feature drift

```text
selectionRule KS_DEFAULT_FEATURE_DRIFT
  if ->
    continuous_feature
    and reference_sample_available
    and current_sample_available
    and direction_unknown

  recommend ->
    TWO_SAMPLE_KS_TWO_SIDED

  because ->
    기준 분포와 현재 분포가 어느 방향으로든 달라졌는지 감지하는 기본 선택이다.

  caveat ->
    ties가 많거나 discrete feature이면 p-value 해석에 주의한다.
```

### 15.2 방향성이 있는 변화

```text
selectionRule KS_DIRECTIONAL_SHIFT
  if ->
    continuous_feature
    and expected_shift_direction_known

  recommend ->
    TWO_SAMPLE_KS_ONE_SIDED_GREATER
    or TWO_SAMPLE_KS_ONE_SIDED_LESS

  because ->
    사전 가설이 있는 방향의 분포 이동을 더 직접적으로 검정할 수 있다.

  caveat ->
    greater/less는 CDF 기준 방향으로 해석해야 한다.
```

### 15.3 작은 표본

```text
selectionRule KS_SMALL_SAMPLE
  if ->
    small_or_medium_sample
    and p_value_is_decision_critical

  recommend ->
    TWO_SAMPLE_KS_EXACT_PVALUE

  because ->
    asymptotic 근사보다 exact p-value가 적절할 수 있다.
```

### 15.4 대량 운영 모니터링

```text
selectionRule KS_LARGE_SCALE_MONITORING
  if ->
    large_sample
    and many_features
    and low_latency_required

  recommend ->
    TWO_SAMPLE_KS_ASYMPTOTIC_PVALUE

  because ->
    계산 비용을 낮추면서 반복 모니터링에 적합하다.
```

### 15.5 매우 큰 데이터 / 분산 처리

```text
selectionRule KS_BIG_DATA_APPROX
  if ->
    very_large_sample
    and distributed_environment

  recommend ->
    TWO_SAMPLE_KS_APPROX_QUANTILE

  because ->
    exact CDF 계산과 전체 정렬 비용을 줄일 수 있다.

  caveat ->
    approximate result이므로 근사 오차를 보고해야 한다.
```

### 15.6 ties 또는 discrete feature

```text
selectionRule KS_DISCRETE_OR_TIES
  if ->
    discrete_feature
    or many_ties

  recommend ->
    KS_WITH_TIES_OR_DISCRETE_CAUTION

  because ->
    classical KS의 연속분포 가정이 약해져 p-value 해석에 주의가 필요하다.

  fallback ->
    CHI_SQUARE_TEST
    DISCRETE_DISTRIBUTION_TEST
    PERMUTATION_TEST
```

### 15.7 tail-sensitive drift

```text
selectionRule KS_TAIL_SENSITIVE_CASE
  if ->
    tail_difference_is_important

  recommend ->
    ANDERSON_DARLING_TEST
    or HIGHER_ORDER_KS

  because ->
    classical KS는 최대 CDF 차이 하나를 보므로 tail 차이에 최적화되어 있지 않을 수 있다.
```

---

## 16. 서비스 구현 버전으로 내려가는 예

논문/알고리즘 변종은 실제 서비스 구현에서 다시 version으로 갈라진다.

```text
serviceMethod KS_FEATURE_DRIFT:v1.0
  implements -> TWO_SAMPLE_KS_TWO_SIDED
  parameters ->
    alternative = two-sided
    pValueMethod = asymptotic
    tiePolicy = warn_only
  outputs ->
    KS_STATISTIC
    P_VALUE

serviceMethod KS_FEATURE_DRIFT:v1.1
  implements -> TWO_SAMPLE_KS_TWO_SIDED
  revises -> KS_FEATURE_DRIFT:v1.0
  parameters ->
    alternative = two-sided
    pValueMethod = exact
    tiePolicy = permutation_fallback
  outputs ->
    KS_STATISTIC
    P_VALUE
    SAMPLE_SIZE_REFERENCE
    SAMPLE_SIZE_CURRENT

  compatibilityWith KS_FEATURE_DRIFT:v1.0 ->
    statisticComparable: True
    pValueComparable: False
    outputSchema: BackwardCompatible
    reason:
      "p-value 계산 방식이 asymptotic에서 exact로 변경되었다."
```

보고서 설명 예:

```text
이번 결과는 KS_FEATURE_DRIFT:v1.1로 계산되었다. 이 버전은 TWO_SAMPLE_KS_TWO_SIDED 알고리즘 변형을 구현하며, v1.0과 달리 p-value 계산에 exact 방식을 사용한다. 따라서 KS_STATISTIC은 v1.0 결과와 비교할 수 있지만, P_VALUE는 계산 방식 차이 때문에 직접 비교하지 않는 것이 좋다.
```

---

## 17. LLM 추천을 위한 최종 구조

KS_TEST에 대해 LLM이 추천을 하려면 단순히 알고리즘 이름만 있으면 안 된다. 다음 구조가 필요하다.

```text
MethodFamily
  KS_TEST

AlgorithmVariant
  TWO_SAMPLE_KS_TWO_SIDED
  TWO_SAMPLE_KS_ONE_SIDED_GREATER
  TWO_SAMPLE_KS_ONE_SIDED_LESS
  TWO_SAMPLE_KS_EXACT_PVALUE
  TWO_SAMPLE_KS_ASYMPTOTIC_PVALUE
  KS_WITH_TIES_OR_DISCRETE_CAUTION
  LILLIEFORS_RELATED_ONE_SAMPLE
  HIGHER_ORDER_KS
  TWO_SAMPLE_KS_APPROX_QUANTILE

SelectionRule
  KS_DEFAULT_FEATURE_DRIFT
  KS_DIRECTIONAL_SHIFT
  KS_SMALL_SAMPLE
  KS_LARGE_SCALE_MONITORING
  KS_BIG_DATA_APPROX
  KS_DISCRETE_OR_TIES
  KS_TAIL_SENSITIVE_CASE

ServiceMethodVersion
  KS_FEATURE_DRIFT:v1.0
  KS_FEATURE_DRIFT:v1.1
```

이 구조가 있으면 LLM은 다음 흐름으로 답할 수 있다.

```text
상황 조건
  → selection rule
  → algorithm variant 추천
  → service method version 확인
  → output metric 설명
  → caveat 설명
  → report guidance 생성
```

---

## 18. 요약

`KS_TEST`는 하나의 고정된 알고리즘으로 두면 안 된다. drift monitoring에서 실용적으로 쓰려면 다음처럼 분해해야 한다.

```text
KS_TEST
  = 경험분포함수 기반 분포 차이 검정 계열

AlgorithmVariant
  = one-sample/two-sample, one-sided/two-sided, exact/asymptotic,
    ties/discrete handling, big-data approximate 등 상황별 변종

ServiceMethodVersion
  = 실제 서비스에서 이 변종을 구현한 버전
```

따라서 LLM 보고서와 추천 시스템을 위해서는 다음 세 가지가 함께 필요하다.

```text
1. 변종 목록
2. 상황별 선택 규칙
3. 서비스 구현 버전과 compatibility 정보
```

한 문장으로 정리하면:

> KS_TEST 카탈로그는 “KS test란 무엇인가”가 아니라, “어떤 상황에서 어떤 KS 계열 변종을 선택하고, 그 결과를 어떤 주의사항과 함께 설명해야 하는가”를 구조화해야 한다.
