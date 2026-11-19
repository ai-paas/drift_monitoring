# Category 계열 차트 해석 가이드

이 문서는 CHART-CAT chart id의 이미지와 해석 방법을 정리한다.

## CHART-CAT-001: C·D등급 증가와 A등급 감소로 보는 범주 비중 변화

![CHART-CAT-001](../charts/output/CHART-CAT-001.png)

### 차트 목적

`CHART-CAT-001`은 범주형 feature에서 관측 빈도가 기대 빈도와 얼마나 다른지 확인하기 위한 차트다. Chi-square Test와 G-test처럼 범주별 빈도 차이를 검정하는 방법에 적합하다.

### 제목

C·D등급 증가와 A등급 감소로 보는 범주 비중 변화

### 현재 상황 요약

현재 관측 빈도는 기대 빈도보다 `C등급`과 `D등급`에서 많이 나오고, `A등급`, `기타`, `미상`에서는 적게 나온다. `C등급`은 기대 `176`건에서 관측 `225`건으로 `+49`건 증가해 전체 Chi-square 기여도 `13.6`으로 가장 크다. 반대로 `A등급`은 기대 `132`건에서 관측 `101`건으로 `-31`건 줄고, 기여도는 `7.3`이다. Chi-square 통계량 `38.0`, 자유도 `5`, p-value `0.003`, 낮은 기대빈도 `0개`이므로 이 예시는 기대 범주 구성과 현재 관측 구성이 달라진 범주형 drift 후보로 해석한다.

이 차트는 다음 질문에 답한다.

```text
1. 어떤 category가 기대보다 많이 또는 적게 관측됐는가?
2. 전체 검정 통계량에 가장 크게 기여한 category는 무엇인가?
3. 기대 빈도가 낮아 검정 신뢰성에 주의해야 하는 category가 있는가?
```

### 차트 구성

왼쪽 패널은 observed vs expected grouped bar다.

- 파란 막대는 기대 빈도다.
- 붉은 막대는 관측 빈도다.
- 두 막대 차이가 큰 category는 drift 설명 후보가 된다.
- 기대 빈도가 낮은 category는 카이제곱 근사 신뢰성을 별도로 확인해야 한다.

오른쪽 위 패널은 표준화 잔차 heatmap이다.

- 표준화 잔차는 `(관측 - 기대) / sqrt(기대)`로 계산한다.
- 초록색은 기대보다 많이 관측된 category다.
- 노란색은 기대보다 적게 관측된 category다.
- 절댓값이 클수록 해당 category의 차이가 크다.

오른쪽 아래 패널은 Chi-square 기여도다.

- 막대 길이는 `(O - E)^2 / E` 값이다.
- 막대가 큰 category는 전체 검정 통계량을 키운 핵심 후보다.
- 가장 큰 기여 category는 보고서에서 우선 설명한다.

상단 요약 카드에는 다음 값이 표시된다.

- `Chi-square`: 전체 카이제곱 통계량
- `df / p-value`: 자유도와 근사 p-value
- `낮은 기대빈도`: 기대 빈도 5 미만 category 수

### 해석 순서

먼저 p-value와 낮은 기대빈도 수를 확인한다.

```text
p-value가 작고 낮은 기대빈도가 없다
  -> 범주형 빈도 차이 신호를 비교적 안정적으로 볼 수 있다.

p-value가 작지만 낮은 기대빈도가 있다
  -> Fisher exact, category 병합, G-test 등 보완 검토가 필요하다.

p-value가 크다
  -> 전체 빈도 차이에 대한 통계적 근거가 약하다.
```

그 다음 표준화 잔차를 본다. 잔차가 양수인 category는 기대보다 많이 관측됐고, 음수인 category는 기대보다 적게 관측됐다.

마지막으로 Chi-square 기여도를 확인한다. 전체 p-value만으로는 어떤 category가 변화했는지 알 수 없으므로, 기여도 상위 category를 중심으로 원인 후보를 좁힌다.

### Drift 후보 판단 기준

p-value가 작고 표준화 잔차 또는 Chi-square 기여도가 큰 category가 명확하면 category frequency drift 후보로 해석한다. 기대 빈도 5 미만 category가 있으면 근사 검정 신뢰성을 별도로 확인한다.

