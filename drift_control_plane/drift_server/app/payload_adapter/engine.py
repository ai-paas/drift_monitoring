from __future__ import annotations

import copy
import re
from typing import Any


class PayloadBindingError(ValueError):
    pass


_TEMPLATE_PATTERN = re.compile(r"{([^{}]+)}")


class BindingPayloadAdapter:
    def __init__(self, spec: dict[str, Any]) -> None:
        self.spec = spec

    # @managed-contract contract_id=payload_adapter.engine.BindingPayloadAdapter.build level=P0
    def build(self, context: dict[str, Any]) -> dict[str, Any]:
        self._validate_context_contract(context)
        payload = copy.deepcopy(self.spec["payloadTemplate"])
        payload["chartId"] = self.spec["chartId"]
        payload["sourceId"] = _path(context, "$.source.sourceId")
        payload["eventId"] = _path(context, "$.driftEvent.eventId")
        payload["featureId"] = _path(context, "$.feature.featureId")
        payload["data"] = self._build_data(context)
        payload["metadata"] = self._build_metadata(context)
        _apply_payload_data_labels(payload)
        self._validate_payload(payload)
        return payload

    def _build_data(self, context: dict[str, Any]) -> dict[str, Any]:
        output: dict[str, Any] = {}
        for binding in self.spec.get("dataBindings", []):
            source_key = binding["targetDataSource"]
            input_name = binding["input"]
            if input_name == "buckets":
                rows = [_map_row(binding, context, {"bucket": bucket}) for bucket in context.get("buckets", [])]
            elif input_name == "single":
                rows = [_map_row(binding, context, {})]
            elif input_name == "literalRows":
                rows = [_evaluate_templates(row, context, {}) for row in binding.get("rows", [])]
            elif input_name == "derivedRows":
                from .transformations import build_derived_rows

                rows = build_derived_rows(binding["transform"], binding.get("fields", []), context)
            else:
                raise PayloadBindingError(f"unsupported binding input: {input_name}")
            output[source_key] = rows
        return output

    def _build_metadata(self, context: dict[str, Any]) -> dict[str, Any]:
        metadata = {
            "bindingId": self.spec["bindingId"],
            "methodVariantKey": self.spec["methodVariantKey"],
            "runtimeMethodKey": _path(context, "$.assignment.runtimeMethodKey", None),
            "methodRunId": _path(context, "$.methodRun.methodRunId", None),
            "score": _path(context, "$.driftEvent.score", None),
        }
        runtime_result = context.get("runtimeResult") or {}
        for key in ("metrics", "diagnostics", "payloadHints"):
            if key in runtime_result:
                metadata[key] = runtime_result[key]
        return metadata

    # @managed-contract contract_id=payload_adapter.engine.BindingPayloadAdapter._validate_context_contract level=P0
    def _validate_context_contract(self, context: dict[str, Any]) -> None:
        contract = self.spec.get("methodEventContract", {})
        for required_path in contract.get("requiredContextPaths", []):
            if _path(context, required_path, _MISSING) is _MISSING:
                raise PayloadBindingError(f"required context path is missing: {required_path}")

    # @managed-contract contract_id=payload_adapter.engine.BindingPayloadAdapter._validate_payload level=P0
    def _validate_payload(self, payload: dict[str, Any]) -> None:
        if payload.get("chartId") != self.spec.get("chartId"):
            raise PayloadBindingError("payload chartId does not match binding chartId")
        data = payload.get("data")
        if not isinstance(data, dict):
            raise PayloadBindingError("payload data must be an object")
        for component in payload.get("components", []):
            binding = component.get("dataBinding") or {}
            source = binding.get("source")
            if source and source not in data:
                component_id = component.get("componentInstanceId", "<unknown>")
                raise PayloadBindingError(f"component data source is missing: {component_id} -> {source}")
        for data_contract in self.spec.get("dataContracts", []):
            source = data_contract["source"]
            required_fields = data_contract.get("requiredFields", [])
            for index, row in enumerate(data.get(source, [])):
                for field in required_fields:
                    if field not in row:
                        raise PayloadBindingError(f"required field is missing: {source}[{index}].{field}")


def _map_row(binding: dict[str, Any], context: dict[str, Any], locals_: dict[str, Any]) -> dict[str, Any]:
    row: dict[str, Any] = {}
    for target_field, rule in binding.get("fields", {}).items():
        row[target_field] = _evaluate(rule, context, locals_)
    return row


def _evaluate(rule: Any, context: dict[str, Any], locals_: dict[str, Any]) -> Any:
    if isinstance(rule, str):
        if rule.startswith("$."):
            return _path(context, rule)
        if rule.startswith("@."):
            return _path(locals_, rule)
        return _render_template(rule, context, locals_)
    if isinstance(rule, dict):
        if "path" in rule:
            value = _evaluate(rule["path"], context, locals_)
            return _transform(value, rule.get("transform"))
        if "value" in rule:
            return rule["value"]
        if "template" in rule:
            return _render_template(rule["template"], context, locals_)
    return copy.deepcopy(rule)


def _transform(value: Any, transform: str | None) -> Any:
    if transform == "displayFloat4":
        return f"{float(value):.4f}" if value is not None else ""
    if transform is None:
        return value
    raise PayloadBindingError(f"unsupported transform: {transform}")


def _render_template(template: str, context: dict[str, Any], locals_: dict[str, Any]) -> str:
    def replace(match: re.Match[str]) -> str:
        expression = match.group(1)
        root = locals_ if expression.startswith("@.") else context
        path = expression if expression.startswith("@.") or expression.startswith("$.") else f"$.{expression}"
        return str(_path(root, path, ""))

    return _TEMPLATE_PATTERN.sub(replace, template)


def _evaluate_templates(value: Any, context: dict[str, Any], locals_: dict[str, Any]) -> Any:
    if isinstance(value, str):
        return _render_template(value, context, locals_)
    if isinstance(value, list):
        return [_evaluate_templates(item, context, locals_) for item in value]
    if isinstance(value, dict):
        return {key: _evaluate_templates(item, context, locals_) for key, item in value.items()}
    return copy.deepcopy(value)


