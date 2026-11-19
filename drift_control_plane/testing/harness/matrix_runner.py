from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .artifact_store import utc_now_iso
from .config import CONTROL_PLANE_ROOT, RUNS_ROOT


MATRIX_RUNS_ROOT = RUNS_ROOT / "matrix"
DEFAULT_MATRIX_PATH = CONTROL_PLANE_ROOT / "testing" / "harness" / "matrix" / "v2_matrix_seed.json"
DEFAULT_MATRIX_PACKS_DIR = CONTROL_PLANE_ROOT / "testing" / "harness" / "matrix" / "packs"
DEFAULT_CHILD_TIMEOUT_SECONDS = int(os.environ.get("HARNESS_MATRIX_CHILD_TIMEOUT_SECONDS", "420"))


@dataclass(frozen=True)
class MatrixRowSelection:
    row: dict[str, Any]
    mode: str | None
    selected: bool
    skip_reason: str | None = None


def _matrix_run_id(matrix_id: str) -> str:
    timestamp = utc_now_iso().replace("-", "").replace(":", "").replace("T", "_").replace("Z", "")
    safe_matrix_id = "".join(ch if ch.isalnum() or ch in "-_" else "_" for ch in matrix_id.lower())
    return f"{timestamp}_{safe_matrix_id}"


# @managed-contract contract_id=harness.matrix_runner.load_matrix_seed level=P1
def load_matrix_seed(matrix_path: Path) -> dict[str, Any]:
    data = json.loads(matrix_path.read_text(encoding="utf-8"))
    if not isinstance(data.get("matrixId"), str) or not data["matrixId"]:
        raise ValueError("matrixId is required")
    rows = data.get("rows")
    if not isinstance(rows, list):
        raise ValueError("rows must be a list")
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            raise ValueError(f"rows[{index}] must be an object")
        if not row.get("matrixRowId"):
            raise ValueError(f"rows[{index}].matrixRowId is required")
        if row.get("status") not in {"executable", "candidate_gap", "blocked"}:
            raise ValueError(f"rows[{index}].status is invalid")
    return data


# @managed-contract contract_id=harness.matrix_runner.load_matrix_pack level=P1
def load_matrix_pack(pack_id: str | None) -> dict[str, Any] | None:
    if not pack_id:
        return None
    pack_path = DEFAULT_MATRIX_PACKS_DIR / f"{pack_id}.json"
    data = json.loads(pack_path.read_text(encoding="utf-8"))
    if data.get("packId") != pack_id:
        raise ValueError(f"matrix pack id mismatch: {pack_id}")
    row_ids = data.get("rowIds")
    if not isinstance(row_ids, list) or not all(isinstance(row_id, str) for row_id in row_ids):
        raise ValueError("matrix pack rowIds must be a list of strings")
    return data


def _executable_skip_reason(row: dict[str, Any]) -> str | None:
    harness = row.get("harness") if isinstance(row.get("harness"), dict) else {}
    compatibility = row.get("compatibility") if isinstance(row.get("compatibility"), dict) else {}
    if row.get("status") != "executable":
        return f"status:{row.get('status')}"
    if compatibility.get("runtimeExecutable") is not True:
        return "runtime_not_executable"
    scenario_path = harness.get("scenarioPath")
    if not scenario_path:
        return "scenario_path_missing"
    if not (CONTROL_PLANE_ROOT / scenario_path).exists():
        return f"scenario_path_not_found:{scenario_path}"
    modes = harness.get("modes")
    if not isinstance(modes, list) or not modes:
        return "modes_missing"
    return None


def _mode_selected(row_mode: str, mode_filter: str) -> bool:
    return mode_filter == "all" or row_mode == mode_filter


# @managed-contract contract_id=harness.matrix_runner.select_matrix_rows level=P1
def select_matrix_rows(
    matrix_seed: dict[str, Any],
    status_filter: str = "executable",
    mode_filter: str = "all",
    row_id_filter: str | None = None,
    pack_row_ids: set[str] | None = None,
) -> list[MatrixRowSelection]:
    selections: list[MatrixRowSelection] = []
    for row in matrix_seed["rows"]:
        row_id = str(row.get("matrixRowId", ""))
        if pack_row_ids is not None and row_id not in pack_row_ids:
            selections.append(MatrixRowSelection(row=row, mode=None, selected=False, skip_reason="pack_filter"))
            continue
        if row_id_filter and row_id != row_id_filter:
            selections.append(MatrixRowSelection(row=row, mode=None, selected=False, skip_reason="row_id_filter"))
            continue

        executable_skip_reason = _executable_skip_reason(row)
        if status_filter == "executable" and executable_skip_reason:
            selections.append(MatrixRowSelection(row=row, mode=None, selected=False, skip_reason=executable_skip_reason))
            continue

        if status_filter not in {"executable", "all"}:
            raise ValueError(f"unsupported status_filter: {status_filter}")

        if executable_skip_reason:
            selections.append(MatrixRowSelection(row=row, mode=None, selected=False, skip_reason=executable_skip_reason))
            continue

        modes = row.get("harness", {}).get("modes", [])
        selected_modes = [mode for mode in modes if _mode_selected(str(mode), mode_filter)]
        if not selected_modes:
            selections.append(MatrixRowSelection(row=row, mode=None, selected=False, skip_reason="mode_filter"))
            continue
        for mode in selected_modes:
            selections.append(MatrixRowSelection(row=row, mode=str(mode), selected=True))
    return selections


