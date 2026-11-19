from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd


# @managed-contract contract_id=drift_algorithm.core.WindowedNumericData level=P1
@dataclass
class WindowedNumericData:
    reference_values: np.ndarray
    current_values: np.ndarray
    metadata: dict[str, Any]
    warnings: list[str]


# @managed-contract contract_id=drift_algorithm.core.prepare_numeric_windows level=P1
def prepare_numeric_windows(
    data: pd.DataFrame,
    *,
    time_col: str,
    value_col: str,
    reference_window: tuple[str, str] | None,
    current_window: tuple[str, str] | None,
) -> WindowedNumericData:
    if reference_window is None or current_window is None:
        raise ValueError("reference_window and current_window are required")
    if time_col not in data.columns:
        raise KeyError(f"missing time column: {time_col}")
    if value_col not in data.columns:
        raise KeyError(f"missing value column: {value_col}")

    ref_start, ref_end = _parse_window(reference_window, "reference_window")
    cur_start, cur_end = _parse_window(current_window, "current_window")
    if max(ref_start, cur_start) <= min(ref_end, cur_end):
        raise ValueError("reference_window and current_window must not overlap")

    frame = data[[time_col, value_col]].copy()
    original_rows = len(frame)
    frame[time_col] = pd.to_datetime(frame[time_col], errors="coerce")
    frame[value_col] = pd.to_numeric(frame[value_col], errors="coerce")
    invalid_time_rows = int(frame[time_col].isna().sum())
    invalid_value_rows = int((~np.isfinite(frame[value_col].to_numpy(dtype=float, na_value=np.nan))).sum())
    frame = frame.dropna(subset=[time_col, value_col])
    frame = frame[np.isfinite(frame[value_col].to_numpy(dtype=float))]
    frame = frame.sort_values(time_col)

    reference_frame = frame[(frame[time_col] >= ref_start) & (frame[time_col] <= ref_end)]
    current_frame = frame[(frame[time_col] >= cur_start) & (frame[time_col] <= cur_end)]

    metadata = {
        "original_rows": original_rows,
        "valid_rows": int(len(frame)),
        "invalid_time_rows": invalid_time_rows,
        "invalid_value_rows": invalid_value_rows,
        "reference_window": [ref_start.isoformat(), ref_end.isoformat()],
        "current_window": [cur_start.isoformat(), cur_end.isoformat()],
        "reference_original_count": int(((data[time_col].pipe(pd.to_datetime, errors="coerce") >= ref_start) & (data[time_col].pipe(pd.to_datetime, errors="coerce") <= ref_end)).sum()),
        "current_original_count": int(((data[time_col].pipe(pd.to_datetime, errors="coerce") >= cur_start) & (data[time_col].pipe(pd.to_datetime, errors="coerce") <= cur_end)).sum()),
        "reference_effective_count": int(len(reference_frame)),
        "current_effective_count": int(len(current_frame)),
    }
    warnings: list[str] = []
    if invalid_time_rows:
        warnings.append(f"dropped {invalid_time_rows} rows with invalid timestamps")
    if invalid_value_rows:
        warnings.append(f"dropped {invalid_value_rows} rows with non-finite numeric values")

    return WindowedNumericData(
        reference_values=reference_frame[value_col].to_numpy(dtype=float),
        current_values=current_frame[value_col].to_numpy(dtype=float),
        metadata=metadata,
        warnings=warnings,
    )


def _parse_window(window: tuple[str, str], name: str) -> tuple[pd.Timestamp, pd.Timestamp]:
    if len(window) != 2:
        raise ValueError(f"{name} must be a (start, end) pair")
    start = pd.to_datetime(window[0], errors="coerce")
    end = pd.to_datetime(window[1], errors="coerce")
    if pd.isna(start) or pd.isna(end):
        raise ValueError(f"{name} contains an unparseable timestamp")
    if start > end:
        raise ValueError(f"{name} start must be <= end")
    return start, end