def _apply_payload_data_labels(payload: dict[str, Any]) -> None:
    if payload.get("chartId") != "CHART-PSI-001":
        if payload.get("chartId") == "CHART-MV-002":
            _apply_mv002_layout_labels(payload)
        elif payload.get("chartId") == "CHART-ANOM-001":
            _apply_anom001_layout_labels(payload)
        elif payload.get("chartId") == "CHART-ERR-005":
            _apply_err005_layout_labels(payload)
        elif payload.get("chartId") == "CHART-STREAM-004":
            _apply_stream004_layout_labels(payload)
        elif payload.get("chartId") == "CHART-TEXT-001":
            _apply_text001_layout_labels(payload)
        elif payload.get("chartId") == "CHART-EXPL-001":
            _apply_expl001_layout_labels(payload)
        elif payload.get("chartId") == "CHART-UNC-001":
            _apply_unc001_layout_labels(payload)
        elif payload.get("chartId") in {"CHART-REP-001", "CHART-REP-003"}:
            _apply_rep_layout_labels(payload)
        return
    _apply_psi_layout_labels(payload)


def _apply_psi_layout_labels(payload: dict[str, Any]) -> None:
    data = payload.get("data") or {}
    contribution_rows = data.get("chart.CHART-PSI-001.contrib") or []
    bin_rows = data.get("chart.CHART-PSI-001.bins") or []
    summary_rows = data.get("chart.CHART-PSI-001.summary") or []
    trend_rows = data.get("chart.CHART-PSI-001.trend") or []
    if not contribution_rows and not bin_rows:
        return

    top_row = _top_contribution_row(contribution_rows or bin_rows)
    top_label = str(top_row.get("label") or top_row.get("category") or top_row.get("bin") or "top bin")
    reference = _safe_float(top_row.get("reference"))
    current = _safe_float(top_row.get("current"))
    delta_label = str(top_row.get("deltaLabel") or _percentage_point_delta(reference, current))
    contribution = str(top_row.get("displayValue") or _format_number(top_row.get("value")))
    psi_display = _summary_display(summary_rows, "PSI") or _format_number((trend_rows[-1] if trend_rows else {}).get("psi"))
    threshold_display = _summary_display(summary_rows, "threshold")
    if not threshold_display:
        threshold_display = _format_number(_metadata_threshold(payload))
    comparison = "넘는다"
    psi_value = _safe_float(_summary_value(summary_rows, "PSI"))
    threshold_value = _safe_float(_summary_value(summary_rows, "threshold"))
    if threshold_value is not None and psi_value is not None and psi_value < threshold_value:
        comparison = "보다 낮다"

    payload["title"] = "구간 비율 변화로 본 PSI 드리프트"
    for area in (payload.get("layout") or {}).get("areas", []):
        area_name = area.get("area")
        if area_name == "main":
            area["description"] = (
                f"{top_label} 구간은 기준 {_format_percent(reference)}에서 "
                f"현재 {_format_percent(current)}로 {delta_label} 변했다."
            )
        elif area_name == "side_top":
            area["description"] = f"{top_label} 기여도 {contribution}가 전체 PSI에서 가장 크다."
        elif area_name == "side_bottom":
            area["description"] = f"최근 window PSI {psi_display}가 관리 기준 {threshold_display}을 {comparison}."

    for component in payload.get("components", []):
        if not str(component.get("componentInstanceId", "")).endswith(".bins.0"):
            continue
        config = component.get("config") or {}
        for annotation in config.get("annotations") or []:
            if not isinstance(annotation, dict):
                continue
            if "category" in annotation:
                annotation["category"] = top_label
            if "text" in annotation:
                annotation["text"] = f"상위 기여: {top_label}"


def _top_contribution_row(rows: list[dict[str, Any]]) -> dict[str, Any]:
    sortable = [row for row in rows if isinstance(row, dict)]
    if not sortable:
        return {}
    return max(sortable, key=lambda row: _safe_float(row.get("value")) or 0.0)


def _summary_display(rows: list[dict[str, Any]], label: str) -> str:
    for row in rows:
        if isinstance(row, dict) and row.get("label") == label:
            return str(row.get("displayValue") or row.get("value") or "")
    return ""


def _summary_value(rows: list[dict[str, Any]], label: str) -> Any:
    for row in rows:
        if isinstance(row, dict) and row.get("label") == label:
            return row.get("value")
    return None


def _metadata_threshold(payload: dict[str, Any]) -> Any:
    return _path(
        payload,
        "$.metadata.metrics.statistic.threshold",
        _path(
            payload,
            "$.metadata.metrics.threshold",
            _path(payload, "$.metadata.metrics.measurements.THRESHOLD", None),
        ),
    )


def _percentage_point_delta(reference: float | None, current: float | None) -> str:
    if reference is None or current is None:
        return ""
    return f"{(current - reference) * 100:+.1f}pp"


def _format_percent(value: float | None) -> str:
    if value is None:
        return "n/a"
    return f"{value * 100:.1f}%"


def _format_number(value: Any) -> str:
    numeric = _safe_float(value)
    if numeric is None:
        return ""
    return f"{numeric:.3f}"


