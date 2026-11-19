from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .chart_method_compatibility import build_compatibility_matrix, csv_value
from .config import CONTROL_PLANE_ROOT


DEFAULT_OUTPUT_DIR = CONTROL_PLANE_ROOT / "testing" / "harness" / "matrix" / "generated" / "sprint39"


@dataclass(frozen=True)
class FamilyRule:
    family_id: str
    classification: str
    generic_runtime_key: str | None
    implementation_strategy: str
    priority: int
    method_keywords: tuple[str, ...]
    variant_keywords: tuple[str, ...] = ()
    chart_prefixes: tuple[str, ...] = ()


FAMILY_RULES: tuple[FamilyRule, ...] = (
    FamilyRule(
        family_id="distribution_ecdf_window",
        classification="generic_runtime_candidate",
        generic_runtime_key="generic_distribution_ecdf_window",
        implementation_strategy="one generic runtime can cover two-sample ECDF/statistic style methods.",
        priority=1,
        method_keywords=("KS Test", "Anderson-Darling", "Cramer-von Mises", "Kuiper", "Epps-Singleton"),
        chart_prefixes=("CHART-EDF", "CHART-DISTSHAPE"),
    ),
    FamilyRule(
        family_id="categorical_contingency_window",
        classification="generic_runtime_candidate",
        generic_runtime_key="generic_categorical_contingency_window",
        implementation_strategy="one categorical frequency/contingency runtime can cover chi-square, G-test, and Fisher style variants.",
        priority=1,
        method_keywords=("Chi-square", "G-test", "Fisher"),
        chart_prefixes=("CHART-CAT",),
    ),
    FamilyRule(
        family_id="rank_mean_variance_window",
        classification="generic_runtime_candidate",
        generic_runtime_key="generic_statistical_test_window",
        implementation_strategy="one numeric reference/current statistical-test runtime can cover rank, mean, and variance comparison methods.",
        priority=1,
        method_keywords=("Mann-Whitney", "Baumgartner", "t-test", "F-test", "Levene"),
        chart_prefixes=("CHART-RANK", "CHART-MEAN", "CHART-VAR", "CHART-ANNOT"),
    ),
    FamilyRule(
        family_id="probability_distance_window",
        classification="generic_runtime_candidate",
        generic_runtime_key="generic_probability_distance_window",
        implementation_strategy="one probability/category distance runtime can cover KL, JS, Hellinger, Bhattacharyya, TV, L-infinity, and HINC families.",
        priority=2,
        method_keywords=(
            "PSI",
            "KL Divergence",
            "Jensen-Shannon",
            "Hellinger",
            "Bhattacharyya",
            "Total Variation",
            "L-Infinity",
            "Histogram Intersection",
        ),
        chart_prefixes=("CHART-PROB", "CHART-CAT", "CHART-HIST"),
    ),
    FamilyRule(
        family_id="streaming_control_chart",
        classification="generic_runtime_candidate",
        generic_runtime_key="generic_streaming_control_chart",
        implementation_strategy="one numeric stream control-chart runtime can cover CUSUM, EWMA, GMA, ECDD/HDDM/STEPD style alarm outputs after method-specific statistic adapters.",
        priority=2,
        method_keywords=("CUSUM", "EWMA", "Geometric Moving Average", "ECDD", "HDDM", "STEPD"),
        chart_prefixes=("CHART-CTRL", "CHART-ERR", "CHART-ANNOT"),
    ),
    FamilyRule(
        family_id="streaming_change_point",
        classification="dedicated_wrapper_required",
        generic_runtime_key=None,
        implementation_strategy="BOCD, SeqDrift, and SPRT require dedicated state/statistic wrappers before generic chart payload reuse.",
        priority=3,
        method_keywords=("BOCD", "SeqDrift", "SPRT"),
        chart_prefixes=("CHART-BOCD", "CHART-STREAM"),
    ),
    FamilyRule(
        family_id="multivariate_embedding_distance",
        classification="requires_new_input_contract",
        generic_runtime_key=None,
        implementation_strategy="requires feature matrix, embedding, kernel, or projection input contracts before runtime implementation.",
        priority=4,
        method_keywords=(
            "MMD",
            "Wasserstein Distance",
            "Energy Distance",
            "LSDD",
            "Hotelling",
            "Mahalanobis",
            "Classifier 기반 embedding",
            "Feature Map",
            "Autoencoder",
            "Graph Embedding",
        ),
        variant_keywords=("SLICED_WASSERSTEIN_EMBEDDING",),
        chart_prefixes=("CHART-MV", "CHART-CLS", "CHART-REP"),
    ),
    FamilyRule(
        family_id="model_explanation_or_retraining",
        classification="out_of_scope_for_demo",
        generic_runtime_key=None,
        implementation_strategy="needs model lifecycle, explanation, anomaly, or retraining workflow contracts; defer for current datasource demo.",
        priority=5,
        method_keywords=("DriftRetraining", "SHAP", "HAT", "OCDD", "Model Uncertainty"),
        chart_prefixes=("CHART-ADAPT", "CHART-EXPL", "CHART-ANOM", "CHART-UNC"),
    ),
    FamilyRule(
        family_id="text_semantic_drift",
        classification="requires_new_input_contract",
        generic_runtime_key=None,
        implementation_strategy="requires text/embedding source schema and projection/reproducibility contract.",
        priority=5,
        method_keywords=("LLM Query", "Text Domain"),
        chart_prefixes=("CHART-TEXT",),
    ),
)


