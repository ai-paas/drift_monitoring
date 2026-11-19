from __future__ import annotations

from pathlib import Path

from admin_server.app.main import _scenario_from_test_data_metadata


def test_case002_connection_uses_tail_shape_recommendations_and_long_horizon_profile() -> None:
    metadata = {
        "case_id": "CASE-002",
        "case_name": "numeric_tail_and_shape_change",
        "data_file": "data.csv.gz",
        "drift_start": "2026-07-01 00:00:00",
        "transition_minutes": 86400,
        "columns": [
            "timestamp",
            "case_id",
            "sample_id",
            "window_id",
            "period",
            "x",
            "tail_weight",
            "mixture_component",
        ],
    }

    scenario = _scenario_from_test_data_metadata(Path("CASE-002_numeric_tail_and_shape_change"), metadata)

    assert scenario["adapter"]["adapterType"] == "test_db_numeric_distribution_window"
    assert scenario["adapter"]["sourceConfig"]["valuePath"] == "$.x"
    recommendations = scenario["recommendedAnalyses"]
    assert [item["methodVariantKey"] for item in recommendations] == [
        "TWO_SAMPLE_EPPS_SINGLETON",
        "ONE_SAMPLE_ANDERSON_DARLING",
        "TAIL_SENSITIVE_AD",
        "WASSERSTEIN_APPROX_HISTOGRAM",
    ]
    assert recommendations[0]["chartId"] == "CHART-DISTSHAPE-001"
    assert recommendations[0]["representativeCaseId"] == "CASE-002"
    assert recommendations[0]["replayProfileId"] == "long_horizon_120d"
    assert recommendations[0]["runtimeMethodKey"] == "generic_distribution_ecdf_window"
    assert recommendations[0]["calibratedWindowConfig"] == {"bucketResolution": "1440m", "lookbackBuckets": 1}
    assert recommendations[0]["calibratedParams"]["variant_id"] == "TWO_SAMPLE_EPPS_SINGLETON"
    assert recommendations[0]["calibratedParams"]["value_col"] == "value"
    assert recommendations[0]["calibratedParams"]["alpha"] == 0.05
    assert recommendations[3]["chartId"] == "CHART-DIST-001"
    assert recommendations[3]["calibratedWindowConfig"] == {"bucketResolution": "1440m", "lookbackBuckets": 1}

    default_profile = scenario["replayProfiles"][0]
    assert default_profile["profileId"] == "long_horizon_120d"
    assert scenario["feeder"]["startTime"] == "2026-06-01T00:00:00Z"
    assert scenario["feeder"]["replayWindow"]["end"] == "2026-09-29T00:00:00Z"
    assert scenario["adapter"]["aggregateIntervalMinutes"] == 1440
    assert scenario["tick"]["logicalMinutesPerTick"] == 1440
    assert scenario["tick"]["tickCount"] == 120


def test_case003_connection_uses_variance_recommendations_and_daily_profile() -> None:
    metadata = {
        "case_id": "CASE-003",
        "case_name": "numeric_variance_spread",
        "data_file": "data.csv.gz",
        "drift_start": "2026-07-01 00:00:00",
        "columns": [
            "timestamp",
            "case_id",
            "sample_id",
            "window_id",
            "period",
            "x",
            "std_target",
            "abs_deviation",
        ],
    }

    scenario = _scenario_from_test_data_metadata(Path("CASE-003_numeric_variance_spread"), metadata)

    assert scenario["adapter"]["adapterType"] == "test_db_numeric_distribution_window"
    assert scenario["adapter"]["sourceConfig"]["valuePath"] == "$.x"
    recommendations = scenario["recommendedAnalyses"]
    assert [item["methodVariantKey"] for item in recommendations] == [
        "F_TEST_EQUAL_VARIANCE",
        "BROWN_FORSYTHE_MEDIAN_CENTER",
    ]
    assert recommendations[0]["chartId"] == "CHART-VAR-001"
    assert recommendations[0]["replayProfileId"] == "case003_daily_45d"
    assert recommendations[0]["runtimeMethodKey"] == "generic_statistical_test_window"
    assert recommendations[0]["calibratedWindowConfig"] == {"bucketResolution": "1440m", "lookbackBuckets": 1}
    assert recommendations[0]["calibratedParams"]["variant_id"] == "F_TEST_EQUAL_VARIANCE"
    assert recommendations[0]["calibratedParams"]["value_col"] == "value"
    assert recommendations[1]["calibratedWindowConfig"] == {"bucketResolution": "1440m", "lookbackBuckets": 1}

    default_profile = scenario["replayProfiles"][0]
    assert default_profile["profileId"] == "case003_daily_45d"
    assert scenario["feeder"]["startTime"] == "2026-06-16T00:00:00Z"
    assert scenario["feeder"]["replayWindow"]["end"] == "2026-07-31T00:00:00Z"
    assert scenario["adapter"]["aggregateIntervalMinutes"] == 1440
    assert scenario["tick"]["logicalMinutesPerTick"] == 1440
    assert scenario["tick"]["tickCount"] == 45


