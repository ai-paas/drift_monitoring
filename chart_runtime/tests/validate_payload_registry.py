from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PAYLOADS = ROOT / "payloads" / "runtime_chart_payloads.json"
RUNTIME_JS = ROOT / "chart_runtime.js"

CARD_FALLBACK_TYPES = {
    "decision_card",
    "domain_specific_visual",
}

OPTIONAL_UNPLACED_AREAS = {
    "notes",
}

FIELD_CONTRACTS = {
    "line_series": {
        "x": [["time_field", "x_field"], ["time", "x"]],
        "y": [["value_field", "y_field", "statistic_field"], ["value", "y"]],
    },
    "category_value": {
        "category": [["category_field", "item_field", "label_field", "name_field"], ["category", "item", "label", "name"]],
        "value": [["value_field", "score_field", "distance_field", "count_field"], ["value", "score", "distance", "count"]],
    },
    "matrix_cells": {
        "x": [["x_field", "column_field"], ["x", "column"]],
        "y": [["y_field", "row_field"], ["y", "row"]],
        "value": [["value_field", "cell_value_field"], ["value"]],
    },
    "xy_points": {
        "x": [["x_field"], ["x"]],
        "y": [["y_field"], ["y"]],
    },
    "projected_features": {
        "x": [["x_field"], ["x"]],
        "y": [["y_field"], ["y"]],
    },
    "estimate_interval": {
        "label": [["label_field", "term_field"], ["label", "term"]],
        "estimate": [["estimate_field", "value_field"], ["estimate", "value"]],
    },
    "node_link": {},
    "polar_bins": {},
    "event_rows": {},
    "distribution_rows": {},
    "time_ranges": {},
    "threshold_config": {},
    "interval_band": {},
    "table_rows": {},
}


def load_runtime_maps(runtime_js: Path) -> tuple[set[str], dict[str, dict[str, object]]]:
    text = runtime_js.read_text(encoding="utf-8")
    renderers_match = re.search(r"const COMPONENT_RENDERERS = \{(?P<body>.*?)\n  \};", text, re.S)
    specs_match = re.search(r"const COMPONENT_SPECS = \{(?P<body>.*?)\n  \};", text, re.S)
    if not renderers_match:
        raise RuntimeError("COMPONENT_RENDERERS를 chart_runtime.js에서 찾지 못했습니다.")
    if not specs_match:
        raise RuntimeError("COMPONENT_SPECS를 chart_runtime.js에서 찾지 못했습니다.")

    renderer_types = set(re.findall(r"^\s+([A-Za-z0-9_]+):", renderers_match.group("body"), re.M))
    specs: dict[str, dict[str, object]] = {}
    spec_pattern = re.compile(
        r'^\s+([A-Za-z0-9_]+): \{ renderer: "([^"]+)", fieldContract: "([^"]+)", requiresData: (true|false)(?:, overlay: true)? \}',
        re.M,
    )
    for component_type, renderer, field_contract, requires_data in spec_pattern.findall(specs_match.group("body")):
        specs[component_type] = {
            "renderer": renderer,
            "fieldContract": field_contract,
            "requiresData": requires_data == "true",
        }
    return renderer_types, specs


def load_payloads(path: Path) -> list[dict[str, object]]:
    payloads = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payloads, list):
        raise RuntimeError("payload fixture는 chart payload 배열이어야 합니다.")
    return payloads


def area_names(payload: dict[str, object]) -> set[str]:
    layout = payload.get("layout")
    if not isinstance(layout, dict):
        return set()
    areas = layout.get("areas", [])
    if not isinstance(areas, list):
        return set()
    return {area.get("area") for area in areas if isinstance(area, dict) and area.get("area")}


def first_rows(payload: dict[str, object], source: str) -> list[dict[str, object]]:
    data = payload.get("data")
    if not isinstance(data, dict):
        return []
    rows = data.get(source, [])
    if not isinstance(rows, list):
        return []
    return [row for row in rows if isinstance(row, dict)]


def field_from_config(config: dict[str, object], keys: list[str]) -> str | None:
    for key in keys:
        value = config.get(key)
        if isinstance(value, str) and value:
            return value
    return None


