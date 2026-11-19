from __future__ import annotations

import csv
import re
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = ROOT / "drift_algorithm" / "docs" / "method_designs"


INPUT_SCHEMA_BY_CATEGORY = {
    "BatchDistributionComparison": "batch reference/current data. Use numeric, categorical, probability, or vector schema according to the method input type.",
    "StreamingChangeDetector": "minute-level ordered stream with `time` and numeric `value` or precomputed error/score column.",
    "SupervisedConceptDriftDetector": "label or error stream with `time` plus either `y_true`/`y_pred` or precomputed `error`.",
    "MultivariateProcessControl": "multivariate numeric DataFrame with `time` and feature columns from `params['feature_cols']`.",
    "RepresentationDriftMethod": "embedding or representation matrix with `time` plus `emb_*`, `embedding`, feature map, reconstruction, or anomaly columns.",
    "ExplanationDriftMethod": "explanation matrix with `time` plus SHAP/explanation columns, or tabular features with time/domain labels.",
    "DomainClassifierMethod": "reference/current domain classification input with `time` plus text, embedding, or descriptor features.",
    "OperationalAdaptationMethod": "labeled operational stream with `time`, prediction/label columns, metric columns, and optional event/model-state columns.",
}


def infer_input_schema(category: str, method_name: str, primary_input: str) -> str:
    text = f"{category} {method_name} {primary_input}".lower()
    if category == "BatchDistributionComparison":
        if any(token in text for token in ["category", "categorical", "class distribution", "contingency", "frequency", "probability", "확률분포", "범주"]):
            return "categorical_schema.md or probability schema. Required: `time` plus category/count or probability columns."
        if method_name in {"Energy Distance", "MMD", "LSDD"}:
            return "multivariate_schema.md or embedding_schema.md. Required: `time` plus numeric feature or embedding columns supplied through params."
        return "numeric_schema.md. Required: `time` plus numeric `value` unless a variant-specific numeric column is supplied."
    if category == "OperationalAdaptationMethod":
        return "label_schema.md plus operational event/model-state columns. Required: `time`, labels or error stream, metric columns, and optional retraining/adaptation event fields."
    if category == "SupervisedConceptDriftDetector" or any(token in text for token in ["labeled", "classification error", "error stream", "accuracy"]):
        return "label_schema.md. Required: `time` plus `y_true`/`y_pred` or precomputed `error`."
    if any(token in text for token in ["shap", "explanation"]):
        return "shap_schema.md. Required: `time` plus wide or long explanation values."
    if any(token in text for token in ["text", "query", "topic", "semantic"]):
        return "text_schema.md and optionally embedding_schema.md. Required: `time` plus `text`, descriptor, topic, or embedding columns according to variant."
    if any(token in text for token in ["embedding", "vector", "feature map", "latent", "graph", "multivariate"]):
        return "multivariate_schema.md or embedding_schema.md. Required: `time` plus feature/embedding columns supplied through params."
    if any(token in text for token in ["category", "categorical", "class distribution", "contingency", "frequency", "probability vector", "확률분포", "범주"]):
        return "categorical_schema.md or probability schema. Required: `time` plus category/count or probability columns."
    if any(token in text for token in ["numeric", "score", "sample", "stream", "variance", "mean", "rank", "histogram", "circular"]):
        return "numeric_schema.md. Required: `time` plus numeric `value` unless a variant-specific column is supplied."
    return INPUT_SCHEMA_BY_CATEGORY.get(category, "DataFrame schema defined by method-specific design.")


def infer_method_kind(category: str) -> str:
    if category == "OperationalAdaptationMethod":
        return "operational"
    return "detector"


