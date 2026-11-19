from __future__ import annotations

import csv
import json
import logging
from logging.handlers import RotatingFileHandler
import re
import sys
from datetime import datetime, timedelta, timezone
from urllib.request import urlopen
from pathlib import Path
from typing import Any

import uvicorn
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .clients.http import DownstreamClient
from .response import ok
from .settings import (
    ADMIN_SERVER_HOST,
    ADMIN_SERVER_PORT,
    DRIFT_SERVER_BASE_URL,
    LLM_INTERPRETATION_BASE_URL,
    REPORT_GALLERY_BASE_URL,
    REQUEST_TIMEOUT_SECONDS,
    TEST_FEEDER_BASE_URL,
)


app = FastAPI(title="Sprint 1 Admin Server")
CONTROL_PLANE_ROOT = Path(__file__).resolve().parents[2]
REPO_ROOT = CONTROL_PLANE_ROOT.parent
ADMIN_WEB_ROOT = CONTROL_PLANE_ROOT / "admin_server" / "web"
REPORT_CHARTS_ROOT = REPO_ROOT / "drift 보고서" / "charts"
TIMESERIES_WEB_ROOT = REPO_ROOT / "drift_metric_timeseries" / "web"
CHART_RUNTIME_ROOT = REPO_ROOT / "chart_runtime"
TEST_DATA_ROOT = REPO_ROOT / "테스트데이터"
ANCHOR_SCENARIO_PATH = CONTROL_PLANE_ROOT / "testing" / "harness" / "scenarios" / "case010_admin_e2e_anchor.json"
COMPATIBILITY_MATRIX_PATH = (
    CONTROL_PLANE_ROOT
    / "testing"
    / "harness"
    / "matrix"
    / "generated"
    / "sprint80_final"
    / "chart_method_compatibility_matrix.csv"
)
ADMIN_DEBUG_LOG_PATH = CONTROL_PLANE_ROOT / "runtime" / "admin_server_debug.log"
ADMIN_DEBUG_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
admin_debug_logger = logging.getLogger("drift_control_plane.admin_debug")
admin_debug_logger.setLevel(logging.INFO)
if not admin_debug_logger.handlers:
    handler = RotatingFileHandler(ADMIN_DEBUG_LOG_PATH, maxBytes=2_000_000, backupCount=3, encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    admin_debug_logger.addHandler(handler)
admin_debug_logger.propagate = False
drift = DownstreamClient(DRIFT_SERVER_BASE_URL, REQUEST_TIMEOUT_SECONDS)
test_feeder = DownstreamClient(TEST_FEEDER_BASE_URL, REQUEST_TIMEOUT_SECONDS)
llm = DownstreamClient(LLM_INTERPRETATION_BASE_URL, REQUEST_TIMEOUT_SECONDS)
state: dict[str, Any] = {"testMode": True, "lastLogicalNow": None, "tickCount": 0}

app.mount("/admin/static", StaticFiles(directory=ADMIN_WEB_ROOT), name="admin-static")
app.mount("/admin/report/charts", StaticFiles(directory=REPORT_CHARTS_ROOT), name="admin-report-charts")
app.mount("/admin/timeseries", StaticFiles(directory=TIMESERIES_WEB_ROOT), name="admin-timeseries")
app.mount("/chart_runtime", StaticFiles(directory=CHART_RUNTIME_ROOT), name="chart-runtime")


@app.get("/")
def root_ui() -> FileResponse:
    return FileResponse(ADMIN_WEB_ROOT / "index.html")


@app.get("/admin")
def admin_ui() -> FileResponse:
    return FileResponse(ADMIN_WEB_ROOT / "index.html")


@app.get("/api/admin/health")
def health() -> dict[str, Any]:
    return ok(
        {
            "database": False,
            "driftServer": drift.health_ok("/api/health"),
            "testFeederServer": test_feeder.health_ok("/api/test-feeder/health"),
            "llmServer": llm.health_ok("/api/health"),
            "testMode": state["testMode"],
        }
    )


@app.post("/api/admin/test/reset")
def test_reset(body: dict[str, Any]) -> dict[str, Any]:
    source_id = body.get("sourceId")
    feeder_response = test_feeder.post("/api/test-feeder/reset", body)
    drift_response = drift.post("/api/drift/test/reset", body)
    state["lastLogicalNow"] = None
    state["tickCount"] = 0
    return ok(
        {
            "sourceId": source_id,
            "testFeederReset": bool(feeder_response.get("ok")),
            "driftReset": bool(drift_response.get("ok")),
        }
    )


@app.post("/api/admin/sources")
def register_source(body: dict[str, Any]) -> dict[str, Any]:
    return drift.post("/api/drift/sources", body)


@app.post("/api/admin/adapters")
def register_adapter(body: dict[str, Any]) -> dict[str, Any]:
    return drift.post("/api/drift/adapters", body)


@app.get("/api/admin/adapters/{adapter_id}/status")
def adapter_status(adapter_id: str) -> dict[str, Any]:
    return drift.get(f"/api/drift/adapters/{adapter_id}/status")


@app.post("/api/admin/sources/{source_id}/method-assignments")
def register_method_assignment(source_id: str, body: dict[str, Any]) -> dict[str, Any]:
    return drift.post(f"/api/drift/sources/{source_id}/method-assignments", body)


@app.post("/api/admin/sources/{source_id}/method-assignments/{assignment_id}/analysis-charts")
def register_analysis_chart(source_id: str, assignment_id: str, body: dict[str, Any]) -> dict[str, Any]:
    payload = dict(body)
    payload.setdefault("chartDefinitionId", "chartdef-case010-adwin-stream")
    payload.setdefault(
        "chartDefinition",
        {
            "chartId": payload.get("chartId", "CHART-STREAM-001"),
            "title": payload.get("chartOptions", {}).get("title", "CASE-010 ADWIN stream analysis"),
        },
    )
    return drift.post(f"/api/drift/sources/{source_id}/method-assignments/{assignment_id}/analysis-charts", payload)


@app.post("/api/admin/test/tick")
def test_tick(body: dict[str, Any]) -> dict[str, Any]:
    logical_now = body.get("logicalNow")
    state["lastLogicalNow"] = logical_now
    state["tickCount"] = int(state.get("tickCount", 0)) + 1
    return ok({"logicalNow": logical_now, "tickCount": state["tickCount"]})


@app.get("/api/admin/anchor/case010/scenario")
def case010_anchor_scenario() -> dict[str, Any]:
    return ok(json.loads(ANCHOR_SCENARIO_PATH.read_text(encoding="utf-8")))


@app.get("/api/admin/test-data/connections")
# @managed-contract contract_id=admin_server.test_data_connections level=P1
def test_data_connections() -> dict[str, Any]:
    return ok({"connections": _test_data_connection_scenarios()})


@app.get("/api/admin/report/scenario-for-selection")
# @managed-contract contract_id=admin_server.scenario_for_selection level=P1
def scenario_for_selection(chartId: str, methodVariantKey: str) -> dict[str, Any]:
    scenario = _scenario_for_selection(chartId, methodVariantKey)
    return ok(scenario)


def _scenario_for_selection(chart_id: str, method_variant_key: str) -> dict[str, Any] | None:
    if not chart_id or not method_variant_key or not COMPATIBILITY_MATRIX_PATH.exists():
        return None
    with COMPATIBILITY_MATRIX_PATH.open("r", encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            if row.get("chartId") != chart_id or row.get("methodVariantKey") != method_variant_key:
                continue
            scenario_path = row.get("scenarioPath") or ""
            if not scenario_path:
                return None
            resolved = (CONTROL_PLANE_ROOT / scenario_path).resolve()
            if not resolved.is_relative_to(CONTROL_PLANE_ROOT.resolve()) or not resolved.exists():
                return None
            scenario = json.loads(resolved.read_text(encoding="utf-8"))
            scenario["_adminSelection"] = {
                "chartId": chart_id,
                "methodVariantKey": method_variant_key,
                "scenarioPath": scenario_path,
                "matrixRowId": row.get("matrixRowId"),
                "status": row.get("status"),
            }
            return scenario
    return None


def _test_data_connection_scenarios() -> list[dict[str, Any]]:
    if not TEST_DATA_ROOT.exists():
        return []
    scenarios: list[dict[str, Any]] = []
    for metadata_path in sorted(TEST_DATA_ROOT.glob("CASE-*/metadata.json")):
        try:
            metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
            scenarios.append(_scenario_from_test_data_metadata(metadata_path.parent, metadata))
        except (OSError, json.JSONDecodeError, ValueError) as exc:
            admin_debug_logger.info(
                json.dumps(
                    {
                        "event": "admin.test_data_connection.skip",
                        "metadataPath": str(metadata_path),
                        "error": str(exc),
                    },
                    ensure_ascii=False,
                )
            )
    return scenarios


def _scenario_from_test_data_metadata(case_dir: Path, metadata: dict[str, Any]) -> dict[str, Any]:
    case_id = str(metadata.get("case_id") or case_dir.name.split("_", 1)[0]).upper()
    case_name = str(metadata.get("case_name") or case_dir.name)
    source_id = f"{case_id.lower()}-dataset"
    adapter_id = f"{source_id}-adapter"
    assignment_id = f"assign-{source_id}"
    analysis_chart_id = f"analysis-{source_id}-stream"
    data_file = str(metadata.get("data_file") or "data.csv.gz")
    csv_path = f"../테스트데이터/{case_dir.name}/{data_file}"
    columns = [str(item) for item in metadata.get("columns", [])]
    adapter_type = _adapter_type_for_columns(columns)
    value_column = _value_column_for_columns(columns)
    feature_id = _feature_id_for_adapter(adapter_type, value_column)
    drift_start = _parse_metadata_time(metadata.get("drift_start") or metadata.get("start_inclusive"))
    data_start = _parse_metadata_time(metadata.get("start_inclusive")) if metadata.get("start_inclusive") else None
    data_end = _parse_metadata_time(metadata.get("end_inclusive")) if metadata.get("end_inclusive") else None
    replay_profiles = _replay_profiles_for_case(case_id, adapter_type, drift_start, data_start, data_end)
    default_replay_profile = replay_profiles[0]
    aggregate_interval_minutes = int(default_replay_profile["aggregateIntervalMinutes"])
    source_config = {
        "datasetCaseId": case_id,
        "columns": columns,
        "valuePath": f"$.{value_column}",
    }
    if adapter_type == "test_db_multivariate_window":
        source_config["featureColumns"] = _feature_columns_for_columns(columns)
        source_config["attributeColumns"] = [
            column
            for column in (
                "category",
                "label",
                "topic",
                "period",
                "top_feature",
                "layer",
                "node_group",
                "group",
                "image_category",
                "image_class",
            )
            if column in columns
        ]
    if adapter_type == "test_db_categorical_count_window":
        source_config["categoryPath"] = "$.category"
    recommended_analyses = _recommended_analyses_for_case(case_id, adapter_type)
    return {
        "scenarioId": f"{source_id}-connection",
        "mode": "A",
        "title": f"{case_id} {case_name}",
        "source": {
            "sourceId": source_id,
            "title": f"{case_id} {case_name}",
            "description": f"Root 테스트데이터 preset for {case_id}",
            "sourceType": "test_db",
            "sourceUrl": csv_path,
            "sourceConfig": {"datasetCaseId": case_id, "columns": columns},
        },
        "feeder": {
            "sourceId": source_id,
            "datasetCaseId": case_id,
            "csvPath": csv_path,
            "speedFactor": 60,
            "startTime": default_replay_profile["startTime"],
            "maxRows": default_replay_profile["maxRows"],
            "replayWindow": {
                "start": default_replay_profile["startTime"],
                "end": default_replay_profile["endTime"],
            },
        },
        "adapter": {
            "adapterId": adapter_id,
            "sourceId": source_id,
            "adapterType": adapter_type,
            "adapterTitle": f"{case_id} dataset adapter",
            "collectionIntervalMinutes": 10,
            "aggregateIntervalMinutes": aggregate_interval_minutes,
            "sourceConfig": {
                "table": "test_source.raw_event",
                "timeColumn": "event_time",
                **source_config,
            },
        },
        "methodAssignment": {
            "assignmentId": assignment_id,
            "adapterId": adapter_id,
            "featureId": feature_id,
            "methodVariantId": 123,
            "algorithmImplementationId": 45,
            "runtimeMethodKey": "adwin_mean_stream",
            "params": {"delta": 0.002, "meanShiftThreshold": 0.05, "useAlgorithmImpl": False},
            "threshold": {"eventLevel": "drift"},
            "windowConfig": {"bucketResolution": "10m", "lookbackBuckets": 144},
            "enabled": True,
        },
        "analysisChart": {
            "analysisChartId": analysis_chart_id,
            "chartId": "CHART-STREAM-001",
            "payloadAdapterKey": "adwin_mean_stream_to_chart_stream_001",
            "chartOptions": {"title": f"{case_id} dataset stream analysis"},
            "payloadAdapterConfig": {},
        },
        "tick": {
            "logicalMinutesPerTick": default_replay_profile["logicalMinutesPerTick"],
            "tickCount": default_replay_profile["tickCount"],
            "pollEveryTicks": default_replay_profile["pollEveryTicks"],
        },
        "replayProfiles": replay_profiles,
        "_adminConnection": {
            "source": "root_test_data",
            "metadataPath": f"../테스트데이터/{case_dir.name}/metadata.json",
            "rowCount": metadata.get("row_count"),
            "frequency": metadata.get("frequency"),
            "defaultReplayProfileId": default_replay_profile["profileId"],
            "replayProfiles": replay_profiles,
            "recommendedAnalyses": recommended_analyses,
        },
        "recommendedAnalyses": recommended_analyses,
    }


def _recommended_analyses_for_case(case_id: str, adapter_type: str) -> list[dict[str, Any]]:
    catalog: dict[str, list[dict[str, Any]]] = {
        "CASE-001": [
            _recommended_analysis("CHART-DIST-001", "WASSERSTEIN_1D_EXACT", "recommended", "numeric location shift에 적합한 분포 거리 차트", "CASE-004"),
            _recommended_analysis("CHART-EDF-001", "TWO_SAMPLE_KS_TWO_SIDED", "alternative", "reference/current 누적분포 차이를 확인", "CASE-004"),
            _recommended_analysis("CHART-PSI-001", "NUMERIC_BINNED_PSI", "alternative", "bin 기준 population shift를 운영 지표로 확인", "CASE-004"),
        ],
        "CASE-002": [
            _recommended_analysis("CHART-EDF-001", "TWO_SAMPLE_KS_TWO_SIDED", "recommended", "tail/shape 변화는 EDF 차트에서 가장 직접적으로 보임", "CASE-004"),
            _recommended_analysis("CHART-DIST-001", "WASSERSTEIN_APPROX_HISTOGRAM", "alternative", "분포 모양 변화의 크기를 거리로 요약", "CASE-004"),
        ],
        "CASE-003": [
            _recommended_analysis("CHART-VAR-001", "F_TEST_EQUAL_VARIANCE", "recommended", "variance/spread 변화 전용 검정", "CASE-004"),
            _recommended_analysis("CHART-VAR-001", "BROWN_FORSYTHE_MEDIAN_CENTER", "alternative", "이상치에 비교적 견고한 분산 변화 검정", "CASE-004"),
        ],
        "CASE-004": [
            _recommended_analysis("CHART-PSI-001", "NUMERIC_BINNED_PSI", "recommended", "binned numeric population shift의 대표 차트", "CASE-004"),
            _recommended_analysis("CHART-CAT-003", "BINNED_NUMERIC_L_INFINITY", "alternative", "가장 크게 움직인 bin을 강조", "CASE-004"),
            _recommended_analysis("CHART-DIST-001", "WASSERSTEIN_APPROX_HISTOGRAM", "alternative", "histogram approximation 기반 분포 거리", "CASE-004"),
        ],
        "CASE-005": [
            _recommended_analysis("CHART-PSI-001", "CATEGORICAL_PSI", "recommended", "categorical proportion shift의 운영 대표 지표", "CASE-004"),
            _recommended_analysis("CHART-CAT-002", "CATEGORICAL_TOTAL_VARIATION", "alternative", "전체 category 분포 이동량을 요약", "CASE-004"),
            _recommended_analysis("CHART-CAT-003", "CATEGORICAL_L_INFINITY", "alternative", "가장 크게 변한 category를 강조", "CASE-004"),
        ],
        "CASE-006": [
            _recommended_analysis("CHART-STREAM-001", "ADWIN_MEAN_STREAM", "recommended", "binary event rate step change를 60분 stream으로 확인", "CASE-006"),
            _recommended_analysis("CHART-PSI-001", "CATEGORICAL_PSI", "alternative", "binary event를 0/1 category proportion shift로 확인", "CASE-004"),
            _recommended_analysis("CHART-CAT-003", "BINNED_NUMERIC_L_INFINITY", "alternative", "event bin 중 가장 크게 움직인 구간을 강조", "CASE-004"),
            _recommended_analysis("CHART-EDF-001", "TWO_SAMPLE_KS_TWO_SIDED", "alternative", "reference/current event 값 분포 차이 확인", "CASE-004"),
        ],
        "CASE-007": [
            _recommended_analysis("CHART-PSI-001", "CATEGORICAL_PSI", "recommended", "probability vector에서 sampling된 class band proportion shift 확인", "CASE-007"),
            _recommended_analysis("CHART-CAT-002", "CATEGORICAL_TOTAL_VARIATION", "alternative", "class band 전체 분포 이동량을 요약", "CASE-007"),
            _recommended_analysis("CHART-CAT-003", "CATEGORICAL_L_INFINITY", "alternative", "가장 크게 움직인 class band를 강조", "CASE-007"),
        ],
        "CASE-008": [
            _recommended_analysis("CHART-MV-002", "LINEAR_TIME_MMD", "recommended", "multivariate embedding shift 대표 검정", "CASE-008"),
            _recommended_analysis("CHART-DIST-001", "SLICED_WASSERSTEIN_EMBEDDING", "alternative", "embedding projection 기반 거리 확인", "CASE-008"),
        ],
        "CASE-009": [
            _recommended_analysis("CHART-ANOM-001", "ISOLATION_FOREST_DRIFT_SCORE", "recommended", "local density/anomaly score 변화에 적합", "CASE-009"),
            _recommended_analysis("CHART-ANOM-001", "ONE_CLASS_SVM_DRIFT", "alternative", "one-class boundary 변화 확인", "CASE-009"),
        ],
        "CASE-010": [
            _recommended_analysis("CHART-STREAM-001", "ADWIN_MEAN_STREAM", "recommended", "numeric stream mean shift의 기본 실행 조합", "CASE-010"),
            _recommended_analysis("CHART-CTRL-001", "ONE_SIDED_UPPER_CUSUM", "alternative", "상방 평균 shift에 민감한 control chart", "CASE-010"),
            _recommended_analysis("CHART-CTRL-002", "EWMA_BASELINE_REPLAY_THRESHOLD", "alternative", "평활 기반 control chart로 변화 추세 확인", "CASE-010"),
        ],
        "CASE-011": [
            _recommended_analysis("CHART-ERR-001", "DDM_STANDARD", "recommended", "supervised error-rate stream drift 대표 조합", "CASE-011"),
            _recommended_analysis("CHART-ERR-003", "EDDM_GRADUAL_DRIFT", "alternative", "gradual error-distance drift 후보 확인", "CASE-011"),
            _recommended_analysis("CHART-ERR-005", "HDDM_A_HOEFFDING_BOUND", "alternative", "Hoeffding bound 기반 error-rate drift", "CASE-011"),
        ],
        "CASE-012": [
            _recommended_analysis("CHART-ERR-005", "HDDM_A_HOEFFDING_BOUND", "recommended", "long-horizon error-rate increase check", "CASE-012"),
            _recommended_analysis("CHART-ERR-003", "EDDM_GRADUAL_DRIFT", "alternative", "gradual concept drift error-distance check", "CASE-012"),
            _recommended_analysis("CHART-ERR-001", "DDM_STANDARD", "alternative", "label/model_prediction error-rate daily jump check", "CASE-012"),
        ],
        "CASE-013": [
            _recommended_analysis("CHART-TEXT-001", "TOPIC_DISTRIBUTION_SHIFT", "recommended", "text topic/semantic distribution shift에 적합", "CASE-018"),
            _recommended_analysis("CHART-TEXT-001", "QUERY_CENTROID_COSINE_SHIFT", "alternative", "query embedding centroid 이동 확인", "CASE-018"),
        ],
        "CASE-014": [
            _recommended_analysis("CHART-EXPL-001", "GLOBAL_IMPORTANCE_RANK_SHIFT", "recommended", "feature importance rank 변화 대표 차트", "CASE-017"),
            _recommended_analysis("CHART-EXPL-001", "SHAP_VALUE_DISTRIBUTION_TEST", "alternative", "SHAP value distribution 변화 확인", "CASE-017"),
        ],
        "CASE-015": [
            _recommended_analysis("CHART-UNC-001", "ENTROPY_DRIFT", "recommended", "annotation/label quality 변화의 uncertainty proxy", "CASE-015"),
            _recommended_analysis("CHART-UNC-001", "SOFTMAX_CONFIDENCE_DRIFT", "alternative", "confidence 분포 변화 확인", "CASE-015"),
        ],
        "CASE-016": [
            _recommended_analysis("CHART-REP-001", "MODEL_FEATURE_MAP_MMD", "recommended", "feature map representation shift 대표 검정", "CASE-014"),
            _recommended_analysis("CHART-REP-003", "GRAPH_EMBEDDING_MMD", "alternative", "graph/embedding representation 이동 확인", "CASE-017"),
        ],
    }
    if case_id.startswith("CASE-019-"):
        return [
            _with_calibration(
                case_id,
                _recommended_analysis(
                    "CHART-UNC-001",
                    "SOFTMAX_CONFIDENCE_DRIFT",
                    "recommended",
                    "객체 탐지 category-class 조합의 reference/current confidence 분포 변화 확인",
                    case_id,
                ),
            ),
            _with_calibration(
                case_id,
                _recommended_analysis(
                    "CHART-STREAM-001",
                    "ADWIN_MEAN_STREAM",
                    "alternative",
                    "시간 순서에 따른 평균 confidence 변화의 보조 감시",
                    case_id,
                ),
            ),
        ]
    if case_id == "CASE-002":
        return [
            _with_calibration(case_id, _recommended_analysis("CHART-DISTSHAPE-001", "TWO_SAMPLE_EPPS_SINGLETON", "recommended", "tail/shape gradual change representative test", "CASE-002")),
            _with_calibration(case_id, _recommended_analysis("CHART-EDF-002", "ONE_SAMPLE_ANDERSON_DARLING", "alternative", "tail expansion with Anderson-Darling", "CASE-002")),
            _with_calibration(case_id, _recommended_analysis("CHART-EDF-002", "TAIL_SENSITIVE_AD", "alternative", "tail-sensitive EDF difference", "CASE-002")),
            _with_calibration(case_id, _recommended_analysis("CHART-DIST-001", "WASSERSTEIN_APPROX_HISTOGRAM", "alternative", "distribution shape distance summary", "CASE-002")),
        ]
    recommendations = catalog.get(case_id, [])
    if recommendations:
        return [_with_calibration(case_id, recommendation) for recommendation in recommendations]
    if adapter_type == "test_db_prediction_log_stream":
        return [_with_calibration(case_id, _recommended_analysis("CHART-ERR-001", "DDM_STANDARD", "recommended", "prediction-log error-rate stream 기본 추천", "CASE-011"))]
    if adapter_type == "test_db_categorical_count_window":
        return [_with_calibration(case_id, _recommended_analysis("CHART-PSI-001", "CATEGORICAL_PSI", "recommended", "categorical count window 기본 추천", "CASE-004"))]
    return [_with_calibration(case_id, _recommended_analysis("CHART-STREAM-001", "ADWIN_MEAN_STREAM", "recommended", "numeric stream 기본 추천", "CASE-010"))]


def _with_calibration(case_id: str, recommendation: dict[str, Any]) -> dict[str, Any]:
    variant = str(recommendation.get("methodVariantKey") or "").upper()
    calibrated = _calibrated_recommendation(case_id, variant)
    if not calibrated:
        return recommendation
    next_recommendation = dict(recommendation)
    if calibrated.get("params"):
        next_recommendation["calibratedParams"] = calibrated["params"]
    if calibrated.get("windowConfig"):
        next_recommendation["calibratedWindowConfig"] = calibrated["windowConfig"]
    if case_id == "CASE-002":
        next_recommendation["replayProfileId"] = "long_horizon_120d"
    if case_id == "CASE-003":
        next_recommendation["replayProfileId"] = "case003_daily_45d"
    if case_id == "CASE-004":
        next_recommendation["replayProfileId"] = "demo_4h"
    if case_id == "CASE-005":
        next_recommendation["replayProfileId"] = "demo_4h"
    if case_id == "CASE-006":
        next_recommendation["replayProfileId"] = "boundary_4h" if variant == "CATEGORICAL_PSI" else "demo_4h"
    if case_id == "CASE-007":
        next_recommendation["replayProfileId"] = "demo_4h"
    if case_id == "CASE-008":
        next_recommendation["replayProfileId"] = "demo_4h"
    if case_id == "CASE-009":
        next_recommendation["replayProfileId"] = "demo_4h"
    if case_id == "CASE-012":
        next_recommendation["replayProfileId"] = "long_horizon_120d"
    if case_id == "CASE-013" and variant == "TOPIC_DISTRIBUTION_SHIFT":
        next_recommendation["replayProfileId"] = "boundary_4h"
    if case_id == "CASE-014" and variant in {"GLOBAL_IMPORTANCE_RANK_SHIFT", "SHAP_VALUE_DISTRIBUTION_TEST"}:
        next_recommendation["replayProfileId"] = "boundary_4h"
    if case_id == "CASE-015" and variant in {"ENTROPY_DRIFT", "SOFTMAX_CONFIDENCE_DRIFT"}:
        next_recommendation["replayProfileId"] = "boundary_4h"
    if case_id == "CASE-016" and variant in {"MODEL_FEATURE_MAP_MMD", "GRAPH_EMBEDDING_MMD"}:
        next_recommendation["replayProfileId"] = "boundary_4h"
    if case_id.startswith("CASE-019-") and variant == "SOFTMAX_CONFIDENCE_DRIFT":
        next_recommendation["replayProfileId"] = "object_detection_full_range"
    return next_recommendation


def _calibrated_recommendation(case_id: str, method_variant_key: str) -> dict[str, Any]:
    stream_window = {"bucketResolution": "10m", "lookbackBuckets": 144}
    one_window = {"bucketResolution": "240m", "lookbackBuckets": 1}
    distribution_base = {"value_col": "value", "min_reference_size": 20, "min_current_size": 20}
    distribution_window = {"bucketResolution": "240m", "lookbackBuckets": 1}
    probability_base = {"threshold": 0.1, "min_reference_size": 20, "min_current_size": 20}
    categorical_base = {"category_col": "category", "count_col": "count", "threshold": 0.01, "min_reference_size": 1, "min_current_size": 1}
    error_base = {"error_col": "error", "min_reference_size": 30, "min_current_size": 30, "errorRateShiftThreshold": 0.12, "maxStatePoints": 720}
    if case_id.startswith("CASE-019-"):
        if method_variant_key == "SOFTMAX_CONFIDENCE_DRIFT":
            return {
                "params": {
                    "variant_id": "SOFTMAX_CONFIDENCE_DRIFT",
                    "confidence_col": "confidence",
                    "alpha": 0.05,
                    "min_reference_size": 5,
                    "min_current_size": 5,
                },
                "windowConfig": {"bucketResolution": "10m", "lookbackBuckets": 1},
            }
        if method_variant_key == "ADWIN_MEAN_STREAM":
            return {
                "params": {
                    "variant_id": "ADWIN_MEAN_STREAM",
                    "delta": 0.002,
                    "meanShiftThreshold": 0.05,
                    "useAlgorithmImpl": False,
                },
                "windowConfig": stream_window,
            }
    catalog: dict[tuple[str, str], dict[str, Any]] = {
        ("CASE-001", "WASSERSTEIN_1D_EXACT"): {"params": {"variant_id": "WASSERSTEIN_1D_EXACT", **distribution_base, "threshold": 0.05}, "windowConfig": distribution_window},
        ("CASE-001", "TWO_SAMPLE_KS_TWO_SIDED"): {"params": {"variant_id": "TWO_SAMPLE_KS_TWO_SIDED", **distribution_base, "alpha": 0.05}, "windowConfig": distribution_window},
        ("CASE-001", "NUMERIC_BINNED_PSI"): {"params": {"variant_id": "NUMERIC_BINNED_PSI", **distribution_base, "bin_count": 5, "threshold": 0.1}, "windowConfig": distribution_window},
        ("CASE-002", "TWO_SAMPLE_EPPS_SINGLETON"): {"params": {"variant_id": "TWO_SAMPLE_EPPS_SINGLETON", **distribution_base, "alpha": 0.05}, "windowConfig": {"bucketResolution": "1440m", "lookbackBuckets": 1}},
        ("CASE-002", "ONE_SAMPLE_ANDERSON_DARLING"): {"params": {"variant_id": "ONE_SAMPLE_ANDERSON_DARLING", **distribution_base, "alpha": 0.05}, "windowConfig": {"bucketResolution": "1440m", "lookbackBuckets": 1}},
        ("CASE-002", "TAIL_SENSITIVE_AD"): {"params": {"variant_id": "TAIL_SENSITIVE_AD", **distribution_base, "alpha": 0.05}, "windowConfig": {"bucketResolution": "1440m", "lookbackBuckets": 1}},
        ("CASE-002", "TWO_SAMPLE_KS_TWO_SIDED"): {"params": {"variant_id": "TWO_SAMPLE_KS_TWO_SIDED", **distribution_base, "alpha": 0.05}, "windowConfig": distribution_window},
        ("CASE-002", "WASSERSTEIN_APPROX_HISTOGRAM"): {"params": {"variant_id": "WASSERSTEIN_APPROX_HISTOGRAM", **distribution_base, "threshold": 0.05, "bin_count": 20, "binning_policy": "equal_width"}, "windowConfig": {"bucketResolution": "1440m", "lookbackBuckets": 1}},
        ("CASE-003", "F_TEST_EQUAL_VARIANCE"): {"params": {"variant_id": "F_TEST_EQUAL_VARIANCE", **distribution_base, "alpha": 0.05}, "windowConfig": {"bucketResolution": "1440m", "lookbackBuckets": 1}},
        ("CASE-003", "BROWN_FORSYTHE_MEDIAN_CENTER"): {"params": {"variant_id": "BROWN_FORSYTHE_MEDIAN_CENTER", **distribution_base, "alpha": 0.05}, "windowConfig": {"bucketResolution": "1440m", "lookbackBuckets": 1}},
        ("CASE-004", "NUMERIC_BINNED_PSI"): {"params": {"variant_id": "NUMERIC_BINNED_PSI", **distribution_base, "bin_count": 5, "threshold": 1.0}, "windowConfig": {"bucketResolution": "60m", "lookbackBuckets": 1}},
        ("CASE-004", "BINNED_NUMERIC_L_INFINITY"): {"params": {"variant_id": "BINNED_NUMERIC_L_INFINITY", **categorical_base}, "windowConfig": distribution_window},
        ("CASE-004", "WASSERSTEIN_APPROX_HISTOGRAM"): {"params": {"variant_id": "WASSERSTEIN_APPROX_HISTOGRAM", **distribution_base, "threshold": 0.05, "bin_count": 20, "binning_policy": "equal_width"}, "windowConfig": distribution_window},
        ("CASE-005", "CATEGORICAL_PSI"): {"params": {"variant_id": "CATEGORICAL_PSI", **categorical_base, "threshold": 0.1}, "windowConfig": {"bucketResolution": "60m", "lookbackBuckets": 1}},
        ("CASE-005", "CATEGORICAL_TOTAL_VARIATION"): {"params": {"variant_id": "CATEGORICAL_TOTAL_VARIATION", **categorical_base, "threshold": 0.2}, "windowConfig": {"bucketResolution": "60m", "lookbackBuckets": 1}},
        ("CASE-005", "CATEGORICAL_L_INFINITY"): {"params": {"variant_id": "CATEGORICAL_L_INFINITY", **categorical_base, "threshold": 0.2}, "windowConfig": {"bucketResolution": "60m", "lookbackBuckets": 1}},
        ("CASE-006", "ADWIN_MEAN_STREAM"): {"params": {"variant_id": "ADWIN_MEAN_STREAM", "delta": 0.002, "meanShiftThreshold": 0.12, "useAlgorithmImpl": False}, "windowConfig": {"bucketResolution": "60m", "lookbackBuckets": 1}},
        ("CASE-006", "CATEGORICAL_PSI"): {"params": {"variant_id": "CATEGORICAL_PSI", **categorical_base}, "windowConfig": distribution_window},
        ("CASE-006", "NUMERIC_BINNED_PSI"): {"params": {"variant_id": "NUMERIC_BINNED_PSI", "value_col": "value", "bin_count": 2, "threshold": 0.05, "min_reference_size": 20, "min_current_size": 20}, "windowConfig": distribution_window},
        ("CASE-006", "BINNED_NUMERIC_L_INFINITY"): {"params": {"variant_id": "BINNED_NUMERIC_L_INFINITY", **categorical_base}, "windowConfig": distribution_window},
        ("CASE-006", "TWO_SAMPLE_KS_TWO_SIDED"): {"params": {"variant_id": "TWO_SAMPLE_KS_TWO_SIDED", **distribution_base, "alpha": 0.05}, "windowConfig": distribution_window},
        ("CASE-007", "CATEGORICAL_PSI"): {"params": {"variant_id": "CATEGORICAL_PSI", **categorical_base, "threshold": 0.1}, "windowConfig": {"bucketResolution": "60m", "lookbackBuckets": 1}},
        ("CASE-007", "CATEGORICAL_TOTAL_VARIATION"): {"params": {"variant_id": "CATEGORICAL_TOTAL_VARIATION", **categorical_base, "threshold": 0.2}, "windowConfig": {"bucketResolution": "60m", "lookbackBuckets": 1}},
        ("CASE-007", "CATEGORICAL_L_INFINITY"): {"params": {"variant_id": "CATEGORICAL_L_INFINITY", **categorical_base, "threshold": 0.2}, "windowConfig": {"bucketResolution": "60m", "lookbackBuckets": 1}},
        ("CASE-008", "LINEAR_TIME_MMD"): {"params": {"variant_id": "LINEAR_TIME_MMD", "feature_cols": ["centroid_x", "embedding_x", "embedding_y"], "threshold": 0.1, "min_reference_size": 20, "min_current_size": 20}, "windowConfig": {"bucketResolution": "60m", "lookbackBuckets": 1}},
        ("CASE-008", "SLICED_WASSERSTEIN_EMBEDDING"): {"params": {"variant_id": "SLICED_WASSERSTEIN_EMBEDDING", "feature_cols": ["centroid_x", "embedding_x", "embedding_y"], "threshold": 0.05, "min_reference_size": 20, "min_current_size": 20, "projection_count": 8}, "windowConfig": {"bucketResolution": "60m", "lookbackBuckets": 1}},
        ("CASE-009", "ISOLATION_FOREST_DRIFT_SCORE"): {"params": {"variant_id": "ISOLATION_FOREST_DRIFT_SCORE", "feature_cols": ["anomaly_score", "embedding_x", "embedding_y"], "anomaly_rate_threshold": 0.1, "min_reference_size": 20, "min_current_size": 20}, "windowConfig": {"bucketResolution": "240m", "lookbackBuckets": 1}},
        ("CASE-009", "ONE_CLASS_SVM_DRIFT"): {"params": {"variant_id": "ONE_CLASS_SVM_DRIFT", "feature_cols": ["anomaly_score", "embedding_x", "embedding_y"], "alpha": 0.05, "anomaly_rate_threshold": 0.1, "min_reference_size": 20, "min_current_size": 20}, "windowConfig": {"bucketResolution": "240m", "lookbackBuckets": 1}},
        ("CASE-010", "ADWIN_MEAN_STREAM"): {"params": {"variant_id": "ADWIN_MEAN_STREAM", "delta": 0.002, "meanShiftThreshold": 0.05, "useAlgorithmImpl": False}, "windowConfig": stream_window},
        ("CASE-010", "ONE_SIDED_UPPER_CUSUM"): {"params": {"variant_id": "ONE_SIDED_UPPER_CUSUM", "meanShiftThreshold": 0.05, "decision_threshold_h": 0.05, "useAlgorithmImpl": False}, "windowConfig": stream_window},
        ("CASE-010", "EWMA_BASELINE_REPLAY_THRESHOLD"): {"params": {"variant_id": "EWMA_BASELINE_REPLAY_THRESHOLD", "meanShiftThreshold": 0.05, "threshold": 0.05, "lambda": 0.3, "useAlgorithmImpl": False}, "windowConfig": stream_window},
        ("CASE-011", "DDM_STANDARD"): {"params": {"variant_id": "DDM_STANDARD", **error_base, "min_num_instances": 30}, "windowConfig": stream_window},
        ("CASE-011", "EDDM_GRADUAL_DRIFT"): {"params": {"variant_id": "EDDM_GRADUAL_DRIFT", **error_base, "min_num_errors": 20, "record_events": True}, "windowConfig": stream_window},
        ("CASE-011", "HDDM_A_HOEFFDING_BOUND"): {"params": {"variant_id": "HDDM_A_HOEFFDING_BOUND", **error_base, "min_instances": 30}, "windowConfig": stream_window},
        ("CASE-012", "DDM_STANDARD"): {"params": {"variant_id": "DDM_STANDARD", **error_base, "errorRateShiftThreshold": 0.02, "maxStatePoints": 720, "useAlgorithmImpl": False, "min_num_instances": 30, "drift_level": 2.0, "warning_level": 1.5}, "windowConfig": {"bucketResolution": "1440m", "lookbackBuckets": 120}},
        ("CASE-012", "EDDM_GRADUAL_DRIFT"): {"params": {"variant_id": "EDDM_GRADUAL_DRIFT", **error_base, "maxStatePoints": 172800, "useAlgorithmImpl": True, "min_num_errors": 20, "warning_level": 0.95, "drift_level": 0.9, "record_events": True}, "windowConfig": {"bucketResolution": "1440m", "lookbackBuckets": 120}},
        ("CASE-012", "HDDM_A_HOEFFDING_BOUND"): {"params": {"variant_id": "HDDM_A_HOEFFDING_BOUND", **error_base, "maxStatePoints": 172800, "useAlgorithmImpl": True, "min_instances": 30, "drift_confidence": 0.002, "warning_confidence": 0.01}, "windowConfig": {"bucketResolution": "1440m", "lookbackBuckets": 120}},
        ("CASE-013", "TOPIC_DISTRIBUTION_SHIFT"): {"params": {"variant_id": "TOPIC_DISTRIBUTION_SHIFT", "topic_col": "topic", "threshold": 0.1, "min_reference_size": 15, "min_current_size": 15}, "windowConfig": one_window},
        ("CASE-013", "QUERY_CENTROID_COSINE_SHIFT"): {"params": {"variant_id": "QUERY_CENTROID_COSINE_SHIFT", "embedding_cols": ["semantic_x", "technical_topic_weight"], "threshold": 0.1, "min_reference_size": 15, "min_current_size": 15}, "windowConfig": one_window},
        ("CASE-014", "GLOBAL_IMPORTANCE_RANK_SHIFT"): {"params": {"variant_id": "GLOBAL_IMPORTANCE_RANK_SHIFT", "shap_cols": ["importance_a", "importance_b", "importance_c"], "rank_shift_threshold": 0.4, "min_reference_size": 20, "min_current_size": 20}, "windowConfig": one_window},
        ("CASE-014", "SHAP_VALUE_DISTRIBUTION_TEST"): {"params": {"variant_id": "SHAP_VALUE_DISTRIBUTION_TEST", "shap_cols": ["importance_a", "importance_b", "importance_c"], "alpha": 0.05, "min_reference_size": 20, "min_current_size": 20}, "windowConfig": one_window},
        ("CASE-015", "ENTROPY_DRIFT"): {"params": {"variant_id": "ENTROPY_DRIFT", "probability_cols": ["annotation_confidence", "label_noise_probability"], "alpha": 0.05, "min_reference_size": 20, "min_current_size": 20}, "windowConfig": one_window},
        ("CASE-015", "SOFTMAX_CONFIDENCE_DRIFT"): {"params": {"variant_id": "SOFTMAX_CONFIDENCE_DRIFT", "confidence_col": "annotation_confidence", "alpha": 0.05, "min_reference_size": 20, "min_current_size": 20}, "windowConfig": one_window},
        ("CASE-016", "MODEL_FEATURE_MAP_MMD"): {"params": {"variant_id": "MODEL_FEATURE_MAP_MMD", "feature_cols": ["activation", "representation_shift"], "alpha": 0.1, "permutation_count": 19, "random_state": 5, "min_reference_size": 20, "min_current_size": 20}, "windowConfig": one_window},
        ("CASE-016", "GRAPH_EMBEDDING_MMD"): {"params": {"variant_id": "GRAPH_EMBEDDING_MMD", "embedding_cols": ["activation", "representation_shift"], "alpha": 0.1, "permutation_count": 19, "random_state": 11, "min_reference_size": 15, "min_current_size": 15}, "windowConfig": one_window},
    }
    return catalog.get((case_id, method_variant_key), {})


def _recommended_analysis(
    chart_id: str,
    method_variant_key: str,
    rank: str,
    reason: str,
    representative_case_id: str,
    *,
    calibrated_params: dict[str, Any] | None = None,
    calibrated_window_config: dict[str, Any] | None = None,
) -> dict[str, Any]:
    recommendation: dict[str, Any] = {
        "chartId": chart_id,
        "methodVariantKey": method_variant_key,
        "runtimeMethodKey": _runtime_alias_for_variant(method_variant_key),
        "rank": rank,
        "reason": reason,
        "representativeCaseId": representative_case_id,
    }
    if calibrated_params:
        recommendation["calibratedParams"] = calibrated_params
    if calibrated_window_config:
        recommendation["calibratedWindowConfig"] = calibrated_window_config
    return recommendation


def _runtime_alias_for_variant(method_variant_key: str) -> str:
    return _runtime_aliases().get(str(method_variant_key or "").upper(), "")


def _parse_metadata_time(value: Any) -> datetime:
    if not value:
        return datetime(2026, 1, 1, tzinfo=timezone.utc)
    parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00").replace(" ", "T"))
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _format_iso(value: datetime) -> str:
    return value.replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _adapter_type_for_columns(columns: list[str]) -> str:
    column_set = set(columns)
    if {"confidence", "period"}.issubset(column_set):
        return "test_db_multivariate_window"
    if {"y_true", "y_pred", "error"}.issubset(column_set):
        return "test_db_prediction_log_stream"
    if {"label", "model_prediction"}.issubset(column_set):
        return "test_db_prediction_log_stream"
    if {"topic", "semantic_x"}.issubset(column_set):
        return "test_db_multivariate_window"
    if {"category", "label"}.intersection(column_set):
        return "test_db_categorical_count_window"
    if {"category_weight_c", "concept_score"}.intersection(column_set):
        return "test_db_numeric_stream"
    if {"importance_a", "importance_b", "importance_c"}.intersection(column_set):
        return "test_db_multivariate_window"
    if {"annotation_confidence", "label_noise_probability"}.intersection(column_set):
        return "test_db_multivariate_window"
    if {"activation", "representation_shift"}.intersection(column_set):
        return "test_db_multivariate_window"
    if {"p0", "p1", "p2", "p3", "p4"}.intersection(column_set):
        return "test_db_numeric_distribution_window"
    if "event" in column_set:
        return "test_db_numeric_distribution_window"
    if any(column.startswith(("emb", "x")) for column in columns) and len([c for c in columns if c.startswith(("emb", "x"))]) >= 2:
        return "test_db_multivariate_window"
    if {"score", "value", "x"}.intersection(column_set):
        return "test_db_numeric_distribution_window"
    return "test_db_numeric_stream"


def _feature_id_for_adapter(adapter_type: str, value_column: str = "metric") -> str:
    if adapter_type == "test_db_prediction_log_stream":
        return "error_rate"
    if adapter_type == "test_db_numeric_distribution_window":
        return "score"
    if adapter_type == "test_db_multivariate_window":
        return "multivariate"
    if adapter_type == "test_db_categorical_count_window":
        return "category"
    return "metric"


def _aggregate_interval_minutes_for_case(case_id: str, adapter_type: str) -> int:
    return 10


def _replay_profiles_for_case(
    case_id: str,
    adapter_type: str,
    drift_start: datetime,
    data_start: datetime | None = None,
    data_end: datetime | None = None,
) -> list[dict[str, Any]]:
    if case_id.startswith("CASE-019-"):
        window_start = data_start or drift_start - timedelta(days=20)
        window_end = data_end or drift_start + timedelta(days=20)
        # The collector floors an initial cursor to the containing hour. Include
        # that leading partial hour so one poll closes a bucket containing every row.
        window_start = window_start.replace(minute=0, second=0, microsecond=0)
        window_minutes = max(1, int(((window_end - window_start).total_seconds() + 59) // 60))
        window_minutes = ((window_minutes + 9) // 10) * 10
        window_end = window_start + timedelta(minutes=window_minutes)
        return [
            _replay_profile(
                "object_detection_full_range",
                "객체 탐지 confidence 전체 데이터 기간: 10분 bucket",
                window_start,
                window_end,
                100000,
                10,
                window_minutes,
                1,
            ),
            _replay_profile(
                "validation_2d",
                "confidence 경계 전후 2일 보조 검증",
                drift_start - timedelta(days=1),
                drift_start + timedelta(days=1),
                100000,
                240,
                10,
                288,
            ),
        ]
    if case_id == "CASE-012":
        return [
            _replay_profile(
                "demo_4h",
                "빠른 시계열: drift 전후 4시간, 10분 bucket",
                drift_start - timedelta(hours=2),
                drift_start + timedelta(hours=2),
                240,
                10,
                10,
                25,
            ),
            _replay_profile(
                "validation_2d",
                "넓은 검증: drift 전후 2일, 10분 bucket",
                drift_start - timedelta(days=1),
                drift_start + timedelta(days=1),
                2880,
                10,
                10,
                288,
            ),
            _replay_profile(
                "long_horizon_120d",
                "장기 검증: gradual boundary 전 30일/후 90일, 1일 bucket",
                drift_start - timedelta(days=30),
                drift_start + timedelta(days=90),
                172800,
                1440,
                1440,
                120,
            ),
        ]
    if case_id == "CASE-009":
        return [
            _replay_profile(
                "demo_4h",
                "OCDD 빠른 검증: drift 경계 4시간 window",
                drift_start - timedelta(hours=2),
                drift_start + timedelta(hours=2),
                240,
                240,
                240,
                1,
            ),
            _replay_profile(
                "validation_2d",
                "넓은 검증: drift 전후 2일, 4시간 bucket",
                drift_start - timedelta(days=1),
                drift_start + timedelta(days=1),
                2880,
                240,
                10,
                288,
            ),
        ]
    if case_id == "CASE-002":
        return [
            _replay_profile(
                "long_horizon_120d",
                "CASE-002 gradual tail/shape validation, 120 days with 1 day buckets",
                drift_start - timedelta(days=30),
                drift_start + timedelta(days=90),
                172800,
                1440,
                1440,
                120,
            ),
            _replay_profile(
                "demo_4h",
                "Quick smoke check around drift boundary, weak signal expected",
                drift_start - timedelta(hours=2),
                drift_start + timedelta(hours=2),
                240,
                10,
                10,
                25,
            ),
            _replay_profile(
                "validation_2d",
                "Short validation around drift boundary, weak signal expected",
                drift_start - timedelta(days=1),
                drift_start + timedelta(days=1),
                2880,
                240,
                10,
                288,
            ),
        ]
    if case_id == "CASE-003":
        return [
            _replay_profile(
                "case003_daily_45d",
                "CASE-003 variance validation, 45 days with 1 day buckets",
                drift_start - timedelta(days=15),
                drift_start + timedelta(days=30),
                64800,
                1440,
                1440,
                45,
            ),
            _replay_profile(
                "demo_4h",
                "Quick smoke check around drift boundary, weak signal expected",
                drift_start - timedelta(hours=2),
                drift_start + timedelta(hours=2),
                240,
                10,
                10,
                25,
            ),
            _replay_profile(
                "validation_2d",
                "Short validation around drift boundary, weak signal expected",
                drift_start - timedelta(days=1),
                drift_start + timedelta(days=1),
                2880,
                240,
                10,
                288,
            ),
        ]
    if case_id == "CASE-013":
        return [
            _replay_profile(
                "boundary_4h",
                "CASE-013 topic shift validation, drift boundary 4 hours with one 4 hour bucket",
                drift_start - timedelta(hours=2),
                drift_start + timedelta(hours=2),
                240,
                240,
                240,
                1,
            ),
            _replay_profile(
                "demo_4h",
                "Quick smoke check around drift boundary, 10 minute buckets",
                drift_start - timedelta(hours=2),
                drift_start + timedelta(hours=2),
                240,
                10,
                10,
                25,
            ),
            _replay_profile(
                "validation_2d",
                "Wider semantic validation around drift boundary, 4 hour buckets",
                drift_start - timedelta(days=1),
                drift_start + timedelta(days=1),
                2880,
                240,
                10,
                288,
            ),
        ]
    if case_id == "CASE-014":
        return [
            _replay_profile(
                "boundary_4h",
                "CASE-014 explanation importance validation, drift boundary 4 hours with one 4 hour bucket",
                drift_start - timedelta(hours=2),
                drift_start + timedelta(hours=2),
                240,
                240,
                240,
                1,
            ),
            _replay_profile(
                "demo_4h",
                "Quick smoke check around drift boundary, 10 minute buckets",
                drift_start - timedelta(hours=2),
                drift_start + timedelta(hours=2),
                240,
                10,
                10,
                25,
            ),
            _replay_profile(
                "validation_2d",
                "Wider explanation validation around drift boundary, 4 hour buckets",
                drift_start - timedelta(days=1),
                drift_start + timedelta(days=1),
                2880,
                240,
                10,
                288,
            ),
        ]
    if case_id == "CASE-015":
        return [
            _replay_profile(
                "boundary_4h",
                "CASE-015 uncertainty validation, drift boundary 4 hours with one 4 hour bucket",
                drift_start - timedelta(hours=2),
                drift_start + timedelta(hours=2),
                240,
                240,
                240,
                1,
            ),
            _replay_profile(
                "demo_4h",
                "Quick smoke check around drift boundary, 10 minute buckets",
                drift_start - timedelta(hours=2),
                drift_start + timedelta(hours=2),
                240,
                10,
                10,
                25,
            ),
            _replay_profile(
                "validation_2d",
                "Wider uncertainty validation around drift boundary, 4 hour buckets",
                drift_start - timedelta(days=1),
                drift_start + timedelta(days=1),
                2880,
                240,
                10,
                288,
            ),
        ]
    if case_id == "CASE-016":
        return [
            _replay_profile(
                "boundary_4h",
                "CASE-016 representation validation, drift boundary 4 hours with one 4 hour bucket",
                drift_start - timedelta(hours=2),
                drift_start + timedelta(hours=2),
                240,
                240,
                240,
                1,
            ),
            _replay_profile(
                "demo_4h",
                "Quick smoke check around drift boundary, 10 minute buckets",
                drift_start - timedelta(hours=2),
                drift_start + timedelta(hours=2),
                240,
                10,
                10,
                25,
            ),
            _replay_profile(
                "validation_2d",
                "Wider representation validation around drift boundary, 4 hour buckets",
                drift_start - timedelta(days=1),
                drift_start + timedelta(days=1),
                2880,
                240,
                10,
                288,
            ),
        ]
    if case_id == "CASE-004":
        return [
            _replay_profile(
                "demo_4h",
                "빠른 검증: drift 전후 4시간, 1시간 bucket",
                drift_start - timedelta(hours=2),
                drift_start + timedelta(hours=2),
                240,
                60,
                60,
                4,
            ),
            _replay_profile(
                "validation_2d",
                "넓은 검증: drift 전후 2일, 4시간 bucket",
                drift_start - timedelta(days=1),
                drift_start + timedelta(days=1),
                2880,
                240,
                10,
                288,
            ),
        ]
    if case_id == "CASE-005":
        return [
            _replay_profile(
                "demo_4h",
                "빠른 시계열: categorical drift 전후 4시간, 1시간 bucket",
                drift_start - timedelta(hours=2),
                drift_start + timedelta(hours=2),
                240,
                60,
                60,
                4,
            ),
            _replay_profile(
                "validation_2d",
                "넓은 검증: categorical drift 전후 2일, 1시간 bucket",
                drift_start - timedelta(days=1),
                drift_start + timedelta(days=1),
                2880,
                60,
                60,
                48,
            ),
        ]
    if case_id == "CASE-006":
        return [
            _replay_profile(
                "demo_4h",
                "빠른 시계열: binary event drift 전후 4시간, 1시간 bucket",
                drift_start - timedelta(hours=2),
                drift_start + timedelta(hours=2),
                240,
                60,
                60,
                4,
            ),
            _replay_profile(
                "boundary_4h",
                "비율 검증: binary event drift 경계 포함 4시간, 4시간 bucket",
                drift_start - timedelta(hours=2),
                drift_start + timedelta(hours=2),
                240,
                240,
                240,
                1,
            ),
            _replay_profile(
                "validation_2d",
                "넓은 검증: binary event drift 전후 2일, 1시간 bucket",
                drift_start - timedelta(days=1),
                drift_start + timedelta(days=1),
                2880,
                60,
                60,
                48,
            ),
        ]
    if case_id == "CASE-007":
        return [
            _replay_profile(
                "demo_4h",
                "빠른 시계열: probability vector class band drift 전후 4시간, 1시간 bucket",
                drift_start - timedelta(hours=2),
                drift_start + timedelta(hours=2),
                240,
                60,
                60,
                4,
            ),
            _replay_profile(
                "validation_2d",
                "넓은 검증: probability vector class band drift 전후 2일, 1시간 bucket",
                drift_start - timedelta(days=1),
                drift_start + timedelta(days=1),
                2880,
                60,
                60,
                48,
            ),
        ]
    if case_id == "CASE-008":
        return [
            _replay_profile(
                "demo_4h",
                "빠른 검증: multivariate embedding drift 전후 4시간, 1시간 bucket",
                drift_start - timedelta(hours=2),
                drift_start + timedelta(hours=2),
                240,
                60,
                60,
                4,
            ),
            _replay_profile(
                "validation_2d",
                "넓은 검증: multivariate embedding drift 전후 2일, 1시간 bucket",
                drift_start - timedelta(days=1),
                drift_start + timedelta(days=1),
                2880,
                60,
                60,
                48,
            ),
        ]
    if adapter_type in {
        "test_db_numeric_distribution_window",
        "test_db_multivariate_window",
        "test_db_categorical_count_window",
    }:
        return [
            _replay_profile(
                "demo_4h",
                "빠른 시계열: drift 전후 4시간, 10분 bucket",
                drift_start - timedelta(hours=2),
                drift_start + timedelta(hours=2),
                240,
                10,
                10,
                25,
            ),
            _replay_profile(
                "validation_2d",
                "넓은 검증: drift 전후 2일, 4시간 bucket",
                drift_start - timedelta(days=1),
                drift_start + timedelta(days=1),
                2880,
                240,
                10,
                288,
            ),
        ]
    return [
        _replay_profile(
            "demo_4h",
            "빠른 시계열: drift 전후 4시간, 10분 bucket",
            drift_start - timedelta(hours=2),
            drift_start + timedelta(hours=2),
            240,
            10,
            10,
            25,
        ),
        _replay_profile(
            "validation_2d",
            "넓은 검증: drift 전후 2일, 10분 bucket",
            drift_start - timedelta(days=1),
            drift_start + timedelta(days=1),
            2880,
            10,
            10,
            288,
        ),
    ]


def _replay_profile(
    profile_id: str,
    label: str,
    start: datetime,
    end: datetime,
    max_rows: int,
    aggregate_interval_minutes: int,
    logical_minutes_per_tick: int,
    tick_count: int,
) -> dict[str, Any]:
    return {
        "profileId": profile_id,
        "label": label,
        "startTime": _format_iso(start),
        "endTime": _format_iso(end),
        "maxRows": max_rows,
        "aggregateIntervalMinutes": aggregate_interval_minutes,
        "logicalMinutesPerTick": logical_minutes_per_tick,
        "tickCount": tick_count,
        "pollEveryTicks": 1,
    }


def _value_column_for_columns(columns: list[str]) -> str:
    for column in (
        "metric",
        "error",
        "event",
        "p3",
        "score",
        "value",
        "x",
        "category_weight_c",
        "centroid_x",
        "anomaly_score",
        "concept_score",
        "technical_topic_weight",
        "importance_b",
        "label_noise_probability",
        "activation",
        "semantic_x",
        "annotation_confidence",
        "representation_shift",
        "confidence",
    ):
        if column in columns:
            return column
    return "metric"


def _feature_columns_for_columns(columns: list[str]) -> list[str]:
    preferred = [
        column
        for column in (
            "semantic_x",
            "technical_topic_weight",
            "centroid_x",
            "anomaly_score",
            "importance_a",
            "importance_b",
            "importance_c",
            "annotation_confidence",
            "label_noise_probability",
            "activation",
            "representation_shift",
            "confidence",
        )
        if column in columns
    ]
    selected = preferred + [column for column in columns if column.startswith(("emb", "x")) and column not in preferred]
    return selected[:8] or ["metric"]


@app.get("/api/admin/report/gallery-data")
def report_gallery_data() -> dict[str, Any]:
    if REPORT_GALLERY_BASE_URL:
        try:
            with urlopen(f"{REPORT_GALLERY_BASE_URL}/api/gallery-data", timeout=2) as response:
                payload = json.loads(response.read().decode("utf-8"))
            if payload.get("ok") and isinstance(payload.get("data"), dict):
                data = payload["data"]
                data.setdefault("source", {"type": "drift_report_gallery_server", "baseUrl": REPORT_GALLERY_BASE_URL})
                data["runtimeAliases"] = _runtime_aliases()
                return ok(data)
        except Exception:
            pass
    return ok(_fallback_report_gallery_data())


def _runtime_aliases() -> dict[str, str]:
    control_plane_root = str(CONTROL_PLANE_ROOT)
    if control_plane_root not in sys.path:
        sys.path.insert(0, control_plane_root)
    try:
        from testing.harness.chart_method_compatibility import RUNTIME_ALIAS_BY_VARIANT
    except Exception:
        return {}
    return dict(RUNTIME_ALIAS_BY_VARIANT)


def _fallback_report_gallery_data() -> dict[str, Any]:
    method_data_path = REPORT_CHARTS_ROOT / "method_data.js"
    text = method_data_path.read_text(encoding="utf-8")
    match = re.search(r"window\.CHART_METHODS\s*=\s*(\{.*\});?\s*$", text, re.S)
    chart_methods = json.loads(match.group(1)) if match else {}
    charts: list[dict[str, str]] = []
    for chart_id in sorted(chart_methods):
        html_path = f"{chart_id.lower().replace('-', '_')}.html"
        title = _chart_html_title(REPORT_CHARTS_ROOT / html_path) or chart_id
        family = chart_id.split("-")[1] if "-" in chart_id else "기타"
        charts.append(
            {
                "chartId": chart_id,
                "title": title,
                "family": f"{family} 계열",
                "htmlPath": html_path,
                "descriptionHtml": "",
            }
        )
    return {
        "charts": charts,
        "chartMethods": chart_methods,
        "methodDescriptions": {},
        "runtimeAliases": _runtime_aliases(),
        "source": {"type": "method_data_js_fallback", "path": str(method_data_path)},
    }


def _chart_html_title(path: Path) -> str | None:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return None
    match = re.search(r"<title>(.*?)</title>", text, re.S | re.I)
    if not match:
        return None
    return re.sub(r"\s+", " ", match.group(1)).strip()


def _log_admin_event(event: str, **fields: Any) -> None:
    payload = {"event": event, **fields}
    admin_debug_logger.info(json.dumps(payload, ensure_ascii=False, default=str, sort_keys=True))


def _timeseries_summary(response: dict[str, Any]) -> dict[str, Any]:
    data = response.get("data") if isinstance(response, dict) else None
    if not isinstance(data, dict):
        return {"ok": bool(response.get("ok")) if isinstance(response, dict) else False, "hasData": False}
    series = data.get("series") if isinstance(data.get("series"), dict) else {}
    events = data.get("events") if isinstance(data.get("events"), dict) else {}
    event_rows: list[dict[str, Any]] = []
    for feature_id, rows in events.items():
        if isinstance(rows, list):
            for row in rows:
                if isinstance(row, dict):
                    event_rows.append({"featureId": feature_id, **row})
    first_event = event_rows[0] if event_rows else {}
    return {
        "ok": bool(response.get("ok")) if isinstance(response, dict) else False,
        "hasData": True,
        "sourceId": data.get("sourceId"),
        "featuresCount": len(data.get("features") or []),
        "seriesPointCount": sum(len(rows) for rows in series.values() if isinstance(rows, list)),
        "eventCount": len(event_rows),
        "eventFeatureKeys": sorted(str(key) for key in events.keys()),
        "firstEventId": first_event.get("eventId"),
        "firstEventLevel": first_event.get("level"),
        "firstEventAnalysisChartCount": len(first_event.get("analysisCharts") or []),
        "pollIntervalMs": data.get("pollIntervalMs"),
    }


@app.post("/api/admin/test/feeders")
def register_test_feeder(body: dict[str, Any]) -> dict[str, Any]:
    return test_feeder.post("/api/test-feeder/feeders", body)


@app.post("/api/admin/test/feeders/{source_id}/tick")
def tick_test_feeder(source_id: str, body: dict[str, Any]) -> dict[str, Any]:
    return test_feeder.post(f"/api/test-feeder/feeders/{source_id}/tick", body)


@app.get("/api/admin/test/raw-events/{source_id}")
def test_raw_events(source_id: str) -> dict[str, Any]:
    return test_feeder.get(f"/api/test-feeder/debug/raw-events?sourceId={source_id}")


@app.post("/api/admin/drift/adapters/{adapter_id}/poll-once")
def poll_drift_adapter(adapter_id: str, body: dict[str, Any]) -> dict[str, Any]:
    path = f"/api/drift/adapters/{adapter_id}/poll-once"
    _log_admin_event("drift.poll_once.request", adapterId=adapter_id, path=path, body=body)
    try:
        response = drift.post(path, body)
    except Exception as exc:
        _log_admin_event("drift.poll_once.error", adapterId=adapter_id, path=path, error=repr(exc))
        raise
    data = response.get("data") if isinstance(response, dict) else None
    _log_admin_event(
        "drift.poll_once.response",
        adapterId=adapter_id,
        path=path,
        ok=bool(response.get("ok")) if isinstance(response, dict) else False,
        data=data,
    )
    return response


@app.get("/api/admin/drift/timeseries/{source_id}")
def drift_timeseries(source_id: str) -> dict[str, Any]:
    path = f"/api/sources/{source_id}/timeseries-data?resolution=10m"
    _log_admin_event("drift.timeseries.request", sourceId=source_id, path=path)
    try:
        response = drift.get(path)
    except Exception as exc:
        _log_admin_event("drift.timeseries.error", sourceId=source_id, path=path, error=repr(exc))
        raise
    _log_admin_event("drift.timeseries.response", sourceId=source_id, path=path, summary=_timeseries_summary(response))
    return response


@app.get("/api/sources/{source_id}/timeseries-data")
def proxied_timeseries_data(source_id: str, resolution: str = "10m") -> dict[str, Any]:
    path = f"/api/sources/{source_id}/timeseries-data?resolution={resolution}"
    _log_admin_event("drift.timeseries_proxy.request", sourceId=source_id, path=path)
    try:
        response = drift.get(path)
    except Exception as exc:
        _log_admin_event("drift.timeseries_proxy.error", sourceId=source_id, path=path, error=repr(exc))
        raise
    _log_admin_event(
        "drift.timeseries_proxy.response",
        sourceId=source_id,
        path=path,
        summary=_timeseries_summary(response),
    )
    return response


@app.get("/api/admin/drift/events/{source_id}/{event_id}/analysis")
def drift_event_analysis(source_id: str, event_id: str) -> dict[str, Any]:
    return drift.get(f"/api/sources/{source_id}/events/{event_id}/analysis")


@app.get("/api/sources/{source_id}/events/{event_id}/analysis")
def proxied_event_analysis(source_id: str, event_id: str) -> dict[str, Any]:
    return drift.get(f"/api/sources/{source_id}/events/{event_id}/analysis")


@app.get("/api/admin/drift/debug/buckets")
def drift_debug_buckets(sourceId: str, adapterId: str | None = None) -> dict[str, Any]:
    path = f"/api/drift/debug/buckets?sourceId={sourceId}"
    if adapterId:
        path += f"&adapterId={adapterId}"
    return drift.get(path)


@app.get("/api/admin/drift/debug/method-runs")
def drift_debug_method_runs(sourceId: str, assignmentId: str | None = None) -> dict[str, Any]:
    path = f"/api/drift/debug/method-runs?sourceId={sourceId}"
    if assignmentId:
        path += f"&assignmentId={assignmentId}"
    return drift.get(path)


@app.get("/api/admin/drift/debug/drift-events")
def drift_debug_events(sourceId: str, assignmentId: str | None = None) -> dict[str, Any]:
    path = f"/api/drift/debug/drift-events?sourceId={sourceId}"
    if assignmentId:
        path += f"&assignmentId={assignmentId}"
    return drift.get(path)


@app.get("/api/admin/drift/debug/method-state/{assignment_id}")
def drift_debug_method_state(assignment_id: str) -> dict[str, Any]:
    return drift.get(f"/api/drift/debug/method-state/{assignment_id}")


@app.post("/api/admin/llm/interpret/chart/jobs")
def create_llm_chart_job(body: dict[str, Any]) -> dict[str, Any]:
    return llm.post("/api/interpret/chart/jobs", body)


@app.get("/api/admin/llm/interpret/chart/jobs/{job_id}")
def get_llm_chart_job(job_id: str) -> dict[str, Any]:
    return llm.get(f"/api/interpret/chart/jobs/{job_id}")


if __name__ == "__main__":
    uvicorn.run(app, host=ADMIN_SERVER_HOST, port=ADMIN_SERVER_PORT)
