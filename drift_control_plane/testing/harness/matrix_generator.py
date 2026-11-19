from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .config import CONTROL_PLANE_ROOT
from .matrix_runner import DEFAULT_MATRIX_PATH, load_matrix_seed


DEFAULT_COVERAGE_REPORT_PATH = CONTROL_PLANE_ROOT / "testing" / "payload_adapter_coverage_report.json"
DEFAULT_GENERATED_DIR = CONTROL_PLANE_ROOT / "testing" / "harness" / "matrix" / "generated"
DEFAULT_GENERATED_MATRIX_PATH = DEFAULT_GENERATED_DIR / "v2_matrix_generated.json"


@dataclass(frozen=True)
class CatalogBinding:
    chart_id: str
    method: str
    method_variant_key: str
    binding_key: str
    data_sources: list[str]


# @managed-contract contract_id=harness.matrix_generator.generate_matrix level=P1
def generate_matrix(
    *,
    seed_path: Path = DEFAULT_MATRIX_PATH,
    coverage_report_path: Path = DEFAULT_COVERAGE_REPORT_PATH,
) -> dict[str, Any]:
    seed = load_matrix_seed(seed_path)
    bindings = _load_catalog_bindings(coverage_report_path)
    seed_by_pair = _seed_rows_by_pair(seed)
    rows: list[dict[str, Any]] = []
    used_row_ids: set[str] = set()

    for row in seed["rows"]:
        copied = json.loads(json.dumps(row, ensure_ascii=False))
        copied["generation"] = {
            "source": "seed_preserved",
            "reason": "existing matrix seed row is preserved verbatim for executable regression continuity",
        }
        rows.append(copied)
        used_row_ids.add(str(copied["matrixRowId"]))

    for binding in bindings:
        pair = (binding.method_variant_key, binding.chart_id)
        if pair in seed_by_pair:
            continue
        row_id = _unique_row_id(
            f"V2-GEN-{binding.chart_id}-{binding.method_variant_key}",
            used_row_ids,
        )
        rows.append(_candidate_gap_row(row_id, binding))
        used_row_ids.add(row_id)

    return {
        "matrixId": "v2-catalog-generated-001",
        "version": 1,
        "description": "Sprint 27 generated matrix candidates from payload adapter coverage catalog while preserving existing seed rows.",
        "sourceDocuments": [
            str(seed_path.relative_to(CONTROL_PLANE_ROOT)),
            str(coverage_report_path.relative_to(CONTROL_PLANE_ROOT)),
            "../drift 보고서/charts/method_data.js",
            "../chart_runtime/payloads/runtime_chart_payloads.json",
        ],
        "generationPolicy": {
            "executableRows": "preserve existing v2_matrix_seed rows",
            "candidateGapRows": "create one candidate_gap row per catalog binding not represented in seed",
            "blockedRows": "reserved for explicit hard blockers; generator currently emits candidate_gap for missing implementation context",
        },
        "rows": rows,
    }


# @managed-contract contract_id=harness.matrix_generator.compare_seed_to_generated level=P1
def compare_seed_to_generated(seed: dict[str, Any], generated: dict[str, Any]) -> dict[str, Any]:
    seed_row_ids = {str(row["matrixRowId"]) for row in seed.get("rows", [])}
    generated_row_ids = {str(row["matrixRowId"]) for row in generated.get("rows", [])}
    seed_executable = [row for row in seed.get("rows", []) if row.get("status") == "executable"]
    generated_executable = [row for row in generated.get("rows", []) if row.get("status") == "executable"]
    preserved_executable = [
        row
        for row in seed_executable
        if str(row.get("matrixRowId")) in generated_row_ids
    ]
    return {
        "seedMatrixId": seed.get("matrixId"),
        "generatedMatrixId": generated.get("matrixId"),
        "seedRowCount": len(seed.get("rows", [])),
        "generatedRowCount": len(generated.get("rows", [])),
        "seedExecutableRows": len(seed_executable),
        "generatedExecutableRows": len(generated_executable),
        "preservedExecutableRows": len(preserved_executable),
        "missingSeedRowIds": sorted(seed_row_ids - generated_row_ids),
        "newGeneratedRowIds": sorted(generated_row_ids - seed_row_ids),
        "candidateGapRows": sum(1 for row in generated.get("rows", []) if row.get("status") == "candidate_gap"),
        "blockedRows": sum(1 for row in generated.get("rows", []) if row.get("status") == "blocked"),
    }


def write_generation_artifacts(
    *,
    generated_matrix: dict[str, Any],
    comparison: dict[str, Any],
    output_path: Path = DEFAULT_GENERATED_MATRIX_PATH,
) -> dict[str, str]:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    comparison_path = output_path.with_name("v2_matrix_generation_comparison.json")
    summary_path = output_path.with_name("v2_matrix_generation_summary.md")
    output_path.write_text(json.dumps(generated_matrix, ensure_ascii=False, indent=2), encoding="utf-8")
    comparison_path.write_text(json.dumps(comparison, ensure_ascii=False, indent=2), encoding="utf-8")
    summary_path.write_text(_generation_summary(generated_matrix, comparison), encoding="utf-8")
    return {
        "generatedMatrixPath": str(output_path),
        "comparisonPath": str(comparison_path),
        "summaryPath": str(summary_path),
    }