def test_case004_connection_uses_psi_recommendation_and_two_day_window() -> None:
    metadata = {
        "case_id": "CASE-004",
        "case_name": "binned_numeric_population_shift",
        "data_file": "data.csv.gz",
        "drift_start": "2026-07-01 00:00:00",
        "columns": [
            "timestamp",
            "case_id",
            "sample_id",
            "window_id",
            "period",
            "score",
            "score_bin",
            "bin_index",
        ],
    }

    scenario = _scenario_from_test_data_metadata(Path("CASE-004_binned_numeric_population_shift"), metadata)

    assert scenario["adapter"]["adapterType"] == "test_db_numeric_distribution_window"
    assert scenario["adapter"]["sourceConfig"]["valuePath"] == "$.score"
    recommendations = scenario["recommendedAnalyses"]
    assert recommendations[0]["chartId"] == "CHART-PSI-001"
    assert recommendations[0]["methodVariantKey"] == "NUMERIC_BINNED_PSI"
    assert recommendations[0]["replayProfileId"] == "demo_4h"
    assert recommendations[0]["runtimeMethodKey"] == "psi_numeric_binned"
    assert recommendations[0]["calibratedWindowConfig"] == {"bucketResolution": "60m", "lookbackBuckets": 1}
    assert recommendations[0]["calibratedParams"]["variant_id"] == "NUMERIC_BINNED_PSI"
    assert recommendations[0]["calibratedParams"]["value_col"] == "value"
    assert recommendations[0]["calibratedParams"]["threshold"] == 1.0

    default_profile = scenario["replayProfiles"][0]
    assert default_profile["profileId"] == "demo_4h"
    assert scenario["feeder"]["startTime"] == "2026-06-30T22:00:00Z"
    assert scenario["feeder"]["replayWindow"]["end"] == "2026-07-01T02:00:00Z"
    assert scenario["adapter"]["aggregateIntervalMinutes"] == 60
    assert scenario["tick"]["logicalMinutesPerTick"] == 60
    assert scenario["tick"]["tickCount"] == 4
    validation_profile = next(profile for profile in scenario["replayProfiles"] if profile["profileId"] == "validation_2d")
    assert validation_profile["aggregateIntervalMinutes"] == 240
    assert validation_profile["tickCount"] == 288


def test_case005_connection_uses_categorical_adapter_and_hourly_bucket_profile() -> None:
    metadata = {
        "case_id": "CASE-005",
        "case_name": "categorical_proportion_shift",
        "data_file": "data.csv.gz",
        "drift_start": "2026-07-01 00:00:00",
        "columns": [
            "timestamp",
            "case_id",
            "sample_id",
            "window_id",
            "period",
            "category",
            "category_weight_c",
        ],
    }

    scenario = _scenario_from_test_data_metadata(Path("CASE-005_categorical_proportion_shift"), metadata)

    assert scenario["adapter"]["adapterType"] == "test_db_categorical_count_window"
    assert scenario["adapter"]["sourceConfig"]["categoryPath"] == "$.category"
    assert scenario["methodAssignment"]["featureId"] == "category"
    recommendations = scenario["recommendedAnalyses"]
    assert recommendations[0]["chartId"] == "CHART-PSI-001"
    assert recommendations[0]["methodVariantKey"] == "CATEGORICAL_PSI"
    assert recommendations[0]["runtimeMethodKey"] == "generic_probability_distance_window"
    assert recommendations[0]["replayProfileId"] == "demo_4h"
    assert recommendations[0]["calibratedWindowConfig"] == {"bucketResolution": "60m", "lookbackBuckets": 1}
    assert recommendations[0]["calibratedParams"]["variant_id"] == "CATEGORICAL_PSI"
    assert recommendations[0]["calibratedParams"]["category_col"] == "category"
    assert recommendations[0]["calibratedParams"]["count_col"] == "count"
    assert recommendations[0]["calibratedParams"]["threshold"] == 0.1

    default_profile = scenario["replayProfiles"][0]
    assert default_profile["profileId"] == "demo_4h"
    assert scenario["feeder"]["startTime"] == "2026-06-30T22:00:00Z"
    assert scenario["feeder"]["replayWindow"]["end"] == "2026-07-01T02:00:00Z"
    assert scenario["adapter"]["aggregateIntervalMinutes"] == 60
    assert scenario["tick"]["logicalMinutesPerTick"] == 60
    assert scenario["tick"]["tickCount"] == 4

    validation_profile = next(profile for profile in scenario["replayProfiles"] if profile["profileId"] == "validation_2d")
    assert validation_profile["startTime"] == "2026-06-30T00:00:00Z"
    assert validation_profile["endTime"] == "2026-07-02T00:00:00Z"
    assert validation_profile["aggregateIntervalMinutes"] == 60
    assert validation_profile["logicalMinutesPerTick"] == 60
    assert validation_profile["tickCount"] == 48


