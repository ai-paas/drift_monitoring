from __future__ import annotations

import os


TEST_FEEDER_SERVER_HOST = os.environ.get("TEST_FEEDER_SERVER_HOST", "127.0.0.1")
TEST_FEEDER_SERVER_PORT = int(os.environ.get("TEST_FEEDER_SERVER_PORT", "8772"))
