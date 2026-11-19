from __future__ import annotations

import os

import psycopg


COMPONENT_GUIDES = {
    "adaptive_model_structure_view": (
        "adaptive tree, alternate tree, challenger, model version count처럼 drift 대응 과정에서 모델 구조가 어떻게 바뀌는지 보여준다.",
        "main/alternate 구조의 색상, node 수, replacement/promotion marker, event 전후 구조 변화를 먼저 읽는다.",
        "대체 구조가 먼저 성장하고 이후 replacement가 발생하는지, replacement 뒤 성능 회복과 연결되는지 설명한다.",
        "구조 변화는 대응 메커니즘의 흔적이지 drift 원인 증거가 아니다.",
    ),
    "annotation_callout": (
        "그래프의 특정 지점, 구간, event, threshold crossing, outlier를 텍스트와 화살표로 설명하는 주석 component다.",
        "callout이 어느 점/구간에 anchor되는지, 텍스트가 데이터 값인지 해석 라벨인지 확인한다.",
        "주석이 실제 그래프 값과 맞는지, event marker나 threshold와 같은 시점인지 연결한다.",
        "주석 문구를 검증 없이 최종 결론으로 복사하지 않는다.",
    ),
    "bar_chart": (
        "category, feature, bin, segment, class별 값을 막대 길이로 비교한다.",
        "축 방향, category field, value field, 색상이 reference/current나 severity를 구분하는지 확인한다.",
        "가장 큰 막대, 상위 항목 격차, 기준 초과, reference/current 방향 차이, 긴 꼬리를 설명한다.",
        "막대가 높다는 이유만으로 나쁘거나 원인이라고 쓰지 않는다.",
    ),
    "comparison_table": (
        "baseline/current, before/after, segment별 metric 값을 열로 비교하는 표 component다.",
        "행 단위와 column 의미(reference/current/delta/%change/p-value/count/rank)를 확인한다.",
        "delta가 큰 행, 변화율과 절대 변화가 엇갈리는 행, count가 작은 행을 구분한다.",
        "표의 한 열만 보고 결론을 쓰지 않는다.",
    ),
    "contribution_view": (
        "전체 통계량, 거리, 손실, PSI, 변화량에 feature/bin/segment가 얼마나 기여했는지 보여준다.",
        "값이 contribution인지 signed contribution인지, 단위가 raw인지 normalized share인지 확인한다.",
        "기여가 소수 항목에 집중되는지, 여러 항목에 퍼지는지, 양/음 방향이 상쇄되는지 설명한다.",
        "기여도가 큰 항목을 업무 원인이나 모델 실패 원인으로 확정하지 않는다.",
    ),
    "control_chart": (
        "중심선과 관리한계선 또는 CUSUM 한계를 기준으로 metric/statistic의 관리 상태를 보여준다.",
        "중심선, UCL/LCL, C+/C-, control limit, 관측점 marker와 값을 확인한다.",
        "한 점 초과와 지속 초과를 구분하고, CUSUM이면 작은 편차가 누적되어 한계를 넘는 흐름을 설명한다.",
        "관리한계 초과는 탐지 후보이지 원인 확정이 아니다.",
    ),
    "cumulative_curve": (
        "ECDF, CDF, 누적 비율, cumulative score로 두 분포나 조건을 누적 형태로 비교한다.",
        "x축이 값인지 threshold인지, y축이 누적확률/비율/누적값인지 확인한다.",
        "곡선 간 간격, tail 차이, 최대 gap 위치와 방향을 설명한다.",
        "CDF 차이만으로 원인이나 성능 영향을 단정하지 않는다.",
    ),
    "decision_card": (
        "분석 지표, 판정, threshold, score, 이벤트 시점, 표본 수를 카드 형태로 요약한다.",
        "label/value가 decision/status/metric/threshold/sample count/time window 중 무엇인지 구분한다.",
        "카드 값은 chart-level summary의 기준 맥락으로 쓰고, 그래프 근거와 연결한다.",
        "카드 자체를 독립적인 drift 증거로 과대해석하지 않는다.",
    ),
    "detector_statistic_view": (
        "drift detector가 계산한 score, statistic, p-value, likelihood ratio, 누적 evidence를 보여준다.",
        "값이 커질수록 위험한지 작을수록 위험한지, threshold/alpha/control limit 의미를 확인한다.",
        "threshold crossing 시점, 지속 여부, 원 신호/성능 변화와의 시간 순서를 설명한다.",
        "detector statistic은 알고리즘 내부 근거이지 비즈니스 영향 자체가 아니다.",
    ),
    "distance_metric_view": (
        "reference와 current 사이의 거리, divergence, discrepancy를 window별 또는 feature별로 보여준다.",
        "무엇을 비교하는 거리인지, 값이 클수록 차이가 큰지, threshold나 baseline이 있는지 확인한다.",
        "거리 증가가 단발인지 지속인지, projection/distribution/성능 component와 같은 방향인지 연결한다.",
        "거리 값만으로 성능 저하나 원인을 직접 증명하지 않는다.",
    ),
    "distribution_summary_plot": (
        "평균, 중앙값, 분위수, IQR, min/max, CI 같은 분포 요약값을 압축해 보여준다.",
        "점/선/box/error bar/range가 어떤 통계량인지 확인한다.",
        "중앙값 이동, IQR 확대/축소, CI 겹침, outlier 범위, group 간 spread 차이를 설명한다.",
        "요약 plot만 보고 전체 분포 모양이나 다봉성을 단정하지 않는다.",
    ),
    "distribution_view": (
        "reference/current 또는 group별 연속형 분포를 density, area, curve로 비교한다.",
        "x축 값, y축 density/count/proportion, 색상별 series, smoothing, vertical marker를 확인한다.",
        "중심 이동, 산포 확대, tail 두꺼워짐, overlap 감소, 새로운 mode를 설명한다.",
        "부드러운 density의 세부 굴곡을 원자료 변화로 단정하지 않는다.",
    ),
    "domain_specific_visual": (
        "도메인 지도, 업무 흐름, 텍스트 예시, 범례, notes, 특수 diagram처럼 표준 chart로 표현하기 어려운 맥락을 보여준다.",
        "실제 데이터 시각화인지 범례/notes인지 구분하고, domain entity와 label 의미를 확인한다.",
        "다른 component의 feature/segment와 같은 entity를 가리키는지, 단순 설명 영역인지 구분한다.",
        "notes나 legend 영역이면 독립 증거로 사용하지 않는다.",
    ),
    "event_marker": (
        "alarm, warning, drift, retrain, replacement 같은 사건 시점을 세로선, 점, flag, band로 표시한다.",
        "붉은 세로 점선, 강조점, label이 어떤 event type인지 확인한다.",
        "metric 변화가 marker 전부터 시작됐는지, marker 이후 강화됐는지, 대응 뒤 회복이 있는지 연결한다.",
        "event marker는 시점 정보이며 원인과 효과를 직접 증명하지 않는다.",
    ),
    "heatmap": (
        "두 축 조합별 metric 값을 색 농도나 색상으로 보여준다.",
        "행/열 의미, cell 값 단위, color scale 방향과 midpoint, missing cell을 확인한다.",
        "짙은 cell 위치, 행/열 band, block 구조, 대각선/off-diagonal 집중, 시간 이후 색 변화를 설명한다.",
        "색이 진하다고 항상 나쁜 것은 아니며 missing과 0을 혼동하지 않는다.",
    ),
    "histogram_view": (
        "numeric 값의 분포를 bin별 count, density, proportion으로 나누어 보여준다.",
        "x축 bin 범위, y축 단위, bin width, normalization, reference/current 색상, marker를 확인한다.",
        "중심 위치, mode 수, tail 두께, 빈 bin, 극단값 구간, reference/current 겹침 정도를 설명한다.",
        "bin 설정과 표본 수에 민감하므로 작은 요철을 과해석하지 않는다.",
    ),
    "matrix_view": (
        "feature, class, segment, state 간 쌍별 관계, 혼동행렬, 전이행렬, 비교행렬을 보여준다.",
        "행/열 의미, cell 단위, row-normalized/column-normalized 여부, 대각선 의미를 확인한다.",
        "대각선 집중도, off-diagonal 증가, 특정 행/열 편향, 비대칭성, reference/current 차이를 설명한다.",
        "normalization 방향과 class imbalance 없이 성능 저하나 drift를 확정하지 않는다.",
    ),
    "model_diagnostic_curve": (
        "ROC, PR, calibration, reliability curve 등 모델 또는 domain classifier의 진단 곡선을 보여준다.",
        "curve_type과 기준선의 의미를 확인한다. ROC 대각선과 calibration 대각선은 의미가 다르다.",
        "구분 가능성, trade-off, calibration 어긋남을 curve type에 맞게 설명한다.",
        "진단 곡선이 좋아 보인다는 이유로 운영 모델 안정성을 단정하지 않는다.",
    ),
    "p_value_view": (
        "통계 검정의 p-value를 feature, window, segment, test별로 보여준다.",
        "검정 종류, 단측/양측, alpha 기준선, log scale, adjusted p-value 여부를 확인한다.",
        "유의수준 아래인지, 여러 window에서 반복되는지, effect size와 같은 방향인지 설명한다.",
        "p-value는 효과 크기나 업무 영향 크기를 말하지 않는다.",
    ),
    "performance_metric_view": (
        "accuracy, AUC, F1, error rate, latency, confidence처럼 모델 운영 품질 또는 사용자 영향과 가까운 지표를 보여준다.",
        "높을수록 좋은 지표인지 낮을수록 좋은 지표인지, 목표선과 event marker를 확인한다.",
        "성능 저하 시작, 지속 시간, detector state나 분포 변화와 같은 시점인지, 대응 후 회복 여부를 설명한다.",
        "성능 저하만으로 데이터 drift 원인을 단정하지 않는다.",
    ),
    "projection_scatter": (
        "embedding, PCA, UMAP 등 고차원 표본을 2D 좌표로 투영해 군집, 겹침, 이동 방향을 보여준다.",
        "각 점이 sample/window인지, 색상/모양이 reference/current/class/outlier인지, centroid나 shift arrow가 있는지 확인한다.",
        "reference/current 겹침, centroid 이동, 군집 분리, outlier 증가, class별 이동 차이를 설명한다.",
        "2D projection 축 위치 자체를 업무 의미나 원인으로 해석하지 않는다.",
    ),
    "proportion_view": (
        "category, class, status, bin, segment의 구성비를 보여준다.",
        "비율인지 count인지, 전체 합이 100%로 정규화됐는지, reference/current 색상과 missing/other bucket을 확인한다.",
        "지배 category 변화, 소수 category 증가, class 비중 변화, count와 비율 변화의 차이를 설명한다.",
        "비율 변화만으로 실제 건수 증가나 성능 영향을 단정하지 않는다.",
    ),
    "quantile_view": (
        "분위수별 값을 비교해 분포의 어느 구간에서 차이가 나는지 보여준다.",
        "x축이 quantile probability인지 reference quantile인지, y축이 current 값인지 차이값인지 확인한다.",
        "중앙부 차이, 상위/하위 tail 차이, 대각선/zero line에서 벗어나는 구간을 설명한다.",
        "극단 분위는 표본 수와 clipping에 민감하므로 과도하게 단정하지 않는다.",
    ),
    "ranking_view": (
        "score, delta, contribution, frequency, risk 기준으로 항목 우선순위를 보여준다.",
        "순위 산정 값, 정렬 방향, 절댓값 기준인지 부호 보존인지, rank/value/delta를 확인한다.",
        "1위와 2위 이하의 격차, 상위권 집중도, 부호가 다른 항목, 이전 대비 급상승을 설명한다.",
        "ranking은 우선순위 표시이지 인과 증거가 아니다.",
    ),
    "raw_signal_trend": (
        "detector statistic으로 가공되기 전 원 관측값, 운영 metric, error stream의 시간 흐름을 보여준다.",
        "실선과 둥근 점이 원값인지 smoothing인지, 기준선/reference value와 event marker가 있는지 확인한다.",
        "일회성 spike, 평균 수준 이동, 분산 증가, 점진 추세, 회복 구간을 구분한다.",
        "원 신호만으로 원인을 단정하지 않고 detector나 성능 component와 연결한다.",
    ),
    "reference_current_comparison": (
        "기준 구간과 현재 구간의 값, 평균, 비율, score, 분포 요약을 나란히 비교한다.",
        "reference/current가 어떤 기간 또는 집단인지, 표시값이 mean/rate/delta/CI/count 중 무엇인지 확인한다.",
        "current가 reference보다 커졌는지 작아졌는지, CI 겹침과 표본 수 불균형을 설명한다.",
        "두 값 차이만으로 통계적 유의성을 단정하지 않는다.",
    ),
    "small_multiples": (
        "여러 feature, segment, metric의 작은 chart를 같은 배열로 보여줘 공통 패턴과 개별 차이를 비교한다.",
        "각 panel이 어떤 series인지, scale이 공유인지 개별인지, marker/baseline/threshold가 공통인지 확인한다.",
        "같은 시점의 동시 변화, 특정 panel만의 변화, 방향이 공통인지 반대인지 설명한다.",
        "개별 scale의 기울기를 직접 크기 차이로 비교하지 않는다.",
    ),
    "state_timeline": (
        "normal, warning, drift, alternate, replace, recovery 같은 상태가 시간에 따라 어떻게 전환되는지 구간형으로 보여준다.",
        "각 색상/라벨 의미, 구간 시작과 종료, 세로 event marker와의 관계를 확인한다.",
        "상태 전환 순서와 지속 시간을 읽고 성능 하락이나 구조 변화와 시간 순서로 연결한다.",
        "상태 색상만으로 원 신호 크기나 원인을 알 수 없다.",
    ),
    "threshold_line": (
        "판정 기준, 허용 한계, 목표값, alpha 기준, control limit를 그래프 위에 표시하는 보조 component다.",
        "점선/실선 색상과 label, 상한 초과가 문제인지 하한 미달이 문제인지 확인한다.",
        "데이터 series가 언제, 얼마나, 얼마나 오래 기준을 넘는지 겹쳐진 metric과 함께 말한다.",
        "임계값 초과는 정책/알고리즘 기준 통과이지 실제 장애 확정이 아니다.",
    ),
    "trend_line": (
        "시간, window, batch index처럼 순서가 있는 축에서 metric이 어떻게 움직이는지 보여준다.",
        "선 색상, 둥근 점 marker, event marker, threshold_line이 무엇을 의미하는지 확인한다.",
        "방향, 기울기, 변곡점, 회복 구간, event 전후 패턴 변화를 설명한다.",
        "선이 올라가거나 내려간 사실만으로 drift를 확정하지 않는다.",
    ),
    "uncertainty_band": (
        "추세선, 예측값, 평균 주변의 confidence interval, prediction interval, bootstrap band를 영역으로 표시한다.",
        "중앙선과 band 상/하한, confidence level, 관측점이 band 안팎 어디에 있는지 확인한다.",
        "band 밖 이탈이 일시적인지 지속적인지, band 자체가 넓어지는지 좁아지는지 설명한다.",
        "band 밖 이탈이 항상 drift는 아니다.",
    ),
    "window_view": (
        "reference window, current window, sliding window, adaptive window 같은 분석 구간을 명시한다.",
        "각 window의 시작/끝, reference/current 역할, overlap 여부, window size를 확인한다.",
        "metric 변화가 어떤 구간 정의 위에서 계산됐는지, 큰 window가 반응을 늦출 수 있음을 설명한다.",
        "window 경계를 실제 원인 발생 시점으로 단정하지 않는다.",
    ),
}