### 패널별 확인

Observed vs Expected:

- `C등급`은 기대 `176`건보다 관측 `225`건이 많아 `+49`건 차이가 난다.
- `D등급`도 기대 `112`건보다 관측 `139`건이 많아 `+27`건 차이가 난다.
- `A등급`은 기대 `132`건보다 관측 `101`건으로 `-31`건 줄고, `기타`는 `58 -> 39`, `미상`은 `32 -> 22`로 줄어든다.

표준화 잔차:

- `C등급` 잔차는 `+3.7`, `D등급` 잔차는 `+2.6`으로 기대보다 과대 관측된 범주다.
- `A등급` 잔차는 `-2.7`, `기타`는 `-2.5`, `미상`은 `-1.8`로 기대보다 과소 관측된 범주다.
- 잔차의 부호를 함께 보면 현재 분포가 A/기타/미상에서 C/D 쪽으로 이동한 모습인지 확인할 수 있다.

Chi-square 기여:

- 전체 Chi-square 통계량은 `38.0`이고, 가장 큰 기여는 `C등급 13.6`이다.
- 그 다음은 `A등급 7.3`, `D등급 6.5`, `기타 6.2` 순서다.
- 낮은 기대빈도는 `0개`이므로 이 예시에서는 카이제곱 근사 자체에 대한 즉각적인 경고는 없다.

### 이 예시 차트의 해석

이 예시에서는 Chi-square 통계량이 `38.0`, 자유도가 `5`, p-value가 `0.003`으로 표시되어 있다. 낮은 기대빈도 category는 `0개`이므로 카이제곱 근사를 사용하는 데 큰 주의 신호는 없다.

표준화 잔차를 보면 `C등급`과 `D등급`은 기대보다 많이 관측됐고, `A등급`, `기타`, `미상`은 기대보다 적게 관측됐다. Chi-square 기여도에서도 `C등급`이 가장 큰 기여를 한다. 따라서 이 예시는 category mix가 A/기타/미상에서 C/D등급 쪽으로 이동한 범주형 drift 후보로 해석할 수 있다.

보고서 문장 예시는 다음과 같다.

```text
기준 기대 빈도와 현재 관측 빈도를 Chi-square 관점에서 비교한 결과,
Chi-square 통계량은 38.0, 자유도는 5, p-value는 0.003으로 나타났다.
표준화 잔차와 기여도를 보면 C등급과 D등급이 기대보다 많이 관측되었고,
C등급이 전체 통계량에 가장 크게 기여했다.
이는 category mix가 A/기타/미상에서 C/D등급 쪽으로 이동한 범주형 drift 후보로 해석할 수 있다.
```

### 금지해야 할 해석

이 차트만으로 다음을 단정하지 않는다.

```text
금지 1
  - p-value만 보고 어떤 category가 변했는지 단정한다.

금지 2
  - 기대 빈도가 낮은 category가 있는데도 카이제곱 근사를 그대로 신뢰한다.

금지 3
  - category 빈도 변화가 곧바로 모델 성능 저하를 의미한다고 말한다.

금지 4
  - category 정의 또는 mapping 변경 가능성을 확인하지 않고 population 변화로 단정한다.
```

범주형 검정은 category 설계, rare category 처리, unknown mapping, category 병합 방식에 민감하다.

### 추가 확인 항목

범주형 빈도 차이가 보이면 다음을 추가 확인한다.

- category 정의, mapping, unknown 처리 변경 여부
- 기대 빈도 5 미만 category 유무
- rare category 병합 또는 Fisher exact test 필요 여부
- 같은 feature의 PSI, Total Variation, JS Distance 결과
- 변화 category의 segment, source, 시간대 구성
- label 확보 후 성능 지표, calibration, error rate 변화

### 적합한 사용 대상

이 chart는 다음 method variant에 적합하다.

- `Chi-square Test / CHI_SQUARE_GOODNESS_OF_FIT`
- `Chi-square Test / CHI_SQUARE_HOMOGENEITY`
- `Chi-square Test / CHI_SQUARE_WITH_LOW_EXPECTED_COUNT_CAUTION`
- `G-test / LIKELIHOOD_RATIO_G_TEST_GOF`
- `G-test / LIKELIHOOD_RATIO_G_TEST_INDEPENDENCE`
- `G-test / G_TEST_WITH_SMALL_COUNT_CAUTION`

