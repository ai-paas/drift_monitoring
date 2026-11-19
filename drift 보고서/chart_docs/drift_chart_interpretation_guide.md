# Drift Chart Interpretation Guide

이 문서는 생성된 drift chart 이미지와 해석 문서의 인덱스다. 세부 해석은 chart family별 문서에 나누어 관리한다.

차트 설명을 작성하거나 수정할 때는 먼저 `drift_chart_explanation_authoring_guide.md`의 기준을 따른다. 차트 설명은 chart id 용도 요약이 아니라 실제 화면의 패널, 예시 데이터, 상태 전환, 해석 한계를 사람이 이해할 수 있게 설명해야 한다.

## 문서 구성

| chart family | 해석 문서 | 포함 chart id |
|---|---|---|
| EDF 계열 | `drift_chart_interpretation_edf.md` | `CHART-EDF-001` ~ `CHART-EDF-004` |
| Rank 계열 | `drift_chart_interpretation_rank.md` | `CHART-RANK-001` |
| Distance 계열 | `drift_chart_interpretation_dist.md` | `CHART-DIST-001` |
| Probability 계열 | `drift_chart_interpretation_prob.md` | `CHART-PROB-001` ~ `CHART-PROB-003` |
| Histogram 계열 | `drift_chart_interpretation_hist.md` | `CHART-HIST-001` |
| Category 계열 | `drift_chart_interpretation_cat.md` | `CHART-CAT-001` ~ `CHART-CAT-004` |
| PSI 계열 | `drift_chart_interpretation_psi.md` | `CHART-PSI-001` |
| Mean 계열 | `drift_chart_interpretation_mean.md` | `CHART-MEAN-001` |
| Variance 계열 | `drift_chart_interpretation_var.md` | `CHART-VAR-001` |
| Distribution Shape 계열 | `drift_chart_interpretation_distshape.md` | `CHART-DISTSHAPE-001` |
| Multivariate 계열 | `drift_chart_interpretation_mv.md` | `CHART-MV-001` ~ `CHART-MV-005` |
| Stream 계열 | `drift_chart_interpretation_stream.md` | `CHART-STREAM-001` ~ `CHART-STREAM-005` |
| Control Chart 계열 | `drift_chart_interpretation_ctrl.md` | `CHART-CTRL-001` ~ `CHART-CTRL-003` |
| BOCD 계열 | `drift_chart_interpretation_bocd.md` | `CHART-BOCD-001` |
| Error Rate Detector 계열 | `drift_chart_interpretation_err.md` | `CHART-ERR-001` ~ `CHART-ERR-006` |
| Anomaly / Novelty 계열 | `drift_chart_interpretation_anom.md` | `CHART-ANOM-001` |
| Representation Drift 계열 | `drift_chart_interpretation_rep.md` | `CHART-REP-001` ~ `CHART-REP-003` |
| Text Drift 계열 | `drift_chart_interpretation_text.md` | `CHART-TEXT-001` ~ `CHART-TEXT-002` |
| Classifier-based Drift 계열 | `drift_chart_interpretation_cls.md` | `CHART-CLS-001` |
| Model Uncertainty 계열 | `drift_chart_interpretation_unc.md` | `CHART-UNC-001` |
| Explainability Drift 계열 | `drift_chart_interpretation_expl.md` | `CHART-EXPL-001` ~ `CHART-EXPL-002` |
| Adaptive Model 계열 | `drift_chart_interpretation_adapt.md` | `CHART-ADAPT-001` ~ `CHART-ADAPT-002` |
| Annotation 계열 | `drift_chart_interpretation_annot.md` | `CHART-ANNOT-001` ~ `CHART-ANNOT-002` |
| Generic / Fallback 계열 | `drift_chart_interpretation_gen.md` | `CHART-GEN-001` |

## 추가 작성 원칙

새 chart 해석은 `chart id`의 family에 맞는 문서에 추가한다.

```text
CHART-EDF-*    -> drift_chart_interpretation_edf.md
CHART-RANK-*   -> drift_chart_interpretation_rank.md
CHART-DIST-*   -> drift_chart_interpretation_dist.md
CHART-PROB-*   -> drift_chart_interpretation_prob.md
CHART-HIST-*   -> drift_chart_interpretation_hist.md
CHART-CAT-*    -> drift_chart_interpretation_cat.md
CHART-PSI-*    -> drift_chart_interpretation_psi.md
CHART-MEAN-*   -> drift_chart_interpretation_mean.md
CHART-VAR-*    -> drift_chart_interpretation_var.md
CHART-DISTSHAPE-* -> drift_chart_interpretation_distshape.md
CHART-MV-*     -> drift_chart_interpretation_mv.md
CHART-STREAM-* -> drift_chart_interpretation_stream.md
CHART-CTRL-*   -> drift_chart_interpretation_ctrl.md
CHART-BOCD-*   -> drift_chart_interpretation_bocd.md
CHART-ERR-*    -> drift_chart_interpretation_err.md
CHART-ANOM-*   -> drift_chart_interpretation_anom.md
CHART-REP-*    -> drift_chart_interpretation_rep.md
CHART-TEXT-*   -> drift_chart_interpretation_text.md
CHART-CLS-*    -> drift_chart_interpretation_cls.md
CHART-UNC-*    -> drift_chart_interpretation_unc.md
CHART-EXPL-*   -> drift_chart_interpretation_expl.md
CHART-ANNOT-*  -> drift_chart_interpretation_annot.md
CHART-GEN-*    -> drift_chart_interpretation_gen.md
```

각 chart 섹션은 다음 구조를 유지한다.

1. 이미지
2. 차트 목적
3. 차트 구성
4. 해석 순서
5. Drift 후보 판단 기준
6. 예시 차트의 해석
7. 금지해야 할 해석
8. 추가 확인 항목
9. 적합한 사용 대상
