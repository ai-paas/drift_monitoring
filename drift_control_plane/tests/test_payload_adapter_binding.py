from __future__ import annotations

import pytest

from drift_server.app.payload_adapter import PayloadBindingError, build_payload, get_binding_spec
from drift_server.app.drift.payload_registry import get_payload_adapter


def _context() -> dict:
    return {
        "source": {"sourceId": "case-010"},
        "feature": {"featureId": "metric", "featureLabel": "Metric"},
        "assignment": {"runtimeMethodKey": "adwin_mean_stream"},
        "methodRun": {"methodRunId": "run-001"},
        "driftEvent": {
            "eventId": "event-001",
            "eventStart": "2026-01-01T00:10:00Z",
            "eventEnd": "2026-01-01T00:20:00Z",
            "level": "drift",
            "score": 3.25,
        },
        "runtimeResult": {
            "metrics": {"meanDifference": 2.5},
            "diagnostics": {"bucketCount": 2},
            "payloadHints": {"preferredChartId": "CHART-STREAM-001"},
        },
        "analysisChart": {
            "chartId": "CHART-STREAM-001",
            "payloadAdapterKey": "adwin_mean_stream_to_chart_stream_001",
        },
        "buckets": [
            {
                "bucketStart": "2026-01-01T00:00:00Z",
                "bucketEnd": "2026-01-01T00:10:00Z",
                "v": 10.0,
                "count": 12,
                "status": "ok",
            },
            {
                "bucketStart": "2026-01-01T00:10:00Z",
                "bucketEnd": "2026-01-01T00:20:00Z",
                "v": 13.5,
                "count": 12,
                "status": "ok",
            },
        ],
    }


def _psi_context() -> dict:
    return {
        "source": {"sourceId": "case-004-psi"},
        "feature": {"featureId": "score", "featureLabel": "Score"},
        "assignment": {"runtimeMethodKey": "psi_numeric_binned"},
        "methodRun": {"methodRunId": "psi-run-001"},
        "driftEvent": {
            "eventId": "psi-event-001",
            "eventStart": "2026-06-30T23:00:00Z",
            "eventEnd": "2026-07-01T01:00:00Z",
            "level": "drift",
            "score": 3.9537504460814215,
        },
        "runtimeResult": {
            "metrics": {
                "measurements": {
                    "THRESHOLD": 0.1,
                    "PSI_CONTRIBUTION": [
                        {
                            "category": "bin_0",
                            "reference_proportion": 0.2,
                            "current_proportion": 0.0,
                            "psi_contribution": 2.4412025230444954,
                        },
                        {
                            "category": "bin_4",
                            "reference_proportion": 0.2,
                            "current_proportion": 0.8333333333333334,
                            "psi_contribution": 0.9038385359774682,
                        },
                    ],
                    "CATEGORY_COUNTS_REFERENCE": {"bin_0": 12.0, "bin_4": 12.0},
                    "CATEGORY_COUNTS_CURRENT": {"bin_0": 0.0, "bin_4": 50.0},
                    "REFERENCE_SAMPLE_SIZE": 60.0,
                    "CURRENT_SAMPLE_SIZE": 60.0,
                }
            }
        },
        "analysisChart": {
            "chartId": "CHART-PSI-001",
            "payloadAdapterKey": "auto__NUMERIC_BINNED_PSI__CHART-PSI-001",
        },
        "buckets": [],
    }


def _hddm_context() -> dict:
    return {
        "source": {"sourceId": "case-012-dataset"},
        "feature": {"featureId": "error_rate", "featureLabel": "Error rate"},
        "assignment": {"runtimeMethodKey": "hddm_a_error_rate_stream"},
        "methodRun": {"methodRunId": "hddm-run-001"},
        "driftEvent": {
            "eventId": "hddm-event-001",
            "eventStart": "2026-07-19T00:00:00Z",
            "eventEnd": "2026-07-20T00:00:00Z",
            "level": "drift",
            "score": 0.021068340429267435,
        },
        "runtimeResult": {
            "metrics": {
                "threshold": 0.020459085784779882,
                "testStatistic": 0.021068340429267435,
                "measurements": {
                    "TEST_STATISTIC": 0.021068340429267435,
                    "DRIFT_CONFIDENCE": 0.002,
                    "WARNING_CONFIDENCE": 0.01,
                    "HOEFFDING_WARNING_BOUND": 0.017611737031632952,
                    "HOEFFDING_DRIFT_BOUND": 0.020459085784779882,
                    "WARNING_START_INDEX": 180,
                    "DRIFT_INDEX": 240,
                    "PROCESSED_COUNT": 300,
                }
            }
        },
        "analysisChart": {
            "chartId": "CHART-ERR-005",
            "payloadAdapterKey": "auto__HDDM_A_HOEFFDING_BOUND__CHART-ERR-005",
        },
        "buckets": [
            {
                "bucketStart": "2026-07-17T00:00:00Z",
                "bucketEnd": "2026-07-18T00:00:00Z",
                "v": 0.04,
                "errorRate": 0.04,
                "count": 120,
                "status": "ok",
            },
            {
                "bucketStart": "2026-07-18T00:00:00Z",
                "bucketEnd": "2026-07-19T00:00:00Z",
                "v": 0.08,
                "errorRate": 0.08,
                "count": 120,
                "status": "ok",
            },
            {
                "bucketStart": "2026-07-19T00:00:00Z",
                "bucketEnd": "2026-07-20T00:00:00Z",
                "v": 0.24,
                "errorRate": 0.24,
                "count": 120,
                "status": "ok",
            },
        ],
    }


def _ddm_err001_context() -> dict:
    return {
        "source": {"sourceId": "case-011-dataset"},
        "feature": {"featureId": "error_rate", "featureLabel": "Error rate"},
        "assignment": {
            "runtimeMethodKey": "ddm_error_rate_stream",
            "params": {"errorRateShiftThreshold": 0.12},
        },
        "methodRun": {"methodRunId": "ddm-run-001"},
        "driftEvent": {
            "eventId": "ddm-event-001",
            "eventStart": "2026-06-30T22:20:00Z",
            "eventEnd": "2026-06-30T22:30:00Z",
            "level": "drift",
            "score": 0.3,
        },
        "runtimeResult": {"metrics": {"threshold": 0.12}},
        "analysisChart": {
            "chartId": "CHART-ERR-001",
            "payloadAdapterKey": "auto__DDM_STANDARD__CHART-ERR-001",
        },
        "buckets": [
            {
                "bucketStart": "2026-06-30T22:00:00Z",
                "bucketEnd": "2026-06-30T22:10:00Z",
                "v": 0.02,
                "errorRate": 0.02,
                "count": 10,
                "status": "ok",
            },
            {
                "bucketStart": "2026-06-30T22:10:00Z",
                "bucketEnd": "2026-06-30T22:20:00Z",
                "v": 0.05,
                "errorRate": 0.05,
                "count": 10,
                "status": "ok",
            },
            {
                "bucketStart": "2026-06-30T22:20:00Z",
                "bucketEnd": "2026-06-30T22:30:00Z",
                "v": 0.35,
                "errorRate": 0.35,
                "count": 10,
                "status": "ok",
            },
            {
                "bucketStart": "2026-06-30T22:30:00Z",
                "bucketEnd": "2026-06-30T22:40:00Z",
                "v": 0.32,
                "errorRate": 0.32,
                "count": 10,
                "status": "ok",
            },
        ],
    }