def test_case006_connection_uses_binary_event_stream_recommendation_and_hourly_profile() -> None:
    metadata = {
        "case_id": "CASE-006",
        "case_name": "binary_event_rate_shift",
        "data_file": "data.csv.gz",
        "drift_start": "2026-07-01 00:00:00",
        "columns": [
            "timestamp",
            "case_id",
            "sample_id",
            "window_id",
            "period",
            "event",
            "event_probability",
            "group",
        ],
    }

    scenario = _scenario_from_test_data_metadata(Path("CASE-006_binary_event_rate_shift"), metadata)

    assert scenario["adapter"]["adapterType"] == "test_db_numeric_distribution_window"
    assert scenario["adapter"]["sourceConfig"]["valuePath"] == "$.event"
    assert scenario["methodAssignment"]["featureId"] == "score"
    recommendations = scenario["recommendedAnalyses"]
    assert recommendations[0]["chartId"] == "CHART-STREAM-001"
    assert recommendations[0]["methodVariantKey"] == "ADWIN_MEAN_STREAM"
    assert recommendations[0]["representativeCaseId"] == "CASE-006"
    assert recommendations[0]["runtimeMethodKey"] == "adwin_mean_stream"
    assert recommendations[0]["replayProfileId"] == "demo_4h"
    assert recommendations[0]["calibratedWindowConfig"] == {"bucketResolution": "60m", "lookbackBuckets": 1}
    assert recommendations[0]["calibratedParams"]["variant_id"] == "ADWIN_MEAN_STREAM"
    assert recommendations[0]["calibratedParams"]["meanShiftThreshold"] == 0.12
    assert recommendations[0]["calibratedParams"]["useAlgorithmImpl"] is False
    assert recommendations[1]["methodVariantKey"] == "CATEGORICAL_PSI"
    assert recommendations[1]["replayProfileId"] == "boundary_4h"

    default_profile = scenario["replayProfiles"][0]
    assert default_profile["profileId"] == "demo_4h"
    assert scenario["feeder"]["startTime"] == "2026-06-30T22:00:00Z"
    assert scenario["feeder"]["replayWindow"]["end"] == "2026-07-01T02:00:00Z"
    assert scenario["adapter"]["aggregateIntervalMinutes"] == 60
    assert scenario["tick"]["logicalMinutesPerTick"] == 60
    assert scenario["tick"]["tickCount"] == 4

    boundary_profile = next(profile for profile in scenario["replayProfiles"] if profile["profileId"] == "boundary_4h")
    assert boundary_profile["aggregateIntervalMinutes"] == 240
    assert boundary_profile["logicalMinutesPerTick"] == 240
    assert boundary_profile["tickCount"] == 1

    validation_profile = next(profile for profile in scenario["replayProfiles"] if profile["profileId"] == "validation_2d")
    assert validation_profile["startTime"] == "2026-06-30T00:00:00Z"
    assert validation_profile["endTime"] == "2026-07-02T00:00:00Z"
    assert validation_profile["aggregateIntervalMinutes"] == 60
    assert validation_profile["logicalMinutesPerTick"] == 60
    assert validation_profile["tickCount"] == 48