def _parse_child_stdout(stdout: str) -> dict[str, str | None]:
    result: dict[str, str | None] = {"runId": None, "status": None, "summary": None}
    for line in stdout.splitlines():
        match = re.match(r"^(runId|status|summary):\s*(.+)$", line.strip())
        if match:
            result[match.group(1)] = match.group(2)
    return result


def _row_contract_fields(row: dict[str, Any]) -> dict[str, Any]:
    method = row.get("method", {}) if isinstance(row.get("method"), dict) else {}
    chart = row.get("chart", {}) if isinstance(row.get("chart"), dict) else {}
    return {
        "runtimeMethodKey": method.get("runtimeMethodKey"),
        "methodVariantKey": method.get("methodVariantKey"),
        "chartId": chart.get("chartId"),
        "payloadAdapterKey": chart.get("payloadAdapterKey"),
    }


def _row_blocked_reasons(row: dict[str, Any]) -> list[str]:
    compatibility = row.get("compatibility") if isinstance(row.get("compatibility"), dict) else {}
    reasons = compatibility.get("blockedReasons")
    if isinstance(reasons, list):
        return [str(reason) for reason in reasons]
    return []


def _read_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def _failure_stage(failed_names: list[str], return_code: int | None) -> str | None:
    if return_code not in (None, 0) and not failed_names:
        return "server_start"
    for name in failed_names:
        if name.startswith("health."):
            return "server_start"
        if name.startswith(("feeder.", "test_feeder.")):
            return "feeder"
        if "runtime" in name or "algorithm_impl" in name or "method_run" in name:
            return "runtime_method"
        if "bucket" in name or "adapter" in name:
            return "adapter_bucket"
        if "analysis" in name or "event" in name:
            return "event_analysis"
        if "llm" in name:
            return "llm"
        if "chart_state" in name:
            return "chart_runtime"
    return "validation" if failed_names else None


# @managed-contract contract_id=harness.matrix_runner.child_diagnostics level=P1
def _child_diagnostics(child_run_id: str | None, return_code: int | None) -> dict[str, Any]:
    if not child_run_id:
        return {
            "validationPassedCount": 0,
            "validationFailedCount": 0,
            "chartRuntimeSmokeStatus": "not_run",
            "failureStage": _failure_stage([], return_code),
        }
    run_dir = RUNS_ROOT / child_run_id
    validation = _read_json(run_dir / "validation_report.json")
    chart_summary = _read_json(run_dir / "chart_test_state" / "summary.json")
    failed_results = [
        result
        for result in validation.get("results", [])
        if isinstance(result, dict) and result.get("status") == "failed"
    ]
    failed_names = [str(result.get("name", "")) for result in failed_results]
    chart_status = "not_run"
    if chart_summary:
        chart_status = "passed" if chart_summary.get("componentCount", 0) >= 1 else "failed"
    return {
        "validationPassedCount": int(validation.get("passed") or 0),
        "validationFailedCount": int(validation.get("failed") or len(failed_results)),
        "chartRuntimeSmokeStatus": chart_status,
        "chartRuntimeComponentCount": chart_summary.get("componentCount"),
        "failureStage": _failure_stage(failed_names, return_code),
    }


