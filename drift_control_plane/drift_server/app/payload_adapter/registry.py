from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

from .engine import BindingPayloadAdapter, PayloadBindingError


BINDINGS_DIR = Path(__file__).resolve().parent / "bindings"
REPO_ROOT = Path(__file__).resolve().parents[4]
RUNTIME_PAYLOADS_PATH = REPO_ROOT / "chart_runtime" / "payloads" / "runtime_chart_payloads.json"
DEFAULT_BINDING_KEY = "adwin_mean_stream_to_chart_stream_001"
_BINDING_FILES = {
    DEFAULT_BINDING_KEY: "adwin_mean_stream__CHART-STREAM-001.json",
}
_RUNTIME_TEMPLATE_BINDINGS = {
    DEFAULT_BINDING_KEY: {
        "methodVariantKey": "ADWIN_MEAN_STREAM",
        "runtimeMethodKey": "adwin_mean_stream",
        "chartId": "CHART-STREAM-001",
    }
}
_AUTO_PREFIX = "auto__"


# @managed-contract contract_id=payload_adapter.registry.get_binding_spec level=P0
@lru_cache(maxsize=32)
def get_binding_spec(binding_key: str) -> dict[str, Any]:
    if binding_key in _RUNTIME_TEMPLATE_BINDINGS:
        return _build_runtime_template_binding_spec(binding_key)
    if binding_key in _BINDING_FILES:
        with (BINDINGS_DIR / _BINDING_FILES[binding_key]).open(encoding="utf-8") as file:
            return json.load(file)
    if binding_key.startswith(_AUTO_PREFIX):
        return _build_auto_binding_spec(binding_key)
    raise PayloadBindingError(f"payload binding is not registered: {binding_key}")


# @managed-contract contract_id=payload_adapter.registry.build_payload level=P0
def build_payload(context: dict[str, Any], binding_key: str = DEFAULT_BINDING_KEY) -> dict[str, Any]:
    spec = get_binding_spec(binding_key)
    return BindingPayloadAdapter(spec).build(context)


# @managed-contract contract_id=payload_adapter.registry.get_registered_binding_index level=P0
def get_registered_binding_index() -> dict[tuple[str, str], str]:
    index: dict[tuple[str, str], str] = {}
    for binding_key in _BINDING_FILES:
        spec = get_binding_spec(binding_key)
        index[(spec["methodVariantKey"], spec["chartId"])] = binding_key
    for chart_id, methods in _load_chart_methods().items():
        for method in methods:
            method_variant_key = _method_variant_key(str(method.get("method", "")))
            index.setdefault((method_variant_key, chart_id), _auto_binding_key(method_variant_key, chart_id))
    return index


def _build_auto_binding_spec(binding_key: str) -> dict[str, Any]:
    method_variant_key, chart_id = _parse_auto_binding_key(binding_key)
    template = _runtime_template(chart_id)
    template["data"] = {}
    _adjust_auto_template(method_variant_key, chart_id, template)
    data_sources = _component_data_specs(template)
    return {
        "bindingId": f"auto__{method_variant_key}__{chart_id}",
        "payloadAdapterKey": binding_key,
        "methodVariantKey": method_variant_key,
        "runtimeMethodKey": method_variant_key.lower(),
        "chartId": chart_id,
        "templateDataPolicy": "replace_data_only",
        "methodEventContract": {
            "requiredContextPaths": [
                "$.source.sourceId",
                "$.feature.featureId",
                "$.assignment.runtimeMethodKey",
                "$.methodRun.methodRunId",
                "$.driftEvent.eventId",
                "$.driftEvent.eventStart",
                "$.driftEvent.eventEnd",
                "$.driftEvent.level",
                "$.driftEvent.score",
            ]
        },
        "payloadTemplate": template,
        "dataBindings": [
            {
                "targetDataSource": spec["source"],
                "input": "derivedRows",
                "transform": spec["transform"],
                "fields": spec["fields"],
            }
            for spec in data_sources
        ],
        "dataContracts": [
            {
                "source": spec["source"],
                "requiredFields": spec["fields"] or _default_required_fields(spec["transform"]),
                "transform": spec["transform"],
            }
            for spec in data_sources
        ],
    }