def test_case007_connection_uses_probability_vector_categorical_psi_and_hourly_profile() -> None:
    metadata = {
        "case_id": "CASE-007",
        "case_name": "probability_vector_shift",
        "data_file": "data.csv.gz",
        "drift_start": "2026-07-01 00:00:00",
        "columns": [
            "timestamp",
            "case_id",
            "sample_id",
            "window_id",
            "period",
            "category",
            "class_label",
            "p0",
            "p1",
            "p2",
            "p3",
            "p4",
        ],
    }

    scenario = _scenario_from_test_data_metadata(Path("CASE-007_probability_vector_shift"), metadata)

    assert scenario["adapter"]["adapterType"] == "test_db_categorical_count_window"
    assert scenario["adapter"]["sourceConfig"]["categoryPath"] == "$.category"
    assert scenario["methodAssignment"]["featureId"] == "category"
    recommendations = scenario["recommendedAnalyses"]
    assert recommendations[0]["chartId"] == "CHART-PSI-001"
    assert recommendations[0]["methodVariantKey"] == "CATEGORICAL_PSI"
    assert recommendations[0]["representativeCaseId"] == "CASE-007"
    assert recommendations[0]["runtimeMethodKey"] == "generic_probability_distance_window"
    assert recommendations[0]["replayProfileId"] == "demo_4h"
    assert recommendations[0]["calibratedWindowConfig"] == {"bucketResolution": "60m", "lookbackBuckets": 1}
    assert recommendations[0]["calibratedParams"]["variant_id"] == "CATEGORICAL_PSI"
    assert recommendations[0]["calibratedParams"]["threshold"] == 0.1

    default_profile = scenario["replayProfiles"][0]
    assert default_profile["profileId"] == "demo_4h"
    assert scenario["feeder"]["startTime"] == "2026-06-30T22:00:00Z"
    assert scenario["feeder"]["replayWindow"]["end"] == "2026-07-01T02:00:00Z"
    assert scenario["adapter"]["aggregateIntervalMinutes"] == 60
    assert scenario["tick"]["logicalMinutesPerTick"] == 60
    assert scenario["tick"]["tickCount"] == 4

    validation_profile = next(profile for profile in scenario["replayProfiles"] if profile["profileId"] == "validation_2d")
    assert validation_profile["startTime"] == "2026-06-30T00:00:00Z"
    assert validation_profile["endTime"] == "2026-07-02T00:00:00Z"
    assert validation_profile["aggregateIntervalMinutes"] == 60
    assert validation_profile["logicalMinutesPerTick"] == 60
    assert validation_profile["tickCount"] == 48


def test_case008_connection_uses_multivariate_mmd_and_hourly_profile() -> None:
    metadata = {
        "case_id": "CASE-008",
        "case_name": "multivariate_embedding_shift",
        "data_file": "data.csv.gz",
        "drift_start": "2026-07-01 00:00:00",
        "columns": [
            "timestamp",
            "case_id",
            "sample_id",
            "window_id",
            "period",
            "drift_start",
            "abrupt_strength",
            "gradual_strength",
            "season_factor",
            "cycle_phase",
            "embedding_x",
            "embedding_y",
            "centroid_x",
            "centroid_y",
        ],
    }

    scenario = _scenario_from_test_data_metadata(Path("CASE-008_multivariate_embedding_shift"), metadata)

    assert scenario["adapter"]["adapterType"] == "test_db_multivariate_window"
    assert scenario["adapter"]["sourceConfig"]["featureColumns"] == ["centroid_x", "embedding_x", "embedding_y"]
    assert scenario["methodAssignment"]["featureId"] == "multivariate"
    recommendations = scenario["recommendedAnalyses"]
    assert recommendations[0]["chartId"] == "CHART-MV-002"
    assert recommendations[0]["methodVariantKey"] == "LINEAR_TIME_MMD"
    assert recommendations[0]["representativeCaseId"] == "CASE-008"
    assert recommendations[0]["runtimeMethodKey"] == "linear_time_mmd"
    assert recommendations[0]["replayProfileId"] == "demo_4h"
    assert recommendations[0]["calibratedWindowConfig"] == {"bucketResolution": "60m", "lookbackBuckets": 1}
    assert recommendations[0]["calibratedParams"]["feature_cols"] == ["centroid_x", "embedding_x", "embedding_y"]
    assert recommendations[0]["calibratedParams"]["threshold"] == 0.1

    default_profile = scenario["replayProfiles"][0]
    assert default_profile["profileId"] == "demo_4h"
    assert scenario["feeder"]["startTime"] == "2026-06-30T22:00:00Z"
    assert scenario["feeder"]["replayWindow"]["end"] == "2026-07-01T02:00:00Z"
    assert scenario["adapter"]["aggregateIntervalMinutes"] == 60
    assert scenario["tick"]["logicalMinutesPerTick"] == 60
    assert scenario["tick"]["tickCount"] == 4

    validation_profile = next(profile for profile in scenario["replayProfiles"] if profile["profileId"] == "validation_2d")
    assert validation_profile["startTime"] == "2026-06-30T00:00:00Z"
    assert validation_profile["endTime"] == "2026-07-02T00:00:00Z"
    assert validation_profile["aggregateIntervalMinutes"] == 60
    assert validation_profile["logicalMinutesPerTick"] == 60
    assert validation_profile["tickCount"] == 48