def _safe_float(value: Any) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _apply_err005_layout_labels(payload: dict[str, Any]) -> None:
    data = payload.get("data") or {}
    series_rows = data.get("chart.CHART-ERR-005.series") or []
    summary_rows = data.get("chart.CHART-ERR-005.summary") or []
    if not series_rows and not summary_rows:
        return
    metrics = ((payload.get("metadata") or {}).get("metrics") or {})
    measurements = metrics.get("measurements") if isinstance(metrics.get("measurements"), dict) else {}
    score = (
        _safe_float(metrics.get("testStatistic"))
        or _safe_float(measurements.get("TEST_STATISTIC"))
        or _safe_float((payload.get("metadata") or {}).get("score"))
        or 0.0
    )
    warning_bound = (
        _safe_float(measurements.get("HOEFFDING_WARNING_BOUND"))
        or _safe_float(metrics.get("warningBound"))
        or _safe_float(metrics.get("warning"))
        or 0.0
    )
    drift_bound = (
        _safe_float(measurements.get("HOEFFDING_DRIFT_BOUND"))
        or _safe_float(metrics.get("threshold"))
        or _safe_float(_metadata_threshold(payload))
        or 0.0
    )
    max_diff = max([abs(_safe_float(row.get("diff")) or 0.0) for row in series_rows if isinstance(row, dict)] + [score, drift_bound])
    max_error = max([_safe_float(row.get("error")) or 0.0 for row in series_rows if isinstance(row, dict)] + [0.0])
    x_values = [_safe_float(row.get("time")) for row in series_rows if isinstance(row, dict)]
    x_max = max([value for value in x_values if value is not None] + [1.0])
    drift_x = _event_axis_from_measurement(measurements, "DRIFT_INDEX", x_max)
    warning_x = _event_axis_from_measurement(measurements, "WARNING_START_INDEX", x_max)
    y_max = max(max_diff * 1.35, drift_bound * 1.45, warning_bound * 1.55, 0.04)
    y_min = min(0.0, -y_max * 0.1)

    for area in (payload.get("layout") or {}).get("areas", []):
        area_name = area.get("area")
        if area_name == "main":
            area["description"] = f"HDDM-A mean difference {score:.4f} is compared with drift bound {drift_bound:.4f}."
        elif area_name == "side_top":
            area["description"] = f"Latest error rate is {_format_number(metrics.get('errorRate'))}."
        elif area_name == "side_bottom":
            area["description"] = "Warning/drift interval is aligned to the runtime event position."

    for component in payload.get("components", []):
        component_id = str(component.get("componentInstanceId", ""))
        config = component.get("config") or {}
        if component_id.endswith(".bound.0"):
            config["x_min"] = 1
            config["x_max"] = round(x_max, 6)
            config["x_ticks"] = _axis_ticks(x_max)
            config["y_min"] = round(y_min, 6)
            config["y_max"] = round(y_max, 6)
            config["y_ticks"] = _nice_ticks(0.0, y_max, 4)
            config["horizontal_markers"] = [
                {
                    "y": round(warning_bound, 6),
                    "class": "warning-line",
                    "label": f"warning {warning_bound:.4f}",
                    "label_class": "warning-text",
                    "label_x": 3,
                    "label_dy": -8,
                },
                {
                    "y": round(drift_bound, 6),
                    "class": "drift-line",
                    "label": f"drift {drift_bound:.4f}",
                    "label_class": "drift-text",
                    "label_x": 3,
                    "label_dy": -8,
                },
            ]
            config["vertical_markers"] = _event_markers(warning_x, drift_x)
            config["annotations"] = [
                {
                    "text": f"score {score:.4f} >= drift {drift_bound:.4f}",
                    "x": max(1.0, min(x_max, drift_x or x_max * 0.75)),
                    "y": round(y_max * 0.88, 6),
                    "class": "callout",
                }
            ]
        elif component_id.endswith(".error.0"):
            config["x_min"] = 1
            config["x_max"] = round(x_max, 6)
            config["x_ticks"] = _axis_ticks(x_max)
            config["y_min"] = 0
            config["y_max"] = round(max(max_error * 1.22, 0.1), 6)
            config["y_ticks"] = _nice_ticks(0.0, max(max_error * 1.22, 0.1), 4)
            config["vertical_markers"] = _event_markers(None, drift_x)
        elif component_id.endswith(".timeline.0"):
            config["x_min"] = 1
            config["x_max"] = round(x_max, 6)
            config["x_ticks"] = _axis_ticks(x_max)


def _apply_text001_layout_labels(payload: dict[str, Any]) -> None:
    data = payload.get("data") or {}
    summary_rows = data.get("summary") or []
    topic_rows = data.get("topic_mix") or []
    distance_rows = data.get("distance") or []
    metrics = ((payload.get("metadata") or {}).get("metrics") or {})
    measurements = metrics.get("measurements") if isinstance(metrics.get("measurements"), dict) else {}
    score = (
        _safe_float(measurements.get("JENSEN_SHANNON_DISTANCE"))
        or _safe_float(measurements.get("COSINE_DISTANCE"))
        or _safe_float(metrics.get("testStatistic"))
        or _safe_float((payload.get("metadata") or {}).get("score"))
        or 0.0
    )
    threshold = _safe_float(metrics.get("threshold")) or _safe_float(measurements.get("THRESHOLD")) or 0.1
    ref_size = int(_safe_float(measurements.get("SAMPLE_SIZE_REFERENCE")) or 0)
    cur_size = int(_safe_float(measurements.get("SAMPLE_SIZE_CURRENT")) or 0)
    top_topic, ref_prop, cur_prop = _text001_top_topic(measurements)
    delta_pp = (cur_prop - ref_prop) * 100.0
    y_max = max(score * 1.22, threshold * 1.45, 0.12)

    payload["title"] = "토픽 분포 변화로 본 텍스트 의미 드리프트"
    for area in (payload.get("layout") or {}).get("areas", []):
        area_name = area.get("area")
        if area_name == "main":
            area["description"] = f"reference {ref_size}건과 current {cur_size}건의 토픽 분포가 분리되는지 본다."
        elif area_name == "side_top":
            area["description"] = f"JS distance {score:.3f}가 관리 기준 {threshold:.3f}을 넘는다."
        elif area_name == "side_bottom":
            area["description"] = f"{top_topic} 비율이 기준 {ref_prop * 100:.1f}%에서 현재 {cur_prop * 100:.1f}%로 {delta_pp:+.1f}pp 변했다."

    for component in payload.get("components", []):
        component_id = str(component.get("componentInstanceId", ""))
        config = component.get("config") or {}
        if component_id.endswith(".side_top.0"):
            config["x_min"] = 1
            config["x_max"] = max(5, len(distance_rows))
            config["x_ticks"] = list(range(1, max(5, len(distance_rows)) + 1))
            config["y_min"] = 0
            config["y_max"] = round(y_max, 6)
            config["y_ticks"] = _nice_ticks(0.0, y_max, 4)
            config["x_axis_label"] = "Jensen-Shannon distance"
            config["horizontal_markers"] = [
                {
                    "y": round(threshold, 6),
                    "class": "limit-line",
                    "label": f"threshold {threshold:.3f}",
                    "label_class": "warning-text",
                    "label_x": 1,
                    "label_dy": -8,
                }
            ]
            config["annotations"] = [
                {
                    "text": f"JS {score:.3f} > {threshold:.3f}",
                    "x": max(1, len(distance_rows)),
                    "y": round(min(y_max * 0.9, max(score, threshold)), 6),
                    "class": "warning-text",
                }
            ]
        elif component_id.endswith(".side_bottom.0"):
            config["caption"] = "top topic mix"
            config["value_label_field"] = "topic3_label"
        elif component_id.endswith(".side_bottom.1"):
            config["x_axis_label"] = "separation surrogate"
        elif component_id.endswith(".notes.0") and summary_rows:
            config["card_style"] = "notes_legend"
    if topic_rows:
        for row in topic_rows:
            row.setdefault("topic3_label", f"{top_topic} {delta_pp:+.1f}pp")


