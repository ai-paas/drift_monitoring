# Drift Method Variant Chart Guide

이 문서는 drift 측정 method와 algorithm variant별로 어떤 차트를 우선 사용할지 정리한다. 앞 표는 method/variant와 chart id를 연결하고, 뒤쪽 chart catalog는 chart id별 공통 설명을 제공한다.

## 1. Method Variant to Chart ID

| drift 메소드 | chart id | 설명 |
|---|---|---|
| KS Test / ONE_SAMPLE_KS_KNOWN_CDF | CHART-EDF-001 | KS 검정으로 확인하는 현재 분포의 오른쪽 이동. x≈0.74에서 기준 CDF 0.804와 현재 CDF 0.587의 최대 차이 D=0.217이 나타나고 현재 분포가 오른쪽으로 이동하는지 읽는다. |
| KS Test / TWO_SAMPLE_KS_TWO_SIDED | CHART-EDF-001 | KS 검정으로 확인하는 현재 분포의 오른쪽 이동. 두 표본 ECDF의 최대 세로 차이와 히스토그램의 위치 이동이 같은 방향인지 확인한다. |
| KS Test / TWO_SAMPLE_KS_ONE_SIDED_GREATER | CHART-EDF-001; CHART-ANNOT-001 | KS 검정으로 확인하는 현재 분포의 오른쪽 이동. one-sided greater 변종에서는 현재 값이 기준보다 커지는 방향인지 CHART-ANNOT-001의 방향성 annotation과 함께 읽는다. |
| KS Test / TWO_SAMPLE_KS_ONE_SIDED_LESS | CHART-EDF-001; CHART-ANNOT-001 | KS 검정으로 확인하는 현재 분포의 오른쪽 이동. less 변종에서는 반대 방향 여부를 별도 확인해야 하며, 이 예시는 현재 분포가 큰 값 쪽으로 이동한 사례다. |
| KS Test / TWO_SAMPLE_KS_EXACT_PVALUE | CHART-EDF-001 | KS 검정으로 확인하는 현재 분포의 오른쪽 이동. ECDF 최대 차이 D=0.217과 p-value 기준을 함께 보고 표본 수 영향을 점검한다. |
| KS Test / TWO_SAMPLE_KS_ASYMPTOTIC_PVALUE | CHART-EDF-001 | KS 검정으로 확인하는 현재 분포의 오른쪽 이동. 근사 p-value가 <0.001인지와 효과 크기 D=0.217을 함께 확인한다. |
| KS Test / KS_WITH_TIES_OR_DISCRETE_CAUTION | CHART-EDF-001 | KS 검정으로 확인하는 현재 분포의 오른쪽 이동. discrete/ties가 있으면 p-value 해석을 조심하고 ECDF 차이 위치와 히스토그램 이동을 함께 설명한다. |
| KS Test / LILLIEFORS_RELATED_ONE_SAMPLE | CHART-EDF-001 | KS 검정으로 확인하는 현재 분포의 오른쪽 이동. 알려진 CDF 또는 추정 CDF와 현재 ECDF의 최대 차이를 값 범위와 함께 설명한다. |
| KS Test / HIGHER_ORDER_KS | CHART-EDF-001 | KS 검정으로 확인하는 현재 분포의 오른쪽 이동. 최대 차이뿐 아니라 히스토그램에서 오른쪽 이동과 분산 변화가 동반되는지 함께 본다. |
| KS Test / TWO_SAMPLE_KS_APPROX_QUANTILE | CHART-EDF-001; CHART-ANNOT-002 | KS 검정으로 확인하는 현재 분포의 오른쪽 이동. 근사 quantile 변종에서는 D=0.217 근처 판단이 approximation error로 뒤집히는지 CHART-ANNOT-002와 함께 확인한다. |
| Wasserstein Distance / WASSERSTEIN_1D_EXACT | CHART-DIST-001 | 결제금액 분포의 오른쪽 이동과 거리 증가. Wasserstein distance 0.68, 평균 이동 +0.68, 상위 10% 분위수 1.13 -> 1.99 이동을 함께 읽는다. |
| Wasserstein Distance / WASSERSTEIN_WINDOW_TREND | CHART-DIST-001 | 결제금액 분포의 오른쪽 이동과 거리 증가. window distance가 관리 기준 0.30을 넘어 최근 0.68까지 증가하는지 확인한다. |
| Wasserstein Distance / SLICED_WASSERSTEIN_EMBEDDING | CHART-DIST-001; CHART-ANNOT-002 | 결제금액 분포의 오른쪽 이동과 거리 증가. sliced/embedding 변종에서는 projection count와 approximation error를 CHART-ANNOT-002와 함께 확인한다. |
| Wasserstein Distance / WASSERSTEIN_APPROX_HISTOGRAM | CHART-DIST-001; CHART-ANNOT-002 | 결제금액 분포의 오른쪽 이동과 거리 증가. histogram 근사 binning이 distance 0.68 판단을 바꾸는지 CHART-ANNOT-002와 함께 점검한다. |
| Chi-square Test / CHI_SQUARE_GOODNESS_OF_FIT | CHART-CAT-001 | C·D등급 증가와 A등급 감소로 보는 범주 비중 변화. Chi-square 38.0, p-value 0.003, C등급 기여도 13.6을 함께 읽는다. |
| Chi-square Test / CHI_SQUARE_HOMOGENEITY | CHART-CAT-001 | C·D등급 증가와 A등급 감소로 보는 범주 비중 변화. C등급 176 -> 225 증가와 A등급 132 -> 101 감소를 확인한다. |
| Chi-square Test / CHI_SQUARE_WITH_LOW_EXPECTED_COUNT_CAUTION | CHART-CAT-001 | C·D등급 증가와 A등급 감소로 보는 범주 비중 변화. 낮은 기대빈도 0개인지 확인해 카이제곱 근사 주의 신호를 점검한다. |
| Fisher's Exact Test / TWO_BY_TWO_FISHER_EXACT | CHART-CAT-004 | Fisher 검정으로 본 event 비율 상승. 기준 6/42(14.3%)에서 현재 14/38(36.8%)로 +22.6pp 증가하고, p-value 0.018과 OR 3.50 [1.18, 10.4]를 함께 읽는다. |
| Fisher's Exact Test / ONE_SIDED_FISHER_EXACT | CHART-CAT-004; CHART-ANNOT-001 | Fisher 검정으로 본 event 비율 상승. 현재 event rate가 36.8%로 기준 14.3%보다 높고 one-sided p-value 0.009가 작으므로, 사전 증가 방향 가설은 CHART-ANNOT-001의 방향성 annotation과 함께 확인한다. |
| Fisher's Exact Test / EXTENDED_CONTINGENCY_EXACT_TEST | CHART-CAT-004 | Fisher 검정으로 본 event 비율 상승. 2x2 예시는 기준 event 6건, 현재 event 14건과 OR 3.50을 통해 작은 표본 contingency 차이를 읽으며, 확장 표에서는 범주별 count 정의 일관성을 추가 확인한다. |
| G-test / LIKELIHOOD_RATIO_G_TEST_GOF | CHART-CAT-001 | C·D등급 증가와 A등급 감소로 보는 범주 비중 변화. 관측/기대 차이와 잔차 방향으로 어떤 범주가 신호를 만드는지 읽는다. |
| G-test / LIKELIHOOD_RATIO_G_TEST_INDEPENDENCE | CHART-CAT-001 | C·D등급 증가와 A등급 감소로 보는 범주 비중 변화. C등급 +49건, D등급 +27건, A등급 -31건의 방향을 함께 확인한다. |
| G-test / G_TEST_WITH_SMALL_COUNT_CAUTION | CHART-CAT-001 | C·D등급 증가와 A등급 감소로 보는 범주 비중 변화. 낮은 기대빈도와 rare category 병합 필요 여부를 함께 점검한다. |
| PSI / NUMERIC_BINNED_PSI | CHART-PSI-001 | 상위 점수 구간 증가로 본 PSI 드리프트. PSI 0.123이 관리 기준 0.10을 넘고, 80-100 bin이 12% -> 20%(+8pp)로 증가해 기여도 0.041로 가장 큰지 읽는다. |
| PSI / CATEGORICAL_PSI | CHART-PSI-001 | 상위 점수 구간 증가로 본 PSI 드리프트. 범주형 bin에서도 80-100 bin 12% -> 20%(+8pp), 20-40 bin 22% -> 15%(-7pp)처럼 어떤 bin 이동이 PSI 0.123을 만드는지 확인한다. |
| PSI / SCORE_BAND_PSI | CHART-PSI-001 | 상위 점수 구간 증가로 본 PSI 드리프트. 80-100과 60-80 score band가 각각 +8pp 증가하고 최근 PSI 0.123이 기준 0.10을 초과하는지 함께 본다. |
| PSI / POPULATION_WEIGHTED_PSI | CHART-PSI-001 | 상위 점수 구간 증가로 본 PSI 드리프트. 낮은 band 감소와 높은 band 증가가 전체 population shift인지, 상위 기여 80-100 bin 0.041과 PSI 추세 0.035 -> 0.123을 함께 읽는다. |
| KL Divergence / DISCRETE_KL_DIVERGENCE | CHART-PROB-001 | 오른쪽 값 구간의 확률 증가와 KL 기여. KL(q||p) 0.023, 직전 window 0.086, 최대 기여 1.2 bin 0.042를 함께 읽는다. |
| KL Divergence / HISTOGRAM_KL_DIVERGENCE | CHART-PROB-001 | 오른쪽 값 구간의 확률 증가와 KL 기여. 0.8, 1.2, 1.6 bin에서 현재 확률이 기준보다 높아지는지 확인한다. |
| KL Divergence / SMOOTHED_KL_DIVERGENCE | CHART-PROB-001 | 오른쪽 값 구간의 확률 증가와 KL 기여. 기준 확률이 낮은 오른쪽 tail bin은 smoothing과 sample count 영향을 함께 점검한다. |
| KL Divergence / SYMMETRIZED_KL | CHART-PROB-001 | 오른쪽 값 구간의 확률 증가와 KL 기여. KL(q||p) 0.023과 역방향 KL 0.062가 서로 다르므로 비대칭 원인을 별도 확인한다. |
| Jensen-Shannon Distance / JENSEN_SHANNON_DIVERGENCE | CHART-PROB-002 | 탐색 감소와 구매 증가로 보는 카테고리 비중 변화. JS Distance 0.121, 직전 0.18, 구매 +0.07과 검색 -0.07을 함께 읽는다. |
| Jensen-Shannon Distance / JENSEN_SHANNON_DISTANCE | CHART-PROB-002 | 탐색 감소와 구매 증가로 보는 카테고리 비중 변화. JS가 현재 관리 기준 아래인지와 category delta 방향이 일관적인지 확인한다. |
| Jensen-Shannon Distance / MULTICLASS_PROBABILITY_JS | CHART-PROB-002 | 탐색 감소와 구매 증가로 보는 카테고리 비중 변화. 검색/상세 감소와 구매/장바구니 증가가 category mix 이동인지 읽는다. |
| Jensen-Shannon Distance / TEXT_TOPIC_JS | CHART-PROB-002 | 탐색 감소와 구매 증가로 보는 카테고리 비중 변화. topic category가 탐색 쪽에서 전환 쪽으로 이동했는지 delta를 함께 본다. |
| Hellinger Distance / DISCRETE_HELLINGER_DISTANCE | CHART-PROB-002 | 탐색 감소와 구매 증가로 보는 카테고리 비중 변화. Hellinger 0.101과 JS 0.121이 같은 방향의 완화 신호인지 확인한다. |
| Hellinger Distance / HISTOGRAM_HELLINGER_DISTANCE | CHART-PROB-002 | 탐색 감소와 구매 증가로 보는 카테고리 비중 변화. bounded distance가 낮아져도 구매 +0.07, 검색 -0.07 delta가 남아 있는지 본다. |
| Hellinger Distance / CATEGORICAL_HELLINGER_DISTANCE | CHART-PROB-002 | 탐색 감소와 구매 증가로 보는 카테고리 비중 변화. category별 확률 차이를 Hellinger와 delta bar로 함께 확인한다. |
| Total Variation Distance / CATEGORICAL_TOTAL_VARIATION | CHART-CAT-002 | 검색 감소와 구매 증가의 범주 비중 이동. TV 0.150, 총 절대 이동 0.300, 검색 -0.08과 구매 +0.08을 함께 읽는다. |
| Total Variation Distance / HISTOGRAM_TOTAL_VARIATION | CHART-CAT-002 | 검색 감소와 구매 증가의 범주 비중 이동. window TV가 0.07에서 0.16까지 오른 뒤 현재 0.15 관리 기준선에 걸쳐 있는지 확인한다. |
| Total Variation Distance / PROBABILITY_VECTOR_TOTAL_VARIATION | CHART-CAT-002 | 검색 감소와 구매 증가의 범주 비중 이동. 확률 벡터에서 검색 0.26 -> 0.18, 구매 0.16 -> 0.24 이동이 TV 신호를 만드는지 본다. |
| L-Infinity Distance / CATEGORICAL_L_INFINITY | CHART-CAT-003 | 검색 감소가 만든 L-infinity 범주 변화 신호. L-infinity 0.120, 검색 0.28 -> 0.16, delta -0.12가 관리 기준 0.10 초과 신호를 만드는지 본다. |
| L-Infinity Distance / PROBABILITY_VECTOR_L_INFINITY | CHART-CAT-003 | 검색 감소가 만든 L-infinity 범주 변화 신호. 확률 벡터에서 가장 큰 단일 차이가 검색 -0.12이고 구매 +0.08은 보조 이동인지 확인한다. |
| L-Infinity Distance / BINNED_NUMERIC_L_INFINITY | CHART-CAT-003 | 검색 감소가 만든 L-infinity 범주 변화 신호. binned category 중 최대 절대 delta 0.12가 최근 window 0.11 -> 0.12 상승과 함께 기준을 넘는지 본다. |
| Bhattacharyya Distance / DISCRETE_BHATTACHARYYA_DISTANCE | CHART-PROB-003 | 오른쪽 이동으로 줄어든 기준·현재 분포 겹침. overlap 0.820, Bhattacharyya 0.023, 1.5 bin +0.055를 함께 읽는다. |
| Bhattacharyya Distance / GAUSSIAN_BHATTACHARYYA_DISTANCE | CHART-PROB-003 | 오른쪽 이동으로 줄어든 기준·현재 분포 겹침. BC 0.977로 유사도는 높지만 오른쪽 이동으로 겹침이 줄었는지 확인한다. |
| Bhattacharyya Distance / HISTOGRAM_BHATTACHARYYA_DISTANCE | CHART-PROB-003 | 오른쪽 이동으로 줄어든 기준·현재 분포 겹침. 직전 distance 0.031이 기준 0.030을 넘은 뒤 현재 0.023으로 내려왔는지 본다. |
| Histogram Intersection Normalized Complement / HINC_CATEGORICAL | CHART-HIST-001 | 높은 값 구간 증가로 줄어든 히스토그램 겹침. HINC 0.180, intersection 0.820, 손실 최대 20-30 bin을 함께 읽는다. |
| Histogram Intersection Normalized Complement / HINC_HISTOGRAM_NUMERIC | CHART-HIST-001 | 높은 값 구간 증가로 줄어든 히스토그램 겹침. 20-30 bin -0.06과 70-80 bin +0.05가 overlap 감소를 만드는지 확인한다. |
| Histogram Intersection Normalized Complement / HINC_IMAGE_FEATURE | CHART-HIST-001 | 높은 값 구간 증가로 줄어든 히스토그램 겹침. 직전 HINC 0.24가 기준 0.22를 넘은 뒤 현재 0.18로 내려왔는지 본다. |
| Anderson-Darling Test / ONE_SAMPLE_ANDERSON_DARLING | CHART-EDF-002 | 상위 꼬리 극단값 확대로 보는 분포 변화. AD 통계량 2.84, p-value 0.012와 함께 상위 99% 분위수가 기준 2.60에서 현재 3.61로 커지는지 읽는다. |
| Anderson-Darling Test / TWO_SAMPLE_ANDERSON_DARLING | CHART-EDF-002 | 상위 꼬리 극단값 확대로 보는 분포 변화. 중심부보다 tail ECDF와 QQ plot의 상위 분위수 이탈을 함께 확인한다. |
| Anderson-Darling Test / K_SAMPLE_ANDERSON_DARLING | CHART-EDF-002 | 상위 꼬리 극단값 확대로 보는 분포 변화. 여러 구간 비교에서도 tail 차이 요약과 QQ tail 이탈이 특정 구간에 집중되는지 본다. |
| Anderson-Darling Test / TAIL_SENSITIVE_AD | CHART-EDF-002 | 상위 꼬리 극단값 확대로 보는 분포 변화. tail 차이 0.50과 상위 98%/99% 분위수 확대를 중심으로 해석한다. |
| Cramer-von Mises Test / ONE_SAMPLE_CVM | CHART-EDF-003 | 중간값 이후 누적되는 CDF 차이로 보는 분포 변화. CvM 통계량 1.89, p-value 0.018, 누적 면적 0.014와 x≈0.07 부근의 CDF 차이 누적을 읽는다. |
| Cramer-von Mises Test / TWO_SAMPLE_CVM | CHART-EDF-003 | 중간값 이후 누적되는 CDF 차이로 보는 분포 변화. 두 ECDF가 한 지점이 아니라 여러 값 범위에서 반복적으로 벌어지는지 확인한다. |
| Cramer-von Mises Test / K_SAMPLE_CVM | CHART-EDF-003 | 중간값 이후 누적되는 CDF 차이로 보는 분포 변화. 여러 구간 비교에서도 누적 제곱 CDF 차이가 어느 값 범위에서 쌓이는지 확인한다. |
| Kuiper's Test / KUIPER_TWO_SAMPLE | CHART-EDF-004 | 원형 데이터의 피크 각도 이동과 CDF 편차. Kuiper V 0.377, p-value 0.009, D-=0.365가 49.5° 부근에서 지배적인지 읽는다. |
| Kuiper's Test / KUIPER_CIRCULAR_DATA | CHART-EDF-004 | 원형 데이터의 피크 각도 이동과 CDF 편차. 기준 peak 20~40°와 현재 peak 40~80° 및 240~260° 구간 변화를 원형 히스토그램으로 확인한다. |
| Kuiper's Test / KUIPER_ONE_SAMPLE | CHART-EDF-004 | 원형 데이터의 피크 각도 이동과 CDF 편차. 알려진 circular 기준 분포 대비 D+/D- 위치와 wrap-around 처리를 함께 확인한다. |
| Baumgartner-Weiss-Schindler Test / BWS_TWO_SAMPLE | CHART-RANK-001 | 높은 순위로 치우친 현재 구간의 위치 이동. 기준/현재 결합 순위에서 현재 샘플이 높은 rank 쪽에 몰리고 중앙값이 -0.07에서 0.50으로 올라가는지 읽는다. |
| Baumgartner-Weiss-Schindler Test / BWS_EXACT_OR_ASYMPTOTIC | CHART-RANK-001 | 높은 순위로 치우친 현재 구간의 위치 이동. 순위 분포와 box/violin의 중앙값/IQR 이동을 함께 확인한다. |
| Baumgartner-Weiss-Schindler Test / BWS_RANK_BASED | CHART-RANK-001 | 높은 순위로 치우친 현재 구간의 위치 이동. 원값 단위보다 결합 순위가 한쪽으로 치우치는지 중심으로 해석한다. |
| Mann-Whitney U / Wilcoxon Rank Sum Test / MANN_WHITNEY_TWO_SIDED | CHART-RANK-001 | 높은 순위로 치우친 현재 구간의 위치 이동. Mann-Whitney U 31,551, 순위 AUC 0.652, 중앙값 차이 +0.57을 함께 읽는다. |
| Mann-Whitney U / Wilcoxon Rank Sum Test / MANN_WHITNEY_ONE_SIDED | CHART-RANK-001; CHART-ANNOT-001 | 높은 순위로 치우친 현재 구간의 위치 이동. one-sided 변종에서는 현재 값이 높아지는 방향 가설과 CHART-ANNOT-001의 방향성 annotation을 함께 확인한다. |
| Mann-Whitney U / Wilcoxon Rank Sum Test / MANN_WHITNEY_EXACT | CHART-RANK-001 | 높은 순위로 치우친 현재 구간의 위치 이동. exact p-value 해석에서도 효과 크기인 순위 AUC 0.652와 분포 위치 이동을 함께 보고한다. |
| t-test 계열 / ONE_SAMPLE_T_TEST | CHART-MEAN-001 | 현재 구간 평균 상승으로 본 드리프트 후보. 현재 평균 57.8이 기준 평균 51.2보다 +6.6 높고, p-value 0.004와 Cohen's d 0.72가 평균 상승 신호를 함께 지지하는지 읽는다. |
| t-test 계열 / TWO_SAMPLE_STUDENT_T_TEST | CHART-MEAN-001 | 현재 구간 평균 상승으로 본 드리프트 후보. 기준 95% CI 49.6~52.8과 현재 55.9~59.7이 분리되는지, 분포 중심 이동도 같은 방향인지 확인한다. |
| t-test 계열 / WELCH_T_TEST | CHART-MEAN-001 | 현재 구간 평균 상승으로 본 드리프트 후보. 분산 차이를 허용하는 변종에서도 평균 51.2 -> 57.8 이동과 d=0.72가 실질적으로 의미 있는지 함께 본다. |
| t-test 계열 / PAIRED_T_TEST | CHART-MEAN-001 | 현재 구간 평균 상승으로 본 드리프트 후보. paired 구조가 유지된 전후 비교에서 평균 차이 +6.6, p-value 0.004, CI 분리가 같은 방향의 변화인지 확인한다. |
| F-test / Variance Test 계열 / F_TEST_EQUAL_VARIANCE | CHART-VAR-001 | 현재 구간에서 커진 값의 변동성. 현재 분산 112.4가 기준 42.3 대비 2.66배이고, SD 6.5 -> 10.6 확대와 box/violin 폭 증가가 같은 방향인지 읽는다. |
| F-test / Variance Test 계열 / ANOVA_F_TEST_GROUP_MEAN | CHART-VAR-001 | 현재 구간에서 커진 값의 변동성. 그룹 간 평균 검정 맥락에서도 분산 42.3 -> 112.4 확대가 평균 차이 해석을 왜곡할 수 있는지 함께 확인한다. |
| F-test / Variance Test 계열 / MODEL_COMPARISON_F_TEST | CHART-VAR-001 | 현재 구간에서 커진 값의 변동성. 모델 비교 F-test에서는 variance ratio 2.66x와 현재 whisker 31.0~77.5 확장이 성능 차이 해석에 영향을 주는지 점검한다. |
| Levene's Test / LEVENE_MEAN_CENTER | CHART-VAR-001 | 현재 구간에서 커진 값의 변동성. 평균 중심 절대편차가 5.1 -> 8.7(+3.6)로 증가하고 Levene p-value 0.012가 같은 신호인지 확인한다. |
| Levene's Test / BROWN_FORSYTHE_MEDIAN_CENTER | CHART-VAR-001 | 현재 구간에서 커진 값의 변동성. 중앙값 주변 퍼짐이 커졌는지 IQR 47.6~56.5 -> 44.0~61.8 확대와 절대편차 +3.6을 함께 읽는다. |
| Levene's Test / TRIMMED_MEAN_LEVENE | CHART-VAR-001 | 현재 구간에서 커진 값의 변동성. outlier 영향을 줄인 변종에서도 분산비 2.66x와 p-value 0.012가 유지되는지 tail 점검과 함께 해석한다. |
| Energy Distance / UNIVARIATE_ENERGY_DISTANCE | CHART-MV-001 | 기준·현재 구간의 다변량 분포 분리. Energy distance 0.73이 관리 기준 0.45를 넘고, p-value 0.012와 projection gap 1.35가 같은 방향의 분리 신호인지 읽는다. |
| Energy Distance / MULTIVARIATE_ENERGY_DISTANCE | CHART-MV-001 | 기준·현재 구간의 다변량 분포 분리. 현재 sample이 우상단으로 이동하고 window 7부터 distance가 0.47 -> 0.73으로 커지는지 확인한다. |
| Energy Distance / ENERGY_DISTANCE_PERMUTATION_TEST | CHART-MV-001 | 기준·현재 구간의 다변량 분포 분리. 관측 distance 0.73이 permutation null의 오른쪽 꼬리 밖에 있고 p-value 0.012인지 함께 본다. |
| Epps-Singleton Test / TWO_SAMPLE_EPPS_SINGLETON | CHART-DISTSHAPE-001 | 현재 분포의 오른쪽 어깨와 다봉성 변화. ES statistic 12.8, p-value 0.006, 최대 ECF 차이 t=2.0(real 0.24, imaginary 0.19)을 함께 읽는다. |
| Epps-Singleton Test / DISCRETE_EPPS_SINGLETON | CHART-DISTSHAPE-001 | 현재 분포의 오른쪽 어깨와 다봉성 변화. 기준 peak 50 부근과 현재 peak 65 부근의 분포 형태 차이가 discrete support나 ties 영향인지 함께 점검한다. |
| Epps-Singleton Test / ASYMPTOTIC_EPPS_SINGLETON | CHART-DISTSHAPE-001 | 현재 분포의 오른쪽 어깨와 다봉성 변화. p-value 0.006을 근사 검정 결과로 읽되, t=2.0 기여도 0.094와 overlay의 다봉성 변화를 같이 확인한다. |
| MMD / KERNEL_MMD_UNBIASED | CHART-MV-002 | 커널 MMD로 본 임베딩 분포 변화. MMD score 0.36이 관리 기준 0.18을 넘고, p-value 0.008과 kernel bandwidth 1.20을 함께 확인한다. |
| MMD / KERNEL_MMD_BIASED | CHART-MV-002 | 커널 MMD로 본 임베딩 분포 변화. 현재 embedding 중심이 약 (-0.4, 0.25)에서 (1.55, 1.75) 방향으로 이동했는지 MMD score 0.36과 함께 읽는다. |
| MMD / LINEAR_TIME_MMD | CHART-MV-002 | 커널 MMD로 본 임베딩 분포 변화. window 7부터 MMD score가 0.19 -> 0.36으로 커지는 흐름이 근사 계산에서도 유지되는지 확인한다. |
| MMD / STREAMING_MMD | CHART-MV-002 | 커널 MMD로 본 임베딩 분포 변화. 최근 window에서 기준 0.18을 반복 초과하고 permutation p-value 0.008인지 함께 본다. |
| LSDD / LEAST_SQUARES_DENSITY_DIFFERENCE | CHART-MV-003 | 밀도 차이로 본 신규 구간 유입과 기존 구간 감소. LSDD score 0.34가 관리 기준 0.17을 넘고, 우상단 밀도 증가 +0.48과 좌하단 밀도 감소 -0.30이 함께 나타나는지 읽는다. |
| LSDD / LSDD_WITH_PREPROCESSING | CHART-MV-003 | 밀도 차이로 본 신규 구간 유입과 기존 구간 감소. 전처리 적용 후에도 window 7부터 LSDD score가 0.18 -> 0.34로 증가하고 heatmap의 증가/감소 위치가 유지되는지 확인한다. |
| LSDD / PERMUTATION_LSDD | CHART-MV-003 | 밀도 차이로 본 신규 구간 유입과 기존 구간 감소. 관측 LSDD score 0.34가 permutation null의 오른쪽 꼬리 밖에 있고 p-value 0.010인지 함께 본다. |
| ADWIN / ADWIN_MEAN_STREAM | CHART-STREAM-001 | ADWIN 경보 이후 스트림 평균 상승과 윈도 축소. t=23 alarm, 평균 0.38 -> 0.68, delta +0.30, p-value 0.009, window width 170 -> 62를 함께 읽어 평균 상승 drift 후보인지 확인한다. |
| ADWIN / ADWIN_ERROR_RATE | CHART-STREAM-001 | ADWIN 경보 이후 스트림 평균 상승과 윈도 축소. error rate stream에 적용할 때도 t=23 alarm 전후 평균 0.38 -> 0.68과 window width 170 -> 62 축소가 같은 방향인지 확인한다. |
| ADWIN / ADWIN_DISTANCE_STREAM | CHART-STREAM-001 | ADWIN 경보 이후 스트림 평균 상승과 윈도 축소. distance stream에 적용할 때도 delta +0.30이 운영 기준 0.20을 넘고 p-value 0.009가 작으며 alarm 후 새 수준이 유지되는지 확인한다. |
| KSWIN / KSWIN_STANDARD | CHART-STREAM-002 | 최근 윈도 분포 이동과 KSWIN 경보. 과거 window 10~20의 0.34~0.42 구간과 최근 window 24~34의 0.52~0.74 구간을 비교하고, KS statistic 0.55, p-value 0.011, threshold 0.36 초과를 함께 읽는다. |
| KSWIN / KSWIN_WITH_SUBSAMPLING | CHART-STREAM-002 | 최근 윈도 분포 이동과 KSWIN 경보. subsampling 변종에서도 ECDF 최대 차이 D=0.55와 alarm index 28이 window 표본 선택에 민감한지 확인한다. |
| KSWIN / KSWIN_NUMERIC_STREAM | CHART-STREAM-002 | 최근 윈도 분포 이동과 KSWIN 경보. numeric stream 값이 과거 0.34~0.42 수준에서 최근 0.52~0.74 수준으로 이동했는지와 KS statistic 0.55가 threshold 0.36을 넘는지 함께 본다. |
| Page-Hinkley Test / PAGE_HINKLEY_INCREASE | CHART-STREAM-003 | Page-Hinkley 기반 스트림 평균 상승 경보. metric이 t=20의 0.53에서 t=36의 0.84까지 상승하고, PH statistic이 t=29에 19.6으로 threshold 18.0을 넘어 최종 25.5까지 증가하는지 읽는다. |
| Page-Hinkley Test / PAGE_HINKLEY_DECREASE | CHART-STREAM-003 | Page-Hinkley 기반 스트림 평균 상승 경보. 감소 방향 변종에서는 방향 설정을 별도 확인해야 하며, 이 예시는 metric 0.53 -> 0.84 상승과 PH statistic threshold 18.0 초과가 나타난 상방 변화 사례다. |
| CUSUM / ONE_SIDED_UPPER_CUSUM | CHART-CTRL-001; CHART-ANNOT-001 | 누적 편차로 확인하는 상방 평균 이동 경보. raw metric이 target 0.53 위로 반복 이탈하고 C+가 control limit 25를 넘어 52.9까지 증가하는지를 읽는다. 방향성 annotation으로 upper 방향을 함께 표시한다. |
| CUSUM / ONE_SIDED_LOWER_CUSUM | CHART-CTRL-001; CHART-ANNOT-001 | 누적 편차로 확인하는 평균 이동 경보. 하방 변종에서는 C-가 control limit을 넘는지를 읽어야 하며, 이 예시처럼 C+가 지배적인 화면은 상방 변화 사례로 해석한다. |
| CUSUM / TWO_SIDED_CUSUM | CHART-CTRL-001 | 누적 편차로 확인하는 상방 평균 이동 경보. C+와 C-를 함께 비교해 어느 방향의 평균 이동이 control limit을 넘었는지 확인한다. |
| CUSUM / CUSUM_ON_DISTANCE_STREAM | CHART-CTRL-001 | 누적 편차로 확인하는 상방 평균 이동 경보. distance stream이 기준선보다 지속적으로 높아져 C+가 누적되는지 확인한다. |
| EWMA / EWMA_UNIVARIATE_CONTROL_CHART | CHART-CTRL-002 | EWMA 평활화로 확인하는 점진적 상방 평균 이동. raw metric 잡음 속에서 EWMA가 UCL 0.72를 넘어 final 0.80까지 상승하고 timeline이 warning에서 alarm으로 전환되는지 읽는다. |
| EWMA / EWMA_ONE_SIDED | CHART-CTRL-002; CHART-ANNOT-001 | EWMA 평활화로 확인하는 점진적 상방 평균 이동. one-sided 변종에서는 EWMA가 선언 방향의 control limit을 넘는지 확인하고 방향성 annotation을 함께 읽는다. |
| EWMA / EWMA_BASELINE_REPLAY_THRESHOLD | CHART-CTRL-002 | EWMA 평활화로 확인하는 점진적 상방 평균 이동. baseline replay로 산정한 UCL/LCL 기준에서 EWMA가 t=27 부근부터 UCL을 넘는지 확인한다. |
| Geometric Moving Average / GMA_CONTROL_CHART | CHART-CTRL-002 | EWMA/GMA 평활화로 확인하는 점진적 상방 평균 이동. smoothed average가 center 0.50에서 UCL 0.72 위로 이동하는지 읽는다. |
| Geometric Moving Average / GMA_ONE_SIDED | CHART-CTRL-002; CHART-ANNOT-001 | EWMA/GMA 평활화로 확인하는 점진적 상방 평균 이동. one-sided 방향과 alarm direction이 일치하는지 annotation과 함께 확인한다. |
| Geometric Moving Average / GMA_WITH_EMPIRICAL_LIMIT | CHART-CTRL-002 | EWMA/GMA 평활화로 확인하는 점진적 상방 평균 이동. empirical limit 기준에서 smoothed average의 UCL 초과와 alarm timeline 전환을 함께 본다. |
| BOCD / BAYESIAN_ONLINE_CHANGE_POINT_GAUSSIAN | CHART-BOCD-001 | 온라인 변화점 확률과 스트림 수준 변화 확인. change point probability가 t=18에서 0.87로 집중되고 run length posterior가 reset되며 stream 평균이 0.55에서 0.87로 이동하는지를 함께 읽는다. |
| BOCD / BOCD_HAZARD_RATE_VARIANT | CHART-BOCD-001 | 온라인 변화점 확률과 스트림 수준 변화 확인. hazard rate 민감도에 따라 t=18 primary peak와 t=27 보조 peak가 과도하게 발생한 것은 아닌지 함께 점검한다. |
| BOCD / BOCD_PREDICTIVE_PROBABILITY | CHART-BOCD-001 | 온라인 변화점 확률과 스트림 수준 변화 확인. posterior peak, run length reset, stream 평균 이동이 같은 시점에 맞물리는지 확인해 predictive probability 기반 변화점 후보로 해석한다. |
| SeqDrift / SEQDRIFT1 | CHART-STREAM-004 | SeqDrift 순차 검정의 스트림 상승 경보. t=27에서 evidence 15.1이 bound 12.2를 넘고, reference mean 0.53 대비 stream 값이 0.75까지 상승하며 detect delay 4 step으로 drift 후보가 표시되는지 읽는다. |
| SeqDrift / SEQDRIFT2 | CHART-STREAM-004 | SeqDrift 순차 검정의 스트림 상승 경보. 최종 evidence 26.5와 alarm index 27, delta +0.34, warning -> drift timeline을 함께 확인해 순차 검정 기반 stream 상승 후보를 해석한다. |
| SPRT / SPRT_BERNOULLI_ERROR_RATE | CHART-STREAM-005 | SPRT의 오류율 상승 가설 채택 과정. 오류율이 0.08에서 0.40까지 상승하고 t=25에서 LLR 11.0이 H1 경계 10.8을 넘어 최종 16.0까지 증가하는지 읽는다. |
| SPRT / SPRT_GAUSSIAN_MEAN_SHIFT | CHART-STREAM-005 | SPRT의 오류율 상승 가설 채택 과정. 이 예시는 Bernoulli 오류율 상승 사례이므로 Gaussian 평균 이동 변종에는 H0/H1 평균 가정이 같은 방향인지 확인한 뒤 LLR 16.0과 H1 경계 10.8 초과를 해석한다. |
| DDM / DDM_STANDARD | CHART-ERR-001 | 오류율 상승과 DDM 드리프트 경보. 오류율이 warning 기준 0.27을 t=22에서 넘고 drift 기준 0.36을 t=26에서 넘은 뒤 final error 0.46까지 상승하는지 읽는다. |
| DDM / DDM_WARNING_BUFFER | CHART-ERR-001 | 오류율 상승과 DDM 드리프트 경보. t=22~25 warning buffer가 t=26 drift alarm으로 이어지는지와 final error 0.46까지 상승이 지속되는지 확인한다. |
| DDM / DDM_CLASS_SPECIFIC | CHART-ERR-001 | 오류율 상승과 DDM 드리프트 경보. 전체 오류율 기준으로 t=22 warning, t=26 drift가 발생하므로 class-specific 변종에서는 같은 시점의 class별 오류율을 추가로 대조한다. |
| RDDM / RDDM_STANDARD | CHART-ERR-002 | RDDM의 경보 구간 보존과 재설정 과정. Error rate가 t=20에 warning 기준 0.28에 닿고 t=25에 drift 기준 0.38을 초과하며, retained window가 reset 직전 156에서 t=26 reset 직후 44로 축소되는지 읽는다. |
| RDDM / RDDM_REACTIVE_RESET | CHART-ERR-002 | RDDM의 경보 구간 보존과 재설정 과정. t=26 reactive reset 이후 error rate가 0.42에서 마지막 0.29까지 낮아지고, warning 구간을 retain한 뒤 새 window로 전환되는지 확인한다. |
| EDDM / EDDM_DISTANCE_BETWEEN_ERRORS | CHART-ERR-003 | 오류 간격 축소로 나타난 점진적 성능 저하. Distance score가 1.00에서 0.44까지 하락하고, t=11에 warning 기준 0.90 아래로 내려간 뒤 t=19에 drift 기준 0.75를 통과하는지 읽는다. |
| EDDM / EDDM_WARNING_DRIFT | CHART-ERR-003 | 오류 간격 축소로 나타난 점진적 성능 저하. t=1~10 normal, t=11~18 warning, t=19 이후 drift로 전환되는 상태 흐름이 score 하락과 일치하는지 확인한다. |
| EDDM / EDDM_GRADUAL_DRIFT | CHART-ERR-003 | 오류 간격 축소로 나타난 점진적 성능 저하. 초반 오류 event는 t=3, 8, 13, 17처럼 떨어져 있지만 후반 t=27~32는 매 시점 발생해 gradual error-rate drift 후보인지 본다. |
| ECDD-WT / ECDD_WT_STANDARD | CHART-ERR-004 | ECDD 통계량 상승과 오류율 드리프트 감지. ECDD statistic이 t=22에서 warning limit 0.72, t=26에서 drift limit 0.95를 넘고 weighted error rate도 0.07 -> 0.45로 상승하는지 함께 읽는다. |
| ECDD-WT / ECDD_WT_WARNING_DRIFT | CHART-ERR-004 | ECDD 통계량 상승과 오류율 드리프트 감지. Warning 구간 t=22~25가 drift 상태로 이어지는지와 statistic final 1.28이 일시 spike가 아닌 누적 악화인지 확인한다. |
| ECDD-WT / ECDD_WT_ERROR_STREAM | CHART-ERR-004 | ECDD 통계량 상승과 오류율 드리프트 감지. Weighted error stream이 t=26 이후 계속 상승해 ECDD-WT drift 후보 판단을 뒷받침하는지 본다. |
| HDDM-A / HDDM_A_HOEFFDING_BOUND | CHART-ERR-005 | 평균 오류 차이 확대로 보는 HDDM 드리프트 경보. Mean difference가 t=22에서 warning bound 0.26, t=26에서 drift bound 0.36을 넘고 final 0.50까지 커지는지 읽는다. |
| HDDM-A / HDDM_A_WARNING_DRIFT | CHART-ERR-005 | 평균 오류 차이 확대로 보는 HDDM 드리프트 경보. t=1~21 normal, t=22~25 warning, t=26 이후 drift로 전환되는 흐름이 bound 초과와 일치하는지 확인한다. |
| HDDM-A / HDDM_A_TWO_SIDED | CHART-ERR-005 | 평균 오류 차이 확대로 보는 HDDM 드리프트 경보. Two-sided guard band가 있어도 이 예시의 판단은 상방 error 증가 방향의 mean difference 초과에서 나온다. |
| HDDM-W / HDDM_W_WEIGHTED_AVERAGE | CHART-ERR-005 | 평균 오류 차이 확대로 보는 HDDM 드리프트 경보. Weighted error trend가 0.08 -> 0.47로 상승해 recent window 오류 평균 증가를 뒷받침하는지 본다. |
| HDDM-W / HDDM_W_WARNING_DRIFT | CHART-ERR-005 | 평균 오류 차이 확대로 보는 HDDM 드리프트 경보. Warning 이후 t=26 drift marker가 나타나고 error trend도 같은 방향인지 함께 확인한다. |
| HDDM-W / HDDM_W_RECENT_ERROR_WEIGHTING | CHART-ERR-005 | 평균 오류 차이 확대로 보는 HDDM 드리프트 경보. 최근 오류에 더 큰 가중치를 둔 설정에서 error 상승과 bound 초과가 동시에 나타나는지 읽는다. |
| STEPD / STEPD_ACCURACY_WINDOW | CHART-ERR-006 | 최근 정확도 하락으로 본 STEPD 드리프트 전환. Recent accuracy가 0.91에서 0.64까지 떨어지고 overall accuracy보다 빠르게 낮아지는지 읽는다. |
| STEPD / STEPD_WARNING_DRIFT | CHART-ERR-006 | 최근 정확도 하락으로 본 STEPD 드리프트 전환. Gap이 t=15에서 warning threshold 0.10을 넘고 t=20에서 drift threshold 0.15를 초과하는지 확인한다. |
| STEPD / STEPD_SUPERVISED_STREAM | CHART-ERR-006 | 최근 정확도 하락으로 본 STEPD 드리프트 전환. t=1~14 normal, t=15~19 warning, t=20 이후 drift로 이어지는 supervised 성능 저하 흐름을 본다. |
| Hotelling T2 / HOTELLING_T2_ONE_SAMPLE_PHASE_II | CHART-MV-004 | 다변량 평균 벡터의 기준 범위 이탈. 현재 T2 25.7이 UCL 14.0을 넘고, p-value 0.004와 평균 shift 1.62가 같은 방향의 평균 이동 신호인지 읽는다. |
| Hotelling T2 / HOTELLING_T2_TWO_SAMPLE | CHART-MV-004 | 다변량 평균 벡터의 기준 범위 이탈. 기준 평균 약 (-0.2, -0.1)에서 현재 평균 약 (1.9, 1.8)로 이동하고 8번째 window부터 T2가 UCL을 넘는지 확인한다. |
| Hotelling T2 / REGULARIZED_HOTELLING_T2 | CHART-MV-004 | 다변량 평균 벡터의 기준 범위 이탈. 소득 36%, 거래금액 28%, 이용빈도 18% 기여가 평균 벡터 이동을 주도하는지 보되 공분산 추정 안정성을 함께 점검한다. |
| MEWMA / MEWMA_STANDARD | CHART-CTRL-003 | MEWMA로 확인하는 여러 지표의 동시 상승 경보. statistic이 t=23 부근에서 UCL 12.0을 넘고 final 19.1까지 상승하며 risk_score 38%, amount 24%, frequency 18% 기여가 함께 나타나는지 읽는다. |
| MEWMA / MEWMA_WITH_MAHALANOBIS_D2 | CHART-CTRL-003 | MEWMA로 확인하는 여러 지표의 동시 상승 경보. Mahalanobis D2 기반 statistic이 UCL을 넘을 때 contribution과 small multiples를 함께 확인해 metric vector의 공동 이동으로 해석한다. |
| Mahalanobis Distance / SAMPLE_MAHALANOBIS_OUTLIER | CHART-MV-005 | 기준 공분산 범위 밖 고거리 샘플 집중. 평균 distance 6.1이 threshold 4.5를 넘고, 초과 sample 22%와 최대 distance 6.9가 우상단 cluster에 모이는지 읽는다. |
| Mahalanobis Distance / WINDOW_MEAN_MAHALANOBIS | CHART-MV-005 | 기준 공분산 범위 밖 고거리 샘플 집중. Window 평균 distance가 8번째 window의 4.9부터 threshold 4.5를 넘고 5.5 -> 6.1로 증가하는지 확인한다. |
| Mahalanobis Distance / ROBUST_MAHALANOBIS | CHART-MV-005 | 기준 공분산 범위 밖 고거리 샘플 집중. Robust covariance 변종에서도 threshold 초과 비중 22%가 소수 outlier인지 구조적 cluster인지 PCA scatter와 histogram으로 함께 본다. |
| OCDD / ONE_CLASS_SVM_DRIFT | CHART-ANOM-001 | 정상 영역 밖 샘플 증가와 이상치 드리프트 후보. Current anomaly score가 0.50 부근으로 이동하고 threshold 0.62 오른쪽 영역이 커지는지 읽는다. |
| OCDD / ISOLATION_FOREST_DRIFT_SCORE | CHART-ANOM-001 | 정상 영역 밖 샘플 증가와 이상치 드리프트 후보. Outlier rate가 t=14에서 기준선 0.20을 넘고 후반 0.37~0.38까지 지속 상승하는지 확인한다. |
| OCDD / AUTOENCODER_RECONSTRUCTION_DRIFT | CHART-ANOM-001 | 정상 영역 밖 샘플 증가와 이상치 드리프트 후보. Projection에서 current outlier가 baseline cluster 밖 current 영역에 집중되는지 함께 본다. |
| Feature Map Drift / MODEL_FEATURE_MAP_KS | CHART-REP-001 | block3 활성 변화로 본 표현 드리프트. block3 c6~c9 score가 0.81, 0.88, 0.92, 0.84로 높아지는지 heatmap에서 읽는다. |
| Feature Map Drift / MODEL_FEATURE_MAP_MMD | CHART-REP-001 | block3 활성 변화로 본 표현 드리프트. Activation histogram의 baseline peak bin 5=35와 current peak bin 7=34 이동을 함께 확인한다. |
| Feature Map Drift / LAYERWISE_FEATURE_MAP_DRIFT | CHART-REP-001 | block3 활성 변화로 본 표현 드리프트. Layer embedding projection에서 baseline cluster와 current cluster가 좌우로 분리되는지 본다. |
| Autoencoder Representation Drift / LATENT_SPACE_DRIFT | CHART-REP-002 | 복원 오차 증가로 본 오토인코더 표현 드리프트. Latent projection에서 baseline/current cluster가 분리되고 latent AUC 0.84가 나타나는지 확인한다. |
| Autoencoder Representation Drift / RECONSTRUCTION_ERROR_DRIFT | CHART-REP-002 | 복원 오차 증가로 본 오토인코더 표현 드리프트. Reconstruction error trend가 t=23에서 threshold 0.36을 넘고 final 0.54까지 상승하는지 읽는다. |
| Autoencoder Representation Drift / AUTOENCODER_DOMAIN_CLASSIFIER | CHART-REP-002 | 복원 오차 증가로 본 오토인코더 표현 드리프트. Baseline error peak 0.14/38에서 current peak 0.26/37로 오른쪽 이동하는지 함께 본다. |
| Graph Embedding Drift / GRAPH_EMBEDDING_MMD | CHART-REP-003 | 그래프 임베딩 분리와 허브 노드 드리프트. Graph-level distance가 t=15에서 threshold 0.40을 넘고 final 0.67까지 상승하는지 읽는다. |
| Graph Embedding Drift / GRAPH_EMBEDDING_CENTROID_SHIFT | CHART-REP-003 | 그래프 임베딩 분리와 허브 노드 드리프트. Projection에서 baseline graph embedding과 current graph embedding이 좌우로 분리되는지 확인한다. |
| Graph Embedding Drift / NODE_REPRESENTATION_DRIFT | CHART-REP-003 | 그래프 임베딩 분리와 허브 노드 드리프트. Hub node group max 0.70과 bridge group 0.66처럼 특정 node group에 score가 집중되는지 본다. |
| LLM Query / Semantic Distance 기반 감지 / QUERY_CENTROID_COSINE_SHIFT | CHART-TEXT-001 | 쿼리 의미 공간 이동과 토픽 비중 변화. Centroid cosine distance가 t=22에서 threshold 0.36을 넘고 final 0.58까지 상승하는지 읽는다. |
| LLM Query / Semantic Distance 기반 감지 / TEXT_DOMAIN_CLASSIFIER_DRIFT | CHART-TEXT-001 | 쿼리 의미 공간 이동과 토픽 비중 변화. Domain classifier ROC AUC 0.82가 baseline/current query 구분 가능성을 보강하는지 확인한다. |
| LLM Query / Semantic Distance 기반 감지 / TOPIC_DISTRIBUTION_SHIFT | CHART-TEXT-001 | 쿼리 의미 공간 이동과 토픽 비중 변화. 세 번째 topic 비중이 0.20 -> 0.48로 +28pt 증가해 의미 구성이 바뀌는지 본다. |
| Model Uncertainty Drift / SOFTMAX_CONFIDENCE_DRIFT | CHART-UNC-001 | 확신도 하락과 엔트로피 상승으로 본 불확실성 드리프트. Baseline confidence peak 0.82/41에서 current peak 0.47/38로 낮아지는지 읽는다. |
| Model Uncertainty Drift / ENTROPY_DRIFT | CHART-UNC-001 | 확신도 하락과 엔트로피 상승으로 본 불확실성 드리프트. Entropy가 t=15에서 threshold 0.55를 넘고 final 0.77까지 상승하는지 확인한다. |
| Model Uncertainty Drift / PREDICTIVE_VARIANCE_DRIFT | CHART-UNC-001 | 확신도 하락과 엔트로피 상승으로 본 불확실성 드리프트. ECE 0.12와 class C uncertainty 0.46이 특정 class 불확실성 집중을 보강하는지 본다. |
| SHAP Drift / SHAP_VALUE_DISTRIBUTION_TEST | CHART-EXPL-001 | risk_score 중심으로 바뀐 SHAP 설명 구조. risk_score SHAP 분포 peak가 -0.04에서 0.12 양수 방향으로 이동하는지 읽는다. |
| SHAP Drift / GLOBAL_IMPORTANCE_RANK_SHIFT | CHART-EXPL-001 | risk_score 중심으로 바뀐 SHAP 설명 구조. risk_score mean |SHAP|가 0.27 -> 0.36으로 상승하고 amount는 0.31 -> 0.18로 낮아지는지 확인한다. |
| SHAP Drift / CLASS_CONDITIONAL_SHAP_DRIFT | CHART-EXPL-001 | risk_score 중심으로 바뀐 SHAP 설명 구조. Class C risk_score heat 0.48처럼 특정 class에서 explanation drift가 집중되는지 본다. |
| Tree Feature 기반 감지 / TIME_FEATURE_SPLIT_DETECTOR | CHART-EXPL-002 | query_age 분기로 드러난 현재 구간 분리. query_age importance 0.34와 time split 18이 가장 큰지 읽는다. |
| Tree Feature 기반 감지 / DOMAIN_CLASSIFIER_TREE | CHART-EXPL-002 | query_age 분기로 드러난 현재 구간 분리. query_age > 14d -> device = mobile 경로가 current 82% leaf로 이어지는지 확인한다. |
| Classifier 기반 embedding drift detection / DOMAIN_CLASSIFIER_ROC_AUC | CHART-CLS-001 | 도메인 분류기로 확인한 임베딩 분리. ROC-AUC 0.89로 baseline/current embedding 구간이 구분되는지 읽는다. |
| Classifier 기반 embedding drift detection / DOMAIN_CLASSIFIER_PROBABILITY_DRIFT | CHART-CLS-001 | 도메인 분류기로 확인한 임베딩 분리. Baseline score peak 0.19/38과 current peak 0.68/36의 score 분리와 gap 0.41을 확인한다. |
| Classifier 기반 embedding drift detection / CROSS_VALIDATED_DOMAIN_CLASSIFIER | CHART-CLS-001 | 도메인 분류기로 확인한 임베딩 분리. emb_17 importance 0.31과 embedding projection 분리가 같은 방향인지 함께 본다. |
| Text Domain Classifier Drift / TEXT_DOMAIN_CLASSIFIER_ROC_AUC | CHART-TEXT-002 | 도메인 분류기로 본 텍스트 구성 변화. ROC AUC 0.89로 baseline/current text domain을 강하게 구분하는지 읽는다. |
| Text Domain Classifier Drift / TEXT_DOMAIN_CLASSIFIER_STAT_TEST | CHART-TEXT-002 | 도메인 분류기로 본 텍스트 구성 변화. Classifier score 분포가 baseline peak 0.19/34에서 current peak 0.68/35로 분리되는지 확인한다. |
| Text Domain Classifier Drift / TEXT_DESCRIPTOR_DRIFT | CHART-TEXT-002 | 도메인 분류기로 본 텍스트 구성 변화. refund policy 0.32, enterprise SSO 0.25, invoice issue 0.18 descriptor drift가 어떤 텍스트 변화를 만드는지 본다. |
| HAT / HAT_ADWIN_NODE_MONITORING | CHART-ADAPT-001 | HAT 모델의 드리프트 감지와 대체 트리 교체 과정을 보여준다. Online accuracy 하락, detector state 전환, alternate tree 성장, replacement 이후 회복을 함께 확인한다. |
| HAT / HAT_ALTERNATE_TREE_REPLACEMENT | CHART-ADAPT-001 | HAT 모델의 드리프트 감지와 대체 트리 교체 과정을 보여준다. Online accuracy 하락, detector state 전환, alternate tree 성장, replacement 이후 회복을 함께 확인한다. |
| DriftRetrainingClassifier / DRIFT_RETRAINING_WITH_ADWIN | CHART-ADAPT-002 | 드리프트 경보 후 재학습과 챌린저 승격 검토 과정을 보여준다. Champion 성능 하락, retrain event, challenger 성능 회복, latency 증가를 함께 확인한다. |
| DriftRetrainingClassifier / DRIFT_RETRAINING_WITH_PAGE_HINKLEY | CHART-ADAPT-002 | 드리프트 경보 후 재학습과 챌린저 승격 검토 과정을 보여준다. Champion 성능 하락, retrain event, challenger 성능 회복, latency 증가를 함께 확인한다. |
| DriftRetrainingClassifier / DRIFT_RETRAINING_CHAMPION_CHALLENGER | CHART-ADAPT-002 | 드리프트 경보 후 재학습과 챌린저 승격 검토 과정을 보여준다. Champion 성능 하락, retrain event, challenger 성능 회복, latency 증가를 함께 확인한다. |
| Generic / Fallback / GENERIC_METRIC_THRESHOLD_DRIFT | CHART-GEN-001 | 임시 지표 상승으로 확인한 일반 드리프트 후보. 전용 chart family가 없을 때 metric이 t=15에서 threshold 0.45를 넘고 final 0.68까지 상승하는지 읽는다. |