def test_case009_connection_uses_ocdd_anomaly_recommendation_and_boundary_profile() -> None:
    metadata = {
        "case_id": "CASE-009",
        "case_name": "multivariate_local_density_or_anomaly",
        "data_file": "data.csv.gz",
        "drift_start": "2026-07-01 00:00:00",
        "columns": [
            "timestamp",
            "case_id",
            "sample_id",
            "window_id",
            "period",
            "drift_start",
            "abrupt_strength",
            "gradual_strength",
            "season_factor",
            "cycle_phase",
            "embedding_x",
            "embedding_y",
            "cluster",
            "anomaly_score",
        ],
    }

    scenario = _scenario_from_test_data_metadata(Path("CASE-009_multivariate_local_density_or_anomaly"), metadata)

    assert scenario["adapter"]["adapterType"] == "test_db_multivariate_window"
    assert scenario["adapter"]["sourceConfig"]["featureColumns"] == ["anomaly_score", "embedding_x", "embedding_y"]
    assert scenario["methodAssignment"]["featureId"] == "multivariate"
    recommendations = scenario["recommendedAnalyses"]
    assert recommendations[0]["chartId"] == "CHART-ANOM-001"
    assert recommendations[0]["methodVariantKey"] == "ISOLATION_FOREST_DRIFT_SCORE"
    assert recommendations[0]["representativeCaseId"] == "CASE-009"
    assert recommendations[0]["runtimeMethodKey"] == "isolation_forest_drift_score"
    assert recommendations[0]["replayProfileId"] == "demo_4h"
    assert recommendations[0]["calibratedWindowConfig"] == {"bucketResolution": "240m", "lookbackBuckets": 1}
    assert recommendations[0]["calibratedParams"]["feature_cols"] == ["anomaly_score", "embedding_x", "embedding_y"]
    assert recommendations[0]["calibratedParams"]["anomaly_rate_threshold"] == 0.1

    default_profile = scenario["replayProfiles"][0]
    assert default_profile["profileId"] == "demo_4h"
    assert scenario["feeder"]["startTime"] == "2026-06-30T22:00:00Z"
    assert scenario["feeder"]["replayWindow"]["end"] == "2026-07-01T02:00:00Z"
    assert scenario["adapter"]["aggregateIntervalMinutes"] == 240
    assert scenario["tick"]["logicalMinutesPerTick"] == 240
    assert scenario["tick"]["tickCount"] == 1

    validation_profile = next(profile for profile in scenario["replayProfiles"] if profile["profileId"] == "validation_2d")
    assert validation_profile["startTime"] == "2026-06-30T00:00:00Z"
    assert validation_profile["endTime"] == "2026-07-02T00:00:00Z"
    assert validation_profile["aggregateIntervalMinutes"] == 240
    assert validation_profile["logicalMinutesPerTick"] == 10
    assert validation_profile["tickCount"] == 288