def _build_runtime_template_binding_spec(binding_key: str) -> dict[str, Any]:
    binding = _RUNTIME_TEMPLATE_BINDINGS[binding_key]
    chart_id = binding["chartId"]
    template = _runtime_template(chart_id)
    template["data"] = {}
    data_bindings = [
        {
            "targetDataSource": f"chart.{chart_id}.summary",
            "input": "derivedRows",
            "transform": "adwin_stream_runtime_summary",
            "fields": ["label", "displayValue"],
        },
        {
            "targetDataSource": f"chart.{chart_id}.stream",
            "input": "derivedRows",
            "transform": "adwin_stream_runtime_series",
            "fields": ["time", "value", "rolling_mean"],
        },
        {
            "targetDataSource": f"chart.{chart_id}.window",
            "input": "derivedRows",
            "transform": "adwin_stream_runtime_window",
            "fields": ["time", "value"],
        },
        {
            "targetDataSource": f"chart.{chart_id}.mean",
            "input": "derivedRows",
            "transform": "adwin_stream_runtime_mean",
            "fields": ["label", "value", "class"],
        },
        {
            "targetDataSource": f"chart.{chart_id}.notes",
            "input": "derivedRows",
            "transform": "adwin_stream_runtime_notes",
            "fields": ["title", "text", "legend"],
        },
    ]
    return {
        "bindingId": f"{binding['runtimeMethodKey']}__{chart_id}",
        "payloadAdapterKey": binding_key,
        "methodVariantKey": binding["methodVariantKey"],
        "runtimeMethodKey": binding["runtimeMethodKey"],
        "chartId": chart_id,
        "templateDataPolicy": "replace_data_only",
        "methodEventContract": {
            "requiredContextPaths": [
                "$.source.sourceId",
                "$.feature.featureId",
                "$.assignment.runtimeMethodKey",
                "$.methodRun.methodRunId",
                "$.driftEvent.eventId",
                "$.driftEvent.eventStart",
                "$.driftEvent.eventEnd",
                "$.driftEvent.level",
                "$.driftEvent.score",
            ]
        },
        "payloadTemplate": template,
        "dataBindings": data_bindings,
        "dataContracts": [
            {
                "source": binding["targetDataSource"],
                "requiredFields": binding["fields"],
                "transform": binding["transform"],
            }
            for binding in data_bindings
        ],
    }


def _runtime_template(chart_id: str) -> dict[str, Any]:
    for payload in _load_runtime_payloads():
        if payload.get("chartId") == chart_id:
            return json.loads(json.dumps(payload, ensure_ascii=False))
    raise PayloadBindingError(f"runtime payload template is missing: {chart_id}")


@lru_cache(maxsize=1)
def _load_runtime_payloads() -> list[dict[str, Any]]:
    with RUNTIME_PAYLOADS_PATH.open(encoding="utf-8") as file:
        return json.load(file)


def _component_data_specs(template: dict[str, Any]) -> list[dict[str, Any]]:
    specs: dict[str, dict[str, Any]] = {}
    chart_id = str(template.get("chartId", ""))
    for component in template.get("components", []):
        binding = component.get("dataBinding") or {}
        source = binding.get("source")
        if not source:
            continue
        source_key = str(source)
        fields = _component_fields(component)
        current = specs.setdefault(
            source_key,
            {
                "source": source_key,
                "componentType": component.get("componentType", ""),
                "fields": set(),
            },
        )
        current["fields"].update(fields)
    normalized: list[dict[str, Any]] = []
    for source_key, spec in sorted(specs.items()):
        fields = sorted(spec["fields"])
        transform = _infer_transform(source_key, str(spec["componentType"]), fields, chart_id)
        if transform in {
            "distance_metric_summary",
            "distance_metric_ranking",
            "text001_summary",
            "text001_distance",
            "text001_topic_mix",
            "text001_notes",
            "expl001_summary",
            "expl001_features",
            "expl001_distribution",
            "expl001_heatmap",
            "expl001_notes",
            "unc001_summary",
            "unc001_confidence",
            "unc001_entropy",
            "unc001_calibration",
            "unc001_notes",
            "variance_summary",
            "variance_spread",
            "variance_bars",
            "variance_stat",
            "variance_notes",
            "psi_summary",
            "psi_notes",
            "mmd_summary",
            "mmd_trend",
            "mmd_null_histogram",
            "mmd_notes",
            "anom_summary",
            "anom_score_distribution",
            "anom_rate_trend",
            "anom_projection",
            "anom_notes",
            "seqdrift_stream_summary",
            "seqdrift_stream_series",
            "seqdrift_evidence_series",
            "seqdrift_timeline",
            "seqdrift_notes",
            "rep001_summary",
            "rep001_heatmap",
            "rep001_activation",
            "rep001_projection",
            "rep001_notes",
            "rep003_summary",
            "rep003_projection",
            "rep003_heatmap",
            "rep003_distance",
            "rep003_notes",
        }:
            fields = sorted(set(fields) | set(_default_required_fields(transform)))
        normalized.append({"source": source_key, "transform": transform, "fields": fields})
    return normalized