## 2. Chart Catalog

| chart id | 설명 |
|---|---|
| CHART-EDF-001 | KS 검정으로 확인하는 현재 분포의 오른쪽 이동. x≈0.74에서 기준 CDF 0.804와 현재 CDF 0.587의 최대 차이 D=0.217이 나타나고 히스토그램에서도 현재 분포가 오른쪽으로 이동하는지 읽는다. |
| CHART-EDF-002 | 상위 꼬리 극단값 확대로 보는 분포 변화. AD 통계량 2.84, p-value 0.012, tail 차이 0.50과 상위 99% 분위수 2.60 -> 3.61 확대를 함께 읽는다. |
| CHART-EDF-003 | 중간값 이후 누적되는 CDF 차이로 보는 분포 변화. CvM 통계량 1.89, p-value 0.018, 누적 면적 0.014와 x≈0.07 이후 반복 누적되는 CDF 차이를 읽는다. |
| CHART-EDF-004 | 원형 데이터의 피크 각도 이동과 CDF 편차. Kuiper V 0.377, D-=0.365 at 49.5°와 기준 peak 20~40°에서 현재 40~80°/240~260°로의 이동을 함께 읽는다. |
| CHART-RANK-001 | 높은 순위로 치우친 현재 구간의 위치 이동. Mann-Whitney U 31,551, 순위 AUC 0.652, 중앙값 -0.07 -> 0.50 이동과 높은 rank 쪽 붉은 막대 집중을 함께 읽는다. |
| CHART-DIST-001 | 결제금액 분포의 오른쪽 이동과 거리 증가. Wasserstein 0.68, 평균 이동 +0.68, 상위 10% 이동 +0.86, 결제금액 feature 순위 1위를 함께 읽는다. |
| CHART-PROB-001 | 오른쪽 값 구간의 확률 증가와 KL 기여. 현재 KL 0.023은 기준 0.070 아래지만 직전 0.086까지 상승했고, 1.2/1.6/0.8 bin의 확률 증가가 KL 기여를 만든다. |
| CHART-PROB-002 | 탐색 감소와 구매 증가로 보는 카테고리 비중 변화. JS 0.121, Hellinger 0.101, 구매 +0.07, 검색 -0.07을 함께 읽어 완화 중인 category mix 변화 후보로 본다. |
| CHART-PROB-003 | 오른쪽 이동으로 줄어든 기준·현재 분포 겹침. overlap 0.820, Bhattacharyya 0.023, 직전 0.031, 1.5 bin +0.055를 함께 읽어 완만한 overlap 감소 후보로 본다. |
| CHART-HIST-001 | 높은 값 구간 증가로 줄어든 히스토그램 겹침. HINC 0.180, intersection 0.820, 직전 0.24, 20-30 bin -0.06을 함께 읽어 완화 중인 분포 이동 후보로 본다. |
| CHART-CAT-001 | C·D등급 증가와 A등급 감소로 보는 범주 비중 변화. Chi-square 38.0, p-value 0.003, C등급 +49건, A등급 -31건, 낮은 기대빈도 0개를 함께 읽는다. |
| CHART-CAT-002 | 검색 감소와 구매 증가의 범주 비중 이동. TV 0.150, 총 절대 이동 0.300, 검색 0.26 -> 0.18과 구매 0.16 -> 0.24를 함께 읽어 category mix drift 후보를 확인한다. |
| CHART-CAT-003 | 검색 감소가 만든 L-infinity 범주 변화 신호. L-infinity 0.120, 검색 0.28 -> 0.16, 구매 0.15 -> 0.23, 최근 window 0.12를 함께 읽어 단일 category 집중 drift 후보를 확인한다. |
| CHART-CAT-004 | Fisher 검정으로 본 event 비율 상승. 기준 6/42(14.3%)에서 현재 14/38(36.8%)로 +22.6pp 증가하고, Fisher p-value 0.018, one-sided p-value 0.009, OR 3.50 [1.18, 10.4]를 함께 읽어 작은 표본 category drift 후보를 확인한다. |
| CHART-PSI-001 | 상위 점수 구간 증가로 본 PSI 드리프트. PSI 0.123이 관리 기준 0.10을 넘고, 80-100 bin 12% -> 20%(+8pp), 60-80 bin 24% -> 32%(+8pp), 20-40 bin 22% -> 15%(-7pp)를 함께 읽어 상위 score band 이동 후보를 확인한다. |
| CHART-MEAN-001 | 현재 구간 평균 상승으로 본 드리프트 후보. 기준 평균 51.2에서 현재 평균 57.8로 +6.6 이동하고, 95% CI 49.6~52.8 vs 55.9~59.7, p-value 0.004, Cohen's d 0.72를 함께 읽어 평균 상승 drift 후보를 확인한다. |
| CHART-VAR-001 | 현재 구간에서 커진 값의 변동성. 중심값은 52.0 -> 52.6으로 비슷하지만 분산은 42.3 -> 112.4, SD는 6.5 -> 10.6, 절대편차는 5.1 -> 8.7로 커져 분산 drift 후보를 확인한다. |
| CHART-DISTSHAPE-001 | 현재 분포의 오른쪽 어깨와 다봉성 변화. 기준 분포는 50 부근 단봉형 peak를 보이고 현재 분포는 65 부근 봉우리와 shoulder가 커지며, ES statistic 12.8, p-value 0.006, t=2.0 기여도 0.094를 함께 읽는다. |
| CHART-MV-001 | 기준·현재 구간의 다변량 분포 분리. Energy distance 0.73, 관리 기준 0.45, permutation p-value 0.012, projection gap 1.35를 함께 읽어 여러 feature의 결합 분포가 이동한 drift 후보를 확인한다. |
| CHART-MV-002 | 커널 MMD로 본 임베딩 분포 변화. MMD score 0.36, 관리 기준 0.18, permutation p-value 0.008, bandwidth 1.20과 embedding 중심 이동 약 (-0.4, 0.25) -> (1.55, 1.75)를 함께 읽는다. |
| CHART-MV-003 | 밀도 차이로 본 신규 구간 유입과 기존 구간 감소. LSDD score 0.34, 관리 기준 0.17, permutation p-value 0.010, 우상단 밀도 증가 +0.48과 좌하단 밀도 감소 -0.30을 함께 읽어 density difference drift 후보를 확인한다. |
| CHART-MV-004 | 다변량 평균 벡터의 기준 범위 이탈. Hotelling T2 25.7, UCL 14.0, p-value 0.004, 평균 shift 1.62와 소득 36%·거래금액 28% 기여를 함께 읽어 다변량 평균 drift 후보를 확인한다. |
| CHART-MV-005 | 기준 공분산 범위 밖 고거리 샘플 집중. 평균 Mahalanobis distance 6.1, threshold 4.5, 초과 비중 22%, 최대 distance 6.9를 함께 읽어 우상단 고거리 sample cluster의 공분산 기반 이탈 후보를 확인한다. |
| CHART-STREAM-001 | ADWIN 경보 이후 스트림 평균 상승과 윈도 축소. t=23 alarm, 평균 0.38 -> 0.68, delta +0.30, p-value 0.009, window width 170 -> 62를 함께 읽어 stream 평균 상승 drift 후보를 확인한다. |
| CHART-STREAM-002 | 최근 윈도 분포 이동과 KSWIN 경보. 과거 window 10~20은 0.34~0.42 수준, 최근 window 24~34는 0.52~0.74 수준으로 이동했고, ECDF 최대 차이 D=0.55, KS statistic 0.55, p-value 0.011, threshold 0.36 초과를 함께 읽어 KSWIN stream drift 후보를 확인한다. |
| CHART-STREAM-003 | Page-Hinkley 기반 스트림 평균 상승 경보. metric이 t=20의 0.53에서 t=36의 0.84까지 상승하고 running mean도 0.48 -> 0.72로 올라가며, t=29에서 PH statistic 19.6이 threshold 18.0을 넘어 최종 25.5까지 증가하는 흐름을 읽는다. |
| CHART-STREAM-004 | SeqDrift 순차 검정의 스트림 상승 경보. reference mean 0.53 주변에 있던 stream 값이 t=20 이후 상승해 t=27에 0.75, t=36에 0.87에 도달하고, evidence 15.1이 bound 12.2를 넘은 뒤 최종 26.5까지 증가하는 흐름을 읽는다. |
| CHART-STREAM-005 | SPRT의 오류율 상승 가설 채택 과정. 오류율이 0.08에서 0.40까지 높아지고, LLR이 t=25의 11.0에서 H1 경계 10.8을 넘은 뒤 최종 16.0까지 증가하며 accept H1 상태로 전환되는 흐름을 읽는다. |
| CHART-CTRL-001 | 누적 편차로 확인하는 상방 평균 이동 경보. raw metric이 target 0.53 위로 반복 이탈하고 C+가 limit 25를 넘어 52.9까지 증가하며 C-는 0.1에 머무는지를 함께 읽는다. |
| CHART-CTRL-002 | EWMA 평활화로 확인하는 점진적 상방 평균 이동. raw metric 잡음 속에서 EWMA가 UCL 0.72를 넘어 final 0.80까지 상승하고 normal -> warning -> alarm으로 전환되는지 읽는다. |
| CHART-CTRL-003 | MEWMA로 확인하는 여러 지표의 동시 상승 경보. statistic이 UCL 12.0을 넘고 final 19.1까지 상승하며 risk_score, amount, frequency가 같은 구간에서 함께 움직이는지 읽는다. |
| CHART-BOCD-001 | 온라인 변화점 확률과 스트림 수준 변화 확인. t=18 posterior peak, run length reset, stream 평균 0.55 -> 0.87 이동을 함께 읽고 t=27 보조 변화 가능성도 확인한다. |
| CHART-ERR-001 | 오류율 상승과 DDM 드리프트 경보. 오류율이 0.08에서 0.46까지 오르고, warning 기준 0.27은 t=22, drift 기준 0.36은 t=26에 초과하며 warning buffer가 drift 상태로 이어지는지 읽는다. |
| CHART-ERR-002 | RDDM의 경보 구간 보존과 재설정 과정. Error rate가 t=20의 0.28에서 warning 기준에 닿고 t=25의 0.40에서 drift 기준 0.38을 초과하며, retained window가 156에서 t=26 reset 직후 44로 축소되는 흐름을 읽는다. |
| CHART-ERR-003 | 오류 간격 축소로 나타난 점진적 성능 저하. Distance score가 1.00에서 0.44까지 낮아지고 t=11 warning, t=19 drift로 전환되며, error event가 후반 t=27~32에 연속 발생하는지 함께 읽는다. |
| CHART-ERR-004 | ECDD 통계량 상승과 오류율 드리프트 감지. ECDD statistic이 0.18에서 1.28까지 상승하고 t=22 warning, t=26 drift로 전환되며 weighted error rate도 0.07 -> 0.45로 높아지는 흐름을 읽는다. |
| CHART-ERR-005 | 평균 오류 차이 확대로 보는 HDDM 드리프트 경보. Mean difference가 0.01에서 0.50까지 증가하고 t=22 warning, t=26 drift로 전환되며 error trend도 0.08 -> 0.47로 상승하는 흐름을 읽는다. |
| CHART-ERR-006 | 최근 정확도 하락으로 본 STEPD 드리프트 전환. Recent accuracy가 0.91 -> 0.64까지 낮아지고 overall-recent gap이 t=15 warning, t=20 drift 기준을 넘는 흐름을 읽는다. |
| CHART-ANOM-001 | 정상 영역 밖 샘플 증가와 이상치 드리프트 후보. Anomaly score threshold 0.62, rate threshold 0.20, t=14 alarm, 최종 outlier rate 0.37을 함께 읽어 novelty 기반 drift 후보를 확인한다. |
| CHART-REP-001 | block3 활성 변화로 본 표현 드리프트. Max drift 0.92가 block3 c8에 집중되고 activation peak와 embedding projection도 current 방향으로 이동하는 흐름을 읽는다. |
| CHART-REP-002 | 복원 오차 증가로 본 오토인코더 표현 드리프트. Reconstruction error가 threshold 0.36을 t=23 이후 넘고 p95 error 0.51, latent AUC 0.84와 함께 baseline/current 분리를 보이는지 읽는다. |
| CHART-REP-003 | 그래프 임베딩 분리와 허브 노드 드리프트. Distance final 0.67, node max 0.70, t=15 alarm을 함께 읽어 graph representation drift 후보를 확인한다. |
| CHART-TEXT-001 | 쿼리 의미 공간 이동과 토픽 비중 변화. Cosine distance final 0.58, topic shift +28pt, domain AUC 0.82를 함께 읽어 LLM query semantic drift 후보를 확인한다. |
| CHART-TEXT-002 | 도메인 분류기로 본 텍스트 구성 변화. ROC AUC 0.89, KS score 0.47, top descriptor refund policy 0.32를 함께 읽어 text domain classifier drift 후보를 확인한다. |
| CHART-CLS-001 | 도메인 분류기로 확인한 임베딩 분리. ROC-AUC 0.89, score gap 0.41, top feature emb_17 0.31을 함께 읽어 classifier 기반 embedding drift 후보를 확인한다. |
| CHART-UNC-001 | 확신도 하락과 엔트로피 상승으로 본 불확실성 드리프트. Confidence peak 하락, entropy final 0.77, ECE 0.12, class C uncertainty 0.46을 함께 읽는다. |
| CHART-EXPL-001 | risk_score 중심으로 바뀐 SHAP 설명 구조. risk_score mean |SHAP| 0.27 -> 0.36, channel 0.17 -> 0.24, class C heat 0.48을 함께 읽는다. |
| CHART-EXPL-002 | query_age 분기로 드러난 현재 구간 분리. query_age importance 0.34, time split 18, S4 current 82%를 함께 읽어 tree feature 기반 drift 후보를 확인한다. |
| CHART-ADAPT-001 | HAT 모델의 드리프트 감지와 대체 트리 교체 과정을 보여준다. Online accuracy 하락, detector state 전환, alternate tree 성장, replacement 이후 회복을 함께 확인한다. |
| CHART-ADAPT-002 | 드리프트 경보 후 재학습과 챌린저 승격 검토 과정을 보여준다. Champion 성능 하락, retrain event, challenger 성능 회복, latency 증가를 함께 확인한다. |
| CHART-ANNOT-001 | 단방향 검정의 증가·감소 방향 판단 기준을 보여준다. 이 예시는 direction upper에서 D+ gap +0.11과 one-sided p-value 0.018을 drift 증거로 보고, lower gap -0.08과 lower/less p-value 0.214는 반대 방향 참고 신호로만 읽는다. |
| CHART-ANNOT-002 | 근사 드리프트 점수의 오차와 안정성을 점검한다. Exact/reference score와 approximate score 차이, projection count별 spread, quantile error를 함께 보고 threshold 근처 판단이 근사 오차로 뒤집힐 수 있는지 확인한다. |
| CHART-GEN-001 | 임시 지표 상승으로 확인한 일반 드리프트 후보. Metric final 0.68, threshold 0.45, reference peak 0.33/38에서 current peak 0.54/37로 이동하는 흐름을 읽는다. |