def _text001_top_topic(measurements: dict[str, Any]) -> tuple[str, float, float]:
    reference = measurements.get("TOPIC_PROPORTIONS_REFERENCE")
    current = measurements.get("TOPIC_PROPORTIONS_CURRENT")
    if not isinstance(reference, dict):
        reference = {}
    if not isinstance(current, dict):
        current = {}
    topics = sorted(set(reference) | set(current))
    if not topics:
        return "topic", 0.0, 0.0
    topic = max(topics, key=lambda item: abs((_safe_float(current.get(item)) or 0.0) - (_safe_float(reference.get(item)) or 0.0)))
    return str(topic), _safe_float(reference.get(topic)) or 0.0, _safe_float(current.get(topic)) or 0.0


def _apply_expl001_layout_labels(payload: dict[str, Any]) -> None:
    data = payload.get("data") or {}
    feature_rows = data.get("chart.CHART-EXPL-001.features") or []
    summary_rows = data.get("chart.CHART-EXPL-001.summary") or []
    if not feature_rows and not summary_rows:
        return
    top_row = _top_expl001_feature(feature_rows)
    top_feature = str(top_row.get("feature") or "feature")
    reference = _safe_float(top_row.get("baseline")) or 0.0
    current = _safe_float(top_row.get("current")) or 0.0
    delta_pp = (current - reference) * 100.0
    score = (
        _safe_float(_summary_value(summary_rows, "SHAP distance"))
        or _safe_float((payload.get("metadata") or {}).get("score"))
        or 0.0
    )
    threshold = (
        _safe_float(_summary_value(summary_rows, "threshold"))
        or _safe_float(_metadata_threshold(payload))
        or 0.05
    )
    comparison = "넘는다" if score >= threshold else "보다 낮다"
    feature_names = [str(row.get("feature")) for row in feature_rows if isinstance(row, dict) and row.get("feature")]
    x_max = max([_safe_float(row.get("baseline")) or 0.0 for row in feature_rows] + [_safe_float(row.get("current")) or 0.0 for row in feature_rows] + [0.1])
    x_max = max(x_max * 1.18, 0.1)

    payload["title"] = "설명 중요도 순위 변화로 본 Explainability 드리프트"
    for area in (payload.get("layout") or {}).get("areas", []):
        area_name = area.get("area")
        if area_name == "main":
            area["description"] = (
                f"{top_feature} 중요도가 기준 {_format_percent(reference)}에서 "
                f"현재 {_format_percent(current)}로 {delta_pp:+.1f}pp 변했다."
            )
        elif area_name == "side_top":
            area["description"] = f"SHAP drift score {score:.3f}가 관리 기준 {threshold:.3f}을 {comparison}."
        elif area_name == "side_bottom":
            area["description"] = f"{top_feature} 중심으로 feature별 reference/current 중요도와 순위 변화를 비교한다."

    for component in payload.get("components", []):
        component_id = str(component.get("componentInstanceId", ""))
        config = component.get("config") or {}
        if component_id.endswith(".shap_summary.0"):
            config["x_max"] = round(x_max, 6)
            config["x_ticks"] = _nice_ticks(0.0, x_max, 5)
            config["x_axis_label"] = "reference/current importance"
            config["annotations"] = [
                {
                    "text": f"{top_feature} {delta_pp:+.1f}pp",
                    "x": round(min(x_max * 0.78, max(reference, current)), 6),
                    "y": 19,
                    "class": "warning-text",
                }
            ]
        elif component_id.endswith(".distribution.0"):
            config["x_axis_label"] = f"{top_feature} importance shift surrogate"
            config["x_min"] = -0.4
            config["x_max"] = 0.4
            config.pop("y_max", None)
            config.pop("y_ticks", None)
            config["annotations"] = [
                {
                    "text": f"score {score:.3f} / threshold {threshold:.3f}",
                    "x": 0.03,
                    "y": 36,
                    "class": "warning-text",
                }
            ]
        elif component_id.endswith(".class_heatmap.0"):
            config["x_values"] = feature_names
            config["x_labels"] = feature_names
            config["y_values"] = ["reference rank", "current rank", "rank delta"]
            config["x_axis_label"] = "feature importance/rank drift"
            config["value_max"] = max(
                [_safe_float(value) or 0.0 for row in data.get("chart.CHART-EXPL-001.heatmap", []) for value in (row.get("values") or [])]
                + [1.0]
            )


def _top_expl001_feature(rows: list[dict[str, Any]]) -> dict[str, Any]:
    sortable = [row for row in rows if isinstance(row, dict)]
    if not sortable:
        return {}
    return max(sortable, key=lambda row: abs((_safe_float(row.get("current")) or 0.0) - (_safe_float(row.get("baseline")) or 0.0)))


