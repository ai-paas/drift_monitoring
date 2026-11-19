from __future__ import annotations

import math
from typing import Any

from .engine import _path


# @managed-contract contract_id=payload_adapter.transformations.build_derived_rows level=P0
def build_derived_rows(transform: str, fields: list[str], context: dict[str, Any]) -> list[dict[str, Any]]:
    if transform == "bocd_summary":
        return _bocd_summary_rows(fields, context)
    if transform == "bocd_change_heatmap":
        return _bocd_change_heatmap_rows(fields, context)
    if transform == "bocd_run_length_heatmap":
        return _bocd_run_length_heatmap_rows(fields, context)
    if transform == "bocd_stream_series":
        return _bocd_stream_series_rows(fields, context)
    if transform == "bocd_notes":
        return [_bocd_note_row(fields, context)]
    if transform == "adwin_stream_runtime_summary":
        return _adwin_stream_summary_rows(fields, context)
    if transform == "adwin_stream_runtime_series":
        return _adwin_stream_series_rows(fields, context)
    if transform == "adwin_stream_runtime_window":
        return _adwin_stream_window_rows(fields, context)
    if transform == "adwin_stream_runtime_mean":
        return _adwin_stream_mean_rows(fields, context)
    if transform == "adwin_stream_runtime_notes":
        return [_adwin_stream_note_row(fields, context)]
    if transform == "kswin_stream_summary":
        return _kswin_stream_summary_rows(fields, context)
    if transform == "kswin_stream_series":
        return _kswin_stream_series_rows(fields, context)
    if transform == "kswin_ecdf":
        return _kswin_ecdf_rows(fields, context)
    if transform == "kswin_stat_series":
        return _kswin_stat_series_rows(fields, context)
    if transform == "kswin_stream_notes":
        return [_kswin_stream_note_row(fields, context)]
    if transform == "seqdrift_stream_summary":
        return _seqdrift_summary_rows(fields, context)
    if transform == "seqdrift_stream_series":
        return _seqdrift_stream_rows(fields, context)
    if transform == "seqdrift_evidence_series":
        return _seqdrift_evidence_rows(fields, context)
    if transform == "seqdrift_timeline":
        return _seqdrift_timeline_rows(fields, context)
    if transform == "seqdrift_notes":
        return [_seqdrift_note_row(fields, context)]
    if transform == "distshape_summary":
        return _distshape_summary_rows(fields, context)
    if transform == "distshape_ecf":
        return _distshape_ecf_rows(fields, context)
    if transform == "distshape_stat":
        return _distshape_stat_rows(fields, context)
    if transform == "variance_summary":
        return _variance_summary_rows(fields, context)
    if transform == "variance_spread":
        return _variance_spread_rows(fields, context)
    if transform == "variance_bars":
        return _variance_bar_rows(fields, context)
    if transform == "variance_stat":
        return _variance_stat_rows(fields, context)
    if transform == "variance_notes":
        return [_variance_note_row(fields, context)]
    if transform == "event_summary":
        return _summary_rows(fields, context)
    if transform == "analysis_note":
        return [_note_row(fields, context)]
    if transform == "event_timeline":
        return [_row(fields, context, _timeline_value)]
    if transform == "hddm_error_series":
        return _hddm_error_series_rows(fields, context)
    if transform == "hddm_error_summary":
        return _hddm_error_summary_rows(fields, context)
    if transform == "hddm_error_timeline":
        return [_hddm_error_timeline_row(fields, context)]
    if transform == "ddm_error_summary":
        return _ddm_error_summary_rows(fields, context)
    if transform == "ddm_error_series":
        return _ddm_error_series_rows(fields, context)
    if transform == "ddm_error_timeline":
        return _ddm_error_timeline_rows(fields, context)
    if transform == "reference_current_distribution":
        rows = _reference_current_distribution_rows(fields, context)
        if rows:
            return rows
        return [_row(fields, context, _distribution_value)]
    if transform == "projection_points":
        return [
            _row(fields, context, lambda field, ctx: _projection_value(field, ctx, "reference")),
            _row(fields, context, lambda field, ctx: _projection_value(field, ctx, "current")),
        ]
    if transform == "matrix_values":
        return [_row(fields, context, _matrix_value)]
    if transform == "category_contribution":
        psi_rows = _psi_contribution_rows(context)
        if psi_rows:
            return [dict(row, **{field: row.get(field, _category_value(field, context)) for field in fields}) for row in psi_rows]
        return [_row(fields, context, _category_value)]
    if transform == "metric_series":
        return _metric_series_rows(fields, context)
    if transform == "distance_metric_trend":
        return _distance_metric_trend_rows(fields, context)
    if transform == "distance_metric_summary":
        return _distance_metric_summary_rows(fields, context)
    if transform == "distance_metric_ranking":
        return _distance_metric_ranking_rows(fields, context)
    if transform == "text001_summary":
        return _text001_summary_rows(fields, context)
    if transform == "text001_projection":
        return _text001_projection_rows(fields, context)
    if transform == "text001_distance":
        return _text001_distance_rows(fields, context)
    if transform == "text001_topic_mix":
        return _text001_topic_mix_rows(fields, context)
    if transform == "text001_roc":
        return _text001_roc_rows(fields, context)
    if transform == "text001_notes":
        return [_text001_note_row(fields, context)]
    if transform == "expl001_summary":
        return _expl001_summary_rows(fields, context)
    if transform == "expl001_features":
        return _expl001_feature_rows(fields, context)
    if transform == "expl001_distribution":
        return _expl001_distribution_rows(fields, context)
    if transform == "expl001_heatmap":
        return _expl001_heatmap_rows(fields, context)
    if transform == "expl001_notes":
        return [_expl001_note_row(fields, context)]
    if transform == "unc001_summary":
        return _unc001_summary_rows(fields, context)
    if transform == "unc001_confidence":
        return _unc001_confidence_rows(fields, context)
    if transform == "unc001_entropy":
        return _unc001_entropy_rows(fields, context)
    if transform == "unc001_calibration":
        return _unc001_calibration_rows(fields, context)
    if transform == "unc001_notes":
        return [_unc001_note_row(fields, context)]
    if transform == "rep001_summary":
        return _rep_summary_rows(fields, context, "feature")
    if transform == "rep001_heatmap":
        return _rep001_heatmap_rows(fields, context)
    if transform == "rep001_activation":
        return _rep001_activation_rows(fields, context)
    if transform == "rep001_projection":
        return _rep_projection_rows(fields, context)
    if transform == "rep001_notes":
        return [_rep_note_row(fields, context, "Feature map")]
    if transform == "rep003_summary":
        return _rep_summary_rows(fields, context, "graph")
    if transform == "rep003_projection":
        return _rep_projection_rows(fields, context)
    if transform == "rep003_heatmap":
        return _rep003_heatmap_rows(fields, context)
    if transform == "rep003_distance":
        return _rep003_distance_rows(fields, context)
    if transform == "rep003_notes":
        return [_rep_note_row(fields, context, "Graph embedding")]
    if transform == "psi_summary":
        return _psi_summary_rows(fields, context)
    if transform == "psi_notes":
        return [_psi_note_row(fields, context)]
    if transform == "psi_trend":
        return _psi_trend_rows(fields, context)
    if transform == "mmd_summary":
        return _mmd_summary_rows(fields, context)
    if transform == "mmd_trend":
        return _mmd_trend_rows(fields, context)
    if transform == "mmd_null_histogram":
        return _mmd_null_histogram_rows(fields, context)
    if transform == "mmd_notes":
        return [_mmd_note_row(fields, context)]
    if transform == "anom_summary":
        return _anom_summary_rows(fields, context)
    if transform == "anom_score_distribution":
        return _anom_score_distribution_rows(fields, context)
    if transform == "anom_rate_trend":
        return _anom_rate_trend_rows(fields, context)
    if transform == "anom_projection":
        return _anom_projection_rows(fields, context)
    if transform == "anom_notes":
        return [_anom_note_row(fields, context)]
    return [_row(fields, context, _generic_value)]


def _bocd_summary_rows(fields: list[str], context: dict[str, Any]) -> list[dict[str, Any]]:
    measurements = _measurements(context)
    rows = [
        {"label": "max CP probability", "value": _format_float(_bocd_score(context))},
        {"label": "alarm count", "value": str(int(_safe_float(measurements.get("ALARM_COUNT"), 0)))},
        {"label": "processed", "value": str(int(_safe_float(measurements.get("PROCESSED_COUNT"), len(context.get("buckets") or []))))},
        {"label": "decision", "value": _path(context, "$.driftEvent.level", "normal")},
    ]
    return [_select_fields(row, fields) for row in rows]


def _bocd_change_heatmap_rows(fields: list[str], context: dict[str, Any]) -> list[dict[str, Any]]:
    score = max(0.0, min(1.0, _bocd_score(context)))
    peak = _bocd_event_index(context)
    rows: list[dict[str, Any]] = []
    for row_index in range(1, 13):
        row_decay = 1.0 / (1.0 + (row_index - 1) * 0.58)
        values = []
        for time_index in range(1, 33):
            distance = abs(time_index - peak)
            shoulder = max(0.0, 1.0 - distance / 9.0)
            baseline = 0.02 + min(0.12, score * 0.08)
            value = baseline + score * row_decay * shoulder * shoulder
            values.append(round(max(0.0, min(1.0, value)), 4))
        rows.append({"row": row_index, "time": row_index, "values": values})
    return [_select_fields(row, fields) for row in rows]


def _bocd_run_length_heatmap_rows(fields: list[str], context: dict[str, Any]) -> list[dict[str, Any]]:
    score = max(0.0, min(1.0, _bocd_score(context)))
    peak = _bocd_event_index(context)
    rows: list[dict[str, Any]] = []
    for row_index in range(1, 13):
        values = []
        for time_index in range(1, 33):
            expected_row = max(1.0, min(12.0, time_index * 0.38))
            if time_index >= peak:
                expected_row = max(1.0, min(12.0, (time_index - peak + 1) * 0.65))
            ridge = max(0.0, 1.0 - abs(row_index - expected_row) / 3.0)
            reset = max(0.0, 1.0 - abs(time_index - peak) / 4.0) if row_index <= 3 else 0.0
            value = (0.14 + ridge * 0.58 + reset * score * 0.42) * (0.86 + score * 0.14)
            values.append(round(max(0.0, min(1.0, value)), 4))
        rows.append({"row": row_index, "time": row_index, "values": values})
    return [_select_fields(row, fields) for row in rows]


def _bocd_stream_series_rows(fields: list[str], context: dict[str, Any]) -> list[dict[str, Any]]:
    values = _bucket_values(context.get("buckets") or [])
    if not values:
        values = [_bocd_score(context)]
    point_count = 32
    before, after = _before_after(values)
    if before == after:
        before, after = 0.55, min(1.12, 0.55 + max(0.18, _bocd_score(context) * 0.45))
    low = min(before, after)
    high = max(before, after)
    span = high - low or 1.0
    rows = []
    for index, value in enumerate(_interpolated_values(values, point_count, 0.52, 1.08)):
        if len(values) > 1:
            raw_index = min(len(values) - 1, round(index * (len(values) - 1) / (point_count - 1)))
            value = 0.52 + ((values[raw_index] - low) / span) * 0.56
        rows.append({"time": index + 1, "value": round(value, 4)})
    return [_select_fields(row, fields) for row in rows]


def _bocd_note_row(fields: list[str], context: dict[str, Any]) -> dict[str, Any]:
    measurements = _measurements(context)
    score = _bocd_score(context)
    threshold = measurements.get("PREDICTIVE_PROBABILITY_THRESHOLD") or measurements.get("THRESHOLD")
    row = {
        "title": "BOCD 해석",
        "text": (
            f"BOCD posterior 기준 최대 change-point probability는 {score:.3f}이다. "
            f"alarm count는 {int(_safe_float(measurements.get('ALARM_COUNT'), 0))}이고, "
            f"탐지 시점은 {_path(context, '$.driftEvent.eventEnd', '')}이다. "
            "상단 heatmap은 change-point posterior spike, 하단 heatmap은 run-length posterior reset을 표시한다."
        ),
        "legend": [
            {"label": "change-point posterior", "class": "swatch-alarm"},
            {"label": "run-length reset", "class": "swatch-threshold"},
            {"label": f"threshold {threshold}", "class": "swatch-reference"} if threshold is not None else {"label": "BOCD threshold", "class": "swatch-reference"},
        ],
    }
    return _select_fields(row, fields)


def _summary_rows(fields: list[str], context: dict[str, Any]) -> list[dict[str, Any]]:
    fields = fields or ["label", "value"]
    labels = [
        ("event", ""),
        ("level", _path(context, "$.driftEvent.level", "")),
        ("score", _score(context)),
        ("method", _path(context, "$.assignment.runtimeMethodKey", "")),
    ]
    rows: list[dict[str, Any]] = []
    for label, value in labels:
        row = {field: _summary_value(field, label, value, context) for field in fields}
        rows.append(row)
    return rows


def _adwin_stream_summary_rows(fields: list[str], context: dict[str, Any]) -> list[dict[str, Any]]:
    buckets = context.get("buckets") or []
    values = _bucket_values(buckets)
    before, after = _before_after(values)
    delta = after - before
    rows = [
        {"label": "alarm index", "displayValue": str(_alarm_index())},
        {"label": "mean delta", "displayValue": f"{delta:+.2f}"},
        {"label": "score", "displayValue": f"{float(_score(context) or 0):.2f}"},
    ]
    return [_select_fields(row, fields) for row in rows]