def test_case012_connection_uses_prediction_log_adapter_and_error_recommendations() -> None:
    metadata = {
        "case_id": "CASE-012",
        "case_name": "supervised_concept_boundary_shift",
        "data_file": "data.csv.gz",
        "drift_start": "2026-07-01 00:00:00",
        "columns": [
            "timestamp",
            "case_id",
            "sample_id",
            "window_id",
            "period",
            "feature_1",
            "feature_2",
            "label",
            "model_prediction",
            "concept_score",
        ],
    }

    scenario = _scenario_from_test_data_metadata(Path("CASE-012_supervised_concept_boundary_shift"), metadata)

    assert scenario["adapter"]["adapterType"] == "test_db_prediction_log_stream"
    assert scenario["adapter"]["sourceConfig"]["valuePath"] == "$.concept_score"
    assert scenario["methodAssignment"]["featureId"] == "error_rate"
    recommendations = scenario["recommendedAnalyses"]
    assert [item["methodVariantKey"] for item in recommendations] == [
        "HDDM_A_HOEFFDING_BOUND",
        "EDDM_GRADUAL_DRIFT",
        "DDM_STANDARD",
    ]
    assert recommendations[0]["chartId"] == "CHART-ERR-005"
    assert recommendations[0]["representativeCaseId"] == "CASE-012"
    assert recommendations[0]["replayProfileId"] == "long_horizon_120d"
    assert recommendations[0]["calibratedWindowConfig"] == {"bucketResolution": "1440m", "lookbackBuckets": 120}
    assert recommendations[0]["calibratedParams"]["error_col"] == "error"
    assert recommendations[0]["calibratedParams"]["useAlgorithmImpl"] is True
    assert recommendations[0]["calibratedParams"]["maxStatePoints"] == 172800
    assert recommendations[0]["calibratedParams"]["drift_confidence"] == 0.002
    assert recommendations[1]["replayProfileId"] == "long_horizon_120d"
    assert recommendations[2]["replayProfileId"] == "long_horizon_120d"
    assert recommendations[2]["calibratedParams"]["useAlgorithmImpl"] is False
    assert recommendations[2]["calibratedParams"]["errorRateShiftThreshold"] == 0.02
    long_horizon = next(profile for profile in scenario["replayProfiles"] if profile["profileId"] == "long_horizon_120d")
    assert long_horizon["startTime"] == "2026-06-01T00:00:00Z"
    assert long_horizon["endTime"] == "2026-09-29T00:00:00Z"
    assert long_horizon["maxRows"] == 172800
    assert long_horizon["aggregateIntervalMinutes"] == 1440
    assert long_horizon["logicalMinutesPerTick"] == 1440
    assert long_horizon["tickCount"] == 120


def test_case013_connection_uses_topic_distribution_boundary_profile() -> None:
    metadata = {
        "case_id": "CASE-013",
        "case_name": "text_topic_semantic_shift",
        "data_file": "data.csv.gz",
        "drift_start": "2026-07-01 00:00:00",
        "columns": [
            "timestamp",
            "case_id",
            "sample_id",
            "window_id",
            "period",
            "drift_start",
            "abrupt_strength",
            "gradual_strength",
            "season_factor",
            "cycle_phase",
            "topic",
            "semantic_x",
            "technical_topic_weight",
        ],
    }

    scenario = _scenario_from_test_data_metadata(Path("CASE-013_text_topic_semantic_shift"), metadata)

    assert scenario["adapter"]["adapterType"] == "test_db_multivariate_window"
    assert scenario["adapter"]["sourceConfig"]["featureColumns"] == ["semantic_x", "technical_topic_weight"]
    assert "topic" in scenario["adapter"]["sourceConfig"]["attributeColumns"]
    recommendations = scenario["recommendedAnalyses"]
    assert [item["methodVariantKey"] for item in recommendations] == [
        "TOPIC_DISTRIBUTION_SHIFT",
        "QUERY_CENTROID_COSINE_SHIFT",
    ]
    assert recommendations[0]["chartId"] == "CHART-TEXT-001"
    assert recommendations[0]["representativeCaseId"] == "CASE-018"
    assert recommendations[0]["runtimeMethodKey"] == "topic_distribution_shift"
    assert recommendations[0]["replayProfileId"] == "boundary_4h"
    assert recommendations[0]["calibratedWindowConfig"] == {"bucketResolution": "240m", "lookbackBuckets": 1}
    assert recommendations[0]["calibratedParams"]["variant_id"] == "TOPIC_DISTRIBUTION_SHIFT"
    assert recommendations[0]["calibratedParams"]["topic_col"] == "topic"
    assert recommendations[0]["calibratedParams"]["threshold"] == 0.1

    default_profile = scenario["replayProfiles"][0]
    assert default_profile["profileId"] == "boundary_4h"
    assert scenario["feeder"]["startTime"] == "2026-06-30T22:00:00Z"
    assert scenario["feeder"]["replayWindow"]["end"] == "2026-07-01T02:00:00Z"
    assert scenario["adapter"]["aggregateIntervalMinutes"] == 240
    assert scenario["tick"]["logicalMinutesPerTick"] == 240
    assert scenario["tick"]["tickCount"] == 1


