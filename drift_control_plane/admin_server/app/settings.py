from __future__ import annotations

import os


DRIFT_SERVER_BASE_URL = os.environ.get("DRIFT_SERVER_BASE_URL", "http://127.0.0.1:8771").rstrip("/")
TEST_FEEDER_BASE_URL = os.environ.get("TEST_FEEDER_BASE_URL", "http://127.0.0.1:8772").rstrip("/")
LLM_INTERPRETATION_BASE_URL = os.environ.get("LLM_INTERPRETATION_BASE_URL", "http://127.0.0.1:8767").rstrip("/")
REPORT_GALLERY_BASE_URL = os.environ.get("REPORT_GALLERY_BASE_URL", "http://127.0.0.1:8765").rstrip("/")
ADMIN_SERVER_HOST = os.environ.get("ADMIN_SERVER_HOST", "127.0.0.1")
ADMIN_SERVER_PORT = int(os.environ.get("ADMIN_SERVER_PORT", "8770"))
REQUEST_TIMEOUT_SECONDS = float(os.environ.get("ADMIN_REQUEST_TIMEOUT_SECONDS", "30"))