def _load_catalog_bindings(coverage_report_path: Path) -> list[CatalogBinding]:
    report = json.loads(coverage_report_path.read_text(encoding="utf-8"))
    bindings = []
    for item in report.get("passedBindings", []):
        if not isinstance(item, dict):
            continue
        bindings.append(
            CatalogBinding(
                chart_id=str(item.get("chartId") or ""),
                method=str(item.get("method") or ""),
                method_variant_key=str(item.get("methodVariantKey") or ""),
                binding_key=str(item.get("bindingKey") or ""),
                data_sources=[str(source) for source in item.get("dataSources", [])],
            )
        )
    return [binding for binding in bindings if binding.chart_id and binding.method_variant_key]


def _seed_rows_by_pair(seed: dict[str, Any]) -> dict[tuple[str, str], dict[str, Any]]:
    rows: dict[tuple[str, str], dict[str, Any]] = {}
    for row in seed.get("rows", []):
        method = row.get("method") if isinstance(row.get("method"), dict) else {}
        chart = row.get("chart") if isinstance(row.get("chart"), dict) else {}
        method_variant_key = method.get("methodVariantKey")
        chart_id = chart.get("chartId")
        if method_variant_key and chart_id:
            rows[(str(method_variant_key), str(chart_id))] = row
    return rows


def _candidate_gap_row(row_id: str, binding: CatalogBinding) -> dict[str, Any]:
    method_name, method_variant = _split_method(binding.method, binding.method_variant_key)
    blocked_reasons = [
        "dataset_adapter_mapping_missing",
        "scenario_missing",
        "runtime_method_key_not_selected",
    ]
    return {
        "matrixRowId": row_id,
        "status": "candidate_gap",
        "dataset": {
            "datasetCaseId": None,
            "sourceId": None,
            "csvPath": None,
            "signalType": "catalog_candidate",
            "primarySignal": "unmapped",
        },
        "adapter": {
            "adapterType": None,
            "aggregateIntervalMinutes": None,
            "bucketResolution": None,
        },
        "method": {
            "methodName": method_name,
            "methodCategory": "CatalogCandidate",
            "methodVariantKey": method_variant,
            "runtimeMethodKey": None,
            "methodVariantId": None,
            "algorithmImplementationId": None,
        },
        "chart": {
            "chartId": binding.chart_id,
            "analysisChartId": None,
            "payloadAdapterKey": binding.binding_key,
        },
        "compatibility": {
            "catalogCompatible": True,
            "payloadCompatible": True,
            "runtimeExecutable": False,
            "blockedReasons": blocked_reasons,
            "notes": "Generated candidate from catalog binding; executable status requires dataset, adapter, runtime method, and scenario mapping.",
        },
        "harness": {
            "scenarioPath": None,
            "modes": [],
            "requiredValidations": [],
        },
        "generation": {
            "source": "payload_adapter_coverage_report.passedBindings",
            "catalogMethod": binding.method,
            "dataSources": binding.data_sources,
            "candidateStatus": "candidate_gap",
            "blockedReasons": blocked_reasons,
        },
    }


def _split_method(method: str, fallback_variant: str) -> tuple[str, str]:
    if "/" in method:
        name, variant = method.rsplit("/", 1)
        return name.strip(), variant.strip()
    return method.strip() or fallback_variant, fallback_variant


def _unique_row_id(base: str, used: set[str]) -> str:
    safe_base = re.sub(r"[^A-Za-z0-9_-]+", "-", base).strip("-")
    candidate = safe_base
    index = 2
    while candidate in used:
        candidate = f"{safe_base}-{index}"
        index += 1
    return candidate


def _generation_summary(generated: dict[str, Any], comparison: dict[str, Any]) -> str:
    rows = generated.get("rows", [])
    lines = [
        "# Matrix Generation Summary",
        "",
        f"- generatedMatrixId: {generated.get('matrixId')}",
        f"- generatedRows: {len(rows)}",
        f"- executableRows: {sum(1 for row in rows if row.get('status') == 'executable')}",
        f"- candidateGapRows: {sum(1 for row in rows if row.get('status') == 'candidate_gap')}",
        f"- blockedRows: {sum(1 for row in rows if row.get('status') == 'blocked')}",
        f"- preservedExecutableRows: {comparison.get('preservedExecutableRows')}",
        f"- missingSeedRows: {len(comparison.get('missingSeedRowIds', []))}",
        "",
        "## Status Policy",
        "",
        "- `executable`: existing seed row with scenario/runtime/chart mapping preserved.",
        "- `candidate_gap`: catalog binding exists, but dataset/adapter/runtime/scenario mapping is not complete.",
        "- `blocked`: reserved for known hard blockers that should not be selected until external state changes.",
        "",
    ]
    return "\n".join(lines)
