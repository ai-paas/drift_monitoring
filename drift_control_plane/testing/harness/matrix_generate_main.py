from __future__ import annotations

import argparse
import json
from pathlib import Path

from .matrix_generator import (
    DEFAULT_COVERAGE_REPORT_PATH,
    DEFAULT_GENERATED_MATRIX_PATH,
    compare_seed_to_generated,
    generate_matrix,
    write_generation_artifacts,
)
from .matrix_runner import DEFAULT_MATRIX_PATH, load_matrix_seed


# @managed-contract contract_id=harness.matrix_generate_main.main level=P1
def main() -> int:
    parser = argparse.ArgumentParser(description="Generate V2 matrix candidates from catalog coverage.")
    parser.add_argument("--seed", default=str(DEFAULT_MATRIX_PATH), help="Existing matrix seed JSON to preserve.")
    parser.add_argument("--coverage-report", default=str(DEFAULT_COVERAGE_REPORT_PATH), help="Payload adapter coverage report JSON.")
    parser.add_argument("--output", default=str(DEFAULT_GENERATED_MATRIX_PATH), help="Generated matrix output JSON.")
    args = parser.parse_args()

    seed_path = Path(args.seed)
    coverage_report_path = Path(args.coverage_report)
    output_path = Path(args.output)
    seed = load_matrix_seed(seed_path)
    generated = generate_matrix(seed_path=seed_path, coverage_report_path=coverage_report_path)
    comparison = compare_seed_to_generated(seed, generated)
    artifacts = write_generation_artifacts(
        generated_matrix=generated,
        comparison=comparison,
        output_path=output_path,
    )
    print(f"generatedMatrixPath: {artifacts['generatedMatrixPath']}")
    print(f"comparisonPath: {artifacts['comparisonPath']}")
    print(f"summaryPath: {artifacts['summaryPath']}")
    print(f"generatedRows: {len(generated['rows'])}")
    print(f"preservedExecutableRows: {comparison['preservedExecutableRows']}")
    print(f"candidateGapRows: {comparison['candidateGapRows']}")
    print(f"missingSeedRows: {json.dumps(comparison['missingSeedRowIds'], ensure_ascii=False)}")
    return 1 if comparison["missingSeedRowIds"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