def _component_fields(component: dict[str, Any]) -> set[str]:
    fields: set[str] = set()
    config = component.get("config") or {}
    for key, value in config.items():
        if key.endswith("_field") or key in {"time_field", "value_field", "label_field"}:
            fields.add(str(value))
    for value in (component.get("dataBinding") or {}).get("requiredFields", []):
        fields.add(str(value))
    return fields


def _infer_transform(source: str, component_type: str, fields: list[str], chart_id: str = "") -> str:
    source_lower = source.lower()
    chart_id_upper = chart_id.upper()
    field_set = set(fields)
    if chart_id_upper == "CHART-TEXT-001" and source_lower == "summary":
        return "text001_summary"
    if chart_id_upper == "CHART-TEXT-001" and source_lower == "projection":
        return "text001_projection"
    if chart_id_upper == "CHART-TEXT-001" and source_lower == "distance":
        return "text001_distance"
    if chart_id_upper == "CHART-TEXT-001" and source_lower == "topic_mix":
        return "text001_topic_mix"
    if chart_id_upper == "CHART-TEXT-001" and source_lower == "roc_small":
        return "text001_roc"
    if chart_id_upper == "CHART-TEXT-001" and source_lower == "notes":
        return "text001_notes"
    if chart_id_upper == "CHART-EXPL-001" and source_lower.endswith(".summary"):
        return "expl001_summary"
    if chart_id_upper == "CHART-EXPL-001" and source_lower.endswith(".features"):
        return "expl001_features"
    if chart_id_upper == "CHART-EXPL-001" and source_lower.endswith(".distribution"):
        return "expl001_distribution"
    if chart_id_upper == "CHART-EXPL-001" and source_lower.endswith(".heatmap"):
        return "expl001_heatmap"
    if chart_id_upper == "CHART-EXPL-001" and source_lower.endswith(".notes"):
        return "expl001_notes"
    if chart_id_upper == "CHART-UNC-001" and source_lower == "summary":
        return "unc001_summary"
    if chart_id_upper == "CHART-UNC-001" and source_lower == "confidence":
        return "unc001_confidence"
    if chart_id_upper == "CHART-UNC-001" and source_lower == "entropy":
        return "unc001_entropy"
    if chart_id_upper == "CHART-UNC-001" and source_lower == "calibration":
        return "unc001_calibration"
    if chart_id_upper == "CHART-UNC-001" and source_lower == "notes":
        return "unc001_notes"
    if chart_id_upper == "CHART-REP-001" and source_lower.endswith(".summary"):
        return "rep001_summary"
    if chart_id_upper == "CHART-REP-001" and source_lower.endswith(".heatmap"):
        return "rep001_heatmap"
    if chart_id_upper == "CHART-REP-001" and source_lower.endswith(".activation"):
        return "rep001_activation"
    if chart_id_upper == "CHART-REP-001" and source_lower.endswith(".projection"):
        return "rep001_projection"
    if chart_id_upper == "CHART-REP-001" and source_lower.endswith(".notes"):
        return "rep001_notes"
    if chart_id_upper == "CHART-REP-003" and source_lower.endswith(".summary"):
        return "rep003_summary"
    if chart_id_upper == "CHART-REP-003" and source_lower.endswith(".projection"):
        return "rep003_projection"
    if chart_id_upper == "CHART-REP-003" and source_lower.endswith(".heatmap"):
        return "rep003_heatmap"
    if chart_id_upper == "CHART-REP-003" and source_lower.endswith(".distance"):
        return "rep003_distance"
    if chart_id_upper == "CHART-REP-003" and source_lower.endswith(".notes"):
        return "rep003_notes"
    if chart_id_upper == "CHART-ANOM-001" and source_lower.endswith(".summary"):
        return "anom_summary"
    if chart_id_upper == "CHART-ANOM-001" and source_lower.endswith(".score"):
        return "anom_score_distribution"
    if chart_id_upper == "CHART-ANOM-001" and source_lower.endswith(".rate"):
        return "anom_rate_trend"
    if chart_id_upper == "CHART-ANOM-001" and source_lower.endswith(".projection"):
        return "anom_projection"
    if chart_id_upper == "CHART-ANOM-001" and source_lower.endswith(".notes"):
        return "anom_notes"
    if "chart-distshape-001.summary" in source_lower:
        return "distshape_summary"
    if "chart-distshape-001.density" in source_lower:
        return "reference_current_distribution"
    if "chart-distshape-001.ecf" in source_lower:
        return "distshape_ecf"
    if "chart-distshape-001.stat" in source_lower:
        return "distshape_stat"
    if "chart-bocd-001.summary" in source_lower:
        return "bocd_summary"
    if "chart-bocd-001.cp_heatmap" in source_lower:
        return "bocd_change_heatmap"
    if "chart-bocd-001.run_length" in source_lower:
        return "bocd_run_length_heatmap"
    if "chart-bocd-001.stream" in source_lower:
        return "bocd_stream_series"
    if "chart-bocd-001.notes" in source_lower:
        return "bocd_notes"
    if "chart-stream-002.summary" in source_lower:
        return "kswin_stream_summary"
    if "chart-stream-002.stream" in source_lower:
        return "kswin_stream_series"
    if "chart-stream-002.ecdf" in source_lower:
        return "kswin_ecdf"
    if "chart-stream-002.ks" in source_lower:
        return "kswin_stat_series"
    if "chart-stream-002.notes" in source_lower:
        return "kswin_stream_notes"
    if chart_id_upper == "CHART-STREAM-004" and source_lower == "summary":
        return "seqdrift_stream_summary"
    if chart_id_upper == "CHART-STREAM-004" and source_lower == "stream":
        return "seqdrift_stream_series"
    if chart_id_upper == "CHART-STREAM-004" and source_lower == "evidence":
        return "seqdrift_evidence_series"
    if chart_id_upper == "CHART-STREAM-004" and source_lower == "timeline":
        return "seqdrift_timeline"
    if chart_id_upper == "CHART-STREAM-004" and source_lower == "notes":
        return "seqdrift_notes"
    if "chart-err-005.series" in source_lower:
        return "hddm_error_series"
    if "chart-err-005.summary" in source_lower:
        return "hddm_error_summary"
    if "chart-err-005.timeline" in source_lower:
        return "hddm_error_timeline"
    if "chart-err-001.summary" in source_lower:
        return "ddm_error_summary"
    if "chart-err-001.error" in source_lower:
        return "ddm_error_series"
    if "chart-err-001.timeline" in source_lower:
        return "ddm_error_timeline"
    if "chart-dist-001.summary" in source_lower:
        return "distance_metric_summary"
    if "chart-dist-001.ranking" in source_lower:
        return "distance_metric_ranking"
    if "chart-psi-001.summary" in source_lower:
        return "psi_summary"
    if "chart-psi-001.notes" in source_lower:
        return "psi_notes"
    if "chart-mv-002.summary" in source_lower:
        return "mmd_summary"
    if "chart-mv-002.mmd" in source_lower:
        return "mmd_trend"
    if "chart-mv-002.null" in source_lower:
        return "mmd_null_histogram"
    if "chart-mv-002.notes" in source_lower:
        return "mmd_notes"
    if chart_id_upper == "CHART-VAR-001" and source_lower == "summary":
        return "variance_summary"
    if chart_id_upper == "CHART-VAR-001" and source_lower == "spread":
        return "variance_spread"
    if chart_id_upper == "CHART-VAR-001" and source_lower == "variance":
        return "variance_bars"
    if chart_id_upper == "CHART-VAR-001" and source_lower == "deviation":
        return "variance_stat"
    if chart_id_upper == "CHART-VAR-001" and source_lower == "notes":
        return "variance_notes"
    if "chart-var-001.summary" in source_lower:
        return "variance_summary"
    if "chart-var-001.main" in source_lower or "chart-var-001.spread" in source_lower:
        return "variance_spread"
    if "chart-var-001.side_top" in source_lower or source_lower.endswith("variance"):
        return "variance_bars"
    if "chart-var-001.side_bottom" in source_lower or source_lower.endswith("deviation"):
        return "variance_stat"
    if "chart-var-001.notes" in source_lower:
        return "variance_notes"
    if source_lower.endswith(".notes") or source_lower == "notes" or "note" in source_lower:
        return "analysis_note"
    if source_lower.endswith(".summary") or source_lower == "summary" or component_type == "decision_card":
        return "event_summary"
    if component_type in {"matrix_view", "heatmap"} or "values" in field_set:
        return "matrix_values"
    if component_type in {"projection_scatter", "feature_projection_view"} or {"x", "y"} <= field_set:
        return "projection_points"
    if component_type in {"distribution_view", "histogram_view", "distribution_summary_plot", "circular_histogram"}:
        return "reference_current_distribution"
    if field_set & {"reference", "current", "baseline", "x0", "x1", "density", "q1", "q3", "observed"}:
        return "reference_current_distribution"
    if component_type == "distance_metric_view" and "chart-dist-001.trend" in source_lower:
        return "distance_metric_trend"
    if component_type == "distance_metric_view" and source_lower.endswith(".trend") and "psi" in field_set:
        return "psi_trend"
    if component_type == "state_timeline" or field_set & {"start", "end", "window"}:
        return "event_timeline"
    if component_type in {"trend_line", "raw_signal_trend", "detector_statistic_view"}:
        return "metric_series"
    if component_type in {"bar_chart", "contribution_view"}:
        return "category_contribution"
    if component_type == "distance_metric_view":
        return "metric_series"
    if field_set & {"category", "feature", "metric", "bin", "contribution", "psi", "kl", "mmd", "lsdd", "t2"}:
        return "category_contribution"
    if field_set & {"time", "value", "score", "stat", "error", "distance", "rate"}:
        return "metric_series"
    return "event_summary"