FAMILY_CONTEXTS = {
    "ADAPT": "adaptive drift 대응 chart다. 성능 metric, detector state, alternate/challenger 구조, replacement/retrain event의 시간 순서를 종합한다.",
    "ANNOT": "annotation 중심 chart다. 주석은 보조 설명이며 실제 수치와 그래프 근거에 맞는지 확인한다.",
    "ANOM": "이상치 chart다. point anomaly와 구간 drift를 구분하고 threshold/event와 연결한다.",
    "BOCD": "Bayesian online change point chart다. posterior, run length, change point candidate를 시간 순서로 설명한다.",
    "CAT": "범주형 drift chart다. category proportion, count, rare category, class/segment 구성 변화와 표본 수를 함께 본다.",
    "CLS": "classifier/domain classifier chart다. 분류 가능성과 운영 모델 성능을 구분한다.",
    "CTRL": "control chart 계열이다. 원 신호, 중심선, 관리한계, CUSUM/EWMA 누적 통계를 함께 읽는다.",
    "DIST": "분포 비교 chart다. reference/current의 중심, 폭, tail, overlap 변화를 설명한다.",
    "DISTSHAPE": "분포 형태 변화 chart다. 중심 이동보다 mode, skew, tail, spread 변화가 핵심인지 살핀다.",
    "EDF": "ECDF/CDF 기반 chart다. 두 누적곡선의 최대 간격, 방향, 값 구간을 중심으로 해석한다.",
    "ERR": "오류/성능 영향 chart다. error rate, class별 오류, warning timeline, threshold를 연결한다.",
    "EXPL": "설명/feature attribution chart다. feature importance와 contribution을 원인 확정이 아닌 후보 근거로 다룬다.",
    "GEN": "일반 drift chart다. 각 component 근거를 먼저 해석하고 종합 판단은 제한적으로 쓴다.",
    "HIST": "histogram 기반 chart다. bin, density/count, tail, observed marker를 중심으로 읽는다.",
    "MEAN": "평균 변화 chart다. reference/current mean, CI, 검정 결과, effect size를 함께 읽는다.",
    "MV": "다변량/representation drift chart다. projection, distance, contribution, feature별 변화가 같은 방향인지 본다.",
    "PROB": "확률/신뢰도 chart다. calibration, confidence, entropy, probability distribution 변화를 성능 영향과 분리한다.",
    "PSI": "PSI chart다. bin별 expected/current proportion과 contribution이 전체 PSI에 어떻게 누적되는지 설명한다.",
    "RANK": "순위 기반 chart다. 상위 후보 집중도와 순위 변화를 우선순위로 읽고 인과 단정은 피한다.",
    "REP": "representation chart다. embedding/projection/cluster/centroid 변화를 보고 원 고차원 해석 한계를 남긴다.",
    "STREAM": "stream monitoring chart다. 시간 순서, window, event, alarm, recovery를 중심으로 흐름을 설명한다.",
    "TEXT": "텍스트/LLM metric chart다. token length, refusal, embedding distance, semantic cluster 등 텍스트 특화 지표의 의미와 운영 영향을 구분한다.",
    "UNC": "불확실성 chart다. band/CI/PI 안팎의 위치와 반복 이탈을 중심으로 해석한다.",
    "VAR": "분산/산포 변화 chart다. 중심 이동과 분산 확대를 분리해 설명한다.",
}


