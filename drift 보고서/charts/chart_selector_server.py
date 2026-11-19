from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

import psycopg
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from psycopg.rows import dict_row


ROOT = Path(__file__).resolve().parent.parent
CHARTS_DIR = ROOT / "charts"
DRIFT_TIMESERIES_DATA_PATH = CHARTS_DIR / "drift_metric_timeseries" / "drift_metric_timeseries_test_data.js"
DRIFT_TIMESERIES_LIVE_STATE_PATH = ROOT / "drift_metric_timeseries_live_state.json"
HOST = os.environ.get("DRIFT_CHART_SELECTOR_HOST", "127.0.0.1")
PORT = int(os.environ.get("DRIFT_CHART_SELECTOR_PORT", "8765"))
DB_CONFIG = {
    "host": os.environ.get("DRIFT_DB_HOST", "127.0.0.1"),
    "port": int(os.environ.get("DRIFT_DB_PORT", "5432")),
    "dbname": os.environ.get("DRIFT_DB_NAME", "drift_monitoring"),
    "user": os.environ.get("DRIFT_DB_USER", "postgres"),
    "password": os.environ.get("DRIFT_DB_PASSWORD", "postgres"),
}

app = FastAPI(title="Drift Chart Selector", version="2.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type"],
)


class SelectChartRequest(BaseModel):
    request: str = ""


class ChatMessage(BaseModel):
    role: str = ""
    content: str = ""


class ExplainChartRequest(BaseModel):
    chartId: str = ""
    question: str = ""
    history: list[ChatMessage] = []