def _adjust_auto_template(method_variant_key: str, chart_id: str, template: dict[str, Any]) -> None:
    psi_variants = {
        "NUMERIC_BINNED_PSI",
        "CATEGORICAL_PSI",
        "SCORE_BAND_PSI",
        "POPULATION_WEIGHTED_PSI",
    }
    if chart_id == "CHART-DISTSHAPE-001":
        _adjust_distshape_template(template)
    if chart_id == "CHART-VAR-001":
        _adjust_variance_template(method_variant_key, template)
    if chart_id == "CHART-ERR-001":
        _adjust_err001_template(template)
    if method_variant_key not in psi_variants or chart_id != "CHART-PSI-001":
        if method_variant_key in {"KSWIN_STANDARD", "KSWIN_NUMERIC_STREAM"} and chart_id == "CHART-STREAM-002":
            _adjust_kswin_stream_template(template)
        return
    for component in template.get("components", []):
        component_id = str(component.get("componentInstanceId", ""))
        config = component.get("config") or {}
        if component_id.endswith(".bins.0"):
            config.pop("y_max", None)
            config.pop("y_ticks", None)
        elif component_id.endswith(".contrib.0"):
            config.pop("x_max", None)
        elif component_id.endswith(".trend.0"):
            config.pop("y_max", None)
            config.pop("y_ticks", None)


