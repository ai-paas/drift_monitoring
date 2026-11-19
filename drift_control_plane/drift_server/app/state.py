from __future__ import annotations

from collections import defaultdict
from typing import Any


class DriftState:
    def __init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        self.sources: dict[str, dict[str, Any]] = {}
        self.adapters: dict[str, dict[str, Any]] = {}
        self.method_assignments: dict[str, dict[str, Any]] = {}
        self.analysis_charts: dict[str, dict[str, Any]] = {}
        self.poll_count: defaultdict[str, int] = defaultdict(int)


state = DriftState()