def _adwin_stream_series_rows(fields: list[str], context: dict[str, Any]) -> list[dict[str, Any]]:
    buckets = context.get("buckets") or []
    values = _bucket_values(buckets)
    if not values:
        values = [float(_score(context) or 0)]
    point_count = max(36, len(values))
    points = _interpolated_values(values, point_count, 0.31, 0.78)
    rolling: list[float] = []
    for index, value in enumerate(points):
        start = max(0, index - 3)
        window = points[start : index + 1]
        rolling.append(sum(window) / len(window))
    rows = [
        {"time": _runtime_time_index(index, point_count), "value": round(value, 4), "rolling_mean": round(rolling[index], 4)}
        for index, value in enumerate(points)
    ]
    return [_select_fields(row, fields) for row in rows]


def _adwin_stream_window_rows(fields: list[str], context: dict[str, Any]) -> list[dict[str, Any]]:
    alarm = _alarm_index()
    point_count = max(36, len(_bucket_values(context.get("buckets") or [])))
    rows = []
    for index in range(point_count):
        time_index = _runtime_time_index(index, point_count)
        if time_index <= alarm:
            value = 118 + time_index * 2.25
        else:
            value = 62 + (time_index - alarm - 1) * 8.15
        rows.append({"time": time_index, "value": round(value, 2)})
    return [_select_fields(row, fields) for row in rows]


def _adwin_stream_mean_rows(fields: list[str], context: dict[str, Any]) -> list[dict[str, Any]]:
    values = _bucket_values(context.get("buckets") or [])
    before, after = _before_after(values)
    scaled_before, scaled_after = _scaled_pair(before, after, 0.38, 0.68)
    rows = [
        {"label": "before", "value": round(scaled_before, 4), "class": "mean-bar-before"},
        {"label": "after", "value": round(scaled_after, 4), "class": "mean-bar-after"},
        {"label": "delta", "value": round(abs(scaled_after - scaled_before), 4), "class": "delta-bar"},
    ]
    return [_select_fields(row, fields) for row in rows]


def _adwin_stream_note_row(fields: list[str], context: dict[str, Any]) -> dict[str, Any]:
    values = _bucket_values(context.get("buckets") or [])
    before, after = _before_after(values)
    delta = after - before
    row = {
        "title": "해석",
        "text": (
            f"ADWIN이 {context.get('driftEvent', {}).get('eventEnd', '')}에 drift 이벤트를 만들었다. "
            f"bucket 평균은 {before:.2f}에서 {after:.2f}로 변했고, delta는 {delta:+.2f}이다. "
            "시각화는 CHART-STREAM-001 정식 runtime template에 맞춰 stream, window, mean 영역으로 표시한다."
        ),
        "legend": [
            {"label": "stream metric", "class": "swatch-stream"},
            {"label": "rolling mean", "class": "swatch-mean"},
            {"label": "drift alarm", "class": "swatch-alarm"},
            {"label": "운영 기준", "class": "swatch-threshold"},
        ],
    }
    return _select_fields(row, fields)


def _kswin_stream_summary_rows(fields: list[str], context: dict[str, Any]) -> list[dict[str, Any]]:
    measurements = _measurements(context)
    rows = [
        {"label": "alarm count", "displayValue": str(measurements.get("ALARM_COUNT", 0)), "value": measurements.get("ALARM_COUNT", 0)},
        {"label": "KS statistic", "displayValue": f"{float(_score(context) or 0):.3f}", "value": _score(context)},
        {"label": "p-value", "displayValue": _format_float(measurements.get("P_VALUE")), "value": measurements.get("P_VALUE")},
    ]
    return [_select_fields(row, fields) for row in rows]


def _kswin_stream_series_rows(fields: list[str], context: dict[str, Any]) -> list[dict[str, Any]]:
    values = _window_payload_values(context)
    if not values:
        values = [float(_score(context) or 0)]
    point_count = max(36, min(120, len(values)))
    points = _interpolated_values(values, point_count, 0.31, 0.78)
    rows = [
        {"time": _runtime_time_index(index, point_count), "value": round(value, 4)}
        for index, value in enumerate(points)
    ]
    return [_select_fields(row, fields) for row in rows]


def _kswin_ecdf_rows(fields: list[str], context: dict[str, Any]) -> list[dict[str, Any]]:
    period_values = _period_payload_values(context)
    reference = period_values.get("reference", [])
    current = period_values.get("current", [])
    if not reference or not current:
        score = float(_score(context) or 0)
        rows = [{"x": 0.5, "reference": 0.5, "current": min(1.0, 0.5 + score)}]
        return [_select_fields(row, fields) for row in rows]
    combined = reference + current
    low = min(combined)
    high = max(combined)
    if low == high:
        high = low + 1.0
    x_values = [low + ((high - low) * index / 19) for index in range(20)]
    rows = []
    for value in x_values:
        scaled_x = 0.3 + ((value - low) / (high - low) * 0.45)
        rows.append(
            {
                "x": round(scaled_x, 4),
                "reference": round(_ecdf(reference, value), 4),
                "current": round(_ecdf(current, value), 4),
            }
        )
    return [_select_fields(row, fields) for row in rows]


def _kswin_stat_series_rows(fields: list[str], context: dict[str, Any]) -> list[dict[str, Any]]:
    measurements = _measurements(context)
    score = float(_score(context) or measurements.get("KS_STATISTIC") or 0)
    alarm_count = int(measurements.get("ALARM_COUNT") or 0)
    start = max(0.02, score * 0.15)
    rows = []
    for index in range(10):
        value = start + ((score - start) * index / 9)
        if alarm_count and index >= 6:
            value = max(value, score * (0.75 + 0.05 * (index - 6)))
        rows.append({"time": index + 1, "value": round(value, 6)})
    return [_select_fields(row, fields) for row in rows]


def _kswin_stream_note_row(fields: list[str], context: dict[str, Any]) -> dict[str, Any]:
    measurements = _measurements(context)
    row = {
        "title": "해석",
        "text": (
            f"KSWIN이 {context.get('driftEvent', {}).get('eventEnd', '')}에 drift 이벤트를 만들었다. "
            f"KS statistic은 {float(_score(context) or 0):.3f}, "
            f"alarm count는 {measurements.get('ALARM_COUNT', 0)}이다. "
            "reference/current window를 finite stream으로 재생해 최근 window 분포 이동을 표시한다."
        ),
        "legend": [
            {"label": "stream metric", "class": "swatch-stream-green"},
            {"label": "reference window", "class": "swatch-reference"},
            {"label": "current window", "class": "swatch-current-red"},
            {"label": "alarm", "class": "swatch-threshold"},
        ],
    }
    return _select_fields(row, fields)


def _seqdrift_summary_rows(fields: list[str], context: dict[str, Any]) -> list[dict[str, Any]]:
    measurements = _measurements(context)
    rows = [
        {"label": "level", "value": _path(context, "$.driftEvent.level", "drift")},
        {"label": "score", "value": _format_float(_score(context))},
        {"label": "alarms", "value": str(int(_safe_float(measurements.get("ALARM_COUNT"), 0)))},
    ]
    return [_select_fields(row, fields) for row in rows]


def _seqdrift_stream_rows(fields: list[str], context: dict[str, Any]) -> list[dict[str, Any]]:
    period_values = _period_payload_values(context)
    values = period_values.get("reference", []) + period_values.get("current", [])
    if not values:
        values = _window_payload_values(context)
    if not values:
        measurements = _measurements(context)
        values = [
            _safe_float(measurements.get("REFERENCE_MEAN"), 0.0),
            _safe_float(measurements.get("CURRENT_MEAN"), _safe_float(_score(context), 0.0)),
        ]
    point_count = min(120, max(36, len(values)))
    sampled = _sample_values(values, point_count)
    rows = [
        {"time": _runtime_time_index(index, len(sampled)), "value": round(value, 6)}
        for index, value in enumerate(sampled)
    ]
    return [_select_fields(row, fields) for row in rows]


def _seqdrift_evidence_rows(fields: list[str], context: dict[str, Any]) -> list[dict[str, Any]]:
    measurements = _measurements(context)
    alarm_events = measurements.get("ALARM_EVENTS")
    rows: list[dict[str, Any]] = []
    if isinstance(alarm_events, list):
        for event in alarm_events:
            if not isinstance(event, dict):
                continue
            time_index = _seqdrift_axis_from_alarm(event, measurements)
            evidence = _safe_float(event.get("evidence"), 0.0)
            bound = _safe_float(event.get("sequential_bound"), 0.0)
            rows.append(
                {
                    "time": time_index,
                    "evidence": round(evidence, 6),
                    "bound": round(bound, 6),
                    "pointClass": "alarm-point" if evidence >= bound else "evidence-point",
                    "pointRadius": 5 if evidence >= bound else 3.4,
                }
            )
    if not rows:
        evidence = _safe_float(measurements.get("LAST_EVIDENCE") or measurements.get("TEST_STATISTIC"), _safe_float(_score(context), 0.0))
        bound = _safe_float(measurements.get("LAST_BOUND") or measurements.get("SEQUENTIAL_BOUND"), evidence)
        rows = [
            {"time": 1, "evidence": 0.0, "bound": round(bound, 6), "pointClass": "evidence-point", "pointRadius": 3.4},
            {"time": 36, "evidence": round(evidence, 6), "bound": round(bound, 6), "pointClass": "alarm-point", "pointRadius": 5},
        ]
    return [_select_fields(row, fields) for row in rows]


def _seqdrift_timeline_rows(fields: list[str], context: dict[str, Any]) -> list[dict[str, Any]]:
    measurements = _measurements(context)
    reference_size = max(1, int(_safe_float(measurements.get("SAMPLE_SIZE_REFERENCE"), 0)))
    current_size = max(1, int(_safe_float(measurements.get("SAMPLE_SIZE_CURRENT"), 0)))
    processed = max(1, int(_safe_float(measurements.get("PROCESSED_COUNT"), reference_size + current_size)))
    current_start = _runtime_axis_index(reference_size, processed, 36)
    first_alarm = _seqdrift_alarm_axis(measurements, "FIRST_ALARM_INDEX", "FIRST_ALARM_TIME")
    last_alarm = _seqdrift_alarm_axis(measurements, "LAST_ALARM_INDEX", "LAST_ALARM_TIME")
    if first_alarm is None:
        first_alarm = max(current_start, 28)
    if last_alarm is None:
        last_alarm = 36
    rows = [
        {"start": 1, "end": current_start, "role": "monitor", "label": "reference"},
        {"start": current_start, "end": first_alarm, "role": "warning", "label": "current"},
        {"start": first_alarm, "end": max(first_alarm, last_alarm), "role": "drift", "label": "alarm"},
    ]
    return [_select_fields(row, fields) for row in rows if _safe_float(row["end"], 0.0) >= _safe_float(row["start"], 0.0)]


def _seqdrift_note_row(fields: list[str], context: dict[str, Any]) -> dict[str, Any]:
    measurements = _measurements(context)
    variant = str((measurements.get("METHOD_POLICY") or {}).get("variant") or _path(context, "$.analysisChart.payloadAdapterKey", "SeqDrift"))
    score = _safe_float(_score(context), 0.0)
    evidence = _safe_float(measurements.get("LAST_EVIDENCE") or measurements.get("MAX_EVIDENCE"), 0.0)
    bound = _safe_float(measurements.get("LAST_BOUND") or measurements.get("SEQUENTIAL_BOUND"), 0.0)
    alarms = int(_safe_float(measurements.get("ALARM_COUNT"), 0))
    row = {
        "title": "SeqDrift analysis note",
        "text": (
            f"{variant} detected {alarms} sequential alarm(s). "
            f"Score {score:.3f}, latest evidence {evidence:.3f}, bound {bound:.3f}. "
            f"Reference/current mean delta is {_format_signed_float(measurements.get('MEAN_DELTA'))}."
        ),
        "legend": [
            {"label": "stream value", "class": "swatch-stream"},
            {"label": "sequential evidence", "class": "swatch-current-red"},
            {"label": "decision bound", "class": "swatch-threshold"},
            {"label": "alarm window", "class": "swatch-alarm"},
        ],
    }
    return _select_fields(row, fields)


def _distshape_summary_rows(fields: list[str], context: dict[str, Any]) -> list[dict[str, Any]]:
    fields = fields or ["label", "value"]
    measurements = _measurements(context)
    statistic = _safe_float(
        measurements.get("EPPS_SINGLETON_STATISTIC")
        or measurements.get("TEST_STATISTIC")
        or _score(context),
        0.0,
    )
    p_value = measurements.get("P_VALUE")
    reference_size = int(_safe_float(measurements.get("SAMPLE_SIZE_REFERENCE"), 0))
    current_size = int(_safe_float(measurements.get("SAMPLE_SIZE_CURRENT"), 0))
    if reference_size <= 0 or current_size <= 0:
        periods = _period_payload_values(context)
        reference_size = len(periods.get("reference", []))
        current_size = len(periods.get("current", []))
    rows = [
        {"label": "Epps-Singleton", "value": f"{statistic:.2f}", "displayValue": f"{statistic:.2f}"},
        {"label": "p-value", "value": _format_float(p_value), "displayValue": _format_float(p_value)},
        {"label": "samples", "value": f"{reference_size}/{current_size}", "displayValue": f"{reference_size}/{current_size}"},
        {"label": "decision", "value": _path(context, "$.driftEvent.level", "drift"), "displayValue": _path(context, "$.driftEvent.level", "drift")},
    ]
    return [_select_fields(row, fields) for row in rows]


def _distshape_ecf_rows(fields: list[str], context: dict[str, Any]) -> list[dict[str, Any]]:
    fields = fields or ["frequency", "real", "imaginary"]
    periods = _period_payload_values(context)
    reference = periods.get("reference", [])
    current = periods.get("current", [])
    if not reference or not current:
        return []
    t_values = _distshape_t_values(context)
    rows = []
    for t_value in t_values:
        reference_real, reference_imag = _empirical_characteristic_parts(reference, t_value)
        current_real, current_imag = _empirical_characteristic_parts(current, t_value)
        row = {
            "frequency": round(t_value, 4),
            "real": round(abs(current_real - reference_real), 6),
            "imaginary": round(abs(current_imag - reference_imag), 6),
        }
        rows.append(_select_fields(row, fields))
    return rows


