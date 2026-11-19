from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from .config import RUNS_ROOT
from .models import ApiCallRecord, StepResult, ValidationResult


def utc_now_iso() -> str:
    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def safe_name(value: str) -> str:
    return "".join(ch if ch.isalnum() or ch in "-_." else "_" for ch in value)


class ArtifactStore:
    def __init__(self, run_id: str, runs_root: Path = RUNS_ROOT) -> None:
        self.run_id = run_id
        self.runs_root = runs_root
        self.run_dir = runs_root / run_id
        self.api_calls_dir = self.run_dir / "api_calls"
        self.timeseries_dir = self.run_dir / "timeseries"
        self.events_dir = self.run_dir / "events"
        self.analysis_payloads_dir = self.run_dir / "analysis_payloads"
        self.logs_dir = self.run_dir / "logs"
        for directory in [
            self.api_calls_dir,
            self.timeseries_dir,
            self.events_dir,
            self.analysis_payloads_dir,
            self.logs_dir,
        ]:
            directory.mkdir(parents=True, exist_ok=True)

    def write_json(self, relative_path: str, data: Any) -> Path:
        path = self.run_dir / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        return path

    def write_text(self, relative_path: str, text: str) -> Path:
        path = self.run_dir / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path

    def save_api_call(self, record: ApiCallRecord) -> Path:
        filename = f"{record.call_id}_{safe_name(record.server)}_{safe_name(record.method)}.json"
        return self.write_json(f"api_calls/{filename}", record.__dict__)

    def write_manifest(self, manifest: dict[str, Any]) -> None:
        self.write_json("run_manifest.json", manifest)

    def write_steps(self, steps: list[StepResult]) -> None:
        self.write_json("scenario_steps.json", [step.__dict__ for step in steps])

    def write_validation_report(self, results: list[ValidationResult]) -> None:
        passed = sum(1 for result in results if result.status == "passed")
        failed = sum(1 for result in results if result.status == "failed")
        self.write_json(
            "validation_report.json",
            {
                "runId": self.run_id,
                "passed": passed,
                "failed": failed,
                "results": [result.__dict__ for result in results],
            },
        )

    def write_summary(self, status: str, scenario_id: str, started_at: str, finished_at: str, error: str | None) -> None:
        lines = [
            f"# Test Run Summary",
            "",
            f"- runId: {self.run_id}",
            f"- scenarioId: {scenario_id}",
            f"- status: {status}",
            f"- startedAt: {started_at}",
            f"- finishedAt: {finished_at}",
        ]
        if error:
            lines.extend(["", "## Error", "", error])
        self.write_text("summary.md", "\n".join(lines) + "\n")

    def append_index(self, metadata: dict[str, Any]) -> None:
        self.runs_root.mkdir(parents=True, exist_ok=True)
        index_path = self.runs_root / "index.jsonl"
        with index_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(metadata, ensure_ascii=False) + "\n")