def test_case014_connection_uses_explanation_boundary_profile() -> None:
    metadata = {
        "case_id": "CASE-014",
        "case_name": "explanation_importance_shift",
        "data_file": "data.csv.gz",
        "drift_start": "2026-07-01 00:00:00",
        "columns": [
            "timestamp",
            "case_id",
            "sample_id",
            "window_id",
            "period",
            "drift_start",
            "abrupt_strength",
            "gradual_strength",
            "season_factor",
            "cycle_phase",
            "importance_a",
            "importance_b",
            "importance_c",
            "top_feature",
        ],
    }

    scenario = _scenario_from_test_data_metadata(Path("CASE-014_explanation_importance_shift"), metadata)

    assert scenario["adapter"]["adapterType"] == "test_db_multivariate_window"
    assert scenario["adapter"]["sourceConfig"]["featureColumns"] == ["importance_a", "importance_b", "importance_c"]
    recommendations = scenario["recommendedAnalyses"]
    assert [item["methodVariantKey"] for item in recommendations] == [
        "GLOBAL_IMPORTANCE_RANK_SHIFT",
        "SHAP_VALUE_DISTRIBUTION_TEST",
    ]
    assert recommendations[0]["chartId"] == "CHART-EXPL-001"
    assert recommendations[0]["representativeCaseId"] == "CASE-017"
    assert recommendations[0]["runtimeMethodKey"] == "global_importance_rank_shift"
    assert recommendations[0]["replayProfileId"] == "boundary_4h"
    assert recommendations[0]["calibratedWindowConfig"] == {"bucketResolution": "240m", "lookbackBuckets": 1}
    assert recommendations[0]["calibratedParams"]["shap_cols"] == ["importance_a", "importance_b", "importance_c"]
    assert recommendations[1]["runtimeMethodKey"] == "shap_value_distribution_test"
    assert recommendations[1]["replayProfileId"] == "boundary_4h"

    default_profile = scenario["replayProfiles"][0]
    assert default_profile["profileId"] == "boundary_4h"
    assert scenario["feeder"]["startTime"] == "2026-06-30T22:00:00Z"
    assert scenario["feeder"]["replayWindow"]["end"] == "2026-07-01T02:00:00Z"
    assert scenario["adapter"]["aggregateIntervalMinutes"] == 240
    assert scenario["tick"]["logicalMinutesPerTick"] == 240
    assert scenario["tick"]["tickCount"] == 1


def test_case015_connection_uses_uncertainty_boundary_profile() -> None:
    metadata = {
        "case_id": "CASE-015",
        "case_name": "annotation_label_quality_shift",
        "data_file": "data.csv.gz",
        "drift_start": "2026-07-01 00:00:00",
        "columns": [
            "timestamp",
            "case_id",
            "sample_id",
            "window_id",
            "period",
            "drift_start",
            "abrupt_strength",
            "gradual_strength",
            "season_factor",
            "cycle_phase",
            "true_label",
            "observed_label",
            "annotator",
            "label_noise_probability",
            "annotation_confidence",
        ],
    }

    scenario = _scenario_from_test_data_metadata(Path("CASE-015_annotation_label_quality_shift"), metadata)

    assert scenario["adapter"]["adapterType"] == "test_db_multivariate_window"
    assert scenario["adapter"]["sourceConfig"]["featureColumns"] == ["annotation_confidence", "label_noise_probability"]
    recommendations = scenario["recommendedAnalyses"]
    assert [item["methodVariantKey"] for item in recommendations] == [
        "ENTROPY_DRIFT",
        "SOFTMAX_CONFIDENCE_DRIFT",
    ]
    assert recommendations[0]["chartId"] == "CHART-UNC-001"
    assert recommendations[0]["runtimeMethodKey"] == "entropy_drift"
    assert recommendations[0]["replayProfileId"] == "boundary_4h"
    assert recommendations[0]["calibratedWindowConfig"] == {"bucketResolution": "240m", "lookbackBuckets": 1}
    assert recommendations[0]["calibratedParams"]["probability_cols"] == ["annotation_confidence", "label_noise_probability"]
    assert recommendations[1]["runtimeMethodKey"] == "softmax_confidence_drift"
    assert recommendations[1]["replayProfileId"] == "boundary_4h"

    default_profile = scenario["replayProfiles"][0]
    assert default_profile["profileId"] == "boundary_4h"
    assert scenario["feeder"]["startTime"] == "2026-06-30T22:00:00Z"
    assert scenario["feeder"]["replayWindow"]["end"] == "2026-07-01T02:00:00Z"
    assert scenario["adapter"]["aggregateIntervalMinutes"] == 240
    assert scenario["tick"]["logicalMinutesPerTick"] == 240
    assert scenario["tick"]["tickCount"] == 1