def _seqdrift_context() -> dict:
    values = [
        {"period": "reference", "value": 0.0 + (index % 5) * 0.01}
        for index in range(160)
    ] + [
        {"period": "current", "value": 1.0 + (index % 5) * 0.01}
        for index in range(80)
    ]
    return {
        "source": {"sourceId": "case-013-seqdrift1-stream004"},
        "feature": {"featureId": "score", "featureLabel": "Score"},
        "assignment": {"runtimeMethodKey": "seqdrift_numeric_window"},
        "methodRun": {"methodRunId": "seqdrift-run-001"},
        "driftEvent": {
            "eventId": "event:assign-case013-seqdrift1-stream004:case-013-seqdrift1-stream004:score:2026-11-01T00:00:00Z:2026-11-01T04:00:00Z",
            "eventStart": "2026-11-01T00:00:00Z",
            "eventEnd": "2026-11-01T04:00:00Z",
            "level": "drift",
            "score": 0.3313853667451706,
        },
        "runtimeResult": {
            "metrics": {
                "statistic": 0.3313853667451706,
                "threshold": 0.6686146332548298,
                "testStatistic": 1.0000000000000004,
                "measurements": {
                    "DRIFT_ALARM_STATE": "drift_detected",
                    "SEQUENTIAL_BOUND": 0.6686146332548298,
                    "TEST_STATISTIC": 1.0000000000000004,
                    "DRIFT_SCORE": 0.3313853667451706,
                    "MAX_EVIDENCE": 1.0000000000000004,
                    "MAX_MARGIN": 0.3313853667451706,
                    "LAST_EVIDENCE": 1.0000000000000004,
                    "LAST_BOUND": 0.6686146332548298,
                    "REFERENCE_MEAN": 0.02,
                    "CURRENT_MEAN": 1.02,
                    "MEAN_DELTA": 1.0,
                    "ALARM_COUNT": 3,
                    "FIRST_ALARM_INDEX": 39,
                    "LAST_ALARM_INDEX": 79,
                    "PROCESSED_COUNT": 240,
                    "SAMPLE_SIZE_REFERENCE": 160,
                    "SAMPLE_SIZE_CURRENT": 80,
                    "METHOD_POLICY": {
                        "variant": "SEQDRIFT1",
                        "bound_type": "hoeffding",
                    },
                    "ALARM_EVENTS": [
                        {
                            "time": "2026-11-01T03:19:00",
                            "index": 39,
                            "evidence": 1.0,
                            "sequential_bound": 0.8631777798755118,
                        },
                        {
                            "time": "2026-11-01T03:39:00",
                            "index": 59,
                            "evidence": 1.0000000000000002,
                            "sequential_bound": 0.7391812892824509,
                        },
                        {
                            "time": "2026-11-01T03:59:00",
                            "index": 79,
                            "evidence": 1.0000000000000004,
                            "sequential_bound": 0.6686146332548298,
                        },
                    ],
                },
            }
        },
        "analysisChart": {
            "chartId": "CHART-STREAM-004",
            "payloadAdapterKey": "auto__SEQDRIFT1__CHART-STREAM-004",
        },
        "buckets": [
            {
                "bucketStart": "2026-11-01T00:00:00Z",
                "bucketEnd": "2026-11-01T04:00:00Z",
                "v": 0.3313853667451706,
                "payload": {"values": values},
            }
        ],
    }


def _text001_topic_context() -> dict:
    return {
        "source": {"sourceId": "case-013-dataset"},
        "feature": {"featureId": "multivariate", "featureLabel": "Multivariate"},
        "assignment": {"runtimeMethodKey": "topic_distribution_shift"},
        "methodRun": {"methodRunId": "topic-run-001"},
        "driftEvent": {
            "eventId": "event:assign-case013-topic",
            "eventStart": "2026-06-30T22:00:00Z",
            "eventEnd": "2026-07-01T02:00:00Z",
            "level": "drift",
            "score": 0.2959335225728409,
        },
        "runtimeResult": {
            "metrics": {
                "statistic": 0.2959335225728409,
                "threshold": 0.1,
                "testStatistic": 0.2959335225728409,
                "measurements": {
                    "TEST_STATISTIC": 0.2959335225728409,
                    "DRIFT_ALARM_STATE": "drift_detected",
                    "THRESHOLD": 0.1,
                    "METHOD_POLICY": "topic_distribution_jensen_shannon_distance",
                    "JENSEN_SHANNON_DISTANCE": 0.2959335225728409,
                    "TOPIC_PROPORTION_DELTA": 0.24166666666666664,
                    "TOPIC_PROPORTIONS_REFERENCE": {
                        "billing": 0.09166666666666666,
                        "delivery": 0.2,
                        "login": 0.175,
                        "refund": 0.23333333333333334,
                        "technical": 0.3,
                    },
                    "TOPIC_PROPORTIONS_CURRENT": {
                        "billing": 0.2833333333333333,
                        "delivery": 0.20833333333333334,
                        "login": 0.31666666666666665,
                        "refund": 0.13333333333333333,
                        "technical": 0.058333333333333334,
                    },
                    "SAMPLE_SIZE_REFERENCE": 120,
                    "SAMPLE_SIZE_CURRENT": 120,
                    "PROCESSED_COUNT": 240,
                },
            }
        },
        "analysisChart": {
            "chartId": "CHART-TEXT-001",
            "payloadAdapterKey": "auto__TOPIC_DISTRIBUTION_SHIFT__CHART-TEXT-001",
        },
        "buckets": [
            {
                "bucketStart": "2026-06-30T22:00:00Z",
                "bucketEnd": "2026-07-01T02:00:00Z",
                "v": 0.2959335225728409,
                "payload": {"values": []},
            }
        ],
    }


def _wasserstein_distribution_context() -> dict:
    reference = [-1.3, -1.1, -0.8, -0.5, -0.2, 0.0, 0.2, 0.4, 0.7, 1.0]
    current = [-0.4, -0.1, 0.1, 0.4, 0.7, 0.9, 1.1, 1.4, 1.6, 1.9]
    values = [
        {"period": "reference", "value": value}
        for value in reference
    ] + [
        {"period": "current", "value": value}
        for value in current
    ]
    return {
        "source": {"sourceId": "case-001"},
        "feature": {"featureId": "score", "featureLabel": "Metric"},
        "assignment": {"runtimeMethodKey": "wasserstein_numeric_window"},
        "methodRun": {"methodRunId": "wasserstein-run-001"},
        "driftEvent": {
            "eventId": "event:assign-case001-wasserstein:case-001:score:2026-06-30T23:00:00Z:2026-07-01T01:00:00Z",
            "eventStart": "2026-06-30T23:00:00Z",
            "eventEnd": "2026-07-01T01:00:00Z",
            "level": "drift",
            "score": 0.535,
        },
        "runtimeResult": {
            "metrics": {
                "distance": 0.535,
                "threshold": 0.3,
                "measurements": {
                    "WASSERSTEIN_DISTANCE": 0.535,
                    "SAMPLE_SIZE_REFERENCE": len(reference),
                    "SAMPLE_SIZE_CURRENT": len(current),
                },
            }
        },
        "analysisChart": {
            "chartId": "CHART-DIST-001",
            "payloadAdapterKey": "auto__WASSERSTEIN_1D_EXACT__CHART-DIST-001",
        },
        "buckets": [
            {
                "bucketStart": "2026-06-30T23:00:00Z",
                "bucketEnd": "2026-07-01T01:00:00Z",
                "v": 0.535,
                "payload": {"values": values},
            }
        ],
    }


def _distshape_context() -> dict:
    reference = [-2.2, -1.7, -1.1, -0.4, 0.0, 0.3, 0.8, 1.2, 1.7, 2.0]
    current = [-8.0, -4.5, -1.6, -0.8, 0.4, 1.2, 2.5, 4.7, 8.5, 13.0]
    values = [
        {"period": "reference", "value": value}
        for value in reference
    ] + [
        {"period": "current", "value": value}
        for value in current
    ]
    return {
        "source": {"sourceId": "case-002"},
        "feature": {"featureId": "score", "featureLabel": "Score"},
        "assignment": {"runtimeMethodKey": "generic_distribution_ecdf_window"},
        "methodRun": {"methodRunId": "distshape-run-001"},
        "driftEvent": {
            "eventId": "event:assign-case002-distshape:score:2026-09-01T00:00:00Z:2026-09-02T00:00:00Z",
            "eventStart": "2026-09-01T00:00:00Z",
            "eventEnd": "2026-09-02T00:00:00Z",
            "level": "drift",
            "score": 89.98390718278196,
        },
        "runtimeResult": {
            "metrics": {
                "measurements": {
                    "EPPS_SINGLETON_STATISTIC": 89.98390718278196,
                    "TEST_STATISTIC": 89.98390718278196,
                    "P_VALUE": 1.32716e-18,
                    "SAMPLE_SIZE_REFERENCE": len(reference),
                    "SAMPLE_SIZE_CURRENT": len(current),
                    "T_POINTS": [0.4, 0.8],
                }
            }
        },
        "analysisChart": {
            "chartId": "CHART-DISTSHAPE-001",
            "payloadAdapterKey": "auto__TWO_SAMPLE_EPPS_SINGLETON__CHART-DISTSHAPE-001",
        },
        "buckets": [
            {
                "bucketStart": "2026-09-01T00:00:00Z",
                "bucketEnd": "2026-09-02T00:00:00Z",
                "v": 89.98390718278196,
                "payload": {"values": values},
            }
        ],
    }