## CHART-CAT-002: 검색 감소와 구매 증가의 범주 비중 이동

![CHART-CAT-002](../charts/output/CHART-CAT-002.png)

### 차트 목적

`CHART-CAT-002`는 category별 확률 질량이 기준 구간에서 현재 구간으로 얼마나 이동했는지 확인하기 위한 차트다. 이 예시는 검색 비율이 줄고 구매 비율이 늘어난 상황에서 Total Variation Distance가 관리 기준선에 닿아 있는지 설명한다.

### 제목

검색 감소와 구매 증가의 범주 비중 이동

### 현재 상황 요약

이 예시에서는 Total Variation이 `0.150`, 총 절대 이동이 `0.300`으로 표시된다. 기준 대비 현재 구간에서 `검색`은 `0.26`에서 `0.18`로 `0.08` 감소했고, `구매`는 `0.16`에서 `0.24`로 `0.08` 증가했다. 추세 패널의 TV는 window 1의 `0.07`에서 window 6의 `0.16`까지 상승한 뒤 현재 window 7에서 `0.15`로 관리 기준선에 걸쳐 있으므로, 탐색 단계에서 구매 단계로 probability mass가 이동한 category mix drift 후보로 읽는다.

이 차트는 다음 질문에 답한다.

```text
1. 기준 category 비율과 현재 category 비율이 얼마나 달라졌는가?
2. 어떤 category가 probability mass 이동을 가장 크게 만들었는가?
3. Total Variation이 시간에 따라 증가하고 있는가?
```

### 패널별 확인

왼쪽 패널은 category 비율 비교다.

- 파란 막대는 기준 구간, 붉은 막대는 현재 구간의 category 비율이다.
- `검색`은 `0.26 -> 0.18`로 줄고 `구매`는 `0.16 -> 0.24`로 늘어 가장 뚜렷한 반대 방향 이동을 만든다.
- `장바구니`는 `0.14 -> 0.18`, `환불`은 `0.05 -> 0.08`로 늘고, `문의`는 `0.12 -> 0.08`로 줄어 보조적인 이동을 만든다.

오른쪽 위 패널은 절대 delta 순위다.

- 막대 길이는 `|현재 비율 - 기준 비율|`이고, 괄호 안 값은 signed delta다.
- 절대 변화량은 `검색 0.08 (-0.08)`과 `구매 0.08 (+0.08)`이 가장 크다.
- 그 다음은 `문의 0.04 (-0.04)`, `장바구니 0.04 (+0.04)`, `환불 0.03 (+0.03)` 순서라서 TV 0.150의 핵심 원인은 검색 감소와 구매 증가다.

오른쪽 아래 패널은 Total Variation 추세다.

- y축은 Total Variation Distance이며, 노란 점선은 관리 기준 `0.15`다.
- window별 값은 `0.07, 0.08, 0.10, 0.12, 0.14, 0.16, 0.15`로 상승한 뒤 현재 기준선에 닿아 있다.
- 직전 window의 `0.16`은 기준을 넘었고 현재 `0.15`도 낮은 신호가 아니므로, 단일 spike인지 반복되는 category mix 변화인지 추가 window로 확인해야 한다.

상단 요약 카드에는 다음 값이 표시된다.

- `Total Variation`: `0.150`
- `총 절대 이동`: `0.300`
- `최대 Delta`: `검색 -0.08`

### 해석 순서

먼저 Total Variation 값을 본다.

```text
Total Variation이 0에 가깝다
  -> 기준/현재 category 분포가 유사하다.

Total Variation이 커진다
  -> category 간 probability mass 이동이 커진다.

추세가 threshold 근처에서 상승한다
  -> 최근 window에서 category mix 변화가 강화되고 있다.
```

그 다음 절대 delta 순위를 확인한다. Total Variation은 전체 이동량을 요약하지만, 실제 설명은 어떤 category가 늘고 줄었는지로 해야 한다.

마지막으로 왼쪽 category 비율 비교에서 기준과 현재의 실제 비율 수준을 확인한다. 작은 category의 상대 변화와 큰 category의 절대 변화는 운영 영향이 다를 수 있다.

