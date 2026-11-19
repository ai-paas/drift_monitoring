from __future__ import annotations

import json
from typing import Any


JSON_FIELDS = {
    "result_json",
    "payload_json",
    "state_json",
    "params_json",
    "threshold_json",
    "window_config_json",
    "chart_definition_json",
    "payload_adapter_config_json",
}


def row_to_dict(row: Any | None) -> dict[str, Any] | None:
    if row is None:
        return None
    data = dict(row)
    for key in JSON_FIELDS:
        if key in data and isinstance(data[key], str):
            data[key] = json.loads(data[key])
    return data


def rows_to_dicts(rows: list[Any]) -> list[dict[str, Any]]:
    return [row_to_dict(row) or {} for row in rows]
