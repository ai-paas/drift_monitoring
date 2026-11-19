from __future__ import annotations

import argparse
from pathlib import Path

from .chart_method_compatibility import (
    DEFAULT_OUTPUT_DIR,
    build_compatibility_matrix,
    write_compatibility_artifacts,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate Sprint36 chart-method compatibility artifacts.")
    parser.add_argument(
        "--output-dir",
        default=str(DEFAULT_OUTPUT_DIR),
        help="Directory for compatibility matrix, CSV, summary, and gap report.",
    )
    args = parser.parse_args()

    matrix = build_compatibility_matrix()
    artifacts = write_compatibility_artifacts(matrix, Path(args.output_dir))
    summary = matrix["summary"]
    print(f"matrixJson: {artifacts['matrixJson']}")
    print(f"matrixCsv: {artifacts['matrixCsv']}")
    print(f"summaryJson: {artifacts['summaryJson']}")
    print(f"gapReport: {artifacts['gapReport']}")
    print(f"chartMethodPairCount: {summary['chartMethodPairCount']}")
    print(f"uniqueMethodVariantCount: {summary['uniqueMethodVariantCount']}")
    print(f"statusCounts: {summary['statusCounts']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
