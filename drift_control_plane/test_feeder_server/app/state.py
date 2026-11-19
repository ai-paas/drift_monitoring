from __future__ import annotations

from typing import Any


class FeederState:
    def __init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        self.feeders: dict[str, dict[str, Any]] = {}
        self.dataset_cache: dict[str, dict[str, Any]] = {}
        self.dataset_cache_paths: dict[str, str] = {}
        self.replay_ranges: dict[str, tuple[int, int]] = {}
        self.cursor_indices: dict[str, int] = {}
        self.logical_cursor_time: dict[str, str] = {}
        self.inserted_rows: dict[str, int] = {}
        self.future_rejected_rows: dict[str, int] = {}


state = FeederState()