ANALYSIS_CONTEXTS = {
    "metric_shift_cusum": (
        "이 chart는 특정 운영 metric이 기준 평균 주변에서 관리 가능한 범위에 있는지, 또는 기준 평균 대비 한 방향으로 누적 편차가 쌓여 drift 후보가 되는지 해석한다.",
        "summary/decision에서 metric, 기준 평균, control limit를 확인하고 raw_signal_trend에서 실제 관측점이 기준 평균 위/아래 어디에 오래 머무는지 읽는다. control_chart에서는 C+와 C- 중 어느 누적선이 커지고 control limit를 넘는지 설명한다. raw 방향과 CUSUM 방향이 일치할 때만 상방/하방 평균 이동 후보로 말한다.",
        "raw 값이 기준 평균 위에 지속되고 C+가 control limit를 넘으며 C-는 작다면 상방 평균 이동 기반 drift 후보로 해석한다.",
        "CUSUM 선이 높으므로 장애가 확정됐다.",
    ),
    "embedding_distribution_shift": (
        "이 chart는 기준 embedding과 현재 embedding이 2D projection, 거리 지표, 분포/cluster 요약에서 얼마나 분리되는지 해석한다.",
        "projection_scatter에서 reference/current 점 색상, centroid, 이동 방향, overlap 정도를 먼저 설명한다. distance_metric_view나 distribution component가 projection에서 보인 분리를 지지하는지 확인하고, contribution/ranking/table은 원인이 아니라 우선 점검 후보로만 쓴다.",
        "current 점군이 reference 중심에서 같은 방향으로 떨어지고 distance metric도 증가한다면 representation 분포 이동 후보로 읽는다.",
        "산점도에서 오른쪽에 있으므로 나쁜 데이터다.",
    ),
    "adaptive_metric_trend": (
        "이 chart는 streaming model이 성능 저하를 감지하고 warning, alternate/challenger 성장, replacement/retrain 같은 적응 절차로 대응했는지 해석한다.",
        "performance_metric_view에서 성능선, 관측점, event marker를 읽고 하락/회복 구간과 값을 설명한다. state_timeline에서 normal, warning, alternate, replace/recovery 상태의 시작과 지속 기간을 설명한다. adaptive_model_structure_view에서 alternate/challenger 구조가 언제 성장하고 replacement 시점에 어떻게 바뀌는지 연결한다.",
        "accuracy가 warning 이후 하락하고, state가 warning에서 alternate로 전환되며, alternate tree가 성장한 뒤 replacement 이후 accuracy가 회복되면 adaptive drift 대응 후보로 해석한다.",
        "replacement가 있으므로 drift 원인은 해결됐다.",
    ),
}