def _expl001_importance_context() -> dict:
    return {
        "source": {"sourceId": "case-014-dataset"},
        "feature": {"featureId": "multivariate", "featureLabel": "Multivariate"},
        "assignment": {"runtimeMethodKey": "global_importance_rank_shift", "methodVariantKey": "GLOBAL_IMPORTANCE_RANK_SHIFT"},
        "methodRun": {"methodRunId": "expl-run-001"},
        "driftEvent": {
            "eventId": "event:assign-case014-expl",
            "eventStart": "2026-06-30T22:00:00Z",
            "eventEnd": "2026-07-01T02:00:00Z",
            "level": "drift",
            "score": 0.6666666666666666,
        },
        "runtimeResult": {
            "metrics": {
                "testStatistic": 0.6666666666666666,
                "threshold": 0.4,
                "measurements": {
                    "SHAP_DRIFT_DISTANCE": 0.6666666666666666,
                    "TEST_STATISTIC": 0.6666666666666666,
                    "THRESHOLD": 0.4,
                    "METHOD_POLICY": "mean_normalized_absolute_rank_delta",
                    "FEATURE_IMPORTANCE_OR_RANK": [
                        {
                            "feature": "importance_a",
                            "rank": 1,
                            "reference_rank": 1,
                            "current_rank": 3,
                            "rank_delta": 2,
                            "score": 1.0,
                            "reference_importance": 0.45042451666666666,
                            "current_importance": 0.19706475,
                            "importance_delta": -0.25335976666666665,
                        },
                        {
                            "feature": "importance_b",
                            "rank": 2,
                            "reference_rank": 3,
                            "current_rank": 1,
                            "rank_delta": -2,
                            "score": 1.0,
                            "reference_importance": 0.25299554166666666,
                            "current_importance": 0.5390002083333333,
                            "importance_delta": 0.28600466666666663,
                        },
                        {
                            "feature": "importance_c",
                            "rank": 3,
                            "reference_rank": 2,
                            "current_rank": 2,
                            "rank_delta": 0,
                            "score": 0.0,
                            "reference_importance": 0.29657991666666667,
                            "current_importance": 0.263935,
                            "importance_delta": -0.03264491666666669,
                        },
                    ],
                    "REFERENCE_SAMPLE_SIZE": 120,
                    "CURRENT_SAMPLE_SIZE": 120,
                    "SAMPLE_SIZE": {"reference": 120, "current": 120},
                    "FEATURE_DIMENSION": 3,
                    "FEATURE_COLUMNS": ["importance_a", "importance_b", "importance_c"],
                    "PROCESSED_COUNT": 240,
                },
            }
        },
        "analysisChart": {
            "chartId": "CHART-EXPL-001",
            "payloadAdapterKey": "auto__GLOBAL_IMPORTANCE_RANK_SHIFT__CHART-EXPL-001",
        },
        "buckets": [
            {
                "bucketStart": "2026-06-30T22:00:00Z",
                "bucketEnd": "2026-07-01T02:00:00Z",
                "v": 0.6666666666666666,
                "payload": {"values": []},
            }
        ],
    }


def _unc001_entropy_context() -> dict:
    return {
        "source": {"sourceId": "case-015-dataset"},
        "feature": {"featureId": "multivariate", "featureLabel": "Multivariate"},
        "assignment": {"runtimeMethodKey": "entropy_drift", "methodVariantKey": "ENTROPY_DRIFT"},
        "methodRun": {"methodRunId": "unc-run-001"},
        "driftEvent": {
            "eventId": "event:assign-case015-unc",
            "eventStart": "2026-06-30T22:00:00Z",
            "eventEnd": "2026-07-01T02:00:00Z",
            "level": "drift",
            "score": 1.0,
        },
        "runtimeResult": {
            "metrics": {
                "statistic": 1.0,
                "threshold": 0.05,
                "pValue": 0.0,
                "testStatistic": 1.0,
                "measurements": {
                    "TEST_STATISTIC": 1.0,
                    "P_VALUE": 0.0,
                    "DRIFT_ALARM_STATE": "drift_detected",
                    "THRESHOLD": 0.05,
                    "METHOD_POLICY": "predictive_entropy_ks",
                    "UNCERTAINTY_MEAN_REFERENCE": 0.45878564637648866,
                    "UNCERTAINTY_MEAN_CURRENT": 0.21918012947375545,
                    "UNCERTAINTY_MEAN_DELTA": -0.2396055169027332,
                    "SAMPLE_SIZE": {"reference": 120, "current": 120},
                    "SAMPLE_SIZE_REFERENCE": 120,
                    "SAMPLE_SIZE_CURRENT": 120,
                    "FEATURE_COLUMNS": ["annotation_confidence", "label_noise_probability"],
                    "PROCESSED_COUNT": 240,
                },
            }
        },
        "analysisChart": {
            "chartId": "CHART-UNC-001",
            "payloadAdapterKey": "auto__ENTROPY_DRIFT__CHART-UNC-001",
        },
        "buckets": [
            {
                "bucketStart": "2026-06-30T22:00:00Z",
                "bucketEnd": "2026-07-01T02:00:00Z",
                "v": 1.0,
                "payload": {
                    "values": [
                        {
                            "period": "reference",
                            "features": {
                                "annotation_confidence": 0.74,
                                "label_noise_probability": 0.15,
                            },
                        },
                        {
                            "period": "reference",
                            "features": {
                                "annotation_confidence": 0.70,
                                "label_noise_probability": 0.15,
                            },
                        },
                        {
                            "period": "current",
                            "features": {
                                "annotation_confidence": 0.85,
                                "label_noise_probability": 0.05,
                            },
                        },
                        {
                            "period": "current",
                            "features": {
                                "annotation_confidence": 0.82,
                                "label_noise_probability": 0.05,
                            },
                        },
                    ]
                },
            }
        ],
    }


def _rep_context(chart_id: str = "CHART-REP-001", variant: str = "MODEL_FEATURE_MAP_MMD") -> dict:
    runtime_key = "graph_embedding_mmd" if variant == "GRAPH_EMBEDDING_MMD" else "model_feature_map_mmd"
    score = 0.6218100551616388 if variant == "GRAPH_EMBEDDING_MMD" else 0.7433107345496132
    measurements = {
        "TEST_STATISTIC": score,
        "P_VALUE": 0.05,
        "DRIFT_ALARM_STATE": "drift_detected",
        "THRESHOLD": 0.019681 if variant == "GRAPH_EMBEDDING_MMD" else 0.016641,
        "METHOD_POLICY": "rbf_mmd_graph_embedding" if variant == "GRAPH_EMBEDDING_MMD" else "rbf_kernel_mmd_feature_map",
        "SAMPLE_SIZE": {"reference": 4, "current": 4},
        "SAMPLE_SIZE_REFERENCE": 4,
        "SAMPLE_SIZE_CURRENT": 4,
        "FEATURE_DIMENSION": 2,
        "FEATURE_COLUMNS": ["activation", "representation_shift"],
        "PROCESSED_COUNT": 8,
    }
    if variant == "GRAPH_EMBEDDING_MMD":
        measurements["GRAPH_EMBEDDING_DRIFT_SCORE"] = score
        measurements["CENTROID_SHIFT"] = 5.096121
        measurements["COSINE_DISTANCE"] = 1.0
    else:
        measurements["FEATURE_MAP_DRIFT_SCORE"] = score
    values = []
    for index, activation in enumerate([0.10, 0.12, 0.14, 0.16]):
        values.append(
            {
                "period": "reference",
                "features": {"activation": activation, "representation_shift": 0.05 + index * 0.01},
            }
        )
    for index, activation in enumerate([0.75, 0.78, 0.81, 0.83]):
        values.append(
            {
                "period": "current",
                "features": {"activation": activation, "representation_shift": 0.55 + index * 0.04},
            }
        )
    return {
        "source": {"sourceId": "case-016-dataset"},
        "feature": {"featureId": "multivariate", "featureLabel": "Multivariate"},
        "assignment": {"runtimeMethodKey": runtime_key, "methodVariantKey": variant},
        "methodRun": {"methodRunId": "rep-run-001"},
        "driftEvent": {
            "eventId": "event:assign-case016-rep",
            "eventStart": "2026-06-30T22:00:00Z",
            "eventEnd": "2026-07-01T02:00:00Z",
            "level": "drift",
            "score": score,
        },
        "runtimeResult": {
            "metrics": {
                "statistic": score,
                "threshold": 0.1,
                "pValue": 0.05,
                "testStatistic": score,
                "measurements": measurements,
            }
        },
        "analysisChart": {
            "chartId": chart_id,
            "payloadAdapterKey": f"auto__{variant}__{chart_id}",
        },
        "buckets": [
            {
                "bucketStart": "2026-06-30T22:00:00Z",
                "bucketEnd": "2026-07-01T02:00:00Z",
                "v": score,
                "payload": {"values": values, "featureColumns": ["activation", "representation_shift"]},
            }
        ],
    }