이 차트에서는 다음 조건이 함께 나타날 때 category mix drift 후보로 해석한다.

```text
1. Total Variation이 관리 기준을 넘거나 최근 window에서 상승 추세를 보인다.
2. 절대 delta 상위 category가 sample size가 충분하고 업무적으로 의미 있는 항목이다.
3. category 정의, tracking, mapping 변경으로 설명되지 않는다.
```

반대로 Total Variation이 작고 delta가 여러 category에 작게 분산되어 있으면 drift 신호는 약한 것으로 본다.

### Drift 후보 판단 기준

Total Variation이 관리 기준을 넘거나 최근 window에서 상승 추세를 보이고, 절대 delta 상위 category가 sample size가 충분하며 업무적으로 의미 있는 항목이면 category mix drift 후보로 해석한다. category 정의, tracking, mapping 변경으로 설명되는 경우는 drift 후보에서 제외한다.

### 이 예시 차트의 해석

이 예시에서는 Total Variation이 `0.150`, 총 절대 이동이 `0.300`, 최대 delta가 `검색 -0.08`로 표시되어 있다. 기준 대비 현재 구간에서 `검색` 비율은 감소했고, `구매` 비율은 증가했다.

추세 패널에서는 Total Variation이 최근 window에서 관리 기준 근처까지 상승했다가 현재 window에서 소폭 낮아진다. 따라서 이 예시는 탐색 category에서 구매 category 쪽으로 probability mass가 이동한 범주형 분포 변화 후보로 해석할 수 있다.

보고서 문장 예시는 다음과 같다.

```text
기준 구간과 현재 구간의 category 비율을 Total Variation 관점에서 비교한 결과,
Total Variation은 0.150, 총 절대 이동은 0.300으로 나타났다.
가장 큰 변화는 검색 category의 0.08 감소이며,
구매 category는 0.08 증가했다.
이는 category probability mass가 탐색 단계에서 구매 단계 쪽으로 이동한 후보로 해석할 수 있다.
```

### 금지해야 할 해석

이 차트만으로 다음을 단정하지 않는다.

```text
금지 1
  - Total Variation 값만 보고 어떤 category가 변했는지 단정한다.

금지 2
  - category mix 변화가 곧바로 모델 성능 저하를 의미한다고 말한다.

금지 3
  - category 정의 또는 tracking 변경 가능성을 확인하지 않고 사용자 행동 변화로 단정한다.

금지 4
  - 단일 window의 일시적 이동을 장기 drift로 확정한다.
```

Total Variation은 직관적인 probability mass 이동 지표지만, 원인 분석에는 category mapping, source 구성, segment 변화를 함께 확인해야 한다.

### 추가 확인 항목

Total Variation이 커지면 다음을 추가 확인한다.

- category 정의, mapping, event tracking 변경 여부
- delta가 큰 category의 sample count와 segment 구성
- 같은 feature의 PSI, JS Distance, Chi-square 결과
- Total Variation 추세가 반복되는지 또는 일시적 spike인지
- 이동 category가 모델 입력 또는 score 분포에 미친 영향
- label 확보 후 성능 지표, calibration, error rate 변화

### 적합한 사용 대상

이 chart는 다음 method variant에 적합하다.

- `Total Variation Distance / CATEGORICAL_TOTAL_VARIATION`
- `Total Variation Distance / HISTOGRAM_TOTAL_VARIATION`
- `Total Variation Distance / PROBABILITY_VECTOR_TOTAL_VARIATION`

## CHART-CAT-003: 검색 감소가 만든 L-infinity 범주 변화 신호

![CHART-CAT-003](../charts/output/CHART-CAT-003.png)

### 제목

검색 감소가 만든 L-infinity 범주 변화 신호

### 현재 상황 요약

이 예시에서는 L-infinity가 `0.120`으로 표시되며, 최대 변화 category는 `검색`이다. 검색 비율은 기준 구간 `0.28`에서 현재 구간 `0.16`으로 `-0.12` 감소했다. 구매는 `0.15`에서 `0.23`으로 `+0.08` 증가하지만, L-infinity 관점의 대표 신호는 절대 변화가 가장 큰 검색 감소다.