def build_runtime_family_backlog() -> dict[str, Any]:
    compatibility = build_compatibility_matrix()
    missing_rows = [row for row in compatibility["rows"] if row["status"] == "runtime_wrapper_missing"]
    classified_rows = [classify_missing_row(row) for row in missing_rows]
    families = summarize_families(classified_rows)
    return {
        "backlogId": "sprint39-runtime-family-backlog-001",
        "version": 1,
        "sourceMatrixId": compatibility["matrixId"],
        "inputCounts": {
            "runtimeWrapperMissing": len(missing_rows),
            "chartMethodPairs": len(compatibility["rows"]),
        },
        "classificationCounts": dict(sorted(Counter(row["classification"] for row in classified_rows).items())),
        "familyCount": len(families),
        "families": families,
        "rows": classified_rows,
    }


def classify_missing_row(row: dict[str, Any]) -> dict[str, Any]:
    rule = select_rule(row)
    return {
        "chartId": row["chartId"],
        "methodName": row["methodName"],
        "methodVariantKey": row["methodVariantKey"],
        "currentStatus": row["status"],
        "familyId": rule.family_id,
        "classification": rule.classification,
        "genericRuntimeKey": rule.generic_runtime_key,
        "implementationStrategy": rule.implementation_strategy,
        "priority": rule.priority,
        "payloadBindingStatus": row["payloadBindingStatus"],
        "payloadBindingKey": row["payloadBindingKey"],
        "description": row["description"],
    }


def select_rule(row: dict[str, Any]) -> FamilyRule:
    method_name = str(row.get("methodName") or "")
    variant_key = str(row.get("methodVariantKey") or "")
    chart_id = str(row.get("chartId") or "")
    for rule in FAMILY_RULES:
        if any(keyword in method_name for keyword in rule.method_keywords):
            return rule
        if any(keyword in variant_key for keyword in rule.variant_keywords):
            return rule
    for rule in FAMILY_RULES:
        if any(chart_id.startswith(prefix) for prefix in rule.chart_prefixes):
            return rule
    return FamilyRule(
        family_id="unclassified_dedicated_review",
        classification="dedicated_wrapper_required",
        generic_runtime_key=None,
        implementation_strategy="manual review required before implementation.",
        priority=6,
        method_keywords=(),
    )


