from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any


@dataclass(frozen=True)
class ClockTick:
    tick_index: int
    logical_now: str


class HarnessClock:
    def __init__(self, start_time: datetime, interval_minutes: int, tick_count: int) -> None:
        if interval_minutes <= 0:
            raise ValueError("intervalMinutes must be positive")
        if tick_count < 0:
            raise ValueError("tickCount must not be negative")
        self.start_time = start_time
        self.interval_minutes = interval_minutes
        self.tick_count = tick_count

    @classmethod
    def from_scenario(cls, scenario: dict[str, Any]) -> "HarnessClock":
        tick = scenario["tick"]
        if tick.get("startTime") and tick.get("endTime") and tick.get("intervalMinutes"):
            start_time = _parse_iso(tick["startTime"])
            end_time = _parse_iso(tick["endTime"])
            interval_minutes = int(tick["intervalMinutes"])
            if end_time <= start_time:
                raise ValueError("tick.endTime must be later than tick.startTime")
            total_minutes = int((end_time - start_time).total_seconds() // 60)
            if total_minutes % interval_minutes != 0:
                raise ValueError("tick duration must be divisible by intervalMinutes")
            return cls(start_time, interval_minutes, total_minutes // interval_minutes)

        start_time = _parse_iso(scenario["feeder"]["startTime"])
        return cls(start_time, int(tick["logicalMinutesPerTick"]), int(tick["tickCount"]))

    @property
    def end_time(self) -> datetime:
        return self.start_time + timedelta(minutes=self.interval_minutes * self.tick_count)

    def ticks(self) -> list[ClockTick]:
        return [
            ClockTick(
                tick_index=index,
                logical_now=_format_iso(self.start_time + timedelta(minutes=index * self.interval_minutes)),
            )
            for index in range(1, self.tick_count + 1)
        ]

    def to_artifact(self) -> dict[str, Any]:
        return {
            "startTime": _format_iso(self.start_time),
            "endTime": _format_iso(self.end_time),
            "intervalMinutes": self.interval_minutes,
            "tickCount": self.tick_count,
            "ticks": [
                {"tickIndex": tick.tick_index, "logicalNow": tick.logical_now}
                for tick in self.ticks()
            ],
        }


def _parse_iso(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _format_iso(value: datetime) -> str:
    return value.replace(microsecond=0).isoformat().replace("+00:00", "Z")