SPECIAL_CHARTS = {
    "CHART-ADAPT-001": (
        "CHART-ADAPT-001은 HAT 또는 adaptive model의 성능 저하 감지, alternate tree 성장, replacement 이후 회복 흐름을 한 화면에서 종합하는 chart다.",
        "online accuracy/performance metric에서는 선, 둥근 점, 붉은 event marker가 보여주는 하락과 회복 구간을 수치로 설명한다. detector state timeline에서는 normal, warning, alternate, replace 구간의 순서와 지속 시간을 설명한다. tree size/adaptive structure에서는 main tree와 alternate tree node 수가 replacement 전후 어떻게 바뀌는지 설명한다. 전체 해석은 성능 하락, 상태 전환, 대체 구조 성장, replacement, 회복이 실제 시간 순서로 연결되는지를 판단한다.",
        "accuracy 하락, warning/alternate/replace 전환, alternate tree 성장과 replacement 이후 회복이 같은 시간 흐름으로 이어지면 HAT adaptive drift 대응 후보로 해석한다.",
        "세 패널이 있으므로 HAT가 drift를 해결했다.",
    ),
    "CHART-CTRL-001": (
        "CHART-CTRL-001은 metric 원 신호와 누적 편차/control limit를 함께 읽어 기준 평균 대비 지속적인 평균 이동 후보를 판독하는 chart다.",
        "summary/decision card에서 metric 이름, 기준 평균, control limit, dominant direction을 확인한다. raw signal trend에서는 관측점과 선이 기준 평균 위/아래 어디에 머무는지, event marker 전후 값이 어떻게 움직이는지 설명한다. CUSUM/control chart에서는 C+와 C- 중 어느 쪽이 누적되고 control limit를 넘는지 설명한다. raw signal 방향과 CUSUM 누적 방향이 일치해야 강한 후보로 말한다.",
        "raw 값이 기준 평균보다 높은 쪽에 지속되고 C+가 control limit를 넘으면 상방 평균 이동 기반 drift 후보로 설명한다.",
        "C+가 높으므로 장애가 발생했다.",
    ),
    "CHART-MV-002": (
        "CHART-MV-002는 embedding/reference-current 분포 이동을 projection, 거리, 분포 요약 또는 contribution 근거로 종합하는 chart다.",
        "projection scatter에서는 점 색상, centroid, overlap, shift arrow를 설명한다. distance/distribution view에서는 reference/current 차이가 거리나 분포 모양에서도 보이는지 설명한다. contribution/ranking/table이 있으면 차이를 키우는 feature/segment/token 후보를 우선순위로만 말한다. projection 분리와 거리/분포 지표가 같은 방향이면 representation drift 후보로 말한다.",
        "current embedding 점군이 reference에서 떨어지고 거리 지표도 커지면 embedding 분포 이동 후보로 읽는다.",
        "산점도에서 떨어졌으니 원인이 확정됐다.",
    ),
}


