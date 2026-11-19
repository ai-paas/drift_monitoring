from __future__ import annotations

from pathlib import Path

from .config import RUNS_ROOT


_active_run_id: str | None = None
_active_runs_root: Path = RUNS_ROOT


# @managed-contract contract_id=harness.proxy_runtime.set_active_proxy_run level=P1
def set_active_proxy_run(run_id: str, runs_root: Path = RUNS_ROOT) -> None:
    global _active_run_id, _active_runs_root
    _active_run_id = run_id
    _active_runs_root = runs_root


def active_proxy_run_dir() -> Path | None:
    if not _active_run_id:
        return None
    return _active_runs_root / _active_run_id
