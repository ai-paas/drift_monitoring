from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
import threading
import time
from datetime import datetime
from pathlib import Path
from urllib.request import urlopen

os.environ.setdefault("ADMIN_REQUEST_TIMEOUT_SECONDS", "30")
os.environ.setdefault("PGCONNECT_TIMEOUT", "1")
os.environ.setdefault("LLM_SKIP_DB", "1")
if "--admin-ui-require-llm-provider" in sys.argv and not os.environ.get("CODEX_EXEC_CMD"):
    codex_cmd = shutil.which("codex.cmd") or shutil.which("codex")
    if codex_cmd:
        os.environ["CODEX_EXEC_CMD"] = f"{codex_cmd} exec --skip-git-repo-check --sandbox read-only -"
        os.environ.setdefault("CODEX_EXEC_TIMEOUT", "180")

import uvicorn

from admin_server.app import main as admin_main
from drift_server.app.main import app as drift_app
from test_feeder_server.app.main import app as feeder_app

LLM_SERVER_ROOT = Path(__file__).resolve().parents[3] / "llm_interpretation_server"
if str(LLM_SERVER_ROOT) not in sys.path:
    sys.path.insert(0, str(LLM_SERVER_ROOT))
from interpretation_server import app as llm_app  # noqa: E402

from .config import HarnessConfig, TESTING_ROOT
from .admin_ui_smoke import run_admin_ui_anchor_smoke
from .artifact_store import ArtifactStore, utc_now_iso
from .models import ValidationResult
from .proxy_server import app as proxy_app
from .scenario_runner import ScenarioRunner


HEALTH_URLS = [
    "http://127.0.0.1:8770/api/admin/health",
    "http://127.0.0.1:8771/api/health",
    "http://127.0.0.1:8772/api/test-feeder/health",
    "http://127.0.0.1:8767/api/health",
]


def main() -> int:
    parser = argparse.ArgumentParser(description="Start local servers in-process and run a harness scenario.")
    parser.add_argument(
        "--scenario",
        default=str(TESTING_ROOT / "harness" / "scenarios" / "case010_mode_a.json"),
        help="Path to scenario JSON file.",
    )
    parser.add_argument(
        "--mode",
        choices=["A", "B"],
        default=None,
        help="Harness execution mode. Defaults to the scenario mode.",
    )
    parser.add_argument(
        "--admin-ui-smoke",
        action="store_true",
        help="Run the browser Admin UI anchor smoke instead of the direct scenario runner.",
    )
    parser.add_argument(
        "--admin-ui-visible",
        action="store_true",
        help="Show the browser while running --admin-ui-smoke.",
    )
    parser.add_argument(
        "--admin-ui-hold-seconds",
        type=int,
        default=None,
        help="Seconds to keep the visible Admin UI browser open after the smoke run. Defaults to 60 when visible.",
    )
    parser.add_argument(
        "--admin-ui-tick-delay-ms",
        type=int,
        default=None,
        help="Delay between Admin logical-time ticks. Defaults to 750 ms when visible.",
    )
    parser.add_argument(
        "--admin-ui-require-llm-provider",
        action="store_true",
        help="Fail --admin-ui-smoke when interpretation completes with rule-only fallback.",
    )
    args = parser.parse_args()
    scenario_path = Path(args.scenario)
    scenario_mode = _scenario_mode(scenario_path)
    mode = args.mode or scenario_mode
    proxy_base_url = "http://127.0.0.1:8780/proxy"

    servers = [
        uvicorn.Server(uvicorn.Config(admin_main.app, host="127.0.0.1", port=8770, log_level="warning")),
        uvicorn.Server(uvicorn.Config(drift_app, host="127.0.0.1", port=8771, log_level="warning")),
        uvicorn.Server(uvicorn.Config(feeder_app, host="127.0.0.1", port=8772, log_level="warning")),
        uvicorn.Server(uvicorn.Config(llm_app, host="127.0.0.1", port=8767, log_level="warning")),
    ]
    if mode == "B":
        _configure_mode_b_proxy(proxy_base_url)
        servers.append(uvicorn.Server(uvicorn.Config(proxy_app, host="127.0.0.1", port=8780, log_level="warning")))
    threads = [threading.Thread(target=server.run, daemon=True) for server in servers]
    for thread in threads:
        thread.start()

    try:
        _wait_for_health(mode)
        if args.admin_ui_smoke:
            return _run_admin_ui_smoke(
                args.admin_ui_visible,
                args.admin_ui_hold_seconds,
                args.admin_ui_tick_delay_ms,
                args.admin_ui_require_llm_provider,
            )
        runner = ScenarioRunner(_harness_config_for_mode(mode, proxy_base_url))
        exit_code = runner.run(scenario_path)
        if runner.last_run_id and runner.last_run_dir:
            print(f"runId: {runner.last_run_id}")
            print(f"status: {runner.last_status}")
            print(f"summary: {runner.last_run_dir / 'summary.md'}")
        return exit_code
    finally:
        for server in servers:
            server.should_exit = True