def validate_field_contract(
    chart_id: str,
    component: dict[str, object],
    spec: dict[str, object],
    rows: list[dict[str, object]],
    warnings: list[str],
) -> None:
    contract_name = spec.get("fieldContract")
    contract = FIELD_CONTRACTS.get(str(contract_name), {})
    if not contract or not rows:
        return

    config = component.get("config")
    if not isinstance(config, dict):
        config = {}
    row_fields = set().union(*(row.keys() for row in rows[:20]))
    for role, alternatives in contract.items():
        config_keys, default_fields = alternatives
        configured = field_from_config(config, config_keys)
        candidates = [configured] if configured else default_fields
        if not any(candidate in row_fields for candidate in candidates if candidate):
            component_id = component.get("componentInstanceId", "<no-component-id>")
            warnings.append(
                f"{chart_id} {component_id}: fieldContract {contract_name}.{role} 후보 {candidates}를 data row에서 찾지 못했습니다."
            )


def validate_payloads(payloads: list[dict[str, object]], renderer_types: set[str], specs: dict[str, dict[str, object]]):
    errors: list[str] = []
    warnings: list[str] = []
    component_count = 0

    missing_specs = sorted(renderer_types - set(specs))
    extra_specs = sorted(set(specs) - renderer_types)
    for component_type in missing_specs:
        errors.append(f"COMPONENT_RENDERERS에 있지만 COMPONENT_SPECS에 없는 타입: {component_type}")
    for component_type in extra_specs:
        errors.append(f"COMPONENT_SPECS에 있지만 COMPONENT_RENDERERS에 없는 타입: {component_type}")
    for component_type, spec in specs.items():
        contract_name = str(spec.get("fieldContract"))
        if contract_name not in FIELD_CONTRACTS:
            errors.append(f"{component_type}: 알 수 없는 fieldContract: {contract_name}")

    for payload in payloads:
        chart_id = str(payload.get("chartId", "<no-chart-id>"))
        areas = area_names(payload)
        components = payload.get("components", [])
        if not areas:
            errors.append(f"{chart_id}: layout.areas가 없거나 비어 있습니다.")
        if not isinstance(components, list):
            errors.append(f"{chart_id}: components는 배열이어야 합니다.")
            continue

        for component in components:
            if not isinstance(component, dict):
                errors.append(f"{chart_id}: component 항목은 객체여야 합니다.")
                continue
            component_count += 1
            component_id = component.get("componentInstanceId", "<no-component-id>")
            component_type = component.get("componentType")
            area = component.get("area")
            if area not in areas:
                message = f"{chart_id} {component_id}: component.area '{area}'가 layout.areas에 없습니다."
                if area in OPTIONAL_UNPLACED_AREAS:
                    warnings.append(message)
                else:
                    errors.append(message)

            if component_type in CARD_FALLBACK_TYPES:
                continue
            if component_type not in renderer_types:
                errors.append(f"{chart_id} {component_id}: registry에 없는 componentType: {component_type}")
                continue

            spec = specs.get(str(component_type))
            if not spec:
                errors.append(f"{chart_id} {component_id}: spec이 없는 componentType: {component_type}")
                continue

            binding = component.get("dataBinding")
            source = binding.get("source") if isinstance(binding, dict) else None
            requires_data = bool(spec.get("requiresData"))
            if requires_data and not source:
                errors.append(f"{chart_id} {component_id}: data가 필요한 componentType이지만 dataBinding.source가 없습니다.")
                continue
            if source:
                rows = first_rows(payload, str(source))
                if not rows:
                    message = f"{chart_id} {component_id}: dataBinding.source '{source}'의 rows가 없거나 객체 배열이 아닙니다."
                    if requires_data:
                        errors.append(message)
                    else:
                        warnings.append(message)
                    continue
                validate_field_contract(chart_id, component, spec, rows, warnings)

    return errors, warnings, component_count


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate chart payloads against runtime registry metadata.")
    parser.add_argument("--payloads", type=Path, default=DEFAULT_PAYLOADS, help="Payload fixture JSON path")
    parser.add_argument("--runtime-js", type=Path, default=RUNTIME_JS, help="chart_runtime.js path")
    args = parser.parse_args()

    renderer_types, specs = load_runtime_maps(args.runtime_js)
    payloads = load_payloads(args.payloads)
    errors, warnings, component_count = validate_payloads(payloads, renderer_types, specs)

    for warning in warnings:
        print(f"WARN {warning}")
    for error in errors:
        print(f"ERROR {error}")
    print(
        f"payloads={len(payloads)} components={component_count} "
        f"registryTypes={len(renderer_types)} specs={len(specs)} warnings={len(warnings)} errors={len(errors)}"
    )
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