def _variance_context() -> dict:
    reference = [-1.2, -0.9, -0.5, -0.3, 0.0, 0.2, 0.4, 0.6, 0.9, 1.1] * 8
    current = [-3.8, -2.9, -1.5, -0.8, 0.0, 0.7, 1.3, 2.1, 3.2, 4.0] * 8
    values = [{"period": "reference", "value": value} for value in reference] + [
        {"period": "current", "value": value} for value in current
    ]
    return {
        "source": {"sourceId": "case-003"},
        "feature": {"featureId": "score", "featureLabel": "Score"},
        "assignment": {"runtimeMethodKey": "generic_statistical_test_window"},
        "methodRun": {"methodRunId": "variance-run-001"},
        "driftEvent": {
            "eventId": "event:assign-case003-variance:score:2026-07-01T00:00:00Z:2026-07-02T00:00:00Z",
            "eventStart": "2026-07-01T00:00:00Z",
            "eventEnd": "2026-07-02T00:00:00Z",
            "level": "drift",
            "score": 3.9059243851955974,
        },
        "runtimeResult": {
            "metrics": {
                "pValue": 1.7248319172160542e-69,
                "testStatistic": 3.9059243851955974,
                "measurements": {
                    "F_STATISTIC": 3.9059243851955974,
                    "P_VALUE": 1.7248319172160542e-69,
                    "SAMPLE_SIZE_REFERENCE": len(reference),
                    "SAMPLE_SIZE_CURRENT": len(current),
                },
            }
        },
        "analysisChart": {
            "chartId": "CHART-VAR-001",
            "payloadAdapterKey": "auto__F_TEST_EQUAL_VARIANCE__CHART-VAR-001",
        },
        "buckets": [
            {
                "bucketStart": "2026-07-01T00:00:00Z",
                "bucketEnd": "2026-07-02T00:00:00Z",
                "v": 3.9059243851955974,
                "payload": {"values": values},
            }
        ],
    }


def _linear_mmd_context() -> dict:
    return {
        "source": {"sourceId": "case-008"},
        "feature": {"featureId": "multivariate", "featureLabel": "Multivariate"},
        "assignment": {"runtimeMethodKey": "linear_time_mmd"},
        "methodRun": {"methodRunId": "mmd-run-001"},
        "driftEvent": {
            "eventId": "mmd-event-001",
            "eventStart": "2026-07-01T00:00:00Z",
            "eventEnd": "2026-07-01T01:00:00Z",
            "level": "drift",
            "score": 0.7304543349837261,
        },
        "runtimeResult": {
            "metrics": {
                "statistic": 0.7304543349837261,
                "threshold": 0.1,
                "measurements": {
                    "MMD_STATISTIC": 0.7304543349837261,
                    "SAMPLE_SIZE_REFERENCE": 30,
                    "SAMPLE_SIZE_CURRENT": 30,
                },
            }
        },
        "analysisChart": {
            "chartId": "CHART-MV-002",
            "payloadAdapterKey": "auto__LINEAR_TIME_MMD__CHART-MV-002",
        },
        "buckets": [
            {
                "bucketStart": "2026-07-01T00:00:00Z",
                "bucketEnd": "2026-07-01T01:00:00Z",
                "v": 0.7304543349837261,
                "payload": {"values": []},
            }
        ],
    }


def _anom_context() -> dict:
    return {
        "source": {"sourceId": "case-009"},
        "feature": {"featureId": "multivariate", "featureLabel": "Multivariate"},
        "assignment": {
            "runtimeMethodKey": "isolation_forest_drift_score",
            "params": {"anomaly_rate_threshold": 0.1},
        },
        "methodRun": {"methodRunId": "anom-run-001"},
        "driftEvent": {
            "eventId": "anom-event-001",
            "eventStart": "2026-06-30T22:00:00Z",
            "eventEnd": "2026-07-01T02:00:00Z",
            "level": "drift",
            "score": 0.175,
        },
        "runtimeResult": {
            "metrics": {
                "statistic": 0.175,
                "threshold": 0.1,
                "measurements": {
                    "ANOMALY_SCORE": 1.1476188099883775,
                    "MAX_ANOMALY_SCORE": 3.716244104601693,
                    "OUTLIER_OR_ANOMALY_RATE": 0.175,
                    "THRESHOLD": 2.3534324640554374,
                    "ANOMALY_RATE_THRESHOLD": 0.1,
                    "ANOMALY_COUNT": 21,
                    "SAMPLE_SIZE_REFERENCE": 120,
                    "SAMPLE_SIZE_CURRENT": 120,
                },
            }
        },
        "analysisChart": {
            "chartId": "CHART-ANOM-001",
            "payloadAdapterKey": "auto__ISOLATION_FOREST_DRIFT_SCORE__CHART-ANOM-001",
        },
        "buckets": [
            {
                "bucketStart": "2026-06-30T22:00:00Z",
                "bucketEnd": "2026-07-01T02:00:00Z",
                "v": 0.175,
                "payload": {"values": []},
            }
        ],
    }


def test_binding_spec_declares_method_chart_and_runtime_data_contract() -> None:
    spec = get_binding_spec("adwin_mean_stream_to_chart_stream_001")

    assert spec["methodVariantKey"] == "ADWIN_MEAN_STREAM"
    assert spec["chartId"] == "CHART-STREAM-001"
    assert spec["templateDataPolicy"] == "replace_data_only"
    assert {item["source"] for item in spec["dataContracts"]} == {
        "chart.CHART-STREAM-001.summary",
        "chart.CHART-STREAM-001.stream",
        "chart.CHART-STREAM-001.window",
        "chart.CHART-STREAM-001.mean",
        "chart.CHART-STREAM-001.notes",
    }


def test_binding_builds_chart_payload_from_drift_event_and_buckets() -> None:
    payload = build_payload(_context())

    assert payload["chartId"] == "CHART-STREAM-001"
    assert payload["sourceId"] == "case-010"
    assert payload["eventId"] == "event-001"
    assert payload["layout"]["columns"] == 12
    assert payload["data"]["chart.CHART-STREAM-001.stream"][0]["time"] == 1
    assert payload["data"]["chart.CHART-STREAM-001.stream"][-1]["time"] == 36
    assert payload["data"]["chart.CHART-STREAM-001.summary"][0]["label"] == "alarm index"
    assert payload["data"]["chart.CHART-STREAM-001.summary"][2]["displayValue"] == "3.25"
    assert payload["data"]["chart.CHART-STREAM-001.notes"][0]["title"] == "해석"
    assert payload["metadata"]["methodVariantKey"] == "ADWIN_MEAN_STREAM"
    assert payload["metadata"]["metrics"]["meanDifference"] == 2.5


def test_binding_fails_fast_when_method_event_contract_is_missing() -> None:
    context = _context()
    del context["driftEvent"]["eventEnd"]

    with pytest.raises(PayloadBindingError, match="eventEnd"):
        build_payload(context)