우측 하단 추세에서는 window별 L-infinity가 `0.05 -> 0.06 -> 0.07 -> 0.08 -> 0.09 -> 0.11 -> 0.12`로 상승하고, 최근 두 window가 관리 기준 `0.10`을 넘는다. 따라서 이 차트는 전체 category mix가 고르게 흔들린 사례라기보다 검색 category 감소에 집중된 drift 후보를 보여준다.

### 차트 목적

이 chart는 기준 구간과 현재 구간의 category 비율 차이 중 가장 큰 단일 변화량을 L-infinity distance로 보여준다.

Total Variation이 전체 probability mass 이동량을 요약한다면, L-infinity는 “가장 크게 바뀐 category가 무엇인가”를 강조한다. 따라서 전체 분포 변화보다 특정 category의 급격한 증가 또는 감소가 운영적으로 중요한 경우에 적합하다.

### 패널별 확인

이 chart는 세 영역에서 같은 결론을 교차 확인한다.

```text
좌측
  - 기준 구간과 현재 구간의 category 비율 grouped bar를 비교한다.
  - 검색은 0.28에서 0.16으로 낮아지고, 구매는 0.15에서 0.23으로 높아진다.
  - 배경 강조는 절대 delta가 가장 큰 검색 category를 가리킨다.

우측 상단
  - category별 |현재 비율 - 기준 비율| 순위를 확인한다.
  - 검색의 |delta|가 0.12로 1위이며 signed delta는 -0.12다.
  - 구매의 |delta|는 0.08로 뒤따르지만 최대 변화 category는 아니다.

우측 하단
  - window별 L-infinity distance 추세를 확인한다.
  - 값이 0.05에서 0.12까지 올라가고, 0.11과 0.12 구간이 관리 기준 0.10 위에 있다.
```

상단 요약 영역에는 현재 window의 L-infinity 값, 최대 변화 category, 변화 방향을 표시한다.

### 해석 순서

먼저 상단 요약의 L-infinity 값을 확인한다.

```text
L-infinity가 크다
  -> 적어도 하나의 category 비율이 기준 대비 크게 달라졌다.

L-infinity가 작다
  -> 단일 category의 최대 변화는 제한적이다.
```

그 다음 최대 category delta bar에서 어떤 category가 가장 크게 변했는지와 증가/감소 방향을 확인한다.

마지막으로 좌측 비율 비교에서 해당 category의 기준 비율과 현재 비율의 실제 수준을 확인한다. 낮은 빈도의 category는 작은 표본 흔들림으로 큰 상대 변화처럼 보일 수 있으므로 sample count 확인이 필요하다.

### Drift 후보 판단 기준

최대 category delta 또는 L-infinity 값이 관리 기준을 넘거나 최근 window에서 상승 추세를 보이고, 해당 category가 충분한 sample size와 업무적 의미를 가지면 단일 category 집중 drift 후보로 해석한다. 반대로 최대 변화 category가 희소 category이거나 category 정의, logging, mapping 변경으로 설명되면 drift 후보로 확정하지 않는다.

### 이 예시 차트의 해석

이 예시에서는 L-infinity가 `0.120`, 최대 변화 category가 `검색`, 변화 방향이 `감소 -0.12`로 표시되어 있다. 기준 구간에서 `검색` category 비율은 `0.28`이었지만 현재 구간에서는 `0.16`으로 낮아졌다.

추세 패널에서는 L-infinity가 최근 window에서 점진적으로 상승하여 관리 기준 `0.10`을 넘는 형태를 보인다. 따라서 이 예시는 전체 category mix 변화 중에서도 `검색` category 감소가 핵심인 단일 category 집중 drift 후보로 해석할 수 있다.

보고서 문장 예시는 다음과 같다.

```text
기준 구간과 현재 구간의 category 비율을 L-infinity 관점에서 비교한 결과,
가장 큰 단일 변화는 검색 category에서 관측되었고 delta는 -0.12였다.
현재 window의 L-infinity 값은 0.120으로 관리 기준을 초과했으며,
최근 window에서도 상승 추세가 이어졌다.
이는 검색 category 유입 감소에 집중된 category drift 후보로 해석할 수 있다.
```

### 금지해야 할 해석

이 차트만으로 다음을 단정하지 않는다.