def _adjust_kswin_stream_template(template: dict[str, Any]) -> None:
    for component in template.get("components", []):
        component_id = str(component.get("componentInstanceId", ""))
        config = component.get("config") or {}
        if component_id.endswith(".stream.0"):
            config.pop("y_min", None)
            config.pop("y_max", None)
            config.pop("y_ticks", None)
        elif component_id.endswith(".ecdf.0"):
            config.pop("x_min", None)
            config.pop("x_max", None)
            config.pop("x_ticks", None)
        elif component_id.endswith(".ks.0"):
            config.pop("y_max", None)
            config.pop("y_ticks", None)


def _adjust_distshape_template(template: dict[str, Any]) -> None:
    template["title"] = "CHART-DISTSHAPE-001 - reference/current 분포 모양 변화"
    for area in template.get("layout", {}).get("areas", []):
        if area.get("area") == "main":
            area["description"] = "reference/current 표본의 밀도 곡선을 같은 축에서 비교한다."
        elif area.get("area") == "side_top":
            area["description"] = "여러 frequency t에서 empirical characteristic function 차이를 비교한다."
        elif area.get("area") == "side_bottom":
            area["description"] = "frequency별 shape-difference 기여도를 비교한다."
    for component in template.get("components", []):
        component_id = str(component.get("componentInstanceId", ""))
        config = component.get("config") or {}
        if component_id.endswith(".distribution.0"):
            for key in ("x_min", "x_max", "y_min", "y_max", "x_ticks", "y_ticks"):
                config.pop(key, None)
            config["annotations"] = []
        elif component_id.endswith(".ecf.0"):
            for key in ("x_min", "x_max", "y_min", "y_max", "x_ticks", "y_ticks"):
                config.pop(key, None)
            config["annotations"] = []
        elif component_id.endswith(".stat.0"):
            config.pop("x_max", None)
            config["annotations"] = []