def _apply_unc001_layout_labels(payload: dict[str, Any]) -> None:
    data = payload.get("data") or {}
    summary_rows = data.get("summary") or []
    confidence_rows = data.get("confidence") or []
    entropy_rows = data.get("entropy") or []
    if not summary_rows and not confidence_rows and not entropy_rows:
        return
    metadata = payload.get("metadata") or {}
    metrics = metadata.get("metrics") if isinstance(metadata.get("metrics"), dict) else {}
    measurements = metrics.get("measurements") if isinstance(metrics.get("measurements"), dict) else {}
    score = (
        _safe_float(measurements.get("TEST_STATISTIC"))
        or _safe_float(metrics.get("testStatistic"))
        or _safe_float(metadata.get("score"))
        or 0.0
    )
    threshold = _safe_float(metrics.get("threshold")) or _safe_float(measurements.get("THRESHOLD")) or 0.05
    p_value = _safe_float(measurements.get("P_VALUE"))
    if p_value is None:
        p_value = _safe_float(metrics.get("pValue"))
    if p_value is None:
        p_value = 1.0
    reference_mean = _safe_float(measurements.get("UNCERTAINTY_MEAN_REFERENCE")) or 0.0
    current_mean = _safe_float(measurements.get("UNCERTAINTY_MEAN_CURRENT")) or reference_mean
    mean_delta = _safe_float(measurements.get("UNCERTAINTY_MEAN_DELTA"))
    if mean_delta is None:
        mean_delta = current_mean - reference_mean
    method_key = str((metadata.get("methodVariantKey") or "")).upper()
    metric_label = "confidence" if "SOFTMAX_CONFIDENCE_DRIFT" in method_key else "uncertainty"
    confidence_y_max = max(
        [
            _safe_float(row.get(field)) or 0.0
            for row in confidence_rows
            if isinstance(row, dict)
            for field in ("baseline", "current")
        ]
        + [1.0]
    )
    y_max = max([_safe_float(row.get("value")) or 0.0 for row in entropy_rows if isinstance(row, dict)] + [reference_mean, current_mean, threshold, 0.1])
    y_min = min([_safe_float(row.get("value")) or 0.0 for row in entropy_rows if isinstance(row, dict)] + [reference_mean, current_mean, 0.0])
    y_pad = max((y_max - y_min) * 0.2, 0.05)

    payload["title"] = "불확실성 분포 변화로 본 annotation quality 드리프트"
    for area in (payload.get("layout") or {}).get("areas", []):
        area_name = area.get("area")
        if area_name == "main":
            area["description"] = (
                f"reference mean {reference_mean:.3f}에서 current mean {current_mean:.3f}로 "
                f"{mean_delta:+.3f} 변했다."
            )
        elif area_name == "side_top":
            area["description"] = f"KS statistic {score:.3f}, p-value {p_value:.3g}가 alpha {threshold:.3f} 이하이다."
        elif area_name == "side_bottom":
            area["description"] = f"calibration proxy는 {metric_label} 분포 이동 방향을 함께 보여준다."

    for component in payload.get("components", []):
        component_id = str(component.get("componentInstanceId", ""))
        config = component.get("config") or {}
        if component_id.endswith(".main.0"):
            config["x_min"] = 0
            config["x_max"] = 1
            config["x_ticks"] = _nice_ticks(0.0, 1.0, 6)
            config.pop("y_max", None)
            config.pop("y_ticks", None)
            config["x_axis_label"] = metric_label
            config["vertical_markers"] = [
                {
                    "x": round(reference_mean, 6),
                    "class": "mean-line",
                    "label": f"reference {reference_mean:.3f}",
                    "label_y": round(confidence_y_max * 0.9, 6),
                    "label_dx": 8,
                    "label_class": "callout",
                },
                {
                    "x": round(current_mean, 6),
                    "class": "threshold-line",
                    "label": f"current {current_mean:.3f}",
                    "label_y": round(confidence_y_max * 0.82, 6),
                    "label_dx": 8,
                    "label_class": "warning-text",
                },
            ]
            config["annotations"] = [
                {
                    "text": f"mean delta {mean_delta:+.3f}",
                    "x": round(max(reference_mean, current_mean), 6),
                    "y": round(confidence_y_max * 0.9, 6),
                    "class": "warning-text",
                }
            ]
        elif component_id.endswith(".side_top.0"):
            x_max = max([_safe_float(row.get("time")) or 0.0 for row in entropy_rows if isinstance(row, dict)] + [1.0])
            config["x_min"] = 1
            config["x_max"] = round(x_max, 6)
            config["x_ticks"] = _axis_ticks(x_max)
            config["y_min"] = round(max(0.0, y_min - y_pad), 6)
            config["y_max"] = round(min(1.0, y_max + y_pad), 6)
            config["y_ticks"] = _nice_ticks(config["y_min"], config["y_max"], 4)
            config["y_axis_label"] = False
            config["horizontal_markers"] = [
                {
                    "y": round(current_mean, 6),
                    "class": "threshold-line",
                    "label": f"current mean {current_mean:.3f}",
                    "label_x": 2,
                    "label_class": "warning-text",
                }
            ]
            config["point_highlights"] = [{"x": round(x_max, 6), "class": "entropy-point", "r": 4.7}]
            config["annotations"] = [
                {
                    "text": f"KS {score:.3f}, p {p_value:.3g}",
                    "x": max(1.0, x_max * 0.58),
                    "y": round(min(1.0, y_max), 6),
                    "class": "warning-text",
                }
            ]
        elif component_id.endswith(".side_bottom.0"):
            config["x_axis_label"] = "calibration proxy"
            for item in config.get("pixel_bars") or []:
                if isinstance(item, dict):
                    item["caption"] = "uncertainty summary"