def summarize_families(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[row["familyId"]].append(row)
    summaries = []
    for family_id, family_rows in grouped.items():
        first = family_rows[0]
        method_counts = Counter(row["methodName"] for row in family_rows)
        chart_counts = Counter(row["chartId"] for row in family_rows)
        summaries.append(
            {
                "familyId": family_id,
                "classification": first["classification"],
                "genericRuntimeKey": first["genericRuntimeKey"],
                "priority": first["priority"],
                "pairCount": len(family_rows),
                "uniqueMethodCount": len(method_counts),
                "uniqueChartCount": len(chart_counts),
                "topMethods": [
                    {"methodName": method, "count": count}
                    for method, count in method_counts.most_common(8)
                ],
                "topCharts": [
                    {"chartId": chart_id, "count": count}
                    for chart_id, count in chart_counts.most_common(8)
                ],
                "implementationStrategy": first["implementationStrategy"],
            }
        )
    return sorted(summaries, key=lambda item: (item["priority"], -item["pairCount"], item["familyId"]))


def write_runtime_family_backlog(backlog: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "runtime_family_backlog.json"
    csv_path = output_dir / "runtime_family_backlog.csv"
    summary_path = output_dir / "runtime_family_summary.json"
    report_path = output_dir / "runtime_family_backlog_report.md"

    json_path.write_text(json.dumps(backlog, ensure_ascii=False, indent=2), encoding="utf-8")
    summary_path.write_text(
        json.dumps(
            {
                "backlogId": backlog["backlogId"],
                "inputCounts": backlog["inputCounts"],
                "classificationCounts": backlog["classificationCounts"],
                "familyCount": backlog["familyCount"],
                "families": backlog["families"],
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    write_backlog_csv(backlog["rows"], csv_path)
    report_path.write_text(render_runtime_family_report(backlog), encoding="utf-8")
    return {
        "backlogJson": str(json_path),
        "backlogCsv": str(csv_path),
        "summaryJson": str(summary_path),
        "report": str(report_path),
    }


def write_backlog_csv(rows: list[dict[str, Any]], path: Path) -> None:
    fieldnames = [
        "priority",
        "classification",
        "familyId",
        "genericRuntimeKey",
        "chartId",
        "methodName",
        "methodVariantKey",
        "payloadBindingStatus",
        "payloadBindingKey",
        "implementationStrategy",
    ]
    with path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: csv_value(row.get(field)) for field in fieldnames})


def render_runtime_family_report(backlog: dict[str, Any]) -> str:
    lines = [
        "# Sprint39 Runtime Family Backlog",
        "",
        "## Summary",
        "",
        f"- runtimeWrapperMissing: {backlog['inputCounts']['runtimeWrapperMissing']}",
        f"- familyCount: {backlog['familyCount']}",
        "",
        "## Classification Counts",
        "",
    ]
    for name, count in backlog["classificationCounts"].items():
        lines.append(f"- {name}: {count}")
    lines.extend(["", "## Families", ""])
    for family in backlog["families"]:
        runtime = family["genericRuntimeKey"] or "n/a"
        lines.append(
            f"### P{family['priority']} {family['familyId']} ({family['pairCount']} pairs, {family['classification']})"
        )
        lines.append("")
        lines.append(f"- genericRuntimeKey: {runtime}")
        lines.append(f"- methodCount: {family['uniqueMethodCount']}")
        lines.append(f"- chartCount: {family['uniqueChartCount']}")
        lines.append(f"- strategy: {family['implementationStrategy']}")
        lines.append("- topMethods: " + ", ".join(f"{item['methodName']}={item['count']}" for item in family["topMethods"]))
        lines.append("- topCharts: " + ", ".join(f"{item['chartId']}={item['count']}" for item in family["topCharts"]))
        lines.append("")
    return "\n".join(lines)