def test_registered_adapter_puts_event_into_runtime_and_legacy_payload_fields() -> None:
    adapter = get_payload_adapter("adwin_mean_stream_to_chart_stream_001")

    payload = adapter(_context())

    assert payload["chartId"] == "CHART-STREAM-001"
    assert payload["eventId"] == "event-001"
    assert payload["metadata"]["bindingId"] == "adwin_mean_stream__CHART-STREAM-001"
    assert payload["metadata"]["score"] == 3.25

    stream_rows = payload["data"]["chart.CHART-STREAM-001.stream"]
    assert len(stream_rows) == 36
    assert stream_rows[0]["value"] < stream_rows[-1]["value"]

    summary_by_label = {row["label"]: row for row in payload["data"]["chart.CHART-STREAM-001.summary"]}
    assert summary_by_label["alarm index"]["displayValue"] == "23"
    assert summary_by_label["score"]["displayValue"] == "3.2500"

    assert payload["eventMarkers"] == [
        {
            "eventId": "event-001",
            "t": "2026-01-01T00:20:00Z",
            "level": "drift",
            "score": 3.25,
        }
    ]
    assert payload["annotations"] == [
        {
            "type": "event-window",
            "start": "2026-01-01T00:10:00Z",
            "end": "2026-01-01T00:20:00Z",
            "level": "drift",
        }
    ]


def test_psi_auto_binding_builds_numeric_trend_rows_and_dynamic_axes() -> None:
    payload = build_payload(_psi_context(), "auto__NUMERIC_BINNED_PSI__CHART-PSI-001")

    assert payload["chartId"] == "CHART-PSI-001"
    summary_rows = payload["data"]["chart.CHART-PSI-001.summary"]
    assert [row["label"] for row in summary_rows] == ["PSI", "threshold", "top bin", "samples"]
    assert summary_rows[0]["displayValue"] == "3.95"
    assert summary_rows[2]["displayValue"] == "bin_0"
    assert summary_rows[3]["displayValue"] == "60/60"
    notes = payload["data"]["chart.CHART-PSI-001.notes"]
    assert notes[0]["title"] == "PSI population shift analysis"
    assert "PSI 3.95 exceeds threshold 0.100" in notes[0]["text"]
    assert payload["title"] == "구간 비율 변화로 본 PSI 드리프트"
    area_descriptions = {
        area["area"]: area.get("description", "")
        for area in payload["layout"]["areas"]
    }
    assert "bin_0 구간은 기준 20.0%에서 현재 0.0%로 -20.0pp 변했다." == area_descriptions["main"]
    assert "bin_0 기여도 2.4412가 전체 PSI에서 가장 크다." == area_descriptions["side_top"]
    assert "최근 window PSI 3.95가 관리 기준 0.100을 넘는다." == area_descriptions["side_bottom"]
    assert "80-100" not in "\n".join(area_descriptions.values())
    bin_component = next(
        component
        for component in payload["components"]
        if component["componentInstanceId"] == "CHART-PSI-001.bins.0"
    )
    assert bin_component["config"]["annotations"][0]["text"] == "상위 기여: bin_0"
    trend_rows = payload["data"]["chart.CHART-PSI-001.trend"]
    assert len(trend_rows) == 7
    assert trend_rows[0]["window"] == 1
    assert trend_rows[-1]["window"] == 7
    assert trend_rows[-1]["psi"] == 3.95375
    assert all(isinstance(row["window"], int) for row in trend_rows)

    component_config_by_id = {
        component["componentInstanceId"]: component["config"]
        for component in payload["components"]
    }
    assert "y_max" not in component_config_by_id["CHART-PSI-001.trend.0"]
    assert "x_max" not in component_config_by_id["CHART-PSI-001.contrib.0"]


def test_psi_auto_binding_applies_dynamic_axes_to_score_band_variant() -> None:
    payload = build_payload(_psi_context(), "auto__SCORE_BAND_PSI__CHART-PSI-001")

    assert payload["chartId"] == "CHART-PSI-001"
    assert payload["metadata"]["bindingId"] == "auto__SCORE_BAND_PSI__CHART-PSI-001"
    assert payload["data"]["chart.CHART-PSI-001.trend"][-1]["psi"] == 3.95375

    component_config_by_id = {
        component["componentInstanceId"]: component["config"]
        for component in payload["components"]
    }
    assert "y_max" not in component_config_by_id["CHART-PSI-001.trend.0"]
    assert "x_max" not in component_config_by_id["CHART-PSI-001.contrib.0"]


def test_linear_mmd_mv002_auto_binding_uses_runtime_values_in_layout_text() -> None:
    payload = build_payload(_linear_mmd_context(), "auto__LINEAR_TIME_MMD__CHART-MV-002")

    assert payload["chartId"] == "CHART-MV-002"
    area_descriptions = {
        area["area"]: area.get("description", "")
        for area in payload["layout"]["areas"]
    }
    assert area_descriptions["main"] == "기준 중심 (0.20, 0.30)에서 현재 중심 (0.80, 0.70)로 이동한 방향을 읽는다."
    assert area_descriptions["side_top"] == "현재 window MMD 0.730가 관리 기준 0.100을 넘는다."
    assert area_descriptions["side_bottom"] == "관측 MMD 0.730와 기준 0.100의 차이를 함께 본다."
    description_text = "\n".join(area_descriptions.values())
    assert "0.36" not in description_text
    assert "0.18" not in description_text
    assert "1.55" not in description_text
    summary_rows = payload["data"]["chart.CHART-MV-002.summary"]
    assert [row["label"] for row in summary_rows] == ["MMD", "threshold", "samples", "bandwidth"]
    assert summary_rows[0]["displayValue"] == "0.730"
    assert summary_rows[1]["displayValue"] == "0.100"
    trend_rows = payload["data"]["chart.CHART-MV-002.mmd"]
    assert len(trend_rows) == 10
    assert trend_rows[-1] == {"mmd": 0.730454, "window": 10}
    null_rows = payload["data"]["chart.CHART-MV-002.null"]
    assert len(null_rows) == 9
    assert all({"x0", "x1", "count", "class"} <= set(row) for row in null_rows)
    config_by_id = {
        component["componentInstanceId"]: component["config"]
        for component in payload["components"]
    }
    assert config_by_id["CHART-MV-002.mmd.0"]["horizontal_markers"][0]["y"] == 0.1
    assert config_by_id["CHART-MV-002.null.0"]["vertical_markers"][0]["x"] == 0.730454


def test_text001_topic_distribution_auto_binding_uses_runtime_topic_metrics() -> None:
    payload = build_payload(_text001_topic_context(), "auto__TOPIC_DISTRIBUTION_SHIFT__CHART-TEXT-001")

    assert payload["chartId"] == "CHART-TEXT-001"
    assert payload["title"] == "토픽 분포 변화로 본 텍스트 의미 드리프트"
    summary_rows = payload["data"]["summary"]
    assert [row["label"] for row in summary_rows] == ["JS distance", "threshold", "max topic delta", "samples"]
    assert summary_rows[0]["displayValue"] == "0.296"
    assert summary_rows[1]["displayValue"] == "0.100"
    assert summary_rows[2]["displayValue"] == "24.2pp"
    assert summary_rows[3]["displayValue"] == "120/120"

    topic_rows = payload["data"]["topic_mix"]
    assert topic_rows[0]["category"] == "baseline"
    assert topic_rows[1]["category"] == "current"
    assert topic_rows[0]["topic1"] == 0.3
    assert topic_rows[1]["topic1"] == 0.058333
    assert topic_rows[0]["topic3_label"] == "technical -24.2pp"

    distance_rows = payload["data"]["distance"]
    assert distance_rows[-1] == {"time": 5, "value": 0.295934}
    note_text = payload["data"]["notes"][0]["text"]
    assert "JS distance 0.296 exceeds threshold 0.100" in note_text
    assert "technical changed from 30.0% to 5.8% (-24.2pp)" in note_text

    area_descriptions = {
        area["area"]: area.get("description", "")
        for area in payload["layout"]["areas"]
    }
    assert area_descriptions["side_top"] == "JS distance 0.296가 관리 기준 0.100을 넘는다."
    assert area_descriptions["side_bottom"] == "technical 비율이 기준 30.0%에서 현재 5.8%로 -24.2pp 변했다."
    description_text = "\n".join(area_descriptions.values())
    assert "0.36" not in description_text
    assert "0.58" not in description_text
    assert "Topic 3" not in description_text
    assert "AUC 0.82" not in description_text

    component_config_by_id = {
        component["componentInstanceId"]: component["config"]
        for component in payload["components"]
    }
    side_top_config = component_config_by_id["CHART-TEXT-001.side_top.0"]
    assert side_top_config["horizontal_markers"][0]["y"] == 0.1
    assert side_top_config["horizontal_markers"][0]["label"] == "threshold 0.100"
    assert side_top_config["annotations"][0]["text"] == "JS 0.296 > 0.100"


