import sys
from pathlib import Path

import uvicorn

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

uvicorn.run("admin_server.app.main:app", host="127.0.0.1", port=8770)
