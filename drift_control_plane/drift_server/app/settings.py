from __future__ import annotations

import os


DRIFT_SERVER_HOST = os.environ.get("DRIFT_SERVER_HOST", "127.0.0.1")
DRIFT_SERVER_PORT = int(os.environ.get("DRIFT_SERVER_PORT", "8771"))