def _apply_rep_layout_labels(payload: dict[str, Any]) -> None:
    data = payload.get("data") or {}
    metadata = payload.get("metadata") or {}
    metrics = metadata.get("metrics") if isinstance(metadata.get("metrics"), dict) else {}
    measurements = metrics.get("measurements") if isinstance(metrics.get("measurements"), dict) else {}
    score = (
        _safe_float(measurements.get("FEATURE_MAP_DRIFT_SCORE"))
        or _safe_float(measurements.get("GRAPH_EMBEDDING_DRIFT_SCORE"))
        or _safe_float(measurements.get("TEST_STATISTIC"))
        or _safe_float(metrics.get("testStatistic"))
        or _safe_float(metadata.get("score"))
        or 0.0
    )
    threshold = _safe_float(measurements.get("THRESHOLD")) or _safe_float(metrics.get("threshold")) or 0.1
    p_value = _safe_float(measurements.get("P_VALUE"))
    if p_value is None:
        p_value = _safe_float(metrics.get("pValue"))
    if p_value is None:
        p_value = 1.0
    sample = measurements.get("SAMPLE_SIZE") if isinstance(measurements.get("SAMPLE_SIZE"), dict) else {}
    reference_size = int(_safe_float(measurements.get("SAMPLE_SIZE_REFERENCE") or sample.get("reference")) or 0)
    current_size = int(_safe_float(measurements.get("SAMPLE_SIZE_CURRENT") or sample.get("current")) or 0)
    chart_id = str(payload.get("chartId") or "")
    projection_rows = data.get(f"chart.{chart_id}.projection") or []
    heatmap_rows = data.get(f"chart.{chart_id}.heatmap") or []
    distance_rows = data.get(f"chart.{chart_id}.distance") or []
    activation_rows = data.get(f"chart.{chart_id}.activation") or []
    top_feature = _rep_top_feature_from_note(data.get(f"chart.{chart_id}.notes") or [])

    if chart_id == "CHART-REP-003":
        payload["title"] = "Graph embedding MMD로 본 표현 공간 드리프트"
    else:
        payload["title"] = "Feature map MMD로 본 표현 공간 드리프트"

    for area in (payload.get("layout") or {}).get("areas", []):
        area_name = area.get("area")
        if area_name == "main":
            area["description"] = f"reference {reference_size}건과 current {current_size}건의 projection 분리를 score {score:.3f}로 요약한다."
        elif area_name == "side_top":
            area["description"] = f"{top_feature} 중심 변화와 score {score:.3f}를 heatmap으로 표시한다."
        elif area_name == "side_bottom":
            area["description"] = f"score {score:.3f}가 threshold {threshold:.3f}을 넘고 p-value는 {p_value:.3g}이다."

    x_values = [_safe_float(row.get("x")) for row in projection_rows if isinstance(row, dict)]
    y_values = [_safe_float(row.get("y")) for row in projection_rows if isinstance(row, dict)]
    x_values = [value for value in x_values if value is not None]
    y_values = [value for value in y_values if value is not None]
    x_min, x_max = _padded_extent(x_values, -1.0, 1.0)
    y_min, y_max = _padded_extent(y_values, -1.0, 1.0)
    max_activation = max([_safe_float(row.get("baseline")) or 0.0 for row in activation_rows if isinstance(row, dict)] + [_safe_float(row.get("current")) or 0.0 for row in activation_rows if isinstance(row, dict)] + [1.0])
    max_heat = max([_safe_float(value) or 0.0 for row in heatmap_rows if isinstance(row, dict) for value in (row.get("values") or [])] + [score, threshold, 1.0])
    max_distance = max([_safe_float(row.get("value")) or 0.0 for row in distance_rows if isinstance(row, dict)] + [score, threshold, 0.1])

    for component in payload.get("components", []):
        component_id = str(component.get("componentInstanceId", ""))
        config = component.get("config") or {}
        if component_id.endswith(".projection.0"):
            config["x_min"] = round(x_min, 6)
            config["x_max"] = round(x_max, 6)
            config["y_min"] = round(y_min, 6)
            config["y_max"] = round(y_max, 6)
            config["x_axis_label"] = "activation / embedding dimension 1"
            config["y_axis_label"] = "representation_shift / dimension 2"
            config["annotations"] = [
                {"text": f"score {score:.3f} > threshold {threshold:.3f}", "x": round(x_min + (x_max - x_min) * 0.55, 6), "y": round(y_max - (y_max - y_min) * 0.18, 6), "class": "warning-text"}
            ]
        elif component_id.endswith(".activation.0"):
            config["y_max"] = round(max_activation * 1.18, 6)
            config["y_ticks"] = _nice_ticks(0.0, max_activation * 1.18, 4)
            config["x_axis_label"] = "activation bins from CASE-016 data"
            config["annotations"] = [{"text": f"{top_feature} changed most", "x": 240, "y": 28, "class": "warning-text"}]
        elif component_id.endswith(".heatmap.0"):
            config["value_max"] = round(max_heat * 1.05, 6)
            config["x_axis_label"] = "runtime feature drift contribution"
        elif component_id.endswith(".distance.0"):
            x_max_distance = max([_safe_float(row.get("time")) or 0.0 for row in distance_rows if isinstance(row, dict)] + [1.0])
            config["x_min"] = 1
            config["x_max"] = round(x_max_distance, 6)
            config["x_ticks"] = _axis_ticks(x_max_distance)
            config["y_min"] = 0
            config["y_max"] = round(max_distance * 1.18, 6)
            config["y_ticks"] = _nice_ticks(0.0, max_distance * 1.18, 4)
            config["horizontal_markers"] = [{"y": round(threshold, 6), "class": "threshold-line", "label": f"threshold {threshold:.3f}"}]
            config["point_highlights"] = [{"x": round(x_max_distance, 6), "class": "distance-point", "r": 4.8}]
            config["annotations"] = [{"text": f"graph MMD {score:.3f}", "x": round(max(1.0, x_max_distance * 0.58), 6), "y": round(score, 6), "class": "warning-text"}]


def _rep_top_feature_from_note(note_rows: list[dict[str, Any]]) -> str:
    if not note_rows:
        return "representation"
    text = str((note_rows[0] if isinstance(note_rows[0], dict) else {}).get("text") or "")
    marker = "p-value "
    if marker in text and ". " in text:
        tail = text.split(". ", 1)[1]
        return tail.split(" mean changed", 1)[0] or "representation"
    return "representation"


def _padded_extent(values: list[float], default_min: float, default_max: float) -> tuple[float, float]:
    if not values:
        return default_min, default_max
    low = min(values)
    high = max(values)
    pad = max((high - low) * 0.12, 0.1)
    return low - pad, high + pad


def _event_axis_from_measurement(measurements: dict[str, Any], key: str, x_max: float) -> float | None:
    raw_index = _safe_float(measurements.get(key))
    processed_count = _safe_float(measurements.get("PROCESSED_COUNT"))
    if raw_index is None or processed_count is None or processed_count <= 0:
        return None
    scaled = 1.0 + (raw_index / processed_count) * (x_max - 1.0)
    return round(max(1.0, min(x_max, scaled)), 6)


def _event_markers(warning_x: float | None, drift_x: float | None) -> list[dict[str, Any]]:
    markers: list[dict[str, Any]] = []
    if warning_x is not None:
        markers.append({"x": warning_x, "class": "state-line", "opacity": 0.7})
    if drift_x is not None:
        markers.append({"x": drift_x, "class": "state-line"})
    return markers


def _axis_ticks(x_max: float) -> list[float]:
    if x_max <= 8:
        return _nice_ticks(1.0, x_max, 4)
    return [round(value, 6) for value in (1.0, x_max * 0.25, x_max * 0.5, x_max * 0.75, x_max)]