def test_expl001_global_importance_auto_binding_uses_runtime_importance_metrics() -> None:
    payload = build_payload(_expl001_importance_context(), "auto__GLOBAL_IMPORTANCE_RANK_SHIFT__CHART-EXPL-001")

    assert payload["chartId"] == "CHART-EXPL-001"
    assert payload["title"] == "설명 중요도 순위 변화로 본 Explainability 드리프트"
    summary_rows = payload["data"]["chart.CHART-EXPL-001.summary"]
    assert [row["label"] for row in summary_rows] == ["SHAP distance", "threshold", "top shift", "samples"]
    assert summary_rows[0]["displayValue"] == "0.667"
    assert summary_rows[1]["displayValue"] == "0.400"
    assert summary_rows[2]["displayValue"] == "importance_b"
    assert summary_rows[3]["displayValue"] == "120/120"

    feature_rows = payload["data"]["chart.CHART-EXPL-001.features"]
    assert feature_rows[0] == {"baseline": 0.252996, "current": 0.539, "feature": "importance_b"}
    assert feature_rows[1] == {"baseline": 0.450425, "current": 0.197065, "feature": "importance_a"}
    assert len(payload["data"]["chart.CHART-EXPL-001.distribution"]) == 10
    assert payload["data"]["chart.CHART-EXPL-001.heatmap"][0]["class"] == "reference rank"
    note_text = payload["data"]["chart.CHART-EXPL-001.notes"][0]["text"]
    assert "score 0.667 exceeds threshold 0.400" in note_text
    assert "importance_b changed from 25.3% to 53.9%" in note_text
    assert "rank 3->1" in note_text

    area_descriptions = {
        area["area"]: area.get("description", "")
        for area in payload["layout"]["areas"]
    }
    assert area_descriptions["main"] == "importance_b 중요도가 기준 25.3%에서 현재 53.9%로 +28.6pp 변했다."
    assert area_descriptions["side_top"] == "SHAP drift score 0.667가 관리 기준 0.400을 넘는다."
    layout_text = str(payload["layout"])
    assert "risk_score" not in layout_text
    assert "amount" not in layout_text
    assert "class C" not in layout_text
    assert "0.27" not in layout_text
    assert "0.36으로 증가" not in layout_text

    component_config_by_id = {
        component["componentInstanceId"]: component["config"]
        for component in payload["components"]
    }
    assert component_config_by_id["CHART-EXPL-001.shap_summary.0"]["x_axis_label"] == "reference/current importance"
    assert component_config_by_id["CHART-EXPL-001.distribution.0"]["x_axis_label"] == "importance_b importance shift surrogate"
    assert component_config_by_id["CHART-EXPL-001.class_heatmap.0"]["x_values"] == ["importance_b", "importance_a", "importance_c"]


def test_unc001_entropy_auto_binding_uses_runtime_uncertainty_metrics() -> None:
    payload = build_payload(_unc001_entropy_context(), "auto__ENTROPY_DRIFT__CHART-UNC-001")

    assert payload["chartId"] == "CHART-UNC-001"
    assert payload["title"] == "불확실성 분포 변화로 본 annotation quality 드리프트"
    summary_rows = payload["data"]["summary"]
    assert [row["label"] for row in summary_rows] == ["KS statistic", "p-value", "mean delta", "samples"]
    assert summary_rows[0]["value"] == "1.000"
    assert summary_rows[1]["value"] == "0"
    assert summary_rows[2]["value"] == "-0.240"
    assert summary_rows[3]["value"] == "120/120"

    confidence_rows = payload["data"]["confidence"]
    assert len(confidence_rows) == 14
    assert all({"confidence", "baseline", "current"} <= set(row) for row in confidence_rows)
    entropy_rows = payload["data"]["entropy"]
    assert entropy_rows[0]["value"] == 0.458786
    assert entropy_rows[-1]["value"] == 0.21918
    note_text = payload["data"]["notes"][0]["text"]
    assert "KS statistic 1.000" in note_text
    assert "p-value 0 <= alpha 0.050" in note_text
    assert "Mean uncertainty changed from 0.459 to 0.219" in note_text

    area_descriptions = {
        area["area"]: area.get("description", "")
        for area in payload["layout"]["areas"]
    }
    assert area_descriptions["main"] == "reference mean 0.459에서 current mean 0.219로 -0.240 변했다."
    assert area_descriptions["side_top"] == "KS statistic 1.000, p-value 0가 alpha 0.050 이하이다."
    layout_text = str(payload["layout"])
    assert "Baseline peak is 0.82/41" not in layout_text
    assert "Entropy crosses threshold 0.55" not in layout_text
    assert "class C uncertainty" not in layout_text

    component_config_by_id = {
        component["componentInstanceId"]: component["config"]
        for component in payload["components"]
    }
    main_config = component_config_by_id["CHART-UNC-001.main.0"]
    assert main_config["x_axis_label"] == "uncertainty"
    confidence_y_max = max(
        max(row["baseline"], row["current"])
        for row in confidence_rows
    )
    assert 0 <= main_config["annotations"][0]["y"] <= max(confidence_y_max, 1.0)
    assert all(
        0 <= marker["label_y"] <= max(confidence_y_max, 1.0)
        for marker in main_config["vertical_markers"]
    )
    assert component_config_by_id["CHART-UNC-001.side_top.0"]["horizontal_markers"][0]["y"] == 0.21918


def test_rep001_feature_map_auto_binding_uses_runtime_representation_metrics() -> None:
    payload = build_payload(_rep_context(), "auto__MODEL_FEATURE_MAP_MMD__CHART-REP-001")

    assert payload["chartId"] == "CHART-REP-001"
    assert payload["title"] == "Feature map MMD로 본 표현 공간 드리프트"
    summary_rows = payload["data"]["chart.CHART-REP-001.summary"]
    assert [row["label"] for row in summary_rows] == ["feature-map MMD", "threshold", "p-value", "samples"]
    assert summary_rows[0]["displayValue"] == "0.743"
    assert summary_rows[1]["displayValue"] == "0.017"
    assert summary_rows[2]["displayValue"] == "0.05"
    assert summary_rows[3]["displayValue"] == "4/4"

    activation_rows = payload["data"]["chart.CHART-REP-001.activation"]
    assert len(activation_rows) == 8
    projection_rows = payload["data"]["chart.CHART-REP-001.projection"]
    assert {row["group"] for row in projection_rows} == {"baseline", "current"}
    note_text = payload["data"]["chart.CHART-REP-001.notes"][0]["text"]
    assert "Feature map drift detected: score 0.743 exceeds threshold 0.017" in note_text
    assert "activation mean changed" in note_text

    layout_text = str(payload["layout"])
    assert "block3 c6~c9" not in layout_text
    assert "baseline peak" not in layout_text
    component_config_by_id = {
        component["componentInstanceId"]: component["config"]
        for component in payload["components"]
    }
    assert component_config_by_id["CHART-REP-001.projection.0"]["x_axis_label"] == "activation / embedding dimension 1"
    assert component_config_by_id["CHART-REP-001.activation.0"]["y_max"] > 0


def test_rep003_graph_embedding_auto_binding_uses_runtime_representation_metrics() -> None:
    payload = build_payload(
        _rep_context("CHART-REP-003", "GRAPH_EMBEDDING_MMD"),
        "auto__GRAPH_EMBEDDING_MMD__CHART-REP-003",
    )

    assert payload["chartId"] == "CHART-REP-003"
    assert payload["title"] == "Graph embedding MMD로 본 표현 공간 드리프트"
    summary_rows = payload["data"]["chart.CHART-REP-003.summary"]
    assert [row["label"] for row in summary_rows] == ["graph MMD", "threshold", "p-value", "samples"]
    assert summary_rows[0]["displayValue"] == "0.622"
    assert summary_rows[1]["displayValue"] == "0.020"

    distance_rows = payload["data"]["chart.CHART-REP-003.distance"]
    assert distance_rows[-1] == {"time": 6, "value": 0.62181}
    heatmap_rows = payload["data"]["chart.CHART-REP-003.heatmap"]
    assert heatmap_rows[0]["nodeGroup"] == "activation"
    note_text = payload["data"]["chart.CHART-REP-003.notes"][0]["text"]
    assert "Graph embedding drift detected: score 0.622 exceeds threshold 0.020" in note_text

    layout_text = str(payload["layout"])
    assert "hub는 0.70" not in layout_text
    assert "distance가 t=15" not in layout_text
    component_config_by_id = {
        component["componentInstanceId"]: component["config"]
        for component in payload["components"]
    }
    distance_config = component_config_by_id["CHART-REP-003.distance.0"]
    assert distance_config["x_max"] == 6
    assert distance_config["horizontal_markers"][0]["y"] == 0.019681