def _run_child(selection: MatrixRowSelection) -> dict[str, Any]:
    row = selection.row
    scenario_path = row["harness"]["scenarioPath"]
    timeout_seconds = DEFAULT_CHILD_TIMEOUT_SECONDS
    command = [
        sys.executable,
        "-m",
        "testing.harness.run_with_servers",
        "--scenario",
        scenario_path,
        "--mode",
        str(selection.mode),
    ]
    try:
        completed = subprocess.run(
            command,
            cwd=CONTROL_PLANE_ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout_seconds,
        )
    except subprocess.TimeoutExpired as exc:
        stdout = _timeout_stream(exc.stdout)
        stderr = _timeout_stream(exc.stderr)
        parsed = _parse_child_stdout(stdout)
        child_run_id = parsed.get("runId")
        diagnostics = _child_diagnostics(child_run_id, None)
        diagnostics["failureStage"] = "timeout"
        diagnostics["timeoutSeconds"] = timeout_seconds
        return {
            "matrixRowId": row["matrixRowId"],
            "mode": selection.mode,
            "status": "failed",
            **_row_contract_fields(row),
            "childRunId": child_run_id,
            "childSummaryPath": parsed.get("summary"),
            "scenarioPath": scenario_path,
            "returnCode": None,
            "timedOut": True,
            "timeoutSeconds": timeout_seconds,
            "diagnostics": diagnostics,
            "stdout": stdout,
            "stderr": stderr + f"\nchild run timed out after {timeout_seconds} seconds",
        }
    parsed = _parse_child_stdout(completed.stdout)
    child_run_id = parsed.get("runId")
    return {
        "matrixRowId": row["matrixRowId"],
        "mode": selection.mode,
        "status": parsed.get("status") or ("passed" if completed.returncode == 0 else "failed"),
        **_row_contract_fields(row),
        "childRunId": child_run_id,
        "childSummaryPath": parsed.get("summary"),
        "scenarioPath": scenario_path,
        "returnCode": completed.returncode,
        "timedOut": False,
        "timeoutSeconds": timeout_seconds,
        "diagnostics": _child_diagnostics(child_run_id, completed.returncode),
        "stdout": completed.stdout,
        "stderr": completed.stderr,
    }