def test_case016_connection_uses_representation_boundary_profile() -> None:
    metadata = {
        "case_id": "CASE-016",
        "name": "graph_or_feature_map_representation_shift",
        "row_count": 525600,
        "frequency": "1min",
        "start_time": "2026-01-01T00:00:00Z",
        "drift_start": "2026-07-01T00:00:00Z",
        "columns": [
            "event_time",
            "drift_start",
            "abrupt_strength",
            "gradual_strength",
            "season_factor",
            "cycle_phase",
            "activation",
            "representation_shift",
            "layer",
            "node_id",
        ],
    }

    scenario = _scenario_from_test_data_metadata(Path("CASE-016_graph_or_feature_map_representation_shift"), metadata)

    assert scenario["adapter"]["adapterType"] == "test_db_multivariate_window"
    assert scenario["adapter"]["sourceConfig"]["featureColumns"] == ["activation", "representation_shift"]
    recommendations = scenario["recommendedAnalyses"]
    assert [item["methodVariantKey"] for item in recommendations] == [
        "MODEL_FEATURE_MAP_MMD",
        "GRAPH_EMBEDDING_MMD",
    ]
    assert recommendations[0]["chartId"] == "CHART-REP-001"
    assert recommendations[0]["runtimeMethodKey"] == "model_feature_map_mmd"
    assert recommendations[0]["replayProfileId"] == "boundary_4h"
    assert recommendations[0]["calibratedWindowConfig"] == {"bucketResolution": "240m", "lookbackBuckets": 1}
    assert recommendations[0]["calibratedParams"]["feature_cols"] == ["activation", "representation_shift"]
    assert recommendations[1]["chartId"] == "CHART-REP-003"
    assert recommendations[1]["runtimeMethodKey"] == "graph_embedding_mmd"
    assert recommendations[1]["replayProfileId"] == "boundary_4h"
    assert recommendations[1]["calibratedParams"]["embedding_cols"] == ["activation", "representation_shift"]

    default_profile = scenario["replayProfiles"][0]
    assert default_profile["profileId"] == "boundary_4h"
    assert scenario["feeder"]["startTime"] == "2026-06-30T22:00:00Z"
    assert scenario["feeder"]["replayWindow"]["end"] == "2026-07-01T02:00:00Z"
    assert scenario["adapter"]["aggregateIntervalMinutes"] == 240
    assert scenario["tick"]["logicalMinutesPerTick"] == 240
    assert scenario["tick"]["tickCount"] == 1


def test_case019_object_detection_confidence_uses_uncertainty_recommendation() -> None:
    metadata = {
        "case_id": "CASE-019-FUS-L-CRACK",
        "case_name": "object_detection_confidence",
        "data_file": "data.csv.gz",
        "drift_start": "2026-07-21T00:00:00Z",
        "start_inclusive": "2026-07-06T00:06:12Z",
        "end_inclusive": "2026-08-04T22:53:09Z",
        "columns": [
            "timestamp",
            "case_id",
            "sample_id",
            "period",
            "image_category",
            "image_class",
            "confidence",
            "metric",
        ],
    }

    scenario = _scenario_from_test_data_metadata(
        Path("CASE-019-FUS-L-CRACK_object_detection_confidence"), metadata
    )

    assert scenario["adapter"]["adapterType"] == "test_db_multivariate_window"
    assert scenario["adapter"]["sourceConfig"]["featureColumns"] == ["confidence"]
    assert scenario["adapter"]["sourceConfig"]["attributeColumns"] == [
        "period",
        "image_category",
        "image_class",
    ]
    recommendations = scenario["recommendedAnalyses"]
    assert [item["methodVariantKey"] for item in recommendations] == [
        "SOFTMAX_CONFIDENCE_DRIFT",
        "ADWIN_MEAN_STREAM",
    ]
    assert recommendations[0]["chartId"] == "CHART-UNC-001"
    assert recommendations[0]["runtimeMethodKey"] == "softmax_confidence_drift"
    assert recommendations[0]["calibratedParams"]["confidence_col"] == "confidence"
    assert recommendations[0]["calibratedParams"]["min_reference_size"] == 5
    assert recommendations[0]["calibratedWindowConfig"] == {
        "bucketResolution": "10m",
        "lookbackBuckets": 1,
    }
    assert recommendations[0]["replayProfileId"] == "object_detection_full_range"
    assert scenario["replayProfiles"][0]["profileId"] == "object_detection_full_range"
    assert scenario["feeder"]["startTime"] == "2026-07-06T00:00:00Z"
    assert scenario["feeder"]["replayWindow"]["end"] == "2026-08-04T23:00:00Z"
    assert scenario["adapter"]["aggregateIntervalMinutes"] == 10
    assert scenario["tick"]["logicalMinutesPerTick"] == 43140
    assert scenario["tick"]["tickCount"] == 1