def _distshape_stat_rows(fields: list[str], context: dict[str, Any]) -> list[dict[str, Any]]:
    fields = fields or ["label", "value", "valueLabel"]
    ecf_rows = _distshape_ecf_rows(["frequency", "real", "imaginary"], context)
    contribution_rows = []
    for row in ecf_rows:
        value = float(row["real"]) ** 2 + float(row["imaginary"]) ** 2
        contribution_rows.append(
            {
                "label": f"t={float(row['frequency']):.2g}",
                "value": round(value, 6),
                "valueLabel": f"{value:.4f}",
            }
        )
    contribution_rows.sort(key=lambda item: item["value"], reverse=True)
    if not contribution_rows:
        measurements = _measurements(context)
        statistic = _safe_float(measurements.get("EPPS_SINGLETON_STATISTIC") or _score(context), 0.0)
        contribution_rows = [{"label": "statistic", "value": round(statistic, 6), "valueLabel": f"{statistic:.2f}"}]
    return [_select_fields(row, fields) for row in contribution_rows[:4]]


def _variance_summary_rows(fields: list[str], context: dict[str, Any]) -> list[dict[str, Any]]:
    fields = fields or ["label", "value"]
    metrics = _variance_metrics(context)
    rows = [
        {"label": metrics["methodLabel"], "value": _format_float(metrics["statistic"]), "displayValue": _format_float(metrics["statistic"])},
        {"label": "p-value", "value": _format_float(metrics["pValue"]), "displayValue": _format_float(metrics["pValue"])},
        {"label": "variance ratio", "value": f"{metrics['ratio']:.2f}x", "displayValue": f"{metrics['ratio']:.2f}x"},
        {"label": "samples", "value": f"{metrics['referenceSize']}/{metrics['currentSize']}", "displayValue": f"{metrics['referenceSize']}/{metrics['currentSize']}"},
    ]
    return [_select_fields(row, fields) for row in rows]


def _variance_spread_rows(fields: list[str], context: dict[str, Any]) -> list[dict[str, Any]]:
    fields = fields or ["label", "center", "median", "q1", "q3", "low", "high", "mean", "density", "class"]
    periods = _period_payload_values(context)
    reference = periods.get("reference", [])
    current = periods.get("current", [])
    if len(reference) < 2 or len(current) < 2:
        return []
    return _distribution_summary_rows(fields, reference, current)


def _variance_bar_rows(fields: list[str], context: dict[str, Any]) -> list[dict[str, Any]]:
    fields = fields or ["label", "variance", "display", "class"]
    metrics = _variance_metrics(context)
    rows = [
        {
            "label": "기준",
            "variance": round(metrics["referenceVariance"], 6),
            "display": _format_float(metrics["referenceVariance"]),
            "class": "ref-bar",
        },
        {
            "label": "현재",
            "variance": round(metrics["currentVariance"], 6),
            "display": _format_float(metrics["currentVariance"]),
            "class": "cur-bar",
        },
    ]
    return [_select_fields(row, fields) for row in rows]


def _variance_stat_rows(fields: list[str], context: dict[str, Any]) -> list[dict[str, Any]]:
    fields = fields or ["label", "value", "display", "threshold", "class"]
    metrics = _variance_metrics(context)
    row = {
        "label": metrics["methodLabel"],
        "value": round(metrics["statistic"], 6),
        "display": _format_float(metrics["statistic"]),
        "threshold": 1.0,
        "class": "deviation-bar",
    }
    return [_select_fields(row, fields)]


def _variance_note_row(fields: list[str], context: dict[str, Any]) -> dict[str, Any]:
    fields = fields or ["title", "text", "legend"]
    metrics = _variance_metrics(context)
    start = _path(context, "$.driftEvent.eventStart", "")
    end = _path(context, "$.driftEvent.eventEnd", "")
    row = {
        "title": "Variance drift analysis",
        "text": (
            f"{metrics['methodLabel']} statistic {_format_float(metrics['statistic'])}, "
            f"p-value {_format_float(metrics['pValue'])}. "
            f"Reference variance {_format_float(metrics['referenceVariance'])}, "
            f"current variance {_format_float(metrics['currentVariance'])}, "
            f"ratio {metrics['ratio']:.2f}x. "
            f"Analysis window: {start} - {end}."
        ),
        "legend": [
            {"label": "reference variance", "class": "swatch-reference"},
            {"label": "current variance", "class": "swatch-current"},
            {"label": metrics["methodLabel"], "class": "swatch-drift"},
        ],
    }
    return _select_fields(row, fields)


def _metric_series_rows(fields: list[str], context: dict[str, Any]) -> list[dict[str, Any]]:
    fields = fields or ["label", "value"]
    buckets = context.get("buckets") or []
    if not buckets:
        return [_row(fields, context, _metric_value)]
    rows: list[dict[str, Any]] = []
    for bucket in buckets:
        rows.append({field: _metric_value(field, context, bucket) for field in fields})
    return rows


def _distance_metric_trend_rows(fields: list[str], context: dict[str, Any]) -> list[dict[str, Any]]:
    fields = fields or ["window", "distance"]
    score = _distance_score(context)
    threshold = _distance_threshold(context)
    start = max(0.0, min(threshold * 0.45, score * 0.35))
    mid = max(start, min(score, threshold * 0.92))
    lead_in = [
        start,
        max(start, threshold * 0.55),
        max(start, threshold * 0.68),
        mid,
        max(mid, threshold * 1.05),
        max(mid, score * 0.72),
        max(mid, score * 0.86),
        score,
        score,
    ]
    rows = [{"window": index + 1, "distance": round(value, 6)} for index, value in enumerate(lead_in)]
    return [_select_fields(row, fields) for row in rows]


def _distance_metric_summary_rows(fields: list[str], context: dict[str, Any]) -> list[dict[str, Any]]:
    fields = fields or ["label", "value", "displayValue"]
    score = _distance_score(context)
    periods = _period_payload_values(context)
    reference = periods.get("reference", [])
    current = periods.get("current", [])
    mean_shift = _mean_shift(reference, current)
    q90_shift = _quantile_shift(reference, current, 0.9)
    rows = [
        {"label": "Wasserstein", "value": round(score, 6), "displayValue": f"{score:.2f}"},
        {"label": "평균 이동", "value": round(mean_shift, 6), "displayValue": f"{mean_shift:+.2f}"},
        {"label": "상위 10% 이동", "value": round(q90_shift, 6), "displayValue": f"{q90_shift:+.2f}"},
    ]
    return [_select_fields(row, fields) for row in rows]


def _distance_metric_ranking_rows(fields: list[str], context: dict[str, Any]) -> list[dict[str, Any]]:
    fields = fields or ["feature", "distance", "distanceLabel", "class"]
    score = _distance_score(context)
    feature = _path(context, "$.feature.featureLabel", None) or _path(context, "$.feature.featureId", "metric")
    row = {
        "feature": feature,
        "distance": round(score, 6),
        "distanceLabel": f"{score:.2f}",
        "class": "dist-bar-highlight",
    }
    return [_select_fields(row, fields)]


def _text001_summary_rows(fields: list[str], context: dict[str, Any]) -> list[dict[str, Any]]:
    fields = fields or ["label", "value", "displayValue"]
    metrics = _text001_metrics(context)
    rows = [
        {"label": "JS distance", "value": metrics["score"], "displayValue": f"{metrics['score']:.3f}"},
        {"label": "threshold", "value": metrics["threshold"], "displayValue": f"{metrics['threshold']:.3f}"},
        {"label": "max topic delta", "value": metrics["maxDelta"], "displayValue": f"{metrics['maxDelta'] * 100:.1f}pp"},
        {"label": "samples", "value": f"{metrics['referenceSize']}/{metrics['currentSize']}", "displayValue": f"{metrics['referenceSize']}/{metrics['currentSize']}"},
    ]
    return [_select_fields(row, fields) for row in rows]


def _text001_projection_rows(fields: list[str], context: dict[str, Any]) -> list[dict[str, Any]]:
    fields = fields or ["x", "y", "group", "label", "value"]
    metrics = _text001_metrics(context)
    shift = max(0.25, min(1.4, metrics["score"] * 3.2))
    top_delta = metrics["topTopics"][0]["delta"] if metrics["topTopics"] else 0.0
    rows = [
        {"x": round(-0.55 - shift * 0.2, 6), "y": round(-0.12, 6), "group": "baseline", "label": "baseline", "value": metrics["score"]},
        {"x": round(-0.25 - shift * 0.1, 6), "y": round(0.16, 6), "group": "baseline", "label": "baseline", "value": metrics["score"]},
        {"x": round(-0.08, 6), "y": round(-0.28, 6), "group": "baseline", "label": "baseline", "value": metrics["score"]},
        {"x": round(0.28 + shift, 6), "y": round(0.12 + top_delta, 6), "group": "current", "label": "current", "value": metrics["score"]},
        {"x": round(0.55 + shift, 6), "y": round(0.34 + top_delta * 0.5, 6), "group": "current", "label": "current", "value": metrics["score"]},
        {"x": round(0.82 + shift, 6), "y": round(-0.08 - top_delta * 0.4, 6), "group": "current", "label": "current", "value": metrics["score"]},
    ]
    return [_select_fields(row, fields) for row in rows]


def _text001_distance_rows(fields: list[str], context: dict[str, Any]) -> list[dict[str, Any]]:
    fields = fields or ["time", "value"]
    metrics = _text001_metrics(context)
    threshold = metrics["threshold"]
    score = metrics["score"]
    values = [
        max(0.0, min(score, threshold * 0.35)),
        max(0.0, min(score, threshold * 0.65)),
        max(0.0, min(score, threshold * 0.95)),
        max(score, threshold * 1.05),
        score,
    ]
    rows = [{"time": index + 1, "value": round(value, 6)} for index, value in enumerate(values)]
    return [_select_fields(row, fields) for row in rows]


def _text001_topic_mix_rows(fields: list[str], context: dict[str, Any]) -> list[dict[str, Any]]:
    fields = fields or ["category", "topic1", "topic2", "topic3", "topic3_label"]
    metrics = _text001_metrics(context)
    topics = metrics["topTopics"][:3]
    while len(topics) < 3:
        topics.append({"topic": f"topic{len(topics) + 1}", "reference": 0.0, "current": 0.0, "delta": 0.0})
    rows = []
    for category, key in (("baseline", "reference"), ("current", "current")):
        row = {"category": category}
        for index, topic in enumerate(topics, start=1):
            row[f"topic{index}"] = round(float(topic[key]), 6)
        row["topic3_label"] = f"{topics[0]['topic']} {topics[0]['delta'] * 100:+.1f}pp"
        rows.append(_select_fields(row, fields))
    return rows


def _text001_roc_rows(fields: list[str], context: dict[str, Any]) -> list[dict[str, Any]]:
    fields = fields or ["time", "value", "label"]
    score = _text001_metrics(context)["score"]
    lift = max(0.08, min(0.35, score))
    rows = [
        {"time": 0.0, "value": 0.0, "label": "separation"},
        {"time": 0.3, "value": round(min(1.0, 0.3 + lift * 0.7), 6), "label": "separation"},
        {"time": 0.6, "value": round(min(1.0, 0.6 + lift * 0.85), 6), "label": "separation"},
        {"time": 1.0, "value": 1.0, "label": "separation"},
    ]
    return [_select_fields(row, fields) for row in rows]


def _text001_note_row(fields: list[str], context: dict[str, Any]) -> dict[str, Any]:
    fields = fields or ["title", "text", "legend"]
    metrics = _text001_metrics(context)
    top = metrics["topTopics"][0] if metrics["topTopics"] else {"topic": "topic", "reference": 0.0, "current": 0.0, "delta": 0.0}
    row = {
        "title": "Topic distribution shift analysis",
        "text": (
            f"TOPIC_DISTRIBUTION_SHIFT detected drift: JS distance {metrics['score']:.3f} "
            f"exceeds threshold {metrics['threshold']:.3f}. "
            f"{top['topic']} changed from {top['reference'] * 100:.1f}% to {top['current'] * 100:.1f}% "
            f"({top['delta'] * 100:+.1f}pp), with {metrics['referenceSize']}/{metrics['currentSize']} samples."
        ),
        "legend": [
            {"label": "baseline", "class": "swatch-base"},
            {"label": "current", "class": "swatch-current"},
            {"label": "topic shift", "class": "swatch-topic"},
        ],
    }
    return _select_fields(row, fields)


def _text001_metrics(context: dict[str, Any]) -> dict[str, Any]:
    measurements = _measurements(context)
    score = _safe_float(
        measurements.get("JENSEN_SHANNON_DISTANCE")
        or measurements.get("COSINE_DISTANCE")
        or measurements.get("TEST_STATISTIC"),
        _safe_float(_score(context), 0.0),
    )
    threshold = _safe_float(_path(context, "$.runtimeResult.metrics.threshold", None) or measurements.get("THRESHOLD"), 0.1)
    ref_props = measurements.get("TOPIC_PROPORTIONS_REFERENCE")
    cur_props = measurements.get("TOPIC_PROPORTIONS_CURRENT")
    if not isinstance(ref_props, dict):
        ref_props = {}
    if not isinstance(cur_props, dict):
        cur_props = {}
    topics = sorted(set(ref_props) | set(cur_props))
    top_topics = [
        {
            "topic": str(topic),
            "reference": _safe_float(ref_props.get(topic), 0.0),
            "current": _safe_float(cur_props.get(topic), 0.0),
            "delta": _safe_float(cur_props.get(topic), 0.0) - _safe_float(ref_props.get(topic), 0.0),
        }
        for topic in topics
    ]
    top_topics.sort(key=lambda item: abs(item["delta"]), reverse=True)
    max_delta = _safe_float(measurements.get("TOPIC_PROPORTION_DELTA"), abs(top_topics[0]["delta"]) if top_topics else 0.0)
    return {
        "score": score,
        "threshold": threshold,
        "maxDelta": max_delta,
        "referenceSize": int(_safe_float(measurements.get("SAMPLE_SIZE_REFERENCE"), 0)),
        "currentSize": int(_safe_float(measurements.get("SAMPLE_SIZE_CURRENT"), 0)),
        "topTopics": top_topics,
    }


