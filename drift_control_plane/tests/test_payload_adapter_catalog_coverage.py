from __future__ import annotations

from pathlib import Path

from tools.check_payload_adapter_coverage import run_coverage


ROOT = Path(__file__).resolve().parents[2]


def test_catalog_coverage_finds_all_runtime_templates_and_registered_bindings() -> None:
    method_data = next(
        path / "charts" / "method_data.js"
        for path in ROOT.iterdir()
        if path.name.startswith("drift ") and (path / "charts" / "method_data.js").exists()
    )
    report = run_coverage(
        method_data,
        ROOT / "chart_runtime" / "payloads" / "runtime_chart_payloads.json",
    )

    assert report["summary"]["chartCountInMethodCatalog"] == 53
    assert report["summary"]["runtimeTemplateChartCount"] == 53
    assert report["summary"]["missingRuntimeTemplateCount"] == 0
    assert report["summary"]["chartMethodPairCount"] == 188
    assert report["summary"]["registeredBindingCount"] == 188
    assert report["summary"]["passedBindingPairCount"] == 188
    assert report["summary"]["failedBindingPairCount"] == 0
    assert report["summary"]["missingBindingPairCount"] == 0