def _apply_stream004_layout_labels(payload: dict[str, Any]) -> None:
    data = payload.get("data") or {}
    stream_rows = data.get("stream") or []
    evidence_rows = data.get("evidence") or []
    timeline_rows = data.get("timeline") or []
    if not stream_rows and not evidence_rows:
        return
    metadata = payload.get("metadata") or {}
    metrics = metadata.get("metrics") if isinstance(metadata.get("metrics"), dict) else {}
    measurements = metrics.get("measurements") if isinstance(metrics.get("measurements"), dict) else {}
    reference_mean = _safe_float(measurements.get("REFERENCE_MEAN"))
    current_mean = _safe_float(measurements.get("CURRENT_MEAN"))
    mean_delta = _safe_float(measurements.get("MEAN_DELTA"))
    score = _safe_float(metadata.get("score")) or 0.0
    alarm_count = int(_safe_float(measurements.get("ALARM_COUNT")) or 0)
    stream_x_max = max([_safe_float(row.get("time")) or 0.0 for row in stream_rows if isinstance(row, dict)] + [36.0])
    stream_values = [_safe_float(row.get("value")) for row in stream_rows if isinstance(row, dict)]
    stream_values = [value for value in stream_values if value is not None]
    evidence_values = [
        value
        for row in evidence_rows
        if isinstance(row, dict)
        for value in (_safe_float(row.get("evidence")), _safe_float(row.get("bound")))
        if value is not None
    ]
    alarm_x_values = [
        _safe_float(row.get("time"))
        for row in evidence_rows
        if isinstance(row, dict) and row.get("pointClass") == "alarm-point"
    ]
    alarm_x_values = [value for value in alarm_x_values if value is not None]
    first_alarm_x = alarm_x_values[0] if alarm_x_values else None
    last_alarm_x = alarm_x_values[-1] if alarm_x_values else None
    stream_min = min(stream_values + ([reference_mean] if reference_mean is not None else []), default=0.0)
    stream_max = max(stream_values + ([current_mean] if current_mean is not None else []), default=1.0)
    stream_pad = max((stream_max - stream_min) * 0.15, 0.05)
    evidence_max = max(evidence_values + [0.1])
    evidence_y_max = evidence_max * 1.25

    payload["title"] = "SeqDrift 순차 경계 초과로 본 스트림 드리프트"
    for area in (payload.get("layout") or {}).get("areas", []):
        area_name = area.get("area")
        if area_name == "main":
            area["description"] = (
                f"reference mean {_format_number(reference_mean)}에서 current mean {_format_number(current_mean)}로 "
                f"{_format_signed_number(mean_delta)} 이동했다."
            )
        elif area_name == "side_top":
            area["description"] = (
                f"순차 evidence가 bound를 넘은 alarm {alarm_count}건을 표시한다. "
                f"마지막 score는 {score:.3f}이다."
            )
        elif area_name == "side_bottom":
            area["description"] = "reference/current 구간과 SeqDrift alarm 구간을 같은 time index 축에 정렬한다."

    for component in payload.get("components", []):
        component_id = str(component.get("componentInstanceId", ""))
        config = component.get("config") or {}
        if component_id.endswith(".main.0"):
            config["x_min"] = 1
            config["x_max"] = round(stream_x_max, 6)
            config["x_ticks"] = _axis_ticks(stream_x_max)
            config["y_min"] = round(stream_min - stream_pad, 6)
            config["y_max"] = round(stream_max + stream_pad, 6)
            config["y_ticks"] = _nice_ticks(stream_min - stream_pad, stream_max + stream_pad, 5)
            config["show_points"] = True
            config["horizontal_markers"] = []
            if reference_mean is not None:
                config["horizontal_markers"].append(
                    {
                        "y": round(reference_mean, 6),
                        "class": "mean-line",
                        "label": f"reference mean {reference_mean:.3f}",
                        "label_x": 3,
                        "label_class": "callout",
                    }
                )
            config["vertical_markers"] = _event_markers(None, first_alarm_x)
            config["point_highlights"] = [
                {"x": round(x_value, 6), "class": "alarm-point", "r": 6}
                for x_value in alarm_x_values
            ]
            config["annotations"] = [
                {
                    "text": f"mean delta {_format_signed_number(mean_delta)}",
                    "x": round(first_alarm_x or stream_x_max * 0.75, 6),
                    "y": round(stream_max, 6),
                    "class": "warning-text",
                }
            ]
        elif component_id.endswith(".side_top.0"):
            config["x_min"] = 1
            config["x_max"] = round(stream_x_max, 6)
            config["x_ticks"] = _axis_ticks(stream_x_max)
            config["y_min"] = 0
            config["y_max"] = round(evidence_y_max, 6)
            config["y_ticks"] = _nice_ticks(0.0, evidence_y_max, 4)
            config["point_highlights"] = [
                {"x": round(x_value, 6), "class": "alarm-point", "r": 5}
                for x_value in alarm_x_values
            ]
            config["annotations"] = [
                {
                    "text": "evidence >= bound",
                    "x": round(last_alarm_x or stream_x_max * 0.82, 6),
                    "y": round(evidence_y_max * 0.82, 6),
                    "class": "warning-text",
                }
            ]
        elif component_id.endswith(".side_bottom.0"):
            config["x_min"] = 1
            config["x_max"] = round(stream_x_max, 6)
            config["x_ticks"] = _axis_ticks(stream_x_max)
            config["markers"] = _event_markers(None, first_alarm_x)
            config["label_map"] = {
                "reference": "reference",
                "current": "current",
                "alarm": "alarm",
            }


def _format_signed_number(value: float | None) -> str:
    if value is None:
        return "n/a"
    return f"{value:+.3f}"


def _apply_mv002_layout_labels(payload: dict[str, Any]) -> None:
    data = payload.get("data") or {}
    embedding_rows = data.get("chart.CHART-MV-002.embedding") or []
    mmd_rows = data.get("chart.CHART-MV-002.mmd") or []
    if not embedding_rows and not mmd_rows:
        return
    reference = _row_by_group(embedding_rows, "reference")
    current = _row_by_group(embedding_rows, "current")
    score = _safe_float((mmd_rows[-1] if mmd_rows else {}).get("mmd"))
    if score is None:
        score = _safe_float(payload.get("metadata", {}).get("score"))
    threshold = _safe_float(_metadata_threshold(payload))
    comparison = "넘는다"
    if threshold is not None and score is not None and score < threshold:
        comparison = "보다 낮다"
    score_label = _format_number(score)
    threshold_label = _format_number(threshold)

    payload["title"] = "커널 MMD로 본 임베딩 분포 변화"
    for area in (payload.get("layout") or {}).get("areas", []):
        area_name = area.get("area")
        if area_name == "main":
            area["description"] = (
                f"기준 중심 {_format_point(reference)}에서 현재 중심 {_format_point(current)}로 "
                "이동한 방향을 읽는다."
            )
        elif area_name == "side_top":
            area["description"] = f"현재 window MMD {score_label}가 관리 기준 {threshold_label}을 {comparison}."
        elif area_name == "side_bottom":
            area["description"] = f"관측 MMD {score_label}와 기준 {threshold_label}의 차이를 함께 본다."
    _apply_mv002_component_config(payload, score or 0.0, threshold or 0.0)