```text
금지 1
  - 최대 category 하나만 보고 전체 분포가 크게 바뀌었다고 단정한다.

금지 2
  - 희소 category의 큰 delta를 sample count 확인 없이 drift로 확정한다.

금지 3
  - category mapping 또는 event logging 변경 가능성을 배제하지 않고 사용자 행동 변화로 단정한다.

금지 4
  - L-infinity 값이 작다는 이유만으로 여러 category에 분산된 작은 변화가 없다고 말한다.
```

L-infinity는 단일 최대 변화를 잘 보여주지만, 여러 category에 고르게 분산된 변화는 Total Variation, JS Distance, PSI 같은 보완 chart로 함께 확인해야 한다.

### 추가 확인 항목

L-infinity가 커지면 다음을 추가 확인한다.

- 최대 변화 category의 sample count와 결측/unknown 비율
- category 정의, mapping, event tracking 변경 여부
- 해당 category가 특정 segment, channel, region에 집중되는지 여부
- Total Variation, PSI, JS Distance에서 같은 방향의 변화가 나타나는지 여부
- 모델 score, calibration, error rate에 미친 영향
- label 확보 후 category별 성능 지표 변화

### 적합한 사용 대상

이 chart는 다음 method variant에 적합하다.

- `L-Infinity Distance / CATEGORICAL_L_INFINITY`
- `L-Infinity Distance / PROBABILITY_VECTOR_L_INFINITY`
- `L-Infinity Distance / BINNED_NUMERIC_L_INFINITY`

## CHART-CAT-004: Fisher 검정으로 본 event 비율 상승

![CHART-CAT-004](../charts/output/CHART-CAT-004.png)

### 제목

Fisher 검정으로 본 event 비율 상승

### 차트 목적

이 chart는 작은 표본의 2x2 contingency table에서 기준 구간과 현재 구간의 event 비율 차이가 우연으로 보기 어려운지 보여준다.

Fisher exact test는 표본 수가 작거나 일부 cell count가 낮아 Chi-square 근사가 불안정할 때 유용하다. 따라서 이 chart는 p-value, 실제 event rate 차이, odds ratio와 신뢰구간을 함께 보여주어 작은 표본 category drift를 해석하게 한다.

### 현재 상황 요약

이 예시에서는 기준 구간의 event가 `6/42(14.3%)`이고 현재 구간의 event가 `14/38(36.8%)`이다. 현재 event rate는 기준보다 `+22.6pp` 높으며, Fisher two-sided p-value는 `0.018`, one-sided p-value는 `0.009`로 표시된다. Odds ratio는 `3.50`이고 95% 신뢰구간 `[1.18, 10.4]`가 null 기준 `1`을 벗어나므로, 작은 표본에서도 현재 구간 event 비율 상승이 우연만으로 설명되기 어려운 category drift 후보로 읽는다.

### 차트 구성

이 chart는 세 영역으로 구성된다.

```text
좌측
  - 기준 구간과 현재 구간의 2x2 contingency mosaic
  - event와 non-event count 및 비율

우측 상단
  - 기준/현재 event rate bar
  - event count와 전체 표본 수

우측 하단
  - odds ratio forest plot
  - 95% confidence interval과 null OR=1 기준선
```

상단 요약 영역에는 Fisher p-value, odds ratio, event rate 변화 폭을 표시한다.

### 패널별 확인

좌측 mosaic 패널에서는 기준 구간 `n=42` 중 event `6건`, non-event `36건`이고, 현재 구간 `n=38` 중 event `14건`, non-event `24건`임을 먼저 확인한다. 현재 행에는 붉은 외곽선이 있어 비교 대상이 현재 구간임을 표시하며, event 면적이 기준보다 크게 넓어져 event 비율이 `14.3%`에서 `36.8%`로 오른 상황을 보여준다.

우측 상단 event 비율 패널은 같은 변화를 막대 높이로 압축해 보여준다. 기준은 `6/42`, 현재는 `14/38`이며 현재 event rate가 기준보다 `+22.6pp` 높아, mosaic에서 보인 event 증가가 비율 기준으로도 작지 않다는 점을 확인한다.

우측 하단 odds ratio 패널은 효과 방향과 불확실성을 함께 확인하는 영역이다. Odds ratio `3.50`은 현재 구간의 event odds가 기준보다 높다는 뜻이고, 95% 신뢰구간 `[1.18, 10.4]` 전체가 null 기준 `1` 오른쪽에 있어 이 예시에서는 증가 방향의 신호가 유지된다.

