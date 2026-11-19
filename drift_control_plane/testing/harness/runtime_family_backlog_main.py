from __future__ import annotations

import argparse
from pathlib import Path

from .runtime_family_backlog import (
    DEFAULT_OUTPUT_DIR,
    build_runtime_family_backlog,
    write_runtime_family_backlog,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Classify runtime wrapper gaps into runtime family backlog.")
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    args = parser.parse_args()

    backlog = build_runtime_family_backlog()
    paths = write_runtime_family_backlog(backlog, Path(args.output_dir))
    for key, value in paths.items():
        print(f"{key}: {value}")
    print(f"runtimeWrapperMissing: {backlog['inputCounts']['runtimeWrapperMissing']}")
    print(f"familyCount: {backlog['familyCount']}")
    print(f"classificationCounts: {backlog['classificationCounts']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