def _run_admin_ui_smoke(
    visible: bool = False,
    hold_seconds: int | None = None,
    tick_delay_ms: int | None = None,
    require_llm_provider: bool = False,
) -> int:
    run_id = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_admin_ui_case010_anchor"
    store = ArtifactStore(run_id)
    started_at = utc_now_iso()
    status = "failed"
    error: str | None = None
    validations: list[ValidationResult] = []
    effective_hold_seconds = 60 if visible and hold_seconds is None else max(hold_seconds or 0, 0)
    effective_tick_delay_ms = 750 if visible and tick_delay_ms is None else max(tick_delay_ms or 0, 0)
    try:
        store.write_manifest(
            {
                "runId": run_id,
                "scenarioId": "admin_ui_case010_anchor",
                "mode": "admin-ui-visible" if visible else "admin-ui-headless",
                "startedAt": started_at,
                "baseUrls": {
                    "admin": HarnessConfig().admin_base_url,
                    "drift": HarnessConfig().drift_base_url,
                    "testFeeder": HarnessConfig().test_feeder_base_url,
                    "llm": HarnessConfig().llm_base_url,
                },
            }
        )
        state = run_admin_ui_anchor_smoke(
            HarnessConfig().admin_base_url,
            store,
            visible=visible,
            hold_seconds=effective_hold_seconds,
            tick_delay_ms=effective_tick_delay_ms,
            require_llm_provider=require_llm_provider,
        )
        status = "passed" if state.get("status") == "passed" else "failed"
        validations.append(
            ValidationResult(
                name="sprint33.admin_ui.status",
                status=status,
                message=f"admin ui completed with status={state.get('status')}",
                details={"eventId": state.get("eventId"), "counts": state.get("counts", {})},
            )
        )
        if status != "passed":
            error = str(state.get("error") or "admin UI did not pass")
    except Exception as exc:  # noqa: BLE001
        error = f"{exc.__class__.__name__}: {exc}"
        validations.append(
            ValidationResult(
                name="sprint33.admin_ui.exception",
                status="failed",
                message=error,
                details={},
            )
        )
    finally:
        finished_at = utc_now_iso()
        store.write_validation_report(validations)
        store.write_summary(status, "admin_ui_case010_anchor", started_at, finished_at, error)
        store.append_index(
            {
                "runId": run_id,
                "scenarioId": "admin_ui_case010_anchor",
                "mode": "admin-ui-visible" if visible else "admin-ui-headless",
                "status": status,
                "startedAt": started_at,
                "finishedAt": finished_at,
                "summaryPath": f"{run_id}/summary.md",
            }
        )
        print(f"runId: {run_id}")
        print(f"status: {status}")
        print(f"summary: {store.run_dir / 'summary.md'}")
    return 0 if status == "passed" else 1


def _wait_for_health(mode: str = "A") -> None:
    failures: dict[str, str] = {}
    health_urls = list(HEALTH_URLS)
    if mode == "B":
        health_urls.append("http://127.0.0.1:8780/proxy-health")
    for _ in range(50):
        failures = {}
        for url in health_urls:
            try:
                with urlopen(url, timeout=1) as response:
                    response.read()
            except Exception as exc:  # noqa: BLE001
                failures[url] = f"{exc.__class__.__name__}: {exc}"
        if not failures:
            return
        time.sleep(0.2)
    raise RuntimeError(f"servers did not become healthy: {failures}")


def _scenario_mode(scenario_path: Path) -> str:
    try:
        scenario = json.loads(scenario_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return "A"
    return scenario.get("mode", "A")


# @managed-contract contract_id=harness.run_with_servers.configure_mode_b_proxy level=P1
def _configure_mode_b_proxy(proxy_base_url: str) -> None:
    admin_main.drift.base_url = f"{proxy_base_url}/drift"
    admin_main.test_feeder.base_url = f"{proxy_base_url}/test_feeder"


# @managed-contract contract_id=harness.run_with_servers.harness_config_for_mode level=P1
def _harness_config_for_mode(mode: str, proxy_base_url: str) -> HarnessConfig:
    if mode != "B":
        return HarnessConfig()
    return HarnessConfig(
        admin_base_url=f"{proxy_base_url}/admin",
        drift_base_url=f"{proxy_base_url}/drift",
        test_feeder_base_url=f"{proxy_base_url}/test_feeder",
        llm_base_url=f"{proxy_base_url}/llm",
    )


if __name__ == "__main__":
    raise SystemExit(main())