def _adjust_variance_template(method_variant_key: str, template: dict[str, Any]) -> None:
    method_label = {
        "F_TEST_EQUAL_VARIANCE": "F-test",
        "BROWN_FORSYTHE_MEDIAN_CENTER": "Brown-Forsythe",
        "LEVENE_MEAN_CENTER": "Levene",
        "TRIMMED_MEAN_LEVENE": "trimmed-mean Levene",
    }.get(method_variant_key, method_variant_key.replace("_", " ").title())
    for component in template.get("components", []):
        component_id = str(component.get("componentInstanceId", ""))
        config = component.get("config") or {}
        if component_id.endswith(".main.0"):
            for key in ("y_min", "y_max", "y_ticks"):
                config.pop(key, None)
            config["annotations"] = []
        elif component_id.endswith(".side_top.0"):
            config.pop("y_max", None)
            config.pop("y_ticks", None)
            config["x_axis_label"] = "reference/current variance"
        elif component_id.endswith(".side_bottom.0"):
            config.pop("x_max", None)
            config["caption"] = f"{method_label} statistic"


def _adjust_err001_template(template: dict[str, Any]) -> None:
    for component in template.get("components", []):
        component_id = str(component.get("componentInstanceId", ""))
        config = component.get("config") or {}
        if component_id.endswith(".error.0"):
            config["vertical_markers"] = []
            config["point_highlights"] = []
            config["annotations"] = []
        elif component_id.endswith(".margin.0"):
            config["vertical_markers"] = []
            config["annotations"] = []
        elif component_id.endswith(".timeline.0"):
            config["x_min"] = 1
            config["x_max"] = 32
            config["label_map"] = {"normal": " ", "warning": "W", "drift": "D"}
            config["track_overlays"] = []
            config["markers"] = []