### 해석 순서

먼저 Fisher p-value가 관리 기준보다 작은지 확인한다.

```text
p-value가 작다
  -> 2x2 contingency 차이가 우연으로 보기 어려운 후보다.

p-value가 크다
  -> 작은 표본 안에서 event/non-event 구성 차이가 충분히 강하지 않다.
```

그 다음 odds ratio forest plot에서 효과 방향과 신뢰구간을 확인한다. Odds ratio가 1보다 크면 현재 구간의 event odds가 기준보다 높고, 1보다 작으면 낮다.

마지막으로 event 비율 비교와 mosaic에서 실제 count를 확인한다. Fisher exact 결과는 작은 표본에서 유용하지만, 표본 정의나 event 집계가 바뀌면 통계적으로 유의해도 drift로 해석할 수 없다.

### Drift 후보 판단 기준

Fisher p-value가 관리 기준보다 작고, odds ratio 신뢰구간이 null 기준인 1을 벗어나며, event rate 차이가 업무적으로 의미 있는 크기이면 작은 표본 category drift 후보로 해석한다. 단, 2x2 table의 표본 정의, event 집계 기준, category mapping이 동일하다는 전제가 확인되어야 한다.

One-sided Fisher exact 변종에서는 사전에 정한 증가 또는 감소 방향과 실제 변화 방향이 일치할 때만 방향성 drift 후보로 해석한다.

### 이 예시 차트의 해석

이 예시에서는 Fisher p-value가 `0.018`, odds ratio가 `3.50`, event rate 변화가 `+22.6pp`로 표시되어 있다. 기준 구간의 event rate는 `6/42 = 14.3%`, 현재 구간의 event rate는 `14/38 = 36.8%`다.

Odds ratio의 95% 신뢰구간은 `[1.18, 10.4]`로 null 기준인 `1`을 벗어난다. 따라서 이 예시는 작은 표본 조건에서도 현재 구간의 event 비율 증가가 우연만으로 설명되기 어려운 2x2 category drift 후보로 해석할 수 있다.

보고서 문장 예시는 다음과 같다.

```text
2x2 contingency table에 Fisher exact test를 적용한 결과,
기준 구간 event rate는 14.3%, 현재 구간 event rate는 36.8%였다.
two-sided p-value는 0.018이고 odds ratio는 3.50이었다.
95% 신뢰구간이 1을 벗어나므로,
현재 구간의 event 비율 증가를 작은 표본 category drift 후보로 해석할 수 있다.
```

### 금지해야 할 해석

이 차트만으로 다음을 단정하지 않는다.

```text
금지 1
  - p-value만 보고 효과 크기가 충분히 크다고 단정한다.

금지 2
  - 표본 정의나 event 집계 기준 변경을 확인하지 않고 drift로 확정한다.

금지 3
  - one-sided test에서 사전 방향 설정 없이 사후에 유리한 방향만 선택한다.

금지 4
  - 매우 작은 cell count의 결과를 장기 추세로 일반화한다.
```

Fisher exact 계열은 작은 표본 조건에 강하지만, 결과 해석은 count, 비율 차이, odds ratio, 업무적 의미를 함께 확인해야 한다.

### 추가 확인 항목

Fisher exact 결과가 유의하면 다음을 추가 확인한다.

- 2x2 table의 표본 정의와 event 집계 기준 일관성
- cell count가 지나치게 작아 단일 건의 영향이 과도하지 않은지 여부
- one-sided 변종의 경우 사전 방향 가설과 실제 변화 방향
- 같은 category의 Total Variation, PSI, L-infinity 결과
- segment, channel, region별로 같은 변화가 반복되는지 여부
- label 확보 후 해당 category의 성능 지표와 error rate 변화

### 적합한 사용 대상

이 chart는 다음 method variant에 적합하다.

- `Fisher's Exact Test / TWO_BY_TWO_FISHER_EXACT`
- `Fisher's Exact Test / ONE_SIDED_FISHER_EXACT`
- `Fisher's Exact Test / EXTENDED_CONTINGENCY_EXACT_TEST`


