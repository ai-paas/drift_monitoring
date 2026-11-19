from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


CONTROL_PLANE_ROOT = Path(__file__).resolve().parents[2]
PROJECT_ROOT = CONTROL_PLANE_ROOT.parent
TESTING_ROOT = CONTROL_PLANE_ROOT / "testing"
RUNS_ROOT = TESTING_ROOT / "runs"


@dataclass(frozen=True)
class HarnessConfig:
    admin_base_url: str = os.environ.get("ADMIN_SERVER_BASE_URL", "http://127.0.0.1:8770")
    drift_base_url: str = os.environ.get("DRIFT_SERVER_BASE_URL", "http://127.0.0.1:8771")
    test_feeder_base_url: str = os.environ.get("TEST_FEEDER_BASE_URL", "http://127.0.0.1:8772")
    llm_base_url: str = os.environ.get("LLM_INTERPRETATION_BASE_URL", "http://127.0.0.1:8767")
    request_timeout_seconds: float = float(os.environ.get("HARNESS_REQUEST_TIMEOUT_SECONDS", "10"))
    runs_root: Path = RUNS_ROOT
