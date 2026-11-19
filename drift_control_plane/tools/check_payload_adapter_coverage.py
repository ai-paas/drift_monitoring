from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DRIFT_SERVER_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(DRIFT_SERVER_ROOT))

from drift_server.app.payload_adapter import build_payload
from drift_server.app.payload_adapter.registry import get_registered_binding_index


DEFAULT_METHOD_DATA = next(
    path / "charts" / "method_data.js"
    for path in ROOT.iterdir()
    if path.name.startswith("drift ") and (path / "charts" / "method_data.js").exists()
)
DEFAULT_RUNTIME_PAYLOADS = ROOT / "chart_runtime" / "payloads" / "runtime_chart_payloads.json"
DEFAULT_REPORT = DRIFT_SERVER_ROOT / "testing" / "payload_adapter_coverage_report.json"


def _load_chart_methods(path: Path) -> dict[str, list[dict[str, Any]]]:
    text = path.read_text(encoding="utf-8")
    match = re.search(r"window\.CHART_METHODS\s*=\s*(\{.*\});\s*$", text, re.S)
    if not match:
        raise ValueError(f"cannot parse CHART_METHODS from {path}")
    return json.loads(match.group(1))


def _load_runtime_chart_ids(path: Path) -> set[str]:
    payloads = json.loads(path.read_text(encoding="utf-8"))
    return {str(payload["chartId"]) for payload in payloads}


def _method_variant_key(method_value: str) -> str:
    if "/" in method_value:
        return method_value.rsplit("/", 1)[1].strip()
    return method_value.strip()


def _context(method_variant_key: str, chart_id: str) -> dict[str, Any]:
    return {
        "source": {"sourceId": "coverage-source"},
        "feature": {"featureId": "metric", "featureLabel": "Metric"},
        "assignment": {"runtimeMethodKey": method_variant_key.lower()},
        "methodRun": {"methodRunId": f"run-{method_variant_key}"},
        "driftEvent": {
            "eventId": f"event-{method_variant_key}",
            "eventStart": "2026-01-01T00:10:00Z",
            "eventEnd": "2026-01-01T00:20:00Z",
            "level": "drift",
            "score": 3.25,
        },
        "runtimeResult": {
            "metrics": {"coverage": 1.0},
            "diagnostics": {"chartId": chart_id},
            "payloadHints": {},
        },
        "analysisChart": {
            "chartId": chart_id,
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


def run_coverage(method_data_path: Path, runtime_payloads_path: Path) -> dict[str, Any]:
    chart_methods = _load_chart_methods(method_data_path)
    runtime_chart_ids = _load_runtime_chart_ids(runtime_payloads_path)
    binding_index = get_registered_binding_index()

    pairs: list[dict[str, Any]] = []
    missing_runtime_templates: list[dict[str, Any]] = []
    missing_bindings: list[dict[str, Any]] = []
    passed_bindings: list[dict[str, Any]] = []
    failed_bindings: list[dict[str, Any]] = []

    for chart_id, methods in sorted(chart_methods.items()):
        if chart_id not in runtime_chart_ids:
            missing_runtime_templates.append({"chartId": chart_id})
        for method in methods:
            method_name = str(method.get("method", ""))
            method_variant_key = _method_variant_key(method_name)
            pair = {
                "chartId": chart_id,
                "method": method_name,
                "methodVariantKey": method_variant_key,
            }
            pairs.append(pair)
            binding_key = binding_index.get((method_variant_key, chart_id))
            if not binding_key:
                missing_bindings.append(pair)
                continue
            try:
                payload = build_payload(_context(method_variant_key, chart_id), binding_key)
                passed_bindings.append(
                    {
                        **pair,
                        "bindingKey": binding_key,
                        "bindingType": "auto" if binding_key.startswith("auto__") else "explicit",
                        "dataSources": sorted(payload.get("data", {}).keys()),
                    }
                )
            except Exception as exc:  # noqa: BLE001
                failed_bindings.append({**pair, "bindingKey": binding_key, "error": str(exc)})

    return {
        "source": {
            "methodData": str(method_data_path),
            "runtimePayloads": str(runtime_payloads_path),
        },
        "summary": {
            "chartCountInMethodCatalog": len(chart_methods),
            "runtimeTemplateChartCount": len(runtime_chart_ids),
            "chartMethodPairCount": len(pairs),
            "registeredBindingCount": len(binding_index),
            "passedBindingPairCount": len(passed_bindings),
            "failedBindingPairCount": len(failed_bindings),
            "missingBindingPairCount": len(missing_bindings),
            "missingRuntimeTemplateCount": len(missing_runtime_templates),
        },
        "passedBindings": passed_bindings,
        "failedBindings": failed_bindings,
        "missingBindings": missing_bindings,
        "missingRuntimeTemplates": missing_runtime_templates,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--method-data", type=Path, default=DEFAULT_METHOD_DATA)
    parser.add_argument("--runtime-payloads", type=Path, default=DEFAULT_RUNTIME_PAYLOADS)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    args = parser.parse_args()

    report = run_coverage(args.method_data, args.runtime_payloads)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report["summary"], ensure_ascii=False, indent=2))
    print(f"report={args.report}")


if __name__ == "__main__":
    main()