def _default_required_fields(transform: str) -> list[str]:
    if transform in {"analysis_note", "kswin_stream_notes", "bocd_notes"}:
        return ["title", "text"]
    if transform == "variance_notes":
        return ["legend", "text", "title"]
    if transform == "distance_metric_summary":
        return ["label", "value", "displayValue"]
    if transform == "distance_metric_ranking":
        return ["feature", "distance", "distanceLabel", "class"]
    if transform == "text001_summary":
        return ["displayValue", "label", "value"]
    if transform == "text001_distance":
        return ["time", "value"]
    if transform == "text001_topic_mix":
        return ["category", "topic1", "topic2", "topic3", "topic3_label"]
    if transform == "text001_notes":
        return ["legend", "text", "title"]
    if transform == "expl001_summary":
        return ["displayValue", "label", "value"]
    if transform == "expl001_features":
        return ["baseline", "current", "feature"]
    if transform == "expl001_distribution":
        return ["baseline", "current", "shap"]
    if transform == "expl001_heatmap":
        return ["class", "values"]
    if transform == "expl001_notes":
        return ["legend", "text", "title"]
    if transform == "unc001_summary":
        return ["label", "value"]
    if transform == "unc001_confidence":
        return ["baseline", "confidence", "current"]
    if transform == "unc001_entropy":
        return ["time", "value"]
    if transform == "unc001_calibration":
        return ["time", "value"]
    if transform == "unc001_notes":
        return ["legend", "text", "title"]
    if transform == "variance_summary":
        return ["displayValue", "label", "value"]
    if transform == "variance_spread":
        return ["center", "class", "density", "high", "label", "low", "mean", "median", "q1", "q3"]
    if transform == "variance_bars":
        return ["class", "display", "label", "variance"]
    if transform == "variance_stat":
        return ["class", "display", "label", "threshold", "value"]
    if transform == "psi_summary":
        return ["displayValue", "label", "value"]
    if transform == "psi_notes":
        return ["legend", "text", "title"]
    if transform == "mmd_summary":
        return ["displayValue", "label", "value"]
    if transform == "mmd_trend":
        return ["mmd", "window"]
    if transform == "mmd_null_histogram":
        return ["class", "count", "x0", "x1"]
    if transform == "mmd_notes":
        return ["legend", "text", "title"]
    if transform == "anom_summary":
        return ["label", "value"]
    if transform == "anom_score_distribution":
        return ["baseline", "current", "score"]
    if transform == "anom_rate_trend":
        return ["rate", "time"]
    if transform == "anom_projection":
        return ["group", "x", "y"]
    if transform == "anom_notes":
        return ["legend", "text", "title"]
    if transform == "hddm_error_summary":
        return ["label", "value"]
    if transform == "seqdrift_stream_summary":
        return ["label", "value"]
    if transform == "seqdrift_stream_series":
        return ["time", "value"]
    if transform == "seqdrift_evidence_series":
        return ["time", "evidence", "bound", "pointClass", "pointRadius"]
    if transform == "seqdrift_timeline":
        return ["start", "end", "role", "label"]
    if transform == "seqdrift_notes":
        return ["title", "text", "legend"]
    if transform in {"rep001_summary", "rep003_summary"}:
        return ["displayValue", "label", "value"]
    if transform == "rep001_heatmap":
        return ["layer", "values"]
    if transform == "rep001_activation":
        return ["baseline", "bin", "current"]
    if transform in {"rep001_projection", "rep003_projection"}:
        return ["group", "x", "y"]
    if transform in {"rep001_notes", "rep003_notes"}:
        return ["legend", "text", "title"]
    if transform == "rep003_heatmap":
        return ["nodeGroup", "values"]
    if transform == "rep003_distance":
        return ["time", "value"]
    return ["label", "value"]


def _auto_binding_key(method_variant_key: str, chart_id: str) -> str:
    return f"{_AUTO_PREFIX}{method_variant_key}__{chart_id}"


def _parse_auto_binding_key(binding_key: str) -> tuple[str, str]:
    rest = binding_key[len(_AUTO_PREFIX) :]
    try:
        method_variant_key, chart_id = rest.rsplit("__", 1)
    except ValueError as exc:
        raise PayloadBindingError(f"invalid auto binding key: {binding_key}") from exc
    return method_variant_key, chart_id


@lru_cache(maxsize=1)
def _load_chart_methods() -> dict[str, list[dict[str, Any]]]:
    method_data_path = _find_method_data_path()
    text = method_data_path.read_text(encoding="utf-8")
    prefix = "window.CHART_METHODS = "
    if not text.startswith(prefix) or not text.rstrip().endswith(";"):
        raise PayloadBindingError(f"cannot parse chart method catalog: {method_data_path}")
    return json.loads(text[len(prefix) :].rstrip()[:-1])


def _find_method_data_path() -> Path:
    for child in REPO_ROOT.iterdir():
        candidate = child / "charts" / "method_data.js"
        if child.name.startswith("drift ") and candidate.exists():
            return candidate
    raise PayloadBindingError("drift report method_data.js is not found")


def _method_variant_key(method_value: str) -> str:
    if "/" in method_value:
        return method_value.rsplit("/", 1)[1].strip()
    return method_value.strip()
