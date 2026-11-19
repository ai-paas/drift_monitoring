from __future__ import annotations

import hashlib
import json
import os
import queue
import threading
import time
import urllib.error
import urllib.request
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import psycopg
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = ROOT.parent
HOST = os.environ.get("LLM_INTERPRETATION_SERVER_HOST", "127.0.0.1")
PORT = int(os.environ.get("LLM_INTERPRETATION_SERVER_PORT") or os.environ.get("CHART_INTERPRETATION_PORT", "8767"))
DRIFT_DB_HOST = os.environ.get("DRIFT_DB_HOST", "127.0.0.1")
DRIFT_DB_PORT = int(os.environ.get("DRIFT_DB_PORT", "5432"))
DRIFT_DB_NAME = os.environ.get("DRIFT_DB_NAME", "drift_monitoring")
DRIFT_DB_USER = os.environ.get("DRIFT_DB_USER", "postgres")
DRIFT_DB_PASSWORD = os.environ.get("DRIFT_DB_PASSWORD", "postgres")
LLM_ENDPOINT = os.environ.get(
    "LLM_API_ENDPOINT",
    "http://127.0.0.1:8001/v1/chat/completions",
).strip()
LLM_MODEL = os.environ.get("LLM_MODEL", "gpt-oss-120b").strip()
LLM_API_KEY = os.environ.get("LLM_API_KEY", "").strip()
LLM_TIMEOUT_SECONDS = int(os.environ.get("LLM_TIMEOUT_SECONDS", "90"))
LLM_RETRY_COUNT = int(os.environ.get("LLM_RETRY_COUNT", "1"))
LLM_SKIP_DB = os.environ.get("LLM_SKIP_DB", "").strip().lower() in {"1", "true", "yes"}
INTERPRETATION_SCHEMA_PATH = ROOT / "docs" / "chart_interpretation_output_schema.json"
PROMPT_TEMPLATE_DIR = ROOT / "docs" / "prompts"
PROMPT_RUN_DIR = ROOT / "interpretation_runs"

app = FastAPI(title="Chart Interpretation Server", version="0.1")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type"],
)

SEVERITY_RANK = {"normal": 0, "watch": 1, "candidate": 2}
JOB_QUEUE: queue.Queue[str] = queue.Queue()
JOBS: dict[str, dict[str, Any]] = {}
PAYLOAD_CACHE: dict[str, str] = {}
JOBS_LOCK = threading.Lock()
WORKER_STARTED = False



@dataclass
class ComponentKnowledge:
    component_code: str
    purpose_text: str = ""
    shows_text: str = ""
    interpretation_text: str = ""
    caution_text: str = ""
    rules: list[dict[str, Any]] | None = None


def db_conn():
    return psycopg.connect(
        host=DRIFT_DB_HOST,
        port=DRIFT_DB_PORT,
        dbname=DRIFT_DB_NAME,
        user=DRIFT_DB_USER,
        password=DRIFT_DB_PASSWORD,
        connect_timeout=1,
        autocommit=True,
    )


def query_one(sql_text: str, params: tuple[Any, ...]) -> dict[str, Any] | None:
    if LLM_SKIP_DB:
        return None
    try:
        with db_conn() as conn:
            with conn.cursor(row_factory=psycopg.rows.dict_row) as cur:
                cur.execute(sql_text, params)
                return cur.fetchone()
    except Exception:
        return None


def query_all(sql_text: str, params: tuple[Any, ...]) -> list[dict[str, Any]]:
    if LLM_SKIP_DB:
        return []
    try:
        with db_conn() as conn:
            with conn.cursor(row_factory=psycopg.rows.dict_row) as cur:
                cur.execute(sql_text, params)
                return list(cur.fetchall())
    except Exception:
        return []


def fallback_rules(component_code: str) -> list[dict[str, Any]]:
    return []

def component_knowledge(component_code: str) -> ComponentKnowledge:
    row = query_one(
        """
        select component_code, purpose_text, shows_text, interpretation_text, caution_text
        from chart_component
        where component_code = %s
        """,
        (component_code,),
    ) or {"component_code": component_code}
    return ComponentKnowledge(
        component_code=component_code,
        purpose_text=str(row.get("purpose_text") or ""),
        shows_text=str(row.get("shows_text") or ""),
        interpretation_text=str(row.get("interpretation_text") or ""),
        caution_text=str(row.get("caution_text") or ""),
        rules=[],
    )

def chart_guide(chart_id: str) -> dict[str, Any]:
    return query_one(
        """
        select chart_code, chart_family, display_title, purpose_text, component_summary_text
        from chart_definition
        where chart_code = %s
        limit 1
        """,
        (chart_id,),
    ) or {}



_CONTEXT_CACHE: dict[str, tuple[float, Any]] = {}


COMPONENT_GUIDE_FILES = {
    "adaptive_model_structure_view": "line_like.md",
    "bar_chart": "bar_chart.md",
    "contribution_view": "bar_chart.md",
    "control_chart": "line_like.md",
    "cumulative_curve": "line_like.md",
    "detector_statistic_view": "line_like.md",
    "distance_metric_view": "line_like.md",
    "model_diagnostic_curve": "model_diagnostic_curve.md",
    "performance_metric_view": "line_like.md",
    "proportion_view": "bar_chart.md",
    "ranking_view": "bar_chart.md",
    "raw_signal_trend": "line_like.md",
    "trend_line": "line_like.md",
    "decision_card": "decision_card.md",
    "circular_histogram": "distribution.md",
    "distribution_view": "distribution.md",
    "distribution_summary_plot": "distribution.md",
    "event_marker": "event_marker.md",
    "event_raster": "event_marker.md",
    "forest_plot": "forest_plot.md",
    "heatmap": "heatmap.md",
    "histogram_view": "distribution.md",
    "matrix_view": "matrix_view.md",
    "node_link_diagram": "context_only.md",
    "projection_scatter": "projection_scatter.md",
    "feature_projection_view": "feature_projection_view.md",
    "quantile_view": "distribution.md",
    "reference_current_comparison": "reference_current_comparison.md",
    "state_timeline": "state_timeline.md",
    "small_multiple_lines": "line_like.md",
    "domain_specific_visual": "context_only.md",
}


def cached_context(key: str, loader, ttl: int = 60):
    now = time.time()
    cached = _CONTEXT_CACHE.get(key)
    if cached and now - cached[0] < ttl:
        return cached[1]
    value = loader()
    _CONTEXT_CACHE[key] = (now, value)
    return value


def llm_component_context(component_code: str) -> dict[str, Any]:
    def load():
        rows = query_all(
            """
            select component_code, context_markdown, example_good, example_bad, version
            from llm_component_interpretation_context
            where component_code = %s
            """,
            (component_code,),
        )
        return dict(rows[0]) if rows else {}
    return cached_context(f"component:{component_code}", load)


def llm_chart_context(payload: dict[str, Any], chart_id: str) -> list[dict[str, Any]]:
    family = str((payload.get("analysisContext") or {}).get("analysisKind") or "")
    keys = [chart_id]
    if family:
        keys.append(family)
    def load():
        rows = query_all(
            """
            select context_key, applies_to, context_markdown, example_good, example_bad, version
            from llm_chart_interpretation_context
            where context_key = any(%s)
            order by case when context_key = %s then 0 else 1 end, context_key
            """,
            (keys, chart_id),
        )
        return [dict(row) for row in rows]
    return cached_context("chart:" + ":".join(keys), load)

def num(value: Any) -> float | None:
    try:
        if value is None or value == "":
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def format_num(value: float | None) -> str:
    if value is None:
        return "n/a"
    if abs(value) >= 100:
        return f"{value:.0f}"
    if abs(value) >= 10:
        return f"{value:.1f}"
    return f"{value:.3f}".rstrip("0").rstrip(".")



def compact_text(value: Any, limit: int = 1200) -> str:
    text = " ".join(str(value or "").split())
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "…"

def summary_from_text(text: str, limit: int = 220) -> str:
    normalized = " ".join(str(text or "").split())
    if not normalized:
        return ""
    sentence_end = [idx for idx in (normalized.find(". "), normalized.find("다. "), normalized.find("요. ")) if idx >= 0]
    end = min(sentence_end) + 1 if sentence_end else min(len(normalized), limit)
    summary = normalized[:end].strip()
    if len(summary) > limit:
        summary = summary[: limit - 1].rstrip() + "…"
    return summary




def ensure_sentence_punctuation(text: str) -> str:
    value = " ".join(str(text or "").split()).strip()
    if not value:
        return ""
    if value[-1] not in ".!?":
        value += "."
    return value


def parse_json_object(text: str) -> dict[str, Any] | None:
    value = str(text or "").strip()
    if value.startswith("```"):
        lines = value.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        value = "\n".join(lines).strip()
    try:
        parsed = json.loads(value)
    except json.JSONDecodeError:
        start = value.find("{")
        end = value.rfind("}")
        if start < 0 or end <= start:
            return None
        try:
            parsed = json.loads(value[start:end + 1])
        except json.JSONDecodeError:
            return None
    return parsed if isinstance(parsed, dict) else None


def chart_output_from_codex(text: str) -> dict[str, Any] | None:
    parsed = parse_json_object(text)
    if not parsed:
        return None
    summary = ensure_sentence_punctuation(str(parsed.get("summary") or ""))
    detail = str(parsed.get("detail") or "").replace("\\r\\n", "\n").replace("\\n", "\n").strip()
    if len(summary) < 10 or len(detail) < 20:
        return None
    component_notes = []
    for item in parsed.get("componentNotes") or []:
        if not isinstance(item, dict):
            continue
        component_id = str(item.get("componentInstanceId") or "").strip()
        note_summary = ensure_sentence_punctuation(str(item.get("summary") or "").strip())
        note_detail = str(item.get("detail") or "").replace("\\r\\n", "\n").replace("\\n", "\n").strip()
        if not component_id or len(note_summary) < 5 or len(note_detail) < 10:
            continue
        severity = str(item.get("severity") or "watch")
        if severity not in {"normal", "watch", "candidate"}:
            severity = "watch"
        component_notes.append({
            "componentInstanceId": component_id,
            "title": str(item.get("title") or f"{component_id} 해석").strip(),
            "summary": note_summary,
            "detail": note_detail,
            "severity": severity,
            "provider": "openai_compatible",
        })
    return {"summary": summary, "detail": detail, "componentNotes": component_notes}