def _expl001_summary_rows(fields: list[str], context: dict[str, Any]) -> list[dict[str, Any]]:
    fields = fields or ["label", "value", "displayValue"]
    metrics = _expl001_metrics(context)
    top = metrics["topFeature"]
    rows = [
        {"label": "SHAP distance", "value": round(metrics["score"], 6), "displayValue": f"{metrics['score']:.3f}"},
        {"label": "threshold", "value": round(metrics["threshold"], 6), "displayValue": f"{metrics['threshold']:.3f}"},
        {"label": "top shift", "value": top.get("feature", ""), "displayValue": str(top.get("feature", ""))},
        {"label": "samples", "value": f"{metrics['referenceSize']}/{metrics['currentSize']}", "displayValue": f"{metrics['referenceSize']}/{metrics['currentSize']}"},
    ]
    if metrics["pValue"] is not None:
        rows[1] = {"label": "p-value", "value": round(metrics["pValue"], 6), "displayValue": f"{metrics['pValue']:.3g}"}
    return [_select_fields(row, fields) for row in rows]


def _expl001_feature_rows(fields: list[str], context: dict[str, Any]) -> list[dict[str, Any]]:
    fields = fields or ["feature", "baseline", "current"]
    rows = [
        {
            "feature": item["feature"],
            "baseline": round(item["reference"], 6),
            "current": round(item["current"], 6),
            "delta": round(item["delta"], 6),
            "rank_delta": item["rankDelta"],
            "score": round(item["score"], 6),
        }
        for item in _expl001_metrics(context)["features"]
    ]
    return [_select_fields(row, fields) for row in rows]


def _expl001_distribution_rows(fields: list[str], context: dict[str, Any]) -> list[dict[str, Any]]:
    fields = fields or ["shap", "baseline", "current"]
    metrics = _expl001_metrics(context)
    top = metrics["topFeature"]
    reference = float(top.get("reference", 0.0))
    current = float(top.get("current", 0.0))
    delta = current - reference
    center = max(-0.36, min(0.36, delta))
    rows = []
    for index in range(10):
        shap = -0.36 + (0.72 * index / 9)
        baseline_density = 40.0 * math.exp(-((shap + reference * 0.18) ** 2) / 0.032)
        current_density = 40.0 * math.exp(-((shap - center) ** 2) / 0.032)
        rows.append(
            {
                "shap": round(shap, 6),
                "baseline": round(baseline_density, 6),
                "current": round(current_density, 6),
            }
        )
    return [_select_fields(row, fields) for row in rows]


def _expl001_heatmap_rows(fields: list[str], context: dict[str, Any]) -> list[dict[str, Any]]:
    fields = fields or ["class", "values"]
    metrics = _expl001_metrics(context)
    features = metrics["features"]
    rows = []
    for label, multiplier in (("reference rank", 1.0), ("current rank", 1.0), ("rank delta", 0.5)):
        values = []
        for item in features:
            if label == "reference rank":
                values.append(round(item["reference"], 6))
            elif label == "current rank":
                values.append(round(item["current"], 6))
            else:
                values.append(round(abs(item["delta"]) + abs(item["rankDelta"]) * multiplier, 6))
        rows.append({"class": label, "values": values})
    return [_select_fields(row, fields) for row in rows]


def _expl001_note_row(fields: list[str], context: dict[str, Any]) -> dict[str, Any]:
    fields = fields or ["title", "text", "legend"]
    metrics = _expl001_metrics(context)
    top = metrics["topFeature"]
    second = metrics["features"][1] if len(metrics["features"]) > 1 else top
    decision = "exceeds" if metrics["score"] >= metrics["threshold"] else "is below"
    row = {
        "title": "SHAP importance drift analysis",
        "text": (
            f"{metrics['methodLabel']} detected explanation drift: score {metrics['score']:.3f} "
            f"{decision} threshold {metrics['threshold']:.3f}. "
            f"{top['feature']} changed from {top['reference'] * 100:.1f}% to {top['current'] * 100:.1f}% "
            f"({top['delta'] * 100:+.1f}pp, rank {top['referenceRank']}->{top['currentRank']}); "
            f"{second['feature']} changed by {second['delta'] * 100:+.1f}pp."
        ),
        "legend": [
            {"label": "baseline", "class": "swatch-base"},
            {"label": "current", "class": "swatch-current-red"},
            {"label": "rank shift", "class": "swatch-shift"},
        ],
    }
    return _select_fields(row, fields)


def _expl001_metrics(context: dict[str, Any]) -> dict[str, Any]:
    measurements = _measurements(context)
    raw_features = measurements.get("FEATURE_IMPORTANCE_OR_RANK")
    features: list[dict[str, Any]] = []
    if isinstance(raw_features, list):
        for index, item in enumerate(raw_features):
            if not isinstance(item, dict):
                continue
            reference_rank = int(_safe_float(item.get("reference_rank"), index + 1))
            current_rank = int(_safe_float(item.get("current_rank") or item.get("rank"), index + 1))
            reference = _safe_float(item.get("reference_importance") or item.get("baseline"), 0.0)
            current = _safe_float(item.get("current_importance") or item.get("current"), 0.0)
            features.append(
                {
                    "feature": str(item.get("feature") or f"feature_{index + 1}"),
                    "reference": reference,
                    "current": current,
                    "delta": current - reference,
                    "referenceRank": reference_rank,
                    "currentRank": current_rank,
                    "rankDelta": int(_safe_float(item.get("rank_delta"), current_rank - reference_rank)),
                    "score": _safe_float(item.get("score"), abs(current - reference)),
                }
            )
    if not features:
        feature = str(_path(context, "$.feature.featureId", "feature"))
        score = _safe_float(_score(context), 0.0)
        features.append(
            {
                "feature": feature,
                "reference": max(0.0, 0.5 - score / 2),
                "current": min(1.0, 0.5 + score / 2),
                "delta": score,
                "referenceRank": 1,
                "currentRank": 1,
                "rankDelta": 0,
                "score": score,
            }
        )
    features.sort(key=lambda item: (abs(item["rankDelta"]), abs(item["delta"])), reverse=True)
    score = _safe_float(
        measurements.get("SHAP_DRIFT_DISTANCE")
        or measurements.get("TEST_STATISTIC")
        or _path(context, "$.runtimeResult.metrics.testStatistic", None),
        _safe_float(_score(context), 0.0),
    )
    threshold = _safe_float(_path(context, "$.runtimeResult.metrics.threshold", None) or measurements.get("THRESHOLD"), 0.05)
    sample_size = measurements.get("SAMPLE_SIZE")
    reference_size = measurements.get("REFERENCE_SAMPLE_SIZE")
    current_size = measurements.get("CURRENT_SAMPLE_SIZE")
    if isinstance(sample_size, dict):
        reference_size = sample_size.get("reference", reference_size)
        current_size = sample_size.get("current", current_size)
    method_key = str(_path(context, "$.assignment.methodVariantKey", "") or _path(context, "$.analysisChart.payloadAdapterKey", ""))
    return {
        "score": score,
        "threshold": threshold,
        "pValue": None if measurements.get("P_VALUE") is None else _safe_float(measurements.get("P_VALUE"), 0.0),
        "referenceSize": int(_safe_float(reference_size, 0)),
        "currentSize": int(_safe_float(current_size, 0)),
        "features": features,
        "topFeature": features[0],
        "methodLabel": "SHAP distribution test" if "SHAP_VALUE_DISTRIBUTION_TEST" in method_key else "Global importance rank shift",
    }


def _unc001_summary_rows(fields: list[str], context: dict[str, Any]) -> list[dict[str, Any]]:
    fields = fields or ["label", "value"]
    metrics = _unc001_metrics(context)
    rows = [
        {"label": "KS statistic", "value": f"{metrics['score']:.3f}"},
        {"label": "p-value", "value": f"{metrics['pValue']:.3g}"},
        {"label": "mean delta", "value": f"{metrics['meanDelta']:+.3f}"},
        {"label": "samples", "value": f"{metrics['referenceSize']}/{metrics['currentSize']}"},
    ]
    return [_select_fields(row, fields) for row in rows]


def _unc001_confidence_rows(fields: list[str], context: dict[str, Any]) -> list[dict[str, Any]]:
    fields = fields or ["confidence", "baseline", "current"]
    metrics = _unc001_metrics(context)
    values = _unc001_period_values(context, metrics)
    reference = values["reference"]
    current = values["current"]
    rows = []
    for index in range(14):
        center = 0.05 + (0.91 * index / 13)
        rows.append(
            {
                "confidence": round(center, 6),
                "baseline": _unc001_bin_count(reference, center, 0.04),
                "current": _unc001_bin_count(current, center, 0.04),
            }
        )
    return [_select_fields(row, fields) for row in rows]


def _unc001_entropy_rows(fields: list[str], context: dict[str, Any]) -> list[dict[str, Any]]:
    fields = fields or ["time", "value"]
    metrics = _unc001_metrics(context)
    start = metrics["referenceMean"]
    end = metrics["currentMean"]
    if start == end:
        end = start + metrics["score"] * 0.1
    rows = []
    for index in range(12):
        ratio = index / 11
        value = start + (end - start) * ratio
        rows.append({"time": index + 1, "value": round(value, 6)})
    return [_select_fields(row, fields) for row in rows]


def _unc001_calibration_rows(fields: list[str], context: dict[str, Any]) -> list[dict[str, Any]]:
    fields = fields or ["time", "value"]
    metrics = _unc001_metrics(context)
    delta = max(-0.35, min(0.35, metrics["meanDelta"]))
    rows = []
    for index, time_value in enumerate([0.1, 0.3, 0.5, 0.7, 0.9]):
        value = max(0.0, min(1.0, time_value - delta * 0.35 + (index - 2) * 0.015))
        rows.append({"time": time_value, "value": round(value, 6)})
    return [_select_fields(row, fields) for row in rows]


def _unc001_note_row(fields: list[str], context: dict[str, Any]) -> dict[str, Any]:
    fields = fields or ["title", "text", "legend"]
    metrics = _unc001_metrics(context)
    decision = "<= alpha" if metrics["pValue"] <= metrics["threshold"] else "> alpha"
    row = {
        "title": "Uncertainty drift analysis",
        "text": (
            f"{metrics['methodLabel']} detected drift: KS statistic {metrics['score']:.3f}, "
            f"p-value {metrics['pValue']:.3g} {decision} {metrics['threshold']:.3f}. "
            f"Mean {metrics['metricLabel']} changed from {metrics['referenceMean']:.3f} to {metrics['currentMean']:.3f} "
            f"({metrics['meanDelta']:+.3f}), with {metrics['referenceSize']}/{metrics['currentSize']} samples."
        ),
        "legend": [
            {"label": "reference", "class": "swatch-base"},
            {"label": "current", "class": "swatch-current"},
            {"label": "uncertainty drift", "class": "swatch-uncertainty"},
        ],
    }
    return _select_fields(row, fields)


def _unc001_metrics(context: dict[str, Any]) -> dict[str, Any]:
    measurements = _measurements(context)
    method_key = str(_path(context, "$.assignment.methodVariantKey", "") or _path(context, "$.analysisChart.payloadAdapterKey", ""))
    score = _safe_float(
        measurements.get("TEST_STATISTIC") or _path(context, "$.runtimeResult.metrics.testStatistic", None),
        _safe_float(_score(context), 0.0),
    )
    threshold = _safe_float(_path(context, "$.runtimeResult.metrics.threshold", None) or measurements.get("THRESHOLD"), 0.05)
    p_value = _safe_float(
        measurements.get("P_VALUE") if measurements.get("P_VALUE") is not None else _path(context, "$.runtimeResult.metrics.pValue", None),
        1.0,
    )
    reference_mean = _safe_float(measurements.get("UNCERTAINTY_MEAN_REFERENCE"), 0.0)
    current_mean = _safe_float(measurements.get("UNCERTAINTY_MEAN_CURRENT"), reference_mean)
    mean_delta = _safe_float(measurements.get("UNCERTAINTY_MEAN_DELTA"), current_mean - reference_mean)
    sample_size = measurements.get("SAMPLE_SIZE")
    reference_size = measurements.get("SAMPLE_SIZE_REFERENCE")
    current_size = measurements.get("SAMPLE_SIZE_CURRENT")
    if isinstance(sample_size, dict):
        reference_size = sample_size.get("reference", reference_size)
        current_size = sample_size.get("current", current_size)
    is_confidence = "SOFTMAX_CONFIDENCE_DRIFT" in method_key
    return {
        "methodLabel": "Softmax confidence drift" if is_confidence else "Entropy drift",
        "metricLabel": "confidence" if is_confidence else "uncertainty",
        "score": score,
        "threshold": threshold,
        "pValue": p_value,
        "referenceMean": reference_mean,
        "currentMean": current_mean,
        "meanDelta": mean_delta,
        "referenceSize": int(_safe_float(reference_size, 0)),
        "currentSize": int(_safe_float(current_size, 0)),
    }


