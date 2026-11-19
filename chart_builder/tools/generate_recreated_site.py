from __future__ import annotations

import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DRIFT_ROOT = ROOT.parent / "drift 보고서"
DRIFT_CHARTS = DRIFT_ROOT / "charts"
COMPONENT_MAP = ROOT / "docs" / "chart_component_to_chart.csv"
OUT_DIR = ROOT / "web"
SAVED_LAYOUTS_PATH = ROOT / "builder_layouts.json"
SAVED_CHARTS_PATH = ROOT / "builder_charts.json"


DEFAULT_AREAS = [
    {"area": "summary", "role": "summary", "x": 0, "y": 0, "w": 12, "h": 1},
    {"area": "main", "role": "primary_visual", "x": 0, "y": 1, "w": 8, "h": 5},
    {"area": "side_top", "role": "secondary_visual", "x": 8, "y": 1, "w": 4, "h": 2},
    {"area": "side_bottom", "role": "secondary_visual", "x": 8, "y": 3, "w": 4, "h": 3},
    {"area": "notes", "role": "interpretation", "x": 0, "y": 6, "w": 12, "h": 2},
]

AREAS_BY_INDEX = ["main", "side_top", "side_bottom", "summary", "notes"]

OVERLAY_COMPONENTS = {"threshold_line", "event_marker", "annotation_callout", "uncertainty_band"}

LINE_COMPONENTS = {
    "trend_line",
    "raw_signal_trend",
    "detector_statistic_view",
    "distance_metric_view",
    "performance_metric_view",
    "control_chart",
    "cumulative_curve",
    "model_diagnostic_curve",
    "adaptive_model_structure_view",
}

BAR_COMPONENTS = {
    "bar_chart",
    "ranking_view",
    "contribution_view",
    "proportion_view",
    "reference_current_comparison",
    "p_value_view",
}

MATRIX_COMPONENTS = {"heatmap", "matrix_view"}
TABLE_COMPONENTS = {"comparison_table"}
SCATTER_COMPONENTS = {"projection_scatter"}
TIMELINE_COMPONENTS = {"state_timeline", "window_view"}
SUMMARY_COMPONENTS = {"decision_card", "domain_specific_visual"}
DISTRIBUTION_COMPONENTS = {"distribution_view", "histogram_view", "distribution_summary_plot", "quantile_view"}


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def chart_id_from_html(path: Path, html: str) -> str:
    match = re.search(r'aria-label="(CHART-[A-Z0-9-]+)"', html)
    if match:
        return match.group(1)
    return path.stem.upper().replace("CHART_", "CHART-").replace("_", "-")


def title_from_html(html: str, chart_id: str) -> str:
    match = re.search(r"<title>(.*?)</title>", html, re.S)
    if not match:
        return chart_id
    title = re.sub(r"\s+", " ", match.group(1)).strip()
    return title