def component_context(code: str, role: str, read: str, pattern: str, caution: str) -> str:
    return f"""## 역할
{role}

## 먼저 읽을 요소
{read}

## 해석 방법
{pattern}

## 단정 금지
{caution}

## 공통 지침
LLM은 component 이름을 번역하는 데서 멈추지 말고, payload의 title, visualEncodingHint, dataSample, machineObservation을 근거로 실제 화면에 보이는 선, 점, 막대, 영역, 색상, 점선, marker, 구간과 값을 설명한다. 현재 payload에 없는 숫자나 원인은 만들지 않는다."""


def chart_context(code: str, family: str, title: str, purpose: str, summary: str) -> tuple[str, str, str]:
    if code in SPECIAL_CHARTS:
        goal, method, good, bad = SPECIAL_CHARTS[code]
    else:
        family_text = FAMILY_CONTEXTS.get(family or "", FAMILY_CONTEXTS["GEN"])
        goal = f"{code}는 {family_text}"
        method = f"""표시 제목은 '{title or code}'이다. 목적 설명은 '{purpose or 'DB metadata 없음'}'이고 component 요약은 '{summary or 'payload components 기준 해석'}'이다. LLM은 먼저 chart payload의 analysisContext와 visible title을 읽고, 각 component note에서 축, 색상, 점/선/막대/영역/점선/marker 같은 시각 부호와 실제 수치를 설명해야 한다. 전체 해석에서는 component별 결론을 단순 반복하지 말고, 서로 보강하거나 반박하는 근거를 시간 순서 또는 reference/current 비교 구조로 연결한다."""
        good = f"{code} 전체 해석은 각 component가 실제로 보여준 값과 시각 요소를 먼저 설명한 뒤, {family or 'GEN'} 계열 판단 근거가 서로 같은 방향인지 종합한다."
        bad = f"{code}는 {family or 'GEN'} chart이므로 drift가 발생했다처럼 component 근거 없이 결론부터 쓴다."
    context = f"""## chart 해석 목표
{goal}

## 종합 지침
{method}

## 출력 품질 기준
요약은 한 문장으로 현재 데이터의 핵심 판단을 말한다. detail은 '무엇을 먼저 봐야 하는가', '각 component가 실제로 보이는 값과 시각 요소', 'component들을 함께 읽었을 때의 판단', '단정하면 안 되는 것'을 구분해 쓴다. chart id나 component 이름만 반복하지 않고, rule 기반 고정 문장을 채우지 않는다."""
    return context, good, bad