def _unc001_period_values(context: dict[str, Any], metrics: dict[str, Any]) -> dict[str, list[float]]:
    values: dict[str, list[float]] = {"reference": [], "current": []}
    method_key = str(_path(context, "$.assignment.methodVariantKey", "") or _path(context, "$.analysisChart.payloadAdapterKey", ""))
    use_confidence = "SOFTMAX_CONFIDENCE_DRIFT" in method_key
    for bucket in context.get("buckets") or []:
        payload = bucket.get("payload") or {}
        if not isinstance(payload, dict):
            continue
        for row in payload.get("values", []):
            if not isinstance(row, dict):
                continue
            period = str(row.get("period") or "")
            if period not in values:
                continue
            features = row.get("features") if isinstance(row.get("features"), dict) else {}
            if use_confidence:
                value = features.get("annotation_confidence")
            else:
                confidence = _safe_float(features.get("annotation_confidence"), 0.0)
                noise = _safe_float(features.get("label_noise_probability"), 0.0)
                value = max(0.0, min(1.0, (1.0 - confidence) * 0.65 + noise * 0.35))
            try:
                values[period].append(float(value))
            except (TypeError, ValueError):
                continue
    if not values["reference"]:
        values["reference"] = [metrics["referenceMean"]]
    if not values["current"]:
        values["current"] = [metrics["currentMean"]]
    return values


def _unc001_bin_count(values: list[float], center: float, half_width: float) -> int:
    low = center - half_width
    high = center + half_width
    return sum(1 for value in values if low <= value < high)


def _rep_metrics(context: dict[str, Any]) -> dict[str, Any]:
    measurements = _measurements(context)
    metrics = context.get("runtimeResult", {}).get("metrics") or {}
    score = _safe_float(
        measurements.get("FEATURE_MAP_DRIFT_SCORE")
        or measurements.get("GRAPH_EMBEDDING_DRIFT_SCORE")
        or measurements.get("TEST_STATISTIC")
        or metrics.get("testStatistic")
        or _score(context),
        0.0,
    )
    threshold = _safe_float(measurements.get("THRESHOLD") or metrics.get("threshold"), 0.1)
    p_value = _safe_float(
        measurements.get("P_VALUE") if measurements.get("P_VALUE") is not None else metrics.get("pValue"),
        1.0,
    )
    sample_size = measurements.get("SAMPLE_SIZE")
    reference_size = measurements.get("SAMPLE_SIZE_REFERENCE")
    current_size = measurements.get("SAMPLE_SIZE_CURRENT")
    if isinstance(sample_size, dict):
        reference_size = sample_size.get("reference", reference_size)
        current_size = sample_size.get("current", current_size)
    feature_columns = list(measurements.get("FEATURE_COLUMNS") or [])
    values = _rep_bucket_values(context, feature_columns)
    feature_stats = _rep_feature_stats(values, feature_columns)
    return {
        "score": score,
        "threshold": threshold,
        "pValue": p_value,
        "referenceSize": int(_safe_float(reference_size, 0)),
        "currentSize": int(_safe_float(current_size, 0)),
        "featureColumns": feature_columns,
        "featureStats": feature_stats,
        "centroidShift": _safe_float(measurements.get("CENTROID_SHIFT"), score),
        "cosineDistance": _safe_float(measurements.get("COSINE_DISTANCE"), 0.0),
    }