def slugify(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    return text.strip("_") or "method"


def read_method_catalog() -> dict[str, dict[str, str]]:
    catalog = {}
    pattern = re.compile(
        r"^\|\s*(DM-\d{3})\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*`([^`]+)`\s*\|"
    )
    for line in (ROOT / "drift_methods_catalog.md").read_text(encoding="utf-8").splitlines():
        match = pattern.match(line)
        if match:
            method_id, name, input_type, output_type, status, variant_doc = match.groups()
            catalog[method_id] = {
                "method_name": name.strip(),
                "primary_input": input_type.strip(),
                "primary_output": output_type.strip(),
                "status": status.strip(),
                "variant_doc": variant_doc.strip(),
            }
    return catalog


def read_variants() -> dict[str, dict[str, object]]:
    rows_by_method: dict[str, dict[str, object]] = {}
    with (ROOT / "drift_method_variant_links.csv").open(encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            method_id = row["method_id"]
            entry = rows_by_method.setdefault(
                method_id,
                {
                    "method_category": row["method_category"],
                    "method_name": row["method_name"],
                    "method_status": row["method_status"],
                    "variant_doc": row["variant_doc"],
                    "variants": [],
                },
            )
            entry["variants"].append(row["variant_id"])
    return rows_by_method


def read_measurements() -> dict[str, list[str]]:
    measurements: dict[str, set[str]] = defaultdict(set)
    with (ROOT / "drift_method_variant_measurement_summary.csv").open(encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            for measurement in row["canonical_measurements"].split(";"):
                measurement = measurement.strip()
                if measurement:
                    measurements[row["method_id"]].add(measurement)
    return {method_id: sorted(values) for method_id, values in measurements.items()}


def render_doc(method_id: str, variant_entry: dict[str, object], catalog_entry: dict[str, str], measurements: list[str]) -> str:
    method_name = str(variant_entry["method_name"])
    category = str(variant_entry["method_category"])
    variants = list(variant_entry["variants"])
    variant_doc = catalog_entry.get("variant_doc") or str(variant_entry["variant_doc"])
    input_schema = infer_input_schema(category, method_name, catalog_entry.get("primary_input", ""))
    method_kind = infer_method_kind(category)

    variant_lines = "\n".join(f"- `{variant}`" for variant in variants)
    measurement_lines = "\n".join(f"- `{measurement}`" for measurement in measurements) or "- To be confirmed from implementation output."

    return f"""# {method_id} {method_name} Design

## 1. Method Identity

- Method ID: `{method_id}`
- Method name: `{method_name}`
- Category: `{category}`
- Method kind: `{method_kind}`
- Status: `{catalog_entry.get('status', variant_entry.get('method_status', ''))}`
- Source catalog: `drift_methods_catalog.md`
- Source variant document: `{variant_doc}`

## 2. Purpose

This method answers the drift question represented by `{method_name}` in the
catalog. Primary input from the catalog: {catalog_entry.get('primary_input', 'not specified')}.
Primary output from the catalog: {catalog_entry.get('primary_output', 'not specified')}.

## 3. Supported Variants

{variant_lines}

## 4. Input Schema

Use the common `pandas.DataFrame` input boundary from
`../input_output_contracts.md`.

Required schema:

```text
{input_schema}
```

The implementation must validate the concrete columns through `params` and
return `severity=\"not_applicable\"` if the supplied schema cannot represent this
method's required input.

## 5. Parameters

Method-specific parameters come from `drift_method_parameter_guide.md` and the
variant source document. The implementation should at minimum support:

- `alpha` or threshold parameter when the method uses a p-value or alarm limit.
- `min_reference_size` and `min_current_size` for batch methods.
- `feature_cols`, `category_col`, `count_col`, `embedding_cols`, or label/error
  column names when applicable.

## 6. Output Measurements

Return canonical measurements where applicable:

{measurement_lines}

Always include `SAMPLE_SIZE` or relevant effective count metadata when the
method compares reference/current windows.

## 7. Algorithm Steps

1. Validate required DataFrame columns and parameter names.
2. Convert `time` to datetime and sort by time.
3. Split reference/current windows or iterate the stream according to the method
   category.
4. Convert validated values to `numpy.ndarray` when numeric calculation starts.
5. Compute the method-specific statistic, distance, score, alarm state, or event.
6. Apply the documented p-value, threshold, control-limit, or policy rule.
7. Return `DriftResult` with canonical measurement keys and interpretation text.

## 8. Drift Decision Rule

The first implementation should use the variant document's default rule when it
is explicit. If no default is explicit, use:

- p-value methods: `p_value < params.get(\"alpha\", 0.05)`
- distance/score methods: compare with `params[\"threshold\"]`; if absent, return
  score with `drift_detected=None`
- streaming alarm methods: final detector alarm state
- supervised methods: warning/drift state from the detector logic

## 9. Warnings and Not-Applicable Conditions

Return warnings for:

- missing required columns
- empty reference/current windows
- sample size below method minimum
- unsupported variant id
- numerical instability such as singular covariance or zero-probability bins
- label-dependent methods called without labels or error stream

## 10. Implementation Target

```text
module: drift_algorithm.methods.{slugify(category)}
function: detect_{slugify(method_name)}
```

## 11. Verification Plan

Create at least two tests when implementation starts:

1. no-drift synthetic data with similar reference/current windows
2. drift-candidate synthetic data that changes the statistic or alarm in the
   expected direction

The test must assert canonical measurement keys, warning behavior, and the
documented `drift_detected` rule.
"""


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    catalog = read_method_catalog()
    variants = read_variants()
    measurements = read_measurements()

    for method_id in sorted(catalog):
        entry = variants.get(method_id)
        if not entry:
            continue
        method_name = entry["method_name"]
        filename = f"{method_id}_{slugify(str(method_name))}.md"
        path = OUT_DIR / filename
        path.write_text(
            render_doc(method_id, entry, catalog[method_id], measurements.get(method_id, [])),
            encoding="utf-8",
        )

    print(f"generated {len(list(OUT_DIR.glob('DM-*.md')))} method design docs in {OUT_DIR}")


if __name__ == "__main__":
    main()