def interpretation_schema_text() -> str:
    try:
        return INTERPRETATION_SCHEMA_PATH.read_text(encoding="utf-8")
    except OSError:
        return '{"type":"object","required":["summary","detail"]}'


def read_text_optional(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8").strip()
    except OSError:
        return ""


def db_sections_for_source_paths(source_paths: list[str], section_types: list[str] | None = None) -> list[dict[str, Any]]:
    if not source_paths:
        return []
    params: list[Any] = [source_paths]
    section_filter = ""
    if section_types:
        params.append(section_types)
        section_filter = "and ds.section_type = any(%s)"
    return query_all(
        f"""
        select sd.source_path, ds.section_type, ds.heading_text, ds.body_markdown, ds.body_plain_text, ds.display_order
        from document_section ds
        join source_document sd on sd.source_document_id = ds.source_document_id
        where sd.source_path = any(%s)
          and ds.is_active = true
          {section_filter}
        order by sd.source_path, ds.display_order
        """,
        tuple(params),
    )


def format_guide_sections(sections: list[dict[str, Any]]) -> str:
    parts: list[str] = []
    for section in sections:
        heading = str(section.get("heading_text") or section.get("section_type") or "Guide").strip()
        body = str(section.get("body_plain_text") or section.get("body_markdown") or "").strip()
        if body:
            parts.append(f"## {heading}\n\n{body}")
    return "\n\n".join(parts)


def interpretation_guide_text() -> str:
    sections = db_sections_for_source_paths(
        [
            "chart_builder/docs/interpretation/general_guide.md",
            "chart_builder/docs/interpretation/chart_level_guide.md",
        ]
    )
    text = format_guide_sections(sections)
    if text:
        return text
    return (
        "Explain component role first, then visual encoding, current evidence, reading rule, and caution. "
        "Do not treat axis ticks as thresholds or infer drift without explicit evidence."
    )


def component_guide_text(component_type: str) -> str:
    rows = query_all(
        """
        select ds.heading_text, ds.body_markdown, ds.body_plain_text, ds.display_order
        from chart_component cc
        join section_entity_link sel on sel.entity_type = 'component'
                                    and sel.entity_id = cc.chart_component_id
                                    and sel.link_role = 'interpretation_guide'
        join document_section ds on ds.document_section_id = sel.document_section_id
        where cc.component_code = %s
          and ds.is_active = true
        order by ds.display_order
        """,
        (component_type,),
    )
    text = format_guide_sections(rows)
    if text:
        return text
    guide_file = COMPONENT_GUIDE_FILES.get(component_type)
    if not guide_file:
        return ""
    fallback_source = f"chart_builder/docs/interpretation/component_guides/{guide_file}"
    return format_guide_sections(db_sections_for_source_paths([fallback_source]))


def chart_specific_guide_text(chart_id: str) -> str:
    normalized = "".join(ch for ch in chart_id.upper() if ch.isalnum() or ch == "-")
    if not normalized:
        return ""
    row = query_one(
        """
        select interpretation_template_text, synthesis_rule_json, caution_text
        from chart_interpretation_guide cig
        join chart_definition cd on cd.chart_definition_id = cig.chart_definition_id
        where cd.chart_code = %s
          and cig.guide_code = 'BUILDER_CHART_GUIDE'
        limit 1
        """,
        (normalized,),
    )
    if row:
        return json.dumps(row, ensure_ascii=False, sort_keys=True)
    fallback_source = f"chart_builder/docs/interpretation/chart_guides/{normalized}.md"
    return format_guide_sections(db_sections_for_source_paths([fallback_source]))


def sample_rows(rows: list[dict[str, Any]], limit: int = 5) -> dict[str, Any]:
    if len(rows) <= limit * 2:
        return {"rowCount": len(rows), "rows": rows}
    return {"rowCount": len(rows), "head": rows[:limit], "tail": rows[-limit:]}


def component_knowledge_context(knowledge: ComponentKnowledge) -> dict[str, Any]:
    llm_context = llm_component_context(knowledge.component_code)
    return {
        "component_code": knowledge.component_code,
        "purpose_text": compact_text(knowledge.purpose_text),
        "shows_text": compact_text(knowledge.shows_text),
        "interpretation_text": compact_text(knowledge.interpretation_text),
        "caution_text": compact_text(knowledge.caution_text),
        "component_guide": compact_text(component_guide_text(knowledge.component_code), limit=2500),
        "llm_context": llm_context,
        "note": "Use llm_context as interpretation guidance. No rule-based prose template is provided.",
    }

def data_for(payload: dict[str, Any], instance: dict[str, Any]) -> list[dict[str, Any]]:
    source = ((instance.get("dataBinding") or {}).get("source"))
    data = payload.get("data") or {}
    rows = data.get(source, []) if source else []
    return rows if isinstance(rows, list) else []



def visual_encoding_note(payload: dict[str, Any], instance: dict[str, Any]) -> str:
    component_type = str(instance.get("componentType") or "")
    config = instance.get("config") or {}
    area = instance.get("area")
    notes: list[str] = []
    line_types = {"trend_line", "raw_signal_trend", "detector_statistic_view", "distance_metric_view", "performance_metric_view", "control_chart", "cumulative_curve", "model_diagnostic_curve", "adaptive_model_structure_view"}
    if component_type in line_types:
        x_label = config.get("x_axis_label") or config.get("time_field") or config.get("x_field") or "time"
        y_label = config.get("y_axis_label") or config.get("label") or config.get("value_field") or config.get("y_field") or "value"
        notes.append(f"파란 실선은 x축 {x_label}에 따른 y축 {y_label} 값의 추세를 연결한 선이다.")
        if config.get("show_points") is not False:
            every = config.get("point_sample_every")
            radius = config.get("point_radius")
            sampled = f" {every}개 간격으로" if every else ""
            size = f" 반지름 {radius}의" if radius else ""
            notes.append(f"둥근 점은{sampled}{size} 관측값 표식이며, 마지막 시점은 항상 점으로 표시된다.")
        if config.get("secondary_value_field"):
            notes.append(f"보조 선/점은 {config.get('secondary_value_field')} 값을 나타내며 주 값과 구조 변화를 비교하기 위한 표시다.")
        if config.get("horizontal_markers"):
            labels = [str(marker.get("label") or marker.get("y")) for marker in config.get("horizontal_markers") or []]
            notes.append(f"수평 기준선은 {', '.join(labels)} 위치를 표시한다.")
        overlays = [item for item in (payload.get("components") or []) if isinstance(item, dict) and item.get("area") == area and item.get("componentType") == "event_marker"]
        for overlay in overlays:
            rows = data_for(payload, overlay)
            event_type_field = (overlay.get("config") or {}).get("event_type_field") or "event_type"
            event_types = [str(row.get(event_type_field) or row.get("label") or "event") for row in rows]
            if event_types:
                notes.append(f"붉은 세로 점선은 같은 area에 겹쳐진 이벤트 marker이며, {', '.join(event_types[:4])} 시점을 강조한다.")
            if (overlay.get("config") or {}).get("highlight_point"):
                notes.append("붉은 둥근 점은 이벤트 시점의 주 추세선 값을 강조한 표식이다.")
    elif component_type == "event_marker":
        notes.append("세로 점선은 이벤트가 발생한 x축 위치를 표시한다.")
        if config.get("highlight_point"):
            notes.append("둥근 강조점은 이벤트 시점에 대응하는 기준 추세선의 값을 표시한다.")
    elif component_type in {"state_timeline", "window_view"}:
        notes.append("가로 막대는 상태가 유지되는 구간을 나타내며 색상/라벨은 normal, warning, alternate, replace 같은 detector 상태를 구분한다.")
        if config.get("marker_role") or config.get("markers"):
            notes.append("세로 marker는 특정 상태나 교체 시점을 기준선처럼 표시한다.")
    elif component_type == "adaptive_model_structure_view":
        notes.append("주 선은 main tree 크기, 보조 선/점은 alternate 또는 secondary tree 크기를 나타낸다.")
    elif component_type == "decision_card":
        notes.append("카드는 주요 지표를 숫자와 라벨로 요약해 분석 대상과 범위를 빠르게 확인하게 한다.")
    return " ".join(notes)

def threshold_from_config(config: dict[str, Any]) -> float | None:
    if num(config.get("threshold_value")) is not None:
        return num(config.get("threshold_value"))
    for key in ("target_value", "control_limit", "limit_value"):
        value = num(config.get(key))
        if value is not None:
            return value
    for marker in config.get("horizontal_markers") or []:
        value = num(marker.get("y"))
        if value is not None:
            return value
    return None

def line_signal(instance: dict[str, Any], rows: list[dict[str, Any]]) -> dict[str, Any]:
    config = instance.get("config") or {}
    x_field = config.get("time_field") or config.get("x_field") or "time"
    y_field = config.get("value_field") or config.get("y_field") or config.get("statistic_field") or "value"
    secondary_field = config.get("secondary_value_field")
    valid = [row for row in rows if num(row.get(y_field)) is not None]
    values = [num(row.get(y_field)) for row in valid]
    secondary_values = [num(row.get(secondary_field)) for row in valid] if secondary_field else []
    secondary_values = [item for item in secondary_values if item is not None]
    latest = values[-1] if values else None
    previous = values[-2] if len(values) >= 2 else None
    first = values[0] if values else None
    min_value = min(values) if values else None
    max_value = max(values) if values else None
    min_index = values.index(min_value) if min_value is not None else None
    max_index = values.index(max_value) if max_value is not None else None
    recent_max = max(values[-5:]) if values else None
    slope = latest - previous if latest is not None and previous is not None else None
    total_change = latest - first if latest is not None and first is not None else None
    secondary_latest = secondary_values[-1] if secondary_values else None
    secondary_previous = secondary_values[-2] if len(secondary_values) >= 2 else None
    secondary_first = secondary_values[0] if secondary_values else None
    secondary_max = max(secondary_values) if secondary_values else None
    secondary_gap_items = []
    if secondary_field:
        for row in valid:
            primary = num(row.get(y_field))
            secondary = num(row.get(secondary_field))
            if primary is not None and secondary is not None:
                secondary_gap_items.append({
                    "x": row.get(x_field),
                    "gap": secondary - primary,
                    "primary": primary,
                    "secondary": secondary,
                })
    max_secondary_gap = max(secondary_gap_items, key=lambda item: abs(item["gap"]), default=None)
    threshold = threshold_from_config(config)
    relation = None
    severity = "normal"
    if latest is not None and threshold is not None:
        if latest >= threshold:
            relation = "above_threshold"
            severity = "candidate"
        elif recent_max is not None and recent_max >= threshold:
            relation = "below_but_recent_touch"
            severity = "watch"
        elif threshold > 0 and latest >= threshold * 0.8:
            relation = "below_but_near_threshold"
            severity = "watch"
        else:
            relation = "below_threshold"
    if severity == "normal" and slope is not None and slope > 0 and threshold is not None and latest is not None and latest < threshold:
        severity = "watch" if latest >= threshold * 0.65 else "normal"
        relation = relation or "rising_toward_threshold"
    return {
        "xField": x_field,
        "yField": y_field,
        "secondaryField": secondary_field,
        "first": first,
        "latest": latest,
        "previous": previous,
        "min": min_value,
        "minX": valid[min_index].get(x_field) if min_index is not None and min_index < len(valid) else None,
        "max": max_value,
        "maxX": valid[max_index].get(x_field) if max_index is not None and max_index < len(valid) else None,
        "recentMax": recent_max,
        "slope": slope,
        "totalChange": total_change,
        "threshold": threshold,
        "relation": relation,
        "secondaryFirst": secondary_first,
        "secondaryLatest": secondary_latest,
        "secondaryPrevious": secondary_previous,
        "secondaryMax": secondary_max,
        "maxSecondaryGap": max_secondary_gap,
        "rowCount": len(valid),
        "severity": severity,
    }

def bar_signal(instance: dict[str, Any], rows: list[dict[str, Any]]) -> dict[str, Any]:
    config = instance.get("config") or {}
    category_field = config.get("category_field") or "label"
    value_field = config.get("value_field") or "value"
    series_fields = [item for item in config.get("series_fields") or [] if isinstance(item, str)]
    candidates = []
    if len(series_fields) >= 2:
        for row in rows:
            vals = [(field, num(row.get(field))) for field in series_fields]
            vals = [(field, value) for field, value in vals if value is not None]
            if len(vals) >= 2:
                delta = vals[-1][1] - vals[0][1]
                candidates.append({"category": row.get(category_field), "value": delta, "displayValue": f"{delta:+.3f}"})
    elif len(series_fields) == 1:
        value_field = series_fields[0]
        for row in rows:
            value = num(row.get(value_field))
            if value is not None:
                candidates.append({"category": row.get(category_field), "value": value, "displayValue": row.get("displayValue") or row.get("rateLabel") or format_num(value)})
    else:
        for row in rows:
            value = num(row.get(value_field))
            if value is not None:
                candidates.append({"category": row.get(category_field), "value": value, "displayValue": row.get("displayValue") or format_num(value)})
    top = max(candidates, key=lambda item: abs(float(item["value"])), default=None)
    severity = "watch" if top and abs(float(top["value"])) > 0 else "normal"
    return {"categoryField": category_field, "valueField": value_field, "top": top, "categoryValues": candidates, "rowCount": len(rows), "severity": severity}


def matrix_signal(instance: dict[str, Any], rows: list[dict[str, Any]]) -> dict[str, Any]:
    config = instance.get("config") or {}
    category_field = config.get("category_field") or config.get("row_field") or "category"
    value_field = config.get("value_field") or "value"
    event_field = config.get("event_field")
    nonevent_field = config.get("nonevent_field")
    if event_field and nonevent_field:
        groups = []
        for row in rows:
            event = num(row.get(event_field))
            nonevent = num(row.get(nonevent_field))
            total = (event or 0) + (nonevent or 0) if event is not None or nonevent is not None else None
            rate = event / total if event is not None and total else None
            groups.append({
                "label": row.get(config.get("label_field") or "label"),
                "event": event,
                "nonevent": nonevent,
                "total": total,
                "rate": rate,
            })
        severity = "candidate" if len(groups) >= 2 and groups[-1].get("rate") is not None and groups[0].get("rate") is not None and groups[-1]["rate"] > groups[0]["rate"] else "normal"
        return {
            "contingency": True,
            "groups": groups,
            "rowCount": len(rows),
            "eventField": event_field,
            "noneventField": nonevent_field,
            "severity": severity,
        }
    candidates = []
    for row in rows:
        value = num(row.get(value_field))
        if value is not None:
            candidates.append({"category": row.get(category_field), "value": value, "displayValue": format_num(value)})
    top_abs = max(candidates, key=lambda item: abs(float(item["value"])), default=None)
    positive = max(candidates, key=lambda item: float(item["value"]), default=None)
    negative = min(candidates, key=lambda item: float(item["value"]), default=None)
    severity = "candidate" if top_abs and abs(float(top_abs["value"])) >= 2 else "watch" if top_abs else "normal"
    return {
        "matrixNumeric": True,
        "categoryField": category_field,
        "valueField": value_field,
        "topAbs": top_abs,
        "positive": positive,
        "negative": negative,
        "rowCount": len(rows),
        "severity": severity,
    }


def forest_signal(instance: dict[str, Any], rows: list[dict[str, Any]]) -> dict[str, Any]:
    config = instance.get("config") or {}
    value_field = config.get("value_field") or "oddsRatio"
    low_field = config.get("low_field") or "ciLow"
    high_field = config.get("high_field") or "ciHigh"
    null_value = num(config.get("null_value"))
    if null_value is None:
        null_value = 1
    row = rows[0] if rows else {}
    value = num(row.get(value_field))
    low = num(row.get(low_field))
    high = num(row.get(high_field))
    excludes_null = None
    if low is not None and high is not None:
        excludes_null = high < null_value or low > null_value
    severity = "candidate" if excludes_null else "watch" if value is not None else "normal"
    return {
        "forest": True,
        "valueField": value_field,
        "lowField": low_field,
        "highField": high_field,
        "value": value,
        "low": low,
        "high": high,
        "nullValue": null_value,
        "excludesNull": excludes_null,
        "rowCount": len(rows),
        "severity": severity,
    }


def card_signal(instance: dict[str, Any], rows: list[dict[str, Any]]) -> dict[str, Any]:
    metrics = []
    severity = "normal"
    for row in rows:
        label = str(row.get("label") or row.get("title") or "metric")
        value = row.get("displayValue") or row.get("display_value") or row.get("value") or row.get("decision")
        if row.get("decision") and "DRIFT" in str(row.get("decision")).upper():
            severity = "candidate"
        metrics.append({"label": label, "value": value})
    return {"metrics": metrics, "rowCount": len(rows), "severity": severity}


def timeline_signal(instance: dict[str, Any], rows: list[dict[str, Any]]) -> dict[str, Any]:
    config = instance.get("config") or {}
    role_field = config.get("window_role_field") or config.get("state_field") or "role"
    start_field = config.get("start_field") or "start"
    end_field = config.get("end_field") or "end"
    label_field = config.get("label_field") or "window"
    segments = []
    for row in rows:
        role = str(row.get(role_field) or row.get("state") or row.get("role") or "")
        if not role:
            continue
        segments.append({
            "role": role,
            "label": row.get(label_field),
            "start": row.get(start_field),
            "end": row.get(end_field),
        })
    roles = [item["role"] for item in segments]
    severity = "candidate" if any("drift" in role or "alarm" in role or "replace" in role for role in roles) else "watch" if any("warn" in role for role in roles) else "normal"
    return {"sequence": roles, "segments": segments, "rowCount": len(rows), "severity": severity}

def scatter_signal(instance: dict[str, Any], rows: list[dict[str, Any]]) -> dict[str, Any]:
    config = instance.get("config") or {}
    group_field = config.get("group_field") or "group"
    x_field = config.get("x_field") or "x"
    y_field = config.get("y_field") or "y"
    counts: dict[str, int] = {}
    sums: dict[str, dict[str, float]] = {}
    for row in rows:
        group = str(row.get(group_field) or "default")
        counts[group] = counts.get(group, 0) + 1
        x = num(row.get(x_field))
        y = num(row.get(y_field))
        if x is not None and y is not None:
            item = sums.setdefault(group, {"x": 0.0, "y": 0.0, "n": 0.0})
            item["x"] += x
            item["y"] += y
            item["n"] += 1
    centroids = {
        group: {"x": item["x"] / item["n"], "y": item["y"] / item["n"]}
        for group, item in sums.items()
        if item["n"]
    }
    centroid_distance = None
    if len(centroids) >= 2:
        values = list(centroids.values())
        dx = values[1]["x"] - values[0]["x"]
        dy = values[1]["y"] - values[0]["y"]
        centroid_distance = (dx * dx + dy * dy) ** 0.5
    diagonal_items = []
    for row in rows:
        x = num(row.get(x_field))
        y = num(row.get(y_field))
        if x is not None and y is not None:
            diagonal_items.append({"x": x, "y": y, "gap": y - x})
    max_diagonal_gap = max(diagonal_items, key=lambda item: abs(item["gap"]), default=None)
    severity = "watch" if len(counts) > 1 else "normal"
    return {
        "groupField": group_field,
        "xField": x_field,
        "yField": y_field,
        "groupCounts": counts,
        "centroids": centroids,
        "centroidDistance": centroid_distance,
        "maxDiagonalGap": max_diagonal_gap,
        "rowCount": len(rows),
        "severity": severity,
    }


def distribution_signal(instance: dict[str, Any], rows: list[dict[str, Any]]) -> dict[str, Any]:
    config = instance.get("config") or {}
    x_field = config.get("x_field") or config.get("bin_field") or "x"
    primary_field = config.get("primary_value_field") or config.get("reference_field") or config.get("baseline_field") or config.get("value_field") or "baseline"
    secondary_field = config.get("secondary_value_field") or config.get("current_field") or "current"
    valid = []
    for row in rows:
        x = num(row.get(x_field))
        primary = num(row.get(primary_field))
        secondary = num(row.get(secondary_field))
        count = num(row.get("count"))
        if x is None and num(row.get("x0")) is not None and num(row.get("x1")) is not None:
            x = (num(row.get("x0")) + num(row.get("x1"))) / 2
        valid.append({"x": x, "primary": primary, "secondary": secondary, "count": count, "row": row})
    primary_valid = [item for item in valid if item["x"] is not None and item["primary"] is not None]
    secondary_valid = [item for item in valid if item["x"] is not None and item["secondary"] is not None]
    count_valid = [item for item in valid if item["x"] is not None and item["count"] is not None]
    primary_peak = max(primary_valid, key=lambda item: item["primary"], default=None)
    secondary_peak = max(secondary_valid, key=lambda item: item["secondary"], default=None)
    count_peak = max(count_valid, key=lambda item: item["count"], default=None)
    peak_shift = None
    if primary_peak and secondary_peak:
        peak_shift = secondary_peak["x"] - primary_peak["x"]
    total_primary = sum(item["primary"] for item in primary_valid) if primary_valid else None
    total_secondary = sum(item["secondary"] for item in secondary_valid) if secondary_valid else None
    top_gap = None
    gap_items = []
    for item in valid:
        if item["x"] is not None and item["primary"] is not None and item["secondary"] is not None:
            gap = item["secondary"] - item["primary"]
            gap_items.append({"x": item["x"], "gap": gap, "primary": item["primary"], "secondary": item["secondary"]})
    if gap_items:
        top_gap = max(gap_items, key=lambda item: abs(item["gap"]))
    severity = "watch"
    if peak_shift is not None and abs(peak_shift) > 0:
        severity = "candidate"
    return {
        "distribution": True,
        "xField": x_field,
        "primaryField": primary_field,
        "secondaryField": secondary_field,
        "rowCount": len(rows),
        "primaryPeak": primary_peak,
        "secondaryPeak": secondary_peak,
        "countPeak": count_peak,
        "peakShift": peak_shift,
        "topGap": top_gap,
        "totalPrimary": total_primary,
        "totalSecondary": total_secondary,
        "severity": severity,
    }


def small_multiple_signal(instance: dict[str, Any], rows: list[dict[str, Any]]) -> dict[str, Any]:
    config = instance.get("config") or {}
    series_field = config.get("series_field") or config.get("group_field") or "series"
    x_field = config.get("time_field") or config.get("x_field") or "time"
    y_field = config.get("value_field") or config.get("y_field") or "value"
    series: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        value = num(row.get(y_field))
        if value is None:
            continue
        key = str(row.get(series_field) or "series")
        series.setdefault(key, []).append({"x": row.get(x_field), "value": value})
    summaries = []
    for key, values in series.items():
        first = values[0]["value"] if values else None
        latest = values[-1]["value"] if values else None
        summaries.append({"series": key, "first": first, "latest": latest, "change": latest - first if first is not None and latest is not None else None, "count": len(values)})
    top = max(summaries, key=lambda item: abs(item["change"] or 0), default=None)
    return {
        "smallMultiple": True,
        "seriesField": series_field,
        "xField": x_field,
        "yField": y_field,
        "series": summaries,
        "topChange": top,
        "rowCount": len(rows),
        "severity": "watch" if summaries else "normal",
    }


def event_raster_signal(instance: dict[str, Any], rows: list[dict[str, Any]]) -> dict[str, Any]:
    config = instance.get("config") or {}
    time_field = config.get("time_field") or config.get("x_field") or "time"
    lane_field = config.get("lane_field") or config.get("category_field") or "lane"
    type_field = config.get("event_type_field") or config.get("type_field") or "event_type"
    lanes: dict[str, int] = {}
    types: dict[str, int] = {}
    times = []
    for row in rows:
        lane = str(row.get(lane_field) or "lane")
        event_type = str(row.get(type_field) or row.get("label") or "event")
        lanes[lane] = lanes.get(lane, 0) + 1
        types[event_type] = types.get(event_type, 0) + 1
        t = num(row.get(time_field))
        if t is not None:
            times.append(t)
    return {
        "eventRaster": True,
        "timeField": time_field,
        "laneField": lane_field,
        "typeField": type_field,
        "laneCounts": lanes,
        "typeCounts": types,
        "timeMin": min(times) if times else None,
        "timeMax": max(times) if times else None,
        "rowCount": len(rows),
        "severity": "candidate" if rows else "normal",
    }


def node_link_signal(instance: dict[str, Any], rows: list[dict[str, Any]]) -> dict[str, Any]:
    nodes = [row for row in rows if str(row.get("kind") or row.get("type") or "").lower() in {"node", "nodes"} or row.get("source") is None and row.get("target") is None]
    links = [row for row in rows if row.get("source") is not None or row.get("target") is not None]
    weighted = [num(row.get("weight") or row.get("value")) for row in links]
    weighted = [item for item in weighted if item is not None]
    return {
        "nodeLink": True,
        "nodeCount": len(nodes),
        "linkCount": len(links),
        "maxWeight": max(weighted) if weighted else None,
        "rowCount": len(rows),
        "severity": "watch" if links else "normal",
    }


def model_diagnostic_signal(instance: dict[str, Any], rows: list[dict[str, Any]]) -> dict[str, Any]:
    config = instance.get("config") or {}
    x_field = config.get("x_field") or "x"
    y_field = config.get("y_field") or "y"
    valid = [row for row in rows if num(row.get(x_field)) is not None and num(row.get(y_field)) is not None]
    points = [{"x": num(row.get(x_field)), "y": num(row.get(y_field))} for row in valid]
    max_gap = None
    max_point = None
    for point in points:
        gap = point["y"] - point["x"]
        if max_gap is None or gap > max_gap:
            max_gap = gap
            max_point = point
    annotation_text = " ".join(str(item.get("text") or "") for item in config.get("annotations") or [] if isinstance(item, dict))
    severity = "candidate" if max_gap is not None and max_gap > 0.2 else "watch" if max_gap is not None and max_gap > 0 else "normal"
    return {
        "diagnosticCurve": True,
        "xField": x_field,
        "yField": y_field,
        "pointCount": len(points),
        "first": points[0] if points else None,
        "last": points[-1] if points else None,
        "maxVerticalGap": max_gap,
        "maxGapPoint": max_point,
        "annotationText": annotation_text,
        "severity": severity,
    }


def feature_projection_signal(instance: dict[str, Any], rows: list[dict[str, Any]]) -> dict[str, Any]:
    config = instance.get("config") or {}
    kind_field = config.get("kind_field") or "kind"
    feature_kind = config.get("feature_kind") or "feature"
    point_kind = config.get("point_kind") or "point"
    feature_name_field = config.get("feature_name_field") or "feature"
    feature_value_field = config.get("feature_value_field") or "value"
    group_field = config.get("point_group_field") or "group"
    features = []
    group_counts: dict[str, int] = {}
    for row in rows:
        kind = row.get(kind_field)
        if kind == feature_kind:
            value = num(row.get(feature_value_field))
            if value is not None:
                features.append({"feature": row.get(feature_name_field), "value": value, "displayValue": row.get("displayValue") or format_num(value)})
        elif kind == point_kind:
            group = str(row.get(group_field) or "default")
            group_counts[group] = group_counts.get(group, 0) + 1
    features.sort(key=lambda item: abs(float(item["value"])), reverse=True)
    severity = "watch" if len(group_counts) > 1 or features else "normal"
    return {
        "featureProjection": True,
        "topFeatures": features[:5],
        "groupCounts": group_counts,
        "rowCount": len(rows),
        "severity": severity,
    }


def event_signal(instance: dict[str, Any], rows: list[dict[str, Any]]) -> dict[str, Any]:
    config = instance.get("config") or {}
    field = config.get("event_type_field") or "event_type"
    time_field = config.get("time_field") or config.get("x_field") or "time"
    label_field = config.get("label_field") or "label"
    events = []
    for row in rows:
        events.append({
            "type": str(row.get(field) or row.get(label_field) or "event"),
            "time": row.get(time_field),
            "label": row.get(label_field),
        })
    severity = "candidate" if events else "normal"
    return {"events": [item["type"] for item in events], "eventDetails": events, "rowCount": len(rows), "severity": severity}


def heatmap_signal(instance: dict[str, Any], rows: list[dict[str, Any]]) -> dict[str, Any]:
    config = instance.get("config") or {}
    x_values = config.get("x_values") or []
    y_field = str(config.get("y_field") or "row")
    values_field = str(config.get("values_field") or "values")
    cells: list[dict[str, Any]] = []
    for row in rows:
        values = row.get(values_field)
        if not isinstance(values, list):
            continue
        y_value = row.get(y_field)
        for idx, value in enumerate(values):
            if not isinstance(value, (int, float)):
                continue
            x_value = x_values[idx] if idx < len(x_values) else idx + 1
            cells.append({"x": x_value, "y": y_value, "value": value})
    if not cells:
        return {"rowCount": len(rows), "severity": "normal"}
    cells.sort(key=lambda item: item["value"], reverse=True)
    top = cells[0]
    by_x: dict[Any, float] = {}
    for cell in cells:
        by_x[cell["x"]] = by_x.get(cell["x"], 0.0) + float(cell["value"])
    top_columns = sorted(by_x.items(), key=lambda item: item[1], reverse=True)[:5]
    markers = [
        marker.get("x")
        for marker in (config.get("vertical_markers") or [])
        if isinstance(marker, dict) and marker.get("x") is not None
    ]
    marker_hits = [x for x in markers if x in {item[0] for item in top_columns[:3]}]
    threshold = config.get("highlight_threshold")
    if threshold is None:
        threshold = config.get("value_max")
    severity = "candidate" if marker_hits or float(top["value"]) >= 0.75 else "watch" if float(top["value"]) >= 0.5 else "normal"
    return {
        "matrix": True,
        "rowCount": len(rows),
        "cellCount": len(cells),
        "topCell": top,
        "topCells": cells[:8],
        "topColumns": [{"x": x, "total": total} for x, total in top_columns],
        "markerHits": marker_hits,
        "valueMin": config.get("value_min"),
        "valueMax": config.get("value_max"),
        "threshold": threshold,
        "severity": severity,
    }


def analyze_signal(payload: dict[str, Any], instance: dict[str, Any]) -> dict[str, Any]:
    rows = data_for(payload, instance)
    component_type = str(instance.get("componentType") or "")
    if component_type in {"trend_line", "raw_signal_trend", "detector_statistic_view", "distance_metric_view", "performance_metric_view", "control_chart", "cumulative_curve", "adaptive_model_structure_view"}:
        return line_signal(instance, rows)
    if component_type == "model_diagnostic_curve":
        return model_diagnostic_signal(instance, rows)
    if component_type in {"distribution_view", "distribution_summary_plot", "histogram_view", "circular_histogram"}:
        return distribution_signal(instance, rows)
    if component_type in {"bar_chart", "ranking_view", "contribution_view", "proportion_view", "reference_current_comparison", "p_value_view"}:
        return bar_signal(instance, rows)
    if component_type in {"state_timeline", "window_view"}:
        return timeline_signal(instance, rows)
    if component_type == "small_multiple_lines":
        return small_multiple_signal(instance, rows)
    if component_type == "feature_projection_view":
        return feature_projection_signal(instance, rows)
    if component_type == "projection_scatter":
        return scatter_signal(instance, rows)
    if component_type == "event_marker":
        return event_signal(instance, rows)
    if component_type == "event_raster":
        return event_raster_signal(instance, rows)
    if component_type == "node_link_diagram":
        return node_link_signal(instance, rows)
    if component_type == "heatmap":
        return heatmap_signal(instance, rows)
    if component_type == "matrix_view":
        return matrix_signal(instance, rows)
    if component_type == "forest_plot":
        return forest_signal(instance, rows)
    if component_type == "decision_card":
        return card_signal(instance, rows)
    return {"rowCount": len(rows), "severity": "normal"}

def component_note_text(instance: dict[str, Any], signal: dict[str, Any], knowledge: ComponentKnowledge, payload: dict[str, Any] | None = None) -> tuple[str, str, str]:
    component_type = str(instance.get("componentType") or "component")
    area = str(instance.get("area") or "")
    area_label = str((instance.get("config") or {}).get("title") or area or component_type)
    title = f"{area_label} 해석"
    visual_note = visual_encoding_note(payload or {}, instance)
    if area == "notes":
        return title, "이 영역은 그래프가 아니라 chart 해석과 범례를 표시하는 보조 notes 영역이다.", "전체 해석의 근거 component로 사용하지 않는다."
    if signal.get("diagnosticCurve"):
        max_point = signal.get("maxGapPoint") or {}
        summary = f"diagnostic curve는 {signal.get('pointCount')}개 point로 구성되고 random diagonal 대비 최대 gap은 {format_num(signal.get('maxVerticalGap'))}이다."
        detail = f"{visual_note} 이 curve는 {signal.get('xField')}와 {signal.get('yField')}의 관계를 보여준다. random diagonal과 비교할 때 가장 큰 분리 지점은 x={format_num(max_point.get('x'))}, y={format_num(max_point.get('y'))}이며 gap은 {format_num(signal.get('maxVerticalGap'))}이다. annotation은 `{signal.get('annotationText')}`를 제공한다. curve가 diagonal보다 위에 있다는 것은 구간 분리 가능성을 뜻하지만 원인을 확정하지는 않는다."
        return title, summary, detail
    if signal.get("featureProjection"):
        top_features = signal.get("topFeatures") or []
        feature_text = ", ".join(f"{item.get('feature')} {format_num(item.get('value'))}" for item in top_features[:4]) or "없음"
        groups = ", ".join(f"{key} {value}건" for key, value in (signal.get("groupCounts") or {}).items()) or "없음"
        summary = f"상위 feature importance는 {feature_text}이고 projection group은 {groups}이다."
        detail = f"{visual_note} 이 component는 feature importance bar와 baseline/current projection point를 함께 보여준다. 상위 feature는 {feature_text}이며, projection point 구성은 {groups}이다. 중요 feature는 classifier가 구간을 나누는 데 쓴 설명 후보일 뿐, feature drift의 원인이나 인과 관계를 단독으로 확정하지 않는다."
        return title, summary, detail
    if signal.get("distribution"):
        primary_peak = signal.get("primaryPeak") or {}
        secondary_peak = signal.get("secondaryPeak") or {}
        count_peak = signal.get("countPeak") or {}
        top_gap = signal.get("topGap") or {}
        if primary_peak and secondary_peak:
            summary = f"{signal.get('primaryField')} peak는 x={format_num(primary_peak.get('x'))}, {signal.get('secondaryField')} peak는 x={format_num(secondary_peak.get('x'))}로 peak shift는 {format_num(signal.get('peakShift'))}이다."
            detail = f"{visual_note} 분포 component는 x축 {signal.get('xField')}에서 {signal.get('primaryField')}와 {signal.get('secondaryField')} 값을 비교한다. {signal.get('primaryField')} 최대는 x={format_num(primary_peak.get('x'))}, 값 {format_num(primary_peak.get('primary'))}이고, {signal.get('secondaryField')} 최대는 x={format_num(secondary_peak.get('x'))}, 값 {format_num(secondary_peak.get('secondary'))}이다. 가장 큰 bin 차이는 x={format_num(top_gap.get('x'))}에서 {format_num(top_gap.get('gap'))}이며, 분포 이동은 원인 확정이 아니라 후속 segment/feature 확인 대상이다."
        elif count_peak:
            summary = f"가장 큰 histogram bin은 x={format_num(count_peak.get('x'))}, count {format_num(count_peak.get('count'))}이다."
            detail = f"{visual_note} histogram은 x축 {signal.get('xField')}의 bin별 count를 비교한다. 최대 bin은 x={format_num(count_peak.get('x'))}, count {format_num(count_peak.get('count'))}이며, 총 {signal.get('rowCount')}개 row가 제공된다. 단일 bin의 크기만으로 drift 원인을 확정하지 않는다."
        else:
            summary = f"분포 component는 {signal.get('rowCount')}개 row로 구성된다."
            detail = f"{visual_note} 분포 component는 제공된 bin/score row를 비교한다. peak나 gap을 계산할 수 있는 값 field가 부족하면 chart-level guide와 인접 component를 함께 확인해야 한다."
        return title, summary, detail
    if signal.get("smallMultiple"):
        top = signal.get("topChange") or {}
        series_text = ", ".join(
            f"{item.get('series')} {format_num(item.get('first'))}->{format_num(item.get('latest'))}"
            for item in (signal.get("series") or [])[:6]
        )
        summary = f"가장 큰 series 변화는 {top.get('series')}의 {format_num(top.get('change'))}이다."
        detail = f"{visual_note} small multiple lines는 {signal.get('seriesField')}별 {signal.get('yField')} 변화를 분리해 보여준다. 주요 series 흐름은 {series_text}이며, 가장 큰 변화는 {top.get('series')}에서 나타난다. 여러 패널의 동시 변화는 공통 drift 후보일 수 있지만 원인 확정 근거는 아니다."
        return title, summary, detail
    if signal.get("eventRaster"):
        lane_text = ", ".join(f"{key} {value}건" for key, value in (signal.get("laneCounts") or {}).items())
        type_text = ", ".join(f"{key} {value}건" for key, value in (signal.get("typeCounts") or {}).items())
        summary = f"event raster는 {signal.get('rowCount')}개 event를 {signal.get('timeMin')}~{signal.get('timeMax')} 구간에 표시한다."
        detail = f"{visual_note} event raster는 시간축 {signal.get('timeField')}와 lane {signal.get('laneField')} 기준으로 event 발생을 배열한다. lane별 건수는 {lane_text}, event type별 건수는 {type_text}이다. event 밀집은 확인 시점을 좁히는 근거이며 원인을 단독으로 증명하지 않는다."
        return title, summary, detail
    if signal.get("nodeLink"):
        summary = f"node-link diagram은 node {signal.get('nodeCount')}개와 link {signal.get('linkCount')}개를 표시한다."
        detail = f"{visual_note} node-link diagram은 관계 구조를 보여주는 context visual이다. 제공 데이터 기준 node {signal.get('nodeCount')}개, link {signal.get('linkCount')}개이며 최대 link weight는 {format_num(signal.get('maxWeight'))}이다. 연결 구조는 설명 후보를 제공하지만, drift 원인 확정에는 별도 feature/segment 근거가 필요하다."
        return title, summary, detail
    if signal.get("matrix"):
        top_cell = signal.get("topCell") or {}
        top_columns = signal.get("topColumns") or []
        column_text = ", ".join(
            f"x={item.get('x')} 합계 {format_num(item.get('total'))}"
            for item in top_columns[:3]
        )
        marker_hits = ", ".join(str(x) for x in signal.get("markerHits") or []) or "없음"
        summary = f"가장 강한 heatmap cell은 x={top_cell.get('x')}, y={top_cell.get('y')}의 {format_num(top_cell.get('value'))}이다."
        detail = f"{visual_note} heatmap은 {signal.get('rowCount')}개 행과 {signal.get('cellCount')}개 cell의 값 강도를 비교한다. 열 기준 상위 구간은 {column_text}이며, 주요 marker와 겹치는 상위 열은 {marker_hits}이다. 값 범위 설정은 {format_num(signal.get('valueMin'))}~{format_num(signal.get('valueMax'))}로 제공되어 있으므로 실제 cell 값과 색상 포화 여부를 함께 확인해야 한다. 높은 cell은 변화 후보 위치를 좁히는 근거이지 원인 확정 근거는 아니다."
        return title, summary, detail
    if signal.get("matrixNumeric"):
        top_abs = signal.get("topAbs") or {}
        positive = signal.get("positive") or {}
        negative = signal.get("negative") or {}
        summary = f"가장 큰 절대 차이는 {top_abs.get('category')}의 {top_abs.get('displayValue')}이다."
        detail = f"{visual_note} 이 matrix는 {signal.get('categoryField')}별 {signal.get('valueField')} 값을 셀로 비교한다. 가장 큰 양의 값은 {positive.get('category')} {format_num(positive.get('value'))}, 가장 큰 음의 값은 {negative.get('category')} {format_num(negative.get('value'))}이다. 양수는 관측이 기대보다 많은 방향, 음수는 기대보다 적은 방향으로 읽되, matrix만으로 원인을 확정하지 않고 grouped bar와 기여도 bar를 함께 확인한다."
        return title, summary, detail
    if signal.get("categoryValues") and len(signal.get("categoryValues") or []) >= 2 and component_type == "proportion_view":
        values = signal.get("categoryValues") or []
        first = values[0]
        latest = values[-1]
        delta = None
        if first.get("value") is not None and latest.get("value") is not None:
            delta = float(latest["value"]) - float(first["value"])
        summary = f"{signal.get('valueField')}는 {first.get('category')} {format_num(first.get('value'))}에서 {latest.get('category')} {format_num(latest.get('value'))}로 변했다."
        detail = f"{visual_note} 이 proportion component는 {signal.get('categoryField')}별 {signal.get('valueField')} 값을 막대로 비교한다. {first.get('category')} 값은 {format_num(first.get('value'))}, {latest.get('category')} 값은 {format_num(latest.get('value'))}이며 차이는 {format_num(delta)}이다. 비율 차이는 표본 수와 검정 통계, interval을 함께 확인해야 하며 단독으로 원인을 확정하지 않는다."
        return title, summary, detail
    if signal.get("contingency"):
        groups = signal.get("groups") or []
        first = groups[0] if groups else {}
        latest = groups[-1] if groups else {}
        first_rate = format_num(first.get("rate"))
        latest_rate = format_num(latest.get("rate"))
        delta = None
        if first.get("rate") is not None and latest.get("rate") is not None:
            delta = latest["rate"] - first["rate"]
        summary = f"event rate는 {first.get('label')} {first_rate}에서 {latest.get('label')} {latest_rate}로 변했다."
        detail = f"{visual_note} 2x2 mosaic은 각 구간의 event와 non-event count를 함께 보여준다. {first.get('label')}는 event {format_num(first.get('event'))}/{format_num(first.get('total'))}, {latest.get('label')}는 event {format_num(latest.get('event'))}/{format_num(latest.get('total'))}이며 event rate 변화는 {format_num(delta)}이다. 작은 표본의 비율 차이는 Fisher p-value와 odds ratio interval을 함께 확인해야 하며, count 차이만으로 원인을 확정하지 않는다."
        return title, summary, detail
    if signal.get("forest"):
        excludes = signal.get("excludesNull")
        relation = "null 값을 벗어난다" if excludes else "null 값을 포함한다" if excludes is False else "null 관계를 판단하기 어렵다"
        summary = f"odds ratio는 {format_num(signal.get('value'))}, interval은 [{format_num(signal.get('low'))}, {format_num(signal.get('high'))}]로 {relation}."
        detail = f"{visual_note} forest plot은 효과 크기 {signal.get('valueField')}와 uncertainty interval을 null={format_num(signal.get('nullValue'))} 기준선과 비교한다. 현재 odds ratio {format_num(signal.get('value'))}, interval [{format_num(signal.get('low'))}, {format_num(signal.get('high'))}]이며, interval이 null 기준선을 벗어나는지 확인해 event odds 증가 신호의 불확실성을 읽는다. 효과 크기는 association evidence이지 원인 확정은 아니다."
        return title, summary, detail
    if "latest" in signal:
        latest = format_num(signal.get("latest"))
        previous = format_num(signal.get("previous"))
        first = format_num(signal.get("first"))
        min_value = format_num(signal.get("min"))
        min_x = signal.get("minX")
        max_value = format_num(signal.get("max"))
        max_x = signal.get("maxX")
        threshold = format_num(signal.get("threshold"))
        slope = signal.get("slope")
        total_change = signal.get("totalChange")
        slope_text = "상승" if slope is not None and slope > 0 else "하락" if slope is not None and slope < 0 else "보합"
        total_text = "증가" if total_change is not None and total_change > 0 else "감소" if total_change is not None and total_change < 0 else "변화 없음"
        secondary_latest = format_num(signal.get("secondaryLatest"))
        secondary_first = format_num(signal.get("secondaryFirst"))
        secondary_max = format_num(signal.get("secondaryMax"))
        relation = signal.get("relation") or "기준 정보 없음"
        if component_type == "performance_metric_view":
            summary = f"온라인 정확도는 시작 {first}에서 최신 {latest}로 {total_text}했고, 최근 구간은 {previous}에서 {latest}로 {slope_text}했다."
            detail = f"{visual_note} 이 component는 시간축({signal.get('xField')})에 따른 성능값({signal.get('yField')}) 변화를 보여준다. 현재 payload에서는 최솟값 {min_value}가 t={min_x}에서 나타나며 최댓값 {max_value}는 t={max_x}이다. 명시 임계값이 없으므로 정확도 하락 자체를 drift 확정으로 보지 않고, detector 상태나 event marker와 함께 읽어야 한다."
            return title, summary, detail
        if component_type == "adaptive_model_structure_view":
            summary = f"주 트리 크기는 시작 {first}에서 최신 {latest}로 {total_text}했고, 보조 트리 최신값은 {secondary_latest}이다."
            detail = f"{visual_note} 이 component는 main tree와 alternate/secondary tree 크기의 변화를 함께 보여준다. 주 값은 최근 {previous}에서 {latest}로 {slope_text}이며, 보조 값은 시작 {secondary_first}, 최신 {secondary_latest}, 최대 {secondary_max}로 나타난다. 보조 트리 성장은 replacement 후보 구조가 준비되는 신호로 볼 수 있지만, 구조 변화만으로 drift 원인을 확정하지 않는다."
            return title, summary, detail
        if signal.get("secondaryField") and signal.get("maxSecondaryGap"):
            gap = signal.get("maxSecondaryGap") or {}
            summary = f"{signal.get('secondaryField')}와 {signal.get('yField')}의 최대 차이는 x={gap.get('x')}에서 {format_num(gap.get('gap'))}이다."
            detail = f"{visual_note} 이 component는 x축 {signal.get('xField')}에서 {signal.get('yField')}와 {signal.get('secondaryField')} 두 선을 비교한다. 시작값은 {first}, 최신 주 값은 {latest}, 최신 보조 값은 {secondary_latest}이며, 가장 큰 선 간 차이는 x={gap.get('x')}에서 주 값 {format_num(gap.get('primary'))}, 보조 값 {format_num(gap.get('secondary'))}, 차이 {format_num(gap.get('gap'))}로 나타난다. 선 간 차이는 분포/성능 차이 후보를 좁히는 근거이며 원인 확정 근거는 아니다."
            return title, summary, detail
        if relation == "above_threshold":
            summary = f"현재 값 {latest}가 기준선 {threshold}를 넘어 drift 후보로 해석된다."
        elif relation in {"below_but_recent_touch", "below_but_near_threshold", "rising_toward_threshold"}:
            summary = f"현재 값 {latest}는 기준선 {threshold} 아래지만, 최근 최대값 {format_num(signal.get('recentMax'))}와 {slope_text} 추세를 보면 관찰이 필요하다."
        elif signal.get("threshold") is not None:
            summary = f"현재 값 {latest}는 기준선 {threshold} 아래로 기준 초과 신호는 뚜렷하지 않다."
        else:
            summary = f"최신 값은 {latest}이고 최근 추세는 {slope_text}이다."
        detail = f"{visual_note} 시작값 {first}, 최솟값 {min_value}(x={min_x}), 최댓값 {max_value}(x={max_x})를 함께 보면 현재 선형 component의 변화 범위를 확인할 수 있다. 기준선이나 event marker가 있으면 해당 시점 전후의 방향과 지속성을 함께 확인하고, 값 변화만으로 원인을 확정하지 않는다."
        return title, summary, detail
    if signal.get("top"):
        top = signal["top"]
        summary = f"{top.get('category')} 항목의 값/변화량 {top.get('displayValue')}가 가장 두드러진 변화 후보다."
        values = signal.get("categoryValues") or []
        value_text = ", ".join(
            f"{item.get('category')} {item.get('displayValue')}"
            for item in values[:6]
        )
        threshold = (instance.get("config") or {}).get("threshold")
        threshold_text = f" 기준선/threshold {format_num(threshold)}와 비교한다." if threshold is not None else ""
        detail = f"{visual_note} 항목별 막대는 {signal.get('valueField')} 값을 비교한다. 주요 값은 {value_text}이며, 가장 큰 항목은 {top.get('category')} {top.get('displayValue')}이다.{threshold_text} 막대 순위는 어느 방향 또는 category가 지배적인지 보여주지만, 원인 확정 근거는 아니다."
        return title, summary, detail
    if signal.get("metrics"):
        pairs = ", ".join(f"{item['label']} {item['value']}" for item in signal["metrics"][:4])
        return title, f"요약 카드는 {pairs}를 표시해 이번 분석 대상과 수신 범위를 알려준다.", f"{visual_note} 이 카드는 판정 자체보다 분석 맥락을 제공하므로 다른 그래프 component의 증거와 함께 읽는다."
    if signal.get("sequence"):
        sequence = " -> ".join(signal["sequence"])
        segment_text = ", ".join(
            f"{item.get('role')}({item.get('start')}~{item.get('end')})"
            for item in signal.get("segments", [])[:6]
        )
        return title, f"감지기 상태는 {sequence} 순서로 전환된다.", f"{visual_note} 표시 구간은 {segment_text}이다. warning/alternate/replace 흐름은 감지기가 변화 후보를 보고 대체 구조를 준비한 뒤 교체 단계로 이동했는지 확인하는 근거다. 상태 전환만으로 원인을 확정하지 않고 성능 추세와 이벤트 marker를 함께 확인한다."
    if signal.get("events"):
        event_text = ", ".join(
            f"{item.get('type')}@{item.get('time')}"
            for item in signal.get("eventDetails", [])[:6]
        ) or ", ".join(signal["events"][:4])
        return title, f"이벤트 marker는 {event_text} 시점을 강조한다.", f"{visual_note} 이벤트 marker는 원인 확정이 아니라 관련 그래프에서 전후 변화가 있는지 확인해야 할 기준 시점이다."
    if signal.get("groupCounts"):
        groups = ", ".join(f"{key} {value}건" for key, value in signal["groupCounts"].items())
        diag = signal.get("maxDiagonalGap") or {}
        centroid_text = f" centroid distance는 {format_num(signal.get('centroidDistance'))}이다." if signal.get("centroidDistance") is not None else ""
        diag_text = f" 대각선 기준 최대 이탈은 x={format_num(diag.get('x'))}, y={format_num(diag.get('y'))}, gap {format_num(diag.get('gap'))}이다." if diag else ""
        return title, f"그룹별 분포는 {groups}으로 나타난다.", f"분포 차이는 표본 구성과 축 설정을 함께 확인한다.{centroid_text}{diag_text} 이 값은 위치 차이를 설명하는 근거이며 원인을 단정하지 않는다."
    return title, f"{component_type}는 chart의 보조 정보를 표시한다.", "현재 payload에서 전용 signal을 충분히 계산하지 못했다. 제공된 data sample, chart-specific guide, 인접 component를 함께 확인하고 원인 단정은 피한다."



class SafeFormatDict(dict):
    def __missing__(self, key: str) -> str:
        return "{" + key + "}"


def render_prompt_template(template: str, values: dict[str, Any]) -> str:
    return template.format_map(SafeFormatDict(values))


def prompt_file_text(prompt_key: str) -> str:
    path = PROMPT_TEMPLATE_DIR / f"{prompt_key}.txt"
    return path.read_text(encoding="utf-8")


def ensure_prompt_template_table() -> None:
    with db_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                create table if not exists llm_prompt_template (
                    prompt_key text primary key,
                    prompt_text text not null,
                    description text,
                    created_at timestamptz not null default now(),
                    updated_at timestamptz not null default now()
                )
                """
            )


def prompt_template_text(prompt_key: str) -> str:
    try:
        ensure_prompt_template_table()
        with db_conn() as conn:
            with conn.cursor(row_factory=psycopg.rows.dict_row) as cur:
                cur.execute("select prompt_text from llm_prompt_template where prompt_key = %s", (prompt_key,))
                row = cur.fetchone()
                if row and row.get("prompt_text"):
                    return str(row["prompt_text"])
                file_text = prompt_file_text(prompt_key)
                cur.execute(
                    """
                    insert into llm_prompt_template (prompt_key, prompt_text, description)
                    values (%s, %s, %s)
                    on conflict (prompt_key) do update
                    set prompt_text = excluded.prompt_text,
                        description = excluded.description,
                        updated_at = now()
                    """,
                    (prompt_key, file_text, "Chart interpretation prompt template seeded from docs/prompts"),
                )
                return file_text
    except Exception:
        try:
            return prompt_file_text(prompt_key)
        except OSError:
            return (
                "Return only the requested result.\n"
                "Schema:\n{schema}\n\n"
                "Guide:\n{guide}\n\n"
                "Task: {task_kind}\n\n"
                "Draft:\n{draft}\n\n"
                "Material:\n{material}\n"
            )


def save_llm_run(prompt_key: str, prompt: str, stdout: str, stderr: str, returncode: int) -> None:
    try:
        PROMPT_RUN_DIR.mkdir(parents=True, exist_ok=True)
        run_id = f"{int(time.time())}_{uuid.uuid4().hex[:8]}"
        run_path = PROMPT_RUN_DIR / f"{run_id}_{prompt_key}_llm.json"
        run_path.write_text(
            json.dumps(
                {
                    "promptKey": prompt_key,
                    "returncode": returncode,
                    "prompt": prompt,
                    "stdout": stdout,
                    "stderr": stderr,
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
    except Exception:
        return
def run_llm_polish(kind: str, payload: dict[str, Any], draft: str) -> str | None:
    if not LLM_ENDPOINT or not LLM_MODEL:
        return None
    prompt_key = f"{kind}_interpretation"
    schema = interpretation_schema_text() if kind == "chart" else "Return only final Korean text."
    system_prompt = (
        "You are a Korean report-style chart interpretation assistant. "
        "Use only the supplied chart payload, database guidance, and draft evidence. "
        "Do not invent values, root causes, business impact, or confirmed drift. "
        "For timed extrema and transitions, use timeEvidence rows as authoritative evidence. "
        "Keep the extremum time separate from an event time; never infer one from the other. "
        "Do not assert a time absent from the supplied evidence. "
        "Encode line breaks with standard JSON newline escapes, not double-escaped literal backslash-n. "
        "For chart tasks, return a JSON object matching the supplied schema. "
        "For component tasks, return concise Korean interpretation text.\n\n"
        f"Task kind: {kind}\n"
        f"Output schema: {schema}\n\n"
        f"Interpretation guide:\n{interpretation_guide_text()}"
    )
    user_payload = {
        "taskKind": kind,
        "draft": draft,
        "payload": payload,
    }
    user_prompt = json.dumps(user_payload, ensure_ascii=False, sort_keys=True)
    request_body = {
        "model": LLM_MODEL,
        "temperature": 0,
        "max_tokens": 6000,
        "reasoning_effort": "low",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    }
    request_text = json.dumps(request_body, ensure_ascii=False)
    headers = {"Content-Type": "application/json"}
    if LLM_API_KEY:
        headers["Authorization"] = f"Bearer {LLM_API_KEY}"

    last_error = ""
    for attempt in range(max(0, LLM_RETRY_COUNT) + 1):
        try:
            request = urllib.request.Request(
                LLM_ENDPOINT,
                data=request_text.encode("utf-8"),
                headers=headers,
                method="POST",
            )
            with urllib.request.urlopen(request, timeout=LLM_TIMEOUT_SECONDS) as response:
                response_text = response.read().decode("utf-8", errors="replace")
            response_json = json.loads(response_text)
            choices = response_json.get("choices") or []
            message = choices[0].get("message") if choices else None
            content = message.get("content") if isinstance(message, dict) else None
            if not isinstance(content, str) or not content.strip():
                raise ValueError("LLM response choices[0].message.content is empty")
            save_llm_run(prompt_key, request_text, content, "", 0)
            return content.strip()
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, ValueError, json.JSONDecodeError) as exc:
            last_error = str(exc)
            if attempt < max(0, LLM_RETRY_COUNT):
                time.sleep(0.2)
        except Exception as exc:
            last_error = str(exc)
            if attempt < max(0, LLM_RETRY_COUNT):
                time.sleep(0.2)
    save_llm_run(prompt_key, request_text, "", last_error, 1)
    return None

def interpret_component(payload: dict[str, Any], instance: dict[str, Any], use_codex: bool = True) -> dict[str, Any]:
    component_type = str(instance.get("componentType") or "component")
    knowledge = component_knowledge(component_type)
    signal = analyze_signal(payload, instance)
    title, summary, detail = component_note_text(instance, signal, knowledge, payload)
    rows = data_for(payload, instance)
    polished = None
    if use_codex:
        polish_context = {
            "chartId": payload.get("chartId"),
            "component": instance,
            "componentKnowledge": component_knowledge_context(knowledge),
            "componentGuide": component_guide_text(component_type),
            "signal": signal,
            "dataSample": sample_rows(rows),
        }
        polished = run_llm_polish("component", polish_context, f"{summary}\n{detail}")
        if polished:
            detail = polished
    return {
        "componentInstanceId": instance.get("componentInstanceId"),
        "componentType": component_type,
        "severity": signal.get("severity", "normal"),
        "title": title,
        "summary": summary,
        "detail": detail,
        "signal": signal,
        "provider": "openai_compatible" if polished else "rule",
    }



def area_metadata(payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        str(area.get("area")): area
        for area in ((payload.get("layout") or {}).get("areas") or [])
        if isinstance(area, dict) and area.get("area") is not None
    }


def component_chart_context(payload: dict[str, Any], instance: dict[str, Any], note: dict[str, Any]) -> dict[str, Any]:
    component_type = str(instance.get("componentType") or "component")
    knowledge = component_knowledge(component_type)
    rows = data_for(payload, instance)
    area_name = str(instance.get("area") or "")
    area = area_metadata(payload).get(area_name, {})
    # Keep exact rows for secondary extrema and resets in the LLM-only context.
    # Sampling can omit the peak immediately before a replacement event.
    config = instance.get("config") or {}
    secondary_field = config.get("secondary_value_field")
    time_evidence = []
    if secondary_field:
        secondary_rows = [row for row in rows if num(row.get(secondary_field)) is not None]
        if secondary_rows:
            peak = max(num(row.get(secondary_field)) for row in secondary_rows)
            time_evidence = [row for row in secondary_rows if num(row.get(secondary_field)) == peak]
            for previous, current in zip(secondary_rows, secondary_rows[1:]):
                if num(previous.get(secondary_field)) != 0 and num(current.get(secondary_field)) == 0:
                    if previous not in time_evidence:
                        time_evidence.append(previous)
                    if current not in time_evidence:
                        time_evidence.append(current)
    return {
        "componentInstanceId": instance.get("componentInstanceId"),
        "componentType": component_type,
        "area": instance.get("area"),
        "areaTitle": area.get("title"),
        "areaRole": area.get("role"),
        "config": instance.get("config") or {},
        "dataBinding": instance.get("dataBinding") or {},
        "componentKnowledge": component_knowledge_context(knowledge),
        "componentGuide": component_guide_text(component_type),
        "llmComponentContext": llm_component_context(component_type),
        "visualEncodingHint": visual_encoding_note(payload, instance),
        "signal": note.get("signal") or {},
        "machineObservation": {
            "severity": note.get("severity"),
            "title": note.get("title"),
            "summary": note.get("summary"),
            "detail": note.get("detail"),
            "note": "Machine-extracted observation only. Use as evidence; do not copy wording as final prose.",
        },
        "dataSample": sample_rows(rows),
        "timeEvidence": time_evidence,
    }

def chart_note(payload: dict[str, Any], component_notes: list[dict[str, Any]], question: str = "") -> dict[str, Any]:
    chart_id = str(payload.get("chartId") or "chart")
    guide = chart_guide(chart_id)
    llm_chart_contexts = llm_chart_context(payload, chart_id)
    max_note = max(component_notes, key=lambda note: SEVERITY_RANK.get(str(note.get("severity")), 0), default={"severity": "normal"})
    severity = str(max_note.get("severity") or "normal")
    watch_notes = [note for note in component_notes if note.get("severity") in {"watch", "candidate"}]
    lead = "drift 후보 신호가 뚜렷하다" if severity == "candidate" else "주의 관찰이 필요하다" if severity == "watch" else "안정적인 상태로 보인다"
    evidence = " ".join(note.get("summary", "") for note in watch_notes[:3]) or " ".join(note.get("summary", "") for note in component_notes[:2])
    summary = f"{chart_id}는 component별 근거를 종합할 때 {lead}. {evidence}".strip()
    fallback_detail = (
        f"{chart_id}는 chart component들의 값을 함께 읽어 판단한다. "
        f"핵심 근거는 {evidence} "
        "각 component의 수치와 marker, threshold, interval을 함께 확인해야 하며, 이 차트만으로 원인이나 업무 영향을 확정하지 않는다."
    )
    chart_components = [component for component in (payload.get("components") or []) if isinstance(component, dict)]
    component_contexts = [
        component_chart_context(payload, component, note)
        for component, note in zip(chart_components, component_notes)
    ]
    evidence_lines = []
    for context in component_contexts:
        observation = context.get("machineObservation") or {}
        title = context.get("areaTitle") or context.get("componentType")
        summary_text = str(observation.get("summary") or "").strip()
        detail_text = str(observation.get("detail") or "").strip()
        signal_text = json.dumps(context.get("signal") or {}, ensure_ascii=False, sort_keys=True)[:900]
        evidence_lines.append(
            f"- {title} ({context.get('componentType')}, {context.get('componentInstanceId')}): "
            f"{summary_text}\n  component_note_detail: {detail_text}\n  signal: {signal_text}"
        )
    detail_parts = [
        "The following machine observations, visual encoding hints, signals, and data samples are current chart material for the LLM. They are not final prose and must not be copied mechanically.",
        "Current component material:\n" + "\n".join(evidence_lines),
    ]
    if llm_chart_contexts:
        detail_parts.append(
            "LLM chart interpretation contexts:\n"
            + json.dumps(llm_chart_contexts, ensure_ascii=False, sort_keys=True)[:5000]
        )
    detail = "\n\n".join(detail_parts)
    polished = run_llm_polish(
        "chart",
        {
            "chartId": chart_id,
            "chartTitle": payload.get("title"),
            "chartGuide": guide,
            "chartSpecificGuide": chart_specific_guide_text(chart_id),
            "activeComponentGuides": {
                component_type: component_guide_text(component_type)
                for component_type in sorted({
                    str(component.get("componentType") or "")
                    for component in chart_components
                    if isinstance(component, dict) and component.get("componentType")
                })
                if component_guide_text(component_type)
            },
            "llmChartContexts": llm_chart_contexts,
            "analysisContext": payload.get("analysisContext") or {},
            "layout": payload.get("layout") or {},
            "componentContexts": component_contexts,
            "machineComponentNotes": component_notes,
            "userQuestion": question,
        },
        f"{summary}\n{fallback_detail}",
    )
    prompt_leak_markers = (
        "Current component material",
        "component_note_detail:",
        "machine observations",
        "signal: {",
        "The following machine observations",
    )
    if polished and any(marker in polished for marker in prompt_leak_markers):
        polished = None
    if polished:
        structured = chart_output_from_codex(polished)
        if structured:
            summary = structured["summary"]
            detail = structured["detail"]
            if structured.get("componentNotes"):
                llm_by_id = {note["componentInstanceId"]: note for note in structured["componentNotes"]}
                merged_notes = []
                for fallback in component_notes:
                    component_id = str(fallback.get("componentInstanceId") or "")
                    llm_note = llm_by_id.get(component_id)
                    if llm_note:
                        merged_notes.append({**fallback, **llm_note, "signal": fallback.get("signal"), "componentType": fallback.get("componentType")})
                    else:
                        merged_notes.append(fallback)
                component_notes[:] = merged_notes
        else:
            detail = polished.replace("\\r\\n", "\n").replace("\\n", "\n")
            codex_summary = summary_from_text(polished)
            if codex_summary:
                summary = ensure_sentence_punctuation(codex_summary)
    else:
        detail = fallback_detail
    return {
        "severity": severity,
        "title": f"{chart_id} 종합 해석",
        "summary": summary,
        "detail": detail,
        "provider": "openai_compatible" if polished else "rule",
    }

TRANSIENT_PAYLOAD_KEYS = {"requestNonce", "_requestNonce", "cacheBust", "_cacheBust"}


def normalized_for_cache(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            key: normalized_for_cache(item)
            for key, item in sorted(value.items())
            if key not in TRANSIENT_PAYLOAD_KEYS
        }
    if isinstance(value, list):
        return [normalized_for_cache(item) for item in value]
    return value


def payload_hash(payload: dict[str, Any], question: str = "") -> str:
    cache_material = {
        "payload": normalized_for_cache(payload),
        "question": " ".join(str(question or "").split()),
    }
    encoded = json.dumps(cache_material, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def build_chart_interpretation(payload: dict[str, Any], question: str = "") -> dict[str, Any]:
    components = payload.get("components") or []
    if not isinstance(components, list):
        raise ValueError("payload.components array is required")
    component_notes = [interpret_component(payload, component, use_codex=False) for component in components if isinstance(component, dict)]
    return {
        "ok": True,
        "chartId": payload.get("chartId"),
        "componentNotes": component_notes,
        "chartNote": chart_note(payload, component_notes, question=question),
    }


def public_job(job: dict[str, Any]) -> dict[str, Any]:
    return {
        "ok": True,
        "jobId": job["jobId"],
        "chartId": job.get("chartId"),
        "status": job["status"],
        "payloadHash": job.get("payloadHash"),
        "question": job.get("question"),
        "createdAt": job.get("createdAt"),
        "startedAt": job.get("startedAt"),
        "finishedAt": job.get("finishedAt"),
        "result": job.get("result"),
        "error": job.get("error"),
    }


def chart_job_worker() -> None:
    while True:
        job_id = JOB_QUEUE.get()
        try:
            with JOBS_LOCK:
                job = JOBS.get(job_id)
                if not job or job.get("status") != "queued":
                    continue
                job["status"] = "running"
                job["startedAt"] = time.time()
                payload = job["payload"]
                question = str(job.get("question") or "")
            try:
                result = build_chart_interpretation(payload, question=question)
            except Exception as exc:
                with JOBS_LOCK:
                    job = JOBS.get(job_id)
                    if job:
                        job["status"] = "failed"
                        job["error"] = str(exc)
                        job["finishedAt"] = time.time()
                continue
            with JOBS_LOCK:
                job = JOBS.get(job_id)
                if job:
                    job["status"] = "succeeded"
                    job["result"] = result
                    job["finishedAt"] = time.time()
                    PAYLOAD_CACHE[job["payloadHash"]] = job_id
        finally:
            JOB_QUEUE.task_done()


def ensure_worker_started() -> None:
    global WORKER_STARTED
    if WORKER_STARTED:
        return
    with JOBS_LOCK:
        if WORKER_STARTED:
            return
        worker = threading.Thread(target=chart_job_worker, name="chart-interpretation-worker", daemon=True)
        worker.start()
        WORKER_STARTED = True

@app.get("/api/health")
def health() -> dict[str, Any]:
    db_ok = False if LLM_SKIP_DB else query_one("select 1 ok", ()) is not None
    return {
        "ok": True,
        "service": "chart-interpretation",
        "backend": "fastapi",
        "database": db_ok,
        "llmApi": bool(LLM_ENDPOINT and LLM_MODEL),
        "llmModel": LLM_MODEL,
    }


@app.post("/api/interpret/component")
def interpret_component_endpoint(request: dict[str, Any]) -> dict[str, Any]:
    payload = request.get("payload") or {}
    instance = request.get("component") or {}
    if not isinstance(payload, dict) or not isinstance(instance, dict):
        return {"ok": False, "error": "payload and component objects are required"}
    return {"ok": True, "note": interpret_component(payload, instance)}


@app.post("/api/interpret/chart")
def interpret_chart_endpoint(request: dict[str, Any]) -> dict[str, Any]:
    payload = request.get("payload") or {}
    if not isinstance(payload, dict):
        return {"ok": False, "error": "payload object is required"}
    question = str(request.get("question") or "")
    try:
        return build_chart_interpretation(payload, question=question)
    except Exception as exc:
        return {"ok": False, "error": str(exc)}


@app.post("/api/interpret/chart/jobs")
def create_chart_interpretation_job(request: dict[str, Any]) -> dict[str, Any]:
    ensure_worker_started()
    payload = request.get("payload") or {}
    if not isinstance(payload, dict):
        return {"ok": False, "error": "payload object is required"}
    components = payload.get("components") or []
    if not isinstance(components, list):
        return {"ok": False, "error": "payload.components array is required"}
    question = str(request.get("question") or "")
    p_hash = payload_hash(payload, question=question)
    now = time.time()
    with JOBS_LOCK:
        cached_id = PAYLOAD_CACHE.get(p_hash)
        if cached_id and cached_id in JOBS:
            return public_job(JOBS[cached_id])
        for existing in JOBS.values():
            if existing.get("payloadHash") == p_hash and existing.get("status") in {"queued", "running"}:
                return public_job(existing)
        job_id = str(uuid.uuid4())
        JOBS[job_id] = {
            "jobId": job_id,
            "chartId": payload.get("chartId"),
            "payloadHash": p_hash,
            "payload": payload,
            "question": question,
            "status": "queued",
            "createdAt": now,
            "startedAt": None,
            "finishedAt": None,
            "result": None,
            "error": None,
        }
    JOB_QUEUE.put(job_id)
    with JOBS_LOCK:
        return public_job(JOBS[job_id])


@app.get("/api/interpret/chart/jobs/{job_id}")
def get_chart_interpretation_job(job_id: str) -> dict[str, Any]:
    with JOBS_LOCK:
        job = JOBS.get(job_id)
        if not job:
            return {"ok": False, "error": "job not found", "jobId": job_id}
        return public_job(job)


def main() -> None:
    print(f"Chart interpretation server: http://{HOST}:{PORT}/api/health")
    print("Press Ctrl+C to stop.")
    uvicorn.run(app, host=HOST, port=PORT, log_level="info")


if __name__ == "__main__":
    main()