def _apply_mv002_component_config(payload: dict[str, Any], score: float, threshold: float) -> None:
    y_max = max(score * 1.18, threshold * 1.6, 0.2)
    x_max = max(score * 1.15, threshold * 2.2, 0.22)
    for component in payload.get("components", []):
        component_id = str(component.get("componentInstanceId", ""))
        config = component.get("config") or {}
        if component_id.endswith(".mmd.0"):
            config["y_max"] = round(y_max, 6)
            config["y_ticks"] = _nice_ticks(0.0, y_max, 5)
            config["horizontal_markers"] = [
                {
                    "class": "threshold-line",
                    "y": round(threshold, 6),
                    "label": f"관리 기준 {threshold:.3f}",
                    "label_x": 7.2,
                    "label_dy": -6,
                    "label_class": "warning-text",
                }
            ]
        elif component_id.endswith(".null.0"):
            config["x_min"] = 0
            config["x_max"] = round(x_max, 6)
            config["x_ticks"] = _nice_ticks(0.0, x_max, 5)
            config.pop("y_max", None)
            config["vertical_markers"] = [
                {
                    "class": "observed-line",
                    "x": round(score, 6),
                    "label": f"observed {score:.3f}",
                    "label_y": 22,
                    "label_dx": -4,
                    "label_class": "warning-text",
                },
                {
                    "class": "threshold-line",
                    "x": round(threshold, 6),
                    "label": f"threshold {threshold:.3f}",
                    "label_y": 39,
                    "label_dx": -4,
                    "label_class": "warning-text",
                },
            ]


def _apply_anom001_layout_labels(payload: dict[str, Any]) -> None:
    data = payload.get("data") or {}
    summary_rows = data.get("chart.CHART-ANOM-001.summary") or []
    rate_rows = data.get("chart.CHART-ANOM-001.rate") or []
    score_rows = data.get("chart.CHART-ANOM-001.score") or []
    if not summary_rows and not rate_rows and not score_rows:
        return
    rate = _safe_float(_summary_value(summary_rows, "outlier rate"))
    threshold = _safe_float(_summary_value(summary_rows, "rate threshold"))
    if rate is None:
        rate = _safe_float((rate_rows[-1] if rate_rows else {}).get("rate"))
    if threshold is None:
        threshold = _safe_float(_metadata_threshold(payload))
    rate_label = _format_number(rate)
    threshold_label = _format_number(threshold)
    comparison = "넘는다"
    if rate is not None and threshold is not None and rate < threshold:
        comparison = "보다 낮다"
    outlier_count = _summary_display(summary_rows, "outlier count")

    payload["title"] = "정상 영역 밖 샘플 증가로 본 이상치 드리프트"
    for area in (payload.get("layout") or {}).get("areas", []):
        area_name = area.get("area")
        if area_name == "main":
            area["description"] = f"현재 score 분포에서 outlier rate {rate_label}가 기준 {threshold_label}을 {comparison}."
        elif area_name == "side_top":
            area["description"] = f"최근 window 이상 비율 {rate_label}가 관리 기준 {threshold_label}을 {comparison}."
        elif area_name == "side_bottom":
            area["description"] = f"현재 window에서 정상 영역 밖 샘플 {outlier_count or '0'}개가 분리되어 보인다."
    _apply_anom001_component_config(payload, rate or 0.0, threshold or 0.0)


def _apply_anom001_component_config(payload: dict[str, Any], rate: float, threshold: float) -> None:
    score_threshold = _safe_float(_path(payload, "$.metadata.metrics.measurements.THRESHOLD", None)) or 0.0
    max_score = _safe_float(_path(payload, "$.metadata.metrics.measurements.MAX_ANOMALY_SCORE", None)) or score_threshold
    score_x_max = max(max_score * 1.12, score_threshold * 1.25, 1.0)
    rate_y_max = max(rate * 1.3, threshold * 1.6, 0.2)
    for component in payload.get("components", []):
        component_id = str(component.get("componentInstanceId", ""))
        config = component.get("config") or {}
        if component_id.endswith(".score.0"):
            config["x_min"] = 0
            config["x_max"] = round(score_x_max, 6)
            config["x_ticks"] = _nice_ticks(0.0, score_x_max, 5)
            config.pop("y_max", None)
            config.pop("y_ticks", None)
            config["vertical_markers"] = [
                {
                    "class": "threshold-line",
                    "x": round(score_threshold, 6),
                    "label": f"score threshold {score_threshold:.3f}",
                    "label_y": 0.72,
                    "label_class": "warning-text",
                }
            ]
            config["annotations"] = [
                {
                    "text": f"outlier rate {rate:.3f}",
                    "x": round(score_threshold * 0.58, 6),
                    "y": 0.82,
                    "class": "warning-text",
                }
            ]
        elif component_id.endswith(".rate.0"):
            config["y_max"] = round(rate_y_max, 6)
            config["y_ticks"] = _nice_ticks(0.0, rate_y_max, 4)
            config["horizontal_markers"] = [
                {
                    "class": "threshold-line",
                    "y": round(threshold, 6),
                    "label": f"rate threshold {threshold:.3f}",
                    "label_x": 4,
                    "label_dy": -7,
                    "label_class": "warning-text",
                }
            ]


def _nice_ticks(start: float, stop: float, count: int) -> list[float]:
    if count <= 1:
        return [round(start, 6)]
    return [round(start + ((stop - start) * index / (count - 1)), 6) for index in range(count)]


def _row_by_group(rows: list[dict[str, Any]], group: str) -> dict[str, Any]:
    for row in rows:
        if isinstance(row, dict) and row.get("group") == group:
            return row
    return {}


def _format_point(row: dict[str, Any]) -> str:
    x = _safe_float(row.get("x"))
    y = _safe_float(row.get("y"))
    if x is None or y is None:
        return "(n/a, n/a)"
    return f"({x:.2f}, {y:.2f})"


class _Missing:
    pass


_MISSING = _Missing()


def _path(root: dict[str, Any], expression: str, default: Any = _MISSING) -> Any:
    if expression.startswith("$."):
        parts = expression[2:].split(".")
    elif expression.startswith("@."):
        parts = expression[2:].split(".")
    else:
        raise PayloadBindingError(f"unsupported path expression: {expression}")
    current: Any = root
    for part in parts:
        if isinstance(current, dict) and part in current:
            current = current[part]
        else:
            if default is not _MISSING:
                return default
            raise PayloadBindingError(f"path not found: {expression}")
    return current
