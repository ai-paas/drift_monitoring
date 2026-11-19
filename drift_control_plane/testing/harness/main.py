from __future__ import annotations

import argparse
from pathlib import Path

from .config import HarnessConfig, TESTING_ROOT
from .scenario_runner import ScenarioRunner


def main() -> int:
    parser = argparse.ArgumentParser(description="Run drift_server headless test harness scenarios.")
    parser.add_argument(
        "--scenario",
        default=str(TESTING_ROOT / "harness" / "scenarios" / "case010_mode_a.json"),
        help="Path to scenario JSON file.",
    )
    args = parser.parse_args()

    runner = ScenarioRunner(HarnessConfig())
    exit_code = runner.run(Path(args.scenario))
    if runner.last_run_id and runner.last_run_dir:
        print(f"runId: {runner.last_run_id}")
        print(f"status: {runner.last_status}")
        print(f"summary: {runner.last_run_dir / 'summary.md'}")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