def component_mapping() -> dict[str, list[str]]:
    mapping: dict[str, list[str]] = {}
    with COMPONENT_MAP.open("r", encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            mapping.setdefault(row["chart"], []).append(row["component"])
    return mapping


def read_json_list(path: Path) -> list[dict[str, object]]:
    if not path.exists():
        return []
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return []
    return value if isinstance(value, list) else []


def saved_layouts() -> list[dict[str, object]]:
    layouts: list[dict[str, object]] = []
    for item in read_json_list(SAVED_LAYOUTS_PATH):
        layout = item.get("layout")
        if isinstance(layout, dict) and isinstance(layout.get("areas"), list):
            layouts.append(layout)
    return layouts


def saved_chart_blueprints() -> list[dict[str, object]]:
    blueprints: list[dict[str, object]] = []
    for item in read_json_list(SAVED_CHARTS_PATH):
        payload = item.get("payload")
        if not isinstance(payload, dict):
            continue
        layout = payload.get("layout")
        components = payload.get("components")
        if isinstance(layout, dict) and isinstance(layout.get("areas"), list) and isinstance(components, list):
            blueprints.append(payload)
    return blueprints


def exact_saved_chart_payload(chart_id: str, title: str, html_file: str, blueprints: list[dict[str, object]]) -> dict[str, object] | None:
    for blueprint in blueprints:
        if blueprint.get("chartId") != chart_id:
            continue
        payload = clone_json(blueprint)
        payload["chartId"] = chart_id
        payload.setdefault("title", title)
        payload["originalPath"] = f"./drift_report_charts/{html_file}"
        payload["reproduction"] = {
            "status": "designed",
            "issues": [
                "Builder에서 저장된 chart payload를 그대로 사용했다.",
                "layout, component area, data는 generator가 재조합하지 않았다.",
            ],
        }
        return payload
    return None


def choose_blueprint(components: list[str], blueprints: list[dict[str, object]]) -> dict[str, object] | None:
    if not blueprints:
        return None
    component_set = set(components)

    def score(blueprint: dict[str, object]) -> tuple[int, int]:
        placed = blueprint.get("components", [])
        placed_types = {
            str(item.get("componentType"))
            for item in placed
            if isinstance(item, dict) and item.get("componentType")
        }
        return (len(component_set & placed_types), len(placed_types))

    return max(blueprints, key=score)


def default_layout(saved: list[dict[str, object]]) -> dict[str, object]:
    if saved:
        return clone_json(saved[0])
    return {
        "layoutType": "semantic_grid",
        "presetCode": "default_3_panel",
        "columns": 12,
        "rows": 8,
        "areas": DEFAULT_AREAS,
    }


def clone_json(value: object) -> object:
    return json.loads(json.dumps(value, ensure_ascii=False))


def layout_area_order(layout: dict[str, object]) -> list[str]:
    areas = [area for area in layout.get("areas", []) if isinstance(area, dict)]
    sorted_areas = sorted(
        areas,
        key=lambda area: (
            0 if area.get("role") == "primary_visual" or area.get("area") == "main" else 1,
            int(area.get("y", 0)),
            int(area.get("x", 0)),
        ),
    )
    return [str(area.get("area")) for area in sorted_areas if area.get("area")]


def primary_area(layout: dict[str, object]) -> str:
    for area in layout.get("areas", []):
        if isinstance(area, dict) and (area.get("role") == "primary_visual" or area.get("area") == "main"):
            return str(area.get("area"))
    order = layout_area_order(layout)
    return order[0] if order else "main"


def component_area_preferences(blueprint: dict[str, object] | None) -> dict[str, str]:
    if not blueprint:
        return {}
    preferences: dict[str, str] = {}
    for item in blueprint.get("components", []):
        if not isinstance(item, dict):
            continue
        component_type = item.get("componentType")
        area = item.get("area")
        if component_type and area:
            preferences.setdefault(str(component_type), str(area))
    return preferences


def extract_const_literals(js: str) -> dict[str, object]:
    values: dict[str, object] = {}
    pattern = re.compile(r"\bconst\s+([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(\[[\s\S]*?\]|\{[\s\S]*?\}|-?\d+(?:\.\d+)?|'[^']*'|\"[^\"]*\")\s*;", re.M)
    for name, literal in pattern.findall(js):
        parsed = parse_js_literal(literal)
        if parsed is not None:
            values[name] = parsed
    return values


def parse_js_literal(literal: str) -> object | None:
    text = literal.strip()
    if re.fullmatch(r"-?\d+(?:\.\d+)?", text):
        return float(text) if "." in text else int(text)
    if (text.startswith("'") and text.endswith("'")) or (text.startswith('"') and text.endswith('"')):
        return text[1:-1]
    try:
        normalized = re.sub(r"(?<![\"'])\b([A-Za-z_][A-Za-z0-9_]*)\s*:", r'"\1":', text)
        normalized = normalized.replace("'", '"')
        return json.loads(normalized)
    except Exception:
        return None


def numeric_arrays(constants: dict[str, object]) -> list[tuple[str, list[float]]]:
    arrays: list[tuple[str, list[float]]] = []
    for name, value in constants.items():
        if isinstance(value, list) and value and all(isinstance(item, (int, float)) for item in value):
            arrays.append((name, [float(item) for item in value]))
    return arrays


def object_arrays(constants: dict[str, object]) -> list[tuple[str, list[dict[str, object]]]]:
    arrays: list[tuple[str, list[dict[str, object]]]] = []
    for name, value in constants.items():
        if isinstance(value, list) and value and all(isinstance(item, dict) for item in value):
            arrays.append((name, value))
    return arrays


def synthetic_rows(chart_id: str) -> list[dict[str, object]]:
    seed = sum(ord(ch) for ch in chart_id) % 17
    return [
        {"time": index + 1, "value": round(0.25 + index * 0.035 + ((seed + index) % 5) * 0.018, 3)}
        for index in range(12)
    ]


def rows_from_numeric_array(values: list[float], field: str = "value") -> list[dict[str, object]]:
    return [{"time": index + 1, field: value} for index, value in enumerate(values)]


def component_data(component: str, chart_id: str, constants: dict[str, object], data_index: int) -> tuple[list[dict[str, object]], dict[str, object], dict[str, object], list[str]]:
    issues: list[str] = []
    num_arrays = numeric_arrays(constants)
    obj_arrays = object_arrays(constants)
    selected_num = num_arrays[data_index % len(num_arrays)] if num_arrays else None
    selected_obj = obj_arrays[data_index % len(obj_arrays)] if obj_arrays else None

    if selected_obj and component not in LINE_COMPONENTS:
        rows = selected_obj[1]
    elif selected_num:
        rows = rows_from_numeric_array(selected_num[1])
    else:
        rows = synthetic_rows(chart_id)
        issues.append("원본 JS에서 component에 직접 연결할 수 있는 독립 데이터 배열을 자동 추출하지 못해 deterministic sample data로 대체함.")

    config: dict[str, object] = {}
    binding: dict[str, object] = {"source": f"chart.{chart_id}.{component}.{data_index}"}

    if component in LINE_COMPONENTS:
        config.update({"time_field": "time", "x_field": "time", "value_field": "value", "y_field": "value", "statistic_field": "value", "show_points": True})
        binding.update(config)
    elif component in BAR_COMPONENTS:
        rows = to_category_rows(rows, chart_id)
        config.update({"category_field": "category", "value_field": "value", "sort_order": "value_desc"})
        binding.update(config)
    elif component in MATRIX_COMPONENTS:
        rows = to_matrix_rows(rows)
        config.update({"x_field": "column", "y_field": "row", "row_field": "row", "column_field": "column", "value_field": "value", "cell_value_field": "value"})
        binding.update(config)
    elif component in SCATTER_COMPONENTS:
        rows = to_scatter_rows(rows)
        config.update({"x_field": "x", "y_field": "y", "group_field": "group"})
        binding.update(config)
    elif component in TIMELINE_COMPONENTS:
        rows = to_window_or_state_rows(rows, component)
        if component == "window_view":
            config.update({"window_id_field": "window", "start_field": "start", "end_field": "end", "window_role_field": "role"})
        else:
            config.update({"time_field": "time", "state_field": "state"})
        binding.update(config)
    elif component in DISTRIBUTION_COMPONENTS:
        rows = to_distribution_rows(rows)
        if component == "quantile_view":
            config.update({"quantile_field": "quantile", "value_field": "value", "target_line": 0})
        elif component == "histogram_view":
            config.update({"bin_field": "bin", "count_field": "value", "series_field": "group"})
        else:
            config.update({"value_field": "value", "group_field": "group", "bin_count": 12})
        binding.update(config)
    elif component in TABLE_COMPONENTS:
        rows = to_table_rows(rows)
        config.update({"row_field": "metric", "reference_field": "reference", "current_field": "current"})
        binding.update(config)
    elif component == "threshold_line":
        threshold = first_number(constants, default=0.68)
        rows = [{"threshold": threshold}]
        config.update({"threshold_value": threshold, "label": "threshold"})
        binding.update({"threshold_value": "threshold"})
    elif component == "event_marker":
        rows = [{"time": 4, "event_type": "marker", "label": "event"}, {"time": 8, "event_type": "alarm", "label": "alarm"}]
        config.update({"time_field": "time", "event_type_field": "event_type", "label_field": "label"})
        binding.update(config)
    elif component == "uncertainty_band":
        rows = to_uncertainty_rows(rows)
        config.update({"time_field": "time", "lower_field": "lower", "upper_field": "upper", "center_field": "center"})
        binding.update(config)
    else:
        rows = [{"label": component, "value": 1}]
        config.update({"label_field": "label", "primary_metric_field": "value", "visual_code": component, "fallback_component": "domain_specific_visual"})
        binding.update(config)

    return rows, config, binding, issues


def to_category_rows(rows: list[dict[str, object]], chart_id: str) -> list[dict[str, object]]:
    out = []
    for index, row in enumerate(rows[:8]):
        value = first_numeric_value(row, default=(index + 1) / 10)
        out.append({"category": f"item {index + 1}", "value": value})
    return out or [{"category": chart_id, "value": 1}]


def to_matrix_rows(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    source = rows[:9] or synthetic_rows("matrix")
    out = []
    for index, row in enumerate(source):
        out.append({"row": f"r{index // 3 + 1}", "column": f"c{index % 3 + 1}", "value": first_numeric_value(row, default=(index % 4) / 3)})
    return out


def to_scatter_rows(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    out = []
    for index, row in enumerate(rows[:32]):
        value = first_numeric_value(row, default=index / 10)
        out.append({"x": round((index % 8) * 0.18 + value * 0.05, 3), "y": round((index // 8) * 0.22 + value * 0.08, 3), "group": "current" if index % 2 else "reference"})
    return out


def to_window_or_state_rows(rows: list[dict[str, object]], component: str) -> list[dict[str, object]]:
    if component == "window_view":
        return [
            {"window": "reference", "start": 1, "end": 4, "role": "reference"},
            {"window": "current", "start": 5, "end": 8, "role": "current"},
            {"window": "alarm", "start": 8, "end": 10, "role": "warning"},
        ]
    states = ["normal", "normal", "warning", "warning", "drift", "drift"]
    return [{"time": index + 1, "state": states[index % len(states)]} for index in range(max(6, min(12, len(rows) or 8)))]


def to_distribution_rows(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    out = []
    for index, row in enumerate(rows[:30]):
        value = first_numeric_value(row, default=index / 30)
        out.append({"group": "current" if index % 2 else "reference", "value": value, "bin": f"b{index % 8 + 1}", "quantile": f"q{index * 5:02d}"})
    return out or [{"group": "reference", "value": 0.3}, {"group": "current", "value": 0.6}]


def to_table_rows(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    out = []
    for index, row in enumerate(rows[:5]):
        value = first_numeric_value(row, default=index / 10)
        out.append({"metric": f"metric {index + 1}", "reference": round(value * 0.85, 3), "current": round(value, 3)})
    return out


def to_uncertainty_rows(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    out = []
    for index, row in enumerate(rows[:12]):
        center = first_numeric_value(row, default=0.4 + index * 0.03)
        out.append({"time": index + 1, "lower": round(center - 0.08, 3), "center": center, "upper": round(center + 0.08, 3)})
    return out


def first_numeric_value(row: dict[str, object], default: float = 0.0) -> float:
    for value in row.values():
        if isinstance(value, (int, float)):
            return float(value)
    return default


def first_number(constants: dict[str, object], default: float) -> float:
    for value in constants.values():
        if isinstance(value, (int, float)):
            return float(value)
    return default


def adapt_001_payload(chart_id: str, title: str, html_file: str, constants: dict[str, object]) -> dict[str, object] | None:
    required = ["accuracy", "mainSize", "altSize", "warningIndex", "alternateIndex", "replaceIndex"]
    if chart_id != "CHART-ADAPT-001" or any(name not in constants for name in required):
        return None

    accuracy = constants["accuracy"]
    main_size = constants["mainSize"]
    alt_size = constants["altSize"]
    warning_index = int(constants["warningIndex"])
    alternate_index = int(constants["alternateIndex"])
    replace_index = int(constants["replaceIndex"])
    if not all(isinstance(values, list) for values in [accuracy, main_size, alt_size]):
        return None

    layout = {
        "layoutType": "semantic_grid",
        "presetCode": "source_adapt_001",
        "displayName": "CHART-ADAPT-001 source layout",
        "columns": 12,
        "rows": 8,
        "areas": [
            {"area": "summary", "role": "summary", "x": 0, "y": 0, "w": 12, "h": 1},
            {"area": "main", "role": "primary_visual", "x": 0, "y": 1, "w": 7, "h": 5},
            {"area": "side_top", "role": "secondary_visual", "x": 7, "y": 1, "w": 5, "h": 2},
            {"area": "side_bottom", "role": "secondary_visual", "x": 7, "y": 3, "w": 5, "h": 3},
            {"area": "notes", "role": "interpretation", "x": 0, "y": 6, "w": 12, "h": 2},
        ],
    }
    accuracy_rows = [{"time": index + 1, "value": float(value)} for index, value in enumerate(accuracy)]
    tree_rows = [
        {"time": index + 1, "value": float(main), "secondary_value": float(alt)}
        for index, (main, alt) in enumerate(zip(main_size, alt_size))
    ]
    state_rows = [
        {"window": "normal", "start": 1, "end": warning_index, "role": "normal"},
        {"window": "warn", "start": warning_index, "end": alternate_index, "role": "warning"},
        {"window": "alternate", "start": alternate_index, "end": replace_index, "role": "alternate"},
        {"window": "replace", "start": replace_index, "end": len(accuracy), "role": "replace"},
    ]
    summary_rows = [
        {"label": "accuracy min", "value": min(float(value) for value in accuracy)},
        {"label": "replacement", "value": replace_index},
        {"label": "alt nodes", "value": max(float(value) for value in alt_size)},
    ]
    events = [
        {"time": warning_index, "event_type": "warning", "label": "warning"},
        {"time": alternate_index, "event_type": "alternate", "label": "alternate"},
        {"time": replace_index, "event_type": "replacement", "label": "replace"},
    ]
    data = {
        f"chart.{chart_id}.summary": summary_rows,
        f"chart.{chart_id}.accuracy": accuracy_rows,
        f"chart.{chart_id}.states": state_rows,
        f"chart.{chart_id}.tree_size": tree_rows,
        f"chart.{chart_id}.events": events,
    }
    components = [
        {
            "componentInstanceId": f"{chart_id}.summary.0",
            "componentType": "decision_card",
            "area": "summary",
            "isOverlay": False,
            "zIndex": 10,
            "config": {"label_field": "label", "primary_metric_field": "value", "visual_code": "summary_metrics"},
            "dataBinding": {"source": f"chart.{chart_id}.summary", "label_field": "label", "primary_metric_field": "value"},
        },
        {
            "componentInstanceId": f"{chart_id}.accuracy.0",
            "componentType": "performance_metric_view",
            "area": "main",
            "isOverlay": False,
            "zIndex": 10,
            "config": {"time_field": "time", "value_field": "value", "y_min": 0.68, "y_max": 0.94, "label": "online accuracy"},
            "dataBinding": {"source": f"chart.{chart_id}.accuracy", "time_field": "time", "value_field": "value"},
        },
        {
            "componentInstanceId": f"{chart_id}.events.0",
            "componentType": "event_marker",
            "area": "main",
            "isOverlay": True,
            "zIndex": 20,
            "config": {"time_field": "time", "event_type_field": "event_type", "label_field": "label", "x_min": 1, "x_max": len(accuracy)},
            "dataBinding": {"source": f"chart.{chart_id}.events", "time_field": "time", "event_type_field": "event_type", "label_field": "label"},
        },
        {
            "componentInstanceId": f"{chart_id}.states.0",
            "componentType": "state_timeline",
            "area": "side_top",
            "isOverlay": False,
            "zIndex": 10,
            "config": {"window_id_field": "window", "start_field": "start", "end_field": "end", "window_role_field": "role"},
            "dataBinding": {"source": f"chart.{chart_id}.states", "window_id_field": "window", "start_field": "start", "end_field": "end", "window_role_field": "role"},
        },
        {
            "componentInstanceId": f"{chart_id}.tree_size.0",
            "componentType": "adaptive_model_structure_view",
            "area": "side_bottom",
            "isOverlay": False,
            "zIndex": 10,
            "config": {"time_field": "time", "value_field": "value", "secondary_value_field": "secondary_value", "y_min": 0, "y_max": 70, "label": "main / alternate tree size"},
            "dataBinding": {"source": f"chart.{chart_id}.tree_size", "time_field": "time", "value_field": "value", "secondary_value_field": "secondary_value"},
        },
        {
            "componentInstanceId": f"{chart_id}.notes.0",
            "componentType": "domain_specific_visual",
            "area": "notes",
            "isOverlay": False,
            "zIndex": 10,
            "config": {"label": "HAT replacement restores accuracy after alternate tree growth.", "visual_code": "interpretation"},
            "dataBinding": {"source": f"chart.{chart_id}.summary"},
        },
    ]
    return {
        "chartId": chart_id,
        "title": title,
        "originalPath": f"./drift_report_charts/{html_file}",
        "layout": layout,
        "components": components,
        "data": data,
        "reproduction": {
            "status": "targeted",
            "issues": [
                "CHART-ADAPT-001은 원본 HTML/CSS/JS 구조를 기준으로 chart-specific payload를 생성했다.",
                "원본 panel 설명문과 하단 긴 해석 문단은 component payload가 아니라 notes component의 요약으로 대체했다.",
            ],
        },
    }


def build_payload(
    chart_id: str,
    title: str,
    html_file: str,
    constants: dict[str, object],
    components: list[str],
    layout: dict[str, object],
    blueprint: dict[str, object] | None,
) -> dict[str, object]:
    issues = [
        "원본 차트는 JS draw 함수가 SVG 요소를 직접 배치하는 imperative 구현이다. component payload로 자동 변환 가능한 데이터/배치만 재현했다.",
        "원본의 세부 axis tick, callout 위치, panel 설명문, CSS 미세 배치는 자동 추출 대상이 아니므로 원본 iframe과 대조가 필요하다.",
    ]
    layout_name = layout.get("displayName") or layout.get("presetCode") or "saved layout"
    issues.append(f"저장된 layout 결과를 사용했다: {layout_name}.")
    if blueprint:
        issues.append(f"저장된 chart component 배치 결과를 blueprint로 사용했다: {blueprint.get('chartId', 'saved chart')}.")
    else:
        issues.append("저장된 chart component 배치 결과가 없어 layout area 순서대로 component를 배치했다.")
    if not constants:
        issues.append("원본 JS 상수 추출 결과가 비어 있어 일부 component data는 대체 sample data를 사용했다.")

    data_sources: dict[str, list[dict[str, object]]] = {}
    instances = []
    base_index = 0
    layout = clone_json(layout)
    area_order = layout_area_order(layout)
    valid_areas = set(area_order)
    fallback_area = primary_area(layout)
    preferences = component_area_preferences(blueprint)
    area_use_counts = {area: 0 for area in area_order}
    for index, component in enumerate(components[:7]):
        is_overlay = component in OVERLAY_COMPONENTS
        if not is_overlay and area_order and sum(area_use_counts.values()) >= len(area_order):
            issues.append(f"저장 layout area 수({len(area_order)})보다 non-overlay component가 많아 {component}는 화면에 배치하지 않았다.")
            continue
        rows, config, binding, component_issues = component_data(component, chart_id, constants, index)
        data_sources[str(binding["source"])] = rows
        issues.extend(component_issues)
        preferred_area = preferences.get(component)
        if preferred_area and preferred_area in valid_areas and (is_overlay or area_use_counts.get(preferred_area, 0) == 0):
            area = preferred_area
        elif is_overlay:
            area = fallback_area
        else:
            if preferred_area and preferred_area not in valid_areas:
                issues.append(f"저장 chart는 {component}를 현재 layout에 없는 '{preferred_area}' area에 배치해서 area 순서대로 재배치했다.")
            elif preferred_area and area_use_counts.get(preferred_area, 0) > 0:
                issues.append(f"저장 chart의 '{preferred_area}' area가 이미 사용 중이라 {component}를 가장 빈 area로 재배치했다.")
            if area_order:
                area = min(area_order, key=lambda name: (area_use_counts.get(name, 0), area_order.index(name)))
            else:
                area = fallback_area
            base_index += 1
            if component not in preferences:
                issues.append(f"{component}에 대한 저장 배치가 없어 '{area}' area에 자동 배치했다.")
        if not is_overlay:
            area_use_counts[area] = area_use_counts.get(area, 0) + 1
        instances.append({
            "componentInstanceId": f"{chart_id}.{component}.{index}",
            "componentType": component,
            "area": area,
            "isOverlay": is_overlay,
            "zIndex": 20 + index if is_overlay else 10 + index,
            "config": config,
            "dataBinding": binding,
        })

    return {
        "chartId": chart_id,
        "title": title,
        "originalPath": f"./drift_report_charts/{html_file}",
        "layout": layout,
        "components": instances,
        "data": data_sources,
        "reproduction": {
            "status": "partial",
            "issues": sorted(set(issues)),
        },
    }


def main() -> None:
    mapping = component_mapping()
    layouts = saved_layouts()
    blueprints = saved_chart_blueprints()
    payloads = []
    for html_path in sorted(DRIFT_CHARTS.glob("chart_*.html")):
        html = read_text(html_path)
        chart_id = chart_id_from_html(html_path, html)
        title = title_from_html(html, chart_id)
        js_path = html_path.with_suffix(".js")
        constants = extract_const_literals(read_text(js_path)) if js_path.exists() else {}
        exact_saved = exact_saved_chart_payload(chart_id, title, html_path.name, blueprints)
        if exact_saved:
            payloads.append(exact_saved)
            continue
        targeted = adapt_001_payload(chart_id, title, html_path.name, constants)
        if targeted:
            payloads.append(targeted)
            continue
        components = mapping.get(chart_id, ["domain_specific_visual"])
        blueprint = choose_blueprint(components, blueprints)
        layout = clone_json(blueprint["layout"]) if blueprint else default_layout(layouts)
        payloads.append(build_payload(chart_id, title, html_path.name, constants, components, layout, blueprint))

    write_payloads(payloads)
    write_site_files(payloads)
    print(f"generated {len(payloads)} recreated chart payloads")


def write_payloads(payloads: list[dict[str, object]]) -> None:
    target = OUT_DIR / "recreated_chart_payloads.js"
    target.write_text(
        "window.RECREATED_CHART_PAYLOADS = "
        + json.dumps(payloads, ensure_ascii=False, indent=2)
        + ";\n",
        encoding="utf-8",
    )


def write_site_files(payloads: list[dict[str, object]]) -> None:
    # Static renderer files are maintained in ../chart_runtime/.
    # The generator owns recreated_chart_payloads.js and per-chart generated
    # wrappers. Builder and generated pages keep using the same chart runtime
    # rendering engine.
    for payload in payloads:
        reproduction = payload.get("reproduction", {})
        if not isinstance(reproduction, dict) or reproduction.get("status") != "designed":
            continue
        chart_id = str(payload.get("chartId", ""))
        if not chart_id:
            continue
        target = OUT_DIR / f"{chart_id.lower().replace('-', '_')}_generated.html"
        target.write_text(single_chart_html(chart_id), encoding="utf-8")


def single_chart_html(chart_id: str) -> str:
    return f"""<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Generated {chart_id}</title>
  <link rel="stylesheet" href="../../chart_runtime/chart_runtime.css">
  <link rel="stylesheet" href="./generated_chart_page.css">
</head>
<body>
  <main class="site single-chart source-compare">
    <aside class="sidebar" aria-hidden="true">
      <input id="searchInput" type="search" autocomplete="off">
      <div id="chartList" class="chart-list"></div>
    </aside>
    <section class="workspace">
      <header class="workspace-head">
        <div>
          <p id="chartStatus" class="eyebrow">generated chart</p>
          <h2 id="chartTitle">{chart_id}</h2>
        </div>
        <button id="originalLink" class="open-link" type="button">원본 보기</button>
      </header>
      <section class="recreated-pane">
        <h3>Generated Chart</h3>
        <div id="componentChart" class="component-chart"></div>
      </section>
      <section class="issues" hidden>
        <h3>Generation Notes</h3>
        <ul id="issueList"></ul>
      </section>
    </section>
  </main>
  <script src="./recreated_chart_payloads.js"></script>
  <script>
    window.RECREATED_CHART_PAYLOADS = (window.RECREATED_CHART_PAYLOADS || []).filter(
      (payload) => payload.chartId === "{chart_id}"
    ).map((payload) => ({{
      ...payload,
      reproduction: {{ ...payload.reproduction, issues: [] }}
    }}));
  </script>
  <script src="../../chart_runtime/chart_runtime.js"></script>
  <script src="./recreated_charts.js"></script>
</body>
</html>
"""


RECREATED_HTML = """<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Component Recreated Drift Charts</title>
  <link rel="stylesheet" href="../../chart_runtime/chart_runtime.css">
</head>
<body>
  <main class="site">
    <aside class="sidebar">
      <header>
        <p class="eyebrow">Drift Chart Components</p>
        <h1>Recreated Charts</h1>
      </header>
      <input id="searchInput" type="search" placeholder="CHART-CTRL-002, component..." autocomplete="off">
      <div id="chartList" class="chart-list"></div>
    </aside>
    <section class="workspace">
      <header class="workspace-head">
        <div>
          <p id="chartStatus" class="eyebrow">partial reproduction</p>
          <h2 id="chartTitle"></h2>
        </div>
        <button id="originalLink" class="open-link" type="button">원본 보기</button>
      </header>
      <section class="recreated-pane">
        <h3>Component Recreated</h3>
        <div id="componentChart" class="component-chart"></div>
      </section>
      <section class="issues">
        <h3>Reproduction Notes</h3>
        <ul id="issueList"></ul>
      </section>
    </section>
  </main>
  <script src="./recreated_chart_payloads.js"></script>
  <script src="../../chart_runtime/chart_runtime.js"></script>
  <script src="./recreated_charts.js"></script>
</body>
</html>
"""


RECREATED_CSS = """:root {
  --bg: #f4f6f7;
  --panel: #ffffff;
  --ink: #17212b;
  --muted: #64707d;
  --line: #d7dde4;
  --active: #2f6f9f;
  --active-bg: #e7f1f8;
  --warning: #c47d1f;
  --danger: #b84444;
  --ok: #247b63;
}
* { box-sizing: border-box; }
html, body { height: 100%; margin: 0; overflow: hidden; }
body { background: var(--bg); color: var(--ink); font-family: "Segoe UI", "Malgun Gothic", Arial, sans-serif; }
button, input { font: inherit; }
.site { display: grid; grid-template-columns: 320px minmax(0, 1fr); height: 100vh; height: 100dvh; max-height: 100vh; max-height: 100dvh; min-height: 0; overflow: hidden; }
.sidebar { display: grid; grid-template-rows: auto auto minmax(0, 1fr); gap: 14px; min-width: 0; min-height: 0; padding: 18px; border-right: 1px solid var(--line); background: var(--panel); overflow: hidden; }
.sidebar h1, .workspace-head h2, .recreated-pane h3, .issues h3 { margin: 0; }
.eyebrow { margin: 0 0 5px; color: var(--muted); font-size: 12px; font-weight: 850; }
#searchInput { height: 36px; padding: 0 11px; border: 1px solid var(--line); border-radius: 7px; }
.chart-list { display: grid; align-content: start; gap: 7px; min-height: 0; overflow: auto; padding-right: 4px; }
.chart-button { display: grid; gap: 4px; width: 100%; padding: 10px 11px; border: 1px solid var(--line); border-radius: 7px; background: #fff; text-align: left; cursor: pointer; }
.chart-button.active { border-color: #a8c8dd; background: var(--active-bg); color: var(--active); }
.chart-button strong { font-size: 13px; }
.chart-button span { color: var(--muted); font-size: 11px; line-height: 1.35; }
.workspace { display: grid; grid-template-rows: auto minmax(0, 1fr) minmax(0, 160px); gap: 12px; min-width: 0; min-height: 0; height: 100%; padding: 18px; overflow: hidden; }
.workspace-head { display: flex; align-items: flex-start; justify-content: space-between; gap: 16px; }
.workspace-head h2 { font-size: 22px; line-height: 1.25; }
.open-link { padding: 8px 11px; border: 1px solid var(--line); border-radius: 7px; background: #fff; color: var(--ink); text-decoration: none; font-size: 13px; font-weight: 800; cursor: pointer; }
.recreated-pane { display: grid; grid-template-rows: auto minmax(0, 1fr); gap: 8px; min-width: 0; min-height: 0; }
.recreated-pane h3, .issues h3 { color: var(--muted); font-size: 13px; font-weight: 900; }
.component-chart { min-height: 0; height: 100%; border: 1px solid var(--line); border-radius: 8px; background: #e9edf1; padding: 12px; overflow: hidden; }
.chart-container { display: grid; gap: 12px; width: 100%; height: 100%; min-width: 0; min-height: 0; }
.chart-area { position: relative; min-width: 0; min-height: 0; border: 1px solid #cbd3db; border-radius: 8px; background: #fff; overflow: hidden; }
.area-body, .component-stage { position: absolute; inset: 0; min-width: 0; min-height: 0; overflow: hidden; }
.component-overlay { position: absolute; inset: 0; z-index: 3; pointer-events: none; overflow: hidden; }
.area-head { position: absolute; top: 0; left: 0; right: 0; z-index: 2; display: flex; justify-content: space-between; gap: 18px; padding: 16px 16px 0; overflow: visible; }
.area-head h2 { margin: 0; color: var(--ink); font-size: 17px; line-height: 1.25; }
.note-link { min-height: 0; padding: 0; border: 0; border-radius: 0; background: transparent; color: var(--muted); font-size: 10px; line-height: 1.2; font-weight: 800; text-decoration: underline; cursor: pointer; }
.note-link:hover { color: var(--active); }
.area-label { position: absolute; top: 8px; left: 10px; z-index: 4; max-width: calc(100% - 20px); padding: 3px 6px; border-radius: 5px; background: rgba(255,255,255,.78); color: var(--muted); font-size: 10px; font-weight: 850; line-height: 1; pointer-events: none; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.summary-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 10px; width: 100%; height: 100%; padding: 10px; }
.summary-metric { display: grid; align-content: center; gap: 4px; min-width: 0; border: 1px solid var(--line); border-radius: 8px; padding: 8px 12px; background: #fff; }
.summary-metric span { color: var(--muted); font-size: 12px; font-weight: 750; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.summary-metric strong { color: var(--ink); font-size: 22px; line-height: 1; }
.chart-svg { display: block; width: 100%; height: 100%; }
.axis-line, .grid-line { vector-effect: non-scaling-stroke; }
.grid-line { stroke: #e3e8ee; stroke-width: 1; }
.axis-line { stroke: #aeb9c4; stroke-width: 1; }
.series-line { fill: none; stroke: var(--active); stroke-width: 2.4; vector-effect: non-scaling-stroke; }
.secondary-line { fill: none; stroke: var(--warning); stroke-width: 2; stroke-dasharray: 5 4; vector-effect: non-scaling-stroke; }
.champion-line { fill: none; stroke: var(--active); stroke-width: 3; vector-effect: non-scaling-stroke; }
.challenger-line { fill: none; stroke: var(--ok); stroke-width: 3; vector-effect: non-scaling-stroke; }
.main-line { fill: none; stroke: var(--ok); stroke-width: 2.8; vector-effect: non-scaling-stroke; }
.alt-line { fill: none; stroke: var(--warning); stroke-width: 2.8; vector-effect: non-scaling-stroke; }
.series-point { fill: var(--active); stroke: #fff; stroke-width: 1; vector-effect: non-scaling-stroke; }
.secondary-point { fill: var(--warning); stroke: #fff; stroke-width: 1; vector-effect: non-scaling-stroke; }
.champion-point { fill: var(--active); stroke: #fff; stroke-width: 2; vector-effect: non-scaling-stroke; }
.challenger-point { fill: var(--ok); stroke: #fff; stroke-width: 2; vector-effect: non-scaling-stroke; }
.alarm-point { fill: var(--warning); stroke: #fff; stroke-width: 2; vector-effect: non-scaling-stroke; }
.retrain-point { fill: var(--danger); stroke: #fff; stroke-width: 2; vector-effect: non-scaling-stroke; }
.bar { fill: #5b91b4; }
.bar.hot { fill: var(--warning); }
.cell { stroke: #fff; stroke-width: 1; }
.scatter { opacity: .78; stroke: #fff; stroke-width: 1; }
.band { fill: rgba(47,111,159,.22); }
.threshold { stroke: var(--danger); stroke-width: 2; stroke-dasharray: 5 4; vector-effect: non-scaling-stroke; }
.marker-line { stroke: var(--danger); stroke-width: 2; stroke-dasharray: 5 4; vector-effect: non-scaling-stroke; }
.baseline-line { stroke: #7b8793; stroke-width: 1.6; stroke-dasharray: 5 5; vector-effect: non-scaling-stroke; }
.alarm-line { stroke: var(--warning); stroke-width: 2.4; stroke-dasharray: 4 4; vector-effect: non-scaling-stroke; }
.retrain-line { stroke: var(--danger); stroke-width: 2.6; stroke-dasharray: 5 4; vector-effect: non-scaling-stroke; }
.event { fill: #7868a8; }
.replace-point { fill: var(--danger); stroke: #fff; stroke-width: 1.6; vector-effect: non-scaling-stroke; }
.warning-text { fill: var(--danger); font-size: 8px; font-weight: 800; }
.callout { fill: var(--ok); font-size: 8px; font-weight: 800; }
.callout-alarm { fill: var(--warning); font-size: 8px; font-weight: 800; }
.callout-retrain { fill: var(--danger); font-size: 8px; font-weight: 800; }
.callout-win { fill: var(--ok); font-size: 8px; font-weight: 800; }
.bar-champion { fill: rgba(47, 111, 159, 0.82); }
.bar-challenger { fill: rgba(58, 128, 100, 0.84); }
.bar-latency { fill: rgba(185, 90, 80, 0.72); }
.state-normal { fill: rgba(47, 111, 159, 0.35); }
.state-warning { fill: rgba(201, 149, 47, 0.62); }
.state-alt { fill: rgba(58, 128, 100, 0.66); }
.state-replace { fill: rgba(185, 90, 80, 0.74); }
.state-drift { fill: #d97870; }
.state-retrain { fill: rgba(58, 128, 100, 0.66); }
.label { fill: var(--muted); font-size: 8px; font-weight: 750; }
.timeline-label { font-size: 8px; font-weight: 850; }
.timeline-note-link { cursor: pointer; fill: var(--ink); text-decoration: underline; pointer-events: auto; }
.value { fill: var(--ink); font-size: 8px; font-weight: 850; }
.axis-tick { fill: var(--muted); font-size: 8px; font-weight: 700; }
.axis-label { fill: var(--muted); font-size: 8px; font-weight: 750; }
.line-readout { fill: var(--muted); font-size: 8px; font-weight: 800; }
.issues { min-height: 0; max-height: 160px; overflow: auto; padding: 12px 14px; border: 1px solid var(--line); border-radius: 8px; background: #fff; }
.issues ul { margin: 8px 0 0; padding-left: 20px; color: var(--muted); font-size: 13px; line-height: 1.45; }
.note-popup { position: fixed; inset: 0; z-index: 1000; display: grid; place-items: center; padding: 24px; background: rgba(23,33,43,.32); }
.note-popup[hidden] { display: none; }
.note-popup-panel { display: grid; gap: 12px; width: min(420px, 100%); border: 1px solid var(--line); border-radius: 8px; background: #fff; padding: 14px; box-shadow: 0 18px 44px rgba(23,33,43,.24); }
.note-popup-close { justify-self: end; min-height: 30px; }
.note-popup-body { color: var(--ink); font-size: 14px; line-height: 1.45; }
"""


RECREATED_JS = r"""(() => {
  const payloads = window.RECREATED_CHART_PAYLOADS || [];
  const list = document.getElementById("chartList");
  const search = document.getElementById("searchInput");
  const chartTitle = document.getElementById("chartTitle");
  const chartStatus = document.getElementById("chartStatus");
  const originalLink = document.getElementById("originalLink");
  const componentChart = document.getElementById("componentChart");
  const issueList = document.getElementById("issueList");
  let activeId = payloads[0]?.chartId || "";
  let activePayload = null;

  function escapeHtml(value) {
    return String(value).replaceAll("&", "&amp;").replaceAll("<", "&lt;").replaceAll(">", "&gt;");
  }

  function renderList() {
    const q = search.value.trim().toLowerCase();
    list.innerHTML = "";
    payloads
      .filter((payload) => !q || payload.chartId.toLowerCase().includes(q) || payload.title.toLowerCase().includes(q) || payload.components.some((item) => item.componentType.includes(q)))
      .forEach((payload) => {
        const button = document.createElement("button");
        button.className = `chart-button${payload.chartId === activeId ? " active" : ""}`;
        button.type = "button";
        button.innerHTML = `<strong>${payload.chartId}</strong><span>${escapeHtml(payload.components.map((item) => item.componentType).join(", "))}</span>`;
        button.addEventListener("click", () => selectChart(payload.chartId));
        list.appendChild(button);
      });
  }

  function selectChart(chartId) {
    activeId = chartId;
    const payload = payloads.find((item) => item.chartId === chartId) || payloads[0];
    if (!payload) return;
    activePayload = payload;
    chartTitle.textContent = `${payload.chartId} - ${payload.title.replace(/^.*? - /, "")}`;
    const layoutName = payload.layout.displayName || payload.layout.presetCode || "saved layout";
    chartStatus.textContent = `${payload.reproduction.status} reproduction - ${layoutName}`;
    originalLink.dataset.originalPath = payload.originalPath;
    originalLink.title = `Open ${payload.chartId} original chart`;
    issueList.innerHTML = payload.reproduction.issues.map((issue) => `<li>${escapeHtml(issue)}</li>`).join("");
    renderComponentChart(payload);
    renderList();
  }

  function renderComponentChart(payload) {
    const layout = payload.layout;
    const container = document.createElement("section");
    container.className = "chart-container";
    container.style.gridTemplateColumns = layout.gridTemplateColumns || `repeat(${layout.columns}, minmax(0, 1fr))`;
    container.style.gridTemplateRows = layout.gridTemplateRows || `repeat(${layout.rows}, minmax(0, 1fr))`;
    if (layout.gap) container.style.gap = layout.gap;
    layout.areas.forEach((area) => {
      const areaEl = document.createElement("article");
      areaEl.className = "chart-area";
      areaEl.dataset.area = area.area;
      areaEl.dataset.role = area.role || "";
      if (area.title || area.description) areaEl.classList.add("has-panel-head");
      if (area.className) areaEl.classList.add(area.className);
      areaEl.style.gridColumn = `${area.x + 1} / span ${area.w}`;
      areaEl.style.gridRow = `${area.y + 1} / span ${area.h}`;
      const instances = payload.components.filter((item) => item.area === area.area);
      const inset = area.stageInset || {};
      const stageStyle = [
        inset.top !== undefined ? `top:${Number(inset.top)}px` : "",
        inset.right !== undefined ? `right:${Number(inset.right)}px` : "",
        inset.bottom !== undefined ? `bottom:${Number(inset.bottom)}px` : "",
        inset.left !== undefined ? `left:${Number(inset.left)}px` : ""
      ].filter(Boolean).join(";");
      const noteButton = area.description
        ? `<button class="note-link" type="button" data-note="${escapeHtml(area.description)}">${escapeHtml(area.noteLabel || "Note")}</button>`
        : "";
      const head = area.title || area.description
        ? `<div class="area-head" style="${area.headerHeight ? `height:${Number(area.headerHeight)}px` : ""}"><h2>${escapeHtml(area.title || "")}</h2>${noteButton}</div>`
        : "";
      const areaLabel = layout.showAreaLabels ? `<div class="area-label">${escapeHtml(area.area)}</div>` : "";
      areaEl.innerHTML = `<div class="area-body">${head}<div class="component-stage" style="${stageStyle}"></div><div class="component-overlay"></div>${areaLabel}</div>`;
      const stage = areaEl.querySelector(".component-stage");
      const overlayStage = areaEl.querySelector(".component-overlay");
      const baseComponents = instances.filter((item) => !item.isOverlay);
      const overlays = instances.filter((item) => item.isOverlay);
      if (baseComponents.length) {
        stage.innerHTML = renderComponent(payload, baseComponents[0]);
        if (baseComponents.length > 1) {
          areaEl.dataset.overflowComponents = baseComponents.slice(1).map((item) => item.componentType).join(", ");
        }
      } else if (overlays.length) {
        stage.innerHTML = renderComponent(payload, overlays[0]);
      }
      overlayStage.innerHTML = overlays.map((item) => renderComponent(payload, item)).join("");
      container.appendChild(areaEl);
    });
    componentChart.innerHTML = "";
    componentChart.appendChild(container);
  }

  function dataFor(payload, instance) {
    return payload.data[instance.dataBinding.source] || [];
  }

  function renderComponent(payload, instance) {
    const type = instance.componentType;
    if (["trend_line","raw_signal_trend","detector_statistic_view","distance_metric_view","performance_metric_view","control_chart","cumulative_curve","model_diagnostic_curve","adaptive_model_structure_view"].includes(type)) return renderLine(payload, instance);
    if (["bar_chart","ranking_view","contribution_view","proportion_view","reference_current_comparison","p_value_view"].includes(type)) return renderBar(payload, instance);
    if (["heatmap","matrix_view"].includes(type)) return renderMatrix(payload, instance);
    if (["projection_scatter"].includes(type)) return renderScatter(payload, instance);
    if (["distribution_view","histogram_view","distribution_summary_plot","quantile_view"].includes(type)) return renderDistribution(payload, instance);
    if (["state_timeline","window_view"].includes(type)) return renderTimeline(payload, instance);
    if (type === "threshold_line") return renderThreshold(instance);
    if (type === "event_marker") return renderEvents(payload, instance);
    if (type === "uncertainty_band") return renderBand(payload, instance);
    if (type === "comparison_table") return renderTable(payload, instance);
    return renderCard(payload, instance);
  }

  function extent(rows, field) {
    const values = rows.map((row) => row[field]).filter(hasFiniteValue).map(Number);
    if (!values.length) return [0, 1];
    const min = Math.min(...values);
    const max = Math.max(...values);
    return min === max ? [min - 1, max + 1] : [min, max];
  }

  function formatNumber(value) {
    const num = Number(value);
    if (!Number.isFinite(num)) return "";
    if (Number.isInteger(num)) return String(num);
    if (Math.abs(num) >= 100) return num.toFixed(0);
    if (Math.abs(num) >= 10) return num.toFixed(1);
    return num.toFixed(2);
  }

  function hasFiniteValue(value) {
    return value !== null && value !== undefined && value !== "" && Number.isFinite(Number(value));
  }

  function viewBoxFor(config, defaultW, defaultH) {
    const box = Array.isArray(config.view_box) ? config.view_box : [];
    const w = Number(box[0] ?? config.view_box_width ?? defaultW);
    const h = Number(box[1] ?? config.view_box_height ?? defaultH);
    return { w: Number.isFinite(w) ? w : defaultW, h: Number.isFinite(h) ? h : defaultH };
  }

  function marginFor(config, defaults) {
    const margin = config.margin || {};
    return {
      t: Number(margin.top ?? config.margin_top ?? defaults.t),
      r: Number(margin.right ?? config.margin_right ?? defaults.r),
      b: Number(margin.bottom ?? config.margin_bottom ?? defaults.b),
      l: Number(margin.left ?? config.margin_left ?? defaults.l)
    };
  }

  function ticksFor(min, max, configured, count = 5) {
    if (Array.isArray(configured)) {
      return configured.map(Number).filter(Number.isFinite);
    }
    if (count <= 1) return [min];
    return Array.from({ length: count }, (_, i) => min + ((max - min) * i) / (count - 1));
  }

  function path(points) {
    return points.map((p, i) => `${i ? "L" : "M"}${p[0].toFixed(1)},${p[1].toFixed(1)}`).join(" ");
  }

  function svg(inner, viewBox = "0 0 360 220") {
    return `<svg class="chart-svg" viewBox="${viewBox}" preserveAspectRatio="none" role="img">${inner}</svg>`;
  }

  function renderLine(payload, instance) {
    const rows = dataFor(payload, instance);
    const xField = instance.config.time_field || instance.config.x_field || "time";
    const yField = instance.config.value_field || instance.config.y_field || instance.config.statistic_field || "value";
    const secondaryField = instance.config.secondary_value_field;
    const primaryRows = rows.filter((row) => hasFiniteValue(row[xField]) && hasFiniteValue(row[yField]));
    if (!primaryRows.length) return renderCard(payload, instance);
    const secondaryRows = secondaryField
      ? primaryRows.filter((row) => hasFiniteValue(row[secondaryField]))
      : [];
    const [xMin, xMax] = extent(primaryRows, xField);
    const [yMinRaw, yMaxRaw] = extent(primaryRows, yField);
    const [y2MinRaw, y2MaxRaw] = secondaryRows.length ? extent(secondaryRows, secondaryField) : [yMinRaw, yMaxRaw];
    const yMin = Number.isFinite(Number(instance.config.y_min)) ? Number(instance.config.y_min) : Math.min(0, yMinRaw, y2MinRaw);
    const yMax = Number.isFinite(Number(instance.config.y_max)) ? Number(instance.config.y_max) : Math.max(yMaxRaw, y2MaxRaw) * 1.08;
    const { w, h } = viewBoxFor(instance.config, 360, 220);
    const m = marginFor(instance.config, { l: 42, r: 16, t: 18, b: 30 });
    const x = (v) => m.l + ((Number(v) - xMin) / (xMax - xMin || 1)) * (w - m.l - m.r);
    const y = (v) => m.t + (1 - ((Number(v) - yMin) / (yMax - yMin || 1))) * (h - m.t - m.b);
    const pts = primaryRows.map((row) => [x(row[xField]), y(row[yField])]);
    const sampleEvery = Math.max(1, Number(instance.config.point_sample_every) || Math.ceil(primaryRows.length / 16));
    const pointRadius = Number(instance.config.point_radius) || 2.4;
    const primaryDots = instance.config.show_points === false ? "" : primaryRows.map((row, i) => (
      i % sampleEvery === 0 || i === primaryRows.length - 1
        ? `<circle class="series-point" cx="${x(row[xField])}" cy="${y(row[yField])}" r="${pointRadius}"></circle>`
        : ""
    )).join("");
    const primaryLineClass = instance.config.line_class || "series-line";
    const secondaryLineClass = instance.config.secondary_line_class || "secondary-line";
    const backgroundRegions = (instance.config.background_regions || []).map((region) => {
      const x0 = x(region.x0);
      const x1 = x(region.x1);
      return `<rect x="${Math.min(x0, x1)}" y="${m.t}" width="${Math.abs(x1 - x0)}" height="${h - m.t - m.b}" fill="${escapeHtml(region.fill || "rgba(47,111,159,.08)")}"></rect>`;
    }).join("");
    const lineSegments = (field, lineClass) => {
      const segments = [];
      let current = [];
      primaryRows.forEach((row) => {
        if (!hasFiniteValue(row[field])) {
          if (current.length) segments.push(current);
          current = [];
        } else {
          current.push([x(row[xField]), y(row[field])]);
        }
      });
      if (current.length) segments.push(current);
      return segments.map((segment) => `<path class="${escapeHtml(lineClass)}" d="${path(segment)}"></path>`).join("");
    };
    const secondary = secondaryRows.length
      ? lineSegments(secondaryField, secondaryLineClass)
      : "";
    const secondaryDots = secondaryRows.length && instance.config.show_secondary_points !== false
      ? secondaryRows.map((row, i) => (
        i % sampleEvery === 0 || i === secondaryRows.length - 1
          ? `<circle class="secondary-point" cx="${x(row[xField])}" cy="${y(row[secondaryField])}" r="2.2"></circle>`
          : ""
      )).join("")
      : "";
    const plotW = w - m.l - m.r;
    const plotH = h - m.t - m.b;
    const yTicks = ticksFor(yMin, yMax, instance.config.y_ticks, 4);
    const xTicks = ticksFor(xMin, xMax, instance.config.x_ticks, 5);
    const xLabel = instance.config.x_axis_label || xField;
    const yLabel = instance.config.y_axis_label || instance.config.label || yField;
    const verticalMarkers = (instance.config.vertical_markers || []).map((marker) => {
      const markerClass = marker.class || "marker-line";
      return `<line class="${escapeHtml(markerClass)}" x1="${x(marker.x)}" x2="${x(marker.x)}" y1="${m.t}" y2="${h - m.b}"></line>`;
    }).join("");
    const horizontalMarkers = (instance.config.horizontal_markers || []).map((marker) => {
      const markerClass = marker.class || "threshold";
      const label = marker.label ? `<text class="${escapeHtml(marker.label_class || "axis-label")}" x="${x(marker.label_x ?? xMin)}" y="${y(marker.y) + Number(marker.label_dy ?? -8)}">${escapeHtml(marker.label)}</text>` : "";
      return `<line class="${escapeHtml(markerClass)}" x1="${m.l}" x2="${m.l + plotW}" y1="${y(marker.y)}" y2="${y(marker.y)}"></line>${label}`;
    }).join("");
    const annotations = (instance.config.annotations || []).map((annotation) => {
      const annotationClass = annotation.class || "callout";
      return `<text class="${escapeHtml(annotationClass)}" x="${x(annotation.x)}" y="${y(annotation.y)}">${escapeHtml(annotation.text || "")}</text>`;
    }).join("");
    const pointHighlights = (instance.config.point_highlights || []).map((point) => {
      const field = point.field || yField;
      const row = primaryRows.find((item) => Number(item[xField]) === Number(point.x));
      if (!row || !hasFiniteValue(row[field])) return "";
      return `<circle class="${escapeHtml(point.class || "series-point")}" cx="${x(row[xField])}" cy="${y(row[field])}" r="${Number(point.r) || pointRadius}"></circle>`;
    }).join("");
    const axisLabelX = Number(instance.config.axis_label_x ?? (m.l + plotW / 2));
    const axisLabelY = Number(instance.config.axis_label_y ?? (h - 12));
    return svg(`${backgroundRegions}
      ${yTicks.map((tick) => `<line class="grid-line" x1="${m.l}" x2="${m.l + plotW}" y1="${y(tick)}" y2="${y(tick)}"></line>`).join("")}
      ${horizontalMarkers}
      <path class="${escapeHtml(primaryLineClass)}" d="${path(pts)}"></path>
      ${secondary}
      ${primaryDots}
      ${secondaryDots}
      ${verticalMarkers}
      ${pointHighlights}
      <line class="axis-line" x1="${m.l}" x2="${m.l + plotW}" y1="${h - m.b}" y2="${h - m.b}"></line>
      <line class="axis-line" x1="${m.l}" x2="${m.l}" y1="${m.t}" y2="${h - m.b}"></line>
      ${yTicks.map((tick) => `<text class="axis-tick" x="${m.l - 12}" y="${y(tick) + 4}" text-anchor="end">${formatNumber(tick)}</text>`).join("")}
      ${xTicks.map((tick) => `<text class="axis-tick" x="${x(tick)}" y="${h - m.b + 24}" text-anchor="middle">${formatNumber(tick)}</text>`).join("")}
      <text class="axis-label" x="${axisLabelX}" y="${axisLabelY}" text-anchor="middle">${escapeHtml(xLabel)}</text>
      ${instance.config.y_axis_label === false ? "" : `<text class="axis-label" x="16" y="${m.t + plotH / 2}" text-anchor="middle" transform="rotate(-90 16 ${m.t + plotH / 2})">${escapeHtml(yLabel)}</text>`}
      ${annotations}`, `0 0 ${w} ${h}`);
  }

  function renderBar(payload, instance) {
    const rows = dataFor(payload, instance);
    if (Array.isArray(instance.config.series_fields) && instance.config.series_fields.length) {
      const categoryField = instance.config.category_field || "category";
      const series = instance.config.series_fields;
      const labels = instance.config.series_labels || series;
      const classes = instance.config.series_classes || [];
      const classFields = instance.config.series_class_fields || [];
      const valueMax = Number(instance.config.x_max) || Math.max(...rows.flatMap((row) => series.map((field) => Number(row[field]) || 0)), 1);
      const { w, h } = viewBoxFor(instance.config, 472, 185);
      const m = marginFor(instance.config, { t: 14, r: 32, b: 36, l: 112 });
      const x = (v) => m.l + (Number(v) / (valueMax || 1)) * (w - m.l - m.r);
      const rowGap = Number(instance.config.row_gap || 42);
      const barH = Number(instance.config.bar_height || 13);
      const firstY = Number(instance.config.first_y || 32);
      const body = rows.map((row, i) => {
        const y0 = firstY + i * rowGap;
        const bars = series.map((field, s) => {
          const y = y0 + s * (barH + 4);
          const value = Number(row[field]) || 0;
          const rowClass = classFields[s] ? row[classFields[s]] : "";
          return `<rect class="${escapeHtml(rowClass || classes[s] || "bar")}" x="${m.l}" y="${y}" width="${Math.max(0, x(value) - m.l)}" height="${barH}" rx="3"></rect><text class="axis-tick" x="${x(value) + 6}" y="${y + barH - 2}">${formatNumber(value)}</text>`;
        }).join("");
        return `<text class="label" x="${m.l - 18}" y="${y0 + barH + 1}" text-anchor="end">${escapeHtml(row[categoryField])}</text>${bars}`;
      }).join("");
      const legend = labels.map((label, i) => `<text class="${escapeHtml(classes[i]?.replace("bar-", "callout-") || "axis-label")}" x="${m.l + i * 88}" y="${h - 14}">${escapeHtml(label)}</text>`).join("");
      const annotations = (instance.config.annotations || []).map((annotation) => `<text class="${escapeHtml(annotation.class || "axis-label")}" x="${annotation.x}" y="${annotation.y}">${escapeHtml(annotation.text || "")}</text>`).join("");
      return svg(`${body}${legend}${annotations}`, `0 0 ${w} ${h}`);
    }
    const categoryField = instance.config.category_field || instance.config.item_field || instance.config.metric_field || "category";
    const valueField = instance.config.value_field || instance.config.score_field || instance.config.distance_field || "value";
    const sorted = rows.slice(0, 7).sort((a, b) => Number(b[valueField]) - Number(a[valueField]));
    const max = Math.max(...sorted.map((row) => Number(row[valueField]) || 0), 1);
    const rowH = 24;
    return svg(sorted.map((row, i) => {
      const y = 18 + i * rowH;
      const w = (Number(row[valueField]) || 0) / max * 220;
      return `<text class="label" x="78" y="${y + 13}" text-anchor="end">${escapeHtml(row[categoryField] || `item ${i+1}`)}</text><rect class="bar${i===0 ? " hot" : ""}" x="86" y="${y}" width="${w}" height="16" rx="4"></rect>`;
    }).join(""));
  }

  function renderMatrix(payload, instance) {
    const rows = dataFor(payload, instance);
    const xField = instance.config.x_field || instance.config.column_field || "column";
    const yField = instance.config.y_field || instance.config.row_field || "row";
    const valueField = instance.config.value_field || instance.config.cell_value_field || "value";
    const xs = [...new Set(rows.map((row) => row[xField]))].slice(0, 6);
    const ys = [...new Set(rows.map((row) => row[yField]))].slice(0, 6);
    return svg(ys.map((yy, r) => xs.map((xx, c) => {
      const item = rows.find((row) => row[xField] === xx && row[yField] === yy);
      const value = item ? Number(item[valueField]) || 0 : 0;
      const color = `rgba(47,111,159,${0.18 + Math.min(0.75, Math.abs(value))})`;
      return `<rect class="cell" x="${78 + c * 40}" y="${24 + r * 26}" width="36" height="22" rx="4" fill="${color}"></rect>`;
    }).join("")).join(""));
  }

  function renderScatter(payload, instance) {
    const rows = dataFor(payload, instance);
    const xField = instance.config.x_field || "x";
    const yField = instance.config.y_field || "y";
    const [xMin, xMax] = extent(rows, xField);
    const [yMin, yMax] = extent(rows, yField);
    const x = (v) => 32 + ((Number(v)-xMin)/(xMax-xMin||1))*300;
    const y = (v) => 20 + (1-((Number(v)-yMin)/(yMax-yMin||1)))*170;
    return svg(rows.map((row) => `<circle class="scatter" cx="${x(row[xField])}" cy="${y(row[yField])}" r="5" fill="${row.group === "current" ? "#c47d1f" : "#5b91b4"}"></circle>`).join(""));
  }

  function renderDistribution(payload, instance) {
    const rows = dataFor(payload, instance);
    const valueField = instance.config.value_field || instance.config.count_field || "value";
    const groups = [...new Set(rows.map((row) => row.group || "value"))].slice(0, 2);
    const values = rows.map((row) => Number(row[valueField])).filter(Number.isFinite);
    const max = Math.max(...values, 1);
    return svg(rows.slice(0, 18).map((row, i) => {
      const h = (Number(row[valueField]) || 0) / max * 120;
      const group = groups.indexOf(row.group || "value");
      return `<rect class="bar${group === 1 ? " hot" : ""}" x="${36 + i * 16}" y="${176 - h}" width="10" height="${h}" rx="2"></rect>`;
    }).join("") + `<line class="axis-line" x1="28" x2="340" y1="176" y2="176"></line>`);
  }

  function renderTimeline(payload, instance) {
    const rows = dataFor(payload, instance);
    if (rows.some((row) => row.start !== undefined && row.end !== undefined)) {
      const startField = instance.config.start_field || "start";
      const endField = instance.config.end_field || "end";
      const roleField = instance.config.window_role_field || "role";
      const labelField = instance.config.window_id_field || "window";
      const [xMin, xMax] = [Math.min(...rows.map((row) => Number(row[startField]) || 0)), Math.max(...rows.map((row) => Number(row[endField]) || 1))];
      const { w, h } = viewBoxFor(instance.config, 360, 220);
      const m = marginFor(instance.config, { t: 32, r: 24, b: 38, l: 48 });
      const y0 = Number(instance.config.track_y ?? 86);
      const trackHeight = Number(instance.config.track_height ?? 28);
      const labelMap = instance.config.label_map || {};
      const roleClassMap = instance.config.role_class_map || {};
      const x = (v) => m.l + ((Number(v) - xMin) / (xMax - xMin || 1)) * (w - m.l - m.r);
      const body = rows.map((row) => {
        const role = String(row[roleField] || "normal");
        const cls = roleClassMap[role] || (role.includes("drift") ? "state-drift" : role.includes("warn") ? "state-warning" : "state-normal");
        const x0 = x(row[startField]);
        const width = Math.max(8, x(row[endField]) - x0);
        const rawLabel = String(row[labelField] || role);
        const compactLabel = labelMap[rawLabel] || rawLabel;
        const note = escapeHtml(`${rawLabel}: ${row.start ?? ""}-${row.end ?? ""}`);
        return `<rect class="${cls}" x="${x0}" y="${y0}" width="${width}" height="${trackHeight}" rx="5"></rect><text class="label timeline-label timeline-note-link" data-note="${note}" x="${x0 + width / 2}" y="${y0 + trackHeight * 0.67}" text-anchor="middle">${escapeHtml(compactLabel)}</text>`;
      }).join("");
      const timelineMarkers = (instance.config.markers || []).map((markerConfig) => {
        const markerPositionField = markerConfig.position_field || instance.config.marker_position_field || startField;
        const markerRow = markerConfig.role ? rows.find((row) => String(row[roleField] || row[labelField] || "") === markerConfig.role) : null;
        const markerX = markerRow ? x(markerRow[markerPositionField]) : Number.isFinite(Number(markerConfig.x)) ? x(markerConfig.x) : null;
        if (markerX === null) return "";
        return `<line class="${escapeHtml(markerConfig.class || "marker-line")}" x1="${markerX}" x2="${markerX}" y1="${m.t}" y2="${h - m.b}"></line>${markerConfig.circle ? `<circle class="${escapeHtml(markerConfig.circle_class || "replace-point")}" cx="${markerX}" cy="${y0 + trackHeight / 2}" r="${Number(markerConfig.radius) || 6}"></circle>` : ""}`;
      }).join("");
      const markerRole = instance.config.marker_role;
      const markerPositionField = instance.config.marker_position_field || startField;
      const markerRow = !timelineMarkers && markerRole ? rows.find((row) => String(row[roleField] || row[labelField] || "") === markerRole) : null;
      const markerX = markerRow ? x(markerRow[markerPositionField]) : null;
      const marker = timelineMarkers || (markerX === null ? "" : `<line class="marker-line" x1="${markerX}" x2="${markerX}" y1="${m.t}" y2="${h - m.b}"></line>${instance.config.marker_circle ? `<circle class="replace-point" cx="${markerX}" cy="${y0 + trackHeight / 2}" r="${Number(instance.config.marker_radius) || 6}"></circle>` : ""}`);
      const axisLabel = instance.config.axis_label ? `<text class="axis-label" x="${Number(instance.config.axis_label_x ?? (m.l + (w - m.l - m.r) / 2))}" y="${Number(instance.config.axis_label_y ?? (h - 6))}" text-anchor="middle">${escapeHtml(instance.config.axis_label)}</text>` : "";
      return svg(`${body}${marker}<line class="axis-line" x1="${m.l}" x2="${w - m.r}" y1="${h - m.b}" y2="${h - m.b}"></line>${axisLabel}`, `0 0 ${w} ${h}`);
    }
    return svg(rows.map((row, i) => {
      const role = row.role || row.state || "normal";
      const cls = role.includes("drift") || role.includes("alarm") ? "state-drift" : role.includes("warn") || role.includes("current") ? "state-warning" : "state-normal";
      return `<rect class="${cls}" x="${36 + i * 72}" y="86" width="62" height="28" rx="5"></rect><text class="label" x="${67 + i * 72}" y="105" text-anchor="middle">${escapeHtml(row.window || row.state || role)}</text>`;
    }).join(""));
  }

  function renderThreshold(instance) {
    const value = Number(instance.config.threshold_value || 0.68);
    const y = 180 - value * 120;
    return svg(`<line class="threshold" x1="32" x2="334" y1="${y}" y2="${y}"></line><text class="value" x="238" y="${y - 8}">threshold ${value.toFixed(2)}</text>`);
  }

  function renderEvents(payload, instance) {
    const rows = dataFor(payload, instance);
    const xField = instance.config.time_field || "time";
    const xMin = Number(instance.config.x_min || Math.min(...rows.map((row) => Number(row[xField]) || 1), 1));
    const xMax = Number(instance.config.x_max || Math.max(...rows.map((row) => Number(row[xField]) || 1), 1));
    const { w, h } = viewBoxFor(instance.config, 360, 220);
    const m = marginFor(instance.config, { l: 42, r: 16, t: 18, b: 30 });
    const x = (v) => m.l + ((Number(v) - xMin) / (xMax - xMin || 1)) * (w - m.l - m.r);
    const base = instance.config.value_source_component_id
      ? payload.components.find((item) => item.componentInstanceId === instance.config.value_source_component_id)
      : payload.components.find((item) => item.area === instance.area && !item.isOverlay && ["trend_line","raw_signal_trend","detector_statistic_view","distance_metric_view","performance_metric_view","control_chart","cumulative_curve","model_diagnostic_curve","adaptive_model_structure_view"].includes(item.componentType));
    const yField = base?.config.value_field || base?.config.y_field || base?.config.statistic_field || "value";
    const baseRows = base ? dataFor(payload, base) : [];
    const [yMinRaw, yMaxRaw] = extent(baseRows, yField);
    const yMin = base && Number.isFinite(Number(base.config.y_min)) ? Number(base.config.y_min) : yMinRaw;
    const yMax = base && Number.isFinite(Number(base.config.y_max)) ? Number(base.config.y_max) : yMaxRaw;
    const y = (v) => m.t + (1 - ((Number(v) - yMin) / (yMax - yMin || 1))) * (h - m.t - m.b);
    const markers = rows.map((row) => `<line class="marker-line" x1="${x(row[xField])}" x2="${x(row[xField])}" y1="${m.t}" y2="${h - m.b}"></line>`).join("");
    const highlightType = String(instance.config.highlight_event_type || "");
    const eventTypeField = instance.config.event_type_field || "event_type";
    const highlights = rows.map((row) => {
      const eventType = String(row[eventTypeField] || row.label || "");
      if (!highlightType || eventType !== highlightType) return "";
      const point = baseRows.find((item) => Number(item[xField]) === Number(row[xField]));
      if (!point) return "";
      const cx = x(row[xField]);
      const cy = y(point[yField]);
      const textX = x(Number(row[xField]) + Number(instance.config.annotation_dx || 0));
      const textY = y(Math.min(yMax, Number(point[yField]) + (yMax - yMin) * Number(instance.config.annotation_dy_fraction || 0)));
      const label = row.annotation_label || instance.config.annotation_label || "";
      return `${instance.config.highlight_point ? `<circle class="replace-point" cx="${cx}" cy="${cy}" r="${Number(instance.config.highlight_radius) || 6}"></circle>` : ""}${label ? `<text class="warning-text" x="${textX}" y="${textY}">${escapeHtml(label)}</text>` : ""}`;
    }).join("");
    return svg(`${markers}${highlights}`, `0 0 ${w} ${h}`);
  }

  function renderBand(payload, instance) {
    const rows = dataFor(payload, instance);
    const upper = rows.map((row) => [30 + Number(row.time || 1) * 25, 180 - Number(row.upper || 0.5) * 120]);
    const lower = rows.map((row) => [30 + Number(row.time || 1) * 25, 180 - Number(row.lower || 0.3) * 120]);
    const center = rows.map((row) => [30 + Number(row.time || 1) * 25, 180 - Number(row.center || 0.4) * 120]);
    return svg(`<path class="band" d="${path(upper)} ${lower.slice().reverse().map((p) => `L${p[0]},${p[1]}`).join(" ")} Z"></path><path class="series-line" d="${path(center)}"></path>`);
  }

  function renderTable(payload, instance) {
    const rows = dataFor(payload, instance);
    return `<table style="width:100%;border-collapse:collapse;font-size:12px">${rows.slice(0, 5).map((row) => `<tr><td style="padding:6px;border-bottom:1px solid #d7dde4">${escapeHtml(row.metric || "metric")}</td><td style="padding:6px;border-bottom:1px solid #d7dde4;text-align:right">${Number(row.current || row.value || 0).toFixed(2)}</td></tr>`).join("")}</table>`;
  }

  function renderCard(payload, instance) {
    const rows = dataFor(payload, instance);
    if (instance.componentType === "decision_card" && rows.length) {
      return `<div class="summary-grid">${rows.map((row) => {
        const value = row.displayValue ?? row.display_value;
        const formatted = value !== undefined ? value : Number(row.value).toFixed(Number(row.value) < 1 ? 2 : 0);
        return `<section class="summary-metric"><span>${escapeHtml(row.label || "metric")}</span><strong>${escapeHtml(formatted)}</strong></section>`;
      }).join("")}</div>`;
    }
    return svg(`<rect x="18" y="18" width="324" height="176" rx="8" fill="#f8fafb" stroke="#d7dde4"></rect><text class="value" x="34" y="60">${escapeHtml(instance.componentType)}</text><text class="label" x="34" y="86">${escapeHtml(instance.config.visual_code || instance.config.label || "component summary")}</text>`);
  }

  search.addEventListener("input", renderList);
  componentChart.addEventListener("click", (event) => {
    const target = event.target.closest(".timeline-note-link, .note-link");
    if (!target) return;
    showNotePopup(target.dataset.note || target.textContent || "");
  });
  originalLink.addEventListener("click", () => {
    if (!activePayload) return;
    const popupName = `original_${activePayload.chartId.replaceAll("-", "_")}`;
    const originalUrl = new URL(activePayload.originalPath, window.location.href);
    originalUrl.searchParams.set("v", Date.now().toString());
    const popup = window.open(
      originalUrl.toString(),
      popupName,
      "popup=yes,width=1180,height=820,scrollbars=yes,resizable=yes"
    );
    if (popup) {
      popup.focus();
    } else {
      window.location.href = activePayload.originalPath;
    }
  });
  renderList();
  selectChart(activeId);

  function showNotePopup(text) {
    let popup = document.getElementById("chartNotePopup");
    if (!popup) {
      popup = document.createElement("div");
      popup.id = "chartNotePopup";
      popup.className = "note-popup";
      popup.innerHTML = `<div class="note-popup-panel"><button class="note-popup-close" type="button">Close</button><div class="note-popup-body"></div></div>`;
      popup.addEventListener("click", (event) => {
        if (event.target === popup || event.target.closest(".note-popup-close")) popup.hidden = true;
      });
      document.body.appendChild(popup);
    }
    popup.querySelector(".note-popup-body").textContent = text;
    popup.hidden = false;
  }
})();
"""


if __name__ == "__main__":
    main()