def test_ocdd_anom001_auto_binding_uses_runtime_values_and_populates_components() -> None:
    payload = build_payload(_anom_context(), "auto__ISOLATION_FOREST_DRIFT_SCORE__CHART-ANOM-001")

    assert payload["chartId"] == "CHART-ANOM-001"
    assert payload["title"] == "정상 영역 밖 샘플 증가로 본 이상치 드리프트"
    area_descriptions = {
        area["area"]: area.get("description", "")
        for area in payload["layout"]["areas"]
    }
    assert area_descriptions["main"] == "현재 score 분포에서 outlier rate 0.175가 기준 0.100을 넘는다."
    assert area_descriptions["side_top"] == "최근 window 이상 비율 0.175가 관리 기준 0.100을 넘는다."
    assert area_descriptions["side_bottom"] == "현재 window에서 정상 영역 밖 샘플 21개가 분리되어 보인다."
    description_text = "\n".join(area_descriptions.values())
    assert "0.62" not in description_text
    assert "0.37" not in description_text
    assert "0.20" not in description_text

    summary_rows = payload["data"]["chart.CHART-ANOM-001.summary"]
    assert [row["label"] for row in summary_rows] == ["outlier rate", "rate threshold", "outlier count", "samples"]
    assert summary_rows[0]["value"] == "0.175"
    assert summary_rows[1]["value"] == "0.100"
    assert summary_rows[2]["value"] == "21"
    assert summary_rows[3]["value"] == "120/120"
    assert len(payload["data"]["chart.CHART-ANOM-001.score"]) == 24
    assert len(payload["data"]["chart.CHART-ANOM-001.rate"]) == 7
    assert payload["data"]["chart.CHART-ANOM-001.rate"][-1] == {"rate": 0.175, "time": 7}
    projection_rows = payload["data"]["chart.CHART-ANOM-001.projection"]
    assert len(projection_rows) > 32
    assert any(row["group"] == "outlier" for row in projection_rows)
    assert payload["data"]["chart.CHART-ANOM-001.notes"][0]["title"] == "OCDD anomaly drift analysis"

    config_by_id = {
        component["componentInstanceId"]: component["config"]
        for component in payload["components"]
    }
    assert config_by_id["CHART-ANOM-001.score.0"]["vertical_markers"][0]["x"] == 2.353432
    assert "y_ticks" not in config_by_id["CHART-ANOM-001.score.0"]
    assert "y_max" not in config_by_id["CHART-ANOM-001.score.0"]
    assert config_by_id["CHART-ANOM-001.rate.0"]["horizontal_markers"][0]["y"] == 0.1


def test_variance_auto_binding_uses_method_specific_caption_and_dynamic_axes() -> None:
    payload = build_payload(_variance_context(), "auto__F_TEST_EQUAL_VARIANCE__CHART-VAR-001")

    assert payload["chartId"] == "CHART-VAR-001"
    assert payload["data"]["summary"]
    assert payload["data"]["spread"]
    assert payload["data"]["variance"]
    assert payload["data"]["deviation"]
    assert [row["label"] for row in payload["data"]["summary"]] == ["F-test", "p-value", "variance ratio", "samples"]
    assert len(payload["data"]["spread"]) == 2
    assert all(row["density"] for row in payload["data"]["spread"])
    assert [row["label"] for row in payload["data"]["variance"]] == ["기준", "현재"]
    assert all(row["variance"] > 0 for row in payload["data"]["variance"])
    assert payload["data"]["variance"][1]["variance"] > payload["data"]["variance"][0]["variance"]
    assert payload["data"]["deviation"][0]["label"] == "F-test"
    assert payload["data"]["notes"][0]["title"] == "Variance drift analysis"

    component_config_by_id = {
        component["componentInstanceId"]: component["config"]
        for component in payload["components"]
    }
    main_config = component_config_by_id["CHART-VAR-001.main.0"]
    variance_config = component_config_by_id["CHART-VAR-001.side_top.0"]
    deviation_config = component_config_by_id["CHART-VAR-001.side_bottom.0"]

    assert "y_min" not in main_config
    assert "y_max" not in main_config
    assert main_config.get("annotations") == []
    assert "y_max" not in variance_config
    assert variance_config["x_axis_label"] == "reference/current variance"
    assert "x_max" not in deviation_config
    assert deviation_config["caption"] == "F-test statistic"
    assert "Levene p=0.012" not in str(payload)


def test_hddm_error_chart_auto_binding_uses_numeric_runtime_axis() -> None:
    binding_key = "auto__HDDM_A_HOEFFDING_BOUND__CHART-ERR-005"
    spec = get_binding_spec(binding_key)

    contracts = {item["source"]: item["transform"] for item in spec["dataContracts"]}
    assert contracts["chart.CHART-ERR-005.summary"] == "hddm_error_summary"
    assert contracts["chart.CHART-ERR-005.series"] == "hddm_error_series"
    assert contracts["chart.CHART-ERR-005.timeline"] == "hddm_error_timeline"

    payload = build_payload(_hddm_context(), binding_key)
    component_config_by_id = {
        component["componentInstanceId"]: component["config"]
        for component in payload["components"]
    }
    summary_rows = payload["data"]["chart.CHART-ERR-005.summary"]
    series_rows = payload["data"]["chart.CHART-ERR-005.series"]
    timeline_rows = payload["data"]["chart.CHART-ERR-005.timeline"]

    assert payload["chartId"] == "CHART-ERR-005"
    assert summary_rows == [
        {"label": "level", "value": "drift"},
        {"label": "score", "value": "0.0211"},
        {"label": "drift bound", "value": "0.0205"},
    ]
    assert all("event:" not in str(row["value"]) for row in summary_rows)
    assert series_rows[0]["time"] == 1
    assert series_rows[-1]["time"] == 32
    assert all(isinstance(row["time"], (int, float)) for row in series_rows)
    assert all(row["time"] == row["time"] for row in series_rows)
    assert series_rows[-1]["error"] == 0.24
    assert timeline_rows == [{"end": 32, "label": "drift", "role": "drift", "start": 26}]
    bound_config = component_config_by_id["CHART-ERR-005.bound.0"]
    assert bound_config["horizontal_markers"][0]["y"] == 0.017612
    assert bound_config["horizontal_markers"][1]["y"] == 0.020459
    assert bound_config["vertical_markers"] == [
        {"x": 19.6, "class": "state-line", "opacity": 0.7},
        {"x": 25.8, "class": "state-line"},
    ]