def _timeout_stream(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return str(value)


def _dry_run_result(selection: MatrixRowSelection) -> dict[str, Any]:
    return {
        "matrixRowId": selection.row["matrixRowId"],
        "mode": selection.mode,
        "status": "dry_run",
        **_row_contract_fields(selection.row),
        "childRunId": None,
        "childSummaryPath": None,
        "scenarioPath": selection.row.get("harness", {}).get("scenarioPath"),
        "returnCode": None,
        "diagnostics": _child_diagnostics(None, None),
        "stdout": "",
        "stderr": "",
    }


def _skip_result(selection: MatrixRowSelection) -> dict[str, Any]:
    blocked_reasons = _row_blocked_reasons(selection.row)
    return {
        "matrixRowId": selection.row["matrixRowId"],
        "mode": selection.mode,
        "status": "skipped",
        **_row_contract_fields(selection.row),
        "skipReason": selection.skip_reason,
        "blockedReasons": blocked_reasons,
        "candidateGapReason": ", ".join(blocked_reasons) if blocked_reasons else selection.skip_reason,
        "childRunId": None,
        "childSummaryPath": None,
        "scenarioPath": selection.row.get("harness", {}).get("scenarioPath"),
        "diagnostics": {
            "validationPassedCount": 0,
            "validationFailedCount": 0,
            "chartRuntimeSmokeStatus": "not_run",
            "failureStage": selection.skip_reason,
        },
    }


def _coverage_summary(matrix_seed: dict[str, Any], results: list[dict[str, Any]]) -> dict[str, Any]:
    rows = matrix_seed["rows"]
    status_counts: dict[str, int] = {}
    skip_reason_counts: dict[str, int] = {}
    candidate_gap_reason_counts: dict[str, int] = {}
    for row in rows:
        status = str(row.get("status"))
        status_counts[status] = status_counts.get(status, 0) + 1
    for result in results:
        skip_reason = result.get("skipReason")
        if skip_reason:
            reason = str(skip_reason)
            skip_reason_counts[reason] = skip_reason_counts.get(reason, 0) + 1
        if result.get("status") == "skipped":
            blocked_reasons = result.get("blockedReasons")
            if isinstance(blocked_reasons, list) and blocked_reasons:
                for reason_value in blocked_reasons:
                    reason = str(reason_value)
                    candidate_gap_reason_counts[reason] = candidate_gap_reason_counts.get(reason, 0) + 1
    return {
        "totalRows": len(rows),
        "executableRows": sum(1 for row in rows if row.get("status") == "executable"),
        "candidateGapRows": sum(1 for row in rows if row.get("status") == "candidate_gap"),
        "blockedRows": sum(1 for row in rows if row.get("status") == "blocked"),
        "rowStatusCounts": status_counts,
        "resultCount": len(results),
        "passedResults": sum(1 for result in results if result.get("status") == "passed"),
        "failedResults": sum(1 for result in results if result.get("status") == "failed"),
        "skippedResults": sum(1 for result in results if result.get("status") == "skipped"),
        "dryRunResults": sum(1 for result in results if result.get("status") == "dry_run"),
        "skipReasonCounts": skip_reason_counts,
        "candidateGapReasonCounts": candidate_gap_reason_counts,
    }


# @managed-contract contract_id=harness.matrix_runner.write_matrix_artifacts level=P1
def write_matrix_artifacts(
    matrix_run_dir: Path,
    manifest: dict[str, Any],
    results: list[dict[str, Any]],
    coverage_summary: dict[str, Any],
) -> None:
    matrix_run_dir.mkdir(parents=True, exist_ok=True)
    (matrix_run_dir / "matrix_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (matrix_run_dir / "row_results.json").write_text(
        json.dumps(results, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (matrix_run_dir / "coverage_summary.json").write_text(
        json.dumps(coverage_summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    lines = [
        "# Matrix Run Summary",
        "",
        f"- matrixRunId: {manifest['matrixRunId']}",
        f"- matrixId: {manifest['matrixId']}",
        f"- status: {'failed' if coverage_summary['failedResults'] else 'passed'}",
        f"- totalRows: {coverage_summary['totalRows']}",
        f"- resultCount: {coverage_summary['resultCount']}",
        f"- passedResults: {coverage_summary['passedResults']}",
        f"- failedResults: {coverage_summary['failedResults']}",
        f"- skippedResults: {coverage_summary['skippedResults']}",
        f"- dryRunResults: {coverage_summary['dryRunResults']}",
        f"- rowStatusCounts: {coverage_summary.get('rowStatusCounts', {})}",
        f"- skipReasonCounts: {coverage_summary.get('skipReasonCounts', {})}",
        f"- candidateGapReasonCounts: {coverage_summary.get('candidateGapReasonCounts', {})}",
        "",
        "## Row Results",
        "",
    ]
    for result in results:
        mode = result.get("mode") or "-"
        suffix = f" ({result.get('skipReason')})" if result.get("skipReason") else ""
        diagnostics = result.get("diagnostics", {}) if isinstance(result.get("diagnostics"), dict) else {}
        chart_status = diagnostics.get("chartRuntimeSmokeStatus", "-")
        failure_stage = diagnostics.get("failureStage") or "-"
        child_summary = result.get("childSummaryPath") or "-"
        candidate_gap_reason = result.get("candidateGapReason")
        reason_text = f", candidateGap={candidate_gap_reason}" if candidate_gap_reason else ""
        lines.append(
            f"- {result['matrixRowId']} / {mode}: {result['status']}{suffix} "
            f"[runtime={result.get('runtimeMethodKey')}, chart={result.get('chartId')}, "
            f"chartSmoke={chart_status}, failureStage={failure_stage}, summary={child_summary}{reason_text}]"
        )
    (matrix_run_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


# @managed-contract contract_id=harness.matrix_runner.run_matrix level=P1
def run_matrix(
    matrix_path: Path = DEFAULT_MATRIX_PATH,
    status_filter: str = "executable",
    mode_filter: str = "all",
    row_id_filter: str | None = None,
    pack_id: str | None = None,
    dry_run: bool = False,
) -> dict[str, Any]:
    started_at = utc_now_iso()
    matrix_seed = load_matrix_seed(matrix_path)
    matrix_pack = load_matrix_pack(pack_id)
    matrix_run_id = _matrix_run_id(matrix_seed["matrixId"])
    pack_row_ids = set(matrix_pack["rowIds"]) if matrix_pack else None
    selections = select_matrix_rows(matrix_seed, status_filter, mode_filter, row_id_filter, pack_row_ids)
    results: list[dict[str, Any]] = []
    for selection in selections:
        if not selection.selected:
            results.append(_skip_result(selection))
        elif dry_run:
            results.append(_dry_run_result(selection))
        else:
            results.append(_run_child(selection))
    finished_at = utc_now_iso()
    coverage = _coverage_summary(matrix_seed, results)
    manifest = {
        "matrixRunId": matrix_run_id,
        "matrixId": matrix_seed["matrixId"],
        "startedAt": started_at,
        "finishedAt": finished_at,
        "filters": {
            "status": status_filter,
            "mode": mode_filter,
            "rowId": row_id_filter,
            "packId": pack_id,
            "dryRun": dry_run,
        },
        "matrixPack": matrix_pack,
        "sourceMatrixPath": str(matrix_path),
    }
    matrix_run_dir = MATRIX_RUNS_ROOT / matrix_run_id
    write_matrix_artifacts(matrix_run_dir, manifest, results, coverage)
    return {
        "matrixRunId": matrix_run_id,
        "matrixRunDir": str(matrix_run_dir),
        "manifest": manifest,
        "coverageSummary": coverage,
        "rowResults": results,
    }
