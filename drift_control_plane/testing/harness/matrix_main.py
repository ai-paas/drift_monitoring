from __future__ import annotations

import argparse
from pathlib import Path

from .matrix_runner import DEFAULT_MATRIX_PATH, load_matrix_seed, run_matrix


def _print_row_list(matrix_path: Path) -> None:
    matrix = load_matrix_seed(matrix_path)
    for row in matrix["rows"]:
        method = row.get("method", {}) if isinstance(row.get("method"), dict) else {}
        chart = row.get("chart", {}) if isinstance(row.get("chart"), dict) else {}
        harness = row.get("harness", {}) if isinstance(row.get("harness"), dict) else {}
        modes = ",".join(str(mode) for mode in harness.get("modes", []))
        print(
            f"{row.get('matrixRowId')}\t{row.get('status')}\t"
            f"{method.get('runtimeMethodKey')}\t{chart.get('chartId')}\t{modes}"
        )


# @managed-contract contract_id=harness.matrix_main.main level=P1
def main() -> int:
    parser = argparse.ArgumentParser(description="Run V2 catalog matrix rows through the harness.")
    parser.add_argument("--matrix", default=str(DEFAULT_MATRIX_PATH), help="Path to matrix seed JSON.")
    parser.add_argument("--status", choices=["executable", "all"], default="executable")
    parser.add_argument("--mode", choices=["A", "B", "all"], default="all")
    parser.add_argument("--row-id", default=None, help="Run or inspect one matrixRowId.")
    parser.add_argument("--pack", default=None, help="Run or inspect a matrix pack id from testing/harness/matrix/packs.")
    parser.add_argument("--list-rows", action="store_true", help="Print matrix rows and exit.")
    parser.add_argument("--dry-run", action="store_true", help="Create matrix artifacts without child scenario runs.")
    args = parser.parse_args()
    matrix_path = Path(args.matrix)

    if args.list_rows:
        _print_row_list(matrix_path)
        return 0

    result = run_matrix(
        matrix_path=matrix_path,
        status_filter=args.status,
        mode_filter=args.mode,
        row_id_filter=args.row_id,
        pack_id=args.pack,
        dry_run=args.dry_run,
    )
    coverage = result["coverageSummary"]
    print(f"matrixRunId: {result['matrixRunId']}")
    print(f"matrixRunDir: {result['matrixRunDir']}")
    print(f"passedResults: {coverage['passedResults']}")
    print(f"failedResults: {coverage['failedResults']}")
    print(f"skippedResults: {coverage['skippedResults']}")
    print(f"dryRunResults: {coverage['dryRunResults']}")
    return 1 if coverage["failedResults"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