def test_ddm_err001_auto_binding_uses_runtime_axis_and_numeric_timeline() -> None:
    binding_key = "auto__DDM_STANDARD__CHART-ERR-001"
    spec = get_binding_spec(binding_key)

    contracts = {item["source"]: item["transform"] for item in spec["dataContracts"]}
    assert contracts["chart.CHART-ERR-001.summary"] == "ddm_error_summary"
    assert contracts["chart.CHART-ERR-001.error"] == "ddm_error_series"
    assert contracts["chart.CHART-ERR-001.timeline"] == "ddm_error_timeline"

    payload = build_payload(_ddm_err001_context(), binding_key)
    component_config_by_id = {
        component["componentInstanceId"]: component["config"]
        for component in payload["components"]
    }
    series_rows = payload["data"]["chart.CHART-ERR-001.error"]
    timeline_rows = payload["data"]["chart.CHART-ERR-001.timeline"]
    summary_rows = payload["data"]["chart.CHART-ERR-001.summary"]

    assert payload["chartId"] == "CHART-ERR-001"
    assert summary_rows == [
        {"label": "현재 오류율", "value": "0.300"},
        {"label": "이전 오류율", "value": "0.000"},
        {"label": "변화량", "value": "+0.300"},
        {"label": "기준", "value": "0.120"},
    ]
    assert component_config_by_id["CHART-ERR-001.error.0"]["vertical_markers"] == []
    assert component_config_by_id["CHART-ERR-001.error.0"]["point_highlights"] == []
    assert component_config_by_id["CHART-ERR-001.margin.0"]["vertical_markers"] == []
    assert component_config_by_id["CHART-ERR-001.timeline.0"]["x_min"] == 1
    assert component_config_by_id["CHART-ERR-001.timeline.0"]["x_max"] == 32
    assert component_config_by_id["CHART-ERR-001.timeline.0"]["label_map"] == {
        "drift": "D",
        "normal": " ",
        "warning": "W",
    }
    assert component_config_by_id["CHART-ERR-001.timeline.0"]["track_overlays"] == []
    assert component_config_by_id["CHART-ERR-001.timeline.0"]["markers"] == []
    assert series_rows[0] == {"error": 0.02, "margin": -0.1, "time": 1}
    assert series_rows[-1]["time"] == 32
    assert all(isinstance(row["time"], (int, float)) for row in series_rows)
    assert all(isinstance(row["margin"], (int, float)) for row in series_rows)
    assert timeline_rows == [
        {"end": series_rows[1]["time"], "label": "normal", "role": "normal", "start": 1},
        {
            "end": series_rows[2]["time"],
            "label": "drift",
            "role": "drift",
            "start": series_rows[1]["time"],
        },
        {"end": 32, "label": "normal", "role": "normal", "start": series_rows[2]["time"]},
    ]
    assert "2026-" not in str(timeline_rows)


def test_seqdrift_stream004_auto_binding_uses_alarm_events_and_numeric_axes() -> None:
    binding_key = "auto__SEQDRIFT1__CHART-STREAM-004"
    spec = get_binding_spec(binding_key)

    contracts = {item["source"]: item["transform"] for item in spec["dataContracts"]}
    assert contracts["stream"] == "seqdrift_stream_series"
    assert contracts["evidence"] == "seqdrift_evidence_series"
    assert contracts["timeline"] == "seqdrift_timeline"

    payload = build_payload(_seqdrift_context(), binding_key)
    component_config_by_id = {
        component["componentInstanceId"]: component["config"]
        for component in payload["components"]
    }
    stream_rows = payload["data"]["stream"]
    evidence_rows = payload["data"]["evidence"]
    timeline_rows = payload["data"]["timeline"]
    summary_rows = payload["data"]["summary"]

    assert payload["chartId"] == "CHART-STREAM-004"
    assert payload["title"] == "SeqDrift 순차 경계 초과로 본 스트림 드리프트"
    assert summary_rows == [
        {"label": "level", "value": "drift"},
        {"label": "score", "value": "0.331"},
        {"label": "alarms", "value": "3"},
    ]
    assert len(stream_rows) > 1
    assert stream_rows[0]["time"] == 1
    assert stream_rows[-1]["time"] == 36
    assert stream_rows[0]["value"] < stream_rows[-1]["value"]
    assert len(evidence_rows) == 3
    assert evidence_rows[-1]["evidence"] == 1.0
    assert evidence_rows[-1]["bound"] == 0.668615
    assert all(row["pointClass"] == "alarm-point" for row in evidence_rows)
    assert timeline_rows[-1]["role"] == "drift"
    assert "2026-" not in str(timeline_rows)
    assert component_config_by_id["CHART-STREAM-004.main.0"]["horizontal_markers"][0]["y"] == 0.02
    assert component_config_by_id["CHART-STREAM-004.main.0"]["point_highlights"]
    assert component_config_by_id["CHART-STREAM-004.side_top.0"]["y_max"] > 1.0
    assert component_config_by_id["CHART-STREAM-004.side_bottom.0"]["markers"]


def test_wasserstein_dist001_auto_binding_builds_distribution_rows_without_internal_note_id() -> None:
    payload = build_payload(_wasserstein_distribution_context(), "auto__WASSERSTEIN_1D_EXACT__CHART-DIST-001")

    density_rows = payload["data"]["chart.CHART-DIST-001.density"]
    summary_rows = payload["data"]["chart.CHART-DIST-001.summary"]
    trend_rows = payload["data"]["chart.CHART-DIST-001.trend"]
    ranking_rows = payload["data"]["chart.CHART-DIST-001.ranking"]
    note_text = payload["data"]["chart.CHART-DIST-001.notes"][0]["text"]

    assert payload["chartId"] == "CHART-DIST-001"
    assert [row["label"] for row in summary_rows] == ["Wasserstein", "평균 이동", "상위 10% 이동"]
    assert summary_rows[0]["displayValue"] == "0.54"
    assert summary_rows[1]["displayValue"].startswith("+")
    assert summary_rows[2]["displayValue"].startswith("+")
    assert len(density_rows) > 10
    assert all({"x", "reference", "current"} <= set(row) for row in density_rows)
    assert all(isinstance(row["x"], float) for row in density_rows)
    assert all(0 <= row["reference"] <= 0.42 for row in density_rows)
    assert all(0 <= row["current"] <= 0.42 for row in density_rows)
    assert len(trend_rows) == 9
    assert trend_rows[0]["window"] == 1
    assert trend_rows[-1]["window"] == 9
    assert trend_rows[-1]["distance"] == 0.535
    assert all(isinstance(row["window"], int) for row in trend_rows)
    assert all(isinstance(row["distance"], float) for row in trend_rows)
    assert ranking_rows == [
        {
            "class": "dist-bar-highlight",
            "distance": 0.535,
            "distanceLabel": "0.54",
            "feature": "Metric",
        }
    ]
    assert "event:" not in note_text
    assert "assign-case001" not in note_text
    assert "2026-06-30T23:00:00Z - 2026-07-01T01:00:00Z" in note_text


def test_distshape_auto_binding_uses_runtime_shape_data_and_dynamic_axes() -> None:
    payload = build_payload(_distshape_context(), "auto__TWO_SAMPLE_EPPS_SINGLETON__CHART-DISTSHAPE-001")

    assert payload["chartId"] == "CHART-DISTSHAPE-001"
    assert payload["title"] == "CHART-DISTSHAPE-001 - reference/current 분포 모양 변화"

    summary_rows = payload["data"]["chart.CHART-DISTSHAPE-001.summary"]
    density_rows = payload["data"]["chart.CHART-DISTSHAPE-001.density"]
    ecf_rows = payload["data"]["chart.CHART-DISTSHAPE-001.ecf"]
    stat_rows = payload["data"]["chart.CHART-DISTSHAPE-001.stat"]

    assert summary_rows[0] == {"label": "Epps-Singleton", "value": "89.98"}
    assert summary_rows[1]["label"] == "p-value"
    assert summary_rows[1]["value"] == "1.33e-18"
    assert summary_rows[2] == {"label": "samples", "value": "10/10"}
    assert len(density_rows) == 25
    assert min(row["x"] for row in density_rows) < -8
    assert max(row["x"] for row in density_rows) > 13
    assert all({"x", "reference", "current", "difference"} <= set(row) for row in density_rows)
    assert len(ecf_rows) >= 8
    assert {0.4, 0.8} <= {row["frequency"] for row in ecf_rows}
    assert all(0 <= row["real"] <= 2 for row in ecf_rows)
    assert all(0 <= row["imaginary"] <= 2 for row in ecf_rows)
    assert len(stat_rows) == 4
    assert all(row["label"].startswith("t=") for row in stat_rows)
    assert stat_rows[0]["value"] >= stat_rows[-1]["value"]

    config_by_id = {
        component["componentInstanceId"]: component["config"]
        for component in payload["components"]
    }
    distribution_config = config_by_id["CHART-DISTSHAPE-001.distribution.0"]
    ecf_config = config_by_id["CHART-DISTSHAPE-001.ecf.0"]
    stat_config = config_by_id["CHART-DISTSHAPE-001.stat.0"]
    assert "x_min" not in distribution_config
    assert "x_max" not in distribution_config
    assert "y_max" not in ecf_config
    assert "x_max" not in stat_config