def _rep_bucket_values(context: dict[str, Any], feature_columns: list[str]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for bucket in context.get("buckets") or []:
        payload = bucket.get("payload") or {}
        if not isinstance(payload, dict):
            continue
        columns = feature_columns or list(payload.get("featureColumns") or [])
        for item in payload.get("values", []):
            if not isinstance(item, dict):
                continue
            features = item.get("features") or {}
            rows.append(
                {
                    "period": item.get("period"),
                    "features": {column: _safe_float(features.get(column), 0.0) for column in columns},
                }
            )
    return rows


def _rep_feature_stats(values: list[dict[str, Any]], feature_columns: list[str]) -> list[dict[str, Any]]:
    stats: list[dict[str, Any]] = []
    for column in feature_columns:
        reference = [row["features"].get(column, 0.0) for row in values if row.get("period") == "reference"]
        current = [row["features"].get(column, 0.0) for row in values if row.get("period") == "current"]
        ref_mean = sum(reference) / len(reference) if reference else 0.0
        cur_mean = sum(current) / len(current) if current else ref_mean
        stats.append({"feature": column, "referenceMean": ref_mean, "currentMean": cur_mean, "delta": cur_mean - ref_mean})
    stats.sort(key=lambda item: abs(item["delta"]), reverse=True)
    return stats


def _rep_summary_rows(fields: list[str], context: dict[str, Any], mode: str) -> list[dict[str, Any]]:
    fields = fields or ["label", "value", "displayValue"]
    metrics = _rep_metrics(context)
    score_label = "graph MMD" if mode == "graph" else "feature-map MMD"
    rows = [
        {"label": score_label, "value": round(metrics["score"], 6), "displayValue": f"{metrics['score']:.3f}"},
        {"label": "threshold", "value": round(metrics["threshold"], 6), "displayValue": f"{metrics['threshold']:.3f}"},
        {"label": "p-value", "value": round(metrics["pValue"], 6), "displayValue": f"{metrics['pValue']:.3g}"},
        {"label": "samples", "value": f"{metrics['referenceSize']}/{metrics['currentSize']}", "displayValue": f"{metrics['referenceSize']}/{metrics['currentSize']}"},
    ]
    return [_select_fields(row, fields) for row in rows]


def _rep001_heatmap_rows(fields: list[str], context: dict[str, Any]) -> list[dict[str, Any]]:
    fields = fields or ["layer", "values"]
    metrics = _rep_metrics(context)
    deltas = [abs(item["delta"]) for item in metrics["featureStats"]] or [metrics["score"]]
    max_delta = max(deltas + [metrics["score"], 0.000001])
    normalized = [round(min(1.0, value / max_delta), 6) for value in deltas]
    while len(normalized) < 4:
        normalized.append(round(min(1.0, metrics["score"]), 6))
    rows = [
        {"layer": "reference-current", "values": normalized[:4]},
        {"layer": "mmd-score", "values": [round(min(1.0, metrics["score"]), 6), round(min(1.0, metrics["threshold"]), 6), round(metrics["pValue"], 6), 0.0]},
    ]
    return [_select_fields(row, fields) for row in rows]


def _rep001_activation_rows(fields: list[str], context: dict[str, Any]) -> list[dict[str, Any]]:
    fields = fields or ["bin", "baseline", "current"]
    metrics = _rep_metrics(context)
    values = _rep_bucket_values(context, metrics["featureColumns"])
    column = "activation" if "activation" in metrics["featureColumns"] else (metrics["featureColumns"][0] if metrics["featureColumns"] else "")
    reference = [row["features"].get(column, 0.0) for row in values if row.get("period") == "reference"]
    current = [row["features"].get(column, 0.0) for row in values if row.get("period") == "current"]
    all_values = reference + current
    if not all_values:
        return []
    low = min(all_values)
    high = max(all_values)
    width = (high - low) / 8 if high > low else 1.0
    rows = []
    for index in range(8):
        start = low + width * index
        end = high if index == 7 else start + width
        rows.append(
            {
                "bin": f"b{index + 1}",
                "baseline": sum(1 for value in reference if start <= value <= end),
                "current": sum(1 for value in current if start <= value <= end),
            }
        )
    return [_select_fields(row, fields) for row in rows]


def _rep_projection_rows(fields: list[str], context: dict[str, Any]) -> list[dict[str, Any]]:
    fields = fields or ["x", "y", "group"]
    metrics = _rep_metrics(context)
    values = _rep_bucket_values(context, metrics["featureColumns"])
    x_col = metrics["featureColumns"][0] if metrics["featureColumns"] else ""
    y_col = metrics["featureColumns"][1] if len(metrics["featureColumns"]) > 1 else x_col
    rows = []
    counters = {"reference": 0, "current": 0}
    for row in values:
        period = str(row.get("period") or "")
        if period not in counters or counters[period] >= 24:
            continue
        counters[period] += 1
        rows.append(
            {
                "x": round(row["features"].get(x_col, 0.0), 6),
                "y": round(row["features"].get(y_col, 0.0), 6),
                "group": "baseline" if period == "reference" else "current",
            }
        )
    return [_select_fields(row, fields) for row in rows]


def _rep003_heatmap_rows(fields: list[str], context: dict[str, Any]) -> list[dict[str, Any]]:
    fields = fields or ["nodeGroup", "values"]
    metrics = _rep_metrics(context)
    top_stats = metrics["featureStats"][:2] or [{"feature": "embedding", "delta": metrics["score"]}]
    rows = []
    for stat in top_stats:
        base = abs(stat["delta"])
        rows.append(
            {
                "nodeGroup": stat["feature"],
                "values": [
                    round(min(1.0, base * 0.35), 6),
                    round(min(1.0, base * 0.65), 6),
                    round(min(1.0, max(base, metrics["score"])), 6),
                ],
            }
        )
    return [_select_fields(row, fields) for row in rows]


def _rep003_distance_rows(fields: list[str], context: dict[str, Any]) -> list[dict[str, Any]]:
    fields = fields or ["time", "value"]
    metrics = _rep_metrics(context)
    threshold = metrics["threshold"]
    score = metrics["score"]
    lead_in = [threshold * 0.25, threshold * 0.45, threshold * 0.75, max(threshold * 1.1, score * 0.45), max(threshold * 1.25, score * 0.72), score]
    rows = [{"time": index + 1, "value": round(value, 6)} for index, value in enumerate(lead_in)]
    return [_select_fields(row, fields) for row in rows]


def _rep_note_row(fields: list[str], context: dict[str, Any], label: str) -> dict[str, Any]:
    fields = fields or ["title", "text", "legend"]
    metrics = _rep_metrics(context)
    top = metrics["featureStats"][0] if metrics["featureStats"] else {"feature": "embedding", "delta": 0.0, "referenceMean": 0.0, "currentMean": 0.0}
    row = {
        "title": f"{label} drift analysis",
        "text": (
            f"{label} drift detected: score {metrics['score']:.3f} exceeds threshold {metrics['threshold']:.3f} "
            f"with p-value {metrics['pValue']:.3g}. {top['feature']} mean changed from "
            f"{top['referenceMean']:.3f} to {top['currentMean']:.3f} ({top['delta']:+.3f}); "
            f"samples {metrics['referenceSize']}/{metrics['currentSize']}."
        ),
        "legend": [
            {"label": "reference", "class": "swatch-reference"},
            {"label": "current", "class": "swatch-current-red"},
            {"label": "drift score", "class": "swatch-mmd"},
        ],
    }
    return _select_fields(row, fields)


def _psi_summary_rows(fields: list[str], context: dict[str, Any]) -> list[dict[str, Any]]:
    fields = fields or ["label", "value", "displayValue"]
    score = _safe_float(_score(context), 0.0)
    threshold = _psi_threshold(context)
    contribution_rows = _psi_contribution_rows(context)
    top = contribution_rows[0] if contribution_rows else {}
    reference_size, current_size = _psi_sample_sizes(context)
    rows = [
        {"label": "PSI", "value": round(score, 6), "displayValue": _format_float(score)},
        {"label": "threshold", "value": round(threshold, 6), "displayValue": f"{threshold:.3f}"},
        {"label": "top bin", "value": top.get("label", ""), "displayValue": top.get("label", "")},
        {"label": "samples", "value": f"{reference_size}/{current_size}", "displayValue": f"{reference_size}/{current_size}"},
    ]
    return [_select_fields(row, fields) for row in rows]


def _psi_note_row(fields: list[str], context: dict[str, Any]) -> dict[str, Any]:
    fields = fields or ["title", "text", "legend"]
    score = _safe_float(_score(context), 0.0)
    threshold = _psi_threshold(context)
    contribution_rows = _psi_contribution_rows(context)
    top = contribution_rows[0] if contribution_rows else {}
    top_label = str(top.get("label") or "top bin")
    top_display = str(top.get("displayValue") or _format_float(top.get("value")))
    start = _path(context, "$.driftEvent.eventStart", "")
    end = _path(context, "$.driftEvent.eventEnd", "")
    row = {
        "title": "PSI population shift analysis",
        "text": (
            f"PSI {_format_float(score)} exceeds threshold {threshold:.3f}. "
            f"The largest contribution is {top_label} ({top_display}). "
            f"Analysis window: {start} - {end}."
        ),
        "legend": [
            {"label": "reference proportion", "class": "swatch-reference"},
            {"label": "current proportion", "class": "swatch-current-red"},
            {"label": "PSI contribution", "class": "swatch-divergence"},
            {"label": "threshold", "class": "swatch-threshold"},
        ],
    }
    return _select_fields(row, fields)


def _hddm_error_series_rows(fields: list[str], context: dict[str, Any]) -> list[dict[str, Any]]:
    fields = fields or ["time", "diff", "error"]
    buckets = context.get("buckets") or []
    if not buckets:
        buckets = [{}]
    score = _safe_float(_score(context), 0.0)
    rows: list[dict[str, Any]] = []
    for index, bucket in enumerate(buckets):
        time_index = _runtime_axis_index(index, len(buckets), 32)
        error = _bucket_error_value(bucket, score)
        previous = _bucket_error_value(buckets[index - 1], error) if index > 0 else error
        row = {
            "time": time_index,
            "timestamp": bucket.get("bucketEnd") or bucket.get("bucketStart") or "",
            "diff": abs(error - previous) if index > 0 else score,
            "error": error,
            "value": error,
            "score": score,
        }
        rows.append(_select_fields(row, fields))
    return rows


def _hddm_error_summary_rows(fields: list[str], context: dict[str, Any]) -> list[dict[str, Any]]:
    fields = fields or ["label", "value"]
    metrics = context.get("runtimeResult", {}).get("metrics") or {}
    measurements = metrics.get("measurements") if isinstance(metrics.get("measurements"), dict) else {}
    score = _safe_float(metrics.get("testStatistic"), _safe_float(_score(context), 0.0))
    drift_bound = _safe_float(measurements.get("HOEFFDING_DRIFT_BOUND"), _safe_float(metrics.get("threshold"), 0.0))
    rows = [
        {"label": "level", "value": _path(context, "$.driftEvent.level", "")},
        {"label": "score", "value": f"{score:.4f}"},
        {"label": "drift bound", "value": f"{drift_bound:.4f}"},
    ]
    return [_select_fields(row, fields) for row in rows]


def _hddm_error_timeline_row(fields: list[str], context: dict[str, Any]) -> dict[str, Any]:
    fields = fields or ["start", "end", "label", "role"]
    level = _path(context, "$.driftEvent.level", "drift")
    row = {
        "start": 26,
        "end": 32,
        "label": level,
        "role": level,
        "eventStart": _path(context, "$.driftEvent.eventStart", ""),
        "eventEnd": _path(context, "$.driftEvent.eventEnd", ""),
    }
    return _select_fields(row, fields)


def _ddm_error_summary_rows(fields: list[str], context: dict[str, Any]) -> list[dict[str, Any]]:
    fields = fields or ["label", "value"]
    metrics = context.get("runtimeResult", {}).get("metrics") or {}
    current_error = _safe_float(metrics.get("errorRate"), _safe_float(_score(context), 0.0))
    previous_error = _safe_float(metrics.get("previousErrorRate"), 0.0)
    delta = _safe_float(_score(context), max(0.0, current_error - previous_error))
    threshold = _error_rate_threshold(context)
    rows = [
        {"label": "현재 오류율", "value": f"{current_error:.3f}"},
        {"label": "이전 오류율", "value": f"{previous_error:.3f}"},
        {"label": "변화량", "value": f"+{delta:.3f}"},
        {"label": "기준", "value": f"{threshold:.3f}"},
    ]
    return [_select_fields(row, fields) for row in rows]


def _ddm_error_series_rows(fields: list[str], context: dict[str, Any]) -> list[dict[str, Any]]:
    fields = fields or ["time", "error", "margin"]
    buckets = context.get("buckets") or []
    if not buckets:
        buckets = [{}]
    threshold = _error_rate_threshold(context)
    score = _safe_float(_score(context), 0.0)
    rows: list[dict[str, Any]] = []
    for index, bucket in enumerate(buckets):
        time_index = _runtime_axis_index(index, len(buckets), 32)
        error = _bucket_error_value(bucket, score)
        row = {
            "time": time_index,
            "timestamp": bucket.get("bucketEnd") or bucket.get("bucketStart") or "",
            "error": error,
            "value": error,
            "score": score,
            "margin": round(error - threshold, 6),
        }
        rows.append(_select_fields(row, fields))
    return rows


def _ddm_error_timeline_rows(fields: list[str], context: dict[str, Any]) -> list[dict[str, Any]]:
    fields = fields or ["start", "end", "label", "role"]
    buckets = context.get("buckets") or []
    event_index = _event_bucket_index(context, buckets)
    start_index = max(0, event_index - 1)
    end_axis = _runtime_axis_index(event_index, len(buckets), 32)
    start_axis = _runtime_axis_index(start_index, len(buckets), 32)
    level = _path(context, "$.driftEvent.level", "drift")
    rows = [
        {"start": 1, "end": start_axis, "label": "normal", "role": "normal"},
        {
            "start": start_axis,
            "end": end_axis,
            "label": level,
            "role": level,
            "eventStart": _path(context, "$.driftEvent.eventStart", ""),
            "eventEnd": _path(context, "$.driftEvent.eventEnd", ""),
        },
        {"start": end_axis, "end": 32, "label": "normal", "role": "normal"},
    ]
    return [_select_fields(row, fields) for row in rows]


def _psi_trend_rows(fields: list[str], context: dict[str, Any]) -> list[dict[str, Any]]:
    fields = fields or ["window", "psi"]
    score = float(_score(context) or 0)
    threshold = _psi_threshold(context)
    lead_in = [
        threshold * 0.35,
        threshold * 0.48,
        threshold * 0.63,
        threshold * 0.82,
        threshold * 1.05,
        max(threshold * 1.2, score * 0.55),
        score,
    ]
    rows = [{"window": index + 1, "psi": round(value, 6)} for index, value in enumerate(lead_in)]
    return [_select_fields(row, fields) for row in rows]


def _mmd_summary_rows(fields: list[str], context: dict[str, Any]) -> list[dict[str, Any]]:
    fields = fields or ["label", "value", "displayValue"]
    measurements = _measurements(context)
    score = _safe_float(measurements.get("MMD_STATISTIC") or _score(context), 0.0)
    threshold = _mmd_threshold(context)
    reference_size = int(_safe_float(measurements.get("SAMPLE_SIZE_REFERENCE"), 0))
    current_size = int(_safe_float(measurements.get("SAMPLE_SIZE_CURRENT"), 0))
    bandwidth = measurements.get("KERNEL_BANDWIDTH")
    rows = [
        {"label": "MMD", "value": round(score, 6), "displayValue": f"{score:.3f}"},
        {"label": "threshold", "value": round(threshold, 6), "displayValue": f"{threshold:.3f}"},
        {"label": "samples", "value": f"{reference_size}/{current_size}", "displayValue": f"{reference_size}/{current_size}"},
        {"label": "bandwidth", "value": _safe_float(bandwidth, 0.0), "displayValue": _format_float(bandwidth)},
    ]
    return [_select_fields(row, fields) for row in rows]


def _mmd_trend_rows(fields: list[str], context: dict[str, Any]) -> list[dict[str, Any]]:
    fields = fields or ["window", "mmd"]
    score = _safe_float(_score(context), 0.0)
    threshold = _mmd_threshold(context)
    lead_in = [
        max(0.0, threshold * 0.18),
        max(0.0, threshold * 0.28),
        max(0.0, threshold * 0.42),
        max(0.0, threshold * 0.62),
        max(0.0, threshold * 0.84),
        max(threshold * 1.04, score * 0.45),
        max(threshold * 1.12, score * 0.62),
        max(threshold * 1.20, score * 0.78),
        max(threshold * 1.28, score * 0.90),
        score,
    ]
    rows = [{"window": index + 1, "mmd": round(value, 6)} for index, value in enumerate(lead_in)]
    return [_select_fields(row, fields) for row in rows]


def _mmd_null_histogram_rows(fields: list[str], context: dict[str, Any]) -> list[dict[str, Any]]:
    fields = fields or ["x0", "x1", "count", "class"]
    threshold = _mmd_threshold(context)
    upper = max(threshold * 1.8, 0.18)
    step = upper / 9
    counts = [3, 8, 15, 23, 28, 22, 14, 8, 4]
    rows = []
    for index, count in enumerate(counts):
        x0 = index * step
        x1 = (index + 1) * step
        rows.append(
            {
                "x0": round(x0, 6),
                "x1": round(x1, 6),
                "count": count,
                "class": "tail-bar" if x0 >= threshold else "null-bar",
            }
        )
    return [_select_fields(row, fields) for row in rows]


def _mmd_note_row(fields: list[str], context: dict[str, Any]) -> dict[str, Any]:
    fields = fields or ["title", "text", "legend"]
    measurements = _measurements(context)
    score = _safe_float(measurements.get("MMD_STATISTIC") or _score(context), 0.0)
    threshold = _mmd_threshold(context)
    reference_size = int(_safe_float(measurements.get("SAMPLE_SIZE_REFERENCE"), 0))
    current_size = int(_safe_float(measurements.get("SAMPLE_SIZE_CURRENT"), 0))
    start = _path(context, "$.driftEvent.eventStart", "")
    end = _path(context, "$.driftEvent.eventEnd", "")
    row = {
        "title": "MMD analysis",
        "text": (
            f"Linear-time MMD score {score:.3f} exceeds threshold {threshold:.3f}. "
            f"Reference/current samples: {reference_size}/{current_size}. "
            f"Analysis window: {start} - {end}."
        ),
        "legend": [
            {"label": "reference embedding", "class": "swatch-reference"},
            {"label": "current embedding", "class": "swatch-current-red"},
            {"label": "MMD score", "class": "swatch-mmd"},
            {"label": "threshold", "class": "swatch-threshold"},
        ],
    }
    return _select_fields(row, fields)


def _mmd_threshold(context: dict[str, Any]) -> float:
    metrics = context.get("runtimeResult", {}).get("metrics") or {}
    params = context.get("assignment", {}).get("params") or {}
    return _safe_float(metrics.get("threshold") or params.get("threshold"), 0.1)


def _anom_metrics(context: dict[str, Any]) -> dict[str, Any]:
    measurements = _measurements(context)
    params = context.get("assignment", {}).get("params") or {}
    metrics = context.get("runtimeResult", {}).get("metrics") or {}
    anomaly_rate = _safe_float(
        measurements.get("OUTLIER_OR_ANOMALY_RATE")
        or measurements.get("BOUNDARY_VIOLATION_RATE")
        or _score(context),
        0.0,
    )
    rate_threshold = _safe_float(
        measurements.get("ANOMALY_RATE_THRESHOLD")
        or metrics.get("threshold")
        or params.get("anomaly_rate_threshold"),
        0.1,
    )
    score_threshold = _safe_float(measurements.get("THRESHOLD") or params.get("threshold"), 0.0)
    mean_score = _safe_float(measurements.get("ANOMALY_SCORE"), 0.0)
    max_score = _safe_float(measurements.get("MAX_ANOMALY_SCORE"), max(score_threshold, mean_score, 1.0))
    return {
        "anomalyRate": anomaly_rate,
        "rateThreshold": rate_threshold,
        "scoreThreshold": score_threshold,
        "meanScore": mean_score,
        "maxScore": max_score,
        "anomalyCount": int(_safe_float(measurements.get("ANOMALY_COUNT"), 0.0)),
        "referenceSize": int(_safe_float(measurements.get("SAMPLE_SIZE_REFERENCE"), 0.0)),
        "currentSize": int(_safe_float(measurements.get("SAMPLE_SIZE_CURRENT"), 0.0)),
    }


def _anom_summary_rows(fields: list[str], context: dict[str, Any]) -> list[dict[str, Any]]:
    fields = fields or ["label", "value"]
    metrics = _anom_metrics(context)
    rows = [
        {"label": "outlier rate", "value": f"{metrics['anomalyRate']:.3f}"},
        {"label": "rate threshold", "value": f"{metrics['rateThreshold']:.3f}"},
        {"label": "outlier count", "value": str(metrics["anomalyCount"])},
        {"label": "samples", "value": f"{metrics['referenceSize']}/{metrics['currentSize']}"},
    ]
    return [_select_fields(row, fields) for row in rows]


def _anom_score_distribution_rows(fields: list[str], context: dict[str, Any]) -> list[dict[str, Any]]:
    fields = fields or ["score", "baseline", "current"]
    metrics = _anom_metrics(context)
    threshold = max(metrics["scoreThreshold"], 0.5)
    high = max(metrics["maxScore"] * 1.12, threshold * 1.25, metrics["meanScore"] * 1.35, 1.0)
    baseline_center = max(threshold * 0.35, high * 0.18)
    current_center = max(metrics["meanScore"], threshold * 0.55)
    baseline_width = max(high * 0.12, 0.15)
    current_width = max(high * 0.18, 0.18)
    rows: list[dict[str, Any]] = []
    for index in range(24):
        score = high * index / 23
        baseline = math.exp(-0.5 * ((score - baseline_center) / baseline_width) ** 2)
        current_main = math.exp(-0.5 * ((score - current_center) / current_width) ** 2)
        current_tail = metrics["anomalyRate"] * 1.4 * math.exp(
            -0.5 * ((score - max(threshold, current_center)) / max(current_width * 0.9, 0.1)) ** 2
        )
        rows.append(
            _select_fields(
                {
                    "score": round(score, 6),
                    "baseline": round(baseline, 6),
                    "current": round(current_main + current_tail, 6),
                },
                fields,
            )
        )
    return rows


def _anom_rate_trend_rows(fields: list[str], context: dict[str, Any]) -> list[dict[str, Any]]:
    fields = fields or ["time", "rate"]
    metrics = _anom_metrics(context)
    rate = metrics["anomalyRate"]
    threshold = metrics["rateThreshold"]
    start = max(0.0, min(rate * 0.25, threshold * 0.45))
    values = [
        start,
        max(start, threshold * 0.45),
        max(start, threshold * 0.65),
        max(start, threshold * 0.85),
        max(start, threshold * 1.02),
        max(start, rate * 0.82),
        rate,
    ]
    rows = [{"time": index + 1, "rate": round(value, 6)} for index, value in enumerate(values)]
    return [_select_fields(row, fields) for row in rows]


def _anom_projection_rows(fields: list[str], context: dict[str, Any]) -> list[dict[str, Any]]:
    fields = fields or ["x", "y", "group"]
    metrics = _anom_metrics(context)
    rows: list[dict[str, Any]] = []
    for index in range(16):
        rows.append(_select_fields({"x": round(-0.9 + (index % 4) * 0.22, 6), "y": round(-0.45 + (index // 4) * 0.18, 6), "group": "baseline"}, fields))
        rows.append(_select_fields({"x": round(0.15 + (index % 4) * 0.24, 6), "y": round(0.05 + (index // 4) * 0.18, 6), "group": "current"}, fields))
    outlier_points = max(3, min(14, round(metrics["anomalyRate"] * 60)))
    for index in range(outlier_points):
        rows.append(_select_fields({"x": round(1.35 + (index % 5) * 0.18, 6), "y": round(0.68 + (index // 5) * 0.22, 6), "group": "outlier"}, fields))
    return rows


def _anom_note_row(fields: list[str], context: dict[str, Any]) -> dict[str, Any]:
    fields = fields or ["title", "text", "legend"]
    metrics = _anom_metrics(context)
    start = _path(context, "$.driftEvent.eventStart", "")
    end = _path(context, "$.driftEvent.eventEnd", "")
    row = {
        "title": "OCDD anomaly drift analysis",
        "text": (
            f"Outlier rate {metrics['anomalyRate']:.3f} exceeds threshold {metrics['rateThreshold']:.3f}. "
            f"Current window has {metrics['anomalyCount']} outliers across {metrics['currentSize']} current rows. "
            f"Analysis window: {start} - {end}."
        ),
        "legend": [
            {"label": "baseline normal region", "class": "swatch-reference"},
            {"label": "current sample", "class": "swatch-current-red"},
            {"label": "current outlier", "class": "swatch-outlier"},
            {"label": "rate threshold", "class": "swatch-threshold"},
        ],
    }
    return _select_fields(row, fields)


def _note_row(fields: list[str], context: dict[str, Any]) -> dict[str, Any]:
    default_fields = fields or ["title", "label", "value", "text"]
    return {field: _note_value(field, context) for field in default_fields}


def _row(fields: list[str], context: dict[str, Any], value_fn: Any) -> dict[str, Any]:
    default_fields = fields or ["label", "value"]
    return {field: value_fn(field, context) for field in default_fields}


def _summary_value(field: str, label: str, value: Any, context: dict[str, Any]) -> Any:
    if field == "label":
        return label
    if field in {"value", "displayValue", "valueLabel"}:
        return value
    if field == "decision":
        return _path(context, "$.driftEvent.level", "")
    return _generic_value(field, context)


def _note_value(field: str, context: dict[str, Any]) -> Any:
    if field == "title":
        return "Analysis note"
    if field == "label":
        return _path(context, "$.driftEvent.level", "event")
    if field == "value":
        return _score(context)
    if field == "text":
        method = _path(context, "$.assignment.runtimeMethodKey", "drift method")
        level = _path(context, "$.driftEvent.level", "event")
        score = _safe_float(_score(context), 0.0)
        start = _path(context, "$.driftEvent.eventStart", "")
        end = _path(context, "$.driftEvent.eventEnd", "")
        return (
            f"{method} detected {level} with score {score:.3f}. "
            f"Analysis window: {start} - {end}."
        )
    return _generic_value(field, context)


def _reference_current_distribution_rows(fields: list[str], context: dict[str, Any]) -> list[dict[str, Any]]:
    period_values = _period_payload_values(context)
    reference = period_values.get("reference", [])
    current = period_values.get("current", [])
    if len(reference) < 2 or len(current) < 2:
        return []
    field_set = set(fields)
    if field_set & {"x0", "x1", "start", "end", "intersection", "observed", "count"}:
        return _histogram_distribution_rows(fields, reference, current)
    if field_set & {"q1", "q3", "median", "low", "high", "mean", "center", "density"} and "x" not in field_set:
        return _distribution_summary_rows(fields, reference, current)
    if field_set & {"x", "reference", "current", "baseline", "exact", "approx"}:
        return _density_distribution_rows(fields, reference, current)
    return []


def _density_distribution_rows(fields: list[str], reference: list[float], current: list[float]) -> list[dict[str, Any]]:
    low, high = _distribution_domain(reference, current)
    points = 25
    x_values = [low + (high - low) * index / (points - 1) for index in range(points)]
    reference_density = _kernel_density(reference, x_values)
    current_density = _kernel_density(current, x_values)
    max_density = max(reference_density + current_density + [1.0])
    scale = 0.42 / max_density
    rows = []
    for index, x_value in enumerate(x_values):
        row = {
            "x": round(x_value, 4),
            "reference": round(reference_density[index] * scale, 6),
            "baseline": round(reference_density[index] * scale, 6),
            "current": round(current_density[index] * scale, 6),
            "exact": round(reference_density[index] * scale, 6),
            "approx": round(current_density[index] * scale, 6),
            "difference": round(abs(current_density[index] - reference_density[index]) * scale, 6),
        }
        rows.append(_select_fields(row, fields))
    return rows


def _histogram_distribution_rows(fields: list[str], reference: list[float], current: list[float]) -> list[dict[str, Any]]:
    low, high = _distribution_domain(reference, current)
    bin_count = 12
    width = (high - low) / bin_count
    rows = []
    for index in range(bin_count):
        x0 = low + width * index
        x1 = high if index == bin_count - 1 else x0 + width
        ref_count = _bin_count(reference, x0, x1, include_right=index == bin_count - 1)
        cur_count = _bin_count(current, x0, x1, include_right=index == bin_count - 1)
        ref_value = ref_count / max(1, len(reference))
        cur_value = cur_count / max(1, len(current))
        row = {
            "x0": round(x0, 4),
            "x1": round(x1, 4),
            "start": round(x0, 4),
            "end": round(x1, 4),
            "mid": round((x0 + x1) / 2, 4),
            "reference": round(ref_value, 6),
            "baseline": round(ref_value, 6),
            "current": round(cur_value, 6),
            "intersection": round(min(ref_value, cur_value), 6),
            "count": ref_count + cur_count,
            "observed": cur_count,
        }
        rows.append(_select_fields(row, fields))
    return rows


def _distribution_summary_rows(fields: list[str], reference: list[float], current: list[float]) -> list[dict[str, Any]]:
    return [
        _select_fields(_distribution_summary_row("reference", reference), fields),
        _select_fields(_distribution_summary_row("current", current), fields),
    ]


def _distribution_summary_row(label: str, values: list[float]) -> dict[str, Any]:
    sorted_values = sorted(values)
    low = sorted_values[0]
    high = sorted_values[-1]
    q1 = _quantile(sorted_values, 0.25)
    median = _quantile(sorted_values, 0.5)
    q3 = _quantile(sorted_values, 0.75)
    mean = sum(sorted_values) / len(sorted_values)
    domain_low, domain_high = _distribution_domain(values, values)
    x_values = [domain_low + (domain_high - domain_low) * index / 8 for index in range(9)]
    density = _kernel_density(values, x_values)
    max_density = max(density + [1.0])
    density_points = [
        [round(x_value, 4), round(value / max_density, 6)]
        for x_value, value in zip(x_values, density)
    ]
    return {
        "label": "기준" if label == "reference" else "현재",
        "group": label,
        "class": "ref-fill" if label == "reference" else "cur-fill",
        "low": round(low, 6),
        "high": round(high, 6),
        "q1": round(q1, 6),
        "median": round(median, 6),
        "q3": round(q3, 6),
        "mean": round(mean, 6),
        "center": round(mean, 6),
        "density": density_points,
    }


def _distribution_domain(reference: list[float], current: list[float]) -> tuple[float, float]:
    values = reference + current
    low = min(values)
    high = max(values)
    if low == high:
        return low - 0.5, high + 0.5
    pad = (high - low) * 0.12
    return low - pad, high + pad


def _kernel_density(values: list[float], x_values: list[float]) -> list[float]:
    if not values:
        return [0.0 for _ in x_values]
    low = min(values)
    high = max(values)
    span = high - low
    bandwidth = max(span / 8, 0.1)
    normalizer = len(values) * bandwidth
    densities = []
    for x_value in x_values:
        total = 0.0
        for value in values:
            z = (x_value - value) / bandwidth
            total += pow(2.718281828459045, -0.5 * z * z)
        densities.append(total / normalizer)
    return densities


def _bin_count(values: list[float], x0: float, x1: float, include_right: bool = False) -> int:
    if include_right:
        return sum(1 for value in values if x0 <= value <= x1)
    return sum(1 for value in values if x0 <= value < x1)


def _quantile(sorted_values: list[float], q: float) -> float:
    if not sorted_values:
        return 0.0
    if len(sorted_values) == 1:
        return sorted_values[0]
    pos = (len(sorted_values) - 1) * q
    lower = int(pos)
    upper = min(lower + 1, len(sorted_values) - 1)
    weight = pos - lower
    return sorted_values[lower] * (1 - weight) + sorted_values[upper] * weight


def _mean_shift(reference: list[float], current: list[float]) -> float:
    if not reference or not current:
        return 0.0
    reference_mean = sum(reference) / len(reference)
    current_mean = sum(current) / len(current)
    return current_mean - reference_mean


def _quantile_shift(reference: list[float], current: list[float], q: float) -> float:
    if not reference or not current:
        return 0.0
    return _quantile(sorted(current), q) - _quantile(sorted(reference), q)


def _timeline_value(field: str, context: dict[str, Any]) -> Any:
    if field in {"time", "end"}:
        return _path(context, "$.driftEvent.eventEnd", "")
    if field == "start":
        return _path(context, "$.driftEvent.eventStart", "")
    if field == "window":
        return f"{_path(context, '$.driftEvent.eventStart', '')} - {_path(context, '$.driftEvent.eventEnd', '')}"
    if field == "role":
        return "current"
    if field == "label":
        return _path(context, "$.driftEvent.level", "")
    return _generic_value(field, context)


def _distribution_value(field: str, context: dict[str, Any]) -> Any:
    if field in {"reference", "baseline", "exact"}:
        return 10.0
    if field in {"current", "approx"}:
        return 10.0 + float(_score(context) or 0)
    if field in {"difference", "delta", "diff", "absDelta", "deltaLabel"}:
        return float(_score(context) or 0)
    if field in {"x", "x0", "start", "mid"}:
        return 0.0
    if field in {"x1", "end"}:
        return 1.0
    if field in {"intersection", "count", "observed"}:
        return 1
    if field in {"density", "q1", "median", "q3", "low", "high", "mean", "center"}:
        return float(_score(context) or 0)
    return _generic_value(field, context)


def _projection_value(field: str, context: dict[str, Any], group: str) -> Any:
    if field == "x":
        return 0.2 if group == "reference" else 0.8
    if field == "y":
        return 0.3 if group == "reference" else 0.7
    if field in {"group", "class", "kind"}:
        return group
    if field in {"feature", "id", "segment"}:
        return _path(context, "$.feature.featureId", "feature")
    if field in {"value", "count", "spread"}:
        return _score(context)
    return _generic_value(field, context)


def _matrix_value(field: str, context: dict[str, Any]) -> Any:
    if field == "values":
        return [[0.1, 0.2], [0.3, float(_score(context) or 0)]]
    if field in {"row", "class", "method"}:
        return _path(context, "$.assignment.runtimeMethodKey", "method")
    if field in {"active", "direction"}:
        return _path(context, "$.driftEvent.level", "drift")
    return _generic_value(field, context)


def _category_value(field: str, context: dict[str, Any]) -> Any:
    psi_rows = _psi_contribution_rows(context)
    if psi_rows:
        row = psi_rows[0]
        if field in row:
            return row[field]
    if field in {"label", "category", "feature", "metric", "bin", "topic3_label"}:
        return _path(context, "$.feature.featureLabel", _path(context, "$.feature.featureId", "metric"))
    if field in {"value", "displayValue", "valueLabel", "contribution", "residual"}:
        return _score(context)
    if field in {"delta", "absDelta", "deltaLabel", "distance", "distanceLabel", "psi", "kl", "js", "hellinger", "mmd", "lsdd", "t2", "energy", "tv", "linf", "hinc"}:
        return _score(context)
    return _generic_value(field, context)


def _metric_value(field: str, context: dict[str, Any], bucket: dict[str, Any] | None = None) -> Any:
    if bucket is None:
        bucket = {}
    if field in {"time", "window"}:
        return bucket.get("bucketEnd") or _path(context, "$.driftEvent.eventEnd", "")
    if field in {"psi"}:
        return _score(context)
    if field in {"value", "raw", "rolling_mean", "running_mean", "stat", "score", "distance", "error", "rate", "bound", "evidence", "llr", "metric"}:
        return bucket.get("v", _score(context))
    if field in {"secondary_value", "retained", "overall", "recent", "gap", "margin", "cplus", "cminus", "ewma", "ph"}:
        return _score(context)
    if field in {"label", "pointClass"}:
        return _path(context, "$.driftEvent.level", "drift")
    if field == "pointRadius":
        return 4
    return _generic_value(field, context)


def _generic_value(field: str, context: dict[str, Any]) -> Any:
    if field in {"label", "eventLabel", "title"}:
        return _path(context, "$.driftEvent.level", "drift")
    if field in {"event", "event_id"}:
        return _path(context, "$.driftEvent.eventId", "")
    if field in {"event_type", "role", "status", "track"}:
        return _path(context, "$.driftEvent.level", "drift")
    if field in {"time", "end"}:
        return _path(context, "$.driftEvent.eventEnd", "")
    if field == "start":
        return _path(context, "$.driftEvent.eventStart", "")
    if field in {"value", "displayValue", "score", "threshold", "confidence", "entropy", "variance", "nonevent"}:
        return _score(context)
    if field == "values":
        return [[float(_score(context) or 0)]]
    return _score(context)


def _score(context: dict[str, Any]) -> Any:
    return _path(context, "$.driftEvent.score", 0)


def _bocd_score(context: dict[str, Any]) -> float:
    measurements = _measurements(context)
    return _safe_float(
        measurements.get("MAX_CHANGE_POINT_PROBABILITY")
        or measurements.get("TEST_STATISTIC")
        or _path(context, "$.runtimeResult.metrics.testStatistic", None)
        or _score(context),
        0.0,
    )


def _bocd_event_index(context: dict[str, Any]) -> int:
    measurements = _measurements(context)
    first_alarm = _safe_float(measurements.get("FIRST_ALARM_TIME"), 0.0)
    processed = max(1.0, _safe_float(measurements.get("PROCESSED_COUNT"), 32.0))
    if first_alarm > 0:
        return max(1, min(32, round(1 + (first_alarm - 1) * 31 / max(1.0, processed - 1))))
    alarm_events = measurements.get("ALARM_EVENTS")
    if isinstance(alarm_events, list) and alarm_events:
        first = alarm_events[0]
        if isinstance(first, dict):
            event_index = _safe_float(first.get("time") or first.get("index") or first.get("t"), 0.0)
            if event_index > 0:
                return max(1, min(32, round(1 + (event_index - 1) * 31 / max(1.0, processed - 1))))
    buckets = context.get("buckets") or []
    event_end = str(_path(context, "$.driftEvent.eventEnd", ""))
    if buckets and event_end:
        for index, bucket in enumerate(buckets):
            if str(bucket.get("bucketEnd") or "") == event_end:
                return max(1, min(32, round(1 + index * 31 / max(1, len(buckets) - 1))))
    return 18


def _measurements(context: dict[str, Any]) -> dict[str, Any]:
    measurements = _path(context, "$.runtimeResult.metrics.measurements", {})
    return measurements if isinstance(measurements, dict) else {}


def _variance_metrics(context: dict[str, Any]) -> dict[str, Any]:
    measurements = _measurements(context)
    periods = _period_payload_values(context)
    reference = periods.get("reference", [])
    current = periods.get("current", [])
    reference_variance = _sample_variance(reference)
    current_variance = _sample_variance(current)
    ratio = current_variance / reference_variance if reference_variance > 0 else 0.0
    method_key = str(_path(context, "$.runtimeResult.metrics.measurements.VARIANT_ID", "") or "")
    if not method_key:
        method_key = str(_path(context, "$.assignment.methodVariantKey", "") or "")
    if not method_key:
        adapter_key = str(_path(context, "$.analysisChart.payloadAdapterKey", "") or "")
        if adapter_key.startswith("auto__") and "__" in adapter_key[6:]:
            method_key = adapter_key[6:].split("__", 1)[0]
    method_label = _variance_method_label(method_key)
    statistic = _safe_float(
        measurements.get("F_STATISTIC")
        or measurements.get("LEVENE_STATISTIC")
        or measurements.get("TEST_STATISTIC")
        or _path(context, "$.runtimeResult.metrics.testStatistic", None)
        or _score(context),
        0.0,
    )
    p_value = (
        measurements.get("P_VALUE")
        or _path(context, "$.runtimeResult.metrics.pValue", None)
    )
    return {
        "methodLabel": method_label,
        "statistic": statistic,
        "pValue": p_value,
        "referenceVariance": reference_variance,
        "currentVariance": current_variance,
        "ratio": ratio,
        "referenceSize": len(reference),
        "currentSize": len(current),
    }


def _variance_method_label(method_key: str) -> str:
    normalized = method_key.upper()
    if normalized == "F_TEST_EQUAL_VARIANCE":
        return "F-test"
    if normalized == "BROWN_FORSYTHE_MEDIAN_CENTER":
        return "Brown-Forsythe"
    if normalized == "LEVENE_MEAN_CENTER":
        return "Levene"
    if normalized == "TRIMMED_MEAN_LEVENE":
        return "trimmed-mean Levene"
    return "variance test"


def _sample_variance(values: list[float]) -> float:
    if len(values) < 2:
        return 0.0
    mean = sum(values) / len(values)
    return sum((value - mean) ** 2 for value in values) / (len(values) - 1)


def _window_payload_values(context: dict[str, Any]) -> list[float]:
    values: list[float] = []
    for rows in _period_payload_values(context).values():
        values.extend(rows)
    return values


def _period_payload_values(context: dict[str, Any]) -> dict[str, list[float]]:
    periods: dict[str, list[float]] = {"reference": [], "current": []}
    for bucket in context.get("buckets") or []:
        payload = bucket.get("payload") or {}
        if not isinstance(payload, dict):
            continue
        for row in payload.get("values", []):
            period = str(row.get("period") or "")
            if period not in periods:
                continue
            try:
                periods[period].append(float(row.get("value")))
            except (TypeError, ValueError):
                continue
    return periods


def _distshape_t_values(context: dict[str, Any]) -> list[float]:
    measurements = _measurements(context)
    raw_t_points = measurements.get("T_POINTS")
    t_points: list[float] = []
    if isinstance(raw_t_points, list):
        for item in raw_t_points:
            value = _safe_float(item, 0.0)
            if value > 0:
                t_points.append(value)
    if not t_points:
        t_points = [0.4, 0.8]
    high = max(max(t_points) * 2.0, 1.6)
    low = max(0.1, min(t_points) / 2.0)
    values = [low + (high - low) * index / 7 for index in range(8)]
    for value in t_points:
        if all(abs(value - existing) > 1e-9 for existing in values):
            values.append(value)
    return sorted(values)


def _empirical_characteristic_parts(values: list[float], frequency: float) -> tuple[float, float]:
    if not values:
        return 0.0, 0.0
    real = sum(math.cos(frequency * value) for value in values) / len(values)
    imaginary = sum(math.sin(frequency * value) for value in values) / len(values)
    return real, imaginary


def _ecdf(values: list[float], threshold: float) -> float:
    if not values:
        return 0.0
    return sum(1 for value in values if value <= threshold) / len(values)


def _format_float(value: Any) -> str:
    try:
        return f"{float(value):.3g}"
    except (TypeError, ValueError):
        return ""


def _format_signed_float(value: Any) -> str:
    try:
        return f"{float(value):+.3g}"
    except (TypeError, ValueError):
        return ""


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _psi_threshold(context: dict[str, Any]) -> float:
    measurements = _path(context, "$.runtimeResult.metrics.measurements", {},)
    if isinstance(measurements, dict):
        try:
            return float(measurements.get("THRESHOLD") or 0.1)
        except (TypeError, ValueError):
            return 0.1
    return 0.1


def _psi_sample_sizes(context: dict[str, Any]) -> tuple[int, int]:
    measurements = _measurements(context)
    reference = measurements.get("REFERENCE_SAMPLE_SIZE")
    current = measurements.get("CURRENT_SAMPLE_SIZE")
    sample_size = measurements.get("SAMPLE_SIZE")
    if isinstance(sample_size, dict):
        reference = sample_size.get("reference", reference)
        current = sample_size.get("current", current)
    if reference is None or current is None:
        periods = _period_payload_values(context)
        reference = len(periods.get("reference", []))
        current = len(periods.get("current", []))
    return int(_safe_float(reference, 0)), int(_safe_float(current, 0))


def _distance_score(context: dict[str, Any]) -> float:
    measurements = _measurements(context)
    return _safe_float(
        _path(context, "$.runtimeResult.metrics.distance", None)
        or measurements.get("WASSERSTEIN_DISTANCE")
        or measurements.get("DISTANCE")
        or _score(context),
        0.0,
    )


def _distance_threshold(context: dict[str, Any]) -> float:
    measurements = _measurements(context)
    return _safe_float(
        _path(context, "$.runtimeResult.metrics.threshold", None)
        or measurements.get("THRESHOLD")
        or measurements.get("DISTANCE_THRESHOLD"),
        0.3,
    )


def _select_fields(row: dict[str, Any], fields: list[str]) -> dict[str, Any]:
    if not fields:
        return dict(row)
    return {field: row.get(field) for field in fields}


def _bucket_values(buckets: list[dict[str, Any]]) -> list[float]:
    values: list[float] = []
    for bucket in buckets:
        value = bucket.get("v", bucket.get("value", bucket.get("meanValue")))
        try:
            values.append(float(value))
        except (TypeError, ValueError):
            continue
    return values


def _before_after(values: list[float]) -> tuple[float, float]:
    if not values:
        return 0.0, 0.0
    if len(values) == 1:
        return values[0], values[0]
    return values[0], values[-1]


def _scaled_pair(before: float, after: float, fallback_before: float, fallback_after: float) -> tuple[float, float]:
    if before == after:
        return fallback_before, fallback_after
    low = min(before, after)
    high = max(before, after)
    scale = lambda value: fallback_before + ((value - low) / (high - low)) * (fallback_after - fallback_before)
    return scale(before), scale(after)


def _interpolated_values(values: list[float], count: int, target_min: float, target_max: float) -> list[float]:
    before, after = _before_after(values)
    scaled_before, scaled_after = _scaled_pair(before, after, target_min, target_max)
    if count <= 1:
        return [scaled_after]
    return [
        scaled_before + ((scaled_after - scaled_before) * index / (count - 1))
        for index in range(count)
    ]


def _alarm_index() -> int:
    return 23


def _runtime_time_index(index: int, count: int) -> float:
    if count <= 1:
        return 1
    value = 1 + (35 * index / (count - 1))
    return round(value, 4)


def _runtime_axis_index(index: int, count: int, max_value: int) -> float:
    if count <= 1:
        return 1
    value = 1 + ((max_value - 1) * index / (count - 1))
    return round(value, 4)


def _sample_values(values: list[float], count: int) -> list[float]:
    if count <= 0 or not values:
        return []
    if len(values) <= count:
        return list(values)
    return [
        values[min(len(values) - 1, round(index * (len(values) - 1) / (count - 1)))]
        for index in range(count)
    ]


def _seqdrift_axis_from_alarm(event: dict[str, Any], measurements: dict[str, Any]) -> float:
    processed = max(1, int(_safe_float(measurements.get("PROCESSED_COUNT"), 36)))
    reference_size = int(_safe_float(measurements.get("SAMPLE_SIZE_REFERENCE"), 0))
    raw_index = _safe_float(event.get("index"), 0.0)
    absolute_index = reference_size + raw_index
    return _runtime_axis_index(round(absolute_index), processed, 36)


def _seqdrift_alarm_axis(measurements: dict[str, Any], index_key: str, time_key: str) -> float | None:
    processed = int(_safe_float(measurements.get("PROCESSED_COUNT"), 0))
    if processed <= 1:
        return None
    reference_size = int(_safe_float(measurements.get("SAMPLE_SIZE_REFERENCE"), 0))
    raw_index = measurements.get(index_key)
    if raw_index is not None:
        return _runtime_axis_index(reference_size + round(_safe_float(raw_index, 0.0)), processed, 36)
    alarm_events = measurements.get("ALARM_EVENTS")
    if isinstance(alarm_events, list):
        target_time = measurements.get(time_key)
        for event in alarm_events:
            if not isinstance(event, dict):
                continue
            if target_time and event.get("time") != target_time:
                continue
            return _seqdrift_axis_from_alarm(event, measurements)
    return None


def _bucket_error_value(bucket: dict[str, Any], fallback: float) -> float:
    return _safe_float(
        bucket.get("errorRate")
        or bucket.get("error_rate")
        or bucket.get("v")
        or bucket.get("value")
        or bucket.get("meanValue"),
        fallback,
    )


def _error_rate_threshold(context: dict[str, Any]) -> float:
    measurements = _measurements(context)
    return _safe_float(
        _path(context, "$.runtimeResult.metrics.threshold", None)
        or measurements.get("THRESHOLD")
        or _path(context, "$.assignment.params.errorRateShiftThreshold", None)
        or _path(context, "$.assignment.calibratedParams.errorRateShiftThreshold", None),
        0.15,
    )


def _event_bucket_index(context: dict[str, Any], buckets: list[dict[str, Any]]) -> int:
    if not buckets:
        return 0
    event_start = str(_path(context, "$.driftEvent.eventStart", "") or "")
    event_end = str(_path(context, "$.driftEvent.eventEnd", "") or "")
    for index, bucket in enumerate(buckets):
        bucket_start = str(bucket.get("bucketStart") or "")
        bucket_end = str(bucket.get("bucketEnd") or "")
        if event_end and bucket_end == event_end:
            return index
        if event_start and bucket_start == event_start:
            return index
    return len(buckets) - 1


def _psi_contribution_rows(context: dict[str, Any]) -> list[dict[str, Any]]:
    measurements = _path(context, "$.runtimeResult.metrics.measurements", {})
    if not isinstance(measurements, dict):
        return []
    contributions = measurements.get("PSI_CONTRIBUTION")
    reference_counts = measurements.get("CATEGORY_COUNTS_REFERENCE", {})
    current_counts = measurements.get("CATEGORY_COUNTS_CURRENT", {})
    reference_total = float(measurements.get("REFERENCE_SAMPLE_SIZE") or 0)
    current_total = float(measurements.get("CURRENT_SAMPLE_SIZE") or 0)
    if not isinstance(contributions, list):
        return []
    rows: list[dict[str, Any]] = []
    for index, contribution in enumerate(contributions):
        if not isinstance(contribution, dict):
            continue
        label = str(contribution.get("category", f"bin_{index}"))
        reference = float(contribution.get("reference_proportion") or 0)
        current = float(contribution.get("current_proportion") or 0)
        if reference_total > 0 and label in reference_counts:
            reference = float(reference_counts[label]) / reference_total
        if current_total > 0 and label in current_counts:
            current = float(current_counts[label]) / current_total
        value = float(contribution.get("psi_contribution") or 0)
        delta = current - reference
        rows.append(
            {
                "label": label,
                "category": label,
                "bin": label,
                "feature": label,
                "reference": reference,
                "current": current,
                "deltaLabel": f"{delta * 100:+.1f}pp",
                "value": value,
                "displayValue": f"{value:.4f}",
                "contribution": value,
                "psi": value,
                "class": "top-contribution" if index == 0 else "contrib-bar",
            }
        )
    return rows