def parse_iso(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed


def iso_z(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def load_drift_timeseries_source() -> dict[str, object]:
    text = DRIFT_TIMESERIES_DATA_PATH.read_text(encoding="utf-8")
    match = re.search(
        r"window\.DRIFT_METRIC_YEARLY_TEST_DATA\s*=\s*(\{.*\});?\s*\}\)\(\);",
        text,
        re.S,
    )
    if not match:
        raise ValueError("drift_metric_timeseries_test_data.js payload not found")
    return json.loads(match.group(1))


def load_live_state() -> dict[str, object]:
    if DRIFT_TIMESERIES_LIVE_STATE_PATH.exists():
        return json.loads(DRIFT_TIMESERIES_LIVE_STATE_PATH.read_text(encoding="utf-8"))
    return {"cursor": 0}


def save_live_state(state: dict[str, object]) -> None:
    DRIFT_TIMESERIES_LIVE_STATE_PATH.write_text(
        json.dumps(state, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def overlaps_window(start: str, end: str | None, window_start: datetime, window_end: datetime) -> bool:
    left = parse_iso(start)
    right = parse_iso(end) if end else left
    return right > window_start and left < window_end


def rows_for_window(
    rows: list[dict[str, object]],
    window_start: datetime,
    window_end: datetime,
) -> list[dict[str, object]]:
    return [
        row
        for row in rows
        if overlaps_window(
            str(row.get("bucket_start")),
            str(row.get("bucket_end") or row.get("bucket_start")),
            window_start,
            window_end,
        )
    ]


def events_for_window(
    events: list[dict[str, object]],
    window_start: datetime,
    window_end: datetime,
) -> list[dict[str, object]]:
    return [
        event
        for event in events
        if overlaps_window(
            str(event.get("start")),
            str(event.get("end") or event.get("start")),
            window_start,
            window_end,
        )
    ]


def db_connect() -> psycopg.Connection:
    return psycopg.connect(**DB_CONFIG, row_factory=dict_row)


def chart_code_to_file(chart_code: str) -> str:
    return f"{chart_code.lower().replace('-', '_')}.html"


def html_asset_path(assets: dict[str, str], chart_code: str) -> str:
    path = assets.get(chart_code)
    if path and path.startswith("charts/"):
        return path.removeprefix("charts/")
    return chart_code_to_file(chart_code)


def chart_html_title(html_path: str) -> str:
    path = CHARTS_DIR / html_path
    if not path.exists():
        return ""
    text = path.read_text(encoding="utf-8", errors="replace")
    match = re.search(r"<h1[^>]*>(.*?)</h1>", text, re.S | re.I)
    if match:
        return re.sub(r"\s+", " ", strip_tags(match.group(1))).strip()
    match = re.search(r"<title[^>]*>(.*?)</title>", text, re.S | re.I)
    if not match:
        return ""
    return re.sub(r"\s+", " ", strip_tags(match.group(1))).strip()


def strip_tags(value: str) -> str:
    return re.sub(r"<[^>]+>", "", value)


def is_markdown_image_reference(body_html: str) -> bool:
    text = strip_tags(body_html).strip()
    return bool(re.fullmatch(r"!\[[^\]]*\]\([^)]+\)", text))


def chart_html_overview(html_path: str) -> str:
    path = CHARTS_DIR / html_path
    if not path.exists():
        return ""
    text = path.read_text(encoding="utf-8", errors="replace")
    items: list[str] = []
    for match in re.finditer(
        r'<div class="panel-head[^"]*">\s*<h2>(.*?)</h2>\s*<p>(.*?)</p>',
        text,
        re.S | re.I,
    ):
        heading = re.sub(r"\s+", " ", strip_tags(match.group(1))).strip()
        body = re.sub(r"\s+", " ", strip_tags(match.group(2))).strip()
        if heading and body:
            items.append(f"<li><strong>{escape_html(heading)}</strong>: {escape_html(body)}</li>")
    notes: list[str] = []
    for match in re.finditer(r'<section class="notes".*?</section>', text, re.S | re.I):
        for paragraph in re.finditer(r"<p>(.*?)</p>", match.group(0), re.S | re.I):
            body = re.sub(r"\s+", " ", strip_tags(paragraph.group(1))).strip()
            if body:
                notes.append(f"<p>{escape_html(body)}</p>")
    if not items and not notes:
        return ""
    parts = ["<h2>차트 화면 읽기</h2>"]
    parts.extend(notes[:2])
    if items:
        parts.append("<h3>패널별 확인</h3>")
        parts.append("<ul>")
        parts.extend(items)
        parts.append("</ul>")
    return "".join(parts)


def render_section_html(rows: list[dict[str, object]], empty_message: str) -> str:
    parts: list[str] = []
    for row in rows:
        heading = str(row.get("heading_text") or "").strip()
        body = str(row.get("body_html") or "").strip()
        if heading.startswith("CHART-") and is_markdown_image_reference(body):
            continue
        if heading:
            parts.append(f"<h2>{escape_html(heading)}</h2>")
        if body:
            parts.append(body)
    if not parts:
        return f"<p>{escape_html(empty_message)}</p>"
    return "".join(parts)


def latest_chart_sections(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    latest_by_type: dict[str, tuple[int, int, dict[str, object]]] = {}
    untyped: list[dict[str, object]] = []
    for index, row in enumerate(rows):
        section_type = str(row.get("section_type") or "").strip()
        if not section_type:
            untyped.append(row)
            continue
        display_order = int(row.get("display_order") or 0)
        current = latest_by_type.get(section_type)
        if current is None or (display_order, index) >= (current[0], current[1]):
            latest_by_type[section_type] = (display_order, index, row)
    deduped = untyped + [item[2] for item in latest_by_type.values()]
    return sorted(
        deduped,
        key=lambda item: (
            int(item.get("display_order") or 0),
            str(item.get("section_type") or ""),
            str(item.get("heading_text") or ""),
        ),
    )


def escape_html(value: str) -> str:
    return (
        value.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#039;")
    )


def load_gallery_data() -> dict[str, object]:
    with db_connect() as conn:
        charts = conn.execute(
            """
            select chart_definition_id, chart_code, chart_family, display_title,
                   purpose_text, component_summary_text
            from chart_definition
            where status = 'active'
            order by chart_family, chart_code
            """
        ).fetchall()
        assets = conn.execute(
            """
            select cd.chart_code, ca.asset_path
            from chart_asset ca
            join chart_definition cd on cd.chart_definition_id = ca.chart_definition_id
            where ca.asset_type = 'html'
            """
        ).fetchall()
        html_assets = {str(row["chart_code"]): str(row["asset_path"]) for row in assets}

        chart_sections = conn.execute(
            """
            select cd.chart_code, ds.section_type, ds.heading_text, ds.body_html,
                   ds.display_order
            from chart_definition cd
            join section_entity_link sel
              on sel.entity_type = 'chart'
             and sel.entity_id = cd.chart_definition_id
            join document_section ds
              on ds.document_section_id = sel.document_section_id
            join source_document sd
              on sd.source_document_id = ds.source_document_id
            where ds.is_active
              and sd.source_path like 'chart_docs/drift_chart_interpretation_%'
              and sd.source_path <> 'chart_docs/drift_chart_interpretation_guide.md'
              and ds.section_type in (
                'chart_interpretation',
                'chart_purpose',
                'chart_components',
                'interpretation_steps',
                'drift_decision_criteria',
                'example_interpretation',
                'forbidden_interpretation',
                'additional_checks',
                'suitable_use_cases'
              )
            order by cd.chart_code, ds.display_order, ds.document_section_id
            """
        ).fetchall()
        sections_by_chart: dict[str, list[dict[str, object]]] = {}
        for row in chart_sections:
            sections_by_chart.setdefault(str(row["chart_code"]), []).append(row)

        chart_methods = conn.execute(
            """
            select cd.chart_code,
                   dm.display_name as method_name,
                   av.variant_code,
                   vc.selection_reason_text,
                   vc.display_order
            from variant_chart vc
            join chart_definition cd on cd.chart_definition_id = vc.chart_definition_id
            join method_variant mv on mv.method_variant_id = vc.method_variant_id
            join drift_method dm on dm.drift_method_id = mv.drift_method_id
            join algorithm_variant av on av.algorithm_variant_id = mv.algorithm_variant_id
            order by cd.chart_code, vc.display_order nulls last, dm.display_name, av.variant_code
            """
        ).fetchall()

        variant_sections = conn.execute(
            """
            select dm.display_name as method_name,
                   av.algorithm_variant_id,
                   av.variant_code,
                   sd.source_path,
                   ds.heading_text,
                   ds.body_html,
                   ds.display_order
            from algorithm_variant av
            join method_variant mv on mv.algorithm_variant_id = av.algorithm_variant_id
            join drift_method dm on dm.drift_method_id = mv.drift_method_id
            left join source_document sd on sd.source_document_id = av.source_document_id
            left join section_entity_link sel
              on sel.entity_type = 'variant'
             and sel.entity_id = av.algorithm_variant_id
            left join document_section ds
              on ds.document_section_id = sel.document_section_id
             and ds.is_active
             and ds.section_type in ('variant_detail', 'selection_rule')
            order by dm.display_name, av.variant_code, ds.display_order nulls last, ds.document_section_id
            """
        ).fetchall()

    methods_by_chart: dict[str, list[dict[str, str]]] = {}
    for row in chart_methods:
        method = f"{row['method_name']} / {row['variant_code']}"
        methods_by_chart.setdefault(str(row["chart_code"]), []).append(
            {
                "method": method,
                "description": str(row.get("selection_reason_text") or "이 차트에 연결된 탐지 방법입니다."),
            }
        )

    method_rows: dict[str, dict[str, object]] = {}
    for row in variant_sections:
        method = f"{row['method_name']} / {row['variant_code']}"
        item = method_rows.setdefault(
            method,
            {
                "variant": str(row["variant_code"]),
                "source": str(row.get("source_path") or ""),
                "sections": [],
            },
        )
        if row.get("heading_text") or row.get("body_html"):
            item["sections"].append(row)

    method_descriptions: dict[str, dict[str, str]] = {}
    for method, item in method_rows.items():
        source = str(item["source"])
        header = [
            f"<p class=\"chart-id\">{escape_html(source or 'DB catalog')}</p>",
            f"<h1>{escape_html(method)} 탐지 방법</h1>",
            f"<p class=\"method-source\">PostgreSQL drift_monitoring DB</p>",
        ]
        method_descriptions[method] = {
            "variant": str(item["variant"]),
            "source": source,
            "html": "".join(header)
            + render_section_html(
                item["sections"],
                "DB에 연결된 상세 section이 아직 없습니다.",
            ),
        }

    gallery_charts: list[dict[str, str]] = []
    for row in charts:
        chart_code = str(row["chart_code"])
        html_path = html_asset_path(html_assets, chart_code)
        title = chart_html_title(html_path) or str(row.get("display_title") or chart_code)
        family = str(row.get("chart_family") or "기타")
        family_label = f"{family} 계열" if "계열" not in family else family
        desc_header = [
            f"<p class=\"chart-id\">{escape_html(chart_code)}</p>",
            f"<h1>{escape_html(title)}</h1>",
            f"<p class=\"method-source\">PostgreSQL drift_monitoring DB</p>",
            chart_html_overview(html_path),
        ]
        gallery_charts.append(
            {
                "chartId": chart_code,
                "title": title,
                "family": family_label,
                "htmlPath": html_path,
                "descriptionHtml": "".join(desc_header)
                + render_section_html(
                    latest_chart_sections(sections_by_chart.get(chart_code, [])),
                    "DB에 연결된 차트 설명 section이 아직 없습니다.",
                ),
            }
        )

    return {
        "charts": gallery_charts,
        "chartMethods": methods_by_chart,
        "methodDescriptions": method_descriptions,
        "source": {
            "type": "postgresql",
            "database": DB_CONFIG["dbname"],
            "host": DB_CONFIG["host"],
            "port": DB_CONFIG["port"],
        },
    }


def load_chart_context() -> str:
    try:
        data = load_gallery_data()
    except Exception as exc:
        return f"chart DB context load failed: {exc}"
    charts = data.get("charts", [])
    chart_methods = data.get("chartMethods", {})
    lines: list[str] = []
    for chart in charts:
        chart_id = chart.get("chartId")
        lines.append(f"chartId: {chart_id}")
        lines.append(f"family: {chart.get('family')}")
        lines.append(f"title: {chart.get('title')}")
        for method in chart_methods.get(chart_id, [])[:8]:
            lines.append(f"method: {method.get('method')} - {method.get('description')}")
        lines.append("")
    return "\n".join(lines)[:60000]


def find_codex_command() -> str | None:
    candidates = [
        os.environ.get("CODEX_EXE"),
        shutil.which("codex.cmd"),
        shutil.which("codex.exe"),
        shutil.which("codex"),
        str(Path.home() / "AppData" / "Roaming" / "npm" / "codex.cmd"),
    ]
    for candidate in candidates:
        if candidate and Path(candidate).exists():
            return candidate
    return None


def parse_json_response(text: str) -> dict[str, object]:
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    match = re.search(r"\{.*\}", text, re.S)
    if not match:
        raise ValueError("Codex response did not contain JSON.")
    return json.loads(match.group(0))


def plain_text_from_html(value: str) -> str:
    text = re.sub(r"<br\s*/?>", "\n", value, flags=re.I)
    text = re.sub(r"</(p|h1|h2|h3|li|div|article|section)>", "\n", text, flags=re.I)
    text = strip_tags(text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()


def build_prompt(user_request: str) -> str:
    return f"""당신은 drift chart selector입니다.

아래 chart guide를 기준으로 사용자의 요청에 가장 적합한 chart id 하나를 선택하세요.
반드시 제공된 chart id 중에서만 고르세요.
파일을 수정하거나 명령을 실행하지 말고, 판단만 하세요.

선택 기준 보정:
- 사용자가 CCTV, 영상 모델, 이미지 모델, 장면 변화, 조명/먼지/카메라 각도/배경 변화처럼 vision model이 보는 feature 또는 embedding 변화에 대해 말하면 `CHART-REP-001`을 우선 검토하세요.
- 사용자가 평소와 다른 장면, 이상 장면, 미지의 객체, 카메라 가림처럼 novelty/anomaly 증가를 말하면 `CHART-ANOM-001`을 우선 검토하세요.
- 사용자가 이미지 feature histogram, bin, histogram intersection처럼 명시적으로 히스토그램 기반 비교를 말할 때만 `CHART-HIST-001`을 우선 검토하세요.
- 사용자가 객체 종류, 안전모/작업자/장비 class 비율 변화처럼 category 비율을 말하면 category 계열 chart를 우선 검토하세요.

응답은 JSON 하나만 출력하세요.

JSON 형식:
{{
  "chartId": "CHART-...",
  "chartTitle": "간단한 차트 이름",
  "family": "차트 계열",
  "reason": "왜 이 차트가 적절한지 한국어로 2~4문장",
  "alternatives": [
    {{"chartId": "CHART-...", "reason": "짧은 대안 이유"}}
  ]
}}

사용자 요청:
{user_request}

chart guide:
{load_chart_context()}
"""


def chart_explanation_context(chart_id: str) -> str:
    data = load_gallery_data()
    charts = data.get("charts", [])
    chart = next((item for item in charts if item.get("chartId") == chart_id), None)
    if not chart:
        raise ValueError(f"알 수 없는 chart id입니다: {chart_id}")
    methods = data.get("chartMethods", {}).get(chart_id, [])
    lines = [
        f"chartId: {chart.get('chartId')}",
        f"title: {chart.get('title')}",
        f"family: {chart.get('family')}",
        "",
        "chart explanation:",
        plain_text_from_html(str(chart.get("descriptionHtml") or ""))[:18000],
        "",
        "connected method variants:",
    ]
    for method in methods[:20]:
        lines.append(f"- {method.get('method')}: {method.get('description')}")
    return "\n".join(lines)


def build_explain_prompt(payload: ExplainChartRequest) -> str:
    history_lines: list[str] = []
    for message in payload.history[-8:]:
        role = "사용자" if message.role == "user" else "답변"
        content = message.content.strip()
        if content:
            history_lines.append(f"{role}: {content}")
    history = "\n".join(history_lines) or "이전 대화 없음"
    return f"""당신은 drift chart 설명 도우미입니다.

사용자는 현재 선택된 차트에 대해 추가 질문을 하고 있습니다.
아래 chart context에 있는 정보만 근거로 답하세요.
모르면 모른다고 말하고, 어떤 추가 확인이 필요한지 제안하세요.
답변은 한국어로 하며, 사용자가 이해할 수 있게 현재 상황, 패널 의미, 해석 한계를 구분해 설명하세요.
파일을 수정하거나 명령을 실행하지 말고, 설명만 하세요.

응답은 JSON 하나만 출력하세요.

JSON 형식:
{{
  "answer": "사용자 질문에 대한 답변"
}}

chart context:
{chart_explanation_context(payload.chartId.strip())}

recent conversation:
{history}

user question:
{payload.question.strip()}
"""


def run_codex_selector(user_request: str) -> dict[str, object]:
    codex = find_codex_command()
    if not codex:
        raise RuntimeError("codex.cmd 또는 codex.exe를 찾지 못했습니다. CODEX_EXE 환경변수로 경로를 지정하세요.")

    schema = {
        "type": "object",
        "additionalProperties": False,
        "required": ["chartId", "chartTitle", "family", "reason", "alternatives"],
        "properties": {
            "chartId": {"type": "string"},
            "chartTitle": {"type": "string"},
            "family": {"type": "string"},
            "reason": {"type": "string"},
            "alternatives": {
                "type": "array",
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": ["chartId", "reason"],
                    "properties": {
                        "chartId": {"type": "string"},
                        "reason": {"type": "string"},
                    },
                },
            },
        },
    }

    with tempfile.TemporaryDirectory(prefix="drift_chart_selector_") as tmp:
        tmp_path = Path(tmp)
        schema_path = tmp_path / "schema.json"
        output_path = tmp_path / "last_message.txt"
        schema_path.write_text(json.dumps(schema, ensure_ascii=False), encoding="utf-8")

        command = [
            codex,
            "exec",
            "--skip-git-repo-check",
            "--sandbox",
            "read-only",
            "--output-schema",
            str(schema_path),
            "--output-last-message",
            str(output_path),
            "-",
        ]
        completed = subprocess.run(
            command,
            input=build_prompt(user_request),
            cwd=str(ROOT),
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            timeout=180,
            check=False,
        )
        output = output_path.read_text(encoding="utf-8") if output_path.exists() else completed.stdout
        if completed.returncode != 0 and not output.strip():
            stderr = completed.stderr.strip() or completed.stdout.strip()
            raise RuntimeError(f"Codex CLI failed: {stderr}")
        return parse_json_response(output)


def run_codex_chart_explainer(payload: ExplainChartRequest) -> str:
    codex = find_codex_command()
    if not codex:
        raise RuntimeError("codex.cmd 또는 codex.exe를 찾지 못했습니다. CODEX_EXE 환경변수로 경로를 지정하세요.")

    schema = {
        "type": "object",
        "additionalProperties": False,
        "required": ["answer"],
        "properties": {
            "answer": {"type": "string"},
        },
    }

    with tempfile.TemporaryDirectory(prefix="drift_chart_explain_") as tmp:
        tmp_path = Path(tmp)
        schema_path = tmp_path / "schema.json"
        output_path = tmp_path / "last_message.txt"
        schema_path.write_text(json.dumps(schema, ensure_ascii=False), encoding="utf-8")
        command = [
            codex,
            "exec",
            "--skip-git-repo-check",
            "--sandbox",
            "read-only",
            "--output-schema",
            str(schema_path),
            "--output-last-message",
            str(output_path),
            "-",
        ]
        completed = subprocess.run(
            command,
            input=build_explain_prompt(payload),
            cwd=str(ROOT),
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            timeout=180,
            check=False,
        )
        output = output_path.read_text(encoding="utf-8") if output_path.exists() else completed.stdout
        if completed.returncode != 0 and not output.strip():
            stderr = completed.stderr.strip() or completed.stdout.strip()
            raise RuntimeError(f"Codex CLI failed: {stderr}")
        result = parse_json_response(output)
        return str(result.get("answer") or "").strip()


@app.get("/api/health")
def health() -> dict[str, object]:
    return {
        "ok": True,
        "service": "drift-chart-selector",
        "backend": "fastapi",
        "database": DB_CONFIG["dbname"],
    }


@app.get("/api/gallery-data")
def gallery_data() -> dict[str, object]:
    try:
        return {"ok": True, "data": load_gallery_data()}
    except Exception as exc:
        return {"ok": False, "error": str(exc)}


@app.post("/api/select-chart")
def select_chart(payload: SelectChartRequest) -> dict[str, object]:
    user_request = payload.request.strip()
    if not user_request:
        return {"ok": False, "error": "요청 내용을 입력하세요."}
    try:
        return {"ok": True, "result": run_codex_selector(user_request)}
    except subprocess.TimeoutExpired:
        return {"ok": False, "error": "Codex CLI 응답 시간이 초과되었습니다."}
    except Exception as exc:
        return {"ok": False, "error": str(exc)}


@app.post("/api/explain-chart")
def explain_chart(payload: ExplainChartRequest) -> dict[str, object]:
    if not payload.chartId.strip():
        return {"ok": False, "error": "chart id가 없습니다."}
    if not payload.question.strip():
        return {"ok": False, "error": "질문 내용을 입력하세요."}
    try:
        answer = run_codex_chart_explainer(payload)
        return {"ok": True, "answer": answer}
    except subprocess.TimeoutExpired:
        return {"ok": False, "error": "Codex CLI 응답 시간이 초과되었습니다."}
    except Exception as exc:
        return {"ok": False, "error": str(exc)}


@app.post("/api/drift-metric-timeseries/live/reset")
def reset_drift_metric_timeseries_live() -> dict[str, object]:
    source = load_drift_timeseries_source()
    source_domain = source.get("fullDomain", [])
    history_start = source_domain[0] if isinstance(source_domain, list) and source_domain else None
    save_live_state({"cursor": 0, "updated_at": iso_z(datetime.now(timezone.utc))})
    return {
        "ok": True,
        "cursor": 0,
        "modelId": source.get("modelId"),
        "features": source.get("features", []),
        "fullDomain": [history_start, history_start] if history_start else [],
    }


@app.get("/api/drift-metric-timeseries/live/metadata")
def get_drift_metric_timeseries_live_metadata() -> dict[str, object]:
    source = load_drift_timeseries_source()
    state = load_live_state()
    source_domain = source.get("fullDomain", [])
    history_start = source_domain[0] if isinstance(source_domain, list) and source_domain else None
    cursor = int(state.get("cursor", 0))
    known_end = state.get("last_day_end") or history_start
    return {
        "ok": True,
        "cursor": cursor,
        "modelId": source.get("modelId"),
        "features": source.get("features", []),
        "fullDomain": [history_start, known_end] if history_start and known_end else [],
        "pollIntervalMs": 5000,
    }


@app.get("/api/drift-metric-timeseries/live/next-day")
def get_drift_metric_timeseries_next_day() -> dict[str, object]:
    source = load_drift_timeseries_source()
    full_domain = source.get("fullDomain", [])
    if not isinstance(full_domain, list) or len(full_domain) < 2:
        return {"ok": False, "error": "invalid fullDomain"}

    state = load_live_state()
    cursor = int(state.get("cursor", 0))
    full_start = parse_iso(str(full_domain[0]))
    full_end = parse_iso(str(full_domain[1]))
    day_start = full_start + timedelta(days=cursor)
    if day_start >= full_end:
        return {
            "ok": True,
            "done": True,
            "cursor": cursor,
            "fullDomain": [full_domain[0], iso_z(full_end)],
            "features": source.get("features", []),
        }
    day_end = min(day_start + timedelta(days=1), full_end)

    source_series = source.get("series", {})
    source_by_resolution = source.get("seriesByResolution", {})
    source_events = source.get("events", {})
    features = source.get("features", [])
    feature_ids = [str(feature.get("featureId")) for feature in features if isinstance(feature, dict)]

    series: dict[str, list[dict[str, object]]] = {}
    series_by_resolution: dict[str, dict[str, list[dict[str, object]]]] = {}
    events: dict[str, list[dict[str, object]]] = {}
    for feature_id in feature_ids:
        daily_rows = rows_for_window(list(source_series.get(feature_id, [])), day_start, day_end)
        series[feature_id] = daily_rows
        by_resolution: dict[str, list[dict[str, object]]] = {}
        for resolution, rows in dict(source_by_resolution.get(feature_id, {})).items():
            if resolution in {"1h", "1d"}:
                by_resolution[str(resolution)] = rows_for_window(list(rows), day_start, day_end)
        if "1d" not in by_resolution:
            by_resolution["1d"] = daily_rows
        series_by_resolution[feature_id] = by_resolution
        events[feature_id] = events_for_window(list(source_events.get(feature_id, [])), day_start, day_end)

    cursor += 1
    save_live_state({
        "cursor": cursor,
        "last_day_start": iso_z(day_start),
        "last_day_end": iso_z(day_end),
        "updated_at": iso_z(datetime.now(timezone.utc)),
    })
    return {
        "ok": True,
        "done": False,
        "cursor": cursor,
        "modelId": source.get("modelId"),
        "features": features,
        "fullDomain": [full_domain[0], iso_z(day_end)],
        "dayStart": iso_z(day_start),
        "dayEnd": iso_z(day_end),
        "loadedDomain": [full_domain[0], iso_z(day_end)],
        "series": series,
        "seriesByResolution": series_by_resolution,
        "events": events,
        "pollIntervalMs": 5000,
    }


app.mount("/", StaticFiles(directory=str(CHARTS_DIR), html=True), name="charts")


def main() -> None:
    print(f"Drift chart selector server: http://{HOST}:{PORT}/gallery.html")
    print("Press Ctrl+C to stop.")
    uvicorn.run(app, host=HOST, port=PORT, log_level="info")


if __name__ == "__main__":
    main()