def upsert_guides() -> None:
    with psycopg.connect(
        host=os.environ.get("DRIFT_DB_HOST", "127.0.0.1"),
        port=int(os.environ.get("DRIFT_DB_PORT", "5432")),
        dbname=os.environ.get("DRIFT_DB_NAME", "drift_monitoring"),
        user=os.environ.get("DRIFT_DB_USER", "postgres"),
        password=os.environ.get("DRIFT_DB_PASSWORD", os.environ.get("POSTGRES_PASSWORD", "postgres")),
        autocommit=True,
    ) as conn:
        with conn.cursor() as cur:
            cur.execute("select component_code from chart_component order by component_code")
            known = {row[0] for row in cur.fetchall()}
            missing = sorted(known - set(COMPONENT_GUIDES))
            if missing:
                raise RuntimeError("missing component guides: " + ", ".join(missing))

            for code, (role, read, pattern, caution) in COMPONENT_GUIDES.items():
                context = component_context(code, role, read, pattern, caution)
                good = f"{code} 해석은 먼저 화면 요소와 실제 값을 설명한 뒤, 그 패턴이 drift 판단에서 어떤 후보 근거인지 제한적으로 말한다."
                bad = f"{code}가 보이므로 drift가 확정됐다고 component 이름만 근거로 결론을 낸다."
                cur.execute(
                    """
                    insert into llm_component_interpretation_context
                    (component_code, context_markdown, example_good, example_bad, version, created_at, updated_at)
                    values (%s,%s,%s,%s,3,now(),now())
                    on conflict (component_code) do update set
                        context_markdown=excluded.context_markdown,
                        example_good=excluded.example_good,
                        example_bad=excluded.example_bad,
                        version=excluded.version,
                        updated_at=now()
                    """,
                    (code, context, good, bad),
                )

            for key, (goal, method, good, bad) in ANALYSIS_CONTEXTS.items():
                context = f"""## 분석유형 해석 목표
{goal}

## 종합 지침
{method}

## 단정 금지
component별 근거가 서로 같은 방향인지 확인하기 전에는 drift 확정, 원인 확정, 대응 성공 확정을 말하지 않는다."""
                cur.execute(
                    """
                    insert into llm_chart_interpretation_context
                    (context_key, applies_to, context_markdown, example_good, example_bad, version, created_at, updated_at)
                    values (%s,'analysisKind',%s,%s,%s,3,now(),now())
                    on conflict (context_key) do update set
                        applies_to=excluded.applies_to,
                        context_markdown=excluded.context_markdown,
                        example_good=excluded.example_good,
                        example_bad=excluded.example_bad,
                        version=excluded.version,
                        updated_at=now()
                    """,
                    (key, context, good, bad),
                )

            cur.execute(
                "select chart_code, chart_family, display_title, purpose_text, component_summary_text from chart_definition order by chart_code"
            )
            for code, family, title, purpose, summary in cur.fetchall():
                context, good, bad = chart_context(code, family or "", title or "", purpose or "", summary or "")
                cur.execute(
                    """
                    insert into llm_chart_interpretation_context
                    (context_key, applies_to, context_markdown, example_good, example_bad, version, created_at, updated_at)
                    values (%s,'chart_code',%s,%s,%s,3,now(),now())
                    on conflict (context_key) do update set
                        applies_to=excluded.applies_to,
                        context_markdown=excluded.context_markdown,
                        example_good=excluded.example_good,
                        example_bad=excluded.example_bad,
                        version=excluded.version,
                        updated_at=now()
                    """,
                    (code, context, good, bad),
                )

            cur.execute("select count(*), min(version), max(version) from llm_component_interpretation_context")
            print("component_contexts", cur.fetchone())
            cur.execute("select count(*), min(version), max(version) from llm_chart_interpretation_context")
            print("chart_contexts", cur.fetchone())


if __name__ == "__main__":
    upsert_guides()
